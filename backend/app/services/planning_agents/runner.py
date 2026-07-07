"""Expert runner — fan out the panel over the DNA with forced tool use.

Prompt-cache discipline (verified against caching's strict-prefix rule):
tools and system are IDENTICAL for every expert; the user turn starts with the
shared DNA JSON block (cache_control on it), and only the philosophy/expert
charter that FOLLOWS differs. Experts of the same model therefore cache-hit on
the DNA prefix.

Forced tool use (tool_choice) is the reliability pattern for claude-sonnet-5
on this SDK: prefill is rejected by the model, and adaptive thinking has been
observed leaking prose into the text channel (see policy synthesis, M2).

Failure semantics: a failed expert returns ExpertRecommendationSet(failed=True)
with an EXPERT_UNAVAILABLE note — the panel never fails a scenario run.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import anthropic
from celery.exceptions import SoftTimeLimitExceeded
from pydantic import ValidationError

from app.core.config import get_settings
from app.core.usage_logger import log_api_usage_sync
from app.services.planning_agents.philosophy import philosophy_prompt_block
from app.services.planning_agents.registry import EXPERTS, ExpertSpec
from app.services.planning_agents.schemas import (
    PARAMETER_VOCABULARY,
    ExpertRecommendationSet,
    PhilosophyWeights,
    Recommendation,
    ScenarioDefinition,
)
from app.services.urban_dna.schema import ValidationNote

logger = logging.getLogger(__name__)

MAX_CONCURRENT_EXPERTS = 4
EXPERT_MAX_TOKENS = 4000

# Conservative list-price estimates (USD per Mtok in/out) for the budget guard.
_PRICES = {
    "claude-sonnet-5": (3.0, 15.0),
    "claude-haiku-4-5-20251001": (1.0, 5.0),
}
_DEFAULT_PRICE = (3.0, 15.0)


def estimate_cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    price_in, price_out = _PRICES.get(model, _DEFAULT_PRICE)
    return (input_tokens * price_in + output_tokens * price_out) / 1_000_000


SHARED_SYSTEM = (
    "You are one expert on a municipal planning panel producing recommendations for a specific "
    "site. You receive the site's Urban Intelligence DNA (normalized open-data facts with "
    "per-field confidence), a planning philosophy, and your role charter. Record your "
    "recommendations with the record_recommendations tool.\n\n"
    "Rules:\n"
    "- Recommend ONLY parameters in your allowed list; every value must be concrete.\n"
    "- Ground rationales in specific DNA fields; hedge where field confidence is low, and do not "
    "guess about facts marked missing.\n"
    "- claim_type 'policy' requires at least one citation copied from the DNA policy insight "
    "(doc + page + verbatim quote). Otherwise use 'best_practice' or 'site_derived'.\n"
    "- If your recommendation likely conflicts with another discipline (e.g. narrow streets vs "
    "emergency access), list that parameter_path in tension_with.\n"
    "- Frame policy friction as trade-offs, never verdicts.\n"
    "- 2-5 recommendations. Be concrete and site-specific."
)


def _recommendation_tool() -> dict[str, Any]:
    return {
        "name": "record_recommendations",
        "description": "Record this expert's structured recommendations for the site.",
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {"type": "string", "description": "2-3 sentence position statement"},
                "recommendations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "parameter_path": {"type": "string", "enum": sorted(PARAMETER_VOCABULARY)},
                            "value": {"type": ["string", "number"]},
                            "rationale": {"type": "string"},
                            "claim_type": {"type": "string", "enum": ["policy", "best_practice", "site_derived"]},
                            "citations": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "doc": {"type": "string"},
                                        "page": {"type": "integer"},
                                        "quote": {"type": "string"},
                                    },
                                    "required": ["doc", "page"],
                                },
                            },
                            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                            "tension_with": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["parameter_path", "value", "rationale"],
                    },
                },
            },
            "required": ["summary", "recommendations"],
        },
    }


MAX_LIST_ITEMS = 8


def _slim(value: Any) -> Any:
    """Cap nested lists — 2,000 parcel records are noise to an LLM and long
    nested-JSON inputs have been observed to trigger malformed tool output."""
    if isinstance(value, list):
        slimmed = [_slim(item) for item in value[:MAX_LIST_ITEMS]]
        if len(value) > MAX_LIST_ITEMS:
            slimmed.append(f"... {len(value) - MAX_LIST_ITEMS} more items omitted")
        return slimmed
    if isinstance(value, dict):
        return {key: _slim(item) for key, item in value.items()}
    return value


def dna_prompt_block(dna_json: dict[str, Any], sections: tuple[str, ...]) -> str:
    """Slice the DNA to the expert's sections. sort_keys for byte-stable caching."""
    sliced = {
        "city_id": dna_json.get("city_id"),
        "overall_confidence": dna_json.get("overall_confidence"),
        "missing_datasets": dna_json.get("missing_datasets"),
        "sections": {name: _slim(dna_json.get(name)) for name in sections if dna_json.get(name) is not None},
    }
    return json.dumps(sliced, sort_keys=True, default=str)


