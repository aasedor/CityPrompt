"""Generate the three reference-locked Wave 12 LEGO building families.

The batch deliberately spans three unrelated construction systems:

* a planted concrete vertical-forest residential tower;
* a Tudor collegiate-gothic gatehouse quadrangle; and
* a cable-stayed steel-and-glass airport terminal.

Every family exports a complete fixed landmark, a six-part semantic fallback
kit, true-metric manifests, and a bounded multi-camera visual proof set.

Run from the repository root with Blender 5.x::

    blender --background --factory-startup --python \
      tools/archetype_compiler/generate_wave12_diverse_families.py -- \
      --family vertical-forest-residential \
      --output-root frontend/public/families --view-set pilot
"""
from __future__ import annotations

import argparse
import json
import math
import random
import shutil
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
    skin_material,
    sphere,
    texture_inventory,
)


_CUBE_MESHES: dict[str, bpy.types.Mesh] = {}
_CYLINDER_MESHES: dict[tuple[str, int], bpy.types.Mesh] = {}
_SPHERE_MESHES: dict[str, bpy.types.Mesh] = {}


FAMILIES: dict[str, dict] = {
    "vertical-forest-residential": {
        "archetype_id": "vertical_forest_residential",
        "variant_id": "vertical_forest_bosco",
        "aliases": [
            "vertical_forest_residential",
            "vertical_forest_bosco",
            "bosco_verticale_residential",
            "planted_concrete_balcony_tower",
        ],
        "label": "Vertical Forest Residential - Bosco",
        "aesthetic": "eco_urban_green_architecture",
        "development_type": "residential_highrise",
        "glass_profile": "neutral_low_iron_residential_occupied",
        "native": (31.0, 31.0, 67.8),
        "native_floors": 18,
        "min_floors": 10,
        "max_floors": 30,
        "floor_height": 3.35,
        "catalogue_slug": "vertical_forest_residential",
        "catalogue_variant_index": None,
        "identity": (
            "An eighteen-storey dark glazed residential core sits behind a "
            "continuous off-white concrete frame, deep cantilevered balcony "
            "trays and real soil planters carrying mature trees on every side."
        ),
        "material_zones": (
            "lightly weathered board-formed off-white concrete; dark bronze "
            "thermally broken frames; neutral low-iron residential glass; warm "
            "occupied apartment depth; charcoal planter liners and dark soil; "
            "temperate olive and restrained burgundy foliage; natural tree bark"
        ),
        "reuse_keys": [
            "Vertical Forest Residential",
            "Bosco Verticale Residential",
            "Planted Balcony Tower",
            "Living Concrete High Rise",
        ],
    },
    "collegiate-gothic-gatehouse": {
        "archetype_id": "collegiate_gothic_education",
        "variant_id": "collegiate_gothic_tudor",
        "aliases": [
            "collegiate_gothic_education",
            "collegiate_gothic_tudor",
            "tudor_gothic_quadrangle",
            "limestone_college_gatehouse",
        ],
        "label": "Collegiate Gothic - Tudor Gatehouse Quadrangle",
        "aesthetic": "collegiate_gothic",
        "development_type": "institutional_education",
        "glass_profile": "heritage_leaded_occupied",
        "native": (64.0, 44.0, 34.0),
        "native_floors": 4,
        "min_floors": 2,
        "max_floors": 6,
        "floor_height": 4.0,
        "catalogue_slug": "collegiate_gothic_education",
        "catalogue_variant_index": 0,
        "identity": (
            "A honey-limestone collegiate quadrangle is centred on a real deep "
            "pointed gate passage beneath a crenellated tower, with deep "
            "lead-glazed traceried windows, buttresses, slate gables, clustered "
            "chimneys and pinnacled parapets."
        ),
        "material_zones": (
            "warm honey Cotswold limestone ashlar; deeper carved limestone "
            "tracery and buttresses; dark Welsh slate; lead-grey heritage glass; "
            "warm occupied academic rooms; dark oak gate doors; black ironwork"
        ),
        "reuse_keys": [
            "Collegiate Gothic",
            "Tudor Gothic Quadrangle",
            "University Gatehouse Court",
            "Honey Limestone College",
        ],
    },
    "cable-stayed-airport-terminal": {
        "archetype_id": "airport_terminal_building",
        "variant_id": "cable_stayed_steel_truss_terminal",
        "aliases": [
            "airport_terminal_building",
            "cable_stayed_steel_truss_terminal",
            "high_tech_airport_terminal",
            "branching_column_departure_hall",
        ],
        "label": "Airport Terminal - Cable-Stayed Steel Truss",
        "aesthetic": "high_tech_civic_infrastructure",
        "development_type": "transportation_terminal",
        "glass_profile": "high_transmission_terminal_curtain_wall",
        "native": (90.0, 68.0, 28.0),
        "native_floors": 3,
        "min_floors": 2,
        "max_floors": 6,
        "floor_height": 5.4,
        "catalogue_slug": "airport-terminal-building",
        "catalogue_variant_index": 0,
        "identity": (
            "A transparent two-level departure hall is sheltered by one sweeping "
            "steel space-frame canopy, supported on branching tree columns and "
            "radiating stay cables from a central mast, with diamond-braced side "
            "walls and three complete airside gate bridges."
        ),
        "material_zones": (
            "neutral high-transmission terminal glass; champagne-silver aluminum "
            "composite panels; graphite and silver structural steel; translucent "
            "roof infill; warm occupied terminal depth; pale concrete apron; "
            "dark low-slope service roof"
        ),
        "reuse_keys": [
            "Airport Terminal Building",
            "Cable Stayed Steel Truss Terminal",
            "High Tech Departure Hall",
            "Branching Column Airport",
        ],
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", choices=sorted(FAMILIES), required=True)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("frontend/public/families"),
    )
    parser.add_argument(
        "--view-set",
        choices=(
            "preview",
            "pilot",
            "all",
            "front_elevation",
            "front_corner_oblique",
            "rear_corner_oblique",
            "aerial",
            "facade_close",
            "identity_close",
            "street",
            "context",
        ),
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


def set_normal_strength(mat: bpy.types.Material, strength: float) -> bpy.types.Material:
    for node in mat.node_tree.nodes:
        if node.bl_idname == "ShaderNodeNormalMap":
            node.inputs["Strength"].default_value = strength
    return mat


def wash_material(
    mat: bpy.types.Material,
    *,
    tint: tuple[float, float, float],
    factor: float,
    roughness: float,
) -> bpy.types.Material:
    """Retain authored microtexture while restoring the approved material hue."""
    bsdf = bsdf_for(mat)
    base_color = bsdf.inputs["Base Color"]
    if base_color.is_linked:
        source = base_color.links[0].from_socket
        mat.node_tree.links.remove(base_color.links[0])
        wash = mat.node_tree.nodes.new("ShaderNodeMixRGB")
        wash.name = wash.label = "REFERENCE_PALETTE_WASH"
        wash.blend_type = "MIX"
        wash.inputs[0].default_value = factor
        wash.inputs[2].default_value = (*tint, 1.0)
        mat.node_tree.links.new(source, wash.inputs[1])
        mat.node_tree.links.new(wash.outputs["Color"], base_color)
    bsdf.inputs["Roughness"].default_value = roughness
    mat.diffuse_color = (*tint, 1.0)
    return mat


def configure_glass(
    mat: bpy.types.Material,
    cfg: dict,
    *,
    tint: tuple[float, float, float],
    transmission: float,
    alpha: float,
) -> bpy.types.Material:
    bsdf = bsdf_for(mat)
    base_color = bsdf.inputs["Base Color"]
    if base_color.is_linked:
        source = base_color.links[0].from_socket
        mat.node_tree.links.remove(base_color.links[0])
        wash = mat.node_tree.nodes.new("ShaderNodeMixRGB")
        wash.name = wash.label = "PHYSICAL_GLASS_TINT_WASH"
        wash.blend_type = "MIX"
        wash.inputs[0].default_value = 0.62
        wash.inputs[2].default_value = (*tint, 1.0)
        mat.node_tree.links.new(source, wash.inputs[1])
        mat.node_tree.links.new(wash.outputs["Color"], base_color)
    bsdf.inputs["Roughness"].default_value = 0.09
    if bsdf.inputs.get("Transmission Weight"):
        bsdf.inputs["Transmission Weight"].default_value = transmission
    if bsdf.inputs.get("Coat Weight"):
        bsdf.inputs["Coat Weight"].default_value = 0.32
    if bsdf.inputs.get("Coat Roughness"):
        bsdf.inputs["Coat Roughness"].default_value = 0.05
    if bsdf.inputs.get("IOR"):
        bsdf.inputs["IOR"].default_value = 1.50
    if bsdf.inputs.get("Alpha"):
        bsdf.inputs["Alpha"].default_value = alpha
    mat.diffuse_color = (*tint, alpha)
    try:
        mat.surface_render_method = "BLENDED"
    except Exception:
        pass
    mat.use_backface_culling = False
    mat["glazing_profile"] = cfg["glass_profile"]
    mat["glazing_lod"] = "physical_separate_pane"
    mat["pane_recess_m"] = 0.16
    mat["interior_depth_m"] = 0.62
    return mat


def configure_occupied(
    mat: bpy.types.Material,
    *,
    warmth: tuple[float, float, float],
    emission: float,
) -> bpy.types.Material:
    bsdf = bsdf_for(mat)
    base_color = bsdf.inputs["Base Color"]
    if base_color.is_linked:
        source = base_color.links[0].from_socket
        mat.node_tree.links.remove(base_color.links[0])
        mix = mat.node_tree.nodes.new("ShaderNodeMixRGB")
        mix.name = mix.label = "OCCUPIED_DEPTH_WARMTH"
        mix.blend_type = "ADD"
        mix.inputs[0].default_value = 0.18
        mix.inputs[2].default_value = (*warmth, 1.0)
        mat.node_tree.links.new(source, mix.inputs[1])
        mat.node_tree.links.new(mix.outputs["Color"], base_color)
        emission_color = bsdf.inputs.get("Emission Color")
        if emission_color:
            mat.node_tree.links.new(mix.outputs["Color"], emission_color)
            bsdf.inputs["Emission Strength"].default_value = emission
    mat["occupied_depth_layer"] = True
    return mat


def foliage_card_material(folder: Path, cfg: dict) -> bpy.types.Material:
    path = folder / "textures" / "source" / "foliage-card-v1.png"
    if not path.is_file():
        raise FileNotFoundError(path)
    mat = bpy.data.materials.new("MAT_W12_FOREST_PhotorealFoliageCard")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    transparent = nodes.new("ShaderNodeBsdfTransparent")
    mix_shader = nodes.new("ShaderNodeMixShader")
    image = nodes.new("ShaderNodeTexImage")
    image.name = image.label = "REFERENCE_LOCKED_FOLIAGE_CUTOUT"
    image.image = bpy.data.images.load(str(path), check_existing=True)
    image.image.alpha_mode = "STRAIGHT"
    image.extension = "CLIP"
    links.new(image.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(image.outputs["Alpha"], bsdf.inputs["Alpha"])
    links.new(image.outputs["Alpha"], mix_shader.inputs[0])
    links.new(transparent.outputs["BSDF"], mix_shader.inputs[1])
    links.new(bsdf.outputs["BSDF"], mix_shader.inputs[2])
    links.new(mix_shader.outputs["Shader"], output.inputs["Surface"])
    bsdf.inputs["Roughness"].default_value = 0.76
    if bsdf.inputs.get("Coat Weight"):
        bsdf.inputs["Coat Weight"].default_value = 0.05
    try:
        mat.surface_render_method = "BLENDED"
    except Exception:
        pass
    mat.use_backface_culling = False
    mat.diffuse_color = (0.28, 0.40, 0.12, 1.0)
    mat["source_variant_id"] = cfg["variant_id"]
    mat["generation_archetype_id"] = cfg["variant_id"]
    mat["reference_locked"] = True
    mat["foliage_cutout_source"] = "textures/source/foliage-card-v1.png"
    return mat


def load_palette(folder: Path, cfg: dict) -> tuple[dict[str, bpy.types.Material], dict]:
    skin = load_skin_manifest(folder)
    if not skin:
        raise FileNotFoundError(folder / "textures" / "skin_manifest.json")
    near = {zone: values["near"] for zone, values in skin["zones"].items()}

    def pbr(
        key: str,
        name: str,
        *,
        metallic: float = 0.0,
        transmission: float = 0.0,
        saturation: float = 1.0,
        value: float = 1.0,
        normal: float = 0.42,
    ) -> bpy.types.Material:
        result = skin_material(
            name,
            folder,
            near[key],
            key,
            metallic=metallic,
            transmission=transmission,
        )
        grade_material(result, saturation=saturation, value=value)
        set_normal_strength(result, normal)
        result["source_variant_id"] = cfg["variant_id"]
        result["generation_archetype_id"] = cfg["variant_id"]
        result["reference_locked"] = True
        return result

    family = cfg["family"]
    if family == "vertical-forest-residential":
        mats = {
            "concrete": pbr("concrete", "MAT_W12_FOREST_BoardFormedConcrete", saturation=0.42, value=0.95, normal=0.46),
            "frame": pbr("bronze_frame", "MAT_W12_FOREST_DarkBronzeFrame", metallic=0.52, saturation=0.36, value=0.52, normal=0.18),
            "glass": configure_glass(
                pbr("vision_glass", "MAT_W12_FOREST_NeutralVisionGlass", transmission=0.55, saturation=0.25, value=0.86, normal=0.08),
                cfg,
                tint=(0.34, 0.40, 0.38),
                transmission=0.78,
                alpha=0.35,
            ),
            "interior": configure_occupied(
                pbr("interior", "MAT_W12_FOREST_OccupiedApartmentDepth", saturation=0.70, value=0.68, normal=0.10),
                warmth=(0.34, 0.20, 0.09),
                emission=0.10,
            ),
            "foliage": wash_material(
                pbr("foliage", "MAT_W12_FOREST_TemperateFoliage", saturation=0.92, value=1.04, normal=0.48),
                tint=(0.15, 0.27, 0.07),
                factor=0.74,
                roughness=0.78,
            ),
            "foliage_alt": wash_material(
                pbr("foliage", "MAT_W12_FOREST_BurgundyFoliage", saturation=0.88, value=0.88, normal=0.48),
                tint=(0.36, 0.16, 0.12),
                factor=0.72,
                roughness=0.80,
            ),
            "soil": pbr("soil", "MAT_W12_FOREST_DarkPlanterSoil", saturation=0.52, value=0.42, normal=0.62),
            "planter": wash_material(
                pbr("planter", "MAT_W12_FOREST_CharcoalPlanter", metallic=0.08, saturation=0.32, value=0.72, normal=0.32),
                tint=(0.11, 0.12, 0.10),
                factor=0.44,
                roughness=0.67,
            ),
            "trunk": wash_material(
                pbr("trunk", "MAT_W12_FOREST_NaturalTreeBark", saturation=0.72, value=0.82, normal=0.66),
                tint=(0.28, 0.18, 0.10),
                factor=0.62,
                roughness=0.82,
            ),
            "roof": pbr("roof", "MAT_W12_FOREST_GreenRoof", saturation=0.62, value=0.52, normal=0.50),
            "paving": pbr("paving", "MAT_W12_FOREST_WarmGreyPaving", saturation=0.20, value=0.80, normal=0.32),
        }
        mats["foliage_card"] = foliage_card_material(folder, cfg)
    elif family == "collegiate-gothic-gatehouse":
        mats = {
            "stone": pbr("limestone", "MAT_W12_GOTHIC_HoneyLimestone", saturation=0.82, value=0.96, normal=0.46),
            "carved": pbr("carved_stone", "MAT_W12_GOTHIC_CarvedLimestone", saturation=0.74, value=0.90, normal=0.56),
            "slate": pbr("slate", "MAT_W12_GOTHIC_DarkWelshSlate", saturation=0.32, value=0.40, normal=0.58),
            "glass": configure_glass(
                pbr("leaded_glass", "MAT_W12_GOTHIC_LeadedGlass", transmission=0.40, saturation=0.34, value=0.58, normal=0.08),
                cfg,
                tint=(0.23, 0.28, 0.27),
                transmission=0.58,
                alpha=0.48,
            ),
            "interior": configure_occupied(
                pbr("interior", "MAT_W12_GOTHIC_OccupiedAcademicDepth", saturation=0.72, value=0.58, normal=0.10),
                warmth=(0.34, 0.18, 0.06),
                emission=0.12,
            ),
            "oak": pbr("oak", "MAT_W12_GOTHIC_DarkOak", saturation=0.66, value=0.44, normal=0.58),
            "iron": pbr("iron", "MAT_W12_GOTHIC_BlackIron", metallic=0.58, saturation=0.18, value=0.35, normal=0.24),
            "paving": pbr("paving", "MAT_W12_GOTHIC_StoneCourtPaving", saturation=0.36, value=0.72, normal=0.44),
            "grass": material("MAT_W12_GOTHIC_QuadrangleLawn", (0.105, 0.185, 0.055, 1.0), 0.94),
        }
    else:
        mats = {
            "steel": pbr("steel", "MAT_W12_TERMINAL_SilverStructuralSteel", metallic=0.70, saturation=0.18, value=0.80, normal=0.16),
            "graphite": pbr("graphite", "MAT_W12_TERMINAL_GraphiteSteel", metallic=0.56, saturation=0.16, value=0.38, normal=0.20),
            "aluminum": pbr("aluminum", "MAT_W12_TERMINAL_ChampagneAluminum", metallic=0.64, saturation=0.30, value=0.78, normal=0.22),
            "glass": configure_glass(
                pbr("terminal_glass", "MAT_W12_TERMINAL_HighTransmissionGlass", transmission=0.58, saturation=0.22, value=0.92, normal=0.06),
                cfg,
                tint=(0.45, 0.54, 0.56),
                transmission=0.84,
                alpha=0.30,
            ),
            "roof_glass": configure_glass(
                pbr("roof_infill", "MAT_W12_TERMINAL_TranslucentRoofInfill", transmission=0.42, saturation=0.20, value=0.94, normal=0.10),
                cfg,
                tint=(0.68, 0.73, 0.72),
                transmission=0.62,
                alpha=0.52,
            ),
            "interior": configure_occupied(
                pbr("interior", "MAT_W12_TERMINAL_OccupiedTerminalDepth", saturation=0.82, value=0.88, normal=0.10),
                warmth=(0.30, 0.17, 0.06),
                emission=0.22,
            ),
            "concrete": pbr("concrete", "MAT_W12_TERMINAL_PaleApronConcrete", saturation=0.20, value=0.96, normal=0.34),
            "roof": pbr("roof", "MAT_W12_TERMINAL_DarkServiceRoof", saturation=0.24, value=0.42, normal=0.34),
        }
    return mats, skin


def tag_object(
    obj: bpy.types.Object,
    semantic: str,
    cfg: dict,
    *,
    role: str = "assembled",
) -> bpy.types.Object:
    obj["module_family"] = cfg["family"]
    obj["source_variant_id"] = cfg["variant_id"]
    obj["generation_archetype_id"] = cfg["variant_id"]
    obj["semantic"] = semantic
    obj["module_role"] = role
    obj["reference_locked"] = True
    return obj


def add_box(
    objects: list[bpy.types.Object],
    name: str,
    size: tuple[float, float, float],
    location: tuple[float, float, float],
    mat: bpy.types.Material,
    cfg: dict,
    semantic: str,
    *,
    bevel: float = 0.0,
    role: str = "assembled",
) -> bpy.types.Object:
    mesh = _CUBE_MESHES.get(mat.name)
    if mesh is None:
        vertices = [
            (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5),
            (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5),
            (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5),
            (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5),
        ]
        faces = [
            (0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
            (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7),
        ]
        mesh = bpy.data.meshes.new("W12_UnitCube_" + mat.name)
        mesh.from_pydata(vertices, [], faces)
        mesh.update()
        mesh.materials.append(mat)
        uv_layer = mesh.uv_layers.new(name="UVMap")
        for polygon in mesh.polygons:
            for loop_index, uv in zip(polygon.loop_indices, ((0, 0), (1, 0), (1, 1), (0, 1))):
                uv_layer.data[loop_index].uv = uv
        _CUBE_MESHES[mat.name] = mesh
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.scale = size
    bpy.context.collection.objects.link(obj)
    tag_object(obj, semantic, cfg, role=role)
    objects.append(obj)
    return obj


def add_beam(
    objects: list[bpy.types.Object],
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    radius: float,
    mat: bpy.types.Material,
    cfg: dict,
    semantic: str,
    *,
    role: str = "assembled",
) -> bpy.types.Object:
    mesh = _unit_cylinder_mesh(mat, 8)
    a, b = Vector(start), Vector(end)
    delta = b - a
    obj = bpy.data.objects.new(name, mesh)
    obj.location = (a + b) * 0.5
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(delta.normalized())
    obj.scale = (radius, radius, delta.length)
    bpy.context.collection.objects.link(obj)
    tag_object(obj, semantic, cfg, role=role)
    objects.append(obj)
    return obj


def _unit_cylinder_mesh(mat: bpy.types.Material, vertices: int) -> bpy.types.Mesh:
    key = (mat.name, vertices)
    mesh = _CYLINDER_MESHES.get(key)
    if mesh is not None:
        return mesh
    points: list[tuple[float, float, float]] = []
    for z in (-0.5, 0.5):
        for index in range(vertices):
            angle = math.tau * index / vertices
            points.append((math.cos(angle), math.sin(angle), z))
    faces: list[tuple[int, ...]] = []
    faces.append(tuple(reversed(range(vertices))))
    faces.append(tuple(range(vertices, vertices * 2)))
    for index in range(vertices):
        nxt = (index + 1) % vertices
        faces.append((index, nxt, vertices + nxt, vertices + index))
    mesh = bpy.data.meshes.new(f"W12_UnitCylinder_{vertices}_{mat.name}")
    mesh.from_pydata(points, [], faces)
    mesh.update()
    mesh.materials.append(mat)
    uv_layer = mesh.uv_layers.new(name="UVMap")
    for polygon in mesh.polygons:
        count = len(polygon.loop_indices)
        for sequence, loop_index in enumerate(polygon.loop_indices):
            vertex = mesh.vertices[mesh.loops[loop_index].vertex_index].co
            if count == 4:
                u = (math.atan2(vertex.y, vertex.x) / math.tau + 1.0) % 1.0
                v = vertex.z + 0.5
            else:
                u, v = vertex.x * 0.5 + 0.5, vertex.y * 0.5 + 0.5
            uv_layer.data[loop_index].uv = (u, v)
    _CYLINDER_MESHES[key] = mesh
    return mesh


def add_cylinder(
    objects: list[bpy.types.Object],
    name: str,
    radius: float,
    depth: float,
    location: tuple[float, float, float],
    mat: bpy.types.Material,
    cfg: dict,
    semantic: str,
    *,
    vertices: int = 16,
    role: str = "assembled",
) -> bpy.types.Object:
    mesh = _unit_cylinder_mesh(mat, vertices)
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.scale = (radius, radius, depth)
    bpy.context.collection.objects.link(obj)
    tag_object(obj, semantic, cfg, role=role)
    objects.append(obj)
    return obj


def add_sphere(
    objects: list[bpy.types.Object],
    name: str,
    radius: float,
    location: tuple[float, float, float],
    mat: bpy.types.Material,
    cfg: dict,
    semantic: str,
    *,
    scale: tuple[float, float, float] = (1.0, 1.0, 1.0),
    role: str = "assembled",
) -> bpy.types.Object:
    mesh = _SPHERE_MESHES.get(mat.name)
    if mesh is None:
        segments, rings = 10, 6
        vertices: list[tuple[float, float, float]] = [(0.0, 0.0, 1.0)]
        for ring in range(1, rings):
            phi = math.pi * ring / rings
            for segment in range(segments):
                theta = math.tau * segment / segments
                vertices.append((math.sin(phi) * math.cos(theta), math.sin(phi) * math.sin(theta), math.cos(phi)))
        vertices.append((0.0, 0.0, -1.0))
        top, bottom = 0, len(vertices) - 1
        faces: list[tuple[int, ...]] = []
        for segment in range(segments):
            faces.append((top, 1 + segment, 1 + (segment + 1) % segments))
        for ring in range(rings - 2):
            start = 1 + ring * segments
            next_start = start + segments
            for segment in range(segments):
                nxt = (segment + 1) % segments
                faces.append((start + segment, next_start + segment, next_start + nxt, start + nxt))
        last_start = 1 + (rings - 2) * segments
        for segment in range(segments):
            faces.append((last_start + segment, bottom, last_start + (segment + 1) % segments))
        mesh = bpy.data.meshes.new("W12_UnitSphere_" + mat.name)
        mesh.from_pydata(vertices, [], faces)
        mesh.update()
        mesh.materials.append(mat)
        uv_layer = mesh.uv_layers.new(name="UVMap")
        for polygon in mesh.polygons:
            for loop_index in polygon.loop_indices:
                co = mesh.vertices[mesh.loops[loop_index].vertex_index].co.normalized()
                uv_layer.data[loop_index].uv = ((math.atan2(co.y, co.x) / math.tau + 1.0) % 1.0, math.acos(max(-1.0, min(1.0, co.z))) / math.pi)
        _SPHERE_MESHES[mat.name] = mesh
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.scale = tuple(radius * value for value in scale)
    bpy.context.collection.objects.link(obj)
    tag_object(obj, semantic, cfg, role=role)
    objects.append(obj)
    return obj


def create_mesh_object(
    objects: list[bpy.types.Object],
    name: str,
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, ...]],
    mat: bpy.types.Material,
    cfg: dict,
    semantic: str,
    *,
    role: str = "assembled",
) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    mesh.materials.append(mat)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    tag_object(obj, semantic, cfg, role=role)
    objects.append(obj)
    return obj


def normalize_bottom_centre(objects: list[bpy.types.Object]) -> None:
    bpy.context.view_layer.update()
    points = [
        obj.matrix_world @ Vector(corner)
        for obj in objects
        if obj.type == "MESH"
        for corner in obj.bound_box
    ]
    minimum = Vector(tuple(min(point[i] for point in points) for i in range(3)))
    maximum = Vector(tuple(max(point[i] for point in points) for i in range(3)))
    centre_x = (minimum.x + maximum.x) * 0.5
    centre_y = (minimum.y + maximum.y) * 0.5
    for obj in objects:
        obj.location.x -= centre_x
        obj.location.y -= centre_y
        obj.location.z -= minimum.z
    bpy.context.view_layer.update()


def bounds_dimensions(objects: list[bpy.types.Object]) -> tuple[float, float, float]:
    bpy.context.view_layer.update()
    points = [
        obj.matrix_world @ Vector(corner)
        for obj in objects
        if obj.type == "MESH"
        for corner in obj.bound_box
    ]
    minimum = Vector(tuple(min(point[i] for point in points) for i in range(3)))
    maximum = Vector(tuple(max(point[i] for point in points) for i in range(3)))
    extent = maximum - minimum
    return tuple(round(value, 3) for value in extent)


def evaluated_triangle_count(objects: list[bpy.types.Object]) -> int:
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
            if slot.material
        }
    )


