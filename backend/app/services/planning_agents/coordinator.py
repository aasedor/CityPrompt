"""Coordinator — deterministic merge of expert recommendations into PlanParameters.

The merge is CODE, not an LLM: group by parameter_path, weight each position by
confidence x philosophy affinity, adopt within tolerance, and surface genuine
disagreements as EXPERT_TRADEOFF ValidationNotes that carry BOTH positions and
which philosophy weight decided — conflicts are never silently averaged.

One optional Claude call writes the scenario narrative — but it narrates a diff
computed in Python, so it cannot claim differences that don't exist; on any
failure a deterministic fallback narrative is used.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import anthropic
from celery.exceptions import SoftTimeLimitExceeded

from app.core.config import get_settings
from app.core.usage_logger import log_api_usage_sync
from app.services.planning_agents.registry import get_expert
from app.services.planning_agents.schemas import (
    PARAMETER_VOCABULARY,
    ChangedParameter,
    ExpertRecommendationSet,
    MergedParameter,
    PhilosophyWeights,
    Recommendation,
    ScenarioDefinition,
    ScenarioExplanation,
)
from app.services.urban_dna.schema import ValidationNote

logger = logging.getLogger(__name__)

NUMERIC_TOLERANCE = 0.15  # positions within ±15% are agreement, not conflict


def _affinity(agent_id: str, philosophy: PhilosophyWeights) -> float:
    spec = get_expert(agent_id)
    if spec is None:
        return 1.0
    affinity = spec.philosophy_affinity.get(philosophy.primary, 1.0)
    if philosophy.secondary:
        affinity = max(affinity, 0.5 + 0.5 * spec.philosophy_affinity.get(philosophy.secondary, 1.0))
    return affinity


def _weight(recommendation: Recommendation, agent_id: str, philosophy: PhilosophyWeights) -> float:
    return recommendation.confidence * (
        1.0 + philosophy.intensity * (_affinity(agent_id, philosophy) - 1.0) + philosophy.intensity
    )


def _is_numeric(path: str, value: Any) -> bool:
    kind = PARAMETER_VOCABULARY.get(path, {}).get("kind")
    return kind == "number" and isinstance(value, (int, float))


def merge_recommendations(
    expert_sets: list[ExpertRecommendationSet],
    philosophy: PhilosophyWeights,
) -> tuple[dict[str, MergedParameter], list[ValidationNote]]:
    """Deterministic merge. Returns (plan parameters, trade-off notes)."""
    positions: dict[str, list[tuple[str, Recommendation, float]]] = {}
    for expert_set in expert_sets:
        if expert_set.failed:
            continue
        for recommendation in expert_set.recommendations:
            weight = _weight(recommendation, expert_set.agent_id, philosophy)
            positions.setdefault(recommendation.parameter_path, []).append(
                (expert_set.agent_id, recommendation, weight)
            )

    merged: dict[str, MergedParameter] = {}
    trade_offs: list[ValidationNote] = []

    for path in sorted(positions):
        candidates = sorted(positions[path], key=lambda item: item[2], reverse=True)
        candidate_dump = [
            {
                "agent_id": agent_id,
                "value": rec.value,
                "rationale": rec.rationale,
                "confidence": rec.confidence,
                "weight": round(weight, 3),
                "principle_ids": list(rec.principle_ids),
            }
            for agent_id, rec, weight in candidates
        ]
        winner_agent, winner_rec, winner_weight = candidates[0]

        contested = False
        if len(candidates) > 1:
            if _is_numeric(path, winner_rec.value):
                numeric = [(a, r, w) for a, r, w in candidates if isinstance(r.value, (int, float))]
                values = [float(r.value) for _, r, _ in numeric]
                spread_ok = max(values) <= min(values) * (1 + NUMERIC_TOLERANCE) if min(values) > 0 else False
                total_weight = sum(w for _, _, w in numeric)
                if spread_ok and numeric and total_weight > 0:
                    # agreement: weighted mean, all contributors join
                    blended = sum(float(r.value) * w for _, r, w in numeric) / total_weight
                    vocab_unit = PARAMETER_VOCABULARY.get(path, {}).get("unit")
                    value = round(blended) if vocab_unit in ("storeys", "dwellings") else round(blended, 1)
                    merged[path] = MergedParameter(
                        parameter_path=path,
                        value=value,
                        rationale=winner_rec.rationale,
                        contributors=[a for a, _, _ in numeric],
                        candidates=candidate_dump,
                        # Agreement means every contributor's doctrine applies.
                        principle_ids=sorted({pid for _, r, _ in numeric for pid in r.principle_ids}),
                    )
                    continue
                # Zero-weight agreement (all confidences 0) is NOT a conflict —
                # only a genuine numeric spread earns a trade-off note.
                contested = not spread_ok
            else:
                distinct = {str(r.value).strip().lower() for _, r, _ in candidates}
                contested = len(distinct) > 1

        tension_flagged = any(
            path in r.tension_with for sets in expert_sets if not sets.failed for r in sets.recommendations
        ) or any(other in winner_rec.tension_with for other in positions)

        if contested or (tension_flagged and len(candidates) > 1):
            runner_agent, runner_rec, runner_weight = candidates[1]
            trade_offs.append(
                ValidationNote(
                    code=f"EXPERT_TRADEOFF:{path}",
                    severity="warning",
                    message=(
                        f"{winner_agent} recommends {winner_rec.value!r} ({winner_rec.rationale[:140]}) while "
                        f"{runner_agent} recommends {runner_rec.value!r} ({runner_rec.rationale[:140]}). "
                        f"Adopted {winner_rec.value!r} under {philosophy.primary} weighting "
                        f"(weight {winner_weight:.2f} vs {runner_weight:.2f}); the alternative remains a "
                        "legitimate position for deliberation."
                    ),
                    source_phase="coordinator",
                )
            )

        merged[path] = MergedParameter(
            parameter_path=path,
            value=winner_rec.value,
            rationale=winner_rec.rationale,
            contributors=[winner_agent],
            contested=contested,
            candidates=candidate_dump,
            principle_ids=list(winner_rec.principle_ids),
        )

    return merged, trade_offs


def diff_scenarios(
    baseline: dict[str, MergedParameter] | None,
    current: dict[str, MergedParameter],
) -> list[ChangedParameter]:
    """Python-computed diff — the narrative can only reference what's here."""
    changed: list[ChangedParameter] = []
    baseline = baseline or {}
    for path in sorted(set(baseline) | set(current)):
        base_param = baseline.get(path)
        curr_param = current.get(path)
        base_value = base_param.value if base_param else None
        curr_value = curr_param.value if curr_param else None
        if base_value == curr_value:
            continue
        changed.append(
            ChangedParameter(
                parameter_path=path,
                baseline_value=base_value,
                value=curr_value,
                driven_by=", ".join(curr_param.contributors) if curr_param else "removed",
            )
        )
    return changed


