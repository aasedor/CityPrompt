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
from shapely import affinity
from shapely.geometry import box
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
_POND_LAKE_ENVELOPE = _park_envelope(
    nominal=(80.0, 60.0), width=(35.0, 180.0), depth=(28.0, 140.0), area=(980.0, 25_200.0),
)
_WETLAND_GARDEN_ENVELOPE = _park_envelope(
    nominal=(80.0, 60.0), width=(45.0, 180.0), depth=(35.0, 140.0), area=(1_575.0, 25_200.0),
)
_RIPARIAN_BUFFER_ENVELOPE = _park_envelope(
    nominal=(200.0, 50.0), width=(70.0, 600.0), depth=(24.0, 100.0), area=(1_680.0, 60_000.0), min_aspect_ratio=2.0,
)
_RESERVOIR_PARK_ENVELOPE = _park_envelope(
    nominal=(140.0, 80.0), width=(90.0, 420.0), depth=(60.0, 280.0), area=(5_400.0, 117_600.0),
)
_CULTURAL_GARDEN_ENVELOPE = _park_envelope(
    nominal=(90.0, 70.0), width=(45.0, 260.0), depth=(40.0, 210.0), area=(1_800.0, 54_600.0),
)
_URBAN_FOREST_ENVELOPE = _park_envelope(
    nominal=(250.0, 200.0), width=(80.0, 500.0), depth=(70.0, 420.0), area=(5_600.0, 210_000.0),
)
_AMPHITHEATER_LAWN_ENVELOPE = _park_envelope(
    nominal=(80.0, 60.0), width=(55.0, 140.0), depth=(45.0, 120.0), area=(2_475.0, 16_800.0),
)
_ADVENTURE_PLAY_ENVELOPE = _park_envelope(
    nominal=(40.0, 35.0), width=(40.0, 65.0), depth=(35.0, 58.0), area=(1_400.0, 3_770.0),
)
_DISC_GOLF_ENVELOPE = _park_envelope(
    nominal=(300.0, 200.0), width=(120.0, 500.0), depth=(90.0, 360.0), area=(10_800.0, 180_000.0),
)
_BOCCE_ENVELOPE = _park_envelope(
    nominal=(28.0, 16.0), width=(28.0, 90.0), depth=(16.0, 55.0), area=(448.0, 4_950.0),
)
_CLIMBING_ENVELOPE = _park_envelope(
    nominal=(25.0, 20.0), width=(25.0, 60.0), depth=(20.0, 50.0), area=(500.0, 3_000.0),
)
_MINI_GOLF_ENVELOPE = _park_envelope(
    nominal=(50.0, 30.0), width=(42.0, 110.0), depth=(28.0, 80.0), area=(1_176.0, 8_800.0),
)
_BEACH_VOLLEYBALL_ENVELOPE = _park_envelope(
    nominal=(24.0, 16.0), width=(24.0, 90.0), depth=(16.0, 55.0), area=(384.0, 4_950.0),
)
_POLLINATOR_ENVELOPE = _park_envelope(
    nominal=(80.0, 60.0), width=(35.0, 180.0), depth=(28.0, 140.0), area=(980.0, 25_200.0),
)
_ORCHARD_ENVELOPE = _park_envelope(
    nominal=(60.0, 50.0), width=(36.0, 150.0), depth=(30.0, 120.0), area=(1_080.0, 18_000.0),
)
_BIOSWALE_ENVELOPE = _park_envelope(
    nominal=(60.0, 15.0), width=(40.0, 300.0), depth=(10.0, 45.0), area=(400.0, 13_500.0), min_aspect_ratio=2.5,
)
_SCULPTURE_GARDEN_ENVELOPE = _park_envelope(
    nominal=(60.0, 50.0), width=(36.0, 150.0), depth=(30.0, 120.0), area=(1_080.0, 18_000.0),
)
_LABYRINTH_ENVELOPE = _park_envelope(
    nominal=(20.0, 20.0), width=(20.0, 65.0), depth=(20.0, 65.0), area=(400.0, 4_225.0),
)
_ICE_RINK_MULTIPURPOSE_ENVELOPE = _park_envelope(
    nominal=(64.0, 38.0), width=(60.0, 120.0), depth=(30.0, 85.0), area=(1_800.0, 10_200.0),
)
_KAYAK_RIVER_LAUNCH_ENVELOPE = _park_envelope(
    nominal=(80.0, 35.0), width=(45.0, 220.0), depth=(24.0, 80.0), area=(1_080.0, 17_600.0), min_aspect_ratio=1.6,
)
_TIDAL_MARSH_CORDGRASS_ENVELOPE = _park_envelope(
    nominal=(150.0, 100.0), width=(80.0, 360.0), depth=(60.0, 260.0), area=(4_800.0, 93_600.0),
)
_CINEMA_LAWN_PROJECTION_ENVELOPE = _park_envelope(
    nominal=(80.0, 50.0), width=(58.0, 160.0), depth=(40.0, 110.0), area=(2_320.0, 17_600.0),
)
_FOOD_TRUCK_PERMANENT_ENVELOPE = _park_envelope(
    nominal=(50.0, 40.0), width=(38.0, 100.0), depth=(32.0, 80.0), area=(1_216.0, 8_000.0),
)
_GREAT_LAWN_ENVELOPE = _park_envelope(
    nominal=(180.0, 120.0), width=(75.0, 420.0), depth=(55.0, 300.0), area=(4_125.0, 126_000.0),
)
_CAMPUS_MEADOW_QUAD_ENVELOPE = _park_envelope(
    nominal=(100.0, 80.0), width=(55.0, 220.0), depth=(45.0, 170.0), area=(2_475.0, 37_400.0),
)
_URBAN_BEACH_FAMILY_ENVELOPE = _park_envelope(
    nominal=(60.0, 45.0), width=(42.0, 130.0), depth=(34.0, 100.0), area=(1_428.0, 13_000.0),
)
_VELODROME_OPEN_AIR_ENVELOPE = _park_envelope(
    nominal=(135.0, 82.0), width=(125.0, 220.0), depth=(72.0, 150.0), area=(9_000.0, 33_000.0),
)
_MTB_SKILLS_DIRT_ENVELOPE = _park_envelope(
    nominal=(90.0, 60.0), width=(55.0, 190.0), depth=(42.0, 130.0), area=(2_310.0, 24_700.0),
)
_REGIONAL_ENGLISH_LANDSCAPE_ENVELOPE = _park_envelope(
    nominal=(220.0, 160.0), width=(100.0, 500.0), depth=(80.0, 400.0), area=(8_000.0, 200_000.0),
)
_BEER_GARDEN_MUNICH_ENVELOPE = _park_envelope(
    nominal=(30.0, 28.0), width=(25.0, 100.0), depth=(25.0, 90.0), area=(625.0, 9_000.0),
)
_SUNKEN_COURTYARD_ENVELOPE = _park_envelope(
    nominal=(30.0, 25.0), width=(26.0, 80.0), depth=(22.0, 70.0), area=(572.0, 5_600.0),
)
_TERRACED_CASCADE_ENVELOPE = _park_envelope(
    nominal=(90.0, 100.0), width=(55.0, 180.0), depth=(60.0, 220.0), area=(3_300.0, 39_600.0),
)
_MARKET_FESTIVAL_LAWN_ENVELOPE = _park_envelope(
    nominal=(95.0, 75.0), width=(60.0, 250.0), depth=(50.0, 180.0), area=(3_000.0, 45_000.0),
)
_BOARDWALK_MARITIME_ENVELOPE = _park_envelope(
    nominal=(120.0, 22.0), width=(60.0, 600.0), depth=(14.0, 55.0), area=(840.0, 33_000.0), min_aspect_ratio=2.5,
)
_FOUNTAIN_FORMAL_POOL_ENVELOPE = _park_envelope(
    nominal=(55.0, 35.0), width=(40.0, 160.0), depth=(28.0, 100.0), area=(1_120.0, 16_000.0),
)
_NATURAL_SWIMMING_POND_ENVELOPE = _park_envelope(
    nominal=(90.0, 70.0), width=(60.0, 200.0), depth=(50.0, 150.0), area=(3_000.0, 30_000.0),
)
_NATURE_PRESERVE_PRAIRIE_ENVELOPE = _park_envelope(
    nominal=(180.0, 120.0), width=(80.0, 600.0), depth=(60.0, 450.0), area=(4_800.0, 270_000.0),
)
_RIVERFRONT_LAKE_BEACH_ENVELOPE = _park_envelope(
    nominal=(130.0, 90.0), width=(80.0, 350.0), depth=(60.0, 220.0), area=(4_800.0, 77_000.0),
)
_RECLAIMED_WHARF_ENVELOPE = _park_envelope(nominal=(100.0, 50.0), width=(50.0, 280.0), depth=(24.0, 110.0), area=(1_200.0, 30_800.0), min_aspect_ratio=1.4)
_QUARRY_TIER_CASCADE_ENVELOPE = _park_envelope(nominal=(200.0, 150.0), width=(35.0, 360.0), depth=(30.0, 300.0), area=(1_200.0, 108_000.0))
_ESTATE_OAK_PICNIC_ENVELOPE = _park_envelope(nominal=(120.0, 100.0), width=(30.0, 320.0), depth=(30.0, 260.0), area=(900.0, 83_200.0))
_CONSTRUCTED_WETLAND_BOARDWALK_ENVELOPE = _park_envelope(nominal=(180.0, 110.0), width=(35.0, 400.0), depth=(28.0, 250.0), area=(1_200.0, 100_000.0))
_ACADEMIC_PLANTED_COURT_ENVELOPE = _park_envelope(nominal=(40.0, 38.0), width=(25.0, 72.0), depth=(25.0, 120.0), area=(625.0, 8_640.0))
_CAMPUS_GREEN_SPINE_ENVELOPE = _park_envelope(nominal=(30.0, 240.0), width=(15.0, 55.0), depth=(60.0, 500.0), area=(900.0, 27_500.0), min_aspect_ratio=2.0)
_BOTANICAL_ROSE_GARDEN_ENVELOPE = _park_envelope(nominal=(120.0, 90.0), width=(30.0, 260.0), depth=(31.0, 210.0), area=(930.0, 54_600.0))
_RESEARCH_ARBORETUM_ENVELOPE = _park_envelope(nominal=(300.0, 220.0), width=(35.0, 700.0), depth=(30.0, 520.0), area=(1_200.0, 364_000.0))
_REWILDING_REFORESTATION_ENVELOPE = _park_envelope(nominal=(300.0, 220.0), width=(35.0, 800.0), depth=(30.0, 650.0), area=(1_200.0, 520_000.0))
_STORMWATER_ARID_CHANNEL_ENVELOPE = _park_envelope(nominal=(200.0, 125.0), width=(35.0, 450.0), depth=(24.0, 300.0), area=(900.0, 135_000.0))
_URBAN_POCKET_RUSTIC_ENVELOPE = _park_envelope(nominal=(20.0, 20.0), width=(10.0, 45.0), depth=(10.0, 45.0), area=(100.0, 2_025.0))
_NEIGHBORHOOD_CONTEMPORARY_ENVELOPE = _park_envelope(nominal=(100.0, 80.0), width=(35.0, 240.0), depth=(28.0, 180.0), area=(980.0, 43_200.0))
_CEMETERY_CLASSICAL_ENVELOPE = _park_envelope(nominal=(250.0, 200.0), width=(45.0, 600.0), depth=(35.0, 460.0), area=(1_575.0, 276_000.0))
_COURTYARD_LINEAR_WATER_ENVELOPE = _park_envelope(nominal=(35.0, 35.0), width=(15.0, 120.0), depth=(15.0, 90.0), area=(225.0, 10_800.0))
_PARKLET_SF_TIMBER_ENVELOPE = _park_envelope(nominal=(10.0, 6.0), width=(5.0, 40.0), depth=(3.0, 14.0), area=(15.0, 560.0), min_aspect_ratio=1.2)
_FRENCH_PARTERRE_AXIS_ENVELOPE = _park_envelope(nominal=(180.0, 140.0), width=(40.0, 420.0), depth=(30.0, 320.0), area=(1_200.0, 134_400.0))
_LONDON_RAILED_SQUARE_ENVELOPE = _park_envelope(nominal=(100.0, 80.0), width=(35.0, 260.0), depth=(28.0, 200.0), area=(980.0, 52_000.0))
_HALIFAX_ROSE_BANDSTAND_ENVELOPE = _park_envelope(nominal=(200.0, 150.0), width=(40.0, 440.0), depth=(32.0, 330.0), area=(1_280.0, 145_200.0))
_OLMSTED_MULTILANDSCAPE_ENVELOPE = _park_envelope(nominal=(400.0, 350.0), width=(50.0, 900.0), depth=(35.0, 720.0), area=(1_750.0, 648_000.0))
_HILLTOP_VIEWPOINT_ENVELOPE = _park_envelope(nominal=(180.0, 180.0), width=(40.0, 420.0), depth=(35.0, 380.0), area=(1_400.0, 159_600.0))
_SKATE_PARK_V0_ENVELOPE = _park_envelope(
    nominal=(40.0, 30.0),
    # The archetype-owned kit is a fixed 40 x 30 m program. These bounds
    # describe only the receiving parcel; the geometry preflight below also
    # proves that the complete rectangle fits inside irregular polygons.
    width=(40.0, 52.0),
    depth=(30.0, 44.0),
    area=(1_200.0, 2_288.0),
)

