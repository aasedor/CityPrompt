"""Author the Wave 10 Prairie Modern Fuel Bar LEGO family.

The fixed assembled GLB is a complete 35 m x 30 m roadside site rather than a
generic store box.  Its six-column canopy, exactly three pump islands, physical
hoses and dispensers, occupied low-E storefront, roof plant, price pylon,
propane cage, drainage and service yard are deterministic metric geometry.
A conservative semantic stack remains available for out-of-band LEGO plans.

Run with Blender 5.x from the repository root:

    blender --background --factory-startup --python \
      tools/archetype_compiler/generate_wave10_gas_station_family.py -- \
      --output-root frontend/public/families --view-set pilot
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


FAMILY = "prairie-modern-fuel-bar"
ARCHETYPE_ID = "rural_gas_station"
VARIANT_ID = "gas_modern_fuel_bar"
ALIASES = [
    ARCHETYPE_ID,
    VARIANT_ID,
    "modern_fuel_bar",
    "prairie_fuel_bar",
]
LABEL = "Rural Gas Station — Prairie Modern Fuel Bar"
GLASS_PROFILE = "low_iron_clear"

NATIVE_WIDTH = 35.0
NATIVE_DEPTH = 30.0
NATIVE_HEIGHT = 9.5
NATIVE_FLOORS = 1
MIN_FLOORS = 1
MAX_FLOORS = 1
PODIUM_HEIGHT = 0.45
FLOOR_HEIGHT = 4.05
CROWN_HEIGHT = 1.0
ROOF_HEIGHT = 0.60

STORE_WIDTH = 24.0
STORE_DEPTH = 10.0
STORE_FRONT_Y = 4.5
STORE_REAR_Y = 14.5
CANOPY_WIDTH = 28.0
CANOPY_DEPTH = 14.0
CANOPY_CENTRE_Y = -5.5
CANOPY_UNDERSIDE_Z = 5.35
CANOPY_TOP_Z = 6.05

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
        choices=("preview", "pilot", "all"),
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
    """Tame image-derived relief where the source is perspective photography."""
    if not mat.use_nodes:
        return mat
    for node in mat.node_tree.nodes:
        if node.bl_idname == "ShaderNodeNormalMap":
            node.inputs["Strength"].default_value = strength
    return mat


def make_glass_material(
    folder: Path,
    assets: dict[str, str],
) -> bpy.types.Material:
    # Window materiality is optical, not a facade photograph.  The registered
    # source remains in the skin package and semantic masks, while the actual
    # pane uses physical transmission so modeled shelves and coolers remain
    # visible at oblique angles.
    mat = material(
        "MAT_W10_FUELBAR_PhysicalLowEStorefront",
        (0.035, 0.072, 0.082, 0.34),
        0.035,
        metallic=0.02,
    )
    bsdf = bsdf_for(mat)
    if bsdf.inputs.get("Roughness"):
        bsdf.inputs["Roughness"].default_value = 0.035
    if bsdf.inputs.get("Transmission Weight"):
        bsdf.inputs["Transmission Weight"].default_value = 0.86
    if bsdf.inputs.get("Coat Weight"):
        bsdf.inputs["Coat Weight"].default_value = 0.42
    if bsdf.inputs.get("Coat Roughness"):
        bsdf.inputs["Coat Roughness"].default_value = 0.045
    if bsdf.inputs.get("IOR"):
        bsdf.inputs["IOR"].default_value = 1.52
    if bsdf.inputs.get("Alpha"):
        bsdf.inputs["Alpha"].default_value = 0.40
    try:
        mat.surface_render_method = "BLENDED"
    except Exception:
        pass
    mat.use_transparency_overlap = False
    mat["glazing_profile"] = GLASS_PROFILE
    mat["glazing_lod"] = "physical_separate_pane"
    mat["skin_zone"] = "storefront_glass"
    mat["pbr_channels"] = json.dumps(
        ["albedo", "normal", "roughness", "ao", "depth", "emissive"]
    )
    mat["semantic_glass_mask"] = assets["glass_mask"]
    mat["semantic_opaque_mask"] = assets["opaque_mask"]
    mat["pane_recess_m"] = 0.16
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
    mats: dict[str, bpy.types.Material] = {}
    mats["brick"] = grade_material(
        skin_material(
            "MAT_W10_FUELBAR_BuffModularBrick",
            folder,
            near["buff_brick"],
            "buff_brick",
        ),
        saturation=0.86,
        value=0.92,
    )
    mats["charcoal"] = grade_material(
        skin_material(
            "MAT_W10_FUELBAR_CharcoalMicroRibMetal",
            folder,
            near["charcoal_metal"],
            "charcoal_metal",
            metallic=0.46,
        ),
        saturation=0.72,
        value=0.58,
    )
    # Broad folded-aluminium planes use a clean physical response. Projecting
    # the perspective material photograph over the whole canopy introduced
    # false diagonal patches in the aerial view; the source remains registered
    # as provenance while seams, fascia and thickness are modeled explicitly.
    mats["white"] = material(
        "MAT_W10_FUELBAR_WhiteSatinCanopyAluminium",
        (0.72, 0.75, 0.76, 1.0),
        0.30,
        metallic=0.22,
    )
    mats["white"]["skin_zone"] = "canopy_aluminum"
    mats["white"]["source_reference"] = near["canopy_aluminum"]["albedo"]
    mats["white"]["reference_locked"] = True
    mats["white"]["surface_strategy"] = (
        "physical_uniform_response_with_modeled_seams_and_folded_edges"
    )
    mats["timber"] = grade_material(
        skin_material(
            "MAT_W10_FUELBAR_HoneyLinearSoffit",
            folder,
            near["timber_soffit"],
            "timber_soffit",
        ),
        saturation=0.92,
        value=0.82,
    )
    mats["concrete"] = set_normal_strength(
        grade_material(
            skin_material(
                "MAT_W10_FUELBAR_BroomFinishForecourt",
                folder,
                near["forecourt_concrete"],
                "forecourt_concrete",
            ),
            saturation=0.42,
            value=0.78,
        ),
        0.12,
    )
    mats["orange"] = grade_material(
        skin_material(
            "MAT_W10_FUELBAR_BurntOrangeIdentity",
            folder,
            near["burnt_orange"],
            "burnt_orange",
            metallic=0.18,
        ),
        saturation=1.16,
        value=0.86,
    )
    mats["pump"] = material(
        "MAT_W10_FUELBAR_PumpPowderCoat",
        (0.028, 0.038, 0.045, 1.0),
        0.30,
        metallic=0.32,
    )
    mats["pump"]["skin_zone"] = "pump_equipment"
    mats["pump"]["source_reference"] = near["pump_equipment"]["albedo"]
    mats["pump"]["reference_locked"] = True
    mats["stainless"] = skin_material(
        "MAT_W10_FUELBAR_StainlessProtection",
        folder,
        near["stainless"],
        "stainless",
        metallic=0.72,
    )
    mats["black"] = grade_material(
        skin_material(
            "MAT_W10_FUELBAR_BlackThermalBreakAndTrim",
            folder,
            near["black_trim"],
            "black_trim",
            metallic=0.34,
        ),
        saturation=0.62,
        value=0.42,
    )
    mats["roof"] = grade_material(
        skin_material(
            "MAT_W10_FUELBAR_DarkRoofMembrane",
            folder,
            near["roof_membrane"],
            "roof_membrane",
        ),
        saturation=0.48,
        value=0.54,
    )
    mats["interior"] = grade_material(
        skin_material(
            "MAT_W10_FUELBAR_OccupiedStoreDepth",
            folder,
            near["interior"],
            "store_interior",
            emission_strength=0.10,
        ),
        saturation=1.08,
        value=0.58,
    )
    mats["glass"] = make_glass_material(folder, near["storefront_glass"])
    mats["marking"] = material(
        "MAT_W10_FUELBAR_PavementMarking",
        (0.84, 0.74, 0.28, 1.0),
        0.78,
    )
    mats["warm_light"] = material(
        "MAT_W10_FUELBAR_WarmLED",
        (1.0, 0.58, 0.24, 1.0),
        0.16,
        emission=(1.0, 0.34, 0.10, 1.0),
        emission_strength=5.0,
    )
    mats["cool_light"] = material(
        "MAT_W10_FUELBAR_CoolInteriorLight",
        (0.82, 0.90, 1.0, 1.0),
        0.18,
        emission=(0.72, 0.84, 1.0, 1.0),
        emission_strength=2.0,
    )
    mats["cooler_depth"] = material(
        "MAT_W10_FUELBAR_CoolerCabinetDepth",
        (0.018, 0.040, 0.060, 1.0),
        0.46,
        emission=(0.05, 0.11, 0.15, 1.0),
        emission_strength=0.24,
    )
    mats["pump_screen"] = material(
        "MAT_W10_FUELBAR_PumpDisplayGlass",
        (0.012, 0.045, 0.065, 1.0),
        0.12,
        metallic=0.08,
        emission=(0.04, 0.22, 0.32, 1.0),
        emission_strength=0.62,
    )
    mats["pump_orange"] = material(
        "MAT_W10_FUELBAR_PumpBurntOrangePowderCoat",
        (0.58, 0.075, 0.018, 1.0),
        0.32,
        metallic=0.18,
    )
    mats["interior_warm"] = material(
        "MAT_W10_FUELBAR_WarmOccupiedStore",
        (0.30, 0.105, 0.025, 1.0),
        0.42,
        emission=(0.72, 0.18, 0.035, 1.0),
        emission_strength=0.45,
    )
    mats["red"] = material(
        "MAT_W10_FUELBAR_RedNozzle",
        (0.55, 0.025, 0.015, 1.0),
        0.34,
        metallic=0.12,
    )
    mats["green"] = material(
        "MAT_W10_FUELBAR_GreenNozzle",
        (0.035, 0.25, 0.065, 1.0),
        0.38,
        metallic=0.10,
    )
    mats["product_a"] = material(
        "MAT_W10_FUELBAR_ProductWarm",
        (0.64, 0.10, 0.018, 1.0),
        0.46,
        emission=(0.32, 0.035, 0.004, 1.0),
        emission_strength=0.20,
    )
    mats["product_b"] = material(
        "MAT_W10_FUELBAR_ProductCool",
        (0.018, 0.24, 0.44, 1.0),
        0.44,
        emission=(0.006, 0.08, 0.18, 1.0),
        emission_strength=0.18,
    )
    mats["prairie"] = grade_material(
        skin_material(
            "MAT_W10_FUELBAR_PrairiePlanting",
            folder,
            near["prairie_planting"],
            "prairie_planting",
        ),
        saturation=0.82,
        value=0.72,
    )
    mats["propane"] = material(
        "MAT_W10_FUELBAR_PropaneSilver",
        (0.56, 0.60, 0.61, 1.0),
        0.28,
        metallic=0.72,
    )
    return mats, skin


def tag_object(
    obj: bpy.types.Object,
    component: str,
    *,
    count_authority: str | None = None,
) -> bpy.types.Object:
    obj["component"] = component
    obj["source_variant_id"] = VARIANT_ID
    obj["generation_archetype_id"] = VARIANT_ID
    obj["reference_locked"] = True
    if count_authority:
        obj["count_authority"] = count_authority
    return obj


def b(
    name: str,
    size: tuple[float, float, float],
    location: tuple[float, float, float],
    mat: bpy.types.Material,
    bevel: float = 0.0,
    *,
    component: str,
    count_authority: str | None = None,
) -> bpy.types.Object:
    return tag_object(
        box(name, size, location, mat, bevel),
        component,
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
    count_authority: str | None = None,
) -> bpy.types.Object:
    return tag_object(
        cylinder(name, radius, depth, location, mat, vertices=vertices),
        component,
        count_authority=count_authority,
    )


def tube_curve(
    name: str,
    points: list[tuple[float, float, float]],
    radius: float,
    mat: bpy.types.Material,
    *,
    component: str,
    resolution: int = 2,
) -> bpy.types.Object:
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = resolution
    curve.bevel_depth = radius
    curve.bevel_resolution = 2
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for point, co in zip(spline.bezier_points, points):
        point.co = co
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return tag_object(obj, component)


def add_forecourt(
    mats: dict[str, bpy.types.Material],
    *,
    detailed: bool,
) -> list[bpy.types.Object]:
    objects = [
        b(
            "FUELBAR_ForecourtSlab",
            (NATIVE_WIDTH, NATIVE_DEPTH, 0.24),
            (0.0, 0.0, 0.12),
            mats["concrete"],
            0.05,
            component="complete_forecourt",
        )
    ]
    if not detailed:
        return objects
    # Saw-cut control joints remain shallow physical lines rather than a baked
    # grid, preventing the apron from reading as one smooth plastic slab.
    for index, x in enumerate((-12.0, -6.0, 0.0, 6.0, 12.0)):
        objects.append(
            b(
                f"FUELBAR_ForecourtJointX_{index:02d}",
                (0.035, 29.4, 0.018),
                (x, 0.0, 0.246),
                mats["black"],
                component="forecourt_control_joint",
            )
        )
    for index, y in enumerate((-12.0, -6.0, 0.0, 4.0, 9.0, 14.0)):
        objects.append(
            b(
                f"FUELBAR_ForecourtJointY_{index:02d}",
                (34.4, 0.035, 0.018),
                (0.0, y, 0.246),
                mats["black"],
                component="forecourt_control_joint",
            )
        )
    for drain_index, y in enumerate((-13.2, 2.6)):
        objects.append(
            b(
                f"FUELBAR_TrenchDrain_{drain_index}",
                (30.5, 0.18, 0.055),
                (0.8, y, 0.268),
                mats["black"],
                0.015,
                component="trench_drain",
            )
        )
        for rib in range(62):
            x = -14.2 + rib * 0.47
            objects.append(
                b(
                    f"FUELBAR_DrainRib_{drain_index}_{rib:02d}",
                    (0.045, 0.20, 0.016),
                    (x, y, 0.303),
                    mats["stainless"],
                    component="trench_drain_grate",
                )
            )
    # Parking and accessible-bay cues remain abstract, never readable branding.
    for index, x in enumerate((-8.7, -5.8, -2.9, 2.9, 5.8, 8.7)):
        objects.append(
            b(
                f"FUELBAR_ParkingLine_{index:02d}",
                (0.075, 2.75, 0.025),
                (x, 3.15, 0.27),
                mats["marking"],
                component="parking_marking",
            )
        )
    for index, (x, y) in enumerate(((-13.4, -12.5), (-10.0, -12.5), (-6.6, -12.5))):
        objects.extend(
            [
                c(
                    f"FUELBAR_TankFillCover_{index}",
                    0.34,
                    0.035,
                    (x, y, 0.28),
                    mats["stainless"],
                    vertices=32,
                    component="tank_fill_cover",
                ),
                c(
                    f"FUELBAR_TankFillRing_{index}",
                    0.22,
                    0.045,
                    (x, y, 0.30),
                    mats["orange"] if index == 0 else mats["black"],
                    vertices=32,
                    component="tank_fill_cover",
                ),
            ]
        )
    # A low perimeter curb fixes the complete site footprint without inventing
    # surrounding streets inside the reusable building asset.
    for name, size, loc in (
        ("Front", (35.0, 0.22, 0.24), (0.0, -14.88, 0.34)),
        ("Rear", (35.0, 0.22, 0.24), (0.0, 14.88, 0.34)),
        ("Left", (0.22, 29.5, 0.24), (-17.38, 0.0, 0.34)),
        ("Right", (0.22, 29.5, 0.24), (17.38, 0.0, 0.34)),
    ):
        objects.append(
            b(
                f"FUELBAR_SiteCurb_{name}",
                size,
                loc,
                mats["concrete"],
                0.025,
                component="site_curb",
            )
        )
    return objects


def add_storefront(
    mats: dict[str, bpy.types.Material],
    *,
    occupied: bool,
    schedule: str = "typical_a",
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    front_y = STORE_FRONT_Y + 0.16
    sill_z = 0.66
    head_z = 4.04
    sections = [
        (-9.72, -7.18),
        (-7.18, -4.62),
        (-4.62, -2.02),
        (-2.02, 2.02),
        (2.02, 4.62),
        (4.62, 7.18),
        (7.18, 9.72),
    ]
    # Deep masonry jambs and soffit make the glass a real recess.
    objects.extend(
        [
            b(
                "FUELBAR_StorefrontSill",
                (19.70, 0.42, 0.28),
                (0.0, front_y - 0.04, 0.52),
                mats["concrete"],
                0.025,
                component="storefront_sill",
            ),
            b(
                "FUELBAR_StorefrontHead",
                (20.20, 1.25, 0.32),
                (0.0, STORE_FRONT_Y - 0.38, 4.23),
                mats["timber"],
                0.03,
                component="projecting_entry_soffit",
            ),
            b(
                "FUELBAR_StorefrontHeadFlashing",
                (20.30, 1.30, 0.09),
                (0.0, STORE_FRONT_Y - 0.40, 4.41),
                mats["black"],
                component="storefront_head_flashing",
            ),
            b(
                "FUELBAR_LeftDeepJamb",
                (0.34, 0.48, 3.70),
                (-9.88, front_y, 2.42),
                mats["brick"],
                0.018,
                component="storefront_deep_jamb",
            ),
            b(
                "FUELBAR_RightDeepJamb",
                (0.34, 0.48, 3.70),
                (9.88, front_y, 2.42),
                mats["brick"],
                0.018,
                component="storefront_deep_jamb",
            ),
        ]
    )
    for section_index, (x0, x1) in enumerate(sections):
        width = x1 - x0
        centre = (x0 + x1) / 2
        if section_index == 3:
            # Two physical sliding doors and a separate transom.
            for door_index, door_x in enumerate((-1.02, 1.02)):
                pane = b(
                    f"FUELBAR_AutomaticDoorPane_{door_index}",
                    (1.90, 0.075, 2.86),
                    (door_x, front_y, 2.08),
                    mats["glass"],
                    0.008,
                    component="automatic_entry_door_glass",
                    count_authority="exactly_two_sliding_door_leaves",
                )
                objects.append(pane)
                for edge_x in (-0.92, 0.92):
                    objects.append(
                        b(
                            f"FUELBAR_DoorFrame_{door_index}_{edge_x:+.2f}",
                            (0.075, 0.14, 2.98),
                            (door_x + edge_x, front_y - 0.01, 2.08),
                            mats["black"],
                            component="thermally_broken_door_frame",
                        )
                    )
            objects.extend(
                [
                    b(
                        "FUELBAR_DoorCentreMeetingStile",
                        (0.085, 0.15, 2.95),
                        (0.0, front_y - 0.02, 2.08),
                        mats["black"],
                        component="automatic_door_meeting_stile",
                    ),
                    b(
                        "FUELBAR_EntryTransomPane",
                        (3.93, 0.075, 0.47),
                        (0.0, front_y, 3.80),
                        mats["glass"],
                        component="storefront_transom_glass",
                    ),
                    b(
                        "FUELBAR_AutomaticDoorHeader",
                        (4.05, 0.18, 0.18),
                        (0.0, front_y - 0.01, 3.50),
                        mats["black"],
                        component="automatic_door_operator_header",
                    ),
                ]
            )
        else:
            split = schedule == "typical_b" and section_index in {1, 5}
            if split:
                for half in (-0.25, 0.25):
                    objects.append(
                        b(
                            f"FUELBAR_StorefrontPane_{section_index}_{half:+.2f}",
                            (width / 2 - 0.08, 0.075, head_z - sill_z),
                            (
                                centre + half * width,
                                front_y,
                                (head_z + sill_z) / 2,
                            ),
                            mats["glass"],
                            component="physical_low_e_storefront_pane",
                        )
                    )
            else:
                objects.append(
                    b(
                        f"FUELBAR_StorefrontPane_{section_index}",
                        (width - 0.10, 0.075, head_z - sill_z),
                        (centre, front_y, (head_z + sill_z) / 2),
                        mats["glass"],
                        component="physical_low_e_storefront_pane",
                    )
                )
        for mullion_x in (x0,):
            objects.append(
                b(
                    f"FUELBAR_StorefrontMullion_{section_index}",
                    (0.095, 0.15, 3.58),
                    (mullion_x, front_y - 0.01, 2.35),
                    mats["black"],
                    component="thermally_broken_storefront_mullion",
                )
            )
    objects.append(
        b(
            "FUELBAR_StorefrontRightMullion",
            (0.095, 0.15, 3.58),
            (sections[-1][1], front_y - 0.01, 2.35),
            mats["black"],
            component="thermally_broken_storefront_mullion",
        )
    )
    for index, x in enumerate((-8.45, -5.90, -3.31, 3.31, 5.90, 8.45)):
        objects.append(
            b(
                f"FUELBAR_StorefrontTransom_{index}",
                (2.42, 0.15, 0.085),
                (x, front_y - 0.01, 3.46),
                mats["black"],
                component="storefront_transom",
            )
        )
    if occupied:
        objects.extend(add_store_interior(mats))
    return objects


def add_store_interior(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = [
        b(
            "FUELBAR_OccupiedDepthBackplane",
            (19.3, 0.10, 3.15),
            (0.0, 13.72, 2.34),
            mats["interior"],
            component="registered_occupied_store_depth",
        ),
        b(
            "FUELBAR_InteriorFloor",
            (19.2, 8.45, 0.08),
            (0.0, 9.15, 0.39),
            mats["concrete"],
            component="occupied_store_floor",
        ),
        b(
            "FUELBAR_InteriorCeiling",
            (19.2, 8.30, 0.10),
            (0.0, 9.15, 4.05),
            mats["white"],
            component="occupied_store_ceiling",
        ),
        b(
            "FUELBAR_WarmOccupiedRearBand",
            (18.8, 0.06, 0.52),
            (0.0, 13.27, 3.52),
            mats["interior_warm"],
            component="occupied_store_warm_rear_band",
        ),
    ]
    # Four gondolas, each with physical shelf plates and varied product blocks.
    for aisle_index, x in enumerate((-6.7, -2.3, 2.3, 6.7)):
        objects.append(
            b(
                f"FUELBAR_GondolaSpine_{aisle_index}",
                (1.15, 4.25, 1.38),
                (x, 9.45, 1.12),
                mats["charcoal"],
                0.04,
                component="occupied_store_gondola",
            )
        )
        for shelf_index, z in enumerate((0.68, 1.04, 1.40, 1.76)):
            objects.append(
                b(
                    f"FUELBAR_GondolaShelf_{aisle_index}_{shelf_index}",
                    (1.34, 4.38, 0.045),
                    (x, 9.45, z),
                    mats["stainless"],
                    component="occupied_store_shelf",
                )
            )
            for product_index in range(6):
                y = 7.75 + product_index * 0.58
                product_mat = (
                    mats["product_a"]
                    if (aisle_index + shelf_index + product_index) % 2
                    else mats["product_b"]
                )
                objects.append(
                    b(
                        f"FUELBAR_ProductBlock_{aisle_index}_{shelf_index}_{product_index}",
                        (0.42, 0.30, 0.22),
                        (x - 0.30 + 0.60 * (product_index % 2), y, z + 0.14),
                        product_mat,
                        0.018,
                        component="unbranded_product_depth",
                    )
                )
    # Cooler bank is built as recessed dark cabinets with physical shelves and
    # varied product depth.  Large emissive cards made the earlier pilot read
    # as a white wall; modeled merchandise keeps the glazing convincingly
    # occupied at both street and close-view distances.
    for cooler_index in range(8):
        x = -8.15 + cooler_index * 2.30
        objects.extend(
            [
                b(
                    f"FUELBAR_CoolerInterior_{cooler_index}",
                    (1.98, 0.18, 2.55),
                    (x, 13.53, 2.12),
                    mats["cooler_depth"],
                    component="occupied_cooler_depth",
                ),
                b(
                    f"FUELBAR_CoolerDoor_{cooler_index}",
                    (2.04, 0.075, 2.62),
                    (x, 13.37, 2.12),
                    mats["glass"],
                    component="physical_cooler_glass",
                ),
                b(
                    f"FUELBAR_CoolerLeftFrame_{cooler_index}",
                    (0.07, 0.14, 2.70),
                    (x - 1.04, 13.35, 2.12),
                    mats["black"],
                    component="cooler_frame",
                ),
            ]
        )
        for shelf_index, shelf_z in enumerate((1.12, 1.58, 2.04, 2.50, 2.96)):
            objects.append(
                b(
                    f"FUELBAR_CoolerShelf_{cooler_index}_{shelf_index}",
                    (1.78, 0.12, 0.035),
                    (x, 13.30, shelf_z),
                    mats["stainless"],
                    component="physical_cooler_shelf",
                )
            )
            for product_index in range(5):
                product_x = x - 0.68 + product_index * 0.34
                palette = (
                    mats["product_a"],
                    mats["product_b"],
                    mats["orange"],
                    mats["green"],
                    mats["red"],
                )
                objects.append(
                    b(
                        (
                            f"FUELBAR_CoolerProduct_{cooler_index}_"
                            f"{shelf_index}_{product_index}"
                        ),
                        (0.22, 0.12, 0.24 + 0.05 * ((product_index + shelf_index) % 2)),
                        (product_x, 13.20, shelf_z + 0.15),
                        palette[(cooler_index + shelf_index + product_index) % len(palette)],
                        0.018,
                        component="unbranded_cooler_merchandise",
                    )
                )
    objects.append(
        b(
            "FUELBAR_ServiceCounter",
            (4.2, 1.05, 1.05),
            (6.55, 6.15, 0.93),
            mats["timber"],
            0.06,
            component="occupied_store_counter",
        )
    )
    objects.append(
        b(
            "FUELBAR_ServiceCounterTop",
            (4.35, 1.15, 0.09),
            (6.55, 6.15, 1.49),
            mats["black"],
            0.035,
            component="occupied_store_counter",
        )
    )
    for row in range(2):
        for col in range(7):
            objects.append(
                b(
                    f"FUELBAR_InteriorLight_{row}_{col}",
                    (1.25, 0.10, 0.035),
                    (-7.5 + col * 2.5, 7.2 + row * 4.1, 3.98),
                    mats["cool_light"],
                    0.012,
                    component="occupied_store_ceiling_light",
                )
            )
    return objects


def add_store(
    mats: dict[str, bpy.types.Material],
    *,
    detailed: bool,
    schedule: str = "typical_a",
) -> list[bpy.types.Object]:
    centre_y = (STORE_FRONT_Y + STORE_REAR_Y) / 2
    objects: list[bpy.types.Object] = [
        b(
            "FUELBAR_StorePlinth",
            (STORE_WIDTH, STORE_DEPTH, 0.44),
            (0.0, centre_y, 0.44),
            mats["concrete"],
            0.04,
            component="store_plinth",
        ),
        b(
            "FUELBAR_LeftSideWall",
            (0.32, STORE_DEPTH, 3.85),
            (-11.84, centre_y, 2.48),
            mats["charcoal"],
            0.02,
            component="charcoal_service_envelope",
        ),
        b(
            "FUELBAR_RightSideWall",
            (0.32, STORE_DEPTH, 3.85),
            (11.84, centre_y, 2.48),
            mats["charcoal"],
            0.02,
            component="charcoal_service_envelope",
        ),
        b(
            "FUELBAR_RearServiceWall",
            (STORE_WIDTH, 0.32, 3.85),
            (0.0, STORE_REAR_Y - 0.16, 2.48),
            mats["charcoal"],
            0.02,
            component="charcoal_service_envelope",
        ),
        b(
            "FUELBAR_LeftBrickEntryPier",
            (2.15, 1.05, 4.22),
            (-10.80, STORE_FRONT_Y + 0.34, 2.56),
            mats["brick"],
            0.025,
            component="buff_brick_end_pier",
        ),
        b(
            "FUELBAR_RightBrickEntryPier",
            (2.15, 1.05, 4.88),
            (10.80, STORE_FRONT_Y + 0.34, 2.89),
            mats["brick"],
            0.025,
            component="buff_brick_sign_pier",
        ),
        b(
            "FUELBAR_StoreRoofSlab",
            (STORE_WIDTH, STORE_DEPTH, 0.24),
            (0.0, centre_y, 4.52),
            mats["roof"],
            0.035,
            component="store_roof_slab",
        ),
        b(
            "FUELBAR_StoreFrontParapet",
            (STORE_WIDTH, 0.42, 0.86),
            (0.0, STORE_FRONT_Y + 0.10, 4.88),
            mats["charcoal"],
            0.025,
            component="store_parapet",
        ),
        b(
            "FUELBAR_StoreRearParapet",
            (STORE_WIDTH, 0.36, 0.72),
            (0.0, STORE_REAR_Y - 0.18, 4.81),
            mats["charcoal"],
            component="store_parapet",
        ),
        b(
            "FUELBAR_StoreLeftParapet",
            (0.36, 9.65, 0.72),
            (-11.82, centre_y, 4.81),
            mats["charcoal"],
            component="store_parapet",
        ),
        b(
            "FUELBAR_StoreRightParapet",
            (0.36, 9.65, 0.72),
            (11.82, centre_y, 4.81),
            mats["charcoal"],
            component="store_parapet",
        ),
        b(
            "FUELBAR_BlankSignBlade",
            (0.58, 0.28, 3.42),
            (10.78, STORE_FRONT_Y - 0.24, 3.08),
            mats["black"],
            0.05,
            component="integrated_blank_sign_blade",
        ),
    ]
    objects.extend(
        add_storefront(
            mats,
            occupied=detailed,
            schedule=schedule,
        )
    )
    if detailed:
        objects.extend(add_store_roof_and_service(mats))
    return objects


def add_store_roof_and_service(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = [
        b(
            "FUELBAR_RoofMembraneField",
            (22.9, 8.8, 0.05),
            (0.0, 9.60, 4.67),
            mats["roof"],
            component="roof_membrane",
        ),
        b(
            "FUELBAR_RoofHatch",
            (1.0, 0.85, 0.18),
            (-7.8, 11.5, 4.80),
            mats["white"],
            0.04,
            component="roof_hatch",
        ),
    ]
    # Rooftop screen is slatted physical geometry around exactly two units.
    screen_centre_y = 10.1
    for side, x in enumerate((-5.5, 5.5)):
        for slat_index in range(7):
            z = 4.95 + slat_index * 0.14
            objects.append(
                b(
                    f"FUELBAR_RoofScreenFront_{side}_{slat_index}",
                    (10.2, 0.065, 0.065),
                    (0.0, screen_centre_y - 2.0, z),
                    mats["black"],
                    component="roof_louver_screen",
                )
            )
            objects.append(
                b(
                    f"FUELBAR_RoofScreenRear_{side}_{slat_index}",
                    (10.2, 0.065, 0.065),
                    (0.0, screen_centre_y + 2.0, z),
                    mats["black"],
                    component="roof_louver_screen",
                )
            )
        break
    for x in (-5.1, 5.1):
        for slat_index in range(7):
            z = 4.95 + slat_index * 0.14
            objects.append(
                b(
                    f"FUELBAR_RoofScreenSide_{x:+.1f}_{slat_index}",
                    (0.065, 4.0, 0.065),
                    (x, screen_centre_y, z),
                    mats["black"],
                    component="roof_louver_screen",
                )
            )
    for unit_index, x in enumerate((-2.7, 2.7)):
        objects.extend(
            [
                b(
                    f"FUELBAR_HVACUnit_{unit_index}",
                    (3.1, 2.15, 1.05),
                    (x, screen_centre_y, 5.22),
                    mats["white"],
                    0.07,
                    component="rooftop_hvac_unit",
                    count_authority="exactly_two_rooftop_hvac_units",
                ),
                c(
                    f"FUELBAR_HVACFan_{unit_index}",
                    0.62,
                    0.07,
                    (x, screen_centre_y, 5.78),
                    mats["black"],
                    vertices=28,
                    component="hvac_condenser_fan",
                ),
            ]
        )
        for grille_index in range(5):
            objects.append(
                b(
                    f"FUELBAR_HVACGrille_{unit_index}_{grille_index}",
                    (2.45, 0.04, 0.055),
                    (
                        x,
                        screen_centre_y - 1.09,
                        4.95 + grille_index * 0.16,
                    ),
                    mats["black"],
                    component="hvac_grille",
                )
            )
    # Rear service doors, condenser grilles and code-plausible utility gear.
    objects.extend(
        [
            b(
                "FUELBAR_RearDeliveryDoor",
                (2.35, 0.12, 2.75),
                (-5.5, STORE_REAR_Y - 0.34, 1.82),
                mats["black"],
                0.04,
                component="recessed_delivery_door",
            ),
            b(
                "FUELBAR_RearDeliveryCanopy",
                (3.1, 1.1, 0.14),
                (-5.5, STORE_REAR_Y - 0.72, 3.35),
                mats["charcoal"],
                0.03,
                component="rear_delivery_canopy",
            ),
            b(
                "FUELBAR_RearStaffDoor",
                (1.15, 0.12, 2.35),
                (5.6, STORE_REAR_Y - 0.34, 1.62),
                mats["glass"],
                0.03,
                component="glazed_staff_door",
            ),
        ]
    )
    for grille_index, x in enumerate((-1.8, 0.0, 1.8)):
        objects.append(
            b(
                f"FUELBAR_CoolerCondenserGrille_{grille_index}",
                (1.25, 0.10, 0.88),
                (x, STORE_REAR_Y - 0.35, 2.25),
                mats["black"],
                0.025,
                component="cooler_condenser_grille",
                count_authority="exactly_three_service_grilles",
            )
        )
        for louver in range(8):
            objects.append(
                b(
                    f"FUELBAR_CoolerLouver_{grille_index}_{louver}",
                    (1.08, 0.045, 0.035),
                    (
                        x,
                        STORE_REAR_Y - 0.41,
                        1.92 + louver * 0.095,
                    ),
                    mats["stainless"],
                    component="cooler_condenser_louver",
                )
            )
    # Right-side electrical and air/vacuum equipment.
    for box_index, (y, z) in enumerate(((8.8, 1.25), (10.3, 1.05), (11.5, 1.45))):
        objects.append(
            b(
                f"FUELBAR_ElectricalCabinet_{box_index}",
                (0.18, 0.85, 0.92),
                (12.05, y, z),
                mats["stainless"],
                0.035,
                component="electrical_meter_bank",
            )
        )
    objects.append(
        b(
            "FUELBAR_AirVacuumCabinet",
            (0.75, 0.70, 1.45),
            (13.35, 5.25, 0.99),
            mats["charcoal"],
            0.09,
            component="air_vacuum_unit",
        )
    )
    # Propane cage: physical mesh-like bar grid and five separate cylinders.
    cage_x, cage_y = 14.25, 8.65
    objects.append(
        b(
            "FUELBAR_PropaneCageBase",
            (3.1, 2.5, 0.12),
            (cage_x, cage_y, 0.34),
            mats["concrete"],
            component="propane_cage",
        )
    )
    for post_index, (dx, dy) in enumerate(
        ((-1.45, -1.12), (1.45, -1.12), (-1.45, 1.12), (1.45, 1.12))
    ):
        objects.append(
            c(
                f"FUELBAR_PropaneCagePost_{post_index}",
                0.045,
                2.2,
                (cage_x + dx, cage_y + dy, 1.48),
                mats["stainless"],
                vertices=12,
                component="propane_cage",
            )
        )
    for bar_index in range(7):
        x = cage_x - 1.35 + bar_index * 0.45
        objects.extend(
            [
                b(
                    f"FUELBAR_PropaneCageFrontBar_{bar_index}",
                    (0.035, 0.035, 2.12),
                    (x, cage_y - 1.13, 1.48),
                    mats["stainless"],
                    component="propane_cage",
                ),
                b(
                    f"FUELBAR_PropaneCageRearBar_{bar_index}",
                    (0.035, 0.035, 2.12),
                    (x, cage_y + 1.13, 1.48),
                    mats["stainless"],
                    component="propane_cage",
                ),
            ]
        )
    for bar_index in range(6):
        y = cage_y - 1.0 + bar_index * 0.4
        objects.extend(
            [
                b(
                    f"FUELBAR_PropaneCageLeftBar_{bar_index}",
                    (0.035, 0.035, 2.12),
                    (cage_x - 1.46, y, 1.48),
                    mats["stainless"],
                    component="propane_cage",
                ),
                b(
                    f"FUELBAR_PropaneCageRightBar_{bar_index}",
                    (0.035, 0.035, 2.12),
                    (cage_x + 1.46, y, 1.48),
                    mats["stainless"],
                    component="propane_cage",
                ),
            ]
        )
    for tank_index in range(5):
        x = cage_x - 1.0 + tank_index * 0.50
        objects.extend(
            [
                c(
                    f"FUELBAR_PropaneTank_{tank_index}",
                    0.18,
                    0.82,
                    (x, cage_y, 0.80),
                    mats["propane"],
                    vertices=20,
                    component="propane_tank",
                ),
                c(
                    f"FUELBAR_PropaneTankCap_{tank_index}",
                    0.10,
                    0.12,
                    (x, cage_y, 1.27),
                    mats["black"],
                    vertices=16,
                    component="propane_tank",
                ),
            ]
        )
    # Screened refuse point at the rear-right edge.
    objects.extend(
        [
            b(
                "FUELBAR_DumpsterBody",
                (2.45, 1.35, 1.25),
                (14.5, 12.7, 0.94),
                mats["charcoal"],
                0.08,
                component="screened_refuse_point",
            ),
            b(
                "FUELBAR_DumpsterLid",
                (2.50, 1.38, 0.12),
                (14.5, 12.7, 1.62),
                mats["black"],
                0.04,
                component="screened_refuse_point",
            ),
        ]
    )
    return objects


def add_canopy(
    mats: dict[str, bpy.types.Material],
    *,
    detailed: bool,
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    # Six columns are the structural authority: two rows of three.
    for row_index, y in enumerate((-10.55, -0.45)):
        for col_index, x in enumerate((-12.0, 0.0, 12.0)):
            index = row_index * 3 + col_index
            objects.extend(
                [
                    b(
                        f"FUELBAR_CanopyColumn_{index:02d}",
                        (0.34, 0.34, 5.00),
                        (x, y, 2.82),
                        mats["charcoal"],
                        0.035,
                        component="canopy_structural_column",
                        count_authority="exactly_six_canopy_columns",
                    ),
                    b(
                        f"FUELBAR_CanopyColumnBasePlate_{index:02d}",
                        (0.64, 0.64, 0.08),
                        (x, y, 0.34),
                        mats["stainless"],
                        0.035,
                        component="canopy_column_baseplate",
                    ),
                ]
            )
            for bolt_index, (dx, dy) in enumerate(
                ((-0.22, -0.22), (0.22, -0.22), (-0.22, 0.22), (0.22, 0.22))
            ):
                objects.append(
                    c(
                        f"FUELBAR_ColumnBolt_{index}_{bolt_index}",
                        0.035,
                        0.055,
                        (x + dx, y + dy, 0.405),
                        mats["black"],
                        vertices=10,
                        component="canopy_column_baseplate",
                    )
                )
    objects.extend(
        [
            b(
                "FUELBAR_CanopyRoofAssembly",
                (CANOPY_WIDTH, CANOPY_DEPTH, 0.35),
                (0.0, CANOPY_CENTRE_Y, 5.70),
                mats["white"],
                0.035,
                component="thin_flat_canopy_roof",
            ),
            b(
                "FUELBAR_CanopySoffit",
                (27.55, 13.55, 0.12),
                (0.0, CANOPY_CENTRE_Y, CANOPY_UNDERSIDE_Z),
                mats["timber"],
                component="honey_linear_canopy_soffit",
            ),
            b(
                "FUELBAR_CanopyFrontFascia",
                (CANOPY_WIDTH, 0.34, 0.68),
                (0.0, CANOPY_CENTRE_Y - 6.83, 5.69),
                mats["white"],
                0.02,
                component="white_canopy_fascia",
            ),
            b(
                "FUELBAR_CanopyRearFascia",
                (CANOPY_WIDTH, 0.34, 0.68),
                (0.0, CANOPY_CENTRE_Y + 6.83, 5.69),
                mats["white"],
                0.02,
                component="white_canopy_fascia",
            ),
            b(
                "FUELBAR_CanopyLeftFascia",
                (0.34, CANOPY_DEPTH - 0.34, 0.68),
                (-13.83, CANOPY_CENTRE_Y, 5.69),
                mats["white"],
                0.02,
                component="white_canopy_fascia",
            ),
            b(
                "FUELBAR_CanopyRightFascia",
                (0.34, CANOPY_DEPTH - 0.34, 0.68),
                (13.83, CANOPY_CENTRE_Y, 5.69),
                mats["white"],
                0.02,
                component="white_canopy_fascia",
            ),
        ]
    )
    # One and only one orange identity stripe runs continuously around.
    for name, size, loc in (
        (
            "Front",
            (CANOPY_WIDTH + 0.02, 0.37, 0.17),
            (0.0, CANOPY_CENTRE_Y - 7.02, 5.70),
        ),
        (
            "Rear",
            (CANOPY_WIDTH + 0.02, 0.37, 0.17),
            (0.0, CANOPY_CENTRE_Y + 7.02, 5.70),
        ),
        (
            "Left",
            (0.37, CANOPY_DEPTH - 0.30, 0.17),
            (-14.02, CANOPY_CENTRE_Y, 5.70),
        ),
        (
            "Right",
            (0.37, CANOPY_DEPTH - 0.30, 0.17),
            (14.02, CANOPY_CENTRE_Y, 5.70),
        ),
    ):
        objects.append(
            b(
                f"FUELBAR_CanopyOrangeBand_{name}",
                size,
                loc,
                mats["orange"],
                0.012,
                component="single_continuous_orange_identity_band",
            )
        )
    if not detailed:
        return objects
    # Subtle top seams and four real drain bodies keep the aerial view legible
    # without projecting a photographed construction junction over the roof.
    for seam_index, x in enumerate((-9.3, -4.65, 0.0, 4.65, 9.3)):
        objects.append(
            b(
                f"FUELBAR_CanopyTopSeam_{seam_index}",
                (0.022, 13.55, 0.018),
                (x, CANOPY_CENTRE_Y, 5.889),
                mats["stainless"],
                component="canopy_roof_panel_seam",
            )
        )
    for drain_index, (x, y) in enumerate(
        ((-10.5, -10.0), (10.5, -10.0), (-10.5, -1.0), (10.5, -1.0))
    ):
        objects.append(
            c(
                f"FUELBAR_CanopyRoofDrain_{drain_index}",
                0.15,
                0.055,
                (x, y, 5.915),
                mats["black"],
                vertices=24,
                component="canopy_roof_drain",
                count_authority="exactly_four_canopy_roof_drains",
            )
        )
    # Physical soffit shadow seams, downlights, gutters and downpipes.
    for seam_index in range(31):
        x = -13.3 + seam_index * 0.887
        objects.append(
            b(
                f"FUELBAR_SoffitShadowJoint_{seam_index:02d}",
                (0.026, 13.25, 0.028),
                (x, CANOPY_CENTRE_Y, 5.278),
                mats["black"],
                component="soffit_shadow_joint",
            )
        )
    for row_index, y in enumerate((-9.65, -5.50, -1.35)):
        for col_index, x in enumerate((-10.4, -5.2, 0.0, 5.2, 10.4)):
            objects.append(
                c(
                    f"FUELBAR_CanopyDownlight_{row_index}_{col_index}",
                    0.15,
                    0.045,
                    (x, y, 5.255),
                    mats["warm_light"],
                    vertices=24,
                    component="recessed_canopy_downlight",
                )
            )
    for side_index, x in enumerate((-13.55, 13.55)):
        objects.append(
            b(
                f"FUELBAR_CanopyGutter_{side_index}",
                (0.18, 13.35, 0.17),
                (x, CANOPY_CENTRE_Y, 5.31),
                mats["black"],
                0.03,
                component="canopy_gutter",
            )
        )
        for pipe_index, y in enumerate((-10.55, -0.45)):
            objects.extend(
                [
                    c(
                        f"FUELBAR_Downpipe_{side_index}_{pipe_index}",
                        0.075,
                        4.60,
                        (x, y, 2.72),
                        mats["black"],
                        vertices=16,
                        component="canopy_downpipe",
                    ),
                    tube_curve(
                        f"FUELBAR_DownpipeOffset_{side_index}_{pipe_index}",
                        [
                            (x, y, 5.03),
                            (x, y, 5.23),
                            (x + (-0.25 if x < 0 else 0.25), y, 5.36),
                        ],
                        0.075,
                        mats["black"],
                        component="canopy_downpipe",
                    ),
                ]
            )
    return objects


def add_pump_island(
    index: int,
    x: float,
    mats: dict[str, bpy.types.Material],
    *,
    detailed: bool,
) -> list[bpy.types.Object]:
    y = CANOPY_CENTRE_Y
    objects: list[bpy.types.Object] = [
        b(
            f"FUELBAR_PumpIsland_{index}",
            (1.72, 4.55, 0.20),
            (x, y, 0.34),
            mats["concrete"],
            0.18,
            component="raised_pump_island",
            count_authority="exactly_three_separate_pump_islands",
        ),
        b(
            f"FUELBAR_PumpDispenser_{index}",
            (1.02, 0.74, 2.22),
            (x, y, 1.55),
            mats["white"],
            0.09,
            component="double_sided_pump_dispenser",
            count_authority="exactly_three_double_sided_dispensers",
        ),
        b(
            f"FUELBAR_PumpOrangeCap_{index}",
            (1.18, 0.87, 0.34),
            (x, y, 2.77),
            mats["pump_orange"],
            0.055,
            component="pump_identity_cap",
        ),
        b(
            f"FUELBAR_PumpOrangeBase_{index}",
            (1.16, 0.88, 0.34),
            (x, y, 0.62),
            mats["pump_orange"],
            0.045,
            component="pump_identity_base",
        ),
        b(
            f"FUELBAR_PumpLeftBlackSpine_{index}",
            (0.10, 0.76, 1.62),
            (x - 0.47, y, 1.62),
            mats["pump"],
            0.025,
            component="pump_powder_coat_spine",
        ),
        b(
            f"FUELBAR_PumpRightBlackSpine_{index}",
            (0.10, 0.76, 1.62),
            (x + 0.47, y, 1.62),
            mats["pump"],
            0.025,
            component="pump_powder_coat_spine",
        ),
    ]
    for face_index, face_y in enumerate((y - 0.39, y + 0.39)):
        face_direction = -1.0 if face_index == 0 else 1.0
        detail_y = face_y + face_direction * 0.045
        objects.extend(
            [
                b(
                    f"FUELBAR_PumpFacePanel_{index}_{face_index}",
                    (0.80, 0.038, 1.34),
                    (x, face_y, 1.78),
                    mats["pump"],
                    0.035,
                    component="pump_service_face",
                ),
                b(
                    f"FUELBAR_PumpDisplay_{index}_{face_index}",
                    (0.61, 0.045, 0.38),
                    (x, detail_y, 2.16),
                    mats["pump_screen"],
                    0.025,
                    component="recessed_pump_display",
                ),
                b(
                    f"FUELBAR_PumpReader_{index}_{face_index}",
                    (0.30, 0.045, 0.20),
                    (x + 0.18, detail_y, 1.70),
                    mats["stainless"],
                    0.02,
                    component="unbranded_card_reader_shape",
                ),
                b(
                    f"FUELBAR_PumpReceiptSlot_{index}_{face_index}",
                    (0.23, 0.048, 0.055),
                    (x - 0.21, detail_y, 1.73),
                    mats["black"],
                    0.012,
                    component="pump_receipt_slot",
                ),
                b(
                    f"FUELBAR_PumpLowerPanel_{index}_{face_index}",
                    (0.72, 0.035, 0.50),
                    (x, detail_y, 1.20),
                    mats["white"],
                    0.018,
                    component="pump_meter_panel",
                ),
            ]
        )
        for key_index in range(9):
            key_col = key_index % 3
            key_row = key_index // 3
            objects.append(
                b(
                    f"FUELBAR_PumpKey_{index}_{face_index}_{key_index}",
                    (0.045, 0.025, 0.035),
                    (
                        x + 0.12 + key_col * 0.055,
                        detail_y + face_direction * 0.014,
                        1.62 + key_row * 0.052,
                    ),
                    mats["black"],
                    0.006,
                    component="pump_keypad",
                )
            )
        for cradle_index, cradle_x in enumerate((x - 0.34, x + 0.34)):
            objects.append(
                b(
                    f"FUELBAR_PumpNozzleCradle_{index}_{face_index}_{cradle_index}",
                    (0.105, 0.050, 0.28),
                    (cradle_x, detail_y, 1.38),
                    mats["black"],
                    0.018,
                    component="recessed_nozzle_cradle",
                )
            )
    for bollard_index, (dx, dy) in enumerate(
        ((-0.92, -1.55), (0.92, -1.55), (-0.92, 1.55), (0.92, 1.55))
    ):
        objects.append(
            c(
                f"FUELBAR_PumpBollard_{index}_{bollard_index}",
                0.095,
                0.92,
                (x + dx, y + dy, 0.84),
                mats["stainless"],
                vertices=20,
                component="stainless_pump_bollard",
            )
        )
    objects.extend(
        [
            b(
                f"FUELBAR_WasteBin_{index}",
                (0.48, 0.48, 0.92),
                (x - 1.08, y + 0.55, 0.80),
                mats["charcoal"],
                0.09,
                component="pump_waste_bin",
            ),
            c(
                f"FUELBAR_SqueegeePole_{index}",
                0.025,
                0.95,
                (x - 1.16, y - 0.45, 0.92),
                mats["stainless"],
                vertices=10,
                component="squeegee_station",
            ),
        ]
    )
    if not detailed:
        return objects
    # Two hose loops and nozzles on each side of every dispenser.
    for side_index, side_x in enumerate((x - 0.58, x + 0.58)):
        nozzle_mat = mats["green"] if side_index == 0 else mats["red"]
        for face_index, direction in enumerate((-1.0, 1.0)):
            face_y = y + direction * 0.28
            objects.append(
                tube_curve(
                    f"FUELBAR_Hose_{index}_{side_index}_{face_index}",
                    [
                        (side_x, face_y, 2.42),
                        (side_x + (-0.16 if side_index == 0 else 0.16), face_y, 1.85),
                        (side_x + (-0.23 if side_index == 0 else 0.23), face_y, 0.74),
                        (side_x, face_y, 1.18),
                    ],
                    0.035,
                    mats["black"],
                    component="physical_fuel_hose",
                )
            )
            objects.extend(
                [
                    b(
                        f"FUELBAR_NozzleBody_{index}_{side_index}_{face_index}",
                        (0.12, 0.10, 0.42),
                        (side_x, face_y, 1.34),
                        nozzle_mat,
                        0.025,
                        component="fuel_nozzle",
                    ),
                    b(
                        f"FUELBAR_NozzleSpout_{index}_{side_index}_{face_index}",
                        (0.035, 0.08, 0.28),
                        (
                            side_x,
                            face_y + direction * 0.08,
                            1.58,
                        ),
                        mats["stainless"],
                        component="fuel_nozzle",
                    ),
                ]
            )
    return objects


def add_pumps(
    mats: dict[str, bpy.types.Material],
    *,
    detailed: bool,
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    for index, x in enumerate((-8.0, 0.0, 8.0)):
        objects.extend(add_pump_island(index, x, mats, detailed=detailed))
    return objects


def add_price_pylon(
    mats: dict[str, bpy.types.Material],
    *,
    detailed: bool,
) -> list[bpy.types.Object]:
    x, y = -15.25, -10.65
    objects: list[bpy.types.Object] = [
        b(
            "FUELBAR_PylonBase",
            (2.45, 1.10, 0.30),
            (x, y, 0.39),
            mats["concrete"],
            0.10,
            component="roadside_price_pylon",
        )
    ]
    for leg_index, dx in enumerate((-0.78, 0.78)):
        objects.append(
            b(
                f"FUELBAR_PylonLeg_{leg_index}",
                (0.18, 0.24, 8.45),
                (x + dx, y, 4.62),
                mats["black"],
                0.035,
                component="roadside_price_pylon",
            )
        )
    panels = [
        ("TopBlank", 8.50, 1.15, mats["black"]),
        ("OrangeBand", 7.52, 0.48, mats["orange"]),
        ("WhiteBand", 6.95, 0.42, mats["white"]),
        ("PriceBlankA", 6.12, 0.92, mats["black"]),
        ("PriceBlankB", 5.16, 0.80, mats["black"]),
        ("PriceBlankC", 4.32, 0.72, mats["black"]),
    ]
    for panel_name, z, height, mat in panels:
        objects.append(
            b(
                f"FUELBAR_Pylon{panel_name}",
                (1.85, 0.30, height),
                (x, y, z),
                mat,
                0.035,
                component="blank_internally_lit_pylon_panel",
            )
        )
    objects.append(
        b(
            "FUELBAR_PylonTopCap",
            (1.98, 0.38, 0.36),
            (x, y, 9.30),
            mats["black"],
            0.045,
            component="roadside_price_pylon",
        )
    )
    return objects


def build_assembled(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    objects.extend(add_forecourt(mats, detailed=True))
    objects.extend(add_store(mats, detailed=True))
    objects.extend(add_canopy(mats, detailed=True))
    objects.extend(add_pumps(mats, detailed=True))
    objects.extend(add_price_pylon(mats, detailed=True))
    return objects


def build_module(
    role: str,
    variant: str,
    mats: dict[str, bpy.types.Material],
) -> tuple[list[bpy.types.Object], float]:
    objects: list[bpy.types.Object] = []
    if role == "podium":
        height = PODIUM_HEIGHT
        objects.extend(add_forecourt(mats, detailed=False))
        objects.extend(
            [
                b(
                    "FUELBARKIT_StorePlinth",
                    (STORE_WIDTH, STORE_DEPTH, 0.44),
                    (0.0, 9.5, 0.22),
                    mats["concrete"],
                    component="store_plinth",
                )
            ]
        )
        for index, x in enumerate((-8.0, 0.0, 8.0)):
            objects.append(
                b(
                    f"FUELBARKIT_PumpIsland_{index}",
                    (1.72, 4.55, 0.20),
                    (x, CANOPY_CENTRE_Y, 0.34),
                    mats["concrete"],
                    0.18,
                    component="raised_pump_island",
                )
            )
    elif role == "floor":
        height = FLOOR_HEIGHT
        objects.extend(
            add_store(
                mats,
                detailed=False,
                schedule=variant,
            )
        )
        # Keep only occupied-envelope elements inside the floor module's
        # vertical band; the canopy remains fixed crown/roof semantics.
        for obj in objects:
            obj.location.z -= PODIUM_HEIGHT
    elif role == "crown":
        height = CROWN_HEIGHT
        # The flexible crown carries only the canopy head and store parapet.
        # Full-height canopy columns belong to the fixed assembled landmark;
        # including them here broke the one-metre vertical module contract.
        objects.extend(
            [
                b(
                    "FUELBARKIT_StoreCrown",
                    (STORE_WIDTH, STORE_DEPTH, 0.78),
                    (0.0, 9.5, 0.39),
                    mats["charcoal"],
                    component="store_parapet",
                ),
                b(
                    "FUELBARKIT_CanopyCrownRoof",
                    (CANOPY_WIDTH, CANOPY_DEPTH, 0.35),
                    (0.0, CANOPY_CENTRE_Y, 0.825),
                    mats["white"],
                    0.025,
                    component="thin_flat_canopy_roof",
                ),
                b(
                    "FUELBARKIT_CanopyCrownSoffit",
                    (27.55, 13.55, 0.12),
                    (0.0, CANOPY_CENTRE_Y, 0.59),
                    mats["timber"],
                    component="honey_linear_canopy_soffit",
                ),
                b(
                    "FUELBARKIT_CanopyCrownFrontFascia",
                    (CANOPY_WIDTH, 0.34, 0.68),
                    (0.0, CANOPY_CENTRE_Y - 6.83, 0.66),
                    mats["white"],
                    0.018,
                    component="white_canopy_fascia",
                ),
                b(
                    "FUELBARKIT_CanopyCrownRearFascia",
                    (CANOPY_WIDTH, 0.34, 0.68),
                    (0.0, CANOPY_CENTRE_Y + 6.83, 0.66),
                    mats["white"],
                    0.018,
                    component="white_canopy_fascia",
                ),
                b(
                    "FUELBARKIT_CanopyCrownOrangeBand",
                    (CANOPY_WIDTH + 0.02, 0.37, 0.17),
                    (0.0, CANOPY_CENTRE_Y - 7.02, 0.66),
                    mats["orange"],
                    0.010,
                    component="single_continuous_orange_identity_band",
                ),
            ]
        )
    elif role == "roof":
        height = ROOF_HEIGHT
        objects.extend(
            [
                b(
                    "FUELBARKIT_CanopyRoof",
                    (CANOPY_WIDTH, CANOPY_DEPTH, 0.35),
                    (0.0, CANOPY_CENTRE_Y, 0.18),
                    mats["white"],
                    0.035,
                    component="thin_flat_canopy_roof",
                ),
                b(
                    "FUELBARKIT_StoreRoof",
                    (STORE_WIDTH, STORE_DEPTH, 0.24),
                    (0.0, 9.5, 0.12),
                    mats["roof"],
                    0.035,
                    component="store_roof_slab",
                ),
            ]
        )
    else:
        raise ValueError(role)
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
        count += sum(max(1, len(poly.vertices) - 2) for poly in mesh.polygons)
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
        if obj.type == "MESH"
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
        "assembly_class": "repeatable_middle" if repeatable else "fixed_semantic",
        "fixed_semantic": not repeatable,
        "lod": 0,
        "allowed_levels": [0] if role in {"podium", "floor", "crown", "roof"} else [],
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
    road = material(
        "MAT_W10_FUELBAR_PresentationRoad",
        (0.055, 0.060, 0.064, 1.0),
        0.88,
    )
    soil = material(
        "MAT_W10_FUELBAR_PresentationSoil",
        (0.10, 0.075, 0.040, 1.0),
        0.94,
    )
    apron = material(
        "MAT_W10_FUELBAR_PresentationConcreteApron",
        (0.31, 0.33, 0.34, 1.0),
        0.86,
    )
    context: list[bpy.types.Object] = [
        box(
            "PRESENTATION_FuelBarGround",
            (85.0, 72.0, 0.16),
            (0.0, 0.0, -0.16),
            mats["prairie"],
            0.03,
        ),
        box(
            "PRESENTATION_FuelBarRoad",
            (85.0, 10.0, 0.18),
            (0.0, -35.5, -0.02),
            road,
            0.02,
        ),
        box(
            "PRESENTATION_FuelBarConcreteApron",
            (50.0, 17.0, 0.12),
            (0.0, -22.0, -0.01),
            apron,
            0.02,
        ),
        box(
            "PRESENTATION_FuelBarBioswale",
            (40.0, 3.6, 0.13),
            (0.0, 18.2, -0.01),
            soil,
            0.04,
        ),
    ]
    for line_index, x in enumerate((-8.0, 8.0)):
        context.append(
            box(
                f"PRESENTATION_RoadLine_{line_index}",
                (0.14, 10.0, 0.025),
                (x, -35.5, 0.09),
                mats["marking"],
            )
        )
    for joint_index, x in enumerate((-16.0, -8.0, 0.0, 8.0, 16.0)):
        context.append(
            box(
                f"PRESENTATION_ApronLongJoint_{joint_index}",
                (0.035, 17.0, 0.012),
                (x, -22.0, 0.065),
                mats["black"],
            )
        )
    for joint_index, y in enumerate((-18.0, -22.0, -26.0)):
        context.append(
            box(
                f"PRESENTATION_ApronCrossJoint_{joint_index}",
                (50.0, 0.035, 0.012),
                (0.0, y, 0.065),
                mats["black"],
            )
        )
    for index in range(48):
        x = -38.0 + index * 1.62
        y = 18.2 + 0.62 * math.sin(index * 1.47)
        height = 0.55 + 0.32 * ((index * 7) % 5) / 4
        context.append(
            c(
                f"PRESENTATION_PrairieGrass_{index:02d}",
                0.06,
                height,
                (x, y, height / 2),
                mats["prairie"],
                vertices=8,
                component="presentation_only",
            )
        )
    # Sparse native planting at the road edge gives the clean forecourt a
    # believable prairie threshold without hiding the drainage/site geometry.
    for side_index, side in enumerate((-1.0, 1.0)):
        for plant_index in range(18):
            x = side * (18.2 + plant_index * 0.92)
            y = -17.9 + 0.55 * math.sin(plant_index * 1.31 + side_index)
            height = 0.34 + 0.24 * ((plant_index * 5 + side_index) % 6) / 5
            context.append(
                c(
                    f"PRESENTATION_ForegroundGrass_{side_index}_{plant_index:02d}",
                    0.055 + 0.012 * (plant_index % 3),
                    height,
                    (x, y, height / 2),
                    mats["prairie"],
                    vertices=7,
                    component="presentation_only",
                )
            )
    return context


def configure_render() -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 920
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.exposure = 0.30
    scene.eevee.taa_render_samples = 96
    scene.eevee.use_raytracing = True
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
    background.inputs["Strength"].default_value = 0.72
    coordinates = nodes.new("ShaderNodeTexCoord")
    separate = nodes.new("ShaderNodeSeparateXYZ")
    gradient = nodes.new("ShaderNodeValToRGB")
    gradient.color_ramp.elements[0].position = 0.0
    gradient.color_ramp.elements[0].color = (0.50, 0.69, 0.92, 1.0)
    gradient.color_ramp.elements[1].position = 0.68
    gradient.color_ramp.elements[1].color = (0.11, 0.30, 0.62, 1.0)
    links.new(coordinates.outputs["Normal"], separate.inputs["Vector"])
    links.new(separate.outputs["Z"], gradient.inputs["Fac"])
    links.new(gradient.outputs["Color"], background.inputs["Color"])
    links.new(background.outputs["Background"], output.inputs["Surface"])
    bpy.ops.object.light_add(type="SUN", location=(-45, -60, 80))
    sun = bpy.context.object
    sun.name = "PRESENTATION_FuelBarSun"
    sun.data.energy = 2.5
    sun.data.color = (1.0, 0.84, 0.67)
    sun.data.angle = math.radians(5.0)
    sun.rotation_euler = (
        Vector((0.0, 0.0, 3.0)) - sun.location
    ).to_track_quat("-Z", "Y").to_euler()
    bpy.ops.object.light_add(type="AREA", location=(0.0, -28.0, 11.0))
    fill = bpy.context.object
    fill.name = "PRESENTATION_FuelBarFacadeFill"
    fill.data.energy = 1350.0
    fill.data.shape = "RECTANGLE"
    fill.data.size = 28.0
    fill.data.size_y = 9.0
    fill.rotation_euler = (
        Vector((0.0, 2.0, 3.0)) - fill.location
    ).to_track_quat("-Z", "Y").to_euler()
    bpy.ops.object.light_add(type="AREA", location=(0.0, 1.2, 3.2))
    interior = bpy.context.object
    interior.name = "PRESENTATION_FuelBarStoreFill"
    interior.data.energy = 180.0
    interior.data.color = (1.0, 0.57, 0.26)
    interior.data.shape = "RECTANGLE"
    interior.data.size = 18.0
    interior.data.size_y = 3.0
    interior.rotation_euler = (
        Vector((0.0, 10.0, 2.2)) - interior.location
    ).to_track_quat("-Z", "Y").to_euler()


def render_views(
    folder: Path,
    mats: dict[str, bpy.types.Material],
    *,
    view_set: str,
) -> list[str]:
    context = add_presentation_context(mats)
    configure_render()
    views = {
        "preview": ((10.0, -52.0, 5.5), (-2.8, 0.0, 2.25), 48),
        "street": ((4.0, -48.0, 4.8), (0.0, 0.0, 3.0), 55),
        "front_corner_oblique": ((-34.0, -46.0, 12.0), (0.0, 0.0, 3.1), 58),
        "rear_corner_oblique": ((34.0, 37.0, 14.0), (0.0, 6.0, 3.0), 58),
        "aerial": ((-38.0, -38.0, 39.0), (0.0, 0.0, 2.0), 56),
        "storefront_close": ((6.2, -17.0, 4.0), (2.0, 6.6, 2.15), 65),
        "facade_close": ((3.5, -21.0, 4.4), (0.0, 6.0, 2.25), 62),
        "entry_close": ((8.0, -17.0, 4.5), (0.0, 5.4, 2.2), 66),
        "pump_close": ((-5.4, -13.8, 3.0), (-8.0, -5.9, 1.62), 72),
        "canopy_close": ((20.0, -21.0, 10.5), (5.0, -5.5, 5.2), 64),
        "service_close": ((28.0, 26.0, 7.0), (9.0, 10.0, 2.4), 62),
        "roof_close": ((-27.0, -12.0, 25.0), (0.0, 4.0, 4.4), 62),
        "pylon_close": ((-29.0, -25.0, 8.0), (-15.2, -10.6, 4.8), 66),
        "context": ((50.0, -53.0, 27.0), (0.0, 0.0, 2.8), 57),
    }
    pilot = {
        "preview",
        "front_corner_oblique",
        "aerial",
        "storefront_close",
        "pump_close",
        "service_close",
        "roof_close",
    }
    if view_set == "preview":
        selected = {"preview"}
    elif view_set == "pilot":
        selected = pilot
    else:
        selected = set(views)
    renders: list[str] = []
    for role, (location, target, lens) in views.items():
        if role not in selected:
            continue
        aim_camera(location, target, lens)
        scene = bpy.context.scene
        scene.render.filepath = str(folder / f"{FAMILY}_{role}.png")
        bpy.ops.render.render(write_still=True)
        renders.append(f"{FAMILY}_{role}.png")
    delete_objects(context)
    return renders


def footprint_contract() -> dict:
    rectangle = {
        "recommendedWidth_m": [27.3, 42.7],
        "recommendedDepth_m": [23.4, 36.6],
        "recommendedFloors": [1, 1],
        "scaleMin": 0.78,
        "scaleMax": 1.22,
        "maxAxisRatio": 1.20,
        "preferredBayMultiple_m": 4.0,
    }
    return {
        "preferredProfiles": ["rectangle"],
        "minimumPreferredProfiles": 1,
        "profileRationale": (
            "The store, six-column canopy, exactly three pump islands and "
            "roadside pylon operate as one fixed site. Mildly imperfect "
            "hand-drawn rectangles scale cleanly; larger sites repeat a "
            "complete station rather than stretching pump clearances."
        ),
        "fixedLandmarkScaleBand": {
            "scaleMin": 0.78,
            "scaleMax": 1.22,
            "maxAxisRatio": 1.20,
        },
        "preferredBayMultiple_m": 4.0,
        **rectangle,
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
            "roadside_pylon",
            "six_column_canopy",
            "three_pump_islands",
            "store_entry_and_sign_pier",
        ],
        "repeatable_middle_bays": [1, 2, 3],
        "middle_variants": ["typical_a", "typical_b", "typical_c"],
        "rule": (
            "The assembled station always preserves all three islands, all "
            "six canopy columns, one pylon and one occupied store. Only the "
            "out-of-band fallback kit repeats complete four-metre facade bays."
        ),
    }
    contract["assembly_contract"] = {
        "fixed": [
            "complete forecourt and drainage",
            "corner returns",
            "six-column canopy",
            "exactly three pump islands",
            "automatic public entrance",
            "podium/entrance",
            "roadside pylon",
            "propane and service yard",
            "crown",
            "roof",
            "store crown and roof plant",
        ],
        "repeatable": ["typical_a", "typical_b", "typical_c"],
        "side_elevations": (
            "The occupied front curtain wall turns into buff-brick end piers "
            "and a charcoal micro-ribbed service envelope with real doors, "
            "grilles, utilities, propane cage and roof drainage."
        ),
        "elevation_coverage": {
            "front": "six-column canopy, three pumps, occupied storefront and pylon",
            "left": "brick return, charcoal service wall and canopy drainage",
            "right": "sign pier, propane cage, air/vacuum and service utilities",
            "rear": "delivery/staff doors, cooler grilles and screened refuse",
            "roof": "canopy fall/drains, membrane store roof, two HVAC units and screen",
        },
        "variation_policy": (
            "Scale the complete fixed site only inside 0.78–1.22 with an "
            "independent-axis ratio no greater than 1.20. Larger targets use "
            "streetwall repeat, never family_incompatible."
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
        else render_views(folder, mats, view_set=view_set)
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
        "silhouette": "low_store_and_broad_detached_flat_canopy",
        "canopy_structural_columns": 6,
        "pump_islands": 3,
        "double_sided_pump_dispensers": 3,
        "occupied_storefront_bays": 7,
        "automatic_entry_door_leaves": 2,
        "roadside_price_pylons": 1,
        "rooftop_hvac_units": 2,
        "propane_cages": 1,
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
                    "id": "complete_fuel_bar_site",
                    "centre_x_m": 0.0,
                    "centre_y_m": 0.0,
                    "length_m": NATIVE_WIDTH,
                    "thickness_m": NATIVE_DEPTH,
                    "rotation_degrees": 0.0,
                }
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
            "name": "archetype_compiler/generate_wave10_gas_station_family.py",
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
        "aesthetic_category_id": "roadside_commercial",
        "development_type": "commercial_retail",
        "reuse_keys": [
            *ALIASES,
            "gas station",
            "fuel station",
            "convenience store",
            "roadside commercial",
        ],
        "generation_tags": [
            "wave10",
            "fixed_landmark",
            "modern_fuel_bar",
            "physical_pump_equipment",
            "occupied_retail_storefront",
            "prairie_roadside",
        ],
        "footprint_compatibility": footprint,
        "coordinate_contract": COORDINATE_CONTRACT,
        "textures": texture_inventory(skin),
        "facade_sheet": facade_sheet_contract(skin),
        "massing_graph": massing_graph,
        "material_budget": {
            "max_assembled_materials": 26,
            "rationale": (
                "Brick, charcoal metal, white canopy aluminium, orange band, "
                "timber soffit, concrete, physical glazing, occupied depth, "
                "pump body, display glass, identity powder coat, stainless "
                "protection and site markings remain separate because their "
                "real material response is the identity."
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
            "A thin white-and-burnt-orange six-column canopy shelters exactly "
            "three physical pump islands in front of an occupied buff-brick, "
            "charcoal-metal and honey-soffit prairie convenience store."
        ),
        "material_zones": (
            "warm buff modular brick and pale honed concrete plinth; charcoal "
            "micro-ribbed metal and black thermal-break frames; satin white "
            "canopy aluminium with one burnt-orange band; honey linear soffit; "
            "physical neutral low-E storefront; stainless pump protection; "
            "broom-finished forecourt and dark roof membrane"
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
                "reference-locked multi-angle ImageGen source pack, clean "
                "six-cell PBR plate, deterministic metric geometry, physical "
                "pump equipment and occupied low-E storefront depth"
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
                "fixed_landmark",
                "six_column_canopy",
                "three_physical_pump_islands",
                "occupied_retail_storefront",
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
    (folder / "archetype-source.json").write_text(
        json.dumps(manifest["source_provenance"], indent=2, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    print(
        f"[wave10-gas] {FAMILY}: {assembled_triangles} triangles, "
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
        f"[wave10-gas-render] {FAMILY}: {len(manifest['renders'])} renders"
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
