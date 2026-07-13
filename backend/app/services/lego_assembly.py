"""Archetype-driven modular building assembly planning.

This experiment deliberately reuses ``ModelLibraryEntry.metadata_`` instead of
introducing a new database table. Library items become modules when their
metadata contains ``lego`` configuration. The planner groups compatible
modules into families and produces a vertical podium/floor/roof recipe.

Expected metadata shape::

    {
      "lego": {
        "enabled": true,
        "role": "podium|floor|setback|roof|attachment",
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

from dataclasses import dataclass
from typing import Any, Iterable


VALID_ROLES = {"podium", "floor", "setback", "roof", "attachment"}


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
    repeatable_z: bool = False


@dataclass(frozen=True)
class AssemblyRequest:
    target_width_m: float
    target_depth_m: float
    target_floors: int
    archetype_id: str | None = None
    reuse_keys: tuple[str, ...] = ()
    preferred_family: str | None = None


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
        repeatable_z=bool(lego.get("repeatable_z", role == "floor")),
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
    families = sorted({m.family for m in descriptors})
    if request.preferred_family:
        families = [f for f in families if f == request.preferred_family]

    best_plan: dict[str, Any] | None = None
    best_score = float("-inf")

    for family in families:
        family_modules = [m for m in descriptors if m.family == family]
        podium = _best((m for m in family_modules if m.role == "podium"), request)
        standard_floor = _best(
            (m for m in family_modules if m.role == "floor" and m.repeatable_z),
            request,
        )
        roof = _best((m for m in family_modules if m.role == "roof"), request)
        setback = _best((m for m in family_modules if m.role == "setback"), request)

        if not podium or not roof:
            continue
        if request.target_floors > 1 and not standard_floor:
            continue

        use_setback = bool(setback and request.target_floors >= 5)
        standard_count = request.target_floors - 1 - (1 if use_setback else 0)
        if standard_count < 0:
            continue

        selected = [podium, roof]
        if standard_floor:
            selected.append(standard_floor)
        if use_setback and setback:
            selected.append(setback)

        # Reject families that require visually destructive non-uniform scaling.
        scale_x = request.target_width_m / podium.width_m
        scale_y = request.target_depth_m / podium.depth_m
        if not (0.80 <= scale_x <= 1.20 and 0.80 <= scale_y <= 1.20):
            continue

        z = 0.0
        instances: list[dict[str, Any]] = []

        def add_instance(module: ModuleDescriptor, role: str, level: int) -> None:
            nonlocal z
            instances.append(
                {
                    "asset_id": module.id,
                    "asset_name": module.name,
                    "model_url": module.model_url,
                    "family": module.family,
                    "role": role,
                    "level": level,
                    "position": [0.0, 0.0, round(z, 4)],
                    "rotation_degrees": 0.0,
                    "scale": [round(scale_x, 5), round(scale_y, 5), 1.0],
                    "native_dimensions_m": [module.width_m, module.depth_m, module.height_m],
                }
            )
            z += module.height_m

        add_instance(podium, "podium", 0)
        for level in range(1, standard_count + 1):
            assert standard_floor is not None
            add_instance(standard_floor, "floor", level)
        if use_setback and setback:
            add_instance(setback, "setback", request.target_floors - 1)
        add_instance(roof, "roof", request.target_floors)

        family_score = sum(_module_score(module, request) for module in selected)
        plan = {
            "version": 1,
            "family": family,
            "archetype_id": request.archetype_id,
            "reuse_keys": list(request.reuse_keys),
            "target": {
                "width_m": request.target_width_m,
                "depth_m": request.target_depth_m,
                "floors": request.target_floors,
            },
            "assembled_height_m": round(z, 4),
            "instances": instances,
            "fit": {
                "scale_x": round(scale_x, 5),
                "scale_y": round(scale_y, 5),
                "score": round(family_score, 5),
            },
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
