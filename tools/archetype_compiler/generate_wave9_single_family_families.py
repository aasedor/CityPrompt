"""Author the Wave 9 reference-locked detached-house LEGO families.

The fixed whole-house GLB owns the approved low-rise silhouette and residential
construction. A conservative six-role stack keeps imprecise user footprints
plannable without vertically stretching the landmark roof, entrance, balcony,
screen, tower, or chimney composition.

Run from the repository root with Blender 5.x:

    blender --background --factory-startup --python \
      tools/archetype_compiler/generate_wave9_single_family_families.py -- \
      --output-root frontend/public/families --view-set all
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import bpy
from mathutils import Vector


TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from generate_wave3_landmark_families import (  # noqa: E402
    COORDINATE_CONTRACT,
    aim_camera,
    arched_panel,
    box,
    cylinder,
    delete_objects,
    export_glb,
    material,
    module_contract_markers,
    setup_render,
    sphere,
)
from generate_wave4_standard_batch import profiled_glass_material  # noqa: E402
from generate_wave4_standard_families import pbr_material  # noqa: E402
from generate_wave6_nonresidential_families import (  # noqa: E402
    mapped_reference_panel,
    rectangular_beam,
    reference_image_material,
)


FAMILIES: dict[str, dict] = {
    "swiss-chalet-residence": {
        "archetype_id": "mountain_alpine_chalet",
        "variant_id": "alpine_swiss_traditional",
        "generation_archetype_id": "alpine_swiss_traditional",
        "label": "Mountain Alpine Chalet — Swiss Traditional",
        "dimensions": (14.0, 12.0, 13.2),
        "floors": (1, 3, 3),
        "floor_height_m": 3.15,
        "roof_height_m": 3.75,
        "glass_profile": "chalet_warm_low_e",
        "aesthetic_category_id": "alpine_vernacular",
        "development_type": "residential_single_family",
        "aliases": [
            "mountain_alpine_chalet",
            "alpine_swiss_traditional",
        ],
        "reuse_keys": [
            "mountain_alpine_chalet",
            "alpine_swiss_traditional",
            "Detached House",
            "Single-Family Residential",
            "Swiss Chalet",
        ],
        "identity": (
            "A three-level Swiss chalet rises from a heavy pale-fieldstone base "
            "into two aged-timber storeys beneath paired deep cross-gables, with "
            "stacked carved balconies, folk-art panels, flower boxes, a recessed "
            "arched entrance and twin masonry chimneys."
        ),
        "materials": (
            "rough pale fieldstone; aged spruce logs; carved dark-timber frames, "
            "balustrades and brackets; weathered timber shingles; warm low-e sash "
            "glass; painted folk-art panels; restrained red flower-box accents"
        ),
        "kits": [
            "fieldstone_ground_storey",
            "paired_cross_gable_roofs",
            "deep_shingled_eaves",
            "carved_balcony_system",
            "recessed_arched_entrance",
            "residential_sash_window_system",
            "folk_art_panels",
            "twin_masonry_chimneys",
        ],
        "footprint": {
            "recommendedWidth_m": [12, 17],
            "recommendedDepth_m": [10, 15],
            "recommendedFloors": [1, 3],
        },
        "fixed_band": {
            "scaleMin": 0.86,
            "scaleMax": 1.16,
            "maxAxisRatio": 1.14,
        },
        "goalpost": (
            "/archetypes/buildings/mountain_alpine_chalet/variant_0.png"
        ),
        "silhouette": "paired_deep_cross_gables_over_stone_and_timber_house",
        "profile_rationale": (
            "A detached house is a roof-and-threshold composition. Mild X/Y "
            "variation preserves the complete chalet; larger drawings repeat "
            "complete timber house bays rather than stretching the cross-gables."
        ),
        "close_target": (1.0, -5.7, 5.5),
        "front_y": -5.50,
    },
    "timber-screen-lanehouse": {
        "archetype_id": "japanese_contemporary_lanehouse",
        "variant_id": "japanese_lane_timber_screen",
        "generation_archetype_id": "japanese_lane_timber_screen",
        "label": "Japanese Contemporary Lanehouse — Timber Screen",
        "dimensions": (12.0, 5.0, 10.2),
        "floors": (1, 3, 3),
        "floor_height_m": 3.0,
        "roof_height_m": 1.2,
        "glass_profile": "lanehouse_screened_low_e",
        "aesthetic_category_id": "japanese_contemporary",
        "development_type": "residential_single_family",
        "aliases": [
            "japanese_contemporary_lanehouse",
            "japanese_lane_timber_screen",
        ],
        "reuse_keys": [
            "japanese_contemporary_lanehouse",
            "japanese_lane_timber_screen",
            "Detached House",
            "Single-Family Residential",
            "Lanehouse",
        ],
        "identity": (
            "A long street-facing three-level Japanese lanehouse wraps two "
            "occupied upper floors in one continuous honey-cedar privacy screen, "
            "held by fine charcoal rails above a deeply recessed entrance and "
            "bench, with a shallow rooftop clerestory."
        ),
        "materials": (
            "fine-grained honey cedar battens and panels; charcoal-bronze support "
            "rails; dark low-e occupied glazing behind the screen; pale concrete "
            "threshold; restrained dark-metal roof and clerestory framing"
        ),
        "kits": [
            "continuous_vertical_cedar_screen",
            "screen_support_rail_datums",
            "occupied_glazing_behind_screen",
            "deep_recessed_entrance",
            "integrated_timber_bench",
            "wrapped_side_screen",
            "rooftop_clerestory",
        ],
        "footprint": {
            "recommendedWidth_m": [9.5, 15.5],
            "recommendedDepth_m": [4.2, 6.3],
            "recommendedFloors": [1, 3],
        },
        "fixed_band": {
            "scaleMin": 0.82,
            "scaleMax": 1.20,
            "maxAxisRatio": 1.18,
        },
        "goalpost": (
            "/archetypes/buildings/japanese_contemporary_lanehouse/variant_1.png"
        ),
        "silhouette": "long_street_facing_cedar_screen_with_rooftop_clerestory",
        "profile_rationale": (
            "The long street-facing screen is a complete privacy facade, so mild "
            "independent scaling is safe. Larger drawings repeat complete screen "
            "bays and their occupied rooms rather than widening battens."
        ),
        "close_target": (0.8, -2.7, 5.0),
        "front_y": -2.5,
    },
    "spanish-colonial-villa": {
        "archetype_id": "mediterranean_villa_estate",
        "variant_id": "med_villa_spanish_colonial",
        "generation_archetype_id": "med_villa_spanish_colonial",
        "label": "Mediterranean Villa Estate — Spanish Colonial",
        "dimensions": (18.0, 14.0, 12.8),
        "floors": (1, 3, 3),
        "floor_height_m": 3.05,
        "roof_height_m": 1.55,
        "glass_profile": "villa_recessed_iron_glass",
        "aesthetic_category_id": "spanish_colonial",
        "development_type": "residential_single_family",
        "aliases": [
            "mediterranean_villa_estate",
            "med_villa_spanish_colonial",
        ],
        "reuse_keys": [
            "mediterranean_villa_estate",
            "med_villa_spanish_colonial",
            "Detached House",
            "Single-Family Residential",
            "Spanish Colonial Villa",
        ],
        "identity": (
            "A three-level aged-stucco Spanish Colonial villa is anchored by a "
            "deep central stone portal and asymmetrical left bell tower, with "
            "barred recessed sash, wrought-iron balconies, exposed brick patches "
            "and a low weathered terracotta roof."
        ),
        "materials": (
            "warm hand-trowelled lime stucco; localized historic red-clay brick; "
            "pale warm limestone; dark timber sash and entrance doors; black "
            "forged iron grilles and balconies; weathered terracotta barrel tile; "
            "aged bronze bell"
        ),
        "kits": [
            "aged_stucco_three_level_body",
            "asymmetrical_bell_tower",
            "deep_central_stone_portal",
            "recessed_barred_sash",
            "forged_iron_balconies",
            "physical_exposed_brick_patches",
            "terracotta_barrel_tile_roof",
            "physical_bell_and_tower_arches",
        ],
        "footprint": {
            "recommendedWidth_m": [15, 23],
            "recommendedDepth_m": [11, 18],
            "recommendedFloors": [1, 3],
        },
        "fixed_band": {
            "scaleMin": 0.84,
            "scaleMax": 1.18,
            "maxAxisRatio": 1.16,
        },
        "goalpost": (
            "/archetypes/buildings/mediterranean_villa_estate/variant_2.png"
        ),
        "silhouette": "long_low_terracotta_villa_with_left_bell_tower",
        "profile_rationale": (
            "The portal, tower and roof are one low-rise landmark composition. "
            "Mild scaling preserves it; oversized parcels repeat complete stucco "
            "window bays through the family stack."
        ),
        "close_target": (0.0, -7.15, 4.5),
        "front_y": -7.0,
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("frontend/public/families"),
    )
    parser.add_argument("--family", action="append", choices=sorted(FAMILIES))
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


def load_palette(
    family: str,
    folder: Path,
) -> tuple[dict[str, bpy.types.Material], dict]:
    skin = json.loads(
        (folder / "textures" / "skin_manifest.json").read_text(encoding="utf-8")
    )
    near = {zone: values["near"] for zone, values in skin["zones"].items()}
    cfg = FAMILIES[family]
    token = family.replace("-", "_").upper()
    mats: dict[str, bpy.types.Material] = {
        "facade": pbr_material(
            f"MAT_W9_{token}_RegisteredFacade",
            folder,
            near["facade"],
            "facade",
            value=0.96,
            saturation=0.96,
        ),
        "glass": profiled_glass_material(
            f"MAT_W9_{token}_PhysicalGlass",
            cfg["glass_profile"],
        ),
        "underlay": reference_image_material(
            f"MAT_W9_{token}_RegisteredOccupiedDepth",
            folder,
            skin.get("sources", {}).get(
                "reference_underlay",
                "textures/source/occupied-depth-source.png",
            ),
            emission_strength=0.085,
        ),
        "deep": material(
            f"MAT_W9_{token}_DeepResidentialCavity",
            (0.020, 0.017, 0.014, 1.0),
            0.94,
        ),
        "plaster": material(
            f"MAT_W9_{token}_WarmInteriorPlaster",
            (0.34, 0.29, 0.23, 1.0),
            0.88,
        ),
        "room_warm": material(
            f"MAT_W9_{token}_OccupiedRoomWarm",
            (0.18, 0.105, 0.052, 1.0),
            0.84,
            emission=(0.72, 0.30, 0.075, 1.0),
            emission_strength=0.18,
        ),
        "room_dim": material(
            f"MAT_W9_{token}_OccupiedRoomDim",
            (0.055, 0.050, 0.044, 1.0),
            0.90,
            emission=(0.23, 0.13, 0.065, 1.0),
            emission_strength=0.045,
        ),
        "curtain": material(
            f"MAT_W9_{token}_LinenCurtain",
            (0.37, 0.33, 0.27, 1.0),
            0.94,
        ),
        "green": material(
            f"MAT_W9_{token}_RestrainedFoliage",
            (0.08, 0.16, 0.055, 1.0),
            0.82,
        ),
    }
    if family == "swiss-chalet-residence":
        mats.update(
            {
                "stone": pbr_material(
                    f"MAT_W9_{token}_Fieldstone",
                    folder,
                    near["stone"],
                    "stone",
                    value=1.05,
                    saturation=0.82,
                ),
                "timber": pbr_material(
                    f"MAT_W9_{token}_AgedTimber",
                    folder,
                    near["timber"],
                    "timber",
                    value=0.82,
                    saturation=0.96,
                ),
                "timber_side": pbr_material(
                    f"MAT_W9_{token}_AgedTimberShadowReturn",
                    folder,
                    near["timber"],
                    "timber_side",
                    value=0.72,
                    saturation=1.02,
                ),
                "carved": pbr_material(
                    f"MAT_W9_{token}_CarvedTimber",
                    folder,
                    near["carved"],
                    "carved",
                    value=0.77,
                    saturation=0.98,
                ),
                "roof": pbr_material(
                    f"MAT_W9_{token}_WeatheredShingles",
                    folder,
                    near["roof"],
                    "roof",
                    value=0.84,
                    saturation=0.68,
                ),
                "metal": pbr_material(
                    f"MAT_W9_{token}_DarkMetal",
                    folder,
                    near["metal"],
                    "metal",
                    metallic=0.64,
                    value=0.72,
                ),
                "flower": pbr_material(
                    f"MAT_W9_{token}_FlowerAccent",
                    folder,
                    near["flower"],
                    "flower",
                    value=0.88,
                    saturation=1.18,
                ),
            }
        )
    elif family == "timber-screen-lanehouse":
        mats.update(
            {
                "cedar": pbr_material(
                    f"MAT_W9_{token}_HoneyCedar",
                    folder,
                    near["cedar"],
                    "cedar",
                    value=0.69,
                    saturation=1.08,
                ),
                "metal": pbr_material(
                    f"MAT_W9_{token}_CharcoalBronze",
                    folder,
                    near["metal"],
                    "metal",
                    metallic=0.62,
                    value=0.62,
                ),
                "concrete": pbr_material(
                    f"MAT_W9_{token}_ThresholdConcrete",
                    folder,
                    near["concrete"],
                    "concrete",
                    value=0.86,
                    saturation=0.72,
                ),
                "roof": pbr_material(
                    f"MAT_W9_{token}_DarkRoof",
                    folder,
                    near["roof"],
                    "roof",
                    metallic=0.32,
                    value=0.66,
                ),
            }
        )
        mats["timber"] = mats["cedar"]
        mats["carved"] = mats["cedar"]
        mats["stone"] = mats["concrete"]
    else:
        mats.update(
            {
                "stucco": pbr_material(
                    f"MAT_W9_{token}_AgedLimeStucco",
                    folder,
                    near["stucco"],
                    "stucco",
                    value=0.61,
                    saturation=1.12,
                ),
                "brick": pbr_material(
                    f"MAT_W9_{token}_ExposedBrick",
                    folder,
                    near["brick"],
                    "brick",
                    value=0.56,
                    saturation=1.22,
                ),
                "roof": pbr_material(
                    f"MAT_W9_{token}_TerracottaBarrelTile",
                    folder,
                    near["roof"],
                    "roof",
                    value=0.64,
                    saturation=1.10,
                ),
                "stone": pbr_material(
                    f"MAT_W9_{token}_WarmLimestone",
                    folder,
                    near["stone"],
                    "stone",
                    value=0.84,
                    saturation=0.90,
                ),
                "iron": pbr_material(
                    f"MAT_W9_{token}_ForgedIron",
                    folder,
                    near["iron"],
                    "iron",
                    metallic=0.74,
                    value=0.46,
                ),
                "timber": pbr_material(
                    f"MAT_W9_{token}_DarkTimber",
                    folder,
                    near["timber"],
                    "timber",
                    value=0.74,
                    saturation=0.88,
                ),
                "bronze": pbr_material(
                    f"MAT_W9_{token}_AgedBronze",
                    folder,
                    near["bronze"],
                    "bronze",
                    metallic=0.70,
                    value=0.72,
                ),
            }
        )
        mats["carved"] = mats["timber"]
        mats["metal"] = mats["iron"]
    mats["glass"]["glazing_lod"] = "always"
    mats["glass"]["reference_locked"] = True
    mats["glass"]["source_variant_id"] = cfg["variant_id"]
    mats["underlay"]["glazing_profile"] = cfg["glass_profile"]
    return mats, skin


def registered_panel(
    name: str,
    *,
    x0: float,
    x1: float,
    y: float,
    z0: float,
    z1: float,
    mat: bpy.types.Material,
    model_x_bounds: tuple[float, float] = (-7.0, 7.0),
    model_z_bounds: tuple[float, float] = (0.0, 13.2),
    source_uv_bounds: tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0),
) -> bpy.types.Object:
    return mapped_reference_panel(
        name,
        (
            (x0, y, z0),
            (x1, y, z0),
            (x1, y, z1),
            (x0, y, z1),
        ),
        mat,
        model_x_bounds=model_x_bounds,
        model_z_bounds=model_z_bounds,
        source_uv_bounds=source_uv_bounds,
    )


def tiled_vertical_panel(
    name: str,
    *,
    axis: str,
    fixed_coordinate: float,
    lateral0: float,
    lateral1: float,
    z0: float,
    z1: float,
    outward_sign: int,
    mat: bpy.types.Material,
    u_repeat: float,
    v_repeat: float,
) -> bpy.types.Object:
    """A true-scale material return for side/rear elevations."""
    if axis == "x":
        if outward_sign > 0:
            vertices = [
                (fixed_coordinate, lateral0, z0),
                (fixed_coordinate, lateral1, z0),
                (fixed_coordinate, lateral1, z1),
                (fixed_coordinate, lateral0, z1),
            ]
        else:
            vertices = [
                (fixed_coordinate, lateral1, z0),
                (fixed_coordinate, lateral0, z0),
                (fixed_coordinate, lateral0, z1),
                (fixed_coordinate, lateral1, z1),
            ]
    else:
        if outward_sign > 0:
            vertices = [
                (lateral1, fixed_coordinate, z0),
                (lateral0, fixed_coordinate, z0),
                (lateral0, fixed_coordinate, z1),
                (lateral1, fixed_coordinate, z1),
            ]
        else:
            vertices = [
                (lateral0, fixed_coordinate, z0),
                (lateral1, fixed_coordinate, z0),
                (lateral1, fixed_coordinate, z1),
                (lateral0, fixed_coordinate, z1),
            ]
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(vertices, [], [(0, 1, 2, 3)])
    mesh.materials.append(mat)
    uv = mesh.uv_layers.new(name="UVMap")
    values = (
        (0.0, 0.0),
        (u_repeat, 0.0),
        (u_repeat, v_repeat),
        (0.0, v_repeat),
    )
    for loop_index, value in enumerate(values):
        uv.data[loop_index].uv = value
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def round_beam(
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    radius: float,
    mat: bpy.types.Material,
    *,
    vertices: int = 12,
) -> bpy.types.Object:
    """Create a cylindrical construction member between two world points."""
    start_vector = Vector(start)
    end_vector = Vector(end)
    delta = end_vector - start_vector
    member = cylinder(
        name,
        radius,
        delta.length,
        tuple((start_vector + end_vector) * 0.5),
        mat,
        vertices=vertices,
    )
    member.rotation_mode = "QUATERNION"
    member.rotation_quaternion = delta.to_track_quat("Z", "Y")
    return member


def rectangles_around_openings(
    x0: float,
    x1: float,
    z0: float,
    z1: float,
    openings: list[tuple[float, float, float, float]],
) -> list[tuple[float, float, float, float]]:
    """Partition a wall into rectangles while preserving actual open cavities."""
    clipped = [
        (
            max(x0, opening_x0),
            min(x1, opening_x1),
            max(z0, opening_z0),
            min(z1, opening_z1),
        )
        for opening_x0, opening_x1, opening_z0, opening_z1 in openings
        if opening_x1 > x0
        and opening_x0 < x1
        and opening_z1 > z0
        and opening_z0 < z1
    ]
    z_breaks = sorted(
        {
            z0,
            z1,
            *(value for opening in clipped for value in opening[2:]),
        }
    )
    rectangles: list[tuple[float, float, float, float]] = []
    for row_z0, row_z1 in zip(z_breaks, z_breaks[1:]):
        if row_z1 - row_z0 < 0.015:
            continue
        midpoint = (row_z0 + row_z1) * 0.5
        blocked = sorted(
            (opening[0], opening[1])
            for opening in clipped
            if opening[2] < midpoint < opening[3]
        )
        cursor = x0
        for blocked_x0, blocked_x1 in blocked:
            if blocked_x0 > cursor + 0.015:
                rectangles.append((cursor, blocked_x0, row_z0, row_z1))
            cursor = max(cursor, blocked_x1)
        if cursor < x1 - 0.015:
            rectangles.append((cursor, x1, row_z0, row_z1))
    return rectangles


def add_registered_front_wall(
    *,
    name: str,
    x0: float,
    x1: float,
    z0: float,
    z1: float,
    y: float,
    openings: list[tuple[float, float, float, float]],
    construction_mat: bpy.types.Material,
    registered_mat: bpy.types.Material | None,
    surface_uv_bounds: tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0),
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    for index, (rx0, rx1, rz0, rz1) in enumerate(
        rectangles_around_openings(x0, x1, z0, z1, openings)
    ):
        objects.append(
            box(
                f"{name}_WallBacking_{index}",
                (rx1 - rx0, 0.24, rz1 - rz0),
                ((rx0 + rx1) * 0.5, y + 0.12, (rz0 + rz1) * 0.5),
                construction_mat,
                0.018,
            )
        )
        if registered_mat is not None:
            objects.append(
                registered_panel(
                    f"{name}_RegisteredSurface_{index}",
                    x0=rx0,
                    x1=rx1,
                    y=y - 0.006,
                    z0=rz0,
                    z1=rz1,
                    mat=registered_mat,
                    model_x_bounds=(x0, x1),
                    model_z_bounds=(z0, z1),
                    source_uv_bounds=surface_uv_bounds,
                )
            )
    return objects


def add_window_assembly(
    *,
    name: str,
    centre_x: float,
    sill_z: float,
    width: float,
    height: float,
    front_y: float,
    mats: dict[str, bpy.types.Material],
    flower_box: bool = False,
    shutters: bool = False,
) -> list[bpy.types.Object]:
    """A real recessed double-sash opening with returns, pane and room depth."""
    objects: list[bpy.types.Object] = []
    x0, x1 = centre_x - width / 2, centre_x + width / 2
    z0, z1 = sill_z, sill_z + height
    frame = 0.070
    recess_y = front_y + 0.42
    room_mat = mats["room_warm"] if sum(ord(char) for char in name) % 3 else mats["room_dim"]
    # Deep reveal surfaces run from the public facade to the glass line.
    objects.extend(
        [
            box(
                f"{name}_LeftReveal",
                (0.10, 0.48, height),
                (x0 + 0.05, front_y + 0.24, (z0 + z1) * 0.5),
                mats["timber"],
                0.018,
            ),
            box(
                f"{name}_RightReveal",
                (0.10, 0.48, height),
                (x1 - 0.05, front_y + 0.24, (z0 + z1) * 0.5),
                mats["timber"],
                0.018,
            ),
            box(
                f"{name}_SillReturn",
                (width, 0.48, 0.11),
                (centre_x, front_y + 0.24, z0 + 0.055),
                mats["timber"],
                0.018,
            ),
            box(
                f"{name}_HeadReturn",
                (width, 0.48, 0.11),
                (centre_x, front_y + 0.24, z1 - 0.055),
                mats["timber"],
                0.018,
            ),
            box(
                f"{name}_OccupiedRoomCard",
                (width - 0.20, 0.030, height - 0.20),
                (centre_x, recess_y + 0.09, (z0 + z1) * 0.5),
                room_mat,
                0.008,
            ),
            box(
                f"{name}_PhysicalPane",
                (width - 0.18, 0.032, height - 0.18),
                (centre_x, recess_y, (z0 + z1) * 0.5),
                mats["glass"],
                0.012,
            ),
            box(
                f"{name}_CentralMullion",
                (frame, 0.09, height - 0.12),
                (centre_x, recess_y - 0.035, (z0 + z1) * 0.5),
                mats["timber"],
                0.012,
            ),
            box(
                f"{name}_MeetingRail",
                (width - 0.10, 0.09, frame),
                (centre_x, recess_y - 0.035, z0 + height * 0.51),
                mats["timber"],
                0.012,
            ),
        ]
    )
    # Fine glazing bars distinguish residential sash from generic curtain wall.
    for offset in (-width * 0.23, width * 0.23):
        objects.append(
            box(
                f"{name}_FineMullion_{offset:+.2f}",
                (0.032, 0.070, height - 0.16),
                (centre_x + offset, recess_y - 0.045, (z0 + z1) * 0.5),
                mats["carved"],
                0.008,
            )
        )
    # A partial linen shade and sill plane give each room readable depth
    # without turning the glazing into a uniformly glowing texture card.
    if sum(ord(char) for char in name) % 2:
        objects.append(
            box(
                f"{name}_LinenShade",
                (width * 0.34, 0.022, height * 0.72),
                (
                    centre_x - width * 0.24,
                    recess_y + 0.055,
                    z0 + height * 0.58,
                ),
                mats["curtain"],
                0.006,
            )
        )
    if shutters:
        for side in (-1, 1):
            shutter_x = centre_x + side * (width * 0.67)
            objects.append(
                box(
                    f"{name}_TimberShutter_{side:+d}",
                    (width * 0.28, 0.10, height * 0.92),
                    (shutter_x, front_y - 0.035, (z0 + z1) * 0.5),
                    mats["timber"],
                    0.025,
                )
            )
            for rail_index in range(5):
                objects.append(
                    box(
                        f"{name}_ShutterLouver_{side:+d}_{rail_index}",
                        (width * 0.24, 0.045, 0.055),
                        (
                            shutter_x,
                            front_y - 0.10,
                            z0 + height * (0.17 + rail_index * 0.16),
                        ),
                        mats["carved"],
                        0.008,
                    )
                )
    if flower_box:
        objects.extend(
            add_flower_box(
                f"{name}_FlowerBox",
                centre_x=centre_x,
                y=front_y - 0.24,
                z=sill_z - 0.08,
                width=width * 1.05,
                mats=mats,
            )
        )
    return objects


def add_flower_box(
    name: str,
    *,
    centre_x: float,
    y: float,
    z: float,
    width: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects = [
        box(
            f"{name}_Planter",
            (width, 0.32, 0.24),
            (centre_x, y, z),
            mats["carved"],
            0.045,
        )
    ]
    cluster_count = max(6, int(width / 0.16))
    for index in range(cluster_count):
        x = centre_x - width * 0.44 + width * 0.88 * index / max(
            1, cluster_count - 1
        )
        objects.append(
            sphere(
                f"{name}_Foliage_{index}",
                0.070,
                (
                    x,
                    y - 0.03 - 0.025 * (index % 3),
                    z + 0.16 + 0.028 * (index % 2),
                ),
                mats["green"],
                (1.0, 0.78, 0.72),
                segments=12,
                rings=6,
            )
        )
        if index % 2 == 0:
            objects.append(
                sphere(
                    f"{name}_RedBloom_{index}",
                    0.035,
                    (
                        x + 0.020,
                        y - 0.10 - 0.015 * (index % 3),
                        z + 0.21,
                    ),
                    mats["flower"],
                    (1.0, 0.86, 0.82),
                    segments=10,
                    rings=5,
                )
            )
    return objects


def add_arch_entrance(
    *,
    name: str,
    centre_x: float,
    sill_z: float,
    width: float,
    height: float,
    front_y: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    radius = width * 0.5
    spring_z = sill_z + height - radius
    recess_y = front_y + 0.48
    objects.extend(
        [
            box(
                f"{name}_RecessFloor",
                (width, 0.72, 0.10),
                (centre_x, front_y + 0.34, sill_z + 0.05),
                mats["stone"],
                0.018,
            ),
            box(
                f"{name}_LeftStoneReturn",
                (0.16, 0.72, height - radius),
                (
                    centre_x - width / 2 + 0.08,
                    front_y + 0.34,
                    sill_z + (height - radius) / 2,
                ),
                mats["stone"],
                0.025,
            ),
            box(
                f"{name}_RightStoneReturn",
                (0.16, 0.72, height - radius),
                (
                    centre_x + width / 2 - 0.08,
                    front_y + 0.34,
                    sill_z + (height - radius) / 2,
                ),
                mats["stone"],
                0.025,
            ),
            arched_panel(
                f"{name}_DeepCarvedDoorLeaf",
                centre_x,
                recess_y,
                sill_z + 0.05,
                width - 0.20,
                height - 0.10,
                mats["carved"],
                32,
            ),
        ]
    )
    # A segmented arch ring and vertical jambs make the opening part of the
    # load-bearing fieldstone base rather than a door-shaped decal.
    objects.extend(
        [
            box(
                f"{name}_LeftCarvedJamb",
                (0.18, 0.18, spring_z - sill_z),
                (
                    centre_x - radius - 0.02,
                    front_y - 0.055,
                    (sill_z + spring_z) * 0.5,
                ),
                mats["carved"],
                0.028,
            ),
            box(
                f"{name}_RightCarvedJamb",
                (0.18, 0.18, spring_z - sill_z),
                (
                    centre_x + radius + 0.02,
                    front_y - 0.055,
                    (sill_z + spring_z) * 0.5,
                ),
                mats["carved"],
                0.028,
            ),
        ]
    )
    segments = 18
    for index in range(segments):
        a0 = math.pi * index / segments
        a1 = math.pi * (index + 1) / segments
        start = (
            centre_x + math.cos(a0) * (radius + 0.02),
            front_y - 0.055,
            spring_z + math.sin(a0) * (radius + 0.02),
        )
        end = (
            centre_x + math.cos(a1) * (radius + 0.02),
            front_y - 0.055,
            spring_z + math.sin(a1) * (radius + 0.02),
        )
        objects.append(
            rectangular_beam(
                f"{name}_CarvedArchRing_{index}",
                start,
                end,
                0.17,
                mats["carved"],
                depth=0.18,
            )
        )
    # Hand-carved split leaves and hardware.
    objects.append(
        box(
            f"{name}_DoorCentreStile",
            (0.09, 0.07, height - 0.30),
            (centre_x, recess_y - 0.04, sill_z + (height - 0.10) * 0.48),
            mats["metal"],
            0.012,
        )
    )
    for side in (-1, 1):
        for row in range(3):
            objects.append(
                box(
                    f"{name}_CarvedDoorPanel_{side:+d}_{row}",
                    (width * 0.31, 0.055, 0.42),
                    (
                        centre_x + side * width * 0.20,
                        recess_y - 0.045,
                        sill_z + 0.48 + row * 0.55,
                    ),
                    mats["timber"],
                    0.025,
                )
            )
    return objects


def add_balcony(
    *,
    name: str,
    centre_x: float,
    width: float,
    slab_z: float,
    front_y: float,
    mats: dict[str, bpy.types.Material],
    flowers: bool,
    bracket_drop: float = 0.74,
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    projection = 1.08
    outer_y = front_y - projection
    objects.extend(
        [
            box(
                f"{name}_TimberSlab",
                (width, projection, 0.18),
                (centre_x, front_y - projection * 0.5, slab_z),
                mats["carved"],
                0.035,
            ),
            box(
                f"{name}_TopRail",
                (width, 0.13, 0.13),
                (centre_x, outer_y, slab_z + 1.02),
                mats["carved"],
                0.025,
            ),
            box(
                f"{name}_BottomRail",
                (width, 0.11, 0.12),
                (centre_x, outer_y, slab_z + 0.25),
                mats["carved"],
                0.022,
            ),
        ]
    )
    post_count = max(5, int(width / 0.40))
    for index in range(post_count):
        x = centre_x - width * 0.47 + width * 0.94 * index / max(
            1, post_count - 1
        )
        objects.append(
            box(
                f"{name}_CarvedBaluster_{index}",
                (0.105, 0.105, 0.72),
                (x, outer_y, slab_z + 0.63),
                mats["carved"],
                0.022,
            )
        )
        if index < post_count - 1:
            next_x = centre_x - width * 0.47 + width * 0.94 * (
                index + 1
            ) / max(1, post_count - 1)
            objects.append(
                rectangular_beam(
                    f"{name}_CarvedDiagonal_{index}",
                    (x, outer_y - 0.012, slab_z + 0.30),
                    (next_x, outer_y - 0.012, slab_z + 0.94),
                    0.055,
                    mats["carved"],
                    depth=0.07,
                )
            )
    bracket_positions = [
        centre_x - width * 0.42,
        centre_x,
        centre_x + width * 0.42,
    ]
    for index, x in enumerate(bracket_positions):
        objects.extend(
            [
                rectangular_beam(
                    f"{name}_BracketArm_{index}",
                    (x, front_y - 0.12, slab_z - 0.07),
                    (x, outer_y + 0.10, slab_z - 0.07),
                    0.13,
                    mats["carved"],
                    depth=0.13,
                ),
                rectangular_beam(
                    f"{name}_BracketKnee_{index}",
                    (x, front_y - 0.10, slab_z - bracket_drop),
                    (x, outer_y + 0.10, slab_z - 0.09),
                    0.12,
                    mats["carved"],
                    depth=0.12,
                ),
            ]
        )
    if flowers:
        objects.extend(
            add_flower_box(
                f"{name}_ContinuousFlowers",
                centre_x=centre_x,
                y=outer_y - 0.16,
                z=slab_z + 1.00,
                width=width * 0.84,
                mats=mats,
            )
        )
    return objects


def gable_roof(
    name: str,
    *,
    centre_x: float,
    width: float,
    depth: float,
    base_z: float,
    rise: float,
    roof_mat: bpy.types.Material,
    gable_mat: bpy.types.Material,
) -> bpy.types.Object:
    """Solid front-facing gable prism with its ridge on the Y axis."""
    x0, x1 = centre_x - width / 2, centre_x + width / 2
    y0, y1 = -depth / 2, depth / 2
    eave_z = base_z + 0.10
    vertices = [
        (x0, y0, base_z),
        (x1, y0, base_z),
        (x1, y1, base_z),
        (x0, y1, base_z),
        (x0, y0, eave_z),
        (x1, y0, eave_z),
        (x1, y1, eave_z),
        (x0, y1, eave_z),
        (centre_x, y0, base_z + rise),
        (centre_x, y1, base_z + rise),
    ]
    faces = [
        (0, 3, 2, 1),
        (4, 8, 9, 7),
        (8, 5, 6, 9),
        (0, 1, 5, 8, 4),
        (3, 7, 9, 6, 2),
    ]
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(roof_mat)
    mesh.materials.append(gable_mat)
    mesh.polygons[3].material_index = 1
    mesh.polygons[4].material_index = 1
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.select_set(False)
    if mesh.uv_layers.active is not None:
        uv_data = mesh.uv_layers.active.data
        for polygon_index in (3, 4):
            polygon = mesh.polygons[polygon_index]
            mirror_u = polygon_index == 4
            for loop_index in polygon.loop_indices:
                vertex_index = mesh.loops[loop_index].vertex_index
                coordinate = mesh.vertices[vertex_index].co
                u = (coordinate.x - x0) / max(width, 0.001)
                if mirror_u:
                    u = 1.0 - u
                v = (coordinate.z - base_z) / max(rise, 0.001)
                uv_data[loop_index].uv = (u, v)
    bevel = obj.modifiers.new("ShingleEdgeSoftening", "BEVEL")
    bevel.width = 0.035
    bevel.segments = 2
    return obj


def add_roof_construction(
    *,
    name: str,
    centre_x: float,
    width: float,
    depth: float,
    base_z: float,
    rise: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects = [
        gable_roof(
            f"{name}_SolidGableRoof",
            centre_x=centre_x,
            width=width,
            depth=depth,
            base_z=base_z,
            rise=rise,
            roof_mat=mats["roof"],
            gable_mat=mats["timber"],
        )
    ]
    # Shingle courses have physical thickness and follow both roof pitches.
    course_count = 12
    for side in (-1, 1):
        for index in range(course_count):
            fraction = (index + 0.35) / course_count
            x = centre_x + side * width * 0.5 * (1.0 - fraction)
            z = base_z + 0.13 + rise * fraction
            objects.append(
                rectangular_beam(
                    f"{name}_ShingleCourse_{side:+d}_{index}",
                    (x, -depth * 0.5 - 0.025, z),
                    (x, depth * 0.5 + 0.025, z),
                    0.018,
                    mats["roof"],
                    depth=0.035,
                )
            )
    # Horizontal log courses articulate each triangular end wall while the
    # projecting frames and glazing remain the foreground construction.
    front_y = -depth * 0.5 - 0.045
    for index in range(6):
        fraction = (index + 1) / 7
        z = base_z + rise * fraction
        half_span = width * 0.5 * (1.0 - fraction)
        objects.append(
            box(
                f"{name}_GableLogCourse_{index}",
                (max(0.30, half_span * 2.0 - 0.18), 0.10, 0.085),
                (centre_x, front_y, z),
                mats["carved"],
                0.018,
            )
        )
    # Front exposed rafters and carved knee braces make the roof read as load
    # bearing, not as a floating cap.
    rafter_y = -depth * 0.5 - 0.04
    for side in (-1, 1):
        objects.append(
            rectangular_beam(
                f"{name}_FrontRafter_{side:+d}",
                (
                    centre_x + side * width * 0.50,
                    rafter_y,
                    base_z + 0.02,
                ),
                (centre_x, rafter_y, base_z + rise),
                0.19,
                mats["carved"],
                depth=0.18,
            )
        )
    for offset in (-width * 0.34, width * 0.34):
        x = centre_x + offset
        roof_z = base_z + rise * (1.0 - abs(offset) / (width * 0.5))
        objects.extend(
            [
                rectangular_beam(
                    f"{name}_GablePost_{offset:+.2f}",
                    (x, rafter_y - 0.03, base_z + 0.12),
                    (x, rafter_y - 0.03, roof_z - 0.08),
                    0.16,
                    mats["carved"],
                    depth=0.16,
                ),
                rectangular_beam(
                    f"{name}_GableKnee_{offset:+.2f}",
                    (x, rafter_y - 0.03, roof_z - 0.52),
                    (
                        centre_x + math.copysign(width * 0.47, offset),
                        rafter_y - 0.03,
                        base_z + 0.22,
                    ),
                    0.13,
                    mats["carved"],
                    depth=0.13,
                ),
            ]
        )
    objects.append(
        rectangular_beam(
            f"{name}_RidgeCap",
            (centre_x, -depth * 0.5 - 0.04, base_z + rise + 0.04),
            (centre_x, depth * 0.5 + 0.04, base_z + rise + 0.04),
            0.17,
            mats["roof"],
            depth=0.18,
        )
    )
    return objects


def add_secondary_opening(
    *,
    name: str,
    axis: str,
    fixed_coordinate: float,
    lateral: float,
    sill_z: float,
    width: float,
    height: float,
    outward_sign: int,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    """Deep secondary-elevation sash set over a dark room cavity."""
    depth_offset = outward_sign * 0.07
    if axis == "x":
        location = (
            fixed_coordinate + depth_offset,
            lateral,
            sill_z + height / 2,
        )
        pane_size = (0.035, width, height)
        horizontal_size = (0.08, width + 0.20, 0.10)
        vertical_size = (0.08, 0.10, height + 0.20)
        left_location = (
            fixed_coordinate + depth_offset * 1.5,
            lateral - width / 2,
            sill_z + height / 2,
        )
        right_location = (
            fixed_coordinate + depth_offset * 1.5,
            lateral + width / 2,
            sill_z + height / 2,
        )
        head_location = (
            fixed_coordinate + depth_offset * 1.5,
            lateral,
            sill_z + height,
        )
        sill_location = (
            fixed_coordinate + depth_offset * 1.5,
            lateral,
            sill_z,
        )
    else:
        location = (
            lateral,
            fixed_coordinate + depth_offset,
            sill_z + height / 2,
        )
        pane_size = (width, 0.035, height)
        horizontal_size = (width + 0.20, 0.08, 0.10)
        vertical_size = (0.10, 0.08, height + 0.20)
        left_location = (
            lateral - width / 2,
            fixed_coordinate + depth_offset * 1.5,
            sill_z + height / 2,
        )
        right_location = (
            lateral + width / 2,
            fixed_coordinate + depth_offset * 1.5,
            sill_z + height / 2,
        )
        head_location = (
            lateral,
            fixed_coordinate + depth_offset * 1.5,
            sill_z + height,
        )
        sill_location = (
            lateral,
            fixed_coordinate + depth_offset * 1.5,
            sill_z,
        )
    return [
        box(f"{name}_DeepCavity", pane_size, location, mats["deep"], 0.018),
        box(f"{name}_PhysicalGlass", pane_size, tuple(
            value + (depth_offset * 0.35 if index == (0 if axis == "x" else 1) else 0)
            for index, value in enumerate(location)
        ), mats["glass"], 0.012),
        box(f"{name}_LeftFrame", vertical_size, left_location, mats["carved"], 0.018),
        box(f"{name}_RightFrame", vertical_size, right_location, mats["carved"], 0.018),
        box(f"{name}_HeadFrame", horizontal_size, head_location, mats["carved"], 0.018),
        box(f"{name}_SillFrame", horizontal_size, sill_location, mats["carved"], 0.018),
    ]


def chalet_fixed(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    cfg = FAMILIES["swiss-chalet-residence"]
    front_y = cfg["front_y"]
    objects: list[bpy.types.Object] = []

    # Recessed structural core: front cavities remain physically open for room
    # plates, while stone/timber construction wraps the other elevations.
    objects.extend(
        [
            box(
                "CHALET_FieldstoneStructuralCore",
                (13.25, 10.25, 3.12),
                (0.0, 0.43, 1.56),
                mats["stone"],
                0.055,
            ),
            box(
                "CHALET_AgedTimberStructuralCore",
                (13.20, 10.20, 6.25),
                (0.0, 0.45, 6.245),
                mats["timber"],
                0.045,
            ),
        ]
    )

    ground_windows = [
        (-5.15, 0.82, 1.18, 1.45),
        (-3.20, 0.82, 1.18, 1.45),
        (-1.15, 0.82, 1.28, 1.45),
        (4.15, 0.82, 1.20, 1.45),
        (5.75, 0.82, 1.05, 1.45),
    ]
    door = (1.55, 0.12, 1.65, 2.82)
    first_windows = [
        (-5.15, 4.12, 1.25, 1.52),
        (-3.25, 4.12, 1.25, 1.52),
        (-1.20, 4.12, 1.25, 1.52),
        (1.50, 4.05, 1.45, 1.68),
        (4.30, 4.12, 1.30, 1.52),
    ]
    second_windows = [
        (-4.85, 7.18, 1.28, 1.45),
        (-2.85, 7.18, 1.28, 1.45),
        (1.35, 7.18, 1.30, 1.50),
        (3.25, 7.18, 1.30, 1.50),
        (5.10, 7.18, 1.15, 1.45),
    ]
    openings = [
        (
            centre - width / 2,
            centre + width / 2,
            sill,
            sill + height,
        )
        for centre, sill, width, height in (
            ground_windows + first_windows + second_windows
        )
    ]
    openings.append(
        (
            door[0] - door[2] / 2,
            door[0] + door[2] / 2,
            door[1],
            door[1] + door[3],
        )
    )
    objects.extend(
        add_registered_front_wall(
            name="CHALET_Ground",
            x0=-6.65,
            x1=6.65,
            z0=0.0,
            z1=3.15,
            y=front_y,
            openings=openings,
            construction_mat=mats["stone"],
            registered_mat=mats["stone"],
            surface_uv_bounds=(0.0, 0.0, 3.0, 1.45),
        )
    )
    objects.extend(
        add_registered_front_wall(
            name="CHALET_TimberUpper",
            x0=-6.65,
            x1=6.65,
            z0=3.15,
            z1=9.38,
            y=front_y,
            openings=openings,
            construction_mat=mats["timber"],
            registered_mat=mats["timber"],
            surface_uv_bounds=(0.0, 0.0, 2.25, 2.20),
        )
    )
    # One exact-coordinate occupied-depth source sits behind all actual voids.
    objects.append(
        registered_panel(
            "CHALET_RegisteredOccupiedDepth",
            x0=-7.0,
            x1=7.0,
            y=front_y + 0.52,
            z0=0.0,
            z1=13.2,
            mat=mats["underlay"],
            source_uv_bounds=(0.080, 0.135, 0.930, 0.895),
        )
    )
    for index, (centre, sill, width, height) in enumerate(
        ground_windows + first_windows + second_windows
    ):
        objects.extend(
            add_window_assembly(
                name=f"CHALET_ResidentialSash_{index}",
                centre_x=centre,
                sill_z=sill,
                width=width,
                height=height,
                front_y=front_y,
                mats=mats,
                flower_box=index in {0, 1, 2, 3, 4, 5, 6, 8, 10, 11, 12, 13},
                shutters=index in {5, 6, 9, 10, 13},
            )
        )
    objects.extend(
        add_arch_entrance(
            name="CHALET_RecessedArchedEntrance",
            centre_x=door[0],
            sill_z=door[1],
            width=door[2],
            height=door[3],
            front_y=front_y,
            mats=mats,
        )
    )

    # Structural timber bands, corner log ends and carved balconies establish
    # the construction hierarchy seen in the catalogue reference.
    for z in (3.18, 6.26, 9.31):
        objects.append(
            box(
                f"CHALET_ContinuousTimberDatum_{z:.2f}",
                (13.85, 0.22, 0.22),
                (0.0, front_y - 0.05, z),
                mats["carved"],
                0.035,
            )
        )
    for x in (-6.58, 6.58):
        for index in range(18):
            objects.append(
                cylinder(
                    f"CHALET_ExpressedLogEnd_{x:+.2f}_{index}",
                    0.115,
                    0.34,
                    (x, front_y - 0.09, 3.35 + index * 0.33),
                    mats["carved"],
                    vertices=10,
                    scale_xy=(1.0, 0.72),
                )
            )
    objects.extend(
        add_balcony(
            name="CHALET_LeftLowerBalcony",
            centre_x=-3.75,
            width=5.45,
            slab_z=3.40,
            front_y=front_y,
            mats=mats,
            flowers=True,
        )
    )
    # The reference's lower gallery reads as one continuous load-bearing
    # timber datum. Bridge the two balcony bays instead of leaving an
    # apartment-like gap between unrelated railings.
    objects.extend(
        add_balcony(
            name="CHALET_IntegratedLowerGalleryConnector",
            centre_x=-0.28,
            width=1.64,
            slab_z=3.40,
            front_y=front_y,
            mats=mats,
            flowers=True,
        )
    )
    objects.extend(
        add_balcony(
            name="CHALET_RightLowerBalcony",
            centre_x=2.45,
            width=4.15,
            slab_z=3.40,
            front_y=front_y,
            mats=mats,
            flowers=True,
        )
    )
    objects.extend(
        add_balcony(
            name="CHALET_LeftUpperBalcony",
            centre_x=-4.15,
            width=4.45,
            slab_z=6.54,
            front_y=front_y,
            mats=mats,
            flowers=True,
        )
    )
    objects.extend(
        add_balcony(
            name="CHALET_RightUpperBalcony",
            centre_x=2.65,
            width=4.35,
            slab_z=6.54,
            front_y=front_y,
            mats=mats,
            flowers=True,
        )
    )

    # Shallow physical frames retain the folk-art panels from the registered
    # source while giving them the depth of painted timber infill.
    for index, (x0, x1) in enumerate(((-0.65, 0.85), (4.35, 6.00))):
        objects.append(
            registered_panel(
                f"CHALET_FolkArtRegisteredPanel_{index}",
                x0=x0,
                x1=x1,
                y=front_y - 0.075,
                z0=7.22,
                z1=8.86,
                mat=mats["facade"],
            )
        )
        for edge_name, size, location in (
            (
                "Left",
                (0.10, 0.12, 1.75),
                (x0, front_y - 0.11, 8.04),
            ),
            (
                "Right",
                (0.10, 0.12, 1.75),
                (x1, front_y - 0.11, 8.04),
            ),
            (
                "Top",
                (x1 - x0, 0.12, 0.10),
                ((x0 + x1) / 2, front_y - 0.11, 8.89),
            ),
            (
                "Bottom",
                (x1 - x0, 0.12, 0.10),
                ((x0 + x1) / 2, front_y - 0.11, 7.19),
            ),
        ):
            objects.append(
                box(
                    f"CHALET_FolkArtFrame_{index}_{edge_name}",
                    size,
                    location,
                    mats["carved"],
                    0.018,
                )
            )

    # Paired overlapping cross-gables, not one generic extrusion.
    objects.extend(
        add_roof_construction(
            name="CHALET_LeftCrossGable",
            centre_x=-4.20,
            width=6.20,
            depth=13.10,
            base_z=9.22,
            rise=3.22,
            mats=mats,
        )
    )
    objects.extend(
        add_roof_construction(
            name="CHALET_PrimaryCrossGable",
            centre_x=2.15,
            width=10.25,
            depth=13.85,
            base_z=9.24,
            rise=3.88,
            mats=mats,
        )
    )
    # High gable sash assemblies sit behind the projecting roof faces.
    for index, (x, z, width, height, y) in enumerate(
        [
            (-4.25, 9.72, 1.05, 1.22, -6.55),
            (1.35, 9.83, 1.00, 1.18, -6.90),
            (2.95, 9.83, 1.00, 1.18, -6.90),
        ]
    ):
        objects.extend(
            add_window_assembly(
                name=f"CHALET_GableSash_{index}",
                centre_x=x,
                sill_z=z,
                width=width,
                height=height,
                front_y=y,
                mats=mats,
                flower_box=False,
                shutters=False,
            )
        )

    # Chimneys pass through the roof mass and terminate in expressed caps.
    for index, (x, y, z) in enumerate(((-2.65, 1.30, 11.25), (5.65, 1.10, 11.38))):
        objects.extend(
            [
                box(
                    f"CHALET_MasonryChimney_{index}",
                    (0.72, 0.62, 2.55),
                    (x, y, z),
                    mats["stone"],
                    0.045,
                ),
                box(
                    f"CHALET_ChimneyCap_{index}",
                    (0.90, 0.80, 0.18),
                    (x, y, z + 1.28),
                    mats["stone"],
                    0.035,
                ),
                box(
                    f"CHALET_ChimneyFluePair_{index}",
                    (0.48, 0.42, 0.42),
                    (x, y, z + 1.52),
                    mats["metal"],
                    0.025,
                ),
            ]
        )

    # Secondary elevations repeat real sash, log datums and roof logic. Their
    # quieter schedules keep the front hierarchy without leaving blank boxes.
    for side in (-1, 1):
        x = side * 6.66
        objects.extend(
            [
                tiled_vertical_panel(
                    f"CHALET_SideFieldstoneReturn_{side:+d}",
                    axis="x",
                    fixed_coordinate=x + side * 0.008,
                    lateral0=-5.48,
                    lateral1=5.54,
                    z0=0.0,
                    z1=3.15,
                    outward_sign=side,
                    mat=mats["stone"],
                    u_repeat=3.0,
                    v_repeat=1.45,
                ),
                tiled_vertical_panel(
                    f"CHALET_SideTimberReturn_{side:+d}",
                    axis="x",
                    fixed_coordinate=x + side * 0.008,
                    lateral0=-5.48,
                    lateral1=5.54,
                    z0=3.15,
                    z1=9.36,
                    outward_sign=side,
                    mat=mats["timber_side"],
                    u_repeat=2.5,
                    v_repeat=2.2,
                ),
            ]
        )
        # Horizontal log courses and structural corner posts continue the
        # chalet construction around both long returns. They intentionally
        # sit proud of the PBR wall so the side elevation cannot collapse into
        # a smooth pale slab in grazing views.
        for course in range(22):
            z = 3.30 + course * 0.275
            segments = [(-5.39, 5.43)]
            for sill in (4.15, 7.20):
                if sill - 0.10 <= z <= sill + 1.48:
                    for lateral in (-2.65, 0.15, 2.95):
                        opening = (lateral - 0.68, lateral + 0.68)
                        clipped: list[tuple[float, float]] = []
                        for start, end in segments:
                            if opening[1] <= start or opening[0] >= end:
                                clipped.append((start, end))
                                continue
                            if opening[0] - start > 0.08:
                                clipped.append((start, opening[0]))
                            if end - opening[1] > 0.08:
                                clipped.append((opening[1], end))
                        segments = clipped
            for segment_index, (start, end) in enumerate(segments):
                suffix = (
                    ""
                    if len(segments) == 1
                    else f"_Segment_{segment_index}"
                )
                objects.append(
                    box(
                        (
                            f"CHALET_SidePhysicalLogCourse_{side:+d}_{course}"
                            f"{suffix}"
                        ),
                        (0.105, end - start, 0.115),
                        (
                            x + side * 0.075,
                            (start + end) * 0.5,
                            z,
                        ),
                        mats["carved"],
                        0.018,
                    )
                )
        for y in (-5.28, 5.28):
            objects.append(
                box(
                    f"CHALET_SideCornerPost_{side:+d}_{y:+.2f}",
                    (0.22, 0.30, 6.25),
                    (x + side * 0.13, y, 6.25),
                    mats["carved"],
                    0.025,
                )
            )
        for storey, sill in enumerate((0.85, 4.15, 7.20)):
            for bay, lateral in enumerate((-2.65, 0.15, 2.95)):
                objects.extend(
                    add_secondary_opening(
                        name=f"CHALET_SideSash_{side:+d}_{storey}_{bay}",
                        axis="x",
                        fixed_coordinate=x,
                        lateral=lateral,
                        sill_z=sill,
                        width=1.15,
                        height=1.38,
                        outward_sign=side,
                        mats=mats,
                    )
                )
    objects.extend(
        [
            tiled_vertical_panel(
                "CHALET_RearFieldstoneReturn",
                axis="y",
                fixed_coordinate=5.558,
                lateral0=-6.64,
                lateral1=6.64,
                z0=0.0,
                z1=3.15,
                outward_sign=1,
                mat=mats["stone"],
                u_repeat=3.2,
                v_repeat=1.45,
            ),
            tiled_vertical_panel(
                "CHALET_RearTimberReturn",
                axis="y",
                fixed_coordinate=5.558,
                lateral0=-6.64,
                lateral1=6.64,
                z0=3.15,
                z1=9.36,
                outward_sign=1,
                mat=mats["timber_side"],
                u_repeat=2.7,
                v_repeat=2.2,
            ),
        ]
    )
    for storey, sill in enumerate((0.85, 4.15, 7.20)):
        for bay, lateral in enumerate((-4.75, -1.65, 1.65, 4.75)):
            objects.extend(
                add_secondary_opening(
                    name=f"CHALET_RearSash_{storey}_{bay}",
                    axis="y",
                    fixed_coordinate=5.55,
                    lateral=lateral,
                    sill_z=sill,
                    width=1.18,
                    height=1.38,
                    outward_sign=1,
                    mats=mats,
                )
            )
    return objects


def chalet_fallback_module(
    role: str,
    variant: str,
    height: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    width, depth = 14.0, 12.0
    front_y = -depth / 2
    objects: list[bpy.types.Object] = []
    if role == "roof":
        objects.extend(
            add_roof_construction(
                name=f"CHALETKIT_{role}_{variant}",
                centre_x=0.0,
                width=width + 0.8,
                depth=depth + 0.8,
                base_z=0.08,
                rise=height - 0.14,
                mats=mats,
            )
        )
        return objects
    wall_mat = mats["stone"] if role == "podium" else mats["timber"]
    objects.append(
        box(
            f"CHALETKIT_{role}_{variant}_Envelope",
            (width, depth, height),
            (0.0, 0.0, height / 2),
            wall_mat,
            0.045,
        )
    )
    if role == "podium":
        objects.extend(
            add_arch_entrance(
                name=f"CHALETKIT_{role}_{variant}_Entrance",
                centre_x=1.45,
                sill_z=0.08,
                width=1.55,
                height=min(2.78, height - 0.15),
                front_y=front_y,
                mats=mats,
            )
        )
        window_centres = (-4.8, -2.7, 4.25)
    elif role == "crown":
        window_centres = (-3.8, -1.2, 1.6, 4.0)
    else:
        window_centres = {
            "typical_a": (-4.8, -2.5, 0.1, 2.7, 4.9),
            "typical_b": (-4.5, -1.8, 1.3, 4.2),
            "typical_c": (-4.9, -3.0, -0.7, 1.8, 4.6),
        }[variant]
    sill = max(0.62, (height - 1.45) * 0.50)
    for index, centre in enumerate(window_centres):
        objects.extend(
            add_window_assembly(
                name=f"CHALETKIT_{role}_{variant}_Sash_{index}",
                centre_x=centre,
                sill_z=sill,
                width=1.15,
                height=min(1.45, height - sill - 0.18),
                front_y=front_y,
                mats=mats,
                flower_box=role != "crown" and index % 2 == 0,
                shutters=role != "podium" and index % 2 == 1,
            )
        )
    if role == "floor" and variant in {"typical_a", "typical_c"}:
        objects.extend(
            add_balcony(
                name=f"CHALETKIT_{role}_{variant}_Balcony",
                centre_x=0.0 if variant == "typical_a" else -1.6,
                width=6.2 if variant == "typical_a" else 4.8,
                slab_z=0.18,
                front_y=front_y,
                mats=mats,
                flowers=True,
                bracket_drop=0.08,
            )
        )
    return objects


def add_lane_screen_front(
    *,
    name: str,
    width: float,
    front_y: float,
    z0: float,
    z1: float,
    mats: dict[str, bpy.types.Material],
    slat_count: int = 31,
) -> list[bpy.types.Object]:
    """Build one continuous cedar privacy layer in front of occupied glass."""
    objects: list[bpy.types.Object] = []
    for index in range(slat_count):
        x = -width / 2 + 0.10 + (width - 0.20) * index / max(
            1, slat_count - 1
        )
        batten_width = (0.064, 0.076, 0.084)[index % 3]
        projection = (0.12, 0.15, 0.135)[index % 3]
        objects.append(
            box(
                f"{name}_VerticalCedarBatten_{index}",
                (batten_width, projection, z1 - z0),
                (x, front_y - 0.17, (z0 + z1) * 0.5),
                mats["cedar"],
                0.018,
            )
        )
    for index, z in enumerate((z0 + 0.08, (z0 + z1) * 0.5, z1 - 0.08)):
        objects.append(
            box(
                f"{name}_CharcoalSupportRail_{index}",
                (width + 0.16, 0.10, 0.085),
                (0.0, front_y - 0.055, z),
                mats["metal"],
                0.018,
            )
        )
    for side in (-1, 1):
        objects.append(
            box(
                f"{name}_ScreenCornerPost_{side:+d}",
                (0.13, 0.22, z1 - z0 + 0.12),
                (side * width / 2, front_y - 0.13, (z0 + z1) * 0.5),
                mats["metal"],
                0.022,
            )
        )
    return objects


def add_lane_screen_side(
    *,
    name: str,
    side: int,
    x: float,
    y0: float,
    y1: float,
    z0: float,
    z1: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    slat_count = max(24, int((y1 - y0) / 0.19))
    for index in range(slat_count):
        y = y0 + (y1 - y0) * index / max(1, slat_count - 1)
        batten_width = (0.064, 0.076, 0.086)[index % 3]
        projection = (0.12, 0.15, 0.135)[index % 3]
        objects.append(
            box(
                f"{name}_SideCedarBatten_{side:+d}_{index}",
                (projection, batten_width, z1 - z0),
                (x + side * 0.17, y, (z0 + z1) * 0.5),
                mats["cedar"],
                0.018,
            )
        )
    for index, z in enumerate((z0 + 0.08, (z0 + z1) * 0.5, z1 - 0.08)):
        objects.append(
            box(
                f"{name}_SideSupportRail_{side:+d}_{index}",
                (0.10, y1 - y0 + 0.10, 0.085),
                (x + side * 0.055, (y0 + y1) * 0.5, z),
                mats["metal"],
                0.018,
            )
        )
    return objects


def add_lane_clerestory(
    *,
    name: str,
    width: float,
    depth: float,
    base_z: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    height = 0.64
    front_y = -depth / 2
    objects.extend(
        [
            box(
                f"{name}_OccupiedClerestoryGlass",
                (width - 0.18, 0.045, height - 0.16),
                (0.0, front_y, base_z + height * 0.5),
                mats["glass"],
                0.012,
            ),
            box(
                f"{name}_ClerestoryRoofCap",
                (width + 0.26, depth + 0.20, 0.14),
                (0.0, 0.0, base_z + height + 0.07),
                mats["roof"],
                0.025,
            ),
            box(
                f"{name}_ClerestoryBase",
                (width + 0.20, depth + 0.16, 0.13),
                (0.0, 0.0, base_z + 0.065),
                mats["metal"],
                0.022,
            ),
        ]
    )
    bay_count = 8
    for index in range(bay_count + 1):
        x = -width / 2 + width * index / bay_count
        objects.append(
            box(
                f"{name}_ClerestoryMullion_{index}",
                (0.075, 0.10, height),
                (x, front_y - 0.03, base_z + height * 0.5),
                mats["metal"],
                0.012,
            )
        )
    for side in (-1, 1):
        objects.append(
            box(
                f"{name}_ClerestorySideGlass_{side:+d}",
                (0.035, depth - 0.12, height - 0.16),
                (side * width / 2, 0.0, base_z + height * 0.5),
                mats["glass"],
                0.012,
            )
        )
    return objects


def lanehouse_fixed(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    cfg = FAMILIES["timber-screen-lanehouse"]
    width, depth, _height = cfg["dimensions"]
    front_y = cfg["front_y"]
    objects: list[bpy.types.Object] = []
    # The structural/occupied volume is deliberately recessed from the screen.
    objects.extend(
        [
            box(
                "LANE_GroundCedarStructuralCore",
                (5.165, 4.62, 3.00),
                (-3.1925, 0.12, 1.50),
                mats["cedar"],
                0.035,
            ),
            box(
                "LANE_GroundCedarStructuralCore_Right",
                (3.665, 4.62, 3.00),
                (3.9425, 0.12, 1.50),
                mats["cedar"],
                0.035,
            ),
            box(
                "LANE_EntranceStructuralHeader",
                (2.72, 4.62, 0.20),
                (0.75, 0.12, 2.90),
                mats["cedar"],
                0.025,
            ),
            box(
                "LANE_ShadowedUpperStructuralCore",
                (11.55, 4.62, 5.92),
                (0.0, 0.12, 6.00),
                mats["deep"],
                0.035,
            ),
            box(
                "LANE_FlatRoofPlate",
                (11.92, 4.92, 0.18),
                (0.0, 0.02, 9.02),
                mats["roof"],
                0.025,
            ),
            box(
                "LANE_UpperOccupiedGlassVolume",
                (11.55, 0.050, 5.72),
                (0.0, front_y + 0.46, 6.04),
                mats["glass"],
                0.012,
            ),
        ]
    )
    objects.append(
        registered_panel(
            "LANE_RegisteredOccupiedDepth",
            x0=-6.0,
            x1=6.0,
            y=front_y + 0.56,
            z0=0.0,
            z1=10.2,
            mat=mats["underlay"],
            model_x_bounds=(-6.0, 6.0),
            model_z_bounds=(0.0, 10.2),
            source_uv_bounds=(0.130, 0.108, 0.865, 0.895),
        )
    )
    # Subtle floor plates and room dividers remain visible through screen gaps.
    for z in (3.05, 6.02, 8.98):
        objects.append(
            box(
                f"LANE_OccupiedFloorDatum_{z:.2f}",
                (11.68, 0.58, 0.12),
                (0.0, front_y + 0.65, z),
                mats["metal"],
                0.012,
            )
        )
    for x in (-4.45, -1.48, 1.48, 4.45):
        objects.append(
            box(
                f"LANE_RoomDivider_{x:+.2f}",
                (0.08, 0.42, 5.72),
                (x, front_y + 0.67, 6.04),
                mats["metal"],
                0.010,
            )
        )
    for floor, (sill, room_height) in enumerate(
        ((3.42, 2.18), (6.42, 2.18))
    ):
        for bay, centre_x in enumerate((-4.45, -1.48, 1.48, 4.45)):
            room_mat = (
                mats["room_warm"]
                if (floor + bay) % 3
                else mats["room_dim"]
            )
            objects.append(
                box(
                    f"LANE_ExplicitOccupiedRoom_{floor}_{bay}",
                    (2.05, 0.028, room_height),
                    (
                        centre_x,
                        front_y + 0.60,
                        sill + room_height * 0.5,
                    ),
                    room_mat,
                    0.008,
                )
            )
    objects.extend(
        add_lane_screen_front(
            name="LANE_ContinuousPrivacyScreen",
            width=11.92,
            front_y=front_y,
            z0=3.04,
            z1=9.02,
            mats=mats,
            slat_count=69,
        )
    )
    for side in (-1, 1):
        # A recessed continuous glass plane and localized occupied rooms make
        # the screen gaps read as real depth instead of a pale solid side wall.
        objects.append(
            box(
                f"LANE_SideOccupiedGlass_{side:+d}",
                (0.035, 4.22, 5.66),
                (side * 5.835, 0.02, 6.03),
                mats["glass"],
                0.010,
            )
        )
        for floor, (sill, room_height) in enumerate(
            ((3.40, 2.16), (6.40, 2.16))
        ):
            for bay, room_y in enumerate((-1.35, 1.05)):
                room_mat = (
                    mats["room_warm"]
                    if (floor + bay + (0 if side < 0 else 1)) % 3
                    else mats["room_dim"]
                )
                objects.append(
                    box(
                        f"LANE_SideOccupiedRoom_{side:+d}_{floor}_{bay}",
                        (0.026, 1.62, room_height),
                        (
                            side * 5.812,
                            room_y,
                            sill + room_height * 0.5,
                        ),
                        room_mat,
                        0.008,
                    )
                )
        objects.extend(
            add_lane_screen_side(
                name="LANE_WrappedPrivacyScreen",
                side=side,
                x=side * 5.88,
                y0=-2.38,
                y1=2.18,
                z0=3.04,
                z1=9.02,
                mats=mats,
            )
        )

    # Ground level is genuinely recessed beneath the screen, with two solid
    # slat wings, a framed vestibule and an integrated bench.
    for side, centre_x, panel_width in (
        (-1, -3.15, 5.55),
        (1, 4.52, 2.88),
    ):
        objects.append(
            box(
                f"LANE_GroundCedarWing_{side:+d}",
                (panel_width, 0.28, 2.92),
                (centre_x, front_y + 0.14, 1.50),
                mats["cedar"],
                0.025,
            )
        )
        slats = max(6, int(panel_width / 0.15))
        for index in range(slats):
            x = centre_x - panel_width / 2 + 0.07 + (
                panel_width - 0.14
            ) * index / max(1, slats - 1)
            objects.append(
                box(
                    f"LANE_GroundSlat_{side:+d}_{index}",
                    (0.055, 0.08, 2.76),
                    (x, front_y - 0.045, 1.50),
                    mats["cedar"],
                    0.010,
                )
            )
    entrance_x = 0.75
    objects.extend(
        [
            box(
                "LANE_RecessedEntranceCavity",
                (2.72, 0.035, 2.62),
                (entrance_x, front_y + 0.83, 1.40),
                mats["deep"],
                0.018,
            ),
            box(
                "LANE_EntranceLeftReveal",
                (0.12, 0.82, 2.62),
                (entrance_x - 1.30, front_y + 0.42, 1.40),
                mats["cedar"],
                0.018,
            ),
            box(
                "LANE_EntranceRightReveal",
                (0.12, 0.82, 2.62),
                (entrance_x + 1.30, front_y + 0.42, 1.40),
                mats["cedar"],
                0.018,
            ),
            box(
                "LANE_RecessedEntranceGlassDoor",
                (1.18, 0.035, 2.34),
                (entrance_x - 0.54, front_y + 0.72, 1.40),
                mats["glass"],
                0.012,
            ),
            box(
                "LANE_GlassDoorLeftFrame",
                (0.075, 0.075, 2.40),
                (entrance_x - 1.13, front_y + 0.68, 1.40),
                mats["cedar"],
                0.012,
            ),
            box(
                "LANE_GlassDoorRightFrame",
                (0.075, 0.075, 2.40),
                (entrance_x + 0.05, front_y + 0.68, 1.40),
                mats["cedar"],
                0.012,
            ),
            box(
                "LANE_GlassDoorHeadFrame",
                (1.25, 0.075, 0.075),
                (entrance_x - 0.54, front_y + 0.68, 2.60),
                mats["cedar"],
                0.012,
            ),
            box(
                "LANE_GlassDoorCentreMullion",
                (0.060, 0.070, 2.30),
                (entrance_x - 0.54, front_y + 0.67, 1.40),
                mats["cedar"],
                0.010,
            ),
            box(
                "LANE_GlassDoorHandle",
                (0.035, 0.060, 0.42),
                (entrance_x - 0.36, front_y + 0.62, 1.38),
                mats["metal"],
                0.008,
            ),
            box(
                "LANE_EntranceLeftStile",
                (0.09, 0.10, 2.52),
                (entrance_x - 1.27, front_y + 0.16, 1.40),
                mats["cedar"],
                0.015,
            ),
            box(
                "LANE_EntranceRightStile",
                (0.09, 0.10, 2.52),
                (entrance_x + 1.27, front_y + 0.16, 1.40),
                mats["cedar"],
                0.015,
            ),
            box(
                "LANE_EntranceHead",
                (2.62, 0.10, 0.10),
                (entrance_x, front_y + 0.16, 2.66),
                mats["cedar"],
                0.015,
            ),
            box(
                "LANE_IntegratedBenchSeat",
                (1.02, 0.45, 0.11),
                (1.56, front_y + 0.24, 0.72),
                mats["cedar"],
                0.035,
            ),
            box(
                "LANE_IntegratedBenchBack",
                (1.02, 0.10, 0.72),
                (1.56, front_y + 0.40, 1.05),
                mats["cedar"],
                0.025,
            ),
            box(
                "LANE_ConcreteThreshold",
                (2.92, 0.92, 0.18),
                (entrance_x, front_y - 0.02, 0.09),
                mats["concrete"],
                0.025,
            ),
            box(
                "LANE_ContinuousDarkBase",
                (12.0, 0.24, 0.17),
                (0.0, front_y + 0.10, 0.085),
                mats["metal"],
                0.020,
            ),
        ]
    )
    # Bench slats and recessed soffit complete the entrance construction.
    for index in range(5):
        objects.append(
            box(
                f"LANE_BenchBackSlat_{index}",
                (0.58, 0.045, 0.040),
                (
                    1.56,
                    front_y + 0.165,
                    0.82 + index * 0.12,
                ),
                mats["metal"],
                0.008,
            )
        )
    objects.append(
        box(
            "LANE_EntranceRecessSoffit",
            (2.78, 0.82, 0.11),
            (entrance_x, front_y + 0.37, 2.76),
            mats["cedar"],
            0.018,
        )
    )

    objects.extend(
        add_lane_clerestory(
            name="LANE_RooftopClerestory",
            width=10.20,
            depth=3.35,
            base_z=9.03,
            mats=mats,
        )
    )
    # Quieter occupied rear openings; the long side screen remains dominant.
    for floor, sill in enumerate((0.72, 3.72, 6.72)):
        for bay, x in enumerate((-4.45, -1.48, 1.48, 4.45)):
            objects.extend(
                add_secondary_opening(
                    name=f"LANE_RearSash_{floor}_{bay}",
                    axis="y",
                    fixed_coordinate=2.43,
                    lateral=x,
                    sill_z=sill,
                    width=1.12,
                    height=1.60,
                    outward_sign=1,
                    mats=mats,
                )
            )
    return objects


def lanehouse_fallback_module(
    role: str,
    variant: str,
    height: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    width, depth = 12.0, 5.0
    front_y = -depth / 2
    objects: list[bpy.types.Object] = []
    if role == "roof":
        objects.extend(
            [
                box(
                    f"LANEKIT_{role}_{variant}_FlatRoof",
                    (width, depth, 0.18),
                    (0.0, 0.0, 0.09),
                    mats["roof"],
                    0.022,
                ),
                *add_lane_clerestory(
                    name=f"LANEKIT_{role}_{variant}_Clerestory",
                    width=10.2,
                    depth=3.3,
                    base_z=0.16,
                    mats=mats,
                ),
            ]
        )
        return objects
    objects.append(
        box(
            f"LANEKIT_{role}_{variant}_Core",
            (11.70, 4.70, height),
            (0.0, 0.08, height / 2),
            mats["cedar"],
            0.028,
        )
    )
    if role == "podium":
        objects.extend(
            [
                box(
                    f"LANEKIT_{role}_{variant}_Recess",
                    (2.70, 0.62, height * 0.82),
                    (0.75, front_y + 0.48, height * 0.45),
                    mats["deep"],
                    0.018,
                ),
                box(
                    f"LANEKIT_{role}_{variant}_Door",
                    (1.18, 0.035, height * 0.72),
                    (0.20, front_y + 0.17, height * 0.45),
                    mats["glass"],
                    0.012,
                ),
                box(
                    f"LANEKIT_{role}_{variant}_Bench",
                    (1.02, 0.42, 0.12),
                    (1.58, front_y + 0.02, 0.65),
                    mats["cedar"],
                    0.025,
                ),
            ]
        )
        for side, x in ((-1, -3.15), (1, 4.52)):
            objects.append(
                box(
                    f"LANEKIT_{role}_{variant}_GroundWing_{side:+d}",
                    (5.55 if side < 0 else 2.88, 0.24, height - 0.10),
                    (x, front_y + 0.12, height / 2),
                    mats["cedar"],
                    0.022,
                )
            )
    else:
        objects.append(
            box(
                f"LANEKIT_{role}_{variant}_OccupiedGlass",
                (11.66, 0.035, height - 0.16),
                (0.0, front_y + 0.42, height / 2),
                mats["glass"],
                0.012,
            )
        )
        slat_count = {
            "typical_a": 69,
            "typical_b": 61,
            "typical_c": 75,
            "crown": 69,
        }[variant]
        objects.extend(
            add_lane_screen_front(
                name=f"LANEKIT_{role}_{variant}_Screen",
                width=11.92,
                front_y=front_y,
                z0=0.05,
                z1=height - 0.05,
                mats=mats,
                slat_count=slat_count,
            )
        )
    return objects


def add_villa_window(
    *,
    name: str,
    centre_x: float,
    sill_z: float,
    width: float,
    height: float,
    front_y: float,
    mats: dict[str, bpy.types.Material],
    juliet: bool = False,
    dense_grille: bool = True,
) -> list[bpy.types.Object]:
    """Deep timber sash with a separate forged-iron security layer."""
    objects: list[bpy.types.Object] = []
    recess_y = front_y + 0.42
    x0, x1 = centre_x - width / 2, centre_x + width / 2
    z0, z1 = sill_z, sill_z + height
    room_mat = mats["room_warm"] if sum(ord(char) for char in name) % 3 else mats["room_dim"]
    objects.extend(
        [
            box(
                f"{name}_OccupiedRoom",
                (width - 0.18, 0.030, height - 0.18),
                (centre_x, recess_y + 0.10, (z0 + z1) * 0.5),
                room_mat,
                0.008,
            ),
            box(
                f"{name}_PhysicalGlass",
                (width - 0.18, 0.030, height - 0.18),
                (centre_x, recess_y, (z0 + z1) * 0.5),
                mats["glass"],
                0.010,
            ),
            box(
                f"{name}_StoneLintel",
                (width + 0.34, 0.28, 0.20),
                (centre_x, front_y + 0.02, z1 + 0.10),
                mats["stone"],
                0.032,
            ),
            box(
                f"{name}_StoneSill",
                (width + 0.30, 0.34, 0.18),
                (centre_x, front_y - 0.02, z0 - 0.09),
                mats["stone"],
                0.032,
            ),
            box(
                f"{name}_LeftTimberFrame",
                (0.11, 0.14, height),
                (x0 + 0.055, recess_y - 0.05, (z0 + z1) * 0.5),
                mats["timber"],
                0.018,
            ),
            box(
                f"{name}_RightTimberFrame",
                (0.11, 0.14, height),
                (x1 - 0.055, recess_y - 0.05, (z0 + z1) * 0.5),
                mats["timber"],
                0.018,
            ),
            box(
                f"{name}_TimberMullion",
                (0.075, 0.12, height - 0.08),
                (centre_x, recess_y - 0.06, (z0 + z1) * 0.5),
                mats["timber"],
                0.012,
            ),
            box(
                f"{name}_TimberTransom",
                (width - 0.08, 0.12, 0.075),
                (centre_x, recess_y - 0.06, z0 + height * 0.53),
                mats["timber"],
                0.012,
            ),
        ]
    )
    grille_y = front_y - (0.23 if juliet else 0.13)
    bar_count = 5 if dense_grille else 3
    for index in range(bar_count):
        x = x0 + width * (index + 1) / (bar_count + 1)
        objects.append(
            cylinder(
                f"{name}_ForgedVerticalBar_{index}",
                0.016,
                height + (0.26 if juliet else 0.04),
                (x, grille_y, (z0 + z1) * 0.5),
                mats["iron"],
                vertices=10,
            )
        )
    for index, z in enumerate(
        (z0 + 0.12, z0 + height * 0.52, z1 - 0.10)
    ):
        objects.append(
            box(
                f"{name}_ForgedHorizontalRail_{index}",
                (width + 0.14, 0.040, 0.030),
                (centre_x, grille_y, z),
                mats["iron"],
                0.012,
            )
        )
    if dense_grille:
        # Security grilles in the reference are shallow cages, not flat bar
        # decals. Tie the outer rail plane back into the stucco reveal.
        grille_y = front_y - 0.31
        for side in (-1, 1):
            x = centre_x + side * (width * 0.5 + 0.04)
            for index, z in enumerate(
                (z0 + 0.13, z0 + height * 0.52, z1 - 0.11)
            ):
                objects.append(
                    rectangular_beam(
                        f"{name}_CageReturn_{side:+d}_{index}",
                        (x, front_y + 0.02, z),
                        (x, grille_y, z),
                        0.030,
                        mats["iron"],
                        depth=0.032,
                    )
                )
        for index in range(bar_count):
            x = x0 + width * (index + 1) / (bar_count + 1)
            objects.append(
                cylinder(
                    f"{name}_ProjectedForgedVerticalBar_{index}",
                    0.018,
                    height + 0.08,
                    (x, grille_y, (z0 + z1) * 0.5),
                    mats["iron"],
                    vertices=10,
                )
            )
    if juliet:
        projection = 0.34
        objects.extend(
            [
                box(
                    f"{name}_JulietTopRail",
                    (width + 0.30, projection, 0.070),
                    (centre_x, front_y - projection * 0.5, z0 + 1.02),
                    mats["iron"],
                    0.012,
                ),
                box(
                    f"{name}_JulietBottomRail",
                    (width + 0.30, projection, 0.060),
                    (centre_x, front_y - projection * 0.5, z0 + 0.10),
                    mats["iron"],
                    0.012,
                ),
            ]
        )
    return objects


def add_villa_portal(
    *,
    name: str,
    centre_x: float,
    sill_z: float,
    width: float,
    height: float,
    front_y: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    radius = width * 0.5
    spring_z = sill_z + height - radius
    recess_y = front_y + 0.55
    objects.extend(
        [
            arched_panel(
                f"{name}_DarkTimberDoor",
                centre_x,
                recess_y,
                sill_z + 0.06,
                width - 0.28,
                height - 0.18,
                mats["timber"],
                36,
            ),
            box(
                f"{name}_LeftStonePier",
                (0.34, 0.42, spring_z - sill_z + 0.26),
                (
                    centre_x - radius - 0.06,
                    front_y - 0.04,
                    sill_z + (spring_z - sill_z) * 0.5 + 0.13,
                ),
                mats["stone"],
                0.045,
            ),
            box(
                f"{name}_RightStonePier",
                (0.34, 0.42, spring_z - sill_z + 0.26),
                (
                    centre_x + radius + 0.06,
                    front_y - 0.04,
                    sill_z + (spring_z - sill_z) * 0.5 + 0.13,
                ),
                mats["stone"],
                0.045,
            ),
            box(
                f"{name}_StonePortalEntablature",
                (width + 1.08, 0.44, 0.30),
                (centre_x, front_y - 0.04, sill_z + height + 0.16),
                mats["stone"],
                0.045,
            ),
            box(
                f"{name}_StoneStepLower",
                (width + 1.25, 0.86, 0.16),
                (centre_x, front_y - 0.28, sill_z + 0.08),
                mats["stone"],
                0.035,
            ),
            box(
                f"{name}_StoneStepUpper",
                (width + 0.82, 0.60, 0.16),
                (centre_x, front_y - 0.12, sill_z + 0.23),
                mats["stone"],
                0.035,
            ),
        ]
    )
    segments = 24
    for index in range(segments):
        a0 = math.pi * index / segments
        a1 = math.pi * (index + 1) / segments
        objects.append(
            rectangular_beam(
                f"{name}_StoneArchVoussoir_{index}",
                (
                    centre_x + math.cos(a0) * (radius + 0.08),
                    front_y - 0.08,
                    spring_z + math.sin(a0) * (radius + 0.08),
                ),
                (
                    centre_x + math.cos(a1) * (radius + 0.08),
                    front_y - 0.08,
                    spring_z + math.sin(a1) * (radius + 0.08),
                ),
                0.27,
                mats["stone"],
                depth=0.30,
            )
        )
    for side in (-1, 1):
        for row in range(4):
            objects.append(
                box(
                    f"{name}_CarvedDoorPanel_{side:+d}_{row}",
                    (width * 0.30, 0.050, 0.44),
                    (
                        centre_x + side * width * 0.20,
                        recess_y - 0.04,
                        sill_z + 0.52 + row * 0.49,
                    ),
                    mats["timber"],
                    0.025,
                )
            )
    objects.append(
        box(
            f"{name}_DoorCentreStile",
            (0.095, 0.065, height - 0.32),
            (centre_x, recess_y - 0.04, sill_z + height * 0.48),
            mats["iron"],
            0.012,
        )
    )
    return objects


def add_iron_balcony(
    *,
    name: str,
    centre_x: float,
    width: float,
    slab_z: float,
    front_y: float,
    mats: dict[str, bpy.types.Material],
    corbel_drop: float = 0.62,
) -> list[bpy.types.Object]:
    projection = 0.82
    outer_y = front_y - projection
    objects = [
        box(
            f"{name}_StoneSlab",
            (width, projection, 0.18),
            (centre_x, front_y - projection * 0.5, slab_z),
            mats["stone"],
            0.035,
        ),
        box(
            f"{name}_ForgedTopRail",
            (width - 0.10, 0.070, 0.070),
            (centre_x, outer_y, slab_z + 1.02),
            mats["iron"],
            0.012,
        ),
        box(
            f"{name}_ForgedBottomRail",
            (width - 0.10, 0.060, 0.060),
            (centre_x, outer_y, slab_z + 0.18),
            mats["iron"],
            0.012,
        ),
    ]
    post_count = max(7, int(width / 0.28))
    for index in range(post_count):
        x = centre_x - width * 0.45 + width * 0.90 * index / max(
            1, post_count - 1
        )
        objects.append(
            cylinder(
                f"{name}_TurnedIronBaluster_{index}",
                0.026,
                0.82,
                (x, outer_y, slab_z + 0.60),
                mats["iron"],
                vertices=10,
            )
        )
        objects.append(
            sphere(
                f"{name}_BalusterKnuckle_{index}",
                0.052,
                (x, outer_y, slab_z + 0.60),
                mats["iron"],
                (1.0, 0.72, 1.0),
                segments=10,
                rings=5,
            )
        )
    for index, x in enumerate(
        (centre_x - width * 0.38, centre_x + width * 0.38)
    ):
        objects.append(
            rectangular_beam(
                f"{name}_StoneCorbel_{index}",
                (x, front_y - 0.08, slab_z - corbel_drop),
                (x, outer_y + 0.10, slab_z - 0.05),
                0.18,
                mats["stone"],
                depth=0.20,
            )
        )
    return objects


def add_brick_patch(
    *,
    name: str,
    centre_x: float,
    centre_z: float,
    columns: int,
    rows: int,
    front_y: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    """Recessed brick repair with a ragged, chipped plaster boundary."""
    objects: list[bpy.types.Object] = [
        box(
            f"{name}_RecessedMortarBed",
            (
                columns * 0.31 * 0.88,
                0.020,
                rows * 0.145 * 0.88,
            ),
            (centre_x, front_y - 0.008, centre_z),
            mats["stone"],
            0.010,
        )
    ]
    brick_width = 0.31
    brick_height = 0.145
    for row in range(rows):
        edge_loss = abs(row - (rows - 1) / 2) / max(1.0, rows / 2)
        irregular_loss = 1 if (row * 5 + columns) % 4 == 0 else 0
        row_columns = max(
            2,
            columns - int(edge_loss * columns * 0.42) - irregular_loss,
        )
        offset = brick_width * 0.5 if row % 2 else 0.0
        for column in range(row_columns):
            if (row * 7 + column * 5) % 13 == 0:
                continue
            if (
                column in {0, row_columns - 1}
                and (row * 3 + column * 7 + columns) % 5 in {0, 1}
            ):
                continue
            if row in {0, rows - 1} and column % 3 == 0:
                continue
            jitter = math.sin((row + 1) * 11.0 + (column + 2) * 7.0)
            x = (
                centre_x
                - row_columns * brick_width * 0.5
                + brick_width * (column + 0.5)
                + offset * 0.45
                + jitter * 0.018
            )
            z = (
                centre_z
                - rows * brick_height * 0.5
                + brick_height * (row + 0.5)
                + math.cos((row + 3) * 5.0 + column * 3.0) * 0.010
            )
            objects.append(
                box(
                    f"{name}_ExposedBrick_{row}_{column}",
                    (
                        brick_width - 0.026 - abs(jitter) * 0.015,
                        0.028,
                        brick_height - 0.022,
                    ),
                    (x, front_y - 0.020, z),
                    mats["brick"],
                    0.008,
                )
            )
    return objects


def ridge_x_roof(
    name: str,
    *,
    width: float,
    depth: float,
    base_z: float,
    rise: float,
    mat: bpy.types.Material,
    gable_mat: bpy.types.Material,
) -> bpy.types.Object:
    """Low roof prism with ridge along X, suited to a long front facade."""
    half_w, half_d = width / 2, depth / 2
    eave_z = base_z + 0.08
    vertices = [
        (-half_w, -half_d, base_z),
        (half_w, -half_d, base_z),
        (half_w, half_d, base_z),
        (-half_w, half_d, base_z),
        (-half_w, -half_d, eave_z),
        (half_w, -half_d, eave_z),
        (half_w, half_d, eave_z),
        (-half_w, half_d, eave_z),
        (-half_w, 0.0, base_z + rise),
        (half_w, 0.0, base_z + rise),
    ]
    faces = [
        (0, 3, 2, 1),
        (4, 5, 9, 8),
        (8, 9, 6, 7),
        (0, 4, 8, 7, 3),
        (1, 2, 6, 9, 5),
    ]
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(mat)
    mesh.materials.append(gable_mat)
    mesh.polygons[3].material_index = 1
    mesh.polygons[4].material_index = 1
    uv = mesh.uv_layers.new(name="UVMap")
    for polygon in mesh.polygons:
        for loop_index in polygon.loop_indices:
            coordinate = mesh.vertices[
                mesh.loops[loop_index].vertex_index
            ].co
            if polygon.index in (1, 2):
                u = (coordinate.x + half_w) / width * 4.0
                v = (
                    abs(coordinate.y) / max(half_d, 0.001) * 3.0
                    + (0.0 if polygon.index == 1 else 3.0)
                )
            else:
                u = (coordinate.y + half_d) / depth
                v = (coordinate.z - base_z) / max(rise, 0.001)
            uv.data[loop_index].uv = (u, v)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bevel = obj.modifiers.new("TerracottaEdgeSoftening", "BEVEL")
    bevel.width = 0.030
    bevel.segments = 2
    return obj


def add_tower_arch(
    *,
    name: str,
    centre_x: float,
    front_y: float,
    sill_z: float,
    width: float,
    height: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects = [
        arched_panel(
            f"{name}_DeepOpenArch",
            centre_x,
            front_y - 0.055,
            sill_z,
            width,
            height,
            mats["deep"],
            28,
        )
    ]
    radius = width / 2
    spring_z = sill_z + height - radius
    for side in (-1, 1):
        objects.append(
            box(
                f"{name}_StoneJamb_{side:+d}",
                (0.16, 0.16, height - radius),
                (
                    centre_x + side * (radius + 0.02),
                    front_y - 0.10,
                    sill_z + (height - radius) * 0.5,
                ),
                mats["stone"],
                0.025,
            )
        )
    for index in range(16):
        a0 = math.pi * index / 16
        a1 = math.pi * (index + 1) / 16
        objects.append(
            rectangular_beam(
                f"{name}_ArchRing_{index}",
                (
                    centre_x + math.cos(a0) * (radius + 0.02),
                    front_y - 0.10,
                    spring_z + math.sin(a0) * (radius + 0.02),
                ),
                (
                    centre_x + math.cos(a1) * (radius + 0.02),
                    front_y - 0.10,
                    spring_z + math.sin(a1) * (radius + 0.02),
                ),
                0.15,
                mats["stone"],
                depth=0.16,
            )
        )
    return objects


def villa_fixed(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    cfg = FAMILIES["spanish-colonial-villa"]
    front_y = cfg["front_y"]
    objects: list[bpy.types.Object] = []
    objects.append(
        box(
            "VILLA_AgedStuccoStructuralCore",
            (17.10, 12.20, 9.05),
            (0.0, 0.65, 4.525),
            mats["stucco"],
            0.055,
        )
    )
    ground_windows = [
        (-5.70, 0.78, 1.20, 1.72),
        (-3.00, 0.78, 1.16, 1.72),
        (3.05, 0.78, 1.16, 1.72),
        (5.85, 0.78, 1.20, 1.72),
    ]
    middle_windows = [
        (-6.05, 3.55, 1.38, 2.05),
        (-3.05, 3.72, 1.15, 1.72),
        (0.05, 3.72, 1.15, 1.72),
        (3.05, 3.72, 1.15, 1.72),
        (6.05, 3.55, 1.38, 2.05),
    ]
    upper_windows = [
        (-6.00, 6.72, 1.04, 1.48),
        (-3.05, 6.72, 1.04, 1.48),
        (0.05, 6.45, 1.30, 1.86),
        (3.05, 6.72, 1.04, 1.48),
        (6.05, 6.72, 1.04, 1.48),
    ]
    portal = (0.05, 0.06, 2.20, 3.18)
    openings = [
        (
            centre - width / 2,
            centre + width / 2,
            sill,
            sill + height,
        )
        for centre, sill, width, height in (
            ground_windows + middle_windows + upper_windows
        )
    ]
    openings.append(
        (
            portal[0] - portal[2] / 2,
            portal[0] + portal[2] / 2,
            portal[1],
            portal[1] + portal[3],
        )
    )
    objects.extend(
        add_registered_front_wall(
            name="VILLA_MainStuccoFacade",
            x0=-8.45,
            x1=8.45,
            z0=0.0,
            z1=9.02,
            y=front_y,
            openings=openings,
            construction_mat=mats["stucco"],
            registered_mat=mats["stucco"],
            surface_uv_bounds=(0.0, 0.0, 3.2, 3.2),
        )
    )
    objects.append(
        registered_panel(
            "VILLA_RegisteredOccupiedDepth",
            x0=-9.0,
            x1=9.0,
            y=front_y + 0.55,
            z0=0.0,
            z1=12.8,
            mat=mats["underlay"],
            model_x_bounds=(-9.0, 9.0),
            model_z_bounds=(0.0, 12.8),
            source_uv_bounds=(0.045, 0.082, 0.958, 0.940),
        )
    )
    for index, (centre, sill, width, height) in enumerate(
        ground_windows + middle_windows + upper_windows
    ):
        is_middle = len(ground_windows) <= index < len(
            ground_windows + middle_windows
        )
        upper_index = index - len(ground_windows + middle_windows)
        objects.extend(
            add_villa_window(
                name=f"VILLA_RecessedBarredSash_{index}",
                centre_x=centre,
                sill_z=sill,
                width=width,
                height=height,
                front_y=front_y,
                mats=mats,
                juliet=(
                    upper_index in {0, 1, 3, 4}
                    if upper_index >= 0
                    else False
                ),
                dense_grille=not (
                    upper_index >= 0 or (is_middle and centre == 0.05)
                ),
            )
        )
    objects.extend(
        add_villa_portal(
            name="VILLA_DeepCentralStonePortal",
            centre_x=portal[0],
            sill_z=portal[1],
            width=portal[2],
            height=portal[3],
            front_y=front_y,
            mats=mats,
        )
    )
    objects.extend(
        add_iron_balcony(
            name="VILLA_CentralForgedIronBalcony",
            centre_x=0.05,
            width=3.65,
            slab_z=6.35,
            front_y=front_y,
            mats=mats,
        )
    )
    # Pale masonry shoulders match the low side wings in the goalpost.
    for side in (-1, 1):
        objects.append(
            box(
                f"VILLA_LimestoneSideWing_{side:+d}",
                (1.25, 13.20, 3.55),
                (side * 8.38, 0.20, 1.775),
                mats["stone"],
                0.055,
            )
        )
        objects.append(
            box(
                f"VILLA_SideWingTileRoof_{side:+d}",
                (1.55, 13.45, 0.30),
                (side * 8.38, 0.15, 3.68),
                mats["roof"],
                0.035,
            )
        )
    for patch in (
        ("LeftLarge", -4.80, 2.35, 9, 8),
        ("LeftUpper", -2.50, 7.78, 6, 5),
        ("CentreMid", 1.30, 4.05, 7, 5),
        ("RightLow", 2.15, 1.78, 6, 5),
        ("RightUpper", 5.20, 7.75, 5, 4),
    ):
        objects.extend(
            add_brick_patch(
                name=f"VILLA_ExposedBrickPatch_{patch[0]}",
                centre_x=patch[1],
                centre_z=patch[2],
                columns=patch[3],
                rows=patch[4],
                front_y=front_y,
                mats=mats,
            )
        )

    main_roof = ridge_x_roof(
        "VILLA_LowTerracottaMainRoof",
        width=17.65,
        depth=13.85,
        base_z=8.98,
        rise=1.28,
        mat=mats["roof"],
        gable_mat=mats["stucco"],
    )
    objects.append(main_roof)
    for index in range(39):
        x = -8.45 + 16.90 * index / 38
        tile = cylinder(
            f"VILLA_PhysicalBarrelEaveTile_{index}",
            0.105,
            0.40,
            (x, -7.00, 9.08),
            mats["roof"],
            vertices=16,
        )
        tile.rotation_euler.x = math.radians(90)
        objects.append(tile)
    # Continuous convex tile runners establish real barrel relief across both
    # roof pitches; the image-derived PBR supplies the smaller overlapping
    # courses. This keeps the aerial silhouette from reading as a flat orange
    # texture card.
    for index in range(35):
        x = -8.32 + 16.64 * index / 34
        for side in (-1, 1):
            objects.append(
                round_beam(
                    f"VILLA_PhysicalBarrelRoofRunner_{side:+d}_{index}",
                    (x, side * 6.88, 9.10),
                    (x, 0.0, 10.30),
                    0.050,
                    mats["roof"],
                    vertices=12,
                )
            )
    objects.append(
        round_beam(
            "VILLA_PhysicalRidgeCap",
            (-8.55, 0.0, 10.34),
            (8.55, 0.0, 10.34),
            0.115,
            mats["roof"],
            vertices=16,
        )
    )
    objects.extend(
        [
            box(
                "VILLA_LeftBellTowerBody",
                (3.20, 4.10, 3.55),
                (-6.35, -4.96, 10.72),
                mats["stucco"],
                0.050,
            ),
            box(
                "VILLA_BellTowerStoneDatum",
                (3.42, 4.28, 0.22),
                (-6.35, -4.96, 9.10),
                mats["stone"],
                0.035,
            ),
        ]
    )
    for index, x in enumerate((-6.90, -5.78)):
        objects.extend(
            add_tower_arch(
                name=f"VILLA_BellTowerArch_{index}",
                centre_x=x,
                front_y=-7.03,
                sill_z=10.05,
                width=0.82,
                height=1.72,
                mats=mats,
            )
        )
    tower_roof = gable_roof(
        "VILLA_BellTowerTerracottaGable",
        centre_x=-6.35,
        width=3.58,
        depth=4.48,
        base_z=12.38,
        rise=0.82,
        roof_mat=mats["roof"],
        gable_mat=mats["stucco"],
    )
    tower_roof.location.y = -4.96
    objects.append(tower_roof)
    # The visible bronze bell is suspended in the right tower arch.
    bpy.ops.mesh.primitive_cone_add(
        vertices=32,
        radius1=0.34,
        radius2=0.20,
        depth=0.55,
        location=(-5.78, -7.16, 10.92),
    )
    bell = bpy.context.object
    bell.name = "VILLA_PhysicalBronzeBell"
    bell.data.materials.append(mats["bronze"])
    objects.extend(
        [
            bell,
            cylinder(
                "VILLA_BellClapper",
                0.055,
                0.30,
                (-5.78, -7.16, 10.56),
                mats["iron"],
                vertices=12,
            ),
            box(
                "VILLA_BellSuspensionBeam",
                (0.72, 0.12, 0.12),
                (-5.78, -7.14, 11.32),
                mats["timber"],
                0.018,
            ),
        ]
    )
    # Secondary elevations retain recessed sash and masonry datums.
    for side in (-1, 1):
        x = side * 8.48
        for floor, sill in enumerate((0.80, 3.75, 6.72)):
            for bay, y in enumerate((-2.65, 1.05, 4.10)):
                objects.extend(
                    add_secondary_opening(
                        name=f"VILLA_SideSash_{side:+d}_{floor}_{bay}",
                        axis="x",
                        fixed_coordinate=x,
                        lateral=y,
                        sill_z=sill,
                        width=1.10,
                        height=1.55,
                        outward_sign=side,
                        mats=mats,
                    )
                )
    for floor, sill in enumerate((0.80, 3.75, 6.72)):
        for bay, x in enumerate((-5.8, -2.0, 2.0, 5.8)):
            objects.extend(
                add_secondary_opening(
                    name=f"VILLA_RearSash_{floor}_{bay}",
                    axis="y",
                    fixed_coordinate=6.82,
                    lateral=x,
                    sill_z=sill,
                    width=1.08,
                    height=1.52,
                    outward_sign=1,
                    mats=mats,
                )
            )
    return objects


def villa_fallback_module(
    role: str,
    variant: str,
    height: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    width, depth = 18.0, 14.0
    front_y = -depth / 2
    objects: list[bpy.types.Object] = []
    if role == "roof":
        objects.append(
            ridge_x_roof(
                f"VILLAKIT_{role}_{variant}_TerracottaRoof",
                width=width,
                depth=depth,
                base_z=0.02,
                rise=height - 0.06,
                mat=mats["roof"],
                gable_mat=mats["stucco"],
            )
        )
        return objects
    objects.append(
        box(
            f"VILLAKIT_{role}_{variant}_StuccoEnvelope",
            (width, depth, height),
            (0.0, 0.0, height / 2),
            mats["stucco"],
            0.045,
        )
    )
    if role == "podium":
        objects.extend(
            add_villa_portal(
                name=f"VILLAKIT_{role}_{variant}_Portal",
                centre_x=0.0,
                sill_z=0.05,
                width=2.10,
                height=min(3.0, height - 0.08),
                front_y=front_y,
                mats=mats,
            )
        )
        centres = (-6.0, -3.2, 3.2, 6.0)
    else:
        centres = {
            "typical_a": (-6.0, -3.0, 0.0, 3.0, 6.0),
            "typical_b": (-6.2, -2.1, 2.1, 6.2),
            "typical_c": (-6.0, -3.6, -1.2, 1.8, 4.4, 6.3),
            "crown": (-6.0, -3.0, 0.0, 3.0, 6.0),
        }[variant]
    for index, x in enumerate(centres):
        objects.extend(
            add_villa_window(
                name=f"VILLAKIT_{role}_{variant}_Window_{index}",
                centre_x=x,
                sill_z=max(0.62, (height - 1.55) * 0.50),
                width=1.10,
                height=min(1.55, height - 0.82),
                front_y=front_y,
                mats=mats,
                juliet=role == "crown" or (role == "floor" and index % 2 == 0),
                dense_grille=role != "crown",
            )
        )
    if role == "floor" and variant == "typical_a":
        objects.extend(
            add_iron_balcony(
                name=f"VILLAKIT_{role}_{variant}_CentralBalcony",
                centre_x=0.0,
                width=3.4,
                slab_z=0.18,
                front_y=front_y,
                mats=mats,
                corbel_drop=0.08,
            )
        )
    return objects


FIXED_BUILDERS: dict[
    str,
    Callable[[dict[str, bpy.types.Material]], list[bpy.types.Object]],
] = {
    "swiss-chalet-residence": chalet_fixed,
    "timber-screen-lanehouse": lanehouse_fixed,
    "spanish-colonial-villa": villa_fixed,
}


def fallback_module(
    family: str,
    role: str,
    variant: str,
    height: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    if family == "swiss-chalet-residence":
        return chalet_fallback_module(role, variant, height, mats)
    if family == "timber-screen-lanehouse":
        return lanehouse_fallback_module(role, variant, height, mats)
    if family == "spanish-colonial-villa":
        return villa_fallback_module(role, variant, height, mats)
    raise ValueError(f"unsupported Wave 9 family {family}")


def render_views(
    family: str,
    folder: Path,
    *,
    view_set: str,
) -> list[str]:
    setup_render()
    scene = bpy.context.scene
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.exposure = 1.15
    cfg = FAMILIES[family]
    width, depth, height = cfg["dimensions"]
    distance = max(width, depth)
    background = scene.world.node_tree.nodes.get("Background")
    if background:
        background.inputs["Color"].default_value = (0.34, 0.36, 0.37, 1.0)
        background.inputs["Strength"].default_value = 0.86
    ground = bpy.data.materials.get("MAT_W3_Ground")
    if ground and ground.use_nodes:
        ground.node_tree.nodes["Principled BSDF"].inputs[
            "Base Color"
        ].default_value = (0.29, 0.28, 0.26, 1.0)
    bpy.ops.object.light_add(
        type="SUN",
        location=(-width * 1.2, -distance * 1.8, height * 3.2),
    )
    sun = bpy.context.object
    sun.name = "PRESENTATION_W9_SoftSun"
    sun.data.energy = 1.45
    sun.data.angle = math.radians(18.0)
    sun.rotation_euler = (
        Vector((0.0, 0.0, height * 0.4)) - sun.location
    ).to_track_quat("-Z", "Y").to_euler()
    views = {
        "preview": (
            (width * 0.82, -distance * 2.52, height * 0.92),
            (0.0, -0.35, height * 0.43),
            50,
        ),
        "street": (
            (width * 0.30, -distance * 2.85, height * 0.38),
            (0.0, -0.65, height * 0.40),
            50,
        ),
        "front_corner_oblique": (
            (-width * 0.94, -distance * 1.72, height * 0.78),
            (0.0, 0.0, height * 0.40),
            52,
        ),
        "rear_corner_oblique": (
            (width * 0.90, distance * 1.80, height * 0.84),
            (0.0, 0.15, height * 0.42),
            52,
        ),
        "aerial": (
            (width * 1.0, -distance * 1.45, height * 2.28),
            (0.0, 0.0, height * 0.34),
            50,
        ),
        "facade_close": (
            (width * 0.05, -distance * 1.67, height * 0.43),
            (0.0, -5.15, height * 0.43),
            60,
        ),
        "identity_close": (
            (-width * 0.30, -distance * 1.20, height * 0.60),
            cfg["close_target"],
            62,
        ),
        "context": (
            (width * 0.22, -distance * 2.55, height * 0.82),
            (0.0, 0.0, height * 0.40),
            55,
        ),
    }
    if family == "timber-screen-lanehouse":
        views["street"] = (
            (0.0, -29.0, height * 0.43),
            (0.0, -2.1, height * 0.49),
            43,
        )
        views["front_corner_oblique"] = (
            (-width * 0.94, -24.5, height * 0.78),
            (0.0, -0.35, height * 0.45),
            46,
        )
    elif family == "spanish-colonial-villa":
        views["street"] = (
            (width * 0.08, -40.0, height * 0.38),
            (0.0, -5.8, height * 0.44),
            45,
        )
    selected = (
        {"preview", "street", "front_corner_oblique", "aerial", "identity_close"}
        if view_set == "pilot"
        else set(views)
    )

    # Transparent physical panes are proof-rendered as low-alpha surfaces so
    # their registered room-depth plates remain legible. Export has already
    # happened, so glTF retains the physical transmission profile.
    snapshots: list[tuple[bpy.types.Material, bpy.types.Node, float, float, str]] = []
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
            )
        )
        bsdf.inputs["Alpha"].default_value = 0.22
        mat.diffuse_color = (*tuple(mat.diffuse_color)[:3], 0.22)
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
            filename = f"{family}_{role}.png"
            scene.render.filepath = str(folder / filename)
            bpy.ops.render.render(write_still=True)
            rendered.append(filename)
    finally:
        for mat, bsdf, alpha, transmission_value, method in snapshots:
            bsdf.inputs["Alpha"].default_value = alpha
            transmission = bsdf.inputs.get("Transmission Weight")
            if transmission:
                transmission.default_value = transmission_value
            if hasattr(mat, "surface_render_method"):
                mat.surface_render_method = method
            mat.diffuse_color = (*tuple(mat.diffuse_color)[:3], 1.0)
    delete_objects(
        [obj for obj in list(bpy.data.objects) if obj.name.startswith("PRESENTATION_")]
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
    family: str,
    role: str,
    variant: str,
    filename: str,
    height: float,
    objects: list[bpy.types.Object],
    size_bytes: int,
    skin: dict,
) -> dict:
    cfg = FAMILIES[family]
    width, depth, _ = cfg["dimensions"]
    repeatable = role == "floor"
    return {
        "role": role,
        "variant_key": variant,
        "assembly_class": "repeatable_middle" if repeatable else "fixed_semantic",
        "fixed_semantic": not repeatable,
        "lod": 0,
        "allowed_levels": [],
        "filename": filename,
        "module_family": family,
        "width_m": width,
        "depth_m": depth,
        "height_m": height,
        "floor_height_m": cfg["floor_height_m"],
        "repeatable_z": repeatable,
        "allow_inset_footprint": True,
        "triangle_count": evaluated_triangle_count(objects),
        "material_count": material_count(objects),
        "texture_keys": sorted(skin["zones"]),
        "ao_baked": True,
        "size_bytes": size_bytes,
    }


def provenance(family: str) -> dict:
    cfg = FAMILIES[family]
    return {
        "kind": (
            "catalogue_goalpost_plus_imagegen_reference_package_and_"
            "authored_residential_construction"
        ),
        "catalogue_archetype_id": cfg["archetype_id"],
        "catalogue_variant_id": cfg["variant_id"],
        "goalpost": cfg["goalpost"],
        "goalpost_local_source": "textures/source/archetype-goalpost.png",
        "orthographic_elevation": "textures/source/elevation-source.png",
        "reference_underlay": "textures/source/occupied-depth-source.png",
        "reference_generation": "textures/source/reference-generation.json",
        "registered_openings": "textures/source/registered-openings.json",
        "registered_bands": "textures/source/registered-bands.json",
        "elevation_source": f"/families/{family}/elevation.jpg",
        "skin_manifest": "textures/skin_manifest.json",
        "generator": (
            "tools/archetype_compiler/"
            "generate_wave9_single_family_families.py"
        ),
        "reference_method": (
            "hard catalogue goalpost, rectified registered elevation, physical "
            "residential openings and construction, occupied-depth underlay, "
            "and finite street/oblique/aerial comparison"
        ),
    }


def facade_contract(family: str, skin: dict) -> dict:
    cfg = FAMILIES[family]
    return {
        "schema": "facade-sheet@5",
        "source_directory": f"/families/{family}",
        "model": "gpt-image-2",
        "style_reference": "elevation.jpg",
        "goalpost_reference": cfg["goalpost"],
        "goalpost_policy": (
            "The catalogue card fixes occupied levels, roof/threshold silhouette, "
            "opening scale, construction hierarchy and material identity."
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
                "The whole detached house remains fixed in-band. Larger parcels "
                "repeat complete residential bays in the family-shaped fallback."
            ),
        },
        "delivery": {
            "near_atlas_width_px": 2048,
            "far_atlas_width_px": 1024,
            "near_usage": (
                "registered skin plus physical windows, threshold, balconies, "
                "eaves, roof construction and occupied room depth"
            ),
            "far_usage": "city-scale render-locked archetype material reference",
        },
        "assembly_contract": {
            "fixed": [
                "podium/entrance",
                "corner returns",
                "stone threshold",
                "residential windows",
                "balconies/porches",
                "crown",
                "roof",
                *cfg["kits"],
            ],
            "repeatable": ["typical_a", "typical_b", "typical_c"],
            "side_elevations": (
                "Floor datums, material transitions, sash scale, eave and roof "
                "logic wrap every elevation; the ceremonial entrance stays fixed."
            ),
            "elevation_coverage": {
                "front": cfg["identity"],
                "left": "related occupied residential return with true sash depth",
                "right": "related occupied residential return with true sash depth",
                "rear": "quieter occupied garden/service elevation",
                "roof": cfg["silhouette"],
            },
            "variation_policy": (
                "Mild X/Y scaling keeps the whole house. Larger or distorted "
                "drawings use the family-shaped modular streetwall fallback."
            ),
        },
        "assets": {
            "skin_manifest": "textures/skin_manifest.json",
            "source": skin["source"],
            "near": skin["zones"]["facade"]["near"],
            "far": skin["zones"]["facade"]["far"],
            "sources": skin["sources"],
        },
        "reference_registration": skin["reference_registration"],
    }


def write_metadata(
    family: str,
    folder: Path,
    skin: dict,
    modules: list[dict],
    fixed_triangles: int,
    fixed_materials: int,
    assembled_path: Path,
    renders: list[str],
) -> None:
    cfg = FAMILIES[family]
    width, depth, height = cfg["dimensions"]
    min_floors, max_floors, native_floors = cfg["floors"]
    footprint = {
        "preferredProfiles": ["rectangle"],
        "minimumPreferredProfiles": 1,
        "profileRationale": cfg["profile_rationale"],
        "fixedLandmarkScaleBand": cfg["fixed_band"],
        **cfg["footprint"],
        "profiles": {"rectangle": cfg["footprint"]},
    }
    assembled = {
        "filename": assembled_path.name,
        "floors": native_floors,
        "uses_setback": False,
        "uses_crown": True,
        "height_m": height,
        "triangle_count": fixed_triangles,
        "material_count": fixed_materials,
        "stack": [
            {
                "role": "assembled",
                "variant_key": "fixed_landmark",
                "level": 0,
                "z_m": 0.0,
                "height_m": height,
            }
        ],
        "footprint_profile": "rectangle",
        "footprint_target": {
            "width_m": width,
            "depth_m": depth,
            "wing_depth_m": depth,
            "segments": [
                {
                    "id": "detached_house",
                    "centre_x_m": 0.0,
                    "centre_y_m": 0.0,
                    "length_m": width,
                    "thickness_m": depth,
                    "rotation_degrees": 0.0,
                }
            ],
        },
        "massing_graph": {
            "type": "fixed_landmark",
            "silhouette": cfg["silhouette"],
        },
        "texture_keys": sorted(skin["zones"]),
        "ao_baked": True,
    }
    source = provenance(family)
    manifest = {
        "manifest_schema": 3,
        "grammar_schema_version": 3,
        "generator": {
            "name": (
                "archetype_compiler/generate_wave9_single_family_families.py"
            ),
            "version": "1.0.0",
            "blender_version": bpy.app.version_string,
            "render_engine": "BLENDER_EEVEE",
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "family": family,
        "archetype_id": cfg["archetype_id"],
        "archetype_label": cfg["label"],
        "variant_id": cfg["variant_id"],
        "generation_archetype_id": cfg["generation_archetype_id"],
        "archetype_aliases": cfg["aliases"],
        "aesthetic_category_id": cfg["aesthetic_category_id"],
        "development_type": cfg["development_type"],
        "reuse_keys": cfg["reuse_keys"],
        "generation_tags": [
            "wave9_single_family_batch",
            "fixed_landmark",
            "custom_pbr_skin",
            "physical_residential_glazing",
            "reference_locked",
            "detached_house",
            *cfg["kits"],
        ],
        "footprint_compatibility": footprint,
        "coordinate_contract": COORDINATE_CONTRACT,
        "textures": texture_inventory(skin),
        "facade_sheet": facade_contract(family, skin),
        "massing_graph": {
            "type": "fixed_landmark",
            "silhouette": cfg["silhouette"],
            "render_locked": True,
            "goalpost": cfg["goalpost"],
            "fallback": "family_shaped_modular_streetwall",
        },
        "material_budget": {
            "max_assembled_materials": 20,
            "rationale": (
                "Registered facade, construction materials, physical glazing, "
                "occupied depth and small identity accents remain semantic."
            ),
        },
        "dimensions": {
            "width_m": width,
            "depth_m": depth,
            "podium_height_m": cfg["floor_height_m"],
            "floor_height_m": cfg["floor_height_m"],
            "setback_height_m": cfg["floor_height_m"],
            "roof_height_m": cfg["roof_height_m"],
            "crown_height_m": cfg["floor_height_m"],
            "default_floors": native_floors,
            "min_floors": min_floors,
            "max_floors": max_floors,
        },
        "native_width_m": width,
        "native_depth_m": depth,
        "native_floors": native_floors,
        "min_floors": min_floors,
        "max_floors": max_floors,
        "default_floors": native_floors,
        "modules": modules,
        "assembled": assembled,
        "thumbnail": f"{family}_preview.png",
        "renders": renders,
        "architectural_identity": cfg["identity"],
        "material_zones": cfg["materials"],
        "glass_profile": cfg["glass_profile"],
        "source_provenance": source,
    }
    (folder / f"{family}_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    grammar = {
        "family_id": family,
        "source": {
            "archetype_id": cfg["archetype_id"],
            "variant_id": cfg["variant_id"],
            "generation_archetype_id": cfg["generation_archetype_id"],
            "reuse_keys": cfg["reuse_keys"],
        },
        "dimensions": manifest["dimensions"],
        "architectural_signature": {
            "identity": cfg["identity"],
            "material_zones": cfg["materials"],
            "glass_profile": cfg["glass_profile"],
            "kits": cfg["kits"],
        },
        "archetype_aliases": cfg["aliases"],
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
    family: str,
    output_root: Path,
    *,
    view_set: str,
    skip_renders: bool,
    skip_modules: bool,
) -> None:
    clear_scene()
    folder = output_root / family
    folder.mkdir(parents=True, exist_ok=True)
    mats, skin = load_palette(family, folder)
    fixed = FIXED_BUILDERS[family](mats)
    assembled_path = folder / f"{family}_assembled.glb"
    export_glb(assembled_path, fixed)
    fixed_triangles = evaluated_triangle_count(fixed)
    fixed_materials = material_count(fixed)
    renders = (
        sorted(path.name for path in folder.glob(f"{family}_*.png"))
        if skip_renders
        else render_views(family, folder, view_set=view_set)
    )
    if skip_modules:
        print(
            f"[wave9] {family} fixed only: {fixed_triangles:,} tris, "
            f"{fixed_materials} materials, {len(renders)} renders",
            flush=True,
        )
        return
    delete_objects(fixed)
    cfg = FAMILIES[family]
    role_specs = [
        ("podium", "default", cfg["floor_height_m"]),
        ("floor", "typical_a", cfg["floor_height_m"]),
        ("floor", "typical_b", cfg["floor_height_m"]),
        ("floor", "typical_c", cfg["floor_height_m"]),
        ("crown", "crown", cfg["floor_height_m"]),
        ("roof", "default", cfg["roof_height_m"]),
    ]
    modules: list[dict] = []
    for role, variant, module_height in role_specs:
        objects = fallback_module(family, role, variant, module_height, mats)
        objects.extend(module_contract_markers(role, variant, module_height))
        filename = (
            f"{family}_{role}.glb"
            if variant == "default"
            else f"{family}_{role}_{variant}.glb"
        )
        path = folder / filename
        export_glb(path, objects)
        modules.append(
            module_payload(
                family,
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
        family,
        folder,
        skin,
        modules,
        fixed_triangles,
        fixed_materials,
        assembled_path,
        renders,
    )
    print(
        f"[wave9] {family}: {fixed_triangles:,} tris, "
        f"{fixed_materials} materials, {len(modules)} modules, "
        f"{len(renders)} renders",
        flush=True,
    )


def render_existing(
    family: str,
    output_root: Path,
    *,
    view_set: str,
) -> None:
    clear_scene()
    folder = output_root / family
    manifest_path = folder / f"{family}_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    bpy.ops.import_scene.gltf(
        filepath=str(folder / manifest["assembled"]["filename"])
    )
    manifest["renders"] = render_views(family, folder, view_set=view_set)
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"[wave9-render] {family}: {len(manifest['renders'])} renders")


def main() -> int:
    args = parse_args()
    output_root = args.output_root.resolve()
    selected = args.family or sorted(FAMILIES)
    for family in selected:
        if args.render_existing:
            render_existing(family, output_root, view_set=args.view_set)
        else:
            build_family(
                family,
                output_root,
                view_set=args.view_set,
                skip_renders=args.skip_renders,
                skip_modules=args.skip_modules,
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
