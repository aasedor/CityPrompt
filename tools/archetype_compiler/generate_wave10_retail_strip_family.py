"""Author the Wave 10 Contemporary Prairie Retail Strip LEGO family.

The assembled GLB is a complete contemporary neighbourhood retail bar rather
than a generic commercial box. One raised russet-brick anchor, six smaller
tenant modules, a continuous black-and-cedar canopy, physical occupied
storefronts, an integrated restaurant patio, seven roof units, and seven rear
service zones are deterministic metric geometry. A semantic LEGO stack remains
available for modest hand-drawn dimension changes and long-axis streetwall
repeat.

Run with Blender 5.x from the repository root:

    blender --background --factory-startup --python \
      tools/archetype_compiler/generate_wave10_retail_strip_family.py -- \
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
    texture_inventory,
)


FAMILY = "contemporary-prairie-retail-strip"
ARCHETYPE_ID = "commercial_strip_mall"
VARIANT_ID = "strip_contemporary_retail"
ALIASES = [
    ARCHETYPE_ID,
    VARIANT_ID,
    "contemporary_retail_strip",
    "prairie_neighbourhood_retail",
]
LABEL = "Commercial Strip Mall — Contemporary Prairie Retail"
GLASS_PROFILE = "low_iron_neutral"

NATIVE_WIDTH = 70.0
NATIVE_DEPTH = 26.0
NATIVE_HEIGHT = 7.50
NATIVE_FLOORS = 1
MIN_FLOORS = 1
MAX_FLOORS = 2
PODIUM_HEIGHT = 0.35
FLOOR_HEIGHT = 4.15
CROWN_HEIGHT = 2.70
ROOF_HEIGHT = 1.45

BUILDING_WIDTH = 60.0
BUILDING_DEPTH = 18.0
FRONT_Y = -9.0
REAR_Y = 9.0
BAY_BOUNDS = (-32.0, -23.0, -14.6, -6.2, 2.2, 10.6, 19.0, 28.0)
BAY_CENTRES = tuple(
    (BAY_BOUNDS[index] + BAY_BOUNDS[index + 1]) * 0.5
    for index in range(7)
)

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
    if not mat.use_nodes:
        return mat
    for node in mat.node_tree.nodes:
        if node.bl_idname == "ShaderNodeNormalMap":
            node.inputs["Strength"].default_value = strength
    return mat


def make_glass_material(
    assets: dict[str, str],
) -> bpy.types.Material:
    mat = material(
        "MAT_W10_RETAIL_PhysicalNeutralLowEStorefront",
        (0.040, 0.072, 0.084, 0.34),
        0.050,
        metallic=0.02,
    )
    bsdf = bsdf_for(mat)
    if bsdf.inputs.get("Roughness"):
        bsdf.inputs["Roughness"].default_value = 0.050
    if bsdf.inputs.get("Transmission Weight"):
        bsdf.inputs["Transmission Weight"].default_value = 0.92
    if bsdf.inputs.get("Coat Weight"):
        bsdf.inputs["Coat Weight"].default_value = 0.38
    if bsdf.inputs.get("Coat Roughness"):
        bsdf.inputs["Coat Roughness"].default_value = 0.045
    if bsdf.inputs.get("IOR"):
        bsdf.inputs["IOR"].default_value = 1.52
    if bsdf.inputs.get("Alpha"):
        bsdf.inputs["Alpha"].default_value = 0.34
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
    mat["pane_recess_m"] = 0.18
    mat["interior_depth_m"] = 8.5
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
    mats["brick"] = grade_material(
        skin_material(
            "MAT_W10_RETAIL_RussetModularBrick",
            folder,
            near["russet_brick"],
            "russet_brick",
        ),
        saturation=0.92,
        value=0.78,
    )
    mats["charcoal"] = grade_material(
        skin_material(
            "MAT_W10_RETAIL_CharcoalMicroRibMetal",
            folder,
            near["charcoal_metal"],
            "charcoal_metal",
            metallic=0.42,
        ),
        saturation=0.66,
        value=0.46,
    )
    mats["cedar"] = grade_material(
        skin_material(
            "MAT_W10_RETAIL_WarmCedarSoffit",
            folder,
            near["cedar_soffit"],
            "cedar_soffit",
        ),
        saturation=0.96,
        value=0.82,
    )
    mats["concrete"] = set_normal_strength(
        grade_material(
            skin_material(
                "MAT_W10_RETAIL_BroomFinishConcrete",
                folder,
                near["sidewalk_concrete"],
                "sidewalk_concrete",
            ),
            saturation=0.34,
            value=0.82,
        ),
        0.16,
    )
    mats["roof"] = grade_material(
        skin_material(
            "MAT_W10_RETAIL_PaleSinglePlyRoof",
            folder,
            near["roof_membrane"],
            "roof_membrane",
        ),
        saturation=0.35,
        value=0.88,
    )
    mats["service"] = grade_material(
        skin_material(
            "MAT_W10_RETAIL_RearServiceMetal",
            folder,
            near["charcoal_metal"],
            "service_metal",
            metallic=0.38,
        ),
        saturation=0.26,
        value=0.32,
    )
    mats["meter"] = skin_material(
        "MAT_W10_RETAIL_MeterBankMetal",
        folder,
        far["meter_bank"],
        "meter_bank",
        metallic=0.62,
    )
    mats["patio_wood"] = grade_material(
        skin_material(
            "MAT_W10_RETAIL_PatioTimber",
            folder,
            near["cedar_soffit"],
            "patio_timber",
        ),
        saturation=0.76,
        value=0.69,
    )
    mats["rail"] = grade_material(
        skin_material(
            "MAT_W10_RETAIL_PatioRail",
            folder,
            near["charcoal_metal"],
            "patio_railing",
            metallic=0.48,
        ),
        saturation=0.40,
        value=0.30,
    )
    mats["black"] = grade_material(
        skin_material(
            "MAT_W10_RETAIL_BlackSteelAndFrames",
            folder,
            near["charcoal_metal"],
            "black_steel",
            metallic=0.48,
        ),
        saturation=0.40,
        value=0.28,
    )
    mats["asphalt"] = set_normal_strength(
        grade_material(
            skin_material(
                "MAT_W10_RETAIL_Asphalt",
                folder,
                far["asphalt"],
                "asphalt",
            ),
            saturation=0.22,
            value=0.42,
        ),
        0.15,
    )
    mats["prairie"] = grade_material(
        skin_material(
            "MAT_W10_RETAIL_PrairiePlanting",
            folder,
            far["prairie_planting"],
            "prairie_planting",
        ),
        saturation=0.76,
        value=0.68,
    )
    mats["interior"] = grade_material(
        skin_material(
            "MAT_W10_RETAIL_OccupiedRetailDepth",
            folder,
            near["interior"],
            "occupied_retail_interior",
            emission_strength=0.55,
        ),
        saturation=0.82,
        value=0.74,
    )
    mats["glass"] = make_glass_material(near["storefront_glass"])
    mats["hvac"] = skin_material(
        "MAT_W10_RETAIL_HVACGalvanizedMetal",
        folder,
        far["hvac_metal"],
        "hvac_metal",
        metallic=0.66,
    )
    mats["sign_frame"] = skin_material(
        "MAT_W10_RETAIL_SignPanelBacking",
        folder,
        far["sign_panels"],
        "sign_panels",
        metallic=0.18,
    )
    mats["warm_light"] = material(
        "MAT_W10_RETAIL_WarmLED",
        (1.0, 0.57, 0.24, 1.0),
        0.15,
        emission=(1.0, 0.33, 0.08, 1.0),
        emission_strength=4.2,
    )
    mats["cool_light"] = material(
        "MAT_W10_RETAIL_CoolDisplayLight",
        (0.80, 0.90, 1.0, 1.0),
        0.16,
        emission=(0.65, 0.80, 1.0, 1.0),
        emission_strength=1.7,
    )
    mats["interior_wood"] = material(
        "MAT_W10_RETAIL_InteriorDisplayWood",
        (0.39, 0.20, 0.080, 1.0),
        0.52,
    )
    mats["stainless"] = material(
        "MAT_W10_RETAIL_StainlessHardware",
        (0.50, 0.54, 0.55, 1.0),
        0.24,
        metallic=0.78,
    )
    mats["product_a"] = material(
        "MAT_W10_RETAIL_MerchandiseWarm",
        (0.42, 0.16, 0.075, 1.0),
        0.52,
    )
    mats["product_b"] = material(
        "MAT_W10_RETAIL_MerchandiseCool",
        (0.17, 0.27, 0.23, 1.0),
        0.55,
    )
    mats["product_c"] = material(
        "MAT_W10_RETAIL_MerchandiseOchre",
        (0.47, 0.36, 0.17, 1.0),
        0.56,
    )
    mats["white"] = material(
        "MAT_W10_RETAIL_CleanWhiteInterior",
        (0.68, 0.70, 0.69, 1.0),
        0.62,
    )
    sign_colours = (
        (0.48, 0.12, 0.055, 1.0),
        (0.62, 0.38, 0.045, 1.0),
        (0.09, 0.30, 0.33, 1.0),
        (0.30, 0.31, 0.34, 1.0),
        (0.62, 0.14, 0.045, 1.0),
        (0.08, 0.24, 0.42, 1.0),
        (0.26, 0.12, 0.06, 1.0),
    )
    mats["signs"] = [
        material(
            f"MAT_W10_RETAIL_AbstractSign_{index}",
            colour,
            0.28,
            metallic=0.08,
            emission=colour,
            emission_strength=0.28,
        )
        for index, colour in enumerate(sign_colours)
    ]
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


def add_site(
    mats: dict[str, bpy.types.Material],
    *,
    detailed: bool,
) -> list[bpy.types.Object]:
    objects = [
        b(
            "RETAILSTRIP_CompleteSiteSlab",
            (NATIVE_WIDTH, NATIVE_DEPTH, 0.22),
            (0.0, 0.0, 0.11),
            mats["concrete"],
            0.035,
            component="complete_retail_site",
        ),
        b(
            "RETAILSTRIP_CoveredSidewalk",
            (66.0, 4.0, 0.16),
            (1.0, -10.6, 0.30),
            mats["concrete"],
            0.025,
            component="covered_public_sidewalk",
        ),
        b(
            "RETAILSTRIP_RearServiceApron",
            (63.0, 4.2, 0.14),
            (-1.0, 10.65, 0.29),
            mats["concrete"],
            0.025,
            component="rear_service_apron",
        ),
    ]
    if not detailed:
        return objects

    # Physical joints and drains stop the broad apron from reading as plastic.
    for index, x in enumerate(range(-32, 35, 4)):
        objects.append(
            b(
                f"RETAILSTRIP_SidewalkJointX_{index:02d}",
                (0.032, 3.92, 0.016),
                (float(x), -10.6, 0.388),
                mats["black"],
                component="sidewalk_control_joint",
            )
        )
    for index, y in enumerate((-11.75, -10.60, -9.45)):
        objects.append(
            b(
                f"RETAILSTRIP_SidewalkJointY_{index:02d}",
                (65.6, 0.032, 0.016),
                (1.0, y, 0.388),
                mats["black"],
                component="sidewalk_control_joint",
            )
        )
    for index, x in enumerate((-22.8, -6.0, 10.8, 27.4)):
        objects.append(
            b(
                f"RETAILSTRIP_TrenchDrain_{index:02d}",
                (6.8, 0.17, 0.045),
                (x, -12.42, 0.25),
                mats["black"],
                0.012,
                component="canopy_trench_drain",
            )
        )
        for rib in range(15):
            objects.append(
                b(
                    f"RETAILSTRIP_DrainRib_{index:02d}_{rib:02d}",
                    (0.035, 0.18, 0.014),
                    (x - 3.15 + rib * 0.45, -12.42, 0.279),
                    mats["stainless"],
                    component="drain_grate",
                )
            )
    for index, x in enumerate(BAY_CENTRES):
        objects.append(
            c(
                f"RETAILSTRIP_Bollard_{index:02d}",
                0.11,
                0.90,
                (x, -11.85, 0.84),
                mats["black"],
                vertices=20,
                component="storefront_protection_bollard",
                count_authority="seven_tenant_frontage_bollards",
            )
        )
    # Perimeter curbs express the reusable site envelope without importing a
    # whole parking lot into every placement.
    for name, size, location in (
        ("Front", (70.0, 0.20, 0.24), (0.0, -12.88, 0.34)),
        ("Rear", (70.0, 0.20, 0.24), (0.0, 12.88, 0.34)),
        ("Left", (0.20, 25.6, 0.24), (-34.88, 0.0, 0.34)),
        ("Right", (0.20, 25.6, 0.24), (34.88, 0.0, 0.34)),
    ):
        objects.append(
            b(
                f"RETAILSTRIP_SiteCurb_{name}",
                size,
                location,
                mats["concrete"],
                0.025,
                component="site_curb",
            )
        )
    # Three restrained planting pockets bracket the long facade without
    # obscuring its seven-bay rhythm.
    for pocket_index, (x, y, width) in enumerate(
        ((-33.2, -10.6, 2.4), (31.5, -12.0, 4.8), (32.4, 10.6, 3.0))
    ):
        objects.append(
            b(
                f"RETAILSTRIP_PlantingPocket_{pocket_index}",
                (width, 1.0, 0.18),
                (x, y, 0.36),
                mats["prairie"],
                0.15,
                component="prairie_planting_pocket",
            )
        )
        for plant_index in range(7):
            px = x - width * 0.36 + plant_index * width * 0.12
            height = 0.38 + 0.09 * ((plant_index * 3) % 4)
            objects.append(
                c(
                    f"RETAILSTRIP_Plant_{pocket_index}_{plant_index}",
                    0.055,
                    height,
                    (px, y, 0.45 + height * 0.5),
                    mats["prairie"],
                    vertices=7,
                    component="prairie_planting",
                )
            )
    return objects


def add_storefront(
    mats: dict[str, bpy.types.Material],
    *,
    detailed: bool,
    schedule: str = "typical_a",
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    pane_y = FRONT_Y - 0.02
    frame_y = FRONT_Y - 0.15
    sill_z = 0.48
    transom_z = 3.30
    head_z = 4.18
    door_shift = {
        "typical_a": 0.0,
        "typical_b": -0.55,
        "typical_c": 0.55,
    }.get(schedule, 0.0)

    # Eight physical brick pilasters establish the full tenant rhythm.
    for boundary_index, x in enumerate(BAY_BOUNDS):
        objects.append(
            b(
                f"RETAILSTRIP_BrickPilaster_{boundary_index:02d}",
                (0.66, 0.72, 4.18),
                (x, FRONT_Y + 0.22, 2.48),
                mats["brick"],
                0.025,
                component="brick_tenant_pilaster",
                count_authority="eight_tenant_boundary_pilasters",
            )
        )
        if detailed and boundary_index not in {0, len(BAY_BOUNDS) - 1}:
            objects.extend(
                [
                    b(
                        f"RETAILSTRIP_WallLightBody_{boundary_index:02d}",
                        (0.18, 0.15, 0.48),
                        (x - 0.32, FRONT_Y - 0.20, 2.70),
                        mats["black"],
                        0.025,
                        component="storefront_wall_light",
                    ),
                    b(
                        f"RETAILSTRIP_WallLightLens_{boundary_index:02d}",
                        (0.10, 0.035, 0.28),
                        (x - 0.32, FRONT_Y - 0.29, 2.70),
                        mats["warm_light"],
                        0.02,
                        component="storefront_wall_light",
                    ),
                ]
            )

    # The raised anchor is an inhabitable brick volume, not a signboard pasted
    # onto the ordinary parapet.
    anchor_centre = BAY_CENTRES[0]
    anchor_width = BAY_BOUNDS[1] - BAY_BOUNDS[0]
    objects.extend(
        [
            b(
                "RETAILSTRIP_AnchorBrickHead",
                (anchor_width, 0.64, 3.02),
                (anchor_centre, FRONT_Y + 0.18, 5.68),
                mats["brick"],
                0.025,
                component="raised_anchor_brick_volume",
                count_authority="one_raised_left_anchor",
            ),
            b(
                "RETAILSTRIP_InlineCharcoalSignFascia",
                (BAY_BOUNDS[-1] - BAY_BOUNDS[1], 0.62, 1.62),
                (
                    (BAY_BOUNDS[-1] + BAY_BOUNDS[1]) * 0.5,
                    FRONT_Y + 0.18,
                    5.15,
                ),
                mats["charcoal"],
                0.018,
                component="continuous_charcoal_signage_parapet",
            ),
        ]
    )

    for bay_index, (x0, x1) in enumerate(zip(BAY_BOUNDS, BAY_BOUNDS[1:])):
        bay_centre = (x0 + x1) * 0.5
        inner_left = x0 + 0.40
        inner_right = x1 - 0.40
        door_centre = bay_centre + door_shift
        door_half = 1.12 if bay_index in {0, 6} else 0.98
        verticals = [
            inner_left,
            door_centre - door_half,
            door_centre,
            door_centre + door_half,
            inner_right,
        ]
        # Avoid narrow residual panes if a shifted module approaches a pier.
        verticals = sorted(
            max(inner_left, min(inner_right, value)) for value in verticals
        )
        for mullion_index, x in enumerate(verticals):
            objects.append(
                b(
                    f"RETAILSTRIP_StorefrontMullion_{bay_index}_{mullion_index}",
                    (0.105, 0.18, head_z - sill_z),
                    (x, frame_y, (head_z + sill_z) * 0.5),
                    mats["black"],
                    0.012,
                    component="thermally_broken_storefront_frame",
                )
            )
        objects.extend(
            [
                b(
                    f"RETAILSTRIP_StorefrontSill_{bay_index}",
                    (inner_right - inner_left, 0.18, 0.12),
                    (bay_centre, frame_y, sill_z),
                    mats["black"],
                    0.012,
                    component="storefront_sill",
                ),
                b(
                    f"RETAILSTRIP_StorefrontTransom_{bay_index}",
                    (inner_right - inner_left, 0.18, 0.11),
                    (bay_centre, frame_y, transom_z),
                    mats["black"],
                    0.010,
                    component="storefront_transom",
                ),
                b(
                    f"RETAILSTRIP_StorefrontHead_{bay_index}",
                    (inner_right - inner_left, 0.30, 0.34),
                    (bay_centre, FRONT_Y + 0.03, head_z),
                    mats["black"],
                    0.012,
                    component="deep_storefront_head",
                ),
            ]
        )
        for pane_index, (left, right) in enumerate(
            zip(verticals[:-1], verticals[1:])
        ):
            width = max(0.08, right - left - 0.10)
            centre = (left + right) * 0.5
            is_door = pane_index in {1, 2}
            objects.append(
                b(
                    (
                        f"RETAILSTRIP_TenantDoorPane_{bay_index}_{pane_index}"
                        if is_door
                        else f"RETAILSTRIP_TenantStorefrontPane_{bay_index}_{pane_index}"
                    ),
                    (width, 0.055, transom_z - sill_z - 0.13),
                    (centre, pane_y, (transom_z + sill_z) * 0.5),
                    mats["glass"],
                    0.008,
                    component=(
                        "physical_glazed_entry_door"
                        if is_door
                        else "physical_low_e_storefront_pane"
                    ),
                )
            )
            objects.append(
                b(
                    f"RETAILSTRIP_TenantTransomPane_{bay_index}_{pane_index}",
                    (width, 0.050, head_z - transom_z - 0.15),
                    (centre, pane_y, (head_z + transom_z) * 0.5),
                    mats["glass"],
                    0.006,
                    component="physical_low_e_transom_pane",
                )
            )
        for leaf_index, x in enumerate(
            (door_centre - door_half * 0.5, door_centre + door_half * 0.5)
        ):
            objects.extend(
                [
                    c(
                        f"RETAILSTRIP_DoorPull_{bay_index}_{leaf_index}",
                        0.038,
                        0.72,
                        (x, FRONT_Y - 0.28, 1.93),
                        mats["stainless"],
                        vertices=16,
                        component="storefront_door_hardware",
                    ),
                    b(
                        f"RETAILSTRIP_DoorKickplate_{bay_index}_{leaf_index}",
                        (door_half - 0.16, 0.025, 0.24),
                        (x, FRONT_Y - 0.25, 0.68),
                        mats["stainless"],
                        component="storefront_door_hardware",
                    ),
                ]
            )
        objects.append(
            b(
                f"RETAILSTRIP_EntryThreshold_{bay_index}",
                (door_half * 2.0, 0.45, 0.055),
                (door_centre, FRONT_Y - 0.30, 0.43),
                mats["stainless"],
                0.012,
                component="recessed_entry_threshold",
            )
        )
        sign_z = 5.70 if bay_index == 0 else 5.20
        sign_width = min(4.5, (x1 - x0) * 0.52)
        objects.extend(
            [
                b(
                    f"RETAILSTRIP_SignFrame_{bay_index}",
                    (sign_width, 0.22, 0.92),
                    (bay_centre, FRONT_Y - 0.18, sign_z),
                    mats["black"],
                    0.055,
                    component="projecting_backlit_sign_frame",
                ),
                b(
                    f"RETAILSTRIP_AbstractSignPanel_{bay_index}",
                    (sign_width - 0.28, 0.045, 0.56),
                    (bay_centre, FRONT_Y - 0.31, sign_z),
                    mats["signs"][bay_index],
                    0.018,
                    component="abstract_non_text_tenant_identity",
                    count_authority="seven_abstract_tenant_signs",
                ),
            ]
        )
        if detailed:
            # Two inlaid geometric fields evoke illuminated channel signage
            # without introducing unreadable pseudo-text.
            objects.extend(
                [
                    b(
                        f"RETAILSTRIP_SignMotifA_{bay_index}",
                        (sign_width * 0.31, 0.022, 0.50),
                        (bay_centre - sign_width * 0.22, FRONT_Y - 0.345, sign_z),
                        mats["white"],
                        0.012,
                        component="abstract_sign_graphic",
                    ),
                    b(
                        f"RETAILSTRIP_SignMotifB_{bay_index}",
                        (sign_width * 0.22, 0.022, 0.50),
                        (bay_centre + sign_width * 0.28, FRONT_Y - 0.345, sign_z),
                        mats["sign_frame"],
                        0.012,
                        component="abstract_sign_graphic",
                    ),
                ]
            )
    return objects


def add_interior(
    mats: dict[str, bpy.types.Material],
    *,
    detailed: bool,
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = [
        b(
            "RETAILSTRIP_InteriorFloor",
            (59.1, 17.1, 0.14),
            (-2.0, 0.0, 0.43),
            mats["concrete"],
            component="occupied_retail_floor",
        ),
        b(
            "RETAILSTRIP_InteriorCeiling",
            (59.1, 17.1, 0.12),
            (-2.0, 0.0, 4.30),
            mats["white"],
            component="occupied_retail_ceiling",
        ),
    ]
    for bay_index, (x0, x1) in enumerate(zip(BAY_BOUNDS, BAY_BOUNDS[1:])):
        centre = (x0 + x1) * 0.5
        width = x1 - x0
        # A registered occupied-depth panel is backed by real fixtures so the
        # view through low-E glass retains parallax at oblique angles.
        objects.append(
            b(
                f"RETAILSTRIP_OccupiedDepthUnderlay_{bay_index}",
                (width - 0.9, 0.08, 3.25),
                (centre, 6.65, 2.20),
                mats["interior"],
                component="registered_occupied_depth_underlay",
            )
        )
        for row_index, y in enumerate((-5.2, -0.8, 3.6)):
            objects.append(
                b(
                    f"RETAILSTRIP_CeilingLight_{bay_index}_{row_index}",
                    (width * 0.52, 0.12, 0.055),
                    (centre, y, 4.20),
                    mats["cool_light"],
                    0.012,
                    component="occupied_interior_lighting",
                )
            )
        if detailed:
            # Track lights and pendant lenses put visibly warm, modeled light
            # sources behind the glass instead of relying on a flat luminous
            # backdrop. Their staggered depth is legible from oblique views.
            for track_index, y in enumerate((-4.4, 0.2, 4.5)):
                objects.append(
                    b(
                        f"RETAILSTRIP_InteriorTrack_{bay_index}_{track_index}",
                        (width * 0.58, 0.055, 0.055),
                        (centre, y, 4.08),
                        mats["black"],
                        0.012,
                        component="occupied_interior_track_lighting",
                    )
                )
                for lamp_index, offset in enumerate((-0.28, 0.0, 0.28)):
                    lamp_x = centre + offset * width
                    objects.extend(
                        [
                            c(
                                f"RETAILSTRIP_InteriorSpotBody_{bay_index}_{track_index}_{lamp_index}",
                                0.085,
                                0.20,
                                (lamp_x, y, 3.92),
                                mats["black"],
                                vertices=14,
                                component="occupied_interior_track_lighting",
                            ),
                            c(
                                f"RETAILSTRIP_InteriorSpotLens_{bay_index}_{track_index}_{lamp_index}",
                                0.068,
                                0.025,
                                (lamp_x, y, 3.80),
                                mats["warm_light"],
                                vertices=14,
                                component="occupied_interior_track_lighting",
                            ),
                        ]
                    )
        if bay_index == 6:
            continue
        shelf_width = width - 1.20
        for shelf_index, y in enumerate((4.9, 6.0)):
            objects.extend(
                [
                    b(
                        f"RETAILSTRIP_BackShelfBase_{bay_index}_{shelf_index}",
                        (shelf_width, 0.52, 0.18),
                        (centre, y, 0.65),
                        mats["interior_wood"],
                        0.018,
                        component="modeled_retail_shelving",
                    ),
                    b(
                        f"RETAILSTRIP_BackShelfTop_{bay_index}_{shelf_index}",
                        (shelf_width, 0.45, 0.16),
                        (centre, y, 3.35),
                        mats["interior_wood"],
                        0.018,
                        component="modeled_retail_shelving",
                    ),
                ]
            )
            for post_index, x in enumerate(
                (x0 + 0.80, centre, x1 - 0.80)
            ):
                objects.append(
                    b(
                        f"RETAILSTRIP_ShelfPost_{bay_index}_{shelf_index}_{post_index}",
                        (0.08, 0.44, 2.75),
                        (x, y, 2.00),
                        mats["black"],
                        component="modeled_retail_shelving",
                    )
                )
            for level_index, z in enumerate((1.15, 1.75, 2.35, 2.95)):
                objects.append(
                    b(
                        f"RETAILSTRIP_ShelfBoard_{bay_index}_{shelf_index}_{level_index}",
                        (shelf_width, 0.48, 0.07),
                        (centre, y, z),
                        mats["interior_wood"],
                        component="modeled_retail_shelving",
                    )
                )
                if detailed:
                    for product_index in range(9):
                        px = x0 + 0.70 + product_index * (shelf_width - 0.5) / 8
                        product_mat = (
                            mats["product_a"],
                            mats["product_b"],
                            mats["product_c"],
                        )[(product_index + level_index + bay_index) % 3]
                        objects.append(
                            b(
                                f"RETAILSTRIP_Merchandise_{bay_index}_{shelf_index}_{level_index}_{product_index}",
                                (0.27, 0.19, 0.22 + 0.06 * (product_index % 2)),
                                (px, y - 0.29, z + 0.18),
                                product_mat,
                                0.025,
                                component="modeled_merchandise_depth",
                            )
                        )
        # Two display tables occupy the foreground of every retail tenant.
        for table_index, y in enumerate((-3.2, 0.4)):
            objects.extend(
                [
                    b(
                        f"RETAILSTRIP_DisplayTableTop_{bay_index}_{table_index}",
                        (width * 0.46, 1.05, 0.12),
                        (centre, y, 1.18),
                        mats["interior_wood"],
                        0.045,
                        component="modeled_retail_display",
                    ),
                    b(
                        f"RETAILSTRIP_DisplayTableBase_{bay_index}_{table_index}",
                        (width * 0.26, 0.66, 0.92),
                        (centre, y, 0.72),
                        mats["black"],
                        0.035,
                        component="modeled_retail_display",
                    ),
                ]
            )
            if detailed:
                for product_index in range(5):
                    px = centre - width * 0.17 + product_index * width * 0.085
                    objects.append(
                        b(
                            f"RETAILSTRIP_DisplayProduct_{bay_index}_{table_index}_{product_index}",
                            (0.25, 0.25, 0.23 + 0.05 * (product_index % 2)),
                            (px, y, 1.40),
                            mats[
                                ("product_a", "product_b", "product_c")[
                                    (product_index + bay_index) % 3
                                ]
                            ],
                            0.028,
                            component="modeled_merchandise_depth",
                        )
                    )
    # The restaurant occupies the right end-cap and is visibly distinct from
    # the inline retail fixtures.
    restaurant_centre = BAY_CENTRES[-1]
    objects.extend(
        [
            b(
                "RETAILSTRIP_RestaurantBarFront",
                (5.8, 0.72, 1.12),
                (restaurant_centre, 3.9, 0.98),
                mats["interior_wood"],
                0.045,
                component="occupied_restaurant_bar",
            ),
            b(
                "RETAILSTRIP_RestaurantBarTop",
                (6.2, 1.02, 0.12),
                (restaurant_centre, 3.65, 1.57),
                mats["stainless"],
                0.055,
                component="occupied_restaurant_bar",
            ),
            b(
                "RETAILSTRIP_RestaurantBackBar",
                (6.4, 0.48, 2.65),
                (restaurant_centre, 6.15, 1.85),
                mats["interior_wood"],
                0.035,
                component="occupied_restaurant_bar",
            ),
        ]
    )
    for table_index, (x, y) in enumerate(
        (
            (21.0, -3.2),
            (25.5, -3.2),
            (21.0, 0.5),
            (25.5, 0.5),
        )
    ):
        objects.append(
            c(
                f"RETAILSTRIP_RestaurantTable_{table_index}",
                0.58,
                0.08,
                (x, y, 1.15),
                mats["interior_wood"],
                vertices=32,
                component="occupied_restaurant_furniture",
            )
        )
        objects.append(
            c(
                f"RETAILSTRIP_RestaurantTableLeg_{table_index}",
                0.09,
                0.82,
                (x, y, 0.72),
                mats["black"],
                vertices=16,
                component="occupied_restaurant_furniture",
            )
        )
        if detailed:
            for chair_index, angle in enumerate((0.0, math.pi * 0.5, math.pi, math.pi * 1.5)):
                cx = x + math.cos(angle) * 0.92
                cy = y + math.sin(angle) * 0.92
                objects.extend(
                    [
                        b(
                            f"RETAILSTRIP_RestaurantChairSeat_{table_index}_{chair_index}",
                            (0.42, 0.42, 0.09),
                            (cx, cy, 0.76),
                            mats["black"],
                            0.035,
                            component="occupied_restaurant_furniture",
                        ),
                        b(
                            f"RETAILSTRIP_RestaurantChairBack_{table_index}_{chair_index}",
                            (0.42, 0.08, 0.58),
                            (
                                cx,
                                cy + (0.36 if math.sin(angle) >= 0 else -0.36),
                                1.03,
                            ),
                            mats["black"],
                            0.025,
                            component="occupied_restaurant_furniture",
                        ),
                    ]
                )
    return objects


def add_shell(
    mats: dict[str, bpy.types.Material],
    *,
    detailed: bool,
    schedule: str = "typical_a",
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = [
        b(
            "RETAILSTRIP_BuildingFloorSlab",
            (BUILDING_WIDTH, BUILDING_DEPTH, 0.26),
            (-2.0, 0.0, 0.36),
            mats["concrete"],
            0.025,
            component="retail_bar_floor_slab",
        ),
        b(
            "RETAILSTRIP_RearServiceEnvelope",
            (BUILDING_WIDTH, 0.42, 5.35),
            (-2.0, REAR_Y - 0.20, 3.02),
            mats["service"],
            0.018,
            component="complete_rear_service_envelope",
        ),
        b(
            "RETAILSTRIP_LeftAnchorSideWall",
            (0.46, BUILDING_DEPTH, 6.85),
            (BAY_BOUNDS[0] + 0.23, 0.0, 3.78),
            mats["brick"],
            0.018,
            component="raised_anchor_brick_return",
        ),
        b(
            "RETAILSTRIP_RightEndWallRear",
            (0.42, 12.2, 5.35),
            (BAY_BOUNDS[-1] - 0.21, 2.90, 3.02),
            mats["brick"],
            0.018,
            component="restaurant_brick_end_return",
        ),
    ]
    # Real tenant fire separations reinforce that each storefront is a
    # leasable module and make occupied depth read correctly through the glass.
    for partition_index, x in enumerate(BAY_BOUNDS[1:-1], start=1):
        objects.append(
            b(
                f"RETAILSTRIP_TenantPartition_{partition_index}",
                (0.15, 16.9, 4.05),
                (x, 0.15, 2.46),
                mats["white"],
                component="tenant_demising_wall",
            )
        )
    objects.extend(
        add_storefront(mats, detailed=detailed, schedule=schedule)
    )
    objects.extend(add_interior(mats, detailed=detailed))
    return objects


def add_canopy(
    mats: dict[str, bpy.types.Material],
    *,
    detailed: bool,
) -> list[bpy.types.Object]:
    canopy_centre_x = (BAY_BOUNDS[0] + BAY_BOUNDS[-1]) * 0.5
    canopy_width = BAY_BOUNDS[-1] - BAY_BOUNDS[0]
    objects: list[bpy.types.Object] = [
        b(
            "RETAILSTRIP_ContinuousCanopyRoof",
            (canopy_width + 0.8, 2.90, 0.22),
            (canopy_centre_x, -10.35, 4.55),
            mats["black"],
            0.025,
            component="continuous_thin_black_steel_canopy",
        ),
        b(
            "RETAILSTRIP_ContinuousCedarSoffit",
            (canopy_width + 0.48, 2.58, 0.10),
            (canopy_centre_x, -10.34, 4.39),
            mats["cedar"],
            component="continuous_warm_cedar_soffit",
        ),
        b(
            "RETAILSTRIP_CanopyFrontFascia",
            (canopy_width + 0.82, 0.24, 0.38),
            (canopy_centre_x, -11.72, 4.51),
            mats["black"],
            0.020,
            component="thin_canopy_front_fascia",
        ),
    ]
    for column_index, x in enumerate(BAY_BOUNDS):
        objects.extend(
            [
                b(
                    f"RETAILSTRIP_CanopyColumn_{column_index}",
                    (0.18, 0.18, 4.05),
                    (x, -11.28, 2.34),
                    mats["black"],
                    0.016,
                    component="canopy_structural_column",
                    count_authority="exactly_eight_bay_aligned_canopy_columns",
                ),
                b(
                    f"RETAILSTRIP_CanopyColumnBase_{column_index}",
                    (0.34, 0.34, 0.055),
                    (x, -11.28, 0.43),
                    mats["stainless"],
                    0.018,
                    component="canopy_column_base_plate",
                ),
            ]
        )
    if detailed:
        # Slat reveals and light strips are modeled at the soffit datum.
        for reveal_index in range(13):
            y = -11.45 + reveal_index * 0.185
            objects.append(
                b(
                    f"RETAILSTRIP_SoffitReveal_{reveal_index:02d}",
                    (canopy_width + 0.25, 0.027, 0.016),
                    (canopy_centre_x, y, 4.335),
                    mats["black"],
                    component="cedar_soffit_reveal",
                )
            )
        for light_index, x in enumerate(BAY_CENTRES):
            objects.append(
                b(
                    f"RETAILSTRIP_CanopyLinearLight_{light_index}",
                    (2.85, 0.075, 0.035),
                    (x, -10.48, 4.325),
                    mats["warm_light"],
                    0.012,
                    component="canopy_recessed_linear_light",
                    count_authority="seven_bay_aligned_canopy_lights",
                )
            )
        for drain_index, x in enumerate((BAY_BOUNDS[0] + 0.25, BAY_BOUNDS[-1] - 0.25)):
            objects.extend(
                [
                    b(
                        f"RETAILSTRIP_CanopyScupper_{drain_index}",
                        (0.30, 0.20, 0.16),
                        (x, -11.65, 4.45),
                        mats["black"],
                        0.015,
                        component="canopy_scupper",
                    ),
                    c(
                        f"RETAILSTRIP_CanopyDownspout_{drain_index}",
                        0.065,
                        3.72,
                        (x, FRONT_Y + 0.34, 2.25),
                        mats["black"],
                        vertices=16,
                        component="canopy_downspout",
                    ),
                ]
            )
    return objects


def add_patio(
    mats: dict[str, bpy.types.Material],
    *,
    detailed: bool,
) -> list[bpy.types.Object]:
    patio_x0, patio_x1 = 28.25, 34.35
    patio_y0, patio_y1 = -11.55, -3.10
    patio_centre_x = (patio_x0 + patio_x1) * 0.5
    patio_centre_y = (patio_y0 + patio_y1) * 0.5
    objects: list[bpy.types.Object] = [
        b(
            "RETAILSTRIP_IntegratedPatioSlab",
            (patio_x1 - patio_x0, patio_y1 - patio_y0, 0.18),
            (patio_centre_x, patio_centre_y, 0.37),
            mats["concrete"],
            0.025,
            component="integrated_restaurant_patio",
        )
    ]

    # Wrap the physical restaurant glazing around the right corner.
    side_x = BAY_BOUNDS[-1] + 0.02
    side_frame_x = BAY_BOUNDS[-1] + 0.15
    side_y_values = (-8.65, -6.85, -5.05, -3.25)
    for frame_index, y in enumerate(side_y_values):
        objects.append(
            b(
                f"RETAILSTRIP_RestaurantCornerMullion_{frame_index}",
                (0.18, 0.10, 3.68),
                (side_frame_x, y, 2.33),
                mats["black"],
                0.012,
                component="wrapped_restaurant_storefront_frame",
            )
        )
    for pane_index, (y0, y1) in enumerate(
        zip(side_y_values[:-1], side_y_values[1:])
    ):
        objects.extend(
            [
                b(
                    f"RETAILSTRIP_RestaurantCornerPane_{pane_index}",
                    (0.055, y1 - y0 - 0.10, 2.70),
                    (side_x, (y0 + y1) * 0.5, 1.86),
                    mats["glass"],
                    0.006,
                    component="physical_low_e_corner_glazing",
                ),
                b(
                    f"RETAILSTRIP_RestaurantCornerTransom_{pane_index}",
                    (0.050, y1 - y0 - 0.10, 0.73),
                    (side_x, (y0 + y1) * 0.5, 3.75),
                    mats["glass"],
                    0.006,
                    component="physical_low_e_corner_glazing",
                ),
            ]
        )
    objects.extend(
        [
            b(
                "RETAILSTRIP_RestaurantCornerSill",
                (0.18, side_y_values[-1] - side_y_values[0], 0.12),
                (
                    side_frame_x,
                    (side_y_values[0] + side_y_values[-1]) * 0.5,
                    0.48,
                ),
                mats["black"],
                component="wrapped_restaurant_storefront_frame",
            ),
            b(
                "RETAILSTRIP_RestaurantCornerTransomBar",
                (0.18, side_y_values[-1] - side_y_values[0], 0.11),
                (
                    side_frame_x,
                    (side_y_values[0] + side_y_values[-1]) * 0.5,
                    3.30,
                ),
                mats["black"],
                component="wrapped_restaurant_storefront_frame",
            ),
            b(
                "RETAILSTRIP_RestaurantCornerHead",
                (0.28, side_y_values[-1] - side_y_values[0], 0.34),
                (
                    side_frame_x,
                    (side_y_values[0] + side_y_values[-1]) * 0.5,
                    4.18,
                ),
                mats["black"],
                component="wrapped_restaurant_storefront_frame",
            ),
        ]
    )

    # The pergola shares the canopy datum and brick corner pier so it reads as
    # an intentional part of the architecture.
    post_locations = (
        (28.65, -11.15),
        (34.00, -11.15),
        (28.65, -7.25),
        (34.00, -7.25),
        (28.65, -3.45),
        (34.00, -3.45),
    )
    for post_index, (x, y) in enumerate(post_locations):
        objects.append(
            b(
                f"RETAILSTRIP_PergolaPost_{post_index}",
                (0.25, 0.25, 4.45),
                (x, y, 2.62),
                mats["patio_wood"],
                0.022,
                component="integrated_patio_pergola_post",
                count_authority="six_structural_pergola_posts",
            )
        )
    for beam_index, x in enumerate((28.65, 34.00)):
        objects.append(
            b(
                f"RETAILSTRIP_PergolaLongBeam_{beam_index}",
                (0.30, 8.15, 0.34),
                (x, patio_centre_y, 4.78),
                mats["patio_wood"],
                0.022,
                component="integrated_patio_pergola_beam",
            )
        )
    for fin_index in range(14):
        y = patio_y0 + 0.35 + fin_index * (patio_y1 - patio_y0 - 0.70) / 13
        objects.append(
            b(
                f"RETAILSTRIP_PergolaFin_{fin_index:02d}",
                (6.25, 0.16, 0.30),
                (patio_centre_x, y, 5.03),
                mats["patio_wood"],
                0.016,
                component="integrated_patio_pergola_fin",
                count_authority="fourteen_aligned_pergola_fins",
            )
        )

    # Open black rail with actual top/bottom members and individually modeled
    # balusters. The reference never has an opaque infill panel here.
    railing_runs = (
        ("Front", (6.00, 0.10, 0.10), (patio_centre_x, patio_y0)),
        ("Outer", (0.10, 8.30, 0.10), (patio_x1, patio_centre_y)),
        ("Rear", (6.00, 0.10, 0.10), (patio_centre_x, patio_y1)),
    )
    for name, size, (x, y) in railing_runs:
        for rail_index, z in enumerate((0.53, 1.43)):
            objects.append(
                b(
                    f"RETAILSTRIP_PatioRail{name}_{rail_index}",
                    size,
                    (x, y, z),
                    mats["rail"],
                    0.012,
                    component="integrated_open_black_patio_railing",
                )
            )
    for post_index, (x, y) in enumerate(
        (
            (patio_x0, patio_y0),
            (patio_x1, patio_y0),
            (patio_x1, patio_y1),
            (patio_x0, patio_y1),
            (patio_x1, patio_centre_y),
        )
    ):
        objects.append(
            b(
                f"RETAILSTRIP_PatioRailPost_{post_index}",
                (0.13, 0.13, 1.12),
                (x, y, 0.94),
                mats["rail"],
                0.012,
                component="integrated_open_black_patio_railing",
            )
        )
    if detailed:
        for baluster_index in range(13):
            x = patio_x0 + 0.35 + baluster_index * (patio_x1 - patio_x0 - 0.70) / 12
            for y, suffix in ((patio_y0, "Front"), (patio_y1, "Rear")):
                objects.append(
                    b(
                        f"RETAILSTRIP_PatioBaluster{suffix}_{baluster_index:02d}",
                        (0.035, 0.10, 0.94),
                        (x, y, 0.93),
                        mats["black"],
                        component="patio_railing_baluster",
                    )
                )
        for baluster_index in range(17):
            y = patio_y0 + 0.30 + baluster_index * (patio_y1 - patio_y0 - 0.60) / 16
            objects.append(
                b(
                    f"RETAILSTRIP_PatioBalusterOuter_{baluster_index:02d}",
                    (0.10, 0.035, 0.94),
                    (patio_x1, y, 0.93),
                    mats["black"],
                    component="patio_railing_baluster",
                )
            )
    for table_index, (x, y) in enumerate(
        (
            (30.25, -9.65),
            (32.75, -9.65),
            (30.25, -7.25),
            (32.75, -7.25),
            (30.25, -4.85),
            (32.75, -4.85),
        )
    ):
        objects.extend(
            [
                c(
                    f"RETAILSTRIP_PatioTableTop_{table_index}",
                    0.52,
                    0.07,
                    (x, y, 1.14),
                    mats["interior_wood"],
                    vertices=28,
                    component="patio_furniture",
                ),
                c(
                    f"RETAILSTRIP_PatioTableLeg_{table_index}",
                    0.08,
                    0.78,
                    (x, y, 0.72),
                    mats["black"],
                    vertices=14,
                    component="patio_furniture",
                ),
            ]
        )
        if detailed:
            for chair_index, (dx, dy) in enumerate(
                ((-0.72, 0.0), (0.72, 0.0), (0.0, -0.72), (0.0, 0.72))
            ):
                chair_x = x + dx
                chair_y = y + dy
                back_x = chair_x + (0.29 if dx > 0 else -0.29 if dx < 0 else 0.0)
                back_y = chair_y + (0.29 if dy > 0 else -0.29 if dy < 0 else 0.0)
                back_size = (
                    (0.06, 0.42, 0.50)
                    if dx
                    else (0.42, 0.06, 0.50)
                )
                objects.extend(
                    [
                        b(
                            f"RETAILSTRIP_PatioChairSeat_{table_index}_{chair_index}",
                            (0.42, 0.42, 0.08),
                            (chair_x, chair_y, 0.82),
                            mats["black"],
                            0.025,
                            component="patio_furniture",
                        ),
                        b(
                            f"RETAILSTRIP_PatioChairBack_{table_index}_{chair_index}",
                            back_size,
                            (back_x, back_y, 1.05),
                            mats["black"],
                            0.020,
                            component="patio_furniture",
                        ),
                    ]
                )
                for leg_index, (leg_x, leg_y) in enumerate(
                    (
                        (-0.15, -0.15),
                        (-0.15, 0.15),
                        (0.15, -0.15),
                        (0.15, 0.15),
                    )
                ):
                    objects.append(
                        b(
                            f"RETAILSTRIP_PatioChairLeg_{table_index}_{chair_index}_{leg_index}",
                            (0.035, 0.035, 0.52),
                            (chair_x + leg_x, chair_y + leg_y, 0.56),
                            mats["black"],
                            component="patio_furniture",
                        )
                    )
    for planter_index, (x, y) in enumerate(
        ((28.95, -10.45), (33.70, -8.35), (33.70, -4.05))
    ):
        objects.extend(
            [
                b(
                    f"RETAILSTRIP_PatioPlanter_{planter_index}",
                    (0.72, 0.72, 0.78),
                    (x, y, 0.76),
                    mats["concrete"],
                    0.10,
                    component="patio_planter",
                ),
                c(
                    f"RETAILSTRIP_PatioPlant_{planter_index}",
                    0.24,
                    0.72,
                    (x, y, 1.48),
                    mats["prairie"],
                    vertices=10,
                    component="patio_planter",
                ),
            ]
        )
    return objects


def add_roof_and_rear_service(
    mats: dict[str, bpy.types.Material],
    *,
    detailed: bool,
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = [
        b(
            "RETAILSTRIP_MainRoofMembrane",
            (59.2, 17.2, 0.18),
            (-2.0, 0.0, 5.55),
            mats["roof"],
            0.025,
            component="single_ply_membrane_roof",
        ),
        b(
            "RETAILSTRIP_RearParapet",
            (60.0, 0.52, 0.72),
            (-2.0, REAR_Y - 0.24, 5.73),
            mats["charcoal"],
            0.018,
            component="rear_charcoal_parapet",
        ),
        b(
            "RETAILSTRIP_LeftAnchorRearHead",
            (9.0, 0.58, 1.55),
            (BAY_CENTRES[0], REAR_Y - 0.26, 6.42),
            mats["brick"],
            0.018,
            component="raised_anchor_brick_return",
        ),
        b(
            "RETAILSTRIP_RightParapetReturn",
            (0.50, 17.0, 0.72),
            (BAY_BOUNDS[-1] - 0.25, 0.0, 5.73),
            mats["charcoal"],
            0.018,
            component="restaurant_parapet_return",
        ),
    ]
    if detailed:
        for seam_index, y in enumerate((-6.0, -2.0, 2.0, 6.0)):
            objects.append(
                b(
                    f"RETAILSTRIP_RoofWeldSeam_{seam_index}",
                    (58.6, 0.035, 0.014),
                    (-2.0, y, 5.65),
                    mats["stainless"],
                    component="roof_membrane_heat_weld_seam",
                )
            )

    # One rooftop unit is centered over each tenant. Count and location are
    # identical in the aerial reference and the deterministic model.
    for hvac_index, x in enumerate(BAY_CENTRES):
        objects.extend(
            [
                b(
                    f"RETAILSTRIP_RooftopHVAC_{hvac_index}",
                    (2.05, 1.55, 0.78),
                    (x, 2.25, 6.10),
                    mats["hvac"],
                    0.045,
                    component="rooftop_hvac_unit",
                    count_authority="exactly_seven_tenant_aligned_hvac_units",
                ),
                b(
                    f"RETAILSTRIP_HVACRoofCurb_{hvac_index}",
                    (2.25, 1.75, 0.18),
                    (x, 2.25, 5.72),
                    mats["black"],
                    0.025,
                    component="rooftop_hvac_curb",
                ),
                c(
                    f"RETAILSTRIP_HVACFan_{hvac_index}",
                    0.38,
                    0.055,
                    (x, 2.25, 6.53),
                    mats["black"],
                    vertices=32,
                    component="rooftop_hvac_fan",
                ),
            ]
        )
        if detailed:
            for grille_index in range(5):
                objects.append(
                    b(
                        f"RETAILSTRIP_HVACGrille_{hvac_index}_{grille_index}",
                        (1.55, 0.035, 0.055),
                        (x, 1.455, 5.88 + grille_index * 0.12),
                        mats["black"],
                        component="rooftop_hvac_grille",
                    )
                )
    for exhaust_index, x in enumerate((22.2, 25.7)):
        objects.extend(
            [
                c(
                    f"RETAILSTRIP_RestaurantExhaust_{exhaust_index}",
                    0.28,
                    0.72,
                    (x, 5.45, 6.05),
                    mats["hvac"],
                    vertices=28,
                    component="restaurant_roof_exhaust",
                    count_authority="exactly_two_restaurant_exhaust_fans",
                ),
                c(
                    f"RETAILSTRIP_RestaurantExhaustCap_{exhaust_index}",
                    0.42,
                    0.16,
                    (x, 5.45, 6.47),
                    mats["stainless"],
                    vertices=28,
                    component="restaurant_roof_exhaust",
                ),
            ]
        )

    # Seven aligned rear service zones: one anchor double door, six single
    # tenant doors, plus rational utilities rather than arbitrary detail.
    for service_index, x in enumerate(BAY_CENTRES):
        if service_index == 0:
            for leaf_index, dx in enumerate((-0.62, 0.62)):
                objects.append(
                    b(
                        f"RETAILSTRIP_AnchorServiceDoorLeaf_{leaf_index}",
                        (1.16, 0.08, 2.65),
                        (x + dx, REAR_Y + 0.035, 1.77),
                        mats["black"],
                        0.025,
                        component="anchor_double_service_door",
                    )
                )
        else:
            objects.append(
                b(
                    f"RETAILSTRIP_RearServiceDoor_{service_index}",
                    (1.18, 0.08, 2.50),
                    (x, REAR_Y + 0.035, 1.70),
                    mats["black"],
                    0.025,
                    component="tenant_service_door",
                    count_authority="six_single_tenant_service_doors",
                )
            )
        door_width = 2.45 if service_index == 0 else 1.48
        objects.extend(
            [
                b(
                    f"RETAILSTRIP_RearDoorHead_{service_index}",
                    (door_width, 0.14, 0.11),
                    (x, REAR_Y + 0.11, 3.08),
                    mats["black"],
                    0.012,
                    component="recessed_rear_service_door_frame",
                ),
                b(
                    f"RETAILSTRIP_RearDoorJambLeft_{service_index}",
                    (0.10, 0.14, 2.55),
                    (x - door_width * 0.5, REAR_Y + 0.11, 1.78),
                    mats["black"],
                    0.012,
                    component="recessed_rear_service_door_frame",
                ),
                b(
                    f"RETAILSTRIP_RearDoorJambRight_{service_index}",
                    (0.10, 0.14, 2.55),
                    (x + door_width * 0.5, REAR_Y + 0.11, 1.78),
                    mats["black"],
                    0.012,
                    component="recessed_rear_service_door_frame",
                ),
                c(
                    f"RETAILSTRIP_RearDoorPull_{service_index}",
                    0.035,
                    0.42,
                    (
                        x + (0.34 if service_index else 0.42),
                        REAR_Y + 0.23,
                        1.72,
                    ),
                    mats["stainless"],
                    vertices=14,
                    component="rear_service_door_hardware",
                ),
            ]
        )
        objects.extend(
            [
                b(
                    f"RETAILSTRIP_RearWallLight_{service_index}",
                    (0.34, 0.18, 0.22),
                    (x, REAR_Y + 0.14, 3.62),
                    mats["black"],
                    0.022,
                    component="rear_service_wall_light",
                ),
                b(
                    f"RETAILSTRIP_RearWallLightLens_{service_index}",
                    (0.22, 0.035, 0.10),
                    (x, REAR_Y + 0.25, 3.59),
                    mats["warm_light"],
                    0.012,
                    component="rear_service_wall_light",
                ),
                b(
                    f"RETAILSTRIP_BlankAddressPlaque_{service_index}",
                    (0.42, 0.035, 0.28),
                    (x + 1.05, REAR_Y + 0.25, 2.30),
                    mats["meter"],
                    0.012,
                    component="blank_service_address_plaque",
                ),
            ]
        )
        if service_index > 0:
            objects.extend(
                [
                    b(
                        f"RETAILSTRIP_MeterBackboard_{service_index}",
                        (1.10, 0.10, 0.78),
                        (x - 1.65, REAR_Y + 0.16, 1.45),
                        mats["meter"],
                        0.018,
                        component="tenant_meter_bank",
                    ),
                    c(
                        f"RETAILSTRIP_GasMeter_{service_index}",
                        0.18,
                        0.18,
                        (x - 1.65, REAR_Y + 0.30, 1.48),
                        mats["stainless"],
                        vertices=20,
                        component="tenant_meter_bank",
                    ),
                ]
            )
    for louver_index, x in enumerate((21.6, 24.0, 26.4)):
        objects.append(
            b(
                f"RETAILSTRIP_RestaurantRearLouver_{louver_index}",
                (1.35, 0.10, 0.82),
                (x, REAR_Y + 0.15, 3.15),
                mats["black"],
                0.018,
                component="restaurant_rear_mechanical_louver",
            )
        )
        if detailed:
            for blade_index in range(6):
                objects.append(
                    b(
                        f"RETAILSTRIP_LouverBlade_{louver_index}_{blade_index}",
                        (1.20, 0.055, 0.035),
                        (x, REAR_Y + 0.23, 2.85 + blade_index * 0.115),
                        mats["stainless"],
                        component="restaurant_rear_mechanical_louver",
                    )
                )
    for drain_index, x in enumerate((-22.8, -6.0, 10.8, 27.0)):
        objects.extend(
            [
                b(
                    f"RETAILSTRIP_RearScupper_{drain_index}",
                    (0.38, 0.20, 0.18),
                    (x, REAR_Y + 0.14, 5.52),
                    mats["black"],
                    0.015,
                    component="roof_scupper",
                ),
                c(
                    f"RETAILSTRIP_RearDownspout_{drain_index}",
                    0.065,
                    4.70,
                    (x, REAR_Y + 0.16, 2.80),
                    mats["black"],
                    vertices=16,
                    component="roof_downspout",
                ),
            ]
        )

    # Matching brick/steel enclosure holds exactly two bins and terminates the
    # service elevation cleanly.
    enclosure_centre_x = 31.45
    enclosure_centre_y = 6.85
    objects.extend(
        [
            b(
                "RETAILSTRIP_DumpsterEnclosureLeftPier",
                (0.55, 3.60, 2.25),
                (28.65, enclosure_centre_y, 1.49),
                mats["brick"],
                0.025,
                component="screened_two_bin_enclosure",
            ),
            b(
                "RETAILSTRIP_DumpsterEnclosureRightPier",
                (0.55, 3.60, 2.25),
                (34.25, enclosure_centre_y, 1.49),
                mats["brick"],
                0.025,
                component="screened_two_bin_enclosure",
            ),
            b(
                "RETAILSTRIP_DumpsterEnclosureRear",
                (5.60, 0.24, 2.10),
                (enclosure_centre_x, 8.55, 1.42),
                mats["service"],
                0.018,
                component="screened_two_bin_enclosure",
            ),
            b(
                "RETAILSTRIP_DumpsterGateLeft",
                (2.65, 0.18, 1.95),
                (30.08, 5.10, 1.34),
                mats["black"],
                0.018,
                component="screened_two_bin_enclosure",
            ),
            b(
                "RETAILSTRIP_DumpsterGateRight",
                (2.65, 0.18, 1.95),
                (32.82, 5.10, 1.34),
                mats["black"],
                0.018,
                component="screened_two_bin_enclosure",
            ),
        ]
    )
    for bin_index, x in enumerate((30.35, 32.55)):
        objects.extend(
            [
                b(
                    f"RETAILSTRIP_DumpsterBin_{bin_index}",
                    (1.72, 1.32, 1.28),
                    (x, 7.05, 1.02),
                    mats["service"],
                    0.08,
                    component="screened_refuse_bin",
                    count_authority="exactly_two_screened_refuse_bins",
                ),
                b(
                    f"RETAILSTRIP_DumpsterLid_{bin_index}",
                    (1.82, 1.42, 0.15),
                    (x, 7.05, 1.70),
                    mats["black"],
                    0.05,
                    component="screened_refuse_bin",
                ),
            ]
        )
    return objects


def build_assembled(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    objects.extend(add_site(mats, detailed=True))
    objects.extend(add_shell(mats, detailed=True))
    objects.extend(add_canopy(mats, detailed=True))
    objects.extend(add_patio(mats, detailed=True))
    objects.extend(add_roof_and_rear_service(mats, detailed=True))
    return objects


def build_floor_module(
    mats: dict[str, bpy.types.Material],
    variant: str,
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = [
        b(
            f"RETAILSTRIPKIT_FloorSlab_{variant}",
            (BUILDING_WIDTH, BUILDING_DEPTH, 0.20),
            (-2.0, 0.0, 0.10),
            mats["concrete"],
            component="retail_floor_module_slab",
        ),
        b(
            f"RETAILSTRIPKIT_RearWall_{variant}",
            (BUILDING_WIDTH, 0.36, FLOOR_HEIGHT - 0.20),
            (-2.0, REAR_Y - 0.18, FLOOR_HEIGHT * 0.5 + 0.10),
            mats["service"],
            component="retail_floor_module_rear",
        ),
        b(
            f"RETAILSTRIPKIT_LeftReturn_{variant}",
            (0.36, BUILDING_DEPTH, FLOOR_HEIGHT - 0.20),
            (BAY_BOUNDS[0] + 0.18, 0.0, FLOOR_HEIGHT * 0.5 + 0.10),
            mats["brick"],
            component="retail_floor_module_corner_return",
        ),
        b(
            f"RETAILSTRIPKIT_RightReturn_{variant}",
            (0.36, BUILDING_DEPTH, FLOOR_HEIGHT - 0.20),
            (BAY_BOUNDS[-1] - 0.18, 0.0, FLOOR_HEIGHT * 0.5 + 0.10),
            mats["brick"],
            component="retail_floor_module_corner_return",
        ),
    ]
    door_offset = {"typical_a": 0.0, "typical_b": -0.55, "typical_c": 0.55}[variant]
    for boundary_index, x in enumerate(BAY_BOUNDS):
        objects.append(
            b(
                f"RETAILSTRIPKIT_Pilaster_{variant}_{boundary_index}",
                (0.60, 0.66, FLOOR_HEIGHT - 0.20),
                (x, FRONT_Y + 0.18, FLOOR_HEIGHT * 0.5 + 0.10),
                mats["brick"],
                0.018,
                component="retail_floor_module_pilaster",
            )
        )
    for bay_index, (x0, x1) in enumerate(zip(BAY_BOUNDS, BAY_BOUNDS[1:])):
        centre = (x0 + x1) * 0.5
        inner_width = x1 - x0 - 0.78
        objects.extend(
            [
                b(
                    f"RETAILSTRIPKIT_Glass_{variant}_{bay_index}",
                    (inner_width, 0.055, 3.45),
                    (centre, FRONT_Y - 0.02, 2.00),
                    mats["glass"],
                    0.006,
                    component="physical_low_e_storefront_pane",
                ),
                b(
                    f"RETAILSTRIPKIT_Sill_{variant}_{bay_index}",
                    (inner_width, 0.16, 0.11),
                    (centre, FRONT_Y - 0.12, 0.30),
                    mats["black"],
                    component="retail_floor_module_frame",
                ),
                b(
                    f"RETAILSTRIPKIT_Head_{variant}_{bay_index}",
                    (inner_width, 0.22, 0.22),
                    (centre, FRONT_Y - 0.08, 3.77),
                    mats["black"],
                    component="retail_floor_module_frame",
                ),
                b(
                    f"RETAILSTRIPKIT_Transom_{variant}_{bay_index}",
                    (inner_width, 0.16, 0.09),
                    (centre, FRONT_Y - 0.12, 3.05),
                    mats["black"],
                    component="retail_floor_module_frame",
                ),
                b(
                    f"RETAILSTRIPKIT_DoorSeam_{variant}_{bay_index}",
                    (0.09, 0.17, 2.80),
                    (centre + door_offset, FRONT_Y - 0.13, 1.70),
                    mats["black"],
                    component="retail_floor_module_entry",
                ),
                b(
                    f"RETAILSTRIPKIT_OccupiedDepth_{variant}_{bay_index}",
                    (inner_width - 0.3, 0.06, 3.10),
                    (centre, 5.85, 1.92),
                    mats["interior"],
                    component="registered_occupied_depth_underlay",
                ),
            ]
        )
        for mullion_index, x in enumerate(
            (x0 + 0.39, centre - 1.08, centre + door_offset, centre + 1.08, x1 - 0.39)
        ):
            objects.append(
                b(
                    f"RETAILSTRIPKIT_Mullion_{variant}_{bay_index}_{mullion_index}",
                    (0.09, 0.16, 3.50),
                    (x, FRONT_Y - 0.12, 2.00),
                    mats["black"],
                    component="retail_floor_module_frame",
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
        objects.extend(add_site(mats, detailed=False))
        objects.append(
            b(
                "RETAILSTRIPKIT_BuildingPodium",
                (BUILDING_WIDTH, BUILDING_DEPTH, PODIUM_HEIGHT),
                (-2.0, 0.0, PODIUM_HEIGHT * 0.5),
                mats["concrete"],
                component="retail_building_podium",
            )
        )
    elif role == "floor":
        height = FLOOR_HEIGHT
        objects.extend(build_floor_module(mats, variant))
    elif role == "crown":
        height = CROWN_HEIGHT
        anchor_centre = BAY_CENTRES[0]
        inline_centre = (BAY_BOUNDS[-1] + BAY_BOUNDS[1]) * 0.5
        inline_width = BAY_BOUNDS[-1] - BAY_BOUNDS[1]
        objects.extend(
            [
                b(
                    "RETAILSTRIPKIT_AnchorCrown",
                    (9.0, 18.0, CROWN_HEIGHT),
                    (anchor_centre, 0.0, CROWN_HEIGHT * 0.5),
                    mats["brick"],
                    0.018,
                    component="raised_anchor_crown",
                ),
                b(
                    "RETAILSTRIPKIT_InlineParapetCrown",
                    (inline_width, 18.0, 1.62),
                    (inline_centre, 0.0, 0.81),
                    mats["charcoal"],
                    0.018,
                    component="continuous_charcoal_crown",
                ),
                b(
                    "RETAILSTRIPKIT_CanopyCrown",
                    (60.8, 2.90, 0.22),
                    (-2.0, -10.35, 0.50),
                    mats["black"],
                    0.025,
                    component="continuous_thin_black_steel_canopy",
                ),
                b(
                    "RETAILSTRIPKIT_CanopySoffit",
                    (60.48, 2.58, 0.10),
                    (-2.0, -10.35, 0.34),
                    mats["cedar"],
                    component="continuous_warm_cedar_soffit",
                ),
                b(
                    "RETAILSTRIPKIT_PatioPergolaBeamOuter",
                    (0.30, 8.15, 0.34),
                    (34.0, -7.32, 0.72),
                    mats["patio_wood"],
                    component="integrated_patio_pergola",
                ),
            ]
        )
        for fin_index in range(14):
            y = -11.2 + fin_index * 0.60
            objects.append(
                b(
                    f"RETAILSTRIPKIT_PergolaFin_{fin_index}",
                    (6.25, 0.16, 0.30),
                    (31.32, y, 0.96),
                    mats["patio_wood"],
                    component="integrated_patio_pergola",
                )
            )
        for bay_index, centre in enumerate(BAY_CENTRES):
            sign_z = 1.62 if bay_index == 0 else 0.85
            objects.append(
                b(
                    f"RETAILSTRIPKIT_AbstractSign_{bay_index}",
                    (3.7, 0.16, 0.62),
                    (centre, FRONT_Y - 0.20, sign_z),
                    mats["signs"][bay_index],
                    0.025,
                    component="abstract_non_text_tenant_identity",
                )
            )
    elif role == "roof":
        height = ROOF_HEIGHT
        objects.append(
            b(
                "RETAILSTRIPKIT_RoofMembrane",
                (59.2, 17.2, 0.18),
                (-2.0, 0.0, 0.09),
                mats["roof"],
                0.025,
                component="single_ply_membrane_roof",
            )
        )
        for hvac_index, x in enumerate(BAY_CENTRES):
            objects.extend(
                [
                    b(
                        f"RETAILSTRIPKIT_HVAC_{hvac_index}",
                        (2.05, 1.55, 0.78),
                        (x, 2.25, 0.96),
                        mats["hvac"],
                        0.035,
                        component="rooftop_hvac_unit",
                    ),
                    b(
                        f"RETAILSTRIPKIT_HVACBase_{hvac_index}",
                        (2.25, 1.75, 0.18),
                        (x, 2.25, 0.30),
                        mats["black"],
                        component="rooftop_hvac_curb",
                    ),
                ]
            )
        for exhaust_index, x in enumerate((22.2, 25.7)):
            objects.append(
                c(
                    f"RETAILSTRIPKIT_Exhaust_{exhaust_index}",
                    0.28,
                    1.10,
                    (x, 5.45, 0.82),
                    mats["hvac"],
                    vertices=24,
                    component="restaurant_roof_exhaust",
                )
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
        "allowed_levels": [0, 1],
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
        "MAT_W10_RETAIL_PresentationRoad",
        (0.050, 0.052, 0.052, 1.0),
        0.90,
    )
    parking_marking = material(
        "MAT_W10_RETAIL_PresentationParkingMarking",
        (0.74, 0.75, 0.71, 1.0),
        0.76,
    )
    context: list[bpy.types.Object] = [
        box(
            "PRESENTATION_RetailPrairieGround",
            (130.0, 110.0, 0.18),
            (0.0, 0.0, -0.18),
            mats["prairie"],
            0.03,
        ),
        box(
            "PRESENTATION_RetailParkingApron",
            (96.0, 31.0, 0.17),
            (0.0, -28.3, -0.02),
            mats["asphalt"],
            0.025,
        ),
        box(
            "PRESENTATION_RetailRoad",
            (130.0, 11.0, 0.18),
            (0.0, -49.0, -0.02),
            road,
            0.025,
        ),
    ]
    for bay_index in range(22):
        x = -44.0 + bay_index * 4.2
        context.append(
            box(
                f"PRESENTATION_ParkingLine_{bay_index:02d}",
                (0.075, 5.8, 0.022),
                (x, -18.5, 0.08),
                parking_marking,
            )
        )
    for row_index, y in enumerate((-20.9, -35.6)):
        context.append(
            box(
                f"PRESENTATION_ParkingCrossLine_{row_index}",
                (92.0, 0.075, 0.022),
                (0.0, y, 0.08),
                parking_marking,
            )
        )
    for island_index, x in enumerate((-47.0, 47.0)):
        context.extend(
            [
                box(
                    f"PRESENTATION_ParkingIsland_{island_index}",
                    (4.0, 9.0, 0.28),
                    (x, -26.0, 0.06),
                    mats["concrete"],
                    0.38,
                ),
                box(
                    f"PRESENTATION_ParkingIslandPlanting_{island_index}",
                    (3.2, 8.2, 0.20),
                    (x, -26.0, 0.25),
                    mats["prairie"],
                    0.34,
                ),
            ]
        )
    for plant_index in range(54):
        x = -61.0 + plant_index * 2.28
        y = 18.5 + math.sin(plant_index * 1.37) * 2.0
        height = 0.52 + 0.35 * ((plant_index * 7) % 5) / 4
        context.append(
            cylinder(
                f"PRESENTATION_PrairieGrass_{plant_index:02d}",
                0.065,
                height,
                (x, y, height * 0.5),
                mats["prairie"],
                vertices=7,
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
    scene.view_settings.exposure = 0.28
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
    background.inputs["Strength"].default_value = 0.82
    coordinates = nodes.new("ShaderNodeTexCoord")
    separate = nodes.new("ShaderNodeSeparateXYZ")
    gradient = nodes.new("ShaderNodeValToRGB")
    gradient.color_ramp.elements[0].position = 0.0
    gradient.color_ramp.elements[0].color = (0.36, 0.64, 0.98, 1.0)
    gradient.color_ramp.elements[1].position = 0.68
    gradient.color_ramp.elements[1].color = (0.055, 0.22, 0.58, 1.0)
    links.new(coordinates.outputs["Normal"], separate.inputs["Vector"])
    links.new(separate.outputs["Z"], gradient.inputs["Fac"])
    links.new(gradient.outputs["Color"], background.inputs["Color"])
    links.new(background.outputs["Background"], output.inputs["Surface"])
    bpy.ops.object.light_add(type="SUN", location=(-52.0, -72.0, 88.0))
    sun = bpy.context.object
    sun.name = "PRESENTATION_RetailStripSun"
    sun.data.energy = 2.35
    sun.data.color = (1.0, 0.86, 0.70)
    sun.data.angle = math.radians(5.0)
    sun.rotation_euler = (
        Vector((-3.0, 0.0, 3.0)) - sun.location
    ).to_track_quat("-Z", "Y").to_euler()
    bpy.ops.object.light_add(type="AREA", location=(-3.0, -31.0, 13.0))
    fill = bpy.context.object
    fill.name = "PRESENTATION_RetailFacadeFill"
    fill.data.energy = 1700.0
    fill.data.shape = "RECTANGLE"
    fill.data.size = 52.0
    fill.data.size_y = 10.0
    fill.rotation_euler = (
        Vector((-3.0, -7.0, 2.8)) - fill.location
    ).to_track_quat("-Z", "Y").to_euler()
    bpy.ops.object.light_add(type="AREA", location=(-2.0, 4.7, 3.4))
    interior = bpy.context.object
    interior.name = "PRESENTATION_RetailInteriorFill"
    interior.data.energy = 1250.0
    interior.data.color = (1.0, 0.55, 0.24)
    interior.data.shape = "RECTANGLE"
    interior.data.size = 48.0
    interior.data.size_y = 5.0
    interior.rotation_euler = (
        Vector((-2.0, -8.2, 2.0)) - interior.location
    ).to_track_quat("-Z", "Y").to_euler()
    bpy.ops.object.light_add(type="AREA", location=(-2.0, 0.0, 4.05))
    ceiling_fill = bpy.context.object
    ceiling_fill.name = "PRESENTATION_RetailInteriorCeilingWash"
    ceiling_fill.data.energy = 900.0
    ceiling_fill.data.color = (1.0, 0.62, 0.32)
    ceiling_fill.data.shape = "RECTANGLE"
    ceiling_fill.data.size = 52.0
    ceiling_fill.data.size_y = 14.0
    ceiling_fill.rotation_euler = (
        Vector((-2.0, 0.0, 0.3)) - ceiling_fill.location
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
        "preview": ((-54.0, -62.0, 4.2), (-1.0, -2.0, 2.9), 48),
        "street": ((0.0, -78.0, 5.2), (-2.0, -4.0, 3.0), 52),
        "front_corner_oblique": ((-56.0, -53.0, 12.5), (-2.0, -2.0, 3.1), 54),
        "rear_corner_oblique": ((49.0, 39.0, 15.0), (-1.0, 5.0, 3.0), 58),
        "aerial": ((-52.0, -44.0, 49.0), (-2.0, 0.0, 2.6), 56),
        "facade_close": ((-8.0, -27.0, 5.2), (-6.0, -8.6, 2.8), 64),
        "storefront_close": ((3.0, -20.0, 3.9), (2.0, -8.7, 2.15), 69),
        "entry_close": ((-17.5, -18.0, 3.8), (-18.8, -8.7, 2.0), 72),
        "anchor_close": ((-43.0, -29.0, 9.0), (-27.5, -7.5, 4.1), 65),
        "patio_close": ((45.0, -26.0, 7.5), (30.2, -7.0, 2.5), 66),
        "service_close": ((39.0, 28.0, 7.5), (20.0, 8.2, 2.6), 64),
        "roof_close": ((-32.0, -2.0, 30.0), (-2.0, 1.0, 4.6), 62),
        "context": ((61.0, -72.0, 31.0), (-2.0, -1.0, 3.0), 58),
    }
    pilot = {
        "preview",
        "front_corner_oblique",
        "aerial",
        "storefront_close",
        "patio_close",
        "service_close",
        "roof_close",
    }
    if view_set == "preview":
        selected = {"preview"}
    elif view_set == "pilot":
        selected = pilot
    elif view_set in views:
        selected = {view_set}
    else:
        selected = set(views)
    # Blender's real-time transmission path makes a thin exported pane behave
    # like a thick tinted solid in proof renders. Temporarily use alpha-only
    # optical glazing so the modeled occupied depth can be judged. The GLB was
    # exported before this point and retains the physical low-E transmission.
    glass_snapshots: list[
        tuple[bpy.types.Material, bpy.types.Node, float, float, str]
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
        glass_snapshots.append(
            (
                mat,
                bsdf,
                float(bsdf.inputs["Alpha"].default_value),
                float(transmission.default_value) if transmission else 0.0,
                getattr(mat, "surface_render_method", "DITHERED"),
            )
        )
        bsdf.inputs["Alpha"].default_value = 0.08
        mat.diffuse_color = (*tuple(mat.diffuse_color)[:3], 0.08)
        if transmission:
            transmission.default_value = 0.0
        if hasattr(mat, "surface_render_method"):
            mat.surface_render_method = "BLENDED"

    renders: list[str] = []
    try:
        for role, (location, target, lens) in views.items():
            if role not in selected:
                continue
            aim_camera(location, target, lens)
            scene = bpy.context.scene
            scene.render.filepath = str(folder / f"{FAMILY}_{role}.png")
            bpy.ops.render.render(write_still=True)
            renders.append(f"{FAMILY}_{role}.png")
    finally:
        for mat, bsdf, alpha, transmission_value, method in glass_snapshots:
            bsdf.inputs["Alpha"].default_value = alpha
            transmission = bsdf.inputs.get("Transmission Weight")
            if transmission:
                transmission.default_value = transmission_value
            if hasattr(mat, "surface_render_method"):
                mat.surface_render_method = method
            mat.diffuse_color = (*tuple(mat.diffuse_color)[:3], 1.0)
        delete_objects(context)
    return renders


def footprint_contract() -> dict:
    rectangle = {
        "recommendedWidth_m": [32.0, 100.0],
        "recommendedDepth_m": [14.0, 30.0],
        "recommendedFloors": [1, 2],
        "preferredBayMultiple_m": 8.4,
    }
    l_shape = {
        "recommendedWidth_m": [50.0, 126.0],
        "recommendedDepth_m": [28.0, 70.0],
        "recommendedFloors": [1, 2],
        "wingDepth_m": [14.0, 24.0],
        "preferredBayMultiple_m": 8.4,
    }
    u_shape = {
        "recommendedWidth_m": [62.0, 142.0],
        "recommendedDepth_m": [34.0, 82.0],
        "recommendedFloors": [1, 2],
        "wingDepth_m": [14.0, 24.0],
        "minimumCourtyard_m": 18.0,
        "preferredBayMultiple_m": 8.4,
    }
    return {
        "preferredProfiles": ["rectangle", "l_shape", "u_shape"],
        "minimumPreferredProfiles": 3,
        "profileRationale": (
            "The identity is a shallow bar of complete tenant modules. A "
            "rectangle preserves the canonical seven-bay frontage; L- and "
            "U-shaped drawings turn complete occupied bars at corners while "
            "keeping storefront, canopy, rear-service and roof-unit datums."
        ),
        "fixedLandmarkScaleBand": {
            "scaleMin": 0.72,
            "scaleMax": 1.32,
            "maxAxisRatio": 1.28,
        },
        "recommendedWidth_m": [32.0, 100.0],
        "recommendedDepth_m": [14.0, 30.0],
        "recommendedFloors": [1, 2],
        "wingDepth_m": [14.0, 24.0],
        "preferredBayMultiple_m": 8.4,
        "minimumCourtyard_m": 18.0,
        "profiles": {
            "rectangle": rectangle,
            "l_shape": l_shape,
            "u_shape": u_shape,
        },
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
            "raised_left_anchor_and_entrance",
            "integrated_right_restaurant_corner_and_patio",
        ],
        "repeatable_middle_bays": [1, 2, 3, 4, 5],
        "middle_variants": ["typical_a", "typical_b", "typical_c"],
        "rule": (
            "Repeat complete 8.4 metre tenant bays along the long axis. Keep "
            "the anchor, restaurant end-cap, physical storefront openings, "
            "canopy columns, rear service doors and rooftop units registered "
            "to bay centres; never stretch an individual window or doorway."
        ),
    }
    contract["assembly_contract"] = {
        "fixed": [
            "podium/entrance",
            "corner returns",
            "crown",
            "roof",
            "podium/entrance and complete sidewalk",
            "raised anchor corner returns",
            "restaurant corner and integrated patio",
            "continuous canopy crown",
            "roof membrane and service plant",
        ],
        "repeatable": ["typical_a", "typical_b", "typical_c"],
        "side_elevations": (
            "The public storefront turns into a glazed restaurant end-cap and "
            "brick anchor return, while the rear is a distinct charcoal service "
            "envelope with doors, meter banks, louvers, drains and screened refuse."
        ),
        "elevation_coverage": {
            "front": "seven occupied low-E storefront modules under one canopy",
            "left": "full-height raised russet-brick anchor return",
            "right": "wrapped restaurant glass, aligned pergola and patio rail",
            "rear": "seven service zones, utilities and screened two-bin enclosure",
            "roof": "single-ply membrane, seven HVAC units and two exhaust fans",
        },
        "variation_policy": (
            "Scale the complete bar only inside 0.72–1.32 with an independent-"
            "axis ratio no greater than 1.28. Larger targets use long-axis "
            "streetwall repeat of complete tenant bars, never family_incompatible."
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
        "type": "modular_retail_bar",
        "silhouette": "one_storey_long_bar_with_raised_left_anchor",
        "tenant_modules": 7,
        "raised_anchor_modules": 1,
        "repeatable_inline_modules": 5,
        "restaurant_end_cap_modules": 1,
        "canopy_structural_columns": 8,
        "occupied_storefront_modules": 7,
        "rear_service_zones": 7,
        "rooftop_hvac_units": 7,
        "restaurant_exhaust_fans": 2,
        "patio_pergola_posts": 6,
        "screened_refuse_bins": 2,
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
                "variant_key": "reference_locked",
                "level": 0,
                "z_m": 0.0,
                "height_m": NATIVE_HEIGHT,
            }
        ],
        "footprint_profile": "rectangle",
        "footprint_target": {
            "width_m": NATIVE_WIDTH,
            "depth_m": NATIVE_DEPTH,
            "wing_depth_m": BUILDING_DEPTH,
            "segments": [
                {
                    "id": "seven_tenant_retail_bar",
                    "centre_x_m": -2.0,
                    "centre_y_m": 0.0,
                    "length_m": BUILDING_WIDTH,
                    "thickness_m": BUILDING_DEPTH,
                    "rotation_degrees": 0.0,
                },
                {
                    "id": "integrated_restaurant_patio",
                    "centre_x_m": 31.3,
                    "centre_y_m": -7.3,
                    "length_m": 6.1,
                    "thickness_m": 8.45,
                    "rotation_degrees": 0.0,
                },
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
            "name": "archetype_compiler/generate_wave10_retail_strip_family.py",
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
            "Commercial Strip Mall",
            "Contemporary Retail",
            "Neighbourhood Retail Plaza",
            "Prairie Storefront Bar",
        ],
        "generation_tags": [
            "wave10",
            "standard_building",
            "modular_retail_streetwall",
            "custom_pbr_skin",
            "physical_commercial_glazing",
            "occupied_retail_depth",
            "raised_brick_anchor",
            "continuous_cedar_soffit_canopy",
            "integrated_restaurant_patio",
            "complete_rear_service_envelope",
        ],
        "footprint_compatibility": footprint,
        "coordinate_contract": COORDINATE_CONTRACT,
        "textures": texture_inventory(skin),
        "facade_sheet": facade_sheet_contract(skin),
        "massing_graph": massing_graph,
        "material_budget": {
            "max_assembled_materials": 30,
            "rationale": (
                "Russet brick, charcoal ribbed metal, cedar soffit and pergola, "
                "physical low-E glass, occupied depth, concrete, roof membrane, "
                "service metal, HVAC, rail, hardware, lighting, restrained sign "
                "colours and merchandise remain separate because their distinct "
                "optical response carries the reference identity."
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
            "A raised russet-brick anchor and six smaller occupied tenant bays "
            "sit beneath one thin black canopy with warm cedar soffit, ending "
            "in a glazed restaurant corner and structurally integrated patio."
        ),
        "material_zones": (
            "warm russet modular brick; charcoal-black narrow micro-ribbed metal; "
            "warm cedar linear soffit and pergola; black thermally broken aluminum; "
            "physical neutral low-E glazing with occupied retail depth; light "
            "broom-finished concrete; pale single-ply roof membrane; galvanized "
            "roof plant; dark rear service metal and restrained illuminated signs"
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
                "reference-locked multi-angle ImageGen source pack, six-zone "
                "construction plate, deterministic seven-bay metric geometry, "
                "physical low-E storefronts, modeled occupied depth, integrated "
                "restaurant patio, and complete roof/rear service schedules"
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
                "reference_locked_assembled_bar",
                "seven_physical_tenant_storefronts",
                "integrated_restaurant_patio",
                "complete_rear_service_and_roof",
                "flexible_semantic_stack",
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
        f"[wave10-retail] {FAMILY}: {assembled_triangles} triangles, "
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
    render_views(folder, mats, view_set=view_set)
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
        f"[wave10-retail-render] {FAMILY}: {len(manifest['renders'])} renders"
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
