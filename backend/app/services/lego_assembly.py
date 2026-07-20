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

import re
from dataclasses import dataclass
from typing import Any, Iterable


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
# roof and are therefore safer to resize as one authored assembly than to fall
# back to an unrelated generic stack. City Prompt parcels vary widely; allow a
# useful but bounded range while keeping ordinary repeated modules at ±20%.
FIXED_LANDMARK_SCALE_MIN = 0.45
FIXED_LANDMARK_SCALE_MAX = 1.75

# Manifest schema emitted by tools/archetype_compiler/blender_generate.py.
SUPPORTED_MANIFEST_SCHEMA = 3
SUPPORTED_MANIFEST_SCHEMAS = {2, SUPPORTED_MANIFEST_SCHEMA}


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


class AssemblyPlanningError(ValueError):
    """Raised when no valid modular assembly can be produced."""


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
            int(value) for value in (lego.get("allowed_levels") or [])
            if isinstance(value, (int, float)) and int(value) >= 0
        ),
        native_floors=_as_int_or_none(lego.get("native_floors")),
        source_variant_id=(
            str(lego.get("source_variant_id")) if lego.get("source_variant_id") else None
        ),
        generation_archetype_id=(
            str(lego.get("generation_archetype_id"))
            if lego.get("generation_archetype_id") else None
        ),
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


def _matches_requested_archetype(module: ModuleDescriptor, archetype_id: str) -> bool:
    requested = _semantic_id(archetype_id)
    return any(_semantic_id(candidate) == requested for candidate in module.archetype_ids)


def _module_score(module: ModuleDescriptor, request: AssemblyRequest) -> float:
    return _dimension_score(module, request) * 2.0 + _semantic_score(module, request)


def _valid_for_floor_count(module: ModuleDescriptor, floors: int) -> bool:
    if module.min_floors is not None and floors < module.min_floors:
        return False
    if module.max_floors is not None and floors > module.max_floors:
        return False
    return True


def _best(modules: Iterable[ModuleDescriptor], request: AssemblyRequest) -> ModuleDescriptor | None:
    candidates = [m for m in modules if _valid_for_floor_count(m, request.target_floors)]
    if not candidates:
        return None
    return max(candidates, key=lambda module: _module_score(module, request))


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
        return [{
            "id": "main", "centre_x_m": 0.0, "centre_y_m": 0.0,
            "length_m": width, "thickness_m": depth, "rotation_degrees": 0.0,
        }]
    requested = float(wing_depth_m) if wing_depth_m else float(native_depth_m)
    wing = min(max(5.5, requested), max(5.5, min(width, depth) * 0.46))
    segments: list[dict[str, float | str]] = [{
        "id": "front", "centre_x_m": 0.0, "centre_y_m": -(depth - wing) / 2,
        "length_m": width, "thickness_m": wing, "rotation_degrees": 0.0,
    }]
    if profile == "l_shape":
        segments.append({
            "id": "left_return", "centre_x_m": -(width - wing) / 2, "centre_y_m": 0.0,
            "length_m": depth, "thickness_m": wing, "rotation_degrees": 90.0,
        })
    elif profile == "u_shape":
        segments.extend([
            {
                "id": "left_return", "centre_x_m": -(width - wing) / 2, "centre_y_m": 0.0,
                "length_m": depth, "thickness_m": wing, "rotation_degrees": 90.0,
            },
            {
                "id": "right_return", "centre_x_m": (width - wing) / 2, "centre_y_m": 0.0,
                "length_m": depth, "thickness_m": wing, "rotation_degrees": 90.0,
            },
        ])
    else:
        segments.extend([
            {
                "id": "rear", "centre_x_m": 0.0, "centre_y_m": (depth - wing) / 2,
                "length_m": width, "thickness_m": wing, "rotation_degrees": 0.0,
            },
            {
                "id": "left_return", "centre_x_m": -(width - wing) / 2, "centre_y_m": 0.0,
                "length_m": depth, "thickness_m": wing, "rotation_degrees": 90.0,
            },
            {
                "id": "right_return", "centre_x_m": (width - wing) / 2, "centre_y_m": 0.0,
                "length_m": depth, "thickness_m": wing, "rotation_degrees": 90.0,
            },
        ])
    return segments


