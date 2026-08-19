"""Coherence audit — deterministic cross-parameter design review. No LLM.

The gap this closes: ``coordinator.merge_recommendations`` resolves every
parameter path INDEPENDENTLY (argmax by confidence x philosophy affinity). Each
winning value can be individually excellent while the SET is incoherent —
6 storeys adopted from the urban designer beside an 11 m right-of-way adopted
from the mobility planner is a 1.7:1 canyon nobody proposed and nobody costed.
No single expert can catch it, because no expert sees outside its own scope.

So the audit runs on the merged set, in Python, against
``design_doctrine.DOCTRINE_THRESHOLDS``. Every rule:

- fires only on parameters that are actually present (a partial panel result
  degrades to fewer rules, never to a false finding);
- names the doctrine principles it enforces, so the finding is explainable;
- carries a *repair* — a value plus a merge mode — that is legal by the same
  thresholds it was judged against.

Repairs are how the panel survives the Design Director being unavailable: the
plan is still made coherent, deterministically, and the user is told which
moves were mechanical rather than designed.

Severity contract: ``error`` is life-safety or arithmetic impossibility and is
always repaired; ``warning`` is a real design defect; ``info`` is a position
worth stating that a designer may legitimately keep.
"""

from __future__ import annotations

import logging
from typing import Any, Iterable, Literal, Mapping

from pydantic import BaseModel, Field

from app.services.plan_metrics import ASSUMPTIONS
from app.services.planning_agents.design_doctrine import threshold
from app.services.planning_agents.schemas import PhilosophyWeights

logger = logging.getLogger(__name__)

RepairMode = Literal["set", "at_least", "at_most"]
Severity = Literal["info", "warning", "error"]

_SEVERITY_RANK: dict[str, int] = {"info": 0, "warning": 1, "error": 2}

# Ground-plane vocabulary used to detect a paved-vs-planted contradiction.
_HARD_SURFACE_WORDS = ("asphalt", "concrete", "granite", "cobble", "stone", "paver", "paving", "sett")
# Sentinel phrase written into (and then detected in) the design brief by the
# context-transition rule. Declared once so the write and the read cannot drift.
_STEP_DOWN_MARKER = "step the massing down"

_SOFT_SURFACE_WORDS = (
    "permeable",
    "rain garden",
    "raingarden",
    "swale",
    "bioswale",
    "planted",
    "lawn",
    "turf",
    "soil",
    "grass",
    "meadow",
    "gravel",
)


class CoherenceFinding(BaseModel):
    """One cross-parameter defect, with a doctrine-legal repair."""

    rule_id: str
    severity: Severity = "warning"
    message: str
    principle_ids: list[str] = Field(default_factory=list)
    parameter_paths: list[str] = Field(default_factory=list)
    repair_path: str = ""
    repair_value: Any = None
    repair_mode: RepairMode = "set"
    # Human-readable statement of what the repair costs, shown beside it.
    repair_cost: str = ""

    @property
    def code(self) -> str:
        return f"COHERENCE:{self.rule_id}"

    def has_repair(self) -> bool:
        return bool(self.repair_path) and self.repair_value is not None


# ---------------------------------------------------------------------------
# Parameter access — tolerates raw values, MergedParameter, or its dump
# ---------------------------------------------------------------------------


def resolve_values(parameters: Mapping[str, Any]) -> dict[str, Any]:
    """Flatten whatever the caller has into ``{parameter_path: value}``."""
    resolved: dict[str, Any] = {}
    for path, entry in parameters.items():
        value = entry
        if isinstance(entry, Mapping) and "value" in entry:
            value = entry["value"]
        elif hasattr(entry, "value"):
            value = entry.value
        resolved[path] = value
    return resolved


def _num(values: Mapping[str, Any], path: str) -> float | None:
    """Numeric parameter or None. Strings like '18 m' are tolerated because
    experts occasionally emit a unit-suffixed value through the tool schema."""
    raw = values.get(path)
    if isinstance(raw, bool) or raw is None:
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    if isinstance(raw, str):
        cleaned = raw.strip().rstrip("m").rstrip().replace(",", "")
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def _text(values: Mapping[str, Any], path: str) -> str:
    raw = values.get(path)
    return raw.strip().lower() if isinstance(raw, str) else ""


