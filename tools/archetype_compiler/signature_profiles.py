"""Load and inject archetype-specific architectural identity profiles."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from massing_recipes import compile_massing_recipe

PROFILE_PATH = Path(__file__).with_name("architectural_signature_profiles.json")
PROFILE_EXTENSION_DIR = Path(__file__).with_name("architectural_signature_profiles.d")


def load_signature_profiles(path: Path = PROFILE_PATH) -> dict[str, dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != "architectural-signatures@1":
        raise ValueError(f"unsupported signature schema in {path}")
    profiles = deepcopy(payload["profiles"])
    if path.resolve() == PROFILE_PATH.resolve() and PROFILE_EXTENSION_DIR.exists():
        for extension_path in sorted(PROFILE_EXTENSION_DIR.glob("*.json")):
            extension = json.loads(extension_path.read_text(encoding="utf-8"))
            if extension.get("schema") != "architectural-signatures@1":
                raise ValueError(f"unsupported signature schema in {extension_path}")
            duplicates = set(profiles) & set(extension.get("profiles") or {})
            if duplicates:
                raise ValueError(
                    f"duplicate architectural signature profiles in {extension_path}: "
                    + ", ".join(sorted(duplicates))
                )
            profiles.update(deepcopy(extension.get("profiles") or {}))
    return profiles


def _merge_profile(base: dict, override: dict) -> dict:
    """Recursively merge a compact variant profile over its parent."""
    merged = deepcopy(base)
    for key, value in override.items():
        if key == "extends":
            continue
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_profile(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def _patch_named_items(items: list[dict], patches: dict[str, dict], removed: set[str]) -> list[dict]:
    """Apply compact variant overrides to graph lists keyed by stable ``id`` values."""
    resolved: list[dict] = []
    found: set[str] = set()
    for item in items:
        item_id = str(item.get("id", ""))
        if item_id in removed:
            continue
        if item_id in patches:
            item = _merge_profile(item, patches[item_id])
            found.add(item_id)
        resolved.append(item)
    missing = set(patches) - found
    if missing:
        raise KeyError(f"massing graph overrides reference missing ids: {', '.join(sorted(missing))}")
    return resolved


def _apply_massing_graph_patches(profile: dict) -> dict:
    """Resolve inherited graph edits without duplicating an entire landmark recipe."""
    graph = profile.get("massing_graph")
    if not isinstance(graph, dict):
        return profile
    for noun, plural in (("node", "nodes"), ("assembly", "assemblies"), ("void", "voids")):
        patches = graph.pop(f"{noun}_overrides", {})
        removed = set(graph.pop(f"remove_{noun}_ids", []))
        appended = graph.pop(f"append_{plural}", [])
        if patches or removed:
            graph[plural] = _patch_named_items(graph.get(plural, []), patches, removed)
        if appended:
            graph.setdefault(plural, []).extend(deepcopy(appended))
    return profile


def _resolved_profile(profiles: dict[str, dict], key: str, trail: tuple[str, ...] = ()) -> dict:
    if key in trail:
        raise ValueError(f"architectural signature inheritance cycle: {' -> '.join((*trail, key))}")
    profile = deepcopy(profiles[key])
    parent = profile.get("extends")
    if not parent:
        return profile
    if parent not in profiles:
        raise KeyError(f"architectural signature profile {key!r} extends missing profile {parent!r}")
    return _apply_massing_graph_patches(
        _merge_profile(_resolved_profile(profiles, parent, (*trail, key)), profile)
    )


def signature_for(archetype_id: str, path: Path = PROFILE_PATH) -> dict:
    profiles = load_signature_profiles(path)
    try:
        return _resolved_profile(profiles, archetype_id)
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
        profile = _resolved_profile(profiles, key)
        massing_recipe = profile.pop("massing_recipe", None)
        if massing_recipe:
            profile["massing_graph"] = compile_massing_recipe(
                massing_recipe, grammar.get("dimensions") or {}
            )
        # Massing graphs are a renderer-level building contract rather than a
        # facade-signature hint. Keep them at the grammar root so renderers can
        # opt in without sending a large geometry recipe to image generators.
        massing_graph = profile.pop("massing_graph", None)
        dimension_overrides = profile.pop("dimension_overrides", None)
        grammar["architectural_signature"] = profile
        if massing_graph:
            grammar["massing_graph"] = massing_graph
        if dimension_overrides:
            grammar.setdefault("dimensions", {}).update(deepcopy(dimension_overrides))
        materials = grammar.get("materials") or {}
        for slot, override in (profile.get("material_overrides") or {}).items():
            if slot in materials:
                materials[slot].update(deepcopy(override))
    return grammar