def plan_vertical_assembly(
    modules: Iterable[ModuleDescriptor],
    request: AssemblyRequest,
) -> dict[str, Any]:
    """Build a podium + repeatable floor + optional setback + roof recipe.

    The output is intentionally renderer-neutral. Each instance has a model URL,
    vertical position and scale. A future Three.js composer or GLB baking worker
    can consume the same recipe.
    """
    if request.target_width_m <= 0 or request.target_depth_m <= 0:
        raise AssemblyPlanningError("Target width and depth must be positive")
    if request.target_floors < 1:
        raise AssemblyPlanningError("Target floors must be at least 1")

    descriptors = list(modules)
    # The API supplies descriptors in ``created_at DESC`` order. Preserve
    # that stable order so a newly imported, quality-improved family wins an
    # otherwise exact score tie over its older predecessor. Alphabetically
    # sorting the set made V4 beat an audited V5 forever unless the caller
    # knew the internal family slug and explicitly preferred it.
    families = list(dict.fromkeys(module.family for module in descriptors))
    if request.preferred_family:
        families = [f for f in families if f == request.preferred_family]
    if request.archetype_id:
        families = [
            family
            for family in families
            if any(
                _matches_requested_archetype(module, request.archetype_id)
                for module in descriptors
                if module.family == family
            )
        ]
        if not families:
            raise AssemblyPlanningError(
                f"No module family explicitly matches archetype '{request.archetype_id}'. "
                "Import that archetype/variant instead of substituting an unrelated family."
            )

    best_plan: dict[str, Any] | None = None
    best_score = float("-inf")

    for family in families:
        family_modules = [m for m in descriptors if m.family == family]
        assembled = _best(
            (
                module for module in family_modules
                if module.role == "assembled"
                and module.native_floors == request.target_floors
                and request.footprint_profile == "rectangle"
                and request.archetype_id
                and any(
                    _semantic_id(candidate) == _semantic_id(request.archetype_id)
                    for candidate in (
                        module.source_variant_id,
                        module.generation_archetype_id,
                    )
                    if candidate
                )
            ),
            request,
        )
        if assembled:
            scale_x = request.target_width_m / assembled.width_m
            scale_y = request.target_depth_m / assembled.depth_m
            if (
                FIXED_LANDMARK_SCALE_MIN <= scale_x <= FIXED_LANDMARK_SCALE_MAX
                and FIXED_LANDMARK_SCALE_MIN <= scale_y <= FIXED_LANDMARK_SCALE_MAX
            ):
                family_score = 100.0 + _module_score(assembled, request)
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
                    "instances": [{
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
                        "rotation_degrees": 0.0,
                        "scale": [round(scale_x, 5), round(scale_y, 5), 1.0],
                        "native_dimensions_m": [
                            assembled.width_m, assembled.depth_m, assembled.height_m,
                        ],
                    }],
                    "fit": {
                        "scale_x": round(scale_x, 5),
                        "scale_y": round(scale_y, 5),
                        "score": round(family_score, 5),
                        "profile": "rectangle",
                        "segment_count": 1,
                        "assembly_mode": "fixed_landmark",
                    },
                    "footprint_segments": [{
                        "id": "landmark", "centre_x_m": 0.0, "centre_y_m": 0.0,
                        "length_m": request.target_width_m,
                        "thickness_m": request.target_depth_m,
                        "rotation_degrees": 0.0,
                    }],
                }
                if family_score > best_score:
                    best_score = family_score
                    best_plan = plan
                continue
        podium = _best((m for m in family_modules if m.role == "podium"), request)
        floor_candidates = [
            m for m in family_modules
            if m.role == "floor" and m.repeatable_z and _valid_for_floor_count(m, request.target_floors)
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
        roof = _best((m for m in family_modules if m.role == "roof"), request)
        setback = _best((m for m in family_modules if m.role == "setback"), request)
        crown = _best((m for m in family_modules if m.role == "crown"), request)

        if not podium or not roof:
            continue
        use_setback = bool(
            setback
            and request.target_floors >= (setback.setback_min_floors or 5)
            and request.allow_setback
        )
        use_crown = bool(crown and request.target_floors >= 3)
        standard_count = request.target_floors - 1 - (1 if use_setback else 0) - (1 if use_crown else 0)
        if standard_count < 0:
            continue
        if standard_count and not floor_variants:
            continue

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
        # Rectangles use the strict production fit. Multi-wing profiles need a
        # little more latitude because the imported family is a streetwall bar,
        # but still reject anything that would visibly crush the facade atlas.
        scale_min, scale_max = (0.80, 1.20) if request.footprint_profile == "rectangle" else (0.62, 1.40)
        if any(not (scale_min <= sx <= scale_max and scale_min <= sy <= scale_max)
               for sx, sy in segment_scales):
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
        for segment in segments:
            for module, role, level, level_z in levels:
                scale_x = float(segment["length_m"]) / module.width_m
                scale_y = float(segment["thickness_m"]) / module.depth_m
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
                        "scale": [round(scale_x, 5), round(scale_y, 5), 1.0],
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
                "scale_x": round(max(scale[0] for scale in segment_scales), 5),
                "scale_y": round(max(scale[1] for scale in segment_scales), 5),
                "score": round(family_score, 5),
                "profile": request.footprint_profile,
                "segment_count": len(segments),
            },
            "footprint_segments": segments,
        }
        if family_score > best_score:
            best_score = family_score
            best_plan = plan

    if best_plan is None:
        raise AssemblyPlanningError(
            "No compatible module family found. Add podium, repeatable floor, and roof modules "
            "whose native footprint is within 20% of the target."
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
        "enabled": resolved_role in STACKABLE_ROLES or (
            resolved_role == "assembled" and bool(manifest.get("massing_graph"))
        ),
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
