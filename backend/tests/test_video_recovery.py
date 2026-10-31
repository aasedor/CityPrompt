"""Paid video admission/recovery with real isolated PostgreSQL and mocked providers."""

import asyncio
import base64
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock
import uuid

from fastapi import HTTPException
import pytest
from tests.test_render_attempts import isolated as render_attempt_fixture

from sqlalchemy import select

from app.api.v1 import video, documents, files
from app.models.models import Project, User, ProjectShare, ApiUsageLog
from app.core.security import create_project_asset_ticket, create_file_asset_ticket
from app.services.render_trial import TRIAL_KEY, check_trial_available
from app.services.render_attempts import now
from tests.test_omni_video import _jpeg_data_url

isolated = render_attempt_fixture  # Pytest discovers the shared fixture by this name.


@pytest.fixture
async def pilot(isolated, monkeypatch):
    f = isolated
    settings = f.settings.model_copy(update={"gemini_api_key": "mock-video-only", "fal_key": "mock-fal-only"})
    monkeypatch.setattr(video, "get_settings", lambda: settings)
    monkeypatch.setattr(video, "_validate_video_scene_revision", AsyncMock(return_value="a" * 64))
    monkeypatch.setattr(video, "seedance_runtime_error", lambda _: None)
    provider = AsyncMock(
        return_value=SimpleNamespace(
            video_bytes=b"mock-mp4", mime_type="video/mp4", interaction_id="remote-id", request_id="remote-id", seed=7
        )
    )
    monkeypatch.setattr(video, "request_omni_video_once", provider)
    monkeypatch.setattr(video, "request_seedance_video_once", provider)
    monkeypatch.setattr(
        video,
        "score_video_fidelity",
        lambda **_: SimpleNamespace(metadata=lambda: {"fidelity_status": "drift", "fidelity_score": 0.1}),
    )
    monkeypatch.setattr(
        video,
        "inspect_video_media",
        lambda *_: {
            "width": 1280,
            "height": 720,
            "fps": 24.0,
            "frame_count": 192,
            "duration_seconds": 8.0,
            "duration_basis": "decoded_frames/fps",
        },
    )
    saved = {}

    async def upload(key, value, _mime):
        saved[key] = value

    monkeypatch.setattr(documents, "_upload_to_storage", upload)
    async with f.sessions() as db:
        project = await db.get(Project, f.project.id)
        project.metadata_ = {
            TRIAL_KEY: {
                "user_id": str(f.user.id),
                "image_limit": 10,
                "video_limit": 3,
                "image_requests": {},
                "video_requests": {},
            }
        }
        await db.commit()
    request = video.VideoGenerateRequest(
        project_id=f.project.id,
        request_id=uuid.uuid4(),
        confirm_paid_submission=True,
        guide_frame_base64=_jpeg_data_url(),
        route_points=[{"x": 0.2, "y": 0.8}, {"x": 0.8, "y": 0.2}],
    )
    return SimpleNamespace(**vars(f), request=request, video_provider=provider, saved=saved)


async def generate(f, request=None):
    async with f.sessions() as db:
        user = await db.get(User, f.user.id)
        return await video.generate_video(request or f.request, user, db)


@pytest.mark.asyncio
async def test_scene_edit_during_control_upload_stops_before_video_spend(pilot, monkeypatch):
    f = pilot
    monkeypatch.setattr(
        video,
        "_validate_video_scene_revision",
        AsyncMock(side_effect=["a" * 64, HTTPException(409, "The scene changed while the source was being saved.")]),
    )
    with pytest.raises(HTTPException) as exc:
        await generate(f)
    assert exc.value.status_code == 409
    f.video_provider.assert_not_awaited()
    async with f.sessions() as db:
        assert (await db.get(User, f.user.id)).render_credits == 1000
        entry = (await db.get(Project, f.project.id)).metadata_["video_pilot_attempts"][0]
        assert entry["status"] == "preflight_failed"
        assert not entry.get("provider_call_started_at")


