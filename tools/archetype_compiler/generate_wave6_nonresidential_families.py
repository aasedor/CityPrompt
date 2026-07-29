"""Author the Wave 6 reference-locked non-residential LEGO families.

The fixed assembled GLBs own the distinctive silhouette and construction of
each selected catalogue variant.  A restrained six-role stack accompanies each
landmark so the planner can accept imperfect user footprints and repeat the
family for targets outside the clean fixed-landmark scale band.

Run with Blender 5.x from the repository root:

    blender --background --factory-startup --python \
      tools/archetype_compiler/generate_wave6_nonresidential_families.py -- \
      --output-root frontend/public/families \
      --family deconstructivist-museum --view-set pilot
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


FAMILIES: dict[str, dict] = {
    "deconstructivist-museum": {
        "archetype_id": "monumental_museum_axis",
        "variant_id": "museum_contemporary_deconstructivist",
        "generation_archetype_id": "museum_contemporary_deconstructivist",
        "label": "Monumental Museum — Deconstructivist Titanium",
        "dimensions": (70.0, 40.7, 34.0),
        "floors": (2, 5, 5),
        "floor_height_m": 6.0,
        "glass_profile": "museum_atrium_low_iron",
        "aesthetic_category_id": "contemporary_cultural",
        "development_type": "institutional",
        "aliases": [
            "monumental_museum_axis",
            "museum_contemporary_deconstructivist",
        ],
        "reuse_keys": [
            "monumental_museum_axis",
            "museum_contemporary_deconstructivist",
            "Museum / Gallery",
            "Civic / Institutional",
        ],
        "identity": (
            "Fractured champagne-silver gallery towers frame a tall widening, "
            "inward-leaning low-iron atrium, with serrated parapets, deep "
            "cantilever notches and a carved triangular public entry."
        ),
        "materials": (
            "champagne-silver titanium panel rainscreen; charcoal structural "
            "steel; low-iron faceted atrium glass; warm timber public interiors; "
            "dark membrane roofs; pale concrete public plinth"
        ),
        "kits": [
            "fractured_gallery_towers",
            "faceted_atrium",
            "serrated_parapets",
            "subtractive_entry",
        ],
        "footprint": {
            "recommendedWidth_m": [45, 100],
            "recommendedDepth_m": [25, 50],
            "recommendedFloors": [2, 5],
        },
        "fixed_band": {"scaleMin": 0.80, "scaleMax": 1.20, "maxAxisRatio": 1.18},
        "goalpost": "/archetypes/buildings/monumental_museum_axis/variant_1.png",
    },
    "terracotta-fin-office": {
        "archetype_id": "modern_glass_office_institutional",
        "variant_id": "glass_office_terracotta_fins",
        "generation_archetype_id": "glass_office_terracotta_fins",
        "label": "Modern Glass Office — Terracotta Fins",
        "dimensions": (43.5, 29.52, 34.2),
        "floors": (5, 20, 8),
        "floor_height_m": 3.8,
        "glass_profile": "terracotta_office_low_e",
        "aesthetic_category_id": "contemporary",
        "development_type": "commercial_office",
        "aliases": [
            "modern_glass_office_institutional",
            "glass_office_terracotta_fins",
        ],
        "reuse_keys": [
            "modern_glass_office_institutional",
            "glass_office_terracotta_fins",
            "Office / Commercial",
        ],
        "identity": (
            "Stepped low-iron office bands alternate with ribbed terracotta fin "
            "fields, two planted setback terraces, a transparent double-height "
            "lobby and an occupied glazed crown."
        ),
        "materials": (
            "low-iron neutral low-e curtain wall; ribbed red terracotta baguettes; "
            "dark bronze mullions; warm occupied offices; planted concrete "
            "terraces; charcoal membrane roof and pergola"
        ),
        "kits": [
            "terracotta_solar_fins",
            "physical_curtain_wall",
            "planted_setbacks",
            "double_height_lobby",
        ],
        "footprint": {
            "recommendedWidth_m": [24, 60],
            "recommendedDepth_m": [18, 40],
            "recommendedFloors": [6, 16],
        },
        "fixed_band": {"scaleMin": 0.82, "scaleMax": 1.18, "maxAxisRatio": 1.16},
        "goalpost": (
            "/archetypes/buildings/modern_glass_office_institutional/variant_1.png"
        ),
    },
    "brutalist-civic-block": {
        "archetype_id": "modernist_civic_block",
        "variant_id": "modernist_civic_concrete_brutalist",
        "generation_archetype_id": "modernist_civic_concrete_brutalist",
        "label": "Modernist Civic Block — Board-Formed Concrete",
        "dimensions": (58.0, 34.0, 20.0),
        "floors": (2, 5, 4),
        "floor_height_m": 4.4,
        "glass_profile": "civic_recessed_smoked",
        "aesthetic_category_id": "modernist_civic",
        "development_type": "institutional",
        "aliases": [
            "modernist_civic_block",
            "modernist_civic_concrete_brutalist",
        ],
        "reuse_keys": [
            "modernist_civic_block",
            "modernist_civic_concrete_brutalist",
            "Civic / Institutional",
        ],
        "identity": (
            "Floating board-formed concrete gallery boxes stand on monumental "
            "pilotis beneath one broad roof plane, cut by deep horizontal window "
            "slits and a recessed civic lobby."
        ),
        "materials": (
            "board-formed exposed concrete; deep smoked low-e ribbon glazing; "
            "charcoal bronze frames; warm public lobby; dark membrane roof; "
            "bush-hammered public plinth"
        ),
        "kits": [
            "floating_concrete_galleries",
            "monumental_pilotis",
            "deep_window_slits",
            "broad_roof_plane",
        ],
        "footprint": {
            "recommendedWidth_m": [36, 70],
            "recommendedDepth_m": [22, 42],
            "recommendedFloors": [2, 5],
        },
        "fixed_band": {"scaleMin": 0.80, "scaleMax": 1.20, "maxAxisRatio": 1.18},
        "goalpost": "/archetypes/buildings/modernist_civic_block/variant_0.png",
    },
}

REFERENCE_UNDERLAYS = {
    "deconstructivist-museum": {
        "path": "textures/source/atrium-underlay-source-v2.png",
        "emission_strength": 0.22,
    },
    "terracotta-fin-office": {
        "path": "textures/source/glazing-underlay-source-v2.png",
        "emission_strength": 0.055,
    },
    "brutalist-civic-block": {
        "path": "textures/source/glazing-underlay-source-v2.png",
        "emission_strength": 0.14,
    },
}

FAST_PILOT_MODE = False


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
    parser.add_argument(
        "--skip-assembled-export",
        action="store_true",
        help=(
            "Render a constructed pilot without replacing its GLB. "
            "Only valid with --skip-modules."
        ),
    )
    parser.add_argument(
        "--modules-only",
        action="store_true",
        help="Reuse the delivered assembled GLB/renders and rebuild only fallback modules plus metadata.",
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


def mesh_object(
    name: str,
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, ...]],
    mat: bpy.types.Material,
    *,
    uv_scale: float = 1.0,
) -> bpy.types.Object:
    """Create an authored mesh with deterministic face-planar UVs."""
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    mesh.materials.append(mat)
    uv = mesh.uv_layers.new(name="UVMap")
    xs = [value[0] for value in vertices]
    ys = [value[1] for value in vertices]
    zs = [value[2] for value in vertices]
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    z0, z1 = min(zs), max(zs)

    def normalized(value: float, low: float, high: float) -> float:
        return 0.0 if abs(high - low) < 1e-6 else (value - low) / (high - low)

    for polygon in mesh.polygons:
        normal = polygon.normal
        for loop_index in polygon.loop_indices:
            vertex = mesh.vertices[mesh.loops[loop_index].vertex_index].co
            if abs(normal.z) > max(abs(normal.x), abs(normal.y)):
                value = (
                    normalized(vertex.x, x0, x1),
                    normalized(vertex.y, y0, y1),
                )
            elif abs(normal.x) > abs(normal.y):
                value = (
                    normalized(vertex.y, y0, y1),
                    normalized(vertex.z, z0, z1),
                )
            else:
                value = (
                    normalized(vertex.x, x0, x1),
                    normalized(vertex.z, z0, z1),
                )
            uv.data[loop_index].uv = (
                value[0] * uv_scale,
                value[1] * uv_scale,
            )
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def mapped_reference_panel(
    name: str,
    points: tuple[
        tuple[float, float, float],
        tuple[float, float, float],
        tuple[float, float, float],
        tuple[float, float, float],
    ],
    mat: bpy.types.Material,
    *,
    model_x_bounds: tuple[float, float],
    model_z_bounds: tuple[float, float],
    source_uv_bounds: tuple[float, float, float, float],
) -> bpy.types.Object:
    """Project one render-locked source over authored facade coordinates."""
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(list(points), [], [(0, 1, 2, 3)])
    mesh.update()
    mesh.materials.append(mat)
    uv = mesh.uv_layers.new(name="UVMap")
    x0, x1 = model_x_bounds
    z0, z1 = model_z_bounds
    u0, v0, u1, v1 = source_uv_bounds

    def project(value: float, low: float, high: float, out0: float, out1: float) -> float:
        if abs(high - low) < 1e-6:
            return out0
        return out0 + (value - low) / (high - low) * (out1 - out0)

    for polygon in mesh.polygons:
        for loop_index in polygon.loop_indices:
            vertex = mesh.vertices[mesh.loops[loop_index].vertex_index].co
            uv.data[loop_index].uv = (
                project(vertex.x, x0, x1, u0, u1),
                project(vertex.z, z0, z1, v0, v1),
            )
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def reference_image_material(
    name: str,
    folder: Path,
    relative_path: str,
    *,
    emission_strength: float,
) -> bpy.types.Material:
    """Keep an authored occupied-depth plate legible behind physical glazing."""
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    texture = nodes.new("ShaderNodeTexImage")
    texture.name = texture.label = "REFERENCE_LOCKED_INTERIOR_UNDERLAY"
    texture.image = bpy.data.images.load(
        str(folder / relative_path),
        check_existing=True,
    )
    texture.extension = "CLIP"
    grade = nodes.new("ShaderNodeHueSaturation")
    grade.name = grade.label = "REFERENCE_UNDERLAY_GRADE"
    grade.inputs["Saturation"].default_value = 0.94
    grade.inputs["Value"].default_value = 0.82
    links.new(texture.outputs["Color"], grade.inputs["Color"])
    links.new(grade.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = 0.78
    if bsdf.inputs.get("Emission Color"):
        links.new(grade.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    mat["skin_zone"] = "reference_underlay"
    mat["reference_locked"] = True
    mat["source"] = relative_path
    mat["underlay_role"] = "occupied_depth_behind_physical_glazing"
    return mat


def tapered_prism(
    name: str,
    *,
    bottom_center: tuple[float, float],
    top_center: tuple[float, float],
    bottom_size: tuple[float, float],
    top_size: tuple[float, float],
    z0: float,
    z1: float,
    mat: bpy.types.Material,
) -> bpy.types.Object:
    bx, by = bottom_center
    tx, ty = top_center
    bw, bd = bottom_size
    tw, td = top_size
    vertices = [
        (bx - bw / 2, by - bd / 2, z0),
        (bx + bw / 2, by - bd / 2, z0),
        (bx + bw / 2, by + bd / 2, z0),
        (bx - bw / 2, by + bd / 2, z0),
        (tx - tw / 2, ty - td / 2, z1),
        (tx + tw / 2, ty - td / 2, z1),
        (tx + tw / 2, ty + td / 2, z1),
        (tx - tw / 2, ty + td / 2, z1),
    ]
    faces = [
        (0, 3, 2, 1),
        (4, 5, 6, 7),
        (0, 1, 5, 4),
        (1, 2, 6, 5),
        (2, 3, 7, 6),
        (3, 0, 4, 7),
    ]
    return mesh_object(name, vertices, faces, mat, uv_scale=3.0)


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
    return mesh_object(name, list(points), [(0, 1, 2, 3)], mat)


def rectangular_beam(
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    thickness: float,
    mat: bpy.types.Material,
    depth: float | None = None,
) -> bpy.types.Object:
    a, b = Vector(start), Vector(end)
    delta = b - a
    midpoint = (a + b) * 0.5
    bpy.ops.mesh.primitive_cube_add(size=1, location=midpoint)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = (thickness, depth or thickness, delta.length)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(
        delta.normalized()
    )
    obj.data.materials.append(mat)
    return obj


def join_mesh_group(
    objects: list[bpy.types.Object],
    predicate: Callable[[bpy.types.Object], bool],
    joined_name: str,
) -> list[bpy.types.Object]:
    """Join one same-material detail system to keep runtime draw calls bounded."""
    members = [
        obj
        for obj in objects
        if obj.type == "MESH" and not obj.modifiers and predicate(obj)
    ]
    if len(members) < 2:
        return objects
    member_ids = {id(obj) for obj in members}
    survivors = [obj for obj in objects if id(obj) not in member_ids]
    bpy.ops.object.select_all(action="DESELECT")
    for obj in members:
        obj.select_set(True)
    active = members[0]
    bpy.context.view_layer.objects.active = active
    bpy.ops.object.join()
    active.name = joined_name
    survivors.append(active)
    return survivors


def optimize_fixed_objects(
    family: str,
    objects: list[bpy.types.Object],
) -> list[bpy.types.Object]:
    """Merge disconnected panes/details without flattening semantic masses."""
    if FAST_PILOT_MODE:
        return objects
    protected = {
        "deconstructivist-museum": {
            "MUSEUM_Atrium_Pane_0_0",
            "MUSEUM_EntryGlazing_Pane_0_0",
        },
        "terracotta-fin-office": {"OFFICE_Lobby_Pane_0_0"},
        "brutalist-civic-block": {
            "CIVIC_LeftGallery_RecessedSlit_Pane_0_0",
            "CIVIC_RecessedLobby_Pane_0_0",
        },
    }[family]
    prefix = {
        "deconstructivist-museum": "MUSEUM_",
        "terracotta-fin-office": "OFFICE_",
        "brutalist-civic-block": "CIVIC_",
    }[family]

    objects = join_mesh_group(
        objects,
        lambda obj: (
            obj.name.startswith(prefix)
            and "_Pane_" in obj.name
            and obj.name not in protected
        ),
        prefix + "PhysicalGlazingSystem",
    )
    objects = join_mesh_group(
        objects,
        lambda obj: (
            obj.name.startswith(prefix)
            and ("_Mullion_" in obj.name or "_Transom_" in obj.name)
        ),
        prefix + "CurtainWallFrameSystem",
    )
    if family == "deconstructivist-museum":
        objects = join_mesh_group(
            objects,
            lambda obj: (
                obj.name.startswith("MUSEUM_")
                and (
                    "VerticalJoint" in obj.name
                    or "ReturnJoint" in obj.name
                    or "PanelJoint" in obj.name
                )
            ),
            "MUSEUM_TitaniumPanelJointSystem",
        )
    elif family == "brutalist-civic-block":
        objects = join_mesh_group(
            objects,
            lambda obj: obj.name.startswith("CIVIC_") and "FormTie" in obj.name,
            "CIVIC_BoardFormTieSystem",
        )
    return objects


def triangular_prism(
    name: str,
    *,
    x0: float,
    x1: float,
    y0: float,
    y1: float,
    base_z: float,
    peak_x: float,
    peak_z: float,
    mat: bpy.types.Material,
) -> bpy.types.Object:
    vertices = [
        (x0, y0, base_z),
        (x1, y0, base_z),
        (peak_x, y0, peak_z),
        (x0, y1, base_z),
        (x1, y1, base_z),
        (peak_x, y1, peak_z),
    ]
    faces = [
        (0, 1, 2),
        (5, 4, 3),
        (0, 3, 4, 1),
        (1, 4, 5, 2),
        (2, 5, 3, 0),
    ]
    return mesh_object(name, vertices, faces, mat, uv_scale=0.6)


def facade_grid(
    prefix: str,
    *,
    bottom_left: tuple[float, float, float],
    bottom_right: tuple[float, float, float],
    top_right: tuple[float, float, float],
    top_left: tuple[float, float, float],
    columns: int,
    rows: int,
    glass: bpy.types.Material,
    frame: bpy.types.Material,
    frame_width: float,
) -> list[bpy.types.Object]:
    """Construct separate physical panes and rectangular mullions on a quad."""
    bl, br, tr, tl = map(Vector, (bottom_left, bottom_right, top_right, top_left))
    objects: list[bpy.types.Object] = []

    def point(u: float, v: float) -> Vector:
        bottom = bl.lerp(br, u)
        top = tl.lerp(tr, u)
        return bottom.lerp(top, v)

    inset_u = 0.006
    inset_v = 0.008
    for row in range(rows):
        for column in range(columns):
            u0 = column / columns + inset_u
            u1 = (column + 1) / columns - inset_u
            v0 = row / rows + inset_v
            v1 = (row + 1) / rows - inset_v
            objects.append(
                quad_panel(
                    f"{prefix}_Pane_{row}_{column}",
                    tuple(
                        tuple(value)
                        for value in (
                            point(u0, v0),
                            point(u1, v0),
                            point(u1, v1),
                            point(u0, v1),
                        )
                    ),
                    glass,
                )
            )
    for column in range(columns + 1):
        u = column / columns
        objects.append(
            rectangular_beam(
                f"{prefix}_Mullion_{column}",
                tuple(point(u, 0.0)),
                tuple(point(u, 1.0)),
                frame_width,
                frame,
                depth=frame_width * 0.70,
            )
        )
    for row in range(rows + 1):
        v = row / rows
        objects.append(
            rectangular_beam(
                f"{prefix}_Transom_{row}",
                tuple(point(0.0, v)),
                tuple(point(1.0, v)),
                frame_width,
                frame,
                depth=frame_width * 0.70,
            )
        )
    return objects


def load_palette(
    family: str,
    folder: Path,
) -> tuple[dict[str, bpy.types.Material], dict]:
    skin = json.loads(
        (folder / "textures" / "skin_manifest.json").read_text(encoding="utf-8")
    )
    near = {zone: values["near"] for zone, values in skin["zones"].items()}
    cfg = FAMILIES[family]
    prefix = family.replace("-", "_").upper()
    shell_grade = {
        "deconstructivist-museum": (0.92, 1.04),
        "terracotta-fin-office": (1.16, 1.16),
        "brutalist-civic-block": (0.96, 0.92),
    }[family]
    mats = {
        "shell": pbr_material(
            f"MAT_W6_{prefix}_ReferenceShell",
            folder,
            near["shell"],
            "shell",
            metallic=0.58 if family == "deconstructivist-museum" else 0.0,
            saturation=shell_grade[0],
            value=shell_grade[1],
        ),
        "facade": pbr_material(
            f"MAT_W6_{prefix}_RegisteredFacade",
            folder,
            near["facade"],
            "facade",
            value=1.02,
        ),
        "side": pbr_material(
            f"MAT_W6_{prefix}_SideConstruction",
            folder,
            near["side"],
            "side",
            metallic=0.52 if family == "deconstructivist-museum" else 0.0,
            saturation=shell_grade[0],
            value=shell_grade[1] - 0.06,
        ),
        "roof": pbr_material(
            f"MAT_W6_{prefix}_Roof",
            folder,
            near["roof"],
            "roof",
            metallic=0.08,
            value=0.78,
        ),
        "trim": pbr_material(
            f"MAT_W6_{prefix}_Trim",
            folder,
            near["trim"],
            "trim",
            metallic=0.18,
            value=0.92,
        ),
        "metal": pbr_material(
            f"MAT_W6_{prefix}_Metal",
            folder,
            near["metal"],
            "metal",
            metallic=0.72,
            value=0.72,
        ),
        "interior": pbr_material(
            f"MAT_W6_{prefix}_OccupiedInterior",
            folder,
            near["interior"],
            "interior",
            emission_strength=0.08,
            value=0.52,
        ),
        "planting": pbr_material(
            f"MAT_W6_{prefix}_Planting",
            folder,
            near["planting"],
            "planting",
            value=0.68,
        ),
        "glass": profiled_glass_material(
            f"MAT_W6_{prefix}_PhysicalGlass",
            cfg["glass_profile"],
        ),
        "timber": material(
            f"MAT_W6_{prefix}_PlantTrunk",
            (0.12, 0.070, 0.032, 1.0),
            0.86,
        ),
        "underlay": reference_image_material(
            f"MAT_W6_{prefix}_ReferenceInteriorUnderlay",
            folder,
            REFERENCE_UNDERLAYS[family]["path"],
            emission_strength=REFERENCE_UNDERLAYS[family]["emission_strength"],
        ),
    }
    occupied_specs = {
        "deconstructivist-museum": (
            (0.060, 0.028, 0.012, 1.0),
            (0.62, 0.28, 0.080, 1.0),
            0.16,
        ),
        "terracotta-fin-office": (
            (0.048, 0.031, 0.018, 1.0),
            (0.38, 0.20, 0.090, 1.0),
            0.06,
        ),
        "brutalist-civic-block": (
            (0.045, 0.028, 0.015, 1.0),
            (0.36, 0.19, 0.080, 1.0),
            0.08,
        ),
    }
    occupied_colour, occupied_emission, occupied_strength = occupied_specs[family]
    mats["interior"] = material(
        f"MAT_W6_{prefix}_OccupiedDepth",
        occupied_colour,
        0.78,
        emission=occupied_emission,
        emission_strength=occupied_strength,
    )
    mats["glass"]["glazing_lod"] = "always"
    mats["glass"]["reference_locked"] = True
    mats["interior"]["glazing_profile"] = cfg["glass_profile"]
    mats["interior"]["environment_intensity"] = 0.20
    return mats, skin


def museum_fixed(m: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = [
        box(
            "MUSEUM_PublicPlinth",
            (69.0, 40.7, 0.45),
            (0, 0, 0.225),
            m["trim"],
            0.08,
        )
    ]
    tower_specs = [
        ("OuterLeft", (-28.0, 0.5), (-27.3, 1.2), (11.5, 34.0), (10.0, 29.0), 0.45, 25.5),
        ("MainLeft", (-11.5, 0.5), (-12.2, 2.0), (20.0, 38.0), (18.0, 31.5), 0.45, 33.1),
        ("Right", (26.0, 1.0), (26.5, 2.0), (18.0, 34.0), (18.0, 29.0), 0.45, 24.0),
    ]
    for name, bottom, top, bsize, tsize, z0, z1 in tower_specs:
        objects.append(
            tapered_prism(
                f"MUSEUM_{name}GalleryMass",
                bottom_center=bottom,
                top_center=top,
                bottom_size=bsize,
                top_size=tsize,
                z0=z0,
                z1=z1,
                mat=m["shell"],
            )
        )
        # The material sample supplies true-scale metal response; this thin
        # coordinate-registered layer supplies the exact panel-tone cadence
        # from the approved elevation instead of discarding that source.
        objects.append(
            mapped_reference_panel(
                f"MUSEUM_{name}RenderLockedFrontSkin",
                (
                    (
                        bottom[0] - bsize[0] / 2,
                        bottom[1] - bsize[1] / 2 - 0.045,
                        z0,
                    ),
                    (
                        bottom[0] + bsize[0] / 2,
                        bottom[1] - bsize[1] / 2 - 0.045,
                        z0,
                    ),
                    (
                        top[0] + tsize[0] / 2,
                        top[1] - tsize[1] / 2 - 0.045,
                        z1,
                    ),
                    (
                        top[0] - tsize[0] / 2,
                        top[1] - tsize[1] / 2 - 0.045,
                        z1,
                    ),
                ),
                m["facade"],
                model_x_bounds=(-35.0, 35.0),
                model_z_bounds=(0.45, 34.0),
                source_uv_bounds=(0.0, 0.0, 1.0, 1.0),
            )
        )
        # Horizontal rainscreen joints are real shadow-casting reveals, not a
        # baked stripe. Their placement follows each leaning public face.
        for index, z in enumerate(
            [value for value in frange(z0 + 1.25, z1 - 0.35, 1.25)]
        ):
            fraction = (z - z0) / (z1 - z0)
            centre_x = bottom[0] + (top[0] - bottom[0]) * fraction
            centre_y = bottom[1] + (top[1] - bottom[1]) * fraction
            width = bsize[0] + (tsize[0] - bsize[0]) * fraction
            depth = bsize[1] + (tsize[1] - bsize[1]) * fraction
            objects.append(
                box(
                    f"MUSEUM_{name}PanelJoint_{index}",
                    (width * 0.985, 0.055, 0.038),
                    (centre_x, centre_y - depth / 2 - 0.030, z),
                    m["metal"],
                )
            )
            panel_span = 2.35
            seam_x = (
                centre_x
                - width / 2
                + panel_span * (0.55 if index % 2 else 1.0)
            )
            seam_index = 0
            while seam_x < centre_x + width / 2 - 0.45:
                for face, seam_y in (
                    ("Front", centre_y - depth / 2 - 0.032),
                    ("Rear", centre_y + depth / 2 + 0.032),
                ):
                    objects.append(
                        box(
                            f"MUSEUM_{name}{face}VerticalJoint_{index}_{seam_index}",
                            (0.032, 0.052, 1.10),
                            (seam_x, seam_y, z - 0.59),
                            m["metal"],
                        )
                    )
                seam_x += panel_span
                seam_index += 1
            side_seam_y = (
                centre_y
                - depth / 2
                + 2.8 * (0.55 if index % 2 else 1.0)
            )
            side_seam_index = 0
            while side_seam_y < centre_y + depth / 2 - 0.55:
                for face, seam_side_x in (
                    ("Left", centre_x - width / 2 - 0.032),
                    ("Right", centre_x + width / 2 + 0.032),
                ):
                    objects.append(
                        box(
                            f"MUSEUM_{name}{face}ReturnJoint_{index}_{side_seam_index}",
                            (0.052, 0.032, 1.10),
                            (seam_side_x, side_seam_y, z - 0.59),
                            m["metal"],
                        )
                    )
                side_seam_y += 2.8
                side_seam_index += 1

    # The left gallery is visibly assembled from colliding volumes.  Its deep
    # angular notches are open air beneath projected gallery boxes.
    objects.extend(
        [
            tapered_prism(
                "MUSEUM_LeftCantileverUpper",
                bottom_center=(-23.5, -3.0),
                top_center=(-22.0, -4.0),
                bottom_size=(24.0, 22.0),
                top_size=(23.0, 20.0),
                z0=17.8,
                z1=24.2,
                mat=m["shell"],
            ),
            tapered_prism(
                "MUSEUM_LeftCantileverLower",
                bottom_center=(-27.0, -5.2),
                top_center=(-26.0, -5.8),
                bottom_size=(15.0, 16.0),
                top_size=(17.0, 15.0),
                z0=10.0,
                z1=15.0,
                mat=m["shell"],
            ),
            triangular_prism(
                "MUSEUM_LeftNotchSoffit",
                x0=-34.0,
                x1=-19.0,
                y0=-13.92,
                y1=-11.8,
                base_z=10.1,
                peak_x=-26.0,
                peak_z=14.2,
                mat=m["metal"],
            ),
        ]
    )
    objects.extend(
        [
            mapped_reference_panel(
                "MUSEUM_LeftCantileverUpperRenderLockedFrontSkin",
                (
                    (-35.5, -14.045, 17.8),
                    (-11.5, -14.045, 17.8),
                    (-10.5, -14.045, 24.2),
                    (-33.5, -14.045, 24.2),
                ),
                m["facade"],
                model_x_bounds=(-35.0, 35.0),
                model_z_bounds=(0.45, 34.0),
                source_uv_bounds=(0.0, 0.0, 1.0, 1.0),
            ),
            mapped_reference_panel(
                "MUSEUM_LeftCantileverLowerRenderLockedFrontSkin",
                (
                    (-34.5, -13.245, 10.0),
                    (-19.5, -13.245, 10.0),
                    (-17.5, -13.345, 15.0),
                    (-34.5, -13.345, 15.0),
                ),
                m["facade"],
                model_x_bounds=(-35.0, 35.0),
                model_z_bounds=(0.45, 34.0),
                source_uv_bounds=(0.0, 0.0, 1.0, 1.0),
            ),
        ]
    )

    # Main atrium: separate panes, structural frame and occupied plates.  The
    # top widens while the facade leans inward, matching the locked elevation.
    atrium_bl = (-1.5, -19.05, 7.1)
    atrium_br = (13.7, -19.05, 7.1)
    atrium_tr = (18.0, -15.20, 29.7)
    atrium_tl = (-2.2, -15.20, 29.7)
    objects.append(
        mapped_reference_panel(
            "MUSEUM_RenderLockedAtriumInteriorUnderlay",
            (
                (atrium_bl[0], atrium_bl[1] + 1.15, atrium_bl[2]),
                (atrium_br[0], atrium_br[1] + 1.15, atrium_br[2]),
                (atrium_tr[0], atrium_tr[1] + 1.15, atrium_tr[2]),
                (atrium_tl[0], atrium_tl[1] + 1.15, atrium_tl[2]),
            ),
            m["underlay"],
            model_x_bounds=(-2.2, 18.0),
            model_z_bounds=(7.1, 29.7),
            source_uv_bounds=(0.36, 0.24, 0.75, 0.95),
        )
    )
    objects.extend(
        facade_grid(
            "MUSEUM_Atrium",
            bottom_left=atrium_bl,
            bottom_right=atrium_br,
            top_right=atrium_tr,
            top_left=atrium_tl,
            columns=7,
            rows=6,
            glass=m["glass"],
            frame=m["metal"],
            frame_width=0.20,
        )
    )
    # Side and roof facets complete the atrium as an enclosed piece of
    # architecture; the public floor plates remain behind glass in obliques.
    atrium_rear_left_bottom = (-0.2, -1.4, 7.1)
    atrium_rear_right_bottom = (15.0, -1.0, 7.1)
    atrium_rear_left_top = (-4.5, 0.8, 29.7)
    atrium_rear_right_top = (16.0, 0.8, 29.7)
    objects.extend(
        facade_grid(
            "MUSEUM_AtriumLeftReturn",
            bottom_left=atrium_bl,
            bottom_right=atrium_rear_left_bottom,
            top_right=atrium_rear_left_top,
            top_left=atrium_tl,
            columns=4,
            rows=6,
            glass=m["glass"],
            frame=m["metal"],
            frame_width=0.16,
        )
    )
    objects.extend(
        facade_grid(
            "MUSEUM_AtriumRightReturn",
            bottom_left=atrium_br,
            bottom_right=atrium_rear_right_bottom,
            top_right=atrium_rear_right_top,
            top_left=atrium_tr,
            columns=4,
            rows=6,
            glass=m["glass"],
            frame=m["metal"],
            frame_width=0.16,
        )
    )
    objects.append(
        quad_panel(
            "MUSEUM_AtriumGlassRoof",
            (
                atrium_tl,
                atrium_tr,
                atrium_rear_right_top,
                atrium_rear_left_top,
            ),
            m["glass"],
        )
    )
    for index, z in enumerate((8.0, 12.2, 16.4, 20.6, 24.8, 28.9)):
        fraction = (z - atrium_bl[2]) / (atrium_tl[2] - atrium_bl[2])
        x_left = atrium_bl[0] + (atrium_tl[0] - atrium_bl[0]) * fraction
        x_right = atrium_br[0] + (atrium_tr[0] - atrium_br[0]) * fraction
        front_y = atrium_bl[1] + (atrium_tl[1] - atrium_bl[1]) * fraction
        objects.append(
            box(
                f"MUSEUM_AtriumFloorPlate_{index}",
                (x_right - x_left - 0.5, 15.5, 0.28),
                ((x_left + x_right) / 2, front_y + 7.9, z),
                m["metal"],
                0.05,
            )
        )
        if z < 28.0:
            objects.append(
                box(
                    f"MUSEUM_AtriumOccupiedRoom_{index}",
                    (x_right - x_left - 2.0, 0.18, 1.55),
                    ((x_left + x_right) / 2, front_y + 1.45, z + 0.92),
                    m["interior"],
                )
            )
    # Diagonal atrium bracing remains subordinate to the orthogonal mullions.
    objects.extend(
        [
            rectangular_beam(
                "MUSEUM_AtriumBraceA",
                (-1.2, -18.7, 8.0),
                (16.3, -15.1, 28.7),
                0.16,
                m["metal"],
            ),
            rectangular_beam(
                "MUSEUM_AtriumBraceB",
                (12.9, -18.7, 8.0),
                (0.0, -15.1, 27.0),
                0.14,
                m["metal"],
            ),
        ]
    )

    # The entrance is a true void under the atrium, with a triangular canopy
    # and load-bearing wedge rather than a window painted on a solid wall.
    objects.extend(
        facade_grid(
            "MUSEUM_EntryGlazing",
            bottom_left=(-1.2, -19.35, 0.50),
            bottom_right=(13.8, -19.35, 0.50),
            top_right=(13.8, -19.35, 6.65),
            top_left=(-1.2, -19.35, 6.65),
            columns=5,
            rows=2,
            glass=m["glass"],
            frame=m["metal"],
            frame_width=0.14,
        )
    )
    objects.append(
        mapped_reference_panel(
            "MUSEUM_RenderLockedEntryInteriorUnderlay",
            (
                (-1.2, -18.05, 0.50),
                (13.8, -18.05, 0.50),
                (13.8, -18.05, 6.65),
                (-1.2, -18.05, 6.65),
            ),
            m["underlay"],
            model_x_bounds=(-1.2, 13.8),
            model_z_bounds=(0.50, 6.65),
            source_uv_bounds=(0.37, 0.07, 0.72, 0.25),
        )
    )
    objects.extend(
        [
            triangular_prism(
                "MUSEUM_EntryCanopy",
                x0=-3.0,
                x1=14.5,
                y0=-20.5,
                y1=-18.4,
                base_z=6.2,
                peak_x=7.5,
                peak_z=7.3,
                mat=m["side"],
            ),
            triangular_prism(
                "MUSEUM_EntryStructuralWedge",
                x0=11.2,
                x1=16.0,
                y0=-19.0,
                y1=-12.5,
                base_z=0.45,
                peak_x=14.1,
                peak_z=7.0,
                mat=m["metal"],
            ),
        ]
    )

    # Serrated parapets are physical, irregular metal crests.
    for prefix, left, right, y_front, top_z, count in (
        ("Main", -21.1, -3.2, -13.8, 33.1, 8),
        ("Right", 23.3, 34.8, -12.4, 24.0, 5),
    ):
        spacing = (right - left) / count
        for index in range(count):
            x0 = left + index * spacing
            x1 = x0 + spacing * 0.82
            peak = x0 + spacing * (0.35 if index % 2 else 0.58)
            objects.append(
                triangular_prism(
                    f"MUSEUM_{prefix}ParapetTooth_{index}",
                    x0=x0,
                    x1=x1,
                    y0=y_front,
                    y1=y_front + 1.0,
                    base_z=top_z,
                    peak_x=peak,
                    peak_z=min(34.0, top_z + 0.9 + 0.20 * (index % 3)),
                    mat=m["shell"],
                )
            )

    # Conservative rear and roof equipment preserve the landmark from aerials.
    objects.extend(
        [
            box("MUSEUM_MainRoof", (15.0, 25.5, 0.24), (-12.2, 3.5, 33.08), m["roof"]),
            box("MUSEUM_OuterRoof", (8.0, 23.0, 0.22), (-27.3, 3.0, 25.46), m["roof"]),
            box("MUSEUM_RightRoof", (9.0, 22.0, 0.22), (29.0, 3.5, 23.96), m["roof"]),
            box("MUSEUM_RoofServiceScreen", (6.0, 3.0, 1.2), (-12.0, 5.0, 32.7), m["metal"], 0.08),
        ]
    )
    return optimize_fixed_objects("deconstructivist-museum", objects)


def office_fixed(m: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = [
        box("OFFICE_PublicPlinth", (41.5, 27.5, 0.35), (0, 0, 0.175), m["trim"], 0.06)
    ]
    # Stacked floor plates and room cards make the clear facade read as glass,
    # not blue paint.
    plate_specs = [
        (0.35, 42.0, 28.0, 0.0),
        (4.2, 42.0, 28.0, 0.0),
        (8.0, 42.0, 28.0, 0.0),
        (11.8, 42.0, 28.0, 0.0),
        (15.6, 38.0, 25.0, 1.2),
        (19.4, 38.0, 25.0, 1.2),
        (23.2, 38.0, 25.0, 1.2),
        (27.0, 40.0, 24.0, 1.8),
        (31.2, 40.0, 24.0, 1.8),
    ]
    for index, (z, width, depth, y) in enumerate(plate_specs):
        objects.append(
            box(
                f"OFFICE_FloorPlate_{index}",
                (width, depth, 0.28),
                (0, y, z),
                m["trim"],
                0.04,
            )
        )
    facade_bands = [
        ("Lobby", -14.10, 0.45, 7.85, 42.0, 9, 2),
        ("Lower", -14.10, 8.05, 15.40, 42.0, 12, 2),
        ("Middle", -11.35, 15.75, 26.75, 38.0, 11, 3),
        ("Crown", -10.35, 27.05, 31.15, 40.0, 12, 1),
    ]
    for label, y, z0, z1, width, columns, rows in facade_bands:
        objects.extend(
            facade_grid(
                f"OFFICE_{label}",
                bottom_left=(-width / 2, y, z0),
                bottom_right=(width / 2, y, z0),
                top_right=(width / 2, y, z1),
                top_left=(-width / 2, y, z1),
                columns=columns,
                rows=rows,
                glass=m["glass"],
                frame=m["metal"],
                frame_width=0.095,
            )
        )
        for floor in range(max(1, rows)):
            objects.append(
                box(
                    f"OFFICE_{label}Occupied_{floor}",
                    (width - 2.0, 0.18, (z1 - z0) / rows - 0.8),
                    (
                        0,
                        y + 0.9,
                        z0 + (floor + 0.5) * (z1 - z0) / rows,
                    ),
                    m["interior"],
                )
            )
        objects.append(
            mapped_reference_panel(
                f"OFFICE_{label}RenderLockedInteriorUnderlay",
                (
                    (-width / 2, y + 0.72, z0),
                    (width / 2, y + 0.72, z0),
                    (width / 2, y + 0.72, z1),
                    (-width / 2, y + 0.72, z1),
                ),
                m["underlay"],
                model_x_bounds=(-21.0, 21.0),
                model_z_bounds=(0.45, 31.15),
                source_uv_bounds=(0.05, 0.12, 0.91, 0.825),
            )
        )

    # Terracotta baguettes occur only on the two reference-locked fin fields.
    for band_index, (y, z0, z1, width, phase) in enumerate(
        [
            (-14.35, 8.15, 11.65, 42.0, 0.0),
            (-11.60, 15.85, 23.10, 38.0, 0.45),
        ]
    ):
        index = 0
        bay_count = max(6, round(width / 4.65))
        bay_width = width / bay_count
        for bay in range(bay_count):
            # The upper screen has one planted outdoor room near the right,
            # visible in both the catalogue card and completed oblique.
            if band_index == 1 and bay == bay_count - 2:
                continue
            bay_left = -width / 2 + bay * bay_width
            for slot, fraction in enumerate(
                (0.09, 0.17, 0.25, 0.34, 0.76, 0.84)
            ):
                x = bay_left + bay_width * fraction
                x += phase * (0.08 if (bay + slot) % 2 else -0.05)
                fin_depth = 1.12 if slot == 0 and bay % 2 == 0 else 0.82
                objects.append(
                    box(
                        f"OFFICE_TerracottaFin_{band_index}_{index}",
                        (0.17, fin_depth, z1 - z0),
                        (x, y - fin_depth / 2, (z0 + z1) / 2),
                        m["shell"],
                        0.035,
                    )
                )
                index += 1
        objects.extend(
            [
                box(
                    f"OFFICE_FinRailLower_{band_index}",
                    (width, 0.25, 0.28),
                    (0, y - 0.22, z0),
                    m["shell"],
                    0.03,
                ),
                box(
                    f"OFFICE_FinRailUpper_{band_index}",
                    (width, 0.25, 0.28),
                    (0, y - 0.22, z1),
                    m["shell"],
                    0.03,
                ),
            ]
        )

    # Every band closes around both returns and the rear so floor plates remain
    # inside the weather envelope in front-, rear- and roof-corner views.
    return_bands = [
        ("Lobby", 21.0, -13.95, 13.95, 0.45, 7.85, 2),
        ("Lower", 21.0, -13.95, 13.95, 8.05, 15.40, 2),
        ("Middle", 19.0, -11.25, 13.65, 15.75, 26.75, 3),
        ("Crown", 20.0, -10.25, 13.75, 27.05, 31.15, 1),
    ]
    for label, half_width, front_y, rear_y, z0, z1, rows in return_bands:
        for side in (-1, 1):
            x = side * (half_width + 0.03)
            objects.extend(
                facade_grid(
                    f"OFFICE_{label}Return_{side}",
                    bottom_left=(x, front_y, z0),
                    bottom_right=(x, rear_y, z0),
                    top_right=(x, rear_y, z1),
                    top_left=(x, front_y, z1),
                    columns=max(6, round((rear_y - front_y) / 3.0)),
                    rows=rows,
                    glass=m["glass"],
                    frame=m["metal"],
                    frame_width=0.09,
                )
            )
        objects.extend(
            facade_grid(
                f"OFFICE_{label}Rear",
                bottom_left=(half_width, rear_y + 0.03, z0),
                bottom_right=(-half_width, rear_y + 0.03, z0),
                top_right=(-half_width, rear_y + 0.03, z1),
                top_left=(half_width, rear_y + 0.03, z1),
                columns=max(8, round(half_width * 2 / 3.3)),
                rows=rows,
                glass=m["glass"],
                frame=m["metal"],
                frame_width=0.09,
            )
        )

    # Terracotta fins wrap the two selected solar-screen bands around both
    # returns instead of ending as a hero-facing stage set.
    for band_index, (half_width, y0, y1, z0, z1) in enumerate(
        [
            (21.0, -13.6, 13.6, 8.15, 11.65),
            (19.0, -10.9, 13.3, 15.85, 23.10),
        ]
    ):
        for side in (-1, 1):
            for index, y in enumerate(frange(y0 + 0.7, y1 - 0.4, 1.32)):
                objects.append(
                    box(
                        f"OFFICE_ReturnTerracottaFin_{band_index}_{side}_{index}",
                        (0.78, 0.22, z1 - z0),
                        (side * (half_width + 0.36), y, (z0 + z1) / 2),
                        m["shell"],
                        0.035,
                    )
                )

    # Tall fired-clay lobby piers give the transparent ground floor a real
    # structural rhythm rather than an undifferentiated glass card.
    for index, x in enumerate(frange(-19.5, 20.0, 5.65)):
        objects.append(
            box(
                f"OFFICE_LobbyTerracottaPier_{index}",
                (0.58, 1.05, 7.45),
                (x, -14.45, 4.18),
                m["shell"],
                0.045,
            )
        )

    # Two deep planted terraces and a planted crown, visible in all obliques.
    terrace_specs = [
        ("Lower", 15.55, 42.0, 3.2, -12.6),
        ("Upper", 26.95, 39.5, 3.0, -10.8),
        ("Roof", 31.45, 40.0, 2.4, -9.8),
    ]
    for name, z, width, depth, y in terrace_specs:
        objects.extend(
            [
                box(
                    f"OFFICE_{name}TerraceSlab",
                    (width, depth, 0.30),
                    (0, y, z),
                    m["trim"],
                    0.04,
                ),
                box(
                    f"OFFICE_{name}Planter",
                    (width - 1.2, 0.75, 0.65),
                    (0, y - depth / 2 + 0.45, z + 0.42),
                    m["trim"],
                    0.08,
                ),
                box(
                    f"OFFICE_{name}PlantingBed",
                    (width - 1.6, 0.58, 0.28),
                    (0, y - depth / 2 + 0.45, z + 0.78),
                    m["planting"],
                    0.07,
                ),
            ]
        )
        crown_y = y - depth / 2 + 0.45
        if name == "Roof":
            for planter_index, planter_x in enumerate(
                frange(-width / 2 + 2.4, width / 2 - 1.6, 7.0)
            ):
                objects.extend(
                    [
                        cylinder(
                            f"OFFICE_{name}TreeTrunk_{planter_x:.1f}",
                            0.075,
                            0.96,
                            (planter_x, crown_y, z + 1.28),
                            m["timber"],
                            10,
                        ),
                        sphere(
                            f"OFFICE_{name}TreeCrownA_{planter_x:.1f}",
                            0.55,
                            (planter_x - 0.18, crown_y, z + 1.95),
                            m["planting"],
                            (1.15, 0.78, 0.92),
                            16,
                            8,
                        ),
                        sphere(
                            f"OFFICE_{name}TreeCrownB_{planter_x:.1f}",
                            0.48,
                            (
                                planter_x + 0.22,
                                crown_y
                                + (0.10 if planter_index % 2 else -0.08),
                                z + 2.10,
                            ),
                            m["planting"],
                            (0.88, 1.05, 1.18),
                            16,
                            8,
                        ),
                        sphere(
                            f"OFFICE_{name}TreeCrownC_{planter_x:.1f}",
                            0.40,
                            (planter_x + 0.05, crown_y - 0.10, z + 2.38),
                            m["planting"],
                            (0.92, 0.78, 0.92),
                            16,
                            8,
                        ),
                    ]
                )
        else:
            # The references show dense trailing shrubs at the occupied
            # setbacks, not a row of identical topiary lollipops.
            for shrub_index, shrub_x in enumerate(
                frange(-width / 2 + 1.2, width / 2 - 0.8, 1.35)
            ):
                objects.extend(
                    [
                        sphere(
                            f"OFFICE_{name}TrailingShrub_{shrub_index}",
                            0.38,
                            (
                                shrub_x,
                                crown_y - 0.08 * (shrub_index % 3),
                                z + 1.00 + 0.07 * (shrub_index % 2),
                            ),
                            m["planting"],
                            (
                                1.35 + 0.15 * (shrub_index % 2),
                                0.78,
                                0.58 + 0.08 * (shrub_index % 3),
                            ),
                            12,
                            6,
                        ),
                        sphere(
                            f"OFFICE_{name}TrailingShrubAccent_{shrub_index}",
                            0.29,
                            (
                                shrub_x + 0.24,
                                crown_y - 0.18,
                                z + 0.86 + 0.06 * (shrub_index % 3),
                            ),
                            m["planting"],
                            (
                                0.90,
                                0.72,
                                0.72 + 0.08 * (shrub_index % 2),
                            ),
                            10,
                            5,
                        ),
                    ]
                )
    objects.extend(
        [
            box("OFFICE_RearCore", (13.0, 4.0, 27.0), (0, 11.5, 13.85), m["side"], 0.10),
            box("OFFICE_RoofMembrane", (38.5, 22.5, 0.25), (0, 1.8, 31.35), m["roof"]),
            box("OFFICE_RoofPergolaA", (40.5, 0.22, 0.45), (0, -9.0, 31.8), m["shell"], 0.04),
            box("OFFICE_RoofPergolaB", (40.5, 0.22, 0.45), (0, 8.6, 31.8), m["shell"], 0.04),
        ]
    )
    return optimize_fixed_objects("terracotta-fin-office", objects)


def civic_gallery_box(
    prefix: str,
    *,
    centre_x: float,
    width: float,
    depth: float,
    z0: float,
    z1: float,
    front_y: float,
    slit_z0: float,
    slit_z1: float,
    m: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    """Build a concrete gallery around a real recessed horizontal opening."""
    centre_y = front_y + depth / 2
    objects = [
        box(
            f"{prefix}_LowerConcrete",
            (width, depth, slit_z0 - z0),
            (centre_x, centre_y, z0 + (slit_z0 - z0) / 2),
            m["shell"],
            0.06,
        ),
        box(
            f"{prefix}_UpperConcrete",
            (width, depth, z1 - slit_z1),
            (centre_x, centre_y, slit_z1 + (z1 - slit_z1) / 2),
            m["shell"],
            0.06,
        ),
        box(
            f"{prefix}_SlitSoffit",
            (width, 1.25, 0.18),
            (centre_x, front_y + 0.62, slit_z1 + 0.09),
            m["side"],
        ),
        box(
            f"{prefix}_SlitSill",
            (width, 1.25, 0.20),
            (centre_x, front_y + 0.62, slit_z0 - 0.10),
            m["side"],
        ),
    ]
    objects.extend(
        facade_grid(
            f"{prefix}_RecessedSlit",
            bottom_left=(centre_x - width / 2 + 0.55, front_y + 1.10, slit_z0),
            bottom_right=(centre_x + width / 2 - 0.55, front_y + 1.10, slit_z0),
            top_right=(centre_x + width / 2 - 0.55, front_y + 1.10, slit_z1),
            top_left=(centre_x - width / 2 + 0.55, front_y + 1.10, slit_z1),
            columns=max(4, round(width / 3.0)),
            rows=1,
            glass=m["glass"],
            frame=m["metal"],
            frame_width=0.10,
        )
    )
    objects.append(
        mapped_reference_panel(
            f"{prefix}_RenderLockedSlitUnderlay",
            (
                (
                    centre_x - width / 2 + 0.55,
                    front_y + 1.42,
                    slit_z0,
                ),
                (
                    centre_x + width / 2 - 0.55,
                    front_y + 1.42,
                    slit_z0,
                ),
                (
                    centre_x + width / 2 - 0.55,
                    front_y + 1.42,
                    slit_z1,
                ),
                (
                    centre_x - width / 2 + 0.55,
                    front_y + 1.42,
                    slit_z1,
                ),
            ),
            m["underlay"],
            model_x_bounds=(-29.0, 29.0),
            model_z_bounds=(0.50, 18.35),
            source_uv_bounds=(0.06, 0.16, 0.90, 0.75),
        )
    )
    return objects


def civic_fixed(m: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = [
        box("CIVIC_PublicPlinth", (57.5, 33.5, 0.36), (0, 0, 0.18), m["trim"], 0.06)
    ]
    # Monumental columns carry the gallery masses; open air remains between
    # them and the transparent public lobby is set well behind.
    for index, (x, y) in enumerate([(-16.0, -8.8), (19.0, -8.0)]):
        objects.append(
            box(
                f"CIVIC_MonumentalPilotis_{index}",
                (3.8, 3.8, 8.0),
                (x, y, 4.35),
                m["shell"],
                0.18,
            )
        )
    objects.extend(
        facade_grid(
            "CIVIC_RecessedLobby",
            bottom_left=(-12.0, -7.0, 0.55),
            bottom_right=(17.0, -7.0, 0.55),
            top_right=(17.0, -7.0, 7.60),
            top_left=(-12.0, -7.0, 7.60),
            columns=8,
            rows=2,
            glass=m["glass"],
            frame=m["metal"],
            frame_width=0.12,
        )
    )
    objects.append(
        mapped_reference_panel(
            "CIVIC_RenderLockedRecessAndLobbyUnderlay",
            (
                (-12.0, -5.85, 0.55),
                (17.0, -5.85, 0.55),
                (17.0, -5.85, 7.60),
                (-12.0, -5.85, 7.60),
            ),
            m["underlay"],
            model_x_bounds=(-29.0, 29.0),
            model_z_bounds=(0.50, 18.35),
            source_uv_bounds=(0.06, 0.16, 0.90, 0.75),
        )
    )

    # Three gallery boxes retain separate shadow joints and slit locations,
    # producing the reference's offset cantilever hierarchy.
    objects.extend(
        civic_gallery_box(
            "CIVIC_LeftGallery",
            centre_x=-15.0,
            width=24.0,
            depth=27.0,
            z0=7.0,
            z1=16.2,
            front_y=-15.7,
            slit_z0=10.70,
            slit_z1=11.55,
            m=m,
        )
    )
    objects.extend(
        civic_gallery_box(
            "CIVIC_CentreGallery",
            centre_x=3.5,
            width=10.5,
            depth=22.0,
            z0=7.8,
            z1=17.0,
            front_y=-13.9,
            slit_z0=12.45,
            slit_z1=13.30,
            m=m,
        )
    )
    objects.extend(
        civic_gallery_box(
            "CIVIC_RightGallery",
            centre_x=18.5,
            width=17.0,
            depth=24.0,
            z0=8.2,
            z1=15.4,
            front_y=-12.3,
            slit_z0=11.10,
            slit_z1=11.95,
            m=m,
        )
    )
    # Narrow full-height glazing slots keep the three heavy gallery masses
    # visibly separate, as in the reference rather than one long concrete bar.
    for slot_index, (x0, x1, y) in enumerate(
        [(-3.0, -1.75, -13.20), (8.75, 10.0, -11.65)]
    ):
        objects.extend(
            facade_grid(
                f"CIVIC_VerticalAtriumSlot_{slot_index}",
                bottom_left=(x0, y, 8.15),
                bottom_right=(x1, y, 8.15),
                top_right=(x1, y, 16.10),
                top_left=(x0, y, 16.10),
                columns=1,
                rows=3,
                glass=m["glass"],
                frame=m["metal"],
                frame_width=0.10,
            )
        )
        objects.append(
            mapped_reference_panel(
                f"CIVIC_VerticalAtriumSlot_{slot_index}Underlay",
                (
                    (x0, y + 0.42, 8.15),
                    (x1, y + 0.42, 8.15),
                    (x1, y + 0.42, 16.10),
                    (x0, y + 0.42, 16.10),
                ),
                m["underlay"],
                model_x_bounds=(-29.0, 29.0),
                model_z_bounds=(0.50, 18.35),
                source_uv_bounds=(0.06, 0.16, 0.90, 0.75),
            )
        )
    objects.extend(
        [
            box(
                "CIVIC_CarvedEntryCanopy",
                (14.5, 5.5, 0.55),
                (2.5, -10.3, 6.95),
                m["shell"],
                0.05,
            ),
        ]
    )

    # A continuous clerestory shadow separates the heavy galleries from one
    # broad overhanging roof plane.
    objects.extend(
        facade_grid(
            "CIVIC_Clerestory",
            bottom_left=(-25.5, -13.0, 16.15),
            bottom_right=(25.5, -13.0, 16.15),
            top_right=(25.5, -13.0, 18.35),
            top_left=(-25.5, -13.0, 18.35),
            columns=16,
            rows=1,
            glass=m["glass"],
            frame=m["metal"],
            frame_width=0.10,
        )
    )
    objects.append(
        mapped_reference_panel(
            "CIVIC_ClerestoryRenderLockedUnderlay",
            (
                (-25.5, -12.55, 16.15),
                (25.5, -12.55, 16.15),
                (25.5, -12.55, 18.35),
                (-25.5, -12.55, 18.35),
            ),
            m["underlay"],
            model_x_bounds=(-29.0, 29.0),
            model_z_bounds=(0.50, 18.35),
            source_uv_bounds=(0.06, 0.16, 0.90, 0.75),
        )
    )
    objects.extend(
        [
            box("CIVIC_BroadRoofPlane", (58.0, 34.0, 1.05), (0, 0, 19.475), m["shell"], 0.08),
            box("CIVIC_RoofMembrane", (55.5, 31.5, 0.18), (0, 0.5, 19.91), m["roof"]),
            box("CIVIC_RoofServicePenthouse", (16.0, 8.0, 1.15), (6.0, 5.0, 18.55), m["side"], 0.06),
        ]
    )
    # Board-form tie holes remain restrained and stay on their actual staggered
    # gallery faces instead of floating along one imaginary front plane.
    gallery_specs = (
        ("Left", -15.0, 24.0, -15.7, 27.0, 7.0, 16.2),
        ("Centre", 3.5, 10.5, -13.9, 22.0, 7.8, 17.0),
        ("Right", 18.5, 17.0, -12.3, 24.0, 8.2, 15.4),
    )
    for gallery, centre_x, width, front_y, _depth, z0, z1 in gallery_specs:
        for row, z in enumerate((9.2, 11.4, 14.7, 16.0)):
            if z < z0 + 0.35 or z > z1 - 0.20:
                continue
            for column, x in enumerate(
                frange(centre_x - width / 2 + 1.4, centre_x + width / 2, 3.8)
            ):
                objects.append(
                    cylinder(
                        f"CIVIC_{gallery}FrontFormTie_{row}_{column}",
                        0.075,
                        0.05,
                        (x, front_y - 0.04, z),
                        m["metal"],
                        16,
                        (1.0, 1.0),
                    )
                )
                objects[-1].rotation_euler.x = math.pi / 2
    # Continue the restrained tie schedule around returns and rear walls. This
    # supplies real close-range board-form depth without adding facade ornament.
    for gallery, centre_x, width, front_y, depth, _z0, _z1 in gallery_specs:
        rear_y = front_y + depth
        left_x = centre_x - width / 2
        right_x = centre_x + width / 2
        for row, z in enumerate((9.2, 11.4, 14.7, 16.0)):
            for column, x in enumerate(
                frange(left_x + 1.7, right_x - 1.0, 3.3)
            ):
                objects.append(
                    cylinder(
                        f"CIVIC_{gallery}RearFormTie_{row}_{column}",
                        0.055,
                        0.045,
                        (x, rear_y + 0.025, z),
                        m["metal"],
                        18,
                    )
                )
                objects[-1].rotation_euler.x = math.pi / 2
            for side_index, x in enumerate((left_x - 0.025, right_x + 0.025)):
                for column, y in enumerate(
                    frange(front_y + 1.7, rear_y - 1.0, 3.4)
                ):
                    objects.append(
                        cylinder(
                            f"CIVIC_{gallery}SideFormTie_{row}_{side_index}_{column}",
                            0.055,
                            0.045,
                            (x, y, z),
                            m["metal"],
                            18,
                        )
                    )
                    objects[-1].rotation_euler.y = math.pi / 2
    return optimize_fixed_objects("brutalist-civic-block", objects)


def frange(start: float, stop: float, step: float) -> list[float]:
    values: list[float] = []
    value = start
    while value < stop - 1e-6:
        values.append(value)
        value += step
    return values


def fallback_module(
    family: str,
    role: str,
    variant: str,
    height: float,
    m: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    """Conservative family-specific stack used only outside the fixed band."""
    cfg = FAMILIES[family]
    width, depth, _ = cfg["dimensions"]
    objects: list[bpy.types.Object] = []
    inset = 1.3 if role in {"crown", "roof"} else 0.0
    shell = m["shell"]
    if family == "deconstructivist-museum":
        if role == "roof":
            objects.append(box("MUSEUMKIT_Roof", (width - 4, depth - 4, height), (0, 1, height / 2), m["roof"], 0.06))
        else:
            objects.extend(
                [
                    box(
                        f"MUSEUMKIT_{role}_{variant}_Left",
                        (width * 0.38 - inset, depth - 2 - inset, height),
                        (-width * 0.27, 0.8, height / 2),
                        shell,
                        0.08,
                    ),
                    box(
                        f"MUSEUMKIT_{role}_{variant}_Right",
                        (width * 0.25 - inset, depth - 4 - inset, height * 0.92),
                        (width * 0.34, 1.5, height * 0.46),
                        shell,
                        0.08,
                    ),
                ]
            )
            objects.extend(
                facade_grid(
                    f"MUSEUMKIT_{role}_{variant}_Atrium",
                    bottom_left=(-3.0, -depth / 2 + 0.03, 0.15),
                    bottom_right=(12.0, -depth / 2 + 0.03, 0.15),
                    top_right=(13.0, -depth / 2 + 0.48, height - 0.15),
                    top_left=(-4.0, -depth / 2 + 0.48, height - 0.15),
                    columns=5,
                    rows=1,
                    glass=m["glass"],
                    frame=m["metal"],
                    frame_width=0.10,
                )
            )
    elif family == "terracotta-fin-office":
        if role == "roof":
            objects.append(box("OFFICEKIT_Roof", (width - 2, depth - 2, height), (0, 0, height / 2), m["roof"], 0.05))
        else:
            objects.append(box(f"OFFICEKIT_{role}_{variant}_Core", (width - 1 - inset, depth - 2 - inset, height), (0, 0.7, height / 2), m["interior"], 0.04))
            objects.extend(
                facade_grid(
                    f"OFFICEKIT_{role}_{variant}_Glass",
                    bottom_left=(-width / 2 + 0.5, -depth / 2 + 0.04, 0.12),
                    bottom_right=(width / 2 - 0.5, -depth / 2 + 0.04, 0.12),
                    top_right=(width / 2 - 0.5, -depth / 2 + 0.04, height - 0.12),
                    top_left=(-width / 2 + 0.5, -depth / 2 + 0.04, height - 0.12),
                    columns=12,
                    rows=1,
                    glass=m["glass"],
                    frame=m["metal"],
                    frame_width=0.08,
                )
            )
            if role in {"floor", "crown"}:
                for index, x in enumerate(frange(-width / 2 + 0.8, width / 2 - 0.4, 1.2)):
                    objects.append(box(f"OFFICEKIT_Fin_{variant}_{index}", (0.20, 0.72, height - 0.3), (x, -depth / 2 + 0.36, height / 2), shell, 0.025))
    else:
        if role == "roof":
            objects.append(box("CIVICKIT_Roof", (width, depth, height), (0, 0, height / 2), shell, 0.06))
        elif role == "podium":
            for index, x in enumerate((-width * 0.30, 0.0, width * 0.30)):
                objects.append(box(f"CIVICKIT_Piloti_{index}", (3.0, 3.0, height), (x, -depth * 0.25, height / 2), shell, 0.14))
            objects.extend(
                facade_grid(
                    "CIVICKIT_Lobby",
                    bottom_left=(-width / 2 + 2, -depth * 0.12, 0.2),
                    bottom_right=(width / 2 - 2, -depth * 0.12, 0.2),
                    top_right=(width / 2 - 2, -depth * 0.12, height - 0.2),
                    top_left=(-width / 2 + 2, -depth * 0.12, height - 0.2),
                    columns=10,
                    rows=1,
                    glass=m["glass"],
                    frame=m["metal"],
                    frame_width=0.10,
                )
            )
        else:
            objects.append(box(f"CIVICKIT_{role}_{variant}", (width - inset, depth - 2 - inset, height), (0, 0.7, height / 2), shell, 0.06))
            objects.append(box(f"CIVICKIT_{role}_{variant}_Slit", (width - 3 - inset, 0.16, max(0.6, height * 0.20)), (0, -depth / 2 + 0.08, height * 0.58), m["glass"]))
    return objects


def render_views(
    family: str,
    folder: Path,
    *,
    view_set: str,
) -> list[str]:
    cfg = FAMILIES[family]
    width, depth, height = cfg["dimensions"]
    setup_render()
    scene = bpy.context.scene
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 900
    # Width-only framing clips tall office families in a landscape viewport.
    # Expand the camera radius only when the height requires more vertical FOV.
    vertical_fit = max(1.0, height * (1280 / 900) / width)
    distance = max(width, depth) * vertical_fit
    if family == "terracotta-fin-office":
        # The rooftop planting/pergola and the double-height lobby extend beyond
        # the nominal massing box. Preserve both in every proof render so the
        # stepped silhouette can be judged against the reference sheet.
        distance *= 1.24
    views = {
        "preview": ((width * 0.82, -distance * 1.82, height * 0.88), (0, 0, height * 0.42), 54),
        "street": ((0, -distance * 1.95, height * 0.48), (0, 0, height * 0.44), 60),
        "front_corner_oblique": ((width * 0.90, -distance * 1.58, height * 0.80), (0, 0, height * 0.42), 54),
        "rear_corner_oblique": ((-width * 0.74, distance * 1.72, height * 0.80), (0, 0, height * 0.43), 55),
        "aerial": ((width * 0.88, -distance * 1.25, height * 2.10), (0, 0, height * 0.30), 52),
        "facade_close": ((0, -distance * 1.52, height * 0.46), (0, 0, height * 0.45), 64),
        "context": ((-width * 0.40, -distance * 2.35, height * 0.72), (0, 0, height * 0.40), 58),
    }
    selected = (
        {"preview", "street", "front_corner_oblique", "aerial"}
        if view_set == "pilot"
        else set(views)
    )
    # City Prompt and standards-compliant glTF viewers resolve the exported
    # opaque KHR transmission against the underlay. Eevee's raster proof does
    # not, so temporarily approximate that same coated-glass result with a
    # dithered surface. Restore every value before fallback modules export.
    proof_alpha = {
        "deconstructivist-museum": 0.22,
        "terracotta-fin-office": 0.18,
        "brutalist-civic-block": 0.48,
    }[family]
    glass_snapshots: list[
        tuple[
            bpy.types.Material,
            bpy.types.Node,
            tuple[float, float, float, float],
            float,
            float,
            str | None,
        ]
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
                tuple(mat.diffuse_color),
                float(bsdf.inputs["Alpha"].default_value),
                (
                    float(transmission.default_value)
                    if transmission is not None
                    else 0.0
                ),
                getattr(mat, "surface_render_method", None),
            )
        )
        mat.diffuse_color = (*tuple(mat.diffuse_color)[:3], proof_alpha)
        bsdf.inputs["Alpha"].default_value = proof_alpha
        if transmission is not None:
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
        for (
            mat,
            bsdf,
            diffuse,
            alpha,
            transmission_value,
            render_method,
        ) in glass_snapshots:
            mat.diffuse_color = diffuse
            bsdf.inputs["Alpha"].default_value = alpha
            transmission = bsdf.inputs.get("Transmission Weight")
            if transmission is not None:
                transmission.default_value = transmission_value
            if render_method is not None:
                mat.surface_render_method = render_method
    delete_objects(
        [obj for obj in list(bpy.data.objects) if obj.name.startswith("PRESENTATION_")]
    )
    if "elevation.jpg" not in rendered and (folder / "elevation.jpg").is_file():
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
        "triangle_count": triangle_count(objects),
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
    facade_assets = skin["zones"]["facade"]
    return {
        "schema": "facade-sheet@5",
        "source_directory": f"/families/{family}",
        "model": "gpt-image-2",
        "style_reference": "elevation.jpg",
        "goalpost_reference": cfg["goalpost"],
        "goalpost_policy": (
            "The locked catalogue image controls silhouette, proportions, "
            "openings, roof hierarchy, entrance geometry and material hierarchy."
        ),
        "runtime_material_profile": "pbr_physical_glazing_v2",
        "geometry_detail_profile": "hero",
        "pbr_channels": ["albedo", "normal", "roughness", "ao", "depth", "emissive"],
        "shadow_neutral": {
            "enabled": True,
            **skin["shadow_neutral"],
        },
        "bay_strategy": {
            "fixed_end_bays": [0, 3],
            "repeatable_middle_bays": [1, 2],
            "middle_variants": ["typical_a", "typical_b", "typical_c"],
            "rule": (
                "the landmark silhouette, entrance, corner returns, crown and "
                "roof stay fixed; only conservative fallback middle bands repeat"
            ),
        },
        "delivery": {
            "near_atlas_width_px": 2048,
            "far_atlas_width_px": 1024,
            "near_usage": "close-range physical glazing and custom PBR construction",
            "far_usage": "city-scale baked archetype material reference",
        },
        "assembly_contract": {
            "fixed": [
                "podium/entrance",
                "corner returns",
                "crown",
                "roof",
                "landmark silhouette",
            ],
            "repeatable": ["typical_a", "typical_b", "typical_c"],
            "side_elevations": (
                "front, left, right, rear and roof are authored as related but "
                "distinct construction; no elevation is a generic extrusion"
            ),
            "elevation_coverage": {
                "front": "primary public entrance, physical glazing and identity assembly",
                "left": "authored return with continued material and opening logic",
                "right": "authored return with continued material and opening logic",
                "rear": "quieter service elevation with compatible construction",
                "roof": "complete weathering plane, edge and screened service hierarchy",
            },
            "variation_policy": (
                "the fixed landmark accepts mild independent X/Y scaling; larger "
                "or more distorted user targets use the conservative family stack"
            ),
        },
        "assets": {
            "skin_manifest": "textures/skin_manifest.json",
            "source": skin["source"],
            "near": facade_assets["near"],
            "far": facade_assets["far"],
            "sources": skin["sources"],
        },
        "reference_registration": skin["reference_registration"],
    }


def source_provenance(family: str) -> dict:
    cfg = FAMILIES[family]
    return {
        "kind": "catalogue_goalpost_plus_imagegen_reference_package_and_authored_geometry",
        "catalogue_archetype_id": cfg["archetype_id"],
        "catalogue_variant_id": cfg["variant_id"],
        "goalpost": cfg["goalpost"],
        "goalpost_local_source": "textures/source/archetype-goalpost.png",
        "angle_reference": "textures/source/angle-reference-60.png",
        "roof_reference": "textures/source/angle-reference-90.png",
        "orthographic_elevation": "textures/source/elevation-source.png",
        "material_source": "textures/source/material-source.png",
        "reference_generation": "textures/source/reference-generation.json",
        "reference_underlay": REFERENCE_UNDERLAYS[family]["path"],
        "reference_underlay_generation": (
            "textures/source/reference-generation-v2.json"
        ),
        "elevation_source": f"/families/{family}/elevation.jpg",
        "skin_manifest": "textures/skin_manifest.json",
        "generator": (
            "tools/archetype_compiler/generate_wave6_nonresidential_families.py"
        ),
        "reference_method": (
            "hard-reference multi-view completion followed by physical "
            "construction and custom PBR derivation"
        ),
    }


def build_family(
    family: str,
    output_root: Path,
    *,
    view_set: str,
    skip_renders: bool,
    skip_modules: bool,
    skip_assembled_export: bool,
    modules_only: bool,
) -> None:
    global FAST_PILOT_MODE
    clear_scene()
    cfg = FAMILIES[family]
    folder = output_root / family
    folder.mkdir(parents=True, exist_ok=True)
    mats, skin = load_palette(family, folder)
    builders: dict[str, Callable[[dict[str, bpy.types.Material]], list[bpy.types.Object]]] = {
        "deconstructivist-museum": museum_fixed,
        "terracotta-fin-office": office_fixed,
        "brutalist-civic-block": civic_fixed,
    }
    assembled_path = folder / f"{family}_assembled.glb"
    if modules_only:
        if not assembled_path.is_file():
            raise FileNotFoundError(assembled_path)
        old_manifest = json.loads(
            (folder / f"{family}_manifest.json").read_text(encoding="utf-8")
        )
        fixed_objects: list[bpy.types.Object] = []
        fixed_triangles = int(old_manifest["assembled"]["triangle_count"])
        fixed_materials = int(old_manifest["assembled"].get("material_count") or 0)
        renders = list(old_manifest.get("renders") or [])
    else:
        FAST_PILOT_MODE = skip_assembled_export
        try:
            fixed_objects = builders[family](mats)
        finally:
            FAST_PILOT_MODE = False
        if not skip_assembled_export:
            export_glb(assembled_path, fixed_objects)
        fixed_triangles = triangle_count(fixed_objects)
        fixed_materials = len(
            {
                mat.name
                for obj in fixed_objects
                if obj.type == "MESH"
                for mat in obj.data.materials
            }
        )
        renders = (
            sorted(path.name for path in folder.glob(f"{family}_*.png"))
            if skip_renders
            else render_views(family, folder, view_set=view_set)
        )
    if (folder / "elevation.jpg").is_file() and "elevation.jpg" not in renders:
        renders.append("elevation.jpg")
    if skip_modules:
        print(
            f"[wave6-pilot] {family}: {fixed_triangles:,} tris, "
            f"{fixed_materials} materials, {len(renders)} renders",
            flush=True,
        )
        return
    if fixed_objects:
        delete_objects(fixed_objects)

    role_specs = [
        ("podium", "default", cfg["floor_height_m"]),
        ("floor", "typical_a", cfg["floor_height_m"]),
        ("floor", "typical_b", cfg["floor_height_m"]),
        ("floor", "typical_c", cfg["floor_height_m"]),
        ("crown", "crown", cfg["floor_height_m"]),
        ("roof", "default", 1.0),
    ]
    modules: list[dict] = []
    for role, variant, height in role_specs:
        objects = fallback_module(family, role, variant, height, mats)
        objects.extend(module_contract_markers(role, variant, height))
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
                height,
                objects,
                path.stat().st_size,
                skin,
            )
        )
        delete_objects(objects)

    width, depth, height = cfg["dimensions"]
    min_floors, max_floors, native_floors = cfg["floors"]
    footprint = {
        "preferredProfiles": ["rectangle"],
        "minimumPreferredProfiles": 1,
        "profileRationale": (
            "The family has one authored public front and landmark silhouette. "
            "Mild rectangular drawing variation uses independent landmark scaling; "
            "larger targets repeat the stack along the long streetwall axis."
        ),
        "fixedLandmarkScaleBand": cfg["fixed_band"],
        **cfg["footprint"],
        "profiles": {"rectangle": cfg["footprint"]},
    }
    assembled = {
        "filename": assembled_path.name,
        "floors": native_floors,
        "uses_setback": family == "terracotta-fin-office",
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
        "massing_graph": {"type": "fixed_landmark", "silhouette": family},
        "texture_keys": sorted(skin["zones"]),
        "ao_baked": True,
    }
    provenance = source_provenance(family)
    manifest = {
        "manifest_schema": 3,
        "grammar_schema_version": 3,
        "generator": {
            "name": (
                "archetype_compiler/generate_wave6_nonresidential_families.py"
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
            "wave6",
            "nonresidential",
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
            "silhouette": family,
            "render_locked": True,
            "goalpost": cfg["goalpost"],
            "fallback": "family_specific_modular_streetwall",
        },
        "material_budget": {
            "max_assembled_materials": 18,
            "rationale": (
                "Physical glazing, occupied depth, custom cladding, structure, "
                "roof and landscape remain separate so close-range materiality "
                "survives in every viewer."
            ),
        },
        "dimensions": {
            "width_m": width,
            "depth_m": depth,
            "podium_height_m": cfg["floor_height_m"],
            "floor_height_m": cfg["floor_height_m"],
            "setback_height_m": cfg["floor_height_m"],
            "roof_height_m": 1.0,
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
        "source_provenance": provenance,
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
        json.dumps(provenance, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"[wave6] {family}: {fixed_triangles:,} tris, "
        f"{len(modules)} modules, {len(renders)} renders",
        flush=True,
    )


def render_existing(family: str, output_root: Path, view_set: str) -> None:
    clear_scene()
    folder = output_root / family
    manifest_path = folder / f"{family}_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    bpy.ops.import_scene.gltf(
        filepath=str(folder / manifest["assembled"]["filename"])
    )
    skin = json.loads(
        (folder / "textures" / "skin_manifest.json").read_text(encoding="utf-8")
    )
    manifest["facade_sheet"] = facade_contract(family, skin)
    manifest["source_provenance"] = source_provenance(family)
    manifest["renders"] = render_views(family, folder, view_set=view_set)
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"[wave6-render] {family}: {len(manifest['renders'])} renders", flush=True)


def main() -> int:
    args = parse_args()
    if args.skip_assembled_export and not args.skip_modules:
        raise ValueError("--skip-assembled-export requires --skip-modules")
    output_root = args.output_root.resolve()
    selected = args.family or list(FAMILIES)
    for family in selected:
        if args.render_existing:
            render_existing(family, output_root, args.view_set)
        else:
            build_family(
                family,
                output_root,
                view_set=args.view_set,
                skip_renders=args.skip_renders,
                skip_modules=args.skip_modules,
                skip_assembled_export=args.skip_assembled_export,
                modules_only=args.modules_only,
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
