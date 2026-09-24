"""Fault injection for the opt-in, network-isolated Linux probe only."""
import os
import signal
import time
from unittest.mock import AsyncMock

from app.core.config import get_settings

settings = get_settings()
if not (os.getenv("CITYPROMPT_PREFORK_PROBE") == "1"
        and "@probe-db/" in settings.database_url
        and settings.redis_url == "redis://probe-redis:6379/0"
        and settings.s3_endpoint_url == "http://probe-media:9000"):
    raise RuntimeError("Fault injection requires the isolated prefork probe services")

from app.api.v1 import direct_3d_render as direct
from app.services.direct_3d_render import Direct3DServiceResult
from app.schemas.direct_3d_render import Direct3DRenderDiagnostics
from app.tasks.worker import celery_app
import redis

client = redis.from_url(settings.redis_url)
direct._validate_direct_3d_project_zones = lambda *_: []
direct.build_render_source_snapshot = lambda *_args, **_kw: {"mocked_probe": True}
direct.persist_render_to_gallery = AsyncMock(return_value=None)
direct._finalize_direct_audit = AsyncMock()


async def generate(self, req, capture=None, **kwargs):
    client.incr("probe:calls:" + str(req.project_id))
    client.set("probe:child:" + str(req.project_id), os.getpid())
    if req.prompt == "hard-timeout":
        signal.signal(signal.SIGUSR1, signal.SIG_IGN)
        time.sleep(90)  # Actual Celery hard limit must kill this child.
    if req.prompt == "child-crash":
        os._exit(71)
    return Direct3DServiceResult(
        image_base64=req.beauty_image_base64,
        audit_input_base64=req.beauty_image_base64,
        capture_fingerprint="a" * 64, output_fingerprint="b" * 64,
        outcome="review_required", warnings=("Mocked provider; not visual evidence",),
        diagnostics=Direct3DRenderDiagnostics(
            source_width=512, source_height=512, normalized_width=1024,
            normalized_height=1024, proposal_coverage=.3, context_coverage=.7,
            object_id_attached=False).model_dump(mode="json"),
        provider_image_base64=req.beauty_image_base64,
    )


direct.Direct3DRenderService.generate = generate
original_write = direct.write_evidence


async def write_then_crash(attempt, part, value):
    await original_write(attempt, part, value)
    if part == "provider-result" and client.get("probe:checkpoint:" + str(attempt.project_id)):
        os._exit(72)  # Paid bytes really exist in S3 before abrupt process loss.


direct.write_evidence = write_then_crash