def add_layered_window_y(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    centre_x: float,
    facade_y: float,
    centre_z: float,
    width: float,
    height: float,
    outward_sign: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
    frame_thickness: float = 0.11,
) -> None:
    glass_y = facade_y
    interior_y = facade_y - outward_sign * 0.30
    frame_y = facade_y + outward_sign * 0.08
    add_box(objects, prefix + "_Occupied", (width - 0.16, 0.08, height - 0.12), (centre_x, interior_y, centre_z), mats["interior"], cfg, "occupied_depth", role=role)
    add_box(objects, prefix + "_Glass", (width - 0.10, 0.10, height - 0.08), (centre_x, glass_y, centre_z), mats["glass"], cfg, "physical_glazing", role=role)
    for x in (centre_x - width / 2, centre_x + width / 2):
        add_box(objects, prefix + f"_Jamb_{x:.2f}", (frame_thickness, 0.18, height), (x, frame_y, centre_z), mats["frame"], cfg, "window_frame", role=role)
    for z in (centre_z - height / 2, centre_z + height / 2):
        add_box(objects, prefix + f"_Rail_{z:.2f}", (width, 0.18, frame_thickness), (centre_x, frame_y, z), mats["frame"], cfg, "window_frame", role=role)
    add_box(objects, prefix + "_Mullion", (frame_thickness, 0.18, height), (centre_x, frame_y, centre_z), mats["frame"], cfg, "window_mullion", role=role)


