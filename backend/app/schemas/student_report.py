import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.schemas.park_access import ParkAccessSnapshot
from urllib.parse import urlparse


class PolicyMapSource(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(max_length=500)
    url: str = Field(max_length=2048)
    excerpt: str = Field(max_length=6000)
    page: int | None = Field(default=None, ge=1)
    section: str | None = Field(default=None, max_length=100)

    @field_validator("url")
    @classmethod
    def city_source(cls, value: str) -> str:
        url = urlparse(value)
        host = url.hostname or ""
        if url.scheme != "https" or not (host == "calgary.ca" or host.endswith(".calgary.ca")):
            raise ValueError("Map evidence must cite a Calgary source")
        return value


class PolicyMapEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")
    boundary_coordinates: list[tuple[float, float]] = Field(max_length=10000)
    sources: list[PolicyMapSource] = Field(max_length=64)


class StudentReportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    zone_ids: list[uuid.UUID] | None = Field(default=None, max_length=5000)
    park_access_snapshot: ParkAccessSnapshot | None = None
    policy_map_evidence: PolicyMapEvidence | None = None


class StudentDecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    choice: Literal["implement", "adapt", "decline"]
    rationale: str = Field(min_length=1, max_length=6000)
    follow_through: str = Field(default="", max_length=6000)
    expected_revision: int = Field(ge=0)

    @field_validator("rationale")
    @classmethod
    def require_own_reasoning(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Explain your own reasoning before saving a response.")
        return value.strip()
