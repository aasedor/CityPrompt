"""Opt-in real Linux prefork process test; never connects to local trial services.

Run using deployment/classroom/prefork-probe.compose.yaml. Providers are mocked
inside each child, while PostgreSQL, Redis and immutable S3 evidence are real.
"""
import asyncio
from datetime import timedelta
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

import pytest

pytestmark = pytest.mark.skipif(
    sys.platform != "linux" or os.getenv("CITYPROMPT_PREFORK_PROBE") != "1",
    reason="Requires disposable Linux prefork probe",
)


@pytest.mark.asyncio
async def test_real_prefork_timeout_crash_and_checkpoint_recovery(tmp_path):
    from tests.prefork_probe_worker import settings, client, celery_app
    from app.models.models import User, Project, RenderAuditLog
    from app.models.render_attempt import RenderAttempt
    from app.services import render_attempts as jobs
    from app.services.render_attempt_storage import _client
    from app.services.readiness import maintenance_key
    from sqlalchemy import update
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from sqlalchemy.pool import NullPool
    from tests.test_direct_3d_render import _request

    s3, bucket = _client()
    s3.create_bucket(Bucket=bucket)
    engine = create_async_engine(settings.database_url, poolclass=NullPool)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    logs, processes, receipts = [], [], []

    def start(name, queue, slots):
        log = open(tmp_path / (name + ".log"), "w")
        logs.append(log)
        process = subprocess.Popen([
            sys.executable, "-m", "celery", "-A", "app.tasks.worker:celery_app",
            "worker", "-I", "tests.prefork_probe_worker", "--pool=prefork",
            f"--concurrency={slots}", f"--queues={queue}", f"--hostname={name}@probe",
            "--time-limit=10", "--soft-time-limit=8", "--loglevel=warning",
        ], stdout=log, stderr=subprocess.STDOUT)
        processes.append(process)
        return process

    async def until(predicate, seconds=55):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            if await predicate():
                return
            await asyncio.sleep(.25)
        raise AssertionError("Timed out waiting for probe state")

    async def submit(mode):
        async with sessions() as db:
            user = User(id=uuid.uuid4(), email=f"{uuid.uuid4()}@probe.invalid",
                        role="editor", render_credits=1000, credits_reset_at=jobs.now())
            db.add(user)
            await db.flush()
            project = Project(id=uuid.uuid4(), name="Disposable " + mode, owner_id=user.id)
            db.add(project)
            await db.commit()
            if mode == "checkpoint-crash":
                client.set("probe:checkpoint:" + str(project.id), "1")
            req = _request().model_copy(update={"project_id": project.id, "prompt": mode})
            attempt = await jobs.submit_attempt(db, user, req, str(uuid.uuid4()))
            return attempt.id, user.id, project.id

    async def dispatched(item):
        return client.get("probe:calls:" + str(item[2])) == b"1"

    async def recover(item, expected):
        # Advance only the disposable attempt's age; retain production's 900s
        # recovery threshold rather than weakening the deployed setting.
        async with sessions() as db:
            await db.execute(update(RenderAttempt).where(RenderAttempt.id == item[0])
                             .values(started_at=jobs.now() - timedelta(seconds=1000)))
            await db.commit()
        celery_app.send_task("cityprompt.direct3d.maintain")

        async def terminal():
            async with sessions() as db:
                return (await db.get(RenderAttempt, item[0])).status == expected
        await until(terminal)
        # Duplicate delivery and concurrent reconciliation cannot charge again.
        for _ in range(3):
            celery_app.send_task("cityprompt.direct3d.render", args=[str(item[0])])
            celery_app.send_task("cityprompt.direct3d.maintain")
        await asyncio.sleep(1)
        async with sessions() as db:
            row = await db.get(RenderAttempt, item[0])
            user = await db.get(User, item[1])
            audit = await db.get(RenderAuditLog, row.audit_id)
            assert audit.tokens_spent > 0
            assert client.get("probe:calls:" + str(item[2])) == b"1"
            if expected == "unknown":
                assert user.render_credits == 1000
                assert audit.student_refunded_at is not None
            else:
                assert user.render_credits == 1000 - audit.tokens_spent
                assert audit.student_refunded_at is None
                result = await jobs.recover_result(row)
                assert result.outcome == "review_required" and result.image_base64
            receipts.append({"attempt": str(item[0]), "status": row.status,
                             "tokens_reserved": audit.tokens_spent,
                             "student_balance": user.render_credits, "provider_calls": 1})

    try:
        images = start("probe-images", "direct3d", 2)
        start("probe-maintenance", "direct3d-maintenance", 1)
        first, second = await submit("hard-timeout"), await submit("hard-timeout")
        await until(lambda: dispatched(first))
        await until(lambda: dispatched(second))
        assert client.get("probe:child:" + str(first[2])) != client.get("probe:child:" + str(second[2]))
        celery_app.send_task("cityprompt.direct3d.maintain")

        async def heartbeat():
            return bool(client.get(maintenance_key()))
        await until(heartbeat, seconds=5)  # Separate maintenance works while both slots block.
        await asyncio.sleep(11)
        assert images.poll() is None  # Parent survived both child hard timeouts.
        await recover(first, "unknown")
        await recover(second, "unknown")
        crash = await submit("child-crash")
        await until(lambda: dispatched(crash))
        await asyncio.sleep(2)
        await recover(crash, "unknown")
        checkpoint = await submit("checkpoint-crash")
        await until(lambda: dispatched(checkpoint))
        await asyncio.sleep(2)
        await recover(checkpoint, "completed")
        assert images.poll() is None
    finally:
        for process in processes:
            process.terminate()
        for process in processes:
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        for log in logs:
            log.close()
        evidence = Path(os.environ.get("PREFORK_EVIDENCE_DIR", str(tmp_path)))
        evidence.mkdir(parents=True, exist_ok=True)
        for log in tmp_path.glob("*.log"):
            (evidence / log.name).write_bytes(log.read_bytes())
        (evidence / "prefork-receipt.json").write_text(json.dumps(receipts, indent=2))
        await engine.dispose()
    worker_log = (tmp_path / "probe-images.log").read_text()
    assert "Hard time limit" in worker_log
    assert "exitcode 71" in worker_log and "exitcode 72" in worker_log