_SKATE_PARK_V0_WIDTH_M = 40.0
_SKATE_PARK_V0_DEPTH_M = 30.0
_SKATE_PARK_V0_CLEARANCE_M = 0.5

_EXACT_PARK_PROGRAMS: dict[tuple[str, str], tuple[float, float, float]] = {
    ("skate_park", "skate_park_v0"): (40.0, 30.0, 0.5),
    ("inclusive_playground", "inclusive_playground_v0"): (50.0, 40.0, 0.5),
    ("dog_park", "dog_park_v0"): (80.0, 50.0, 0.5),
    ("splash_pad_area", "splash_pad_area_v0"): (30.0, 25.0, 0.5),
    ("community_garden", "community_garden_v0"): (50.0, 50.0, 0.5),
    ("basketball_court", "basketball_court_v0"): (32.0, 19.0, 0.5),
    ("basketball_court", "basketball_court_v1"): (32.0, 19.0, 0.5),
    ("basketball_court", "basketball_court_v2"): (19.0, 17.0, 0.5),
    ("basketball_court", "basketball_court_v3"): (32.0, 19.0, 0.5),
    # Adaptive regulation families prove that at least one complete module can
    # fit. The renderer then keeps the maximum count of whole modules inside
    # the actual polygon; these values must never describe a stretched field.
    ("tennis_court_cluster", "tennis_court_cluster_v0"): (36.58, 18.29, 0.5),
    ("soccer_pitch_caged", "soccer_pitch_caged_v0"): (30.0, 18.0, 0.5),
    ("athletics_precinct_sports_fields", "athletics_precinct_sports_fields_variant_0"): (100.0, 64.0, 0.5),
    ("nature_play_area", "nature_play_area_v0"): (40.0, 30.0, 0.5),
    ("pump_track", "pump_track_v0"): (50.0, 30.0, 0.5),
    ("outdoor_fitness_circuit", "outdoor_fitness_circuit_v0"): (30.0, 25.0, 0.5),
    ("memorial_garden", "memorial_garden_v0"): (50.0, 40.0, 0.5),
    ("pickleball_courts", "pickleball_courts_v1"): (78.0, 66.0, 0.5),
    ("running_track_oval", "running_track_oval_v2"): (220.0, 135.0, 0.5),
    ("baseball_softball_diamond", "baseball_softball_diamond_v1"): (230.0, 210.0, 0.5),
    ("cricket_pitch_oval", "cricket_pitch_oval_v0"): (190.0, 170.0, 0.5),
    ("sports_field_complex", "sports_field_complex_v0"): (330.0, 245.0, 0.5),
}

