"""Build the four approved reference-locked Wave 4 standard families.

This is intentionally an authored family generator rather than a generic box
extruder.  Each selected catalogue variant owns its facade registration,
physical opening rhythm, entrance construction, secondary elevations and roof.

Run with Blender 5.x:

    blender --background --factory-startup --python \
      tools/archetype_compiler/generate_wave4_standard_batch.py -- \
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
    arched_panel,
    beam,
    box,
    cylinder,
    delete_objects,
    export_glb,
    material,
    module_contract_markers,
    setup_render,
)
from generate_wave4_standard_families import (  # noqa: E402
    _principled,
    facade_panel,
    pbr_material,
    slim_arch_frame,
    texture_inventory,
)


FAMILIES: dict[str, dict] = {
    "brownstone-rowhouse-frontage": {
        "archetype_id": "brownstone_rowhouse_frontage",
        "variant_id": "brownstone_rowhouse_red_sandstone",
        "generation_archetype_id": "brownstone_rowhouse_red_sandstone",
        "label": "Brownstone Rowhouse Frontage — Red Brick and Sandstone",
        "dimensions": (8.0, 15.0),
        "native_floors": 3,
        "min_floors": 2,
        "max_floors": 4,
        # The reference counts the garden level and raised piano nobile as one
        # fixed entrance/podium assembly; one repeatable upper storey completes
        # the three-level selected variant.
        "podium_height_m": 5.70,
        "floor_height_m": 3.20,
        "canonical_floor_variants": ["typical_b"],
        "crown_height_m": 0.80,
        "roof_height_m": 0.50,
        "development_type": "residential_lowrise",
        "aesthetic_category_id": "historic",
        "catalogue_dir": "brownstone_rowhouse_frontage",
        "catalogue_variant": "variant_0",
        "aliases": [
            "brownstone_rowhouse_frontage",
            "brownstone_rowhouse_red_sandstone",
        ],
        "reuse_keys": [
            "brownstone_rowhouse_frontage",
            "brownstone_rowhouse_red_sandstone",
            "Residential — Brownstone / Rowhouse",
        ],
        "identity": (
            "A narrow five-bay red-brick rowhouse with carved sandstone lintels, "
            "deep paired sash reveals, a shadowed garden level and a central "
            "sandstone stoop physically integrated into the entrance."
        ),
        "materials": (
            "warm red pressed brick; buff carved sandstone; charcoal painted "
            "sash frames and railings; dark membrane roof; occupied warm glazing"
        ),
        "glass_profile": "heritage_sash_occupied",
        "profile": "red_brick_sandstone_rowhouse_v98",
        "kits": [
            "integrated_sandstone_stoop",
            "five_bay_sash_rhythm",
            "carved_lintels_and_sills",
            "bracketed_metal_cornice",
            "garden_level_areaways",
            "membrane_roof_skylight_chimneys",
        ],
        "footprint": {
            "recommendedWidth_m": [5, 30],
            "recommendedDepth_m": [12, 24],
            "recommendedFloors": [2, 4],
            "wingDepth_m": [5, 8],
            "preferredBayMultiple_m": 1.60,
            "minimumCourtyard_m": 6,
        },
        "palette": {
            "body": (0.24, 0.075, 0.035, 1),
            "trim": (0.54, 0.39, 0.22, 1),
            "metal": (0.025, 0.030, 0.030, 1),
            "glass": (0.055, 0.10, 0.12, 1),
            "interior": (0.55, 0.19, 0.055, 1),
            "roof": (0.055, 0.060, 0.065, 1),
        },
    },
    "industrial-brick-mixed-use": {
        "archetype_id": "industrial_brick_mixed_use",
        "variant_id": "industrial_brick_original_mill",
        "generation_archetype_id": "industrial_brick_original_mill",
        "label": "Industrial Brick Mixed Use — Original Mill",
        "dimensions": (30.0, 20.0),
        "native_floors": 4,
        "min_floors": 3,
        "max_floors": 6,
        "podium_height_m": 4.00,
        "floor_height_m": 3.50,
        "canonical_floor_variants": ["typical_a", "typical_b", "typical_c"],
        "crown_height_m": 1.00,
        "roof_height_m": 4.00,
        "development_type": "mixed_use",
        "aesthetic_category_id": "industrial",
        "catalogue_dir": "industrial_brick_mixed_use",
        "catalogue_variant": "variant_0",
        "aliases": [
            "industrial_brick_mixed_use",
            "industrial_brick_original_mill",
        ],
        "reuse_keys": [
            "industrial_brick_mixed_use",
            "industrial_brick_original_mill",
            "Mixed Use — Industrial Brick / Adaptive Reuse",
        ],
        "identity": (
            "A four-storey Victorian brick mill with six complete structural "
            "bays, shallow segmental-arched Crittall windows, expressed piers, "
            "corbelled eaves, gabled end walls and a long glazed roof monitor."
        ),
        "materials": (
            "weathered red common brick; dark steel Crittall frames; buff stone "
            "sills; slate roof; blackened metal monitor; occupied workshop glazing"
        ),
        "glass_profile": "industrial_crittall_occupied",
        "profile": "victorian_original_mill_v98",
        "kits": [
            "six_structural_bays",
            "segmental_arch_crittall_windows",
            "expressed_brick_piers",
            "corbelled_eaves",
            "shallow_slate_gable",
            "glazed_roof_monitor_and_chimney",
        ],
        "footprint": {
            "recommendedWidth_m": [24, 50],
            "recommendedDepth_m": [16, 32],
            "recommendedFloors": [3, 6],
            "wingDepth_m": [8, 13],
            "preferredBayMultiple_m": 5.00,
            "minimumCourtyard_m": 10,
        },
        "palette": {
            "body": (0.28, 0.075, 0.035, 1),
            "trim": (0.50, 0.36, 0.21, 1),
            "metal": (0.030, 0.040, 0.042, 1),
            "glass": (0.045, 0.095, 0.105, 1),
            "interior": (0.72, 0.29, 0.07, 1),
            "roof": (0.075, 0.085, 0.090, 1),
        },
    },
    "contemporary-midrise-residential": {
        "archetype_id": "contemporary_midrise_residential",
        "variant_id": "contemporary_midrise_variant_brick_bronze",
        "generation_archetype_id": "contemporary_midrise_variant_brick_bronze",
        "label": "Contemporary Mid-Rise Residential — Brick and Bronze",
        "dimensions": (25.0, 18.0),
        "native_floors": 6,
        "min_floors": 4,
        "max_floors": 8,
        "podium_height_m": 3.90,
        "floor_height_m": 3.00,
        "canonical_floor_variants": [
            "typical_a",
            "typical_b",
            "typical_c",
            "typical_a",
            "typical_b",
        ],
        "crown_height_m": 0.80,
        "roof_height_m": 0.80,
        "development_type": "residential_midrise",
        "aesthetic_category_id": "contemporary",
        "catalogue_dir": "contemporary_mid_rise_residential",
        "catalogue_variant": "variant_2",
        "aliases": [
            "contemporary_midrise_residential",
            "contemporary_midrise_variant_brick_bronze",
        ],
        "reuse_keys": [
            "contemporary_midrise_residential",
            "contemporary_midrise_variant_brick_bronze",
            "Residential — Contemporary Mid-Rise",
        ],
        "identity": (
            "A six-storey urban residential block with a pale limestone base, "
            "one deeply recessed arched entrance and a disciplined wide/narrow "
            "window cadence held by brick piers and bronze spandrel frames."
        ),
        "materials": (
            "deep umber brick; pale honed limestone; warm bronze frames and "
            "spandrels; clear occupied glazing; planted dark membrane service roof"
        ),
        "glass_profile": "bronze_recessed_occupied",
        "profile": "brick_bronze_midrise_v98",
        "kits": [
            "limestone_podium",
            "subtractive_arched_entrance",
            "wide_narrow_six_bay_cadence",
            "bronze_spandrel_frames",
            "brick_pilaster_grid",
            "planted_service_roof",
        ],
        "footprint": {
            "recommendedWidth_m": [15, 42],
            "recommendedDepth_m": [14, 30],
            "recommendedFloors": [4, 8],
            "wingDepth_m": [8, 13],
            "preferredBayMultiple_m": 4.15,
            "minimumCourtyard_m": 10,
        },
        "palette": {
            "body": (0.19, 0.075, 0.045, 1),
            "trim": (0.67, 0.60, 0.50, 1),
            "metal": (0.25, 0.12, 0.055, 1),
            "glass": (0.055, 0.105, 0.13, 1),
            "interior": (0.68, 0.26, 0.055, 1),
            "roof": (0.070, 0.075, 0.075, 1),
        },
    },
    "scandinavian-urban-residential": {
        "archetype_id": "scandinavian_urban_residential",
        "variant_id": "scandi_urban_white_plaster",
        "generation_archetype_id": "scandi_urban_white_plaster",
        "label": "Scandinavian Urban Residential — White Plaster",
        "dimensions": (38.0, 22.0),
        "native_floors": 6,
        "min_floors": 4,
        "max_floors": 7,
        "podium_height_m": 3.30,
        "floor_height_m": 3.00,
        "canonical_floor_variants": [
            "typical_a",
            "typical_b",
            "typical_c",
            "typical_a",
        ],
        "crown_height_m": 0.40,
        "roof_height_m": 4.80,
        "development_type": "residential_midrise",
        "aesthetic_category_id": "scandinavian",
        "catalogue_dir": "scandinavian_urban_residential",
        "catalogue_variant": "variant_0",
        "aliases": [
            "scandinavian_urban_residential",
            "scandi_urban_white_plaster",
        ],
        "reuse_keys": [
            "scandinavian_urban_residential",
            "scandi_urban_white_plaster",
            "Residential — Scandinavian Urban Block",
        ],
        "identity": (
            "A long white-plaster perimeter block with a real central courtyard "
            "passage, three vertically integrated timber balcony stacks and a "
            "dark standing-seam pitched roof punctuated by five aligned dormers."
        ),
        "materials": (
            "warm white mineral plaster; honey-toned timber balcony linings; "
            "black steel rails and window frames; standing-seam metal; clear glazing"
        ),
        "glass_profile": "nordic_clear_occupied",
        "profile": "white_plaster_dormer_block_v98",
        "kits": [
            "through_courtyard_passage",
            "three_timber_balcony_stacks",
            "restrained_black_window_grid",
            "standing_seam_gable_roof",
            "five_timber_trimmed_dormers",
            "integrated_downpipes",
        ],
        "footprint": {
            "recommendedWidth_m": [18, 48],
            "recommendedDepth_m": [14, 32],
            "recommendedFloors": [4, 7],
            "wingDepth_m": [8, 13],
            "preferredBayMultiple_m": 4.50,
            "minimumCourtyard_m": 10,
        },
        "palette": {
            "body": (0.73, 0.72, 0.68, 1),
            "trim": (0.42, 0.20, 0.075, 1),
            "metal": (0.025, 0.030, 0.032, 1),
            "glass": (0.050, 0.105, 0.13, 1),
            "interior": (0.70, 0.30, 0.070, 1),
            "roof": (0.055, 0.065, 0.070, 1),
        },
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("frontend/public/families"),
    )
    parser.add_argument(
        "--family",
        action="append",
        choices=sorted(FAMILIES),
        help="May be repeated. Defaults to the complete approved four-family batch.",
    )
    parser.add_argument("--view-set", choices=("pilot", "all"), default="all")
    parser.add_argument("--skip-renders", action="store_true")
    parser.add_argument("--skip-modules", action="store_true")
    parser.add_argument("--render-existing", action="store_true")
    return parser.parse_args(
        sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    )


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


def palette(
    family: str,
    family_dir: Path,
) -> tuple[dict[str, bpy.types.Material], dict]:
    cfg = FAMILIES[family]
    skin = json.loads(
        (family_dir / "textures" / "skin_manifest.json").read_text(encoding="utf-8")
    )
    near = {zone: values["near"] for zone, values in skin["zones"].items()}
    prefix = family.replace("-", "_")
    mats: dict[str, bpy.types.Material] = {
        "facade": pbr_material(
            f"MAT_W4_{prefix}_Facade",
            family_dir,
            near["facade"],
            "facade",
            alpha_mask=True,
            emission_strength=0.16,
        ),
        "podium": pbr_material(
            f"MAT_W4_{prefix}_Podium",
            family_dir,
            near["podium"],
            "podium",
            alpha_mask=True,
            emission_strength=0.12,
        ),
        "floor_a": pbr_material(
            f"MAT_W4_{prefix}_FloorA",
            family_dir,
            near["floor_a"],
            "floor_a",
            alpha_mask=True,
            emission_strength=0.14,
        ),
        "floor_b": pbr_material(
            f"MAT_W4_{prefix}_FloorB",
            family_dir,
            near["floor_b"],
            "floor_b",
            alpha_mask=True,
            emission_strength=0.14,
        ),
        "floor_c": pbr_material(
            f"MAT_W4_{prefix}_FloorC",
            family_dir,
            near["floor_c"],
            "floor_c",
            alpha_mask=True,
            emission_strength=0.14,
        ),
        "crown": pbr_material(
            f"MAT_W4_{prefix}_Crown",
            family_dir,
            near["crown"],
            "crown",
            emission_strength=0.06,
        ),
        "roof_skin": pbr_material(
            f"MAT_W4_{prefix}_RoofSkin",
            family_dir,
            near["roof"],
            "roof",
            metallic=0.20 if family == "scandinavian-urban-residential" else 0.02,
        ),
    }
    # The contract validator intentionally looks for distinct, always-visible
    # side/rear materials on every facade-bearing module.
    for elevation in ("Left", "Right", "Rear"):
        mats[elevation.lower()] = pbr_material(
            f"MAT_Sheet_Wrapped_{prefix}_{elevation}",
            family_dir,
            near["side"],
            "side",
            emission_strength=0.04,
        )
    if family == "scandinavian-urban-residential":
        mats["front_clean"] = pbr_material(
            f"MAT_W4_{prefix}_ReferencePlasterFront",
            family_dir,
            near["side"],
            "side",
            emission_strength=0.02,
        )
    colours = cfg["palette"]
    mats.update(
        {
            "body": material(
                f"MAT_W4_{prefix}_Body",
                colours["body"],
                0.76,
            ),
            "trim": material(
                f"MAT_W4_{prefix}_Trim",
                colours["trim"],
                0.62,
            ),
            "metal": material(
                f"MAT_W4_{prefix}_Metal",
                colours["metal"],
                0.32,
                metallic=0.62,
            ),
            "glass": material(
                f"MAT_W4_{prefix}_Glass",
                colours["glass"],
                0.18,
                metallic=0.05,
                emission=colours["interior"],
                emission_strength=0.22,
            ),
            "glass_alt": material(
                f"MAT_W4_{prefix}_GlassAlt",
                (
                    colours["glass"][0] * 0.72,
                    colours["glass"][1] * 0.78,
                    colours["glass"][2] * 0.85,
                    1,
                ),
                0.24,
                emission=(
                    colours["interior"][0] * 0.48,
                    colours["interior"][1] * 0.48,
                    colours["interior"][2] * 0.48,
                    1,
                ),
                emission_strength=0.12,
            ),
            "interior": material(
                f"MAT_W4_{prefix}_Interior",
                (0.055, 0.026, 0.014, 1),
                0.88,
                emission=colours["interior"],
                emission_strength=0.16,
            ),
            "roof": material(
                f"MAT_W4_{prefix}_Roof",
                colours["roof"],
                0.64,
                metallic=0.34,
            ),
            "green": material(
                f"MAT_W4_{prefix}_Planting",
                (0.075, 0.18, 0.055, 1),
                0.90,
            ),
        }
    )
    for key in ("glass", "glass_alt"):
        bsdf = _principled(mats[key])
        if bsdf.inputs.get("Transmission Weight"):
            bsdf.inputs["Transmission Weight"].default_value = 0.20
        if bsdf.inputs.get("Coat Weight"):
            bsdf.inputs["Coat Weight"].default_value = 0.18
        if bsdf.inputs.get("Emission Strength"):
            bsdf.inputs["Emission Strength"].default_value = (
                0.04 if key == "glass" else 0.12
            )
    return mats, skin


def facade_panel_uv(
    name: str,
    *,
    axis: str,
    centre: tuple[float, float, float],
    span: float,
    height: float,
    mat: bpy.types.Material,
    uv_bounds: tuple[float, float, float, float],
) -> bpy.types.Object:
    """Facade plane that samples a registered horizontal/vertical subregion."""
    obj = facade_panel(
        name,
        axis=axis,
        centre=centre,
        span=span,
        height=height,
        mat=mat,
    )
    u0, v0, u1, v1 = uv_bounds
    values = ((u0, v0), (u1, v0), (u1, v1), (u0, v1))
    for loop_index, value in enumerate(values):
        obj.data.uv_layers.active.data[loop_index].uv = value
    return obj


def _oriented_box(
    name: str,
    axis: str,
    lateral: float,
    plane: float,
    z: float,
    lateral_size: float,
    depth: float,
    height: float,
    mat: bpy.types.Material,
    bevel: float = 0.0,
) -> bpy.types.Object:
    if axis in {"front", "rear"}:
        return box(
            name,
            (lateral_size, depth, height),
            (lateral, plane, z),
            mat,
            bevel=bevel,
        )
    return box(
        name,
        (depth, lateral_size, height),
        (plane, lateral, z),
        mat,
        bevel=bevel,
    )


def rectangular_window(
    name: str,
    *,
    axis: str,
    lateral: float,
    plane: float,
    sill_z: float,
    width: float,
    height: float,
    mats: dict[str, bpy.types.Material],
    trim: str = "metal",
    mullions: int = 1,
    transoms: int = 1,
    reveal: float = 0.12,
    alt_glass: bool = False,
    heavy_surround: bool = False,
) -> list[bpy.types.Object]:
    """Make a recessed occupied opening, frame, sill and true muntin grid."""
    glass = mats["glass_alt" if alt_glass else "glass"]
    centre_z = sill_z + height / 2
    objects = [
        _oriented_box(
            f"{name}_Cavity",
            axis,
            lateral,
            plane + (reveal if axis in {"front", "left"} else -reveal),
            centre_z,
            width + 0.22,
            0.08,
            height + 0.20,
            mats["interior"],
        ),
        _oriented_box(
            f"{name}_Glass",
            axis,
            lateral,
            plane,
            centre_z,
            width,
            0.055,
            height,
            glass,
            bevel=0.025,
        ),
    ]
    frame = 0.065 if not heavy_surround else 0.105
    surround = 0.11 if not heavy_surround else 0.20
    for side in (-1, 1):
        objects.append(
            _oriented_box(
                f"{name}_Jamb_{side:+d}",
                axis,
                lateral + side * (width / 2 + surround / 2),
                plane - 0.025,
                centre_z,
                surround,
                0.10,
                height + surround * 1.5,
                mats[trim],
                bevel=0.025,
            )
        )
    for top in (0, 1):
        objects.append(
            _oriented_box(
                f"{name}_{'Lintel' if top else 'Sill'}",
                axis,
                lateral,
                plane - 0.035,
                sill_z + (height if top else 0) + (surround / 2 if top else -surround / 2),
                width + surround * 2,
                0.14 if heavy_surround else 0.10,
                surround,
                mats[trim],
                bevel=0.025,
            )
        )
    for index in range(1, mullions + 1):
        offset = -width / 2 + width * index / (mullions + 1)
        objects.append(
            _oriented_box(
                f"{name}_Mullion_{index}",
                axis,
                lateral + offset,
                plane - 0.045,
                centre_z,
                frame,
                0.075,
                height,
                mats["metal"],
            )
        )
    for index in range(1, transoms + 1):
        z = sill_z + height * index / (transoms + 1)
        objects.append(
            _oriented_box(
                f"{name}_Transom_{index}",
                axis,
                lateral,
                plane - 0.045,
                z,
                width,
                0.075,
                frame,
                mats["metal"],
            )
        )
    return objects


def segmental_arch_panel(
    name: str,
    *,
    axis: str,
    lateral: float,
    plane: float,
    sill_z: float,
    width: float,
    height: float,
    rise: float,
    mat: bpy.types.Material,
    segments: int = 20,
) -> bpy.types.Object:
    """Create a shallow segmental-arched pane (not a semicircular substitute)."""
    spring = sill_z + height - rise
    radius = width * width / (8 * rise) + rise / 2
    centre_z = spring + rise - radius
    points: list[tuple[float, float, float]] = []

    def vertex(value: float, z: float) -> tuple[float, float, float]:
        if axis in {"front", "rear"}:
            return (value, plane, z)
        return (plane, value, z)

    points.append(vertex(lateral - width / 2, sill_z))
    points.append(vertex(lateral + width / 2, sill_z))
    points.append(vertex(lateral + width / 2, spring))
    for index in range(1, segments):
        x = width / 2 - width * index / segments
        z = centre_z + math.sqrt(max(0.0, radius * radius - x * x))
        points.append(vertex(lateral + x, z))
    points.append(vertex(lateral - width / 2, spring))
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(points, [], [tuple(range(len(points)))])
    mesh.materials.append(mat)
    uv = mesh.uv_layers.new(name="UVMap")
    for loop_index, vertex_index in enumerate(mesh.polygons[0].vertices):
        co = points[vertex_index]
        value = co[0] if axis in {"front", "rear"} else co[1]
        uv.data[loop_index].uv = (
            (value - (lateral - width / 2)) / width,
            (co[2] - sill_z) / height,
        )
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def segmental_arch_window(
    name: str,
    *,
    axis: str,
    lateral: float,
    plane: float,
    sill_z: float,
    width: float,
    height: float,
    rise: float,
    mats: dict[str, bpy.types.Material],
    alt_glass: bool = False,
) -> list[bpy.types.Object]:
    glass = mats["glass_alt" if alt_glass else "glass"]
    spring = sill_z + height - rise
    radius = width * width / (8 * rise) + rise / 2
    centre_z = spring + rise - radius
    objects = [
        segmental_arch_panel(
            f"{name}_Glass",
            axis=axis,
            lateral=lateral,
            plane=plane,
            sill_z=sill_z,
            width=width,
            height=height,
            rise=rise,
            mat=glass,
        )
    ]
    for side in (-1, 1):
        objects.append(
            _oriented_box(
                f"{name}_Jamb_{side:+d}",
                axis,
                lateral + side * width / 2,
                plane - 0.03,
                sill_z + (height - rise) / 2,
                0.14,
                0.14,
                height - rise,
                mats["trim"],
                bevel=0.025,
            )
        )
    curve_points = []
    for index in range(25):
        x = -width / 2 + width * index / 24
        z = centre_z + math.sqrt(max(0.0, radius * radius - x * x))
        if axis in {"front", "rear"}:
            curve_points.append((lateral + x, plane - 0.035, z))
        else:
            curve_points.append((plane - 0.035, lateral + x, z))
    for index in range(len(curve_points) - 1):
        objects.append(
            beam(
                f"{name}_Arch_{index:02d}",
                curve_points[index],
                curve_points[index + 1],
                0.075,
                mats["trim"],
            )
        )
    objects.append(
        _oriented_box(
            f"{name}_Sill",
            axis,
            lateral,
            plane - 0.04,
            sill_z - 0.08,
            width + 0.28,
            0.20,
            0.16,
            mats["trim"],
            bevel=0.02,
        )
    )
    # Fine Crittall grid remains genuinely physical at close range.
    for column in (-0.25, 0.0, 0.25):
        objects.append(
            _oriented_box(
                f"{name}_Mullion_{column:+.2f}",
                axis,
                lateral + column * width,
                plane - 0.045,
                sill_z + (height - rise) / 2,
                0.045,
                0.07,
                height - rise,
                mats["metal"],
            )
        )
    for row in (0.28, 0.55, 0.80):
        objects.append(
            _oriented_box(
                f"{name}_Transom_{row:.2f}",
                axis,
                lateral,
                plane - 0.045,
                sill_z + row * (height - rise),
                width,
                0.07,
                0.045,
                mats["metal"],
            )
        )
    return objects


def add_wrapped_envelope(
    family: str,
    mats: dict[str, bpy.types.Material],
    *,
    base_z: float,
    height: float,
    front_mat: bpy.types.Material,
    inset: float = 0.0,
    passage_width: float | None = None,
) -> list[bpy.types.Object]:
    """Build a solid band plus separately authored front/left/right/rear skins."""
    cfg = FAMILIES[family]
    width, depth = cfg["dimensions"]
    width -= inset * 2
    depth -= inset * 2
    z = base_z + height / 2
    front_y = -depth / 2
    objects: list[bpy.types.Object] = []
    if passage_width:
        side_width = (width - passage_width) / 2
        objects.extend(
            [
                box(
                    "PassageEnvelopeLeft",
                    (side_width, depth, height),
                    (-(passage_width + side_width) / 2, 0, z),
                    mats["body"],
                    bevel=0.04,
                ),
                box(
                    "PassageEnvelopeRight",
                    (side_width, depth, height),
                    ((passage_width + side_width) / 2, 0, z),
                    mats["body"],
                    bevel=0.04,
                ),
            ]
        )
        left_fraction = side_width / width
        right_start = (side_width + passage_width) / width
        objects.extend(
            [
                facade_panel_uv(
                    "RegisteredFrontLeftOfPassage",
                    axis="front",
                    centre=(-(passage_width + side_width) / 2, front_y - 0.012, z),
                    span=side_width,
                    height=height,
                    mat=front_mat,
                    uv_bounds=(0.0, 0.0, left_fraction, 1.0),
                ),
                facade_panel_uv(
                    "RegisteredFrontRightOfPassage",
                    axis="front",
                    centre=((passage_width + side_width) / 2, front_y - 0.012, z),
                    span=side_width,
                    height=height,
                    mat=front_mat,
                    uv_bounds=(right_start, 0.0, 1.0, 1.0),
                ),
                facade_panel_uv(
                    "RegisteredRearLeftOfPassage",
                    axis="rear",
                    centre=(-(passage_width + side_width) / 2, depth / 2 + 0.012, z),
                    span=side_width,
                    height=height,
                    mat=mats["rear"],
                    uv_bounds=(0.0, 0.0, left_fraction, 1.0),
                ),
                facade_panel_uv(
                    "RegisteredRearRightOfPassage",
                    axis="rear",
                    centre=((passage_width + side_width) / 2, depth / 2 + 0.012, z),
                    span=side_width,
                    height=height,
                    mat=mats["rear"],
                    uv_bounds=(right_start, 0.0, 1.0, 1.0),
                ),
            ]
        )
    else:
        objects.append(
            box(
                f"{family}_BandEnvelope",
                (width, depth, height),
                (0, 0, z),
                mats["body"],
                bevel=0.035,
            )
        )
        objects.extend(
            [
                facade_panel(
                    "RegisteredFrontBand",
                    axis="front",
                    centre=(0, front_y - 0.012, z),
                    span=width,
                    height=height,
                    mat=front_mat,
                ),
                facade_panel(
                    "RegisteredRearBand",
                    axis="rear",
                    centre=(0, depth / 2 + 0.012, z),
                    span=width,
                    height=height,
                    mat=mats["rear"],
                ),
            ]
        )
    objects.extend(
        [
            facade_panel(
                "RegisteredLeftBand",
                axis="left",
                centre=(-width / 2 - 0.012, 0, z),
                span=depth,
                height=height,
                mat=mats["left"],
            ),
            facade_panel(
                "RegisteredRightBand",
                axis="right",
                centre=(width / 2 + 0.012, 0, z),
                span=depth,
                height=height,
                mat=mats["right"],
            ),
        ]
    )
    return objects


def add_secondary_windows(
    family: str,
    mats: dict[str, bpy.types.Material],
    *,
    base_z: float,
    height: float,
    sparse: bool = False,
) -> list[bpy.types.Object]:
    """Quiet occupied side/rear openings that never wrap the ceremonial front."""
    width, depth = FAMILIES[family]["dimensions"]
    objects: list[bpy.types.Object] = []
    sill = base_z + max(0.55, height * 0.24)
    window_height = min(1.75, height * 0.55)
    side_positions = (-depth * 0.24, depth * 0.24) if sparse else (
        -depth * 0.30,
        0,
        depth * 0.30,
    )
    for side, axis, plane in (
        ("L", "left", -width / 2 - 0.08),
        ("R", "right", width / 2 + 0.08),
    ):
        for index, y in enumerate(side_positions):
            objects.extend(
                rectangular_window(
                    f"{family}_{side}SideWindow_{index}",
                    axis=axis,
                    lateral=y,
                    plane=plane,
                    sill_z=sill,
                    width=1.05 if sparse else 1.25,
                    height=window_height,
                    mats=mats,
                    mullions=1,
                    transoms=1,
                    alt_glass=(index % 2 == 1),
                )
            )
    rear_positions = (
        (-width * 0.28, width * 0.28)
        if sparse
        else (-width * 0.33, -width * 0.11, width * 0.11, width * 0.33)
    )
    for index, x in enumerate(rear_positions):
        objects.extend(
            rectangular_window(
                f"{family}_RearWindow_{index}",
                axis="rear",
                lateral=x,
                plane=depth / 2 + 0.08,
                sill_z=sill,
                width=1.05 if sparse else 1.35,
                height=window_height,
                mats=mats,
                mullions=1,
                transoms=1,
                alt_glass=(index % 2 == 0),
            )
        )
    return objects


def add_industrial_secondary_windows(
    mats: dict[str, bpy.types.Material],
    *,
    base_z: float,
    height: float,
    role: str,
) -> list[bpy.types.Object]:
    """Continue the mill's segmental structural rhythm around every elevation."""
    width, depth = FAMILIES["industrial-brick-mixed-use"]["dimensions"]
    objects: list[bpy.types.Object] = []
    sill = base_z + (0.58 if role == "podium" else 0.46)
    opening_h = min(2.82, height - 0.78)
    for side, axis, plane in (
        ("L", "left", -width / 2 - 0.10),
        ("R", "right", width / 2 + 0.10),
    ):
        for index, y in enumerate((-7.35, -2.45, 2.45, 7.35)):
            objects.extend(
                segmental_arch_window(
                    f"Mill{side}EndCrittall_{role}_{index}",
                    axis=axis,
                    lateral=y,
                    plane=plane,
                    sill_z=sill,
                    width=3.18,
                    height=opening_h,
                    rise=0.38,
                    mats=mats,
                    alt_glass=(index + (role == "podium")) % 3 == 0,
                )
            )
    for index, x in enumerate((-12.5, -7.5, -2.5, 2.5, 7.5, 12.5)):
        objects.extend(
            segmental_arch_window(
                f"MillRearCrittall_{role}_{index}",
                axis="rear",
                lateral=x,
                plane=depth / 2 + 0.10,
                sill_z=sill,
                width=3.30,
                height=opening_h,
                rise=0.40,
                mats=mats,
                alt_glass=index % 4 == 0,
            )
        )
    return objects