def add_layered_window_x(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    centre_y: float,
    facade_x: float,
    centre_z: float,
    width: float,
    height: float,
    outward_sign: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
) -> None:
    glass_x = facade_x
    interior_x = facade_x - outward_sign * 0.30
    frame_x = facade_x + outward_sign * 0.08
    add_box(objects, prefix + "_Occupied", (0.08, width - 0.16, height - 0.12), (interior_x, centre_y, centre_z), mats["interior"], cfg, "occupied_depth", role=role)
    add_box(objects, prefix + "_Glass", (0.10, width - 0.10, height - 0.08), (glass_x, centre_y, centre_z), mats["glass"], cfg, "physical_glazing", role=role)
    for y in (centre_y - width / 2, centre_y + width / 2):
        add_box(objects, prefix + f"_Jamb_{y:.2f}", (0.18, 0.11, height), (frame_x, y, centre_z), mats["frame"], cfg, "window_frame", role=role)
    for z in (centre_z - height / 2, centre_z + height / 2):
        add_box(objects, prefix + f"_Rail_{z:.2f}", (0.18, width, 0.11), (frame_x, centre_y, z), mats["frame"], cfg, "window_frame", role=role)
    add_box(objects, prefix + "_Mullion", (0.18, 0.11, height), (frame_x, centre_y, centre_z), mats["frame"], cfg, "window_mullion", role=role)


def add_tree(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    base: tuple[float, float, float],
    height: float,
    crown_radius: float,
    mats: dict,
    cfg: dict,
    rng: random.Random,
    role: str = "assembled",
    burgundy: bool = False,
) -> None:
    x, y, z = base
    trunk_height = height * 0.70
    add_cylinder(objects, prefix + "_Trunk", 0.10 + crown_radius * 0.035, trunk_height, (x, y, z + trunk_height / 2), mats["trunk"], cfg, "real_tree_trunk", vertices=9, role=role)
    for branch_index, angle in enumerate((0.2, 2.3, 4.4)):
        start = (x, y, z + trunk_height * 0.56)
        end = (
            x + math.cos(angle + rng.uniform(-0.25, 0.25)) * crown_radius * 0.62,
            y + math.sin(angle + rng.uniform(-0.25, 0.25)) * crown_radius * 0.62,
            z + trunk_height * (0.82 + 0.10 * branch_index),
        )
        add_beam(objects, prefix + f"_Branch_{branch_index}", start, end, 0.045, mats["trunk"], cfg, "real_tree_branch", role=role)
    crown_centre = (x, y, z + trunk_height * 0.88)
    add_foliage_cross(
        objects,
        prefix=prefix + "_Canopy",
        centre=crown_centre,
        width=crown_radius * 2.65,
        height=crown_radius * 2.25,
        mat=mats["foliage_card"],
        cfg=cfg,
        role=role,
        rotation_offset=rng.uniform(0.0, math.tau),
    )
    # A few physical interior clusters keep the cutout from reading as a flat card
    # at grazing angles while the keyed leaf edge carries the fine silhouette.
    interior_mat = mats["foliage_alt"] if burgundy else mats["foliage"]
    for cluster in range(1):
        angle = rng.uniform(0.0, math.tau)
        add_sphere(
            objects,
            prefix + f"_InteriorFoliage_{cluster}",
            crown_radius * 0.26,
            (
                x + math.cos(angle) * crown_radius * 0.34,
                y + math.sin(angle) * crown_radius * 0.34,
                crown_centre[2],
            ),
            interior_mat,
            cfg,
            "three_dimensional_foliage_core",
            scale=(1.0, 0.82, 0.70),
            role=role,
        )


def add_foliage_cross(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    centre: tuple[float, float, float],
    width: float,
    height: float,
    mat: bpy.types.Material,
    cfg: dict,
    role: str,
    rotation_offset: float,
) -> None:
    cx, cy, cz = centre
    vertices = [
        (-width / 2, 0.0, -height / 2),
        (width / 2, 0.0, -height / 2),
        (width / 2, 0.0, height / 2),
        (-width / 2, 0.0, height / 2),
    ]
    for plane_index in range(4):
        mesh = bpy.data.meshes.new(prefix + f"_VerticalMesh_{plane_index}")
        mesh.from_pydata(vertices, [], [(0, 1, 2, 3)])
        mesh.update()
        mesh.materials.append(mat)
        uv = mesh.uv_layers.new(name="UVMap")
        for loop_index, coord in zip(mesh.polygons[0].loop_indices, ((0, 0), (1, 0), (1, 1), (0, 1))):
            uv.data[loop_index].uv = coord
        obj = bpy.data.objects.new(prefix + f"_Vertical_{plane_index}", mesh)
        obj.location = (cx, cy, cz)
        obj.rotation_euler[2] = rotation_offset + plane_index * math.pi / 4
        bpy.context.collection.objects.link(obj)
        tag_object(obj, "photoreal_crossed_foliage_card", cfg, role=role)
        objects.append(obj)


def add_vertical_planter(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    centre: tuple[float, float, float],
    size: tuple[float, float],
    tree_axis: str,
    floor_index: int,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
    tree: bool = True,
) -> None:
    x, y, slab_z = centre
    sx, sy = size
    planter_height = 0.76
    add_box(objects, prefix + "_Shell", (sx, sy, planter_height), (x, y, slab_z + planter_height / 2), mats["planter"], cfg, "integral_balcony_planter", bevel=0.05, role=role)
    add_box(objects, prefix + "_Soil", (sx - 0.16, sy - 0.16, 0.10), (x, y, slab_z + planter_height - 0.04), mats["soil"], cfg, "real_planter_soil", role=role)
    rng = random.Random(12000 + floor_index * 97 + round((x + 20) * 13) + round((y + 20) * 17))
    if tree:
        height = 3.35 + rng.uniform(-0.15, 0.70)
        crown = 1.72 + rng.uniform(-0.10, 0.26)
        tree_x = x + (rng.uniform(-0.40, 0.40) if tree_axis == "x" else rng.uniform(-0.18, 0.18))
        tree_y = y + (rng.uniform(-0.40, 0.40) if tree_axis == "y" else rng.uniform(-0.18, 0.18))
        add_tree(
            objects,
            prefix=prefix + "_Tree",
            base=(tree_x, tree_y, slab_z + planter_height),
            height=height,
            crown_radius=crown,
            mats=mats,
            cfg=cfg,
            rng=rng,
            role=role,
            burgundy=(floor_index + round(abs(x + y))) % 7 == 0,
        )
        for support_index, offset in enumerate((-0.34, 0.34)):
            if tree_axis == "x":
                end = (tree_x + offset, y, slab_z + 0.16)
            else:
                end = (x, tree_y + offset, slab_z + 0.16)
            add_beam(objects, prefix + f"_TreeStay_{support_index}", (tree_x, tree_y, slab_z + 1.42), end, 0.018, mats["frame"], cfg, "tree_support_cable", role=role)
    for shrub_index in range(2):
        offset_x = (shrub_index - 0.5) * sx * 0.34 if tree_axis == "x" else 0.0
        offset_y = (shrub_index - 0.5) * sy * 0.34 if tree_axis == "y" else 0.0
        add_sphere(objects, prefix + f"_Shrub_{shrub_index}", 0.40, (x + offset_x, y + offset_y, slab_z + 0.92), mats["foliage"], cfg, "balcony_shrub", scale=(1.25, 0.84, 0.58), role=role)


def add_vertical_storey(
    objects: list[bpy.types.Object],
    *,
    floor_index: int,
    base_z: float,
    storey_height: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
    module_variant: str = "typical_a",
) -> None:
    prefix = f"FOREST_{role}_{floor_index}_{module_variant}"
    slab_z = base_z + 0.20
    add_box(objects, prefix + "_BalconyTray", (28.0, 28.0, 0.40), (0.0, 0.0, slab_z), mats["concrete"], cfg, "deep_cantilevered_balcony_tray", bevel=0.07, role=role)
    window_height = storey_height - 0.72
    window_z = base_z + 0.50 + window_height / 2
    for bay, x in enumerate((-8.25, -2.75, 2.75, 8.25)):
        add_layered_window_y(objects, prefix=f"{prefix}_FrontWindow_{bay}", centre_x=x, facade_y=-11.15, centre_z=window_z, width=5.22, height=window_height, outward_sign=-1.0, mats=mats, cfg=cfg, role=role)
        add_layered_window_y(objects, prefix=f"{prefix}_RearWindow_{bay}", centre_x=x, facade_y=11.15, centre_z=window_z, width=5.22, height=window_height, outward_sign=1.0, mats=mats, cfg=cfg, role=role)
    for bay, y in enumerate((-8.25, -2.75, 2.75, 8.25)):
        add_layered_window_x(objects, prefix=f"{prefix}_LeftWindow_{bay}", centre_y=y, facade_x=-11.15, centre_z=window_z, width=5.22, height=window_height, outward_sign=-1.0, mats=mats, cfg=cfg, role=role)
        add_layered_window_x(objects, prefix=f"{prefix}_RightWindow_{bay}", centre_y=y, facade_x=11.15, centre_z=window_z, width=5.22, height=window_height, outward_sign=1.0, mats=mats, cfg=cfg, role=role)
    patterns = {
        "typical_a": ((-8.2, -2.7, 8.2), (-5.4, 5.4), (-8.2, 2.7), (-2.7, 8.2)),
        "typical_b": ((-5.4, 2.7), (-8.2, 0.0, 8.2), (-5.4, 5.4), (-8.2, 0.0)),
        "typical_c": ((-8.2, 0.0, 8.2), (-2.7, 5.4), (-8.2, -2.7, 8.2), (0.0, 8.2)),
    }
    front, right, rear, left = patterns[module_variant]
    for index, x in enumerate(front):
        add_vertical_planter(objects, prefix=f"{prefix}_FrontPlanter_{index}", centre=(x, -13.08, base_z + 0.40), size=(4.35, 1.38), tree_axis="x", floor_index=floor_index, mats=mats, cfg=cfg, role=role, tree=True)
    for index, y in enumerate(right):
        add_vertical_planter(objects, prefix=f"{prefix}_RightPlanter_{index}", centre=(13.08, y, base_z + 0.40), size=(1.38, 4.35), tree_axis="y", floor_index=floor_index + 19, mats=mats, cfg=cfg, role=role, tree=True)
    for index, x in enumerate(rear):
        add_vertical_planter(objects, prefix=f"{prefix}_RearPlanter_{index}", centre=(x, 13.08, base_z + 0.40), size=(4.35, 1.38), tree_axis="x", floor_index=floor_index + 37, mats=mats, cfg=cfg, role=role, tree=True)
    for index, y in enumerate(left):
        add_vertical_planter(objects, prefix=f"{prefix}_LeftPlanter_{index}", centre=(-13.08, y, base_z + 0.40), size=(1.38, 4.35), tree_axis="y", floor_index=floor_index + 53, mats=mats, cfg=cfg, role=role, tree=True)


