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
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.usage_logger import log_api_usage_sync
from app.tasks.worker import celery_app

logger = logging.getLogger(__name__)
settings = get_settings()


def _get_sync_session() -> Session:
    """Create a sync SQLAlchemy session for use in Celery tasks."""
    engine = create_engine(settings.database_url_sync)
    return Session(engine)


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
        except Exception:
            pass  # Bucket exists or auto-creation not supported (R2)
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
            floors = ab.get("floor_count") or max(1, int(height / 3.0))
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
        # No AI interpretation — build from extracted coordinates
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
        # Minimal fallback — create a single default building
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


@celery_app.task(bind=True, name="process_document", max_retries=3)
def process_document(self, document_id: str):
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

        # Step 4: AI interpretation using Claude — prioritize floor plans & elevations
        interpretation_result = {}
        try:
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

                    # Skip text-only and schedule pages — no architectural drawings
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
                            # Unknown — try floor plan first, fall back to elevation
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
                            # Single building from floor plan — tag with confidence
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
        except Exception as e:
            logger.warning(f"AI interpretation failed (non-fatal): {e}")

        self.update_state(state="PROCESSING", meta={"progress": 0.7, "step": "normalizing"})

        # Step 5: Normalize extracted data
        normalized_buildings = _normalize_extraction_data(extraction_result, interpretation_result)

        self.update_state(state="PROCESSING", meta={"progress": 0.8, "step": "generating_3d"})

        # Step 6: Create building records and trigger 3D generation
        created_building_ids = []
        for bdata in normalized_buildings:
            building = Building(
                project_id=document.project_id,
                name=bdata["name"],
                height_meters=bdata["height_meters"],
                floor_count=bdata["floor_count"],
                floor_height_meters=bdata["floor_height_meters"],
                roof_type=bdata["roof_type"],
                specifications=bdata.get("specifications"),
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

            # Trigger 3D model generation for this building
            generate_3d_model.delay(str(building.id), bdata)

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

        logger.info(f"Document processing complete: {document_id}, created {len(created_building_ids)} buildings")
        return {"status": "completed", "document_id": document_id, "building_ids": created_building_ids}

    except Exception as exc:
        logger.error(f"Document processing failed: {document_id} - {exc}")
        try:
            from app.models.models import Document
            document = session.query(Document).filter_by(id=uuid.UUID(document_id)).first()
            if document:
                document.processing_status = "failed"
                document.extracted_data = {"error": str(exc)}
                session.commit()
        except Exception:
            session.rollback()
        raise self.retry(exc=exc, countdown=60)
    finally:
        session.close()
        # Clean up temp file
        import os
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def _propagate_model_to_siblings(session: Session, building_id: str, model_url: str, lod_urls: dict):
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

        # Found the zone — propagate to siblings
        sibling_count = 0
        for bid_str in bid_list:
            if str(bid_str) == str(building_id):
                continue  # Skip the source building
            sibling = session.query(Building).filter_by(id=uuid.UUID(str(bid_str))).first()
            if sibling:
                sibling.model_url = model_url
                sibling.lod_urls = lod_urls
                sibling.generation_status = "completed"
                sibling_count += 1

        if sibling_count > 0:
            session.commit()
            logger.info(
                f"Propagated model from building {building_id} to {sibling_count} sibling(s)"
            )
        break  # A building belongs to at most one zone


@celery_app.task(bind=True, name="generate_3d_model_ai", max_retries=2)
def generate_3d_model_ai(
    self, building_id: str, prompt: str, mode: str = "text",
    image_url: str = None, refine: bool = True,
    engine: str = "meshy", style_id: str = None,
    negative_prompt: str = None,
):
    """
    Generate a 3D model via AI API (Meshy or Tripo3D).

    Pipeline:
    1. Call AI API (text-to-3d or image-to-3d)
    2. Poll until complete
    3. Download GLB file
    4. Upload to MinIO
    5. Update building.model_url in DB
    6. Update building.generation_status = 'completed'
    """
    logger.info(f"AI generating 3D model for building: {building_id} (mode={mode}, engine={engine})")
    session = _get_sync_session()

    try:
        from app.models.models import Building
        building = session.query(Building).filter_by(id=uuid.UUID(building_id)).first()
        if not building:
            raise ValueError(f"Building not found: {building_id}")

        building.generation_status = "generating"
        building.generation_prompt = prompt
        building.generation_engine = engine
        if style_id:
            building.architectural_style = style_id
        session.commit()

        architectural_negative_prompt = negative_prompt or (
            "blurry, low quality, deformed, floating objects, ground plane, "
            "background, people, vehicles, cartoon, anime, stylized, miniature"
        )

        # --- Tripo3D engine ---
        if engine == "tripo":
            self.update_state(state="GENERATING", meta={"progress": 0.1, "step": "calling_tripo"})

            from app.generation.tripo_client import TripoClient
            tripo = TripoClient()

            if mode == "image" and image_url:
                task_id = asyncio.run(tripo.image_to_3d(image_url))
                log_api_usage_sync(provider="tripo", operation="image_to_3d", credits_used=30, task_id=task_id, building_id=building_id)
            else:
                task_id = asyncio.run(tripo.text_to_3d(prompt, negative_prompt=architectural_negative_prompt))
                log_api_usage_sync(provider="tripo", operation="text_to_3d", credits_used=30, task_id=task_id, building_id=building_id)

            building.meshy_task_id = task_id
            session.commit()

            self.update_state(state="GENERATING", meta={"progress": 0.3, "step": "polling_tripo"})
            result = asyncio.run(tripo.poll_until_done(task_id, timeout=120))

            model_url_remote = result.get("model_url") or result.get("output", {}).get("model", {}).get("url")
            if not model_url_remote:
                raise RuntimeError("No model URL in Tripo result")

            # Optionally run smart_low_poly for web-ready LOD
            lod_model_url_remote = None
            try:
                self.update_state(state="GENERATING", meta={"progress": 0.5, "step": "smart_low_poly"})
                lp_task_id = asyncio.run(tripo.smart_low_poly(task_id))
                lp_result = asyncio.run(tripo.poll_until_done(lp_task_id, timeout=120))
                lod_model_url_remote = lp_result.get("model_url") or lp_result.get("output", {}).get("model", {}).get("url")
                log_api_usage_sync(provider="tripo", operation="retopology", credits_used=10, task_id=lp_task_id, building_id=building_id)
            except Exception as lp_err:
                logger.warning(f"Tripo smart_low_poly failed (non-fatal): {lp_err}")

            self.update_state(state="GENERATING", meta={"progress": 0.7, "step": "downloading"})
            glb_data = asyncio.run(tripo.download_model(model_url_remote))

            self.update_state(state="GENERATING", meta={"progress": 0.85, "step": "uploading"})
            project_id = building.project_id
            model_key = f"projects/{project_id}/models/{building_id}_tripo.glb"
            model_url = _upload_to_storage(model_key, glb_data, "model/gltf-binary")

            lod_urls = {"0": model_url}
            if lod_model_url_remote:
                try:
                    lod_glb = asyncio.run(tripo.download_model(lod_model_url_remote))
                    lod_key = f"projects/{project_id}/models/{building_id}_tripo_lod1.glb"
                    lod_url = _upload_to_storage(lod_key, lod_glb, "model/gltf-binary")
                    lod_urls["1"] = lod_url
                except Exception:
                    pass

        # --- Meshy engine (default) ---
        else:
            self.update_state(state="GENERATING", meta={"progress": 0.1, "step": "calling_meshy"})

            from app.generation.meshy_client import MeshyClient
            client = MeshyClient()

            if mode == "image" and image_url:
                task_id = asyncio.run(client.image_to_3d(image_url))
                task_type = "image"
                log_api_usage_sync(provider="meshy", operation="image_to_3d", credits_used=20, task_id=task_id, building_id=building_id)
            else:
                task_id = asyncio.run(client.text_to_3d_preview(
                    prompt, negative_prompt=architectural_negative_prompt
                ))
                task_type = "text"
                log_api_usage_sync(provider="meshy", operation="text_to_3d_preview", credits_used=10, task_id=task_id, building_id=building_id)

            building.meshy_task_id = task_id
            session.commit()

            self.update_state(state="GENERATING", meta={"progress": 0.3, "step": "polling"})

            result = asyncio.run(client.poll_until_done(task_id, timeout=300, task_type=task_type))
            logger.info(f"Meshy preview result keys: {list(result.keys())}, model_urls: {result.get('model_urls', {}).keys() if result.get('model_urls') else 'NONE'}")

            # For text mode, run refine step to get PBR textures (preview has no textures)
            if mode == "text" and refine:
                self.update_state(state="GENERATING", meta={"progress": 0.5, "step": "refining"})
                try:
                    refine_task_id = asyncio.run(client.text_to_3d_refine(
                        task_id,
                        texture_prompt=f"realistic architectural materials and textures for: {prompt[:200]}"
                    ))
                    logger.info(f"Refine task started: {refine_task_id} (from preview {task_id})")
                    building.meshy_task_id = refine_task_id
                    session.commit()
                    result = asyncio.run(client.poll_until_done(refine_task_id, timeout=600, task_type="text"))
                    logger.info(f"Meshy refine result keys: {list(result.keys())}, model_urls: {result.get('model_urls', {}).keys() if result.get('model_urls') else 'NONE'}")
                    log_api_usage_sync(provider="meshy", operation="text_to_3d_refine", credits_used=10, task_id=refine_task_id, building_id=building_id)
                except Exception as refine_err:
                    logger.error(f"Refine step FAILED for building {building_id}: {refine_err}", exc_info=True)
                    logger.warning("Falling back to preview model (will lack textures)")
            elif mode == "text":
                logger.info(f"Refine disabled for building {building_id} — using preview model")

            self.update_state(state="GENERATING", meta={"progress": 0.7, "step": "downloading"})

            # Extract the GLB URL from result
            glb_url = None
            model_urls = result.get("model_urls", {})
            glb_url = model_urls.get("glb") or model_urls.get("obj")

            if not glb_url:
                raise RuntimeError("No GLB model URL in Meshy result")

            # Download the GLB file
            import httpx as httpx_sync
            glb_data = httpx_sync.get(glb_url, timeout=60.0).content

            self.update_state(state="GENERATING", meta={"progress": 0.85, "step": "uploading"})

            project_id = building.project_id
            model_key = f"projects/{project_id}/models/{building_id}_ai.glb"
            model_url = _upload_to_storage(model_key, glb_data, "model/gltf-binary")

            lod_urls = {"0": model_url}

        self.update_state(state="GENERATING", meta={"progress": 0.95, "step": "updating"})

        # Update building record
        building.model_url = model_url
        building.lod_urls = lod_urls
        building.generation_status = "completed"
        session.commit()

        # Propagate model to sibling buildings in the same zone (multi-unit)
        try:
            _propagate_model_to_siblings(session, building_id, model_url, lod_urls)
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
        log_api_usage_sync(provider=engine, operation=f"{mode}_to_3d", status="failed", building_id=building_id)
        try:
            from app.models.models import Building
            building = session.query(Building).filter_by(id=uuid.UUID(building_id)).first()
            if building:
                building.generation_status = "failed"
                session.commit()
        except Exception:
            session.rollback()
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

    try:
        self.update_state(state="GENERATING", meta={"progress": 0.1, "step": "geometry"})

        # Step 1: Generate building geometry
        from app.generation.geometry.building_generator import (
            BuildingGenerator, GLBExporter, LODGenerator,
        )
        import trimesh

        generator = BuildingGenerator()

        # Prepare data for generator — ensure footprint is available
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
            from app.models.models import Building as BuildingModel
            building_record = session.query(BuildingModel).filter_by(id=uuid.UUID(building_id)).first()
            if building_record and building_record.architectural_style:
                from app.generation.styles import get_style
                style = get_style(building_record.architectural_style)
        except Exception:
            pass

        scene = generator.generate_building(gen_data, style=style)

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

        # Step 4: Upload all GLBs to S3/MinIO
        from app.models.models import Building
        building = session.query(Building).filter_by(id=uuid.UUID(building_id)).first()
        if not building:
            raise ValueError(f"Building not found: {building_id}")

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
        session.rollback()
        raise
    finally:
        session.close()
