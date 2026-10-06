"""Real isolated PostgreSQL admission/recovery; every provider/storage call mocked."""

import asyncio
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock
import uuid

from fastapi import HTTPException
import pytest
from sqlalchemy import select

from app.api.v1 import render_animation as animation, video, documents, files
from app.models.models import Project, ProjectShare, User, ApiUsageLog
from app.services.render_trial import TRIAL_KEY
from tests.test_render_attempts import isolated as isolated
from tests.test_kling_video import png


@pytest.fixture
async def pilot(isolated, monkeypatch):  # noqa: F811
    f = isolated
    settings = f.settings.model_copy(
        update={"kling_animation_enabled": True, "fal_key": "mock-key-never-sent"}
    )
    monkeypatch.setattr(animation, "get_settings", lambda: settings)
    monkeypatch.setattr(video, "get_settings", lambda: settings)
    source_bytes = png()
    monkeypatch.setattr(animation, "_read_source", lambda _: source_bytes)
    upload = AsyncMock(return_value="https://fal.media/full-render.png")
    submit = AsyncMock(return_value="saved-fal-request")
    poll = AsyncMock(return_value=("saving", "https://fal.media/paid-output.mp4"))
    monkeypatch.setattr(animation, "upload_kling_source", upload)
    monkeypatch.setattr(animation, "submit_kling_once", submit)
    monkeypatch.setattr(animation, "poll_kling_request", poll)
    download = AsyncMock(return_value=b"mock-paid-video")
    monkeypatch.setattr(animation, "download_kling_video", download)
    saved = {}

    async def save(key, data, _mime):
        saved[key] = data

    monkeypatch.setattr(documents, "_upload_to_storage", save)
    render_id = uuid.uuid4()
    async with f.sessions() as db:
        project = await db.get(Project, f.project.id)
        project.metadata_ = {
            "saved_renders": [
                {
                    "id": str(render_id),
                    "image_url": f"/api/v1/files/projects/{project.id}/renders/{render_id}.png",
                    "prompt": "Finished architectural view",
                    "variant": "final",
                    "outcome": "accepted",
                }
            ],
            TRIAL_KEY: {
                "user_id": str(f.user.id),
                "image_limit": 10,
                "video_limit": 3,
                "image_requests": {},
                "video_requests": {},
            },
        }
        await db.commit()
    req = animation.RenderAnimationRequest(
        project_id=f.project.id,
        source_render_id=render_id,
        request_id=uuid.uuid4(),
        confirm_paid_submission=True,
    )
    return SimpleNamespace(
        **(vars(f) | {"settings": settings}),
        request=req,
        submit=submit,
        upload=upload,
        poll=poll,
        download=download,
        saved=saved,
        source_bytes=source_bytes,
    )


async def generate(f, req=None):
    async with f.sessions() as db:
        return await animation.animate_render(
            req or f.request, await db.get(User, f.user.id), db
        )


async def recover(f, attempt):
    async with f.sessions() as db:
        return await animation.recover_animation(
            f.project.id, uuid.UUID(attempt.id), await db.get(User, f.user.id), db
        )


@pytest.mark.asyncio
async def test_free_preflight_reads_finished_full_resolution_without_provider_or_reservation(
    pilot,
):
    f = pilot
    async with f.sessions() as db:
        result = await animation.preflight_animation(
            animation.RenderAnimationPreflightRequest(
                project_id=f.project.id, source_render_id=f.request.source_render_id
            ),
            await db.get(User, f.user.id),
            db,
        )
        assert (result.width, result.height, result.duration_seconds) == (1600, 900, 5)
        assert result.estimated_cost_usd == 0.56 and result.generate_audio is False
        assert (await db.get(Project, f.project.id)).metadata_[TRIAL_KEY][
            "video_requests"
        ] == {}
        assert (await db.get(User, f.user.id)).render_credits == 1000
    f.submit.assert_not_awaited()
    f.upload.assert_not_awaited()


@pytest.mark.asyncio
async def test_concurrent_idempotent_requests_reserve_bill_and_submit_once(pilot):
    f = pilot
    responses = await asyncio.gather(*(generate(f) for _ in range(8)))
    assert len({item.id for item in responses}) == 1
    f.submit.assert_awaited_once()
    f.upload.assert_awaited_once()
    assert f.upload.call_args.args[1].data == f.source_bytes
    async with f.sessions() as db:
        project = await db.get(Project, f.project.id)
        stored = project.metadata_["video_pilot_attempts"][0]
        assert stored["interaction_id"] == "saved-fal-request"
        assert stored["source_render_id"] == str(f.request.source_render_id)
        assert stored["generation_settings"] == {
            "duration": "5",
            "generate_audio": False,
            "cfg_scale": 0.5,
        }
        assert (
            stored["project_id"] == str(project.id)
            and stored["prompt"]
            and stored["negative_prompt"]
        )
        assert (await db.get(User, f.user.id)).render_credits == 950
        assert len(project.metadata_[TRIAL_KEY]["video_requests"]) == 1
        assert len((await db.execute(select(ApiUsageLog))).scalars().all()) == 1
    with pytest.raises(HTTPException) as exc:
        await generate(
            f, f.request.model_copy(update={"source_render_id": uuid.uuid4()})
        )
    assert exc.value.status_code == 409
    f.submit.assert_awaited_once()


