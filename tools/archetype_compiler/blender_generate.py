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

GENERATOR_VERSION = "0.10.0"
SUPPORTED_SCHEMA_VERSION = 3

# Set from CLI in main(); make_material reads them so build_materials stays a
# pure function of the grammar.
TEXTURES_DIR: Path | None = None
DEFAULT_TEXTURES_DIR = Path(__file__).resolve().parent / "textures"
FACADE_SHEET: dict | None = None
FACADE_SHEET_DETAIL = "hero"
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
            alpha.default_value = 0.42
        transmission = bsdf.inputs.get("Transmission Weight") or bsdf.inputs.get("Transmission")
        if transmission:
            transmission.default_value = 0.22
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
            "heritage_portland_stone": 0.91,
            "welsh_slate": 0.74,
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
            "heritage_portland_stone": 0.05,
            "welsh_slate": 0.06,
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


def make_facade_sheet_material(
    name: str,
    albedo: Path,
    roughness: Path | None,
    emissive: Path | None,
) -> bpy.types.Material:
    """Photo-elevation material used only on the thin street-facing skin.

    The source image contains fine windows, reveals and material joints.  A
    restrained derived roughness and warm-window mask preserve material/readout
    without analytically re-lighting every shadow already present in the photo.
    """
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (460, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (120, 0)
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = 0.72
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.26
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    uv_node = nodes.new("ShaderNodeUVMap")
    uv_node.uv_map = "UVMap"
    uv_node.location = (-760, 0)
    albedo_node = nodes.new("ShaderNodeTexImage")
    albedo_node.name = albedo_node.label = "SHEET_Albedo"
    albedo_node.image = _load_image(albedo, "sRGB")
    albedo_node.extension = "REPEAT"
    albedo_node.location = (-500, 220)
    links.new(uv_node.outputs["UV"], albedo_node.inputs["Vector"])
    links.new(albedo_node.outputs["Color"], bsdf.inputs["Base Color"])

    if roughness and roughness.exists():
        roughness_node = nodes.new("ShaderNodeTexImage")
        roughness_node.name = roughness_node.label = "SHEET_Roughness"
        roughness_node.image = _load_image(roughness, "Non-Color")
        roughness_node.extension = "REPEAT"
        roughness_node.location = (-500, -40)
        links.new(uv_node.outputs["UV"], roughness_node.inputs["Vector"])
        links.new(roughness_node.outputs["Color"], bsdf.inputs["Roughness"])

    if emissive and emissive.exists():
        emissive_node = nodes.new("ShaderNodeTexImage")
        emissive_node.name = emissive_node.label = "SHEET_EmissiveMask"
        emissive_node.image = _load_image(emissive, "Non-Color")
        emissive_node.extension = "REPEAT"
        emissive_node.location = (-500, -300)
        links.new(uv_node.outputs["UV"], emissive_node.inputs["Vector"])
        emission = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
        if emission:
            links.new(emissive_node.outputs["Color"], emission)
        if bsdf.inputs.get("Emission Strength"):
            # The mask is intentionally only a dusk hint. Gemini elevations
            # contain naturally warm timber/stone pixels that can otherwise
            # be mistaken for lit glass and wash the whole facade pale.
            bsdf.inputs["Emission Strength"].default_value = 0.035

    mat.diffuse_color = (0.46, 0.46, 0.46, 1.0)
    mat["facade_sheet"] = True
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
        "signature_warm": make_material("MAT_Signature_WarmTimber", {
            "base_color": "#9b5f32", "roughness": 0.58, "metallic": 0.0,
        }),
        "signature_dark": make_material("MAT_Signature_CharredLarch", {
            "base_color": "#252525", "roughness": 0.72, "metallic": 0.0,
        }),
        "signature_stone": make_material("MAT_Signature_CutStone", {
            "base_color": "#8c8980", "roughness": 0.82, "metallic": 0.0,
        }),
        "signature_metal": make_material("MAT_Signature_BlackMetal", {
            "base_color": "#17191b", "roughness": 0.34, "metallic": 0.72,
        }),
    }
    room_count = 4 if grammar.get("facade", {}).get("system") == "heritage_stone" else 8
    result["interior_cells"] = [make_interior_atlas_material(index) for index in range(room_count)]
    if FACADE_SHEET:
        root = FACADE_SHEET["dir"]
        for role, band in FACADE_SHEET["manifest"].get("bands", {}).items():
            if role not in ("floor", "floor_alt", "crown", "podium"):
                continue
            result[f"sheet_{role}"] = make_facade_sheet_material(
                f"MAT_Sheet_{role.capitalize()}",
                root / band["albedo"],
                root / band["roughness"] if band.get("roughness") else None,
                root / band["emissive"] if band.get("emissive") else None,
            )
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


def apply_facade_sheet_uv(obj: bpy.types.Object, span_m: float, module_height_m: float) -> None:
    """Map sheet-material faces in real units after all parts have been joined.

    The hero profile uses the sheet on its principal elevation.  The lighter
    city profile also wraps the repeatable band around side/rear skins, which
    gives orbit views atlas-level detail without thousands of extra window
    meshes. U repeats at the strip span detected from the image itself; V
    covers the complete modular storey.
    """
    mesh = obj.data
    sheet_indices = {
        index for index, material in enumerate(mesh.materials)
        if material and material.name.startswith("MAT_Sheet_")
    }
    if not sheet_indices:
        return
    uv_layer = mesh.uv_layers.get("UVMap") or mesh.uv_layers.new(name="UVMap")
    mesh.uv_layers.active = uv_layer
    span_m = max(float(span_m), 0.25)
    module_height_m = max(float(module_height_m), 0.25)
    for polygon in mesh.polygons:
        if polygon.material_index not in sheet_indices:
            continue
        x_dominant = abs(polygon.normal.x) > abs(polygon.normal.y)
        for loop_index in polygon.loop_indices:
            coordinate = mesh.vertices[mesh.loops[loop_index].vertex_index].co
            uv_layer.data[loop_index].uv = (
                (coordinate.y if x_dominant else coordinate.x) / span_m + 0.5,
                coordinate.z / module_height_m,
            )


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


def add_heritage_sash_front(
    parts: list,
    prefix: str,
    x: float,
    face_y: float,
    centre_z: float,
    opening_w: float,
    opening_h: float,
    mats: dict,
    *,
    pediment: str = "lintel",
    interior_seed: int = 0,
    overlay: bool = False,
) -> None:
    """Deep multi-pane sash plus an independent carved-stone surround.

    The glass, frame and architrave sit on separate depth planes, so grazing
    light produces the same hierarchy that makes compact baked heritage assets
    convincing without requiring sculpted ornament on every stone.
    """
    atlas_cells = mats.get("interior_cells") or []
    room_mat = atlas_cells[interior_seed % len(atlas_cells)] if atlas_cells else mats["interior_warm"]
    room_y = face_y - 0.015 if overlay else face_y + 0.28
    glass_y = face_y - 0.070 if overlay else face_y + 0.20
    frame_y = face_y - 0.115 if overlay else face_y + 0.14
    parts.append(add_box(f"{prefix}_Room", (opening_w + 0.12, 0.055, opening_h + 0.12),
                         (x, room_y, centre_z), room_mat))
    parts.append(add_box(f"{prefix}_Glass", (opening_w, 0.045, opening_h),
                         (x, glass_y, centre_z), mats["glass"]))
    add_frame_bars(
        parts, f"{prefix}_Sash", "front", (x, frame_y, centre_z),
        opening_w, opening_h, 0.095, mats["accent"], profile=0.052, mullions="double",
    )
    # Sash meeting rail and small glazing bars establish human scale.
    parts.append(add_box(f"{prefix}_MeetingRail", (opening_w, 0.105, 0.075),
                         (x, frame_y - 0.01, centre_z), mats["accent"]))
    for rail_index, offset in enumerate((-opening_h * 0.25, opening_h * 0.25)):
        parts.append(add_box(f"{prefix}_GlazingRail{rail_index}", (opening_w, 0.085, 0.035),
                             (x, frame_y - 0.015, centre_z + offset), mats["accent"]))

    trim_depth = 0.22
    trim_y = face_y - trim_depth / 2 + 0.025
    jamb = 0.16
    parts.extend([
        add_box(f"{prefix}_ArchitraveL", (jamb, trim_depth, opening_h + 0.38),
                (x - opening_w / 2 - jamb / 2 - 0.055, trim_y, centre_z + 0.03), mats["secondary"]),
        add_box(f"{prefix}_ArchitraveR", (jamb, trim_depth, opening_h + 0.38),
                (x + opening_w / 2 + jamb / 2 + 0.055, trim_y, centre_z + 0.03), mats["secondary"]),
        add_box(f"{prefix}_Sill", (opening_w + 0.42, trim_depth + 0.08, 0.13),
                (x, trim_y - 0.035, centre_z - opening_h / 2 - 0.10), mats["secondary"]),
    ])
    top_z = centre_z + opening_h / 2
    if pediment == "triangle":
        half_w = opening_w / 2 + 0.32
        y0, y1 = face_y - trim_depth - 0.02, face_y + 0.025
        verts = [
            (x - half_w, y0, top_z + 0.08), (x + half_w, y0, top_z + 0.08), (x, y0, top_z + 0.48),
            (x - half_w, y1, top_z + 0.08), (x + half_w, y1, top_z + 0.08), (x, y1, top_z + 0.48),
        ]
        faces = [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)]
        parts.append(add_prism(f"{prefix}_TriangularPediment", verts, faces, mats["secondary"]))
        parts.append(add_box(f"{prefix}_PedimentBed", (opening_w + 0.72, trim_depth + 0.10, 0.11),
                             (x, trim_y - 0.04, top_z + 0.05), mats["secondary"]))
    elif pediment == "segmental":
        half_w, rise, band = opening_w / 2 + 0.24, 0.30, 0.11
        y0, y1 = face_y - trim_depth - 0.02, face_y + 0.025
        segments = 12
        verts: list[tuple[float, float, float]] = []
        for y in (y0, y1):
            for radius_scale, z_offset in ((1.0, 0.08), (0.80, 0.05)):
                for arc_index in range(segments + 1):
                    theta = math.pi * arc_index / segments
                    verts.append((
                        x + half_w * radius_scale * math.cos(theta), y,
                        top_z + z_offset + rise * radius_scale * math.sin(theta),
                    ))
        stride = segments + 1
        outer_front, inner_front, outer_back, inner_back = 0, stride, stride * 2, stride * 3
        faces: list[tuple[int, ...]] = []
        for arc_index in range(segments):
            nxt = arc_index + 1
            faces.extend([
                (outer_front + arc_index, outer_front + nxt, inner_front + nxt, inner_front + arc_index),
                (inner_back + arc_index, inner_back + nxt, outer_back + nxt, outer_back + arc_index),
                (outer_front + arc_index, outer_back + arc_index, outer_back + nxt, outer_front + nxt),
                (inner_front + arc_index, inner_front + nxt, inner_back + nxt, inner_back + arc_index),
            ])
        parts.append(add_prism(f"{prefix}_SegmentalPediment", verts, faces, mats["secondary"]))
    else:
        parts.append(add_box(f"{prefix}_Lintel", (opening_w + 0.46, trim_depth + 0.06, 0.18),
                             (x, trim_y - 0.025, top_z + 0.12), mats["secondary"]))


