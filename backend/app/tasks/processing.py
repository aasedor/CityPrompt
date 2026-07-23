"""
Async tasks for document processing pipeline.
"""

import asyncio
import logging
import tempfile
import time
import uuid
from datetime import datetime, timezone

import boto3
from botocore.config import Config
from celery.exceptions import SoftTimeLimitExceeded
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.usage_logger import log_api_usage_sync
from app.generation.engine import MESHY_MAX_RUNTIME_S, get_engine
from app.services.residual_landscape import (
    lock_residual_landscape_project_sync,
    mark_linked_community_3d_stale_sync,
)
from app.tasks.worker import celery_app

logger = logging.getLogger(__name__)
settings = get_settings()

_sync_engine = None
_sync_session_factory = None
_sync_pool_size = 5 if settings.app_env == "production" else 20
_sync_max_overflow = 3 if settings.app_env == "production" else 10
_COMMUNITY_MODEL_CHANGED_REASON = (
    "Linked generated building model changed; rebuild Community 3D before Direct rendering."
)


def _get_sync_engine():
    global _sync_engine
    if _sync_engine is None:
        _sync_engine = create_engine(
            settings.database_url_sync,
            echo=settings.app_debug,
            pool_size=_sync_pool_size,
            max_overflow=_sync_max_overflow,
            pool_pre_ping=True,
        )
    return _sync_engine


def _get_sync_session() -> Session:
    """Create a sync SQLAlchemy session for use in Celery tasks."""
    global _sync_session_factory
    if _sync_session_factory is None:
        _sync_session_factory = sessionmaker(
            bind=_get_sync_engine(),
            class_=Session,
            expire_on_commit=False,
        )
    return _sync_session_factory()


def _merge_building_specifications(building, updates: dict) -> None:
    specs = dict(building.specifications or {})
    specs.update(updates)
    building.specifications = specs


def _begin_building_representation_mutation(session: Session, building) -> None:
    """Serialize a worker's visible model write with paid Direct preflight."""

    lock_residual_landscape_project_sync(session, building.project_id)
    session.refresh(building)


def _mark_building_representation_stale(session: Session, building) -> None:
    mark_linked_community_3d_stale_sync(
        session,
        project_id=building.project_id,
        building_id=building.id,
        reason=_COMMUNITY_MODEL_CHANGED_REASON,
    )


def _queue_procedural_generation_jobs(session: Session, document, jobs: list[tuple[object, dict]]) -> list[dict]:
    """Queue committed procedural generation jobs and persist task metadata best-effort."""
    queue_failures: list[dict] = []

    for building, building_data in jobs:
        try:
            task = generate_3d_model.delay(str(building.id), building_data)
        except Exception as exc:
            logger.error(
                "Failed to queue procedural generation for building %s: %s",
                building.id,
                exc,
            )
            building.generation_status = "failed"
            _merge_building_specifications(
                building,
                {"generation_error": f"Failed to queue procedural generation: {exc}"},
            )
            queue_failures.append({"building_id": str(building.id), "error": str(exc)})
            continue

        task_id = getattr(task, "id", None)
        if task_id:
            _merge_building_specifications(building, {"celery_task_id": task_id})

    if queue_failures:
        extracted = dict(document.extracted_data or {})
        extracted["generation_queue_failures"] = queue_failures
        document.extracted_data = extracted

    if not jobs:
        return queue_failures

    try:
        session.commit()
    except Exception as exc:
        session.rollback()
        logger.warning("Failed to persist procedural queue metadata: %s", exc)

    return queue_failures


def _get_s3_client():
    """Create a boto3 S3 client for MinIO."""
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
        config=Config(signature_version="s3v4"),
    )


def _download_from_storage(storage_url: str) -> bytes:
    """Download a file from S3/MinIO given its storage URL."""
    s3 = _get_s3_client()
    url_parts = storage_url.split(f"/{settings.s3_bucket_name}/", 1)
    if len(url_parts) != 2:
        raise ValueError(f"Invalid storage URL: {storage_url}")
    file_key = url_parts[1]
    obj = s3.get_object(Bucket=settings.s3_bucket_name, Key=file_key)
    return obj["Body"].read()


def _upload_to_storage(key: str, data: bytes, content_type: str) -> str:
    """Upload bytes to S3/MinIO and return the URL."""
    s3 = _get_s3_client()
    try:
        s3.head_bucket(Bucket=settings.s3_bucket_name)
    except Exception:
        try:
            s3.create_bucket(Bucket=settings.s3_bucket_name)
        except Exception as bucket_err:
            logger.debug("Bucket creation skipped (may already exist): %s", bucket_err)
    s3.put_object(
        Bucket=settings.s3_bucket_name,
        Key=key,
        Body=data,
        ContentType=content_type,
    )
    return f"{settings.s3_endpoint_url}/{settings.s3_bucket_name}/{key}"


def _file_proxy_url(key: str) -> str:
    """Browser-reachable URL for a stored object.

    _upload_to_storage returns the internal S3 endpoint (e.g.
    http://minio:9000/...), which a browser can't resolve. Model/LOD GLBs are
    fetched client-side by the 3D viewer, so they must be served through the
    /api/v1/files proxy — the same pattern thumbnails and saved renders use.
    """
    return f"/api/v1/files/{key}"


def _storage_key_from_url(url: str) -> str | None:
    """Extract the storage key from a stored-object URL. Modern URLs are API
    paths (/api/v1/files/<key>); legacy URLs embed the bucket directly
    (http://minio:9000/<bucket>/<key>)."""
    files_prefix = "/api/v1/files/"
    if files_prefix in url:
        return url.split(files_prefix, 1)[1]
    parts = url.split(f"/{settings.s3_bucket_name}/", 1)
    return parts[1] if len(parts) == 2 else None


def _copy_storage_object(source_key: str, dest_key: str, content_type: str = "model/gltf-binary") -> None:
    """Server-side S3 copy within the app bucket (no download round-trip)."""
    s3 = _get_s3_client()
    s3.copy_object(
        Bucket=settings.s3_bucket_name,
        CopySource={"Bucket": settings.s3_bucket_name, "Key": source_key},
        Key=dest_key,
        ContentType=content_type,
    )


# Minimum AI confidence score to accept a building interpretation.
# Results below this threshold are logged and skipped.
CONFIDENCE_THRESHOLD = 0.3


