"""Helpers for queueing AI generation tasks after DB state is persisted."""

import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Building

logger = logging.getLogger(__name__)


def _merge_building_specifications(building: Building, updates: dict) -> None:
    specs = dict(building.specifications or {})
    specs.update(updates)
    building.specifications = specs


async def queue_ai_generation_task(
    db: AsyncSession,
    building: Building,
    prompt: str,
    mode: str = "text",
    image_url: str | None = None,
    refine: bool = True,
    engine: str = "meshy",
    style_id: str | None = None,
    negative_prompt: str | None = None,
) -> str | None:
    """Commit the current DB state before queueing AI generation work."""
    from app.tasks.processing import generate_3d_model_ai

    building.generation_engine = engine
    await db.commit()

    try:
        task = await asyncio.to_thread(
            generate_3d_model_ai.delay,
            str(building.id),
            prompt,
            mode,
            image_url,
            refine,
            engine,
            style_id,
            negative_prompt,
        )
    except Exception as exc:
        building.generation_status = "failed"
        _merge_building_specifications(
            building,
            {"generation_error": f"Failed to queue AI generation: {exc}"},
        )
        try:
            await db.commit()
        except Exception as commit_exc:
            await db.rollback()
            logger.warning("Failed to persist AI queue failure for building %s: %s", building.id, commit_exc)
        raise

    task_id = getattr(task, "id", None)
    if task_id:
        _merge_building_specifications(building, {"celery_task_id": task_id})
        try:
            await db.commit()
        except Exception as exc:
            await db.rollback()
            logger.warning("Failed to persist AI queue metadata for building %s: %s", building.id, exc)

    return task_id