_INCLUSIVE_PLAYGROUND_V0_ENVELOPE = _park_envelope(
    nominal=(50.0, 40.0), width=(50.0, 65.0), depth=(40.0, 55.0), area=(2_000.0, 3_575.0),
)
_DOG_PARK_V0_ENVELOPE = _park_envelope(
    nominal=(80.0, 50.0), width=(80.0, 100.0), depth=(50.0, 65.0), area=(4_000.0, 6_500.0),
)
_SPLASH_PAD_V0_ENVELOPE = _park_envelope(
    nominal=(30.0, 25.0), width=(30.0, 42.0), depth=(25.0, 35.0), area=(750.0, 1_470.0),
)
_COMMUNITY_GARDEN_V0_ENVELOPE = _park_envelope(
    nominal=(50.0, 50.0), width=(50.0, 65.0), depth=(50.0, 65.0), area=(2_500.0, 4_225.0),
)
_TENNIS_CLUSTER_V0_ENVELOPE = _park_envelope(
    nominal=(82.0, 46.0), width=(36.58, 120.0), depth=(18.29, 100.0), area=(669.0, 12_000.0),
)
_BASKETBALL_COURT_V0_ENVELOPE = _park_envelope(
    nominal=(32.0, 19.0), width=(32.0, 100.0), depth=(19.0, 80.0), area=(608.0, 8_000.0),
)
_BASKETBALL_COURT_V1_ENVELOPE = _park_envelope(
    nominal=(64.0, 22.0), width=(32.0, 100.0), depth=(19.0, 80.0), area=(608.0, 8_000.0),
)
_BASKETBALL_COURT_V2_ENVELOPE = _park_envelope(
    nominal=(19.0, 17.0), width=(17.0, 100.0), depth=(17.0, 80.0), area=(323.0, 8_000.0),
)
_BASKETBALL_COURT_V3_ENVELOPE = _park_envelope(
    nominal=(32.0, 19.0), width=(32.0, 100.0), depth=(19.0, 80.0), area=(608.0, 8_000.0),
)
_CAGED_SOCCER_V0_ENVELOPE = _park_envelope(
    nominal=(66.0, 24.0), width=(30.0, 100.0), depth=(18.0, 70.0), area=(540.0, 7_000.0),
)
_ATHLETICS_FIELDS_V0_ENVELOPE = _park_envelope(
    nominal=(210.0, 76.0), width=(100.0, 350.0), depth=(64.0, 230.0), area=(6_400.0, 80_000.0),
)
_NATURE_PLAY_V0_ENVELOPE = _park_envelope(
    nominal=(40.0, 30.0), width=(40.0, 60.0), depth=(30.0, 45.0), area=(1_200.0, 2_700.0),
)
_PUMP_TRACK_V0_ENVELOPE = _park_envelope(
    nominal=(50.0, 30.0), width=(50.0, 70.0), depth=(30.0, 45.0), area=(1_500.0, 3_150.0),
)
_OUTDOOR_FITNESS_V0_ENVELOPE = _park_envelope(
    nominal=(30.0, 25.0), width=(30.0, 45.0), depth=(25.0, 40.0), area=(750.0, 1_800.0),
)
_MEMORIAL_GARDEN_V0_ENVELOPE = _park_envelope(
    nominal=(50.0, 40.0), width=(50.0, 70.0), depth=(40.0, 55.0), area=(2_000.0, 3_850.0),
)
_PICKLEBALL_COMMUNITY_V1_ENVELOPE = _park_envelope(
    nominal=(78.0, 66.0), width=(78.0, 100.0), depth=(66.0, 88.0), area=(5_148.0, 8_800.0),
)
_TRACK_OVAL_SCHOOL_V2_ENVELOPE = _park_envelope(
    nominal=(220.0, 135.0), width=(220.0, 270.0), depth=(135.0, 175.0), area=(29_700.0, 47_250.0),
)
_BASEBALL_CLUB_HUB_V1_ENVELOPE = _park_envelope(
    nominal=(230.0, 210.0), width=(230.0, 285.0), depth=(210.0, 260.0), area=(48_300.0, 74_100.0),
)
_CRICKET_VILLAGE_GREEN_V0_ENVELOPE = _park_envelope(
    nominal=(190.0, 170.0), width=(190.0, 240.0), depth=(170.0, 220.0), area=(32_300.0, 52_800.0),
)
_SPORTS_COMPLEX_TOURNAMENT_V0_ENVELOPE = _park_envelope(
    nominal=(330.0, 245.0), width=(330.0, 400.0), depth=(245.0, 310.0), area=(80_850.0, 124_000.0),
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
        family_id="park_skate_archetype_v0",
        kind="park",
        title="Skate Park / Professional Grade v0",
        generator="park_kit",
        selections=(
            _selection(
                "skate_park",
                "skate_park_v0",
                profile_id="skate-park-archetype-v1",
                appearance_kit_id="skate_park_v0_reference_skin",
                planting_structure="skate_archetype_v0",
                compatibility=_SKATE_PARK_V0_ENVELOPE,
                components=(
                    "skate_park_v0_ground_program",
                    "skate_bowl_module_v1",
                    "skate_stair_hubba_module_v1",
                    "skate_rail_v1",
                    "skate_ledge_v1",
                    "skate_spectator_bench_v1",
                ),
                default=True,
            ),
        ),
    ),
    PublicRealmFamilyCapability(
        family_id="park_inclusive_playground_v0", kind="park",
        title="Inclusive Playground / Universal Access v0", generator="park_kit",
        selections=(_selection(
            "inclusive_playground", "inclusive_playground_v0",
            profile_id="inclusive-playground-archetype-v1",
            appearance_kit_id="inclusive_playground_v0_reference_skin",
            planting_structure="inclusive_playground_v0",
            compatibility=_INCLUSIVE_PLAYGROUND_V0_ENVELOPE,
            components=("inclusive_playground_v0_ground_program", "accessible_play_structure_v1", "accessible_swing_bay_v1", "inclusive_spinner_v1", "sensory_panel_v1", "shade_canopy_v1"),
            default=True,
        ),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_dog_archetype_v0", kind="park",
        title="Dog Park / Natural Exercise Enclosures v0", generator="park_kit",
        selections=(_selection(
            "dog_park", "dog_park_v0", profile_id="dog-park-archetype-v1",
            appearance_kit_id="dog_park_v0_reference_skin", planting_structure="dog_park_v0",
            compatibility=_DOG_PARK_V0_ENVELOPE,
            components=("dog_park_v0_ground_program", "dog_park_gate_v1", "timber_rail_fence_v1", "shade_shelter_v1", "boulder_cluster_v1"), default=True,
        ),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_splash_pad_v0", kind="park",
        title="Splash Pad / Timber Water Play v0", generator="park_kit",
        selections=(_selection(
            "splash_pad_area", "splash_pad_area_v0", profile_id="splash-pad-archetype-v1",
            appearance_kit_id="splash_pad_area_v0_reference_skin", planting_structure="splash_pad_area_v0",
            compatibility=_SPLASH_PAD_V0_ENVELOPE,
            components=("splash_pad_v0_ground_program", "timber_water_tower_v1", "spray_arch_v1", "ground_jet_v1", "split_rail_fence_v1"), default=True,
        ),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_community_garden_v0", kind="park",
        title="Community Garden / Allotments v0", generator="park_kit",
        selections=(_selection(
            "community_garden", "community_garden_v0", profile_id="community-garden-archetype-v1",
            appearance_kit_id="community_garden_v0_reference_skin", planting_structure="community_garden_v0",
            compatibility=_COMMUNITY_GARDEN_V0_ENVELOPE,
            components=("community_garden_v0_ground_program", "raised_growing_bed_v1", "garden_greenhouse_v1", "garden_trellis_v1", "compost_bins_v1", "split_rail_fence_v1"), default=True,
        ),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_basketball_court_v0", kind="park",
        title="Basketball Court / Archetype Variants v1", generator="park_kit",
        selections=(
            _selection(
                "basketball_court", "basketball_court_v0", profile_id="basketball-court-archetype-v2",
                appearance_kit_id="basketball_court_v0_classic_asphalt_skin", planting_structure="basketball_classic_v0",
                compatibility=_BASKETBALL_COURT_V0_ENVELOPE,
                components=(
                    "basketball_full_court_metric_program_v1", "classic_asphalt_surface_v1",
                    "basketball_hoop_regulation_v1", "chain_link_court_enclosure_v1",
                    "basketball_player_bench_v1", "court_floodlight_v1", "shared_park_equipment_v1",
                ), default=True,
            ),
            _selection(
                "basketball_court", "basketball_court_v1", profile_id="basketball-court-archetype-v2",
                appearance_kit_id="basketball_court_v1_pro_acrylic_skin", planting_structure="basketball_pro_v1",
                compatibility=_BASKETBALL_COURT_V1_ENVELOPE,
                components=(
                    "basketball_full_court_metric_program_v1", "pro_acrylic_surface_v1",
                    "basketball_hoop_regulation_v1", "black_mesh_court_enclosure_v1",
                    "basketball_scoreboard_v1", "spectator_bleacher_v1", "court_floodlight_v1",
                    "shared_park_equipment_v1",
                ),
            ),
            _selection(
                "basketball_court", "basketball_court_v2", profile_id="basketball-court-archetype-v2",
                appearance_kit_id="basketball_court_v2_half_court_mural_skin", planting_structure="basketball_half_court_v2",
                compatibility=_BASKETBALL_COURT_V2_ENVELOPE,
                components=(
                    "basketball_half_court_metric_program_v1", "geometric_mural_surface_v1",
                    "basketball_hoop_regulation_v1", "basketball_seating_wall_v1",
                    "low_chain_link_enclosure_v1", "shared_park_equipment_v1",
                ),
            ),
            _selection(
                "basketball_court", "basketball_court_v3", profile_id="basketball-court-archetype-v2",
                appearance_kit_id="basketball_court_v3_streetball_skin", planting_structure="basketball_streetball_v3",
                compatibility=_BASKETBALL_COURT_V3_ENVELOPE,
                components=(
                    "basketball_full_court_metric_program_v1", "worn_street_art_surface_v1",
                    "basketball_hoop_regulation_v1", "graffiti_fence_panel_v1",
                    "concrete_step_seating_v1", "shared_park_equipment_v1",
                ),
            ),
        ),
    ),
    PublicRealmFamilyCapability(
        family_id="park_tennis_cluster_v0", kind="park",
        title="Tennis Court Cluster / Professional Grade v0", generator="park_kit",
        selections=(_selection(
            "tennis_court_cluster", "tennis_court_cluster_v0", profile_id="tennis-cluster-archetype-v1",
            appearance_kit_id="tennis_court_cluster_v0_reference_skin", planting_structure="tennis_court_cluster_v0",
            compatibility=_TENNIS_CLUSTER_V0_ENVELOPE,
            components=("tennis_cluster_v0_ground_program", "tennis_net_v1", "tennis_fence_v1", "tennis_floodlight_v1", "spectator_bleacher_v1"), default=True,
        ),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_caged_soccer_v0", kind="park",
        title="Caged Soccer Pitch / European Street Cage v0", generator="park_kit",
        selections=(_selection(
            "soccer_pitch_caged", "soccer_pitch_caged_v0", profile_id="caged-soccer-pitch-v1",
            appearance_kit_id="soccer_pitch_caged_v0_reference_skin", planting_structure="caged_soccer_v0",
            compatibility=_CAGED_SOCCER_V0_ENVELOPE,
            components=("caged_soccer_v0_ground_program", "five_a_side_goal_v1", "soccer_rebound_board_v1", "soccer_cage_mesh_v1", "soccer_floodlight_v1", "player_bench_v1"), default=True,
        ),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_athletics_fields_v0", kind="park",
        title="Athletics Precinct / Regulation Playing Fields v0", generator="park_kit",
        selections=(_selection(
            "athletics_precinct_sports_fields", "athletics_precinct_sports_fields_variant_0", profile_id="athletics-precinct-sports-fields-v1",
            appearance_kit_id="athletics_precinct_sports_fields_v0_reference_skin", planting_structure="athletics_fields_v0",
            compatibility=_ATHLETICS_FIELDS_V0_ENVELOPE,
            components=("athletics_fields_v0_ground_program", "regulation_soccer_goal_v1", "field_floodlight_v1", "spectator_bleacher_v1"), default=True,
        ),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_nature_play_v0", kind="park",
        title="Nature Play Area / Forest Adventure v0", generator="park_kit",
        selections=(_selection(
            "nature_play_area", "nature_play_area_v0", profile_id="nature-play-archetype-v1",
            appearance_kit_id="nature_play_area_v0_reference_skin", planting_structure="nature_play_area_v0",
            compatibility=_NATURE_PLAY_V0_ENVELOPE,
            components=("nature_play_v0_ground_program", "water_rill_v1", "balance_log_v1", "log_fort_v1", "willow_tunnel_v1", "stepping_stump_v1", "play_boulders_v1"), default=True,
        ),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_pump_track_v0", kind="park",
        title="Pump Track / Asphalt Competition v0", generator="park_kit",
        selections=(_selection(
            "pump_track", "pump_track_v0", profile_id="pump-track-archetype-v1",
            appearance_kit_id="pump_track_v0_reference_skin", planting_structure="pump_track_v0",
            compatibility=_PUMP_TRACK_V0_ENVELOPE,
            components=("pump_track_v0_ground_program", "pump_track_loop_v1", "pump_track_start_mound_v1", "spectator_bench_v1"), default=True,
        ),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_outdoor_fitness_v0", kind="park",
        title="Outdoor Fitness Circuit / Urban Calisthenics v0", generator="park_kit",
        selections=(_selection(
            "outdoor_fitness_circuit", "outdoor_fitness_circuit_v0", profile_id="outdoor-fitness-archetype-v1",
            appearance_kit_id="outdoor_fitness_circuit_v0_reference_skin", planting_structure="outdoor_fitness_circuit_v0",
            compatibility=_OUTDOOR_FITNESS_V0_ENVELOPE,
            components=("outdoor_fitness_v0_ground_program", "calisthenics_rig_v1", "parallel_bars_v1", "situp_bench_v1", "rings_frame_v1"), default=True,
        ),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_memorial_garden_v0", kind="park",
        title="Memorial Garden / Classical Formal v0", generator="park_kit",
        selections=(_selection(
            "memorial_garden", "memorial_garden_v0", profile_id="memorial-garden-archetype-v1",
            appearance_kit_id="memorial_garden_v0_reference_skin", planting_structure="memorial_garden_v0",
            compatibility=_MEMORIAL_GARDEN_V0_ENVELOPE,
            components=("memorial_garden_v0_ground_program", "reflecting_pool_v1", "tiered_fountain_v1", "memorial_wall_v1", "topiary_urn_v1"), default=True,
        ),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_pickleball_community_v1", kind="park",
        title="Pickleball Courts / Community Five-Court Hub v1", generator="park_kit",
        selections=(_selection(
            "pickleball_courts", "pickleball_courts_v1", profile_id="pickleball-community-five-court-v1",
            appearance_kit_id="pickleball_courts_v1_multi_angle_skin", planting_structure="pickleball_community_v1",
            compatibility=_PICKLEBALL_COMMUNITY_V1_ENVELOPE,
            components=("pickleball_community_v1_full_assembly", "pickleball_court_v1", "playground_social_edge_v1", "shade_seating_v1"), default=True,
        ),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_track_oval_school_v2", kind="park",
        title="Running Track / School Athletics Oval v2", generator="park_kit",
        selections=(_selection(
            "running_track_oval", "running_track_oval_v2", profile_id="track-oval-school-athletic-v2",
            appearance_kit_id="running_track_oval_v2_multi_angle_skin", planting_structure="track_oval_school_v2",
            compatibility=_TRACK_OVAL_SCHOOL_V2_ENVELOPE,
            components=("track_oval_school_v2_full_assembly", "regulation_track_v1", "soccer_infield_v1", "field_events_v1", "spectator_bleacher_v1"), default=True,
        ),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_baseball_club_hub_v1", kind="park",
        title="Baseball / Three-Field Club Hub v1", generator="park_kit",
        selections=(_selection(
            "baseball_softball_diamond", "baseball_softball_diamond_v1", profile_id="baseball-three-field-club-hub-v1",
            appearance_kit_id="baseball_softball_diamond_v1_multi_angle_skin", planting_structure="baseball_club_hub_v1",
            compatibility=_BASEBALL_CLUB_HUB_V1_ENVELOPE,
            components=("baseball_club_hub_v1_full_assembly", "three_regulation_diamonds_v1", "dugout_backstop_bleacher_v1", "batting_cages_v1", "reserved_clubhouse_pad_v1"), default=True,
        ),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_cricket_village_green_v0", kind="park",
        title="Cricket / Village Green Oval v0", generator="park_kit",
        selections=(_selection(
            "cricket_pitch_oval", "cricket_pitch_oval_v0", profile_id="cricket-village-green-v1",
            appearance_kit_id="cricket_pitch_oval_v0_multi_angle_skin", planting_structure="cricket_village_green_v0",
            compatibility=_CRICKET_VILLAGE_GREEN_V0_ENVELOPE,
            components=("cricket_village_green_v0_full_assembly", "regulation_wicket_v1", "oval_boundary_v1", "practice_nets_v1", "white_perimeter_fence_v1"), default=True,
        ),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_sports_complex_tournament_v0", kind="park",
        title="Sports Field Complex / Tournament Grounds v0", generator="park_kit",
        selections=(_selection(
            "sports_field_complex", "sports_field_complex_v0", profile_id="sports-complex-tournament-v1",
            appearance_kit_id="sports_field_complex_v0_multi_angle_skin", planting_structure="sports_complex_tournament_v0",
            compatibility=_SPORTS_COMPLEX_TOURNAMENT_V0_ENVELOPE,
            components=("sports_complex_tournament_v0_full_assembly", "regulation_soccer_fields_v1", "softball_fields_v1", "spectator_service_spine_v1", "field_lighting_v1"), default=True,
        ),),
    ),
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
            _selection(
                "community_park", "community_park_v0",
                profile_id="community-park-lego-v1",
                appearance_kit_id="english_pastoral_v1",
                planting_structure="naturalistic_grove",
                compatibility=_COMMUNITY_ENVELOPE,
                components=("community_park_ground_program_v1", "regulation_recreation_field_v1", "naturalistic_pond_v1", "picnic_social_edge_v1"),
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
            _selection(
                "pond_lake", "pond_lake_v0",
                profile_id="pond-lake-lego-v1",
                appearance_kit_id="pond_lake_v0_naturalistic_skin",
                planting_structure="pond_lake_v0",
                compatibility=_POND_LAKE_ENVELOPE,
                components=("pond_lake_ground_program_v1", "natural_stone_shore_v1", "timber_dock_v1", "riparian_planting_v1"),
            ),
            _selection(
                "wetland_rain_garden", "wetland_rain_garden_v0",
                profile_id="wetland-rain-garden-v2",
                appearance_kit_id="wetland_rain_garden_v0_native_restoration_skin",
                planting_structure="wetland_rain_garden_v0",
                compatibility=_WETLAND_GARDEN_ENVELOPE,
                components=("wetland_cells_ground_program_v2", "accessible_boardwalk_network_v1", "interpretive_overlook_v1", "riparian_planting_v1"),
            ),
            _selection(
                "riparian_buffer", "riparian_buffer_v0",
                profile_id="riparian-buffer-lego-v1",
                appearance_kit_id="riparian_buffer_v0_native_restoration_skin",
                planting_structure="riparian_buffer_v0",
                compatibility=_RIPARIAN_BUFFER_ENVELOPE,
                components=("riparian_corridor_ground_program_v1", "creek_channel_v1", "parallel_access_trail_v1", "small_timber_bridge_v1"),
            ),
            _selection(
                "reservoir_watershed_park", "reservoir_watershed_park_v0",
                profile_id="reservoir-watershed-park-v3",
                appearance_kit_id="reservoir_watershed_park_v0_concrete_edge_skin",
                planting_structure="reservoir_watershed_park_v0",
                compatibility=_RESERVOIR_PARK_ENVELOPE,
                components=("reservoir_ground_program_v3", "concrete_dam_spillway_v1", "perimeter_fence_v1", "viewing_deck_v1"),
            ),
        ),
    ),
    PublicRealmFamilyCapability(
        family_id="park_cultural_gardens",
        kind="park",
        title="Cultural and Botanical Gardens",
        generator="park_kit",
        selections=(
            _selection(
                "japanese_garden", "japanese_garden_v0",
                profile_id="japanese-garden-v4",
                appearance_kit_id="japanese_garden_v0_stroll_skin",
                planting_structure="japanese_garden_v0",
                compatibility=_CULTURAL_GARDEN_ENVELOPE,
                components=("japanese_stroll_ground_program_v4", "lacquer_bridge_v1", "raked_gravel_v1", "stepping_stone_route_v1"),
                default=True,
            ),
            _selection(
                "botanical_garden", "botanical_garden_v0",
                profile_id="botanical-garden-v5",
                appearance_kit_id="botanical_garden_v0_collection_skin",
                planting_structure="botanical_garden_v0",
                compatibility=_CULTURAL_GARDEN_ENVELOPE,
                components=("botanical_collection_ground_program_v5", "compact_conservatory_v1", "collection_beds_v1", "interpretive_loop_v1"),
            ),
        ),
    ),
    PublicRealmFamilyCapability(
        family_id="park_urban_forest",
        kind="park",
        title="Urban Forest / Native Woodland",
        generator="park_kit",
        selections=(_selection(
            "urban_forest", "urban_forest_v0",
            profile_id="urban-forest-v2",
            appearance_kit_id="urban_forest_v0_native_restoration_skin",
            planting_structure="urban_forest_v0",
            compatibility=_URBAN_FOREST_ENVELOPE,
            components=("urban_forest_ground_program_v2", "multi_age_canopy_v1", "understory_layer_v1", "low_impact_trail_v1"),
            default=True,
        ),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_amphitheater_lawn_v0",
        kind="park",
        title="Amphitheater Lawn / Terraced Performance",
        generator="park_kit",
        selections=(_selection(
            "amphitheater_lawn", "amphitheater_lawn_v0",
            profile_id="amphitheater-lawn-lego-v1",
            appearance_kit_id="amphitheater_lawn_v0_terraced_performance_skin",
            planting_structure="amphitheater_lawn_v0",
            compatibility=_AMPHITHEATER_LAWN_ENVELOPE,
            components=("amphitheater_lawn_ground_program_v1", "terraced_lawn_bowl_v1", "timber_stage_v1", "upper_rim_path_v1"),
            default=True,
        ),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_playground_adventure_v0",
        kind="park",
        title="Adventure Playground / Modular Towers",
        generator="park_kit",
        selections=(_selection(
            "playground_adventure", "playground_adventure_v0",
            profile_id="playground-adventure-lego-v1",
            appearance_kit_id="playground_adventure_v0_rustic_timber_skin",
            planting_structure="playground_adventure_v0",
            compatibility=_ADVENTURE_PLAY_ENVELOPE,
            components=("adventure_play_ground_program_v1", "rough_hewn_timber_towers_v1", "rope_climbing_network_v1", "swing_bay_v1", "split_rail_fence_v1", "play_boulders_v1"),
            default=True,
        ),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_disc_golf_wooded_v0", kind="park", title="Disc Golf / Wooded Championship v0", generator="park_kit",
        selections=(_selection("disc_golf_course", "disc_golf_course_v0", profile_id="disc-golf-wooded-lego-v1", appearance_kit_id="disc_golf_course_v0_wooded_championship_skin", planting_structure="disc_golf_wooded_v0", compatibility=_DISC_GOLF_ENVELOPE, components=("disc_golf_ground_program_v1", "nine_tee_pad_route_v1", "disc_basket_targets_v1", "wooded_fairway_clearings_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_bocce_piazza_v0", kind="park", title="Bocce / Italian Piazza v0", generator="park_kit",
        selections=(_selection("bocce_petanque_court", "bocce_petanque_court_v0", profile_id="bocce-piazza-lego-v1", appearance_kit_id="bocce_petanque_court_v0_italian_piazza_skin", planting_structure="bocce_piazza_v0", compatibility=_BOCCE_ENVELOPE, components=("bocce_ground_program_v1", "regulation_bocce_lane_v1", "stone_border_v1", "vine_pergola_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_climbing_competition_v0", kind="park", title="Climbing / Competition Boulder v0", generator="park_kit",
        selections=(_selection("climbing_bouldering_wall", "climbing_bouldering_wall_v0", profile_id="climbing-competition-lego-v1", appearance_kit_id="climbing_bouldering_wall_v0_competition_skin", planting_structure="climbing_competition_v0", compatibility=_CLIMBING_ENVELOPE, components=("climbing_ground_program_v1", "angular_boulder_walls_v1", "route_hold_set_v1", "continuous_fall_zone_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_mini_golf_classic_v0", kind="park", title="Mini Golf / Classic Themed v0", generator="park_kit",
        selections=(_selection("mini_golf_course", "mini_golf_course_v0", profile_id="mini-golf-classic-lego-v1", appearance_kit_id="mini_golf_course_v0_classic_skin", planting_structure="mini_golf_classic_v0", compatibility=_MINI_GOLF_ENVELOPE, components=("mini_golf_ground_program_v1", "nine_putting_lanes_v1", "classic_obstacles_v1", "lane_edge_masonry_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_beach_volleyball_competition_v0", kind="park", title="Beach Volleyball / Competition v0", generator="park_kit",
        selections=(_selection("beach_volleyball_courts", "beach_volleyball_courts_v0", profile_id="beach-volleyball-competition-lego-v1", appearance_kit_id="beach_volleyball_courts_v0_competition_skin", planting_structure="beach_volleyball_competition_v0", compatibility=_BEACH_VOLLEYBALL_ENVELOPE, components=("beach_volleyball_ground_program_v1", "regulation_sand_court_v1", "competition_net_v1", "referee_stand_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_pollinator_prairie_v0", kind="park", title="Pollinator Meadow / Prairie Restoration v0", generator="park_kit",
        selections=(_selection("pollinator_meadow", "pollinator_meadow_v0", profile_id="pollinator-prairie-lego-v1", appearance_kit_id="pollinator_meadow_v0_prairie_skin", planting_structure="pollinator_prairie_v0", compatibility=_POLLINATOR_ENVELOPE, components=("pollinator_ground_program_v1", "mown_loop_v1", "prairie_drift_matrix_v1", "interpretive_nodes_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_orchard_heritage_v0", kind="park", title="Urban Orchard / Heritage Apple v0", generator="park_kit",
        selections=(_selection("urban_orchard_food_forest", "urban_orchard_food_forest_v0", profile_id="orchard-heritage-lego-v1", appearance_kit_id="urban_orchard_food_forest_v0_heritage_apple_skin", planting_structure="orchard_heritage_v0", compatibility=_ORCHARD_ENVELOPE, components=("orchard_ground_program_v1", "heritage_tree_rows_v1", "harvest_spine_v1", "cider_press_shed_pad_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_bioswale_streetside_v0", kind="park", title="Bioswale / Streetside v0", generator="park_kit",
        selections=(_selection("bioswale_rain_garden", "bioswale_rain_garden_v0", profile_id="bioswale-streetside-lego-v1", appearance_kit_id="bioswale_rain_garden_v0_streetside_skin", planting_structure="bioswale_streetside_v0", compatibility=_BIOSWALE_ENVELOPE, components=("bioswale_ground_program_v1", "linear_treatment_cells_v1", "curb_inlets_v1", "overflow_check_dams_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_sculpture_museum_court_v0", kind="park", title="Sculpture Garden / Museum Court v0", generator="park_kit",
        selections=(_selection("sculpture_garden", "sculpture_garden_v0", profile_id="sculpture-museum-court-lego-v1", appearance_kit_id="sculpture_garden_v0_museum_court_skin", planting_structure="sculpture_museum_court_v0", compatibility=_SCULPTURE_GARDEN_ENVELOPE, components=("sculpture_court_ground_program_v1", "curated_display_plinths_v1", "abstract_sculpture_set_v1", "gravel_gallery_route_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_labyrinth_classical_v0", kind="park", title="Labyrinth / Classical Stone v0", generator="park_kit",
        selections=(_selection("labyrinth_meditation", "labyrinth_meditation_v0", profile_id="labyrinth-classical-lego-v1", appearance_kit_id="labyrinth_meditation_v0_classical_stone_skin", planting_structure="labyrinth_classical_v0", compatibility=_LABYRINTH_ENVELOPE, components=("labyrinth_ground_program_v1", "chartres_ring_path_v1", "central_stone_bench_v1", "formal_hedge_frame_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_ice_rink_multipurpose_v3", kind="park", title="Outdoor Ice Rink / Multipurpose Pad v3", generator="park_kit",
        selections=(_selection("outdoor_ice_rink", "outdoor_ice_rink_v3", profile_id="ice-rink-multipurpose-lego-v1", appearance_kit_id="outdoor_ice_rink_v3_multipurpose_pad_skin", planting_structure="ice_rink_multipurpose_v3", compatibility=_ICE_RINK_MULTIPURPOSE_ENVELOPE, components=("multipurpose_rink_ground_program_v1", "permanent_rink_boards_v1", "seasonal_surface_markings_v1", "rink_light_standard_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_kayak_river_launch_v0", kind="park", title="Kayak Launch / River Launch v0", generator="park_kit",
        selections=(_selection("kayak_launch_dock", "kayak_launch_dock_v0", profile_id="kayak-river-launch-lego-v1", appearance_kit_id="kayak_launch_dock_v0_river_launch_skin", planting_structure="kayak_river_launch_v0", compatibility=_KAYAK_RIVER_LAUNCH_ENVELOPE, components=("kayak_launch_ground_program_v1", "floating_dock_v1", "accessible_launch_slide_v1", "kayak_rack_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_tidal_marsh_cordgrass_v0", kind="park", title="Tidal Marsh Boardwalk / Cordgrass v0", generator="park_kit",
        selections=(_selection("tidal_marsh_boardwalk", "tidal_marsh_boardwalk_v0", profile_id="tidal-marsh-cordgrass-lego-v1", appearance_kit_id="tidal_marsh_boardwalk_v0_cordgrass_skin", planting_structure="tidal_marsh_cordgrass_v0", compatibility=_TIDAL_MARSH_CORDGRASS_ENVELOPE, components=("tidal_marsh_ground_program_v1", "elevated_boardwalk_v1", "hexagonal_overlook_v1", "interpretive_trailhead_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_cinema_lawn_projection_v1", kind="park", title="Outdoor Cinema / Park Lawn v1", generator="park_kit",
        selections=(_selection("outdoor_cinema_lawn", "outdoor_cinema_lawn_v1", profile_id="cinema-lawn-projection-lego-v1", appearance_kit_id="outdoor_cinema_lawn_v1_park_projection_skin", planting_structure="cinema_lawn_projection_v1", compatibility=_CINEMA_LAWN_PROJECTION_ENVELOPE, components=("cinema_lawn_ground_program_v1", "fixed_projection_screen_v1", "projection_booth_v1", "sightline_lawn_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_food_truck_permanent_v1", kind="park", title="Food-Truck Plaza / Permanent Park v1", generator="park_kit",
        selections=(_selection("food_truck_plaza", "food_truck_plaza_v1", profile_id="food-truck-permanent-lego-v1", appearance_kit_id="food_truck_plaza_v1_permanent_park_skin", planting_structure="food_truck_permanent_v1", compatibility=_FOOD_TRUCK_PERMANENT_ENVELOPE, components=("food_truck_plaza_ground_program_v1", "utility_truck_bays_v1", "shared_truck_prop_v1", "communal_picnic_grid_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_great_lawn_v2", kind="park", title="Festival / Great Lawn v2", generator="park_kit",
        selections=(_selection("festival_event_lawn", "festival_event_lawn_v2", profile_id="great-lawn-lego-v1", appearance_kit_id="festival_event_lawn_v2_great_lawn_skin", planting_structure="great_lawn_v2", compatibility=_GREAT_LAWN_ENVELOPE, components=("great_lawn_ground_program_v1", "perimeter_event_hookups_v1", "gentle_landform_v1", "clear_event_field_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_campus_meadow_quad_v0", kind="park", title="Campus Quad / Naturalized Meadow v0", generator="park_kit",
        selections=(_selection("campus_central_quad", "campus_central_quad_variant_0", profile_id="campus-meadow-quad-lego-v1", appearance_kit_id="campus_central_quad_v0_naturalized_meadow_skin", planting_structure="campus_meadow_quad_v0", compatibility=_CAMPUS_MEADOW_QUAD_ENVELOPE, components=("campus_meadow_ground_program_v1", "desire_line_crossing_v1", "social_nodes_v1", "meadow_boulder_matrix_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_urban_beach_family_v2", kind="park", title="Urban Beach / Family Splash v2", generator="park_kit",
        selections=(_selection("urban_beach", "urban_beach_v2", profile_id="urban-beach-family-lego-v1", appearance_kit_id="urban_beach_v2_family_splash_skin", planting_structure="urban_beach_family_v2", compatibility=_URBAN_BEACH_FAMILY_ENVELOPE, components=("urban_beach_ground_program_v1", "family_splash_pad_v1", "shade_sail_cluster_v1", "accessible_boardwalk_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_velodrome_open_air_v0", kind="park", title="Velodrome / Open Air v0", generator="park_kit",
        selections=(_selection("velodrome_cycling_track", "velodrome_cycling_track_variant_0", profile_id="velodrome-open-air-lego-v1", appearance_kit_id="velodrome_cycling_track_v0_open_air_skin", planting_structure="velodrome_open_air_v0", compatibility=_VELODROME_OPEN_AIR_ENVELOPE, components=("velodrome_ground_program_v1", "banked_250m_track_v1", "open_bleacher_v1", "timing_tower_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_mtb_skills_dirt_v2", kind="park", title="Mountain Bike / Skills and Dirt v2", generator="park_kit",
        selections=(_selection("mountain_bike_park", "mountain_bike_park_variant_2", profile_id="mtb-skills-dirt-lego-v1", appearance_kit_id="mountain_bike_park_v2_skills_dirt_skin", planting_structure="mtb_skills_dirt_v2", compatibility=_MTB_SKILLS_DIRT_ENVELOPE, components=("mtb_skills_ground_program_v1", "connected_pump_loop_v1", "dirt_jump_line_v1", "technical_feature_set_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_regional_english_landscape_v0", kind="park", title="Regional Park / English Landscape v0", generator="park_kit",
        selections=(_selection("regional_park", "regional_park_v0", profile_id="regional-english-landscape-lego-v1", appearance_kit_id="regional_park_v0_english_landscape_skin", planting_structure="regional_english_landscape_v0", compatibility=_REGIONAL_ENGLISH_LANDSCAPE_ENVELOPE, components=("regional_landscape_ground_program_v1", "serpentine_walk_network_v1", "naturalistic_pond_v1", "romantic_bridge_v1", "specimen_tree_matrix_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_beer_garden_munich_v0", kind="park", title="Beer Garden / Munich Chestnut v0", generator="park_kit",
        selections=(_selection("beer_garden", "beer_garden_v0", profile_id="beer-garden-munich-lego-v1", appearance_kit_id="beer_garden_v0_munich_chestnut_skin", planting_structure="beer_garden_munich_v0", compatibility=_BEER_GARDEN_MUNICH_ENVELOPE, components=("beer_garden_ground_program_v1", "communal_trestle_row_v1", "chestnut_canopy_grid_v1", "self_service_kiosk_v1", "pennant_string_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_sunken_courtyard_v0", kind="park", title="Sunken Plaza / Intimate Courtyard v0", generator="park_kit",
        selections=(_selection("sunken_plaza", "sunken_plaza_v0", profile_id="sunken-courtyard-lego-v1", appearance_kit_id="sunken_plaza_v0_intimate_courtyard_skin", planting_structure="sunken_courtyard_v0", compatibility=_SUNKEN_COURTYARD_ENVELOPE, components=("sunken_court_ground_program_v1", "three_sided_step_bowl_v1", "bronze_fountain_v1", "rim_hedge_v1", "cafe_clearance_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_terraced_cascade_v3", kind="park", title="Stepped Plaza / Modernist Cascade v3", generator="park_kit",
        selections=(_selection("stepped_terraced_plaza", "stepped_terraced_plaza_v3", profile_id="terraced-cascade-lego-v1", appearance_kit_id="stepped_terraced_plaza_v3_modernist_cascade_skin", planting_structure="terraced_cascade_v3", compatibility=_TERRACED_CASCADE_ENVELOPE, components=("terraced_plaza_ground_program_v1", "three_basin_water_axis_v1", "accessible_wrap_ramp_v1", "planter_terrace_v1", "seat_step_matrix_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_market_festival_lawn_v1", kind="park", title="Market Square / Open Festival Lawn v1", generator="park_kit",
        selections=(_selection("market_square", "market_square_v1", profile_id="market-festival-lawn-lego-v1", appearance_kit_id="market_square_v1_open_festival_lawn_skin", planting_structure="market_festival_lawn_v1", compatibility=_MARKET_FESTIVAL_LAWN_ENVELOPE, components=("market_lawn_ground_program_v1", "event_utility_bollard_v1", "vendor_pad_matrix_v1", "shade_anchor_v1", "service_loop_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_boardwalk_maritime_v0", kind="park", title="Promenade / Maritime Boardwalk v0", generator="park_kit",
        selections=(_selection("promenade_boardwalk", "promenade_boardwalk_v0", profile_id="boardwalk-maritime-lego-v1", appearance_kit_id="promenade_boardwalk_v0_maritime_skin", planting_structure="boardwalk_maritime_v0", compatibility=_BOARDWALK_MARITIME_ENVELOPE, components=("maritime_boardwalk_ground_program_v1", "rope_rail_v1", "nautical_light_v1", "view_bench_v1", "mooring_bollard_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_fountain_formal_pool_v1", kind="park", title="Fountain / Formal Reflecting Pool v1", generator="park_kit",
        selections=(_selection("fountain_water_feature", "fountain_water_feature_v1", profile_id="fountain-formal-pool-lego-v1", appearance_kit_id="fountain_water_feature_v1_formal_pool_skin", planting_structure="fountain_formal_pool_v1", compatibility=_FOUNTAIN_FORMAL_POOL_ENVELOPE, components=("formal_pool_ground_program_v1", "symmetric_jet_array_v1", "granite_coping_v1", "clipped_hedge_frame_v1", "classical_urn_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_natural_swimming_pond_v0", kind="park", title="Swimming Complex / Natural Pond v0", generator="park_kit",
        selections=(_selection("swimming_pool_complex", "swimming_pool_complex_v0", profile_id="natural-swimming-pond-lego-v1", appearance_kit_id="swimming_pool_complex_v0_natural_pond_skin", planting_structure="natural_swimming_pond_v0", compatibility=_NATURAL_SWIMMING_POND_ENVELOPE, components=("natural_swimming_ground_program_v1", "metric_lap_basin_v1", "regeneration_pond_v1", "timber_dock_v1", "sun_deck_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_nature_preserve_prairie_v1", kind="park", title="Nature Preserve / Tallgrass Prairie v1", generator="park_kit",
        selections=(_selection("nature_preserve", "nature_preserve_v1", profile_id="nature-preserve-prairie-lego-v1", appearance_kit_id="nature_preserve_v1_tallgrass_prairie_skin", planting_structure="nature_preserve_prairie_v1", compatibility=_NATURE_PRESERVE_PRAIRIE_ENVELOPE, components=("prairie_preserve_ground_program_v1", "mown_trail_network_v1", "timber_observation_deck_v1", "bur_oak_savanna_v1", "interpretive_post_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_riverfront_lake_beach_v1", kind="park", title="Riverfront / Lake Swimming Beach v1", generator="park_kit",
        selections=(_selection("riverfront_park_beach", "riverfront_park_beach_v1", profile_id="riverfront-lake-beach-lego-v1", appearance_kit_id="riverfront_park_beach_v1_lake_swimming_skin", planting_structure="riverfront_lake_beach_v1", compatibility=_RIVERFRONT_LAKE_BEACH_ENVELOPE, components=("lake_beach_ground_program_v1", "crescent_sand_beach_v1", "t_swimming_dock_v1", "kayak_rack_v1", "bathhouse_reservation_pad_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_reclaimed_wharf_v0", kind="park", title="Reclaimed Industrial Wharf v0", generator="park_kit",
        selections=(_selection("reclaimed_industrial_park", "reclaimed_industrial_park_v0", profile_id="reclaimed-industrial-wharf-lego-v1", appearance_kit_id="reclaimed_industrial_park_v0_wharf_skin", planting_structure="reclaimed_wharf_v0", compatibility=_RECLAIMED_WHARF_ENVELOPE, components=("reclaimed_wharf_ground_program_v1", "continuous_wharf_walk_v1", "whole_dock_crane_modules_v1", "native_planting_strip_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_quarry_tier_cascade_v2", kind="park", title="Quarry Limestone Tier Cascade v2", generator="park_kit",
        selections=(_selection("quarry_sunken_garden_park", "quarry_sunken_garden_park_v2", profile_id="quarry-tier-cascade-lego-v1", appearance_kit_id="quarry_sunken_garden_park_v2_tier_cascade_skin", planting_structure="quarry_tier_cascade_v2", compatibility=_QUARRY_TIER_CASCADE_ENVELOPE, components=("quarry_bowl_ground_program_v1", "whole_garden_terraces_v1", "linked_reflecting_basins_v1", "limestone_cascade_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_estate_oak_picnic_v1", kind="park", title="Estate Oak Picnic Grove v1", generator="park_kit",
        selections=(_selection("estate_picnic_grove", "estate_picnic_grove_v1", profile_id="estate-oak-picnic-lego-v1", appearance_kit_id="estate_picnic_grove_v1_oak_skin", planting_structure="estate_oak_picnic_v1", compatibility=_ESTATE_OAK_PICNIC_ENVELOPE, components=("oak_grove_ground_program_v1", "complete_oak_picnic_station_v1", "central_play_lawn_v1", "crushed_stone_loop_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_constructed_wetland_boardwalk_v0", kind="park", title="Constructed Urban Boardwalk Wetland v0", generator="park_kit",
        selections=(_selection("constructed_wetland_eco_park", "constructed_wetland_eco_park_variant_0", profile_id="constructed-wetland-boardwalk-lego-v1", appearance_kit_id="constructed_wetland_eco_park_v0_boardwalk_skin", planting_structure="constructed_wetland_boardwalk_v0", compatibility=_CONSTRUCTED_WETLAND_BOARDWALK_ENVELOPE, components=("wetland_mosaic_ground_program_v1", "complete_treatment_cells_v1", "zigzag_boardwalk_v1", "viewing_deck_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_academic_planted_court_v0", kind="park", title="Academic Modern Planted Courtyard v0", generator="park_kit",
        selections=(_selection("academic_courtyard", "academic_courtyard_variant_0", profile_id="academic-planted-courtyard-lego-v1", appearance_kit_id="academic_courtyard_v0_planted_skin", planting_structure="academic_planted_court_v0", compatibility=_ACADEMIC_PLANTED_COURT_ENVELOPE, components=("academic_court_ground_program_v1", "whole_raised_planters_v1", "integrated_seat_ledges_v1", "clear_cross_routes_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_campus_green_spine_v0", kind="park", title="Campus Green Pedestrian Spine v0", generator="park_kit",
        selections=(_selection("campus_pedestrian_spine", "campus_pedestrian_spine_variant_0", profile_id="campus-green-spine-lego-v1", appearance_kit_id="campus_pedestrian_spine_v0_green_skin", planting_structure="campus_green_spine_v0", compatibility=_CAMPUS_GREEN_SPINE_ENVELOPE, components=("campus_spine_ground_program_v1", "continuous_accessible_axis_v1", "rain_garden_bands_v1", "repeating_tree_bays_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_botanical_rose_garden_v3", kind="park", title="Botanical Romantic Rose Garden v3", generator="park_kit",
        selections=(_selection("botanical_garden", "botanical_garden_v3", profile_id="botanical-rose-garden-lego-v1", appearance_kit_id="botanical_garden_v3_rose_skin", planting_structure="botanical_rose_garden_v3", compatibility=_BOTANICAL_ROSE_GARDEN_ENVELOPE, components=("rose_garden_ground_program_v1", "complete_flower_rooms_v1", "timber_rose_arbors_v1", "brick_stone_walk_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_research_arboretum_v0", kind="park", title="Research Teaching Arboretum v0", generator="park_kit",
        selections=(_selection("research_garden_teaching_arboretum", "research_garden_teaching_arboretum_variant_0", profile_id="research-arboretum-lego-v1", appearance_kit_id="research_garden_teaching_arboretum_v0_skin", planting_structure="research_arboretum_v0", compatibility=_RESEARCH_ARBORETUM_ENVELOPE, components=("arboretum_ground_program_v1", "specimen_tree_collection_v1", "interpretive_loop_v1", "label_and_boulder_nodes_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_rewilding_reforestation_v1", kind="park", title="Rewilding Reforestation Zone v1", generator="park_kit",
        selections=(_selection("rewilding_ecological_restoration_zone", "rewilding_ecological_restoration_zone_variant_1", profile_id="rewilding-reforestation-lego-v1", appearance_kit_id="rewilding_ecological_restoration_zone_v1_skin", planting_structure="rewilding_reforestation_v1", compatibility=_REWILDING_REFORESTATION_ENVELOPE, components=("reforestation_ground_program_v1", "sapling_cohort_matrix_v1", "native_understory_v1", "habitat_log_piles_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_stormwater_arid_channel_v3", kind="park", title="Stormwater Arid Rock Channel v3", generator="park_kit",
        selections=(_selection("stormwater_resilience_park", "stormwater_resilience_park_variant_3", profile_id="stormwater-arid-channel-lego-v1", appearance_kit_id="stormwater_resilience_park_v3_arid_skin", planting_structure="stormwater_arid_channel_v3", compatibility=_STORMWATER_ARID_CHANNEL_ENVELOPE, components=("arid_resilience_ground_program_v1", "continuous_ephemeral_channel_v1", "gravel_detention_pockets_v1", "xeric_planting_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_urban_pocket_rustic_v0", kind="park", title="Urban Pocket Park / Rustic Timber v0", generator="park_kit",
        selections=(_selection("urban_pocket_park", "urban_pocket_park_v0", profile_id="urban-pocket-rustic-lego-v1", appearance_kit_id="urban_pocket_park_v0_rustic_skin", planting_structure="urban_pocket_rustic_v0", compatibility=_URBAN_POCKET_RUSTIC_ENVELOPE, components=("rustic_pocket_ground_program_v1", "whole_pergola_bay_v1", "split_rail_edge_v1", "boulder_seat_cluster_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_neighborhood_contemporary_v3", kind="park", title="Neighborhood Park / Urban Contemporary v3", generator="park_kit",
        selections=(_selection("neighborhood_park", "neighborhood_park_v3", profile_id="neighborhood-contemporary-lego-v1", appearance_kit_id="neighborhood_park_v3_contemporary_skin", planting_structure="neighborhood_contemporary_v3", compatibility=_NEIGHBORHOOD_CONTEMPORARY_ENVELOPE, components=("contemporary_neighborhood_ground_program_v1", "whole_social_room_v1", "water_jet_pad_v1", "raised_planter_bays_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_cemetery_classical_v0", kind="park", title="Cemetery / Classical Formal v0", generator="park_kit",
        selections=(_selection("cemetery_memorial_grounds", "cemetery_memorial_grounds_v0", profile_id="cemetery-classical-lego-v1", appearance_kit_id="cemetery_memorial_grounds_v0_classical_skin", planting_structure="cemetery_classical_v0", compatibility=_CEMETERY_CLASSICAL_ENVELOPE, components=("classical_memorial_ground_program_v1", "axial_allee_v1", "whole_memorial_rows_v1", "fountain_parterre_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_courtyard_linear_water_v1", kind="park", title="Courtyard / Contemporary Linear Water v1", generator="park_kit",
        selections=(_selection("courtyard_plaza", "courtyard_plaza_v1", profile_id="courtyard-linear-water-lego-v1", appearance_kit_id="courtyard_plaza_v1_linear_water_skin", planting_structure="courtyard_linear_water_v1", compatibility=_COURTYARD_LINEAR_WATER_ENVELOPE, components=("linear_water_court_ground_program_v1", "continuous_rill_v1", "concrete_seat_walls_v1", "specimen_tree_grates_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_parklet_sf_timber_v1", kind="park", title="Street Parklet / SF Timber v1", generator="park_kit",
        selections=(_selection("street_plaza_parklet", "street_plaza_parklet_v1", profile_id="parklet-sf-timber-lego-v1", appearance_kit_id="street_plaza_parklet_v1_sf_timber_skin", planting_structure="parklet_sf_timber_v1", compatibility=_PARKLET_SF_TIMBER_ENVELOPE, components=("timber_parklet_ground_program_v1", "slat_guard_edge_v1", "cafe_table_bay_v1", "terracotta_planter_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_french_parterre_axis_v1", kind="park", title="Jardin a la Francaise / Water Axis v1", generator="park_kit",
        selections=(_selection("parisian_jardin", "parisian_jardin_v1", profile_id="french-parterre-axis-lego-v1", appearance_kit_id="parisian_jardin_v1_water_axis_skin", planting_structure="french_parterre_axis_v1", compatibility=_FRENCH_PARTERRE_AXIS_ENVELOPE, components=("french_garden_ground_program_v1", "continuous_water_axis_v1", "mirrored_parterre_rooms_v1", "clipped_topiary_bays_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_london_railed_square_v1", kind="park", title="London Garden Square / Railed Garden v1", generator="park_kit",
        selections=(_selection("london_garden_square", "london_garden_square_v1", profile_id="london-railed-square-lego-v1", appearance_kit_id="london_garden_square_v1_railed_skin", planting_structure="london_railed_square_v1", compatibility=_LONDON_RAILED_SQUARE_ENVELOPE, components=("london_square_ground_program_v1", "continuous_iron_rail_v1", "central_lawn_room_v1", "perimeter_tree_walk_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_halifax_rose_bandstand_v0", kind="park", title="Halifax Public Gardens / Rose Garden v0", generator="park_kit",
        selections=(_selection("halifax_public_gardens", "halifax_public_gardens_v0", profile_id="halifax-rose-bandstand-lego-v1", appearance_kit_id="halifax_public_gardens_v0_rose_skin", planting_structure="halifax_rose_bandstand_v0", compatibility=_HALIFAX_ROSE_BANDSTAND_ENVELOPE, components=("victorian_garden_ground_program_v1", "whole_rose_bed_rooms_v1", "ornate_bandstand_v1", "wrought_iron_gate_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_olmsted_multilandscape_v3", kind="park", title="Olmsted Park / Central Park Multi-Landscape v3", generator="park_kit",
        selections=(_selection("picturesque_olmsted_park", "picturesque_olmsted_park_v3", profile_id="olmsted-multilandscape-lego-v1", appearance_kit_id="picturesque_olmsted_park_v3_multilandscape_skin", planting_structure="olmsted_multilandscape_v3", compatibility=_OLMSTED_MULTILANDSCAPE_ENVELOPE, components=("olmsted_ground_program_v1", "whole_landscape_rooms_v1", "rustic_bow_bridge_v1", "elm_mall_bays_v1"), default=True),),
    ),
    PublicRealmFamilyCapability(
        family_id="park_hilltop_viewpoint_v3", kind="park", title="Hilltop Park / Pacific Terraced Viewpoint v3", generator="park_kit",
        selections=(_selection("hilltop_topographic_park", "hilltop_topographic_park_v3", profile_id="hilltop-viewpoint-lego-v1", appearance_kit_id="hilltop_topographic_park_v3_viewpoint_skin", planting_structure="hilltop_viewpoint_v3", compatibility=_HILLTOP_VIEWPOINT_ENVELOPE, components=("hilltop_ground_program_v1", "continuous_switchback_trail_v1", "whole_viewpoint_decks_v1", "cedar_fir_slope_v1"), default=True),),
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
    # An explicitly selected variant should resolve to its reviewed one-family
    # compiler when both that exact compiler and an older multi-variant
    # fallback advertise the same catalog identity. Without an explicit
    # variant, retain the established generic/default family behaviour.
    def selection_rank(pair: tuple[PublicRealmFamilyCapability, PublicRealmSelectionCapability]) -> tuple[int, str, str]:
        capability, selection = pair
        exact_family_rank = 0 if request.variant_id is not None and len(capability.selections) == 1 else 1
        return exact_family_rank, capability.family_id, selection.variant_id

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
            key=selection_rank,
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
        key=selection_rank,
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


def _metric_polygon_contains_fixed_park_program(
    geometry: BaseGeometry,
    *,
    width_m: float,
    depth_m: float,
    clearance_m: float,
) -> bool:
    """Prove that a fixed park program rectangle fits without scaling.

    The capability envelope rejects obviously wrong parcels cheaply. This
    geometry-aware pass handles concave and clipped sites whose rotated bounds
    look large enough even though the complete archetype program is not.
    Candidate orientations come from real parcel edges; candidate centres use
    a bounded deterministic grid so API compilation and Direct revalidation
    make the same decision.
    """

    receiving = geometry.buffer(-clearance_m)
    if receiving.is_empty:
        return False
    min_x, min_y, max_x, max_y = receiving.bounds
    if max_x - min_x < min(width_m, depth_m) or max_y - min_y < min(width_m, depth_m):
        return False

    angles: set[float] = {0.0, 90.0}
    exterior = getattr(geometry, "exterior", None)
    coordinates = list(exterior.coords) if exterior is not None else []
    for index in range(max(0, len(coordinates) - 1)):
        start = coordinates[index]
        end = coordinates[index + 1]
        length = math.dist(start, end)
        if length < 2.0:
            continue
        angle = math.degrees(math.atan2(end[1] - start[1], end[0] - start[0])) % 180.0
        angles.add(round(angle, 6))
        angles.add(round((angle + 90.0) % 180.0, 6))

    centroid = receiving.centroid
    x_values = [centroid.x] + [min_x + (max_x - min_x) * index / 8 for index in range(9)]
    y_values = [centroid.y] + [min_y + (max_y - min_y) * index / 8 for index in range(9)]
    base = box(
        -width_m / 2,
        -depth_m / 2,
        width_m / 2,
        depth_m / 2,
    )
    for angle in sorted(angles):
        rotated = affinity.rotate(base, angle, origin=(0, 0), use_radians=False)
        for center_x in x_values:
            for center_y in y_values:
                candidate = affinity.translate(rotated, xoff=center_x, yoff=center_y)
                if receiving.covers(candidate):
                    return True
    return False


def _metric_polygon_contains_skate_park_v0(geometry: BaseGeometry) -> bool:
    """Backward-compatible wrapper retained for focused callers/tests."""
    return _metric_polygon_contains_fixed_park_program(
        geometry,
        width_m=_SKATE_PARK_V0_WIDTH_M,
        depth_m=_SKATE_PARK_V0_DEPTH_M,
        clearance_m=_SKATE_PARK_V0_CLEARANCE_M,
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
    exact_variant_id = variant_id or next((
        candidate_variant
        for candidate_archetype, candidate_variant in _EXACT_PARK_PROGRAMS
        if candidate_archetype == archetype_id
    ), None)
    exact_program = _EXACT_PARK_PROGRAMS.get((archetype_id, exact_variant_id or ""))
    if exact_program is not None:
        program_width_m, program_depth_m, clearance_m = exact_program
        if not _metric_polygon_contains_fixed_park_program(
            metric_geometry,
            width_m=program_width_m,
            depth_m=program_depth_m,
            clearance_m=clearance_m,
        ):
            error = PublicRealmPlanningError(
                f"{archetype_id} requires one complete, unscaled {program_width_m:g} x {program_depth_m:g} m program inside the parcel.",
                code="family_incompatible",
                requested={
                    "archetype_id": archetype_id,
                    "variant_id": exact_variant_id,
                    "target": target.model_dump(mode="json"),
                },
                supported_families=[
                    _family_summary(capability)
                    for capability, selection in matching
                    if selection.variant_id == exact_variant_id
                ],
                violations=[{
                    "field": "target.polygon_fit",
                    "requested": "irregular polygon",
                    "supported": {
                        "program_width_m": program_width_m,
                        "program_depth_m": program_depth_m,
                        "minimum_clearance_m": clearance_m,
                        "scale": 1.0,
                    },
                }],
            )
            if strict:
                raise error
            return None
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