def add_brownstone_details(
    role: str,
    variant: str,
    mats: dict[str, bpy.types.Material],
    *,
    base_z: float,
    height: float,
) -> list[bpy.types.Object]:
    width, depth = FAMILIES["brownstone-rowhouse-frontage"]["dimensions"]
    front = -depth / 2 - 0.10
    objects: list[bpy.types.Object] = []
    bays = (-3.20, -1.60, 0.0, 1.60, 3.20)
    if role == "podium":
        for index, x in enumerate(bays):
            if index == 2:
                # The entrance is recessed behind the landing, not pasted on.
                objects.append(
                    box(
                        "BrownstoneEntranceCavity",
                        (1.18, 0.18, 2.18),
                        (x, front + 0.12, 2.28),
                        mats["interior"],
                        bevel=0.04,
                    )
                )
                objects.extend(
                    rectangular_window(
                        "BrownstoneEntranceDoor",
                        axis="front",
                        lateral=x,
                        plane=front - 0.03,
                        sill_z=1.68,
                        width=0.92,
                        height=2.52,
                        mats=mats,
                        trim="trim",
                        mullions=0,
                        transoms=1,
                        heavy_surround=True,
                    )
                )
                objects.append(
                    box(
                        "BrownstoneDarkTimberDoorLeaf",
                        (0.82, 0.09, 2.28),
                        (0, front - 0.085, 2.83),
                        mats["interior"],
                        bevel=0.035,
                    )
                )
                for panel_index, panel_z in enumerate((2.20, 2.78, 3.38)):
                    objects.append(
                        box(
                            f"BrownstoneDoorPanelRail_{panel_index}",
                            (0.66, 0.06, 0.055),
                            (0, front - 0.145, panel_z),
                            mats["trim"],
                        )
                    )
                objects.append(
                    box(
                        "BrownstoneDoorCentreStile",
                        (0.045, 0.06, 1.82),
                        (0, front - 0.145, 2.70),
                        mats["trim"],
                    )
                )
            else:
                # Raised main-floor sash aligns with the stoop landing.
                objects.extend(
                    rectangular_window(
                        f"BrownstoneMainWindow_{index}",
                        axis="front",
                        lateral=x,
                        plane=front,
                        sill_z=2.02,
                        width=0.88,
                        height=2.18,
                        mats=mats,
                        trim="trim",
                        mullions=1,
                        transoms=1,
                        alt_glass=index % 3 == 0,
                        heavy_surround=True,
                    )
                )
                objects.extend(
                    rectangular_window(
                        f"BrownstoneGardenWindow_{index}",
                        axis="front",
                        lateral=x,
                        plane=front,
                        sill_z=0.30,
                        width=0.78,
                        height=1.02,
                        mats=mats,
                        trim="trim",
                        mullions=1,
                        transoms=1,
                        alt_glass=index % 2 == 0,
                    )
                )
        # Seven real step blocks rise into one integrated sandstone landing.
        steps = 7
        for index in range(steps):
            step_height = 0.22 * (index + 1)
            y = front - 2.40 + index * 0.31
            objects.append(
                box(
                    f"BrownstoneStoopStep_{index:02d}",
                    (2.24, 0.42, step_height),
                    (0, y, step_height / 2),
                    mats["trim"],
                    bevel=0.045,
                )
            )
        objects.append(
            box(
                "BrownstoneStoopLanding",
                (2.34, 1.18, 0.22),
                (0, front - 0.42, 1.65),
                mats["trim"],
                bevel=0.05,
            )
        )
        for side in (-1, 1):
            objects.append(
                box(
                    f"BrownstoneStoopCheek_{side:+d}",
                    (0.22, 2.75, 0.54),
                    (side * 1.16, front - 1.30, 1.30),
                    mats["trim"],
                    bevel=0.05,
                )
            )
            rail_points = [
                (
                    side * 1.17,
                    front - 2.35 + index * 0.38,
                    0.82 + index * 0.25,
                )
                for index in range(7)
            ]
            for index in range(len(rail_points) - 1):
                objects.append(
                    beam(
                        f"BrownstoneHandrail_{side:+d}_{index}",
                        rail_points[index],
                        rail_points[index + 1],
                        0.035,
                        mats["metal"],
                    )
                )
            for index, point in enumerate(rail_points):
                objects.append(
                    beam(
                        f"BrownstoneRailPost_{side:+d}_{index}",
                        (point[0], point[1], max(0.05, point[2] - 0.75)),
                        point,
                        0.024,
                        mats["metal"],
                    )
                )
    elif role in {"floor", "setback"}:
        for index, x in enumerate(bays):
            objects.extend(
                rectangular_window(
                    f"BrownstoneSash_{variant}_{index}",
                    axis="front",
                    lateral=x,
                    plane=front,
                    sill_z=base_z + 0.58,
                    width=0.88,
                    height=1.92,
                    mats=mats,
                    trim="trim",
                    mullions=1,
                    transoms=1,
                    alt_glass=(index + (variant == "typical_b")) % 3 == 0,
                    heavy_surround=True,
                )
            )
        # A sandstone string course makes the stacked modules read as masonry.
        objects.append(
            box(
                f"BrownstoneStringCourse_{variant}",
                (width + 0.18, 0.18, 0.16),
                (0, front - 0.03, base_z + 0.15),
                mats["trim"],
                bevel=0.025,
            )
        )
    elif role == "crown":
        objects.extend(
            [
                box(
                    "BrownstoneCorniceLower",
                    (width + 0.30, 0.34, 0.18),
                    (0, front - 0.09, base_z + 0.18),
                    mats["metal"],
                    bevel=0.035,
                ),
                box(
                    "BrownstoneCorniceUpper",
                    (width + 0.52, 0.46, 0.18),
                    (0, front - 0.14, base_z + 0.66),
                    mats["metal"],
                    bevel=0.035,
                ),
            ]
        )
        for index, x in enumerate(
            [-3.55, -2.85, -2.15, -1.45, -0.72, 0, 0.72, 1.45, 2.15, 2.85, 3.55]
        ):
            objects.append(
                box(
                    f"BrownstoneCorniceBracket_{index:02d}",
                    (0.18, 0.38, 0.40),
                    (x, front - 0.12, base_z + 0.40),
                    mats["metal"],
                    bevel=0.03,
                )
            )
    return objects


