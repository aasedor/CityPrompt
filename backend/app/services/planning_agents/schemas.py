"""Contracts for the planning-agent layer.

PARAMETER_VOCABULARY is the hard boundary between "agents advise" and "engine
draws": every recommendation must target one of these paths, each of which maps
onto a zone-properties key the existing layout_planner/master_plan_2d prompts
already consume. Experts cannot invent parameters; the coordinator cannot emit
values outside what experts proposed.
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

from app.services.urban_dna.schema import ValidationNote

# parameter_path -> how it lands in zone properties + what agents should know
PARAMETER_VOCABULARY: dict[str, dict[str, Any]] = {
    "buildings.development_type": {
        "maps_to": "development_type", "kind": "enum",
        "options": ["residential", "mixed_use", "commercial", "institutional"],
        "description": "primary use for building zones",
    },
    "buildings.floors": {
        "maps_to": "floors", "kind": "number", "unit": "storeys",
        "description": "target storeys for building zones",
    },
    "buildings.height_m": {
        "maps_to": "height", "kind": "number", "unit": "m",
        "description": "target building height",
    },
    "buildings.unit_count": {
        "maps_to": "unit_count", "kind": "number", "unit": "dwellings",
        "description": "target dwelling units on the site",
    },
    "buildings.development_aesthetic": {
        "maps_to": "development_aesthetic", "kind": "string",
        "description": "architectural character family (e.g. 'contemporary_midrise', 'heritage_brick')",
    },
    "streets.row_width_m": {
        "maps_to": "width", "kind": "number", "unit": "m",
        "description": "right-of-way width for internal streets",
    },
    "landscape.tree_density": {
        "maps_to": "tree_density", "kind": "number", "unit": "0-1",
        "description": "canopy/planting intensity from 0 (none) to 1 (dense)",
    },
    "landscape.ground_texture": {
        "maps_to": "ground_texture", "kind": "string",
        "description": "dominant ground-plane treatment (e.g. 'permeable pavers and rain gardens')",
    },
    "layout.strategy": {
        "maps_to": "_layout_strategy_preference", "kind": "string",
        "description": "site layout organizing idea (e.g. 'fine-grained grid', 'central green with courtyards')",
    },
    "site.design_brief": {
        "maps_to": "description_text", "kind": "text",
        "description": "<=60 words of concrete design guidance appended to the site brief",
    },
}


class PhilosophyWeights(BaseModel):
    primary: str = "balanced"
    secondary: Optional[str] = None
    intensity: float = Field(default=0.5, ge=0.0, le=1.0)


class PolicyCitationRef(BaseModel):
    doc: str
    page: int
    quote: str = ""


class Recommendation(BaseModel):
    parameter_path: str
    value: Any
    rationale: str
    claim_type: Literal["policy", "best_practice", "site_derived"] = "site_derived"
    citations: list[PolicyCitationRef] = Field(default_factory=list)
    confidence: float = Field(default=0.6, ge=0.0, le=1.0)
    tension_with: list[str] = Field(default_factory=list)  # parameter_paths it expects to fight


class ExpertRecommendationSet(BaseModel):
    agent_id: str
    summary: str = ""
    recommendations: list[Recommendation] = Field(default_factory=list)
    validation_notes: list[ValidationNote] = Field(default_factory=list)
    failed: bool = False


class MergedParameter(BaseModel):
    parameter_path: str
    value: Any
    rationale: str
    contributors: list[str]                 # agent_ids whose recommendation won/joined
    contested: bool = False
    candidates: list[dict[str, Any]] = Field(default_factory=list)  # all positions, kept for the WHY


class ScenarioDefinition(BaseModel):
    scenario_id: str
    label: str
    philosophy: PhilosophyWeights
    emphasis: str = ""                      # scenario-specific instruction injected into expert prompts
    description: str = ""


class ChangedParameter(BaseModel):
    parameter_path: str
    baseline_value: Any = None
    value: Any = None
    driven_by: str = ""


class ScenarioExplanation(BaseModel):
    baseline: str = "as_of_right"
    changed_parameters: list[ChangedParameter] = Field(default_factory=list)
    narrative: str = ""


class ScenarioResult(BaseModel):
    scenario_id: str
    label: str
    philosophy: PhilosophyWeights
    plan_parameters: dict[str, MergedParameter] = Field(default_factory=dict)
    trade_offs: list[ValidationNote] = Field(default_factory=list)
    expert_summaries: dict[str, str] = Field(default_factory=dict)
    explanation: Optional[ScenarioExplanation] = None
    usage: dict[str, Any] = Field(default_factory=dict)      # tokens + estimated cost
    warnings: list[ValidationNote] = Field(default_factory=list)

    def zone_property_updates(self) -> dict[str, Any]:
        """PlanParameters -> the zone-properties dict the geometry engine reads."""
        updates: dict[str, Any] = {}
        for path, merged in self.plan_parameters.items():
            spec = PARAMETER_VOCABULARY.get(path)
            if spec is None:
                continue
            updates[spec["maps_to"]] = merged.value
        return updates
