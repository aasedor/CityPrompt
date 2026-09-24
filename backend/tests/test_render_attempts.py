"""Durable image recovery. Integration uses an isolated schema, never live rows.

CITYPROMPT_TEST_DATABASE_URL enables PostgreSQL tests. Paid providers are always
replaced. CITYPROMPT_TEST_S3=1 additionally checks immutable private evidence.
"""

import asyncio
from dataclasses import asdict
from datetime import timedelta
import importlib.util
import os
from pathlib import Path
from types import SimpleNamespace
import uuid
from unittest.mock import AsyncMock

from alembic.migration import MigrationContext
from alembic.operations import Operations
from fastapi import HTTPException
import pytest
from sqlalchemy import MetaData, delete, select, text, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.api.v1 import direct_3d_render as direct
from app.core.config import get_settings
from app.models.models import User, Project, ProjectShare, Building, SiteZone, RenderAuditLog
from app.models.render_attempt import RenderAttempt
from app.services import render_attempts as jobs
from app.services import render_attempt_storage as storage
from app.services.direct_3d_render import Direct3DServiceResult, estimate_direct_3d_token_cost, prepare_direct_3d_capture
from app.schemas.direct_3d_render import Direct3DRenderDiagnostics
from tests.test_direct_3d_render import _request


@pytest.fixture
async def isolated(monkeypatch):
    url = os.getenv("CITYPROMPT_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set CITYPROMPT_TEST_DATABASE_URL for isolated-schema PostgreSQL verification")
    schema = "test_image_attempt_" + uuid.uuid4().hex
    admin = create_async_engine(url, poolclass=NullPool)
    async with admin.begin() as connection:
        await connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    engine = create_async_engine(url, pool_size=8, max_overflow=8,
                                 connect_args={"server_settings": {"search_path": f"{schema},public"}})
    try:
        metadata = MetaData()
        for model in (User, Project, ProjectShare, Building, SiteZone, RenderAuditLog):
            model.__table__.to_metadata(metadata)
        # Start from pre-030 tables, then execute the actual additive migration.
        table = metadata.tables["render_audit_logs"]
        table._columns.remove(table.c.student_refunded_at)
        async with engine.begin() as connection:
            await connection.run_sync(lambda conn: metadata.create_all(conn, checkfirst=False))
            spec = importlib.util.spec_from_file_location("image_migration", Path(__file__).parents[1] / "migrations/versions/030_render_attempts.py")
            migration = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migration)
            def migrate(conn):
                with Operations.context(MigrationContext.configure(conn)):
                    migration.upgrade()
            await connection.run_sync(migrate)
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        settings = get_settings().model_copy(update={
            "direct_3d_jobs_enabled": True, "direct_3d_images_enabled": True,
            "openai_api_key": "mock-never-sent", "render_global_daily_token_cap": 1000,
            "direct_3d_queue_limit": 16, "direct_3d_project_queue_limit": 2,
        })
        monkeypatch.setattr(jobs, "get_settings", lambda: settings)
        monkeypatch.setattr(direct, "get_settings", lambda: settings)
        delivered = AsyncMock()
        monkeypatch.setattr(jobs, "deliver_attempt", delivered)
        evidence = {}
        async def write(attempt, part, value):
            key = storage.evidence_key(attempt, part)
            if key in evidence and evidence[key] != value:
                raise ValueError("immutable")
            evidence[key] = value
        async def read(attempt, part):
            return evidence.get(storage.evidence_key(attempt, part))
        monkeypatch.setattr(jobs, "write_evidence", write)
        monkeypatch.setattr(jobs, "read_evidence", read)
        monkeypatch.setattr(direct, "write_evidence", write)
        monkeypatch.setattr(direct, "_validate_direct_3d_project_zones", lambda *_: [])
        monkeypatch.setattr(direct, "build_render_source_snapshot", lambda *_args, **_kwargs: {"test_snapshot": True})
        monkeypatch.setattr(direct, "_finalize_direct_audit", AsyncMock())
        monkeypatch.setattr(direct, "persist_render_to_gallery", AsyncMock(return_value=None))
        result = Direct3DServiceResult(
            image_base64="exact-paid-result", audit_input_base64="exact-source",
            capture_fingerprint="a"*64, output_fingerprint="b"*64,
            outcome="review_required", warnings=("Compare with source",),
            diagnostics=Direct3DRenderDiagnostics(
                source_width=512, source_height=512, normalized_width=1024, normalized_height=1024,
                proposal_coverage=0.3, context_coverage=0.7, object_id_attached=False,
            ).model_dump(mode="json"), provider_image_base64="provider-original",
        )
        provider = AsyncMock(return_value=result)
        monkeypatch.setattr(direct.Direct3DRenderService, "generate", provider)
        async with sessions() as db:
            user = User(id=uuid.uuid4(), email=f"{uuid.uuid4()}@test.invalid", full_name="Student", role="editor", render_credits=1000, credits_reset_at=jobs.now())
            db.add(user)
            await db.flush()
            project = Project(id=uuid.uuid4(), owner_id=user.id, name="Disposable image test")
            db.add(project)
            await db.commit()
        yield SimpleNamespace(sessions=sessions, user=user, project=project,
                              req=_request().model_copy(update={"project_id": project.id}), settings=settings, provider=provider,
                              evidence=evidence, result=result, write=write, read=read, delivered=delivered,
                              url=url, schema=schema)
    finally:
        await engine.dispose()
        assert schema.startswith("test_image_attempt_") and len(schema) == 51
        async with admin.begin() as connection:
            await connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        await admin.dispose()


