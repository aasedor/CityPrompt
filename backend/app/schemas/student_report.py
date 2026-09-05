import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StudentReportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    zone_ids: list[uuid.UUID] | None = Field(default=None, max_length=5000)


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