def implied_height_m(floors: float, development_type: str = "") -> float:
    """Height the storey count actually implies, use-aware.

    A mixed-use or commercial ground floor needs the retail premium, so the
    same storey count is a taller building — folding that in here is what keeps
    the height/floors rule from flagging a correctly-taller mixed-use block.
    """
    height = floors * threshold("typical_storey_m")
    if development_type in ("mixed_use", "commercial"):
        height += threshold("ground_floor_premium_m")
    return height


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------


def _rule_fire_access(values: Mapping[str, Any]) -> CoherenceFinding | None:
    row = _num(values, "streets.row_width_m")
    minimum = threshold("fire_clear_width_m")
    if row is None or row >= minimum:
        return None
    return CoherenceFinding(
        rule_id="fire_access",
        severity="error",
        message=(
            f"The recommended {row:g} m right-of-way is below the {minimum:g} m clear width "
            "emergency apparatus requires. Intimate streets are a legitimate position right up to "
            "this line and never past it; the width is raised to the life-safety minimum."
        ),
        principle_ids=["mobility.life_safety"],
        parameter_paths=["streets.row_width_m"],
        repair_path="streets.row_width_m",
        repair_value=minimum,
        repair_mode="at_least",
        repair_cost="Slightly wider street than the mobility position proposed.",
    )


def _rule_street_enclosure(values: Mapping[str, Any]) -> CoherenceFinding | None:
    """Height:width is one decision. This is the rule that catches the canyon
    (or the void) that independent per-path merging creates."""
    row = _num(values, "streets.row_width_m")
    if row is None or row <= 0:
        return None
    height = _num(values, "buildings.height_m")
    floors = _num(values, "buildings.floors")
    if height is None and floors is not None:
        height = implied_height_m(floors, _text(values, "buildings.development_type"))
    if height is None or height <= 0:
        return None

    ratio = height / row
    ratio_max = threshold("enclosure_ratio_max")
    ratio_min = threshold("enclosure_ratio_min")
    comfort_low = threshold("enclosure_ratio_comfort_low")
    comfort_high = threshold("enclosure_ratio_comfort_high")
    row_max_local = threshold("row_max_local_m")

    if ratio > ratio_max:
        # Widen to the top of comfortable enclosure if that stays a
        # neighbourhood street; otherwise the height is the thing that is wrong.
        target_row = round(height / comfort_high, 1)
        if target_row <= row_max_local:
            return CoherenceFinding(
                rule_id="street_enclosure",
                severity="warning",
                message=(
                    f"{height:.1f} m of building on a {row:g} m right-of-way is a "
                    f"{ratio:.1f}:1 canyon — past the {ratio_max:g}:1 limit where sky view, "
                    "daylight and winter sun collapse. No expert proposed this proportion; it is "
                    "an artefact of height and width being decided separately. Widening the "
                    f"right-of-way to {target_row:g} m restores a 1:1 street room."
                ),
                principle_ids=["street.enclosure", "climate.winter_city"],
                parameter_paths=["streets.row_width_m", "buildings.height_m", "buildings.floors"],
                repair_path="streets.row_width_m",
                repair_value=target_row,
                repair_mode="at_least",
                repair_cost="More land in right-of-way, so less net developable area.",
            )
        target_height = round(row * ratio_max, 1)
        return CoherenceFinding(
            rule_id="street_enclosure",
            severity="warning",
            message=(
                f"{height:.1f} m of building on a {row:g} m right-of-way is a {ratio:.1f}:1 canyon, "
                f"and the width needed to hold it ({target_row:g} m) would no longer be a "
                "neighbourhood street. The height is the parameter that has to give: capped at "
                f"{target_height:g} m."
            ),
            principle_ids=["street.enclosure", "climate.winter_city"],
            parameter_paths=["buildings.height_m", "streets.row_width_m"],
            repair_path="buildings.height_m",
            repair_value=target_height,
            repair_mode="at_most",
            repair_cost="Lower massing, so lower yield than the built-form position assumed.",
        )

    if ratio < ratio_min:
        target_row = round(height / comfort_low, 1)
        row_min = threshold("row_min_two_way_m")
        if target_row < row_min:
            return None  # narrowing past a real two-way street is not a repair
        return CoherenceFinding(
            rule_id="street_enclosure",
            severity="info",
            message=(
                f"{height:.1f} m of building on a {row:g} m right-of-way is {ratio:.2f}:1 — below "
                f"the {ratio_min:g} ratio at which a street still reads as an enclosed space. The "
                "result is a road with buildings near it rather than a street. Narrowing to "
                f"{target_row:g} m would give it edges; keeping the width is defensible only if "
                "this is a boulevard whose trees, not its buildings, define it."
            ),
            principle_ids=["street.enclosure", "human.positive_space"],
            parameter_paths=["streets.row_width_m", "buildings.height_m"],
            repair_path="streets.row_width_m",
            repair_value=target_row,
            repair_mode="at_most",
            repair_cost="Narrower carriageway and less room for large-species street trees.",
        )
    return None


