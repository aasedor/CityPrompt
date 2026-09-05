"""Bounded client-derived park routes; no server geometry-certification claim."""

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Longitude = Annotated[float, Field(ge=-180, le=180, allow_inf_nan=False)]
Latitude = Annotated[float, Field(ge=-85, le=85, allow_inf_nan=False)]
Point = tuple[Longitude, Latitude]
Width = Annotated[float, Field(ge=1.2, le=4, allow_inf_nan=False)]


class ParkAccessModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class ParkAccessSource(ParkAccessModel):
    zoneId: str = Field(min_length=1, max_length=36)
    updatedAt: str = Field(min_length=1, max_length=64)
    geometrySignature: str = Field(min_length=1, max_length=128)

    @field_validator("zoneId")
    @classmethod
    def valid_zone_id(cls, value: str) -> str:
        UUID(value)
        return value

    @field_validator("updatedAt")
    @classmethod
    def aware_revision(cls, value: str) -> str:
        if datetime.fromisoformat(value.replace("Z", "+00:00")).tzinfo is None:
            raise ValueError("Source revision must include its time zone")
        return value


class ParkAccessSettings(ParkAccessModel):
    maxGapM: float = Field(ge=0, le=12)
    pathWidthM: Width
    obstacleClearanceM: float = Field(ge=0.1, le=2)
    maxConnections: int = Field(ge=1, le=3)
    gridStepM: float = Field(ge=1, le=4)


class ParkAccessPath(ParkAccessModel):
    points: list[Point] = Field(min_length=2, max_length=1024)
    widthM: Width


class ParkAccessConnection(ParkAccessModel):
    id: str = Field(min_length=1, max_length=160)
    streetZoneId: UUID
    streetBand: Literal["sidewalk", "path"]
    streetPoint: Point
    gateway: Point
    path: list[Point] = Field(min_length=2, max_length=1024)
    widthM: Width
    streetLiftM: float = Field(ge=-10, le=10)


class ParkAccessPlan(ParkAccessModel):
    parkZoneId: UUID
    status: Literal["connected", "explicit", "blocked", "unresolved"]
    reason: str | None = Field(default=None, max_length=1000)
    connections: list[ParkAccessConnection] = Field(max_length=3)
    paths: list[ParkAccessPath] = Field(max_length=4)


class ParkAccessSnapshot(ParkAccessModel):
    version: Literal[1]
    sourceSignature: str = Field(min_length=1, max_length=128)
    settings: ParkAccessSettings
    eligibleStreetZoneIds: list[UUID] = Field(max_length=256)
    sources: list[ParkAccessSource] = Field(min_length=1, max_length=256)
    parks: list[ParkAccessPlan] = Field(max_length=256)

    @model_validator(mode="after")
    def bounded_routes(self):
        points = sum(
            sum(len(connection.path) + 2 for connection in park.connections)
            + sum(len(path.points) for path in park.paths)
            for park in self.parks
        )
        if points > 16384:
            raise ValueError("Park routes exceed the capture point budget")
        return self
