"""The Master Planner call — one LLM authoring a whole-site design.

Follows the planning_agents runner discipline: forced tool use (prose leaks
otherwise), up to two samples for malformed payloads, never raises — a failed
composition returns (None, usage, notes) and the caller falls back to the
scenario's preset palette. The DNA block leads the user turn with
cache_control so repeated compositions on the same snapshot cache-hit.
"""

from __future__ import annotations

import json
import logging
from functools import lru_cache
from typing import Any

import anthropic
from celery.exceptions import SoftTimeLimitExceeded
from pydantic import ValidationError

from app.services.master_planner.lego_catalog import LegoPlanningCatalog
from app.services.master_planner.spec import (
    BAND_KEYS,
    CENTRAL_PARK_VARIANT_IDS,
    CENTRAL_PARK_IDS,
    COURTYARD_STRUCTURES,
    GREENWAY_VARIANT_IDS,
    LAYOUT_STRATEGIES,
    LEGO_CENTRAL_PARK_IDS,
    LEGO_LOCAL_STREET_IDS,
    LEGO_SPINE_STREET_IDS,
    LEGO_WATER_ARCHETYPE_IDS,
    LINEAR_STRUCTURES,
    LOCAL_PUBLIC_REALM_VARIANT_IDS,
    LOCAL_STREET_IDS,
    PARK_STRUCTURES,
    POCKET_PARK_VARIANT_IDS,
    POCKET_STRUCTURES,
    SPINE_PUBLIC_REALM_VARIANT_IDS,
    SPINE_STREET_IDS,
    TYPOLOGIES,
    WATER_ARCHETYPE_IDS,
    MasterPlanSpec,
    lego_fallback_spec,
    validate_spec,
)
from app.services.plan_geometry.archetypes import load_dims_table
from app.services.planning_agents.runner import dna_prompt_block
from app.services.planning_agents.schemas import ScenarioDefinition
from app.services.public_realm_lego import build_public_realm_capability_catalog

logger = logging.getLogger(__name__)

MASTER_PLANNER_MAX_TOKENS = 3500
DNA_SECTIONS = ("site", "land_use", "built_form", "mobility", "environment", "policy")

SYSTEM = (
    "You are the Master Planner for City Prompt — one of the world's most accomplished and "
    "creative urban designers, with the combined instincts of a master architect, an urban "
    "planner, and a landscape architect. You are handed a site's Urban Intelligence DNA, a "
    "planning philosophy, and the expert panel's parameters; you compose the master plan a "
    "deterministic geometry engine will draw. Record it with the record_master_plan tool.\n\n"
    "Design principles you never compromise on:\n"
    "- A real district is VARIED: no band monoculture. Give each band a distinct primary "
    "character plus 1-3 alternates of genuinely different type or aesthetic, so a block ring "
    "reads as several buildings by several hands, never one model stamped around a courtyard.\n"
    "- Vary the massing: mix perimeter_block, row_bars, point_towers and anchor_mass across "
    "bands as the philosophy demands. Do not default everything to courtyard perimeter blocks.\n"
    "- Anchor deliberately: the anchor band is ONE landmark block beside the central green — "
    "give it civic or institutional presence, not another apartment ring.\n"
    "- Set the urban grain to the LOCAL context: choose block_target_m so the site subdivides "
    "into several walkable blocks (Calgary inner-city blocks run ~100-115 m long, ~60-70 m deep). "
    "Never leave a multi-hectare site as one megablock wrapped in a single giant courtyard.\n"
    "- Respect the context: step heights down at edges that meet existing low-rise fabric; let "
    "the DNA's surrounding heights and land uses shape the section.\n"
    "- Landscape is DESIGNED, never scattered: formal allées line boulevards and civic greens, "
    "groves and meadows shape naturalistic parks, courtyards are gardens or formal quads. "
    "Choose planting structures the way a landscape architect would, and say why.\n"
    "- Streets have character: pick a spine and local street identity that carries the plan's "
    "idea (a Haussmann boulevard says something different from a woonerf).\n\n"
    "- For executable LEGO plans, choose a Public Realm LEGO variant for every requested "
    "park and street role. You choose design intent; the deterministic family compiler owns "
    "dimensions, clearances, accessibility, topology, and object placement.\n\n"
    "Hard rules:\n"
    "- development_type values MUST come from the catalog list you are given; aesthetics should "
    "come from the per-type lists (fuzzy matching tolerates close variants).\n"
    "- floors must be believable for the type (rowhouses are not 20 storeys).\n"
    "- Direct archetype ids (streets, water, central park) must come from the allowed lists or "
    "be omitted — an invented id renders nothing.\n"
    "- Small sites express few bands: with fewer than ~5 blocks only mid/edge (and maybe "
    "frontage) will appear; put your best thinking there and set single_block_typology for the "
    "degenerate one-block case."
)


