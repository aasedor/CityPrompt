"""Rule profiles — the hard-rule layer, resolved from scenario + parameters.

CSPS033 fire access is the one non-negotiable: every internal street must keep
a 6.0 m clear width. The ROW is clear width + walk zones; a parameter asking
for less than the floor is raised to it and noted.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.services.plan_metrics import coerce_floors

FIRE_CLEAR_WIDTH_M = 6.0          # CSPS033 — hard rule
WALK_ZONE_EACH_SIDE_M = 1.8       # sidewalk/boulevard per side inside the ROW
MIN_ROW_M = FIRE_CLEAR_WIDTH_M + 2 * WALK_ZONE_EACH_SIDE_M  # 9.6
FLOOR_HEIGHT_M = 3.2


@dataclass(frozen=True)
class RuleProfile:
    scenario_id: str
    block_target_m: float          # street-grid spacing (centreline to centreline)
    row_width_m: float             # internal street right-of-way
    open_space_share: float        # of gross site area
    coverage_ratio: float          # building footprint / net block area (cap)
    parcel_width_m: float
    front_setback_m: float
    building_depth_m: float        # perimeter-block bar depth
    floors: float                  # working storey count (ceilings clamp per block)
    floors_note: str
    perimeter_inset_m: float       # boundary inset before the internal grid starts

    @property
    def clear_width_m(self) -> float:
        return self.row_width_m - 2 * WALK_ZONE_EACH_SIDE_M


_SCENARIO_DEFAULTS: dict[str, dict[str, float]] = {
    # block spacing / open share / coverage tuned per philosophy
    "as_of_right": {"block": 200.0, "open": 0.10, "coverage": 0.50},
    "lap_compliant": {"block": 150.0, "open": 0.12, "coverage": 0.50},
    "climate_first": {"block": 160.0, "open": 0.16, "coverage": 0.45},
}
_DEFAULTS = {"block": 180.0, "open": 0.10, "coverage": 0.50}


def _param_value(parameters: dict[str, Any], path: str) -> Any:
    merged = parameters.get(path)
    if isinstance(merged, dict) and "value" in merged:
        return merged["value"]
    return merged


def resolve_rules(
    scenario_id: str,
    parameters: dict[str, Any],
) -> tuple[RuleProfile, list[dict[str, Any]]]:
    """PlanParameters + scenario -> RuleProfile (+ notes about coercions)."""
    notes: list[dict[str, Any]] = []
    defaults = _SCENARIO_DEFAULTS.get(scenario_id, _DEFAULTS)

    row_param = _param_value(parameters, "streets.row_width_m")
    row_width, _ = coerce_floors(row_param, 1.0)  # numeric-or-range coercion reused
    if row_width is None:
        row_width = 16.0
        notes.append({
            "code": "ROW_DEFAULTED", "severity": "info",
            "message": "No interpretable streets.row_width_m — using 16.0 m internal ROW.",
            "source_phase": "row_geometry",
        })
    if row_width < MIN_ROW_M:
        notes.append({
            "code": "FIRE_CLEAR_WIDTH_FLOOR", "severity": "warning",
            "message": (
                f"Requested {row_width:g} m ROW cannot keep the CSPS033 {FIRE_CLEAR_WIDTH_M:g} m "
                f"clear width plus walk zones — raised to {MIN_ROW_M:g} m."
            ),
            "source_phase": "row_geometry",
        })
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
        notes.append({
            "code": "FLOORS_DEFAULTED", "severity": "info",
            "message": floors_note, "source_phase": "building_placement",
        })

    profile = RuleProfile(
        scenario_id=scenario_id,
        block_target_m=defaults["block"],
        row_width_m=float(row_width),
        open_space_share=defaults["open"],
        coverage_ratio=defaults["coverage"],
        parcel_width_m=22.0,
        front_setback_m=3.0,
        building_depth_m=16.0,
        floors=float(floors),
        floors_note=floors_note,
        perimeter_inset_m=float(row_width) / 2,
    )
    return profile, notes