def _rule_height_floors_consistency(values: Mapping[str, Any]) -> CoherenceFinding | None:
    height = _num(values, "buildings.height_m")
    floors = _num(values, "buildings.floors")
    if height is None or floors is None or floors <= 0:
        return None
    development_type = _text(values, "buildings.development_type")
    implied = implied_height_m(floors, development_type)
    if implied <= 0:
        return None
    drift = abs(height - implied) / implied
    if drift <= 0.20:
        return None

    use_note = ""
    if development_type in ("mixed_use", "commercial"):
        use_note = (
            f" A {development_type.replace('_', ' ')} ground floor carries a "
            f"{threshold('ground_floor_premium_m'):g} m premium so it can actually let, which is "
            "included in the implied height."
        )
    return CoherenceFinding(
        rule_id="height_floors_consistency",
        severity="warning",
        message=(
            f"{floors:g} storeys implies about {implied:.1f} m at "
            f"{threshold('typical_storey_m'):g} m floor-to-floor, but the adopted height is "
            f"{height:.1f} m — a {drift * 100:.0f}% divergence. Two experts described the same "
            f"massing with different numbers; the geometry engine can only draw one.{use_note}"
        ),
        principle_ids=["street.ground_floor_height", "integrity.arithmetic"],
        parameter_paths=["buildings.height_m", "buildings.floors"],
        repair_path="buildings.height_m",
        repair_value=round(implied, 1),
        repair_mode="set",
        repair_cost="Height is restated from the storey count; the storey count is unchanged.",
    )


def _rule_canopy_deliverability(values: Mapping[str, Any]) -> CoherenceFinding | None:
    density = _num(values, "landscape.tree_density")
    row = _num(values, "streets.row_width_m")
    min_row = threshold("street_tree_min_row_m")
    if density is None or row is None or density < 0.6 or row >= min_row:
        return None
    return CoherenceFinding(
        rule_id="canopy_deliverability",
        severity="warning",
        message=(
            f"A {density:.2f} planting intensity cannot be delivered in a {row:g} m right-of-way. "
            f"Continuous street trees need about {min_row:g} m to fit boulevards with real soil "
            f"volume beside sidewalks and a travel lane ({threshold('structural_soil_min_row_m'):g} m "
            "for large species). Canopy is bought with soil, not with a target — either the street "
            "widens or the number is fiction."
        ),
        principle_ids=["climate.canopy"],
        parameter_paths=["streets.row_width_m", "landscape.tree_density"],
        repair_path="streets.row_width_m",
        repair_value=min_row,
        repair_mode="at_least",
        repair_cost="More land in right-of-way, so less net developable area.",
    )


