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


def inject_signature(grammar: dict, archetype_id: str | None = None) -> dict:
    """Mutate and return a serialized grammar with its optional v8 profile."""
    source = grammar.get("source") or {}
    key = archetype_id or source.get("archetype_id")
    profiles = load_signature_profiles()
    if key in profiles:
        profile = deepcopy(profiles[key])
        grammar["architectural_signature"] = profile
        materials = grammar.get("materials") or {}
        for slot, override in (profile.get("material_overrides") or {}).items():
            if slot in materials:
                materials[slot].update(deepcopy(override))
    return grammar
