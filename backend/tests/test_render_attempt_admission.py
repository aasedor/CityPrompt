"""Credit admission is read-only and precedes queue/trial side effects."""

from datetime import datetime, timedelta, timezone
import asyncio
import threading
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
import uuid

from fastapi import HTTPException
import pytest

from app.core.config import get_settings
from app.schemas.video_appearance import VideoAppearanceRequest
from app.services import render_attempts as jobs
from app.services import direct_3d_render as direct_service
from app.services.direct_3d_render import prepare_direct_3d_capture, estimate_direct_3d_token_cost
from app.services.render_provenance import revision_sha256
from tests.test_direct_3d_render import _request


@pytest.fixture
def admission(monkeypatch):
    settings = get_settings().model_copy(
        update={
            "direct_3d_jobs_enabled": True,
            "direct_3d_images_enabled": True,
            "openai_api_key": "mock-never-sent",
            "gemini_api_key": "mock-never-sent",
            "direct_3d_queue_limit": 16,
            "direct_3d_project_queue_limit": 2,
        }
    )
    monkeypatch.setattr(jobs, "get_settings", lambda: settings)
    monkeypatch.setattr(jobs, "check_project_permission", AsyncMock())
    writes, slots, delivery = AsyncMock(), AsyncMock(), AsyncMock()
    monkeypatch.setattr(jobs, "write_evidence", writes)
    monkeypatch.setattr(jobs, "reserve_image_trial_slot", slots)
    monkeypatch.setattr(jobs, "deliver_attempt", delivery)
    db = SimpleNamespace(
        execute=AsyncMock(),
        scalar=AsyncMock(return_value=None),
        scalars=AsyncMock(return_value=SimpleNamespace(all=lambda: [])),
        refresh=AsyncMock(),
        add=MagicMock(),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )
    user = SimpleNamespace(
        id=uuid.uuid4(), role="editor", render_credits=1000, credits_reset_at=datetime.now(timezone.utc)
    )
    req = _request()
    capture = prepare_direct_3d_capture(req)
    cost = estimate_direct_3d_token_cost(
        capture.normalized_beauty.width,
        capture.normalized_beauty.height,
        object_id_attached=capture.normalized_object_id is not None,
        instance_id_attached=capture.normalized_instance_id is not None,
        control_bundle_version=req.control_bundle_version,
        model=req.model,
    )
    return SimpleNamespace(db=db, user=user, req=req, cost=cost, writes=writes, slots=slots, delivery=delivery)


@pytest.mark.asyncio
@pytest.mark.parametrize("balance", [0, "one_short"])
async def test_insufficient_credit_never_reserves_trial_or_creates_job(admission, balance):
    f = admission
    f.user.render_credits = 0 if balance == 0 else f.cost - 1
    with pytest.raises(HTTPException) as error:
        await jobs.submit_attempt(f.db, f.user, f.req, "new-image")
    assert error.value.status_code == 403
    assert str(f.cost) in error.value.detail
    f.db.refresh.assert_awaited_once_with(f.user, with_for_update=True)
    f.slots.assert_not_awaited()
    f.writes.assert_not_awaited()
    f.delivery.assert_not_awaited()
    f.db.add.assert_not_called()
    f.db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_admission_uses_locked_fresh_balance(admission):
    f = admission

    async def refreshed(user, **_):
        user.render_credits = 0

    f.db.refresh.side_effect = refreshed
    with pytest.raises(HTTPException) as error:
        await jobs.submit_attempt(f.db, f.user, f.req, "stale-balance")
    assert error.value.status_code == 403
    f.slots.assert_not_awaited()
    f.delivery.assert_not_awaited()


@pytest.mark.asyncio
async def test_exact_affordable_cost_admits_without_charging(admission):
    f = admission
    f.user.render_credits = f.cost
    reset = f.user.credits_reset_at
    result = await jobs.submit_attempt(f.db, f.user, f.req, "affordable")
    assert result.status == "queued"
    assert f.user.render_credits == f.cost and f.user.credits_reset_at == reset
    f.slots.assert_awaited_once()
    f.writes.assert_awaited_once()
    f.delivery.assert_awaited_once_with(result.id)


