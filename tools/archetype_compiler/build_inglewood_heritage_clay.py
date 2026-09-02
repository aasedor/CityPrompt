"""Build the first clay-first RLASM v6.1 catalogue candidate.

The model is authored directly as semantic architectural clay from the exact
Inglewood Victorian Brick catalogue triplet.  It deliberately stops before
source-specific PBR/texture work, while retaining the RLASM source lock,
measured massing, complete envelope, openings, roof, contacts, and QA views.

Run with Blender 5.2 in background mode::

    blender --background --python build_inglewood_heritage_clay.py -- \
      --output-dir <external-artifact-directory>

The authoring Blend remains modular by bay.  The exported GLB is joined by
semantic role, reducing the runtime asset to at most eight mesh nodes without
stretching identity-bearing geometry.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import bpy
from mathutils import Vector


CANDIDATE = "inglewood-victorian-brick-commercial-semantic-clay-v001"
METHOD = "RLASM v6.1 clay-first"
WIDTH = 20.4
DEPTH = 24.0
PARAPET_HEIGHT = 10.35
GABLE_HEIGHT = 13.25

SOURCE_LOCK = (
    {
        "view": "front",
        "repo_path": "frontend/public/archetypes/buildings/inglewood-heritage-brick-commercial/variant_0.png",
        "sha256": "e5122ce4dc9277ade776a994de8cf6eb173a3458657e3d2c5c45f3edab4287ab",
        "bytes": 1_446_464,
    },
    {
        "view": "oblique_aerial",
        "repo_path": "frontend/public/archetypes/buildings/inglewood-heritage-brick-commercial/variant_0_angle_60.jpg",
        "sha256": "26d1413d8434fcdbcdfaab8dc151cd346daab3fda486738b04fa067eca7747b9",
        "bytes": 943_353,
    },
    {
        "view": "near_true_top",
        "repo_path": "frontend/public/archetypes/buildings/inglewood-heritage-brick-commercial/variant_0_angle_90.jpg",
        "sha256": "67b91bf68860537f9fb0f2022e506f025fc9ed5ceaada2e30a04ae468ed2fa7e",
        "bytes": 812_731,
    },
)


SEMANTIC_PALETTE: dict[str, tuple[tuple[float, float, float, float], float, float]] = {
    "masonry": ((0.50, 0.19, 0.105, 1.0), 0.86, 0.0),
    "wall": ((0.67, 0.54, 0.39, 1.0), 0.88, 0.0),
    "trim": ((0.82, 0.69, 0.47, 1.0), 0.82, 0.0),
    "roof": ((0.16, 0.18, 0.19, 1.0), 0.93, 0.0),
    "glass": ((0.075, 0.18, 0.22, 1.0), 0.28, 0.0),
    "timber": ((0.27, 0.12, 0.055, 1.0), 0.77, 0.0),
    "interior": ((0.62, 0.33, 0.12, 1.0), 0.78, 0.0),
    "hardware": ((0.055, 0.06, 0.065, 1.0), 0.48, 0.15),
}


@dataclass(frozen=True)
class CameraSpec:
    name: str
    location: tuple[float, float, float]
    target: tuple[float, float, float]
    lens: float = 54.0
    ortho_scale: float | None = None


# Authored before geometry, per the RLASM camera-first rule.
CAMERA_SPECS = (
    CameraSpec("front", (0.0, -45.0, 7.4), (0.0, -2.0, 6.1), 58.0),
    CameraSpec("front_corner", (29.0, -35.0, 15.5), (0.0, 0.0, 5.7), 54.0),
    CameraSpec("aerial", (31.0, -33.0, 28.0), (0.0, 0.0, 4.8), 56.0),
    CameraSpec("left", (-31.0, -28.0, 12.5), (0.0, 0.0, 5.4), 56.0),
    CameraSpec("right", (31.0, -28.0, 12.5), (0.0, 0.0, 5.4), 56.0),
    CameraSpec("rear", (0.0, 46.0, 8.4), (0.0, 0.0, 5.2), 58.0),
    CameraSpec("rear_corner", (29.0, 35.0, 15.0), (0.0, 0.0, 5.2), 54.0),
    CameraSpec("true_top", (0.0, 0.0, 52.0), (0.0, 0.0, 0.0), 58.0, 31.0),
    CameraSpec("entrance_close", (0.0, -30.0, 6.4), (0.0, -10.8, 5.3), 58.0),
    CameraSpec("facade_close", (8.5, -24.0, 7.0), (6.6, -11.3, 6.1), 65.0),
    CameraSpec("roof_close", (23.0, -22.0, 23.0), (0.0, 0.0, 9.3), 60.0),
)


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--resolution", type=int, default=1280)
    return parser.parse_args(argv)


def flat_material(role: str) -> bpy.types.Material:
    color, roughness, metallic = SEMANTIC_PALETTE[role]
    material = bpy.data.materials.new(f"CP_SEMANTIC_CLAY_{role.upper()}")
    material.use_nodes = True
    material.diffuse_color = color
    nodes = material.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    if role == "glass":
        shader.inputs["Coat Weight"].default_value = 0.32
        shader.inputs["Coat Roughness"].default_value = 0.16
    material.node_tree.links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    material["cityprompt_semantic_role"] = role
    return material


def tag_building(obj: bpy.types.Object, role: str, module: str) -> bpy.types.Object:
    obj["rlasm_building_object"] = True
    obj["rlasm_method"] = METHOD
    obj["cityprompt_material_mode"] = "semantic_architectural_clay"
    obj["cityprompt_semantic_role"] = role
    obj["cityprompt_lego_module"] = module
    return obj


def apply_bevel(obj: bpy.types.Object, width: float, segments: int = 2) -> None:
    if width <= 0:
        return
    modifier = obj.modifiers.new("RLASM edge softness", "BEVEL")
    modifier.width = width
    modifier.segments = segments
    modifier.limit_method = "ANGLE"
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)


def add_box(
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    role: str,
    materials: dict[str, bpy.types.Material],
    module: str,
    bevel: float = 0.025,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = (scale[0] / 2.0, scale[1] / 2.0, scale[2] / 2.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(materials[role])
    tag_building(obj, role, module)
    apply_bevel(obj, bevel)
    return obj


def extruded_prism_xz(
    name: str,
    polygon: Iterable[tuple[float, float]],
    y_center: float,
    depth: float,
    role: str,
    materials: dict[str, bpy.types.Material],
    module: str,
    bevel: float = 0.0,
) -> bpy.types.Object:
    points = list(polygon)
    y0, y1 = y_center - depth / 2.0, y_center + depth / 2.0
    vertices = [(x, y0, z) for x, z in points] + [(x, y1, z) for x, z in points]
    count = len(points)
    faces = [tuple(range(count)), tuple(range(count, count * 2))]
    for index in range(count):
        nxt = (index + 1) % count
        faces.append((index, nxt, count + nxt, count + index))
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(materials[role])
    tag_building(obj, role, module)
    apply_bevel(obj, bevel)
    return obj


def extruded_prism_yz(
    name: str,
    polygon: Iterable[tuple[float, float]],
    x_center: float,
    depth: float,
    role: str,
    materials: dict[str, bpy.types.Material],
    module: str,
    bevel: float = 0.0,
) -> bpy.types.Object:
    points = list(polygon)
    x0, x1 = x_center - depth / 2.0, x_center + depth / 2.0
    vertices = [(x0, y, z) for y, z in points] + [(x1, y, z) for y, z in points]
    count = len(points)
    faces = [tuple(range(count)), tuple(range(count, count * 2))]
    for index in range(count):
        nxt = (index + 1) % count
        faces.append((index, nxt, count + nxt, count + index))
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(materials[role])
    tag_building(obj, role, module)
    apply_bevel(obj, bevel)
    return obj


def arch_polygon(cx: float, bottom: float, spring: float, radius: float, segments: int = 24) -> list[tuple[float, float]]:
    points = [(cx - radius, bottom), (cx + radius, bottom), (cx + radius, spring)]
    for index in range(segments + 1):
        angle = math.pi * index / segments
        points.append((cx + radius * math.cos(angle), spring + radius * math.sin(angle)))
    return points


def arch_ring_polygon(cx: float, spring: float, inner: float, width: float, segments: int = 28) -> list[tuple[float, float]]:
    outer = inner + width
    points = []
    for index in range(segments + 1):
        angle = math.pi * index / segments
        points.append((cx + outer * math.cos(angle), spring + outer * math.sin(angle)))
    for index in range(segments, -1, -1):
        angle = math.pi * index / segments
        points.append((cx + inner * math.cos(angle), spring + inner * math.sin(angle)))
    return points


def add_front_arch_window(
    prefix: str,
    cx: float,
    bottom: float,
    spring: float,
    radius: float,
    materials: dict[str, bpy.types.Material],
    module: str,
    mullions: int = 1,
) -> None:
    glass_y = -11.89
    outer_y = -12.035
    extruded_prism_xz(
        prefix + "_Glass",
        arch_polygon(cx, bottom, spring, radius),
        glass_y,
        0.055,
        "glass",
        materials,
        module,
    )
    ring = 0.18
    extruded_prism_xz(
        prefix + "_ArchTrim",
        arch_ring_polygon(cx, spring, radius, ring),
        outer_y,
        0.16,
        "trim",
        materials,
        module,
        0.012,
    )
    for side in (-1.0, 1.0):
        add_box(
            prefix + ("_LeftJamb" if side < 0 else "_RightJamb"),
            (cx + side * (radius + ring / 2.0), outer_y, (bottom + spring) / 2.0),
            (ring, 0.16, spring - bottom),
            "trim",
            materials,
            module,
            0.012,
        )
    add_box(prefix + "_Sill", (cx, outer_y, bottom), (radius * 2.0 + 0.5, 0.2, 0.18), "trim", materials, module, 0.016)
    add_box(prefix + "_MeetingRail", (cx, outer_y - 0.04, bottom + (spring - bottom) * 0.43), (radius * 1.9, 0.105, 0.11), "timber", materials, module, 0.008)
    if mullions > 0:
        for index in range(1, mullions + 1):
            offset = radius * (index / (mullions + 1) - 0.5) * 1.25
            add_box(prefix + f"_Mullion{index}", (cx + offset, outer_y - 0.04, bottom + (spring - bottom) / 2.0), (0.10, 0.105, spring - bottom), "timber", materials, module, 0.008)


def add_side_arch_window(
    prefix: str,
    side: float,
    cy: float,
    bottom: float,
    spring: float,
    radius: float,
    materials: dict[str, bpy.types.Material],
    module: str,
) -> None:
    glass_x = side * 9.92
    outer_x = side * 10.065
    extruded_prism_yz(prefix + "_Glass", arch_polygon(cy, bottom, spring, radius), glass_x, 0.055, "glass", materials, module)
    ring = 0.17
    extruded_prism_yz(prefix + "_ArchTrim", arch_ring_polygon(cy, spring, radius, ring), outer_x, 0.16, "trim", materials, module, 0.012)
    for direction in (-1.0, 1.0):
        add_box(
            prefix + ("_NearJamb" if direction < 0 else "_FarJamb"),
            (outer_x, cy + direction * (radius + ring / 2.0), (bottom + spring) / 2.0),
            (0.16, ring, spring - bottom),
            "trim",
            materials,
            module,
            0.012,
        )
    add_box(prefix + "_Sill", (outer_x, cy, bottom), (0.2, radius * 2.0 + 0.45, 0.18), "trim", materials, module, 0.016)
    add_box(prefix + "_MeetingRail", (outer_x - side * 0.04, cy, bottom + (spring - bottom) * 0.43), (0.105, radius * 1.9, 0.11), "timber", materials, module, 0.008)


def add_storefront(
    prefix: str,
    cx: float,
    width: float,
    materials: dict[str, bpy.types.Material],
    module: str,
) -> None:
    glass_y = -11.89
    outer_y = -12.07
    bottom, top = 0.72, 3.92
    add_box(prefix + "_Glass", (cx, glass_y, (bottom + top) / 2.0), (width, 0.06, top - bottom), "glass", materials, module, 0.006)
    add_box(prefix + "_Sill", (cx, outer_y, bottom), (width + 0.18, 0.18, 0.18), "timber", materials, module, 0.012)
    add_box(prefix + "_Head", (cx, outer_y, top), (width + 0.18, 0.18, 0.20), "timber", materials, module, 0.012)
    for x in (cx - width / 2.0, cx, cx + width / 2.0):
        add_box(prefix + f"_Frame_{x:+.2f}", (x, outer_y, (bottom + top) / 2.0), (0.12, 0.18, top - bottom), "timber", materials, module, 0.008)
    transom_z = 3.18
    add_box(prefix + "_Transom", (cx, outer_y, transom_z), (width, 0.16, 0.13), "timber", materials, module, 0.008)
    for index in range(1, 4):
        x = cx - width / 2.0 + width * index / 4.0
        add_box(prefix + f"_TransomMullion{index}", (x, outer_y, (transom_z + top) / 2.0), (0.075, 0.16, top - transom_z), "timber", materials, module, 0.006)


def add_front_field_panels(materials: dict[str, bpy.types.Material]) -> None:
    front_y = -11.835
    # Wing panels leave genuinely recessed storefront and upper-window fields.
    for side, label in ((-1.0, "Left"), (1.0, "Right")):
        centre_x = side * 6.65
        add_box(f"Front{label}_GroundSpandrel", (centre_x, front_y, 4.38), (7.0, 0.36, 0.78), "masonry", materials, "fixed_front_wing", 0.02)
        add_box(f"Front{label}_UpperSpandrel", (centre_x, front_y, 8.85), (7.0, 0.36, 1.45), "masonry", materials, "fixed_front_wing", 0.02)
        add_box(f"Front{label}_Base", (centre_x, front_y, 0.35), (7.0, 0.38, 0.70), "trim", materials, "fixed_front_wing", 0.024)
        # Outer and inter-bay masonry piers.
        for index, x in enumerate((centre_x - 3.45, centre_x - 1.15, centre_x + 1.15, centre_x + 3.45)):
            add_box(f"Front{label}_Pier{index}", (x, front_y, 4.7), (0.48, 0.38, 8.7), "masonry", materials, "repeatable_front_bay", 0.025)
        for index, x in enumerate((centre_x - 2.3, centre_x, centre_x + 2.3)):
            add_storefront(f"Front{label}_Shop{index}", x, 2.0, materials, "repeatable_storefront_bay")
            add_front_arch_window(f"Front{label}_Upper{index}", x, 5.14, 7.35, 0.72, materials, "repeatable_upper_bay")


def add_central_entry(materials: dict[str, bpy.types.Material]) -> None:
    front_y = -11.90
    # Monumental opening and warm occupied depth.
    extruded_prism_xz("EntryArchGlass", arch_polygon(0.0, 0.55, 5.25, 2.25), -11.83, 0.08, "glass", materials, "fixed_entry")
    add_box("EntryInteriorGlow", (0.0, -11.72, 3.7), (4.15, 0.08, 6.0), "interior", materials, "fixed_entry", 0.0)
    extruded_prism_xz("EntryOuterArch", arch_ring_polygon(0.0, 5.25, 2.25, 0.34), -12.10, 0.23, "trim", materials, "fixed_entry", 0.018)
    extruded_prism_xz("EntryInnerBrickArch", arch_ring_polygon(0.0, 5.25, 1.91, 0.28), -12.19, 0.16, "masonry", materials, "fixed_entry", 0.012)
    # The source's buff-brick central field remains distinct from the red wings.
    add_box("EntryUpperBuffField", (0.0, -11.86, 8.68), (5.25, 0.35, 2.02), "wall", materials, "fixed_entry", 0.018)
    for side in (-1.0, 1.0):
        x = side * 2.42
        add_box("EntryStonePier" + ("L" if side < 0 else "R"), (x, front_y, 3.35), (0.74, 0.66, 6.7), "trim", materials, "fixed_entry", 0.035)
        for band in range(5):
            add_box(f"EntryPierBand{side:+.0f}_{band}", (x, -12.26, 0.92 + band * 1.1), (0.82, 0.17, 0.17), "wall", materials, "fixed_entry", 0.01)
    # Double doors, fanlight division, and physical threshold.
    for side in (-1.0, 1.0):
        x = side * 0.82
        add_box("EntryDoor" + ("L" if side < 0 else "R"), (x, -12.13, 1.78), (1.56, 0.14, 2.58), "timber", materials, "fixed_entry", 0.025)
        add_box("EntryDoorGlass" + ("L" if side < 0 else "R"), (x, -12.22, 1.87), (1.18, 0.045, 1.78), "glass", materials, "fixed_entry", 0.006)
    add_box("EntryDoorHead", (0.0, -12.14, 3.18), (3.35, 0.16, 0.16), "timber", materials, "fixed_entry", 0.01)
    for x in (-1.64, 0.0, 1.64):
        add_box(f"EntryFanlightMullion{x:+.2f}", (x, -12.14, 4.25), (0.105, 0.16, 1.92), "timber", materials, "fixed_entry", 0.008)
    add_box("EntryThreshold", (0.0, -12.30, 0.28), (3.9, 0.9, 0.20), "trim", materials, "fixed_entry", 0.025)


def add_gable(materials: dict[str, bpy.types.Material]) -> None:
    polygon = [(-3.05, 9.72), (3.05, 9.72), (3.05, 10.15), (0.0, 13.25), (-3.05, 10.15)]
    extruded_prism_xz("CentralGableField", polygon, -11.85, 0.42, "masonry", materials, "fixed_gable", 0.018)
    # Stepped trim follows the two gable slopes as rotated rectangular beams.
    for side in (-1.0, 1.0):
        length = math.hypot(3.05, 3.1)
        bpy.ops.mesh.primitive_cube_add(location=(side * 1.52, -12.13, 11.68))
        beam = bpy.context.object
        beam.name = "GableSlopeTrim" + ("L" if side < 0 else "R")
        beam.scale = (length / 2.0, 0.15, 0.14)
        beam.rotation_euler.y = side * math.atan2(3.1, 3.05)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        beam.data.materials.append(materials["trim"])
        tag_building(beam, "trim", "fixed_gable")
        apply_bevel(beam, 0.025)
    add_box("GablePeakCap", (0.0, -12.12, 13.18), (0.52, 0.38, 0.28), "trim", materials, "fixed_gable", 0.025)
    # Three narrow arched attic lights.
    for index, x in enumerate((-0.82, 0.0, 0.82)):
        add_front_arch_window(f"GableAttic{index}", x, 10.05, 11.45, 0.31, materials, "fixed_gable", 0)
    # Rhythmic recessed dentils express the reference's Romanesque gable field.
    for index in range(9):
        x = -2.32 + index * 0.58
        roof_line = 12.82 - abs(x) * 0.78
        add_box(f"GableDentil{index}", (x, -12.15, roof_line - 0.30), (0.19, 0.13, 0.58), "trim", materials, "fixed_gable", 0.055)


def add_decorative_bands(materials: dict[str, bpy.types.Material]) -> None:
    for z, depth, role in ((4.70, 0.22, "trim"), (4.92, 0.18, "masonry"), (9.36, 0.22, "trim"), (9.62, 0.26, "masonry"), (10.03, 0.30, "trim")):
        for side, cx in ((-1.0, -6.65), (1.0, 6.65)):
            add_box(f"FrontBand{z:.2f}_{side:+.0f}", (cx, -12.08, z), (7.15, depth, 0.18 if z < 9.8 else 0.22), role, materials, "fixed_cornice", 0.015)
    # Checker band below upper windows.
    for side, start in ((-1.0, -9.85), (1.0, 3.45)):
        for index in range(12):
            x = start + index * 0.56
            z = 4.48 + (index % 2) * 0.18
            add_box(f"FrontChecker{side:+.0f}_{index}", (x, -12.18, z), (0.34, 0.15, 0.16), "trim" if index % 2 else "masonry", materials, "fixed_banding", 0.008)
    # Projecting dentils under the cornice.
    for side, start in ((-1.0, -9.82), (1.0, 3.5)):
        for index in range(14):
            x = start + index * 0.49
            add_box(f"FrontDentil{side:+.0f}_{index}", (x, -12.19, 9.20), (0.25, 0.22, 0.32), "trim", materials, "fixed_cornice", 0.012)


def add_side_facades(materials: dict[str, bpy.types.Material]) -> None:
    bay_centres = (-9.45, -5.75, -2.05, 1.65, 5.35, 9.05)
    for side in (-1.0, 1.0):
        label = "West" if side < 0 else "East"
        outer_x = side * 9.985
        add_box(f"{label}Base", (outer_x, 0.0, 0.35), (0.38, 23.75, 0.70), "trim", materials, "fixed_side", 0.025)
        add_box(f"{label}GroundSpandrel", (outer_x, 0.0, 4.40), (0.36, 23.75, 0.78), "masonry", materials, "fixed_side", 0.02)
        add_box(f"{label}UpperSpandrel", (outer_x, 0.0, 8.86), (0.36, 23.75, 1.45), "masonry", materials, "fixed_side", 0.02)
        for index, cy in enumerate((-11.7, -7.6, -3.9, -0.2, 3.5, 7.2, 11.65)):
            add_box(f"{label}Pier{index}", (outer_x, cy, 4.72), (0.38, 0.50, 8.75), "masonry", materials, "repeatable_side_bay", 0.025)
        for index, cy in enumerate(bay_centres):
            add_side_arch_window(f"{label}Ground{index}", side, cy, 0.85, 3.15, 0.70, materials, "repeatable_side_bay")
            add_side_arch_window(f"{label}Upper{index}", side, cy, 5.16, 7.36, 0.70, materials, "repeatable_side_bay")
        for z, role in ((4.74, "trim"), (9.35, "trim"), (9.64, "masonry"), (10.03, "trim")):
            add_box(f"{label}Band{z:.2f}", (side * 10.09, 0.0, z), (0.22, 24.0, 0.18 if z < 9.8 else 0.22), role, materials, "fixed_cornice", 0.014)
        for index, cy in enumerate([-10.9 + i * 0.82 for i in range(28)]):
            add_box(f"{label}Dentil{index}", (side * 10.18, cy, 9.19), (0.22, 0.38, 0.30), "trim", materials, "fixed_cornice", 0.012)


def add_rear_facade(materials: dict[str, bpy.types.Material]) -> None:
    rear_y = 11.84
    add_box("RearBase", (0.0, rear_y, 0.35), (20.1, 0.36, 0.70), "trim", materials, "fixed_rear", 0.024)
    add_box("RearGroundSpandrel", (0.0, rear_y, 4.38), (20.1, 0.36, 0.78), "masonry", materials, "fixed_rear", 0.02)
    add_box("RearUpperSpandrel", (0.0, rear_y, 8.86), (20.1, 0.36, 1.45), "masonry", materials, "fixed_rear", 0.02)
    for index, x in enumerate((-9.9, -6.6, -3.3, 0.0, 3.3, 6.6, 9.9)):
        add_box(f"RearPier{index}", (x, rear_y, 4.7), (0.46, 0.36, 8.7), "masonry", materials, "repeatable_rear_bay", 0.025)
    # Reuse front arch construction on a rotated collection of parts.
    for index, x in enumerate((-8.15, -4.95, -1.65, 1.65, 4.95, 8.15)):
        # Rear glass and trim are mirrored to +Y.
        extruded_prism_xz(f"RearUpper{index}_Glass", arch_polygon(x, 5.15, 7.34, 0.68), 11.89, 0.055, "glass", materials, "repeatable_rear_bay")
        extruded_prism_xz(f"RearUpper{index}_Arch", arch_ring_polygon(x, 7.34, 0.68, 0.17), 12.055, 0.16, "trim", materials, "repeatable_rear_bay", 0.012)
        for direction in (-1.0, 1.0):
            add_box(f"RearUpper{index}_Jamb{direction:+.0f}", (x + direction * 0.765, 12.055, 6.245), (0.17, 0.16, 2.19), "trim", materials, "repeatable_rear_bay", 0.012)
        add_box(f"RearUpper{index}_Sill", (x, 12.055, 5.15), (1.78, 0.2, 0.18), "trim", materials, "repeatable_rear_bay", 0.014)
    # Four service windows and a centred double service door.
    for index, x in enumerate((-8.1, -5.0, 5.0, 8.1)):
        add_box(f"RearServiceGlass{index}", (x, 11.89, 2.2), (2.2, 0.06, 2.55), "glass", materials, "repeatable_rear_bay", 0.006)
        for fx in (x - 1.16, x + 1.16):
            add_box(f"RearServiceJamb{index}_{fx:+.2f}", (fx, 12.055, 2.2), (0.18, 0.16, 2.7), "trim", materials, "repeatable_rear_bay", 0.012)
        add_box(f"RearServiceHead{index}", (x, 12.055, 3.55), (2.5, 0.16, 0.18), "trim", materials, "repeatable_rear_bay", 0.012)
    for side in (-1.0, 1.0):
        x = side * 1.05
        add_box("RearDoor" + ("L" if side < 0 else "R"), (x, 12.04, 1.6), (1.9, 0.16, 2.8), "timber", materials, "fixed_rear_entry", 0.025)
        add_box("RearDoorGlass" + ("L" if side < 0 else "R"), (x, 12.14, 1.78), (1.35, 0.045, 1.55), "glass", materials, "fixed_rear_entry", 0.006)
    add_box("RearDoorCanopy", (0.0, 12.48, 3.25), (5.2, 1.3, 0.18), "hardware", materials, "fixed_rear_entry", 0.035)
    for side in (-1.0, 1.0):
        add_box(f"RearCanopyBrace{side:+.0f}", (side * 2.1, 12.28, 2.65), (0.12, 0.12, 1.25), "hardware", materials, "fixed_rear_entry", 0.02)


def add_roof(materials: dict[str, bpy.types.Material]) -> None:
    add_box("FlatMembraneRoof", (0.0, 0.0, 9.75), (19.55, 23.25, 0.24), "roof", materials, "fixed_roof", 0.018)
    # Parapets form a complete closed roof graph.
    add_box("RearParapet", (0.0, 11.78, 10.05), (20.2, 0.45, 0.95), "masonry", materials, "fixed_roof", 0.025)
    for side in (-1.0, 1.0):
        add_box(f"SideParapet{side:+.0f}", (side * 10.0, 0.0, 10.05), (0.45, 23.6, 0.95), "masonry", materials, "fixed_roof", 0.025)
        add_box(f"SideCoping{side:+.0f}", (side * 10.0, 0.0, 10.55), (0.62, 23.7, 0.18), "trim", materials, "fixed_roof", 0.025)
    add_box("RearCoping", (0.0, 11.83, 10.55), (20.4, 0.62, 0.18), "trim", materials, "fixed_roof", 0.025)
    # Short gabled cap immediately behind the identity-bearing front gable.
    roof_polygon = [(-3.02, 9.72), (0.0, 12.82), (3.02, 9.72)]
    extruded_prism_xz("EntryGableRoof", roof_polygon, -9.65, 4.3, "roof", materials, "fixed_gable_roof", 0.035)
    # Discrete equipment inferred from the aerial source.
    for index, (x, y, sx, sy, sz) in enumerate(((-5.3, 4.2, 2.2, 2.6, 1.25), (4.9, 3.3, 1.8, 2.1, 1.0), (2.0, -1.6, 1.2, 1.5, 0.55))):
        add_box(f"RooftopUnit{index}", (x, y, 10.0 + sz / 2.0), (sx, sy, sz), "hardware", materials, "fixed_roof_equipment", 0.09)
        for slat in range(4):
            add_box(f"RooftopUnit{index}Slat{slat}", (x, y - sy / 2.0 - 0.055, 10.25 + slat * sz / 5.0), (sx * 0.68, 0.06, 0.045), "roof", materials, "fixed_roof_equipment", 0.008)
    add_box("RoofHatch", (-1.2, 5.5, 10.08), (1.6, 2.0, 0.45), "hardware", materials, "fixed_roof_equipment", 0.035)
    add_box("RoofVent", (5.2, -5.0, 10.5), (0.45, 0.45, 1.4), "hardware", materials, "fixed_roof_equipment", 0.04)


def build_building(materials: dict[str, bpy.types.Material]) -> None:
    # Inset structural volume lets all openings read as physical recesses.
    add_box("OccupiedCore", (0.0, 0.0, 4.85), (19.66, 23.30, 9.70), "masonry", materials, "fixed_envelope", 0.035)
    add_box("FoundationContact", (0.0, 0.0, 0.14), (20.25, 23.85, 0.28), "trim", materials, "fixed_contact", 0.02)
    add_front_field_panels(materials)
    add_central_entry(materials)
    add_gable(materials)
    add_decorative_bands(materials)
    add_side_facades(materials)
    add_rear_facade(materials)
    add_roof(materials)


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def setup_scene(resolution: int) -> tuple[dict[str, bpy.types.Material], dict[str, bpy.types.Object]]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene["rlasm_method"] = METHOD
    scene["rlasm_candidate"] = CANDIDATE
    scene["rlasm_source_mode"] = "exact_catalogue_triplet_only"
    scene["rlasm_source_hashes"] = json.dumps([item["sha256"] for item in SOURCE_LOCK])
    scene["cityprompt_asset_class"] = "semantic_architectural_clay"
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = resolution
    scene.render.resolution_y = round(resolution * 0.75)
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.image_settings.color_depth = "8"
    scene.view_settings.look = "AgX - Medium High Contrast"

    world = bpy.data.worlds.new("CityPrompt Clay QA World")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.055, 0.072, 0.085, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.68
    scene.world = world

    materials = {role: flat_material(role) for role in SEMANTIC_PALETTE}

    # Review context is marked and never enters the GLB.
    bpy.ops.mesh.primitive_plane_add(size=120.0, location=(0.0, 0.0, -0.015))
    ground = bpy.context.object
    ground.name = "QA_Ground_NotForExport"
    ground["rlasm_review_context"] = True
    ground.data.materials.append(materials["hardware"])

    # Camera roster is instantiated before geometry.
    cameras: dict[str, bpy.types.Object] = {}
    for spec in CAMERA_SPECS:
        bpy.ops.object.camera_add(location=spec.location)
        camera = bpy.context.object
        camera.name = "RLASM_QA_" + spec.name
        camera.data.lens = spec.lens
        if spec.ortho_scale is not None:
            camera.data.type = "ORTHO"
            camera.data.ortho_scale = spec.ortho_scale
        look_at(camera, Vector(spec.target))
        cameras[spec.name] = camera

    # Three-point daylight rig.
    bpy.ops.object.light_add(type="AREA", location=(-14.0, -24.0, 28.0))
    key = bpy.context.object
    key.name = "RLASM_QA_Key"
    key.data.energy = 1850
    key.data.shape = "DISK"
    key.data.size = 18.0
    look_at(key, Vector((0.0, 0.0, 5.0)))
    bpy.ops.object.light_add(type="AREA", location=(18.0, -20.0, 17.0))
    fill = bpy.context.object
    fill.name = "RLASM_QA_Fill"
    fill.data.energy = 900
    fill.data.size = 16.0
    look_at(fill, Vector((0.0, 0.0, 5.0)))
    bpy.ops.object.light_add(type="AREA", location=(-4.0, 20.0, 15.0))
    rim = bpy.context.object
    rim.name = "RLASM_QA_Rim"
    rim.data.energy = 1100
    rim.data.size = 13.0
    look_at(rim, Vector((0.0, 0.0, 5.0)))
    bpy.ops.object.light_add(type="SUN", location=(0.0, 0.0, 30.0))
    sun = bpy.context.object
    sun.name = "RLASM_QA_Sun"
    sun.rotation_euler = (math.radians(24.0), math.radians(-18.0), math.radians(132.0))
    sun.data.energy = 1.35
    sun.data.angle = math.radians(9.0)
    return materials, cameras


def render_views(output_dir: Path, cameras: dict[str, bpy.types.Object]) -> dict[str, str]:
    render_dir = output_dir / "qa"
    render_dir.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    paths: dict[str, str] = {}
    for index, spec in enumerate(CAMERA_SPECS, start=1):
        path = render_dir / f"{index:02d}-{spec.name.replace('_', '-')}.png"
        scene.camera = cameras[spec.name]
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        paths[spec.name] = str(path)
    return paths


def mesh_metrics(objects: Iterable[bpy.types.Object]) -> dict[str, int]:
    meshes = [obj for obj in objects if obj.type == "MESH"]
    return {
        "mesh_objects": len(meshes),
        "vertices": sum(len(obj.data.vertices) for obj in meshes),
        "polygons": sum(len(obj.data.polygons) for obj in meshes),
    }


def building_bounds(objects: Iterable[bpy.types.Object]) -> tuple[list[float], list[float]]:
    points: list[Vector] = []
    for obj in objects:
        if obj.type == "MESH":
            points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    return (
        [round(min(point[index] for point in points), 6) for index in range(3)],
        [round(max(point[index] for point in points), 6) for index in range(3)],
    )


def join_runtime_by_role() -> dict[str, int]:
    counts: dict[str, int] = {}
    for role in SEMANTIC_PALETTE:
        objects = [
            obj
            for obj in bpy.context.scene.objects
            if obj.type == "MESH" and obj.get("rlasm_building_object") and obj.get("cityprompt_semantic_role") == role
        ]
        if not objects:
            continue
        counts[role] = len(objects)
        bpy.ops.object.select_all(action="DESELECT")
        for obj in objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = objects[0]
        if len(objects) > 1:
            bpy.ops.object.join()
            joined = bpy.context.object
        else:
            joined = objects[0]
        joined.name = "CP_CLAY_" + role.upper()
        joined["rlasm_building_object"] = True
        joined["rlasm_method"] = METHOD
        joined["cityprompt_material_mode"] = "semantic_architectural_clay"
        joined["cityprompt_semantic_role"] = role
        joined["cityprompt_source_object_count"] = len(objects)
    return counts


def export_glb(path: Path) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH" and obj.get("rlasm_building_object"):
            obj.select_set(True)
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=True,
        export_materials="EXPORT",
        export_extras=True,
        export_cameras=False,
        export_lights=False,
        export_yup=True,
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def glb_json(path: Path) -> dict:
    with path.open("rb") as handle:
        magic, version, total_length = struct.unpack("<4sII", handle.read(12))
        if magic != b"glTF" or version != 2 or total_length != path.stat().st_size:
            raise RuntimeError("Invalid GLB header")
        chunk_length, chunk_type = struct.unpack("<II", handle.read(8))
        if chunk_type != 0x4E4F534A:
            raise RuntimeError("First GLB chunk is not JSON")
        return json.loads(handle.read(chunk_length).decode("utf-8").rstrip(" \t\r\n\x00"))


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    materials, cameras = setup_scene(args.resolution)
    build_building(materials)

    building_objects = [obj for obj in bpy.context.scene.objects if obj.get("rlasm_building_object")]
    authoring_metrics = mesh_metrics(building_objects)
    bounds_min, bounds_max = building_bounds(building_objects)
    if abs(bounds_min[2]) > 1e-6:
        raise RuntimeError(f"Bottom-centre contract violated: min z is {bounds_min[2]}")

    blend_path = output_dir / f"{CANDIDATE}-authoring.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    preview_paths = render_views(output_dir, cameras)

    joined_from = join_runtime_by_role()
    runtime_objects = [obj for obj in bpy.context.scene.objects if obj.get("rlasm_building_object")]
    runtime_metrics = mesh_metrics(runtime_objects)
    glb_path = output_dir / f"{CANDIDATE}.glb"
    export_glb(glb_path)
    payload = glb_json(glb_path)

    report = {
        "schema": "cityprompt.rlasm.semantic-clay-build@1",
        "candidate": CANDIDATE,
        "status": "BUILDER_VERIFIED_FOR_USER_VISUAL_REVIEW",
        "keeper_claimed": False,
        "method": METHOD,
        "source_mode": "exact_catalogue_triplet_only",
        "source_lock": list(SOURCE_LOCK),
        "measured_spec_m": {
            "width": WIDTH,
            "depth": DEPTH,
            "parapet_height": PARAPET_HEIGHT,
            "gable_height": GABLE_HEIGHT,
            "storeys": 2,
            "front_side_bay_count": 3,
            "depth_bay_count": 6,
        },
        "authoring": {
            "path": str(blend_path),
            "bytes": blend_path.stat().st_size,
            "sha256": sha256(blend_path),
            **authoring_metrics,
            "modular_by_bay": True,
        },
        "runtime_glb": {
            "path": str(glb_path),
            "bytes": glb_path.stat().st_size,
            "sha256": sha256(glb_path),
            **runtime_metrics,
            "glb_nodes": len(payload.get("nodes", [])),
            "glb_meshes": len(payload.get("meshes", [])),
            "materials": len(payload.get("materials", [])),
            "images": len(payload.get("images", [])),
            "textures": len(payload.get("textures", [])),
            "joined_source_objects_by_role": joined_from,
        },
        "bounds_m": {"min": bounds_min, "max": bounds_max},
        "semantic_roles": [role for role, count in joined_from.items() if count],
        "qa_views": preview_paths,
        "semantic_size_grammar": {
            "mode": "fixed_central_entry_plus_repeatable_whole_bays",
            "stretching_allowed": False,
            "native_front_bays_per_side": 3,
            "native_depth_bays": 6,
            "width_growth": "insert_or_remove_matching_storefront_and_upper_window_bay_pairs_symmetrically",
            "depth_growth": "insert_or_remove_complete_side_and_roof_bays before the fixed rear module",
            "fixed_roles": ["central_entry", "gable", "corner_piers", "cornice_returns", "rear_service_entry"],
        },
        "review": {
            "builder_pass": True,
            "independent_keeper_review": "pending",
            "runtime_seed_allowed": False,
        },
    }
    report_path = output_dir / "build-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("CLAY_FIRST_BUILD " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
