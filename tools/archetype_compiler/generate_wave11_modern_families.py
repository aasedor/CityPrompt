"""Generate the two reference-locked modern Wave 11 LEGO families.

The skyline cluster is a fixed three-tower landmark with physical curtain-wall
layers, two enclosed skybridges, stepped glazed crowns and a transparent shared
podium.  The technology campus is a fixed U-shaped pavilion composition with
an expressed white frame, occupied low-iron glazing, courtyard, canopy roofs,
photovoltaics and a screened penthouse.  Both also ship semantic stack modules
for ordinary hand-drawn size variation.

Run from the repository root with Blender 5.x::

    blender --background --factory-startup --python \
      tools/archetype_compiler/generate_wave11_modern_families.py -- \
      --family skyline-glass-office-cluster \
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


FAMILIES: dict[str, dict] = {
    "skyline-glass-office-cluster": {
        "archetype_id": "skyline_glass_office_cluster",
        "variant_id": "skyline_cluster_staggered",
        "aliases": [
            "skyline_glass_office_cluster",
            "skyline_cluster_staggered",
            "staggered_glass_office_cluster",
            "three_tower_skybridge_cluster",
        ],
        "label": "Skyline Glass Office Cluster - Staggered",
        "aesthetic": "contemporary_corporate",
        "development_type": "office",
        "glass_profile": "neutral_low_e_office_curtain_wall",
        "native": (70.0, 40.0, 76.1),
        "native_floors": 17,
        "min_floors": 8,
        "max_floors": 30,
        "floor_height": 3.65,
        "identity": (
            "Exactly three staggered silver-blue curtain-wall office towers rise "
            "from one transparent civic podium, linked by two enclosed glazed "
            "skybridges and finished with stepped glass lantern crowns."
        ),
        "material_zones": (
            "neutral blue-grey low-e vision glass; physical silver anodized "
            "aluminum pressure caps; charcoal glass spandrels; pale honed podium "
            "stone and plaza paving; graphite bridge trusses; warm occupied "
            "office depth; dark low-slope roofs"
        ),
        "reuse_keys": [
            "Skyline Glass Office Cluster",
            "Staggered Office Towers",
            "Three Tower Office Complex",
            "Skybridge Office Campus",
        ],
    },
    "autonomous-tech-campus-silicon-valley": {
        "archetype_id": "autonomous_tech_campus",
        "variant_id": "tech_campus_silicon_valley",
        "aliases": [
            "autonomous_tech_campus",
            "tech_campus_silicon_valley",
            "silicon_valley_research_campus",
            "white_steel_technology_pavilions",
        ],
        "label": "Autonomous Tech Campus - Silicon Valley Pavilion",
        "aesthetic": "contemporary_research",
        "development_type": "research_and_development",
        "glass_profile": "low_iron_research_pavilion",
        "native": (74.0, 54.0, 13.4),
        "native_floors": 3,
        "min_floors": 2,
        "max_floors": 7,
        "floor_height": 4.10,
        "identity": (
            "Three connected low-rise research pavilions form a planted U-shaped "
            "courtyard behind a warm-white external steel frame, full-height "
            "occupied glass, broad canopy roofs and photovoltaic arrays."
        ),
        "material_zones": (
            "neutral low-iron research glass; warm-white powder-coated external "
            "steel; pale architectural precast; warm occupied laboratory depth; "
            "blue-black photovoltaic cells; cool pale roof membrane and concrete "
            "pavers; restrained bioswale planting"
        ),
        "reuse_keys": [
            "Autonomous Tech Campus",
            "Silicon Valley Research Pavilion",
            "Low Rise Technology Campus",
            "White Steel Laboratory Campus",
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
            "bridge_close",
            "courtyard_close",
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


def configure_glass(
    mat: bpy.types.Material,
    cfg: dict,
    *,
    transmission: float,
    alpha: float,
    tint: tuple[float, float, float],
) -> bpy.types.Material:
    bsdf = bsdf_for(mat)
    base_color = bsdf.inputs["Base Color"]
    if base_color.is_linked:
        source = base_color.links[0].from_socket
        mat.node_tree.links.remove(base_color.links[0])
        wash = mat.node_tree.nodes.new("ShaderNodeMixRGB")
        wash.name = wash.label = "PHYSICAL_GLASS_TINT_WASH"
        wash.blend_type = "MIX"
        wash.inputs[0].default_value = 0.58
        wash.inputs[2].default_value = (*tint, 1.0)
        mat.node_tree.links.new(source, wash.inputs[1])
        mat.node_tree.links.new(wash.outputs["Color"], base_color)
    bsdf.inputs["Roughness"].default_value = 0.085
    if bsdf.inputs.get("Transmission Weight"):
        bsdf.inputs["Transmission Weight"].default_value = transmission
    if bsdf.inputs.get("Coat Weight"):
        bsdf.inputs["Coat Weight"].default_value = 0.34
    if bsdf.inputs.get("Coat Roughness"):
        bsdf.inputs["Coat Roughness"].default_value = 0.045
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


def configure_occupied_depth(
    mat: bpy.types.Material,
    *,
    warm_color: tuple[float, float, float],
    warmth: float,
    emission: float,
) -> bpy.types.Material:
    """Keep the authored interior image while restoring believable warm depth."""
    bsdf = bsdf_for(mat)
    base_color = bsdf.inputs["Base Color"]
    if base_color.is_linked:
        source = base_color.links[0].from_socket
        mat.node_tree.links.remove(base_color.links[0])
        mix = mat.node_tree.nodes.new("ShaderNodeMixRGB")
        mix.name = mix.label = "OCCUPIED_DEPTH_WARMTH"
        mix.blend_type = "ADD"
        mix.inputs[0].default_value = warmth
        mix.inputs[2].default_value = (*warm_color, 1.0)
        mat.node_tree.links.new(source, mix.inputs[1])
        mat.node_tree.links.new(mix.outputs["Color"], base_color)
        emission_color = bsdf.inputs.get("Emission Color")
        if emission_color:
            while emission_color.is_linked:
                mat.node_tree.links.remove(emission_color.links[0])
            mat.node_tree.links.new(mix.outputs["Color"], emission_color)
            bsdf.inputs["Emission Strength"].default_value = emission
    mat["occupied_depth_layer"] = True
    mat["warmth_reference_locked"] = True
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
        emission_strength: float = 0.0,
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
            emission_strength=emission_strength,
        )
        grade_material(result, saturation=saturation, value=value)
        set_normal_strength(result, normal)
        result["source_variant_id"] = cfg["variant_id"]
        result["generation_archetype_id"] = cfg["variant_id"]
        result["reference_locked"] = True
        return result

    family = cfg["family"]
    if family == "skyline-glass-office-cluster":
        mats = {
            "glass": configure_glass(
                pbr(
                    "vision_glass",
                    "MAT_W11_SKYLINE_NeutralLowEVisionGlass",
                    transmission=0.52,
                    saturation=0.30,
                    value=1.06,
                    normal=0.08,
                ),
                cfg,
                transmission=0.80,
                alpha=0.34,
                tint=(0.45, 0.57, 0.64),
            ),
            "frame": pbr(
                "aluminum",
                "MAT_W11_SKYLINE_SilverAnodizedAluminum",
                metallic=0.72,
                saturation=0.22,
                value=0.96,
                normal=0.18,
            ),
            "spandrel": pbr(
                "spandrel",
                "MAT_W11_SKYLINE_CharcoalGlassSpandrel",
                saturation=0.36,
                value=0.64,
                normal=0.10,
            ),
            "stone": pbr(
                "stone",
                "MAT_W11_SKYLINE_PalePodiumStone",
                saturation=0.42,
                value=0.83,
                normal=0.32,
            ),
            "steel": pbr(
                "steel",
                "MAT_W11_SKYLINE_GraphiteStructuralSteel",
                metallic=0.58,
                saturation=0.24,
                value=0.38,
                normal=0.20,
            ),
            "plaza": pbr(
                "plaza",
                "MAT_W11_SKYLINE_CivicPlazaPaving",
                saturation=0.36,
                value=0.78,
                normal=0.30,
            ),
            "roof": pbr(
                "roof",
                "MAT_W11_SKYLINE_LowSlopeRoof",
                saturation=0.25,
                value=0.48,
                normal=0.22,
            ),
            "interior": pbr(
                "interior",
                "MAT_W11_SKYLINE_OccupiedOfficeDepth",
                emission_strength=0.64,
                saturation=0.70,
                value=0.98,
                normal=0.08,
            ),
        }
        mats["core"] = material(
            "MAT_W11_SKYLINE_WarmCore",
            (0.19, 0.20, 0.20, 1.0),
            0.76,
        )
        configure_occupied_depth(
            mats["interior"],
            warm_color=(0.44, 0.24, 0.10),
            warmth=0.16,
            emission=0.30,
        )
        mats["green"] = material(
            "MAT_W11_SKYLINE_PlanterGreen",
            (0.16, 0.26, 0.12, 1.0),
            0.78,
        )
        mats["wood"] = material(
            "MAT_W11_SKYLINE_TreeTrunk",
            (0.22, 0.14, 0.075, 1.0),
            0.84,
        )
    else:
        mats = {
            "glass": configure_glass(
                pbr(
                    "glass",
                    "MAT_W11_CAMPUS_NeutralLowIronGlass",
                    transmission=0.58,
                    saturation=0.30,
                    value=1.02,
                    normal=0.07,
                ),
                cfg,
                transmission=0.80,
                alpha=0.33,
                tint=(0.48, 0.57, 0.60),
            ),
            "frame": pbr(
                "white_steel",
                "MAT_W11_CAMPUS_WarmWhitePowderCoatedSteel",
                metallic=0.30,
                saturation=0.24,
                value=0.97,
                normal=0.16,
            ),
            "precast": pbr(
                "precast",
                "MAT_W11_CAMPUS_PaleArchitecturalPrecast",
                saturation=0.36,
                value=0.84,
                normal=0.36,
            ),
            "pv": pbr(
                "photovoltaic",
                "MAT_W11_CAMPUS_BlueBlackPhotovoltaicCells",
                metallic=0.32,
                saturation=0.70,
                value=0.48,
                normal=0.12,
            ),
            "paving": pbr(
                "paving",
                "MAT_W11_CAMPUS_PaleConcretePavers",
                saturation=0.30,
                value=0.82,
                normal=0.34,
            ),
            "roof": pbr(
                "roof",
                "MAT_W11_CAMPUS_CoolRoofMembrane",
                saturation=0.20,
                value=0.86,
                normal=0.20,
            ),
            "landscape": pbr(
                "landscape",
                "MAT_W11_CAMPUS_BioswaleGroundcover",
                saturation=0.65,
                value=0.58,
                normal=0.34,
            ),
            "interior": pbr(
                "interior",
                "MAT_W11_CAMPUS_OccupiedLaboratoryDepth",
                emission_strength=0.76,
                saturation=0.84,
                value=1.06,
                normal=0.08,
            ),
        }
        mats["dark"] = material(
            "MAT_W11_CAMPUS_GraphiteScreen",
            (0.16, 0.17, 0.17, 1.0),
            0.62,
            metallic=0.38,
        )
        configure_occupied_depth(
            mats["interior"],
            warm_color=(0.50, 0.25, 0.085),
            warmth=0.20,
            emission=0.34,
        )
        mats["green"] = material(
            "MAT_W11_CAMPUS_Foliage",
            (0.16, 0.30, 0.12, 1.0),
            0.78,
        )
        mats["green_alt"] = material(
            "MAT_W11_CAMPUS_FoliageSilver",
            (0.27, 0.39, 0.19, 1.0),
            0.80,
        )
        groundcover = material(
            "MAT_W11_CAMPUS_LayeredBioswaleGroundcover",
            (0.13, 0.27, 0.08, 1.0),
            0.86,
        )
        ground_nodes = groundcover.node_tree.nodes
        ground_links = groundcover.node_tree.links
        ground_bsdf = bsdf_for(groundcover)
        noise = ground_nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 1.15
        noise.inputs["Detail"].default_value = 4.2
        noise.inputs["Roughness"].default_value = 0.72
        ramp = ground_nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.23
        ramp.color_ramp.elements[0].color = (0.045, 0.115, 0.025, 1.0)
        ramp.color_ramp.elements[1].position = 0.78
        ramp.color_ramp.elements[1].color = (0.25, 0.40, 0.105, 1.0)
        bump = ground_nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.22
        bump.inputs["Distance"].default_value = 0.08
        ground_links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
        ground_links.new(ramp.outputs["Color"], ground_bsdf.inputs["Base Color"])
        ground_links.new(noise.outputs["Fac"], bump.inputs["Height"])
        ground_links.new(bump.outputs["Normal"], ground_bsdf.inputs["Normal"])
        mats["groundcover"] = groundcover
        mats["wood"] = material(
            "MAT_W11_CAMPUS_TreeTrunk",
            (0.23, 0.15, 0.075, 1.0),
            0.84,
        )
    return mats, skin


def tag_object(
    obj: bpy.types.Object,
    semantic: str,
    cfg: dict,
    *,
    role: str = "assembled",
) -> bpy.types.Object:
    obj["semantic"] = semantic
    obj["module_role"] = role
    obj["source_variant_id"] = cfg["variant_id"]
    obj["generation_archetype_id"] = cfg["variant_id"]
    obj["reference_locked"] = True
    return obj


def metric_uv(obj: bpy.types.Object, tile_m: float = 2.8) -> None:
    if obj.type != "MESH" or not obj.data.polygons:
        return
    layer = obj.data.uv_layers.active or obj.data.uv_layers.new(name="UVMap")
    for poly in obj.data.polygons:
        normal = poly.normal
        for loop_index in poly.loop_indices:
            co = obj.data.vertices[obj.data.loops[loop_index].vertex_index].co
            if abs(normal.z) > 0.72:
                u, v = co.x / tile_m, co.y / tile_m
            elif abs(normal.y) > abs(normal.x):
                u, v = co.x / tile_m, co.z / tile_m
            else:
                u, v = co.y / tile_m, co.z / tile_m
            layer.data[loop_index].uv = (u, v)


def b(
    name: str,
    size: tuple[float, float, float],
    location: tuple[float, float, float],
    mat: bpy.types.Material,
    cfg: dict,
    *,
    bevel: float = 0.028,
    semantic: str = "construction",
    role: str = "assembled",
    tile_m: float = 2.8,
) -> bpy.types.Object:
    # Direct mesh creation avoids one operator + transform-apply cycle for
    # every curtain-wall pane.  The physical geometry and metric UVs are
    # identical, but a multi-thousand-part tower now builds in seconds rather
    # than spending minutes in Blender's context-dependent operator stack.
    sx, sy, sz = (dimension / 2 for dimension in size)
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(
        [
            (-sx, -sy, -sz),
            (sx, -sy, -sz),
            (sx, sy, -sz),
            (-sx, sy, -sz),
            (-sx, -sy, sz),
            (sx, -sy, sz),
            (sx, sy, sz),
            (-sx, sy, sz),
        ],
        [],
        [
            (0, 3, 2, 1),
            (4, 5, 6, 7),
            (0, 1, 5, 4),
            (1, 2, 6, 5),
            (2, 3, 7, 6),
            (3, 0, 4, 7),
        ],
    )
    mesh.materials.append(mat)
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    bpy.context.collection.objects.link(obj)
    if bevel:
        modifier = obj.modifiers.new("EdgeSoftening", "BEVEL")
        modifier.width = min(bevel, min(size) * 0.20)
        modifier.segments = 2
    metric_uv(obj, tile_m)
    return tag_object(obj, semantic, cfg, role=role)


def tagged_beam(
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    thickness: float,
    mat: bpy.types.Material,
    cfg: dict,
    *,
    semantic: str,
    role: str = "assembled",
) -> bpy.types.Object:
    return tag_object(
        beam(name, start, end, thickness, mat),
        semantic,
        cfg,
        role=role,
    )


def normalize_bottom_origin(objects: list[bpy.types.Object]) -> None:
    # Quaternion beams and rotated PV panels must have evaluated world matrices
    # before their bounds establish the delivery origin.
    bpy.context.view_layer.update()
    minimum_z = min(
        (obj.matrix_world @ Vector(corner)).z
        for obj in objects
        for corner in obj.bound_box
    )
    for obj in objects:
        obj.location.z -= minimum_z


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
            for slot in obj.material_slots
            if slot.material
        }
    )


def add_curtain_face(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    axis: str,
    fixed: float,
    centre: float,
    length: float,
    z0: float,
    floors: int,
    floor_height: float,
    outward: float,
    mats: dict[str, bpy.types.Material],
    cfg: dict,
    role: str = "assembled",
    target_bay: float = 3.0,
    interior_every: int = 1,
) -> None:
    bay_count = max(2, round(length / target_bay))
    bay = length / bay_count
    frame = mats["frame"]
    spandrel = mats.get("spandrel", mats.get("precast", frame))
    for level in range(floors):
        base_z = z0 + level * floor_height
        spandrel_height = 0.38 if cfg["family"] == "skyline-glass-office-cluster" else 0.38
        vision_height = floor_height - spandrel_height - 0.10
        vision_z = base_z + spandrel_height + vision_height / 2
        spandrel_z = base_z + spandrel_height / 2
        for bay_index in range(bay_count):
            along = centre - length / 2 + bay * (bay_index + 0.5)
            if axis == "x":
                pane_size = (bay - 0.12, 0.075, vision_height)
                pane_location = (along, fixed, vision_z)
                strip_size = (bay, 0.11, spandrel_height)
                strip_location = (along, fixed + outward * 0.012, spandrel_z)
                card_size = (bay - 0.25, 0.055, vision_height - 0.22)
                card_location = (along, fixed - outward * 0.34, vision_z)
            else:
                pane_size = (0.075, bay - 0.12, vision_height)
                pane_location = (fixed, along, vision_z)
                strip_size = (0.11, bay, spandrel_height)
                strip_location = (fixed + outward * 0.012, along, spandrel_z)
                card_size = (0.055, bay - 0.25, vision_height - 0.22)
                card_location = (fixed - outward * 0.34, along, vision_z)
            objects.append(
                b(
                    f"{prefix}_Glass_L{level:02d}_B{bay_index:02d}",
                    pane_size,
                    pane_location,
                    mats["glass"],
                    cfg,
                    bevel=0.0,
                    semantic="physical_separate_vision_pane",
                    role=role,
                    tile_m=3.1,
                )
            )
            objects.append(
                b(
                    f"{prefix}_Spandrel_L{level:02d}_B{bay_index:02d}",
                    strip_size,
                    strip_location,
                    spandrel,
                    cfg,
                    bevel=0.0,
                    semantic="physical_spandrel_or_slab_edge",
                    role=role,
                    tile_m=2.4,
                )
            )
            if bay_index % interior_every == 0:
                objects.append(
                    b(
                        f"{prefix}_OccupiedDepth_L{level:02d}_B{bay_index:02d}",
                        card_size,
                        card_location,
                        mats["interior"],
                        cfg,
                        bevel=0.0,
                        semantic="occupied_room_depth_behind_glass",
                        role=role,
                        tile_m=3.0,
                    )
                )
        # A real slab edge sits behind each spandrel datum.
        if axis == "x":
            slab_size = (length - 0.35, 0.62, 0.16)
            slab_location = (centre, fixed - outward * 0.48, base_z + 0.12)
        else:
            slab_size = (0.62, length - 0.35, 0.16)
            slab_location = (fixed - outward * 0.48, centre, base_z + 0.12)
        objects.append(
            b(
                f"{prefix}_Slab_{level:02d}",
                slab_size,
                slab_location,
                mats.get("roof", spandrel),
                cfg,
                bevel=0.0,
                semantic="physical_floor_slab_edge",
                role=role,
                tile_m=3.0,
            )
        )
    total_height = floors * floor_height
    cap_depth = 0.15
    for boundary in range(bay_count + 1):
        along = centre - length / 2 + bay * boundary
        if axis == "x":
            size = (0.095, cap_depth, total_height)
            location = (along, fixed + outward * 0.055, z0 + total_height / 2)
        else:
            size = (cap_depth, 0.095, total_height)
            location = (fixed + outward * 0.055, along, z0 + total_height / 2)
        objects.append(
            b(
                f"{prefix}_VerticalCap_{boundary:02d}",
                size,
                location,
                frame,
                cfg,
                bevel=0.009,
                semantic="continuous_external_curtain_wall_mullion",
                role=role,
                tile_m=1.0,
            )
        )
    for boundary in range(floors + 1):
        z = z0 + boundary * floor_height
        if axis == "x":
            size = (length + 0.08, cap_depth, 0.095)
            location = (centre, fixed + outward * 0.057, z)
        else:
            size = (cap_depth, length + 0.08, 0.095)
            location = (fixed + outward * 0.057, centre, z)
        objects.append(
            b(
                f"{prefix}_HorizontalCap_{boundary:02d}",
                size,
                location,
                frame,
                cfg,
                bevel=0.009,
                semantic="continuous_external_curtain_wall_transom",
                role=role,
                tile_m=1.0,
            )
        )


def add_curtain_tier(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    centre: tuple[float, float],
    size: tuple[float, float],
    z0: float,
    floors: int,
    floor_height: float,
    mats: dict[str, bpy.types.Material],
    cfg: dict,
    role: str = "assembled",
    target_bay: float = 3.0,
) -> None:
    cx, cy = centre
    width, depth = size
    add_curtain_face(
        objects,
        prefix=f"{prefix}_Front",
        axis="x",
        fixed=cy - depth / 2,
        centre=cx,
        length=width,
        z0=z0,
        floors=floors,
        floor_height=floor_height,
        outward=-1.0,
        mats=mats,
        cfg=cfg,
        role=role,
        target_bay=target_bay,
    )
    add_curtain_face(
        objects,
        prefix=f"{prefix}_Rear",
        axis="x",
        fixed=cy + depth / 2,
        centre=cx,
        length=width,
        z0=z0,
        floors=floors,
        floor_height=floor_height,
        outward=1.0,
        mats=mats,
        cfg=cfg,
        role=role,
        target_bay=target_bay,
    )
    add_curtain_face(
        objects,
        prefix=f"{prefix}_Left",
        axis="y",
        fixed=cx - width / 2,
        centre=cy,
        length=depth,
        z0=z0,
        floors=floors,
        floor_height=floor_height,
        outward=-1.0,
        mats=mats,
        cfg=cfg,
        role=role,
        target_bay=target_bay,
        interior_every=2,
    )
    add_curtain_face(
        objects,
        prefix=f"{prefix}_Right",
        axis="y",
        fixed=cx + width / 2,
        centre=cy,
        length=depth,
        z0=z0,
        floors=floors,
        floor_height=floor_height,
        outward=1.0,
        mats=mats,
        cfg=cfg,
        role=role,
        target_bay=target_bay,
        interior_every=2,
    )
    objects.append(
        b(
            f"{prefix}_Core",
            (max(3.0, width * 0.22), max(3.0, depth * 0.22), floors * floor_height),
            (cx, cy + depth * 0.12, z0 + floors * floor_height / 2),
            mats.get("core", mats.get("precast", mats["frame"])),
            cfg,
            bevel=0.045,
            semantic="opaque_vertical_service_core",
            role=role,
            tile_m=2.4,
        )
    )


def add_roof_lantern(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    centre: tuple[float, float],
    size: tuple[float, float],
    base_z: float,
    mats: dict[str, bpy.types.Material],
    cfg: dict,
    mast: bool = False,
    role: str = "assembled",
) -> None:
    cx, cy = centre
    width, depth = size
    objects.append(
        b(
            f"{prefix}_RoofDeck",
            (width + 1.2, depth + 1.2, 0.22),
            (cx, cy, base_z + 0.11),
            mats["roof"],
            cfg,
            bevel=0.035,
            semantic="stepped_tower_roof_deck",
            role=role,
        )
    )
    lantern_w = width * 0.68
    lantern_d = depth * 0.70
    lantern_h = 2.15
    # Four transparent walls and physical corner posts make a real lantern.
    for side, axis, fixed, length, outward in (
        ("Front", "x", cy - lantern_d / 2, lantern_w, -1.0),
        ("Rear", "x", cy + lantern_d / 2, lantern_w, 1.0),
        ("Left", "y", cx - lantern_w / 2, lantern_d, -1.0),
        ("Right", "y", cx + lantern_w / 2, lantern_d, 1.0),
    ):
        add_curtain_face(
            objects,
            prefix=f"{prefix}_Lantern{side}",
            axis=axis,
            fixed=fixed,
            centre=cx if axis == "x" else cy,
            length=length,
            z0=base_z + 0.20,
            floors=1,
            floor_height=lantern_h,
            outward=outward,
            mats=mats,
            cfg=cfg,
            role=role,
            target_bay=3.0,
            interior_every=3,
        )
    top_z = base_z + lantern_h + 0.42
    objects.append(
        b(
            f"{prefix}_LanternCanopy",
            (lantern_w + 1.3, lantern_d + 1.3, 0.18),
            (cx, cy, top_z),
            mats["glass"],
            cfg,
            bevel=0.012,
            semantic="transparent_glazed_roof_lantern_canopy",
            role=role,
        )
    )
    for side, size, location in (
        ("Front", (lantern_w + 1.4, 0.12, 0.16), (cx, cy - (lantern_d + 1.3) / 2, top_z)),
        ("Rear", (lantern_w + 1.4, 0.12, 0.16), (cx, cy + (lantern_d + 1.3) / 2, top_z)),
        ("Left", (0.12, lantern_d + 1.4, 0.16), (cx - (lantern_w + 1.3) / 2, cy, top_z)),
        ("Right", (0.12, lantern_d + 1.4, 0.16), (cx + (lantern_w + 1.3) / 2, cy, top_z)),
    ):
        objects.append(
            b(
                f"{prefix}_LanternCanopy{side}Frame",
                size,
                location,
                mats["frame"],
                cfg,
                bevel=0.012,
                semantic="silver_glazed_lantern_roof_perimeter",
                role=role,
                tile_m=1.0,
            )
        )
    # Light diagonal roof braces read in the aerial without becoming a solid cap.
    for index, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        objects.append(
            tagged_beam(
                f"{prefix}_LanternRoofBrace_{index}",
                (cx + sx * lantern_w / 2, cy + sy * lantern_d / 2, base_z + lantern_h + 0.18),
                (cx + sx * (lantern_w + 1.1) / 2, cy + sy * (lantern_d + 1.1) / 2, top_z),
                0.075,
                mats["frame"],
                cfg,
                semantic="glazed_lantern_roof_brace",
                role=role,
            )
        )
    if mast:
        mast_obj = cylinder(
            f"{prefix}_CentreMast",
            0.13,
            6.2,
            (cx, cy, top_z + 3.1),
            mats["steel"],
            20,
        )
        objects.append(tag_object(mast_obj, "centre_tower_antenna_mast", cfg, role=role))
        ring = cylinder(
            f"{prefix}_MastRing",
            0.48,
            0.18,
            (cx, cy, top_z + 2.15),
            mats["frame"],
            24,
        )
        objects.append(tag_object(ring, "centre_tower_mast_ring", cfg, role=role))


def add_skybridge(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    x0: float,
    x1: float,
    y: float,
    z0: float,
    mats: dict[str, bpy.types.Material],
    cfg: dict,
    role: str = "assembled",
) -> None:
    span = x1 - x0
    centre_x = (x0 + x1) / 2
    depth = 3.45
    height = 3.20
    objects.extend(
        [
            b(
                f"{prefix}_Deck",
                (span, depth, 0.24),
                (centre_x, y, z0 + 0.12),
                mats["steel"],
                cfg,
                bevel=0.025,
                semantic="enclosed_skybridge_floor",
                role=role,
            ),
            b(
                f"{prefix}_Roof",
                (span, depth, 0.20),
                (centre_x, y, z0 + height),
                mats["steel"],
                cfg,
                bevel=0.025,
                semantic="enclosed_skybridge_roof",
                role=role,
            ),
            b(
                f"{prefix}_FrontGlass",
                (span - 0.20, 0.07, height - 0.34),
                (centre_x, y - depth / 2, z0 + height / 2),
                mats["glass"],
                cfg,
                bevel=0.004,
                semantic="enclosed_skybridge_front_glass",
                role=role,
                tile_m=3.0,
            ),
            b(
                f"{prefix}_RearGlass",
                (span - 0.20, 0.07, height - 0.34),
                (centre_x, y + depth / 2, z0 + height / 2),
                mats["glass"],
                cfg,
                bevel=0.004,
                semantic="enclosed_skybridge_rear_glass",
                role=role,
                tile_m=3.0,
            ),
            b(
                f"{prefix}_OccupiedDepth",
                (span - 0.50, 0.06, height - 0.70),
                (centre_x, y + 0.22, z0 + height / 2),
                mats["interior"],
                cfg,
                bevel=0.002,
                semantic="occupied_bridge_depth",
                role=role,
                tile_m=3.0,
            ),
        ]
    )
    bay_count = max(2, round(span / 3.3))
    bay = span / bay_count
    for side_index, side in enumerate((-1, 1)):
        facade_y = y + side * depth / 2
        for index in range(bay_count + 1):
            x = x0 + index * bay
            objects.append(
                b(
                    f"{prefix}_Frame_{side_index}_{index}",
                    (0.105, 0.16, height),
                    (x, facade_y, z0 + height / 2),
                    mats["frame"],
                    cfg,
                    bevel=0.009,
                    semantic="skybridge_aluminum_post",
                    role=role,
                    tile_m=1.0,
                )
            )
        for index in range(bay_count):
            a = x0 + index * bay
            c = x0 + (index + 1) * bay
            if index % 2:
                start, end = (a, facade_y, z0 + 0.26), (c, facade_y, z0 + height - 0.20)
            else:
                start, end = (a, facade_y, z0 + height - 0.20), (c, facade_y, z0 + 0.26)
            objects.append(
                tagged_beam(
                    f"{prefix}_Truss_{side_index}_{index}",
                    start,
                    end,
                    0.095,
                    mats["steel"],
                    cfg,
                    semantic="legible_skybridge_diagonal_truss",
                    role=role,
                )
            )


def add_tree(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    location: tuple[float, float, float],
    scale: float,
    mats: dict[str, bpy.types.Material],
    cfg: dict,
) -> None:
    x, y, z = location
    trunk = cylinder(prefix + "_Trunk", 0.13 * scale, 2.7 * scale, (x, y, z + 1.35 * scale), mats["wood"], 12)
    objects.append(tag_object(trunk, "integrated_landscape_tree_trunk", cfg))
    for index, (dx, dy, dz, radius) in enumerate(
        (
            (-0.52, 0.02, 2.62, 0.76),
            (0.47, -0.08, 2.72, 0.72),
            (0.00, 0.18, 3.24, 0.86),
            (-0.12, -0.14, 3.75, 0.64),
        )
    ):
        leaf = sphere(
            f"{prefix}_Crown_{index}",
            radius * scale,
            (x + dx * scale, y + dy * scale, z + dz * scale),
            mats["green_alt"] if "green_alt" in mats and index % 2 else mats["green"],
            (1.0, 1.0, 0.72),
            segments=20,
            rings=12,
        )
        objects.append(tag_object(leaf, "restrained_integrated_tree_canopy", cfg))


def build_skyline(mats: dict[str, bpy.types.Material], cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    floor_height = cfg["floor_height"]
    podium_h = 5.20
    objects.extend(
        [
            b(
                "SKYLINE_Plaza",
                (70.0, 40.0, 0.18),
                (0.0, -1.0, 0.09),
                mats["plaza"],
                cfg,
                bevel=0.030,
                semantic="paved_civic_plaza",
                tile_m=2.0,
            ),
            b(
                "SKYLINE_PodiumStonePlinth",
                (64.0, 24.0, 0.48),
                (0.0, 2.0, 0.24),
                mats["stone"],
                cfg,
                bevel=0.05,
                semantic="shared_honed_stone_podium_plinth",
                tile_m=2.2,
            ),
        ]
    )
    add_curtain_tier(
        objects,
        prefix="SKYLINE_SharedPodium",
        centre=(0.0, 2.0),
        size=(62.0, 22.0),
        z0=0.48,
        floors=1,
        floor_height=podium_h - 0.48,
        mats=mats,
        cfg=cfg,
        target_bay=4.1,
    )
    # Deep central entry canopy and transparent vestibule make the public base legible.
    objects.extend(
        [
            b(
                "SKYLINE_EntryCanopy",
                (12.0, 4.2, 0.22),
                (0.0, -11.7, 4.65),
                mats["frame"],
                cfg,
                bevel=0.04,
                semantic="floating_public_entry_canopy",
            ),
            b(
                "SKYLINE_EntryVestibule",
                (7.0, 3.0, 4.0),
                (0.0, -9.75, 2.5),
                mats["glass"],
                cfg,
                bevel=0.025,
                semantic="transparent_recessed_entry_vestibule",
            ),
        ]
    )
    # Each shaft is a stack of genuinely different tiers, not a box with a roof decal.
    tower_specs = (
        (
            "Left",
            -23.0,
            [((15.5, 18.0), 10), ((13.4, 16.0), 3), ((11.6, 14.0), 1)],
            False,
        ),
        (
            "Centre",
            0.0,
            [((17.0, 19.0), 12), ((15.0, 17.0), 3), ((12.8, 14.5), 2)],
            True,
        ),
        (
            "Right",
            23.0,
            [((15.5, 17.5), 9), ((13.3, 15.5), 3), ((11.4, 13.5), 1)],
            False,
        ),
    )
    for name, cx, tiers, mast in tower_specs:
        z = podium_h
        for tier_index, (size, floors) in enumerate(tiers):
            add_curtain_tier(
                objects,
                prefix=f"SKYLINE_{name}_Tier{tier_index}",
                centre=(cx, 2.3),
                size=size,
                z0=z,
                floors=floors,
                floor_height=floor_height,
                mats=mats,
                cfg=cfg,
                target_bay=2.85,
            )
            z += floors * floor_height
        add_roof_lantern(
            objects,
            prefix=f"SKYLINE_{name}_Crown",
            centre=(cx, 2.3),
            size=tiers[-1][0],
            base_z=z,
            mats=mats,
            cfg=cfg,
            mast=mast,
        )
    add_skybridge(
        objects,
        prefix="SKYLINE_LeftLowerBridge",
        x0=-15.25,
        x1=-8.48,
        y=2.0,
        z0=podium_h + floor_height * 4.0,
        mats=mats,
        cfg=cfg,
    )
    add_skybridge(
        objects,
        prefix="SKYLINE_RightUpperBridge",
        x0=8.48,
        x1=15.25,
        y=2.0,
        z0=podium_h + floor_height * 8.0,
        mats=mats,
        cfg=cfg,
    )
    for index, x in enumerate((-29.0, -15.5, 15.5, 29.0)):
        objects.append(
            b(
                f"SKYLINE_Planter_{index}",
                (4.4, 2.0, 0.48),
                (x, -13.0, 0.34),
                mats["stone"],
                cfg,
                bevel=0.12,
                semantic="integrated_plaza_planter",
            )
        )
        add_tree(
            objects,
            prefix=f"SKYLINE_Tree_{index}",
            location=(x, -13.0, 0.55),
            scale=1.05,
            mats=mats,
            cfg=cfg,
        )
    return objects


def add_canopy_roof(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    centre: tuple[float, float],
    size: tuple[float, float],
    base_z: float,
    mats: dict[str, bpy.types.Material],
    cfg: dict,
    role: str = "assembled",
) -> None:
    cx, cy = centre
    width, depth = size
    objects.extend(
        [
            b(
                f"{prefix}_FloatingRoofPlate",
                (width + 2.4, depth + 2.4, 0.20),
                (cx, cy, base_z + 0.18),
                mats["roof"],
                cfg,
                bevel=0.035,
                semantic="broad_cantilevered_cool_roof_plate",
                role=role,
            ),
            b(
                f"{prefix}_FrontFascia",
                (width + 2.6, 0.16, 0.32),
                (cx, cy - depth / 2 - 1.20, base_z + 0.19),
                mats["frame"],
                cfg,
                bevel=0.018,
                semantic="warm_white_canopy_edge",
                role=role,
                tile_m=1.0,
            ),
            b(
                f"{prefix}_RearFascia",
                (width + 2.6, 0.16, 0.32),
                (cx, cy + depth / 2 + 1.20, base_z + 0.19),
                mats["frame"],
                cfg,
                bevel=0.018,
                semantic="warm_white_canopy_edge",
                role=role,
                tile_m=1.0,
            ),
            b(
                f"{prefix}_LeftFascia",
                (0.16, depth + 2.6, 0.32),
                (cx - width / 2 - 1.20, cy, base_z + 0.19),
                mats["frame"],
                cfg,
                bevel=0.018,
                semantic="warm_white_canopy_edge",
                role=role,
                tile_m=1.0,
            ),
            b(
                f"{prefix}_RightFascia",
                (0.16, depth + 2.6, 0.32),
                (cx + width / 2 + 1.20, cy, base_z + 0.19),
                mats["frame"],
                cfg,
                bevel=0.018,
                semantic="warm_white_canopy_edge",
                role=role,
                tile_m=1.0,
            ),
        ]
    )


def add_external_brace_bay(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    x0: float,
    x1: float,
    y: float,
    z0: float,
    height: float,
    mats: dict[str, bpy.types.Material],
    cfg: dict,
) -> None:
    objects.extend(
        [
            tagged_beam(
                prefix + "_BraceA",
                (x0, y, z0),
                (x1, y, z0 + height),
                0.10,
                mats["frame"],
                cfg,
                semantic="external_white_steel_diagonal_brace",
            ),
            tagged_beam(
                prefix + "_BraceB",
                (x1, y, z0),
                (x0, y, z0 + height),
                0.10,
                mats["frame"],
                cfg,
                semantic="external_white_steel_diagonal_brace",
            ),
        ]
    )


def add_pv_array(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    centre: tuple[float, float],
    size: tuple[float, float],
    z: float,
    mats: dict[str, bpy.types.Material],
    cfg: dict,
    role: str = "assembled",
) -> None:
    cx, cy = centre
    width, depth = size
    cols = max(2, int(width // 3.0))
    rows = max(1, int(depth // 2.2))
    panel_w = min(2.55, width / cols - 0.18)
    panel_d = min(1.85, depth / rows - 0.18)
    for row in range(rows):
        for col in range(cols):
            x = cx - width / 2 + (col + 0.5) * width / cols
            y = cy - depth / 2 + (row + 0.5) * depth / rows
            panel = b(
                f"{prefix}_Panel_{row:02d}_{col:02d}",
                (panel_w, panel_d, 0.10),
                (x, y, z + 0.24),
                mats["pv"],
                cfg,
                bevel=0.018,
                semantic="physical_rooftop_photovoltaic_panel",
                role=role,
                tile_m=1.8,
            )
            panel.rotation_euler.x = math.radians(-5.0)
            objects.append(panel)
            objects.append(
                b(
                    f"{prefix}_Rail_{row:02d}_{col:02d}",
                    (panel_w + 0.06, 0.055, 0.09),
                    (x, y, z + 0.13),
                    mats["frame"],
                    cfg,
                    bevel=0.008,
                    semantic="photovoltaic_support_rail",
                    role=role,
                    tile_m=1.0,
                )
            )


def build_campus(mats: dict[str, bpy.types.Material], cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    fh = cfg["floor_height"]
    objects.extend(
        [
            b(
                "CAMPUS_SitePaving",
                (74.0, 54.0, 0.16),
                (0.0, 1.0, 0.08),
                mats["paving"],
                cfg,
                bevel=0.035,
                semantic="pale_concrete_research_campus_paving",
                tile_m=2.1,
            ),
            b(
                "CAMPUS_CourtyardGround",
                (26.0, 25.0, 0.18),
                (0.0, -4.0, 0.18),
                mats["groundcover"],
                cfg,
                bevel=0.05,
                semantic="open_landscaped_central_research_courtyard",
                tile_m=2.0,
            ),
        ]
    )
    wings = (
        ("West", (-22.0, 0.5), (15.0, 41.0), 3),
        ("East", (22.0, 0.5), (15.0, 41.0), 3),
        ("Rear", (0.0, 14.0), (29.0, 14.0), 2),
    )
    for name, centre, size, floors in wings:
        add_curtain_tier(
            objects,
            prefix=f"CAMPUS_{name}Pavilion",
            centre=centre,
            size=size,
            z0=0.20,
            floors=floors,
            floor_height=fh,
            mats=mats,
            cfg=cfg,
            target_bay=3.4,
        )
        add_canopy_roof(
            objects,
            prefix=f"CAMPUS_{name}Canopy",
            centre=centre,
            size=size,
            base_z=0.20 + floors * fh,
            mats=mats,
            cfg=cfg,
        )
    # Two shallow glass links clarify that the pavilions are one campus.
    for side, cx in (("West", -14.1), ("East", 14.1)):
        objects.extend(
            [
                b(
                    f"CAMPUS_{side}ConnectorGlass",
                    (1.8, 7.0, 7.65),
                    (cx, 10.6, 4.05),
                    mats["glass"],
                    cfg,
                    bevel=0.018,
                    semantic="slender_enclosed_glazed_pavilion_connector",
                ),
                b(
                    f"CAMPUS_{side}ConnectorFrame",
                    (2.05, 7.25, 0.18),
                    (cx, 10.6, 7.88),
                    mats["frame"],
                    cfg,
                    bevel=0.020,
                    semantic="white_steel_connector_roof_frame",
                ),
            ]
        )
    # External braces occupy selected bays only, matching the reference restraint.
    add_external_brace_bay(
        objects,
        prefix="CAMPUS_WestFrontBrace",
        x0=-27.8,
        x1=-23.0,
        y=-20.05,
        z0=0.35,
        height=fh * 2.0,
        mats=mats,
        cfg=cfg,
    )
    add_external_brace_bay(
        objects,
        prefix="CAMPUS_EastFrontBrace",
        x0=23.0,
        x1=27.8,
        y=-20.05,
        z0=0.35,
        height=fh * 2.0,
        mats=mats,
        cfg=cfg,
    )
    # Courtyard paths, bioswale beds and entry bridge preserve the open U.
    objects.extend(
        [
            b(
                "CAMPUS_CourtyardAxisPath",
                (5.0, 29.0, 0.10),
                (0.0, -5.0, 0.30),
                mats["paving"],
                cfg,
                bevel=0.025,
                semantic="central_courtyard_pedestrian_axis",
            ),
            b(
                "CAMPUS_CourtyardCrossPath",
                (26.0, 3.0, 0.10),
                (0.0, -1.0, 0.31),
                mats["paving"],
                cfg,
                bevel=0.025,
                semantic="courtyard_cross_path",
            ),
            b(
                "CAMPUS_ArrivalCanopy",
                (12.0, 7.0, 0.22),
                (0.0, -22.0, 4.25),
                mats["frame"],
                cfg,
                bevel=0.035,
                semantic="cantilevered_courtyard_arrival_canopy",
            ),
        ]
    )
    for index, (x, y) in enumerate(((-4.9, -23.7), (4.9, -23.7), (-4.9, -20.3), (4.9, -20.3))):
        objects.append(
            b(
                f"CAMPUS_ArrivalCanopyPost_{index}",
                (0.14, 0.14, 4.10),
                (x, y, 2.15),
                mats["frame"],
                cfg,
                bevel=0.018,
                semantic="slender_white_arrival_canopy_post",
                tile_m=1.0,
            )
        )
    for index, x in enumerate((-8.8, 8.8)):
        objects.append(
            b(
                f"CAMPUS_Bioswale_{index}",
                (7.0, 19.5, 0.26),
                (x, -4.0, 0.38),
                mats["groundcover"],
                cfg,
                bevel=0.18,
                semantic="planted_courtyard_bioswale",
                tile_m=1.8,
            )
        )
        for mound_index, (dx, y) in enumerate(
            (
                (-2.25, -12.0),
                (0.2, -11.1),
                (2.35, -9.4),
                (-1.1, -7.4),
                (1.35, -5.6),
                (-2.0, -3.0),
                (0.1, -0.7),
                (2.1, 1.6),
                (-1.2, 4.3),
            )
        ):
            mound = sphere(
                f"CAMPUS_BioswaleMound_{index}_{mound_index}",
                0.46,
                (x + dx, y, 0.72),
                mats["green_alt"] if mound_index % 2 else mats["green"],
                (1.35, 0.75, 0.52),
                segments=18,
                rings=10,
            )
            objects.append(tag_object(mound, "layered_bioswale_plant_mound", cfg))
        for tree_index, y in enumerate((-10.0, -2.2, 5.5)):
            add_tree(
                objects,
                prefix=f"CAMPUS_CourtyardTree_{index}_{tree_index}",
                location=(x, y, 0.55),
                scale=0.72,
                mats=mats,
                cfg=cfg,
            )
    # Photovoltaic arrays keep each roof legible from the aerial.
    add_pv_array(
        objects,
        prefix="CAMPUS_WestPV",
        centre=(-22.0, 1.0),
        size=(12.0, 33.0),
        z=0.20 + 3 * fh + 0.35,
        mats=mats,
        cfg=cfg,
    )
    add_pv_array(
        objects,
        prefix="CAMPUS_EastPV",
        centre=(22.0, 1.0),
        size=(12.0, 33.0),
        z=0.20 + 3 * fh + 0.35,
        mats=mats,
        cfg=cfg,
    )
    add_pv_array(
        objects,
        prefix="CAMPUS_RearPV",
        centre=(0.0, 14.0),
        size=(20.0, 8.0),
        z=0.20 + 2 * fh + 0.35,
        mats=mats,
        cfg=cfg,
    )
    # One screened mechanical penthouse, deliberately smaller than the wings.
    objects.extend(
        [
            b(
                "CAMPUS_MechanicalPenthouse",
                (10.0, 6.0, 2.60),
                (0.0, 14.0, 0.20 + 2 * fh + 1.55),
                mats["dark"],
                cfg,
                bevel=0.045,
                semantic="screened_rooftop_mechanical_penthouse",
                tile_m=2.0,
            ),
            b(
                "CAMPUS_MechanicalCap",
                (10.6, 6.6, 0.18),
                (0.0, 14.0, 0.20 + 2 * fh + 2.92),
                mats["frame"],
                cfg,
                bevel=0.028,
                semantic="white_mechanical_screen_cap",
            ),
        ]
    )
    for face_index, y in enumerate((10.92, 17.08)):
        for louver_index in range(15):
            x = -4.55 + louver_index * 0.65
            objects.append(
                b(
                    f"CAMPUS_MechanicalLouver_{face_index}_{louver_index}",
                    (0.08, 0.16, 2.20),
                    (x, y, 0.20 + 2 * fh + 1.55),
                    mats["frame"],
                    cfg,
                    bevel=0.010,
                    semantic="physical_mechanical_screen_louver",
                    tile_m=1.0,
                )
            )
    return objects


def build_assembled(mats: dict[str, bpy.types.Material], cfg: dict) -> list[bpy.types.Object]:
    if cfg["family"] == "skyline-glass-office-cluster":
        return build_skyline(mats, cfg)
    return build_campus(mats, cfg)


def build_module(
    role: str,
    variant: str,
    mats: dict[str, bpy.types.Material],
    cfg: dict,
) -> tuple[list[bpy.types.Object], float]:
    objects: list[bpy.types.Object] = []
    family = cfg["family"]
    width, depth, _ = cfg["native"]
    fh = cfg["floor_height"]
    prefix = f"MODULE_{family.upper().replace('-', '_')}_{role.upper()}_{variant.upper()}"
    if role == "podium":
        height = 1.0
        objects.extend(
            [
                b(
                    prefix + "_Plinth",
                    (width * 0.88, depth * 0.70, 0.55),
                    (0.0, 0.0, 0.275),
                    mats.get("stone", mats.get("precast", mats["frame"])),
                    cfg,
                    semantic="fixed_public_podium",
                    role=role,
                ),
                b(
                    prefix + "_Threshold",
                    (width * 0.24, 3.2, 0.18),
                    (0.0, -depth * 0.37, 0.64),
                    mats.get("plaza", mats.get("paving", mats["roof"])),
                    cfg,
                    semantic="fixed_public_threshold",
                    role=role,
                ),
            ]
        )
    elif role == "floor":
        height = fh
        module_width = width * (0.80 if family == "skyline-glass-office-cluster" else 0.78)
        module_depth = depth * (0.62 if family == "skyline-glass-office-cluster" else 0.58)
        add_curtain_tier(
            objects,
            prefix=prefix,
            centre=(0.0, 0.0),
            size=(module_width, module_depth),
            z0=0.0,
            floors=1,
            floor_height=fh,
            mats=mats,
            cfg=cfg,
            role=role,
            target_bay=3.0 if variant != "typical_c" else 3.5,
        )
        if variant == "typical_b" and family == "autonomous-tech-campus-silicon-valley":
            add_external_brace_bay(
                objects,
                prefix=prefix + "_Brace",
                x0=-module_width / 2 + 1.0,
                x1=-module_width / 2 + 5.0,
                y=-module_depth / 2 - 0.08,
                z0=0.15,
                height=fh - 0.30,
                mats=mats,
                cfg=cfg,
            )
    elif role == "crown":
        height = 1.20
        edge = mats["frame"]
        objects.extend(
            [
                b(prefix + "_Front", (width * 0.82, 0.20, height), (0.0, -depth * 0.31, height / 2), edge, cfg, semantic="fixed_reference_crown", role=role),
                b(prefix + "_Rear", (width * 0.82, 0.20, height), (0.0, depth * 0.31, height / 2), edge, cfg, semantic="fixed_reference_crown", role=role),
                b(prefix + "_Left", (0.20, depth * 0.62, height), (-width * 0.41, 0.0, height / 2), edge, cfg, semantic="fixed_reference_crown", role=role),
                b(prefix + "_Right", (0.20, depth * 0.62, height), (width * 0.41, 0.0, height / 2), edge, cfg, semantic="fixed_reference_crown", role=role),
            ]
        )
    elif role == "roof":
        height = 1.80 if family == "skyline-glass-office-cluster" else 2.10
        objects.append(
            b(
                prefix + "_Deck",
                (width * 0.82, depth * 0.62, 0.22),
                (0.0, 0.0, 0.11),
                mats["roof"],
                cfg,
                semantic="fixed_reference_roof",
                role=role,
            )
        )
        if family == "autonomous-tech-campus-silicon-valley":
            add_pv_array(
                objects,
                prefix=prefix + "_PV",
                centre=(0.0, 0.0),
                size=(width * 0.42, depth * 0.34),
                z=0.22,
                mats=mats,
                cfg=cfg,
                role=role,
            )
        else:
            add_roof_lantern(
                objects,
                prefix=prefix + "_Lantern",
                centre=(0.0, 0.0),
                size=(width * 0.30, depth * 0.30),
                base_z=0.20,
                mats=mats,
                cfg=cfg,
                role=role,
            )
            height = 3.0
    else:
        raise ValueError(role)
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
    width, depth, _ = cfg["native"]
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
        "height_m": height,
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
        normalize_bottom_origin(objects)
        suffix = role if variant == "default" else f"{role}_{variant}"
        filename = f"{cfg['family']}_{suffix}.glb"
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
                cfg,
            )
        )
        delete_objects(objects)
    return payloads


def configure_render(cfg: dict) -> list[bpy.types.Object]:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 920
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.32 if cfg["family"] == "skyline-glass-office-cluster" else 0.18
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.57, 0.68, 0.78, 1.0)
    background.inputs["Strength"].default_value = 0.62
    presentation: list[bpy.types.Object] = []
    ground_mat = material(
        "MAT_W11_MODERN_PresentationGround",
        (0.39, 0.40, 0.39, 1.0),
        0.90,
    )
    presentation.append(
        box(
            "PRESENTATION_ModernGround",
            (260.0, 260.0, 0.10),
            (0.0, 0.0, -0.10),
            ground_mat,
            0.0,
        )
    )
    bpy.ops.object.light_add(
        type="SUN",
        location=(-90.0, -110.0, 130.0),
        rotation=(math.radians(30), math.radians(-18), math.radians(-38)),
    )
    sun = bpy.context.object
    sun.name = "PRESENTATION_ModernSun"
    sun.data.color = (1.0, 0.89, 0.76)
    sun.data.energy = 2.0
    sun.data.angle = math.radians(9.0)
    presentation.append(sun)
    target_z = 32.0 if cfg["family"] == "skyline-glass-office-cluster" else 7.0
    for name, location, energy, size, color in (
        ("Key", (-60.0, -70.0, 75.0), 6200, 18.0, (1.0, 0.82, 0.68)),
        ("Fill", (70.0, -30.0, 48.0), 4300, 16.0, (0.68, 0.82, 1.0)),
        ("Rim", (0.0, 75.0, 62.0), 5600, 14.0, (0.76, 0.88, 1.0)),
    ):
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.name = f"PRESENTATION_Modern{name}"
        light.data.energy = energy
        light.data.shape = "DISK"
        light.data.size = size
        light.data.color = color
        aim = Vector((0.0, 0.0, target_z)) - light.location
        light.rotation_euler = aim.to_track_quat("-Z", "Y").to_euler()
        presentation.append(light)
    return presentation


def render_views(folder: Path, cfg: dict, *, view_set: str) -> list[str]:
    presentation = configure_render(cfg)
    if cfg["family"] == "skyline-glass-office-cluster":
        views = {
            "preview": ((120.0, -158.0, 98.0), (0.0, 1.0, 35.0), 54),
            "front_corner_oblique": ((112.0, -145.0, 80.0), (0.0, 1.0, 35.0), 55),
            "front_elevation": ((0.0, -198.0, 44.0), (0.0, 1.0, 38.0), 56),
            "rear_corner_oblique": ((-105.0, 127.0, 75.0), (0.0, 2.0, 32.0), 56),
            "aerial": ((118.0, -120.0, 142.0), (0.0, 2.0, 25.0), 54),
            "facade_close": ((31.0, -47.0, 25.0), (20.0, -5.0, 24.0), 70),
            "bridge_close": ((31.0, -42.0, 36.0), (10.0, 1.0, 34.0), 72),
            "street": ((64.0, -128.0, 16.0), (0.0, 0.0, 28.0), 64),
            "context": ((132.0, -150.0, 100.0), (0.0, 2.0, 26.0), 52),
        }
    else:
        views = {
            "preview": ((78.0, -88.0, 48.0), (0.0, -1.0, 6.7), 56),
            "front_corner_oblique": ((70.0, -80.0, 33.0), (0.0, -2.0, 6.8), 58),
            "front_elevation": ((0.0, -108.0, 12.0), (0.0, -1.0, 7.0), 62),
            "rear_corner_oblique": ((-73.0, 76.0, 36.0), (0.0, 3.0, 6.6), 58),
            "aerial": ((78.0, -72.0, 82.0), (0.0, 1.0, 4.0), 55),
            "facade_close": ((42.0, -45.0, 14.0), (22.0, -11.0, 7.0), 72),
            "courtyard_close": ((0.0, -39.0, 11.0), (0.0, -2.0, 4.8), 68),
            "street": ((65.0, -105.0, 9.5), (0.0, -1.0, 6.5), 64),
            "context": ((112.0, -125.0, 68.0), (0.0, 1.0, 4.5), 52),
        }
    selected = {
        "preview": {"preview"},
        "pilot": {"preview", "front_corner_oblique", "front_elevation", "aerial", "facade_close"},
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
    if cfg["family"] == "skyline-glass-office-cluster":
        profiles = {
            "rectangle": {
                "recommendedWidth_m": [55.0, 100.0],
                "recommendedDepth_m": [30.0, 58.0],
                "recommendedFloors": [8, 30],
                "scaleMin": 0.78,
                "scaleMax": 1.24,
                "maxAxisRatio": 1.18,
                "preferredBayMultiple_m": 3.1,
            }
        }
        preferred = ["rectangle"]
        rationale = (
            "The exact three-tower count, one podium and two bridge connections form "
            "one landmark composition. The rectangle matrix accepts ordinary hand-"
            "drawn variation from 55-100 by 30-58 metres; larger targets repeat "
            "complete curtain-wall office bars rather than stretching bridges or towers."
        )
    else:
        profiles = {
            "rectangle": {
                "recommendedWidth_m": [56.0, 100.0],
                "recommendedDepth_m": [38.0, 76.0],
                "recommendedFloors": [2, 7],
                "scaleMin": 0.76,
                "scaleMax": 1.26,
                "maxAxisRatio": 1.20,
                "preferredBayMultiple_m": 3.4,
            },
            "l_shape": {
                "recommendedWidth_m": [54.0, 105.0],
                "recommendedDepth_m": [36.0, 82.0],
                "recommendedFloors": [2, 7],
                "scaleMin": 0.74,
                "scaleMax": 1.28,
                "maxAxisRatio": 1.22,
                "preferredBayMultiple_m": 3.4,
            },
            "u_shape": {
                "recommendedWidth_m": [58.0, 110.0],
                "recommendedDepth_m": [42.0, 88.0],
                "recommendedFloors": [2, 7],
                "scaleMin": 0.74,
                "scaleMax": 1.30,
                "maxAxisRatio": 1.22,
                "preferredBayMultiple_m": 3.4,
            },
        }
        preferred = ["rectangle", "l_shape", "u_shape"]
        rationale = (
            "The identity is a set of complete occupied research pavilion bars around "
            "outdoor space. Rectangle, L and U drawings turn or repeat whole 3.4 metre "
            "laboratory bays while preserving the primary entry, external frame, real "
            "glazing and courtyard; openings and photovoltaic panels are never stretched."
        )
    primary = profiles["rectangle"]
    return {
        "preferredProfiles": preferred,
        "minimumPreferredProfiles": len(preferred),
        "profileRationale": rationale,
        "fixedLandmarkScaleBand": {
            "scaleMin": primary["scaleMin"],
            "scaleMax": primary["scaleMax"],
            "maxAxisRatio": primary["maxAxisRatio"],
        },
        "recommendedWidth_m": primary["recommendedWidth_m"],
        "recommendedDepth_m": primary["recommendedDepth_m"],
        "recommendedFloors": primary["recommendedFloors"],
        "preferredBayMultiple_m": primary["preferredBayMultiple_m"],
        "scaleMin": primary["scaleMin"],
        "scaleMax": primary["scaleMax"],
        "maxAxisRatio": primary["maxAxisRatio"],
        "profiles": profiles,
    }


def facade_sheet_contract(skin: dict, cfg: dict) -> dict:
    family = cfg["family"]
    contract = facade_contract(
        family,
        skin,
        f"/families/{family}/textures/source/archetype-goalpost.png",
    )
    contract["geometry_detail_profile"] = "hero"
    if family == "skyline-glass-office-cluster":
        contract["bay_strategy"] = {
            "fixed_end_bays": [
                "three_staggered_tower_shafts",
                "two_enclosed_skybridges",
                "three_stepped_glazed_crowns",
            ],
            "repeatable_middle_bays": list(range(18)),
            "middle_variants": ["typical_a", "typical_b", "typical_c"],
            "rule": "Repeat complete 3.1 metre vision/spandrel office bays; never stretch a pane, cap, truss or bridge.",
        }
        coverage = {
            "front": "three staggered occupied curtain-wall towers over one transparent public podium",
            "left": "wrapped physical curtain wall and stepped left crown",
            "right": "wrapped physical curtain wall and stepped right crown",
            "rear": "occupied secondary curtain walls and both bridge connections",
            "roof": "three lantern crowns, centre mast and low-slope service roofs",
        }
        fixed = [
            "podium/entrance",
            "corner returns",
            "crown",
            "roof",
            "three tower count",
            "two skybridge positions",
            "shared podium",
            "three crowns and centre mast",
        ]
    else:
        contract["bay_strategy"] = {
            "fixed_end_bays": [
                "courtyard_arrival",
                "three_pavilion_junctions",
                "screened_mechanical_penthouse",
            ],
            "repeatable_middle_bays": list(range(16)),
            "middle_variants": ["typical_a", "typical_b", "typical_c"],
            "rule": "Repeat or turn complete 3.4 metre occupied research bays, including pane, frame, slab, interior and optional brace.",
        }
        coverage = {
            "front": "two courtyard-facing pavilion ends, open arrival axis and cantilevered canopy",
            "left": "occupied external-frame research pavilion with photovoltaic roof",
            "right": "occupied external-frame research pavilion with photovoltaic roof",
            "rear": "two-storey connecting pavilion and screened mechanical penthouse",
            "roof": "three broad canopy plates, three photovoltaic fields and one penthouse",
        }
        fixed = [
            "podium/entrance",
            "corner returns",
            "crown",
            "roof",
            "open U-shaped courtyard",
            "three pavilion junctions",
            "arrival canopy",
            "penthouse and PV fields",
        ]
    contract["assembly_contract"] = {
        "fixed": fixed,
        "repeatable": ["typical_a", "typical_b", "typical_c"],
        "side_elevations": coverage["left"] + "; " + coverage["right"],
        "elevation_coverage": coverage,
        "variation_policy": (
            "Use the fixed landmark inside its authored independent-axis scale band. "
            "Oversized or differently proportioned targets use long-axis streetwall "
            "repeat of complete occupied semantic bays, never family_incompatible."
        ),
    }
    return contract


def massing_graph(cfg: dict) -> dict:
    if cfg["family"] == "skyline-glass-office-cluster":
        return {
            "type": "fixed_three_tower_skybridge_landmark_with_repeatable_office_bays",
            "tower_count": 3,
            "tower_floor_counts": [14, 17, 13],
            "enclosed_skybridges": 2,
            "shared_transparent_podium": True,
            "stepped_glazed_crowns": 3,
            "centre_antenna_masts": 1,
            "physical_curtain_wall_layers": ["vision", "spandrel", "aluminum_caps", "slab", "occupied_depth"],
        }
    return {
        "type": "fixed_u_shaped_research_campus_with_repeatable_pavilion_bays",
        "pavilion_wings": 3,
        "open_landscaped_courtyard": True,
        "occupied_storeys": [3, 3, 2],
        "glazed_connectors": 2,
        "external_white_steel_frame": True,
        "cantilevered_canopy_roofs": 3,
        "photovoltaic_fields": 3,
        "screened_mechanical_penthouses": 1,
        "physical_curtain_wall_layers": ["low_iron_pane", "external_frame", "slab", "occupied_lab_depth"],
    }


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
    normalize_bottom_origin(objects)
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
    width, depth, height = cfg["native"]
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
        "footprint_profile": "rectangle" if family == "skyline-glass-office-cluster" else "u_shape",
        "footprint_target": {
            "width_m": width,
            "depth_m": depth,
            "wing_depth_m": 15.0 if family != "skyline-glass-office-cluster" else 22.0,
            "segments": (
                [
                    {"id": "left_tower", "centre_x_m": -23.0, "centre_y_m": 2.3, "length_m": 15.5, "thickness_m": 18.0, "rotation_degrees": 0.0},
                    {"id": "centre_tower", "centre_x_m": 0.0, "centre_y_m": 2.3, "length_m": 17.0, "thickness_m": 19.0, "rotation_degrees": 0.0},
                    {"id": "right_tower", "centre_x_m": 23.0, "centre_y_m": 2.3, "length_m": 15.5, "thickness_m": 17.5, "rotation_degrees": 0.0},
                ]
                if family == "skyline-glass-office-cluster"
                else [
                    {"id": "west_pavilion", "centre_x_m": -22.0, "centre_y_m": 0.5, "length_m": 41.0, "thickness_m": 15.0, "rotation_degrees": 90.0},
                    {"id": "east_pavilion", "centre_x_m": 22.0, "centre_y_m": 0.5, "length_m": 41.0, "thickness_m": 15.0, "rotation_degrees": 90.0},
                    {"id": "rear_pavilion", "centre_x_m": 0.0, "centre_y_m": 14.0, "length_m": 29.0, "thickness_m": 14.0, "rotation_degrees": 0.0},
                ]
            ),
        },
        "massing_graph": graph,
        "texture_keys": sorted(skin["zones"]),
        "ao_baked": True,
    }
    aliases = cfg["aliases"]
    manifest = {
        "manifest_schema": 3,
        "grammar_schema_version": 3,
        "generator": {
            "name": "archetype_compiler/generate_wave11_modern_families.py",
            "version": "1.0.0",
            "blender_version": bpy.app.version_string,
            "render_engine": "BLENDER_EEVEE",
        },
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
        "generation_tags": [
            "wave11",
            "fixed_landmark_and_modular_fallback",
            "custom_pbr_skin",
            "physical_separate_glazing",
            "occupied_interior_depth",
            "complete_semantic_bay_repeat",
            *( ["three_towers", "two_enclosed_skybridges", "stepped_glazed_crowns"] if family == "skyline-glass-office-cluster" else ["three_pavilions", "open_courtyard", "expressed_white_frame", "photovoltaic_roofs"] ),
        ],
        "footprint_compatibility": footprint,
        "coordinate_contract": COORDINATE_CONTRACT,
        "textures": texture_inventory(skin),
        "facade_sheet": facade_sheet_contract(skin, cfg),
        "massing_graph": graph,
        "material_budget": {
            "max_assembled_materials": 18,
            "rationale": "Vision glass, occupied depth, frame, opaque skin, roofs and ground retain distinct physically based responses because their material contrast carries the archetype identity.",
        },
        "dimensions": {
            "width_m": width,
            "depth_m": depth,
            "podium_height_m": 5.20 if family == "skyline-glass-office-cluster" else 0.20,
            "floor_height_m": cfg["floor_height"],
            "setback_height_m": cfg["floor_height"],
            "roof_height_m": 3.0 if family == "skyline-glass-office-cluster" else 3.1,
            "crown_height_m": 2.6 if family == "skyline-glass-office-cluster" else 1.2,
            "default_floors": cfg["native_floors"],
            "min_floors": cfg["min_floors"],
            "max_floors": cfg["max_floors"],
        },
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
        "source_provenance": {
            "catalogue_archetype_id": cfg["archetype_id"],
            "catalogue_variant_id": cfg["variant_id"],
            "catalogue_alias_ids": aliases[2:],
            "elevation_source": f"/families/{family}/elevation.jpg",
            "goalpost": f"/families/{family}/textures/source/archetype-goalpost.png",
            "reference_generation": f"/families/{family}/textures/source/reference-generation.json",
            "method": "reference-locked four-view source board, six-zone material construction plate, deterministic metric envelope, physical layered glazing, occupied depth, complete secondary elevations and semantic LEGO fallback modules",
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    grammar = {
        "family_id": family,
        "source": {
            "archetype_id": cfg["archetype_id"],
            "variant_id": cfg["variant_id"],
            "generation_archetype_id": cfg["variant_id"],
            "reuse_keys": manifest["reuse_keys"],
        },
        "dimensions": manifest["dimensions"],
        "architectural_signature": {
            "identity": cfg["identity"],
            "material_zones": cfg["material_zones"],
            "glass_profile": cfg["glass_profile"],
            "kits": [
                "reference_locked_fixed_landmark",
                "physical_layered_curtain_wall",
                "occupied_interior_depth",
                "semantic_repeatable_middle_bays",
                "fixed_crown_and_roof_kit",
            ],
        },
        "archetype_aliases": aliases,
        "footprint_compatibility": footprint,
        "massing_graph": graph,
    }
    (folder / "grammar.json").write_text(json.dumps(grammar, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (folder / "archetype-source.json").write_text(json.dumps(manifest["source_provenance"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"[wave11] {family}: {assembled_triangles} triangles, "
        f"{assembled_materials} materials, {len(modules)} modules, "
        f"{len(renders)} renders",
        flush=True,
    )


def render_existing(output_root: Path, cfg: dict, *, view_set: str) -> None:
    clear_scene()
    folder = (output_root / cfg["family"]).resolve()
    mats, _skin = load_palette(folder, cfg)
    objects = build_assembled(mats, cfg)
    normalize_bottom_origin(objects)
    rendered = render_views(folder, cfg, view_set=view_set)
    delete_objects(objects)
    print(f"[wave11] {cfg['family']}: rendered {len(rendered)} views", flush=True)


def main() -> int:
    args = parse_args()
    cfg = dict(FAMILIES[args.family])
    cfg["family"] = args.family
    if args.render_existing:
        render_existing(args.output_root, cfg, view_set=args.view_set)
    else:
        build_family(
            args.output_root,
            cfg,
            view_set=args.view_set,
            skip_renders=args.skip_renders,
            skip_modules=args.skip_modules,
            skip_assembled_export=args.skip_assembled_export,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
