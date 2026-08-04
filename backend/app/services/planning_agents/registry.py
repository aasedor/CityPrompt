"""Expert registry — an expert is DATA, not code. Adding expert #5 = one literal.

Model split per plan: the three core disciplines run claude-sonnet-5; the
public-realm/climate expert runs claude-haiku-4-5 (cheap, ample context).
philosophy_affinity scales an expert's voice in the merge when the scenario's
philosophy aligns with its domain (default 1.0 when absent).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ExpertSpec:
    agent_id: str
    title: str
    model: str
    dna_sections: tuple[str, ...]  # sections this expert receives (token control)
    focus_prompt: str  # role charter, appended AFTER the shared DNA block
    parameter_scope: tuple[str, ...]  # PARAMETER_VOCABULARY paths it may recommend
    philosophy_affinity: dict[str, float] = field(default_factory=dict)


EXPERTS: tuple[ExpertSpec, ...] = (
    ExpertSpec(
        agent_id="land_use_zoning",
        title="Land Use & Zoning Planner",
        model="claude-sonnet-5",
        dna_sections=("site", "land_use", "policy"),
        focus_prompt=(
            "You are the land use and zoning planner. Ground every recommendation in the site's "
            "districts, FAR/height/density assumptions, LAP context, and the policy insight. "
            "Recommend use mix, intensity (floors/height/units) and character consistent with the "
            "regulatory frame; flag where the philosophy pushes beyond as-of-right entitlement."
        ),
        parameter_scope=(
            "buildings.development_type",
            "buildings.floors",
            "buildings.height_m",
            "buildings.unit_count",
            "buildings.development_aesthetic",
            "site.design_brief",
        ),
        philosophy_affinity={
            "missing_middle": 1.3,
            "developer_feasibility": 1.2,
            "new_urbanism": 1.1,
            "neighbourhood_context": 1.3,
        },
    ),
    ExpertSpec(
        agent_id="mobility",
        title="Transportation & Mobility Planner",
        model="claude-sonnet-5",
        dna_sections=("site", "mobility", "policy"),
        focus_prompt=(
            "You are the transportation planner. Reason from road hierarchy, frontage streets, "
            "transit access, bike network and pathways. Recommend street pattern, right-of-way "
            "widths and access strategy; always protect emergency apparatus access (>=6m clear "
            "width) and goods movement while advancing the philosophy."
        ),
        parameter_scope=(
            "streets.row_width_m",
            "layout.strategy",
            "landscape.ground_texture",
            "site.design_brief",
        ),
        philosophy_affinity={"transit_oriented": 1.3, "fifteen_minute": 1.2, "new_urbanism": 1.1},
    ),
    ExpertSpec(
        agent_id="built_form_urban_design",
        title="Urban Designer",
        model="claude-sonnet-5",
        dna_sections=("site", "land_use", "built_form"),
        focus_prompt=(
            "You are the urban designer. Reason from context heights, coverage, grain and street "
            "wall. Recommend massing (floors/height), character, and the layout organizing idea; "
            "ensure transitions to lower-scale neighbours and active frontages."
        ),
        parameter_scope=(
            "buildings.floors",
            "buildings.height_m",
            "buildings.development_aesthetic",
            "layout.strategy",
            "site.design_brief",
        ),
        philosophy_affinity={
            "new_urbanism": 1.3,
            "garden_city": 1.1,
            "landscape_urbanism": 1.1,
            "city_beautiful": 1.5,
        },
    ),
    ExpertSpec(
        agent_id="climate_public_realm",
        title="Climate & Public Realm Specialist",
        model="claude-haiku-4-5-20251001",
        dna_sections=("site", "environment", "public_realm"),
        focus_prompt=(
            "You are the climate and public-realm specialist. Reason from parks access, pathway "
            "connectivity, ground elevation and canopy context. Recommend planting intensity, "
            "ground-plane treatment and open-space structure; favour shade, stormwater and "
            "winter-city comfort."
        ),
        parameter_scope=(
            "landscape.tree_density",
            "landscape.ground_texture",
            "layout.strategy",
            "site.design_brief",
        ),
        philosophy_affinity={"climate_resilience": 1.4, "landscape_urbanism": 1.3, "garden_city": 1.2},
    ),
)


def get_expert(agent_id: str) -> ExpertSpec | None:
    return next((e for e in EXPERTS if e.agent_id == agent_id), None)
