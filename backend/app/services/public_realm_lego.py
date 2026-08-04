"""Versioned, executable Public Realm LEGO capability and recipe contract.

The visual catalog is intentionally much larger than the finite cohort that
has passed metric and live-3D review.  This module advertises only that smaller
executable vocabulary to AI planning and produces a canonical, persistable
recipe for every accepted target.  Manual/legacy public-realm zones may still
use the historical procedural renderer; callers decide whether an unsupported
selection is an error by passing ``strict=True`` to
``plan_public_realm_zone_recipe``.

This is backend-owned source data rather than a runtime import from frontend
TypeScript.  It keeps Celery/API consumers deterministic and makes a catalog
revision an explicit code review instead of an accidental UI-data change.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Annotated, Any, Iterable, Literal

from pydantic import BaseModel, ConfigDict, Field
from shapely.geometry.base import BaseGeometry

from app.services.site_engine import (
    WGS84_CRS,
    build_transformer,
    local_metric_crs_for_polygon,
    project_geometry,
)


PUBLIC_REALM_RECIPE_PROPERTY = "public_realm_lego"
PUBLIC_REALM_SCHEMA_VERSION = 1
PUBLIC_REALM_FAMILY_VERSION = 1

PublicRealmKind = Literal["park", "street"]
PublicRealmGenerator = Literal["park_kit", "street_section"]
PublicRealmPlanningErrorCode = Literal["family_not_found", "family_incompatible"]


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ParkPolygonTarget(_FrozenModel):
    target_type: Literal["park_polygon"] = "park_polygon"
    width_m: float = Field(gt=0)
    depth_m: float = Field(gt=0)
    area_m2: float = Field(gt=0)


class StreetSegmentTarget(_FrozenModel):
    target_type: Literal["street_segment"] = "street_segment"
    row_width_m: float = Field(gt=0)
    length_m: float = Field(gt=0)


class StreetNodeTarget(_FrozenModel):
    target_type: Literal["street_node"] = "street_node"
    approach_row_width_m: float = Field(gt=0)
    diameter_m: float = Field(gt=0)
    arm_count: int = Field(ge=3, le=8)


PublicRealmTarget = Annotated[
    ParkPolygonTarget | StreetSegmentTarget | StreetNodeTarget,
    Field(discriminator="target_type"),
]


class PublicRealmCompatibility(_FrozenModel):
    """Metric target envelope for one exact source archetype."""

    target_type: Literal["park_polygon", "street_segment", "street_node"]
    nominal_width_m: float | None = Field(default=None, gt=0)
    nominal_depth_m: float | None = Field(default=None, gt=0)
    min_width_m: float | None = Field(default=None, gt=0)
    max_width_m: float | None = Field(default=None, gt=0)
    min_depth_m: float | None = Field(default=None, gt=0)
    max_depth_m: float | None = Field(default=None, gt=0)
    min_area_m2: float | None = Field(default=None, gt=0)
    max_area_m2: float | None = Field(default=None, gt=0)
    min_aspect_ratio: float | None = Field(default=None, gt=1)
    nominal_row_width_m: float | None = Field(default=None, gt=0)
    min_row_width_m: float | None = Field(default=None, gt=0)
    max_row_width_m: float | None = Field(default=None, gt=0)
    min_length_m: float | None = Field(default=None, gt=0)
    max_length_m: float | None = Field(default=None, gt=0)
    min_diameter_m: float | None = Field(default=None, gt=0)
    max_diameter_m: float | None = Field(default=None, gt=0)
    supported_arm_counts: tuple[int, ...] = ()
    allow_quarter_turn: bool = False


class PublicRealmSelectionCapability(_FrozenModel):
    """One exact catalog identity with an executable geometry/appearance recipe."""

    archetype_id: str = Field(min_length=1)
    variant_id: str = Field(min_length=1)
    profile_id: str = Field(min_length=1)
    profile_version: int = Field(ge=1)
    appearance_kit_id: str = Field(min_length=1)
    planting_structure: str | None = None
    component_set_ids: tuple[str, ...] = ()
    compatibility: PublicRealmCompatibility
    is_default: bool = False


class PublicRealmFamilyCapability(_FrozenModel):
    family_id: str = Field(min_length=1)
    family_version: int = Field(default=PUBLIC_REALM_FAMILY_VERSION, ge=1)
    kind: PublicRealmKind
    title: str = Field(min_length=1)
    generator: PublicRealmGenerator
    terrain_policy: Literal["terrain_drape_and_metric_assemblies"] = "terrain_drape_and_metric_assemblies"
    selections: tuple[PublicRealmSelectionCapability, ...]


class PublicRealmPlanRequest(_FrozenModel):
    archetype_id: str = Field(min_length=1)
    variant_id: str | None = None
    target: PublicRealmTarget
    preferred_family_id: str | None = None


class PublicRealmRecipePayload(_FrozenModel):
    """JSON-safe representation persisted on ``SiteZone.properties``."""

    schema_version: Literal[1] = PUBLIC_REALM_SCHEMA_VERSION
    family_id: str = Field(min_length=1)
    family_version: int = Field(ge=1)
    kind: PublicRealmKind
    generator: PublicRealmGenerator
    archetype_id: str = Field(min_length=1)
    variant_id: str = Field(min_length=1)
    profile_id: str = Field(min_length=1)
    profile_version: int = Field(ge=1)
    appearance_kit_id: str = Field(min_length=1)
    planting_structure: str | None = None
    component_set_ids: tuple[str, ...] = ()
    terrain_policy: Literal["terrain_drape_and_metric_assemblies"]
    target: PublicRealmTarget
    catalog_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    capability_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    recipe_hash: str = Field(pattern=r"^[a-f0-9]{64}$")


@dataclass(frozen=True)
class PublicRealmCapabilityCatalog:
    capabilities: tuple[PublicRealmFamilyCapability, ...]
    family_ids: tuple[str, ...]
    archetype_ids: tuple[str, ...]
    variants_by_archetype: dict[str, tuple[str, ...]]
    prompt_vocabulary: str
    fingerprint: str


class PublicRealmPlanningError(ValueError):
    """Stable API-facing failure with renderer-neutral compatibility details."""

    def __init__(
        self,
        message: str,
        *,
        code: PublicRealmPlanningErrorCode,
        requested: dict[str, Any],
        supported_families: list[dict[str, Any]],
        violations: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.requested = requested
        self.supported_families = supported_families
        self.violations = violations or []

    def as_detail(self) -> dict[str, Any]:
        detail: dict[str, Any] = {
            "code": self.code,
            "message": str(self),
            "requested": self.requested,
            "supported_families": self.supported_families,
        }
        if self.violations:
            detail["violations"] = self.violations
        return detail


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _park_envelope(
    *,
    nominal: tuple[float, float],
    width: tuple[float, float],
    depth: tuple[float, float],
    area: tuple[float, float],
    min_aspect_ratio: float | None = None,
) -> PublicRealmCompatibility:
    return PublicRealmCompatibility(
        target_type="park_polygon",
        nominal_width_m=nominal[0],
        nominal_depth_m=nominal[1],
        min_width_m=width[0],
        max_width_m=width[1],
        min_depth_m=depth[0],
        max_depth_m=depth[1],
        min_area_m2=area[0],
        max_area_m2=area[1],
        min_aspect_ratio=min_aspect_ratio,
        allow_quarter_turn=True,
    )


def _segment_envelope(
    *,
    nominal_row_m: float,
    row: tuple[float, float],
    length: tuple[float, float] = (0.25, 2_000.0),
) -> PublicRealmCompatibility:
    return PublicRealmCompatibility(
        target_type="street_segment",
        nominal_row_width_m=nominal_row_m,
        min_row_width_m=row[0],
        max_row_width_m=row[1],
        min_length_m=length[0],
        max_length_m=length[1],
    )


def _node_envelope(
    *,
    nominal_row_m: float,
    row: tuple[float, float],
    diameter: tuple[float, float],
    arm_counts: tuple[int, ...],
) -> PublicRealmCompatibility:
    return PublicRealmCompatibility(
        target_type="street_node",
        nominal_row_width_m=nominal_row_m,
        min_row_width_m=row[0],
        max_row_width_m=row[1],
        min_diameter_m=diameter[0],
        max_diameter_m=diameter[1],
        supported_arm_counts=arm_counts,
    )


def _selection(
    archetype_id: str,
    variant_id: str,
    *,
    profile_id: str,
    appearance_kit_id: str,
    compatibility: PublicRealmCompatibility,
    planting_structure: str | None = None,
    components: tuple[str, ...],
    default: bool = False,
) -> PublicRealmSelectionCapability:
    try:
        profile_version = int(profile_id.rsplit("-v", 1)[1])
    except (IndexError, ValueError):
        profile_version = 1
    return PublicRealmSelectionCapability(
        archetype_id=archetype_id,
        variant_id=variant_id,
        profile_id=profile_id,
        profile_version=profile_version,
        appearance_kit_id=appearance_kit_id,
        planting_structure=planting_structure,
        component_set_ids=components,
        compatibility=compatibility,
        is_default=default,
    )


_POCKET_ENVELOPE = _park_envelope(
    nominal=(30.0, 30.0),
    # The executable family intentionally covers both freestanding pocket
    # parks and clipped/L-shaped internal courtyards.  Courtyard bounding
    # boxes can be much broader than their landscaped area without asking the
    # procedural kit to stretch any fixed component.
    width=(8.0, 100.0),
    depth=(8.0, 100.0),
    area=(64.0, 3_600.0),
)
_NEIGHBORHOOD_ENVELOPE = _park_envelope(
    nominal=(100.0, 80.0),
    width=(30.0, 200.0),
    depth=(25.0, 160.0),
    area=(1_000.0, 32_000.0),
)
_COMMUNITY_ENVELOPE = _park_envelope(
    nominal=(250.0, 160.0),
    width=(80.0, 400.0),
    depth=(60.0, 250.0),
    area=(6_000.0, 100_000.0),
)
_CIVIC_PLAZA_ENVELOPE = _park_envelope(
    nominal=(80.0, 75.0),
    width=(40.0, 150.0),
    depth=(35.0, 140.0),
    area=(1_400.0, 21_000.0),
)
_LINEAR_GREENWAY_ENVELOPE = _park_envelope(
    nominal=(400.0, 30.0),
    # A compact community can still carry a real end-to-end greenway.  The
    # V1 kit is parametric along its principal axis, so 60 m is its reviewed
    # lower bound.  Requiring a 3:1 aspect ratio keeps square pond-garden
    # lobes out of this family even when their area is otherwise sufficient.
    width=(60.0, 1_000.0),
    depth=(12.0, 60.0),
    area=(750.0, 60_000.0),
    min_aspect_ratio=3.0,
)
_STORMWATER_ENVELOPE = _park_envelope(
    nominal=(60.0, 40.0),
    width=(20.0, 120.0),
    depth=(15.0, 80.0),
    area=(300.0, 9_600.0),
)

_PARK_COMPONENTS = (
    "park_ground_program_v1",
    "landscape_instances_v1",
    "public_realm_furnishings_v1",
)
_STREET_COMPONENTS = (
    "street_metric_bands_v1",
    "street_edges_markings_v1",
    "public_realm_furnishings_v1",
)


def _park_variants(
    archetype_id: str,
    *,
    profile_id: str,
    compatibility: PublicRealmCompatibility,
    appearances: tuple[str, str, str, str],
    structures: tuple[str, str, str, str],
) -> tuple[PublicRealmSelectionCapability, ...]:
    return tuple(
        _selection(
            archetype_id,
            f"{archetype_id}_v{index}",
            profile_id=profile_id,
            appearance_kit_id=appearance,
            planting_structure=structures[index],
            compatibility=compatibility,
            components=_PARK_COMPONENTS,
            default=index == 0,
        )
        for index, appearance in enumerate(appearances)
    )


_DISTRICT_APPEARANCE_KITS = (
    "calgary_contemporary_native",
    "heritage_brick_stone",
    "timber_biophilic",
    "industrial_adaptive_reuse",
)

# Street-card variant numbers are local to each archetype.  They are not a
# district-palette index: for example, v0 means Classic Tree-Lined on both the
# approved Main Street and Narrow Residential cards, while it means Dutch
# Woonerf on the Yield Street card.  Keep this mapping explicit so adding or
# reordering a shared palette can never silently change a selected street's
# visual identity.
_STREET_APPEARANCE_KITS_BY_ARCHETYPE: dict[str, tuple[str, ...]] = {
    "main_street_complete": (
        "classic_tree_lined_v1",
        "modern_minimalist_v1",
        "european_cobblestone_v1",
        "tropical_boulevard_v1",
    ),
    "narrow_residential_street": (
        "classic_tree_lined_v1",
        "modern_minimalist_v1",
        "european_cobblestone_v1",
        "tropical_boulevard_v1",
    ),
    "yield_street": ("dutch_woonerf_v1",),
    "woonerf_shared_street": ("dutch_woonerf_v1",),
    # The source card and the render-locked V1 cohort expose only the Street
    # Manual identity.  Historical backend catalogs accidentally synthesized
    # v1-v3 by applying the generic district palette.
    "calgary_local": ("calgary_contemporary_native",),
    # The green-alley V1 render lock is the permeable planted corridor.  The
    # other source-card variants remain manual/legacy until their own kits are
    # reviewed rather than borrowing unrelated district-building identities.
    "green_alley": ("green_corridor_v1",),
    # Traditional service-lane v0 is intentionally neutral.  Of the existing
    # reviewed kits, the contemporary local-street palette makes the fewest
    # unsupported claims about heritage, timber, or industrial character.
    "toronto_laneway": ("calgary_contemporary_native",),
}


# These exact IDs were advertised by an earlier executable catalog even
# though no matching visual kit existed.  Existing AI plans can therefore
# legitimately contain them.  Community 3D compilation migrates only this
# finite historical set to the reviewed default; every other unknown variant
# must continue to fail closed.
_LEGACY_STREET_VARIANT_NORMALIZATION: dict[tuple[str, str], str] = {
    **{("yield_street", f"yield_street_v{index}"): "yield_street_v0" for index in range(1, 4)},
    **{
        ("woonerf_shared_street", f"woonerf_shared_street_v{index}"): "woonerf_shared_street_v0"
        for index in range(1, 4)
    },
    **{("calgary_local", f"calgary_local_v{index}"): "calgary_local_v0" for index in range(1, 4)},
    **{("green_alley", f"green_alley_v{index}"): "green_alley_v0" for index in range(1, 4)},
    **{("toronto_laneway", f"toronto_laneway_v{index}"): "toronto_laneway_v0" for index in range(1, 4)},
}


def normalize_legacy_ai_street_variant_properties(
    properties: dict[str, Any] | None,
) -> tuple[dict[str, Any], str | None]:
    """Normalize one formerly advertised, unbuilt AI street variant.

    Returns a copy plus the migrated source variant ID.  Callers deliberately
    opt into this compatibility path only for saved AI-plan zones; the core
    recipe planner remains strict and never accepts these retired identities.
    """

    normalized = dict(properties or {})
    archetype_id = str(normalized.get("road_archetype_id") or "").strip()
    variant_id = str(normalized.get("road_selected_variant_id") or "").strip()
    canonical_variant_id = _LEGACY_STREET_VARIANT_NORMALIZATION.get((archetype_id, variant_id))
    if canonical_variant_id is None:
        return normalized, None
    normalized["road_selected_variant_id"] = canonical_variant_id
    return normalized, variant_id


def _street_variants(
    archetype_id: str,
    *,
    profile_id: str,
    compatibility: PublicRealmCompatibility,
    components: tuple[str, ...] = _STREET_COMPONENTS,
) -> tuple[PublicRealmSelectionCapability, ...]:
    """Four explicit card appearances over one authoritative metric section."""

    appearance_kits = _STREET_APPEARANCE_KITS_BY_ARCHETYPE.get(
        archetype_id,
        _DISTRICT_APPEARANCE_KITS,
    )

    return tuple(
        _selection(
            archetype_id,
            f"{archetype_id}_v{index}",
            profile_id=profile_id,
            appearance_kit_id=appearance_kit_id,
            compatibility=compatibility,
            components=components,
            default=index == 0,
        )
        for index, appearance_kit_id in enumerate(appearance_kits)
    )


_CAPABILITIES: tuple[PublicRealmFamilyCapability, ...] = (
    PublicRealmFamilyCapability(
        family_id="park_pocket_courtyard",
        kind="park",
        title="Pocket Park / Courtyard",
        generator="park_kit",
        selections=_park_variants(
            "urban_pocket_park",
            profile_id="urban-pocket-park-v1",
            compatibility=_POCKET_ENVELOPE,
            appearances=(
                "rustic_timber_gravel_v1",
                "modern_steel_turf_v1",
                "natural_meadow_v1",
                "urban_contemporary_v1",
            ),
            structures=(
                "garden_courtyard",
                "formal_quad",
                "naturalistic_grove",
                "garden_courtyard",
            ),
        ),
    ),
    PublicRealmFamilyCapability(
        family_id="park_neighborhood_community",
        kind="park",
        title="Neighborhood / Community Park",
        generator="park_kit",
        selections=(
            *_park_variants(
                "neighborhood_park",
                profile_id="neighborhood-park-v4",
                compatibility=_NEIGHBORHOOD_ENVELOPE,
                appearances=(
                    "rustic_timber_gravel_v1",
                    "modern_steel_turf_v1",
                    "natural_meadow_v1",
                    "urban_contemporary_v1",
                ),
                structures=(
                    "active_recreation",
                    "active_recreation",
                    "naturalistic_grove",
                    "active_recreation",
                ),
            ),
            *_park_variants(
                "community_park",
                profile_id="community-park-lego-v1",
                compatibility=_COMMUNITY_ENVELOPE,
                appearances=(
                    "english_pastoral_v1",
                    "modern_minimalist_v1",
                    "mediterranean_xeriscape_v1",
                    "tropical_lush_v1",
                ),
                structures=(
                    "naturalistic_grove",
                    "active_recreation",
                    "naturalistic_grove",
                    "naturalistic_grove",
                ),
            ),
        ),
    ),
    PublicRealmFamilyCapability(
        family_id="park_civic_plaza",
        kind="park",
        title="Civic Plaza",
        generator="park_kit",
        selections=(
            _selection(
                "formal_civic_plaza",
                "formal_civic_plaza_v0",
                profile_id="formal-civic-plaza-v1",
                appearance_kit_id="neoclassical_stone_v1",
                planting_structure="paved_plaza",
                compatibility=_CIVIC_PLAZA_ENVELOPE,
                components=(
                    "civic_plaza_ground_program_v1",
                    "civic_fountain_assembly_v1",
                    "public_realm_furnishings_v1",
                ),
                default=True,
            ),
        ),
    ),
    PublicRealmFamilyCapability(
        family_id="park_linear_greenway",
        kind="park",
        title="Linear Greenway",
        generator="park_kit",
        selections=(
            _selection(
                "linear_park_greenway",
                "linear_park_greenway_v0",
                profile_id="linear-park-greenway-v1",
                appearance_kit_id="rail_trail_v1",
                planting_structure="naturalistic_grove",
                compatibility=_LINEAR_GREENWAY_ENVELOPE,
                components=(
                    "linear_greenway_ground_program_v1",
                    "trail_edges_markings_v1",
                    "landscape_instances_v1",
                ),
                default=True,
            ),
        ),
    ),
    PublicRealmFamilyCapability(
        family_id="park_water_ecology",
        kind="park",
        title="Water Ecology / Resilience",
        generator="park_kit",
        selections=(
            _selection(
                "stormwater_retention_pond",
                "stormwater_retention_pond_v0",
                profile_id="stormwater-retention-pond-v1",
                appearance_kit_id="naturalistic_pond_v1",
                planting_structure="reservoir_perimeter",
                compatibility=_STORMWATER_ENVELOPE,
                components=(
                    "stormwater_ground_program_v1",
                    "water_control_assemblies_v1",
                    "landscape_instances_v1",
                ),
                default=True,
            ),
        ),
    ),
    PublicRealmFamilyCapability(
        family_id="street_local_public_realm",
        kind="street",
        title="Local Public Realm",
        generator="street_section",
        selections=(
            *_street_variants(
                "yield_street",
                profile_id="yield-street-v1",
                compatibility=_segment_envelope(nominal_row_m=6, row=(6, 10)),
            ),
            *_street_variants(
                "narrow_residential_street",
                profile_id="narrow-residential-street-v1",
                compatibility=_segment_envelope(nominal_row_m=10, row=(9, 15)),
            ),
            *_street_variants(
                "woonerf_shared_street",
                profile_id="woonerf-shared-street-v1",
                compatibility=_segment_envelope(nominal_row_m=10, row=(6, 14)),
            ),
            *_street_variants(
                "calgary_local",
                profile_id="calgary-local-v1",
                compatibility=_segment_envelope(nominal_row_m=16, row=(14, 18)),
            ),
            *_street_variants(
                "green_alley",
                profile_id="green-alley-v1",
                compatibility=_segment_envelope(nominal_row_m=5, row=(3.5, 7)),
            ),
            _selection(
                "multi_use_trail",
                "multi_use_trail_v1",
                profile_id="multi-use-trail-v1",
                appearance_kit_id="green_corridor_v1",
                compatibility=_segment_envelope(nominal_row_m=4, row=(3.9, 4.1)),
                components=(
                    "trail_metric_surface_v1",
                    "trail_edges_markings_v1",
                    "public_realm_furnishings_v1",
                ),
                default=True,
            ),
            *_street_variants(
                "toronto_laneway",
                profile_id="toronto-laneway-v1",
                compatibility=_segment_envelope(nominal_row_m=5, row=(5, 7)),
            ),
        ),
    ),
    PublicRealmFamilyCapability(
        family_id="street_complete_main_18m",
        kind="street",
        title="Render-Locked 18 m Complete Main Street",
        generator="street_section",
        selections=_street_variants(
            "main_street_complete",
            profile_id="complete-main-18m-v1",
            compatibility=_segment_envelope(
                nominal_row_m=18,
                row=(17.95, 18.05),
                length=(8, 2_000),
            ),
            components=(
                "complete_main_18m_bands_v1",
                "street_edges_markings_v1",
                "commercial_public_realm_v1",
            ),
        ),
    ),
    # Compatibility family for already-authored 22 m polygons.  New requests
    # resolve to the canonical 18 m family above; an exact 22 m source can
    # still be rebuilt instead of becoming an unrenderable orphan.  Retaining
    # the historical family ID is deliberate migration compatibility.
    PublicRealmFamilyCapability(
        family_id="street_complete_main_22m",
        kind="street",
        title="Legacy 22 m Complete Main Street",
        generator="street_section",
        selections=_street_variants(
            "main_street_complete",
            profile_id="complete-main-22m-v1",
            compatibility=_segment_envelope(
                nominal_row_m=22,
                row=(21.95, 22.05),
                length=(8, 2_000),
            ),
            components=(
                "complete_main_22m_bands_v1",
                "street_edges_markings_v1",
                "commercial_public_realm_v1",
            ),
        ),
    ),
    PublicRealmFamilyCapability(
        family_id="street_four_way_intersection",
        kind="street",
        title="Four-Way Intersection",
        generator="street_section",
        selections=(
            _selection(
                "protected_intersection",
                "protected_intersection_v0",
                profile_id="four-way-intersection-v1",
                appearance_kit_id="dutch_corner_islands_v1",
                compatibility=_node_envelope(
                    nominal_row_m=22,
                    row=(18, 30),
                    diameter=(18, 50),
                    arm_counts=(4,),
                ),
                components=(
                    "four_way_node_geometry_v1",
                    "accessible_crossings_v1",
                    "street_signals_markings_v1",
                ),
                default=True,
            ),
        ),
    ),
    PublicRealmFamilyCapability(
        family_id="street_compact_roundabout",
        kind="street",
        title="Compact Roundabout",
        generator="street_section",
        selections=(
            _selection(
                "roundabout",
                "roundabout_v0",
                profile_id="compact-roundabout-v1",
                appearance_kit_id="classic_tree_lined_v1",
                compatibility=_node_envelope(
                    nominal_row_m=22,
                    row=(14, 34),
                    diameter=(20, 45),
                    arm_counts=(4,),
                ),
                components=(
                    "compact_roundabout_geometry_v1",
                    "roundabout_approach_markings_v1",
                    "landscape_instances_v1",
                ),
                default=True,
            ),
        ),
    ),
)


def public_realm_capability_fingerprint(
    capability: PublicRealmFamilyCapability,
) -> str:
    return _sha256(capability.model_dump(mode="json"))


def _catalog_prompt(capabilities: tuple[PublicRealmFamilyCapability, ...]) -> str:
    lines = ["EXECUTABLE PUBLIC REALM LEGO CATALOG " "(select only exact archetype and variant identifiers below):"]
    if not capabilities:
        return lines[0] + "\n- No executable public-realm families are available."
    for capability in capabilities:
        sources: dict[str, list[str]] = {}
        for selection in capability.selections:
            sources.setdefault(selection.archetype_id, []).append(selection.variant_id)
        source_text = "; ".join(
            f"{archetype_id}=[{', '.join(sorted(variants))}]" for archetype_id, variants in sorted(sources.items())
        )
        lines.append(
            f"- {capability.family_id}@{capability.family_version}; " f"kind={capability.kind}; sources={source_text}"
        )
    return "\n".join(lines)


def build_public_realm_capability_catalog(
    *,
    kinds: Iterable[PublicRealmKind] | None = None,
    family_ids: Iterable[str] | None = None,
) -> PublicRealmCapabilityCatalog:
    """Return a stable filtered view of the reviewed executable cohort."""

    allowed_kinds = set(kinds) if kinds is not None else None
    allowed_families = set(family_ids) if family_ids is not None else None
    capabilities = tuple(
        sorted(
            (
                capability
                for capability in _CAPABILITIES
                if (allowed_kinds is None or capability.kind in allowed_kinds)
                and (allowed_families is None or capability.family_id in allowed_families)
            ),
            key=lambda capability: capability.family_id,
        )
    )
    variants_by_archetype: dict[str, tuple[str, ...]] = {}
    for archetype_id in sorted(
        {selection.archetype_id for capability in capabilities for selection in capability.selections}
    ):
        variants_by_archetype[archetype_id] = tuple(
            sorted(
                {
                    selection.variant_id
                    for capability in capabilities
                    for selection in capability.selections
                    if selection.archetype_id == archetype_id
                }
            )
        )
    payload = [capability.model_dump(mode="json") for capability in capabilities]
    return PublicRealmCapabilityCatalog(
        capabilities=capabilities,
        family_ids=tuple(capability.family_id for capability in capabilities),
        archetype_ids=tuple(variants_by_archetype),
        variants_by_archetype=variants_by_archetype,
        prompt_vocabulary=_catalog_prompt(capabilities),
        fingerprint=_sha256(payload),
    )


def _family_summary(capability: PublicRealmFamilyCapability) -> dict[str, Any]:
    return {
        "family_id": capability.family_id,
        "family_version": capability.family_version,
        "kind": capability.kind,
        "archetype_ids": sorted({selection.archetype_id for selection in capability.selections}),
        "variant_ids": sorted({selection.variant_id for selection in capability.selections}),
    }


def _request_payload(request: PublicRealmPlanRequest) -> dict[str, Any]:
    return request.model_dump(mode="json", exclude_none=True)


def _in_range(value: float, lower: float | None, upper: float | None) -> bool:
    return (lower is None or value >= lower) and (upper is None or value <= upper)


def _compatibility_violations(
    target: PublicRealmTarget,
    envelope: PublicRealmCompatibility,
) -> list[dict[str, Any]]:
    if target.target_type != envelope.target_type:
        return [
            {
                "field": "target.target_type",
                "requested": target.target_type,
                "supported": envelope.target_type,
            }
        ]

    violations: list[dict[str, Any]] = []
    if isinstance(target, ParkPolygonTarget):
        orientations = [(target.width_m, target.depth_m)]
        if envelope.allow_quarter_turn:
            orientations.append((target.depth_m, target.width_m))
        axes_fit = any(
            _in_range(width, envelope.min_width_m, envelope.max_width_m)
            and _in_range(depth, envelope.min_depth_m, envelope.max_depth_m)
            for width, depth in orientations
        )
        if not axes_fit:
            violations.append(
                {
                    "field": "target.footprint_m",
                    "requested": [target.width_m, target.depth_m],
                    "supported": {
                        "width_m": [envelope.min_width_m, envelope.max_width_m],
                        "depth_m": [envelope.min_depth_m, envelope.max_depth_m],
                        "quarter_turn": envelope.allow_quarter_turn,
                    },
                }
            )
        if not _in_range(target.area_m2, envelope.min_area_m2, envelope.max_area_m2):
            violations.append(
                {
                    "field": "target.area_m2",
                    "requested": target.area_m2,
                    "supported": [envelope.min_area_m2, envelope.max_area_m2],
                }
            )
        aspect_ratio = max(target.width_m, target.depth_m) / min(
            target.width_m,
            target.depth_m,
        )
        if envelope.min_aspect_ratio is not None and aspect_ratio < envelope.min_aspect_ratio:
            violations.append(
                {
                    "field": "target.aspect_ratio",
                    "requested": round(aspect_ratio, 3),
                    "supported": {"min": envelope.min_aspect_ratio},
                }
            )
    elif isinstance(target, StreetSegmentTarget):
        if not _in_range(
            target.row_width_m,
            envelope.min_row_width_m,
            envelope.max_row_width_m,
        ):
            violations.append(
                {
                    "field": "target.row_width_m",
                    "requested": target.row_width_m,
                    "supported": [envelope.min_row_width_m, envelope.max_row_width_m],
                }
            )
        if not _in_range(target.length_m, envelope.min_length_m, envelope.max_length_m):
            violations.append(
                {
                    "field": "target.length_m",
                    "requested": target.length_m,
                    "supported": [envelope.min_length_m, envelope.max_length_m],
                }
            )
    else:
        if not _in_range(
            target.approach_row_width_m,
            envelope.min_row_width_m,
            envelope.max_row_width_m,
        ):
            violations.append(
                {
                    "field": "target.approach_row_width_m",
                    "requested": target.approach_row_width_m,
                    "supported": [envelope.min_row_width_m, envelope.max_row_width_m],
                }
            )
        if not _in_range(target.diameter_m, envelope.min_diameter_m, envelope.max_diameter_m):
            violations.append(
                {
                    "field": "target.diameter_m",
                    "requested": target.diameter_m,
                    "supported": [envelope.min_diameter_m, envelope.max_diameter_m],
                }
            )
        if envelope.supported_arm_counts and target.arm_count not in envelope.supported_arm_counts:
            violations.append(
                {
                    "field": "target.arm_count",
                    "requested": target.arm_count,
                    "supported": list(envelope.supported_arm_counts),
                }
            )
    return violations


def _normalized_target(target: PublicRealmTarget) -> PublicRealmTarget:
    values = target.model_dump(mode="json")
    for key, value in tuple(values.items()):
        if isinstance(value, float):
            values[key] = round(value, 3)
    return type(target).model_validate(values)


def public_realm_recipe_hash(recipe: PublicRealmRecipePayload | dict[str, Any]) -> str:
    """Hash every canonical recipe field except the self-verifying hash itself."""

    payload = (
        recipe.model_dump(mode="json")
        if isinstance(recipe, PublicRealmRecipePayload)
        else PublicRealmRecipePayload.model_validate(recipe).model_dump(mode="json")
    )
    payload.pop("recipe_hash", None)
    return _sha256(payload)


def plan_public_realm_recipe(
    request: PublicRealmPlanRequest,
    *,
    catalog: PublicRealmCapabilityCatalog | None = None,
) -> PublicRealmRecipePayload:
    """Resolve one exact source identity and metric target into a stable recipe."""

    catalog = catalog or build_public_realm_capability_catalog()
    candidates = [
        capability
        for capability in catalog.capabilities
        if request.preferred_family_id in (None, capability.family_id)
        and any(selection.archetype_id == request.archetype_id for selection in capability.selections)
    ]
    supported = [_family_summary(capability) for capability in catalog.capabilities]
    if not candidates:
        qualifier = f" in family '{request.preferred_family_id}'" if request.preferred_family_id else ""
        raise PublicRealmPlanningError(
            f"No executable Public Realm LEGO family supports " f"'{request.archetype_id}'{qualifier}.",
            code="family_not_found",
            requested=_request_payload(request),
            supported_families=supported,
        )

    selection_candidates = [
        (capability, selection)
        for capability in candidates
        for selection in capability.selections
        if selection.archetype_id == request.archetype_id
    ]
    if request.variant_id is not None:
        selection_candidates = [
            (capability, selection)
            for capability, selection in selection_candidates
            if selection.variant_id == request.variant_id
        ]
        if not selection_candidates:
            raise PublicRealmPlanningError(
                f"Variant '{request.variant_id}' is not executable for " f"'{request.archetype_id}'.",
                code="family_incompatible",
                requested=_request_payload(request),
                supported_families=[_family_summary(capability) for capability in candidates],
                violations=[
                    {
                        "field": "variant_id",
                        "requested": request.variant_id,
                        "supported": sorted(
                            {
                                selection.variant_id
                                for capability in candidates
                                for selection in capability.selections
                                if selection.archetype_id == request.archetype_id
                            }
                        ),
                    }
                ],
            )
    else:
        defaults = [(capability, selection) for capability, selection in selection_candidates if selection.is_default]
        selection_candidates = defaults or selection_candidates

    normalized_target = _normalized_target(request.target)
    compatible = [
        (capability, selection)
        for capability, selection in selection_candidates
        if not _compatibility_violations(
            normalized_target,
            selection.compatibility,
        )
    ]
    if not compatible:
        capability, selection = min(
            selection_candidates,
            key=lambda pair: (pair[0].family_id, pair[1].variant_id),
        )
        violations = _compatibility_violations(
            normalized_target,
            selection.compatibility,
        )
        raise PublicRealmPlanningError(
            f"Family '{capability.family_id}' cannot compile the requested metric target.",
            code="family_incompatible",
            requested=_request_payload(request),
            supported_families=[_family_summary(candidate) for candidate in candidates],
            violations=violations,
        )
    capability, selection = min(
        compatible,
        key=lambda pair: (pair[0].family_id, pair[1].variant_id),
    )

    payload = {
        "schema_version": PUBLIC_REALM_SCHEMA_VERSION,
        "family_id": capability.family_id,
        "family_version": capability.family_version,
        "kind": capability.kind,
        "generator": capability.generator,
        "archetype_id": selection.archetype_id,
        "variant_id": selection.variant_id,
        "profile_id": selection.profile_id,
        "profile_version": selection.profile_version,
        "appearance_kit_id": selection.appearance_kit_id,
        "planting_structure": selection.planting_structure,
        "component_set_ids": selection.component_set_ids,
        "terrain_policy": capability.terrain_policy,
        "target": normalized_target,
        "catalog_fingerprint": catalog.fingerprint,
        "capability_fingerprint": public_realm_capability_fingerprint(capability),
        "recipe_hash": "0" * 64,
    }
    provisional = PublicRealmRecipePayload.model_validate(payload)
    return provisional.model_copy(
        update={
            "recipe_hash": public_realm_recipe_hash(provisional),
        }
    )


def _positive_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and number > 0 else None


def _metric_rectangle_axes(geometry: BaseGeometry) -> tuple[float, float]:
    rectangle = geometry.minimum_rotated_rectangle
    exterior = getattr(rectangle, "exterior", None)
    if exterior is None:
        raise ValueError("Public-realm geometry has no measurable footprint")
    coordinates = list(exterior.coords)
    sides = sorted(
        math.dist(coordinates[index], coordinates[index + 1]) for index in range(min(4, len(coordinates) - 1))
    )
    if len(sides) < 2 or sides[-1] <= 0 or sides[0] <= 0:
        raise ValueError("Public-realm geometry has no measurable footprint")
    return sides[-1], sides[0]


def _has_attestable_segment_width(
    geometry: BaseGeometry,
    *,
    long_axis: float,
    short_axis: float,
) -> bool:
    rectangle = geometry.minimum_rotated_rectangle
    rectangular_fill = float(geometry.area) / max(float(rectangle.area), 1e-9)
    return rectangular_fill >= 0.98 and long_axis >= short_axis * 2.0


def _target_from_metric_geometry(
    geometry: BaseGeometry,
    properties: dict[str, Any],
    *,
    target_type: Literal["park_polygon", "street_segment", "street_node"],
    attest_segment_width: bool = False,
) -> PublicRealmTarget:
    if geometry.is_empty or not geometry.is_valid:
        raise ValueError("Public-realm geometry must be non-empty and valid")
    long_axis, short_axis = _metric_rectangle_axes(geometry)
    if target_type == "park_polygon":
        return ParkPolygonTarget(
            width_m=round(long_axis, 3),
            depth_m=round(short_axis, 3),
            area_m2=round(float(geometry.area), 3),
        )

    if target_type == "street_segment":
        declared_width = _positive_number(properties.get("width"))
        use_measured_width = attest_segment_width and (
            properties.get("_plan_street_geometry_source") == "locked_area"
            or _has_attestable_segment_width(
                geometry,
                long_axis=long_axis,
                short_axis=short_axis,
            )
        )
        if use_measured_width and declared_width is not None and abs(short_axis - declared_width) <= 0.1:
            # Projection round-trips can move an otherwise exact authored
            # edge by a few centimetres.  The measured geometry has attested
            # the declaration; retain its canonical native-section value.
            row_width = declared_width
        else:
            row_width = short_axis if use_measured_width else declared_width or short_axis
        length = float(geometry.area) / row_width if geometry.area > 0 else long_axis
        return StreetSegmentTarget(
            row_width_m=round(row_width, 3),
            length_m=round(max(length, long_axis), 3),
        )

    row_width = _positive_number(properties.get("width")) or short_axis
    return StreetNodeTarget(
        approach_row_width_m=round(row_width, 3),
        diameter_m=round(max(long_axis, short_axis), 3),
        arm_count=int(_positive_number(properties.get("arm_count")) or 4),
    )


def public_realm_park_archetype_supports_metric_geometry(
    archetype_id: str,
    geometry_metric: BaseGeometry,
    *,
    variant_id: str | None = None,
    catalog: PublicRealmCapabilityCatalog | None = None,
) -> bool:
    """Whether one measured park polygon can compile as an exact family.

    The plan generator uses this at its final emission boundary to classify a
    compact central green or a decomposed pond-edge lobe by what the renderer
    can truthfully build.  It deliberately calls the same recipe planner as
    API assembly instead of duplicating family thresholds in geometry code.
    """

    try:
        target = _target_from_metric_geometry(
            geometry_metric,
            {},
            target_type="park_polygon",
        )
        plan_public_realm_recipe(
            PublicRealmPlanRequest(
                archetype_id=archetype_id,
                variant_id=variant_id,
                target=target,
            ),
            catalog=catalog,
        )
    except (PublicRealmPlanningError, TypeError, ValueError):
        return False
    return True


def plan_public_realm_metric_street_recipe(
    archetype_id: str,
    geometry_metric: BaseGeometry,
    *,
    variant_id: str | None,
    declared_width_m: float,
    catalog: PublicRealmCapabilityCatalog | None = None,
) -> PublicRealmRecipePayload | None:
    """Plan a locked metric street piece using geometry-attested width."""

    try:
        catalog = catalog or build_public_realm_capability_catalog()
        target = _target_from_metric_geometry(
            geometry_metric,
            {
                "width": declared_width_m,
                "_plan_street_geometry_source": "locked_area",
            },
            target_type="street_segment",
            attest_segment_width=True,
        )
        nominal_widths = sorted(
            {
                float(selection.compatibility.nominal_row_width_m)
                for capability in catalog.capabilities
                for selection in capability.selections
                if selection.archetype_id == archetype_id
                and variant_id in (None, selection.variant_id)
                and selection.compatibility.nominal_row_width_m is not None
            }
        )
        if nominal_widths:
            nearest_nominal = min(
                nominal_widths,
                key=lambda width: abs(width - target.row_width_m),
            )
            if abs(nearest_nominal - target.row_width_m) <= 0.1:
                # Preserve canonical section widths across WGS84 projection
                # round-trips, including the accepted legacy 22 m migration
                # family. Geometry has already attested the value here.
                target = target.model_copy(
                    update={
                        "row_width_m": nearest_nominal,
                    }
                )
        return plan_public_realm_recipe(
            PublicRealmPlanRequest(
                archetype_id=archetype_id,
                variant_id=variant_id,
                target=target,
            ),
            catalog=catalog,
        )
    except (PublicRealmPlanningError, TypeError, ValueError):
        return None


def plan_public_realm_zone_recipe(
    zone_type: str | None,
    geometry_wgs84: BaseGeometry,
    properties: dict[str, Any] | None,
    *,
    strict: bool,
    catalog: PublicRealmCapabilityCatalog | None = None,
) -> PublicRealmRecipePayload | None:
    """Compile a SiteZone-like source without importing ORM or API modules.

    ``None`` is the intentional manual/legacy compatibility path. In strict
    mode, missing catalog identity and unsupported families become structured
    errors so an AI plan can never silently escape the executable cohort.
    """

    props = properties or {}
    is_street = props.get("_plan_role") == "street" or zone_type in {"road", "street", "path"}
    if is_street:
        archetype_id = str(props.get("road_archetype_id") or "").strip()
        variant_id = str(props.get("road_selected_variant_id") or "").strip() or None
    else:
        archetype_id = str(props.get("green_space_archetype_id") or props.get("plaza_archetype_id") or "").strip()
        variant_id = (
            str(props.get("green_space_selected_variant_id") or props.get("plaza_selected_variant_id") or "").strip()
            or None
        )

    catalog = catalog or build_public_realm_capability_catalog()
    matching = [
        (capability, selection)
        for capability in catalog.capabilities
        for selection in capability.selections
        if selection.archetype_id == archetype_id
    ]
    if not archetype_id or not matching:
        if not strict:
            return None
        raise PublicRealmPlanningError(
            f"No executable Public Realm LEGO family supports " f"'{archetype_id or 'missing_archetype_id'}'.",
            code="family_not_found",
            requested={
                "archetype_id": archetype_id or "missing_archetype_id",
                **({"variant_id": variant_id} if variant_id else {}),
                "kind": "street" if is_street else "park",
            },
            supported_families=[_family_summary(capability) for capability in catalog.capabilities],
        )

    target_types = {selection.compatibility.target_type for _capability, selection in matching}
    if len(target_types) != 1:
        raise ValueError(f"Public-realm archetype '{archetype_id}' has ambiguous target types")
    transformer = build_transformer(
        WGS84_CRS,
        local_metric_crs_for_polygon(geometry_wgs84),
    )
    metric_geometry = project_geometry(geometry_wgs84, transformer)
    target = _target_from_metric_geometry(
        metric_geometry,
        props,
        target_type=target_types.pop(),
        # Strictness controls failure behavior, not recipe geometry.  Every
        # emitted V1 recipe must use the same target policy so a manual compile
        # and Direct's later canonical replan cannot disagree.
        attest_segment_width=True,
    )
    try:
        return plan_public_realm_recipe(
            PublicRealmPlanRequest(
                archetype_id=archetype_id,
                variant_id=variant_id,
                target=target,
            ),
            catalog=catalog,
        )
    except PublicRealmPlanningError:
        if strict:
            raise
        return None


def public_realm_recipe_identity(
    value: PublicRealmRecipePayload | dict[str, Any] | None,
    *,
    catalog: PublicRealmCapabilityCatalog | None = None,
) -> dict[str, Any] | None:
    """Validate a stored recipe against both its hashes and the live catalog."""

    if value is None:
        return None
    try:
        recipe = (
            value if isinstance(value, PublicRealmRecipePayload) else PublicRealmRecipePayload.model_validate(value)
        )
    except (TypeError, ValueError):
        return None
    if public_realm_recipe_hash(recipe) != recipe.recipe_hash:
        return None
    catalog = catalog or build_public_realm_capability_catalog()
    if recipe.catalog_fingerprint != catalog.fingerprint:
        return None
    capability = next(
        (
            item
            for item in catalog.capabilities
            if item.family_id == recipe.family_id and item.family_version == recipe.family_version
        ),
        None,
    )
    if capability is None:
        return None
    if public_realm_capability_fingerprint(capability) != recipe.capability_fingerprint:
        return None
    try:
        canonical = plan_public_realm_recipe(
            PublicRealmPlanRequest(
                archetype_id=recipe.archetype_id,
                variant_id=recipe.variant_id,
                target=recipe.target,
                preferred_family_id=recipe.family_id,
            ),
            catalog=catalog,
        )
    except PublicRealmPlanningError:
        return None
    # Replanning rechecks metric compatibility and reconstructs every
    # renderer-affecting field from the live capability.  A caller therefore
    # cannot alter an appearance/component/terrain field and bless it by
    # merely recomputing the self-hash.
    if canonical != recipe:
        return None
    return {
        "capability_fingerprint": recipe.capability_fingerprint,
        "recipe_hash": recipe.recipe_hash,
        "recipe": recipe.model_dump(mode="json"),
    }


def public_realm_representation_hash(
    *,
    source_hash: str,
    recipe: PublicRealmRecipePayload | dict[str, Any],
) -> str | None:
    """Bind source, current capability, recipe hash, and canonical recipe."""

    identity = public_realm_recipe_identity(recipe)
    if identity is None:
        return None
    return _sha256(
        {
            "contract_version": 1,
            "source_hash": source_hash.lower(),
            **identity,
        }
    )
