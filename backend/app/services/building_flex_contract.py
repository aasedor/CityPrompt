"""Trusted finite building footprint contracts.

Client properties identify a selected programme and scale, but do not define
native dimensions or limits. Those values come from server-owned contracts
(the hash-pinned manifest for low-rise houses), so a saved zone cannot enlarge
an arbitrary model by supplying its own claimed approval band.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "seed/model-library/rlasm-architectural-clay/house-flex-pilot-v001.json"
TOWER_CONTRACTS = ROOT / "frontend/src/data/localTowerStoreyPrograms.json"

# --- Building resize pilot -------------------------------------------------
# The id is spelled here so an ordinary building never has to open the trial
# manifest. The manifest is packaged with the backend and mirrors
# frontend/src/data/buildingResizeTrial.json byte for byte.
RESIZE_TRIAL_PROGRAM_ID = "building-resize-trial-v001"
RESIZE_TRIAL_MANIFEST = Path(__file__).resolve().parents[1] / "data/buildingResizeTrial.json"
RESIZE_TRIAL_SCHEMA = "cityprompt.building-resize-trial@1"
RESIZE_TRIAL_EXACT_MODEL = "exact_model"
RESIZE_TRIAL_SHAPE_FREELY = "shape_freely"
# Hard ceiling for any tuned band. The manifest may narrow it, never widen it.
RESIZE_TRIAL_SCALE_FLOOR = 0.5
RESIZE_TRIAL_SCALE_CEILING = 1.6
_RESIZE_TRIAL_SCALE_TOLERANCE = 1e-9
_RESIZE_TRIAL_OUTLINE_TOLERANCE_M = 0.02


@lru_cache(maxsize=1)
def _tower_contracts() -> dict[str, dict[str, Any]]:
    payload = json.loads(TOWER_CONTRACTS.read_text(encoding="utf-8"))
    if payload.get("schema") != "cityprompt.local-tower-storeys@1":
        raise ValueError("Unknown tower programme schema")
    return {row["storeyProgram"]["id"] + "-native-footprint": row for row in payload["programmes"]}


def trusted_building_footprint_target(properties: dict[str, Any]) -> tuple[float, float] | None:
    """Bind an authored model target independently from its reserved plot.

    The local Brick Podium programme repeats unscaled 54 x 44 m geometry
    inside its 57 x 47 m placement plot. Inventory validation still requires
    the installed exact source revision and its executable modules; this
    footprint contract grants neither module availability nor publication.
    """

    declared = properties.get("building_footprint_program_id")
    if declared == RESIZE_TRIAL_PROGRAM_ID and building_resize_trial_enabled():
        return trusted_resize_trial_footprint_target(properties)
    tower = (
        _tower_contracts().get(declared)
        if isinstance(declared, str) and declared.endswith("-native-footprint")
        else None
    )
    if tower:
        if (
            properties.get("pick_place_asset") != tower["assetId"]
            or properties.get("development_selected_variant_id") != tower["variantId"]
            or properties.get("pick_place_model_revision") != tower["sourceRevision"]
        ):
            raise ValueError("The selected building revision is not part of this tower programme")
        try:
            scale = float(properties["building_footprint_scale"])
            floors = float(properties.get("floor_count", properties.get("floors")))
            height = float(
                properties.get("development_height_override_m", properties.get("height_m", properties.get("height")))
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("The tower scale, storeys or height is missing or invalid") from exc
        program = tower["storeyProgram"]
        expected = (
            program["podiumHeightM"]
            + (floors - program["podiumStoreys"]) * program["repeatedStoreyHeightM"]
            + program["roofHeightM"]
        )
        if (
            not math.isfinite(scale)
            or scale != 1
            or not math.isfinite(floors)
            or not floors.is_integer()
            or not program["minStoreys"] <= floors <= program["maxStoreys"]
            or ("supportedStoreys" in program and floors not in program["supportedStoreys"])
            or not math.isfinite(height)
            or abs(height - expected) > 0.05
        ):
            raise ValueError("The tower dimensions are outside its authored storey programme")
        return tower["nativeWidthM"], tower["nativeDepthM"]
    if properties.get("building_footprint_program_id") != "brick-podium-condo-native-footprint-v001":
        return trusted_house_footprint_target(properties)
    if (
        properties.get("pick_place_asset") != "claude_trial_brick_podium_condo_tower"
        or properties.get("development_selected_variant_id") != "brick_podium_glass_tower"
        or properties.get("pick_place_model_revision") != "clay-brick-podium-condo-tower-clay-v006"
    ):
        raise ValueError("The selected building revision is not part of this footprint programme")
    try:
        scale = float(properties["building_footprint_scale"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("The building footprint scale is missing or invalid") from exc
    if not math.isfinite(scale) or scale != 1:
        raise ValueError("The building footprint scale is outside the reviewed range")
    return 54.0, 44.0


@lru_cache(maxsize=1)
def _contracts() -> tuple[str, float, float, dict[str, tuple[float, float]]]:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if payload.get("schema") != "cityprompt.authored-lowrise-storey-program@1":
        raise ValueError("Unknown low-rise building programme schema")
    footprint = payload["footprint_contract"]
    if footprint.get("mode") != "uniform_horizontal_scale" or footprint.get("vertical_scale") != 1.0:
        raise ValueError("Low-rise programme must retain unit vertical scale")
    minimum = float(footprint["minimum_scale"])
    maximum = float(footprint["maximum_scale"])
    if not (0.75 <= minimum <= 1.0 <= maximum <= 1.25):
        raise ValueError("Low-rise footprint band is outside the bounded runtime range")
    families: dict[str, tuple[float, float]] = {}
    for family in payload["families"]:
        assemblies = family["assemblies"]
        widths = {round(float(row["native_dimensions_m"][0]), 6) for row in assemblies}
        depths = {round(float(row["native_dimensions_m"][1]), 6) for row in assemblies}
        if len(widths) != 1 or len(depths) != 1:
            raise ValueError(f"Storey assemblies changed footprint for {family['variant_id']}")
        families[str(family["variant_id"])] = (
            float(assemblies[0]["native_dimensions_m"][0]),
            float(assemblies[0]["native_dimensions_m"][1]),
        )
    return str(payload["id"]), minimum, maximum, families


def trusted_house_footprint_target(properties: dict[str, Any]) -> tuple[float, float] | None:
    """Return trusted model dimensions for a declared pilot scale.

    A missing or unrelated programme remains on the ordinary drawn-footprint
    path.  A known programme with an invalid variant or scale fails closed.
    """

    program_id, minimum, maximum, families = _contracts()
    declared = properties.get("building_footprint_program_id")
    if declared != program_id:
        return None
    variant = properties.get("development_selected_variant_id")
    if not isinstance(variant, str) or variant not in families:
        raise ValueError("The selected building is not part of this footprint programme")
    try:
        scale = float(properties["building_footprint_scale"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("The building footprint scale is missing or invalid") from exc
    if not math.isfinite(scale) or not minimum <= scale <= maximum:
        raise ValueError("The building footprint scale is outside the reviewed range")
    width, depth = families[variant]
    # Retain the hash-pinned GLB dimensions at full precision. Rounding a
    # target on the edge of the approved band (for example 115%) can move the
    # recomputed ratio a few millionths above the limit and make a freshly
    # planned recipe look different during the server's final lock check.
    return width * scale, depth * scale


# ---------------------------------------------------------------------------
# Building resize pilot (ENABLE_BUILDING_RESIZE_TRIAL, default off)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ResizeTrialFamily:
    """One exact, hash-pinned model that the pilot may stretch."""

    asset_id: str
    archetype_id: str
    variant_id: str
    candidate: str
    sha256: str
    native_width_m: float
    native_depth_m: float
    native_height_m: float
    native_storeys: int


@dataclass(frozen=True)
class ResizeTrialContract:
    """Server-owned limits. Client properties select a state; they never define one."""

    program_id: str
    minimum_scale: float
    maximum_scale: float
    minimum_width_m: float
    minimum_depth_m: float
    minimum_area_m2: float
    maximum_size_m: float
    maximum_outline_points: int
    families: tuple[ResizeTrialFamily, ...]

    def family_for_properties(self, properties: dict[str, Any]) -> ResizeTrialFamily | None:
        for family in self.families:
            if (
                properties.get("pick_place_asset") == family.asset_id
                and properties.get("development_selected_variant_id") == family.variant_id
                and properties.get("pick_place_model_revision") == family.candidate
            ):
                return family
        return None

    def family_for_module(self, module: Any) -> ResizeTrialFamily | None:
        """Match the installed library row by exact variant, candidate and bytes."""

        if (
            getattr(module, "role", None) != "assembled"
            or getattr(module, "repeatable_z", True)
            or getattr(module, "delivery_format", None) != "architectural_clay"
        ):
            return None
        for family in self.families:
            if (
                getattr(module, "source_variant_id", None) == family.variant_id
                and getattr(module, "model_revision", None) == family.candidate
                and getattr(module, "model_sha256", None) == family.sha256
            ):
                return family
        return None

    def scale_in_band(self, scale: float) -> bool:
        return (
            math.isfinite(scale)
            and self.minimum_scale - _RESIZE_TRIAL_SCALE_TOLERANCE
            <= scale
            <= self.maximum_scale + _RESIZE_TRIAL_SCALE_TOLERANCE
        )


@dataclass(frozen=True)
class ResizeTrialState:
    """A validated saved state for one trial building."""

    family: ResizeTrialFamily
    mode: str
    width_scale: float
    depth_scale: float


def building_resize_trial_enabled() -> bool:
    from app.core.config import get_settings

    return bool(get_settings().enable_building_resize_trial)


@lru_cache(maxsize=1)
def _resize_trial_manifest() -> ResizeTrialContract:
    payload = json.loads(RESIZE_TRIAL_MANIFEST.read_text(encoding="utf-8"))
    if payload.get("schema") != RESIZE_TRIAL_SCHEMA or payload.get("id") != RESIZE_TRIAL_PROGRAM_ID:
        raise ValueError("Unknown building resize trial manifest")
    stretch = payload["stretch"]
    if stretch.get("mode") != "independent_horizontal_scale" or stretch.get("vertical_scale") != 1.0:
        raise ValueError("The resize trial must keep unit vertical scale")
    minimum = float(stretch["minimum_scale"])
    maximum = float(stretch["maximum_scale"])
    if not (RESIZE_TRIAL_SCALE_FLOOR <= minimum <= 1.0 <= maximum <= RESIZE_TRIAL_SCALE_CEILING):
        raise ValueError("The resize trial band is outside the bounded runtime range")
    shape = payload["shape_freely"]
    minimum_width = float(shape["minimum_width_m"])
    minimum_depth = float(shape["minimum_depth_m"])
    minimum_area = float(shape["minimum_area_m2"])
    maximum_size = float(shape["maximum_size_m"])
    maximum_points = int(shape["maximum_outline_points"])
    if not (
        0 < minimum_width <= maximum_size
        and 0 < minimum_depth <= maximum_size
        and minimum_area > 0
        and 4 <= maximum_points <= 128
    ):
        raise ValueError("The resize trial outline limits are invalid")
    families: list[ResizeTrialFamily] = []
    for row in payload["families"]:
        width, depth, height = (float(value) for value in row["native_dimensions_m"])
        sha256 = str(row["sha256"]).lower()
        storeys = int(row["native_storeys"])
        if (
            len(sha256) != 64
            or any(character not in "0123456789abcdef" for character in sha256)
            or any(not math.isfinite(value) or value <= 0 for value in (width, depth, height))
            or storeys < 1
        ):
            raise ValueError(f"Invalid resize trial family: {row.get('variant_id')}")
        families.append(
            ResizeTrialFamily(
                asset_id=str(row["asset_id"]),
                archetype_id=str(row["archetype_id"]),
                variant_id=str(row["variant_id"]),
                candidate=str(row["candidate"]),
                sha256=sha256,
                native_width_m=width,
                native_depth_m=depth,
                native_height_m=height,
                native_storeys=storeys,
            )
        )
    if not families or len({family.asset_id for family in families}) != len(families):
        raise ValueError("The resize trial needs distinct families")
    return ResizeTrialContract(
        program_id=RESIZE_TRIAL_PROGRAM_ID,
        minimum_scale=minimum,
        maximum_scale=maximum,
        minimum_width_m=minimum_width,
        minimum_depth_m=minimum_depth,
        minimum_area_m2=minimum_area,
        maximum_size_m=maximum_size,
        maximum_outline_points=maximum_points,
        families=tuple(families),
    )


def resize_trial_contract(program_id: Any = RESIZE_TRIAL_PROGRAM_ID) -> ResizeTrialContract | None:
    """The explicit trial contract, or None while the server flag is off."""

    if program_id != RESIZE_TRIAL_PROGRAM_ID or not building_resize_trial_enabled():
        return None
    return _resize_trial_manifest()


def resize_trial_state(properties: dict[str, Any] | None) -> ResizeTrialState | None:
    """Validate a saved trial state.

    Unrelated buildings, and every building while the flag is off, return None
    and keep their ordinary behaviour. A building that declares the trial
    programme with a wrong identity, mode or scale fails closed.
    """

    properties = properties or {}
    if properties.get("building_footprint_program_id") != RESIZE_TRIAL_PROGRAM_ID:
        return None
    contract = resize_trial_contract()
    if contract is None:
        return None
    family = contract.family_for_properties(properties)
    if family is None:
        raise ValueError("The selected building revision is not part of the resize trial")
    mode = properties.get("building_footprint_mode")
    if mode == RESIZE_TRIAL_SHAPE_FREELY:
        return ResizeTrialState(family, RESIZE_TRIAL_SHAPE_FREELY, 1.0, 1.0)
    if mode != RESIZE_TRIAL_EXACT_MODEL:
        raise ValueError("The building resize mode is missing or invalid")
    try:
        width_scale = float(properties["building_footprint_width_scale"])
        depth_scale = float(properties["building_footprint_depth_scale"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("The building width or depth scale is missing or invalid") from exc
    if isinstance(properties["building_footprint_width_scale"], bool) or isinstance(
        properties["building_footprint_depth_scale"], bool
    ):
        raise ValueError("The building width or depth scale is missing or invalid")
    if not contract.scale_in_band(width_scale) or not contract.scale_in_band(depth_scale):
        raise ValueError("The building width or depth scale is outside the trial range")
    return ResizeTrialState(family, RESIZE_TRIAL_EXACT_MODEL, width_scale, depth_scale)


def trusted_resize_trial_footprint_target(properties: dict[str, Any]) -> tuple[float, float] | None:
    """Trusted stretched dimensions for Exact model; None for Shape freely.

    Shape freely keeps the drawn polygon as its own target. Native dimensions
    come from the packaged manifest, never from client properties.
    """

    state = resize_trial_state(properties)
    if state is None or state.mode != RESIZE_TRIAL_EXACT_MODEL:
        return None
    return state.family.native_width_m * state.width_scale, state.family.native_depth_m * state.depth_scale


def resize_trial_stretch_program_id(properties: dict[str, Any] | None) -> str | None:
    """Programme id to hand the planner, only for a valid Exact model stretch."""

    state = resize_trial_state(properties)
    return RESIZE_TRIAL_PROGRAM_ID if state is not None and state.mode == RESIZE_TRIAL_EXACT_MODEL else None


def resize_trial_is_shape_freely(properties: dict[str, Any] | None) -> bool:
    """True when the student explicitly chose shaped massing for a trial building."""

    try:
        state = resize_trial_state(properties)
    except ValueError:
        return False
    return state is not None and state.mode == RESIZE_TRIAL_SHAPE_FREELY


def resize_trial_outline_problem(ring: list[tuple[float, float]] | None) -> str | None:
    """Minimum-size guard for a freely shaped outline, in local metres.

    Width runs along the first drawn edge and depth across it, matching the
    browser's outline frame so both sides reject the same shapes.
    """

    contract = resize_trial_contract()
    if contract is None:
        return None
    points = [(float(point[0]), float(point[1])) for point in (ring or [])]
    if len(points) > 3 and math.dist(points[0], points[-1]) < 1e-9:
        points.pop()
    if len(points) < 3 or any(not math.isfinite(value) for point in points for value in point):
        return "A freely shaped building needs at least three finite corners."
    if len(points) > contract.maximum_outline_points:
        return f"A freely shaped building can have at most {contract.maximum_outline_points} corners."
    angle = math.atan2(points[1][1] - points[0][1], points[1][0] - points[0][0])
    cos, sin = math.cos(angle), math.sin(angle)
    along = [x * cos + y * sin for x, y in points]
    across = [-x * sin + y * cos for x, y in points]
    width, depth = max(along) - min(along), max(across) - min(across)
    area = abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(points, points[1:] + points[:1])) / 2)
    tolerance = _RESIZE_TRIAL_OUTLINE_TOLERANCE_M
    if width < contract.minimum_width_m - tolerance or depth < contract.minimum_depth_m - tolerance:
        return (
            f"A freely shaped building must be at least {contract.minimum_width_m:g} m wide "
            f"and {contract.minimum_depth_m:g} m deep."
        )
    if area < contract.minimum_area_m2 - tolerance:
        return f"A freely shaped building needs a footprint of at least {contract.minimum_area_m2:g} m²."
    if max(width, depth) > contract.maximum_size_m + tolerance:
        return f"A freely shaped building can be at most {contract.maximum_size_m:g} m across."
    return None