def _normalize_extraction_data(extraction_result, interpretation_result) -> list[dict]:
    """
    Merge extraction and AI interpretation results into normalized building records.
    Filters out AI results with confidence below CONFIDENCE_THRESHOLD.
    Returns a list of building data dicts ready for DB insertion and 3D generation.
    """
    buildings = []
    extraction_dict = extraction_result.to_dict()

    # Overall confidence from the AI interpretation
    overall_confidence = 0.0
    if isinstance(interpretation_result, dict):
        overall_confidence = interpretation_result.get("confidence", 0.0)

    # Try to get buildings from AI interpretation
    ai_buildings = []
    if isinstance(interpretation_result, dict):
        ai_buildings = interpretation_result.get("buildings", [])

        # If no buildings list, check for direct building dimensions (floor plan interpretation)
        if not ai_buildings and "building_dimensions" in interpretation_result:
            dims = interpretation_result["building_dimensions"]
            ai_buildings = [{
                "name": "Building A",
                "height_meters": interpretation_result.get("total_height_meters"),
                "floor_count": interpretation_result.get("floor_count"),
                "floor_height_meters": interpretation_result.get("floor_height_meters"),
                "footprint_area_sqm": dims.get("estimated_area_sqm"),
                "width": dims.get("width_meters", 20),
                "depth": dims.get("depth_meters", 15),
                "roof_type": interpretation_result.get("roof_type", "flat"),
                "_confidence": overall_confidence,
            }]

    if ai_buildings:
        for i, ab in enumerate(ai_buildings):
            # Per-building confidence (from _confidence tag) or fallback to overall
            confidence = ab.get("_confidence", ab.get("confidence", overall_confidence))
            try:
                confidence = float(confidence)
            except (TypeError, ValueError):
                confidence = 0.0

            if confidence < CONFIDENCE_THRESHOLD:
                logger.warning(
                    f"Skipping building '{ab.get('name', i)}': "
                    f"confidence {confidence:.2f} < threshold {CONFIDENCE_THRESHOLD}"
                )
                continue

            width = ab.get("width", 20)
            depth = ab.get("depth", 15)
            height = ab.get("height_meters") or 10.0
            floors = max(1, ab.get("floor_count") or int(height / 3.0))
            floor_height = ab.get("floor_height_meters") or (height / floors)

            # Generate a simple rectangular footprint if no coordinates available
            footprint = None
            if extraction_dict.get("coordinates") and i < len(extraction_dict["coordinates"]):
                footprint = extraction_dict["coordinates"][i]
            else:
                # Create rectangular footprint centered at origin offset by index
                offset_x = i * (width + 10)
                footprint = [
                    [offset_x, 0],
                    [offset_x + width, 0],
                    [offset_x + width, depth],
                    [offset_x, depth],
                    [offset_x, 0],
                ]

            buildings.append({
                "name": ab.get("name", f"Building {chr(65 + i)}"),
                "height_meters": height,
                "floor_count": floors,
                "floor_height_meters": floor_height,
                "roof_type": ab.get("roof_type", "flat"),
                "footprint": footprint,
                "specifications": {
                    "total_area_sqm": ab.get("total_area_sqm") or ab.get("footprint_area_sqm"),
                    "residential_units": ab.get("units"),
                    "use_type": ab.get("use_type"),
                    "ai_confidence": confidence,
                },
            })
    elif extraction_dict.get("coordinates"):
        # No AI interpretation - build from extracted coordinates
        for i, coords in enumerate(extraction_dict["coordinates"]):
            buildings.append({
                "name": f"Building {chr(65 + i)}",
                "height_meters": 10.0,
                "floor_count": 3,
                "floor_height_meters": 3.33,
                "roof_type": "flat",
                "footprint": coords,
                "specifications": {},
            })
    else:
        # Minimal fallback - create a single default building
        buildings.append({
            "name": "Building A",
            "height_meters": 10.0,
            "floor_count": 3,
            "floor_height_meters": 3.33,
            "roof_type": "flat",
            "footprint": [[0, 0], [20, 0], [20, 15], [0, 15], [0, 0]],
            "specifications": {},
        })

    return buildings


class _SkipInterpretationError(Exception):
    """Internal sentinel: extract_only uploads skip the AI-interpretation step."""


