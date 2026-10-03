"""Paid video admission/recovery with real isolated PostgreSQL and mocked providers."""
import asyncio
import base64
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock
import uuid

from fastapi import HTTPException
import pytest

from app.api.v1 import video, documents, files
from app.models.models import Project, User, ProjectShare
from app.core.security import create_project_asset_ticket, create_file_asset_ticket
from app.services.render_trial import TRIAL_KEY, check_trial_available
from app.services.render_attempts import now
from tests.test_omni_video import _jpeg_data_url
from tests.test_render_attempts import isolated


@pytest.fixture
async def pilot(isolated, monkeypatch):
    f = isolated
    settings = f.settings.model_copy(update={"gemini_api_key": "mock-video-only", "fal_key": "mock-fal-only"})
    monkeypatch.setattr(video, "get_settings", lambda: settings)
    monkeypatch.setattr(video, "_validate_video_scene_revision", AsyncMock(return_value="a" * 64))
    monkeypatch.setattr(video, "seedance_runtime_error", lambda _: None)
    provider = AsyncMock(return_value=SimpleNamespace(video_bytes=b"mock-mp4", mime_type="video/mp4", interaction_id="remote-id", request_id="remote-id", seed=7))
    monkeypatch.setattr(video, "request_omni_video_once", provider)
    monkeypatch.setattr(video, "request_seedance_video_once", provider)
    monkeypatch.setattr(video, "score_video_fidelity", lambda **_: SimpleNamespace(metadata=lambda: {"fidelity_status": "drift", "fidelity_score": 0.1}))
    saved = {}
    async def upload(key, value, _mime):
        saved[key] = value
    monkeypatch.setattr(documents, "_upload_to_storage", upload)
    async with f.sessions() as db:
        project = await db.get(Project, f.project.id)
        project.metadata_ = {TRIAL_KEY: {"user_id": str(f.user.id), "image_limit": 10,
            "video_limit": 3, "image_requests": {}, "video_requests": {}}}
        await db.commit()
    request = video.VideoGenerateRequest(project_id=f.project.id, request_id=uuid.uuid4(), confirm_paid_submission=True,
        guide_frame_base64=_jpeg_data_url(), route_points=[{"x": .2, "y": .8}, {"x": .8, "y": .2}])
    return SimpleNamespace(**vars(f), request=request, video_provider=provider, saved=saved)


async def generate(f, request=None):
    async with f.sessions() as db:
        user = await db.get(User, f.user.id)
        return await video.generate_video(request or f.request, user, db)


@pytest.mark.asyncio
async def test_concurrent_duplicate_video_submits_pay_once_and_recover_after_new_session(pilot):
    f = pilot
    results = await asyncio.gather(*(generate(f) for _ in range(8)))
    assert len({r.attempt.id for r in results}) == 1
    f.video_provider.assert_awaited_once()
    restored = await generate(f)
    assert restored.attempt.status == "complete"
    assert restored.attempt.video_url
    async with f.sessions() as db:
        assert (await db.get(User, f.user.id)).render_credits == 950
        p = await db.get(Project, f.project.id)
        assert len(p.metadata_[TRIAL_KEY]["video_requests"]) == 1
    with pytest.raises(HTTPException) as error:
        await generate(f, f.request.model_copy(update={"scene_brief": "A different camera design request, using the same key."}))
    assert error.value.status_code == 409
    f.video_provider.assert_awaited_once()


@pytest.mark.asyncio
async def test_video_allowance_spans_providers_and_counts_failure(pilot):
    f = pilot
    f.video_provider.side_effect = RuntimeError("uncertain paid outcome")
    with pytest.raises(HTTPException):
        await generate(f)
    assert (await generate(f)).attempt.status == "failed"
    f.video_provider.side_effect = None
    preview = "data:video/webm;base64," + base64.b64encode(b"\x1aE\xdf\xa3" + b"0" * 1024).decode()
    await generate(f, f.request.model_copy(update={"request_id": uuid.uuid4(), "provider": "seedance_mini",
        "control_mode": "preview_video", "preview_video_base64": preview, "preview_video_mime_type": "video/webm"}))
    await generate(f, f.request.model_copy(update={"request_id": uuid.uuid4()}))
    with pytest.raises(HTTPException) as error:
        await generate(f, f.request.model_copy(update={"request_id": uuid.uuid4(), "provider": "seedance_mini",
            "control_mode": "preview_video", "preview_video_base64": preview, "preview_video_mime_type": "video/webm"}))
    assert error.value.status_code == 409
    assert f.video_provider.await_count == 3
    async with f.sessions() as db:
        p = await db.get(Project, f.project.id)
        with pytest.raises(HTTPException):
            check_trial_available(p, f.user.id, "video")
        assert len(p.metadata_[TRIAL_KEY]["video_requests"]) == 3


@pytest.mark.asyncio
async def test_paid_pixels_survive_late_completion_failure(pilot, monkeypatch):
    f = pilot
    real_update = video._update_attempt
    async def fail_complete(db, project_id, attempt_id, **changes):
        if changes.get("status") == "complete":
            raise RuntimeError("simulated interruption after retained pixels")
        return await real_update(db, project_id, attempt_id, **changes)
    monkeypatch.setattr(video, "_update_attempt", fail_complete)
    with pytest.raises(HTTPException):
        await generate(f)
    recovered = await generate(f)
    assert recovered.attempt.status == "complete"
    assert recovered.attempt.fidelity_status == "unavailable"
    assert f.saved[recovered.attempt.video_url.removeprefix("/api/v1/files/")] == b"mock-mp4"
    f.video_provider.assert_awaited_once()