def _rule_paved_canopy_conflict(values: Mapping[str, Any]) -> CoherenceFinding | None:
    density = _num(values, "landscape.tree_density")
    texture = _text(values, "landscape.ground_texture")
    if density is None or density < 0.6 or not texture:
        return None
    if not any(word in texture for word in _HARD_SURFACE_WORDS):
        return None
    if any(word in texture for word in _SOFT_SURFACE_WORDS):
        return None
    return CoherenceFinding(
        rule_id="paved_canopy_conflict",
        severity="info",
        message=(
            f"A {density:.2f} planting intensity is recommended over a ground plane described as "
            f"'{texture}' — a sealed surface with no permeable or planted component. Trees at this "
            "density need rooting volume and water; a fully hard ground plane gives them neither, "
            "and drains to pipe rather than to the landscape."
        ),
        principle_ids=["climate.absorbent_ground", "climate.canopy"],
        parameter_paths=["landscape.ground_texture", "landscape.tree_density"],
        repair_path="landscape.ground_texture",
        repair_value=f"{texture} with permeable joints, structural soil and rain gardens",
        repair_mode="set",
        repair_cost="Higher unit cost on the ground plane than sealed paving.",
    )


def _rule_yield_plausibility(
    values: Mapping[str, Any],
    site_area_m2: float | None,
) -> CoherenceFinding | None:
    """Unit count against the massing that would have to hold it.

    Uses ``plan_metrics.ASSUMPTIONS`` — the same arithmetic the metrics engine
    runs — so the audit can never disagree with the numbers the UI reports.
    """
    units = _num(values, "buildings.unit_count")
    floors = _num(values, "buildings.floors")
    if units is None or floors is None or not site_area_m2 or site_area_m2 <= 0 or units <= 0 or floors <= 0:
        return None

    row_share = float(ASSUMPTIONS["internal_row_share"]["value"])
    coverage = float(ASSUMPTIONS["coverage_ratio_default"]["value"])
    efficiency = float(ASSUMPTIONS["residential_efficiency"]["value"])
    unit_area = float(ASSUMPTIONS["avg_unit_area_m2"]["value"])
    open_space = float(ASSUMPTIONS["open_space_share_default"]["value"])

    net_area = site_area_m2 * (1.0 - row_share - open_space)
    implied_units = net_area * coverage * floors * efficiency / unit_area
    if implied_units <= 0:
        return None

    band = threshold("yield_plausibility_band")
    ratio = units / implied_units
    if 1 / band <= ratio <= band:
        return None

    direction = "more" if ratio > 1 else "fewer"
    return CoherenceFinding(
        rule_id="yield_plausibility",
        severity="error",
        message=(
            f"{units:g} dwellings is {ratio:.1f}x the roughly {implied_units:.0f} that "
            f"{floors:g} storeys can hold on this site "
            f"({site_area_m2:,.0f} m² gross, less {row_share:.0%} streets and {open_space:.0%} open "
            f"space, at {coverage:.0%} coverage and {unit_area:g} m² average units) — "
            f"{band:g}x outside the plausible band. A yield the massing cannot physically hold is "
            f"not an ambitious position, it is an error, and it discredits every defensible number "
            f"beside it. Restated to the {direction} count the massing supports."
        ),
        principle_ids=["integrity.arithmetic", "context.format_fit"],
        parameter_paths=["buildings.unit_count", "buildings.floors"],
        repair_path="buildings.unit_count",
        repair_value=round(implied_units),
        repair_mode="set",
        repair_cost="The headline unit count changes; the massing it was attached to does not.",
    )