@celery_app.task(bind=True, name="process_document", max_retries=3)
def process_document(self, document_id: str, extract_only: bool = False):
    """
    Main document processing task.

    Pipeline:
    1. Download file from storage
    2. Detect file type and route to appropriate extractor
    3. Extract data (text, dimensions, coordinates)
    4. Send to AI for interpretation if needed
    5. Normalize extracted data to standard schema
    6. Create building records and trigger 3D generation
    7. Update document record with results

    With extract_only=True (style-reference uploads for custom render zones),
    steps 4-6 are skipped: no AI interpretation, no Building records, no 3D
    generation — only text/image extraction into Document.extracted_data.
    """
    logger.info(f"Processing document: {document_id}")
    session = _get_sync_session()

    try:
        # Load document record
        from app.models.models import Document, Building
        document = session.query(Document).filter_by(id=uuid.UUID(document_id)).first()
        if not document:
            raise ValueError(f"Document not found: {document_id}")

        document.processing_status = "processing"
        session.commit()

        self.update_state(state="PROCESSING", meta={"progress": 0.1, "step": "downloading"})

        # Step 1: Download file from S3
        file_data = _download_from_storage(document.storage_url)

        self.update_state(state="PROCESSING", meta={"progress": 0.2, "step": "extracting"})

        # Step 2-3: Write to temp file and extract data based on file type
        from app.processing.extractors.document_extractor import extract_from_file

        with tempfile.NamedTemporaryFile(
            suffix=f".{document.file_type}", delete=False
        ) as tmp:
            tmp.write(file_data)
            tmp_path = tmp.name

        extraction_result = extract_from_file(tmp_path, document.file_type)

        self.update_state(state="PROCESSING", meta={"progress": 0.5, "step": "interpreting"})

        # Step 4: AI interpretation using Claude - prioritize floor plans & elevations
        # Skipped entirely for extract_only (style-reference) uploads.
        interpretation_result = {}
        try:
            if extract_only:
                raise _SkipInterpretationError()
            from app.processing.analyzers.claude_interpreter import ClaudeInterpreter
            interpreter = ClaudeInterpreter()

            if extraction_result.images:
                all_buildings = []
                total_images = len(extraction_result.images)
                classifications = extraction_result.page_classifications

                for img_idx, image_data in enumerate(extraction_result.images):
                    progress = 0.5 + (img_idx / max(total_images, 1)) * 0.15

                    # Use page classification to decide interpretation strategy
                    page_type = "unknown"
                    if img_idx < len(classifications):
                        page_type = classifications[img_idx].get("type", "unknown")

                    # Skip text-only and schedule pages - no architectural drawings
                    if page_type in ("text", "schedule"):
                        logger.info(
                            f"Skipping page {img_idx + 1}/{total_images} "
                            f"(classified as '{page_type}')"
                        )
                        continue

                    self.update_state(
                        state="PROCESSING",
                        meta={
                            "progress": progress,
                            "step": f"interpreting {page_type} page {img_idx + 1}/{total_images}",
                        },
                    )

                    try:
                        # Route to appropriate interpreter based on page classification
                        if page_type == "floor_plan":
                            result = asyncio.run(interpreter.interpret_floor_plan(image_data))
                        elif page_type == "elevation":
                            result = asyncio.run(interpreter.interpret_elevation(image_data))
                        else:
                            # Unknown - try floor plan first, fall back to elevation
                            result = asyncio.run(interpreter.interpret_floor_plan(image_data))
                            if not result or not result.get("buildings") and not result.get("building_dimensions"):
                                result = asyncio.run(interpreter.interpret_elevation(image_data))
                    except Exception as img_err:
                        logger.warning(f"AI interpretation failed for image {img_idx + 1}: {img_err}")
                        continue

                    if isinstance(result, dict):
                        img_confidence = result.get("confidence", 0.0)
                        # Collect buildings from each image, tagging with source confidence
                        if result.get("buildings"):
                            for b in result["buildings"]:
                                b.setdefault("_confidence", img_confidence)
                            all_buildings.extend(result["buildings"])
                        elif result.get("building_dimensions"):
                            # Single building from floor plan - tag with confidence
                            result["_confidence"] = img_confidence
                            all_buildings.append(result)

                # Merge all discovered buildings into one result
                if all_buildings:
                    interpretation_result = {"buildings": all_buildings}
                    logger.info(f"AI interpretation found {len(all_buildings)} building(s) from {total_images} image(s)")

            elif extraction_result.text_content.strip():
                # Use text-based dimension extraction
                interpretation_result = asyncio.run(
                    interpreter.extract_dimensions_from_text(extraction_result.text_content)
                )
        except _SkipInterpretationError:
            logger.info(f"extract_only upload — skipping AI interpretation for {document_id}")
        except Exception as e:
            logger.warning(f"AI interpretation failed (non-fatal): {e}")

        self.update_state(state="PROCESSING", meta={"progress": 0.7, "step": "normalizing"})

        # Step 5: Normalize extracted data.
        # extract_only uploads are style references — never create Building
        # records or 3D generation jobs from them.
        normalized_buildings = [] if extract_only else _normalize_extraction_data(extraction_result, interpretation_result)

        self.update_state(state="PROCESSING", meta={"progress": 0.8, "step": "generating_3d"})

        # Step 6: Create building records and trigger 3D generation
        created_building_ids = []
        queued_generation_jobs: list[tuple[object, dict]] = []
        for bdata in normalized_buildings:
            building = Building(
                project_id=document.project_id,
                name=bdata["name"],
                height_meters=bdata["height_meters"],
                floor_count=bdata["floor_count"],
                floor_height_meters=bdata["floor_height_meters"],
                roof_type=bdata["roof_type"],
                specifications=bdata.get("specifications"),
                generation_status="generating",
            )

            # Set footprint if coordinates available
            if bdata.get("footprint"):
                from geoalchemy2.elements import WKTElement
                coords = bdata["footprint"]
                if coords[0] != coords[-1]:
                    coords.append(coords[0])
                coords_str = ", ".join(f"{c[0]} {c[1]}" for c in coords)
                building.footprint = WKTElement(f"POLYGON(({coords_str}))", srid=4326)

            session.add(building)
            session.flush()
            created_building_ids.append(str(building.id))
            queued_generation_jobs.append((building, bdata))

        self.update_state(state="PROCESSING", meta={"progress": 1.0, "step": "complete"})

        # Step 7: Update document record with results
        document.processing_status = "completed"
        document.processed_at = datetime.now(timezone.utc)
        document.extracted_data = {
            "extraction": extraction_result.to_dict(),
            "interpretation": interpretation_result if isinstance(interpretation_result, dict) else {},
            "building_ids": created_building_ids,
        }
        session.commit()
        queue_failures = _queue_procedural_generation_jobs(session, document, queued_generation_jobs)
        logger.info(f"Document processing complete: {document_id}, created {len(created_building_ids)} buildings")
        return {
            "status": "completed",
            "document_id": document_id,
            "building_ids": created_building_ids,
            "generation_queue_failures": queue_failures,
        }

    except Exception as exc:
        logger.error(f"Document processing failed: {document_id} - {exc}")
        try:
            from app.models.models import Document
            document = session.query(Document).filter_by(id=uuid.UUID(document_id)).first()
            if document:
                document.processing_status = "failed"
                document.extracted_data = {"error": str(exc)}
                session.commit()
        except Exception as inner_exc:
            session.rollback()
            logger.warning("Failed to mark document %s as failed: %s", document_id, inner_exc)
        raise self.retry(exc=exc, countdown=60)
    finally:
        session.close()
        # Clean up temp file (runs on both success and error paths)
        import os
        try:
            os.unlink(tmp_path)
        except (NameError, TypeError):
            pass  # tmp_path was never assigned (download failed before temp file creation)
        except OSError as cleanup_err:
            logger.debug("Temp file cleanup: %s", cleanup_err)


def _propagate_model_to_siblings(session: Session, building_id: str, model_url: str, lod_urls: dict, preview_url: str | None = None):
    """Copy generated model to all sibling buildings in the same zone.

    Finds the zone that contains this building_id in its building_ids list,
    then updates all other buildings in that list with the same model_url and lod_urls.
    """
    from app.models.models import Building, SiteZone

    # Find zones where building_ids contains this building_id
    zones = session.query(SiteZone).filter(
        SiteZone.building_ids.isnot(None)
    ).all()

    for zone in zones:
        bid_list = zone.building_ids or []
        if building_id not in bid_list and str(building_id) not in [str(b) for b in bid_list]:
            continue

        # Found the zone - propagate to siblings
        lock_residual_landscape_project_sync(session, zone.project_id)
        session.refresh(zone)
        bid_list = zone.building_ids or []
        if str(building_id) not in [str(b) for b in bid_list]:
            continue
        sibling_count = 0
        for bid_str in bid_list:
            if str(bid_str) == str(building_id):
                continue  # Skip the source building
            sibling = session.query(Building).filter_by(id=uuid.UUID(str(bid_str))).first()
            if sibling:
                session.refresh(sibling)
                sibling.model_url = model_url
                sibling.lod_urls = lod_urls
                sibling.generation_status = "completed"
                if preview_url:
                    sibling.preview_url = preview_url
                    sibling.preview_status = "completed"
                _mark_building_representation_stale(session, sibling)
                sibling_count += 1

        if sibling_count > 0:
            session.commit()
            logger.info(
                f"Propagated model from building {building_id} to {sibling_count} sibling(s)"
            )
        break  # A building belongs to at most one zone


# soft/hard limits are DERIVED from the engine's poll ceilings so they can't
# drift back under them (which silently soft-killed paid generations).
def _wait_for_cache_entry(session: Session, entry_id, progress_callback=None):
    """Poll another worker's in-flight cache claim until it resolves.

    Returns the entry (completed or failed) or None on timeout. The caller
    falls back to an uncached generation on failure/timeout — waiting must
    never be the reason a building has no model.
    """
    from app.models.models import ArchetypeModelCache

    deadline = time.monotonic() + settings.archetype_cache_wait_s
    while time.monotonic() < deadline:
        entry = session.get(ArchetypeModelCache, entry_id)
        if entry is None or entry.status in ("completed", "failed"):
            return entry
        session.expire(entry)
        # Close the read transaction between polls — sleeping 15s inside an
        # open transaction pins the connection "idle in transaction".
        session.rollback()
        if progress_callback:
            progress_callback(0.3, "waiting_for_cache")
        time.sleep(15)
    logger.warning("Timed out waiting for cache entry %s; generating uncached", entry_id)
    return None