@pytest.mark.asyncio
@pytest.mark.parametrize("model", ["gpt-image-2", "gpt-image-2.5-sunburst", "gemini-nano-banana-2.1"])
async def test_exact_cost_includes_selected_engine_and_real_capture_controls(admission, model):
    f = admission
    req = _request(model=model, presentation_mode="scene")
    capture = prepare_direct_3d_capture(req)
    assert capture.normalized_object_id is not None and capture.normalized_instance_id is not None
    cost = estimate_direct_3d_token_cost(
        capture.normalized_beauty.width,
        capture.normalized_beauty.height,
        object_id_attached=True,
        instance_id_attached=True,
        control_bundle_version=req.control_bundle_version,
        model=model,
    )
    f.user.render_credits = cost - 1
    with pytest.raises(HTTPException) as error:
        await jobs.submit_attempt(f.db, f.user, req, "controlled-image")
    assert error.value.status_code == 403 and f"costs {cost} tokens" in error.value.detail
    f.slots.assert_not_awaited()
    f.delivery.assert_not_awaited()


@pytest.mark.asyncio
async def test_invalid_capture_returns_validation_error_before_admission_side_effects(admission):
    f = admission
    req = f.req.model_copy(update={"beauty_image_base64": "not-valid-base64"})
    with pytest.raises(HTTPException) as error:
        await jobs.submit_attempt(f.db, f.user, req, "invalid-image")
    assert error.value.status_code == 400
    f.slots.assert_not_awaited()
    f.writes.assert_not_awaited()
    f.delivery.assert_not_awaited()
    f.db.add.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("role", ["admin", "cofounder"])
async def test_zero_credit_admin_exemption_is_preserved(admission, role):
    f = admission
    f.user.role, f.user.render_credits = role, 0
    assert (await jobs.submit_attempt(f.db, f.user, f.req, "admin-image")).status == "queued"
    assert f.user.render_credits == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("reset_age", [None, 8])
async def test_due_weekly_allowance_admits_without_persisting_reset(admission, reset_age):
    f = admission
    reset = None if reset_age is None else datetime.now(timezone.utc) - timedelta(days=reset_age)
    f.user.render_credits, f.user.credits_reset_at = 0, reset
    assert (await jobs.submit_attempt(f.db, f.user, f.req, "weekly-image")).status == "queued"
    assert f.user.render_credits == 0 and f.user.credits_reset_at == reset


@pytest.mark.asyncio
@pytest.mark.parametrize("status", ["queued", "running", "completed"])
async def test_existing_request_recovery_ignores_current_balance(admission, status, monkeypatch):
    f = admission
    f.user.render_credits = 0
    existing = SimpleNamespace(status=status, request_sha256=revision_sha256(f.req.model_dump(mode="json")))
    f.db.scalar.return_value = existing
    prepare = MagicMock(side_effect=AssertionError("Existing jobs must not prepare another capture"))
    monkeypatch.setattr(direct_service, "prepare_direct_3d_capture", prepare)
    assert await jobs.submit_attempt(f.db, f.user, f.req, "existing") is existing
    f.db.execute.assert_not_awaited()
    prepare.assert_not_called()
    f.db.refresh.assert_not_awaited()
    f.slots.assert_not_awaited()
    f.writes.assert_not_awaited()
    f.delivery.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("balance", [0, 25, 26])
async def test_shared_appearance_queue_uses_its_fixed_authoritative_cost(admission, balance):
    f = admission
    f.user.render_credits = balance
    req = VideoAppearanceRequest(
        project_id=f.req.project_id, beauty_image_base64=f.req.beauty_image_base64, source_video_sha256="a" * 64
    )
    if balance < 26:
        with pytest.raises(HTTPException) as error:
            await jobs.submit_attempt(f.db, f.user, req, "appearance")
        assert error.value.status_code == 403
        f.slots.assert_not_awaited()
        f.delivery.assert_not_awaited()
    else:
        assert (await jobs.submit_attempt(f.db, f.user, req, "appearance")).status == "queued"
    assert f.user.render_credits == balance