def add_heritage_quoins(parts: list, prefix: str, w: float, face_y: float, h: float, mats: dict) -> None:
    course_h = 0.46
    count = max(3, int(h / course_h))
    for row in range(count):
        z = (row + 0.5) * h / count
        block_w = 0.54 if row % 2 == 0 else 0.42
        for side, sign in (("L", -1), ("R", 1)):
            parts.append(add_box(
                f"{prefix}_{side}_{row:02d}", (block_w, 0.28, h / count - 0.035),
                (sign * (w / 2 - block_w / 2 + 0.025), face_y - 0.09, z), mats["secondary"],
            ))


def build_heritage_podium(grammar: dict, mats: dict) -> bpy.types.Object:
    dims, facade = grammar["dimensions"], grammar["facade"]
    w, d, h = dims["width_m"], dims["depth_m"], dims["podium_height_m"]
    face_y = -d / 2
    parts: list = [
        add_box("HeritagePodium_Core", (w, d, h), (0, 0, h / 2), mats["primary"]),
        add_box("HeritagePodium_Plinth", (w + 0.24, d + 0.20, 0.52), (0, 0, 0.26), mats["secondary"]),
    ]
    # Rusticated horizontal courses remain modeled at the base where parallax
    # matters most; the AI-derived normal map carries the finer ashlar joints.
    for course in range(1, 8):
        z = 0.52 + course * (h - 0.58) / 8
        parts.append(add_box(f"Podium_Rustication_{course:02d}", (w + 0.08, 0.075, 0.055),
                             (0, face_y - 0.035, z), mats["secondary"]))

    bay_count = max(5, int(facade.get("front_bay_count", 8)))
    bay = w / bay_count
    for index in range(bay_count):
        x = -w / 2 + bay * (index + 0.5)
        if abs(x) < bay * 0.82:
            continue
        add_heritage_sash_front(
            parts, f"Podium_Window_{index:02d}", x, face_y - 0.03, 2.08,
            min(1.42, bay * 0.46), min(2.45, h * 0.55), mats,
            pediment="segmental" if index in (1, bay_count - 2) else "lintel",
            interior_seed=index, overlay=True,
        )

    # A three-layer portal, broad steps and paired lamps establish a legible
    # address instead of the generic full-width storefront used by modern kits.
    portal_w = min(4.4, w * 0.22)
    spring_z = min(2.85, h * 0.60)
    pier_w = 0.44
    parts.extend([
        add_box("GrandPortal_Shadow", (portal_w - 0.42, 0.08, spring_z + portal_w * 0.32),
                (0, face_y - 0.03, (spring_z + portal_w * 0.32) / 2), mats["interior"]),
        add_box("GrandPortal_DoorL", (portal_w * 0.34, 0.10, 2.55),
                (-portal_w * 0.19, face_y - 0.16, 1.60), mats["accent"]),
        add_box("GrandPortal_DoorR", (portal_w * 0.34, 0.10, 2.55),
                (portal_w * 0.19, face_y - 0.16, 1.60), mats["accent"]),
        add_box("GrandPortal_PierL", (pier_w, 0.52, spring_z),
                (-(portal_w / 2 + pier_w / 2), face_y - 0.16, spring_z / 2), mats["secondary"]),
        add_box("GrandPortal_PierR", (pier_w, 0.52, spring_z),
                ((portal_w / 2 + pier_w / 2), face_y - 0.16, spring_z / 2), mats["secondary"]),
    ])
    parts.append(add_arch_ring("GrandPortal_Arch", 0, face_y - 0.16, spring_z, portal_w / 2,
                               pier_w, 0.52, mats["secondary"], segments=24))
    portico_y = face_y - 0.52
    column_h = min(3.35, h * 0.72)
    for column_index, x in enumerate((-portal_w * 0.62, portal_w * 0.62)):
        parts.append(add_cylinder(f"GrandPortico_Column{column_index}", 0.23, column_h,
                                  (x, portico_y, column_h / 2 + 0.28), mats["secondary"], 20))
        parts.append(add_cylinder(f"GrandPortico_Base{column_index}", 0.32, 0.16,
                                  (x, portico_y, 0.36), mats["secondary"], 20))
        parts.append(add_cylinder(f"GrandPortico_Capital{column_index}", 0.34, 0.18,
                                  (x, portico_y, column_h + 0.25), mats["secondary"], 20))
    entablature_z = min(h - 0.72, column_h + 0.42)
    pediment_half_w = portal_w * 0.82
    parts.append(add_box("GrandPortico_Entablature", (pediment_half_w * 2 + 0.30, 0.82, 0.26),
                         (0, portico_y, entablature_z), mats["secondary"]))
    y0, y1 = portico_y - 0.43, portico_y + 0.43
    pediment_verts = [
        (-pediment_half_w, y0, entablature_z + 0.14), (pediment_half_w, y0, entablature_z + 0.14),
        (0, y0, min(h + 0.58, entablature_z + 1.22)),
        (-pediment_half_w, y1, entablature_z + 0.14), (pediment_half_w, y1, entablature_z + 0.14),
        (0, y1, min(h + 0.58, entablature_z + 1.22)),
    ]
    parts.append(add_prism("GrandPortico_Pediment", pediment_verts,
                           [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)],
                           mats["secondary"]))
    for step in range(3):
        parts.append(add_box(f"GrandPortal_Step{step}", (portal_w + 1.2 - step * 0.28, 0.48, 0.16),
                             (0, face_y - 0.55 - step * 0.35, 0.08 + step * 0.16), mats["concrete"]))
    for lamp_index, sign in enumerate((-1, 1)):
        parts.append(add_box(f"PortalLampStem{lamp_index}", (0.055, 0.08, 0.52),
                             (sign * (portal_w / 2 + 0.78), face_y - 0.22, 2.15), mats["accent"]))
        parts.append(add_box(f"PortalLampBox{lamp_index}", (0.22, 0.18, 0.34),
                             (sign * (portal_w / 2 + 0.78), face_y - 0.24, 2.55), mats["interior_warm"]))

    # Low stone balustrade integrates the building with its footprint and gives
    # the base the same fine-grained silhouette density as the roof.
    rail_y, rail_h = face_y - 0.48, 0.92
    opening_half = portal_w * 0.86
    left_span = w / 2 - opening_half
    for rail_index, sign in enumerate((-1, 1)):
        rail_x = sign * (opening_half + left_span / 2)
        parts.append(add_box(f"Podium_BalustradeTop{rail_index}", (left_span, 0.20, 0.13),
                             (rail_x, rail_y, rail_h), mats["secondary"]))
        parts.append(add_box(f"Podium_BalustradeBase{rail_index}", (left_span, 0.24, 0.15),
                             (rail_x, rail_y, 0.28), mats["secondary"]))
        post_count = max(4, round(left_span / 1.05))
        for post_index in range(post_count + 1):
            x = sign * opening_half + sign * left_span * post_index / post_count
            parts.append(add_box(f"Podium_Baluster{rail_index}_{post_index:02d}", (0.13, 0.16, 0.52),
                                 (x, rail_y, 0.59), mats["secondary"]))

    add_heritage_quoins(parts, "Podium_Quoin", w, face_y, h, mats)
    for layer, (extra_w, depth, band_h, z) in enumerate((
        (0.16, 0.28, 0.18, h - 0.47), (0.34, 0.38, 0.22, h - 0.24), (0.56, 0.48, 0.20, h - 0.06),
    )):
        parts.append(add_box(f"Podium_Cornice_{layer}", (w + extra_w, depth, band_h),
                             (0, face_y - depth / 2 + 0.04, z), mats["secondary"]))

    side_count, side_bay = _bays(d, facade["bay_width_m"])
    add_window_row(parts, "HeritagePodium", w, "rear", d / 2, 0.5, min(1.4, bay * 0.46), 2.1, 0.55,
                   bay_count, mats)
    add_window_row(parts, "HeritagePodium", d, "left", w / 2, 0.5, min(1.35, side_bay * 0.46), 2.1, 0.55,
                   side_count, mats)
    add_window_row(parts, "HeritagePodium", d, "right", w / 2, 0.5, min(1.35, side_bay * 0.46), 2.1, 0.55,
                   side_count, mats)
    return join_as("MOD_Podium", parts)


# ---------------------------------------------------------------------------
# Module builders — each returns ONE joined object with base at z=0
# ---------------------------------------------------------------------------

def build_podium(grammar: dict, mats: dict) -> bpy.types.Object:
    dims, facade, massing = grammar["dimensions"], grammar["facade"], grammar["massing"]
    if facade.get("system") == "heritage_stone":
        return build_heritage_podium(grammar, mats)
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


