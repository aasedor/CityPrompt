from types import SimpleNamespace
import pytest
from fastapi import HTTPException
from app.api.v1.video import _photographic_preflight_credit_cost


def config(**changes):
    return SimpleNamespace(
        **dict(
            dict(
                classroom_release=False,
                direct_3d_jobs_enabled=True,
                direct_3d_images_enabled=True,
                openai_api_key="test-only",
            ),
            **changes
        )
    )


def request(**changes):
    return SimpleNamespace(
        **dict(
            dict(
                prepare_photographic_finish=True,
                provider="omni",
                control_mode="preview_video",
                appearance_attempt_id=None,
            ),
            **changes
        )
    )


def test_quote_includes_one_saved_guide_before_any_paid_image():
    assert _photographic_preflight_credit_cost(request(), config()) == 26
    assert _photographic_preflight_credit_cost(request(prepare_photographic_finish=False), config()) == 0
    assert _photographic_preflight_credit_cost(request(appearance_attempt_id="saved"), config()) == 0


@pytest.mark.parametrize(
    "changes",
    [
        dict(classroom_release=True),
        dict(direct_3d_jobs_enabled=False),
        dict(direct_3d_images_enabled=False),
        dict(openai_api_key=""),
    ],
)
def test_unavailable_guide_cannot_get_a_paid_workflow_quote(changes):
    with pytest.raises(HTTPException) as error:
        _photographic_preflight_credit_cost(request(), config(**changes))
    assert error.value.status_code == 503


def test_photographic_preparation_requires_the_original_omni_route():
    with pytest.raises(HTTPException) as error:
        _photographic_preflight_credit_cost(request(control_mode="single_frame"), config())
    assert error.value.status_code == 400


@pytest.mark.asyncio
async def test_free_route_quote_admits_the_combined_workflow_budget(monkeypatch):
    from unittest.mock import AsyncMock
    from app.api.v1 import video

    settings = config()
    settings.omni_video_model = "gemini-omni-1.1-flash"
    monkeypatch.setattr(video, "get_settings", lambda: settings)
    settings.gemini_api_key = "test-only"
    monkeypatch.setattr(video, "check_project_permission", AsyncMock())
    guide = SimpleNamespace(width=1280, height=720, mime_type="image/jpeg")
    monkeypatch.setattr(video, "_preflight_values", lambda req: (guide, [], None, [], "prompt", None))
    monkeypatch.setattr(video, "_inspect_omni_source", AsyncMock())
    monkeypatch.setattr(video, "_validate_video_scene_revision", AsyncMock(return_value="a" * 64))
    monkeypatch.setattr(video, "_validate_appearance_binding", AsyncMock())
    monkeypatch.setattr(video, "_saved_people_prompt", lambda req, project, prompt: prompt)
    monkeypatch.setattr(video, "check_trial_available", lambda *args: None)
    monkeypatch.setattr(video, "is_admin_or_above", lambda user: False)
    req = video.VideoPreflightRequest(
        project_id="00000000-0000-0000-0000-000000000001",
        guide_frame_base64="x" * 100,
        control_mode="preview_video",
        route_points=[dict(x=0.2, y=0.4), dict(x=0.5, y=0.6)],
        prepare_photographic_finish=True,
    )
    db = SimpleNamespace(get=AsyncMock(return_value=SimpleNamespace(metadata_={})))
    user = SimpleNamespace(id="student", render_credits=50)
    with pytest.raises(HTTPException) as error:
        await video.preflight_video(req, user, db)
    assert error.value.status_code == 402
    assert "76" in error.value.detail
    user.render_credits = 76
    quote = await video.preflight_video(req, user, db)
    assert quote.ready and quote.provider_called is False
    assert (quote.video_credit_cost, quote.photographic_guide_credit_cost, quote.total_credit_cost) == (50, 26, 76)
