"""Author the Wave 10 French Third Republic school LEGO family.

The canonical building is a two-storey, forty-metre civic school.  Its fixed
entrance/crown/roof roles preserve the three public portals, clock pavilion,
slate hips and chimney groups, while repeatable classroom floors permit the
user's hand-drawn height to vary without stretching a window or material bay.

Run with Blender 5.x from the repository root:

    blender --background --factory-startup --python \
      tools/archetype_compiler/generate_wave10_school_family.py -- \
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
    beam,
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
)
from generate_wave10_courtyard_family import (  # noqa: E402
    arch_ring,
    arch_soffit,
    arch_spandrels,
    evaluated_triangle_count,
    material_count,
    mesh_object,
    segmental_arch_panel,
    tbox,
)


FAMILY = "ecole-republicaine-third-republic"
ARCHETYPE_ID = "ecole_republicaine"
VARIANT_ID = "ecole-republicaine-third-republic-original"
LABEL = "École Républicaine — Third Republic Original"
GLASS_PROFILE = "heritage_sash_occupied"

WIDTH = 40.0
DEPTH = 15.0
FLOOR_HEIGHT = 3.8
BODY_HEIGHT = FLOOR_HEIGHT * 2.0
CROWN_HEIGHT = 0.55
ROOF_HEIGHT = 6.85
TOTAL_HEIGHT = BODY_HEIGHT + CROWN_HEIGHT + ROOF_HEIGHT
WALL_THICKNESS = 0.30
FRONT_Y = -7.0
CENTRE_FRONT_Y = -7.22
REAR_Y = 7.0
STAIR_REAR_Y = 7.24

FRONT_GROUND_WINDOWS = (-16.2, -11.8, -8.0, 8.0, 11.8, 16.2)
FRONT_UPPER_WINDOWS = (-16.2, -11.8, -7.4, 0.0, 7.4, 11.8, 16.2)
FRONT_ENTRANCES = (-3.4, 0.0, 3.4)
REAR_CLASSROOM_WINDOWS = (-16.2, -11.8, -7.4, 7.4, 11.8, 16.2)
SIDE_WINDOWS = (-4.55, 0.0, 4.55)


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


def load_palette(folder: Path) -> tuple[dict[str, bpy.types.Material], dict]:
    skin = json.loads(
        (folder / "textures" / "skin_manifest.json").read_text(encoding="utf-8")
    )
    near = {zone: values["near"] for zone, values in skin["zones"].items()}
    mats: dict[str, bpy.types.Material] = {
        "brick": pbr_material(
            "MAT_W10_SCHOOL_AgedPressedRedBrick",
            folder,
            near["brick"],
            "brick",
            value=0.82,
            saturation=0.92,
        ),
        "limestone": pbr_material(
            "MAT_W10_SCHOOL_WarmCreamLimestone",
            folder,
            near["limestone"],
            "limestone",
            value=0.95,
            saturation=0.76,
        ),
        "meuliere": pbr_material(
            "MAT_W10_SCHOOL_RoughMeuliereBase",
            folder,
            near["meuliere"],
            "meuliere",
            value=0.86,
            saturation=0.78,
        ),
        "slate": pbr_material(
            "MAT_W10_SCHOOL_NaturalGreySlate",
            folder,
            near["slate"],
            "slate",
            value=0.62,
            saturation=0.56,
        ),
        "zinc": pbr_material(
            "MAT_W10_SCHOOL_AgedZinc",
            folder,
            near["zinc"],
            "zinc",
            metallic=0.70,
            value=0.62,
            saturation=0.42,
        ),
        "green": pbr_material(
            "MAT_W10_SCHOOL_DarkGreenPaintedTimber",
            folder,
            near["green_wood"],
            "green_wood",
            value=0.52,
            saturation=0.82,
        ),
        "paving": pbr_material(
            "MAT_W10_SCHOOL_PavedForecourt",
            folder,
            near["paving"],
            "paving",
            value=0.82,
            saturation=0.52,
        ),
        "facade": pbr_material(
            "MAT_W10_SCHOOL_RegisteredPublicElevation",
            folder,
            near["facade"],
            "facade",
            value=0.96,
            saturation=0.90,
        ),
        "glass": profiled_glass_material(
            "MAT_W10_SCHOOL_PhysicalHeritageLowE",
            GLASS_PROFILE,
            tint="#344344",
            roughness_scale=1.05,
            transmission_scale=0.76,
        ),
        "underlay": reference_image_material(
            "MAT_W10_SCHOOL_RegisteredOccupiedClassroomDepth",
            folder,
            skin["sources"]["reference_underlay"],
            emission_strength=0.070,
        ),
        "deep": material(
            "MAT_W10_SCHOOL_DeepMasonryCavity",
            (0.018, 0.020, 0.018, 1.0),
            0.96,
        ),
        "warm": material(
            "MAT_W10_SCHOOL_DimOccupiedClassroom",
            (0.16, 0.11, 0.065, 1.0),
            0.90,
            emission=(0.62, 0.32, 0.12, 1.0),
            emission_strength=0.11,
        ),
        "curtain": material(
            "MAT_W10_SCHOOL_PaleLinenCurtain",
            (0.64, 0.61, 0.55, 1.0),
            0.92,
        ),
        "clock": material(
            "MAT_W10_SCHOOL_ClockFace",
            (0.80, 0.78, 0.70, 1.0),
            0.58,
        ),
        "clock_ink": material(
            "MAT_W10_SCHOOL_ClockHandsAndTicks",
            (0.018, 0.019, 0.018, 1.0),
            0.42,
            metallic=0.16,
        ),
        "terracotta": material(
            "MAT_W10_SCHOOL_TerracottaChimneyPots",
            (0.39, 0.13, 0.075, 1.0),
            0.88,
        ),
    }
    for node in mats["underlay"].node_tree.nodes:
        if node.bl_idname == "ShaderNodeTexImage":
            node.extension = "REPEAT"
    mats["glass"]["glazing_lod"] = "always"
    mats["glass"]["reference_locked"] = True
    mats["glass"]["source_variant_id"] = VARIANT_ID
    mats["underlay"]["glazing_profile"] = GLASS_PROFILE
    mats["underlay"]["source_variant_id"] = VARIANT_ID
    return mats, skin


def add_y_wall(
    name: str,
    *,
    x0: float,
    x1: float,
    z0: float,
    z1: float,
    surface_y: float,
    outward_sign: int,
    openings: list[tuple[float, float, float, float]],
    mat: bpy.types.Material,
) -> list[bpy.types.Object]:
    inside = -outward_sign
    return [
        tbox(
            f"{name}_Wall_{index:02d}",
            (rx1 - rx0, WALL_THICKNESS, rz1 - rz0),
            (
                (rx0 + rx1) * 0.5,
                surface_y + inside * WALL_THICKNESS * 0.5,
                (rz0 + rz1) * 0.5,
            ),
            mat,
            0.012,
            tile_m=1.20,
        )
        for index, (rx0, rx1, rz0, rz1) in enumerate(
            rectangles_around_openings(x0, x1, z0, z1, openings)
        )
    ]


def add_x_wall(
    name: str,
    *,
    y0: float,
    y1: float,
    z0: float,
    z1: float,
    surface_x: float,
    outward_sign: int,
    openings: list[tuple[float, float, float, float]],
    mat: bpy.types.Material,
) -> list[bpy.types.Object]:
    inside = -outward_sign
    return [
        tbox(
            f"{name}_Wall_{index:02d}",
            (WALL_THICKNESS, ry1 - ry0, rz1 - rz0),
            (
                surface_x + inside * WALL_THICKNESS * 0.5,
                (ry0 + ry1) * 0.5,
                (rz0 + rz1) * 0.5,
            ),
            mat,
            0.012,
            tile_m=1.20,
        )
        for index, (ry0, ry1, rz0, rz1) in enumerate(
            rectangles_around_openings(y0, y1, z0, z1, openings)
        )
    ]


def add_y_arch_window(
    name: str,
    *,
    centre_x: float,
    sill_z: float,
    width: float,
    height: float,
    arch_rise: float,
    surface_y: float,
    outward_sign: int,
    mats: dict[str, bpy.types.Material],
    variant: str = "typical_a",
) -> list[bpy.types.Object]:
    """Build one deep segmental-arch classroom sash and masonry surround."""
    inside = -outward_sign
    x0, x1 = centre_x - width * 0.5, centre_x + width * 0.5
    z0, z1 = sill_z, sill_z + height
    spring = z1 - arch_rise
    reveal_y = surface_y + inside * 0.19
    pane_y = surface_y + inside * 0.34
    room_y = surface_y + inside * 0.50
    frame_y = pane_y - inside * 0.024
    objects: list[bpy.types.Object] = []
    objects.extend(
        arch_spandrels(
            f"{name}_BrickSpandrel",
            centre_x=centre_x,
            y=surface_y + inside * 0.004,
            sill_z=z0,
            width=width,
            height=height,
            arch_rise=arch_rise,
            mat=mats["brick"],
            segments=18,
        )
    )
    objects.extend(
        arch_soffit(
            f"{name}_LimestoneReveal",
            centre_x=centre_x,
            normal_centre=(surface_y + pane_y) * 0.5,
            normal_depth=abs(pane_y - surface_y) + 0.08,
            sill_z=z0,
            width=width,
            height=height,
            arch_rise=arch_rise,
            mat=mats["limestone"],
            segments=28,
        )
    )
    objects.extend(
        arch_ring(
            f"{name}_LimestoneSurround",
            centre_x=centre_x,
            y=surface_y + outward_sign * 0.055,
            sill_z=z0,
            width=width,
            height=height,
            arch_rise=arch_rise,
            band=0.21,
            mat=mats["limestone"],
            segments=28,
        )
    )
    objects.extend(
        [
            tbox(
                f"{name}_DeepRoomCard",
                (width - 0.24, 0.025, height - 0.28),
                (centre_x, room_y, (z0 + z1) * 0.5),
                mats["underlay"],
                0.003,
                tile_m=1.0,
            ),
            segmental_arch_panel(
                f"{name}_PhysicalLowEPane",
                centre_x=centre_x,
                y=pane_y,
                sill_z=z0 + 0.07,
                width=width - 0.20,
                height=height - 0.13,
                arch_rise=max(0.14, arch_rise - 0.08),
                mat=mats["glass"],
                segments=28,
            ),
            tbox(
                f"{name}_StoneSill",
                (width + 0.42, 0.44, 0.14),
                (
                    centre_x,
                    surface_y + outward_sign * 0.08,
                    z0 - 0.02,
                ),
                mats["limestone"],
                0.018,
                tile_m=0.82,
            ),
        ]
    )
    # Painted timber jambs and transoms sit in front of separate physical glass.
    for side in (-1, 1):
        objects.append(
            tbox(
                f"{name}_TimberJamb_{side:+d}",
                (0.082, 0.12, spring - z0 - 0.06),
                (
                    centre_x + side * (width * 0.5 - 0.10),
                    frame_y,
                    (z0 + spring) * 0.5,
                ),
                mats["green"],
                0.006,
                tile_m=0.55,
            )
        )
    objects.extend(
        arch_ring(
            f"{name}_CurvedTimberHead",
            centre_x=centre_x,
            y=frame_y,
            sill_z=z0 + 0.07,
            width=width - 0.20,
            height=height - 0.13,
            arch_rise=max(0.14, arch_rise - 0.08),
            band=0.065,
            mat=mats["green"],
            segments=24,
        )
    )
    for index in range(1, 3):
        mx = x0 + width * index / 3.0
        objects.append(
            tbox(
                f"{name}_Mullion_{index}",
                (0.060, 0.125, spring - z0 - 0.08),
                (mx, frame_y, (z0 + spring) * 0.5),
                mats["green"],
                0.005,
                tile_m=0.50,
            )
        )
    for index, z in enumerate(
        (z0 + (spring - z0) / 3.0, z0 + 2.0 * (spring - z0) / 3.0)
    ):
        objects.append(
            tbox(
                f"{name}_Transom_{index}",
                (width - 0.16, 0.125, 0.058),
                (centre_x, frame_y, z),
                mats["green"],
                0.005,
                tile_m=0.50,
            )
        )
    if (sum(ord(char) for char in name + variant) % 3) != 0:
        curtain_x = centre_x + (-0.54 if variant == "typical_b" else 0.54)
        objects.append(
            tbox(
                f"{name}_OffsetLinenCurtain",
                (0.48, 0.018, max(0.8, spring - z0 - 0.24)),
                (
                    curtain_x,
                    room_y - inside * 0.025,
                    (z0 + spring) * 0.5,
                ),
                mats["curtain"],
                0.002,
                tile_m=0.80,
            )
        )
    return objects


def add_x_arch_window(
    name: str,
    *,
    centre_y: float,
    sill_z: float,
    width: float,
    height: float,
    surface_x: float,
    outward_sign: int,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    """Side-elevation counterpart, rotated from the public window assembly."""
    temp = add_y_arch_window(
        name,
        centre_x=centre_y,
        sill_z=sill_z,
        width=width,
        height=height,
        arch_rise=0.40,
        surface_y=0.0,
        outward_sign=-outward_sign,
        mats=mats,
    )
    bpy.context.view_layer.update()
    # Keep the deep stone sill and arch ring proud of the side wall without
    # letting stack modules exceed the authored 40 m LEGO contract.  The
    # public Y-facing assembly has a 0.30 m sill projection; translate its
    # rotated side counterpart 0.10 m into the masonry return.
    registered_surface_x = surface_x - outward_sign * 0.10
    transform = (
        Matrix.Translation(Vector((registered_surface_x, 0.0, 0.0)))
        @ Matrix.Rotation(math.radians(90.0), 4, "Z")
    )
    for obj in temp:
        obj.matrix_world = transform @ obj.matrix_world
    return temp


def add_y_arch_entry(
    name: str,
    *,
    centre_x: float,
    surface_y: float,
    width: float,
    height: float,
    mats: dict[str, bpy.types.Material],
    central: bool = False,
) -> list[bpy.types.Object]:
    """Carve a traversable civic portal with inset timber doors and fanlight."""
    z0 = 0.12
    arch_rise = 0.72 if central else 0.64
    spring = z0 + height - arch_rise
    pane_y = surface_y + 0.48
    frame_y = surface_y + 0.41
    objects: list[bpy.types.Object] = []
    objects.extend(
        arch_spandrels(
            f"{name}_BrickSpandrel",
            centre_x=centre_x,
            y=surface_y + 0.004,
            sill_z=z0,
            width=width,
            height=height,
            arch_rise=arch_rise,
            mat=mats["brick"],
            segments=20,
        )
    )
    objects.extend(
        arch_soffit(
            f"{name}_DeepStonePortal",
            centre_x=centre_x,
            normal_centre=surface_y + 0.26,
            normal_depth=0.54,
            sill_z=z0,
            width=width,
            height=height,
            arch_rise=arch_rise,
            mat=mats["limestone"],
            segments=30,
        )
    )
    objects.extend(
        arch_ring(
            f"{name}_CarvedLimestoneArchivolt",
            centre_x=centre_x,
            y=surface_y - 0.075,
            sill_z=z0,
            width=width,
            height=height,
            arch_rise=arch_rise,
            band=0.28 if central else 0.23,
            mat=mats["limestone"],
            segments=30,
        )
    )
    door_height = spring - z0 - 0.08
    objects.extend(
        [
            tbox(
                f"{name}_ShadowedVestibule",
                (width - 0.18, 0.04, height - 0.18),
                (centre_x, surface_y + 0.58, z0 + height * 0.5),
                mats["deep"],
                0.004,
                tile_m=1.0,
            ),
            tbox(
                f"{name}_LeftTimberDoor",
                ((width - 0.20) * 0.5, 0.08, door_height),
                (
                    centre_x - (width - 0.20) * 0.25,
                    pane_y,
                    z0 + door_height * 0.5,
                ),
                mats["green"],
                0.018,
                tile_m=0.70,
            ),
            tbox(
                f"{name}_RightTimberDoor",
                ((width - 0.20) * 0.5, 0.08, door_height),
                (
                    centre_x + (width - 0.20) * 0.25,
                    pane_y,
                    z0 + door_height * 0.5,
                ),
                mats["green"],
                0.018,
                tile_m=0.70,
            ),
            segmental_arch_panel(
                f"{name}_FanlightGlass",
                centre_x=centre_x,
                y=frame_y,
                sill_z=spring - 0.04,
                width=width - 0.20,
                height=arch_rise,
                arch_rise=max(0.20, arch_rise - 0.08),
                mat=mats["glass"],
                segments=28,
            ),
            tbox(
                f"{name}_DoorTransom",
                (width - 0.12, 0.12, 0.075),
                (centre_x, frame_y, spring - 0.02),
                mats["green"],
                0.006,
                tile_m=0.52,
            ),
            tbox(
                f"{name}_CentreDoorStile",
                (0.075, 0.13, door_height),
                (centre_x, frame_y, z0 + door_height * 0.5),
                mats["green"],
                0.005,
                tile_m=0.52,
            ),
        ]
    )
    for panel_index, z in enumerate((z0 + 0.48, z0 + 1.18)):
        for side in (-1, 1):
            objects.append(
                tbox(
                    f"{name}_RaisedDoorPanel_{panel_index}_{side:+d}",
                    ((width - 0.40) * 0.42, 0.025, 0.34),
                    (
                        centre_x + side * width * 0.235,
                        pane_y - 0.052,
                        z,
                    ),
                    mats["green"],
                    0.015,
                    tile_m=0.52,
                )
            )
    step_width = width + (0.65 if central else 0.45)
    for index in range(3):
        objects.append(
            tbox(
                f"{name}_StoneStep_{index}",
                (step_width + index * 0.20, 0.30, 0.10),
                (
                    centre_x,
                    surface_y - 0.18 - index * 0.14,
                    0.05 + index * 0.10,
                ),
                mats["limestone"],
                0.015,
                tile_m=0.85,
            )
        )
    return objects


def add_text_relief(
    name: str,
    text: str,
    *,
    location: tuple[float, float, float],
    size: float,
    depth: float,
    mat: bpy.types.Material,
) -> bpy.types.Object:
    bpy.ops.object.text_add(location=location, rotation=(math.pi / 2.0, 0.0, 0.0))
    obj = bpy.context.object
    obj.name = name
    obj.data.body = text
    obj.data.align_x = "CENTER"
    obj.data.align_y = "CENTER"
    obj.data.size = size
    obj.data.extrude = depth
    obj.data.bevel_depth = min(0.006, depth * 0.25)
    obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    return obj


def add_y_surface_band(
    name: str,
    *,
    x0: float,
    x1: float,
    z0: float,
    z1: float,
    surface_y: float,
    outward_sign: int,
    openings: list[tuple[float, float, float, float]],
    mat: bpy.types.Material,
    depth: float = 0.07,
) -> list[bpy.types.Object]:
    return [
        tbox(
            f"{name}_{index:02d}",
            (rx1 - rx0, depth, rz1 - rz0),
            (
                (rx0 + rx1) * 0.5,
                surface_y + outward_sign * depth * 0.5,
                (rz0 + rz1) * 0.5,
            ),
            mat,
            0.008,
            tile_m=0.95,
        )
        for index, (rx0, rx1, rz0, rz1) in enumerate(
            rectangles_around_openings(x0, x1, z0, z1, openings)
        )
    ]


def add_x_surface_band(
    name: str,
    *,
    y0: float,
    y1: float,
    z0: float,
    z1: float,
    surface_x: float,
    outward_sign: int,
    openings: list[tuple[float, float, float, float]],
    mat: bpy.types.Material,
    depth: float = 0.07,
) -> list[bpy.types.Object]:
    return [
        tbox(
            f"{name}_{index:02d}",
            (depth, ry1 - ry0, rz1 - rz0),
            (
                surface_x + outward_sign * depth * 0.5,
                (ry0 + ry1) * 0.5,
                (rz0 + rz1) * 0.5,
            ),
            mat,
            0.008,
            tile_m=0.95,
        )
        for index, (ry0, ry1, rz0, rz1) in enumerate(
            rectangles_around_openings(y0, y1, z0, z1, openings)
        )
    ]


def front_surface_for_x(x: float) -> float:
    return CENTRE_FRONT_Y if abs(x) <= 5.45 else FRONT_Y


def add_front_pilasters(
    *,
    z0: float,
    z1: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    for pilaster_index, (x, surface) in enumerate(
        (
            (-19.82, FRONT_Y),
            (-5.47, CENTRE_FRONT_Y),
            (5.47, CENTRE_FRONT_Y),
            (19.82, FRONT_Y),
        )
    ):
        course = 0
        z = z0 + 0.04
        while z < z1 - 0.04:
            height = min(0.44, z1 - z)
            width = 0.58 if course % 2 == 0 else 0.46
            objects.append(
                tbox(
                    f"SchoolFrontQuoin_{pilaster_index}_{course:02d}",
                    (width, 0.13, height),
                    (x, surface - 0.075, z + height * 0.5),
                    mats["limestone"],
                    0.014,
                    tile_m=0.82,
                )
            )
            z += height + 0.035
            course += 1
    return objects


def add_rear_pilasters(
    *,
    z0: float,
    z1: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    for pilaster_index, (x, surface) in enumerate(
        (
            (-19.82, REAR_Y),
            (-3.05, STAIR_REAR_Y),
            (3.05, STAIR_REAR_Y),
            (19.82, REAR_Y),
        )
    ):
        course = 0
        z = z0 + 0.04
        while z < z1 - 0.04:
            height = min(0.44, z1 - z)
            width = 0.56 if course % 2 == 0 else 0.45
            objects.append(
                tbox(
                    f"SchoolRearQuoin_{pilaster_index}_{course:02d}",
                    (width, 0.13, height),
                    (x, surface + 0.075, z + height * 0.5),
                    mats["limestone"],
                    0.014,
                    tile_m=0.82,
                )
            )
            z += height + 0.035
            course += 1
    return objects


def add_side_corner_returns(
    *,
    z0: float,
    z1: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    for side_index, x in enumerate((-19.98, 19.98)):
        for end_index, y in enumerate((-6.74, 6.74)):
            course = 0
            z = z0 + 0.04
            while z < z1 - 0.04:
                height = min(0.44, z1 - z)
                length = 0.56 if course % 2 == 0 else 0.45
                objects.append(
                    tbox(
                        f"SchoolSideQuoin_{side_index}_{end_index}_{course:02d}",
                        (0.13, length, height),
                        (x, y, z + height * 0.5),
                        mats["limestone"],
                        0.014,
                        tile_m=0.82,
                    )
                )
                z += height + 0.035
                course += 1
    return objects


def add_simple_y_service_door(
    name: str,
    *,
    centre_x: float,
    surface_y: float,
    outward_sign: int,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    inside = -outward_sign
    width, height = 1.36, 2.44
    door_y = surface_y + inside * 0.42
    objects = [
        tbox(
            f"{name}_LeftReveal",
            (0.16, 0.48, height),
            (
                centre_x - width * 0.5 + 0.08,
                surface_y + inside * 0.22,
                0.18 + height * 0.5,
            ),
            mats["limestone"],
            0.012,
            tile_m=0.80,
        ),
        tbox(
            f"{name}_RightReveal",
            (0.16, 0.48, height),
            (
                centre_x + width * 0.5 - 0.08,
                surface_y + inside * 0.22,
                0.18 + height * 0.5,
            ),
            mats["limestone"],
            0.012,
            tile_m=0.80,
        ),
        tbox(
            f"{name}_HeadReveal",
            (width, 0.48, 0.16),
            (centre_x, surface_y + inside * 0.22, 0.18 + height - 0.08),
            mats["limestone"],
            0.012,
            tile_m=0.80,
        ),
        tbox(
            f"{name}_DarkGreenDoor",
            (width - 0.20, 0.07, height - 0.16),
            (centre_x, door_y, 0.18 + (height - 0.16) * 0.5),
            mats["green"],
            0.018,
            tile_m=0.70,
        ),
        tbox(
            f"{name}_ZincCanopy",
            (width + 0.78, 0.82, 0.10),
            (
                centre_x,
                surface_y + outward_sign * 0.34,
                2.84,
            ),
            mats["zinc"],
            0.018,
            tile_m=0.55,
        ),
    ]
    for side in (-1, 1):
        objects.append(
            beam(
                f"{name}_IronBracket_{side:+d}",
                (
                    centre_x + side * (width * 0.5 + 0.16),
                    surface_y + outward_sign * 0.05,
                    2.43,
                ),
                (
                    centre_x + side * (width * 0.5 + 0.16),
                    surface_y + outward_sign * 0.34,
                    2.79,
                ),
                0.025,
                mats["green"],
            )
        )
    return objects


def front_openings(role: str) -> list[tuple[float, float, float, float]]:
    if role == "podium":
        openings = [
            (x - 1.03, x + 1.03, 0.62, 3.31)
            for x in FRONT_GROUND_WINDOWS
        ]
        openings.extend(
            (
                x - (1.20 if abs(x) < 0.1 else 1.00),
                x + (1.20 if abs(x) < 0.1 else 1.00),
                0.10,
                3.42,
            )
            for x in FRONT_ENTRANCES
        )
        return openings
    return [
        (x - 1.03, x + 1.03, 0.55, 3.30)
        for x in FRONT_UPPER_WINDOWS
    ]


def rear_openings(role: str) -> list[tuple[float, float, float, float]]:
    if role == "podium":
        openings = [
            (x - 1.03, x + 1.03, 0.62, 3.31)
            for x in REAR_CLASSROOM_WINDOWS
        ]
        openings.extend(
            [
                (-4.88, -3.52, 0.16, 2.65),
                (3.52, 4.88, 0.16, 2.65),
                (-0.92, 0.92, 0.72, 2.38),
            ]
        )
        return openings
    openings = [
        (x - 1.03, x + 1.03, 0.55, 3.30)
        for x in REAR_CLASSROOM_WINDOWS
    ]
    openings.append((-1.05, 1.05, 0.38, 3.44))
    return openings


def side_openings(role: str) -> list[tuple[float, float, float, float]]:
    sill = 0.62 if role == "podium" else 0.55
    return [(y - 0.91, y + 0.91, sill, 3.30) for y in SIDE_WINDOWS]


def build_occupied_band(
    role: str,
    variant: str,
    mats: dict[str, bpy.types.Material],
    *,
    include_contract_markers: bool = True,
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    front_voids = front_openings(role)
    rear_voids = rear_openings(role)
    side_voids = side_openings(role)

    # Three front wall segments keep the central civic pavilion visibly proud.
    for segment_index, (x0, x1, surface) in enumerate(
        (
            (-20.0, -5.45, FRONT_Y),
            (-5.45, 5.45, CENTRE_FRONT_Y),
            (5.45, 20.0, FRONT_Y),
        )
    ):
        objects.extend(
            add_y_wall(
                f"School{role.title()}FrontSegment{segment_index}",
                x0=x0,
                x1=x1,
                z0=0.0,
                z1=FLOOR_HEIGHT,
                surface_y=surface,
                outward_sign=-1,
                openings=front_voids,
                mat=mats["brick"],
            )
        )
        if role == "podium":
            objects.extend(
                add_y_surface_band(
                    f"SchoolFrontMeuliere{segment_index}",
                    x0=x0,
                    x1=x1,
                    z0=0.0,
                    z1=0.92,
                    surface_y=surface,
                    outward_sign=-1,
                    openings=front_voids,
                    mat=mats["meuliere"],
                )
            )

    # Rear stair bay is a shallow integral projection, never a tacked-on box.
    for segment_index, (x0, x1, surface) in enumerate(
        (
            (-20.0, -3.05, REAR_Y),
            (-3.05, 3.05, STAIR_REAR_Y),
            (3.05, 20.0, REAR_Y),
        )
    ):
        objects.extend(
            add_y_wall(
                f"School{role.title()}RearSegment{segment_index}",
                x0=x0,
                x1=x1,
                z0=0.0,
                z1=FLOOR_HEIGHT,
                surface_y=surface,
                outward_sign=1,
                openings=rear_voids,
                mat=mats["brick"],
            )
        )
        if role == "podium":
            objects.extend(
                add_y_surface_band(
                    f"SchoolRearMeuliere{segment_index}",
                    x0=x0,
                    x1=x1,
                    z0=0.0,
                    z1=0.92,
                    surface_y=surface,
                    outward_sign=1,
                    openings=rear_voids,
                    mat=mats["meuliere"],
                )
            )

    for side_index, (surface_x, outward_sign) in enumerate(((-20.0, -1), (20.0, 1))):
        objects.extend(
            add_x_wall(
                f"School{role.title()}Side{side_index}",
                y0=-7.0,
                y1=7.0,
                z0=0.0,
                z1=FLOOR_HEIGHT,
                surface_x=surface_x,
                outward_sign=outward_sign,
                openings=side_voids,
                mat=mats["brick"],
            )
        )
        if role == "podium":
            objects.extend(
                add_x_surface_band(
                    f"SchoolSideMeuliere{side_index}",
                    y0=-7.0,
                    y1=7.0,
                    z0=0.0,
                    z1=0.92,
                    surface_x=surface_x,
                    outward_sign=outward_sign,
                    openings=side_voids,
                    mat=mats["meuliere"],
                )
            )

    front_windows = (
        FRONT_GROUND_WINDOWS if role == "podium" else FRONT_UPPER_WINDOWS
    )
    for index, x in enumerate(front_windows):
        objects.extend(
            add_y_arch_window(
                f"School{role.title()}FrontClassroom_{index:02d}",
                centre_x=x,
                sill_z=0.62 if role == "podium" else 0.55,
                width=2.06,
                height=2.69 if role == "podium" else 2.75,
                arch_rise=0.42,
                surface_y=front_surface_for_x(x),
                outward_sign=-1,
                mats=mats,
                variant=variant,
            )
        )
    if role == "podium":
        for index, x in enumerate(FRONT_ENTRANCES):
            objects.extend(
                add_y_arch_entry(
                    f"SchoolFrontCivicEntry_{index}",
                    centre_x=x,
                    surface_y=CENTRE_FRONT_Y,
                    width=2.40 if index == 1 else 2.00,
                    height=3.30,
                    mats=mats,
                    central=index == 1,
                )
            )
        # Blank relief panel plus deterministic mesh lettering supply the civic
        # hierarchy that ImageGen intentionally left free of malformed text.
        objects.extend(
            [
                tbox(
                    "SchoolCentralInscriptionPanel",
                    (5.35, 0.18, 0.38),
                    (0.0, CENTRE_FRONT_Y - 0.12, 3.55),
                    mats["limestone"],
                    0.025,
                    tile_m=0.82,
                ),
                add_text_relief(
                    "SchoolEcoleCommunaleRelief",
                    "ECOLE COMMUNALE",
                    location=(0.0, CENTRE_FRONT_Y - 0.225, 3.54),
                    size=0.245,
                    depth=0.018,
                    mat=mats["green"],
                ),
                add_text_relief(
                    "SchoolGarconsRelief",
                    "GARCONS",
                    location=(-3.4, CENTRE_FRONT_Y - 0.195, 3.30),
                    size=0.135,
                    depth=0.015,
                    mat=mats["green"],
                ),
                add_text_relief(
                    "SchoolFillesRelief",
                    "FILLES",
                    location=(3.4, CENTRE_FRONT_Y - 0.195, 3.30),
                    size=0.135,
                    depth=0.015,
                    mat=mats["green"],
                ),
            ]
        )

    rear_windows = REAR_CLASSROOM_WINDOWS
    for index, x in enumerate(rear_windows):
        objects.extend(
            add_y_arch_window(
                f"School{role.title()}RearClassroom_{index:02d}",
                centre_x=x,
                sill_z=0.62 if role == "podium" else 0.55,
                width=2.06,
                height=2.69 if role == "podium" else 2.75,
                arch_rise=0.42,
                surface_y=REAR_Y,
                outward_sign=1,
                mats=mats,
                variant=variant,
            )
        )
    if role == "podium":
        for index, x in enumerate((-4.2, 4.2)):
            objects.extend(
                add_simple_y_service_door(
                    f"SchoolRearServiceDoor_{index}",
                    centre_x=x,
                    surface_y=REAR_Y,
                    outward_sign=1,
                    mats=mats,
                )
            )
        objects.extend(
            add_y_arch_window(
                "SchoolGroundRearStairFanlight",
                centre_x=0.0,
                sill_z=0.72,
                width=1.84,
                height=1.66,
                arch_rise=0.28,
                surface_y=STAIR_REAR_Y,
                outward_sign=1,
                mats=mats,
                variant=variant,
            )
        )
    else:
        objects.extend(
            add_y_arch_window(
                "SchoolUpperRearStairWindow",
                centre_x=0.0,
                sill_z=0.38,
                width=2.10,
                height=3.06,
                arch_rise=0.40,
                surface_y=STAIR_REAR_Y,
                outward_sign=1,
                mats=mats,
                variant=variant,
            )
        )

    for side_index, (surface_x, outward_sign) in enumerate(((-20.0, -1), (20.0, 1))):
        for index, y in enumerate(SIDE_WINDOWS):
            objects.extend(
                add_x_arch_window(
                    f"School{role.title()}Side{side_index}Classroom_{index:02d}",
                    centre_y=y,
                    sill_z=0.62 if role == "podium" else 0.55,
                    width=1.82,
                    height=2.68 if role == "podium" else 2.75,
                    surface_x=surface_x,
                    outward_sign=outward_sign,
                    mats=mats,
                )
            )

    objects.extend(add_front_pilasters(z0=0.0, z1=FLOOR_HEIGHT, mats=mats))
    objects.extend(add_rear_pilasters(z0=0.0, z1=FLOOR_HEIGHT, mats=mats))
    objects.extend(add_side_corner_returns(z0=0.0, z1=FLOOR_HEIGHT, mats=mats))
    # Stone datums express construction and conceal LEGO stack seams.
    for y, outward_sign in (
        (FRONT_Y, -1),
        (CENTRE_FRONT_Y, -1),
        (REAR_Y, 1),
        (STAIR_REAR_Y, 1),
    ):
        width = 10.9 if abs(y) > 7.1 else WIDTH
        objects.append(
            tbox(
                f"School{role.title()}StoneDatum_{y:+.2f}",
                (width, 0.16, 0.18),
                (0.0, y + outward_sign * 0.08, FLOOR_HEIGHT - 0.13),
                mats["limestone"],
                0.018,
                tile_m=0.82,
            )
        )
    for x, outward_sign in ((-20.0, -1), (20.0, 1)):
        objects.append(
            tbox(
                f"School{role.title()}SideStoneDatum_{x:+.0f}",
                (0.16, 14.0, 0.18),
                (x + outward_sign * 0.08, 0.0, FLOOR_HEIGHT - 0.13),
                mats["limestone"],
                0.018,
                tile_m=0.82,
            )
        )
    for index, x in enumerate((-19.35, -4.82, 4.82, 19.35)):
        objects.extend(
            [
                beam(
                    f"School{role.title()}FrontDownpipe_{index}",
                    (x, -7.28, 0.10),
                    (x, -7.28, FLOOR_HEIGHT - 0.08),
                    0.060,
                    mats["zinc"],
                ),
                beam(
                    f"School{role.title()}RearDownpipe_{index}",
                    (x, 7.28, 0.10),
                    (x, 7.28, FLOOR_HEIGHT - 0.08),
                    0.060,
                    mats["zinc"],
                ),
            ]
        )

    if include_contract_markers:
        objects.extend(module_contract_markers(role, variant, FLOOR_HEIGHT))
    return objects


def build_crown(
    mats: dict[str, bpy.types.Material],
    *,
    include_contract_markers: bool = True,
) -> list[bpy.types.Object]:
    """Build the projecting brick corbel table, stone dentils and eaves."""
    objects: list[bpy.types.Object] = [
        tbox(
            "SchoolCrownBrickCore",
            (39.92, 14.0, CROWN_HEIGHT),
            (0.0, 0.0, CROWN_HEIGHT * 0.5),
            mats["brick"],
            0.014,
            tile_m=1.20,
        ),
        tbox(
            "SchoolFrontCrownStoneBand",
            (40.35, 0.22, 0.20),
            (0.0, -7.10, 0.16),
            mats["limestone"],
            0.020,
            tile_m=0.82,
        ),
        tbox(
            "SchoolRearCrownStoneBand",
            (40.35, 0.22, 0.20),
            (0.0, 7.10, 0.16),
            mats["limestone"],
            0.020,
            tile_m=0.82,
        ),
        tbox(
            "SchoolFrontProjectingEavesCourse",
            (40.40, 0.38, 0.16),
            (0.0, -7.18, 0.47),
            mats["limestone"],
            0.024,
            tile_m=0.82,
        ),
        tbox(
            "SchoolRearProjectingEavesCourse",
            (40.40, 0.38, 0.16),
            (0.0, 7.18, 0.47),
            mats["limestone"],
            0.024,
            tile_m=0.82,
        ),
    ]
    for side, x in enumerate((-20.07, 20.07)):
        objects.extend(
            [
                tbox(
                    f"SchoolSideCrownStoneBand_{side}",
                    (0.22, 14.0, 0.20),
                    (x, 0.0, 0.16),
                    mats["limestone"],
                    0.020,
                    tile_m=0.82,
                ),
                tbox(
                    f"SchoolSideProjectingEavesCourse_{side}",
                    (0.28, 14.35, 0.16),
                    (x, 0.0, 0.47),
                    mats["limestone"],
                    0.024,
                    tile_m=0.82,
                ),
            ]
        )
    for face_index, y in enumerate((-7.25, 7.25)):
        for index in range(40):
            x = -19.50 + index
            objects.append(
                tbox(
                    f"SchoolDentil_{face_index}_{index:02d}",
                    (0.34, 0.36, 0.20),
                    (x, y, 0.33),
                    mats["limestone"],
                    0.015,
                    tile_m=0.55,
                )
            )
    for side_index, x in enumerate((-20.08, 20.08)):
        for index in range(13):
            y = -6.50 + index
            objects.append(
                tbox(
                    f"SchoolSideDentil_{side_index}_{index:02d}",
                    (0.28, 0.34, 0.20),
                    (x, y, 0.33),
                    mats["limestone"],
                    0.015,
                    tile_m=0.55,
                )
            )
    for index, x in enumerate((-19.35, -4.82, 4.82, 19.35)):
        objects.extend(
            [
                beam(
                    f"SchoolCrownFrontDownpipe_{index}",
                    (x, -7.28, 0.02),
                    (x, -7.28, CROWN_HEIGHT - 0.02),
                    0.060,
                    mats["zinc"],
                ),
                beam(
                    f"SchoolCrownRearDownpipe_{index}",
                    (x, 7.28, 0.02),
                    (x, 7.28, CROWN_HEIGHT - 0.02),
                    0.060,
                    mats["zinc"],
                ),
            ]
        )
    if include_contract_markers:
        objects.extend(module_contract_markers("crown", "crown", CROWN_HEIGHT))
    return objects


def hipped_roof_mesh(
    name: str,
    *,
    width: float,
    depth: float,
    eave_z: float,
    ridge_z: float,
    ridge_length: float,
    mat: bpy.types.Material,
) -> bpy.types.Object:
    half_w, half_d = width * 0.5, depth * 0.5
    half_ridge = ridge_length * 0.5
    vertices = [
        (-half_w, -half_d, eave_z),
        (half_w, -half_d, eave_z),
        (half_w, half_d, eave_z),
        (-half_w, half_d, eave_z),
        (-half_ridge, -0.10, ridge_z),
        (half_ridge, -0.10, ridge_z),
        (half_ridge, 0.10, ridge_z),
        (-half_ridge, 0.10, ridge_z),
    ]
    faces = [
        (0, 1, 5, 4),
        (1, 2, 6, 5),
        (2, 3, 7, 6),
        (3, 0, 4, 7),
        (4, 5, 6, 7),
    ]
    return mesh_object(name, vertices, faces, mat, uv_scale=10.0)


def truncated_pyramid(
    name: str,
    *,
    lower_size: tuple[float, float],
    upper_size: tuple[float, float],
    z0: float,
    z1: float,
    mat: bpy.types.Material,
) -> bpy.types.Object:
    lx, ly = lower_size[0] * 0.5, lower_size[1] * 0.5
    ux, uy = upper_size[0] * 0.5, upper_size[1] * 0.5
    vertices = [
        (-lx, -ly, z0),
        (lx, -ly, z0),
        (lx, ly, z0),
        (-lx, ly, z0),
        (-ux, -uy, z1),
        (ux, -uy, z1),
        (ux, uy, z1),
        (-ux, uy, z1),
    ]
    faces = [
        (0, 1, 5, 4),
        (1, 2, 6, 5),
        (2, 3, 7, 6),
        (3, 0, 4, 7),
        (4, 5, 6, 7),
    ]
    return mesh_object(name, vertices, faces, mat, uv_scale=4.0)


def central_roof_pediment(
    name: str,
    *,
    y: float,
    mat: bpy.types.Material,
) -> bpy.types.Object:
    """Stepped civic shoulder that visually grows the clock through the roof."""
    vertices = [
        (-3.25, y, 1.78),
        (-3.25, y, 2.18),
        (-2.55, y, 2.18),
        (-1.90, y, 2.78),
        (1.90, y, 2.78),
        (2.55, y, 2.18),
        (3.25, y, 2.18),
        (3.25, y, 1.78),
    ]
    return mesh_object(name, vertices, [tuple(range(8))], mat, uv_scale=2.0)


def add_dormer(
    name: str,
    *,
    x: float,
    y: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects = [
        tbox(
            f"{name}_SlateCheek",
            (1.30, 0.78, 1.12),
            (x, y, 1.52),
            mats["slate"],
            0.025,
            tile_m=0.58,
        ),
        tbox(
            f"{name}_PhysicalGlass",
            (0.70, 0.035, 0.65),
            (x, y - 0.405, 1.52),
            mats["glass"],
            0.008,
            tile_m=0.55,
        ),
        tbox(
            f"{name}_GreenFrameLeft",
            (0.07, 0.09, 0.72),
            (x - 0.37, y - 0.435, 1.52),
            mats["green"],
            0.008,
            tile_m=0.50,
        ),
        tbox(
            f"{name}_GreenFrameRight",
            (0.07, 0.09, 0.72),
            (x + 0.37, y - 0.435, 1.52),
            mats["green"],
            0.008,
            tile_m=0.50,
        ),
        tbox(
            f"{name}_GreenFrameHead",
            (0.81, 0.09, 0.07),
            (x, y - 0.435, 1.88),
            mats["green"],
            0.008,
            tile_m=0.50,
        ),
        tbox(
            f"{name}_GreenFrameSill",
            (0.81, 0.09, 0.07),
            (x, y - 0.435, 1.16),
            mats["green"],
            0.008,
            tile_m=0.50,
        ),
        tbox(
            f"{name}_CentreMullion",
            (0.055, 0.09, 0.65),
            (x, y - 0.44, 1.52),
            mats["green"],
            0.006,
            tile_m=0.50,
        ),
    ]
    roof = truncated_pyramid(
        f"{name}_ZincHippedCap",
        lower_size=(1.64, 1.16),
        upper_size=(0.12, 0.12),
        z0=2.08,
        z1=2.70,
        mat=mats["slate"],
    )
    roof.location.x = x
    roof.location.y = y
    objects.append(roof)
    objects.append(
        tbox(
            f"{name}_ZincSill",
            (1.02, 0.14, 0.08),
            (x, y - 0.48, 1.10),
            mats["zinc"],
            0.012,
            tile_m=0.50,
        )
    )
    return objects


def add_chimney_pair(
    name: str,
    *,
    x: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    for index, y in enumerate((-1.18, 1.18)):
        objects.extend(
            [
                tbox(
                    f"{name}_BrickStack_{index}",
                    (0.80, 0.74, 2.75),
                    (x, y, 2.70),
                    mats["brick"],
                    0.025,
                    tile_m=0.72,
                ),
                tbox(
                    f"{name}_CorbelBandLower_{index}",
                    (0.94, 0.88, 0.16),
                    (x, y, 3.80),
                    mats["brick"],
                    0.020,
                    tile_m=0.72,
                ),
                tbox(
                    f"{name}_CorbelBandUpper_{index}",
                    (1.04, 0.98, 0.16),
                    (x, y, 4.02),
                    mats["brick"],
                    0.020,
                    tile_m=0.72,
                ),
                cylinder(
                    f"{name}_TerracottaPot_{index}",
                    0.18,
                    0.48,
                    (x, y, 4.34),
                    mats["terracotta"],
                    vertices=20,
                ),
            ]
        )
    return objects


def add_clock_face(
    name: str,
    *,
    y: float,
    outward_sign: int,
    z: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    disc = cylinder(
        f"{name}_CreamClockFace",
        0.88,
        0.08,
        (0.0, y, z),
        mats["clock"],
        vertices=64,
    )
    disc.rotation_euler = (math.pi / 2.0, 0.0, 0.0)
    objects.append(disc)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.94,
        minor_radius=0.085,
        major_segments=48,
        minor_segments=10,
        location=(0.0, y + outward_sign * 0.055, z),
        rotation=(math.pi / 2.0, 0.0, 0.0),
    )
    ring = bpy.context.object
    ring.name = f"{name}_CarvedStoneClockRing"
    ring.data.materials.append(mats["limestone"])
    objects.append(ring)
    for index in range(12):
        theta = math.radians(index * 30.0)
        x = math.sin(theta) * 0.68
        tick_z = z + math.cos(theta) * 0.68
        tick = tbox(
            f"{name}_ClockTick_{index:02d}",
            (0.045, 0.05, 0.17 if index % 3 == 0 else 0.12),
            (x, y + outward_sign * 0.105, tick_z),
            mats["clock_ink"],
            0.004,
            tile_m=0.40,
        )
        tick.rotation_euler[1] = theta
        objects.append(tick)
    objects.extend(
        [
            beam(
                f"{name}_MinuteHand",
                (0.0, y + outward_sign * 0.13, z),
                (0.0, y + outward_sign * 0.13, z + 0.54),
                0.038,
                mats["clock_ink"],
            ),
            beam(
                f"{name}_HourHand",
                (0.0, y + outward_sign * 0.135, z),
                (-0.38, y + outward_sign * 0.135, z + 0.17),
                0.048,
                mats["clock_ink"],
            ),
            cylinder(
                f"{name}_ClockHub",
                0.09,
                0.10,
                (0.0, y + outward_sign * 0.16, z),
                mats["clock_ink"],
                vertices=24,
            ),
        ]
    )
    objects[-1].rotation_euler = (math.pi / 2.0, 0.0, 0.0)
    return objects


def build_roof(
    mats: dict[str, bpy.types.Material],
    *,
    include_contract_markers: bool = True,
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = [
        hipped_roof_mesh(
            "SchoolLongNaturalSlateHipRoof",
            width=40.70,
            depth=14.86,
            eave_z=0.12,
            ridge_z=2.88,
            ridge_length=25.30,
            mat=mats["slate"],
        )
    ]
    # Zinc ridge, hips, gutters and downpipes make the roof legible as assembly.
    objects.extend(
        [
            beam(
                "SchoolZincMainRidge",
                (-12.65, 0.0, 2.93),
                (12.65, 0.0, 2.93),
                0.065,
                mats["zinc"],
            ),
            beam(
                "SchoolZincFrontLeftHip",
                (-20.30, -7.37, 0.17),
                (-12.65, 0.0, 2.93),
                0.055,
                mats["zinc"],
            ),
            beam(
                "SchoolZincFrontRightHip",
                (20.30, -7.37, 0.17),
                (12.65, 0.0, 2.93),
                0.055,
                mats["zinc"],
            ),
            beam(
                "SchoolZincRearLeftHip",
                (-20.30, 7.37, 0.17),
                (-12.65, 0.0, 2.93),
                0.055,
                mats["zinc"],
            ),
            beam(
                "SchoolZincRearRightHip",
                (20.30, 7.37, 0.17),
                (12.65, 0.0, 2.93),
                0.055,
                mats["zinc"],
            ),
            beam(
                "SchoolFrontHalfRoundZincGutter",
                (-20.28, -7.45, 0.10),
                (20.28, -7.45, 0.10),
                0.075,
                mats["zinc"],
            ),
            beam(
                "SchoolRearHalfRoundZincGutter",
                (-20.28, 7.45, 0.10),
                (20.28, 7.45, 0.10),
                0.075,
                mats["zinc"],
            ),
        ]
    )
    for index, x in enumerate((-19.35, -4.82, 4.82, 19.35)):
        objects.extend(
            [
                beam(
                    f"SchoolFrontDownpipe_{index}",
                    (x, -7.28, 0.10),
                    (x, -7.28, 0.00),
                    0.060,
                    mats["zinc"],
                ),
                beam(
                    f"SchoolRearDownpipe_{index}",
                    (x, 7.28, 0.10),
                    (x, 7.28, 0.00),
                    0.060,
                    mats["zinc"],
                ),
            ]
        )

    for index, x in enumerate((-12.0, -6.2, 6.2, 12.0)):
        objects.extend(
            add_dormer(
                f"SchoolFrontZincDormer_{index}",
                x=x,
                y=-4.95,
                mats=mats,
            )
        )
    objects.extend(add_chimney_pair("SchoolLeftChimneys", x=-15.75, mats=mats))
    objects.extend(add_chimney_pair("SchoolRightChimneys", x=15.75, mats=mats))

    # The clock pavilion is integral with the central masonry and rises through
    # the slate roof; stone shoulders hide every roof/pavilion junction.
    objects.extend(
        [
            tbox(
                "SchoolCentralRoofPavilionBrickCore",
                (6.20, 4.70, 2.78),
                (0.0, 0.0, 1.44),
                mats["brick"],
                0.035,
                tile_m=1.20,
            ),
            tbox(
                "SchoolCentralPavilionFrontStoneShoulder",
                (6.58, 0.30, 0.40),
                (0.0, -2.44, 2.40),
                mats["limestone"],
                0.035,
                tile_m=0.82,
            ),
            tbox(
                "SchoolCentralPavilionRearStoneShoulder",
                (6.58, 0.30, 0.40),
                (0.0, 2.44, 2.40),
                mats["limestone"],
                0.035,
                tile_m=0.82,
            ),
            central_roof_pediment(
                "SchoolCentralFrontSteppedStonePediment",
                y=-2.50,
                mat=mats["limestone"],
            ),
            central_roof_pediment(
                "SchoolCentralRearSteppedStonePediment",
                y=2.50,
                mat=mats["limestone"],
            ),
            tbox(
                "SchoolCentralFrontPedimentBrickInfill",
                (3.60, 0.08, 0.54),
                (0.0, -2.545, 2.27),
                mats["brick"],
                0.015,
                tile_m=1.05,
            ),
            tbox(
                "SchoolCentralRearPedimentBrickInfill",
                (3.60, 0.08, 0.54),
                (0.0, 2.545, 2.27),
                mats["brick"],
                0.015,
                tile_m=1.05,
            ),
            tbox(
                "SchoolClockChamberSlateCore",
                (3.75, 3.55, 2.25),
                (0.0, 0.0, 3.78),
                mats["slate"],
                0.025,
                tile_m=0.70,
            ),
            tbox(
                "SchoolClockChamberLowerStoneCourse",
                (4.14, 3.94, 0.22),
                (0.0, 0.0, 2.67),
                mats["limestone"],
                0.025,
                tile_m=0.82,
            ),
            tbox(
                "SchoolClockChamberUpperStoneCornice",
                (4.34, 4.14, 0.24),
                (0.0, 0.0, 4.91),
                mats["limestone"],
                0.028,
                tile_m=0.82,
            ),
        ]
    )
    for face_name, y in (("Front", -2.68), ("Rear", 2.68)):
        objects.extend(
            [
                beam(
                    f"SchoolCentral{face_name}LeftPedimentSlope",
                    (-3.05, y, 2.02),
                    (-1.82, y, 2.92),
                    0.13,
                    mats["limestone"],
                ),
                beam(
                    f"SchoolCentral{face_name}RightPedimentSlope",
                    (3.05, y, 2.02),
                    (1.82, y, 2.92),
                    0.13,
                    mats["limestone"],
                ),
                tbox(
                    f"SchoolCentral{face_name}PedimentBaseCourse",
                    (6.35, 0.18, 0.18),
                    (0.0, y, 1.96),
                    mats["limestone"],
                    0.020,
                    tile_m=0.82,
                ),
            ]
        )
    for side_index, x in enumerate((-1.78, 1.78)):
        objects.append(
            tbox(
                f"SchoolClockFrontStonePilaster_{side_index}",
                (0.25, 0.25, 2.18),
                (x, -1.80, 3.78),
                mats["limestone"],
                0.020,
                tile_m=0.82,
            )
        )
        objects.append(
            tbox(
                f"SchoolClockRearStonePilaster_{side_index}",
                (0.25, 0.25, 2.18),
                (x, 1.80, 3.78),
                mats["limestone"],
                0.020,
                tile_m=0.82,
            )
        )
    objects.extend(
        add_clock_face(
            "SchoolFrontClock",
            y=-1.83,
            outward_sign=-1,
            z=3.86,
            mats=mats,
        )
    )
    objects.extend(
        add_clock_face(
            "SchoolRearClock",
            y=1.83,
            outward_sign=1,
            z=3.86,
            mats=mats,
        )
    )
    objects.append(
        truncated_pyramid(
            "SchoolClockPavilionSlateCap",
            lower_size=(4.42, 4.22),
            upper_size=(0.22, 0.22),
            z0=4.95,
            z1=6.45,
            mat=mats["slate"],
        )
    )
    for start, end, suffix in (
        ((-2.16, -2.06, 4.98), (0.0, 0.0, 6.49), "FrontLeft"),
        ((2.16, -2.06, 4.98), (0.0, 0.0, 6.49), "FrontRight"),
        ((-2.16, 2.06, 4.98), (0.0, 0.0, 6.49), "RearLeft"),
        ((2.16, 2.06, 4.98), (0.0, 0.0, 6.49), "RearRight"),
    ):
        objects.append(
            beam(
                f"SchoolClockCapZincHip_{suffix}",
                start,
                end,
                0.040,
                mats["zinc"],
            )
        )
    objects.extend(
        [
            cylinder(
                "SchoolClockFinialBase",
                0.12,
                0.26,
                (0.0, 0.0, 6.60),
                mats["zinc"],
                vertices=20,
            ),
            beam(
                "SchoolClockFinialSpire",
                (0.0, 0.0, 6.70),
                (0.0, 0.0, 6.85),
                0.035,
                mats["zinc"],
            ),
        ]
    )
    if include_contract_markers:
        objects.extend(module_contract_markers("roof", "default", ROOF_HEIGHT))
    return objects


def build_band(
    role: str,
    variant: str,
    mats: dict[str, bpy.types.Material],
    *,
    include_contract_markers: bool = True,
) -> list[bpy.types.Object]:
    if role in {"podium", "floor"}:
        return build_occupied_band(
            role,
            variant,
            mats,
            include_contract_markers=include_contract_markers,
        )
    if role == "crown":
        return build_crown(
            mats,
            include_contract_markers=include_contract_markers,
        )
    if role == "roof":
        return build_roof(
            mats,
            include_contract_markers=include_contract_markers,
        )
    raise ValueError(f"unsupported role {role}")


def translate_z(objects: list[bpy.types.Object], amount: float) -> None:
    for obj in objects:
        obj.location.z += amount


def build_assembled(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    stack = (
        ("podium", "default", 0.0),
        ("floor", "typical_a", FLOOR_HEIGHT),
        ("crown", "crown", BODY_HEIGHT),
        ("roof", "default", BODY_HEIGHT + CROWN_HEIGHT),
    )
    for role, variant, z in stack:
        band = build_band(
            role,
            variant,
            mats,
            include_contract_markers=False,
        )
        translate_z(band, z)
        objects.extend(band)
    return objects


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
        "depth_m": DEPTH,
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
    specs = (
        ("podium", "default", FLOOR_HEIGHT),
        ("floor", "typical_a", FLOOR_HEIGHT),
        ("floor", "typical_b", FLOOR_HEIGHT),
        ("floor", "typical_c", FLOOR_HEIGHT),
        ("crown", "crown", CROWN_HEIGHT),
        ("roof", "default", ROOF_HEIGHT),
    )
    modules: list[dict] = []
    for role, variant, height in specs:
        objects = build_band(role, variant, mats)
        suffix = role if variant == "default" else f"{role}_{variant}"
        filename = f"{FAMILY}_{suffix}.glb"
        output = folder / filename
        export_glb(output, objects)
        modules.append(
            module_payload(
                role,
                variant,
                filename,
                height,
                objects,
                output.stat().st_size,
                skin,
            )
        )
        delete_objects(objects)
    return modules


def render_views(folder: Path, *, view_set: str) -> list[str]:
    setup_render()
    scene = bpy.context.scene
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 950
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.exposure = 0.50
    background = scene.world.node_tree.nodes.get("Background")
    if background:
        background.inputs["Color"].default_value = (0.46, 0.47, 0.47, 1.0)
        background.inputs["Strength"].default_value = 0.92
    ground = bpy.data.materials.get("MAT_W3_Ground")
    if ground and ground.use_nodes:
        ground.node_tree.nodes["Principled BSDF"].inputs[
            "Base Color"
        ].default_value = (0.42, 0.41, 0.38, 1.0)
    bpy.ops.object.light_add(type="SUN", location=(-50.0, -70.0, 90.0))
    sun = bpy.context.object
    sun.name = "PRESENTATION_W10_SchoolSoftSun"
    sun.data.energy = 1.60
    sun.data.color = (1.0, 0.88, 0.75)
    sun.data.angle = math.radians(13.0)
    sun.rotation_euler = (
        Vector((0.0, 0.0, 6.0)) - sun.location
    ).to_track_quat("-Z", "Y").to_euler()
    views = {
        "preview": ((38.0, -59.0, 23.0), (0.0, -0.6, 7.0), 56),
        "street": ((0.0, -70.0, 7.5), (0.0, -6.6, 6.6), 57),
        "front_corner_oblique": ((-45.0, -57.0, 22.0), (0.0, 0.0, 6.8), 54),
        "rear_corner_oblique": ((39.0, 45.0, 20.0), (0.0, 0.5, 6.6), 53),
        "aerial": ((40.0, -44.0, 43.0), (0.0, 0.0, 5.5), 55),
        "facade_close": ((0.0, -64.0, 7.2), (0.0, -6.8, 6.6), 62),
        "identity_close": ((-1.0, -31.0, 11.0), (0.0, -2.5, 8.3), 60),
        "roof_close": ((20.0, -24.0, 29.0), (0.0, 0.0, 10.3), 57),
        "side_close": ((48.0, 0.0, 8.5), (19.0, 0.0, 6.0), 58),
        "context": ((43.0, -54.0, 26.0), (0.0, 0.0, 6.5), 58),
    }
    selected = (
        {
            "preview",
            "street",
            "front_corner_oblique",
            "aerial",
            "facade_close",
            "roof_close",
        }
        if view_set == "pilot"
        else set(views)
    )
    snapshots: list[tuple[bpy.types.Material, bpy.types.Node, float, float, str, tuple]] = []
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
        bsdf.inputs["Base Color"].default_value = (0.018, 0.032, 0.034, 1.0)
        bsdf.inputs["Alpha"].default_value = 0.78
        mat.diffuse_color = (0.018, 0.032, 0.034, 0.78)
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
        for mat, bsdf, alpha, transmission_value, method, colour in snapshots:
            bsdf.inputs["Base Color"].default_value = colour
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


def footprint_compatibility() -> dict:
    return {
        "preferredProfiles": ["rectangle", "l_shape", "u_shape"],
        "minimumPreferredProfiles": 3,
        "profileRationale": (
            "The identity is a shallow civic classroom bar with one fixed "
            "entrance pavilion. Rectangle preserves the canonical school; L- "
            "and U-shaped user drawings turn complete classroom bars around "
            "schoolyards while the primary bar keeps its three entrances, "
            "clock centre and unscaled arched-window bays."
        ),
        "fixedLandmarkScaleBand": {
            "scaleMin": 0.75,
            "scaleMax": 1.32,
            "maxAxisRatio": 1.35,
        },
        "recommendedWidth_m": [30, 60],
        "recommendedDepth_m": [12, 20],
        "recommendedFloors": [2, 3],
        "wingDepth_m": [10, 20],
        "preferredBayMultiple_m": 4.4,
        "profiles": {
            "rectangle": {
                "recommendedWidth_m": [30, 60],
                "recommendedDepth_m": [12, 20],
                "recommendedFloors": [2, 3],
            },
            "l_shape": {
                "recommendedWidth_m": [32, 64],
                "recommendedDepth_m": [18, 42],
                "recommendedFloors": [2, 3],
                "wingDepth_m": [10, 20],
            },
            "u_shape": {
                "recommendedWidth_m": [34, 70],
                "recommendedDepth_m": [22, 46],
                "recommendedFloors": [2, 3],
                "wingDepth_m": [10, 20],
                "minimumCourtyard_m": 10.0,
            },
        },
        "notes": [
            "Keep the three arched civic entrances and inscription on one primary bar.",
            "Keep the clock pavilion, slate roof, dormers and chimneys as the fixed roof role.",
            "Repeat complete 4.4 metre classroom bays; never stretch an arch or sash.",
            "Use family-shaped streetwall repeat for oversized targets.",
        ],
    }


def provenance() -> dict:
    return {
        "kind": (
            "catalogue_brief_plus_authoritative_heritage_research_and_"
            "imagegen_multiview_reference_locked_authored_construction"
        ),
        "catalogue_archetype_id": ARCHETYPE_ID,
        "catalogue_variant_id": VARIANT_ID,
        "goalpost": f"/families/{FAMILY}/textures/source/archetype-goalpost.png",
        "goalpost_local_source": "textures/source/archetype-goalpost.png",
        "orthographic_elevation": "textures/source/elevation-source-v1.png",
        "aerial_reference": "textures/source/aerial-source-v1.png",
        "rear_reference": "textures/source/rear-elevation-source-v1.png",
        "reference_underlay": "textures/source/occupied-depth-source-v1.png",
        "material_source": "textures/source/masonry-material-source-v1.png",
        "detail_source": "textures/source/clock-cornice-detail-source-v1.png",
        "reference_generation": "textures/source/reference-generation.json",
        "registered_openings": "textures/source/registered-openings.json",
        "registered_bands": "textures/source/registered-bands.json",
        "elevation_source": f"/families/{FAMILY}/elevation.jpg",
        "skin_manifest": "textures/skin_manifest.json",
        "generator": "tools/archetype_compiler/generate_wave10_school_family.py",
        "reference_method": (
            "catalogue identity brief, authoritative French heritage precedents, "
            "canonical street goalpost, rectified front and rear elevations, "
            "aerial roof proof, material/detail sources, physical opening "
            "cavities, custom true-scale PBR, occupied-depth underlay and finite "
            "street/oblique/aerial/detail comparison"
        ),
    }


def facade_contract(skin: dict) -> dict:
    return {
        "schema": "facade-sheet@5",
        "source_directory": f"/families/{FAMILY}",
        "model": "gpt-image-2",
        "style_reference": "elevation.jpg",
        "goalpost_reference": (
            f"/families/{FAMILY}/textures/source/archetype-goalpost.png"
        ),
        "goalpost_policy": (
            "The authored multi-view package fixes a two-storey symmetrical "
            "Jules Ferry-era school, its brick/limestone polychromy, three "
            "recessed entrances, tall classroom sashes, slate hips, clock "
            "pavilion, dormers, chimneys and rear stair/service composition."
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
            "fixed_end_bays": [0, 8],
            "repeatable_middle_bays": [1, 2, 3, 4, 5, 6, 7],
            "middle_variants": ["typical_a", "typical_b", "typical_c"],
            "rule": (
                "Repeat complete classroom bays. Keep the three public portals, "
                "central pavilion, corner returns, crown, clock and slate roof "
                "semantic and unscaled."
            ),
        },
        "delivery": {
            "near_atlas_width_px": 2048,
            "far_atlas_width_px": 1024,
            "near_usage": (
                "true-scale brick, limestone, meuliere and slate plus physical "
                "arched openings, heritage sashes, low-e glass, occupied depth, "
                "zinc drainage, dormers, clock, chimneys and carved civic entry"
            ),
            "far_usage": "city-scale render-locked archetype material reference",
        },
        "assembly_contract": {
            "fixed": [
                "podium/entrance",
                "corner returns",
                "crown",
                "roof",
                "three recessed civic portals",
                "ECOLE COMMUNALE inscription panel",
                "central clock pavilion",
                "slate hipped roof",
                "four zinc dormers",
                "four chimney stacks",
                "rear stair pavilion",
            ],
            "repeatable": ["typical_a", "typical_b", "typical_c"],
            "side_elevations": (
                "Meuliere base, red brick, stone strings, corner quoins, arched "
                "occupied classroom sashes, eaves and drainage wrap all returns."
            ),
            "elevation_coverage": {
                "front": "three portals, civic inscription, classroom arches and projecting centre",
                "left": "three occupied classroom bays and wrapped quoins",
                "right": "three occupied classroom bays and wrapped quoins",
                "rear": "integral stair pavilion, classroom rhythm and two zinc canopies",
                "roof": "slate hips, zinc seams, four dormers, four stacks and clock cap",
            },
            "variation_policy": (
                "Mild full-envelope scaling is safe. Larger targets place "
                "multiple complete classroom bars with the planner's streetwall "
                "repeat instead of stretching portals, sashes or the clock."
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
            "role": "crown",
            "variant_key": "crown",
            "level": 2,
            "z_m": BODY_HEIGHT,
            "height_m": CROWN_HEIGHT,
        },
        {
            "role": "roof",
            "variant_key": "default",
            "level": 3,
            "z_m": BODY_HEIGHT + CROWN_HEIGHT,
            "height_m": ROOF_HEIGHT,
        },
    ]
    assembled = {
        "filename": assembled_path.name,
        "floors": 2,
        "uses_setback": False,
        "uses_crown": True,
        "height_m": TOTAL_HEIGHT,
        "triangle_count": fixed_triangles,
        "material_count": fixed_materials,
        "stack": stack,
        "footprint_profile": "rectangle",
        "footprint_target": {
            "width_m": WIDTH,
            "depth_m": DEPTH,
            "wing_depth_m": DEPTH,
            "segments": [
                {
                    "id": "left_classroom_wing",
                    "centre_x_m": -12.725,
                    "centre_y_m": 0.0,
                    "length_m": 14.55,
                    "thickness_m": DEPTH,
                    "rotation_degrees": 0.0,
                },
                {
                    "id": "central_civic_pavilion",
                    "centre_x_m": 0.0,
                    "centre_y_m": -0.11,
                    "length_m": 10.90,
                    "thickness_m": 14.46,
                    "rotation_degrees": 0.0,
                },
                {
                    "id": "right_classroom_wing",
                    "centre_x_m": 12.725,
                    "centre_y_m": 0.0,
                    "length_m": 14.55,
                    "thickness_m": DEPTH,
                    "rotation_degrees": 0.0,
                },
            ],
        },
        "massing_graph": {
            "type": "symmetrical_third_republic_school_bar",
            "classroom_wings": 2,
            "public_entrances": 3,
            "central_pavilion_width_m": 10.9,
            "rear_stair_projection_m": 0.24,
            "clock_pavilion": True,
            "hipped_roof": True,
        },
        "texture_keys": sorted(skin["zones"]),
        "ao_baked": True,
    }
    dimensions = {
        "width_m": WIDTH,
        "depth_m": DEPTH,
        "wing_depth_m": DEPTH,
        "podium_height_m": FLOOR_HEIGHT,
        "floor_height_m": FLOOR_HEIGHT,
        "setback_height_m": FLOOR_HEIGHT,
        "roof_height_m": ROOF_HEIGHT,
        "crown_height_m": CROWN_HEIGHT,
        "default_floors": 2,
        "min_floors": 2,
        "max_floors": 3,
    }
    identity = (
        "A sober two-storey French Third Republic school reads as one "
        "forty-metre symmetrical civic monument through long red-brick "
        "classroom wings, cream limestone quoins and bands, three deeply "
        "recessed arched entrances, tall occupied dark-green timber sashes, a "
        "rough meuliere base, slate hips, four dormers, chimney pairs and a "
        "raised central clock pavilion."
    )
    material_zones = (
        "aged red-brown pressed brick in Flemish bond; porous warm cream "
        "limestone quoins, strings, archivolts, sills, dentils and inscription "
        "panel; rough tan-grey meuliere plinth; blue-grey natural slate; aged "
        "zinc ridges, gutters and canopies; dark-green painted timber; heritage "
        "low-e glass with pale curtains and occupied classroom depth; grey paving"
    )
    source = provenance()
    manifest = {
        "manifest_schema": 3,
        "grammar_schema_version": 3,
        "generator": {
            "name": "archetype_compiler/generate_wave10_school_family.py",
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
        "aesthetic_category_id": "classical",
        "development_type": "education",
        "reuse_keys": [
            ARCHETYPE_ID,
            VARIANT_ID,
            "Ecole Republicaine",
            "École Républicaine",
            "Third Republic Original",
            "Jules Ferry School",
            "French Municipal School",
        ],
        "generation_tags": [
            "wave10_essential_family",
            "standard_civic_building",
            "modular_classroom_streetwall",
            "custom_pbr_skin",
            "physical_heritage_sash_glazing",
            "reference_locked",
            "symmetrical_third_republic_school",
            "three_deep_civic_portals",
            "ecole_communale_relief",
            "tall_arched_classroom_windows",
            "red_brick_and_limestone_polychromy",
            "meuliere_base",
            "central_clock_pavilion",
            "natural_slate_hip_roof",
            "zinc_dormers_and_drainage",
            "rear_stair_pavilion",
        ],
        "footprint_compatibility": footprint,
        "coordinate_contract": COORDINATE_CONTRACT,
        "textures": texture_inventory(skin),
        "facade_sheet": facade_contract(skin),
        "massing_graph": {
            "type": "symmetrical_third_republic_school_bar",
            "silhouette": (
                "two_storey_horizontal_brick_school_with_raised_clock_centre_"
                "and_long_slate_hip"
            ),
            "render_locked": True,
            "goalpost": (
                f"/families/{FAMILY}/textures/source/archetype-goalpost.png"
            ),
            "fallback": "complete_classroom_bay_modular_streetwall",
            "classroom_wings": 2,
            "public_entrances": 3,
            "clock_pavilion": True,
        },
        "material_budget": {
            "max_assembled_materials": 18,
            "rationale": (
                "Custom masonry and roof PBR, physical heritage glazing, "
                "registered occupied depth, painted timber, zinc, clock and "
                "terracotta remain semantic."
            ),
        },
        "dimensions": dimensions,
        "native_width_m": WIDTH,
        "native_depth_m": DEPTH,
        "native_floors": 2,
        "min_floors": 2,
        "max_floors": 3,
        "default_floors": 2,
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
        "dimensions": dimensions,
        "architectural_signature": {
            "identity": identity,
            "material_zones": material_zones,
            "glass_profile": GLASS_PROFILE,
            "kits": [
                "symmetrical_third_republic_school",
                "three_deep_civic_portals",
                "ecole_communale_relief",
                "tall_arched_classroom_windows",
                "red_brick_and_limestone_polychromy",
                "meuliere_base",
                "central_clock_pavilion",
                "natural_slate_hip_roof",
                "zinc_dormers_and_drainage",
                "rear_stair_pavilion",
            ],
        },
        "archetype_aliases": [ARCHETYPE_ID, VARIANT_ID],
        "footprint_compatibility": footprint,
        "massing_graph": manifest["massing_graph"],
    }
    (folder / "grammar.json").write_text(
        json.dumps(grammar, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (folder / "archetype-source.json").write_text(
        json.dumps(source, indent=2, ensure_ascii=False) + "\n",
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
    assembled_objects = build_assembled(mats)
    assembled_path = folder / f"{FAMILY}_assembled.glb"
    export_glb(assembled_path, assembled_objects)
    fixed_triangles = evaluated_triangle_count(assembled_objects)
    fixed_materials = material_count(assembled_objects)
    existing_manifest_path = folder / f"{FAMILY}_manifest.json"
    existing_manifest = (
        json.loads(existing_manifest_path.read_text(encoding="utf-8"))
        if existing_manifest_path.is_file()
        else {}
    )
    renders = (
        list(existing_manifest.get("renders", []))
        if skip_renders
        else render_views(folder, view_set=view_set)
    )
    modules = (
        list(existing_manifest.get("modules", []))
        if skip_modules
        else build_modules(folder, mats, skin)
    )
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
        f"[wave10-school] {FAMILY}: {fixed_triangles} triangles, "
        f"{fixed_materials} materials, {len(modules)} modules, "
        f"{len(renders)} renders"
    )


def render_existing(output_root: Path, *, view_set: str) -> None:
    clear_scene()
    folder = output_root / FAMILY
    manifest_path = folder / f"{FAMILY}_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    bpy.ops.import_scene.gltf(
        filepath=str(folder / manifest["assembled"]["filename"])
    )
    manifest["renders"] = render_views(folder, view_set=view_set)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"[wave10-school-render] {FAMILY}: {len(manifest['renders'])} renders")


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