def _add_heritage_balcony(
    parts: list,
    prefix: str,
    width: float,
    facade_y: float,
    mats: dict,
) -> None:
    """Continuous wrought-iron balcony for Parisian/European stone fronts.

    The rail is modeled as individual pickets so it reads at street distance;
    the stone slab and regularly spaced corbels provide the heavier shadow line
    visible in the catalog references.
    """
    width = max(2.4, width - 0.64)
    depth = 0.92
    centre_y = facade_y - depth / 2
    front_y = facade_y - depth
    parts.append(add_box(f"{prefix}_Slab", (width, depth, 0.18), (0, centre_y, 0.20), mats["secondary"]))
    parts.append(add_box(f"{prefix}_SlabShadow", (width - 0.12, depth - 0.08, 0.045),
                         (0, centre_y, 0.095), mats["accent"]))

    corbel_count = max(4, round(width / 2.2))
    for index in range(corbel_count + 1):
        x = -width / 2 + width * index / corbel_count
        parts.append(add_box(f"{prefix}_Corbel_{index:02d}", (0.22, 0.48, 0.42),
                             (x, facade_y - 0.20, 0.21), mats["secondary"]))

    bottom_z, top_z = 0.43, 1.31
    parts.append(add_box(f"{prefix}_BottomRail", (width, 0.055, 0.055),
                         (0, front_y, bottom_z), mats["accent"]))
    parts.append(add_box(f"{prefix}_TopRail", (width + 0.10, 0.075, 0.075),
                         (0, front_y, top_z), mats["accent"]))
    picket_count = max(12, round(width / 0.34))
    for index in range(picket_count + 1):
        x = -width / 2 + width * index / picket_count
        parts.append(add_box(f"{prefix}_Picket_{index:03d}", (0.035, 0.045, top_z - bottom_z),
                             (x, front_y, (top_z + bottom_z) / 2), mats["accent"]))
    for side, sign in (("L", -1), ("R", 1)):
        x = sign * width / 2
        parts.append(add_box(f"{prefix}_SideTop{side}", (0.055, depth, 0.055),
                             (x, centre_y, top_z), mats["accent"]))
        parts.append(add_box(f"{prefix}_SidePost{side}", (0.055, 0.055, top_z - bottom_z),
                             (x, facade_y - 0.04, (top_z + bottom_z) / 2), mats["accent"]))


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


