"""Deterministic planning catalogue derived from imported LEGO modules.

The Master Planner must never advertise a catalogue archetype merely because
it has a render card.  This module derives the smaller, executable vocabulary
from the same ``ModelLibraryEntry`` metadata consumed by the LEGO assembly
planner and proves every advertised floor count with ``plan_vertical_assembly``.

The builder is intentionally pure: callers own database access and pass the
entries visible to the project.  This keeps capability discovery reusable from
Celery tasks, API endpoints, and focused tests without introducing a session or
authorization dependency here.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable

from app.services.lego_assembly import (
    AssemblyPlanningError,
    AssemblyRequest,
    ModuleDescriptor,
    _matches_requested_archetype,
    descriptor_from_library_entry,
    plan_vertical_assembly,
)
from app.services.plan_geometry.archetypes import load_dims_table


MIN_PLANNING_FLOORS = 1
MAX_PLANNING_FLOORS = 40


@dataclass(frozen=True)
class LegoArchetypeCapability:
    """One catalogue parent backed by at least one executable LEGO family."""

    parent_id: str
    title: str
    development_type: str
    aesthetic_category: str
    target_width_m: float
    target_depth_m: float
    selectable_ids: tuple[str, ...]
    variant_ids: tuple[str, ...]
    supported_floors: tuple[int, ...]
    supported_floors_by_selectable_id: dict[str, tuple[int, ...]]
    target_dimensions_by_selectable_id: dict[str, tuple[float, float]]
    families: tuple[str, ...]


@dataclass(frozen=True)
class LegoPlanningCatalog:
    """Stable, prompt-ready summary of the installed planning vocabulary."""

    capabilities: tuple[LegoArchetypeCapability, ...]
    parent_ids: tuple[str, ...]
    variants_by_parent: dict[str, tuple[str, ...]]
    supported_floors_by_parent: dict[str, tuple[int, ...]]
    supported_floors_by_selectable_id: dict[str, tuple[int, ...]]
    target_dimensions_by_selectable_id: dict[str, tuple[float, float]]
    parent_by_selectable_id: dict[str, str]
    prompt_vocabulary: str
    fingerprint: str


@dataclass(frozen=True)
class LegoArchetypeSelection:
    """Executable parent/variant identity at one proven storey count."""

    parent_id: str
    selectable_id: str
    floors: int

    @property
    def variant_id(self) -> str | None:
        return self.selectable_id if self.selectable_id != self.parent_id else None


def select_lego_archetype(
    catalog: LegoPlanningCatalog,
    parent_id: str,
    target_floors: int | float,
    *,
    preferred_selectable_id: str | None = None,
    at_or_below: bool = False,
) -> LegoArchetypeSelection | None:
    """Choose the closest executable identity for one catalog parent.

    A modular parent alias is preferred over a variant at an equal distance;
    assembled-only families naturally select their exact source variant.  The
    optional ceiling mode is used after a zoning-height clamp and never jumps
    above that policy ceiling.
    """

    capability = next(
        (item for item in catalog.capabilities if item.parent_id == parent_id),
        None,
    )
    if capability is None:
        return None
    try:
        target_value = float(target_floors)
        target = max(1, int(target_value) if at_or_below else int(round(target_value)))
    except (TypeError, ValueError):
        target = 1

    candidates: list[tuple[int, int, str, int]] = []
    for selectable_id in capability.selectable_ids:
        for floors in capability.supported_floors_by_selectable_id.get(selectable_id, ()):
            if at_or_below and floors > target:
                continue
            preference = 0 if selectable_id == preferred_selectable_id else 1 if selectable_id == parent_id else 2
            distance = target - floors if at_or_below else abs(floors - target)
            candidates.append((distance, preference, selectable_id, floors))
    if not candidates:
        return None
    _, _, selectable_id, floors = min(candidates)
    return LegoArchetypeSelection(
        parent_id=parent_id,
        selectable_id=selectable_id,
        floors=floors,
    )


def _catalog_parent_maps() -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    entries = sorted(load_dims_table(), key=lambda entry: str(entry.get("id") or ""))
    parents = {str(entry["id"]): entry for entry in entries if entry.get("usable") and entry.get("id")}
    parent_by_id: dict[str, str] = {parent_id: parent_id for parent_id in parents}
    for parent_id, entry in parents.items():
        for variant_id in sorted(str(value) for value in (entry.get("variant_ids") or []) if value):
            # Variant ids are expected to be globally unique.  Keeping the
            # lexicographically first parent makes a malformed duplicate stable.
            parent_by_id.setdefault(variant_id, parent_id)
    return parents, parent_by_id


def _descriptor_identifiers(descriptor: ModuleDescriptor) -> set[str]:
    values = set(descriptor.archetype_ids)
    if descriptor.source_variant_id:
        values.add(descriptor.source_variant_id)
    if descriptor.generation_archetype_id:
        values.add(descriptor.generation_archetype_id)
    return {str(value).strip() for value in values if str(value).strip()}


def _assembled_exact_identifiers(descriptors: Iterable[ModuleDescriptor]) -> set[str]:
    """Identifiers an assembled-only family can honestly advertise.

    ``archetype_ids`` also contains broad parent aliases.  A fixed assembled
    landmark is executable only when its source/generation identity and native
    floor match the request, mirroring ``plan_vertical_assembly`` itself.
    """

    values: set[str] = set()
    for descriptor in descriptors:
        if descriptor.role != "assembled" or descriptor.native_floors is None:
            continue
        if descriptor.source_variant_id:
            values.add(descriptor.source_variant_id)
        if descriptor.generation_archetype_id:
            values.add(descriptor.generation_archetype_id)
    return values


def _assembled_native_dimensions(
    descriptors: Iterable[ModuleDescriptor],
    archetype_id: str,
) -> tuple[float, float] | None:
    """Return the exact plan footprint for an assembled-only selectable id."""

    matches = sorted(
        (
            descriptor
            for descriptor in descriptors
            if descriptor.role == "assembled"
            and archetype_id
            in {
                descriptor.source_variant_id,
                descriptor.generation_archetype_id,
            }
        ),
        key=lambda descriptor: (
            (
                int(descriptor.horizontal_bay_contract.get("width_bays") or 0)
                + int(descriptor.horizontal_bay_contract.get("depth_bays") or 0)
                if isinstance(descriptor.horizontal_bay_contract, dict)
                else 1_000_000
            ),
            descriptor.variant_key != "native",
            descriptor.lod,
            descriptor.id,
        ),
    )
    if not matches:
        return None
    chosen = matches[0]
    return float(chosen.width_m), float(chosen.depth_m)


def _modular_native_dimensions(
    descriptors: Iterable[ModuleDescriptor],
    archetype_id: str,
) -> tuple[float, float] | None:
    """Return the authored plan footprint for a modular selectable id.

    Catalogue-card suggestions are useful before a family is imported, but
    they are not authoritative once executable modules exist.  Planning a
    25 x 18 m cell for a 30 x 20 m podium visibly compresses facades even
    though the broad assembly safety envelope accepts it.  Prefer the podium
    explicitly tagged for this identity; a family-wide podium is safe only
    when every podium in the family has the same authored footprint.
    """

    podiums = sorted(
        (descriptor for descriptor in descriptors if descriptor.role == "podium"),
        key=lambda descriptor: (descriptor.lod, descriptor.id),
    )
    matches = [descriptor for descriptor in podiums if archetype_id in _descriptor_identifiers(descriptor)]
    if matches:
        dimensions = {(float(descriptor.width_m), float(descriptor.depth_m)) for descriptor in matches}
        return next(iter(dimensions)) if len(dimensions) == 1 else None

    dimensions = {(float(descriptor.width_m), float(descriptor.depth_m)) for descriptor in podiums}
    if len(dimensions) == 1:
        return next(iter(dimensions))
    return None


def _runtime_native_floors(
    descriptors: list[ModuleDescriptor],
    *,
    family: str,
    archetype_id: str,
    target_width_m: float,
    target_depth_m: float,
    floors: Iterable[int],
) -> tuple[int, ...]:
    """Keep only pairs the unpinned runtime planner resolves natively.

    The frontend does not send an internal family slug.  This second proof
    therefore mirrors its real request and rejects a catalogue pair if another
    matching family wins or either authored axis would move by more than 5%.
    """

    native: list[int] = []
    for floor_count in floors:
        try:
            plan = plan_vertical_assembly(
                descriptors,
                AssemblyRequest(
                    target_width_m=target_width_m,
                    target_depth_m=target_depth_m,
                    target_floors=floor_count,
                    archetype_id=archetype_id,
                    allow_setback=False,
                    footprint_profile="rectangle",
                ),
                # Catalogue probes prove real fits; forced fits would
                # advertise every floor count.
                allow_forced_fit=False,
            )
        except AssemblyPlanningError:
            continue
        fit = plan.get("fit") or {}
        if (
            plan.get("family") == family
            and abs(float(fit.get("scale_x", 0.0)) - 1.0) <= 0.05
            and abs(float(fit.get("scale_y", 0.0)) - 1.0) <= 0.05
        ):
            native.append(floor_count)
    return tuple(native)


def _supported_floors(
    descriptors: list[ModuleDescriptor],
    *,
    family: str,
    archetype_id: str,
    target_width_m: float,
    target_depth_m: float,
    probe_floors: Iterable[int],
) -> tuple[int, ...]:
    supported: list[int] = []
    for floors in probe_floors:
        try:
            plan_vertical_assembly(
                descriptors,
                AssemblyRequest(
                    target_width_m=target_width_m,
                    target_depth_m=target_depth_m,
                    target_floors=floors,
                    archetype_id=archetype_id,
                    preferred_family=family,
                    allow_setback=False,
                    footprint_profile="rectangle",
                ),
                allow_forced_fit=False,
            )
        except AssemblyPlanningError:
            continue
        supported.append(floors)
    return tuple(supported)


def _floor_summary(floors: tuple[int, ...]) -> str:
    if not floors:
        return "none"
    ranges: list[str] = []
    start = previous = floors[0]
    for floor in floors[1:]:
        if floor == previous + 1:
            previous = floor
            continue
        ranges.append(str(start) if start == previous else f"{start}-{previous}")
        start = previous = floor
    ranges.append(str(start) if start == previous else f"{start}-{previous}")
    return ", ".join(ranges)


def _prompt_vocabulary(capabilities: tuple[LegoArchetypeCapability, ...]) -> str:
    lines = ["IMPORTED LEGO BUILDING CATALOG (select only the exact identifiers listed below):"]
    if not capabilities:
        lines.append("- No executable LEGO building families are currently available.")
        return "\n".join(lines)

    for capability in capabilities:
        lines.append(
            f"- {capability.parent_id} ({capability.title}); "
            f"type={capability.development_type}; "
            f"aesthetic={capability.aesthetic_category or 'unspecified'}; "
            f"catalog_target={capability.target_width_m:g}x{capability.target_depth_m:g}m; "
            f"supported_floors={_floor_summary(capability.supported_floors)}; "
            f"selectable_ids={', '.join(capability.selectable_ids)}; "
            "selectable_targets="
            + ", ".join(
                f"{selectable_id}:{dimensions[0]:g}x{dimensions[1]:g}m"
                for selectable_id, dimensions in sorted(capability.target_dimensions_by_selectable_id.items())
            )
        )
    return "\n".join(lines)


def _fingerprint_payload(
    capabilities: tuple[LegoArchetypeCapability, ...],
) -> list[dict[str, Any]]:
    return [
        {
            "parent_id": capability.parent_id,
            "development_type": capability.development_type,
            "aesthetic_category": capability.aesthetic_category,
            "target_width_m": capability.target_width_m,
            "target_depth_m": capability.target_depth_m,
            "selectable_ids": list(capability.selectable_ids),
            "variant_ids": list(capability.variant_ids),
            "supported_floors": list(capability.supported_floors),
            "supported_floors_by_selectable_id": {
                selectable_id: list(floors)
                for selectable_id, floors in sorted(capability.supported_floors_by_selectable_id.items())
            },
            "target_dimensions_by_selectable_id": {
                selectable_id: list(dimensions)
                for selectable_id, dimensions in sorted(capability.target_dimensions_by_selectable_id.items())
            },
            "families": list(capability.families),
        }
        for capability in capabilities
    ]


def build_lego_planning_catalog(entries: Iterable[Any]) -> LegoPlanningCatalog:
    """Build the executable Master Planner vocabulary from library entries.

    Families missing a podium or roof are excluded.  A modular family without
    a repeatable floor may prove only a one-floor recipe; floors above one are
    probed only when the floor role exists.  An assembled-only family may
    contribute only its exact source/generation identifier at its native floor.
    Every exposed result is therefore backed by a successful assembly plan at
    the parent catalogue's target width and depth.
    """

    def entry_order(entry: Any) -> tuple[int, float, str]:
        created_at = getattr(entry, "created_at", None)
        timestamp = created_at.timestamp() if isinstance(created_at, datetime) else 0.0
        return (1 if isinstance(created_at, datetime) else 0, timestamp, str(entry.id))

    # Match the runtime assembly API's newest-first inventory order.  Tests and
    # offline callers without timestamps still get deterministic ID ordering.
    ordered_entries = sorted(list(entries), key=entry_order, reverse=True)
    descriptors = [
        descriptor for entry in ordered_entries if (descriptor := descriptor_from_library_entry(entry)) is not None
    ]
    by_family: dict[str, list[ModuleDescriptor]] = {}
    for descriptor in descriptors:
        by_family.setdefault(descriptor.family, []).append(descriptor)
    for family_descriptors in by_family.values():
        family_descriptors.sort(
            key=lambda item: (
                item.role,
                item.variant_key,
                item.lod,
                item.id,
            )
        )

    parents, parent_by_id = _catalog_parent_maps()
    proven_by_parent: dict[str, dict[str, Any]] = {}

    # ``by_family`` preserves the newest-first descriptor order above.  A
    # broad parent alias can occur on several revisions or stylistic families;
    # the first family is the same canonical candidate the runtime API sees.
    for family in by_family:
        family_descriptors = by_family[family]
        roles = {descriptor.role for descriptor in family_descriptors}
        modular = {"podium", "roof"}.issubset(roles)
        assembled_exact = _assembled_exact_identifiers(family_descriptors)
        if not modular and not assembled_exact:
            continue

        if modular:
            broad_candidate_ids = set().union(
                *(_descriptor_identifiers(descriptor) for descriptor in family_descriptors)
            )
            # A source/generation marker identifies a variant-specific package.
            # Its broad parent aliases are grouping metadata, not permission to
            # redefine the parent's native target. Generic modular packages
            # (with no exact marker) may own those broad identities.
            family_exact_ids = {
                identifier
                for descriptor in family_descriptors
                for identifier in (
                    descriptor.source_variant_id,
                    descriptor.generation_archetype_id,
                )
                if identifier
            }
            mapped_exact_ids = {identifier for identifier in family_exact_ids if identifier in parent_by_id}
            candidate_ids = mapped_exact_ids or broad_candidate_ids
            probe_floors: Iterable[int] = (
                range(MIN_PLANNING_FLOORS, MAX_PLANNING_FLOORS + 1) if "floor" in roles else (MIN_PLANNING_FLOORS,)
            )
        else:
            candidate_ids = assembled_exact
            mapped_exact_ids = set(assembled_exact)
            native_floors = sorted(
                {
                    int(descriptor.native_floors)
                    for descriptor in family_descriptors
                    if descriptor.role == "assembled"
                    and descriptor.native_floors is not None
                    and MIN_PLANNING_FLOORS <= int(descriptor.native_floors) <= MAX_PLANNING_FLOORS
                }
            )
            probe_floors = native_floors

        for archetype_id in sorted(candidate_ids):
            parent_id = parent_by_id.get(archetype_id)
            parent = parents.get(parent_id or "")
            if parent is None:
                continue
            # The unpinned proof below must preserve competition between every
            # family that exactly matches this selectable ID, but unrelated
            # families can never survive the runtime planner's archetype gate.
            # Pre-filter them once here instead of rescanning the complete
            # library for every one of the 40 floor-count probes.
            runtime_families = {
                descriptor.family
                for descriptor in descriptors
                if _matches_requested_archetype(descriptor, archetype_id)
            }
            runtime_descriptors = [descriptor for descriptor in descriptors if descriptor.family in runtime_families]
            # Hybrid render-locked families can carry both modular roles and
            # one exact assembled hero asset. An exact source variant must use
            # that hero asset's native footprint even when modular roles are
            # present; probing it at the parent card dimensions would merely
            # prove that a broad 45%-175% landmark squash is technically legal.
            native_dimensions = _assembled_native_dimensions(
                family_descriptors, archetype_id
            ) or _modular_native_dimensions(family_descriptors, archetype_id)
            if native_dimensions is None:
                continue
            target_width_m, target_depth_m = native_dimensions
            supported = _supported_floors(
                family_descriptors,
                family=family,
                archetype_id=archetype_id,
                target_width_m=target_width_m,
                target_depth_m=target_depth_m,
                probe_floors=probe_floors,
            )
            supported = _runtime_native_floors(
                runtime_descriptors,
                family=family,
                archetype_id=archetype_id,
                target_width_m=target_width_m,
                target_depth_m=target_depth_m,
                floors=supported,
            )
            if not supported:
                continue

            aggregate = proven_by_parent.setdefault(
                parent_id,
                {
                    "ids": set(),
                    "variants": set(),
                    "floors": set(),
                    "floors_by_id": {},
                    "dimensions_by_id": {},
                    "families": set(),
                    "exact_ids": set(),
                    "family_by_id": {},
                },
            )
            # One selectable ID has one target footprint and one floor set in
            # the public contract.  Never union floors from another family at
            # a different native size: that advertised a dimension/floor pair
            # which the unpinned runtime planner could satisfy only by visibly
            # stretching a different family.  Exact source variants remain
            # separate selectable IDs and therefore keep their own families.
            if archetype_id in aggregate["ids"]:
                continue
            aggregate["ids"].add(archetype_id)
            if archetype_id in mapped_exact_ids:
                aggregate["exact_ids"].add(archetype_id)
            if archetype_id != parent_id:
                aggregate["variants"].add(archetype_id)
            aggregate["floors"].update(supported)
            aggregate["floors_by_id"][archetype_id] = set(supported)
            aggregate["dimensions_by_id"][archetype_id] = (
                target_width_m,
                target_depth_m,
            )
            aggregate["families"].add(family)
            aggregate["family_by_id"][archetype_id] = family

    # When audited exact variants exist, the broad parent remains the grouping
    # identity but is not itself selectable. This makes deterministic/fallback
    # plans choose a concrete high-fidelity asset rather than an older generic
    # family carrying the same parent alias.
    for parent_id, aggregate in proven_by_parent.items():
        exact_variants = aggregate["exact_ids"] - {parent_id}
        if exact_variants and parent_id in aggregate["ids"]:
            aggregate["ids"].remove(parent_id)
            aggregate["floors_by_id"].pop(parent_id, None)
            aggregate["dimensions_by_id"].pop(parent_id, None)
            aggregate["family_by_id"].pop(parent_id, None)
        aggregate["floors"] = {
            floor for selectable_id in aggregate["ids"] for floor in aggregate["floors_by_id"][selectable_id]
        }
        aggregate["families"] = {aggregate["family_by_id"][selectable_id] for selectable_id in aggregate["ids"]}

    capabilities_list: list[LegoArchetypeCapability] = []
    for parent_id, aggregate in sorted(proven_by_parent.items()):
        parent_target = aggregate["dimensions_by_id"].get(parent_id)
        if parent_target is None:
            first_selectable_id = min(aggregate["dimensions_by_id"])
            parent_target = aggregate["dimensions_by_id"][first_selectable_id]
        capabilities_list.append(
            LegoArchetypeCapability(
                parent_id=parent_id,
                title=str(parents[parent_id].get("title") or parent_id),
                development_type=str(parents[parent_id].get("development_type") or ""),
                aesthetic_category=str(parents[parent_id].get("aesthetic_category") or ""),
                target_width_m=float(parent_target[0]),
                target_depth_m=float(parent_target[1]),
                selectable_ids=tuple(sorted(aggregate["ids"])),
                variant_ids=tuple(sorted(aggregate["variants"])),
                supported_floors=tuple(sorted(aggregate["floors"])),
                supported_floors_by_selectable_id={
                    selectable_id: tuple(sorted(floors))
                    for selectable_id, floors in sorted(aggregate["floors_by_id"].items())
                },
                target_dimensions_by_selectable_id={
                    selectable_id: tuple(dimensions)
                    for selectable_id, dimensions in sorted(aggregate["dimensions_by_id"].items())
                },
                families=tuple(sorted(aggregate["families"])),
            )
        )
    capabilities = tuple(capabilities_list)
    parent_ids = tuple(capability.parent_id for capability in capabilities)
    variants_by_parent = {capability.parent_id: capability.variant_ids for capability in capabilities}
    supported_floors_by_parent = {capability.parent_id: capability.supported_floors for capability in capabilities}
    supported_floors_by_selectable_id = {
        selectable_id: floors
        for capability in capabilities
        for selectable_id, floors in capability.supported_floors_by_selectable_id.items()
    }
    target_dimensions_by_selectable_id = {
        selectable_id: dimensions
        for capability in capabilities
        for selectable_id, dimensions in (capability.target_dimensions_by_selectable_id.items())
    }
    parent_by_selectable_id = {
        selectable_id: capability.parent_id
        for capability in capabilities
        for selectable_id in capability.selectable_ids
    }
    prompt_vocabulary = _prompt_vocabulary(capabilities)
    canonical = json.dumps(
        _fingerprint_payload(capabilities),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    fingerprint = hashlib.sha256(canonical).hexdigest()

    return LegoPlanningCatalog(
        capabilities=capabilities,
        parent_ids=parent_ids,
        variants_by_parent=variants_by_parent,
        supported_floors_by_parent=supported_floors_by_parent,
        supported_floors_by_selectable_id=supported_floors_by_selectable_id,
        target_dimensions_by_selectable_id=target_dimensions_by_selectable_id,
        parent_by_selectable_id=parent_by_selectable_id,
        prompt_vocabulary=prompt_vocabulary,
        fingerprint=fingerprint,
    )


__all__ = [
    "LegoArchetypeCapability",
    "LegoArchetypeSelection",
    "LegoPlanningCatalog",
    "build_lego_planning_catalog",
    "select_lego_archetype",
]
