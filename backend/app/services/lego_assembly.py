"""Archetype-driven modular building assembly planning.

This experiment deliberately reuses ``ModelLibraryEntry.metadata_`` instead of
introducing a new database table. Library items become modules when their
metadata contains ``lego`` configuration. The planner groups compatible
modules into families and produces a vertical podium/floor/roof recipe.

Expected metadata shape::

    {
      "lego": {
        "enabled": true,
        "role": "podium|floor|setback|crown|roof|attachment|assembled",
        "variant_key": "typical_a",
        "lod": 0,
        "family": "nordic-midrise",
        "width_m": 24,
        "depth_m": 18,
        "height_m": 3.2,
        "repeatable_z": true,
        "archetype_ids": ["nordic-midrise"],
        "reuse_keys": ["nordic", "mixed-use"],
        "min_floors": 3,
        "max_floors": 12
      }
    }
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Iterable, Literal

from app.services.plan_geometry.archetypes import load_dims_table


VALID_ROLES = {"podium", "floor", "setback", "crown", "roof", "attachment", "assembled"}
VALID_FOOTPRINT_PROFILES = {"rectangle", "l_shape", "u_shape", "courtyard"}

# family/role/variant/LOD become storage-key path segments
# so they must be plain slugs — no slashes, dots, or other path syntax.
_FAMILY_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,99}$")
_ROLE_SLUG_RE = re.compile(r"^[a-z][a-z_]{0,29}$")
_VARIANT_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_]{0,49}$")

# Roles the vertical planner is allowed to stack. Anything else (e.g. the
# pre-assembled preview GLB) is stored in the library with enabled=False so it
# is browsable but never picked by ``plan_vertical_assembly``.
STACKABLE_ROLES = ("podium", "floor", "setback", "crown", "roof")

# Exact render-locked landmarks carry their own corners, entrance, crown and
# roof. Preserve that whole-building asset for realistically imprecise parcel
# drawings, but only inside a near-native band. Large or strongly anisotropic
# changes belong to the authored LEGO fallback kit. Individual manifests may
# author a family-specific band inside the assessor's safety ceiling through
# footprint_compatibility.fixedLandmarkScaleBand.
FIXED_LANDMARK_SCALE_MIN = 0.80
FIXED_LANDMARK_SCALE_MAX = 1.20
FIXED_LANDMARK_MAX_AXIS_RATIO = 1.18
# A uniformly scaled landmark does not suffer the per-axis deformation guarded
# by the stricter authored band. Permit a modest additional downscale when the
# complete model still occupies the parcel coherently; beyond this bounded
# contain-fit, use the authored stack/repeat kit.
FIXED_LANDMARK_CONTAIN_SCALE_MIN = 0.62
FIXED_LANDMARK_CONTAIN_MAX_AXIS_RATIO = 2.00
FIXED_LANDMARK_CONTAIN_MAX_ENVELOPE_SCALE = 1.80

# Manifest schema emitted by tools/archetype_compiler/blender_generate.py.
SUPPORTED_MANIFEST_SCHEMA = 4
SUPPORTED_MANIFEST_SCHEMAS = {2, 3, SUPPORTED_MANIFEST_SCHEMA}


@dataclass(frozen=True)
class ModuleDescriptor:
    id: str
    name: str
    model_url: str
    family: str
    role: str
    width_m: float
    depth_m: float
    height_m: float
    archetype_ids: tuple[str, ...]
    reuse_keys: tuple[str, ...]
    min_floors: int | None = None
    max_floors: int | None = None
    setback_min_floors: int | None = None
    repeatable_z: bool = False
    variant_key: str = "default"
    lod: int = 0
    allowed_levels: tuple[int, ...] = ()
    native_floors: int | None = None
    source_variant_id: str | None = None
    generation_archetype_id: str | None = None
    footprint_compatibility: dict[str, Any] | None = None
    placement_contract: dict[str, Any] | None = None
    # The declared width/depth are a placement envelope. The authored mesh may
    # intentionally occupy less of that envelope (setbacks, shoulders, courts,
    # chamfers, entrance recesses, sculptural roofs) and must not be stretched
    # independently back to the parcel edges at runtime.
    allow_inset_footprint: bool = False
    # RLASM semantic-LEGO v4 modules are authored construction pieces, not
    # complete buildings that may be stretched to a polygon.  ``semantic_role``
    # names the horizontal job owned by this GLB; the v4 solver requires one
    # left end, one entrance, one right end, and whole repeatable middle bays.
    assembly_axis: str | None = None
    semantic_role: str | None = None
    repeatable_x: bool = False
    required_once: bool = False
    min_repeats: int | None = None
    max_repeats: int | None = None
    native_repeat_count: int | None = None


@dataclass(frozen=True)
class AssemblyRequest:
    target_width_m: float
    target_depth_m: float
    target_floors: int
    archetype_id: str | None = None
    reuse_keys: tuple[str, ...] = ()
    preferred_family: str | None = None
    allow_setback: bool = True
    footprint_profile: str = "rectangle"
    wing_depth_m: float | None = None


AssemblyPlanningErrorCode = Literal["family_not_found", "family_incompatible"]


class AssemblyPlanningError(ValueError):
    """Raised when no valid modular assembly can be produced.

    ``code`` is a stable API-facing classification. The optional metadata is
    deliberately renderer-neutral so callers can explain an incompatible
    target without parsing the human-readable message.
    """

    def __init__(
        self,
        message: str,
        *,
        code: AssemblyPlanningErrorCode = "family_incompatible",
        requested: dict[str, Any] | None = None,
        supported_families: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.requested = requested
        self.supported_families = supported_families


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _as_int_or_none(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def descriptor_from_library_entry(entry: Any) -> ModuleDescriptor | None:
    """Convert a ModelLibraryEntry-like object into a validated module."""
    metadata = getattr(entry, "metadata_", None) or {}
    lego = metadata.get("lego") if isinstance(metadata, dict) else None
    if not isinstance(lego, dict) or not lego.get("enabled", False):
        return None

    role = str(lego.get("role") or "").strip().lower()
    family = str(lego.get("family") or "").strip()
    if role not in VALID_ROLES or not family:
        return None

    width_m = _as_float(lego.get("width_m"))
    depth_m = _as_float(lego.get("depth_m"))
    height_m = _as_float(lego.get("height_m"))
    if width_m <= 0 or depth_m <= 0 or height_m <= 0:
        return None

    return ModuleDescriptor(
        id=str(entry.id),
        name=str(entry.name),
        model_url=str(entry.model_url),
        family=family,
        role=role,
        width_m=width_m,
        depth_m=depth_m,
        height_m=height_m,
        archetype_ids=tuple(str(v) for v in lego.get("archetype_ids", []) if v),
        reuse_keys=tuple(str(v) for v in lego.get("reuse_keys", []) if v),
        min_floors=_as_int_or_none(lego.get("min_floors")),
        max_floors=_as_int_or_none(lego.get("max_floors")),
        setback_min_floors=_as_int_or_none(lego.get("setback_min_floors")),
        repeatable_z=bool(lego.get("repeatable_z", role == "floor")),
        variant_key=str(lego.get("variant_key") or "default"),
        lod=max(0, _as_int_or_none(lego.get("lod")) or 0),
        allowed_levels=tuple(
            int(value)
            for value in (lego.get("allowed_levels") or [])
            if isinstance(value, (int, float)) and int(value) >= 0
        ),
        native_floors=_as_int_or_none(lego.get("native_floors")),
        source_variant_id=(str(lego.get("source_variant_id")) if lego.get("source_variant_id") else None),
        generation_archetype_id=(
            str(lego.get("generation_archetype_id")) if lego.get("generation_archetype_id") else None
        ),
        footprint_compatibility=(
            lego.get("footprint_compatibility") if isinstance(lego.get("footprint_compatibility"), dict) else None
        ),
        placement_contract=(
            lego.get("placement_contract") if isinstance(lego.get("placement_contract"), dict) else None
        ),
        allow_inset_footprint=bool(lego.get("allow_inset_footprint", False)),
        assembly_axis=(str(lego.get("assembly_axis")) if lego.get("assembly_axis") else None),
        semantic_role=(str(lego.get("semantic_role")) if lego.get("semantic_role") else None),
        repeatable_x=bool(lego.get("repeatable_x", False)),
        required_once=bool(lego.get("required_once", False)),
        min_repeats=_as_int_or_none(lego.get("min_repeats")),
        max_repeats=_as_int_or_none(lego.get("max_repeats")),
        native_repeat_count=_as_int_or_none(lego.get("native_repeat_count")),
    )


def _dimension_score(module: ModuleDescriptor, request: AssemblyRequest) -> float:
    width_ratio = min(module.width_m, request.target_width_m) / max(module.width_m, request.target_width_m)
    depth_ratio = min(module.depth_m, request.target_depth_m) / max(module.depth_m, request.target_depth_m)
    return (width_ratio + depth_ratio) / 2.0


def _semantic_score(module: ModuleDescriptor, request: AssemblyRequest) -> float:
    score = 0.0
    if request.archetype_id and request.archetype_id in module.archetype_ids:
        score += 1.0

    requested_keys = {key.lower() for key in request.reuse_keys}
    module_keys = {key.lower() for key in module.reuse_keys}
    if requested_keys:
        score += len(requested_keys & module_keys) / len(requested_keys)

    if request.preferred_family and module.family == request.preferred_family:
        score += 1.5
    return score


def _semantic_id(value: str) -> str:
    """Normalize catalogue/runtime id punctuation without collapsing variants."""
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _strip_card_variant_suffix(semantic_id: str) -> str:
    """Drop a planner-added ``_variant_<n>`` card suffix.

    Master-plan zones store the selected catalogue card as
    ``<archetype_id>_variant_<n>``. The card index picks artwork, not a
    different building family, so matching must resolve it to the archetype
    itself. Real variant families (e.g. ``nordic_timber_charred_wood``) are
    unaffected — they never use the ``variant_<n>`` spelling.
    """
    return re.sub(r"_variant_\d+$", "", semantic_id)


def _matches_requested_archetype(module: ModuleDescriptor, archetype_id: str) -> bool:
    requested = _strip_card_variant_suffix(_semantic_id(archetype_id))
    candidates = (
        *module.archetype_ids,
        module.source_variant_id,
        module.generation_archetype_id,
    )
    return any(
        _strip_card_variant_suffix(_semantic_id(candidate)) == requested for candidate in candidates if candidate
    )


@lru_cache(maxsize=512)
def _catalog_parent_archetype_id(archetype_id: str) -> str | None:
    """Resolve a known design child to its catalogue parent.

    A user can select a real catalogue child before its independently authored
    LEGO family is imported.  In that bounded case a generic modular family
    explicitly registered to the parent remains a truthful fallback.  Unknown
    IDs never fall back, and an exact imported child family always wins first.
    """

    requested = _strip_card_variant_suffix(_semantic_id(archetype_id))
    for entry in load_dims_table():
        parent_id = str(entry.get("id") or "").strip()
        if not parent_id:
            continue
        if _semantic_id(parent_id) == requested:
            return parent_id
        if any(_semantic_id(str(variant_id)) == requested for variant_id in (entry.get("variant_ids") or ())):
            return parent_id
    return None


def catalog_parent_archetype_id(archetype_id: str) -> str | None:
    """Return the trusted catalogue parent for a parent or exact child ID."""

    return _catalog_parent_archetype_id(archetype_id)


def _is_generic_parent_fallback_family(
    descriptors: Iterable[ModuleDescriptor],
    family: str,
    parent_archetype_id: str,
) -> bool:
    """Reject a sibling-specific family masquerading as a parent fallback.

    Exact variant manifests commonly include their broad catalogue parent in
    ``archetype_ids`` for discovery. That does not make a red-sandstone
    brownstone a truthful fallback for an unbuilt limestone sibling. A parent
    fallback is eligible only when its source/generation identity is absent or
    explicitly the parent itself; independently authored children must wait
    for their own family and use planned massing in the meantime.
    """

    parent = _semantic_id(parent_archetype_id)
    explicit_identities = {
        _semantic_id(identity)
        for module in descriptors
        if module.family == family
        for identity in (module.source_variant_id, module.generation_archetype_id)
        if identity
    }
    return not explicit_identities or explicit_identities == {parent}


def _module_score(module: ModuleDescriptor, request: AssemblyRequest) -> float:
    return _dimension_score(module, request) * 2.0 + _semantic_score(module, request)


def _valid_for_floor_count(module: ModuleDescriptor, floors: int) -> bool:
    if module.min_floors is not None and floors < module.min_floors:
        return False
    if module.max_floors is not None and floors > module.max_floors:
        return False
    return True


def _recommended_range_contains(value: float, recommended: Any) -> bool | None:
    """Return whether a value is inside a declared two-number range.

    ``None`` means the manifest did not provide a usable range, so callers can
    retain the conservative native-dimension fallback.
    """

    if not isinstance(recommended, (list, tuple)) or len(recommended) != 2:
        return None
    lower = _as_float(recommended[0], float("nan"))
    upper = _as_float(recommended[1], float("nan"))
    if not (math.isfinite(lower) and math.isfinite(upper)):
        return None
    return min(lower, upper) <= value <= max(lower, upper)


def _declared_profile_covers_target(
    module: ModuleDescriptor,
    request: AssemblyRequest,
) -> bool:
    """Honor the shape matrix authored and validated with a module family."""

    compatibility = module.footprint_compatibility
    if not isinstance(compatibility, dict):
        return False
    profiles = compatibility.get("profiles")
    profile = profiles.get(request.footprint_profile) if isinstance(profiles, dict) else None
    if not isinstance(profile, dict):
        return False

    width_range = profile.get("recommendedWidth_m")
    depth_range = profile.get("recommendedDepth_m")
    floor_range = profile.get("recommendedFloors")
    direct_width = _recommended_range_contains(request.target_width_m, width_range)
    direct_depth = _recommended_range_contains(request.target_depth_m, depth_range)
    rotated_width = _recommended_range_contains(request.target_depth_m, width_range)
    rotated_depth = _recommended_range_contains(request.target_width_m, depth_range)
    floors = _recommended_range_contains(float(request.target_floors), floor_range)

    dimensions_declared = direct_width is not None and direct_depth is not None
    dimensions_fit = bool((direct_width and direct_depth) or (rotated_width and rotated_depth))
    floors_fit = floors is not False
    return dimensions_declared and dimensions_fit and floors_fit


def _best(
    modules: Iterable[ModuleDescriptor],
    request: AssemblyRequest,
    *,
    forced: bool = False,
) -> ModuleDescriptor | None:
    pool = list(modules)
    candidates = [m for m in pool if _valid_for_floor_count(m, request.target_floors)]
    if not candidates and forced:
        # Forced fit: the authored floor-range is guidance, not a build gate.
        candidates = pool
    if not candidates:
        return None
    return max(candidates, key=lambda module: _module_score(module, request))


def _requested_target_metadata(request: AssemblyRequest) -> dict[str, Any]:
    return {
        "width_m": float(request.target_width_m),
        "depth_m": float(request.target_depth_m),
        "floors": int(request.target_floors),
        "footprint_profile": request.footprint_profile,
    }


def _supported_family_metadata(
    descriptors: list[ModuleDescriptor],
    families: Iterable[str],
) -> list[dict[str, Any]]:
    """Summarize the matching library families for actionable fit guidance."""

    summaries: list[dict[str, Any]] = []
    for family in families:
        modules = [module for module in descriptors if module.family == family]
        if not modules:
            continue
        minimum_floors = [int(module.min_floors) for module in modules if module.min_floors is not None]
        maximum_floors = [int(module.max_floors) for module in modules if module.max_floors is not None]
        native_floors = [int(module.native_floors) for module in modules if module.native_floors is not None]
        summaries.append(
            {
                "family": family,
                "widths_m": sorted({round(float(module.width_m), 4) for module in modules}),
                "depths_m": sorted({round(float(module.depth_m), 4) for module in modules}),
                "min_floors": min(minimum_floors + native_floors) if (minimum_floors or native_floors) else None,
                "max_floors": max(maximum_floors + native_floors) if (maximum_floors or native_floors) else None,
            }
        )
    return summaries


def footprint_segments(
    profile: str,
    width_m: float,
    depth_m: float,
    native_depth_m: float,
    wing_depth_m: float | None = None,
) -> list[dict[str, float | str]]:
    """Describe a polygonal block as positioned rectangular streetwall bars.

    The recipe renderer already supports per-instance translation and rotation;
    this is the missing planning layer that lets the same module family follow
    L, U and closed-court parcels without baking one bespoke GLB per polygon.
    """
    if profile not in VALID_FOOTPRINT_PROFILES:
        raise AssemblyPlanningError(
            f"Unsupported footprint profile '{profile}'. Expected one of {sorted(VALID_FOOTPRINT_PROFILES)}"
        )
    width = float(width_m)
    depth = float(depth_m)
    if profile == "rectangle":
        return [
            {
                "id": "main",
                "centre_x_m": 0.0,
                "centre_y_m": 0.0,
                "length_m": width,
                "thickness_m": depth,
                "rotation_degrees": 0.0,
            }
        ]
    requested = float(wing_depth_m) if wing_depth_m else float(native_depth_m)
    wing = min(max(5.5, requested), max(5.5, min(width, depth) * 0.46))
    segments: list[dict[str, float | str]] = [
        {
            "id": "front",
            "centre_x_m": 0.0,
            "centre_y_m": -(depth - wing) / 2,
            "length_m": width,
            "thickness_m": wing,
            "rotation_degrees": 0.0,
        }
    ]
    if profile == "l_shape":
        segments.append(
            {
                "id": "left_return",
                "centre_x_m": -(width - wing) / 2,
                "centre_y_m": 0.0,
                "length_m": depth,
                "thickness_m": wing,
                "rotation_degrees": 90.0,
            }
        )
    elif profile == "u_shape":
        segments.extend(
            [
                {
                    "id": "left_return",
                    "centre_x_m": -(width - wing) / 2,
                    "centre_y_m": 0.0,
                    "length_m": depth,
                    "thickness_m": wing,
                    "rotation_degrees": 90.0,
                },
                {
                    "id": "right_return",
                    "centre_x_m": (width - wing) / 2,
                    "centre_y_m": 0.0,
                    "length_m": depth,
                    "thickness_m": wing,
                    "rotation_degrees": 90.0,
                },
            ]
        )
    else:
        segments.extend(
            [
                {
                    "id": "rear",
                    "centre_x_m": 0.0,
                    "centre_y_m": (depth - wing) / 2,
                    "length_m": width,
                    "thickness_m": wing,
                    "rotation_degrees": 0.0,
                },
                {
                    "id": "left_return",
                    "centre_x_m": -(width - wing) / 2,
                    "centre_y_m": 0.0,
                    "length_m": depth,
                    "thickness_m": wing,
                    "rotation_degrees": 90.0,
                },
                {
                    "id": "right_return",
                    "centre_x_m": (width - wing) / 2,
                    "centre_y_m": 0.0,
                    "length_m": depth,
                    "thickness_m": wing,
                    "rotation_degrees": 90.0,
                },
            ]
        )
    return segments


def _rectangle_orientation(
    module: ModuleDescriptor,
    request: AssemblyRequest,
    *,
    scale_min: float,
    scale_max: float,
) -> tuple[float, float, float, float, float]:
    """Choose the least-distorted direct or quarter-turned module fit.

    Polygon footprint measurement intentionally reports the long bounding-box
    side as width. A faithfully carved narrow module can therefore arrive as a
    15 x 8 m request even though its authored local axes are 8 x 15 m. Treating
    those numbers as semantic facade/depth axes rejects an exact fit. Returning
    a 90-degree segment keeps the authored axes and texture proportions intact.
    """

    candidates = (
        (
            request.target_width_m / module.width_m,
            request.target_depth_m / module.depth_m,
            0.0,
            request.target_width_m,
            request.target_depth_m,
        ),
        (
            request.target_depth_m / module.width_m,
            request.target_width_m / module.depth_m,
            90.0,
            request.target_depth_m,
            request.target_width_m,
        ),
    )

    def fit_key(candidate: tuple[float, float, float, float, float]) -> tuple:
        scale_x, scale_y, rotation, _, _ = candidate
        valid = scale_min <= scale_x <= scale_max and scale_min <= scale_y <= scale_max
        distortion = (
            abs(math.log(max(scale_x, 1e-9)))
            + abs(math.log(max(scale_y, 1e-9)))
            + 0.5 * abs(math.log(max(scale_x, 1e-9) / max(scale_y, 1e-9)))
        )
        # Preserve the historic direct orientation on an exact quality tie.
        return (not valid, distortion, rotation != 0.0)

    return min(candidates, key=fit_key)


def _fixed_landmark_scale_contract(
    module: ModuleDescriptor,
) -> tuple[float, float, float]:
    """Return a safe, manifest-authored near-native landmark fit contract."""

    footprint = module.footprint_compatibility or {}
    declared = footprint.get("fixedLandmarkScaleBand")
    if not isinstance(declared, dict):
        return (
            FIXED_LANDMARK_SCALE_MIN,
            FIXED_LANDMARK_SCALE_MAX,
            FIXED_LANDMARK_MAX_AXIS_RATIO,
        )

    try:
        scale_min = float(declared.get("scaleMin", FIXED_LANDMARK_SCALE_MIN))
        scale_max = float(declared.get("scaleMax", FIXED_LANDMARK_SCALE_MAX))
        max_axis_ratio = float(declared.get("maxAxisRatio", FIXED_LANDMARK_MAX_AXIS_RATIO))
    except (TypeError, ValueError):
        return (
            FIXED_LANDMARK_SCALE_MIN,
            FIXED_LANDMARK_SCALE_MAX,
            FIXED_LANDMARK_MAX_AXIS_RATIO,
        )

    if not (0.75 <= scale_min <= 1.0 <= scale_max <= 1.25 and 1.0 <= max_axis_ratio <= 1.20):
        return (
            FIXED_LANDMARK_SCALE_MIN,
            FIXED_LANDMARK_SCALE_MAX,
            FIXED_LANDMARK_MAX_AXIS_RATIO,
        )
    return scale_min, scale_max, max_axis_ratio


def _fixed_landmark_is_select_and_place(module: ModuleDescriptor) -> bool:
    """Whether a reviewed landmark forbids the forced-resize escape hatch.

    Current compiler manifests express this twice: the placement contract says
    the complete landmark is fixed/non-resizable, while footprint compatibility
    exposes ``select_and_place`` / ``polygonFit: false`` to older importers.
    Honor either explicit declaration so already-imported families and future
    re-imports share the same runtime behavior.
    """

    placement = module.placement_contract or {}
    footprint = module.footprint_compatibility or {}
    placement_mode = _semantic_id(str(placement.get("mode") or ""))
    footprint_mode = _semantic_id(str(footprint.get("placementMode") or ""))
    fixed_non_resizable = placement_mode == "fixed_landmark" and placement.get("continuous_resize_allowed") is False
    return bool(fixed_non_resizable or footprint_mode == "select_and_place" or footprint.get("polygonFit") is False)


# Streetwall repeat: bars validate against the same relaxed band multi-wing
# profiles already use — repeated bars keep authored facade proportions, so the
# strict single-bar production band would be needlessly conservative here.
_STREETWALL_BAND = (0.62, 1.40)
_MAX_STREETWALL_BARS_ALONG = 4
_MAX_STREETWALL_ROWS_DEEP = 2


def _best_bar_count(scale: float, limit: int, *, forced: bool = False) -> int | None:
    """Bar count whose per-bar scale sits in the repeat band, least distorted.

    Forced mode drops the band requirement and simply returns the count with
    the least per-bar distortion — it always finds an answer.
    """
    lo, hi = _STREETWALL_BAND
    best: tuple[float, int] | None = None
    for count in range(1, limit + 1):
        per_bar = scale / count
        if not forced and not (lo <= per_bar <= hi):
            continue
        distortion = abs(math.log(max(per_bar, 1e-9)))
        if best is None or distortion < best[0]:
            best = (distortion, count)
    return best[1] if best else None


def _rectangle_repeat_segments(
    module: ModuleDescriptor,
    request: AssemblyRequest,
    *,
    forced: bool = False,
) -> list[dict[str, float | str]] | None:
    """Cover an out-of-band rectangle with a grid of abutting module bars.

    A parcel too large for one stretched module (e.g. 46 m frontage against a
    30 m native facade) is planned as repeated streetwall bars along the long
    axis — and up to two back-to-back rows for deep double-loaded blocks. The
    module facades are authored to tile, and the composer already places every
    instance by per-segment position/rotation. Outside forced mode a 1x1 grid
    is never returned: single bars must pass the strict band, not sneak
    through the repeat band. Forced mode always returns the least-distorted
    configuration, including a plain stretched single bar.
    """
    best: tuple[float, list[dict[str, float | str]]] | None = None
    for rotation, length, thickness in (
        (0.0, request.target_width_m, request.target_depth_m),
        (90.0, request.target_depth_m, request.target_width_m),
    ):
        scale_len = length / module.width_m
        scale_thk = thickness / module.depth_m
        bars_along = _best_bar_count(scale_len, _MAX_STREETWALL_BARS_ALONG, forced=forced)
        rows_deep = _best_bar_count(scale_thk, _MAX_STREETWALL_ROWS_DEEP, forced=forced)
        if bars_along is None or rows_deep is None:
            continue
        if not forced and bars_along * rows_deep == 1:
            continue
        distortion = abs(math.log(scale_len / bars_along)) + abs(math.log(scale_thk / rows_deep))
        if best is not None and distortion >= best[0]:
            continue
        bar_length = length / bars_along
        bar_thickness = thickness / rows_deep
        theta = math.radians(rotation)
        segments: list[dict[str, float | str]] = []
        for row in range(rows_deep):
            v = -thickness / 2 + bar_thickness * (row + 0.5)
            for col in range(bars_along):
                u = -length / 2 + bar_length * (col + 0.5)
                segments.append(
                    {
                        "id": f"bar_r{row}_c{col}",
                        "centre_x_m": round(u * math.cos(theta) - v * math.sin(theta), 4),
                        "centre_y_m": round(u * math.sin(theta) + v * math.cos(theta), 4),
                        "length_m": bar_length,
                        "thickness_m": bar_thickness,
                        "rotation_degrees": rotation,
                    }
                )
        best = (distortion, segments)
    return best[1] if best else None


_SEMANTIC_BAY_FIXED_ROLES = ("left_end", "entrance", "right_end")


def _semantic_bay_grid_plan(
    family_modules: list[ModuleDescriptor],
    request: AssemblyRequest,
) -> dict[str, Any] | None:
    """Assemble an RLASM v4 frontage from fixed anchors and whole bays.

    No transform scale is computed here.  The drawn polygon is a site envelope:
    fixed architectural anchors retain their authored dimensions, middle bays
    repeat as complete GLBs, and any fractional remainder becomes a symmetric
    setback.  A target that cannot hold the construction kit returns ``None``
    so the caller can reject it instead of entering the legacy forced-fit path.
    """

    semantic_modules = [
        module
        for module in family_modules
        if module.assembly_axis == "x" and module.semantic_role
    ]
    if not semantic_modules:
        return None
    if request.footprint_profile != "rectangle":
        return None

    by_role: dict[str, list[ModuleDescriptor]] = {}
    for module in semantic_modules:
        by_role.setdefault(str(module.semantic_role), []).append(module)
    if any(role not in by_role for role in (*_SEMANTIC_BAY_FIXED_ROLES, "middle")):
        return None

    fixed: dict[str, ModuleDescriptor] = {}
    for role in _SEMANTIC_BAY_FIXED_ROLES:
        candidates = [
            module
            for module in by_role[role]
            if module.required_once and _valid_for_floor_count(module, request.target_floors)
        ]
        if not candidates:
            return None
        fixed[role] = max(candidates, key=lambda module: (_module_score(module, request), -module.lod))

    middle_variants = [
        module
        for module in by_role["middle"]
        if module.repeatable_x and _valid_for_floor_count(module, request.target_floors)
    ]
    if not middle_variants:
        return None
    # Preserve authored variant order while keeping one best render LOD for
    # each identity.  This is visual alternation, never a dimensional choice.
    selected_middle = [
        max(
            (candidate for candidate in middle_variants if candidate.variant_key == variant),
            key=lambda module: (_module_score(module, request), -module.lod),
        )
        for variant in sorted({module.variant_key for module in middle_variants})
    ]
    bay_width = selected_middle[0].width_m
    native_depth = max(
        module.depth_m for module in (*fixed.values(), *selected_middle)
    )
    if any(not math.isclose(module.width_m, bay_width, abs_tol=1e-4) for module in selected_middle):
        return None
    if any(not math.isclose(module.depth_m, native_depth, abs_tol=1e-4) for module in (*fixed.values(), *selected_middle)):
        return None

    fixed_width = sum(module.width_m for module in fixed.values())
    minimum_repeats = max(module.min_repeats or 0 for module in selected_middle)
    maximum_repeats = min(module.max_repeats or 64 for module in selected_middle)
    native_repeats = max(module.native_repeat_count or minimum_repeats for module in selected_middle)

    candidates: list[tuple[float, float, float]] = []
    for rotation, available_width, available_depth in (
        (0.0, request.target_width_m, request.target_depth_m),
        (90.0, request.target_depth_m, request.target_width_m),
    ):
        if available_depth + 1e-6 < native_depth or available_width + 1e-6 < fixed_width:
            continue
        repeat_count = min(maximum_repeats, int(math.floor((available_width - fixed_width + 1e-6) / bay_width)))
        # Entrance-centred kits add bays in balanced pairs.  Keeping the native
        # parity prevents a supposedly rational wider building from walking
        # the one public entrance off its authored datum.
        if (repeat_count - native_repeats) % 2:
            repeat_count -= 1
        if repeat_count < minimum_repeats:
            continue
        occupied_width = fixed_width + repeat_count * bay_width
        candidates.append((available_width - occupied_width, rotation, float(repeat_count)))
    if not candidates:
        return None

    # Polygon measurement reports the long axis as width in normal City Prompt
    # placement. Preserve that authored street frontage whenever it fits;
    # quarter-turn only rescues a genuinely transposed narrow rectangle.
    remainder, rotation, repeat_count_float = min(candidates, key=lambda item: (item[1] != 0.0, item[0]))
    repeat_count = int(repeat_count_float)
    occupied_width = fixed_width + repeat_count * bay_width
    available_width = request.target_width_m if rotation == 0.0 else request.target_depth_m
    available_depth = request.target_depth_m if rotation == 0.0 else request.target_width_m
    left_count = repeat_count // 2
    right_count = repeat_count - left_count
    sequence: list[ModuleDescriptor] = [fixed["left_end"]]
    sequence.extend(selected_middle[index % len(selected_middle)] for index in range(left_count))
    sequence.append(fixed["entrance"])
    sequence.extend(
        selected_middle[(left_count + index) % len(selected_middle)] for index in range(right_count)
    )
    sequence.append(fixed["right_end"])

    theta = math.radians(rotation)
    cursor = -occupied_width / 2.0
    instances: list[dict[str, Any]] = []
    semantic_counts: dict[str, int] = {}
    for index, module in enumerate(sequence):
        local_x = cursor + module.width_m / 2.0
        cursor += module.width_m
        local_y = 0.0
        x = local_x * math.cos(theta) - local_y * math.sin(theta)
        y = local_x * math.sin(theta) + local_y * math.cos(theta)
        semantic_role = str(module.semantic_role)
        semantic_counts[semantic_role] = semantic_counts.get(semantic_role, 0) + 1
        instances.append(
            {
                "asset_id": module.id,
                "asset_name": module.name,
                "model_url": module.model_url,
                "family": module.family,
                "role": module.role,
                "semantic_role": semantic_role,
                "variant_key": module.variant_key,
                "lod": module.lod,
                "level": 0,
                "segment_id": f"bay_{index:02d}",
                "position": [round(x, 4), round(y, 4), 0.0],
                "rotation_degrees": rotation,
                "scale": [1.0, 1.0, 1.0],
                "native_dimensions_m": [module.width_m, module.depth_m, module.height_m],
            }
        )

    assembled_height = max(module.height_m for module in sequence)
    score = 150.0 + sum(_module_score(module, request) for module in fixed.values())
    return {
        "version": 4,
        "family": fixed["entrance"].family,
        "archetype_id": request.archetype_id,
        "reuse_keys": list(request.reuse_keys),
        "target": {
            "width_m": request.target_width_m,
            "depth_m": request.target_depth_m,
            "floors": request.target_floors,
            "footprint_profile": "rectangle",
            "wing_depth_m": native_depth,
        },
        "assembled_height_m": round(assembled_height, 4),
        "instances": instances,
        "fit": {
            "scale_x": 1.0,
            "scale_y": 1.0,
            "envelope_scale_x": round(available_width / occupied_width, 5),
            "envelope_scale_y": round(available_depth / native_depth, 5),
            "score": round(score, 5),
            "profile": "rectangle",
            "segment_count": len(instances),
            "assembly_mode": "semantic_bay_grid",
            "footprint_mode": "whole_bays_inside_site_envelope",
            "compatibility_source": "rlasm_semantic_lego_v4",
            "occupied_width_m": round(occupied_width, 4),
            "occupied_depth_m": round(native_depth, 4),
            "site_margin_width_each_m": round(remainder / 2.0, 4),
            "site_margin_depth_each_m": round((available_depth - native_depth) / 2.0, 4),
        },
        "semantic_invariants": {
            "fixed_anchor_counts": {role: semantic_counts.get(role, 0) for role in _SEMANTIC_BAY_FIXED_ROLES},
            "repeatable_middle_count": semantic_counts.get("middle", 0),
            "native_repeatable_middle_count": native_repeats,
            "integer_bays_only": True,
            "continuous_resize_allowed": False,
        },
        "footprint_segments": [
            {
                "id": "semantic_frontage",
                "centre_x_m": 0.0,
                "centre_y_m": 0.0,
                "length_m": round(occupied_width, 4),
                "thickness_m": round(native_depth, 4),
                "rotation_degrees": rotation,
            }
        ],
    }


def plan_vertical_assembly(
    modules: Iterable[ModuleDescriptor],
    request: AssemblyRequest,
    *,
    allow_forced_fit: bool = True,
) -> dict[str, Any]:
    """Build a podium + repeatable floor + optional setback + roof recipe.

    ``allow_forced_fit=True`` lets ordinary modular families label and absorb
    out-of-band targets. Explicit fixed select-and-place landmarks remain hard
    fit contracts and reject targets beyond their audited containment band.
    Planner probes pass ``False`` so genuine incompatibility keeps raising and
    can drive re-homing and catalogue decisions.

    The output is intentionally renderer-neutral. Each instance has a model URL,
    vertical position and scale. A future Three.js composer or GLB baking worker
    can consume the same recipe.
    """
    if request.target_width_m <= 0 or request.target_depth_m <= 0:
        raise AssemblyPlanningError("Target width and depth must be positive")
    if request.target_floors < 1:
        raise AssemblyPlanningError("Target floors must be at least 1")

    descriptors = list(modules)
    # Catalogue planning calls this function hundreds of times while proving
    # supported floor counts.  Re-filtering the complete library once for
    # every family made one ordinary /plan request quadratic in catalogue
    # size (26+ seconds with the 705-row seed).  Preserve descriptor order in
    # one index so family discovery and both fit passes stay linear.
    modules_by_family: dict[str, list[ModuleDescriptor]] = {}
    for descriptor in descriptors:
        modules_by_family.setdefault(descriptor.family, []).append(descriptor)
    # The API supplies descriptors in ``created_at DESC`` order. Preserve
    # that stable order so a newly imported, quality-improved family wins an
    # otherwise exact score tie over its older predecessor. Alphabetically
    # sorting the set made V4 beat an audited V5 forever unless the caller
    # knew the internal family slug and explicitly preferred it.
    families = list(modules_by_family)
    if request.preferred_family:
        families = [f for f in families if f == request.preferred_family]
        if not families:
            raise AssemblyPlanningError(
                f"No module family named '{request.preferred_family}' is available.",
                code="family_not_found",
                requested=_requested_target_metadata(request),
            )
    eligible_families = tuple(families)
    parent_alias_id: str | None = None
    if request.archetype_id:
        exact_families = [
            family
            for family in eligible_families
            if any(_matches_requested_archetype(module, request.archetype_id) for module in modules_by_family[family])
        ]
        families = exact_families
        if not families:
            candidate_parent = _catalog_parent_archetype_id(request.archetype_id)
            if candidate_parent and _semantic_id(candidate_parent) != _semantic_id(request.archetype_id):
                families = [
                    family
                    for family in eligible_families
                    if any(
                        _matches_requested_archetype(module, candidate_parent) for module in modules_by_family[family]
                    )
                    and _is_generic_parent_fallback_family(
                        modules_by_family[family],
                        family,
                        candidate_parent,
                    )
                ]
                if families:
                    parent_alias_id = candidate_parent
        if not families:
            raise AssemblyPlanningError(
                f"No module family explicitly matches archetype '{request.archetype_id}'. "
                "Import that archetype/variant instead of substituting an unrelated family.",
                code="family_not_found",
                requested=_requested_target_metadata(request),
            )
    if not families:
        raise AssemblyPlanningError(
            "No module families are available.",
            code="family_not_found",
            requested=_requested_target_metadata(request),
        )

    best_plan: dict[str, Any] | None = None
    best_score = float("-inf")

    # Two-pass contract: pass 1 honors the production fit bands; the forced
    # pass runs only when nothing fit and always builds the least-distorted
    # configuration. The LEGO builder's promise is that a matched family
    # assembles even outside its preferred ranges — out-of-band results are
    # labeled (compatibility_source="forced_fit"), never rejected.
    passes = [(family, False) for family in families]
    if allow_forced_fit:
        passes += [(family, True) for family in families]
    for family, forced in passes:
        if forced and best_plan is not None:
            break
        family_modules = modules_by_family[family]
        has_semantic_bay_kit = any(
            module.assembly_axis == "x" and module.semantic_role
            for module in family_modules
        )
        if has_semantic_bay_kit:
            semantic_plan = _semantic_bay_grid_plan(family_modules, request)
            if semantic_plan is not None:
                semantic_score = float(semantic_plan["fit"]["score"])
                if semantic_score > best_score:
                    best_score = semantic_score
                    best_plan = semantic_plan
            # A v4 family is a hard semantic contract. Never fall through to
            # its legacy full-width stack or the forced-fit pass when the site
            # cannot accept complete authored pieces.
            continue
        # Fixed landmarks are the most faithful option inside their audited
        # near-native band. Outside it, prefer the semantic LEGO fallback kit
        # so a hand-drawn rectangle does not crush a courtyard, dome, chamfer,
        # mansard, entrance recess, or other identity-bearing form. An
        # An assembled-only family remains eligible for the forced pass only
        # when its manifest does not declare fixed select-and-place behavior.
        has_stack_fallback = (
            any(module.role == "podium" for module in family_modules)
            and any(module.role == "roof" for module in family_modules)
            and (
                request.target_floors <= 1
                or any(module.role == "floor" and module.repeatable_z for module in family_modules)
            )
        )
        executable_archetype_ids = tuple(value for value in (request.archetype_id, parent_alias_id) if value)
        assembled = _best(
            (
                module
                for module in family_modules
                if module.role == "assembled"
                and module.native_floors == request.target_floors
                and request.footprint_profile == "rectangle"
                and request.archetype_id
                and any(
                    _semantic_id(candidate) == _semantic_id(executable_id)
                    for candidate in (
                        module.source_variant_id,
                        module.generation_archetype_id,
                    )
                    if candidate
                    for executable_id in executable_archetype_ids
                )
            ),
            request,
        )
        if assembled:
            (
                landmark_scale_min,
                landmark_scale_max,
                landmark_max_axis_ratio,
            ) = _fixed_landmark_scale_contract(assembled)
            (
                scale_x,
                scale_y,
                rectangle_rotation,
                segment_length,
                segment_thickness,
            ) = _rectangle_orientation(
                assembled,
                request,
                scale_min=landmark_scale_min,
                scale_max=landmark_scale_max,
            )
            axis_ratio = max(
                scale_x / max(scale_y, 1e-9),
                scale_y / max(scale_x, 1e-9),
            )
            authored_axis_scale_x = request.target_width_m / max(assembled.width_m, 1e-9)
            authored_axis_scale_y = request.target_depth_m / max(assembled.depth_m, 1e-9)
            raw_contain_scale = min(scale_x, scale_y)
            # A parcel larger than the landmark does not require the building
            # to swell until it touches an edge. Cap the applied scale at the
            # family's audited maximum and leave the remaining land as a real
            # setback inside the site envelope.
            contain_scale = min(raw_contain_scale, landmark_scale_max)
            near_native_fit = (
                landmark_scale_min <= scale_x <= landmark_scale_max
                and landmark_scale_min <= scale_y <= landmark_scale_max
                and axis_ratio <= landmark_max_axis_ratio
            )
            uniform_contain_fit = (
                FIXED_LANDMARK_CONTAIN_SCALE_MIN <= raw_contain_scale
                and max(scale_x, scale_y) <= FIXED_LANDMARK_CONTAIN_MAX_ENVELOPE_SCALE
                # Do not let a 90-degree trial disguise a genuinely oversized
                # authored axis. Large sites still belong on the LEGO
                # repeat/stack path; containment is for ordinary drawing
                # tolerance around the landmark's declared orientation.
                and max(authored_axis_scale_x, authored_axis_scale_y) <= FIXED_LANDMARK_CONTAIN_MAX_ENVELOPE_SCALE
                and axis_ratio <= FIXED_LANDMARK_CONTAIN_MAX_AXIS_RATIO
            )
            forced_landmark_fit = (
                forced and not has_stack_fallback and not _fixed_landmark_is_select_and_place(assembled)
            )
            if near_native_fit or uniform_contain_fit or forced_landmark_fit:
                # The polygon is a site envelope, not an extrusion mould.
                # Preserve the reviewed landmark proportions and centre the
                # complete authored form inside the available rectangle.
                family_score = 100.0 + _module_score(assembled, request)
                if forced:
                    family_score -= 2.0 * (abs(math.log(max(scale_x, 1e-9))) + abs(math.log(max(scale_y, 1e-9))))
                plan = {
                    "version": 3,
                    "family": family,
                    "archetype_id": request.archetype_id,
                    "reuse_keys": list(request.reuse_keys),
                    "target": {
                        "width_m": request.target_width_m,
                        "depth_m": request.target_depth_m,
                        "floors": request.target_floors,
                        "footprint_profile": request.footprint_profile,
                        "wing_depth_m": request.target_depth_m,
                    },
                    "assembled_height_m": round(assembled.height_m, 4),
                    "instances": [
                        {
                            "asset_id": assembled.id,
                            "asset_name": assembled.name,
                            "model_url": assembled.model_url,
                            "family": assembled.family,
                            "role": "assembled",
                            "variant_key": assembled.variant_key,
                            "lod": assembled.lod,
                            "level": 0,
                            "segment_id": "landmark",
                            "position": [0.0, 0.0, 0.0],
                            "rotation_degrees": rectangle_rotation,
                            "scale": [
                                round(contain_scale, 5),
                                round(contain_scale, 5),
                                1.0,
                            ],
                            "native_dimensions_m": [
                                assembled.width_m,
                                assembled.depth_m,
                                assembled.height_m,
                            ],
                        }
                    ],
                    "fit": {
                        "scale_x": round(contain_scale, 5),
                        "scale_y": round(contain_scale, 5),
                        "envelope_scale_x": round(scale_x, 5),
                        "envelope_scale_y": round(scale_y, 5),
                        "axis_ratio": round(axis_ratio, 5),
                        "score": round(family_score, 5),
                        "profile": "rectangle",
                        "segment_count": 1,
                        "assembly_mode": "fixed_landmark",
                        "footprint_mode": "archetype_contain",
                        "compatibility_source": (
                            "forced_fit"
                            if forced and not (near_native_fit or uniform_contain_fit)
                            else (
                                "fixed_landmark_native"
                                if math.isclose(scale_x, 1.0, abs_tol=1e-6) and math.isclose(scale_y, 1.0, abs_tol=1e-6)
                                else "fixed_landmark_tolerance" if near_native_fit else "fixed_landmark_contain"
                            )
                        ),
                        "scale_band": {
                            "min": landmark_scale_min,
                            "max": landmark_scale_max,
                            "max_axis_ratio": landmark_max_axis_ratio,
                        },
                        "containment_band": {
                            "min": FIXED_LANDMARK_CONTAIN_SCALE_MIN,
                            "max": landmark_scale_max,
                            "max_envelope_axis_ratio": (FIXED_LANDMARK_CONTAIN_MAX_AXIS_RATIO),
                            "max_envelope_scale": (FIXED_LANDMARK_CONTAIN_MAX_ENVELOPE_SCALE),
                        },
                    },
                    "footprint_segments": [
                        {
                            "id": "landmark",
                            "centre_x_m": 0.0,
                            "centre_y_m": 0.0,
                            "length_m": segment_length,
                            "thickness_m": segment_thickness,
                            "rotation_degrees": rectangle_rotation,
                        }
                    ],
                }
                if family_score > best_score:
                    best_score = family_score
                    best_plan = plan
                continue
        podium = _best((m for m in family_modules if m.role == "podium"), request, forced=forced)
        floor_candidates = [
            m
            for m in family_modules
            if m.role == "floor" and m.repeatable_z and (forced or _valid_for_floor_count(m, request.target_floors))
        ]
        # Pick one render LOD for each design variant. Cycling LOD0/LOD1 as if
        # they were different facades would create visual and performance pops.
        floor_variants = [
            max(
                (module for module in floor_candidates if module.variant_key == variant_key),
                key=lambda module: (_module_score(module, request), -module.lod),
            )
            for variant_key in sorted({module.variant_key for module in floor_candidates})
        ]
        roof = _best((m for m in family_modules if m.role == "roof"), request, forced=forced)
        setback = _best((m for m in family_modules if m.role == "setback"), request, forced=forced)
        crown = _best((m for m in family_modules if m.role == "crown"), request, forced=forced)

        if not podium or not roof:
            continue
        use_setback = bool(
            setback and request.target_floors >= (setback.setback_min_floors or 5) and request.allow_setback
        )
        use_crown = bool(crown and request.target_floors >= 3)
        standard_count = request.target_floors - 1 - (1 if use_setback else 0) - (1 if use_crown else 0)
        if standard_count < 0:
            continue
        if standard_count and not floor_variants:
            continue

        # Rectangles can represent either authored axis order after browser
        # measurement. Quarter-turn the complete stack when that is the exact
        # fit; multi-wing profiles already encode each return's rotation.
        declared_profile_fit = _declared_profile_covers_target(podium, request)
        scale_min, scale_max = (
            (0.62, 1.40) if declared_profile_fit or request.footprint_profile != "rectangle" else (0.80, 1.20)
        )
        streetwall_repeat = False
        if request.footprint_profile == "rectangle":
            (
                _,
                _,
                rectangle_rotation,
                segment_length,
                segment_thickness,
            ) = _rectangle_orientation(
                podium,
                request,
                scale_min=scale_min,
                scale_max=scale_max,
            )
            segments = [
                {
                    "id": "main",
                    "centre_x_m": 0.0,
                    "centre_y_m": 0.0,
                    "length_m": segment_length,
                    "thickness_m": segment_thickness,
                    "rotation_degrees": rectangle_rotation,
                }
            ]
            single_fits = (
                scale_min <= segment_length / podium.width_m <= scale_max
                and scale_min <= segment_thickness / podium.depth_m <= scale_max
            )
            if not single_fits:
                # A parcel no single stretched bar can cover (wide frontage or
                # deep double-loaded block) is planned as repeated abutting
                # bars instead of being rejected outright. In forced mode the
                # helper always answers, possibly with one stretched bar.
                repeated = _rectangle_repeat_segments(podium, request, forced=forced)
                if repeated is None:
                    continue
                segments = repeated
                streetwall_repeat = len(segments) > 1
        else:
            segments = footprint_segments(
                request.footprint_profile,
                request.target_width_m,
                request.target_depth_m,
                podium.depth_m,
                request.wing_depth_m,
            )
        segment_scales = [
            (
                float(segment["length_m"]) / podium.width_m,
                float(segment["thickness_m"]) / podium.depth_m,
            )
            for segment in segments
        ]
        # Rectangles use the strict production fit. Multi-wing profiles and
        # streetwall-repeat bars need a little more latitude because each bar
        # keeps authored facade proportions, but still reject anything that
        # would visibly crush the facade atlas.
        bar_scale_min, bar_scale_max = _STREETWALL_BAND if streetwall_repeat else (scale_min, scale_max)
        if not forced and any(
            not (bar_scale_min <= sx <= bar_scale_max and bar_scale_min <= sy <= bar_scale_max)
            for sx, sy in segment_scales
        ):
            continue

        levels: list[tuple[ModuleDescriptor, str, int, float]] = []
        z = 0.0

        def add_level(module: ModuleDescriptor, role: str, level: int) -> None:
            nonlocal z
            levels.append((module, role, level, z))
            z += module.height_m

        add_level(podium, "podium", 0)
        for level in range(1, standard_count + 1):
            add_level(floor_variants[(level - 1) % len(floor_variants)], "floor", level)
        if use_setback and setback:
            add_level(setback, "setback", request.target_floors - (2 if use_crown else 1))
        if use_crown and crown:
            add_level(crown, "crown", request.target_floors - 1)
        add_level(roof, "roof", request.target_floors)

        instances: list[dict[str, Any]] = []
        # Keep every selected module inside the segment while applying one
        # common horizontal scale to the complete stack. Scaling each level by
        # its own native width/depth made every level fill the rectangle and
        # erased authored setbacks, narrower crowns, roof shoulders and voids.
        # The largest declared level envelope is the containment anchor; all
        # smaller modules retain their designed relative footprint.
        stack_envelope_width = max(module.width_m for module, _, _, _ in levels)
        stack_envelope_depth = max(module.depth_m for module, _, _, _ in levels)
        segment_contain_scales = [
            min(
                float(segment["length_m"]) / stack_envelope_width,
                float(segment["thickness_m"]) / stack_envelope_depth,
            )
            for segment in segments
        ]
        for segment, contain_scale in zip(segments, segment_contain_scales, strict=True):
            for module, role, level, level_z in levels:
                instances.append(
                    {
                        "asset_id": module.id,
                        "asset_name": module.name,
                        "model_url": module.model_url,
                        "family": module.family,
                        "role": role,
                        "variant_key": module.variant_key,
                        "lod": module.lod,
                        "level": level,
                        "segment_id": segment["id"],
                        "position": [
                            round(float(segment["centre_x_m"]), 4),
                            round(float(segment["centre_y_m"]), 4),
                            round(level_z, 4),
                        ],
                        "rotation_degrees": float(segment["rotation_degrees"]),
                        "scale": [
                            round(contain_scale, 5),
                            round(contain_scale, 5),
                            1.0,
                        ],
                        "native_dimensions_m": [module.width_m, module.depth_m, module.height_m],
                    }
                )

        family_score = _module_score(podium, request) + _module_score(roof, request)
        if floor_variants:
            family_score += sum(_module_score(module, request) for module in floor_variants) / len(floor_variants)
        if use_setback and setback:
            family_score += _module_score(setback, request)
        if use_crown and crown:
            family_score += _module_score(crown, request)
        if streetwall_repeat:
            # Prefer a family that covers the parcel in one bar over one that
            # needs repetition, all else equal.
            family_score -= 0.25 * (len(segments) - 1)
        if forced:
            # Within the forced pass the least-distorted family must win.
            family_score -= (
                2.0
                * sum(abs(math.log(max(sx, 1e-9))) + abs(math.log(max(sy, 1e-9))) for sx, sy in segment_scales)
                / len(segment_scales)
            )
        plan = {
            "version": 2,
            "family": family,
            "archetype_id": request.archetype_id,
            "reuse_keys": list(request.reuse_keys),
            "target": {
                "width_m": request.target_width_m,
                "depth_m": request.target_depth_m,
                "floors": request.target_floors,
                "footprint_profile": request.footprint_profile,
                "wing_depth_m": round(float(segments[0]["thickness_m"]), 4),
            },
            "assembled_height_m": round(z, 4),
            "instances": instances,
            "fit": {
                "scale_x": round(max(segment_contain_scales), 5),
                "scale_y": round(max(segment_contain_scales), 5),
                "envelope_scale_x": round(max(scale[0] for scale in segment_scales), 5),
                "envelope_scale_y": round(max(scale[1] for scale in segment_scales), 5),
                "score": round(family_score, 5),
                "profile": request.footprint_profile,
                "segment_count": len(segments),
                "footprint_mode": "archetype_contain",
                "compatibility_source": (
                    "forced_fit"
                    if forced
                    else (
                        "streetwall_repeat"
                        if streetwall_repeat
                        else "manifest_shape_matrix" if declared_profile_fit else "native_scale"
                    )
                ),
            },
            "footprint_segments": segments,
        }
        if family_score > best_score:
            best_score = family_score
            best_plan = plan

    if best_plan is None:
        raise AssemblyPlanningError(
            "No compatible module family found. Add podium, repeatable floor, and roof modules "
            "whose native footprint is within 20% of the target.",
            code="family_incompatible",
            requested=_requested_target_metadata(request),
            supported_families=_supported_family_metadata(descriptors, families),
        )
    return best_plan


# ---------------------------------------------------------------------------
# Compiler-manifest helpers (import pipeline)
#
# tools/archetype_compiler/blender_generate.py writes a *_manifest.json next
# to the module GLBs. These pure helpers validate that manifest and translate
# it into the ``metadata_["lego"]`` shape documented at the top of this file,
# so the API layer only has to do I/O (storage upload + DB rows).
# ---------------------------------------------------------------------------


def manifest_validation_errors(manifest: Any) -> list[str]:
    """Return a list of human-actionable problems with a compiler manifest.

    An empty list means the manifest is importable. Kept intentionally
    shallow — the Blender generator is the source of truth; this only guards
    against importing the wrong file or a stale schema.
    """
    if not isinstance(manifest, dict):
        return ["manifest must be a JSON object (got a non-object payload)"]

    errors: list[str] = []
    if manifest.get("manifest_schema") not in SUPPORTED_MANIFEST_SCHEMAS:
        errors.append(
            f"manifest_schema must be one of {sorted(SUPPORTED_MANIFEST_SCHEMAS)} "
            f"(got {manifest.get('manifest_schema')!r}); regenerate with the current blender_generate.py"
        )
    family = str(manifest.get("family") or "").strip()
    if not family:
        errors.append("family is required")
    elif not _FAMILY_SLUG_RE.match(family):
        # family and role become storage-key path segments; reject anything
        # that isn't the kebab-case slug the compiler emits (no '/', '..', etc.)
        errors.append(
            f"family {family!r} must be a kebab-case slug (letters/digits/hyphens); "
            "it is used as a storage path segment"
        )
    if not str(manifest.get("archetype_id") or "").strip():
        errors.append("archetype_id is required")

    reuse_keys = manifest.get("reuse_keys")
    if not isinstance(reuse_keys, list) or not [k for k in reuse_keys if str(k or "").strip()]:
        errors.append("reuse_keys must be a non-empty list of strings")

    modules = manifest.get("modules")
    if not isinstance(modules, list) or not modules:
        errors.append("modules must be a non-empty list")
    else:
        identities: set[tuple[str, str, int]] = set()
        semantic_counts: dict[str, int] = {}
        for index, module in enumerate(modules):
            if not isinstance(module, dict) or not module.get("role") or not module.get("filename"):
                errors.append(f"modules[{index}] must be an object with 'role' and 'filename'")
                continue
            role = str(module["role"]).strip().lower()
            variant_key = str(module.get("variant_key") or "default").strip().lower()
            lod = _as_int_or_none(module.get("lod")) or 0
            if role not in VALID_ROLES or not _ROLE_SLUG_RE.match(role):
                errors.append(
                    f"modules[{index}].role {module['role']!r} must be a short lowercase word; "
                    "it is used as a storage path segment"
                )
            if not _VARIANT_SLUG_RE.match(variant_key):
                errors.append(f"modules[{index}].variant_key {variant_key!r} must be a snake_case slug")
            if lod < 0:
                errors.append(f"modules[{index}].lod must be zero or greater")
            identity = (role, variant_key, lod)
            if identity in identities:
                errors.append(f"modules[{index}] duplicates module identity {identity}")
            identities.add(identity)
            semantic_role = str(module.get("semantic_role") or "").strip()
            if semantic_role:
                semantic_counts[semantic_role] = semantic_counts.get(semantic_role, 0) + 1
                if module.get("assembly_axis") != "x":
                    errors.append(f"modules[{index}] semantic module must declare assembly_axis='x'")
                if role != "attachment":
                    errors.append(f"modules[{index}] semantic module role must be 'attachment'")
                if semantic_role == "middle":
                    if module.get("repeatable_x") is not True:
                        errors.append(f"modules[{index}] middle module must declare repeatable_x=true")
                elif semantic_role in _SEMANTIC_BAY_FIXED_ROLES:
                    if module.get("required_once") is not True:
                        errors.append(f"modules[{index}] fixed semantic anchor must declare required_once=true")
                else:
                    errors.append(f"modules[{index}].semantic_role {semantic_role!r} is not supported")
        if semantic_counts:
            for semantic_role in _SEMANTIC_BAY_FIXED_ROLES:
                if semantic_counts.get(semantic_role) != 1:
                    errors.append(
                        f"semantic bay grid requires exactly one {semantic_role!r} module identity"
                    )
            if semantic_counts.get("middle", 0) < 1:
                errors.append("semantic bay grid requires at least one repeatable 'middle' module")
    return errors


def lego_metadata_from_manifest(
    manifest: dict[str, Any],
    module: dict[str, Any],
    *,
    role: str | None = None,
    validation_status: str = "unknown",
) -> dict[str, Any]:
    """Build the ``metadata_["lego"]`` payload for one manifest module.

    ``module`` is either an entry of ``manifest["modules"]`` or a synthesized
    dict for the pre-assembled GLB. Landmark massing graphs enable that asset
    for exact-variant/canonical-size planning; ordinary previews stay disabled.
    """
    resolved_role = str(role or module.get("role") or "").strip().lower()
    archetype_ids = [str(manifest.get("archetype_id"))]
    variant_id = manifest.get("variant_id")
    if variant_id:
        archetype_ids.append(str(variant_id))
    generation_archetype_id = manifest.get("generation_archetype_id")
    if generation_archetype_id:
        archetype_ids.append(str(generation_archetype_id))
    for alias in manifest.get("archetype_aliases") or []:
        normalized_alias = str(alias or "").strip()
        if normalized_alias and normalized_alias not in archetype_ids:
            archetype_ids.append(normalized_alias)

    dimensions = manifest.get("dimensions") or {}
    generator = manifest.get("generator") or {}
    return {
        "enabled": resolved_role in STACKABLE_ROLES
        or (
            resolved_role == "attachment"
            and module.get("assembly_axis") == "x"
            and bool(module.get("semantic_role"))
        )
        or (resolved_role == "assembled" and bool(manifest.get("massing_graph"))),
        "role": resolved_role,
        "family": str(manifest.get("family") or ""),
        "width_m": module.get("width_m"),
        "depth_m": module.get("depth_m"),
        "height_m": module.get("height_m"),
        "floor_height_m": module.get("floor_height_m"),
        "repeatable_z": bool(module.get("repeatable_z", False)),
        "variant_key": str(module.get("variant_key") or "default"),
        "lod": max(0, int(module.get("lod") or 0)),
        "allowed_levels": [int(value) for value in (module.get("allowed_levels") or [])],
        "native_floors": _as_int_or_none(module.get("native_floors")),
        "archetype_ids": archetype_ids,
        "reuse_keys": [str(k) for k in (manifest.get("reuse_keys") or []) if str(k or "").strip()],
        "min_floors": manifest.get("min_floors", dimensions.get("min_floors")),
        "max_floors": manifest.get("max_floors", dimensions.get("max_floors")),
        "setback_min_floors": module.get("setback_min_floors"),
        "schema_version": manifest.get("grammar_schema_version") or 1,
        "generator_version": generator.get("version"),
        "validation_status": validation_status,
        "triangle_count": module.get("triangle_count"),
        "material_count": module.get("material_count"),
        "coordinate_contract": manifest.get("coordinate_contract") or {},
        "footprint_compatibility": manifest.get("footprint_compatibility") or {},
        "placement_contract": manifest.get("placement_contract") or {},
        "allow_inset_footprint": bool(module.get("allow_inset_footprint", False)),
        "assembly_axis": module.get("assembly_axis"),
        "semantic_role": module.get("semantic_role"),
        "repeatable_x": bool(module.get("repeatable_x", False)),
        "required_once": bool(module.get("required_once", False)),
        "min_repeats": _as_int_or_none(module.get("min_repeats")),
        "max_repeats": _as_int_or_none(module.get("max_repeats")),
        "native_repeat_count": _as_int_or_none(module.get("native_repeat_count")),
        "source_variant_id": variant_id,
        "generation_archetype_id": generation_archetype_id,
        "asset_kind": "lego_module",
    }


def find_family_module_entry(
    entries: Iterable[Any],
    family: str,
    role: str,
    variant_key: str = "default",
    lod: int = 0,
) -> Any | None:
    """Dedupe on the complete module identity, preserving floor variants.

    ``model_library`` has no unique constraints, so re-importing a family must
    update rows in place instead of stacking duplicates.
    """
    for entry in entries:
        metadata = getattr(entry, "metadata_", None) or {}
        lego = metadata.get("lego") if isinstance(metadata, dict) else None
        if not isinstance(lego, dict):
            continue
        if (
            str(lego.get("family") or "") == family
            and str(lego.get("role") or "") == role
            and str(lego.get("variant_key") or "default") == variant_key
            and (_as_int_or_none(lego.get("lod")) or 0) == lod
        ):
            return entry
    return None
