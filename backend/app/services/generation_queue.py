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
    countdown: int = 0,
    photo_reference_keys: list[str] | None = None,
    photo_batch_id: str | None = None,
    photo_audit_id: str | None = None,
) -> str | None:
    """Commit the current DB state before queueing AI generation work.

    countdown staggers batch submissions — Meshy rejects bursts over its
    concurrent-task limit with 400s, so generate-all spaces its tasks out.
    """
    from app.tasks.processing import generate_3d_model_ai

    building.generation_engine = engine
    await db.commit()

    try:
        task = await asyncio.to_thread(
            generate_3d_model_ai.apply_async,
            args=[
                str(building.id),
                prompt,
                mode,
                image_url,
                refine,
                engine,
                style_id,
                negative_prompt,
                photo_reference_keys,
                photo_batch_id,
                photo_audit_id,
            ],
            countdown=countdown,
        )
    except Exception as exc:
        building.generation_status = "failed"
        updates = {"generation_error": f"Failed to queue AI generation: {exc}"}
        if photo_batch_id:
            from app.services.photo_building import photo_state

            state = photo_state(building.specifications)
            if state.get("batch_id") == photo_batch_id:
                updates["photo_generation"] = {
                    **state,
                    "status": "failed",
                    "error": "Could not start 3D generation. Please try again.",
                }
        _merge_building_specifications(building, updates)
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
