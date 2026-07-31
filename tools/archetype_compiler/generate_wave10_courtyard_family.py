"""Author the Wave 10 Modern Brick Mews LEGO-family pilot.

The canonical assembled model is a real four-wing courtyard building.  The
stackable units remain one straight occupied bar so the assembly planner can
place them as rectangle, U-shaped, or closed-courtyard streetwalls without
duplicating a complete ring at every segment.

Run from the repository root with Blender 5.x:

    blender --background --factory-startup --python \
      tools/archetype_compiler/generate_wave10_courtyard_family.py -- \
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
from mathutils import Matrix, Vector


TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from generate_wave3_landmark_families import (  # noqa: E402
    COORDINATE_CONTRACT,
    aim_camera,
    box,
    cylinder,
    delete_objects,
    export_glb,
    material,
    module_contract_markers,
    setup_render,
)
from generate_wave4_standard_batch import profiled_glass_material  # noqa: E402
from generate_wave4_standard_families import pbr_material  # noqa: E402
from generate_wave6_nonresidential_families import (  # noqa: E402
    reference_image_material,
)
from generate_wave9_single_family_families import (  # noqa: E402
    rectangles_around_openings,
    round_beam,
)


FAMILY = "courtyard-family-brick-mews"
ARCHETYPE_ID = "courtyard_family_housing"
VARIANT_ID = "courtyard_family_brick_modern"
LABEL = "Courtyard Family Housing — Modern Brick Mews"
GLASS_PROFILE = "residential_low_e"

WIDTH = 28.0
BLOCK_DEPTH = 24.0
WING_DEPTH = 5.0
COURT_WIDTH = WIDTH - WING_DEPTH * 2.0
COURT_DEPTH = BLOCK_DEPTH - WING_DEPTH * 2.0
FLOOR_HEIGHT = 3.20
CROWN_HEIGHT = 0.45
ROOF_HEIGHT = 2.75
BODY_HEIGHT = FLOOR_HEIGHT * 3.0
TOTAL_HEIGHT = BODY_HEIGHT + CROWN_HEIGHT + ROOF_HEIGHT
WALL_THICKNESS = 0.24
ROOF_WIDTH_OVERHANG = 0.56
ROOF_END_OVERHANG = 0.46


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
    parser.add_argument("--render-existing", action="store_true")
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(argv)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for item in list(block):
            if item.users == 0:
                block.remove(item)


def mesh_object(
    name: str,
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, ...]],
    mat: bpy.types.Material,
    *,
    uv_scale: float = 1.0,
) -> bpy.types.Object:
    """Create authored geometry with deterministic face-planar UVs."""
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    mesh.materials.append(mat)
    uv = mesh.uv_layers.new(name="UVMap")
    xs = [value[0] for value in vertices]
    ys = [value[1] for value in vertices]
    zs = [value[2] for value in vertices]
    bounds = (
        (min(xs), max(xs)),
        (min(ys), max(ys)),
        (min(zs), max(zs)),
    )

    def normalized(value: float, low: float, high: float) -> float:
        return 0.0 if abs(high - low) < 1e-6 else (value - low) / (high - low)

    for polygon in mesh.polygons:
        normal = polygon.normal
        for loop_index in polygon.loop_indices:
            vertex = mesh.vertices[mesh.loops[loop_index].vertex_index].co
            if abs(normal.z) > max(abs(normal.x), abs(normal.y)):
                value = (
                    normalized(vertex.x, *bounds[0]),
                    normalized(vertex.y, *bounds[1]),
                )
            elif abs(normal.x) > abs(normal.y):
                value = (
                    normalized(vertex.y, *bounds[1]),
                    normalized(vertex.z, *bounds[2]),
                )
            else:
                value = (
                    normalized(vertex.x, *bounds[0]),
                    normalized(vertex.z, *bounds[2]),
                )
            uv.data[loop_index].uv = (
                value[0] * uv_scale,
                value[1] * uv_scale,
            )
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def apply_true_scale_uv(obj: bpy.types.Object, tile_m: float = 2.0) -> None:
    """Project construction textures at one stable metric scale."""
    mesh = obj.data
    uv = mesh.uv_layers.active or mesh.uv_layers.new(name="UVMap")
    for polygon in mesh.polygons:
        normal = polygon.normal
        for loop_index in polygon.loop_indices:
            vertex = mesh.vertices[mesh.loops[loop_index].vertex_index].co
            if abs(normal.z) > max(abs(normal.x), abs(normal.y)):
                value = (vertex.x / tile_m, vertex.y / tile_m)
            elif abs(normal.x) > abs(normal.y):
                value = (vertex.y / tile_m, vertex.z / tile_m)
            else:
                value = (vertex.x / tile_m, vertex.z / tile_m)
            uv.data[loop_index].uv = value


def tbox(
    name: str,
    size: tuple[float, float, float],
    location: tuple[float, float, float],
    mat: bpy.types.Material,
    bevel: float = 0.0,
    *,
    tile_m: float = 2.0,
) -> bpy.types.Object:
    obj = box(name, size, location, mat, bevel)
    # One physical chamfer is enough at City Prompt viewing distances.  The
    # shared helper defaults to two segments, which multiplies triangles across
    # the thousands of narrow brick reveals, frames, guards, and wall strips in
    # this deliberately opening-rich family without changing its silhouette.
    edge_softening = obj.modifiers.get("EdgeSoftening")
    if edge_softening is not None:
        edge_softening.segments = 1
    if obj.type == "MESH":
        apply_true_scale_uv(obj, tile_m)
    return obj


def load_palette(folder: Path) -> tuple[dict[str, bpy.types.Material], dict]:
    skin = json.loads(
        (folder / "textures" / "skin_manifest.json").read_text(encoding="utf-8")
    )
    near = {zone: values["near"] for zone, values in skin["zones"].items()}
    mats: dict[str, bpy.types.Material] = {
        "brick": pbr_material(
            "MAT_W10_MEWS_GoldenBuffBrick",
            folder,
            near["brick"],
            "brick",
            value=0.84,
            saturation=1.04,
        ),
        "facade": pbr_material(
            "MAT_W10_MEWS_RegisteredElevation",
            folder,
            near["facade"],
            "facade",
            value=0.98,
            saturation=0.94,
        ),
        "metal": pbr_material(
            "MAT_W10_MEWS_CharcoalMetal",
            folder,
            near["metal"],
            "metal",
            metallic=0.72,
            value=0.58,
            saturation=0.72,
        ),
        "roof": pbr_material(
            "MAT_W10_MEWS_DarkConcreteRoofTile",
            folder,
            near["roof"],
            "roof",
            value=0.69,
            saturation=0.62,
        ),
        "paving": pbr_material(
            "MAT_W10_MEWS_GreyUnitPaving",
            folder,
            near["paving"],
            "paving",
            value=0.88,
            saturation=0.58,
        ),
        "soffit": pbr_material(
            "MAT_W10_MEWS_ShadowedBrickSoffit",
            folder,
            near["soffit"],
            "soffit",
            value=0.54,
            saturation=0.78,
        ),
        "glass": profiled_glass_material(
            "MAT_W10_MEWS_PhysicalResidentialLowEGlass",
            GLASS_PROFILE,
            tint="#172326",
            roughness_scale=1.10,
            transmission_scale=0.48,
        ),
        "underlay": reference_image_material(
            "MAT_W10_MEWS_RegisteredOccupiedDepth",
            folder,
            "textures/source/occupied-depth-source-v1.png",
            emission_strength=0.075,
        ),
        "deep": material(
            "MAT_W10_MEWS_DeepCavity",
            (0.018, 0.017, 0.015, 1.0),
            0.95,
        ),
        "warm": material(
            "MAT_W10_MEWS_DimOccupiedRoom",
            (0.15, 0.105, 0.065, 1.0),
            0.88,
            emission=(0.55, 0.27, 0.10, 1.0),
            emission_strength=0.11,
        ),
        "curtain": material(
            "MAT_W10_MEWS_MutedLinenCurtain",
            (0.48, 0.43, 0.36, 1.0),
            0.93,
        ),
    }
    mats["glass"]["glazing_lod"] = "always"
    mats["glass"]["reference_locked"] = True
    mats["glass"]["source_variant_id"] = VARIANT_ID
    mats["underlay"]["glazing_profile"] = GLASS_PROFILE
    mats["underlay"]["source_variant_id"] = VARIANT_ID
    return mats, skin


def transform_objects(
    objects: list[bpy.types.Object],
    *,
    translation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    rotation_degrees: float = 0.0,
) -> None:
    transform = (
        Matrix.Translation(Vector(translation))
        @ Matrix.Rotation(math.radians(rotation_degrees), 4, "Z")
    )
    # Blender defers the matrix update after assigning a quaternion to a newly
    # created round beam. Without this flush, the final beam in a wing can be
    # transformed from its stale vertical-cylinder matrix while every earlier
    # beam is correct only because creating the next object forced an update.
    bpy.context.view_layer.update()
    for obj in objects:
        obj.matrix_world = transform @ obj.matrix_world


def arch_spandrels(
    name: str,
    *,
    centre_x: float,
    y: float,
    sill_z: float,
    width: float,
    height: float,
    mat: bpy.types.Material,
    arch_rise: float = 1.10,
    segments: int = 18,
) -> list[bpy.types.Object]:
    half_width = width / 2.0
    spring = sill_z + height - arch_rise
    top = sill_z + height
    x0, x1 = centre_x - half_width, centre_x + half_width
    left = [(x0, y, spring), (x0, y, top), (centre_x, y, top)]
    left.extend(
        (
            centre_x + half_width * math.cos(theta),
            y,
            spring + arch_rise * math.sin(theta),
        )
        for theta in (
            math.pi / 2.0
            + (math.pi / 2.0) * index / segments
            for index in range(1, segments + 1)
        )
    )
    right = [(centre_x, y, top), (x1, y, top), (x1, y, spring)]
    right.extend(
        (
            centre_x + half_width * math.cos(theta),
            y,
            spring + arch_rise * math.sin(theta),
        )
        for theta in (
            (math.pi / 2.0) * index / segments
            for index in range(0, segments + 1)
        )
    )
    return [
        mesh_object(
            f"{name}_LeftBrickSpandrel",
            left,
            [tuple(range(len(left)))],
            mat,
            uv_scale=2.0,
        ),
        mesh_object(
            f"{name}_RightBrickSpandrel",
            right,
            [tuple(range(len(right)))],
            mat,
            uv_scale=2.0,
        ),
    ]


def arch_ring(
    name: str,
    *,
    centre_x: float,
    y: float,
    sill_z: float,
    width: float,
    height: float,
    band: float,
    mat: bpy.types.Material,
    arch_rise: float = 1.10,
    segments: int = 28,
) -> list[bpy.types.Object]:
    half_width = width / 2.0
    spring = sill_z + height - arch_rise
    vertices: list[tuple[float, float, float]] = []
    for index in range(segments + 1):
        theta = math.pi * index / segments
        for width_radius, rise_radius in (
            (half_width, arch_rise),
            (half_width + band, arch_rise + band),
        ):
            vertices.append(
                (
                    centre_x + width_radius * math.cos(theta),
                    y,
                    spring + rise_radius * math.sin(theta),
                )
            )
    faces = [
        (index * 2, index * 2 + 1, index * 2 + 3, index * 2 + 2)
        for index in range(segments)
    ]
    objects = [
        mesh_object(
            f"{name}_PhysicalSoldierArch",
            vertices,
            faces,
            mat,
            uv_scale=4.0,
        )
    ]
    jamb_height = max(0.08, spring - sill_z)
    for side in (-1, 1):
        objects.append(
            tbox(
                f"{name}_SoldierJamb_{side:+d}",
                (band, 0.10, jamb_height),
                (
                    centre_x + side * (half_width + band * 0.5),
                    y,
                    sill_z + jamb_height * 0.5,
                ),
                mat,
                0.008,
                tile_m=0.65,
            )
        )
    return objects


def segmental_arch_panel(
    name: str,
    *,
    centre_x: float,
    y: float,
    sill_z: float,
    width: float,
    height: float,
    arch_rise: float,
    mat: bpy.types.Material,
    segments: int = 28,
) -> bpy.types.Object:
    """A filled rectangular opening with a shallow elliptical arch head."""
    half_width = width / 2.0
    spring = sill_z + height - arch_rise
    vertices = [
        (centre_x - half_width, y, sill_z),
        (centre_x + half_width, y, sill_z),
        (centre_x + half_width, y, spring),
    ]
    vertices.extend(
        (
            centre_x + half_width * math.cos(theta),
            y,
            spring + arch_rise * math.sin(theta),
        )
        for theta in (math.pi * index / segments for index in range(segments + 1))
    )
    return mesh_object(
        name,
        vertices,
        [tuple(range(len(vertices)))],
        mat,
        uv_scale=1.0,
    )


def arch_soffit(
    name: str,
    *,
    centre_x: float,
    normal_centre: float,
    normal_depth: float,
    sill_z: float,
    width: float,
    height: float,
    mat: bpy.types.Material,
    arch_rise: float = 1.10,
    segments: int = 32,
) -> list[bpy.types.Object]:
    """Build a traversable curved brick soffit and full-depth jambs."""
    half_width = width / 2.0
    spring = sill_z + height - arch_rise
    y0 = normal_centre - normal_depth / 2.0
    y1 = normal_centre + normal_depth / 2.0
    vertices: list[tuple[float, float, float]] = []
    for index in range(segments + 1):
        theta = math.pi * index / segments
        x = centre_x + half_width * math.cos(theta)
        z = spring + arch_rise * math.sin(theta)
        vertices.extend([(x, y0, z), (x, y1, z)])
    faces = [
        (index * 2, index * 2 + 1, index * 2 + 3, index * 2 + 2)
        for index in range(segments)
    ]
    objects: list[bpy.types.Object] = [
        mesh_object(
            f"{name}_ContinuousSegmentalBrickBarrel",
            vertices,
            faces,
            mat,
            uv_scale=4.0,
        )
    ]
    jamb_height = max(0.10, spring - sill_z)
    for side in (-1, 1):
        objects.append(
            tbox(
                f"{name}_FullDepthJamb_{side:+d}",
                (0.18, normal_depth, jamb_height),
                (
                    centre_x + side * (half_width - 0.09),
                    normal_centre,
                    sill_z + jamb_height / 2.0,
                ),
                mat,
                0.012,
                tile_m=0.65,
            )
        )
    return objects


def add_wall_face(
    name: str,
    *,
    length: float,
    surface_y: float,
    outward_sign: int,
    z0: float,
    z1: float,
    openings: list[tuple[float, float, float, float]],
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    inside_y = surface_y - outward_sign * WALL_THICKNESS / 2.0
    for index, (x0, x1, rz0, rz1) in enumerate(
        rectangles_around_openings(
            -length / 2.0,
            length / 2.0,
            z0,
            z1,
            openings,
        )
    ):
        objects.append(
            tbox(
                f"{name}_PhysicalBuffBrickWall_{index:03d}",
                (x1 - x0, WALL_THICKNESS, rz1 - rz0),
                ((x0 + x1) / 2.0, inside_y, (rz0 + rz1) / 2.0),
                mats["brick"],
                0.012,
                tile_m=1.45,
            )
        )
    return objects


def add_juliet_balcony(
    name: str,
    *,
    centre_x: float,
    width: float,
    sill_z: float,
    surface_y: float,
    outward_sign: int,
    mats: dict[str, bpy.types.Material],
    shallow: bool = False,
) -> list[bpy.types.Object]:
    depth = 0.24 if shallow else 0.43
    rail_y = surface_y + outward_sign * (depth + 0.11)
    slab_y = surface_y + outward_sign * (depth * 0.46)
    objects = [
        tbox(
            f"{name}_RecessedBalconyThreshold",
            (width + 0.22, depth, 0.12),
            (centre_x, slab_y, sill_z - 0.03),
            mats["metal"],
            0.018,
            tile_m=0.7,
        ),
        tbox(
            f"{name}_TopRail",
            (width + 0.24, 0.07, 0.075),
            (centre_x, rail_y, sill_z + 1.02),
            mats["metal"],
            0.012,
            tile_m=0.5,
        ),
        tbox(
            f"{name}_BottomRail",
            (width + 0.24, 0.06, 0.055),
            (centre_x, rail_y, sill_z + 0.18),
            mats["metal"],
            0.010,
            tile_m=0.5,
        ),
    ]
    count = max(5, int(width / 0.20))
    for index in range(count + 1):
        x = centre_x - width * 0.5 + width * index / count
        objects.append(
            tbox(
                f"{name}_VerticalGuard_{index:02d}",
                (0.032, 0.055, 0.84),
                (x, rail_y, sill_z + 0.60),
                mats["metal"],
                0.006,
                tile_m=0.4,
            )
        )
    for side in (-1, 1):
        side_y = surface_y + outward_sign * (depth * 0.54)
        objects.append(
            tbox(
                f"{name}_SideReturn_{side:+d}",
                (0.045, depth, 0.86),
                (
                    centre_x + side * (width / 2.0 + 0.10),
                    side_y,
                    sill_z + 0.59,
                ),
                mats["metal"],
                0.008,
                tile_m=0.5,
            )
        )
    return objects


def add_window(
    name: str,
    *,
    centre_x: float,
    sill_z: float,
    width: float,
    height: float,
    surface_y: float,
    outward_sign: int,
    mats: dict[str, bpy.types.Material],
    juliet: bool = False,
    shallow_juliet: bool = False,
) -> list[bpy.types.Object]:
    """Construct one genuinely recessed occupied residential window."""
    inside = -outward_sign
    x0, x1 = centre_x - width / 2.0, centre_x + width / 2.0
    z0, z1 = sill_z, sill_z + height
    reveal_centre = surface_y + inside * 0.23
    pane_y = surface_y + inside * 0.39
    room_y = surface_y + inside * 0.49
    reveal_mat = mats["brick"]
    frame = 0.075
    objects = [
        tbox(
            f"{name}_LeftBrickReveal",
            (0.11, 0.46, height),
            (x0 + 0.055, reveal_centre, (z0 + z1) / 2.0),
            reveal_mat,
            0.010,
            tile_m=0.70,
        ),
        tbox(
            f"{name}_RightBrickReveal",
            (0.11, 0.46, height),
            (x1 - 0.055, reveal_centre, (z0 + z1) / 2.0),
            reveal_mat,
            0.010,
            tile_m=0.70,
        ),
        tbox(
            f"{name}_BrickSill",
            (width, 0.46, 0.105),
            (centre_x, reveal_centre, z0 + 0.0525),
            reveal_mat,
            0.010,
            tile_m=0.70,
        ),
        tbox(
            f"{name}_BrickHead",
            (width, 0.46, 0.105),
            (centre_x, reveal_centre, z1 - 0.0525),
            reveal_mat,
            0.010,
            tile_m=0.70,
        ),
        tbox(
            f"{name}_RegisteredOccupiedDepth",
            (width - 0.20, 0.025, height - 0.20),
            (centre_x, room_y, (z0 + z1) / 2.0),
            mats["underlay"],
            0.006,
            tile_m=1.0,
        ),
        tbox(
            f"{name}_PhysicalLowEPane",
            (width - 0.18, 0.032, height - 0.18),
            (centre_x, pane_y, (z0 + z1) / 2.0),
            mats["glass"],
            0.008,
            tile_m=1.0,
        ),
        tbox(
            f"{name}_LeftFrame",
            (frame, 0.105, height - 0.08),
            (x0 + frame / 2.0, pane_y - inside * 0.035, (z0 + z1) / 2.0),
            mats["metal"],
            0.008,
            tile_m=0.55,
        ),
        tbox(
            f"{name}_RightFrame",
            (frame, 0.105, height - 0.08),
            (x1 - frame / 2.0, pane_y - inside * 0.035, (z0 + z1) / 2.0),
            mats["metal"],
            0.008,
            tile_m=0.55,
        ),
        tbox(
            f"{name}_TopFrame",
            (width, 0.105, frame),
            (centre_x, pane_y - inside * 0.035, z1 - frame / 2.0),
            mats["metal"],
            0.008,
            tile_m=0.55,
        ),
        tbox(
            f"{name}_BottomFrame",
            (width, 0.105, frame),
            (centre_x, pane_y - inside * 0.035, z0 + frame / 2.0),
            mats["metal"],
            0.008,
            tile_m=0.55,
        ),
    ]
    if width > 1.45:
        objects.append(
            tbox(
                f"{name}_CentreMullion",
                (0.070, 0.11, height - 0.12),
                (centre_x, pane_y - inside * 0.045, (z0 + z1) / 2.0),
                mats["metal"],
                0.008,
                tile_m=0.55,
            )
        )
    elif width > 0.92:
        objects.append(
            tbox(
                f"{name}_OpeningLightMullion",
                (0.052, 0.10, height - 0.14),
                (centre_x + width * 0.20, pane_y - inside * 0.045, (z0 + z1) / 2.0),
                mats["metal"],
                0.007,
                tile_m=0.55,
            )
        )
    if sum(ord(char) for char in name) % 3:
        curtain_x = centre_x - width * 0.25
        objects.append(
            tbox(
                f"{name}_PartialLinenCurtain",
                (max(0.20, width * 0.30), 0.020, height * 0.72),
                (curtain_x, room_y - inside * 0.025, z0 + height * 0.58),
                mats["curtain"],
                0.004,
                tile_m=0.7,
            )
        )
    if juliet:
        objects.extend(
            add_juliet_balcony(
                f"{name}_IntegratedJuliet",
                centre_x=centre_x,
                width=width,
                sill_z=sill_z,
                surface_y=surface_y,
                outward_sign=outward_sign,
                mats=mats,
                shallow=shallow_juliet,
            )
        )
    return objects


def public_upper_schedule(variant: str) -> list[dict]:
    schedule = [
        {"x": -10.55, "w": 3.10, "sill": 0.52, "h": 2.12, "juliet": True},
        {"x": -6.65, "w": 1.12, "sill": 0.52, "h": 2.12, "juliet": True, "shallow": True},
        {"x": -3.70, "w": 1.10, "sill": 0.88, "h": 1.52},
        {"x": -0.35, "w": 1.10, "sill": 0.88, "h": 1.52},
        {"x": 3.00, "w": 1.10, "sill": 0.88, "h": 1.52},
        {"x": 6.45, "w": 1.12, "sill": 0.52, "h": 2.12, "juliet": True, "shallow": True},
        {"x": 10.55, "w": 3.10, "sill": 0.52, "h": 2.12, "juliet": True},
    ]
    if variant == "typical_b":
        schedule[2]["x"] = -3.45
        schedule[3]["x"] = 0.0
        schedule[4]["x"] = 3.45
    elif variant == "typical_c":
        schedule[0]["w"] = 2.70
        schedule[-1]["w"] = 2.70
        schedule[1]["juliet"] = False
        schedule[-2]["juliet"] = False
    return schedule


def quiet_upper_schedule(length: float, variant: str) -> list[dict]:
    margin = 1.35
    bay_count = max(3, round((length - margin * 2.0) / 2.75))
    positions = [
        -length / 2.0 + margin
        + (length - margin * 2.0) * index / max(1, bay_count - 1)
        for index in range(bay_count)
    ]
    schedule: list[dict] = []
    for index, x in enumerate(positions):
        wide = index in {1, bay_count - 2} and length >= 17.0
        schedule.append(
            {
                "x": x,
                "w": 1.82 if wide else 1.02,
                "sill": 0.62 if wide else 0.86,
                "h": 1.94 if wide else 1.52,
                "juliet": wide and variant != "typical_c",
                "shallow": True,
            }
        )
    return schedule


def add_upper_face(
    name: str,
    *,
    length: float,
    surface_y: float,
    outward_sign: int,
    z_base: float,
    style: str,
    variant: str,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    schedule = (
        public_upper_schedule(variant)
        if style == "public"
        else quiet_upper_schedule(length, variant)
    )
    openings = [
        (
            item["x"] - item["w"] / 2.0,
            item["x"] + item["w"] / 2.0,
            z_base + item["sill"],
            z_base + item["sill"] + item["h"],
        )
        for item in schedule
    ]
    objects = add_wall_face(
        name,
        length=length,
        surface_y=surface_y,
        outward_sign=outward_sign,
        z0=z_base,
        z1=z_base + FLOOR_HEIGHT,
        openings=openings,
        mats=mats,
    )
    for index, item in enumerate(schedule):
        objects.extend(
            add_window(
                f"{name}_ResidentialOpening_{index:02d}",
                centre_x=item["x"],
                sill_z=z_base + item["sill"],
                width=item["w"],
                height=item["h"],
                surface_y=surface_y,
                outward_sign=outward_sign,
                mats=mats,
                juliet=bool(item.get("juliet")),
                shallow_juliet=bool(item.get("shallow")),
            )
        )
    objects.append(
        tbox(
            f"{name}_ContinuousSoldierCourse",
            (length + 0.06, 0.12, 0.17),
            (
                0.0,
                surface_y + outward_sign * 0.055,
                z_base + FLOOR_HEIGHT - 0.13,
            ),
            mats["brick"],
            0.008,
            tile_m=0.55,
        )
    )
    return objects


def quiet_ground_schedule(length: float) -> list[dict]:
    bay_count = max(3, round((length - 2.6) / 3.0))
    positions = [
        -length / 2.0 + 1.4
        + (length - 2.8) * index / max(1, bay_count - 1)
        for index in range(bay_count)
    ]
    return [
        {
            "x": x,
            "w": 1.06 if index % 3 else 1.20,
            "sill": 0.78 if index % 3 else 0.18,
            "h": 1.62 if index % 3 else 2.45,
            "door": index % 3 == 0,
        }
        for index, x in enumerate(positions)
    ]


def add_quiet_ground_face(
    name: str,
    *,
    length: float,
    surface_y: float,
    outward_sign: int,
    z_base: float,
    mats: dict[str, bpy.types.Material],
    passage_x: float | None = None,
) -> list[bpy.types.Object]:
    schedule = quiet_ground_schedule(length)
    if passage_x is not None:
        schedule = [
            item for item in schedule if abs(item["x"] - passage_x) > 2.65
        ]
    openings = [
        (
            item["x"] - item["w"] / 2.0,
            item["x"] + item["w"] / 2.0,
            z_base + item["sill"],
            z_base + item["sill"] + item["h"],
        )
        for item in schedule
    ]
    if passage_x is not None:
        openings.append(
            (
                passage_x - 2.15,
                passage_x + 2.15,
                z_base,
                z_base + 3.05,
            )
        )
    objects = add_wall_face(
        name,
        length=length,
        surface_y=surface_y,
        outward_sign=outward_sign,
        z0=z_base,
        z1=z_base + FLOOR_HEIGHT,
        openings=openings,
        mats=mats,
    )
    for index, item in enumerate(schedule):
        objects.extend(
            add_window(
                f"{name}_{'Door' if item['door'] else 'Window'}_{index:02d}",
                centre_x=item["x"],
                sill_z=z_base + item["sill"],
                width=item["w"],
                height=item["h"],
                surface_y=surface_y,
                outward_sign=outward_sign,
                mats=mats,
            )
        )
        if item["door"]:
            objects.extend(
                [
                    tbox(
                        f"{name}_Door_{index:02d}_StoneThreshold",
                        (item["w"] + 0.20, 0.32, 0.09),
                        (
                            item["x"],
                            surface_y + outward_sign * 0.11,
                            z_base + 0.045,
                        ),
                        mats["paving"],
                        0.012,
                        tile_m=0.55,
                    ),
                    cylinder(
                        f"{name}_Door_{index:02d}_MetalPull",
                        0.026,
                        0.16,
                        (
                            item["x"] + item["w"] * 0.28,
                            surface_y + outward_sign * 0.08,
                            z_base + 1.14,
                        ),
                        mats["metal"],
                        vertices=10,
                    ),
                ]
            )
    if passage_x is not None:
        objects.extend(
            arch_spandrels(
                f"{name}_CourtyardPassage",
                centre_x=passage_x,
                y=surface_y + outward_sign * 0.006,
                sill_z=z_base,
                width=4.30,
                height=3.05,
                mat=mats["brick"],
            )
        )
        for index, bicycle_x in enumerate((passage_x + 4.85, passage_x + 6.00)):
            objects.extend(
                add_bicycle(
                    f"{name}_CourtyardBicycle_{index}",
                    centre_x=bicycle_x,
                    y=surface_y + outward_sign * 0.22,
                    z=z_base + 0.04,
                    mats=mats,
                )
            )
        objects.extend(
            arch_ring(
                f"{name}_CourtyardPassage",
                centre_x=passage_x,
                y=surface_y + outward_sign * 0.075,
                sill_z=z_base,
                width=4.30,
                height=3.05,
                band=0.20,
                mat=mats["brick"],
            )
        )
    objects.append(
        tbox(
            f"{name}_GroundSoldierCourse",
            (length + 0.06, 0.12, 0.17),
            (
                0.0,
                surface_y + outward_sign * 0.055,
                z_base + FLOOR_HEIGHT - 0.13,
            ),
            mats["brick"],
            0.008,
            tile_m=0.55,
        )
    )
    return objects


def add_bicycle(
    name: str,
    *,
    centre_x: float,
    y: float,
    z: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    wheel_radius = 0.34
    wheel_positions = (centre_x - 0.46, centre_x + 0.46)
    for index, x in enumerate(wheel_positions):
        bpy.ops.mesh.primitive_torus_add(
            major_radius=wheel_radius,
            minor_radius=0.026,
            major_segments=32,
            minor_segments=8,
            location=(x, y, z + wheel_radius),
            rotation=(math.pi / 2.0, 0.0, 0.0),
        )
        wheel = bpy.context.object
        wheel.name = f"{name}_Wheel_{index}"
        wheel.data.materials.append(mats["metal"])
        objects.append(wheel)
    frame_points = [
        ((wheel_positions[0], y, z + wheel_radius), (centre_x, y, z + 0.62)),
        ((centre_x, y, z + 0.62), (wheel_positions[1], y, z + wheel_radius)),
        ((wheel_positions[0], y, z + wheel_radius), (centre_x + 0.18, y, z + 0.34)),
        ((centre_x + 0.18, y, z + 0.34), (centre_x, y, z + 0.62)),
        ((centre_x, y, z + 0.62), (centre_x - 0.08, y, z + 0.92)),
    ]
    for index, (start, end) in enumerate(frame_points):
        objects.append(
            round_beam(
                f"{name}_FrameMember_{index}",
                start,
                end,
                0.026,
                mats["metal"],
                vertices=10,
            )
        )
    objects.extend(
        [
            round_beam(
                f"{name}_Handlebar",
                (centre_x - 0.24, y, z + 0.93),
                (centre_x + 0.12, y, z + 0.93),
                0.022,
                mats["metal"],
                vertices=10,
            ),
            tbox(
                f"{name}_Saddle",
                (0.26, 0.10, 0.07),
                (centre_x + 0.10, y, z + 0.76),
                mats["metal"],
                0.020,
                tile_m=0.4,
            ),
        ]
    )
    return objects


def add_public_ground_face(
    name: str,
    *,
    length: float,
    surface_y: float,
    outward_sign: int,
    z_base: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    centres = (-10.5, -3.5, 3.5, 10.5)
    width = 4.30
    height = 3.05
    openings = [
        (
            centre - width / 2.0,
            centre + width / 2.0,
            z_base,
            z_base + height,
        )
        for centre in centres
    ]
    objects = add_wall_face(
        name,
        length=length,
        surface_y=surface_y,
        outward_sign=outward_sign,
        z0=z_base,
        z1=z_base + FLOOR_HEIGHT,
        openings=openings,
        mats=mats,
    )
    inside = -outward_sign
    for index, centre in enumerate(centres):
        arch_name = f"{name}_GroundArch_{index}"
        objects.extend(
            arch_spandrels(
                arch_name,
                centre_x=centre,
                y=surface_y + outward_sign * 0.006,
                sill_z=z_base,
                width=width,
                height=height,
                mat=mats["brick"],
            )
        )
        objects.extend(
            arch_ring(
                arch_name,
                centre_x=centre,
                y=surface_y + outward_sign * 0.075,
                sill_z=z_base,
                width=width,
                height=height,
                band=0.20,
                mat=mats["brick"],
            )
        )
        if index == 1:
            continue
        recess_y = surface_y + inside * 0.88
        objects.append(
            segmental_arch_panel(
                f"{arch_name}_DeepStorageCavity",
                centre_x=centre,
                y=recess_y,
                sill_z=z_base + 0.05,
                width=width - 0.28,
                height=height - 0.16,
                arch_rise=1.02,
                mat=mats["deep"],
                segments=28,
            )
        )
        # Paired dark storage doors occupy only the outer quarters, preserving
        # a believable recessed bicycle bay rather than a painted black arch.
        for side in (-1, 1):
            objects.append(
                tbox(
                    f"{arch_name}_IntegratedStorageDoor_{side:+d}",
                    (0.78, 0.10, 1.60),
                    (
                        centre + side * 1.18,
                        recess_y - inside * 0.07,
                        z_base + 0.84,
                    ),
                    mats["metal"],
                    0.018,
                    tile_m=0.7,
                )
            )
        if index in {0, 3}:
            objects.extend(
                add_bicycle(
                    f"{arch_name}_StoredBicycle",
                    centre_x=centre,
                    y=recess_y - inside * 0.12,
                    z=z_base + 0.04,
                    mats=mats,
                )
            )
    objects.append(
        tbox(
            f"{name}_GroundSoldierCourse",
            (length + 0.06, 0.12, 0.17),
            (
                0.0,
                surface_y + outward_sign * 0.055,
                z_base + FLOOR_HEIGHT - 0.13,
            ),
            mats["brick"],
            0.008,
            tile_m=0.55,
        )
    )
    return objects


def add_end_walls(
    name: str,
    *,
    length: float,
    depth: float,
    z_base: float,
    height: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    return [
        tbox(
            f"{name}_LeftReturn",
            (WALL_THICKNESS, depth, height),
            (-length / 2.0 + WALL_THICKNESS / 2.0, 0.0, z_base + height / 2.0),
            mats["brick"],
            0.012,
            tile_m=1.45,
        ),
        tbox(
            f"{name}_RightReturn",
            (WALL_THICKNESS, depth, height),
            (length / 2.0 - WALL_THICKNESS / 2.0, 0.0, z_base + height / 2.0),
            mats["brick"],
            0.012,
            tile_m=1.45,
        ),
    ]


def build_level_wing(
    *,
    name: str,
    length: float,
    z_base: float,
    role: str,
    variant: str,
    front_style: str,
    rear_style: str,
    mats: dict[str, bpy.types.Material],
    include_ends: bool,
    through_passage: bool = False,
) -> list[bpy.types.Object]:
    front_y = -WING_DEPTH / 2.0
    rear_y = WING_DEPTH / 2.0
    objects: list[bpy.types.Object] = []
    if role == "podium":
        if front_style == "public":
            objects.extend(
                add_public_ground_face(
                    f"{name}_PublicGround",
                    length=length,
                    surface_y=front_y,
                    outward_sign=-1,
                    z_base=z_base,
                    mats=mats,
                )
            )
        else:
            objects.extend(
                add_quiet_ground_face(
                    f"{name}_FrontGround",
                    length=length,
                    surface_y=front_y,
                    outward_sign=-1,
                    z_base=z_base,
                    mats=mats,
                    passage_x=-3.5 if front_style == "passage" else None,
                )
            )
        objects.extend(
            add_quiet_ground_face(
                f"{name}_RearGround",
                length=length,
                surface_y=rear_y,
                outward_sign=1,
                z_base=z_base,
                mats=mats,
                passage_x=-3.5 if rear_style == "passage" else None,
            )
        )
        if through_passage:
            objects.extend(
                arch_soffit(
                    f"{name}_ThroughCarriagePassage",
                    centre_x=-3.5,
                    normal_centre=0.0,
                    normal_depth=WING_DEPTH - 0.28,
                    sill_z=z_base,
                    width=4.30,
                    height=3.05,
                    mat=mats["soffit"],
                )
            )
            objects.append(
                tbox(
                    f"{name}_ThroughCarriagePassage_PavedFloor",
                    (4.10, WING_DEPTH + 2.2, 0.075),
                    (-3.5, 0.72, z_base + 0.0375),
                    mats["paving"],
                    0.008,
                    tile_m=1.1,
                )
            )
    else:
        objects.extend(
            add_upper_face(
                f"{name}_FrontUpper",
                length=length,
                surface_y=front_y,
                outward_sign=-1,
                z_base=z_base,
                style=front_style,
                variant=variant,
                mats=mats,
            )
        )
        objects.extend(
            add_upper_face(
                f"{name}_RearUpper",
                length=length,
                surface_y=rear_y,
                outward_sign=1,
                z_base=z_base,
                style=rear_style,
                variant=variant,
                mats=mats,
            )
        )
    # Thin occupied floor plates stop every wing from reading as two facade
    # cards while leaving the courtyard and passage visibly open.
    objects.extend(
        [
            tbox(
                f"{name}_StructuralFloorPlate",
                (length, WING_DEPTH - 0.26, 0.13),
                (0.0, 0.0, z_base + 0.065),
                mats["soffit"],
                0.008,
                tile_m=1.25,
            ),
            tbox(
                f"{name}_StructuralCeilingPlate",
                (length, WING_DEPTH - 0.26, 0.12),
                (0.0, 0.0, z_base + FLOOR_HEIGHT - 0.06),
                mats["soffit"],
                0.008,
                tile_m=1.25,
            ),
        ]
    )
    if include_ends:
        objects.extend(
            add_end_walls(
                name,
                length=length,
                depth=WING_DEPTH,
                z_base=z_base,
                height=FLOOR_HEIGHT,
                mats=mats,
            )
        )
    return objects


def build_crown_wing(
    name: str,
    *,
    length: float,
    z_base: float,
    mats: dict[str, bpy.types.Material],
    include_ends: bool,
) -> list[bpy.types.Object]:
    objects = [
        tbox(
            f"{name}_OuterBrickCrown",
            (length, 0.34, CROWN_HEIGHT),
            (0.0, -WING_DEPTH / 2.0 + 0.17, z_base + CROWN_HEIGHT / 2.0),
            mats["brick"],
            0.015,
            tile_m=0.80,
        ),
        tbox(
            f"{name}_CourtBrickCrown",
            (length, 0.34, CROWN_HEIGHT),
            (0.0, WING_DEPTH / 2.0 - 0.17, z_base + CROWN_HEIGHT / 2.0),
            mats["brick"],
            0.015,
            tile_m=0.80,
        ),
        tbox(
            f"{name}_ProjectingEaveDatumOuter",
            (length + 0.18, 0.46, 0.12),
            (0.0, -WING_DEPTH / 2.0 - 0.04, z_base + CROWN_HEIGHT - 0.06),
            mats["metal"],
            0.010,
            tile_m=0.65,
        ),
        tbox(
            f"{name}_HiddenCourtGutterDatum",
            (length + 0.18, 0.36, 0.11),
            (0.0, WING_DEPTH / 2.0 + 0.02, z_base + CROWN_HEIGHT - 0.07),
            mats["metal"],
            0.010,
            tile_m=0.65,
        ),
    ]
    if include_ends:
        objects.extend(
            add_end_walls(
                name,
                length=length,
                depth=WING_DEPTH,
                z_base=z_base,
                height=CROWN_HEIGHT,
                mats=mats,
            )
        )
    return objects


def gable_roof_mesh(
    name: str,
    *,
    length: float,
    depth: float,
    base_z: float,
    rise: float,
    mat: bpy.types.Material,
    cap_ends: bool = True,
) -> bpy.types.Object:
    half_l = length / 2.0
    half_d = depth / 2.0
    vertices = [
        (-half_l, -half_d, base_z),
        (half_l, -half_d, base_z),
        (half_l, half_d, base_z),
        (-half_l, half_d, base_z),
        (-half_l, 0.0, base_z + rise),
        (half_l, 0.0, base_z + rise),
    ]
    faces: list[tuple[int, ...]] = [
        (0, 1, 5, 4),
        (4, 5, 2, 3),
        (0, 3, 2, 1),
    ]
    if cap_ends:
        faces.extend([(0, 4, 3), (1, 2, 5)])
    return mesh_object(
        name,
        vertices,
        faces,
        mat,
        uv_scale=max(4.0, length / 1.8),
    )


def roof_skylight(
    name: str,
    *,
    x: float,
    slope_sign: int,
    base_z: float,
    rise: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    half_depth = (WING_DEPTH + ROOF_WIDTH_OVERHANG) / 2.0
    y = slope_sign * half_depth * 0.54
    z = base_z + rise * (1.0 - abs(y) / half_depth)
    angle = math.atan2(rise, half_depth)
    rotation = -slope_sign * angle
    frame = tbox(
        f"{name}_DarkMetalCurb",
        (1.34, 1.58, 0.14),
        (x, y, z + 0.10),
        mats["metal"],
        0.025,
        tile_m=0.65,
    )
    pane = tbox(
        f"{name}_PhysicalSkylightPane",
        (1.12, 1.34, 0.065),
        (
            x,
            y - slope_sign * 0.015,
            z + 0.17,
        ),
        mats["glass"],
        0.012,
        tile_m=0.8,
    )
    frame.rotation_euler.x = rotation
    pane.rotation_euler.x = rotation
    return [frame, pane]


def build_roof_wing(
    name: str,
    *,
    length: float,
    z_base: float,
    mats: dict[str, bpy.types.Material],
    skylights: bool,
    cap_ends: bool = True,
) -> list[bpy.types.Object]:
    roof_length = length + ROOF_END_OVERHANG
    roof_depth = WING_DEPTH + ROOF_WIDTH_OVERHANG
    rise = ROOF_HEIGHT - 0.18
    objects: list[bpy.types.Object] = [
        gable_roof_mesh(
            f"{name}_ConnectedPitchedRoof",
            length=roof_length,
            depth=roof_depth,
            base_z=z_base + 0.02,
            rise=rise,
            mat=mats["roof"],
            cap_ends=cap_ends,
        ),
        round_beam(
            f"{name}_PhysicalRidgeCap",
            (-roof_length / 2.0, 0.0, z_base + rise + 0.03),
            (roof_length / 2.0, 0.0, z_base + rise + 0.03),
            0.085,
            mats["roof"],
            vertices=14,
        ),
    ]
    half_depth = roof_depth / 2.0
    for side in (-1, 1):
        objects.extend(
            [
                tbox(
                    f"{name}_EaveFascia_{side:+d}",
                    (roof_length, 0.15, 0.23),
                    (0.0, side * (half_depth - 0.03), z_base + 0.06),
                    mats["metal"],
                    0.016,
                    tile_m=0.65,
                ),
                round_beam(
                    f"{name}_ContinuousEaveGutter_{side:+d}",
                    (-roof_length / 2.0, side * half_depth, z_base + 0.01),
                    (roof_length / 2.0, side * half_depth, z_base + 0.01),
                    0.075,
                    mats["metal"],
                    vertices=12,
                ),
            ]
        )
        for course in range(1, 9):
            fraction = course / 9.0
            y = side * half_depth * fraction
            z = z_base + rise * (1.0 - fraction)
            objects.append(
                round_beam(
                    f"{name}_PhysicalTileCourse_{side:+d}_{course:02d}",
                    (-roof_length / 2.0 + 0.08, y, z + 0.015),
                    (roof_length / 2.0 - 0.08, y, z + 0.015),
                    0.022,
                    mats["roof"],
                    vertices=8,
                )
            )
    if skylights and length >= 15.0:
        skylight_offset = min(7.6, length * 0.29)
        for index, x in enumerate((-skylight_offset, skylight_offset)):
            objects.extend(
                roof_skylight(
                    f"{name}_RestrainedSkylight_{index}",
                    x=x,
                    slope_sign=-1,
                    base_z=z_base,
                    rise=rise,
                    mats=mats,
                )
            )
    return objects


def hip_corner_roof(
    name: str,
    *,
    centre_x: float,
    centre_y: float,
    x_sign: int,
    y_sign: int,
    base_z: float,
    rise: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    """Close one ring corner while continuing both incoming roof ridges."""
    half = (WING_DEPTH + ROOF_WIDTH_OVERHANG) / 2.0
    outer_x = centre_x + x_sign * half
    inner_x = centre_x - x_sign * half
    outer_y = centre_y + y_sign * half
    inner_y = centre_y - y_sign * half
    peak_z = base_z + rise
    vertices = [
        (outer_x, outer_y, base_z),  # 0 exterior corner
        (inner_x, outer_y, base_z),  # 1 front/rear outer eave join
        (inner_x, inner_y, base_z),  # 2 courtyard valley corner
        (outer_x, inner_y, base_z),  # 3 return outer eave join
        (inner_x, centre_y, peak_z),  # 4 front/rear ridge endpoint
        (centre_x, inner_y, peak_z),  # 5 return ridge endpoint
        (centre_x, centre_y, peak_z),  # 6 shared corner ridge apex
    ]
    raw_faces = [
        (0, 1, 4, 6),
        (6, 4, 2),
        (6, 2, 5),
        (0, 6, 5, 3),
        (0, 3, 2, 1),
    ]

    def upward(face: tuple[int, ...]) -> tuple[int, ...]:
        a, b, c = (Vector(vertices[index]) for index in face[:3])
        return tuple(reversed(face)) if (b - a).cross(c - a).z < 0 else face

    roof = mesh_object(
        f"{name}_FourPlaneHipRoof",
        vertices,
        [upward(face) for face in raw_faces],
        mats["roof"],
        uv_scale=3.2,
    )
    apply_true_scale_uv(roof, tile_m=1.8)
    objects: list[bpy.types.Object] = [
        roof,
        round_beam(
            f"{name}_FrontRidgeContinuation",
            vertices[4],
            vertices[6],
            0.075,
            mats["roof"],
            vertices=12,
        ),
        round_beam(
            f"{name}_ReturnRidgeContinuation",
            vertices[6],
            vertices[5],
            0.075,
            mats["roof"],
            vertices=12,
        ),
    ]

    def lerp(start: tuple[float, float, float], end: tuple[float, float, float], t: float):
        return tuple(
            start[index] + (end[index] - start[index]) * t
            for index in range(3)
        )

    course_edges = {
        "OuterStreetPlane": (vertices[0], vertices[6], vertices[1], vertices[4]),
        "InnerStreetPlane": (vertices[6], vertices[2], vertices[4], vertices[2]),
        "InnerReturnPlane": (vertices[6], vertices[2], vertices[5], vertices[2]),
        "OuterReturnPlane": (vertices[0], vertices[6], vertices[3], vertices[5]),
    }
    for face_label, (start_a, end_a, start_b, end_b) in course_edges.items():
        for index in range(1, 5):
            fraction = index / 5.0
            point_a = lerp(start_a, end_a, fraction)
            point_b = lerp(start_b, end_b, fraction)
            point_a = (point_a[0], point_a[1], point_a[2] + 0.015)
            point_b = (point_b[0], point_b[1], point_b[2] + 0.015)
            objects.append(
                round_beam(
                    f"{name}_{face_label}_TileCourse_{index:02d}",
                    point_a,
                    point_b,
                    0.018,
                    mats["roof"],
                    vertices=8,
                )
            )
    return objects


def build_downpipes(
    name: str,
    *,
    surface_y: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    for index, x in enumerate((-5.55, 5.55)):
        objects.extend(
            [
                cylinder(
                    f"{name}_IntegratedDownpipe_{index}",
                    0.065,
                    BODY_HEIGHT - 0.28,
                    (x, surface_y - 0.10, BODY_HEIGHT / 2.0),
                    mats["metal"],
                    vertices=12,
                ),
                tbox(
                    f"{name}_DownpipeShoe_{index}",
                    (0.13, 0.28, 0.16),
                    (x, surface_y - 0.01, 0.11),
                    mats["metal"],
                    0.015,
                    tile_m=0.5,
                ),
            ]
        )
    return objects


def build_assembled(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    wing_specs = [
        {
            "name": "MEWS_PublicStreetWing",
            "length": WIDTH,
            "roof_length": (
                COURT_WIDTH - ROOF_WIDTH_OVERHANG - ROOF_END_OVERHANG
            ),
            "translation": (0.0, -(BLOCK_DEPTH - WING_DEPTH) / 2.0, 0.0),
            "rotation": 0.0,
            "front": "public",
            "rear_ground": "passage",
            "rear_upper": "quiet",
            "through": True,
            "skylights": True,
            "ends": True,
        },
        {
            "name": "MEWS_RearGardenWing",
            "length": WIDTH,
            "roof_length": (
                COURT_WIDTH - ROOF_WIDTH_OVERHANG - ROOF_END_OVERHANG
            ),
            "translation": (0.0, (BLOCK_DEPTH - WING_DEPTH) / 2.0, 0.0),
            "rotation": 0.0,
            "front": "quiet",
            "rear_ground": "quiet",
            "rear_upper": "quiet",
            "through": False,
            "skylights": True,
            "ends": True,
        },
        {
            "name": "MEWS_LeftReturnWing",
            "length": COURT_DEPTH,
            "roof_length": (
                COURT_DEPTH - ROOF_WIDTH_OVERHANG - ROOF_END_OVERHANG
            ),
            "translation": (-(WIDTH - WING_DEPTH) / 2.0, 0.0, 0.0),
            "rotation": -90.0,
            "front": "quiet",
            "rear_ground": "quiet",
            "rear_upper": "quiet",
            "through": False,
            "skylights": False,
            "ends": False,
        },
        {
            "name": "MEWS_RightReturnWing",
            "length": COURT_DEPTH,
            "roof_length": (
                COURT_DEPTH - ROOF_WIDTH_OVERHANG - ROOF_END_OVERHANG
            ),
            "translation": ((WIDTH - WING_DEPTH) / 2.0, 0.0, 0.0),
            "rotation": 90.0,
            "front": "quiet",
            "rear_ground": "quiet",
            "rear_upper": "quiet",
            "through": False,
            "skylights": False,
            "ends": False,
        },
    ]
    for spec in wing_specs:
        wing_objects: list[bpy.types.Object] = []
        wing_objects.extend(
            build_level_wing(
                name=spec["name"],
                length=spec["length"],
                z_base=0.0,
                role="podium",
                variant="default",
                front_style=spec["front"],
                rear_style=spec["rear_ground"],
                mats=mats,
                include_ends=spec["ends"],
                through_passage=spec["through"],
            )
        )
        wing_objects.extend(
            build_level_wing(
                name=spec["name"],
                length=spec["length"],
                z_base=FLOOR_HEIGHT,
                role="floor",
                variant="typical_a",
                front_style=spec["front"],
                rear_style=spec["rear_upper"],
                mats=mats,
                include_ends=spec["ends"],
            )
        )
        wing_objects.extend(
            build_level_wing(
                name=spec["name"],
                length=spec["length"],
                z_base=FLOOR_HEIGHT * 2.0,
                role="floor",
                variant="typical_b",
                front_style=spec["front"],
                rear_style=spec["rear_upper"],
                mats=mats,
                include_ends=spec["ends"],
            )
        )
        wing_objects.extend(
            build_crown_wing(
                spec["name"],
                length=spec["length"],
                z_base=BODY_HEIGHT,
                mats=mats,
                include_ends=spec["ends"],
            )
        )
        wing_objects.extend(
            build_roof_wing(
                spec["name"],
                length=spec["roof_length"],
                z_base=BODY_HEIGHT + CROWN_HEIGHT,
                mats=mats,
                skylights=spec["skylights"],
                cap_ends=False,
            )
        )
        transform_objects(
            wing_objects,
            translation=spec["translation"],
            rotation_degrees=spec["rotation"],
        )
        objects.extend(wing_objects)
    # The open court is deliberately only a paving plane: no slab, wall, or
    # roof crosses the void above it.
    objects.extend(
        [
            tbox(
                "MEWS_OpenToSkyCourtyard_Paving",
                (COURT_WIDTH, COURT_DEPTH, 0.07),
                (0.0, 0.0, 0.035),
                mats["paving"],
                0.006,
                tile_m=1.15,
            ),
            tbox(
                "MEWS_PublicThreshold_Paving",
                (WIDTH + 1.8, 2.4, 0.07),
                (0.0, -BLOCK_DEPTH / 2.0 - 1.15, 0.035),
                mats["paving"],
                0.006,
                tile_m=1.15,
            ),
        ]
    )
    # Each straight field stops at a mathematically shared eave boundary. Four
    # physical corner hips and their inner valleys complete one connected roof
    # ring without crossing—or ever capping—the open courtyard.
    roof_base = BODY_HEIGHT + CROWN_HEIGHT
    rise = ROOF_HEIGHT - 0.18
    for x_sign in (-1, 1):
        for y_sign in (-1, 1):
            apex = (
                x_sign * (WIDTH - WING_DEPTH) / 2.0,
                y_sign * (BLOCK_DEPTH - WING_DEPTH) / 2.0,
                roof_base + rise,
            )
            objects.extend(
                hip_corner_roof(
                    f"MEWS_CornerRoof_{x_sign:+d}_{y_sign:+d}",
                    centre_x=apex[0],
                    centre_y=apex[1],
                    x_sign=x_sign,
                    y_sign=y_sign,
                    base_z=roof_base + 0.02,
                    rise=rise,
                    mats=mats,
                )
            )
            objects.extend(
                [
                    round_beam(
                        f"MEWS_ConnectedRoofValley_{x_sign:+d}_{y_sign:+d}",
                        (
                            x_sign * COURT_WIDTH / 2.0,
                            y_sign * COURT_DEPTH / 2.0,
                            roof_base + 0.03,
                        ),
                        apex,
                        0.085,
                        mats["metal"],
                        vertices=12,
                    ),
                    round_beam(
                        f"MEWS_ExteriorRoofHip_{x_sign:+d}_{y_sign:+d}",
                        (
                            x_sign * (WIDTH / 2.0 + 0.28),
                            y_sign * (BLOCK_DEPTH / 2.0 + 0.28),
                            roof_base + 0.03,
                        ),
                        apex,
                        0.075,
                        mats["roof"],
                        vertices=12,
                    ),
                ]
            )
    court_pipe_positions = (
        ("PublicLeft", -5.70, -COURT_DEPTH / 2.0 + 0.10),
        ("PublicRight", 5.70, -COURT_DEPTH / 2.0 + 0.10),
        ("RearLeft", -5.70, COURT_DEPTH / 2.0 - 0.10),
        ("RearRight", 5.70, COURT_DEPTH / 2.0 - 0.10),
        ("LeftFront", -COURT_WIDTH / 2.0 + 0.10, -3.30),
        ("LeftRear", -COURT_WIDTH / 2.0 + 0.10, 3.30),
        ("RightFront", COURT_WIDTH / 2.0 - 0.10, -3.30),
        ("RightRear", COURT_WIDTH / 2.0 - 0.10, 3.30),
    )
    for label, x, y in court_pipe_positions:
        objects.extend(
            [
                cylinder(
                    f"MEWS_Courtyard_{label}_IntegratedDownpipe",
                    0.055,
                    BODY_HEIGHT - 0.28,
                    (x, y, BODY_HEIGHT / 2.0),
                    mats["metal"],
                    vertices=12,
                ),
                tbox(
                    f"MEWS_Courtyard_{label}_DownpipeShoe",
                    (0.14, 0.18, 0.16),
                    (x, y, 0.11),
                    mats["metal"],
                    0.012,
                    tile_m=0.5,
                ),
            ]
        )
    objects.extend(
        build_downpipes(
            "MEWS_PublicStreetWing",
            surface_y=-BLOCK_DEPTH / 2.0,
            mats=mats,
        )
    )
    return objects


def build_module(
    role: str,
    variant: str,
    height: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    if role == "podium":
        return build_level_wing(
            name=f"MEWSKIT_{role}_{variant}",
            length=WIDTH,
            z_base=0.0,
            role=role,
            variant=variant,
            front_style="public",
            rear_style="passage",
            mats=mats,
            include_ends=True,
            through_passage=True,
        )
    if role == "floor":
        return build_level_wing(
            name=f"MEWSKIT_{role}_{variant}",
            length=WIDTH,
            z_base=0.0,
            role=role,
            variant=variant,
            front_style="public",
            rear_style="quiet",
            mats=mats,
            include_ends=True,
        )
    if role == "crown":
        return build_crown_wing(
            f"MEWSKIT_{role}_{variant}",
            length=WIDTH,
            z_base=0.0,
            mats=mats,
            include_ends=True,
        )
    if role == "roof":
        objects = build_roof_wing(
            f"MEWSKIT_{role}_{variant}",
            length=WIDTH,
            z_base=0.0,
            mats=mats,
            skylights=True,
        )
        # The eave gutter is a physical cylinder centred 1 cm above the module
        # datum. Lift the complete roof kit so its 7.5 cm radius remains on or
        # above the glTF bottom-centre origin contract.
        transform_objects(objects, translation=(0.0, 0.0, 0.07))
        return objects
    raise ValueError(f"unsupported module role {role}")


def render_views(
    folder: Path,
    *,
    view_set: str,
) -> list[str]:
    setup_render()
    scene = bpy.context.scene
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 950
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.exposure = 0.58
    background = scene.world.node_tree.nodes.get("Background")
    if background:
        background.inputs["Color"].default_value = (0.39, 0.40, 0.39, 1.0)
        background.inputs["Strength"].default_value = 0.88
    ground = bpy.data.materials.get("MAT_W3_Ground")
    if ground and ground.use_nodes:
        ground.node_tree.nodes["Principled BSDF"].inputs[
            "Base Color"
        ].default_value = (0.36, 0.35, 0.32, 1.0)
    bpy.ops.object.light_add(
        type="SUN",
        location=(-48.0, -72.0, 85.0),
    )
    sun = bpy.context.object
    sun.name = "PRESENTATION_W10_SoftSun"
    sun.data.energy = 1.85
    sun.data.color = (1.0, 0.84, 0.66)
    sun.data.angle = math.radians(11.0)
    sun.rotation_euler = (
        Vector((0.0, 0.0, 5.0)) - sun.location
    ).to_track_quat("-Z", "Y").to_euler()
    views = {
        "preview": (
            (21.0, -45.0, 17.0),
            (0.0, -1.4, 5.6),
            56,
        ),
        "street": (
            (2.0, -48.0, 6.2),
            (0.0, -10.8, 5.2),
            54,
        ),
        "front_corner_oblique": (
            (-24.0, -38.0, 14.0),
            (0.0, -1.0, 5.3),
            52,
        ),
        "rear_corner_oblique": (
            (23.0, 37.0, 15.0),
            (0.0, 1.5, 5.5),
            52,
        ),
        "aerial": (
            (25.0, -31.0, 37.0),
            (0.0, 0.0, 4.0),
            52,
        ),
        "facade_close": (
            (0.0, -39.0, 5.3),
            (0.0, -11.4, 5.2),
            63,
        ),
        "identity_close": (
            (-7.5, -25.5, 4.3),
            (-4.0, -11.6, 2.7),
            57,
        ),
        "courtyard_close": (
            (0.0, 4.2, 2.55),
            (-3.0, -7.7, 5.2),
            22,
        ),
        "context": (
            (28.0, -45.0, 22.0),
            (0.0, 0.0, 5.2),
            58,
        ),
    }
    selected = (
        {
            "preview",
            "street",
            "front_corner_oblique",
            "aerial",
            "courtyard_close",
            "identity_close",
        }
        if view_set == "pilot"
        else set(views)
    )
    snapshots: list[
        tuple[
            bpy.types.Material,
            bpy.types.Node,
            float,
            float,
            str,
            tuple[float, float, float, float],
        ]
    ] = []
    for mat in bpy.data.materials:
        if not mat.get("glazing_profile") or not mat.use_nodes:
            continue
        bsdf = next(
            (
                node
                for node in mat.node_tree.nodes
                if node.bl_idname == "ShaderNodeBsdfPrincipled"
            ),
            None,
        )
        if bsdf is None or not bsdf.inputs.get("Alpha"):
            continue
        transmission = bsdf.inputs.get("Transmission Weight")
        snapshots.append(
            (
                mat,
                bsdf,
                float(bsdf.inputs["Alpha"].default_value),
                float(transmission.default_value) if transmission else 0.0,
                getattr(mat, "surface_render_method", "DITHERED"),
                tuple(bsdf.inputs["Base Color"].default_value),
            )
        )
        # A near-opaque proof tint makes the neutral low-e material read as
        # dark residential glass under the studio world. The GLB was exported
        # before this proof-only override and retains physical transmission.
        bsdf.inputs["Base Color"].default_value = (0.010, 0.017, 0.020, 1.0)
        bsdf.inputs["Alpha"].default_value = 0.86
        mat.diffuse_color = (0.010, 0.017, 0.020, 0.86)
        if transmission:
            transmission.default_value = 0.0
        if hasattr(mat, "surface_render_method"):
            mat.surface_render_method = "BLENDED"
    rendered: list[str] = []
    try:
        for role, (location, target, lens) in views.items():
            if role not in selected:
                continue
            aim_camera(location, target, lens)
            filename = f"{FAMILY}_{role}.png"
            scene.render.filepath = str(folder / filename)
            bpy.ops.render.render(write_still=True)
            rendered.append(filename)
    finally:
        for (
            mat,
            bsdf,
            alpha,
            transmission_value,
            method,
            base_colour,
        ) in snapshots:
            bsdf.inputs["Base Color"].default_value = base_colour
            bsdf.inputs["Alpha"].default_value = alpha
            transmission = bsdf.inputs.get("Transmission Weight")
            if transmission:
                transmission.default_value = transmission_value
            if hasattr(mat, "surface_render_method"):
                mat.surface_render_method = method
            mat.diffuse_color = (*tuple(mat.diffuse_color)[:3], 1.0)
    delete_objects(
        [
            obj
            for obj in list(bpy.data.objects)
            if obj.name.startswith("PRESENTATION_")
        ]
    )
    if (folder / "elevation.jpg").is_file():
        rendered.append("elevation.jpg")
    return rendered


def texture_inventory(skin: dict) -> list[dict]:
    return [
        {
            "key": f"{zone}_{lod}_{channel}",
            "path": path,
            "lod": lod,
            "channel": channel,
            "zone": zone,
        }
        for zone, lods in skin["zones"].items()
        for lod, assets in lods.items()
        for channel, path in assets.items()
    ]


def evaluated_triangle_count(objects: list[bpy.types.Object]) -> int:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total = 0
    for obj in objects:
        if obj.type != "MESH":
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh(
            preserve_all_data_layers=False,
            depsgraph=depsgraph,
        )
        try:
            total += sum(
                max(0, len(polygon.vertices) - 2)
                for polygon in mesh.polygons
            )
        finally:
            evaluated.to_mesh_clear()
    return total


def material_count(objects: list[bpy.types.Object]) -> int:
    return len(
        {
            mat.name
            for obj in objects
            if obj.type == "MESH"
            for mat in obj.data.materials
        }
    )


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
        "allowed_levels": [],
        "filename": filename,
        "module_family": FAMILY,
        "width_m": WIDTH,
        "depth_m": WING_DEPTH,
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


def footprint_compatibility() -> dict:
    return {
        "preferredProfiles": ["courtyard", "u_shape", "rectangle"],
        "minimumPreferredProfiles": 3,
        "profileRationale": (
            "The canonical family is a four-wing open court, while each LEGO "
            "unit is one occupied five-metre-deep bar. Whole bars turn corners "
            "and repeat along long axes, preserving room-scale windows, arches, "
            "soldier courses and roof pitch as user drawings vary."
        ),
        "fixedLandmarkScaleBand": {
            "scaleMin": 0.84,
            "scaleMax": 1.16,
            "maxAxisRatio": 1.15,
        },
        "recommendedWidth_m": [24, 42],
        "recommendedDepth_m": [18, 36],
        "recommendedFloors": [2, 6],
        "wingDepth_m": [4.6, 7.0],
        "preferredBayMultiple_m": 3.5,
        "minimumCourtyard_m": 8.0,
        "profiles": {
            "courtyard": {
                "recommendedWidth_m": [24, 42],
                "recommendedDepth_m": [20, 36],
                "recommendedFloors": [2, 6],
                "wingDepth_m": [4.6, 7.0],
                "minimumCourtyard_m": 8.0,
            },
            "u_shape": {
                "recommendedWidth_m": [22, 42],
                "recommendedDepth_m": [16, 36],
                "recommendedFloors": [2, 6],
                "wingDepth_m": [4.6, 7.0],
                "minimumCourtyard_m": 8.0,
            },
            "rectangle": {
                "recommendedWidth_m": [22, 42],
                "recommendedDepth_m": [8, 30],
                "recommendedFloors": [2, 6],
            },
        },
        "notes": [
            "Keep the public through-passage and grouped arches on the entrance bar.",
            "Keep the courtyard open through podium, floor, crown, and roof roles.",
            "Repeat whole 3.5 metre residential bays; never stretch individual windows.",
            "Use the family-shaped streetwall repeat for oversized targets.",
        ],
    }


def provenance() -> dict:
    return {
        "kind": (
            "catalogue_goalpost_plus_imagegen_multiview_package_and_"
            "authored_courtyard_construction"
        ),
        "catalogue_archetype_id": ARCHETYPE_ID,
        "catalogue_variant_id": VARIANT_ID,
        "goalpost": "/archetypes/buildings/courtyard_family_housing/variant_2.png",
        "goalpost_local_source": "textures/source/archetype-goalpost.png",
        "orthographic_elevation": "textures/source/elevation-source-v1.png",
        "aerial_reference": "textures/source/aerial-source-v1.png",
        "courtyard_reference": "textures/source/courtyard-source-v1.png",
        "reference_underlay": "textures/source/occupied-depth-source-v1.png",
        "brick_material_source": "textures/source/buff-brick-material-source-v1.png",
        "reference_generation": "textures/source/reference-generation.json",
        "registered_openings": "textures/source/registered-openings.json",
        "registered_bands": "textures/source/registered-bands.json",
        "elevation_source": f"/families/{FAMILY}/elevation.jpg",
        "skin_manifest": "textures/skin_manifest.json",
        "generator": (
            "tools/archetype_compiler/generate_wave10_courtyard_family.py"
        ),
        "reference_method": (
            "hard catalogue goalpost, rectified public elevation, generated "
            "aerial and courtyard construction views, physical cavity schedule, "
            "custom true-scale PBR, occupied-depth underlay, and finite "
            "street/oblique/aerial/courtyard comparison"
        ),
    }


def facade_contract(skin: dict) -> dict:
    return {
        "schema": "facade-sheet@5",
        "source_directory": f"/families/{FAMILY}",
        "model": "gpt-image-2",
        "style_reference": "elevation.jpg",
        "goalpost_reference": (
            "/archetypes/buildings/courtyard_family_housing/variant_2.png"
        ),
        "goalpost_policy": (
            "The catalogue and authored reference package fix three occupied "
            "buff-brick levels, grouped arches, real through-passage, Juliet "
            "guards, open court, and connected pitched-roof ring."
        ),
        "runtime_material_profile": "pbr_physical_glazing_v2",
        "geometry_detail_profile": "hero",
        "pbr_channels": [
            "albedo",
            "normal",
            "roughness",
            "ao",
            "depth",
            "emissive",
        ],
        "shadow_neutral": {"enabled": True, **skin["shadow_neutral"]},
        "bay_strategy": {
            "fixed_end_bays": [0, 7],
            "repeatable_middle_bays": [1, 2, 3, 4, 5, 6],
            "middle_variants": ["typical_a", "typical_b", "typical_c"],
            "rule": (
                "Repeat complete occupied mews bays. Keep the carriage passage, "
                "storage arches, corner joins, crown, and pitched roof semantic."
            ),
        },
        "delivery": {
            "near_atlas_width_px": 2048,
            "far_atlas_width_px": 1024,
            "near_usage": (
                "true-scale buff brick plus physical window cavities, low-e "
                "panes, occupied depth, steel guards, arches, gutters, and roof"
            ),
            "far_usage": "city-scale render-locked archetype material reference",
        },
        "assembly_contract": {
            "fixed": [
                "podium/entrance",
                "corner returns",
                "crown",
                "roof",
                "grouped ground arches",
                "through carriage passage",
                "integrated bicycle recesses",
                "soldier-course datums",
                "black Juliet guards",
                "open courtyard void",
            ],
            "repeatable": ["typical_a", "typical_b", "typical_c"],
            "side_elevations": (
                "Room-scale openings, soldier bands, brick returns, eaves, "
                "gutters, and roof pitch continue around every court edge."
            ),
            "elevation_coverage": {
                "front": "grouped arches, passage, black Juliet guards, and restrained skylights",
                "left": "quiet occupied return with aligned soldier courses",
                "right": "quiet occupied return with aligned soldier courses",
                "rear": "quieter occupied garden elevation",
                "courtyard": "open paved court and traversable public passage",
                "roof": "four connected pitched strips with open central void",
            },
            "variation_policy": (
                "Mild full-envelope scaling is safe. Larger targets place "
                "multiple whole occupied bars with the planner's streetwall "
                "repeat instead of stretching windows or roof construction."
            ),
        },
        "assets": {
            "skin_manifest": "textures/skin_manifest.json",
            "source": skin["source"],
            "near": skin["zones"]["brick"]["near"],
            "far": skin["zones"]["brick"]["far"],
            "sources": skin["sources"],
        },
        "reference_registration": skin["reference_registration"],
    }


def write_metadata(
    folder: Path,
    skin: dict,
    modules: list[dict],
    fixed_triangles: int,
    fixed_materials: int,
    assembled_path: Path,
    renders: list[str],
) -> None:
    footprint = footprint_compatibility()
    stack = [
        {
            "role": "podium",
            "variant_key": "default",
            "level": 0,
            "z_m": 0.0,
            "height_m": FLOOR_HEIGHT,
        },
        {
            "role": "floor",
            "variant_key": "typical_a",
            "level": 1,
            "z_m": FLOOR_HEIGHT,
            "height_m": FLOOR_HEIGHT,
        },
        {
            "role": "floor",
            "variant_key": "typical_b",
            "level": 2,
            "z_m": FLOOR_HEIGHT * 2.0,
            "height_m": FLOOR_HEIGHT,
        },
        {
            "role": "crown",
            "variant_key": "crown",
            "level": 3,
            "z_m": BODY_HEIGHT,
            "height_m": CROWN_HEIGHT,
        },
        {
            "role": "roof",
            "variant_key": "default",
            "level": 4,
            "z_m": BODY_HEIGHT + CROWN_HEIGHT,
            "height_m": ROOF_HEIGHT,
        },
    ]
    segments = [
        {
            "id": "front",
            "centre_x_m": 0.0,
            "centre_y_m": -(BLOCK_DEPTH - WING_DEPTH) / 2.0,
            "length_m": WIDTH,
            "thickness_m": WING_DEPTH,
            "rotation_degrees": 0.0,
        },
        {
            "id": "rear",
            "centre_x_m": 0.0,
            "centre_y_m": (BLOCK_DEPTH - WING_DEPTH) / 2.0,
            "length_m": WIDTH,
            "thickness_m": WING_DEPTH,
            "rotation_degrees": 0.0,
        },
        {
            "id": "left_return",
            "centre_x_m": -(WIDTH - WING_DEPTH) / 2.0,
            "centre_y_m": 0.0,
            "length_m": BLOCK_DEPTH,
            "thickness_m": WING_DEPTH,
            "rotation_degrees": 90.0,
        },
        {
            "id": "right_return",
            "centre_x_m": (WIDTH - WING_DEPTH) / 2.0,
            "centre_y_m": 0.0,
            "length_m": BLOCK_DEPTH,
            "thickness_m": WING_DEPTH,
            "rotation_degrees": 90.0,
        },
    ]
    assembled = {
        "filename": assembled_path.name,
        "floors": 3,
        "uses_setback": False,
        "uses_crown": True,
        "height_m": TOTAL_HEIGHT,
        "triangle_count": fixed_triangles,
        "material_count": fixed_materials,
        "stack": stack,
        "footprint_profile": "courtyard",
        "footprint_target": {
            "width_m": WIDTH,
            "depth_m": BLOCK_DEPTH,
            "wing_depth_m": WING_DEPTH,
            "segments": segments,
        },
        "massing_graph": {
            "type": "open_courtyard_perimeter",
            "court_width_m": COURT_WIDTH,
            "court_depth_m": COURT_DEPTH,
            "passage_centre_x_m": -3.5,
            "passage_width_m": 4.3,
            "roof_void_preserved": True,
        },
        "texture_keys": sorted(skin["zones"]),
        "ao_baked": True,
    }
    dimensions = {
        "width_m": WIDTH,
        "depth_m": BLOCK_DEPTH,
        "wing_depth_m": WING_DEPTH,
        "courtyard_width_m": COURT_WIDTH,
        "courtyard_depth_m": COURT_DEPTH,
        "podium_height_m": FLOOR_HEIGHT,
        "floor_height_m": FLOOR_HEIGHT,
        "setback_height_m": FLOOR_HEIGHT,
        "roof_height_m": ROOF_HEIGHT,
        "crown_height_m": CROWN_HEIGHT,
        "default_floors": 3,
        "min_floors": 2,
        "max_floors": 6,
    }
    identity = (
        "A three-level golden-buff-brick mews forms four occupied wings around "
        "one open paved court, entered through a deep brick carriage passage "
        "within four grouped arches and detailed by room-scale black windows, "
        "Juliet guards, aligned soldier courses, bicycle recesses, and a "
        "connected dark pitched-tile roof ring."
    )
    material_zones = (
        "fine golden-buff running-bond brick and pale mortar; darker soldier "
        "courses and passage soffits; charcoal powder-coated window frames, "
        "Juliet guards, gutters and downpipes; neutral residential low-e glass; "
        "muted occupied-room depth; dark grey concrete roof tile; grey unit paving"
    )
    source = provenance()
    manifest = {
        "manifest_schema": 3,
        "grammar_schema_version": 3,
        "generator": {
            "name": "archetype_compiler/generate_wave10_courtyard_family.py",
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
        "archetype_aliases": [ARCHETYPE_ID, VARIANT_ID],
        "aesthetic_category_id": "contemporary_north_american",
        "development_type": "residential_multifamily",
        "reuse_keys": [
            ARCHETYPE_ID,
            VARIANT_ID,
            "Courtyard Housing",
            "Family Housing",
            "Modern Brick Mews",
            "Low-Rise Residential",
        ],
        "generation_tags": [
            "wave10_courtyard_pilot",
            "standard_building",
            "modular_courtyard_streetwall",
            "custom_pbr_skin",
            "physical_residential_glazing",
            "reference_locked",
            "four_wing_open_courtyard",
            "deep_through_carriage_passage",
            "grouped_ground_arches",
            "integrated_bicycle_storage",
            "room_scale_black_windows",
            "black_steel_juliet_balconies",
            "soldier_course_datums",
            "connected_pitched_roof_ring",
        ],
        "footprint_compatibility": footprint,
        "coordinate_contract": COORDINATE_CONTRACT,
        "textures": texture_inventory(skin),
        "facade_sheet": facade_contract(skin),
        "massing_graph": {
            "type": "open_courtyard_perimeter",
            "silhouette": "three_level_buff_brick_ring_beneath_connected_pitched_roofs",
            "render_locked": True,
            "goalpost": (
                "/archetypes/buildings/courtyard_family_housing/variant_2.png"
            ),
            "fallback": "family_shaped_modular_streetwall",
            "court_width_m": COURT_WIDTH,
            "court_depth_m": COURT_DEPTH,
            "roof_void_preserved": True,
        },
        "material_budget": {
            "max_assembled_materials": 18,
            "rationale": (
                "Construction PBR, physical low-e glazing, registered occupied "
                "depth, passage shadow, and paving remain semantic."
            ),
        },
        "dimensions": dimensions,
        "native_width_m": WIDTH,
        "native_depth_m": BLOCK_DEPTH,
        "native_floors": 3,
        "min_floors": 2,
        "max_floors": 6,
        "default_floors": 3,
        "modules": modules,
        "assembled": assembled,
        "thumbnail": f"{FAMILY}_preview.png",
        "renders": renders,
        "architectural_identity": identity,
        "material_zones": material_zones,
        "glass_profile": GLASS_PROFILE,
        "source_provenance": source,
    }
    (folder / f"{FAMILY}_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
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
        "dimensions": dimensions,
        "architectural_signature": {
            "identity": identity,
            "material_zones": material_zones,
            "glass_profile": GLASS_PROFILE,
            "kits": [
                "four_wing_open_courtyard",
                "deep_through_carriage_passage",
                "grouped_ground_arches",
                "integrated_bicycle_storage",
                "room_scale_black_windows",
                "black_steel_juliet_balconies",
                "soldier_course_datums",
                "connected_pitched_roof_ring",
            ],
        },
        "archetype_aliases": [ARCHETYPE_ID, VARIANT_ID],
        "footprint_compatibility": footprint,
        "massing_graph": manifest["massing_graph"],
    }
    (folder / "grammar.json").write_text(
        json.dumps(grammar, indent=2) + "\n",
        encoding="utf-8",
    )
    (folder / "archetype-source.json").write_text(
        json.dumps(source, indent=2) + "\n",
        encoding="utf-8",
    )


def build_family(
    output_root: Path,
    *,
    view_set: str,
    skip_renders: bool,
    skip_modules: bool,
) -> None:
    clear_scene()
    folder = output_root / FAMILY
    folder.mkdir(parents=True, exist_ok=True)
    mats, skin = load_palette(folder)
    fixed = build_assembled(mats)
    assembled_path = folder / f"{FAMILY}_assembled.glb"
    export_glb(assembled_path, fixed)
    fixed_triangles = evaluated_triangle_count(fixed)
    fixed_materials = material_count(fixed)
    renders = (
        sorted(path.name for path in folder.glob(f"{FAMILY}_*.png"))
        if skip_renders
        else render_views(folder, view_set=view_set)
    )
    if skip_modules:
        print(
            f"[wave10] {FAMILY} assembled only: {fixed_triangles:,} tris, "
            f"{fixed_materials} materials, {len(renders)} renders",
            flush=True,
        )
        return
    delete_objects(fixed)
    role_specs = [
        ("podium", "default", FLOOR_HEIGHT),
        ("floor", "typical_a", FLOOR_HEIGHT),
        ("floor", "typical_b", FLOOR_HEIGHT),
        ("floor", "typical_c", FLOOR_HEIGHT),
        ("crown", "crown", CROWN_HEIGHT),
        ("roof", "default", ROOF_HEIGHT),
    ]
    modules: list[dict] = []
    for role, variant, module_height in role_specs:
        objects = build_module(role, variant, module_height, mats)
        objects.extend(module_contract_markers(role, variant, module_height))
        filename = (
            f"{FAMILY}_{role}.glb"
            if variant == "default"
            else f"{FAMILY}_{role}_{variant}.glb"
        )
        path = folder / filename
        export_glb(path, objects)
        modules.append(
            module_payload(
                role,
                variant,
                filename,
                module_height,
                objects,
                path.stat().st_size,
                skin,
            )
        )
        delete_objects(objects)
    write_metadata(
        folder,
        skin,
        modules,
        fixed_triangles,
        fixed_materials,
        assembled_path,
        renders,
    )
    print(
        f"[wave10] {FAMILY}: {fixed_triangles:,} tris, "
        f"{fixed_materials} materials, {len(modules)} modules, "
        f"{len(renders)} renders",
        flush=True,
    )


def render_existing(output_root: Path, *, view_set: str) -> None:
    clear_scene()
    folder = output_root / FAMILY
    manifest_path = folder / f"{FAMILY}_manifest.json"
    manifest = (
        json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest_path.is_file()
        else {
            "assembled": {"filename": f"{FAMILY}_assembled.glb"},
            "renders": [],
        }
    )
    bpy.ops.import_scene.gltf(
        filepath=str(folder / manifest["assembled"]["filename"])
    )
    manifest["renders"] = render_views(folder, view_set=view_set)
    if manifest_path.is_file():
        manifest_path.write_text(
            json.dumps(manifest, indent=2) + "\n",
            encoding="utf-8",
        )
    print(f"[wave10-render] {FAMILY}: {len(manifest['renders'])} renders")


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
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
