"""Author the Wave 10 corten-arch university-library LEGO family.

The fixed assembled GLB is a true barrel-arch building rather than a box with
an arch texture. Weathering-steel shell panels curve continuously from grade
to crown, front and rear curtain walls sit physically behind thick arch rings,
and the four occupied reading levels, triangular mullion lattice, ceremonial
stair, accessible ramps, roof skylight, side reading windows and drainage are
deterministic metric geometry.

Run with Blender 5.x from the repository root:

    blender --background --factory-startup --python \
      tools/archetype_compiler/generate_wave10_corten_library_family.py -- \
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
    sphere,
    texture_inventory,
)


FAMILY = "corten-arch-university-library"
ARCHETYPE_ID = "university_library"
VARIANT_ID = "contemporary_corten_arch"
ALIASES = [
    ARCHETYPE_ID,
    VARIANT_ID,
    "corten_arch_university_library",
    "sculptural_campus_library",
]
REUSE_KEYS = [
    *ALIASES,
    "university library",
    "campus library",
    "civic library",
    "corten arch",
]
LABEL = "University Library — Contemporary Corten Arch"
GLASS_PROFILE = "library_neutral_low_iron_clear"

NATIVE_WIDTH = 70.0
NATIVE_DEPTH = 56.0
NATIVE_HEIGHT = 25.0
NATIVE_FLOORS = 4
MIN_FLOORS = 2
MAX_FLOORS = 6

BUILDING_WIDTH = 58.0
BUILDING_DEPTH = 42.0
OUTER_RX = 29.0
OUTER_RZ = 24.72
OUTER_SPRING = 0.28
INNER_RX = 26.25
INNER_RZ = 21.55
INNER_SPRING = 1.48
ARCH_SEGMENTS = 40
DEPTH_BAYS = 7
CURTAIN_WALL_RECESS = 2.15

PODIUM_HEIGHT = 2.0
FLOOR_HEIGHT = 4.6
CROWN_HEIGHT = 1.0
ROOF_HEIGHT = 5.4

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
            "rear_corner",
            "aerial",
            "shell_close",
            "curtainwall_close",
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


def colorize_material(
    mat: bpy.types.Material,
    color: tuple[float, float, float, float],
    factor: float,
) -> bpy.types.Material:
    """Bias reflective source albedo back to its render-locked material hue."""
    socket = bsdf_for(mat).inputs["Base Color"]
    if socket.is_linked:
        source = socket.links[0].from_socket
        mat.node_tree.links.remove(socket.links[0])
        colorize = mat.node_tree.nodes.new("ShaderNodeMixRGB")
        colorize.name = colorize.label = "REFERENCE_LOCKED_COLORIZE"
        colorize.blend_type = "COLOR"
        colorize.inputs[0].default_value = factor
        colorize.inputs[2].default_value = color
        mat.node_tree.links.new(source, colorize.inputs[1])
        mat.node_tree.links.new(colorize.outputs["Color"], socket)
    return mat


def make_glass_material(
    folder: Path,
    assets: dict[str, str],
) -> bpy.types.Material:
    # The source plate remains the semantic/mask authority, but the public
    # pane itself is a physically transparent shader. Baking the photographed
    # sample's own mullions into Base Color would double the real lattice.
    mat = material(
        "MAT_W10_LIBRARY_PhysicalNeutralLowIronGlass",
        (0.045, 0.080, 0.105, 0.50),
        0.10,
        metallic=0.0,
    )
    bsdf = bsdf_for(mat)
    bsdf.inputs["Roughness"].default_value = 0.10
    if bsdf.inputs.get("Transmission Weight"):
        bsdf.inputs["Transmission Weight"].default_value = 0.68
    if bsdf.inputs.get("Coat Weight"):
        bsdf.inputs["Coat Weight"].default_value = 0.34
    if bsdf.inputs.get("Coat Roughness"):
        bsdf.inputs["Coat Roughness"].default_value = 0.05
    if bsdf.inputs.get("IOR"):
        bsdf.inputs["IOR"].default_value = 1.51
    if bsdf.inputs.get("Alpha"):
        bsdf.inputs["Alpha"].default_value = 0.50
    mat.diffuse_color = (0.045, 0.080, 0.105, 0.50)
    mat.use_transparency_overlap = False
    mat.use_backface_culling = False
    try:
        mat.surface_render_method = "BLENDED"
    except Exception:
        pass
    mat["glazing_profile"] = GLASS_PROFILE
    mat["glazing_lod"] = "physical_separate_pane"
    mat["skin_zone"] = "low_iron_glass"
    mat["semantic_glass_mask"] = assets["glass_mask"]
    mat["semantic_opaque_mask"] = assets["opaque_mask"]
    mat["pane_recess_m"] = CURTAIN_WALL_RECESS
    mat["interior_depth_m"] = 6.4
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
    mats["corten"] = set_normal_strength(
        colorize_material(
            grade_material(
                skin_material(
                    "MAT_W10_LIBRARY_VariegatedWeatheringSteel",
                    folder,
                    near["corten"],
                    "corten",
                    metallic=0.16,
                ),
                saturation=1.35,
                value=0.72,
            ),
            (0.52, 0.16, 0.055, 1.0),
            0.34,
        ),
        0.36,
    )
    mats["corten_dark"] = material(
        "MAT_W10_LIBRARY_CortenInnerReveal",
        (0.15, 0.036, 0.012, 1.0),
        0.68,
        metallic=0.06,
    )
    mats["concrete"] = set_normal_strength(
        grade_material(
            skin_material(
                "MAT_W10_LIBRARY_BoardFormedConcrete",
                folder,
                near["board_concrete"],
                "board_concrete",
            ),
            saturation=0.38,
            value=0.92,
        ),
        0.24,
    )
    mats["precast"] = set_normal_strength(
        grade_material(
            skin_material(
                "MAT_W10_LIBRARY_HonedPrecastStair",
                folder,
                near["precast"],
                "precast",
            ),
            saturation=0.32,
            value=0.88,
        ),
        0.18,
    )
    mats["bronze"] = grade_material(
        skin_material(
            "MAT_W10_LIBRARY_DarkBronzeAESS",
            folder,
            near["bronze_steel"],
            "bronze_steel",
            metallic=0.70,
        ),
        saturation=0.44,
        value=0.35,
    )
    mats["oak"] = set_normal_strength(
        grade_material(
            skin_material(
                "MAT_W10_LIBRARY_HoneyOakInterior",
                folder,
                near["oak"],
                "oak",
            ),
            saturation=0.88,
            value=0.72,
        ),
        0.22,
    )
    mats["interior"] = grade_material(
        skin_material(
            "MAT_W10_LIBRARY_OccupiedReadingDepth",
            folder,
            near["interior"],
            "occupied_library",
            emission_strength=0.18,
        ),
        saturation=0.65,
        value=0.43,
    )
    mats["roof_membrane"] = grade_material(
        skin_material(
            "MAT_W10_LIBRARY_DarkRoofMembrane",
            folder,
            far["roof_membrane"],
            "roof_membrane",
            metallic=0.18,
        ),
        saturation=0.20,
        value=0.34,
    )
    mats["vegetation"] = material(
        "MAT_W10_LIBRARY_NativeCampusPlanting",
        (0.13, 0.22, 0.075, 1.0),
        0.86,
    )
    mats["asphalt"] = grade_material(
        skin_material(
            "MAT_W10_LIBRARY_CampusAsphalt",
            folder,
            far["asphalt"],
            "asphalt",
        ),
        saturation=0.22,
        value=0.42,
    )
    mats["glass"] = make_glass_material(folder, near["low_iron_glass"])
    mats["warm_light"] = material(
        "MAT_W10_LIBRARY_WarmReadingLight",
        (1.0, 0.58, 0.26, 1.0),
        0.14,
        emission=(1.0, 0.40, 0.10, 1.0),
        emission_strength=4.2,
    )
    mats["book_red"] = material(
        "MAT_W10_LIBRARY_BookRust",
        (0.32, 0.065, 0.035, 1.0),
        0.70,
    )
    mats["book_blue"] = material(
        "MAT_W10_LIBRARY_BookBlue",
        (0.055, 0.12, 0.19, 1.0),
        0.68,
    )
    mats["book_green"] = material(
        "MAT_W10_LIBRARY_BookGreen",
        (0.075, 0.18, 0.105, 1.0),
        0.72,
    )
    mats["book_cream"] = material(
        "MAT_W10_LIBRARY_BookCream",
        (0.58, 0.49, 0.34, 1.0),
        0.74,
    )
    mats["dark"] = material(
        "MAT_W10_LIBRARY_BlackThermalBreak",
        (0.012, 0.014, 0.015, 1.0),
        0.34,
        metallic=0.52,
    )
    mats["tree_bark"] = material(
        "MAT_W10_LIBRARY_TreeBark",
        (0.13, 0.075, 0.035, 1.0),
        0.90,
    )
    return mats, skin


def apply_metric_uv_scale(obj: bpy.types.Object) -> None:
    if obj.type != "MESH" or not obj.data.uv_layers.active:
        return
    mat = obj.data.materials[0] if obj.data.materials else None
    zone = str(mat.get("skin_zone", "")) if mat else ""
    repeat = {
        "corten": (1.25, 1.25),
        "board_concrete": (2.40, 1.00),
        "precast": (2.50, 1.70),
        "oak": (1.40, 0.75),
        "asphalt": (4.20, 4.20),
        "vegetation": (2.50, 2.50),
    }.get(zone)
    if not repeat:
        return
    dims = obj.dimensions
    layer = obj.data.uv_layers.active
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
            layer.data[loop_index].uv.x *= scale_u
            layer.data[loop_index].uv.y *= scale_v


def tag_object(
    obj: bpy.types.Object,
    component: str,
    *,
    role: str,
    count_authority: str | None = None,
    metric_uv: bool = True,
) -> bpy.types.Object:
    obj["component"] = component
    obj["module_role"] = role
    obj["source_variant_id"] = VARIANT_ID
    obj["generation_archetype_id"] = VARIANT_ID
    obj["reference_locked"] = True
    if count_authority:
        obj["count_authority"] = count_authority
    if metric_uv:
        apply_metric_uv_scale(obj)
    return obj


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
) -> bpy.types.Object:
    return tag_object(
        beam(name, start, end, radius, mat),
        component,
        role=role,
        metric_uv=False,
    )


def mesh_object(
    name: str,
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, ...]],
    mat: bpy.types.Material,
    *,
    component: str,
    role: str,
    uvs: list[tuple[float, float]] | None = None,
    count_authority: str | None = None,
) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    mesh.materials.append(mat)
    layer = mesh.uv_layers.new(name="UVMap")
    if uvs:
        for polygon in mesh.polygons:
            for loop_index in polygon.loop_indices:
                vertex_index = mesh.loops[loop_index].vertex_index
                layer.data[loop_index].uv = uvs[vertex_index]
    else:
        xs = [item[0] for item in vertices]
        ys = [item[1] for item in vertices]
        zs = [item[2] for item in vertices]
        mins = (min(xs), min(ys), min(zs))
        spans = (
            max(max(xs) - min(xs), 0.001),
            max(max(ys) - min(ys), 0.001),
            max(max(zs) - min(zs), 0.001),
        )
        for polygon in mesh.polygons:
            for loop_index in polygon.loop_indices:
                co = mesh.vertices[mesh.loops[loop_index].vertex_index].co
                if abs(polygon.normal.y) > 0.72:
                    uv = ((co.x - mins[0]) / spans[0], (co.z - mins[2]) / spans[2])
                elif abs(polygon.normal.x) > 0.72:
                    uv = ((co.y - mins[1]) / spans[1], (co.z - mins[2]) / spans[2])
                else:
                    uv = ((co.x - mins[0]) / spans[0], (co.y - mins[1]) / spans[1])
                layer.data[loop_index].uv = uv
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return tag_object(
        obj,
        component,
        role=role,
        count_authority=count_authority,
        metric_uv=False,
    )


def rect_beam(
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    thickness: float,
    depth: float,
    mat: bpy.types.Material,
    *,
    component: str,
    role: str,
) -> bpy.types.Object:
    a = Vector(start)
    z = Vector(end)
    delta = z - a
    obj = box(
        name,
        (thickness, depth, delta.length),
        tuple((a + z) * 0.5),
        mat,
        min(thickness, depth) * 0.08,
    )
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(
        delta.normalized()
    )
    return tag_object(
        obj,
        component,
        role=role,
        metric_uv=False,
    )


def sloped_walk(
    name: str,
    x0: float,
    x1: float,
    y0: float,
    y1: float,
    z0: float,
    z1: float,
    thickness: float,
    mat: bpy.types.Material,
    *,
    component: str,
    role: str,
) -> bpy.types.Object:
    vertices = [
        (x0, y0, z0),
        (x1, y0, z0),
        (x1, y1, z1),
        (x0, y1, z1),
        (x0, y0, z0 - thickness),
        (x1, y0, z0 - thickness),
        (x1, y1, z1 - thickness),
        (x0, y1, z1 - thickness),
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
    )


def arch_point(
    theta: float,
    *,
    rx: float,
    rz: float,
    spring: float,
) -> tuple[float, float]:
    return (rx * math.cos(theta), spring + rz * math.sin(theta))


def arch_segment(
    name: str,
    theta0: float,
    theta1: float,
    y0: float,
    y1: float,
    outer: tuple[float, float, float],
    inner: tuple[float, float, float],
    mat: bpy.types.Material,
    *,
    component: str,
    role: str,
    count_authority: str | None = None,
    uv_origin: tuple[float, float] = (0.0, 0.0),
    uv_scale: tuple[float, float] = (1.0, 1.0),
) -> bpy.types.Object:
    ox0, oz0 = arch_point(theta0, rx=outer[0], rz=outer[1], spring=outer[2])
    ox1, oz1 = arch_point(theta1, rx=outer[0], rz=outer[1], spring=outer[2])
    ix0, iz0 = arch_point(theta0, rx=inner[0], rz=inner[1], spring=inner[2])
    ix1, iz1 = arch_point(theta1, rx=inner[0], rz=inner[1], spring=inner[2])
    vertices = [
        (ox0, y0, oz0),
        (ox1, y0, oz1),
        (ox1, y1, oz1),
        (ox0, y1, oz0),
        (ix0, y0, iz0),
        (ix1, y0, iz1),
        (ix1, y1, iz1),
        (ix0, y1, iz0),
    ]
    faces = [
        (0, 1, 2, 3),
        (7, 6, 5, 4),
        (0, 4, 5, 1),
        (1, 5, 6, 2),
        (2, 6, 7, 3),
        (3, 7, 4, 0),
    ]
    u0, v0 = uv_origin
    us, vs = uv_scale
    uvs = [
        (u0, v0),
        (u0, v0 + vs),
        (u0 + us, v0 + vs),
        (u0 + us, v0),
        (u0, v0),
        (u0, v0 + vs),
        (u0 + us, v0 + vs),
        (u0 + us, v0),
    ]
    return mesh_object(
        name,
        vertices,
        faces,
        mat,
        component=component,
        role=role,
        uvs=uvs,
        count_authority=count_authority,
    )


def arch_infill(
    name: str,
    y: float,
    mat: bpy.types.Material,
    *,
    role: str,
) -> bpy.types.Object:
    # The sampled arc already includes both spring points. Repeating those
    # endpoints gives Blender's ngon triangulator zero-area corners, which can
    # escape the facade plane as bright triangular shards in glTF renders.
    points = []
    for index in range(ARCH_SEGMENTS + 1):
        theta = math.pi - math.pi * index / ARCH_SEGMENTS
        x, z = arch_point(
            theta,
            rx=INNER_RX,
            rz=INNER_RZ,
            spring=INNER_SPRING,
        )
        points.append((x, y, z))
    face = tuple(range(len(points)))
    uvs = [
        (
            0.5 + point[0] / (2 * INNER_RX),
            (point[2] - INNER_SPRING) / INNER_RZ,
        )
        for point in points
    ]
    return mesh_object(
        name,
        points,
        [face],
        mat,
        component="physical_arch_curtain_wall_glass",
        role=role,
        uvs=uvs,
    )


def arch_half_width(z: float) -> float:
    ratio = (z - INNER_SPRING) / INNER_RZ
    return INNER_RX * math.sqrt(max(0.0, 1.0 - ratio * ratio))


def add_site(
    mats: dict[str, bpy.types.Material],
    *,
    detailed: bool,
    prefix: str = "LIBRARY",
) -> list[bpy.types.Object]:
    role = "podium"
    objects = [
        b(
            f"{prefix}_SiteDatum",
            (NATIVE_WIDTH, NATIVE_DEPTH, 0.20),
            (0.0, 0.0, 0.10),
            mats["precast"],
            component="site_datum",
            role=role,
        ),
        b(
            f"{prefix}_FrontCivicPlaza",
            (50.0, 13.0, 0.08),
            (0.0, -21.5, 0.24),
            mats["precast"],
            component="civic_forecourt",
            role=role,
        ),
        b(
            f"{prefix}_RearCampusWalk",
            (58.0, 7.0, 0.08),
            (0.0, 24.2, 0.24),
            mats["precast"],
            component="rear_campus_walk",
            role=role,
        ),
    ]
    for side in (-1, 1):
        objects.append(
            b(
                f"{prefix}_NativePlantingBed_{side}",
                (5.0, 39.0, 0.16),
                (side * 32.3, 1.5, 0.30),
                mats["vegetation"],
                component="native_planting_bed",
                role=role,
            )
        )
    if detailed:
        for side in (-1, 1):
            for index, y in enumerate((-2.0, 10.0, 21.0)):
                trunk = c(
                    f"{prefix}_CampusTreeTrunk_{side}_{index}",
                    0.18,
                    3.6,
                    (side * 32.0, y, 2.1),
                    mats["tree_bark"],
                    vertices=12,
                    component="campus_tree",
                    role=role,
                )
                crown = sphere(
                    f"{prefix}_CampusTreeCrown_{side}_{index}",
                    1.0,
                    (side * 32.0, y, 5.0),
                    mats["vegetation"],
                    (1.45, 1.25, 1.80),
                    segments=20,
                    rings=12,
                )
                objects.extend(
                    [
                        trunk,
                        tag_object(
                            crown,
                            "campus_tree",
                            role=role,
                            metric_uv=False,
                        ),
                    ]
                )
        for side in (-1, 1):
            for index, y in enumerate((-14.0, -3.0, 8.0, 19.0)):
                objects.append(
                    b(
                        f"{prefix}_CampusBench_{side}_{index}",
                        (2.8, 0.55, 0.18),
                        (side * 32.0, y, 0.62),
                        mats["oak"],
                        0.06,
                        component="campus_bench",
                        role=role,
                    )
                )
    return objects


def side_window_void(index: int, bay: int) -> bool:
    return (
        # Keep the opening as a low, continuous reading-room ribbon. Cutting
        # five arc segments made the vertical glazing stop well below the
        # curved head and exposed triangular views through the shell.
        (index <= 2 or index >= ARCH_SEGMENTS - 3)
        and 1 <= bay <= DEPTH_BAYS - 2
    )


def add_arch_shell(
    mats: dict[str, bpy.types.Material],
    *,
    detailed: bool,
    prefix: str = "LIBRARY",
) -> list[bpy.types.Object]:
    role = "assembled"
    objects: list[bpy.types.Object] = []
    panel_gap_y = 0.08
    y_min = -BUILDING_DEPTH / 2 + 1.45
    y_max = BUILDING_DEPTH / 2 - 1.45
    bay_depth = (y_max - y_min) / DEPTH_BAYS
    panel_outer = (OUTER_RX, OUTER_RZ, OUTER_SPRING)
    panel_inner = (OUTER_RX - 0.18, OUTER_RZ - 0.18, OUTER_SPRING)
    backing_outer = (OUTER_RX - 0.19, OUTER_RZ - 0.19, OUTER_SPRING)
    backing_inner = (OUTER_RX - 0.27, OUTER_RZ - 0.27, OUTER_SPRING)
    liner_outer = (INNER_RX + 0.16, INNER_RZ + 0.16, INNER_SPRING)
    liner_inner = (INNER_RX, INNER_RZ, INNER_SPRING)
    for index in range(ARCH_SEGMENTS):
        theta0 = index * math.pi / ARCH_SEGMENTS + 0.0018
        theta1 = (index + 1) * math.pi / ARCH_SEGMENTS - 0.0018
        if 4 < index < ARCH_SEGMENTS - 4:
            objects.append(
                arch_segment(
                    f"{prefix}_DarkPanelJointBacking_{index:02d}",
                    index * math.pi / ARCH_SEGMENTS,
                    (index + 1) * math.pi / ARCH_SEGMENTS,
                    y_min - 0.02,
                    y_max + 0.02,
                    backing_outer,
                    backing_inner,
                    mats["corten_dark"],
                    component="dark_drained_corten_joint_backing",
                    role=role,
                )
            )
        for bay in range(DEPTH_BAYS):
            if side_window_void(index, bay):
                continue
            y0 = y_min + bay * bay_depth + panel_gap_y
            y1 = y_min + (bay + 1) * bay_depth - panel_gap_y
            objects.append(
                arch_segment(
                    f"{prefix}_CortenShellPanel_{index:02d}_{bay:02d}",
                    theta0,
                    theta1,
                    y0,
                    y1,
                    panel_outer,
                    panel_inner,
                    mats["corten"],
                    component="continuous_corten_barrel_shell_panel",
                    role=role,
                    count_authority="one_shell_40_arc_segments_7_depth_bays",
                    uv_origin=(
                        bay * 0.47 + (index % 3) * 0.11,
                        index * 0.31,
                    ),
                    uv_scale=(0.46, 0.34),
                )
            )
            if index <= 4 or index >= ARCH_SEGMENTS - 4:
                objects.append(
                    arch_segment(
                        f"{prefix}_DarkPanelJointBacking_{index:02d}_{bay:02d}",
                        index * math.pi / ARCH_SEGMENTS,
                        (index + 1) * math.pi / ARCH_SEGMENTS,
                        y_min + bay * bay_depth,
                        y_min + (bay + 1) * bay_depth,
                        backing_outer,
                        backing_inner,
                        mats["corten_dark"],
                        component="dark_drained_corten_joint_backing",
                        role=role,
                    )
                )
            objects.append(
                arch_segment(
                    f"{prefix}_CortenInnerLiner_{index:02d}_{bay:02d}",
                    theta0,
                    theta1,
                    y0,
                    y1,
                    liner_outer,
                    liner_inner,
                    mats["corten_dark"],
                    component="continuous_corten_inner_liner",
                    role=role,
                )
            )
    # Thick front and rear arch rings prove that the shell is construction,
    # not an image pasted onto a facade.
    for side, y0, y1 in (
        ("Front", -BUILDING_DEPTH / 2, -BUILDING_DEPTH / 2 + 1.48),
        ("Rear", BUILDING_DEPTH / 2 - 1.48, BUILDING_DEPTH / 2),
    ):
        for index in range(ARCH_SEGMENTS):
            theta0 = index * math.pi / ARCH_SEGMENTS + 0.00025
            theta1 = (index + 1) * math.pi / ARCH_SEGMENTS - 0.00025
            objects.append(
                arch_segment(
                    f"{prefix}_{side}CortenPortalRing_{index:02d}",
                    theta0,
                    theta1,
                    y0,
                    y1,
                    (OUTER_RX, OUTER_RZ, OUTER_SPRING),
                    (INNER_RX, INNER_RZ, INNER_SPRING),
                    mats["corten"],
                    component="thick_corten_arch_portal_ring",
                    role=role,
                    count_authority="two_complete_40_segment_arch_rings",
                    uv_origin=(index * 0.29, 0.13 if side == "Front" else 0.61),
                    uv_scale=(0.32, 0.55),
                )
            )
    # Exposed AESS ribs run inside the shell at each depth seam.
    if detailed:
        for rib_index in range(DEPTH_BAYS + 1):
            y = y_min + rib_index * bay_depth
            for index in range(ARCH_SEGMENTS):
                theta0 = index * math.pi / ARCH_SEGMENTS
                theta1 = (index + 1) * math.pi / ARCH_SEGMENTS
                x0, z0 = arch_point(
                    theta0,
                    rx=INNER_RX - 0.28,
                    rz=INNER_RZ - 0.28,
                    spring=INNER_SPRING,
                )
                x1, z1 = arch_point(
                    theta1,
                    rx=INNER_RX - 0.28,
                    rz=INNER_RZ - 0.28,
                    spring=INNER_SPRING,
                )
                objects.append(
                    bm(
                        f"{prefix}_InnerArchRib_{rib_index:02d}_{index:02d}",
                        (x0, y, z0),
                        (x1, y, z1),
                        0.115,
                        mats["bronze"],
                        component="architecturally_exposed_arch_rib",
                        role=role,
                    )
                )
    return objects


def lattice_nodes(z: float, spacing: float, offset: float) -> list[float]:
    half = arch_half_width(z) - 0.45
    start = -half + offset
    while start > -half:
        start -= spacing
    values = []
    value = start
    while value <= half:
        if value >= -half:
            values.append(value)
        value += spacing
    return values


def add_arch_curtain_wall(
    mats: dict[str, bpy.types.Material],
    *,
    front: bool,
    detailed: bool,
    prefix: str = "LIBRARY",
) -> list[bpy.types.Object]:
    role = "assembled"
    label = "Front" if front else "Rear"
    y = (
        -BUILDING_DEPTH / 2 + CURTAIN_WALL_RECESS
        if front
        else BUILDING_DEPTH / 2 - CURTAIN_WALL_RECESS
    )
    lattice_y = y - 0.15 if front else y + 0.15
    objects = [arch_infill(f"{prefix}_{label}ArchGlass", y, mats["glass"], role=role)]

    # Perimeter mullion follows the actual inner arch.
    for index in range(ARCH_SEGMENTS):
        theta0 = index * math.pi / ARCH_SEGMENTS
        theta1 = (index + 1) * math.pi / ARCH_SEGMENTS
        x0, z0 = arch_point(
            theta0,
            rx=INNER_RX,
            rz=INNER_RZ,
            spring=INNER_SPRING,
        )
        x1, z1 = arch_point(
            theta1,
            rx=INNER_RX,
            rz=INNER_RZ,
            spring=INNER_SPRING,
        )
        objects.append(
            bm(
                f"{prefix}_{label}PerimeterMullion_{index:02d}",
                (x0, lattice_y, z0),
                (x1, lattice_y, z1),
                0.11,
                mats["bronze"],
                component="curved_curtain_wall_perimeter",
                role=role,
            )
        )
    floor_levels = [1.62, 6.15, 10.65, 15.15, 19.45]
    for index, z in enumerate(floor_levels):
        half = arch_half_width(max(z, INNER_SPRING + 0.02)) - 0.20
        objects.append(
            rect_beam(
                f"{prefix}_{label}FloorEdgeMullion_{index}",
                (-half, lattice_y, z),
                (half, lattice_y, z),
                0.24 if index else 0.30,
                0.24,
                mats["bronze"],
                component="curtain_wall_floor_edge",
                role=role,
            )
        )
    # A precise triangular lattice is constructed row by row. Rear glazing is
    # quieter but uses the same registered frame system.
    row_levels = [1.65, 5.20, 8.75, 12.30, 15.85, 19.40, 22.25]
    spacing = 5.50 if front else 6.20
    for row in range(len(row_levels) - 1):
        z0 = row_levels[row]
        z1 = row_levels[row + 1]
        if z1 >= INNER_SPRING + INNER_RZ:
            continue
        lower = lattice_nodes(z0, spacing, 0.0)
        upper = lattice_nodes(z1, spacing, spacing / 2 if row % 2 == 0 else 0.0)
        for low_index, x0 in enumerate(lower):
            choices = sorted(upper, key=lambda value: abs(value - x0))[:2]
            for choice_index, x1 in enumerate(choices):
                if not front and choice_index == 1:
                    continue
                objects.append(
                    rect_beam(
                        f"{prefix}_{label}TriangularLattice_{row:02d}_{low_index:02d}_{choice_index}",
                        (x0, lattice_y, z0),
                        (x1, lattice_y, z1),
                        0.085 if front else 0.072,
                        0.14,
                        mats["bronze"],
                        component=(
                            "front_triangular_honeycomb_lattice"
                            if front
                            else "rear_reading_wall_lattice"
                        ),
                        role=role,
                    )
                )
        if detailed:
            half = arch_half_width(z1) - 0.25
            objects.append(
                rect_beam(
                    f"{prefix}_{label}HorizontalLattice_{row:02d}",
                    (-half, lattice_y, z1),
                    (half, lattice_y, z1),
                    0.09,
                    0.15,
                    mats["bronze"],
                    component="curtain_wall_horizontal_lattice",
                    role=role,
                )
            )
    return objects


def add_side_reading_windows(
    mats: dict[str, bpy.types.Material],
    *,
    prefix: str = "LIBRARY",
) -> list[bpy.types.Object]:
    role = "assembled"
    objects: list[bpy.types.Object] = []
    shell_y_min = -BUILDING_DEPTH / 2 + 1.45
    shell_y_max = BUILDING_DEPTH / 2 - 1.45
    bay_width = (shell_y_max - shell_y_min) / DEPTH_BAYS
    pane_width = bay_width - 0.24
    for side in (-1, 1):
        # The window wall is recessed behind the curved shell instead of
        # sitting on its tangent. This produces a real corten reveal at the
        # jambs and keeps the glass inside the arch at its curved head.
        x = side * 27.10
        for bay in range(5):
            shell_bay = bay + 1
            y = shell_y_min + (shell_bay + 0.5) * bay_width
            for tier, z in enumerate((2.55, 4.55)):
                objects.append(
                    b(
                        f"{prefix}_SideReadingGlass_{side}_{bay}_{tier}",
                        (0.14, pane_width, 1.82),
                        (x, y, z),
                        mats["glass"],
                        component="physical_side_reading_window",
                        role=role,
                        count_authority="ten_side_bays_two_tiers",
                    )
                )
            for edge, edge_y in enumerate(
                (y - bay_width / 2, y + bay_width / 2)
            ):
                objects.append(
                    b(
                        f"{prefix}_SideWindowVerticalFrame_{side}_{bay}_{edge}",
                        (0.24, 0.16, 4.24),
                        (x + side * 0.08, edge_y, 3.55),
                        mats["bronze"],
                        component="side_window_frame",
                        role=role,
                    )
                )
            objects.append(
                b(
                    f"{prefix}_SideWindowTransom_{side}_{bay}",
                    (0.24, pane_width, 0.18),
                    (x + side * 0.08, y, 3.55),
                    mats["bronze"],
                    component="side_window_frame",
                    role=role,
                )
            )
        objects.append(
            b(
                f"{prefix}_SideWindowSill_{side}",
                (0.42, bay_width * 5, 0.28),
                (x, 0.0, 1.50),
                mats["precast"],
                component="side_window_sill",
                role=role,
            )
        )
        objects.extend(
            [
                b(
                    f"{prefix}_SideWindowConcretePlinth_{side}",
                    (0.40, bay_width * 5, 1.18),
                    (x - side * 0.10, 0.0, 0.86),
                    mats["concrete"],
                    component="integrated_side_window_plinth",
                    role=role,
                ),
                b(
                    f"{prefix}_SideWindowShadowHead_{side}",
                    (0.34, bay_width * 5, 0.42),
                    (x - side * 0.08, 0.0, 5.77),
                    mats["dark"],
                    component="recessed_side_window_head",
                    role=role,
                ),
            ]
        )
        objects.append(
            b(
                f"{prefix}_SideOccupiedDepth_{side}",
                (0.12, bay_width * 5, 4.18),
                (side * 26.78, 0.0, 3.55),
                mats["dark"],
                component="occupied_depth_behind_side_glazing",
                role=role,
            )
        )
    return objects


def add_ceremonial_entry(
    mats: dict[str, bpy.types.Material],
    *,
    detailed: bool,
    prefix: str = "LIBRARY",
) -> list[bpy.types.Object]:
    role = "assembled"
    objects: list[bpy.types.Object] = []
    step_count = 12
    riser = 0.15
    tread = 0.48
    stair_width = 24.0
    y_start = -27.68
    for index in range(step_count):
        height = riser * (index + 1)
        y = y_start + index * tread
        objects.append(
            b(
                f"{prefix}_CeremonialStairTread_{index:02d}",
                (stair_width, tread + 0.035, height),
                (0.0, y, height / 2 + 0.22),
                mats["precast"],
                0.015,
                component="real_ceremonial_stair",
                role=role,
                count_authority="twelve_uniform_closed_risers",
            )
        )
    landing_y = y_start + step_count * tread + 1.08
    objects.append(
        b(
            f"{prefix}_EntranceLanding",
            (24.0, 2.6, 1.80),
            (0.0, landing_y, 0.90 + 0.22),
            mats["precast"],
            component="entry_landing",
            role=role,
        )
    )
    for side in (-1, 1):
        objects.append(
            sloped_walk(
                f"{prefix}_AccessibleEntryRamp_{side}",
                side * 16.4 - 1.65,
                side * 16.4 + 1.65,
                -27.5,
                -20.1,
                0.35,
                2.02,
                0.22,
                mats["precast"],
                component="integrated_accessible_entry_route",
                role=role,
            )
        )
        objects.append(
            b(
                f"{prefix}_StairCheekWall_{side}",
                (0.48, 7.4, 2.22),
                (side * 12.28, -23.7, 1.33),
                mats["concrete"],
                0.06,
                component="integrated_stair_cheek_wall",
                role=role,
            )
        )
    # Handrails align with the stair slope and return onto both landings.
    for rail_x in (-8.0, -2.7, 2.7, 8.0):
        objects.extend(
            [
                bm(
                    f"{prefix}_StairHandrailSlope_{rail_x}",
                    (rail_x, -27.65, 1.18),
                    (rail_x, -21.92, 2.93),
                    0.055,
                    mats["bronze"],
                    component="continuous_stair_handrail",
                    role=role,
                ),
                bm(
                    f"{prefix}_StairHandrailTopReturn_{rail_x}",
                    (rail_x, -21.92, 2.93),
                    (rail_x, -20.90, 2.93),
                    0.055,
                    mats["bronze"],
                    component="continuous_stair_handrail",
                    role=role,
                ),
            ]
        )
        for index in (0, 4, 8, 11):
            z = 1.18 + index * riser
            y = y_start + index * tread
            objects.append(
                bm(
                    f"{prefix}_StairHandrailPost_{rail_x}_{index:02d}",
                    (rail_x, y, z - 0.88),
                    (rail_x, y, z),
                    0.045,
                    mats["bronze"],
                    component="stair_handrail_post",
                    role=role,
                )
            )
    # The entry is recessed into the glass wall rather than attached outside.
    entry_y = -BUILDING_DEPTH / 2 + 1.22
    objects.extend(
        [
            b(
                f"{prefix}_RecessedEntranceHead",
                (10.8, 0.62, 0.42),
                (0.0, entry_y, 5.00),
                mats["bronze"],
                component="recessed_entrance_portal",
                role=role,
            ),
            b(
                f"{prefix}_RecessedEntranceLeftJamb",
                (0.40, 0.62, 3.12),
                (-5.20, entry_y, 3.45),
                mats["bronze"],
                component="recessed_entrance_portal",
                role=role,
            ),
            b(
                f"{prefix}_RecessedEntranceRightJamb",
                (0.40, 0.62, 3.12),
                (5.20, entry_y, 3.45),
                mats["bronze"],
                component="recessed_entrance_portal",
                role=role,
            ),
        ]
    )
    for door in range(5):
        x = -4.15 + door * 2.075
        objects.append(
            b(
                f"{prefix}_EntranceDoorGlass_{door}",
                (1.82, 0.12, 2.72),
                (x, entry_y - 0.34, 3.22),
                mats["glass"],
                component="physical_glazed_entry_door",
                role=role,
                count_authority="five_public_entry_doors",
            )
        )
        objects.append(
            b(
                f"{prefix}_EntranceDoorFrame_{door}",
                (0.12, 0.20, 2.92),
                (x - 0.97, entry_y - 0.40, 3.30),
                mats["bronze"],
                component="entry_door_hardware",
                role=role,
            )
        )
    if detailed:
        for door in range(5):
            x = -4.15 + door * 2.075
            objects.append(
                bm(
                    f"{prefix}_EntranceDoorPull_{door}",
                    (x + 0.42, entry_y - 0.52, 2.85),
                    (x + 0.42, entry_y - 0.52, 3.85),
                    0.025,
                    mats["bronze"],
                    component="entry_door_hardware",
                    role=role,
                )
            )
    return objects


def add_occupied_library(
    mats: dict[str, bpy.types.Material],
    *,
    detailed: bool,
    prefix: str = "LIBRARY",
) -> list[bpy.types.Object]:
    role = "assembled"
    objects: list[bpy.types.Object] = []
    levels = [
        (1.82, 50.0),
        (6.20, 48.0),
        (10.65, 43.0),
        (15.10, 34.0),
    ]
    for level, (z, width) in enumerate(levels):
        # Two plate wings leave a real double-height central reading void.
        gap = 10.0 if level in (1, 2) else 6.0
        wing_width = (width - gap) / 2
        for side in (-1, 1):
            x = side * (gap / 2 + wing_width / 2)
            objects.append(
                b(
                    f"{prefix}_ReadingFloorPlate_{level}_{side}",
                    (wing_width, 35.5, 0.36),
                    (x, 0.2, z),
                    mats["concrete"],
                    component="occupied_library_floor_plate",
                    role=role,
                )
            )
        # Continuous front edge reads through the glass like the goalpost.
        objects.append(
            b(
                f"{prefix}_ReadingFloorEdge_{level}",
                (width, 0.46, 0.50),
                (0.0, -18.90, z + 0.05),
                mats["bronze"],
                component="visible_reading_floor_edge",
                role=role,
            )
        )
        # Book stacks and reading tables populate both wings.
        if detailed:
            for side in (-1, 1):
                for stack_index in range(4):
                    x = side * (7.5 + (stack_index % 2) * 5.2)
                    y = -8.5 + (stack_index // 2) * 12.0
                    shelf_z = z + 1.55
                    objects.append(
                        b(
                            f"{prefix}_BookStackCase_{level}_{side}_{stack_index}",
                            (3.8, 0.52, 2.65),
                            (x, y, shelf_z),
                            mats["oak"],
                            0.04,
                            component="occupied_book_stack",
                            role=role,
                        )
                    )
                    for row in range(3):
                        book_mat = (
                            mats["book_red"],
                            mats["book_blue"],
                            mats["book_green"],
                            mats["book_cream"],
                        )[(level + stack_index + row) % 4]
                        objects.append(
                            b(
                                f"{prefix}_Books_{level}_{side}_{stack_index}_{row}",
                                (3.35, 0.18, 0.46),
                                (x, y - 0.34, z + 0.62 + row * 0.78),
                                book_mat,
                                component="occupied_library_books",
                                role=role,
                            )
                        )
                for table_index in range(3):
                    x = side * (5.8 + table_index * 3.7)
                    y = -14.5
                    objects.extend(
                        [
                            b(
                                f"{prefix}_ReadingTableTop_{level}_{side}_{table_index}",
                                (2.8, 1.05, 0.12),
                                (x, y, z + 0.92),
                                mats["oak"],
                                0.06,
                                component="occupied_reading_table",
                                role=role,
                            ),
                            b(
                                f"{prefix}_ReadingTableBase_{level}_{side}_{table_index}",
                                (0.16, 0.72, 0.86),
                                (x, y, z + 0.48),
                                mats["bronze"],
                                component="occupied_reading_table",
                                role=role,
                            ),
                        ]
                    )
        light_width = max(width - 5.0, 10.0)
        for light_index in range(5):
            y = -14.0 + light_index * 7.0
            objects.append(
                b(
                    f"{prefix}_ReadingLinearLight_{level}_{light_index}",
                    (light_width, 0.10, 0.09),
                    (0.0, y, z + 3.95),
                    mats["warm_light"],
                    component="warm_linear_reading_light",
                    role=role,
                )
            )
    # Columns and atrium balustrades make the interior physically legible.
    for x in (-20.0, -10.0, 10.0, 20.0):
        for y in (-12.0, 0.0, 12.0):
            roof_top = (
                INNER_SPRING
                + INNER_RZ
                * math.sqrt(max(0.0, 1.0 - (x / INNER_RX) ** 2))
                - 0.55
            )
            column_bottom = 1.65
            column_height = roof_top - column_bottom
            objects.append(
                b(
                    f"{prefix}_InteriorColumn_{x}_{y}",
                    (0.34, 0.34, column_height),
                    (x, y, column_bottom + column_height / 2),
                    mats["bronze"],
                    component="interior_structural_column",
                    role=role,
                )
            )
    for level, z in enumerate((6.55, 11.0, 15.45)):
        for side in (-1, 1):
            objects.append(
                b(
                    f"{prefix}_AtriumBalustrade_{level}_{side}",
                    (0.12, 28.0, 1.15),
                    (side * 5.0, 1.0, z + 0.55),
                    mats["glass"],
                    component="physical_atrium_balustrade",
                    role=role,
                )
            )
            objects.append(
                b(
                    f"{prefix}_AtriumHandrail_{level}_{side}",
                    (0.16, 28.0, 0.12),
                    (side * 5.0, 1.0, z + 1.14),
                    mats["bronze"],
                    component="atrium_handrail",
                    role=role,
                )
            )
    # Storey-specific warm depth planes prevent transparent glazing from
    # reading as empty. Their widths follow the arch at each upper edge; a
    # single rectangular plane protruded through the narrowing shell at the
    # top storey when viewed from the rear corner.
    for level, (bottom, top) in enumerate(
        (
            (2.10, 5.55),
            (6.35, 9.95),
            (10.85, 14.45),
            (15.30, 18.55),
        )
    ):
        half_width = max(4.0, arch_half_width(top) - 1.25)
        objects.append(
            b(
                f"{prefix}_OccupiedDepthBackdrop_{level}",
                (2 * half_width, 0.16, top - bottom),
                (0.0, 15.3, (bottom + top) / 2),
                mats["interior"],
                component="arch_fitted_occupied_depth_underlay",
                role=role,
            )
        )
    return objects


def add_roof_details(
    mats: dict[str, bpy.types.Material],
    *,
    prefix: str = "LIBRARY",
) -> list[bpy.types.Object]:
    role = "assembled"
    objects: list[bpy.types.Object] = []
    # Linear crown skylight is a separate glass assembly above the shell.
    objects.extend(
        [
            b(
                f"{prefix}_CrownSkylightGlass",
                (2.4, 31.0, 0.18),
                (0.0, 0.0, 25.02),
                mats["glass"],
                component="linear_crown_skylight",
                role=role,
                count_authority="one_continuous_crown_skylight",
            ),
            b(
                f"{prefix}_CrownSkylightLeftCurb",
                (0.22, 32.0, 0.36),
                (-1.35, 0.0, 24.91),
                mats["bronze"],
                component="linear_crown_skylight",
                role=role,
            ),
            b(
                f"{prefix}_CrownSkylightRightCurb",
                (0.22, 32.0, 0.36),
                (1.35, 0.0, 24.91),
                mats["bronze"],
                component="linear_crown_skylight",
                role=role,
            ),
        ]
    )
    for index in range(8):
        y = -14.0 + index * 4.0
        objects.append(
            b(
                f"{prefix}_CrownSkylightTransom_{index}",
                (2.9, 0.16, 0.24),
                (0.0, y, 25.06),
                mats["bronze"],
                component="linear_crown_skylight",
                role=role,
            )
        )
    # Spring-line gutters and four downpipes complete the shell drainage.
    for side in (-1, 1):
        x = side * 28.92
        objects.append(
            bm(
                f"{prefix}_SpringLineGutter_{side}",
                (x, -19.5, 0.70),
                (x, 19.5, 0.70),
                0.14,
                mats["bronze"],
                component="integrated_shell_drainage",
                role=role,
            )
        )
        for end, y in enumerate((-18.9, 18.9)):
            objects.append(
                bm(
                    f"{prefix}_Downpipe_{side}_{end}",
                    (x, y, 0.72),
                    (x, y, 0.22),
                    0.095,
                    mats["bronze"],
                    component="integrated_shell_drainage",
                    role=role,
                )
            )
    return objects


def build_assembled(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    objects.extend(add_site(mats, detailed=True))
    objects.extend(add_arch_shell(mats, detailed=True))
    objects.extend(add_arch_curtain_wall(mats, front=True, detailed=True))
    objects.extend(add_arch_curtain_wall(mats, front=False, detailed=True))
    objects.extend(add_side_reading_windows(mats))
    objects.extend(add_ceremonial_entry(mats, detailed=True))
    objects.extend(add_occupied_library(mats, detailed=True))
    objects.extend(add_roof_details(mats))
    normalize_bottom_origin(objects)
    return objects


def normalize_bottom_origin(objects: list[bpy.types.Object]) -> None:
    if not objects:
        return
    minimum = min(
        (obj.matrix_world @ Vector(corner)).z
        for obj in objects
        if obj.type == "MESH"
        for corner in obj.bound_box
    )
    if abs(minimum) > 1e-6:
        for obj in objects:
            obj.location.z -= minimum


def evaluated_triangle_count(objects: list[bpy.types.Object]) -> int:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    count = 0
    for obj in objects:
        if obj.type != "MESH":
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            count += sum(max(1, len(poly.vertices) - 2) for poly in mesh.polygons)
        finally:
            evaluated.to_mesh_clear()
    return count


def material_count(objects: list[bpy.types.Object]) -> int:
    return len(
        {
            slot.material.name
            for obj in objects
            if obj.type == "MESH"
            for slot in obj.material_slots
            if slot.material
        }
    )


def build_floor_module(
    variant: str,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    role = "floor"
    prefix = f"MODULE_FLOOR_{variant.upper()}"
    objects: list[bpy.types.Object] = [
        b(
            f"{prefix}_FloorPlate",
            (BUILDING_WIDTH, BUILDING_DEPTH, 0.28),
            (0.0, 0.0, 0.14),
            mats["concrete"],
            component="flexible_library_floor_plate",
            role=role,
        ),
        b(
            f"{prefix}_FrontGlass",
            (50.0, 0.14, FLOOR_HEIGHT - 0.32),
            (0.0, -BUILDING_DEPTH / 2 + 0.25, FLOOR_HEIGHT / 2),
            mats["glass"],
            component="flexible_physical_curtain_wall",
            role=role,
        ),
        b(
            f"{prefix}_RearGlass",
            (50.0, 0.14, FLOOR_HEIGHT - 0.32),
            (0.0, BUILDING_DEPTH / 2 - 0.25, FLOOR_HEIGHT / 2),
            mats["glass"],
            component="flexible_physical_curtain_wall",
            role=role,
        ),
    ]
    for side in (-1, 1):
        objects.extend(
            [
                b(
                    f"{prefix}_CortenSidePier_{side}",
                    (4.0, BUILDING_DEPTH, FLOOR_HEIGHT),
                    (side * 27.0, 0.0, FLOOR_HEIGHT / 2),
                    mats["corten"],
                    component="flexible_corten_shell_return",
                    role=role,
                ),
                b(
                    f"{prefix}_SideReadingGlass_{side}",
                    (0.15, 30.0, 2.85),
                    (side * 24.9, 0.0, 2.25),
                    mats["glass"],
                    component="flexible_side_reading_window",
                    role=role,
                ),
            ]
        )
    shift = {"typical_a": 0.0, "typical_b": 1.35, "typical_c": -1.35}[variant]
    for facade_y in (-BUILDING_DEPTH / 2, BUILDING_DEPTH / 2):
        for index in range(-6, 7):
            x0 = index * 4.0 + shift
            x1 = x0 + (2.0 if (index + (0 if variant == "typical_a" else 1)) % 2 == 0 else -2.0)
            if abs(x0) < 25 and abs(x1) < 25:
                objects.append(
                    rect_beam(
                        f"{prefix}_Lattice_{facade_y}_{index}",
                        (x0, facade_y, 0.35),
                        (x1, facade_y, FLOOR_HEIGHT - 0.25),
                        0.10,
                        0.16,
                        mats["bronze"],
                        component="flexible_triangular_lattice",
                        role=role,
                    )
                )
        objects.append(
            b(
                f"{prefix}_FacadeFloorEdge_{facade_y}",
                (51.0, 0.22, 0.22),
                (0.0, facade_y, FLOOR_HEIGHT / 2),
                mats["bronze"],
                component="flexible_curtain_wall_floor_edge",
                role=role,
            )
        )
    objects.append(
        b(
            f"{prefix}_OakReadingDepth",
            (45.0, 0.22, 3.2),
            (0.0, 14.0, 2.0),
            mats["interior"],
            component="flexible_occupied_reading_depth",
            role=role,
        )
    )
    return objects


def build_roof_module(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    role = "roof"
    prefix = "MODULE_ROOF_DEFAULT"
    objects: list[bpy.types.Object] = []
    segments = 24
    for index in range(segments):
        theta0 = index * math.pi / segments + 0.002
        theta1 = (index + 1) * math.pi / segments - 0.002
        objects.append(
            arch_segment(
                f"{prefix}_CortenBarrelPanel_{index:02d}",
                theta0,
                theta1,
                -BUILDING_DEPTH / 2,
                BUILDING_DEPTH / 2,
                (OUTER_RX, ROOF_HEIGHT, 0.0),
                (OUTER_RX - 0.22, ROOF_HEIGHT - 0.22, 0.0),
                mats["corten"],
                component="flexible_corten_barrel_roof",
                role=role,
                uv_origin=(index * 0.37, 0.0),
                uv_scale=(0.48, 0.62),
            )
        )
    objects.extend(
        [
            b(
                f"{prefix}_SkylightGlass",
                (2.3, 31.0, 0.16),
                (0.0, 0.0, ROOF_HEIGHT + 0.03),
                mats["glass"],
                component="flexible_crown_skylight",
                role=role,
            ),
            b(
                f"{prefix}_SkylightLeftCurb",
                (0.18, 32.0, 0.30),
                (-1.28, 0.0, ROOF_HEIGHT - 0.10),
                mats["bronze"],
                component="flexible_crown_skylight",
                role=role,
            ),
            b(
                f"{prefix}_SkylightRightCurb",
                (0.18, 32.0, 0.30),
                (1.28, 0.0, ROOF_HEIGHT - 0.10),
                mats["bronze"],
                component="flexible_crown_skylight",
                role=role,
            ),
        ]
    )
    return objects


def build_module(
    role: str,
    variant: str,
    mats: dict[str, bpy.types.Material],
) -> tuple[list[bpy.types.Object], float]:
    prefix = f"MODULE_{role.upper()}_{variant.upper()}"
    if role == "podium":
        objects = add_site(mats, detailed=False, prefix=prefix)
        objects.extend(
            [
                b(
                    f"{prefix}_RaisedLibraryPodium",
                    (58.0, 42.0, PODIUM_HEIGHT),
                    (0.0, 0.0, PODIUM_HEIGHT / 2),
                    mats["concrete"],
                    component="flexible_library_podium",
                    role=role,
                ),
                b(
                    f"{prefix}_EntryStairBlock",
                    (24.0, 7.0, PODIUM_HEIGHT),
                    (0.0, -24.2, PODIUM_HEIGHT / 2),
                    mats["precast"],
                    component="fixed_podium_entrance",
                    role=role,
                ),
            ]
        )
        height = PODIUM_HEIGHT
    elif role == "floor":
        objects = build_floor_module(variant, mats)
        height = FLOOR_HEIGHT
    elif role == "crown":
        objects = [
            b(
                f"{prefix}_CortenCrownBand",
                (58.0, 42.0, CROWN_HEIGHT),
                (0.0, 0.0, CROWN_HEIGHT / 2),
                mats["corten"],
                component="fixed_corten_crown",
                role=role,
            )
        ]
        height = CROWN_HEIGHT
    elif role == "roof":
        objects = build_roof_module(mats)
        height = ROOF_HEIGHT
    else:
        raise ValueError(role)
    markers = module_contract_markers(role, variant, height)
    for marker in markers:
        tag_object(
            marker,
            "four_elevation_material_contract",
            role=role,
            metric_uv=False,
        )
    objects.extend(markers)
    normalize_bottom_origin(objects)
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


def build_modules(
    folder: Path,
    mats: dict[str, bpy.types.Material],
    skin: dict,
) -> list[dict]:
    specs = [
        ("podium", "default"),
        ("floor", "typical_a"),
        ("floor", "typical_b"),
        ("floor", "typical_c"),
        ("crown", "crown"),
        ("roof", "default"),
    ]
    modules = []
    for role, variant in specs:
        objects, height = build_module(role, variant, mats)
        filename = (
            f"{FAMILY}_{role}_{variant}.glb"
            if role not in {"podium", "roof"}
            else f"{FAMILY}_{role}.glb"
        )
        path = folder / filename
        export_glb(path, objects)
        modules.append(
            module_payload(
                role,
                variant,
                filename,
                height,
                objects,
                path.stat().st_size,
                skin,
            )
        )
        delete_objects(objects)
    return modules


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
    scene.view_settings.exposure = 0.45
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.47, 0.54, 0.61, 1.0)
    background.inputs["Strength"].default_value = 0.72

    presentation: list[bpy.types.Object] = []
    ground_mat = material(
        "MAT_W10_LIBRARY_PresentationGround",
        (0.35, 0.36, 0.34, 1.0),
        0.88,
    )
    presentation.append(
        box(
            "PRESENTATION_LibraryGround",
            (180.0, 180.0, 0.10),
            (0.0, 0.0, -0.08),
            ground_mat,
        )
    )
    bpy.ops.object.light_add(
        type="SUN",
        location=(-70.0, -90.0, 95.0),
        rotation=(math.radians(29), math.radians(-20), math.radians(-36)),
    )
    sun = bpy.context.object
    sun.name = "PRESENTATION_LibrarySun"
    sun.data.energy = 1.35
    sun.data.angle = math.radians(8.0)
    sun.data.color = (1.0, 0.87, 0.74)
    presentation.append(sun)
    for name, location, energy, size, color in (
        (
            "PRESENTATION_LibraryKey",
            (-40.0, -55.0, 55.0),
            2300,
            26.0,
            (1.0, 0.84, 0.72),
        ),
        (
            "PRESENTATION_LibraryFill",
            (42.0, -8.0, 38.0),
            650,
            22.0,
            (0.70, 0.80, 1.0),
        ),
        (
            "PRESENTATION_LibraryRear",
            (0.0, 55.0, 34.0),
            850,
            20.0,
            (0.74, 0.83, 1.0),
        ),
    ):
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.name = name
        light.data.energy = energy
        light.data.shape = "DISK"
        light.data.size = size
        light.data.color = color
        direction = Vector((0.0, 0.0, 9.0)) - light.location
        light.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        presentation.append(light)
    return presentation


def render_views(
    folder: Path,
    *,
    view_set: str,
) -> list[str]:
    presentation = configure_render()
    views = {
        "preview": ((61.0, -86.0, 37.0), (0.0, -3.0, 9.5), 58),
        "street": ((50.0, -91.0, 20.0), (0.0, -5.0, 8.5), 60),
        "front_elevation": ((0.0, -104.0, 14.0), (0.0, -4.0, 10.5), 68),
        "rear_corner": ((-49.0, 70.0, 28.0), (0.0, 4.0, 9.0), 58),
        "aerial": ((58.0, -62.0, 67.0), (0.0, 0.0, 9.0), 56),
        "shell_close": ((42.0, -13.0, 35.0), (10.0, 0.0, 18.0), 67),
        "curtainwall_close": ((-18.0, -44.0, 14.0), (-8.0, -19.0, 10.0), 70),
        "entrance_close": ((0.0, -45.0, 7.5), (0.0, -21.5, 3.0), 72),
        "side": ((-78.0, -5.0, 18.0), (-22.0, 0.0, 9.0), 63),
    }
    if view_set == "preview":
        selected = ["preview"]
    elif view_set == "pilot":
        selected = [
            "preview",
            "street",
            "front_elevation",
            "rear_corner",
            "aerial",
            "shell_close",
            "curtainwall_close",
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
        "rear_corner_oblique": "rear_corner",
        "facade_close": "curtainwall_close",
        "context": "street",
    }
    for canonical_role, source_role in canonical_aliases.items():
        source = folder / f"{FAMILY}_{source_role}.png"
        target = folder / f"{FAMILY}_{canonical_role}.png"
        if source.is_file():
            shutil.copyfile(source, target)
            renders.append(target.name)
    delete_objects(
        [obj for obj in presentation if obj and obj.name in bpy.data.objects]
    )
    if scene_camera := bpy.context.scene.camera:
        if scene_camera.name in bpy.data.objects:
            bpy.data.objects.remove(scene_camera, do_unlink=True)
    return renders


def footprint_contract() -> dict:
    rectangle = {
        "recommendedWidth_m": [44.0, 90.0],
        "recommendedDepth_m": [34.0, 70.0],
        "recommendedFloors": [2, 6],
        "scaleMin": 0.76,
        "scaleMax": 1.28,
        "maxAxisRatio": 1.20,
        "preferredBayMultiple_m": 6.0,
    }
    return {
        "preferredProfiles": ["rectangle"],
        "minimumPreferredProfiles": 1,
        "profileRationale": (
            "The continuous barrel shell and one ceremonial stair form a "
            "singular landmark. The authored rectangle matrix deliberately "
            "accepts ordinary hand-drawn variation from 44–90 by 34–70 metres; "
            "larger targets repeat complete library halls instead of bending "
            "or clipping the arch."
        ),
        "fixedLandmarkScaleBand": {
            "scaleMin": 0.76,
            "scaleMax": 1.28,
            "maxAxisRatio": 1.20,
        },
        "preferredBayMultiple_m": 6.0,
        "recommendedWidth_m": [44.0, 90.0],
        "recommendedDepth_m": [34.0, 70.0],
        "recommendedFloors": [2, 6],
        "scaleMin": 0.76,
        "scaleMax": 1.28,
        "maxAxisRatio": 1.20,
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
            "front_corten_arch_ring_and_ceremonial_stair",
            "rear_corten_arch_ring_and_reading_wall",
        ],
        "repeatable_middle_bays": list(range(DEPTH_BAYS)),
        "middle_variants": ["typical_a", "typical_b", "typical_c"],
        "rule": (
            "Repeat complete six-metre shell and reading-floor bays only. Keep "
            "corten panel, inner AESS rib, side glazing and floor edge aligned; "
            "never stretch one arch panel or triangular curtain-wall cell."
        ),
    }
    contract["assembly_contract"] = {
        "fixed": ["podium/entrance", "corner returns", "crown", "roof"],
        "repeatable": ["typical_a", "typical_b", "typical_c"],
        "side_elevations": (
            "The front and rear are physically recessed arch curtain walls; "
            "both shell returns carry real two-tier reading windows; the roof "
            "is a continuously panelled weathering-steel barrel with skylight."
        ),
        "elevation_coverage": {
            "front": "corten arch ring, honeycomb glass, five doors and stair",
            "left": "curved shell return and ten physical reading panes",
            "right": "curved shell return and ten physical reading panes",
            "rear": "recessed reading curtain wall and complete arch ring",
            "roof": "corten panels, seams, inner ribs, skylight and drainage",
        },
        "variation_policy": (
            "Scale the complete fixed library from 0.76–1.28 with an independent "
            "axis ratio no greater than 1.20. Oversized sites use long-axis "
            "streetwall repetition of complete library halls."
        ),
    }
    return contract


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
    manifest_path = folder / f"{FAMILY}_manifest.json"
    previous = (
        json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest_path.is_file()
        else {}
    )
    objects = build_assembled(mats)
    assembled_path = folder / f"{FAMILY}_assembled.glb"
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
        "type": "fixed_landmark",
        "silhouette": "one_continuous_symmetric_corten_barrel_arch",
        "continuous_barrel_arch_shells": 1,
        "front_corten_portal_rings": 1,
        "rear_corten_portal_rings": 1,
        "occupied_reading_storeys": 4,
        "front_triangular_lattice": True,
        "recessed_public_entrance": 1,
        "public_entry_doors": 5,
        "ceremonial_stair_risers": 12,
        "accessible_side_ramps": 2,
        "linear_crown_skylights": 1,
        "side_reading_window_panes": 20,
        "shell_drainage_downpipes": 4,
    }
    assembled = {
        "filename": assembled_path.name,
        "floors": NATIVE_FLOORS,
        "uses_setback": False,
        "uses_crown": True,
        "height_m": NATIVE_HEIGHT,
        "triangle_count": assembled_triangles,
        "material_count": assembled_materials,
        "footprint_profile": "rectangle",
        "footprint_target": {
            "width_m": NATIVE_WIDTH,
            "depth_m": NATIVE_DEPTH,
        },
        "source_variant_id": VARIANT_ID,
        "generation_archetype_id": VARIANT_ID,
        "assembly_class": "fixed_landmark",
        "stack": [
            {
                "role": "assembled",
                "variant_key": "fixed_landmark",
                "height_m": NATIVE_HEIGHT,
                "filename": assembled_path.name,
            }
        ],
        "massing_graph": massing_graph,
    }
    facade = facade_sheet_contract(skin)
    dimensions = {
        "width_m": NATIVE_WIDTH,
        "depth_m": NATIVE_DEPTH,
        "podium_height_m": PODIUM_HEIGHT,
        "floor_height_m": FLOOR_HEIGHT,
        "setback_height_m": FLOOR_HEIGHT,
        "roof_height_m": ROOF_HEIGHT,
        "crown_height_m": CROWN_HEIGHT,
    }
    manifest = {
        "manifest_schema": 3,
        "grammar_schema_version": 3,
        "generator": {
            "name": "archetype_compiler/generate_wave10_corten_library_family.py",
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
        "aesthetic_category_id": "institutional_civic",
        "development_type": "institutional",
        "reuse_keys": REUSE_KEYS,
        "generation_tags": [
            "wave10",
            "fixed_landmark",
            "corten_arch_library",
            "physical_curtain_wall",
            "occupied_reading_depth",
            "flexible_fallback_stack",
        ],
        "footprint_compatibility": footprint,
        "coordinate_contract": COORDINATE_CONTRACT,
        "textures": texture_inventory(skin),
        "facade_sheet": facade,
        "dimensions": dimensions,
        "native_width_m": NATIVE_WIDTH,
        "native_depth_m": NATIVE_DEPTH,
        "native_height_m": NATIVE_HEIGHT,
        "native_floors": NATIVE_FLOORS,
        "min_floors": MIN_FLOORS,
        "max_floors": MAX_FLOORS,
        "modules": modules,
        "assembled": assembled,
        "package_profile": "fixed_landmark_with_flexible_lego_stack",
        "thumbnail": f"{FAMILY}_preview.png",
        "renders": renders,
        "architectural_identity": (
            "One continuous weathering-steel barrel arch rises from grade to "
            "enclose a physically recessed triangular-lattice curtain wall, "
            "four occupied reading levels and a broad concrete civic stair."
        ),
        "material_zones": (
            "variegated burnt-sienna weathering-steel panels; pale board-formed "
            "concrete; honed precast stairs; dark-bronze AESS ribs and mullions; "
            "neutral low-iron glass; honey-oak stacks and furniture; warm "
            "occupied reading depth; native campus planting"
        ),
        "glass_profile": GLASS_PROFILE,
        "source_provenance": {
            "catalogue_archetype_id": ARCHETYPE_ID,
            "catalogue_variant_id": VARIANT_ID,
            "catalogue_alias_ids": ALIASES[2:],
            "elevation_source": f"/families/{FAMILY}/elevation.jpg",
            "goalpost": (
                f"/families/{FAMILY}/textures/source/archetype-goalpost.png"
            ),
            "reference_generation": (
                f"/families/{FAMILY}/textures/source/reference-generation.json"
            ),
            "method": (
                "official material and envelope research, locked four-view "
                "ImageGen goalpost, six-zone construction plate, deterministic "
                "metric arch panels, physical glazing and populated depth"
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
            "reuse_keys": REUSE_KEYS,
        },
        "dimensions": {
            **dimensions,
            "default_floors": NATIVE_FLOORS,
            "min_floors": MIN_FLOORS,
            "max_floors": MAX_FLOORS,
        },
        "architectural_signature": {
            "identity": manifest["architectural_identity"],
            "material_zones": manifest["material_zones"],
            "glass_profile": GLASS_PROFILE,
            "kits": [
                "fixed_landmark",
                "continuous_corten_barrel_shell",
                "physical_triangular_curtain_wall",
                "ceremonial_stair",
                "flexible_fallback_stack",
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
    source = {
        "catalogue_archetype_id": ARCHETYPE_ID,
        "catalogue_variant_id": VARIANT_ID,
        "catalogue_alias_ids": ALIASES[2:],
        "elevation_source": f"/families/{FAMILY}/elevation.jpg",
        "goalpost": f"/families/{FAMILY}/textures/source/archetype-goalpost.png",
        "reference_generation": (
            f"/families/{FAMILY}/textures/source/reference-generation.json"
        ),
        "method": (
            "official technical research, locked multi-angle ImageGen source "
            "pack, clean PBR cells, deterministic metric arch construction and "
            "physical occupied curtain-wall glazing"
        ),
    }
    (folder / "archetype-source.json").write_text(
        json.dumps(source, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    elevation_source = folder / "textures" / "source" / "front-elevation-source-v1.png"
    if elevation_source.is_file():
        shutil.copyfile(elevation_source, folder / "elevation.jpg")
    print(
        f"[wave10-corten-library] {FAMILY}: "
        f"{assembled_triangles} triangles, {assembled_materials} materials, "
        f"{len(modules)} modules, {len(renders)} renders",
        flush=True,
    )


def render_existing(output_root: Path, *, view_set: str) -> None:
    clear_scene()
    folder = output_root / FAMILY
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
        f"[wave10-corten-library-render] "
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
