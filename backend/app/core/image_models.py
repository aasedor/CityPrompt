"""Supported paid image engines and application credit policy.

Keep explicit legacy IDs for saved workflows. Image 2.6 uses the same Images
edit API; changing engines must not change the geometry-control contract.
"""

from typing import Final, Literal

FLARE_IMAGE_MODEL = "gpt-image-2.6-flare"
SUNBURST_IMAGE_MODEL = "gpt-image-2.6-sunburst"
LEGACY_FLARE_IMAGE_MODEL = "gpt-image-2.5-flare"
LEGACY_SUNBURST_IMAGE_MODEL: Final = "gpt-image-2.5-sunburst"

OpenAIImageModel = Literal[
    "gpt-image-2.6-flare",
    "gpt-image-2.6-sunburst",
    "gpt-image-2.5-flare",
    "gpt-image-2.5-sunburst",
    "gpt-image-2",
    "gpt-image-2-2026-04-21",
]
# Old clients omit a model. Keep those requests working during the rollout;
# current clients discover account access and prefer the new engines.
DEFAULT_OPENAI_IMAGE_MODEL: OpenAIImageModel = "gpt-image-2"
NANO_BANANA_MODEL = "gemini-nano-banana-2.1"
PaidImageModel = Literal[OpenAIImageModel, "gemini-nano-banana-2.1"]
# Keep the same reservation for 2.5 and 2.6. Both generations have the same
# published per-token rates. Token consumption can still vary with the model.
OPENAI_IMAGE_CREDIT_MULTIPLIERS: dict[str, int] = {
    FLARE_IMAGE_MODEL: 2,
    SUNBURST_IMAGE_MODEL: 2,
    LEGACY_FLARE_IMAGE_MODEL: 2,
    LEGACY_SUNBURST_IMAGE_MODEL: 2,
    "gpt-image-2": 1,
    "gpt-image-2-2026-04-21": 1,
}
# Application reservations remain conservative; these are not provider prices.
PAID_IMAGE_CREDIT_MULTIPLIERS = {
    **OPENAI_IMAGE_CREDIT_MULTIPLIERS,
    NANO_BANANA_MODEL: 1,
}


def image_provider_key(settings, model: str) -> str:
    return settings.gemini_api_key if model == NANO_BANANA_MODEL else settings.openai_api_key
