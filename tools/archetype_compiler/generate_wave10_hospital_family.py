"""Author the Wave 10 Mass-Timber Biophilic Hospital LEGO family.

The canonical assembly is a four-storey U-shaped clinical building.  Two
patient-room wings frame an open healing courtyard, an integrated glazed
glulam atrium closes the rear of the court, and a separate two-bay ambulance
arrival completes the service elevation.  The fallback kit keeps the public
podium, courtyard ends, crown and photovoltaic roof semantic while allowing
two to six occupied levels and complete-bay streetwall repetition.

Run with Blender 5.x from the repository root:

    blender --background --factory-startup --python \
      tools/archetype_compiler/generate_wave10_hospital_family.py -- \
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


FAMILY = "biophilic-healthcare-mass-timber"
ARCHETYPE_ID = "biophilic_healthcare"
VARIANT_ID = "healthcare_mass_timber"
REGIONAL_ALIAS = "regional_hospital_biophilic_wellness"
LABEL = "Biophilic Modern Healthcare — Mass Timber Modern"
GLASS_PROFILE = "timber_station_neutral_low_e"
ATRIUM_GLASS_PROFILE = "low_iron_clear"

WIDTH = 70.0
DEPTH = 50.0
NATIVE_WIDTH = 71.2
NATIVE_DEPTH = 51.2
PODIUM_HEIGHT = 4.80
FLOOR_HEIGHT = 4.00
TYPICAL_FLOORS = 3
CROWN_HEIGHT = 0.45
ROOF_HEIGHT = 4.20
BODY_HEIGHT = PODIUM_HEIGHT + FLOOR_HEIGHT * TYPICAL_FLOORS
TOTAL_HEIGHT = BODY_HEIGHT + CROWN_HEIGHT + ROOF_HEIGHT
WALL_THICKNESS = 0.28

FRONT_Y = -DEPTH / 2.0
REAR_Y = DEPTH / 2.0
LEFT_X = -WIDTH / 2.0
RIGHT_X = WIDTH / 2.0
INNER_LEFT_X = -18.0
INNER_RIGHT_X = 18.0
REAR_BAR_FRONT_Y = 10.0
ATRIUM_FRONT_Y = 8.8
ATRIUM_LEFT_X = -15.2
ATRIUM_RIGHT_X = 15.2


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
    parser.add_argument(
        "--skip-assembled-export",
        action="store_true",
        help="Render a constructed visual iteration without replacing its GLB.",
    )
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
            "MAT_W10_HOSP_HoneyVerticalTimberRainscreen",
            folder,
            near["honey_timber"],
            "honey_timber",
            saturation=1.04,
            value=0.89,
        ),
        "glulam": pbr_material(
            "MAT_W10_HOSP_ExposedHoneyGlulam",
            folder,
            near["glulam"],
            "glulam",
            saturation=1.03,
            value=0.92,
        ),
        "charred": pbr_material(
            "MAT_W10_HOSP_ShouSugiBanClinicalPlinth",
            folder,
            near["charred_timber"],
            "charred_timber",
            saturation=0.62,
            value=0.68,
        ),
        "concrete": pbr_material(
            "MAT_W10_HOSP_PaleMineralPlinth",
            folder,
            near["concrete"],
            "concrete",
            saturation=0.54,
            value=0.93,
        ),
        "living": pbr_material(
            "MAT_W10_HOSP_IntegratedLivingWall",
            folder,
            near["living_wall"],
            "living_wall",
            saturation=1.03,
            value=0.83,
        ),
        "solar": pbr_material(
            "MAT_W10_HOSP_PhotovoltaicAndScreenMetal",
            folder,
            near["solar_metal"],
            "solar_metal",
            metallic=0.58,
            saturation=0.78,
            value=0.70,
        ),
        "paving": pbr_material(
            "MAT_W10_HOSP_CalmForecourtPaving",
            folder,
            near["paving"],
            "paving",
            saturation=0.50,
            value=0.94,
        ),
        "green_roof": pbr_material(
            "MAT_W10_HOSP_MeadowRoof",
            folder,
            near["green_roof"],
            "green_roof",
            saturation=1.10,
            value=0.92,
        ),
        "registered_facade": pbr_material(
            "MAT_W10_HOSP_RegisteredElevationProof",
            folder,
            near["facade"],
            "facade",
            saturation=0.94,
            value=0.97,
        ),
        "patient_glass": profiled_glass_material(
            "MAT_W10_HOSP_ClinicalNeutralLowE",
            GLASS_PROFILE,
            tint="#6f7d7d",
            roughness_scale=1.10,
            transmission_scale=0.92,
        ),
        "atrium_glass": profiled_glass_material(
            "MAT_W10_HOSP_PublicAtriumLowIron",
            ATRIUM_GLASS_PROFILE,
            tint="#c7d0ca",
            roughness_scale=0.90,
            transmission_scale=0.93,
        ),
        "patient_underlay": reference_image_material(
            "MAT_W10_HOSP_RegisteredPatientRoomDepth",
            folder,
            "textures/source/patient-interior-source-v1.png",
            emission_strength=0.040,
        ),
        "atrium_underlay": reference_image_material(
            "MAT_W10_HOSP_RegisteredAtriumDepth",
            folder,
            "textures/source/atrium-interior-source-v1.png",
            emission_strength=0.095,
        ),
        "deep": material(
            "MAT_W10_HOSP_DeepClinicalCavity",
            (0.012, 0.015, 0.015, 1.0),
            0.96,
        ),
        "frame": material(
            "MAT_W10_HOSP_BlackThermalBreakFrame",
            (0.025, 0.028, 0.028, 1.0),
            0.34,
            metallic=0.42,
        ),
        "curtain": material(
            "MAT_W10_HOSP_PaleClinicalCurtain",
            (0.80, 0.78, 0.73, 1.0),
            0.90,
        ),
        "soil": material(
            "MAT_W10_HOSP_PlanterSoil",
            (0.060, 0.045, 0.032, 1.0),
            0.94,
        ),
        "leaf_a": material(
            "MAT_W10_HOSP_FoliageDark",
            (0.055, 0.16, 0.052, 1.0),
            0.88,
        ),
        "leaf_b": material(
            "MAT_W10_HOSP_FoliageMid",
            (0.11, 0.25, 0.075, 1.0),
            0.86,
        ),
        "leaf_c": material(
            "MAT_W10_HOSP_FoliageLight",
            (0.22, 0.36, 0.10, 1.0),
            0.84,
        ),
        "red": material(
            "MAT_W10_HOSP_AmbulanceRed",
            (0.58, 0.020, 0.018, 1.0),
            0.30,
            metallic=0.08,
        ),
        "white": material(
            "MAT_W10_HOSP_AmbulanceWhite",
            (0.80, 0.82, 0.80, 1.0),
            0.36,
            metallic=0.05,
        ),
        "chrome": material(
            "MAT_W10_HOSP_ServiceMetal",
            (0.38, 0.41, 0.42, 1.0),
            0.22,
            metallic=0.86,
        ),
        "water": profiled_glass_material(
            "MAT_W10_HOSP_RainGardenWater",
            ATRIUM_GLASS_PROFILE,
            tint="#48666d",
            roughness_scale=2.40,
            transmission_scale=0.44,
        ),
    }
    for key in ("patient_underlay", "atrium_underlay"):
        for node in mats[key].node_tree.nodes:
            if node.bl_idname == "ShaderNodeTexImage":
                node.extension = "REPEAT"
        mats[key]["glazing_profile"] = GLASS_PROFILE
        mats[key]["source_variant_id"] = VARIANT_ID
    atrium_grade = mats["atrium_underlay"].node_tree.nodes.get(
        "REFERENCE_UNDERLAY_GRADE"
    )
    if atrium_grade:
        atrium_grade.inputs["Saturation"].default_value = 1.04
        atrium_grade.inputs["Value"].default_value = 0.98
    for key in ("patient_glass", "atrium_glass"):
        mats[key]["glazing_lod"] = "always"
        mats[key]["reference_locked"] = True
        mats[key]["source_variant_id"] = VARIANT_ID
    for key in ("leaf_a", "leaf_b", "leaf_c"):
        mats[key].use_backface_culling = False
    mats["registered_facade"]["reference_locked"] = True
    mats["registered_facade"]["source_variant_id"] = VARIANT_ID
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
            f"{name}_Wall_{index:03d}",
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
            f"{name}_Wall_{index:03d}",
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


def leaf_lobe(
    name: str,
    *,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    mat: bpy.types.Material,
) -> bpy.types.Object:
    """Create one low-poly leaf mass without the blocky planter silhouette."""
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=1,
        radius=1.0,
        location=location,
    )
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(mat)
    return obj


def grass_tuft(
    name: str,
    *,
    location: tuple[float, float, float],
    width: float,
    depth: float,
    height: float,
    mat: bpy.types.Material,
    rotation_z: float = 0.0,
) -> bpy.types.Object:
    """Create crossed tapered grass blades instead of geometric green balls."""
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int]] = []
    blade_angles = (0.0, 0.58, 1.18, 1.82, 2.46)
    for index, angle in enumerate(blade_angles):
        blade_height = height * (0.74 + 0.065 * index)
        blade_width = width * (0.18 + 0.018 * (index % 2))
        base_offset = depth * 0.16 * math.sin(index * 1.71)
        lean = width * 0.34 * math.cos(index * 1.37)
        cosine = math.cos(angle)
        sine = math.sin(angle)
        across = Vector((cosine, sine, 0.0))
        forward = Vector((-sine, cosine, 0.0))
        centre = forward * base_offset
        left = centre - across * blade_width
        right = centre + across * blade_width
        tip = centre + forward * lean + Vector((0.0, 0.0, blade_height))
        start = len(vertices)
        vertices.extend([tuple(left), tuple(right), tuple(tip)])
        faces.append((start, start + 1, start + 2))
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler[2] = rotation_z
    obj.data.materials.append(mat)
    return obj


def leaf_sprig(
    name: str,
    *,
    location: tuple[float, float, float],
    axis: str,
    width: float,
    height: float,
    mat: bpy.types.Material,
) -> bpy.types.Object:
    """Create layered ivy leaves that read as foliage, not polyhedra."""
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int, int]] = []
    for index, (offset, scale) in enumerate(
        ((-0.34, 0.78), (0.0, 1.0), (0.31, 0.70))
    ):
        leaf_width = width * scale
        leaf_height = height * (0.76 + 0.12 * (index % 2))
        z = offset * height
        if axis == "y":
            points = [
                (-leaf_width, 0.0, z),
                (0.0, 0.0, z + leaf_height),
                (leaf_width, 0.0, z),
                (0.0, 0.0, z - leaf_height * 0.62),
            ]
        else:
            points = [
                (0.0, -leaf_width, z),
                (0.0, 0.0, z + leaf_height),
                (0.0, leaf_width, z),
                (0.0, 0.0, z - leaf_height * 0.62),
            ]
        start = len(vertices)
        vertices.extend(points)
        faces.append((start, start + 1, start + 2, start + 3))
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.data.materials.append(mat)
    return obj


def add_patient_window_y(
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
    planter: bool = True,
) -> list[bpy.types.Object]:
    inside = -outward_sign
    zc = sill_z + height * 0.5
    pane_y = surface_y + inside * 0.34
    frame_y = pane_y - inside * 0.035
    room_y = surface_y + inside * 0.92
    objects: list[bpy.types.Object] = [
        box(
            f"{name}_RegisteredCareRoomDepth",
            (width - 0.30, 0.025, height - 0.30),
            (centre_x, room_y, zc),
            mats["patient_underlay"],
            0.004,
        ),
        tbox(
            f"{name}_PhysicalClinicalLowEPane",
            (width - 0.20, 0.030, height - 0.20),
            (centre_x, pane_y, zc),
            mats["patient_glass"],
            0.006,
            tile_m=0.85,
        ),
    ]
    jamb = 0.12
    for side in (-1, 1):
        objects.append(
            tbox(
                f"{name}_DeepTimberJamb_{side:+d}",
                (jamb, 0.42, height),
                (
                    centre_x + side * (width * 0.5 - jamb * 0.5),
                    surface_y + inside * 0.17,
                    zc,
                ),
                mats["timber"],
                0.016,
                tile_m=1.0,
            )
        )
    for token, z in (
        ("Sill", sill_z + 0.07),
        ("Head", sill_z + height - 0.07),
    ):
        objects.append(
            tbox(
                f"{name}_DeepTimber{token}",
                (width, 0.42, 0.14),
                (centre_x, surface_y + inside * 0.17, z),
                mats["timber"],
                0.014,
                tile_m=1.0,
            )
        )
    objects.extend(
        [
            tbox(
                f"{name}_CentralMullion",
                (0.085, 0.18, height - 0.18),
                (centre_x, frame_y, zc),
                mats["frame"],
                0.006,
                tile_m=0.55,
            ),
            tbox(
                f"{name}_OperableVentTransom",
                (width - 0.22, 0.18, 0.070),
                (centre_x, frame_y, sill_z + height * 0.73),
                mats["frame"],
                0.006,
                tile_m=0.55,
            ),
        ]
    )
    if sum(ord(value) for value in name + variant) % 3 != 0:
        curtain_x = centre_x + (0.48 if variant == "typical_b" else -0.48)
        objects.append(
            tbox(
                f"{name}_OffsetPrivacyCurtain",
                (0.76, 0.020, height - 0.34),
                (curtain_x, room_y - inside * 0.035, zc),
                mats["curtain"],
                0.004,
                tile_m=0.80,
            )
        )
    if planter:
        planter_y = surface_y + outward_sign * 0.34
        objects.extend(
            [
                tbox(
                    f"{name}_IntegratedPlanter",
                    (width + 0.18, 0.48, 0.34),
                    (centre_x, planter_y, sill_z - 0.08),
                    mats["timber"],
                    0.016,
                    tile_m=1.0,
                ),
                tbox(
                    f"{name}_PlanterSoil",
                    (width - 0.06, 0.34, 0.06),
                    (
                        centre_x,
                        planter_y + outward_sign * 0.02,
                        sill_z + 0.10,
                    ),
                    mats["soil"],
                    0.004,
                    tile_m=0.8,
                ),
            ]
        )
        for index in range(5):
            x = centre_x - width * 0.38 + index * width * 0.19
            height_leaf = 0.24 + 0.035 * ((index + len(name)) % 3)
            objects.append(
                grass_tuft(
                    f"{name}_PlanterGrass_{index}",
                    location=(
                        x,
                        planter_y + outward_sign * 0.06,
                        sill_z + 0.14,
                    ),
                    width=0.19,
                    depth=0.13,
                    height=height_leaf,
                    mat=mats["leaf_b" if index % 2 else "leaf_a"],
                    rotation_z=0.29 * index,
                )
            )
    if sum(ord(value) for value in name) % 2 == 0:
        fin_x = centre_x + width * 0.5 + 0.18
        for index in range(4):
            objects.append(
                tbox(
                    f"{name}_TimberSolarFin_{index}",
                    (0.095, 0.54, height + 0.18),
                    (
                        fin_x + index * 0.18,
                        surface_y + outward_sign * 0.25,
                        zc,
                    ),
                    mats["timber"],
                    0.010,
                    tile_m=0.9,
                )
            )
    return objects


def add_patient_window_x(
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
    planter: bool = True,
) -> list[bpy.types.Object]:
    inside = -outward_sign
    zc = sill_z + height * 0.5
    pane_x = surface_x + inside * 0.34
    frame_x = pane_x - inside * 0.035
    room_x = surface_x + inside * 0.92
    objects: list[bpy.types.Object] = [
        box(
            f"{name}_RegisteredCareRoomDepth",
            (0.025, width - 0.30, height - 0.30),
            (room_x, centre_y, zc),
            mats["patient_underlay"],
            0.004,
        ),
        tbox(
            f"{name}_PhysicalClinicalLowEPane",
            (0.030, width - 0.20, height - 0.20),
            (pane_x, centre_y, zc),
            mats["patient_glass"],
            0.006,
            tile_m=0.85,
        ),
    ]
    jamb = 0.12
    for side in (-1, 1):
        objects.append(
            tbox(
                f"{name}_DeepTimberJamb_{side:+d}",
                (0.42, jamb, height),
                (
                    surface_x + inside * 0.17,
                    centre_y + side * (width * 0.5 - jamb * 0.5),
                    zc,
                ),
                mats["timber"],
                0.016,
                tile_m=1.0,
            )
        )
    for token, z in (
        ("Sill", sill_z + 0.07),
        ("Head", sill_z + height - 0.07),
    ):
        objects.append(
            tbox(
                f"{name}_DeepTimber{token}",
                (0.42, width, 0.14),
                (surface_x + inside * 0.17, centre_y, z),
                mats["timber"],
                0.014,
                tile_m=1.0,
            )
        )
    objects.extend(
        [
            tbox(
                f"{name}_CentralMullion",
                (0.18, 0.085, height - 0.18),
                (frame_x, centre_y, zc),
                mats["frame"],
                0.006,
                tile_m=0.55,
            ),
            tbox(
                f"{name}_OperableVentTransom",
                (0.18, width - 0.22, 0.070),
                (frame_x, centre_y, sill_z + height * 0.73),
                mats["frame"],
                0.006,
                tile_m=0.55,
            ),
        ]
    )
    if sum(ord(value) for value in name + variant) % 3 != 0:
        curtain_y = centre_y + (0.48 if variant == "typical_c" else -0.48)
        objects.append(
            tbox(
                f"{name}_OffsetPrivacyCurtain",
                (0.020, 0.76, height - 0.34),
                (room_x - inside * 0.035, curtain_y, zc),
                mats["curtain"],
                0.004,
                tile_m=0.80,
            )
        )
    if planter:
        planter_x = surface_x + outward_sign * 0.34
        objects.extend(
            [
                tbox(
                    f"{name}_IntegratedPlanter",
                    (0.48, width + 0.18, 0.34),
                    (planter_x, centre_y, sill_z - 0.08),
                    mats["timber"],
                    0.016,
                    tile_m=1.0,
                ),
                tbox(
                    f"{name}_PlanterSoil",
                    (0.34, width - 0.06, 0.06),
                    (
                        planter_x + outward_sign * 0.02,
                        centre_y,
                        sill_z + 0.10,
                    ),
                    mats["soil"],
                    0.004,
                    tile_m=0.8,
                ),
            ]
        )
        for index in range(5):
            y = centre_y - width * 0.38 + index * width * 0.19
            height_leaf = 0.24 + 0.035 * ((index + len(name)) % 3)
            objects.append(
                grass_tuft(
                    f"{name}_PlanterGrass_{index}",
                    location=(
                        planter_x + outward_sign * 0.06,
                        y,
                        sill_z + 0.14,
                    ),
                    width=0.19,
                    depth=0.13,
                    height=height_leaf,
                    mat=mats["leaf_b" if index % 2 else "leaf_a"],
                    rotation_z=math.pi * 0.5 + 0.29 * index,
                )
            )
    if sum(ord(value) for value in name) % 2 == 0:
        fin_y = centre_y + width * 0.5 + 0.18
        for index in range(4):
            objects.append(
                tbox(
                    f"{name}_TimberSolarFin_{index}",
                    (0.54, 0.095, height + 0.18),
                    (
                        surface_x + outward_sign * 0.25,
                        fin_y + index * 0.18,
                        zc,
                    ),
                    mats["timber"],
                    0.010,
                    tile_m=0.9,
                )
            )
    return objects


def add_patient_face_y(
    name: str,
    *,
    x0: float,
    x1: float,
    surface_y: float,
    outward_sign: int,
    mats: dict[str, bpy.types.Material],
    variant: str,
    bay_count: int,
    planter: bool = True,
) -> list[bpy.types.Object]:
    margin = 0.62
    bay = (x1 - x0) / bay_count
    opening_width = min(3.10, bay - 0.72)
    sill = 0.72
    height = 2.72
    centres = [x0 + bay * (index + 0.5) for index in range(bay_count)]
    openings = [
        (
            centre - opening_width * 0.5,
            centre + opening_width * 0.5,
            sill,
            sill + height,
        )
        for centre in centres
    ]
    objects = add_y_wall(
        name,
        x0=x0,
        x1=x1,
        z0=0.0,
        z1=FLOOR_HEIGHT,
        surface_y=surface_y,
        outward_sign=outward_sign,
        openings=openings,
        mat=mats["timber"],
    )
    for index, centre in enumerate(centres):
        objects.extend(
            add_patient_window_y(
                f"{name}_Bay_{index:02d}",
                centre_x=centre,
                sill_z=sill,
                width=opening_width,
                height=height,
                surface_y=surface_y,
                outward_sign=outward_sign,
                mats=mats,
                variant=variant,
                planter=planter,
            )
        )
    for index in range(bay_count + 1):
        x = x0 + bay * index
        objects.append(
            tbox(
                f"{name}_GlulamPier_{index:02d}",
                (0.28 if index in (0, bay_count) else 0.22, 0.54, FLOOR_HEIGHT),
                (
                    x,
                    surface_y + outward_sign * 0.22,
                    FLOOR_HEIGHT * 0.5,
                ),
                mats["glulam"],
                0.018,
                tile_m=1.15,
            )
        )
    objects.extend(
        [
            tbox(
                f"{name}_CLTSlabDatum",
                (x1 - x0 + margin, 0.64, 0.22),
                (
                    (x0 + x1) * 0.5,
                    surface_y + outward_sign * 0.21,
                    0.11,
                ),
                mats["glulam"],
                0.018,
                tile_m=1.15,
            ),
            tbox(
                f"{name}_GlulamHead",
                (x1 - x0 + margin, 0.60, 0.28),
                (
                    (x0 + x1) * 0.5,
                    surface_y + outward_sign * 0.20,
                    FLOOR_HEIGHT - 0.14,
                ),
                mats["glulam"],
                0.018,
                tile_m=1.15,
            ),
        ]
    )
    return objects


def add_patient_face_x(
    name: str,
    *,
    y0: float,
    y1: float,
    surface_x: float,
    outward_sign: int,
    mats: dict[str, bpy.types.Material],
    variant: str,
    bay_count: int,
    planter: bool = True,
) -> list[bpy.types.Object]:
    margin = 0.62
    bay = (y1 - y0) / bay_count
    opening_width = min(3.10, bay - 0.72)
    sill = 0.72
    height = 2.72
    centres = [y0 + bay * (index + 0.5) for index in range(bay_count)]
    openings = [
        (
            centre - opening_width * 0.5,
            centre + opening_width * 0.5,
            sill,
            sill + height,
        )
        for centre in centres
    ]
    objects = add_x_wall(
        name,
        y0=y0,
        y1=y1,
        z0=0.0,
        z1=FLOOR_HEIGHT,
        surface_x=surface_x,
        outward_sign=outward_sign,
        openings=openings,
        mat=mats["timber"],
    )
    for index, centre in enumerate(centres):
        objects.extend(
            add_patient_window_x(
                f"{name}_Bay_{index:02d}",
                centre_y=centre,
                sill_z=sill,
                width=opening_width,
                height=height,
                surface_x=surface_x,
                outward_sign=outward_sign,
                mats=mats,
                variant=variant,
                planter=planter,
            )
        )
    for index in range(bay_count + 1):
        y = y0 + bay * index
        objects.append(
            tbox(
                f"{name}_GlulamPier_{index:02d}",
                (0.54, 0.28 if index in (0, bay_count) else 0.22, FLOOR_HEIGHT),
                (
                    surface_x + outward_sign * 0.22,
                    y,
                    FLOOR_HEIGHT * 0.5,
                ),
                mats["glulam"],
                0.018,
                tile_m=1.15,
            )
        )
    objects.extend(
        [
            tbox(
                f"{name}_CLTSlabDatum",
                (0.64, y1 - y0 + margin, 0.22),
                (
                    surface_x + outward_sign * 0.21,
                    (y0 + y1) * 0.5,
                    0.11,
                ),
                mats["glulam"],
                0.018,
                tile_m=1.15,
            ),
            tbox(
                f"{name}_GlulamHead",
                (0.60, y1 - y0 + margin, 0.28),
                (
                    surface_x + outward_sign * 0.20,
                    (y0 + y1) * 0.5,
                    FLOOR_HEIGHT - 0.14,
                ),
                mats["glulam"],
                0.018,
                tile_m=1.15,
            ),
        ]
    )
    return objects


def add_ground_glazing_y(
    name: str,
    *,
    x0: float,
    x1: float,
    surface_y: float,
    outward_sign: int,
    mats: dict[str, bpy.types.Material],
    bays: int,
    wall_mat: bpy.types.Material,
) -> list[bpy.types.Object]:
    bay = (x1 - x0) / bays
    opening_width = bay - 0.54
    sill = 0.30
    height = 3.72
    centres = [x0 + bay * (index + 0.5) for index in range(bays)]
    openings = [
        (
            centre - opening_width * 0.5,
            centre + opening_width * 0.5,
            sill,
            sill + height,
        )
        for centre in centres
    ]
    objects = add_y_wall(
        name,
        x0=x0,
        x1=x1,
        z0=0.0,
        z1=PODIUM_HEIGHT,
        surface_y=surface_y,
        outward_sign=outward_sign,
        openings=openings,
        mat=wall_mat,
    )
    inside = -outward_sign
    for index, centre in enumerate(centres):
        pane_y = surface_y + inside * 0.30
        room_y = surface_y + inside * 1.10
        zc = sill + height * 0.5
        objects.extend(
            [
                box(
                    f"{name}_Bay_{index:02d}_OccupiedClinicDepth",
                    (opening_width - 0.28, 0.025, height - 0.30),
                    (centre, room_y, zc),
                    mats["atrium_underlay"],
                    0.004,
                ),
                tbox(
                    f"{name}_Bay_{index:02d}_PhysicalLowEPane",
                    (opening_width - 0.18, 0.030, height - 0.18),
                    (centre, pane_y, zc),
                    mats["patient_glass"],
                    0.006,
                    tile_m=0.85,
                ),
            ]
        )
        for side in (-1, 1):
            objects.append(
                tbox(
                    f"{name}_Bay_{index:02d}_FrameJamb_{side:+d}",
                    (0.105, 0.18, height),
                    (
                        centre + side * (opening_width * 0.5 - 0.0525),
                        pane_y - inside * 0.035,
                        zc,
                    ),
                    mats["frame"],
                    0.007,
                    tile_m=0.55,
                )
            )
        for mullion in (1, 2):
            objects.append(
                tbox(
                    f"{name}_Bay_{index:02d}_Mullion_{mullion}",
                    (0.075, 0.18, height - 0.18),
                    (
                        centre - opening_width * 0.5
                        + opening_width * mullion / 3.0,
                        pane_y - inside * 0.035,
                        zc,
                    ),
                    mats["frame"],
                    0.006,
                    tile_m=0.55,
                )
            )
        for token, z in (
            ("Sill", sill + 0.055),
            ("Head", sill + height - 0.055),
        ):
            objects.append(
                tbox(
                    f"{name}_Bay_{index:02d}_{token}",
                    (opening_width, 0.18, 0.11),
                    (centre, pane_y - inside * 0.035, z),
                    mats["frame"],
                    0.007,
                    tile_m=0.55,
                )
            )
    return objects


def add_ground_glazing_x(
    name: str,
    *,
    y0: float,
    y1: float,
    surface_x: float,
    outward_sign: int,
    mats: dict[str, bpy.types.Material],
    bays: int,
    wall_mat: bpy.types.Material,
) -> list[bpy.types.Object]:
    bay = (y1 - y0) / bays
    opening_width = bay - 0.54
    sill = 0.30
    height = 3.72
    centres = [y0 + bay * (index + 0.5) for index in range(bays)]
    openings = [
        (
            centre - opening_width * 0.5,
            centre + opening_width * 0.5,
            sill,
            sill + height,
        )
        for centre in centres
    ]
    objects = add_x_wall(
        name,
        y0=y0,
        y1=y1,
        z0=0.0,
        z1=PODIUM_HEIGHT,
        surface_x=surface_x,
        outward_sign=outward_sign,
        openings=openings,
        mat=wall_mat,
    )
    inside = -outward_sign
    for index, centre in enumerate(centres):
        pane_x = surface_x + inside * 0.30
        room_x = surface_x + inside * 1.10
        zc = sill + height * 0.5
        objects.extend(
            [
                box(
                    f"{name}_Bay_{index:02d}_OccupiedClinicDepth",
                    (0.025, opening_width - 0.28, height - 0.30),
                    (room_x, centre, zc),
                    mats["atrium_underlay"],
                    0.004,
                ),
                tbox(
                    f"{name}_Bay_{index:02d}_PhysicalLowEPane",
                    (0.030, opening_width - 0.18, height - 0.18),
                    (pane_x, centre, zc),
                    mats["patient_glass"],
                    0.006,
                    tile_m=0.85,
                ),
            ]
        )
        for side in (-1, 1):
            objects.append(
                tbox(
                    f"{name}_Bay_{index:02d}_FrameJamb_{side:+d}",
                    (0.18, 0.105, height),
                    (
                        pane_x - inside * 0.035,
                        centre + side * (opening_width * 0.5 - 0.0525),
                        zc,
                    ),
                    mats["frame"],
                    0.007,
                    tile_m=0.55,
                )
            )
        for mullion in (1, 2):
            objects.append(
                tbox(
                    f"{name}_Bay_{index:02d}_Mullion_{mullion}",
                    (0.18, 0.075, height - 0.18),
                    (
                        pane_x - inside * 0.035,
                        centre - opening_width * 0.5
                        + opening_width * mullion / 3.0,
                        zc,
                    ),
                    mats["frame"],
                    0.006,
                    tile_m=0.55,
                )
            )
        for token, z in (
            ("Sill", sill + 0.055),
            ("Head", sill + height - 0.055),
        ):
            objects.append(
                tbox(
                    f"{name}_Bay_{index:02d}_{token}",
                    (0.18, opening_width, 0.11),
                    (pane_x - inside * 0.035, centre, z),
                    mats["frame"],
                    0.007,
                    tile_m=0.55,
                )
            )
    return objects


def add_atrium_band(
    name: str,
    *,
    height: float,
    mats: dict[str, bpy.types.Material],
    ground: bool,
) -> list[bpy.types.Object]:
    width = ATRIUM_RIGHT_X - ATRIUM_LEFT_X
    pane_y = ATRIUM_FRONT_Y - 0.20
    room_y = ATRIUM_FRONT_Y + 1.25
    objects: list[bpy.types.Object] = [
        box(
            f"{name}_RegisteredAtriumOccupiedDepth",
            (width - 1.0, 0.025, height - 0.34),
            (0.0, room_y, height * 0.5),
            mats["atrium_underlay"],
            0.004,
        ),
        tbox(
            f"{name}_ContinuousLowIronCurtainWall",
            (width - 0.34, 0.035, height - 0.16),
            (0.0, pane_y, height * 0.5),
            mats["atrium_glass"],
            0.006,
            tile_m=1.1,
        ),
    ]
    columns = 8
    for index in range(columns + 1):
        x = ATRIUM_LEFT_X + width * index / columns
        objects.append(
            tbox(
                f"{name}_PressureCapVertical_{index:02d}",
                (0.085, 0.16, height),
                (x, pane_y - 0.035, height * 0.5),
                mats["frame"],
                0.006,
                tile_m=0.55,
            )
        )
    for index in range(3):
        z = height * index / 3.0
        objects.append(
            tbox(
                f"{name}_PressureCapHorizontal_{index:02d}",
                (width, 0.16, 0.085),
                (0.0, pane_y - 0.035, z + 0.0425),
                mats["frame"],
                0.006,
                tile_m=0.55,
            )
        )
    for index, x in enumerate((-8.8, 0.0, 8.8)):
        base = (x, ATRIUM_FRONT_Y + 0.45, 0.0)
        top = (
            x + (-1.20 if index == 0 else 1.20 if index == 2 else 0.0),
            ATRIUM_FRONT_Y + 1.2,
            height,
        )
        objects.append(
            round_beam(
                f"{name}_GlulamTreeTrunk_{index}",
                base,
                top,
                0.22,
                mats["glulam"],
                vertices=12,
            )
        )
        if not ground:
            continue
        for branch_index, direction in enumerate((-1, 1)):
            objects.append(
                round_beam(
                    f"{name}_GlulamTreeBranch_{index}_{branch_index}",
                    (top[0], top[1], height * 0.57),
                    (
                        top[0] + direction * 2.1,
                        ATRIUM_FRONT_Y + 1.55,
                        height - 0.10,
                    ),
                    0.16,
                    mats["glulam"],
                    vertices=12,
                )
            )
    if ground:
        door_width = 4.0
        door_height = 3.15
        objects.extend(
            [
                tbox(
                    f"{name}_RecessedPublicDoubleDoor",
                    (door_width, 0.04, door_height),
                    (0.0, pane_y - 0.10, door_height * 0.5),
                    mats["atrium_glass"],
                    0.006,
                    tile_m=0.8,
                ),
                tbox(
                    f"{name}_PublicDoorMullion",
                    (0.09, 0.18, door_height),
                    (0.0, pane_y - 0.14, door_height * 0.5),
                    mats["frame"],
                    0.006,
                    tile_m=0.55,
                ),
                tbox(
                    f"{name}_PublicThreshold",
                    (door_width + 1.0, 1.40, 0.16),
                    (0.0, ATRIUM_FRONT_Y - 0.52, 0.08),
                    mats["concrete"],
                    0.018,
                    tile_m=1.2,
                ),
            ]
        )
    else:
        objects.extend(
            [
                tbox(
                    f"{name}_AtriumBridgeCLTEdge",
                    (width - 1.6, 2.2, 0.26),
                    (0.0, ATRIUM_FRONT_Y + 1.7, 0.22),
                    mats["glulam"],
                    0.018,
                    tile_m=1.15,
                ),
                tbox(
                    f"{name}_AtriumBridgeGlassGuard",
                    (width - 2.1, 0.035, 1.05),
                    (0.0, ATRIUM_FRONT_Y + 0.64, 0.82),
                    mats["atrium_glass"],
                    0.006,
                    tile_m=0.8,
                ),
            ]
        )
    return objects


def add_public_canopy(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    canopy_width = 26.0
    canopy_depth = 17.0
    canopy_y = -0.4
    z = PODIUM_HEIGHT - 0.22
    objects: list[bpy.types.Object] = [
        tbox(
            "HospitalIntegratedGlulamEntryCanopy",
            (canopy_width, canopy_depth, 0.42),
            (0.0, canopy_y, z),
            mats["glulam"],
            0.030,
            tile_m=1.45,
        ),
        tbox(
            "HospitalEntryCanopyDarkFlashing",
            (canopy_width + 0.18, canopy_depth + 0.18, 0.12),
            (0.0, canopy_y, z + 0.27),
            mats["solar"],
            0.012,
            tile_m=1.2,
        ),
    ]
    for x in (-9.8, -3.2, 3.2, 9.8):
        objects.append(
            tbox(
                f"HospitalEntryGlulamPost_{x:+.1f}",
                (0.42, 0.42, PODIUM_HEIGHT - 0.42),
                (x, -7.2, (PODIUM_HEIGHT - 0.42) * 0.5),
                mats["glulam"],
                0.024,
                tile_m=1.2,
            )
        )
        objects.extend(
            [
                round_beam(
                    f"HospitalEntryTreeBraceLeft_{x:+.1f}",
                    (x, -7.2, 2.65),
                    (x - 1.25, -6.2, z - 0.22),
                    0.17,
                    mats["glulam"],
                    vertices=12,
                ),
                round_beam(
                    f"HospitalEntryTreeBraceRight_{x:+.1f}",
                    (x, -7.2, 2.65),
                    (x + 1.25, -6.2, z - 0.22),
                    0.17,
                    mats["glulam"],
                    vertices=12,
                ),
            ]
        )
    return objects


def add_living_wall_strip(
    name: str,
    *,
    axis: str,
    fixed: float,
    lateral: float,
    height: float,
    outward_sign: int,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    if axis == "y":
        panel = tbox(
            f"{name}_LivingWallBacking",
            (2.10, 0.24, height - 0.22),
            (
                lateral,
                fixed + outward_sign * 0.18,
                height * 0.5,
            ),
            mats["living"],
            0.018,
            tile_m=1.0,
        )
    else:
        panel = tbox(
            f"{name}_LivingWallBacking",
            (0.24, 2.10, height - 0.22),
            (
                fixed + outward_sign * 0.18,
                lateral,
                height * 0.5,
            ),
            mats["living"],
            0.018,
            tile_m=1.0,
        )
    objects = [panel]
    for index in range(11):
        z = 0.35 + (height - 0.75) * index / 10.0
        offset = 0.70 * math.sin(index * 1.7)
        if axis == "y":
            location = (
                lateral + offset,
                fixed + outward_sign * 0.34,
                z,
            )
        else:
            location = (
                fixed + outward_sign * 0.34,
                lateral + offset,
                z,
            )
        objects.append(
            leaf_sprig(
                f"{name}_FoliageCluster_{index:02d}",
                location=location,
                axis=axis,
                width=0.17,
                height=0.22,
                mat=mats[("leaf_a", "leaf_b", "leaf_c")[index % 3]],
            )
        )
    return objects


def add_courtyard_tree(
    name: str,
    *,
    x: float,
    y: float,
    height: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    trunk_height = height * 0.56
    trunk = cylinder(
        f"{name}_Trunk",
        0.16,
        trunk_height,
        (x, y, trunk_height * 0.5),
        mats["glulam"],
        vertices=12,
    )
    objects: list[bpy.types.Object] = [trunk]
    for index, (dx, dy, dz, scale) in enumerate(
        (
            (0.0, 0.0, 0.78, 1.0),
            (-0.70, 0.10, 0.69, 0.72),
            (0.62, -0.20, 0.72, 0.76),
            (-0.18, 0.58, 0.73, 0.68),
            (0.18, -0.62, 0.70, 0.70),
        )
    ):
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=2,
            radius=height * 0.19 * scale,
            location=(x + dx, y + dy, height * dz),
        )
        crown = bpy.context.object
        crown.name = f"{name}_LeafCrown_{index}"
        crown.data.materials.append(
            mats[("leaf_a", "leaf_b", "leaf_c")[index % 3]]
        )
        objects.append(crown)
    return objects


def add_healing_courtyard(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = [
        tbox(
            "HospitalCourtyardStonePath",
            (24.0, 27.0, 0.12),
            (0.0, -4.0, 0.06),
            mats["paving"],
            0.018,
            tile_m=1.6,
        ),
        tbox(
            "HospitalCourtyardCentralPlantingBed",
            (9.0, 11.0, 0.48),
            (-5.4, -1.2, 0.24),
            mats["concrete"],
            0.10,
            tile_m=1.2,
        ),
        tbox(
            "HospitalCourtyardCentralSoil",
            (8.5, 10.5, 0.13),
            (-5.4, -1.2, 0.49),
            mats["soil"],
            0.03,
            tile_m=0.8,
        ),
        tbox(
            "HospitalCourtyardRainGardenBasin",
            (6.2, 8.4, 0.34),
            (6.8, 0.8, 0.17),
            mats["concrete"],
            0.12,
            tile_m=1.2,
        ),
        tbox(
            "HospitalCourtyardRainGardenWater",
            (5.8, 8.0, 0.05),
            (6.8, 0.8, 0.37),
            mats["water"],
            0.04,
            tile_m=1.0,
        ),
    ]
    for index, (x, y, height) in enumerate(
        (
            (-7.4, -3.6, 4.7),
            (-3.7, 1.6, 4.2),
            (4.7, -4.1, 3.9),
            (8.1, 4.0, 4.5),
        )
    ):
        objects.extend(
            add_courtyard_tree(
                f"HospitalHealingTree_{index}",
                x=x,
                y=y,
                height=height,
                mats=mats,
            )
        )
    for index in range(34):
        angle = index * 2.399963
        radius = 1.1 + (index % 7) * 0.58
        x = -5.4 + math.cos(angle) * radius
        y = -1.2 + math.sin(angle) * radius * 1.2
        plant_height = 0.35 + 0.09 * (index % 4)
        objects.append(
            tbox(
                f"HospitalTherapeuticPlant_{index:02d}",
                (0.17, 0.17, plant_height),
                (x, y, 0.55 + plant_height * 0.5),
                mats[("leaf_a", "leaf_b", "leaf_c")[index % 3]],
                0.03,
                tile_m=0.5,
            )
        )
    for index, (x, y, rotation) in enumerate(
        (
            (-11.0, -8.4, 0.0),
            (10.8, -7.8, 0.0),
            (-10.5, 6.1, math.pi / 2),
        )
    ):
        bench = tbox(
            f"HospitalCourtyardBenchSeat_{index}",
            (3.0, 0.48, 0.16),
            (x, y, 0.55),
            mats["glulam"],
            0.05,
            tile_m=1.0,
        )
        bench.rotation_euler.z = rotation
        objects.append(bench)
        for end in (-1, 1):
            leg = tbox(
                f"HospitalCourtyardBenchLeg_{index}_{end:+d}",
                (0.16, 0.42, 0.48),
                (x + end * 1.05, y, 0.29),
                mats["frame"],
                0.02,
                tile_m=0.6,
            )
            leg.rotation_euler.z = rotation
            objects.append(leg)
    return objects


def add_ambulance(
    name: str,
    *,
    x: float,
    y: float,
    mats: dict[str, bpy.types.Material],
    facing: int = 1,
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = [
        tbox(
            f"{name}_Body",
            (2.35, 5.5, 2.25),
            (x, y, 1.35),
            mats["white"],
            0.20,
            tile_m=1.4,
        ),
        tbox(
            f"{name}_Cab",
            (2.30, 1.85, 1.62),
            (x, y - facing * 3.05, 1.14),
            mats["white"],
            0.22,
            tile_m=1.2,
        ),
        tbox(
            f"{name}_Windshield",
            (1.88, 0.04, 0.74),
            (x, y - facing * 4.00, 1.55),
            mats["patient_glass"],
            0.04,
            tile_m=0.8,
        ),
        tbox(
            f"{name}_RedStripeLeft",
            (0.08, 5.8, 0.30),
            (x - 1.18, y - 0.12, 1.18),
            mats["red"],
            0.02,
            tile_m=0.7,
        ),
        tbox(
            f"{name}_RedStripeRight",
            (0.08, 5.8, 0.30),
            (x + 1.18, y - 0.12, 1.18),
            mats["red"],
            0.02,
            tile_m=0.7,
        ),
        tbox(
            f"{name}_EmergencyLightBar",
            (1.65, 0.38, 0.16),
            (x, y - facing * 1.9, 2.58),
            mats["red"],
            0.05,
            tile_m=0.6,
        ),
    ]
    for side in (-1, 1):
        for axle_y in (y - facing * 2.55, y + facing * 1.95):
            wheel = cylinder(
                f"{name}_Wheel_{side:+d}_{axle_y:+.1f}",
                0.43,
                0.26,
                (x + side * 1.17, axle_y, 0.49),
                mats["deep"],
                vertices=16,
            )
            wheel.rotation_euler.y = math.radians(90)
            objects.append(wheel)
    return objects


def add_rear_ambulance_arrival(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    service_wall_y = REAR_Y - 4.0
    bay_centres = (22.2, 29.2)
    door_width = 5.7
    door_height = 3.72
    openings = [
        (
            centre - door_width * 0.5,
            centre + door_width * 0.5,
            0.18,
            0.18 + door_height,
        )
        for centre in bay_centres
    ]
    objects = add_y_wall(
        "HospitalRearAmbulanceWall",
        x0=18.0,
        x1=35.0,
        z0=0.0,
        z1=PODIUM_HEIGHT,
        surface_y=service_wall_y,
        outward_sign=1,
        openings=openings,
        mat=mats["charred"],
    )
    for index, centre in enumerate(bay_centres):
        pane_y = service_wall_y - 0.28
        zc = 0.18 + door_height * 0.5
        objects.extend(
            [
                tbox(
                    f"HospitalAmbulanceDoor_{index}_DeepCavity",
                    (door_width - 0.20, 0.12, door_height - 0.18),
                    (centre, pane_y + 0.25, zc),
                    mats["deep"],
                    0.008,
                    tile_m=0.8,
                ),
                tbox(
                    f"HospitalAmbulanceDoor_{index}_PhysicalGlass",
                    (door_width - 0.30, 0.035, door_height - 0.30),
                    (centre, pane_y, zc),
                    mats["patient_glass"],
                    0.006,
                    tile_m=0.8,
                ),
            ]
        )
        for mullion in range(1, 4):
            objects.append(
                tbox(
                    f"HospitalAmbulanceDoor_{index}_Mullion_{mullion}",
                    (0.075, 0.18, door_height - 0.22),
                    (
                        centre - door_width * 0.5 + door_width * mullion / 4.0,
                        pane_y - 0.035,
                        zc,
                    ),
                    mats["frame"],
                    0.006,
                    tile_m=0.55,
                )
            )
        for transom in range(1, 4):
            objects.append(
                tbox(
                    f"HospitalAmbulanceDoor_{index}_Transom_{transom}",
                    (door_width - 0.22, 0.18, 0.075),
                    (
                        centre,
                        pane_y - 0.035,
                        0.18 + door_height * transom / 4.0,
                    ),
                    mats["frame"],
                    0.006,
                    tile_m=0.55,
                )
            )
    canopy_centre = sum(bay_centres) * 0.5
    objects.extend(
        [
            tbox(
                "HospitalAmbulanceIntegratedCanopy",
                (16.4, 4.0, 0.42),
                (canopy_centre, REAR_Y - 2.0, 4.36),
                mats["glulam"],
                0.024,
                tile_m=1.35,
            ),
            tbox(
                "HospitalAmbulanceCanopyDarkRoof",
                (16.6, 4.2, 0.12),
                (canopy_centre, REAR_Y - 2.0, 4.63),
                mats["solar"],
                0.012,
                tile_m=1.1,
            ),
            tbox(
                "HospitalEmergencyRouteStripe",
                (15.8, 4.0, 0.035),
                (canopy_centre, REAR_Y - 2.0, 0.025),
                mats["red"],
                0.010,
                tile_m=1.1,
            ),
        ]
    )
    for x in (18.6, 32.8):
        objects.append(
            tbox(
                f"HospitalAmbulanceCanopyPost_{x:+.1f}",
                (0.42, 0.42, 4.30),
                (x, REAR_Y - 0.55, 2.15),
                mats["glulam"],
                0.022,
                tile_m=1.1,
            )
        )
    objects.extend(
        add_ambulance(
            "HospitalAmbulance",
            x=22.2,
            y=REAR_Y - 5.0,
            mats=mats,
            facing=-1,
        )
    )
    return objects


def build_podium(
    mats: dict[str, bpy.types.Material],
    *,
    include_contract_markers: bool,
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = [
        tbox(
            "HospitalLeftWingGroundSlab",
            (17.0, DEPTH, 0.24),
            (-26.5, 0.0, 0.12),
            mats["concrete"],
            0.025,
            tile_m=1.4,
        ),
        tbox(
            "HospitalRightWingGroundSlab",
            (17.0, DEPTH, 0.24),
            (26.5, 0.0, 0.12),
            mats["concrete"],
            0.025,
            tile_m=1.4,
        ),
        tbox(
            "HospitalRearClinicalGroundSlab",
            (36.0, 15.0, 0.24),
            (0.0, 17.5, 0.12),
            mats["concrete"],
            0.025,
            tile_m=1.4,
        ),
    ]
    objects.extend(
        add_ground_glazing_y(
            "HospitalLeftPublicPodiumFront",
            x0=LEFT_X,
            x1=INNER_LEFT_X,
            surface_y=FRONT_Y,
            outward_sign=-1,
            mats=mats,
            bays=4,
            wall_mat=mats["charred"],
        )
    )
    objects.extend(
        add_ground_glazing_y(
            "HospitalRightPublicPodiumFront",
            x0=INNER_RIGHT_X,
            x1=RIGHT_X,
            surface_y=FRONT_Y,
            outward_sign=-1,
            mats=mats,
            bays=4,
            wall_mat=mats["charred"],
        )
    )
    objects.extend(
        add_ground_glazing_x(
            "HospitalLeftOuterGround",
            y0=FRONT_Y,
            y1=REAR_Y,
            surface_x=LEFT_X,
            outward_sign=-1,
            mats=mats,
            bays=8,
            wall_mat=mats["charred"],
        )
    )
    objects.extend(
        add_ground_glazing_x(
            "HospitalRightOuterGround",
            y0=FRONT_Y,
            y1=REAR_BAR_FRONT_Y,
            surface_x=RIGHT_X,
            outward_sign=1,
            mats=mats,
            bays=6,
            wall_mat=mats["charred"],
        )
    )
    objects.extend(
        add_ground_glazing_x(
            "HospitalLeftCourtyardGround",
            y0=FRONT_Y,
            y1=REAR_BAR_FRONT_Y,
            surface_x=INNER_LEFT_X,
            outward_sign=1,
            mats=mats,
            bays=6,
            wall_mat=mats["charred"],
        )
    )
    objects.extend(
        add_ground_glazing_x(
            "HospitalRightCourtyardGround",
            y0=FRONT_Y,
            y1=REAR_BAR_FRONT_Y,
            surface_x=INNER_RIGHT_X,
            outward_sign=-1,
            mats=mats,
            bays=6,
            wall_mat=mats["charred"],
        )
    )
    objects.extend(
        add_ground_glazing_y(
            "HospitalRearGroundLeft",
            x0=LEFT_X,
            x1=18.0,
            surface_y=REAR_Y,
            outward_sign=1,
            mats=mats,
            bays=9,
            wall_mat=mats["charred"],
        )
    )
    objects.extend(
        add_atrium_band(
            "HospitalAtriumGround",
            height=PODIUM_HEIGHT,
            mats=mats,
            ground=True,
        )
    )
    objects.extend(add_public_canopy(mats))
    objects.extend(add_healing_courtyard(mats))
    objects.extend(add_rear_ambulance_arrival(mats))
    for index, (axis, fixed, lateral, outward) in enumerate(
        (
            ("y", FRONT_Y, -17.0, -1),
            ("y", FRONT_Y, 17.0, -1),
            ("x", INNER_LEFT_X, 8.5, 1),
            ("x", INNER_RIGHT_X, 8.5, -1),
        )
    ):
        objects.extend(
            add_living_wall_strip(
                f"HospitalPodiumLivingWall_{index}",
                axis=axis,
                fixed=fixed,
                lateral=lateral,
                height=PODIUM_HEIGHT,
                outward_sign=outward,
                mats=mats,
            )
        )
    if include_contract_markers:
        objects.extend(module_contract_markers("podium", "default", PODIUM_HEIGHT))
    return objects


def build_floor(
    mats: dict[str, bpy.types.Material],
    *,
    variant: str,
    include_contract_markers: bool,
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = [
        tbox(
            f"Hospital_{variant}_LeftWingCLTPlate",
            (17.0, DEPTH, 0.22),
            (-26.5, 0.0, 0.11),
            mats["glulam"],
            0.018,
            tile_m=1.25,
        ),
        tbox(
            f"Hospital_{variant}_RightWingCLTPlate",
            (17.0, DEPTH, 0.22),
            (26.5, 0.0, 0.11),
            mats["glulam"],
            0.018,
            tile_m=1.25,
        ),
        tbox(
            f"Hospital_{variant}_RearClinicalCLTPlate",
            (36.0, 15.0, 0.22),
            (0.0, 17.5, 0.11),
            mats["glulam"],
            0.018,
            tile_m=1.25,
        ),
    ]
    objects.extend(
        add_patient_face_y(
            f"Hospital_{variant}_LeftWingFront",
            x0=LEFT_X,
            x1=INNER_LEFT_X,
            surface_y=FRONT_Y,
            outward_sign=-1,
            mats=mats,
            variant=variant,
            bay_count=4,
        )
    )
    objects.extend(
        add_patient_face_y(
            f"Hospital_{variant}_RightWingFront",
            x0=INNER_RIGHT_X,
            x1=RIGHT_X,
            surface_y=FRONT_Y,
            outward_sign=-1,
            mats=mats,
            variant=variant,
            bay_count=4,
        )
    )
    objects.extend(
        add_patient_face_x(
            f"Hospital_{variant}_LeftOuter",
            y0=FRONT_Y,
            y1=REAR_Y,
            surface_x=LEFT_X,
            outward_sign=-1,
            mats=mats,
            variant=variant,
            bay_count=8,
        )
    )
    objects.extend(
        add_patient_face_x(
            f"Hospital_{variant}_RightOuter",
            y0=FRONT_Y,
            y1=REAR_Y,
            surface_x=RIGHT_X,
            outward_sign=1,
            mats=mats,
            variant=variant,
            bay_count=8,
        )
    )
    objects.extend(
        add_patient_face_x(
            f"Hospital_{variant}_LeftCourtyard",
            y0=FRONT_Y,
            y1=REAR_BAR_FRONT_Y,
            surface_x=INNER_LEFT_X,
            outward_sign=1,
            mats=mats,
            variant=variant,
            bay_count=6,
        )
    )
    objects.extend(
        add_patient_face_x(
            f"Hospital_{variant}_RightCourtyard",
            y0=FRONT_Y,
            y1=REAR_BAR_FRONT_Y,
            surface_x=INNER_RIGHT_X,
            outward_sign=-1,
            mats=mats,
            variant=variant,
            bay_count=6,
        )
    )
    objects.extend(
        add_patient_face_y(
            f"Hospital_{variant}_RearClinical",
            x0=LEFT_X,
            x1=RIGHT_X,
            surface_y=REAR_Y,
            outward_sign=1,
            mats=mats,
            variant=variant,
            bay_count=14,
        )
    )
    objects.extend(
        add_atrium_band(
            f"HospitalAtrium_{variant}",
            height=FLOOR_HEIGHT,
            mats=mats,
            ground=False,
        )
    )
    for index, (axis, fixed, lateral, outward) in enumerate(
        (
            ("y", FRONT_Y, -17.0, -1),
            ("y", FRONT_Y, 17.0, -1),
            ("x", INNER_LEFT_X, 8.5, 1),
            ("x", INNER_RIGHT_X, 8.5, -1),
        )
    ):
        objects.extend(
            add_living_wall_strip(
                f"Hospital_{variant}_LivingWall_{index}",
                axis=axis,
                fixed=fixed,
                lateral=lateral,
                height=FLOOR_HEIGHT,
                outward_sign=outward,
                mats=mats,
            )
        )
    if include_contract_markers:
        objects.extend(module_contract_markers("floor", variant, FLOOR_HEIGHT))
    return objects


def build_crown(
    mats: dict[str, bpy.types.Material],
    *,
    include_contract_markers: bool,
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = [
        tbox(
            "HospitalCrownLeftWingTimberFascia",
            (17.4, DEPTH, CROWN_HEIGHT),
            (-26.5, 0.0, CROWN_HEIGHT * 0.5),
            mats["glulam"],
            0.018,
            tile_m=1.15,
        ),
        tbox(
            "HospitalCrownRightWingTimberFascia",
            (17.4, DEPTH, CROWN_HEIGHT),
            (26.5, 0.0, CROWN_HEIGHT * 0.5),
            mats["glulam"],
            0.018,
            tile_m=1.15,
        ),
        tbox(
            "HospitalCrownRearClinicalTimberFascia",
            (36.0, 15.4, CROWN_HEIGHT),
            (0.0, 17.5, CROWN_HEIGHT * 0.5),
            mats["glulam"],
            0.018,
            tile_m=1.15,
        ),
        tbox(
            "HospitalCrownAtriumGlulamHeader",
            (
                ATRIUM_RIGHT_X - ATRIUM_LEFT_X + 0.8,
                0.72,
                CROWN_HEIGHT,
            ),
            (0.0, ATRIUM_FRONT_Y - 0.05, CROWN_HEIGHT * 0.5),
            mats["glulam"],
            0.018,
            tile_m=1.15,
        ),
    ]
    for x in (-35.0, -18.0, 18.0, 35.0):
        objects.append(
            tbox(
                f"HospitalCrownDarkMetalCoping_{x:+.0f}",
                (0.20, DEPTH, 0.16),
                (x, 0.0, CROWN_HEIGHT - 0.08),
                mats["solar"],
                0.010,
                tile_m=1.0,
            )
        )
    if include_contract_markers:
        objects.extend(module_contract_markers("crown", "crown", CROWN_HEIGHT))
    return objects


def add_green_roof_detail(
    name: str,
    *,
    x0: float,
    x1: float,
    y0: float,
    y1: float,
    z: float,
    mats: dict[str, bpy.types.Material],
    count: int,
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    for index in range(count):
        u = ((index * 37) % 101) / 100.0
        v = ((index * 61 + 17) % 103) / 102.0
        x = x0 + 0.8 + (x1 - x0 - 1.6) * u
        y = y0 + 0.8 + (y1 - y0 - 1.6) * v
        height = 0.14 + 0.08 * (index % 4)
        objects.append(
            tbox(
                f"{name}_MeadowPlant_{index:03d}",
                (0.10, 0.10, height),
                (x, y, z + height * 0.5),
                mats[("leaf_a", "leaf_b", "leaf_c")[index % 3]],
                0.025,
                tile_m=0.5,
            )
        )
    return objects


def add_screened_penthouse(
    name: str,
    *,
    centre: tuple[float, float],
    size: tuple[float, float],
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    x, y = centre
    width, depth = size
    height = 2.70
    objects: list[bpy.types.Object] = [
        tbox(
            f"{name}_MechanicalCore",
            (width - 0.40, depth - 0.40, height - 0.20),
            (x, y, 1.46),
            mats["deep"],
            0.08,
            tile_m=1.1,
        )
    ]
    for face, fixed, span0, span1, axis in (
        ("Front", y - depth * 0.5, x - width * 0.5, x + width * 0.5, "y"),
        ("Rear", y + depth * 0.5, x - width * 0.5, x + width * 0.5, "y"),
        ("Left", x - width * 0.5, y - depth * 0.5, y + depth * 0.5, "x"),
        ("Right", x + width * 0.5, y - depth * 0.5, y + depth * 0.5, "x"),
    ):
        for index in range(13):
            z = 0.36 + index * 0.18
            if axis == "y":
                size_value = (span1 - span0, 0.10, 0.08)
                location = ((span0 + span1) * 0.5, fixed, z)
            else:
                size_value = (0.10, span1 - span0, 0.08)
                location = (fixed, (span0 + span1) * 0.5, z)
            objects.append(
                tbox(
                    f"{name}_{face}_Louver_{index:02d}",
                    size_value,
                    location,
                    mats["solar"],
                    0.008,
                    tile_m=0.8,
                )
            )
    return objects


def add_pv_canopy(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    x0, x1 = -16.0, 16.0
    y0, y1 = 13.0, 24.0
    canopy_z = 3.52
    objects: list[bpy.types.Object] = []
    for x in (-15.4, -7.7, 0.0, 7.7, 15.4):
        for y in (13.7, 23.3):
            objects.append(
                tbox(
                    f"HospitalPVCanopyColumn_{x:+.1f}_{y:+.1f}",
                    (0.20, 0.20, canopy_z),
                    (x, y, canopy_z * 0.5),
                    mats["frame"],
                    0.012,
                    tile_m=0.8,
                )
            )
    for y in (13.7, 18.5, 23.3):
        objects.append(
            tbox(
                f"HospitalPVCanopyGlulamGirder_{y:+.1f}",
                (32.0, 0.24, 0.28),
                (0.0, y, canopy_z - 0.20),
                mats["glulam"],
                0.016,
                tile_m=1.15,
            )
        )
    columns = 10
    rows = 4
    panel_w = (x1 - x0 - 1.0) / columns
    panel_d = (y1 - y0 - 0.8) / rows
    for row in range(rows):
        for column in range(columns):
            x = x0 + 0.5 + panel_w * (column + 0.5)
            y = y0 + 0.4 + panel_d * (row + 0.5)
            objects.append(
                tbox(
                    f"HospitalPVPanel_{row:02d}_{column:02d}",
                    (panel_w - 0.12, panel_d - 0.12, 0.09),
                    (x, y, canopy_z),
                    mats["solar"],
                    0.010,
                    tile_m=0.9,
                )
            )
    return objects


def build_roof(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    roof_z = 0.18
    objects: list[bpy.types.Object] = [
        tbox(
            "HospitalLeftWingMeadowRoof",
            (16.4, 49.4, 0.36),
            (-26.5, 0.0, roof_z),
            mats["green_roof"],
            0.028,
            tile_m=1.2,
        ),
        tbox(
            "HospitalRightWingMeadowRoof",
            (16.4, 49.4, 0.36),
            (26.5, 0.0, roof_z),
            mats["green_roof"],
            0.028,
            tile_m=1.2,
        ),
        tbox(
            "HospitalRearClinicalMeadowRoof",
            (35.4, 14.4, 0.36),
            (0.0, 17.5, roof_z),
            mats["green_roof"],
            0.028,
            tile_m=1.2,
        ),
        tbox(
            "HospitalLeftWingGravelFireBreak",
            (2.0, 48.6, 0.12),
            (-26.5, 0.0, 0.40),
            mats["paving"],
            0.018,
            tile_m=1.0,
        ),
        tbox(
            "HospitalRightWingGravelFireBreak",
            (2.0, 48.6, 0.12),
            (26.5, 0.0, 0.40),
            mats["paving"],
            0.018,
            tile_m=1.0,
        ),
        tbox(
            "HospitalRearRoofServicePath",
            (34.6, 1.70, 0.12),
            (0.0, 17.5, 0.40),
            mats["paving"],
            0.018,
            tile_m=1.0,
        ),
        tbox(
            "HospitalAtriumRoofLowIron",
            (30.0, 7.4, 0.10),
            (0.0, 12.3, 0.62),
            mats["atrium_glass"],
            0.018,
            tile_m=1.0,
        ),
    ]
    for x in (-15.0, -7.5, 0.0, 7.5, 15.0):
        objects.append(
            tbox(
                f"HospitalAtriumRoofGlulamRib_{x:+.1f}",
                (0.22, 7.8, 0.28),
                (x, 12.3, 0.65),
                mats["glulam"],
                0.016,
                tile_m=1.1,
            )
        )
    for index, (x, y) in enumerate(
        (
            (-29.0, -14.0),
            (-24.0, 4.0),
            (24.0, -8.0),
            (29.0, 7.0),
            (-9.0, 20.5),
            (9.0, 20.5),
        )
    ):
        objects.append(
            tbox(
                f"HospitalRoofSkylight_{index}",
                (2.1, 1.45, 0.16),
                (x, y, 0.52),
                mats["atrium_glass"],
                0.05,
                tile_m=0.8,
            )
        )
    objects.extend(
        add_screened_penthouse(
            "HospitalLeftMechanicalPenthouse",
            centre=(-27.0, 13.5),
            size=(8.2, 7.0),
            mats=mats,
        )
    )
    objects.extend(
        add_screened_penthouse(
            "HospitalRightMechanicalPenthouse",
            centre=(27.0, 13.5),
            size=(8.2, 7.0),
            mats=mats,
        )
    )
    objects.extend(add_pv_canopy(mats))
    objects.extend(
        add_green_roof_detail(
            "HospitalLeftRoof",
            x0=-34.5,
            x1=-18.5,
            y0=-24.5,
            y1=24.5,
            z=0.43,
            mats=mats,
            count=52,
        )
    )
    objects.extend(
        add_green_roof_detail(
            "HospitalRightRoof",
            x0=18.5,
            x1=34.5,
            y0=-24.5,
            y1=24.5,
            z=0.43,
            mats=mats,
            count=52,
        )
    )
    objects.extend(
        add_green_roof_detail(
            "HospitalRearRoof",
            x0=-17.5,
            x1=17.5,
            y0=10.5,
            y1=24.5,
            z=0.43,
            mats=mats,
            count=34,
        )
    )
    for index, (x, y) in enumerate(
        (
            (-33.2, -23.2),
            (-18.8, -23.2),
            (18.8, -23.2),
            (33.2, -23.2),
            (-33.2, 23.2),
            (33.2, 23.2),
        )
    ):
        objects.append(
            cylinder(
                f"HospitalRoofDrain_{index}",
                0.16,
                0.46,
                (x, y, 0.33),
                mats["chrome"],
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


def normalize_bottom_origin(
    objects: list[bpy.types.Object],
) -> float:
    """Move evaluated bevel geometry to an exact bottom-centre Z origin."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    minimum_z = min(
        (
            evaluated.matrix_world @ Vector(corner)
        ).z
        for obj in objects
        if obj.type == "MESH"
        for evaluated in (obj.evaluated_get(depsgraph),)
        for corner in evaluated.bound_box
    )
    correction = -minimum_z
    if abs(correction) > 1e-6:
        translate_z(objects, correction)
        bpy.context.view_layer.update()
    return correction