def build_heritage_floor(
    grammar: dict,
    mats: dict,
    variant_key: str,
    interior_seed: int,
) -> bpy.types.Object:
    """Architecturally specific London stone body/crown module.

    It retains the Lego stack contract, but each repeatable floor carries real
    openings, deep sash assemblies, projecting pavilions, quoins, and a wrapped
    string course. The crown swaps window ornament for a complete entablature.
    """
    dims, facade = grammar["dimensions"], grammar["facade"]
    w, d = dims["width_m"], dims["depth_m"]
    h = dims["floor_height_m"]
    crown = variant_key == "crown"
    upper = variant_key == "upper"
    face_y = -d / 2
    reveal_depth = max(0.32, float(facade.get("window_recess_m", 0.38)))
    room_depth = 0.38
    core_depth = max(0.5, d - reveal_depth - room_depth)
    parts: list = [
        add_box("HeritageFloor_Core", (w, core_depth, h),
                (0, (reveal_depth + room_depth) / 2, h / 2), mats["primary"]),
        add_box("HeritageFloor_Slab", (w + 0.12, d + 0.08, 0.16), (0, 0, 0.08), mats["secondary"]),
    ]

    bay_count = max(5, int(facade.get("front_bay_count", 8)))
    bay = w / bay_count
    opening_w = min(bay * 0.47, bay - 0.78)
    opening_h = min(h * (0.58 if crown else 0.66), h - 0.72)
    sill = 0.74 if crown else (0.62 if not upper else 0.72)
    centre_z = sill + opening_h / 2
    centre_indices = {bay_count // 2 - 1, bay_count // 2}

    for index in range(bay_count):
        x = -w / 2 + bay * (index + 0.5)
        corner_pavilion = index in (0, bay_count - 1)
        centre_pavilion = index in centre_indices
        projection = 0.26 if centre_pavilion else (0.16 if corner_pavilion else 0.0)
        local_face = face_y - projection
        wall_depth = 0.24
        left_edge = x - bay / 2
        pier = max(0.24, (bay - opening_w) / 2)
        panel_mat = mats["secondary"] if crown and index % 2 else mats["primary"]
        parts.extend([
            add_box(f"Heritage_{index:02d}_SillPanel", (bay + 0.01, wall_depth, sill),
                    (x, local_face + wall_depth / 2, sill / 2), panel_mat),
            add_box(f"Heritage_{index:02d}_HeadPanel", (bay + 0.01, wall_depth, h - sill - opening_h),
                    (x, local_face + wall_depth / 2, sill + opening_h + (h - sill - opening_h) / 2), panel_mat),
            add_box(f"Heritage_{index:02d}_PierL", (pier + 0.01, wall_depth, opening_h),
                    (left_edge + pier / 2, local_face + wall_depth / 2, centre_z), panel_mat),
            add_box(f"Heritage_{index:02d}_PierR", (pier + 0.01, wall_depth, opening_h),
                    (left_edge + bay - pier / 2, local_face + wall_depth / 2, centre_z), panel_mat),
        ])
        # Stone-lined returns make the reveal physically legible around the
        # glazing instead of relying on a dark decal.
        return_y = local_face + reveal_depth * 0.62
        return_d = reveal_depth * 0.72
        parts.extend([
            add_box(f"Heritage_{index:02d}_RevealL", (0.07, return_d, opening_h),
                    (x - opening_w / 2, return_y, centre_z), mats["secondary"]),
            add_box(f"Heritage_{index:02d}_RevealR", (0.07, return_d, opening_h),
                    (x + opening_w / 2, return_y, centre_z), mats["secondary"]),
            add_box(f"Heritage_{index:02d}_RevealHead", (opening_w, return_d, 0.07),
                    (x, return_y, centre_z + opening_h / 2), mats["secondary"]),
        ])
        if centre_pavilion:
            pediment = "triangle"
        elif (index + interior_seed) % 3 == 0 and not crown:
            pediment = "segmental"
        else:
            pediment = "lintel"
        add_heritage_sash_front(
            parts, f"Heritage_{index:02d}", x, local_face, centre_z, opening_w, opening_h, mats,
            pediment=pediment, interior_seed=index * 3 + interior_seed,
        )

        # Pavilion pilasters extend the projection to the full storey and keep
        # vertically stacked feature bays aligned when modules repeat.
        if centre_pavilion or corner_pavilion:
            pilaster_x = x + (-1 if index < bay_count / 2 else 1) * (bay / 2 - 0.12)
            parts.append(add_box(f"Heritage_{index:02d}_Pilaster", (0.24, 0.34 + projection, h - 0.18),
                                 (pilaster_x, local_face - 0.07, h / 2), mats["secondary"]))

    add_heritage_quoins(parts, "HeritageFloor_Quoin", w, face_y, h, mats)

    # Mixed-use European mansion blocks commonly carry continuous iron
    # balconies above the retail base. Keep the Kinnaird mansion variant clean,
    # while honoring catalog archetypes that explicitly compile projecting
    # balconies. Alternating/crown modules create a believable vertical rhythm.
    if (
        grammar.get("massing", {}).get("has_podium_retail")
        and facade.get("balcony_mode") == "projecting"
        and variant_key in ("typical_b", "upper", "crown")
    ):
        _add_heritage_balcony(parts, f"HeritageBalcony_{variant_key}", w, face_y - 0.10, mats)

    # Wrapped string courses keep the four-sided aerial silhouette coherent.
    for band_index, (z, band_h, extra) in enumerate(((0.13, 0.16, 0.12), (h - 0.11, 0.18, 0.20))):
        parts.extend([
            add_box(f"HeritageBand{band_index}_Front", (w + extra, 0.24, band_h),
                    (0, face_y - 0.08, z), mats["secondary"]),
            add_box(f"HeritageBand{band_index}_Rear", (w + extra, 0.24, band_h),
                    (0, d / 2 + 0.08, z), mats["secondary"]),
            add_box(f"HeritageBand{band_index}_Left", (0.24, d, band_h),
                    (-w / 2 - 0.08, 0, z), mats["secondary"]),
            add_box(f"HeritageBand{band_index}_Right", (0.24, d, band_h),
                    (w / 2 + 0.08, 0, z), mats["secondary"]),
        ])

    side_count, side_bay = _bays(d, facade["bay_width_m"])
    add_window_row(parts, "HeritageFloor", w, "rear", d / 2, 0.0, opening_w * 0.88, opening_h * 0.92,
                   sill, bay_count, mats, interior_seed=interior_seed)
    add_window_row(parts, "HeritageFloor", d * 0.92, "left", w / 2, 0.0,
                   min(side_bay * 0.46, opening_w), opening_h * 0.92, sill, side_count, mats,
                   interior_seed=interior_seed)
    add_window_row(parts, "HeritageFloor", d * 0.92, "right", w / 2, 0.0,
                   min(side_bay * 0.46, opening_w), opening_h * 0.92, sill, side_count, mats,
                   interior_seed=interior_seed + 2)
    side_span = d * 0.92
    side_window_w = min(side_bay * 0.46, opening_w)
    side_window_h = opening_h * 0.92
    side_z = sill + side_window_h / 2
    for side_name, sign in (("Left", -1), ("Right", 1)):
        trim_x = sign * (w / 2 + 0.13)
        for index in range(side_count):
            y = -side_span / 2 + side_span * (index + 0.5) / side_count
            parts.extend([
                add_box(f"HeritageSide{side_name}_{index:02d}_JambA", (0.20, 0.15, side_window_h + 0.34),
                        (trim_x, y - side_window_w / 2 - 0.09, side_z + 0.02), mats["secondary"]),
                add_box(f"HeritageSide{side_name}_{index:02d}_JambB", (0.20, 0.15, side_window_h + 0.34),
                        (trim_x, y + side_window_w / 2 + 0.09, side_z + 0.02), mats["secondary"]),
                add_box(f"HeritageSide{side_name}_{index:02d}_Head", (0.20, side_window_w + 0.42, 0.17),
                        (trim_x, y, side_z + side_window_h / 2 + 0.12), mats["secondary"]),
                add_box(f"HeritageSide{side_name}_{index:02d}_Sill", (0.22, side_window_w + 0.42, 0.12),
                        (sign * (w / 2 + 0.15), y, side_z - side_window_h / 2 - 0.09), mats["secondary"]),
            ])

    if crown:
        # Full classical entablature: three stepped bands, a row of dentils,
        # modillion blocks, and an open balustrade silhouetted against the roof.
        for layer, (extra_w, depth, band_h, z) in enumerate((
            (0.22, 0.34, 0.18, h - 0.72), (0.40, 0.46, 0.24, h - 0.44),
            (0.56, 0.58, 0.24, h - 0.13),
        )):
            parts.append(add_box(f"Crown_Entablature_{layer}", (w + extra_w, depth, band_h),
                                 (0, face_y - depth / 2 + 0.06, z), mats["secondary"]))
        dentil_count = max(12, bay_count * 4)
        for index in range(dentil_count):
            x = -w / 2 + w * (index + 0.5) / dentil_count
            parts.append(add_box(f"Crown_Dentil_{index:02d}", (w / dentil_count * 0.52, 0.42, 0.18),
                                 (x, face_y - 0.22, h - 0.82), mats["secondary"]))
        for index in range(bay_count + 1):
            x = -w / 2 + w * index / bay_count
            parts.append(add_box(f"Crown_Modillion_{index:02d}", (0.28, 0.62, 0.20),
                                 (x, face_y - 0.31, h - 0.58), mats["secondary"]))
        rail_z = h - 0.01
        parts.append(add_box("Crown_BalustradeRail", (w + 0.36, 0.19, 0.13),
                             (0, face_y - 0.08, rail_z), mats["secondary"]))
        for index in range(bay_count * 2 + 1):
            x = -w / 2 + w * index / (bay_count * 2)
            parts.append(add_box(f"Crown_Baluster_{index:02d}", (0.12, 0.16, 0.46),
                                 (x, face_y - 0.08, h - 0.27), mats["secondary"]))

    role_name = "Crown" if crown else "Upper" if upper else variant_key.title().replace("_", "")
    return join_as(f"MOD_{role_name}", parts)


def build_floor_v3(
    grammar: dict,
    mats: dict,
    variant_key: str = "typical_a",
    interior_seed: int = 0,
) -> bpy.types.Object:
    """Build one graph-selected floor with a true front facade opening system."""
    if grammar["facade"].get("system") == "heritage_stone":
        return build_heritage_floor(grammar, mats, variant_key, interior_seed)
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


def _add_economy_window_row(
    parts: list,
    prefix: str,
    wall_length: float,
    axis: str,
    wall_offset: float,
    window_height: float,
    sill: float,
    mats: dict,
) -> None:
    """Low-draw-call side/rear windows for the City Prompt sheet profile."""
    count = max(2, int(round(wall_length / 4.5)))
    bay = wall_length / count
    window_width = bay * 0.58
    z = sill + window_height / 2
    for index in range(count):
        along = -wall_length / 2 + bay * (index + 0.5)
        if axis in ("front", "rear"):
            sign = -1.0 if axis == "front" else 1.0
            frame_location = (along, sign * (wall_offset + 0.018), z)
            glass_location = (along, sign * (wall_offset + 0.042), z)
            frame_size = (window_width + 0.16, 0.045, window_height + 0.16)
            glass_size = (window_width, 0.052, window_height)
        else:
            sign = -1.0 if axis == "left" else 1.0
            frame_location = (sign * (wall_offset + 0.018), along, z)
            glass_location = (sign * (wall_offset + 0.042), along, z)
            frame_size = (0.045, window_width + 0.16, window_height + 0.16)
            glass_size = (0.052, window_width, window_height)
        parts.append(add_box(f"{prefix}_{axis}_Frame_{index:02d}", frame_size, frame_location, mats["accent"]))
        parts.append(add_box(f"{prefix}_{axis}_Glass_{index:02d}", glass_size, glass_location, mats["glass"]))


def _signature_kits(grammar: dict) -> set[str]:
    return set((grammar.get("architectural_signature") or {}).get("kits") or [])


def _add_front_rail(parts: list, prefix: str, x: float, width: float, front_y: float,
                    z0: float, height: float, mats: dict) -> None:
    """Fine metal guard with real gaps; used by several regional kits."""
    metal = mats["signature_metal"]
    parts.append(add_box(f"{prefix}_Top", (width, 0.045, 0.045), (x, front_y, z0 + height), metal))
    parts.append(add_box(f"{prefix}_Bottom", (width, 0.04, 0.035), (x, front_y, z0 + 0.12), metal))
    count = max(3, int(width / 0.24))
    for index in range(count + 1):
        px = x - width / 2 + width * index / count
        parts.append(add_box(f"{prefix}_Picket{index:02d}", (0.026, 0.04, height - 0.1),
                             (px, front_y, z0 + height / 2 + 0.05), metal))


def _add_signature_podium_details(grammar: dict, parts: list, width: float, depth: float,
                                  height: float, mats: dict) -> None:
    kits = _signature_kits(grammar)
    if not kits:
        return
    front_y = -depth / 2
    warm, stone, metal = mats["signature_warm"], mats["signature_stone"], mats["signature_metal"]

    if kits & {"stone_base", "rusticated_base"}:
        course_h = min(0.46, height / 7)
        for row in range(max(3, int(height / course_h))):
            z = min(height - 0.12, course_h * (row + 0.5))
            parts.append(add_box(f"Signature_StoneCourse{row:02d}", (width + 0.08, 0.075, 0.045),
                                 (0, front_y - 0.07, z), stone))

    if kits & {"ceremonial_steps", "rowhouse_stoops", "layered_threshold"}:
        groups = 3 if "rowhouse_stoops" in kits else 1
        group_w = width / groups
        for group in range(groups):
            x = -width / 2 + group_w * (group + 0.5)
            stair_w = group_w * (0.56 if groups > 1 else 0.48)
            for step in range(3):
                step_h = 0.14 * (step + 1)
                step_d = 0.42 + (2 - step) * 0.28
                parts.append(add_box(f"Signature_Step{group}_{step}", (stair_w + step * 0.12, step_d, step_h),
                                     (x, front_y - step_d / 2, step_h / 2), stone))
            if groups > 1:
                for sx in (-1, 1):
                    parts.append(add_box(f"Signature_StoopRail{group}_{sx}", (0.045, 0.74, 0.74),
                                         (x + sx * stair_w * 0.48, front_y - 0.37, 0.62), metal))

    if kits & {"giant_portico", "pilotis"}:
        span = width * (0.48 if "giant_portico" in kits else 0.72)
        count = max(4, min(8, round(span / 3.0)))
        radius = min(0.36, width / 80 + 0.16)
        column_h = height * 0.92
        for index in range(count):
            x = -span / 2 + span * index / max(1, count - 1)
            y = front_y - (0.88 if "giant_portico" in kits else 0.38)
            parts.append(add_cylinder(f"Signature_PorticoColumn{index:02d}", radius, column_h,
                                      (x, y, column_h / 2), stone if "giant_portico" in kits else mats["concrete"], 20))
            parts.append(add_box(f"Signature_PorticoCapital{index:02d}", (radius * 2.8, radius * 2.8, 0.16),
                                 (x, y, column_h - 0.08), stone))
        if "giant_portico" in kits:
            parts.append(add_box("Signature_PorticoEntablature", (span + 1.25, 1.36, 0.34),
                                 (0, front_y - 0.78, height - 0.28), stone))

    if kits & {"ground_arcade", "romanesque_arcade"}:
        count = max(3, min(8, round(width / 4.4)))
        bay = width / count
        radius = min(bay * 0.34, height * 0.28)
        spring = height * (0.48 if "ground_arcade" in kits else 0.42)
        for index in range(count):
            x = -width / 2 + bay * (index + 0.5)
            parts.append(add_arch_ring(f"Signature_Arcade{index:02d}", x, front_y - 0.10,
                                       spring, radius, min(0.26, radius * 0.26), 0.18, stone, 18))
            for sx in (-1, 1):
                parts.append(add_box(f"Signature_ArcadePier{index:02d}_{sx}",
                                     (0.22, 0.20, spring),
                                     (x + sx * (radius + 0.11), front_y - 0.10, spring / 2), stone))

    if kits & {"cast_iron_storefront", "machiya_shopfront", "double_height_lobby"}:
        span = width * (0.82 if "double_height_lobby" in kits else 0.72)
        z0, z1 = 0.35, height * 0.84
        parts.append(add_box("Signature_StorefrontHeader", (span, 0.16, 0.16),
                             (0, front_y - 0.12, z1), metal))
        mullions = max(4, min(12, round(span / 1.45)))
        for index in range(mullions + 1):
            x = -span / 2 + span * index / mullions
            mat = warm if "machiya_shopfront" in kits else metal
            parts.append(add_box(f"Signature_StorefrontMullion{index:02d}", (0.07, 0.14, z1 - z0),
                                 (x, front_y - 0.12, (z0 + z1) / 2), mat))

    if kits & {"shopfront_canopies", "loading_canopy", "cantilever_canopy", "porte_cochere"}:
        if "porte_cochere" in kits:
            canopy_w, canopy_d = min(width * 0.34, 18.0), 2.35
        elif "cantilever_canopy" in kits:
            canopy_w, canopy_d = width * 0.66, 1.8
        else:
            canopy_w, canopy_d = width * 0.52, 1.25
        canopy_z = min(height - 0.45, 3.15)
        parts.append(add_box("Signature_Canopy", (canopy_w, canopy_d, 0.16),
                             (0, front_y - canopy_d / 2, canopy_z), warm if "porte_cochere" in kits else metal))
        if "porte_cochere" in kits:
            for x in (-canopy_w * 0.44, canopy_w * 0.44):
                parts.append(add_cylinder(f"Signature_PorteCochereColumn{x}", 0.22, canopy_z,
                                          (x, front_y - canopy_d * 0.82, canopy_z / 2), stone, 16))

    if kits & {"pointed_portal", "deco_portal", "carved_portal"}:
        portal_w = min(4.2, width * 0.18)
        portal_h = min(height * 0.86, 4.4)
        parts.append(add_box("Signature_PortalLeft", (0.34, 0.30, portal_h),
                             (-portal_w / 2, front_y - 0.16, portal_h / 2), stone))
        parts.append(add_box("Signature_PortalRight", (0.34, 0.30, portal_h),
                             (portal_w / 2, front_y - 0.16, portal_h / 2), stone))
        if "pointed_portal" in kits:
            apex = min(height - 0.08, portal_h + 0.92)
            verts = [(-portal_w / 2 - 0.17, front_y - 0.31, portal_h - 0.2),
                     (portal_w / 2 + 0.17, front_y - 0.31, portal_h - 0.2),
                     (0, front_y - 0.31, apex),
                     (-portal_w / 2 - 0.17, front_y - 0.01, portal_h - 0.2),
                     (portal_w / 2 + 0.17, front_y - 0.01, portal_h - 0.2),
                     (0, front_y - 0.01, apex)]
            parts.append(add_prism("Signature_PointedPortal", verts,
                                   [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)], stone))
        else:
            parts.append(add_box("Signature_PortalHead", (portal_w + 0.68, 0.30, 0.42),
                                 (0, front_y - 0.16, portal_h - 0.2), stone))

    if kits & {"brick_pilasters", "heavy_masonry_piers", "rowhouse_divisions"}:
        count = max(3, min(12, round(width / 4.5)))
        for index in range(count + 1):
            x = -width / 2 + width * index / count
            pier_w = 0.34 if "heavy_masonry_piers" not in kits else 0.56
            parts.append(add_box(f"Signature_BasePier{index:02d}", (pier_w, 0.24, height * 0.96),
                                 (x, front_y - 0.13, height * 0.48), stone if "heavy_masonry_piers" in kits else mats["secondary"]))

    if kits & {"sign_frieze"}:
        parts.append(add_box("Signature_SignFrieze", (width * 0.82, 0.18, 0.62),
                             (0, front_y - 0.12, height * 0.77), mats["secondary"]))


