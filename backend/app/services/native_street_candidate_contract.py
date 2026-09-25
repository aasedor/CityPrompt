"""Offline compiler proposals for hash-locked native street pilots.

The offline builder remains usable for candidate review. The finite classroom
runtime cohort uses the same validator and locks, from a packaged backend copy.
Executable support does not imply completion of a live student/visual review.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from functools import lru_cache

from app.services.public_realm_catalog import resolve_public_realm_catalog_identity
from app.services.public_realm_lego import (
    PublicRealmCapabilityCatalog,
    PublicRealmCompatibility,
    PublicRealmFamilyCapability,
    PublicRealmSelectionCapability,
)


_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_ID = re.compile(r"[a-z][a-z0-9_]*\Z")
_APPEARANCE_BY_FINISH = {
    "pavers": "heritage_brick_stone",
    "cobble": "european_cobblestone_v1",
}


@lru_cache(maxsize=1)
def native_street_runtime_capabilities() -> tuple[PublicRealmFamilyCapability, ...]:
    data_dir = Path(__file__).resolve().parents[1] / "data"
    roster = json.loads((data_dir / "classroomStarter.json").read_text(encoding="utf-8"))
    allowed = {row["variantId"]: row for row in roster["entries"] if row["representation"] == "native-modules"}
    candidates = build_native_street_candidate_catalog(data_dir / "nativeStreetPilots.json")
    accepted = []
    for capability in candidates.capabilities:
        selection = capability.selections[0]
        release = allowed.get(selection.variant_id)
        if release is None:
            continue
        if release["archetypeId"] != selection.archetype_id or f"source_recipe:{release['revision']}" not in selection.component_set_ids:
            raise ValueError(f"Native street release lock disagrees with {selection.variant_id}")
        accepted.append(capability.model_copy(update={"title": capability.title.removeprefix("Candidate: ")}))
    if len(accepted) != len(allowed):
        raise ValueError("Classroom native street manifest is incomplete")
    return tuple(accepted)


def build_native_street_candidate_catalog(manifest_path: Path) -> PublicRealmCapabilityCatalog:
    """Compile an explicit review-only catalogue from the staged source lock."""

    rows = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or not rows:
        raise ValueError("Native street candidate manifest must be a nonempty list")
    capabilities: list[PublicRealmFamilyCapability] = []
    seen: set[str] = set()
    for row in rows:
        pilot_id = row["id"]
        parent_id = row["sourceArchetypeId"]
        if not _ID.fullmatch(pilot_id) or not _ID.fullmatch(parent_id) or pilot_id in seen:
            raise ValueError("Native street candidate identity is invalid or duplicated")
        seen.add(pilot_id)
        if row["status"] != "candidate" or resolve_public_realm_catalog_identity("street", parent_id) is None:
            raise ValueError(f"{pilot_id} is not an unpublished candidate with a trusted street parent")
        width = float(row["widthM"])
        sections = row["sections"]
        if not 5 <= width <= 60 or not isinstance(sections, list) or not sections:
            raise ValueError(f"{pilot_id} has an invalid metric section")
        edge = -width / 2
        for band in sections:
            band_width = float(band["width"])
            start = float(band["x"]) - band_width / 2
            if band_width <= 0 or abs(start - edge) > 1e-5:
                raise ValueError(f"{pilot_id} has an invalid metric section")
            edge = start + band_width
        if abs(edge - width / 2) > 1e-5:
            raise ValueError(f"{pilot_id} has an invalid metric section")
        finish = row["junctionSurface"]
        appearance = _APPEARANCE_BY_FINISH.get(finish)
        if appearance is None:
            raise ValueError(f"{pilot_id} needs an explicit reviewed appearance mapping")
        locks = [
            ("source_recipe", row["sourceRecipeSha256"]),
            ("source_assembly", row["sourceAssemblySha256"]),
            ("reference", row["referenceSha256"]),
        ]
        modules = row["modules"]
        if not isinstance(modules, dict) or not modules:
            raise ValueError(f"{pilot_id} has no native modules")
        for kind, module in sorted(modules.items()):
            if not _ID.fullmatch(kind) or module["url"] != f"/street-kits/pilots/{pilot_id}/{kind}.glb":
                raise ValueError(f"{pilot_id} has an invalid native module identity")
            locks.append((f"module_{kind}", module["sha256"]))
        if any(not _SHA256.fullmatch(value) for _, value in locks):
            raise ValueError(f"{pilot_id} has an invalid source or module hash")
        selection = PublicRealmSelectionCapability(
            archetype_id=parent_id,
            variant_id=pilot_id,
            profile_id=f"native-{pilot_id.replace('_', '-')}-v1",
            profile_version=1,
            appearance_kit_id=appearance,
            component_set_ids=tuple(f"{name}:{sha}" for name, sha in locks),
            compatibility=PublicRealmCompatibility(
                target_type="street_segment",
                nominal_row_width_m=width,
                min_row_width_m=round(width - 0.05, 3),
                max_row_width_m=round(width + 0.05, 3),
                min_length_m=8,
                max_length_m=2_000,
            ),
            is_default=True,
        )
        capabilities.append(PublicRealmFamilyCapability(
            family_id=f"street_native_{pilot_id}",
            kind="street",
            title=f"Candidate: {row['title']}",
            generator="street_section",
            selections=(selection,),
        ))
    capabilities.sort(key=lambda item: item.family_id)
    payload = [item.model_dump(mode="json") for item in capabilities]
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    variants: dict[str, tuple[str, ...]] = {}
    for item in capabilities:
        selection = item.selections[0]
        variants[selection.archetype_id] = (*variants.get(selection.archetype_id, ()), selection.variant_id)
    return PublicRealmCapabilityCatalog(
        capabilities=tuple(capabilities),
        family_ids=tuple(item.family_id for item in capabilities),
        archetype_ids=tuple(sorted(variants)),
        variants_by_archetype=variants,
        prompt_vocabulary="",  # Never advertise a review candidate to AI planning.
        fingerprint=hashlib.sha256(encoded).hexdigest(),
    )
