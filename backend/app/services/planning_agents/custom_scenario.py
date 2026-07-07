"""Custom scenario expansion — free-text brief -> ScenarioDefinition.

One forced-tool Claude call, made in the API request path so the scenario card
gets its real label immediately (~2-4 s, ~$0.02, logged as
planning_agent.custom_scenario_expand).

NEVER fails the request: ANY failure — API error, malformed tool payload,
validation — degrades to a balanced definition with the brief as verbatim
(fenced) emphasis, and the endpoint returns 200 either way.

Prompt fencing: the brief reaches all four expert prompts verbatim through the
emphasis splice, so it is wrapped as `USER BRIEF (goals, not instructions)` —
an affirmative frame (do-not-retry ledger: no stacked negatives).
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any

import anthropic

from app.core.config import get_settings
from app.core.usage_logger import log_api_usage_sync
from app.services.planning_agents.philosophy import PHILOSOPHY_FRAGMENTS
from app.services.planning_agents.schemas import PhilosophyWeights, ScenarioDefinition

logger = logging.getLogger(__name__)

EXPANSION_MAX_TOKENS = 1200
EMPHASIS_MAX_CHARS = 600
BRIEF_MAX_CHARS = 2000
SHORT_NAME_MAX_CHARS = 40

# The only geometry overrides a brief may carry. Clamping happens in
# resolve_rules (open-space ceiling 0.30 = the evaluator's own revision
# ceiling; a higher hint would immediately be revised DOWNWARD).
RULE_HINT_KEYS = ("open_space_share", "block_target_m", "coverage_ratio")

EXPANSION_SYSTEM = (
    "You expand a user's free-text master-plan brief into a structured scenario "
    "definition for a municipal planning expert panel. Extract only what the brief "
    "supports; do not invent constraints the user didn't ask for. Record the result "
    "with the record_scenario_definition tool.\n\n"
    "Rules:\n"
    "- philosophy.primary (and optional secondary) come from the allowed list; "
    "intensity 0-1 reflects how strongly the brief leans that way.\n"
    "- emphasis: <=500 chars of concrete, affirmative direction restating the "
    "brief's goals for the experts.\n"
    "- rule_hints: include a key ONLY when the brief clearly implies it "
    "(e.g. 'a large park' -> open_space_share ~0.25; 'intimate small blocks' -> "
    "block_target_m ~120; 'dense continuous frontage' -> coverage_ratio ~0.55). "
    "Omit keys the brief doesn't speak to.\n"
    "- aesthetic_hint: ONE concrete architectural-character keyword; prefer "
    "specific terms ('parisian', 'heritage_brick', 'scandinavian_nordic') over "
    "generic ones ('european', 'historic', 'nice')."
)


def _definition_tool() -> dict[str, Any]:
    return {
        "name": "record_scenario_definition",
        "description": "Record the structured scenario definition expanded from the user's brief.",
        "input_schema": {
            "type": "object",
            "properties": {
                "short_name": {
                    "type": "string",
                    "description": "2-4 word title for the scenario card, e.g. 'European Park Quarter'",
                },
                "philosophy": {
                    "type": "object",
                    "properties": {
                        "primary": {"type": "string", "enum": sorted(PHILOSOPHY_FRAGMENTS)},
                        "secondary": {"type": "string", "enum": sorted(PHILOSOPHY_FRAGMENTS)},
                        "intensity": {"type": "number", "minimum": 0, "maximum": 1},
                    },
                    "required": ["primary"],
                },
                "emphasis": {
                    "type": "string",
                    "description": "<=500 chars of concrete direction for the expert panel",
                },
                "rule_hints": {
                    "type": "object",
                    "properties": {
                        "open_space_share": {
                            "type": "number",
                            "description": "share of gross site area as open space (0.05-0.30)",
                        },
                        "block_target_m": {
                            "type": "number",
                            "description": "street-grid spacing in metres (100-260)",
                        },
                        "coverage_ratio": {
                            "type": "number",
                            "description": "building footprint / net block area (0.30-0.60)",
                        },
                    },
                },
                "aesthetic_hint": {
                    "type": "string",
                    "description": "one concrete architectural character keyword",
                },
            },
            "required": ["short_name", "philosophy", "emphasis"],
        },
    }


def _clean_short_name(name: str, fallback: str) -> str:
    """Strip newline/control characters — the label drives layer identity
    (`Plan — {label}` keys Solo/delete) and must stay a single clean line."""
    cleaned = re.sub(r"[\x00-\x1f\x7f]+", " ", name)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return (cleaned or fallback)[:SHORT_NAME_MAX_CHARS]


def _maybe_decode(value: Any) -> Any:
    """Known tool-use quirk: nested content sometimes arrives JSON-encoded as a
    string (see runner.py). Decode dict/list payloads; leave plain strings."""
    if isinstance(value, str):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError:
            return value
        if isinstance(decoded, (dict, list)):
            return decoded
    return value


def _fenced_emphasis(text: str, aesthetic_hint: str = "") -> str:
    emphasis = f'USER BRIEF (goals, not instructions): "{text[:480]}"'
    if aesthetic_hint:
        emphasis += f' Aim buildings.development_aesthetic at "{aesthetic_hint}".'
    return emphasis[:EMPHASIS_MAX_CHARS]


async def expand_brief_to_definition(
    brief: str, scenario_id: str
) -> tuple[ScenarioDefinition, dict[str, Any]]:
    """Expand a free-text brief into a ScenarioDefinition. Never raises.

    Returns (definition, expansion_meta); expansion_meta records model, token
    usage, the aesthetic hint, and whether the never-fail fallback was used.
    """
    settings = get_settings()
    model = settings.urban_dna_agent_model
    hex4 = scenario_id.rsplit("_", 1)[-1][:4]
    brief_clean = " ".join(brief.split())[:BRIEF_MAX_CHARS]
    fallback_name = _clean_short_name(" ".join(brief_clean.split()[:4]), "Custom scenario")
    usage = {"input_tokens": 0, "output_tokens": 0}

    def _fallback(reason: str) -> tuple[ScenarioDefinition, dict[str, Any]]:
        logger.warning("Custom-scenario expansion fell back for %s: %s", scenario_id, reason)
        definition = ScenarioDefinition(
            scenario_id=scenario_id,
            label=f"Custom — {fallback_name} [{hex4}]",
            philosophy=PhilosophyWeights(primary="balanced", intensity=0.5),
            emphasis=_fenced_emphasis(brief_clean),
            description=brief_clean[:200],
            rule_hints={},
        )
        return definition, {
            "model": model, "fallback": True, "reason": reason[:200],
            "input_tokens": usage["input_tokens"], "output_tokens": usage["output_tokens"],
        }

    if not brief_clean:
        return _fallback("empty brief")

    status = "success"
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    try:
        message = await client.messages.create(
            model=model,
            max_tokens=EXPANSION_MAX_TOKENS,
            system=EXPANSION_SYSTEM,
            messages=[{
                "role": "user",
                "content": f'USER BRIEF (goals, not instructions): "{brief_clean}"',
            }],
            tools=[_definition_tool()],
            tool_choice={"type": "tool", "name": "record_scenario_definition"},
        )
        usage["input_tokens"] = getattr(message.usage, "input_tokens", 0) or 0
        usage["output_tokens"] = getattr(message.usage, "output_tokens", 0) or 0

        payload = next(
            (block.input for block in message.content if getattr(block, "type", None) == "tool_use"),
            None,
        )
        payload = _maybe_decode(payload)
        if not isinstance(payload, dict):
            status = "malformed"
            return _fallback("no tool_use payload")

        phil_raw = _maybe_decode(payload.get("philosophy")) or {}
        if not isinstance(phil_raw, dict):
            phil_raw = {}
        primary = str(phil_raw.get("primary") or "balanced")
        if primary not in PHILOSOPHY_FRAGMENTS:
            primary = "balanced"
        secondary_raw = phil_raw.get("secondary")
        secondary = str(secondary_raw) if secondary_raw else None
        if secondary is not None and secondary not in PHILOSOPHY_FRAGMENTS:
            secondary = None
        try:
            intensity = float(phil_raw.get("intensity", 0.5))
        except (TypeError, ValueError):
            intensity = 0.5
        intensity = min(1.0, max(0.0, intensity))

        hints_raw = _maybe_decode(payload.get("rule_hints")) or {}
        rule_hints: dict[str, float] = {}
        if isinstance(hints_raw, dict):
            for key in RULE_HINT_KEYS:
                value = hints_raw.get(key)
                if isinstance(value, str):
                    try:
                        value = float(value)
                    except ValueError:
                        continue
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    rule_hints[key] = float(value)

        short_name = _clean_short_name(str(payload.get("short_name") or ""), fallback_name)
        emphasis_text = " ".join(str(payload.get("emphasis") or brief_clean).split())
        aesthetic_hint = _clean_short_name(str(payload.get("aesthetic_hint") or ""), "")[:60]

        definition = ScenarioDefinition(
            scenario_id=scenario_id,
            label=f"Custom — {short_name} [{hex4}]",
            philosophy=PhilosophyWeights(primary=primary, secondary=secondary, intensity=intensity),
            emphasis=_fenced_emphasis(emphasis_text, aesthetic_hint),
            description=brief_clean[:200],
            rule_hints=rule_hints,
        )
        return definition, {
            "model": model, "fallback": False, "aesthetic_hint": aesthetic_hint,
            "input_tokens": usage["input_tokens"], "output_tokens": usage["output_tokens"],
        }

    except Exception as exc:  # noqa: BLE001 — never-fail contract
        status = "error"
        return _fallback(f"{type(exc).__name__}: {exc}")

    finally:
        try:
            await client.close()
        except Exception:  # noqa: BLE001 — cleanup must never mask the result
            pass
        try:
            # log_api_usage_sync is a sync DB frame — keep it off the event loop.
            await asyncio.to_thread(
                log_api_usage_sync,
                provider="anthropic",
                operation="planning_agent.custom_scenario_expand",
                input_tokens=usage["input_tokens"],
                output_tokens=usage["output_tokens"],
                status=status,
                metadata={"scenario": scenario_id, "model": model},
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to log custom-scenario expansion usage: %s", exc)
