"""Blender headless generator for archetype-compiled modular GLBs.

Run (Blender 4.x / 5.x):

  blender --background --factory-startup --python blender_generate.py -- \
      --grammar build/nordic-grammar.json --output build/nordic [--floors 6] \
      [--keep-blend] [--no-thumbnail] [--no-assembled]

Coordinate decisions (Blender side of the contract):
- Blender is Z-up; every module is built with its base at z=0 and centred on
  the XY origin, so "origin at bottom centre" holds by construction.
- The front facade faces NEGATIVE Y. The glTF exporter is run with
  ``export_yup=True``; Blender -Y (front) becomes glTF +Z, which three.js
  treats as "toward the default camera" — the assembled preview therefore
  faces the viewer without extra rotation.
- All transforms are applied before export; module parts are joined into a
  single mesh named MOD_<Role> so the GLB has one node per module.
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

GENERATOR_VERSION = "0.7.0"
SUPPORTED_SCHEMA_VERSION = 3

# Set from CLI in main(); make_material reads them so build_materials stays a
# pure function of the grammar.
TEXTURES_DIR: Path | None = None
DEFAULT_TEXTURES_DIR = Path(__file__).resolve().parent / "textures"
UV_TILE_METRES = 2.0  # one texture tile covers 2 m of facade (matches generate_textures.py prompts)
INTERIOR_ATLAS_FILENAME = "interior-atlas-gpt-v1.jpg"
INTERIOR_ATLAS_COLUMNS = 4
INTERIOR_ATLAS_ROWS = 2


# ---------------------------------------------------------------------------
# Scene plumbing
# ---------------------------------------------------------------------------

def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    # Purge orphan meshes/materials so repeated module builds don't accumulate
    for block_list in (bpy.data.meshes, bpy.data.lights, bpy.data.cameras):
        for block in list(block_list):
            if block.users == 0:
                block_list.remove(block)


def configure_units() -> None:
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = "METERS"


def hex_rgba(value: str, alpha: float = 1.0) -> tuple[float, float, float, float]:
    value = (value or "#808080").lstrip("#")
    if len(value) != 6:
        value = "808080"
    # sRGB hex -> linear, otherwise exported colours look washed out
    def lin(channel: float) -> float:
        return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4

    r, g, b = (int(value[i : i + 2], 16) / 255 for i in (0, 2, 4))
    return (lin(r), lin(g), lin(b), alpha)


def _texture_set(texture_key: str | None) -> dict[str, Path] | None:
    """Resolve a texture_key to its on-disk set; None when absent so the
    pipeline keeps working with zero textures (flat-colour fallback)."""
    if not texture_key or TEXTURES_DIR is None:
        return None
    roots = [TEXTURES_DIR]
    if TEXTURES_DIR != DEFAULT_TEXTURES_DIR:
        roots.append(DEFAULT_TEXTURES_DIR)
    tex_dir = next((root / texture_key for root in roots if (root / texture_key / "albedo.jpg").exists()), None)
    if tex_dir is None:
        return None
    albedo = tex_dir / "albedo.jpg"
    found = {"albedo": albedo}
    for slot, filename in (("normal", "normal.png"), ("roughness", "roughness.jpg")):
        path = tex_dir / filename
        if path.exists():
            found[slot] = path
    return found


def _shared_texture(filename: str) -> Path | None:
    roots = [TEXTURES_DIR, DEFAULT_TEXTURES_DIR]
    for root in roots:
        if root is None:
            continue
        candidate = root / "_shared" / filename
        if candidate.exists():
            return candidate
    return None


def _load_image(path: Path, colorspace: str) -> bpy.types.Image:
    image = bpy.data.images.load(str(path), check_existing=True)
    image.colorspace_settings.name = colorspace
    return image


def make_material(name: str, spec: dict) -> bpy.types.Material:
    """Principled material from a grammar spec. When the spec carries a
    texture_key with generated files, wire albedo/normal/roughness image nodes
    (UV layer "UVMap", box-projected at UV_TILE_METRES); else flat colour."""
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    # Rebuild from scratch: materials persist across module builds in one run,
    # so leftover texture nodes from a previous grammar must not survive.
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (420, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (60, 0)
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    color = hex_rgba(spec.get("base_color", "#808080"))
    if name == "MAT_Glass":
        color = tuple(min(1.0, channel * 1.25 + 0.02) for channel in color[:3]) + (1.0,)
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = float(spec.get("metallic", 0.0))
    bsdf.inputs["Roughness"].default_value = float(spec.get("roughness", 0.6))
    emission_color = spec.get("emission_color")
    if emission_color:
        emission_input = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
        if emission_input:
            emission_input.default_value = hex_rgba(emission_color)
        emission_strength = bsdf.inputs.get("Emission Strength")
        if emission_strength:
            emission_strength.default_value = float(spec.get("emission_strength", 0.0))
    if name == "MAT_Glass":
        # Keep glazing opaque enough for map-scale readability while giving it
        # a coated, reflective architectural-glass response in presentation renders.
        if "Coat Weight" in bsdf.inputs:
            bsdf.inputs["Coat Weight"].default_value = 0.45
        if "Coat Roughness" in bsdf.inputs:
            bsdf.inputs["Coat Roughness"].default_value = 0.08
        if "IOR" in bsdf.inputs:
            bsdf.inputs["IOR"].default_value = 1.48
        # Coated low-iron glazing is a dielectric, not a blue metal. Alpha
        # blending keeps the room atlas legible in EEVEE and glTF/Three.js;
        # clearcoat preserves a restrained reflection layer.
        bsdf.inputs["Metallic"].default_value = 0.0
        bsdf.inputs["Roughness"].default_value = 0.13
        alpha = bsdf.inputs.get("Alpha")
        if alpha:
            alpha.default_value = 0.56
        transmission = bsdf.inputs.get("Transmission Weight") or bsdf.inputs.get("Transmission")
        if transmission:
            transmission.default_value = 0.0
        try:
            mat.surface_render_method = "BLENDED"
        except (AttributeError, TypeError):
            mat.blend_method = "BLEND"
        try:
            mat.use_transparency_overlap = False
        except AttributeError:
            pass
        color = color[:3] + (0.56,)
    mat.diffuse_color = color  # viewport/solid fallback

    if "texture_key" in mat:
        del mat["texture_key"]  # material datablocks persist across builds
    textures = _texture_set(spec.get("texture_key"))
    if textures:
        uv_node = nodes.new("ShaderNodeUVMap")
        uv_node.uv_map = "UVMap"
        uv_node.location = (-760, 0)

        albedo_node = nodes.new("ShaderNodeTexImage")
        albedo_node.name = albedo_node.label = "TEX_Albedo"
        albedo_node.image = _load_image(textures["albedo"], "sRGB")
        albedo_node.location = (-480, 260)
        links.new(uv_node.outputs["UV"], albedo_node.inputs["Vector"])
        grade_node = nodes.new("ShaderNodeHueSaturation")
        grade_node.name = grade_node.label = "TEX_ArchitecturalGrade"
        texture_key = spec.get("texture_key")
        archviz_timber = bool(TEXTURES_DIR and TEXTURES_DIR.name == "textures_archviz_v5" and texture_key == "clt")
        archviz_sedum = bool(TEXTURES_DIR and TEXTURES_DIR.name == "textures_archviz_v5" and texture_key == "sedum_roof")
        grade_node.inputs["Saturation"].default_value = (
            0.9 if archviz_timber else (0.88 if archviz_sedum else (1.04 if texture_key == "red_brick" else 1.08))
        )
        grade_node.inputs["Value"].default_value = {
            "red_brick": 0.64,
            "clt": 0.82 if archviz_timber else 0.8,
            "sedum_roof": 0.94 if archviz_sedum else 0.84,
            "white_plaster": 0.98,
            "limestone": 0.94,
        }.get(texture_key, 0.84)
        grade_node.location = (-190, 260)
        links.new(albedo_node.outputs["Color"], grade_node.inputs["Color"])
        # The texture supplies real surface variation; the catalogue colour
        # still needs to steer its architectural palette (notably honey-toned
        # CLT versus pale raw pine). A partial multiply preserves photography
        # while carrying the archetype-specific tint into renders and GLB.
        tint_node = nodes.new("ShaderNodeMixRGB")
        tint_node.name = tint_node.label = "TEX_CatalogueTint"
        tint_node.blend_type = "MULTIPLY"
        tint_node.inputs[0].default_value = {
            "clt": 0.15 if archviz_timber else 0.46,
            "sedum_roof": 0.04 if archviz_sedum else 0.14,
            "red_brick": 0.18,
            "white_plaster": 0.08,
            "limestone": 0.12,
        }.get(texture_key, 0.14)
        tint_node.inputs[2].default_value = color
        tint_node.location = (20, 260)
        links.new(grade_node.outputs["Color"], tint_node.inputs[1])
        links.new(tint_node.outputs["Color"], bsdf.inputs["Base Color"])

        if "roughness" in textures:
            rough_node = nodes.new("ShaderNodeTexImage")
            rough_node.name = rough_node.label = "TEX_Roughness"
            rough_node.image = _load_image(textures["roughness"], "Non-Color")
            rough_node.location = (-480, -40)
            links.new(uv_node.outputs["UV"], rough_node.inputs["Vector"])
            links.new(rough_node.outputs["Color"], bsdf.inputs["Roughness"])

        if "normal" in textures:
            normal_tex = nodes.new("ShaderNodeTexImage")
            normal_tex.name = normal_tex.label = "TEX_Normal"
            normal_tex.image = _load_image(textures["normal"], "Non-Color")
            normal_tex.location = (-480, -340)
            links.new(uv_node.outputs["UV"], normal_tex.inputs["Vector"])
            normal_map = nodes.new("ShaderNodeNormalMap")
            normal_map.uv_map = "UVMap"
            normal_map.inputs["Strength"].default_value = 0.45
            normal_map.location = (-180, -340)
            links.new(normal_tex.outputs["Color"], normal_map.inputs["Color"])
            links.new(normal_map.outputs["Normal"], bsdf.inputs["Normal"])

        mat["texture_key"] = spec.get("texture_key")
    return mat


def make_interior_atlas_material(index: int) -> bpy.types.Material:
    """One atlas-backed room material. Eight material slots share one image;
    per-face UVs select the cell, avoiding eight duplicate image payloads."""
    atlas_path = _shared_texture(INTERIOR_ATLAS_FILENAME)
    if atlas_path is None:
        return make_material(
            f"MAT_Interior_Room_{index:02d}",
            {"base_color": "#221b17", "roughness": 0.82, "metallic": 0.0,
             "emission_color": "#8f5b32", "emission_strength": 0.08},
        )

    mat = bpy.data.materials.get(f"MAT_Interior_Room_{index:02d}") or bpy.data.materials.new(
        f"MAT_Interior_Room_{index:02d}"
    )
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (360, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (80, 0)
    bsdf.inputs["Roughness"].default_value = 0.78
    emission_strength = bsdf.inputs.get("Emission Strength")
    if emission_strength:
        emission_strength.default_value = 0.32 if index != 7 else 0.08
    uv_node = nodes.new("ShaderNodeUVMap")
    uv_node.uv_map = "UVMap"
    uv_node.location = (-560, 0)
    image_node = nodes.new("ShaderNodeTexImage")
    image_node.name = image_node.label = "TEX_InteriorAtlas"
    image_node.image = _load_image(atlas_path, "sRGB")
    image_node.interpolation = "Linear"
    image_node.extension = "CLIP"
    image_node.location = (-300, 0)
    links.new(uv_node.outputs["UV"], image_node.inputs["Vector"])
    links.new(image_node.outputs["Color"], bsdf.inputs["Base Color"])
    emission = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
    if emission:
        links.new(image_node.outputs["Color"], emission)
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    mat.diffuse_color = (0.18, 0.11, 0.07, 1.0)
    mat["interior_atlas_cell"] = index
    mat["interior_atlas_columns"] = INTERIOR_ATLAS_COLUMNS
    mat["interior_atlas_rows"] = INTERIOR_ATLAS_ROWS
    return mat


def build_materials(grammar: dict) -> dict[str, bpy.types.Material]:
    materials = grammar["materials"]
    result = {
        "primary": make_material("MAT_Facade_Primary", materials["primary"]),
        "secondary": make_material("MAT_Facade_Secondary", materials["secondary"]),
        "accent": make_material("MAT_Accent", materials["accent"]),
        "glass": make_material("MAT_Glass", materials["glass"]),
        "concrete": make_material("MAT_Concrete", materials["concrete"]),
        "roof": make_material("MAT_Roof", materials["roof"]),
        "green_roof": make_material("MAT_GreenRoof", materials["green_roof"]),
        "plant": make_material("MAT_Plants", {"base_color": "#416f38", "roughness": 0.86, "metallic": 0.0}),
        "plant_alt": make_material("MAT_Plants_Alt", {"base_color": "#6b7b45", "roughness": 0.88, "metallic": 0.0}),
        "interior": make_material("MAT_Interior_Shadow", {"base_color": "#171c21", "roughness": 0.72, "metallic": 0.0}),
        "interior_warm": make_material("MAT_Interior_Warm", {
            "base_color": "#6e4e2e", "roughness": 0.82, "metallic": 0.0,
            "emission_color": "#b77c3f", "emission_strength": 0.08,
        }),
    }
    result["interior_cells"] = [make_interior_atlas_material(index) for index in range(8)]
    return result


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def add_box(name: str, size: tuple[float, float, float], location: tuple[float, float, float], mat) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    return obj


def add_cylinder(
    name: str,
    radius: float,
    depth: float,
    location: tuple[float, float, float],
    mat,
    vertices: int = 12,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj


def add_foliage(
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    mat,
    subdivisions: int = 2,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj


def add_planter_vegetation(
    parts: list,
    prefix: str,
    centre: tuple[float, float, float],
    width: float,
    mats: dict,
) -> None:
    """Small stems and leaf clusters replace the old row of green spheres.
    The asymmetric silhouettes remain inexpensive but read as planting at the
    aerial distances for which the builder is designed."""
    cx, cy, cz = centre
    count = max(3, min(7, round(width / 0.42)))
    for index in range(count):
        t = (index + 0.5) / count - 0.5
        x = cx + t * width * 0.82
        height = 0.28 + 0.09 * ((index * 3) % 4)
        stem = add_cylinder(
            f"{prefix}_Stem{index:02d}", 0.014, height,
            (x, cy + 0.018 * ((index % 3) - 1), cz + height / 2), mats["plant_alt"], 7,
        )
        stem.rotation_euler.x = math.radians(-7 + 5 * (index % 3))
        parts.append(stem)
        for leaf_index, dz in enumerate((0.45, 0.72, 0.96)):
            direction = -1 if (index + leaf_index) % 2 else 1
            leaf = add_foliage(
                f"{prefix}_Leaf{index:02d}_{leaf_index}",
                (x + direction * (0.055 + leaf_index * 0.012), cy - 0.025 * leaf_index, cz + height * dz),
                (0.11 + 0.015 * leaf_index, 0.045, 0.065 + 0.012 * leaf_index),
                mats["plant"] if (index + leaf_index) % 3 else mats["plant_alt"],
                subdivisions=1,
            )
            leaf.rotation_euler.y = math.radians(direction * (18 + leaf_index * 7))
            parts.append(leaf)


def add_prism(name: str, verts: list[tuple[float, float, float]], faces: list[tuple[int, ...]], mat) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def add_arch_ring(
    name: str,
    centre_x: float,
    front_y: float,
    spring_z: float,
    inner_radius: float,
    ring_width: float,
    depth: float,
    mat,
    segments: int = 18,
) -> bpy.types.Object:
    """Extruded semicircular masonry ring; unlike the v2 stepped lintel this
    preserves a genuine curved void through the entrance surround."""
    outer_radius = inner_radius + ring_width
    y_front, y_back = front_y - depth / 2, front_y + depth / 2
    verts: list[tuple[float, float, float]] = []
    for y in (y_front, y_back):
        for radius in (inner_radius, outer_radius):
            for index in range(segments + 1):
                theta = math.pi * index / segments
                verts.append((centre_x + radius * math.cos(theta), y, spring_z + radius * math.sin(theta)))

    stride = segments + 1
    inner_front, outer_front = 0, stride
    inner_back, outer_back = stride * 2, stride * 3
    faces: list[tuple[int, ...]] = []
    for index in range(segments):
        nxt = index + 1
        faces.extend([
            (outer_front + index, outer_front + nxt, inner_front + nxt, inner_front + index),
            (inner_back + index, inner_back + nxt, outer_back + nxt, outer_back + index),
            (outer_front + index, outer_back + index, outer_back + nxt, outer_front + nxt),
            (inner_front + index, inner_front + nxt, inner_back + nxt, inner_back + index),
        ])
    faces.extend([
        (inner_front, inner_back, outer_back, outer_front),
        (inner_front + segments, outer_front + segments, outer_back + segments, inner_back + segments),
    ])
    return add_prism(name, verts, faces, mat)


def add_frame_bars(
    parts: list,
    prefix: str,
    axis: str,
    centre: tuple[float, float, float],
    opening_w: float,
    opening_h: float,
    depth: float,
    mat,
    profile: float = 0.075,
    mullions: str = "single",
) -> None:
    """Build four thin jamb/head/sill members instead of a solid facade plate.

    This is the visual hinge of v3: glass is no longer hidden behind a filled
    'frame' cube, and the dark reveal remains visible around the real opening.
    """
    x, y, z = centre
    if axis in ("front", "rear"):
        parts.extend([
            add_box(f"{prefix}_JambL", (profile, depth, opening_h + profile * 2), (x - opening_w / 2 - profile / 2, y, z), mat),
            add_box(f"{prefix}_JambR", (profile, depth, opening_h + profile * 2), (x + opening_w / 2 + profile / 2, y, z), mat),
            add_box(f"{prefix}_Head", (opening_w, depth, profile), (x, y, z + opening_h / 2 + profile / 2), mat),
            add_box(f"{prefix}_Sill", (opening_w, depth, profile), (x, y, z - opening_h / 2 - profile / 2), mat),
        ])
        if mullions in ("single", "double"):
            offsets = (0.0,) if mullions == "single" else (-opening_w * 0.18, opening_w * 0.18)
            for index, offset in enumerate(offsets):
                parts.append(add_box(f"{prefix}_Mullion{index}", (profile * 0.62, depth * 1.05, opening_h), (x + offset, y, z), mat))
    else:
        parts.extend([
            add_box(f"{prefix}_JambL", (depth, profile, opening_h + profile * 2), (x, y - opening_w / 2 - profile / 2, z), mat),
            add_box(f"{prefix}_JambR", (depth, profile, opening_h + profile * 2), (x, y + opening_w / 2 + profile / 2, z), mat),
            add_box(f"{prefix}_Head", (depth, opening_w, profile), (x, y, z + opening_h / 2 + profile / 2), mat),
            add_box(f"{prefix}_Sill", (depth, opening_w, profile), (x, y, z - opening_h / 2 - profile / 2), mat),
        ])
        if mullions in ("single", "double"):
            offsets = (0.0,) if mullions == "single" else (-opening_w * 0.18, opening_w * 0.18)
            for index, offset in enumerate(offsets):
                parts.append(add_box(f"{prefix}_Mullion{index}", (depth * 1.05, profile * 0.62, opening_h), (x, y + offset, z), mat))


def join_as(name: str, objects: list[bpy.types.Object]) -> bpy.types.Object:
    """Join module parts into a single mesh so the GLB gets one node per module."""
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    if len(objects) > 1:
        bpy.ops.object.join()
    joined = bpy.context.view_layer.objects.active
    joined.name = name
    joined.data.name = name
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    # Small real-world edge radii create highlight lines and eliminate the
    # unmistakable razor-edged procedural-box look.
    bevel = joined.modifiers.new(name="ArchitecturalEdge", type="BEVEL")
    bevel.width = 0.025
    bevel.segments = 1
    bevel.limit_method = "ANGLE"
    try:
        bevel.harden_normals = True
    except AttributeError:
        pass
    bpy.context.view_layer.objects.active = joined
    try:
        bpy.ops.object.modifier_apply(modifier=bevel.name)
    except RuntimeError:
        joined.modifiers.remove(bevel)
    apply_box_uv(joined)
    return joined


def apply_box_uv(obj: bpy.types.Object, tile: float = UV_TILE_METRES) -> None:
    """Deterministic box projection on UV layer "UVMap" (TEXCOORD_0): each face
    maps by its dominant normal axis at real-world density (1 tile = ``tile`` m).
    Runs after join_as, when transforms are applied, so coordinates are metric."""
    mesh = obj.data
    uv_layer = mesh.uv_layers.get("UVMap") or mesh.uv_layers.new(name="UVMap")
    mesh.uv_layers.active = uv_layer
    for poly in mesh.polygons:
        n = poly.normal
        ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
        material = mesh.materials[poly.material_index] if poly.material_index < len(mesh.materials) else None
        atlas_cell = material.get("interior_atlas_cell") if material else None
        projected: list[tuple[float, float]] = []
        for loop_index in poly.loop_indices:
            co = mesh.vertices[mesh.loops[loop_index].vertex_index].co
            if az >= ax and az >= ay:
                u, v = co.x, co.y
            elif ax >= ay:
                u, v = co.y, co.z
            else:
                u, v = co.x, co.z
            projected.append((u, v))

        if atlas_cell is not None:
            # Normalize each original box face, then select its atlas cell with
            # a small gutter that excludes GPT Image's black separator lines.
            columns = int(material.get("interior_atlas_columns", INTERIOR_ATLAS_COLUMNS))
            rows = int(material.get("interior_atlas_rows", INTERIOR_ATLAS_ROWS))
            col, row = int(atlas_cell) % columns, int(atlas_cell) // columns
            min_u, max_u = min(v[0] for v in projected), max(v[0] for v in projected)
            min_v, max_v = min(v[1] for v in projected), max(v[1] for v in projected)
            span_u, span_v = max(max_u - min_u, 1e-6), max(max_v - min_v, 1e-6)
            gutter_u, gutter_v = 0.006, 0.011
            cell_u0 = col / columns + gutter_u
            cell_u1 = (col + 1) / columns - gutter_u
            # Image rows are top-down; Blender UV V=0 starts at the bottom.
            cell_v0 = (rows - row - 1) / rows + gutter_v
            cell_v1 = (rows - row) / rows - gutter_v
            for loop_index, (u, v) in zip(poly.loop_indices, projected):
                nu, nv = (u - min_u) / span_u, (v - min_v) / span_v
                uv_layer.data[loop_index].uv = (
                    cell_u0 + nu * (cell_u1 - cell_u0),
                    cell_v0 + nv * (cell_v1 - cell_v0),
                )
        else:
            for loop_index, (u, v) in zip(poly.loop_indices, projected):
                uv_layer.data[loop_index].uv = (u / tile, v / tile)


def _gltf_output_group() -> bpy.types.NodeTree:
    """The glTF exporter reads occlusion from a node group named
    "glTF Material Output" with an input socket called "Occlusion"."""
    tree = bpy.data.node_groups.get("glTF Material Output")
    if tree is None:
        tree = bpy.data.node_groups.new("glTF Material Output", "ShaderNodeTree")
        tree.interface.new_socket("Occlusion", in_out="INPUT", socket_type="NodeSocketFloat")
    return tree


def bake_ao(obj: bpy.types.Object, resolution: int = 512, samples: int = 16) -> bool:
    """Bake ambient occlusion for one joined module into a per-module map on a
    second, non-overlapping UV layer (TEXCOORD_1) and wire it to the glTF
    occlusion output so viewers apply it independently of the tiled albedo."""
    mesh = obj.data
    if not mesh.materials:
        return False

    # Non-overlapping unwrap on a dedicated layer; box UVs overlap by design.
    ao_layer = mesh.uv_layers.get("AOMap") or mesh.uv_layers.new(name="AOMap")
    mesh.uv_layers.active = ao_layer
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.02, correct_aspect=True)
    bpy.ops.object.mode_set(mode="OBJECT")

    image = bpy.data.images.new(f"AO_{obj.name}", resolution, resolution, alpha=False)
    image.colorspace_settings.name = "Non-Color"

    # Blender 5.1 can fail silently when one joined mesh has many materials:
    # even with an active target node in every tree it may report that no
    # target exists and leave a packed, solid-black AO texture. AO is geometry-
    # only, so bake through one temporary material and restore the authored
    # slots before wiring the result into glTF.
    original_materials = list(mesh.materials)
    original_indices = [poly.material_index for poly in mesh.polygons]
    target_mat = bpy.data.materials.new(f"AO_TARGET_{obj.name}")
    target_mat.use_nodes = True
    target_nodes = target_mat.node_tree.nodes
    target_nodes.clear()
    target_output = target_nodes.new("ShaderNodeOutputMaterial")
    target_bsdf = target_nodes.new("ShaderNodeBsdfPrincipled")
    target_mat.node_tree.links.new(target_bsdf.outputs["BSDF"], target_output.inputs["Surface"])
    target_tex = target_nodes.new("ShaderNodeTexImage")
    target_tex.name = "AO_BAKE_TARGET"
    target_tex.image = image
    for node in target_nodes:
        node.select = node is target_tex
    target_nodes.active = target_tex
    mesh.materials.clear()
    mesh.materials.append(target_mat)
    for poly in mesh.polygons:
        poly.material_index = 0
    obj.active_material_index = 0
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.context.view_layer.update()
    mesh.uv_layers.active_index = mesh.uv_layers.find("AOMap")
    ao_layer.active_render = True
    for node in target_nodes:
        node.select = False
    target_nodes.active = target_tex
    target_tex.select = True
    def restore_materials() -> None:
        mesh.materials.clear()
        for material in original_materials:
            mesh.materials.append(material)
        for poly, material_index in zip(mesh.polygons, original_indices):
            poly.material_index = material_index

    def wire_occlusion() -> None:
        for mat in original_materials:
            nodes, links = mat.node_tree.nodes, mat.node_tree.links
            for stale in [n for n in nodes if n.name.startswith("AO_BAKE")]:
                nodes.remove(stale)
            uv_node = nodes.new("ShaderNodeUVMap")
            uv_node.name = "AO_BAKE_UV"
            uv_node.uv_map = "AOMap"
            uv_node.location = (-760, -640)
            tex_node = nodes.new("ShaderNodeTexImage")
            tex_node.name = "AO_BAKE_TEX"
            tex_node.image = image
            tex_node.location = (-480, -640)
            links.new(uv_node.outputs["UV"], tex_node.inputs["Vector"])
            group = nodes.new("ShaderNodeGroup")
            group.name = "AO_BAKE_OUT"
            group.node_tree = _gltf_output_group()
            group.location = (-180, -640)
            links.new(tex_node.outputs["Color"], group.inputs["Occlusion"])

    scene = bpy.context.scene
    previous_engine = scene.render.engine
    try:
        scene.render.engine = "CYCLES"
        scene.cycles.samples = samples
        scene.cycles.device = "CPU"
        scene.render.bake.target = "IMAGE_TEXTURES"
        try:  # AO ray distance: architectural scale, not world-sized
            scene.world.light_settings.distance = 10.0
        except AttributeError:
            pass
        bpy.ops.object.bake(type="AO", margin=8, use_clear=True, uv_layer="AOMap")
        # Sample every 257th red channel. A real AO bake must contain both lit
        # and occluded values; flat black is a failed target, not valid AO.
        pixels = image.pixels[:]
        red_samples = pixels[0::4 * 257]
        if not red_samples or max(red_samples) - min(red_samples) < 0.015:
            raise RuntimeError("AO bake produced a flat image")
        restore_materials()
        wire_occlusion()
        image.pack()
        return True
    except Exception as exc:  # pragma: no cover - depends on Cycles availability
        print(f"[blender_generate] WARNING: AO bake failed for {obj.name}: {exc}")
        restore_materials()
        for mat in original_materials:
            nodes = mat.node_tree.nodes
            for stale in [n for n in nodes if n.name.startswith("AO_BAKE")]:
                nodes.remove(stale)
        return False
    finally:
        if list(mesh.materials) == [target_mat]:
            restore_materials()
        if target_mat.users == 0:
            bpy.data.materials.remove(target_mat)
        scene.render.engine = previous_engine


def _bays(length: float, bay_width: float) -> tuple[int, float]:
    count = max(1, int(round(length / bay_width)))
    return count, length / count


def add_window_row(
    parts: list,
    prefix: str,
    wall_length: float,
    axis: str,  # 'front' (-Y), 'rear' (+Y), 'left' (-X), 'right' (+X)
    wall_offset: float,  # distance from origin to the wall plane
    z0: float,
    window_w: float,
    window_h: float,
    sill: float,
    bay_count: int,
    mats: dict,
    frame_depth: float = 0.07,
    interior_seed: int = 0,
) -> None:
    """A row of glazing units with a shadow reveal, projecting surround and mullion."""
    bay = wall_length / bay_count
    window_w = min(window_w, bay * 0.78)
    for i in range(bay_count):
        along = -wall_length / 2 + bay * (i + 0.5)
        z_center = z0 + sill + window_h / 2
        if axis in ("front", "rear"):
            sign = -1.0 if axis == "front" else 1.0
            reveal_loc = (along, sign * (wall_offset + 0.018), z_center)
            glass_loc = (along, sign * (wall_offset + 0.13), z_center)
            frame_loc = (along, sign * (wall_offset + 0.075), z_center)
            glass_size = (window_w, 0.06, window_h)
            reveal_size = (window_w + frame_depth * 3.6, 0.04, window_h + frame_depth * 3.6)
            frame_size = (window_w + frame_depth * 2, 0.08, window_h + frame_depth * 2)
            mullion_size = (0.045, 0.09, window_h)
            mullion_loc = (along, sign * (wall_offset + 0.155), z_center)
        else:
            sign = -1.0 if axis == "left" else 1.0
            reveal_loc = (sign * (wall_offset + 0.018), along, z_center)
            glass_loc = (sign * (wall_offset + 0.13), along, z_center)
            frame_loc = (sign * (wall_offset + 0.075), along, z_center)
            glass_size = (0.06, window_w, window_h)
            reveal_size = (0.04, window_w + frame_depth * 3.6, window_h + frame_depth * 3.6)
            frame_size = (0.08, window_w + frame_depth * 2, window_h + frame_depth * 2)
            mullion_size = (0.09, 0.045, window_h)
            mullion_loc = (sign * (wall_offset + 0.155), along, z_center)
        atlas_cells = mats.get("interior_cells") or []
        axis_seed = {"front": 0, "rear": 2, "left": 4, "right": 6}.get(axis, 0)
        reveal_mat = atlas_cells[(i * 3 + axis_seed + interior_seed) % len(atlas_cells)] if atlas_cells else mats["interior"]
        parts.append(add_box(f"{prefix}_Reveal_{axis}_{i:02d}", reveal_size, reveal_loc, reveal_mat))
        parts.append(add_box(f"{prefix}_Glass_{axis}_{i:02d}", glass_size, glass_loc, mats["glass"]))
        add_frame_bars(
            parts, f"{prefix}_Frame_{axis}_{i:02d}", axis, frame_loc,
            window_w, window_h, 0.1, mats["accent"],
            profile=max(0.055, frame_depth),
            mullions="single" if window_w > 1.25 else "none",
        )
        # Projecting sill/flashing turns an overlay window into a layered
        # facade element and remains legible on rear/side aerial elevations.
        sill_z = z_center - window_h / 2 - 0.025
        if axis in ("front", "rear"):
            cap_size = (window_w + 0.14, 0.16, 0.055)
            cap_loc = (along, sign * (wall_offset + 0.17), sill_z)
        else:
            cap_size = (0.16, window_w + 0.14, 0.055)
            cap_loc = (sign * (wall_offset + 0.17), along, sill_z)
        parts.append(add_box(f"{prefix}_SillCap_{axis}_{i:02d}", cap_size, cap_loc, mats["accent"]))


def add_entry_expression(parts: list, entrance_type: str, w: float, d: float, h: float, mats: dict) -> None:
    """Add an archetype-specific, legible address at the centre front facade."""
    front = d / 2
    door_w, door_h = min(2.3, w * 0.14), min(3.2, h * 0.74)
    y = -(front + 0.18)
    if entrance_type == "portal":
        portal_w = door_w + 1.2
        parts.append(add_box("EntryPortalL", (0.42, 0.5, door_h + 0.65), (-portal_w / 2, y, (door_h + 0.65) / 2), mats["primary"]))
        parts.append(add_box("EntryPortalR", (0.42, 0.5, door_h + 0.65), (portal_w / 2, y, (door_h + 0.65) / 2), mats["primary"]))
        parts.append(add_box("EntryPortalTop", (portal_w + 0.42, 0.5, 0.42), (0, y, door_h + 0.44), mats["primary"]))
    elif entrance_type == "recessed":
        parts.append(add_box("EntryShadow", (door_w + 1.1, 0.18, door_h + 0.65), (0, -(front + 0.04), (door_h + 0.65) / 2), mats["accent"]))
        parts.append(add_box("EntryThinCanopy", (door_w + 1.8, 1.05, 0.1), (0, -(front + 0.52), door_h + 0.45), mats["accent"]))
    elif entrance_type == "arched":
        portal_w = door_w + 1.0
        inner_radius = portal_w / 2
        pier_width = 0.42
        spring_z = min(door_h * 0.68, h - inner_radius - 0.35)
        parts.append(add_box("EntryArchPierL", (pier_width, 0.4, spring_z), (-(inner_radius + pier_width / 2), y, spring_z / 2), mats["secondary"]))
        parts.append(add_box("EntryArchPierR", (pier_width, 0.4, spring_z), ((inner_radius + pier_width / 2), y, spring_z / 2), mats["secondary"]))
        parts.append(add_arch_ring("EntryTrueArch", 0.0, y, spring_z, inner_radius, pier_width, 0.4, mats["secondary"]))
        # Dark, recessed lobby makes the void legible through the arch.
        parts.append(add_box("EntryArchShadow", (portal_w * 0.86, 0.08, spring_z + inner_radius * 0.7),
                             (0, y + 0.24, (spring_z + inner_radius * 0.7) / 2), mats["interior"]))
    elif entrance_type == "colonnade":
        for i, x in enumerate((-3.0, -1.55, 1.55, 3.0)):
            if abs(x) < w * 0.42:
                parts.append(add_cylinder(f"EntryColumn{i}", 0.22, door_h + 0.55, (x, y, (door_h + 0.55) / 2), mats["concrete"], 16))
        parts.append(add_box("EntryEntablature", (min(7.2, w * 0.5), 0.5, 0.42), (0, y, door_h + 0.45), mats["primary"]))


# ---------------------------------------------------------------------------
# Module builders — each returns ONE joined object with base at z=0
# ---------------------------------------------------------------------------

def build_podium(grammar: dict, mats: dict) -> bpy.types.Object:
    dims, facade, massing = grammar["dimensions"], grammar["facade"], grammar["massing"]
    w, d, h = dims["width_m"], dims["depth_m"], dims["podium_height_m"]
    retail = bool(massing.get("has_podium_retail"))
    parts: list = []

    parts.append(add_box("Podium_Shell", (w, d, h), (0, 0, h / 2), mats["primary"]))
    # Stone/concrete plinth grounds the building visually
    plinth_h = 0.45
    parts.append(add_box("Podium_Plinth", (w + 0.1, d + 0.1, plinth_h), (0, 0, plinth_h / 2), mats["concrete"]))

    bay_count, bay = _bays(w, facade["bay_width_m"])
    front_y = d / 2

    if retail:
        # Storefront: tall glazing between accent mullions, centred double door, canopy
        sf_h = h * facade["storefront_height_ratio"] - plinth_h
        sf_z0 = plinth_h
        for i in range(bay_count):
            x = -w / 2 + bay * (i + 0.5)
            parts.append(add_box(
                f"Podium_Storefront_{i:02d}", (bay * 0.82, 0.08, sf_h),
                (x, -(front_y + 0.03), sf_z0 + sf_h / 2), mats["glass"],
            ))
            parts.append(add_box(
                f"Podium_Mullion_{i:02d}", (0.14, 0.12, sf_h),
                (-w / 2 + bay * i + bay, -(front_y + 0.02), sf_z0 + sf_h / 2), mats["accent"],
            )) if i < bay_count - 1 else None
        parts = [p for p in parts if p is not None]
        # Transom band above the storefront
        parts.append(add_box("Podium_Transom", (w * 0.98, 0.1, 0.3),
                             (0, -(front_y + 0.02), sf_z0 + sf_h + 0.15), mats["accent"]))
        # Entry door (double, centred)
        parts.append(add_box("Podium_Door", (2.0, 0.12, 2.3), (0, -(front_y + 0.05), plinth_h + 1.15), mats["accent"]))
        # Canopy over the retail frontage
        parts.append(add_box("Podium_Canopy", (w * 0.86, 1.35, 0.12),
                             (0, -(front_y + 0.68), h * facade["storefront_height_ratio"] + 0.35), mats["accent"]))
    else:
        # Residential/lobby podium: generous glazing, centred entrance + porch canopy
        window_h = (h - plinth_h) * 0.62
        add_window_row(parts, "Podium", w, "front", front_y, plinth_h, bay * 0.6, window_h, 0.35, bay_count, mats)
        parts.append(add_box("Podium_Door", (1.9, 0.12, 2.25), (0, -(front_y + 0.06), plinth_h + 1.125), mats["accent"]))
        parts.append(add_box("Podium_EntryCanopy", (3.2, 1.2, 0.12), (0, -(front_y + 0.6), plinth_h + 2.5), mats["accent"]))

    # Rear: smaller secondary windows; sides: modest bays
    side_count, _ = _bays(d, facade["bay_width_m"])
    rear_h = (h - plinth_h) * 0.4
    add_window_row(parts, "Podium", w, "rear", d / 2, plinth_h + 0.4, bay * 0.5, rear_h, 0.5, bay_count, mats)
    add_window_row(parts, "Podium", d, "left", w / 2, plinth_h + 0.4, bay * 0.5, rear_h, 0.5, side_count, mats)
    add_window_row(parts, "Podium", d, "right", w / 2, plinth_h + 0.4, bay * 0.5, rear_h, 0.5, side_count, mats)

    add_entry_expression(parts, facade.get("entrance_type", "canopy"), w, d, h, mats)
    # Layered double-door glazing, transom and hardware keep the address
    # readable after the broad entry-expression geometry is added.
    door_y = -(front_y + 0.24)
    door_z = plinth_h + 1.12
    parts.append(add_box("Podium_DoorGlassL", (0.78, 0.045, 2.05), (-0.43, door_y, door_z), mats["glass"]))
    parts.append(add_box("Podium_DoorGlassR", (0.78, 0.045, 2.05), (0.43, door_y, door_z), mats["glass"]))
    parts.append(add_box("Podium_DoorTransom", (1.72, 0.05, 0.42), (0, door_y, door_z + 1.27), mats["glass"]))
    for handle_index, x in enumerate((-0.16, 0.16)):
        parts.append(add_cylinder(f"Podium_DoorHandle{handle_index}", 0.025, 0.62,
                                  (x, door_y - 0.055, door_z), mats["accent"], 10))
    if facade.get("system") in ("timber_grid", "brick_bays", "stone_frame"):
        band_mat = mats["primary"] if facade["system"] != "stone_frame" else mats["secondary"]
        parts.append(add_box("Podium_CrownBand", (w + 0.16, 0.22, 0.34), (0, -(d / 2 + 0.08), h - 0.2), band_mat))

    return join_as("MOD_Podium", parts)


def build_floor(grammar: dict, mats: dict, setback: bool = False) -> bpy.types.Object:
    dims, facade, massing = grammar["dimensions"], grammar["facade"], grammar["massing"]
    h = dims["setback_height_m"] if setback else dims["floor_height_m"]
    full_w, full_d = dims["width_m"], dims["depth_m"]

    if setback:
        inset_front = massing["setback_front_m"]
        inset_side = massing["setback_side_m"]
        w = full_w - inset_side * 2
        # Setback recedes from the FRONT only (street side); rear wall stays put
        d = full_d - inset_front
        center_y = inset_front / 2
    else:
        w, d, center_y = full_w, full_d, 0.0

    parts: list = []
    shell_mat = mats["secondary"] if setback else mats["primary"]
    parts.append(add_box("Floor_Shell", (w, d, h), (0, center_y, h / 2), shell_mat))
    # Expressed slab edge at the base of every floor
    parts.append(add_box("Floor_SlabEdge", (w + 0.08, d + 0.08, 0.2), (0, center_y, 0.1), mats["concrete"]))

    bay_count, bay = _bays(w, facade["bay_width_m"])
    side_count, _ = _bays(d, facade["bay_width_m"])
    window_h = h * facade["window_height_ratio"]
    window_w = min(bay * facade["window_width_ratio"], bay - 0.7)  # keep visible wall piers between bays
    sill = min(facade["sill_height_m"], h - window_h - 0.3)
    front_wall_y = -(center_y - d / 2)  # distance from origin to front wall plane (positive)

    balcony_mode = facade.get("balcony_mode", "none")
    balcony_every = max(1, int(facade.get("balcony_frequency", 2)))
    balcony_depth = facade.get("balcony_depth_m", 1.5)
    system = facade.get("system", "regular")
    feature_every = max(1, int(facade.get("feature_bay_frequency", 3)))
    material_every = max(1, int(facade.get("material_bay_frequency", 3)))
    planter_every = int(facade.get("planter_frequency", 0))
    projection = float(facade.get("panel_projection_m", 0.08))
    guard = facade.get("balcony_guard", "metal")

    for i in range(bay_count):
        x = -w / 2 + bay * (i + 0.5)
        has_balcony = (not setback) and balcony_mode == "projecting" and (i % balcony_every == 0)
        is_feature = i % feature_every == 0
        z_center = sill + window_h / 2
        # Window (door-height glazing behind balconies)
        glass_h = h * 0.72 if has_balcony else window_h
        glass_z = 0.25 + glass_h / 2 if has_balcony else z_center
        feature_projection = projection if is_feature and system in ("brick_bays", "stone_frame") else 0.0
        if feature_projection:
            feature_mat = mats["primary"] if system == "brick_bays" else mats["secondary"]
            parts.append(add_box(
                f"Floor_FeatureBay_{i:02d}", (bay * 0.9, feature_projection + 0.12, h - 0.18),
                (x, -(front_wall_y + feature_projection / 2), h / 2), feature_mat,
            ))
        elif system in ("punched_render", "stone_frame") and i % material_every == material_every - 1:
            parts.append(add_box(
                f"Floor_MaterialBay_{i:02d}", (bay * 0.9, 0.1, h - 0.2),
                (x, -(front_wall_y + 0.04), h / 2), mats["secondary"],
            ))

        glass_y = -(front_wall_y + feature_projection + 0.15)
        frame_y = -(front_wall_y + feature_projection + 0.085)
        parts.append(add_box(f"Floor_Reveal_{i:02d}", (window_w + 0.38, 0.08, glass_h + 0.38),
                             (x, -(front_wall_y + feature_projection + 0.025), glass_z), mats["accent"]))
        parts.append(add_box(f"Floor_Frame_{i:02d}", (window_w + 0.18, 0.1, glass_h + 0.18),
                             (x, frame_y, glass_z), mats["accent"]))
        parts.append(add_box(f"Floor_Glass_{i:02d}", (window_w, 0.06, glass_h),
                             (x, glass_y, glass_z), mats["glass"]))
        if facade.get("mullions", True) and window_w > 1.15:
            parts.append(add_box(f"Floor_Mullion_{i:02d}", (0.05, 0.12, glass_h),
                                 (x, glass_y - 0.04, glass_z), mats["accent"]))
        if has_balcony:
            bw = bay * 0.85
            by = -(front_wall_y + balcony_depth / 2)
            parts.append(add_box(f"Floor_BalconySlab_{i:02d}", (bw, balcony_depth, 0.14), (x, by, 0.2), mats["concrete"]))
            rail_y = -(front_wall_y + balcony_depth - 0.03)
            if guard in ("solid", "planter"):
                guard_h = 0.44 if guard == "planter" else 1.02
                guard_mat = mats["primary"] if guard == "planter" else mats["secondary"]
                parts.append(add_box(f"Floor_Balustrade_{i:02d}", (bw, 0.12, guard_h),
                                     (x, rail_y, 0.27 + guard_h / 2), guard_mat))
                if guard == "planter":
                    parts.append(add_box(f"Floor_PlanterRail_{i:02d}", (bw + 0.06, 0.055, 0.52),
                                         (x, rail_y - 0.025, 0.98), mats["glass"]))
                    parts.append(add_box(f"Floor_PlanterTopRail_{i:02d}", (bw + 0.1, 0.07, 0.07),
                                         (x, rail_y - 0.04, 1.26), mats["accent"]))
            else:
                guard_mat = mats["glass"] if guard == "glass" else mats["accent"]
                parts.append(add_box(f"Floor_Balustrade_{i:02d}", (bw, 0.045, 0.88),
                                     (x, rail_y, 0.76), guard_mat))
                parts.append(add_box(f"Floor_Handrail_{i:02d}", (bw + 0.08, 0.08, 0.08),
                                     (x, rail_y, 1.23), mats["accent"]))
            parts.append(add_box(f"Floor_BalustradeL_{i:02d}", (0.06, balcony_depth - 0.06, 1.02),
                                 (x - bw / 2 + 0.03, by, 0.78), mats["accent"]))
            parts.append(add_box(f"Floor_BalustradeR_{i:02d}", (0.06, balcony_depth - 0.06, 1.02),
                                 (x + bw / 2 - 0.03, by, 0.78), mats["accent"]))
            if guard == "planter" or (planter_every and i % planter_every == 0):
                for plant_idx, dx in enumerate((-bw * 0.28, 0.0, bw * 0.28)):
                    parts.append(add_foliage(
                        f"Floor_Plant_{i:02d}_{plant_idx}",
                        (x + dx, rail_y - 0.02, 0.88 + 0.08 * (plant_idx % 2)),
                        (0.3, 0.22, 0.27 + 0.07 * (plant_idx % 2)), mats["plant"],
                    ))

    if system in ("timber_grid", "brick_bays"):
        band_mat = mats["primary"] if system == "timber_grid" else mats["secondary"]
        parts.append(add_box("Floor_FacadeDatum", (w + 0.12, 0.16, 0.18),
                             (0, -(front_wall_y + 0.07), h - 0.12), band_mat))

    # Rear + side windows
    add_window_row(parts, "Floor", w, "rear", (center_y + d / 2), 0.0, window_w, window_h, sill, bay_count, mats)
    add_window_row(parts, "Floor", d * 0.9, "left", w / 2, 0.0, window_w, window_h, sill, side_count, mats)
    add_window_row(parts, "Floor", d * 0.9, "right", w / 2, 0.0, window_w, window_h, sill, side_count, mats)

    if setback:
        # Terrace deck over the full original footprint + parapet on the exposed front edge
        parts.append(add_box("Setback_TerraceDeck", (full_w, full_d, 0.08), (0, 0, 0.04), mats["concrete"]))
        parapet_h = 1.0
        parts.append(add_box("Setback_ParapetFront", (full_w, 0.14, parapet_h),
                             (0, -full_d / 2 + 0.07, parapet_h / 2), shell_mat))
        parts.append(add_box("Setback_ParapetLeft", (0.14, inset_front, parapet_h),
                             (-full_w / 2 + 0.07, -full_d / 2 + inset_front / 2, parapet_h / 2), shell_mat))
        parts.append(add_box("Setback_ParapetRight", (0.14, inset_front, parapet_h),
                             (full_w / 2 - 0.07, -full_d / 2 + inset_front / 2, parapet_h / 2), shell_mat))

    return join_as("MOD_Setback" if setback else "MOD_Floor", parts)


def _graph_lookup(grammar: dict) -> tuple[dict, dict, dict, dict]:
    graph = grammar.get("facade_graph") or {}
    openings = {item["id"]: item for item in graph.get("openings", [])}
    attachments = {item["id"]: item for item in graph.get("attachments", [])}
    bays = {item["id"]: item for item in graph.get("bays", [])}
    variants = {item["key"]: item for item in graph.get("floor_variants", [])}
    return openings, attachments, bays, variants


def _add_balcony_v3(
    parts: list,
    prefix: str,
    x: float,
    facade_y: float,
    bay_width: float,
    depth: float,
    guard: str,
    mats: dict,
    plants: bool = False,
) -> None:
    width = bay_width * 0.84
    centre_y = facade_y - depth / 2
    front_y = facade_y - depth + 0.035
    parts.append(add_box(f"{prefix}_Slab", (width, depth, 0.14), (x, centre_y, 0.18), mats["concrete"]))
    parts.append(add_box(f"{prefix}_SlabShadow", (width - 0.08, depth - 0.05, 0.035),
                         (x, centre_y, 0.095), mats["accent"]))
    if guard == "solid":
        parts.append(add_box(f"{prefix}_Guard", (width, 0.13, 0.82), (x, front_y, 0.66), mats["secondary"]))
    elif guard == "planter":
        parts.append(add_box(f"{prefix}_Planter", (width, 0.22, 0.48), (x, front_y, 0.52), mats["primary"]))
        parts.append(add_box(f"{prefix}_GlassGuard", (width - 0.12, 0.045, 0.52), (x, front_y - 0.04, 1.02), mats["glass"]))
    else:
        guard_mat = mats["glass"] if guard == "glass" else mats["accent"]
        parts.append(add_box(f"{prefix}_Guard", (width, 0.045, 0.84), (x, front_y, 0.73), guard_mat))
    parts.append(add_box(f"{prefix}_Rail", (width + 0.08, 0.065, 0.065), (x, front_y - 0.035, 1.18), mats["accent"]))
    parts.append(add_box(f"{prefix}_SideL", (0.055, depth - 0.12, 0.92), (x - width / 2 + 0.03, centre_y, 0.7), mats["accent"]))
    parts.append(add_box(f"{prefix}_SideR", (0.055, depth - 0.12, 0.92), (x + width / 2 - 0.03, centre_y, 0.7), mats["accent"]))
    if plants:
        add_planter_vegetation(parts, f"{prefix}_Vegetation", (x, front_y - 0.02, 0.72), width, mats)


def _add_oriel_v3(
    parts: list,
    prefix: str,
    x: float,
    facade_y: float,
    bay_width: float,
    opening_h: float,
    sill: float,
    projection: float,
    mats: dict,
) -> None:
    """Projecting, vertically stackable brick oriel with glazed front/sides."""
    width = bay_width * 0.86
    projection = max(0.72, projection + 0.5)
    front_y = facade_y - projection
    centre_z = sill + opening_h / 2
    masonry = mats["secondary"]
    parts.append(add_box(f"{prefix}_Base", (width, projection, 0.2), (x, facade_y - projection / 2, sill - 0.08), masonry))
    parts.append(add_box(f"{prefix}_Head", (width, projection, 0.2), (x, facade_y - projection / 2, sill + opening_h + 0.08), masonry))
    for side, sign in (("L", -1), ("R", 1)):
        side_x = x + sign * (width / 2 - 0.09)
        parts.append(add_box(f"{prefix}_Pier{side}", (0.18, projection, opening_h), (side_x, facade_y - projection / 2, centre_z), masonry))
        parts.append(add_box(f"{prefix}_SideGlass{side}", (0.055, projection * 0.62, opening_h * 0.78),
                             (x + sign * (width / 2 - 0.13), facade_y - projection * 0.52, centre_z), mats["glass"]))
    glass_width = width - 0.48
    parts.append(add_box(f"{prefix}_Shadow", (glass_width + 0.12, 0.06, opening_h + 0.12), (x, front_y + 0.06, centre_z), mats["interior"]))
    parts.append(add_box(f"{prefix}_Glass", (glass_width, 0.055, opening_h), (x, front_y - 0.015, centre_z), mats["glass"]))
    add_frame_bars(parts, f"{prefix}_Frame", "front", (x, front_y - 0.055, centre_z),
                   glass_width, opening_h, 0.1, mats["accent"], profile=0.07, mullions="double")


def _add_crown_v3(parts: list, system: str, w: float, d: float, h: float, facade_y: float, mats: dict) -> None:
    """One silhouette-scale signature per family, kept separate from the
    repeating middle so a building reads as base / body / crown."""
    if system == "timber_grid":
        parts.append(add_box("Crown_TimberCanopy", (w + 0.8, d + 0.7, 0.24), (0, 0, h - 0.12), mats["primary"]))
        for index, x in enumerate((-w * 0.34, -w * 0.17, 0.0, w * 0.17, w * 0.34)):
            parts.append(add_box(f"Crown_TimberFin{index}", (0.18, 0.55, h * 0.72), (x, facade_y - 0.22, h * 0.52), mats["primary"]))
        for index, x in enumerate((-w * 0.31, 0.0, w * 0.31)):
            parts.append(add_box(f"Crown_Planter{index}", (w * 0.2, 0.72, 0.38), (x, facade_y - 0.46, 0.3), mats["primary"]))
            add_planter_vegetation(parts, f"Crown_Green{index}", (x, facade_y - 0.5, 0.5), w * 0.2, mats)
    elif system == "punched_render":
        parts.append(add_box("Crown_WhiteBlade", (w + 0.42, 0.32, h * 0.92), (0, facade_y - 0.12, h * 0.5), mats["primary"]))
        # Deeply cut loggia across the centre prevents another flat white box.
        loggia_w = w * 0.52
        parts.append(add_box("Crown_LoggiaShadow", (loggia_w, 0.12, h * 0.58), (0, facade_y - 0.31, h * 0.52), mats["interior"]))
        parts.append(add_box("Crown_LoggiaGlass", (loggia_w * 0.92, 0.055, h * 0.5), (0, facade_y - 0.38, h * 0.5), mats["glass"]))
        for index, x in enumerate((-loggia_w / 2, 0.0, loggia_w / 2)):
            parts.append(add_box(f"Crown_PergolaPost{index}", (0.12, 1.1, h * 0.78), (x, facade_y - 0.5, h * 0.54), mats["accent"]))
        parts.append(add_box("Crown_PergolaBeam", (loggia_w + 0.5, 1.2, 0.14), (0, facade_y - 0.5, h - 0.2), mats["accent"]))
    elif system == "brick_bays":
        for index, (extra_w, z, band_h) in enumerate(((0.18, h - 0.7, 0.18), (0.42, h - 0.4, 0.22), (0.72, h - 0.12, 0.24))):
            parts.append(add_box(f"Crown_Cornice{index}", (w + extra_w, 0.36 + index * 0.1, band_h),
                                 (0, facade_y - 0.08 - index * 0.03, z), mats["secondary"]))
        # Brick pilasters align with the body/oriel rhythm.
        for index, x in enumerate((-w * 0.38, -w * 0.19, 0.0, w * 0.19, w * 0.38)):
            parts.append(add_box(f"Crown_BrickPier{index}", (0.28, 0.34, h * 0.82), (x, facade_y - 0.1, h * 0.46), mats["secondary"]))
    elif system == "stone_frame":
        parts.append(add_box("Crown_CortenHeader", (w + 0.55, 0.5, 0.28), (0, facade_y - 0.12, h - 0.17), mats["secondary"]))
        for index, x in enumerate((-w * 0.42, -w * 0.28, -w * 0.14, 0.0, w * 0.14, w * 0.28, w * 0.42)):
            parts.append(add_box(f"Crown_CortenFin{index}", (0.13, 0.48, h * 0.82), (x, facade_y - 0.1, h * 0.47), mats["secondary"]))
        parts.append(add_box("Crown_StoneDatum", (w + 0.2, 0.25, 0.24), (0, facade_y - 0.04, 0.18), mats["primary"]))


def build_floor_v3(
    grammar: dict,
    mats: dict,
    variant_key: str = "typical_a",
    interior_seed: int = 0,
) -> bpy.types.Object:
    """Build one graph-selected floor with a true front facade opening system."""
    dims, facade, massing = grammar["dimensions"], grammar["facade"], grammar["massing"]
    openings, attachment_specs, bay_specs, variants = _graph_lookup(grammar)
    variant = variants.get(variant_key) or variants.get("typical_a") or {}
    setback = variant_key == "upper"
    crown = variant_key == "crown"
    h = dims["setback_height_m"] if setback else dims["floor_height_m"]
    full_w, full_d = dims["width_m"], dims["depth_m"]

    if setback:
        inset_front = max(float(massing.get("setback_front_m", 0.0)), 0.8)
        inset_side = max(float(massing.get("setback_side_m", 0.0)), 0.45)
    elif crown:
        inset_front = 0.35
        inset_side = 0.2
    else:
        inset_front = inset_side = 0.0
    w = full_w - inset_side * 2
    d = full_d - inset_front
    centre_y = inset_front / 2
    facade_y = centre_y - d / 2
    system = facade.get("system", "regular")

    parts: list = []
    reveal_depth = max(0.18, float(facade.get("window_recess_m", 0.18)))
    wall_depth = min(0.24, reveal_depth * 0.72)
    # Reserve a shallow room behind the glazing instead of pressing the dark
    # backing plane directly against it. The resulting jamb/ceiling shadows are
    # visible in both close orbit views and aerial renders.
    interior_depth = min(0.42, max(0.24, reveal_depth * 1.35))
    core_depth = max(0.5, d - reveal_depth - interior_depth)
    core_mat = mats["secondary"] if setback else mats["primary"]
    # The core stops behind the front facade. The facade itself is reconstructed
    # from sill/head/pier solids, leaving a true opening at every bay.
    parts.append(add_box(
        "Floor_Core", (w, core_depth, h),
        (0, centre_y + (reveal_depth + interior_depth) / 2, h / 2), core_mat,
    ))
    parts.append(add_box("Floor_SlabEdge", (w + 0.1, d + 0.08, 0.2), (0, centre_y, 0.1), mats["concrete"]))

    bay_sequence = list(variant.get("bay_sequence") or [])
    bay_count = len(bay_sequence) or int(facade.get("front_bay_count", 1))
    if not bay_sequence:
        bay_sequence = ["standard"] * bay_count
    bay_width = w / bay_count

    for index, bay_key in enumerate(bay_sequence):
        bay_spec = bay_specs.get(bay_key) or bay_specs.get("standard") or {}
        opening = openings.get(bay_spec.get("opening_id")) or next(iter(openings.values()))
        x = -w / 2 + bay_width * (index + 0.5)
        opening_w = min(bay_width * float(opening.get("width_ratio", 0.55)), bay_width - 0.5)
        opening_h = min(h * float(opening.get("height_ratio", 0.62)), h - 0.62)
        sill = min(float(opening.get("sill_m", 0.75)), h - opening_h - 0.32)
        opening_z = sill + opening_h / 2
        panel_mat = mats.get(bay_spec.get("material_slot", "primary"), mats["primary"])
        projection = float(bay_spec.get("projection_m", 0.0))

        left_edge = x - bay_width / 2
        pier_width = max(0.18, (bay_width - opening_w) / 2)
        # Each bay is four wall pieces around an actual void.
        parts.append(add_box(f"V3_{index:02d}_SillPanel", (bay_width + 0.01, wall_depth, max(0.12, sill)),
                             (x, facade_y + wall_depth / 2, max(0.12, sill) / 2), panel_mat))
        head_h = max(0.12, h - sill - opening_h)
        parts.append(add_box(f"V3_{index:02d}_HeadPanel", (bay_width + 0.01, wall_depth, head_h),
                             (x, facade_y + wall_depth / 2, sill + opening_h + head_h / 2), panel_mat))
        parts.append(add_box(f"V3_{index:02d}_PierL", (pier_width + 0.01, wall_depth, opening_h),
                             (left_edge + pier_width / 2, facade_y + wall_depth / 2, opening_z), panel_mat))
        parts.append(add_box(f"V3_{index:02d}_PierR", (pier_width + 0.01, wall_depth, opening_h),
                             (left_edge + bay_width - pier_width / 2, facade_y + wall_depth / 2, opening_z), panel_mat))

        glass_y = facade_y + reveal_depth - 0.035
        atlas_cells = mats.get("interior_cells") or []
        variant_seed = {"typical_a": 0, "typical_b": 3, "upper": 5, "crown": 7}.get(variant_key, 0)
        interior_mat = atlas_cells[(index * 3 + variant_seed + interior_seed) % len(atlas_cells)] if atlas_cells else (
            mats["interior_warm"] if (index + (1 if variant_key == "typical_b" else 0)) % 4 == 0 else mats["interior"]
        )
        interior_y = facade_y + reveal_depth + interior_depth - 0.035
        parts.append(add_box(f"V4_{index:02d}_Interior", (opening_w + 0.14, 0.055, opening_h + 0.14),
                             (x, interior_y, opening_z), interior_mat))
        # Return surfaces give the opening genuine depth and catch ambient
        # occlusion rather than reading as glass pasted onto a wall.
        return_depth = max(0.12, interior_y - glass_y)
        return_y = (glass_y + interior_y) / 2
        parts.append(add_box(f"V4_{index:02d}_SillReturn", (opening_w, return_depth, 0.055),
                             (x, return_y, sill + 0.035), mats["concrete"]))
        parts.append(add_box(f"V4_{index:02d}_HeadReturn", (opening_w, return_depth, 0.045),
                             (x, return_y, sill + opening_h - 0.025), mats["accent"]))
        parts.append(add_box(f"V3_{index:02d}_Glass", (opening_w, 0.05, opening_h),
                             (x, glass_y, opening_z), mats["glass"]))
        add_frame_bars(
            parts, f"V3_{index:02d}_Frame", "front", (x, facade_y - 0.035, opening_z),
            opening_w, opening_h, 0.1, mats["accent"],
            profile=0.065 if opening.get("frame_profile_id") == "slim" else 0.09,
            mullions=opening.get("mullion_pattern", "single"),
        )
        parts.append(add_box(f"V4_{index:02d}_SillCap", (opening_w + 0.12, 0.16, 0.055),
                             (x, facade_y - 0.045, sill - 0.015), mats["accent"]))
        if system == "brick_bays":
            parts.append(add_box(f"V4_{index:02d}_SoldierCourse", (opening_w + 0.32, 0.15, 0.14),
                                 (x, facade_y - 0.035, sill + opening_h + 0.10), mats["secondary"]))

        attachment_ids = bay_spec.get("attachment_ids") or []
        attachment_kinds = {attachment_specs[item]["kind"] for item in attachment_ids if item in attachment_specs}
        if "oriel" in attachment_kinds and not crown:
            _add_oriel_v3(parts, f"V3_Oriel_{index:02d}", x, facade_y, bay_width, opening_h, sill,
                          max(projection, 0.2), mats)
        elif "balcony" in attachment_kinds and not crown and not setback:
            _add_balcony_v3(
                parts, f"V3_Balcony_{index:02d}", x, facade_y, bay_width,
                float(facade.get("balcony_depth_m", 1.5)), facade.get("balcony_guard", "metal"), mats,
                plants=facade.get("balcony_guard") == "planter",
            )

    # Material joint/post grids make each facade system legible from an aerial
    # view and prevent a single smooth procedural slab from dominating.
    grid_mat = mats["primary"] if system == "timber_grid" else mats["accent"]
    grid_width = 0.14 if system == "timber_grid" else 0.035
    grid_depth = 0.24 if system == "timber_grid" else 0.055
    if system in ("timber_grid", "punched_render", "stone_frame"):
        for joint_index in range(bay_count + 1):
            joint_x = -w / 2 + bay_width * joint_index
            parts.append(add_box(
                f"V4_FacadeJoint_{joint_index:02d}", (grid_width, grid_depth, h - 0.16),
                (joint_x, facade_y - grid_depth / 2 + 0.02, h / 2), grid_mat,
            ))
    if system == "stone_frame":
        parts.append(add_box("V4_StonePanelDatum", (w, 0.055, 0.035),
                             (0, facade_y - 0.02, h * 0.48), mats["accent"]))

    # Rear and sides remain economical overlay systems; the street-facing
    # elevation receives the high-fidelity geometric treatment.
    side_count, _ = _bays(d, facade["bay_width_m"])
    rear_window_w = min(bay_width * float(facade.get("window_width_ratio", 0.55)), bay_width - 0.55)
    rear_window_h = h * float(facade.get("window_height_ratio", 0.62))
    rear_sill = min(float(facade.get("sill_height_m", 0.75)), h - rear_window_h - 0.3)
    add_window_row(parts, "V3_Floor", w, "rear", centre_y + d / 2, 0.0, rear_window_w, rear_window_h, rear_sill, bay_count, mats,
                   interior_seed=interior_seed)
    add_window_row(parts, "V3_Floor", d * 0.9, "left", w / 2, 0.0, rear_window_w, rear_window_h, rear_sill, side_count, mats,
                   interior_seed=interior_seed)
    add_window_row(parts, "V3_Floor", d * 0.9, "right", w / 2, 0.0, rear_window_w, rear_window_h, rear_sill, side_count, mats,
                   interior_seed=interior_seed)

    if system in ("timber_grid", "punched_render", "stone_frame"):
        wrap_mat = mats["primary"] if system == "timber_grid" else mats["accent"]
        wrap_width = 0.13 if system == "timber_grid" else 0.032
        wrap_depth = 0.2 if system == "timber_grid" else 0.05
        side_span = d * 0.9
        for side_joint in range(side_count + 1):
            joint_y = centre_y - side_span / 2 + side_span * side_joint / side_count
            for side_name, side_x in (("L", -w / 2 - wrap_depth / 2), ("R", w / 2 + wrap_depth / 2)):
                parts.append(add_box(
                    f"V4_SideJoint{side_name}_{side_joint:02d}",
                    (wrap_depth, wrap_width, h - 0.16), (side_x, joint_y, h / 2), wrap_mat,
                ))
        for rear_joint in range(bay_count + 1):
            joint_x = -w / 2 + w * rear_joint / bay_count
            parts.append(add_box(
                f"V4_RearJoint_{rear_joint:02d}",
                (wrap_width, wrap_depth, h - 0.16),
                (joint_x, centre_y + d / 2 + wrap_depth / 2, h / 2), wrap_mat,
            ))
        if system in ("punched_render", "stone_frame"):
            parts.append(add_box("V4_RearPanelDatum", (w, 0.055, 0.035),
                                 (0, centre_y + d / 2 + 0.025, h * 0.48), mats["accent"]))
            for side_name, side_x in (("L", -w / 2 - 0.025), ("R", w / 2 + 0.025)):
                parts.append(add_box(f"V4_SidePanelDatum{side_name}", (0.055, d * 0.9, 0.035),
                                     (side_x, centre_y, h * 0.48), mats["accent"]))

    if system in ("timber_grid", "brick_bays"):
        parts.append(add_box("V3_FacadeDatum", (w + 0.16, 0.17, 0.18),
                             (0, facade_y - 0.06, h - 0.11), mats["primary"] if system == "timber_grid" else mats["secondary"]))
    if setback:
        parts.append(add_box("V3_TerraceDeck", (full_w, full_d, 0.09), (0, 0, 0.045), mats["concrete"]))
        terrace_y = -full_d / 2 + 0.07
        parts.append(add_box("V3_TerraceRail", (full_w, 0.075, 0.075), (0, terrace_y, 0.98), mats["accent"]))
        for post_index, x in enumerate((-full_w / 2 + 0.12, -full_w / 4, 0.0, full_w / 4, full_w / 2 - 0.12)):
            parts.append(add_box(f"V3_TerracePost{post_index}", (0.075, 0.075, 0.92), (x, terrace_y, 0.5), mats["accent"]))
    if crown:
        _add_crown_v3(parts, system, w, d, h, facade_y, mats)

    role_name = "Crown" if crown else "Setback" if setback else variant_key.title().replace("_", "")
    return join_as(f"MOD_{role_name}", parts)


def build_roof(grammar: dict, mats: dict) -> bpy.types.Object:
    dims, roof = grammar["dimensions"], grammar["roof"]
    w, d, h = dims["width_m"], dims["depth_m"], dims["roof_height_m"]
    parts: list = []

    if roof["type"] == "gabled":
        # Triangular prism, ridge running along X (parallel to the front facade)
        slab_h = 0.2
        parts.append(add_box("Roof_Base", (w + 0.4, d + 0.4, slab_h), (0, 0, slab_h / 2), mats["roof"]))
        ridge = h
        ov = 0.35  # eave overhang
        verts = [
            (-w / 2 - ov, -d / 2 - ov, slab_h), (w / 2 + ov, -d / 2 - ov, slab_h),
            (w / 2 + ov, d / 2 + ov, slab_h), (-w / 2 - ov, d / 2 + ov, slab_h),
            (-w / 2 - ov, 0.0, ridge), (w / 2 + ov, 0.0, ridge),
        ]
        faces = [(0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)]
        parts.append(add_prism("Roof_Gable", verts, faces, mats["roof"]))
    elif roof["type"] == "mono_pitch":
        slab_h = 0.2
        parts.append(add_box("Roof_Base", (w + 0.3, d + 0.3, slab_h), (0, 0, slab_h / 2), mats["roof"]))
        low, high = slab_h + 0.15, h
        verts = [
            (-w / 2, -d / 2, slab_h), (w / 2, -d / 2, slab_h), (w / 2, d / 2, slab_h), (-w / 2, d / 2, slab_h),
            (-w / 2, -d / 2, low), (w / 2, -d / 2, low), (w / 2, d / 2, high), (-w / 2, d / 2, high),
        ]
        faces = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7), (3, 2, 1, 0)]
        parts.append(add_prism("Roof_Mono", verts, faces, mats["roof"]))
    else:  # flat
        slab_h = 0.25
        parts.append(add_box("Roof_Slab", (w, d, slab_h), (0, 0, slab_h / 2), mats["roof"]))
        if roof.get("parapet", True):
            ph, t = 0.65, 0.2
            parts.append(add_box("Roof_ParapetFront", (w, t, ph), (0, -d / 2 + t / 2, ph / 2), mats["primary"]))
            parts.append(add_box("Roof_ParapetBack", (w, t, ph), (0, d / 2 - t / 2, ph / 2), mats["primary"]))
            parts.append(add_box("Roof_ParapetLeft", (t, d - t * 2, ph), (-w / 2 + t / 2, 0, ph / 2), mats["primary"]))
            parts.append(add_box("Roof_ParapetRight", (t, d - t * 2, ph), (w / 2 - t / 2, 0, ph / 2), mats["primary"]))
            # Thin coping caps catch highlights and make the roof edge read as
            # an assembled construction instead of an extruded wall.
            cap_h, cap_w = 0.055, t + 0.08
            parts.append(add_box("Roof_CopingFront", (w + 0.08, cap_w, cap_h), (0, -d / 2 + t / 2, ph + cap_h / 2), mats["accent"]))
            parts.append(add_box("Roof_CopingBack", (w + 0.08, cap_w, cap_h), (0, d / 2 - t / 2, ph + cap_h / 2), mats["accent"]))
            parts.append(add_box("Roof_CopingLeft", (cap_w, d - t * 2, cap_h), (-w / 2 + t / 2, 0, ph + cap_h / 2), mats["accent"]))
            parts.append(add_box("Roof_CopingRight", (cap_w, d - t * 2, cap_h), (w / 2 - t / 2, 0, ph + cap_h / 2), mats["accent"]))
        if roof.get("green_roof"):
            parts.append(add_box("Roof_GreenSurface", (w - 0.8, d - 0.8, 0.09), (0, 0, slab_h + 0.045), mats["green_roof"]))
        if roof.get("mechanical_screen"):
            mw, md, mh = w * 0.24, d * 0.28, max(0.8, h * 0.75)
            parts.append(add_box("Roof_MechScreen", (mw, md, mh), (w * 0.18, d * 0.12, slab_h + mh / 2), mats["accent"]))

        if h >= 0.75:
            service_top = min(h - 0.045, 1.12)
            unit_h = max(0.22, service_top - slab_h - 0.18)
            # Two real-scale air handling units with fan cowls and service pads.
            equipment = (
                (-w * 0.18, d * 0.17, w * 0.15, d * 0.13),
                (w * 0.03, -d * 0.18, w * 0.12, d * 0.11),
            )
            for unit_index, (x, y, unit_w, unit_d) in enumerate(equipment):
                pad_z = slab_h + 0.055
                parts.append(add_box(f"Roof_ServicePad{unit_index}", (unit_w + 0.34, unit_d + 0.34, 0.11),
                                     (x, y, pad_z), mats["concrete"]))
                parts.append(add_box(f"Roof_AHU{unit_index}", (unit_w, unit_d, unit_h),
                                     (x, y, slab_h + 0.11 + unit_h / 2), mats["accent"]))
                for fan_index, fan_x in enumerate((-unit_w * 0.24, unit_w * 0.24)):
                    parts.append(add_cylinder(
                        f"Roof_AHU{unit_index}_Fan{fan_index}",
                        min(unit_w, unit_d) * 0.16, 0.055,
                        (x + fan_x, y, slab_h + 0.11 + unit_h + 0.028), mats["roof"], 18,
                    ))
                # Horizontal louver bars give the equipment a believable scale.
                for louver_index in range(3):
                    parts.append(add_box(
                        f"Roof_AHU{unit_index}_Louver{louver_index}",
                        (unit_w * 0.72, 0.035, 0.035),
                        (x, y - unit_d / 2 - 0.02, slab_h + 0.2 + louver_index * unit_h * 0.22),
                        mats["roof"],
                    ))

            # Access penthouse, vents and drain leaders break the empty-roof silhouette.
            access_h = max(0.3, service_top - slab_h - 0.08)
            parts.append(add_box("Roof_AccessPenthouse", (w * 0.13, d * 0.15, access_h),
                                 (-w * 0.04, d * 0.31, slab_h + access_h / 2), mats["primary"]))
            parts.append(add_box("Roof_AccessDoor", (w * 0.045, 0.045, access_h * 0.72),
                                 (-w * 0.04, d * 0.31 - d * 0.075 - 0.025, slab_h + access_h * 0.42), mats["accent"]))
            for vent_index, (x, y) in enumerate(((-w * 0.33, -d * 0.28), (w * 0.34, d * 0.31), (w * 0.31, -d * 0.31))):
                vent_h = min(0.5, service_top - slab_h)
                parts.append(add_cylinder(f"Roof_Vent{vent_index}", 0.09, vent_h,
                                          (x, y, slab_h + vent_h / 2), mats["accent"], 14))
                parts.append(add_cylinder(f"Roof_VentCap{vent_index}", 0.15, 0.055,
                                          (x, y, slab_h + vent_h + 0.027), mats["roof"], 14))

            # A compact PV field adds high-frequency aerial detail without
            # covering the planted portion of a green roof.
            pv_y = -d * 0.30 if roof.get("green_roof") else d * 0.32
            for row in range(2):
                for column in range(4):
                    panel_x = -w * 0.24 + column * w * 0.16
                    panel = add_box(
                        f"Roof_PV_{row}_{column}", (w * 0.13, d * 0.09, 0.045),
                        (panel_x, pv_y + row * d * 0.11, slab_h + 0.18), mats["glass"],
                    )
                    panel.rotation_euler.x = math.radians(7)
                    parts.append(panel)

    return join_as("MOD_Roof", parts)


# ---------------------------------------------------------------------------
# Export / render
# ---------------------------------------------------------------------------

def export_objects(path: Path, objects: list[bpy.types.Object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    kwargs = dict(
        filepath=str(path),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,   # Blender Z-up -> glTF Y-up; front (-Y) becomes glTF +Z
        export_cameras=False,
        export_lights=False,
        export_extras=True,
        # AUTO preserves lossless normal/AO maps and keeps source JPEG albedo
        # maps compressed instead of recompressing every texture indiscriminately.
        export_image_format="AUTO",
    )
    try:
        bpy.ops.export_scene.gltf(**kwargs)
    except TypeError:  # older exporter without export_jpeg_quality
        kwargs.pop("export_jpeg_quality", None)
        bpy.ops.export_scene.gltf(**kwargs)


def triangle_count(obj: bpy.types.Object) -> int:
    obj.data.calc_loop_triangles()
    return len(obj.data.loop_triangles)


def pick_render_engine(preferred: str = "eevee", samples: int = 48) -> str:
    scene = bpy.context.scene
    if preferred == "cycles":
        try:
            scene.render.engine = "CYCLES"
            scene.cycles.samples = samples
            scene.cycles.use_denoising = True
            scene.cycles.use_adaptive_sampling = True
            scene.cycles.adaptive_threshold = 0.035
            scene.cycles.max_bounces = 6
            scene.cycles.diffuse_bounces = 3
            scene.cycles.glossy_bounces = 3
            scene.cycles.transmission_bounces = 4
            return "CYCLES"
        except (TypeError, AttributeError):
            pass
    for engine in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "BLENDER_WORKBENCH"):
        try:
            scene.render.engine = engine
            return engine
        except TypeError:
            continue
    return scene.render.engine


def add_preview_tree(
    rig: list[bpy.types.Object],
    index: int,
    x: float,
    y: float,
    scale: float,
    bark_mat,
    leaf_mat,
) -> None:
    """Layered broadleaf tree tuned for oblique urban-scale renders."""
    trunk_h = 4.3 * scale
    rig.append(add_cylinder(f"ContextTreeTrunk{index}", 0.17 * scale, trunk_h,
                            (x, y, trunk_h / 2), bark_mat, 10))
    crowns = (
        (0.0, 0.0, 1.1, (1.55, 1.35, 1.55)),
        (-0.72, 0.08, 0.62, (1.12, 1.0, 1.12)),
        (0.68, -0.05, 0.74, (1.08, 0.96, 1.2)),
        (0.05, 0.55, 0.78, (1.02, 0.92, 1.06)),
    )
    for crown_index, (dx, dy, dz, crown_scale) in enumerate(crowns):
        rig.append(add_foliage(
            f"ContextTreeCrown{index}_{crown_index}",
            (x + dx * scale, y + dy * scale, trunk_h + dz * scale),
            tuple(value * scale for value in crown_scale), leaf_mat,
        ))


def add_context_building(
    rig: list[bpy.types.Object],
    index: int,
    x: float,
    y: float,
    width: float,
    depth: float,
    height: float,
    facade_mat,
    context_mats: dict,
) -> None:
    """A lightweight but articulated background building for aerial review."""
    rig.append(add_box(f"ContextBuilding{index}_Body", (width, depth, height),
                       (x, y, height / 2), facade_mat))
    rig.append(add_box(f"ContextBuilding{index}_Plinth", (width + 0.16, depth + 0.16, 0.55),
                       (x, y, 0.275), context_mats["concrete"]))
    parapet_h = 0.5
    rig.append(add_box(f"ContextBuilding{index}_Roof", (width + 0.12, depth + 0.12, 0.22),
                       (x, y, height + 0.11), context_mats["roof"]))
    rig.append(add_box(f"ContextBuilding{index}_ParapetFront", (width, 0.18, parapet_h),
                       (x, y - depth / 2 + 0.09, height + parapet_h / 2), facade_mat))
    rig.append(add_box(f"ContextBuilding{index}_ParapetBack", (width, 0.18, parapet_h),
                       (x, y + depth / 2 - 0.09, height + parapet_h / 2), facade_mat))

    floors = max(2, round(height / 3.25))
    floor_height = height / floors
    for floor in range(floors):
        window_z = floor_height * (floor + 0.56)
        window_h = min(1.25, floor_height * 0.42)
        rig.append(add_box(
            f"ContextBuilding{index}_FrontGlass{floor}",
            (width * 0.78, 0.045, window_h),
            (x, y - depth / 2 - 0.028, window_z), context_mats["glass"],
        ))
        rig.append(add_box(
            f"ContextBuilding{index}_SideGlass{floor}",
            (0.045, depth * 0.7, window_h),
            (x + width / 2 + 0.028, y, window_z), context_mats["glass"],
        ))

    unit_w, unit_d = width * 0.18, depth * 0.2
    rig.append(add_box(f"ContextBuilding{index}_RoofUnit", (unit_w, unit_d, 0.72),
                       (x + width * 0.18, y - depth * 0.08, height + 0.58), context_mats["metal"]))
    rig.append(add_cylinder(f"ContextBuilding{index}_Vent", 0.13, 0.55,
                            (x - width * 0.22, y + depth * 0.16, height + 0.48), context_mats["metal"], 12))


def render_presentation_views(
    output: Path,
    family: str,
    focus_height: float,
    width: float,
    depth: float,
    preferred_engine: str = "eevee",
    samples: int = 48,
) -> tuple[str, list[str]]:
    """Render consistent studio, street and aerial views of the assembled kit.

    Context is deterministic and exists only for these review images; it never
    leaks into the modular or assembled GLBs.
    """
    scene = bpy.context.scene
    engine = pick_render_engine(preferred_engine, samples)
    footprint = max(width, depth)

    ground_mat = make_material("MAT_PreviewGround", {"base_color": "#b9b6ae", "roughness": 0.92, "metallic": 0.0})
    road_mat = make_material("MAT_PreviewRoad", {"base_color": "#33373b", "roughness": 0.95, "metallic": 0.0})
    curb_mat = make_material("MAT_PreviewCurb", {"base_color": "#d5d0c5", "roughness": 0.9, "metallic": 0.0})
    bark_mat = make_material("MAT_PreviewBark", {"base_color": "#5d4431", "roughness": 0.95, "metallic": 0.0})
    leaf_mat = make_material("MAT_PreviewLeaves", {"base_color": "#527543", "roughness": 0.88, "metallic": 0.0})
    leaf_alt_mat = make_material("MAT_PreviewLeavesAlt", {"base_color": "#6d7541", "roughness": 0.9, "metallic": 0.0})
    line_mat = make_material("MAT_PreviewLine", {"base_color": "#d9d1b5", "roughness": 0.82, "metallic": 0.0})
    context_mats = {
        "facade_light": make_material("MAT_ContextFacadeLight", {"base_color": "#c9c5ba", "roughness": 0.82, "metallic": 0.0}),
        "facade_warm": make_material("MAT_ContextFacadeWarm", {"base_color": "#a89b87", "roughness": 0.86, "metallic": 0.0}),
        "facade_white": make_material("MAT_ContextFacadeWhite", {"base_color": "#dedbd2", "roughness": 0.8, "metallic": 0.0}),
        "facade_dark": make_material("MAT_ContextFacadeDark", {"base_color": "#666963", "roughness": 0.83, "metallic": 0.0}),
        "glass": make_material("MAT_ContextGlass", {"base_color": "#50616d", "roughness": 0.2, "metallic": 0.1}),
        "concrete": curb_mat,
        "roof": make_material("MAT_ContextRoof", {"base_color": "#696d6b", "roughness": 0.92, "metallic": 0.0}),
        "metal": make_material("MAT_ContextMetal", {"base_color": "#818682", "roughness": 0.48, "metallic": 0.45}),
    }

    rig: list[bpy.types.Object] = []
    rig.append(add_box("PreviewGround", (footprint * 18, footprint * 18, 0.06), (0, 0, -0.04), ground_mat))
    street_y = -(depth / 2 + 7.0)
    road_length = footprint * 9.0
    rig.append(add_box("PreviewSidewalk", (road_length, 5.0, 0.13), (0, -(depth / 2 + 2.25), 0.045), curb_mat))
    rig.append(add_box("PreviewRoad", (road_length, 10.0, 0.08), (0, street_y, -0.005), road_mat))
    rig.append(add_box("PreviewCurb", (road_length, 0.26, 0.28), (0, -(depth / 2 + 4.85), 0.1), curb_mat))
    rear_road_y = depth / 2 + 23.0
    rig.append(add_box("PreviewRearRoad", (road_length, 11.0, 0.08), (0, rear_road_y, -0.005), road_mat))
    for cross_index, cross_x in enumerate((-width / 2 - 27.0, width / 2 + 29.0)):
        rig.append(add_box(f"PreviewCrossRoad{cross_index}", (10.5, road_length, 0.08),
                           (cross_x, 12.0, -0.003), road_mat))

    # Broken centre lines and parking bays add the small-scale evidence that
    # makes the aerial view feel like a real urban block.
    for line_index in range(-8, 9):
        rig.append(add_box(f"PreviewLaneMark{line_index}", (5.2, 0.12, 0.025),
                           (line_index * 11.0, street_y, 0.055), line_mat))
    parking_x, parking_y = width / 2 + 13.0, depth / 2 + 6.0
    rig.append(add_box("PreviewParkingLot", (20.0, 24.0, 0.045), (parking_x, parking_y, 0.01), road_mat))
    for bay_index in range(6):
        rig.append(add_box(f"PreviewParkingLine{bay_index}", (0.08, 8.0, 0.025),
                           (parking_x - 8.5 + bay_index * 3.4, parking_y - 6.0, 0.055), line_mat))

    facade_cycle = (
        context_mats["facade_light"], context_mats["facade_warm"],
        context_mats["facade_white"], context_mats["facade_dark"],
    )
    context_buildings = (
        (-53.0, 7.0, 24.0, 27.0, 16.0), (-48.0, 48.0, 32.0, 19.0, 24.0),
        (-12.0, 50.0, 24.0, 21.0, 31.0), (22.0, 53.0, 30.0, 20.0, 18.0),
        (58.0, 46.0, 25.0, 22.0, 27.0), (57.0, 5.0, 23.0, 25.0, 14.0),
        (-63.0, -34.0, 30.0, 20.0, 12.0), (-26.0, -43.0, 25.0, 19.0, 19.0),
        (22.0, -44.0, 29.0, 18.0, 15.0), (61.0, -36.0, 27.0, 21.0, 22.0),
        (-91.0, 42.0, 34.0, 24.0, 20.0), (94.0, 38.0, 38.0, 25.0, 17.0),
    )
    context_only: list[bpy.types.Object] = []
    for context_index, spec in enumerate(context_buildings):
        context_start = len(rig)
        add_context_building(rig, context_index, *spec, facade_cycle[context_index % len(facade_cycle)], context_mats)
        context_only.extend(rig[context_start:])

    tree_positions = (
        (-width * 0.72, -depth / 2 - 3.1, 0.9), (width * 0.74, -depth / 2 - 3.5, 1.0),
        (-19.0, 17.0, 1.15), (18.0, 18.0, 0.95), (-36.0, 24.0, 1.2), (39.0, 28.0, 1.1),
        (-67.0, 25.0, 1.05), (72.0, 24.0, 1.2), (-42.0, -21.0, 0.95), (43.0, -22.0, 1.0),
        (-77.0, 61.0, 1.3), (-60.0, 68.0, 1.05), (-30.0, 68.0, 1.15),
        (10.0, 72.0, 1.2), (45.0, 70.0, 1.0), (78.0, 62.0, 1.25),
        (-86.0, -18.0, 1.15), (86.0, -15.0, 1.0), (-8.0, -64.0, 1.2),
    )
    for tree_index, (x, y, scale) in enumerate(tree_positions):
        add_preview_tree(rig, tree_index, x, y, scale, bark_mat, leaf_mat if tree_index % 3 else leaf_alt_mat)

    car_colors = (context_mats["facade_white"], context_mats["facade_dark"], context_mats["facade_warm"])
    for car_index, (x, y, yaw) in enumerate((
        (-58.0, street_y - 2.2, 0.0), (-24.0, street_y + 2.1, 0.0),
        (31.0, street_y - 2.0, 0.0), (66.0, street_y + 2.0, 0.0),
        (parking_x - 6.8, parking_y - 5.7, math.pi / 2),
        (parking_x + 0.1, parking_y - 5.7, math.pi / 2),
        (parking_x + 6.8, parking_y - 5.7, math.pi / 2),
    )):
        car = add_box(f"PreviewCar{car_index}", (3.9, 1.75, 1.25), (x, y, 0.68), car_colors[car_index % 3])
        car.rotation_euler.z = yaw
        rig.append(car)
        cabin = add_box(f"PreviewCarCabin{car_index}", (1.9, 1.55, 0.62), (x, y, 1.38), context_mats["glass"])
        cabin.rotation_euler.z = yaw
        rig.append(cabin)

    sun_data = bpy.data.lights.new("PreviewSun", type="SUN")
    sun_data.energy = 2.8
    sun_data.angle = math.radians(4.0)
    sun = bpy.data.objects.new("PreviewSun", sun_data)
    sun.rotation_euler = (math.radians(42), math.radians(-18), math.radians(-38))
    scene.collection.objects.link(sun)
    rig.append(sun)

    area_data = bpy.data.lights.new("PreviewFill", type="AREA")
    area_data.energy = 760.0
    area_data.shape = "DISK"
    area_data.size = footprint * 1.4
    area = bpy.data.objects.new("PreviewFill", area_data)
    area.location = (width * 0.8, -depth * 1.2, focus_height * 0.8)
    area.rotation_euler = (math.radians(38), 0, math.radians(32))
    scene.collection.objects.link(area)
    rig.append(area)

    cam_data = bpy.data.cameras.new("PreviewCamera")
    cam_data.lens = 48
    cam_data.clip_end = 1600.0
    cam = bpy.data.objects.new("PreviewCamera", cam_data)
    scene.collection.objects.link(cam)
    rig.append(cam)
    scene.camera = cam

    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.58, 0.67, 0.77, 1.0)
        bg.inputs[1].default_value = 0.58

    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        pass
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.compression = 18
    scene.render.film_transparent = False
    scene.render.resolution_percentage = 100
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1000
    if hasattr(scene, "eevee") and hasattr(scene.eevee, "taa_render_samples"):
        scene.eevee.taa_render_samples = 64

    dist = max(footprint * 2.15, focus_height * 1.95)
    context_dist = max(footprint * 4.2, focus_height * 3.5)
    views = (
        ("preview", (-dist * 0.72, -dist * 0.92, focus_height * 0.68), (0.0, 0.0, focus_height * 0.43), 43),
        ("street", (-width * 0.82, -(depth / 2 + 35.0), focus_height * 0.31), (0.0, -depth * 0.12, focus_height * 0.39), 46),
        ("aerial", (dist * 0.62, -dist * 0.78, focus_height + dist * 0.52), (0.0, 0.0, focus_height * 0.38), 49),
        ("context", (context_dist * 0.72, -context_dist * 0.85, focus_height + context_dist * 0.70),
         (0.0, 10.0, focus_height * 0.22), 52),
    )
    rendered: list[str] = []
    for view_name, location, target_tuple, lens in views:
        # Background masses make the drone views legible but can sit directly
        # between a low camera and the hero building. Street/studio views keep
        # roads, trees and cars while hiding only those distant massing blocks.
        context_visible = view_name in ("aerial", "context")
        for context_object in context_only:
            context_object.hide_render = not context_visible
        cam.location = location
        cam.data.lens = lens
        direction = Vector(target_tuple) - cam.location
        cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        filename = f"{family}_{view_name}.png"
        scene.render.filepath = str(output / filename)
        bpy.ops.render.render(write_still=True)
        rendered.append(filename)

    for obj in rig:
        if obj.name in bpy.data.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
    return engine, rendered


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def build_module(
    role: str,
    grammar: dict,
    mats: dict,
    variant_key: str = "default",
    interior_seed: int = 0,
) -> bpy.types.Object:
    if role == "podium":
        return build_podium(grammar, mats)
    if role == "floor":
        return build_floor_v3(grammar, mats, variant_key if variant_key != "default" else "typical_a", interior_seed)
    if role == "setback":
        return build_floor_v3(grammar, mats, "upper", interior_seed)
    if role == "crown":
        return build_floor_v3(grammar, mats, "crown", interior_seed)
    if role == "roof":
        return build_roof(grammar, mats)
    raise ValueError(f"unknown module role {role}")


def generate(grammar: dict, output: Path, *, floors_override: int | None, keep_blend: bool,
             thumbnail: bool, assembled: bool, ao: bool = True, ao_resolution: int = 512,
             ao_samples: int = 16, presentation_engine: str = "eevee",
             presentation_samples: int = 48) -> None:
    if grammar.get("schema_version") != SUPPORTED_SCHEMA_VERSION:
        raise SystemExit(
            f"grammar schema_version={grammar.get('schema_version')!r} unsupported "
            f"(generator expects {SUPPORTED_SCHEMA_VERSION}); re-run compiler.py"
        )

    configure_units()
    family = grammar["family_id"]
    dims = grammar["dimensions"]
    source = grammar["source"]
    output.mkdir(parents=True, exist_ok=True)

    texture_keys_used = sorted({
        spec.get("texture_key") for spec in grammar["materials"].values()
        if _texture_set(spec.get("texture_key"))
    })
    print(f"[blender_generate] textures: {texture_keys_used or 'none (flat colours)'}"
          f" from {TEXTURES_DIR}")

    module_specs = [
        ("podium", "default"),
        ("floor", "typical_a"),
        ("floor", "typical_b"),
        ("setback", "upper"),
        ("crown", "crown"),
        ("roof", "default"),
    ]
    height_key = {
        "podium": "podium_height_m", "floor": "floor_height_m",
        "setback": "setback_height_m", "crown": "floor_height_m", "roof": "roof_height_m",
    }

    manifest_modules = []
    floor_variants = {
        item["key"]: item for item in grammar.get("facade_graph", {}).get("floor_variants", [])
    }
    for role, variant_key in module_specs:
        reset_scene()
        mats = build_materials(grammar)
        module = build_module(role, grammar, mats, variant_key)
        ao_baked = bake_ao(module, ao_resolution, ao_samples) if ao else False
        suffix = role if variant_key == "default" else f"{role}_{variant_key}"
        glb_path = output / f"{family}_{suffix}.glb"
        export_objects(glb_path, [module])
        variant_spec = floor_variants.get(variant_key, {})
        manifest_modules.append({
            "role": role,
            "variant_key": variant_key,
            "lod": 0,
            "allowed_levels": variant_spec.get("allowed_levels") or [],
            "filename": glb_path.name,
            "module_family": family,
            "width_m": dims["width_m"],
            "depth_m": dims["depth_m"],
            "height_m": dims[height_key[role]],
            "floor_height_m": dims["floor_height_m"],
            "repeatable_z": role == "floor" and variant_key.startswith("typical_"),
            "triangle_count": triangle_count(module),
            "material_count": len(module.data.materials),
            "texture_keys": texture_keys_used,
            "ao_baked": ao_baked,
            "size_bytes": glb_path.stat().st_size,
        })
        print(f"[blender_generate] exported {glb_path.name} ({manifest_modules[-1]['triangle_count']} tris, "
              f"{glb_path.stat().st_size // 1024} KB, ao={ao_baked})")

    # ---- assembled preview -------------------------------------------------
    floors = floors_override or dims["default_floors"]
    use_setback = bool(grammar["massing"].get("has_setback")) and floors >= 5
    use_crown = floors >= 3
    standard_floors = max(0, floors - 1 - (1 if use_setback else 0) - (1 if use_crown else 0))

    assembled_meta = None
    engine_used = None
    rendered_views: list[str] = []
    if assembled:
        reset_scene()
        mats = build_materials(grammar)
        stack: list[bpy.types.Object] = []
        z = 0.0

        stack_meta: list[dict] = []

        def place(role: str, level: int, variant_key: str = "default") -> None:
            nonlocal z
            module = build_module(role, grammar, mats, variant_key, interior_seed=level)
            module.name = f"ASM_{role}_{variant_key}_{level:02d}"
            module.location.z = z
            bpy.ops.object.select_all(action="DESELECT")
            module.select_set(True)
            bpy.context.view_layer.objects.active = module
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            stack.append(module)
            module_height = dims[height_key[role]]
            stack_meta.append({"role": role, "variant_key": variant_key, "level": level, "z_m": round(z, 3), "height_m": module_height})
            z += module_height

        place("podium", 0)
        for level in range(1, standard_floors + 1):
            place("floor", level, "typical_a" if level % 2 else "typical_b")
        if use_setback:
            place("setback", floors - (2 if use_crown else 1), "upper")
        if use_crown:
            place("crown", floors - 1, "crown")
        place("roof", floors)

        assembled_path = output / f"{family}_assembled.glb"
        export_objects(assembled_path, stack)
        assembled_meta = {
            "filename": assembled_path.name,
            "floors": floors,
            "uses_setback": use_setback,
            "uses_crown": use_crown,
            "height_m": round(z, 3),
            "triangle_count": sum(triangle_count(obj) for obj in stack),
            "stack": stack_meta,
        }
        print(f"[blender_generate] exported {assembled_path.name} (height {z:.2f} m, {floors} floors)")

        if thumbnail:
            try:
                engine_used, rendered_views = render_presentation_views(
                    output, family, z, dims["width_m"], dims["depth_m"],
                    preferred_engine=presentation_engine, samples=presentation_samples,
                )
                print(f"[blender_generate] rendered {', '.join(rendered_views)} via {engine_used}")
            except Exception as exc:  # pragma: no cover - render backends vary by machine
                print(f"[blender_generate] WARNING: presentation renders failed: {exc}")

        if keep_blend:
            blend_path = output / f"{family}.blend"
            bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
            print(f"[blender_generate] saved {blend_path.name}")

    manifest = {
        "manifest_schema": 3,
        "grammar_schema_version": grammar["schema_version"],
        "generator": {
            "name": "archetype_compiler/blender_generate.py",
            "version": GENERATOR_VERSION,
            "blender_version": bpy.app.version_string,
            "render_engine": engine_used,
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "family": family,
        "archetype_id": source["archetype_id"],
        "archetype_label": source.get("archetype_label"),
        "variant_id": source.get("variant_id"),
        "generation_archetype_id": source.get("generation_archetype_id"),
        "aesthetic_category_id": source.get("aesthetic_category_id"),
        "development_type": source.get("development_type"),
        "reuse_keys": source.get("reuse_keys", []),
        "generation_tags": source.get("generation_tags", []),
        "coordinate_contract": {
            "units": "metres",
            "blender_up": "+Z",
            "gltf_up": "+Y (export_yup)",
            "origin": "bottom centre",
            "front_facade": "-Y in Blender, +Z in glTF",
            "transforms": "applied",
        },
        "textures": {
            "keys_used": texture_keys_used,
            "uv_tile_metres": UV_TILE_METRES,
            "ao_requested": ao,
            "uv_layers": {"UVMap": "box projection, tiled materials", "AOMap": "smart project, baked AO"},
        },
        "dimensions": dims,
        "min_floors": dims["min_floors"],
        "max_floors": dims["max_floors"],
        "default_floors": dims["default_floors"],
        "modules": manifest_modules,
        "assembled": assembled_meta,
        "thumbnail": f"{family}_preview.png" if (assembled and thumbnail) else None,
        "renders": rendered_views,
    }
    manifest_path = output / f"{family}_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[blender_generate] wrote {manifest_path.name}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="blender_generate.py")
    parser.add_argument("--grammar", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--floors", type=int, default=None, help="assembled preview floor count override")
    parser.add_argument("--keep-blend", action="store_true")
    parser.add_argument("--no-thumbnail", action="store_true")
    parser.add_argument("--no-assembled", action="store_true")
    parser.add_argument("--textures", type=Path, default=Path(__file__).resolve().parent / "textures",
                        help="texture library root (generate_textures.py output)")
    parser.add_argument("--no-ao", action="store_true", help="skip the Cycles AO bake (fast runs)")
    parser.add_argument("--ao-resolution", type=int, default=512)
    parser.add_argument("--ao-samples", type=int, default=16)
    parser.add_argument("--presentation-engine", choices=("eevee", "cycles"), default="eevee",
                        help="render engine for review images (GLB output is unchanged)")
    parser.add_argument("--presentation-samples", type=int, default=48,
                        help="Cycles samples for review images")
    return parser.parse_args(argv)


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    args = parse_args(argv)
    global TEXTURES_DIR
    TEXTURES_DIR = args.textures.resolve() if args.textures else None
    grammar = json.loads(args.grammar.resolve().read_text(encoding="utf-8"))
    generate(
        grammar,
        # Blender resolves relative paths against its own notion of cwd/blend dir,
        # so everything downstream must see absolute paths.
        args.output.resolve(),
        floors_override=args.floors,
        keep_blend=args.keep_blend,
        thumbnail=not args.no_thumbnail,
        assembled=not args.no_assembled,
        ao=not args.no_ao,
        ao_resolution=args.ao_resolution,
        ao_samples=args.ao_samples,
        presentation_engine=args.presentation_engine,
        presentation_samples=args.presentation_samples,
    )


if __name__ == "__main__":
    main()