@pytest.mark.asyncio
@pytest.mark.parametrize("reference_mode", ["architecture_references", "appearance_references"])
async def test_scene_edit_persists_reference_bytes_and_replay_cannot_swap_them(pilot, reference_mode):
    f = pilot
    frames = [_jpeg_data_url(), _jpeg_data_url(width=1920, height=1080)]
    request = f.request.model_copy(
        update={
            "control_mode": "preview_video",
            "omni_reference_mode": reference_mode,
            "route_keyframes_base64": frames,
            "preview_video_base64": base64.b64encode(b"\x1aE\xdf\xa3" + b"0" * 1024).decode(),
            "preview_video_mime_type": "video/webm",
        }
    )
    result = await generate(f, request)
    assert result.attempt.status == "complete"
    payload = f.video_provider.await_args.kwargs["payload"]
    assert [part["type"] for part in payload["input"]] == ["video", "image", "image", "text"]
    for index, frame in enumerate(frames, start=1):
        expected = frame.split(",", 1)[-1]
        assert payload["input"][index]["data"] == expected
        assert base64.b64decode(expected) in f.saved.values()
    async with f.sessions() as db:
        project = await db.get(Project, f.project.id)
        entry = project.metadata_["video_pilot_attempts"][0]
        assert entry["omni_reference_mode"] == reference_mode
        assert entry["reference_image_count"] == 2
    replay = await generate(f, request)
    assert replay.attempt.id == result.attempt.id
    with pytest.raises(HTTPException) as error:
        await generate(f, request.model_copy(update={"route_keyframes_base64": frames[::-1]}))
    assert error.value.status_code == 409
    f.video_provider.assert_awaited_once()


@pytest.mark.asyncio
async def test_pre_reference_mode_receipt_remains_replayable_without_a_new_paid_call(pilot):
    f = pilot
    original = await generate(f)
    async with f.sessions() as db:
        project = await db.get(Project, f.project.id)
        meta = dict(project.metadata_)
        entry = dict(meta["video_pilot_attempts"][0])
        entry.pop("omni_reference_mode")
        entry["request_sha256"] = video.revision_sha256(
            f.request.model_dump(mode="json", exclude={"omni_reference_mode"})
        )
        meta["video_pilot_attempts"] = [entry]
        project.metadata_ = meta
        await db.commit()
    replay = await generate(f)
    assert replay.attempt.id == original.attempt.id
    f.video_provider.assert_awaited_once()


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
        await generate(
            f, f.request.model_copy(update={"scene_brief": "A different camera design request, using the same key."})
        )
    assert error.value.status_code == 409
    f.video_provider.assert_awaited_once()


@pytest.mark.asyncio
async def test_legacy_request_replays_without_new_prompt_or_provider_call(pilot):
    f = pilot
    original = await generate(f)
    async with f.sessions() as db:
        project = await db.get(Project, f.project.id)
        meta = dict(project.metadata_)
        entry = dict(meta["video_pilot_attempts"][0])
        legacy_body = f.request.model_dump(mode="json", exclude={"custom_prompt", "use_custom_prompt_only"})
        entry.pop("custom_prompt", None)
        entry.pop("use_custom_prompt_only", None)
        entry["request_sha256"] = video.revision_sha256(legacy_body)
        meta["video_pilot_attempts"] = [entry]
        project.metadata_ = meta
        await db.commit()
    recovered = await generate(f)
    assert recovered.attempt.id == original.attempt.id
    assert recovered.attempt.status == "complete"
    with pytest.raises(HTTPException) as error:
        await generate(f, f.request.model_copy(update={"custom_prompt": "Add a dog."}))
    assert error.value.status_code == 409
    f.video_provider.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("old_prompt_fields", [set(), {"custom_prompt", "use_custom_prompt_only"}])
