"""Generate the reference-locked parametric wave-shell aquatic-centre family.

This is a sculpted fixed landmark first, with a conservative semantic fallback
kit for LEGO sizing outside the clean whole-building scale band.  The model is
not a skinned box: its continuous unequal double-wave shell, saddle skylight,
cable masts, concrete branch supports, recessed entry, pool halls and service
elevations are physical geometry.

Run with Blender 5.x from the repository root:

    blender --background --factory-startup --python \
      tools/archetype_compiler/generate_wave10_aquatic_family.py -- \
      --output-root frontend/public/families --view-set pilot --skip-modules
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
    select_only,
    skin_material,
    texture_inventory,
)


FAMILY = "parametric-wave-shell-aquatic-centre"
ARCHETYPE_ID = "community_recreation_centre"
VARIANT_ID = "rec_centre_aquatic"
ALIASES = [
    ARCHETYPE_ID,
    VARIANT_ID,
    "aquatic_natatorium_complex",
    "parametric_wave_shell",
]
LABEL = "Community Recreation Centre — Parametric Wave-Shell Aquatic Centre"
NATIVE_WIDTH = 80.0
NATIVE_DEPTH = 55.0
NATIVE_HEIGHT = 20.0
NATIVE_FLOORS = 1
MIN_FLOORS = 1
MAX_FLOORS = 2
PODIUM_HEIGHT = 4.5
FLOOR_HEIGHT = 3.0
CROWN_HEIGHT = 1.0
ROOF_HEIGHT = 11.5

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
    parser.add_argument("--view-set", choices=("pilot", "all"), default="all")
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
    bsdf = bsdf_for(mat)
    socket = bsdf.inputs["Base Color"]
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


def make_glass_material(
    name: str,
    color: tuple[float, float, float, float],
    *,
    roughness: float,
    transmission: float,
    profile: str,
) -> bpy.types.Material:
    mat = material(name, color, roughness, metallic=0.02)
    bsdf = bsdf_for(mat)
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    if bsdf.inputs.get("Transmission Weight"):
        bsdf.inputs["Transmission Weight"].default_value = transmission
    if bsdf.inputs.get("Coat Weight"):
        bsdf.inputs["Coat Weight"].default_value = 0.18
    if bsdf.inputs.get("Coat Roughness"):
        bsdf.inputs["Coat Roughness"].default_value = 0.08
    if bsdf.inputs.get("IOR"):
        bsdf.inputs["IOR"].default_value = 1.45
    if bsdf.inputs.get("Alpha"):
        bsdf.inputs["Alpha"].default_value = color[3]
    try:
        mat.surface_render_method = "DITHERED"
    except Exception:
        pass
    mat.use_transparency_overlap = False
    mat["glazing_profile"] = profile
    mat["glazing_lod"] = "physical_separate_pane"
    mat["source_variant_id"] = VARIANT_ID
    mat["generation_archetype_id"] = VARIANT_ID
    mat["reference_locked"] = True
    return mat


def load_palette(folder: Path) -> tuple[dict[str, bpy.types.Material], dict]:
    skin = load_skin_manifest(folder)
    if not skin:
        raise FileNotFoundError(folder / "textures" / "skin_manifest.json")
    near = {zone: values["near"] for zone, values in skin["zones"].items()}
    mats: dict[str, bpy.types.Material] = {}
    mats["roof"] = grade_material(
        skin_material(
            "MAT_W10_AQUA_PlatinumStandingSeamRoof",
            folder,
            near["roof_metal"],
            "roof_metal",
            metallic=0.68,
        ),
        saturation=0.68,
        value=0.82,
    )
    mats["timber"] = grade_material(
        skin_material(
            "MAT_W10_AQUA_HoneyGlulamAndSoffit",
            folder,
            near["timber"],
            "timber",
        ),
        saturation=1.04,
        value=0.96,
    )
    mats["concrete"] = grade_material(
        skin_material(
            "MAT_W10_AQUA_PaleBoardFormedConcrete",
            folder,
            near["concrete"],
            "concrete",
        ),
        saturation=0.66,
        value=0.84,
    )
    mats["polycarbonate"] = grade_material(
        skin_material(
            "MAT_W10_AQUA_TranslucentRibbedPolycarbonate",
            folder,
            near["polycarbonate"],
            "polycarbonate",
            transmission=0.22,
            emission_strength=0.14,
        ),
        saturation=0.78,
        value=0.92,
    )
    poly_bsdf = bsdf_for(mats["polycarbonate"])
    if poly_bsdf.inputs.get("Alpha"):
        poly_bsdf.inputs["Alpha"].default_value = 0.82
    try:
        mats["polycarbonate"].surface_render_method = "DITHERED"
    except Exception:
        pass
    mats["cobalt"] = grade_material(
        skin_material(
            "MAT_W10_AQUA_CobaltMicroperforatedPanel",
            folder,
            near["cobalt_panel"],
            "cobalt_panel",
            metallic=0.34,
        ),
        saturation=1.08,
        value=0.82,
    )
    mats["plinth"] = grade_material(
        skin_material(
            "MAT_W10_AQUA_CharcoalHonedPlinth",
            folder,
            near["plinth"],
            "plinth",
        ),
        saturation=0.48,
        value=0.72,
    )
    mats["deck"] = grade_material(
        skin_material(
            "MAT_W10_AQUA_PaleWetDeck",
            folder,
            near["wet_deck"],
            "wet_deck",
        ),
        saturation=0.62,
        value=0.90,
    )
    mats["landscape"] = grade_material(
        skin_material(
            "MAT_W10_AQUA_BioswaleLandscape",
            folder,
            near["landscape"],
            "landscape",
        ),
        saturation=0.95,
        value=0.76,
    )
    mats["interior"] = grade_material(
        skin_material(
            "MAT_W10_AQUA_RegisteredCompetitionPoolDepth",
            folder,
            near["interior"],
            "interior",
            emission_strength=0.82,
        ),
        saturation=0.96,
        value=0.90,
    )
    mats["interior"]["underlay_role"] = (
        "occupied_depth_behind_physical_glazing"
    )
    mats["interior"]["source_variant_id"] = VARIANT_ID
    mats["interior"]["reference_locked"] = True
    mats["glass"] = make_glass_material(
        "MAT_W10_AQUA_LowIronPoolCurtainWall",
        (0.10, 0.24, 0.28, 0.40),
        roughness=0.16,
        transmission=0.30,
        profile="aquatic_low_iron_pool_clear",
    )
    mats["skylight"] = make_glass_material(
        "MAT_W10_AQUA_SaddleValleySkylight",
        (0.22, 0.43, 0.52, 0.68),
        roughness=0.17,
        transmission=0.20,
        profile="aquatic_roof_daylight_clear",
    )
    mats["water"] = make_glass_material(
        "MAT_W10_AQUA_CompetitionPoolWater",
        (0.02, 0.42, 0.66, 0.78),
        roughness=0.08,
        transmission=0.22,
        profile="aquatic_pool_water",
    )
    mats["water"]["underlay_role"] = "physical_pool_water_depth"
    mats["dark"] = material(
        "MAT_W10_AQUA_BlackThermalBreakAndCable",
        (0.018, 0.024, 0.030, 1.0),
        0.29,
        metallic=0.64,
    )
    mats["white"] = material(
        "MAT_W10_AQUA_WhiteDivingStructure",
        (0.68, 0.71, 0.70, 1.0),
        0.40,
        metallic=0.04,
    )
    mats["warm_light"] = material(
        "MAT_W10_AQUA_IntegratedWarmLinearLight",
        (0.88, 0.52, 0.18, 1.0),
        0.24,
        emission=(1.0, 0.42, 0.12, 1.0),
        emission_strength=3.8,
    )
    mats["lobby"] = material(
        "MAT_W10_AQUA_WarmOccupiedLobbyDepth",
        (0.22, 0.15, 0.065, 1.0),
        0.38,
        emission=(0.62, 0.32, 0.06, 1.0),
        emission_strength=0.25,
    )
    mats["lane_blue"] = material(
        "MAT_W10_AQUA_LaneBlue",
        (0.015, 0.10, 0.33, 1.0),
        0.38,
    )
    mats["lane_white"] = material(
        "MAT_W10_AQUA_LaneWhite",
        (0.86, 0.89, 0.88, 1.0),
        0.40,
    )
    return mats, skin


def mesh_object(
    name: str,
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, ...]],
    mat: bpy.types.Material,
    *,
    uvs: list[tuple[float, float]] | None = None,
) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    if uvs:
        layer = mesh.uv_layers.new(name="UVMap")
        for polygon in mesh.polygons:
            for loop_index in polygon.loop_indices:
                vertex_index = mesh.loops[loop_index].vertex_index
                layer.data[loop_index].uv = uvs[vertex_index]
    return obj


ROOF_CONTROLS = (
    (-40.0, 8.25),
    (-31.0, 12.10),
    (-22.0, 14.00),
    (-10.0, 11.55),
    (3.0, 8.15),
    (15.0, 9.30),
    (27.0, 12.15),
    (40.0, 8.10),
)


def roof_cross_height(x: float) -> float:
    points = ROOF_CONTROLS
    if x <= points[0][0]:
        return points[0][1]
    if x >= points[-1][0]:
        return points[-1][1]
    index = next(
        i for i in range(len(points) - 1)
        if points[i][0] <= x <= points[i + 1][0]
    )
    x0, y0 = points[index]
    x1, y1 = points[index + 1]
    previous = points[max(0, index - 1)]
    following = points[min(len(points) - 1, index + 2)]
    m0 = (y1 - previous[1]) / (x1 - previous[0])
    m1 = (following[1] - y0) / (following[0] - x0)
    t = (x - x0) / (x1 - x0)
    h00 = 2 * t**3 - 3 * t**2 + 1
    h10 = t**3 - 2 * t**2 + t
    h01 = -2 * t**3 + 3 * t**2
    h11 = t**3 - t**2
    return h00 * y0 + h10 * (x1 - x0) * m0 + h01 * y1 + h11 * (
        x1 - x0
    ) * m1


def roof_height(x: float, y: float) -> float:
    longitudinal = 0.66 * max(0.0, 1.0 - (y / 27.5) ** 2)
    return roof_cross_height(x) + longitudinal


def create_surface(
    name: str,
    mat: bpy.types.Material,
    *,
    offset_z: float,
    x_steps: int = 64,
    y_steps: int = 22,
) -> bpy.types.Object:
    vertices: list[tuple[float, float, float]] = []
    uvs: list[tuple[float, float]] = []
    for yi in range(y_steps + 1):
        y = -27.5 + 55.0 * yi / y_steps
        for xi in range(x_steps + 1):
            x = -40.0 + 80.0 * xi / x_steps
            vertices.append((x, y, roof_height(x, y) + offset_z))
            uvs.append((xi / x_steps * 4.0, yi / y_steps * 2.0))
    faces: list[tuple[int, ...]] = []
    row = x_steps + 1
    for yi in range(y_steps):
        for xi in range(x_steps):
            a = yi * row + xi
            b = a + 1
            c = a + row + 1
            d = a + row
            faces.append((a, b, c, d))
    return mesh_object(name, vertices, faces, mat, uvs=uvs)


def create_edge_strip(
    name: str,
    mat: bpy.types.Material,
    *,
    axis: str,
    fixed: float,
    offset_z: float = 0.0,
    steps: int = 64,
    drop: float = 0.42,
) -> bpy.types.Object:
    vertices: list[tuple[float, float, float]] = []
    uvs: list[tuple[float, float]] = []
    for index in range(steps + 1):
        if axis == "x":
            x = -40.0 + 80.0 * index / steps
            y = fixed
        else:
            x = fixed
            y = -27.5 + 55.0 * index / steps
        top = roof_height(x, y) + offset_z
        vertices.extend(((x, y, top), (x, y, top - drop)))
        u = index / steps * 3.0
        uvs.extend(((u, 1.0), (u, 0.0)))
    faces = [
        (index * 2, index * 2 + 2, index * 2 + 3, index * 2 + 1)
        for index in range(steps)
    ]
    return mesh_object(name, vertices, faces, mat, uvs=uvs)


def polyline_tube(
    name: str,
    points: list[tuple[float, float, float]],
    radius: float,
    mat: bpy.types.Material,
    *,
    resolution: int = 1,
) -> bpy.types.Object:
    curve = bpy.data.curves.new(f"{name}_Curve", type="CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = resolution
    curve.bevel_resolution = 1
    curve.bevel_depth = radius
    curve.resolution_u = 1
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, value in zip(spline.points, points):
        point.co = (*value, 1.0)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    select_only([obj])
    bpy.ops.object.convert(target="MESH")
    return bpy.context.object


def rect_beam(
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    width: float,
    depth: float,
    mat: bpy.types.Material,
) -> bpy.types.Object:
    a, b = Vector(start), Vector(end)
    delta = b - a
    obj = box(
        name,
        (width, depth, delta.length),
        tuple((a + b) * 0.5),
        mat,
        min(width, depth) * 0.08,
    )
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0.0, 0.0, 1.0)).rotation_difference(
        delta.normalized()
    )
    return obj


def trapezoid_prism(
    name: str,
    *,
    x0: float,
    x1: float,
    y0: float,
    y1: float,
    bottom: float,
    top0: float,
    top1: float,
    mat: bpy.types.Material,
    uv_rect: tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0),
) -> bpy.types.Object:
    vertices = [
        (x0, y0, bottom),
        (x1, y0, bottom),
        (x1, y0, top1),
        (x0, y0, top0),
        (x0, y1, bottom),
        (x1, y1, bottom),
        (x1, y1, top1),
        (x0, y1, top0),
    ]
    faces = [
        (0, 1, 2, 3),
        (5, 4, 7, 6),
        (4, 0, 3, 7),
        (1, 5, 6, 2),
        (3, 2, 6, 7),
        (4, 5, 1, 0),
    ]
    u0, v0, u1, v1 = uv_rect
    uvs = [
        (u0, v0),
        (u1, v0),
        (u1, v1),
        (u0, v1),
        (u0, v0),
        (u1, v0),
        (u1, v1),
        (u0, v1),
    ]
    return mesh_object(name, vertices, faces, mat, uvs=uvs)


def create_roof_system(
    mats: dict[str, bpy.types.Material],
    *,
    vertical_offset: float = 0.0,
    mast_top: float = NATIVE_HEIGHT,
    full_detail: bool = True,
) -> list[bpy.types.Object]:
    objects = [
        create_surface(
            "AquaticContinuousDoubleWaveShell",
            mats["roof"],
            offset_z=vertical_offset,
        ),
        create_surface(
            "AquaticWarmTimberWaveSoffit",
            mats["timber"],
            offset_z=vertical_offset - 0.42,
        ),
        create_edge_strip(
            "AquaticFrontContinuousWaveFascia",
            mats["roof"],
            axis="x",
            fixed=-27.5,
            offset_z=vertical_offset,
            drop=0.68,
        ),
        create_edge_strip(
            "AquaticRearContinuousWaveFascia",
            mats["roof"],
            axis="x",
            fixed=27.5,
            offset_z=vertical_offset,
            drop=0.68,
        ),
        create_edge_strip(
            "AquaticLeftContinuousWaveFascia",
            mats["roof"],
            axis="y",
            fixed=-40.0,
            offset_z=vertical_offset,
            steps=44,
            drop=0.56,
        ),
        create_edge_strip(
            "AquaticRightContinuousWaveFascia",
            mats["roof"],
            axis="y",
            fixed=40.0,
            offset_z=vertical_offset,
            steps=44,
            drop=0.56,
        ),
    ]
    if full_detail:
        for index, x in enumerate(
            -37.5 + 2.5 * value for value in range(31)
        ):
            points = [
                (
                    x,
                    -27.3 + 54.6 * step / 20.0,
                    roof_height(x, -27.3 + 54.6 * step / 20.0)
                    + vertical_offset
                    + 0.055,
                )
                for step in range(21)
            ]
            objects.append(
                polyline_tube(
                    f"AquaticStandingSeam_{index:02d}",
                    points,
                    0.035,
                    mats["roof"],
                )
            )
        for index, y in enumerate(-22.0 + 5.5 * value for value in range(9)):
            points = [
                (
                    -39.2 + 78.4 * step / 40.0,
                    y,
                    roof_height(-39.2 + 78.4 * step / 40.0, y)
                    + vertical_offset
                    - 0.55,
                )
                for step in range(41)
            ]
            objects.append(
                polyline_tube(
                    f"AquaticGlulamWaveRib_{index:02d}",
                    points,
                    0.17,
                    mats["timber"],
                )
            )
    for strip_index, (x0, x1) in enumerate(((1.1, 2.4), (3.6, 4.9))):
        vertices: list[tuple[float, float, float]] = []
        uvs: list[tuple[float, float]] = []
        steps = 24
        for step in range(steps + 1):
            y = -24.0 + 48.0 * step / steps
            vertices.extend(
                (
                    (x0, y, roof_height(x0, y) + vertical_offset + 0.025),
                    (x1, y, roof_height(x1, y) + vertical_offset + 0.025),
                )
            )
            uvs.extend(((0.0, step / steps), (1.0, step / steps)))
        faces = [
            (index * 2, index * 2 + 1, index * 2 + 3, index * 2 + 2)
            for index in range(steps)
        ]
        objects.append(
            mesh_object(
                f"AquaticSaddleValleySkylight_{strip_index}",
                vertices,
                faces,
                mats["skylight"],
                uvs=uvs,
            )
        )
    mast_locations = ((-20.0, 1.0), (21.0, 1.0))
    for mast_index, (x, y) in enumerate(mast_locations):
        mast_base = roof_height(x, y) + vertical_offset - 0.15
        objects.append(
            cylinder(
                f"AquaticCableStayMast_{mast_index}",
                0.18,
                mast_top - mast_base,
                (x, y, (mast_top + mast_base) * 0.5),
                mats["white"],
                vertices=20,
            )
        )
        top = (x, y, mast_top - 0.18)
        anchors = (
            (x - 11.5, -22.0),
            (x - 8.0, 0.0),
            (x - 10.0, 22.0),
            (x + 10.0, -22.0),
            (x + 8.0, 0.0),
            (x + 11.5, 22.0),
        )
        for cable_index, (anchor_x, anchor_y) in enumerate(anchors):
            anchor_x = max(-39.0, min(39.0, anchor_x))
            objects.append(
                beam(
                    f"AquaticMast_{mast_index}_TensionRod_{cable_index:02d}",
                    top,
                    (
                        anchor_x,
                        anchor_y,
                        roof_height(anchor_x, anchor_y)
                        + vertical_offset
                        + 0.10,
                    ),
                    0.035,
                    mats["dark"],
                )
            )
    return objects


def add_front_curtain_wall(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    bay_width = 5.0
    for bay in range(16):
        x0 = -40.0 + bay * bay_width
        x1 = x0 + bay_width
        centre = (x0 + x1) * 0.5
        entry_bay = 7.5 <= centre <= 22.5
        bottom = 4.85 if entry_bay else 0.72
        top0 = roof_height(x0, -27.25) - 0.58
        top1 = roof_height(x1, -27.25) - 0.58
        objects.append(
            trapezoid_prism(
                f"AquaticFrontBay_{bay:02d}_PhysicalLowIronPane",
                x0=x0 + 0.08,
                x1=x1 - 0.08,
                y0=-27.28,
                y1=-27.20,
                bottom=bottom,
                top0=top0,
                top1=top1,
                mat=mats["glass"],
                uv_rect=(bay / 16.0, 0.0, (bay + 1) / 16.0, 1.0),
            )
        )
    for index, x in enumerate(-40.0 + 5.0 * value for value in range(17)):
        top = roof_height(x, -27.25) - 0.40
        objects.append(
            box(
                f"AquaticFrontCurtainWallMullion_{index:02d}",
                (0.12, 0.16, top - 0.60),
                (x, -27.35, (top + 0.60) * 0.5),
                mats["dark"],
                0.012,
            )
        )
    for level, z in enumerate((4.05, 7.55)):
        for x, width in ((-20.0, 40.0), (30.0, 20.0)):
            objects.append(
                box(
                    f"AquaticFrontCurtainWallTransom_{level}_{x:+.0f}",
                    (width, 0.16, 0.12),
                    (x, -27.35, z),
                    mats["dark"],
                    0.01,
                )
            )
    return objects


def add_branch_supports(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    # One uninterrupted member runs from each plinth bearing to the wave edge.
    # The alternating lean forms the reference facade's W rhythm without the
    # mid-air Y joints that made the supports look applied.
    support_pairs = (
        (-35.0, -30.0),
        (-27.0, -21.0),
        (-18.0, -24.0),
        (-10.0, -4.0),
        (-2.0, -8.0),
        (26.0, 32.0),
        (34.0, 28.0),
        (39.0, 35.0),
    )
    for index, (base_x, target_x) in enumerate(support_pairs):
        objects.append(
            rect_beam(
                f"AquaticConcreteIntegratedBranchSupport_{index:02d}",
                (base_x, -27.20, 0.25),
                (
                    target_x,
                    -26.88,
                    roof_height(target_x, -27.0) - 0.50,
                ),
                0.76,
                0.86,
                mats["concrete"],
            )
        )
    return objects


def add_entry(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects = [
        box(
            "AquaticRecessedPublicEntryGlazing",
            (20.0, 0.12, 4.55),
            (15.0, -25.72, 2.58),
            mats["glass"],
            0.02,
        ),
        box(
            "AquaticIntegratedEntryCanopyTimberSoffit",
            (20.0, 3.25, 0.30),
            (15.0, -26.0, 5.12),
            mats["timber"],
            0.08,
        ),
        box(
            "AquaticIntegratedEntryCanopySilverEdge",
            (20.25, 3.42, 0.18),
            (15.0, -26.0, 5.29),
            mats["roof"],
            0.06,
        ),
        box(
            "AquaticEntryDoorLeftPhysicalGlass",
            (2.35, 0.12, 3.30),
            (12.2, -25.83, 1.95),
            mats["glass"],
            0.02,
        ),
        box(
            "AquaticEntryDoorRightPhysicalGlass",
            (2.35, 0.12, 3.30),
            (17.8, -25.83, 1.95),
            mats["glass"],
            0.02,
        ),
        box(
            "AquaticEntryWarmLobbyBackdrop",
            (18.8, 0.12, 3.8),
            (15.0, -23.10, 2.45),
            mats["lobby"],
            0.08,
        ),
        box(
            "AquaticEntryWarmLobbyCeiling",
            (18.8, 3.0, 0.16),
            (15.0, -24.30, 4.30),
            mats["timber"],
            0.05,
        ),
        box(
            "AquaticEntryWarmLobbyFloor",
            (18.8, 3.0, 0.10),
            (15.0, -24.30, 0.60),
            mats["deck"],
            0.025,
        ),
        box(
            "AquaticEntryDarkPortalHeader",
            (19.4, 0.34, 0.40),
            (15.0, -25.60, 4.48),
            mats["dark"],
            0.03,
        ),
        box(
            "AquaticEntryDarkPortalLeft",
            (0.34, 0.34, 4.35),
            (5.47, -25.60, 2.30),
            mats["dark"],
            0.03,
        ),
        box(
            "AquaticEntryDarkPortalRight",
            (0.34, 0.34, 4.35),
            (24.53, -25.60, 2.30),
            mats["dark"],
            0.03,
        ),
        box(
            "AquaticEntryWarmReceptionCounter",
            (4.8, 0.8, 1.05),
            (17.2, -23.35, 0.98),
            mats["timber"],
            0.08,
        ),
    ]
    for index, x in enumerate((9.3, 20.7)):
        objects.append(
            cylinder(
                f"AquaticEntryCanopyColumn_{index}",
                0.18,
                4.95,
                (x, -26.1, 2.48),
                mats["concrete"],
                vertices=16,
            )
        )
    for x in (5.5, 7.7, 9.9, 12.2, 15.0, 17.8, 20.1, 22.3, 24.5):
        objects.append(
            box(
                f"AquaticEntryPressureCap_{x:.1f}",
                (0.10, 0.15, 4.35),
                (x, -25.90, 2.52),
                mats["dark"],
                0.01,
            )
        )
    for index, x in enumerate((10.1, 12.55, 15.0, 17.45, 19.9)):
        objects.append(
            box(
                f"AquaticEntryDoorLeaf_{index:02d}_PhysicalGlass",
                (2.25, 0.10, 3.25),
                (x, -25.78, 1.92),
                mats["glass"],
                0.015,
            )
        )
        objects.append(
            box(
                f"AquaticEntryDoorHandle_{index:02d}",
                (0.045, 0.10, 0.72),
                (x + 0.62, -25.86, 1.60),
                mats["dark"],
                0.008,
            )
        )
    return objects


def add_registered_interior(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = [
        box(
            "AquaticDarkContinuousPlinthSlab",
            (79.4, 54.4, 0.36),
            (0.0, 0.0, 0.18),
            mats["plinth"],
            0.08,
        ),
        box(
            "AquaticPaleWetDeck",
            (75.8, 50.8, 0.20),
            (0.0, 0.6, 0.43),
            mats["deck"],
            0.05,
        ),
        box(
            "AquaticCompetitionPoolWater",
            (30.0, 46.0, 0.10),
            (-17.0, 1.0, 0.62),
            mats["water"],
            0.02,
        ),
        box(
            "AquaticLeisurePoolWater",
            (17.0, 28.0, 0.10),
            (22.5, 2.0, 0.62),
            mats["water"],
            0.02,
        ),
        trapezoid_prism(
            "AquaticCompetitionHallRegisteredOccupiedDepth",
            x0=-38.0,
            x1=5.0,
            y0=-26.93,
            y1=-26.90,
            bottom=0.72,
            top0=10.25,
            top1=8.55,
            mat=mats["interior"],
        ),
        trapezoid_prism(
            "AquaticLeisureHallRegisteredOccupiedDepth",
            x0=25.0,
            x1=38.0,
            y0=-26.93,
            y1=-26.90,
            bottom=0.72,
            top0=9.55,
            top1=10.15,
            mat=mats["interior"],
            uv_rect=(0.56, 0.0, 1.0, 1.0),
        ),
    ]
    for lane in range(8):
        x = -29.8 + lane * 3.65
        objects.append(
            box(
                f"AquaticCompetitionLaneLine_{lane:02d}",
                (0.11, 43.5, 0.035),
                (x, 1.0, 0.685),
                mats["lane_white" if lane in (0, 7) else "lane_blue"],
                0.01,
            )
        )
        objects.append(
            box(
                f"AquaticStartingBlock_{lane:02d}",
                (0.72, 0.90, 0.22),
                (x, -21.1, 0.86),
                mats["white"],
                0.06,
            )
        )
    objects.extend(
        [
            cylinder(
                "AquaticDivingTowerColumn",
                0.42,
                9.2,
                (-34.0, 5.8, 4.90),
                mats["white"],
                vertices=24,
            ),
            box(
                "AquaticDivingTowerPlatform_3m",
                (5.0, 1.6, 0.28),
                (-31.8, 5.8, 3.15),
                mats["white"],
                0.10,
            ),
            box(
                "AquaticDivingTowerPlatform_5m",
                (4.3, 1.5, 0.28),
                (-32.1, 5.8, 5.25),
                mats["white"],
                0.10,
            ),
            box(
                "AquaticDivingTowerPlatform_8m",
                (3.7, 1.4, 0.28),
                (-32.4, 5.8, 8.25),
                mats["white"],
                0.10,
            ),
        ]
    )
    for step in range(5):
        objects.append(
            box(
                f"AquaticSpectatorGalleryTier_{step:02d}",
                (5.5 - step * 0.55, 26.0, 0.32),
                (35.2 + step * 0.28, 4.0, 0.78 + step * 0.52),
                mats["timber"],
                0.04,
            )
        )
    for index, y in enumerate(-20.0 + 5.0 * value for value in range(9)):
        objects.append(
            box(
                f"AquaticIntegratedWarmLinearLight_{index:02d}",
                (62.0, 0.055, 0.055),
                (-1.0, y, 7.65),
                mats["warm_light"],
                0.01,
            )
        )
    return objects


def add_side_and_rear_envelope(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    for side_index, x in enumerate((-39.78, 39.78)):
        height_base = roof_height(x, 0.0) - 0.52
        for bay in range(11):
            y = -25.0 + bay * 5.0
            front_clear = y <= -12.5
            upper_mat = mats["glass"] if front_clear else mats["polycarbonate"]
            objects.append(
                box(
                    f"AquaticSide_{side_index}_Bay_{bay:02d}_CobaltPlinth",
                    (0.22, 4.82, 2.65),
                    (x, y, 1.55),
                    mats["cobalt"],
                    0.03,
                )
            )
            objects.append(
                box(
                    f"AquaticSide_{side_index}_Bay_{bay:02d}_"
                    + ("PhysicalGlass" if front_clear else "RibbedPolycarbonate"),
                    (0.20, 4.78, max(0.8, height_base - 3.08)),
                    (x, y, (height_base + 3.08) * 0.5),
                    upper_mat,
                    0.025,
                )
            )
        for index, y in enumerate(-27.5 + 5.0 * value for value in range(12)):
            objects.append(
                box(
                    f"AquaticSide_{side_index}_VerticalFrame_{index:02d}",
                    (0.30, 0.13, height_base - 0.55),
                    (x, y, (height_base + 0.55) * 0.5),
                    mats["dark"],
                    0.015,
                )
            )
    for bay in range(16):
        x = -37.5 + bay * 5.0
        top = roof_height(x, 27.25) - 0.55
        service_door = bay in (2, 13)
        objects.append(
            box(
                f"AquaticRearBay_{bay:02d}_CobaltServiceBase",
                (4.82, 0.22, 2.72),
                (x, 27.30, 1.58),
                mats["cobalt"],
                0.03,
            )
        )
        objects.append(
            trapezoid_prism(
                f"AquaticRearBay_{bay:02d}_RibbedPolycarbonate",
                x0=x - 2.38,
                x1=x + 2.38,
                y0=27.18,
                y1=27.36,
                bottom=3.05,
                top0=top,
                top1=top,
                mat=mats["polycarbonate"],
            )
        )
        if service_door:
            objects.append(
                box(
                    f"AquaticRearServiceDoor_{bay:02d}",
                    (1.65, 0.30, 2.35),
                    (x, 27.13, 1.40),
                    mats["dark"],
                    0.05,
                )
            )
    for x in (-29.0, 29.0):
        objects.append(
            box(
                f"AquaticRearRecessedMechanicalLouver_{x:+.0f}",
                (8.0, 0.34, 1.45),
                (x, 27.05, 3.50),
                mats["dark"],
                0.04,
            )
        )
    return objects


def build_assembled(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    objects.extend(add_registered_interior(mats))
    objects.extend(add_front_curtain_wall(mats))
    objects.extend(add_branch_supports(mats))
    objects.extend(add_entry(mats))
    objects.extend(add_side_and_rear_envelope(mats))
    objects.extend(create_roof_system(mats))
    for index, x in enumerate((-37.5, 37.5)):
        objects.append(
            box(
                f"AquaticFrontCobaltBookendPanel_{index}",
                (5.0, 0.24, 3.05),
                (x, -27.26, 1.67),
                mats["cobalt"],
                0.04,
            )
        )
    for segment, (x, width) in enumerate(((-23.5, 31.0), (30.5, 18.0))):
        objects.append(
            box(
                f"AquaticFrontCharcoalPlinth_{segment}",
                (width, 0.45, 0.65),
                (x, -27.15, 0.40),
                mats["plinth"],
                0.05,
            )
        )
    return objects


def build_module(
    role: str,
    variant: str,
    mats: dict[str, bpy.types.Material],
) -> tuple[list[bpy.types.Object], float]:
    objects: list[bpy.types.Object] = []
    if role == "podium":
        height = PODIUM_HEIGHT
        objects.extend(
            [
                box(
                    "AquaticFallbackPodium",
                    (79.2, 54.2, 0.42),
                    (0.0, 0.0, 0.21),
                    mats["plinth"],
                    0.08,
                ),
                box(
                    "AquaticFallbackPodiumFrontGlass",
                    (78.0, 0.22, 3.45),
                    (0.0, -27.0, 2.10),
                    mats["glass"],
                    0.04,
                ),
                box(
                    "AquaticFallbackPodiumSideLeft",
                    (0.24, 53.0, 2.75),
                    (-39.5, 0.0, 1.60),
                    mats["cobalt"],
                    0.05,
                ),
                box(
                    "AquaticFallbackPodiumSideRight",
                    (0.24, 53.0, 2.75),
                    (39.5, 0.0, 1.60),
                    mats["cobalt"],
                    0.05,
                ),
                box(
                    "AquaticFallbackRecessedEntrance",
                    (15.0, 1.2, 3.55),
                    (15.0, -26.1, 2.12),
                    mats["interior"],
                    0.06,
                ),
            ]
        )
    elif role == "floor":
        height = FLOOR_HEIGHT
        zone = (
            mats["glass"]
            if variant == "typical_a"
            else mats["polycarbonate"]
            if variant == "typical_b"
            else mats["cobalt"]
        )
        objects.extend(
            [
                box(
                    f"AquaticFallbackFloor_{variant}_Front",
                    (78.5, 0.20, 2.72),
                    (0.0, -27.0, 1.50),
                    zone,
                    0.03,
                ),
                box(
                    f"AquaticFallbackFloor_{variant}_Rear",
                    (78.5, 0.20, 2.72),
                    (0.0, 27.0, 1.50),
                    mats["polycarbonate"],
                    0.03,
                ),
                box(
                    f"AquaticFallbackFloor_{variant}_Left",
                    (0.20, 53.5, 2.72),
                    (-39.5, 0.0, 1.50),
                    mats["polycarbonate"],
                    0.03,
                ),
                box(
                    f"AquaticFallbackFloor_{variant}_Right",
                    (0.20, 53.5, 2.72),
                    (39.5, 0.0, 1.50),
                    mats["polycarbonate"],
                    0.03,
                ),
            ]
        )
        for x in range(-35, 40, 5):
            objects.append(
                box(
                    f"AquaticFallbackFloor_{variant}_Mullion_{x:+03d}",
                    (0.10, 0.28, 2.82),
                    (float(x), -27.14, 1.50),
                    mats["dark"],
                    0.01,
                )
            )
    elif role == "crown":
        height = CROWN_HEIGHT
        objects.extend(
            [
                box(
                    "AquaticFallbackCrownFront",
                    (80.0, 0.30, 0.76),
                    (0.0, -27.25, 0.50),
                    mats["roof"],
                    0.05,
                ),
                box(
                    "AquaticFallbackCrownRear",
                    (80.0, 0.30, 0.76),
                    (0.0, 27.25, 0.50),
                    mats["roof"],
                    0.05,
                ),
                box(
                    "AquaticFallbackCrownLeft",
                    (0.30, 55.0, 0.76),
                    (-39.85, 0.0, 0.50),
                    mats["roof"],
                    0.05,
                ),
                box(
                    "AquaticFallbackCrownRight",
                    (0.30, 55.0, 0.76),
                    (39.85, 0.0, 0.50),
                    mats["roof"],
                    0.05,
                ),
            ]
        )
    else:
        height = ROOF_HEIGHT
        objects.extend(
            create_roof_system(
                mats,
                vertical_offset=-7.95,
                mast_top=ROOF_HEIGHT,
                full_detail=False,
            )
        )
    if role != "roof":
        objects.extend(module_contract_markers(role, variant, height))
    return objects, height


def evaluated_triangle_count(objects: list[bpy.types.Object]) -> int:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    count = 0
    for obj in objects:
        if obj.type != "MESH":
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        count += sum(max(1, len(polygon.vertices) - 2) for polygon in mesh.polygons)
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


def normalize_bottom_origin(objects: list[bpy.types.Object]) -> None:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    minimum_z = min(
        (evaluated.matrix_world @ Vector(corner)).z
        for obj in objects
        for evaluated in (obj.evaluated_get(depsgraph),)
        for corner in evaluated.bound_box
    )
    for obj in objects:
        obj.location.z -= minimum_z
    bpy.context.view_layer.update()


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
        "allowed_levels": [],
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


def add_presentation_context(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    ground = material(
        "MAT_W10_AQUA_PresentationPaving",
        (0.22, 0.215, 0.205, 1.0),
        0.76,
    )
    soil = material(
        "MAT_W10_AQUA_PresentationSoil",
        (0.08, 0.065, 0.045, 1.0),
        0.92,
    )
    leaf = material(
        "MAT_W10_AQUA_PresentationLeaves",
        (0.055, 0.19, 0.045, 1.0),
        0.82,
    )
    leaf_light = material(
        "MAT_W10_AQUA_PresentationLeavesLight",
        (0.12, 0.31, 0.07, 1.0),
        0.80,
    )
    person = material(
        "MAT_W10_AQUA_PresentationPeople",
        (0.12, 0.14, 0.16, 1.0),
        0.72,
    )
    objects = [
        box(
            "PRESENTATION_AquaticGround",
            (150.0, 130.0, 0.18),
            (0.0, 0.0, -0.16),
            ground,
            0.02,
        ),
        box(
            "PRESENTATION_AquaticBioswaleSoil",
            (72.0, 4.5, 0.20),
            (-3.0, -33.0, 0.02),
            soil,
            0.30,
        ),
        box(
            "PRESENTATION_AquaticEntryWalk",
            (22.0, 12.0, 0.08),
            (15.0, -32.0, 0.02),
            mats["deck"],
            0.08,
        ),
    ]
    for index in range(34):
        x = -36.0 + index * 2.1
        y = -33.0 + 0.55 * math.sin(index * 1.7)
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=1,
            radius=0.55 + 0.16 * (index % 3),
            location=(x, y, 0.36),
        )
        plant = bpy.context.object
        plant.name = f"PRESENTATION_BioswalePlant_{index:02d}"
        plant.scale = (0.72, 0.55, 0.86)
        plant.data.materials.append(leaf if index % 3 else leaf_light)
        select_only([plant])
        bpy.ops.object.shade_smooth()
        objects.append(plant)
    for index, (x, y) in enumerate(
        ((-49, -24), (-40, -38), (43, -39), (50, -22), (-46, 25), (47, 24))
    ):
        trunk = cylinder(
            f"PRESENTATION_Tree_{index}_Trunk",
            0.22,
            4.6,
            (x, y, 2.3),
            mats["timber"],
            vertices=12,
        )
        objects.append(trunk)
        for crown_index, (dx, dy, dz) in enumerate(
            ((0, 0, 0), (-0.8, 0.2, -0.2), (0.7, -0.3, 0.1))
        ):
            bpy.ops.mesh.primitive_ico_sphere_add(
                subdivisions=2,
                radius=1.65,
                location=(x + dx, y + dy, 5.0 + dz),
            )
            crown = bpy.context.object
            crown.name = (
                f"PRESENTATION_Tree_{index}_Crown_{crown_index}"
            )
            crown.scale = (1.0, 0.82, 1.18)
            crown.data.materials.append(
                leaf if (index + crown_index) % 3 else leaf_light
            )
            select_only([crown])
            bpy.ops.object.shade_smooth()
            objects.append(crown)
    for index, (x, y) in enumerate(
        ((8, -33), (13, -34), (19, -32), (-19, -31), (-10, -35), (29, -31))
    ):
        objects.extend(
            [
                cylinder(
                    f"PRESENTATION_Person_{index}_Body",
                    0.16,
                    1.32,
                    (x, y, 0.76),
                    person,
                    vertices=10,
                ),
                cylinder(
                    f"PRESENTATION_Person_{index}_Head",
                    0.20,
                    0.28,
                    (x, y, 1.58),
                    mats["concrete"],
                    vertices=12,
                ),
            ]
        )
    return objects


def configure_render() -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 920
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.exposure = 0.08
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass
    for obj in list(bpy.data.objects):
        if obj.type == "LIGHT":
            bpy.data.objects.remove(obj, do_unlink=True)
    world = scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputWorld")
    background = nodes.new("ShaderNodeBackground")
    background.inputs["Strength"].default_value = 0.58
    coordinates = nodes.new("ShaderNodeTexCoord")
    separate = nodes.new("ShaderNodeSeparateXYZ")
    gradient = nodes.new("ShaderNodeValToRGB")
    gradient.color_ramp.elements[0].position = 0.0
    gradient.color_ramp.elements[0].color = (0.48, 0.66, 0.88, 1.0)
    gradient.color_ramp.elements[1].position = 0.72
    gradient.color_ramp.elements[1].color = (0.055, 0.20, 0.52, 1.0)
    links.new(coordinates.outputs["Normal"], separate.inputs["Vector"])
    links.new(separate.outputs["Z"], gradient.inputs["Fac"])
    links.new(gradient.outputs["Color"], background.inputs["Color"])
    links.new(background.outputs["Background"], output.inputs["Surface"])
    bpy.ops.object.light_add(type="SUN", location=(-80, -100, 120))
    sun = bpy.context.object
    sun.name = "PRESENTATION_AquaticSun"
    sun.data.energy = 2.45
    sun.data.color = (1.0, 0.84, 0.66)
    sun.data.angle = math.radians(6.0)
    sun.rotation_euler = (
        Vector((0.0, 0.0, 6.0)) - sun.location
    ).to_track_quat("-Z", "Y").to_euler()
    bpy.ops.object.light_add(type="AREA", location=(0.0, -38.0, 22.0))
    fill = bpy.context.object
    fill.name = "PRESENTATION_AquaticFacadeFill"
    fill.data.energy = 900.0
    fill.data.shape = "RECTANGLE"
    fill.data.size = 50.0
    fill.data.size_y = 18.0
    fill.rotation_euler = (
        Vector((0.0, 0.0, 6.5)) - fill.location
    ).to_track_quat("-Z", "Y").to_euler()
    bpy.ops.object.light_add(type="AREA", location=(0.0, -21.0, 8.5))
    interior = bpy.context.object
    interior.name = "PRESENTATION_AquaticWarmInteriorFill"
    interior.data.energy = 720.0
    interior.data.color = (1.0, 0.42, 0.16)
    interior.data.shape = "RECTANGLE"
    interior.data.size = 58.0
    interior.data.size_y = 5.0
    interior.rotation_euler = (
        Vector((0.0, -29.0, 4.5)) - interior.location
    ).to_track_quat("-Z", "Y").to_euler()


def render_views(
    folder: Path,
    mats: dict[str, bpy.types.Material],
    *,
    view_set: str,
) -> list[str]:
    context_objects = add_presentation_context(mats)
    configure_render()
    views = {
        "preview": ((62.0, -105.0, 21.0), (2.0, -2.0, 7.0), 58),
        "street": ((10.0, -100.0, 5.8), (2.0, -5.0, 6.2), 55),
        "front_corner_oblique": (
            (-66.0, -105.0, 18.0),
            (0.0, -3.0, 7.0),
            58,
        ),
        "rear_corner_oblique": (
            (74.0, 80.0, 31.0),
            (0.0, 0.0, 6.8),
            57,
        ),
        "aerial": ((72.0, -72.0, 76.0), (0.0, 0.0, 5.8), 55),
        "facade_close": ((0.0, -96.0, 7.5), (0.0, -5.0, 7.0), 62),
        "entry_close": ((34.0, -75.0, 7.5), (15.0, -20.0, 4.5), 64),
        "glazing_close": (
            (-53.0, -77.0, 7.0),
            (-20.0, -20.0, 5.0),
            63,
        ),
        "pool_close": ((-30.0, -48.0, 10.0), (-15.0, 1.0, 3.0), 68),
        "roof_close": ((50.0, -45.0, 42.0), (0.0, 0.0, 10.5), 62),
        "side_close": ((79.0, -4.0, 12.0), (23.0, 1.0, 5.5), 62),
        "structure_close": (
            (-47.0, -57.0, 12.0),
            (-22.0, -20.0, 8.5),
            64,
        ),
        "context": ((92.0, -105.0, 45.0), (0.0, 0.0, 7.0), 58),
    }
    pilot = {
        "preview",
        "front_corner_oblique",
        "aerial",
        "facade_close",
        "entry_close",
        "glazing_close",
        "roof_close",
    }
    selected = pilot if view_set == "pilot" else set(views)
    renders: list[str] = []
    for role, (location, target, lens) in views.items():
        if role not in selected:
            continue
        aim_camera(location, target, lens)
        scene = bpy.context.scene
        scene.render.filepath = str(folder / f"{FAMILY}_{role}.png")
        bpy.ops.render.render(write_still=True)
        renders.append(f"{FAMILY}_{role}.png")
    delete_objects(context_objects)
    return renders


def footprint_contract() -> dict:
    rectangle = {
        "recommendedWidth_m": [62.0, 98.0],
        "recommendedDepth_m": [43.0, 67.0],
        "recommendedFloors": [1, 2],
        "scaleMin": 0.78,
        "scaleMax": 1.22,
        "maxAxisRatio": 1.18,
        "preferredBayMultiple_m": 5.0,
    }
    return {
        "preferredProfiles": ["rectangle"],
        "minimumPreferredProfiles": 1,
        "profileRationale": (
            "The unequal double-wave shell, two masts and one public entrance "
            "form a singular long-span landmark. Mildly imperfect hand-drawn "
            "rectangles scale cleanly; non-rectangular sites must preserve the "
            "complete hall rather than bend or duplicate one crest."
        ),
        "fixedLandmarkScaleBand": {
            "scaleMin": 0.78,
            "scaleMax": 1.22,
            "maxAxisRatio": 1.18,
        },
        "preferredBayMultiple_m": 5.0,
        **rectangle,
        "profiles": {"rectangle": rectangle},
    }


def facade_sheet_contract(skin: dict) -> dict:
    contract = facade_contract(
        FAMILY,
        skin,
        "/families/parametric-wave-shell-aquatic-centre/"
        "textures/source/archetype-goalpost.png",
    )
    contract["geometry_detail_profile"] = "hero"
    contract["bay_strategy"] = {
        "fixed_end_bays": [
            "competition_crest",
            "saddle_entry",
            "leisure_crest",
            "two_cable_masts",
        ],
        "repeatable_middle_bays": [1, 2, 3],
        "middle_variants": ["typical_a", "typical_b", "typical_c"],
        "rule": (
            "The assembled landmark always preserves both unequal crests, the "
            "saddle, two masts, eight integrated supports and one entry. "
            "Only the out-of-band fallback kit repeats complete 5 m bays."
        ),
    }
    contract["assembly_contract"] = {
        "fixed": [
            "podium/entrance",
            "corner returns",
            "competition and leisure pool halls",
            "two cable-stay masts",
            "eight integrated concrete supports",
            "crown",
            "roof",
        ],
        "repeatable": ["typical_a", "typical_b", "typical_c"],
        "side_elevations": (
            "Full-height clear pool glazing turns into translucent ribbed "
            "polycarbonate above a cobalt service plinth; black frames, roof "
            "fascia and timber soffit continue around both sides and rear."
        ),
        "elevation_coverage": {
            "front": "double-wave pool curtain wall, branch supports and entry",
            "left": "clear pool glazing, cobalt base and shell landing",
            "right": "clear-to-translucent programme bays and cobalt base",
            "rear": "polycarbonate service bays, doors and recessed louvers",
            "roof": "continuous shell, standing seams, valley skylights, masts and cables",
        },
        "variation_policy": (
            "Scale the whole fixed landmark only inside 0.78–1.22 with an "
            "independent-axis ratio no greater than 1.18. Larger sites repeat "
            "complete halls through streetwall planning."
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
    payloads = []
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
    old_manifest_path = folder / f"{FAMILY}_manifest.json"
    old_manifest = (
        json.loads(old_manifest_path.read_text(encoding="utf-8"))
        if old_manifest_path.is_file()
        else {}
    )
    if not skip_assembled_export:
        export_glb(assembled_path, objects)
        assembled_triangles = evaluated_triangle_count(objects)
        assembled_materials = material_count(objects)
    else:
        assembled_triangles = int(
            (old_manifest.get("assembled") or {}).get("triangle_count")
            or evaluated_triangle_count(objects)
        )
        assembled_materials = int(
            (old_manifest.get("assembled") or {}).get("material_count")
            or material_count(objects)
        )
    renders = (
        list(old_manifest.get("renders") or [])
        if skip_renders
        else render_views(folder, mats, view_set=view_set)
    )
    delete_objects(objects)
    modules = (
        list(old_manifest.get("modules") or [])
        if skip_modules
        else build_modules(folder, mats, skin)
    )
    footprint = footprint_contract()
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
                "variant_key": "fixed_landmark",
                "level": 0,
                "z_m": 0.0,
                "height_m": NATIVE_HEIGHT,
            }
        ],
        "footprint_profile": "rectangle",
        "footprint_target": {
            "width_m": NATIVE_WIDTH,
            "depth_m": NATIVE_DEPTH,
            "wing_depth_m": NATIVE_DEPTH,
            "segments": [
                {
                    "id": "complete_natatorium",
                    "centre_x_m": 0.0,
                    "centre_y_m": 0.0,
                    "length_m": NATIVE_WIDTH,
                    "thickness_m": NATIVE_DEPTH,
                    "rotation_degrees": 0.0,
                }
            ],
        },
        "massing_graph": {
            "type": "fixed_landmark",
            "silhouette": "continuous_asymmetrical_double_wave_shell",
            "competition_crest": 1,
            "leisure_crest": 1,
            "glazed_saddle_valley": True,
            "cable_stay_masts": 2,
            "concrete_branch_support_assemblies": 8,
            "recessed_public_entrance": 1,
            "competition_pool_length_m": 50,
        },
        "texture_keys": sorted(skin["zones"]),
        "ao_baked": True,
    }
    manifest = {
        "manifest_schema": 3,
        "grammar_schema_version": 3,
        "generator": {
            "name": "archetype_compiler/generate_wave10_aquatic_family.py",
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
        "aesthetic_category_id": "institutional_civic_sports",
        "development_type": "civic_recreation",
        "reuse_keys": [
            *ALIASES,
            "aquatic_centre",
            "natatorium",
            "community recreation",
        ],
        "generation_tags": [
            "wave10",
            "fixed_landmark",
            "parametric_wave_shell",
            "large_span_aquatic",
            "physical_pool_glazing",
        ],
        "footprint_compatibility": footprint,
        "coordinate_contract": COORDINATE_CONTRACT,
        "textures": texture_inventory(skin),
        "facade_sheet": facade_sheet_contract(skin),
        "massing_graph": assembled["massing_graph"],
        "material_budget": {
            "max_assembled_materials": 24,
            "rationale": (
                "Roof metal, timber, concrete, polycarbonate, cobalt, plinth, "
                "physical glazing, occupied depth, pool water and civic "
                "interior materials remain separate to preserve construction."
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
            "A transparent civic natatorium beneath one continuous unequal "
            "double-wave silver shell, held by two cable masts and pale "
            "concrete branch supports above warm timber pool-hall depth."
        ),
        "material_zones": (
            "platinum standing-seam shell; honey glulam and soffit; pale "
            "board-formed branch supports; low-iron pool glass; milky ribbed "
            "polycarbonate; cobalt microperforated service panels; charcoal "
            "honed plinth; blue competition and leisure pool water"
        ),
        "glass_profile": "aquatic_low_iron_pool_clear",
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
                "official built-precedent research, locked multi-angle "
                "ImageGen source pack, clean PBR cells, deterministic metric "
                "geometry and physical pool glazing"
            ),
        },
    }
    old_manifest_path.write_text(
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
                "fixed_landmark",
                "continuous_double_wave_shell",
                "cable_stay_masts",
                "physical_pool_glazing",
                "flexible_fallback_stack",
            ],
        },
        "archetype_aliases": ALIASES,
        "footprint_compatibility": footprint,
        "massing_graph": manifest["massing_graph"],
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
        f"[wave10-aquatic] {FAMILY}: {assembled_triangles} triangles, "
        f"{assembled_materials} materials, {len(modules)} modules, "
        f"{len(renders)} renders",
        flush=True,
    )


def render_existing(output_root: Path, *, view_set: str) -> None:
    clear_scene()
    folder = output_root / FAMILY
    mats, _skin = load_palette(folder)
    manifest_path = folder / f"{FAMILY}_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    bpy.ops.import_scene.gltf(
        filepath=str(folder / manifest["assembled"]["filename"])
    )
    manifest["renders"] = render_views(folder, mats, view_set=view_set)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"[wave10-aquatic-render] {FAMILY}: {len(manifest['renders'])} renders"
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
