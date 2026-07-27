"""Load and inject archetype-specific architectural identity profiles."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

PROFILE_PATH = Path(__file__).with_name("architectural_signature_profiles.json")


def load_signature_profiles(path: Path = PROFILE_PATH) -> dict[str, dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != "architectural-signatures@1":
        raise ValueError(f"unsupported signature schema in {path}")
    return payload["profiles"]


def signature_for(archetype_id: str, path: Path = PROFILE_PATH) -> dict:
    profiles = load_signature_profiles(path)
    try:
        return deepcopy(profiles[archetype_id])
    except KeyError as exc:
        raise KeyError(f"no architectural signature profile for {archetype_id!r}") from exc


def inject_signature(
    grammar: dict,
    archetype_id: str | None = None,
    variant_id: str | None = None,
) -> dict:
    """Mutate and return a serialized grammar with its optional v8 profile."""
    source = grammar.get("source") or {}
    profiles = load_signature_profiles()
    parent_key = archetype_id or source.get("archetype_id")
    source_variant = source.get("variant_id") or source.get("selected_variant_id")
    preferred_variant = variant_id or source_variant
    key = preferred_variant if preferred_variant in profiles else parent_key
    if key in profiles:
        profile = deepcopy(profiles[key])
        # Massing graphs are a renderer-level building contract rather than a
        # facade-signature hint. Keep them at the grammar root so renderers can
        # opt in without sending a large geometry recipe to image generators.
        massing_graph = profile.pop("massing_graph", None)
        dimension_overrides = profile.pop("dimension_overrides", None)
        archetype_aliases = profile.pop("archetype_aliases", None)
        grammar["architectural_signature"] = profile
        if massing_graph:
            grammar["massing_graph"] = massing_graph
        if dimension_overrides:
            grammar.setdefault("dimensions", {}).update(deepcopy(dimension_overrides))
        if archetype_aliases:
            grammar["archetype_aliases"] = list(
                dict.fromkeys(
                    str(value).strip()
                    for value in archetype_aliases
                    if str(value).strip()
                )
            )
        materials = grammar.get("materials") or {}
        for slot, override in (profile.get("material_overrides") or {}).items():
            if slot in materials:
                materials[slot].update(deepcopy(override))
    return grammar