def _add_signature_floor_details(grammar: dict, parts: list, width: float, depth: float,
                                 height: float, facade_y: float, variant_key: str,
                                 mats: dict, sheet_material=None) -> None:
    kits = _signature_kits(grammar)
    if not kits:
        return
    warm, stone, metal = mats["signature_warm"], mats["signature_stone"], mats["signature_metal"]
    typical_b = variant_key == "typical_b"
    crown = variant_key == "crown"

    if kits & {"centre_pavilion", "concrete_frame", "gothic_tower"}:
        pavilion_w = width * (0.24 if "gothic_tower" in kits else 0.30 if "centre_pavilion" in kits else 0.74)
        frame_mat = stone if kits & {"centre_pavilion", "gothic_tower"} else mats["concrete"]
        pier_w = min(0.58, pavilion_w * 0.08)
        projection = 0.42 if "gothic_tower" in kits else 0.30
        if sheet_material is not None and kits & {"centre_pavilion", "gothic_tower"}:
            parts.append(add_box("Signature_CentrePavilionField", (pavilion_w, projection + 0.12, height * 0.94),
                                 (0, facade_y - (projection + 0.12) / 2, height * 0.50), sheet_material))
        parts.append(add_box("Signature_CentrePavilionLeft", (pier_w, projection, height * 0.94),
                             (-pavilion_w / 2, facade_y - projection / 2, height * 0.50), frame_mat))
        parts.append(add_box("Signature_CentrePavilionRight", (pier_w, projection, height * 0.94),
                             (pavilion_w / 2, facade_y - projection / 2, height * 0.50), frame_mat))
        parts.append(add_box("Signature_CentrePavilionHead", (pavilion_w + pier_w, projection, 0.20),
                             (0, facade_y - projection / 2, height - 0.14), frame_mat))
        parts.append(add_box("Signature_CentrePavilionSill", (pavilion_w + pier_w, projection, 0.16),
                             (0, facade_y - projection / 2, 0.12), frame_mat))

    if kits & {"timber_picture_frames", "recessed_balcony_columns"}:
        centres = (-width * 0.27, width * 0.27) if width > 13 else (width * 0.22,)
        frame_w = min(3.25, width * 0.22)
        projection = facade_y - 0.29
        for index, x in enumerate(centres):
            parts.append(add_box(f"Signature_TimberFrame{index}_L", (0.18, 0.34, height * 0.92),
                                 (x - frame_w / 2, projection, height * 0.50), warm))
            parts.append(add_box(f"Signature_TimberFrame{index}_R", (0.18, 0.34, height * 0.92),
                                 (x + frame_w / 2, projection, height * 0.50), warm))
            parts.append(add_box(f"Signature_TimberFrame{index}_Head", (frame_w + 0.18, 0.34, 0.18),
                                 (x, projection, height - 0.16), warm))
            parts.append(add_box(f"Signature_TimberFrame{index}_Sill", (frame_w + 0.18, 0.34, 0.16),
                                 (x, projection, 0.14), warm))
            if "recessed_balcony_columns" in kits and not crown:
                slab_y = facade_y - 0.42
                parts.append(add_box(f"Signature_LoggiaSlab{index}", (frame_w - 0.22, 0.82, 0.12),
                                     (x, slab_y, 0.08), warm))
                _add_front_rail(parts, f"Signature_LoggiaRail{index}", x, frame_w - 0.36,
                                facade_y - 0.86, 0.12, min(1.02, height * 0.34), mats)

    if kits & {"haussmann_balconies", "continuous_balcony", "eixample_balconies"}:
        should_add = typical_b or "eixample_balconies" in kits or crown
        if should_add:
            balcony_w = width * (0.92 if "eixample_balconies" not in kits else 0.86)
            slab_y = facade_y - 0.46
            parts.append(add_box("Signature_ContinuousBalconySlab", (balcony_w, 0.78, 0.12),
                                 (0, slab_y, 0.09), stone))
            _add_front_rail(parts, "Signature_ContinuousBalconyRail", 0, balcony_w,
                            facade_y - 0.88, 0.13, min(1.0, height * 0.34), mats)

    if kits & {"oriel_bays"} and not crown:
        for index, x in enumerate((-width * 0.27, width * 0.27)):
            ow = min(2.7, width * 0.18)
            parts.append(add_box(f"Signature_Oriel{index}", (ow, 0.52, height * 0.80),
                                 (x, facade_y - 0.27, height * 0.52), mats["secondary"]))
            parts.append(add_box(f"Signature_OrielGlass{index}", (ow * 0.72, 0.05, height * 0.56),
                                 (x, facade_y - 0.55, height * 0.54), mats["glass"]))

    if kits & {"brick_pilasters", "heavy_masonry_piers", "giant_pilasters", "buttresses", "vertical_fins"}:
        if "vertical_fins" in kits:
            count, pier_w, projection = max(6, min(18, round(width / 2.2))), 0.16, 0.52
        else:
            count = max(4, min(14, round(width / 4.2)))
            pier_w = 0.56 if kits & {"heavy_masonry_piers", "buttresses"} else 0.30
            projection = 0.32 if "buttresses" not in kits else 0.58
        for index in range(count + 1):
            x = -width / 2 + width * index / count
            parts.append(add_box(f"Signature_VerticalPier{index:02d}", (pier_w, projection, height * 0.96),
                                 (x, facade_y - projection / 2, height * 0.50),
                                 metal if "vertical_fins" in kits else stone))

    if kits & {"brise_soleil", "curtainwall_fins", "timber_lattice"}:
        count = max(8, min(28, round(width / (0.72 if "timber_lattice" in kits else 1.25))))
        fin_depth = 0.48 if "brise_soleil" in kits else 0.30
        fin_mat = warm if "timber_lattice" in kits else metal
        for index in range(count + 1):
            x = -width / 2 + width * index / count
            parts.append(add_box(f"Signature_ScreenFin{index:02d}", (0.07, fin_depth, height * 0.84),
                                 (x, facade_y - fin_depth / 2 - 0.04, height * 0.52), fin_mat))
        if "brise_soleil" in kits:
            for z in (height * 0.28, height * 0.55, height * 0.82):
                parts.append(add_box(f"Signature_BriseHorizontal{z}", (width * 0.94, fin_depth, 0.08),
                                     (0, facade_y - fin_depth / 2, z), mats["concrete"]))

    if kits & {"industrial_steel_bays", "upper_loggias"}:
        count = max(3, min(10, round(width / 4.4)))
        bay = width / count
        for index in range(count):
            x = -width / 2 + bay * (index + 0.5)
            frame_w = bay * 0.76
            add_frame_bars(parts, f"Signature_IndustrialBay{index:02d}", "front",
                           (x, facade_y - 0.16, height * 0.52), frame_w, height * 0.68,
                           0.18, metal if "industrial_steel_bays" in kits else stone,
                           profile=0.10, mullions="double")

    if kits & {"steel_bracing"} and typical_b:
        span = width * 0.72
        length = math.sqrt(span * span + (height * 0.72) ** 2)
        angle = math.atan2(height * 0.72, span)
        for sign in (-1, 1):
            brace = add_box(f"Signature_SteelBrace{sign}", (length, 0.13, 0.10),
                            (0, facade_y - 0.24, height * 0.51), metal)
            brace.rotation_euler.y = sign * angle
            parts.append(brace)

    if kits & {"romanesque_arcade"} and not crown:
        count = max(3, min(8, round(width / 4.8)))
        bay = width / count
        radius = min(bay * 0.29, height * 0.30)
        for index in range(count):
            x = -width / 2 + bay * (index + 0.5)
            parts.append(add_arch_ring(f"Signature_FloorArch{index:02d}", x, facade_y - 0.15,
                                       height * 0.52, radius, 0.20, 0.20, stone, 16))

    if kits & {"corner_rotunda", "transparent_corners"}:
        radius = min(0.58, width * 0.035)
        x = -width / 2 + radius
        parts.append(add_cylinder("Signature_CornerRotunda", radius, height * 0.92,
                                  (x, facade_y - radius * 0.30, height * 0.50),
                                  mats["glass"] if "transparent_corners" in kits else stone, 24))

    if kits & {"asymmetric_bays"}:
        x = width * 0.34
        parts.append(add_box("Signature_AsymmetricBlade", (0.32, 0.52, height * 0.88),
                             (x, facade_y - 0.27, height * 0.50), warm))


