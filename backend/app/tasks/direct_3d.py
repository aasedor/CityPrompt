"""Dedicated image worker. Messages contain IDs only; never autoretry paid work."""

import asyncio
import uuid

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.tasks.worker import celery_app


async def _with_session(callback, *args):
    # Each Celery invocation has its own event loop; don't reuse asyncpg pools.
    engine = create_async_engine(get_settings().database_url, poolclass=NullPool)
    try:
        async with async_sessionmaker(engine, expire_on_commit=False)() as db:
            await callback(db, *args)
    finally:
        await engine.dispose()


@celery_app.task(name="cityprompt.direct3d.render", acks_late=True, reject_on_worker_lost=False, max_retries=0, ignore_result=True)
def render_direct_3d_attempt(attempt_id: str):
    from app.services.render_attempts import execute_attempt
    asyncio.run(_with_session(execute_attempt, uuid.UUID(attempt_id)))


@celery_app.task(name="cityprompt.direct3d.maintain", max_retries=0, ignore_result=True)
def maintain_direct_3d_attempts():
    from app.services.render_attempts import maintain_attempts
    asyncio.run(_with_session(maintain_attempts))
