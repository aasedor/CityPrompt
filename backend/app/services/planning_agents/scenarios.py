"""Scenario presets — four master-plan philosophies plus the custom-brief path.

The diff/comparison baseline is "economic" (the conservative market case: what
would plausibly get built anyway). Retired V1 presets live in
LEGACY_SCENARIO_PRESETS so existing scenario rows keep resolving; new rows can
only be created from SCENARIO_PRESETS.
"""

from __future__ import annotations

from app.services.planning_agents.schemas import PhilosophyWeights, ScenarioDefinition

SCENARIO_PRESETS: dict[str, ScenarioDefinition] = {
    "economic": ScenarioDefinition(
        scenario_id="economic",
        label="Economic",
        philosophy=PhilosophyWeights(
            primary="developer_feasibility", secondary="neighbourhood_context", intensity=0.5,
        ),
        emphasis=(
            "Deliver dependable returns with minimal approval risk. Treat the DNA's built_form "
            "context (surrounding heights, adjacent uses) as the envelope — propose development "
            "similar in scale and character to what is already around the site. Prefer "
            "market-proven formats, simple servicing and sellable frontage. Flag anything likely "
            "to draw neighbourhood opposition."
        ),
        description="Conservative, returns-focused; fits the surrounding neighbourhood.",
    ),
    "city_policy": ScenarioDefinition(
        scenario_id="city_policy",
        label="City Policy",
        philosophy=PhilosophyWeights(
            primary="new_urbanism", secondary="missing_middle", intensity=0.65,
        ),
        emphasis=(
            "Follow the city's adopted policy direction from the DNA policy insight (statutory "
            "plans, building-scale categories, corridor policies) — typically more ambitious than "
            "pure economics. Cite documents (doc/page/quote) for policy claims. Where policy "
            "direction exceeds as-of-right zoning, say so explicitly in rationales."
        ),
        description="Implements the city's adopted policy direction.",
    ),
    "city_beautiful": ScenarioDefinition(
        scenario_id="city_beautiful",
        label="City Beautiful",
        philosophy=PhilosophyWeights(
            primary="city_beautiful", secondary="garden_city", intensity=0.8,
        ),
        emphasis=(
            "Design the most beautiful ensemble this site can carry: formal composition, a grand "
            "tree-lined boulevard, civic landmarks, generous plazas and a formal water feature; "
            "consistent, dignified architectural character throughout. Yield, parking convenience "
            "and cost efficiency are secondary — record every trade-off you accept for beauty."
        ),
        description="Aesthetics first: formal composition, boulevards, civic grandeur.",
    ),
    "environmental": ScenarioDefinition(
        scenario_id="environmental",
        label="Environmental",
        philosophy=PhilosophyWeights(
            primary="climate_resilience", secondary="transit_oriented", intensity=0.8,
        ),
        emphasis=(
            "Most sustainable development achievable: green high-performance buildings, maximum "
            "canopy and green stormwater, and ALTERNATIVE TRANSPORTATION first — walking, cycling "
            "and transit shape the street network; minimize car infrastructure and parking. "
            "Accept yield/feasibility trade-offs and record them."
        ),
        description="Green buildings, canopy, and walking/cycling/transit priority.",
    ),
}

# Retired V1 presets — resolvable for EXISTING scenario rows only (the task
# resolver falls back here); excluded from available_presets and from
# create-scenario validation.
LEGACY_SCENARIO_PRESETS: dict[str, ScenarioDefinition] = {
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

DEFAULT_SCENARIO_IDS = ("economic", "city_policy", "city_beautiful", "environmental")
BASELINE_SCENARIO_ID = "economic"


def resolve_scenario_preset(scenario_id: str) -> ScenarioDefinition | None:
    """Current presets first, then retired ones (old DB rows)."""
    return SCENARIO_PRESETS.get(scenario_id) or LEGACY_SCENARIO_PRESETS.get(scenario_id)
