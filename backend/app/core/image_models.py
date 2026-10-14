"""Supported paid image engines and application credit policy.

Keep explicit legacy IDs for saved workflows. Image 2.5 uses the same Images
edit API; changing engines must not change the geometry-control contract.
"""

from typing import Literal

OpenAIImageModel = Literal[
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
OPENAI_IMAGE_CREDIT_MULTIPLIERS: dict[str, int] = {
    "gpt-image-2.5-flare": 2,
    "gpt-image-2.5-sunburst": 2,
    "gpt-image-2": 1,
    "gpt-image-2-2026-04-21": 1,
}
# Application reservations remain conservative; these are not provider prices.
PAID_IMAGE_CREDIT_MULTIPLIERS = {
    **OPENAI_IMAGE_CREDIT_MULTIPLIERS,
    NANO_BANANA_MODEL: 1,
}
# Provisional application reservations, not provider invoice estimates. At
# launch both 2.5 engines have twice Image 2's per-token image/text rates.
# Output token counts can differ; keep quality capped at the existing high
# setting and review these envelopes against actual usage after live trials.


def image_provider_key(settings, model: str) -> str:
    return (
        settings.gemini_api_key
        if model == NANO_BANANA_MODEL
        else settings.openai_api_key
    )