@pytest.mark.asyncio
async def test_receipt_is_durable_before_poll_and_recovery_survives_failure_new_session(
    pilot,
):
    f = pilot
    first = await generate(f)
    f.poll.assert_not_awaited()  # No wait/result fetch before committing the receipt.
    f.poll.side_effect = RuntimeError("temporary queue connection error")
    paused = await recover(f, first)
    assert paused.recoverable and paused.interaction_id == "saved-fal-request"
    f.poll.side_effect = None
    result = await recover(f, paused)
    assert result.status == "complete" and result.source_render_id == str(
        f.request.source_render_id
    )
    assert result.fidelity_status is None
    assert (
        f.saved[result.video_url.removeprefix("/api/v1/files/")] == b"mock-paid-video"
    )
    assert (await recover(f, result)).video_url == result.video_url
    assert (await generate(f)).video_url == result.video_url
    f.submit.assert_awaited_once()
    f.poll.assert_awaited_with(
        "mock-key-never-sent",
        "fal-ai/kling-video/v3/pro/image-to-video",
        "saved-fal-request",
    )
    async with f.sessions() as db:
        assert (await db.get(User, f.user.id)).render_credits == 950
        logs = (await db.execute(select(ApiUsageLog))).scalars().all()
        assert len(logs) == 1 and logs[0].status == "success"


@pytest.mark.asyncio
async def test_unknown_submission_is_visible_and_never_retried(pilot):
    f = pilot
    f.submit.side_effect = TimeoutError("paid receipt lost")
    first = await generate(f)
    assert first.status == "submission_unknown" and not first.recoverable
    assert (await generate(f)).status == "submission_unknown"
    assert (await recover(f, first)).status == "submission_unknown"
    f.submit.assert_awaited_once()
    f.poll.assert_not_awaited()


@pytest.mark.asyncio
async def test_failed_first_receipt_commit_keeps_known_request_id(pilot, monkeypatch):
    f = pilot
    real_update = animation._update_attempt
    failed = False

    async def lose_first_commit(db, project_id, attempt_id, **updates):
        nonlocal failed
        if updates.get("interaction_id") and not failed:
            failed = True
            raise RuntimeError("interrupted receipt commit")
        return await real_update(db, project_id, attempt_id, **updates)

    monkeypatch.setattr(animation, "_update_attempt", lose_first_commit)
    first = await generate(f)
    assert first.interaction_id == "saved-fal-request" and first.recoverable
    assert (await recover(f, first)).status == "complete"
    f.submit.assert_awaited_once()


@pytest.mark.asyncio
async def test_project_ownership_render_membership_and_source_fallback_are_enforced(
    pilot,
):
    f = pilot
    async with f.sessions() as db:
        user = await db.get(User, f.user.id)
        stranger = User(
            id=uuid.uuid4(),
            email=f"{uuid.uuid4()}@test.invalid",
            full_name="Other student",
            role="editor",
        )
        viewer = User(
            id=uuid.uuid4(),
            email=f"{uuid.uuid4()}@test.invalid",
            full_name="View only",
            role="viewer",
        )
        db.add_all([stranger, viewer])
        await db.flush()
        db.add(
            ProjectShare(
                project_id=f.project.id, user_id=viewer.id, permission="viewer"
            )
        )
        await db.commit()
        for actor in [stranger, viewer]:
            with pytest.raises(HTTPException) as exc:
                await animation.animate_render(f.request, actor, db)
            assert exc.value.status_code == 403
        with pytest.raises(HTTPException) as exc:
            await animation.animate_render(
                f.request.model_copy(update={"source_render_id": uuid.uuid4()}),
                user,
                db,
            )
        assert exc.value.status_code == 404
        await db.rollback()
        user = await db.get(User, f.user.id)
        project = await db.get(Project, f.project.id)
        meta = dict(project.metadata_)
        meta["saved_renders"] = [
            {
                **meta["saved_renders"][0],
                "presentation_strategy": "authoritative_source",
            }
        ]
        project.metadata_ = meta
        await db.commit()
        with pytest.raises(HTTPException) as exc:
            await animation.animate_render(f.request, user, db)
        assert exc.value.status_code == 400
    f.submit.assert_not_awaited()