def _apply_cached_model(session: Session, building_id: str, building, entry, engine_id: str) -> dict:
    """Point a building at an already-generated cache entry (zero credits)."""
    from app.services.archetype_model_cache import bump_use_count

    model_url = _file_proxy_url(entry.model_key)
    lod_urls = {str(k): _file_proxy_url(v) for k, v in (entry.lod_keys or {}).items()}
    lod_urls.setdefault("0", model_url)

    _begin_building_representation_mutation(session, building)
    building.model_url = model_url
    building.lod_urls = lod_urls
    building.generation_status = "completed"
    building.meshy_task_id = entry.source_task_id
    if entry.thumbnail_key:
        building.preview_url = _file_proxy_url(entry.thumbnail_key)
        building.preview_status = "completed"
    _mark_building_representation_stale(session, building)
    session.commit()

    bump_use_count(session, entry.id)
    log_api_usage_sync(
        provider=engine_id,
        operation="cache_hit",
        credits_used=0,
        task_id=entry.source_task_id,
        building_id=building_id,
        metadata={
            "archetype_id": entry.archetype_id,
            "variant_id": entry.variant_id,
            "cache_id": str(entry.id),
        },
    )
    try:
        _propagate_model_to_siblings(session, building_id, model_url, lod_urls, building.preview_url)
    except Exception as prop_err:
        logger.warning(f"Model propagation to siblings failed (non-fatal): {prop_err}")

    logger.info(
        "Cache hit for building %s: %s/%s -> %s",
        building_id, entry.archetype_id, entry.variant_id, model_url,
    )
    return {
        "status": "completed",
        "building_id": building_id,
        "model_url": model_url,
        "cache_hit": True,
    }


def _find_library_model(session: Session, building, archetype_id: str):
    """Best saved model-library entry whose SOURCE building carries the same
    archetype identity as this building.

    Only entries the project owner could apply manually qualify: their own or
    public ones. Raw archetype ids carry legacy suffixes ("_front_day", baked
    "_variant_N"), so the SQL LIKE is just a prefilter — equality is decided
    by the same normalizer the archetype cache keys with.
    """
    from sqlalchemy import or_, select

    from app.models.models import Building, ModelLibraryEntry, Project
    from app.services.archetype_model_cache import normalize_cache_key

    owner_id = session.execute(
        select(Project.owner_id).where(Project.id == building.project_id)
    ).scalar_one_or_none()
    access = [ModelLibraryEntry.is_public.is_(True)]
    if owner_id is not None:
        access.append(ModelLibraryEntry.owner_id == owner_id)

    # Anchor the suffix boundary ("park" must not sweep in "parking_garage"
    # sources and crowd the LIMIT window into a false miss).
    raw_id = Building.specifications["development_archetype_id"].astext
    rows = session.execute(
        select(ModelLibraryEntry, Building.specifications)
        .join(Building, ModelLibraryEntry.source_building_id == Building.id)
        .where(
            or_(raw_id == archetype_id, raw_id.like(f"{archetype_id}\\_%", escape="\\")),
            or_(*access),
        )
        .order_by(
            ModelLibraryEntry.use_count.desc().nulls_last(),
            ModelLibraryEntry.created_at.desc(),
        )
        .limit(25)
    ).all()
    for entry, source_specs in rows:
        key = normalize_cache_key(source_specs)
        if key is not None and key[0] == archetype_id:
            return entry
    return None


def _apply_library_model(session: Session, building_id: str, building, entry, archetype_id: str, engine_id: str) -> dict | None:
    """Point a building at a saved model-library entry (zero credits).

    Objects are COPIED into the building's project (mirroring the manual
    /model-library/items/{id}/apply endpoint) — deleting a library entry
    deletes its library/ objects, which must not strand buildings that
    reused it. Returns None on failure so the caller falls back to a paid
    generation.
    """
    from sqlalchemy import func as sa_func
    from sqlalchemy import update as sa_update

    from app.models.models import ModelLibraryEntry

    source_key = _storage_key_from_url(entry.model_url)
    if source_key is None:
        logger.warning("Library entry %s has an unparseable model_url; skipping", entry.id)
        return None
    dest_key = f"projects/{building.project_id}/models/{building_id}_ai.glb"
    try:
        _copy_storage_object(source_key, dest_key)
    except Exception as copy_err:
        logger.warning("Library model copy failed for entry %s (non-fatal): %s", entry.id, copy_err)
        return None

    model_url = _file_proxy_url(dest_key)
    lod_urls: dict[str, str] = {}
    for level, lod_source_url in (entry.lod_urls or {}).items():
        lod_source_key = _storage_key_from_url(lod_source_url)
        if lod_source_key is None:
            continue
        lod_dest_key = f"projects/{building.project_id}/models/{building_id}_lod{level}.glb"
        try:
            _copy_storage_object(lod_source_key, lod_dest_key)
        except Exception:
            continue  # a missing LOD only costs detail, never the model
        lod_urls[str(level)] = _file_proxy_url(lod_dest_key)
    lod_urls.setdefault("0", model_url)

    try:
        _begin_building_representation_mutation(session, building)
        building.model_url = model_url
        building.lod_urls = lod_urls
        building.generation_status = "completed"
        if entry.generation_engine:
            building.generation_engine = entry.generation_engine
        if entry.thumbnail_url:
            building.preview_url = entry.thumbnail_url
            building.preview_status = "completed"
        _mark_building_representation_stale(session, building)
        session.commit()
    except Exception as db_err:
        session.rollback()
        logger.warning("Library model apply failed for entry %s (non-fatal): %s", entry.id, db_err)
        return None

    # Bookkeeping below is optional polish — the reused model is committed.
    try:
        session.execute(
            sa_update(ModelLibraryEntry)
            .where(ModelLibraryEntry.id == entry.id)
            .values(use_count=sa_func.coalesce(ModelLibraryEntry.use_count, 0) + 1)
        )
        session.commit()
    except Exception as bump_err:
        session.rollback()
        logger.warning("Library use_count bump failed (non-fatal): %s", bump_err)
    log_api_usage_sync(
        provider=engine_id,
        operation="model_library_hit",
        credits_used=0,
        building_id=building_id,
        metadata={
            "library_entry_id": str(entry.id),
            "archetype_id": archetype_id,
        },
    )
    try:
        _propagate_model_to_siblings(session, building_id, model_url, lod_urls, building.preview_url)
    except Exception as prop_err:
        logger.warning(f"Model propagation to siblings failed (non-fatal): {prop_err}")

    logger.info(
        "Model library hit for building %s: %s -> %s (entry %s)",
        building_id, archetype_id, model_url, entry.id,
    )
    return {
        "status": "completed",
        "building_id": building_id,
        "model_url": model_url,
        "library_hit": True,
    }