def _rule_context_transition(
    values: Mapping[str, Any],
    context_height_m: float | None,
) -> CoherenceFinding | None:
    if not context_height_m or context_height_m <= 0:
        return None
    height = _num(values, "buildings.height_m")
    floors = _num(values, "buildings.floors")
    if height is None and floors is not None:
        height = implied_height_m(floors, _text(values, "buildings.development_type"))
    if height is None:
        return None
    step = threshold("context_step_ratio")
    if height <= context_height_m * step:
        return None
    # This rule's repair is a design-brief instruction, not a height change, so
    # the triggering height persists. Once the brief carries the step-down the
    # condition is answered — without this the finding would be permanent.
    if _STEP_DOWN_MARKER in _text(values, "site.design_brief"):
        return None
    return CoherenceFinding(
        rule_id="context_transition",
        severity="warning",
        message=(
            f"At {height:.1f} m the proposal is {height / context_height_m:.1f}x the prevailing "
            f"{context_height_m:.1f} m context, past the {step:g}x point where a step-down at the "
            "sensitive edge stops being optional. The height can stand if the plan steps down at "
            "the shared edge — the transition is what converts an objection into an accepted edge, "
            "and it costs less yield than a refusal does."
        ),
        principle_ids=["context.transition", "mobility.transect"],
        parameter_paths=["buildings.height_m", "site.design_brief"],
        repair_path="site.design_brief",
        repair_value=(
            _STEP_DOWN_MARKER.capitalize() + " to within "
            f"{context_height_m * step:.0f} m at edges shared with the existing lower-scale "
            "context, holding the full height toward the interior and the primary frontage."
        ),
        repair_mode="set",
        repair_cost="Lost floor area along the sensitive edge.",
    )


def _rule_row_band(values: Mapping[str, Any]) -> CoherenceFinding | None:
    row = _num(values, "streets.row_width_m")
    row_max = threshold("row_max_local_m")
    if row is None or row <= row_max:
        return None
    return CoherenceFinding(
        rule_id="row_band",
        severity="info",
        message=(
            f"A {row:g} m right-of-way is an arterial cross-section, not a neighbourhood street. "
            "At this width crossing distances and traffic speeds work against the walkable "
            "structure the rest of the plan is pursuing, unless this is deliberately a boulevard "
            "with a planted median and service lanes."
        ),
        principle_ids=["street.enclosure", "grain.short_blocks"],
        parameter_paths=["streets.row_width_m"],
        repair_path="",
        repair_value=None,
        repair_cost="",
    )


def _rule_philosophy_band(
    values: Mapping[str, Any],
    philosophy: PhilosophyWeights | None,
) -> CoherenceFinding | None:
    """A scenario whose adopted intensity contradicts its own stated philosophy."""
    if philosophy is None:
        return None
    floors = _num(values, "buildings.floors")
    if floors is None:
        return None
    stated = {philosophy.primary, philosophy.secondary or ""}

    cap = threshold("missing_middle_max_floors")
    if "missing_middle" in stated and floors > cap:
        return CoherenceFinding(
            rule_id="philosophy_band",
            severity="warning",
            message=(
                f"This scenario runs a missing-middle philosophy but adopted {floors:g} storeys, "
                f"above the {cap:g}-storey band that defines the format. Past that line it is "
                "mid-rise apartment development — a legitimate choice, but it is no longer the "
                "gentle density the scenario is named for, and it should be argued as mid-rise."
            ),
            principle_ids=["context.format_fit", "mobility.transect"],
            parameter_paths=["buildings.floors"],
            repair_path="buildings.floors",
            repair_value=cap,
            repair_mode="at_most",
            repair_cost="Lower yield than the adopted intensity.",
        )

    if "transit_oriented" in stated and floors <= 3:
        return CoherenceFinding(
            rule_id="philosophy_band",
            severity="info",
            message=(
                f"A transit-oriented scenario that adopts {floors:g} storeys puts too few people "
                f"within the {threshold('tod_core_radius_m'):g} m walk to carry the service the "
                "philosophy depends on. Transit-oriented development is a density gradient before "
                "it is anything else; at this intensity the label is doing no work."
            ),
            principle_ids=["mobility.transect", "mobility.daily_needs"],
            parameter_paths=["buildings.floors"],
            repair_path="",
            repair_value=None,
            repair_cost="",
        )
    return None