def build_vertical_forest(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    ground_height = 4.20
    typical = cfg["floor_height"]
    roof_z = ground_height + 17 * typical
    add_box(objects, "FOREST_BasePaving", (30.2, 30.2, 0.18), (0.0, 0.0, 0.09), mats["paving"], cfg, "integrated_landscaped_base", bevel=0.08)
    add_vertical_storey(objects, floor_index=0, base_z=0.0, storey_height=ground_height, mats=mats, cfg=cfg, module_variant="typical_a")
    for floor in range(1, 18):
        variant = ("typical_a", "typical_b", "typical_c")[floor % 3]
        add_vertical_storey(objects, floor_index=floor, base_z=ground_height + (floor - 1) * typical, storey_height=typical, mats=mats, cfg=cfg, module_variant=variant)
    for x in (-13.65, -6.82, 0.0, 6.82, 13.65):
        for y in (-13.65, 13.65):
            add_box(objects, f"FOREST_ContinuousPost_Y_{x}_{y}", (0.46, 0.46, roof_z + 0.80), (x, y, (roof_z + 0.80) / 2), mats["concrete"], cfg, "continuous_perimeter_concrete_frame", bevel=0.05)
    for y in (-6.82, 0.0, 6.82):
        for x in (-13.65, 13.65):
            add_box(objects, f"FOREST_ContinuousPost_X_{x}_{y}", (0.46, 0.46, roof_z + 0.80), (x, y, (roof_z + 0.80) / 2), mats["concrete"], cfg, "continuous_perimeter_concrete_frame", bevel=0.05)
    add_box(objects, "FOREST_RoofSlab", (28.0, 28.0, 0.50), (0.0, 0.0, roof_z + 0.25), mats["concrete"], cfg, "roof_garden_structural_slab", bevel=0.08)
    add_box(objects, "FOREST_RoofCore", (10.0, 9.0, 2.6), (0.0, 0.8, roof_z + 1.80), mats["frame"], cfg, "screened_rooftop_service_core", bevel=0.10)
    for side_index, (x, y, sx, sy, axis) in enumerate(((-8.0, -10.5, 6.5, 2.1, "x"), (7.8, -10.4, 6.8, 2.2, "x"), (-10.4, 0.0, 2.2, 8.0, "y"), (10.4, 1.0, 2.2, 8.0, "y"), (-5.5, 10.2, 7.0, 2.2, "x"), (5.7, 10.2, 6.5, 2.2, "x"))):
        add_vertical_planter(objects, prefix=f"FOREST_RoofPlanter_{side_index}", centre=(x, y, roof_z + 0.50), size=(sx, sy), tree_axis=axis, floor_index=90 + side_index, mats=mats, cfg=cfg, tree=True)
    for index, x in enumerate((-8.0, 0.0, 8.0)):
        add_box(objects, f"FOREST_LobbyDoor_{index}", (2.4, 0.12, 3.2), (x, -14.01, 1.85), mats["glass"], cfg, "transparent_planted_lobby_entrance")
        add_box(objects, f"FOREST_LobbyDoorFrame_{index}", (2.62, 0.20, 0.14), (x, -14.08, 3.48), mats["frame"], cfg, "bronze_lobby_frame")
    return objects


def create_gable_roof(
    objects: list[bpy.types.Object],
    *,
    name: str,
    centre: tuple[float, float],
    length: float,
    depth: float,
    base_z: float,
    ridge_z: float,
    orientation: str,
    mat: bpy.types.Material,
    cfg: dict,
    role: str = "assembled",
) -> bpy.types.Object:
    cx, cy = centre
    if orientation == "x":
        vertices = [
            (cx - length / 2, cy - depth / 2, base_z),
            (cx + length / 2, cy - depth / 2, base_z),
            (cx + length / 2, cy + depth / 2, base_z),
            (cx - length / 2, cy + depth / 2, base_z),
            (cx - length / 2, cy, ridge_z),
            (cx + length / 2, cy, ridge_z),
        ]
        faces = [(0, 1, 5, 4), (3, 4, 5, 2), (0, 4, 3), (1, 2, 5)]
    else:
        vertices = [
            (cx - depth / 2, cy - length / 2, base_z),
            (cx + depth / 2, cy - length / 2, base_z),
            (cx + depth / 2, cy + length / 2, base_z),
            (cx - depth / 2, cy + length / 2, base_z),
            (cx, cy - length / 2, ridge_z),
            (cx, cy + length / 2, ridge_z),
        ]
        faces = [(0, 1, 4), (3, 5, 2), (0, 4, 5, 3), (1, 2, 5, 4)]
    return create_mesh_object(objects, name, vertices, faces, mat, cfg, "steep_true_slate_gable", role=role)


def add_pointed_window_y(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    x: float,
    y: float,
    base_z: float,
    width: float,
    rect_height: float,
    point_height: float,
    outward_sign: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
) -> None:
    centre_z = base_z + rect_height / 2
    add_box(objects, prefix + "_Interior", (width - 0.26, 0.08, rect_height + point_height - 0.20), (x, y - outward_sign * 0.30, base_z + (rect_height + point_height) / 2), mats["interior"], cfg, "occupied_academic_depth", role=role)
    add_box(objects, prefix + "_Glass", (width - 0.20, 0.10, rect_height), (x, y, centre_z), mats["glass"], cfg, "physical_leaded_glazing", role=role)
    glass_vertices = [
        (x - width / 2 + 0.10, y, base_z + rect_height - 0.04),
        (x + width / 2 - 0.10, y, base_z + rect_height - 0.04),
        (x, y, base_z + rect_height + point_height - 0.10),
    ]
    create_mesh_object(objects, prefix + "_PointGlass", glass_vertices, [(0, 1, 2)], mats["glass"], cfg, "physical_pointed_leaded_glazing", role=role)
    frame_y = y + outward_sign * 0.10
    for sx in (-1.0, 1.0):
        add_box(objects, prefix + f"_Jamb_{sx}", (0.13, 0.24, rect_height), (x + sx * width / 2, frame_y, centre_z), mats["carved"], cfg, "carved_stone_tracery", role=role)
        add_beam(objects, prefix + f"_Arch_{sx}", (x + sx * width / 2, frame_y, base_z + rect_height), (x, frame_y, base_z + rect_height + point_height), 0.09, mats["carved"], cfg, "continuous_pointed_arch_frame", role=role)
    add_box(objects, prefix + "_StoneMullion", (0.10, 0.24, rect_height + point_height * 0.88), (x, frame_y, base_z + (rect_height + point_height * 0.88) / 2), mats["carved"], cfg, "stone_window_mullion", role=role)
    add_box(objects, prefix + "_StoneTransom", (width, 0.24, 0.10), (x, frame_y, base_z + rect_height * 0.56), mats["carved"], cfg, "stone_window_transom", role=role)
    # Fine dark lead cames sit on the pane rather than being baked into stone.
    # Their small shadows and contrasting material keep the glazing legible at
    # both street and catalogue distances.
    lead_y = frame_y + outward_sign * 0.035
    for ratio in (-0.25, 0.25):
        add_box(objects, prefix + f"_LeadVertical_{ratio}", (0.026, 0.055, rect_height - 0.12), (x + ratio * width, lead_y, centre_z), mats["iron"], cfg, "physical_lead_came", role=role)
    for ratio in (0.28, 0.76):
        add_box(objects, prefix + f"_LeadHorizontal_{ratio}", (width - 0.25, 0.055, 0.026), (x, lead_y, base_z + rect_height * ratio), mats["iron"], cfg, "physical_lead_came", role=role)


def add_gothic_facade_y(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    width: float,
    y: float,
    base_z: float,
    floors: int,
    floor_height: float,
    bays: int,
    outward_sign: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
    omit_centre_ground: bool = False,
) -> None:
    bay_width = width / bays
    total_height = floors * floor_height
    for boundary in range(bays + 1):
        x = -width / 2 + boundary * bay_width
        add_box(objects, prefix + f"_Pier_{boundary}", (0.58, 0.85, total_height), (x, y, base_z + total_height / 2), mats["stone"], cfg, "load_bearing_limestone_pier", bevel=0.05, role=role)
        if boundary in (0, bays):
            add_box(objects, prefix + f"_Buttress_{boundary}", (1.05, 1.45, total_height * 0.88), (x, y + outward_sign * 0.48, base_z + total_height * 0.44), mats["carved"], cfg, "integrated_stone_buttress", bevel=0.08, role=role)
    for floor in range(floors + 1):
        z = base_z + floor * floor_height
        add_box(objects, prefix + f"_String_{floor}", (width + 0.65, 0.82, 0.42), (0.0, y, z + 0.21), mats["stone"], cfg, "carved_stone_string_course", bevel=0.04, role=role)
    for floor in range(floors):
        for bay in range(bays):
            if omit_centre_ground and floor == 0 and abs(bay - (bays - 1) / 2) < 0.6:
                continue
            x = -width / 2 + bay_width * (bay + 0.5)
            z0 = base_z + floor * floor_height + 0.64
            add_pointed_window_y(objects, prefix=f"{prefix}_F{floor}_B{bay}", x=x, y=y + outward_sign * 0.44, base_z=z0, width=bay_width * 0.56, rect_height=floor_height * 0.52, point_height=floor_height * 0.18, outward_sign=outward_sign, mats=mats, cfg=cfg, role=role)


def add_battlements(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    width: float,
    depth: float,
    base_z: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
) -> None:
    add_box(objects, prefix + "_ParapetFront", (width, 0.75, 0.78), (0.0, -depth / 2, base_z + 0.39), mats["stone"], cfg, "crenellated_parapet_base", role=role)
    add_box(objects, prefix + "_ParapetRear", (width, 0.75, 0.78), (0.0, depth / 2, base_z + 0.39), mats["stone"], cfg, "crenellated_parapet_base", role=role)
    add_box(objects, prefix + "_ParapetLeft", (0.75, depth, 0.78), (-width / 2, 0.0, base_z + 0.39), mats["stone"], cfg, "crenellated_parapet_base", role=role)
    add_box(objects, prefix + "_ParapetRight", (0.75, depth, 0.78), (width / 2, 0.0, base_z + 0.39), mats["stone"], cfg, "crenellated_parapet_base", role=role)
    count_x = max(3, round(width / 2.2))
    count_y = max(3, round(depth / 2.2))
    for side_y in (-depth / 2, depth / 2):
        for index in range(count_x):
            x = -width / 2 + (index + 0.5) * width / count_x
            add_box(objects, prefix + f"_MerlonY_{side_y}_{index}", (0.95, 0.92, 0.92), (x, side_y, base_z + 1.22), mats["carved"], cfg, "crenellation_merlon", bevel=0.04, role=role)
    for side_x in (-width / 2, width / 2):
        for index in range(count_y):
            y = -depth / 2 + (index + 0.5) * depth / count_y
            add_box(objects, prefix + f"_MerlonX_{side_x}_{index}", (0.92, 0.95, 0.92), (side_x, y, base_z + 1.22), mats["carved"], cfg, "crenellation_merlon", bevel=0.04, role=role)


def build_collegiate_gothic(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    wing_height = 15.8
    add_box(objects, "GOTHIC_QuadranglePaving", (61.5, 41.5, 0.18), (0.0, 0.0, 0.09), mats["paving"], cfg, "open_college_quadrangle_paving")
    add_box(objects, "GOTHIC_QuadrangleLawn", (39.0, 17.0, 0.12), (0.0, 0.7, 0.20), mats["grass"], cfg, "enclosed_collegiate_lawn")
    add_box(objects, "GOTHIC_CourtCrossPath", (4.0, 22.0, 0.07), (0.0, 0.7, 0.31), mats["paving"], cfg, "axial_college_court_path")
    add_box(objects, "GOTHIC_CourtPerimeterPathFront", (48.0, 2.4, 0.07), (0.0, -10.0, 0.31), mats["paving"], cfg, "college_court_perimeter_path")
    add_box(objects, "GOTHIC_CourtPerimeterPathRear", (48.0, 2.4, 0.07), (0.0, 11.4, 0.31), mats["paving"], cfg, "college_court_perimeter_path")
    for name, size, centre in (
        # The front wing is deliberately split around the gate. A shaded box
        # placed over a solid bar is not a passage and failed the street proof.
        ("FrontWingFloorLeft", (27.0, 10.0, wing_height), (-16.5, -15.0, wing_height / 2)),
        ("FrontWingFloorRight", (27.0, 10.0, wing_height), (16.5, -15.0, wing_height / 2)),
        ("RearWingFloor", (60.0, 9.0, wing_height), (0.0, 15.5, wing_height / 2)),
        ("WestWingFloor", (10.0, 21.5, wing_height), (-25.0, 0.2, wing_height / 2)),
        ("EastWingFloor", (10.0, 21.5, wing_height), (25.0, 0.2, wing_height / 2)),
    ):
        add_box(objects, "GOTHIC_" + name, size, centre, mats["stone"], cfg, "collegiate_quadrangle_wing_mass", bevel=0.06)
    add_gothic_facade_y(objects, prefix="GOTHIC_FrontOuter", width=60.0, y=-20.05, base_z=0.0, floors=3, floor_height=5.26, bays=11, outward_sign=-1.0, mats=mats, cfg=cfg, omit_centre_ground=True)
    add_gothic_facade_y(objects, prefix="GOTHIC_FrontCourt", width=60.0, y=-9.95, base_z=0.0, floors=3, floor_height=5.26, bays=11, outward_sign=1.0, mats=mats, cfg=cfg, omit_centre_ground=True)
    add_gothic_facade_y(objects, prefix="GOTHIC_RearOuter", width=60.0, y=20.05, base_z=0.0, floors=3, floor_height=5.26, bays=11, outward_sign=1.0, mats=mats, cfg=cfg)
    add_gothic_facade_y(objects, prefix="GOTHIC_RearCourt", width=60.0, y=10.95, base_z=0.0, floors=3, floor_height=5.26, bays=11, outward_sign=-1.0, mats=mats, cfg=cfg)
    # Side wings use rotated facade schedules: build them locally and rotate.
    for side, x, outward in (("West", -30.05, -1.0), ("East", 30.05, 1.0)):
        for bay, y in enumerate((-7.8, -2.6, 2.6, 7.8)):
            for floor in range(3):
                z0 = floor * 5.26 + 0.76
                glass_x = x + outward * 0.44
                # X-facing Gothic opening assembled from a rotated Y-facing group.
                before = len(objects)
                add_pointed_window_y(objects, prefix=f"GOTHIC_{side}_F{floor}_B{bay}", x=y, y=0.0, base_z=z0, width=2.75, rect_height=2.85, point_height=0.82, outward_sign=outward, mats=mats, cfg=cfg)
                for obj in objects[before:]:
                    obj.rotation_euler[2] = math.radians(90)
                    obj.location.x, obj.location.y = x + obj.location.y, y - obj.location.x
                    # The local rotation places the authored reveal on the real side facade.
                    obj["semantic"] = "wrapped_side_" + str(obj.get("semantic", "gothic_opening"))
        for boundary, y in enumerate((-10.75, -5.37, 0.0, 5.37, 10.75)):
            add_box(objects, f"GOTHIC_{side}_Pier_{boundary}", (0.85, 0.58, wing_height), (x, y, wing_height / 2), mats["stone"], cfg, "side_limestone_pier", bevel=0.05)
        for floor in range(4):
            add_box(objects, f"GOTHIC_{side}_String_{floor}", (0.82, 21.5, 0.36), (x, 0.2, floor * 5.26 + 0.18), mats["stone"], cfg, "wrapped_stone_string_course")
    for roof_name, centre, length, depth, orientation in (
        ("FrontRoof", (0.0, -15.0), 60.0, 10.6, "x"),
        ("RearRoof", (0.0, 15.5), 60.0, 9.6, "x"),
        ("WestRoof", (-25.0, 0.2), 21.5, 10.6, "y"),
        ("EastRoof", (25.0, 0.2), 21.5, 10.6, "y"),
    ):
        create_gable_roof(objects, name="GOTHIC_" + roof_name, centre=centre, length=length, depth=depth, base_z=15.8, ridge_z=20.2, orientation=orientation, mat=mats["slate"], cfg=cfg)
    # A castellated stone eave is one of the reference's strongest long-range
    # cues. It remains separate from the slate so both materials shade properly.
    for side_y in (-20.22, 20.22):
        for index in range(28):
            x = -29.0 + index * (58.0 / 27.0)
            add_box(objects, f"GOTHIC_EaveMerlon_{side_y}_{index}", (0.82, 0.72, 0.78), (x, side_y, 16.15), mats["carved"], cfg, "castellated_college_eave", bevel=0.035)
    # Gate tower is constructed around a real passage, never as a facade card.
    tower_y = -21.2
    gate_width = 5.4
    gate_rect = 4.25
    gate_point = 4.25
    tower_width = 12.4
    tower_depth = 8.4
    tower_height = 26.0
    # Split the tall piers into coursed lifts so the ashlar remains at a true
    # architectural scale instead of stretching one texture over 28 metres.
    for segment in range(5):
        z0 = segment * tower_height / 5
        height = tower_height / 5
        for side, x in (("Left", -(tower_width + gate_width) / 4), ("Right", (tower_width + gate_width) / 4)):
            add_box(objects, f"GOTHIC_GateTower{side}Pier_{segment}", ((tower_width - gate_width) / 2, tower_depth, height + 0.04), (x, tower_y, z0 + height / 2), mats["stone"], cfg, "integrated_gatehouse_pier", bevel=0.045)
    for segment in range(4):
        z0 = gate_rect + gate_point + segment * (tower_height - gate_rect - gate_point) / 4
        height = (tower_height - gate_rect - gate_point) / 4
        add_box(objects, f"GOTHIC_GateTowerUpper_{segment}", (gate_width, tower_depth, height + 0.04), (0.0, tower_y, z0 + height / 2), mats["stone"], cfg, "gatehouse_upper_tower", bevel=0.045)
    # True empty tunnel: only the returns, ceiling and paving are modelled.
    # The sightline continues through the split front wing into the green court.
    add_box(objects, "GOTHIC_GateTunnelLeftReturn", (0.22, tower_depth + 10.0, gate_rect), (-gate_width / 2 + 0.12, tower_y + 1.0, gate_rect / 2), mats["interior"], cfg, "open_gate_passage_return")
    add_box(objects, "GOTHIC_GateTunnelRightReturn", (0.22, tower_depth + 10.0, gate_rect), (gate_width / 2 - 0.12, tower_y + 1.0, gate_rect / 2), mats["interior"], cfg, "open_gate_passage_return")
    add_box(objects, "GOTHIC_GateTunnelPaving", (gate_width - 0.35, tower_depth + 12.0, 0.10), (0.0, tower_y + 1.5, 0.25), mats["paving"], cfg, "continuous_gate_passage_paving")
    # A segmented two-centre arch replaces the earlier straight triangular
    # outline, which read as a porch roof instead of a deep Gothic gateway.
    # Each spandrel strip is a real extruded stone volume, leaving the central
    # passage genuinely empty from forecourt to quadrangle.
    y0, y1 = tower_y - tower_depth / 2, tower_y + tower_depth / 2
    def arch_half(sign: float, radius: float, spring: float, top: float) -> list[tuple[float, float]]:
        start = (sign * radius, spring)
        control = (sign * radius * 0.98, top - (top - spring) * 0.12)
        end = (0.0, top)
        result: list[tuple[float, float]] = []
        for index in range(7):
            t = index / 6
            one = 1.0 - t
            result.append((
                one * one * start[0] + 2.0 * one * t * control[0] + t * t * end[0],
                one * one * start[1] + 2.0 * one * t * control[1] + t * t * end[1],
            ))
        return result

    arch_top = gate_rect + gate_point
    outer_halves = {side: arch_half(side, gate_width / 2, gate_rect, arch_top) for side in (-1.0, 1.0)}
    for side, points in outer_halves.items():
        for segment, (a, b) in enumerate(zip(points, points[1:])):
            poly = [(a[0], a[1]), (b[0], b[1]), (b[0], arch_top), (a[0], arch_top)]
            vertices = [(x, y0, z) for x, z in poly] + [(x, y1, z) for x, z in poly]
            faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
            create_mesh_object(objects, f"GOTHIC_GateSpandrel_{side}_{segment}", vertices, faces, mats["stone"], cfg, "curved_stone_gate_arch_spandrel")
    front_y = tower_y - tower_depth / 2 - 0.28
    for sx in (-1.0, 1.0):
        add_box(objects, f"GOTHIC_GateJamb_{sx}", (0.48, 0.82, gate_rect), (sx * gate_width / 2, front_y, gate_rect / 2), mats["carved"], cfg, "carved_gate_portal_return", bevel=0.04)
        outer = outer_halves[sx]
        inner = arch_half(sx, gate_width / 2 - 0.38, gate_rect - 0.16, arch_top - 0.42)
        for segment, (a, b) in enumerate(zip(outer, outer[1:])):
            add_beam(objects, f"GOTHIC_GateArch_{sx}_{segment}", (a[0], front_y, a[1]), (b[0], front_y, b[1]), 0.30, mats["carved"], cfg, "continuous_two_centre_gate_arch")
        for segment, (a, b) in enumerate(zip(inner, inner[1:])):
            add_beam(objects, f"GOTHIC_GateArchInner_{sx}_{segment}", (a[0], front_y - 0.06, a[1]), (b[0], front_y - 0.06, b[1]), 0.15, mats["carved"], cfg, "nested_two_centre_gate_arch")
    for rib, y in enumerate((tower_y - 2.9, tower_y - 1.45, tower_y, tower_y + 1.45, tower_y + 2.9)):
        for sx in (-1.0, 1.0):
            tunnel_curve = arch_half(sx, gate_width / 2 - 0.46, gate_rect - 0.30, arch_top - 0.55)
            for segment, (a, b) in enumerate(zip(tunnel_curve, tunnel_curve[1:])):
                add_beam(objects, f"GOTHIC_GateTunnelRib_{rib}_{sx}_{segment}", (a[0], y, a[1]), (b[0], y, b[1]), 0.22, mats["interior"], cfg, "ribbed_two_centre_gate_tunnel")
    add_box(objects, "GOTHIC_GateOakDoorLeft", (0.20, 2.35, 4.4), (-gate_width / 2 + 0.30, tower_y - 0.5, 2.2), mats["oak"], cfg, "open_heavy_oak_gate_door")
    add_box(objects, "GOTHIC_GateOakDoorRight", (0.20, 2.35, 4.4), (gate_width / 2 - 0.30, tower_y - 0.5, 2.2), mats["oak"], cfg, "open_heavy_oak_gate_door")
    for step in range(5):
        add_box(objects, f"GOTHIC_IntegratedEntryStep_{step}", (8.8 - step * 0.38, 1.05, 0.18), (0.0, -26.0 - step * 0.45, 0.09 + step * 0.18), mats["paving"], cfg, "integrated_ceremonial_gate_stair", bevel=0.04)
    for tier, (base_z, rect_h, point_h) in enumerate(((10.0, 3.0, 0.82), (15.6, 4.7, 1.20))):
        for bay, x in enumerate((-3.0, 0.0, 3.0)):
            add_pointed_window_y(objects, prefix=f"GOTHIC_TowerTraceried_T{tier}_{bay}", x=x, y=tower_y - tower_depth / 2 - 0.05, base_z=base_z, width=2.10, rect_height=rect_h, point_height=point_h, outward_sign=-1.0, mats=mats, cfg=cfg)
    for x in (-tower_width / 2 + 0.55, tower_width / 2 - 0.55):
        add_box(objects, f"GOTHIC_TowerCornerButtress_{x}", (0.72, 1.00, tower_height), (x, tower_y - tower_depth / 2 - 0.24, tower_height / 2), mats["carved"], cfg, "continuous_gatehouse_corner_buttress", bevel=0.05)
    for z in (8.9, 14.8, 22.2):
        add_box(objects, f"GOTHIC_TowerString_{z}", (tower_width + 0.60, 0.86, 0.34), (0.0, tower_y - tower_depth / 2 - 0.08, z), mats["carved"], cfg, "gatehouse_string_course", bevel=0.035)
    battlement_start = len(objects)
    add_battlements(objects, prefix="GOTHIC_GateTower", width=tower_width, depth=tower_depth, base_z=tower_height, mats=mats, cfg=cfg)
    for obj in objects[battlement_start:]:
        obj.location.y += tower_y
    add_box(objects, "GOTHIC_TowerHeraldicPanel", (1.75, 0.26, 1.42), (0.0, tower_y - tower_depth / 2 - 0.28, 23.35), mats["carved"], cfg, "carved_college_heraldic_panel", bevel=0.055)
    for x in (-tower_width / 2, tower_width / 2):
        for y in (tower_y - tower_depth / 2, tower_y + tower_depth / 2):
            add_cylinder(objects, f"GOTHIC_PinnacleBase_{x}_{y}", 0.46, 1.9, (x, y, 28.2), mats["carved"], cfg, "stone_gatehouse_pinnacle", vertices=8)
            add_cylinder(objects, f"GOTHIC_PinnacleSpire_{x}_{y}", 0.24, 2.4, (x, y, 30.0), mats["carved"], cfg, "stone_gatehouse_pinnacle_spire", vertices=8)
    for wing_x in (-25.0, -9.0, 9.0, 25.0):
        add_box(objects, f"GOTHIC_ChimneyBase_{wing_x}", (2.15, 1.20, 0.55), (wing_x, 14.2, 19.0), mats["carved"], cfg, "integrated_chimney_base", bevel=0.04)
        for stack in range(3):
            x = wing_x + (stack - 1) * 0.68
            add_box(objects, f"GOTHIC_Chimney_{wing_x}_{stack}", (0.46, 0.52, 2.9), (x, 14.2, 20.55), mats["stone"], cfg, "clustered_square_chimney_flue", bevel=0.035)
            add_box(objects, f"GOTHIC_ChimneyCap_{wing_x}_{stack}", (0.62, 0.66, 0.18), (x, 14.2, 22.08), mats["carved"], cfg, "carved_chimney_cap", bevel=0.025)
    return objects


def create_curved_terminal_roof(
    objects: list[bpy.types.Object],
    *,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
    width: float = 88.0,
    depth: float = 60.0,
    base_z: float = 14.8,
) -> None:
    x_count = 12
    y_count = 8
    vertices: list[tuple[float, float, float]] = []
    for yi in range(y_count + 1):
        y = -depth / 2 + yi * depth / y_count
        for xi in range(x_count + 1):
            x = -width / 2 + xi * width / x_count
            z = base_z + 4.2 * (1.0 - (x / (width / 2)) ** 2) - 0.034 * y
            vertices.append((x, y, z))
    faces = []
    for yi in range(y_count):
        for xi in range(x_count):
            a = yi * (x_count + 1) + xi
            faces.append((a, a + 1, a + x_count + 2, a + x_count + 1))
    create_mesh_object(objects, "TERMINAL_SweepingRoofInfill", vertices, faces, mats["roof_glass"], cfg, "translucent_sweeping_roof_infill", role=role)
    def roof_point(x: float, y: float) -> tuple[float, float, float]:
        return (x, y, base_z + 4.2 * (1.0 - (x / (width / 2)) ** 2) - 0.034 * y)
    for xi in range(x_count + 1):
        x = -width / 2 + xi * width / x_count
        add_beam(objects, f"TERMINAL_RoofLongTruss_{xi}", roof_point(x, -depth / 2), roof_point(x, depth / 2), 0.16, mats["steel"], cfg, "steel_space_frame_longitudinal", role=role)
    for yi in range(y_count + 1):
        y = -depth / 2 + yi * depth / y_count
        for xi in range(x_count):
            x0 = -width / 2 + xi * width / x_count
            x1 = -width / 2 + (xi + 1) * width / x_count
            add_beam(objects, f"TERMINAL_RoofCrossTruss_{yi}_{xi}", roof_point(x0, y), roof_point(x1, y), 0.14, mats["steel"], cfg, "steel_space_frame_transverse", role=role)
    # Fine crossed webs turn the canopy into a real two-way space frame and
    # reproduce the dense triangulated soffit visible in the roof reference.
    for yi in range(y_count):
        y0 = -depth / 2 + yi * depth / y_count
        y1 = -depth / 2 + (yi + 1) * depth / y_count
        for xi in range(x_count):
            x0 = -width / 2 + xi * width / x_count
            x1 = -width / 2 + (xi + 1) * width / x_count
            add_beam(objects, f"TERMINAL_RoofDiagonalA_{yi}_{xi}", roof_point(x0, y0), roof_point(x1, y1), 0.045, mats["steel"], cfg, "triangulated_space_frame_web", role=role)
            add_beam(objects, f"TERMINAL_RoofDiagonalB_{yi}_{xi}", roof_point(x1, y0), roof_point(x0, y1), 0.045, mats["steel"], cfg, "triangulated_space_frame_web", role=role)


def add_terminal_glazed_wall_y(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    y: float,
    width: float,
    height: float,
    outward_sign: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
) -> None:
    bays = 12
    bay_width = width / bays
    for bay in range(bays):
        x = -width / 2 + (bay + 0.5) * bay_width
        add_box(objects, prefix + f"_Occupied_{bay}", (bay_width - 0.30, 0.10, height - 0.40), (x, y - outward_sign * 0.42, height / 2), mats["interior"], cfg, "occupied_terminal_depth", role=role)
        add_box(objects, prefix + f"_Glass_{bay}", (bay_width - 0.22, 0.12, height - 0.28), (x, y, height / 2), mats["glass"], cfg, "physical_terminal_glass", role=role)
        add_box(objects, prefix + f"_Mullion_{bay}", (0.18, 0.30, height), (-width / 2 + bay * bay_width, y + outward_sign * 0.10, height / 2), mats["steel"], cfg, "curtain_wall_pressure_cap", role=role)
        add_box(objects, prefix + f"_MidRail_{bay}", (bay_width, 0.30, 0.20), (x, y + outward_sign * 0.10, height * 0.50), mats["steel"], cfg, "curtain_wall_pressure_cap", role=role)
    add_box(objects, prefix + "_EndMullion", (0.18, 0.30, height), (width / 2, y + outward_sign * 0.10, height / 2), mats["steel"], cfg, "curtain_wall_pressure_cap", role=role)


def build_airport_terminal(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    add_box(objects, "TERMINAL_Apron", (88.0, 66.0, 0.20), (0.0, 0.0, 0.10), mats["concrete"], cfg, "integrated_terminal_apron", bevel=0.08)
    add_box(objects, "TERMINAL_InteriorGroundPlate", (82.0, 49.0, 0.36), (0.0, 0.5, 0.38), mats["concrete"], cfg, "terminal_ground_floor_plate", bevel=0.05)
    add_box(objects, "TERMINAL_Mezzanine", (72.0, 28.0, 0.40), (0.0, 5.0, 5.8), mats["concrete"], cfg, "terminal_mezzanine_plate", bevel=0.05)
    add_box(objects, "TERMINAL_UpperConcourse", (78.0, 34.0, 0.42), (0.0, 2.0, 11.1), mats["concrete"], cfg, "upper_departure_concourse_plate", bevel=0.05)
    add_terminal_glazed_wall_y(objects, prefix="TERMINAL_Landside", y=-25.0, width=82.0, height=13.8, outward_sign=-1.0, mats=mats, cfg=cfg)
    add_terminal_glazed_wall_y(objects, prefix="TERMINAL_Airside", y=25.0, width=82.0, height=13.8, outward_sign=1.0, mats=mats, cfg=cfg)
    for side, x, sign in (("West", -41.0, -1.0), ("East", 41.0, 1.0)):
        add_box(objects, f"TERMINAL_{side}Glass", (0.14, 50.0, 13.6), (x, 0.0, 6.9), mats["glass"], cfg, "wrapped_terminal_side_glass")
        add_box(objects, f"TERMINAL_{side}Occupied", (0.10, 49.6, 13.2), (x - sign * 0.38, 0.0, 6.9), mats["interior"], cfg, "wrapped_occupied_terminal_depth")
        y_steps = (-25.0, -12.5, 0.0, 12.5, 25.0)
        for bay in range(len(y_steps) - 1):
            y0, y1 = y_steps[bay], y_steps[bay + 1]
            add_beam(objects, f"TERMINAL_{side}DiamondA_{bay}", (x + sign * 0.16, y0, 0.8), (x + sign * 0.16, y1, 13.0), 0.20, mats["aluminum"], cfg, "diamond_braced_side_enclosure")
            add_beam(objects, f"TERMINAL_{side}DiamondB_{bay}", (x + sign * 0.16, y0, 13.0), (x + sign * 0.16, y1, 0.8), 0.20, mats["aluminum"], cfg, "diamond_braced_side_enclosure")
    create_curved_terminal_roof(objects, mats=mats, cfg=cfg)
    # Branching columns grow from the landside hall into the canopy grid.
    for index, x in enumerate((-34.0, -20.4, -6.8, 6.8, 20.4, 34.0)):
        stem_top = (x, -26.2, 9.1)
        add_beam(objects, f"TERMINAL_TreeColumnStem_{index}", (x, -26.2, 0.35), stem_top, 0.38, mats["graphite"], cfg, "branching_steel_tree_column")
        for branch, target_x in enumerate((x - 5.7, x + 5.7)):
            target_y = -29.1
            target_z = 14.8 + 4.2 * (1.0 - (target_x / 44.0) ** 2) - 0.034 * target_y
            add_beam(objects, f"TERMINAL_TreeColumnBranch_{index}_{branch}", stem_top, (target_x, target_y, target_z), 0.30, mats["graphite"], cfg, "branching_steel_tree_column")
        # A shorter inner fork completes the tree silhouette and makes the
        # load path visibly continuous in a straight-on elevation.
        inner_z = 14.8 + 4.2 * (1.0 - (x / 44.0) ** 2) - 0.034 * -27.2
        add_beam(objects, f"TERMINAL_TreeColumnCrown_{index}", stem_top, (x, -27.2, inner_z), 0.31, mats["graphite"], cfg, "branching_steel_tree_column")
    # Central mast and radiating stays are one structural canopy assembly.
    add_cylinder(objects, "TERMINAL_CentralMast", 0.58, 27.2, (0.0, -6.0, 13.6), mats["graphite"], cfg, "central_cable_stay_mast", vertices=20)
    mast_top = (0.0, -6.0, 27.2)
    for stay_index, (x, y) in enumerate(((-42.0, -29.0), (-28.0, -29.0), (-14.0, -29.0), (14.0, -29.0), (28.0, -29.0), (42.0, -29.0), (-38.0, 18.0), (-19.0, 22.0), (19.0, 22.0), (38.0, 18.0))):
        z = 14.8 + 4.2 * (1.0 - (x / 44.0) ** 2) - 0.034 * y
        add_beam(objects, f"TERMINAL_StayCable_{stay_index}", mast_top, (x, y, z + 0.15), 0.055, mats["steel"], cfg, "radiating_structural_stay_cable")
    # Physical landside entry is part of the facade section, not a pasted card.
    add_box(objects, "TERMINAL_EntranceCanopyGlass", (24.0, 8.0, 0.18), (0.0, -29.0, 5.1), mats["roof_glass"], cfg, "integrated_glazed_departure_dropoff_canopy", bevel=0.04)
    for edge_x in (-12.0, 12.0):
        add_beam(objects, f"TERMINAL_EntranceCanopySide_{edge_x}", (edge_x, -33.0, 5.1), (edge_x, -25.0, 5.1), 0.10, mats["aluminum"], cfg, "entrance_canopy_edge_frame")
    for frame, x in enumerate((-12.0, -6.0, 0.0, 6.0, 12.0)):
        add_beam(objects, f"TERMINAL_EntranceCanopyRib_{frame}", (x, -33.0, 5.1), (x, -25.0, 5.1), 0.08, mats["aluminum"], cfg, "entrance_canopy_glazing_bar")
    for post, x in enumerate((-10.5, -3.5, 3.5, 10.5)):
        add_beam(objects, f"TERMINAL_EntranceCanopyPost_{post}", (x, -32.2, 0.25), (x, -32.2, 5.05), 0.11, mats["aluminum"], cfg, "entrance_canopy_column")
    for door in range(6):
        x = (door - 2.5) * 3.2
        add_box(objects, f"TERMINAL_AutomaticDoor_{door}", (2.65, 0.14, 3.7), (x, -25.18, 2.15), mats["glass"], cfg, "automatic_glazed_terminal_door")
        add_box(objects, f"TERMINAL_DoorHeader_{door}", (2.85, 0.26, 0.18), (x, -25.28, 4.05), mats["steel"], cfg, "terminal_door_frame")
    # Complete rear gate bridges prove the airside elevation and programme.
    for gate, x in enumerate((-25.0, 0.0, 25.0)):
        add_box(objects, f"TERMINAL_GateBridge_{gate}", (5.2, 15.0, 3.2), (x, 32.0, 7.2), mats["glass"], cfg, "complete_airside_gate_bridge", bevel=0.12)
        add_box(objects, f"TERMINAL_GateBridgeFloor_{gate}", (5.5, 15.2, 0.28), (x, 32.0, 5.72), mats["aluminum"], cfg, "airside_gate_bridge_floor")
        for segment in range(4):
            y = 26.6 + segment * 3.5
            add_beam(objects, f"TERMINAL_GateBridgeBraceA_{gate}_{segment}", (x - 2.5, y - 1.6, 5.9), (x + 2.5, y + 1.6, 8.5), 0.07, mats["steel"], cfg, "gate_bridge_diagonal_frame")
            add_beam(objects, f"TERMINAL_GateBridgeBraceB_{gate}_{segment}", (x + 2.5, y - 1.6, 5.9), (x - 2.5, y + 1.6, 8.5), 0.07, mats["steel"], cfg, "gate_bridge_diagonal_frame")
    add_box(objects, "TERMINAL_ServiceRoof", (28.0, 11.0, 0.42), (0.0, 8.0, 14.5), mats["roof"], cfg, "screened_terminal_service_roof", bevel=0.06)
    for unit, x in enumerate((-8.0, 0.0, 8.0)):
        add_box(objects, f"TERMINAL_RoofPlant_{unit}", (5.4, 3.6, 1.25), (x, 8.0, 15.2), mats["aluminum"], cfg, "screened_rooftop_plant", bevel=0.12)
    return objects


def build_assembled(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    if cfg["family"] == "vertical-forest-residential":
        return build_vertical_forest(mats, cfg)
    if cfg["family"] == "collegiate-gothic-gatehouse":
        return build_collegiate_gothic(mats, cfg)
    return build_airport_terminal(mats, cfg)


def build_module(
    role: str,
    variant: str,
    mats: dict,
    cfg: dict,
) -> tuple[list[bpy.types.Object], float]:
    objects: list[bpy.types.Object] = []
    family = cfg["family"]
    floor_height = cfg["floor_height"]
    if family == "vertical-forest-residential":
        if role == "podium":
            height = 4.20
            add_vertical_storey(objects, floor_index=0, base_z=0.0, storey_height=height, mats=mats, cfg=cfg, role=role, module_variant="typical_a")
            add_box(objects, "FOREST_MODULE_LobbyEntry", (6.8, 0.18, 3.2), (0.0, -14.05, 1.85), mats["glass"], cfg, "fixed_transparent_lobby_entry", role=role)
        elif role == "floor":
            height = floor_height
            add_vertical_storey(objects, floor_index={"typical_a": 2, "typical_b": 4, "typical_c": 7}[variant], base_z=0.0, storey_height=height, mats=mats, cfg=cfg, role=role, module_variant=variant)
        elif role == "crown":
            height = 1.20
            add_box(objects, "FOREST_MODULE_CrownSlab", (28.0, 28.0, 0.42), (0.0, 0.0, 0.21), mats["concrete"], cfg, "fixed_rooftop_garden_crown", role=role)
            for index, x in enumerate((-8.0, 0.0, 8.0)):
                add_vertical_planter(objects, prefix=f"FOREST_MODULE_CrownPlanter_{index}", centre=(x, -12.5, 0.42), size=(4.8, 1.4), tree_axis="x", floor_index=120 + index, mats=mats, cfg=cfg, role=role, tree=False)
        else:
            height = 4.0
            add_box(objects, "FOREST_MODULE_Roof", (28.0, 28.0, 0.45), (0.0, 0.0, 0.225), mats["roof"], cfg, "fixed_intensive_roof_garden", role=role)
            add_box(objects, "FOREST_MODULE_ServiceCore", (10.0, 9.0, 2.6), (0.0, 0.8, 1.75), mats["frame"], cfg, "screened_roof_service_core", role=role)
    elif family == "collegiate-gothic-gatehouse":
        width, depth = 60.0, 25.0
        if role == "podium":
            height = 4.8
            add_box(objects, "GOTHIC_MODULE_PodiumPaving", (width, depth, 0.18), (0.0, 0.0, 0.09), mats["paving"], cfg, "fixed_college_gate_podium", role=role)
            add_box(objects, "GOTHIC_MODULE_PodiumLeft", (26.5, 10.0, height), (-16.75, -7.5, height / 2), mats["stone"], cfg, "fixed_gatehouse_left_wing", role=role)
            add_box(objects, "GOTHIC_MODULE_PodiumRight", (26.5, 10.0, height), (16.75, -7.5, height / 2), mats["stone"], cfg, "fixed_gatehouse_right_wing", role=role)
            for sx in (-1.0, 1.0):
                add_beam(objects, f"GOTHIC_MODULE_GateArch_{sx}", (sx * 3.0, -12.8, 0.4), (0.0, -12.8, 4.6), 0.28, mats["carved"], cfg, "fixed_real_gate_arch", role=role)
        elif role == "floor":
            height = floor_height
            add_box(objects, f"GOTHIC_MODULE_FloorMass_{variant}", (width, depth, height), (0.0, 0.0, height / 2), mats["stone"], cfg, "repeatable_academic_wing", role=role)
            add_gothic_facade_y(objects, prefix=f"GOTHIC_MODULE_{variant}", width=width, y=-depth / 2 - 0.05, base_z=0.0, floors=1, floor_height=height, bays=11, outward_sign=-1.0, mats=mats, cfg=cfg, role=role)
        elif role == "crown":
            height = 2.2
            add_battlements(objects, prefix="GOTHIC_MODULE_Crown", width=width, depth=depth, base_z=0.0, mats=mats, cfg=cfg, role=role)
        else:
            height = 5.2
            create_gable_roof(objects, name="GOTHIC_MODULE_SlateRoof", centre=(0.0, 0.0), length=width, depth=depth, base_z=0.0, ridge_z=height, orientation="x", mat=mats["slate"], cfg=cfg, role=role)
    else:
        width, depth = 88.0, 60.0
        if role == "podium":
            height = 5.4
            add_box(objects, "TERMINAL_MODULE_Podium", (width, depth, 0.35), (0.0, 0.0, 0.175), mats["concrete"], cfg, "fixed_terminal_arrival_podium", role=role)
            add_terminal_glazed_wall_y(objects, prefix="TERMINAL_MODULE_PodiumFront", y=-depth / 2, width=width - 4.0, height=height, outward_sign=-1.0, mats=mats, cfg=cfg, role=role)
        elif role == "floor":
            height = floor_height
            add_box(objects, f"TERMINAL_MODULE_FloorPlate_{variant}", (width - 6.0, depth - 8.0, 0.40), (0.0, 0.0, 0.20), mats["concrete"], cfg, "repeatable_complete_terminal_concourse", role=role)
            add_terminal_glazed_wall_y(objects, prefix=f"TERMINAL_MODULE_{variant}", y=-depth / 2, width=width - 4.0, height=height, outward_sign=-1.0, mats=mats, cfg=cfg, role=role)
            if variant != "typical_a":
                for x in (-32.0, -16.0, 0.0, 16.0, 32.0):
                    add_beam(objects, f"TERMINAL_MODULE_Brace_{variant}_{x}", (x - 5.0, -30.3, 0.4), (x + 5.0, -30.3, height - 0.4), 0.15, mats["steel"], cfg, "terminal_structural_bay_variant", role=role)
        elif role == "crown":
            height = 2.0
            for x in range(-40, 41, 8):
                add_beam(objects, f"TERMINAL_MODULE_CrownTruss_{x}", (x, -30.0, 0.2), (x, 30.0, 1.8), 0.15, mats["steel"], cfg, "fixed_space_frame_crown", role=role)
        else:
            height = 13.0
            create_curved_terminal_roof(objects, mats=mats, cfg=cfg, role=role, width=width, depth=depth, base_z=2.4)
            add_cylinder(objects, "TERMINAL_MODULE_RoofMast", 0.52, height, (0.0, -6.0, height / 2), mats["graphite"], cfg, "fixed_cable_stay_roof_mast", vertices=18, role=role)
    for marker in module_contract_markers(role, variant, height):
        objects.append(tag_object(marker, "four_elevation_material_contract", cfg, role=role))
    return objects, height


def module_payload(
    role: str,
    variant: str,
    filename: str,
    height: float,
    objects: list[bpy.types.Object],
    size_bytes: int,
    skin: dict,
    cfg: dict,
) -> dict:
    repeatable = role == "floor"
    width, depth, actual_height = bounds_dimensions(objects)
    return {
        "role": role,
        "variant_key": variant,
        "assembly_class": "repeatable_middle" if repeatable else "fixed_semantic",
        "fixed_semantic": not repeatable,
        "lod": 0,
        "allowed_levels": [0, 1, 2],
        "filename": filename,
        "module_family": cfg["family"],
        "width_m": width,
        "depth_m": depth,
        "height_m": actual_height,
        "floor_height_m": cfg["floor_height"],
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
    cfg: dict,
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
        objects, height = build_module(role, variant, mats, cfg)
        normalize_bottom_centre(objects)
        suffix = role if variant == "default" else f"{role}_{variant}"
        filename = f"{cfg['family']}_{suffix}.glb"
        destination = folder / filename
        export_glb(destination, objects)
        payloads.append(module_payload(role, variant, filename, height, objects, destination.stat().st_size, skin, cfg))
        delete_objects(objects)
    return payloads


def configure_render(cfg: dict) -> list[bpy.types.Object]:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 980
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.12
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.66, 0.72, 0.76, 1.0)
    background.inputs["Strength"].default_value = 0.68
    presentation: list[bpy.types.Object] = []
    ground_mat = material("MAT_W12_PresentationGround", (0.43, 0.43, 0.41, 1.0), 0.92)
    presentation.append(box("PRESENTATION_W12_Ground", (260.0, 260.0, 0.10), (0.0, 0.0, -0.10), ground_mat))
    bpy.ops.object.light_add(type="SUN", location=(-90.0, -110.0, 130.0), rotation=(math.radians(28), math.radians(-16), math.radians(-38)))
    sun = bpy.context.object
    sun.name = "PRESENTATION_W12_Sun"
    sun.data.color = (1.0, 0.90, 0.79)
    sun.data.energy = 1.8
    sun.data.angle = math.radians(10.0)
    presentation.append(sun)
    target_z = cfg["native"][2] * 0.42
    for name, location, energy, size, color in (
        ("Key", (-75.0, -90.0, 85.0), 5600, 20.0, (1.0, 0.84, 0.72)),
        ("Fill", (82.0, -32.0, 55.0), 3900, 18.0, (0.70, 0.84, 1.0)),
        ("Rim", (0.0, 88.0, 72.0), 4800, 18.0, (0.78, 0.90, 1.0)),
    ):
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.name = f"PRESENTATION_W12_{name}"
        light.data.energy = energy
        light.data.shape = "DISK"
        light.data.size = size
        light.data.color = color
        light.rotation_euler = (Vector((0.0, 0.0, target_z)) - light.location).to_track_quat("-Z", "Y").to_euler()
        presentation.append(light)
    return presentation


def view_map(cfg: dict) -> dict[str, tuple[tuple[float, float, float], tuple[float, float, float], float]]:
    family = cfg["family"]
    if family == "vertical-forest-residential":
        return {
            "preview": ((96.0, -128.0, 78.0), (0.0, 0.0, 32.0), 48),
            "front_corner_oblique": ((88.0, -117.0, 64.0), (0.0, 0.0, 32.0), 50),
            "front_elevation": ((0.0, -170.0, 39.0), (0.0, 0.0, 33.0), 54),
            "rear_corner_oblique": ((-62.0, 74.0, 48.0), (0.0, 0.0, 28.0), 58),
            "aerial": ((91.0, -88.0, 122.0), (0.0, 0.0, 24.0), 53),
            "facade_close": ((24.0, -39.0, 28.0), (7.0, -8.0, 26.0), 72),
            "identity_close": ((30.0, -42.0, 51.0), (8.0, -8.0, 49.0), 74),
            "street": ((53.0, -91.0, 12.0), (0.0, 0.0, 27.0), 64),
            "context": ((90.0, -106.0, 78.0), (0.0, 0.0, 24.0), 52),
        }
    if family == "collegiate-gothic-gatehouse":
        return {
            "preview": ((78.0, -103.0, 49.0), (0.0, -4.0, 12.0), 57),
            "front_corner_oblique": ((72.0, -95.0, 39.0), (0.0, -5.0, 11.0), 60),
            "front_elevation": ((0.0, -128.0, 18.0), (0.0, -6.0, 13.0), 63),
            "rear_corner_oblique": ((-76.0, 88.0, 43.0), (0.0, 3.0, 10.0), 58),
            "aerial": ((82.0, -76.0, 88.0), (0.0, 0.0, 8.0), 55),
            "facade_close": ((25.0, -52.0, 14.0), (8.0, -18.0, 10.0), 70),
            "identity_close": ((15.0, -48.0, 18.0), (0.0, -20.0, 11.0), 72),
            "street": ((62.0, -116.0, 9.5), (0.0, -5.0, 12.0), 65),
            "context": ((112.0, -128.0, 67.0), (0.0, 0.0, 9.0), 52),
        }
    return {
        "preview": ((113.0, -139.0, 66.0), (0.0, -2.0, 9.0), 57),
        "front_corner_oblique": ((104.0, -129.0, 48.0), (0.0, -4.0, 8.0), 60),
        "front_elevation": ((0.0, -164.0, 20.0), (0.0, -5.0, 10.0), 63),
        "rear_corner_oblique": ((-112.0, 124.0, 55.0), (0.0, 6.0, 8.0), 58),
        "aerial": ((118.0, -108.0, 112.0), (0.0, 0.0, 5.0), 55),
        "facade_close": ((42.0, -65.0, 18.0), (14.0, -23.0, 9.0), 72),
        "identity_close": ((34.0, -61.0, 26.0), (0.0, -12.0, 18.0), 74),
        "street": ((91.0, -145.0, 12.0), (0.0, -5.0, 9.0), 65),
        "context": ((145.0, -162.0, 88.0), (0.0, 2.0, 6.0), 52),
    }


def render_views(folder: Path, cfg: dict, *, view_set: str) -> list[str]:
    presentation = configure_render(cfg)
    views = view_map(cfg)
    selected = {
        "preview": {"preview"},
        "pilot": {"preview", "front_corner_oblique", "front_elevation", "aerial", "facade_close", "identity_close"},
        "all": set(views),
    }.get(view_set, {view_set})
    rendered: list[str] = []
    for role, (location, target, lens) in views.items():
        if role not in selected:
            continue
        aim_camera(location, target, lens)
        filename = f"{cfg['family']}_{role}.png"
        bpy.context.scene.render.filepath = str(folder / filename)
        bpy.ops.render.render(write_still=True)
        rendered.append(filename)
    delete_objects(presentation)
    return rendered


def footprint_contract(cfg: dict) -> dict:
    family = cfg["family"]
    if family == "vertical-forest-residential":
        profiles = {
            "rectangle": {"recommendedWidth_m": [21.0, 40.0], "recommendedDepth_m": [21.0, 40.0], "recommendedFloors": [10, 30], "scaleMin": 0.72, "scaleMax": 1.30, "maxAxisRatio": 1.16, "preferredBayMultiple_m": 5.5},
            "courtyard": {"recommendedWidth_m": [28.0, 48.0], "recommendedDepth_m": [28.0, 48.0], "recommendedFloors": [10, 26], "scaleMin": 0.76, "scaleMax": 1.28, "maxAxisRatio": 1.18, "preferredBayMultiple_m": 5.5, "minimumCourtyard_m": 8.0},
        }
        preferred = ["rectangle", "courtyard"]
        rationale = "The fixed planted tower accepts ordinary near-square drawing error. Larger rectangles or courtyard drawings repeat complete 5.5 metre occupied balcony bays with their slab, pane, planter and vegetation, never a stretched tree or window."
    elif family == "collegiate-gothic-gatehouse":
        profiles = {
            "rectangle": {"recommendedWidth_m": [45.0, 82.0], "recommendedDepth_m": [22.0, 48.0], "recommendedFloors": [2, 6], "scaleMin": 0.74, "scaleMax": 1.28, "maxAxisRatio": 1.22, "preferredBayMultiple_m": 5.45},
            "u_shape": {"recommendedWidth_m": [48.0, 86.0], "recommendedDepth_m": [30.0, 55.0], "recommendedFloors": [2, 6], "scaleMin": 0.72, "scaleMax": 1.30, "maxAxisRatio": 1.24, "preferredBayMultiple_m": 5.45, "wingDepth_m": [8.0, 14.0]},
            "courtyard": {"recommendedWidth_m": [52.0, 90.0], "recommendedDepth_m": [34.0, 60.0], "recommendedFloors": [2, 6], "scaleMin": 0.72, "scaleMax": 1.30, "maxAxisRatio": 1.24, "preferredBayMultiple_m": 5.45, "wingDepth_m": [8.0, 14.0], "minimumCourtyard_m": 12.0},
        }
        preferred = ["rectangle", "u_shape", "courtyard"]
        rationale = "The gate tower, real passage, corner returns and roof terminals remain fixed while complete 5.45 metre academic bays repeat along rectangle, U-shaped or courtyard wings. Tracery and buttresses are never stretched across openings."
    else:
        profiles = {
            "rectangle": {"recommendedWidth_m": [62.0, 135.0], "recommendedDepth_m": [42.0, 92.0], "recommendedFloors": [2, 6], "scaleMin": 0.70, "scaleMax": 1.32, "maxAxisRatio": 1.24, "preferredBayMultiple_m": 6.83},
            "l_shape": {"recommendedWidth_m": [68.0, 150.0], "recommendedDepth_m": [44.0, 105.0], "recommendedFloors": [2, 6], "scaleMin": 0.68, "scaleMax": 1.34, "maxAxisRatio": 1.26, "preferredBayMultiple_m": 6.83, "wingDepth_m": [22.0, 38.0]},
        }
        preferred = ["rectangle", "l_shape"]
        rationale = "The reviewed mast, cable fan, tree columns and canopy remain one fixed landmark inside a broad transport scale band. Oversized rectangles or L-shaped concourses repeat complete 6.83 metre glazed structural bays and gate bridges along the long axis."
    primary = profiles["rectangle"]
    return {
        "preferredProfiles": preferred,
        "minimumPreferredProfiles": len(preferred),
        "profileRationale": rationale,
        "fixedLandmarkScaleBand": {"scaleMin": primary["scaleMin"], "scaleMax": primary["scaleMax"], "maxAxisRatio": primary["maxAxisRatio"]},
        "recommendedWidth_m": primary["recommendedWidth_m"],
        "recommendedDepth_m": primary["recommendedDepth_m"],
        "recommendedFloors": primary["recommendedFloors"],
        "preferredBayMultiple_m": primary["preferredBayMultiple_m"],
        "scaleMin": primary["scaleMin"],
        "scaleMax": primary["scaleMax"],
        "maxAxisRatio": primary["maxAxisRatio"],
        "profiles": profiles,
    }


def massing_graph(cfg: dict) -> dict:
    family = cfg["family"]
    if family == "vertical-forest-residential":
        return {"type": "fixed_vertical_forest_tower_with_repeatable_complete_balcony_storeys", "occupied_storeys": 18, "continuous_perimeter_frame": True, "deep_balcony_trays": 18, "integral_planter_volumes": True, "three_dimensional_supported_trees": True, "intensive_rooftop_garden": True, "physical_window_layers": ["occupied_depth", "neutral_low_iron_pane", "bronze_frame", "slab_edge", "external_concrete_frame"]}
    if family == "collegiate-gothic-gatehouse":
        return {"type": "fixed_tudor_college_quadrangle_with_repeatable_academic_bays", "open_quadrangle": True, "gate_towers": 1, "real_through_passages": 1, "academic_wings": 4, "steep_slate_gable_fields": 4, "pointed_traceried_window_bays": 38, "clustered_chimney_stacks": 4, "physical_window_layers": ["occupied_depth", "leaded_pane", "stone_tracery", "deep_reveal", "buttress"]}
    return {"type": "fixed_cable_stayed_terminal_with_repeatable_structural_concourse_bays", "transparent_departure_halls": 2, "branching_tree_columns": 6, "central_stay_masts": 1, "radiating_stay_cables": 10, "sweeping_space_frame_canopies": 1, "diamond_braced_side_walls": 2, "complete_airside_gate_bridges": 3, "physical_window_layers": ["occupied_terminal_depth", "high_transmission_pane", "pressure_cap", "mezzanine", "external_structure"]}


def facade_sheet_contract(skin: dict, cfg: dict) -> dict:
    family = cfg["family"]
    contract = facade_contract(family, skin, f"/families/{family}/textures/source/archetype-goalpost.png")
    contract["geometry_detail_profile"] = "hero"
    if family == "vertical-forest-residential":
        contract["bay_strategy"] = {"fixed_end_bays": ["transparent_planted_lobby", "continuous_perimeter_frame", "intensive_rooftop_garden"], "repeatable_middle_bays": list(range(17)), "middle_variants": ["typical_a", "typical_b", "typical_c"], "rule": "Repeat complete planted residential storeys: slab, pane, frame, planter, soil, support and tree remain one semantic bay."}
        coverage = {"front": "continuous concrete frame, irregular deep planters and occupied recessed glass", "left": "wrapped planted balcony construction", "right": "wrapped planted balcony construction", "rear": "complete occupied secondary elevation with real planters", "roof": "intensive roof garden around screened service core"}
        fixed = ["podium/entrance", "corner returns", "crown", "roof", "planted transparent lobby", "continuous frame", "corner balcony returns", "roof garden", "service core"]
    elif family == "collegiate-gothic-gatehouse":
        contract["bay_strategy"] = {"fixed_end_bays": ["real_gate_passage", "gate_tower", "corner_buttresses", "roof_terminals"], "repeatable_middle_bays": list(range(11)), "middle_variants": ["typical_a", "typical_b", "typical_c"], "rule": "Repeat whole 5.45 metre academic bays with pier, deep pointed opening, leaded pane, tracery and buttress datum."}
        coverage = {"front": "real carved gate passage beneath traceried crenellated tower", "left": "complete academic wing with pointed glazing and slate gable", "right": "complete academic wing with pointed glazing and slate gable", "rear": "occupied fourth wing and clustered chimneys", "roof": "four connected slate gable fields, tower parapet, pinnacles and chimneys"}
        fixed = ["podium/entrance", "corner returns", "crown", "roof", "gate passage", "gate tower", "ceremonial stair", "corner buttresses", "slate roof fields", "pinnacles and chimneys"]
    else:
        contract["bay_strategy"] = {"fixed_end_bays": ["central_mast", "radiating_stays", "branching_tree_columns", "three_gate_bridges"], "repeatable_middle_bays": list(range(12)), "middle_variants": ["typical_a", "typical_b", "typical_c"], "rule": "Repeat complete 6.83 metre terminal structural bays, including pane, cap, occupied depth, slab and optional diagonal brace."}
        coverage = {"front": "transparent departure hall, integrated drop-off canopy and branching columns", "left": "diamond-braced occupied terminal enclosure", "right": "diamond-braced occupied terminal enclosure", "rear": "complete airside curtain wall and three gate bridges", "roof": "sweeping translucent space frame, central mast, cables and service roof"}
        fixed = ["podium/entrance", "corner returns", "crown", "roof", "central mast", "stay cable fan", "branching columns", "arrival canopy", "side enclosure returns", "sweeping roof", "three gate bridges"]
    contract["assembly_contract"] = {"fixed": fixed, "repeatable": ["typical_a", "typical_b", "typical_c"], "side_elevations": coverage["left"] + "; " + coverage["right"], "elevation_coverage": coverage, "variation_policy": "Use the complete fixed landmark inside its independent-axis scale band. Oversized or differently proportioned targets use long-axis streetwall repeat of complete semantic bays, never family_incompatible."}
    return contract


def promote_catalogue_thumbnail(folder: Path, cfg: dict) -> None:
    preview = folder / f"{cfg['family']}_preview.png"
    if not preview.is_file():
        return
    catalogue = folder.parents[1] / "archetypes" / "buildings" / cfg["catalogue_slug"]
    catalogue.mkdir(parents=True, exist_ok=True)
    shutil.copy2(preview, catalogue / "hero.png")
    index = cfg.get("catalogue_variant_index")
    if index is not None:
        shutil.copy2(preview, catalogue / f"variant_{index}.png")


def build_family(
    output_root: Path,
    cfg: dict,
    *,
    view_set: str,
    skip_renders: bool,
    skip_modules: bool,
    skip_assembled_export: bool,
) -> None:
    clear_scene()
    family = cfg["family"]
    folder = (output_root / family).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    mats, skin = load_palette(folder, cfg)
    objects = build_assembled(mats, cfg)
    normalize_bottom_centre(objects)
    actual_native = bounds_dimensions(objects)
    assembled_path = folder / f"{family}_assembled.glb"
    manifest_path = folder / f"{family}_manifest.json"
    previous = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}
    if not skip_assembled_export:
        export_glb(assembled_path, objects)
        assembled_triangles = evaluated_triangle_count(objects)
        assembled_materials = material_count(objects)
    else:
        assembled_triangles = int((previous.get("assembled") or {}).get("triangle_count") or evaluated_triangle_count(objects))
        assembled_materials = int((previous.get("assembled") or {}).get("material_count") or material_count(objects))
    renders = list(previous.get("renders") or []) if skip_renders else render_views(folder, cfg, view_set=view_set)
    delete_objects(objects)
    modules = list(previous.get("modules") or []) if skip_modules else build_modules(folder, mats, skin, cfg)
    footprint = footprint_contract(cfg)
    graph = massing_graph(cfg)
    width, depth, height = actual_native
    assembled = {
        "filename": assembled_path.name,
        "module_family": family,
        "assembly_class": "fixed_landmark",
        "fixed_semantic": True,
        "repeatable_z": False,
        "source_variant_id": cfg["variant_id"],
        "generation_archetype_id": cfg["variant_id"],
        "width_m": width,
        "depth_m": depth,
        "floors": cfg["native_floors"],
        "uses_setback": True,
        "uses_crown": True,
        "height_m": height,
        "triangle_count": assembled_triangles,
        "material_count": assembled_materials,
        "stack": [{"role": "assembled", "variant_key": "reference_locked", "level": 0, "z_m": 0.0, "height_m": height}],
        "footprint_profile": "courtyard" if family == "collegiate-gothic-gatehouse" else "rectangle",
        "footprint_target": {"width_m": width, "depth_m": depth, "segments": [{"id": "complete_fixed_landmark", "centre_x_m": 0.0, "centre_y_m": 0.0, "length_m": width, "thickness_m": depth, "rotation_degrees": 0.0}]},
        "massing_graph": graph,
        "texture_keys": sorted(skin["zones"]),
        "ao_baked": True,
    }
    aliases = cfg["aliases"]
    manifest = {
        "manifest_schema": 3,
        "grammar_schema_version": 3,
        "generator": {"name": "archetype_compiler/generate_wave12_diverse_families.py", "version": "1.0.0", "blender_version": bpy.app.version_string, "render_engine": "BLENDER_EEVEE"},
        "created_at": datetime.now(timezone.utc).isoformat(),
        "family": family,
        "archetype_id": cfg["archetype_id"],
        "archetype_label": cfg["label"],
        "variant_id": cfg["variant_id"],
        "generation_archetype_id": cfg["variant_id"],
        "archetype_aliases": aliases,
        "aesthetic_category_id": cfg["aesthetic"],
        "development_type": cfg["development_type"],
        "reuse_keys": [*aliases, *cfg["reuse_keys"]],
        "generation_tags": ["wave12", "fixed_landmark_and_modular_fallback", "custom_pbr_skin", "physical_separate_glazing", "occupied_interior_depth", "complete_semantic_bay_repeat", *( ["real_planter_volumes", "three_dimensional_supported_trees", "deep_balcony_trays"] if family == "vertical-forest-residential" else ["real_gate_passage", "carved_pointed_tracery", "steep_slate_roofs"] if family == "collegiate-gothic-gatehouse" else ["sweeping_space_frame", "branching_tree_columns", "radiating_stay_cables", "complete_gate_bridges"] )],
        "footprint_compatibility": footprint,
        "coordinate_contract": COORDINATE_CONTRACT,
        "textures": texture_inventory(skin),
        "facade_sheet": facade_sheet_contract(skin, cfg),
        "massing_graph": graph,
        "material_budget": {"max_assembled_materials": 18, "rationale": "Opaque construction, physical glazing, occupied depth, structure, roof and landscape retain distinct physically based responses because their contrast carries each archetype identity."},
        "dimensions": {"width_m": width, "depth_m": depth, "podium_height_m": 4.2 if family == "vertical-forest-residential" else 4.8 if family == "collegiate-gothic-gatehouse" else 5.4, "floor_height_m": cfg["floor_height"], "setback_height_m": cfg["floor_height"], "roof_height_m": 4.0 if family == "vertical-forest-residential" else 5.2 if family == "collegiate-gothic-gatehouse" else 13.0, "crown_height_m": 1.2 if family == "vertical-forest-residential" else 2.2 if family == "collegiate-gothic-gatehouse" else 2.0, "default_floors": cfg["native_floors"], "min_floors": cfg["min_floors"], "max_floors": cfg["max_floors"]},
        "native_width_m": width,
        "native_depth_m": depth,
        "native_height_m": height,
        "native_floors": cfg["native_floors"],
        "min_floors": cfg["min_floors"],
        "max_floors": cfg["max_floors"],
        "default_floors": cfg["native_floors"],
        "modules": modules,
        "assembled": assembled,
        "thumbnail": f"{family}_preview.png",
        "renders": renders,
        "architectural_identity": cfg["identity"],
        "material_zones": cfg["material_zones"],
        "glass_profile": cfg["glass_profile"],
        "source_provenance": {"catalogue_archetype_id": cfg["archetype_id"], "catalogue_variant_id": cfg["variant_id"], "catalogue_alias_ids": aliases[2:], "elevation_source": f"/families/{family}/elevation.jpg", "goalpost": f"/families/{family}/textures/source/archetype-goalpost.png", "reference_generation": f"/families/{family}/textures/source/reference-generation.json", "method": "reference-locked four-view source board, six-zone material construction plate, deterministic metric envelope, physical layered glazing, occupied depth, complete secondary elevations and semantic LEGO fallback modules"},
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    grammar = {"family_id": family, "source": {"archetype_id": cfg["archetype_id"], "variant_id": cfg["variant_id"], "generation_archetype_id": cfg["variant_id"], "reuse_keys": manifest["reuse_keys"]}, "dimensions": manifest["dimensions"], "architectural_signature": {"identity": cfg["identity"], "material_zones": cfg["material_zones"], "glass_profile": cfg["glass_profile"], "kits": ["reference_locked_fixed_landmark", "physical_layered_glazing", "occupied_interior_depth", "semantic_repeatable_middle_bays", "fixed_crown_and_roof_kit"]}, "archetype_aliases": aliases, "footprint_compatibility": footprint, "massing_graph": graph}
    (folder / "grammar.json").write_text(json.dumps(grammar, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (folder / "archetype-source.json").write_text(json.dumps(manifest["source_provenance"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    promote_catalogue_thumbnail(folder, cfg)
    print(f"[wave12] {family}: {assembled_triangles} triangles, {assembled_materials} materials, {len(modules)} modules, {len(renders)} renders, native={actual_native}", flush=True)


def render_existing(output_root: Path, cfg: dict, *, view_set: str) -> None:
    clear_scene()
    folder = (output_root / cfg["family"]).resolve()
    mats, _skin = load_palette(folder, cfg)
    objects = build_assembled(mats, cfg)
    normalize_bottom_centre(objects)
    rendered = render_views(folder, cfg, view_set=view_set)
    delete_objects(objects)
    promote_catalogue_thumbnail(folder, cfg)
    print(f"[wave12] {cfg['family']}: rendered {len(rendered)} views", flush=True)


def main() -> int:
    args = parse_args()
    cfg = dict(FAMILIES[args.family])
    cfg["family"] = args.family
    if args.render_existing:
        render_existing(args.output_root, cfg, view_set=args.view_set)
    else:
        build_family(args.output_root, cfg, view_set=args.view_set, skip_renders=args.skip_renders, skip_modules=args.skip_modules, skip_assembled_export=args.skip_assembled_export)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