async def test_legacy_request_without_character_defaults_replays_exactly_once(pilot, old_prompt_fields):
    f = pilot
    original = await generate(f)
    async with f.sessions() as db:
        project = await db.get(Project, f.project.id)
        meta = dict(project.metadata_)
        entry = dict(meta["video_pilot_attempts"][0])
        for key in list(entry):
            if key.startswith("character_reference_") or key in old_prompt_fields:
                entry.pop(key)
        entry["request_sha256"] = video.revision_sha256(
            f.request.model_dump(
                mode="json", exclude={"character_reference_base64", "character_reference_mime_type"} | old_prompt_fields
            )
        )
        meta["video_pilot_attempts"] = [entry]
        project.metadata_ = meta
        await db.commit()
    assert (await generate(f)).attempt.id == original.attempt.id
    with pytest.raises(HTTPException) as error:
        await generate(f, f.request.model_copy(update={"character_reference_mime_type": "image/jpeg"}))
    assert error.value.status_code == 409
    f.video_provider.assert_awaited_once()


@pytest.mark.asyncio
async def test_four_second_character_edit_saves_exact_private_reference_and_replays(pilot, monkeypatch):
    from tests.test_people_video import _reference
    import hashlib

    f = pilot
    monkeypatch.setattr(
        video,
        "inspect_video_media",
        lambda *_: {
            "width": 1280,
            "height": 720,
            "fps": 24.0,
            "frame_count": 96,
            "duration_seconds": 4.0,
            "duration_basis": "decoded_frames/fps",
        },
    )
    preview = base64.b64encode(b"\x1aE\xdf\xa3" + b"0" * 1024).decode()
    request = video.VideoGenerateRequest.model_validate(
        {
            **f.request.model_dump(),
            "control_mode": "preview_video",
            "duration_seconds": 4,
            "preview_video_base64": preview,
            "preview_video_mime_type": "video/webm",
            "character_reference_base64": _reference(),
            "character_reference_mime_type": "image/png",
        }
    )
    async with f.sessions() as db:
        user = await db.get(User, f.user.id)
        preflight = await video.preflight_video(request, user, db)
    assert preflight.reference_image_count == 1
    f.video_provider.assert_not_awaited()
    result = await generate(f, request)
    sent = f.video_provider.call_args.kwargs["payload"]
    assert sent["input"][-1]["text"] == preflight.prompt_preview
    assert [part["type"] for part in sent["input"]] == ["video", "image", "text"]
    assert result.attempt.source_media["frame_count"] == 96
    async with f.sessions() as db:
        project = await db.get(Project, f.project.id)
        entry = project.metadata_["video_pilot_attempts"][0]
        assert entry["character_reference_sha256"] == hashlib.sha256(base64.b64decode(_reference())).hexdigest()
        assert entry["character_reference_mime_type"] == "image/png"
        assert entry["character_reference_width"] == 64
        assert entry["character_reference_height"] == 128
        assert entry["character_reference_role"] == "identity_appearance"
        assert entry["reference_image_count"] == 1
        assert f.saved[entry["character_reference_url"].removeprefix("/api/v1/files/")] == base64.b64decode(
            _reference()
        )
        assert "character_reference_base64" not in entry
        assert entry["request_sha256"] == video.revision_sha256(request.model_dump(mode="json"))
        control = hashlib.sha256()
        control.update(base64.b64decode(f.request.guide_frame_base64.split(",")[1]))
        control.update(base64.b64decode(preview))
        control.update(base64.b64decode(_reference()))
        assert entry["guide_sha256"] == control.hexdigest()
        monkeypatch.setattr(video, "check_project_read_access", AsyncMock())
        shared = await video.list_video_attempts(project.id, SimpleNamespace(id=uuid.uuid4()), db)
        assert shared.attempts[0].character_reference_url is None
        assert shared.attempts[0].character_reference_sha256 is None
        assert shared.attempts[0].character_reference_role is None
        assert shared.attempts[0].character_reference_mime_type is None
        assert shared.attempts[0].character_reference_width is None
        assert shared.attempts[0].character_reference_height is None
    assert (await generate(f, request)).attempt.id == result.attempt.id
    with pytest.raises(HTTPException) as error:
        await generate(f, request.model_copy(update={"character_reference_base64": _reference(width=65)}))
    assert error.value.status_code == 409
    f.video_provider.assert_awaited_once()