@pytest.mark.asyncio
async def test_blocked_capture_preparation_keeps_loop_responsive_and_queue_unlocked(admission, monkeypatch):
    f = admission
    started, released = threading.Event(), threading.Event()
    transaction = {"open": True}
    user_fields = vars(f.user).copy()

    async def release_read_transaction():
        transaction["open"] = False
        vars(f.user).clear()  # SQLAlchemy rollback expires ORM-loaded fields.

    async def reopen_transaction(*_args, **_kwargs):
        transaction["open"] = True

    async def refresh_expired_user(user, **_kwargs):
        vars(user).update(user_fields)

    f.db.rollback.side_effect = release_read_transaction
    f.db.execute.side_effect = reopen_transaction
    f.db.refresh.side_effect = refresh_expired_user
    original = direct_service.prepare_direct_3d_capture

    def blocked(req):
        started.set()
        released.wait(2)
        return original(req)

    monkeypatch.setattr(direct_service, "prepare_direct_3d_capture", blocked)
    # The watchdog also makes the pre-fix synchronous implementation terminate.
    watchdog = threading.Timer(1, released.set)
    watchdog.start()
    task = asyncio.create_task(jobs.submit_attempt(f.db, f.user, f.req, "slow-capture"))
    try:
        async with asyncio.timeout(2):
            while not started.is_set():
                await asyncio.sleep(0.001)
        await asyncio.sleep(0.01)  # Another coroutine runs while capture remains blocked.
        assert not released.is_set(), "Capture preparation blocked the event loop"
        assert not task.done()
        assert not transaction["open"], "Read transaction retained a pool connection during capture preparation"
        f.db.rollback.assert_awaited_once()
        f.db.execute.assert_not_awaited()  # QUEUE_LOCK is acquired only after preparation.
    finally:
        released.set()
        watchdog.cancel()
        await task


@pytest.mark.asyncio
async def test_concurrent_duplicate_preparations_admit_one_attempt(admission, monkeypatch):
    f = admission
    barrier = threading.Barrier(2, timeout=2)
    original = direct_service.prepare_direct_3d_capture

    def simultaneous(req):
        barrier.wait()
        return original(req)

    monkeypatch.setattr(direct_service, "prepare_direct_3d_capture", simultaneous)
    queue_lock = asyncio.Lock()
    shared = SimpleNamespace(row=None)

    def session():
        db = SimpleNamespace(
            locked=False,
            pending=None,
            refresh=AsyncMock(),
            rollback=AsyncMock(),
            scalars=AsyncMock(return_value=SimpleNamespace(all=lambda: [])),
        )

        async def execute(*_args, **_kwargs):
            await queue_lock.acquire()
            db.locked = True

        async def scalar(*_args, **_kwargs):
            return shared.row

        async def commit():
            if db.pending is not None:
                shared.row = db.pending
            if db.locked:
                db.locked = False
                queue_lock.release()

        db.execute, db.scalar, db.commit = (
            AsyncMock(side_effect=execute),
            AsyncMock(side_effect=scalar),
            AsyncMock(side_effect=commit),
        )
        db.add = lambda row: setattr(db, "pending", row)
        return db

    first, second = await asyncio.wait_for(
        asyncio.gather(
            jobs.submit_attempt(session(), f.user, f.req, "same-image"),
            jobs.submit_attempt(session(), f.user, f.req, "same-image"),
        ),
        timeout=5,
    )
    assert first.id == second.id == shared.row.id
    f.slots.assert_awaited_once()
    f.writes.assert_awaited_once()
    f.delivery.assert_awaited_once_with(first.id)


@pytest.mark.asyncio
async def test_preparation_capacity_is_bounded_and_cancellation_does_not_release_running_slot(admission, monkeypatch):
    f = admission
    # Exercise saturation without retaining the production limit of 64 images.
    monkeypatch.setattr(jobs, "_ADMISSION_PREPARATION_SLOTS", threading.BoundedSemaphore(2))
    released = threading.Event()
    counts, guard = {"started": 0, "finished": 0}, threading.Lock()
    original = direct_service.prepare_direct_3d_capture

    def blocked(req):
        with guard:
            counts["started"] += 1
        try:
            released.wait(3)
            return original(req)
        finally:
            with guard:
                counts["finished"] += 1

    monkeypatch.setattr(direct_service, "prepare_direct_3d_capture", blocked)
    tasks = [asyncio.create_task(jobs.submit_attempt(f.db, f.user, f.req, f"blocked-{i}")) for i in range(2)]
    try:
        async with asyncio.timeout(2):
            while counts["started"] != 2:
                await asyncio.sleep(0.001)
        with pytest.raises(HTTPException) as busy:
            await jobs.submit_attempt(f.db, f.user, f.req, "overflow")
        assert busy.value.status_code == 429
        tasks[0].cancel()
        with pytest.raises(asyncio.CancelledError):
            await tasks[0]
        with pytest.raises(HTTPException) as still_busy:
            await jobs.submit_attempt(f.db, f.user, f.req, "overflow-after-cancel")
        assert still_busy.value.status_code == 429
        f.db.execute.assert_not_awaited()
        f.slots.assert_not_awaited()
    finally:
        released.set()
        await asyncio.gather(*tasks, return_exceptions=True)
        async with asyncio.timeout(3):
            while counts["finished"] != 2:
                await asyncio.sleep(0.001)
    f.slots.assert_awaited_once()
    f.delivery.assert_awaited_once()
