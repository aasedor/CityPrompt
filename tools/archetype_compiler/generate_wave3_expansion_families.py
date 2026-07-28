"""Generate the Wave 3 concert hall, Barcelona mercat and grand station.

Each family ships two complementary representations:

* a fixed assembled landmark whose geometry owns the catalogue silhouette; and
* a conservative podium / three-floor-variant / crown / roof LEGO fallback kit.

The fixed landmark is the normal path for these one-off civic forms.  The
fallback kit exists so the assembly planner can still satisfy oversized or
height-adjusted requests without ever falling back to a generic family.

Run with Blender 5.x:

  blender --background --factory-startup --python \
    tools/archetype_compiler/generate_wave3_expansion_families.py -- \
    --output-root frontend/public/families --family concert-hall-modern
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
    arch_frame,
    arched_panel,
    beam,
    box,
    cylinder,
    delete_objects,
    export_glb,
    load_skin_manifest,
    material,
    module_contract_markers,
    normalize_world_bounds,
    render_views,
    select_only,
    setup_render,
    shift_to_ground,
    skin_material,
    sphere,
    tapered_ellipse,
    triangle_count,
    triangular_prism,
)


FAMILIES = {
    "concert-hall-modern": {
        "archetype_id": "concert_hall_modern",
        "variant_id": "concert_sculptural_organic",
        "generation_archetype_id": "concert_sculptural_organic",
        "label": "Concert Hall (Modern) — Sculptural Organic",
        "dimensions": (90.0, 65.0, 48.0),
        "floors": (3, 8, 5),
        "floor_height_m": 6.0,
        "development_type": "recreational",
        "aesthetic_category_id": "contemporary_cultural",
        "reuse_keys": [
            "concert_hall_modern",
            "concert_sculptural_organic",
            "Entertainment / Culture",
        ],
        "aliases": ["concert_hall_modern", "concert_sculptural_organic"],
        "profiles": {
            "recommendedWidth_m": [60, 126],
            "recommendedDepth_m": [45, 91],
            "recommendedFloors": [3, 8],
        },
        "fixed_landmark_scale_band": {
            "scaleMin": 0.80,
            "scaleMax": 1.20,
            "maxAxisRatio": 1.18,
        },
        "identity": (
            "A low civic concert hall formed by overlapping pearlescent-white "
            "aluminum shell ribbons, three asymmetric acoustic peaks, a "
            "full-height recessed glass lobby, and visible ash-timber ribs."
        ),
        "materials": (
            "pearlescent satin aluminum panels; clear low-iron curtain wall; "
            "dark bronze mullions; honey ash acoustic ribs; pale granite plinth"
        ),
        "glass": "low_iron_cultural_lobby",
        "goalpost": "/archetypes/buildings/concert_hall_modern/variant_0.png",
        "kits": [
            "flowing_shell_ribbons",
            "asymmetric_acoustic_peaks",
            "full_height_lobby",
            "timber_acoustic_ribs",
            "integrated_civic_stair",
        ],
    },
    "barcelona-mercat": {
        "archetype_id": "barcelona_mercat",
        "variant_id": "mercat_modernista",
        "generation_archetype_id": "mercat_modernista",
        "label": "Barcelona Mercat — Modernista Market",
        "dimensions": (65.0, 45.0, 24.0),
        "floors": (1, 2, 1),
        "floor_height_m": 7.2,
        "development_type": "commercial_retail",
        "aesthetic_category_id": "historical",
        "reuse_keys": [
            "barcelona_mercat",
            "mercat_modernista",
            "Commercial — Market / Specialty Retail",
        ],
        "aliases": ["barcelona_mercat", "mercat_modernista"],
        "profiles": {
            "recommendedWidth_m": [45, 90],
            "recommendedDepth_m": [30, 60],
            "recommendedFloors": [1, 2],
        },
        "fixed_landmark_scale_band": {
            "scaleMin": 0.80,
            "scaleMax": 1.20,
            "maxAxisRatio": 1.18,
        },
        "identity": (
            "A five-aisled Barcelona market hall with a real Modernista iron "
            "entrance pediment and arch, polychrome stained glass, tiled "
            "perimeter arcade, open produce hall and ornate ridge cresting."
        ),
        "materials": (
            "dark green-black wrought iron; clear and polychrome glass; "
            "terracotta-and-cream glazed ceramic tile; warm stone plinth"
        ),
        "glass": "polychrome_heritage_market",
        "goalpost": "/archetypes/buildings/barcelona-mercat/variant_0.png",
        "kits": [
            "modernista_entrance_arch",
            "five_aisle_roof",
            "cast_iron_arcade",
            "polychrome_stained_glass",
            "ridge_cresting",
        ],
    },
    "historic-grand-station": {
        "archetype_id": "historic_grand_station",
        "variant_id": "station_beaux_arts",
        "generation_archetype_id": "station_beaux_arts",
        "label": "Historic Grand Station — Beaux-Arts Terminal",
        "dimensions": (200.0, 80.0, 58.0),
        "floors": (2, 5, 3),
        "floor_height_m": 5.8,
        "development_type": "transit_station",
        "aesthetic_category_id": "transportation",
        "reuse_keys": [
            "historic_grand_station",
            "station_beaux_arts",
            "Transportation",
        ],
        "aliases": ["historic_grand_station", "station_beaux_arts"],
        "profiles": {
            "recommendedWidth_m": [120, 280],
            "recommendedDepth_m": [50, 112],
            "recommendedFloors": [2, 5],
        },
        "fixed_landmark_scale_band": {
            "scaleMin": 0.80,
            "scaleMax": 1.20,
            "maxAxisRatio": 1.18,
        },
        "identity": (
            "A monumental pale-granite Beaux-Arts terminal with a five-bay "
            "ceremonial entrance of deeply carved arched portals, paired "
            "Corinthian columns, a sculpted clock attic, and three immense "
            "iron-and-glass barrel-vault train sheds."
        ),
        "materials": (
            "pale warm granite ashlar; carved stone relief; weathered bronze "
            "doors and fanlights; charcoal iron ribs; clear smoky shed glass"
        ),
        "glass": "beaux_arts_bronze_and_shed_glass",
        "goalpost": "/archetypes/buildings/historic_grand_station/variant_0.png",
        "kits": [
            "three_carved_portals",
            "paired_corinthian_order",
            "sculpted_clock_attic",
            "three_barrel_vault_sheds",
            "integrated_ceremonial_steps",
        ],
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--family", action="append", choices=sorted(FAMILIES))
    parser.add_argument(
        "--view-set",
        choices=("all", "pilot"),
        default="all",
        help="pilot renders preview, front-corner, facade and aerial only",
    )
    parser.add_argument(
        "--skip-renders",
        action="store_true",
        help="re-export GLBs/manifests while retaining the existing reviewed view set",
    )
    parser.add_argument(
        "--render-existing",
        action="store_true",
        help="refresh renders from the existing assembled GLB without rebuilding geometry",
    )
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


def _principled(mat: bpy.types.Material) -> bpy.types.Node:
    return next(
        node
        for node in mat.node_tree.nodes
        if node.bl_idname == "ShaderNodeBsdfPrincipled"
    )


def _glazing_treatment(mat: bpy.types.Material, alpha: float = 0.76) -> bpy.types.Material:
    bsdf = _principled(mat)
    if bsdf.inputs.get("Alpha"):
        bsdf.inputs["Alpha"].default_value = alpha
    if bsdf.inputs.get("Transmission Weight"):
        bsdf.inputs["Transmission Weight"].default_value = 0.20
    if bsdf.inputs.get("Coat Weight"):
        bsdf.inputs["Coat Weight"].default_value = 0.42
    try:
        mat.surface_render_method = "DITHERED"
    except Exception:
        pass
    return mat


def _grade_base(
    mat: bpy.types.Material,
    *,
    saturation: float = 1.0,
    value: float = 1.0,
) -> bpy.types.Material:
    """Grade a registered atlas without replacing its PBR graph."""
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = _principled(mat)
    base = bsdf.inputs["Base Color"]
    if base.is_linked:
        source = base.links[0].from_socket
        links.remove(base.links[0])
        grade = nodes.new("ShaderNodeHueSaturation")
        grade.name = grade.label = "ARCHETYPE_REFERENCE_GRADE"
        grade.inputs["Saturation"].default_value = saturation
        grade.inputs["Value"].default_value = value
        links.new(source, grade.inputs["Color"])
        links.new(grade.outputs["Color"], base)
    emission = bsdf.inputs.get("Emission Color")
    if emission and emission.is_linked:
        source = emission.links[0].from_socket
        links.remove(emission.links[0])
        grade = nodes.new("ShaderNodeHueSaturation")
        grade.name = grade.label = "OCCUPANCY_EMISSION_GRADE"
        grade.inputs["Saturation"].default_value = min(1.0, saturation * 0.75)
        grade.inputs["Value"].default_value = min(0.34, value * 0.34)
        links.new(source, grade.inputs["Color"])
        links.new(grade.outputs["Color"], emission)
    return mat


def family_palette(family_dir: Path) -> dict[str, bpy.types.Material]:
    skin = load_skin_manifest(family_dir)
    if not skin:
        raise FileNotFoundError(f"{family_dir / 'textures' / 'skin_manifest.json'}")
    near = {zone: values["near"] for zone, values in skin["zones"].items()}
    common = {
        "dark": material("MAT_W3X_DarkSteel", (0.035, 0.045, 0.048, 1), 0.28, 0.78),
        "warm": material(
            "MAT_W3X_WarmInterior",
            (0.48, 0.22, 0.055, 1),
            0.48,
            emission=(1.0, 0.31, 0.06, 1),
            emission_strength=0.72,
        ),
        "bronze": material("MAT_W3X_Bronze", (0.16, 0.09, 0.035, 1), 0.33, 0.68),
        "black": material("MAT_W3X_Black", (0.012, 0.016, 0.018, 1), 0.24, 0.62),
        "cream": material("MAT_W3X_CreamStone", (0.48, 0.38, 0.25, 1), 0.72),
    }
    if family_dir.name == "concert-hall-modern":
        common.update(
            {
                "shell": _grade_base(
                    skin_material(
                        "MAT_W3X_ConcertAluminum",
                        family_dir,
                        near["aluminum"],
                        "aluminum",
                        metallic=0.16,
                    ),
                    saturation=0.70,
                    value=1.10,
                ),
                "glass": _glazing_treatment(
                    _grade_base(
                        skin_material(
                            "MAT_W3X_ConcertGlass",
                            family_dir,
                            near["concert_glass"],
                            "concert_glass",
                            metallic=0.04,
                            transmission=0.18,
                            emission_strength=0.18,
                        ),
                        saturation=0.32,
                        value=0.86,
                    ),
                    0.64,
                ),
                "timber": skin_material(
                    "MAT_W3X_ConcertTimber",
                    family_dir,
                    near["timber"],
                    "timber",
                ),
                "interior_timber": _grade_base(
                    skin_material(
                        "MAT_W3X_ConcertInteriorTimber",
                        family_dir,
                        near["timber"],
                        "timber",
                    ),
                    saturation=0.75,
                    value=0.68,
                ),
                "bronze": material(
                    "MAT_W3X_ConcertBronze",
                    (0.18, 0.075, 0.018, 1),
                    0.34,
                    0.72,
                ),
                # The reference exposes the acoustic lining beneath each
                # cantilever.  A modest self-lit finish keeps that underside
                # warm in shadow without turning it into a luminous ceiling.
                "soffit": material(
                    "MAT_W3X_ConcertShellUnderside",
                    (0.72, 0.70, 0.66, 1),
                    0.70,
                    0.03,
                    emission=(0.36, 0.34, 0.30, 1),
                    emission_strength=0.14,
                ),
                "concert_interior": material(
                    "MAT_W3X_ConcertOccupiedInterior",
                    (0.075, 0.034, 0.010, 1),
                    0.50,
                    0.04,
                    emission=(0.62, 0.16, 0.020, 1),
                    emission_strength=0.32,
                ),
                "stone": skin_material(
                    "MAT_W3X_ConcertGranite",
                    family_dir,
                    near["granite"],
                    "granite",
                ),
            }
        )
    elif family_dir.name == "barcelona-mercat":
        common.update(
            {
                "iron": skin_material(
                    "MAT_W3X_MercatIron",
                    family_dir,
                    near["iron"],
                    "iron",
                    metallic=0.62,
                ),
                "stained": _glazing_treatment(
                    _grade_base(
                        skin_material(
                            "MAT_W3X_MercatStainedGlass",
                            family_dir,
                            near["stained_glass"],
                            "stained_glass",
                            transmission=0.09,
                            emission_strength=0.38,
                        ),
                        saturation=0.80,
                        value=1.10,
                    ),
                    0.72,
                ),
                "tile": _grade_base(
                    skin_material(
                        "MAT_W3X_MercatCeramic",
                        family_dir,
                        near["ceramic"],
                        "ceramic",
                    ),
                    saturation=0.52,
                    value=0.88,
                ),
                "roof_glass": _glazing_treatment(
                    _grade_base(
                        skin_material(
                            "MAT_W3X_MercatRoofGlass",
                            family_dir,
                            near["roof_glass"],
                            "roof_glass",
                            transmission=0.28,
                            emission_strength=0.20,
                        ),
                        saturation=0.68,
                        value=0.88,
                    ),
                    0.62,
                ),
                "roof_metal": material(
                    "MAT_W3X_MercatWeatheredZinc",
                    (0.20, 0.22, 0.22, 1),
                    0.58,
                    0.48,
                ),
                "stained_red": material(
                    "MAT_W3X_MercatStainedRed",
                    (0.25, 0.012, 0.008, 0.90),
                    0.30,
                    0.04,
                    emission=(0.42, 0.018, 0.010, 1),
                    emission_strength=0.10,
                ),
                "stained_blue": material(
                    "MAT_W3X_MercatStainedBlue",
                    (0.012, 0.075, 0.30, 0.90),
                    0.30,
                    0.04,
                    emission=(0.015, 0.10, 0.48, 1),
                    emission_strength=0.10,
                ),
                "stained_gold": material(
                    "MAT_W3X_MercatStainedGold",
                    (0.34, 0.11, 0.008, 0.90),
                    0.32,
                    0.03,
                    emission=(0.54, 0.16, 0.010, 1),
                    emission_strength=0.10,
                ),
                "stained_green": material(
                    "MAT_W3X_MercatStainedGreen",
                    (0.012, 0.18, 0.045, 0.90),
                    0.32,
                    0.03,
                    emission=(0.018, 0.30, 0.065, 1),
                    emission_strength=0.09,
                ),
                "terracotta": material(
                    "MAT_W3X_MercatTerracottaRoof",
                    (0.26, 0.072, 0.026, 1),
                    0.72,
                    0.02,
                ),
                "market_interior": material(
                    "MAT_W3X_MercatOccupiedInterior",
                    (0.16, 0.065, 0.018, 1),
                    0.55,
                    0.02,
                    emission=(0.78, 0.20, 0.025, 1),
                    emission_strength=0.24,
                ),
                "produce_red": material(
                    "MAT_W3X_MercatProduceRed",
                    (0.48, 0.025, 0.012, 1),
                    0.68,
                ),
                "produce_green": material(
                    "MAT_W3X_MercatProduceGreen",
                    (0.08, 0.28, 0.035, 1),
                    0.72,
                ),
                "produce_gold": material(
                    "MAT_W3X_MercatProduceGold",
                    (0.72, 0.26, 0.018, 1),
                    0.66,
                ),
            }
        )
    else:
        common.update(
            {
                "stone": _grade_base(
                    skin_material(
                        "MAT_W3X_StationGranite",
                        family_dir,
                        near["granite"],
                        "granite",
                    ),
                    saturation=1.05,
                    value=0.94,
                ),
                "portal_glass": _glazing_treatment(
                    _grade_base(
                        skin_material(
                            "MAT_W3X_StationBronzeGlass",
                            family_dir,
                            near["bronze_glass"],
                            "bronze_glass",
                            transmission=0.12,
                            emission_strength=0.30,
                        ),
                        saturation=0.62,
                        value=0.88,
                    ),
                    0.70,
                ),
                "shed_glass": _glazing_treatment(
                    _grade_base(
                        skin_material(
                            "MAT_W3X_StationShedGlass",
                            family_dir,
                            near["iron_glass"],
                            "iron_glass",
                            transmission=0.20,
                            emission_strength=0.12,
                        ),
                        saturation=0.60,
                        value=0.72,
                    ),
                    0.72,
                ),
                "relief": skin_material(
                    "MAT_W3X_StationRelief",
                    family_dir,
                    near["relief"],
                    "relief",
                ),
                "station_interior": material(
                    "MAT_W3X_StationOccupiedInterior",
                    (0.035, 0.016, 0.008, 1),
                    0.50,
                    0.08,
                    emission=(0.22, 0.040, 0.004, 1),
                    emission_strength=0.06,
                ),
                "coffer": material(
                    "MAT_W3X_StationCofferedStone",
                    (0.48, 0.40, 0.30, 1),
                    0.76,
                ),
            }
        )
    return common


def mesh_object(
    name: str,
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, ...]],
    mat: bpy.types.Material,
    uv_by_vertex: list[tuple[float, float]] | None = None,
    *,
    smooth: bool = False,
    bevel: float = 0.0,
) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    mesh.materials.append(mat)
    if uv_by_vertex:
        layer = mesh.uv_layers.new(name="UVMap")
        for polygon in mesh.polygons:
            for loop_index in polygon.loop_indices:
                vertex_index = mesh.loops[loop_index].vertex_index
                layer.data[loop_index].uv = uv_by_vertex[vertex_index]
    if smooth:
        for polygon in mesh.polygons:
            polygon.use_smooth = True
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if bevel:
        modifier = obj.modifiers.new("ArchitecturalEdge", "BEVEL")
        modifier.width = bevel
        modifier.segments = 2
    return obj


def surface_volume(
    name: str,
    point: Callable[[float, float], tuple[float, float, float]],
    mat: bpy.types.Material,
    *,
    u_steps: int = 36,
    v_steps: int = 18,
    thickness: float = 0.55,
    uv_scale: tuple[float, float] = (3.0, 2.0),
    bottom_mat: bpy.types.Material | None = None,
) -> bpy.types.Object:
    """Create a closed, vertically thickened parametric shell patch."""
    top = [
        point(i / u_steps, j / v_steps)
        for i in range(u_steps + 1)
        for j in range(v_steps + 1)
    ]
    bottom = [(x, y, z - thickness) for x, y, z in top]
    vertices = top + bottom
    layer_size = len(top)
    uv = [
        (i / u_steps * uv_scale[0], j / v_steps * uv_scale[1])
        for i in range(u_steps + 1)
        for j in range(v_steps + 1)
    ]
    uv += uv
    faces: list[tuple[int, ...]] = []

    def idx(i: int, j: int) -> int:
        return i * (v_steps + 1) + j

    for i in range(u_steps):
        for j in range(v_steps):
            a, b = idx(i, j), idx(i + 1, j)
            c, d = idx(i, j + 1), idx(i + 1, j + 1)
            faces.append((a, b, d, c))
            faces.append(
                (
                    a + layer_size,
                    c + layer_size,
                    d + layer_size,
                    b + layer_size,
                )
            )
    for i in range(u_steps):
        for j in (0, v_steps):
            a, b = idx(i, j), idx(i + 1, j)
            faces.append((a, a + layer_size, b + layer_size, b))
    for j in range(v_steps):
        for i in (0, u_steps):
            a, b = idx(i, j), idx(i, j + 1)
            faces.append((a, b, b + layer_size, a + layer_size))
    obj = mesh_object(
        name,
        vertices,
        faces,
        mat,
        uv,
        smooth=True,
        bevel=0.05,
    )
    if bottom_mat is not None:
        obj.data.materials.append(bottom_mat)
        gridded_face_count = u_steps * v_steps * 2
        for polygon in obj.data.polygons[:gridded_face_count]:
            # Top and bottom quads are appended as alternating pairs.
            if polygon.index % 2:
                polygon.material_index = 1
    return obj


def vertical_shell_panel(
    name: str,
    x0: float,
    x1: float,
    y_front: Callable[[float], float],
    top_z: Callable[[float], float],
    mat: bpy.types.Material,
    *,
    thickness: float = 0.65,
    u_steps: int = 18,
    v_steps: int = 8,
) -> bpy.types.Object:
    front = []
    uv = []
    for i in range(u_steps + 1):
        u = i / u_steps
        x = x0 + (x1 - x0) * u
        top = top_z(u)
        for j in range(v_steps + 1):
            v = j / v_steps
            front.append((x, y_front(u), top * v))
            uv.append((u * 1.8, v * 1.5))
    back = [(x, y + thickness, z) for x, y, z in front]
    vertices = front + back
    uv += uv
    layer_size = len(front)
    faces: list[tuple[int, ...]] = []

    def idx(i: int, j: int) -> int:
        return i * (v_steps + 1) + j

    for i in range(u_steps):
        for j in range(v_steps):
            a, b = idx(i, j), idx(i + 1, j)
            c, d = idx(i, j + 1), idx(i + 1, j + 1)
            # The public facade is the negative-Y face. Keep its winding
            # outward so studio and City Prompt lighting describe the shell
            # relief instead of shading the visible side as an inward backface.
            faces.append((a, b, d, c))
            faces.append(
                (
                    a + layer_size,
                    c + layer_size,
                    d + layer_size,
                    b + layer_size,
                )
            )
    for i in range(u_steps):
        for j in (0, v_steps):
            a, b = idx(i, j), idx(i + 1, j)
            faces.append((a, b, b + layer_size, a + layer_size))
    for j in range(v_steps):
        for i in (0, u_steps):
            a, b = idx(i, j), idx(i, j + 1)
            faces.append((a, a + layer_size, b + layer_size, b))
    return mesh_object(name, vertices, faces, mat, uv, smooth=True, bevel=0.04)


def vertical_ribbon_panel(
    name: str,
    x0: float,
    x1: float,
    y_front: Callable[[float], float],
    bottom_z: Callable[[float], float],
    top_z: Callable[[float], float],
    mat: bpy.types.Material,
    *,
    thickness: float = 0.65,
    u_steps: int = 32,
    v_steps: int = 4,
) -> bpy.types.Object:
    """Create a closed flowing facade fascia between two authored profiles."""
    front: list[tuple[float, float, float]] = []
    uv: list[tuple[float, float]] = []
    for i in range(u_steps + 1):
        u = i / u_steps
        x = x0 + (x1 - x0) * u
        low = bottom_z(u)
        high = max(low + 0.10, top_z(u))
        for j in range(v_steps + 1):
            v = j / v_steps
            front.append((x, y_front(u), low + (high - low) * v))
            uv.append((u * 3.2, v))
    back = [(x, y + thickness, z) for x, y, z in front]
    vertices = front + back
    uv += uv
    layer_size = len(front)
    faces: list[tuple[int, ...]] = []

    def idx(i: int, j: int) -> int:
        return i * (v_steps + 1) + j

    for i in range(u_steps):
        for j in range(v_steps):
            a, b = idx(i, j), idx(i + 1, j)
            c, d = idx(i, j + 1), idx(i + 1, j + 1)
            faces.append((a, b, d, c))
            faces.append(
                (
                    a + layer_size,
                    c + layer_size,
                    d + layer_size,
                    b + layer_size,
                )
            )
    for i in range(u_steps):
        for j in (0, v_steps):
            a, b = idx(i, j), idx(i + 1, j)
            faces.append((a, a + layer_size, b + layer_size, b))
    for j in range(v_steps):
        for i in (0, u_steps):
            a, b = idx(i, j), idx(i, j + 1)
            faces.append((a, b, b + layer_size, a + layer_size))
    return mesh_object(name, vertices, faces, mat, uv, smooth=True, bevel=0.045)


def elliptical_ribbon_shell(
    name: str,
    radius_x: float,
    radius_y: float,
    bottom_z: Callable[[float], float],
    top_z: Callable[[float], float],
    mat: bpy.types.Material,
    *,
    thickness: float = 0.78,
    segments: int = 112,
    vertical_steps: int = 3,
) -> bpy.types.Object:
    """Build a closed organic ribbon around an elliptical landmark envelope."""
    outer: list[tuple[float, float, float]] = []
    inner: list[tuple[float, float, float]] = []
    uv: list[tuple[float, float]] = []
    for index in range(segments + 1):
        theta = math.tau * index / segments
        low = bottom_z(theta)
        high = max(low + 0.24, top_z(theta))
        for row in range(vertical_steps + 1):
            v = row / vertical_steps
            z = low + (high - low) * v
            outer.append((radius_x * math.cos(theta), radius_y * math.sin(theta), z))
            inner.append(
                (
                    (radius_x - thickness) * math.cos(theta),
                    (radius_y - thickness) * math.sin(theta),
                    z,
                )
            )
            uv.append((index / segments * 4.0, v))
    vertices = outer + inner
    uv += uv
    layer_size = len(outer)
    stride = vertical_steps + 1
    faces: list[tuple[int, ...]] = []
    for index in range(segments):
        for row in range(vertical_steps):
            a = index * stride + row
            b = (index + 1) * stride + row
            c = a + 1
            d = b + 1
            faces.append((a, b, d, c))
            faces.append(
                (
                    a + layer_size,
                    c + layer_size,
                    d + layer_size,
                    b + layer_size,
                )
            )
        low_a = index * stride
        low_b = (index + 1) * stride
        high_a = low_a + vertical_steps
        high_b = low_b + vertical_steps
        faces.append(
            (
                low_a,
                low_a + layer_size,
                low_b + layer_size,
                low_b,
            )
        )
        faces.append(
            (
                high_a,
                high_b,
                high_b + layer_size,
                high_a + layer_size,
            )
        )
    return mesh_object(
        name,
        vertices,
        faces,
        mat,
        uv,
        smooth=True,
        bevel=0.07,
    )


def quad_panel(
    name: str,
    points: tuple[
        tuple[float, float, float],
        tuple[float, float, float],
        tuple[float, float, float],
        tuple[float, float, float],
    ],
    mat: bpy.types.Material,
) -> bpy.types.Object:
    return mesh_object(
        name,
        list(points),
        [(0, 1, 2, 3)],
        mat,
        [(0, 0), (1, 0), (1, 1), (0, 1)],
    )


def _concert_front_y(x: float) -> float:
    return -29.8 + 4.4 * (abs(x) / 33.0) ** 1.7


def _concert_lobby_top(x: float) -> float:
    # The reference lobby rises into the left acoustic shell and falls toward
    # the right-hand sweep. A symmetric semicircle reads as a generic atrium.
    return (
        18.0
        + 9.0 * math.exp(-((x + 17.0) / 16.0) ** 2)
        + 3.0 * math.exp(-((x - 6.0) / 27.0) ** 2)
    )


def concert_lobby(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    columns, rows = 18, 5
    x_values = [-29.0 + 58.0 * i / columns for i in range(columns + 1)]
    for col in range(columns):
        xa, xb = x_values[col], x_values[col + 1]
        ya, yb = _concert_front_y(xa), _concert_front_y(xb)
        za, zb = _concert_lobby_top(xa), _concert_lobby_top(xb)
        for row in range(rows):
            low_a = 1.2 + (za - 1.2) * row / rows
            high_a = 1.2 + (za - 1.2) * (row + 1) / rows
            low_b = 1.2 + (zb - 1.2) * row / rows
            high_b = 1.2 + (zb - 1.2) * (row + 1) / rows
            objects.append(
                quad_panel(
                    f"CONCERT_LobbyPane_{col}_{row}",
                    (
                        (xa, ya, low_a),
                        (xb, yb, low_b),
                        (xb, yb, high_b),
                        (xa, ya, high_a),
                    ),
                    mats["glass"],
                )
            )
    for index, x in enumerate(x_values):
        y = _concert_front_y(x) - 0.05
        objects.append(
            beam(
                f"CONCERT_LobbyVertical_{index}",
                (x, y, 1.0),
                (x, y, _concert_lobby_top(x) - 0.18),
                0.105,
                mats["bronze"],
            )
        )
    for row in range(1, rows):
        fraction = row / rows
        for col in range(columns):
            xa, xb = x_values[col], x_values[col + 1]
            objects.append(
                beam(
                    f"CONCERT_LobbyTransom_{row}_{col}",
                    (
                        xa,
                        _concert_front_y(xa) - 0.04,
                        1.2 + (_concert_lobby_top(xa) - 1.2) * fraction,
                    ),
                    (
                        xb,
                        _concert_front_y(xb) - 0.04,
                        1.2 + (_concert_lobby_top(xb) - 1.2) * fraction,
                    ),
                    0.085,
                    mats["bronze"],
                )
            )

    # Separate occupied backing and real balcony edges provide depth through
    # the curtain wall instead of asking an opaque warm pane to do both jobs.
    objects.append(
        vertical_shell_panel(
            "CONCERT_OccupiedLobbyBackplate",
            -27.5,
            27.5,
            lambda u: -24.3 + 3.2 * abs(u - 0.5),
            lambda u: _concert_lobby_top(-27.5 + 55.0 * u) - 1.15,
            mats["interior_timber"],
            thickness=0.18,
            u_steps=20,
            v_steps=5,
        )
    )
    for level in (7.0, 12.5, 18.0, 23.2):
        objects.append(
            box(
                f"CONCERT_LobbyBalcony_{level}",
                (38.0 - level * 0.30, 3.0, 0.32),
                (0, -24.4 + level * 0.025, level),
                mats["timber"],
                0.08,
            )
        )
        objects.append(
            box(
                f"CONCERT_LobbyWarmCeiling_{level}",
                (20.0, 0.22, 0.16),
                (0, -24.9, level + 0.42),
                mats["warm"],
            )
        )
        objects.append(
            box(
                f"CONCERT_LobbyBalustrade_{level}",
                (37.0 - level * 0.30, 0.09, 1.05),
                (0, -28.0 + level * 0.025, level + 0.62),
                mats["glass"],
            )
        )
    for index, x in enumerate((-24, -17, -10, 0, 10, 17, 24)):
        y0 = _concert_front_y(x) + 1.0
        top = _concert_lobby_top(x) - 1.2
        mid = (y0 + 5.4, top * 0.60)
        objects.append(
            beam(
                f"CONCERT_TimberRibLower_{index}",
                (x, y0, 1.2),
                (x * 0.82, mid[0], mid[1]),
                0.19,
                mats["timber"],
            )
        )
        objects.append(
            beam(
                f"CONCERT_TimberRibUpper_{index}",
                (x * 0.82, mid[0], mid[1]),
                (x * 0.55, y0 + 10.0, top),
                0.19,
                mats["timber"],
            )
        )

    # Seven physically recessed entrance door leaves and bronze frames.
    door_width = 3.0
    for index in range(7):
        x = (index - 3) * 3.35
        objects.append(
            box(
                f"CONCERT_EntryDoorPane_{index}",
                (door_width, 0.12, 4.2),
                (x, -30.12, 3.30),
                mats["glass"],
            )
        )
        for edge in (-door_width / 2, door_width / 2):
            objects.append(
                box(
                    f"CONCERT_EntryDoorJamb_{index}_{edge}",
                    (0.08, 0.22, 4.35),
                    (x + edge, -30.22, 3.30),
                    mats["bronze"],
                )
            )
    objects.append(
        box(
            "CONCERT_EntryHeader",
            (24.2, 0.26, 0.16),
            (0, -30.22, 5.48),
            mats["bronze"],
        )
    )
    return objects


def concert_integrated_steps(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    count = 10
    for index in range(count):
        width = 38.0 + index * 0.45
        depth = 0.74
        rise = 0.15
        level = count - 1 - index
        objects.append(
            box(
                f"CONCERT_IntegratedStep_{index}",
                (width, depth, rise),
                (0, -31.0 - index * depth, rise / 2 + level * rise),
                mats["stone"],
                0.025,
            )
        )
    # Ramps are cut into the same plinth language, not tacked-on stairs.
    for side in (-1, 1):
        objects.append(
            surface_volume(
                f"CONCERT_IntegratedRamp_{side}",
                lambda u, v, side=side: (
                    side * (23.0 + u * 5.0),
                    -31.0 - v * 8.0,
                    1.55 - v * 1.45,
                ),
                mats["stone"],
                u_steps=4,
                v_steps=10,
                thickness=0.12,
                uv_scale=(1.0, 1.0),
            )
        )
        objects.append(
            beam(
                f"CONCERT_RampRail_{side}",
                (side * 28.2, -31.0, 2.55),
                (side * 28.2, -39.0, 1.10),
                0.055,
                mats["bronze"],
            )
        )
    return objects


def concert_side_glazing(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    radius_x, radius_y = 43.55, 29.25
    inner_x, inner_y = 42.45, 28.15
    segments = 72
    front_angle = -math.pi / 2

    def angle_distance(a: float, b: float) -> float:
        return abs((a - b + math.pi) % math.tau - math.pi)

    for row, (bottom, top) in enumerate(((8.0, 11.3), (15.7, 19.1), (23.0, 26.4))):
        for index in range(segments):
            theta_a = math.tau * index / segments
            theta_b = math.tau * (index + 1) / segments
            theta_mid = (theta_a + theta_b) * 0.5
            if angle_distance(theta_mid, front_angle) < 1.48:
                continue
            xa, ya = radius_x * math.cos(theta_a), radius_y * math.sin(theta_a)
            xb, yb = radius_x * math.cos(theta_b), radius_y * math.sin(theta_b)
            xia, yia = inner_x * math.cos(theta_a), inner_y * math.sin(theta_a)
            xib, yib = inner_x * math.cos(theta_b), inner_y * math.sin(theta_b)
            objects.append(
                quad_panel(
                    f"CONCERT_CurvedGlass_{row}_{index}",
                    (
                        (xa, ya, bottom),
                        (xb, yb, bottom),
                        (xb, yb, top),
                        (xa, ya, top),
                    ),
                    mats["glass"],
                )
            )
            objects.append(
                quad_panel(
                    f"CONCERT_CurvedOccupiedBack_{row}_{index}",
                    (
                        (xia, yia, bottom + 0.24),
                        (xib, yib, bottom + 0.24),
                        (xib, yib, top - 0.24),
                        (xia, yia, top - 0.24),
                    ),
                    mats["concert_interior"],
                )
            )
            if index % 2 == 0:
                objects.append(
                    beam(
                        f"CONCERT_CurvedMullion_{row}_{index}",
                        (xa, ya, bottom - 0.10),
                        (xa, ya, top + 0.10),
                        0.09,
                        mats["bronze"],
                    )
                )
            objects.append(
                beam(
                    f"CONCERT_CurvedTransomLow_{row}_{index}",
                    (xa, ya, bottom),
                    (xb, yb, bottom),
                    0.07,
                    mats["bronze"],
                )
            )
            objects.append(
                beam(
                    f"CONCERT_CurvedTransomHigh_{row}_{index}",
                    (xa, ya, top),
                    (xb, yb, top),
                    0.07,
                    mats["bronze"],
                )
            )
    return objects


def concert_fixed(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    objects.append(
        tapered_ellipse(
            "CONCERT_GranitePlinth",
            [(0.0, 44.0, 30.75), (1.15, 44.0, 30.75)],
            mats["stone"],
            segments=128,
        )
    )
    objects.extend(concert_lobby(mats))
    objects.extend(concert_integrated_steps(mats))
    objects.extend(concert_side_glazing(mats))

    def front_weight(theta: float) -> float:
        return max(0.0, -math.sin(theta)) ** 3.2

    def rear_weight(theta: float) -> float:
        return max(0.0, math.sin(theta)) ** 2.4

    def left_front_peak(theta: float) -> float:
        x_fraction = math.cos(theta)
        return front_weight(theta) * math.exp(-((x_fraction + 0.34) / 0.32) ** 2)

    def folded_sail_peak(
        u: float,
        v: float,
        centre_u: float,
        lean: float,
        half_width: float,
        centre_v: float,
        v_width: float,
        amplitude: float,
    ) -> float:
        """Sharp leaning ridge with broad shell planes on either side."""

        ridge_u = centre_u + lean * v
        cross_section = max(0.0, 1.0 - abs(u - ridge_u) / half_width) ** 1.18
        longitudinal = math.exp(-((v - centre_v) / v_width) ** 2)
        return amplitude * cross_section * longitudinal

    # Three continuous shell loops now own the rounded plan silhouette. Their
    # heights change around the building, so front, sides and rear remain one
    # constructed envelope instead of unrelated facade strips.
    objects.extend(
        [
            elliptical_ribbon_shell(
                "CONCERT_LowerEnvelopeLoop",
                44.35,
                30.15,
                lambda theta: (
                    3.7
                    + 3.3 * front_weight(theta)
                    + 0.35 * math.cos(theta + 0.4)
                ),
                lambda theta: (
                    8.45
                    + 1.6 * front_weight(theta)
                    + 2.7 * left_front_peak(theta)
                    + 1.4 * rear_weight(theta)
                    + 0.75 * math.cos(theta - 0.4)
                ),
                mats["shell"],
                thickness=0.92,
            ),
            elliptical_ribbon_shell(
                "CONCERT_MiddleEnvelopeLoop",
                43.65,
                29.50,
                lambda theta: (
                    14.8
                    + 1.6 * rear_weight(theta)
                    + 0.55 * math.sin(theta + 0.3)
                ),
                lambda theta: (
                    15.8
                    + 5.2 * left_front_peak(theta)
                    + 3.1 * rear_weight(theta)
                    + 1.2 * math.cos(theta + 0.5)
                ),
                mats["shell"],
                thickness=0.86,
            ),
            elliptical_ribbon_shell(
                "CONCERT_UpperEnvelopeLoop",
                42.55,
                28.65,
                lambda theta: (
                    25.0
                    + 1.1 * front_weight(theta)
                    + 1.2 * math.sin(theta - 0.35)
                ),
                lambda theta: (
                    29.0
                    + 5.2 * left_front_peak(theta)
                    + 6.2 * rear_weight(theta)
                    + 1.4 * math.cos(theta - 0.8)
                ),
                mats["shell"],
                thickness=0.82,
            ),
        ]
    )

    # Lobby-framing shell wings physically wrap around the opening.
    objects.append(
        vertical_shell_panel(
            "CONCERT_LeftLobbyShell",
            -45.0,
            -27.0,
            lambda u: -25.4 - 3.6 * math.sin(math.pi * u * 0.5),
            lambda u: 13.0 + 15.0 * u ** 0.72,
            mats["shell"],
            thickness=0.72,
        )
    )
    objects.append(
        vertical_shell_panel(
            "CONCERT_RightLobbyShell",
            27.0,
            45.0,
            lambda u: -29.0 + 3.6 * math.sin(math.pi * u * 0.5),
            lambda u: 28.0 - 14.0 * u ** 0.8,
            mats["shell"],
            thickness=0.72,
        )
    )

    # First snow-dune shell: a broad entrance canopy that rises over the
    # central lobby and then sweeps down toward the long sides.
    objects.append(
        surface_volume(
            "CONCERT_LowerFlowingShell",
            lambda u, v: (
                (u - 0.5) * (
                    91.0 - 16.0 * v + 5.0 * math.sin(math.pi * v)
                ),
                -29.0 + 47.0 * v,
                15.4
                + 7.4 * math.sin(math.pi * u) ** 1.35
                + 6.8 * math.exp(-((u - 0.29) / 0.17) ** 2)
                + 5.5 * v
                + 1.6 * math.sin(math.pi * v),
            ),
            mats["shell"],
            u_steps=44,
            v_steps=22,
            thickness=0.72,
            uv_scale=(4.0, 2.6),
            bottom_mat=mats["soffit"],
        )
    )
    objects.append(
        vertical_ribbon_panel(
            "CONCERT_LowerFlowingShellFascia",
            -45.5,
            45.5,
            lambda u: -29.22 + 0.55 * math.sin(math.pi * u),
            lambda u: (
                10.8
                + 6.2 * math.sin(math.pi * u) ** 1.35
                + 5.4 * math.exp(-((u - 0.29) / 0.17) ** 2)
            ),
            lambda u: (
                15.4
                + 7.4 * math.sin(math.pi * u) ** 1.35
                + 6.8 * math.exp(-((u - 0.29) / 0.17) ** 2)
            ),
            mats["shell"],
            thickness=0.86,
            u_steps=48,
            v_steps=5,
        )
    )
    # The entrance threshold is carved between two low shell skirts. These
    # bands turn the ground floor into the reference's continuous white ribbon
    # while preserving a genuinely open central lobby.
    for side in (-1, 1):
        x0, x1 = (-45.0, -15.5) if side < 0 else (15.5, 45.0)
        objects.append(
            vertical_ribbon_panel(
                f"CONCERT_EntryShellSkirt_{side}",
                x0,
                x1,
                lambda u: -30.05 + 1.15 * math.sin(math.pi * u),
                lambda u: 3.5 + 1.8 * math.sin(math.pi * u),
                lambda u: 7.0 + 3.0 * math.sin(math.pi * u),
                mats["shell"],
                thickness=0.72,
                u_steps=20,
                v_steps=3,
            )
        )

    # The upper acoustic volume is genuinely non-prismatic: the rear-right
    # saddle grows into the goalpost's highest peak while the front-left edge
    # stays low enough to preserve the glazed lobby.
    objects.append(
        surface_volume(
            "CONCERT_UpperAcousticShell",
            lambda u, v: (
                8.0
                + 3.0 * (2.0 * v - 1.0)
                + (2.0 * u - 1.0)
                * (
                    18.0
                    + 26.0 * max(0.0, math.sin(math.pi * v)) ** 0.72
                ),
                -5.0 + 46.0 * v,
                27.0
                + 2.7 * v
                + 3.2 * math.sin(math.pi * v)
                + folded_sail_peak(
                    u, v, 0.53, 0.20, 0.21, 0.62, 0.34, 20.0
                )
                - 2.4 * abs(2.0 * u - 1.0) ** 1.7,
            ),
            mats["shell"],
            u_steps=48,
            v_steps=24,
            thickness=0.68,
            uv_scale=(4.2, 2.2),
            bottom_mat=mats["soffit"],
        )
    )
    objects.append(
        vertical_ribbon_panel(
            "CONCERT_UpperAcousticShellFascia",
            -28.0,
            44.0,
            lambda u: -5.18 + 0.30 * math.sin(math.pi * u),
            lambda u: 24.2 + 1.8 * math.sin(math.pi * u),
            lambda u: (
                27.0
                + 1.8 * math.sin(math.pi * u)
                + 2.2 * math.exp(-((u - 0.68) / 0.19) ** 2)
            ),
            mats["shell"],
            thickness=0.80,
            u_steps=42,
            v_steps=4,
        )
    )
    # A narrower overlapping rear sail supplies the third peak and the deep
    # shadow seam seen in the catalogue goalpost.
    objects.append(
        surface_volume(
            "CONCERT_RearSailShell",
            lambda u, v: (
                -8.0
                + 2.0 * (2.0 * v - 1.0)
                + (2.0 * u - 1.0)
                * (
                    12.0
                    + 18.0 * max(0.0, math.sin(math.pi * v)) ** 0.72
                ),
                6.0 + v * 32.0,
                31.0
                + 3.0 * v
                + 4.0 * math.sin(math.pi * v)
                + folded_sail_peak(
                    u, v, 0.14, 0.20, 0.20, 0.66, 0.32, 8.0
                )
                - 1.8 * abs(2.0 * u - 1.0) ** 1.6,
            ),
            mats["shell"],
            u_steps=40,
            v_steps=20,
            thickness=0.62,
            uv_scale=(3.4, 1.7),
            bottom_mat=mats["soffit"],
        )
    )

    # A quiet rear service elevation remains fully authored.
    objects.append(
        box(
            "CONCERT_RearServiceGlass",
            (58.0, 0.16, 11.0),
            (0, 31.0, 8.0),
            mats["glass"],
        )
    )
    for x in range(-28, 29, 4):
        objects.append(
            box(
                f"CONCERT_RearMullion_{x}",
                (0.10, 0.28, 11.2),
                (x, 31.1, 8.0),
                mats["bronze"],
            )
        )
    return objects


def concert_module(
    role: str,
    variant: str,
    height: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    if role == "podium":
        objects.append(
            tapered_ellipse(
                "CONCERTKIT_PodiumShell",
                [(0, 41.0, 28.0), (height, 44.0, 30.5)],
                mats["shell"],
                mats["dark"],
                segments=96,
            )
        )
        objects.append(
            box(
                "CONCERTKIT_PodiumLobby",
                (40.0, 0.18, height * 0.82),
                (0, -30.6, height * 0.47),
                mats["glass"],
            )
        )
    elif role == "floor":
        offset = {"typical_a": 0.0, "typical_b": 1.2, "typical_c": -1.0}[variant]
        objects.append(
            tapered_ellipse(
                f"CONCERTKIT_FloorShell_{variant}",
                [(0, 43.0 + offset, 29.5), (height, 42.0 - offset * 0.3, 29.0)],
                mats["shell"],
                mats["dark"],
                segments=96,
            )
        )
        objects.append(
            box(
                f"CONCERTKIT_FloorGlass_{variant}",
                (50.0, 0.14, height * 0.54),
                (0, -29.7, height * 0.52),
                mats["glass"],
            )
        )
    elif role == "crown":
        objects.append(
            surface_volume(
                "CONCERTKIT_CrownShell",
                lambda u, v: (
                    (u - 0.5) * (86.0 - 8.0 * v),
                    -28.0 + 56.0 * v,
                    0.5
                    + (height - 0.5)
                    * (
                        0.35
                        + 0.35 * math.sin(math.pi * u)
                        + 0.30 * v
                    ),
                ),
                mats["shell"],
                u_steps=24,
                v_steps=12,
                thickness=0.35,
            )
        )
    elif role == "roof":
        objects.append(
            surface_volume(
                "CONCERTKIT_RoofShell",
                lambda u, v: (
                    (u - 0.5) * (88.0 - 7.0 * v),
                    -29.0 + 58.0 * v,
                    0.5
                    + (height - 0.5)
                    * (
                        0.20
                        + 0.38 * math.sin(math.pi * u)
                        + 0.42 * v
                    ),
                ),
                mats["shell"],
                u_steps=26,
                v_steps=14,
                thickness=0.42,
            )
        )
    return objects


def mercat_fixed(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    objects.append(
        box(
            "MERCAT_StonePlinth",
            (64.0, 44.0, 0.75),
            (0, 0, 0.375),
            mats["tile"],
            0.08,
        )
    )

    def iron_column(
        name: str,
        location: tuple[float, float, float],
        height: float = 10.5,
    ) -> list[bpy.types.Object]:
        x, y, z = location
        parts = [
            cylinder(
                name + "_Shaft",
                0.23,
                height - 1.0,
                (x, y, z + height / 2),
                mats["iron"],
                24,
            ),
            cylinder(
                name + "_Base",
                0.52,
                0.42,
                (x, y, z + 0.21),
                mats["iron"],
                24,
            ),
            cylinder(
                name + "_BaseNeck",
                0.34,
                0.42,
                (x, y, z + 0.55),
                mats["iron"],
                24,
            ),
            cylinder(
                name + "_Capital",
                0.62,
                0.34,
                (x, y, z + height - 0.26),
                mats["iron"],
                24,
            ),
            box(
                name + "_Abacus",
                (1.15, 1.15, 0.20),
                (x, y, z + height - 0.05),
                mats["iron"],
                0.06,
            ),
        ]
        return parts

    # Tile plinth and a genuinely open cast-iron perimeter arcade.
    side_bays = 10
    y_values = [-20.0 + 40.0 * index / side_bays for index in range(side_bays + 1)]
    for side in (-1, 1):
        x = side * 31.2
        for index, y in enumerate(y_values):
            objects.extend(iron_column(f"MERCAT_SideColumn_{side}_{index}", (x, y, 0.8)))
            # The iron order grows out of the tiled masonry base; these
            # buttresses visually lock the arcade to the building instead of
            # leaving a row of freestanding posts.
            objects.append(
                box(
                    f"MERCAT_SideStonePost_{side}_{index}",
                    (1.35, 1.05, 2.15),
                    (side * 31.48, y, 1.35),
                    mats["cream"],
                    0.08,
                )
            )
        for index in range(side_bays):
            y = (y_values[index] + y_values[index + 1]) / 2
            span = y_values[index + 1] - y_values[index]
            objects.append(
                box(
                    f"MERCAT_SideTilePlinth_{side}_{index}",
                    (0.72, span - 0.18, 1.45),
                    (side * 31.55, y, 1.48),
                    mats["tile"],
                    0.05,
                )
            )
            objects.append(
                box(
                    f"MERCAT_SidePlinthCap_{side}_{index}",
                    (0.92, span - 0.10, 0.24),
                    (side * 31.53, y, 2.28),
                    mats["cream"],
                    0.035,
                )
            )
            objects.extend(
                arch_frame(
                    f"MERCAT_SideArcade_{side}_{index}",
                    x,
                    y,
                    2.0,
                    span - 0.25,
                    8.0,
                    0.28,
                    mats["iron"],
                    front_axis="x",
                )
            )
            objects.append(
                box(
                    f"MERCAT_SideGlass_{side}_{index}",
                    (0.12, span - 0.55, 5.5),
                    (side * 31.28, y, 6.4),
                    mats["roof_glass"],
                )
            )
            objects.append(
                box(
                    f"MERCAT_SideOccupiedBacking_{side}_{index}",
                    (0.08, span - 0.72, 5.15),
                    (side * 30.92, y, 6.35),
                    mats["market_interior"],
                )
            )
            for transom_index, z in enumerate((4.25, 6.30, 8.30)):
                objects.append(
                    box(
                        f"MERCAT_SideTransom_{side}_{index}_{transom_index}",
                        (0.18, span - 0.48, 0.10),
                        (side * 31.38, y, z),
                        mats["iron"],
                    )
                )
            objects.append(
                box(
                    f"MERCAT_SideMullion_{side}_{index}",
                    (0.18, 0.10, 5.60),
                    (side * 31.38, y, 6.35),
                    mats["iron"],
                )
            )
            for brace_side in (-1, 1):
                objects.append(
                    beam(
                        f"MERCAT_SideSpandrelBrace_{side}_{index}_{brace_side}",
                        (
                            side * 31.38,
                            y + brace_side * (span / 2 - 0.30),
                            10.55,
                        ),
                        (
                            side * 31.38,
                            y + brace_side * span * 0.16,
                            8.75,
                        ),
                        0.105,
                        mats["iron"],
                    )
                )

    # Front arcade bays flank the central portal.  Its rhythm continues around
    # the corners instead of ending at a facade applique.
    front_x = (-29.0, -24.5, -20.0, -15.5, 15.5, 20.0, 24.5, 29.0)
    for index, x in enumerate(front_x):
        objects.extend(iron_column(f"MERCAT_FrontColumn_{index}", (x, -21.4, 0.8)))
    for side, centres in (
        (-1, (-26.75, -22.25, -17.75)),
        (1, (17.75, 22.25, 26.75)),
    ):
        for index, x in enumerate(centres):
            objects.append(
                box(
                    f"MERCAT_FrontTilePlinth_{side}_{index}",
                    (4.25, 0.72, 1.45),
                    (x, -21.75, 1.48),
                    mats["tile"],
                    0.05,
                )
            )
            objects.extend(
                arch_frame(
                    f"MERCAT_FrontArcade_{side}_{index}",
                    x,
                    -21.4,
                    2.0,
                    4.25,
                    8.0,
                    0.28,
                    mats["iron"],
                )
            )
            objects.append(
                box(
                    f"MERCAT_FrontGlass_{side}_{index}",
                    (4.0, 0.12, 5.6),
                    (x, -21.75, 6.35),
                    mats["roof_glass"],
                )
            )
            objects.append(
                box(
                    f"MERCAT_FrontOccupiedBacking_{side}_{index}",
                    (3.70, 0.10, 5.20),
                    (x, -21.18, 6.35),
                    mats["market_interior"],
                )
            )
            objects.append(
                box(
                    f"MERCAT_FrontMullion_{side}_{index}",
                    (0.10, 0.18, 5.50),
                    (x, -21.84, 6.35),
                    mats["iron"],
                )
            )
            for transom_index, z in enumerate((4.35, 6.35, 8.25)):
                objects.append(
                    box(
                        f"MERCAT_FrontTransom_{side}_{index}_{transom_index}",
                        (3.85, 0.18, 0.10),
                        (x, -21.84, z),
                        mats["iron"],
                    )
                )
            for brace_side in (-1, 1):
                objects.append(
                    beam(
                        f"MERCAT_FrontSpandrelBrace_{side}_{index}_{brace_side}",
                        (
                            x + brace_side * 1.90,
                            -21.84,
                            10.45,
                        ),
                        (
                            x + brace_side * 0.62,
                            -21.84,
                            8.65,
                        ),
                        0.10,
                        mats["iron"],
                    )
                )

    # Five longitudinal market aisles preserve the established roof rhythm.
    # Their slopes are weathered zinc and terracotta, with glazing restricted
    # to raised ridge lanterns; making every slope transparent produced a
    # generic greenhouse and exposed an implausible forest of internal trusses.
    aisle_centres = (-26.0, -13.0, 0.0, 13.0, 26.0)
    aisle_widths = (11.0, 12.0, 14.0, 12.0, 11.0)
    ridge_heights = (14.4, 15.8, 19.6, 15.8, 14.4)
    eave_heights = (10.6, 10.9, 11.3, 10.9, 10.6)
    roof_front, roof_rear = -19.8, 21.0
    for aisle, (cx, width, ridge_z, eave_z) in enumerate(
        zip(aisle_centres, aisle_widths, ridge_heights, eave_heights)
    ):
        half = width / 2
        lantern_ratio = 0.18
        left_lantern_x = cx - half * lantern_ratio
        right_lantern_x = cx + half * lantern_ratio
        lantern_eave_z = ridge_z - (ridge_z - eave_z) * lantern_ratio
        objects.append(
            quad_panel(
                f"MERCAT_RoofZincLeft_{aisle}",
                (
                    (cx - half, roof_front, eave_z),
                    (left_lantern_x, roof_front, lantern_eave_z),
                    (left_lantern_x, roof_rear, lantern_eave_z),
                    (cx - half, roof_rear, eave_z),
                ),
                mats["roof_metal"],
            )
        )
        objects.append(
            quad_panel(
                f"MERCAT_RoofZincRight_{aisle}",
                (
                    (right_lantern_x, roof_front, lantern_eave_z),
                    (cx + half, roof_front, eave_z),
                    (cx + half, roof_rear, eave_z),
                    (right_lantern_x, roof_rear, lantern_eave_z),
                ),
                mats["roof_metal"],
            )
        )
        objects.append(
            quad_panel(
                f"MERCAT_RoofLanternGlassLeft_{aisle}",
                (
                    (left_lantern_x, roof_front, lantern_eave_z),
                    (cx, roof_front, ridge_z),
                    (cx, roof_rear, ridge_z),
                    (left_lantern_x, roof_rear, lantern_eave_z),
                ),
                mats["roof_glass"],
            )
        )
        objects.append(
            quad_panel(
                f"MERCAT_RoofLanternGlassRight_{aisle}",
                (
                    (cx, roof_front, ridge_z),
                    (right_lantern_x, roof_front, lantern_eave_z),
                    (right_lantern_x, roof_rear, lantern_eave_z),
                    (cx, roof_rear, ridge_z),
                ),
                mats["roof_glass"],
            )
        )
        # Terracotta weathering aprons cover the lower roof slopes while the
        # upper panes remain glazed.  This is the warm, layered roof hierarchy
        # visible in every reference angle, and prevents a generic all-glass
        # greenhouse reading.
        seam_ratio = 0.20
        left_seam_x = cx - half * (1.0 - seam_ratio)
        right_seam_x = cx + half * (1.0 - seam_ratio)
        seam_z = eave_z + (ridge_z - eave_z) * seam_ratio
        objects.append(
            quad_panel(
                f"MERCAT_TerracottaApronLeft_{aisle}",
                (
                    (cx - half, roof_front - 0.02, eave_z + 0.03),
                    (left_seam_x, roof_front - 0.02, seam_z + 0.03),
                    (left_seam_x, roof_rear + 0.02, seam_z + 0.03),
                    (cx - half, roof_rear + 0.02, eave_z + 0.03),
                ),
                mats["terracotta"],
            )
        )
        objects.append(
            quad_panel(
                f"MERCAT_TerracottaApronRight_{aisle}",
                (
                    (right_seam_x, roof_front - 0.02, seam_z + 0.03),
                    (cx + half, roof_front - 0.02, eave_z + 0.03),
                    (cx + half, roof_rear + 0.02, eave_z + 0.03),
                    (right_seam_x, roof_rear + 0.02, seam_z + 0.03),
                ),
                mats["terracotta"],
            )
        )
        objects.extend(
            [
                beam(
                    f"MERCAT_Ridge_{aisle}",
                    (cx, roof_front, ridge_z),
                    (cx, roof_rear, ridge_z),
                    0.16,
                    mats["iron"],
                ),
                beam(
                    f"MERCAT_EaveLeft_{aisle}",
                    (cx - half, roof_front, eave_z),
                    (cx - half, roof_rear, eave_z),
                    0.16,
                    mats["iron"],
                ),
                beam(
                    f"MERCAT_EaveRight_{aisle}",
                    (cx + half, roof_front, eave_z),
                    (cx + half, roof_rear, eave_z),
                    0.16,
                    mats["iron"],
                ),
                beam(
                    f"MERCAT_RoofApronSeamLeft_{aisle}",
                    (left_seam_x, roof_front, seam_z),
                    (left_seam_x, roof_rear, seam_z),
                    0.12,
                    mats["iron"],
                ),
                beam(
                    f"MERCAT_RoofApronSeamRight_{aisle}",
                    (right_seam_x, roof_front, seam_z),
                    (right_seam_x, roof_rear, seam_z),
                    0.12,
                    mats["iron"],
                ),
            ]
        )
        for truss, y in enumerate(range(-19, 22, 4)):
            objects.extend(
                [
                    beam(
                        f"MERCAT_TrussLeft_{aisle}_{truss}",
                        (cx - half, y, eave_z),
                        (cx, y, ridge_z),
                        0.12,
                        mats["iron"],
                    ),
                    beam(
                        f"MERCAT_TrussRight_{aisle}_{truss}",
                        (cx, y, ridge_z),
                        (cx + half, y, eave_z),
                        0.12,
                        mats["iron"],
                    ),
                    beam(
                        f"MERCAT_TrussTie_{aisle}_{truss}",
                        (cx - half, y, eave_z + 0.25),
                        (cx + half, y, eave_z + 0.25),
                        0.10,
                        mats["iron"],
                    ),
                ]
            )
        # The glazed ridge lantern remains legible as a separate construction
        # system in all views, with closely spaced transoms rather than a
        # texture-only strip.
        for side, lantern_x in ((-1, left_lantern_x), (1, right_lantern_x)):
            objects.append(
                box(
                    f"MERCAT_ClerestorySide_{aisle}_{side}",
                    (0.12, roof_rear - roof_front, 1.35),
                    (lantern_x, 0.6, lantern_eave_z + 0.68),
                    mats["roof_glass"],
                )
            )
            for y in range(-18, 21, 3):
                objects.append(
                    box(
                        f"MERCAT_ClerestoryMullion_{aisle}_{side}_{y}",
                        (0.22, 0.10, 1.48),
                        (lantern_x, y, lantern_eave_z + 0.68),
                        mats["iron"],
                    )
                )
        # Fine ridge cresting is continuous in oblique/aerial views.
        for finial_index, y in enumerate(range(-18, 21, 4)):
            objects.extend(
                [
                    beam(
                        f"MERCAT_RidgeCrestStem_{aisle}_{finial_index}",
                        (cx, y, ridge_z + 0.05),
                        (cx, y, ridge_z + 0.78),
                        0.055,
                        mats["iron"],
                    ),
                    sphere(
                        f"MERCAT_RidgeCrestBud_{aisle}_{finial_index}",
                        0.13,
                        (cx, y, ridge_z + 0.86),
                        mats["iron"],
                        (0.72, 0.72, 1.25),
                        12,
                        6,
                    ),
                ]
            )

    # The long elevations carry a receding row of side-facing sawtooth
    # monitors in the primary oblique reference.  Build those as integrated
    # glazed gables with iron outlines and louver rails, seated into the roof
    # field rather than perched above it as generic dormer props.
    for side in (-1, 1):
        monitor_x = side * 25.3
        outward_x = side * 25.42
        for monitor_index, y in enumerate((-14.0, -6.0, 2.0, 10.0, 18.0)):
            monitor = triangular_prism(
                f"MERCAT_SawtoothMonitor_{side}_{monitor_index}",
                7.5,
                3.2,
                0.18,
                (monitor_x, y, 13.20),
                mats["roof_metal"],
            )
            monitor.rotation_euler[2] = math.pi / 2
            objects.append(monitor)
            objects.extend(
                [
                    box(
                        f"MERCAT_SawtoothKerb_{side}_{monitor_index}",
                        (1.15, 7.8, 0.38),
                        (monitor_x, y, 13.32),
                        mats["roof_metal"],
                        0.04,
                    ),
                    beam(
                        f"MERCAT_SawtoothSlopeA_{side}_{monitor_index}",
                        (outward_x, y - 3.75, 13.40),
                        (outward_x, y, 16.35),
                        0.14,
                        mats["iron"],
                    ),
                    beam(
                        f"MERCAT_SawtoothSlopeB_{side}_{monitor_index}",
                        (outward_x, y, 16.35),
                        (outward_x, y + 3.75, 13.40),
                        0.14,
                        mats["iron"],
                    ),
                    beam(
                        f"MERCAT_SawtoothTie_{side}_{monitor_index}",
                        (outward_x, y - 3.75, 13.40),
                        (outward_x, y + 3.75, 13.40),
                        0.14,
                        mats["iron"],
                    ),
                ]
            )
            for louver_index, (z, span) in enumerate(
                (
                    (14.00, 6.0),
                    (14.65, 4.8),
                    (15.30, 3.4),
                    (15.90, 1.8),
                )
            ):
                objects.append(
                    box(
                        f"MERCAT_SawtoothLouver_{side}_{monitor_index}_{louver_index}",
                        (0.12, span, 0.10),
                        (outward_x, y, z),
                        mats["iron"],
                    )
                )

    # Integral Modernista portal: an arched stained-glass field, two iron
    # rings, radial fanlight structure, tiled piers and recessed doors.
    portal_y = -22.05
    portal_width, portal_height, portal_sill = 28.0, 17.2, 1.1
    portal_radius = portal_width / 2
    portal_spring = portal_sill + portal_height - portal_radius
    objects.append(
        arched_panel(
            "MERCAT_ModernistaClearPortal",
            0.0,
            portal_y + 0.03,
            portal_sill,
            portal_width,
            portal_height,
            mats["roof_glass"],
            segments=48,
        )
    )

    def semicircle_fanlight(
        name: str,
        centre_x: float,
        y: float,
        spring_z: float,
        radius: float,
        mat: bpy.types.Material,
        segments: int = 48,
    ) -> bpy.types.Object:
        vertices = [(centre_x, y, spring_z)]
        vertices.extend(
            (
                centre_x + radius * math.cos(math.pi * index / segments),
                y,
                spring_z + radius * math.sin(math.pi * index / segments),
            )
            for index in range(segments + 1)
        )
        faces = [
            (0, index + 1, index + 2)
            for index in range(segments)
        ]
        uv = [
            (0.5, 0.0),
            *[
                (
                    0.5 + 0.5 * math.cos(math.pi * index / segments),
                    math.sin(math.pi * index / segments),
                )
                for index in range(segments + 1)
            ],
        ]
        return mesh_object(name, vertices, faces, mat, uv)

    objects.append(
        semicircle_fanlight(
            "MERCAT_ModernistaStainedFanlight",
            0.0,
            portal_y - 0.04,
            portal_spring,
            portal_radius,
            mats["stained"],
        )
    )
    # The real entrance reads as fine polychrome leadwork rather than a clear
    # greenhouse end.  Keep the generated mosaic as the broad field and use
    # restrained physical coloured lights only for its rose and perimeter
    # medallions; oversized flat discs would turn the heritage glass into a
    # cartoon.
    stained_palette = (
        mats["stained_red"],
        mats["stained_blue"],
        mats["stained_gold"],
        mats["stained_green"],
    )
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=48,
        radius=0.92,
        depth=0.16,
        location=(0.0, portal_y - 0.56, portal_spring + 2.55),
        rotation=(math.pi / 2, 0, 0),
    )
    central_rose = bpy.context.object
    central_rose.name = "MERCAT_CentralPolychromeRose"
    central_rose.data.materials.append(mats["stained"])
    objects.append(central_rose)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=1.08,
        minor_radius=0.10,
        major_segments=48,
        minor_segments=10,
        location=(0.0, portal_y - 0.67, portal_spring + 2.55),
        rotation=(math.pi / 2, 0, 0),
    )
    central_rose_ring = bpy.context.object
    central_rose_ring.name = "MERCAT_CentralPolychromeRoseRing"
    central_rose_ring.data.materials.append(mats["bronze"])
    objects.append(central_rose_ring)
    for petal in range(10):
        angle = math.tau * petal / 10
        x = 1.48 * math.cos(angle)
        z = portal_spring + 2.55 + 1.48 * math.sin(angle)
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=24,
            radius=0.34,
            depth=0.14,
            location=(x, portal_y - 0.57, z),
            rotation=(math.pi / 2, 0, 0),
        )
        rose_petal = bpy.context.object
        rose_petal.name = f"MERCAT_CentralRosePetal_{petal}"
        rose_petal.data.materials.append(stained_palette[(petal + 1) % 4])
        objects.append(rose_petal)
    objects.extend(
        arch_frame(
            "MERCAT_ModernistaOuterArch",
            0.0,
            portal_y - 0.18,
            portal_sill,
            portal_width + 1.3,
            portal_height + 0.65,
            0.32,
            mats["iron"],
        )
    )
    objects.extend(
        arch_frame(
            "MERCAT_ModernistaInnerArch",
            0.0,
            portal_y - 0.28,
            portal_sill,
            portal_width - 1.2,
            portal_height - 0.55,
            0.25,
            mats["iron"],
        )
    )
    objects.extend(
        arch_frame(
            "MERCAT_ModernistaFiligreeArch",
            0.0,
            portal_y - 0.42,
            portal_sill - 0.18,
            portal_width + 2.35,
            portal_height + 1.20,
            0.14,
            mats["bronze"],
        )
    )
    # The ornament is constructed as a real radial iron-and-glass spandrel,
    # not painted onto the portal.  From oblique views the medallions, rings,
    # and lace sit at distinct depths.
    ornament_radius = portal_radius + 1.15
    medallion_angles = [
        math.radians(12.0 + index * 13.0)
        for index in range(13)
    ]
    for index, angle in enumerate(medallion_angles):
        x = ornament_radius * math.cos(angle)
        z = portal_spring + ornament_radius * math.sin(angle)
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=32,
            radius=0.38,
            depth=0.13,
            location=(x, portal_y - 0.62, z),
            rotation=(math.pi / 2, 0, 0),
        )
        medallion = bpy.context.object
        medallion.name = f"MERCAT_StainedMedallion_{index}"
        medallion.data.materials.append(stained_palette[index % 4])
        objects.append(medallion)
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.48,
            minor_radius=0.065,
            major_segments=28,
            minor_segments=8,
            location=(x, portal_y - 0.72, z),
            rotation=(math.pi / 2, 0, 0),
        )
        ring = bpy.context.object
        ring.name = f"MERCAT_MedallionIronRing_{index}"
        ring.data.materials.append(mats["iron"])
        objects.append(ring)
        inner = portal_radius + 0.12
        objects.append(
            beam(
                f"MERCAT_SpandrelRadial_{index}",
                (
                    inner * math.cos(angle),
                    portal_y - 0.54,
                    portal_spring + inner * math.sin(angle),
                ),
                (
                    (ornament_radius - 0.80) * math.cos(angle),
                    portal_y - 0.54,
                    portal_spring + (ornament_radius - 0.80) * math.sin(angle),
                ),
                0.075,
                mats["iron"],
            )
        )
        if index:
            previous_angle = medallion_angles[index - 1]
            objects.append(
                beam(
                    f"MERCAT_SpandrelLace_{index}",
                    (
                        ornament_radius * math.cos(previous_angle),
                        portal_y - 0.52,
                        portal_spring + ornament_radius * math.sin(previous_angle),
                    ),
                    (
                        ornament_radius * math.cos(angle),
                        portal_y - 0.52,
                        portal_spring + ornament_radius * math.sin(angle),
                    ),
                    0.065,
                    mats["bronze"],
                )
            )
    for index in range(13):
        angle = math.pi * index / 12
        end = (
            portal_radius * math.cos(angle),
            portal_y - 0.36,
            portal_spring + portal_radius * math.sin(angle),
        )
        objects.append(
            beam(
                f"MERCAT_FanlightSpoke_{index}",
                (0.0, portal_y - 0.36, portal_spring),
                end,
                0.075,
                mats["iron"],
            )
        )
    for x in (-16.3, 16.3):
        objects.append(
            box(
                f"MERCAT_PortalStonePier_{x}",
                (3.6, 2.1, 8.6),
                (x, -21.4, 4.8),
                mats["cream"],
                0.18,
            )
        )
        objects.append(
            box(
                f"MERCAT_PortalTileInset_{x}",
                (2.35, 0.14, 4.6),
                (x, -22.50, 4.2),
                mats["tile"],
                0.05,
            )
        )
        for edge_x in (-1.25, 1.25):
            objects.append(
                box(
                    f"MERCAT_PortalInsetJamb_{x}_{edge_x}",
                    (0.16, 0.28, 5.10),
                    (x + edge_x, -22.60, 4.20),
                    mats["bronze"],
                    0.025,
                )
            )
        for edge_z in (1.63, 6.77):
            objects.append(
                box(
                    f"MERCAT_PortalInsetRail_{x}_{edge_z}",
                    (2.65, 0.28, 0.16),
                    (x, -22.60, edge_z),
                    mats["bronze"],
                    0.025,
                )
            )
        for course, z in enumerate((1.25, 3.0, 5.0, 7.0, 8.9)):
            objects.append(
                box(
                    f"MERCAT_PortalPierCourse_{x}_{course}",
                    (3.95 if course in {0, 4} else 3.72, 2.28, 0.24),
                    (x, -21.4, z),
                    mats["cream"],
                    0.04,
                )
            )
        objects.extend(iron_column(f"MERCAT_PortalColumn_{x}", (x, -22.1, 0.8), 13.8))

    for door in range(5):
        x = (door - 2) * 3.6
        objects.append(
            box(
                f"MERCAT_EntranceDoor_{door}",
                (3.2, 0.14, 5.0),
                (x, -22.42, 3.6),
                mats["roof_glass"],
            )
        )
        for edge in (-1.6, 1.6):
            objects.append(
                box(
                    f"MERCAT_EntranceJamb_{door}_{edge}",
                    (0.09, 0.26, 5.2),
                    (x + edge, -22.50, 3.6),
                    mats["iron"],
                )
            )

    # Gable frame and custom iron crest/scrolls.  The reference entrance is a
    # pitched iron pediment wrapped around the arch, not a freestanding round
    # fanlight.  A heavy triangular perimeter plus real medallions and lace
    # ties the portal into the three-nave roof section.
    objects.extend(
        [
            beam(
                "MERCAT_GableLeft",
                (-18.0, -21.9, 11.0),
                (0.0, -21.9, 22.0),
                0.48,
                mats["iron"],
            ),
            beam(
                "MERCAT_GableRight",
                (0.0, -21.9, 22.0),
                (18.0, -21.9, 11.0),
                0.48,
                mats["iron"],
            ),
            beam(
                "MERCAT_GableTie",
                (-18.0, -21.9, 11.0),
                (18.0, -21.9, 11.0),
                0.38,
                mats["iron"],
            ),
        ]
    )
    for side in (-1, 1):
        for division in range(1, 7):
            fraction = division / 7.0
            x = side * 18.0 * (1.0 - fraction)
            z = 11.0 + 11.0 * fraction
            objects.append(
                beam(
                    f"MERCAT_GableLace_{side}_{division}",
                    (x, -22.00, 11.15),
                    (x, -22.00, z - 0.28),
                    0.075,
                    mats["bronze"],
                )
            )
            bpy.ops.mesh.primitive_cylinder_add(
                vertices=32,
                radius=0.42,
                depth=0.14,
                location=(x, -22.13, z),
                rotation=(math.pi / 2, 0, 0),
            )
            gable_medallion = bpy.context.object
            gable_medallion.name = f"MERCAT_GableMedallion_{side}_{division}"
            gable_medallion.data.materials.append(
                stained_palette[(division + (0 if side < 0 else 2)) % 4]
            )
            objects.append(gable_medallion)
            bpy.ops.mesh.primitive_torus_add(
                major_radius=0.51,
                minor_radius=0.065,
                major_segments=28,
                minor_segments=8,
                location=(x, -22.22, z),
                rotation=(math.pi / 2, 0, 0),
            )
            gable_ring = bpy.context.object
            gable_ring.name = f"MERCAT_GableMedallionRing_{side}_{division}"
            gable_ring.data.materials.append(mats["iron"])
            objects.append(gable_ring)

    def tube_curve(
        name: str,
        points: list[tuple[float, float, float]],
        radius: float,
        mat: bpy.types.Material,
    ) -> bpy.types.Object:
        curve = bpy.data.curves.new(name + "Curve", "CURVE")
        curve.dimensions = "3D"
        curve.resolution_u = 2
        curve.bevel_depth = radius
        curve.bevel_resolution = 2
        spline = curve.splines.new("NURBS")
        spline.points.add(len(points) - 1)
        for point, value in zip(spline.points, points):
            point.co = (*value, 1.0)
        spline.order_u = min(4, len(points))
        spline.use_endpoint_u = True
        obj = bpy.data.objects.new(name, curve)
        bpy.context.collection.objects.link(obj)
        obj.data.materials.append(mat)
        select_only([obj])
        bpy.ops.object.convert(target="MESH")
        return bpy.context.object

    crest_y = -22.22
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=1.05,
        depth=0.24,
        location=(0.0, crest_y - 0.14, 22.35),
        rotation=(math.pi / 2, 0, 0),
    )
    crest_shield = bpy.context.object
    crest_shield.name = "MERCAT_CentralCrestShield"
    crest_shield.scale = (0.78, 1.0, 1.10)
    crest_shield.data.materials.append(mats["stained"])
    objects.append(crest_shield)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=1.16,
        minor_radius=0.12,
        major_segments=36,
        minor_segments=8,
        location=(0.0, crest_y - 0.28, 22.35),
        rotation=(math.pi / 2, 0, 0),
    )
    crest_ring = bpy.context.object
    crest_ring.name = "MERCAT_CentralCrestRing"
    crest_ring.scale = (0.78, 1.0, 1.10)
    crest_ring.data.materials.append(mats["bronze"])
    objects.append(crest_ring)
    objects.append(
        beam(
            "MERCAT_CentralCrestStem",
            (0.0, crest_y, 20.7),
            (0.0, crest_y, 24.1),
            0.105,
            mats["iron"],
        )
    )
    for side in (-1, 1):
        objects.append(
            tube_curve(
                f"MERCAT_CentralSCurve_{side}",
                [
                    (
                        side
                        * (
                            0.3
                            + 1.35 * math.sin(math.pi * t)
                            - 0.72 * math.sin(2 * math.pi * t)
                        ),
                        crest_y,
                        21.0 + 2.8 * t,
                    )
                    for t in [index / 28 for index in range(29)]
                ],
                0.09,
                mats["iron"],
            )
        )
    for side in (-1, 1):
        for scroll in range(3):
            cx = side * (2.6 + scroll * 2.35)
            radius = 0.82 - scroll * 0.08
            objects.append(
                tube_curve(
                    f"MERCAT_CrestScroll_{side}_{scroll}",
                    [
                        (
                            cx
                            + side
                            * (0.12 + radius * t)
                            * math.cos(-math.pi * 0.55 + math.tau * 1.45 * t),
                            crest_y,
                            20.35
                            + scroll * 0.18
                            + 0.58 * t
                            + (0.12 + radius * t)
                            * math.sin(-math.pi * 0.55 + math.tau * 1.45 * t),
                        )
                        for t in [index / 38 for index in range(39)]
                    ],
                    0.10,
                    mats["iron"],
                )
            )
            objects.append(
                beam(
                    f"MERCAT_CrestScrollStem_{side}_{scroll}",
                    (cx - side * 0.25, crest_y, 19.72 + scroll * 0.12),
                    (cx, crest_y, 20.35 + scroll * 0.18),
                    0.075,
                    mats["iron"],
                )
            )
    for x in (-28, -24, -20, -16, -12, 12, 16, 20, 24, 28):
        objects.append(
            beam(
                f"MERCAT_RidgeFinial_{x}",
                (x, -20.0, 16.0 + 4.0 * max(0.0, 1.0 - abs(x) / 30.0)),
                (x, -20.0, 17.0 + 4.0 * max(0.0, 1.0 - abs(x) / 30.0)),
                0.07,
                mats["iron"],
            )
        )

    # Warm market stalls are visible through the transparent perimeter.
    for row, y in enumerate((-8.0, 3.0, 14.0)):
        for bay, x in enumerate(range(-25, 26, 10)):
            objects.append(
                box(
                    f"MERCAT_ProduceStall_{row}_{bay}",
                    (6.5, 4.5, 2.1),
                    (x, y, 2.0),
                    mats["warm"] if (row + bay) % 2 else mats["tile"],
                    0.10,
                )
            )
            objects.append(
                box(
                    f"MERCAT_StallCanopy_{row}_{bay}",
                    (7.0, 5.0, 0.18),
                    (x, y, 3.25),
                    mats["iron"],
                )
            )
    # The entrance sightline terminates on real produce displays so the
    # transparent doors reveal an occupied market, not an empty orange box.
    produce_materials = (
        mats["produce_red"],
        mats["produce_green"],
        mats["produce_gold"],
    )
    for stall_index, x in enumerate((-9.0, 0.0, 9.0)):
        objects.extend(
            [
                box(
                    f"MERCAT_FrontProduceCounter_{stall_index}",
                    (6.6, 2.8, 1.25),
                    (x, -17.2, 1.75),
                    mats["cream"],
                    0.08,
                ),
                box(
                    f"MERCAT_FrontProduceCanopy_{stall_index}",
                    (7.1, 3.2, 0.18),
                    (x, -17.2, 4.25),
                    mats["iron"],
                ),
            ]
        )
        for fruit_index in range(15):
            column = fruit_index % 5
            row = fruit_index // 5
            objects.append(
                sphere(
                    f"MERCAT_ProduceFruit_{stall_index}_{fruit_index}",
                    0.24,
                    (
                        x - 1.55 + column * 0.78,
                        -18.15 + row * 0.68,
                        2.55 + 0.07 * ((column + row) % 2),
                    ),
                    produce_materials[(stall_index + fruit_index) % 3],
                    (1.0, 1.0, 0.82),
                    12,
                    6,
                )
            )

    # Rear elevation uses a simpler iron/glass gable but the same system.
    objects.append(
        arched_panel(
            "MERCAT_RearGlazedGable",
            0.0,
            21.75,
            2.0,
            22.0,
            14.5,
            mats["roof_glass"],
            segments=36,
        )
    )
    objects.extend(
        arch_frame(
            "MERCAT_RearArch",
            0.0,
            21.9,
            2.0,
            22.0,
            14.5,
            0.25,
            mats["iron"],
        )
    )
    return objects


def mercat_module(
    role: str,
    variant: str,
    height: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    if role == "podium":
        objects.append(
            box(
                "MERCATKIT_TiledPlinth",
                (64.0, 44.0, 1.4),
                (0, 0, 0.7),
                mats["tile"],
                0.08,
            )
        )
        for x in range(-28, 29, 7):
            objects.append(
                cylinder(
                    f"MERCATKIT_PodiumColumn_{x}",
                    0.22,
                    height - 1.0,
                    (x, -21.3, height / 2 + 0.4),
                    mats["iron"],
                    20,
                )
            )
    elif role == "floor":
        spacing = {"typical_a": 6.5, "typical_b": 7.5, "typical_c": 5.5}[variant]
        objects.append(
            box(
                f"MERCATKIT_FloorGlass_{variant}",
                (61.0, 42.0, height - 0.8),
                (0, 0, height / 2),
                mats["roof_glass"],
            )
        )
        x = -29.0
        index = 0
        while x <= 29.0:
            objects.append(
                box(
                    f"MERCATKIT_FloorPier_{variant}_{index}",
                    (0.26, 42.5, height),
                    (x, 0, height / 2),
                    mats["iron"],
                )
            )
            x += spacing
            index += 1
    elif role == "crown":
        objects.append(
            arched_panel(
                "MERCATKIT_CrownStained",
                0.0,
                -21.8,
                0.1,
                12.0,
                height - 0.1,
                mats["stained"],
                segments=36,
            )
        )
        objects.extend(
            arch_frame(
                "MERCATKIT_CrownArch",
                0.0,
                -21.95,
                0.1,
                13.0,
                height - 0.05,
                0.25,
                mats["iron"],
            )
        )
    elif role == "roof":
        centres = (-26.0, -13.0, 0.0, 13.0, 26.0)
        widths = (11.0, 12.0, 14.0, 12.0, 11.0)
        for index, (cx, width) in enumerate(zip(centres, widths)):
            half = width / 2
            ridge = height
            eave = 0.5
            objects.append(
                quad_panel(
                    f"MERCATKIT_RoofLeft_{index}",
                    (
                        (cx - half, -21.5, eave),
                        (cx, -21.5, ridge),
                        (cx, 21.5, ridge),
                        (cx - half, 21.5, eave),
                    ),
                    mats["roof_glass"],
                )
            )
            objects.append(
                quad_panel(
                    f"MERCATKIT_RoofRight_{index}",
                    (
                        (cx, -21.5, ridge),
                        (cx + half, -21.5, eave),
                        (cx + half, 21.5, eave),
                        (cx, 21.5, ridge),
                    ),
                    mats["roof_glass"],
                )
            )
            objects.append(
                beam(
                    f"MERCATKIT_Ridge_{index}",
                    (cx, -21.5, ridge),
                    (cx, 21.5, ridge),
                    0.14,
                    mats["iron"],
                )
            )
    return objects


def station_fixed(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    objects.append(
        box(
            "STATION_GranitePlinth",
            (198.0, 77.0, 1.1),
            (0, 0, 0.55),
            mats["stone"],
            0.10,
        )
    )

    # The head house is assembled around the five empty ceremonial portal
    # volumes visible in the reference. Its core stops five metres behind the
    # public facade, preserving real coffered cavities for glass, doors and
    # occupied backing.
    wall_intervals = (
        (-57.0, -46.0),
        (-22.0, -15.0),
        (15.0, 22.0),
        (46.0, 57.0),
    )
    for index, (x0, x1) in enumerate(wall_intervals):
        objects.append(
            box(
                f"STATION_HeadHousePierMass_{index}",
                (x1 - x0, 23.0, 32.5),
                ((x0 + x1) / 2, -27.7, 17.35),
                mats["stone"],
                0.22,
            )
        )
    # The two outer wings are also sectional window assemblies.  Masonry is
    # split into base, crown and narrow bay piers so the physical panes see the
    # recessed room cards; a solid wing block would silently bury every window
    # behind stone despite having detailed frames on its face.
    for side in (-1, 1):
        wing_centre = side * 89.0
        objects.extend(
            [
                box(
                    f"STATION_WingMasonryBase_{side}",
                    (20.0, 23.0, 2.5),
                    (wing_centre, -27.7, 2.35),
                    mats["stone"],
                    0.16,
                ),
                box(
                    f"STATION_WingMasonryCrown_{side}",
                    (20.0, 23.0, 14.3),
                    (wing_centre, -27.7, 25.25),
                    mats["stone"],
                    0.18,
                ),
            ]
        )
        for pier_index, absolute_x in enumerate((83.5, 88.5, 93.5, 98.5)):
            objects.append(
                box(
                    f"STATION_WingMasonryPier_{side}_{pier_index}",
                    (0.92, 23.0, 15.6),
                    (side * absolute_x, -27.7, 10.65),
                    mats["stone"],
                    0.12,
                )
            )
    objects.append(
        box(
            "STATION_ContinuousEntablature",
            (198.0, 23.4, 5.4),
            (0, -27.7, 35.2),
            mats["relief"],
            0.18,
        )
    )
    objects.extend(
        [
            box(
                "STATION_LowerCornice",
                (200.0, 24.2, 0.75),
                (0, -27.9, 32.4),
                mats["stone"],
                0.10,
            ),
            box(
                "STATION_UpperCornice",
                (202.0, 24.8, 0.92),
                (0, -27.9, 38.3),
                mats["stone"],
                0.12,
            ),
            box(
                "STATION_SculptureFrieze",
                (192.0, 1.15, 2.0),
                (0, -40.05, 35.2),
                mats["relief"],
                0.06,
            ),
        ]
    )

    def front_disc(
        name: str,
        radius: float,
        depth: float,
        location: tuple[float, float, float],
        mat: bpy.types.Material,
        vertices: int = 64,
    ) -> bpy.types.Object:
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=vertices,
            radius=radius,
            depth=depth,
            location=location,
            rotation=(math.pi / 2, 0, 0),
        )
        obj = bpy.context.object
        obj.name = name
        obj.data.materials.append(mat)
        return obj

    def station_column(
        name: str,
        x: float,
        y: float,
        *,
        base_z: float = 1.1,
        height: float = 31.8,
        radius: float = 1.92,
    ) -> list[bpy.types.Object]:
        parts: list[bpy.types.Object] = []
        shaft_height = height - 4.2
        shaft_centre = base_z + 2.1 + shaft_height / 2
        parts.extend(
            [
                cylinder(
                    name + "_BasePlinth",
                    radius * 1.62,
                    0.55,
                    (x, y, base_z + 0.275),
                    mats["stone"],
                    40,
                ),
                cylinder(
                    name + "_BaseTorus",
                    radius * 1.32,
                    0.70,
                    (x, y, base_z + 0.9),
                    mats["stone"],
                    40,
                ),
                cylinder(
                    name + "_Shaft",
                    radius,
                    shaft_height,
                    (x, y, shaft_centre),
                    mats["stone"],
                    48,
                ),
            ]
        )
        # Twenty physical flutes catch light in hero views.
        for flute in range(20):
            angle = 2 * math.pi * flute / 20
            parts.append(
                cylinder(
                    f"{name}_Flute_{flute}",
                    0.075,
                    shaft_height - 0.6,
                    (
                        x + (radius + 0.035) * math.cos(angle),
                        y + (radius + 0.035) * math.sin(angle),
                        shaft_centre,
                    ),
                    mats["relief"],
                    10,
                )
            )
        capital_z = base_z + height - 1.45
        parts.extend(
            [
                cylinder(
                    name + "_Neck",
                    radius * 1.18,
                    0.48,
                    (x, y, capital_z - 0.45),
                    mats["stone"],
                    40,
                ),
                cylinder(
                    name + "_CapitalBell",
                    radius * 1.62,
                    0.72,
                    (x, y, capital_z + 0.12),
                    mats["relief"],
                    40,
                ),
                box(
                    name + "_Abacus",
                    (radius * 3.65, radius * 3.65, 0.48),
                    (x, y, capital_z + 0.70),
                    mats["stone"],
                    0.08,
                ),
            ]
        )
        for side_x in (-1, 1):
            for side_y in (-1, 1):
                parts.append(
                    sphere(
                        f"{name}_Volute_{side_x}_{side_y}",
                        0.42,
                        (
                            x + side_x * radius * 1.30,
                            y + side_y * radius * 1.30,
                            capital_z + 0.22,
                        ),
                        mats["relief"],
                        (1.0, 0.72, 0.72),
                        20,
                        10,
                    )
                )
        return parts

    def station_portal(
        name: str,
        centre_x: float,
        width: float,
        height: float,
        *,
        stair_width: float,
    ) -> list[bpy.types.Object]:
        parts: list[bpy.types.Object] = []
        sill = 2.55
        radius = width / 2
        spring = sill + height - radius
        facade_y = -40.15
        parts.append(
            arched_panel(
                name + "_Glass",
                centre_x,
                facade_y - 0.24,
                sill,
                width - 2.2,
                height - 1.6,
                mats["portal_glass"],
                segments=48,
            )
        )
        parts.append(
            arched_panel(
                name + "_OccupiedBackplate",
                centre_x,
                -35.25,
                sill + 0.35,
                width - 3.3,
                height - 2.4,
                mats["station_interior"],
                segments=48,
            )
        )
        for light_index, light_z in enumerate((7.0, 13.0, 19.0, 25.0)):
            usable_width = max(
                5.0,
                2.0
                * math.sqrt(
                    max(
                        0.0,
                        (radius - 2.1) ** 2
                        - max(0.0, light_z - spring) ** 2,
                    )
                )
                if light_z > spring
                else width - 5.0,
            )
            parts.append(
                box(
                    f"{name}_WarmInteriorBand_{light_index}",
                    (usable_width * 0.78, 0.20, 0.30),
                    (centre_x, -35.55, light_z),
                    mats["warm"],
                )
            )
        for side in (-1, 1):
            parts.append(
                box(
                    f"{name}_DeepJamb_{side}",
                    (2.15, 5.4, spring - sill + 0.9),
                    (
                        centre_x + side * (radius - 0.4),
                        -37.55,
                        sill + (spring - sill + 0.9) / 2,
                    ),
                    mats["stone"],
                    0.12,
                )
            )
        # Three concentric stone arches and radial coffers make the portal a
        # carved void rather than another window pasted onto a wall.
        arch_depths = (-40.65, -38.25, -35.9)
        arch_radii = (1.05, 0.72, 0.52)
        arch_points: list[list[tuple[float, float, float]]] = []
        for ring, (y, beam_radius) in enumerate(zip(arch_depths, arch_radii)):
            points = [
                (
                    centre_x + radius * math.cos(math.pi * index / 32),
                    y,
                    spring + radius * math.sin(math.pi * index / 32),
                )
                for index in range(33)
            ]
            arch_points.append(points)
            for index in range(32):
                parts.append(
                    beam(
                        f"{name}_StoneArch_{ring}_{index}",
                        points[index],
                        points[index + 1],
                        beam_radius,
                        mats["stone"] if ring != 1 else mats["relief"],
                    )
                )
        # A restrained outer course of actual voussoir blocks supplies the
        # deep carved-stone cadence visible in the reference.  Each block is
        # tangent to the portal curve rather than painted into the glass.
        voussoir_radius = radius + 0.88
        voussoir_count = 23 if width > 26 else 21
        for voussoir in range(voussoir_count):
            angle = math.pi * (voussoir + 0.5) / voussoir_count
            x = centre_x + voussoir_radius * math.cos(angle)
            z = spring + voussoir_radius * math.sin(angle)
            block = box(
                f"{name}_Voussoir_{voussoir}",
                (
                    math.pi * voussoir_radius / voussoir_count * 0.96,
                    1.28,
                    1.02,
                ),
                (x, facade_y - 0.94, z),
                mats["relief"] if voussoir % 2 else mats["stone"],
            )
            block.rotation_euler[1] = -(angle + math.pi / 2)
            parts.append(block)
        keystone = box(
            name + "_Keystone",
            (1.82 if width > 26 else 1.60, 1.55, 2.35),
            (
                centre_x,
                facade_y - 1.02,
                spring + voussoir_radius + 0.22,
            ),
            mats["relief"],
            0.10,
        )
        parts.append(keystone)
        for coffer in range(0, 33, 4):
            parts.append(
                beam(
                    f"{name}_CofferedSoffit_{coffer}",
                    arch_points[0][coffer],
                    arch_points[-1][coffer],
                    0.23,
                    mats["coffer"],
                )
            )
        # Warm stone coffers bridge the nested arch rings as actual recessed
        # ceiling panels. Their alternating depth is visible at plaza level.
        for coffer in range(2, 32, 4):
            outer_a = arch_points[0][coffer - 1]
            outer_b = arch_points[0][coffer + 1]
            inner_b = arch_points[-1][coffer + 1]
            inner_a = arch_points[-1][coffer - 1]
            parts.append(
                mesh_object(
                    f"{name}_CofferedPanel_{coffer}",
                    [outer_a, outer_b, inner_b, inner_a],
                    [(0, 1, 2, 3)],
                    mats["coffer"],
                    [(0, 0), (1, 0), (1, 1), (0, 1)],
                    bevel=0.03,
                )
            )
        # Bronze fanlight radial muntins.
        for spoke in range(13):
            angle = math.pi * spoke / 12
            parts.append(
                beam(
                    f"{name}_FanlightSpoke_{spoke}",
                    (centre_x, facade_y - 0.48, spring),
                    (
                        centre_x + (radius - 1.35) * math.cos(angle),
                        facade_y - 0.48,
                        spring + (radius - 1.35) * math.sin(angle),
                    ),
                    0.11,
                    mats["bronze"],
                )
            )
        door_count = 5 if width > 30 else 4
        door_span = (width - 5.0) / door_count
        for door in range(door_count):
            x = centre_x - (door_count - 1) * door_span / 2 + door * door_span
            parts.append(
                box(
                    f"{name}_DoorPane_{door}",
                    (door_span - 0.35, 0.16, 5.9),
                    (x, facade_y - 0.58, 5.50),
                    mats["portal_glass"],
                )
            )
            for edge in (-1, 1):
                parts.append(
                    box(
                        f"{name}_DoorJamb_{door}_{edge}",
                        (0.12, 0.28, 6.1),
                        (
                            x + edge * (door_span - 0.35) / 2,
                            facade_y - 0.66,
                            5.50,
                        ),
                        mats["bronze"],
                    )
                )
        door_group_width = min(width * 0.52, door_count * door_span)
        parts.extend(
            [
                box(
                    name + "_DoorEntablature",
                    (door_group_width + 1.0, 0.55, 0.42),
                    (centre_x, facade_y - 0.82, 8.62),
                    mats["bronze"],
                    0.06,
                ),
                triangular_prism(
                    name + "_DoorPediment",
                    door_group_width + 1.8,
                    2.15,
                    0.85,
                    (centre_x, facade_y - 0.76, 8.72),
                    mats["coffer"],
                ),
            ]
        )
        # Each stair is seated into the same granite plinth. The flight rises
        # toward the recessed doors; the earlier outward-rising order made
        # these read as thin ledges instead of a ceremonial entrance.
        parts.append(
            box(
                name + "_ThresholdLanding",
                (stair_width, 2.4, sill),
                (centre_x, -40.2, sill / 2),
                mats["stone"],
                0.04,
            )
        )
        for step in range(9):
            rise = sill / 9.0
            depth = 0.82
            level = 8 - step
            parts.append(
                box(
                    f"{name}_IntegratedStep_{step}",
                    (stair_width + step * 0.35, depth, rise),
                    (
                        centre_x,
                        -41.55 - step * depth,
                        rise / 2 + level * rise,
                    ),
                    mats["stone"],
                    0.025,
                )
            )
            parts.append(
                box(
                    f"{name}_StepNosing_{step}",
                    (stair_width + step * 0.35 + 0.05, 0.09, 0.10),
                    (
                        centre_x,
                        -41.55 - step * depth - depth / 2,
                        level * rise + 0.10,
                    ),
                    mats["relief"],
                )
            )
        return parts

    portal_specs = (
        ("OuterLeft", -68.0, 22.0, 24.5, 24.0),
        ("InnerLeft", -34.0, 24.0, 27.5, 26.0),
        ("Central", 0.0, 30.0, 31.0, 32.0),
        ("InnerRight", 34.0, 24.0, 27.5, 26.0),
        ("OuterRight", 68.0, 22.0, 24.5, 24.0),
    )
    for label, centre_x, portal_width, portal_height, stair_width in portal_specs:
        objects.extend(
            station_portal(
                f"STATION_{label}Portal",
                centre_x,
                portal_width,
                portal_height,
                stair_width=stair_width,
            )
        )
    for _, centre_x, _, _, stair_width in portal_specs:
        for side in (-1, 1):
            rail_x = centre_x + side * (stair_width / 2 + 0.65)
            objects.append(
                beam(
                    f"STATION_StairCheek_{centre_x}_{side}",
                    (rail_x + side * 1.35, -48.8, 0.65),
                    (rail_x, -40.2, 3.25),
                    0.48,
                    mats["stone"],
                )
            )
            if centre_x in {-68.0, 0.0, 68.0}:
                objects.append(
                    box(
                        f"STATION_StairSculpturePedestal_{centre_x}_{side}",
                        (3.0, 3.0, 2.2),
                        (rail_x + side * 1.15, -48.1, 1.1),
                        mats["stone"],
                        0.10,
                    )
                )
                objects.extend(
                    [
                        cylinder(
                            f"STATION_StairFigureBody_{centre_x}_{side}",
                            0.58,
                            2.3,
                            (rail_x + side * 1.15, -48.1, 3.25),
                            mats["relief"],
                            18,
                        ),
                        sphere(
                            f"STATION_StairFigureHead_{centre_x}_{side}",
                            0.48,
                            (rail_x + side * 1.15, -48.1, 4.75),
                            mats["relief"],
                            (1.0, 0.92, 1.08),
                            18,
                            9,
                        ),
                    ]
                )

    # Paired giant-order columns bracket every portal and continue the exact
    # Beaux-Arts structural rhythm across the head house.
    column_positions = (-80.2, -57.8, -45.2, -22.8, -14.2, 14.2, 22.8, 45.2, 57.8, 80.2)
    for index, x in enumerate(column_positions):
        objects.extend(station_column(f"STATION_Corinthian_{index}", x, -41.2))

    # Outer wings use true recessed arched windows with separate room cards,
    # returns and mullions instead of a flat repetitive image.
    for side in (-1, 1):
        for bay in range(3):
            x = side * (86.0 + bay * 5.0)
            pane_y = -40.25
            objects.append(
                arched_panel(
                    f"STATION_WingPane_{side}_{bay}",
                    x,
                    pane_y,
                    2.6,
                    4.25,
                    15.2,
                    mats["portal_glass"],
                    segments=24,
                )
            )
            objects.append(
                arched_panel(
                    f"STATION_WingRoom_{side}_{bay}",
                    x,
                    -35.4,
                    2.95,
                    3.55,
                    14.3,
                    mats["station_interior"],
                    segments=24,
                )
            )
            objects.extend(
                arch_frame(
                    f"STATION_WingFrame_{side}_{bay}",
                    x,
                    pane_y - 0.15,
                    2.6,
                    4.85,
                    15.7,
                    0.40,
                    mats["stone"],
                )
            )
            objects.append(
                box(
                    f"STATION_WingMullion_{side}_{bay}",
                    (0.11, 0.22, 12.4),
                    (x, pane_y - 0.28, 8.8),
                    mats["bronze"],
                )
            )
            for transom_index, z in enumerate((6.0, 10.0, 13.0)):
                objects.append(
                    box(
                        f"STATION_WingTransom_{side}_{bay}_{transom_index}",
                        (3.85, 0.22, 0.10),
                        (x, pane_y - 0.28, z),
                        mats["bronze"],
                    )
                )
        for pier_index in range(4):
            x = side * (83.5 + pier_index * 5.0)
            objects.extend(
                station_column(
                    f"STATION_WingEngagedOrder_{side}_{pier_index}",
                    x,
                    -40.65,
                    base_z=1.1,
                    height=24.5,
                    radius=0.72,
                )
            )

    # Central clock attic, balustrade and sculpture groups.
    objects.extend(
        [
            box(
                "STATION_ClockAttic",
                (23.0, 12.0, 8.5),
                (0, -31.2, 42.7),
                mats["stone"],
                0.22,
            ),
            box(
                "STATION_ClockPediment",
                (27.0, 13.0, 0.86),
                (0, -31.2, 47.3),
                mats["relief"],
                0.15,
            ),
        ]
    )
    objects.append(
        triangular_prism(
            "STATION_ClockPedimentRoof",
            25.0,
            5.2,
            3.5,
            (0, -36.2, 47.4),
            mats["stone"],
        )
    )
    objects.extend(
        [
            beam(
                "STATION_ClockPedimentLeftCornice",
                (-12.5, -38.05, 47.5),
                (0.0, -38.05, 52.7),
                0.36,
                mats["relief"],
            ),
            beam(
                "STATION_ClockPedimentRightCornice",
                (0.0, -38.05, 52.7),
                (12.5, -38.05, 47.5),
                0.36,
                mats["relief"],
            ),
        ]
    )
    clock_face = front_disc(
        "STATION_ClockFace",
        3.35,
        0.42,
        (0, -38.0, 42.7),
        mats["cream"],
    )
    objects.append(clock_face)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=3.62,
        minor_radius=0.34,
        major_segments=64,
        minor_segments=12,
        location=(0, -38.25, 42.7),
        rotation=(math.pi / 2, 0, 0),
    )
    clock_ring = bpy.context.object
    clock_ring.name = "STATION_ClockRing"
    clock_ring.data.materials.append(mats["relief"])
    objects.append(clock_ring)
    for side in (-1, 1):
        objects.extend(
            station_column(
                f"STATION_ClockPilaster_{side}",
                side * 5.6,
                -38.0,
                base_z=38.2,
                height=8.8,
                radius=0.52,
            )
        )
        bpy.ops.mesh.primitive_torus_add(
            major_radius=1.05,
            minor_radius=0.20,
            major_segments=32,
            minor_segments=10,
            location=(side * 8.1, -38.15, 43.7),
            rotation=(math.pi / 2, 0, 0),
        )
        volute = bpy.context.object
        volute.name = f"STATION_ClockVolute_{side}"
        volute.data.materials.append(mats["relief"])
        objects.append(volute)
        objects.append(
            beam(
                f"STATION_ClockGarland_{side}",
                (side * 3.9, -38.38, 40.1),
                (side * 8.1, -38.38, 43.7),
                0.24,
                mats["relief"],
            )
        )
    objects.extend(
        [
            cylinder(
                "STATION_ClockApexFigureBody",
                0.56,
                2.5,
                (0.0, -38.0, 54.0),
                mats["relief"],
                18,
            ),
            sphere(
                "STATION_ClockApexFigureHead",
                0.46,
                (0.0, -38.0, 55.6),
                mats["relief"],
                (1.0, 0.92, 1.08),
                18,
                9,
            ),
        ]
    )
    objects.extend(
        [
            beam(
                "STATION_ClockMinuteHand",
                (0, -38.48, 42.7),
                (0.0, -38.48, 45.2),
                0.13,
                mats["black"],
            ),
            beam(
                "STATION_ClockHourHand",
                (0, -38.50, 42.7),
                (-1.7, -38.50, 43.7),
                0.16,
                mats["black"],
            ),
        ]
    )
    for hour in range(12):
        angle = 2 * math.pi * hour / 12
        objects.append(
            front_disc(
                f"STATION_ClockMarker_{hour}",
                0.11,
                0.12,
                (
                    2.72 * math.sin(angle),
                    -38.50,
                    42.7 + 2.72 * math.cos(angle),
                ),
                mats["black"],
                16,
            )
        )

    # Balustrade runs remain quiet enough not to compete with the portals.
    objects.extend(
        [
            box("STATION_BalustradeBase", (194.0, 1.2, 0.42), (0, -39.6, 39.2), mats["stone"]),
            box("STATION_BalustradeRail", (194.0, 1.2, 0.42), (0, -39.6, 41.5), mats["stone"]),
        ]
    )
    for index, x in enumerate(range(-94, 95, 3)):
        if abs(x) < 18:
            continue
        objects.append(
            cylinder(
                f"STATION_Baluster_{index}",
                0.20,
                2.2,
                (x, -39.6, 40.35),
                mats["stone"],
                16,
            )
        )

    # Stylised stone groups occupy the reference's skyline positions.  These
    # are low-poly sculpture masses, not billboard decoration.
    for group_x in (-49.0, 49.0):
        objects.append(
            box(
                f"STATION_SculpturePedestal_{group_x}",
                (15.0, 6.2, 2.1),
                (group_x, -40.5, 42.15),
                mats["stone"],
                0.12,
            )
        )
        for figure in range(5):
            x = group_x + (figure - 2) * 2.25
            figure_height = 5.0 + (2 - abs(figure - 2)) * 0.78
            objects.extend(
                [
                    cylinder(
                        f"STATION_FigureBody_{group_x}_{figure}",
                        0.86,
                        figure_height * 0.60,
                        (x, -42.0, 43.25 + figure_height * 0.30),
                        mats["relief"],
                        16,
                    ),
                    sphere(
                        f"STATION_FigureHead_{group_x}_{figure}",
                        0.62,
                        (x, -42.0, 43.25 + figure_height * 0.68),
                        mats["relief"],
                        (1.0, 0.92, 1.08),
                        16,
                        8,
                    ),
                ]
            )
            bpy.ops.mesh.primitive_cone_add(
                vertices=20,
                radius1=1.30,
                radius2=0.56,
                depth=figure_height * 0.52,
                location=(
                    x,
                    -42.0,
                    43.15 + figure_height * 0.26,
                ),
            )
            drapery = bpy.context.object
            drapery.name = f"STATION_FigureDrapery_{group_x}_{figure}"
            drapery.data.materials.append(mats["relief"])
            objects.append(drapery)

    def barrel_vault(
        name: str,
        centre_x: float,
        width: float,
        spring_z: float,
        *,
        y_front: float = -18.0,
        y_rear: float = 38.5,
        segments: int = 24,
        bays: int = 14,
    ) -> list[bpy.types.Object]:
        parts: list[bpy.types.Object] = []
        radius = width / 2
        vertices = []
        uv = []
        for angle_index in range(segments + 1):
            angle = math.pi * angle_index / segments
            for bay in range(bays + 1):
                v = bay / bays
                y = y_front + (y_rear - y_front) * v
                vertices.append(
                    (
                        centre_x + radius * math.cos(angle),
                        y,
                        spring_z + radius * 0.96 * math.sin(angle),
                    )
                )
                uv.append((angle_index / segments * 3.0, v * 4.0))
        faces = []
        stride = bays + 1
        for angle_index in range(segments):
            for bay in range(bays):
                a = angle_index * stride + bay
                b = (angle_index + 1) * stride + bay
                faces.append((a, b, b + 1, a + 1))
        parts.append(
            mesh_object(
                name + "_GlassShell",
                vertices,
                faces,
                mats["shed_glass"],
                uv,
                smooth=True,
            )
        )
        # Tall glazed spring walls make each shed a complete rail hall in
        # side/rear views rather than a roof cage floating behind the head
        # house.
        wall_bottom = 5.0
        end_glass_width = width - 1.4
        end_glass_height = (
            spring_z - wall_bottom + end_glass_width / 2
        )
        for end_name, end_y, frame_y in (
            ("Front", y_front + 0.10, y_front - 0.16),
            ("Rear", y_rear - 0.10, y_rear + 0.16),
        ):
            parts.append(
                arched_panel(
                    f"{name}_{end_name}GlazedWall",
                    centre_x,
                    end_y,
                    wall_bottom,
                    end_glass_width,
                    end_glass_height,
                    mats["shed_glass"],
                    segments=segments,
                )
            )
            # Full-height vertical mullions and clipped transoms replace the
            # open rib cage that the front-only pilot failed to expose.
            for mullion in range(-5, 6):
                lateral = (radius - 1.3) * mullion / 5.0
                top_z = spring_z + 0.96 * math.sqrt(
                    max(0.0, radius * radius - lateral * lateral)
                )
                parts.append(
                    beam(
                        f"{name}_{end_name}EndMullion_{mullion}",
                        (centre_x + lateral, frame_y, wall_bottom),
                        (centre_x + lateral, frame_y, top_z),
                        0.16,
                        mats["dark"],
                    )
                )
            for transom_index, z in enumerate(
                (
                    wall_bottom + 5.0,
                    wall_bottom + 10.0,
                    spring_z - 1.0,
                    spring_z + radius * 0.34,
                    spring_z + radius * 0.63,
                )
            ):
                if z <= spring_z:
                    half_span = radius - 0.8
                else:
                    half_span = math.sqrt(
                        max(
                            0.0,
                            radius * radius
                            - ((z - spring_z) / 0.96) ** 2,
                        )
                    ) - 0.65
                if half_span > 0.5:
                    parts.append(
                        beam(
                            f"{name}_{end_name}EndTransom_{transom_index}",
                            (centre_x - half_span, frame_y, z),
                            (centre_x + half_span, frame_y, z),
                            0.15,
                            mats["dark"],
                        )
                    )
        for side in (-1, 1):
            wall_x = centre_x + side * radius
            parts.append(
                quad_panel(
                    f"{name}_SideCurtain_{side}",
                    (
                        (wall_x, y_front + 0.4, wall_bottom),
                        (wall_x, y_rear, wall_bottom),
                        (wall_x, y_rear, spring_z),
                        (wall_x, y_front + 0.4, spring_z),
                    ),
                    mats["shed_glass"],
                )
            )
            for mullion, y in enumerate(
                y_front + 0.5 + (y_rear - y_front - 0.5) * index / 14
                for index in range(15)
            ):
                parts.append(
                    box(
                        f"{name}_SidePier_{side}_{mullion}",
                        (0.28, 0.30, spring_z - wall_bottom + 0.5),
                        (wall_x, y, wall_bottom + (spring_z - wall_bottom) / 2),
                        mats["dark"],
                    )
                )
            for transom_index, z in enumerate(
                wall_bottom + (spring_z - wall_bottom) * index / 4
                for index in range(1, 4)
            ):
                parts.append(
                    box(
                        f"{name}_SideTransom_{side}_{transom_index}",
                        (0.30, y_rear - y_front - 0.4, 0.22),
                        (wall_x, (y_front + y_rear + 0.4) / 2, z),
                        mats["dark"],
                    )
                )
        # Full ribs every 3.1 m and longitudinal purlins every 11.25 degrees.
        for rib, y in enumerate(
            y_front + (y_rear - y_front) * index / bays
            for index in range(bays + 1)
        ):
            points = [
                (
                    centre_x + radius * math.cos(math.pi * index / segments),
                    y,
                    spring_z + radius * 0.96 * math.sin(math.pi * index / segments),
                )
                for index in range(segments + 1)
            ]
            for index in range(segments):
                parts.append(
                    beam(
                        f"{name}_Rib_{rib}_{index}",
                        points[index],
                        points[index + 1],
                        0.25,
                        mats["dark"],
                    )
                )
        for purlin in range(0, segments + 1, 4):
            angle = math.pi * purlin / segments
            parts.append(
                beam(
                    f"{name}_Purlin_{purlin}",
                    (
                        centre_x + radius * math.cos(angle),
                        y_front,
                        spring_z + radius * 0.96 * math.sin(angle),
                    ),
                    (
                        centre_x + radius * math.cos(angle),
                        y_rear,
                        spring_z + radius * 0.96 * math.sin(angle),
                    ),
                    0.20,
                    mats["dark"],
                )
            )
        # Front and rear fanlight trusses reveal the shed span above the stone
        # head house and close the rear elevation.
        for end_name, y in (("Front", y_front - 0.12), ("Rear", y_rear + 0.12)):
            end_points = [
                (
                    centre_x + radius * math.cos(math.pi * index / segments),
                    y,
                    spring_z + radius * 0.96 * math.sin(math.pi * index / segments),
                )
                for index in range(segments + 1)
            ]
            for index in range(segments):
                parts.append(
                    beam(
                        f"{name}_{end_name}MonumentalArch_{index}",
                        end_points[index],
                        end_points[index + 1],
                        0.72 if end_name == "Front" else 0.42,
                        mats["relief"] if end_name == "Front" else mats["dark"],
                    )
                )
                if end_name == "Front" and index % 3 == 1:
                    a = end_points[index]
                    b = end_points[index + 1]
                    parts.append(
                        sphere(
                            f"{name}_FrontArchPlaque_{index}",
                            0.52,
                            (
                                (a[0] + b[0]) / 2,
                                y - 0.62,
                                (a[2] + b[2]) / 2,
                            ),
                            mats["relief"],
                            (1.18, 0.34, 0.78),
                            16,
                            8,
                        )
                    )
            for spoke in range(0, segments + 1, 4):
                angle = math.pi * spoke / segments
                parts.append(
                    beam(
                        f"{name}_{end_name}Fan_{spoke}",
                        (centre_x, y, spring_z),
                        (
                            centre_x + radius * math.cos(angle),
                            y,
                            spring_z + radius * 0.96 * math.sin(angle),
                        ),
                        0.18,
                        mats["dark"],
                    )
                )
        return parts

    objects.extend(barrel_vault("STATION_LeftShed", -65.0, 58.0, 21.5))
    objects.extend(barrel_vault("STATION_CentralShed", 0.0, 70.0, 22.0))
    objects.extend(barrel_vault("STATION_RightShed", 65.0, 58.0, 21.5))

    # Long masonry side arcades continue beneath the train-shed curtains. This
    # is the critical oblique-view junction in the reference: monumental
    # stone base below, iron-and-glass rail engineering above.
    for side in (-1, 1):
        objects.extend(
            [
                box(
                    f"STATION_LongSideMasonryBase_{side}",
                    (2.2, 56.0, 8.4),
                    (side * 97.0, 10.5, 5.3),
                    mats["stone"],
                    0.12,
                ),
                box(
                    f"STATION_LongSideCornice_{side}",
                    (2.8, 57.0, 0.72),
                    (side * 97.0, 10.5, 9.85),
                    mats["relief"],
                    0.08,
                ),
            ]
        )
        for bay, y in enumerate(range(-14, 39, 5)):
            pane_x = side * 98.15
            objects.append(
                arched_panel(
                    f"STATION_LongSidePane_{side}_{bay}",
                    pane_x,
                    y,
                    8.2,
                    3.55,
                    11.8,
                    mats["portal_glass"],
                    segments=20,
                    front_axis="x",
                )
            )
            objects.append(
                arched_panel(
                    f"STATION_LongSideRoom_{side}_{bay}",
                    side * 94.15,
                    y,
                    8.45,
                    3.1,
                    11.1,
                    mats["station_interior"],
                    segments=20,
                    front_axis="x",
                )
            )
            objects.extend(
                arch_frame(
                    f"STATION_LongSideFrame_{side}_{bay}",
                    side * 98.25,
                    y,
                    8.2,
                    4.05,
                    12.25,
                    0.32,
                    mats["stone"],
                    front_axis="x",
                )
            )
            objects.append(
                box(
                    f"STATION_LongSideMullion_{side}_{bay}",
                    (0.20, 0.10, 9.1),
                    (side * 98.38, y, 13.6),
                    mats["bronze"],
                )
            )
            for transom_index, z in enumerate((12.0, 15.0, 17.6)):
                objects.append(
                    box(
                        f"STATION_LongSideTransom_{side}_{bay}_{transom_index}",
                        (0.20, 3.15, 0.10),
                        (side * 98.38, y, z),
                        mats["bronze"],
                    )
                )

    # Authored side/rear head-house elevations and service bands.
    for side in (-1, 1):
        objects.append(
            box(
                f"STATION_SideHeadHouse_{side}",
                (1.4, 22.0, 31.5),
                (side * 98.4, -28.0, 16.85),
                mats["stone"],
                0.10,
            )
        )
        for bay, y in enumerate((-35.0, -30.0, -25.0, -20.0)):
            objects.append(
                arched_panel(
                    f"STATION_SideWindow_{side}_{bay}",
                    side * 99.15,
                    y,
                    4.0,
                    3.2,
                    10.5,
                    mats["portal_glass"],
                    segments=20,
                    front_axis="x",
                )
            )
            objects.extend(
                arch_frame(
                    f"STATION_SideWindowFrame_{side}_{bay}",
                    side * 99.20,
                    y,
                    4.0,
                    3.8,
                    11.0,
                    0.28,
                    mats["stone"],
                    front_axis="x",
                )
            )
    objects.append(
        box(
            "STATION_RearServiceBand",
            (196.0, 1.1, 8.0),
            (0, 39.0, 4.6),
            mats["stone"],
            0.10,
        )
    )
    return objects


def station_module(
    role: str,
    variant: str,
    height: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    if role == "podium":
        objects.append(
            box(
                "STATIONKIT_GranitePodium",
                (198.0, 77.0, 1.0),
                (0, 0, 0.5),
                mats["stone"],
                0.08,
            )
        )
        for centre in (-48.0, 0.0, 48.0):
            portal_width = 8.5 if centre == 0 else 7.0
            objects.append(
                arched_panel(
                    f"STATIONKIT_PodiumPortal_{centre}",
                    centre,
                    -38.5,
                    0.2,
                    portal_width,
                    height - 0.2,
                    mats["portal_glass"],
                    segments=28,
                )
            )
            objects.extend(
                arch_frame(
                    f"STATIONKIT_PodiumArch_{centre}",
                    centre,
                    -38.7,
                    0.2,
                    portal_width + 0.8,
                    height - 0.1,
                    0.35,
                    mats["stone"],
                )
            )
    elif role == "floor":
        objects.append(
            box(
                f"STATIONKIT_FloorCore_{variant}",
                (196.0, 75.0, height),
                (0, 0, height / 2),
                mats["stone"],
                0.10,
            )
        )
        spacing = {"typical_a": 10.0, "typical_b": 12.0, "typical_c": 8.5}[variant]
        x = -90.0
        bay = 0
        while x <= 90.0:
            objects.append(
                arched_panel(
                    f"STATIONKIT_FloorPane_{variant}_{bay}",
                    x,
                    -37.65,
                    0.5,
                    4.0,
                    height - 0.9,
                    mats["portal_glass"],
                    segments=18,
                )
            )
            objects.extend(
                arch_frame(
                    f"STATIONKIT_FloorFrame_{variant}_{bay}",
                    x,
                    -37.82,
                    0.5,
                    4.6,
                    height - 0.6,
                    0.25,
                    mats["stone"],
                )
            )
            x += spacing
            bay += 1
    elif role == "crown":
        objects.extend(
            [
                box(
                    "STATIONKIT_CrownEntablature",
                    (200.0, 77.0, height * 0.66),
                    (0, 0, height * 0.33),
                    mats["relief"],
                    0.12,
                ),
                box(
                    "STATIONKIT_CrownCornice",
                    (200.4, 78.0, 0.52),
                    (0, 0, height - 0.26),
                    mats["stone"],
                    0.08,
                ),
            ]
        )
    elif role == "roof":
        for centre, width in ((-66.0, 62.0), (0.0, 66.0), (66.0, 62.0)):
            radius = width / 2
            segments = 24
            vertices = []
            uv = []
            for angle_index in range(segments + 1):
                angle = math.pi * angle_index / segments
                for end, y in enumerate((-37.5, 37.5)):
                    vertices.append(
                        (
                            centre + radius * math.cos(angle),
                            y,
                            0.2 + (height - 0.2) * math.sin(angle),
                        )
                    )
                    uv.append((angle_index / segments * 2.0, float(end)))
            faces = []
            for angle_index in range(segments):
                a = angle_index * 2
                faces.append((a, a + 2, a + 3, a + 1))
            objects.append(
                mesh_object(
                    f"STATIONKIT_RoofGlass_{centre}",
                    vertices,
                    faces,
                    mats["shed_glass"],
                    uv,
                    smooth=True,
                )
            )
            for angle_index in range(segments):
                a0 = math.pi * angle_index / segments
                a1 = math.pi * (angle_index + 1) / segments
                for end, y in enumerate((-37.5, 37.5)):
                    objects.append(
                        beam(
                            f"STATIONKIT_RoofRib_{centre}_{end}_{angle_index}",
                            (
                                centre + radius * math.cos(a0),
                                y,
                                0.2 + (height - 0.2) * math.sin(a0),
                            ),
                            (
                                centre + radius * math.cos(a1),
                                y,
                                0.2 + (height - 0.2) * math.sin(a1),
                            ),
                            0.18,
                            mats["dark"],
                        )
                    )
    return objects


def render_elevation(
    folder: Path,
    family: str,
    width: float,
    depth: float,
    height: float,
) -> str:
    scene = bpy.context.scene
    camera = scene.camera
    if camera is None:
        aim_camera((0, -max(width, depth) * 2.0, height * 0.50), (0, 0, height * 0.50), 70)
        camera = scene.camera
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = max(height * 1.32, width / 1.6 * 1.08)
    camera.location = (0, -max(width, depth) * 2.2, height * 0.50)
    camera.rotation_euler = (Vector((0, 0, height * 0.50)) - camera.location).to_track_quat(
        "-Z", "Y"
    ).to_euler()
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1000
    scene.render.image_settings.file_format = "JPEG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.quality = 95
    scene.render.filepath = str(folder / "elevation.jpg")
    bpy.ops.render.render(write_still=True)
    camera.data.type = "PERSP"
    scene.render.image_settings.file_format = "PNG"
    return "elevation.jpg"


def module_payload(
    family: str,
    role: str,
    variant: str,
    filename: str,
    width: float,
    depth: float,
    height: float,
    floor_height: float,
    tris: int,
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
        "module_family": family,
        "width_m": width,
        "depth_m": depth,
        "height_m": height,
        "floor_height_m": floor_height,
        "repeatable_z": repeatable,
        "allow_inset_footprint": True,
        "triangle_count": tris,
        "material_count": 12,
        "texture_keys": sorted(skin["zones"]),
        "ao_baked": True,
        "size_bytes": size_bytes,
    }


def texture_inventory(skin: dict) -> list[dict]:
    inventory = []
    for lod, assets in skin["atlases"].items():
        for channel, path in assets.items():
            inventory.append(
                {
                    "key": f"{lod}_atlas_{channel}",
                    "path": path,
                    "lod": lod,
                    "channel": channel,
                }
            )
    return inventory


def facade_contract(family: str, config: dict, skin: dict) -> dict:
    return {
        "schema": "facade-sheet@5",
        "source_directory": f"/families/{family}",
        "model": "gpt-image-2",
        "style_reference": "elevation.jpg",
        "goalpost_reference": config["goalpost"],
        "goalpost_policy": (
            "The locked catalogue image controls silhouette, proportions, "
            "openings, roof hierarchy, entrance geometry and material hierarchy."
        ),
        "runtime_material_profile": "pbr_physical_glazing_v2",
        "geometry_detail_profile": "hero",
        "pbr_channels": ["albedo", "normal", "roughness", "ao", "depth", "emissive"],
        "shadow_neutral": {
            "enabled": True,
            "method": "custom archetype material sources under neutral survey light",
            "lighting_authority": "City Prompt environment and sun",
        },
        "bay_strategy": {
            "fixed_end_bays": [0, 3],
            "repeatable_middle_bays": [1, 2],
            "middle_variants": ["typical_a", "typical_b", "typical_c"],
            "rule": (
                "the landmark silhouette, entrance, corners, crown and roof stay "
                "fixed; only the conservative fallback middle band repeats"
            ),
        },
        "delivery": {
            "near_atlas_width_px": 2048,
            "far_atlas_width_px": 1024,
            "near_usage": "close-range physical glazing and PBR materials",
            "far_usage": "city-scale baked material reference",
            "container": "PNG sources embedded into delivery GLBs; KTX2/UASTC at runtime packaging",
        },
        "assembly_contract": {
            "fixed": ["podium/entrance", "corner returns", "crown", "roof"],
            "repeatable": ["typical_a", "typical_b", "typical_c"],
            "side_elevations": (
                "front, left, right, rear and roof are authored as related but "
                "distinct construction; no elevation is a generic extrusion"
            ),
            "elevation_coverage": {
                "front": "primary public entrance with physical openings and glazing",
                "left": "authored secondary elevation with recessed occupied glazing",
                "right": "authored secondary elevation with recessed occupied glazing",
                "rear": "authored service/secondary elevation",
                "roof": "fully modeled landmark roof construction",
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


def build_family(
    family: str,
    config: dict,
    output_root: Path,
    view_set: str,
    skip_renders: bool = False,
) -> None:
    clear_scene()
    folder = output_root / family
    folder.mkdir(parents=True, exist_ok=True)
    skin = load_skin_manifest(folder)
    if skin is None:
        raise FileNotFoundError(folder / "textures" / "skin_manifest.json")
    mats = family_palette(folder)
    width, depth, height = config["dimensions"]
    min_floors, max_floors, native_floors = config["floors"]

    if family == "concert-hall-modern":
        fixed_objects = concert_fixed(mats)
        module_builder = concert_module
    elif family == "barcelona-mercat":
        fixed_objects = mercat_fixed(mats)
        module_builder = mercat_module
    else:
        fixed_objects = station_fixed(mats)
        module_builder = station_module

    normalize_world_bounds(fixed_objects, config["dimensions"])
    shift_to_ground(fixed_objects)
    assembled_path = folder / f"{family}_assembled.glb"
    export_glb(assembled_path, fixed_objects)
    fixed_triangles = triangle_count(fixed_objects)

    if skip_renders:
        renders = sorted(path.name for path in folder.glob(f"{family}_*.png"))
        if (folder / "elevation.jpg").is_file():
            renders.append("elevation.jpg")
    else:
        selected_roles = None
        if view_set == "pilot":
            selected_roles = {"preview", "front_corner_oblique", "facade_close", "aerial"}
        renders = render_views(
            folder,
            family,
            width,
            depth,
            height,
            selected_roles=selected_roles,
        )
        renders.append(render_elevation(folder, family, width, depth, height))
        delete_objects(
            [obj for obj in list(bpy.data.objects) if obj.name.startswith("PRESENTATION_")]
        )

    if module_builder is None:
        raise NotImplementedError(f"{family} module builder")
    delete_objects(fixed_objects)
    role_specs = [
        ("podium", "default", config["floor_height_m"]),
        ("floor", "typical_a", config["floor_height_m"]),
        ("floor", "typical_b", config["floor_height_m"]),
        ("floor", "typical_c", config["floor_height_m"]),
        ("crown", "crown", config["floor_height_m"]),
        ("roof", "default", 8.0),
    ]
    modules = []
    for role, variant, module_height in role_specs:
        objects = module_builder(role, variant, module_height, mats)
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
                width,
                depth,
                module_height,
                config["floor_height_m"],
                triangle_count(objects),
                path.stat().st_size,
                skin,
            )
        )
        delete_objects(objects)

    footprint = {
        "preferredProfiles": ["rectangle"],
        "minimumPreferredProfiles": 1,
        "profileRationale": (
            "This is a one-front landmark whose entrance and roof silhouette "
            "must not be duplicated around L, U or courtyard segments."
        ),
        "fixedLandmarkScaleBand": config["fixed_landmark_scale_band"],
        **config["profiles"],
        "profiles": {"rectangle": config["profiles"]},
    }
    source_provenance = {
        "kind": "imagegen_goalpost_plus_authored_parametric_landmark",
        "catalogue_archetype_id": config["archetype_id"],
        "catalogue_variant_id": config["variant_id"],
        "goalpost": config["goalpost"],
        "goalpost_local_source": "textures/source/archetype-goalpost.png",
        "goalpost_prompt": "textures/source/goalpost-source.json",
        "angle_reference": "textures/source/angle-reference-v2.png",
        "angle_reference_prompt": "textures/source/angle-reference-source-v2.json",
        "material_source": f"textures/source/{family}_material_source.png",
        "material_source_prompt": "textures/source/material-source-v2.json",
        "elevation_source": f"/families/{family}/elevation.jpg",
        "skin_manifest": "textures/skin_manifest.json",
        "generator": "tools/archetype_compiler/generate_wave3_expansion_families.py",
    }
    assembled = {
        "filename": assembled_path.name,
        "floors": native_floors,
        "uses_setback": False,
        "uses_crown": True,
        "height_m": height,
        "triangle_count": fixed_triangles,
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
        "massing_graph": {"type": "fixed_landmark", "silhouette": family},
        "texture_keys": sorted(skin["zones"]),
        "ao_baked": True,
    }
    manifest = {
        "manifest_schema": 3,
        "grammar_schema_version": 3,
        "generator": {
            "name": "archetype_compiler/generate_wave3_expansion_families.py",
            "version": "1.0.0",
            "blender_version": bpy.app.version_string,
            "render_engine": "BLENDER_EEVEE",
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "family": family,
        "archetype_id": config["archetype_id"],
        "archetype_label": config["label"],
        "variant_id": config["variant_id"],
        "generation_archetype_id": config["generation_archetype_id"],
        "archetype_aliases": config["aliases"],
        "aesthetic_category_id": config["aesthetic_category_id"],
        "development_type": config["development_type"],
        "reuse_keys": config["reuse_keys"],
        "generation_tags": [
            "wave3",
            "fixed_landmark",
            "sculpted_silhouette",
            "custom_pbr_skin",
            *config["kits"],
        ],
        "footprint_compatibility": footprint,
        "coordinate_contract": COORDINATE_CONTRACT,
        "textures": texture_inventory(skin),
        "facade_sheet": facade_contract(family, config, skin),
        "massing_graph": {
            "type": "fixed_landmark",
            "silhouette": family,
            "render_locked": True,
            "goalpost": config["goalpost"],
        },
        "material_budget": {
            "max_assembled_materials": 24,
            "rationale": (
                "The landmark keeps shell, structure, physical glazing, occupied "
                "interior, roof and accent materials separate so construction "
                "depth remains legible in the Direct 3D hero range."
            ),
        },
        "dimensions": {
            "width_m": width,
            "depth_m": depth,
            "podium_height_m": config["floor_height_m"],
            "floor_height_m": config["floor_height_m"],
            "setback_height_m": config["floor_height_m"],
            "roof_height_m": 8.0,
            "crown_height_m": config["floor_height_m"],
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
        "architectural_identity": config["identity"],
        "material_zones": config["materials"],
        "glass_profile": config["glass"],
        "source_provenance": source_provenance,
    }
    (folder / f"{family}_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    grammar = {
        "family_id": family,
        "source": {
            "archetype_id": config["archetype_id"],
            "variant_id": config["variant_id"],
            "generation_archetype_id": config["generation_archetype_id"],
            "reuse_keys": config["reuse_keys"],
        },
        "dimensions": manifest["dimensions"],
        "architectural_signature": {
            "identity": config["identity"],
            "material_zones": config["materials"],
            "glass_profile": config["glass"],
            "kits": config["kits"],
        },
        "archetype_aliases": config["aliases"],
        "footprint_compatibility": footprint,
        "massing_graph": manifest["massing_graph"],
    }
    (folder / "grammar.json").write_text(
        json.dumps(grammar, indent=2) + "\n",
        encoding="utf-8",
    )
    (folder / "archetype-source.json").write_text(
        json.dumps(source_provenance, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"[wave3-expansion] {family}: {fixed_triangles:,} tris, "
        f"{len(modules)} modules, {len(renders)} renders",
        flush=True,
    )


def render_existing_family(
    family: str,
    output_root: Path,
    view_set: str,
) -> None:
    """Refresh acceptance renders from the delivered GLB without re-exporting it."""
    clear_scene()
    folder = output_root / family
    manifest_path = folder / f"{family}_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assembled_path = folder / manifest["assembled"]["filename"]
    if not assembled_path.is_file():
        raise FileNotFoundError(assembled_path)

    bpy.ops.import_scene.gltf(filepath=str(assembled_path))
    dimensions = manifest["dimensions"]
    selected_roles = None
    if view_set == "pilot":
        selected_roles = {"preview", "front_corner_oblique", "facade_close", "aerial"}
    renders = render_views(
        folder,
        family,
        float(dimensions["width_m"]),
        float(dimensions["depth_m"]),
        float(manifest["assembled"]["height_m"]),
        selected_roles=selected_roles,
    )
    renders.append(
        render_elevation(
            folder,
            family,
            float(dimensions["width_m"]),
            float(dimensions["depth_m"]),
            float(manifest["assembled"]["height_m"]),
        )
    )
    delete_objects(
        [obj for obj in list(bpy.data.objects) if obj.name.startswith("PRESENTATION_")]
    )
    if view_set == "all":
        manifest["renders"] = renders
        manifest_path.write_text(
            json.dumps(manifest, indent=2) + "\n",
            encoding="utf-8",
        )
    print(
        f"[wave3-expansion-render] {family}: "
        f"{len(renders)} reviewed renders from {assembled_path.name}",
        flush=True,
    )


def main() -> int:
    args = parse_args()
    output_root = args.output_root.resolve()
    selected = args.family or list(FAMILIES)
    for family in selected:
        if args.render_existing:
            render_existing_family(family, output_root, args.view_set)
        else:
            build_family(
                family,
                FAMILIES[family],
                output_root,
                args.view_set,
                skip_renders=args.skip_renders,
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
