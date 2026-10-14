"""Supported OpenAI image engines and application credit policy.

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
# Default engine for requests that omit a model and for unknown account access.
# Accounts whose model list confirms 2.5 is absent fall back to "gpt-image-2"
# (see app/services/image_model_availability.py).
DEFAULT_OPENAI_IMAGE_MODEL: OpenAIImageModel = "gpt-image-2.5-flare"
OPENAI_IMAGE_CREDIT_MULTIPLIERS: dict[str, int] = {
    "gpt-image-2.5-flare": 2,
    "gpt-image-2.5-sunburst": 2,
    "gpt-image-2": 1,
    "gpt-image-2-2026-04-21": 1,
}
# Provisional application reservations, not provider invoice estimates. At
# launch both 2.5 engines have twice Image 2's per-token image/text rates.
# Output token counts can differ; keep quality capped at the existing high
# setting and review these envelopes against actual usage after live trials.