@celery_app.task(
    bind=True,
    name="generate_3d_model_ai",
    max_retries=3,
    # Budget = full generation ceiling PLUS the cache wait: a claim-losing
    # waiter may block archetype_cache_wait_s before falling back to its own
    # full paid generation — the old limit soft-killed exactly those paid runs.
    soft_time_limit=MESHY_MAX_RUNTIME_S + settings.archetype_cache_wait_s,
    time_limit=MESHY_MAX_RUNTIME_S + settings.archetype_cache_wait_s + 120,
)
def generate_3d_model_ai(
    self, building_id: str, prompt: str, mode: str = "text",
    image_url: str = None, refine: bool = True,
    engine: str = "meshy", style_id: str = None,
    negative_prompt: str = None,
):
    """
    Generate a 3D model via an AI provider adapter.

    Processing owns orchestration, persistence, and storage. Provider adapters own
    the provider-specific API choreography.
    """
    logger.info(f"AI generating 3D model for building: {building_id} (mode={mode}, engine={engine})")
    session = _get_sync_session()
    building = None
    provider = None
    # Set only once the completed model is durably committed. Read in the error
    # handler WITHOUT touching the DB (the session may be broken there).
    completed_model_url: str | None = None
    # Archetype cache row THIS task claimed and must complete/fail. Read in
    # the error handler to release the claim.
    cache_claim = None

    try:
        from app.models.models import Building

        building = session.query(Building).filter_by(id=uuid.UUID(building_id)).first()
        if not building:
            raise ValueError(f"Building not found: {building_id}")

        provider = get_engine(engine)
        if not provider.is_available():
            raise RuntimeError(f"AI generation engine '{engine}' is not configured")

        style_changed = bool(
            style_id and building.architectural_style != style_id
        )
        if style_changed:
            _begin_building_representation_mutation(session, building)
        building.generation_status = "generating"
        building.generation_prompt = prompt
        building.generation_engine = provider.engine_id
        if style_id:
            building.architectural_style = style_id
        if style_changed:
            _mark_building_representation_stale(session, building)
        session.commit()

        architectural_negative_prompt = negative_prompt or (
            "blurry, low quality, deformed, floating objects, ground plane, "
            "background, people, vehicles, cartoon, anime, stylized, miniature"
        )

        def _progress_callback(progress: float, step: str) -> None:
            self.update_state(state="GENERATING", meta={"progress": progress, "step": step})

        def _task_callback(task_id: str) -> None:
            building.meshy_task_id = task_id
            session.commit()

        def _preview_callback(preview_data: bytes) -> None:
            preview_key = f"projects/{building.project_id}/models/{building_id}_preview.glb"
            _upload_to_storage(preview_key, preview_data, "model/gltf-binary")
            preview_url = _file_proxy_url(preview_key)
            _begin_building_representation_mutation(session, building)
            building.model_url = preview_url
            building.lod_urls = {"0": preview_url}
            _mark_building_representation_stale(session, building)
            session.commit()
            logger.info(f"Preview model saved for building {building_id}: {preview_url}")
            _progress_callback(0.5, "preview_ready")

        # --- Archetype model cache: never pay twice for the same key ------
        # Hit → apply instantly (0 credits). Miss → claim the key and
        # generate. Claim lost → wait for the claimant, then hit-apply or
        # fall back to an uncached generation.
        if settings.archetype_cache_enabled and mode == "text":
            from app.services.archetype_model_cache import claim_entry, normalize_cache_key

            cache_key = normalize_cache_key(building.specifications)
            if cache_key is not None:
                archetype_id, variant_id = cache_key
                entry, claimed = claim_entry(
                    session,
                    archetype_id,
                    variant_id,
                    provider.engine_id,
                    generation_mode=mode,
                    generation_prompt=prompt,
                )
                if claimed:
                    cache_claim = entry
                elif entry is not None:
                    if entry.status != "completed":
                        entry = _wait_for_cache_entry(session, entry.id, _progress_callback)
                    if entry is not None and entry.status == "completed":
                        return _apply_cached_model(
                            session, building_id, building, entry, provider.engine_id
                        )
                    logger.info(
                        "Cache unusable for building %s (%s/%s); generating uncached",
                        building_id, archetype_id, variant_id,
                    )

        # --- Model library: library-first, Meshy-fallback -----------------
        # A user-saved model of the same archetype substitutes for a paid
        # generation. Consulted only once the cache declined to resolve the
        # model (completed hits returned above); explicit image uploads and
        # buildings without an archetype key always generate.
        if settings.model_library_first_enabled and mode == "text":
            from app.services.archetype_model_cache import normalize_cache_key

            library_key = normalize_cache_key(building.specifications)
            if library_key is not None:
                library_result = None
                try:
                    library_entry = _find_library_model(session, building, library_key[0])
                    if library_entry is not None:
                        library_result = _apply_library_model(
                            session, building_id, building, library_entry,
                            library_key[0], provider.engine_id,
                        )
                except Exception as lib_err:
                    # Fail-open: the library is an optimization — a lookup
                    # failure must never block the paid fallback.
                    session.rollback()
                    logger.warning("Model library lookup failed (non-fatal): %s", lib_err)
                if library_result is not None:
                    if cache_claim is not None:
                        # This task will never complete the claim it just
                        # took — release it or same-key waiters block until
                        # the stale takeover (~47 min).
                        try:
                            from app.services.archetype_model_cache import fail_entry

                            fail_entry(session, cache_claim.id, "released: model library hit")
                        except Exception:
                            logger.warning(
                                "Could not release cache claim after library hit", exc_info=True
                            )
                        finally:
                            cache_claim = None
                    return library_result

        result = asyncio.run(provider.run_generation(
            prompt=prompt,
            mode=mode,
            image_url=image_url,
            refine=refine,
            negative_prompt=architectural_negative_prompt,
            building_id=building_id,
            progress_callback=_progress_callback,
            task_callback=_task_callback,
            preview_callback=_preview_callback,
        ))

        _progress_callback(0.85, "uploading")

        # Shrink before storage: raw Meshy GLBs ship 4K PBR textures and the
        # globe loads up to 20 models at once. Fail-open — optimize_glb
        # returns the original bytes on any error.
        if settings.glb_optimization_enabled:
            from app.processing.glb_optimizer import optimize_glb

            result.glb_data = optimize_glb(
                result.glb_data, max_texture_dim=settings.glb_max_texture_dim
            )

        project_id = building.project_id
        if cache_claim is not None:
            # Shared, immutable, project-independent — every future placement
            # of this archetype+variant points here.
            from app.services.archetype_model_cache import cache_storage_key

            model_key = cache_storage_key(cache_claim)
        else:
            model_suffix = "tripo" if provider.engine_id == "tripo" else "ai"
            model_key = f"projects/{project_id}/models/{building_id}_{model_suffix}.glb"
        _upload_to_storage(model_key, result.glb_data, "model/gltf-binary")
        model_url = _file_proxy_url(model_key)

        lod_urls = {"0": model_url}
        lod_keys_for_cache: dict[str, str] = {}
        for level, lod_glb_data in (result.lod_glb_data or {}).items():
            if cache_claim is not None:
                lod_key = (
                    f"archetype-cache/{cache_claim.archetype_id}/{cache_claim.variant_id}/"
                    f"{provider.engine_id}/{cache_claim.id}_lod{level}.glb"
                )
            else:
                lod_key = f"projects/{project_id}/models/{building_id}_{provider.engine_id}_lod{level}.glb"
            _upload_to_storage(lod_key, lod_glb_data, "model/gltf-binary")
            lod_urls[str(level)] = _file_proxy_url(lod_key)
            lod_keys_for_cache[str(level)] = lod_key

        _progress_callback(0.95, "updating")

        _begin_building_representation_mutation(session, building)
        building.model_url = model_url
        building.lod_urls = lod_urls
        building.generation_status = "completed"
        building.meshy_task_id = result.task_id
        _mark_building_representation_stale(session, building)
        # Commit the paid result IMMEDIATELY. Everything below is optional
        # polish; a crash or soft-kill during it must not lose a model that
        # Meshy already charged for and that is already uploaded to storage.
        session.commit()
        completed_model_url = model_url

        if cache_claim is not None:
            # Publish to the cache right after the paid commit — waiters are
            # polling this row. Thumbnail attaches later (non-blocking).
            try:
                from app.processing.glb_measure import measure_glb
                from app.services.archetype_model_cache import complete_entry

                dims = measure_glb(result.glb_data)
                complete_entry(
                    session,
                    cache_claim.id,
                    model_key=model_key,
                    size_bytes=len(result.glb_data),
                    source_task_id=result.task_id,
                    source_building_id=building.id,
                    lod_keys=lod_keys_for_cache or None,
                    metadata={"dimensions": dims} if dims else None,
                )
                completed_cache = cache_claim
                cache_claim = None  # completed — error handler must not fail it
            except Exception as cache_err:
                completed_cache = None
                logger.warning("Failed to complete cache entry (non-fatal): %s", cache_err)
                # Release the claim NOW — the task returns success from here,
                # so the error handler will never run and waiters would
                # otherwise block until stale takeover (~47 min).
                try:
                    session.rollback()
                    from app.services.archetype_model_cache import fail_entry

                    fail_entry(session, cache_claim.id, f"complete_entry failed: {cache_err}")
                except Exception:
                    logger.warning("Could not release cache claim after complete failure", exc_info=True)
                finally:
                    cache_claim = None
        else:
            completed_cache = None

        if result.thumbnail_url:
            try:
                import httpx as httpx_thumb
                thumb_resp = httpx_thumb.get(result.thumbnail_url, timeout=30.0, follow_redirects=True)
                # A 403 from an expired signed URL must not be stored as a
                # "PNG" — the cache copy would hand the garbage to every hit.
                thumb_resp.raise_for_status()
                thumb_data = thumb_resp.content
                thumb_key = f"projects/{building.project_id}/thumbnails/{building_id}.png"
                _upload_to_storage(thumb_key, thumb_data, "image/png")
                building.preview_url = f"/api/v1/files/{thumb_key}"
                building.preview_status = "completed"
                session.commit()
                logger.info(f"Thumbnail saved for building {building_id}")
                if completed_cache is not None:
                    # Own copy under archetype-cache/ so the cache never
                    # dangles on a project-scoped object.
                    from app.services.archetype_model_cache import set_entry_thumbnail

                    cache_thumb_key = (
                        f"archetype-cache/{completed_cache.archetype_id}/"
                        f"{completed_cache.variant_id}/{completed_cache.engine}/"
                        f"{completed_cache.id}_thumb.png"
                    )
                    _upload_to_storage(cache_thumb_key, thumb_data, "image/png")
                    set_entry_thumbnail(session, completed_cache.id, cache_thumb_key)
            except Exception as thumb_err:
                session.rollback()
                logger.warning(f"Failed to save thumbnail (non-fatal): {thumb_err}")

        try:
            _propagate_model_to_siblings(session, building_id, model_url, lod_urls, building.preview_url)
        except Exception as prop_err:
            logger.warning(f"Model propagation to siblings failed (non-fatal): {prop_err}")

        logger.info(f"AI 3D model generated for building {building_id}: {model_url}")
        return {
            "status": "completed",
            "building_id": building_id,
            "model_url": model_url,
        }

    except Exception as exc:
        logger.error(f"AI 3D generation failed for building {building_id}: {exc}")
        # Release an unfinished cache claim FIRST — other workers are waiting
        # on this row and must be able to take over the key.
        if cache_claim is not None:
            try:
                session.rollback()  # clear any broken transaction state
                from app.services.archetype_model_cache import fail_entry

                fail_entry(session, cache_claim.id, str(exc))
            except Exception as cache_err:
                logger.warning("Failed to release cache claim (non-fatal): %s", cache_err)
                # A dead connection makes even rollback raise — never let it
                # mask the real error or skip the failure bookkeeping below.
                try:
                    session.rollback()
                except Exception:
                    pass
        # Usage rows have a FK to buildings — logging against a deleted
        # building just adds an IntegrityError on top of the real failure.
        log_api_usage_sync(
            provider=provider.engine_id if provider else engine,
            operation=f"{mode}_to_3d",
            status="failed",
            building_id=building_id if building is not None else None,
        )
        # Never bury a generation that already succeeded and was committed —
        # an exception in the optional tail (thumbnail, sibling propagation)
        # used to flip a completed, uploaded model to "failed".
        if completed_model_url is not None:
            logger.warning(
                "Building %s already completed; ignoring post-success error: %s", building_id, exc
            )
            return {"status": "completed", "building_id": building_id, "model_url": completed_model_url}

        try:
            if building is not None:
                building.generation_status = "failed"
                # Persist WHY — the UI and post-mortems read this; failures
                # with an empty error field are invisible to the user.
                specs = dict(building.specifications or {})
                specs["generation_error"] = str(exc)[:400]
                building.specifications = specs
                session.commit()
        except Exception as inner_exc:
            session.rollback()
            logger.warning("Failed to mark building %s as failed: %s", building_id, inner_exc)
        # A missing building is terminal (it was deleted) — retrying can never
        # succeed and previously burned all retries 30s apart.
        if building is None:
            raise
        # Permanent client errors (bad prompt/params) can only fail again —
        # don't retry, just leave the building failed with its captured reason.
        from app.generation.meshy_client import MeshyClientError
        if isinstance(exc, MeshyClientError):
            return {"status": "failed", "error": str(exc)[:200]}
        # Running past the ceiling is terminal too. A retry re-runs the ENTIRE
        # paid generation (a fresh preview + refine ≈ 20 Meshy credits) and, at
        # these limits, would almost certainly hit the same wall — the old
        # behaviour silently burned 4x credits per stuck building.
        if isinstance(exc, (TimeoutError, SoftTimeLimitExceeded)):
            return {"status": "failed", "error": str(exc)[:200]}
        # Exponential backoff for genuinely TRANSIENT failures (network, 5xx).
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
    finally:
        session.close()

