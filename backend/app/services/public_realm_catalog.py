"""Backend-owned identity index for the complete park and street catalogue.

The executable Public Realm LEGO registry is intentionally partial.  This
generated index is the wider trust boundary: it lets known catalogue cards
use a family-pending procedural fallback while unknown or prompt-like IDs
remain fail-closed.  Regenerate the companion JSON from the two frontend
catalogues and let the parity test review any drift explicitly.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Literal


PublicRealmCatalogKind = Literal["park", "street"]
_DATA_DIR = Path(__file__).resolve().parents[1] / "data"
_CATALOG_PATHS = {
    "park": _DATA_DIR / "public_realm_park_variants.json",
    "street": _DATA_DIR / "public_realm_street_variants.json",
}


@dataclass(frozen=True)
class PublicRealmCatalogIdentity:
    kind: PublicRealmCatalogKind
    archetype_id: str
    variant_id: str | None


@lru_cache(maxsize=1)
def public_realm_catalog_variants() -> dict[PublicRealmCatalogKind, dict[str, tuple[str, ...]]]:
    normalized: dict[PublicRealmCatalogKind, dict[str, tuple[str, ...]]] = {}
    for kind, path in _CATALOG_PATHS.items():
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise RuntimeError(f"{path.name} must contain an archetype-to-variant object")
        values: dict[str, tuple[str, ...]] = {}
        for archetype_id, variants in raw.items():
            if not isinstance(archetype_id, str) or not archetype_id:
                raise RuntimeError(f"{path.name} contains an invalid archetype id")
            if not isinstance(variants, list) or not all(
                isinstance(variant_id, str) and variant_id for variant_id in variants
            ):
                raise RuntimeError(f"{path.name} has invalid variants for '{archetype_id}'")
            if len(variants) != len(set(variants)):
                raise RuntimeError(f"{path.name} has duplicate variants for '{archetype_id}'")
            values[archetype_id] = tuple(variants)
        normalized[kind] = values
    return normalized


def public_realm_catalog_ids() -> dict[PublicRealmCatalogKind, frozenset[str]]:
    return {
        kind: frozenset(values)
        for kind, values in public_realm_catalog_variants().items()
    }


def resolve_public_realm_catalog_identity(
    kind: PublicRealmCatalogKind,
    archetype_id: str,
    variant_id: str | None = None,
) -> PublicRealmCatalogIdentity | None:
    variants = public_realm_catalog_variants()[kind].get(archetype_id)
    if variants is None:
        return None
    if variant_id is not None and variant_id not in variants:
        return None
    return PublicRealmCatalogIdentity(
        kind=kind,
        archetype_id=archetype_id,
        variant_id=variant_id,
    )
