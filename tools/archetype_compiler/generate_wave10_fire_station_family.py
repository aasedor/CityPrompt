"""Author the Wave 10 Mass-Timber Modern Fire Station LEGO family.

The canonical assembly is a real drive-through civic building with exactly
three apparatus lanes, an occupied glulam crew wing, a charred service spine,
an integrated stair/training tower and a planted photovoltaic roof.  Its LEGO
fallback keeps the operational podium and tower semantic while allowing one
to three occupied levels and whole-station streetwall repeat for hand-drawn
targets.

Run with Blender 5.x from the repository root:

    blender --background --factory-startup --python \
      tools/archetype_compiler/generate_wave10_fire_station_family.py -- \
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
from generate_wave10_courtyard_family import (  # noqa: E402
    evaluated_triangle_count,
    material_count,
    tbox,
)


FAMILY = "modern-fire-station-mass-timber"
ARCHETYPE_ID = "modern_fire_station"
VARIANT_ID = "fire_mass_timber"
LABEL = "Modern Fire Station — Mass Timber"
GLASS_PROFILE = "timber_station_neutral_low_e"

WIDTH = 40.0
DEPTH = 35.0
PODIUM_HEIGHT = 4.70
FLOOR_HEIGHT = 4.10
CROWN_HEIGHT = 0.45
ROOF_HEIGHT = 4.10
BODY_HEIGHT = PODIUM_HEIGHT + FLOOR_HEIGHT
TOTAL_HEIGHT = BODY_HEIGHT + CROWN_HEIGHT + ROOF_HEIGHT
WALL_THICKNESS = 0.28

FRONT_Y = -DEPTH / 2.0
REAR_Y = DEPTH / 2.0
MAIN_LEFT_X = -15.50
TOWER_LEFT_X = -20.0
TOWER_RIGHT_X = MAIN_LEFT_X
TOWER_FRONT_Y = FRONT_Y
TOWER_REAR_Y = -10.40
APPARATUS_LEFT_X = -11.15
APPARATUS_RIGHT_X = 11.35
SERVICE_LEFT_X = APPARATUS_RIGHT_X
RIGHT_X = WIDTH / 2.0
APPARATUS_CENTRES = (-7.35, 0.10, 7.55)
APPARATUS_WIDTH = 5.85
UPPER_WINDOW_CENTRES = (-11.95, -6.35, -0.75, 4.85)


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
        "timber": pbr_material(
            "MAT_W10_FIRE_HoneyVerticalTimberRainscreen",
            folder,
            near["honey_timber"],
            "honey_timber",
            saturation=0.92,
            value=0.92,
        ),
        "glulam": pbr_material(
            "MAT_W10_FIRE_ExposedHoneyGlulam",
            folder,
            near["glulam"],
            "glulam",
            saturation=0.92,
            value=0.94,
        ),
        "charred": pbr_material(
            "MAT_W10_FIRE_ShouSugiBanCharredTimber",
            folder,
            near["charred_timber"],
            "charred_timber",
            saturation=0.62,
            value=0.66,
        ),
        "concrete": pbr_material(
            "MAT_W10_FIRE_BoardFormedConcrete",
            folder,
            near["concrete"],
            "concrete",
            saturation=0.60,
            value=0.93,
        ),
        "green_roof": pbr_material(
            "MAT_W10_FIRE_NativeMeadowGreenRoof",
            folder,
            near["green_roof"],
            "green_roof",
            saturation=0.92,
            value=0.76,
        ),
        "solar": pbr_material(
            "MAT_W10_FIRE_PhotovoltaicAndBlackMetal",
            folder,
            near["solar_metal"],
            "solar_metal",
            metallic=0.60,
            saturation=0.76,
            value=0.68,
        ),
        "paving": pbr_material(
            "MAT_W10_FIRE_PaleApparatusConcrete",
            folder,
            near["paving"],
            "paving",
            saturation=0.52,
            value=0.93,
        ),
        "facade": pbr_material(
            "MAT_W10_FIRE_RegisteredFrontElevationProof",
            folder,
            near["facade"],
            "facade",
            saturation=0.92,
            value=0.96,
        ),
        "glass": profiled_glass_material(
            "MAT_W10_FIRE_PhysicalNeutralLowE",
            GLASS_PROFILE,
            tint="#607074",
            roughness_scale=1.10,
            transmission_scale=0.92,
        ),
        "channel_glass": profiled_glass_material(
            "MAT_W10_FIRE_TranslucentChannelGlass",
            "low_iron_clear",
            tint="#aebcba",
            roughness_scale=4.20,
            transmission_scale=0.64,
        ),
        "crew_underlay": reference_image_material(
            "MAT_W10_FIRE_RegisteredOccupiedCrewDepth",
            folder,
            "textures/source/crew-interior-source-v1.png",
            emission_strength=0.055,
        ),
        "apparatus_underlay": reference_image_material(
            "MAT_W10_FIRE_RegisteredApparatusDepth",
            folder,
            "textures/source/apparatus-interior-source-v1.png",
            emission_strength=0.070,
        ),
        "deep": material(
            "MAT_W10_FIRE_DeepConstructionCavity",
            (0.010, 0.013, 0.014, 1.0),
            0.96,
        ),
        "frame": material(
            "MAT_W10_FIRE_BlackThermalBreakFrame",
            (0.022, 0.025, 0.026, 1.0),
            0.38,
            metallic=0.38,
        ),
        "red": material(
            "MAT_W10_FIRE_EngineRed",
            (0.55, 0.018, 0.014, 1.0),
            0.25,
            metallic=0.12,
        ),
        "chrome": material(
            "MAT_W10_FIRE_EngineChrome",
            (0.47, 0.50, 0.52, 1.0),
            0.18,
            metallic=0.90,
        ),
        "rubber": material(
            "MAT_W10_FIRE_EngineRubber",
            (0.012, 0.013, 0.013, 1.0),
            0.84,
        ),
        "yellow": material(
            "MAT_W10_FIRE_ApparatusSafetyYellow",
            (0.90, 0.61, 0.04, 1.0),
            0.46,
        ),
        "warm_light": material(
            "MAT_W10_FIRE_WarmInteriorLight",
            (0.65, 0.48, 0.28, 1.0),
            0.48,
            emission=(1.0, 0.70, 0.38, 1.0),
            emission_strength=1.7,
        ),
        "curtain": material(
            "MAT_W10_FIRE_PaleLinenCurtain",
            (0.52, 0.50, 0.45, 1.0),
            0.92,
        ),
        "gravel": material(
            "MAT_W10_FIRE_LightRoofGravel",
            (0.43, 0.43, 0.39, 1.0),
            0.94,
        ),
        "plant_dark": material(
            "MAT_W10_FIRE_DarkNativeGrass",
            (0.075, 0.16, 0.055, 1.0),
            0.96,
        ),
        "flower_yellow": material(
            "MAT_W10_FIRE_YellowWildflower",
            (0.70, 0.43, 0.035, 1.0),
            0.88,
        ),
        "flower_purple": material(
            "MAT_W10_FIRE_PurpleWildflower",
            (0.37, 0.16, 0.34, 1.0),
            0.88,
        ),
    }
    for key in ("crew_underlay", "apparatus_underlay"):
        for node in mats[key].node_tree.nodes:
            if node.bl_idname == "ShaderNodeTexImage":
                node.extension = "REPEAT"
        mats[key]["glazing_profile"] = GLASS_PROFILE
        mats[key]["source_variant_id"] = VARIANT_ID
    for key in ("glass", "channel_glass"):
        mats[key]["glazing_lod"] = "always"
        mats[key]["reference_locked"] = True
        mats[key]["source_variant_id"] = VARIANT_ID
    mats["channel_glass"]["channel_glass"] = True
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
            tile_m=1.30,
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
            tile_m=1.30,
        )
        for index, (ry0, ry1, rz0, rz1) in enumerate(
            rectangles_around_openings(y0, y1, z0, z1, openings)
        )
    ]


def add_vertical_battens_y(
    name: str,
    *,
    x0: float,
    x1: float,
    height: float,
    surface_y: float,
    outward_sign: int,
    openings: list[tuple[float, float, float, float]],
    mat: bpy.types.Material,
    spacing: float = 0.34,
) -> list[bpy.types.Object]:
    count = max(1, int((x1 - x0) / spacing))
    objects: list[bpy.types.Object] = []
    for index in range(count + 1):
        x = x0 + (x1 - x0) * index / count
        for segment_index, (_, _, z0, z1) in enumerate(
            rectangles_around_openings(
                x - 0.027,
                x + 0.027,
                0.0,
                height,
                openings,
            )
        ):
            objects.append(
                tbox(
                    f"{name}_Batten_{index:03d}_{segment_index}",
                    (0.054, 0.038, z1 - z0),
                    (
                        x,
                        surface_y + outward_sign * 0.022,
                        (z0 + z1) * 0.5,
                    ),
                    mat,
                    0.006,
                    tile_m=0.72,
                )
            )
    return objects


def add_vertical_battens_x(
    name: str,
    *,
    y0: float,
    y1: float,
    height: float,
    surface_x: float,
    outward_sign: int,
    openings: list[tuple[float, float, float, float]],
    mat: bpy.types.Material,
    spacing: float = 0.34,
) -> list[bpy.types.Object]:
    count = max(1, int((y1 - y0) / spacing))
    objects: list[bpy.types.Object] = []
    for index in range(count + 1):
        y = y0 + (y1 - y0) * index / count
        for segment_index, (_, _, z0, z1) in enumerate(
            rectangles_around_openings(
                y - 0.027,
                y + 0.027,
                0.0,
                height,
                openings,
            )
        ):
            objects.append(
                tbox(
                    f"{name}_Batten_{index:03d}_{segment_index}",
                    (0.038, 0.054, z1 - z0),
                    (
                        surface_x + outward_sign * 0.022,
                        y,
                        (z0 + z1) * 0.5,
                    ),
                    mat,
                    0.006,
                    tile_m=0.72,
                )
            )
    return objects


def add_y_window(
    name: str,
    *,
    centre_x: float,
    sill_z: float,
    width: float,
    height: float,
    surface_y: float,
    outward_sign: int,
    mats: dict[str, bpy.types.Material],
    variant: str,
) -> list[bpy.types.Object]:
    inside = -outward_sign
    zc = sill_z + height * 0.5
    pane_y = surface_y + inside * 0.28
    frame_y = pane_y - inside * 0.035
    room_y = surface_y + inside * 0.76
    objects: list[bpy.types.Object] = [
        box(
            f"{name}_OccupiedDayroomDepth",
            (width - 0.26, 0.025, height - 0.24),
            (centre_x, room_y, zc),
            mats["crew_underlay"],
            0.004,
        ),
        tbox(
            f"{name}_PhysicalLowEPane",
            (width - 0.18, 0.030, height - 0.18),
            (centre_x, pane_y, zc),
            mats["glass"],
            0.006,
            tile_m=0.9,
        ),
    ]
    jamb = 0.105
    head = 0.110
    for side in (-1, 1):
        objects.append(
            tbox(
                f"{name}_ThermalJamb_{side:+d}",
                (jamb, 0.16, height),
                (
                    centre_x + side * (width * 0.5 - jamb * 0.5),
                    frame_y,
                    zc,
                ),
                mats["frame"],
                0.008,
                tile_m=0.55,
            )
        )
    for position, z in (
        ("Sill", sill_z + head * 0.5),
        ("Head", sill_z + height - head * 0.5),
    ):
        objects.append(
            tbox(
                f"{name}_{position}",
                (width, 0.16, head),
                (centre_x, frame_y, z),
                mats["frame"],
                0.008,
                tile_m=0.55,
            )
        )
    for index in (1, 2):
        x = centre_x - width * 0.5 + width * index / 3.0
        objects.append(
            tbox(
                f"{name}_Mullion_{index}",
                (0.075, 0.165, height - 0.18),
                (x, frame_y, zc),
                mats["frame"],
                0.006,
                tile_m=0.55,
            )
        )
    objects.append(
        tbox(
            f"{name}_OperableTransom",
            (width - 0.20, 0.17, 0.068),
            (centre_x, frame_y, sill_z + height * 0.74),
            mats["frame"],
            0.006,
            tile_m=0.55,
        )
    )
    if (sum(ord(value) for value in name + variant) % 3) != 0:
        curtain_x = centre_x + (-0.62 if variant == "typical_b" else 0.62)
        objects.append(
            tbox(
                f"{name}_OffsetLinenCurtain",
                (0.66, 0.020, height - 0.34),
                (curtain_x, room_y - inside * 0.035, zc),
                mats["curtain"],
                0.004,
                tile_m=0.75,
            )
        )
    return objects


def add_x_window(
    name: str,
    *,
    centre_y: float,
    sill_z: float,
    width: float,
    height: float,
    surface_x: float,
    outward_sign: int,
    mats: dict[str, bpy.types.Material],
    variant: str,
) -> list[bpy.types.Object]:
    inside = -outward_sign
    zc = sill_z + height * 0.5
    pane_x = surface_x + inside * 0.28
    frame_x = pane_x - inside * 0.035
    room_x = surface_x + inside * 0.76
    objects: list[bpy.types.Object] = [
        box(
            f"{name}_OccupiedDayroomDepth",
            (0.025, width - 0.26, height - 0.24),
            (room_x, centre_y, zc),
            mats["crew_underlay"],
            0.004,
        ),
        tbox(
            f"{name}_PhysicalLowEPane",
            (0.030, width - 0.18, height - 0.18),
            (pane_x, centre_y, zc),
            mats["glass"],
            0.006,
            tile_m=0.9,
        ),
    ]
    for side in (-1, 1):
        objects.append(
            tbox(
                f"{name}_ThermalJamb_{side:+d}",
                (0.16, 0.105, height),
                (
                    frame_x,
                    centre_y + side * (width * 0.5 - 0.0525),
                    zc,
                ),
                mats["frame"],
                0.008,
                tile_m=0.55,
            )
        )
    for position, z in (
        ("Sill", sill_z + 0.055),
        ("Head", sill_z + height - 0.055),
    ):
        objects.append(
            tbox(
                f"{name}_{position}",
                (0.16, width, 0.110),
                (frame_x, centre_y, z),
                mats["frame"],
                0.008,
                tile_m=0.55,
            )
        )
    objects.extend(
        [
            tbox(
                f"{name}_Mullion",
                (0.165, 0.075, height - 0.18),
                (frame_x, centre_y, zc),
                mats["frame"],
                0.006,
                tile_m=0.55,
            ),
            tbox(
                f"{name}_OperableTransom",
                (0.17, width - 0.20, 0.068),
                (frame_x, centre_y, sill_z + height * 0.74),
                mats["frame"],
                0.006,
                tile_m=0.55,
            ),
        ]
    )
    if (sum(ord(value) for value in name + variant) % 2) == 0:
        objects.append(
            tbox(
                f"{name}_OffsetLinenCurtain",
                (0.020, 0.68, height - 0.34),
                (room_x - inside * 0.035, centre_y + 0.44, zc),
                mats["curtain"],
                0.004,
                tile_m=0.75,
            )
        )
    return objects


def add_public_entry(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    centre_x = -13.26
    width = 2.85
    height = 3.48
    inside_y = FRONT_Y + 0.58
    objects: list[bpy.types.Object] = [
        box(
            "FirePublicEntryOccupiedLobbyDepth",
            (width - 0.30, 0.025, height - 0.34),
            (centre_x, FRONT_Y + 2.25, height * 0.5 + 0.10),
            mats["crew_underlay"],
            0.004,
        ),
        tbox(
            "FirePublicEntryDoubleGlass",
            (width - 0.34, 0.035, height - 0.38),
            (centre_x, inside_y, height * 0.5 + 0.10),
            mats["glass"],
            0.006,
            tile_m=0.8,
        ),
        tbox(
            "FirePublicEntryDoorMullion",
            (0.085, 0.15, height - 0.32),
            (centre_x, inside_y - 0.04, height * 0.5 + 0.10),
            mats["frame"],
            0.006,
            tile_m=0.55,
        ),
        tbox(
            "FirePublicEntryHeader",
            (width, 0.18, 0.12),
            (centre_x, inside_y - 0.04, height + 0.10),
            mats["frame"],
            0.008,
            tile_m=0.55,
        ),
        tbox(
            "FirePublicEntryThreshold",
            (width + 0.36, 0.90, 0.16),
            (centre_x, FRONT_Y - 0.12, 0.08),
            mats["concrete"],
            0.018,
            tile_m=1.2,
        ),
    ]
    for side in (-1, 1):
        x = centre_x + side * (width * 0.5 + 0.32)
        objects.append(
            tbox(
                f"FirePublicEntryGlulamPost_{side:+d}",
                (0.38, 0.46, 4.22),
                (x, FRONT_Y - 0.48, 2.11),
                mats["glulam"],
                0.025,
                tile_m=1.25,
            )
        )
    objects.extend(
        [
            tbox(
                "FirePublicEntryIntegratedGlulamCanopy",
                (width + 1.20, 2.10, 0.34),
                (centre_x, FRONT_Y - 0.15, 4.05),
                mats["glulam"],
                0.025,
                tile_m=1.25,
            ),
            tbox(
                "FirePublicEntryCanopyFlashing",
                (width + 1.34, 2.18, 0.075),
                (centre_x, FRONT_Y - 0.15, 4.255),
                mats["solar"],
                0.012,
                tile_m=0.65,
            ),
        ]
    )
    return objects


def add_apparatus_door(
    name: str,
    *,
    centre_x: float,
    surface_y: float,
    outward_sign: int,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    inside = -outward_sign
    width = APPARATUS_WIDTH
    height = 4.05
    zc = 0.14 + height * 0.5
    pane_y = surface_y + inside * 0.30
    frame_y = pane_y - inside * 0.045
    depth_y = surface_y + inside * 3.20
    objects: list[bpy.types.Object] = [
        box(
            f"{name}_RegisteredApparatusDepth",
            (width - 0.34, 0.028, height - 0.30),
            (centre_x, depth_y, zc),
            mats["apparatus_underlay"],
            0.004,
        ),
        tbox(
            f"{name}_PhysicalFourFoldGlass",
            (width - 0.16, 0.035, height - 0.14),
            (centre_x, pane_y, zc),
            mats["glass"],
            0.005,
            tile_m=0.9,
        ),
    ]
    for side in (-1, 1):
        objects.append(
            tbox(
                f"{name}_DoorJamb_{side:+d}",
                (0.14, 0.22, height),
                (
                    centre_x + side * (width * 0.5 - 0.07),
                    frame_y,
                    zc,
                ),
                mats["frame"],
                0.008,
                tile_m=0.55,
            )
        )
    for rail_index in range(7):
        z = 0.14 + height * rail_index / 6.0
        objects.append(
            tbox(
                f"{name}_PanelRail_{rail_index}",
                (width, 0.19, 0.085),
                (centre_x, frame_y, z),
                mats["frame"],
                0.006,
                tile_m=0.55,
            )
        )
    for mullion_index, offset in enumerate((-width / 4.0, 0.0, width / 4.0)):
        objects.append(
            tbox(
                f"{name}_FourFoldMullion_{mullion_index}",
                (0.082, 0.19, height - 0.16),
                (centre_x + offset, frame_y, zc),
                mats["frame"],
                0.006,
                tile_m=0.55,
            )
        )
    return objects


def add_service_door_y(
    name: str,
    *,
    centre_x: float,
    surface_y: float,
    outward_sign: int,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    inside = -outward_sign
    objects = [
        tbox(
            f"{name}_DoorLeaf",
            (1.02, 0.080, 2.28),
            (centre_x, surface_y + inside * 0.40, 1.24),
            mats["frame"],
            0.012,
            tile_m=0.65,
        ),
        tbox(
            f"{name}_NarrowGlass",
            (0.38, 0.035, 1.45),
            (centre_x, surface_y + inside * 0.35, 1.45),
            mats["glass"],
            0.005,
            tile_m=0.7,
        ),
    ]
    return objects


def build_fire_engine(
    index: int,
    centre_x: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    centre_y = -10.20 + (index % 2) * 0.18
    objects: list[bpy.types.Object] = [
        tbox(
            f"FireEngine{index}_Chassis",
            (2.62, 7.20, 0.38),
            (centre_x, centre_y, 0.56),
            mats["frame"],
            0.06,
            tile_m=0.8,
        ),
        tbox(
            f"FireEngine{index}_Body",
            (2.52, 4.55, 1.86),
            (centre_x, centre_y + 1.05, 1.65),
            mats["red"],
            0.10,
            tile_m=0.9,
        ),
        tbox(
            f"FireEngine{index}_Cab",
            (2.48, 2.35, 2.32),
            (centre_x, centre_y - 2.35, 1.88),
            mats["red"],
            0.12,
            tile_m=0.9,
        ),
        tbox(
            f"FireEngine{index}_FrontWindshield",
            (2.12, 0.055, 0.72),
            (centre_x, centre_y - 3.555, 2.45),
            mats["glass"],
            0.012,
            tile_m=0.7,
        ),
        tbox(
            f"FireEngine{index}_ChromeGrille",
            (1.58, 0.10, 0.70),
            (centre_x, centre_y - 3.605, 1.30),
            mats["chrome"],
            0.025,
            tile_m=0.55,
        ),
        tbox(
            f"FireEngine{index}_FrontBumper",
            (2.66, 0.22, 0.22),
            (centre_x, centre_y - 3.72, 0.66),
            mats["chrome"],
            0.04,
            tile_m=0.55,
        ),
        tbox(
            f"FireEngine{index}_RoofEquipment",
            (1.75, 3.10, 0.24),
            (centre_x, centre_y + 0.80, 2.78),
            mats["chrome"],
            0.05,
            tile_m=0.55,
        ),
        tbox(
            f"FireEngine{index}_RedLightBar",
            (1.72, 0.24, 0.16),
            (centre_x, centre_y - 2.60, 3.12),
            mats["red"],
            0.035,
            tile_m=0.55,
        ),
    ]
    for side in (-1, 1):
        for axle_index, y in enumerate((centre_y - 2.15, centre_y + 2.05)):
            wheel = cylinder(
                f"FireEngine{index}_Wheel_{side:+d}_{axle_index}",
                0.48,
                0.34,
                (centre_x + side * 1.30, y, 0.50),
                mats["rubber"],
                vertices=20,
            )
            wheel.rotation_euler.y = math.radians(90.0)
            objects.append(wheel)
            hub = cylinder(
                f"FireEngine{index}_WheelHub_{side:+d}_{axle_index}",
                0.22,
                0.37,
                (centre_x + side * 1.31, y, 0.50),
                mats["chrome"],
                vertices=16,
            )
            hub.rotation_euler.y = math.radians(90.0)
            objects.append(hub)
    for side in (-1, 1):
        objects.append(
            tbox(
                f"FireEngine{index}_Headlight_{side:+d}",
                (0.30, 0.08, 0.23),
                (
                    centre_x + side * 0.80,
                    centre_y - 3.67,
                    1.02,
                ),
                mats["warm_light"],
                0.02,
                tile_m=0.5,
            )
        )
    return objects


def add_apparatus_hall_structure(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    for x_index, x in enumerate(
        (
            APPARATUS_LEFT_X + 0.24,
            -3.62,
            3.82,
            APPARATUS_RIGHT_X - 0.24,
        )
    ):
        for y_index, y in enumerate((-15.9, -7.9, 0.0, 7.9, 15.9)):
            objects.append(
                tbox(
                    f"FireHallGlulamColumn_{x_index}_{y_index}",
                    (0.34, 0.34, 4.28),
                    (x, y, 2.14),
                    mats["glulam"],
                    0.025,
                    tile_m=1.25,
                )
            )
    for x_index, x in enumerate((-7.35, 0.10, 7.55)):
        for y_index, y in enumerate((-13.8, -6.9, 0.0, 6.9, 13.8)):
            objects.append(
                tbox(
                    f"FireHallGlulamCeilingBeam_{x_index}_{y_index}",
                    (6.75, 0.32, 0.42),
                    (x, y, 4.34),
                    mats["glulam"],
                    0.025,
                    tile_m=1.25,
                )
            )
            objects.append(
                tbox(
                    f"FireHallLinearLight_{x_index}_{y_index}",
                    (3.15, 0.09, 0.055),
                    (x, y - 0.20, 4.08),
                    mats["warm_light"],
                    0.01,
                    tile_m=0.5,
                )
            )
        objects.extend(
            [
                tbox(
                    f"FireHallGuideLineFront_{x_index}",
                    (0.10, 13.8, 0.018),
                    (x - 2.25, -7.2, 0.22),
                    mats["yellow"],
                    0.003,
                    tile_m=0.5,
                ),
                tbox(
                    f"FireHallGuideLineRear_{x_index}",
                    (0.10, 13.8, 0.018),
                    (x + 2.25, 7.2, 0.22),
                    mats["yellow"],
                    0.003,
                    tile_m=0.5,
                ),
            ]
        )
    return objects


def add_stair_flight(
    name: str,
    *,
    x_center: float,
    y0: float,
    y1: float,
    z0: float,
    z1: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    steps = 11
    stair_width = 1.52
    tread_depth = abs(y1 - y0) / steps + 0.035
    objects: list[bpy.types.Object] = []
    for index in range(steps):
        fraction = (index + 0.5) / steps
        y = y0 + (y1 - y0) * fraction
        z = z0 + (z1 - z0) * (index + 1) / steps
        objects.append(
            tbox(
                f"{name}_RealTread_{index:02d}",
                (stair_width, tread_depth, 0.115),
                (x_center, y, z),
                mats["glulam"],
                0.008,
                tile_m=0.72,
            )
        )
    for side in (-1, 1):
        x = x_center + side * stair_width * 0.46
        objects.append(
            round_beam(
                f"{name}_SteelStringer_{side:+d}",
                (x, y0, z0 + 0.03),
                (x, y1, z1 + 0.03),
                0.055,
                mats["frame"],
                vertices=10,
            )
        )
        objects.append(
            round_beam(
                f"{name}_Handrail_{side:+d}",
                (x, y0, z0 + 1.02),
                (x, y1, z1 + 1.02),
                0.032,
                mats["frame"],
                vertices=10,
            )
        )
        for post_index in range(4):
            fraction = post_index / 3.0
            y = y0 + (y1 - y0) * fraction
            z = z0 + (z1 - z0) * fraction
            objects.append(
                round_beam(
                    f"{name}_GuardPost_{side:+d}_{post_index}",
                    (x, y, z + 0.12),
                    (x, y, z + 1.02),
                    0.023,
                    mats["frame"],
                    vertices=8,
                )
            )
    return objects


def add_tower_segment(
    name: str,
    *,
    height: float,
    mats: dict[str, bpy.types.Material],
    include_stairs: bool = True,
) -> list[bpy.types.Object]:
    centre_x = (TOWER_LEFT_X + TOWER_RIGHT_X) * 0.5
    centre_y = (TOWER_FRONT_Y + TOWER_REAR_Y) * 0.5
    depth = TOWER_REAR_Y - TOWER_FRONT_Y
    objects: list[bpy.types.Object] = [
        tbox(
            f"{name}_LeftConcreteWall",
            (0.48, depth, height),
            (TOWER_LEFT_X + 0.24, centre_y, height * 0.5),
            mats["concrete"],
            0.018,
            tile_m=1.35,
        ),
        tbox(
            f"{name}_RightConcreteWall",
            (0.48, depth, height),
            (TOWER_RIGHT_X - 0.24, centre_y, height * 0.5),
            mats["concrete"],
            0.018,
            tile_m=1.35,
        ),
        tbox(
            f"{name}_RearConcreteWall",
            (TOWER_RIGHT_X - TOWER_LEFT_X, 0.36, height),
            (centre_x, TOWER_REAR_Y - 0.18, height * 0.5),
            mats["concrete"],
            0.018,
            tile_m=1.35,
        ),
        tbox(
            f"{name}_PhysicalChannelGlass",
            (3.18, 0.035, height - 0.28),
            (centre_x, TOWER_FRONT_Y + 0.34, height * 0.5),
            mats["channel_glass"],
            0.006,
            tile_m=0.85,
        ),
        tbox(
            f"{name}_TowerFloorTie",
            (TOWER_RIGHT_X - TOWER_LEFT_X, depth, 0.20),
            (centre_x, centre_y, 0.10),
            mats["concrete"],
            0.015,
            tile_m=1.35,
        ),
        tbox(
            f"{name}_TowerTopTie",
            (TOWER_RIGHT_X - TOWER_LEFT_X, depth, 0.24),
            (centre_x, centre_y, height - 0.12),
            mats["concrete"],
            0.015,
            tile_m=1.35,
        ),
    ]
    for x_index, x in enumerate((centre_x - 1.12, centre_x, centre_x + 1.12)):
        objects.append(
            tbox(
                f"{name}_ChannelGlassVertical_{x_index}",
                (0.085, 0.16, height - 0.30),
                (x, TOWER_FRONT_Y + 0.30, height * 0.5),
                mats["frame"],
                0.006,
                tile_m=0.55,
            )
        )
    objects.append(
        tbox(
            f"{name}_ChannelGlassMidRail",
            (3.26, 0.16, 0.09),
            (centre_x, TOWER_FRONT_Y + 0.30, height * 0.50),
            mats["frame"],
            0.006,
            tile_m=0.55,
        )
    )
    for slat_index in range(11):
        x = centre_x - 1.30 + slat_index * 0.26
        objects.append(
            tbox(
                f"{name}_WarmTimberScreen_{slat_index:02d}",
                (0.055, 0.070, height - 0.38),
                (x, TOWER_FRONT_Y + 0.52, height * 0.5),
                mats["timber"],
                0.005,
                tile_m=0.55,
            )
        )
    if include_stairs:
        half = height * 0.5
        objects.extend(
            add_stair_flight(
                f"{name}_LowerFlight",
                x_center=centre_x,
                y0=TOWER_FRONT_Y + 1.08,
                y1=TOWER_REAR_Y - 1.12,
                z0=0.20,
                z1=half,
                mats=mats,
            )
        )
        objects.append(
            tbox(
                f"{name}_RealMidLanding",
                (2.05, 1.22, 0.16),
                (centre_x, TOWER_REAR_Y - 0.72, half + 0.03),
                mats["concrete"],
                0.012,
                tile_m=1.15,
            )
        )
        objects.extend(
            add_stair_flight(
                f"{name}_UpperFlight",
                x_center=centre_x,
                y0=TOWER_REAR_Y - 1.14,
                y1=TOWER_FRONT_Y + 1.08,
                z0=half + 0.10,
                z1=height - 0.22,
                mats=mats,
            )
        )
    return objects


def add_upper_glulam_gallery(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    gallery_y = FRONT_Y - 0.10
    # The inhabited balcony belongs to the lobby/apparatus bar and stops at
    # the charred service spine, as it does in every authored reference view.
    post_xs = (-15.05, -10.30, -4.70, 0.90, 6.50, 11.95)
    for index, x in enumerate(post_xs):
        objects.append(
            tbox(
                f"FireUpperGalleryGlulamPost_{index}",
                (0.34, 0.38, FLOOR_HEIGHT - 0.22),
                (x, gallery_y, (FLOOR_HEIGHT - 0.22) * 0.5),
                mats["glulam"],
                0.025,
                tile_m=1.25,
            )
        )
    objects.extend(
        [
            tbox(
                "FireUpperGalleryContinuousGlulamBeam",
                (27.35, 0.50, 0.42),
                (-1.55, gallery_y, FLOOR_HEIGHT - 0.23),
                mats["glulam"],
                0.025,
                tile_m=1.25,
            ),
            tbox(
                "FireUpperGallerySoffit",
                (27.10, 1.42, 0.20),
                (-1.55, FRONT_Y + 0.54, FLOOR_HEIGHT - 0.58),
                mats["glulam"],
                0.018,
                tile_m=1.25,
            ),
            tbox(
                "FireUpperGalleryBalconySlab",
                (27.10, 1.48, 0.20),
                (-1.55, FRONT_Y + 0.56, 0.12),
                mats["concrete"],
                0.018,
                tile_m=1.30,
            ),
        ]
    )
    for panel_index, (x0, x1) in enumerate(zip(post_xs, post_xs[1:])):
        centre = (x0 + x1) * 0.5
        width = x1 - x0 - 0.22
        objects.extend(
            [
                tbox(
                    f"FireUpperGalleryGlassGuard_{panel_index}",
                    (width, 0.028, 0.92),
                    (centre, FRONT_Y - 0.23, 0.68),
                    mats["glass"],
                    0.004,
                    tile_m=0.8,
                ),
                tbox(
                    f"FireUpperGalleryGuardCap_{panel_index}",
                    (width, 0.065, 0.050),
                    (centre, FRONT_Y - 0.23, 1.16),
                    mats["frame"],
                    0.005,
                    tile_m=0.55,
                ),
            ]
        )
    for planter_index, x in enumerate((-13.50, -8.10, 2.75, 9.90)):
        objects.extend(
            [
                cylinder(
                    f"FireUpperGalleryPlanter_{planter_index}",
                    0.23,
                    0.44,
                    (x, FRONT_Y + 0.30, 0.42),
                    mats["frame"],
                    vertices=16,
                    scale_xy=(1.0, 0.82),
                ),
                cylinder(
                    f"FireUpperGalleryNativePlant_{planter_index}",
                    0.17,
                    0.50,
                    (x, FRONT_Y + 0.30, 0.85),
                    mats["plant_dark"],
                    vertices=7,
                    scale_xy=(1.0, 0.56),
                ),
            ]
        )
    return objects


def build_podium(
    mats: dict[str, bpy.types.Material],
    *,
    include_contract_markers: bool = True,
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = [
        tbox(
            "FirePodiumFullOperationalSlab",
            (WIDTH, DEPTH, 0.22),
            (0.0, 0.0, 0.11),
            mats["concrete"],
            0.016,
            tile_m=1.50,
        )
    ]
    apparatus_openings = [
        (
            centre - APPARATUS_WIDTH * 0.5,
            centre + APPARATUS_WIDTH * 0.5,
            0.14,
            4.19,
        )
        for centre in APPARATUS_CENTRES
    ]
    objects.extend(
        add_y_wall(
            "FirePodiumFrontApparatus",
            x0=APPARATUS_LEFT_X,
            x1=APPARATUS_RIGHT_X,
            z0=0.0,
            z1=PODIUM_HEIGHT,
            surface_y=FRONT_Y,
            outward_sign=-1,
            openings=apparatus_openings,
            mat=mats["concrete"],
        )
    )
    objects.extend(
        add_y_wall(
            "FirePodiumRearApparatus",
            x0=APPARATUS_LEFT_X,
            x1=APPARATUS_RIGHT_X,
            z0=0.0,
            z1=PODIUM_HEIGHT,
            surface_y=REAR_Y,
            outward_sign=1,
            openings=apparatus_openings,
            mat=mats["concrete"],
        )
    )
    entry_opening = [(-14.685, -11.835, 0.10, 3.58)]
    for face, y, sign in (
        ("Front", FRONT_Y, -1),
        ("Rear", REAR_Y, 1),
    ):
        objects.extend(
            add_y_wall(
                f"FirePodium{face}Lobby",
                x0=MAIN_LEFT_X,
                x1=APPARATUS_LEFT_X,
                z0=0.0,
                z1=PODIUM_HEIGHT,
                surface_y=y,
                outward_sign=sign,
                openings=entry_opening if face == "Front" else [],
                mat=mats["timber"],
            )
        )
    service_front_openings = [(14.15, 15.33, 0.10, 2.50)]
    service_rear_openings = [
        (13.15, 14.33, 0.10, 2.50),
        (17.10, 18.28, 0.10, 2.50),
    ]
    for face, y, sign, openings in (
        ("Front", FRONT_Y, -1, service_front_openings),
        ("Rear", REAR_Y, 1, service_rear_openings),
    ):
        objects.extend(
            add_y_wall(
                f"FirePodium{face}CharredService",
                x0=SERVICE_LEFT_X,
                x1=RIGHT_X,
                z0=0.0,
                z1=PODIUM_HEIGHT,
                surface_y=y,
                outward_sign=sign,
                openings=openings,
                mat=mats["charred"],
            )
        )
        objects.extend(
            add_vertical_battens_y(
                f"FirePodium{face}Charred",
                x0=SERVICE_LEFT_X + 0.10,
                x1=RIGHT_X - 0.10,
                height=PODIUM_HEIGHT,
                surface_y=y,
                outward_sign=sign,
                openings=openings,
                mat=mats["charred"],
                spacing=0.30,
            )
        )
    right_openings = [
        (-12.3, -10.7, 0.55, 2.60),
        (6.8, 8.0, 0.10, 2.50),
        (11.4, 13.1, 0.55, 2.60),
    ]
    objects.extend(
        add_x_wall(
            "FirePodiumRightServiceReturn",
            y0=FRONT_Y,
            y1=REAR_Y,
            z0=0.0,
            z1=PODIUM_HEIGHT,
            surface_x=RIGHT_X,
            outward_sign=1,
            openings=right_openings,
            mat=mats["charred"],
        )
    )
    objects.extend(
        add_vertical_battens_x(
            "FirePodiumRightCharredReturn",
            y0=FRONT_Y + 0.10,
            y1=REAR_Y - 0.10,
            height=PODIUM_HEIGHT,
            surface_x=RIGHT_X,
            outward_sign=1,
            openings=right_openings,
            mat=mats["charred"],
            spacing=0.31,
        )
    )
    left_openings = [
        (-5.0, -2.9, 0.65, 2.85),
        (7.8, 9.9, 0.65, 2.85),
    ]
    objects.extend(
        add_x_wall(
            "FirePodiumLeftCrewReturn",
            y0=TOWER_REAR_Y,
            y1=REAR_Y,
            z0=0.0,
            z1=PODIUM_HEIGHT,
            surface_x=MAIN_LEFT_X,
            outward_sign=-1,
            openings=left_openings,
            mat=mats["timber"],
        )
    )
    for index, centre in enumerate(APPARATUS_CENTRES):
        objects.extend(
            add_apparatus_door(
                f"FireFrontApparatusDoor_{index + 1}",
                centre_x=centre,
                surface_y=FRONT_Y,
                outward_sign=-1,
                mats=mats,
            )
        )
        objects.extend(
            add_apparatus_door(
                f"FireRearApparatusDoor_{index + 1}",
                centre_x=centre,
                surface_y=REAR_Y,
                outward_sign=1,
                mats=mats,
            )
        )
        objects.extend(build_fire_engine(index + 1, centre, mats))
    objects.extend(add_public_entry(mats))
    objects.extend(
        add_service_door_y(
            "FireFrontServiceDoor",
            centre_x=14.74,
            surface_y=FRONT_Y,
            outward_sign=-1,
            mats=mats,
        )
    )
    objects.extend(
        add_service_door_y(
            "FireRearDecontaminationDoor",
            centre_x=13.74,
            surface_y=REAR_Y,
            outward_sign=1,
            mats=mats,
        )
    )
    objects.extend(
        add_service_door_y(
            "FireRearServiceDoor",
            centre_x=17.69,
            surface_y=REAR_Y,
            outward_sign=1,
            mats=mats,
        )
    )
    for index, (y, width) in enumerate(((-11.5, 1.60), (12.2, 1.70))):
        objects.extend(
            add_x_window(
                f"FirePodiumRightServiceWindow_{index}",
                centre_y=y,
                sill_z=0.55,
                width=width,
                height=2.05,
                surface_x=RIGHT_X,
                outward_sign=1,
                mats=mats,
                variant="podium",
            )
        )
    objects.extend(add_apparatus_hall_structure(mats))
    objects.extend(
        add_tower_segment(
            "FirePodiumIntegratedTrainingTower",
            height=PODIUM_HEIGHT,
            mats=mats,
        )
    )
    # Trench drains and hose/decontamination fixtures make both service aprons
    # operational without expanding the metric building envelope.
    for face, y in (("Front", FRONT_Y + 0.06), ("Rear", REAR_Y - 0.06)):
        objects.append(
            tbox(
                f"Fire{face}ContinuousTrenchDrain",
                (23.3, 0.12, 0.045),
                (0.10, y, 0.245),
                mats["frame"],
                0.004,
                tile_m=0.55,
            )
        )
    for fixture_index, z in enumerate((1.05, 1.42, 1.79)):
        objects.append(
            cylinder(
                f"FireRearHoseConnection_{fixture_index}",
                0.115,
                0.16,
                (16.2, REAR_Y - 0.10, z),
                mats["chrome"],
                vertices=16,
            )
        )
    if include_contract_markers:
        objects.extend(
            module_contract_markers("podium", "default", PODIUM_HEIGHT)
        )
    return objects


def build_floor(
    mats: dict[str, bpy.types.Material],
    *,
    variant: str,
    include_contract_markers: bool = True,
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = [
        tbox(
            f"FireFloor_{variant}_CLTDeck",
            (35.48, DEPTH, 0.24),
            (2.25, 0.0, 0.12),
            mats["glulam"],
            0.018,
            tile_m=1.25,
        )
    ]
    front_openings = [
        (
            centre - 2.12,
            centre + 2.12,
            0.52,
            3.33,
        )
        for centre in UPPER_WINDOW_CENTRES
    ]
    rear_centres = (-11.80, -6.15, -0.50, 5.15, 11.40, 16.45)
    rear_openings = [
        (centre - 1.78, centre + 1.78, 0.58, 3.30)
        for centre in rear_centres
    ]
    for face, y, sign, openings in (
        ("Front", FRONT_Y + 1.42, -1, front_openings),
        ("Rear", REAR_Y, 1, rear_openings),
    ):
        objects.extend(
            add_y_wall(
                f"FireFloor{variant}{face}TimberWall",
                x0=MAIN_LEFT_X,
                x1=RIGHT_X,
                z0=0.0,
                z1=FLOOR_HEIGHT,
                surface_y=y,
                outward_sign=sign,
                openings=openings,
                mat=mats["timber"],
            )
        )
        objects.extend(
            add_vertical_battens_y(
                f"FireFloor{variant}{face}TimberSkin",
                x0=MAIN_LEFT_X + 0.10,
                x1=RIGHT_X - 0.10,
                height=FLOOR_HEIGHT,
                surface_y=y,
                outward_sign=sign,
                openings=openings,
                mat=mats["timber"],
                spacing=0.36,
            )
        )
    left_centres = (-6.3, 1.2, 8.7, 14.0)
    right_centres = (-13.7, -6.0, 2.0, 9.8, 14.4)
    left_openings = [
        (centre - 1.35, centre + 1.35, 0.64, 3.20)
        for centre in left_centres
        if centre > TOWER_REAR_Y + 1.5
    ]
    right_openings = [
        (centre - 1.35, centre + 1.35, 0.64, 3.20)
        for centre in right_centres
    ]
    for side, x, sign, y0, openings in (
        ("Left", MAIN_LEFT_X, -1, TOWER_REAR_Y, left_openings),
        ("Right", RIGHT_X, 1, FRONT_Y, right_openings),
    ):
        objects.extend(
            add_x_wall(
                f"FireFloor{variant}{side}TimberWall",
                y0=y0,
                y1=REAR_Y,
                z0=0.0,
                z1=FLOOR_HEIGHT,
                surface_x=x,
                outward_sign=sign,
                openings=openings,
                mat=mats["timber"],
            )
        )
        objects.extend(
            add_vertical_battens_x(
                f"FireFloor{variant}{side}TimberSkin",
                y0=y0 + 0.10,
                y1=REAR_Y - 0.10,
                height=FLOOR_HEIGHT,
                surface_x=x,
                outward_sign=sign,
                openings=openings,
                mat=mats["timber"],
                spacing=0.36,
            )
        )
    for index, centre in enumerate(UPPER_WINDOW_CENTRES):
        objects.extend(
            add_y_window(
                f"FireFloor{variant}FrontCrewWindow_{index}",
                centre_x=centre,
                sill_z=0.52,
                width=4.24,
                height=2.81,
                surface_y=FRONT_Y + 1.42,
                outward_sign=-1,
                mats=mats,
                variant=variant,
            )
        )
    for index, centre in enumerate(rear_centres):
        objects.extend(
            add_y_window(
                f"FireFloor{variant}RearCrewWindow_{index}",
                centre_x=centre,
                sill_z=0.58,
                width=3.56,
                height=2.72,
                surface_y=REAR_Y,
                outward_sign=1,
                mats=mats,
                variant=variant,
            )
        )
    for index, centre in enumerate(left_centres):
        if centre <= TOWER_REAR_Y + 1.5:
            continue
        objects.extend(
            add_x_window(
                f"FireFloor{variant}LeftCrewWindow_{index}",
                centre_y=centre,
                sill_z=0.64,
                width=2.70,
                height=2.56,
                surface_x=MAIN_LEFT_X,
                outward_sign=-1,
                mats=mats,
                variant=variant,
            )
        )
    for index, centre in enumerate(right_centres):
        objects.extend(
            add_x_window(
                f"FireFloor{variant}RightCrewWindow_{index}",
                centre_y=centre,
                sill_z=0.64,
                width=2.70,
                height=2.56,
                surface_x=RIGHT_X,
                outward_sign=1,
                mats=mats,
                variant=variant,
            )
        )
    objects.extend(add_upper_glulam_gallery(mats))
    objects.extend(
        add_tower_segment(
            f"FireFloor{variant}IntegratedTrainingTower",
            height=FLOOR_HEIGHT,
            mats=mats,
        )
    )
    # Minimal occupied furniture reads through separate glazing without making
    # the room-card photograph carry the whole depth illusion.
    desk_offsets = (
        (-9.8, -14.75),
        (-4.1, -14.75),
        (1.5, -14.75),
        (7.1, -14.75),
    )
    for index, (x, y) in enumerate(desk_offsets):
        objects.extend(
            [
                tbox(
                    f"FireFloor{variant}DayroomTable_{index}",
                    (1.40, 0.70, 0.08),
                    (x, y, 0.92),
                    mats["glulam"],
                    0.025,
                    tile_m=0.75,
                ),
                tbox(
                    f"FireFloor{variant}DayroomLamp_{index}",
                    (0.15, 0.15, 0.22),
                    (x + 0.44, y, 1.14),
                    mats["warm_light"],
                    0.018,
                    tile_m=0.5,
                ),
            ]
        )
    if include_contract_markers:
        objects.extend(module_contract_markers("floor", variant, FLOOR_HEIGHT))
    return objects


def build_crown(
    mats: dict[str, bpy.types.Material],
    *,
    include_contract_markers: bool = True,
) -> list[bpy.types.Object]:
    centre_x = (MAIN_LEFT_X + RIGHT_X) * 0.5
    main_width = RIGHT_X - MAIN_LEFT_X
    objects: list[bpy.types.Object] = [
        tbox(
            "FireCrownFrontGlulamDatum",
            (main_width, 0.38, CROWN_HEIGHT),
            (centre_x, FRONT_Y + 0.19, CROWN_HEIGHT * 0.5),
            mats["glulam"],
            0.018,
            tile_m=1.25,
        ),
        tbox(
            "FireCrownRearGlulamDatum",
            (main_width, 0.38, CROWN_HEIGHT),
            (centre_x, REAR_Y - 0.19, CROWN_HEIGHT * 0.5),
            mats["glulam"],
            0.018,
            tile_m=1.25,
        ),
        tbox(
            "FireCrownLeftTimberDatum",
            (0.38, DEPTH, CROWN_HEIGHT),
            (MAIN_LEFT_X + 0.19, 0.0, CROWN_HEIGHT * 0.5),
            mats["timber"],
            0.018,
            tile_m=1.25,
        ),
        tbox(
            "FireCrownRightTimberDatum",
            (0.38, DEPTH, CROWN_HEIGHT),
            (RIGHT_X - 0.19, 0.0, CROWN_HEIGHT * 0.5),
            mats["timber"],
            0.018,
            tile_m=1.25,
        ),
        tbox(
            "FireCrownFrontBlackFlashing",
            (main_width + 0.16, 0.48, 0.075),
            (centre_x, FRONT_Y + 0.16, CROWN_HEIGHT - 0.0375),
            mats["solar"],
            0.010,
            tile_m=0.55,
        ),
        tbox(
            "FireCrownRearBlackFlashing",
            (main_width + 0.16, 0.48, 0.075),
            (centre_x, REAR_Y - 0.16, CROWN_HEIGHT - 0.0375),
            mats["solar"],
            0.010,
            tile_m=0.55,
        ),
    ]
    objects.extend(
        add_tower_segment(
            "FireCrownIntegratedTowerBand",
            height=CROWN_HEIGHT,
            mats=mats,
            include_stairs=False,
        )
    )
    if include_contract_markers:
        objects.extend(
            module_contract_markers("crown", "crown", CROWN_HEIGHT)
        )
    return objects


def add_pv_array(
    name: str,
    *,
    centre_x: float,
    centre_y: float,
    columns: int,
    rows: int = 2,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    panel_w = 1.72
    panel_d = 1.02
    gap = 0.12
    for row in range(rows):
        y = centre_y + (row - (rows - 1) * 0.5) * (panel_d + gap)
        for index in range(columns):
            x = centre_x + (index - (columns - 1) * 0.5) * (
                panel_w + gap
            )
            panel = tbox(
                f"{name}_PhotovoltaicPanel_{row}_{index}",
                (panel_w, panel_d, 0.075),
                (x, y, 1.03),
                mats["solar"],
                0.012,
                tile_m=0.55,
            )
            panel.rotation_euler.x = math.radians(8.0)
            objects.append(panel)
            for side in (-1, 1):
                objects.append(
                    tbox(
                        f"{name}_Rack_{row}_{index}_{side:+d}",
                        (0.055, 0.46, 0.40),
                        (x + side * 0.58, y + 0.18, 0.78),
                        mats["frame"],
                        0.006,
                        tile_m=0.55,
                    )
                )
    return objects


def add_meadow_detail(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    for row in range(7):
        for column in range(15):
            x = -12.8 + column * 2.06 + (row % 2) * 0.28
            y = -13.0 + row * 4.08
            if -5.5 < y < 5.5 and -9.5 < x < 14.0:
                # Leave the photovoltaic maintenance zone comparatively clear.
                continue
            seed = row * 31 + column * 17
            height = 0.18 + (seed % 7) * 0.035
            tuft = cylinder(
                f"FireRoofNativeGrass_{row}_{column}",
                0.075,
                height,
                (x, y, 0.64 + height * 0.5),
                mats["plant_dark"],
                vertices=6,
                scale_xy=(1.0, 0.45),
            )
            objects.append(tuft)
            if seed % 3 == 0:
                flower_mat = (
                    mats["flower_yellow"]
                    if seed % 2
                    else mats["flower_purple"]
                )
                objects.append(
                    cylinder(
                        f"FireRoofWildflower_{row}_{column}",
                        0.055,
                        0.055,
                        (x, y, 0.67 + height),
                        flower_mat,
                        vertices=8,
                    )
                )
    return objects


def build_roof(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    centre_x = (MAIN_LEFT_X + RIGHT_X) * 0.5
    main_width = RIGHT_X - MAIN_LEFT_X
    objects: list[bpy.types.Object] = [
        tbox(
            "FireRoofCLTDeck",
            (main_width - 0.32, DEPTH - 0.34, 0.22),
            (centre_x, 0.0, 0.11),
            mats["glulam"],
            0.016,
            tile_m=1.25,
        ),
        tbox(
            "FireRoofMeadowBuildUp",
            (main_width - 1.00, DEPTH - 1.00, 0.38),
            (centre_x, 0.0, 0.41),
            mats["green_roof"],
            0.035,
            tile_m=1.35,
        ),
        tbox(
            "FireRoofFrontGravelBreak",
            (main_width - 0.70, 0.46, 0.12),
            (centre_x, FRONT_Y + 0.48, 0.66),
            mats["gravel"],
            0.018,
            tile_m=0.65,
        ),
        tbox(
            "FireRoofRearGravelBreak",
            (main_width - 0.70, 0.46, 0.12),
            (centre_x, REAR_Y - 0.48, 0.66),
            mats["gravel"],
            0.018,
            tile_m=0.65,
        ),
        tbox(
            "FireRoofFrontParapet",
            (main_width, 0.28, 0.72),
            (centre_x, FRONT_Y + 0.14, 0.36),
            mats["solar"],
            0.015,
            tile_m=0.55,
        ),
        tbox(
            "FireRoofRearParapet",
            (main_width, 0.28, 0.72),
            (centre_x, REAR_Y - 0.14, 0.36),
            mats["solar"],
            0.015,
            tile_m=0.55,
        ),
        tbox(
            "FireRoofLeftParapet",
            (0.28, DEPTH, 0.72),
            (MAIN_LEFT_X + 0.14, 0.0, 0.36),
            mats["solar"],
            0.015,
            tile_m=0.55,
        ),
        tbox(
            "FireRoofRightParapet",
            (0.28, DEPTH, 0.72),
            (RIGHT_X - 0.14, 0.0, 0.36),
            mats["solar"],
            0.015,
            tile_m=0.55,
        ),
        tbox(
            "FireRoofAccessHatch",
            (1.35, 1.65, 0.24),
            (15.45, 9.90, 0.78),
            mats["solar"],
            0.035,
            tile_m=0.55,
        ),
    ]
    objects.extend(
        add_pv_array(
            "FireRoofSouthPV",
            centre_x=1.2,
            centre_y=-3.25,
            columns=8,
            mats=mats,
        )
    )
    objects.extend(
        add_pv_array(
            "FireRoofNorthPV",
            centre_x=5.0,
            centre_y=3.55,
            columns=7,
            mats=mats,
        )
    )
    objects.extend(add_meadow_detail(mats))
    objects.extend(
        add_tower_segment(
            "FireRoofIntegratedTowerTop",
            height=3.16,
            mats=mats,
        )
    )
    centre_tower_x = (TOWER_LEFT_X + TOWER_RIGHT_X) * 0.5
    centre_tower_y = (TOWER_FRONT_Y + TOWER_REAR_Y) * 0.5
    tower_width = TOWER_RIGHT_X - TOWER_LEFT_X
    tower_depth = TOWER_REAR_Y - TOWER_FRONT_Y
    objects.extend(
        [
            tbox(
                "FireTowerTopDarkCap",
                (tower_width, tower_depth, 0.34),
                (centre_tower_x, centre_tower_y, 3.24),
                mats["solar"],
                0.025,
                tile_m=0.55,
            ),
            round_beam(
                "FireTowerBeaconMast",
                (centre_tower_x, centre_tower_y, 3.40),
                (centre_tower_x, centre_tower_y, 4.00),
                0.045,
                mats["frame"],
                vertices=10,
            ),
            cylinder(
                "FireTowerRedBeacon",
                0.12,
                0.24,
                (centre_tower_x, centre_tower_y, 4.02),
                mats["red"],
                vertices=16,
            ),
        ]
    )
    for index, (x, y) in enumerate(
        ((-11.8, -12.8), (17.0, -12.8), (-11.8, 12.8), (17.0, 12.8))
    ):
        objects.append(
            cylinder(
                f"FireRoofDrain_{index}",
                0.12,
                0.08,
                (x, y, 0.69),
                mats["frame"],
                vertices=16,
            )
        )
    return objects


def build_band(
    role: str,
    variant: str,
    mats: dict[str, bpy.types.Material],
    *,
    include_contract_markers: bool = True,
) -> list[bpy.types.Object]:
    if role == "podium":
        return build_podium(
            mats,
            include_contract_markers=include_contract_markers,
        )
    if role == "floor":
        return build_floor(
            mats,
            variant=variant,
            include_contract_markers=include_contract_markers,
        )
    if role == "crown":
        return build_crown(
            mats,
            include_contract_markers=include_contract_markers,
        )
    if role == "roof":
        return build_roof(mats)
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
        ("floor", "typical_a", PODIUM_HEIGHT),
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
        ("podium", "default", PODIUM_HEIGHT),
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
    scene.view_settings.exposure = 0.64
    background = scene.world.node_tree.nodes.get("Background")
    if background:
        background.inputs["Color"].default_value = (0.46, 0.48, 0.50, 1.0)
        background.inputs["Strength"].default_value = 0.90
    ground = bpy.data.materials.get("MAT_W3_Ground")
    if ground and ground.use_nodes:
        ground.node_tree.nodes["Principled BSDF"].inputs[
            "Base Color"
        ].default_value = (0.37, 0.36, 0.33, 1.0)
    bpy.ops.object.light_add(type="SUN", location=(-48.0, -66.0, 78.0))
    sun = bpy.context.object
    sun.name = "PRESENTATION_W10_FireStationSoftSun"
    sun.data.energy = 1.82
    sun.data.color = (1.0, 0.88, 0.74)
    sun.data.angle = math.radians(10.0)
    sun.rotation_euler = (
        Vector((0.0, 0.0, 4.5)) - sun.location
    ).to_track_quat("-Z", "Y").to_euler()
    views = {
        "preview": ((-44.0, -62.0, 16.5), (0.0, 0.0, 5.2), 46),
        "street": ((0.0, -62.0, 5.6), (0.0, -11.5, 4.8), 42),
        "front_corner_oblique": (
            (-44.0, -58.0, 14.0),
            (0.0, 0.0, 5.2),
            47,
        ),
        "rear_corner_oblique": (
            (35.0, 48.0, 15.0),
            (0.0, 0.8, 5.0),
            54,
        ),
        "aerial": ((35.0, -40.0, 38.0), (0.0, 0.0, 4.6), 54),
        "facade_close": ((0.0, -54.0, 5.2), (0.0, -15.4, 4.6), 62),
        "apparatus_close": ((0.0, -36.0, 3.6), (0.1, -16.4, 2.1), 65),
        "tower_close": (
            (-31.0, -38.0, 10.0),
            (-17.7, -14.5, 6.5),
            52,
        ),
        "roof_close": ((18.0, -20.0, 29.0), (3.0, 0.5, 9.8), 58),
        "side_close": ((48.0, 0.0, 8.0), (17.5, 0.0, 5.0), 60),
        "context": ((38.0, -52.0, 22.0), (0.0, 0.0, 5.2), 58),
    }
    selected = (
        {
            "preview",
            "street",
            "front_corner_oblique",
            "aerial",
            "apparatus_close",
            "tower_close",
            "rear_corner_oblique",
        }
        if view_set == "pilot"
        else set(views)
    )
    snapshots: list[
        tuple[bpy.types.Material, bpy.types.Node, float, float, str, tuple]
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
        if mat.get("channel_glass"):
            colour = (0.14, 0.19, 0.19, 1.0)
            alpha = 0.30
        else:
            colour = (0.035, 0.060, 0.065, 1.0)
            alpha = 0.32
        bsdf.inputs["Base Color"].default_value = colour
        bsdf.inputs["Alpha"].default_value = alpha
        mat.diffuse_color = (*colour[:3], alpha)
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
            "The operational identity is one three-lane apparatus bar with an "
            "integrated tower and crew wing. A rectangle preserves the canonical "
            "station; L- and U-shaped user drawings turn complete station bars "
            "around service/training yards while each primary bar keeps its "
            "three unscaled doors, real lane depth and public entrance."
        ),
        "fixedLandmarkScaleBand": {
            "scaleMin": 0.70,
            "scaleMax": 1.35,
            "maxAxisRatio": 1.34,
        },
        "recommendedWidth_m": [28, 58],
        "recommendedDepth_m": [25, 50],
        "recommendedFloors": [1, 3],
        "wingDepth_m": [24, 38],
        "preferredBayMultiple_m": 7.50,
        "profiles": {
            "rectangle": {
                "recommendedWidth_m": [28, 58],
                "recommendedDepth_m": [25, 50],
                "recommendedFloors": [1, 3],
                "preferredBayMultiple_m": 7.50,
            },
            "l_shape": {
                "recommendedWidth_m": [34, 74],
                "recommendedDepth_m": [30, 62],
                "recommendedFloors": [1, 3],
                "wingDepth_m": [24, 38],
                "preferredBayMultiple_m": 7.50,
            },
            "u_shape": {
                "recommendedWidth_m": [40, 84],
                "recommendedDepth_m": [34, 68],
                "recommendedFloors": [1, 3],
                "wingDepth_m": [24, 38],
                "minimumCourtyard_m": 16.0,
                "preferredBayMultiple_m": 7.50,
            },
        },
        "notes": [
            "Keep exactly three apparatus openings on every primary station bar.",
            "Keep the public entry and integrated training tower together.",
            "Repeat complete station bars for oversized targets; never stretch one door.",
            "Preserve real drive-through depth and align front/rear lane doors.",
            "Keep meadow roof, photovoltaic arrays and tower cap in the roof role.",
        ],
    }


def provenance() -> dict:
    return {
        "kind": (
            "catalogue_brief_plus_built_precedent_research_and_original_"
            "imagegen_multiview_package"
        ),
        "catalogue_archetype_id": ARCHETYPE_ID,
        "catalogue_variant_id": VARIANT_ID,
        "goalpost_local_source": "textures/source/archetype-goalpost.png",
        "orthographic_elevation": (
            "textures/source/front-elevation-source-v1.png"
        ),
        "aerial_reference": "textures/source/aerial-roof-source-v1.png",
        "rear_reference": "textures/source/rear-service-source-v1.png",
        "material_reference": (
            "textures/source/material-construction-source-v1.png"
        ),
        "glazing_reference": (
            "textures/source/glazing-occupied-depth-source-v1.png"
        ),
        "tower_reference": (
            "textures/source/integrated-training-tower-source-v1.png"
        ),
        "reference_generation": "textures/source/reference-generation.json",
        "registered_openings": "textures/source/registered-openings.json",
        "registered_bands": "textures/source/registered-bands.json",
        "elevation_source": f"/families/{FAMILY}/elevation.jpg",
        "skin_manifest": "textures/skin_manifest.json",
        "generator": (
            "tools/archetype_compiler/generate_wave10_fire_station_family.py"
        ),
        "reference_method": (
            "built-station research, canonical goalpost, rectified front, "
            "aerial roof proof, complete rear drive-through source, dedicated "
            "material construction sheet, physical glazing/depth source, "
            "integrated tower/stair source and finite multiscale comparison"
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
            "The source pack fixes exactly three transparent drive-through "
            "apparatus lanes, the integrated inhabited tower, public glulam "
            "entry, occupied timber crew gallery, charred service spine and "
            "planted photovoltaic roof."
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
            "fixed_end_bays": ["tower_entry", "service_spine"],
            "repeatable_middle_bays": [1, 2, 3],
            "middle_variants": ["typical_a", "typical_b", "typical_c"],
            "rule": (
                "Repeat complete occupied crew bands vertically and complete "
                "three-lane station bars horizontally. Never deform an "
                "apparatus door, tower stair, public entry or lane depth."
            ),
        },
        "delivery": {
            "near_atlas_width_px": 2048,
            "far_atlas_width_px": 1024,
            "near_usage": (
                "true-scale timber, glulam, charred wood, concrete, meadow and "
                "metal plus physical doors, panes, apparatus, rooms and stairs"
            ),
            "far_usage": "city-scale render-locked archetype material reference",
        },
        "assembly_contract": {
            "fixed": [
                "podium/entrance",
                "corner returns",
                "crown",
                "roof",
                "three drive-through apparatus lanes",
                "three front and three rear four-fold doors",
                "integrated training tower and stair",
                "public glulam entry porch",
                "charred service spine",
                "meadow roof and photovoltaic arrays",
            ],
            "repeatable": ["typical_a", "typical_b", "typical_c"],
            "side_elevations": (
                "Honey timber or charred rainscreen, occupied windows, concrete "
                "tower walls, deep returns, drainage, service doors and roof "
                "flashings continue around both side and rear elevations."
            ),
            "elevation_coverage": {
                "front": (
                    "tower, public entry, exactly three apparatus doors, "
                    "occupied timber crew gallery and charred service wing"
                ),
                "left": "integrated stair tower plus occupied timber crew return",
                "right": "charred service base and occupied timber crew return",
                "rear": (
                    "three aligned drive-through doors, decontamination, "
                    "service doors and occupied crew rooms"
                ),
                "roof": (
                    "native meadow, gravel breaks, drains, two photovoltaic "
                    "arrays, roof hatch and tower beacon"
                ),
            },
            "variation_policy": (
                "One to three levels use semantic stack bands. Mild full-envelope "
                "scaling is safe; larger drawings repeat complete station bars."
            ),
        },
        "assets": {
            "skin_manifest": "textures/skin_manifest.json",
            "source": skin["source"],
            "near": skin["zones"]["honey_timber"]["near"],
            "far": skin["zones"]["honey_timber"]["far"],
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
            "height_m": PODIUM_HEIGHT,
        },
        {
            "role": "floor",
            "variant_key": "typical_a",
            "level": 1,
            "z_m": PODIUM_HEIGHT,
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
        "source_variant_id": VARIANT_ID,
        "generation_archetype_id": VARIANT_ID,
        "footprint_target": {
            "width_m": WIDTH,
            "depth_m": DEPTH,
            "wing_depth_m": DEPTH,
            "segments": [
                {
                    "id": "three_lane_station_bar",
                    "centre_x_m": 0.0,
                    "centre_y_m": 0.0,
                    "length_m": WIDTH,
                    "thickness_m": DEPTH,
                    "rotation_degrees": 0.0,
                }
            ],
        },
        "massing_graph": {
            "type": "three_lane_mass_timber_fire_station",
            "apparatus_lanes": 3,
            "drive_through": True,
            "integrated_training_tower": True,
            "occupied_crew_gallery": True,
            "charred_service_spine": True,
            "native_meadow_roof": True,
            "photovoltaic_arrays": 2,
        },
        "texture_keys": sorted(skin["zones"]),
        "ao_baked": True,
    }
    dimensions = {
        "width_m": WIDTH,
        "depth_m": DEPTH,
        "wing_depth_m": DEPTH,
        "podium_height_m": PODIUM_HEIGHT,
        "floor_height_m": FLOOR_HEIGHT,
        "setback_height_m": FLOOR_HEIGHT,
        "crown_height_m": CROWN_HEIGHT,
        "roof_height_m": ROOF_HEIGHT,
        "total_height_m": TOTAL_HEIGHT,
        "native_floors": 2,
        "min_floors": 1,
        "max_floors": 3,
        "default_floors": 2,
    }
    identity = (
        "A welcoming two-storey mass-timber fire station reads as one civic "
        "working building through three transparent drive-through apparatus "
        "bays, a honey-toned glulam crew wing, a charred service spine, an "
        "inhabited channel-glass training tower and a planted photovoltaic roof."
    )
    material_zones = (
        "warm honey vertical timber rainscreen and exposed glulam; tactile "
        "charred shou sugi ban; pale board-formed concrete; black thermally "
        "broken frames; physical neutral low-e and translucent channel glass; "
        "red apparatus; native meadow roof, gravel breaks and dark photovoltaics"
    )
    source = provenance()
    manifest = {
        "manifest_schema": 3,
        "grammar_schema_version": 3,
        "generator": {
            "name": (
                "archetype_compiler/generate_wave10_fire_station_family.py"
            ),
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
        "aesthetic_category_id": "eco_urban_green_architecture",
        "development_type": "civic_institutional",
        "reuse_keys": [
            ARCHETYPE_ID,
            VARIANT_ID,
            "Modern Fire Station",
            "Mass Timber Fire Station",
            "Mass Timber Fire Hall",
            "CLT Fire Hall",
            "Emergency Services Station",
        ],
        "generation_tags": [
            "wave10_essential_family",
            "civic_institutional",
            "fire_station",
            "mass_timber",
            "custom_pbr_skin",
            "physical_glazing",
            "reference_locked",
            "three_drive_through_apparatus_lanes",
            "integrated_training_tower",
            "real_stair_flights_and_landings",
            "occupied_glulam_crew_gallery",
            "charred_timber_service_spine",
            "native_meadow_green_roof",
            "photovoltaic_arrays",
            "rear_decontamination_service",
        ],
        "footprint_compatibility": footprint,
        "coordinate_contract": COORDINATE_CONTRACT,
        "textures": texture_inventory(skin),
        "facade_sheet": facade_contract(skin),
        "massing_graph": {
            "type": "three_lane_mass_timber_fire_station",
            "silhouette": (
                "horizontal_two_storey_timber_crew_bar_over_three_glazed_bays_"
                "with_integrated_left_training_tower_and_meadow_roof"
            ),
            "render_locked": True,
            "goalpost": (
                f"/families/{FAMILY}/textures/source/archetype-goalpost.png"
            ),
            "fallback": "complete_three_lane_station_bar_streetwall",
            "apparatus_lanes": 3,
            "drive_through": True,
            "integrated_training_tower": True,
        },
        "material_budget": {
            "max_assembled_materials": 22,
            "rationale": (
                "Custom timber/concrete/green-roof PBR, separate physical "
                "glazing, apparatus, stair, metal and restrained occupied-depth "
                "materials remain semantically distinct."
            ),
        },
        "dimensions": dimensions,
        "native_width_m": WIDTH,
        "native_depth_m": DEPTH,
        "native_floors": 2,
        "min_floors": 1,
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
                "three_drive_through_apparatus_lanes",
                "three_front_and_three_rear_four_fold_glass_doors",
                "three_physical_red_engines",
                "integrated_training_tower",
                "real_stair_flights_and_landings",
                "recessed_public_glulam_entry",
                "occupied_honey_timber_crew_gallery",
                "charred_service_spine",
                "board_formed_concrete_piers",
                "native_meadow_green_roof",
                "two_photovoltaic_arrays",
                "rear_decontamination_service",
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
        f"[wave10-fire] {FAMILY}: {fixed_triangles} triangles, "
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
    print(f"[wave10-fire-render] {FAMILY}: {len(manifest['renders'])} renders")


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