def _add_signature_roof_details(grammar: dict, parts: list, width: float, depth: float,
                                height: float, mats: dict) -> None:
    kits = _signature_kits(grammar)
    if not kits:
        return
    warm, stone, metal = mats["signature_warm"], mats["signature_stone"], mats["signature_metal"]
    base_z = min(0.34, height * 0.28)

    if kits & {"roof_guard"}:
        rail_z = min(height - 0.08, 0.92)
        _add_front_rail(parts, "Signature_RoofGuard", 0, width * 0.94,
                        -depth / 2 - 0.04, base_z, max(0.18, rail_z - base_z), mats)

    if kits & {"roof_monitor"}:
        monitor_h = min(height * 0.72, 1.55)
        parts.append(add_box("Signature_RoofMonitor", (width * 0.34, depth * 0.24, monitor_h),
                             (0, 0, monitor_h / 2), metal))
        parts.append(add_box("Signature_RoofMonitorGlass", (width * 0.28, 0.05, monitor_h * 0.52),
                             (0, -depth * 0.12 - 0.03, monitor_h * 0.52), mats["glass"]))

    if kits & {"roof_pergola"}:
        top_z = min(height - 0.06, 1.12)
        span = width * 0.48
        for x in (-span / 2, span / 2):
            parts.append(add_box(f"Signature_PergolaColumn{x}", (0.13, 0.13, top_z),
                                 (x, 0, top_z / 2), metal))
        for index in range(7):
            x = -span / 2 + span * index / 6
            parts.append(add_box(f"Signature_PergolaBeam{index}", (0.10, depth * 0.34, 0.10),
                                 (x, 0, top_z), metal))

    if kits & {"crenellated_crown"}:
        block_h = min(0.52, height * 0.44)
        count = max(5, min(18, round(width / 2.7)))
        for index in range(count):
            if index % 2:
                continue
            x = -width / 2 + width * (index + 0.5) / count
            parts.append(add_box(f"Signature_Crenel{index:02d}", (width / count * 0.82, 0.42, block_h),
                                 (x, -depth / 2 + 0.21, block_h / 2), stone))

    if kits & {"stepped_crown", "deco_spire"}:
        remaining = max(0.24, height - 0.18)
        stages = ((0.40, 0.48), (0.25, 0.30), (0.12, 0.16))
        z = 0.10
        for index, (scale, frac) in enumerate(stages):
            stage_h = remaining * frac
            if z + stage_h > height:
                stage_h = max(0.08, height - z)
            parts.append(add_box(f"Signature_DecoCrown{index}", (width * scale, depth * scale, stage_h),
                                 (0, 0, z + stage_h / 2), stone if index < 2 else warm))
            z += stage_h
        if "deco_spire" in kits and z < height - 0.06:
            parts.append(add_cylinder("Signature_DecoSpire", 0.12, height - z,
                                      (0, 0, (z + height) / 2), metal, 12))

    if kits & {"deep_eaves", "tile_eaves", "slim_eaves", "deep_cornice", "civic_cornice", "pressed_metal_cornice", "bracketed_cornice", "corbelled_cornice"}:
        mat = warm if kits & {"deep_eaves", "tile_eaves"} else stone
        parts.append(add_box("Signature_RoofEdge", (width + 0.56, depth + 0.48, min(0.22, height * 0.18)),
                             (0, 0, min(height - 0.11, 0.24)), mat))

    if kits & {"corner_turret"}:
        turret_h = min(height * 0.94, 3.8)
        radius = min(2.4, width * 0.055)
        for index, x in enumerate((-width / 2 + radius * 0.82, width / 2 - radius * 0.82)):
            parts.append(add_cylinder(f"Signature_RoofTurret{index}", radius, turret_h * 0.46,
                                      (x, -depth / 2 + radius * 0.82, turret_h * 0.23), stone, 20))
            cap_z = turret_h * 0.46
            verts = [(x - radius * 1.1, -depth / 2 - radius * 0.20, cap_z),
                     (x + radius * 1.1, -depth / 2 - radius * 0.20, cap_z),
                     (x + radius * 1.1, -depth / 2 + radius * 1.72, cap_z),
                     (x - radius * 1.1, -depth / 2 + radius * 1.72, cap_z),
                     (x, -depth / 2 + radius * 0.76, turret_h)]
            parts.append(add_prism(f"Signature_RoofTurretCap{index}", verts,
                                   [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (3, 2, 1, 0)], mats["roof"]))


def build_facade_sheet_podium(grammar: dict, mats: dict) -> bpy.types.Object:
    """Hybrid podium: photo elevation in front, conventional PBR construction elsewhere."""
    dims, facade, massing = grammar["dimensions"], grammar["facade"], grammar["massing"]
    width, depth, height = dims["width_m"], dims["depth_m"], dims["podium_height_m"]
    front_y = -depth / 2
    parts: list = [
        add_box("SheetPodium_Core", (width, depth, height), (0, 0, height / 2), mats["primary"]),
        add_box("SheetPodium_FrontAtlas", (width, 0.045, height),
                (0, front_y - 0.0225, height / 2), mats["sheet_podium"]),
        add_box("SheetPodium_Plinth", (width + 0.14, depth + 0.12, 0.24),
                (0, 0, 0.12), mats["concrete"]),
        add_box("SheetPodium_HeadCourse", (width + 0.24, depth + 0.18, 0.18),
                (0, 0, height - 0.09), mats["secondary"]),
    ]
    if FACADE_SHEET_DETAIL == "city":
        parts.extend([
            add_box("SheetPodium_LeftAtlas", (0.045, depth, height),
                    (-width / 2 - 0.0225, 0, height / 2), mats["sheet_podium"]),
            add_box("SheetPodium_RightAtlas", (0.045, depth, height),
                    (width / 2 + 0.0225, 0, height / 2), mats["sheet_podium"]),
            add_box("SheetPodium_RearAtlas", (width, 0.045, height),
                    (0, depth / 2 + 0.0225, height / 2), mats["sheet_podium"]),
        ])
    elif massing.get("corner_condition") == "corner":
        parts.append(add_box("SheetPodium_CornerAtlas", (0.045, depth, height),
                             (-width / 2 - 0.0225, 0, height / 2), mats["sheet_podium"]))
    # A real canopy is worth retaining: it provides the street-level shadow and
    # silhouette that a flat photograph cannot cast in City Prompt.
    if massing.get("has_podium_retail"):
        canopy_width = min(width * 0.46, 15.0)
        parts.append(add_box("SheetPodium_EntranceCanopy", (canopy_width, 1.15, 0.13),
                             (0, front_y - 0.57, min(height - 0.55, 3.15)), mats["accent"]))

    # Keep economical windows on non-hero elevations so orbit/aerial views do
    # not reveal an unarticulated box behind the photographic front.
    bay_count, bay_width = _bays(width, facade["bay_width_m"])
    side_count, _ = _bays(depth * 0.9, facade["bay_width_m"])
    window_height = max(1.4, height * 0.48)
    sill = max(0.55, (height - window_height) * 0.38)
    if FACADE_SHEET_DETAIL == "hero":
        add_window_row(parts, "SheetPodium", width, "rear", depth / 2, 0.0,
                       bay_width * 0.56, window_height, sill, bay_count, mats)
        if massing.get("corner_condition") != "corner":
            add_window_row(parts, "SheetPodium", depth * 0.9, "left", width / 2, 0.0,
                           bay_width * 0.52, window_height, sill, side_count, mats)
        add_window_row(parts, "SheetPodium", depth * 0.9, "right", width / 2, 0.0,
                       bay_width * 0.52, window_height, sill, side_count, mats)
    # City-profile side/rear detail is carried by the wrapped atlas skins.
    _add_signature_podium_details(grammar, parts, width, depth, height, mats)
    module = join_as("MOD_Podium", parts)
    apply_facade_sheet_uv(module, FACADE_SHEET["manifest"]["span_m"], height)
    return module


