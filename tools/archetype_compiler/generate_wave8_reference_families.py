"""Author three Wave 8 reference-locked LEGO building families.

The fixed GLBs own the approved catalogue silhouettes and construction:

* a five-level double-curved fluid shell with carved organic openings;
* a five-level mass-timber station beneath one oversized tree-column canopy;
* a seven-bay cut-stone souk with deep pointed arches and seven roof domes.

Each whole-building landmark is accompanied by a conservative six-role stack
so imprecise and oversized user drawings remain plannable without distorting
the canonical silhouette.

Run from the repository root with Blender 5.x:

    blender --background --factory-startup --python \
      tools/archetype_compiler/generate_wave8_reference_families.py -- \
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
    box,
    cylinder,
    delete_objects,
    export_glb,
    material,
    module_contract_markers,
    setup_render,
    sphere,
    triangle_count,
)
from generate_wave4_standard_batch import profiled_glass_material  # noqa: E402
from generate_wave4_standard_families import pbr_material  # noqa: E402
from generate_wave6_nonresidential_families import (  # noqa: E402
    join_mesh_group,
    mapped_reference_panel,
    mesh_object,
    rectangular_beam,
    reference_image_material,
)


FAMILIES: dict[str, dict] = {
    "parametric-fluid-hub": {
        "archetype_id": "parametric_future_hub",
        "variant_id": "parametric_fluid_organic",
        "generation_archetype_id": "parametric_fluid_organic",
        "label": "Parametric Future Hub — Fluid Organic Shell",
        "dimensions": (46.0, 34.0, 28.0),
        "floors": (4, 7, 5),
        "floor_height_m": 5.0,
        "roof_height_m": 3.0,
        "glass_profile": "fluid_hub_low_iron_curved",
        "aesthetic_category_id": "parametric_contemporary",
        "development_type": "commercial_office",
        "aliases": ["parametric_future_hub", "parametric_fluid_organic"],
        "reuse_keys": [
            "parametric_future_hub",
            "parametric_fluid_organic",
            "Office / Commercial",
            "Innovation Hub",
        ],
        "identity": (
            "A five-level pearl-white hourglass shell flares into one continuous "
            "roof, pinched by a concave lower waist and carved with six deep "
            "asymmetrical organic openings exposing warm occupied interiors."
        ),
        "materials": (
            "pearl-white perforated GFRC/composite shell panels; fine pale-metal "
            "joints; curved low-iron glazing; warm timber public interiors; "
            "restrained stainless frames; pale terrazzo public plinth"
        ),
        "kits": [
            "double_curved_flared_shell",
            "subtractive_organic_openings",
            "deep_shell_reveals",
            "curved_low_iron_glazing",
            "continuous_shell_roof",
        ],
        "footprint": {
            "recommendedWidth_m": [38, 54],
            "recommendedDepth_m": [28, 40],
            "recommendedFloors": [4, 7],
        },
        "fixed_band": {"scaleMin": 0.86, "scaleMax": 1.14, "maxAxisRatio": 1.12},
        "goalpost": "/archetypes/buildings/parametric_future_hub/variant_0.png",
        "silhouette": "double_curved_hourglass_shell",
        "profile_rationale": (
            "The free-form shell is authored inside an approximate rectangular "
            "placement envelope. Mild independent scaling preserves the landmark; "
            "larger parcels switch to a related curved-panel stack."
        ),
        "close_target": (-10.0, -12.0, 7.0),
    },
    "timber-transit-station": {
        "archetype_id": "transit_oriented_station_block",
        "variant_id": "transit_station_timber_sustainable",
        "generation_archetype_id": "transit_station_timber_sustainable",
        "label": "Transit-Oriented Station Block — Timber Sustainable",
        "dimensions": (52.0, 32.0, 29.0),
        "floors": (4, 8, 5),
        "floor_height_m": 4.2,
        "roof_height_m": 7.5,
        "glass_profile": "timber_station_neutral_low_e",
        "aesthetic_category_id": "mass_timber",
        "development_type": "transit_station",
        "aliases": [
            "transit_oriented_station_block",
            "transit_station_timber_sustainable",
        ],
        "reuse_keys": [
            "transit_oriented_station_block",
            "transit_station_timber_sustainable",
            "Transit Station",
            "Mass Timber",
        ],
        "identity": (
            "A five-level mass-timber station block lifts above a transparent "
            "transit concourse, with an exposed glulam frame, alternating CLT, "
            "louver and occupied glass bays, and one oversized tree-column canopy."
        ),
        "materials": (
            "honey glulam and CLT; deep timber louver fields; neutral low-e glass; "
            "warm occupied concourse and offices; translucent ETFE roof membrane; "
            "pale concrete platforms; planted rain-garden accents"
        ),
        "kits": [
            "five_level_glulam_frame",
            "alternating_louver_window_bays",
            "transparent_transit_concourse",
            "tree_column_canopy",
            "translucent_roof_membrane",
        ],
        "footprint": {
            "recommendedWidth_m": [42, 64],
            "recommendedDepth_m": [25, 40],
            "recommendedFloors": [4, 8],
        },
        "fixed_band": {"scaleMin": 0.84, "scaleMax": 1.18, "maxAxisRatio": 1.15},
        "goalpost": (
            "/archetypes/buildings/transit_oriented_station_block/variant_2.png"
        ),
        "silhouette": "glulam_station_under_oversized_canopy",
        "profile_rationale": (
            "The station and canopy remain one fixed structural composition for "
            "ordinary hand-drawn variation. Oversized parcels repeat complete "
            "timber structural bays through the family stack."
        ),
        "close_target": (-14.0, -13.0, 7.0),
    },
    "covered-souk-market": {
        "archetype_id": "traditional_vernacular_market_street",
        "variant_id": "vernacular_market_souk_bazaar",
        "generation_archetype_id": "vernacular_market_souk_bazaar",
        "label": "Traditional Vernacular Market — Covered Souk / Bazaar",
        "dimensions": (49.0, 24.0, 14.5),
        "floors": (1, 3, 2),
        "floor_height_m": 5.0,
        "roof_height_m": 4.5,
        "glass_profile": "souk_recessed_amber_glass",
        "aesthetic_category_id": "regional_vernacular",
        "development_type": "commercial_light",
        "aliases": [
            "traditional_vernacular_market_street",
            "vernacular_market_souk_bazaar",
        ],
        "reuse_keys": [
            "traditional_vernacular_market_street",
            "vernacular_market_souk_bazaar",
            "Market Hall",
            "Commercial / Retail",
        ],
        "identity": (
            "A long seven-bay honey-limestone souk is cut by genuinely deep "
            "pointed arcades, upper walnut mashrabiya screens and recessed shops, "
            "with seven shallow domes and aged-copper lanterns aligned above."
        ),
        "materials": (
            "warm hand-cut honey limestone; dark carved walnut mashrabiya and "
            "shopfronts; aged bronze and copper lanterns; restrained amber occupied "
            "glass; lime-stone dome fields and stone-paved thresholds"
        ),
        "kits": [
            "seven_bay_pointed_arcade",
            "deep_stone_arch_soffits",
            "mashrabiya_screen_grid",
            "recessed_shopfronts",
            "seven_aligned_domes",
        ],
        "footprint": {
            "recommendedWidth_m": [35, 70],
            "recommendedDepth_m": [18, 32],
            "recommendedFloors": [1, 3],
        },
        "fixed_band": {"scaleMin": 0.80, "scaleMax": 1.25, "maxAxisRatio": 1.20},
        "goalpost": (
            "/archetypes/buildings/traditional_vernacular_market_street/"
            "variant_2.png"
        ),
        "silhouette": "seven_pointed_bays_beneath_seven_domes",
        "profile_rationale": (
            "Seven complete arch-and-dome bays define the native landmark. Mild "
            "scaling preserves their rhythm; larger market frontages repeat "
            "complete authored bays through the stack."
        ),
        "close_target": (-15.0, -12.0, 5.2),
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


def _near_zones(skin: dict) -> dict[str, dict]:
    return {zone: values["near"] for zone, values in skin["zones"].items()}


def load_palette(
    family: str,
    folder: Path,
) -> tuple[dict[str, bpy.types.Material], dict]:
    skin = json.loads(
        (folder / "textures" / "skin_manifest.json").read_text(encoding="utf-8")
    )
    near = _near_zones(skin)
    cfg = FAMILIES[family]
    token = family.replace("-", "_").upper()
    mats: dict[str, bpy.types.Material] = {
        "glass": profiled_glass_material(
            f"MAT_W8_{token}_PhysicalGlass",
            cfg["glass_profile"],
        ),
                "underlay": reference_image_material(
            f"MAT_W8_{token}_ReferenceOccupiedDepth",
            folder,
            "textures/source/occupied-depth-source.png",
            emission_strength={
                "parametric-fluid-hub": 0.30,
                "timber-transit-station": 0.18,
                "covered-souk-market": 0.28,
            }[family],
        ),
        "dark": material(
            f"MAT_W8_{token}_DeepCavity",
            (0.026, 0.022, 0.019, 1.0),
            0.92,
        ),
        "concrete": material(
            f"MAT_W8_{token}_PaleConcrete",
            (0.46, 0.45, 0.42, 1.0),
            0.82,
        ),
    }
    if family == "parametric-fluid-hub":
        mats.update(
            {
                "shell": pbr_material(
                    f"MAT_W8_{token}_RegisteredShell",
                    folder,
                    near["shell"],
                    "shell",
                    value=1.03,
                    saturation=0.82,
                ),
                "side": pbr_material(
                    f"MAT_W8_{token}_WrappedShell",
                    folder,
                    near["side"],
                    "side",
                    value=0.98,
                    saturation=0.76,
                ),
                "roof": pbr_material(
                    f"MAT_W8_{token}_ContinuousRoof",
                    folder,
                    near["roof"],
                    "roof",
                    value=1.02,
                    saturation=0.78,
                ),
                "metal": pbr_material(
                    f"MAT_W8_{token}_PaleMetal",
                    folder,
                    near["metal"],
                    "metal",
                    metallic=0.70,
                    value=0.82,
                ),
                "interior": pbr_material(
                    f"MAT_W8_{token}_WarmInterior",
                    folder,
                    near["interior"],
                    "interior",
                    emission_strength=0.055,
                    value=0.48,
                ),
            }
        )
    elif family == "timber-transit-station":
        mats.update(
            {
                "facade": pbr_material(
                    f"MAT_W8_{token}_RegisteredFacade",
                    folder,
                    near["facade"],
                    "facade",
                    value=0.92,
                ),
                "timber": pbr_material(
                    f"MAT_W8_{token}_StructuralTimber",
                    folder,
                    near["timber"],
                    "timber",
                    value=1.10,
                    saturation=1.04,
                ),
                "louver": pbr_material(
                    f"MAT_W8_{token}_TimberLouvers",
                    folder,
                    near["louver"],
                    "louver",
                    value=0.98,
                    saturation=1.02,
                ),
                "canopy": pbr_material(
                    f"MAT_W8_{token}_CanopyTimber",
                    folder,
                    near["canopy"],
                    "canopy",
                    value=1.13,
                    saturation=1.04,
                ),
                "side": pbr_material(
                    f"MAT_W8_{token}_SecondaryTimberFacade",
                    folder,
                    near["side"],
                    "side",
                    value=0.84,
                ),
                "green": pbr_material(
                    f"MAT_W8_{token}_Planting",
                    folder,
                    near["green"],
                    "green",
                    value=0.58,
                ),
                "interior": pbr_material(
                    f"MAT_W8_{token}_OccupiedInterior",
                    folder,
                    near["interior"],
                    "interior",
                    emission_strength=0.04,
                    value=0.46,
                ),
                "membrane": material(
                    f"MAT_W8_{token}_TranslucentMembrane",
                    (0.88, 0.90, 0.86, 0.52),
                    0.18,
                ),
            }
        )
    else:
        mats.update(
            {
                "facade": pbr_material(
                    f"MAT_W8_{token}_RegisteredFacade",
                    folder,
                    near["facade"],
                    "facade",
                    value=0.90,
                    saturation=0.88,
                ),
                "stone": pbr_material(
                    f"MAT_W8_{token}_CutStone",
                    folder,
                    near["stone"],
                    "stone",
                    value=1.08,
                    saturation=1.06,
                ),
                "dome": pbr_material(
                    f"MAT_W8_{token}_DomeStone",
                    folder,
                    near["dome"],
                    "dome",
                    value=1.06,
                    saturation=1.04,
                ),
                "roof": pbr_material(
                    f"MAT_W8_{token}_StoneDomes",
                    folder,
                    near["roof"],
                    "roof",
                    value=0.90,
                    saturation=0.84,
                ),
                "side": pbr_material(
                    f"MAT_W8_{token}_SecondaryStone",
                    folder,
                    near["side"],
                    "side",
                    value=0.80,
                    saturation=0.82,
                ),
                "timber": pbr_material(
                    f"MAT_W8_{token}_CarvedWalnut",
                    folder,
                    near["timber"],
                    "timber",
                    value=0.88,
                    saturation=1.08,
                ),
                "bronze": pbr_material(
                    f"MAT_W8_{token}_AgedBronze",
                    folder,
                    near["bronze"],
                    "bronze",
                    metallic=0.72,
                    value=0.96,
                ),
                "mortar": material(
                    f"MAT_W8_{token}_RecessedMortarJoint",
                    (0.26, 0.18, 0.105, 1.0),
                    0.90,
                ),
                "lantern_glow": material(
                    f"MAT_W8_{token}_LanternGlow",
                    (0.72, 0.20, 0.025, 1.0),
                    0.34,
                    emission=(1.0, 0.18, 0.018, 1.0),
                    emission_strength=3.2,
                ),
                "interior": pbr_material(
                    f"MAT_W8_{token}_RecessedMarketInterior",
                    folder,
                    near["interior"],
                    "interior",
                    emission_strength=0.065,
                    value=0.44,
                ),
            }
        )
    if family == "timber-transit-station":
        # The canopy is an ETFE/glass weather skin carried by the glulam tree
        # structure, not an opaque white roof plate. Keep that distinction in
        # both Eevee proof renders and the exported glTF material.
        membrane = mats["membrane"]
        membrane_bsdf = membrane.node_tree.nodes.get("Principled BSDF")
        membrane_bsdf.inputs["Base Color"].default_value = (
            0.78,
            0.84,
            0.82,
            1.0,
        )
        membrane_bsdf.inputs["Alpha"].default_value = 0.22
        if membrane_bsdf.inputs.get("Transmission Weight"):
            membrane_bsdf.inputs["Transmission Weight"].default_value = 0.48
        if membrane_bsdf.inputs.get("IOR"):
            membrane_bsdf.inputs["IOR"].default_value = 1.42
        if membrane_bsdf.inputs.get("Coat Weight"):
            membrane_bsdf.inputs["Coat Weight"].default_value = 0.36
        membrane.diffuse_color = (0.78, 0.84, 0.82, 0.22)
        if hasattr(membrane, "surface_render_method"):
            membrane.surface_render_method = "BLENDED"
        membrane["construction"] = "translucent_etfe_weather_membrane"
        membrane["alpha_strategy"] = "blend_over_expressed_glulam_structure"
    mats["glass"]["glazing_lod"] = "always"
    mats["glass"]["reference_locked"] = True
    mats["glass"]["source_variant_id"] = cfg["variant_id"]
    mats["underlay"]["glazing_profile"] = cfg["glass_profile"]
    return mats, skin


def shade_smooth(obj: bpy.types.Object) -> bpy.types.Object:
    if obj.type == "MESH":
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
    return obj


def join_tokens(
    objects: list[bpy.types.Object],
    groups: list[tuple[str, str]],
) -> list[bpy.types.Object]:
    for token, name in groups:
        objects = join_mesh_group(
            objects,
            lambda obj, value=token: value in obj.name,
            name,
        )
    return objects


def ellipse_point(
    centre_x: float,
    centre_z: float,
    radius_x: float,
    radius_z: float,
    rotation: float,
    angle: float,
) -> tuple[float, float]:
    x = math.cos(angle) * radius_x
    z = math.sin(angle) * radius_z
    c, s = math.cos(rotation), math.sin(rotation)
    return centre_x + x * c - z * s, centre_z + x * s + z * c


def ellipse_contains(
    x: float,
    z: float,
    opening: dict,
    *,
    scale: float = 1.0,
) -> bool:
    c, s = math.cos(-opening["rotation"]), math.sin(-opening["rotation"])
    dx, dz = x - opening["x"], z - opening["z"]
    local_x = dx * c - dz * s
    local_z = dx * s + dz * c
    return (
        (local_x / (opening["rx"] * scale)) ** 2
        + (local_z / (opening["rz"] * scale)) ** 2
        <= 1.0
    )


FLUID_OPENINGS = [
    {"x": -7.7, "z": 21.2, "rx": 5.2, "rz": 2.5, "rotation": -0.03},
    {"x": -6.7, "z": 16.8, "rx": 6.0, "rz": 2.3, "rotation": -0.05},
    {"x": -5.8, "z": 12.4, "rx": 5.4, "rz": 2.5, "rotation": -0.10},
    {"x": -10.8, "z": 4.2, "rx": 6.3, "rz": 3.4, "rotation": 0.18},
    {"x": 11.1, "z": 9.6, "rx": 2.7, "rz": 2.1, "rotation": -0.08},
    {"x": 10.2, "z": 4.72, "rx": 5.6, "rz": 4.2, "rotation": -0.12},
]

# Bottom-left and top-right UV bounds into the render-locked occupied-depth
# plate.  Each crop is rebound to its physical opening, avoiding the false
# windows and registration drift produced by one full-facade underlay card.
FLUID_INTERIOR_UV = [
    (0.280, 0.690, 0.490, 0.840),
    (0.280, 0.590, 0.520, 0.725),
    (0.305, 0.475, 0.535, 0.625),
    (0.150, 0.185, 0.410, 0.395),
    (0.745, 0.355, 0.875, 0.515),
    (0.655, 0.145, 0.905, 0.395),
]


def _piecewise(z: float, points: list[tuple[float, float]]) -> float:
    if z <= points[0][0]:
        return points[0][1]
    if z >= points[-1][0]:
        return points[-1][1]
    for (z0, value0), (z1, value1) in zip(points, points[1:]):
        if z0 <= z <= z1:
            t = (z - z0) / (z1 - z0)
            t = t * t * (3.0 - 2.0 * t)
            return value0 + (value1 - value0) * t
    raise AssertionError(z)


def fluid_left_width(z: float) -> float:
    return _piecewise(
        z,
        [(0.0, 23.0), (6.0, 18.0), (14.0, 18.6), (21.0, 21.0), (27.8, 23.0)],
    )


def fluid_right_width(z: float) -> float:
    return _piecewise(
        z,
        [(0.0, 22.6), (6.0, 19.8), (14.0, 19.2), (21.0, 21.4), (27.8, 23.0)],
    )


def fluid_half_depth(z: float) -> float:
    return _piecewise(
        z,
        [(0.0, 14.0), (7.0, 14.4), (16.0, 15.2), (22.0, 16.2), (27.8, 17.0)],
    )


def fluid_front_y(x: float, z: float) -> float:
    width = fluid_left_width(z) if x < 0 else fluid_right_width(z)
    normalized = min(1.0, abs(x) / max(width, 0.001))
    edge_sweep = 4.1 * normalized**3.2
    local_wave = 0.38 * math.sin((x / 46.0 + 0.5) * math.pi * 2.0) * (
        0.25 + 0.75 * math.sin(math.pi * min(1.0, z / 28.0)) ** 2
    )
    return -fluid_half_depth(z) + edge_sweep + local_wave


def fluid_front_shell(m: dict[str, bpy.types.Material]) -> bpy.types.Object:
    columns, rows = 104, 58
    vertices: list[tuple[float, float, float]] = []
    for row in range(rows + 1):
        z = 27.8 * row / rows
        left, right = fluid_left_width(z), fluid_right_width(z)
        for column in range(columns + 1):
            u = column / columns
            x = -left + (left + right) * u
            vertices.append((x, fluid_front_y(x, z), z))
    faces: list[tuple[int, ...]] = []
    stride = columns + 1
    for row in range(rows):
        for column in range(columns):
            a = row * stride + column
            b = a + 1
            d = (row + 1) * stride + column
            c = d + 1
            centre_x = sum(vertices[index][0] for index in (a, b, c, d)) / 4.0
            centre_z = sum(vertices[index][2] for index in (a, b, c, d)) / 4.0
            if any(
                ellipse_contains(centre_x, centre_z, opening, scale=1.08)
                for opening in FLUID_OPENINGS
            ):
                continue
            faces.append((a, b, c, d))
    obj = mesh_object("FLUID_RegisteredDoubleCurvedFrontShell", vertices, faces, m["shell"])
    return shade_smooth(obj)


def fluid_side_and_back_shell(
    m: dict[str, bpy.types.Material],
) -> bpy.types.Object:
    rows, side_steps, back_steps = 30, 24, 72
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []

    def add_grid(
        point: Callable[[int, int], tuple[float, float, float]],
        columns: int,
    ) -> None:
        base = len(vertices)
        for row in range(rows + 1):
            for column in range(columns + 1):
                vertices.append(point(row, column))
        stride = columns + 1
        for row in range(rows):
            for column in range(columns):
                a = base + row * stride + column
                faces.append((a, a + 1, a + stride + 1, a + stride))

    for side in (-1, 1):
        def side_point(row: int, column: int, sign: int = side) -> tuple[float, float, float]:
            z = 27.8 * row / rows
            width = fluid_left_width(z) if sign < 0 else fluid_right_width(z)
            front = fluid_front_y(sign * width, z)
            t = column / side_steps
            y = front + (fluid_half_depth(z) - front) * t
            x = sign * width * (1.0 - 0.055 * math.sin(math.pi * t))
            return (x, y, z)

        add_grid(side_point, side_steps)

    def back_point(row: int, column: int) -> tuple[float, float, float]:
        z = 27.8 * row / rows
        left, right = fluid_left_width(z), fluid_right_width(z)
        u = column / back_steps
        x = -left + (left + right) * u
        edge_curve = 0.55 * (abs(2.0 * u - 1.0) ** 2.2)
        return (x, fluid_half_depth(z) - edge_curve, z)

    add_grid(back_point, back_steps)
    obj = mesh_object("FLUID_WrappedSecondaryShell", vertices, faces, m["side"])
    return shade_smooth(obj)


def fluid_ellipse_reveal(
    opening: dict,
    index: int,
    m: dict[str, bpy.types.Material],
    *,
    segments: int = 64,
) -> list[bpy.types.Object]:
    outer_rx, outer_rz = opening["rx"] + 0.52, opening["rz"] + 0.46
    inner_rx, inner_rz = opening["rx"], opening["rz"]
    outer: list[tuple[float, float, float]] = []
    inner_front: list[tuple[float, float, float]] = []
    inner_back: list[tuple[float, float, float]] = []
    for step in range(segments):
        angle = 2.0 * math.pi * step / segments
        ox, oz = ellipse_point(
            opening["x"],
            opening["z"],
            outer_rx,
            outer_rz,
            opening["rotation"],
            angle,
        )
        ix, iz = ellipse_point(
            opening["x"],
            opening["z"],
            inner_rx,
            inner_rz,
            opening["rotation"],
            angle,
        )
        outer.append((ox, fluid_front_y(ox, oz) - 0.03, oz))
        front_y = fluid_front_y(ix, iz)
        inner_front.append((ix, front_y + 0.02, iz))
        inner_back.append((ix, front_y + 1.12, iz))
    vertices = outer + inner_front + inner_back
    faces: list[tuple[int, ...]] = []
    for step in range(segments):
        nxt = (step + 1) % segments
        faces.append((step, nxt, segments + nxt, segments + step))
        faces.append(
            (
                segments + step,
                segments + nxt,
                segments * 2 + nxt,
                segments * 2 + step,
            )
        )
    reveal = mesh_object(
        f"FLUID_OpeningReveal_{index}",
        vertices,
        faces,
        m["shell"],
    )
    shade_smooth(reveal)

    pane_vertices = [
        (
            x,
            fluid_front_y(x, z) + 1.18,
            z,
        )
        for x, z in (
            ellipse_point(
                opening["x"],
                opening["z"],
                inner_rx * 0.94,
                inner_rz * 0.92,
                opening["rotation"],
                2.0 * math.pi * step / segments,
            )
            for step in range(segments)
        )
    ]
    pane_vertices.append(
        (
            opening["x"],
            fluid_front_y(opening["x"], opening["z"]) + 1.18,
            opening["z"],
        )
    )
    centre = segments
    pane = mesh_object(
        f"FLUID_OrganicPane_{index}",
        pane_vertices,
        [(centre, step, (step + 1) % segments) for step in range(segments)],
        m["glass"],
    )
    shade_smooth(pane)
    objects = [reveal, pane]

    # Slender structural mullions are clipped to the true ellipse.
    for mullion_index, local_x in enumerate(
        [-inner_rx * 0.62, -inner_rx * 0.30, 0.0, inner_rx * 0.30, inner_rx * 0.62]
    ):
        z_extent = inner_rz * math.sqrt(max(0.0, 1.0 - (local_x / inner_rx) ** 2))
        c, s = math.cos(opening["rotation"]), math.sin(opening["rotation"])
        points = []
        for local_z in (-z_extent * 0.90, z_extent * 0.90):
            x = opening["x"] + local_x * c - local_z * s
            z = opening["z"] + local_x * s + local_z * c
            points.append((x, fluid_front_y(x, z) + 1.08, z))
        objects.append(
            rectangular_beam(
                f"FLUID_Mullion_{index}_{mullion_index}",
                points[0],
                points[1],
                0.10,
                m["metal"],
                depth=0.07,
            )
        )
    if index in {0, 1, 2, 5}:
        local_z = 0.0
        c, s = math.cos(opening["rotation"]), math.sin(opening["rotation"])
        points = []
        for local_x in (-inner_rx * 0.88, inner_rx * 0.88):
            x = opening["x"] + local_x * c - local_z * s
            z = opening["z"] + local_x * s + local_z * c
            points.append((x, fluid_front_y(x, z) + 1.07, z))
        objects.append(
            rectangular_beam(
                f"FLUID_Transom_{index}",
                points[0],
                points[1],
                0.095,
                m["metal"],
                depth=0.07,
            )
        )
    return objects


def fluid_roof(m: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    front_steps, side_steps, rear_steps = 64, 24, 64
    outer_xy: list[tuple[float, float]] = []
    z = 27.8
    left, right = fluid_left_width(z), fluid_right_width(z)
    front_left = fluid_front_y(-left, z)
    front_right = fluid_front_y(right, z)
    rear_y = fluid_half_depth(z)
    for step in range(front_steps):
        t = step / front_steps
        x = -left + (left + right) * t
        outer_xy.append((x, fluid_front_y(x, z)))
    for step in range(side_steps):
        t = step / side_steps
        outer_xy.append((right, front_right + (rear_y - front_right) * t))
    for step in range(rear_steps):
        t = step / rear_steps
        x = right - (left + right) * t
        u = (x + left) / (left + right)
        edge_curve = 0.55 * (abs(2.0 * u - 1.0) ** 2.2)
        outer_xy.append((x, rear_y - edge_curve))
    for step in range(side_steps):
        t = step / side_steps
        outer_xy.append((-left, rear_y + (front_left - rear_y) * t))

    segments = len(outer_xy)
    inner_rx, inner_ry = 6.2, 3.5
    inner_xy: list[tuple[float, float]] = []
    for x, y in outer_xy:
        angle = math.atan2(y / 17.0, x / 23.0)
        inner_xy.append((inner_rx * math.cos(angle), inner_ry * math.sin(angle)))
    vertices = [
        (x, y, 27.78)
        for x, y in outer_xy
    ] + [
        (x, y, 27.98)
        for x, y in inner_xy
    ]
    faces = []
    for step in range(segments):
        nxt = (step + 1) % segments
        faces.append((step, nxt, segments + nxt, segments + step))
    roof = shade_smooth(mesh_object("FLUID_ContinuousShellRoof", vertices, faces, m["roof"]))

    skylight_vertices = [(0.0, 0.0, 27.96)]
    skylight_vertices.extend(
        (
            inner_rx * math.cos(2.0 * math.pi * step / segments),
            inner_ry * math.sin(2.0 * math.pi * step / segments),
            27.96,
        )
        for step in range(segments)
    )
    skylight = mesh_object(
        "FLUID_OvalRoofSkylight",
        skylight_vertices,
        [
            (0, 1 + step, 1 + ((step + 1) % segments))
            for step in range(segments)
        ],
        m["glass"],
    )
    return [roof, skylight]


def fluid_interior(m: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    for level in range(1, 5):
        z = level * 5.0
        objects.append(
            box(
                f"FLUID_InteriorFloor_{level}",
                (31.0, 20.0, 0.22),
                (0.0, 0.8, z),
                m["interior"],
                0.05,
            )
        )
    for x in (-10.0, 0.0, 10.0):
        objects.append(
            cylinder(
                f"FLUID_InteriorColumn_{x:+.0f}",
                0.34,
                24.0,
                (x, 0.8, 12.0),
                m["concrete"],
                20,
            )
        )
    for index, (opening, uv_bounds) in enumerate(
        zip(FLUID_OPENINGS, FLUID_INTERIOR_UV)
    ):
        c, s = math.cos(opening["rotation"]), math.sin(opening["rotation"])
        x_extent = math.sqrt(
            (opening["rx"] * c) ** 2 + (opening["rz"] * s) ** 2
        ) * 1.03
        z_extent = math.sqrt(
            (opening["rx"] * s) ** 2 + (opening["rz"] * c) ** 2
        ) * 1.03
        x0, x1 = opening["x"] - x_extent, opening["x"] + x_extent
        z0, z1 = opening["z"] - z_extent, opening["z"] + z_extent
        y = fluid_front_y(opening["x"], opening["z"]) + 1.42
        objects.append(
            mapped_reference_panel(
                f"FLUID_RenderLockedOccupiedDepth_{index}",
                (
                    (x0, y, z0),
                    (x1, y, z0),
                    (x1, y, z1),
                    (x0, y, z1),
                ),
                m["underlay"],
                model_x_bounds=(x0, x1),
                model_z_bounds=(z0, z1),
                source_uv_bounds=uv_bounds,
            )
        )
    return objects


def fluid_public_realm(m: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    objects = [
        box(
            "FLUID_PublicPlinth",
            (46.0, 33.4, 0.34),
            (0.0, 0.0, 0.17),
            m["concrete"],
            0.08,
        )
    ]
    for step in range(4):
        step_height = 0.12 * (step + 1)
        objects.append(
            box(
                f"FLUID_EntranceStep_{step}",
                (12.5 + step * 0.7, 1.05, step_height),
                (10.0, -16.50 + step * 0.44, step_height / 2),
                m["concrete"],
                0.04,
            )
        )
    return objects


def fluid_fixed(m: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = [
        fluid_front_shell(m),
        fluid_side_and_back_shell(m),
        *fluid_roof(m),
        *fluid_interior(m),
        *fluid_public_realm(m),
    ]
    for index, opening in enumerate(FLUID_OPENINGS):
        objects.extend(fluid_ellipse_reveal(opening, index, m))
    return join_tokens(
        objects,
        [
            ("FLUID_Mullion_", "FLUID_OrganicOpeningMullionSystem"),
            ("FLUID_Transom_", "FLUID_OrganicOpeningTransomSystem"),
            ("FLUID_InteriorFloor_", "FLUID_InteriorFloorSystem"),
            ("FLUID_EntranceStep_", "FLUID_EntranceStairSystem"),
        ],
    )


STATION_BODY_WIDTH = 44.0
STATION_BODY_DEPTH = 24.0
STATION_FRONT_Y = -STATION_BODY_DEPTH / 2
STATION_BODY_BASE = 5.25
STATION_BODY_TOP = 21.85
STATION_BAYS = 8
STATION_ROWS = 4


def station_front_cell(
    row: int,
    column: int,
    kind: str,
    m: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    bay_width = STATION_BODY_WIDTH / STATION_BAYS
    row_height = (STATION_BODY_TOP - STATION_BODY_BASE) / STATION_ROWS
    x0 = -STATION_BODY_WIDTH / 2 + column * bay_width
    x1 = x0 + bay_width
    z0 = STATION_BODY_BASE + row * row_height
    z1 = z0 + row_height
    inset = 0.24
    if kind == "glass":
        objects.append(
            box(
                f"STATION_UpperPane_{row}_{column}",
                (bay_width - inset * 2, 0.10, row_height - inset * 2),
                ((x0 + x1) / 2, STATION_FRONT_Y - 0.05, (z0 + z1) / 2),
                m["glass"],
                0.025,
            )
        )
        objects.append(
            rectangular_beam(
                f"STATION_WindowMullion_{row}_{column}",
                ((x0 + x1) / 2, STATION_FRONT_Y - 0.12, z0 + inset),
                ((x0 + x1) / 2, STATION_FRONT_Y - 0.12, z1 - inset),
                0.095,
                m["timber"],
                depth=0.12,
            )
        )
    elif kind == "louver":
        objects.append(
            mapped_reference_panel(
                f"STATION_LouverBacking_{row}_{column}",
                (
                    (x0 + inset, STATION_FRONT_Y - 0.03, z0 + inset),
                    (x1 - inset, STATION_FRONT_Y - 0.03, z0 + inset),
                    (x1 - inset, STATION_FRONT_Y - 0.03, z1 - inset),
                    (x0 + inset, STATION_FRONT_Y - 0.03, z1 - inset),
                ),
                m["louver"],
                model_x_bounds=(-STATION_BODY_WIDTH / 2, STATION_BODY_WIDTH / 2),
                model_z_bounds=(STATION_BODY_BASE, STATION_BODY_TOP),
                source_uv_bounds=(
                    column / STATION_BAYS,
                    row / STATION_ROWS,
                    (column + 1) / STATION_BAYS,
                    (row + 1) / STATION_ROWS,
                ),
            )
        )
        slat_count = 7 if row == 0 else 11
        for slat in range(slat_count):
            if row == 0:
                x = x0 + bay_width * (slat + 1) / (slat_count + 1)
                start = (x, STATION_FRONT_Y - 0.18, z0 + inset)
                end = (x, STATION_FRONT_Y - 0.18, z1 - inset)
            else:
                z = z0 + row_height * (slat + 1) / (slat_count + 1)
                start = (x0 + inset, STATION_FRONT_Y - 0.18, z)
                end = (x1 - inset, STATION_FRONT_Y - 0.18, z)
            objects.append(
                rectangular_beam(
                    f"STATION_LouverSlat_{row}_{column}_{slat}",
                    start,
                    end,
                    0.060,
                    m["louver"],
                    depth=0.16,
                )
            )
    else:
        objects.append(
            mapped_reference_panel(
                f"STATION_CLTPanel_{row}_{column}",
                (
                    (x0 + inset, STATION_FRONT_Y - 0.03, z0 + inset),
                    (x1 - inset, STATION_FRONT_Y - 0.03, z0 + inset),
                    (x1 - inset, STATION_FRONT_Y - 0.03, z1 - inset),
                    (x0 + inset, STATION_FRONT_Y - 0.03, z1 - inset),
                ),
                m["timber"],
                model_x_bounds=(-STATION_BODY_WIDTH / 2, STATION_BODY_WIDTH / 2),
                model_z_bounds=(STATION_BODY_BASE, STATION_BODY_TOP),
                source_uv_bounds=(
                    column / STATION_BAYS,
                    row / STATION_ROWS,
                    (column + 1) / STATION_BAYS,
                    (row + 1) / STATION_ROWS,
                ),
            )
        )
    return objects


def station_body(m: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = [
        box(
            "STATION_UpperShadowCore",
            (STATION_BODY_WIDTH - 0.8, STATION_BODY_DEPTH - 0.8, STATION_BODY_TOP - STATION_BODY_BASE),
            (0.0, 0.0, (STATION_BODY_TOP + STATION_BODY_BASE) / 2),
            m["dark"],
            0.10,
        ),
        mapped_reference_panel(
            "STATION_RenderLockedOccupiedDepth",
            (
                (-STATION_BODY_WIDTH / 2, STATION_FRONT_Y + 0.34, 0.4),
                (STATION_BODY_WIDTH / 2, STATION_FRONT_Y + 0.34, 0.4),
                (STATION_BODY_WIDTH / 2, STATION_FRONT_Y + 0.34, STATION_BODY_TOP),
                (-STATION_BODY_WIDTH / 2, STATION_FRONT_Y + 0.34, STATION_BODY_TOP),
            ),
            m["underlay"],
            model_x_bounds=(-STATION_BODY_WIDTH / 2, STATION_BODY_WIDTH / 2),
            model_z_bounds=(0.4, STATION_BODY_TOP),
            source_uv_bounds=(0.14, 0.08, 0.86, 0.68),
        ),
    ]
    pattern = [
        ["louver", "louver", "solid", "louver", "louver", "solid", "louver", "louver"],
        ["glass", "solid", "glass", "louver", "glass", "louver", "glass", "solid"],
        ["solid", "glass", "louver", "glass", "solid", "glass", "louver", "glass"],
        ["louver", "louver", "solid", "glass", "louver", "glass", "louver", "louver"],
    ]
    for row in range(STATION_ROWS):
        for column in range(STATION_BAYS):
            objects.extend(station_front_cell(row, column, pattern[row][column], m))

    # The primary structural grid remains visible in front of all infill.
    for column in range(STATION_BAYS + 1):
        x = -STATION_BODY_WIDTH / 2 + STATION_BODY_WIDTH * column / STATION_BAYS
        objects.append(
            rectangular_beam(
                f"STATION_PrimaryPost_{column}",
                (x, STATION_FRONT_Y - 0.30, STATION_BODY_BASE),
                (x, STATION_FRONT_Y - 0.30, STATION_BODY_TOP),
                0.30,
                m["timber"],
                depth=0.38,
            )
        )
    for row in range(STATION_ROWS + 1):
        z = STATION_BODY_BASE + (STATION_BODY_TOP - STATION_BODY_BASE) * row / STATION_ROWS
        objects.append(
            rectangular_beam(
                f"STATION_PrimaryBeam_{row}",
                (-STATION_BODY_WIDTH / 2, STATION_FRONT_Y - 0.30, z),
                (STATION_BODY_WIDTH / 2, STATION_FRONT_Y - 0.30, z),
                0.30,
                m["timber"],
                depth=0.38,
            )
        )

    # Secondary elevations carry the same structural datums but a quieter bay mix.
    for side in (-1, 1):
        x = side * STATION_BODY_WIDTH / 2
        for column in range(5):
            y0 = -STATION_BODY_DEPTH / 2 + column * STATION_BODY_DEPTH / 5
            y1 = -STATION_BODY_DEPTH / 2 + (column + 1) * STATION_BODY_DEPTH / 5
            for row in range(STATION_ROWS):
                z0 = STATION_BODY_BASE + row * (STATION_BODY_TOP - STATION_BODY_BASE) / STATION_ROWS
                z1 = STATION_BODY_BASE + (row + 1) * (STATION_BODY_TOP - STATION_BODY_BASE) / STATION_ROWS
                cell_index = column + row + (1 if side > 0 else 0)
                mat = (
                    m["glass"]
                    if cell_index % 3 == 0
                    else (m["louver"] if cell_index % 2 else m["timber"])
                )
                objects.append(
                    box(
                        f"STATION_SideCell_{side}_{row}_{column}",
                        (0.10, y1 - y0 - 0.22, z1 - z0 - 0.22),
                        (x + side * 0.05, (y0 + y1) / 2, (z0 + z1) / 2),
                        mat,
                        0.025,
                    )
                )
        for column in range(6):
            y = -STATION_BODY_DEPTH / 2 + STATION_BODY_DEPTH * column / 5
            objects.append(
                rectangular_beam(
                    f"STATION_SidePost_{side}_{column}",
                    (x + side * 0.14, y, STATION_BODY_BASE),
                    (x + side * 0.14, y, STATION_BODY_TOP),
                    0.28,
                    m["timber"],
                    depth=0.34,
                )
            )
        for row in range(STATION_ROWS + 1):
            z = STATION_BODY_BASE + (STATION_BODY_TOP - STATION_BODY_BASE) * row / STATION_ROWS
            objects.append(
                rectangular_beam(
                    f"STATION_SideBeam_{side}_{row}",
                    (x + side * 0.14, -STATION_BODY_DEPTH / 2, z),
                    (x + side * 0.14, STATION_BODY_DEPTH / 2, z),
                    0.28,
                    m["timber"],
                    depth=0.34,
                )
            )
    objects.append(
        box(
            "STATION_RearTimberFacade",
            (STATION_BODY_WIDTH, 0.16, STATION_BODY_TOP - STATION_BODY_BASE),
            (0.0, STATION_BODY_DEPTH / 2 + 0.08, (STATION_BODY_TOP + STATION_BODY_BASE) / 2),
            m["timber"],
            0.04,
        )
    )
    return objects


def station_concourse(m: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = [
        box(
            "STATION_ConcourseFloor",
            (48.0, 27.0, 0.32),
            (0.0, -0.5, 0.16),
            m["concrete"],
            0.08,
        ),
        box(
            "STATION_ConcourseCeiling",
            (48.0, 28.0, 0.32),
            (0.0, -0.5, 5.18),
            m["timber"],
            0.07,
        ),
    ]
    bays = 10
    for column in range(bays):
        x0 = -22.0 + 44.0 * column / bays
        x1 = -22.0 + 44.0 * (column + 1) / bays
        objects.append(
            box(
                f"STATION_ConcoursePane_{column}",
                (x1 - x0 - 0.14, 0.10, 4.45),
                ((x0 + x1) / 2, STATION_FRONT_Y - 0.12, 2.62),
                m["glass"],
                0.02,
            )
        )
        objects.append(
            rectangular_beam(
                f"STATION_ConcoursePost_{column}",
                (x0, STATION_FRONT_Y - 0.24, 0.34),
                (x0, STATION_FRONT_Y - 0.24, 5.18),
                0.22,
                m["timber"],
                depth=0.28,
            )
        )
    objects.append(
        rectangular_beam(
            f"STATION_ConcoursePost_{bays}",
            (22.0, STATION_FRONT_Y - 0.24, 0.34),
            (22.0, STATION_FRONT_Y - 0.24, 5.18),
            0.22,
            m["timber"],
            depth=0.28,
        )
    )
    for x in (-7.0, 7.0):
        objects.append(
            box(
                f"STATION_EntryDoor_{x:+.0f}",
                (3.2, 0.12, 3.35),
                (x, STATION_FRONT_Y - 0.22, 1.98),
                m["glass"],
                0.02,
            )
        )
        objects.append(
            rectangular_beam(
                f"STATION_EntryDoorMullion_{x:+.0f}",
                (x, STATION_FRONT_Y - 0.30, 0.34),
                (x, STATION_FRONT_Y - 0.30, 3.65),
                0.11,
                m["timber"],
                depth=0.13,
            )
        )

    # The lower veranda is a real supported structure, not a floating fascia.
    objects.append(
        box(
            "STATION_TransitVerandaRoof",
            (52.0, 30.0, 0.28),
            (0.0, -1.0, 5.28),
            m["canopy"],
            0.08,
        )
    )
    for x in (-24.0, -16.0, -8.0, 0.0, 8.0, 16.0, 24.0):
        objects.append(
            rectangular_beam(
                f"STATION_VerandaPost_{x:+.0f}",
                (x, -15.0, 0.34),
                (x, -15.0, 5.18),
                0.26,
                m["timber"],
                depth=0.32,
            )
        )
        objects.append(
            rectangular_beam(
                f"STATION_VerandaBracket_{x:+.0f}",
                (x, -15.0, 4.0),
                (x, -12.0, 5.20),
                0.20,
                m["timber"],
                depth=0.24,
            )
        )
    return objects


def station_roof_canopy(m: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = [
        box(
            "STATION_RoofTerraceDeck",
            (44.0, 24.0, 0.30),
            (0.0, 0.0, 21.98),
            m["timber"],
            0.06,
        )
    ]
    trunk_positions = [-19.0, -12.5, -6.3, 0.0, 6.3, 12.5, 19.0]
    for index, x in enumerate(trunk_positions):
        for y in (-6.0, 6.0):
            objects.append(
                rectangular_beam(
                    f"STATION_TreeColumn_{index}_{y:+.0f}",
                    (x, y, 22.08),
                    (x, y, 26.1),
                    0.44,
                    m["canopy"],
                    depth=0.42,
                )
            )
            for target_x, target_y in (
                (x - 3.4, y - 4.2),
                (x + 3.4, y - 4.2),
                (x - 3.4, y + 4.2),
                (x + 3.4, y + 4.2),
            ):
                objects.append(
                    rectangular_beam(
                        f"STATION_TreeBranch_{index}_{y:+.0f}_{target_x:+.1f}_{target_y:+.1f}",
                        (x, y, 25.4),
                        (target_x, target_y, 28.35),
                        0.30,
                        m["canopy"],
                        depth=0.30,
                    )
                )
    for y in (-14.0, -7.0, 0.0, 7.0, 14.0):
        objects.append(
            rectangular_beam(
                f"STATION_CanopyPrimaryX_{y:+.0f}",
                (-25.7, y, 28.55),
                (25.7, y, 28.55),
                0.36,
                m["canopy"],
                depth=0.38,
            )
        )
    for x in range(-24, 25, 4):
        objects.append(
            rectangular_beam(
                f"STATION_CanopyPurlinY_{x:+d}",
                (float(x), -15.7, 28.66),
                (float(x), 15.7, 28.66),
                0.18,
                m["canopy"],
                depth=0.20,
            )
        )
    objects.append(
        box(
            "STATION_TranslucentCanopyMembrane",
            (52.0, 32.0, 0.16),
            (0.0, 0.0, 28.92),
            m["membrane"],
            0.03,
        )
    )
    # Sparse roof planting keeps the terrace occupied without obscuring structure.
    for x in (-16.0, -5.0, 6.0, 17.0):
        objects.append(
            box(
                f"STATION_RoofPlanter_{x:+.0f}",
                (4.0, 1.2, 0.52),
                (x, 9.6, 22.34),
                m["green"],
                0.12,
            )
        )
    # A real glazed terrace guard matches the occupied roofline in the
    # goalpost and keeps the elevated public deck credible in oblique views.
    for side in (-1.0, 1.0):
        y = side * 11.55
        for bay in range(8):
            x0 = -21.8 + bay * 5.45
            x1 = x0 + 5.25
            objects.append(
                box(
                    f"STATION_RoofGuardGlass_{int(side):+d}_{bay}",
                    (x1 - x0, 0.06, 1.12),
                    ((x0 + x1) / 2, y, 22.70),
                    m["glass"],
                    0.015,
                )
            )
            objects.append(
                rectangular_beam(
                    f"STATION_RoofGuardPost_{int(side):+d}_{bay}",
                    (x0, y - side * 0.05, 22.12),
                    (x0, y - side * 0.05, 23.28),
                    0.075,
                    m["canopy"],
                    depth=0.075,
                )
            )
        objects.append(
            rectangular_beam(
                f"STATION_RoofGuardRail_{int(side):+d}",
                (-21.9, y - side * 0.05, 23.28),
                (21.9, y - side * 0.05, 23.28),
                0.085,
                m["canopy"],
                depth=0.085,
            )
        )
    return objects


def station_public_realm(m: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    objects = [
        box(
            "STATION_FullPlacementPlinth",
            (52.0, 32.0, 0.22),
            (0.0, 0.0, 0.11),
            m["concrete"],
            0.05,
        )
    ]
    for step in range(4):
        step_height = 0.14 * (step + 1)
        objects.append(
            box(
                f"STATION_EntryStep_{step}",
                (28.0 - step * 1.2, 0.72, step_height),
                (0.0, -15.64 + step * 0.36, step_height / 2),
                m["concrete"],
                0.04,
            )
        )
    for x in (-18.0, 18.0):
        objects.append(
            box(
                f"STATION_RainGarden_{x:+.0f}",
                (8.0, 2.0, 0.34),
                (x, -14.5, 0.42),
                m["green"],
                0.14,
            )
        )
    return objects


def station_fixed(m: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    objects = [
        *station_body(m),
        *station_concourse(m),
        *station_roof_canopy(m),
        *station_public_realm(m),
    ]
    return join_tokens(
        objects,
        [
            ("STATION_LouverSlat_", "STATION_PhysicalLouverSystem"),
            ("STATION_WindowMullion_", "STATION_UpperWindowMullionSystem"),
            ("STATION_PrimaryPost_", "STATION_PrimaryFrontPostSystem"),
            ("STATION_PrimaryBeam_", "STATION_PrimaryFrontBeamSystem"),
            ("STATION_SideCell_", "STATION_SecondaryFacadeCellSystem"),
            ("STATION_SidePost_", "STATION_SecondaryPostSystem"),
            ("STATION_SideBeam_", "STATION_SecondaryBeamSystem"),
            ("STATION_ConcoursePane_", "STATION_ConcoursePhysicalGlassSystem"),
            ("STATION_ConcoursePost_", "STATION_ConcoursePostSystem"),
            ("STATION_VerandaPost_", "STATION_VerandaPostSystem"),
            ("STATION_VerandaBracket_", "STATION_VerandaBracketSystem"),
            ("STATION_TreeColumn_", "STATION_TreeColumnSystem"),
            ("STATION_TreeBranch_", "STATION_TreeBranchSystem"),
            ("STATION_CanopyPrimaryX_", "STATION_CanopyPrimaryBeamSystem"),
            ("STATION_CanopyPurlinY_", "STATION_CanopyPurlinSystem"),
            ("STATION_RoofPlanter_", "STATION_RoofPlanterSystem"),
            ("STATION_RoofGuardGlass_", "STATION_RoofGuardGlassSystem"),
            ("STATION_RoofGuardPost_", "STATION_RoofGuardPostSystem"),
            ("STATION_EntryStep_", "STATION_EntryStairSystem"),
        ],
    )


SOUK_WIDTH = 49.0
SOUK_DEPTH = 24.0
SOUK_BAYS = 7
SOUK_BAY_WIDTH = SOUK_WIDTH / SOUK_BAYS
SOUK_FRONT_Y = -SOUK_DEPTH / 2
SOUK_WALL_TOP = 10.2


def pointed_arch_outline(
    width: float,
    z0: float,
    spring_z: float,
    peak_z: float,
    *,
    curve_steps: int = 22,
) -> list[tuple[float, float]]:
    half = width / 2
    points = [(-half, z0), (-half, spring_z)]
    for step in range(1, curve_steps + 1):
        t = step / curve_steps
        points.append(
            (
                -half * (1.0 - t),
                spring_z + (peak_z - spring_z) * math.sin(t * math.pi / 2) ** 0.90,
            )
        )
    for step in range(curve_steps - 1, 0, -1):
        t = step / curve_steps
        points.append(
            (
                half * (1.0 - t),
                spring_z + (peak_z - spring_z) * math.sin(t * math.pi / 2) ** 0.90,
            )
        )
    points.extend([(half, spring_z), (half, z0)])
    return points


def pointed_arch_ring(
    name: str,
    centre_x: float,
    front_y: float,
    back_y: float,
    m: bpy.types.Material,
    *,
    outer_width: float = 6.65,
    inner_width: float = 5.35,
    outer_z0: float = 0.28,
    inner_z0: float = 0.48,
    outer_spring: float = 5.35,
    inner_spring: float = 5.05,
    outer_peak: float = 9.62,
    inner_peak: float = 8.88,
) -> bpy.types.Object:
    outer_2d = pointed_arch_outline(
        outer_width,
        outer_z0,
        outer_spring,
        outer_peak,
    )
    inner_2d = pointed_arch_outline(
        inner_width,
        inner_z0,
        inner_spring,
        inner_peak,
    )
    assert len(outer_2d) == len(inner_2d)
    count = len(outer_2d)
    vertices = []
    for y, outline in (
        (front_y, outer_2d),
        (front_y, inner_2d),
        (back_y, outer_2d),
        (back_y, inner_2d),
    ):
        vertices.extend((centre_x + x, y, z) for x, z in outline)
    outer_front, inner_front, outer_back, inner_back = (
        0,
        count,
        count * 2,
        count * 3,
    )
    faces: list[tuple[int, ...]] = []
    for index in range(count - 1):
        nxt = index + 1
        faces.extend(
            [
                (
                    outer_front + index,
                    outer_front + nxt,
                    inner_front + nxt,
                    inner_front + index,
                ),
                (
                    outer_back + nxt,
                    outer_back + index,
                    inner_back + index,
                    inner_back + nxt,
                ),
                (
                    outer_front + index,
                    outer_back + index,
                    outer_back + nxt,
                    outer_front + nxt,
                ),
                (
                    inner_front + nxt,
                    inner_back + nxt,
                    inner_back + index,
                    inner_front + index,
                ),
            ]
        )
    # Close only the two vertical feet; leave the threshold genuinely open.
    for index in (0, count - 1):
        faces.append(
            (
                outer_front + index,
                inner_front + index,
                inner_back + index,
                outer_back + index,
            )
        )
    return mesh_object(name, vertices, faces, m, uv_scale=2.4)


def pointed_arch_voussoir_joints(
    centre_x: float,
    front_y: float,
    bay: int,
    m: bpy.types.Material,
) -> list[bpy.types.Object]:
    """Lay recessed radial joints across the physical pointed-arch ring."""
    outer = pointed_arch_outline(6.65, 0.28, 5.35, 9.62)
    inner = pointed_arch_outline(5.35, 0.48, 5.05, 8.88)
    objects: list[bpy.types.Object] = []
    indices = [*range(4, 23, 3), *range(26, 45, 3)]
    for joint, index in enumerate(indices):
        outer_x, outer_z = outer[index]
        inner_x, inner_z = inner[index]
        objects.append(
            rectangular_beam(
                f"SOUK_VoussoirJoint_{bay}_{joint}",
                (centre_x + outer_x, front_y - 0.025, outer_z),
                (centre_x + inner_x, front_y - 0.025, inner_z),
                0.050,
                m,
                depth=0.040,
            )
        )
    return objects


def pointed_arch_top(
    local_x: float,
    width: float = 5.35,
    spring_z: float = 5.05,
    peak_z: float = 8.88,
) -> float:
    half = width / 2
    normalized = min(1.0, abs(local_x) / half)
    t = 1.0 - normalized
    return spring_z + (peak_z - spring_z) * math.sin(t * math.pi / 2) ** 0.90


def hemisphere_mesh(
    name: str,
    centre: tuple[float, float],
    radii: tuple[float, float, float],
    base_z: float,
    mat: bpy.types.Material,
    *,
    segments: int = 40,
    rings: int = 14,
) -> bpy.types.Object:
    cx, cy = centre
    rx, ry, rz = radii
    vertices: list[tuple[float, float, float]] = []
    for ring in range(rings + 1):
        latitude = (math.pi / 2) * ring / rings
        radial = math.cos(latitude)
        z = base_z + rz * math.sin(latitude)
        for segment in range(segments):
            angle = 2.0 * math.pi * segment / segments
            vertices.append(
                (
                    cx + rx * radial * math.cos(angle),
                    cy + ry * radial * math.sin(angle),
                    z,
                )
            )
    faces: list[tuple[int, ...]] = []
    for ring in range(rings):
        for segment in range(segments):
            nxt = (segment + 1) % segments
            a = ring * segments + segment
            b = ring * segments + nxt
            c = (ring + 1) * segments + nxt
            d = (ring + 1) * segments + segment
            faces.append((a, b, c, d))
    obj = mesh_object(name, vertices, faces, mat, uv_scale=2.2)
    return shade_smooth(obj)


def souk_frontage(m: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = [
        mapped_reference_panel(
            "SOUK_RenderLockedOccupiedDepth",
            (
                (-SOUK_WIDTH / 2, SOUK_FRONT_Y + 3.65, 0.3),
                (SOUK_WIDTH / 2, SOUK_FRONT_Y + 3.65, 0.3),
                (SOUK_WIDTH / 2, SOUK_FRONT_Y + 3.65, SOUK_WALL_TOP),
                (-SOUK_WIDTH / 2, SOUK_FRONT_Y + 3.65, SOUK_WALL_TOP),
            ),
            m["underlay"],
            model_x_bounds=(-SOUK_WIDTH / 2, SOUK_WIDTH / 2),
            model_z_bounds=(0.3, SOUK_WALL_TOP),
            source_uv_bounds=(0.04, 0.28, 0.96, 0.80),
        ),
        box(
            "SOUK_UpperSpandrelBand",
            (SOUK_WIDTH, 1.1, 0.72),
            (0.0, SOUK_FRONT_Y + 0.55, 9.84),
            m["stone"],
            0.08,
        ),
        box(
            "SOUK_CarvedCornice",
            (SOUK_WIDTH, 0.60, 0.46),
            (0.0, SOUK_FRONT_Y + 0.30, 10.10),
            m["stone"],
            0.08,
        ),
    ]
    for boundary in range(SOUK_BAYS + 1):
        x = -SOUK_WIDTH / 2 + boundary * SOUK_BAY_WIDTH
        if boundary == 0:
            x += 0.56
        elif boundary == SOUK_BAYS:
            x -= 0.56
        objects.append(
            box(
                f"SOUK_StonePier_{boundary}",
                (1.12, 2.12, SOUK_WALL_TOP),
                (x, SOUK_FRONT_Y + 1.10, SOUK_WALL_TOP / 2),
                m["stone"],
                0.10,
            )
        )
        # True coursing on each pier keeps the stone legible at close range
        # without stretching a photographed facade across a narrow solid.
        for course in range(1, 18):
            z = course * 0.55
            objects.append(
                box(
                    f"SOUK_PierBedJoint_{boundary}_{course}",
                    (1.04, 0.040, 0.036),
                    (x, SOUK_FRONT_Y + 0.020, z),
                    m["mortar"],
                    0.008,
                )
            )
        for course in range(0, 17, 2):
            offset = -0.22 if (course // 2 + boundary) % 2 else 0.22
            objects.append(
                box(
                    f"SOUK_PierHeadJoint_{boundary}_{course}",
                    (0.032, 0.040, 0.48),
                    (x + offset, SOUK_FRONT_Y + 0.020, course * 0.55 + 0.275),
                    m["mortar"],
                    0.006,
                )
            )
    for bay in range(SOUK_BAYS):
        centre_x = -SOUK_WIDTH / 2 + SOUK_BAY_WIDTH * (bay + 0.5)
        objects.append(
            pointed_arch_ring(
                f"SOUK_DeepPointedArch_{bay}",
                centre_x,
                SOUK_FRONT_Y + 0.04,
                SOUK_FRONT_Y + 2.25,
                m["stone"],
            )
        )
        objects.extend(
            pointed_arch_voussoir_joints(
                centre_x,
                SOUK_FRONT_Y + 0.04,
                bay,
                m["mortar"],
            )
        )
        # Carved mashrabiya is a bounded screen within the upper arch.
        for bar in range(7):
            local_x = -2.30 + 4.60 * bar / 6
            top = pointed_arch_top(local_x) - 0.28
            objects.append(
                rectangular_beam(
                    f"SOUK_MashrabiyaVertical_{bay}_{bar}",
                    (centre_x + local_x, SOUK_FRONT_Y + 2.47, 5.28),
                    (centre_x + local_x, SOUK_FRONT_Y + 2.47, top),
                    0.105,
                    m["timber"],
                    depth=0.12,
                )
            )
        for row, z in enumerate((6.05, 6.92, 7.74)):
            t = (z - 5.05) / (8.88 - 5.05)
            half = 2.675 * (
                1.0 - (2.0 / math.pi) * math.asin(min(1.0, t ** (1 / 0.90)))
            )
            half = max(0.45, half)
            objects.append(
                rectangular_beam(
                    f"SOUK_MashrabiyaHorizontal_{bay}_{row}",
                    (centre_x - half, SOUK_FRONT_Y + 2.45, z),
                    (centre_x + half, SOUK_FRONT_Y + 2.45, z),
                    0.095,
                    m["timber"],
                    depth=0.12,
                )
            )
        # Fine crossed lattice supplies the small-scale mashrabiya identity
        # inside the coarse structural frame.
        for direction in (-1.0, 1.0):
            for offset_index in range(-6, 7):
                candidates: list[tuple[float, float, float]] = []
                for sample in range(49):
                    local_x = -2.30 + 4.60 * sample / 48
                    z = (
                        6.72
                        + direction * 0.58 * local_x
                        + offset_index * 0.30
                    )
                    if 5.33 <= z <= pointed_arch_top(local_x) - 0.20:
                        candidates.append(
                            (centre_x + local_x, SOUK_FRONT_Y + 2.41, z)
                        )
                if len(candidates) >= 2:
                    objects.append(
                        rectangular_beam(
                            (
                                f"SOUK_MashrabiyaFine_{bay}_"
                                f"{int(direction):+d}_{offset_index:+d}"
                            ),
                            candidates[0],
                            candidates[-1],
                            0.034,
                            m["timber"],
                            depth=0.045,
                        )
                    )
        # Shopfronts sit well behind the facade plane and terminate the arcade.
        objects.append(
            box(
                f"SOUK_RecessedShopGlazing_{bay}",
                (4.65, 0.10, 3.25),
                (centre_x, SOUK_FRONT_Y + 3.50, 2.08),
                m["glass"],
                0.02,
            )
        )
        for bar in range(5):
            x = centre_x - 2.15 + 4.30 * bar / 4
            objects.append(
                rectangular_beam(
                    f"SOUK_ShopfrontVertical_{bay}_{bar}",
                    (x, SOUK_FRONT_Y + 3.38, 0.48),
                    (x, SOUK_FRONT_Y + 3.38, 3.72),
                    0.10,
                    m["timber"],
                    depth=0.14,
                )
            )
        objects.append(
            rectangular_beam(
                f"SOUK_ShopfrontTransom_{bay}",
                (centre_x - 2.20, SOUK_FRONT_Y + 3.38, 3.05),
                (centre_x + 2.20, SOUK_FRONT_Y + 3.38, 3.05),
                0.11,
                m["timber"],
                depth=0.14,
            )
        )
        # One real suspended lantern per bay.
        objects.append(
            cylinder(
                f"SOUK_LanternChain_{bay}",
                0.025,
                1.0,
                (centre_x, SOUK_FRONT_Y + 2.65, 4.68),
                m["bronze"],
                10,
            )
        )
        objects.append(
            sphere(
                f"SOUK_LanternBody_{bay}",
                0.32,
                (centre_x, SOUK_FRONT_Y + 2.65, 4.08),
                m["bronze"],
                (0.78, 0.78, 1.15),
                24,
                12,
            )
        )
        objects.append(
            cylinder(
                f"SOUK_LanternGlow_{bay}",
                0.13,
                0.34,
                (centre_x, SOUK_FRONT_Y + 2.65, 4.08),
                m["lantern_glow"],
                16,
            )
        )
    return objects


def souk_envelope(m: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    objects = [
        box(
            "SOUK_LeftSideWall",
            (1.15, SOUK_DEPTH, SOUK_WALL_TOP),
            (-SOUK_WIDTH / 2 + 0.575, 0.0, SOUK_WALL_TOP / 2),
            m["stone"],
            0.10,
        ),
        box(
            "SOUK_RightSideWall",
            (1.15, SOUK_DEPTH, SOUK_WALL_TOP),
            (SOUK_WIDTH / 2 - 0.575, 0.0, SOUK_WALL_TOP / 2),
            m["stone"],
            0.10,
        ),
        box(
            "SOUK_RearServiceWall",
            (SOUK_WIDTH, 0.90, SOUK_WALL_TOP),
            (0.0, SOUK_DEPTH / 2 - 0.45, SOUK_WALL_TOP / 2),
            m["stone"],
            0.10,
        ),
        box(
            "SOUK_RoofDeck",
            (SOUK_WIDTH, SOUK_DEPTH, 0.30),
            (0.0, 0.0, 10.02),
            m["stone"],
            0.05,
        ),
    ]
    # Three restrained side openings keep the market occupied in orbit views.
    for side in (-1, 1):
        x = side * (SOUK_WIDTH / 2 - 0.10)
        for index, y in enumerate((-6.0, 0.0, 6.0)):
            objects.append(
                box(
                    f"SOUK_SideRecess_{side}_{index}",
                    (0.10, 3.2, 4.8),
                    (x, y, 3.6),
                    m["dark"],
                    0.12,
                )
            )
            for bar in range(4):
                local_y = y - 1.30 + 2.60 * bar / 3
                objects.append(
                    rectangular_beam(
                        f"SOUK_SideScreen_{side}_{index}_{bar}",
                        (x - side * 0.08, local_y, 1.0),
                        (x - side * 0.08, local_y, 6.0),
                        0.10,
                        m["timber"],
                        depth=0.12,
                    )
                )
    return objects


def souk_roof(m: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    for bay in range(SOUK_BAYS):
        x = -SOUK_WIDTH / 2 + SOUK_BAY_WIDTH * (bay + 0.5)
        objects.append(
            hemisphere_mesh(
                f"SOUK_Dome_{bay}",
                (x, 0.2),
                (3.20, 4.60, 3.72),
                10.18,
                m["dome"],
            )
        )
        objects.append(
            cylinder(
                f"SOUK_DomeOculusCap_{bay}",
                0.18,
                0.38,
                (x, 0.2, 14.10),
                m["bronze"],
                16,
            )
        )
        objects.append(
            sphere(
                f"SOUK_DomeFinial_{bay}",
                0.14,
                (x, 0.2, 14.36),
                m["bronze"],
                (1.0, 1.0, 1.0),
                16,
                8,
            )
        )
    return objects


def souk_public_realm(m: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    objects = [
        box(
            "SOUK_FullPlacementPlinth",
            (SOUK_WIDTH, SOUK_DEPTH, 0.26),
            (0.0, 0.0, 0.13),
            m["concrete"],
            0.05,
        )
    ]
    for bay in range(SOUK_BAYS):
        x = -SOUK_WIDTH / 2 + SOUK_BAY_WIDTH * (bay + 0.5)
        objects.append(
            box(
                f"SOUK_StoneThreshold_{bay}",
                (5.30, 1.80, 0.20),
                (x, SOUK_FRONT_Y + 0.90, 0.28),
                m["stone"],
                0.04,
            )
        )
    return objects


def souk_fixed(m: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    objects = [
        *souk_frontage(m),
        *souk_envelope(m),
        *souk_roof(m),
        *souk_public_realm(m),
    ]
    return join_tokens(
        objects,
        [
            ("SOUK_DeepPointedArch_", "SOUK_SevenDeepPointedArchSystem"),
            ("SOUK_VoussoirJoint_", "SOUK_VoussoirJointSystem"),
            ("SOUK_PierBedJoint_", "SOUK_PierBedJointSystem"),
            ("SOUK_PierHeadJoint_", "SOUK_PierHeadJointSystem"),
            ("SOUK_MashrabiyaVertical_", "SOUK_MashrabiyaVerticalSystem"),
            ("SOUK_MashrabiyaHorizontal_", "SOUK_MashrabiyaHorizontalSystem"),
            ("SOUK_MashrabiyaFine_", "SOUK_MashrabiyaFineLatticeSystem"),
            ("SOUK_RecessedShopGlazing_", "SOUK_RecessedShopGlazingSystem"),
            ("SOUK_ShopfrontVertical_", "SOUK_ShopfrontVerticalSystem"),
            ("SOUK_ShopfrontTransom_", "SOUK_ShopfrontTransomSystem"),
            ("SOUK_LanternChain_", "SOUK_LanternChainSystem"),
            ("SOUK_LanternBody_", "SOUK_LanternBodySystem"),
            ("SOUK_LanternGlow_", "SOUK_LanternGlowSystem"),
            ("SOUK_SideScreen_", "SOUK_SecondaryMashrabiyaSystem"),
            ("SOUK_Dome_", "SOUK_SevenAlignedDomeSystem"),
            ("SOUK_DomeOculusCap_", "SOUK_DomeOculusCapSystem"),
            ("SOUK_DomeFinial_", "SOUK_DomeFinialSystem"),
            ("SOUK_StoneThreshold_", "SOUK_StoneThresholdSystem"),
        ],
    )


def ellipse_prism(
    name: str,
    radius_x: float,
    radius_y: float,
    z0: float,
    z1: float,
    mat: bpy.types.Material,
    *,
    segments: int = 40,
) -> bpy.types.Object:
    vertices: list[tuple[float, float, float]] = []
    for z in (z0, z1):
        vertices.extend(
            (
                radius_x * math.cos(2.0 * math.pi * step / segments),
                radius_y * math.sin(2.0 * math.pi * step / segments),
                z,
            )
            for step in range(segments)
        )
    faces: list[tuple[int, ...]] = [
        tuple(range(segments - 1, -1, -1)),
        tuple(range(segments, segments * 2)),
    ]
    for step in range(segments):
        nxt = (step + 1) % segments
        faces.append((step, nxt, segments + nxt, segments + step))
    return mesh_object(name, vertices, faces, mat, uv_scale=3.0)


def fluid_fallback_module(
    role: str,
    variant: str,
    height: float,
    m: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    if role == "roof":
        objects.append(
            ellipse_prism(
                "FLUIDKIT_ContinuousRoof",
                23.0,
                17.0,
                0.0,
                height,
                m["roof"],
                segments=36,
            )
        )
        objects.append(
            ellipse_prism(
                "FLUIDKIT_RoofSkylight",
                8.0,
                4.8,
                height - 0.10,
                height,
                m["glass"],
                segments=32,
            )
        )
        return objects
    inset = 1.2 if role == "crown" else 0.0
    objects.append(
        ellipse_prism(
            f"FLUIDKIT_{role}_{variant}_Shell",
            23.0 - inset,
            17.0 - inset,
            0.0,
            height,
            m["shell"] if variant != "typical_b" else m["side"],
            segments=36,
        )
    )
    front_y = -(17.0 - inset) - 0.06
    if role == "podium":
        objects.append(
            box(
                "FLUIDKIT_CarvedEntranceGlazing",
                (13.0, 0.12, height * 0.68),
                (8.0, front_y, height * 0.43),
                m["glass"],
                0.90,
            )
        )
    else:
        for index, x in enumerate((-13.0, -5.0, 4.0, 12.0)):
            objects.append(
                box(
                    f"FLUIDKIT_{role}_{variant}_OrganicPane_{index}",
                    (5.2, 0.10, height * 0.46),
                    (x, front_y, height * (0.48 + 0.06 * ((index + len(variant)) % 2))),
                    m["glass"],
                    min(1.0, height * 0.20),
                )
            )
    return objects


def station_fallback_module(
    role: str,
    variant: str,
    height: float,
    m: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    width, depth = 52.0, 32.0
    objects: list[bpy.types.Object] = []
    if role == "roof":
        objects.append(
            box(
                "STATIONKIT_RoofTerrace",
                (width, depth, 0.28),
                (0.0, 0.0, 0.14),
                m["timber"],
                0.06,
            )
        )
        for x in (-20.0, -10.0, 0.0, 10.0, 20.0):
            objects.append(
                rectangular_beam(
                    f"STATIONKIT_CanopyTree_{x:+.0f}",
                    (x, 0.0, 0.28),
                    (x, 0.0, height - 0.65),
                    0.34,
                    m["canopy"],
                    depth=0.40,
                )
            )
            for target_y in (-12.0, 12.0):
                objects.append(
                    rectangular_beam(
                        f"STATIONKIT_CanopyBranch_{x:+.0f}_{target_y:+.0f}",
                        (x, 0.0, height * 0.55),
                        (x, target_y, height - 0.45),
                        0.22,
                        m["canopy"],
                        depth=0.28,
                    )
                )
        objects.append(
            box(
                "STATIONKIT_TranslucentCanopy",
                (width, depth, 0.16),
                (0.0, 0.0, height - 0.08),
                m["membrane"],
                0.03,
            )
        )
        return objects

    body_mat = m["timber"] if role == "podium" else m["facade"]
    objects.append(
        box(
            f"STATIONKIT_{role}_{variant}_Body",
            (width, depth, height),
            (0.0, 0.0, height / 2),
            m["dark"],
            0.10,
        )
    )
    bay_width = width / 8
    front_y = -depth / 2 - 0.06
    for column in range(8):
        x = -width / 2 + bay_width * (column + 0.5)
        if role == "podium" or (column + len(variant)) % 3 == 0:
            mat = m["glass"]
        elif (column + len(variant)) % 2:
            mat = m["louver"]
        else:
            mat = body_mat
        objects.append(
            box(
                f"STATIONKIT_{role}_{variant}_Bay_{column}",
                (bay_width - 0.32, 0.10, height - 0.38),
                (x, front_y, height / 2),
                mat,
                0.03,
            )
        )
        objects.append(
            rectangular_beam(
                f"STATIONKIT_{role}_{variant}_Post_{column}",
                (-width / 2 + column * bay_width, front_y - 0.08, 0.10),
                (-width / 2 + column * bay_width, front_y - 0.08, height - 0.10),
                0.20,
                m["timber"],
                depth=0.25,
            )
        )
    return objects


def souk_fallback_module(
    role: str,
    variant: str,
    height: float,
    m: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    if role == "roof":
        objects.append(
            box(
                "SOUKKIT_RoofDeck",
                (SOUK_WIDTH, SOUK_DEPTH, 0.24),
                (0.0, 0.0, 0.12),
                m["stone"],
                0.05,
            )
        )
        for bay in range(SOUK_BAYS):
            x = -SOUK_WIDTH / 2 + SOUK_BAY_WIDTH * (bay + 0.5)
            objects.append(
                hemisphere_mesh(
                    f"SOUKKIT_Dome_{bay}",
                    (x, 0.0),
                    (3.20, 4.60, height - 0.45),
                    0.18,
                    m["dome"],
                    segments=28,
                    rings=10,
                )
            )
        return objects
    objects.append(
        box(
            f"SOUKKIT_{role}_{variant}_Body",
            (SOUK_WIDTH, SOUK_DEPTH, height),
            (0.0, 0.0, height / 2),
            m["stone"],
            0.10,
        )
    )
    front_y = -SOUK_DEPTH / 2 - 0.06
    if role == "podium":
        for bay in range(SOUK_BAYS):
            x = -SOUK_WIDTH / 2 + SOUK_BAY_WIDTH * (bay + 0.5)
            objects.append(
                box(
                    f"SOUKKIT_RecessedShop_{bay}",
                    (SOUK_BAY_WIDTH - 1.25, 0.12, height * 0.68),
                    (x, front_y, height * 0.42),
                    m["glass"],
                    0.55,
                )
            )
            for boundary in (x - SOUK_BAY_WIDTH / 2, x + SOUK_BAY_WIDTH / 2):
                objects.append(
                    rectangular_beam(
                        f"SOUKKIT_Pier_{bay}_{boundary:+.1f}",
                        (boundary, front_y - 0.10, 0.0),
                        (boundary, front_y - 0.10, height),
                        0.50,
                        m["stone"],
                        depth=0.70,
                    )
                )
    else:
        for bay in range(SOUK_BAYS):
            x = -SOUK_WIDTH / 2 + SOUK_BAY_WIDTH * (bay + 0.5)
            objects.append(
                box(
                    f"SOUKKIT_Mashrabiya_{role}_{variant}_{bay}",
                    (SOUK_BAY_WIDTH - 1.20, 0.14, height * 0.58),
                    (x, front_y, height * 0.52),
                    m["timber"],
                    0.42,
                )
            )
    return objects


def fallback_module(
    family: str,
    role: str,
    variant: str,
    height: float,
    m: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    if family == "parametric-fluid-hub":
        return fluid_fallback_module(role, variant, height, m)
    if family == "timber-transit-station":
        return station_fallback_module(role, variant, height, m)
    return souk_fallback_module(role, variant, height, m)


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
    cfg = FAMILIES[family]
    width, depth, height = cfg["dimensions"]
    distance = max(width, depth)
    views = {
        "preview": (
            (width * 0.72, -distance * 2.25, height * 1.02),
            (0.0, -1.0, height * 0.43),
            50,
        ),
        "street": (
            (0.0, -distance * 2.42, height * 0.40),
            (0.0, -1.0, height * 0.42),
            54,
        ),
        "front_corner_oblique": (
            (-width * 0.88, -distance * 2.05, height * 0.90),
            (0.0, 0.0, height * 0.42),
            50,
        ),
        "rear_corner_oblique": (
            (width * 0.84, distance * 2.08, height * 0.94),
            (0.0, 0.0, height * 0.44),
            50,
        ),
        "aerial": (
            (width * 0.88, -distance * 1.36, height * 3.20),
            (0.0, 0.0, height * 0.28),
            48,
        ),
        "facade_close": (
            (0.0, -distance * 2.08, height * 0.38),
            (0.0, -depth * 0.30, height * 0.42),
            58,
        ),
        "identity_close": (
            (-width * 0.55, -distance * 0.82, height * 0.46),
            cfg["close_target"],
            60,
        ),
        "context": (
            (width * 0.16, -distance * 2.72, height * 0.78),
            (0.0, 0.0, height * 0.42),
            54,
        ),
    }
    if family == "covered-souk-market":
        # The goalpost is a warm, low street oblique where the depth of the
        # stone arcade is the primary read. A closer camera and grazing sun
        # make the actual recesses, voussoirs, coursing, and mashrabiya
        # legible without baking presentation shadows into the GLB.
        background = scene.world.node_tree.nodes.get("Background")
        background.inputs["Color"].default_value = (0.30, 0.285, 0.255, 1.0)
        background.inputs["Strength"].default_value = 0.96
        ground = bpy.data.materials.get("MAT_W3_Ground")
        if ground and ground.use_nodes:
            ground.node_tree.nodes["Principled BSDF"].inputs[
                "Base Color"
            ].default_value = (0.34, 0.30, 0.25, 1.0)
        scene.view_settings.exposure = 1.55
        bpy.ops.object.light_add(
            type="SUN",
            location=(width * 0.9, -distance * 1.4, height * 4.0),
        )
        sun = bpy.context.object
        sun.name = "PRESENTATION_SoukSun"
        sun.data.energy = 1.8
        sun.data.angle = math.radians(9.0)
        sun.rotation_euler = (
            Vector((0.0, 0.0, height * 0.35)) - sun.location
        ).to_track_quat("-Z", "Y").to_euler()
        views["preview"] = (
            (width * 0.78, -distance * 1.30, height * 0.62),
            (0.0, -1.5, height * 0.40),
            50,
        )
        views["street"] = (
            (width * 0.82, -distance * 1.16, height * 0.28),
            (0.0, -2.0, height * 0.34),
            48,
        )
        views["identity_close"] = (
            (width * 0.48, -distance * 0.72, height * 0.50),
            (width * 0.12, SOUK_FRONT_Y + 1.8, height * 0.42),
            58,
        )
    selected = (
        {"preview", "street", "front_corner_oblique", "aerial", "identity_close"}
        if view_set == "pilot"
        else set(views)
    )

    snapshots: list[tuple[bpy.types.Material, bpy.types.Node, float, float, str]] = []
    for mat in bpy.data.materials:
        if not mat.get("glazing_profile") or not mat.use_nodes:
            continue
        # Souk shopfronts are intentionally low-transmission amber panes set
        # deep in a stone arcade. The general clear-glass proof override would
        # reveal the pale presentation ground and erase that shadowed depth.
        if family == "covered-souk-market":
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
        bsdf.inputs["Alpha"].default_value = 0.15
        mat.diffuse_color = (*tuple(mat.diffuse_color)[:3], 0.15)
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
    inventory: list[dict] = []
    for zone, lods in skin["zones"].items():
        for lod, assets in lods.items():
            for channel, path in assets.items():
                inventory.append(
                    {
                        "key": f"{zone}_{lod}_{channel}",
                        "path": path,
                        "lod": lod,
                        "channel": channel,
                        "zone": zone,
                    }
                )
    return inventory


def evaluated_triangle_count(objects: list[bpy.types.Object]) -> int:
    """Count the triangles Blender's evaluated export graph will actually emit."""
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
            total += sum(max(0, len(polygon.vertices) - 2) for polygon in mesh.polygons)
        finally:
            evaluated.to_mesh_clear()
    return total


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
        "material_count": len(
            {
                mat.name
                for obj in objects
                if obj.type == "MESH"
                for mat in obj.data.materials
            }
        ),
        "texture_keys": sorted(skin["zones"]),
        "ao_baked": True,
        "size_bytes": size_bytes,
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
            "The selected catalogue card is the hard identity authority. The "
            "rectified source fixes silhouette, occupied level count, opening "
            "schedule, material hierarchy and roof construction before assembly."
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
                "The complete reference landmark stays fixed in-band. Only the "
                "related family-shaped fallback bays repeat for larger parcels."
            ),
        },
        "delivery": {
            "near_atlas_width_px": 2048,
            "far_atlas_width_px": 1024,
            "near_usage": (
                "registered skin plus physical openings, structure, reveals and "
                "occupied depth"
            ),
            "far_usage": "city-scale render-locked archetype material reference",
        },
        "assembly_contract": {
            "fixed": [
                "podium/entrance",
                "corner returns",
                "crown",
                "roof",
                *cfg["kits"],
            ],
            "repeatable": ["typical_a", "typical_b", "typical_c"],
            "side_elevations": (
                "Material datums, structure and roof logic wrap the left, right "
                "and rear elevations; ceremonial front elements remain fixed."
            ),
            "elevation_coverage": {
                "front": cfg["identity"],
                "left": "related structural/material return with secondary openings",
                "right": "related structural/material return with secondary openings",
                "rear": "quieter occupied service elevation",
                "roof": cfg["silhouette"],
            },
            "variation_policy": (
                "Mild independent X/Y scaling keeps the whole landmark. Larger "
                "or axis-distorting drawings switch to the family-shaped stack "
                "and streetwall repeat."
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


def provenance(family: str) -> dict:
    cfg = FAMILIES[family]
    return {
        "kind": "catalogue_goalpost_plus_imagegen_reference_package_and_authored_geometry",
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
        "generator": "tools/archetype_compiler/generate_wave8_reference_families.py",
        "reference_method": (
            "hard catalogue goalpost, registration-preserving orthographic source, "
            "physical openings and structure, occupied-depth underlay, and finite "
            "street/oblique/aerial comparison"
        ),
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
                    "id": "landmark",
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
            "name": "archetype_compiler/generate_wave8_reference_families.py",
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
            "wave8_reference_batch",
            "fixed_landmark",
            "custom_pbr_skin",
            "physical_glazing",
            "reference_locked",
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
            "max_assembled_materials": 24,
            "rationale": (
                "Reference skin, physical glazing, occupied depth, structure, "
                "roof and family-specific detail systems remain semantically separate."
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


FIXED_BUILDERS: dict[str, Callable[[dict[str, bpy.types.Material]], list[bpy.types.Object]]] = {
    "parametric-fluid-hub": fluid_fixed,
    "timber-transit-station": station_fixed,
    "covered-souk-market": souk_fixed,
}


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
    fixed_materials = len(
        {
            mat.name
            for obj in fixed
            if obj.type == "MESH"
            for mat in obj.data.materials
        }
    )
    renders = (
        sorted(path.name for path in folder.glob(f"{family}_*.png"))
        if skip_renders
        else render_views(family, folder, view_set=view_set)
    )
    if skip_modules:
        print(
            f"[wave8] {family} fixed only: {fixed_triangles:,} tris, "
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
        f"[wave8] {family}: {fixed_triangles:,} tris, "
        f"{fixed_materials} materials, {len(modules)} modules, {len(renders)} renders",
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
    print(f"[wave8-render] {family}: {len(manifest['renders'])} renders")


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