_NARRATIVE_TOOL = {
    "name": "record_narrative",
    "description": "Record the scenario narrative.",
    "input_schema": {
        "type": "object",
        "properties": {"narrative": {"type": "string", "description": "<=120 words"}},
        "required": ["narrative"],
    },
}


def _fallback_narrative(scenario: ScenarioDefinition, changed: list[ChangedParameter]) -> str:
    if not changed:
        return f"{scenario.label} matches the baseline parameters."
    fragments = [
        f"{c.parameter_path.split('.')[-1].replace('_', ' ')} {c.baseline_value} → {c.value}" for c in changed[:4]
    ]
    return f"{scenario.label} differs from the baseline in: " + "; ".join(fragments) + "."


async def write_explanation(
    scenario: ScenarioDefinition,
    changed: list[ChangedParameter],
    trade_offs: list[ValidationNote],
    baseline_id: str = "as_of_right",
) -> ScenarioExplanation:
    """Narrate the computed diff. Degrades to a deterministic narrative."""
    explanation = ScenarioExplanation(baseline=baseline_id, changed_parameters=changed)
    if not changed:
        explanation.narrative = _fallback_narrative(scenario, changed)
        return explanation

    settings = get_settings()
    client = None
    try:
        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        message = await client.messages.create(
            model=settings.urban_dna_agent_model,
            max_tokens=1500,
            system=(
                "You write a WHY-it-differs narrative for a planning scenario. You are given the "
                "scenario's philosophy and a computed list of parameter changes vs the baseline. "
                "Reference ONLY those changes (at least two of them). <=120 words, plain language, "
                "trade-off framing, no verdict language. Record it with the record_narrative tool."
            ),
            messages=[
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "scenario": scenario.label,
                            "philosophy": scenario.philosophy.model_dump(),
                            "changed_parameters": [c.model_dump() for c in changed],
                            "trade_offs": [t.message for t in trade_offs[:4]],
                        },
                        default=str,
                    ),
                }
            ],
            tools=[_NARRATIVE_TOOL],
            tool_choice={"type": "tool", "name": "record_narrative"},
        )
        try:
            log_api_usage_sync(
                provider="anthropic",
                operation="planning_agent.narrative",
                input_tokens=message.usage.input_tokens,
                output_tokens=message.usage.output_tokens,
                metadata={"scenario": scenario.scenario_id},
            )
        except SoftTimeLimitExceeded:
            raise  # sync DB frame — must reach the task handler, not the fallback narrative
        except Exception:  # noqa: BLE001
            pass
        payload = next(
            (block.input for block in message.content if getattr(block, "type", None) == "tool_use"),
            None,
        )
        narrative = (payload or {}).get("narrative", "").strip()
        explanation.narrative = narrative or _fallback_narrative(scenario, changed)
    except SoftTimeLimitExceeded:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.warning("Narrative generation failed: %s", exc)
        explanation.narrative = _fallback_narrative(scenario, changed)
    finally:
        # Close inside the running loop (asyncio.run in the Celery task) —
        # a GC-time close after the loop ends emits "Event loop is closed".
        if client is not None:
            try:
                await client.close()
            except Exception:  # noqa: BLE001
                pass
    return explanation