def add_industrial_details(
    role: str,
    variant: str,
    mats: dict[str, bpy.types.Material],
    *,
    base_z: float,
    height: float,
) -> list[bpy.types.Object]:
    width, depth = FAMILIES["industrial-brick-mixed-use"]["dimensions"]
    front = -depth / 2 - 0.10
    objects: list[bpy.types.Object] = []
    bays = (-12.5, -7.5, -2.5, 2.5, 7.5, 12.5)
    if role in {"podium", "floor", "setback"}:
        sill = base_z + (0.62 if role == "podium" else 0.48)
        opening_h = min(2.86, height - 0.82)
        for index, x in enumerate(bays):
            if role == "podium" and index == 2:
                objects.extend(
                    rectangular_window(
                        "MillRecessedEntrance",
                        axis="front",
                        lateral=x,
                        plane=front,
                        sill_z=base_z + 0.22,
                        width=2.70,
                        height=2.85,
                        mats=mats,
                        trim="metal",
                        mullions=2,
                        transoms=2,
                        heavy_surround=True,
                    )
                )
            else:
                objects.extend(
                    segmental_arch_window(
                        f"MillCrittall_{variant}_{index}",
                        axis="front",
                        lateral=x,
                        plane=front,
                        sill_z=sill,
                        width=3.45,
                        height=opening_h,
                        rise=0.42,
                        mats=mats,
                        alt_glass=(index + len(variant)) % 3 == 0,
                    )
                )
        for index, x in enumerate((-15.0, -10.0, -5.0, 0.0, 5.0, 10.0, 15.0)):
            objects.append(
                box(
                    f"MillStructuralPier_{role}_{index}",
                    (0.48, 0.30, height),
                    (x, front - 0.06, base_z + height / 2),
                    mats["body"],
                    bevel=0.035,
                )
            )
        objects.extend(
            [
                box(
                    f"MillSillCourse_{role}",
                    (width + 0.28, 0.20, 0.15),
                    (0, front - 0.035, base_z + 0.22),
                    mats["trim"],
                ),
                box(
                    f"MillHeadCourse_{role}",
                    (width + 0.22, 0.18, 0.13),
                    (0, front - 0.025, base_z + height - 0.20),
                    mats["trim"],
                ),
            ]
        )
    elif role == "crown":
        for row in range(3):
            objects.append(
                box(
                    f"MillCorbelCourse_{row}",
                    (width + 0.22 + row * 0.16, 0.24 + row * 0.08, 0.16),
                    (0, front - 0.04 * row, base_z + 0.18 + row * 0.25),
                    mats["body" if row != 1 else "trim"],
                    bevel=0.02,
                )
            )
        for index, x in enumerate(
            [-14.3, -13.3, -12.3, -11.3, -10.3, -9.3, -8.3, -7.3,
             -6.3, -5.3, -4.3, -3.3, -2.3, -1.3, -0.3, 0.7, 1.7, 2.7,
             3.7, 4.7, 5.7, 6.7, 7.7, 8.7, 9.7, 10.7, 11.7, 12.7, 13.7, 14.3]
        ):
            objects.append(
                box(
                    f"MillDentil_{index:02d}",
                    (0.34, 0.34, 0.30),
                    (x, front - 0.11, base_z + 0.82),
                    mats["body"],
                    bevel=0.025,
                )
            )
    return objects


