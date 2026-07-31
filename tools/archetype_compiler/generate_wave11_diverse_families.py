"""Author the Wave 11 reference-locked diverse LEGO families.

The first family is a three-level white Mediterranean coastal resort.  Its
fixed landmark owns the cascading terraces, real infinity-pool section,
shuttered French-door openings, open iron guards, pergolas, roof terraces,
stone service base and planting.  The fallback stack repeats only ordinary
room bays so hand-drawn parcel variation never stretches the landmark.

Run with Blender 5.x from the repository root:

    blender --background --factory-startup --python \
      tools/archetype_compiler/generate_wave11_diverse_families.py -- \
      --family coastal-mediterranean-resort \
      --output-root frontend/public/families --view-set all
"""
from __future__ import annotations

import argparse
import json
import math
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
    sphere,
    texture_inventory,
)


FAMILY = "coastal-mediterranean-resort"
ARCHETYPE_ID = "coastal_resort_terrace_block"
VARIANT_ID = "coastal_resort_white_mediterranean"
ALIASES = [
    ARCHETYPE_ID,
    VARIANT_ID,
    "coastal_mediterranean_resort",
    "white_mediterranean_resort_block",
]
LABEL = "Coastal Resort Terrace Block — White Mediterranean"
GLASS_PROFILE = "coastal_residential_low_iron"

NATIVE_WIDTH = 40.0
NATIVE_DEPTH = 28.0
NATIVE_HEIGHT = 13.40
NATIVE_FLOORS = 3
MIN_FLOORS = 3
MAX_FLOORS = 8
PODIUM_HEIGHT = 0.45
FLOOR_HEIGHT = 3.80
CROWN_HEIGHT = 0.95
ROOF_HEIGHT = 1.70

BODY_WIDTH = 34.0
BODY_FRONT = -5.80
BODY_REAR = 9.00


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", choices=(FAMILY,), default=FAMILY)
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
            "front_elevation",
            "front_corner_oblique",
            "rear_corner_oblique",
            "aerial",
            "pool_close",
            "window_close",
            "facade_close",
            "street",
            "context",
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


def set_normal_strength(mat: bpy.types.Material, strength: float) -> bpy.types.Material:
    for node in mat.node_tree.nodes:
        if node.bl_idname == "ShaderNodeNormalMap":
            node.inputs["Strength"].default_value = strength
    return mat


def configure_glass(mat: bpy.types.Material) -> bpy.types.Material:
    bsdf = bsdf_for(mat)
    bsdf.inputs["Roughness"].default_value = 0.10
    if bsdf.inputs.get("Transmission Weight"):
        bsdf.inputs["Transmission Weight"].default_value = 0.72
    if bsdf.inputs.get("Coat Weight"):
        bsdf.inputs["Coat Weight"].default_value = 0.25
    if bsdf.inputs.get("Coat Roughness"):
        bsdf.inputs["Coat Roughness"].default_value = 0.06
    if bsdf.inputs.get("IOR"):
        bsdf.inputs["IOR"].default_value = 1.50
    if bsdf.inputs.get("Alpha"):
        bsdf.inputs["Alpha"].default_value = 0.50
    mat.diffuse_color = (0.29, 0.38, 0.40, 0.50)
    try:
        mat.surface_render_method = "BLENDED"
    except Exception:
        pass
    mat.use_backface_culling = False
    mat["glazing_profile"] = GLASS_PROFILE
    mat["glazing_lod"] = "physical_separate_pane"
    mat["pane_recess_m"] = 0.22
    mat["interior_depth_m"] = 0.75
    mat["source_variant_id"] = VARIANT_ID
    mat["generation_archetype_id"] = VARIANT_ID
    mat["reference_locked"] = True
    return mat


def load_palette(folder: Path) -> tuple[dict[str, bpy.types.Material], dict]:
    skin = load_skin_manifest(folder)
    if not skin:
        raise FileNotFoundError(folder / "textures" / "skin_manifest.json")
    near = {zone: values["near"] for zone, values in skin["zones"].items()}

    def pbr(
        key: str,
        name: str,
        *,
        metallic: float = 0.0,
        transmission: float = 0.0,
        emission_strength: float = 0.0,
        saturation: float = 1.0,
        value: float = 1.0,
        normal: float = 0.52,
    ) -> bpy.types.Material:
        result = skin_material(
            name,
            folder,
            near[key],
            key,
            metallic=metallic,
            transmission=transmission,
            emission_strength=emission_strength,
        )
        result = grade_material(result, saturation=saturation, value=value)
        result = set_normal_strength(result, normal)
        result["source_variant_id"] = VARIANT_ID
        result["generation_archetype_id"] = VARIANT_ID
        result["reference_locked"] = True
        return result

    mats = {
        "stucco": pbr(
            "stucco",
            "MAT_W11_COASTAL_HandTrowelledLimeStucco",
            saturation=0.64,
            value=0.88,
            normal=0.38,
        ),
        "stone": pbr(
            "stone",
            "MAT_W11_COASTAL_PaleRubbleLimestone",
            saturation=0.72,
            value=0.80,
            normal=0.68,
        ),
        "blue": pbr(
            "blue_timber",
            "MAT_W11_COASTAL_WeatheredAegeanBlueTimber",
            saturation=0.86,
            value=0.78,
            normal=0.45,
        ),
        "iron": pbr(
            "wrought_iron",
            "MAT_W11_COASTAL_BlackWroughtIron",
            metallic=0.52,
            saturation=0.26,
            value=0.27,
            normal=0.25,
        ),
        "paving": pbr(
            "paving",
            "MAT_W11_COASTAL_HonedPoolLimestone",
            saturation=0.46,
            value=0.88,
            normal=0.28,
        ),
        "roof": pbr(
            "roof",
            "MAT_W11_COASTAL_PaleFlatRoofMembrane",
            saturation=0.38,
            value=0.76,
            normal=0.20,
        ),
        "interior": pbr(
            "interior",
            "MAT_W11_COASTAL_OccupiedResortRoom",
            emission_strength=0.28,
            saturation=0.75,
            value=0.82,
            normal=0.12,
        ),
    }
    mats["glass"] = configure_glass(
        pbr(
            "glass",
            "MAT_W11_COASTAL_NeutralLowIronResidentialGlass",
            transmission=0.60,
            emission_strength=0.01,
            saturation=0.45,
            value=0.90,
            normal=0.10,
        )
    )
    mats["window_frame"] = pbr(
        "paving",
        "MAT_W11_COASTAL_WarmWhitePaintedWindowFrame",
        saturation=0.24,
        value=0.96,
        normal=0.12,
    )
    water = material(
        "MAT_W11_COASTAL_InfinityPoolWater",
        (0.075, 0.37, 0.47, 0.64),
        0.12,
    )
    water_bsdf = bsdf_for(water)
    if water_bsdf.inputs.get("Transmission Weight"):
        water_bsdf.inputs["Transmission Weight"].default_value = 0.58
    if water_bsdf.inputs.get("IOR"):
        water_bsdf.inputs["IOR"].default_value = 1.333
    if water_bsdf.inputs.get("Coat Weight"):
        water_bsdf.inputs["Coat Weight"].default_value = 0.22
    nodes = water.node_tree.nodes
    links = water.node_tree.links
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 2.8
    noise.inputs["Detail"].default_value = 2.2
    noise.inputs["Roughness"].default_value = 0.55
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.16
    bump.inputs["Distance"].default_value = 0.055
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], water_bsdf.inputs["Normal"])
    water["skin_zone"] = "water"
    water["glazing_profile"] = "shallow_pool_water"
    water["source_variant_id"] = VARIANT_ID
    water["generation_archetype_id"] = VARIANT_ID
    water["reference_locked"] = True
    mats["water"] = water
    mats["olive"] = material(
        "MAT_W11_COASTAL_OliveLeaves",
        (0.21, 0.29, 0.12, 1.0),
        0.74,
    )
    mats["olive_alt"] = material(
        "MAT_W11_COASTAL_OliveLeavesSilver",
        (0.31, 0.38, 0.22, 1.0),
        0.76,
    )
    mats["trunk"] = material(
        "MAT_W11_COASTAL_OliveWood",
        (0.24, 0.17, 0.10, 1.0),
        0.82,
    )
    mats["flower"] = material(
        "MAT_W11_COASTAL_Bougainvillea",
        (0.52, 0.035, 0.24, 1.0),
        0.66,
    )
    mats["flower_alt"] = material(
        "MAT_W11_COASTAL_BougainvilleaLight",
        (0.78, 0.075, 0.36, 1.0),
        0.64,
    )
    mats["vine_leaf"] = material(
        "MAT_W11_COASTAL_BougainvilleaLeaves",
        (0.18, 0.31, 0.10, 1.0),
        0.76,
    )
    mats["soil"] = material(
        "MAT_W11_COASTAL_PlanterSoil",
        (0.15, 0.105, 0.065, 1.0),
        0.92,
    )
    return mats, skin


