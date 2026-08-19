"""Design Director — the synthesis voice that reviews the whole plan.

The panel's four experts each argue inside one discipline and the coordinator
merges them one parameter at a time. Nobody in that pipeline ever looks at the
resulting plan AS A PLAN. This module is that reviewer: the master architect
who reads the merged set against the design doctrine, resolves the incoherence
the deterministic audit found, and states the organizing idea the plan is
actually pursuing.

Authority is deliberately bounded, because a design voice with an open hand
over the numbers would silently become the geometry engine:

- NUMERIC AND ENUM paths — it may only choose a value an expert already put on
  the table, or the deterministic repair the coherence audit computed. Anything
  else is dropped with a note. It cannot invent a height nobody proposed.
- NARRATIVE paths (``site.design_brief``, ``layout.strategy``) — free
  authorship. These are prose the geometry/prompt layers read as guidance, they
  cannot violate a threshold, and authoring them is the entire reason a design
  director exists.

Degradation contract, matching the rest of the panel: if the model call fails,
the deterministic repairs still apply and the charter falls back to a computed
summary. A design review NEVER fails a scenario run.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import anthropic
from celery.exceptions import SoftTimeLimitExceeded
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.core.usage_logger import log_api_usage_sync
from app.services.planning_agents.coherence import (
    ARITHMETIC_RULE_IDS,
    CoherenceFinding,
    CoherenceOutcome,
    apply_repairs,
    audit_and_repair,
    audit_coherence,
    resolve_values,
)
from app.services.planning_agents.design_doctrine import (
    doctrine_prompt_block,
    get_principle,
)
from app.services.planning_agents.philosophy import philosophy_prompt_block
from app.services.planning_agents.schemas import (
    PARAMETER_VOCABULARY,
    MergedParameter,
    ScenarioDefinition,
)
from app.services.urban_dna.schema import ValidationNote

logger = logging.getLogger(__name__)

DIRECTOR_MAX_TOKENS = 3000

# Prose guidance the director may author outright — see the module docstring.
NARRATIVE_PATHS = ("site.design_brief", "layout.strategy")

# Numeric equality tolerance when checking a proposed value against the values
# experts actually put on the table.
_VALUE_EPSILON = 1e-6


class DesignNote(BaseModel):
    """One design observation, anchored to a doctrine principle."""

    principle_id: str
    title: str = ""
    observation: str
    severity: str = "info"


class ParameterResolution(BaseModel):
    """What the director did about one coherence finding."""

    rule_id: str
    parameter_path: str
    from_value: Any = None
    to_value: Any = None
    decided_by: str = "deterministic"  # "deterministic" | "design_director"
    reason: str = ""


class DesignReview(BaseModel):
    charter: str = ""
    critique: list[DesignNote] = Field(default_factory=list)
    signature_moves: list[str] = Field(default_factory=list)
    resolutions: list[ParameterResolution] = Field(default_factory=list)
    findings: list[CoherenceFinding] = Field(default_factory=list)
    residual_findings: list[CoherenceFinding] = Field(default_factory=list)
    notes: list[ValidationNote] = Field(default_factory=list)
    usage: dict[str, Any] = Field(default_factory=dict)
    failed: bool = False


DIRECTOR_SYSTEM = (
    "You are the Design Director on a municipal planning panel — the master architect and urban "
    "designer who reviews the plan as a whole after four discipline experts have each argued "
    "inside their own scope and a deterministic coordinator has merged them one parameter at a "
    "time.\n\n"
    "Nobody before you has looked at the plan as a plan. That is your entire job. You are given "
    "the merged parameters, every position the experts took, and a deterministic coherence audit "
    "that has already found where the merged set contradicts itself.\n\n"
    "Rules:\n"
    "- Numeric and enum parameters: you may ONLY select a value that an expert proposed or that "
    "the audit computed as its repair. You may not invent numbers. Anything else is discarded.\n"
    "- site.design_brief and layout.strategy are yours to write. This is where the design lives.\n"
    "- Every critique note must cite a principle_id from the doctrine you were given. A note "
    "without a real principle_id is discarded.\n"
    "- State the organizing idea first and concretely. 'A vibrant mixed-use community' is not an "
    "organizing idea; 'a single planted spine from the station to the creek, with the tallest "
    "frontage facing it and the fabric stepping down to the west' is one.\n"
    "- Name what the plan gives up. A design position presented as pure gain is not a position.\n"
    "- Record everything with the record_design_review tool."
)


def _director_tool() -> dict[str, Any]:
    return {
        "name": "record_design_review",
        "description": "Record the Design Director's whole-plan review.",
        "input_schema": {
            "type": "object",
            "properties": {
                "charter": {
                    "type": "string",
                    "description": "<=80 words: the organizing idea this plan pursues, concretely.",
                },
                "signature_moves": {
                    "type": "array",
                    "description": "2-4 concrete moves that give this plan its identity.",
                    "items": {"type": "string"},
                },
                "critique": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "principle_id": {"type": "string", "description": "must exist in the doctrine"},
                            "observation": {"type": "string"},
                            "severity": {"type": "string", "enum": ["info", "warning", "error"]},
                        },
                        "required": ["principle_id", "observation"],
                    },
                },
                "resolutions": {
                    "type": "array",
                    "description": "One entry per coherence finding you are deciding.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "rule_id": {"type": "string"},
                            "parameter_path": {"type": "string", "enum": sorted(PARAMETER_VOCABULARY)},
                            "value": {"type": ["string", "number"]},
                            "reason": {"type": "string"},
                        },
                        "required": ["rule_id", "parameter_path", "value", "reason"],
                    },
                },
            },
            "required": ["charter", "critique"],
        },
    }


# ---------------------------------------------------------------------------
# Bounded authority
# ---------------------------------------------------------------------------


def _same_value(left: Any, right: Any) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return left is right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return abs(float(left) - float(right)) <= _VALUE_EPSILON
    return str(left).strip().lower() == str(right).strip().lower()


def allowed_values(
    path: str,
    merged: dict[str, MergedParameter],
    findings: list[CoherenceFinding],
) -> list[Any]:
    """Every value the director is permitted to select for ``path``.

    The union of what the experts actually proposed (including the losing
    positions — reopening a merge the philosophy weighting decided is a
    legitimate design act) and what the audit computed as a legal repair.
    """
    permitted: list[Any] = []
    parameter = merged.get(path)
    if parameter is not None:
        for candidate in parameter.candidates:
            if isinstance(candidate, dict) and "value" in candidate:
                permitted.append(candidate["value"])
        permitted.append(parameter.value)
    for finding in findings:
        if finding.repair_path == path and finding.repair_value is not None:
            permitted.append(finding.repair_value)
    return permitted


def _coerce_to_vocabulary(path: str, value: Any) -> Any:
    """Match the value's type to the vocabulary entry, so a numeric parameter
    returned as the string '18' is not rejected as an out-of-bounds string."""
    kind = PARAMETER_VOCABULARY.get(path, {}).get("kind")
    if kind == "number" and isinstance(value, str):
        try:
            return float(value.strip().rstrip("m").strip())
        except ValueError:
            return value
    return value


# ---------------------------------------------------------------------------
# Prompt assembly
# ---------------------------------------------------------------------------


def _parameter_block(merged: dict[str, MergedParameter]) -> str:
    lines = ["MERGED PLAN PARAMETERS (what the coordinator adopted, and every position taken):"]
    for path in sorted(merged):
        parameter = merged[path]
        lines.append(f"\n{path} = {parameter.value!r}  [adopted from {', '.join(parameter.contributors)}]")
        lines.append(f"  reason: {parameter.rationale[:200]}")
        others = [
            f"{c.get('agent_id')}={c.get('value')!r}"
            for c in parameter.candidates
            if isinstance(c, dict) and not _same_value(c.get("value"), parameter.value)
        ]
        if others:
            lines.append(f"  positions NOT adopted (you may select any of these): {'; '.join(others)}")
    return "\n".join(lines)


def _findings_block(findings: list[CoherenceFinding]) -> str:
    if not findings:
        return (
            "COHERENCE AUDIT: no cross-parameter defects found. The merged set is internally "
            "consistent — your job is the design reading, not repair."
        )
    lines = ["COHERENCE AUDIT — defects the merged set contains, most severe first:"]
    for finding in findings:
        lines.append(f"\n[{finding.severity.upper()}] {finding.rule_id} ({', '.join(finding.principle_ids)})")
        lines.append(f"  {finding.message}")
        if finding.has_repair():
            lines.append(
                f"  DETERMINISTIC REPAIR: {finding.repair_path} -> {finding.repair_value!r} "
                f"({finding.repair_mode}). Cost: {finding.repair_cost}"
            )
            lines.append(
                "  You may accept this repair, or select a different value that an expert "
                "proposed for that path. Say why."
            )
    return "\n".join(lines)


def _site_block(dna_json: dict[str, Any] | None, metrics: dict[str, Any] | None) -> str:
    if not dna_json and not metrics:
        return ""
    payload: dict[str, Any] = {}
    if dna_json:
        payload["site"] = dna_json.get("site")
        payload["built_form_context"] = dna_json.get("built_form")
    if metrics:
        payload["derived_metrics"] = metrics
    return "SITE FACTS AND DERIVED NUMBERS:\n" + json.dumps(payload, sort_keys=True, default=str)[:6000]


def context_height_from_dna(dna_json: dict[str, Any] | None) -> float | None:
    """Prevailing surrounding building height, for the transition rule.

    Reads ``built_form.context_avg_height_m`` — the field every city connector
    populates from nearby building footprints. Returns None when the DNA has no
    built-form context, which correctly disables the transition rule rather
    than inventing a context to measure against.
    """
    if not isinstance(dna_json, dict):
        return None
    section = dna_json.get("built_form")
    if not isinstance(section, dict):
        return None
    field = (section.get("fields") or {}).get("context_avg_height_m")
    value = field.get("value") if isinstance(field, dict) else field
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value) if value > 0 else None


def _fallback_charter(
    scenario: ScenarioDefinition,
    outcome: CoherenceOutcome,
) -> str:
    """Deterministic charter — used when the model is unavailable. States what
    was actually done rather than inventing a design intent nobody authored."""
    base = (
        f"{scenario.label}: parameters set under a {scenario.philosophy.primary.replace('_', ' ')} "
        f"philosophy at intensity {scenario.philosophy.intensity:.2f}."
    )
    if not outcome.applied:
        return base + " The merged parameter set passed the coherence audit without repair."
    repaired = ", ".join(sorted({finding.rule_id.replace("_", " ") for finding in outcome.applied}))
    return (
        base + f" The design review was unavailable, so {len(outcome.applied)} coherence "
        f"repair(s) were applied mechanically ({repaired}) rather than resolved by design judgement."
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


async def run_design_review(
    merged: dict[str, MergedParameter],
    scenario: ScenarioDefinition,
    *,
    dna_json: dict[str, Any] | None = None,
    metrics: dict[str, Any] | None = None,
    site_area_m2: float | None = None,
    context_height_m: float | None = None,
) -> tuple[dict[str, MergedParameter], DesignReview]:
    """Audit, repair and design-review the merged plan.

    Returns the reviewed parameters and the review. Never raises: every failure
    path still returns a coherent parameter set.
    """
    review = DesignReview()

    outcome = audit_and_repair(
        merged,
        philosophy=scenario.philosophy,
        site_area_m2=site_area_m2,
        context_height_m=context_height_m,
    )
    review.findings = outcome.initial_findings
    review.residual_findings = outcome.residual_findings

    if not outcome.converged:
        review.notes.append(
            ValidationNote(
                code="COHERENCE_UNCONVERGED",
                severity="warning",
                message=(
                    f"The parameter set still carried {len(outcome.residual_findings)} coherence "
                    f"finding(s) after {outcome.passes} repair passes; the remaining conflicts are "
                    "reported rather than resolved."
                ),
                source_phase="coordinator",
            )
        )

    # Deterministic repairs are the floor. The director can move a value off
    # this floor only to another position an expert actually took.
    baseline_values = dict(resolve_values(merged))
    working_values = dict(outcome.values)
    # One resolution per parameter, not one per repair pass. Convergence can
    # touch the same path several times; the user needs the net move, and a
    # list that repeats "yield_plausibility" three times reads as a bug.
    by_path: dict[str, list[CoherenceFinding]] = {}
    for finding in outcome.applied:
        by_path.setdefault(finding.repair_path, []).append(finding)
    for path, group in by_path.items():
        rule_ids = list(dict.fromkeys(finding.rule_id for finding in group))
        review.resolutions.append(
            ParameterResolution(
                rule_id="+".join(rule_ids),
                parameter_path=path,
                from_value=baseline_values.get(path),
                to_value=working_values.get(path),
                decided_by="deterministic",
                reason=group[0].message,
            )
        )

    payload, usage = await _call_director(merged, scenario, outcome, dna_json, metrics)
    review.usage = usage
    _log_usage(usage, scenario.scenario_id)

    if payload is None:
        review.failed = True
        review.charter = _fallback_charter(scenario, outcome)
        review.notes.append(
            ValidationNote(
                code="DESIGN_DIRECTOR_UNAVAILABLE",
                severity="warning",
                message=(
                    "The Design Director review was unavailable; deterministic coherence repairs "
                    "were applied and the plan continues without a design synthesis."
                ),
                source_phase="agent_deliberation",
            )
        )
        return _rebuild(merged, working_values, review), review

    review.charter = str(payload.get("charter", "")).strip() or _fallback_charter(scenario, outcome)
    review.signature_moves = [
        str(move).strip() for move in (payload.get("signature_moves") or []) if str(move).strip()
    ][:4]

    # --- critique: every note must cite a real principle -------------------
    for raw in payload.get("critique") or []:
        if not isinstance(raw, dict):
            continue
        principle = get_principle(str(raw.get("principle_id", "")).strip())
        if principle is None:
            logger.info("Design Director cited unknown principle %r — note dropped", raw.get("principle_id"))
            continue
        observation = str(raw.get("observation", "")).strip()
        if not observation:
            continue
        severity = str(raw.get("severity", "info"))
        review.critique.append(
            DesignNote(
                principle_id=principle.principle_id,
                title=principle.title,
                observation=observation,
                severity=severity if severity in ("info", "warning", "error") else "info",
            )
        )

    # --- resolutions: bounded authority ------------------------------------
    for raw in payload.get("resolutions") or []:
        if not isinstance(raw, dict):
            continue
        path = str(raw.get("parameter_path", "")).strip()
        if path not in PARAMETER_VOCABULARY:
            continue
        proposed = _coerce_to_vocabulary(path, raw.get("value"))
        reason = str(raw.get("reason", "")).strip()
        rule_id = str(raw.get("rule_id", "")).strip() or "design_judgement"
        current = working_values.get(path)

        if path not in NARRATIVE_PATHS:
            permitted = allowed_values(path, merged, outcome.initial_findings)
            if not any(_same_value(proposed, option) for option in permitted):
                review.notes.append(
                    ValidationNote(
                        code=f"DIRECTOR_OUT_OF_BOUNDS:{path}",
                        severity="info",
                        message=(
                            f"The Design Director proposed {proposed!r} for {path}, which no expert "
                            "recommended and the coherence audit did not compute. The value was "
                            "discarded and the audited value kept — the director advises within the "
                            "panel's positions, it does not author numbers."
                        ),
                        source_phase="agent_deliberation",
                    )
                )
                continue

        if _same_value(proposed, current):
            continue
        working_values[path] = proposed
        review.resolutions.append(
            ParameterResolution(
                rule_id=rule_id,
                parameter_path=path,
                from_value=current,
                to_value=proposed,
                decided_by="design_director",
                reason=reason,
            )
        )

    # The director's own moves can reintroduce a defect. Design positions it
    # takes are its to take — those are reported, not overwritten. But raising
    # the storey count without restating the height leaves two numbers
    # describing different buildings, and the geometry engine can only draw
    # one, so arithmetic and life safety are reconciled regardless.
    def _audit(values: dict[str, Any]) -> list[CoherenceFinding]:
        return audit_coherence(
            values,
            philosophy=scenario.philosophy,
            site_area_m2=site_area_m2,
            context_height_m=context_height_m,
        )

    arithmetic = [finding for finding in _audit(working_values) if finding.rule_id in ARITHMETIC_RULE_IDS]
    if arithmetic:
        working_values, reconciled = apply_repairs(working_values, arithmetic)
        for finding in reconciled:
            review.resolutions.append(
                ParameterResolution(
                    rule_id=finding.rule_id,
                    parameter_path=finding.repair_path,
                    from_value=None,
                    to_value=working_values.get(finding.repair_path),
                    decided_by="deterministic",
                    reason=("Reconciled after the Design Director's decision — " + finding.message),
                )
            )

    review.residual_findings = _audit(working_values)

    return _rebuild(merged, working_values, review), review


def _rebuild(
    merged: dict[str, MergedParameter],
    values: dict[str, Any],
    review: DesignReview,
) -> dict[str, MergedParameter]:
    """Fold reviewed values back into MergedParameters, preserving provenance.

    A reviewed parameter keeps its original candidates (the WHY panel still
    shows every position) and gains the design director as a contributor, so
    the audit trail says who moved it and why.
    """
    changed_by_rule = {resolution.parameter_path: resolution for resolution in review.resolutions}
    rebuilt: dict[str, MergedParameter] = {}

    for path, value in values.items():
        original = merged.get(path)
        resolution = changed_by_rule.get(path)
        if original is None:
            rebuilt[path] = MergedParameter(
                parameter_path=path,
                value=value,
                rationale=resolution.reason if resolution else "Introduced by the design review.",
                contributors=["design_director"],
            )
            continue
        if resolution is None:
            rebuilt[path] = original
            continue
        contributors = list(original.contributors)
        marker = "design_director" if resolution.decided_by == "design_director" else "coherence_audit"
        if marker not in contributors:
            contributors.append(marker)
        rebuilt[path] = MergedParameter(
            parameter_path=path,
            value=value,
            rationale=resolution.reason or original.rationale,
            contributors=contributors,
            contested=original.contested,
            candidates=original.candidates,
        )
    return rebuilt


def _log_usage(usage: dict[str, Any], scenario_id: str) -> None:
    """Record token usage. Called after the await, never from inside it."""
    try:
        log_api_usage_sync(
            provider="anthropic",
            operation="planning_agent.design_director",
            input_tokens=usage.get("input_tokens", 0),
            output_tokens=usage.get("output_tokens", 0),
            status=usage.get("status", "success"),
            metadata={"scenario": scenario_id, "model": usage.get("model")},
        )
    except SoftTimeLimitExceeded:
        raise  # sync DB frame — a swallowed soft limit here strands the scenario row
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to log design director usage: %s", exc)


async def _call_director(
    merged: dict[str, MergedParameter],
    scenario: ScenarioDefinition,
    outcome: CoherenceOutcome,
    dna_json: dict[str, Any] | None,
    metrics: dict[str, Any] | None,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """One forced-tool-use call. Returns (payload or None, usage record)."""
    settings = get_settings()
    model = getattr(settings, "design_director_model", "") or settings.urban_dna_agent_model
    usage: dict[str, Any] = {
        "agent_id": "design_director",
        "model": model,
        "input_tokens": 0,
        "output_tokens": 0,
        "status": "success",
    }

    doctrine = doctrine_prompt_block(
        "design_director",
        scenario.philosophy.primary,
        scenario.philosophy.secondary or "",
        limit=10,
    )
    sections = [
        doctrine,
        philosophy_prompt_block(scenario.philosophy),
        f"SCENARIO: {scenario.label}. {scenario.emphasis}" if scenario.emphasis else "",
        _site_block(dna_json, metrics),
        _parameter_block(merged),
        _findings_block(outcome.initial_findings),
    ]
    user_text = "\n\n".join(section for section in sections if section)

    client = None
    try:
        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        message = await client.messages.create(
            model=model,
            max_tokens=DIRECTOR_MAX_TOKENS,
            system=DIRECTOR_SYSTEM,
            messages=[{"role": "user", "content": [{"type": "text", "text": user_text}]}],
            tools=[_director_tool()],
            tool_choice={"type": "tool", "name": "record_design_review"},
        )
        usage["input_tokens"] = message.usage.input_tokens
        usage["output_tokens"] = message.usage.output_tokens
        payload = next(
            (block.input for block in message.content if getattr(block, "type", None) == "tool_use"),
            None,
        )
        if isinstance(payload, str):
            payload = json.loads(payload)
        if not isinstance(payload, dict):
            raise ValueError("design review payload was not an object")
        return payload, usage
    except SoftTimeLimitExceeded:
        raise  # must reach the Celery handler or the scenario row hangs 'running'
    except Exception as exc:  # noqa: BLE001 — the review must never fail the run
        logger.warning("Design Director review failed: %s", exc)
        usage["status"] = "error"
        return None, usage
    finally:
        # Close inside the running loop — a GC-time close after the loop is
        # gone emits "Event loop is closed" noise. Usage is logged by the
        # caller, after the await: log_api_usage_sync opens its own sync DB
        # session and would block the event loop from inside this coroutine.
        if client is not None:
            try:
                await client.close()
            except Exception:  # noqa: BLE001
                pass