def add_contemporary_details(
    role: str,
    variant: str,
    mats: dict[str, bpy.types.Material],
    *,
    base_z: float,
    height: float,
) -> list[bpy.types.Object]:
    width, depth = FAMILIES["contemporary-midrise-residential"]["dimensions"]
    front = -depth / 2 - 0.10
    objects: list[bpy.types.Object] = []
    bays = (-10.35, -6.20, -2.05, 2.05, 6.20, 10.35)
    if role == "podium":
        objects.append(
            box(
                "ContemporaryLimestonePlinth",
                (width + 0.18, 0.32, 1.05),
                (0, front - 0.06, base_z + 0.525),
                mats["trim"],
                bevel=0.055,
            )
        )
        for index, x in enumerate((-9.0, -4.7, 4.7, 9.0)):
            objects.extend(
                rectangular_window(
                    f"ContemporaryPodiumWindow_{index}",
                    axis="front",
                    lateral=x,
                    plane=front,
                    sill_z=base_z + 0.62,
                    width=3.20,
                    height=2.62,
                    mats=mats,
                    trim="metal",
                    mullions=2,
                    transoms=1,
                    alt_glass=index % 3 == 0,
                )
            )
        # A genuine dark recess and stone arch form the entrance threshold.
        objects.append(
            arched_panel(
                "ContemporaryArchedEntranceCavity",
                0.0,
                front - 0.03,
                base_z + 0.12,
                3.45,
                3.40,
                mats["interior"],
                segments=32,
            )
        )
        objects.extend(
            slim_arch_frame(
                "ContemporaryArchedEntrance",
                axis="front",
                lateral=0,
                plane=front - 0.10,
                sill_z=base_z + 0.12,
                width=3.45,
                height=3.40,
                depth=0.22,
                rail_radius=0.13,
                mat=mats["trim"],
            )
        )
        objects.extend(
            [
                box(
                    "ContemporaryEntranceDoorLeft",
                    (1.35, 0.08, 2.45),
                    (-0.72, front - 0.11, base_z + 1.35),
                    mats["glass_alt"],
                ),
                box(
                    "ContemporaryEntranceDoorRight",
                    (1.35, 0.08, 2.45),
                    (0.72, front - 0.11, base_z + 1.35),
                    mats["glass"],
                ),
            ]
        )
    elif role in {"floor", "setback"}:
        for index, x in enumerate(bays):
            wide = (index + (variant == "typical_b")) % 2 == 0
            objects.extend(
                rectangular_window(
                    f"ContemporaryWindow_{variant}_{index}",
                    axis="front",
                    lateral=x,
                    plane=front,
                    sill_z=base_z + 0.48,
                    width=2.38 if wide else 1.08,
                    height=2.10,
                    mats=mats,
                    trim="metal",
                    mullions=1 if wide else 0,
                    transoms=1,
                    alt_glass=(index + len(variant)) % 3 == 0,
                )
            )
        # Bronze spandrel lines and brick pilasters produce the reference cadence.
        objects.append(
            box(
                f"ContemporaryBronzeSpandrel_{variant}",
                (width + 0.08, 0.15, 0.14),
                (0, front - 0.035, base_z + height - 0.20),
                mats["metal"],
                bevel=0.02,
            )
        )
        for index, x in enumerate((-12.5, -8.3, -4.15, 0, 4.15, 8.3, 12.5)):
            objects.append(
                box(
                    f"ContemporaryBrickPier_{variant}_{index}",
                    (0.32, 0.25, height),
                    (x, front - 0.035, base_z + height / 2),
                    mats["body"],
                    bevel=0.025,
                )
            )
    elif role == "crown":
        objects.extend(
            [
                box(
                    "ContemporaryCrownBronze",
                    (width + 0.18, 0.24, 0.16),
                    (0, front - 0.05, base_z + 0.18),
                    mats["metal"],
                ),
                box(
                    "ContemporaryParapetCap",
                    (width + 0.34, depth + 0.28, 0.14),
                    (0, 0, base_z + height - 0.07),
                    mats["trim"],
                    bevel=0.025,
                ),
            ]
        )
    return objects


