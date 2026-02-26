"""
Celery task for generating AI render preview images via Stability AI.
"""

import asyncio
import logging
import uuid

from app.core.config import get_settings
from app.tasks.worker import celery_app

logger = logging.getLogger(__name__)
settings = get_settings()


def _get_sync_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    engine = create_engine(settings.database_url_sync)
    return Session(engine)


def _upload_to_storage(key: str, data: bytes, content_type: str) -> str:
    import boto3
    from botocore.config import Config
    s3 = boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
        config=Config(signature_version="s3v4"),
    )
    try:
        s3.head_bucket(Bucket=settings.s3_bucket_name)
    except Exception:
        try:
            s3.create_bucket(Bucket=settings.s3_bucket_name)
        except Exception:
            pass
    s3.put_object(
        Bucket=settings.s3_bucket_name,
        Key=key,
        Body=data,
        ContentType=content_type,
    )
    return f"{settings.s3_endpoint_url}/{settings.s3_bucket_name}/{key}"


@celery_app.task(bind=True, name="generate_render_preview", max_retries=2)
def generate_render_preview(
    self,
    building_id: str,
    prompt: str,
    source_type: str = "text",
    source_image_url: str | None = None,
    style_id: str | None = None,
):
    """
    Generate a photorealistic AI render preview for a building.

    Pipeline:
    1. Enrich prompt with style info
    2. Call Stability AI (text-to-image or image-to-image)
    3. Upload PNG to MinIO
    4. Create RenderPreview record
    5. Update building.preview_url and preview_status
    """
    logger.info(f"Generating render preview for building: {building_id}")
    session = _get_sync_session()

    try:
        from app.models.models import Building, RenderPreview

        building = session.query(Building).filter_by(id=uuid.UUID(building_id)).first()
        if not building:
            raise ValueError(f"Building not found: {building_id}")

        building.preview_status = "generating"
        session.commit()

        self.update_state(state="GENERATING", meta={"progress": 0.1, "step": "preparing"})

        # Enrich prompt with style info
        enriched_prompt = prompt
        if style_id:
            from app.generation.styles import get_style
            style = get_style(style_id)
            from app.generation.stability_client import build_architectural_prompt
            enriched_prompt = build_architectural_prompt(
                prompt,
                style_prefix=style.prompt_prefix,
                style_suffix=style.prompt_suffix,
                materials=style.facade_material,
            )

        self.update_state(state="GENERATING", meta={"progress": 0.3, "step": "generating_image"})

        from app.generation.stability_client import StabilityClient
        client = StabilityClient()

        if source_type in ("sketch", "floor_plan") and source_image_url:
            # Download source image first
            import httpx as httpx_sync
            source_bytes = httpx_sync.get(source_image_url, timeout=30.0).content
            image_bytes = asyncio.run(client.image_to_image(
                source_bytes,
                enriched_prompt,
                strength=0.65,
            ))
        else:
            image_bytes = asyncio.run(client.text_to_image(
                enriched_prompt,
                negative_prompt="blurry, low quality, distorted, unrealistic, cartoon",
            ))

        self.update_state(state="GENERATING", meta={"progress": 0.7, "step": "uploading"})

        # Upload PNG to storage
        preview_uuid = str(uuid.uuid4())
        project_id = building.project_id
        preview_key = f"projects/{project_id}/previews/{building_id}_{preview_uuid}.png"
        image_url = _upload_to_storage(preview_key, image_bytes, "image/png")

        self.update_state(state="GENERATING", meta={"progress": 0.9, "step": "saving"})

        # Create RenderPreview record
        preview = RenderPreview(
            building_id=uuid.UUID(building_id),
            image_url=image_url,
            prompt=prompt,
            style=style_id,
            source_type=source_type,
            source_image_url=source_image_url,
        )
        session.add(preview)

        # Update building
        building.preview_url = image_url
        building.preview_status = "completed"
        session.commit()

        logger.info(f"Render preview generated for building {building_id}: {image_url}")
        return {
            "status": "completed",
            "building_id": building_id,
            "image_url": image_url,
            "preview_id": str(preview.id),
        }

    except Exception as exc:
        logger.error(f"Render preview failed for building {building_id}: {exc}")
        try:
            building = session.query(Building).filter_by(id=uuid.UUID(building_id)).first()
            if building:
                building.preview_status = "failed"
                session.commit()
        except Exception:
            session.rollback()
        raise self.retry(exc=exc, countdown=30)
    finally:
        session.close()
