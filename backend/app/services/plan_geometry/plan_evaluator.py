"""Plan Evaluator — deterministic measurement of the DRAWN plan, and the
deterministic revision rules that close the generate→evaluate→refine loop.

No LLM judges anything here: every score is spatial arithmetic over the drawn
geometry, every revision is an auditable rule keyed to a finding, and every
iteration's diff is recorded by the caller. Locked layers constrain which
revisions are applicable.
"""

from __future__ import annotations

import logging
import math
from typing import Any

from pydantic import BaseModel, Field
from shapely.ops import unary_union

from app.services.plan_geometry.community_rules import FIRE_CLEAR_WIDTH_M
from app.services.plan_geometry.generator import PlanGeometryResult
from app.services.plan_metrics import coerce_floors

logger = logging.getLogger(__name__)

PARK_ACCESS_RADIUS_M = 400.0
INTERSECTION_TARGET_PER_KM2 = 40.0   # walkable-grid benchmark
# Jacobs long-axis max / Calgary Complete Streets 150 m min intersection
# spacing — the block_scale score rewards real walkable blocks, not a 200 m
# megablock passing as "walkable" (2026-07-12 morphology research).
BLOCK_EDGE_MAX_M = 150.0
CANOPY_TARGET = 0.16                 # Calgary Urban Forest: 16% canopy by 2060
GOOD_ENOUGH_OVERALL = 0.85

SCORE_WEIGHTS = {
    "fire_access": 2.0,              # life-safety weighs double
    "park_access": 1.0,
    "open_space": 1.0,
    "block_scale": 1.0,
    "intersection_density": 0.8,
    "canopy_proxy": 0.8,
    "yield_vs_target": 1.0,
    "ceiling_conformance": 1.0,
    "context_connectivity": 1.0,
}


class ScoreItem(BaseModel):
    key: str
    score: float = Field(ge=0.0, le=1.0)
    measured: float | None = None
    target: float | None = None
    detail: str = ""


class EvaluationReport(BaseModel):
    overall: float = 0.0
    scores: dict[str, ScoreItem] = Field(default_factory=dict)
    notes: list[dict[str, Any]] = Field(default_factory=list)

    def add(self, item: ScoreItem) -> None:
        self.scores[item.key] = item

    def finalize(self) -> "EvaluationReport":
        total = sum(SCORE_WEIGHTS.get(k, 1.0) for k in self.scores)
        self.overall = round(
            sum(s.score * SCORE_WEIGHTS.get(k, 1.0) for k, s in self.scores.items()) / total, 3
        ) if total else 0.0
        return self


def _param_value(parameters: dict[str, Any], path: str) -> Any:
    merged = parameters.get(path)
    if isinstance(merged, dict) and "value" in merged:
        return merged["value"]
    return merged


