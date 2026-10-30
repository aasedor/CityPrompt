"""Queue isolation must cover both Celery routes and durable render dispatch."""

import json
import subprocess
import sys
from unittest.mock import MagicMock
import uuid

import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.services import render_attempts
from app.tasks.direct_3d import render_direct_3d_attempt


def settings(**overrides):
    return Settings(
        _env_file=None,
        app_env="development",
        classroom_release=False,
        direct_3d_jobs_enabled=True,
        **overrides,
    )


def test_queue_defaults_preserve_existing_worker_names(monkeypatch):
    monkeypatch.delenv("DIRECT_3D_QUEUE_NAME", raising=False)
    monkeypatch.delenv("CELERY_DEFAULT_QUEUE", raising=False)
    values = settings().model_dump()
    assert values.get("direct_3d_queue_name") == "direct3d"
    assert values.get("celery_default_queue") == "celery"


@pytest.mark.parametrize("field", ["direct_3d_queue_name", "celery_default_queue"])
@pytest.mark.parametrize("invalid", ["", "bad queue", "bad/queue", "bad:queue", "bad\n", "bad*queue", "x" * 65])
def test_queue_names_reject_invalid_broker_names(field, invalid):
    with pytest.raises(ValidationError):
        settings(**{field: invalid})


def test_queue_names_accept_safe_characters_and_maximum_length():
    values = settings(direct_3d_queue_name="Q_2026.10-30", celery_default_queue="x" * 64).model_dump()
    assert values.get("direct_3d_queue_name") == "Q_2026.10-30"
    assert values.get("celery_default_queue") == "x" * 64


@pytest.mark.parametrize("direct_queue,default_queue", [("direct3d", "celery"), ("night-direct3d", "night-celery")])
def test_worker_routes_use_the_configured_queue_names(direct_queue, default_queue):
    # A fresh process imports the real worker configuration without changing the
    # current app/task registry used by other tests. No broker is contacted.
    script = """
import json
import sys
from app.core import config
settings = config.Settings(
    _env_file=None, app_env="development", classroom_release=False,
    direct_3d_jobs_enabled=True,
    direct_3d_queue_name=sys.argv[1], celery_default_queue=sys.argv[2],
)
config.get_settings = lambda: settings
from app.tasks.worker import celery_app
router = celery_app.amqp.Router()
def queue_for(task):
    return router.route({}, task, (), {})["queue"].name
print(json.dumps({
    "direct": queue_for("cityprompt.direct3d.render"),
    "maintenance": queue_for("cityprompt.direct3d.maintain"),
    "generic": queue_for("generate_render_preview"),
    "default": celery_app.conf.task_default_queue,
}))
"""
    result = subprocess.run(
        [sys.executable, "-c", script, direct_queue, default_queue],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert json.loads(result.stdout) == {
        "direct": direct_queue,
        "maintenance": direct_queue + "-maintenance",
        "generic": default_queue,
        "default": default_queue,
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("queue", ["direct3d", "night-direct3d"])
async def test_durable_attempt_delivery_uses_configured_queue(monkeypatch, queue):
    config = settings(direct_3d_queue_name=queue)
    monkeypatch.setattr(render_attempts, "get_settings", lambda: config)
    dispatch = MagicMock()
    monkeypatch.setattr(render_direct_3d_attempt, "apply_async", dispatch)
    attempt_id = uuid.uuid4()
    await render_attempts.deliver_attempt(attempt_id)
    dispatch.assert_called_once_with(args=[str(attempt_id)], queue=queue, retry=False)