def _rule_construction_band(values: Mapping[str, Any]) -> CoherenceFinding | None:
    floors = _num(values, "buildings.floors")
    walkup = threshold("walkup_max_floors")
    if floors is None or not (walkup < floors <= walkup + 1):
        return None
    return CoherenceFinding(
        rule_id="construction_band",
        severity="info",
        message=(
            f"{floors:g} storeys sits one floor past the {walkup:g}-storey walk-up ceiling, which "
            "is a construction-type threshold rather than a design one: the whole building moves "
            "to a concrete or steel frame with an elevator core for a single extra floor. Worth "
            f"confirming the extra storey earns its step change, or dropping to {walkup:g}."
        ),
        principle_ids=["context.format_fit"],
        parameter_paths=["buildings.floors"],
        repair_path="",
        repair_value=None,
        repair_cost="",
    )


def _rule_mixed_use_ground_floor(values: Mapping[str, Any]) -> CoherenceFinding | None:
    """Mixed-use declared but the massing leaves no lettable ground floor."""
    development_type = _text(values, "buildings.development_type")
    if development_type not in ("mixed_use", "commercial"):
        return None
    height = _num(values, "buildings.height_m")
    floors = _num(values, "buildings.floors")
    if height is None or floors is None or floors < 1:
        return None
    upper = (floors - 1) * threshold("typical_storey_m")
    ground = height - upper
    minimum = threshold("commercial_ground_floor_min_m")
    # Epsilon guard: a height restated from the storey count lands exactly on
    # this bound, and binary float noise would otherwise re-fire the rule
    # forever with a repair equal to the value already in place.
    if ground >= minimum - 1e-6:
        return None
    return CoherenceFinding(
        rule_id="mixed_use_ground_floor",
        severity="warning",
        message=(
            f"The adopted massing leaves about {ground:.1f} m for the ground floor once "
            f"{floors - 1:g} upper storeys are stacked at {threshold('typical_storey_m'):g} m — "
            f"below the {minimum:g} m a real commercial tenant needs. The plan would be labelled "
            f"{development_type.replace('_', ' ')} while being physically unable to house the use."
        ),
        principle_ids=["street.ground_floor_height", "street.active_frontage"],
        parameter_paths=["buildings.height_m", "buildings.development_type"],
        repair_path="buildings.height_m",
        repair_value=round(upper + minimum, 1),
        repair_mode="at_least",
        repair_cost="Slightly taller building than the built-form position proposed.",
    )


# ---------------------------------------------------------------------------
# Audit + repair
# ---------------------------------------------------------------------------


def audit_coherence(
    parameters: Mapping[str, Any],
    *,
    philosophy: PhilosophyWeights | None = None,
    site_area_m2: float | None = None,
    context_height_m: float | None = None,
) -> list[CoherenceFinding]:
    """Run every rule over the merged parameter set. Never raises.

    Ordered most-severe first so the caller — and the Design Director's prompt —
    sees life-safety and arithmetic failures before stylistic ones.
    """
    values = resolve_values(parameters)

    checks: Iterable[CoherenceFinding | None] = (
        _rule_fire_access(values),
        _rule_yield_plausibility(values, site_area_m2),
        _rule_street_enclosure(values),
        _rule_height_floors_consistency(values),
        _rule_mixed_use_ground_floor(values),
        _rule_canopy_deliverability(values),
        _rule_context_transition(values, context_height_m),
        _rule_philosophy_band(values, philosophy),
        _rule_paved_canopy_conflict(values),
        _rule_construction_band(values),
        _rule_row_band(values),
    )
    findings = [finding for finding in checks if finding is not None]
    findings.sort(key=lambda f: -_SEVERITY_RANK[f.severity])
    return findings


