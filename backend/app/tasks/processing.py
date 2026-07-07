"""
Async tasks for document processing pipeline.
"""

import asyncio
import logging
import tempfile
import uuid
from datetime import datetime, timezone

import boto3
from botocore.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.usage_logger import log_api_usage_sync
from app.generation.engine import get_engine
from app.tasks.worker import celery_app

logger = logging.getLogger(__name__)
settings = get_settings()

_sync_engine = None
_sync_session_factory = None
_sync_pool_size = 5 if settings.app_env == "production" else 20
_sync_max_overflow = 3 if settings.app_env == "production" else 10


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
        sibling_count = 0
        for bid_str in bid_list:
            if str(bid_str) == str(building_id):
                continue  # Skip the source building
            sibling = session.query(Building).filter_by(id=uuid.UUID(str(bid_str))).first()
            if sibling:
                sibling.model_url = model_url
                sibling.lod_urls = lod_urls
                sibling.generation_status = "completed"
                if preview_url:
                    sibling.preview_url = preview_url
                    sibling.preview_status = "completed"
                sibling_count += 1

        if sibling_count > 0:
            session.commit()
            logger.info(
                f"Propagated model from building {building_id} to {sibling_count} sibling(s)"
            )
        break  # A building belongs to at most one zone


@celery_app.task(bind=True, name="generate_3d_model_ai", max_retries=2, soft_time_limit=900, time_limit=960)
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

    try:
        from app.models.models import Building

        building = session.query(Building).filter_by(id=uuid.UUID(building_id)).first()
        if not building:
            raise ValueError(f"Building not found: {building_id}")

        provider = get_engine(engine)
        if not provider.is_available():
            raise RuntimeError(f"AI generation engine '{engine}' is not configured")

        building.generation_status = "generating"
        building.generation_prompt = prompt
        building.generation_engine = provider.engine_id
        if style_id:
            building.architectural_style = style_id
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
            preview_s3_url = _upload_to_storage(preview_key, preview_data, "model/gltf-binary")
            building.model_url = preview_s3_url
            building.lod_urls = {"0": preview_s3_url}
            session.commit()
            logger.info(f"Preview model saved for building {building_id}: {preview_s3_url}")
            _progress_callback(0.5, "preview_ready")

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

        project_id = building.project_id
        model_suffix = "tripo" if provider.engine_id == "tripo" else "ai"
        model_key = f"projects/{project_id}/models/{building_id}_{model_suffix}.glb"
        model_url = _upload_to_storage(model_key, result.glb_data, "model/gltf-binary")

        lod_urls = {"0": model_url}
        for level, lod_glb_data in (result.lod_glb_data or {}).items():
            lod_key = f"projects/{project_id}/models/{building_id}_{provider.engine_id}_lod{level}.glb"
            lod_urls[str(level)] = _upload_to_storage(lod_key, lod_glb_data, "model/gltf-binary")

        _progress_callback(0.95, "updating")

        building.model_url = model_url
        building.lod_urls = lod_urls
        building.generation_status = "completed"
        building.meshy_task_id = result.task_id

        if result.thumbnail_url:
            try:
                import httpx as httpx_thumb
                thumb_data = httpx_thumb.get(result.thumbnail_url, timeout=30.0).content
                thumb_key = f"projects/{building.project_id}/thumbnails/{building_id}.png"
                _upload_to_storage(thumb_key, thumb_data, "image/png")
                building.preview_url = f"/api/v1/files/{thumb_key}"
                building.preview_status = "completed"
                logger.info(f"Thumbnail saved for building {building_id}")
            except Exception as thumb_err:
                logger.warning(f"Failed to save thumbnail (non-fatal): {thumb_err}")

        session.commit()

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
        log_api_usage_sync(
            provider=provider.engine_id if provider else engine,
            operation=f"{mode}_to_3d",
            status="failed",
            building_id=building_id,
        )
        try:
            if building is None:
                from app.models.models import Building
                building = session.query(Building).filter_by(id=uuid.UUID(building_id)).first()
            if building:
                building.generation_status = "failed"
                session.commit()
        except Exception as inner_exc:
            session.rollback()
            logger.warning("Failed to mark building %s as failed: %s", building_id, inner_exc)
        raise self.retry(exc=exc, countdown=30)
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
        model_url = _upload_to_storage(model_key, glb_data, "model/gltf-binary")

        # Upload LOD variants
        lod_urls = {"0": model_url}
        for level, lod_data in lod_glbs.items():
            lod_key = f"projects/{project_id}/models/{building_id}_lod{level}.glb"
            lod_url = _upload_to_storage(lod_key, lod_data, "model/gltf-binary")
            lod_urls[str(level)] = lod_url
            logger.info(f"LOD {level} uploaded: {lod_url}")

        self.update_state(state="GENERATING", meta={"progress": 0.9, "step": "updating"})

        # Step 5: Update building record with model URL + LOD URLs
        building.model_url = model_url
        building.lod_urls = lod_urls
        building.generation_status = "completed"
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

