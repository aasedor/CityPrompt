"""Photographic guides reuse the image outbox without buying a video."""

import asyncio
import base64
import hashlib
from unittest.mock import AsyncMock
import uuid

from fastapi import HTTPException
import httpx
import pytest

from app.models.models import User
from app.models.render_attempt import RenderAttempt
from app.services import render_attempts as jobs
from app.services import video_appearance as appearance
from app.schemas.video_appearance import VideoAppearanceRequest
from tests.test_render_attempts import isolated as image_job_fixture, submit, execute
from tests.test_omni_video import _jpeg_data_url

isolated = image_job_fixture


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "code,expected",
    [
        ("insufficient_quota", "insufficient_quota"),
        ("rate_limit_exceeded", "rate_limit_exceeded"),
        ("private detail with spaces", None),
    ],
)
async def test_failed_guide_keeps_a_safe_provider_code_without_retrying_or_billing(
    isolated, monkeypatch, code, expected
):
    f = isolated
    monkeypatch.setattr(appearance, "get_settings", lambda: f.settings)
    monkeypatch.setattr(appearance, "write_evidence", f.write)
    monkeypatch.setattr(appearance, "validate_scene", AsyncMock(return_value="c" * 64))
    provider = AsyncMock(
        return_value=httpx.Response(
            429, json={"error": {"code": code, "message": "Do not store private provider prose"}}
        )
    )
    monkeypatch.setattr(appearance, "call_image_edit", provider)
    a = await submit(f, req=request(f))
    await execute(f, a)
    evidence = await f.read(a, "provider-error")
    assert evidence == {"billing_status": "unproduced", "status_code": 429, "provider_error_code": expected}
    assert provider.await_count == 1
    async with f.sessions() as db:
        assert (await db.get(User, f.user.id)).render_credits == 1000


def request(f):
    return VideoAppearanceRequest(
        project_id=f.project.id,
        beauty_image_base64=_jpeg_data_url(),
        source_video_sha256="a" * 64,
        details_revision=1,
        community_3d_claims=[],
    )


@pytest.mark.asyncio
async def test_guide_is_one_paid_image_and_recovers_exact_bytes_without_a_second_dispatch(isolated, monkeypatch):
    f = isolated
    monkeypatch.setattr(appearance, "get_settings", lambda: f.settings)
    monkeypatch.setattr(appearance, "write_evidence", f.write)
    monkeypatch.setattr(appearance, "validate_scene", AsyncMock(return_value="c" * 64))
    pixels = _jpeg_data_url().split(",", 1)[1]
    provider = AsyncMock(
        return_value=httpx.Response(200, json={"data": [{"b64_json": pixels}], "usage": {"total_tokens": 42}})
    )
    monkeypatch.setattr(appearance, "call_image_edit", provider)
    key = str(uuid.uuid4())
    attempts = await asyncio.gather(*[submit(f, key, request(f)) for _ in range(8)])
    assert len({a.id for a in attempts}) == 1
    a = attempts[0]
    await asyncio.gather(*[execute(f, a) for _ in range(8)])
    async with f.sessions() as db:
        row = await db.get(RenderAttempt, a.id)
        assert row.status == "completed"
        result = await jobs.recover_result(row)
        assert result["image_base64"] == pixels
        assert result["source_video_sha256"] == "a" * 64
        assert result["scene_revision_sha256"] == "c" * 64
        assert result["output_fingerprint"] == hashlib.sha256(base64.b64decode(pixels)).hexdigest()
        assert (await db.get(User, f.user.id)).render_credits == 974
    assert provider.await_count == 1
    image_request = provider.await_args.args[0]
    assert image_request.model == "gpt-image-2.5-sunburst"
    assert image_request.image_quality == "high" and image_request.post_process is False
    assert image_request.mask_base64 is None
    assert provider.await_args.kwargs["include_mask"] is False
    f.provider.assert_not_awaited()  # The existing Direct 3D provider path is untouched.


@pytest.mark.asyncio
async def test_stale_scene_cannot_spend_for_a_guide(isolated, monkeypatch):
    f = isolated
    monkeypatch.setattr(appearance, "get_settings", lambda: f.settings)
    monkeypatch.setattr(appearance, "validate_scene", AsyncMock(side_effect=HTTPException(409, "Scene changed")))
    provider = AsyncMock()
    monkeypatch.setattr(appearance, "call_image_edit", provider)
    a = await submit(f, req=request(f))
    await execute(f, a)
    async with f.sessions() as db:
        row = await db.get(RenderAttempt, a.id)
        assert row.status == "failed" and row.audit_id is None
        assert (await db.get(User, f.user.id)).render_credits == 1000
    provider.assert_not_awaited()


