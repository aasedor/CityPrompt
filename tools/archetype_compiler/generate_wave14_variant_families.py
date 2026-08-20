"""Generate ten reference-locked sibling-variant LEGO families for Wave 14.

Every family exports a fixed whole-building landmark and six semantic fallback
modules.  The fixed landmark carries the exact reference silhouette; the
fallback repeats complete construction bays so a user's approximate footprint
does not stretch windows, screens, lattice, columns, entrances, or ornament.

Run from the repository root with Blender 5.x::

    blender --background --factory-startup --python \
      tools/archetype_compiler/generate_wave14_variant_families.py -- \
      --family art-deco-polychrome-zigzag-tower --view-set pilot
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import bpy
from mathutils import Vector


TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from generate_wave3_landmark_families import (  # noqa: E402
    COORDINATE_CONTRACT,
    aim_camera,
    clear_scene,
    delete_objects,
    export_glb,
    facade_contract,
    load_skin_manifest,
    material,
    module_contract_markers,
    skin_material,
    texture_inventory,
)
from generate_wave12_diverse_families import (  # noqa: E402
    add_beam,
    add_box,
    add_cylinder,
    add_sphere,
    bounds_dimensions,
    bsdf_for,
    configure_glass,
    configure_occupied,
    create_mesh_object,
    evaluated_triangle_count,
    grade_material,
    material_count,
    normalize_bottom_centre,
    set_normal_strength,
    tag_object,
    wash_material,
)
from wave14_variant_specs import FAMILIES, with_family  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", choices=sorted(FAMILIES), required=True)
    parser.add_argument("--output-root", type=Path, default=Path("frontend/public/families"))
    parser.add_argument(
        "--view-set",
        choices=("preview", "pilot", "assessment", "all", "street", "context", "front_elevation", "front_corner_oblique", "rear_corner_oblique", "aerial", "facade_close"),
        default="all",
    )
    parser.add_argument("--skip-renders", action="store_true")
    parser.add_argument("--skip-modules", action="store_true")
    parser.add_argument("--skip-assembled-export", action="store_true")
    parser.add_argument("--render-existing", action="store_true")
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(argv)


def _pbr(
    folder: Path,
    near: dict,
    cfg: dict,
    key: str,
    name: str,
    *,
    metallic: float = 0.0,
    transmission: float = 0.0,
    normal: float = 0.42,
) -> bpy.types.Material:
    result = skin_material(
        name, folder, near[key], key, metallic=metallic, transmission=transmission
    )
    grade_material(result, saturation=0.96, value=0.93)
    set_normal_strength(result, normal)
    result["source_variant_id"] = cfg["variant_id"]
    result["generation_archetype_id"] = cfg["variant_id"]
    result["reference_locked"] = True
    result["wave14_variant_specific_material"] = True
    return result


def load_palette(
    folder: Path,
    cfg: dict,
    *,
    texture_lod: str = "near",
) -> tuple[dict[str, bpy.types.Material], dict]:
    skin = load_skin_manifest(folder)
    if not skin:
        raise FileNotFoundError(folder / "textures" / "skin_manifest.json")
    if texture_lod not in {"near", "far"}:
        raise ValueError(f"unsupported texture LOD: {texture_lod}")
    atlas = {zone: values[texture_lod] for zone, values in skin["zones"].items()}
    mats: dict[str, bpy.types.Material] = {}
    for key, (_description, rgb, kind) in cfg["palette"].items():
        tint = tuple(channel / 255.0 for channel in rgb)
        if key == "glass":
            mats[key] = configure_glass(
                _pbr(folder, atlas, cfg, key, f"MAT_W14_{cfg['family']}_{key}", transmission=0.58, normal=0.06),
                cfg,
                tint=tint,
                transmission=0.76,
                alpha=0.34,
            )
        else:
            metallic = 0.62 if kind == "metal" else 0.0
            roughness = 0.22 if kind == "metal" else 0.64 if kind == "wood" else 0.72
            mats[key] = wash_material(
                _pbr(folder, atlas, cfg, key, f"MAT_W14_{cfg['family']}_{key}", metallic=metallic, normal=0.34 if kind == "metal" else 0.52),
                tint=tint,
                factor=0.31,
                roughness=roughness,
            )
    mats["interior"] = configure_occupied(
        _pbr(folder, atlas, cfg, "interior", f"MAT_W14_{cfg['family']}_OccupiedDepth", normal=0.08),
        warmth=(0.31, 0.17, 0.055),
        emission=0.14,
    )
    mats["plant"] = material(
        f"MAT_W14_{cfg['family']}_LivingPlanting",
        (0.075, 0.205, 0.055, 1.0),
        0.78,
    )
    for key in ("facade", "podium", "floor_a", "floor_b", "crown", "side"):
        mats[key + "_skin"] = _pbr(folder, atlas, cfg, key, f"MAT_W14_{cfg['family']}_{key}_registered", normal=0.12)
    return mats, skin


def add_adaptive_delivery_bevels(
    objects: list[bpy.types.Object],
    cfg: dict,
    *,
    minimum_triangles: int = 12000,
) -> int:
    """Soften construction edges until the hero-detail floor is satisfied.

    The procedural cube primitives are intentionally economical during visual
    iteration.  Final delivery adds a small real bevel to six-face solids so
    masonry, timber, frames, screens and slab edges catch separate highlights.
    Detailed mesh shells and cylinders are left untouched.
    """
    initial = evaluated_triangle_count(objects)
    cfg["_delivery_edge_bevel_segments"] = 0
    if initial >= minimum_triangles:
        return initial
    candidates = [
        obj
        for obj in objects
        if obj.type == "MESH" and len(obj.data.polygons) == 6
    ]
    if not candidates:
        return initial
    modifiers: list[bpy.types.Modifier] = []
    for obj in candidates:
        modifier = obj.modifiers.new("W14_DELIVERY_EDGE_BEVEL", "BEVEL")
        modifier.width = 0.003
        modifier.segments = 2
        modifier.limit_method = "ANGLE"
        obj["delivery_edge_bevel"] = True
        modifiers.append(modifier)
    bpy.context.view_layer.update()
    count = evaluated_triangle_count(objects)
    for segments in range(3, 7):
        if count >= minimum_triangles:
            break
        for modifier in modifiers:
            modifier.segments = segments
        bpy.context.view_layer.update()
        count = evaluated_triangle_count(objects)
    cfg["_delivery_edge_bevel_segments"] = max(
        (modifier.segments for modifier in modifiers),
        default=0,
    )
    return count


def add_window_band_y(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    width: float,
    facade_y: float,
    centre_z: float,
    height: float,
    bays: int,
    outward_sign: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
    margin: float = 0.55,
) -> None:
    clear_width = width - margin * 2
    glass_y = facade_y
    interior_y = facade_y - outward_sign * 0.34
    frame_y = facade_y + outward_sign * 0.075
    add_box(objects, prefix + "_Occupied", (clear_width, 0.08, height - 0.18), (0.0, interior_y, centre_z), mats["interior"], cfg, "continuous_occupied_depth", role=role)
    add_box(objects, prefix + "_Glass", (clear_width, 0.10, height - 0.12), (0.0, glass_y, centre_z), mats["glass"], cfg, "physical_glazing_band", role=role)
    bay = clear_width / bays
    for index in range(bays + 1):
        x = -clear_width / 2 + index * bay
        add_box(objects, f"{prefix}_Mullion_{index}", (0.12, 0.18, height), (x, frame_y, centre_z), mats["frame"], cfg, "physical_vertical_frame", role=role)
    for z in (centre_z - height / 2, centre_z + height / 2):
        add_box(objects, f"{prefix}_Rail_{z:.2f}", (clear_width, 0.18, 0.12), (0.0, frame_y, z), mats["frame"], cfg, "physical_horizontal_frame", role=role)


def add_window_band_x(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    depth: float,
    facade_x: float,
    centre_z: float,
    height: float,
    bays: int,
    outward_sign: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
    margin: float = 0.55,
) -> None:
    clear_width = depth - margin * 2
    glass_x = facade_x
    interior_x = facade_x - outward_sign * 0.34
    frame_x = facade_x + outward_sign * 0.075
    add_box(objects, prefix + "_Occupied", (0.08, clear_width, height - 0.18), (interior_x, 0.0, centre_z), mats["interior"], cfg, "continuous_occupied_depth", role=role)
    add_box(objects, prefix + "_Glass", (0.10, clear_width, height - 0.12), (glass_x, 0.0, centre_z), mats["glass"], cfg, "physical_glazing_band", role=role)
    bay = clear_width / bays
    for index in range(bays + 1):
        y = -clear_width / 2 + index * bay
        add_box(objects, f"{prefix}_Mullion_{index}", (0.18, 0.12, height), (frame_x, y, centre_z), mats["frame"], cfg, "physical_vertical_frame", role=role)
    for z in (centre_z - height / 2, centre_z + height / 2):
        add_box(objects, f"{prefix}_Rail_{z:.2f}", (0.18, clear_width, 0.12), (frame_x, 0.0, z), mats["frame"], cfg, "physical_horizontal_frame", role=role)


def add_arch_ring_y(
    objects: list[bpy.types.Object],
    *,
    name: str,
    centre_x: float,
    facade_y: float,
    spring_z: float,
    inner_radius: float,
    ring_width: float,
    thickness: float,
    mat: bpy.types.Material,
    cfg: dict,
    role: str = "assembled",
    segments: int = 24,
) -> None:
    outer = inner_radius + ring_width
    vertices: list[tuple[float, float, float]] = []
    for y in (facade_y - thickness / 2, facade_y + thickness / 2):
        for radius in (inner_radius, outer):
            for index in range(segments + 1):
                angle = math.pi * index / segments
                vertices.append((centre_x + math.cos(angle) * radius, y, spring_z + math.sin(angle) * radius))
    stride = segments + 1
    faces: list[tuple[int, ...]] = []
    for side in range(2):
        base = side * stride * 2
        for index in range(segments):
            if side == 0:
                faces.append((base + index, base + index + 1, base + stride + index + 1, base + stride + index))
            else:
                faces.append((base + index, base + stride + index, base + stride + index + 1, base + index + 1))
    for radius_index in range(2):
        front = radius_index * stride
        back = stride * 2 + radius_index * stride
        for index in range(segments):
            faces.append((front + index, back + index, back + index + 1, front + index + 1))
    faces.extend(((0, stride, stride * 3, stride * 2), (segments, stride + segments, stride * 3 + segments, stride * 2 + segments)))
    create_mesh_object(objects, name, vertices, faces, mat, cfg, "physical_arch_ring", role=role)


def add_pyramid_roof(
    objects: list[bpy.types.Object],
    *,
    name: str,
    width: float,
    depth: float,
    base_z: float,
    height: float,
    mat: bpy.types.Material,
    cfg: dict,
    role: str = "assembled",
) -> None:
    vertices = [
        (-width / 2, -depth / 2, base_z),
        (width / 2, -depth / 2, base_z),
        (width / 2, depth / 2, base_z),
        (-width / 2, depth / 2, base_z),
        (0.0, 0.0, base_z + height),
    ]
    faces = [(0, 1, 2, 3), (0, 4, 1), (1, 4, 2), (2, 4, 3), (3, 4, 0)]
    create_mesh_object(objects, name, vertices, faces, mat, cfg, "faceted_pyramidal_roof", role=role)


def add_hip_roof(
    objects: list[bpy.types.Object],
    *,
    name: str,
    width: float,
    depth: float,
    base_z: float,
    height: float,
    ridge_fraction: float,
    mat: bpy.types.Material,
    cfg: dict,
    role: str = "assembled",
) -> None:
    """Create one continuous shallow hip volume with a real ridge."""
    ridge_x = width * ridge_fraction * 0.5
    vertices = [
        (-width / 2, -depth / 2, base_z),
        (width / 2, -depth / 2, base_z),
        (width / 2, depth / 2, base_z),
        (-width / 2, depth / 2, base_z),
        (-ridge_x, 0.0, base_z + height),
        (ridge_x, 0.0, base_z + height),
    ]
    faces = [
        (0, 3, 2, 1),
        (0, 1, 5, 4),
        (3, 4, 5, 2),
        (0, 4, 3),
        (1, 2, 5),
    ]
    create_mesh_object(objects, name, vertices, faces, mat, cfg, "continuous_shallow_hip_roof", role=role)


def add_battered_block(
    objects: list[bpy.types.Object],
    *,
    name: str,
    base_width: float,
    top_width: float,
    depth: float,
    height: float,
    centre_x: float,
    centre_y: float,
    base_z: float,
    mat: bpy.types.Material,
    cfg: dict,
    role: str = "assembled",
) -> None:
    y0, y1 = centre_y - depth / 2, centre_y + depth / 2
    vertices = [
        (centre_x - base_width / 2, y0, base_z), (centre_x + base_width / 2, y0, base_z),
        (centre_x + base_width / 2, y1, base_z), (centre_x - base_width / 2, y1, base_z),
        (centre_x - top_width / 2, y0, base_z + height), (centre_x + top_width / 2, y0, base_z + height),
        (centre_x + top_width / 2, y1, base_z + height), (centre_x - top_width / 2, y1, base_z + height),
    ]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    create_mesh_object(objects, name, vertices, faces, mat, cfg, "battered_pylon_mass", role=role)


def add_sector_shell(
    objects: list[bpy.types.Object],
    *,
    name: str,
    centre: tuple[float, float],
    inner_radius: float,
    outer_radius: float,
    start_angle: float,
    end_angle: float,
    base_z: float,
    height: float,
    mat: bpy.types.Material,
    cfg: dict,
    semantic: str,
    role: str = "assembled",
    segments: int = 18,
) -> None:
    cx, cy = centre
    vertices: list[tuple[float, float, float]] = []
    for z in (base_z, base_z + height):
        for radius in (inner_radius, outer_radius):
            for index in range(segments + 1):
                angle = start_angle + (end_angle - start_angle) * index / segments
                vertices.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius, z))
    stride = segments + 1
    faces: list[tuple[int, ...]] = []
    for layer in range(2):
        base = layer * 2 * stride
        for index in range(segments):
            faces.append((base + index, base + index + 1, base + stride + index + 1, base + stride + index))
    for radius in range(2):
        low = radius * stride
        high = 2 * stride + radius * stride
        for index in range(segments):
            faces.append((low + index, high + index, high + index + 1, low + index + 1))
    faces.extend(((0, stride, 3 * stride, 2 * stride), (segments, stride + segments, 3 * stride + segments, 2 * stride + segments)))
    create_mesh_object(objects, name, vertices, faces, mat, cfg, semantic, role=role)


def add_deco_storey(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    width: float,
    depth: float,
    base_z: float,
    height: float,
    front_bays: int,
    side_bays: int,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
    mosaic: bool = False,
    omit_front: bool = False,
) -> None:
    centre_z = base_z + height * 0.52
    opening_height = height * 0.66
    spandrel = mats["ornament"] if mosaic else mats["primary"]
    for y, sign, name in ((-depth / 2, -1.0, "Front"), (depth / 2, 1.0, "Rear")):
        add_box(objects, f"{prefix}_{name}_Spandrel", (width, 0.42, height * 0.27), (0.0, y - sign * 0.20, base_z + height * 0.135), spandrel, cfg, "polychrome_spandrel_or_sill", role=role)
        if not (omit_front and sign < 0):
            add_window_band_y(objects, prefix=f"{prefix}_{name}", width=width - 0.85, facade_y=y, centre_z=centre_z, height=opening_height, bays=front_bays, outward_sign=sign, mats=mats, cfg=cfg, role=role)
    for x, sign, name in ((-width / 2, -1.0, "Left"), (width / 2, 1.0, "Right")):
        add_box(objects, f"{prefix}_{name}_Spandrel", (0.42, depth, height * 0.27), (x - sign * 0.20, 0.0, base_z + height * 0.135), spandrel, cfg, "wrapped_polychrome_spandrel", role=role)
        add_window_band_x(objects, prefix=f"{prefix}_{name}", depth=depth - 0.85, facade_x=x, centre_z=centre_z, height=opening_height, bays=side_bays, outward_sign=sign, mats=mats, cfg=cfg, role=role)
    add_box(objects, f"{prefix}_FloorPlate", (width - 0.55, depth - 0.55, 0.17), (0.0, 0.0, base_z + 0.09), mats["secondary"], cfg, "physical_floor_datum", role=role)


def add_punched_window_y(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    centre_x: float,
    facade_y: float,
    centre_z: float,
    width: float,
    height: float,
    outward_sign: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
) -> None:
    glass_y = facade_y + outward_sign * 0.08
    interior_y = facade_y - outward_sign * 0.18
    frame_y = facade_y + outward_sign * 0.14
    add_box(objects, prefix + "_Occupied", (width - 0.18, 0.07, height - 0.18), (centre_x, interior_y, centre_z), mats["interior"], cfg, "deep_occupied_punched_opening", role=role)
    add_box(objects, prefix + "_Glass", (width - 0.12, 0.10, height - 0.12), (centre_x, glass_y, centre_z), mats["glass"], cfg, "physical_recessed_punched_glass", role=role)
    for x in (centre_x - width / 2, centre_x + width / 2):
        add_box(objects, prefix + f"_Jamb_{x:.2f}", (0.16, 0.22, height), (x, frame_y, centre_z), mats["frame"], cfg, "deep_punched_window_frame", role=role)
    for z in (centre_z - height / 2, centre_z + height / 2):
        add_box(objects, prefix + f"_Rail_{z:.2f}", (width, 0.22, 0.16), (centre_x, frame_y, z), mats["frame"], cfg, "deep_punched_window_frame", role=role)


def add_punched_window_x(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    centre_y: float,
    facade_x: float,
    centre_z: float,
    width: float,
    height: float,
    outward_sign: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
) -> None:
    glass_x = facade_x + outward_sign * 0.08
    interior_x = facade_x - outward_sign * 0.18
    frame_x = facade_x + outward_sign * 0.14
    add_box(objects, prefix + "_Occupied", (0.07, width - 0.18, height - 0.18), (interior_x, centre_y, centre_z), mats["interior"], cfg, "deep_occupied_punched_opening", role=role)
    add_box(objects, prefix + "_Glass", (0.10, width - 0.12, height - 0.12), (glass_x, centre_y, centre_z), mats["glass"], cfg, "physical_recessed_punched_glass", role=role)
    for y in (centre_y - width / 2, centre_y + width / 2):
        add_box(objects, prefix + f"_Jamb_{y:.2f}", (0.22, 0.16, height), (frame_x, y, centre_z), mats["frame"], cfg, "deep_punched_window_frame", role=role)
    for z in (centre_z - height / 2, centre_z + height / 2):
        add_box(objects, prefix + f"_Rail_{z:.2f}", (0.22, width, 0.16), (frame_x, centre_y, z), mats["frame"], cfg, "deep_punched_window_frame", role=role)


def add_punched_deco_storey(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    width: float,
    depth: float,
    base_z: float,
    height: float,
    front_bays: int,
    side_bays: int,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
    mosaic: bool = False,
    omit_front: bool = False,
) -> None:
    opening_height = height * 0.57
    centre_z = base_z + height * 0.57
    for y, sign, face in ((-depth / 2, -1.0, "Front"), (depth / 2, 1.0, "Rear")):
        if omit_front and sign < 0:
            portal_width = width * 0.34
            wing_width = (width - portal_width) / 2
            for wing_sign, wing_name in ((-1.0, "LeftWing"), (1.0, "RightWing")):
                wing_x = wing_sign * (portal_width / 2 + wing_width / 2)
                add_box(objects, f"{prefix}_{face}_{wing_name}_Wall", (wing_width, 0.38, height), (wing_x, y - sign * 0.42, base_z + height / 2), mats["primary"], cfg, "solid_portal_flanking_terracotta_wall", role=role)
                for bay in range(2):
                    x = wing_x - wing_width * 0.24 + bay * wing_width * 0.48
                    add_punched_window_y(objects, prefix=f"{prefix}_{face}_{wing_name}_Window_{bay}", centre_x=x, facade_y=y, centre_z=centre_z, width=wing_width * 0.25, height=opening_height, outward_sign=sign, mats=mats, cfg=cfg, role=role)
        else:
            add_box(objects, f"{prefix}_{face}_Wall", (width, 0.38, height), (0.0, y - sign * 0.42, base_z + height / 2), mats["primary"], cfg, "solid_glazed_terracotta_wall_field", role=role)
            bay_pitch = (width - 1.4) / front_bays
            window_width = bay_pitch * 0.48
            for bay in range(front_bays):
                x = -(width - 1.4) / 2 + bay_pitch * (bay + 0.5)
                add_punched_window_y(objects, prefix=f"{prefix}_{face}_Window_{bay}", centre_x=x, facade_y=y, centre_z=centre_z, width=window_width, height=opening_height, outward_sign=sign, mats=mats, cfg=cfg, role=role)
                add_box(objects, f"{prefix}_{face}_Pier_{bay}", (bay_pitch * 0.24, 0.50, height), (x - bay_pitch / 2, y + sign * 0.22, base_z + height / 2), mats["secondary"], cfg, "cream_or_chrome_vertical_pier", role=role)
        belt_mat = mats["ornament"] if mosaic else mats["secondary"]
        add_box(objects, f"{prefix}_{face}_Belt", (width, 0.56, 0.42 if not mosaic else 0.62), (0.0, y + sign * 0.27, base_z + height * 0.16), belt_mat, cfg, "polychrome_chevron_spandrel_belt" if mosaic else "molded_terracotta_spandrel_belt", role=role)
        if mosaic:
            chevrons = max(4, front_bays * 2)
            pitch = width / chevrons
            zc = base_z + height * 0.16
            for index in range(chevrons):
                x0 = -width / 2 + index * pitch
                xm = x0 + pitch / 2
                x1 = x0 + pitch
                add_beam(objects, f"{prefix}_{face}_ChevronA_{index}", (x0, y + sign * 0.59, zc + 0.18), (xm, y + sign * 0.59, zc - 0.18), 0.075, mats["frame"], cfg, "physical_polychrome_chevron_tesserae", role=role)
                add_beam(objects, f"{prefix}_{face}_ChevronB_{index}", (xm, y + sign * 0.59, zc - 0.18), (x1, y + sign * 0.59, zc + 0.18), 0.075, mats["frame"], cfg, "physical_polychrome_chevron_tesserae", role=role)
    for x, sign, face in ((-width / 2, -1.0, "Left"), (width / 2, 1.0, "Right")):
        add_box(objects, f"{prefix}_{face}_Wall", (0.38, depth, height), (x - sign * 0.42, 0.0, base_z + height / 2), mats["primary"], cfg, "wrapped_solid_glazed_terracotta_wall_field", role=role)
        bay_pitch = (depth - 1.4) / side_bays
        window_width = bay_pitch * 0.48
        for bay in range(side_bays):
            y = -(depth - 1.4) / 2 + bay_pitch * (bay + 0.5)
            add_punched_window_x(objects, prefix=f"{prefix}_{face}_Window_{bay}", centre_y=y, facade_x=x, centre_z=centre_z, width=window_width, height=opening_height, outward_sign=sign, mats=mats, cfg=cfg, role=role)
        belt_mat = mats["ornament"] if mosaic else mats["secondary"]
        add_box(objects, f"{prefix}_{face}_Belt", (0.56, depth, 0.42 if not mosaic else 0.62), (x + sign * 0.27, 0.0, base_z + height * 0.16), belt_mat, cfg, "wrapped_polychrome_spandrel_belt", role=role)
    add_box(objects, f"{prefix}_FloorPlate", (width - 0.8, depth - 0.8, 0.20), (0.0, 0.0, base_z + 0.10), mats["secondary"], cfg, "paired_internal_floor_datum", role=role)


def add_deco_stage(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    width: float,
    depth: float,
    base_z: float,
    floors: int,
    bays: int,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
    portal_floors: int = 0,
) -> float:
    floor_height = cfg.get("visual_floor_height", cfg["floor_height"])
    side_bays = max(3, round(bays * depth / width))
    for floor in range(floors):
        add_punched_deco_storey(
            objects,
            prefix=f"{prefix}_{floor:02d}",
            width=width,
            depth=depth,
            base_z=base_z + floor * floor_height,
            height=floor_height,
            front_bays=bays,
            side_bays=side_bays,
            mats=mats,
            cfg=cfg,
            role=role,
            mosaic=(floor % 4 == 3 or floor == floors - 1),
            omit_front=floor < portal_floors,
        )
    # Continuous piers are physically separate and visually connect the floor
    # bands, preventing the tower from reading as a stack of decorated boxes.
    stage_height = floors * floor_height
    bay = (width - 1.0) / bays
    for index in range(bays + 1):
        x = -(width - 1.0) / 2 + index * bay
        if not (portal_floors and abs(x) < width * 0.16):
            add_box(objects, f"{prefix}_FrontPier_{index}", (0.28, 0.46, stage_height), (x, -depth / 2 - 0.16, base_z + stage_height / 2), mats["secondary"], cfg, "continuous_vertical_terracotta_pier", role=role)
        add_box(objects, f"{prefix}_RearPier_{index}", (0.28, 0.46, stage_height), (x, depth / 2 + 0.16, base_z + stage_height / 2), mats["secondary"], cfg, "continuous_vertical_terracotta_pier", role=role)
    return base_z + stage_height


def build_polychrome_deco(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    add_box(objects, "POLY_Platform", (45.0, 38.0, 0.55), (0.0, 0.0, 0.275), mats["secondary"], cfg, "fixed_ashlar_platform")
    z = 0.55
    z = add_deco_stage(objects, prefix="POLY_Lower", width=44.0, depth=37.0, base_z=z, floors=8, bays=7, mats=mats, cfg=cfg, portal_floors=2)
    add_box(objects, "POLY_Terrace1", (40.0, 34.0, 0.45), (0.0, 0.0, z + 0.225), mats["roof"], cfg, "real_first_setback_terrace")
    z += 0.45
    z = add_deco_stage(objects, prefix="POLY_Middle", width=35.0, depth=30.5, base_z=z, floors=5, bays=5, mats=mats, cfg=cfg)
    add_box(objects, "POLY_Terrace2", (30.0, 27.0, 0.45), (0.0, 0.0, z + 0.225), mats["roof"], cfg, "real_second_setback_terrace")
    z += 0.45
    z = add_deco_stage(objects, prefix="POLY_Upper", width=25.0, depth=23.0, base_z=z, floors=3, bays=3, mats=mats, cfg=cfg)
    # Deep, integral two-storey portal: the lower front bands are omitted so
    # this is a true recess, not a window image laid over the tower.
    portal_y = -18.90
    add_box(objects, "POLY_PortalVoidDepth", (11.5, 1.55, 10.0), (0.0, -17.45, 5.55), mats["interior"], cfg, "carved_two_storey_public_entrance_depth")
    add_box(objects, "POLY_PortalGlass", (11.0, 0.10, 9.5), (0.0, -18.25, 5.55), mats["glass"], cfg, "recessed_public_entrance_glazing")
    for x in (-6.6, 6.6):
        add_box(objects, f"POLY_PortalPier_{x}", (1.45, 1.35, 10.2), (x, portal_y, 5.7), mats["ornament"], cfg, "integral_mosaic_portal_pier")
    add_arch_ring_y(objects, name="POLY_PortalArch", centre_x=0.0, facade_y=portal_y, spring_z=6.4, inner_radius=5.6, ring_width=1.25, thickness=1.25, mat=mats["ornament"], cfg=cfg)
    for step in range(5):
        add_box(objects, f"POLY_EntranceStep_{step}", (12.0 - step * 0.55, 0.58, 0.16), (0.0, -19.55 - step * 0.38, 0.63 + step * 0.16), mats["secondary"], cfg, "integral_public_entry_stair")
    add_box(objects, "POLY_CrownFrieze", (24.2, 22.2, 1.15), (0.0, 0.0, z + 0.575), mats["ornament"], cfg, "polychrome_crown_frieze")
    add_pyramid_roof(objects, name="POLY_GreenPyramid", width=22.6, depth=20.8, base_z=z + 1.15, height=8.7, mat=mats["roof"], cfg=cfg)
    add_cylinder(objects, "POLY_Finial", 0.16, 2.5, (0.0, 0.0, z + 11.10), mats["frame"], cfg, "slender_crown_finial", vertices=10)
    return objects


def build_black_chrome_deco(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    add_box(objects, "BLACK_Platform", (35.0, 30.0, 0.50), (0.0, 0.0, 0.25), mats["primary"], cfg, "polished_black_granite_platform")
    z = 0.50
    # Twenty-four occupied floors are grouped behind fifteen strongly expressed
    # facade tiers.  This restores the broad 1930s silhouette in the goalpost
    # instead of reading as a contemporary pencil tower.
    for stage_index, (width, depth, floors, bays) in enumerate(((34.0, 29.0, 8, 7), (27.0, 24.0, 4, 5), (19.0, 18.0, 3, 3))):
        start = z
        z = add_deco_stage(objects, prefix=f"BLACK_Stage{stage_index}", width=width, depth=depth, base_z=z, floors=floors, bays=bays, mats=mats, cfg=cfg, portal_floors=2 if stage_index == 0 else 0)
        bay = (width - 1.0) / bays
        for index in range(bays + 1):
            x = -(width - 1.0) / 2 + index * bay
            add_box(objects, f"BLACK_ChromeFin_{stage_index}_{index}", (0.16, 0.62, z - start), (x, -depth / 2 - 0.36, start + (z - start) / 2), mats["secondary"], cfg, "continuous_polished_chrome_fin")
        if stage_index < 2:
            add_box(objects, f"BLACK_Terrace_{stage_index}", (width - 1.2, depth - 1.2, 0.44), (0.0, 0.0, z + 0.22), mats["roof"], cfg, "streamlined_setback_terrace")
            z += 0.44
    # Integrated black-and-chrome entrance and fluted crown.
    add_box(objects, "BLACK_EntranceDepth", (8.5, 1.15, 6.3), (0.0, -14.15, 3.65), mats["interior"], cfg, "carved_black_granite_entrance")
    add_box(objects, "BLACK_EntranceGlass", (8.0, 0.10, 5.9), (0.0, -14.77, 3.65), mats["glass"], cfg, "recessed_entrance_glass")
    for index, x in enumerate((-3.7, -2.2, 0.0, 2.2, 3.7)):
        add_box(objects, f"BLACK_EntranceChrome_{index}", (0.16, 0.44, 6.4), (x, -14.98, 3.7), mats["secondary"], cfg, "entrance_chrome_fin")
    for index, width in enumerate((16.8, 13.2, 9.4)):
        add_box(objects, f"BLACK_CrownStep_{index}", (width, width * 0.92, 1.0 + index * 0.35), (0.0, 0.0, z + 0.5 + index * 1.15), mats["primary" if index < 2 else "secondary"], cfg, "streamlined_chrome_crown")
    for x in (-3.0, -1.5, 0.0, 1.5, 3.0):
        add_box(objects, f"BLACK_CrownFlute_{x}", (0.18, 9.0, 4.8), (x, 0.0, z + 4.4), mats["secondary"], cfg, "fluted_chrome_crown_fin")
    add_cylinder(objects, "BLACK_NeedleFinial", 0.13, 5.6, (0.0, 0.0, z + 8.9), mats["secondary"], cfg, "chrome_needle_finial", vertices=10)
    return objects


def add_roof_plane(
    objects: list[bpy.types.Object],
    *,
    name: str,
    size: tuple[float, float, float],
    location: tuple[float, float, float],
    rotation: tuple[float, float, float],
    mat: bpy.types.Material,
    cfg: dict,
    semantic: str,
    role: str = "assembled",
) -> bpy.types.Object:
    obj = add_box(objects, name, size, location, mat, cfg, semantic, role=role)
    obj.rotation_euler = rotation
    return obj


def add_rectangular_glass_level(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    width: float,
    depth: float,
    base_z: float,
    height: float,
    front_bays: int,
    side_bays: int,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
) -> None:
    centre_z = base_z + height / 2
    add_window_band_y(objects, prefix=prefix + "_Front", width=width, facade_y=-depth / 2, centre_z=centre_z, height=height - 0.32, bays=front_bays, outward_sign=-1.0, mats=mats, cfg=cfg, role=role)
    add_window_band_y(objects, prefix=prefix + "_Rear", width=width, facade_y=depth / 2, centre_z=centre_z, height=height - 0.32, bays=front_bays, outward_sign=1.0, mats=mats, cfg=cfg, role=role)
    add_window_band_x(objects, prefix=prefix + "_Left", depth=depth, facade_x=-width / 2, centre_z=centre_z, height=height - 0.32, bays=side_bays, outward_sign=-1.0, mats=mats, cfg=cfg, role=role)
    add_window_band_x(objects, prefix=prefix + "_Right", depth=depth, facade_x=width / 2, centre_z=centre_z, height=height - 0.32, bays=side_bays, outward_sign=1.0, mats=mats, cfg=cfg, role=role)
    add_box(objects, prefix + "_Slab", (width + 0.25, depth + 0.25, 0.24), (0.0, 0.0, base_z + 0.12), mats["secondary"], cfg, "physical_floor_plate", role=role)


def build_wood_stone_pavilion(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    add_box(objects, "WOODSTONE_LowerTerrace", (38.0, 25.0, 0.42), (0.0, 0.0, 0.21), mats["secondary"], cfg, "layered_native_stone_terrace")
    add_box(objects, "WOODSTONE_UpperTerrace", (31.0, 19.0, 0.34), (-1.0, -0.4, 3.78), mats["secondary"], cfg, "cantilevered_upper_stone_terrace")
    # Interlocking solid hearths anchor transparent occupied bars.
    add_box(objects, "WOODSTONE_MainHearth", (6.8, 11.0, 7.2), (-10.2, 1.5, 4.0), mats["secondary"], cfg, "massive_native_stone_hearth_core")
    add_box(objects, "WOODSTONE_EndWall", (4.0, 18.0, 6.4), (13.0, 1.0, 3.6), mats["primary"], cfg, "horizontal_cedar_end_volume")
    for level in range(2):
        base = 0.45 + level * 3.45
        add_rectangular_glass_level(objects, prefix=f"WOODSTONE_Level{level}", width=31.0 - level * 2.0, depth=18.0 - level * 1.0, base_z=base, height=3.25, front_bays=8, side_bays=5, mats=mats, cfg=cfg)
        # Warm timber datum and opaque boards interrupt the glazing just as in
        # the reference, rather than creating a generic transparent pavilion.
        add_box(objects, f"WOODSTONE_CedarBelt_{level}", (32.0 - level * 2.0, 0.44, 0.52), (-0.5, -9.35 + level * 0.5, base + 2.95), mats["primary"], cfg, "continuous_horizontal_cedar_board_belt")
    # Solid stone and cedar panels interrupt the transparent bars.  These are
    # architectural wall planes, not color baked into the window texture.
    add_box(objects, "WOODSTONE_FrontStoneWall", (10.5, 0.52, 3.15), (-7.6, -9.18, 2.05), mats["secondary"], cfg, "native_stone_front_wall_plane")
    add_box(objects, "WOODSTONE_UpperCedarWall", (14.0, 0.48, 2.95), (2.5, -8.72, 5.52), mats["primary"], cfg, "warm_cedar_upper_wall_plane")
    # One continuous shallow hip with a long ridge matches the broad sheltering
    # roof in the reference and prevents detached floating roof shards.
    add_hip_roof(objects, name="WOODSTONE_ContinuousHipRoof", width=40.0, depth=27.0, base_z=7.82, height=1.95, ridge_fraction=0.48, mat=mats["roof"], cfg=cfg)
    add_box(objects, "WOODSTONE_FrontFascia", (40.0, 0.34, 0.42), (0.0, -13.55, 7.88), mats["ornament"], cfg, "continuous_deep_roof_fascia")
    add_box(objects, "WOODSTONE_RearFascia", (40.0, 0.34, 0.42), (0.0, 13.55, 7.88), mats["ornament"], cfg, "continuous_deep_roof_fascia")
    for x in (-20.0, 20.0):
        add_box(objects, f"WOODSTONE_EndFascia_{x}", (0.34, 27.0, 0.42), (x, 0.0, 7.88), mats["ornament"], cfg, "continuous_deep_roof_fascia")
    for x in (-14.0, -4.5, 4.5, 12.0):
        add_box(objects, f"WOODSTONE_RoofPost_{x}", (0.18, 0.18, 7.7), (x, -7.8, 4.25), mats["ornament"], cfg, "slender_dark_roof_post")
    return objects


def add_screen_grid_y(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    width: float,
    facade_y: float,
    base_z: float,
    height: float,
    columns: int,
    rows: int,
    mat: bpy.types.Material,
    cfg: dict,
    role: str = "assembled",
    member: float = 0.19,
) -> None:
    for column in range(columns + 1):
        x = -width / 2 + width * column / columns
        add_box(objects, f"{prefix}_Vertical_{column}", (member, 0.28, height), (x, facade_y, base_z + height / 2), mat, cfg, "real_open_brise_soleil_member", role=role)
    for row in range(rows + 1):
        z = base_z + height * row / rows
        add_box(objects, f"{prefix}_Horizontal_{row}", (width, 0.28, member), (0.0, facade_y, z), mat, cfg, "real_open_brise_soleil_member", role=role)


def add_screen_grid_x(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    depth: float,
    facade_x: float,
    base_z: float,
    height: float,
    columns: int,
    rows: int,
    mat: bpy.types.Material,
    cfg: dict,
    role: str = "assembled",
    member: float = 0.19,
) -> None:
    for column in range(columns + 1):
        y = -depth / 2 + depth * column / columns
        add_box(objects, f"{prefix}_Vertical_{column}", (0.28, member, height), (facade_x, y, base_z + height / 2), mat, cfg, "real_open_brise_soleil_member", role=role)
    for row in range(rows + 1):
        z = base_z + height * row / rows
        add_box(objects, f"{prefix}_Horizontal_{row}", (0.28, depth, member), (facade_x, 0.0, z), mat, cfg, "real_open_brise_soleil_member", role=role)


def build_white_concrete_pavilion(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    add_box(objects, "WHITE_Plinth", (31.0, 23.0, 0.38), (0.0, 0.0, 0.19), mats["ornament"], cfg, "pale_terrazzo_pavilion_plinth")
    # Recessed ground enclosure and truly free-standing pilotis.
    add_rectangular_glass_level(objects, prefix="WHITE_Ground", width=24.5, depth=17.5, base_z=0.40, height=3.25, front_bays=7, side_bays=5, mats=mats, cfg=cfg)
    for x in (-13.5, -9.0, -4.5, 0.0, 4.5, 9.0, 13.5):
        for y in (-9.7, 9.7):
            add_cylinder(objects, f"WHITE_Pilotis_{x}_{y}", 0.16, 3.75, (x, y, 2.25), mats["primary"], cfg, "free_standing_white_concrete_pilotis", vertices=16)
    add_box(objects, "WHITE_UpperSlab", (30.0, 22.0, 0.30), (0.0, 0.0, 4.00), mats["primary"], cfg, "floating_upper_concrete_slab")
    add_rectangular_glass_level(objects, prefix="WHITE_Upper", width=27.0, depth=19.0, base_z=4.15, height=3.20, front_bays=8, side_bays=5, mats=mats, cfg=cfg)
    # Egg-crate and breeze-block screens are open physical members on all
    # exposed elevations, never a tiled opacity map.
    add_screen_grid_y(objects, prefix="WHITE_FrontScreen", width=29.0, facade_y=-10.35, base_z=4.15, height=3.20, columns=29, rows=8, mat=mats["secondary"], cfg=cfg, member=0.105)
    add_screen_grid_x(objects, prefix="WHITE_RightScreen", depth=20.0, facade_x=14.35, base_z=4.15, height=3.20, columns=20, rows=8, mat=mats["secondary"], cfg=cfg, member=0.105)
    add_box(objects, "WHITE_PlantedTerrace", (27.0, 4.0, 0.32), (0.0, -8.6, 7.62), mats["ornament"], cfg, "planted_upper_terrace_bed")
    for index, x in enumerate((-11.5, -8.7, -5.8, -2.9, 0.0, 2.9, 5.8, 8.7, 11.5)):
        add_sphere(objects, f"WHITE_TerracePlant_{index}", 0.54, (x, -8.7, 8.08 + (index % 2) * 0.10), mats["plant"], cfg, "living_upper_terrace_plant", scale=(1.15, 0.72, 0.86))
    # A recessed glazed rooftop garden room rises behind the planting.  It is
    # visually a clerestory pavilion, not a third generic stacked floor.
    add_rectangular_glass_level(objects, prefix="WHITE_RoofGardenRoom", width=23.0, depth=14.5, base_z=7.72, height=2.45, front_bays=8, side_bays=5, mats=mats, cfg=cfg)
    add_box(objects, "WHITE_ThinFlatCanopy", (32.5, 24.5, 0.32), (0.0, 0.0, 10.38), mats["roof"], cfg, "wafer_thin_horizontal_pavilion_canopy")
    return objects


def add_koshi_screen(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    width: float,
    facade_y: float,
    base_z: float,
    height: float,
    slats: int,
    mat: bpy.types.Material,
    cfg: dict,
    role: str = "assembled",
    rails: int = 3,
) -> None:
    pitch = width / slats
    slat_width = min(0.11, pitch * 0.38)
    for index in range(slats + 1):
        x = -width / 2 + index * pitch
        add_box(objects, f"{prefix}_Slat_{index}", (slat_width, 0.18, height), (x, facade_y, base_z + height / 2), mat, cfg, "real_gap_preserving_koshi_slat", role=role)
    for rail in range(rails + 1):
        z = base_z + height * rail / rails
        add_box(objects, f"{prefix}_Rail_{rail}", (width, 0.18, 0.10), (0.0, facade_y, z), mat, cfg, "real_gap_preserving_koshi_rail", role=role)


def add_koshi_screen_x(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    depth: float,
    facade_x: float,
    base_z: float,
    height: float,
    slats: int,
    mat: bpy.types.Material,
    cfg: dict,
    role: str = "assembled",
    rails: int = 3,
) -> None:
    pitch = depth / slats
    slat_width = min(0.11, pitch * 0.38)
    for index in range(slats + 1):
        y = -depth / 2 + index * pitch
        add_box(objects, f"{prefix}_Slat_{index}", (0.18, slat_width, height), (facade_x, y, base_z + height / 2), mat, cfg, "real_gap_preserving_side_koshi_slat", role=role)
    for rail in range(rails + 1):
        z = base_z + height * rail / rails
        add_box(objects, f"{prefix}_Rail_{rail}", (0.18, depth, 0.10), (facade_x, 0.0, z), mat, cfg, "real_gap_preserving_side_koshi_rail", role=role)


def add_gable_planes(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    width: float,
    depth: float,
    base_z: float,
    rise: float,
    mat: bpy.types.Material,
    cfg: dict,
    role: str = "assembled",
) -> None:
    # A closed triangular prism guarantees both slopes meet the ridge and the
    # gable ends remain integral at every export scale.
    vertices = [
        (-width / 2, -depth / 2, base_z),
        (width / 2, -depth / 2, base_z),
        (-width / 2, depth / 2, base_z),
        (width / 2, depth / 2, base_z),
        (-width / 2, 0.0, base_z + rise),
        (width / 2, 0.0, base_z + rise),
    ]
    faces = [
        (0, 2, 3, 1),
        (0, 1, 5, 4),
        (2, 4, 5, 3),
        (0, 4, 2),
        (1, 3, 5),
    ]
    create_mesh_object(objects, f"{prefix}_ContinuousGable", vertices, faces, mat, cfg, "continuous_deep_gable_roof_volume", role=role)
    add_box(objects, f"{prefix}_Ridge", (width + 0.25, 0.24, 0.24), (0.0, 0.0, base_z + rise), mat, cfg, "physical_roof_ridge", role=role)


def build_modern_machiya(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    add_box(objects, "MODMACHIYA_BasaltPlinth", (13.0, 18.0, 0.42), (0.0, 0.0, 0.21), mats["ornament"], cfg, "dark_basalt_plinth")
    # The ground footprint is split so the public passage is genuinely carved
    # through to a visible tsuboniwa rather than painted onto a black wall.
    add_box(objects, "MODMACHIYA_GroundLeft", (4.3, 15.0, 3.35), (-4.2, 0.8, 2.10), mats["secondary"], cfg, "charred_cedar_ground_wing")
    add_box(objects, "MODMACHIYA_GroundRight", (4.3, 15.0, 3.35), (4.2, 0.8, 2.10), mats["secondary"], cfg, "charred_cedar_ground_wing")
    add_box(objects, "MODMACHIYA_PassageDepth", (3.4, 15.5, 3.20), (0.0, 0.4, 2.10), mats["interior"], cfg, "carved_ground_passage_to_tsuboniwa")
    add_box(objects, "MODMACHIYA_CourtyardBed", (3.2, 4.2, 0.34), (0.0, 5.6, 0.58), mats["roof"], cfg, "visible_inner_tsuboniwa")
    for level in range(4):
        base = 0.45 + level * 3.25
        add_window_band_y(objects, prefix=f"MODMACHIYA_Front_{level}", width=11.8, facade_y=-9.05, centre_z=base + 1.62, height=2.95, bays=4, outward_sign=-1.0, mats=mats, cfg=cfg)
        add_window_band_y(objects, prefix=f"MODMACHIYA_Rear_{level}", width=11.8, facade_y=9.05, centre_z=base + 1.62, height=2.95, bays=4, outward_sign=1.0, mats=mats, cfg=cfg)
        add_box(objects, f"MODMACHIYA_SideLeft_{level}", (0.45, 17.4, 3.25), (-6.25, 0.0, base + 1.62), mats["secondary"], cfg, "charred_cedar_side_wall")
        add_box(objects, f"MODMACHIYA_SideRight_{level}", (0.45, 17.4, 3.25), (6.25, 0.0, base + 1.62), mats["secondary"], cfg, "charred_cedar_side_wall")
    add_koshi_screen(objects, prefix="MODMACHIYA_FullHeightScreen", width=12.2, facade_y=-9.42, base_z=0.48, height=13.05, slats=44, mat=mats["primary"], cfg=cfg, rails=8)
    add_koshi_screen_x(objects, prefix="MODMACHIYA_LeftWrapScreen", depth=17.4, facade_x=-6.53, base_z=0.48, height=13.05, slats=54, mat=mats["primary"], cfg=cfg, rails=8)
    add_koshi_screen_x(objects, prefix="MODMACHIYA_RightWrapScreen", depth=17.4, facade_x=6.53, base_z=0.48, height=13.05, slats=54, mat=mats["primary"], cfg=cfg, rails=8)
    add_hip_roof(objects, name="MODMACHIYA_ContinuousHipRoof", width=14.0, depth=19.0, base_z=13.35, height=1.80, ridge_fraction=0.42, mat=mats["roof"], cfg=cfg)
    # The perforated rooftop parapet encloses a small sky garden and is built
    # from the same gap-preserving screen grammar as the elevations.
    add_koshi_screen(objects, prefix="MODMACHIYA_RoofGardenFront", width=11.0, facade_y=-6.25, base_z=14.02, height=1.90, slats=18, mat=mats["primary"], cfg=cfg, rails=2)
    add_koshi_screen(objects, prefix="MODMACHIYA_RoofGardenRear", width=11.0, facade_y=6.25, base_z=14.02, height=1.90, slats=18, mat=mats["primary"], cfg=cfg, rails=2)
    add_koshi_screen_x(objects, prefix="MODMACHIYA_RoofGardenLeft", depth=12.5, facade_x=-5.50, base_z=14.02, height=1.90, slats=20, mat=mats["primary"], cfg=cfg, rails=2)
    add_koshi_screen_x(objects, prefix="MODMACHIYA_RoofGardenRight", depth=12.5, facade_x=5.50, base_z=14.02, height=1.90, slats=20, mat=mats["primary"], cfg=cfg, rails=2)
    for index, x in enumerate((-3.8, -1.9, 0.0, 1.9, 3.8)):
        add_sphere(objects, f"MODMACHIYA_RoofGardenPlant_{index}", 0.50, (x, 0.2 + (index % 2), 14.50), mats["plant"], cfg, "living_rooftop_tsuboniwa_plant", scale=(0.85, 0.85, 1.05))
    return objects


def build_cafe_machiya(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    wash_material(mats["primary"], tint=(0.42, 0.12, 0.09), factor=0.46, roughness=0.68)
    wash_material(mats["roof"], tint=(0.055, 0.065, 0.075), factor=0.84, roughness=0.76)
    add_box(objects, "CAFE_StoneSill", (18.0, 15.0, 0.34), (0.0, 0.0, 0.17), mats["ornament"], cfg, "grey_stone_machiya_sill")
    # Physical red post-and-beam frame; the large cafe room remains open.
    for x in (-8.3, -5.5, -2.7, 0.1, 2.9, 5.7, 8.3):
        add_box(objects, f"CAFE_Post_{x}", (0.24, 0.34, 6.5), (x, -7.22, 3.55), mats["primary"], cfg, "vermilion_post_and_beam_frame")
    for z in (0.48, 3.65, 6.80):
        add_box(objects, f"CAFE_Beam_{z}", (17.0, 0.34, 0.24), (0.0, -7.22, z), mats["primary"], cfg, "vermilion_post_and_beam_frame")
    add_box(objects, "CAFE_EarthenRear", (17.0, 0.42, 6.2), (0.0, 7.15, 3.55), mats["secondary"], cfg, "pale_earthen_rear_wall")
    add_box(objects, "CAFE_GroundDepth", (11.0, 0.08, 2.85), (-1.5, -6.68, 2.0), mats["interior"], cfg, "open_occupied_cafe_gallery_depth")
    add_box(objects, "CAFE_GroundGlass", (10.8, 0.10, 2.75), (-1.5, -7.00, 2.0), mats["glass"], cfg, "open_ground_cafe_glazing")
    add_koshi_screen(objects, prefix="CAFE_GroundKoshi", width=5.2, facade_y=-7.38, base_z=0.52, height=2.9, slats=20, mat=mats["primary"], cfg=cfg, rails=3)
    # Deliberately off-centre side passage exposes the inner garden.
    add_box(objects, "CAFE_SidePassage", (2.2, 12.0, 3.0), (6.8, 0.0, 1.95), mats["interior"], cfg, "open_side_passage_to_inner_garden")
    add_window_band_y(objects, prefix="CAFE_UpperGlass", width=16.3, facade_y=-7.02, centre_z=5.20, height=2.55, bays=6, outward_sign=-1.0, mats=mats, cfg=cfg)
    add_koshi_screen(objects, prefix="CAFE_UpperKoshi", width=16.5, facade_y=-7.38, base_z=3.92, height=2.65, slats=52, mat=mats["primary"], cfg=cfg, rails=4)
    # Separate bamboo blinds sit behind selected lattice bays.
    for bay in (-5.4, -1.8, 1.8):
        for slat in range(12):
            add_box(objects, f"CAFE_BambooBlind_{bay}_{slat}", (3.0, 0.06, 0.06), (bay, -7.12, 4.05 + slat * 0.19), mats["ornament"], cfg, "woven_bamboo_blind_slat")
    add_roof_plane(objects, name="CAFE_GroundEave", size=(19.2, 4.8, 0.30), location=(0.0, -6.15, 3.78), rotation=(math.radians(-4.0), 0.0, 0.0), mat=mats["roof"], cfg=cfg, semantic="continuous_lower_kawara_eave")
    add_gable_planes(objects, prefix="CAFE_KawaraRoof", width=19.0, depth=16.5, base_z=6.9, rise=3.65, mat=mats["roof"], cfg=cfg)
    # Tile battens create a real small-scale kawara rhythm on both slopes.
    for row in range(12):
        y = -7.5 + row * 1.35
        z = 7.05 + (1.0 - abs(y) / 8.1) * 3.25
        add_box(objects, f"CAFE_KawaraRow_{row}", (19.1, 0.22, 0.15), (0.0, y, z), mats["roof"], cfg, "individual_kawara_tile_row")
    return objects


def add_frame_grid(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    width: float,
    depth: float,
    base_z: float,
    levels: int,
    level_height: float,
    front_bays: int,
    side_bays: int,
    mat: bpy.types.Material,
    cfg: dict,
    role: str = "assembled",
    member: float = 0.24,
) -> None:
    full_height = levels * level_height
    for index in range(front_bays + 1):
        x = -width / 2 + width * index / front_bays
        for y in (-depth / 2, depth / 2):
            add_box(objects, f"{prefix}_ColumnY_{index}_{y}", (member, member, full_height), (x, y, base_z + full_height / 2), mat, cfg, "expressed_external_structural_column", role=role)
    for index in range(side_bays + 1):
        y = -depth / 2 + depth * index / side_bays
        for x in (-width / 2, width / 2):
            add_box(objects, f"{prefix}_ColumnX_{index}_{x}", (member, member, full_height), (x, y, base_z + full_height / 2), mat, cfg, "expressed_external_structural_column", role=role)
    for level in range(levels + 1):
        z = base_z + level * level_height
        for y in (-depth / 2, depth / 2):
            add_box(objects, f"{prefix}_BeamY_{level}_{y}", (width + member, member, member), (0.0, y, z), mat, cfg, "expressed_external_structural_beam", role=role)
        for x in (-width / 2, width / 2):
            add_box(objects, f"{prefix}_BeamX_{level}_{x}", (member, depth + member, member), (x, 0.0, z), mat, cfg, "expressed_external_structural_beam", role=role)


def build_dark_frame_office(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    add_box(objects, "DARKOFFICE_TerrazzoPlinth", (35.0, 25.0, 0.38), (0.0, 0.0, 0.19), mats["ornament"], cfg, "pale_terrazzo_public_plinth")
    for level in range(5):
        base = 0.40 + level * 4.15
        add_rectangular_glass_level(objects, prefix=f"DARKOFFICE_Level{level}", width=33.5, depth=23.5, base_z=base, height=3.98, front_bays=7, side_bays=5, mats=mats, cfg=cfg)
        # Clear physical slabs remain readable behind the outer structure.
        add_box(objects, f"DARKOFFICE_BrightSlab_{level}", (33.6, 23.6, 0.24), (0.0, 0.0, base + 0.12), mats["secondary"], cfg, "visible_bright_floor_plate")
    add_frame_grid(objects, prefix="DARKOFFICE_Exoskeleton", width=34.1, depth=24.1, base_z=0.42, levels=5, level_height=4.15, front_bays=7, side_bays=5, mat=mats["primary"], cfg=cfg, member=0.32)
    # Carved double-height corner lobby: a dark frame returns around a genuinely
    # recessed glass corner instead of a pasted entrance panel.
    add_box(objects, "DARKOFFICE_LobbyVoid", (9.0, 1.25, 7.6), (11.7, -11.45, 4.35), mats["interior"], cfg, "recessed_double_height_corner_lobby")
    add_box(objects, "DARKOFFICE_LobbyGlass", (8.4, 0.10, 7.2), (11.7, -12.05, 4.35), mats["glass"], cfg, "double_height_lobby_glass")
    add_box(objects, "DARKOFFICE_LobbyCanopy", (9.0, 2.8, 0.28), (11.7, -13.2, 8.15), mats["primary"], cfg, "integral_dark_frame_lobby_canopy")
    # Transparent rooftop room/greenhouse.
    roof_base = 21.20
    add_box(objects, "DARKOFFICE_RoofDeck", (33.5, 23.5, 0.32), (0.0, 0.0, roof_base), mats["roof"], cfg, "zinc_roof_deck")
    for side_x in (-10.0, 10.0):
        add_box(objects, f"DARKOFFICE_GreenhouseEnd_{side_x}", (0.10, 10.0, 2.5), (side_x, 0.0, roof_base + 1.45), mats["glass"], cfg, "transparent_rooftop_pavilion_glass")
    for side_y in (-5.0, 5.0):
        add_box(objects, f"DARKOFFICE_GreenhouseSide_{side_y}", (20.0, 0.10, 2.5), (0.0, side_y, roof_base + 1.45), mats["glass"], cfg, "transparent_rooftop_pavilion_glass")
    add_frame_grid(objects, prefix="DARKOFFICE_GreenhouseFrame", width=20.0, depth=10.0, base_z=roof_base + 0.2, levels=1, level_height=2.5, front_bays=5, side_bays=3, mat=mats["frame"], cfg=cfg, member=0.11)
    add_box(objects, "DARKOFFICE_GreenhouseRoof", (20.4, 10.4, 0.12), (0.0, 0.0, roof_base + 2.78), mats["glass"], cfg, "transparent_rooftop_pavilion_roof")
    return objects


def add_timber_office_bar(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    centre_x: float,
    width: float,
    depth: float,
    levels: int,
    base_z: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
) -> None:
    level_height = cfg["floor_height"]
    # Glass and room-depth cards are independent of the glulam frame.
    for level in range(levels):
        z = base_z + level * level_height
        for y, sign, face in ((-depth / 2, -1.0, "Front"), (depth / 2, 1.0, "Rear")):
            clear = width - 0.6
            add_box(objects, f"{prefix}_{face}_Occupied_{level}", (clear, 0.08, level_height - 0.42), (centre_x, y - sign * 0.34, z + level_height / 2), mats["interior"], cfg, "biophilic_occupied_office_depth", role=role)
            add_box(objects, f"{prefix}_{face}_Glass_{level}", (clear, 0.10, level_height - 0.36), (centre_x, y, z + level_height / 2), mats["glass"], cfg, "neutral_low_iron_glazing", role=role)
        add_box(objects, f"{prefix}_CLTSlab_{level}", (width, depth, 0.28), (centre_x, 0.0, z + 0.14), mats["secondary"], cfg, "visible_clt_floor_plate", role=role)
    front_bays = max(3, round(width / 4.3))
    for column in range(front_bays + 1):
        x = centre_x - width / 2 + width * column / front_bays
        for y in (-depth / 2 - 0.18, depth / 2 + 0.18):
            add_box(objects, f"{prefix}_GlulamColumn_{column}_{y}", (0.34, 0.46, levels * level_height), (x, y, base_z + levels * level_height / 2), mats["primary"], cfg, "complete_external_glulam_column", role=role)
    for level in range(levels + 1):
        z = base_z + level * level_height
        for y in (-depth / 2 - 0.18, depth / 2 + 0.18):
            add_box(objects, f"{prefix}_GlulamBeam_{level}_{y}", (width + 0.3, 0.46, 0.34), (centre_x, y, z), mats["primary"], cfg, "complete_external_glulam_beam", role=role)


def build_timber_hybrid_office(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    add_box(objects, "TIMBEROFFICE_ConcretePlinth", (45.0, 28.0, 0.42), (0.0, 0.0, 0.21), mats["ornament"], cfg, "pale_concrete_public_plinth")
    # Two bars are offset in plan and height, giving the reference its stepped,
    # sawtooth silhouette and a real recessed entrance court between them.
    add_timber_office_bar(objects, prefix="TIMBEROFFICE_WestBar", centre_x=-10.8, width=22.0, depth=25.0, levels=5, base_z=0.45, mats=mats, cfg=cfg)
    add_timber_office_bar(objects, prefix="TIMBEROFFICE_EastBar", centre_x=11.8, width=19.5, depth=21.0, levels=4, base_z=0.45, mats=mats, cfg=cfg)
    add_box(objects, "TIMBEROFFICE_EntryCourt", (5.0, 10.0, 0.22), (1.0, -8.5, 0.53), mats["ornament"], cfg, "recessed_landscaped_entry_court")
    add_box(objects, "TIMBEROFFICE_EntryGlass", (4.5, 0.10, 4.2), (1.0, -12.0, 2.6), mats["glass"], cfg, "recessed_mass_timber_entry_glass")
    add_box(objects, "TIMBEROFFICE_EntryDepth", (4.3, 0.08, 4.0), (1.0, -11.65, 2.6), mats["interior"], cfg, "warm_mass_timber_lobby_depth")
    # Sawtooth clerestory roofs, separately framed and glazed.
    roof_z = 19.25
    for index, x in enumerate((-16.0, -9.0, -2.0)):
        add_roof_plane(objects, name=f"TIMBEROFFICE_WestSawtoothMetal_{index}", size=(7.3, 26.0, 0.20), location=(x, 0.0, roof_z + 1.05), rotation=(0.0, math.radians(-10.0), 0.0), mat=mats["roof"], cfg=cfg, semantic="standing_seam_sawtooth_roof")
        add_box(objects, f"TIMBEROFFICE_WestClerestory_{index}", (0.10, 24.0, 1.7), (x + 3.2, 0.0, roof_z + 1.1), mats["glass"], cfg, "clear_sawtooth_clerestory")
    east_z = 15.5
    for index, x in enumerate((7.0, 13.5, 19.5)):
        add_roof_plane(objects, name=f"TIMBEROFFICE_EastSawtoothMetal_{index}", size=(6.6, 22.0, 0.20), location=(x, 0.0, east_z + 1.0), rotation=(0.0, math.radians(-10.0), 0.0), mat=mats["roof"], cfg=cfg, semantic="standing_seam_sawtooth_roof")
        add_box(objects, f"TIMBEROFFICE_EastClerestory_{index}", (0.10, 20.0, 1.6), (x + 2.9, 0.0, east_z + 1.05), mats["glass"], cfg, "clear_sawtooth_clerestory")
    # Biophilic interior silhouettes are physical clusters behind the glass.
    for index, (x, y, z) in enumerate(((-15, -10, 4.5), (-7, -10, 8.2), (9, -8, 4.4), (16, -7, 11.8))):
        add_cylinder(objects, f"TIMBEROFFICE_InteriorTreeTrunk_{index}", 0.10, 2.2, (x, y, z), mats["ornament"], cfg, "visible_biophilic_interior_tree", vertices=10)
        add_sphere(objects, f"TIMBEROFFICE_InteriorTreeCrown_{index}", 0.75, (x, y, z + 1.4), mats["roof"], cfg, "visible_biophilic_interior_tree", scale=(1.0, 1.0, 1.2))
    return objects


def add_curved_band(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    centre: tuple[float, float],
    inner_radius: float,
    outer_radius: float,
    base_z: float,
    height: float,
    mat: bpy.types.Material,
    cfg: dict,
    semantic: str,
    role: str = "assembled",
    start_angle: float = -math.pi / 2,
    end_angle: float = 0.0,
) -> None:
    add_sector_shell(objects, name=prefix, centre=centre, inner_radius=inner_radius, outer_radius=outer_radius, start_angle=start_angle, end_angle=end_angle, base_z=base_z, height=height, mat=mat, cfg=cfg, semantic=semantic, role=role, segments=36)


def build_streamline_theater(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    # Deep auditorium behind the public curved corner.
    add_box(objects, "STREAM_Auditorium", (25.5, 27.0, 13.2), (-0.6, 2.2, 6.8), mats["primary"], cfg, "deep_fixed_auditorium_volume")
    add_box(objects, "STREAM_StageTower", (17.0, 12.0, 4.2), (-2.5, 8.5, 15.1), mats["primary"], cfg, "integral_auditorium_fly_volume")
    # The reference is a rounded rectangle: a broad flat entrance between two
    # quarter-cylinder corners.  Separate concentric construction shells make
    # the glass-block ribbons and glazing physically wrap both corners.
    corner_radius = 5.55
    left_centre = (-7.0, -7.0)
    right_centre = (7.0, -7.0)
    corners = (
        ("Left", left_centre, -math.pi, -math.pi / 2),
        ("Right", right_centre, -math.pi / 2, 0.0),
    )
    for suffix, centre, start, end in corners:
        add_curved_band(objects, prefix=f"STREAM_CurvedLobbyDepth{suffix}", centre=centre, inner_radius=5.12, outer_radius=5.22, base_z=0.5, height=10.5, mat=mats["interior"], cfg=cfg, semantic="occupied_rounded_corner_lobby_depth", start_angle=start, end_angle=end)
        add_curved_band(objects, prefix=f"STREAM_CurvedLobbyGlass{suffix}", centre=centre, inner_radius=5.30, outer_radius=5.42, base_z=0.5, height=7.2, mat=mats["glass"], cfg=cfg, semantic="physical_rounded_corner_lobby_glass", start_angle=start, end_angle=end)
        add_curved_band(objects, prefix=f"STREAM_GlassBlockRibbon{suffix}", centre=centre, inner_radius=5.44, outer_radius=5.62, base_z=7.85, height=2.05, mat=mats["secondary"], cfg=cfg, semantic="translucent_glass_block_ribbon", start_angle=start, end_angle=end)
    add_box(objects, "STREAM_FrontOccupiedDepth", (13.9, 0.08, 10.5), (0.0, -12.18, 5.75), mats["interior"], cfg, "occupied_flat_front_lobby_depth")
    add_box(objects, "STREAM_FrontLobbyGlass", (13.9, 0.12, 7.2), (0.0, -12.38, 4.10), mats["glass"], cfg, "physical_flat_front_lobby_glass")
    add_box(objects, "STREAM_FrontGlassBlockRibbon", (13.9, 0.18, 2.05), (0.0, -12.48, 8.875), mats["secondary"], cfg, "translucent_front_glass_block_ribbon")
    add_screen_grid_y(objects, prefix="STREAM_FrontGlassBlockJoints", width=13.9, facade_y=-12.70, base_z=7.85, height=2.05, columns=28, rows=5, mat=mats["frame"], cfg=cfg, member=0.055)
    for z in (0.45, 3.1, 6.0, 7.35, 10.0, 11.25):
        add_box(objects, f"STREAM_FrontSpeedBand_{z}", (14.1, 0.25, 0.30), (0.0, -12.62, z + 0.15), mats["primary"], cfg, "continuous_flat_front_speed_band")
        for suffix, centre, start, end in corners:
            add_curved_band(objects, prefix=f"STREAM_WhiteSpeedBand_{suffix}_{z}", centre=centre, inner_radius=5.60, outer_radius=5.84, base_z=z, height=0.30, mat=mats["primary"], cfg=cfg, semantic="sweeping_integral_speed_band", start_angle=start, end_angle=end)
    for z, mat in ((3.50, mats["ornament"]), (6.40, mats["secondary"]), (10.42, mats["ornament"])):
        add_box(objects, f"STREAM_FrontNeonBand_{z}", (14.1, 0.10, 0.14), (0.0, -12.78, z + 0.07), mat, cfg, "restrained_integral_neon_band")
        for suffix, centre, start, end in corners:
            add_curved_band(objects, prefix=f"STREAM_NeonBand_{suffix}_{z}", centre=centre, inner_radius=5.84, outer_radius=5.93, base_z=z, height=0.14, mat=mat, cfg=cfg, semantic="restrained_integral_neon_band", start_angle=start, end_angle=end)
    for row in range(1, 5):
        z = 7.85 + row * 2.05 / 5
        for suffix, centre, start, end in corners:
            add_curved_band(objects, prefix=f"STREAM_GlassBlockJoint_{suffix}_{row}", centre=centre, inner_radius=5.62, outer_radius=5.69, base_z=z, height=0.055, mat=mats["frame"], cfg=cfg, semantic="physical_curved_glass_block_joint", start_angle=start, end_angle=end)
    for suffix, centre, start, end in corners:
        for index in range(8):
            angle = start + (end - start) * index / 7
            x = centre[0] + math.cos(angle) * 5.95
            y = centre[1] + math.sin(angle) * 5.95
            add_cylinder(objects, f"STREAM_CurvedMullion_{suffix}_{index}", 0.075, 9.4, (x, y, 5.2), mats["frame"], cfg, "physical_curved_lobby_mullion", vertices=10)
    for index in range(8):
        x = -6.8 + index * 13.6 / 7
        add_box(objects, f"STREAM_FrontMullion_{index}", (0.12, 0.22, 9.4), (x, -12.72, 5.2), mats["frame"], cfg, "physical_flat_front_lobby_mullion")
    add_box(objects, "STREAM_EntranceDepth", (4.6, 1.20, 4.35), (0.0, -12.45, 2.68), mats["interior"], cfg, "carved_central_theater_entrance")
    add_box(objects, "STREAM_EntranceGlass", (4.2, 0.10, 3.95), (0.0, -13.08, 2.68), mats["glass"], cfg, "recessed_central_theater_doors")
    add_box(objects, "STREAM_Marquee", (26.5, 5.0, 0.50), (0.0, -14.2, 4.25), mats["frame"], cfg, "sweeping_integral_cantilevered_marquee")
    add_box(objects, "STREAM_MarqueeSoffit", (25.7, 4.5, 0.14), (0.0, -14.2, 3.92), mats["ornament"], cfg, "illuminated_marquee_soffit")
    # Fin-shaped blade grows from the lobby wall and is braced into the marquee.
    add_battered_block(objects, name="STREAM_IntegralFin", base_width=3.3, top_width=1.0, depth=2.0, height=17.5, centre_x=5.7, centre_y=-12.0, base_z=1.0, mat=mats["primary"], cfg=cfg)
    for z in (5.2, 8.0, 10.8, 13.6, 16.2):
        add_box(objects, f"STREAM_FinNeon_{z}", (2.25 - z * 0.035, 0.22, 0.13), (5.7, -13.05, z), mats["ornament"], cfg, "integral_fin_neon_detail")
    add_box(objects, "STREAM_AuditoriumRoof", (25.5, 27.0, 0.38), (-0.6, 2.2, 13.60), mats["roof"], cfg, "charcoal_auditorium_roof")
    return objects


def add_lotus_column(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    x: float,
    y: float,
    base_z: float,
    height: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
) -> None:
    add_cylinder(objects, prefix + "_Shaft", 0.38, height - 1.05, (x, y, base_z + (height - 1.05) / 2), mats["primary"], cfg, "separate_lotus_column_shaft", vertices=18, role=role)
    add_cylinder(objects, prefix + "_Base", 0.60, 0.45, (x, y, base_z + 0.23), mats["secondary"], cfg, "lotus_column_base", vertices=18, role=role)
    for ring, radius in enumerate((0.48, 0.62, 0.78)):
        add_cylinder(objects, prefix + f"_Capital_{ring}", radius, 0.28, (x, y, base_z + height - 0.88 + ring * 0.25), mats["ornament" if ring == 1 else "primary"], cfg, "painted_lotus_column_capital", vertices=18, role=role)


def build_egyptian_theater(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    add_box(objects, "EGYPT_Auditorium", (29.0, 29.0, 12.5), (0.0, 2.5, 6.55), mats["secondary"], cfg, "deep_fixed_egyptian_auditorium")
    add_box(objects, "EGYPT_AuditoriumRoof", (29.0, 29.0, 0.42), (0.0, 2.5, 12.95), mats["roof"], cfg, "charcoal_auditorium_roof")
    # Shallow battered pylons frame a broad recessed temple front.  Their taper
    # is deliberately restrained so the facade reads like the reference's
    # monumental horizontal theater, not two freestanding pyramids.
    for x, name in ((-11.5, "Left"), (11.5, "Right")):
        add_battered_block(objects, name=f"EGYPT_{name}Pylon", base_width=6.2, top_width=5.5, depth=5.2, height=14.6, centre_x=x, centre_y=-13.5, base_z=0.4, mat=mats["primary"], cfg=cfg)
        for z in (4.6, 9.4, 13.7):
            add_box(objects, f"EGYPT_{name}PylonBand_{z}", (5.9 - z * 0.025, 0.30, 0.28), (x, -16.18, z), mats["ornament"], cfg, "turquoise_copper_pylon_inlay")
        add_box(objects, f"EGYPT_{name}InsetPanel", (3.05, 0.24, 6.2), (x, -16.22, 8.2), mats["secondary"], cfg, "recessed_monumental_pylon_panel")
        for offset in (-1.72, 1.72):
            add_box(objects, f"EGYPT_{name}PanelJamb_{offset}", (0.16, 0.34, 6.6), (x + offset, -16.35, 8.2), mats["ornament"], cfg, "turquoise_inset_panel_jamb")
        add_sphere(objects, f"EGYPT_{name}ScarabRelief", 0.42, (x, -16.38, 12.95), mats["ornament"], cfg, "small_integral_scarab_relief", scale=(1.0, 0.20, 1.18))
    add_box(objects, "EGYPT_EntryCourtDepth", (18.0, 6.0, 12.4), (0.0, -12.2, 6.6), mats["interior"], cfg, "deep_shadowed_ceremonial_entry_court")
    add_box(objects, "EGYPT_LobbyGlass", (17.6, 0.10, 4.4), (0.0, -14.65, 2.9), mats["glass"], cfg, "recessed_ceremonial_lobby_glass")
    for door_index, x in enumerate((-6.0, 0.0, 6.0)):
        add_box(objects, f"EGYPT_DoorDepth_{door_index}", (4.2, 0.20, 3.65), (x, -15.10, 2.42), mats["interior"], cfg, "recessed_bronze_entry_door_bay")
        for jamb in (-2.0, 0.0, 2.0):
            add_box(objects, f"EGYPT_DoorJamb_{door_index}_{jamb}", (0.14, 0.28, 3.72), (x + jamb, -15.28, 2.42), mats["frame"], cfg, "physical_bronze_entry_door_jamb")
    for window_index, x in enumerate((-6.2, -2.1, 2.1, 6.2)):
        add_box(objects, f"EGYPT_UpperWindowDepth_{window_index}", (2.0, 0.08, 4.8), (x, -14.72, 8.95), mats["interior"], cfg, "deep_upper_portico_window")
        add_box(objects, f"EGYPT_UpperWindowGlass_{window_index}", (1.8, 0.10, 4.6), (x, -14.88, 8.95), mats["glass"], cfg, "tall_upper_portico_glazing")
    for index, x in enumerate((-6.0, -2.0, 2.0, 6.0)):
        add_lotus_column(objects, prefix=f"EGYPT_Lotus_{index}", x=x, y=-15.35, base_z=5.55, height=6.65, mats=mats, cfg=cfg)
    add_box(objects, "EGYPT_Entablature", (19.5, 3.8, 1.05), (0.0, -14.1, 12.65), mats["primary"], cfg, "deep_egyptian_entry_entablature")
    add_box(objects, "EGYPT_PolychromeFrieze", (19.0, 0.32, 0.62), (0.0, -16.05, 12.7), mats["ornament"], cfg, "turquoise_copper_hieroglyphic_frieze")
    add_box(objects, "EGYPT_ContinuousCornice", (30.5, 2.7, 0.72), (0.0, -14.25, 15.12), mats["primary"], cfg, "broad_continuous_egyptian_cornice")
    add_box(objects, "EGYPT_CorniceCopperLip", (31.2, 2.95, 0.24), (0.0, -14.32, 15.55), mats["ornament"], cfg, "rolled_turquoise_cornice_lip")
    # Winged sun disc assembled from a central solar disc and two tapering wings.
    add_cylinder(objects, "EGYPT_SunDisc", 0.72, 0.22, (0.0, -16.35, 14.05), mats["ornament"], cfg, "winged_sun_disc_relief", vertices=24)
    bpy.context.view_layer.update()
    # Cylinder depth is along local Z; rotate into the facade plane.
    objects[-1].rotation_euler.x = math.radians(90.0)
    for side in (-1.0, 1.0):
        for feather in range(7):
            x0 = side * (0.65 + feather * 0.75)
            x1 = side * (1.4 + feather * 0.92)
            add_beam(objects, f"EGYPT_SunWing_{side}_{feather}", (x0, -16.40, 14.05 - feather * 0.045), (x1, -16.40, 13.72 - feather * 0.09), 0.14, mats["ornament"], cfg, "winged_sun_disc_feather")
    add_box(objects, "EGYPT_Marquee", (20.5, 4.8, 0.48), (0.0, -17.6, 5.15), mats["frame"], cfg, "integral_bronze_theater_marquee")
    add_box(objects, "EGYPT_MarqueeSoffit", (19.8, 4.2, 0.14), (0.0, -17.6, 4.82), mats["ornament"], cfg, "turquoise_marquee_soffit")
    for step in range(5):
        add_box(objects, f"EGYPT_EntryStep_{step}", (16.0 - step * 0.55, 0.58, 0.16), (0.0, -17.0 - step * 0.38, 0.48 + step * 0.16), mats["secondary"], cfg, "integral_ceremonial_entry_stair")
    return objects


def build_assembled(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    return {
        "polychrome_deco": build_polychrome_deco,
        "black_chrome_deco": build_black_chrome_deco,
        "wood_stone_pavilion": build_wood_stone_pavilion,
        "white_concrete_pavilion": build_white_concrete_pavilion,
        "modern_machiya": build_modern_machiya,
        "cafe_machiya": build_cafe_machiya,
        "dark_frame_office": build_dark_frame_office,
        "timber_hybrid_office": build_timber_hybrid_office,
        "streamline_theater": build_streamline_theater,
        "egyptian_theater": build_egyptian_theater,
    }[cfg["shape"]](mats, cfg)


def build_module(
    role: str,
    variant: str,
    mats: dict,
    cfg: dict,
) -> tuple[list[bpy.types.Object], float]:
    objects: list[bpy.types.Object] = []
    width = cfg["native"][0] * 0.94
    depth = cfg["native"][1] * 0.91
    shape = cfg["shape"]
    if role == "podium":
        height = cfg["podium_height"]
        add_box(objects, "MODULE_PodiumPlinth", (width, depth, 0.34), (0.0, 0.0, 0.17), mats["secondary"], cfg, "fixed_variant_podium_plinth", role=role)
        if "deco" in shape:
            add_deco_storey(objects, prefix="MODULE_DecoPodium", width=width - 0.5, depth=depth - 0.5, base_z=0.34, height=height - 0.34, front_bays=7, side_bays=5, mats=mats, cfg=cfg, role=role, mosaic=True, omit_front=True)
            add_box(objects, "MODULE_DecoEntranceDepth", (width * 0.27, 0.75, height * 0.78), (0.0, -depth / 2 + 0.15, height * 0.47), mats["interior"], cfg, "fixed_integral_public_entrance", role=role)
        elif "theater" in shape:
            add_box(objects, "MODULE_TheaterAuditoriumBase", (width, depth, height - 0.34), (0.0, 0.0, 0.34 + (height - 0.34) / 2), mats["primary"], cfg, "fixed_theater_public_base", role=role)
            add_box(objects, "MODULE_TheaterEntryDepth", (width * 0.45, 0.90, height * 0.68), (0.0, -depth / 2 - 0.10, height * 0.45), mats["interior"], cfg, "fixed_deep_theater_entry", role=role)
        else:
            add_rectangular_glass_level(objects, prefix="MODULE_PodiumGlass", width=width - 0.8, depth=depth - 0.8, base_z=0.34, height=max(1.0, height - 0.34), front_bays=6, side_bays=4, mats=mats, cfg=cfg, role=role)
    elif role == "floor":
        height = cfg["floor_height"]
        phase = {"typical_a": 0, "typical_b": 1, "typical_c": 2}[variant]
        if "deco" in shape:
            add_deco_storey(objects, prefix=f"MODULE_Deco_{variant}", width=width, depth=depth, base_z=0.0, height=height, front_bays=7, side_bays=5, mats=mats, cfg=cfg, role=role, mosaic=phase == 2)
        elif "machiya" in shape:
            add_window_band_y(objects, prefix=f"MODULE_Machiya_{variant}", width=width - 0.8, facade_y=-depth / 2, centre_z=height / 2, height=height - 0.35, bays=5, outward_sign=-1.0, mats=mats, cfg=cfg, role=role)
            add_box(objects, "MODULE_MachiyaRear", (width, depth - 0.4, height), (0.0, 0.2, height / 2), mats["secondary"], cfg, "repeatable_complete_machiya_room_bay", role=role)
            add_koshi_screen(objects, prefix=f"MODULE_Koshi_{variant}", width=width - 0.5, facade_y=-depth / 2 - 0.24, base_z=0.12, height=height - 0.24, slats=32 + phase * 4, mat=mats["primary"], cfg=cfg, role=role, rails=3)
        elif shape == "white_concrete_pavilion":
            add_rectangular_glass_level(objects, prefix=f"MODULE_White_{variant}", width=width - 1.0, depth=depth - 1.0, base_z=0.0, height=height, front_bays=7, side_bays=5, mats=mats, cfg=cfg, role=role)
            add_screen_grid_y(objects, prefix=f"MODULE_WhiteScreen_{variant}", width=width, facade_y=-depth / 2 - 0.30, base_z=0.0, height=height, columns=10, rows=3, mat=mats["secondary"], cfg=cfg, role=role)
        elif shape == "wood_stone_pavilion":
            add_rectangular_glass_level(objects, prefix=f"MODULE_WoodStone_{variant}", width=width - 1.0, depth=depth - 1.0, base_z=0.0, height=height, front_bays=8, side_bays=5, mats=mats, cfg=cfg, role=role)
            add_box(objects, f"MODULE_CedarBelt_{variant}", (width, 0.42, 0.45), (0.0, -depth / 2 - 0.18, height - 0.30), mats["primary"], cfg, "repeatable_complete_cedar_glass_bay", role=role)
        elif shape == "timber_hybrid_office":
            add_timber_office_bar(objects, prefix=f"MODULE_TimberOffice_{variant}", centre_x=0.0, width=width, depth=depth, levels=1, base_z=0.0, mats=mats, cfg=cfg, role=role)
        else:
            add_rectangular_glass_level(objects, prefix=f"MODULE_Glass_{variant}", width=width, depth=depth, base_z=0.0, height=height, front_bays=7, side_bays=5, mats=mats, cfg=cfg, role=role)
            if shape == "dark_frame_office":
                add_frame_grid(objects, prefix=f"MODULE_DarkFrame_{variant}", width=width, depth=depth, base_z=0.0, levels=1, level_height=height, front_bays=7, side_bays=5, mat=mats["primary"], cfg=cfg, role=role, member=0.28)
            elif "theater" in shape:
                add_box(objects, f"MODULE_TheaterWall_{variant}", (width, depth, height), (0.0, 0.0, height / 2), mats["primary"], cfg, "repeatable_auditorium_height_band", role=role)
    elif role == "crown":
        height = max(0.35, cfg["crown_height"])
        add_box(objects, "MODULE_Crown", (width, depth, height), (0.0, 0.0, height / 2), mats["ornament"], cfg, "fixed_variant_crown_transition", role=role)
    else:
        height = max(0.45, cfg["roof_height"])
        if shape == "polychrome_deco":
            add_pyramid_roof(objects, name="MODULE_PolychromeRoof", width=width * 0.55, depth=depth * 0.55, base_z=0.0, height=height, mat=mats["roof"], cfg=cfg, role=role)
        elif "machiya" in shape:
            add_gable_planes(objects, prefix="MODULE_MachiyaRoof", width=width, depth=depth, base_z=0.05, rise=height * 0.82, mat=mats["roof"], cfg=cfg, role=role)
        elif shape == "white_concrete_pavilion":
            add_roof_plane(objects, name="MODULE_ButterflyLeft", size=(width / 2 + 0.5, depth, 0.24), location=(-width / 4, 0.0, height * 0.55), rotation=(0.0, math.radians(7), 0.0), mat=mats["roof"], cfg=cfg, semantic="fixed_butterfly_roof", role=role)
            add_roof_plane(objects, name="MODULE_ButterflyRight", size=(width / 2 + 0.5, depth, 0.24), location=(width / 4, 0.0, height * 0.55), rotation=(0.0, math.radians(-7), 0.0), mat=mats["roof"], cfg=cfg, semantic="fixed_butterfly_roof", role=role)
        else:
            add_box(objects, "MODULE_Roof", (width, depth, min(height, 0.55)), (0.0, 0.0, min(height, 0.55) / 2), mats["roof"], cfg, "fixed_variant_roof", role=role)
    for marker in module_contract_markers(role, variant, height):
        objects.append(tag_object(marker, "four_elevation_material_contract", cfg, role=role))
    return objects, height


def module_payload(
    role: str,
    variant: str,
    filename: str,
    objects: list[bpy.types.Object],
    size_bytes: int,
    skin: dict,
    cfg: dict,
    *,
    texture_lod: str,
) -> dict:
    width, depth, height = bounds_dimensions(objects)
    repeatable = role == "floor"
    return {
        "role": role,
        "variant_key": variant,
        "assembly_class": "repeatable_middle" if repeatable else "fixed_semantic",
        "fixed_semantic": not repeatable,
        "lod": 0,
        "allowed_levels": [0, 1, 2],
        "filename": filename,
        "module_family": cfg["family"],
        "width_m": width,
        "depth_m": depth,
        "height_m": height,
        "floor_height_m": cfg["floor_height"],
        "repeatable_z": repeatable,
        "allow_inset_footprint": True,
        "triangle_count": evaluated_triangle_count(objects),
        "material_count": material_count(objects),
        "texture_keys": sorted(skin["zones"]),
        "texture_lod": texture_lod,
        "ao_baked": True,
        "size_bytes": size_bytes,
    }


def build_modules(
    folder: Path,
    mats: dict,
    skin: dict,
    cfg: dict,
    *,
    texture_lod: str,
) -> list[dict]:
    specs = (("podium", "default"), ("floor", "typical_a"), ("floor", "typical_b"), ("floor", "typical_c"), ("crown", "crown"), ("roof", "default"))
    payloads: list[dict] = []
    for role, variant in specs:
        objects, _height = build_module(role, variant, mats, cfg)
        normalize_bottom_centre(objects)
        suffix = role if variant == "default" else f"{role}_{variant}"
        filename = f"{cfg['family']}_{suffix}.glb"
        destination = folder / filename
        export_glb(destination, objects)
        payloads.append(
            module_payload(
                role,
                variant,
                filename,
                objects,
                destination.stat().st_size,
                skin,
                cfg,
                texture_lod=texture_lod,
            )
        )
        delete_objects(objects)
    return payloads


def footprint_contract(cfg: dict) -> dict:
    width, depth, _height = cfg["native"]
    shape = cfg["shape"]
    tower = "deco" in shape
    bay_count = 7 if tower else 8 if "office" in shape or "pavilion" in shape else 6
    bay = round(width / bay_count, 2)
    floors = [cfg["min_floors"], cfg["max_floors"]]
    rectangle = {
        "recommendedWidth_m": [round(width * 0.66, 1), round(width * 1.80, 1)],
        "recommendedDepth_m": [round(depth * 0.66, 1), round(depth * 1.58, 1)],
        "recommendedFloors": floors,
        "scaleMin": 0.62,
        "scaleMax": 1.40,
        "maxAxisRatio": 1.30,
        "preferredBayMultiple_m": bay,
    }
    profiles = {"rectangle": rectangle}
    preferred = ["rectangle"]
    if not tower:
        profiles["l_shape"] = {
            "recommendedWidth_m": [round(width * 0.72, 1), round(width * 2.05, 1)],
            "recommendedDepth_m": [round(depth * 0.70, 1), round(depth * 1.80, 1)],
            "recommendedFloors": floors,
            "scaleMin": 0.62,
            "scaleMax": 1.40,
            "maxAxisRatio": 1.32,
            "preferredBayMultiple_m": bay,
            "wingDepth_m": [round(depth * 0.28, 1), round(depth * 0.65, 1)],
        }
        preferred.append("l_shape")
    return {
        "preferredProfiles": preferred,
        "minimumPreferredProfiles": len(preferred),
        "profileRationale": (
            "The complete reference landmark tolerates independent-axis drawing error from 0.62x to 1.40x. "
            f"Larger targets repeat whole {bay:.2f} m construction bays along the long axis, preserving physical "
            "glass, occupied depth, frames, screens, structure and floor datums; entrances, corners, crowns and roofs remain fixed."
        ),
        "fixedLandmarkScaleBand": {"scaleMin": 0.62, "scaleMax": 1.40, "maxAxisRatio": 1.30},
        **rectangle,
        "profiles": profiles,
    }


def massing_graph(cfg: dict) -> dict:
    features = {
        "black_chrome_deco": ["three_streamlined_setback_stages", "continuous_chrome_fins", "carved_public_entrance", "fluted_chrome_crown"],
        "polychrome_deco": ["three_polychrome_setback_stages", "carved_two_storey_arched_portal", "continuous_mosaic_belts", "green_pyramidal_crown"],
        "wood_stone_pavilion": ["interlocking_native_stone_hearths", "two_occupied_glass_and_cedar_bars", "layered_cantilevered_terraces", "continuous_shallow_hip_roof"],
        "white_concrete_pavilion": ["free_standing_pilotis", "recessed_glass_enclosure", "real_open_dense_brise_soleil", "planted_rooftop_garden_room", "wafer_thin_flat_canopy"],
        "modern_machiya": ["carved_ground_passage", "visible_tsuboniwa", "full_height_wrapped_real_gap_koshi_screen", "shallow_dark_hip", "screened_rooftop_garden"],
        "cafe_machiya": ["vermilion_post_and_beam_frame", "open_cafe_room", "side_passage_to_garden", "real_koshi_and_bamboo_blinds", "individual_kawara_rows"],
        "dark_frame_office": ["complete_external_steel_grid", "clear_occupied_glazing", "visible_floor_plates", "carved_double_height_corner_lobby", "transparent_rooftop_pavilion"],
        "timber_hybrid_office": ["two_offset_mass_timber_bars", "complete_glulam_frame", "visible_clt_slabs", "biophilic_occupied_depth", "sawtooth_clerestory_roofs"],
        "streamline_theater": ["deep_auditorium", "paired_rounded_front_corners", "curved_and_flat_glass_block_fields", "sweeping_neon_bands", "integral_fin_and_marquee"],
        "egyptian_theater": ["deep_auditorium", "paired_battered_pylons", "four_lotus_columns", "deep_entry_court", "winged_sun_scarab_frieze", "integral_marquee"],
    }[cfg["shape"]]
    return {
        "type": f"fixed_{cfg['shape']}_with_repeatable_complete_middle_bays",
        "variant_id": cfg["variant_id"],
        "occupied_storeys": cfg["native_floors"],
        "features": features,
        "physical_window_layers": ["occupied_depth", "physical_pane", "separate_frame", "structural_or_screen_layer", "floor_datum", "material_return"],
        "fallback_policy": "fixed identity ends plus repeatable complete middle construction bays",
    }


def facade_sheet_contract(skin: dict, cfg: dict) -> dict:
    family = cfg["family"]
    contract = facade_contract(family, skin, f"/families/{family}/textures/source/archetype-goalpost.png")
    contract["geometry_detail_profile"] = "hero"
    contract["variant_id"] = cfg["variant_id"]
    contract["bay_strategy"] = {
        "fixed_end_bays": ["integral_public_entrance", "complete_corner_returns", "variant_specific_roof_or_crown", "variant_specific_ornament"],
        "repeatable_middle_bays": list(range(8)),
        "middle_variants": ["typical_a", "typical_b", "typical_c"],
        "rule": "Repeat a complete semantic bay containing physical glass, occupied depth, frame, structure or screen, wall return and floor datum; never stretch an individual pane or ornament.",
    }
    contract["assembly_contract"] = {
        "fixed": ["podium/entrance", "corner returns", "crown", "roof", *massing_graph(cfg)["features"]],
        "repeatable": ["typical_a", "typical_b", "typical_c"],
        "side_elevations": "complete wrapped left and right construction with reference-related but independently scheduled secondary openings",
        "elevation_coverage": {"front": "complete reference-locked public elevation", "left": "complete wrapped secondary construction", "right": "complete wrapped secondary construction", "rear": "complete occupied service elevation", "roof": "complete variant-specific roof, terraces, courts and crowns"},
        "variation_policy": "Use the fixed landmark throughout the 0.62–1.40 independent-axis band; oversized targets streetwall-repeat complete long-axis construction bays rather than returning family_incompatible.",
    }
    return contract


def quality_standard_evidence(cfg: dict, graph: dict) -> dict:
    """Declare machine-checkable review evidence without self-approving it.

    Geometry and locked renders can be generated deterministically.  The two
    approval booleans deliberately remain false until a human has inspected the
    comparison sheet; quality_memory.py therefore routes a fresh build to
    review instead of silently promoting it.
    """
    family = cfg["family"]
    return {
        "standard_id": "haussmann-depth-shape-skin-scale@1",
        "distinctive_shape_features": list(graph["features"]),
        "physical_depth_features": list(graph["physical_window_layers"]),
        "photoreal_skin_approved": False,
        "fixed_identity_anchors": [
            "podium/entrance",
            "corner returns",
            "crown",
            "roof",
        ],
        "repeatable_middle_roles": [
            "floor/typical_a",
            "floor/typical_b",
            "floor/typical_c",
        ],
        "comparison_views": [
            "street",
            "context",
            "front_elevation",
            "front_corner_oblique",
            "rear_corner_oblique",
            "aerial",
            "facade_close",
        ],
        "comparison_sheet": f"{family}_comparison.jpg",
        "human_visual_approval": False,
    }


def configure_render(cfg: dict) -> list[bpy.types.Object]:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.12
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.64, 0.70, 0.74, 1.0)
    background.inputs["Strength"].default_value = 0.74
    presentation: list[bpy.types.Object] = []
    ground = material("MAT_W14_PresentationGround", (0.40, 0.405, 0.40, 1.0), 0.92)
    add_box(presentation, "PRESENTATION_W14_Ground", (300.0, 300.0, 0.10), (0.0, 0.0, -0.10), ground, cfg, "presentation_only_ground")
    bpy.ops.object.light_add(type="SUN", location=(-80.0, -110.0, 150.0), rotation=(math.radians(28), math.radians(-16), math.radians(-38)))
    sun = bpy.context.object
    sun.name = "PRESENTATION_W14_Sun"
    sun.data.color = (1.0, 0.91, 0.80)
    sun.data.energy = 1.65
    sun.data.angle = math.radians(8.0)
    presentation.append(sun)
    target_z = cfg["native"][2] * 0.42
    scale = max(cfg["native"])
    for name, location, energy, size, color in (
        ("Key", (-scale * 0.85, -scale * 0.95, scale * 0.90), 5200, max(18.0, scale * 0.18), (1.0, 0.85, 0.72)),
        ("Fill", (scale * 0.90, -scale * 0.25, scale * 0.62), 3300, max(17.0, scale * 0.16), (0.72, 0.84, 1.0)),
        ("Rim", (-scale * 0.10, scale * 0.82, scale * 0.72), 4100, max(16.0, scale * 0.15), (0.80, 0.91, 1.0)),
    ):
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.name = f"PRESENTATION_W14_{name}"
        light.data.energy = energy
        light.data.shape = "DISK"
        light.data.size = size
        light.data.color = color
        light.rotation_euler = (Vector((0.0, 0.0, target_z)) - light.location).to_track_quat("-Z", "Y").to_euler()
        presentation.append(light)
    return presentation


def view_map(cfg: dict) -> dict[str, tuple[tuple[float, float, float], tuple[float, float, float], float]]:
    width, depth, height = cfg["native"]
    front_distance = max(height * 2.45, width * 1.95, depth * 2.1)
    oblique_distance = max(height * 2.15, width * 1.75, depth * 1.90)
    target = (0.0, 0.0, height * 0.42)
    return {
        "preview": ((oblique_distance * 0.65, -oblique_distance, height * 0.66), target, 52),
        "street": ((oblique_distance * 0.47, -oblique_distance * 0.86, height * 0.39), (0.0, -depth * 0.08, height * 0.36), 55),
        "context": ((oblique_distance * 0.92, -oblique_distance * 1.30, height * 0.78), target, 50),
        "front_corner_oblique": ((oblique_distance * 0.68, -oblique_distance, height * 0.52), target, 55),
        "front_elevation": ((0.0, -front_distance, height * 0.46), target, 58),
        "rear_corner_oblique": ((-oblique_distance * 0.70, oblique_distance, height * 0.58), target, 54),
        "aerial": ((oblique_distance * 0.70, -oblique_distance * 0.68, height * 1.28), (0.0, 0.0, height * 0.34), 52),
        "facade_close": ((width * 0.46, -max(depth * 1.15, width * 0.82), height * 0.23), (0.0, -depth * 0.40, height * 0.23), 66),
    }


def render_views(folder: Path, cfg: dict, *, view_set: str) -> list[str]:
    presentation = configure_render(cfg)
    views = view_map(cfg)
    if view_set == "preview":
        roles = ["preview"]
    elif view_set == "pilot":
        roles = ["preview", "front_elevation", "front_corner_oblique", "aerial", "facade_close"]
    elif view_set == "assessment":
        roles = ["street", "context"]
    elif view_set == "all":
        roles = list(views)
    else:
        roles = [view_set]
    rendered: list[str] = []
    for role in roles:
        location, target, lens = views[role]
        aim_camera(location, target, lens)
        filename = f"{cfg['family']}_{role}.png"
        bpy.context.scene.render.filepath = str(folder / filename)
        bpy.ops.render.render(write_still=True)
        rendered.append(filename)
    delete_objects(presentation)
    return rendered


def promote_catalogue_variant(folder: Path, cfg: dict) -> None:
    preview = folder / f"{cfg['family']}_preview.png"
    if not preview.is_file():
        return
    catalogue = folder.parents[1] / "archetypes" / "buildings" / cfg["catalogue_slug"]
    catalogue.mkdir(parents=True, exist_ok=True)
    # Sibling families own only their exact variant card.  The parent hero is
    # left with the canonical parent family so ten variants cannot overwrite it.
    shutil.copy2(preview, catalogue / f"variant_{cfg['catalogue_variant_index']}.png")


def build_family(
    output_root: Path,
    cfg: dict,
    *,
    view_set: str,
    skip_renders: bool,
    skip_modules: bool,
    skip_assembled_export: bool,
) -> None:
    clear_scene()
    family = cfg["family"]
    folder = (output_root / family).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    mats, skin = load_palette(folder, cfg)
    objects = build_assembled(mats, cfg)
    add_adaptive_delivery_bevels(objects, cfg)
    normalize_bottom_centre(objects)
    actual_native = bounds_dimensions(objects)
    assembled_path = folder / f"{family}_assembled.glb"
    manifest_path = folder / f"{family}_manifest.json"
    previous = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}
    if not skip_assembled_export:
        export_glb(assembled_path, objects)
        assembled_triangles = evaluated_triangle_count(objects)
        assembled_materials = material_count(objects)
    else:
        assembled_triangles = int((previous.get("assembled") or {}).get("triangle_count") or evaluated_triangle_count(objects))
        assembled_materials = int((previous.get("assembled") or {}).get("material_count") or material_count(objects))
    renders = list(previous.get("renders") or []) if skip_renders else render_views(folder, cfg, view_set=view_set)
    delete_objects(objects)
    if skip_modules:
        modules = list(previous.get("modules") or [])
    else:
        module_mats, module_skin = load_palette(folder, cfg, texture_lod="far")
        modules = build_modules(
            folder,
            module_mats,
            module_skin,
            cfg,
            texture_lod="far",
        )
    footprint = footprint_contract(cfg)
    graph = massing_graph(cfg)
    width, depth, height = actual_native
    assembled = {
        "filename": assembled_path.name,
        "module_family": family,
        "assembly_class": "fixed_landmark",
        "fixed_semantic": True,
        "repeatable_z": False,
        "source_variant_id": cfg["variant_id"],
        "generation_archetype_id": cfg["variant_id"],
        "width_m": width,
        "depth_m": depth,
        "floors": cfg["native_floors"],
        "uses_setback": "deco" in cfg["shape"],
        "uses_crown": True,
        "height_m": height,
        "triangle_count": assembled_triangles,
        "material_count": assembled_materials,
        "stack": [{"role": "assembled", "variant_key": "reference_locked", "level": 0, "z_m": 0.0, "height_m": height}],
        "footprint_profile": "rectangle",
        "footprint_target": {"width_m": width, "depth_m": depth, "segments": [{"id": "complete_fixed_landmark", "centre_x_m": 0.0, "centre_y_m": 0.0, "length_m": width, "thickness_m": depth, "rotation_degrees": 0.0}]},
        "massing_graph": graph,
        "texture_keys": sorted(skin["zones"]),
        "ao_baked": True,
        "edge_treatment": {
            "method": "adaptive_physical_delivery_bevel",
            "segments": cfg.get("_delivery_edge_bevel_segments", 0),
            "minimum_assembled_triangles": 12000,
        },
    }
    aliases = cfg["aliases"]
    manifest = {
        "manifest_schema": 3,
        "grammar_schema_version": 3,
        "generator": {"name": "archetype_compiler/generate_wave14_variant_families.py", "version": "1.0.0", "blender_version": bpy.app.version_string, "render_engine": "BLENDER_EEVEE"},
        "created_at": datetime.now(timezone.utc).isoformat(),
        "family": family,
        "archetype_id": cfg["archetype_id"],
        "archetype_label": cfg["label"],
        "variant_id": cfg["variant_id"],
        "generation_archetype_id": cfg["variant_id"],
        "archetype_aliases": aliases,
        "aesthetic_category_id": cfg["aesthetic"],
        "development_type": cfg["development_type"],
        "reuse_keys": [*aliases, *cfg["reuse_keys"]],
        "generation_tags": ["wave14", "catalogue_sibling_variant", "fixed_landmark_and_modular_fallback", "custom_pbr_skin", "physical_separate_glazing", "occupied_interior_depth", "complete_semantic_bay_repeat", *graph["features"]],
        "footprint_compatibility": footprint,
        "coordinate_contract": COORDINATE_CONTRACT,
        "textures": texture_inventory(skin),
        "facade_sheet": facade_sheet_contract(skin, cfg),
        "massing_graph": graph,
        "quality_standard_evidence": quality_standard_evidence(cfg, graph),
        "material_budget": {"max_assembled_materials": 18, "rationale": "Variant-specific opaque construction, physical glazing, occupied depth, expressed structure, screens, ornament and roof finishes remain separate because their optical contrast carries the catalogue identity."},
        "dimensions": {"width_m": width, "depth_m": depth, "podium_height_m": cfg["podium_height"], "floor_height_m": cfg["floor_height"], "setback_height_m": cfg["floor_height"], "roof_height_m": cfg["roof_height"], "crown_height_m": cfg["crown_height"], "default_floors": cfg["native_floors"], "min_floors": cfg["min_floors"], "max_floors": cfg["max_floors"]},
        "native_width_m": width,
        "native_depth_m": depth,
        "native_height_m": height,
        "native_floors": cfg["native_floors"],
        "min_floors": cfg["min_floors"],
        "max_floors": cfg["max_floors"],
        "default_floors": cfg["native_floors"],
        "modules": modules,
        "assembled": assembled,
        "thumbnail": f"{family}_preview.png",
        "renders": renders,
        "architectural_identity": cfg["identity"],
        "material_zones": cfg["material_zones"],
        "glass_profile": cfg["glass_profile"],
        "source_provenance": {"catalogue_archetype_id": cfg["archetype_id"], "catalogue_variant_id": cfg["variant_id"], "catalogue_alias_ids": aliases[2:], "elevation_source": f"/families/{family}/elevation.jpg", "goalpost": f"/families/{family}/textures/source/archetype-goalpost.png", "reference_generation": f"/families/{family}/textures/source/reference-generation.json", "method": "variant-locked four-view source board, six-zone construction plate, deterministic true-metric parts, physical layered glazing, occupied depth, complete secondary elevations, fixed whole-building landmark and semantic LEGO fallback modules"},
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    grammar = {
        "family_id": family,
        "source": {"archetype_id": cfg["archetype_id"], "variant_id": cfg["variant_id"], "generation_archetype_id": cfg["variant_id"], "reuse_keys": manifest["reuse_keys"]},
        "dimensions": manifest["dimensions"],
        "architectural_signature": {"identity": cfg["identity"], "material_zones": cfg["material_zones"], "glass_profile": cfg["glass_profile"], "kits": ["reference_locked_fixed_landmark", "physical_layered_glazing", "occupied_interior_depth", "semantic_repeatable_middle_bays", "fixed_variant_roof_and_identity_kit", *graph["features"]]},
        "archetype_aliases": aliases,
        "footprint_compatibility": footprint,
        "massing_graph": graph,
    }
    (folder / "grammar.json").write_text(json.dumps(grammar, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (folder / "archetype-source.json").write_text(json.dumps(manifest["source_provenance"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    promote_catalogue_variant(folder, cfg)
    print(f"[wave14] {family}: {assembled_triangles} triangles, {assembled_materials} materials, {len(modules)} modules, {len(renders)} renders, native={actual_native}", flush=True)


def render_existing(output_root: Path, cfg: dict, *, view_set: str) -> None:
    clear_scene()
    folder = (output_root / cfg["family"]).resolve()
    mats, _skin = load_palette(folder, cfg)
    objects = build_assembled(mats, cfg)
    add_adaptive_delivery_bevels(objects, cfg)
    normalize_bottom_centre(objects)
    rendered = render_views(folder, cfg, view_set=view_set)
    delete_objects(objects)
    manifest_path = folder / f"{cfg['family']}_manifest.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["renders"] = list(dict.fromkeys([*(manifest.get("renders") or []), *rendered]))
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    promote_catalogue_variant(folder, cfg)
    print(f"[wave14] {cfg['family']}: rendered {len(rendered)} views", flush=True)


def main() -> int:
    args = parse_args()
    cfg = with_family(args.family)
    if args.render_existing:
        render_existing(args.output_root, cfg, view_set=args.view_set)
    else:
        build_family(args.output_root, cfg, view_set=args.view_set, skip_renders=args.skip_renders, skip_modules=args.skip_modules, skip_assembled_export=args.skip_assembled_export)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
