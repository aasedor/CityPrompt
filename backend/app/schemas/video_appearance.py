"""One optional, reviewable photographic guide for an existing route capture."""

import uuid
from typing import Any
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.direct_3d_render import Direct3DCommunityZoneClaim, Direct3DResidualLandscapeClaim


class VideoAppearanceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    purpose: Literal["video_appearance"] = "video_appearance"
    project_id: uuid.UUID
    beauty_image_base64: str = Field(min_length=100, max_length=20_000_000)
    source_video_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    source_request: dict[str, Any] | None = None
    prompt: str = Field(default="", max_length=600)
    model: Literal["gpt-image-2.5-sunburst"] = "gpt-image-2.5-sunburst"
    style: Literal["video-appearance"] = "video-appearance"
    fidelity_policy: Literal["expressive"] = "expressive"
    details_revision: int | None = Field(default=None, ge=0, strict=True)
    community_3d_claims: list[Direct3DCommunityZoneClaim] = Field(default_factory=list, max_length=2000)
    residual_landscape_claim: Direct3DResidualLandscapeClaim | None = None