def apply_repairs(
    parameters: Mapping[str, Any],
    findings: list[CoherenceFinding],
    *,
    min_severity: Severity = "warning",
) -> tuple[dict[str, Any], list[CoherenceFinding]]:
    """Apply doctrine-legal repairs to a flat ``{path: value}`` map.

    Merge modes exist so that repairs cannot cancel each other out: a life-
    safety minimum and an enclosure minimum both raise the same right-of-way,
    and the binding one must win regardless of rule order. ``at_least`` takes
    the max, ``at_most`` the min, ``set`` overwrites.

    Returns the repaired values and the findings that were actually applied.
    """
    repaired = dict(resolve_values(parameters))
    applied: list[CoherenceFinding] = []
    floor_rank = _SEVERITY_RANK[min_severity]

    for finding in findings:
        if _SEVERITY_RANK[finding.severity] < floor_rank or not finding.has_repair():
            continue
        path = finding.repair_path
        proposed = finding.repair_value
        current = repaired.get(path)

        if finding.repair_mode in ("at_least", "at_most") and isinstance(proposed, (int, float)):
            current_num = _num(repaired, path)
            if current_num is not None:
                proposed = (
                    max(current_num, float(proposed))
                    if finding.repair_mode == "at_least"
                    else min(current_num, float(proposed))
                )
                if proposed == current_num:
                    continue  # already satisfied by a stronger repair

        if proposed == current:
            continue
        repaired[path] = proposed
        applied.append(finding)

    return repaired, applied


class CoherenceOutcome(BaseModel):
    """Result of auditing and repairing to convergence."""

    initial_findings: list[CoherenceFinding] = Field(default_factory=list)
    applied: list[CoherenceFinding] = Field(default_factory=list)
    residual_findings: list[CoherenceFinding] = Field(default_factory=list)
    values: dict[str, Any] = Field(default_factory=dict)
    passes: int = 0
    converged: bool = True

    @property
    def clean(self) -> bool:
        return not self.initial_findings


MAX_REPAIR_PASSES = 4

# Rules that are NOT design judgements and therefore survive a Design Director
# override: one is pure arithmetic (a storey count and a height must describe
# the same building) and one is life safety. Every other rule encodes a
# position a designer is entitled to overrule with a reason.
ARITHMETIC_RULE_IDS = frozenset({"fire_access", "height_floors_consistency"})


def audit_and_repair(
    parameters: Mapping[str, Any],
    *,
    philosophy: PhilosophyWeights | None = None,
    site_area_m2: float | None = None,
    context_height_m: float | None = None,
    min_severity: Severity = "warning",
    max_passes: int = MAX_REPAIR_PASSES,
) -> CoherenceOutcome:
    """Audit, repair, and re-audit until the parameter set stops changing.

    A single pass is not enough: repairs interact. Capping storeys to hold a
    missing-middle band leaves the previously-consistent height describing a
    building that no longer exists, and only a second pass sees it. Iterating
    to a fixed point is what makes the repaired set genuinely coherent rather
    than coherent-on-the-axis-that-was-checked-last.

    Bounded at ``max_passes``; a set still moving at the bound is reported with
    ``converged=False`` and its residual findings, never silently accepted.
    """
    values = dict(resolve_values(parameters))
    initial = audit_coherence(
        values,
        philosophy=philosophy,
        site_area_m2=site_area_m2,
        context_height_m=context_height_m,
    )

    applied: list[CoherenceFinding] = []
    findings = initial
    passes = 0
    converged = True

    for passes in range(1, max_passes + 1):
        values, pass_applied = apply_repairs(values, findings, min_severity=min_severity)
        applied.extend(pass_applied)
        findings = audit_coherence(
            values,
            philosophy=philosophy,
            site_area_m2=site_area_m2,
            context_height_m=context_height_m,
        )
        if not pass_applied:
            break
    else:
        # Loop ran to the bound with the last pass still changing values.
        converged = not any(
            _SEVERITY_RANK[f.severity] >= _SEVERITY_RANK[min_severity] and f.has_repair() for f in findings
        )
        if not converged:
            logger.warning(
                "Coherence repair did not converge in %d passes; %d finding(s) remain",
                max_passes,
                len(findings),
            )

    return CoherenceOutcome(
        initial_findings=initial,
        applied=applied,
        residual_findings=findings,
        values=values,
        passes=passes,
        converged=converged,
    )