def build_facade_sheet_floor(
    grammar: dict,
    mats: dict,
    variant_key: str = "typical_a",
    interior_seed: int = 0,
) -> bpy.types.Object:
    """Hybrid repeatable floor with a photographed hero facade and 3D silhouette detail."""
    dims, facade, massing = grammar["dimensions"], grammar["facade"], grammar["massing"]
    openings, attachment_specs, bay_specs, variants = _graph_lookup(grammar)
    variant = variants.get(variant_key) or variants.get("typical_a") or {}
    setback = variant_key == "upper"
    crown = variant_key == "crown"
    height = dims["setback_height_m"] if setback else dims["floor_height_m"]
    full_width, full_depth = dims["width_m"], dims["depth_m"]
    if setback:
        inset_front = max(float(massing.get("setback_front_m", 0.0)), 0.8)
        inset_side = max(float(massing.get("setback_side_m", 0.0)), 0.45)
    elif crown:
        inset_front, inset_side = 0.35, 0.2
    else:
        inset_front = inset_side = 0.0
    width = full_width - inset_side * 2
    depth = full_depth - inset_front
    centre_y = inset_front / 2
    facade_y = centre_y - depth / 2
    system = facade.get("system", "regular")
    shell_material = mats["secondary"] if setback else mats["primary"]
    if crown and "sheet_crown" in mats:
        sheet_material = mats["sheet_crown"]
    elif variant_key == "typical_b" and "sheet_floor_alt" in mats:
        sheet_material = mats["sheet_floor_alt"]
    else:
        sheet_material = mats["sheet_floor"]
    parts: list = [
        add_box("SheetFloor_Core", (width, depth, height), (0, centre_y, height / 2), shell_material),
        add_box("SheetFloor_FrontAtlas", (width, 0.045, height),
                (0, facade_y - 0.0225, height / 2), sheet_material),
        add_box("SheetFloor_SlabEdge", (width + 0.10, depth + 0.08, 0.16),
                (0, centre_y, 0.08), mats["concrete"]),
    ]
    if FACADE_SHEET_DETAIL == "city":
        parts.extend([
            add_box("SheetFloor_LeftAtlas", (0.045, depth, height),
                    (-width / 2 - 0.0225, centre_y, height / 2), sheet_material),
            add_box("SheetFloor_RightAtlas", (0.045, depth, height),
                    (width / 2 + 0.0225, centre_y, height / 2), sheet_material),
            add_box("SheetFloor_RearAtlas", (width, 0.045, height),
                    (0, centre_y + depth / 2 + 0.0225, height / 2), sheet_material),
        ])
    elif massing.get("corner_condition") == "corner":
        parts.append(add_box("SheetFloor_CornerAtlas", (0.045, depth, height),
                             (-width / 2 - 0.0225, centre_y, height / 2), sheet_material))

    bay_sequence = list(variant.get("bay_sequence") or [])
    bay_count = len(bay_sequence) or int(facade.get("front_bay_count", 1))
    if not bay_sequence:
        bay_sequence = ["standard"] * bay_count
    bay_width = width / max(1, bay_count)

    # Retain only elements that materially change the silhouette or cast useful
    # shadows. Fine frames/panels remain exclusively in the sheet.
    for index, bay_key in enumerate(bay_sequence):
        bay_spec = bay_specs.get(bay_key) or bay_specs.get("standard") or {}
        kinds = {
            attachment_specs[item]["kind"] for item in (bay_spec.get("attachment_ids") or [])
            if item in attachment_specs
        }
        x = -width / 2 + bay_width * (index + 0.5)
        signature_kits = _signature_kits(grammar)
        signature_controls_balconies = bool(signature_kits & {
            "recessed_balcony_columns", "haussmann_balconies", "continuous_balcony",
            "eixample_balconies", "upper_loggias",
        })
        if "balcony" in kinds and not crown and not setback and not signature_controls_balconies:
            _add_balcony_v3(
                parts, f"SheetBalcony_{index:02d}", x, facade_y, bay_width,
                float(facade.get("balcony_depth_m", 1.5)),
                facade.get("balcony_guard", "metal"), mats,
                plants=facade.get("balcony_guard") == "planter",
            )
        # Oriel/window-bay detail stays in the sheet. A generic projecting box
        # covers the photographed glazing and looks worse than the source; only
        # balconies with a real walkable projection survive as 3D attachments.

    if system == "heritage_stone" and variant_key == "typical_b":
        _add_heritage_balcony(parts, "SheetHeritageBalcony", width, facade_y - 0.04, mats)

    # Side/rear detail remains procedural. This keeps one generated image per
    # family while retaining believable all-around models in orbit and aerial views.
    side_count, _ = _bays(depth * 0.9, facade["bay_width_m"])
    rear_window_width = min(bay_width * float(facade.get("window_width_ratio", 0.55)), bay_width - 0.48)
    rear_window_height = height * float(facade.get("window_height_ratio", 0.62))
    rear_sill = min(float(facade.get("sill_height_m", 0.75)), height - rear_window_height - 0.3)
    if FACADE_SHEET_DETAIL == "hero":
        add_window_row(parts, "SheetFloor", width, "rear", centre_y + depth / 2, 0.0,
                       rear_window_width, rear_window_height, rear_sill, bay_count, mats,
                       interior_seed=interior_seed)
        if massing.get("corner_condition") != "corner":
            add_window_row(parts, "SheetFloor", depth * 0.9, "left", width / 2, 0.0,
                           rear_window_width, rear_window_height, rear_sill, side_count, mats,
                           interior_seed=interior_seed)
        add_window_row(parts, "SheetFloor", depth * 0.9, "right", width / 2, 0.0,
                       rear_window_width, rear_window_height, rear_sill, side_count, mats,
                       interior_seed=interior_seed)
    # City-profile side/rear detail is carried by the wrapped atlas skins.

    if setback:
        parts.append(add_box("SheetTerrace_Deck", (full_width, full_depth, 0.09), (0, 0, 0.045), mats["concrete"]))
        terrace_y = -full_depth / 2 + 0.07
        parts.append(add_box("SheetTerrace_Rail", (full_width, 0.075, 0.075),
                             (0, terrace_y, 0.98), mats["accent"]))
        for post_index, x in enumerate((-full_width / 2 + 0.12, -full_width / 4, 0.0,
                                        full_width / 4, full_width / 2 - 0.12)):
            parts.append(add_box(f"SheetTerrace_Post{post_index}", (0.075, 0.075, 0.92),
                                 (x, terrace_y, 0.5), mats["accent"]))
    if crown:
        _add_crown_v3(parts, system, width, depth, height, facade_y, mats)
    elif "timber_picture_frames" not in _signature_kits(grammar):
        parts.append(add_box("SheetFloor_HeadDatum", (width + 0.14, 0.12, 0.10),
                             (0, facade_y - 0.04, height - 0.05), mats["secondary"]))

    _add_signature_floor_details(
        grammar, parts, width, depth, height, facade_y, variant_key, mats, sheet_material
    )

    role_name = "Crown" if crown else "Setback" if setback else variant_key.title().replace("_", "")
    module = join_as(f"MOD_{role_name}", parts)
    apply_facade_sheet_uv(module, FACADE_SHEET["manifest"]["span_m"], height)
    return module