@pytest.mark.asyncio
async def test_changed_video_or_guide_pixels_cannot_reuse_a_completed_appearance(isolated, monkeypatch):
    f = isolated
    req = request(f)
    a = await submit(f, req=req)
    image = _jpeg_data_url().split(",", 1)[1]
    result = {
        "purpose": "video_appearance",
        "image_base64": image,
        "source_video_sha256": "a" * 64,
        "scene_revision_sha256": "c" * 64,
        "output_fingerprint": hashlib.sha256(base64.b64decode(image)).hexdigest(),
    }
    async with f.sessions() as db:
        row = await db.get(RenderAttempt, a.id)
        row.status = "completed"
        await f.write(row, "response", result)
        await db.commit()
        user = await db.get(User, f.user.id)
        await appearance.validate_binding(
            db,
            user,
            f.project.id,
            a.id,
            source_sha256="a" * 64,
            scene_sha256="c" * 64,
            images=[base64.b64decode(image)],
        )
        for source, scene, images in [
            ("b" * 64, "c" * 64, [base64.b64decode(image)]),
            ("a" * 64, "d" * 64, [base64.b64decode(image)]),
            ("a" * 64, "c" * 64, [b"changed"]),
        ]:
            with pytest.raises(HTTPException) as exc:
                await appearance.validate_binding(
                    db, user, f.project.id, a.id, source_sha256=source, scene_sha256=scene, images=images
                )
            assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_guide_recovery_retains_the_exact_original_video_request(isolated, monkeypatch):
    f = isolated
    from app.api.v1 import render_attempts as routes

    monkeypatch.setattr(routes, "read_evidence", f.read)
    # This is retained private evidence; recovery does not reinterpret/re-encode it.
    source = {
        "preview_video_base64": "ZXhhY3Qtb3JpZ2luYWwtbXA0",
        "route_points": [{"x": 0.2, "y": 0.8}, {"x": 0.8, "y": 0.2}],
    }
    payload = request(f).model_dump(mode="json")
    payload["source_request"] = source
    req = VideoAppearanceRequest.model_validate(payload)
    a = await submit(f, req=req)
    async with f.sessions() as db:
        row = await db.get(RenderAttempt, a.id)
        row.status = "completed"
        await f.write(row, "response", {"purpose": "video_appearance", "image_base64": "saved-guide"})
        await db.commit()
        user = await db.get(User, f.user.id)
        recovered = await routes.result(a.id, user, db)
        assert recovered["source_request"] == source
        assert await routes.recent(f.project.id, user, db) == []
        assert [v["id"] for v in await routes.recent(f.project.id, user, db, purpose="video_appearance")] == [str(a.id)]


@pytest.mark.asyncio
@pytest.mark.parametrize("camera_motion", ["path_follow", "street_walkby", "people_follow"])
async def test_only_aerial_guides_request_google_tile_refinement(isolated, monkeypatch, camera_motion):
    f = isolated
    monkeypatch.setattr(appearance, "get_settings", lambda: f.settings)
    monkeypatch.setattr(appearance, "write_evidence", f.write)
    monkeypatch.setattr(appearance, "validate_scene", AsyncMock(return_value="c" * 64))
    provider = AsyncMock(
        return_value=httpx.Response(200, json={"data": [{"b64_json": _jpeg_data_url().split(",", 1)[1]}]})
    )
    monkeypatch.setattr(appearance, "call_image_edit", provider)
    payload = request(f).model_dump(mode="json")
    payload["source_request"] = {
        "project_id": str(f.project.id),
        "guide_frame_base64": _jpeg_data_url(),
        "route_points": [{"x": 0.2, "y": 0.8}, {"x": 0.8, "y": 0.2}],
        "camera_motion": camera_motion,
    }
    a = await submit(f, req=VideoAppearanceRequest.model_validate(payload))
    await execute(f, a)
    image_request = provider.await_args.args[0]
    if camera_motion == "path_follow":
        assert "AERIAL CONTEXT REFINEMENT" in image_request.prompt
        assert provider.await_args.kwargs["source_view_mode"] == "aerial"
        assert "same footprints, heights, rooflines" in image_request.prompt
    else:
        assert "AERIAL CONTEXT REFINEMENT" not in image_request.prompt
        assert "source_view_mode" not in provider.await_args.kwargs