def build_assembled(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    stack = (
        ("podium", "default", 0.0),
        ("floor", "typical_a", PODIUM_HEIGHT),
        ("floor", "typical_b", PODIUM_HEIGHT + FLOOR_HEIGHT),
        ("floor", "typical_c", PODIUM_HEIGHT + FLOOR_HEIGHT * 2.0),
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
    normalize_bottom_origin(objects)
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
        normalize_bottom_origin(objects)
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
    scene.view_settings.exposure = 0.68
    background = scene.world.node_tree.nodes.get("Background")
    if background:
        background.inputs["Color"].default_value = (0.48, 0.50, 0.52, 1.0)
        background.inputs["Strength"].default_value = 0.92
    ground = bpy.data.materials.get("MAT_W3_Ground")
    if ground and ground.use_nodes:
        ground.node_tree.nodes["Principled BSDF"].inputs[
            "Base Color"
        ].default_value = (0.35, 0.35, 0.32, 1.0)
    bpy.ops.object.light_add(type="SUN", location=(-82.0, -96.0, 118.0))
    sun = bpy.context.object
    sun.name = "PRESENTATION_W10_HospitalSoftSun"
    sun.data.energy = 1.84
    sun.data.color = (1.0, 0.89, 0.77)
    sun.data.angle = math.radians(11.0)
    sun.rotation_euler = (
        Vector((0.0, 0.0, 7.0)) - sun.location
    ).to_track_quat("-Z", "Y").to_euler()
    views = {
        "preview": ((-86.0, -108.0, 36.0), (0.0, 0.0, 7.4), 52),
        "street": ((0.0, -105.0, 7.5), (0.0, -7.0, 7.0), 50),
        "front_corner_oblique": (
            (-82.0, -104.0, 31.0),
            (0.0, -1.0, 7.5),
            54,
        ),
        "rear_corner_oblique": (
            (82.0, 84.0, 30.0),
            (7.0, 8.0, 7.2),
            56,
        ),
        "aerial": ((78.0, -78.0, 82.0), (0.0, 2.0, 6.8), 58),
        "facade_close": ((-1.0, -82.0, 10.0), (0.0, -9.0, 7.0), 66),
        "atrium_close": ((0.0, -43.0, 17.5), (0.0, 7.8, 12.2), 70),
        "patient_window_close": (
            (-47.0, -47.0, 11.5),
            (-25.0, -24.7, 8.3),
            66,
        ),
        "courtyard": ((0.0, -33.0, 8.0), (0.0, 1.0, 5.3), 58),
        "ambulance_close": (
            (61.0, 58.0, 11.0),
            (25.0, 21.0, 3.2),
            62,
        ),
        "roof_close": ((50.0, -35.0, 56.0), (0.0, 9.0, 16.0), 62),
        "side_close": ((92.0, -2.0, 13.0), (32.0, 0.0, 8.0), 64),
        "context": ((92.0, -106.0, 46.0), (0.0, 0.0, 7.3), 60),
    }
    selected = (
        {
            "preview",
            "street",
            "front_corner_oblique",
            "aerial",
            "atrium_close",
            "patient_window_close",
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
        if mat.get("source"):
            continue
        is_atrium = str(mat.get("glazing_profile")) == ATRIUM_GLASS_PROFILE
        colour = (0.22, 0.29, 0.29, 1.0) if is_atrium else (0.08, 0.11, 0.11, 1.0)
        alpha = 0.12 if is_atrium else 0.30
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
        "preferredProfiles": ["u_shape", "courtyard", "rectangle", "l_shape"],
        "minimumPreferredProfiles": 3,
        "profileRationale": (
            "The clinical identity is a pair of complete patient-room bars "
            "framing a therapeutic court, with one fixed public atrium and one "
            "rear clinical/service bar. U and courtyard drawings preserve the "
            "canonical plan directly; rectangle and L drawings repeat complete "
            "patient-room bars without stretching windows, atrium or ambulance bays."
        ),
        "fixedLandmarkScaleBand": {
            "scaleMin": 0.78,
            "scaleMax": 1.28,
            "maxAxisRatio": 1.24,
        },
        "recommendedWidth_m": [52, 92],
        "recommendedDepth_m": [38, 72],
        "recommendedFloors": [2, 6],
        "wingDepth_m": [14, 25],
        "preferredBayMultiple_m": 4.25,
        "profiles": {
            "u_shape": {
                "recommendedWidth_m": [52, 96],
                "recommendedDepth_m": [40, 76],
                "recommendedFloors": [2, 6],
                "wingDepth_m": [14, 25],
                "minimumCourtyard_m": 22.0,
                "preferredBayMultiple_m": 4.25,
            },
            "courtyard": {
                "recommendedWidth_m": [58, 104],
                "recommendedDepth_m": [44, 82],
                "recommendedFloors": [2, 6],
                "wingDepth_m": [14, 25],
                "minimumCourtyard_m": 22.0,
                "preferredBayMultiple_m": 4.25,
            },
            "rectangle": {
                "recommendedWidth_m": [48, 94],
                "recommendedDepth_m": [34, 66],
                "recommendedFloors": [2, 6],
                "preferredBayMultiple_m": 4.25,
            },
            "l_shape": {
                "recommendedWidth_m": [52, 98],
                "recommendedDepth_m": [38, 74],
                "recommendedFloors": [2, 6],
                "wingDepth_m": [14, 25],
                "preferredBayMultiple_m": 4.25,
            },
        },
        "notes": [
            "Keep the public atrium, entry canopy and courtyard threshold together.",
            "Repeat complete paired patient-room bays; never stretch one window.",
            "Keep the ambulance arrival separate from the public forecourt.",
            "Preserve the open healing court on U and courtyard profiles.",
            "Keep meadow roofs, screened plant and the PV canopy in the roof role.",
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
        "regional_variant_alias": REGIONAL_ALIAS,
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
        "reference_generation": "textures/source/reference-generation.json",
        "registered_openings": "textures/source/registered-openings.json",
        "registered_bands": "textures/source/registered-bands.json",
        "elevation_source": f"/families/{FAMILY}/elevation.jpg",
        "skin_manifest": "textures/skin_manifest.json",
        "generator": (
            "tools/archetype_compiler/generate_wave10_hospital_family.py"
        ),
        "reference_method": (
            "built-healthcare and mass-timber research, one canonical goalpost, "
            "rectified front registration, aerial courtyard/roof proof, rear "
            "emergency-service source, dedicated material construction sheet, "
            "layered patient/atrium glazing source and finite multiscale comparison"
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
            "The source pack fixes one four-storey U-shaped hospital with two "
            "patient wings, an open healing courtyard, an integrated glulam "
            "atrium and entry canopy, a separate two-bay ambulance arrival, "
            "living-wall strips, meadow roofs, screened plant and a PV canopy."
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
            "fixed_end_bays": [
                "public_atrium_and_entry",
                "courtyard_ends",
                "ambulance_service_arrival",
            ],
            "repeatable_middle_bays": [1, 2, 3],
            "middle_variants": ["typical_a", "typical_b", "typical_c"],
            "rule": (
                "Repeat complete paired patient-room bays and complete clinical "
                "floors. Never deform the atrium, public canopy, one patient "
                "window, living-wall junction or ambulance door."
            ),
        },
        "delivery": {
            "near_atlas_width_px": 2048,
            "far_atlas_width_px": 1024,
            "near_usage": (
                "true-scale timber, glulam, charred wood, concrete, living "
                "walls, meadow and metal plus physical panes, rooms and structure"
            ),
            "far_usage": "city-scale render-locked archetype material reference",
        },
        "assembly_contract": {
            "fixed": [
                "podium/entrance",
                "courtyard threshold and landscape",
                "integrated glulam atrium",
                "public entry canopy",
                "two-bay ambulance arrival",
                "corner returns",
                "crown",
                "roof",
                "meadow roof",
                "screened plant",
                "photovoltaic canopy",
            ],
            "repeatable": ["typical_a", "typical_b", "typical_c"],
            "side_elevations": (
                "Honey timber frames, paired occupied patient windows, planter "
                "ledges, living-wall strips, charred base, deep returns and roof "
                "flashings continue around both outer and courtyard elevations."
            ),
            "elevation_coverage": {
                "front": (
                    "two patient wings, integrated atrium, broad timber entry "
                    "canopy, charred public podium and living-wall junctions"
                ),
                "left": "complete occupied patient bays and planted timber frame",
                "right": (
                    "complete occupied patient bays plus separated emergency return"
                ),
                "rear": (
                    "rear clinical bar, exactly two ambulance bays, staff/service "
                    "arrival and screened mechanical functions"
                ),
                "roof": (
                    "meadow roofs, gravel breaks, skylights, atrium roof, two "
                    "screened penthouses and large photovoltaic canopy"
                ),
            },
            "variation_policy": (
                "Two to six levels use semantic stack bands. Mild full-envelope "
                "scaling is safe; larger drawings repeat complete clinical bars."
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
            "role": "floor",
            "variant_key": "typical_b",
            "level": 2,
            "z_m": PODIUM_HEIGHT + FLOOR_HEIGHT,
            "height_m": FLOOR_HEIGHT,
        },
        {
            "role": "floor",
            "variant_key": "typical_c",
            "level": 3,
            "z_m": PODIUM_HEIGHT + FLOOR_HEIGHT * 2.0,
            "height_m": FLOOR_HEIGHT,
        },
        {
            "role": "crown",
            "variant_key": "crown",
            "level": 4,
            "z_m": BODY_HEIGHT,
            "height_m": CROWN_HEIGHT,
        },
        {
            "role": "roof",
            "variant_key": "default",
            "level": 5,
            "z_m": BODY_HEIGHT + CROWN_HEIGHT,
            "height_m": ROOF_HEIGHT,
        },
    ]
    assembled = {
        "filename": assembled_path.name,
        "floors": 4,
        "uses_setback": False,
        "uses_crown": True,
        "height_m": TOTAL_HEIGHT,
        "triangle_count": fixed_triangles,
        "material_count": fixed_materials,
        "stack": stack,
        "footprint_profile": "u_shape",
        "source_variant_id": VARIANT_ID,
        "generation_archetype_id": VARIANT_ID,
        "footprint_target": {
            "width_m": NATIVE_WIDTH,
            "depth_m": NATIVE_DEPTH,
            "wing_depth_m": 17.0,
            "courtyard_width_m": 36.0,
            "courtyard_depth_m": 35.0,
            "segments": [
                {
                    "id": "left_patient_wing",
                    "centre_x_m": -26.5,
                    "centre_y_m": 0.0,
                    "length_m": DEPTH,
                    "thickness_m": 17.0,
                    "rotation_degrees": 90.0,
                },
                {
                    "id": "right_patient_wing",
                    "centre_x_m": 26.5,
                    "centre_y_m": 0.0,
                    "length_m": DEPTH,
                    "thickness_m": 17.0,
                    "rotation_degrees": 90.0,
                },
                {
                    "id": "rear_clinical_bar",
                    "centre_x_m": 0.0,
                    "centre_y_m": 17.5,
                    "length_m": 36.0,
                    "thickness_m": 15.0,
                    "rotation_degrees": 0.0,
                },
            ],
        },
        "massing_graph": {
            "type": "u_shaped_mass_timber_biophilic_hospital",
            "patient_wings": 2,
            "open_healing_courtyard": True,
            "integrated_public_atrium": True,
            "ambulance_bays": 2,
            "occupied_patient_room_rows": 3,
            "living_wall_strips": 4,
            "screened_mechanical_penthouses": 2,
            "photovoltaic_canopies": 1,
        },
        "texture_keys": sorted(skin["zones"]),
        "ao_baked": True,
    }
    dimensions = {
        "width_m": NATIVE_WIDTH,
        "depth_m": NATIVE_DEPTH,
        "wing_depth_m": 17.0,
        "courtyard_width_m": 36.0,
        "courtyard_depth_m": 35.0,
        "podium_height_m": PODIUM_HEIGHT,
        "floor_height_m": FLOOR_HEIGHT,
        "setback_height_m": FLOOR_HEIGHT,
        "crown_height_m": CROWN_HEIGHT,
        "roof_height_m": ROOF_HEIGHT,
        "total_height_m": TOTAL_HEIGHT,
        "native_floors": 4,
        "min_floors": 2,
        "max_floors": 6,
        "default_floors": 4,
    }
    identity = (
        "A four-storey U-shaped mass-timber hospital frames an open healing "
        "courtyard between two deep patient-room wings, joined by an integrated "
        "triple-height glulam atrium and entry canopy, with a separate two-bay "
        "ambulance arrival below meadow roofs and a photovoltaic terrace canopy."
    )
    material_zones = (
        "honey vertical timber rainscreen and exposed glulam/CLT; charred "
        "shou sugi ban public/service plinth; pale mineral concrete and paving; "
        "black thermally broken frames; physical neutral low-e patient glazing "
        "and low-iron atrium glass; occupied care rooms and public atrium; living "
        "walls and planted ledges; meadow roofs, gravel breaks and photovoltaics"
    )
    source = provenance()
    aliases = [ARCHETYPE_ID, VARIANT_ID, REGIONAL_ALIAS]
    manifest = {
        "manifest_schema": 3,
        "grammar_schema_version": 3,
        "generator": {
            "name": (
                "archetype_compiler/generate_wave10_hospital_family.py"
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
        "archetype_aliases": aliases,
        "aesthetic_category_id": "biophilic_healthcare",
        "development_type": "institutional_health",
        "reuse_keys": [
            ARCHETYPE_ID,
            VARIANT_ID,
            REGIONAL_ALIAS,
            "Biophilic Modern Healthcare",
            "Mass Timber Modern Hospital",
            "Mass Timber Hospital",
            "Regional Biophilic Wellness Hospital",
            "CLT Healthcare Centre",
        ],
        "generation_tags": [
            "wave10_essential_family",
            "institutional_health",
            "hospital",
            "mass_timber",
            "biophilic",
            "custom_pbr_skin",
            "physical_clinical_glazing",
            "reference_locked",
            "u_shaped_healing_courtyard",
            "integrated_glulam_atrium",
            "deep_patient_room_windows",
            "occupied_care_room_depth",
            "separate_ambulance_arrival",
            "living_wall_strips",
            "meadow_green_roof",
            "photovoltaic_healing_terrace",
        ],
        "footprint_compatibility": footprint,
        "coordinate_contract": COORDINATE_CONTRACT,
        "textures": texture_inventory(skin),
        "facade_sheet": facade_contract(skin),
        "massing_graph": {
            "type": "u_shaped_mass_timber_biophilic_hospital",
            "silhouette": (
                "two_four_storey_timber_patient_wings_frame_open_courtyard_"
                "around_integrated_glass_glulam_atrium_below_pv_canopy"
            ),
            "render_locked": True,
            "goalpost": (
                f"/families/{FAMILY}/textures/source/archetype-goalpost.png"
            ),
            "fallback": "complete_patient_bay_clinical_bar_streetwall",
            "patient_wings": 2,
            "open_healing_courtyard": True,
            "integrated_public_atrium": True,
            "ambulance_bays": 2,
        },
        "material_budget": {
            "max_assembled_materials": 26,
            "rationale": (
                "Custom timber, glulam, charred wood, mineral, living-wall, "
                "roof and photovoltaic PBR remain separate from physical "
                "patient/atrium glazing, occupied depth, planting and service objects."
            ),
        },
        "dimensions": dimensions,
        "native_width_m": NATIVE_WIDTH,
        "native_depth_m": NATIVE_DEPTH,
        "native_floors": 4,
        "min_floors": 2,
        "max_floors": 6,
        "default_floors": 4,
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
                "u_shaped_patient_wings",
                "open_landscaped_healing_courtyard",
                "integrated_triple_height_glass_glulam_atrium",
                "broad_integrated_public_entry_canopy",
                "deep_paired_patient_room_windows",
                "physical_low_e_glazing_and_occupied_care_rooms",
                "living_wall_strips_and_planter_ledges",
                "charred_public_and_service_plinth",
                "separate_two_bay_ambulance_arrival",
                "meadow_roofs_and_gravel_breaks",
                "two_screened_mechanical_penthouses",
                "large_photovoltaic_healing_terrace_canopy",
            ],
        },
        "archetype_aliases": aliases,
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
    skip_assembled_export: bool,
) -> None:
    clear_scene()
    folder = output_root / FAMILY
    folder.mkdir(parents=True, exist_ok=True)
    mats, skin = load_palette(folder)
    assembled_objects = build_assembled(mats)
    assembled_path = folder / f"{FAMILY}_assembled.glb"
    existing_manifest_path = folder / f"{FAMILY}_manifest.json"
    existing_manifest = (
        json.loads(existing_manifest_path.read_text(encoding="utf-8"))
        if existing_manifest_path.is_file()
        else {}
    )
    if not skip_assembled_export:
        export_glb(assembled_path, assembled_objects)
        fixed_triangles = evaluated_triangle_count(assembled_objects)
        fixed_materials = material_count(assembled_objects)
    elif not assembled_path.is_file():
        raise FileNotFoundError(
            f"--skip-assembled-export requires an existing {assembled_path}"
        )
    else:
        assembled_metadata = existing_manifest.get("assembled", {})
        fixed_triangles = int(
            assembled_metadata.get(
                "triangle_count",
                evaluated_triangle_count(assembled_objects),
            )
        )
        fixed_materials = int(
            assembled_metadata.get(
                "material_count",
                material_count(assembled_objects),
            )
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
        f"[wave10-hospital] {FAMILY}: {fixed_triangles} triangles, "
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
    print(f"[wave10-hospital-render] {FAMILY}: {len(manifest['renders'])} renders")


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