@lru_cache(maxsize=1)
def _legacy_catalog_vocabulary() -> str:
    """development_type -> aesthetic families, generated from the live dims
    table so the prompt can never drift from the catalog."""
    by_type: dict[str, set[str]] = {}
    for entry in load_dims_table():
        if not entry.get("usable"):
            continue
        aesthetic = entry.get("aesthetic_category")
        by_type.setdefault(entry["development_type"], set()).add(aesthetic or "")
    lines = ["BUILDING CATALOG (development_type: aesthetics):"]
    for dev_type in sorted(by_type):
        aesthetics = sorted(a for a in by_type[dev_type] if a)
        lines.append(f"- {dev_type}: {', '.join(aesthetics) if aesthetics else '(any)'}")
    return "\n".join(lines)


def _catalog_vocabulary(lego_catalog: LegoPlanningCatalog | None = None) -> str:
    if lego_catalog is None:
        return _legacy_catalog_vocabulary()
    return (
        lego_catalog.prompt_vocabulary
        + "\n\n"
        + build_public_realm_capability_catalog().prompt_vocabulary
    )


def _band_schema(
    lego_catalog: LegoPlanningCatalog | None = None,
) -> dict[str, Any]:
    properties: dict[str, Any] = {
        "development_type": {"type": "string", "description": "One of the catalog development_type values."},
        "aesthetic": {"type": "string", "description": "Aesthetic family for this band, from the catalog list for the chosen type."},
        "floors": {"type": "number", "minimum": 1, "maximum": 40},
        "typology": {"type": "string", "enum": list(TYPOLOGIES)},
        "alternates": {
            "type": "array",
            "maxItems": 3,
            "description": "1-3 DIFFERENT characters rotated across this band's blocks and bars.",
            "items": {
                "type": "object",
                "properties": {
                    "development_type": {"type": "string"},
                    "aesthetic": {"type": "string"},
                },
                "required": ["development_type"],
            },
        },
    }
    required = ["development_type", "aesthetic", "floors", "typology"]
    if lego_catalog is not None:
        exact_parent = {
            "type": "string",
            "enum": list(lego_catalog.parent_ids),
            "description": (
                "Exact imported LEGO parent archetype. Choose only from this enum; "
                "the validator selects an executable child variant when required."
            ),
        }
        properties["archetype_id"] = exact_parent
        properties["alternates"]["items"]["properties"]["archetype_id"] = exact_parent
        properties["alternates"]["items"]["required"] = [
            "development_type",
            "archetype_id",
        ]
        required.append("archetype_id")

    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def _master_plan_tool(
    lego_catalog: LegoPlanningCatalog | None = None,
) -> dict[str, Any]:
    # The legacy colored-polygon planner keeps its full visual vocabulary.
    # When the LEGO catalog is supplied, the tool itself exposes only public-
    # realm identities that have an executable family/recipe contract.
    spine_ids = LEGO_SPINE_STREET_IDS if lego_catalog is not None else SPINE_STREET_IDS
    local_ids = LEGO_LOCAL_STREET_IDS if lego_catalog is not None else LOCAL_STREET_IDS
    central_park_ids = (
        LEGO_CENTRAL_PARK_IDS if lego_catalog is not None else CENTRAL_PARK_IDS
    )
    water_ids = LEGO_WATER_ARCHETYPE_IDS if lego_catalog is not None else WATER_ARCHETYPE_IDS
    tool = {
        "name": "record_master_plan",
        "description": "Record the composed master plan for the site.",
        "input_schema": {
            "type": "object",
            "properties": {
                "design_narrative": {
                    "type": "string",
                    "description": "Your design statement, 60-140 words, in the voice of the master planner: the organizing idea, how built form and landscape carry it, and why it fits this site.",
                },
                "layout_strategy": {"type": "string", "enum": list(LAYOUT_STRATEGIES)},
                "block_target_m": {
                    "type": "number",
                    "description": "Urban grain: preferred block edge in metres (~70-100 fine inner-city, ~110-140 generous/grand). The engine guarantees no block edge exceeds ~1.15x this, so a small site still subdivides. Match the LOCAL grain; omit to use the scenario default.",
                },
                "curvilinear": {"type": "boolean", "description": "Bow the street grid toward the site's heart."},
                "laneways": {"type": "boolean", "description": "Rear lanes behind rowhouse bars."},
                "spine_archetype_id": {
                    "type": "string",
                    "enum": sorted(spine_ids),
                    "description": f"Main-street character, one of: {', '.join(sorted(spine_ids))}. Omit for width-band default.",
                },
                "local_archetype_id": {
                    "type": "string",
                    "enum": sorted(local_ids),
                    "description": f"Local-street character, one of: {', '.join(sorted(local_ids))}. Omit for width-band default.",
                },
                "crescent_archetype_id": {
                    "type": "string",
                    "description": "Set to london_crescent_road to tag genuinely bowed locals as crescents (requires curvilinear).",
                },
                "single_block_typology": {
                    "type": "string",
                    "enum": list(TYPOLOGIES),
                    "description": "Massing when the site yields ONE block (no internal streets). Omit to keep a perimeter courtyard.",
                },
                "bands": {
                    "type": "object",
                    "description": "anchor = landmark block by the central green; frontage = blocks on the main spine; core = deep interior; edge = boundary step-down; mid = general fabric.",
                    "properties": {
                        key: _band_schema(lego_catalog)
                        for key in BAND_KEYS
                    },
                    "required": list(BAND_KEYS),
                },
                "open_space": {
                    "type": "object",
                    "properties": {
                        "water_feature": {"type": "boolean"},
                        "formal_water": {"type": "boolean", "description": "true = formal reflecting basin, false = naturalized pond edge."},
                        "water_archetype_id": {
                            "type": "string",
                            "enum": sorted(water_ids),
                            "description": f"One of: {', '.join(sorted(water_ids))}.",
                        },
                        "plaza": {"type": "boolean", "description": "Carve a civic plaza off the anchor block."},
                        "central_park_archetype_id": {
                            "type": "string",
                            "enum": sorted(central_park_ids),
                            "description": f"Direct character for the signature green, one of: {', '.join(sorted(central_park_ids))}. Omit to resolve by area.",
                        },
                    },
                    "required": ["water_feature", "plaza"],
                },
                "landscape": {
                    "type": "object",
                    "properties": {
                        "park_structure": {"type": "string", "enum": list(PARK_STRUCTURES)},
                        "pocket_structure": {"type": "string", "enum": list(POCKET_STRUCTURES)},
                        "courtyard_structure": {"type": "string", "enum": list(COURTYARD_STRUCTURES)},
                        "greenway_structure": {"type": "string", "enum": list(LINEAR_STRUCTURES)},
                        "rationale": {"type": "string", "description": "One or two sentences of landscape-architecture reasoning."},
                    },
                    "required": ["park_structure", "courtyard_structure"],
                },
                "public_realm": {
                    "type": "object",
                    "description": (
                        "Visible variants from executable Public Realm LEGO families. "
                        "Select identities only; the compiler owns metric geometry and safety."
                    ),
                    "properties": {
                        "spine_street_variant_id": {
                            "type": "string",
                            "enum": list(SPINE_PUBLIC_REALM_VARIANT_IDS),
                        },
                        "local_street_variant_id": {
                            "type": "string",
                            "enum": list(LOCAL_PUBLIC_REALM_VARIANT_IDS),
                        },
                        "central_park_variant_id": {
                            "type": "string",
                            "enum": list(CENTRAL_PARK_VARIANT_IDS),
                        },
                        "pocket_park_variant_id": {
                            "type": "string",
                            "enum": list(POCKET_PARK_VARIANT_IDS),
                        },
                        "courtyard_variant_id": {
                            "type": "string",
                            "enum": list(POCKET_PARK_VARIANT_IDS),
                        },
                        "greenway_variant_id": {
                            "type": "string",
                            "enum": list(GREENWAY_VARIANT_IDS),
                        },
                        "rationale": {
                            "type": "string",
                            "description": "One sentence explaining how the variants reinforce the plan.",
                        },
                    },
                    "required": [
                        "spine_street_variant_id",
                        "local_street_variant_id",
                        "central_park_variant_id",
                        "pocket_park_variant_id",
                        "courtyard_variant_id",
                        "greenway_variant_id",
                    ],
                },
            },
            "required": [
                "design_narrative",
                "layout_strategy",
                "bands",
                "open_space",
                "landscape",
                "public_realm",
            ],
        },
    }
    if lego_catalog is None:
        # Keep the established colored-polygon Master Planner schema intact.
        # Public Realm LEGO selection is an executable-3D concern only.
        tool["input_schema"]["properties"].pop("public_realm", None)
        tool["input_schema"]["required"].remove("public_realm")
    return tool


