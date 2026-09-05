"""Finite client-measured Google mesh evidence, not server height certification."""

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Longitude = Annotated[float, Field(ge=-180, le=180, allow_inf_nan=False)]
Latitude = Annotated[float, Field(ge=-85, le=85, allow_inf_nan=False)]
Height = Annotated[float, Field(ge=-1000, le=10000, allow_inf_nan=False)]


class SharedGroundModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class SharedGroundGrid(SharedGroundModel):
    west: Longitude
    south: Latitude
    columns: int = Field(ge=2, le=600)
    rows: int = Field(ge=2, le=600)
    stepLng: float = Field(gt=0, le=1)
    stepLat: float = Field(gt=0, le=1)


class SharedGroundQuality(SharedGroundModel):
    sampleCount: int = Field(ge=4, le=1200)
    stablePasses: Literal[2]
    maxPassDeltaM: float = Field(ge=0, le=0.08)
    maxSlope: float = Field(ge=0, le=0.45)
    maxLocalResidualM: float = Field(ge=0, le=0.6)


class SharedGroundSnapshot(SharedGroundModel):
    version: Literal[1]
    source: Literal["google_3d_tiles"]
    verticalReference: Literal["WGS84_ellipsoid"]
    boundaryId: UUID
    boundaryUpdatedAt: str = Field(min_length=1, max_length=64)
    boundaryCoordinates: list[tuple[Longitude, Latitude]] = Field(min_length=3, max_length=2048)
    sourceSignature: str = Field(min_length=1, max_length=128)
    grid: SharedGroundGrid
    heights: list[Height] = Field(min_length=4, max_length=1200)
    quality: SharedGroundQuality
    signature: str = Field(min_length=1, max_length=128)

    @field_validator("boundaryUpdatedAt")
    @classmethod
    def aware_revision(cls, value: str) -> str:
        if datetime.fromisoformat(value.replace("Z", "+00:00")).tzinfo is None:
            raise ValueError("Boundary revision must include its time zone")
        return value

    @model_validator(mode="after")
    def complete_grid(self):
        if self.grid.columns * self.grid.rows != len(self.heights) or self.quality.sampleCount != len(self.heights):
            raise ValueError("Shared ground requires one height per grid point")
        west = min(point[0] for point in self.boundaryCoordinates)
        south = min(point[1] for point in self.boundaryCoordinates)
        east = max(point[0] for point in self.boundaryCoordinates)
        north = max(point[1] for point in self.boundaryCoordinates)
        if any(abs(actual - expected) > 1e-9 for actual, expected in (
            (self.grid.west, west), (self.grid.south, south),
            (self.grid.west + (self.grid.columns - 1) * self.grid.stepLng, east),
            (self.grid.south + (self.grid.rows - 1) * self.grid.stepLat, north),
        )):
            raise ValueError("Shared ground support grid must span its boundary bounds")
        return self
