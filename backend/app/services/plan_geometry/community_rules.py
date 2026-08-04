"""Rule profiles — the hard-rule layer, resolved from scenario + parameters.

CSPS033 fire access is the one non-negotiable: every internal street must keep
a 6.0 m clear width. The ROW is clear width + walk zones; a parameter asking
for less than the floor is raised to it and noted.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.services.plan_metrics import coerce_floors

FIRE_CLEAR_WIDTH_M = 6.0  # CSPS033 — hard rule
WALK_ZONE_EACH_SIDE_M = 1.8  # sidewalk/boulevard per side inside the ROW
MIN_ROW_M = FIRE_CLEAR_WIDTH_M + 2 * WALK_ZONE_EACH_SIDE_M  # 9.6
FLOOR_HEIGHT_M = 3.2
# Rear laneways are secondary access — blocks they serve still front a full
# street, so CSPS033's clear-width floor applies to the fronting streets, not
# the lane itself (Calgary lanes are typically 6-9 m).
LANE_ROW_M = 7.0


@dataclass(frozen=True)
class RuleProfile:
    scenario_id: str
    block_target_m: float  # preferred block edge (street-grid spacing = this + local ROW)
    row_width_m: float  # internal street right-of-way
    open_space_share: float  # of gross site area
    coverage_ratio: float  # building footprint / net block area (cap)
    parcel_width_m: float
    front_setback_m: float
    building_depth_m: float  # perimeter-block bar depth
    floors: float  # working storey count (ceilings clamp per block)
    floors_note: str
    perimeter_inset_m: float  # boundary inset before the internal grid starts
    # Hard walkability cap on the LONGEST block edge. The street grid adds
    # internal streets until no block edge exceeds this — so a site smaller
    # than one target block still subdivides instead of becoming a single
    # megablock ringed by a giant courtyard. Design target (~90-130 m for
    # inner-city grain), well under the evaluator's 220 m outer bound.
    max_block_edge_m: float = 120.0
    # Street hierarchy: one wide main spine + narrower locals. The widths are
    # chosen so the frontend width-band resolver lands on distinct street
    # archetypes (locals 10-15 m -> narrow_residential_street, spine >=22 m ->
    # main_street_complete / a direct arterial id).
    spine_row_width_m: float = 22.0
    local_row_width_m: float = 14.0

    @property
    def clear_width_m(self) -> float:
        # The narrowest full street governs fire access (lanes are exempt —
        # see LANE_ROW_M). Locals never drop below MIN_ROW_M, so this stays
        # >= FIRE_CLEAR_WIDTH_M by construction.
        return min(self.row_width_m, self.local_row_width_m) - 2 * WALK_ZONE_EACH_SIDE_M


# block = preferred block edge; edge = hard max block edge (forces subdivision).
# Calibrated to inner-city / Calgary grain (2026-07-12 morphology research):
# walkable block 80-110 m/side, short axis 60-90 m, long axis <=150 m; Calgary
# inner-city block faces ~80-120 m, ~79 m deep between lanes; Complete Streets
# 150 m min intersection spacing. The edge cap = min(block+20, 120) with a
# 105 m floor so it always binds BELOW medium-site scale (converts the old
# single-megablock bug into real subdivision). City Beautiful keeps the
# grandest grain; Environmental the finest/most permeable.
_SCENARIO_DEFAULTS: dict[str, dict[str, float]] = {
    "economic": {"block": 100.0, "edge": 120.0, "open": 0.10, "coverage": 0.50},
    "city_policy": {"block": 95.0, "edge": 115.0, "open": 0.12, "coverage": 0.50},
    "city_beautiful": {"block": 115.0, "edge": 120.0, "open": 0.18, "coverage": 0.45},
    "environmental": {"block": 85.0, "edge": 105.0, "open": 0.20, "coverage": 0.42},
    # Retired V1 preset ids — kept so existing scenario rows redraw sensibly.
    "as_of_right": {"block": 115.0, "edge": 120.0, "open": 0.10, "coverage": 0.50},
    "lap_compliant": {"block": 95.0, "edge": 115.0, "open": 0.12, "coverage": 0.50},
    "climate_first": {"block": 85.0, "edge": 105.0, "open": 0.16, "coverage": 0.45},
}
_DEFAULTS = {"block": 100.0, "edge": 120.0, "open": 0.10, "coverage": 0.50}

# Custom-brief rule hints: hint key -> (defaults key, min, max). The open-space
# ceiling is 0.30 ON PURPOSE — it matches the evaluator's own revision ceiling
# (plan_evaluator.py); a higher hint would immediately be revised DOWNWARD and
# the drawn plan would contradict the brief anyway.
_RULE_HINT_CLAMPS: dict[str, tuple[str, float, float]] = {
    "open_space_share": ("open", 0.05, 0.30),
    "coverage_ratio": ("coverage", 0.30, 0.60),
    # Block edge floor lowered to 60 m so the Master Planner can call for a
    # genuinely fine inner-city grain; the edge cap tracks the target.
    "block_target_m": ("block", 60.0, 220.0),
    "max_block_edge_m": ("edge", 70.0, 230.0),
}


def _param_value(parameters: dict[str, Any], path: str) -> Any:
    merged = parameters.get(path)
    if isinstance(merged, dict) and "value" in merged:
        return merged["value"]
    return merged


def resolve_rules(
    scenario_id: str,
    parameters: dict[str, Any],
    *,
    rule_hints: dict[str, float] | None = None,
) -> tuple[RuleProfile, list[dict[str, Any]]]:
    """PlanParameters + scenario -> RuleProfile (+ notes about coercions).

    rule_hints are deterministic overrides extracted from a custom brief —
    merged over the scenario defaults, clamped, and noted. Presets pass None.
    """
    notes: list[dict[str, Any]] = []
    defaults = dict(_SCENARIO_DEFAULTS.get(scenario_id, _DEFAULTS))

    for hint_key, (defaults_key, lo, hi) in _RULE_HINT_CLAMPS.items():
        raw = (rule_hints or {}).get(hint_key)
        if not isinstance(raw, (int, float)) or isinstance(raw, bool):
            continue
        clamped = min(hi, max(lo, float(raw)))
        defaults[defaults_key] = clamped
        clamp_suffix = f" (clamped from {float(raw):g})" if clamped != float(raw) else ""
        notes.append(
            {
                "code": "RULE_HINT_APPLIED",
                "severity": "info",
                "message": f"Custom brief hint: {hint_key} = {clamped:g}{clamp_suffix}.",
                "source_phase": "community_rules",
            }
        )

    row_param = _param_value(parameters, "streets.row_width_m")
    row_width, _ = coerce_floors(row_param, 1.0)  # numeric-or-range coercion reused
    if row_width is None:
        row_width = 16.0
        notes.append(
            {
                "code": "ROW_DEFAULTED",
                "severity": "info",
                "message": "No interpretable streets.row_width_m — using 16.0 m internal ROW.",
                "source_phase": "row_geometry",
            }
        )
    if row_width < MIN_ROW_M:
        notes.append(
            {
                "code": "FIRE_CLEAR_WIDTH_FLOOR",
                "severity": "warning",
                "message": (
                    f"Requested {row_width:g} m ROW cannot keep the CSPS033 {FIRE_CLEAR_WIDTH_M:g} m "
                    f"clear width plus walk zones — raised to {MIN_ROW_M:g} m."
                ),
                "source_phase": "row_geometry",
            }
        )
        row_width = MIN_ROW_M

    floors, floors_note = coerce_floors(_param_value(parameters, "buildings.floors"), FLOOR_HEIGHT_M)
    if floors is None:
        height, how = coerce_floors(_param_value(parameters, "buildings.height_m"), FLOOR_HEIGHT_M)
        if height:
            floors = height / FLOOR_HEIGHT_M
            floors_note = f"{how}; / {FLOOR_HEIGHT_M} m per storey"
    if floors is None:
        floors = 4.0
        floors_note = "no floors/height parameter — conservative 4 storeys"
        notes.append(
            {
                "code": "FLOORS_DEFAULTED",
                "severity": "info",
                "message": floors_note,
                "source_phase": "building_placement",
            }
        )

    # Edge cap tracks the (possibly hinted) block target: a bespoke fine grain
    # must not be undone by a stale default edge, and vice-versa.
    edge_cap = max(defaults.get("edge", defaults["block"] + 10.0), defaults["block"])

    profile = RuleProfile(
        scenario_id=scenario_id,
        block_target_m=defaults["block"],
        max_block_edge_m=edge_cap,
        row_width_m=float(row_width),
        open_space_share=defaults["open"],
        coverage_ratio=defaults["coverage"],
        parcel_width_m=22.0,
        front_setback_m=3.0,
        # Shallow ring (Copenhagen 8-13 m dual-aspect) keeps the interior a real
        # daylit courtyard, not an Eixample lightwell — the primary void lever.
        building_depth_m=13.0,
        floors=float(floors),
        floors_note=floors_note,
        perimeter_inset_m=float(row_width) / 2,
        spine_row_width_m=max(22.0, float(row_width)),
        local_row_width_m=min(max(float(row_width), MIN_ROW_M), 14.0),
    )
    return profile, notes