def _note(code: str, severity: str, message: str) -> dict[str, Any]:
    return {"code": code, "severity": severity, "message": message,
            "source_phase": "master_planner"}


def _site_brief(site_summary: dict[str, Any], definition: ScenarioDefinition,
                parameters: dict[str, Any], brief: str | None) -> str:
    area_m2 = float(site_summary.get("area_m2") or 0.0)
    est_blocks = site_summary.get("est_blocks")
    lines = [
        f"SCENARIO: {definition.label} ({definition.scenario_id})",
        f"PHILOSOPHY: primary={definition.philosophy.primary}"
        + (f", secondary={definition.philosophy.secondary}" if definition.philosophy.secondary else "")
        + f", intensity={definition.philosophy.intensity:g}",
    ]
    if definition.emphasis:
        lines.append(f"EMPHASIS: {definition.emphasis}")
    if brief:
        lines.append(f"USER BRIEF: {str(brief)[:600]}")
    lines.append(
        f"SITE GEOMETRY: ~{area_m2 / 10000:.1f} ha"
        + (f", expect roughly {est_blocks} developable blocks" if est_blocks else "")
    )
    if parameters:
        expert_lines = [
            f"  - {path}: {merged.get('value') if isinstance(merged, dict) else merged}"
            for path, merged in sorted(parameters.items())
        ]
        lines.append("EXPERT PANEL PARAMETERS (already merged — your plan should honor their intent):\n"
                     + "\n".join(expert_lines[:12]))
    return "\n".join(lines)


