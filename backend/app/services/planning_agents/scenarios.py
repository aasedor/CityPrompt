"""Scenario presets. V1 ships three; the diff baseline is always as_of_right."""

from __future__ import annotations

from app.services.planning_agents.schemas import PhilosophyWeights, ScenarioDefinition

SCENARIO_PRESETS: dict[str, ScenarioDefinition] = {
    "as_of_right": ScenarioDefinition(
        scenario_id="as_of_right",
        label="As-of-Right",
        philosophy=PhilosophyWeights(primary="balanced", intensity=0.3),
        emphasis=(
            "Treat the DNA's land_use FAR/height/density assumptions and district rules as HARD "
            "ceilings. Recommend what today's entitlement supports without relaxations."
        ),
        description="What current zoning supports without any discretionary relief.",
    ),
    "lap_compliant": ScenarioDefinition(
        scenario_id="lap_compliant",
        label="Local Area Plan Aligned",
        philosophy=PhilosophyWeights(primary="new_urbanism", secondary="missing_middle", intensity=0.6),
        emphasis=(
            "Align with the applicable statutory plans and the policy insight's direction "
            "(building-scale categories, corridor policies). Where the plan's direction exceeds "
            "as-of-right zoning, say so in rationales."
        ),
        description="Follows the applicable local area plan direction and policy insight.",
    ),
    "climate_first": ScenarioDefinition(
        scenario_id="climate_first",
        label="Climate First",
        philosophy=PhilosophyWeights(primary="climate_resilience", secondary="landscape_urbanism", intensity=0.8),
        emphasis=(
            "Lead with canopy, shade continuity, green stormwater and winter-city comfort; accept "
            "moderate yield/feasibility trade-offs and record them explicitly."
        ),
        description="Canopy, stormwater and comfort lead; yield trades off.",
    ),
}

DEFAULT_SCENARIO_IDS = ("as_of_right", "lap_compliant", "climate_first")
BASELINE_SCENARIO_ID = "as_of_right"