def evaluate_plan(
    result: PlanGeometryResult,
    parameters: dict[str, Any],
    units_estimate: float | None,
) -> EvaluationReport:
    """Measure the drawn plan. ``units_estimate`` comes from geometry-mode metrics."""
    report = EvaluationReport()
    gi = result.geometry_inputs
    gross = gi.get("site_area_m2") or 1.0

    # 1. Fire access (hard rule; the profile enforces it, this verifies it).
    clear = float(result.rules.get("clear_width_m") or 0.0)
    report.add(ScoreItem(
        key="fire_access", score=1.0 if clear >= FIRE_CLEAR_WIDTH_M else 0.0,
        measured=clear, target=FIRE_CLEAR_WIDTH_M,
        detail=f"internal clear width {clear:g} m vs CSPS033 {FIRE_CLEAR_WIDTH_M:g} m",
    ))

    # 2. Park access: share of building masses within 400 m of drawn open space.
    if result.masses_m:
        if result.green_m:
            green = unary_union(result.green_m)
            served = sum(1 for m in result.masses_m if m.distance(green) <= PARK_ACCESS_RADIUS_M)
            share = served / len(result.masses_m)
            detail = f"{served}/{len(result.masses_m)} building masses within {PARK_ACCESS_RADIUS_M:.0f} m of drawn open space"
        else:
            share, detail = 0.0, "no open space drawn"
        report.add(ScoreItem(key="park_access", score=share, measured=share, target=1.0, detail=detail))

    # 3. Open-space share vs the scenario's target.
    target_share = float(result.rules.get("open_space_share") or 0.1)
    actual_share = (gi.get("open_space_area_m2") or 0.0) / gross
    report.add(ScoreItem(
        key="open_space", score=min(actual_share / target_share, 1.0) if target_share else 1.0,
        measured=round(actual_share, 3), target=target_share,
        detail=f"drawn open space {actual_share:.1%} of gross vs {target_share:.0%} target",
    ))

    # 4. Block scale: share of blocks whose long edge is walkable.
    if result.blocks_m:
        compliant = 0
        for block in result.blocks_m:
            rect = block.minimum_rotated_rectangle
            coords = list(rect.exterior.coords)
            long_edge = max(math.hypot(x2 - x1, y2 - y1)
                            for (x1, y1), (x2, y2) in zip(coords[:-1], coords[1:]))
            if long_edge <= BLOCK_EDGE_MAX_M:
                compliant += 1
        share = compliant / len(result.blocks_m)
        report.add(ScoreItem(
            key="block_scale", score=share, measured=share, target=1.0,
            detail=f"{compliant}/{len(result.blocks_m)} blocks ≤ {BLOCK_EDGE_MAX_M:.0f} m long edge",
        ))

    # 5. Intersection density vs walkable benchmark. A LOCKED street network is
    # reconstructed from area polygons and has no countable centerlines — the
    # density would read as a spurious 0.0, so the dimension is skipped (the
    # user chose that network; the loop may not judge or change it).
    streets_locked = any(n.get("code") == "STREETS_LOCKED" for n in result.notes)
    if not streets_locked:
        density = result.intersection_density_per_km2
        report.add(ScoreItem(
            key="intersection_density", score=min(density / INTERSECTION_TARGET_PER_KM2, 1.0),
            measured=round(density, 1), target=INTERSECTION_TARGET_PER_KM2,
            detail=f"{density:.1f} intersections/km² vs {INTERSECTION_TARGET_PER_KM2:.0f} walkable benchmark",
        ))

    # Existing road/path continuity. Absence of source context is neutral; if
    # anchors exist, every one must join the internal graph to earn full marks.
    context_total = (
        float(gi.get("context_road_anchors") or 0.0)
        + float(gi.get("context_path_anchors") or 0.0)
    )
    if context_total:
        context_served = (
            float(gi.get("context_road_connections") or 0.0)
            + float(gi.get("context_path_connections") or 0.0)
        )
        share = min(context_served / context_total, 1.0)
        report.add(ScoreItem(
            key="context_connectivity", score=share,
            measured=round(share, 3), target=1.0,
            detail=f"{context_served:g}/{context_total:g} detected road/path frontage anchors "
                   "joined to the internal network",
        ))

    # 6. Canopy proxy: planted share of the unbuilt ground plane vs the 2060 target.
    tree_density = _param_value(parameters, "landscape.tree_density")
    tree_density = float(tree_density) if isinstance(tree_density, (int, float)) else 0.4
    unbuilt = max(gross - (gi.get("building_footprint_m2") or 0.0) - (gi.get("row_area_m2") or 0.0), 0.0)
    canopy_share = tree_density * unbuilt / gross
    report.add(ScoreItem(
        key="canopy_proxy", score=min(canopy_share / CANOPY_TARGET, 1.0),
        measured=round(canopy_share, 3), target=CANOPY_TARGET,
        detail=f"tree_density {tree_density:g} × unbuilt {unbuilt / gross:.1%} = {canopy_share:.1%} "
               f"vs {CANOPY_TARGET:.0%} Urban Forest trajectory (proxy)",
    ))

    # 7. Yield vs the experts' unit target (when one exists).
    unit_target, _ = coerce_floors(_param_value(parameters, "buildings.unit_count"), 1.0)
    if unit_target and units_estimate is not None:
        report.add(ScoreItem(
            key="yield_vs_target", score=min(units_estimate / unit_target, 1.0),
            measured=round(units_estimate), target=unit_target,
            detail=f"drawn plan yields ~{units_estimate:,.0f} units vs {unit_target:,.0f} target",
        ))

    # 8. Ceiling conformance: clamps guarantee it; unknown ceilings are disclosed.
    clamped = sum(1 for n in result.notes if n.get("code") == "FLOORS_CLAMPED")
    report.add(ScoreItem(
        key="ceiling_conformance", score=1.0,
        detail="storeys clamped to district ceilings during massing"
               + (f" ({clamped} clamp note{'s' if clamped != 1 else ''})" if clamped else
                  "; districts without numeric ceilings are disclosed in the metrics reconciliation"),
    ))

    return report.finalize()