async def compose_master_plan(
    *,
    dna_json: dict[str, Any],
    definition: ScenarioDefinition,
    site_summary: dict[str, Any],
    parameters: dict[str, Any] | None = None,
    brief: str | None = None,
    api_key: str,
    model: str,
    palette_hint: str | None = None,
    lego_catalog: LegoPlanningCatalog | None = None,
) -> tuple[MasterPlanSpec | None, dict[str, Any], list[dict[str, Any]]]:
    """Compose and validate a master plan. Never raises (soft time limit
    excepted — Celery must see it); returns (spec|None, usage, notes)."""
    usage: dict[str, Any] = {"agent_id": "master_planner", "model": model,
                             "input_tokens": 0, "output_tokens": 0, "status": "success"}
    notes: list[dict[str, Any]] = []

    if lego_catalog is not None and not lego_catalog.capabilities:
        usage["status"] = "error"
        notes.append(_note(
            "MASTER_PLANNER_NO_LEGO_CATALOG",
            "warning",
            "No executable LEGO building families are available; the Master Planner cannot draw buildings.",
        ))
        return None, usage, notes

    user_content = [
        {
            "type": "text",
            "text": "URBAN INTELLIGENCE DNA:\n" + dna_prompt_block(dna_json, DNA_SECTIONS),
            "cache_control": {"type": "ephemeral"},
        },
        {
            "type": "text",
            "text": (
                _site_brief(site_summary, definition, parameters or {}, brief)
                + "\n\n" + _catalog_vocabulary(lego_catalog)
                + "\n\nCompose the master plan now. Be site-specific and philosophy-true; "
                  "make the variety deliberate (distinct alternates per band, mixed typologies) "
                  "and the landscape intentional."
            ),
        },
    ]

    client = anthropic.AsyncAnthropic(api_key=api_key)
    try:
        payload: dict[str, Any] | None = None
        for attempt in range(2):
            message = await client.messages.create(
                model=model,
                max_tokens=MASTER_PLANNER_MAX_TOKENS,
                system=SYSTEM,
                messages=[{"role": "user", "content": user_content}],
                tools=[_master_plan_tool(lego_catalog)],
                tool_choice={"type": "tool", "name": "record_master_plan"},
            )
            usage["input_tokens"] += message.usage.input_tokens
            usage["output_tokens"] += message.usage.output_tokens
            payload = next(
                (block.input for block in message.content
                 if getattr(block, "type", None) == "tool_use"),
                None,
            )
            if isinstance(payload, str):
                # Known tool-use quirk (see runner.py): nested JSON as string.
                try:
                    payload = json.loads(payload)
                except json.JSONDecodeError:
                    payload = None
            if isinstance(payload, dict):
                break
            logger.warning("Master planner attempt %d: no usable tool payload", attempt)
        if not isinstance(payload, dict):
            raise ValueError("no usable tool payload after retry")

        try:
            raw_spec = MasterPlanSpec(**payload)
        except (ValidationError, TypeError) as exc:
            raise ValueError(f"spec failed validation: {exc}") from exc

        spec, repair_notes = validate_spec(
            raw_spec,
            definition.scenario_id,
            palette_hint,
            lego_catalog=lego_catalog,
        )
        notes.extend(repair_notes)
        if not spec.bands:
            # Nothing usable survived — the preset palette will draw better.
            raise ValueError("no valid bands in the composed plan")
        notes.append(_note(
            "MASTER_PLAN_COMPOSED", "info",
            f"Master Planner: {spec.design_narrative[:220]}" if spec.design_narrative
            else "Master Planner composed the plan.",
        ))
        return spec, usage, notes

    except SoftTimeLimitExceeded:
        raise  # must reach the Celery task handler
    except Exception as exc:  # noqa: BLE001 — the draw must survive the planner
        logger.warning("Master planner failed: %s", exc)
        usage["status"] = "error"
        fallback_description = (
            "the imported LEGO catalog supplied a deterministic fallback plan"
            if lego_catalog is not None
            else "the scenario's preset palette drew this plan"
        )
        notes.append(_note(
            "MASTER_PLANNER_UNAVAILABLE", "warning",
            f"Master Planner unavailable ({exc}) — {fallback_description}.",
        ))
        if lego_catalog is not None:
            fallback = lego_fallback_spec(
                definition.scenario_id,
                lego_catalog,
                palette_hint,
                narrative=(
                    "A deterministic plan composed from the imported LEGO "
                    "building, park, and street kits."
                ),
            )
            notes.append(_note(
                "MASTER_PLANNER_LEGO_FALLBACK",
                "info",
                "The imported LEGO catalog supplied a complete deterministic fallback plan.",
            ))
            return fallback, usage, notes
        return None, usage, notes
    finally:
        try:
            await client.close()
        except Exception:  # noqa: BLE001 — cleanup must never mask the result
            pass
