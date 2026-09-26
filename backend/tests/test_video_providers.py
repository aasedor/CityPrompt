import pytest

from app.services.video_providers import (
    VIDEO_PROVIDER_IDS,
    VIDEO_PROVIDERS,
    provider_setting_error,
    video_provider,
)


def test_five_engines_with_pilot_caps_and_credits():
    assert VIDEO_PROVIDER_IDS == ("omni", "seedance_mini", "internal_enhance", "vace_depth", "grok_video")
    policy = {spec.id: (spec.credit_cost, spec.max_calls) for spec in VIDEO_PROVIDERS.values()}
    assert policy == {
        "omni": (50, 49),
        "seedance_mini": (125, 4),
        "internal_enhance": (0, None),
        "vace_depth": (50, 12),
        "grok_video": (75, 20),
    }


def test_structure_lock_needs_the_depth_track_and_the_preview_mode():
    spec = video_provider("vace_depth")
    assert spec.required_control_videos == {"depth"}
    assert spec.control_modes == {"preview_video"}
    assert spec.required_setting == "fal_key"
    assert spec.prompt_policy == "look_sheet"
    assert spec.output_name == "structure-lock.mp4"


def test_only_seedance_and_internal_keep_the_legacy_prose():
    policies = {spec.id: spec.prompt_policy for spec in VIDEO_PROVIDERS.values()}
    assert policies["seedance_mini"] == "legacy"
    assert policies["internal_enhance"] == "internal"
    assert {policies[key] for key in ("omni", "vace_depth", "grok_video")} == {"look_sheet"}


def test_setting_errors_name_the_environment_variable():
    assert provider_setting_error("grok_video") == "XAI_API_KEY is not configured."
    assert provider_setting_error("omni") == "GEMINI_API_KEY is not configured."
    assert provider_setting_error("internal_enhance") is None
    with pytest.raises(ValueError, match="Unknown video provider"):
        video_provider("runway")
