"""Gallery artifacts returned by manual and automatic render saves."""

from typing import Optional

from pydantic import BaseModel, Field, model_validator


class SavedRenderResponse(BaseModel):
    id: str
    image_url: str
    prompt: str
    style: Optional[str] = None
    seed: Optional[int] = None
    model: Optional[str] = None
    image_quality: Optional[str] = None
    created_at: str
    # Direct 3D auto-saves: "final" (what the pipeline returned) or
    # "provider_original" (the untouched paid provider image when a safety
    # fallback replaced it). Manual gallery saves leave these unset.
    variant: Optional[str] = None
    outcome: Optional[str] = None
    # Pipeline treatment is separate from the stable review outcome. A clean
    # source fallback can still require review without being a generated finish.
    presentation_strategy: Optional[str] = None
    scene_revision_sha256: Optional[str] = Field(
        default=None,
        pattern=r"^[a-fA-F0-9]{64}$",
    )
    plan_revision_sha256: Optional[str] = None
    camera_revision_sha256: Optional[str] = None
    capture_fingerprint: Optional[str] = None
    output_fingerprint: Optional[str] = None
    provenance_url: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_outcome(cls, value):
        """Read historical compound labels without changing their stored audit."""
        if isinstance(value, dict) and isinstance(value.get("outcome"), str):
            outcome, separator, strategy = value["outcome"].partition(" · ")
            if separator and outcome in {"accepted", "review_required"}:
                value = dict(value)
                value["outcome"] = outcome
                if not value.get("presentation_strategy"):
                    value["presentation_strategy"] = strategy or None
        return value