@pytest.mark.asyncio
async def test_interrupted_submission_is_visible_and_never_replayed(pilot):
    f = pilot
    result = await generate(f)
    async with f.sessions() as db:
        p = await db.get(Project, f.project.id)
        meta = dict(p.metadata_)
        entry = dict(meta["video_pilot_attempts"][0])
        entry.update(status="generating", video_url=None,
                     provider_call_started_at=(now() - timedelta(days=1)).isoformat())
        meta["video_pilot_attempts"] = [entry]
        p.metadata_ = meta
        await db.commit()
    recovered = await generate(f)
    assert recovered.attempt.id == result.attempt.id
    assert recovered.attempt.status == "interrupted"
    assert "will not be submitted again" in recovered.attempt.error
    f.video_provider.assert_awaited_once()


@pytest.mark.asyncio
async def test_trial_preflight_does_not_consume_allowance(pilot):
    f = pilot
    async with f.sessions() as db:
        user = await db.get(User, f.user.id)
        for _ in range(2):
            preflight = await video.preflight_video(f.request, user, db)
            assert preflight.provider_called is False
            assert preflight.allowance_scope == "trial"
            assert preflight.max_attempts == preflight.attempts_remaining == 3
        p = await db.get(Project, f.project.id)
        assert p.metadata_[TRIAL_KEY]["video_requests"] == {}
    f.video_provider.assert_not_called()


@pytest.mark.asyncio
async def test_shared_gallery_excludes_others_private_attempt_recovery(pilot, monkeypatch):
    f = pilot
    await generate(f)
    monkeypatch.setattr(video, "check_project_read_access", AsyncMock())
    collaborator = SimpleNamespace(id=uuid.uuid4())
    async with f.sessions() as db:
        project = await db.get(Project, f.project.id)
        meta = dict(project.metadata_)
        saved = meta["video_pilot_attempts"][0]
        private = {**saved, "id": "interrupted-private", "status": "generating", "video_url": None}
        meta["video_pilot_attempts"] = [saved, private]
        project.metadata_ = meta
        await db.commit()
        shared = await video.list_video_attempts(project.id, collaborator, db)
        assert len(shared.attempts) == 1
        assert shared.attempts[0].video_url == saved["video_url"]
        assert shared.attempts[0].request_id == ""
        assert shared.attempts[0].prompt is shared.attempts[0].guide_image_url is None
        own = await video.list_video_attempts(project.id, f.user, db)
        assert len(own.attempts) == 2
        assert own.attempts[1].request_id == private["request_id"]


@pytest.mark.asyncio
async def test_real_membership_saved_video_private_controls_and_revocation(pilot):
    """Exercise the real permission resolver, including old URL credentials."""
    f = pilot
    completed = await generate(f)
    async with f.sessions() as db:
        requester = await db.get(User, f.user.id)
        owner = User(id=uuid.uuid4(), email=f"{uuid.uuid4()}@test.invalid", full_name="Owner", role="editor")
        viewer = User(id=uuid.uuid4(), email=f"{uuid.uuid4()}@test.invalid", full_name="Viewer", role="viewer")
        db.add_all([owner, viewer])
        await db.flush()
        project = await db.get(Project, f.project.id)
        project.owner_id = owner.id
        editor_share = ProjectShare(project_id=project.id, user_id=requester.id, permission="editor")
        viewer_share = ProjectShare(project_id=project.id, user_id=viewer.id, permission="viewer")
        db.add_all([editor_share, viewer_share])
        await db.commit()
        attempt = project.metadata_["video_pilot_attempts"][0]
        output = files._key_from_url(completed.attempt.video_url)
        guide = files._key_from_url(attempt["guide_image_url"])
        image_evidence = f"projects/{project.id}/render-attempts/private/request.json"
        for actor in [owner, requester, viewer]:
            assert await files._authorize_file(output, actor, db, None, None) is False
            shared = await video.list_video_attempts(project.id, actor, db)
            assert len(shared.attempts) == 1
            if actor.id == requester.id:
                assert shared.attempts[0].request_id
                assert await files._authorize_file(guide, actor, db, None, None) is False
            else:
                assert shared.attempts[0].request_id == ""
                assert shared.attempts[0].prompt is None
                with pytest.raises(HTTPException) as exc:
                    await files._authorize_file(guide, actor, db, None, None)
                assert exc.value.status_code == 403
            with pytest.raises(HTTPException) as exc:
                await files._authorize_file(image_evidence, actor, db, None, None)
            assert exc.value.status_code == 403
        project_ticket = create_project_asset_ticket(project.id, requester.id)
        file_ticket = create_file_asset_ticket(output, requester.id)
        await db.delete(editor_share)
        await db.commit()
        for endpoint in [files.get_file, files.head_file]:
            for auth in [dict(user=requester), dict(user=None, asset_ticket=project_ticket), dict(user=None, file_ticket=file_ticket)]:
                with pytest.raises(HTTPException) as exc:
                    await endpoint(output, db=db, **auth)
                assert exc.value.status_code == 403
        with pytest.raises(HTTPException) as exc:
            await video.list_video_attempts(project.id, requester, db)
        assert exc.value.status_code == 403
