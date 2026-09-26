"""The video engines City Prompt can hand a route to, and what each one needs.

Adding an engine means one spec here, one service module, and one dispatch
branch in the API. Caps and credits are pilot policy, not provider facts, so
they live here rather than beside each client.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

VideoProviderId = Literal["omni", "seedance_mini", "internal_enhance", "vace_depth", "grok_video"]
VideoVendor = Literal["gemini", "fal", "xai", "local"]
PromptPolicy = Literal["look_sheet", "legacy", "internal"]


@dataclass(frozen=True)
class VideoProviderSpec:
    id: VideoProviderId
    label: str
    vendor: VideoVendor
    operation: str
    output_name: str
    credit_cost: int
    max_calls: int | None
    required_setting: str | None
    control_modes: frozenset[str]
    required_control_videos: frozenset[str]
    prompt_policy: PromptPolicy
    estimated_cost_per_second_usd: float


VIDEO_PROVIDERS: dict[str, VideoProviderSpec] = {
    "omni": VideoProviderSpec(
        id="omni",
        label="Omni",
        vendor="gemini",
        operation="omni_video",
        output_name="omni.mp4",
        credit_cost=50,
        max_calls=49,
        required_setting="gemini_api_key",
        control_modes=frozenset({"single_frame", "multi_keyframe", "preview_video"}),
        required_control_videos=frozenset(),
        prompt_policy="look_sheet",
        estimated_cost_per_second_usd=0.10,
    ),
    "seedance_mini": VideoProviderSpec(
        id="seedance_mini",
        label="Seedance Mini",
        vendor="fal",
        operation="seedance_video",
        output_name="seedance-mini.mp4",
        credit_cost=125,
        max_calls=4,
        required_setting="fal_key",
        control_modes=frozenset({"preview_video"}),
        required_control_videos=frozenset(),
        prompt_policy="legacy",
        estimated_cost_per_second_usd=0.2475,
    ),
    "internal_enhance": VideoProviderSpec(
        id="internal_enhance",
        label="Internal Enhance",
        vendor="local",
        operation="internal_video_enhance",
        output_name="internal-enhance.mp4",
        credit_cost=0,
        max_calls=None,
        required_setting=None,
        control_modes=frozenset({"preview_video"}),
        required_control_videos=frozenset(),
        prompt_policy="internal",
        estimated_cost_per_second_usd=0.0,
    ),
    "vace_depth": VideoProviderSpec(
        id="vace_depth",
        label="Structure Lock",
        vendor="fal",
        operation="vace_depth_video",
        output_name="structure-lock.mp4",
        credit_cost=50,
        max_calls=12,
        required_setting="fal_key",
        control_modes=frozenset({"preview_video"}),
        required_control_videos=frozenset({"depth"}),
        prompt_policy="look_sheet",
        estimated_cost_per_second_usd=0.10,
    ),
    "grok_video": VideoProviderSpec(
        id="grok_video",
        label="Grok Video",
        vendor="xai",
        operation="grok_video",
        output_name="grok-video.mp4",
        credit_cost=75,
        max_calls=20,
        required_setting="xai_api_key",
        control_modes=frozenset({"single_frame", "multi_keyframe", "preview_video"}),
        required_control_videos=frozenset(),
        prompt_policy="look_sheet",
        estimated_cost_per_second_usd=0.05,
    ),
}

VIDEO_PROVIDER_IDS: tuple[str, ...] = tuple(VIDEO_PROVIDERS)


def video_provider(provider_id: str) -> VideoProviderSpec:
    try:
        return VIDEO_PROVIDERS[provider_id]
    except KeyError as exc:
        raise ValueError(f"Unknown video provider '{provider_id}'.") from exc


def provider_setting_error(provider_id: str) -> str | None:
    """The 503 message shown when the engine's key is missing."""
    spec = video_provider(provider_id)
    if spec.required_setting is None:
        return None
    return f"{spec.required_setting.upper()} is not configured."