async def submit(fixture, key=None, req=None):
    async with fixture.sessions() as db:
        user = await db.get(User, fixture.user.id)
        return await jobs.submit_attempt(db, user, req or fixture.req, key or str(uuid.uuid4()))


async def execute(fixture, attempt):
    async with fixture.sessions() as db:
        await jobs.execute_attempt(db, attempt.id)


@pytest.mark.asyncio
async def test_duplicate_submissions_and_deliveries_call_provider_once(isolated):
    f = isolated
    key = str(uuid.uuid4())
    attempts = await asyncio.gather(*[submit(f, key) for _ in range(12)])
    assert len({a.id for a in attempts}) == 1
    a = attempts[0]
    await asyncio.gather(*[execute(f, a) for _ in range(12)])
    f.provider.assert_awaited_once()
    async with f.sessions() as db:
        row = await db.get(RenderAttempt, a.id)
        assert row.status == "completed"
        audit = await db.get(RenderAuditLog, row.audit_id)
        user = await db.get(User, f.user.id)
        assert user.render_credits == 1000 - audit.tokens_spent
        assert audit.student_refunded_at is None
        result = await jobs.recover_result(row)
        assert result.image_base64 == "exact-paid-result"
        assert (await f.read(row, "provider-result"))["result"]["provider_image_base64"] == "provider-original"
        assert (await f.read(row, "request"))["proposal_mask_base64"] == f.req.proposal_mask_base64
        assert await f.read(row, "source") == {"snapshot": {"test_snapshot": True}, "scene_revision_sha256": direct.compiled_scene_revision_sha256(f.req.community_3d_claims, f.req.residual_landscape_claim), "server_inventory": []}
    # Same key with different intent cannot buy a second image.
    with pytest.raises(HTTPException) as conflict:
        await submit(f, key, f.req.model_copy(update={"prompt": "Changed design"}))
    assert conflict.value.status_code == 409


@pytest.mark.asyncio
async def test_paid_result_survives_gallery_and_response_storage_failure(isolated, monkeypatch):
    f = isolated
    a = await submit(f)
    async def fail_response(attempt, part, value):
        if part == "response":
            raise ConnectionError("storage disconnected after paid result")
        await f.write(attempt, part, value)
    monkeypatch.setattr(jobs, "write_evidence", fail_response)
    monkeypatch.setattr(direct, "persist_render_to_gallery", AsyncMock(side_effect=ConnectionError("gallery offline")))
    await execute(f, a)
    await execute(f, a)
    async with f.sessions() as db:
        row = await db.get(RenderAttempt, a.id)
        assert row.status == "completed"
        assert (await jobs.recover_result(row)).image_base64 == "exact-paid-result"
    f.provider.assert_awaited_once()