@celery_app.task(
    bind=True,
    name="prewarm_archetype_model",
    max_retries=0,
    soft_time_limit=MESHY_MAX_RUNTIME_S,
    time_limit=MESHY_MAX_RUNTIME_S + 120,
)
def prewarm_archetype_model(
    self,
    archetype_id: str,
    variant_id: str = "default",
    engine: str = "meshy",
    mode: str = "text",
    prompt: str | None = None,
    image_data_uri: str | None = None,
    image_data_uris: list[str] | None = None,
    isolate_images: bool | None = None,
    target_polycount: int | None = None,
    clean_images: str | None = None,
    multiview_prompt: str | None = None,
):
    """Warm the archetype model cache without a Building — claim the key,
    generate, optimize, upload to archetype-cache/, complete the row.

    mode="multi_image" sends image_data_uris (street card first, then the
    45°/90° aerials) to Meshy multi-image-to-3D; prompt becomes the Meshy
    texture_prompt. isolate_images: None = per-mode default (image -> True,
    multi_image -> False — rembg mangles context-rich aerials).
    multiview_prompt (multi_image only) switches to the two-stage CHAIN:
    Meshy Image-to-Image multi-view synth (this prompt) -> multi_image_to_3d.
    It auto-isolates + harmonizes views, so clean_images/isolate are redundant.
    clean_images: "entourage" or "building_only" runs a Gemini removal edit
    on every input first (people/vehicles fuse into mutant geometry)."""
    logger.info(
        "Pre-warming archetype model %s/%s (engine=%s, mode=%s)",
        archetype_id, variant_id, engine, mode,
    )
    session = _get_sync_session()
    entry = None
    claimed = False
    try:
        from app.services.archetype_model_cache import (
            cache_storage_key,
            claim_entry,
            complete_entry,
            fail_entry,
            set_entry_thumbnail,
        )

        entry, claimed = claim_entry(
            session, archetype_id, variant_id, engine,
            generation_mode=mode, generation_prompt=prompt,
        )
        if not claimed:
            status = entry.status if entry is not None else "missing"
            logger.info("Pre-warm skipped for %s/%s: entry is %s", archetype_id, variant_id, status)
            return {"status": f"skipped_{status}", "archetype_id": archetype_id, "variant_id": variant_id}

        provider = get_engine(engine)
        if not provider.is_available():
            raise RuntimeError(f"AI generation engine '{engine}' is not configured")

        if clean_images:
            # Gemini removal edit BEFORE isolation/submission: entourage in
            # the refs becomes fused mesh geometry otherwise. Fail-open.
            import base64 as b64

            from app.processing.image_cleanup import clean_reference_image

            def _clean_uri(uri: str) -> str:
                if not uri or not uri.startswith("data:"):
                    return uri
                header, _, payload = uri.partition(",")
                cleaned = clean_reference_image(b64.b64decode(payload), level=clean_images)
                cleaned_mime = (
                    "image/png" if cleaned[:8] == b"\x89PNG\r\n\x1a\n" else "image/jpeg"
                )
                return f"data:{cleaned_mime};base64," + b64.b64encode(cleaned).decode()

            if image_data_uri:
                image_data_uri = _clean_uri(image_data_uri)
            if image_data_uris:
                image_data_uris = [_clean_uri(u) for u in image_data_uris]

        do_isolate = isolate_images if isolate_images is not None else (mode == "image")
        if do_isolate and mode == "image" and image_data_uri and image_data_uri.startswith("data:"):
            # Matte out neighbours before Meshy models them into the mesh
            # (pilot failure mode 2026-07-10). Fail-open without rembg.
            import base64 as b64

            from app.processing.image_isolation import isolate_building

            header, _, payload = image_data_uri.partition(",")
            isolated = isolate_building(b64.b64decode(payload))
            image_data_uri = "data:image/png;base64," + b64.b64encode(isolated).decode()
        elif do_isolate and mode == "multi_image" and image_data_uris:
            # Opt-in only, and only the street card (index 0) — the aerials
            # need their context intact for Meshy's view fusion.
            import base64 as b64

            from app.processing.image_isolation import isolate_building

            first = image_data_uris[0]
            if first.startswith("data:"):
                header, _, payload = first.partition(",")
                isolated = isolate_building(b64.b64decode(payload))
                image_data_uris = [
                    "data:image/png;base64," + b64.b64encode(isolated).decode(),
                    *image_data_uris[1:],
                ]

        def _progress_callback(progress: float, step: str) -> None:
            self.update_state(state="GENERATING", meta={"progress": progress, "step": step})

        result = asyncio.run(provider.run_generation(
            prompt=prompt or archetype_id.replace("_", " "),
            mode=mode,
            image_url=image_data_uri,
            image_urls=image_data_uris,
            target_polycount=target_polycount,
            multiview_prompt=multiview_prompt,
            refine=True,
            negative_prompt=(
                "blurry, low quality, deformed, floating objects, ground plane, "
                "background, people, vehicles, cartoon, anime, stylized, miniature"
            ),
            building_id=None,
            progress_callback=_progress_callback,
        ))

        if settings.glb_optimization_enabled:
            from app.processing.glb_optimizer import optimize_glb

            result.glb_data = optimize_glb(
                result.glb_data, max_texture_dim=settings.glb_max_texture_dim
            )

        model_key = cache_storage_key(entry)
        _upload_to_storage(model_key, result.glb_data, "model/gltf-binary")
        lod_keys_for_cache: dict[str, str] = {}
        for level, lod_glb_data in (result.lod_glb_data or {}).items():
            lod_key = (
                f"archetype-cache/{archetype_id}/{variant_id}/{engine}/{entry.id}_lod{level}.glb"
            )
            _upload_to_storage(lod_key, lod_glb_data, "model/gltf-binary")
            lod_keys_for_cache[str(level)] = lod_key
        from app.processing.glb_measure import measure_glb

        dims = measure_glb(result.glb_data)
        complete_entry(
            session,
            entry.id,
            model_key=model_key,
            size_bytes=len(result.glb_data),
            source_task_id=result.task_id,
            lod_keys=lod_keys_for_cache or None,
            metadata={"dimensions": dims} if dims else None,
        )

        if result.thumbnail_url:
            try:
                import httpx as httpx_thumb

                thumb_resp = httpx_thumb.get(result.thumbnail_url, timeout=30.0, follow_redirects=True)
                thumb_resp.raise_for_status()
                thumb_data = thumb_resp.content
                thumb_key = (
                    f"archetype-cache/{archetype_id}/{variant_id}/{engine}/{entry.id}_thumb.png"
                )
                _upload_to_storage(thumb_key, thumb_data, "image/png")
                set_entry_thumbnail(session, entry.id, thumb_key)
            except Exception as thumb_err:
                session.rollback()
                logger.warning("Pre-warm thumbnail failed (non-fatal): %s", thumb_err)

        # When a cleanup edit ran, persist what Meshy actually saw — the
        # only way to distinguish "bad edit" from "bad fusion" in QA.
        if clean_images and image_data_uris:
            import base64 as b64

            for i, uri in enumerate(image_data_uris):
                try:
                    header, _, payload = uri.partition(",")
                    ext = "png" if "png" in header else "jpg"
                    _upload_to_storage(
                        f"archetype-cache/{archetype_id}/{variant_id}/{engine}/{entry.id}_input_{i}.{ext}",
                        b64.b64decode(payload),
                        "image/png" if ext == "png" else "image/jpeg",
                    )
                except Exception as input_err:
                    logger.warning("Cleaned-input upload %d failed (non-fatal): %s", i, input_err)

        # Multi-image tasks return 4 cardinal-view thumbnails — persist them
        # now (Meshy asset URLs expire) under deterministic keys the QA
        # tooling can derive from the entry id.
        cardinal_thumbs = (result.metadata or {}).get("thumbnail_urls") or {}
        if isinstance(cardinal_thumbs, dict):
            import httpx as httpx_thumb

            for view, url in cardinal_thumbs.items():
                if not url or view not in ("front", "right", "back", "left"):
                    continue
                try:
                    view_resp = httpx_thumb.get(url, timeout=30.0, follow_redirects=True)
                    view_resp.raise_for_status()
                    _upload_to_storage(
                        f"archetype-cache/{archetype_id}/{variant_id}/{engine}/{entry.id}_thumb_{view}.png",
                        view_resp.content,
                        "image/png",
                    )
                except Exception as view_err:
                    logger.warning("Multi-view thumb %s failed (non-fatal): %s", view, view_err)

        logger.info(
            "Pre-warmed %s/%s -> %s (%.1fMB)",
            archetype_id, variant_id, model_key, len(result.glb_data) / 1e6,
        )
        return {
            "status": "completed",
            "archetype_id": archetype_id,
            "variant_id": variant_id,
            "cache_id": str(entry.id),
            "model_key": model_key,
            "size_bytes": len(result.glb_data),
        }
    except Exception as exc:
        logger.error("Pre-warm failed for %s/%s: %s", archetype_id, variant_id, exc)
        if claimed and entry is not None:
            try:
                session.rollback()
                from app.services.archetype_model_cache import fail_entry

                fail_entry(session, entry.id, str(exc))
            except Exception as cache_err:
                session.rollback()
                logger.warning("Failed to release pre-warm claim: %s", cache_err)
        log_api_usage_sync(
            provider=engine,
            operation="prewarm",
            status="failed",
            metadata={"archetype_id": archetype_id, "variant_id": variant_id},
        )
        return {"status": "failed", "error": str(exc)[:300]}
    finally:
        session.close()