@pytest.mark.asyncio
async def test_storage_failure_retains_receipt_and_recovers_without_rebilling(
    pilot, monkeypatch
):
    f = pilot
    first = await generate(f)
    save = documents._upload_to_storage
    monkeypatch.setattr(
        documents,
        "_upload_to_storage",
        AsyncMock(side_effect=RuntimeError("storage unavailable")),
    )
    paused = await recover(f, first)
    assert paused.recoverable and paused.interaction_id == first.interaction_id
    monkeypatch.setattr(documents, "_upload_to_storage", save)
    assert (await recover(f, first)).status == "complete"
    f.submit.assert_awaited_once()


@pytest.mark.asyncio
async def test_restart_with_stale_poll_lease_and_changed_endpoint_uses_original_job(
    pilot,
):
    f = pilot
    first = await generate(f)
    async with f.sessions() as db:
        project = await db.get(Project, f.project.id)
        meta = dict(project.metadata_)
        meta["video_pilot_attempts"] = [
            {
                **meta["video_pilot_attempts"][0],
                "poll_lease_until": (
                    datetime.now(timezone.utc) - timedelta(seconds=1)
                ).isoformat(),
            }
        ]
        project.metadata_ = meta
        await db.commit()
    f.settings.kling_animation_endpoint = "fal-ai/kling-video/future/pro/image-to-video"
    result = await recover(f, first)
    assert result.status == "complete"
    f.poll.assert_awaited_with(
        "mock-key-never-sent",
        "fal-ai/kling-video/v3/pro/image-to-video",
        "saved-fal-request",
    )
    f.submit.assert_awaited_once()


@pytest.mark.asyncio
async def test_trial_allowance_spans_still_animations_and_route_videos(pilot):
    f = pilot
    for _ in range(3):
        await generate(f, f.request.model_copy(update={"request_id": uuid.uuid4()}))
    with pytest.raises(HTTPException) as exc:
        await generate(f, f.request.model_copy(update={"request_id": uuid.uuid4()}))
    assert exc.value.status_code == 409
    assert f.submit.await_count == 3


@pytest.mark.asyncio
async def test_saved_output_is_shared_but_recovery_and_provider_receipt_stay_private(
    pilot,
):
    f = pilot
    first = await generate(f)
    result = await recover(f, first)
    async with f.sessions() as db:
        viewer = User(
            id=uuid.uuid4(),
            email=f"{uuid.uuid4()}@test.invalid",
            full_name="Team viewer",
            role="viewer",
        )
        editor = User(
            id=uuid.uuid4(),
            email=f"{uuid.uuid4()}@test.invalid",
            full_name="Team editor",
            role="editor",
        )
        db.add_all([viewer, editor])
        await db.flush()
        db.add_all(
            [
                ProjectShare(
                    project_id=f.project.id, user_id=viewer.id, permission="viewer"
                ),
                ProjectShare(
                    project_id=f.project.id, user_id=editor.id, permission="editor"
                ),
            ]
        )
        await db.commit()
        output_key = result.video_url.removeprefix("/api/v1/files/")
        for actor in [viewer, editor]:
            assert (
                await files._authorize_file(output_key, actor, db, None, None) is False
            )
            gallery = await video.list_video_attempts(f.project.id, actor, db)
            assert gallery.attempts[0].video_url == result.video_url
            assert gallery.attempts[0].source_render_id == str(
                f.request.source_render_id
            )
            assert not gallery.attempts[0].recoverable
            assert gallery.attempts[0].interaction_id is None
            assert gallery.attempts[0].request_id == ""
            assert gallery.attempts[0].generation_settings is None
        with pytest.raises(HTTPException) as exc:
            await animation.recover_animation(
                f.project.id, uuid.UUID(first.id), editor, db
            )
        assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_stale_poll_cannot_overwrite_a_newer_completed_result(pilot):
    f = pilot
    first = await generate(f)
    async with f.sessions() as db:
        current = await animation._update_attempt(
            db,
            f.project.id,
            first.id,
            poll_lease_id="newer-worker",
            status="complete",
            video_url="/api/v1/files/saved-output.mp4",
        )
        restored = await animation._recovery_update(
            db,
            f.project.id,
            first.id,
            "expired-worker",
            release=True,
            status="failed",
            error="late failure",
        )
        assert (
            restored["video_url"] == current["video_url"]
            and restored["status"] == "complete"
        )
        assert restored["poll_lease_id"] == "newer-worker"