def tag_object(
    obj: bpy.types.Object,
    semantic: str,
    *,
    role: str = "assembled",
) -> bpy.types.Object:
    obj["semantic"] = semantic
    obj["module_role"] = role
    obj["source_variant_id"] = VARIANT_ID
    obj["generation_archetype_id"] = VARIANT_ID
    obj["reference_locked"] = True
    return obj


def metric_uv(obj: bpy.types.Object, tile_m: float = 2.4) -> None:
    if obj.type != "MESH" or not obj.data.polygons:
        return
    layer = obj.data.uv_layers.active or obj.data.uv_layers.new(name="UVMap")
    for poly in obj.data.polygons:
        normal = poly.normal
        for loop_index in poly.loop_indices:
            co = obj.data.vertices[obj.data.loops[loop_index].vertex_index].co
            if abs(normal.z) > 0.72:
                u, v = co.x / tile_m, co.y / tile_m
            elif abs(normal.y) > abs(normal.x):
                u, v = co.x / tile_m, co.z / tile_m
            else:
                u, v = co.y / tile_m, co.z / tile_m
            layer.data[loop_index].uv = (u, v)


def b(
    name: str,
    size: tuple[float, float, float],
    location: tuple[float, float, float],
    mat: bpy.types.Material,
    *,
    bevel: float = 0.035,
    semantic: str = "construction",
    role: str = "assembled",
    tile_m: float = 2.4,
) -> bpy.types.Object:
    obj = box(name, size, location, mat, bevel)
    metric_uv(obj, tile_m)
    return tag_object(obj, semantic, role=role)


def segmental_panel(
    name: str,
    centre_x: float,
    y: float,
    sill_z: float,
    width: float,
    height: float,
    rise: float,
    mat: bpy.types.Material,
    *,
    semantic: str,
    role: str = "assembled",
    segments: int = 20,
) -> bpy.types.Object:
    spring_z = sill_z + height - rise
    verts = [
        (centre_x - width / 2, y, sill_z),
        (centre_x + width / 2, y, sill_z),
        (centre_x + width / 2, y, spring_z),
    ]
    for index in range(1, segments):
        theta = index * math.pi / segments
        verts.append(
            (
                centre_x + width / 2 * math.cos(theta),
                y,
                spring_z + rise * math.sin(theta),
            )
        )
    verts.append((centre_x - width / 2, y, spring_z))
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], [tuple(range(len(verts)))])
    mesh.materials.append(mat)
    layer = mesh.uv_layers.new(name="UVMap")
    for loop_index, vertex_index in enumerate(mesh.polygons[0].vertices):
        x, _, z = verts[vertex_index]
        layer.data[loop_index].uv = (
            (x - (centre_x - width / 2)) / width,
            (z - sill_z) / height,
        )
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return tag_object(obj, semantic, role=role)