@celery_app.task(bind=True, name="generate_3d_model")
def generate_3d_model(self, building_id: str, building_data: dict):
    """
    Generate 3D model from normalized building data.

    Pipeline:
    1. Create building geometry from footprint
    2. Export full-detail GLB
    3. Generate LOD variants (simplified meshes)
    4. Upload all GLBs to storage
    5. Update building record with model URL + LOD URLs
    """
    logger.info(f"Generating 3D model for building: {building_id}")
    session = _get_sync_session()
    building = None

    try:
        self.update_state(state="GENERATING", meta={"progress": 0.1, "step": "geometry"})

        from app.models.models import Building

        building = session.query(Building).filter_by(id=uuid.UUID(building_id)).first()
        if not building:
            raise ValueError(f"Building not found: {building_id}")

        building.generation_status = "generating"
        session.commit()

        # Step 1: Generate building geometry
        from app.generation.geometry.building_generator import (
            BuildingGenerator, GLBExporter, LODGenerator,
        )
        import trimesh

        generator = BuildingGenerator()

        # Prepare data for generator - ensure footprint is available
        gen_data = {
            "footprint": building_data.get("footprint", [[0, 0], [20, 0], [20, 15], [0, 15], [0, 0]]),
            "height": building_data.get("height_meters", 10.0),
            "floors": building_data.get("floor_count", 3),
            "floor_height": building_data.get("floor_height_meters", 3.33),
            "roof_type": building_data.get("roof_type", "flat"),
            "features": {"windows": True},
        }

        # Load architectural style if set on building
        style = None
        try:
            if building.architectural_style:
                from app.generation.styles import get_style
                style = get_style(building.architectural_style)
        except Exception as style_err:
            logger.warning("Failed to load style '%s' for building %s: %s", building.architectural_style, building_id, style_err)

        scene = generator.generate_building(gen_data, style=style)

        if not scene.geometry:
            raise ValueError(f"Building generation produced empty scene for {building_id}")

        self.update_state(state="GENERATING", meta={"progress": 0.3, "step": "exporting"})

        # Step 2: Export full-detail GLB (LOD 0)
        glb_data = GLBExporter.export_to_bytes(scene)

        self.update_state(state="GENERATING", meta={"progress": 0.4, "step": "generating_lods"})

        # Step 3: Generate LOD variants
        # Concatenate all meshes in the scene into a single Trimesh for LOD processing
        lod_glbs = {}
        try:
            if isinstance(scene, trimesh.Scene):
                combined = scene.dump(concatenate=True)
            else:
                combined = scene

            if isinstance(combined, trimesh.Trimesh) and len(combined.faces) > 10:
                lods = LODGenerator.generate_lods(combined)
                for level, lod_mesh in lods.items():
                    if level == 0:
                        continue  # LOD 0 is the full scene we already exported
                    lod_scene = trimesh.Scene([lod_mesh])
                    lod_glbs[level] = GLBExporter.export_to_bytes(lod_scene)
                    logger.info(f"LOD {level} exported: {len(lod_glbs[level])} bytes")
            else:
                logger.info("Mesh too simple for LOD generation, using full detail only")
        except Exception as e:
            logger.warning(f"LOD generation failed (non-fatal): {e}")

        self.update_state(state="GENERATING", meta={"progress": 0.6, "step": "uploading"})

        project_id = building.project_id

        # Upload full-detail model (LOD 0)
        model_key = f"projects/{project_id}/models/{building_id}.glb"
        _upload_to_storage(model_key, glb_data, "model/gltf-binary")
        model_url = _file_proxy_url(model_key)

        # Upload LOD variants
        lod_urls = {"0": model_url}
        for level, lod_data in lod_glbs.items():
            lod_key = f"projects/{project_id}/models/{building_id}_lod{level}.glb"
            _upload_to_storage(lod_key, lod_data, "model/gltf-binary")
            lod_url = _file_proxy_url(lod_key)
            lod_urls[str(level)] = lod_url
            logger.info(f"LOD {level} uploaded: {lod_url}")

        self.update_state(state="GENERATING", meta={"progress": 0.9, "step": "updating"})

        # Step 5: Update building record with model URL + LOD URLs
        _begin_building_representation_mutation(session, building)
        building.model_url = model_url
        building.lod_urls = lod_urls
        building.generation_status = "completed"
        _mark_building_representation_stale(session, building)
        session.commit()

        logger.info(
            f"3D model generated for building {building_id}: "
            f"{model_url} ({len(lod_urls)} LOD levels)"
        )
        return {
            "status": "completed",
            "building_id": building_id,
            "model_url": model_url,
            "lod_urls": lod_urls,
        }

    except Exception as exc:
        logger.error(f"3D generation failed for building {building_id}: {exc}")
        try:
            session.rollback()
            if building is None:
                from app.models.models import Building
                building = session.query(Building).filter_by(id=uuid.UUID(building_id)).first()
            if building:
                building.generation_status = "failed"
                session.commit()
        except Exception as inner_exc:
            session.rollback()
            logger.warning("Failed to mark building %s as failed: %s", building_id, inner_exc)
        raise
    finally:
        session.close()