@pytest.mark.asyncio
async def test_worker_crash_refunds_once_keeps_uncertain_cap_and_never_requeues(isolated):
    f = isolated
    a = await submit(f)
    async with f.sessions() as db:
        row = await db.get(RenderAttempt, a.id)
        row.status, row.started_at = "running", jobs.now() - timedelta(seconds=1000)
        await db.commit()
        user = await db.get(User, f.user.id)
        audit = await direct._reserve_direct_render(db, user, token_cost=13, daily_cap=1000,
            prompt="mock crash", project_id=f.project.id, attempt=row)
        audit_id = audit.id
    async def reconcile():
        async with f.sessions() as db:
            await jobs.reconcile_attempt(db, a.id)
    await asyncio.gather(*[reconcile() for _ in range(12)])
    await execute(f, a)
    async with f.sessions() as db:
        row, user, audit = await db.get(RenderAttempt, a.id), await db.get(User, f.user.id), await db.get(RenderAuditLog, audit_id)
        assert row.status == "unknown"
        assert user.render_credits == 1000
        assert audit.tokens_spent == 13 and audit.student_refunded_at is not None
        await direct._refund_unproduced_direct_render(db, user, audit, token_cost=99999, detail="duplicate wrong refund")
        assert user.render_credits == 1000 and audit.tokens_spent == 13
    f.provider.assert_not_awaited()


@pytest.mark.asyncio
async def test_pre_dispatch_storage_failure_costs_nothing(isolated, monkeypatch):
    f = isolated
    a = await submit(f)
    monkeypatch.setattr(direct, "write_evidence", AsyncMock(side_effect=ConnectionError("source storage offline")))
    await execute(f, a)
    async with f.sessions() as db:
        row = await db.get(RenderAttempt, a.id)
        assert row.status == "failed" and row.audit_id is None
        assert (await db.get(User, f.user.id)).render_credits == 1000
    f.provider.assert_not_awaited()


@pytest.mark.asyncio
async def test_expired_queue_and_revoked_access_never_dispatch(isolated):
    f = isolated
    a = await submit(f)
    async with f.sessions() as db:
        await db.execute(update(RenderAttempt).where(RenderAttempt.id == a.id).values(created_at=jobs.now() - timedelta(seconds=1000)))
        await db.commit()
        await jobs.maintain_attempts(db)
        assert (await db.get(RenderAttempt, a.id)).status == "failed"
    await execute(f, a)
    b = await submit(f)
    async with f.sessions() as db:
        user = await db.get(User, f.user.id)
        user.is_active = False
        await db.commit()
    await execute(f, b)
    f.provider.assert_not_awaited()
    async with f.sessions() as db:
        row = await db.get(RenderAttempt, b.id)
        assert row.status == "failed" and row.audit_id is None