# --- Deterministic revision rules ------------------------------------------------

REVISION_FLOOR_STEP = 1.0
MAX_FLOORS_BUMP = 3.0


def revise_rules(
    evaluation: EvaluationReport,
    current_overrides: dict[str, float],
    base_rules: dict[str, Any],
    locks: list[str],
) -> tuple[dict[str, float], list[dict[str, Any]]]:
    """Findings -> bounded rule revisions. Returns (new_overrides, revision records).

    Each rule fires at most once per iteration; an empty revision list means the
    loop has converged (nothing applicable left to try).
    """
    overrides = dict(current_overrides)
    revisions: list[dict[str, Any]] = []

    def record(parameter: str, old: float, new: float, reason: str) -> None:
        overrides[parameter] = new
        revisions.append({"parameter": parameter, "from": old, "to": round(new, 2), "reason": reason})

    scores = evaluation.scores

    yield_score = scores.get("yield_vs_target")
    if yield_score and yield_score.score < 0.9:
        # base_rules reflects the CURRENT iteration (overrides already applied),
        # so "how far have we bumped" must be tracked explicitly — comparing
        # against base_rules always reads zero and the cap never binds.
        bumps = int(overrides.get("_floors_bumps", 0))
        if bumps < MAX_FLOORS_BUMP:
            base_floors = float(overrides.get("floors", base_rules.get("floors", 4.0)))
            record("floors", base_floors, base_floors + REVISION_FLOOR_STEP,
                   f"yield_vs_target {yield_score.score:.2f}: add a storey toward the unit target "
                   "(district ceilings still clamp per block)")
            overrides["_floors_bumps"] = bumps + 1

    open_score = scores.get("open_space")
    if open_score and open_score.score < 0.85:
        base_share = float(overrides.get("open_space_share", base_rules.get("open_space_share", 0.1)))
        record("open_space_share", base_share, min(base_share + 0.03, 0.30),
               f"open_space {open_score.score:.2f}: raise the open-space share so a whole block qualifies")

    park_score = scores.get("park_access")
    if park_score and park_score.score < 0.7 and "open_space_share" not in overrides:
        base_share = float(base_rules.get("open_space_share", 0.1))
        record("open_space_share", base_share, min(base_share + 0.04, 0.30),
               f"park_access {park_score.score:.2f}: more open space to bring masses within 400 m")

    if "streets" not in locks:
        density_score = scores.get("intersection_density")
        block_score = scores.get("block_scale")
        needs_finer_grid = (density_score and density_score.score < 0.5) or (block_score and block_score.score < 0.7)
        if needs_finer_grid:
            base_block = float(overrides.get("block_target_m", base_rules.get("block_target_m", 100.0)))
            # Floor at 70 m: below inner-city block grain the added ROW/lane
            # land costs more than the finer blocks return (non-linear optimum).
            if base_block > 70.0:
                reason_key = "intersection_density" if (density_score and density_score.score < 0.5) else "block_scale"
                record("block_target_m", base_block, max(base_block - 25.0, 70.0),
                       f"{reason_key} {scores[reason_key].score:.2f}: tighten the grid for walkability")

    # Drop revisions that didn't change anything (already at bounds).
    revisions = [r for r in revisions if abs(r["to"] - r["from"]) > 1e-9]
    return overrides, revisions
