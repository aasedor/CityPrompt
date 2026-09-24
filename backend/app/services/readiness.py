"""Operational readiness distinct from process liveness; no paid provider calls."""

import asyncio
import hashlib
import json
from pathlib import Path

import redis.asyncio as redis
from sqlalchemy import text

from app.core.config import get_settings
from app.core.database import async_session_factory
from app.services.render_attempt_storage import _client
from scripts.prepare_database import expected_schema_heads


def maintenance_key():
    settings = get_settings()
    scope = hashlib.sha256(f"{settings.database_url}|{settings.s3_bucket_name}".encode()).hexdigest()[:20]
    return f"cityprompt:direct3d:maintenance:{scope}"


async def database_ready():
    async with async_session_factory() as db:
        versions = set((await db.execute(text("SELECT version_num FROM alembic_version"))).scalars())
        if versions != expected_schema_heads():
            raise RuntimeError("schema")
        await db.execute(text("SELECT student_refunded_at FROM render_audit_logs LIMIT 0"))
        await db.execute(text("SELECT id FROM render_attempts LIMIT 0"))


async def redis_ready():
    async with redis.from_url(get_settings().redis_url, socket_connect_timeout=2, socket_timeout=2) as client:
        await client.ping()


async def storage_ready():
    def check():
        client, bucket = _client(timeout_seconds=2, retries=0)
        client.head_bucket(Bucket=bucket)
    await asyncio.to_thread(check)


async def images_ready():
    from app.tasks.worker import celery_app
    settings = get_settings()
    if not settings.direct_3d_jobs_enabled or not settings.direct_3d_images_enabled:
        return "not_enabled"
    async with redis.from_url(settings.redis_url, socket_connect_timeout=2, socket_timeout=2) as client:
        if not await client.exists(maintenance_key()):
            raise RuntimeError("maintenance")
    queues = await asyncio.to_thread(lambda: celery_app.control.inspect(timeout=1).active_queues())
    if not any(queue.get("name") == "direct3d" for worker in (queues or {}).values() for queue in worker):
        raise RuntimeError("worker")


async def assets_ready():
    settings = get_settings()
    if not settings.classroom_release:
        return "not_enabled"
    if not settings.direct_3d_jobs_enabled:
        raise RuntimeError("Classroom release requires durable image attempts")
    roster = json.loads((Path(__file__).parents[1] / "data/classroomStarter.json").read_text(encoding="utf-8"))
    receipt = json.loads(Path(settings.classroom_asset_receipt).read_text(encoding="utf-8"))
    roster_hash = hashlib.sha256((json.dumps(roster, indent=2, ensure_ascii=False) + "\n").encode()).hexdigest()
    expected = {row["id"] for row in roster["dependencies"]}
    verified = {row["id"] for row in receipt.get("dependencies", []) if row.get("status") == "verified"}
    if (receipt.get("command") != "preflight" or receipt.get("errors") != []
        or receipt.get("roster_sha256") != roster_hash or not receipt.get("runtime_reviews_required")
        or expected != verified or any(row["review"]["runtime"] != "passed" for row in roster["entries"])):
        raise RuntimeError("Starter asset/review receipt does not qualify this release")


async def readiness():
    probes = {"database": database_ready, "redis": redis_ready, "storage": storage_ready,
              "image_worker": images_ready, "starter_assets": assets_ready}
    async def probe(name, check):
        try:
            result = await asyncio.wait_for(check(), timeout=4)
            return name, "not_enabled" if result == "not_enabled" else "ready"
        except Exception:
            # Public readiness never returns DSNs, provider keys or exception text.
            return name, "unavailable"
    checks = dict(await asyncio.gather(*(probe(name, check) for name, check in probes.items())))
    return {"status": "ready" if all(value in {"ready", "not_enabled"} for value in checks.values()) else "unavailable",
            "classroom_release": get_settings().classroom_release, "checks": checks}