@pytest.mark.asyncio
async def test_sixty_students_eight_projects_obey_queue_limits(isolated):
    f = isolated
    async with f.sessions() as db:
        users = [User(id=uuid.uuid4(), email=f"{uuid.uuid4()}@test.invalid", role="editor", render_credits=1000, credits_reset_at=jobs.now()) for _ in range(60)]
        db.add_all(users)
        await db.flush()
        projects = [Project(id=uuid.uuid4(), name=f"Group {i}", owner_id=users[i].id) for i in range(8)]
        db.add_all(projects)
        await db.flush()
        db.add_all([ProjectShare(project_id=projects[i % 8].id, user_id=user.id, permission="editor") for i, user in enumerate(users)])
        await db.commit()
    async def admit(i):
        async with f.sessions() as db:
            try:
                return await jobs.submit_attempt(db, await db.get(User, users[i].id), f.req.model_copy(update={"project_id": projects[i % 8].id}), str(uuid.uuid4()))
            except HTTPException as exc:
                return exc.status_code
    outcomes = await asyncio.gather(*[admit(i) for i in range(60)])
    accepted = [a for a in outcomes if isinstance(a, RenderAttempt)]
    assert len(accepted) == 16
    assert outcomes.count(429) == 44
    assert all(sum(a.project_id == p.id for a in accepted) == 2 for p in projects)
    # A simulated two-slot worker drains the bounded queue with mock images.
    semaphore = asyncio.Semaphore(2)
    async def work(a):
        async with semaphore:
            await execute(f, a)
    await asyncio.gather(*[work(a) for a in accepted])
    capture = prepare_direct_3d_capture(f.req)
    cost = estimate_direct_3d_token_cost(capture.normalized_beauty.width, capture.normalized_beauty.height,
        object_id_attached=False, model=f.req.model)
    expected = min(16, f.settings.render_global_daily_token_cap // cost)
    assert f.provider.await_count == expected
    async with f.sessions() as db:
        rows = list((await db.scalars(select(RenderAttempt))).all())
        assert sum(row.status == "completed" for row in rows) == expected
        failed = [row for row in rows if row.status == "failed"]
        assert len(failed) == 16 - expected
        assert all("Daily render token cap reached" in row.error["message"] and row.audit_id is None for row in failed)
        audits = list((await db.scalars(select(RenderAuditLog))).all())
        assert sum(audit.tokens_spent for audit in audits) == expected * cost <= f.settings.render_global_daily_token_cap


@pytest.mark.asyncio
async def test_only_requester_with_current_project_access_can_recover(isolated):
    f = isolated
    a = await submit(f)
    async with f.sessions() as db:
        other = User(id=uuid.uuid4(), email=f"{uuid.uuid4()}@test.invalid", role="editor")
        db.add(other)
        await db.commit()
        with pytest.raises(HTTPException) as denied:
            await jobs.authorized_attempt(db, other, a.id)
        assert denied.value.status_code == 404
        # Transfer test-project ownership: the original requester now lacks access.
        project = await db.get(Project, f.project.id)
        project.owner_id = other.id
        await db.commit()
        with pytest.raises(HTTPException) as revoked:
            await jobs.authorized_attempt(db, f.user, a.id)
        assert revoked.value.status_code == 403
    await execute(f, a)
    f.provider.assert_not_awaited()


@pytest.mark.asyncio
async def test_actual_s3_evidence_is_immutable_and_roundtrips_controls():
    if os.getenv("CITYPROMPT_TEST_S3") != "1":
        pytest.skip("Set CITYPROMPT_TEST_S3=1 for private object-storage verification")
    a = SimpleNamespace(project_id=uuid.uuid4(), id=uuid.uuid4())
    key = storage.evidence_key(a, "request")
    payload = _request().model_copy(update={"project_id": a.project_id}).model_dump(mode="json")
    try:
        await storage.write_evidence(a, "request", payload)
        await storage.write_evidence(a, "request", payload)
        assert await storage.read_evidence(a, "request") == payload
        with pytest.raises(ValueError, match="different bytes"):
            await storage.write_evidence(a, "request", {"overwritten": True})
        assert await storage.read_evidence(a, "request") == payload
    finally:
        s3, bucket = storage._client()
        assert key == f"projects/{a.project_id}/render-attempts/{a.id}/request.json"
        s3.delete_object(Bucket=bucket, Key=key)


@pytest.mark.asyncio
async def test_real_redis_celery_delivery_uses_database_identity(isolated, monkeypatch):
    if os.getenv("CITYPROMPT_TEST_REDIS_URL") is None:
        pytest.skip("Set CITYPROMPT_TEST_REDIS_URL for isolated-queue Celery verification")
    from celery.contrib.testing.worker import start_worker
    from app.tasks import direct_3d as tasks
    f = isolated
    attempt = await submit(f)
    async def test_session(callback, *args):
        engine = create_async_engine(f.url, poolclass=NullPool,
            connect_args={"server_settings": {"search_path": f"{f.schema},public"}})
        try:
            async with async_sessionmaker(engine, expire_on_commit=False)() as db:
                await callback(db, *args)
        finally:
            await engine.dispose()
    monkeypatch.setattr(tasks, "_with_session", test_session)
    app = tasks.celery_app
    queue = "test-image-attempt-" + uuid.uuid4().hex
    # Never consume an existing deployment queue, or flush the shared broker.
    with start_worker(app, pool="solo", concurrency=1, queues=[queue], perform_ping_check=False, shutdown_timeout=10):
        for _ in range(3):
            await asyncio.to_thread(tasks.render_direct_3d_attempt.apply_async, args=[str(attempt.id)], queue=queue)
        for _ in range(100):
            async with f.sessions() as db:
                row = await db.get(RenderAttempt, attempt.id)
                if row.status == "completed":
                    break
            await asyncio.sleep(0.1)
        assert row.status == "completed"
        assert f.provider.await_count == 1
    with app.connection() as connection:
        connection.default_channel.queue_delete(queue)


@pytest.mark.asyncio
async def test_http_submit_status_and_recovery_contract(isolated, monkeypatch):
    from fastapi import FastAPI
    from httpx import ASGITransport, AsyncClient
    from app.api.v1 import render_attempts as api
    from app.core.database import get_db
    from app.core.security import require_auth
    f = isolated
    app = FastAPI()
    app.include_router(api.router, prefix="/render")
    async def db_session():
        async with f.sessions() as db:
            yield db
    app.dependency_overrides[get_db] = db_session
    app.dependency_overrides[require_auth] = lambda: f.user
    monkeypatch.setattr(api, "read_evidence", f.read)
    monkeypatch.setattr(api, "get_settings", lambda: f.settings)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        key = str(uuid.uuid4())
        response = await client.post("/render/direct-3d-attempts", json=f.req.model_dump(mode="json"), headers={"Idempotency-Key": key})
        assert response.status_code == 202
        data = response.json()
        assert data["idempotency_key"] == key
        assert response.headers["cache-control"] == "private, no-store"
        before = await client.get(f'/render/direct-3d-attempts/{data["id"]}/result')
        assert before.status_code == 409
        await execute(f, SimpleNamespace(id=uuid.UUID(data["id"])))
        recovered = await client.get(f'/render/direct-3d-attempts/{data["id"]}/result')
        assert recovered.status_code == 200
        assert recovered.json()["response"]["image_base64"] == "exact-paid-result"
        assert recovered.json()["source_image_base64"] == f.req.beauty_image_base64
        recent = await client.get("/render/direct-3d-attempts", params={"project_id": str(f.project.id)})
        assert recent.json()[0]["status"] == "completed"


@pytest.mark.asyncio
@pytest.mark.parametrize("billing", ["unproduced", "unknown", "produced"])
async def test_provider_failure_evidence_and_refund_remain_consistent(isolated, billing):
    from app.services.direct_3d_render import Direct3DProviderError
    f = isolated
    f.provider.side_effect = Direct3DProviderError("Mock provider failure", billing_status=billing,
        provider_request_id="mock-request", provider_image_base64="rejected-original" if billing == "produced" else None)
    a = await submit(f)
    await execute(f, a)
    await execute(f, a)
    async with f.sessions() as db:
        row = await db.get(RenderAttempt, a.id)
        audit = await db.get(RenderAuditLog, row.audit_id)
        user = await db.get(User, f.user.id)
        assert row.status == ("unknown" if billing == "unknown" else "failed")
        assert (audit.student_refunded_at is not None) == (billing != "produced")
        assert (audit.tokens_spent == 0) == (billing == "unproduced")
        assert user.render_credits == (1000 - audit.tokens_spent if billing == "produced" else 1000)
        assert (await f.read(row, "provider-error"))["provider_request_id"] == "mock-request"
    f.provider.assert_awaited_once()
