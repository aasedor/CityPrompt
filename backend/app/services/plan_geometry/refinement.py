"""The generate → evaluate → refine loop, as a pure service (Celery-free).

Bounded at MAX_ITERATIONS; every iteration records its scores, the overrides in
effect, and the revisions (with reasons) that produced the next attempt. The
final drawn geometry + geometry-mode metrics are returned together so callers
persist one consistent plan.
"""

from __future__ import annotations

import logging
from typing import Any

from shapely.geometry import Polygon

from app.services.plan_geometry.generator import PlanGeometryResult, generate_plan_geometry
from app.services.plan_geometry.plan_evaluator import (
    GOOD_ENOUGH_OVERALL,
    evaluate_plan,
    revise_rules,
)
from app.services.plan_metrics import MetricsReport, compute_metrics

logger = logging.getLogger(__name__)

MAX_ITERATIONS = 3


def run_refinement_loop(
    *,
    site_polygon_wgs84: Polygon,
    scenario_id: str,
    scenario_label: str,
    parameters: dict[str, Any],
    dna: dict[str, Any],
    road_features: list[dict[str, Any]] | None = None,
    district_features: list[dict[str, Any]] | None = None,
    locked_street_area_wgs84: Polygon | None = None,
    rule_hints: dict[str, float] | None = None,
    locks: list[str] | None = None,
    palette_hint: str | None = None,
) -> tuple[PlanGeometryResult, MetricsReport, list[dict[str, Any]]]:
    locks = locks or []
    overrides: dict[str, float] = {}
    iterations: list[dict[str, Any]] = []
    result: PlanGeometryResult | None = None
    metrics_report: MetricsReport | None = None

    for iteration in range(MAX_ITERATIONS):
        result = generate_plan_geometry(
            site_polygon_wgs84=site_polygon_wgs84,
            scenario_id=scenario_id,
            scenario_label=scenario_label,
            parameters=parameters,
            road_features=road_features,
            district_features=district_features,
            locked_street_area_wgs84=locked_street_area_wgs84,
            rule_overrides=overrides or None,
            rule_hints=rule_hints,
            dna=dna,
            palette_hint=palette_hint,
        )
        metrics_report = compute_metrics(
            scenario_id=scenario_id,
            dna=dna,
            parameters=parameters,
            geometry_inputs=result.geometry_inputs,
            # Reconcile what was actually drawn (incl. refinement floor bumps),
            # not the raw parameter the experts first asked for.
            effective_floors=float(result.rules.get("floors") or 0) or None,
        )
        units_metric = metrics_report.metrics.get("units")
        evaluation = evaluate_plan(
            result, parameters,
            units_estimate=units_metric.value if units_metric else None,
        )

        new_overrides, revisions = revise_rules(evaluation, overrides, result.rules, locks)
        iterations.append({
            "iteration": iteration + 1,
            "overall_score": evaluation.overall,
            "scores": {k: s.model_dump() for k, s in evaluation.scores.items()},
            "overrides_in_effect": dict(overrides),
            "revisions": revisions,
            "block_count": result.block_count,
            "building_count": result.building_count,
        })
        logger.info(
            "Plan %s iteration %d: score %.3f, %d revision(s)",
            scenario_id, iteration + 1, evaluation.overall, len(revisions),
        )
        # Converged = good overall AND no single dimension badly failed — a
        # weighted average (fire safety counts double) can otherwise mask one
        # dimension scoring near zero.
        min_score = min((s.score for s in evaluation.scores.values()), default=1.0)
        if (evaluation.overall >= GOOD_ENOUGH_OVERALL and min_score >= 0.5) or not revisions:
            break
        overrides = new_overrides

    assert result is not None and metrics_report is not None  # loop runs at least once
    return result, metrics_report, iterations