@pytest.mark.asyncio
async def test_invalid_character_reference_never_reserves_or_contacts_provider(pilot):
    f = pilot
    preview = base64.b64encode(b"\x1aE\xdf\xa3" + b"0" * 1024).decode()
    request = f.request.model_copy(
        update={
            "control_mode": "preview_video",
            "preview_video_base64": preview,
            "preview_video_mime_type": "video/webm",
            "character_reference_base64": "not an image",
        }
    )
    with pytest.raises(HTTPException, match="base64"):
        await generate(f, request)
    f.video_provider.assert_not_awaited()
    assert not f.saved
    async with f.sessions() as db:
        project = await db.get(Project, f.project.id)
        assert not project.metadata_[TRIAL_KEY]["video_requests"]
        assert not project.metadata_.get("video_pilot_attempts")


@pytest.mark.asyncio
async def test_video_allowance_spans_providers_and_counts_failure(pilot):
    f = pilot
    f.video_provider.side_effect = RuntimeError("uncertain paid outcome")
    with pytest.raises(HTTPException):
        await generate(f)
    assert (await generate(f)).attempt.status == "failed"
    f.video_provider.side_effect = None
    preview = "data:video/webm;base64," + base64.b64encode(b"\x1aE\xdf\xa3" + b"0" * 1024).decode()
    await generate(
        f,
        f.request.model_copy(
            update={
                "request_id": uuid.uuid4(),
                "provider": "seedance_mini",
                "control_mode": "preview_video",
                "preview_video_base64": preview,
                "preview_video_mime_type": "video/webm",
            }
        ),
    )
    await generate(f, f.request.model_copy(update={"request_id": uuid.uuid4()}))
    with pytest.raises(HTTPException) as error:
        await generate(
            f,
            f.request.model_copy(
                update={
                    "request_id": uuid.uuid4(),
                    "provider": "seedance_mini",
                    "control_mode": "preview_video",
                    "preview_video_base64": preview,
                    "preview_video_mime_type": "video/webm",
                }
            ),
        )
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
async def test_paid_interaction_receipt_survives_download_failure(pilot):
    f = pilot

    async def created_but_download_failed(**kwargs):
        await kwargs["on_interaction"]("saved-google-interaction")
        raise RuntimeError("simulated media download failure")

    f.video_provider.side_effect = created_but_download_failed
    with pytest.raises(HTTPException):
        await generate(f)
    recovered = await generate(f)
    assert recovered.attempt.status == "failed"
    assert recovered.attempt.interaction_id == "saved-google-interaction"
    async with f.sessions() as db:
        usage = await db.scalar(select(ApiUsageLog).where(ApiUsageLog.task_id == recovered.attempt.id))
        assert usage.metadata_["interaction_id"] == "saved-google-interaction"
    f.video_provider.assert_awaited_once()


@pytest.mark.asyncio
async def test_interrupted_submission_is_visible_and_never_replayed(pilot):
    f = pilot
    result = await generate(f)
    async with f.sessions() as db:
        p = await db.get(Project, f.project.id)
        meta = dict(p.metadata_)
        entry = dict(meta["video_pilot_attempts"][0])
        entry.update(
            status="generating", video_url=None, provider_call_started_at=(now() - timedelta(days=1)).isoformat()
        )
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
        saved["custom_prompt"] = "A private scene direction."
        private = {**saved, "id": "interrupted-private", "status": "generating", "video_url": None}
        meta["video_pilot_attempts"] = [saved, private]
        project.metadata_ = meta
        await db.commit()
        shared = await video.list_video_attempts(project.id, collaborator, db)
        assert len(shared.attempts) == 1
        assert shared.attempts[0].video_url == saved["video_url"]
        assert shared.attempts[0].request_id == ""
        assert shared.attempts[0].prompt is shared.attempts[0].guide_image_url is None
        assert shared.attempts[0].custom_prompt == ""
        own = await video.list_video_attempts(project.id, f.user, db)
        assert len(own.attempts) == 2
        assert own.attempts[1].request_id == private["request_id"]


