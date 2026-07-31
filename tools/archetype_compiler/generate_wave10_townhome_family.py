"""Author the Wave 10 Cedar & Black-Metal missing-middle townhome family.

The canonical assembly is four complete seven-metre homes.  Its LEGO fallback
keeps the entrance floor, two occupied upper variants, parapet and private
roof-terrace system semantic, while the planner may repeat whole dwelling bars
for user-drawn widths.

Run with Blender 5.x from the repository root:

    blender --background --factory-startup --python \
      tools/archetype_compiler/generate_wave10_townhome_family.py -- \
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
)
from generate_wave10_courtyard_family import (  # noqa: E402
    evaluated_triangle_count,
    material_count,
    tbox,
)


FAMILY = "rndsqr-cedar-black-townhomes"
ARCHETYPE_ID = "rndsqr_missing_middle_townhomes"
VARIANT_ID = "rndsqr_townhome_dark_wood_metal"
LABEL = "RNDSQR Missing-Middle Townhomes — Cedar & Black-Metal Row"
GLASS_PROFILE = "residential_low_e"

WIDTH = 28.0
DEPTH = 14.0
UNIT_WIDTH = 7.0
FLOOR_HEIGHT = 3.0
BODY_HEIGHT = FLOOR_HEIGHT * 3.0
CROWN_HEIGHT = 0.40
ROOF_HEIGHT = 2.45
TOTAL_HEIGHT = BODY_HEIGHT + CROWN_HEIGHT + ROOF_HEIGHT
FRONT_Y = (-6.45, -6.00, -6.45, -6.00)
REAR_Y = 6.45
WALL_THICKNESS = 0.24
UNIT_CENTRES = (-10.5, -3.5, 3.5, 10.5)
UNIT_BOUNDS = tuple(
    (-WIDTH / 2.0 + index * UNIT_WIDTH, -WIDTH / 2.0 + (index + 1) * UNIT_WIDTH)
    for index in range(4)
)


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
        "cedar": pbr_material(
            "MAT_W10_TOWN_CedarRainscreen",
            folder,
            near["cedar"],
            "cedar",
            saturation=0.90,
            value=0.86,
        ),
        "metal": pbr_material(
            "MAT_W10_TOWN_FineCharcoalCorrugatedMetal",
            folder,
            near["metal"],
            "metal",
            metallic=0.62,
            saturation=0.70,
            value=0.54,
        ),
        "concrete": pbr_material(
            "MAT_W10_TOWN_WarmGreyConcrete",
            folder,
            near["concrete"],
            "concrete",
            saturation=0.66,
            value=0.90,
        ),
        "roof": pbr_material(
            "MAT_W10_TOWN_DarkMembraneRoof",
            folder,
            near["roof"],
            "roof",
            saturation=0.58,
            value=0.58,
        ),
        "paving": pbr_material(
            "MAT_W10_TOWN_TerracePaving",
            folder,
            near["paving"],
            "paving",
            saturation=0.48,
            value=0.25,
        ),
        "facade": pbr_material(
            "MAT_W10_TOWN_RegisteredElevationProof",
            folder,
            near["facade"],
            "facade",
            saturation=0.90,
            value=0.94,
        ),
        "glass": profiled_glass_material(
            "MAT_W10_TOWN_PhysicalResidentialLowE",
            GLASS_PROFILE,
            tint="#1d292d",
            roughness_scale=1.30,
            transmission_scale=0.76,
        ),
        "underlay": reference_image_material(
            "MAT_W10_TOWN_RegisteredOccupiedDepth",
            folder,
            skin["sources"]["reference_underlay"],
            emission_strength=0.070,
        ),
        "deep": material(
            "MAT_W10_TOWN_DeepConstructionCavity",
            (0.012, 0.014, 0.014, 1.0),
            0.95,
        ),
        "door": material(
            "MAT_W10_TOWN_MatteBlackDoor",
            (0.025, 0.027, 0.027, 1.0),
            0.46,
            metallic=0.18,
        ),
        "terrace": material(
            "MAT_W10_TOWN_CharcoalTerraceMembrane",
            (0.075, 0.078, 0.078, 1.0),
            0.88,
        ),
        "curtain": material(
            "MAT_W10_TOWN_LinenCurtain",
            (0.44, 0.42, 0.37, 1.0),
            0.88,
        ),
        "plant": material(
            "MAT_W10_TOWN_RestrainedPlanting",
            (0.085, 0.13, 0.072, 1.0),
            0.92,
        ),
    }
    # Room cards use a modular 4x4 atlas.  Repeat it across physical cards;
    # CLIP would turn true-scale UV coordinates outside 0..1 into flat black.
    for node in mats["underlay"].node_tree.nodes:
        if node.bl_idname == "ShaderNodeTexImage":
            node.extension = "REPEAT"
    mats["glass"]["glazing_lod"] = "always"
    mats["glass"]["reference_locked"] = True
    mats["glass"]["source_variant_id"] = VARIANT_ID
    mats["underlay"]["glazing_profile"] = GLASS_PROFILE
    mats["underlay"]["source_variant_id"] = VARIANT_ID
    return mats, skin


def front_material(unit_index: int) -> str:
    return "metal" if unit_index % 2 == 0 else "cedar"


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
            f"{name}_Wall_{index}",
            (rx1 - rx0, WALL_THICKNESS, rz1 - rz0),
            (
                (rx0 + rx1) * 0.5,
                surface_y + inside * WALL_THICKNESS * 0.5,
                (rz0 + rz1) * 0.5,
            ),
            mat,
            0.012,
            tile_m=1.25,
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
            f"{name}_Wall_{index}",
            (WALL_THICKNESS, ry1 - ry0, rz1 - rz0),
            (
                surface_x + inside * WALL_THICKNESS * 0.5,
                (ry0 + ry1) * 0.5,
                (rz0 + rz1) * 0.5,
            ),
            mat,
            0.012,
            tile_m=1.25,
        )
        for index, (ry0, ry1, rz0, rz1) in enumerate(
            rectangles_around_openings(y0, y1, z0, z1, openings)
        )
    ]


def add_y_window(
    name: str,
    *,
    centre_x: float,
    sill_z: float,
    width: float,
    height: float,
    surface_y: float,
    outward_sign: int,
    reveal_mat: bpy.types.Material,
    mats: dict[str, bpy.types.Material],
    mullions: int = 1,
    privacy_side: int = 0,
    juliet: bool = False,
) -> list[bpy.types.Object]:
    inside = -outward_sign
    x0, x1 = centre_x - width / 2.0, centre_x + width / 2.0
    z0, z1 = sill_z, sill_z + height
    reveal_y = surface_y + inside * 0.18
    pane_y = surface_y + inside * 0.34
    room_y = surface_y + inside * 0.46
    frame = 0.075
    objects = [
        tbox(
            f"{name}_LeftReveal",
            (0.12, 0.38, height),
            (x0 + 0.06, reveal_y, (z0 + z1) / 2.0),
            reveal_mat,
            0.008,
            tile_m=0.9,
        ),
        tbox(
            f"{name}_RightReveal",
            (0.12, 0.38, height),
            (x1 - 0.06, reveal_y, (z0 + z1) / 2.0),
            reveal_mat,
            0.008,
            tile_m=0.9,
        ),
        tbox(
            f"{name}_HeadReveal",
            (width, 0.38, 0.12),
            (centre_x, reveal_y, z1 - 0.06),
            reveal_mat,
            0.008,
            tile_m=0.9,
        ),
        tbox(
            f"{name}_SillReveal",
            (width, 0.40, 0.12),
            (centre_x, reveal_y, z0 + 0.06),
            mats["metal"],
            0.008,
            tile_m=0.55,
        ),
        tbox(
            f"{name}_OccupiedDepth",
            (width - 0.20, 0.025, height - 0.20),
            (centre_x, room_y, (z0 + z1) / 2.0),
            mats["underlay"],
            0.004,
            tile_m=1.0,
        ),
        tbox(
            f"{name}_PhysicalLowEPane",
            (width - 0.18, 0.032, height - 0.18),
            (centre_x, pane_y, (z0 + z1) / 2.0),
            mats["glass"],
            0.005,
            tile_m=1.0,
        ),
        tbox(
            f"{name}_LeftFrame",
            (frame, 0.105, height - 0.06),
            (x0 + frame / 2.0, pane_y - inside * 0.025, (z0 + z1) / 2.0),
            mats["metal"],
            0.006,
            tile_m=0.5,
        ),
        tbox(
            f"{name}_RightFrame",
            (frame, 0.105, height - 0.06),
            (x1 - frame / 2.0, pane_y - inside * 0.025, (z0 + z1) / 2.0),
            mats["metal"],
            0.006,
            tile_m=0.5,
        ),
        tbox(
            f"{name}_TopFrame",
            (width, 0.105, frame),
            (centre_x, pane_y - inside * 0.025, z1 - frame / 2.0),
            mats["metal"],
            0.006,
            tile_m=0.5,
        ),
        tbox(
            f"{name}_BottomFrame",
            (width, 0.105, frame),
            (centre_x, pane_y - inside * 0.025, z0 + frame / 2.0),
            mats["metal"],
            0.006,
            tile_m=0.5,
        ),
    ]
    for index in range(1, mullions + 1):
        mx = x0 + width * index / (mullions + 1)
        objects.append(
            tbox(
                f"{name}_Mullion_{index}",
                (0.060, 0.112, height - 0.12),
                (mx, pane_y - inside * 0.032, (z0 + z1) / 2.0),
                mats["metal"],
                0.005,
                tile_m=0.5,
            )
        )
    # A low operable lite is physically framed within the first pane rather
    # than painted into the glass.  This small scale cue prevents the wide
    # openings from reading as commercial curtain wall.
    transom_width = max(0.48, width / (mullions + 1) - 0.12)
    transom_x = x0 + transom_width / 2.0 + 0.08
    objects.append(
        tbox(
            f"{name}_OperableLiteTransom",
            (transom_width, 0.112, 0.052),
            (transom_x, pane_y - inside * 0.032, z0 + min(0.46, height * 0.28)),
            mats["metal"],
            0.005,
            tile_m=0.5,
        )
    )
    if sum(ord(char) for char in name) % 3 != 0:
        objects.append(
            tbox(
                f"{name}_PartialLinenCurtain",
                (max(0.28, width * 0.22), 0.018, height * 0.72),
                (
                    centre_x - width * 0.27,
                    room_y - inside * 0.022,
                    z0 + height * 0.57,
                ),
                mats["curtain"],
                0.003,
                tile_m=0.8,
            )
        )
    if privacy_side:
        side_x = x1 - 0.44 if privacy_side > 0 else x0 + 0.44
        for fin_index in range(8):
            objects.append(
                tbox(
                    f"{name}_CedarPrivacyFin_{fin_index}",
                    (0.036, 0.14, height - 0.08),
                    (
                        side_x + privacy_side * (fin_index - 3.5) * 0.095,
                        surface_y + outward_sign * 0.075,
                        (z0 + z1) / 2.0,
                    ),
                    mats["cedar"],
                    0.006,
                    tile_m=0.7,
                )
            )
    if juliet:
        guard_y = surface_y + outward_sign * 0.18
        guard_width = 1.26 if privacy_side else min(width + 0.18, 3.65)
        guard_centre = (
            x0 + guard_width / 2.0 + 0.04
            if privacy_side < 0
            else x1 - guard_width / 2.0 - 0.04
            if privacy_side > 0
            else centre_x
        )
        guard_bottom = z0 + 0.08
        guard_top = z0 + 1.08
        objects.extend(
            [
                tbox(
                    f"{name}_JulietTopRail",
                    (guard_width, 0.065, 0.065),
                    (guard_centre, guard_y, guard_top),
                    mats["metal"],
                    0.012,
                    tile_m=0.5,
                ),
                tbox(
                    f"{name}_JulietBottomRail",
                    (guard_width, 0.055, 0.055),
                    (guard_centre, guard_y, guard_bottom),
                    mats["metal"],
                    0.010,
                    tile_m=0.5,
                ),
            ]
        )
        for bar_index in range(11):
            bx = guard_centre - guard_width / 2.0 + guard_width * bar_index / 10.0
            objects.append(
                tbox(
                    f"{name}_JulietBar_{bar_index}",
                    (0.032, 0.045, guard_top - guard_bottom),
                    (bx, guard_y, (guard_top + guard_bottom) / 2.0),
                    mats["metal"],
                    0.007,
                    tile_m=0.5,
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
    reveal_mat: bpy.types.Material,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    inside = -outward_sign
    y0, y1 = centre_y - width / 2.0, centre_y + width / 2.0
    z0, z1 = sill_z, sill_z + height
    reveal_x = surface_x + inside * 0.18
    pane_x = surface_x + inside * 0.34
    room_x = surface_x + inside * 0.46
    frame = 0.075
    return [
        tbox(
            f"{name}_NearReveal",
            (0.38, 0.12, height),
            (reveal_x, y0 + 0.06, (z0 + z1) / 2.0),
            reveal_mat,
            0.008,
            tile_m=0.9,
        ),
        tbox(
            f"{name}_FarReveal",
            (0.38, 0.12, height),
            (reveal_x, y1 - 0.06, (z0 + z1) / 2.0),
            reveal_mat,
            0.008,
            tile_m=0.9,
        ),
        tbox(
            f"{name}_HeadReveal",
            (0.38, width, 0.12),
            (reveal_x, centre_y, z1 - 0.06),
            reveal_mat,
            0.008,
            tile_m=0.9,
        ),
        tbox(
            f"{name}_SillReveal",
            (0.40, width, 0.12),
            (reveal_x, centre_y, z0 + 0.06),
            mats["metal"],
            0.008,
            tile_m=0.5,
        ),
        tbox(
            f"{name}_OccupiedDepth",
            (0.025, width - 0.20, height - 0.20),
            (room_x, centre_y, (z0 + z1) / 2.0),
            mats["underlay"],
            0.004,
            tile_m=1.0,
        ),
        tbox(
            f"{name}_PhysicalLowEPane",
            (0.032, width - 0.18, height - 0.18),
            (pane_x, centre_y, (z0 + z1) / 2.0),
            mats["glass"],
            0.005,
            tile_m=1.0,
        ),
        tbox(
            f"{name}_NearFrame",
            (0.105, frame, height - 0.06),
            (pane_x - inside * 0.025, y0 + frame / 2.0, (z0 + z1) / 2.0),
            mats["metal"],
            0.006,
            tile_m=0.5,
        ),
        tbox(
            f"{name}_FarFrame",
            (0.105, frame, height - 0.06),
            (pane_x - inside * 0.025, y1 - frame / 2.0, (z0 + z1) / 2.0),
            mats["metal"],
            0.006,
            tile_m=0.5,
        ),
        tbox(
            f"{name}_TopFrame",
            (0.105, width, frame),
            (pane_x - inside * 0.025, centre_y, z1 - frame / 2.0),
            mats["metal"],
            0.006,
            tile_m=0.5,
        ),
        tbox(
            f"{name}_BottomFrame",
            (0.105, width, frame),
            (pane_x - inside * 0.025, centre_y, z0 + frame / 2.0),
            mats["metal"],
            0.006,
            tile_m=0.5,
        ),
        tbox(
            f"{name}_CentreMullion",
            (0.11, 0.060, height - 0.12),
            (pane_x - inside * 0.032, centre_y, (z0 + z1) / 2.0),
            mats["metal"],
            0.005,
            tile_m=0.5,
        ),
    ]


def add_front_entry(
    name: str,
    *,
    centre_x: float,
    surface_y: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    width = 1.22
    z0, z1 = 0.24, 2.64
    inside = 1.0
    reveal_y = surface_y + inside * 0.24
    door_y = surface_y + inside * 0.46
    objects = [
        tbox(
            f"{name}_LeftCedarJamb",
            (0.16, 0.52, z1 - z0),
            (centre_x - width / 2.0 + 0.08, reveal_y, (z0 + z1) / 2.0),
            mats["cedar"],
            0.008,
            tile_m=0.85,
        ),
        tbox(
            f"{name}_RightCedarJamb",
            (0.16, 0.52, z1 - z0),
            (centre_x + width / 2.0 - 0.08, reveal_y, (z0 + z1) / 2.0),
            mats["cedar"],
            0.008,
            tile_m=0.85,
        ),
        tbox(
            f"{name}_CedarHead",
            (width, 0.52, 0.16),
            (centre_x, reveal_y, z1 - 0.08),
            mats["cedar"],
            0.008,
            tile_m=0.85,
        ),
        tbox(
            f"{name}_MatteBlackDoor",
            (width - 0.22, 0.055, z1 - z0 - 0.18),
            (centre_x, door_y, (z0 + z1) / 2.0 - 0.01),
            mats["door"],
            0.018,
            tile_m=0.8,
        ),
        tbox(
            f"{name}_SlimBlackCanopy",
            (1.70, 0.96, 0.12),
            (centre_x, surface_y - 0.42, 2.70),
            mats["metal"],
            0.025,
            tile_m=0.6,
        ),
        tbox(
            f"{name}_ConcreteThreshold",
            (1.44, 0.50, 0.12),
            (centre_x, surface_y - 0.18, 0.18),
            mats["concrete"],
            0.018,
            tile_m=0.85,
        ),
    ]
    for index, (depth, centre_y, height, span) in enumerate(
        (
            (0.42, surface_y - 0.43, 0.24, 1.52),
            (0.34, surface_y - 0.69, 0.16, 1.66),
            (0.22, surface_y - 0.89, 0.08, 1.80),
        )
    ):
        objects.append(
            tbox(
                f"{name}_IntegratedStoopStep_{index}",
                (span, depth, height),
                (centre_x, centre_y, height / 2.0),
                mats["concrete"],
                0.025,
                tile_m=0.85,
            )
        )
    objects.extend(
        [
            cylinder(
                f"{name}_DoorPull",
                0.022,
                0.54,
                (centre_x + 0.34, door_y - 0.045, 1.42),
                mats["metal"],
                vertices=12,
            ),
            tbox(
                f"{name}_AddressLightBox",
                (0.15, 0.10, 0.32),
                (centre_x + 0.88, surface_y - 0.07, 1.60),
                mats["metal"],
                0.018,
                tile_m=0.5,
            ),
        ]
    )
    return objects


def add_rear_service_door(
    name: str,
    *,
    centre_x: float,
    surface_y: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    door_y = surface_y - 0.38
    width, height = 0.88, 2.25
    return [
        tbox(
            f"{name}_Door",
            (width, 0.055, height),
            (centre_x, door_y, 1.25),
            mats["door"],
            0.012,
            tile_m=0.7,
        ),
        tbox(
            f"{name}_GlazedLite",
            (0.46, 0.026, 1.26),
            (centre_x, door_y + 0.035, 1.50),
            mats["glass"],
            0.006,
            tile_m=0.7,
        ),
    ]


def add_rear_garage(
    name: str,
    *,
    centre_x: float,
    surface_y: float,
    width: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    door_y = surface_y - 0.34
    height = 2.42
    objects = [
        tbox(
            f"{name}_InsulatedDoor",
            (width - 0.18, 0.060, height - 0.16),
            (centre_x, door_y, 0.16 + (height - 0.16) / 2.0),
            mats["door"],
            0.015,
            tile_m=0.8,
        )
    ]
    for index in range(1, 5):
        z = 0.16 + (height - 0.16) * index / 5.0
        objects.append(
            tbox(
                f"{name}_HorizontalPanelJoint_{index}",
                (width - 0.25, 0.025, 0.025),
                (centre_x, door_y + 0.045, z),
                mats["metal"],
                0.004,
                tile_m=0.5,
            )
        )
    return objects


def front_schedule(
    unit_index: int,
    role: str,
    variant: str,
) -> list[dict[str, float | int | bool]]:
    x0, _ = UNIT_BOUNDS[unit_index]
    if role == "podium":
        return [
            {
                "kind": 0,
                "x": x0 + 1.58,
                "w": 1.22,
                "sill": 0.24,
                "h": 2.40,
            },
            {
                "kind": 1,
                "x": x0 + 5.25,
                "w": 0.86,
                "sill": 0.66,
                "h": 1.55,
                "mullions": 0,
            },
        ]
    if variant == "typical_a":
        if unit_index % 2 == 0:
            return [
                {
                    "kind": 1,
                    "x": x0 + 3.48,
                    "w": 3.75,
                    "sill": 0.46,
                    "h": 2.10,
                    "mullions": 2,
                }
            ]
        return [
            {
                "kind": 1,
                "x": x0 + 3.68,
                "w": 3.18,
                "sill": 0.46,
                "h": 2.10,
                "mullions": 1,
                "privacy": -1,
                "juliet": True,
            }
        ]
    if variant == "typical_c":
        if unit_index % 2 == 0:
            return [
                {
                    "kind": 1,
                    "x": x0 + 3.18,
                    "w": 3.32,
                    "sill": 0.64,
                    "h": 1.82,
                    "mullions": 1,
                }
            ]
        return [
            {
                "kind": 1,
                "x": x0 + 3.82,
                "w": 3.48,
                "sill": 0.54,
                "h": 1.94,
                "mullions": 1,
                "privacy": -1,
            }
        ]
    if unit_index % 2 == 0:
        return [
            {
                "kind": 1,
                "x": x0 + 3.62,
                "w": 3.82,
                "sill": 0.50,
                "h": 1.98,
                "mullions": 1,
                "privacy": 1,
            }
        ]
    return [
        {
            "kind": 1,
            "x": x0 + 3.55,
            "w": 3.95,
            "sill": 0.50,
            "h": 1.98,
            "mullions": 2,
        }
    ]


def build_occupied_band(
    role: str,
    variant: str,
    mats: dict[str, bpy.types.Material],
    *,
    include_contract_markers: bool = True,
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    for unit_index, ((x0, x1), centre_x, surface_y) in enumerate(
        zip(UNIT_BOUNDS, UNIT_CENTRES, FRONT_Y)
    ):
        schedule = front_schedule(unit_index, role, variant)
        openings = [
            (
                float(item["x"]) - float(item["w"]) / 2.0,
                float(item["x"]) + float(item["w"]) / 2.0,
                float(item["sill"]),
                float(item["sill"]) + float(item["h"]),
            )
            for item in schedule
        ]
        cladding = mats[front_material(unit_index)]
        objects.extend(
            add_y_wall(
                f"{role}_{variant}_Unit{unit_index + 1}_Front",
                x0=x0 + 0.025,
                x1=x1 - 0.025,
                z0=0.0,
                z1=FLOOR_HEIGHT,
                surface_y=surface_y,
                outward_sign=-1,
                openings=openings,
                mat=cladding,
            )
        )
        for item_index, item in enumerate(schedule):
            if int(item["kind"]) == 0:
                objects.extend(
                    add_front_entry(
                        f"{role}_{variant}_Unit{unit_index + 1}_Entry",
                        centre_x=float(item["x"]),
                        surface_y=surface_y,
                        mats=mats,
                    )
                )
            else:
                objects.extend(
                    add_y_window(
                        f"{role}_{variant}_Unit{unit_index + 1}_FrontWindow_{item_index}",
                        centre_x=float(item["x"]),
                        sill_z=float(item["sill"]),
                        width=float(item["w"]),
                        height=float(item["h"]),
                        surface_y=surface_y,
                        outward_sign=-1,
                        reveal_mat=cladding,
                        mats=mats,
                        mullions=int(item.get("mullions", 1)),
                        privacy_side=int(item.get("privacy", 0)),
                        juliet=bool(item.get("juliet", False)),
                    )
                )
        rear_cladding = mats["metal"] if role == "podium" else cladding
        if role == "podium":
            garage_centre = centre_x - 0.72
            service_centre = x1 - 0.72
            garage_width = 3.78
            rear_openings = [
                (
                    garage_centre - garage_width / 2.0,
                    garage_centre + garage_width / 2.0,
                    0.14,
                    2.58,
                ),
                (
                    service_centre - 0.44,
                    service_centre + 0.44,
                    0.14,
                    2.50,
                ),
            ]
            objects.extend(
                add_y_wall(
                    f"{role}_{variant}_Unit{unit_index + 1}_Rear",
                    x0=x0 + 0.025,
                    x1=x1 - 0.025,
                    z0=0.0,
                    z1=FLOOR_HEIGHT,
                    surface_y=REAR_Y,
                    outward_sign=1,
                    openings=rear_openings,
                    mat=rear_cladding,
                )
            )
            objects.extend(
                add_rear_garage(
                    f"{role}_{variant}_Unit{unit_index + 1}_LaneGarage",
                    centre_x=garage_centre,
                    surface_y=REAR_Y,
                    width=garage_width,
                    mats=mats,
                )
            )
            objects.extend(
                add_rear_service_door(
                    f"{role}_{variant}_Unit{unit_index + 1}_ServiceEntry",
                    centre_x=service_centre,
                    surface_y=REAR_Y,
                    mats=mats,
                )
            )
        else:
            rear_width = (
                3.20
                if variant == "typical_a"
                else 2.88
                if variant == "typical_c"
                else 3.45
            )
            offset = 0.52 if variant == "typical_c" else 0.34
            rear_centre = centre_x + (offset if unit_index % 2 else -offset)
            rear_sill = (
                0.48
                if variant == "typical_a"
                else 0.76
                if variant == "typical_c"
                else 0.66
            )
            rear_height = (
                2.05
                if variant == "typical_a"
                else 1.62
                if variant == "typical_c"
                else 1.78
            )
            rear_openings = [
                (
                    rear_centre - rear_width / 2.0,
                    rear_centre + rear_width / 2.0,
                    rear_sill,
                    rear_sill + rear_height,
                )
            ]
            objects.extend(
                add_y_wall(
                    f"{role}_{variant}_Unit{unit_index + 1}_Rear",
                    x0=x0 + 0.025,
                    x1=x1 - 0.025,
                    z0=0.0,
                    z1=FLOOR_HEIGHT,
                    surface_y=REAR_Y,
                    outward_sign=1,
                    openings=rear_openings,
                    mat=rear_cladding,
                )
            )
            objects.extend(
                add_y_window(
                    f"{role}_{variant}_Unit{unit_index + 1}_RearWindow",
                    centre_x=rear_centre,
                    sill_z=rear_sill,
                    width=rear_width,
                    height=rear_height,
                    surface_y=REAR_Y,
                    outward_sign=1,
                    reveal_mat=rear_cladding,
                    mats=mats,
                    mullions=1,
                    privacy_side=1 if variant == "typical_b" and unit_index % 2 == 0 else 0,
                    juliet=variant == "typical_a" and unit_index % 2 == 1,
                )
            )
        if role == "podium":
            objects.append(
                tbox(
                    f"{role}_{variant}_Unit{unit_index + 1}_GroundSlab",
                    (UNIT_WIDTH - 0.08, REAR_Y - surface_y, 0.16),
                    (
                        centre_x,
                        (REAR_Y + surface_y) / 2.0,
                        0.08,
                    ),
                    mats["concrete"],
                    0.010,
                    tile_m=1.1,
                )
            )
    # End walls are occupied and carved rather than blank party-wall caps.
    side_specs = (
        (-WIDTH / 2.0, -1, FRONT_Y[0], mats["metal"], "Left"),
        (WIDTH / 2.0, 1, FRONT_Y[-1], mats["metal"], "Right"),
    )
    for surface_x, outward_sign, front_y, side_mat, side_name in side_specs:
        if role == "podium":
            side_windows = [(-1.7, 0.72, 1.40, 1.55), (3.2, 0.78, 1.25, 1.45)]
        elif variant == "typical_a":
            side_windows = [(-2.0, 0.54, 1.65, 2.00), (3.0, 0.62, 1.45, 1.88)]
        else:
            side_windows = [(-2.7, 0.70, 1.35, 1.72), (2.1, 0.58, 1.65, 1.95)]
        openings = [
            (
                centre_y - width / 2.0,
                centre_y + width / 2.0,
                sill,
                sill + height,
            )
            for centre_y, sill, width, height in side_windows
        ]
        objects.extend(
            add_x_wall(
                f"{role}_{variant}_{side_name}End",
                y0=front_y + 0.025,
                y1=REAR_Y - 0.025,
                z0=0.0,
                z1=FLOOR_HEIGHT,
                surface_x=surface_x,
                outward_sign=outward_sign,
                openings=openings,
                mat=side_mat,
            )
        )
        for index, (centre_y, sill, width, height) in enumerate(side_windows):
            objects.extend(
                add_x_window(
                    f"{role}_{variant}_{side_name}Window_{index}",
                    centre_y=centre_y,
                    sill_z=sill,
                    width=width,
                    height=height,
                    surface_x=surface_x,
                    outward_sign=outward_sign,
                    reveal_mat=side_mat,
                    mats=mats,
                )
            )
    # Party-wall depth remains explicit inside the row.
    for party_index, x in enumerate((-7.0, 0.0, 7.0), start=1):
        objects.append(
            tbox(
                f"{role}_{variant}_PartyWall_{party_index}",
                (0.12, 12.55, FLOOR_HEIGHT),
                (x, 0.20, FLOOR_HEIGHT / 2.0),
                mats["deep"],
                0.0,
                tile_m=1.0,
            )
        )
    # A crisp joint and drainage line makes each home legible as one bay.
    for joint_index, x in enumerate((-14.0, -7.0, 0.0, 7.0, 14.0)):
        objects.append(
            tbox(
                f"{role}_{variant}_FrontUnitJoint_{joint_index}",
                (0.065, 0.075, FLOOR_HEIGHT - 0.08),
                (
                    max(-13.96, min(13.96, x)),
                    FRONT_Y[min(max(joint_index - 1, 0), 3)] - 0.045,
                    FLOOR_HEIGHT / 2.0,
                ),
                mats["metal"],
                0.006,
                tile_m=0.5,
            )
        )
    if include_contract_markers:
        objects.extend(module_contract_markers(role, variant, FLOOR_HEIGHT))
    return objects


def build_crown(
    mats: dict[str, bpy.types.Material],
    *,
    include_contract_markers: bool = True,
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    for unit_index, ((x0, x1), centre_x, front_y) in enumerate(
        zip(UNIT_BOUNDS, UNIT_CENTRES, FRONT_Y)
    ):
        cladding = mats[front_material(unit_index)]
        objects.extend(
            [
                tbox(
                    f"Crown_Unit{unit_index + 1}_FrontParapet",
                    (UNIT_WIDTH - 0.04, 0.24, CROWN_HEIGHT),
                    (centre_x, front_y + 0.12, CROWN_HEIGHT / 2.0),
                    cladding,
                    0.012,
                    tile_m=1.25,
                ),
                tbox(
                    f"Crown_Unit{unit_index + 1}_RearParapet",
                    (UNIT_WIDTH - 0.04, 0.24, CROWN_HEIGHT),
                    (centre_x, REAR_Y - 0.12, CROWN_HEIGHT / 2.0),
                    cladding,
                    0.012,
                    tile_m=1.25,
                ),
                tbox(
                    f"Crown_Unit{unit_index + 1}_FrontCoping",
                    (UNIT_WIDTH, 0.34, 0.075),
                    (centre_x, front_y + 0.10, CROWN_HEIGHT - 0.0375),
                    mats["metal"],
                    0.012,
                    tile_m=0.55,
                ),
                tbox(
                    f"Crown_Unit{unit_index + 1}_RearCoping",
                    (UNIT_WIDTH, 0.34, 0.075),
                    (centre_x, REAR_Y - 0.10, CROWN_HEIGHT - 0.0375),
                    mats["metal"],
                    0.012,
                    tile_m=0.55,
                ),
            ]
        )
        if unit_index in (0, 3):
            side_x = x0 if unit_index == 0 else x1
            objects.extend(
                [
                    tbox(
                        f"Crown_Unit{unit_index + 1}_EndParapet",
                        (0.24, REAR_Y - front_y, CROWN_HEIGHT),
                        (
                            side_x + (0.12 if unit_index == 0 else -0.12),
                            (REAR_Y + front_y) / 2.0,
                            CROWN_HEIGHT / 2.0,
                        ),
                        cladding,
                        0.012,
                        tile_m=1.25,
                    ),
                    tbox(
                        f"Crown_Unit{unit_index + 1}_EndCoping",
                        (0.34, REAR_Y - front_y, 0.075),
                        (
                            side_x + (0.10 if unit_index == 0 else -0.10),
                            (REAR_Y + front_y) / 2.0,
                            CROWN_HEIGHT - 0.0375,
                        ),
                        mats["metal"],
                        0.012,
                        tile_m=0.55,
                    ),
                ]
            )
    for party_index, x in enumerate((-7.0, 0.0, 7.0), start=1):
        objects.extend(
            [
                tbox(
                    f"Crown_PartyParapet_{party_index}",
                    (0.20, 12.60, CROWN_HEIGHT),
                    (x, 0.20, CROWN_HEIGHT / 2.0),
                    mats["metal"],
                    0.010,
                    tile_m=0.55,
                ),
                tbox(
                    f"Crown_PartyCoping_{party_index}",
                    (0.31, 12.62, 0.075),
                    (x, 0.20, CROWN_HEIGHT - 0.0375),
                    mats["metal"],
                    0.010,
                    tile_m=0.55,
                ),
            ]
        )
    # The markers sit inside the roof build-up and never change silhouette;
    # their material identities let the compiler prove all exposed elevations
    # remain authored when this thin semantic crown is exported alone.
    if include_contract_markers:
        objects.extend(module_contract_markers("crown", "crown", CROWN_HEIGHT))
    return objects


def add_horizontal_guard(
    name: str,
    *,
    x0: float,
    x1: float,
    y: float,
    base_z: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    height = 1.08
    objects = [
        tbox(
            f"{name}_Top",
            (x1 - x0, 0.055, 0.055),
            ((x0 + x1) / 2.0, y, base_z + height),
            mats["metal"],
            0.008,
            tile_m=0.5,
        )
    ]
    bar_count = max(3, int((x1 - x0) / 0.38))
    for index in range(bar_count + 1):
        x = x0 + (x1 - x0) * index / bar_count
        objects.append(
            tbox(
                f"{name}_Bar_{index}",
                (0.030, 0.045, height),
                (x, y, base_z + height / 2.0),
                mats["metal"],
                0.006,
                tile_m=0.5,
            )
        )
    return objects


def add_vertical_guard(
    name: str,
    *,
    x: float,
    y0: float,
    y1: float,
    base_z: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    height = 1.08
    objects = [
        tbox(
            f"{name}_Top",
            (0.055, y1 - y0, 0.055),
            (x, (y0 + y1) / 2.0, base_z + height),
            mats["metal"],
            0.008,
            tile_m=0.5,
        )
    ]
    bar_count = max(3, int((y1 - y0) / 0.38))
    for index in range(bar_count + 1):
        y = y0 + (y1 - y0) * index / bar_count
        objects.append(
            tbox(
                f"{name}_Bar_{index}",
                (0.045, 0.030, height),
                (x, y, base_z + height / 2.0),
                mats["metal"],
                0.006,
                tile_m=0.5,
            )
        )
    return objects


def build_roof(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    for unit_index, ((x0, x1), centre_x, front_y) in enumerate(
        zip(UNIT_BOUNDS, UNIT_CENTRES, FRONT_Y)
    ):
        roof_depth = REAR_Y - front_y
        objects.extend(
            [
                tbox(
                    f"Roof_Unit{unit_index + 1}_Membrane",
                    (UNIT_WIDTH - 0.16, roof_depth - 0.24, 0.14),
                    (centre_x, (REAR_Y + front_y) / 2.0, 0.07),
                    mats["roof"],
                    0.010,
                    tile_m=1.2,
                ),
                tbox(
                    f"Roof_Unit{unit_index + 1}_TerraceMembrane",
                    (UNIT_WIDTH - 0.72, 6.80, 0.085),
                    (centre_x, front_y + 3.85, 0.22),
                    mats["terrace"],
                    0.008,
                    tile_m=0.95,
                ),
            ]
        )
        for seam_index in range(1, 6):
            objects.append(
                tbox(
                    f"Roof_Unit{unit_index + 1}_MembraneSeam_{seam_index}",
                    (UNIT_WIDTH - 0.86, 0.018, 0.012),
                    (
                        centre_x,
                        front_y + 0.60 + seam_index * 1.04,
                        0.270,
                    ),
                    mats["metal"],
                    0.003,
                    tile_m=0.5,
                )
            )
        rail_base = CROWN_HEIGHT
        objects.extend(
            add_horizontal_guard(
                f"Roof_Unit{unit_index + 1}_FrontGuard",
                x0=x0 + 0.10,
                x1=x1 - 0.10,
                y=front_y - 0.03,
                base_z=rail_base,
                mats=mats,
            )
        )
        objects.extend(
            add_horizontal_guard(
                f"Roof_Unit{unit_index + 1}_RearGuard",
                x0=x0 + 0.10,
                x1=x1 - 0.10,
                y=REAR_Y + 0.03,
                base_z=rail_base,
                mats=mats,
            )
        )
        if unit_index == 0:
            objects.extend(
                add_vertical_guard(
                    f"Roof_Unit{unit_index + 1}_LeftGuard",
                    x=x0 - 0.03,
                    y0=front_y + 0.10,
                    y1=REAR_Y - 0.10,
                    base_z=rail_base,
                    mats=mats,
                )
            )
        if unit_index == 3:
            objects.extend(
                add_vertical_guard(
                    f"Roof_Unit{unit_index + 1}_RightGuard",
                    x=x1 + 0.03,
                    y0=front_y + 0.10,
                    y1=REAR_Y - 0.10,
                    base_z=rail_base,
                    mats=mats,
                )
            )
        bulkhead_y = 3.15
        bulkhead_width = 1.90
        bulkhead_depth = 2.35
        bulkhead_height = 2.25
        objects.extend(
            [
                tbox(
                    f"Roof_Unit{unit_index + 1}_StairBulkhead",
                    (bulkhead_width, bulkhead_depth, bulkhead_height),
                    (
                        centre_x,
                        bulkhead_y,
                        0.16 + bulkhead_height / 2.0,
                    ),
                    mats["metal"],
                    0.035,
                    tile_m=0.85,
                ),
                tbox(
                    f"Roof_Unit{unit_index + 1}_BulkheadCoping",
                    (bulkhead_width + 0.12, bulkhead_depth + 0.12, 0.085),
                    (
                        centre_x,
                        bulkhead_y,
                        0.16 + bulkhead_height + 0.0425,
                    ),
                    mats["metal"],
                    0.020,
                    tile_m=0.5,
                ),
                tbox(
                    f"Roof_Unit{unit_index + 1}_BulkheadDoor",
                    (1.00, 0.055, 1.92),
                    (
                        centre_x,
                        bulkhead_y - bulkhead_depth / 2.0 - 0.031,
                        1.15,
                    ),
                    mats["door"],
                    0.015,
                    tile_m=0.7,
                ),
                tbox(
                    f"Roof_Unit{unit_index + 1}_BulkheadDoorPane",
                    (0.58, 0.026, 1.12),
                    (
                        centre_x,
                        bulkhead_y - bulkhead_depth / 2.0 - 0.067,
                        1.42,
                    ),
                    mats["glass"],
                    0.006,
                    tile_m=0.7,
                ),
            ]
        )
    for party_index, x in enumerate((-7.0, 0.0, 7.0), start=1):
        objects.extend(
            add_vertical_guard(
                f"Roof_PartyDivider_{party_index}",
                x=x,
                y0=-5.75,
                y1=5.95,
                base_z=CROWN_HEIGHT,
                mats=mats,
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
        ("floor", "typical_a", FLOOR_HEIGHT),
        ("floor", "typical_b", FLOOR_HEIGHT * 2.0),
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
    scene.view_settings.exposure = 0.56
    background = scene.world.node_tree.nodes.get("Background")
    if background:
        background.inputs["Color"].default_value = (0.40, 0.41, 0.40, 1.0)
        background.inputs["Strength"].default_value = 0.90
    ground = bpy.data.materials.get("MAT_W3_Ground")
    if ground and ground.use_nodes:
        ground.node_tree.nodes["Principled BSDF"].inputs[
            "Base Color"
        ].default_value = (0.38, 0.37, 0.34, 1.0)
    bpy.ops.object.light_add(type="SUN", location=(-42.0, -62.0, 72.0))
    sun = bpy.context.object
    sun.name = "PRESENTATION_W10_TownhomeSoftSun"
    sun.data.energy = 1.75
    sun.data.color = (1.0, 0.86, 0.70)
    sun.data.angle = math.radians(12.0)
    sun.rotation_euler = (
        Vector((0.0, 0.0, 4.0)) - sun.location
    ).to_track_quat("-Z", "Y").to_euler()
    views = {
        "preview": ((26.0, -48.0, 15.5), (0.0, -0.8, 5.1), 55),
        "street": ((0.0, -50.0, 5.3), (0.0, -5.9, 4.7), 55),
        "front_corner_oblique": ((-31.0, -44.0, 14.5), (0.0, 0.0, 5.0), 53),
        "rear_corner_oblique": ((22.0, 27.0, 12.0), (0.0, 0.4, 5.0), 52),
        "aerial": ((26.0, -31.0, 33.0), (0.0, 0.0, 4.3), 54),
        "facade_close": ((0.0, -49.0, 5.0), (0.0, -6.1, 4.8), 61),
        "identity_close": ((-9.0, -21.5, 4.0), (-7.0, -6.0, 3.4), 58),
        "roof_close": ((8.0, -13.0, 20.0), (3.5, 1.2, 8.8), 56),
        "side_close": ((39.0, 0.0, 6.2), (13.5, 0.0, 4.8), 58),
        "context": ((27.0, -39.0, 17.0), (0.0, 0.0, 5.0), 58),
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
        bsdf.inputs["Base Color"].default_value = (0.022, 0.035, 0.040, 1.0)
        bsdf.inputs["Alpha"].default_value = 0.78
        mat.diffuse_color = (0.022, 0.035, 0.040, 0.78)
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
            "The identity is a shallow attached row of complete seven-metre "
            "ground-oriented homes. A straight rectangle preserves it directly; "
            "L- and U-shaped drawings turn complete occupied row bars at corners "
            "without stretching windows, entries, garages, or terrace access."
        ),
        "fixedLandmarkScaleBand": {
            "scaleMin": 0.72,
            "scaleMax": 1.28,
            "maxAxisRatio": 1.24,
        },
        "recommendedWidth_m": [16, 60],
        "recommendedDepth_m": [10, 20],
        "recommendedFloors": [2, 4],
        "wingDepth_m": [10, 16],
        "preferredBayMultiple_m": 7.0,
        "minimumCourtyard_m": 0.0,
        "profiles": {
            "rectangle": {
                "recommendedWidth_m": [16, 60],
                "recommendedDepth_m": [10, 20],
                "recommendedFloors": [2, 4],
                "preferredBayMultiple_m": 7.0,
            },
            "l_shape": {
                "recommendedWidth_m": [21, 70],
                "recommendedDepth_m": [18, 40],
                "recommendedFloors": [2, 4],
                "preferredBayMultiple_m": 7.0,
                "wingDepth_m": [10, 16],
            },
            "u_shape": {
                "recommendedWidth_m": [28, 84],
                "recommendedDepth_m": [20, 42],
                "recommendedFloors": [2, 4],
                "preferredBayMultiple_m": 7.0,
                "wingDepth_m": [10, 16],
            },
        },
        "notes": [
            "Repeat complete seven-metre dwelling bays along the long axis.",
            "Keep individual public entries and rear lane garages one-to-one.",
            "Keep roof terraces and stair bulkheads aligned to dwelling party walls.",
            "Use streetwall_repeat for oversized targets; never stretch a window bay.",
        ],
    }


def provenance() -> dict:
    return {
        "kind": (
            "catalogue_brief_plus_original_imagegen_multiview_package_and_"
            "authored_four_dwelling_construction"
        ),
        "catalogue_archetype_id": ARCHETYPE_ID,
        "catalogue_variant_id": VARIANT_ID,
        "goalpost_local_source": "textures/source/archetype-goalpost.png",
        "orthographic_elevation": "textures/source/elevation-source-v1.png",
        "aerial_reference": "textures/source/aerial-source-v1.png",
        "rear_elevation_reference": "textures/source/rear-elevation-source-v1.png",
        "reference_underlay": "textures/source/occupied-depth-source-v1.png",
        "cedar_material_source": "textures/source/cedar-material-source-v1.png",
        "metal_material_source": (
            "textures/source/charcoal-metal-material-source-v1.png"
        ),
        "reference_generation": "textures/source/reference-generation.json",
        "registered_openings": "textures/source/registered-openings.json",
        "registered_bands": "textures/source/registered-bands.json",
        "elevation_source": f"/families/{FAMILY}/elevation.jpg",
        "skin_manifest": "textures/skin_manifest.json",
        "generator": (
            "tools/archetype_compiler/generate_wave10_townhome_family.py"
        ),
        "reference_method": (
            "catalogue design brief, original goalpost, rectified public and "
            "rear elevations, aerial roof proof, physical cavity schedules, "
            "custom true-scale cedar and corrugated-metal PBR, occupied-depth "
            "underlay, and finite multiscale comparison"
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
            "The authored source package fixes four distinct three-level homes, "
            "alternating cedar and charcoal fields, individual recessed entries, "
            "room-scale windows, rear garages, and four private roof terraces."
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
            "fixed_end_bays": [0, 3],
            "repeatable_middle_bays": [1, 2],
            "middle_variants": ["typical_a", "typical_b", "typical_c"],
            "rule": (
                "Repeat complete seven-metre dwelling bays. Keep public entries, "
                "lane garages, party walls, parapets and roof access aligned."
            ),
        },
        "delivery": {
            "near_atlas_width_px": 2048,
            "far_atlas_width_px": 1024,
            "near_usage": (
                "true-scale cedar and corrugated metal plus physical cavities, "
                "low-e panes, occupied depth, stoops, guards, drains, and roof access"
            ),
            "far_usage": "city-scale render-locked archetype material reference",
        },
        "assembly_contract": {
            "fixed": [
                "podium/entrance",
                "corner returns",
                "crown",
                "roof",
                "four individual entrance recesses",
                "four lane-loaded garages",
                "unit-boundary cladding changes",
                "parapet and coping",
                "four private roof terraces",
                "four stair bulkheads",
                "end-wall window hierarchy",
            ],
            "repeatable": ["typical_a", "typical_b", "typical_c"],
            "side_elevations": (
                "Cedar or charcoal cladding, physical occupied windows, joints, "
                "copings and drainage continue around both end walls and the rear."
            ),
            "elevation_coverage": {
                "front": "four entries, alternating identity fields and picture windows",
                "left": "occupied charcoal end wall with two openings per level",
                "right": "occupied cedar end wall with two openings per level",
                "rear": "four lane garages, service doors and quieter upper windows",
                "roof": "four divided terraces, four guards and four stair bulkheads",
            },
            "variation_policy": (
                "Mild full-envelope scaling is safe. Larger drawings use whole-"
                "bar streetwall repeat rather than deforming one dwelling bay."
            ),
        },
        "assets": {
            "skin_manifest": "textures/skin_manifest.json",
            "source": skin["source"],
            "near": skin["zones"]["cedar"]["near"],
            "far": skin["zones"]["cedar"]["far"],
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
    assembled = {
        "filename": assembled_path.name,
        "floors": 3,
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
                    "id": f"dwelling_{index + 1}",
                    "centre_x_m": centre,
                    "centre_y_m": (FRONT_Y[index] + REAR_Y) / 2.0,
                    "length_m": UNIT_WIDTH,
                    "thickness_m": REAR_Y - FRONT_Y[index],
                    "rotation_degrees": 0.0,
                }
                for index, centre in enumerate(UNIT_CENTRES)
            ],
        },
        "massing_graph": {
            "type": "four_attached_dwelling_row",
            "dwelling_count": 4,
            "dwelling_width_m": UNIT_WIDTH,
            "front_offsets_m": [0.0, 0.45, 0.0, 0.45],
            "rear_lane_service": True,
            "private_roof_terraces": 4,
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
        "default_floors": 3,
        "min_floors": 2,
        "max_floors": 4,
    }
    identity = (
        "Exactly four three-level Calgary missing-middle homes read as separate "
        "seven-metre vertical bays through alternating charcoal corrugated metal "
        "and honey cedar, shallow front offsets, four deep street entries, large "
        "room-scale low-e windows, rear lane garages, and four private rooftop "
        "terraces with compact stair bulkheads."
    )
    material_zones = (
        "matte charcoal fine-corrugated steel; natural vertical honey cedar; "
        "warm-grey concrete stoops and base; black powder-coated frames, canopies, "
        "guards, copings and garage doors; neutral residential low-e glass; "
        "restrained occupied depth; dark roof membrane; grey terrace paving"
    )
    source = provenance()
    manifest = {
        "manifest_schema": 3,
        "grammar_schema_version": 3,
        "generator": {
            "name": "archetype_compiler/generate_wave10_townhome_family.py",
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
        "aesthetic_category_id": "contemporary_urban",
        "development_type": "residential_lowrise",
        "reuse_keys": [
            ARCHETYPE_ID,
            VARIANT_ID,
            "RNDSQR Missing Middle Townhomes",
            "Cedar & Black-Metal Row",
            "Ground-Oriented Missing Middle",
            "Calgary Infill Townhomes",
        ],
        "generation_tags": [
            "wave10_essential_family",
            "standard_building",
            "modular_rowhouse_streetwall",
            "custom_pbr_skin",
            "physical_residential_glazing",
            "reference_locked",
            "four_complete_dwelling_bays",
            "four_deep_individual_entries",
            "four_lane_loaded_garages",
            "alternating_cedar_and_corrugated_metal",
            "room_scale_picture_windows",
            "cedar_privacy_fins",
            "four_private_roof_terraces",
            "four_stair_bulkheads",
        ],
        "footprint_compatibility": footprint,
        "coordinate_contract": COORDINATE_CONTRACT,
        "textures": texture_inventory(skin),
        "facade_sheet": facade_contract(skin),
        "massing_graph": {
            "type": "four_attached_dwelling_row",
            "silhouette": "three_level_alternating_cedar_charcoal_row_with_four_roof_bulkheads",
            "render_locked": True,
            "goalpost": (
                f"/families/{FAMILY}/textures/source/archetype-goalpost.png"
            ),
            "fallback": "whole_dwelling_modular_streetwall",
            "dwelling_count": 4,
            "dwelling_width_m": UNIT_WIDTH,
            "front_offsets_m": [0.0, 0.45, 0.0, 0.45],
            "rear_lane_service": True,
        },
        "material_budget": {
            "max_assembled_materials": 16,
            "rationale": (
                "Construction PBR, physical low-e glazing, registered occupied "
                "depth, deep recesses, terrace paving and planting remain semantic."
            ),
        },
        "dimensions": dimensions,
        "native_width_m": WIDTH,
        "native_depth_m": DEPTH,
        "native_floors": 3,
        "min_floors": 2,
        "max_floors": 4,
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
                "four_complete_dwelling_bays",
                "alternating_cedar_and_corrugated_metal",
                "four_deep_individual_entries",
                "room_scale_picture_windows",
                "four_lane_loaded_garages",
                "cedar_privacy_fins",
                "four_private_roof_terraces",
                "four_stair_bulkheads",
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
        f"[wave10-townhome] {FAMILY}: {fixed_triangles} triangles, "
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
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"[wave10-townhome-render] {FAMILY}: {len(manifest['renders'])} renders")


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
