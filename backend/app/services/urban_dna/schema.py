"""Urban DNA schema — the contract Planning Agents (and the frontend) consume.

Sections are fixed; fields inside a section are registry-driven (a DatasetSpec
declares dotted paths like ``land_use.dominant_district`` and its transform
produces them). Every field is a DnaField leaf carrying value, confidence, and
dataset provenance so agents can reason about trust and the UI can badge it.

Structural guarantee: all eight sections always exist. A city with no data for
a section still yields it with ``confidence=0`` and populated
``missing_datasets`` — planning continues (never-fail hard requirement).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

DNA_SCHEMA_VERSION = "1.0.0"

SECTION_NAMES = (
    "site",
    "land_use",
    "mobility",
    "public_realm",
    "environment",
    "built_form",
    "market",
    "policy",
)

# Extends docs/community-layout-pipeline-spec.md's geometry-phase union with
# the intelligence phases. Mirror any change in frontend/src/types/index.ts.
SourcePhase = Literal[
    "street_graph",
    "row_geometry",
    "parceling",
    "civic_distribution",
    "zoning",
    "building_placement",
    "collision_validation",
    "city_connector",
    "spatial_engine",
    "policy_intelligence",
    "agent_deliberation",
    "coordinator",
]

# Confidence bands (final plan): fresh / aging cache / partial-or-stale-regime / proxy / missing
CONF_FRESH = 1.0
CONF_AGING_CACHE = 0.8
CONF_DEGRADED = 0.6
CONF_PROXY = 0.3
CONF_MISSING = 0.0


class ValidationNote(BaseModel):
    code: str
    severity: Literal["info", "warning", "error"] = "warning"
    message: str
    source_phase: SourcePhase = "city_connector"


class DnaField(BaseModel):
    value: Any = None
    unit: Optional[str] = None
    confidence: float = CONF_MISSING
    source_datasets: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class SectionMeta(BaseModel):
    confidence: float = 0.0
    missing_datasets: list[str] = Field(default_factory=list)
    warnings: list[ValidationNote] = Field(default_factory=list)


class DnaSection(BaseModel):
    meta: SectionMeta = Field(default_factory=SectionMeta)
    fields: dict[str, DnaField] = Field(default_factory=dict)


class PlanningPhilosophy(BaseModel):
    primary: str = "balanced"
    secondary: Optional[str] = None
    intensity: float = Field(default=0.5, ge=0.0, le=1.0)


class UrbanDNA(BaseModel):
    dna_schema_version: str = DNA_SCHEMA_VERSION
    city_id: str
    project_id: str
    zone_id: str
    site_boundary: dict[str, Any]  # GeoJSON polygon, WGS84
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    site: DnaSection = Field(default_factory=DnaSection)
    land_use: DnaSection = Field(default_factory=DnaSection)
    mobility: DnaSection = Field(default_factory=DnaSection)
    public_realm: DnaSection = Field(default_factory=DnaSection)
    environment: DnaSection = Field(default_factory=DnaSection)
    built_form: DnaSection = Field(default_factory=DnaSection)
    market: DnaSection = Field(default_factory=DnaSection)  # stub until market datasets land
    policy: DnaSection = Field(default_factory=DnaSection)

    philosophy: Optional[PlanningPhilosophy] = None
    overall_confidence: float = 0.0
    missing_datasets: list[str] = Field(default_factory=list)
    warnings: list[ValidationNote] = Field(default_factory=list)

    def section(self, name: str) -> DnaSection:
        if name not in SECTION_NAMES:
            raise KeyError(f"Unknown DNA section {name!r}")
        return getattr(self, name)


def coerce_note(raw: dict[str, Any]) -> ValidationNote:
    """Connector-layer note dicts -> typed ValidationNote (tolerant of extras)."""
    return ValidationNote(
        code=str(raw.get("code", "UNSPECIFIED")),
        severity=raw.get("severity", "warning"),
        message=str(raw.get("message", "")),
        source_phase=raw.get("source_phase", "city_connector"),
    )