def build_roof(grammar: dict, mats: dict) -> bpy.types.Object:
    dims, roof = grammar["dimensions"], grammar["roof"]
    w, d, h = dims["width_m"], dims["depth_m"], dims["roof_height_m"]
    parts: list = []

    if roof["type"] == "mansard":
        slab_h = 0.18
        skirt_h = max(2.6, h * 0.72)
        inset = min(2.25, min(w, d) * 0.18)
        ov = 0.28
        parts.append(add_box("Mansard_CorniceDeck", (w + 0.72, d + 0.64, slab_h),
                             (0, 0, slab_h / 2), mats["secondary"]))
        bottom = [
            (-w / 2 - ov, -d / 2 - ov, slab_h), (w / 2 + ov, -d / 2 - ov, slab_h),
            (w / 2 + ov, d / 2 + ov, slab_h), (-w / 2 - ov, d / 2 + ov, slab_h),
        ]
        top = [
            (-w / 2 + inset, -d / 2 + inset, skirt_h), (w / 2 - inset, -d / 2 + inset, skirt_h),
            (w / 2 - inset, d / 2 - inset, skirt_h), (-w / 2 + inset, d / 2 - inset, skirt_h),
        ]
        parts.append(add_prism(
            "Mansard_SlateSkirt", bottom + top,
            [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7), (3, 2, 1, 0)],
            mats["roof"],
        ))
        parts.append(add_box("Mansard_LeadTop", (w - inset * 2 + 0.18, d - inset * 2 + 0.18, 0.16),
                             (0, 0, skirt_h + 0.08), mats["accent"]))
        # Flashing bands are intentionally modeled: they catch highlights in
        # aerial views where a normal map alone would disappear.
        parts.append(add_box("Mansard_FrontFlashing", (w + 0.28, 0.16, 0.16),
                             (0, -d / 2 - 0.18, slab_h + 0.08), mats["accent"]))
        parts.append(add_box("Mansard_RearFlashing", (w + 0.28, 0.16, 0.16),
                             (0, d / 2 + 0.18, slab_h + 0.08), mats["accent"]))

        dormer_count = max(4, min(6, round(w / 4.8)))
        dormer_w = min(1.48, w / dormer_count * 0.48)
        dormer_h = min(1.75, skirt_h * 0.46)
        dormer_z = slab_h + skirt_h * 0.51
        for index in range(dormer_count):
            x = -w / 2 + w * (index + 0.5) / dormer_count
            body_d = 0.86
            body_y = -d / 2 + 0.30
            parts.append(add_box(f"DormerFront_{index:02d}_Body", (dormer_w + 0.34, body_d, dormer_h + 0.38),
                                 (x, body_y, dormer_z), mats["secondary"]))
            add_heritage_sash_front(
                parts, f"DormerFront_{index:02d}", x, body_y - body_d / 2 - 0.02, dormer_z,
                dormer_w, dormer_h, mats,
                pediment="triangle" if index in (0, dormer_count // 2, dormer_count - 1) else "segmental",
                interior_seed=index + 3, overlay=True,
            )
            # Rear dormers keep the asset credible in orbit views without
            # duplicating the full carved front surround.
            rear_y = d / 2 - 0.30
            parts.append(add_box(f"DormerRear_{index:02d}_Body", (dormer_w + 0.28, body_d, dormer_h + 0.30),
                                 (x, rear_y, dormer_z), mats["secondary"]))
            parts.append(add_box(f"DormerRear_{index:02d}_Glass", (dormer_w, 0.05, dormer_h),
                                 (x, rear_y + body_d / 2 + 0.03, dormer_z), mats["glass"]))
            add_frame_bars(parts, f"DormerRear_{index:02d}_Frame", "rear",
                           (x, rear_y + body_d / 2 + 0.06, dormer_z), dormer_w, dormer_h,
                           0.09, mats["secondary"], profile=0.052, mullions="double")

        side_dormer_count = max(2, min(4, round(d / 5)))
        for side_name, sign in (("Left", -1), ("Right", 1)):
            for index in range(side_dormer_count):
                y = -d / 2 + d * (index + 0.5) / side_dormer_count
                body_x = sign * (w / 2 - 0.30)
                parts.append(add_box(f"Dormer{side_name}_{index:02d}_Body", (0.86, dormer_w + 0.22, dormer_h + 0.28),
                                     (body_x, y, dormer_z), mats["secondary"]))
                parts.append(add_box(f"Dormer{side_name}_{index:02d}_Glass", (0.05, dormer_w, dormer_h),
                                     (sign * (w / 2 + 0.15), y, dormer_z), mats["glass"]))
                add_frame_bars(parts, f"Dormer{side_name}_{index:02d}_Frame", "left" if sign < 0 else "right",
                               (sign * (w / 2 + 0.19), y, dormer_z), dormer_w, dormer_h,
                               0.09, mats["secondary"], profile=0.052, mullions="double")

        # Four inhabited corner pavilions turn the roof into a composed skyline
        # rather than rooftop equipment. They are deliberately taller than the
        # dormer field and carry their own window and string-course hierarchy.
        pavilion_w = min(4.1, w * 0.18)
        pavilion_d = min(3.8, d * 0.24)
        pavilion_base_z = skirt_h - 1.02
        drum_h = 1.48
        pavilion_positions = [
            (sx * (w / 2 - pavilion_w * 0.62), sy * (d / 2 - pavilion_d * 0.62), sx, sy)
            for sy in (-1, 1) for sx in (-1, 1)
        ]
        for pavilion_index, (px, py, sx, sy) in enumerate(pavilion_positions):
            parts.append(add_box(f"RoofPavilion_{pavilion_index}_Drum", (pavilion_w, pavilion_d, drum_h),
                                 (px, py, pavilion_base_z + drum_h / 2), mats["secondary"]))
            for band_index, z in enumerate((pavilion_base_z + 0.18, pavilion_base_z + drum_h - 0.18)):
                parts.append(add_box(f"RoofPavilion_{pavilion_index}_Band{band_index}",
                                     (pavilion_w + 0.22, pavilion_d + 0.22, 0.16),
                                     (px, py, z), mats["secondary"]))
            if sy < 0:
                add_heritage_sash_front(
                    parts, f"RoofPavilion_{pavilion_index}_Front", px, py - pavilion_d / 2 - 0.015,
                    pavilion_base_z + drum_h * 0.55, min(1.08, pavilion_w * 0.30), 0.96, mats,
                    pediment="segmental", interior_seed=pavilion_index + 1, overlay=True,
                )
            side_x = px + sx * (pavilion_w / 2 + 0.025)
            parts.append(add_box(f"RoofPavilion_{pavilion_index}_SideGlass", (0.05, 0.92, 0.88),
                                 (side_x, py, pavilion_base_z + drum_h * 0.55), mats["glass"]))
            add_frame_bars(parts, f"RoofPavilion_{pavilion_index}_SideFrame", "left" if sx < 0 else "right",
                           (side_x + sx * 0.04, py, pavilion_base_z + drum_h * 0.55), 0.92, 0.88,
                           0.09, mats["accent"], profile=0.052, mullions="single")

            cap_z = pavilion_base_z + drum_h
            cap_half_w, cap_half_d = pavilion_w * 0.58, pavilion_d * 0.58
            apex = (px, py, h - 0.48)
            verts = [
                (px - cap_half_w, py - cap_half_d, cap_z), (px + cap_half_w, py - cap_half_d, cap_z),
                (px + cap_half_w, py + cap_half_d, cap_z), (px - cap_half_w, py + cap_half_d, cap_z), apex,
            ]
            parts.append(add_prism(f"RoofPavilion_{pavilion_index}_Cap", verts,
                                   [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (3, 2, 1, 0)], mats["roof"]))
            parts.append(add_cylinder(f"RoofPavilion_{pavilion_index}_Finial", 0.055, 0.34,
                                      (px, py, h - 0.23), mats["accent"], 10))
            parts.append(add_cylinder(f"RoofPavilion_{pavilion_index}_FinialBall", 0.11, 0.12,
                                      (px, py, h - 0.03), mats["accent"], 12))

        # A lit roof lantern provides a single asymmetric landmark moment like
        # the cupola on the Kinnaird reference while remaining kit-generated.
        lantern_x, lantern_y = -w * 0.12, d * 0.05
        lantern_base_z = skirt_h + 0.12
        parts.append(add_box("RoofLantern_Base", (2.35, 2.35, 0.26),
                             (lantern_x, lantern_y, lantern_base_z), mats["secondary"]))
        parts.append(add_box("RoofLantern_Glow", (1.48, 1.48, 0.78),
                             (lantern_x, lantern_y, lantern_base_z + 0.63), mats["interior_warm"]))
        for column_index, (dx, dy) in enumerate(((-0.88, -0.88), (0.88, -0.88), (0.88, 0.88), (-0.88, 0.88))):
            parts.append(add_cylinder(f"RoofLantern_Column{column_index}", 0.13, 1.12,
                                      (lantern_x + dx, lantern_y + dy, lantern_base_z + 0.70),
                                      mats["secondary"], 16))
        lantern_cap_z = lantern_base_z + 1.30
        parts.append(add_box("RoofLantern_Cornice", (2.45, 2.45, 0.22),
                             (lantern_x, lantern_y, lantern_cap_z), mats["secondary"]))
        lantern_apex = (lantern_x, lantern_y, min(h - 0.18, lantern_cap_z + 1.05))
        lantern_half = 1.34
        lantern_verts = [
            (lantern_x - lantern_half, lantern_y - lantern_half, lantern_cap_z + 0.11),
            (lantern_x + lantern_half, lantern_y - lantern_half, lantern_cap_z + 0.11),
            (lantern_x + lantern_half, lantern_y + lantern_half, lantern_cap_z + 0.11),
            (lantern_x - lantern_half, lantern_y + lantern_half, lantern_cap_z + 0.11), lantern_apex,
        ]
        parts.append(add_prism("RoofLantern_Cap", lantern_verts,
                               [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (3, 2, 1, 0)], mats["roof"]))

        chimney_positions = (
            (-w * 0.32, -d * 0.18), (w * 0.32, -d * 0.18),
            (-w * 0.34, d * 0.20), (w * 0.34, d * 0.20),
        )
        for index, (x, y) in enumerate(chimney_positions):
            stack_z = min(skirt_h + 0.82, h - 1.70)
            parts.append(add_box(f"Chimney_{index:02d}_Stack", (0.92, 0.62, 1.64),
                                 (x, y, stack_z), mats["secondary"]))
            parts.append(add_box(f"Chimney_{index:02d}_Crown", (1.08, 0.78, 0.18),
                                 (x, y, stack_z + 0.88), mats["secondary"]))
            for pot_index, pot_x in enumerate((-0.24, 0.24)):
                parts.append(add_cylinder(f"Chimney_{index:02d}_Pot{pot_index}", 0.12, 0.58,
                                          (x + pot_x, y, stack_z + 1.26), mats["accent"], 12))
                parts.append(add_cylinder(f"Chimney_{index:02d}_PotCap{pot_index}", 0.16, 0.10,
                                          (x + pot_x, y, stack_z + 1.58), mats["accent"], 12))
    elif roof["type"] == "gabled":
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

    _add_signature_roof_details(grammar, parts, w, d, h, mats)
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
    view_set: str = "all",
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
    # Calibrated as an overcast-bright archviz rig. The previous 2.8-strength
    # sun clipped dark timber and masonry facade sheets into pale grey.
    sun_data.energy = 1.35
    sun_data.angle = math.radians(4.0)
    sun = bpy.data.objects.new("PreviewSun", sun_data)
    sun.rotation_euler = (math.radians(42), math.radians(-18), math.radians(-38))
    scene.collection.objects.link(sun)
    rig.append(sun)

    area_data = bpy.data.lights.new("PreviewFill", type="AREA")
    area_data.energy = 390.0
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
        bg.inputs[1].default_value = 0.34

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
    if view_set == "preview":
        views = views[:1]
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
        if FACADE_SHEET and "sheet_podium" in mats:
            return build_facade_sheet_podium(grammar, mats)
        return build_podium(grammar, mats)
    if role == "floor":
        if FACADE_SHEET and "sheet_floor" in mats:
            return build_facade_sheet_floor(
                grammar, mats, variant_key if variant_key != "default" else "typical_a", interior_seed
            )
        return build_floor_v3(grammar, mats, variant_key if variant_key != "default" else "typical_a", interior_seed)
    if role == "setback":
        if FACADE_SHEET and "sheet_floor" in mats:
            return build_facade_sheet_floor(grammar, mats, "upper", interior_seed)
        return build_floor_v3(grammar, mats, "upper", interior_seed)
    if role == "crown":
        if FACADE_SHEET and "sheet_floor" in mats:
            return build_facade_sheet_floor(grammar, mats, "crown", interior_seed)
        return build_floor_v3(grammar, mats, "crown", interior_seed)
    if role == "roof":
        return build_roof(grammar, mats)
    raise ValueError(f"unknown module role {role}")


def generate(grammar: dict, output: Path, *, floors_override: int | None, keep_blend: bool,
             thumbnail: bool, assembled: bool, ao: bool = True, ao_resolution: int = 512,
             ao_samples: int = 16, presentation_engine: str = "eevee",
             presentation_samples: int = 48, presentation_view_set: str = "all") -> None:
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
        # Photo elevations already contain micro-occlusion. Baking another AO
        # layout onto their glTF material causes double-darkening and, in some
        # viewers, a mismatched UV-channel artifact.
        ao_baked = bake_ao(module, ao_resolution, ao_samples) if ao and not FACADE_SHEET else False
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
                    view_set=presentation_view_set,
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
        "facade_sheet": ({
            "schema": FACADE_SHEET["manifest"].get("schema", "facade-sheet@1"),
            "source_directory": str(FACADE_SHEET["dir"]),
            "model": FACADE_SHEET["manifest"].get("model"),
            "span_m": FACADE_SHEET["manifest"].get("span_m"),
            "style_reference": FACADE_SHEET["manifest"].get("style_reference"),
            "runtime_material_profile": "photo_baked_v1",
            "geometry_detail_profile": FACADE_SHEET_DETAIL,
        } if FACADE_SHEET else None),
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
    parser.add_argument("--presentation-view-set", choices=("all", "preview"), default="all",
                        help="render all review angles or only the hero preview")
    parser.add_argument("--facade-sheets", type=Path, default=None,
                        help="facade-sheet directory; enables the hybrid photo-elevation modules")
    parser.add_argument("--facade-sheet-detail", choices=("hero", "city"), default="hero",
                        help="hero keeps full side/rear openings; city uses a lighter orbit-safe treatment")
    return parser.parse_args(argv)


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    args = parse_args(argv)
    global TEXTURES_DIR, FACADE_SHEET, FACADE_SHEET_DETAIL
    TEXTURES_DIR = args.textures.resolve() if args.textures else None
    FACADE_SHEET_DETAIL = args.facade_sheet_detail
    if args.facade_sheets:
        sheet_dir = args.facade_sheets.resolve()
        sheet_manifest = sheet_dir / "manifest.json"
        if not sheet_manifest.exists():
            raise SystemExit(f"--facade-sheets: {sheet_manifest} not found")
        FACADE_SHEET = {
            "dir": sheet_dir,
            "manifest": json.loads(sheet_manifest.read_text(encoding="utf-8")),
        }
        print(
            f"[blender_generate] facade-sheet mode: {sheet_dir.name} "
            f"(span={FACADE_SHEET['manifest'].get('span_m')}m)"
        )
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
        presentation_view_set=args.presentation_view_set,
    )


if __name__ == "__main__":
    main()