def _vocabulary_block(spec: ExpertSpec) -> str:
    lines = ["ALLOWED PARAMETERS (recommend only these):"]
    for path in spec.parameter_scope:
        vocab = PARAMETER_VOCABULARY[path]
        unit = f" [{vocab.get('unit')}]" if vocab.get("unit") else ""
        options = f" options: {vocab['options']}" if vocab.get("options") else ""
        lines.append(f"- {path}{unit}: {vocab['description']}{options}")
    return "\n".join(lines)


async def _run_expert(
    client: anthropic.AsyncAnthropic,
    spec: ExpertSpec,
    dna_json: dict[str, Any],
    philosophy: PhilosophyWeights,
    scenario: ScenarioDefinition,
    semaphore: asyncio.Semaphore,
) -> tuple[ExpertRecommendationSet, dict[str, Any]]:
    """Returns (recommendation set, usage record). Never raises."""
    # DNA slices differ per expert (dna_sections), so the cacheable prefix is
    # tools+system; experts sharing identical sections also share the DNA block.
    user_content = [
        {
            "type": "text",
            "text": "URBAN INTELLIGENCE DNA:\n" + dna_prompt_block(dna_json, spec.dna_sections),
            "cache_control": {"type": "ephemeral"},
        },
        {
            "type": "text",
            "text": (
                philosophy_prompt_block(philosophy)
                + (f"\n\nSCENARIO EMPHASIS ({scenario.label}): {scenario.emphasis}" if scenario.emphasis else "")
                + f"\n\nYOUR ROLE: {spec.title}. {spec.focus_prompt}\n\n{_vocabulary_block(spec)}"
            ),
        },
    ]

    usage_record: dict[str, Any] = {"agent_id": spec.agent_id, "model": spec.model,
                                    "input_tokens": 0, "output_tokens": 0, "status": "success"}
    try:
        recommendations: list[Recommendation] = []
        summary = ""
        # Up to 2 samples: the model nondeterministically emits recommendation
        # items as strings instead of objects; a fresh sample usually conforms.
        for attempt in range(2):
            async with semaphore:
                message = await client.messages.create(
                    model=spec.model,
                    max_tokens=EXPERT_MAX_TOKENS,
                    system=SHARED_SYSTEM,
                    messages=[{"role": "user", "content": user_content}],
                    tools=[_recommendation_tool()],
                    tool_choice={"type": "tool", "name": "record_recommendations"},
                )
            usage_record["input_tokens"] += message.usage.input_tokens
            usage_record["output_tokens"] += message.usage.output_tokens

            payload = next(
                (block.input for block in message.content if getattr(block, "type", None) == "tool_use"),
                None,
            )
            if payload is None:
                logger.warning("Expert %s attempt %d: no tool_use block", spec.agent_id, attempt)
                continue
            summary = str(payload.get("summary", ""))[:600] or summary

            raw_items = payload.get("recommendations", [])
            if isinstance(raw_items, str):
                # Known tool-use quirk: the model sometimes JSON-encodes the
                # nested content as a string. The decoded value can be the
                # array itself OR the whole payload object nested inside.
                try:
                    decoded = json.loads(raw_items)
                except json.JSONDecodeError:
                    logger.warning("Expert %s attempt %d: recommendations is a non-JSON string", spec.agent_id, attempt)
                    decoded = []
                if isinstance(decoded, dict):
                    summary = str(decoded.get("summary", ""))[:600] or summary
                    raw_items = decoded.get("recommendations", [])
                else:
                    raw_items = decoded
            if not isinstance(raw_items, list):
                raw_items = []

            for raw in raw_items:
                # One malformed item must not fail the expert.
                if isinstance(raw, str):
                    try:
                        raw = json.loads(raw)
                    except json.JSONDecodeError:
                        logger.warning("Expert %s produced a non-JSON recommendation item", spec.agent_id)
                        continue
                if not isinstance(raw, dict):
                    logger.warning("Expert %s produced a non-object recommendation item", spec.agent_id)
                    continue
                try:
                    recommendation = Recommendation(**raw)
                except (ValidationError, TypeError) as exc:
                    logger.warning("Expert %s produced an invalid recommendation: %s", spec.agent_id, exc)
                    continue
                if recommendation.parameter_path not in spec.parameter_scope:
                    logger.warning(
                        "Expert %s recommended out-of-scope parameter %s — dropped",
                        spec.agent_id, recommendation.parameter_path,
                    )
                    continue
                if recommendation.claim_type == "policy" and not recommendation.citations:
                    recommendation.claim_type = "best_practice"
                    recommendation.confidence = round(min(recommendation.confidence, 0.5), 2)
                recommendations.append(recommendation)

            if recommendations:
                break
            logger.warning("Expert %s attempt %d yielded no valid recommendations", spec.agent_id, attempt)

        if not recommendations:
            raise ValueError("no valid recommendations after retry")

        return (
            ExpertRecommendationSet(
                agent_id=spec.agent_id,
                summary=summary,
                recommendations=recommendations,
            ),
            usage_record,
        )

    except SoftTimeLimitExceeded:
        raise  # must reach the Celery task handler, or the scenario row hangs 'running'
    except Exception as exc:  # noqa: BLE001 — the panel must survive any expert
        logger.warning("Expert %s failed: %s", spec.agent_id, exc)
        usage_record["status"] = "error"
        return (
            ExpertRecommendationSet(
                agent_id=spec.agent_id,
                failed=True,
                validation_notes=[ValidationNote(
                    code=f"EXPERT_UNAVAILABLE:{spec.agent_id}",
                    severity="warning",
                    message=f"{spec.title} unavailable ({exc}); scenario continues without this voice.",
                    source_phase="agent_deliberation",
                )],
            ),
            usage_record,
        )