@pytest.mark.asyncio
async def test_custom_video_detail_reaches_preflight_provider_and_saved_history_once(pilot):
    f = pilot
    direction = "A woman walks her dog on the existing sidewalk."
    preview = "data:video/webm;base64," + base64.b64encode(b"\x1aE\xdf\xa3" + b"0" * 1024).decode()
    request = f.request.model_copy(
        update={
            "control_mode": "preview_video",
            "preview_video_base64": preview,
            "preview_video_mime_type": "video/webm",
            "custom_prompt": direction,
            "use_custom_prompt_only": True,
        }
    )
    async with f.sessions() as db:
        user = await db.get(User, f.user.id)
        check = await video.preflight_video(request, user, db)
    f.video_provider.assert_not_awaited()
    result = await generate(f, request)
    assert result.attempt.custom_prompt == direction
    assert result.attempt.prompt == check.prompt_preview
    assert result.attempt.prompt == direction
    assert result.attempt.use_custom_prompt_only is True
    assert result.attempt.prompt.count(direction) == 1
    sent = f.video_provider.call_args.kwargs["payload"]
    assert sent["input"][-1]["text"] == check.prompt_preview
    assert len(sent["input"]) == 2
    assert sent["response_format"]["resolution"] == "1080p"
    assert result.attempt.output_media["frame_count"] == 192
    assert result.attempt.source_media["duration_seconds"] == 8.0
    assert check.estimated_cost_usd == pytest.approx(1.0136)
    await generate(f, request)
    f.video_provider.assert_awaited_once()


@pytest.mark.asyncio
async def test_saved_people_actions_reach_custom_only_preflight_provider_and_idempotent_receipt(pilot):
    f = pilot
    async with f.sessions() as db:
        project = await db.get(Project, f.project.id)
        project.metadata_ = {
            **project.metadata_,
            "scene_details": {
                "revision": 3,
                "props": [{"id": "person", "variant": "people-pilot-commuter", "people_action": "reading"}],
            },
        }
        await db.commit()
    preview = "data:video/webm;base64," + base64.b64encode(b"\x1aE\xdf\xa3" + b"0" * 1024).decode()
    request = f.request.model_copy(
        update={
            "control_mode": "preview_video",
            "details_revision": 3,
            "preview_video_base64": preview,
            "preview_video_mime_type": "video/webm",
            "custom_prompt": "Warm sunset.",
            "use_custom_prompt_only": True,
        }
    )
    async with f.sessions() as db:
        user = await db.get(User, f.user.id)
        preflight = await video.preflight_video(request, user, db)
    f.video_provider.assert_not_awaited()
    assert "reading" in preflight.prompt_preview and "SAVED PEOPLE ACTIONS:" in preflight.prompt_preview
    assert "offscreen" in preflight.prompt_preview
    result = await generate(f, request)
    assert result.attempt.prompt == preflight.prompt_preview
    sent = f.video_provider.call_args.kwargs["payload"]["input"][-1]["text"]
    assert sent == preflight.prompt_preview
    async with f.sessions() as db:
        project = await db.get(Project, f.project.id)
        project.metadata_ = {
            **project.metadata_,
            "scene_details": {
                "revision": 4,
                "props": [{"variant": "people-pilot-commuter", "people_action": "walking"}],
            },
        }
        await db.commit()
    replay = await generate(f, request)
    assert replay.attempt.id == result.attempt.id
    assert replay.attempt.prompt == preflight.prompt_preview
    f.video_provider.assert_awaited_once()