def balcony_stack_floor(
    name: str,
    *,
    x: float,
    front: float,
    base_z: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = [
        box(
            f"{name}_TimberRecess",
            (3.30, 0.22, 2.42),
            (x, front + 0.10, base_z + 1.55),
            mats["trim"],
            bevel=0.045,
        ),
        box(
            f"{name}_DoorGlass",
            (1.62, 0.10, 2.10),
            (x, front - 0.055, base_z + 1.52),
            mats["glass"],
            bevel=0.025,
        ),
        box(
            f"{name}_Slab",
            (3.48, 1.48, 0.18),
            (x, front - 0.72, base_z + 0.34),
            mats["trim"],
            bevel=0.055,
        ),
    ]
    for side in (-1, 1):
        objects.append(
            box(
                f"{name}_TimberReturn_{side:+d}",
                (0.18, 1.28, 2.42),
                (x + side * 1.56, front - 0.48, base_z + 1.55),
                mats["trim"],
                bevel=0.035,
            )
        )
    rail_y = front - 1.42
    rail_z = base_z + 1.18
    objects.append(
        beam(
            f"{name}_TopRail",
            (x - 1.62, rail_y, rail_z),
            (x + 1.62, rail_y, rail_z),
            0.045,
            mats["metal"],
        )
    )
    for index in range(10):
        px = x - 1.55 + index * 3.10 / 9
        objects.append(
            beam(
                f"{name}_Baluster_{index:02d}",
                (px, rail_y, base_z + 0.43),
                (px, rail_y, rail_z),
                0.021,
                mats["metal"],
            )
        )
    for side in (-1, 1):
        objects.append(
            beam(
                f"{name}_SideRail_{side:+d}",
                (x + side * 1.62, front - 0.05, rail_z),
                (x + side * 1.62, rail_y, rail_z),
                0.040,
                mats["metal"],
            )
        )
    return objects


def add_scandi_details(
    role: str,
    variant: str,
    mats: dict[str, bpy.types.Material],
    *,
    base_z: float,
    height: float,
) -> list[bpy.types.Object]:
    width, depth = FAMILIES["scandinavian-urban-residential"]["dimensions"]
    front = -depth / 2 - 0.10
    objects: list[bpy.types.Object] = []
    if role == "podium":
        # Stone/metal portal lining makes the through-passage read as a cut.
        passage_w = 4.60
        for side in (-1, 1):
            objects.append(
                box(
                    f"ScandiPassageJamb_{side:+d}",
                    (0.28, depth + 0.10, height),
                    (side * passage_w / 2, 0, base_z + height / 2),
                    mats["trim"],
                    bevel=0.04,
                )
            )
        objects.append(
            box(
                "ScandiPassageCeiling",
                (passage_w, depth + 0.05, 0.22),
                (0, 0, base_z + height - 0.11),
                mats["trim"],
            )
        )
        for index, x in enumerate((-16.0, -12.0, -8.0, 8.0, 12.0, 16.0)):
            objects.extend(
                rectangular_window(
                    f"ScandiPodiumWindow_{index}",
                    axis="front",
                    lateral=x,
                    plane=front,
                    sill_z=base_z + 0.62,
                    width=1.55,
                    height=1.95,
                    mats=mats,
                    trim="metal",
                    mullions=0,
                    transoms=1,
                    alt_glass=index % 3 == 0,
                )
            )
    elif role in {"floor", "setback"}:
        balcony_x = (-12.0, 0.0, 12.0)
        for index, x in enumerate(balcony_x):
            objects.extend(
                balcony_stack_floor(
                    f"ScandiBalcony_{variant}_{index}",
                    x=x,
                    front=front,
                    base_z=base_z,
                    mats=mats,
                )
            )
        window_x = (-17.0, -15.0, -8.2, -6.2, 6.2, 8.2, 15.0, 17.0)
        for index, x in enumerate(window_x):
            objects.extend(
                rectangular_window(
                    f"ScandiWindow_{variant}_{index}",
                    axis="front",
                    lateral=x,
                    plane=front,
                    sill_z=base_z + 0.55,
                    width=1.15,
                    height=1.92,
                    mats=mats,
                    trim="metal",
                    mullions=0,
                    transoms=1,
                    alt_glass=(index + len(variant)) % 4 == 0,
                )
            )
    elif role == "crown":
        objects.extend(
            [
                box(
                    "ScandiEaveBandFront",
                    (width + 0.20, 0.26, 0.24),
                    (0, front - 0.04, base_z + 0.20),
                    mats["trim"],
                    bevel=0.025,
                ),
                box(
                    "ScandiEaveBandRear",
                    (width + 0.20, 0.26, 0.24),
                    (0, depth / 2 + 0.14, base_z + 0.20),
                    mats["trim"],
                    bevel=0.025,
                ),
            ]
        )
    return objects


DETAIL_BUILDERS = {
    "brownstone-rowhouse-frontage": add_brownstone_details,
    "industrial-brick-mixed-use": add_industrial_details,
    "contemporary-midrise-residential": add_contemporary_details,
    "scandinavian-urban-residential": add_scandi_details,
}


def build_band_module(
    family: str,
    mats: dict[str, bpy.types.Material],
    *,
    role: str,
    variant: str,
    base_z: float = 0.0,
    setback: bool = False,
) -> list[bpy.types.Object]:
    cfg = FAMILIES[family]
    if role == "podium":
        height = cfg["podium_height_m"]
        front_mat = mats["podium"]
    elif role in {"floor", "setback"}:
        height = cfg["floor_height_m"]
        front_mat = mats[
            {"typical_a": "floor_a", "typical_b": "floor_b"}.get(variant, "floor_c")
        ]
    else:
        height = cfg["crown_height_m"]
        front_mat = mats["crown"]
    if family == "scandinavian-urban-residential":
        # The physical windows, balcony niches and carved passage already carry
        # the registered composition. A reference-palette plaster PBR prevents
        # the orthographic source from leaving a second "ghost" balcony layer.
        front_mat = mats["front_clean"]
    passage = (
        4.60
        if family == "scandinavian-urban-residential" and role == "podium"
        else None
    )
    # Setback variants keep the registered window/return geometry on the same
    # module envelope. The composer may inset the complete module as a unit.
    inset = 0.0
    objects = add_wrapped_envelope(
        family,
        mats,
        base_z=base_z,
        height=height,
        front_mat=front_mat,
        inset=inset,
        passage_width=passage,
    )
    objects.extend(
        DETAIL_BUILDERS[family](
            role,
            variant,
            mats,
            base_z=base_z,
            height=height,
        )
    )
    sparse_secondary = family == "brownstone-rowhouse-frontage"
    if role != "crown" and family == "industrial-brick-mixed-use":
        objects.extend(
            add_industrial_secondary_windows(
                mats,
                base_z=base_z,
                height=height,
                role=role,
            )
        )
    elif role != "crown":
        objects.extend(
            add_secondary_windows(
                family,
                mats,
                base_z=base_z,
                height=height,
                sparse=sparse_secondary,
            )
        )
    return objects


def gable_roof_shell(
    name: str,
    *,
    width: float,
    depth: float,
    height: float,
    base_z: float,
    mat: bpy.types.Material,
    gable_mat: bpy.types.Material | None = None,
) -> bpy.types.Object:
    """Solid roof prism with ridge along the long X axis and true end gables."""
    half_w = width / 2
    half_d = depth / 2
    eave = base_z + 0.12
    ridge = base_z + height
    verts = [
        (-half_w, -half_d, base_z),
        (half_w, -half_d, base_z),
        (half_w, half_d, base_z),
        (-half_w, half_d, base_z),
        (-half_w, -half_d, eave),
        (half_w, -half_d, eave),
        (half_w, half_d, eave),
        (-half_w, half_d, eave),
        (-half_w, 0, ridge),
        (half_w, 0, ridge),
    ]
    faces = [
        (0, 3, 2, 1),
        (4, 5, 9, 8),
        (8, 9, 6, 7),
        (0, 1, 5, 4),
        (3, 7, 6, 2),
        (0, 4, 8, 7, 3),
        (1, 2, 6, 9, 5),
    ]
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    if gable_mat is not None:
        mesh.materials.append(gable_mat)
        # The last two polygons are the end-wall gables, not roof weathering.
        mesh.polygons[5].material_index = 1
        mesh.polygons[6].material_index = 1
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    # A smart projection preserves true-scale roof material rather than
    # stretching the facade elevation over the slopes.
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.select_set(False)
    return obj


def add_gable_seams(
    name: str,
    *,
    width: float,
    depth: float,
    rise: float,
    base_z: float,
    mat: bpy.types.Material,
    spacing: float,
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    x = -width / 2 + spacing / 2
    while x < width / 2:
        objects.extend(
            [
                beam(
                    f"{name}_FrontSeam_{x:+.2f}",
                    (x, -depth / 2 - 0.02, base_z + 0.18),
                    (x, 0, base_z + rise + 0.04),
                    0.025,
                    mat,
                ),
                beam(
                    f"{name}_RearSeam_{x:+.2f}",
                    (x, 0, base_z + rise + 0.04),
                    (x, depth / 2 + 0.02, base_z + 0.18),
                    0.025,
                    mat,
                ),
            ]
        )
        x += spacing
    objects.append(
        beam(
            f"{name}_Ridge",
            (-width / 2 - 0.12, 0, base_z + rise + 0.06),
            (width / 2 + 0.12, 0, base_z + rise + 0.06),
            0.06,
            mat,
        )
    )
    return objects


def build_flat_roof(
    family: str,
    mats: dict[str, bpy.types.Material],
    *,
    base_z: float,
) -> list[bpy.types.Object]:
    cfg = FAMILIES[family]
    width, depth = cfg["dimensions"]
    height = cfg["roof_height_m"]
    objects: list[bpy.types.Object] = [
        box(
            f"{family}_RoofDeck",
            (width, depth, 0.22),
            (0, 0, base_z + 0.11),
            mats["roof_skin"],
            bevel=0.035,
        )
    ]
    parapet_h = min(0.48, height * 0.70)
    objects.extend(
        [
            box(
                f"{family}_FrontParapet",
                (width + 0.18, 0.28, parapet_h),
                (0, -depth / 2 + 0.10, base_z + parapet_h / 2),
                mats["body"],
                bevel=0.025,
            ),
            box(
                f"{family}_RearParapet",
                (width + 0.18, 0.28, parapet_h),
                (0, depth / 2 - 0.10, base_z + parapet_h / 2),
                mats["body"],
                bevel=0.025,
            ),
            box(
                f"{family}_LeftParapet",
                (0.28, depth, parapet_h),
                (-width / 2 + 0.10, 0, base_z + parapet_h / 2),
                mats["body"],
                bevel=0.025,
            ),
            box(
                f"{family}_RightParapet",
                (0.28, depth, parapet_h),
                (width / 2 - 0.10, 0, base_z + parapet_h / 2),
                mats["body"],
                bevel=0.025,
            ),
        ]
    )
    if family == "brownstone-rowhouse-frontage":
        objects.extend(
            [
                box(
                    "BrownstoneRoofSkylightCurb",
                    (2.2, 3.2, 0.20),
                    (0, 1.5, base_z + 0.28),
                    mats["trim"],
                    bevel=0.06,
                ),
                box(
                    "BrownstoneRoofSkylightGlass",
                    (1.9, 2.9, 0.10),
                    (0, 1.5, base_z + 0.42),
                    mats["glass"],
                    bevel=0.05,
                ),
                box(
                    "BrownstoneChimneyLeft",
                    (0.72, 0.82, height),
                    (-2.65, 4.8, base_z + height / 2),
                    mats["rear"],
                    bevel=0.04,
                ),
                box(
                    "BrownstoneChimneyRight",
                    (0.72, 0.82, height * 0.88),
                    (2.65, 4.8, base_z + height * 0.44),
                    mats["rear"],
                    bevel=0.04,
                ),
            ]
        )
    else:
        # Brick plant courts, roof lights and planting follow the selected
        # contemporary reference instead of a generic equipment scatter.
        objects.extend(
            [
                box(
                    "ContemporaryPlantCourt",
                    (7.0, 4.4, 0.58),
                    (4.7, 2.4, base_z + 0.29),
                    mats["body"],
                    bevel=0.06,
                ),
                box(
                    "ContemporaryLiftOverrun",
                    (3.6, 3.2, 0.72),
                    (-5.0, 2.6, base_z + 0.36),
                    mats["metal"],
                    bevel=0.08,
                ),
                box(
                    "ContemporaryRoofLight",
                    (4.4, 2.4, 0.28),
                    (0, -2.8, base_z + 0.28),
                    mats["glass"],
                    bevel=0.08,
                ),
            ]
        )
        for index, x in enumerate((-8.5, -4.5, 4.5, 8.5)):
            objects.append(
                box(
                    f"ContemporaryPlanter_{index}",
                    (2.2, 0.9, 0.42),
                    (x, -5.4, base_z + 0.25),
                    mats["green"],
                    bevel=0.10,
                )
            )
    return objects


def build_industrial_roof(
    mats: dict[str, bpy.types.Material],
    *,
    base_z: float,
) -> list[bpy.types.Object]:
    cfg = FAMILIES["industrial-brick-mixed-use"]
    width, depth = cfg["dimensions"]
    height = cfg["roof_height_m"]
    gable_rise = 2.65
    objects = [
        gable_roof_shell(
            "MillSlateGableRoof",
            width=width + 0.55,
            depth=depth + 0.55,
            height=gable_rise,
            base_z=base_z,
            mat=mats["roof_skin"],
            gable_mat=mats["rear"],
        )
    ]
    objects.extend(
        add_gable_seams(
            "MillRoof",
            width=width + 0.50,
            depth=depth + 0.50,
            rise=gable_rise,
            base_z=base_z,
            mat=mats["metal"],
            spacing=2.50,
        )
    )
    monitor_z = base_z + height - 0.78
    objects.extend(
        [
            box(
                "MillMonitorFrontGlass",
                (19.0, 0.16, 1.10),
                (0, -1.48, monitor_z),
                mats["glass"],
                bevel=0.035,
            ),
            box(
                "MillMonitorRearGlass",
                (19.0, 0.16, 1.10),
                (0, 1.48, monitor_z),
                mats["glass_alt"],
                bevel=0.035,
            ),
            box(
                "MillMonitorRoof",
                (19.5, 3.30, 0.18),
                (0, 0, base_z + height - 0.12),
                mats["metal"],
                bevel=0.05,
            ),
            box(
                "MillChimney",
                (1.45, 1.45, height),
                (10.8, 5.8, base_z + height / 2),
                mats["rear"],
                bevel=0.06,
            ),
        ]
    )
    for index, x in enumerate((-8.0, -4.0, 0.0, 4.0, 8.0)):
        objects.extend(
            [
                box(
                    f"MillMonitorMullionFront_{index}",
                    (0.10, 0.24, 1.18),
                    (x, -1.52, monitor_z),
                    mats["metal"],
                ),
                box(
                    f"MillMonitorMullionRear_{index}",
                    (0.10, 0.24, 1.18),
                    (x, 1.52, monitor_z),
                    mats["metal"],
                ),
            ]
        )
    return objects


def build_scandi_roof(
    mats: dict[str, bpy.types.Material],
    *,
    base_z: float,
) -> list[bpy.types.Object]:
    cfg = FAMILIES["scandinavian-urban-residential"]
    width, depth = cfg["dimensions"]
    height = cfg["roof_height_m"]
    objects = [
        gable_roof_shell(
            "ScandiStandingSeamRoof",
            width=width + 0.50,
            depth=depth + 0.50,
            height=height - 0.20,
            base_z=base_z,
            mat=mats["roof_skin"],
        )
    ]
    objects.extend(
        add_gable_seams(
            "ScandiRoof",
            width=width + 0.45,
            depth=depth + 0.45,
            rise=height - 0.20,
            base_z=base_z,
            mat=mats["metal"],
            spacing=1.35,
        )
    )
    dormer_y = -5.55
    dormer_base = base_z + 2.20
    for index, x in enumerate((-14.4, -7.2, 0.0, 7.2, 14.4)):
        objects.append(
            box(
                f"ScandiDormerBody_{index}",
                (3.00, 3.10, 2.28),
                (x, dormer_y + 1.10, dormer_base + 1.14),
                mats["body"],
                bevel=0.045,
            )
        )
        objects.extend(
            rectangular_window(
                f"ScandiDormerWindow_{index}",
                axis="front",
                lateral=x,
                plane=dormer_y - 0.48,
                sill_z=dormer_base + 0.36,
                width=1.45,
                height=1.42,
                mats=mats,
                trim="trim",
                mullions=1,
                transoms=0,
                alt_glass=index % 2 == 0,
                heavy_surround=True,
            )
        )
        # Small timber-edged dormer gables read clearly in aerial and street views.
        objects.extend(
            [
                beam(
                    f"ScandiDormerRoofLeft_{index}",
                    (x - 1.65, dormer_y - 0.62, dormer_base + 2.18),
                    (x, dormer_y - 0.62, dormer_base + 3.00),
                    0.10,
                    mats["trim"],
                ),
                beam(
                    f"ScandiDormerRoofRight_{index}",
                    (x, dormer_y - 0.62, dormer_base + 3.00),
                    (x + 1.65, dormer_y - 0.62, dormer_base + 2.18),
                    0.10,
                    mats["trim"],
                ),
                box(
                    f"ScandiDormerCap_{index}",
                    (3.45, 3.45, 0.14),
                    (x, dormer_y + 1.00, dormer_base + 2.35),
                    mats["roof"],
                    bevel=0.035,
                ),
            ]
        )
    # Downpipes belong to the facade/roof system rather than floating details.
    for side, x in enumerate((-18.55, 18.55)):
        pipe_height = base_z + 0.20
        objects.append(
            cylinder(
                f"ScandiDownpipe_{side}",
                0.065,
                pipe_height,
                (x, -depth / 2 - 0.18, pipe_height / 2),
                mats["metal"],
                vertices=16,
            )
        )
    return objects


def build_roof_module(
    family: str,
    mats: dict[str, bpy.types.Material],
    *,
    base_z: float = 0.0,
) -> list[bpy.types.Object]:
    if family == "industrial-brick-mixed-use":
        return build_industrial_roof(mats, base_z=base_z)
    if family == "scandinavian-urban-residential":
        return build_scandi_roof(mats, base_z=base_z)
    return build_flat_roof(family, mats, base_z=base_z)


def build_canonical(
    family: str,
    mats: dict[str, bpy.types.Material],
) -> tuple[list[bpy.types.Object], list[dict]]:
    cfg = FAMILIES[family]
    objects: list[bpy.types.Object] = []
    stack: list[dict] = []
    z = 0.0

    def append_role(role: str, variant: str, height: float) -> None:
        nonlocal z
        if role == "roof":
            objects.extend(build_roof_module(family, mats, base_z=z))
        else:
            objects.extend(
                build_band_module(
                    family,
                    mats,
                    role=role,
                    variant=variant,
                    base_z=z,
                )
            )
        stack.append(
            {
                "role": role,
                "variant_key": variant,
                "level": len(stack),
                "z_m": round(z, 4),
                "height_m": height,
            }
        )
        z += height

    append_role("podium", "default", cfg["podium_height_m"])
    for variant in cfg["canonical_floor_variants"]:
        append_role("floor", variant, cfg["floor_height_m"])
    append_role("crown", "crown", cfg["crown_height_m"])
    append_role("roof", "default", cfg["roof_height_m"])
    return objects, stack


def evaluated_triangle_count(objects: list[bpy.types.Object]) -> int:
    """Count evaluated geometry so bevelled construction detail is represented."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total = 0
    for obj in objects:
        if obj.type != "MESH":
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            total += sum(max(1, len(poly.vertices) - 2) for poly in mesh.polygons)
        finally:
            evaluated.to_mesh_clear()
    return total


def material_count(objects: list[bpy.types.Object]) -> int:
    return len(
        {
            slot.material.name
            for obj in objects
            if obj.type == "MESH"
            for slot in obj.material_slots
            if slot.material is not None
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
    width, depth = cfg["dimensions"]
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


def footprint_contract(family: str) -> dict:
    cfg = FAMILIES[family]
    values = cfg["footprint"]
    width = values["recommendedWidth_m"]
    depth = values["recommendedDepth_m"]
    floors = values["recommendedFloors"]
    wing = values["wingDepth_m"]
    courtyard = values["minimumCourtyard_m"]
    return {
        "preferredProfiles": ["rectangle", "l_shape", "u_shape"],
        "minimumPreferredProfiles": 3,
        "profileRationale": (
            "The reference-locked entrance, corner returns, crown and roof remain "
            "fixed semantic modules; ordinary registered bays repeat along the long "
            "streetwall axis and turn corners with authored secondary elevations."
        ),
        "recommendedWidth_m": width,
        "recommendedDepth_m": depth,
        "recommendedFloors": floors,
        "wingDepth_m": wing,
        "preferredBayMultiple_m": values["preferredBayMultiple_m"],
        "minimumCourtyard_m": courtyard,
        "profiles": {
            "rectangle": {
                "recommendedWidth_m": width,
                "recommendedDepth_m": depth,
                "recommendedFloors": floors,
            },
            "l_shape": {
                "recommendedWidth_m": [max(width[0] * 2, width[0] + 8), width[1] * 1.55],
                "recommendedDepth_m": [max(depth[0], 16), depth[1] * 1.35],
                "recommendedFloors": floors,
                "wingDepth_m": wing,
            },
            "u_shape": {
                "recommendedWidth_m": [max(width[0] * 2.4, 24), width[1] * 1.9],
                "recommendedDepth_m": [max(depth[0], 18), depth[1] * 1.5],
                "recommendedFloors": floors,
                "wingDepth_m": wing,
                "minimumCourtyard_m": courtyard,
            },
        },
        "notes": [
            "Preserve the selected entrance and full roof identity as fixed semantic pieces.",
            (
                f"Vary width in whole {values['preferredBayMultiple_m']:.2f} metre "
                "bays and height in whole floor modules."
            ),
            "Use authored left/right/rear bands on returns; never wrap the public front.",
        ],
    }


def source_provenance(family: str) -> dict:
    cfg = FAMILIES[family]
    return {
        "kind": "reviewed_render_locked_elevation_plus_authored_modular_geometry",
        "catalogue_archetype_id": cfg["archetype_id"],
        "catalogue_variant_id": cfg["variant_id"],
        "goalpost": (
            f"/archetypes/buildings/{cfg['catalogue_dir']}/"
            f"{cfg['catalogue_variant']}.png"
        ),
        "goalpost_local_source": "textures/source/archetype-goalpost.png",
        "angle_reference": "textures/source/angle-reference-60.jpg",
        "roof_reference": "textures/source/angle-reference-90.jpg",
        "orthographic_elevation": "textures/source/elevation-source.png",
        "registered_openings": "textures/source/registered-openings.json",
        "registered_bands": "textures/source/registered-bands.json",
        "skin_manifest": "textures/skin_manifest.json",
        "generator": "tools/archetype_compiler/generate_wave4_standard_batch.py",
    }


def facade_contract(family: str, skin: dict) -> dict:
    cfg = FAMILIES[family]
    bay = cfg["footprint"]["preferredBayMultiple_m"]
    special = {
        "brownstone-rowhouse-frontage": (
            "The central stoop/door, sandstone trim, five-bay sash alignment and "
            "bracketed cornice remain fixed; ordinary sash bays may repeat."
        ),
        "industrial-brick-mixed-use": (
            "The six-bay pier rhythm, entrance bay, gabled ends and roof monitor "
            "remain coordinated; complete segmental-window bays may repeat."
        ),
        "contemporary-midrise-residential": (
            "The limestone arch and wide/narrow opening cadence stay fixed while "
            "ordinary brick-and-bronze residential bays repeat."
        ),
        "scandinavian-urban-residential": (
            "The through-passage, balcony stacks and five-dormer roof composition "
            "remain fixed; ordinary plaster window bays repeat between them."
        ),
    }[family]
    return {
        "schema": "facade-sheet@5",
        "source_directory": f"/families/{family}",
        "model": "gpt-image-2",
        "style_reference": "elevation.jpg",
        "goalpost_reference": (
            f"/archetypes/buildings/{cfg['catalogue_dir']}/"
            f"{cfg['catalogue_variant']}.png"
        ),
        "goalpost_policy": (
            "The selected catalogue front, 60-degree oblique and roof view control "
            "massing, bay count, entrances, roof orientation and material hierarchy."
        ),
        "runtime_material_profile": "pbr_physical_glazing_v2",
        "geometry_detail_profile": "hero",
        "pbr_channels": ["albedo", "normal", "roughness", "ao", "depth", "emissive"],
        "shadow_neutral": {
            "enabled": True,
            "method": "render-locked orthographic source and deterministic PBR derivation",
            "lighting_authority": "City Prompt environment and sun",
        },
        "bay_strategy": {
            "fixed_end_bays": [0, -1],
            "repeatable_middle_bays": [1, 2, 3],
            "middle_variants": ["typical_a", "typical_b", "typical_c"],
            "preferred_bay_multiple_m": bay,
            "rule": special,
        },
        "delivery": {
            "near_atlas_width_px": 2048,
            "far_atlas_width_px": 1024,
            "near_usage": "close-range registered skin and physical glazing",
            "far_usage": "city-scale baked facade bands",
            "container": "PNG sources embedded into delivery GLBs; KTX2/UASTC at runtime packaging",
        },
        "assembly_contract": {
            "fixed": ["podium/entrance", "corner returns", "crown", "roof"],
            "repeatable": ["typical_a", "typical_b", "typical_c"],
            "side_elevations": (
                "front, left, right, rear and roof are authored as related but "
                "different elevations; the public entrance atlas never wraps"
            ),
            "elevation_coverage": {
                "front": "registered public elevation with physical openings and entrance",
                "left": "authored quiet secondary skin with occupied punched openings",
                "right": "authored quiet secondary skin with occupied punched openings",
                "rear": "authored restrained service/courtyard elevation",
                "roof": "reference-specific roof form, drainage and service elements",
            },
            "abutting_policy": "author every elevation; site geometry alone controls occlusion",
        },
        "assets": {
            "skin_manifest": "textures/skin_manifest.json",
            "source": skin["source"],
            "near": skin["atlases"]["near"],
            "far": skin["atlases"]["far"],
            "semantic_masks": {
                "glass_mask": skin["atlases"]["near"]["glass_mask"],
                "opaque_mask": skin["atlases"]["near"]["opaque_mask"],
            },
        },
        "reference_registration": skin["reference_registration"],
    }


def setup_standard_render() -> None:
    setup_render()
    scene = bpy.context.scene
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.view_settings.exposure = 0.62
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.22, 0.30, 0.38, 1)
    background.inputs["Strength"].default_value = 0.58
    ground = bpy.data.materials.get("MAT_W3_Ground")
    if ground:
        _principled(ground).inputs["Base Color"].default_value = (0.40, 0.38, 0.34, 1)
    bpy.ops.object.light_add(
        type="SUN",
        location=(-35, -45, 60),
        rotation=(math.radians(27), math.radians(-17), math.radians(-36)),
    )
    sun = bpy.context.object
    sun.name = "PRESENTATION_Wave4BatchSun"
    sun.data.color = (1.0, 0.80, 0.62)
    sun.data.energy = 2.05
    sun.data.angle = math.radians(7)
    key = bpy.data.objects.get("PRESENTATION_Key")
    if key:
        key.data.color = (1.0, 0.82, 0.66)
        key.data.energy = 5900
    fill = bpy.data.objects.get("PRESENTATION_Fill")
    if fill:
        fill.data.color = (0.70, 0.84, 1.0)
        fill.data.energy = 2200


def render_views(
    family: str,
    family_dir: Path,
    *,
    selected_roles: set[str] | None = None,
) -> list[str]:
    cfg = FAMILIES[family]
    width, depth = cfg["dimensions"]
    height = (
        cfg["podium_height_m"]
        + len(cfg["canonical_floor_variants"]) * cfg["floor_height_m"]
        + cfg["crown_height_m"]
        + cfg["roof_height_m"]
    )
    setup_standard_render()
    # Keep the full envelope, roof and projecting entrance/balconies in frame.
    # A depth-only distance made narrow rowhouses read as accidental close-ups.
    distance = max(width, depth, height * 1.35) * 1.95
    views = {
        "preview": (
            (width * 0.72, -distance * 1.05, height * 0.72),
            (0, 0, height * 0.42),
            55,
        ),
        "front_corner_oblique": (
            (width * 1.12, -distance * 0.94, height * 0.78),
            (0, 0, height * 0.42),
            53,
        ),
        "rear_corner_oblique": (
            (-width * 1.08, distance * 0.95, height * 0.82),
            (0, 0, height * 0.43),
            54,
        ),
        "facade_close": (
            (0, -distance * 0.96, height * 0.44),
            (0, -depth * 0.16, height * 0.44),
            60,
        ),
        "street": (
            (-width * 0.64, -distance * 0.86, height * 0.18),
            (0, -depth * 0.12, height * 0.30),
            49,
        ),
        "aerial": (
            (width * 1.05, -distance * 0.72, height * 2.45),
            (0, 0, height * 0.26),
            49,
        ),
        "context": (
            (width * 1.42, -distance * 1.10, height * 0.96),
            (0, 0, height * 0.37),
            58,
        ),
    }
    outputs: list[str] = []
    for role, (location, target, lens) in views.items():
        if selected_roles is not None and role not in selected_roles:
            continue
        aim_camera(location, target, lens)
        filename = f"{family}_{role}.png"
        bpy.context.scene.render.filepath = str(family_dir / filename)
        bpy.ops.render.render(write_still=True)
        outputs.append(filename)
    return outputs


def build_family(
    family: str,
    output_root: Path,
    view_set: str,
    skip_renders: bool,
    skip_modules: bool,
) -> None:
    clear_scene()
    cfg = FAMILIES[family]
    family_dir = output_root / family
    family_dir.mkdir(parents=True, exist_ok=True)
    mats, skin = palette(family, family_dir)
    canonical, stack = build_canonical(family, mats)
    assembled_path = family_dir / f"{family}_assembled.glb"
    export_glb(assembled_path, canonical)
    assembled_tris = evaluated_triangle_count(canonical)
    assembled_materials = material_count(canonical)
    if skip_renders:
        renders = sorted(path.name for path in family_dir.glob(f"{family}_*.png"))
    else:
        selected = None
        if view_set == "pilot":
            selected = {"preview", "front_corner_oblique", "facade_close", "aerial"}
        renders = render_views(family, family_dir, selected_roles=selected)
        delete_objects(
            [
                obj
                for obj in list(bpy.data.objects)
                if obj.name.startswith("PRESENTATION_")
            ]
        )
    if "elevation.jpg" not in renders:
        renders.append("elevation.jpg")
    if skip_modules:
        print(
            f"[wave4-standard-batch-pilot] {family}: {assembled_tris:,} tris, "
            f"{len(renders)} renders",
            flush=True,
        )
        return
    delete_objects(canonical)

    role_specs = (
        ("podium", "default", cfg["podium_height_m"]),
        ("floor", "typical_a", cfg["floor_height_m"]),
        ("floor", "typical_b", cfg["floor_height_m"]),
        ("floor", "typical_c", cfg["floor_height_m"]),
        ("setback", "setback_upper", cfg["floor_height_m"]),
        ("crown", "crown", cfg["crown_height_m"]),
        ("roof", "default", cfg["roof_height_m"]),
    )
    modules: list[dict] = []
    for role, variant, height in role_specs:
        if role == "roof":
            objects = build_roof_module(family, mats)
        else:
            objects = build_band_module(
                family,
                mats,
                role=role,
                variant=variant,
                setback=role == "setback",
            )
        objects.extend(module_contract_markers(role, variant, height))
        filename = (
            f"{family}_{role}.glb"
            if variant == "default"
            else f"{family}_{role}_{variant}.glb"
        )
        destination = family_dir / filename
        export_glb(destination, objects)
        modules.append(
            module_payload(
                family,
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

    width, depth = cfg["dimensions"]
    assembled_height = sum(float(item["height_m"]) for item in stack)
    footprint = footprint_contract(family)
    provenance = source_provenance(family)
    assembled = {
        "filename": assembled_path.name,
        "floors": cfg["native_floors"],
        "uses_setback": False,
        "uses_crown": True,
        "height_m": assembled_height,
        "triangle_count": assembled_tris,
        "material_count": assembled_materials,
        "stack": stack,
        "footprint_profile": "rectangle",
        "footprint_target": {
            "width_m": width,
            "depth_m": depth,
            "wing_depth_m": depth,
            "segments": [
                {
                    "id": "main",
                    "centre_x_m": 0.0,
                    "centre_y_m": 0.0,
                    "length_m": width,
                    "thickness_m": depth,
                    "rotation_degrees": 0.0,
                }
            ],
        },
        "massing_graph": {
            "type": "modular_streetwall",
            "profile": cfg["profile"],
        },
        "texture_keys": sorted(skin["zones"]),
        "ao_baked": True,
    }
    manifest = {
        "manifest_schema": 3,
        "grammar_schema_version": 3,
        "generator": {
            "name": "archetype_compiler/generate_wave4_standard_batch.py",
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
            "wave4",
            "standard_building",
            "modular_streetwall",
            "custom_pbr_skin",
            "reference_locked",
            *cfg["kits"],
        ],
        "footprint_compatibility": footprint,
        "coordinate_contract": COORDINATE_CONTRACT,
        "textures": texture_inventory(skin),
        "facade_sheet": facade_contract(family, skin),
        "massing_graph": {
            "type": "modular_streetwall",
            "profile": cfg["profile"],
            "render_locked": True,
            "goalpost": provenance["goalpost"],
            "fixed": ["podium/entrance", "corner returns", "crown", "roof"],
            "repeatable": ["typical_a", "typical_b", "typical_c"],
        },
        "material_budget": {
            "max_assembled_materials": 28,
            "rationale": (
                "Registered semantic bands, four authored elevations, physical "
                "glazing, entrance construction and reference-specific roof "
                "materials remain separate to preserve close-range depth."
            ),
        },
        "dimensions": {
            "width_m": width,
            "depth_m": depth,
            "podium_height_m": cfg["podium_height_m"],
            "floor_height_m": cfg["floor_height_m"],
            "setback_height_m": cfg["floor_height_m"],
            "roof_height_m": cfg["roof_height_m"],
            "crown_height_m": cfg["crown_height_m"],
            "default_floors": cfg["native_floors"],
            "min_floors": cfg["min_floors"],
            "max_floors": cfg["max_floors"],
        },
        "native_width_m": width,
        "native_depth_m": depth,
        "native_floors": cfg["native_floors"],
        "min_floors": cfg["min_floors"],
        "max_floors": cfg["max_floors"],
        "default_floors": cfg["native_floors"],
        "modules": modules,
        "assembled": assembled,
        "thumbnail": f"{family}_preview.png",
        "renders": renders,
        "architectural_identity": cfg["identity"],
        "material_zones": cfg["materials"],
        "glass_profile": cfg["glass_profile"],
        "source_provenance": provenance,
    }
    (family_dir / f"{family}_manifest.json").write_text(
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
    (family_dir / "grammar.json").write_text(
        json.dumps(grammar, indent=2) + "\n",
        encoding="utf-8",
    )
    (family_dir / "archetype-source.json").write_text(
        json.dumps(provenance, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"[wave4-standard-batch] {family}: {assembled_tris:,} tris, "
        f"{len(modules)} modules, {len(renders)} renders",
        flush=True,
    )


def render_existing(family: str, output_root: Path, view_set: str) -> None:
    clear_scene()
    family_dir = output_root / family
    manifest_path = family_dir / f"{family}_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    bpy.ops.import_scene.gltf(
        filepath=str(family_dir / manifest["assembled"]["filename"])
    )
    selected = None
    if view_set == "pilot":
        selected = {"preview", "front_corner_oblique", "facade_close", "aerial"}
    renders = render_views(family, family_dir, selected_roles=selected)
    if "elevation.jpg" not in renders:
        renders.append("elevation.jpg")
    if view_set == "all":
        manifest["renders"] = renders
        manifest_path.write_text(
            json.dumps(manifest, indent=2) + "\n",
            encoding="utf-8",
        )
    print(f"[wave4-standard-batch-render] {family}: {len(renders)} renders", flush=True)


def main() -> int:
    args = parse_args()
    # Blender may change its process working directory while loading startup
    # state; bind every texture/export path to the invocation directory first.
    args.output_root = args.output_root.resolve()
    families = args.family or list(FAMILIES)
    for family in families:
        if args.render_existing:
            render_existing(family, args.output_root, args.view_set)
        else:
            build_family(
                family,
                args.output_root,
                args.view_set,
                args.skip_renders,
                args.skip_modules,
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
