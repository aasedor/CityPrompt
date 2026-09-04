from datetime import datetime
from typing import Any, Literal
import uuid

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class ReferenceLayerMetadata(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    kind: Literal["reference", "zoning"] = "reference"
    source_url: HttpUrl | None = Field(default=None, max_length=2048)
    description: str | None = Field(default=None, max_length=2000)
    color: str = Field(default="#7c3aed", pattern=r"^#[0-9a-fA-F]{6}$")
    opacity: float = Field(default=0.8, ge=0.1, le=1)

    @field_validator("name")
    @classmethod
    def meaningful_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("A layer name is required.")
        return value


class ReferenceLayerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    source_filename: str
    source_crs: str
    source_url: str | None
    description: str | None
    kind: str
    feature_collection: dict[str, Any]
    feature_count: int
    bounds: list[float]
    warnings: list[str]
    color: str
    opacity: float
    created_at: datetime


class ReferenceLayerListResponse(BaseModel):
    layers: list[ReferenceLayerResponse]
    can_edit: bool
