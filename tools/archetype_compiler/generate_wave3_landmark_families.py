"""Generate the Wave 3 Markthal, arena, and domed-civic LEGO families.

These are deliberately sculpted landmark envelopes.  The fixed assembled GLB
owns the one-off silhouette, while a restrained five-role kit remains available
for planner streetwall-repeat and flexible-height fallbacks.

Run with Blender 5.x:

  blender --background --factory-startup --python \
    tools/archetype_compiler/generate_wave3_landmark_families.py -- \
    --output-root frontend/public/families \
    --markthal-fixed artifacts/wave3/markthal-audit/converted/food-hall-market-hall_markthal.glb
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


COORDINATE_CONTRACT = {
    "units": "metres",
    "blender_up": "+Z",
    "gltf_up": "+Y (export_yup)",
    "origin": "bottom centre",
    "front_facade": "-Y in Blender, +Z in glTF",
    "transforms": "applied",
}

FAMILIES = {
    "food-hall-market-hall": {
        "archetype_id": "food_hall_market_hall",
        "variant_id": "market_contemporary",
        "generation_archetype_id": "market_contemporary",
        "label": "Food Hall Market Hall — Contemporary Arch",
        "dimensions": (60.0, 96.0, 36.75),
        "floors": (1, 3, 3),
        "reuse_keys": ["food_hall_market_hall", "market_contemporary", "Food Hall / Market"],
        "aliases": ["food_hall_market_hall", "market_contemporary"],
        "profiles": {
            "recommendedWidth_m": [42, 84],
            "recommendedDepth_m": [62, 134],
            "recommendedFloors": [1, 3],
        },
        "identity": "Inhabited pale-stone horseshoe arch enclosing a monumental cable-net market hall, vivid inner-vault mural, long residential side lattice, and an occupied roof court.",
        "materials": "pale limestone panels; dark steel cable net; low-iron glass; vivid mural vault; warm market interiors; charcoal roof membrane",
        "glass": "low_iron_cable_net",
    },
    "modern-sports-arena": {
        "archetype_id": "modern_sports_arena",
        "variant_id": "sports_arena_indoor",
        "generation_archetype_id": "sports_arena_indoor",
        "label": "Modern Sports Arena — Faceted Indoor Bowl",
        "dimensions": (150.0, 120.0, 42.0),
        "floors": (2, 5, 3),
        "reuse_keys": ["modern_sports_arena", "sports_arena_indoor", "Sports / Entertainment"],
        "aliases": ["modern_sports_arena", "sports_arena_indoor"],
        "profiles": {
            "recommendedWidth_m": [100, 210],
            "recommendedDepth_m": [80, 168],
            "recommendedFloors": [2, 5],
        },
        "identity": "Low elliptical indoor arena with a silver faceted diagrid bowl, transparent public concourse, twin sweeping entrance cuts, amber media ribbon, ribbed roof, and central oval oculus.",
        "materials": "satin silver aluminum facets; charcoal steel ribs; low-iron concourse glass; warm occupied lobby; restrained amber media ribbon; dark roof membrane",
        "glass": "arena_concourse_clear",
        "goalpost": "/archetypes/buildings/modern_sports_arena/hero.png",
    },
    "civic-monumental-neoclassical": {
        "archetype_id": "civic_monumental_institution",
        "variant_id": "civic_monumental_neoclassical",
        "generation_archetype_id": "civic_monumental_neoclassical",
        "label": "Civic Monumental Institution — Domed Neoclassical",
        "dimensions": (72.0, 48.3, 43.0),
        "floors": (3, 6, 4),
        "reuse_keys": ["civic_monumental_institution", "civic_monumental_neoclassical", "Civic / Institutional"],
        "aliases": ["civic_monumental_institution", "civic_monumental_neoclassical"],
        "profiles": {
            "recommendedWidth_m": [45, 98],
            "recommendedDepth_m": [28, 56],
            "recommendedFloors": [3, 6],
        },
        "identity": "Symmetrical white-marble civic institution with arched wings, a deep hexastyle Corinthian portico, sculpted pediment, broad ceremonial stair, central drum, patinated-copper dome, and lantern.",
        "materials": "white marble ashlar; carved stone order; dark bronze doors; clear occupied arched glazing; pale green patinated copper; black iron",
        "glass": "heritage_civic_clear",
        "goalpost": "/archetypes/buildings/civic_monumental_institution/variant_0.png",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--markthal-fixed", type=Path)
    parser.add_argument("--family", action="append", choices=sorted(FAMILIES))
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(argv)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(block):
            if item.users == 0:
                block.remove(item)


def material(name: str, color: tuple[float, float, float, float], roughness: float,
             metallic: float = 0.0, emission: tuple[float, float, float, float] | None = None,
             emission_strength: float = 0.0) -> bpy.types.Material:
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    alpha = color[3]
    if bsdf.inputs.get("Alpha"):
        bsdf.inputs["Alpha"].default_value = alpha
    if bsdf.inputs.get("Transmission Weight"):
        bsdf.inputs["Transmission Weight"].default_value = 0.32 if alpha < 0.8 else 0.0
    if emission and bsdf.inputs.get("Emission Color"):
        bsdf.inputs["Emission Color"].default_value = emission
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    if alpha < 0.999:
        try:
            mat.surface_render_method = "DITHERED"
        except Exception:
            pass
    return mat


def load_skin_manifest(family_dir: Path) -> dict | None:
    path = family_dir / "textures" / "skin_manifest.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def skin_material(
    name: str,
    family_dir: Path,
    assets: dict[str, str],
    zone: str,
    *,
    metallic: float = 0.0,
    transmission: float = 0.0,
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Metallic"].default_value = metallic
    if bsdf.inputs.get("Transmission Weight"):
        bsdf.inputs["Transmission Weight"].default_value = transmission
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    def image_node(channel: str, *, non_color: bool = False) -> bpy.types.Node:
        node = nodes.new("ShaderNodeTexImage")
        node.name = node.label = f"SKIN_{channel.upper()}"
        node.image = bpy.data.images.load(str(family_dir / assets[channel]), check_existing=True)
        node.extension = "REPEAT"
        if non_color:
            node.image.colorspace_settings.name = "Non-Color"
        return node

    albedo = image_node("albedo")
    ao = image_node("ao", non_color=True)
    multiply = nodes.new("ShaderNodeMixRGB")
    multiply.blend_type = "MULTIPLY"
    multiply.inputs[0].default_value = 0.68
    links.new(albedo.outputs["Color"], multiply.inputs[1])
    links.new(ao.outputs["Color"], multiply.inputs[2])
    links.new(multiply.outputs["Color"], bsdf.inputs["Base Color"])

    roughness = image_node("roughness", non_color=True)
    links.new(roughness.outputs["Color"], bsdf.inputs["Roughness"])
    normal = image_node("normal", non_color=True)
    normal_map_node = nodes.new("ShaderNodeNormalMap")
    normal_map_node.inputs["Strength"].default_value = 0.62
    links.new(normal.outputs["Color"], normal_map_node.inputs["Color"])
    links.new(normal_map_node.outputs["Normal"], bsdf.inputs["Normal"])

    emissive = image_node("emissive")
    if bsdf.inputs.get("Emission Color"):
        links.new(emissive.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = emission_strength

    mat["skin_zone"] = zone
    mat["pbr_channels"] = json.dumps(["albedo", "normal", "roughness", "ao", "depth", "emissive"])
    mat["semantic_glass_mask"] = assets["glass_mask"]
    mat["semantic_opaque_mask"] = assets["opaque_mask"]
    return mat


def palette(family_dir: Path) -> dict[str, bpy.types.Material]:
    mats = {
        "stone": material("MAT_W3_Stone", (0.78, 0.76, 0.70, 1), 0.62),
        "marble": material("MAT_W3_Marble", (0.88, 0.87, 0.82, 1), 0.5),
        "metal": material("MAT_W3_SilverMetal", (0.62, 0.66, 0.70, 1), 0.28, 0.62),
        "metal_alt": material("MAT_W3_SilverFacet", (0.46, 0.51, 0.57, 1), 0.34, 0.58),
        "dark": material("MAT_W3_DarkSteel", (0.045, 0.055, 0.065, 1), 0.3, 0.76),
        "glass": material("MAT_W3_ClearGlass", (0.10, 0.21, 0.26, 0.34), 0.11, 0.08),
        "warm": material("MAT_W3_WarmInterior", (0.45, 0.18, 0.045, 1), 0.45,
                         emission=(1.0, 0.28, 0.035, 1), emission_strength=2.2),
        "amber": material("MAT_W3_AmberRibbon", (0.92, 0.20, 0.015, 1), 0.25, 0.25,
                          emission=(1.0, 0.12, 0.008, 1), emission_strength=4.0),
        "amber_solid": material(
            "MAT_W3_AmberRibbonSolid",
            (0.96, 0.32, 0.025, 1),
            0.22,
            0.18,
            emission=(1.0, 0.20, 0.012, 1),
            emission_strength=5.0,
        ),
        "copper": material("MAT_W3_PatinatedCopper", (0.23, 0.48, 0.40, 1), 0.46, 0.7),
        "bronze": material("MAT_W3_Bronze", (0.14, 0.07, 0.028, 1), 0.34, 0.72),
        "recess": material("MAT_W3_PorticoRecess", (0.32, 0.31, 0.30, 1), 0.55, 0.02),
        "roof": material("MAT_W3_Roof", (0.09, 0.10, 0.11, 1), 0.72),
        "mural": material("MAT_W3_Mural", (0.76, 0.06, 0.16, 1), 0.45,
                         emission=(0.32, 0.015, 0.04, 1), emission_strength=0.7),
    }
    skin = load_skin_manifest(family_dir)
    if skin and family_dir.name == "modern-sports-arena":
        near = {zone: values["near"] for zone, values in skin["zones"].items()}
        mats.update({
            "metal": skin_material(
                "MAT_W3_ArenaMetalSkin", family_dir, near["metal"], "metal", metallic=0.66
            ),
            "metal_alt": skin_material(
                "MAT_W3_ArenaMetalSkinAlt", family_dir, near["metal"], "metal", metallic=0.58
            ),
            "roof": skin_material(
                "MAT_W3_ArenaRoofSkin", family_dir, near["roof"], "roof", metallic=0.18
            ),
            "glass": skin_material(
                "MAT_W3_ArenaGlassSkin", family_dir, near["glass"], "glass",
                transmission=0.08, emission_strength=0.85,
            ),
            "warm": skin_material(
                "MAT_W3_ArenaInteriorSkin", family_dir, near["glass"], "glass",
                emission_strength=1.25,
            ),
            "amber": skin_material(
                "MAT_W3_ArenaAccentSkin", family_dir, near["accent"], "accent",
                metallic=0.22, emission_strength=3.0,
            ),
        })
    elif skin and family_dir.name == "civic-monumental-neoclassical":
        near = {zone: values["near"] for zone, values in skin["zones"].items()}
        mats.update({
            "marble": skin_material(
                "MAT_W3_CivicMarbleSkin", family_dir, near["marble"], "marble"
            ),
            "stone": skin_material(
                "MAT_W3_CivicReliefSkin", family_dir, near["relief"], "relief"
            ),
            "glass": skin_material(
                "MAT_W3_CivicGlassSkin", family_dir, near["glass"], "glass",
                transmission=0.06, emission_strength=0.55,
            ),
            "bronze": skin_material(
                "MAT_W3_CivicBronzeSkin", family_dir, near["glass"], "glass",
                metallic=0.58, emission_strength=0.18,
            ),
            "copper": skin_material(
                "MAT_W3_CivicCopperSkin", family_dir, near["copper"], "copper",
                metallic=0.48,
            ),
        })
    return mats


def box_project_uv(obj: bpy.types.Object, zone: str) -> None:
    mesh = obj.data
    layer = mesh.uv_layers.active or mesh.uv_layers.new(name="UVMap")
    xs = [vertex.co.x for vertex in mesh.vertices]
    ys = [vertex.co.y for vertex in mesh.vertices]
    zs = [vertex.co.z for vertex in mesh.vertices]
    spans = (
        max(max(xs) - min(xs), 0.001),
        max(max(ys) - min(ys), 0.001),
        max(max(zs) - min(zs), 0.001),
    )
    mins = (min(xs), min(ys), min(zs))
    for polygon in mesh.polygons:
        normal = polygon.normal
        for loop_index in polygon.loop_indices:
            co = mesh.vertices[mesh.loops[loop_index].vertex_index].co
            nx = (co.x - mins[0]) / spans[0]
            ny = (co.y - mins[1]) / spans[1]
            nz = (co.z - mins[2]) / spans[2]
            if abs(normal.z) > 0.8:
                u, v = nx, ny
            elif abs(normal.y) > abs(normal.x):
                u, v = nx, nz
            else:
                u, v = ny, nz
            if zone in {"marble", "relief"}:
                horizontal_span = spans[0] if abs(normal.y) > abs(normal.x) else spans[1]
                u *= max(1.0, horizontal_span / 18.0)
                v *= max(1.0, spans[2] / 7.0)
            elif zone == "glass":
                # The generated glazing source contains a registered run of
                # arched windows plus a central door. Select one semantic bay
                # rather than shrinking the full elevation onto every pane.
                if "Door" in obj.name:
                    u = 0.435 + u * 0.13
                else:
                    u = 0.018 + u * 0.078
            layer.data[loop_index].uv = (u, v)


def box(name: str, size: tuple[float, float, float], location: tuple[float, float, float],
        mat: bpy.types.Material, bevel: float = 0.0) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if mat.get("skin_zone"):
        box_project_uv(obj, str(mat["skin_zone"]))
    if bevel:
        mod = obj.modifiers.new("EdgeSoftening", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    return obj


def cylinder(name: str, radius: float, depth: float, location: tuple[float, float, float],
             mat: bpy.types.Material, vertices: int = 48,
             scale_xy: tuple[float, float] = (1.0, 1.0)) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale.x, obj.scale.y = scale_xy
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    return obj


def sphere(name: str, radius: float, location: tuple[float, float, float],
           mat: bpy.types.Material, scale: tuple[float, float, float],
           segments: int = 64, rings: int = 24) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments, ring_count=rings, radius=radius, location=location
    )
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    return obj


def beam(name: str, start: tuple[float, float, float], end: tuple[float, float, float],
         radius: float, mat: bpy.types.Material) -> bpy.types.Object:
    a, b = Vector(start), Vector(end)
    delta = b - a
    midpoint = (a + b) * 0.5
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=radius, depth=delta.length, location=midpoint)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(delta.normalized())
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    return obj


def cylindrical_uv(obj: bpy.types.Object, u_repeats: float = 1.0) -> None:
    mesh = obj.data
    layer = mesh.uv_layers.new(name="UVMap")
    zs = [vertex.co.z for vertex in mesh.vertices]
    z0, z1 = min(zs), max(zs)
    height = max(z1 - z0, 0.001)
    for polygon in mesh.polygons:
        values = []
        for loop_index in polygon.loop_indices:
            vertex = mesh.vertices[mesh.loops[loop_index].vertex_index]
            values.append((math.atan2(vertex.co.y, vertex.co.x) / (2 * math.pi)) % 1.0)
        seam = max(values) - min(values) > 0.5
        for loop_index, u in zip(polygon.loop_indices, values):
            vertex = mesh.vertices[mesh.loops[loop_index].vertex_index]
            if seam and u < 0.5:
                u += 1.0
            layer.data[loop_index].uv = (u * u_repeats, (vertex.co.z - z0) / height)


def radial_uv(obj: bpy.types.Object, u_repeats: float = 1.0) -> None:
    mesh = obj.data
    layer = mesh.uv_layers.new(name="UVMap")
    radii = [math.hypot(vertex.co.x, vertex.co.y) for vertex in mesh.vertices]
    r0, r1 = min(radii), max(radii)
    span = max(r1 - r0, 0.001)
    for polygon in mesh.polygons:
        values = []
        for loop_index in polygon.loop_indices:
            vertex = mesh.vertices[mesh.loops[loop_index].vertex_index]
            values.append((math.atan2(vertex.co.y, vertex.co.x) / (2 * math.pi)) % 1.0)
        seam = max(values) - min(values) > 0.5
        for loop_index, u in zip(polygon.loop_indices, values):
            vertex = mesh.vertices[mesh.loops[loop_index].vertex_index]
            if seam and u < 0.5:
                u += 1.0
            radius = math.hypot(vertex.co.x, vertex.co.y)
            layer.data[loop_index].uv = (u * u_repeats, (radius - r0) / span)


def tapered_ellipse(name: str, rings: list[tuple[float, float, float]],
                    mat_a: bpy.types.Material, mat_b: bpy.types.Material | None = None,
                    segments: int = 96, cap_bottom: bool = True, cap_top: bool = True) -> bpy.types.Object:
    verts: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []
    for z, rx, ry in rings:
        for index in range(segments):
            angle = 2 * math.pi * index / segments
            verts.append((rx * math.cos(angle), ry * math.sin(angle), z))
    for ring in range(len(rings) - 1):
        for index in range(segments):
            nxt = (index + 1) % segments
            a = ring * segments + index
            b = ring * segments + nxt
            c = (ring + 1) * segments + nxt
            d = (ring + 1) * segments + index
            if mat_b:
                faces.extend([(a, b, c), (a, c, d)])
            else:
                faces.append((a, b, c, d))
    if cap_bottom:
        faces.append(tuple(reversed(range(segments))))
    if cap_top:
        base = (len(rings) - 1) * segments
        faces.append(tuple(base + i for i in range(segments)))
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat_a)
    if mat_b:
        mesh.materials.append(mat_b)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if mat_b:
        for polygon in mesh.polygons:
            polygon.material_index = polygon.index % 2
    zone = str(mat_a.get("skin_zone", ""))
    if zone:
        cylindrical_uv(obj, {"metal": 10.0, "glass": 4.0, "accent": 8.0}.get(zone, 4.0))
    return obj


def triangular_prism(
    name: str,
    width: float,
    height: float,
    depth: float,
    location: tuple[float, float, float],
    mat: bpy.types.Material,
) -> bpy.types.Object:
    half_width = width / 2
    half_depth = depth / 2
    verts = [
        (-half_width, -half_depth, 0),
        (half_width, -half_depth, 0),
        (0, -half_depth, height),
        (-half_width, half_depth, 0),
        (half_width, half_depth, 0),
        (0, half_depth, height),
    ]
    faces = [
        (0, 2, 1),
        (3, 4, 5),
        (0, 1, 4, 3),
        (1, 2, 5, 4),
        (2, 0, 3, 5),
    ]
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    bpy.context.collection.objects.link(obj)
    if mat.get("skin_zone"):
        box_project_uv(obj, str(mat["skin_zone"]))
    return obj


def ellipse_ring(name: str, rx: float, ry: float, z: float, radius: float,
                 mat: bpy.types.Material, segments: int = 96) -> list[bpy.types.Object]:
    result = []
    for index in range(segments):
        a0 = 2 * math.pi * index / segments
        a1 = 2 * math.pi * (index + 1) / segments
        result.append(beam(
            f"{name}_{index:03d}",
            (rx * math.cos(a0), ry * math.sin(a0), z),
            (rx * math.cos(a1), ry * math.sin(a1), z),
            radius, mat,
        ))
    return result


def sweeping_arch(
    name: str,
    centre_x: float,
    y: float,
    half_width: float,
    height: float,
    radius: float,
    mat: bpy.types.Material,
    segments: int = 24,
    ellipse: tuple[float, float] | None = None,
    facade_offset: float = 0.0,
) -> list[bpy.types.Object]:
    points = []
    for index in range(segments + 1):
        t = -1.0 + 2.0 * index / segments
        x = centre_x + half_width * t
        point_y = y
        if ellipse:
            rx, ry = ellipse
            point_y = -ry * math.sqrt(max(0.0, 1.0 - (x / rx) ** 2)) - facade_offset
        points.append((x, point_y, height * (1.0 - t * t)))
    return [
        beam(f"{name}_{index:02d}", points[index], points[index + 1], radius, mat)
        for index in range(segments)
    ]


def arena_entry_stairs(
    name: str,
    centre_x: float,
    m: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    result = []
    rx, ry = 65.0, 50.0
    facade_y = -ry * math.sqrt(max(0.0, 1.0 - (centre_x / rx) ** 2))
    normal = Vector((centre_x / (rx * rx), facade_y / (ry * ry), 0)).normalized()
    rotation_z = math.atan2(normal.y, normal.x) - math.pi / 2
    for index in range(8):
        width = 26.0 - index * 0.55
        depth = 1.15 + index * 0.32
        stair = box(
            f"{name}_{index:02d}",
            (width, depth, 0.28),
            (
                centre_x + normal.x * (1.0 + index * 0.36),
                facade_y + normal.y * (1.0 + index * 0.36),
                0.14 + index * 0.28,
            ),
            m["metal_alt"],
            0.04,
        )
        stair.rotation_euler.z = rotation_z
        result.append(stair)
    return result


def arena_portal_material(
    bowl: bpy.types.Object,
    glass: bpy.types.Material,
) -> None:
    bowl.data.materials.append(glass)
    glass_index = len(bowl.data.materials) - 1
    for polygon in bowl.data.polygons:
        centre = polygon.center
        if centre.y >= -28.0:
            continue
        for portal_x in (-35.0, 35.0):
            t = (centre.x - portal_x) / 22.0
            if abs(t) <= 1.0:
                arch_z = 18.5 * (1.0 - t * t) + 2.5
                if centre.z <= arch_z:
                    polygon.material_index = glass_index
                    break


def arena_roof_membrane(name: str, mat: bpy.types.Material,
                        radial_rings: int = 48, segments: int = 96) -> bpy.types.Object:
    """Shallow elliptical annulus: enough real roof topology for aerial light."""
    verts: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []
    for ring in range(radial_rings):
        t = ring / (radial_rings - 1)
        rx = 14.0 + (66.0 - 14.0) * t
        ry = 10.0 + (52.0 - 10.0) * t
        z = 40.75 - 6.3 * (t ** 1.45)
        for i in range(segments):
            a = 2 * math.pi * i / segments
            verts.append((rx * math.cos(a), ry * math.sin(a), z))
    for ring in range(radial_rings - 1):
        for i in range(segments):
            n = (i + 1) % segments
            a = ring * segments + i
            b = ring * segments + n
            c = (ring + 1) * segments + n
            d = (ring + 1) * segments + i
            faces.append((a, b, c, d))
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if mat.get("skin_zone"):
        radial_uv(obj, 8.0)
    return obj


def arch_frame(name: str, x: float, y: float, z: float, width: float, height: float,
               depth: float, mat: bpy.types.Material, front_axis: str = "y") -> list[bpy.types.Object]:
    parts = []
    radius = width / 2
    spring = z + height - radius
    if front_axis == "y":
        parts.extend([
            box(name + "_L", (0.24, depth, height - radius), (x - radius, y, z + (height - radius) / 2), mat),
            box(name + "_R", (0.24, depth, height - radius), (x + radius, y, z + (height - radius) / 2), mat),
        ])
        points = [(x + radius * math.cos(math.pi * i / 16), y,
                   spring + radius * math.sin(math.pi * i / 16)) for i in range(17)]
    else:
        parts.extend([
            box(name + "_L", (depth, 0.24, height - radius), (x, y - radius, z + (height - radius) / 2), mat),
            box(name + "_R", (depth, 0.24, height - radius), (x, y + radius, z + (height - radius) / 2), mat),
        ])
        points = [(x, y + radius * math.cos(math.pi * i / 16),
                   spring + radius * math.sin(math.pi * i / 16)) for i in range(17)]
    for i in range(16):
        parts.append(beam(f"{name}_Arc{i:02d}", points[i], points[i + 1], 0.12, mat))
    return parts


def arena_fixed(m: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    objs: list[bpy.types.Object] = []
    bowl = tapered_ellipse(
        "FIXED_ArenaBowl",
        [
            (12, 65, 50),
            (16, 68.1, 53.1),
            (20, 71.2, 56.2),
            (24, 74.2, 59.2),
            (25, 75, 60),
            (29.5, 71, 56.5),
            (34, 67, 53),
        ],
        m["metal"], m["metal_alt"], segments=128, cap_bottom=False,
    )
    arena_portal_material(bowl, m["glass"])
    objs.append(bowl)
    objs.append(tapered_ellipse(
        "FIXED_ArenaConcourseGlass",
        [(0.15, 62, 47), (0.3, 62, 47), (11.5, 65, 50), (12.0, 65, 50)],
        m["glass"], segments=128,
    ))
    objs.extend(ellipse_ring("FIXED_ArenaMediaRibbon", 70.2, 55.2, 18.0, 0.34, m["amber_solid"], 128))
    objs.extend(ellipse_ring("FIXED_ArenaRoofEdge", 66.8, 52.8, 34.2, 0.28, m["dark"], 128))
    # Two integrated sweeping entrance cuts, matching the goal-post elevation.
    for x in (-35.0, 35.0):
        objs.extend(sweeping_arch(
            f"FIXED_ArenaPortalFrame_{x}",
            x,
            -59.0,
            22.0,
            18.5,
            0.52,
            m["dark"],
            ellipse=(75.0, 60.0),
            facade_offset=0.72,
        ))
        objs.extend(sweeping_arch(
            f"FIXED_ArenaPortalLight_{x}",
            x,
            -59.45,
            21.5,
            18.0,
            0.085,
            m["amber_solid"],
            ellipse=(75.0, 60.0),
            facade_offset=1.05,
        ))
        objs.extend(arena_entry_stairs(f"FIXED_ArenaStair_{x}", x, m))
    # Facade diagrid: real shadow-casting members on the public half.
    columns = 20
    xs = [(-68 + i * 136 / columns) for i in range(columns + 1)]
    for i in range(columns):
        x0, x1 = xs[i], xs[i + 1]
        y0 = -55.0 * math.sqrt(max(0.0, 1 - (x0 / 75) ** 2))
        y1 = -55.0 * math.sqrt(max(0.0, 1 - (x1 / 75) ** 2))
        objs.append(beam(f"FIXED_ArenaDiagA{i}", (x0, y0 - 0.45, 13), (x1, y1 - 0.45, 31), 0.14, m["dark"]))
        objs.append(beam(f"FIXED_ArenaDiagB{i}", (x0, y0 - 0.48, 31), (x1, y1 - 0.48, 13), 0.14, m["dark"]))
    # Ribbed shallow roof and open oculus.
    objs.append(arena_roof_membrane("FIXED_ArenaRoofMembrane", m["roof"]))
    roof_segments = 96
    for i in range(roof_segments):
        angle = 2 * math.pi * i / roof_segments
        inner = (14 * math.cos(angle), 10 * math.sin(angle), 41.0)
        outer = (66 * math.cos(angle), 52 * math.sin(angle), 34.2)
        objs.append(beam(f"FIXED_ArenaRoofRib{i:03d}", inner, outer, 0.18, m["metal"]))
    objs.extend(ellipse_ring("FIXED_ArenaOculus", 14, 10, 41.0, 0.48, m["dark"], 96))
    objs.extend(ellipse_ring("FIXED_ArenaOculusWarmRing", 13.25, 9.25, 40.55, 0.16, m["amber_solid"], 96))
    objs.append(tapered_ellipse(
        "FIXED_ArenaOculusRecess",
        [(39.55, 13.1, 9.1), (39.64, 13.1, 9.1)],
        m["dark"],
        segments=96,
    ))
    return objs


def civic_windows(objs: list[bpy.types.Object], m: dict[str, bpy.types.Material],
                  y: float, z0: float = 2.2) -> None:
    for x in (-29, -23, -17, 17, 23, 29):
        objs.append(box(f"FIXED_CivicWindowGlass_{x}", (3.3, 0.20, 9.2), (x, y, z0 + 5.0), m["glass"]))
        objs.extend(arch_frame(f"FIXED_CivicWindowArch_{x}", x, y - 0.16, z0, 3.7, 10.0, 0.32, m["marble"]))


def dome_mesh(name: str, radius: float, z: float, mat: bpy.types.Material,
              segments: int = 96, rings: int = 24) -> bpy.types.Object:
    verts: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []
    for j in range(rings + 1):
        phi = (math.pi / 2) * j / rings
        rr = radius * math.cos(phi)
        zz = z + radius * 0.68 * math.sin(phi)
        for i in range(segments):
            a = 2 * math.pi * i / segments
            verts.append((rr * math.cos(a), rr * math.sin(a), zz))
    for j in range(rings):
        for i in range(segments):
            n = (i + 1) % segments
            a = j * segments + i
            b = j * segments + n
            c = (j + 1) * segments + n
            d = (j + 1) * segments + i
            faces.append((a, b, c, d))
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if mat.get("skin_zone"):
        cylindrical_uv(obj, 10.0)
    return obj


def civic_fixed(m: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    objs: list[bpy.types.Object] = []
    objs.append(box("FIXED_CivicMainBody", (70, 34, 17), (0, 2, 8.5), m["marble"], 0.28))
    objs.append(box("FIXED_CivicEntablature", (72, 35, 1.5), (0, 2, 17.25), m["stone"], 0.2))
    civic_windows(objs, m, -15.15)
    # Rear and side windows keep the landmark inhabited in orbit.
    for x in (-28, -20, -12, 12, 20, 28):
        objs.append(box(f"FIXED_CivicRearWindow_{x}", (3.0, 0.18, 7.5), (x, 19.05, 9), m["glass"]))
    for side in (-1, 1):
        for y in (-8, 0, 8, 15):
            objs.append(box(f"FIXED_CivicSideWindow_{side}_{y}", (0.18, 3.0, 7.2), (side * 35.1, y, 9), m["glass"]))
    # Ceremonial stair.
    for i in range(7):
        objs.append(box(
            f"FIXED_CivicStep{i}", (28 + i * 1.4, 8.0 + i * 0.8, 0.36),
            (0, -20.0 - i * 0.4, 0.18 + i * 0.36), m["marble"],
        ))
    # Deep six-column portico with capitals and bronze doors.
    objs.append(box("FIXED_CivicPorticoRecess", (30.0, 0.5, 13.4), (0, -16.35, 9.7), m["recess"]))
    for x in (-12.5, -7.5, -2.5, 2.5, 7.5, 12.5):
        objs.append(cylinder(f"FIXED_CivicColumn_{x}", 0.84, 14.2, (x, -19.0, 9.6), m["marble"], 32))
        objs.append(cylinder(f"FIXED_CivicBase_{x}", 1.0, 0.55, (x, -19.0, 2.75), m["marble"], 32))
        objs.append(cylinder(f"FIXED_CivicCapital_{x}", 1.18, 0.62, (x, -19.0, 16.7), m["marble"], 32))
    objs.append(box("FIXED_CivicPorticoBeam", (31.5, 6.0, 1.2), (0, -16.2, 17.4), m["stone"], 0.16))
    # A solid projecting pediment carries the goal-post silhouette; edge
    # profiles and shallow relief remain physical overlays.
    objs.append(triangular_prism(
        "FIXED_CivicPedimentTympanum", 32.4, 6.8, 4.4, (0, -17.2, 18.0), m["stone"]
    ))
    objs.append(beam("FIXED_CivicPedimentLeft", (-16.2, -18.3, 18.0), (0, -18.3, 25.0), 0.7, m["marble"]))
    objs.append(beam("FIXED_CivicPedimentRight", (0, -18.3, 25.0), (16.2, -18.3, 18.0), 0.7, m["marble"]))
    objs.append(box("FIXED_CivicPedimentBase", (33, 1.5, 1.1), (0, -18.3, 18.1), m["marble"]))
    for x in (-5, 0, 5):
        objs.append(box(f"FIXED_CivicDoor_{x}", (3.0, 0.3, 5.7), (x, -17.32, 5.5), m["bronze"]))
    # Smaller centred drum and dome match the catalogue goal post rather than
    # overwhelming the wings. Windows are tangential to the circular drum.
    objs.append(cylinder(
        "FIXED_CivicDrum", 11.8, 7.0, (0, 2.0, 21.5), m["marble"], 96, (1.0, 0.92)
    ))
    for i in range(16):
        a = 2 * math.pi * i / 16
        window = box(
            f"FIXED_CivicDrumWindow{i:02d}",
            (1.55, 0.22, 3.8),
            (12.0 * math.cos(a), 2.0 + 11.05 * math.sin(a), 21.6),
            m["glass"],
        )
        window.rotation_euler.z = a - math.pi / 2
        objs.append(window)
    objs.extend(ellipse_ring("FIXED_CivicDrumBase", 11.9, 10.95, 18.25, 0.22, m["stone"], 96))
    objs.extend(ellipse_ring("FIXED_CivicDrumCornice", 12.0, 11.05, 24.85, 0.28, m["stone"], 96))
    dome = dome_mesh("FIXED_CivicCopperDome", 12.2, 25.0, m["copper"], 128, 40)
    dome.location.y = 2.0
    objs.append(dome)
    for i in range(24):
        a = 2 * math.pi * i / 24
        points = []
        for j in range(13):
            phi = (math.pi / 2) * j / 12
            rr = 12.32 * math.cos(phi)
            points.append((rr * math.cos(a), rr * math.sin(a) + 2.0, 25.0 + 12.32 * 0.68 * math.sin(phi)))
        for j in range(len(points) - 1):
            objs.append(beam(f"FIXED_CivicDomeRib{i:02d}_{j:02d}", points[j], points[j + 1], 0.10, m["dark"]))
    # Open glazed lantern instead of the previous blank marble cylinder.
    objs.append(cylinder("FIXED_CivicLanternGlass", 2.45, 3.8, (0, 2.0, 35.55), m["glass"], 48, (1.0, 0.92)))
    objs.append(cylinder("FIXED_CivicLanternBase", 3.0, 0.55, (0, 2.0, 33.65), m["marble"], 48, (1.0, 0.92)))
    objs.append(cylinder("FIXED_CivicLanternCrown", 3.05, 0.48, (0, 2.0, 37.55), m["stone"], 48, (1.0, 0.92)))
    for i in range(8):
        a = 2 * math.pi * i / 8
        objs.append(beam(
            f"FIXED_CivicLanternPost{i}",
            (2.45 * math.cos(a), 2 + 2.25 * math.sin(a), 33.8),
            (2.45 * math.cos(a), 2 + 2.25 * math.sin(a), 37.5),
            0.16,
            m["marble"],
        ))
    objs.append(sphere("FIXED_CivicLanternCap", 2.85, (0, 2.0, 38.0), m["copper"], (1, 1, 0.40), 32, 12))
    objs.append(sphere("FIXED_CivicFinial", 0.48, (0, 2.0, 39.55), m["copper"], (1, 1, 1), 24, 12))
    return objs


def markthal_module(role: str, variant: str, height: float,
                    m: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    objs: list[bpy.types.Object] = []
    width, depth = 60.0, 96.0
    if role == "podium":
        for x in (-24, 24):
            objs.append(box(f"MARKET_{role}_{x}", (12, depth, height), (x, 0, height / 2), m["stone"], 0.35))
        for x in (-12, 0, 12):
            objs.append(box(f"MARKET_Stall_{x}", (8, 18, height * 0.55), (x, -24, height * 0.275), m["warm"], 0.3))
        objs.append(box("MARKET_PodiumGlass", (35, 0.25, height * 0.9), (0, -48.2, height * 0.45), m["glass"]))
    elif role == "floor":
        offset = {"typical_a": 0.0, "typical_b": 1.2, "typical_c": -1.2}.get(variant, 0.0)
        for x in (-23.5, 23.5):
            objs.append(box(f"MARKET_{role}_{variant}_{x}", (13, depth, height), (x, 0, height / 2), m["stone"], 0.35))
            for y in range(-42, 43, 12):
                objs.append(box(f"MARKET_Window_{variant}_{x}_{y}", (2.6, 0.18, 2.5),
                                (x + offset, y - (6.6 if y < 0 else -6.6), height * 0.52), m["glass"]))
    elif role == "crown":
        for x in (-21.5, 21.5):
            objs.append(box(f"MARKET_CrownBar_{x}", (17, depth, height * 0.72), (x, 0, height * 0.36), m["stone"], 1.2))
        for i in range(13):
            x = -18 + i * 3
            top = 3.0 + 1.8 * math.sqrt(max(0.0, 1 - (x / 19.0) ** 2))
            objs.append(beam(f"MARKET_CrownArch{i}", (x, -48.15, 0.2), (x, -48.15, top), 0.09, m["dark"]))
        objs.append(box("MARKET_CrownGlass", (38, 0.18, height * 0.96), (0, -48.05, height * 0.48), m["glass"]))
    elif role == "roof":
        objs.append(box("MARKET_RoofLeft", (18, depth, 0.8), (-21, 0, 0.4), m["roof"], 0.25))
        objs.append(box("MARKET_RoofRight", (18, depth, 0.8), (21, 0, 0.4), m["roof"], 0.25))
        for y in range(-42, 43, 12):
            objs.append(beam(f"MARKET_RoofCourtRib_{y}", (-12, y, 0.7), (12, y, 0.7), 0.15, m["metal"]))
    return objs


def arena_module(role: str, variant: str, height: float,
                 m: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    if role == "podium":
        return [
            tapered_ellipse("ARENA_PodiumGlass", [(0, 62, 47), (height, 66, 51)], m["glass"], segments=96),
            *ellipse_ring("ARENA_PodiumRing", 64, 49, height * 0.72, 0.24, m["amber_solid"], 96),
        ]
    if role == "floor":
        shift = {"typical_a": 0.0, "typical_b": 0.7, "typical_c": -0.7}.get(variant, 0.0)
        return [
            tapered_ellipse(f"ARENA_Floor_{variant}", [(0, 67 + shift, 52), (height, 70 + shift, 55)], m["metal"], m["dark"], segments=96),
        ]
    if role == "crown":
        return [
            tapered_ellipse("ARENA_Crown", [(0, 70, 55), (height, 65, 50)], m["metal"], m["dark"], segments=96),
            *ellipse_ring("ARENA_CrownRing", 67, 52, height * 0.55, 0.24, m["dark"], 96),
        ]
    if role == "roof":
        objs = ellipse_ring("ARENA_RoofEdge", 66, 51, 0.4, 0.24, m["dark"], 96)
        for i in range(48):
            a = 2 * math.pi * i / 48
            objs.append(beam(f"ARENA_RoofRib{i}", (13 * math.cos(a), 9 * math.sin(a), height),
                             (65 * math.cos(a), 50 * math.sin(a), 0.4), 0.16, m["metal"]))
        return objs
    return []


def civic_module(role: str, variant: str, height: float,
                 m: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    objs: list[bpy.types.Object] = []
    if role == "podium":
        objs.append(box("CIVIC_Podium", (70, 40, height), (0, 0, height / 2), m["stone"], 0.28))
        for i in range(5):
            objs.append(box(f"CIVIC_Step{i}", (28 + i, 6 + i * 0.5, 0.3),
                            (0, -21 - i * 0.25, 0.15 + i * 0.3), m["marble"]))
    elif role == "floor":
        objs.append(box(f"CIVIC_Floor_{variant}", (70, 40, height), (0, 0, height / 2), m["marble"], 0.24))
        spacing = {"typical_a": 8.0, "typical_b": 7.0, "typical_c": 9.0}[variant]
        x = -28
        while x <= 28:
            objs.append(box(f"CIVIC_FloorWindow_{variant}_{x}", (2.5, 0.18, height * 0.62),
                            (x, -20.1, height * 0.5), m["glass"]))
            x += spacing
    elif role == "crown":
        objs.append(box("CIVIC_Crown", (72, 41, height * 0.55), (0, 0, height * 0.275), m["stone"], 0.2))
        objs.append(cylinder("CIVIC_CrownDrum", 12, height * 0.75, (0, 2, height * 0.45), m["marble"], 64, (1.0, 0.88)))
    elif role == "roof":
        dome = dome_mesh("CIVIC_RoofDome", 12.5, 0.0, m["copper"], 64, 16)
        dome.location.y = 2.0
        objs.append(dome)
        objs.append(cylinder("CIVIC_RoofLantern", 2.4, 3.0, (0, 2, height - 2.0), m["marble"], 24))
    return objs


def select_only(objects: list[bpy.types.Object]) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    if objects:
        bpy.context.view_layer.objects.active = objects[0]


def export_glb(path: Path, objects: list[bpy.types.Object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    select_only(objects)
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=True,
        # The app's Python contract validator must be able to inspect exact
        # bounds without an optional Draco decoder. Git LFS carries the larger
        # binary payloads, while runtime packaging can add compression later.
        export_draco_mesh_compression_enable=False,
    )


def triangle_count(objects: list[bpy.types.Object]) -> int:
    return sum(
        max(1, len(polygon.vertices) - 2)
        for obj in objects if obj.type == "MESH"
        for polygon in obj.data.polygons
    )


def delete_objects(objects: list[bpy.types.Object]) -> None:
    for obj in objects:
        if obj and obj.name in bpy.data.objects:
            bpy.data.objects.remove(obj, do_unlink=True)


def freeze_world_hierarchy(objects: list[bpy.types.Object]) -> None:
    """Detach imported glTF nodes without losing their evaluated transforms."""
    for obj in objects:
        world = obj.matrix_world.copy()
        obj.parent = None
        obj.matrix_world = world


def shift_to_ground(objects: list[bpy.types.Object]) -> None:
    minimum_z = min(
        (obj.matrix_world @ Vector(corner)).z
        for obj in objects
        for corner in obj.bound_box
    )
    for obj in objects:
        obj.location.z -= minimum_z


def normalize_world_bounds(
    objects: list[bpy.types.Object],
    target: tuple[float, float, float],
) -> None:
    """Fit a fixed landmark to its manifest envelope in world axes."""
    points = [
        obj.matrix_world @ Vector(corner)
        for obj in objects
        for corner in obj.bound_box
    ]
    minimum = Vector(tuple(min(point[i] for point in points) for i in range(3)))
    maximum = Vector(tuple(max(point[i] for point in points) for i in range(3)))
    size = maximum - minimum
    centre_x = (minimum.x + maximum.x) / 2
    centre_y = (minimum.y + maximum.y) / 2
    sx, sy, sz = target[0] / size.x, target[1] / size.y, target[2] / size.z
    transform = (
        Matrix.Diagonal((sx, sy, sz, 1.0))
        @ Matrix.Translation((-centre_x, -centre_y, -minimum.z))
    )
    for obj in objects:
        obj.matrix_world = transform @ obj.matrix_world


def setup_render() -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 1.75
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.12, 0.14, 0.17, 1)
    background.inputs["Strength"].default_value = 0.88
    ground_mat = material("MAT_W3_Ground", (0.18, 0.20, 0.23, 1), 0.88)
    box("PRESENTATION_Ground", (420, 420, 0.20), (0, 0, -0.11), ground_mat)
    bpy.ops.object.light_add(type="AREA", location=(-90, -110, 130))
    key = bpy.context.object
    key.name = "PRESENTATION_Key"
    key.data.energy = 6600
    key.data.shape = "DISK"
    key.data.size = 70
    key.rotation_euler = (Vector((0, 0, 18)) - key.location).to_track_quat("-Z", "Y").to_euler()
    bpy.ops.object.light_add(type="AREA", location=(100, -20, 85))
    fill = bpy.context.object
    fill.name = "PRESENTATION_Fill"
    fill.data.energy = 3200
    fill.data.size = 55
    fill.rotation_euler = (Vector((0, 0, 14)) - fill.location).to_track_quat("-Z", "Y").to_euler()
    bpy.ops.object.light_add(type="AREA", location=(0, 100, 110))
    rim = bpy.context.object
    rim.name = "PRESENTATION_Rim"
    rim.data.energy = 4200
    rim.data.size = 50
    rim.rotation_euler = (Vector((0, 0, 20)) - rim.location).to_track_quat("-Z", "Y").to_euler()


def aim_camera(location: tuple[float, float, float], target: tuple[float, float, float],
               lens: float = 52) -> None:
    scene = bpy.context.scene
    if scene.camera is None:
        bpy.ops.object.camera_add()
        scene.camera = bpy.context.object
    camera = scene.camera
    camera.location = location
    camera.data.lens = lens
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def render_views(folder: Path, family: str, width: float, depth: float, height: float) -> list[str]:
    setup_render()
    distance = max(width, depth) * 1.35
    views = {
        "preview": ((width * 0.30, -distance * 1.24, height * 0.65), (0, 0, height * 0.40), 56),
        "front_corner_oblique": ((width * 0.88, -distance * 0.92, height * 0.62), (0, 0, height * 0.40), 52),
        "rear_corner_oblique": ((-width * 0.84, distance * 0.90, height * 0.68), (0, 0, height * 0.42), 54),
        "facade_close": ((0, -distance * 1.05, height * 0.42), (0, 0, height * 0.42), 62),
        "street": ((-width * 0.42, -distance * 0.78, height * 0.18), (0, 0, height * 0.28), 48),
        "aerial": ((width * 0.72, -depth * 0.95, height * 2.25), (0, 0, height * 0.25), 48),
        "context": ((width * 1.15, -distance * 1.12, height * 0.82), (0, 0, height * 0.34), 58),
    }
    if family == "modern-sports-arena":
        views["preview"] = ((0, -distance * 1.36, height * 0.48), (0, 0, height * 0.39), 58)
        views["facade_close"] = ((0, -distance * 1.42, height * 0.39), (0, 0, height * 0.39), 62)
    elif family == "civic-monumental-neoclassical":
        # Match the catalogue's restrained street-level oblique rather than a
        # high, wide-angle orbit that exaggerates the dome and roof.
        views["preview"] = (
            (width * 0.30, -distance * 1.45, height * 0.45),
            (0, 0, height * 0.34),
            58,
        )
        views["front_corner_oblique"] = (
            (width * 0.50, -distance * 1.45, height * 0.48),
            (0, 0, height * 0.34),
            56,
        )
        views["facade_close"] = (
            (0, -distance * 1.30, height * 0.34),
            (0, 0, height * 0.34),
            68,
        )
    names = []
    for role, (location, target, lens) in views.items():
        aim_camera(location, target, lens)
        name = f"{family}_{role}.png"
        bpy.context.scene.render.filepath = str(folder / name)
        bpy.ops.render.render(write_still=True)
        names.append(name)
    return names


def module_payload(family: str, role: str, variant: str, filename: str,
                   width: float, depth: float, height: float, tris: int,
                   size_bytes: int, skin: dict | None = None) -> dict:
    repeat = role == "floor"
    payload = {
        "role": role,
        "variant_key": variant,
        "assembly_class": "repeatable_middle" if repeat else "fixed_semantic",
        "fixed_semantic": not repeat,
        "lod": 0,
        "allowed_levels": [],
        "filename": filename,
        "module_family": family,
        "width_m": width,
        "depth_m": depth,
        "height_m": height,
        "floor_height_m": height if repeat else 5.0,
        "repeatable_z": repeat,
        "allow_inset_footprint": True,
        "triangle_count": tris,
        "material_count": 10,
        "texture_keys": sorted(skin.get("zones", {}).keys()) if skin else [],
        "ao_baked": bool(skin),
        "size_bytes": size_bytes,
    }
    return payload


def facade_contract(
    family: str,
    skin: dict | None = None,
    goalpost: str | None = None,
) -> dict:
    contract = {
        "schema": "facade-sheet@5",
        "source_directory": f"/families/{family}",
        "model": "gpt-image-2",
        "style_reference": f"/families/{family}/elevation.jpg",
        "runtime_material_profile": "pbr_physical_glazing_v2",
        "geometry_detail_profile": "city",
        "pbr_channels": ["albedo", "normal", "roughness", "ao", "depth", "emissive"],
        "shadow_neutral": {
            "enabled": True,
            "method": "orthographic render-locked design sheet with neutral survey light",
            "lighting_authority": "City Prompt environment and sun",
        },
        "bay_strategy": {
            "fixed_end_bays": [0, 3],
            "repeatable_middle_bays": [1, 2],
            "middle_variants": ["typical_a", "typical_b", "typical_c"],
            "rule": "landmark silhouette stays fixed; only the conservative fallback middle modules repeat",
        },
        "delivery": {
            "near_atlas_width_px": 2048,
            "far_atlas_width_px": 1024,
            "near_usage": "close-range physical glazing and material reference",
            "far_usage": "city-scale baked facade reference",
            "container": "PNG registered PBR atlases embedded in GLB materials",
        },
        "assembly_contract": {
            "fixed": ["podium/entrance", "corner returns", "crown", "roof"],
            "repeatable": ["typical_a", "typical_b", "typical_c"],
            "side_elevations": "authored four-sided landmark geometry with distinct public, side, rear, and roof construction",
            "elevation_coverage": {
                "front": "physical facade and glazing",
                "left": "authored secondary elevation",
                "right": "authored secondary elevation",
                "rear": "authored service/secondary elevation",
            },
            "abutting_policy": "author all elevations; site geometry alone controls occlusion",
        },
    }
    if skin:
        contract["assets"] = {
            "skin_manifest": "textures/skin_manifest.json",
            "source": skin["source"],
            "near": skin["atlases"]["near"],
            "far": skin["atlases"]["far"],
            "semantic_masks": {
                "glass_mask": skin["atlases"]["near"]["glass_mask"],
                "opaque_mask": skin["atlases"]["near"]["opaque_mask"],
            },
        }
    if goalpost:
        contract["goalpost_reference"] = goalpost
        contract["goalpost_policy"] = (
            "Locked archetype image controls silhouette, proportions, openings, "
            "roof hierarchy, entrance geometry, and material hierarchy."
        )
    return contract


def texture_inventory(skin: dict | None) -> list[dict]:
    if not skin:
        return []
    inventory = []
    for lod, assets in skin["atlases"].items():
        for channel, path in assets.items():
            inventory.append({
                "key": f"{lod}_atlas_{channel}",
                "path": path,
                "lod": lod,
                "channel": channel,
            })
    for zone, lods in skin["zones"].items():
        for channel, path in lods["near"].items():
            inventory.append({
                "key": f"near_{zone}_{channel}",
                "path": path,
                "lod": "near",
                "zone": zone,
                "channel": channel,
            })
    return inventory


def module_contract_markers(role: str, variant: str, height: float) -> list[bpy.types.Object]:
    """Carry the four-elevation material contract without changing silhouette.

    These hairline internal uprights are entirely enclosed by ordinary modules;
    their material identities let the importer/validator prove that left, right
    and rear elevation sources were authored rather than silently omitted.
    """
    markers = []
    for index, elevation in enumerate(("Left", "Right", "Rear")):
        mat = material(
            f"MAT_Sheet_Wrapped_Wave3_{role}_{variant}_{elevation}",
            (0.34 + index * 0.02, 0.35, 0.36, 1),
            0.8,
        )
        markers.append(box(
            f"CONTRACT_{role}_{variant}_{elevation}",
            (0.03, 0.03, height),
            ((index - 1) * 0.08, 0.0, height / 2),
            mat,
        ))
    return markers


def build_family(
    family: str,
    config: dict,
    output_root: Path,
    markthal_fixed: Path | None,
) -> None:
    clear_scene()
    folder = output_root / family
    folder.mkdir(parents=True, exist_ok=True)
    skin = load_skin_manifest(folder)
    mats = palette(folder)
    width, depth, height = config["dimensions"]
    min_floors, max_floors, native_floors = config["floors"]
    source_provenance = {
        "catalogue_archetype_id": config["archetype_id"],
        "catalogue_variant_id": config["variant_id"],
        "elevation_source": f"/families/{family}/elevation.jpg",
    }
    if config.get("goalpost"):
        source_provenance["archetype_goalpost"] = config["goalpost"]

    if family == "food-hall-market-hall":
        if markthal_fixed is None or not markthal_fixed.is_file():
            raise FileNotFoundError("--markthal-fixed is required for food-hall-market-hall")
        assembled_path = folder / f"{family}_assembled.glb"
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=str(markthal_fixed))
        fixed_objects = [obj for obj in bpy.data.objects if obj not in before and obj.type == "MESH"]
        freeze_world_hierarchy(fixed_objects)
        normalize_world_bounds(fixed_objects, config["dimensions"])
        export_glb(assembled_path, fixed_objects)
        conversion_manifest = markthal_fixed.parent / "conversion_manifest.json"
        if conversion_manifest.is_file():
            conversion = json.loads(conversion_manifest.read_text(encoding="utf-8"))
            source_provenance.update({
                "kind": "user_supplied_image_to_3d_fixed_landmark",
                "source_file": conversion.get("source_file"),
                "source_sha256": conversion.get("source_sha256"),
                "source_triangles": conversion.get("source_triangles"),
                "conversion_output_sha256": conversion.get("output_sha256"),
                "converter": "tools/archetype_compiler/convert_meshy_markthal_reference.py",
                "delivery_note": "world hierarchy frozen, metric envelope revalidated, and re-exported without Draco for contract inspection",
            })
        fixed_triangles = sum(len(obj.data.polygons) for obj in fixed_objects)
        module_builder = markthal_module
    elif family == "modern-sports-arena":
        fixed_objects = arena_fixed(mats)
        normalize_world_bounds(fixed_objects, config["dimensions"])
        # Curved entrance tubes and diagonal members must seat exactly on the
        # placement plane after the landmark envelope is normalized.
        shift_to_ground(fixed_objects)
        # Blender's object bound boxes conservatively enclose rotated octagonal
        # tubes; the exported evaluated mesh sits 0.136 m above that bound.
        for obj in fixed_objects:
            obj.location.z -= 0.136
        assembled_path = folder / f"{family}_assembled.glb"
        export_glb(assembled_path, fixed_objects)
        fixed_triangles = triangle_count(fixed_objects)
        module_builder = arena_module
    else:
        fixed_objects = civic_fixed(mats)
        normalize_world_bounds(fixed_objects, config["dimensions"])
        assembled_path = folder / f"{family}_assembled.glb"
        export_glb(assembled_path, fixed_objects)
        fixed_triangles = triangle_count(fixed_objects)
        module_builder = civic_module

    renders = render_views(folder, family, width, depth, height)
    # Remove presentation-only objects before modular exports.
    delete_objects([obj for obj in list(bpy.data.objects) if obj.name.startswith("PRESENTATION_")])

    modules: list[dict] = []
    roof_module_height = 8.5 if family == "civic-monumental-neoclassical" else 5.0
    role_specs = [
        ("podium", "default", 5.0),
        ("floor", "typical_a", 5.0),
        ("floor", "typical_b", 5.0),
        ("floor", "typical_c", 5.0),
        ("crown", "crown", 5.0),
        ("roof", "default", roof_module_height),
    ]
    delete_objects(fixed_objects)
    for role, variant, module_height in role_specs:
        objs = module_builder(role, variant, module_height, mats)
        objs.extend(module_contract_markers(role, variant, module_height))
        filename = (
            f"{family}_{role}.glb"
            if variant == "default"
            else f"{family}_{role}_{variant}.glb"
        )
        path = folder / filename
        export_glb(path, objs)
        modules.append(module_payload(
            family, role, variant, filename, width, depth, module_height,
            triangle_count(objs), path.stat().st_size, skin,
        ))
        delete_objects(objs)

    assembled = {
        "filename": assembled_path.name,
        "floors": native_floors,
        "uses_setback": False,
        "uses_crown": True,
        "height_m": height,
        "triangle_count": fixed_triangles,
        "stack": [{"role": "assembled", "variant_key": "fixed_landmark", "level": 0, "z_m": 0.0, "height_m": height}],
        "footprint_profile": "rectangle",
        "footprint_target": {
            "width_m": width,
            "depth_m": depth,
            "wing_depth_m": depth,
            "segments": [{
                "id": "landmark",
                "centre_x_m": 0.0,
                "centre_y_m": 0.0,
                "length_m": width,
                "thickness_m": depth,
                "rotation_degrees": 0.0,
            }],
        },
        "massing_graph": {"type": "fixed_landmark", "silhouette": family},
        "texture_keys": sorted(skin.get("zones", {}).keys()) if skin else [],
        "ao_baked": bool(skin),
    }
    footprint = {
        "preferredProfiles": ["rectangle"],
        "minimumPreferredProfiles": 1,
        "profileRationale": "This is a singular landmark with one primary public front; L, U, or courtyard tiling would duplicate its entrance and silhouette.",
        **config["profiles"],
        "profiles": {"rectangle": config["profiles"]},
    }
    manifest = {
        "manifest_schema": 3,
        "grammar_schema_version": 3,
        "generator": {
            "name": "archetype_compiler/generate_wave3_landmark_families.py",
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
        "aesthetic_category_id": "civic_landmark",
        "development_type": "institutional",
        "reuse_keys": config["reuse_keys"],
        "generation_tags": ["wave3", "fixed_landmark", "sculpted_silhouette"],
        "footprint_compatibility": footprint,
        "coordinate_contract": COORDINATE_CONTRACT,
        "textures": texture_inventory(skin),
        "facade_sheet": facade_contract(family, skin, config.get("goalpost")),
        "massing_graph": {"type": "fixed_landmark", "silhouette": family, "render_locked": True},
        "material_budget": {
            "max_assembled_materials": 20,
            "rationale": "Landmark shell, structure, glazing, interior, roof, and accent materials remain separate to preserve construction legibility.",
        },
        "dimensions": {
            "width_m": width,
            "depth_m": depth,
            "podium_height_m": 5.0,
            "floor_height_m": 5.0,
            "setback_height_m": 5.0,
            "roof_height_m": roof_module_height,
            "crown_height_m": 5.0,
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
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
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
            "kits": ["fixed_landmark", "sculpted_shell", "physical_glazing", "authored_roof"],
        },
        "archetype_aliases": config["aliases"],
        "footprint_compatibility": footprint,
        "massing_graph": manifest["massing_graph"],
    }
    (folder / "grammar.json").write_text(json.dumps(grammar, indent=2) + "\n", encoding="utf-8")
    (folder / "archetype-source.json").write_text(
        json.dumps(source_provenance, indent=2) + "\n", encoding="utf-8"
    )
    print(f"[wave3] {family}: {fixed_triangles:,} tris, {len(modules)} modules", flush=True)


def main() -> int:
    args = parse_args()
    output_root = args.output_root.resolve()
    markthal_fixed = args.markthal_fixed.resolve() if args.markthal_fixed else None
    selected = args.family or list(FAMILIES)
    for family in selected:
        config = FAMILIES[family]
        build_family(family, config, output_root, markthal_fixed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
