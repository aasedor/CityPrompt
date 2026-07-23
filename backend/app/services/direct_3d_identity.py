"""Server-owned, human-readable design identity for Direct 3D prompts.

The paid renderer may use persisted catalog identifiers as a small amount of
architectural context, but it must never forward user-authored labels or prose.
Every word returned here is therefore resolved through backend-owned building
family data or the validated executable public-realm catalog.
"""

from __future__ import annotations

import re
from typing import Any

from app.services.plan_geometry.archetypes import dims_by_id, load_families
from app.services.public_realm_lego import (
    PUBLIC_REALM_RECIPE_PROPERTY,
    build_public_realm_capability_catalog,
    public_realm_recipe_identity,
)


_VERSION_SUFFIX = re.compile(r"_v\d+$", re.IGNORECASE)


def _humanize_identifier(value: str) -> str:
    """Turn one trusted catalog identifier into a compact display phrase."""

    without_version = _VERSION_SUFFIX.sub("", value.strip())
    return " ".join(
        token.upper() if token.lower() in {"bipoc", "brt"} else token.capitalize()
        for token in re.split(r"[_\-\s]+", without_version)
        if token
    )


def _building_design_identity(properties: dict[str, Any]) -> str | None:
    table = dims_by_id()
    families = load_families()
    archetype_map = families.get("archetypes", {})
    family_specs = families.get("families", {})

    raw_archetype_id = properties.get("development_archetype_id")
    if not isinstance(raw_archetype_id, str):
        return None
    archetype_id = raw_archetype_id.strip()
    entry = table.get(archetype_id)

    # Some persisted selections carry a known variant in the archetype slot.
    # Resolve it only through the server catalog; never humanize an unknown ID.
    if entry is None:
        entry = next(
            (
                candidate
                for candidate in table.values()
                if archetype_id in (candidate.get("variant_ids") or ())
            ),
            None,
        )
    if not isinstance(entry, dict):
        return None

    canonical_id = str(entry.get("id") or "")
    family_id = archetype_map.get(canonical_id)
    family = family_specs.get(family_id) if isinstance(family_id, str) else None
    title = entry.get("title")
    if not isinstance(title, str) or not title.strip():
        return None
    title = title.strip()
    if not isinstance(family, dict):
        return title

    region = family.get("region")
    character = family.get("character")
    region_text = region.strip() if isinstance(region, str) else ""
    character_text = character.strip() if isinstance(character, str) else ""
    if region_text and character_text:
        return f"{title} — {region_text}: {character_text}"
    if region_text:
        return f"{title} — {region_text}"
    if character_text:
        return f"{title} — {character_text}"
    return title


def _public_realm_design_identity(properties: dict[str, Any]) -> str | None:
    stored_recipe = properties.get(PUBLIC_REALM_RECIPE_PROPERTY)
    if not isinstance(stored_recipe, dict):
        return None
    identity = public_realm_recipe_identity(stored_recipe)
    if identity is None:
        return None
    recipe = identity["recipe"]
    catalog = build_public_realm_capability_catalog()
    capability = next(
        (
            item
            for item in catalog.capabilities
            if item.family_id == recipe["family_id"]
            and item.family_version == recipe["family_version"]
        ),
        None,
    )
    if capability is None:
        return None
    selection = next(
        (
            item
            for item in capability.selections
            if item.archetype_id == recipe["archetype_id"]
            and item.variant_id == recipe["variant_id"]
        ),
        None,
    )
    if selection is None:
        return None

    archetype = _humanize_identifier(selection.archetype_id)
    family = re.sub(
        r"^(?:Render-Locked|Legacy)\s+",
        "",
        capability.title,
        flags=re.IGNORECASE,
    ).strip()
    appearance = _humanize_identifier(selection.appearance_kit_id)
    details = [family, appearance]
    if capability.kind == "park" and selection.planting_structure:
        details.append(_humanize_identifier(selection.planting_structure))
    return f"{archetype} — {', '.join(details)}"


def direct_3d_zone_design_identity(
    semantic_class: str,
    properties: dict[str, Any] | None,
) -> str | None:
    """Resolve one concise identity from server-known persisted selections."""

    safe_properties = properties if isinstance(properties, dict) else {}
    if semantic_class == "building":
        return _building_design_identity(safe_properties)
    if semantic_class in {"park", "street"}:
        return _public_realm_design_identity(safe_properties)
    return None
