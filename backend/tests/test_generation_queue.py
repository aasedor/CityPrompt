from types import SimpleNamespace
import uuid
from unittest.mock import AsyncMock

import pytest

from app.services.generation_queue import queue_ai_generation_task
from app.tasks import processing


@pytest.mark.anyio
async def test_queue_ai_generation_task_commits_before_queue_and_persists_task_id(monkeypatch):
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    building = SimpleNamespace(
        id=uuid.uuid4(),
        specifications={"existing": "value"},
        generation_status="generating",
        generation_engine=None,
    )

    captured_kwargs = {}

    def _apply_async(args=None, countdown=0):
        captured_kwargs['args'] = args
        captured_kwargs['countdown'] = countdown
        return SimpleNamespace(id='task-123')

    monkeypatch.setattr(
        processing,
        'generate_3d_model_ai',
        SimpleNamespace(apply_async=_apply_async),
    )

    task_id = await queue_ai_generation_task(
        session,
        building,
        'prompt text',
        engine='tripo',
        style_id='modern',
        negative_prompt='no clutter',
        countdown=90,
    )

    assert task_id == 'task-123'
    assert captured_kwargs['countdown'] == 90
    assert captured_kwargs['args'][0] == str(building.id)
    assert building.generation_engine == 'tripo'
    assert building.specifications['existing'] == 'value'
    assert building.specifications['celery_task_id'] == 'task-123'
    assert session.commit.await_count == 2
    session.rollback.assert_not_awaited()


@pytest.mark.anyio
async def test_queue_ai_generation_task_marks_failed_when_broker_queue_fails(monkeypatch):
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    building = SimpleNamespace(
        id=uuid.uuid4(),
        specifications=None,
        generation_status='generating',
        generation_engine=None,
    )

    def _raise_apply_async(args=None, countdown=0):
        raise RuntimeError('broker down')

    monkeypatch.setattr(
        processing,
        'generate_3d_model_ai',
        SimpleNamespace(apply_async=_raise_apply_async),
    )

    with pytest.raises(RuntimeError, match='broker down'):
        await queue_ai_generation_task(session, building, 'prompt text')

    assert building.generation_status == 'failed'
    assert building.specifications['generation_error'] == 'Failed to queue AI generation: broker down'
    assert session.commit.await_count == 2
    session.rollback.assert_not_awaited()