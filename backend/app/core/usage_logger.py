"""
Centralized API usage logging for all external provider calls.
Provides both sync (Celery tasks) and async (FastAPI handlers) interfaces.
"""

import logging
import uuid
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# Lazy-initialized sync engine for Celery tasks
_sync_engine = None


def _get_sync_engine():
    global _sync_engine
    if _sync_engine is None:
        _sync_engine = create_engine(settings.database_url_sync)
    return _sync_engine


def log_api_usage_sync(
    provider: str,
    operation: str,
    credits_used: Optional[float] = None,
    input_tokens: Optional[int] = None,
    output_tokens: Optional[int] = None,
    task_id: Optional[str] = None,
    building_id: Optional[str] = None,
    document_id: Optional[str] = None,
    user_id: Optional[str] = None,
    status: str = "success",
    metadata: Optional[dict] = None,
    session: Optional[Session] = None,
) -> None:
    """Log an API usage record synchronously (for Celery tasks).

    If no session is passed, creates one from settings.database_url_sync.
    """
    from app.models.models import ApiUsageLog

    own_session = False
    if session is None:
        own_session = True
        session = Session(_get_sync_engine())

    try:
        record = ApiUsageLog(
            provider=provider,
            operation=operation,
            credits_used=credits_used,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            task_id=task_id,
            building_id=uuid.UUID(building_id) if building_id else None,
            document_id=uuid.UUID(document_id) if document_id else None,
            user_id=uuid.UUID(user_id) if user_id else None,
            status=status,
            metadata_=metadata,
        )
        session.add(record)
        session.commit()
    except Exception as exc:
        logger.warning(f"Failed to log API usage ({provider}/{operation}): {exc}")
        try:
            session.rollback()
        except Exception:
            pass
    finally:
        if own_session:
            session.close()


async def log_api_usage(
    session: AsyncSession,
    provider: str,
    operation: str,
    credits_used: Optional[float] = None,
    input_tokens: Optional[int] = None,
    output_tokens: Optional[int] = None,
    task_id: Optional[str] = None,
    building_id: Optional[str] = None,
    document_id: Optional[str] = None,
    user_id: Optional[str] = None,
    status: str = "success",
    metadata: Optional[dict] = None,
) -> None:
    """Log an API usage record asynchronously (for FastAPI handlers)."""
    from app.models.models import ApiUsageLog

    try:
        record = ApiUsageLog(
            provider=provider,
            operation=operation,
            credits_used=credits_used,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            task_id=task_id,
            building_id=uuid.UUID(building_id) if building_id else None,
            document_id=uuid.UUID(document_id) if document_id else None,
            user_id=uuid.UUID(user_id) if user_id else None,
            status=status,
            metadata_=metadata,
        )
        session.add(record)
        await session.flush()
    except Exception as exc:
        logger.warning(f"Failed to log API usage ({provider}/{operation}): {exc}")