@pytest.mark.asyncio
async def test_no_details_capture_cannot_buy_after_person_added_but_existing_receipt_replays(pilot):
    f = pilot
    original = await generate(f)
    async with f.sessions() as db:
        project = await db.get(Project, f.project.id)
        project.metadata_ = {
            **project.metadata_,
            "scene_details": {
                "version": 1,
                "revision": 1,
                "props": [{"id": "person", "variant": "people-pilot-commuter", "people_action": "reading"}],
            },
        }
        credits = (await db.get(User, f.user.id)).render_credits
        await db.commit()
    async with f.sessions() as db:
        user = await db.get(User, f.user.id)
        with pytest.raises(HTTPException) as preflight_error:
            await video.preflight_video(f.request, user, db)
        assert preflight_error.value.status_code == 409
    with pytest.raises(HTTPException) as generate_error:
        await generate(f, f.request.model_copy(update={"request_id": uuid.uuid4()}))
    assert generate_error.value.status_code == 409
    replay = await generate(f)
    assert replay.attempt.id == original.attempt.id
    assert replay.attempt.prompt == original.attempt.prompt
    f.video_provider.assert_awaited_once()
    async with f.sessions() as db:
        assert (await db.get(User, f.user.id)).render_credits == credits
        project = await db.get(Project, f.project.id)
        assert len(project.metadata_["video_pilot_attempts"]) == 1
        assert len(project.metadata_[TRIAL_KEY]["video_requests"]) == 1


@pytest.mark.asyncio
async def test_invalid_omni_recording_is_refused_without_admission_or_paid_call(pilot, monkeypatch):
    f = pilot
    monkeypatch.setattr(
        video,
        "inspect_video_media",
        lambda *_: {"width": 1280, "height": 720, "fps": 24.0, "frame_count": 48, "duration_seconds": 2.0},
    )
    preview = "data:video/webm;base64," + base64.b64encode(b"\x1aE\xdf\xa3" + b"0" * 1024).decode()
    request = f.request.model_copy(
        update={
            "control_mode": "preview_video",
            "preview_video_base64": preview,
            "preview_video_mime_type": "video/webm",
        }
    )
    with pytest.raises(HTTPException, match="route recording"):
        await generate(f, request)
    f.video_provider.assert_not_awaited()
    async with f.sessions() as db:
        project = await db.get(Project, f.project.id)
        assert not project.metadata_[TRIAL_KEY]["video_requests"]


@pytest.mark.asyncio
async def test_output_check_failure_keeps_paid_pixels_and_never_resubmits(pilot, monkeypatch):
    f = pilot
    monkeypatch.setattr(
        video, "inspect_video_media", lambda *_: (_ for _ in ()).throw(ValueError("Cannot decode result"))
    )
    result = await generate(f)
    assert result.attempt.status == "complete"
    assert result.attempt.video_url
    assert "Cannot decode result" in result.attempt.media_warning
    assert (await generate(f)).attempt.id == result.attempt.id
    f.video_provider.assert_awaited_once()


@pytest.mark.asyncio
async def test_saved_preview_replay_does_not_depend_on_new_codec_checks(pilot, monkeypatch):
    f = pilot
    preview = "data:video/webm;base64," + base64.b64encode(b"\x1aE\xdf\xa3" + b"0" * 1024).decode()
    request = f.request.model_copy(
        update={
            "control_mode": "preview_video",
            "preview_video_base64": preview,
            "preview_video_mime_type": "video/webm",
        }
    )
    original = await generate(f, request)
    monkeypatch.setattr(video, "inspect_video_media", lambda *_: (_ for _ in ()).throw(ValueError("Codec unavailable")))
    assert (await generate(f, request)).attempt.id == original.attempt.id
    f.video_provider.assert_awaited_once()


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
            for auth in [
                dict(user=requester),
                dict(user=None, asset_ticket=project_ticket),
                dict(user=None, file_ticket=file_ticket),
            ]:
                with pytest.raises(HTTPException) as exc:
                    await endpoint(output, db=db, **auth)
                assert exc.value.status_code == 403
        with pytest.raises(HTTPException) as exc:
            await video.list_video_attempts(project.id, requester, db)
        assert exc.value.status_code == 403