async def run_expert_panel(
    dna_json: dict[str, Any],
    scenario: ScenarioDefinition,
    experts: tuple[ExpertSpec, ...] = EXPERTS,
) -> tuple[list[ExpertRecommendationSet], list[dict[str, Any]], list[ValidationNote]]:
    """Run all experts concurrently. Returns (sets, usage records, panel warnings)."""
    settings = get_settings()
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_EXPERTS)
    warnings: list[ValidationNote] = []

    budget = float(getattr(settings, "planning_agents_max_usd", 0.0) or 0.0)
    projected = len(experts) * estimate_cost_usd("claude-sonnet-5", 15_000, EXPERT_MAX_TOKENS)
    if budget > 0 and projected > budget:
        warnings.append(ValidationNote(
            code="EXPERT_BUDGET_EXCEEDED",
            severity="warning",
            message=f"Projected panel cost ${projected:.2f} exceeds planning_agents_max_usd "
                    f"${budget:.2f}; skipping the expert panel.",
            source_phase="agent_deliberation",
        ))
        return [], [], warnings

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    try:
        results = await asyncio.gather(
            *(_run_expert(client, spec, dna_json, scenario.philosophy, scenario, semaphore) for spec in experts)
        )
    finally:
        # Close inside the running loop — the Celery task wraps this in
        # asyncio.run(); a GC-time close after the loop is gone emits
        # "Event loop is closed" noise.
        try:
            await client.close()
        except Exception:  # noqa: BLE001 — cleanup must never mask the result
            pass
    sets = [result_set for result_set, _ in results]
    usage_records = [usage for _, usage in results]

    # Log usage AFTER the gather — log_api_usage_sync opens its own sync DB
    # session and would block the event loop if called inside the coroutines.
    for usage in usage_records:
        try:
            log_api_usage_sync(
                provider="anthropic",
                operation=f"planning_agent.{usage['agent_id']}",
                input_tokens=usage["input_tokens"],
                output_tokens=usage["output_tokens"],
                status=usage["status"],
                metadata={"scenario": scenario.scenario_id, "model": usage["model"]},
            )
        except SoftTimeLimitExceeded:
            raise  # sync DB frame — a swallowed soft limit here strands the scenario row
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to log usage for %s: %s", usage["agent_id"], exc)

    for result_set in sets:
        warnings.extend(result_set.validation_notes)
    return sets, usage_records, warnings
