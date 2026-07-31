"""Author the Wave 10 Historic Daylight Factory LEGO family.

The assembled GLB is a complete brick northlight factory rather than a box
wearing a factory texture.  Exactly seven physical sawtooth roof bays, ten
deep segmental-arched steel-sash windows, a projecting administration entry,
three recessed loading docks, occupied workshop depth, roof trusses, gutters,
downpipes, platforms and stairs are deterministic metric geometry.

Run with Blender 5.x from the repository root:

    blender --background --factory-startup --python \
      tools/archetype_compiler/generate_wave10_daylight_factory_family.py -- \
      --output-root frontend/public/families --view-set pilot
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

from generate_wave3_landmark_families import (
    aim_camera,
    beam,
    box,
    clear_scene,
    cylinder,
    delete_objects,
    export_glb,
    facade_contract,
    load_skin_manifest,
    material,
    module_contract_markers,
    skin_material,
    texture_inventory,
)


FAMILY = "historic-daylight-factory"
ARCHETYPE_ID = "daylight_factory"
VARIANT_ID = "factory_sawtooth_roof"
ALIASES = [
    ARCHETYPE_ID,
    VARIANT_ID,
    "historic_daylight_factory",
    "brick_northlight_factory",
]
LABEL = "Daylight Factory — Historic Brick Sawtooth"
GLASS_PROFILE = "industrial_low_iron_neutral"

NATIVE_WIDTH = 70.0
NATIVE_DEPTH = 50.0
# Whole fixed-landmark height includes the restrained 3.3 m exhaust projection;
# the seven northlight peaks themselves remain 10.15 m above grade.
NATIVE_HEIGHT = 13.45
NATIVE_FLOORS = 1
MIN_FLOORS = 1
MAX_FLOORS = 3
PODIUM_HEIGHT = 0.35
FLOOR_HEIGHT = 5.80
CROWN_HEIGHT = 0.50
ROOF_HEIGHT = 3.50

BUILDING_WIDTH = 60.0
BUILDING_DEPTH = 38.0
WALL_TOP = 6.65
ROOF_VALLEY_Z = 6.65
ROOF_PEAK_Z = 10.15
ROOF_TEETH = 7
TOOTH_WIDTH = BUILDING_WIDTH / ROOF_TEETH
FRONT_Y = -BUILDING_DEPTH / 2
REAR_Y = BUILDING_DEPTH / 2

COORDINATE_CONTRACT = {
    "units": "metres",
    "blender_up": "+Z",
    "gltf_up": "+Y (export_yup)",
    "origin": "bottom centre",
    "front_facade": "-Y in Blender, +Z in glTF",
    "transforms": "applied",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("frontend/public/families"),
    )
    parser.add_argument(
        "--view-set",
        choices=(
            "preview",
            "pilot",
            "all",
            "street",
            "front_elevation",
            "rear_loading",
            "aerial",
            "roof_close",
            "window_close",
            "entrance_close",
            "side",
        ),
        default="all",
    )
    parser.add_argument("--skip-renders", action="store_true")
    parser.add_argument("--skip-modules", action="store_true")
    parser.add_argument("--skip-assembled-export", action="store_true")
    parser.add_argument("--render-existing", action="store_true")
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(argv)


def bsdf_for(mat: bpy.types.Material) -> bpy.types.Node:
    return next(
        node
        for node in mat.node_tree.nodes
        if node.bl_idname == "ShaderNodeBsdfPrincipled"
    )


def grade_material(
    mat: bpy.types.Material,
    *,
    saturation: float = 1.0,
    value: float = 1.0,
) -> bpy.types.Material:
    socket = bsdf_for(mat).inputs["Base Color"]
    if socket.is_linked:
        source = socket.links[0].from_socket
        mat.node_tree.links.remove(socket.links[0])
        grade = mat.node_tree.nodes.new("ShaderNodeHueSaturation")
        grade.name = grade.label = "REFERENCE_LOCKED_GRADE"
        grade.inputs["Saturation"].default_value = saturation
        grade.inputs["Value"].default_value = value
        mat.node_tree.links.new(source, grade.inputs["Color"])
        mat.node_tree.links.new(grade.outputs["Color"], socket)
    return mat


def set_normal_strength(
    mat: bpy.types.Material,
    strength: float,
) -> bpy.types.Material:
    for node in mat.node_tree.nodes:
        if node.bl_idname == "ShaderNodeNormalMap":
            node.inputs["Strength"].default_value = strength
    return mat


def make_glass_material(
    folder: Path,
    assets: dict[str, str],
) -> bpy.types.Material:
    mat = grade_material(
        skin_material(
            "MAT_W10_DAYLIGHT_PhysicalIndustrialLowEGlass",
            folder,
            assets,
            "industrial_glass",
            transmission=0.58,
            emission_strength=0.06,
        ),
        saturation=0.58,
        value=0.47,
    )
    bsdf = bsdf_for(mat)
    bsdf.inputs["Roughness"].default_value = 0.11
    if bsdf.inputs.get("Transmission Weight"):
        bsdf.inputs["Transmission Weight"].default_value = 0.58
    if bsdf.inputs.get("Coat Weight"):
        bsdf.inputs["Coat Weight"].default_value = 0.28
    if bsdf.inputs.get("Coat Roughness"):
        bsdf.inputs["Coat Roughness"].default_value = 0.06
    if bsdf.inputs.get("IOR"):
        bsdf.inputs["IOR"].default_value = 1.52
    if bsdf.inputs.get("Alpha"):
        bsdf.inputs["Alpha"].default_value = 0.62
    mat.diffuse_color = (0.045, 0.075, 0.095, 0.62)
    mat.use_transparency_overlap = False
    mat.use_backface_culling = False
    try:
        mat.surface_render_method = "BLENDED"
    except Exception:
        pass
    mat["glazing_profile"] = GLASS_PROFILE
    mat["glazing_lod"] = "physical_separate_pane"
    mat["skin_zone"] = "industrial_glass"
    mat["semantic_glass_mask"] = assets["glass_mask"]
    mat["semantic_opaque_mask"] = assets["opaque_mask"]
    mat["pane_recess_m"] = 0.23
    mat["interior_depth_m"] = 3.2
    mat["source_variant_id"] = VARIANT_ID
    mat["generation_archetype_id"] = VARIANT_ID
    mat["reference_locked"] = True
    return mat


def load_palette(folder: Path) -> tuple[dict[str, bpy.types.Material], dict]:
    skin = load_skin_manifest(folder)
    if not skin:
        raise FileNotFoundError(folder / "textures" / "skin_manifest.json")
    near = {zone: values["near"] for zone, values in skin["zones"].items()}
    far = {zone: values["far"] for zone, values in skin["zones"].items()}
    mats: dict[str, bpy.types.Material] = {}
    mats["brick"] = set_normal_strength(
        grade_material(
            skin_material(
                "MAT_W10_DAYLIGHT_RedBrownFiredBrick",
                folder,
                near["red_brick"],
                "red_brick",
            ),
            saturation=1.02,
            value=0.80,
        ),
        0.52,
    )
    mats["zinc"] = set_normal_strength(
        grade_material(
            skin_material(
                "MAT_W10_DAYLIGHT_OxidizedStandingSeamZinc",
                folder,
                near["zinc_roof"],
                "zinc_roof",
                metallic=0.54,
            ),
            saturation=0.48,
            value=1.05,
        ),
        0.28,
    )
    mats["steel"] = grade_material(
        skin_material(
            "MAT_W10_DAYLIGHT_BlackenedPaintedSteel",
            folder,
            near["black_steel"],
            "black_steel",
            metallic=0.55,
        ),
        saturation=0.36,
        value=0.31,
    )
    mats["limestone"] = set_normal_strength(
        grade_material(
            skin_material(
                "MAT_W10_DAYLIGHT_PaleCutLimestone",
                folder,
                near["limestone"],
                "limestone",
            ),
            saturation=0.42,
            value=0.86,
        ),
        0.23,
    )
    mats["concrete"] = set_normal_strength(
        grade_material(
            skin_material(
                "MAT_W10_DAYLIGHT_BroomFinishConcrete",
                folder,
                near["concrete"],
                "concrete",
            ),
            saturation=0.30,
            value=0.76,
        ),
        0.20,
    )
    mats["loading"] = grade_material(
        skin_material(
            "MAT_W10_DAYLIGHT_DarkGreenLoadingDoors",
            folder,
            near["loading_door"],
            "loading_door",
            metallic=0.34,
            ),
            saturation=0.72,
            value=0.56,
    )
    mats["asphalt"] = set_normal_strength(
        grade_material(
            skin_material(
                "MAT_W10_DAYLIGHT_AgedFactoryAsphalt",
                folder,
                far["asphalt"],
                "asphalt",
            ),
            saturation=0.20,
            value=0.40,
        ),
        0.13,
    )
    mats["timber"] = grade_material(
        skin_material(
            "MAT_W10_DAYLIGHT_WorkshopTimber",
            folder,
            near["timber"],
            "timber",
        ),
        saturation=0.74,
        value=0.54,
    )
    mats["interior"] = grade_material(
        skin_material(
            "MAT_W10_DAYLIGHT_OccupiedWorkshopDepth",
            folder,
            near["interior"],
            "occupied_workshop",
            emission_strength=0.42,
        ),
        saturation=0.55,
        value=0.49,
    )
    mats["glass"] = make_glass_material(folder, near["industrial_glass"])
    mats["warm_light"] = material(
        "MAT_W10_DAYLIGHT_WarmWorkshopLight",
        (1.0, 0.55, 0.23, 1.0),
        0.16,
        emission=(1.0, 0.32, 0.07, 1.0),
        emission_strength=3.6,
    )
    mats["cool_light"] = material(
        "MAT_W10_DAYLIGHT_NorthlightBounce",
        (0.64, 0.78, 0.92, 1.0),
        0.18,
        emission=(0.48, 0.70, 1.0, 1.0),
        emission_strength=0.65,
    )
    mats["rubber"] = material(
        "MAT_W10_DAYLIGHT_DockRubber",
        (0.022, 0.025, 0.024, 1.0),
        0.72,
    )
    mats["galvanized"] = material(
        "MAT_W10_DAYLIGHT_GalvanizedHardware",
        (0.20, 0.22, 0.23, 1.0),
        0.40,
        metallic=0.66,
    )
    mats["paint"] = material(
        "MAT_W10_DAYLIGHT_AdministrationInterior",
        (0.48, 0.44, 0.36, 1.0),
        0.64,
    )
    mats["vegetation"] = material(
        "MAT_W10_DAYLIGHT_RestrainedPlanting",
        (0.19, 0.25, 0.11, 1.0),
        0.82,
    )
    return mats, skin


def tag_object(
    obj: bpy.types.Object,
    component: str,
    *,
    role: str,
    count_authority: str | None = None,
) -> bpy.types.Object:
    obj["component"] = component
    obj["module_role"] = role
    obj["source_variant_id"] = VARIANT_ID
    obj["generation_archetype_id"] = VARIANT_ID
    obj["reference_locked"] = True
    if count_authority:
        obj["count_authority"] = count_authority
    apply_metric_uv_scale(obj)
    return obj


def apply_metric_uv_scale(obj: bpy.types.Object) -> None:
    """Keep generated PBR materials at construction scale, not object scale."""
    if obj.type != "MESH" or not obj.data.uv_layers.active:
        return
    mat = obj.data.materials[0] if obj.data.materials else None
    zone = str(mat.get("skin_zone", "")) if mat else ""
    repeat = {
        "red_brick": (0.88, 0.58),
        "limestone": (2.40, 1.40),
        "concrete": (2.80, 2.20),
        "zinc_roof": (3.20, 2.60),
        "asphalt": (4.20, 4.20),
        "timber": (1.80, 0.95),
    }.get(zone)
    if not repeat:
        return
    dims = obj.dimensions
    uv_layer = obj.data.uv_layers.active
    for polygon in obj.data.polygons:
        normal = polygon.normal
        if abs(normal.y) > 0.72:
            scale_u = max(dims.x / repeat[0], 0.25)
            scale_v = max(dims.z / repeat[1], 0.25)
        elif abs(normal.x) > 0.72:
            scale_u = max(dims.y / repeat[0], 0.25)
            scale_v = max(dims.z / repeat[1], 0.25)
        else:
            scale_u = max(dims.x / repeat[0], 0.25)
            scale_v = max(dims.y / repeat[1], 0.25)
        for loop_index in polygon.loop_indices:
            uv_layer.data[loop_index].uv.x *= scale_u
            uv_layer.data[loop_index].uv.y *= scale_v


def b(
    name: str,
    size: tuple[float, float, float],
    location: tuple[float, float, float],
    mat: bpy.types.Material,
    bevel: float = 0.0,
    *,
    component: str,
    role: str,
    count_authority: str | None = None,
) -> bpy.types.Object:
    return tag_object(
        box(name, size, location, mat, bevel),
        component,
        role=role,
        count_authority=count_authority,
    )


def c(
    name: str,
    radius: float,
    depth: float,
    location: tuple[float, float, float],
    mat: bpy.types.Material,
    *,
    vertices: int = 24,
    component: str,
    role: str,
    count_authority: str | None = None,
) -> bpy.types.Object:
    return tag_object(
        cylinder(
            name,
            radius,
            depth,
            location,
            mat,
            vertices=vertices,
        ),
        component,
        role=role,
        count_authority=count_authority,
    )


def bm(
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    radius: float,
    mat: bpy.types.Material,
    *,
    component: str,
    role: str,
    count_authority: str | None = None,
) -> bpy.types.Object:
    return tag_object(
        beam(name, start, end, radius, mat),
        component,
        role=role,
        count_authority=count_authority,
    )


def mesh_object(
    name: str,
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, ...]],
    mat: bpy.types.Material,
    *,
    component: str,
    role: str,
    count_authority: str | None = None,
) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(mat)
    if vertices:
        xs = [item[0] for item in vertices]
        ys = [item[1] for item in vertices]
        zs = [item[2] for item in vertices]
        span_x = max(max(xs) - min(xs), 0.001)
        span_y = max(max(ys) - min(ys), 0.001)
        span_z = max(max(zs) - min(zs), 0.001)
        uv = mesh.uv_layers.new(name="UVMap")
        for polygon in mesh.polygons:
            for loop_index in polygon.loop_indices:
                co = mesh.vertices[
                    mesh.loops[loop_index].vertex_index
                ].co
                if abs(polygon.normal.y) > 0.72:
                    value = (
                        (co.x - min(xs)) / span_x,
                        (co.z - min(zs)) / span_z,
                    )
                elif abs(polygon.normal.x) > 0.72:
                    value = (
                        (co.y - min(ys)) / span_y,
                        (co.z - min(zs)) / span_z,
                    )
                else:
                    value = (
                        (co.y - min(ys)) / span_y,
                        (co.x - min(xs)) / span_x,
                    )
                uv.data[loop_index].uv = value
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return tag_object(
        obj,
        component,
        role=role,
        count_authority=count_authority,
    )


def sloped_slab(
    name: str,
    x0: float,
    z0: float,
    x1: float,
    z1: float,
    y0: float,
    y1: float,
    thickness: float,
    mat: bpy.types.Material,
    *,
    component: str,
    role: str,
    count_authority: str | None = None,
) -> bpy.types.Object:
    vertices = [
        (x0, y0, z0),
        (x1, y0, z1),
        (x1, y1, z1),
        (x0, y1, z0),
        (x0, y0, z0 - thickness),
        (x1, y0, z1 - thickness),
        (x1, y1, z1 - thickness),
        (x0, y1, z0 - thickness),
    ]
    faces = [
        (0, 1, 2, 3),
        (7, 6, 5, 4),
        (0, 4, 5, 1),
        (1, 5, 6, 2),
        (2, 6, 7, 3),
        (3, 7, 4, 0),
    ]
    return mesh_object(
        name,
        vertices,
        faces,
        mat,
        component=component,
        role=role,
        count_authority=count_authority,
    )


def segmental_curve(
    centre_x: float,
    width: float,
    spring_z: float,
    rise: float,
    segments: int = 18,
) -> list[tuple[float, float]]:
    radius = width * width / (8.0 * rise) + rise / 2.0
    centre_z = spring_z - (radius - rise)
    values = []
    for index in range(segments + 1):
        x = centre_x - width / 2 + width * index / segments
        local_x = x - centre_x
        z = centre_z + math.sqrt(max(radius * radius - local_x * local_x, 0))
        values.append((x, z))
    return values


def segmental_window(
    prefix: str,
    index: int,
    centre_x: float,
    facade_y: float,
    sill_z: float,
    width: float,
    spring_z: float,
    rise: float,
    mats: dict[str, bpy.types.Material],
    *,
    role: str,
    mullion_variant: int = 0,
    detailed: bool = True,
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    curve = segmental_curve(centre_x, width, spring_z, rise)
    glass_y = facade_y + 0.245
    frame_y = facade_y + 0.19
    vertices = [
        (centre_x - width / 2, glass_y, sill_z),
        (centre_x + width / 2, glass_y, sill_z),
        (centre_x + width / 2, glass_y, spring_z),
        *[
            (x, glass_y, z)
            for x, z in reversed(curve[:-1])
        ],
    ]
    objects.append(
        mesh_object(
            f"{prefix}_FrontWindowGlass_{index:02d}",
            vertices,
            [tuple(range(len(vertices)))],
            mats["glass"],
            component="physical_segmental_arch_glass",
            role=role,
            count_authority="ten_front_steel_sash_window_openings",
        )
    )
    # Deep sill and jambs establish the physical wall thickness.
    objects.append(
        b(
            f"{prefix}_FrontWindowStoneSill_{index:02d}",
            (width + 0.34, 0.55, 0.18),
            (centre_x, facade_y - 0.01, sill_z - 0.08),
            mats["limestone"],
            0.025,
            component="deep_limestone_window_sill",
            role=role,
        )
    )
    for side in (-1, 1):
        objects.append(
            b(
                f"{prefix}_FrontWindowDeepJamb_{index:02d}_{side}",
                (0.24, 0.50, spring_z - sill_z),
                (
                    centre_x + side * (width / 2 + 0.12),
                    facade_y,
                    sill_z + (spring_z - sill_z) / 2,
                ),
                mats["brick"],
                0.025,
                component="deep_brick_window_reveal",
                role=role,
            )
        )
    # Steel perimeter follows the actual segmental head.
    objects.append(
        bm(
            f"{prefix}_FrontWindowFrameLeft_{index:02d}",
            (centre_x - width / 2, frame_y, sill_z),
            (centre_x - width / 2, frame_y, spring_z),
            0.055,
            mats["steel"],
            component="rolled_steel_sash_perimeter",
            role=role,
        )
    )
    objects.append(
        bm(
            f"{prefix}_FrontWindowFrameRight_{index:02d}",
            (centre_x + width / 2, frame_y, sill_z),
            (centre_x + width / 2, frame_y, spring_z),
            0.055,
            mats["steel"],
            component="rolled_steel_sash_perimeter",
            role=role,
        )
    )
    objects.append(
        bm(
            f"{prefix}_FrontWindowFrameSill_{index:02d}",
            (centre_x - width / 2, frame_y, sill_z),
            (centre_x + width / 2, frame_y, sill_z),
            0.055,
            mats["steel"],
            component="rolled_steel_sash_perimeter",
            role=role,
        )
    )
    for segment in range(len(curve) - 1):
        objects.append(
            bm(
                f"{prefix}_FrontWindowArchFrame_{index:02d}_{segment:02d}",
                (curve[segment][0], frame_y, curve[segment][1]),
                (curve[segment + 1][0], frame_y, curve[segment + 1][1]),
                0.055,
                mats["steel"],
                component="rolled_segmental_arch_head",
                role=role,
            )
        )
        # Brick spandrel is constructed around, never behind, the opening.
        xa, za = curve[segment]
        xb, zb = curve[segment + 1]
        vertices_fill = [
            (xa, facade_y - 0.225, za + 0.12),
            (xb, facade_y - 0.225, zb + 0.12),
            (xb, facade_y - 0.225, WALL_TOP - 0.50),
            (xa, facade_y - 0.225, WALL_TOP - 0.50),
            (xa, facade_y + 0.225, za + 0.12),
            (xb, facade_y + 0.225, zb + 0.12),
            (xb, facade_y + 0.225, WALL_TOP - 0.50),
            (xa, facade_y + 0.225, WALL_TOP - 0.50),
        ]
        objects.append(
            mesh_object(
                f"{prefix}_FrontWindowBrickSpandrel_{index:02d}_{segment:02d}",
                vertices_fill,
                [
                    (0, 1, 2, 3),
                    (7, 6, 5, 4),
                    (0, 4, 5, 1),
                    (1, 5, 6, 2),
                    (2, 6, 7, 3),
                    (3, 7, 4, 0),
                ],
                mats["brick"],
                component="brick_spandrel_around_arch_void",
                role=role,
            )
        )
    mullions = (3, 4, 5)[mullion_variant % 3]
    for mullion in range(1, mullions):
        x = centre_x - width / 2 + width * mullion / mullions
        radius = width * width / (8.0 * rise) + rise / 2.0
        centre_z = spring_z - (radius - rise)
        top_z = centre_z + math.sqrt(
            max(radius * radius - (x - centre_x) ** 2, 0)
        )
        objects.append(
            bm(
                f"{prefix}_FrontWindowMullion_{index:02d}_{mullion:02d}",
                (x, frame_y - 0.01, sill_z + 0.06),
                (x, frame_y - 0.01, top_z - 0.06),
                0.036,
                mats["steel"],
                component="slender_vertical_steel_sash",
                role=role,
            )
        )
    transom_count = 5 if detailed else 4
    for transom in range(1, transom_count):
        z = sill_z + (spring_z - sill_z) * transom / transom_count
        objects.append(
            bm(
                f"{prefix}_FrontWindowTransom_{index:02d}_{transom:02d}",
                (centre_x - width / 2 + 0.06, frame_y, z),
                (centre_x + width / 2 - 0.06, frame_y, z),
                0.032,
                mats["steel"],
                component="slender_horizontal_steel_sash",
                role=role,
            )
        )
    if detailed:
        objects.append(
            b(
                f"{prefix}_OccupiedWorkshopDepth_{index:02d}",
                (width - 0.25, 0.10, spring_z - sill_z - 0.35),
                (
                    centre_x,
                    facade_y + 2.65,
                    sill_z + (spring_z - sill_z) / 2,
                ),
                mats["interior"],
                component="occupied_workshop_depth_plane",
                role=role,
            )
        )
        # A bench and task light create true parallax behind each sash.
        objects.append(
            b(
                f"{prefix}_WorkshopBench_{index:02d}",
                (width - 0.55, 0.72, 0.12),
                (centre_x, facade_y + 1.55, 1.35),
                mats["timber"],
                0.025,
                component="visible_workshop_bench",
                role=role,
            )
        )
        objects.append(
            b(
                f"{prefix}_WorkshopTaskLight_{index:02d}",
                (width - 0.80, 0.055, 0.055),
                (centre_x, facade_y + 1.78, 4.65),
                mats["warm_light"],
                component="visible_workshop_task_light",
                role=role,
            )
        )
    return objects


def add_site(
    mats: dict[str, bpy.types.Material],
    *,
    detailed: bool,
    prefix: str = "DAYLIGHT",
) -> list[bpy.types.Object]:
    role = "podium"
    objects = [
        b(
            f"{prefix}_CompleteSiteSlab",
            (NATIVE_WIDTH, NATIVE_DEPTH, 0.24),
            (0.0, 0.0, 0.12),
            mats["asphalt"],
            0.04,
            component="complete_factory_site",
            role=role,
        ),
        b(
            f"{prefix}_FrontPublicApron",
            (64.0, 5.2, 0.16),
            (0.0, -21.3, 0.26),
            mats["concrete"],
            0.025,
            component="front_public_apron",
            role=role,
        ),
        b(
            f"{prefix}_RearLoadingApron",
            (66.0, 7.0, 0.18),
            (0.0, 21.0, 0.27),
            mats["concrete"],
            0.025,
            component="rear_loading_apron",
            role=role,
        ),
        b(
            f"{prefix}_FactoryFloorSlab",
            (59.2, 37.2, 0.26),
            (0.0, 0.0, 0.38),
            mats["concrete"],
            0.03,
            component="factory_floor_slab",
            role=role,
        ),
    ]
    if not detailed:
        return objects
    for index, x in enumerate(range(-30, 31, 5)):
        objects.append(
            b(
                f"{prefix}_FrontApronJoint_{index:02d}",
                (0.035, 5.0, 0.018),
                (float(x), -21.3, 0.35),
                mats["rubber"],
                component="concrete_control_joint",
                role=role,
            )
        )
    for index, x in enumerate(range(-30, 31, 6)):
        objects.append(
            b(
                f"{prefix}_RearApronJoint_{index:02d}",
                (0.035, 6.8, 0.018),
                (float(x), 21.0, 0.37),
                mats["rubber"],
                component="loading_apron_control_joint",
                role=role,
            )
        )
    for side in (-1, 1):
        for index, y in enumerate((-13.5, -7.5, -1.5, 4.5, 10.5)):
            objects.append(
                c(
                    f"{prefix}_SidePlanting_{side}_{index:02d}",
                    0.38,
                    0.8,
                    (side * 32.2, y, 0.70),
                    mats["vegetation"],
                    vertices=12,
                    component="restrained_factory_edge_planting",
                    role=role,
                )
            )
    return objects


def add_front_facade(
    mats: dict[str, bpy.types.Material],
    *,
    base_z: float,
    detailed: bool,
    prefix: str = "DAYLIGHT",
    mullion_variant: int = 0,
) -> list[bpy.types.Object]:
    role = "floor"
    top = base_z + FLOOR_HEIGHT
    facade_y = FRONT_Y
    objects: list[bpy.types.Object] = [
        b(
            f"{prefix}_FrontBrickPodiumBand",
            (BUILDING_WIDTH, 0.46, 0.72),
            (0.0, facade_y, base_z + 0.36),
            mats["brick"],
            0.018,
            component="load_bearing_brick_podium_band",
            role=role,
        ),
        b(
            f"{prefix}_FrontLimestonePlinth",
            (BUILDING_WIDTH + 0.20, 0.52, 0.34),
            (0.0, facade_y - 0.02, base_z + 0.20),
            mats["limestone"],
            0.018,
            component="continuous_limestone_plinth",
            role=role,
        ),
        b(
            f"{prefix}_FrontBrickHead",
            (BUILDING_WIDTH, 0.46, 0.52),
            (0.0, facade_y, top - 0.26),
            mats["brick"],
            0.018,
            component="continuous_brick_window_head",
            role=role,
        ),
    ]
    window_centres = (
        -26.6,
        -21.3,
        -16.0,
        -10.7,
        -5.4,
        5.4,
        10.7,
        16.0,
        21.3,
        26.6,
    )
    # Piers define the wall around the apertures; there is no hidden wall
    # plane behind the physical panes.
    pier_centres = (
        -29.55,
        -23.95,
        -18.65,
        -13.35,
        -8.05,
        -2.75,
        2.75,
        8.05,
        13.35,
        18.65,
        23.95,
        29.55,
    )
    for index, x in enumerate(pier_centres):
        width = 0.90 if abs(x) > 29.0 else 1.08
        objects.append(
            b(
                f"{prefix}_FrontLoadBearingPier_{index:02d}",
                (width, 0.46, FLOOR_HEIGHT - 0.72),
                (x, facade_y, base_z + 0.72 + (FLOOR_HEIGHT - 0.72) / 2),
                mats["brick"],
                0.018,
                component="load_bearing_brick_pier",
                role=role,
            )
        )
    sill_z = base_z + 1.12
    spring_z = base_z + 4.78
    for index, x in enumerate(window_centres):
        objects.extend(
            segmental_window(
                prefix,
                index,
                x,
                facade_y,
                sill_z,
                3.82,
                spring_z,
                0.55,
                mats,
                role=role,
                mullion_variant=mullion_variant,
                detailed=detailed,
            )
        )
    objects.extend(
        add_entrance(
            mats,
            base_z=base_z,
            detailed=detailed,
            prefix=prefix,
        )
    )
    return objects


def add_entrance(
    mats: dict[str, bpy.types.Material],
    *,
    base_z: float,
    detailed: bool,
    prefix: str,
) -> list[bpy.types.Object]:
    role = "floor"
    y = FRONT_Y - 1.05
    objects = [
        b(
            f"{prefix}_AdministrationVestibuleLeftPier",
            (1.02, 2.28, 3.25),
            (-2.30, y, base_z + 1.625),
            mats["brick"],
            0.035,
            component="projecting_brick_administration_entry",
            role=role,
        ),
        b(
            f"{prefix}_AdministrationVestibuleRightPier",
            (1.02, 2.28, 3.25),
            (2.30, y, base_z + 1.625),
            mats["brick"],
            0.035,
            component="projecting_brick_administration_entry",
            role=role,
        ),
        b(
            f"{prefix}_AdministrationVestibuleHead",
            (5.62, 2.28, 0.55),
            (0.0, y, base_z + 3.00),
            mats["brick"],
            0.035,
            component="projecting_brick_administration_entry",
            role=role,
        ),
        b(
            f"{prefix}_AdministrationEntryLimestoneCap",
            (5.88, 2.52, 0.17),
            (0.0, y, base_z + 3.36),
            mats["limestone"],
            0.025,
            component="entry_limestone_cap",
            role=role,
        ),
        b(
            f"{prefix}_AdministrationBrickWallAboveEntry",
            (5.50, 0.46, 2.40),
            (
                0.0,
                FRONT_Y,
                base_z + 3.40 + 1.20,
            ),
            mats["brick"],
            0.018,
            component="continuous_brick_wall_above_projecting_entry",
            role=role,
        ),
        b(
            f"{prefix}_AdministrationDoorLeftPane",
            (1.58, 0.08, 2.55),
            (-0.82, FRONT_Y - 2.20, base_z + 1.42),
            mats["glass"],
            component="recessed_glazed_double_entry",
            role=role,
        ),
        b(
            f"{prefix}_AdministrationDoorRightPane",
            (1.58, 0.08, 2.55),
            (0.82, FRONT_Y - 2.20, base_z + 1.42),
            mats["glass"],
            component="recessed_glazed_double_entry",
            role=role,
        ),
    ]
    for x in (-1.66, 0.0, 1.66):
        objects.append(
            b(
                f"{prefix}_AdministrationDoorMullion_{x:+.2f}",
                (0.08, 0.13, 2.62),
                (x, FRONT_Y - 2.24, base_z + 1.42),
                mats["steel"],
                0.012,
                component="entry_steel_frame",
                role=role,
            )
        )
    for frame_name, z, width, depth in (
        ("Head", base_z + 2.70, 3.40, 0.10),
        ("Transom", base_z + 2.02, 3.28, 0.075),
        ("Threshold", base_z + 0.14, 3.40, 0.10),
    ):
        objects.append(
            b(
                f"{prefix}_AdministrationDoor{frame_name}Frame",
                (width, 0.15, depth),
                (0.0, FRONT_Y - 2.24, z),
                mats["steel"],
                0.012,
                component="entry_steel_frame",
                role=role,
            )
        )
    objects.append(
        b(
            f"{prefix}_AdministrationCanopy",
            (6.80, 2.10, 0.18),
            (0.0, FRONT_Y - 2.75, base_z + 3.10),
            mats["zinc"],
            0.025,
            component="thin_integrated_steel_entry_canopy",
            role=role,
        )
    )
    for side in (-1, 1):
        objects.append(
            bm(
                f"{prefix}_AdministrationCanopyRod_{side}",
                (side * 2.55, FRONT_Y - 1.72, base_z + 3.02),
                (side * 2.55, FRONT_Y - 3.55, base_z + 3.88),
                0.036,
                mats["steel"],
                component="canopy_tension_rod",
                role=role,
            )
        )
    if detailed:
        for side in (-1, 1):
            objects.append(
                b(
                    f"{prefix}_AdministrationDoorHandle_{side}",
                    (0.035, 0.14, 0.72),
                    (side * 0.18, FRONT_Y - 2.31, base_z + 1.34),
                    mats["galvanized"],
                    0.012,
                    component="entry_door_hardware",
                    role=role,
                )
            )
        objects.append(
            b(
                f"{prefix}_AdministrationOccupiedDepth",
                (3.05, 0.10, 2.38),
                (0.0, FRONT_Y - 0.15, base_z + 1.43),
                mats["paint"],
                component="occupied_administration_depth",
                role=role,
            )
        )
        objects.append(
            b(
                f"{prefix}_AdministrationWarmCeilingLight",
                (2.35, 0.08, 0.06),
                (0.0, FRONT_Y - 0.35, base_z + 2.66),
                mats["warm_light"],
                component="occupied_administration_light",
                role=role,
            )
        )
    return objects


def add_crown(
    mats: dict[str, bpy.types.Material],
    *,
    base_z: float,
    detailed: bool,
    prefix: str = "DAYLIGHT",
) -> list[bpy.types.Object]:
    role = "crown"
    objects = [
        b(
            f"{prefix}_FrontCorbelCourse",
            (BUILDING_WIDTH + 0.18, 0.62, 0.18),
            (0.0, FRONT_Y - 0.04, base_z + 0.14),
            mats["brick"],
            0.015,
            component="corbelled_brick_eave_course",
            role=role,
        ),
        b(
            f"{prefix}_RearCorbelCourse",
            (BUILDING_WIDTH + 0.18, 0.62, 0.18),
            (0.0, REAR_Y + 0.04, base_z + 0.14),
            mats["brick"],
            0.015,
            component="corbelled_brick_eave_course",
            role=role,
        ),
        b(
            f"{prefix}_LeftBrickCap",
            (0.62, BUILDING_DEPTH, 0.20),
            (-BUILDING_WIDTH / 2, 0.0, base_z + 0.16),
            mats["brick"],
            0.015,
            component="brick_return_eave_course",
            role=role,
        ),
        b(
            f"{prefix}_RightBrickCap",
            (0.62, BUILDING_DEPTH, 0.20),
            (BUILDING_WIDTH / 2, 0.0, base_z + 0.16),
            mats["brick"],
            0.015,
            component="brick_return_eave_course",
            role=role,
        ),
    ]
    if detailed:
        for facade_name, y in (("Front", FRONT_Y - 0.38), ("Rear", REAR_Y + 0.38)):
            for index in range(82):
                x = -29.52 + index * 0.73
                objects.append(
                    b(
                        f"{prefix}_{facade_name}CorbelBlock_{index:02d}",
                        (0.34, 0.34, 0.24),
                        (x, y, base_z + 0.30),
                        mats["brick"],
                        0.018,
                        component="individual_brick_corbel_block",
                        role=role,
                    )
                )
    return objects


def side_window(
    prefix: str,
    side: int,
    index: int,
    centre_y: float,
    base_z: float,
    mats: dict[str, bpy.types.Material],
    *,
    detailed: bool,
) -> list[bpy.types.Object]:
    role = "floor"
    x = side * (BUILDING_WIDTH / 2 - 0.245)
    frame_x = side * (BUILDING_WIDTH / 2 - 0.30)
    width = 3.45
    sill = base_z + 1.25
    height = 3.70
    objects = [
        b(
            f"{prefix}_SideWindowGlass_{side}_{index:02d}",
            (0.07, width, height),
            (x, centre_y, sill + height / 2),
            mats["glass"],
            component="physical_side_industrial_window",
            role=role,
        ),
        b(
            f"{prefix}_SideWindowSill_{side}_{index:02d}",
            (0.56, width + 0.30, 0.18),
            (side * (BUILDING_WIDTH / 2 + 0.01), centre_y, sill - 0.09),
            mats["limestone"],
            0.018,
            component="side_limestone_sill",
            role=role,
        ),
    ]
    for offset in (-width / 2, 0.0, width / 2):
        objects.append(
            b(
                f"{prefix}_SideWindowVerticalFrame_{side}_{index:02d}_{offset:+.2f}",
                (0.12, 0.075, height),
                (frame_x, centre_y + offset, sill + height / 2),
                mats["steel"],
                0.012,
                component="side_steel_sash_frame",
                role=role,
            )
        )
    for transom in range(5):
        z = sill + height * transom / 4
        objects.append(
            b(
                f"{prefix}_SideWindowTransom_{side}_{index:02d}_{transom}",
                (0.12, width, 0.065),
                (frame_x, centre_y, z),
                mats["steel"],
                0.012,
                component="side_steel_sash_frame",
                role=role,
            )
        )
    if detailed:
        objects.append(
            b(
                f"{prefix}_SideWindowOccupiedDepth_{side}_{index:02d}",
                (0.08, width - 0.20, height - 0.25),
                (
                    side * (BUILDING_WIDTH / 2 - 2.30),
                    centre_y,
                    sill + height / 2,
                ),
                mats["interior"],
                component="side_occupied_workshop_depth",
                role=role,
            )
        )
    return objects


def add_side_facades(
    mats: dict[str, bpy.types.Material],
    *,
    base_z: float,
    detailed: bool,
    prefix: str = "DAYLIGHT",
) -> list[bpy.types.Object]:
    role = "floor"
    objects: list[bpy.types.Object] = []
    window_centres = (-13.6, -7.1, 0.0, 7.1, 13.6)
    pier_centres = (-18.55, -10.35, -3.55, 3.55, 10.35, 18.55)
    for side in (-1, 1):
        objects.extend(
            [
                b(
                    f"{prefix}_SideBrickBase_{side}",
                    (0.46, BUILDING_DEPTH, 0.76),
                    (
                        side * BUILDING_WIDTH / 2,
                        0.0,
                        base_z + 0.38,
                    ),
                    mats["brick"],
                    0.018,
                    component="side_load_bearing_brick_base",
                    role=role,
                ),
                b(
                    f"{prefix}_SideBrickHead_{side}",
                    (0.46, BUILDING_DEPTH, 0.62),
                    (
                        side * BUILDING_WIDTH / 2,
                        0.0,
                        base_z + FLOOR_HEIGHT - 0.31,
                    ),
                    mats["brick"],
                    0.018,
                    component="side_load_bearing_brick_head",
                    role=role,
                ),
            ]
        )
        for index, y in enumerate(pier_centres):
            objects.append(
                b(
                    f"{prefix}_SideLoadBearingPier_{side}_{index:02d}",
                    (0.46, 2.80, FLOOR_HEIGHT - 0.76),
                    (
                        side * BUILDING_WIDTH / 2,
                        y,
                        base_z + 0.76 + (FLOOR_HEIGHT - 0.76) / 2,
                    ),
                    mats["brick"],
                    0.018,
                    component="side_load_bearing_brick_pier",
                    role=role,
                )
            )
        for index, y in enumerate(window_centres):
            objects.extend(
                side_window(
                    prefix,
                    side,
                    index,
                    y,
                    base_z,
                    mats,
                    detailed=detailed,
                )
            )
    return objects


def add_loading_stair(
    prefix: str,
    side: int,
    mats: dict[str, bpy.types.Material],
    *,
    base_z: float,
) -> list[bpy.types.Object]:
    role = "floor"
    objects: list[bpy.types.Object] = []
    steps = 7
    x_start = side * 23.8
    direction = -side
    y = REAR_Y + 2.45
    for index in range(steps):
        height = 0.16 * (index + 1)
        x = x_start + direction * 0.30 * index
        objects.append(
            b(
                f"{prefix}_LoadingStairTread_{side}_{index:02d}",
                (0.34, 1.35, height),
                (x, y, base_z + height / 2),
                mats["galvanized"],
                0.015,
                component="real_loading_stair_tread",
                role=role,
                count_authority="two_integrated_loading_stair_runs",
            )
        )
    run_end = x_start + direction * 0.30 * (steps - 1)
    for y_side in (-0.68, 0.68):
        objects.append(
            bm(
                f"{prefix}_LoadingStairRail_{side}_{y_side:+.2f}",
                (x_start, y + y_side, base_z + 0.82),
                (run_end, y + y_side, base_z + 1.88),
                0.038,
                mats["galvanized"],
                component="loading_stair_handrail",
                role=role,
            )
        )
        for index in (0, 3, 6):
            x = x_start + direction * 0.30 * index
            z = base_z + 0.16 * (index + 1)
            objects.append(
                bm(
                    f"{prefix}_LoadingStairRailPost_{side}_{y_side:+.2f}_{index}",
                    (x, y + y_side, z),
                    (x, y + y_side, z + 0.92),
                    0.028,
                    mats["galvanized"],
                    component="loading_stair_handrail_post",
                    role=role,
                )
            )
    return objects


def add_rear_facade(
    mats: dict[str, bpy.types.Material],
    *,
    base_z: float,
    detailed: bool,
    prefix: str = "DAYLIGHT",
) -> list[bpy.types.Object]:
    role = "floor"
    top = base_z + FLOOR_HEIGHT
    objects: list[bpy.types.Object] = [
        b(
            f"{prefix}_RearBrickBase",
            (BUILDING_WIDTH, 0.46, 1.10),
            (0.0, REAR_Y, base_z + 0.55),
            mats["brick"],
            0.018,
            component="rear_loading_wall_base",
            role=role,
        ),
        b(
            f"{prefix}_RearBrickHead",
            (BUILDING_WIDTH, 0.46, 1.30),
            (0.0, REAR_Y, top - 0.65),
            mats["brick"],
            0.018,
            component="rear_loading_wall_head",
            role=role,
        ),
    ]
    door_centres = (-16.0, 0.0, 16.0)
    # Solid brick wall intervals between the five genuine openings.  These
    # panels close the service elevation without placing a wall behind any
    # loading or personnel door.
    wall_intervals = (
        (-30.0, -27.725),
        (-26.275, -19.325),
        (-12.675, -3.325),
        (3.325, 12.675),
        (19.325, 26.275),
        (27.725, 30.0),
    )
    for index, (x0, x1) in enumerate(wall_intervals):
        width = x1 - x0
        x = (x0 + x1) / 2
        objects.append(
            b(
                f"{prefix}_RearLoadBearingWallPanel_{index:02d}",
                (width, 0.46, FLOOR_HEIGHT - 1.10),
                (
                    x,
                    REAR_Y,
                    base_z + 1.10 + (FLOOR_HEIGHT - 1.10) / 2,
                ),
                mats["brick"],
                0.018,
                component="rear_load_bearing_brick_wall_between_openings",
                role=role,
            )
        )
    for index, x in enumerate(door_centres):
        door_z = base_z + 1.10
        objects.append(
            b(
                f"{prefix}_RecessedLoadingDoor_{index}",
                (6.65, 0.12, 3.90),
                (x, REAR_Y - 0.29, door_z + 1.95),
                mats["loading"],
                0.025,
                component="genuinely_recessed_loading_door",
                role=role,
                count_authority="three_recessed_rear_loading_docks",
            )
        )
        for slat in range(1, 12):
            z = door_z + 3.90 * slat / 12
            objects.append(
                b(
                    f"{prefix}_LoadingDoorSlat_{index}_{slat:02d}",
                    (6.48, 0.035, 0.026),
                    (x, REAR_Y + 0.075, z),
                    mats["steel"],
                    component="loading_door_section_joint",
                    role=role,
                )
            )
        for pane in range(3):
            objects.append(
                b(
                    f"{prefix}_LoadingDoorVisionPane_{index}_{pane}",
                    (1.18, 0.05, 0.34),
                    (
                        x - 1.40 + pane * 1.40,
                        REAR_Y + 0.095,
                        door_z + 2.08,
                    ),
                    mats["glass"],
                    component="loading_door_vision_panel",
                    role=role,
                )
            )
        objects.append(
            b(
                f"{prefix}_LoadingDockPlatform_{index}",
                (8.20, 3.05, 1.05),
                (x, REAR_Y + 1.58, base_z + 0.525),
                mats["concrete"],
                0.035,
                component="real_loading_dock_platform",
                role=role,
            )
        )
        objects.append(
            b(
                f"{prefix}_LoadingDockCanopy_{index}",
                (8.60, 2.60, 0.20),
                (x, REAR_Y + 1.25, base_z + 5.18),
                mats["zinc"],
                0.025,
                component="loading_dock_weather_canopy",
                role=role,
            )
        )
        for side in (-1, 1):
            objects.append(
                b(
                    f"{prefix}_DockBumper_{index}_{side}",
                    (0.34, 0.34, 0.72),
                    (
                        x + side * 2.62,
                        REAR_Y + 0.33,
                        base_z + 1.45,
                    ),
                    mats["rubber"],
                    0.03,
                    component="loading_dock_rubber_bumper",
                    role=role,
                )
            )
    # Two personnel doors flank the dock rhythm.
    for side in (-1, 1):
        x = side * 27.0
        objects.append(
            b(
                f"{prefix}_RearPersonnelDoor_{side}",
                (1.45, 0.10, 2.55),
                (x, REAR_Y - 0.29, base_z + 1.28),
                mats["loading"],
                0.02,
                component="recessed_rear_personnel_door",
                role=role,
            )
        )
        personnel_head_bottom = base_z + 2.555
        main_head_bottom = base_z + FLOOR_HEIGHT - 1.30
        personnel_head_height = main_head_bottom - personnel_head_bottom
        objects.append(
            b(
                f"{prefix}_RearPersonnelDoorBrickHead_{side}",
                (1.45, 0.46, personnel_head_height),
                (
                    x,
                    REAR_Y,
                    personnel_head_bottom + personnel_head_height / 2,
                ),
                mats["brick"],
                0.018,
                component="brick_wall_above_recessed_personnel_door",
                role=role,
            )
        )
        objects.append(
            b(
                f"{prefix}_RearPersonnelDoorCanopy_{side}",
                (2.20, 1.05, 0.16),
                (x, REAR_Y + 0.42, base_z + 2.82),
                mats["zinc"],
                0.02,
                component="personnel_door_canopy",
                role=role,
            )
        )
    if detailed:
        objects.extend(
            add_loading_stair(
                prefix,
                -1,
                mats,
                base_z=base_z,
            )
        )
        objects.extend(
            add_loading_stair(
                prefix,
                1,
                mats,
                base_z=base_z,
            )
        )
        for index, x in enumerate((-24.2, -8.1, 8.1, 24.2)):
            objects.append(
                b(
                    f"{prefix}_RearWallVent_{index}",
                    (2.1, 0.10, 0.70),
                    (x, REAR_Y + 0.245, base_z + 4.85),
                    mats["steel"],
                    0.025,
                    component="rear_wall_louver",
                    role=role,
                )
            )
            for slat in range(5):
                objects.append(
                    b(
                        f"{prefix}_RearWallVentSlat_{index}_{slat}",
                        (1.92, 0.08, 0.035),
                        (
                            x,
                            REAR_Y + 0.32,
                            base_z + 4.57 + slat * 0.14,
                        ),
                        mats["galvanized"],
                        component="rear_louver_blade",
                        role=role,
                    )
                )
    return objects


def add_interior_structure(
    mats: dict[str, bpy.types.Material],
    *,
    base_z: float,
    detailed: bool,
    prefix: str = "DAYLIGHT",
) -> list[bpy.types.Object]:
    if not detailed:
        return []
    role = "floor"
    objects: list[bpy.types.Object] = []
    # Real columns and work cells are visible through both facade and roof.
    for row, y in enumerate((-12.5, -6.25, 0.0, 6.25, 12.5)):
        for tooth in range(ROOF_TEETH + 1):
            x = -BUILDING_WIDTH / 2 + tooth * TOOTH_WIDTH
            objects.append(
                b(
                    f"{prefix}_WorkshopColumn_{row}_{tooth}",
                    (0.26, 0.26, FLOOR_HEIGHT - 0.35),
                    (x, y, base_z + (FLOOR_HEIGHT - 0.35) / 2),
                    mats["steel"],
                    0.018,
                    component="visible_workshop_steel_column",
                    role=role,
                )
            )
    for row, y in enumerate((-14.0, -7.0, 0.0, 7.0, 14.0)):
        for cell, x in enumerate((-22.0, -11.0, 0.0, 11.0, 22.0)):
            objects.extend(
                [
                    b(
                        f"{prefix}_WorkshopTableTop_{row}_{cell}",
                        (6.0, 1.35, 0.14),
                        (x, y, base_z + 1.08),
                        mats["timber"],
                        0.025,
                        component="occupied_workshop_table",
                        role=role,
                    ),
                    b(
                        f"{prefix}_WorkshopMachineBase_{row}_{cell}",
                        (1.3, 0.95, 1.25),
                        (x - 1.55, y, base_z + 0.72),
                        mats["loading"],
                        0.08,
                        component="occupied_workshop_machine",
                        role=role,
                    ),
                    b(
                        f"{prefix}_WorkshopPendantLight_{row}_{cell}",
                        (2.6, 0.09, 0.07),
                        (x, y, base_z + 5.00),
                        mats["warm_light"],
                        component="occupied_workshop_light",
                        role=role,
                    ),
                ]
            )
    return objects


def add_roof(
    mats: dict[str, bpy.types.Material],
    *,
    base_z: float,
    detailed: bool,
    prefix: str = "DAYLIGHT",
) -> list[bpy.types.Object]:
    role = "roof"
    objects: list[bpy.types.Object] = []
    valley_z = base_z
    peak_z = base_z + ROOF_HEIGHT
    y0 = FRONT_Y + 0.40
    y1 = REAR_Y - 0.40
    for index in range(ROOF_TEETH):
        x0 = -BUILDING_WIDTH / 2 + index * TOOTH_WIDTH
        x1 = x0 + TOOTH_WIDTH
        peak_x = x0 + TOOTH_WIDTH * 0.80
        objects.append(
            sloped_slab(
                f"{prefix}_RoofToothOpaque_{index}",
                x0,
                valley_z,
                peak_x,
                peak_z,
                y0,
                y1,
                0.16,
                mats["zinc"],
                component="opaque_standing_seam_northlight_slope",
                role=role,
                count_authority="exactly_seven_northlight_roof_teeth",
            )
        )
        objects.append(
            sloped_slab(
                f"{prefix}_RoofToothClerestoryGlass_{index}",
                peak_x,
                peak_z,
                x1,
                valley_z,
                y0,
                y1,
                0.055,
                mats["glass"],
                component="steep_north_facing_clerestory_glass",
                role=role,
                count_authority="exactly_seven_physical_clerestories",
            )
        )
        # Steel head, sill and evenly spaced mullions are independent of glass.
        objects.append(
            bm(
                f"{prefix}_ClerestoryHeadRail_{index}",
                (peak_x, y0, peak_z + 0.03),
                (peak_x, y1, peak_z + 0.03),
                0.085,
                mats["steel"],
                component="clerestory_steel_head_rail",
                role=role,
            )
        )
        objects.append(
            bm(
                f"{prefix}_ClerestorySillRail_{index}",
                (x1, y0, valley_z + 0.05),
                (x1, y1, valley_z + 0.05),
                0.085,
                mats["steel"],
                component="clerestory_steel_sill_rail",
                role=role,
            )
        )
        mullion_count = 10 if detailed else 6
        for mullion in range(mullion_count + 1):
            y = y0 + (y1 - y0) * mullion / mullion_count
            objects.append(
                bm(
                    f"{prefix}_ClerestoryMullion_{index}_{mullion:02d}",
                    (peak_x, y, peak_z),
                    (x1, y, valley_z),
                    0.048,
                    mats["steel"],
                    component="clerestory_vertical_steel_mullion",
                    role=role,
                )
            )
        # True valley gutter and rainwater leader datum.
        objects.append(
            bm(
                f"{prefix}_NorthlightValleyGutter_{index}",
                (x0, y0 - 0.20, valley_z + 0.05),
                (x0, y1 + 0.20, valley_z + 0.05),
                0.105,
                mats["galvanized"],
                component="continuous_northlight_valley_gutter",
                role=role,
            )
        )
        if detailed:
            for seam in range(1, 13):
                y = y0 + (y1 - y0) * seam / 13
                objects.append(
                    bm(
                        f"{prefix}_StandingSeam_{index}_{seam:02d}",
                        (x0 + 0.05, y, valley_z + 0.08),
                        (peak_x - 0.05, y, peak_z + 0.08),
                        0.026,
                        mats["galvanized"],
                        component="individual_zinc_standing_seam",
                        role=role,
                    )
                )
    if detailed:
        # Cross-section trusses at seven interior frames give the clerestories
        # believable support and remain visible through facade glazing.
        for frame, y in enumerate((-15.0, -10.0, -5.0, 0.0, 5.0, 10.0, 15.0)):
            for tooth in range(ROOF_TEETH):
                x0 = -BUILDING_WIDTH / 2 + tooth * TOOTH_WIDTH
                x1 = x0 + TOOTH_WIDTH
                peak_x = x0 + TOOTH_WIDTH * 0.80
                objects.extend(
                    [
                        bm(
                            f"{prefix}_RoofTrussTop_{frame}_{tooth}",
                            (x0, y, valley_z - 0.10),
                            (peak_x, y, peak_z - 0.14),
                            0.075,
                            mats["steel"],
                            component="visible_northlight_roof_truss",
                            role=role,
                        ),
                        bm(
                            f"{prefix}_RoofTrussChord_{frame}_{tooth}",
                            (x0, y, valley_z - 0.18),
                            (x1, y, valley_z - 0.18),
                            0.065,
                            mats["steel"],
                            component="visible_northlight_roof_truss",
                            role=role,
                        ),
                        bm(
                            f"{prefix}_RoofTrussDiagonal_{frame}_{tooth}",
                            (x0 + 0.35, y, valley_z - 0.18),
                            (peak_x - 0.20, y, peak_z - 0.24),
                            0.052,
                            mats["steel"],
                            component="visible_northlight_roof_truss",
                            role=role,
                        ),
                    ]
                )
        for index in range(ROOF_TEETH + 1):
            x = -BUILDING_WIDTH / 2 + index * TOOTH_WIDTH
            drain_faces = [("Rear", REAR_Y + 0.30, 1)]
            if index in (0, ROOF_TEETH):
                drain_faces.append(("Front", FRONT_Y - 0.30, -1))
            for facade_name, y, sign in drain_faces:
                objects.extend(
                    [
                        bm(
                            f"{prefix}_{facade_name}Downpipe_{index}",
                            (x, y, 0.60),
                            (x, y, valley_z - 0.08),
                            0.070,
                            mats["galvanized"],
                            component="working_rainwater_downpipe",
                            role=role,
                        ),
                        bm(
                            f"{prefix}_{facade_name}DownpipeShoe_{index}",
                            (x, y, 0.60),
                            (x, y + sign * 0.65, 0.34),
                            0.070,
                            mats["galvanized"],
                            component="rainwater_downpipe_shoe",
                            role=role,
                        ),
                    ]
                )
        # One restrained exhaust stack and two low ventilators.
        objects.append(
            c(
                f"{prefix}_FactoryExhaustStack",
                0.48,
                4.8,
                (23.3, 8.5, peak_z + 0.75),
                mats["galvanized"],
                vertices=24,
                component="restrained_factory_exhaust_stack",
                role=role,
            )
        )
        objects.append(
            c(
                f"{prefix}_FactoryExhaustCap",
                0.68,
                0.24,
                (23.3, 8.5, peak_z + 3.18),
                mats["steel"],
                vertices=24,
                component="factory_exhaust_rain_cap",
                role=role,
            )
        )
        for index, y in enumerate((-7.5, 7.5)):
            objects.append(
                c(
                    f"{prefix}_LowRoofVent_{index}",
                    0.32,
                    1.25,
                    (-21.5, y, peak_z + 0.20),
                    mats["galvanized"],
                    vertices=20,
                    component="low_roof_ventilator",
                    role=role,
                )
            )
    return objects


def build_assembled(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    objects.extend(add_site(mats, detailed=True))
    objects.extend(
        add_front_facade(
            mats,
            base_z=PODIUM_HEIGHT,
            detailed=True,
        )
    )
    objects.extend(
        add_side_facades(
            mats,
            base_z=PODIUM_HEIGHT,
            detailed=True,
        )
    )
    objects.extend(
        add_rear_facade(
            mats,
            base_z=PODIUM_HEIGHT,
            detailed=True,
        )
    )
    objects.extend(
        add_interior_structure(
            mats,
            base_z=PODIUM_HEIGHT,
            detailed=True,
        )
    )
    objects.extend(
        add_crown(
            mats,
            base_z=PODIUM_HEIGHT + FLOOR_HEIGHT,
            detailed=True,
        )
    )
    objects.extend(
        add_roof(
            mats,
            base_z=ROOF_VALLEY_Z,
            detailed=True,
        )
    )
    return objects


def normalize_bottom_origin(objects: list[bpy.types.Object]) -> None:
    minimum_z = min(
        (obj.matrix_world @ Vector(corner)).z
        for obj in objects
        for corner in obj.bound_box
    )
    for obj in objects:
        obj.location.z -= minimum_z


def evaluated_triangle_count(objects: list[bpy.types.Object]) -> int:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total = 0
    for obj in objects:
        if obj.type != "MESH":
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            total += sum(max(1, len(poly.vertices) - 2) for poly in mesh.polygons)
        finally:
            evaluated.to_mesh_clear()
    return total


def material_count(objects: list[bpy.types.Object]) -> int:
    return len(
        {
            slot.material.name
            for obj in objects
            for slot in obj.material_slots
            if slot.material
        }
    )


def build_module(
    role: str,
    variant: str,
    mats: dict[str, bpy.types.Material],
) -> tuple[list[bpy.types.Object], float]:
    prefix = f"MODULE_{role.upper()}_{variant.upper()}"
    if role == "podium":
        objects = add_site(mats, detailed=False, prefix=prefix)
        height = PODIUM_HEIGHT
    elif role == "floor":
        mullion_variant = {
            "typical_a": 0,
            "typical_b": 1,
            "typical_c": 2,
        }[variant]
        objects = []
        objects.extend(
            add_front_facade(
                mats,
                base_z=0.0,
                detailed=False,
                prefix=prefix,
                mullion_variant=mullion_variant,
            )
        )
        objects.extend(
            add_side_facades(
                mats,
                base_z=0.0,
                detailed=False,
                prefix=prefix,
            )
        )
        objects.extend(
            add_rear_facade(
                mats,
                base_z=0.0,
                detailed=False,
                prefix=prefix,
            )
        )
        height = FLOOR_HEIGHT
    elif role == "crown":
        objects = add_crown(
            mats,
            base_z=0.0,
            detailed=False,
            prefix=prefix,
        )
        height = CROWN_HEIGHT
    elif role == "roof":
        objects = add_roof(
            mats,
            base_z=0.0,
            detailed=False,
            prefix=prefix,
        )
        height = ROOF_HEIGHT
    else:
        raise ValueError(role)
    markers = module_contract_markers(role, variant, height)
    for marker in markers:
        tag_object(
            marker,
            "four_elevation_material_contract",
            role=role,
        )
    objects.extend(markers)
    return objects, height


def module_payload(
    role: str,
    variant: str,
    filename: str,
    height: float,
    objects: list[bpy.types.Object],
    size_bytes: int,
    skin: dict,
) -> dict:
    repeatable = role == "floor"
    return {
        "role": role,
        "variant_key": variant,
        "assembly_class": (
            "repeatable_middle" if repeatable else "fixed_semantic"
        ),
        "fixed_semantic": not repeatable,
        "lod": 0,
        "allowed_levels": [0, 1, 2],
        "filename": filename,
        "module_family": FAMILY,
        "width_m": NATIVE_WIDTH,
        "depth_m": NATIVE_DEPTH,
        "height_m": height,
        "floor_height_m": FLOOR_HEIGHT,
        "repeatable_z": repeatable,
        "allow_inset_footprint": True,
        "triangle_count": evaluated_triangle_count(objects),
        "material_count": material_count(objects),
        "texture_keys": sorted(skin["zones"]),
        "ao_baked": True,
        "size_bytes": size_bytes,
    }


def configure_render() -> list[bpy.types.Object]:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 920
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.image_settings.color_depth = "8"
    scene.render.resolution_percentage = 100
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.32
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.36, 0.45, 0.56, 1.0)
    background.inputs["Strength"].default_value = 0.65

    presentation: list[bpy.types.Object] = []
    ground_mat = material(
        "MAT_W10_DAYLIGHT_PresentationGround",
        (0.31, 0.31, 0.29, 1.0),
        0.86,
    )
    presentation.append(
        box(
            "PRESENTATION_DaylightGround",
            (180.0, 180.0, 0.10),
            (0.0, 0.0, -0.08),
            ground_mat,
        )
    )
    bpy.ops.object.light_add(
        type="SUN",
        location=(-70.0, -90.0, 95.0),
        rotation=(math.radians(31), math.radians(-18), math.radians(-38)),
    )
    sun = bpy.context.object
    sun.name = "PRESENTATION_DaylightSun"
    sun.data.energy = 1.25
    sun.data.angle = math.radians(7.0)
    sun.data.color = (1.0, 0.84, 0.68)
    presentation.append(sun)
    for name, location, energy, size, color in (
        (
            "PRESENTATION_DaylightKey",
            (-35.0, -48.0, 48.0),
            2100,
            24.0,
            (1.0, 0.82, 0.68),
        ),
        (
            "PRESENTATION_DaylightFill",
            (38.0, -5.0, 35.0),
            450,
            20.0,
            (0.67, 0.78, 1.0),
        ),
        (
            "PRESENTATION_DaylightRear",
            (0.0, 48.0, 28.0),
            600,
            18.0,
            (0.72, 0.82, 1.0),
        ),
    ):
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.name = name
        light.data.energy = energy
        light.data.shape = "DISK"
        light.data.size = size
        light.data.color = color
        aim_camera(location, (0.0, 0.0, 4.0), 50)
        # aim_camera creates/aims the scene camera, not the light. Orient area
        # lights explicitly along their local -Z axes.
        direction = Vector((0.0, 0.0, 4.0)) - light.location
        light.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        presentation.append(light)
    if scene.camera:
        presentation.append(scene.camera)
    return presentation


def render_views(
    folder: Path,
    *,
    view_set: str,
) -> list[str]:
    presentation = configure_render()
    views = {
        "preview": ((52.0, -73.0, 32.0), (0.0, -1.5, 4.2), 54),
        "street": ((45.0, -80.0, 20.0), (0.0, -2.0, 3.9), 58),
        "front_elevation": ((0.0, -103.0, 12.5), (0.0, -4.0, 4.1), 68),
        "rear_loading": ((-47.0, 74.0, 23.0), (0.0, 8.0, 3.4), 58),
        "aerial": ((58.0, -66.0, 69.0), (0.0, 0.0, 3.2), 55),
        "roof_close": ((43.0, -18.0, 30.0), (13.0, 1.0, 8.2), 66),
        "window_close": ((-17.0, -36.0, 7.0), (-16.0, -18.3, 3.3), 68),
        "entrance_close": ((0.0, -38.0, 6.8), (0.0, -19.2, 1.9), 70),
        "side": ((-70.0, -12.0, 17.0), (-20.0, 0.0, 4.0), 60),
    }
    if view_set == "preview":
        selected = ["preview"]
    elif view_set == "pilot":
        selected = [
            "preview",
            "street",
            "front_elevation",
            "rear_loading",
            "aerial",
            "roof_close",
            "window_close",
            "entrance_close",
        ]
    elif view_set == "all":
        selected = list(views)
    else:
        selected = [view_set]
    renders: list[str] = []
    for role in selected:
        location, target, lens = views[role]
        aim_camera(location, target, lens)
        bpy.context.scene.camera.data.clip_end = 500.0
        filename = f"{FAMILY}_{role}.png"
        bpy.context.scene.render.filepath = str(folder / filename)
        bpy.ops.render.render(write_still=True)
        renders.append(filename)
    canonical_aliases = {
        "front_corner_oblique": "preview",
        "rear_corner_oblique": "rear_loading",
        "facade_close": "window_close",
        "context": "street",
    }
    for canonical_role, source_role in canonical_aliases.items():
        source = folder / f"{FAMILY}_{source_role}.png"
        target = folder / f"{FAMILY}_{canonical_role}.png"
        if source.is_file():
            shutil.copyfile(source, target)
            if target.name not in renders:
                renders.append(target.name)
    delete_objects([obj for obj in presentation if obj and obj.name in bpy.data.objects])
    return renders


def footprint_contract() -> dict:
    rectangle = {
        "recommendedWidth_m": [40.0, 90.0],
        "recommendedDepth_m": [28.0, 55.0],
        "recommendedFloors": [1, 3],
        "preferredBayMultiple_m": TOOTH_WIDTH,
    }
    l_shape = {
        "recommendedWidth_m": [54.0, 118.0],
        "recommendedDepth_m": [40.0, 78.0],
        "recommendedFloors": [1, 3],
        "wingDepth_m": [18.0, 32.0],
        "preferredBayMultiple_m": TOOTH_WIDTH,
        "minimumCourtyard_m": 16.0,
    }
    u_shape = {
        "recommendedWidth_m": [66.0, 136.0],
        "recommendedDepth_m": [46.0, 88.0],
        "recommendedFloors": [1, 3],
        "wingDepth_m": [18.0, 32.0],
        "preferredBayMultiple_m": TOOTH_WIDTH,
        "minimumCourtyard_m": 18.0,
    }
    return {
        "preferredProfiles": ["rectangle", "l_shape", "u_shape"],
        "minimumPreferredProfiles": 3,
        "profileRationale": (
            "The identity is a repeatable 8.57 metre northlight structural bay. "
            "Rectangles preserve the complete seven-tooth hall; L and U drawings "
            "turn whole hall bars at brick service corners while retaining roof "
            "teeth, steel-sash openings and loading datums."
        ),
        "fixedLandmarkScaleBand": {
            "scaleMin": 0.70,
            "scaleMax": 1.36,
            "maxAxisRatio": 1.30,
        },
        "recommendedWidth_m": [40.0, 118.0],
        "recommendedDepth_m": [28.0, 78.0],
        "recommendedFloors": [1, 3],
        "wingDepth_m": [18.0, 32.0],
        "preferredBayMultiple_m": TOOTH_WIDTH,
        "minimumCourtyard_m": 16.0,
        "profiles": {
            "rectangle": rectangle,
            "l_shape": l_shape,
            "u_shape": u_shape,
        },
    }


def facade_sheet_contract(skin: dict) -> dict:
    contract = facade_contract(
        FAMILY,
        skin,
        f"/families/{FAMILY}/textures/source/archetype-goalpost.png",
    )
    contract["geometry_detail_profile"] = "hero"
    contract["bay_strategy"] = {
        "fixed_end_bays": [
            "projecting_administration_vestibule",
            "three_recessed_loading_docks",
        ],
        "repeatable_middle_bays": list(range(ROOF_TEETH)),
        "middle_variants": ["typical_a", "typical_b", "typical_c"],
        "rule": (
            "Repeat complete 8.57 metre northlight structural bays. Keep the "
            "opaque slope, steep clerestory, frame, truss, gutter and facade "
            "pier/window registration together; never stretch one tooth or pane."
        ),
    }
    contract["assembly_contract"] = {
        "fixed": [
            "podium/entrance",
            "corner returns",
            "crown",
            "roof",
            "administration vestibule",
            "three loading docks and stairs",
        ],
        "repeatable": ["typical_a", "typical_b", "typical_c"],
        "side_elevations": (
            "The front carries ten occupied segmental-arched steel-sash windows "
            "and a projecting administration entry; returns carry five deep "
            "industrial windows each; the rear is a working loading wall."
        ),
        "elevation_coverage": {
            "front": "ten physical steel-sash windows and administration vestibule",
            "left": "five deep industrial windows and brick return",
            "right": "five deep industrial windows and brick return",
            "rear": "three recessed docks, personnel doors, stairs and louvers",
            "roof": "seven zinc slopes, seven clerestories, trusses and drainage",
        },
        "variation_policy": (
            "Scale complete hall assemblies only inside 0.70-1.36 with an "
            "independent-axis ratio no greater than 1.30. Larger targets use "
            "long-axis streetwall repeat of whole northlight bays."
        ),
    }
    return contract


def build_modules(
    folder: Path,
    mats: dict[str, bpy.types.Material],
    skin: dict,
) -> list[dict]:
    specs = (
        ("podium", "default"),
        ("floor", "typical_a"),
        ("floor", "typical_b"),
        ("floor", "typical_c"),
        ("crown", "crown"),
        ("roof", "default"),
    )
    payloads: list[dict] = []
    for role, variant in specs:
        objects, height = build_module(role, variant, mats)
        normalize_bottom_origin(objects)
        suffix = role if variant == "default" else f"{role}_{variant}"
        filename = f"{FAMILY}_{suffix}.glb"
        destination = folder / filename
        export_glb(destination, objects)
        payloads.append(
            module_payload(
                role,
                variant,
                filename,
                height,
                objects,
                destination.stat().st_size,
                skin,
            )
        )
        delete_objects(objects)
    return payloads


def build_family(
    output_root: Path,
    *,
    view_set: str,
    skip_renders: bool,
    skip_modules: bool,
    skip_assembled_export: bool,
) -> None:
    clear_scene()
    folder = output_root / FAMILY
    folder.mkdir(parents=True, exist_ok=True)
    mats, skin = load_palette(folder)
    objects = build_assembled(mats)
    normalize_bottom_origin(objects)
    assembled_path = folder / f"{FAMILY}_assembled.glb"
    manifest_path = folder / f"{FAMILY}_manifest.json"
    previous = (
        json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest_path.is_file()
        else {}
    )
    if not skip_assembled_export:
        export_glb(assembled_path, objects)
        assembled_triangles = evaluated_triangle_count(objects)
        assembled_materials = material_count(objects)
    else:
        assembled_triangles = int(
            (previous.get("assembled") or {}).get("triangle_count")
            or evaluated_triangle_count(objects)
        )
        assembled_materials = int(
            (previous.get("assembled") or {}).get("material_count")
            or material_count(objects)
        )
    renders = (
        list(previous.get("renders") or [])
        if skip_renders
        else render_views(folder, view_set=view_set)
    )
    delete_objects(objects)
    modules = (
        list(previous.get("modules") or [])
        if skip_modules
        else build_modules(folder, mats, skin)
    )
    footprint = footprint_contract()
    massing_graph = {
        "type": "modular_northlight_factory_hall",
        "silhouette": "seven_repeating_asymmetric_sawtooth_roof_bays",
        "northlight_roof_teeth": 7,
        "physical_clerestory_assemblies": 7,
        "front_steel_sash_window_openings": 10,
        "side_steel_sash_window_openings": 10,
        "projecting_administration_entries": 1,
        "recessed_loading_docks": 3,
        "integrated_loading_stair_runs": 2,
        "interior_column_rows": 5,
        "roof_truss_frames": 7,
        "rainwater_downpipes": 10,
        "factory_exhaust_stacks": 1,
    }
    assembled = {
        "filename": assembled_path.name,
        "floors": NATIVE_FLOORS,
        "uses_setback": False,
        "uses_crown": True,
        "height_m": NATIVE_HEIGHT,
        "triangle_count": assembled_triangles,
        "material_count": assembled_materials,
        "stack": [
            {
                "role": "assembled",
                "variant_key": "reference_locked",
                "level": 0,
                "z_m": 0.0,
                "height_m": NATIVE_HEIGHT,
            }
        ],
        "footprint_profile": "rectangle",
        "footprint_target": {
            "width_m": NATIVE_WIDTH,
            "depth_m": NATIVE_DEPTH,
            "wing_depth_m": BUILDING_DEPTH,
            "segments": [
                {
                    "id": "seven_bay_northlight_hall",
                    "centre_x_m": 0.0,
                    "centre_y_m": 0.0,
                    "length_m": BUILDING_WIDTH,
                    "thickness_m": BUILDING_DEPTH,
                    "rotation_degrees": 0.0,
                },
                {
                    "id": "projecting_administration_vestibule",
                    "centre_x_m": 0.0,
                    "centre_y_m": FRONT_Y - 1.1,
                    "length_m": 5.62,
                    "thickness_m": 2.28,
                    "rotation_degrees": 0.0,
                },
            ],
        },
        "massing_graph": massing_graph,
        "texture_keys": sorted(skin["zones"]),
        "ao_baked": True,
    }
    manifest = {
        "manifest_schema": 3,
        "grammar_schema_version": 3,
        "generator": {
            "name": "archetype_compiler/generate_wave10_daylight_factory_family.py",
            "version": "1.0.0",
            "blender_version": bpy.app.version_string,
            "render_engine": "BLENDER_EEVEE",
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "family": FAMILY,
        "archetype_id": ARCHETYPE_ID,
        "archetype_label": LABEL,
        "variant_id": VARIANT_ID,
        "generation_archetype_id": VARIANT_ID,
        "archetype_aliases": ALIASES,
        "aesthetic_category_id": "industrial_heritage",
        "development_type": "industrial_light",
        "reuse_keys": [
            *ALIASES,
            "Daylight Factory",
            "Sawtooth Roof Factory",
            "Historic Brick Northlight Works",
            "Steel-Sash Industrial Hall",
        ],
        "generation_tags": [
            "wave10",
            "standard_building",
            "modular_industrial_hall",
            "custom_pbr_skin",
            "seven_physical_northlight_roof_teeth",
            "physical_segmental_arch_steel_sash_windows",
            "occupied_workshop_depth",
            "projecting_administration_entry",
            "three_working_loading_docks",
            "visible_roof_trusses_and_complete_drainage",
        ],
        "footprint_compatibility": footprint,
        "coordinate_contract": COORDINATE_CONTRACT,
        "textures": texture_inventory(skin),
        "facade_sheet": facade_sheet_contract(skin),
        "massing_graph": massing_graph,
        "material_budget": {
            "max_assembled_materials": 24,
            "rationale": (
                "Reference-specific fired brick, pale limestone, oxidized zinc, "
                "blackened steel, physical industrial glass, occupied workshop "
                "depth, dark-green loading doors, concrete, asphalt, timber, "
                "galvanized hardware, rubber and lighting retain distinct PBR "
                "responses because those differences carry the factory identity."
            ),
        },
        "dimensions": {
            "width_m": NATIVE_WIDTH,
            "depth_m": NATIVE_DEPTH,
            "podium_height_m": PODIUM_HEIGHT,
            "floor_height_m": FLOOR_HEIGHT,
            "setback_height_m": FLOOR_HEIGHT,
            "roof_height_m": ROOF_HEIGHT,
            "crown_height_m": CROWN_HEIGHT,
            "default_floors": NATIVE_FLOORS,
            "min_floors": MIN_FLOORS,
            "max_floors": MAX_FLOORS,
        },
        "native_width_m": NATIVE_WIDTH,
        "native_depth_m": NATIVE_DEPTH,
        "native_floors": NATIVE_FLOORS,
        "min_floors": MIN_FLOORS,
        "max_floors": MAX_FLOORS,
        "default_floors": NATIVE_FLOORS,
        "modules": modules,
        "assembled": assembled,
        "thumbnail": f"{FAMILY}_preview.png",
        "renders": renders,
        "architectural_identity": (
            "A long red-brown brick industrial hall is defined by exactly seven "
            "asymmetric zinc-and-glass northlight roof teeth, deep segmental-"
            "arched steel-sash windows, a modest projecting administration "
            "vestibule and a complete three-bay rear loading court."
        ),
        "material_zones": (
            "varied red-brown fired common brick and recessed lime mortar; pale "
            "cut-limestone plinth and sills; oxidized blue-grey standing-seam "
            "zinc roof slopes; blackened rolled-steel sash and roof trusses; "
            "physical blue-grey low-iron industrial glazing; occupied workshop "
            "depth and warm task lighting; dark-green sectional loading doors; "
            "broom-finish concrete; aged asphalt; galvanized drainage and stairs"
        ),
        "glass_profile": GLASS_PROFILE,
        "source_provenance": {
            "catalogue_archetype_id": ARCHETYPE_ID,
            "catalogue_variant_id": VARIANT_ID,
            "catalogue_alias_ids": ALIASES[2:],
            "elevation_source": f"/families/{FAMILY}/elevation.jpg",
            "goalpost": f"/families/{FAMILY}/textures/source/archetype-goalpost.png",
            "reference_generation": (
                f"/families/{FAMILY}/textures/source/reference-generation.json"
            ),
            "method": (
                "reference-locked four-view ImageGen source board, six-zone "
                "orthographic construction plate, deterministic metric brick "
                "wall construction around physical openings, separate northlight "
                "roof slopes and clerestories, modeled occupied depth, complete "
                "loading-court hardware, roof structure and drainage"
            ),
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    grammar = {
        "family_id": FAMILY,
        "source": {
            "archetype_id": ARCHETYPE_ID,
            "variant_id": VARIANT_ID,
            "generation_archetype_id": VARIANT_ID,
            "reuse_keys": manifest["reuse_keys"],
        },
        "dimensions": manifest["dimensions"],
        "architectural_signature": {
            "identity": manifest["architectural_identity"],
            "material_zones": manifest["material_zones"],
            "glass_profile": manifest["glass_profile"],
            "kits": [
                "reference_locked_seven_tooth_factory_hall",
                "physical_segmental_arch_steel_sash_bays",
                "northlight_clerestory_and_truss_assemblies",
                "projecting_administration_entry",
                "complete_loading_court_and_drainage",
                "flexible_semantic_stack",
            ],
        },
        "archetype_aliases": ALIASES,
        "footprint_compatibility": footprint,
        "massing_graph": massing_graph,
    }
    (folder / "grammar.json").write_text(
        json.dumps(grammar, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (folder / "archetype-source.json").write_text(
        json.dumps(manifest["source_provenance"], indent=2, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    print(
        f"[wave10-daylight-factory] {FAMILY}: "
        f"{assembled_triangles} triangles, {assembled_materials} materials, "
        f"{len(modules)} modules, {len(renders)} renders",
        flush=True,
    )


def render_existing(output_root: Path, *, view_set: str) -> None:
    clear_scene()
    folder = output_root / FAMILY
    _mats, _skin = load_palette(folder)
    manifest_path = folder / f"{FAMILY}_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    bpy.ops.import_scene.gltf(
        filepath=str(folder / manifest["assembled"]["filename"])
    )
    render_views(folder, view_set=view_set)
    manifest["renders"] = sorted(
        path.name
        for path in folder.glob(f"{FAMILY}_*.png")
        if path.is_file()
    )
    if (folder / "elevation.jpg").is_file():
        manifest["renders"].append("elevation.jpg")
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"[wave10-daylight-factory-render] "
        f"{FAMILY}: {len(manifest['renders'])} renders"
    )


def main() -> int:
    args = parse_args()
    output_root = args.output_root.resolve()
    if args.render_existing:
        render_existing(output_root, view_set=args.view_set)
    else:
        build_family(
            output_root,
            view_set=args.view_set,
            skip_renders=args.skip_renders,
            skip_modules=args.skip_modules,
            skip_assembled_export=args.skip_assembled_export,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