def add_segmental_frame(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    centre_x: float,
    y: float,
    sill_z: float,
    width: float,
    height: float,
    rise: float,
    mat: bpy.types.Material,
    role: str,
) -> None:
    profile = 0.058
    spring_z = sill_z + height - rise
    objects.extend(
        [
            b(
                f"{prefix}_FrameLeft",
                (profile, 0.12, height - rise),
                (centre_x - width / 2, y, sill_z + (height - rise) / 2),
                mat,
                bevel=0.012,
                semantic="painted_timber_window_frame",
                role=role,
                tile_m=1.0,
            ),
            b(
                f"{prefix}_FrameRight",
                (profile, 0.12, height - rise),
                (centre_x + width / 2, y, sill_z + (height - rise) / 2),
                mat,
                bevel=0.012,
                semantic="painted_timber_window_frame",
                role=role,
                tile_m=1.0,
            ),
            b(
                f"{prefix}_Threshold",
                (width + 0.18, 0.30, 0.095),
                (centre_x, y - 0.02, sill_z + 0.025),
                mat,
                bevel=0.018,
                semantic="painted_timber_threshold",
                role=role,
                tile_m=1.0,
            ),
            b(
                f"{prefix}_Transom",
                (width, 0.11, profile),
                (centre_x, y, spring_z),
                mat,
                bevel=0.010,
                semantic="painted_timber_transom",
                role=role,
                tile_m=1.0,
            ),
        ]
    )
    for division in (-0.25, 0.0, 0.25):
        objects.append(
            b(
                f"{prefix}_Mullion_{division:+.2f}",
                (profile * 0.82, 0.095, height - rise),
                (centre_x + width * division, y, sill_z + (height - rise) / 2),
                mat,
                bevel=0.010,
                semantic="painted_timber_mullion",
                role=role,
                tile_m=1.0,
            )
        )
    # Build the segmental head as one ribbon.  Discrete beam chords catch a
    # separate highlight at every joint and make an otherwise smooth opening
    # read as a staircase in close views.
    segments = 40
    outer_half = width / 2
    inner_half = max(outer_half - profile, profile)
    inner_rise = max(rise - profile, profile)
    verts: list[tuple[float, float, float]] = []
    for index in range(segments + 1):
        theta = index * math.pi / segments
        verts.extend(
            [
                (
                    centre_x + outer_half * math.cos(theta),
                    y - 0.025,
                    spring_z + rise * math.sin(theta),
                ),
                (
                    centre_x + inner_half * math.cos(theta),
                    y - 0.026,
                    spring_z + inner_rise * math.sin(theta),
                ),
            ]
        )
    faces = [
        (2 * index, 2 * index + 1, 2 * index + 3, 2 * index + 2)
        for index in range(segments)
    ]
    mesh = bpy.data.meshes.new(prefix + "_CurvedHeadMesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    obj = bpy.data.objects.new(prefix + "_CurvedHead", mesh)
    bpy.context.collection.objects.link(obj)
    solidify = obj.modifiers.new("Painted frame depth", "SOLIDIFY")
    solidify.thickness = 0.055
    solidify.offset = 0.0
    objects.append(tag_object(obj, "continuous_painted_timber_segmental_head", role=role))


def add_arch_infill(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    centre_x: float,
    front_y: float,
    width: float,
    spring_z: float,
    rise: float,
    top_z: float,
    mat: bpy.types.Material,
    role: str,
) -> None:
    # One continuous front face follows the architectural head.  Earlier
    # vertical filler strips made a technically curved opening read as a row of
    # white blocks at close range.
    y = front_y - 0.231
    verts = [
        (centre_x - width / 2, y, top_z),
        (centre_x + width / 2, y, top_z),
        (centre_x + width / 2, y, spring_z),
    ]
    segments = 48
    for index in range(1, segments):
        theta = index * math.pi / segments
        verts.append(
            (
                centre_x + width / 2 * math.cos(theta),
                y,
                spring_z + rise * math.sin(theta),
            )
        )
    verts.append((centre_x - width / 2, y, spring_z))
    mesh = bpy.data.meshes.new(prefix + "_ArchSpandrelMesh")
    mesh.from_pydata(verts, [], [tuple(range(len(verts)))])
    mesh.materials.append(mat)
    uv = mesh.uv_layers.new(name="UVMap")
    for loop_index, vertex_index in enumerate(mesh.polygons[0].vertices):
        x, _, z = verts[vertex_index]
        uv.data[loop_index].uv = (
            (x - (centre_x - width / 2)) / width,
            (z - spring_z) / max(rise, 0.001),
        )
    obj = bpy.data.objects.new(prefix + "_ArchSpandrel", mesh)
    bpy.context.collection.objects.link(obj)
    objects.append(tag_object(obj, "continuous_stucco_arch_spandrel", role=role))


def add_shutters(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    centre_x: float,
    y: float,
    sill_z: float,
    opening_width: float,
    height: float,
    mat: bpy.types.Material,
    role: str,
) -> None:
    panel_width = min(0.74, opening_width * 0.22)
    for side_index, side in enumerate((-1, 1)):
        x = centre_x + side * (opening_width / 2 + panel_width / 2 + 0.10)
        panel = b(
            f"{prefix}_Shutter_{side_index}",
            (panel_width, 0.11, height),
            (x, y, sill_z + height / 2),
            mat,
            bevel=0.025,
            semantic="operable_aegean_blue_shutter",
            role=role,
            tile_m=1.1,
        )
        panel.rotation_euler.z = math.radians(side * 4.0)
        objects.append(panel)
        for rail_index, fraction in enumerate((0.08, 0.50, 0.92)):
            objects.append(
                b(
                    f"{prefix}_ShutterRail_{side_index}_{rail_index}",
                    (panel_width + 0.025, 0.045, 0.050),
                    (x, y - 0.065, sill_z + height * fraction),
                    mat,
                    bevel=0.010,
                    semantic="shutter_frame_rail",
                    role=role,
                    tile_m=0.8,
                )
            )
        for slat_index in range(9):
            objects.append(
                b(
                    f"{prefix}_ShutterSlat_{side_index}_{slat_index:02d}",
                    (panel_width * 0.76, 0.036, 0.027),
                    (
                        x,
                        y - 0.075,
                        sill_z + 0.22 + slat_index * (height - 0.44) / 8,
                    ),
                    mat,
                    bevel=0.006,
                    semantic="open_shutter_louver",
                    role=role,
                    tile_m=0.8,
                )
            )


def add_balcony(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    centre_x: float,
    front_y: float,
    width: float,
    floor_z: float,
    mats: dict[str, bpy.types.Material],
    role: str,
) -> None:
    projection = 1.05
    outside_y = front_y - 0.25
    objects.append(
        b(
            f"{prefix}_Slab",
            (width + 0.55, projection, 0.18),
            (centre_x, outside_y - projection / 2 + 0.04, floor_z - 0.04),
            mats["paving"],
            bevel=0.035,
            semantic="thin_limestone_balcony_slab",
            role=role,
        )
    )
    rail_y = outside_y - projection + 0.04
    rail_top = floor_z + 1.02
    objects.extend(
        [
            b(
                f"{prefix}_TopRail",
                (width + 0.42, 0.055, 0.055),
                (centre_x, rail_y, rail_top),
                mats["iron"],
                bevel=0.010,
                semantic="open_wrought_iron_balcony_guard",
                role=role,
                tile_m=0.8,
            ),
            b(
                f"{prefix}_BottomRail",
                (width + 0.42, 0.045, 0.045),
                (centre_x, rail_y, floor_z + 0.16),
                mats["iron"],
                bevel=0.008,
                semantic="open_wrought_iron_balcony_guard",
                role=role,
                tile_m=0.8,
            ),
        ]
    )
    pickets = max(8, round((width + 0.3) / 0.28))
    for index in range(pickets + 1):
        x = centre_x - (width + 0.30) / 2 + index * (width + 0.30) / pickets
        objects.append(
            b(
                f"{prefix}_Picket_{index:02d}",
                (0.036, 0.040, 0.88),
                (x, rail_y, floor_z + 0.58),
                mats["iron"],
                bevel=0.006,
                semantic="open_wrought_iron_balcony_picket",
                role=role,
                tile_m=0.8,
            )
        )
    for side_index, x in enumerate((centre_x - width / 2 - 0.22, centre_x + width / 2 + 0.22)):
        objects.append(
            b(
                f"{prefix}_SideRail_{side_index}",
                (0.045, projection, 0.055),
                (x, outside_y - projection / 2 + 0.04, rail_top),
                mats["iron"],
                bevel=0.008,
                semantic="open_balcony_end_rail",
                role=role,
                tile_m=0.8,
            )
        )


def add_front_opening(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    spec: dict,
    front_y: float,
    z0: float,
    mats: dict[str, bpy.types.Material],
    role: str,
) -> None:
    centre_x = spec["x"]
    width = spec["width"]
    sill_z = z0 + spec.get("sill", 0.18)
    height = spec["height"]
    rise = spec.get("rise", 0.0)
    pane_y = front_y - 0.015
    room_y = front_y + 0.52
    if rise > 0:
        glass = segmental_panel(
            f"{prefix}_PhysicalGlass",
            centre_x,
            pane_y,
            sill_z,
            width,
            height,
            rise,
            mats["glass"],
            semantic="physical_low_iron_french_door_glass",
            role=role,
        )
        room = segmental_panel(
            f"{prefix}_OccupiedDepth",
            centre_x,
            room_y,
            sill_z + 0.02,
            width * 0.96,
            height * 0.96,
            rise * 0.96,
            mats["interior"],
            semantic="occupied_resort_room_depth",
            role=role,
        )
        objects.extend([glass, room])
    else:
        objects.extend(
            [
                b(
                    f"{prefix}_PhysicalGlass",
                    (width, 0.045, height),
                    (centre_x, pane_y, sill_z + height / 2),
                    mats["glass"],
                    bevel=0.012,
                    semantic="physical_low_iron_french_door_glass",
                    role=role,
                    tile_m=3.0,
                ),
                b(
                    f"{prefix}_OccupiedDepth",
                    (width * 0.96, 0.035, height * 0.94),
                    (centre_x, room_y, sill_z + height * 0.50),
                    mats["interior"],
                    bevel=0.010,
                    semantic="occupied_resort_room_depth",
                    role=role,
                    tile_m=3.0,
                ),
            ]
        )
    add_segmental_frame(
        objects,
        prefix=prefix,
        centre_x=centre_x,
        y=front_y - 0.095,
        sill_z=sill_z,
        width=width,
        height=height,
        rise=rise,
        mat=mats["window_frame"],
        role=role,
    )
    if spec.get("shutters", True):
        add_shutters(
            objects,
            prefix=prefix,
            centre_x=centre_x,
            y=front_y - 0.32,
            sill_z=sill_z,
            opening_width=width,
            height=max(1.9, height - rise * 0.35),
            mat=mats["blue"],
            role=role,
        )
    if spec.get("balcony"):
        add_balcony(
            objects,
            prefix=prefix,
            centre_x=centre_x,
            front_y=front_y,
            width=width,
            floor_z=sill_z,
            mats=mats,
            role=role,
        )


def add_storey_shell(
    *,
    prefix: str,
    width: float,
    front_y: float,
    rear_y: float,
    z0: float,
    height: float,
    openings: list[dict],
    mats: dict[str, bpy.types.Material],
    role: str = "assembled",
    rear_stone: bool = False,
    side_windows: bool = True,
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    wall_thickness = 0.45
    bounds = sorted(
        (spec["x"] - spec["width"] / 2, spec["x"] + spec["width"] / 2, spec)
        for spec in openings
    )
    cursor = -width / 2
    for index, (left, right, spec) in enumerate(bounds):
        if left - cursor > 0.04:
            objects.append(
                b(
                    f"{prefix}_FrontPier_{index:02d}",
                    (left - cursor, wall_thickness, height),
                    ((cursor + left) / 2, front_y, z0 + height / 2),
                    mats["stucco"],
                    semantic="continuous_front_stucco_pier",
                    role=role,
                )
            )
        sill = spec.get("sill", 0.18)
        if sill > 0.025:
            objects.append(
                b(
                    f"{prefix}_OpeningSillWall_{index:02d}",
                    (spec["width"], wall_thickness, sill),
                    (spec["x"], front_y, z0 + sill / 2),
                    mats["stucco"],
                    semantic="stucco_below_opening",
                    role=role,
                )
            )
        top = sill + spec["height"]
        if height - top > 0.03:
            objects.append(
                b(
                    f"{prefix}_OpeningHeader_{index:02d}",
                    (spec["width"], wall_thickness, height - top),
                    (spec["x"], front_y, z0 + top + (height - top) / 2),
                    mats["stucco"],
                    semantic="stucco_header_above_opening",
                    role=role,
                )
            )
        rise = spec.get("rise", 0.0)
        if rise > 0:
            spring_z = z0 + sill + spec["height"] - rise
            add_arch_infill(
                objects,
                prefix=f"{prefix}_Opening{index:02d}",
                centre_x=spec["x"],
                front_y=front_y,
                width=spec["width"],
                spring_z=spring_z,
                rise=rise,
                top_z=z0 + sill + spec["height"],
                mat=mats["stucco"],
                role=role,
            )
        add_front_opening(
            objects,
            prefix=f"{prefix}_Opening{index:02d}",
            spec=spec,
            front_y=front_y,
            z0=z0,
            mats=mats,
            role=role,
        )
        cursor = right
    if width / 2 - cursor > 0.04:
        objects.append(
            b(
                f"{prefix}_FrontPier_End",
                (width / 2 - cursor, wall_thickness, height),
                ((cursor + width / 2) / 2, front_y, z0 + height / 2),
                mats["stucco"],
                semantic="continuous_front_stucco_pier",
                role=role,
            )
        )
    depth = rear_y - front_y
    objects.extend(
        [
            b(
                f"{prefix}_LeftReturn",
                (wall_thickness, depth, height),
                (-width / 2, (front_y + rear_y) / 2, z0 + height / 2),
                mats["stucco"],
                semantic="wrapped_left_stucco_return",
                role=role,
            ),
            b(
                f"{prefix}_RightReturn",
                (wall_thickness, depth, height),
                (width / 2, (front_y + rear_y) / 2, z0 + height / 2),
                mats["stucco"],
                semantic="wrapped_right_stucco_return",
                role=role,
            ),
            b(
                f"{prefix}_RearWall",
                (width, wall_thickness, height),
                (0.0, rear_y, z0 + height / 2),
                mats["stucco"],
                semantic="quiet_rear_stucco_elevation",
                role=role,
            ),
            b(
                f"{prefix}_FloorSlab",
                (width, depth, 0.18),
                (0.0, (front_y + rear_y) / 2, z0 + 0.09),
                mats["paving"],
                semantic="occupied_floor_slab",
                role=role,
            ),
        ]
    )
    if rear_stone:
        objects.append(
            b(
                f"{prefix}_RearStoneVeneer",
                (width - 0.8, 0.10, min(2.45, height - 0.2)),
                (0.0, rear_y + 0.275, z0 + min(2.45, height - 0.2) / 2),
                mats["stone"],
                bevel=0.020,
                semantic="pale_rubble_stone_service_base",
                role=role,
                tile_m=1.6,
            )
        )
    if side_windows:
        side_y_positions = [front_y + depth * fraction for fraction in (0.28, 0.60, 0.82)]
        for side_index, x in enumerate((-width / 2 - 0.235, width / 2 + 0.235)):
            for window_index, y in enumerate(side_y_positions):
                window_width = 1.55
                window_height = min(2.05, height - 0.75)
                z = z0 + 0.55 + window_height / 2
                objects.append(
                    b(
                        f"{prefix}_SideGlass_{side_index}_{window_index}",
                        (0.045, window_width, window_height),
                        (x, y, z),
                        mats["glass"],
                        bevel=0.012,
                        semantic="recessed_side_resort_window",
                        role=role,
                        tile_m=2.4,
                    )
                )
                objects.append(
                    b(
                        f"{prefix}_SideRoom_{side_index}_{window_index}",
                        (0.035, window_width * 0.92, window_height * 0.90),
                        (x - (0.38 if side_index else -0.38), y, z),
                        mats["interior"],
                        bevel=0.010,
                        semantic="occupied_side_room_depth",
                        role=role,
                        tile_m=2.4,
                    )
                )
                for yoff in (-window_width / 2, 0.0, window_width / 2):
                    objects.append(
                        b(
                            f"{prefix}_SideFrameV_{side_index}_{window_index}_{yoff:+.2f}",
                            (0.11, 0.065, window_height + 0.12),
                            (x + (-0.045 if side_index == 0 else 0.045), y + yoff, z),
                            mats["blue"],
                            bevel=0.010,
                            semantic="blue_timber_side_frame",
                            role=role,
                            tile_m=1.0,
                        )
                    )
                for zoff in (-window_height / 2, window_height / 2):
                    objects.append(
                        b(
                            f"{prefix}_SideFrameH_{side_index}_{window_index}_{zoff:+.2f}",
                            (0.11, window_width + 0.12, 0.065),
                            (x + (-0.045 if side_index == 0 else 0.045), y, z + zoff),
                            mats["blue"],
                            bevel=0.010,
                            semantic="blue_timber_side_frame",
                            role=role,
                            tile_m=1.0,
                        )
                    )
    return objects


def add_pergola(
    *,
    prefix: str,
    centre: tuple[float, float],
    size: tuple[float, float],
    base_z: float,
    height: float,
    mat: bpy.types.Material,
    role: str = "assembled",
) -> list[bpy.types.Object]:
    cx, cy = centre
    width, depth = size
    objects: list[bpy.types.Object] = []
    for x_index, x in enumerate((cx - width / 2, cx + width / 2)):
        for y_index, y in enumerate((cy - depth / 2, cy + depth / 2)):
            objects.append(
                b(
                    f"{prefix}_Post_{x_index}_{y_index}",
                    (0.15, 0.15, height),
                    (x, y, base_z + height / 2),
                    mat,
                    bevel=0.018,
                    semantic="open_blue_timber_pergola_post",
                    role=role,
                    tile_m=1.2,
                )
            )
    roof_z = base_z + height
    for y_index, y in enumerate((cy - depth / 2, cy + depth / 2)):
        objects.append(
            b(
                f"{prefix}_Header_{y_index}",
                (width + 0.35, 0.18, 0.18),
                (cx, y, roof_z),
                mat,
                bevel=0.018,
                semantic="open_blue_timber_pergola_header",
                role=role,
                tile_m=1.2,
            )
        )
    slats = max(7, round(width / 0.65))
    for index in range(slats + 1):
        x = cx - width / 2 + index * width / slats
        objects.append(
            b(
                f"{prefix}_Rafter_{index:02d}",
                (0.11, depth + 0.55, 0.12),
                (x, cy, roof_z + 0.12),
                mat,
                bevel=0.012,
                semantic="open_blue_timber_pergola_rafter",
                role=role,
                tile_m=1.2,
            )
        )
    return objects


def add_open_guard(
    *,
    prefix: str,
    start_x: float,
    end_x: float,
    y: float,
    base_z: float,
    mat: bpy.types.Material,
    role: str = "assembled",
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    span = end_x - start_x
    objects.extend(
        [
            b(
                f"{prefix}_TopRail",
                (span, 0.055, 0.055),
                ((start_x + end_x) / 2, y, base_z + 1.02),
                mat,
                bevel=0.010,
                semantic="open_roof_terrace_guard",
                role=role,
                tile_m=0.8,
            ),
            b(
                f"{prefix}_BottomRail",
                (span, 0.045, 0.045),
                ((start_x + end_x) / 2, y, base_z + 0.15),
                mat,
                bevel=0.008,
                semantic="open_roof_terrace_guard",
                role=role,
                tile_m=0.8,
            ),
        ]
    )
    pickets = max(4, round(span / 0.30))
    for index in range(pickets + 1):
        x = start_x + index * span / pickets
        objects.append(
            b(
                f"{prefix}_Picket_{index:02d}",
                (0.036, 0.040, 0.90),
                (x, y, base_z + 0.58),
                mat,
                bevel=0.006,
                semantic="open_roof_terrace_picket",
                role=role,
                tile_m=0.8,
            )
        )
    return objects


def add_olive_tree(
    *,
    prefix: str,
    location: tuple[float, float, float],
    scale: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    x, y, z = location
    objects: list[bpy.types.Object] = []
    trunk = cylinder(
        f"{prefix}_Trunk",
        0.16 * scale,
        2.1 * scale,
        (x, y, z + 1.05 * scale),
        mats["trunk"],
        vertices=10,
    )
    objects.append(tag_object(trunk, "olive_tree_trunk"))
    for branch_index, angle in enumerate((0.25, 1.35, 2.65, 3.8, 5.0)):
        start = Vector((x, y, z + 1.45 * scale))
        end = start + Vector(
            (
                math.cos(angle) * 0.72 * scale,
                math.sin(angle) * 0.62 * scale,
                0.75 * scale,
            )
        )
        objects.append(
            tag_object(
                beam(
                    f"{prefix}_Branch_{branch_index}",
                    tuple(start),
                    tuple(end),
                    0.07 * scale,
                    mats["trunk"],
                ),
                "olive_tree_branch",
            )
        )
    clusters = []
    for index in range(17):
        angle = index * 2.399963
        radius = 0.25 + 0.72 * ((index % 5) / 4)
        clusters.append(
            (
                math.cos(angle) * radius,
                math.sin(angle) * radius * 0.76,
                1.95 + 0.16 * (index % 6),
            )
        )
    for index, (dx, dy, dz) in enumerate(clusters):
        foliage = sphere(
            f"{prefix}_Foliage_{index}",
            (0.29 + 0.045 * (index % 3)) * scale,
            (x + dx * scale, y + dy * scale, z + dz * scale),
            mats["olive" if index % 2 == 0 else "olive_alt"],
            (1.38, 0.82, 0.62),
            segments=12,
            rings=6,
        )
        objects.append(tag_object(foliage, "mediterranean_olive_foliage"))
    return objects


def add_bougainvillea(
    *,
    prefix: str,
    x: float,
    y: float,
    base_z: float,
    height: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    points = []
    point_count = 12
    for index in range(point_count):
        z = base_z + index * height / (point_count - 1)
        point = (
            x + math.sin(index * 1.17) * 0.27,
            y + math.cos(index * 0.91) * 0.045,
            z,
        )
        points.append(point)
        if index:
            objects.append(
                tag_object(
                    beam(
                        f"{prefix}_Vine_{index:02d}",
                        points[index - 1],
                        point,
                        0.026,
                        mats["trunk"],
                    ),
                    "integrated_bougainvillea_vine",
                )
            )
        if index and index % 2 == 0:
            branch_end = (
                point[0] + (0.34 if index % 4 else -0.34),
                y - 0.04,
                z + 0.22,
            )
            objects.append(
                tag_object(
                    beam(
                        f"{prefix}_SideBranch_{index:02d}",
                        point,
                        branch_end,
                        0.020,
                        mats["trunk"],
                    ),
                    "integrated_bougainvillea_branch",
                )
            )
        for leaf_index in range(3):
            angle = index * 1.7 + leaf_index * 2.1
            lateral = math.cos(angle) * (0.13 + leaf_index * 0.045)
            leaf = sphere(
                f"{prefix}_Leaf_{index:02d}_{leaf_index}",
                0.090 + 0.012 * ((index + leaf_index) % 2),
                (
                    point[0] + lateral,
                    y - 0.08 + math.sin(angle) * 0.055,
                    z + (leaf_index - 1) * 0.11,
                ),
                mats["vine_leaf"],
                (1.45, 0.48, 0.68),
                segments=10,
                rings=5,
            )
            objects.append(tag_object(leaf, "bougainvillea_leaf_cluster"))
        for bloom_index in range(4):
            angle = index * 1.31 + bloom_index * 1.57
            lateral = math.cos(angle) * (0.16 + 0.035 * (bloom_index % 2))
            bloom = sphere(
                f"{prefix}_Bloom_{index:02d}_{bloom_index}",
                0.072 + 0.015 * ((index + bloom_index) % 3),
                (
                    point[0] + lateral,
                    y - 0.11 + math.sin(angle) * 0.07,
                    z + (bloom_index - 1.5) * 0.095,
                ),
                mats["flower" if (index + bloom_index) % 2 == 0 else "flower_alt"],
                (1.0, 0.70, 0.82),
                segments=10,
                rings=5,
            )
            objects.append(tag_object(bloom, "magenta_bougainvillea_bloom"))
    return objects


def add_site_and_pool(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    objects.extend(
        [
            b(
                "COASTAL_SiteTerrace",
                (40.0, 28.0, 0.34),
                (0.0, 0.0, 0.17),
                mats["paving"],
                bevel=0.05,
                semantic="honed_limestone_site_terrace",
                tile_m=3.0,
            ),
            b(
                "COASTAL_RearRetainingWall",
                (39.2, 0.65, 2.0),
                (0.0, 13.15, 1.0),
                mats["stone"],
                bevel=0.045,
                semantic="pale_rubble_stone_retaining_wall",
                tile_m=1.8,
            ),
            b(
                "COASTAL_RightRetainingWall",
                (0.65, 10.0, 1.45),
                (19.25, 7.0, 0.725),
                mats["stone"],
                bevel=0.045,
                semantic="pale_rubble_stone_retaining_wall",
                tile_m=1.8,
            ),
        ]
    )
    pool_width = 22.0
    pool_depth = 4.40
    pool_centre_y = -9.72
    water_z = 0.83
    coping = 0.42
    wall_height = 0.72
    objects.extend(
        [
            b(
                "COASTAL_PoolFrontWall",
                (pool_width + coping * 2, coping, wall_height),
                (0.0, pool_centre_y - pool_depth / 2 - coping / 2, wall_height / 2),
                mats["paving"],
                bevel=0.035,
                semantic="infinity_pool_front_edge",
                tile_m=2.0,
            ),
            b(
                "COASTAL_PoolRearCoping",
                (pool_width + coping * 2, coping, 0.22),
                (0.0, pool_centre_y + pool_depth / 2 + coping / 2, water_z - 0.04),
                mats["paving"],
                bevel=0.035,
                semantic="pool_limestone_coping",
                tile_m=2.0,
            ),
            b(
                "COASTAL_PoolLeftCoping",
                (coping, pool_depth, 0.22),
                (-pool_width / 2 - coping / 2, pool_centre_y, water_z - 0.04),
                mats["paving"],
                bevel=0.035,
                semantic="pool_limestone_coping",
                tile_m=2.0,
            ),
            b(
                "COASTAL_PoolRightCoping",
                (coping, pool_depth, 0.22),
                (pool_width / 2 + coping / 2, pool_centre_y, water_z - 0.04),
                mats["paving"],
                bevel=0.035,
                semantic="pool_limestone_coping",
                tile_m=2.0,
            ),
            b(
                "COASTAL_PoolWater",
                (pool_width, pool_depth, 0.07),
                (0.0, pool_centre_y, water_z),
                mats["water"],
                bevel=0.015,
                semantic="physical_infinity_pool_water",
                tile_m=4.0,
            ),
            b(
                "COASTAL_PoolFloor",
                (pool_width - 0.30, pool_depth - 0.30, 0.10),
                (0.0, pool_centre_y, 0.29),
                mats["paving"],
                bevel=0.015,
                semantic="submerged_pool_limestone",
                tile_m=2.0,
            ),
        ]
    )
    step_count = 5
    for index in range(step_count):
        rise = 0.17 * (index + 1)
        run = 0.40
        objects.append(
            b(
                f"COASTAL_EntryStair_{index:02d}",
                (3.15, run, rise),
                (-14.55, -13.20 + run * (index + 0.5), rise / 2),
                mats["paving"],
                bevel=0.025,
                semantic="integrated_pool_terrace_entry_stair",
                tile_m=2.0,
            )
        )
    for x in (-12.7, 12.7):
        objects.append(
            b(
                f"COASTAL_PoolPlanter_{x:+.0f}",
                (1.50, 1.50, 0.78),
                (x, -8.0, 0.39),
                mats["stone"],
                bevel=0.08,
                semantic="stone_pool_terrace_planter",
                tile_m=1.6,
            )
        )
        objects.append(
            b(
                f"COASTAL_PoolPlanterSoil_{x:+.0f}",
                (1.25, 1.25, 0.08),
                (x, -8.0, 0.81),
                mats["soil"],
                bevel=0.02,
                semantic="planter_soil",
                tile_m=1.0,
            )
        )
    objects.extend(add_olive_tree(prefix="COASTAL_OliveLeft", location=(-12.7, -8.0, 0.84), scale=0.78, mats=mats))
    objects.extend(add_olive_tree(prefix="COASTAL_OliveRight", location=(12.7, -8.0, 0.84), scale=0.72, mats=mats))
    return objects


def build_assembled(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    objects = add_site_and_pool(mats)
    ground_openings = [
        {"x": -12.5, "width": 2.65, "height": 3.05, "sill": 0.20},
        {"x": -6.3, "width": 3.05, "height": 3.10, "sill": 0.15},
        {"x": 0.0, "width": 3.05, "height": 3.10, "sill": 0.15},
        {"x": 6.3, "width": 3.05, "height": 3.10, "sill": 0.15},
        {"x": 12.5, "width": 2.65, "height": 3.05, "sill": 0.20},
    ]
    second_openings = [
        {"x": -11.2, "width": 3.35, "height": 3.20, "sill": 0.32, "rise": 0.62, "balcony": True},
        {"x": -3.8, "width": 3.35, "height": 3.20, "sill": 0.32, "rise": 0.62, "balcony": True},
        {"x": 3.8, "width": 3.35, "height": 3.20, "sill": 0.32, "rise": 0.62, "balcony": True},
        {"x": 11.2, "width": 2.90, "height": 2.82, "sill": 0.38, "balcony": True},
    ]
    top_openings = [
        {"x": -7.2, "width": 1.85, "height": 2.40, "sill": 0.48},
        {"x": -1.0, "width": 3.60, "height": 2.75, "sill": 0.28},
        {"x": 6.4, "width": 2.60, "height": 2.58, "sill": 0.38},
    ]
    objects.extend(
        add_storey_shell(
            prefix="COASTAL_Ground",
            width=BODY_WIDTH,
            front_y=BODY_FRONT,
            rear_y=BODY_REAR,
            z0=0.35,
            height=3.70,
            openings=ground_openings,
            mats=mats,
            rear_stone=True,
        )
    )
    objects.extend(
        add_storey_shell(
            prefix="COASTAL_Second",
            width=31.5,
            front_y=-5.35,
            rear_y=8.55,
            z0=4.05,
            height=3.75,
            openings=second_openings,
            mats=mats,
        )
    )
    objects.extend(
        add_storey_shell(
            prefix="COASTAL_Top",
            width=23.0,
            front_y=-2.85,
            rear_y=7.55,
            z0=7.80,
            height=3.40,
            openings=top_openings,
            mats=mats,
        )
    )
    # Cascading terrace decks remain open and establish the silhouette.
    objects.extend(
        [
            b(
                "COASTAL_SecondTerraceLeft",
                (3.60, 12.6, 0.20),
                (-15.55, 1.30, 4.08),
                mats["paving"],
                semantic="second_level_cascading_terrace",
            ),
            b(
                "COASTAL_TopTerraceLeft",
                (4.40, 10.7, 0.20),
                (-13.65, 2.25, 7.82),
                mats["paving"],
                semantic="top_level_cascading_terrace",
            ),
            b(
                "COASTAL_TopTerraceRight",
                (4.40, 10.7, 0.20),
                (13.65, 2.25, 7.82),
                mats["paving"],
                semantic="top_level_cascading_terrace",
            ),
            b(
                "COASTAL_MainRoofDeck",
                (22.7, 10.1, 0.22),
                (0.0, 2.35, 11.22),
                mats["roof"],
                semantic="flat_parapeted_roof_terrace",
            ),
        ]
    )
    # Open guards at terrace edges; no opaque balcony slabs masquerade as railings.
    objects.extend(add_open_guard(prefix="COASTAL_TopGuardLeft", start_x=-15.8, end_x=-11.7, y=-2.98, base_z=7.84, mat=mats["iron"]))
    objects.extend(add_open_guard(prefix="COASTAL_TopGuardRight", start_x=11.7, end_x=15.8, y=-2.98, base_z=7.84, mat=mats["iron"]))
    objects.extend(add_open_guard(prefix="COASTAL_RoofGuard", start_x=-10.9, end_x=10.9, y=-2.98, base_z=11.25, mat=mats["iron"]))
    # Parapets wrap all exposed roof edges but stop at the open terrace fronts.
    objects.extend(
        [
            b("COASTAL_RoofRearParapet", (23.1, 0.34, 0.72), (0.0, 7.48, 11.58), mats["stucco"], semantic="white_roof_parapet"),
            b("COASTAL_RoofLeftParapet", (0.34, 10.3, 0.72), (-11.55, 2.35, 11.58), mats["stucco"], semantic="white_roof_parapet"),
            b("COASTAL_RoofRightParapet", (0.34, 10.3, 0.72), (11.55, 2.35, 11.58), mats["stucco"], semantic="white_roof_parapet"),
            b("COASTAL_Chimney", (0.72, 0.72, 2.10), (8.7, 6.25, 12.25), mats["stucco"], semantic="single_white_roof_chimney"),
            b("COASTAL_ChimneyCap", (0.94, 0.94, 0.16), (8.7, 6.25, 13.33), mats["paving"], bevel=0.035, semantic="limestone_chimney_cap"),
        ]
    )
    objects.extend(add_pergola(prefix="COASTAL_GroundPergola", centre=(-8.2, -6.45), size=(7.1, 2.3), base_z=0.83, height=3.00, mat=mats["blue"]))
    objects.extend(add_pergola(prefix="COASTAL_SecondPergola", centre=(10.4, -5.85), size=(6.0, 2.1), base_z=4.23, height=3.05, mat=mats["blue"]))
    objects.extend(add_pergola(prefix="COASTAL_RoofPergola", centre=(1.2, -2.10), size=(8.2, 4.1), base_z=11.24, height=1.65, mat=mats["blue"]))
    # Restrained reference-specific planting is integrated with the construction.
    objects.extend(add_bougainvillea(prefix="COASTAL_VineLeft", x=-5.05, y=-6.07, base_z=0.55, height=7.0, mats=mats))
    objects.extend(add_bougainvillea(prefix="COASTAL_VineCentre", x=2.05, y=-5.65, base_z=0.55, height=8.7, mats=mats))
    objects.extend(add_bougainvillea(prefix="COASTAL_VineRight", x=9.55, y=-5.62, base_z=0.55, height=6.5, mats=mats))
    objects.extend(add_olive_tree(prefix="COASTAL_RoofOliveLeft", location=(-8.4, 1.6, 11.28), scale=0.56, mats=mats))
    objects.extend(add_olive_tree(prefix="COASTAL_RoofOliveRight", location=(8.1, 4.7, 11.28), scale=0.53, mats=mats))
    return objects


def normalize_bottom_origin(objects: list[bpy.types.Object]) -> None:
    bpy.context.view_layer.update()
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
    objects: list[bpy.types.Object] = []
    if role == "podium":
        objects.extend(
            [
                b(
                    f"{prefix}_StonePlinth",
                    (34.0, 16.0, PODIUM_HEIGHT),
                    (0.0, 1.0, PODIUM_HEIGHT / 2),
                    mats["stone"],
                    semantic="fixed_stone_pool_terrace_podium",
                    role=role,
                    tile_m=1.8,
                ),
                b(
                    f"{prefix}_Threshold",
                    (7.0, 2.2, 0.18),
                    (0.0, -8.0, 0.36),
                    mats["paving"],
                    semantic="fixed_public_threshold",
                    role=role,
                    tile_m=2.0,
                ),
            ]
        )
        height = PODIUM_HEIGHT
    elif role == "floor":
        openings = []
        bay_centres = (-12.4, -6.2, 0.0, 6.2, 12.4)
        for index, x in enumerate(bay_centres):
            openings.append(
                {
                    "x": x,
                    "width": 2.75,
                    "height": 3.05,
                    "sill": 0.26,
                    "rise": 0.52 if variant == "typical_b" and index % 2 == 0 else 0.0,
                    "balcony": variant == "typical_b",
                    "shutters": variant != "typical_c" or index % 2 == 0,
                }
            )
        objects.extend(
            add_storey_shell(
                prefix=prefix,
                width=34.0,
                front_y=-7.0,
                rear_y=9.0,
                z0=0.0,
                height=FLOOR_HEIGHT,
                openings=openings,
                mats=mats,
                role=role,
                side_windows=True,
            )
        )
        height = FLOOR_HEIGHT
    elif role == "crown":
        objects.extend(
            [
                b(f"{prefix}_FrontParapet", (34.0, 0.38, CROWN_HEIGHT), (0.0, -7.0, CROWN_HEIGHT / 2), mats["stucco"], semantic="fixed_white_parapet_crown", role=role),
                b(f"{prefix}_RearParapet", (34.0, 0.38, CROWN_HEIGHT), (0.0, 9.0, CROWN_HEIGHT / 2), mats["stucco"], semantic="fixed_white_parapet_crown", role=role),
                b(f"{prefix}_LeftParapet", (0.38, 16.0, CROWN_HEIGHT), (-17.0, 1.0, CROWN_HEIGHT / 2), mats["stucco"], semantic="fixed_white_parapet_crown", role=role),
                b(f"{prefix}_RightParapet", (0.38, 16.0, CROWN_HEIGHT), (17.0, 1.0, CROWN_HEIGHT / 2), mats["stucco"], semantic="fixed_white_parapet_crown", role=role),
            ]
        )
        height = CROWN_HEIGHT
    elif role == "roof":
        objects.append(
            b(
                f"{prefix}_RoofDeck",
                (33.3, 15.3, 0.22),
                (0.0, 1.0, 0.11),
                mats["roof"],
                semantic="fixed_flat_roof_terrace",
                role=role,
            )
        )
        objects.extend(
            add_pergola(
                prefix=f"{prefix}_OpenPergola",
                centre=(0.0, -2.0),
                size=(8.0, 4.0),
                base_z=0.12,
                height=1.48,
                mat=mats["blue"],
                role=role,
            )
        )
        height = ROOF_HEIGHT
    else:
        raise ValueError(role)
    markers = module_contract_markers(role, variant, height)
    for marker in markers:
        tag_object(marker, "four_elevation_material_contract", role=role)
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
        "assembly_class": "repeatable_middle" if repeatable else "fixed_semantic",
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
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.10
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.46, 0.59, 0.72, 1.0)
    background.inputs["Strength"].default_value = 0.55
    presentation: list[bpy.types.Object] = []
    ground_mat = material(
        "MAT_W11_COASTAL_PresentationGround",
        (0.44, 0.42, 0.37, 1.0),
        0.90,
    )
    presentation.append(
        box(
            "PRESENTATION_CoastalGround",
            (150.0, 150.0, 0.10),
            (0.0, 0.0, -0.10),
            ground_mat,
            0.0,
        )
    )
    bpy.ops.object.light_add(
        type="SUN",
        location=(-70.0, -90.0, 95.0),
        rotation=(math.radians(31), math.radians(-18), math.radians(-38)),
    )
    sun = bpy.context.object
    sun.name = "PRESENTATION_CoastalSun"
    sun.data.color = (1.0, 0.83, 0.68)
    sun.data.energy = 2.25
    sun.data.angle = math.radians(8.0)
    presentation.append(sun)
    for name, location, energy, size, color in (
        ("Key", (-24.0, -34.0, 30.0), 5000, 12.0, (1.0, 0.78, 0.62)),
        ("Fill", (28.0, -12.0, 19.0), 2600, 10.0, (0.67, 0.80, 1.0)),
        ("Rim", (0.0, 30.0, 24.0), 4200, 9.0, (0.76, 0.86, 1.0)),
    ):
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.name = f"PRESENTATION_Coastal{name}"
        light.data.energy = energy
        light.data.shape = "DISK"
        light.data.size = size
        light.data.color = color
        aim = Vector((0.0, 0.0, 5.0)) - light.location
        light.rotation_euler = aim.to_track_quat("-Z", "Y").to_euler()
        presentation.append(light)
    return presentation


def render_views(folder: Path, *, view_set: str) -> list[str]:
    presentation = configure_render()
    views = {
        "preview": ((31.0, -39.0, 22.0), (0.0, -1.0, 5.5), 55),
        "front_corner_oblique": ((27.0, -34.0, 17.0), (0.0, -2.0, 5.4), 58),
        "front_elevation": ((0.0, -46.0, 8.3), (0.0, -2.0, 6.0), 62),
        "rear_corner_oblique": ((-28.0, 34.0, 17.0), (0.0, 2.5, 5.7), 58),
        "aerial": ((31.0, -35.0, 39.0), (0.0, 0.0, 3.6), 56),
        "pool_close": ((18.0, -29.0, 7.5), (0.0, -7.5, 2.3), 64),
        "window_close": ((-8.0, -18.0, 7.3), (-4.0, -5.6, 6.2), 72),
        "facade_close": ((-8.0, -18.0, 7.3), (-4.0, -5.6, 6.2), 72),
        "street": ((24.0, -44.0, 7.0), (0.0, -2.0, 5.2), 64),
        "context": ((44.0, -50.0, 28.0), (0.0, 0.0, 4.5), 52),
    }
    selected = {
        "preview": {"preview"},
        "pilot": {"preview", "front_corner_oblique", "front_elevation", "aerial", "window_close"},
        "all": set(views),
    }.get(view_set, {view_set})
    rendered: list[str] = []
    for role, (location, target, lens) in views.items():
        if role not in selected:
            continue
        aim_camera(location, target, lens)
        filename = f"{FAMILY}_{role}.png"
        bpy.context.scene.render.filepath = str(folder / filename)
        bpy.ops.render.render(write_still=True)
        rendered.append(filename)
    delete_objects(presentation)
    return rendered


def footprint_contract() -> dict:
    rectangle = {
        "recommendedWidth_m": [32.0, 48.0],
        "recommendedDepth_m": [22.0, 34.0],
        "recommendedFloors": [3, 8],
        "preferredBayMultiple_m": 6.2,
    }
    return {
        "preferredProfiles": ["rectangle"],
        "minimumPreferredProfiles": 1,
        "profileRationale": (
            "The selected coastal resort is one frontage-led composition: its "
            "pool, stair, three cascading terraces and public pergolas cannot be "
            "turned into L/U/courtyard bars without duplicating the entrance. "
            "Near-native rectangles preserve the fixed landmark; larger drawings "
            "repeat complete ordinary shuttered room bays along the long axis."
        ),
        "fixedLandmarkScaleBand": {
            "scaleMin": 0.82,
            "scaleMax": 1.20,
            "maxAxisRatio": 1.16,
        },
        "recommendedWidth_m": [32.0, 48.0],
        "recommendedDepth_m": [22.0, 34.0],
        "recommendedFloors": [3, 8],
        "preferredBayMultiple_m": 6.2,
        "profiles": {"rectangle": rectangle},
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
            "infinity_pool_and_entry_stair",
            "cascading_terrace_ends",
            "roof_pergola_and_chimney",
        ],
        "repeatable_middle_bays": [0, 1, 2, 3, 4],
        "middle_variants": ["typical_a", "typical_b", "typical_c"],
        "rule": (
            "Repeat complete 6.2 metre occupied room bays, including the wall "
            "pier, French-door cavity, blue shutters, glazing, room depth and "
            "optional iron balcony. Never stretch shutters, door leaves or guards."
        ),
    }
    contract["assembly_contract"] = {
        "fixed": [
            "podium/entrance",
            "corner returns",
            "crown",
            "roof",
            "pool podium and stair",
            "cascading end terraces",
            "roof parapets",
            "open pergolas",
            "chimney and planted roof assemblies",
        ],
        "repeatable": ["typical_a", "typical_b", "typical_c"],
        "side_elevations": (
            "The public front uses deeply recessed shuttered French doors and "
            "open iron balconies; side returns use quieter blue-framed windows; "
            "the rear sits on a pale rubble-stone service base."
        ),
        "elevation_coverage": {
            "front": "three stepped levels of shuttered occupied French doors, balconies and pergolas",
            "left": "quiet stucco return with blue-framed occupied openings",
            "right": "quiet stucco return with blue-framed occupied openings and stone wall",
            "rear": "rubble-stone service base, stucco upper walls and roof terraces",
            "roof": "open pergola, parapets, planted terraces and single chimney",
        },
        "variation_policy": (
            "Scale the complete landmark only inside 0.82-1.20 with an "
            "independent-axis ratio no greater than 1.16. Larger targets use "
            "long-axis streetwall repeat of complete room bays."
        ),
    }
    return contract


def build_modules(folder: Path, mats: dict[str, bpy.types.Material], skin: dict) -> list[dict]:
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
    folder = (output_root / FAMILY).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    mats, skin = load_palette(folder)
    objects = build_assembled(mats)
    normalize_bottom_origin(objects)
    assembled_path = folder / f"{FAMILY}_assembled.glb"
    manifest_path = folder / f"{FAMILY}_manifest.json"
    previous = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}
    if not skip_assembled_export:
        export_glb(assembled_path, objects)
        assembled_triangles = evaluated_triangle_count(objects)
        assembled_materials = material_count(objects)
    else:
        assembled_triangles = int((previous.get("assembled") or {}).get("triangle_count") or evaluated_triangle_count(objects))
        assembled_materials = int((previous.get("assembled") or {}).get("material_count") or material_count(objects))
    if skip_renders:
        renders = list(previous.get("renders") or [])
        facade_close = f"{FAMILY}_facade_close.png"
        if (folder / facade_close).is_file() and facade_close not in renders:
            renders.append(facade_close)
    else:
        renders = render_views(folder, view_set=view_set)
    delete_objects(objects)
    modules = list(previous.get("modules") or []) if skip_modules else build_modules(folder, mats, skin)
    footprint = footprint_contract()
    massing_graph = {
        "type": "fixed_cascading_coastal_resort_with_repeatable_room_bays",
        "silhouette": "three_cascading_flat_roof_terraces_behind_front_infinity_pool",
        "occupied_storeys": 3,
        "principal_french_door_openings": 12,
        "segmental_arched_balcony_openings": 3,
        "physical_blue_shutter_leaves": 24,
        "open_wrought_iron_balcony_guards": 4,
        "open_blue_timber_pergolas": 3,
        "infinity_pool_basins": 1,
        "integrated_entry_stair_runs": 1,
        "flat_roof_terraces": 5,
        "white_roof_chimneys": 1,
        "rubble_stone_service_elevations": 1,
    }
    assembled = {
        "filename": assembled_path.name,
        "module_family": FAMILY,
        "assembly_class": "fixed_landmark",
        "fixed_semantic": True,
        "repeatable_z": False,
        "source_variant_id": VARIANT_ID,
        "generation_archetype_id": VARIANT_ID,
        "width_m": NATIVE_WIDTH,
        "depth_m": NATIVE_DEPTH,
        "floors": NATIVE_FLOORS,
        "uses_setback": True,
        "uses_crown": True,
        "height_m": NATIVE_HEIGHT,
        "triangle_count": assembled_triangles,
        "material_count": assembled_materials,
        "stack": [{"role": "assembled", "variant_key": "reference_locked", "level": 0, "z_m": 0.0, "height_m": NATIVE_HEIGHT}],
        "footprint_profile": "rectangle",
        "footprint_target": {
            "width_m": NATIVE_WIDTH,
            "depth_m": NATIVE_DEPTH,
            "wing_depth_m": BODY_REAR - BODY_FRONT,
            "segments": [
                {"id": "three_level_resort_body", "centre_x_m": 0.0, "centre_y_m": 1.6, "length_m": BODY_WIDTH, "thickness_m": BODY_REAR - BODY_FRONT, "rotation_degrees": 0.0},
                {"id": "front_infinity_pool_terrace", "centre_x_m": 0.0, "centre_y_m": -9.7, "length_m": 23.0, "thickness_m": 5.2, "rotation_degrees": 0.0},
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
            "name": "archetype_compiler/generate_wave11_diverse_families.py",
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
        "aesthetic_category_id": "coastal_mediterranean",
        "development_type": "hotel",
        "reuse_keys": [
            *ALIASES,
            "Coastal Resort Terrace Block",
            "White Mediterranean Resort",
            "Boutique Coastal Hotel",
            "Terraced Resort",
        ],
        "generation_tags": [
            "wave11",
            "hospitality",
            "fixed_landmark_and_modular_fallback",
            "custom_pbr_skin",
            "cascading_terraces",
            "physical_infinity_pool",
            "real_french_door_openings",
            "physical_operable_shutters",
            "open_wrought_iron_guards",
            "open_timber_pergolas",
            "occupied_residential_glazing",
        ],
        "footprint_compatibility": footprint,
        "coordinate_contract": COORDINATE_CONTRACT,
        "textures": texture_inventory(skin),
        "facade_sheet": facade_sheet_contract(skin),
        "massing_graph": massing_graph,
        "material_budget": {
            "max_assembled_materials": 22,
            "rationale": (
                "Reference-specific lime stucco, rubble limestone, painted blue "
                "timber, wrought iron, honed pool stone, physical low-iron glass, "
                "occupied room depth, pool water and restrained planting retain "
                "distinct PBR responses because those differences carry the resort identity."
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
        "native_height_m": NATIVE_HEIGHT,
        "native_floors": NATIVE_FLOORS,
        "min_floors": MIN_FLOORS,
        "max_floors": MAX_FLOORS,
        "default_floors": NATIVE_FLOORS,
        "modules": modules,
        "assembled": assembled,
        "thumbnail": f"{FAMILY}_preview.png",
        "renders": renders,
        "architectural_identity": (
            "A three-level white Mediterranean resort cascades toward one long "
            "front infinity pool through irregular lime-stucco terraces, deep "
            "blue-shuttered French doors, open iron balconies and pergolas, with "
            "a quieter pale-stone service rear and planted flat roof terraces."
        ),
        "material_zones": (
            "imperfect warm-white hand-trowelled lime stucco; pale local rubble "
            "limestone and recessed mortar; weathered Aegean-blue painted timber; "
            "nearly black wrought iron; honed pale pool limestone; physical neutral "
            "low-iron residential glazing; warm occupied room depth; shallow blue-"
            "green pool water; olive foliage and restrained magenta bougainvillea"
        ),
        "glass_profile": GLASS_PROFILE,
        "source_provenance": {
            "catalogue_archetype_id": ARCHETYPE_ID,
            "catalogue_variant_id": VARIANT_ID,
            "catalogue_alias_ids": ALIASES[2:],
            "elevation_source": f"/families/{FAMILY}/elevation.jpg",
            "goalpost": f"/families/{FAMILY}/textures/source/archetype-goalpost.png",
            "reference_generation": f"/families/{FAMILY}/textures/source/reference-generation.json",
            "method": (
                "reference-locked four-view ImageGen source board, six-zone "
                "shadow-neutral construction plate, deterministic metric walls "
                "split around physical French-door voids, layered glazing and "
                "occupied depth, open shutters/guards/pergolas, complete pool "
                "section, cascading terraces, wrapped secondary elevations and roof"
            ),
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
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
                "reference_locked_cascading_resort_landmark",
                "physical_shuttered_french_door_bays",
                "open_wrought_iron_balcony_system",
                "open_blue_timber_pergolas",
                "infinity_pool_and_entry_stair",
                "flexible_semantic_room_bay_stack",
            ],
        },
        "archetype_aliases": ALIASES,
        "footprint_compatibility": footprint,
        "massing_graph": massing_graph,
    }
    (folder / "grammar.json").write_text(json.dumps(grammar, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (folder / "archetype-source.json").write_text(json.dumps(manifest["source_provenance"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"[wave11] {FAMILY}: {assembled_triangles} triangles, "
        f"{assembled_materials} materials, {len(modules)} modules, "
        f"{len(renders)} renders",
        flush=True,
    )


def render_existing(output_root: Path, *, view_set: str) -> None:
    clear_scene()
    folder = (output_root / FAMILY).resolve()
    mats, _skin = load_palette(folder)
    objects = build_assembled(mats)
    normalize_bottom_origin(objects)
    rendered = render_views(folder, view_set=view_set)
    delete_objects(objects)
    print(f"[wave11] {FAMILY}: rendered {len(rendered)} views", flush=True)


def main() -> int:
    args = parse_args()
    if args.render_existing:
        render_existing(args.output_root, view_set=args.view_set)
    else:
        build_family(
            args.output_root,
            view_set=args.view_set,
            skip_renders=args.skip_renders,
            skip_modules=args.skip_modules,
            skip_assembled_export=args.skip_assembled_export,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
