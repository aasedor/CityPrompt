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

# Blender's --python entry point does not consistently add the script's folder
# to sys.path on Windows; keep compiler-side helper modules importable.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from glass_profiles import glass_profile, glass_profile_for_grammar

GENERATOR_VERSION = "0.14.1"
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
    roots = [
        TEXTURES_DIR,
        DEFAULT_TEXTURES_DIR,
        DEFAULT_TEXTURES_DIR.parent / "textures_archviz_v5",
        DEFAULT_TEXTURES_DIR.parent / "textures_kinnaird_v6",
    ]
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
        # A real dielectric surface: physical transmission with an opaque alpha
        # channel.  Mixing partial alpha and transmission double-counts the
        # transparency term in glTF/Three.js and produces grey, toy-like panes.
        if "Coat Weight" in bsdf.inputs:
            bsdf.inputs["Coat Weight"].default_value = 0.32
        if "Coat Roughness" in bsdf.inputs:
            bsdf.inputs["Coat Roughness"].default_value = 0.07
        if "IOR" in bsdf.inputs:
            bsdf.inputs["IOR"].default_value = 1.50
        bsdf.inputs["Metallic"].default_value = 0.0
        bsdf.inputs["Roughness"].default_value = 0.10
        alpha = bsdf.inputs.get("Alpha")
        if alpha:
            alpha.default_value = 1.0
        transmission = bsdf.inputs.get("Transmission Weight") or bsdf.inputs.get("Transmission")
        if transmission:
            transmission.default_value = 0.78
        color = color[:3] + (1.0,)
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
            "standing_seam": 1.10,
            "verdigris_copper": 0.98,
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
            "standing_seam": 0.04,
            "verdigris_copper": 0.03,
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


def make_profile_glass_material(name: str, profile_name: str) -> bpy.types.Material:
    """Create unmasked physical glass from the shared optical profile.

    Facade-sheet overlays already use the profile, but semantic graph windows
    also need the same tint, transmission and IOR.  Keeping alpha opaque avoids
    the double-transparency artefact in glTF/Three.js while the occupied room
    card supplies the warm interior behind the pane.
    """
    profile = glass_profile(profile_name)
    mat = make_material(name, {
        "base_color": profile["tint"],
        "roughness": profile["roughness"],
        "metallic": 0.0,
    })
    principled = next(
        (node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"),
        None,
    )
    if principled is not None:
        principled.inputs["Base Color"].default_value = hex_rgba(str(profile["tint"]))
        principled.inputs["Metallic"].default_value = 0.0
        principled.inputs["Roughness"].default_value = float(profile["roughness"])
        alpha = principled.inputs.get("Alpha")
        if alpha:
            alpha.default_value = 1.0
        transmission = principled.inputs.get("Transmission Weight") or principled.inputs.get("Transmission")
        if transmission:
            transmission.default_value = float(profile["transmission"])
        if principled.inputs.get("IOR"):
            principled.inputs["IOR"].default_value = float(profile["ior"])
        if principled.inputs.get("Coat Weight"):
            principled.inputs["Coat Weight"].default_value = float(profile["clearcoat"])
        if principled.inputs.get("Coat Roughness"):
            principled.inputs["Coat Roughness"].default_value = float(profile["clearcoat_roughness"])
        if principled.inputs.get("Specular IOR Level"):
            principled.inputs["Specular IOR Level"].default_value = float(profile["specular_ior_level"])
        emission = principled.inputs.get("Emission Color") or principled.inputs.get("Emission")
        if emission:
            emission.default_value = hex_rgba(str(profile["interior_light_color"]))
        if principled.inputs.get("Emission Strength"):
            principled.inputs["Emission Strength"].default_value = float(profile.get("glass_emission_strength", 0.0))
    mat.diffuse_color = hex_rgba(str(profile["tint"]))
    mat["glazing_profile"] = profile_name
    mat["glazing_lod"] = "near"
    mat["alpha_strategy"] = "opaque_physical_transmission"
    return mat


def make_facade_sheet_material(
    name: str,
    albedo: Path,
    roughness: Path | None,
    emissive: Path | None,
    normal: Path | None = None,
    ao: Path | None = None,
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

    if normal and normal.exists():
        normal_node = nodes.new("ShaderNodeTexImage")
        normal_node.name = normal_node.label = "SHEET_Normal"
        normal_node.image = _load_image(normal, "Non-Color")
        normal_node.extension = "REPEAT"
        normal_node.location = (-500, -280)
        normal_map = nodes.new("ShaderNodeNormalMap")
        normal_map.name = normal_map.label = "SHEET_NormalMap"
        normal_map.uv_map = "UVMap"
        normal_map.inputs["Strength"].default_value = 0.62
        normal_map.location = (-180, -250)
        links.new(uv_node.outputs["UV"], normal_node.inputs["Vector"])
        links.new(normal_node.outputs["Color"], normal_map.inputs["Color"])
        links.new(normal_map.outputs["Normal"], bsdf.inputs["Normal"])

    if ao and ao.exists():
        ao_node = nodes.new("ShaderNodeTexImage")
        ao_node.name = ao_node.label = "SHEET_Occlusion"
        ao_node.image = _load_image(ao, "Non-Color")
        ao_node.extension = "REPEAT"
        ao_node.location = (-500, -500)
        gltf_output = nodes.new("ShaderNodeGroup")
        gltf_output.name = gltf_output.label = "glTF Material Output"
        gltf_output.node_tree = _gltf_output_group()
        gltf_output.location = (-120, -500)
        links.new(uv_node.outputs["UV"], ao_node.inputs["Vector"])
        links.new(ao_node.outputs["Color"], gltf_output.inputs["Occlusion"])

    if emissive and emissive.exists():
        emissive_node = nodes.new("ShaderNodeTexImage")
        emissive_node.name = emissive_node.label = "SHEET_EmissiveMask"
        emissive_node.image = _load_image(emissive, "Non-Color")
        emissive_node.extension = "REPEAT"
        emissive_node.location = (-500, -690)
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
    mat["facade_uv"] = True
    mat["glazing_lod"] = "far"
    return mat


def _add_binary_alpha_mask(
    mat: bpy.types.Material,
    mask_path: Path,
    *,
    node_label: str,
) -> None:
    """Wire a binary mask through a recognized alpha-clip node graph.

    The source texture is already white where this material should render.
    ``GREATER_THAN`` exports as glTF ``alphaMode=MASK`` rather than alpha
    blending, so transmissive glass pixels retain opacity=1 as required by the
    physical material model.
    """
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = next((node for node in nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None or bsdf.inputs.get("Alpha") is None:
        raise ValueError(f"{mat.name} has no Principled alpha input")
    uv_node = next((node for node in nodes if node.type == "UVMAP"), None)
    if uv_node is None:
        uv_node = nodes.new("ShaderNodeUVMap")
        uv_node.uv_map = "UVMap"
        uv_node.location = (-760, -430)
    mask_node = nodes.new("ShaderNodeTexImage")
    mask_node.name = mask_node.label = node_label
    mask_node.image = _load_image(mask_path, "Non-Color")
    mask_node.extension = "REPEAT"
    mask_node.interpolation = "Closest"
    mask_node.location = (-500, -500)
    threshold = nodes.new("ShaderNodeMath")
    threshold.name = threshold.label = f"{node_label}_Clip"
    threshold.operation = "GREATER_THAN"
    threshold.inputs[1].default_value = 0.5
    threshold.location = (-140, -470)
    links.new(uv_node.outputs["UV"], mask_node.inputs["Vector"])
    links.new(mask_node.outputs["Color"], threshold.inputs[0])
    links.new(threshold.outputs[0], bsdf.inputs["Alpha"])


def make_near_facade_sheet_material(
    name: str,
    far_material: bpy.types.Material,
    opaque_mask: Path,
    pbr: dict[str, Path] | None = None,
) -> bpy.types.Material:
    """Facade albedo with semantic holes where physical glazing takes over."""
    if pbr and pbr.get("albedo"):
        mat = make_facade_sheet_material(
            name,
            pbr["albedo"],
            pbr.get("roughness"),
            pbr.get("emissive"),
            pbr.get("normal"),
            pbr.get("ao"),
        )
    else:
        mat = far_material.copy()
        mat.name = name
    _add_binary_alpha_mask(mat, opaque_mask, node_label="SHEET_OpaqueMask")
    mat["facade_sheet"] = True
    mat["facade_uv"] = True
    mat["glazing_lod"] = "near"
    return mat


def make_glass_overlay_material(
    name: str,
    glass_mask: Path,
    profile_name: str,
    reference_albedo: Path | None = None,
) -> bpy.types.Material:
    """Pixel-masked, fully physical glazing for the close-range facade LOD."""
    profile = glass_profile(profile_name)
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (420, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (70, 0)
    bsdf.inputs["Base Color"].default_value = hex_rgba(str(profile["tint"]))
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = float(profile["roughness"])
    alpha = bsdf.inputs.get("Alpha")
    if alpha:
        alpha.default_value = 1.0
    transmission = bsdf.inputs.get("Transmission Weight") or bsdf.inputs.get("Transmission")
    if transmission:
        transmission.default_value = float(profile["transmission"])
    if bsdf.inputs.get("IOR"):
        bsdf.inputs["IOR"].default_value = float(profile["ior"])
    if bsdf.inputs.get("Coat Weight"):
        bsdf.inputs["Coat Weight"].default_value = float(profile["clearcoat"])
    if bsdf.inputs.get("Coat Roughness"):
        bsdf.inputs["Coat Roughness"].default_value = float(profile["clearcoat_roughness"])
    if bsdf.inputs.get("Specular IOR Level"):
        bsdf.inputs["Specular IOR Level"].default_value = float(profile["specular_ior_level"])
    emission = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
    if emission:
        emission.default_value = hex_rgba(str(profile["interior_light_color"]), 1.0)
    if bsdf.inputs.get("Emission Strength"):
        # A restrained warm contribution keeps every occupied pane readable in
        # Eevee and the City Prompt renderer without turning the glass itself
        # into a lightbox. The room card remains the dominant close-range cue.
        bsdf.inputs["Emission Strength"].default_value = float(profile.get("glass_emission_strength", 0.0))
    if reference_albedo and reference_albedo.exists():
        # Physical transmission alone loses the reflected streetscape and
        # interior variation authored by the reference-guided facade sheet.
        # Registered albedo restores those high-frequency cues while the
        # Principled shader still supplies IOR, transmission and reflections.
        uv_node = nodes.new("ShaderNodeUVMap")
        uv_node.uv_map = "UVMap"
        uv_node.location = (-720, 160)
        reference_node = nodes.new("ShaderNodeTexImage")
        reference_node.name = reference_node.label = "GLASS_BakedReference"
        reference_node.image = _load_image(reference_albedo, "sRGB")
        reference_node.extension = "REPEAT"
        reference_node.interpolation = "Linear"
        reference_node.location = (-500, 180)
        mix = nodes.new("ShaderNodeMixRGB")
        mix.name = mix.label = "GLASS_PhysicalBakedMix"
        mix.blend_type = "MIX"
        mix.inputs[0].default_value = float(profile.get("baked_glass_mix", 0.7))
        mix.inputs[1].default_value = hex_rgba(str(profile["tint"]), 1.0)
        mix.location = (-180, 170)
        links.new(uv_node.outputs["UV"], reference_node.inputs["Vector"])
        links.new(reference_node.outputs["Color"], mix.inputs[2])
        links.new(mix.outputs["Color"], bsdf.inputs["Base Color"])
        if emission:
            # The registered elevation already contains varied rooms, sky and
            # reflected streetscape. A very small emissive contribution keeps
            # that authored variation legible behind transmission (especially
            # in Eevee) without making every pane a uniform glowing rectangle.
            links.new(reference_node.outputs["Color"], emission)
            if bsdf.inputs.get("Emission Strength"):
                bsdf.inputs["Emission Strength"].default_value = float(
                    profile.get("baked_glass_emission", profile.get("glass_emission_strength", 0.0))
                )
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    _add_binary_alpha_mask(mat, glass_mask, node_label="GLASS_SemanticMask")
    mat.diffuse_color = hex_rgba(str(profile["tint"]), 1.0)
    mat["facade_uv"] = True
    mat["glazing_lod"] = "physical"
    mat["glass_profile"] = profile_name
    mat["environment_intensity"] = float(profile["environment_intensity"])
    return mat


def facade_mask_paths(role: str) -> tuple[Path, Path] | None:
    if not FACADE_SHEET:
        return None
    root = FACADE_SHEET["dir"]
    manifest = FACADE_SHEET["manifest"]
    if role == "elevation":
        semantic = ((manifest.get("pbr_lods") or {}).get("near")
                    or manifest.get("semantic_glass") or {})
        glass_name = semantic.get("glass_mask")
        opaque_name = semantic.get("opaque_mask")
    else:
        band = (manifest.get("bands") or {}).get(role) or {}
        near = ((band.get("lods") or {}).get("near") or band)
        glass_name = near.get("glass_mask")
        opaque_name = near.get("opaque_mask")
    if not glass_name or not opaque_name:
        return None
    glass_path, opaque_path = root / glass_name, root / opaque_name
    if not glass_path.exists() or not opaque_path.exists():
        return None
    return glass_path, opaque_path


def facade_lod_paths(role: str, lod: str) -> dict[str, Path]:
    """Resolve registered PBR maps, with schema-3 facade sheets as fallback."""
    if not FACADE_SHEET:
        return {}
    root = FACADE_SHEET["dir"]
    manifest = FACADE_SHEET["manifest"]
    if role == "elevation":
        payload = ((manifest.get("pbr_lods") or {}).get(lod) or {})
        if not payload:
            legacy = manifest.get("elevation_source") or "elevation_raw.jpg"
            payload = {"albedo": legacy}
    else:
        band = (manifest.get("bands") or {}).get(role) or {}
        payload = ((band.get("lods") or {}).get(lod) or band)
    paths: dict[str, Path] = {}
    for key in ("albedo", "normal", "roughness", "ao", "depth", "emissive"):
        filename = payload.get(key)
        if filename:
            path = root / filename
            if path.exists():
                paths[key] = path
    return paths


def facade_glass_regions(role: str) -> list[list[float]]:
    """Normalized opening groups extracted from the registered semantic mask."""
    if not FACADE_SHEET:
        return []
    manifest = FACADE_SHEET["manifest"]
    if role == "elevation":
        payload = manifest.get("semantic_glass") or {}
    else:
        payload = (manifest.get("bands") or {}).get(role) or {}
    regions = payload.get("glass_regions") or []
    return [
        [float(value) for value in region]
        for region in regions
        if isinstance(region, list) and len(region) == 4
    ]


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
    profile_name = glass_profile_for_grammar(grammar)
    glass_profile(profile_name)  # fail early on an invalid profile id
    signature_materials = (
        (grammar.get("architectural_signature") or {}).get("signature_material_overrides")
        or {}
    )
    signature_stone_spec = {
        "base_color": "#c7baa3", "roughness": 0.82, "metallic": 0.0,
        "texture_key": "limestone",
        **dict(signature_materials.get("signature_stone") or {}),
    }
    signature_warm_spec = {
        "base_color": "#765033", "roughness": 0.62, "metallic": 0.0,
        "texture_key": "oak_wood",
        **dict(signature_materials.get("signature_warm") or {}),
    }
    signature_roof_spec = {
        "base_color": "#7d898d", "roughness": 0.56, "metallic": 0.42,
        "texture_key": "standing_seam",
        **dict(signature_materials.get("signature_roof") or {}),
    }
    signature_metal_spec = {
        "base_color": "#17191b", "roughness": 0.34, "metallic": 0.72,
        **dict(signature_materials.get("signature_metal") or {}),
    }
    result = {
        "primary": make_material("MAT_Facade_Primary", materials["primary"]),
        "secondary": make_material("MAT_Facade_Secondary", materials["secondary"]),
        "accent": make_material("MAT_Accent", materials["accent"]),
        "glass": make_profile_glass_material("MAT_Glass", profile_name),
        "concrete": make_material("MAT_Concrete", materials["concrete"]),
        "roof": make_material("MAT_Roof", materials["roof"]),
        "roof_lead": make_material("MAT_Roof_AgedLead", {
            "base_color": "#65737a", "roughness": 0.56, "metallic": 0.58,
            "texture_key": "standing_seam",
        }),
        "green_roof": make_material("MAT_GreenRoof", materials["green_roof"]),
        "plant": make_material("MAT_Plants", {"base_color": "#416f38", "roughness": 0.86, "metallic": 0.0}),
        "plant_alt": make_material("MAT_Plants_Alt", {"base_color": "#6b7b45", "roughness": 0.88, "metallic": 0.0}),
        "interior": make_material("MAT_Interior_Shadow", {"base_color": "#171c21", "roughness": 0.72, "metallic": 0.0}),
        "interior_warm": make_material("MAT_Interior_Warm", {
            "base_color": "#6e4e2e", "roughness": 0.82, "metallic": 0.0,
            "emission_color": "#b77c3f", "emission_strength": 0.08,
        }),
        "signature_warm": make_material("MAT_Signature_WarmTimber", signature_warm_spec),
        "signature_dark": make_material("MAT_Signature_CharredLarch", {
            "base_color": "#252525", "roughness": 0.72, "metallic": 0.0,
        }),
        "signature_door": make_material("MAT_Signature_DarkOakDoor", {
            "base_color": "#3f2d22", "roughness": 0.64, "metallic": 0.0,
            "texture_key": "charred_timber",
        }),
        "signature_stone": make_material("MAT_Signature_CutStone", signature_stone_spec),
        "signature_roof": make_material("MAT_Signature_AgedLeadRoof", signature_roof_spec),
        "signature_metal": make_material("MAT_Signature_BlackMetal", signature_metal_spec),
        "massing_soffit": make_material("MAT_Massing_DarkConcreteSoffit", {
            "base_color": "#42413e", "roughness": 0.88, "metallic": 0.0,
            "texture_key": "concrete",
        }),
        "massing_joint": make_material("MAT_Massing_RecessShadow", {
            "base_color": "#17191a", "roughness": 0.72, "metallic": 0.0,
        }),
    }
    result["glass_profile_name"] = profile_name
    # Cell 7 in the legacy atlas is deliberately blue/dark. The occupied-city
    # treatment keeps every window lit, so omit that cell from new assemblies.
    room_count = 4 if grammar.get("facade", {}).get("system") == "heritage_stone" else 7
    result["interior_cells"] = [make_interior_atlas_material(index) for index in range(room_count)]
    glazing_frame = result["signature_metal"].copy()
    glazing_frame.name = f"MAT_GlazingFrame_{profile_name}"
    glazing_frame["glazing_lod"] = "near"
    result["glazing_frame"] = glazing_frame
    glazing_interiors = []
    glazing_profile = glass_profile(profile_name)
    for index, source in enumerate(result["interior_cells"]):
        interior = source.copy()
        interior.name = f"MAT_GlazingInterior_{profile_name}_{index:02d}"
        interior["glazing_lod"] = "interior"
        interior["always_lit"] = True
        # Room photography remains the base colour, but every glazing card has
        # a warm independent emission factor. This prevents dark navy panes in
        # daytime views while retaining furniture/parallax detail.
        if interior.use_nodes and interior.node_tree:
            principled = next(
                (node for node in interior.node_tree.nodes if node.type == "BSDF_PRINCIPLED"),
                None,
            )
            if principled:
                emission = principled.inputs.get("Emission Color") or principled.inputs.get("Emission")
                if emission:
                    # Atlas photography already contains lamps, furniture and
                    # tonal depth. Keep it linked to emission so illumination
                    # does not flatten every room into one white rectangle.
                    if not emission.links:
                        emission.default_value = hex_rgba(str(glazing_profile["interior_light_color"]), 1.0)
                strength = principled.inputs.get("Emission Strength")
                if strength:
                    strength.default_value = float(glazing_profile["interior_light_strength"])
        glazing_interiors.append(interior)
        # Expose deterministic aliases to the massing graph so exceptional
        # openings (turrets, lanterns and gable lancets) can use the same
        # occupied-room photography as registered facade glazing.
        result[f"glazing_interior_{index}"] = interior
    result["glazing_interior_cells"] = glazing_interiors
    if FACADE_SHEET:
        root = FACADE_SHEET["dir"]
        full_far = facade_lod_paths("elevation", "far")
        full_near = facade_lod_paths("elevation", "near")
        full_elevation = full_far.get("albedo")
        if full_elevation and full_elevation.exists():
            result["sheet_elevation"] = make_facade_sheet_material(
                "MAT_Sheet_Far_FullElevation",
                full_elevation,
                full_far.get("roughness"),
                full_far.get("emissive"),
                full_far.get("normal"),
                full_far.get("ao"),
            )
            result["sheet_elevation"]["facade_sheet_role"] = "elevation"
            masks = facade_mask_paths("elevation")
            if masks:
                glass_mask, opaque_mask = masks
                result["sheet_near_elevation"] = make_near_facade_sheet_material(
                    "MAT_Sheet_Near_FullElevation", result["sheet_elevation"], opaque_mask, full_near,
                )
                result["glass_overlay_elevation"] = make_glass_overlay_material(
                    f"MAT_GlassOverlay_{profile_name}_FullElevation", glass_mask, profile_name,
                    full_near.get("albedo", full_elevation),
                )
        for role, band in FACADE_SHEET["manifest"].get("bands", {}).items():
            if role not in ("floor", "floor_alt", "floor_c", "crown", "podium", "entrance"):
                continue
            far_pbr = facade_lod_paths(role, "far")
            near_pbr = facade_lod_paths(role, "near")
            if not far_pbr.get("albedo"):
                continue
            result[f"sheet_{role}"] = make_facade_sheet_material(
                f"MAT_Sheet_Far_{role.capitalize()}",
                far_pbr["albedo"],
                far_pbr.get("roughness"),
                far_pbr.get("emissive"),
                far_pbr.get("normal"),
                far_pbr.get("ao"),
            )
            result[f"sheet_{role}"]["facade_sheet_role"] = role
            masks = facade_mask_paths(role)
            if masks:
                glass_mask, opaque_mask = masks
                result[f"sheet_near_{role}"] = make_near_facade_sheet_material(
                    f"MAT_Sheet_Near_{role.capitalize()}", result[f"sheet_{role}"], opaque_mask, near_pbr,
                )
                result[f"glass_overlay_{role}"] = make_glass_overlay_material(
                    f"MAT_GlassOverlay_{profile_name}_{role.capitalize()}", glass_mask, profile_name,
                    near_pbr.get("albedo", far_pbr["albedo"]),
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


def add_cone(
    name: str,
    radius: float,
    depth: float,
    location: tuple[float, float, float],
    mat,
    vertices: int = 12,
) -> bpy.types.Object:
    """Low-cost architectural finial/pinnacle cap with a true tapered silhouette."""
    bpy.ops.mesh.primitive_cone_add(
        vertices=vertices, radius1=radius, radius2=0.0, depth=depth, location=location,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.use_smooth = vertices >= 12
    return obj


def add_torus(
    name: str,
    major_radius: float,
    minor_radius: float,
    location: tuple[float, float, float],
    mat,
    *,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    major_segments: int = 14,
    minor_segments: int = 4,
) -> bpy.types.Object:
    """Small forged-metal loop used as real silhouette-scale ornament.

    A few low-poly loops communicate wrought iron much more convincingly than
    a perfectly regular picket array, while remaining cheap enough to repeat
    across a resizable balcony module.
    """
    bpy.ops.mesh.primitive_torus_add(
        major_segments=major_segments,
        minor_segments=minor_segments,
        major_radius=major_radius,
        minor_radius=minor_radius,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj


def add_ellipsoid(
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    mat,
) -> bpy.types.Object:
    """Soft carved medallion/escutcheon with an intentionally shallow relief."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=10, radius=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
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


def add_beveled_box(
    name: str,
    size: tuple[float, float, float],
    location: tuple[float, float, float],
    mat,
    bevel_m: float = 0.025,
) -> bpy.types.Object:
    """Box with a construction-scale edge radius applied before joining.

    Landmark massing uses larger pieces than the repeatable facade modules. A
    per-node bevel keeps their roof and concrete edges from reading as perfect
    computer primitives while remaining deterministic in exported GLBs.
    """
    obj = add_box(name, size, location, mat)
    width = max(0.0, min(float(bevel_m), min(size) * 0.2))
    if width <= 0:
        return obj
    bevel = obj.modifiers.new(name="ConstructionEdge", type="BEVEL")
    bevel.width = width
    bevel.segments = 4 if width >= 0.09 else 3 if width >= 0.04 else 2
    bevel.limit_method = "ANGLE"
    try:
        bevel.harden_normals = True
    except AttributeError:
        pass
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    try:
        bpy.ops.object.modifier_apply(modifier=bevel.name)
    except RuntimeError:
        obj.modifiers.remove(bevel)
    return obj


def add_gable_roof(
    name: str,
    size: tuple[float, float, float],
    location: tuple[float, float, float],
    mat,
    bevel_m: float = 0.05,
    ridge_axis: str = "y",
) -> bpy.types.Object:
    """Triangular-prism roof with a ridge running along the depth axis.

    A real silhouette break is more effective than shading tricks at removing
    the procedural-box read. ``location.z`` is the eave datum and ``size.z``
    is the ridge rise, which keeps graph recipes easy to compare to elevations.
    """
    width, depth, rise = size
    cx, cy, eave_z = location
    x0, x1 = cx - width / 2, cx + width / 2
    y0, y1 = cy - depth / 2, cy + depth / 2
    ridge_z = eave_z + rise
    if ridge_axis == "x":
        verts = [
            (x0, y0, eave_z), (x0, y1, eave_z), (x0, cy, ridge_z),
            (x1, y0, eave_z), (x1, y1, eave_z), (x1, cy, ridge_z),
        ]
    elif ridge_axis == "y":
        verts = [
            (x0, y0, eave_z), (x1, y0, eave_z), (cx, y0, ridge_z),
            (x0, y1, eave_z), (x1, y1, eave_z), (cx, y1, ridge_z),
        ]
    else:
        raise ValueError(f"gable roof ridge axis {ridge_axis!r} is unsupported")
    faces = [
        (0, 3, 4, 1), (0, 1, 2), (3, 5, 4),
        (0, 2, 5, 3), (2, 1, 4, 5),
    ]
    obj = add_prism(name, verts, faces, mat)
    width_m = max(0.0, min(float(bevel_m), min(width, depth, rise) * 0.18))
    if width_m > 0:
        bevel = obj.modifiers.new(name="ConstructionEdge", type="BEVEL")
        bevel.width = width_m
        bevel.segments = 4 if width_m >= 0.09 else 3
        bevel.limit_method = "ANGLE"
        try:
            bevel.harden_normals = True
        except AttributeError:
            pass
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        try:
            bpy.ops.object.modifier_apply(modifier=bevel.name)
        except RuntimeError:
            obj.modifiers.remove(bevel)
    return obj


def add_hipped_roof(
    name: str,
    size: tuple[float, float, float],
    location: tuple[float, float, float],
    mat,
    bevel_m: float = 0.05,
    ridge_axis: str = "x",
    ridge_inset_m: float | None = None,
) -> bpy.types.Object:
    """Shallow rectangular hip roof with a real ridge and four sloping faces.

    Collegiate, civic and institutional landmarks often hide a low lead or
    standing-seam roof behind parapets. A gable prism leaves vertical end
    triangles that remain obvious in aerial Google Tiles views; this primitive
    closes those ends with hip planes while keeping the graph recipe parametric.
    ``location.z`` is the eave datum and ``size.z`` is the ridge rise.
    """
    width, depth, rise = size
    cx, cy, eave_z = location
    x0, x1 = cx - width / 2, cx + width / 2
    y0, y1 = cy - depth / 2, cy + depth / 2
    ridge_z = eave_z + rise
    if ridge_axis == "x":
        inset = (
            float(ridge_inset_m)
            if ridge_inset_m is not None
            else min(depth / 2, width * 0.42)
        )
        inset = max(0.01, min(inset, width / 2 - 0.01))
        verts = [
            (x0, y0, eave_z), (x1, y0, eave_z),
            (x1, y1, eave_z), (x0, y1, eave_z),
            (x0 + inset, cy, ridge_z), (x1 - inset, cy, ridge_z),
        ]
        faces = [
            (0, 1, 5, 4), (3, 4, 5, 2),
            (0, 4, 3), (1, 2, 5), (0, 3, 2, 1),
        ]
    elif ridge_axis == "y":
        inset = (
            float(ridge_inset_m)
            if ridge_inset_m is not None
            else min(width / 2, depth * 0.42)
        )
        inset = max(0.01, min(inset, depth / 2 - 0.01))
        verts = [
            (x0, y0, eave_z), (x1, y0, eave_z),
            (x1, y1, eave_z), (x0, y1, eave_z),
            (cx, y0 + inset, ridge_z), (cx, y1 - inset, ridge_z),
        ]
        faces = [
            (0, 4, 5, 3), (1, 2, 5, 4),
            (0, 1, 4), (3, 5, 2), (0, 3, 2, 1),
        ]
    else:
        raise ValueError(f"hipped roof ridge axis {ridge_axis!r} is unsupported")
    obj = add_prism(name, verts, faces, mat)
    width_m = max(0.0, min(float(bevel_m), min(width, depth, rise) * 0.18))
    if width_m > 0:
        bevel = obj.modifiers.new(name="ConstructionEdge", type="BEVEL")
        bevel.width = width_m
        bevel.segments = 4 if width_m >= 0.09 else 3
        bevel.limit_method = "ANGLE"
        try:
            bevel.harden_normals = True
        except AttributeError:
            pass
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        try:
            bpy.ops.object.modifier_apply(modifier=bevel.name)
        except RuntimeError:
            obj.modifiers.remove(bevel)
    return obj


def add_barrel_vault(
    name: str,
    span: float,
    depth: float,
    rise: float,
    location: tuple[float, float, float],
    mat,
    thickness: float = 0.10,
    segments: int = 18,
) -> bpy.types.Object:
    """Closed, thin semicylindrical roof shell with a depth-running ridge.

    Barrel roofs are silhouette geometry, not a bump-map effect.  A closed
    shell avoids one-sided faces in glTF and retains a credible eave thickness
    in grazing City Prompt views.
    """
    cx, cy, eave_z = location
    half_span = span / 2
    y_front, y_back = cy - depth / 2, cy + depth / 2
    count = max(8, int(segments))
    outer: list[tuple[float, float]] = []
    inner: list[tuple[float, float]] = []
    for index in range(count + 1):
        theta = math.pi - math.pi * index / count
        x = cx + half_span * math.cos(theta)
        z = eave_z + rise * math.sin(theta)
        outer.append((x, z))
        inner.append((x, z - thickness))
    verts = (
        [(x, y_front, z) for x, z in outer]
        + [(x, y_back, z) for x, z in outer]
        + [(x, y_front, z) for x, z in inner]
        + [(x, y_back, z) for x, z in inner]
    )
    stride = count + 1
    outer_front, outer_back, inner_front, inner_back = 0, stride, stride * 2, stride * 3
    faces: list[tuple[int, ...]] = []
    for index in range(count):
        nxt = index + 1
        faces.extend([
            (outer_front + index, outer_front + nxt, outer_back + nxt, outer_back + index),
            (inner_front + index, inner_back + index, inner_back + nxt, inner_front + nxt),
            (outer_front + index, inner_front + index, inner_front + nxt, outer_front + nxt),
            (outer_back + index, outer_back + nxt, inner_back + nxt, inner_back + index),
        ])
    faces.extend([
        (outer_front, outer_back, inner_back, inner_front),
        (outer_front + count, inner_front + count, inner_back + count, outer_back + count),
    ])
    obj = add_prism(name, verts, faces, mat)
    for polygon in obj.data.polygons[:count]:
        polygon.use_smooth = True
    return obj


def add_chamfered_box(
    name: str,
    size: tuple[float, float, float],
    location: tuple[float, float, float],
    mat,
    chamfer_m: float,
    bevel_m: float = 0.05,
) -> bpy.types.Object:
    """Eight-sided urban block with equal plan chamfers at every corner.

    This is the reusable Cerda/Eixample corner primitive.  It is deliberately
    authored as real geometry rather than a normal-map trick so the chamfered
    entry and returning balconies survive Google-Tiles oblique and aerial
    views.  Fixed corner assemblies can sit on the diagonal faces while the
    four cardinal middle elevations remain ordinary repeatable LEGO bays.
    """
    width, depth, height = size
    cx, cy, cz = location
    cut = max(0.01, min(float(chamfer_m), width * 0.48, depth * 0.48))
    x0, x1 = cx - width / 2, cx + width / 2
    y0, y1 = cy - depth / 2, cy + depth / 2
    z0, z1 = cz - height / 2, cz + height / 2
    ring = [
        (x0 + cut, y0), (x1 - cut, y0), (x1, y0 + cut), (x1, y1 - cut),
        (x1 - cut, y1), (x0 + cut, y1), (x0, y1 - cut), (x0, y0 + cut),
    ]
    verts = [(x, y, z0) for x, y in ring] + [(x, y, z1) for x, y in ring]
    faces: list[tuple[int, ...]] = [tuple(reversed(range(8))), tuple(range(8, 16))]
    faces.extend((i, (i + 1) % 8, (i + 1) % 8 + 8, i + 8) for i in range(8))
    obj = add_prism(name, verts, faces, mat)
    width_m = max(0.0, min(float(bevel_m), min(width, depth, height) * 0.12))
    if width_m > 0:
        bevel = obj.modifiers.new(name="ConstructionEdge", type="BEVEL")
        bevel.width = width_m
        bevel.segments = 4 if width_m >= 0.09 else 3
        bevel.limit_method = "ANGLE"
        try:
            bevel.harden_normals = True
        except AttributeError:
            pass
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        try:
            bpy.ops.object.modifier_apply(modifier=bevel.name)
        except RuntimeError:
            obj.modifiers.remove(bevel)
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


def add_pointed_arch_frame(
    parts: list,
    prefix: str,
    centre_x: float,
    front_y: float,
    base_z: float,
    spring_z: float,
    apex_z: float,
    inner_width: float,
    depth: float,
    profile: float,
    mat,
    back_mat=None,
) -> None:
    """Build a projected lancet surround from real jambs and converging arch stones.

    The former Gothic portal was a filled triangular prism. This assembly keeps
    the opening void legible, adds a shadowed door/window plane behind it, and
    remains parameterized by width and height for different facade bays.
    """
    half = inner_width / 2
    jamb_height = max(0.25, spring_z - base_z)
    rise = max(profile * 1.5, apex_z - spring_z)
    arch_length = math.sqrt(half * half + rise * rise)
    angle = math.atan2(rise, half)
    bevel = min(0.045, profile * 0.16)

    for side, x in (("L", centre_x - half - profile / 2), ("R", centre_x + half + profile / 2)):
        parts.append(add_beveled_box(
            f"{prefix}_Jamb{side}", (profile, depth, jamb_height + profile * 0.25),
            (x, front_y, base_z + jamb_height / 2), mat, bevel,
        ))

    left = add_beveled_box(
        f"{prefix}_ArchL", (arch_length + profile * 0.15, depth, profile),
        (centre_x - half / 2, front_y, (spring_z + apex_z) / 2), mat, bevel,
    )
    left.rotation_euler.y = -angle
    parts.append(left)
    right = add_beveled_box(
        f"{prefix}_ArchR", (arch_length + profile * 0.15, depth, profile),
        (centre_x + half / 2, front_y, (spring_z + apex_z) / 2), mat, bevel,
    )
    right.rotation_euler.y = angle
    parts.append(right)

    parts.append(add_beveled_box(
        f"{prefix}_Threshold", (inner_width + profile * 1.2, depth * 1.05, profile * 0.72),
        (centre_x, front_y, base_z + profile * 0.36), mat, bevel,
    ))
    if back_mat is not None:
        parts.append(add_box(
            f"{prefix}_Recess", (inner_width * 0.94, 0.045, apex_z - base_z - profile * 0.45),
            (centre_x, front_y + depth * 0.58, base_z + (apex_z - base_z) / 2), back_mat,
        ))


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
        if material and (material.name.startswith("MAT_Sheet_") or material.get("facade_uv"))
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
        material = mesh.materials[polygon.material_index]
        offset_u = float(material.get("facade_uv_offset_u", 0.0)) if material else 0.0
        scale_u = float(material.get("facade_uv_scale_u", 1.0)) if material else 1.0
        material_span_m = float(material.get("facade_uv_span_m", span_m)) if material else span_m
        flip_u = bool(material.get("facade_uv_flip_u", False)) if material else False
        x_dominant = abs(polygon.normal.x) > abs(polygon.normal.y)
        for loop_index in polygon.loop_indices:
            coordinate = mesh.vertices[mesh.loops[loop_index].vertex_index].co
            base_u = (
                (coordinate.y if x_dominant else coordinate.x) / max(0.25, material_span_m) + 0.5
            ) * scale_u
            uv_layer.data[loop_index].uv = (
                (-base_u if flip_u else base_u) + offset_u,
                coordinate.z / module_height_m,
            )


def wrapped_facade_material(
    source,
    role: str,
    elevation: str,
    *,
    offset_u: float = 0.0,
    scale_u: float = 1.0,
    span_m: float | None = None,
    flip_u: bool = False,
):
    """Clone a sheet for an always-visible secondary elevation.

    Near/far switching is a principal-elevation concern. Reusing a
    ``MAT_Sheet_Far_*`` material on side and rear polygons caused the runtime
    close LOD to hide those polygons whenever a near front sheet existed,
    exposing the plain wall core. The wrapped name/property intentionally sits
    outside that complementary LOD pair while preserving the same PBR maps.
    Per-elevation phase/flip avoids four mechanically identical facades.
    """
    material = source.copy()
    material.name = f"MAT_Sheet_Wrapped_{role.title()}_{elevation.title()}"
    material["facade_uv"] = True
    material["facade_sheet_role"] = role
    material["facade_elevation"] = elevation
    material["facade_scope"] = "wrapped_secondary_elevation"
    material["glazing_lod"] = "always"
    material["facade_uv_offset_u"] = float(offset_u)
    material["facade_uv_scale_u"] = float(scale_u)
    if span_m is not None:
        material["facade_uv_span_m"] = float(span_m)
    material["facade_uv_flip_u"] = bool(flip_u)
    return material


def apply_fixed_front_atlas_uv(
    obj: bpy.types.Object,
    material,
    *,
    centre_x: float,
    span_m: float,
    height_m: float,
) -> None:
    """Map one fixed landmark atlas exactly once after the repeatable UV pass."""
    mesh = obj.data
    target_indices = {
        index for index, candidate in enumerate(mesh.materials)
        if candidate == material
    }
    if not target_indices:
        return
    uv_layer = mesh.uv_layers.get("UVMap") or mesh.uv_layers.new(name="UVMap")
    half = max(0.125, span_m / 2)
    height_m = max(0.25, height_m)
    for polygon in mesh.polygons:
        if polygon.material_index not in target_indices:
            continue
        for loop_index in polygon.loop_indices:
            coordinate = mesh.vertices[mesh.loops[loop_index].vertex_index].co
            uv_layer.data[loop_index].uv = (
                (coordinate.x - centre_x + half) / (half * 2),
                coordinate.z / height_m,
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
    surround_material=None,
    frame_material=None,
    glass_material=None,
    trim_scale: float = 1.0,
    sash_mullions: str = "double",
    fine_glazing_rails: bool = True,
) -> None:
    """Deep multi-pane sash plus an independent carved-stone surround.

    The glass, frame and architrave sit on separate depth planes, so grazing
    light produces the same hierarchy that makes compact baked heritage assets
    convincing without requiring sculpted ornament on every stone.
    """
    atlas_cells = mats.get("interior_cells") or []
    room_mat = atlas_cells[interior_seed % len(atlas_cells)] if atlas_cells else mats["interior_warm"]
    surround_mat = surround_material or mats["secondary"]
    frame_mat = frame_material or mats["accent"]
    glass_mat = glass_material or mats["glass"]
    trim_scale = max(0.45, min(1.25, float(trim_scale)))
    room_y = face_y - 0.015 if overlay else face_y + 0.28
    glass_y = face_y - 0.070 if overlay else face_y + 0.20
    frame_y = face_y - 0.115 if overlay else face_y + 0.14
    parts.append(add_box(f"{prefix}_Room", (opening_w + 0.12, 0.055, opening_h + 0.12),
                         (x, room_y, centre_z), room_mat))
    parts.append(add_box(f"{prefix}_Glass", (opening_w, 0.045, opening_h),
                         (x, glass_y, centre_z), glass_mat))
    add_frame_bars(
        parts, f"{prefix}_Sash", "front", (x, frame_y, centre_z),
        opening_w, opening_h, 0.095, frame_mat, profile=0.052, mullions=sash_mullions,
    )
    # Sash meeting rail and small glazing bars establish human scale.
    parts.append(add_box(f"{prefix}_MeetingRail", (opening_w, 0.105, 0.075),
                         (x, frame_y - 0.01, centre_z), frame_mat))
    if fine_glazing_rails:
        for rail_index, offset in enumerate((-opening_h * 0.25, opening_h * 0.25)):
            parts.append(add_box(f"{prefix}_GlazingRail{rail_index}", (opening_w, 0.085, 0.035),
                                 (x, frame_y - 0.015, centre_z + offset), frame_mat))

    trim_depth = 0.22 * trim_scale
    trim_y = face_y - trim_depth / 2 + 0.025
    jamb = 0.16 * trim_scale
    parts.extend([
        add_box(f"{prefix}_ArchitraveL", (jamb, trim_depth, opening_h + 0.38),
                (x - opening_w / 2 - jamb / 2 - 0.055 * trim_scale, trim_y, centre_z + 0.03), surround_mat),
        add_box(f"{prefix}_ArchitraveR", (jamb, trim_depth, opening_h + 0.38),
                (x + opening_w / 2 + jamb / 2 + 0.055 * trim_scale, trim_y, centre_z + 0.03), surround_mat),
        add_box(f"{prefix}_Sill", (opening_w + 0.42 * trim_scale, trim_depth + 0.08, 0.13 * trim_scale),
                (x, trim_y - 0.035, centre_z - opening_h / 2 - 0.10 * trim_scale), surround_mat),
    ])
    top_z = centre_z + opening_h / 2
    if pediment == "triangle":
        half_w = opening_w / 2 + 0.32 * trim_scale
        y0, y1 = face_y - trim_depth - 0.02, face_y + 0.025
        verts = [
            (x - half_w, y0, top_z + 0.08), (x + half_w, y0, top_z + 0.08), (x, y0, top_z + 0.48 * trim_scale),
            (x - half_w, y1, top_z + 0.08), (x + half_w, y1, top_z + 0.08), (x, y1, top_z + 0.48 * trim_scale),
        ]
        faces = [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)]
        parts.append(add_prism(f"{prefix}_TriangularPediment", verts, faces, surround_mat))
        parts.append(add_box(f"{prefix}_PedimentBed", (opening_w + 0.72 * trim_scale, trim_depth + 0.10, 0.11),
                             (x, trim_y - 0.04, top_z + 0.05), surround_mat))
    elif pediment == "segmental":
        half_w, rise, band = opening_w / 2 + 0.24 * trim_scale, 0.30 * trim_scale, 0.11 * trim_scale
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
        parts.append(add_prism(f"{prefix}_SegmentalPediment", verts, faces, surround_mat))
    else:
        parts.append(add_box(f"{prefix}_Lintel", (opening_w + 0.46 * trim_scale, trim_depth + 0.06, 0.18 * trim_scale),
                             (x, trim_y - 0.025, top_z + 0.12 * trim_scale), surround_mat))


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
    rooftop_pavilion = _has_rooftop_pavilion(grammar)
    rooftop_pavilion = _has_rooftop_pavilion(grammar)
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


def _has_rooftop_pavilion(grammar: dict) -> bool:
    """True when the fixed crown is a recessed contemporary addition.

    Keeping this semantic in the grammar lets every adaptive-reuse archetype
    share the terrace/pavilion construction without hard-coding a family id.
    """
    return bool((grammar.get("massing") or {}).get("rooftop_pavilion"))


def _signature_relief_box(
    parts: list,
    name: str,
    size: tuple[float, float, float],
    location: tuple[float, float, float],
    material,
    *,
    bevel_m: float = 0.035,
):
    """Construction-softened box for facade elements that project from a skin.

    The bevel is intentionally small relative to the member: it produces the
    highlight roll-off found on cast stone, timber and folded metal without
    turning the architecture into rounded plastic.
    """
    smallest = max(0.001, min(float(value) for value in size))
    part = add_beveled_box(name, size, location, material, min(bevel_m, smallest * 0.22))
    parts.append(part)
    return part


def _rotated_beveled_box(
    name: str,
    size: tuple[float, float, float],
    location: tuple[float, float, float],
    material,
    rotation_z: float,
    bevel_m: float = 0.04,
) -> bpy.types.Object:
    part = add_beveled_box(name, size, location, material, bevel_m)
    part.rotation_euler[2] = rotation_z
    bpy.context.view_layer.objects.active = part
    part.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    return part


def _add_haussmann_corner_returns(
    parts: list,
    prefix: str,
    width: float,
    depth: float,
    height: float,
    facade_y: float,
    mats: dict,
    *,
    podium: bool = False,
) -> None:
    """Textured, softened 45-degree pavilions that turn onto side elevations."""
    stone, metal = mats["signature_stone"], mats["signature_metal"]
    pavilion_span = 1.72 if podium else 1.48
    pavilion_depth = 0.86 if podium else 0.72
    sqrt_half = math.sqrt(0.5)
    for side, sign in (("L", -1), ("R", 1)):
        rotation = math.pi / 4 if sign > 0 else math.pi * 3 / 4
        # Keep the chamfer within the module's dimensional contract while its
        # diagonal face still masks the original 90-degree atlas seam.
        centre_x = sign * (width / 2 - (0.72 if podium else 0.62))
        centre_y = facade_y + 0.13
        parts.append(_rotated_beveled_box(
            f"{prefix}_{side}_ChamferedPavilion",
            (pavilion_span, pavilion_depth, height * 0.985),
            (centre_x, centre_y, height * 0.50),
            stone,
            rotation,
            0.17 if podium else 0.14,
        ))

        outward = (sign * sqrt_half, -sqrt_half)
        window_h = min(2.35 if podium else 2.16, height * (0.56 if podium else 0.62))
        window_w = 0.82 if podium else 0.72
        window_z = min(height - window_h / 2 - 0.30, 0.64 + window_h / 2)
        surface_offset = pavilion_depth / 2 + 0.035
        window_x = centre_x + outward[0] * surface_offset
        window_y = centre_y + outward[1] * surface_offset
        window_material = (
            mats["interior_cells"][(0 if sign < 0 else 2) % len(mats["interior_cells"])]
            if FACADE_SHEET_DETAIL == "city" else mats["glass"]
        )
        parts.append(_rotated_beveled_box(
            f"{prefix}_{side}_CornerWindow",
            (window_w, 0.05, window_h),
            (window_x, window_y, window_z),
            window_material,
            rotation,
            0.018,
        ))
        frame_offset = surface_offset + 0.04
        frame_x = centre_x + outward[0] * frame_offset
        frame_y = centre_y + outward[1] * frame_offset
        frame_profile = 0.07 if podium else 0.06
        for edge, dx, dz, edge_w, edge_h in (
            ("L", -window_w / 2, 0.0, frame_profile, window_h + frame_profile),
            ("R", window_w / 2, 0.0, frame_profile, window_h + frame_profile),
            ("Head", 0.0, window_h / 2, window_w + frame_profile, frame_profile),
            ("Sill", 0.0, -window_h / 2, window_w + frame_profile, frame_profile),
            ("Mullion", 0.0, 0.0, frame_profile * 0.62, window_h),
            ("MeetingRail", 0.0, 0.0, window_w, frame_profile * 0.62),
        ):
            parts.append(_rotated_beveled_box(
                f"{prefix}_{side}_Window{edge}",
                (edge_w, 0.075, edge_h),
                (
                    frame_x + math.cos(rotation) * dx,
                    frame_y + math.sin(rotation) * dx,
                    window_z + dz,
                ),
                metal,
                rotation,
                0.018,
            ))
        for band_index, z in enumerate((0.12, height - 0.12)):
            parts.append(_rotated_beveled_box(
                f"{prefix}_{side}_Band{band_index}",
                (pavilion_span + 0.16, pavilion_depth + 0.12, 0.14),
                (centre_x, centre_y, z),
                stone,
                rotation,
                0.05,
            ))


def _add_haussmann_shopfronts(
    parts: list,
    width: float,
    height: float,
    front_y: float,
    mats: dict,
) -> None:
    """Recessed bronze/oak shopfront bays and one legible central address."""
    stone, metal, timber = mats["signature_stone"], mats["signature_metal"], mats["signature_door"]
    city_lod = FACADE_SHEET_DETAIL == "city"
    span = width * 0.88
    bay_count = max(5, min(10, round(width / 3.0)))
    bay = span / bay_count
    base_z = 0.30
    opening_h = min(2.82, height * 0.64)
    opening_z = base_z + opening_h / 2
    face_glass = front_y - 0.19
    face_frame = front_y - 0.23
    face_room = front_y - 0.105
    entry_index = bay_count // 2

    for index in range(bay_count):
        x = -span / 2 + bay * (index + 0.5)
        opening_w = bay * 0.74
        is_entry = index == entry_index
        parts.append(add_beveled_box(
            f"Signature_Shopfront{index:02d}_StoneHead",
            (bay * 0.92, 0.22, 0.22),
            (x, front_y - 0.11, base_z + opening_h + 0.16),
            stone,
            0.045,
        ))
        if not city_lod:
            parts.append(add_box(
                f"Signature_Shopfront{index:02d}_WarmRoom",
                (opening_w, 0.04, opening_h * 0.92),
                (x, face_room, opening_z),
                mats["interior_cells"][index % len(mats["interior_cells"])],
            ))
            parts.append(add_box(
                f"Signature_Shopfront{index:02d}_Glass",
                (opening_w, 0.045, opening_h),
                (x, face_glass, opening_z),
                mats["glass"],
            ))
        frame_mat = timber if is_entry else metal
        add_frame_bars(
            parts,
            f"Signature_Shopfront{index:02d}_Frame",
            "front",
            (x, face_frame, opening_z),
            opening_w,
            opening_h,
            0.10,
            frame_mat,
            profile=0.055 if is_entry else (0.036 if city_lod else 0.046),
            mullions="single" if is_entry or city_lod else "double",
        )
        # Solid kickplates and an independent transom keep the storefront from
        # reading as one printed rectangle.
        parts.append(add_beveled_box(
            f"Signature_Shopfront{index:02d}_Kickplate",
            (opening_w, 0.12, 0.34),
            (x, face_frame - 0.015, base_z + 0.17),
            frame_mat,
            0.025,
        ))
        parts.append(add_box(
            f"Signature_Shopfront{index:02d}_Transom",
            (opening_w, 0.10, 0.075),
            (x, face_frame - 0.01, base_z + opening_h * 0.78),
            frame_mat,
        ))
        if is_entry:
            # A genuine pair of glazed timber doors, not a brown atlas patch.
            for leaf, leaf_x in enumerate((x - opening_w * 0.255, x + opening_w * 0.255)):
                leaf_w = opening_w * 0.46
                parts.append(add_beveled_box(
                    f"Signature_EntryDoor{leaf}_Timber",
                    (leaf_w, 0.13, opening_h * 0.76),
                    (leaf_x, face_frame - 0.025, base_z + opening_h * 0.38),
                    timber,
                    0.035,
                ))
                parts.append(add_box(
                    f"Signature_EntryDoor{leaf}_Glass",
                    (leaf_w * 0.68, 0.035, opening_h * 0.49),
                    (leaf_x, face_frame - 0.10, base_z + opening_h * 0.48),
                    mats["interior_cells"][(entry_index + leaf) % len(mats["interior_cells"])]
                    if city_lod else mats["glass"],
                ))
                handle_x = leaf_x + (-1 if leaf == 0 else 1) * leaf_w * 0.28
                parts.append(add_cylinder(
                    f"Signature_EntryDoor{leaf}_Handle",
                    0.025,
                    0.46,
                    (handle_x, face_frame - 0.12, base_z + opening_h * 0.42),
                    metal,
                    10,
                ))

    # Stone piers terminate every bay and hide the lower-atlas repetition.
    for index in range(bay_count + 1):
        x = -span / 2 + bay * index
        parts.append(add_beveled_box(
            f"Signature_ShopfrontPier{index:02d}",
            (0.22, 0.28, opening_h + 0.34),
            (x, front_y - 0.14, base_z + (opening_h + 0.34) / 2),
            stone,
            0.055,
        ))


def _add_front_rail(parts: list, prefix: str, x: float, width: float, front_y: float,
                    z0: float, height: float, mats: dict, *, ornamental: bool = False) -> None:
    """Fine metal guard with real gaps; used by several regional kits."""
    metal = mats["signature_metal"]
    parts.append(add_box(f"{prefix}_Top", (width, 0.045, 0.045), (x, front_y, z0 + height), metal))
    parts.append(add_box(f"{prefix}_Bottom", (width, 0.04, 0.035), (x, front_y, z0 + 0.12), metal))
    city_lod = FACADE_SHEET_DETAIL == "city"
    count = max(3, int(width / (1.15 if city_lod else 0.24)))
    for index in range(count + 1):
        px = x - width / 2 + width * index / count
        parts.append(add_box(f"{prefix}_Picket{index:02d}", (0.026, 0.04, height - 0.1),
                             (px, front_y, z0 + height / 2 + 0.05), metal))
    if ornamental and not city_lod:
        panel_count = max(3, round(width / 0.82))
        panel = width / panel_count
        radius = min(0.18, height * 0.19, panel * 0.24)
        for index in range(panel_count):
            px = x - width / 2 + panel * (index + 0.5)
            parts.append(add_torus(
                f"{prefix}_Scroll{index:02d}", radius, 0.014,
                (px, front_y - 0.018, z0 + height * 0.55), metal,
                rotation=(math.pi / 2, 0.0, 0.0),
            ))


def _add_side_rail(
    parts: list,
    prefix: str,
    side_x: float,
    centre_y: float,
    span: float,
    z0: float,
    height: float,
    mats: dict,
    *,
    ornamental: bool = False,
) -> None:
    """Side-elevation counterpart to `_add_front_rail` for orbit views."""
    metal = mats["signature_metal"]
    parts.append(add_box(f"{prefix}_Top", (0.045, span, 0.045),
                         (side_x, centre_y, z0 + height), metal))
    parts.append(add_box(f"{prefix}_Bottom", (0.04, span, 0.035),
                         (side_x, centre_y, z0 + 0.12), metal))
    city_lod = FACADE_SHEET_DETAIL == "city"
    count = max(3, int(span / (1.15 if city_lod else 0.24)))
    for index in range(count + 1):
        py = centre_y - span / 2 + span * index / count
        parts.append(add_box(f"{prefix}_Picket{index:02d}", (0.04, 0.026, height - 0.1),
                             (side_x, py, z0 + height / 2 + 0.05), metal))
    if ornamental and not city_lod:
        panel_count = max(3, round(span / 0.82))
        panel = span / panel_count
        radius = min(0.18, height * 0.19, panel * 0.24)
        for index in range(panel_count):
            py = centre_y - span / 2 + panel * (index + 0.5)
            parts.append(add_torus(
                f"{prefix}_Scroll{index:02d}", radius, 0.014,
                (side_x, py, z0 + height * 0.55), metal,
                rotation=(0.0, math.pi / 2, 0.0),
            ))


def _add_front_fire_escape_stage(
    parts: list,
    prefix: str,
    width: float,
    height: float,
    facade_y: float,
    mats: dict,
    *,
    podium: bool = False,
    crown: bool = False,
) -> None:
    """Resizable black-steel fire-escape stage aligned to one LEGO storey.

    The atlas supplies the archetype-specific visual registration while these
    members provide silhouette, contact shadows and parallax. Each repeatable
    floor owns one flight and one landing, so the assembly stays continuous as
    users change its floor count.
    """
    metal = mats["signature_metal"]
    landing_w = min(3.25, width * 0.17)
    landing_d = 1.05
    centre_x = -width * 0.13
    landing_z = height * (0.70 if podium else 0.15)
    landing_y = facade_y - landing_d / 2 - 0.03
    _signature_relief_box(
        parts, f"{prefix}_Landing", (landing_w, landing_d, 0.11),
        (centre_x, landing_y, landing_z), metal, bevel_m=0.018,
    )
    rail_h = min(0.94, height * 0.28)
    _add_front_rail(
        parts, f"{prefix}_FrontRail", centre_x, landing_w,
        facade_y - landing_d - 0.04, landing_z, rail_h, mats,
    )
    for side_index, side_x in enumerate((centre_x - landing_w / 2, centre_x + landing_w / 2)):
        parts.append(add_box(
            f"{prefix}_SideRailTop{side_index}", (0.045, landing_d, 0.045),
            (side_x, landing_y, landing_z + rail_h), metal,
        ))
        for picket_index, py in enumerate((
            facade_y - 0.12,
            facade_y - landing_d * 0.52,
            facade_y - landing_d + 0.05,
        )):
            parts.append(add_box(
                f"{prefix}_SidePicket{side_index}_{picket_index}",
                (0.04, 0.04, rail_h - 0.08),
                (side_x, py, landing_z + rail_h / 2 + 0.02), metal,
            ))

    # The top module terminates with roof access rather than inventing a stair
    # flight that continues beyond the crown.
    if crown:
        ladder_x = centre_x - landing_w * 0.34
        ladder_y = facade_y - landing_d * 0.58
        ladder_h = max(1.1, height - landing_z - 0.12)
        for side in (-1, 1):
            parts.append(add_box(
                f"{prefix}_LadderRail{side}", (0.045, 0.045, ladder_h),
                (ladder_x + side * 0.26, ladder_y, landing_z + ladder_h / 2), metal,
            ))
        rung_count = max(4, int(ladder_h / 0.34))
        for rung in range(rung_count + 1):
            z = landing_z + ladder_h * rung / rung_count
            parts.append(add_box(
                f"{prefix}_LadderRung{rung:02d}", (0.56, 0.045, 0.035),
                (ladder_x, ladder_y - 0.01, z), metal,
            ))
        return

    if podium:
        start_x, start_z = centre_x + landing_w * 0.42, 0.22
        end_x, end_z = centre_x - landing_w * 0.38, landing_z + 0.02
    else:
        start_x, start_z = centre_x + landing_w * 0.40, landing_z + 0.04
        end_x, end_z = centre_x - landing_w * 0.40, height - 0.16
    run, rise = end_x - start_x, end_z - start_z
    flight_length = math.sqrt(run * run + rise * rise)
    angle = -math.atan2(rise, run)
    flight_x, flight_z = (start_x + end_x) / 2, (start_z + end_z) / 2
    for stringer_index, y in enumerate((facade_y - 0.30, facade_y - landing_d + 0.22)):
        stringer = add_beveled_box(
            f"{prefix}_Stringer{stringer_index}", (flight_length, 0.055, 0.085),
            (flight_x, y, flight_z), metal, 0.012,
        )
        stringer.rotation_euler.y = angle
        parts.append(stringer)
    tread_count = 7 if FACADE_SHEET_DETAIL == "city" else 11
    for tread in range(tread_count + 1):
        t = tread / tread_count
        x = start_x + run * t
        z = start_z + rise * t
        parts.append(add_box(
            f"{prefix}_Tread{tread:02d}", (0.38, landing_d * 0.68, 0.04),
            (x, facade_y - landing_d * 0.53, z), metal,
        ))


def _add_heritage_stone_depth_relief(
    grammar: dict,
    parts: list,
    prefix: str,
    width: float,
    depth: float,
    height: float,
    facade_y: float,
    mats: dict,
    *,
    podium: bool = False,
) -> None:
    """Wrap a scalable heritage module in real shadow-casting stone relief.

    The facade sheet remains the source of fine carving and colour variation,
    while semantic opening caps provide most of the depth hierarchy. Only the
    real building corners and podium datum are added here: a generic bay grid
    inevitably crosses photographed windows when a user resizes the footprint.
    """
    stone = mats["signature_stone"]
    rear_y = facade_y + depth
    projection = 0.24 if podium else 0.18
    course_depth = projection + 0.08
    course_height = min(0.19, height * 0.052)
    # Podium plinth/head are authored by ``build_facade_sheet_podium`` using
    # the same stone material; do not duplicate them as floating bands here.
    course_levels: list[float] = []

    for index, z in enumerate(course_levels):
        _signature_relief_box(
            parts, f"{prefix}_FrontCourse{index:02d}",
            (width + projection * 2, course_depth, course_height),
            (0.0, facade_y - course_depth / 2 - 0.025, z), stone, bevel_m=0.035,
        )
        _signature_relief_box(
            parts, f"{prefix}_RearCourse{index:02d}",
            (width + projection * 2, course_depth, course_height),
            (0.0, rear_y + course_depth / 2 + 0.025, z), stone, bevel_m=0.035,
        )
        _signature_relief_box(
            parts, f"{prefix}_LeftCourse{index:02d}",
            (course_depth, depth, course_height),
            (-width / 2 - course_depth / 2 - 0.025, facade_y + depth / 2, z),
            stone, bevel_m=0.035,
        )
        _signature_relief_box(
            parts, f"{prefix}_RightCourse{index:02d}",
            (course_depth, depth, course_height),
            (width / 2 + course_depth / 2 + 0.025, facade_y + depth / 2, z),
            stone, bevel_m=0.035,
        )

    corner_size = 0.48 if podium else 0.38
    corner_projection = 0.16 if podium else 0.11
    corner_height = height - (course_height * 2 if podium else 0.06)
    corner_z = height / 2
    for face, y in (
        ("Front", facade_y - corner_projection),
        ("Rear", rear_y + corner_projection),
    ):
        for side, x in (
            ("Left", -width / 2 + corner_size / 2 - corner_projection),
            ("Right", width / 2 - corner_size / 2 + corner_projection),
        ):
            corner_y = (
                y + corner_size / 2 if face == "Front"
                else y - corner_size / 2
            )
            _signature_relief_box(
                parts, f"{prefix}_{face}{side}Corner",
                (corner_size, corner_size, corner_height), (x, corner_y, corner_z),
                stone, bevel_m=0.065,
            )


def _add_chateau_turret_segments(
    parts: list,
    prefix: str,
    width: float,
    height: float,
    facade_y: float,
    mats: dict,
    *,
    podium: bool,
) -> None:
    """Stackable round corner-turret drums for Chateauesque families.

    Each LEGO level contributes one aligned masonry cylinder.  The roof module
    supplies the conical cap, so the landmark survives arbitrary floor counts
    without stretching a texture or floating above the facade.  The cylinder
    remains within the width contract and projects only toward the street.
    """
    if width < 20.0 or height < 2.5:
        return
    stone = mats["signature_stone"]
    metal = mats["accent"]
    room_cells = mats.get("interior_cells") or [mats["interior_warm"]]
    radius = min(2.15, max(1.55, width * 0.024))
    centre_y = facade_y + radius * 0.34
    window_h = min(1.62 if not podium else 1.86, height * 0.47)
    window_w = min(0.96, radius * 0.52)
    window_z = height * (0.52 if not podium else 0.48)
    for index, sign in enumerate((-1, 1)):
        x = sign * (width / 2 - radius * 0.98)
        parts.append(add_cylinder(
            f"{prefix}_{index:02d}_Drum", radius, height * 0.992,
            (x, centre_y, height / 2), stone, 32,
        ))
        for band_index, band_z in enumerate((0.12, height - 0.12)):
            parts.append(add_cylinder(
                f"{prefix}_{index:02d}_Course{band_index}", radius + 0.10, 0.16,
                (x, centre_y, band_z), stone, 32,
            ))

        # Street-facing occupied sash, recessed behind a real stone surround.
        add_heritage_sash_front(
            parts, f"{prefix}_{index:02d}_FrontSash", x,
            centre_y - radius - 0.015, window_z, window_w, window_h, mats,
            pediment="lintel", interior_seed=index + (4 if podium else 0),
            overlay=True, surround_material=stone, frame_material=metal,
            glass_material=room_cells[(index + 1) % len(room_cells)],
            trim_scale=0.70, sash_mullions="single", fine_glazing_rails=False,
        )

        # One side-facing sash makes the round projection read as inhabited
        # architecture in orbit views instead of a blank procedural cylinder.
        outer_x = x + sign * (radius + 0.025)
        room_mat = room_cells[(index + 2) % len(room_cells)]
        parts.append(add_box(
            f"{prefix}_{index:02d}_SideRoom",
            (0.055, window_w + 0.12, window_h + 0.12),
            (outer_x - sign * 0.08, centre_y, window_z), room_mat,
        ))
        parts.append(add_box(
            f"{prefix}_{index:02d}_SideGlass",
            (0.045, window_w, window_h),
            (outer_x, centre_y, window_z), room_mat,
        ))
        add_frame_bars(
            parts, f"{prefix}_{index:02d}_SideSash",
            "left" if sign < 0 else "right",
            (outer_x + sign * 0.055, centre_y, window_z),
            window_w, window_h, 0.09, metal,
            profile=0.048, mullions="single",
        )
        for jamb_index, offset_y in enumerate((-window_w / 2 - 0.09, window_w / 2 + 0.09)):
            _signature_relief_box(
                parts, f"{prefix}_{index:02d}_SideJamb{jamb_index}",
                (0.22, 0.15, window_h + 0.34),
                (outer_x + sign * 0.06, centre_y + offset_y, window_z),
                stone, bevel_m=0.035,
            )
        _signature_relief_box(
            parts, f"{prefix}_{index:02d}_SideSill",
            (0.24, window_w + 0.42, 0.13),
            (outer_x + sign * 0.07, centre_y, window_z - window_h / 2 - 0.10),
            stone, bevel_m=0.030,
        )


def _add_signature_podium_details(grammar: dict, parts: list, width: float, depth: float,
                                  height: float, mats: dict) -> None:
    kits = _signature_kits(grammar)
    if not kits:
        return
    front_y = -depth / 2
    warm, stone, metal = mats["signature_warm"], mats["signature_stone"], mats["signature_metal"]
    podium_band = ((FACADE_SHEET or {}).get("manifest", {}).get("bands", {}).get("podium") or {})
    # A render-locked podium crop already carries its stone coursing.  Testing
    # only for hand-audited openings let the generic ``stone_base`` kit draw a
    # ladder of pale courses across GPT-authored shopfront glass.
    audited_podium = bool(
        podium_band.get("audited_openings") or podium_band.get("audited_storey_crop")
    )
    facade_manifest = (FACADE_SHEET or {}).get("manifest", {})
    render_locked_chateau = bool(
        facade_manifest.get("render_target_id")
        and grammar.get("source", {}).get("archetype_id") == "chateauesque_grand_railway_hotel"
    )

    if "heritage_stone_depth" in kits:
        _add_heritage_stone_depth_relief(
            grammar, parts, "Signature_HeritagePodium", width, depth, height,
            front_y, mats, podium=True,
        )

    if "corner_turret" in kits:
        _add_chateau_turret_segments(
            parts, "Signature_PodiumTurret", width, height, front_y, mats,
            podium=True,
        )

    if kits & {"stone_base", "rusticated_base"} and not audited_podium:
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

    if "brewery_arch_portals" in kits:
        # The brewery reference is not a row of punched windows: four enormous
        # masonry arches are the massing.  Model their reveals and springing as
        # a fixed four-bay assembly while the audited atlas supplies brick and
        # ghost-sign detail inside those registered bays.
        bay_count = 4
        bay = width / bay_count
        radius = min(bay * 0.39, height * 0.34)
        spring = min(height * 0.62, height - radius - 0.18)
        for index in range(bay_count):
            x = -width / 2 + bay * (index + 0.5)
            parts.append(add_arch_ring(
                f"Signature_BreweryPortal{index:02d}", x, front_y - 0.28,
                spring, radius, 0.38, 0.42, mats["primary"], 22,
            ))
            parts.append(add_box(
                f"Signature_BreweryPortalBack{index:02d}",
                (radius * 1.88, 0.08, spring + radius * 0.76),
                (x, front_y + 0.08, (spring + radius * 0.76) / 2),
                mats["interior_warm"],
            ))
            for side_index, side in enumerate((-1, 1)):
                _signature_relief_box(
                    parts, f"Signature_BreweryJamb{index:02d}_{side_index}",
                    (0.42, 0.54, spring),
                    (x + side * radius, front_y - 0.29, spring / 2),
                    mats["primary"], bevel_m=0.055,
                )
        _signature_relief_box(
            parts, "Signature_BreweryLoadingThreshold",
            (width * 0.92, 0.72, 0.18),
            (0, front_y - 0.36, 0.09), mats["concrete"], bevel_m=0.035,
        )

    if "brewery_crane_beams" in kits:
        bay = width / 4
        beam_z = min(height - 0.44, height * 0.76)
        for index in range(4):
            x = -width / 2 + bay * (index + 0.5)
            _signature_relief_box(
                parts, f"Signature_BreweryCraneBeam{index:02d}",
                (bay * 0.58, 1.12, 0.24),
                (x, front_y - 0.56, beam_z), warm, bevel_m=0.04,
            )

    if "corten_insertion" in kits:
        # One end bay remains fixed while middle turbine bays repeat.  Its deep
        # folded returns make the weathering-steel intervention read as a volume
        # rather than a differently coloured rectangle in the facade atlas.
        insert_w = min(5.4, width * 0.18)
        insert_x = -width / 2 + insert_w / 2 + 0.24
        corten = mats["signature_warm"]
        _signature_relief_box(
            parts, "Signature_CortenPodiumFace", (insert_w, 0.74, height * 0.92),
            (insert_x, front_y - 0.38, height * 0.48), corten, bevel_m=0.10,
        )
        _signature_relief_box(
            parts, "Signature_CortenPodiumReturn", (0.62, 2.8, height * 0.92),
            (-width / 2 + 0.31, front_y + 1.4, height * 0.48), corten, bevel_m=0.10,
        )

    if kits & {"cast_iron_storefront", "machiya_shopfront", "double_height_lobby"}:
        span = width * (0.82 if "double_height_lobby" in kits else 0.72)
        z0, z1 = 0.35, height * 0.84
        _signature_relief_box(parts, "Signature_StorefrontHeader", (span, 0.16, 0.16),
                              (0, front_y - 0.12, z1), metal, bevel_m=0.025)
        mullions = max(4, min(12, round(span / 1.45)))
        for index in range(mullions + 1):
            x = -span / 2 + span * index / mullions
            mat = warm if "machiya_shopfront" in kits else metal
            _signature_relief_box(
                parts, f"Signature_StorefrontMullion{index:02d}", (0.07, 0.14, z1 - z0),
                (x, front_y - 0.12, (z0 + z1) / 2), mat, bevel_m=0.012,
            )

    if "shopfront_canopies" in kits:
        # The archetype has recessed timber/bronze shopfronts and sign fascias,
        # not unsupported black slabs. Build the actual bays and address.
        _add_haussmann_shopfronts(parts, width, height, front_y, mats)
        _add_haussmann_corner_returns(
            parts, "Signature_PodiumCorner", width, depth, height, front_y, mats, podium=True,
        )
    elif "fixed_loading_bay" in kits:
        # A converted truck-dock entrance is a fixed identity bay at the end of
        # the resizable middle-bay run. It must not stretch to half the facade.
        canopy_w = min(5.8, width * 0.24)
        canopy_d = 1.18
        canopy_x = width / 2 - canopy_w / 2 - min(0.72, width * 0.025)
        canopy_z = min(height - 0.46, 3.35)
        _signature_relief_box(
            parts, "Signature_FixedLoadingCanopy",
            (canopy_w, canopy_d, 0.15),
            (canopy_x, front_y - canopy_d / 2, canopy_z),
            metal, bevel_m=0.03,
        )
        for rod_index, rod_x in enumerate((
            canopy_x - canopy_w * 0.38,
            canopy_x,
            canopy_x + canopy_w * 0.38,
        )):
            rod_h = min(0.92, height * 0.21)
            parts.append(add_cylinder(
                f"Signature_FixedLoadingTie{rod_index}", 0.025, rod_h,
                (rod_x, front_y - canopy_d * 0.62, canopy_z + rod_h / 2),
                metal, 8,
            ))
    elif kits & {"loading_canopy", "cantilever_canopy", "porte_cochere"}:
        if "porte_cochere" in kits:
            # Keep the ceremonial entrance fixed and subordinate to the
            # centre pavilion.  Scaling it as a percentage of a 90-100 m LEGO
            # frontage produced the long green shelf seen in the V27 city
            # review; real railway-hotel entrances stay a legible object even
            # when the repeatable middle bays grow around them.
            canopy_w, canopy_d = min(width * 0.27, 14.0), 2.55
        elif "cantilever_canopy" in kits:
            canopy_w, canopy_d = width * 0.66, 1.8
        else:
            canopy_w, canopy_d = width * 0.52, 1.25
        canopy_z = min(height - 0.45, 3.35)
        if "porte_cochere" in kits:
            # Treat the porte-cochere as a miniature piece of the hotel: the
            # wall ledger, columns and edge profiles inherit the facade stone;
            # the pitched weathering surface inherits the roof; and only the
            # narrow ridge/flashing uses patinated metal.  This material and
            # profile inheritance keeps the entrance from looking like a prop
            # attached to an otherwise photographic elevation.
            canopy_y = front_y - canopy_d / 2
            _signature_relief_box(
                parts, "Signature_PorteCochereWallLedger", (canopy_w + 0.56, 0.34, 0.72),
                (0, front_y - 0.13, canopy_z - 0.10), stone, bevel_m=0.065,
            )
            _signature_relief_box(
                parts, "Signature_PorteCochereSoffit", (canopy_w - 0.42, canopy_d - 0.28, 0.10),
                (0, canopy_y, canopy_z - 0.16), mats["massing_soffit"], bevel_m=0.025,
            )
            if render_locked_chateau:
                # The approved Beaux-Arts target uses a stone balcony/terrace
                # over the ceremonial arrival.  A small copper gable made the
                # entrance look like a detachable shelter, so this target-
                # locked assembly inherits the facade's entablature instead.
                _signature_relief_box(
                    parts, "Signature_PorteCochereTerrace",
                    (canopy_w + 0.46, canopy_d + 0.22, 0.30),
                    (0, canopy_y, canopy_z + 0.02), stone, bevel_m=0.065,
                )
                balustrade_y = front_y - canopy_d - 0.03
                _signature_relief_box(
                    parts, "Signature_PorteCochereBalustradeTop",
                    (canopy_w + 0.38, 0.22, 0.16),
                    (0, balustrade_y, canopy_z + 0.76), stone, bevel_m=0.045,
                )
                _signature_relief_box(
                    parts, "Signature_PorteCochereBalustradeBase",
                    (canopy_w + 0.26, 0.20, 0.13),
                    (0, balustrade_y, canopy_z + 0.28), stone, bevel_m=0.035,
                )
                baluster_count = max(7, min(13, round(canopy_w / 1.15)))
                for baluster_index in range(baluster_count):
                    baluster_x = -canopy_w / 2 + canopy_w * baluster_index / max(1, baluster_count - 1)
                    parts.append(add_cylinder(
                        f"Signature_PorteCochereBaluster{baluster_index:02d}",
                        0.075, 0.42, (baluster_x, balustrade_y, canopy_z + 0.52), stone, 12,
                    ))
            else:
                parts.append(add_gable_roof(
                    "Signature_PorteCocherePitchedRoof",
                    (canopy_w + 0.30, canopy_d + 0.20, 0.44),
                    (0, canopy_y, canopy_z - 0.02), mats["roof"], 0.040, "x",
                ))
                _signature_relief_box(
                    parts, "Signature_PorteCochereRidgeCap", (canopy_w + 0.42, 0.13, 0.12),
                    (0, canopy_y, canopy_z + 0.45), mats["accent"], bevel_m=0.026,
                )
            _signature_relief_box(
                parts, "Signature_PorteCochereFrontFascia", (canopy_w + 0.18, 0.22, 0.32),
                (0, front_y - canopy_d - 0.08, canopy_z - 0.04), stone, bevel_m=0.050,
            )
            for return_index, return_x in enumerate((-canopy_w / 2, canopy_w / 2)):
                _signature_relief_box(
                    parts, f"Signature_PorteCochereSideFascia{return_index:02d}",
                    (0.22, canopy_d + 0.12, 0.32),
                    (return_x, canopy_y, canopy_z - 0.04), stone, bevel_m=0.050,
                )
            column_y = front_y - canopy_d + 0.36
            shaft_h = canopy_z - 0.56
            for column_index, x in enumerate((-canopy_w * 0.41, -canopy_w * 0.14,
                                               canopy_w * 0.14, canopy_w * 0.41)):
                _signature_relief_box(
                    parts, f"Signature_PorteCocherePlinth{column_index:02d}",
                    (0.78, 0.78, 0.34), (x, column_y, 0.17),
                    stone, bevel_m=0.060,
                )
                _signature_relief_box(
                    parts, f"Signature_PorteCochereShaft{column_index:02d}",
                    (0.48, 0.48, shaft_h), (x, column_y, 0.34 + shaft_h / 2),
                    stone, bevel_m=0.075,
                )
                _signature_relief_box(
                    parts, f"Signature_PorteCochereCapital{column_index:02d}",
                    (0.70, 0.70, 0.28), (x, column_y, canopy_z - 0.31),
                    stone, bevel_m=0.055,
                )
                _signature_relief_box(
                    parts, f"Signature_PorteCochereAbacus{column_index:02d}",
                    (0.82, 0.82, 0.16), (x, column_y, canopy_z - 0.10),
                    stone, bevel_m=0.045,
                )
        else:
            _signature_relief_box(
                parts, "Signature_Canopy", (canopy_w, canopy_d, 0.16),
                (0, front_y - canopy_d / 2, canopy_z), metal, bevel_m=0.035,
            )

    if kits & {"pointed_portal", "deco_portal", "carved_portal"}:
        portal_w = min(4.2, width * 0.18)
        portal_h = min(height * 0.86, 4.4)
        if "pointed_portal" in kits:
            spring = min(height * 0.63, portal_h - 0.34)
            apex = min(height - 0.10, spring + portal_w * 0.52)
            add_pointed_arch_frame(
                parts, "Signature_PointedPortal", 0.0, front_y - 0.19,
                0.08, spring, apex, portal_w, 0.38, 0.30, stone, mats["interior_warm"],
            )
        else:
            parts.append(add_box("Signature_PortalLeft", (0.34, 0.30, portal_h),
                                 (-portal_w / 2, front_y - 0.16, portal_h / 2), stone))
            parts.append(add_box("Signature_PortalRight", (0.34, 0.30, portal_h),
                                 (portal_w / 2, front_y - 0.16, portal_h / 2), stone))
            parts.append(add_box("Signature_PortalHead", (portal_w + 0.68, 0.30, 0.42),
                                 (0, front_y - 0.16, portal_h - 0.2), stone))

    if kits & {"brick_pilasters", "heavy_masonry_piers", "rowhouse_divisions"}:
        count = max(3, min(12, round(width / 4.5)))
        for index in range(count + 1):
            x = -width / 2 + width * index / count
            pier_w = 0.34 if "heavy_masonry_piers" not in kits else 0.56
            parts.append(add_box(f"Signature_BasePier{index:02d}", (pier_w, 0.24, height * 0.96),
                                 (x, front_y - 0.13, height * 0.48), stone if "heavy_masonry_piers" in kits else mats["secondary"]))

    if "external_fire_escape" in kits:
        _add_front_fire_escape_stage(
            parts, "Signature_FireEscapePodium", width, height, front_y, mats,
            podium=True,
        )

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
    continuous_heritage_pavilion = (
        "centre_pavilion" in kits and "heritage_stone_depth" in kits
    )

    if "external_fire_escape" in kits:
        _add_front_fire_escape_stage(
            parts, f"Signature_FireEscape_{variant_key}", width, height,
            facade_y, mats, crown=crown,
        )

    if kits & {"centre_pavilion", "concrete_frame", "gothic_tower"}:
        pavilion_w = width * (
            0.24 if "gothic_tower" in kits
            else 0.18 if "centre_pavilion" in kits and "heritage_stone_depth" in kits
            else 0.30 if "centre_pavilion" in kits
            else 0.74
        )
        frame_mat = stone if kits & {"centre_pavilion", "gothic_tower"} else mats["concrete"]
        pier_w = min(0.58, pavilion_w * 0.08)
        projection = (
            1.28 if "centre_pavilion" in kits and "heritage_stone_depth" in kits
            else 0.42 if "gothic_tower" in kits
            else 0.30
        )
        if sheet_material is not None and kits & {"centre_pavilion", "gothic_tower"}:
            parts.append(add_beveled_box(
                "Signature_CentrePavilionField",
                (pavilion_w, projection + 0.12, height * 0.94),
                (0, facade_y - (projection + 0.12) / 2, height * 0.50),
                sheet_material, 0.055,
            ))
        for side, x in (("Left", -pavilion_w / 2), ("Right", pavilion_w / 2)):
            _signature_relief_box(
                parts, f"Signature_CentrePavilion{side}",
                (pier_w, projection, height * 0.99),
                (x, facade_y - projection / 2, height * 0.50),
                frame_mat, bevel_m=0.055,
            )
        # A stackable pavilion must read as one continuous projection. Boxing
        # every repeatable floor with its own head and sill produced the white
        # horizontal ladders seen in the V37 grazing-angle comparison. The
        # terminal crown keeps one modeled cornice; intermediate floor datums
        # remain in the audited PBR sheet and no longer double in geometry.
        if not continuous_heritage_pavilion or crown:
            _signature_relief_box(
                parts, "Signature_CentrePavilionHead",
                (pavilion_w + pier_w, projection, 0.20),
                (0, facade_y - projection / 2, height - 0.14),
                frame_mat, bevel_m=0.045,
            )
        if not continuous_heritage_pavilion:
            _signature_relief_box(
                parts, "Signature_CentrePavilionSill",
                (pavilion_w + pier_w, projection, 0.16),
                (0, facade_y - projection / 2, 0.12),
                frame_mat, bevel_m=0.040,
            )

    if (
        {"centre_pavilion", "corner_turret", "heritage_stone_depth"}.issubset(kits)
        and sheet_material is not None
    ):
        # Wide railway hotels need a five-part rhythm: corner / secondary /
        # centre / secondary / corner.  Repeating only the flat middle bays
        # across a 90-100 m parcel erases the landmark hierarchy even when the
        # texture is excellent.  These subordinate pavilions stay at relative
        # quarter points, carry the same atlas as the facade, and project less
        # than the entrance pavilion so the centre remains dominant.
        secondary_w = min(8.4, max(5.8, width * 0.09))
        secondary_projection = 0.78
        secondary_pier_w = min(0.46, secondary_w * 0.075)
        for pavilion_index, sign in enumerate((-1, 1)):
            pavilion_x = sign * width * 0.27
            parts.append(add_beveled_box(
                f"Signature_SecondaryPavilion{pavilion_index}_Field",
                (secondary_w, secondary_projection + 0.10, height * 0.92),
                (pavilion_x, facade_y - (secondary_projection + 0.10) / 2, height * 0.50),
                sheet_material, 0.045,
            ))
            for pier_index, pier_x in enumerate((
                pavilion_x - secondary_w / 2,
                pavilion_x + secondary_w / 2,
            )):
                _signature_relief_box(
                    parts, f"Signature_SecondaryPavilion{pavilion_index}_Pier{pier_index}",
                    (secondary_pier_w, secondary_projection + 0.08, height * 0.94),
                    (pier_x, facade_y - secondary_projection / 2 - 0.04, height * 0.50),
                    stone, bevel_m=0.045,
                )
            if crown:
                _signature_relief_box(
                    parts, f"Signature_SecondaryPavilion{pavilion_index}_Head",
                    (secondary_w + secondary_pier_w, secondary_projection + 0.08, 0.20),
                    (pavilion_x, facade_y - secondary_projection / 2 - 0.04, height - 0.13),
                    stone, bevel_m=0.04,
                )

    if "heritage_stone_depth" in kits:
        _add_heritage_stone_depth_relief(
            grammar, parts, "Signature_HeritageFloor", width, depth, height,
            facade_y, mats,
        )

    if "corner_turret" in kits:
        _add_chateau_turret_segments(
            parts, f"Signature_{variant_key.title()}Turret", width, height,
            facade_y, mats, podium=False,
        )

    if kits & {"timber_picture_frames", "recessed_balcony_columns"}:
        centres = (-width * 0.27, width * 0.27) if width > 13 else (width * 0.22,)
        frame_w = min(3.25, width * 0.22)
        # Three depth planes: cladding skin, projected timber surround, then
        # the deeper loggia slab/guard. This is the hierarchy visible in the
        # Nordic reference rather than one continuous applied grid.
        projection_depth = 0.46
        projection = facade_y - projection_depth / 2 - 0.04
        for index, x in enumerate(centres):
            _signature_relief_box(
                parts, f"Signature_TimberFrame{index}_L",
                (0.20, projection_depth, height * 0.92),
                (x - frame_w / 2, projection, height * 0.50), warm, bevel_m=0.035,
            )
            _signature_relief_box(
                parts, f"Signature_TimberFrame{index}_R",
                (0.20, projection_depth, height * 0.92),
                (x + frame_w / 2, projection, height * 0.50), warm, bevel_m=0.035,
            )
            _signature_relief_box(
                parts, f"Signature_TimberFrame{index}_Head",
                (frame_w + 0.20, projection_depth + 0.05, 0.22),
                (x, projection - 0.025, height - 0.16), warm, bevel_m=0.04,
            )
            _signature_relief_box(
                parts, f"Signature_TimberFrame{index}_Sill",
                (frame_w + 0.20, projection_depth, 0.18),
                (x, projection, 0.14), warm, bevel_m=0.032,
            )
            if "recessed_balcony_columns" in kits and not crown:
                slab_depth = 1.02
                slab_y = facade_y - slab_depth / 2
                _signature_relief_box(
                    parts, f"Signature_LoggiaSlab{index}",
                    (frame_w - 0.22, slab_depth, 0.14),
                    (x, slab_y, 0.08), warm, bevel_m=0.025,
                )
                _add_front_rail(parts, f"Signature_LoggiaRail{index}", x, frame_w - 0.36,
                                facade_y - slab_depth + 0.08, 0.12,
                                min(1.02, height * 0.34), mats)

    if kits & {"haussmann_balconies", "continuous_balcony", "eixample_balconies"}:
        should_add = typical_b or "eixample_balconies" in kits or crown
        if should_add:
            balcony_w = width * (0.92 if "eixample_balconies" not in kits else 0.86)
            slab_y = facade_y - 0.46
            _signature_relief_box(
                parts, "Signature_ContinuousBalconySlab", (balcony_w, 0.78, 0.14),
                (0, slab_y, 0.09), stone, bevel_m=0.03,
            )
            _add_front_rail(
                parts, "Signature_ContinuousBalconyRail", 0, balcony_w,
                facade_y - 0.88, 0.13, min(1.0, height * 0.34), mats,
                ornamental="haussmann_balconies" in kits or "eixample_balconies" in kits,
            )
            if "haussmann_balconies" in kits:
                side_span = depth * 0.92
                centre_y = facade_y + depth / 2
                # Side returns are Juliet-depth: enough to continue the iron
                # datum around the corner without changing the user polygon's
                # authored footprint or creating a projecting side catwalk.
                side_depth = 0.24
                for side, sign in (("L", -1), ("R", 1)):
                    _signature_relief_box(
                        parts, f"Signature_SideBalcony{side}_Slab",
                        (side_depth, side_span, 0.14),
                        (sign * (width / 2 + side_depth / 2), centre_y, 0.09),
                        stone, bevel_m=0.03,
                    )
                    _add_side_rail(
                        parts, f"Signature_SideBalcony{side}_Rail",
                        sign * (width / 2 + side_depth), centre_y, side_span,
                        0.13, min(1.0, height * 0.34), mats, ornamental=True,
                    )

    # Haussmann facades rely on small but continuous depth changes: projecting
    # sills, jambs and lintels catch light even on floors without a balcony.
    # The array is derived from the current bay count, so widening the footprint
    # adds bays instead of stretching one ornamented photograph.
    if kits & {"haussmann_balconies", "eixample_balconies"} and FACADE_SHEET_DETAIL != "city":
        facade = grammar.get("facade") or {}
        bay_count = max(3, int(facade.get("front_bay_count", round(width / 3.0))))
        bay = width / bay_count
        opening_w = min(bay * 0.48, 1.65)
        opening_h = min(height * 0.62, 2.28)
        sill_z = min(max(0.58, float(facade.get("sill_height_m", 0.72))), height - opening_h - 0.26)
        opening_cz = sill_z + opening_h / 2
        relief_depth = 0.20
        relief_y = facade_y - relief_depth / 2 - 0.035
        jamb_w = min(0.16, bay * 0.06)
        for index in range(bay_count):
            x = -width / 2 + bay * (index + 0.5)
            for side, offset in (("L", -opening_w / 2), ("R", opening_w / 2)):
                _signature_relief_box(
                    parts, f"Signature_WindowSurround{index:02d}_{side}",
                    (jamb_w, relief_depth, opening_h + 0.20),
                    (x + offset, relief_y, opening_cz), stone, bevel_m=0.022,
                )
            _signature_relief_box(
                parts, f"Signature_WindowLintel{index:02d}",
                (opening_w + jamb_w, relief_depth + 0.03, 0.16),
                (x, relief_y - 0.015, sill_z + opening_h + 0.08), stone, bevel_m=0.026,
            )
            _signature_relief_box(
                parts, f"Signature_WindowSill{index:02d}",
                (opening_w + 0.18, relief_depth + 0.09, 0.13),
                (x, relief_y - 0.045, sill_z - 0.045), stone, bevel_m=0.022,
            )

    # The corner return is silhouette-critical and therefore cannot disappear
    # from the city LOD with the per-window relief above.
    if "haussmann_balconies" in kits:
        _add_haussmann_corner_returns(
            parts, "Signature_FloorCorner", width, depth, height, facade_y, mats,
        )

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
        pier_mat = (
            mats["primary"] if "brick_pilasters" in kits
            else metal if "vertical_fins" in kits
            else stone
        )
        for index in range(count + 1):
            x = -width / 2 + width * index / count
            parts.append(add_box(f"Signature_VerticalPier{index:02d}", (pier_w, projection, height * 0.96),
                                 (x, facade_y - projection / 2, height * 0.50),
                                 pier_mat))

    if "monumental_turbine_windows" in kits:
        count = max(4, min(8, round(width / 6.0)))
        for index in range(count + 1):
            x = -width / 2 + width * index / count
            _signature_relief_box(
                parts, f"Signature_TurbinePier{index:02d}",
                (0.46, 0.52, height * 0.98),
                (x, facade_y - 0.28, height * 0.50), mats["primary"], bevel_m=0.055,
            )
        # Keep a single recessed steel datum per stackable storey; the atlas and
        # glazing mask carry the finer Crittall grid.
        _signature_relief_box(
            parts, "Signature_TurbineTransom", (width * 0.97, 0.34, 0.16),
            (0, facade_y - 0.22, height - 0.16), metal, bevel_m=0.025,
        )
        # A projecting brick sill and a slimmer mid-height steel rail complete
        # the turbine-hall section. These align at every LEGO storey boundary
        # and keep the tall glazing legible as construction, not a photograph.
        _signature_relief_box(
            parts, "Signature_TurbineSill", (width * 0.97, 0.42, 0.18),
            (0, facade_y - 0.23, 0.13), mats["primary"], bevel_m=0.030,
        )
        _signature_relief_box(
            parts, "Signature_TurbineMidRail", (width * 0.965, 0.24, 0.105),
            (0, facade_y - 0.19, height * 0.51), metal, bevel_m=0.018,
        )

    if "corten_insertion" in kits:
        insert_w = min(5.4, width * 0.18)
        insert_x = -width / 2 + insert_w / 2 + 0.24
        corten = mats["signature_warm"]
        _signature_relief_box(
            parts, f"Signature_Corten_{variant_key}",
            (insert_w, 0.74, height * 0.96),
            (insert_x, facade_y - 0.38, height * 0.50), corten, bevel_m=0.10,
        )

    if "expressed_concrete_frame" in kits:
        # A pale precast frame projects in front of the dark brick and turns the
        # corner by a real 0.8 m. Intermediate floors keep only verticals; the
        # podium and crown terminate the frame so LEGO stacking stays seamless.
        count = max(4, min(8, round(width / 4.6)))
        for index in range(count + 1):
            x = -width / 2 + width * index / count
            _signature_relief_box(
                parts, f"Signature_PrecastPier{index:02d}",
                (0.34, 0.48, height * 0.98),
                (x, facade_y - 0.26, height * 0.50), stone, bevel_m=0.060,
            )
        if crown:
            _signature_relief_box(
                parts, "Signature_PrecastCrownBeam", (width + 0.28, 0.52, 0.34),
                (0, facade_y - 0.28, height - 0.20), stone, bevel_m=0.060,
            )
        for side_index, sign in enumerate((-1, 1)):
            _signature_relief_box(
                parts, f"Signature_PrecastCornerReturn{side_index}",
                (0.48, 1.60, height * 0.98),
                (sign * (width / 2 + 0.03), facade_y + 0.54, height * 0.50),
                stone, bevel_m=0.060,
            )

    if kits & {"brise_soleil", "curtainwall_fins", "timber_lattice"}:
        count = max(8, min(28, round(width / (0.72 if "timber_lattice" in kits else 1.25))))
        # Terracotta screens are ceramic architectural elements, not dark
        # curtain-wall mullions.  Giving every generated fin the generic metal
        # material made the render-locked terracotta office read as a black cage.
        # The target-specific accent carries the same warm fired-clay language
        # as the audited facade atlas while ordinary curtain walls remain metal.
        render_target_id = str(((FACADE_SHEET or {}).get("manifest", {})).get("render_target_id") or "")
        terracotta_screen = render_target_id.endswith(":glass_office_terracotta_fins")
        fin_mat = warm if "timber_lattice" in kits else (mats["accent"] if terracotta_screen else metal)
        for index in range(count + 1):
            x = -width / 2 + width * index / count
            if "brise_soleil" in kits:
                fin_depth = 0.48
            elif "curtainwall_fins" in kits:
                fin_depth = 0.24 if index % 3 else 0.42
            else:
                fin_depth = 0.30
            _signature_relief_box(
                parts, f"Signature_ScreenFin{index:02d}",
                (0.075 if "curtainwall_fins" in kits else 0.07, fin_depth, height * 0.84),
                (x, facade_y - fin_depth / 2 - 0.04, height * 0.52), fin_mat,
                bevel_m=0.014,
            )
        if "curtainwall_fins" in kits:
            for suffix, z in (("Sill", 0.10), ("Head", height - 0.10)):
                _signature_relief_box(
                    parts, f"Signature_CurtainWall{suffix}",
                    (width + 0.10, 0.24, 0.12),
                    (0, facade_y - 0.12, z), metal, bevel_m=0.022,
                )
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

    if "mill_chimney" in kits:
        chimney_h = max(1.85, height * 1.65)
        chimney_x, chimney_y = width * 0.32, depth * 0.08
        _signature_relief_box(
            parts, "Signature_MillChimneyStack", (0.92, 0.86, chimney_h),
            (chimney_x, chimney_y, chimney_h / 2), mats["primary"], bevel_m=0.035,
        )
        for course_index, (course_scale, z) in enumerate((
            (1.10, chimney_h - 0.38),
            (1.22, chimney_h - 0.22),
            (1.32, chimney_h - 0.07),
        )):
            _signature_relief_box(
                parts, f"Signature_MillChimneyCourse{course_index}",
                (0.92 * course_scale, 0.86 * course_scale, 0.12),
                (chimney_x, chimney_y, z), mats["primary"], bevel_m=0.025,
            )
        parts.append(add_beveled_box(
            "Signature_MillChimneyCap", (1.32, 1.24, 0.15),
            (chimney_x, chimney_y, chimney_h + 0.03), mats["accent"], 0.025,
        ))

    if kits & {"roof_pergola"}:
        top_z = min(height - 0.08, 2.25)
        span_x, span_y = width * 0.58, depth * 0.46
        for column_index, (x, y) in enumerate((
            (-span_x / 2, -span_y / 2), (span_x / 2, -span_y / 2),
            (-span_x / 2, span_y / 2), (span_x / 2, span_y / 2),
        )):
            _signature_relief_box(
                parts, f"Signature_PergolaColumn{column_index}", (0.16, 0.16, top_z),
                (x, y, top_z / 2), metal, bevel_m=0.025,
            )
        for beam_index, y in enumerate((-span_y / 2, span_y / 2)):
            _signature_relief_box(
                parts, f"Signature_PergolaEdgeBeam{beam_index}",
                (span_x + 0.22, 0.18, 0.20), (0, y, top_z), metal, bevel_m=0.025,
            )
        for slat_index in range(11):
            x = -span_x / 2 + span_x * slat_index / 10
            _signature_relief_box(
                parts, f"Signature_PergolaTimberSlat{slat_index:02d}",
                (0.10, span_y + 0.34, 0.12), (x, 0, top_z + 0.05), warm, bevel_m=0.018,
            )

    if "roof_terrace_planting" in kits:
        planter_y = depth * 0.30
        for index, x in enumerate((-width * 0.26, -width * 0.08, width * 0.18, width * 0.34)):
            _signature_relief_box(
                parts, f"Signature_RoofPlanter{index:02d}",
                (min(3.2, width * 0.13), 0.72, 0.46),
                (x, planter_y, 0.31), stone, bevel_m=0.055,
            )
            parts.append(add_cylinder(
                f"Signature_RoofPlant{index:02d}", 0.42, 0.72,
                (x, planter_y, 0.88), mats["green_roof"], 16,
            ))

    if "barrel_vault_roof" in kits:
        vault_count = 4
        vault_span = width / vault_count + 0.08
        # Industrial barrel roofs are shallow elliptical shells, not four
        # attached Quonset huts.  Keep their spring below the parapet and their
        # rise near one fifth of the bay span, as in the brewery oblique views.
        rise = min(height - 0.42, vault_span * 0.22)
        for index in range(vault_count):
            x = -width / 2 + width * (index + 0.5) / vault_count
            parts.append(add_barrel_vault(
                f"Signature_BarrelVault{index:02d}", vault_span, depth * 0.96,
                rise, (x, 0, 0.28), mats["roof"], 0.11, 18,
            ))
            for rib_index, y in enumerate((-depth * 0.34, -depth * 0.12, depth * 0.12, depth * 0.34)):
                parts.append(add_barrel_vault(
                    f"Signature_BarrelVault{index:02d}_Rib{rib_index}",
                    vault_span + 0.08, 0.10, rise + 0.05, (x, y, 0.27), metal, 0.08, 18,
                ))

    if "barrel_vault_clerestory" in kits:
        clerestory_w = min(width * 0.24, 8.2)
        clerestory_h = min(height * 0.42, 1.75)
        _signature_relief_box(
            parts, "Signature_BreweryClerestoryCore",
            (clerestory_w, depth * 0.58, clerestory_h),
            (0, 0, 0.36 + clerestory_h / 2), mats["glass"], bevel_m=0.045,
        )
        parts.append(add_barrel_vault(
            "Signature_BreweryClerestoryCap", clerestory_w + 0.18,
            depth * 0.60, min(height * 0.25, 1.25),
            (0, 0, 0.36 + clerestory_h), mats["roof"], 0.09, 16,
        ))

    if "glass_turbine_lantern" in kits:
        lantern_w, lantern_d = width * 0.86, depth * 0.64
        wall_h = min(height * 0.44, 1.65)
        roof_h = min(height * 0.42, 1.55)
        _signature_relief_box(
            parts, "Signature_TurbineLanternGlass",
            (lantern_w, lantern_d, wall_h), (0, 0, 0.34 + wall_h / 2),
            mats["glass"], bevel_m=0.035,
        )
        parts.append(add_gable_roof(
            "Signature_TurbineLanternGable", (lantern_w + 0.16, lantern_d + 0.16, roof_h),
            (0, 0, 0.34 + wall_h), mats["glass"], 0.025, "x",
        ))
        eave_z = 0.34 + wall_h
        half_run = (lantern_d + 0.16) / 2
        slope_length = math.sqrt(half_run * half_run + roof_h * roof_h)
        slope_angle = math.atan2(roof_h, half_run)
        for rib_index in range(9):
            x = -lantern_w / 2 + lantern_w * rib_index / 8
            for slope_index, sign in enumerate((-1, 1)):
                rib = add_beveled_box(
                    f"Signature_TurbineLanternRib{rib_index:02d}_{slope_index}",
                    (0.10, slope_length + 0.08, 0.10),
                    (x, sign * half_run / 2, eave_z + roof_h / 2), metal, 0.018,
                )
                rib.rotation_euler.x = sign * slope_angle
                parts.append(rib)
        _signature_relief_box(
            parts, "Signature_TurbineLanternRidge",
            (lantern_w + 0.24, 0.14, 0.14),
            (0, 0, eave_z + roof_h), metal, bevel_m=0.025,
        )

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

    if (
        kits & {"deep_eaves", "tile_eaves", "slim_eaves", "deep_cornice", "civic_cornice", "pressed_metal_cornice", "bracketed_cornice", "corbelled_cornice"}
        and "roof_monitor" not in kits
    ):
        mat = warm if kits & {"deep_eaves", "tile_eaves"} else stone
        _signature_relief_box(
            parts, "Signature_RoofEdge",
            (width + 0.56, depth + 0.48, min(0.22, height * 0.18)),
            (0, 0, min(height - 0.11, 0.24)), mat, bevel_m=0.045,
        )

    if kits & {"corner_turret"}:
        # Chateauesque turrets are cylindrical masonry towers with tall copper
        # cones, not square pyramid caps. Align these centres with the stacked
        # podium/floor turret segments so the landmark is continuous at every
        # supported floor count.
        total_h = min(height * 0.96, 5.85)
        radius = min(2.15, max(1.55, width * 0.024))
        drum_h = min(1.48, total_h * 0.30)
        cap_h = max(1.8, total_h - drum_h - 0.10)
        centre_y = -depth / 2 + radius * 0.34
        for index, sign in enumerate((-1, 1)):
            x = sign * (width / 2 - radius * 0.98)
            parts.append(add_cylinder(
                f"Signature_RoofTurret{index}_Drum", radius, drum_h,
                (x, centre_y, drum_h / 2), stone, 32,
            ))
            parts.append(add_cylinder(
                f"Signature_RoofTurret{index}_Cornice", radius + 0.16, 0.18,
                (x, centre_y, drum_h - 0.09), stone, 32,
            ))
            parts.append(add_cone(
                f"Signature_RoofTurret{index}_CopperCone", radius + 0.10, cap_h,
                (x, centre_y, drum_h + cap_h / 2 - 0.02), mats["roof"], 40,
            ))
            parts.append(add_cylinder(
                f"Signature_RoofTurret{index}_Finial", 0.055, 0.34,
                (x, centre_y, drum_h + cap_h + 0.15), metal, 12,
            ))


def _add_modular_glazing_overlays(
    grammar: dict,
    parts: list,
    mats: dict,
    *,
    role: str,
    width: float,
    depth: float,
    height: float,
    centre_y: float,
    facade_y: float,
) -> None:
    if f"glass_overlay_{role}" not in mats or f"sheet_near_{role}" not in mats:
        return
    facade = grammar["facade"]
    heritage_stone = facade.get("system") == "heritage_stone"
    heritage_depth = heritage_stone and "heritage_stone_depth" in _signature_kits(grammar)
    band_payload = ((FACADE_SHEET or {}).get("manifest", {}).get("bands", {}).get(role) or {})
    audited_openings = bool(band_payload.get("audited_openings"))
    # City-scale delivery uses the shadow-neutral baked glass in the 1K far
    # atlas. Close/hero delivery replaces those pixels with recessed physical
    # glazing, occupied room cards and stone returns on all four elevations.
    # Heritage landmarks use a bounded hybrid: the whole near sheet receives
    # correctly recessed physical glass, while real returns/caps are reserved
    # for a representative front set. This preserves grazing-angle depth at a
    # 90 m parcel width without making each resizable module take ten minutes.
    city_profile = FACADE_SHEET_DETAIL == "city"
    city_hybrid = city_profile and heritage_depth
    has_semantic_masks = facade_mask_paths(role) is not None
    if not has_semantic_masks:
        return
    # Large retail openings already carry their dressed-stone surrounds in the
    # unique podium atlas. Geometry-derived returns around those masks became
    # giant grey cages; retain true returns only for upper punched windows.
    stone_returns = heritage_stone and role != "podium"
    front_columns = max(1, int(facade.get("front_bay_count", 4)))
    profile_name = str(mats["glass_profile_name"])
    profile = glass_profile(profile_name)
    # City Prompt previously omitted this assembly entirely for non-heritage
    # families, so even a 4K PBR facade still read as a printed cardboard skin.
    # Keep a bounded semantic opening set in the city delivery: real facade
    # returns, a recessed pane, a slim sash and an occupied room plane.  The
    # cap is driven by the archetype's construction depth, not a fixed visual
    # offset, so industrial sash can sit much deeper than curtain wall glass.
    pane_recess = max(
        float(profile["pane_recess_m"]),
        min(0.30, float(facade.get("window_recess_m", profile["pane_recess_m"]))),
    )
    frame_depth = max(
        float(profile["frame_depth_m"]),
        min(0.30, float(facade.get("frame_depth_m", profile["frame_depth_m"]))),
    )
    return_material_key = "signature_stone" if heritage_depth else "primary"
    _glazing_overlay_segment(parts, {
        "id": f"Module_{role}_FrontGlazing",
        "axis": "front",
        "centre": [0.0, facade_y - 0.0225, height / 2],
        "span_m": width,
        "height_m": height,
        "columns": front_columns,
        "rows": 1,
        "band": role,
        "glass_profile": profile_name,
        # 45–55 mm is a believable exposed steel/aluminium sightline.  The
        # former 95 mm cap proved visually heavy in City Prompt close-ups and
        # made real recess geometry read like a black picture frame.
        "profile_m": 0.052 if not heritage_depth else 0.085,
        "stone_returns": stone_returns,
        "opening_returns": True,
        "return_material_key": return_material_key,
        "projecting_sills": role != "podium",
        "depth_mullions": role != "podium",
        "frame_mode": (
            # Audited atlases already contain registered steel/wood sash at
            # the glazing plane. A second outer perimeter duplicates that
            # frame and reads as a heavy black picture box, but relying on the
            # atlas for every fine bar leaves the window flat at grazing
            # angles. ``sash_relief`` therefore adds only slim, registered
            # mullions/transoms at the recessed pane while the atlas retains
            # its fine colour/weathering variation.
            "sash_relief" if audited_openings and not heritage_depth else
            "region_caps" if heritage_depth else
            "mask_only" if heritage_stone else "region_caps"
        ),
        "cap_material_key": "signature_stone" if heritage_depth else "glazing_frame",
        "frame_depth_m": 0.28 if heritage_depth else frame_depth,
        "repeat_span_m": float(FACADE_SHEET["manifest"].get("span_m", width)),
        "cavity_depth_m": 0.54 if stone_returns else max(0.42, pane_recess + 0.22),
        "pane_recess_m": 0.24 if stone_returns else pane_recess,
        "max_regions": 18 if city_profile else 0,
        "surface_only": city_hybrid and role == "podium" and not audited_openings,
        "window_region_filter": heritage_depth and not audited_openings,
        # Audited bands have tightly registered opaque/glass masks. They can
        # afford the complete near facade, recessed transmission plane and
        # occupied room cards even in the city profile; legacy auto-masks keep
        # the bounded geometry-only hybrid until their openings are audited.
        "geometry_only": city_hybrid and not audited_openings,
        "interior_cards": audited_openings or not city_hybrid,
        "skip_near_facade": audited_openings,
    }, mats)
    # The hero profile continues the same physical construction on side/rear
    # elevations so an orbit camera never reveals placeholder windows.
    side_columns, _ = _bays(depth * 0.9, facade["bay_width_m"])
    side_role = (
        "side"
        if facade_mask_paths("side") is not None and "glass_overlay_side" in mats
        else role
    )
    side_band_payload = (
        ((FACADE_SHEET or {}).get("manifest", {}).get("bands", {}).get(side_role) or {})
    )
    side_repeat_span = float(
        side_band_payload.get("span_m")
        or (FACADE_SHEET or {}).get("manifest", {}).get("span_m", width)
    )
    side_specs = (
        ("left", [-width / 2 - 0.0225, centre_y, height / 2], depth),
        ("right", [width / 2 + 0.0225, centre_y, height / 2], depth),
        ("rear", [0.0, centre_y + depth / 2 + 0.0225, height / 2], width),
    )
    for axis, centre, span in side_specs:
        _glazing_overlay_segment(parts, {
            "id": f"Module_{role}_{axis.title()}Glazing",
            "axis": axis,
            "centre": centre,
            "span_m": span,
            "height_m": height,
            "columns": side_columns if axis in ("left", "right") else front_columns,
            "rows": 1,
            "band": side_role,
            "glass_profile": profile_name,
            "profile_m": 0.048 if not heritage_depth else 0.075,
            "flip_u": axis == "left",
            "stone_returns": stone_returns,
            "opening_returns": True,
            "return_material_key": return_material_key,
            "projecting_sills": role != "podium",
            "depth_mullions": role != "podium",
            "frame_mode": (
                "sash_relief" if audited_openings and not heritage_depth else
                "region_caps" if heritage_depth else
                "mask_only" if heritage_stone else "region_caps"
            ),
            "cap_material_key": "signature_stone" if heritage_depth else "glazing_frame",
            "frame_depth_m": 0.28 if heritage_depth else frame_depth,
            "repeat_span_m": side_repeat_span,
            "cavity_depth_m": 0.54 if stone_returns else max(0.42, pane_recess + 0.22),
            "pane_recess_m": 0.24 if stone_returns else pane_recess,
            "max_regions": 8 if city_profile else 0,
            # At city detail the audited physical stack is reserved for the
            # principal elevation. Wrapped PBR sheets keep side/rear views in
            # the same material language without quadrupling every module's
            # opening geometry on a 90 m resizable frontage.
            "surface_only": city_hybrid,
            "window_region_filter": heritage_depth and not audited_openings,
            # Side and rear elevations keep real frame/return/sill relief in
            # the delivery GLB, but reuse the baked glazing already in their
            # wrapped atlas. This avoids three more transmissive material
            # stacks per module while retaining the oblique-view depth cue.
            "geometry_only": city_profile,
            "interior_cards": not city_profile,
        }, mats)


def build_facade_sheet_podium(grammar: dict, mats: dict) -> bpy.types.Object:
    """Hybrid podium: photo elevation in front, conventional PBR construction elsewhere."""
    dims, facade, massing = grammar["dimensions"], grammar["facade"], grammar["massing"]
    width, depth, height = dims["width_m"], dims["depth_m"], dims["podium_height_m"]
    front_y = -depth / 2
    rooftop_pavilion = _has_rooftop_pavilion(grammar)
    heritage_depth = (
        facade.get("system") == "heritage_stone"
        and "heritage_stone_depth" in _signature_kits(grammar)
    )
    podium_band = ((FACADE_SHEET or {}).get("manifest", {}).get("bands", {}).get("podium") or {})
    audited_openings = bool(podium_band.get("audited_openings"))
    semantic_openings = facade_mask_paths("podium") is not None
    depth_openings = semantic_openings and FACADE_SHEET_DETAIL in {"city", "hero"}
    front_cavity = min(0.78, max(0.46, depth * 0.08)) if depth_openings else 0.0
    core_depth = max(0.25, depth - front_cavity)
    core_centre_y = front_cavity / 2
    front_sheet_material = (
        mats.get("sheet_near_podium", mats["sheet_podium"])
        if depth_openings else mats["sheet_podium"]
    )
    # End-bay signs and loading entrances are street-address identity elements,
    # not a wallpaper pattern. Side/rear walls reuse a related window-only band
    # so they remain detailed without duplicating the sign or front door.
    side_band_payload = ((FACADE_SHEET or {}).get("manifest", {}).get("bands", {}).get("side") or {})
    side_sheet_available = "sheet_side" in mats
    side_repeat_span = float(side_band_payload.get("span_m") or FACADE_SHEET["manifest"].get("span_m", width))
    fixed_loading_wrap = "fixed_loading_bay" in _signature_kits(grammar) and not side_sheet_available
    wrapped_podium_source = (
        mats["sheet_side"] if side_sheet_available else
        mats.get("sheet_floor", mats["sheet_podium"])
        if fixed_loading_wrap else mats["sheet_podium"]
    )
    wrapped_podium_scale = 0.72 if fixed_loading_wrap else 1.0
    left_sheet_material = wrapped_facade_material(
        wrapped_podium_source, "podium", "left",
        offset_u=0.02 if fixed_loading_wrap else 0.17, scale_u=wrapped_podium_scale,
        span_m=side_repeat_span if side_sheet_available else None,
        flip_u=not fixed_loading_wrap,
    )
    right_sheet_material = wrapped_facade_material(
        wrapped_podium_source, "podium", "right",
        offset_u=0.02 if fixed_loading_wrap else 0.43,
        scale_u=wrapped_podium_scale,
        span_m=side_repeat_span if side_sheet_available else None,
    )
    rear_sheet_material = wrapped_facade_material(
        wrapped_podium_source, "podium", "rear",
        offset_u=0.02 if fixed_loading_wrap else 0.71,
        scale_u=wrapped_podium_scale,
        span_m=side_repeat_span if side_sheet_available else None,
        flip_u=not fixed_loading_wrap,
    )
    datum_material = mats["signature_stone"] if heritage_depth else mats["concrete"]
    head_material = mats["signature_stone"] if heritage_depth else mats["secondary"]
    parts: list = [
        # Audited physical glazing needs a real wall cavity. The old core ran
        # flush to the facade and sat in front of the glass/backplate, which
        # made every opening render as an opaque white panel in City Prompt.
        add_box("SheetPodium_Core", (width, core_depth, height),
                (0, core_centre_y, height / 2), mats["primary"]),
        add_box("SheetPodium_FrontAtlas", (width, 0.045, height),
                (0, front_y - 0.0225, height / 2), front_sheet_material),
        add_box("SheetPodium_Plinth", (width + 0.14, depth + 0.12, 0.24),
                (0, 0, 0.12), datum_material),
        add_box("SheetPodium_HeadCourse", (width + 0.24, depth + 0.18, 0.18),
                (0, 0, height - 0.09), head_material),
    ]
    parts.extend([
        add_box("SheetPodium_LeftAtlas", (0.045, depth, height),
                (-width / 2 - 0.0225, 0, height / 2), left_sheet_material),
        add_box("SheetPodium_RightAtlas", (0.045, depth, height),
                (width / 2 + 0.0225, 0, height / 2), right_sheet_material),
        add_box("SheetPodium_RearAtlas", (width, 0.045, height),
                (0, depth / 2 + 0.0225, height / 2), rear_sheet_material),
    ])
    fixed_entrance_material = None
    fixed_entrance_width = 0.0
    render_target_id = str(((FACADE_SHEET or {}).get("manifest", {})).get("render_target_id") or "")
    if "sheet_entrance" in mats and (
        "centre_pavilion" in _signature_kits(grammar) or render_target_id
    ):
        # The full source elevation contains one ceremonial portal. Keep that
        # identity atlas fixed at the building centre while the window-only
        # podium strip repeats behind it as the user's polygon grows.
        fixed_entrance_width = min(14.0, max(8.8, width * 0.16))
        fixed_entrance_material = mats["sheet_entrance"].copy()
        fixed_entrance_material.name = "MAT_Sheet_Fixed_CentralEntrance"
        fixed_entrance_material["facade_sheet_role"] = "entrance"
        fixed_entrance_material["facade_uv"] = True
        parts.append(add_beveled_box(
            "SheetPodium_FixedCentralEntrance",
            (fixed_entrance_width, 0.24, height * 0.985),
            (0, front_y - 0.12, height * 0.50),
            fixed_entrance_material, 0.055,
        ))
        for pier_index, pier_x in enumerate((-fixed_entrance_width / 2, fixed_entrance_width / 2)):
            _signature_relief_box(
                parts, f"SheetPodium_FixedEntrancePier{pier_index}",
                (0.34, 0.34, height * 0.96),
                (pier_x, front_y - 0.19, height * 0.49),
                datum_material, bevel_m=0.045,
            )
        _signature_relief_box(
            parts, "SheetPodium_FixedEntranceCornice",
            (fixed_entrance_width + 0.46, 0.38, 0.22),
            (0, front_y - 0.19, height - 0.15),
            datum_material, bevel_m=0.05,
        )
    # A real canopy is worth retaining: it provides the street-level shadow and
    # silhouette that a flat photograph cannot cast in City Prompt.
    suppress_sheet_canopy = render_target_id.endswith((
        ":contemporary_midrise_variant_brick_bronze",
        ":glass_office_terracotta_fins",
    ))
    if (
        massing.get("has_podium_retail")
        and facade.get("system") != "heritage_stone"
        and not suppress_sheet_canopy
        and not audited_openings
    ):
        # Adaptive-reuse industrial blocks use a continuous, slender steel
        # canopy instead of the former small central awning. It supplies the
        # strong street-level datum and shadow visible in the render while the
        # atlas carries the individual storefronts behind it.
        canopy_width = width * 0.94 if rooftop_pavilion else min(width * 0.46, 15.0)
        canopy_depth = 1.65 if rooftop_pavilion else 1.15
        canopy_z = min(height - 0.46, 3.38 if rooftop_pavilion else 3.15)
        canopy = add_beveled_box(
            "SheetPodium_ContinuousSteelCanopy" if rooftop_pavilion else "SheetPodium_EntranceCanopy",
            (canopy_width, canopy_depth, 0.16 if rooftop_pavilion else 0.13),
            (0, front_y - canopy_depth / 2, canopy_z), mats["accent"], 0.035,
        )
        parts.append(canopy)
        if rooftop_pavilion:
            for rod_index, x in enumerate((-canopy_width * 0.42, -canopy_width * 0.21, 0.0,
                                           canopy_width * 0.21, canopy_width * 0.42)):
                parts.append(add_cylinder(
                    f"SheetPodium_CanopyTie{rod_index}", 0.025, 0.78,
                    (x, front_y - canopy_depth * 0.55, canopy_z + 0.43), mats["accent"], 8,
                ))
    # A registered, audited podium atlas already contains the archetype's exact
    # entrance and storefront proportions.  Generic portals and canopies must
    # not be layered over it: doing so replaces a rectangular industrial door
    # with an unrelated arch and makes the render-locked facade read as a kit of
    # mismatched parts.  Legacy/un-audited sheets retain the fallback expression.
    if (
        facade.get("system") != "heritage_stone"
        and not rooftop_pavilion
        and not audited_openings
    ):
        add_entry_expression(parts, facade.get("entrance_type", "canopy"), width, depth, height, mats)
    _add_modular_glazing_overlays(
        grammar, parts, mats, role="podium", width=width, depth=depth,
        height=height, centre_y=0.0, facade_y=front_y,
    )

    # Side/rear detail is carried by the same wrapped atlas and physical
    # glazing assembly as the front; no generic overlay windows are added.
    _add_signature_podium_details(grammar, parts, width, depth, height, mats)
    module = join_as("MOD_Podium", parts)
    apply_facade_sheet_uv(module, FACADE_SHEET["manifest"]["span_m"], height)
    if fixed_entrance_material is not None:
        apply_fixed_front_atlas_uv(
            module, fixed_entrance_material,
            centre_x=0.0, span_m=fixed_entrance_width, height_m=height,
        )
    return module


def build_facade_sheet_floor(
    grammar: dict,
    mats: dict,
    variant_key: str = "typical_a",
    interior_seed: int = 0,
) -> bpy.types.Object:
    """Hybrid repeatable floor with a photographed hero facade and 3D silhouette detail."""
    dims, facade, massing = grammar["dimensions"], grammar["facade"], grammar["massing"]
    render_target_id = str(((FACADE_SHEET or {}).get("manifest", {})).get("render_target_id") or "")
    suppress_generic_balconies = render_target_id.endswith((
        ":contemporary_midrise_variant_brick_bronze",
        ":glass_office_terracotta_fins",
        ":victorian_heritage_second_empire",
    ))
    openings, attachment_specs, bay_specs, variants = _graph_lookup(grammar)
    variant = variants.get(variant_key) or variants.get("typical_a") or {}
    setback = variant_key == "upper"
    crown = variant_key == "crown"
    rooftop_pavilion = _has_rooftop_pavilion(grammar)
    height = (
        dims["setback_height_m"] if setback
        else dims.get("crown_height_m", dims["floor_height_m"]) if crown
        else dims["floor_height_m"]
    )
    full_width, full_depth = dims["width_m"], dims["depth_m"]
    if setback:
        inset_front = max(float(massing.get("setback_front_m", 0.0)), 0.8)
        inset_side = max(float(massing.get("setback_side_m", 0.0)), 0.45)
    elif crown:
        # The fixed crown is the contemporary glass pavilion. Give it the
        # catalogue setback on the street and both sides, leaving the full roof
        # plate below as an occupiable planted terrace.
        if rooftop_pavilion:
            inset_front = max(float(massing.get("setback_front_m", 0.0)), 1.6)
            inset_side = max(float(massing.get("setback_side_m", 0.0)), 0.9)
        else:
            inset_front, inset_side = 0.35, 0.2
    else:
        inset_front = inset_side = 0.0
    width = full_width - inset_side * 2
    depth = full_depth - inset_front
    centre_y = inset_front / 2
    facade_y = centre_y - depth / 2
    system = facade.get("system", "regular")
    heritage_depth = system == "heritage_stone" and "heritage_stone_depth" in _signature_kits(grammar)
    shell_material = mats["secondary"] if setback or (crown and rooftop_pavilion) else mats["primary"]
    signature_rooftop_addition = bool(
        setback
        and rooftop_pavilion
        and "sheet_crown" in mats
    )
    if (crown or signature_rooftop_addition) and "sheet_crown" in mats:
        sheet_material = mats["sheet_crown"]
    elif variant_key == "typical_c" and "sheet_floor_c" in mats:
        sheet_material = mats["sheet_floor_c"]
    elif variant_key == "typical_b" and "sheet_floor_alt" in mats:
        sheet_material = mats["sheet_floor_alt"]
    else:
        sheet_material = mats["sheet_floor"]
    glazing_role = (
        "crown" if crown or signature_rooftop_addition else
        "floor_alt" if variant_key == "typical_b" else
        "floor_c" if variant_key == "typical_c" else
        "floor"
    )
    if (
        f"sheet_{glazing_role}" not in mats
        or facade_mask_paths(glazing_role) is None
    ):
        # A third middle-bay variant is always emitted by the LEGO contract,
        # but older facade sheets only author floor/floor_alt. Reuse the base
        # strip's semantic openings instead of silently flattening typical_c.
        glazing_role = "floor"
    band_payload = ((FACADE_SHEET or {}).get("manifest", {}).get("bands", {}).get(glazing_role) or {})
    audited_openings = bool(band_payload.get("audited_openings"))
    audited_brick_bays = audited_openings and system == "brick_bays"
    semantic_openings = facade_mask_paths(glazing_role) is not None
    depth_openings = semantic_openings and FACADE_SHEET_DETAIL in {"city", "hero"}
    front_cavity = min(0.78, max(0.46, depth * 0.08)) if depth_openings else 0.0
    core_depth = max(0.25, depth - front_cavity)
    core_centre_y = centre_y + front_cavity / 2
    front_sheet_material = (
        mats.get(f"sheet_near_{glazing_role}", sheet_material)
        if depth_openings else sheet_material
    )
    wrapped_candidates = [
        mats[key] for key in ("sheet_floor", "sheet_floor_alt", "sheet_floor_c")
        if key in mats
    ]
    side_band_payload = ((FACADE_SHEET or {}).get("manifest", {}).get("bands", {}).get("side") or {})
    side_sheet_available = "sheet_side" in mats
    side_repeat_span = float(side_band_payload.get("span_m") or FACADE_SHEET["manifest"].get("span_m", width))
    if side_sheet_available:
        wrapped_candidates = [mats["sheet_side"]]
    elif crown or signature_rooftop_addition:
        if "fixed_loading_bay" in _signature_kits(grammar):
            wrapped_candidates = [
                mats[key] for key in ("sheet_floor", "sheet_floor_alt") if key in mats
            ] or [sheet_material]
        else:
            wrapped_candidates = [mats.get("sheet_crown", sheet_material)]
    if not wrapped_candidates:
        wrapped_candidates = [sheet_material]
    try:
        wrapped_start = wrapped_candidates.index(sheet_material)
    except ValueError:
        wrapped_start = 0

    def wrapped_source(step: int):
        return wrapped_candidates[(wrapped_start + step) % len(wrapped_candidates)]

    fixed_loading_wrap = "fixed_loading_bay" in _signature_kits(grammar) and not side_sheet_available
    wrapped_floor_scale = 0.72 if fixed_loading_wrap else 1.0
    left_sheet_material = wrapped_facade_material(
        wrapped_source(1), glazing_role, "left",
        offset_u=0.02 if fixed_loading_wrap else 0.17,
        scale_u=wrapped_floor_scale,
        span_m=side_repeat_span if side_sheet_available else None,
        flip_u=not fixed_loading_wrap,
    )
    right_sheet_material = wrapped_facade_material(
        wrapped_source(2), glazing_role, "right",
        offset_u=0.02 if fixed_loading_wrap else 0.43,
        scale_u=wrapped_floor_scale,
        span_m=side_repeat_span if side_sheet_available else None,
    )
    rear_sheet_material = wrapped_facade_material(
        wrapped_source(3), glazing_role, "rear",
        offset_u=0.02 if fixed_loading_wrap else 0.71,
        scale_u=wrapped_floor_scale,
        span_m=side_repeat_span if side_sheet_available else None,
        flip_u=not fixed_loading_wrap,
    )
    parts: list = [
        add_box("SheetFloor_Core", (width, core_depth, height),
                (0, core_centre_y, height / 2), shell_material),
        add_box("SheetFloor_FrontAtlas", (width, 0.045, height),
                (0, facade_y - 0.0225, height / 2), front_sheet_material),
        add_box(
            "SheetFloor_SlabEdge",
            (
                width + (0.02 if audited_brick_bays else 0.0 if audited_openings and heritage_depth else 0.16 if heritage_depth else 0.10),
                depth + (0.02 if audited_brick_bays else 0.0 if audited_openings and heritage_depth else 0.14 if heritage_depth else 0.08),
                0.08 if audited_brick_bays else 0.08 if audited_openings and heritage_depth else 0.11 if heritage_depth else 0.16,
            ),
            (
                0, centre_y,
                0.04 if audited_brick_bays or (audited_openings and heritage_depth) else 0.055 if heritage_depth else 0.08,
            ),
            mats["primary"] if audited_brick_bays else mats["signature_stone"] if heritage_depth else mats["concrete"],
        ),
    ]
    parts.extend([
        add_box("SheetFloor_LeftAtlas", (0.045, depth, height),
                (-width / 2 - 0.0225, centre_y, height / 2), left_sheet_material),
        add_box("SheetFloor_RightAtlas", (0.045, depth, height),
                (width / 2 + 0.0225, centre_y, height / 2), right_sheet_material),
        add_box("SheetFloor_RearAtlas", (width, 0.045, height),
                (0, centre_y + depth / 2 + 0.0225, height / 2), rear_sheet_material),
    ])

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
        if (
            "balcony" in kinds
            and not crown
            and not setback
            and not signature_controls_balconies
            and not suppress_generic_balconies
        ):
            _add_balcony_v3(
                parts, f"SheetBalcony_{index:02d}", x, facade_y, bay_width,
                float(facade.get("balcony_depth_m", 1.5)),
                facade.get("balcony_guard", "metal"), mats,
                plants=facade.get("balcony_guard") == "planter",
            )
        # Oriel/window-bay detail stays in the sheet. A generic projecting box
        # covers the photographed glazing and looks worse than the source; only
        # balconies with a real walkable projection survive as 3D attachments.

    if (
        system == "heritage_stone"
        and variant_key == "typical_b"
        and facade.get("balcony_mode") == "projecting"
        and not (_signature_kits(grammar) & {"haussmann_balconies", "continuous_balcony", "eixample_balconies"})
        and not suppress_generic_balconies
    ):
        _add_heritage_balcony(parts, "SheetHeritageBalcony", width, facade_y - 0.04, mats)

    # Side/rear construction is the same PBR/physical-glazing stack as the
    # front. This keeps corner and aerial views in the same material language.

    if setback:
        parts.append(add_box("SheetTerrace_Deck", (full_width, full_depth, 0.09), (0, 0, 0.045), mats["concrete"]))
        terrace_y = -full_depth / 2 + 0.07
        parts.append(add_box("SheetTerrace_Rail", (full_width, 0.075, 0.075),
                             (0, terrace_y, 0.98), mats["accent"]))
        for post_index, x in enumerate((-full_width / 2 + 0.12, -full_width / 4, 0.0,
                                        full_width / 4, full_width / 2 - 0.12)):
            parts.append(add_box(f"SheetTerrace_Post{post_index}", (0.075, 0.075, 0.92),
                                 (x, terrace_y, 0.5), mats["accent"]))
    if crown and rooftop_pavilion:
        # Full-footprint terrace below the recessed crown. The pavilion itself
        # remains an independently resizable module, while planting and rail
        # geometry establish the depth cues that a flat atlas cannot provide.
        terrace_z = 0.075
        parts.append(add_beveled_box(
            "Pavilion_TerraceDeck", (full_width, full_depth, 0.15),
            (0, 0, terrace_z), mats["concrete"], 0.035,
        ))
        parts.append(add_box(
            "Pavilion_TerraceGreen", (full_width - 0.55, full_depth - 0.55, 0.075),
            (0, 0, 0.19), mats["green_roof"],
        ))
        terrace_front_y = -full_depth / 2 + 0.46
        planter_width = full_width * 0.235
        for planter_index, x in enumerate((-full_width * 0.33, 0.0, full_width * 0.33)):
            parts.append(add_beveled_box(
                f"Pavilion_FrontPlanter{planter_index}", (planter_width, 0.62, 0.42),
                (x, terrace_front_y, 0.38), mats["secondary"], 0.045,
            ))
            add_planter_vegetation(
                parts, f"Pavilion_FrontGreen{planter_index}",
                (x, terrace_front_y - 0.03, 0.60), planter_width * 0.86, mats,
            )
        rail_z = 0.92
        parts.append(add_box(
            "Pavilion_FrontRail", (full_width - 0.42, 0.055, 0.075),
            (0, -full_depth / 2 + 0.16, rail_z), mats["accent"],
        ))
        for rail_index, x in enumerate((-full_width / 2 + 0.22, -full_width / 4, 0.0,
                                        full_width / 4, full_width / 2 - 0.22)):
            parts.append(add_box(
                f"Pavilion_FrontRailPost{rail_index}", (0.055, 0.055, 0.78),
                (x, -full_depth / 2 + 0.16, 0.52), mats["accent"],
            ))
        # Folded zinc cap and slim corner posts frame the modern addition
        # without reverting to the brick cornice/pilaster crown kit.
        monitor_crown = "roof_monitor" in _signature_kits(grammar)
        parts.append(add_beveled_box(
            "Pavilion_ZincFascia",
            (
                width + (0.10 if monitor_crown else 0.26),
                depth + (0.10 if monitor_crown else 0.22),
                0.18 if monitor_crown else 0.32,
            ),
            (0, centre_y, height - (0.10 if monitor_crown else 0.18)),
            mats["accent"] if monitor_crown else mats["secondary"],
            0.025 if monitor_crown else 0.055,
        ))
        for post_index, x in enumerate((-width / 2 + 0.12, width / 2 - 0.12)):
            parts.append(add_box(
                f"Pavilion_CornerPost{post_index}", (0.12, 0.22, height * 0.82),
                (x, facade_y - 0.06, height * 0.48), mats["accent"],
            ))
    elif crown:
        _add_crown_v3(parts, system, width, depth, height, facade_y, mats)
    elif "timber_picture_frames" not in _signature_kits(grammar):
        parts.append(add_box("SheetFloor_HeadDatum", (width + 0.14, 0.12, 0.10),
                             (0, facade_y - 0.04, height - 0.05), mats["secondary"]))

    _add_signature_floor_details(
        grammar, parts, width, depth, height, facade_y, variant_key, mats, sheet_material
    )

    _add_modular_glazing_overlays(
        grammar, parts, mats, role=glazing_role, width=width, depth=depth,
        height=height, centre_y=centre_y, facade_y=facade_y,
    )

    role_name = "Crown" if crown else "Setback" if setback else variant_key.title().replace("_", "")
    module = join_as(f"MOD_{role_name}", parts)
    apply_facade_sheet_uv(module, FACADE_SHEET["manifest"]["span_m"], height)
    return module


def build_roof(grammar: dict, mats: dict) -> bpy.types.Object:
    dims, roof = grammar["dimensions"], grammar["roof"]
    w, d, h = dims["width_m"], dims["depth_m"], dims["roof_height_m"]
    kits = _signature_kits(grammar)
    parts: list = []
    signature_roof_hero = bool(kits & {
        "barrel_vault_roof", "glass_turbine_lantern", "roof_pergola",
    })

    if roof["type"] == "mansard":
        slab_h = 0.18
        skirt_h = max(2.6, h * 0.72)
        inset = min(2.25, min(w, d) * 0.18)
        ov = 0.28
        haussmann_roof = "haussmann_balconies" in kits
        heritage_roof = "heritage_stone_depth" in kits
        # Wide/deep railway hotels are perimeter buildings.  Their approved
        # aerial render has a genuine roof court, not one enormous hipped lid.
        # Keep the compact hipped cap for smaller footprints, but switch to a
        # copper roof ring once there is enough plan depth for a credible court.
        heritage_courtyard_roof = heritage_roof and w >= 65.0 and d >= 48.0
        parts.append(add_beveled_box(
            "Mansard_CorniceDeck", (w + 0.72, d + 0.64, slab_h),
            (0, 0, slab_h / 2), mats["secondary"], 0.045,
        ))
        bottom = [
            (-w / 2 - ov, -d / 2 - ov, slab_h), (w / 2 + ov, -d / 2 - ov, slab_h),
            (w / 2 + ov, d / 2 + ov, slab_h), (-w / 2 - ov, d / 2 + ov, slab_h),
        ]
        top = [
            (-w / 2 + inset, -d / 2 + inset, skirt_h), (w / 2 - inset, -d / 2 + inset, skirt_h),
            (w / 2 - inset, d / 2 - inset, skirt_h), (-w / 2 + inset, d / 2 - inset, skirt_h),
        ]
        skirt_faces = [
            (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (3, 2, 1, 0),
        ]
        if not haussmann_roof and not heritage_courtyard_roof:
            skirt_faces.append((4, 5, 6, 7))
        parts.append(add_prism(
            "Mansard_SlateSkirt", bottom + top,
            skirt_faces,
            mats["roof"],
        ))
        top_w, top_d = w - inset * 2 + 0.18, d - inset * 2 + 0.18
        if heritage_courtyard_roof:
            # Four shallow copper roof fields form a registered perimeter ring
            # around a recessed service/guest court.  The outer steep mansard
            # still carries every dormer; only the broad top plane is opened.
            # This is the target render's dominant aerial massing cue.
            well_w = min(top_w * 0.50, max(24.0, top_w - 26.0))
            well_d = min(top_d * 0.42, max(16.0, top_d - 22.0))
            strip_y = (top_d - well_d) / 2
            strip_x = (top_w - well_w) / 2
            deck_z = skirt_h + 0.08
            parts.extend([
                add_beveled_box("Mansard_CopperCourtRoofFront", (top_w, strip_y, 0.16),
                                (0, -(well_d + strip_y) / 2, deck_z), mats["roof"], 0.030),
                add_beveled_box("Mansard_CopperCourtRoofRear", (top_w, strip_y, 0.16),
                                (0, (well_d + strip_y) / 2, deck_z), mats["roof"], 0.030),
                add_beveled_box("Mansard_CopperCourtRoofLeft", (strip_x, well_d, 0.16),
                                (-(well_w + strip_x) / 2, 0, deck_z), mats["roof"], 0.030),
                add_beveled_box("Mansard_CopperCourtRoofRight", (strip_x, well_d, 0.16),
                                ((well_w + strip_x) / 2, 0, deck_z), mats["roof"], 0.030),
            ])
            well_depth = min(2.30, skirt_h * 0.52)
            wall_z = skirt_h - well_depth / 2
            wall_t = 0.24
            parts.extend([
                add_beveled_box("Mansard_CourtWallFront", (well_w, wall_t, well_depth),
                                (0, -well_d / 2, wall_z), mats["signature_stone"], 0.035),
                add_beveled_box("Mansard_CourtWallRear", (well_w, wall_t, well_depth),
                                (0, well_d / 2, wall_z), mats["signature_stone"], 0.035),
                add_beveled_box("Mansard_CourtWallLeft", (wall_t, well_d, well_depth),
                                (-well_w / 2, 0, wall_z), mats["signature_stone"], 0.035),
                add_beveled_box("Mansard_CourtWallRight", (wall_t, well_d, well_depth),
                                (well_w / 2, 0, wall_z), mats["signature_stone"], 0.035),
                add_beveled_box("Mansard_CourtFloor",
                                (well_w - wall_t * 2, well_d - wall_t * 2, 0.12),
                                (0, 0, skirt_h - well_depth + 0.06), mats["concrete"], 0.025),
            ])
            # A stone coping catches the same highlight as the outer facade
            # cornice and visually terminates the inner elevations.
            coping_z = skirt_h + 0.11
            parts.extend([
                add_beveled_box("Mansard_CourtCopingFront", (well_w + 0.30, 0.34, 0.15),
                                (0, -well_d / 2, coping_z), mats["signature_stone"], 0.035),
                add_beveled_box("Mansard_CourtCopingRear", (well_w + 0.30, 0.34, 0.15),
                                (0, well_d / 2, coping_z), mats["signature_stone"], 0.035),
                add_beveled_box("Mansard_CourtCopingLeft", (0.34, well_d, 0.15),
                                (-well_w / 2, 0, coping_z), mats["signature_stone"], 0.035),
                add_beveled_box("Mansard_CourtCopingRight", (0.34, well_d, 0.15),
                                (well_w / 2, 0, coping_z), mats["signature_stone"], 0.035),
            ])
            # The court is inhabited architecture, not a black texture hole.
            # Warm recessed panes and real frames make the inner elevations
            # legible in the same close Google-Tiles orbit used for QA.
            court_window_h = min(1.34, well_depth * 0.62)
            court_window_w = min(1.42, well_w / 12.0)
            court_window_z = wall_z
            front_count = max(6, min(12, round(well_w / 7.0)))
            front_margin = max(1.8, well_w * 0.06)
            for wall_name, wall_y, axis, facing_sign in (
                ("Front", -well_d / 2, "rear", 1),
                ("Rear", well_d / 2, "front", -1),
            ):
                for window_index in range(front_count):
                    window_x = (
                        -well_w / 2 + front_margin
                        + (well_w - front_margin * 2) * window_index / max(1, front_count - 1)
                    )
                    window_y = wall_y + facing_sign * (wall_t / 2 + 0.035)
                    room_mat = mats["interior_cells"][(window_index + (0 if wall_name == "Front" else 2)) % len(mats["interior_cells"])]
                    parts.append(add_box(
                        f"Mansard_Court{wall_name}Window{window_index:02d}",
                        (court_window_w, 0.055, court_window_h),
                        (window_x, window_y, court_window_z), room_mat,
                    ))
                    add_frame_bars(
                        parts, f"Mansard_Court{wall_name}Frame{window_index:02d}", axis,
                        (window_x, window_y + facing_sign * 0.03, court_window_z),
                        court_window_w, court_window_h, 0.08, mats["accent"],
                        profile=0.045, mullions="single",
                    )
                    _signature_relief_box(
                        parts, f"Mansard_Court{wall_name}Sill{window_index:02d}",
                        (court_window_w + 0.24, 0.16, 0.10),
                        (window_x, window_y, court_window_z - court_window_h / 2 - 0.08),
                        mats["signature_stone"], bevel_m=0.022,
                    )

            side_count = max(3, min(6, round(well_d / 6.5)))
            side_margin = max(1.5, well_d * 0.09)
            for wall_name, wall_x, axis, facing_sign in (
                ("Left", -well_w / 2, "right", 1),
                ("Right", well_w / 2, "left", -1),
            ):
                for window_index in range(side_count):
                    window_y = (
                        -well_d / 2 + side_margin
                        + (well_d - side_margin * 2) * window_index / max(1, side_count - 1)
                    )
                    window_x = wall_x + facing_sign * (wall_t / 2 + 0.035)
                    room_mat = mats["interior_cells"][(window_index + (1 if wall_name == "Left" else 3)) % len(mats["interior_cells"])]
                    parts.append(add_box(
                        f"Mansard_Court{wall_name}Window{window_index:02d}",
                        (0.055, court_window_w, court_window_h),
                        (window_x, window_y, court_window_z), room_mat,
                    ))
                    add_frame_bars(
                        parts, f"Mansard_Court{wall_name}Frame{window_index:02d}", axis,
                        (window_x + facing_sign * 0.03, window_y, court_window_z),
                        court_window_w, court_window_h, 0.08, mats["accent"],
                        profile=0.045, mullions="single",
                    )
        elif haussmann_roof and w >= 18.0 and d >= 14.0:
            # A perimeter mansard block normally encloses an inner court. Four
            # lead-deck strips plus recessed walls create a genuine aerial void
            # instead of the former dead black lid, while scaling with any
            # sufficiently large user-drawn footprint.
            well_w = min(top_w * 0.48, max(5.0, top_w - 8.0))
            well_d = min(top_d * 0.44, max(4.0, top_d - 7.0))
            strip_y = (top_d - well_d) / 2
            strip_x = (top_w - well_w) / 2
            deck_z = skirt_h + 0.08
            parts.extend([
                add_beveled_box("Mansard_LeadDeckFront", (top_w, strip_y, 0.16),
                                (0, -(well_d + strip_y) / 2, deck_z), mats["roof_lead"], 0.025),
                add_beveled_box("Mansard_LeadDeckRear", (top_w, strip_y, 0.16),
                                (0, (well_d + strip_y) / 2, deck_z), mats["roof_lead"], 0.025),
                add_beveled_box("Mansard_LeadDeckLeft", (strip_x, well_d, 0.16),
                                (-(well_w + strip_x) / 2, 0, deck_z), mats["roof_lead"], 0.025),
                add_beveled_box("Mansard_LeadDeckRight", (strip_x, well_d, 0.16),
                                ((well_w + strip_x) / 2, 0, deck_z), mats["roof_lead"], 0.025),
            ])
            well_depth = min(1.35, skirt_h * 0.30)
            wall_z = skirt_h - well_depth / 2
            wall_t = 0.18
            parts.extend([
                add_box("Mansard_CourtWallFront", (well_w, wall_t, well_depth),
                        (0, -well_d / 2, wall_z), mats["secondary"]),
                add_box("Mansard_CourtWallRear", (well_w, wall_t, well_depth),
                        (0, well_d / 2, wall_z), mats["secondary"]),
                add_box("Mansard_CourtWallLeft", (wall_t, well_d, well_depth),
                        (-well_w / 2, 0, wall_z), mats["secondary"]),
                add_box("Mansard_CourtWallRight", (wall_t, well_d, well_depth),
                        (well_w / 2, 0, wall_z), mats["secondary"]),
                add_box("Mansard_CourtFloor", (well_w - wall_t * 2, well_d - wall_t * 2, 0.12),
                        (0, 0, skirt_h - well_depth + 0.06), mats["concrete"]),
            ])
        elif heritage_roof:
            # Chateauesque references resolve as one continuous oxidized-
            # copper roof silhouette.  A generic flat lead lid is especially
            # visible from the Google Tiles aerial camera and makes the rich
            # stone facade feel like it belongs to a different model.  Close
            # the mansard skirt with a shallow hipped copper cap instead.  The
            # long ridge scales with user-drawn frontage while the end hips
            # preserve a credible rain-shedding roof at every supported depth.
            cap_eave_z = skirt_h - 0.015
            cap_ridge_z = max(cap_eave_z + 0.72, h - 0.24)
            cap_half_w = top_w / 2
            cap_half_d = top_d / 2
            cap_ridge_half = max(0.85, cap_half_w - cap_half_d)
            cap_verts = [
                (-cap_half_w, -cap_half_d, cap_eave_z),
                (cap_half_w, -cap_half_d, cap_eave_z),
                (cap_half_w, cap_half_d, cap_eave_z),
                (-cap_half_w, cap_half_d, cap_eave_z),
                (-cap_ridge_half, 0.0, cap_ridge_z),
                (cap_ridge_half, 0.0, cap_ridge_z),
            ]
            parts.append(add_prism(
                "Mansard_CopperHipCap", cap_verts,
                [(0, 1, 5, 4), (3, 4, 5, 2), (0, 4, 3),
                 (1, 2, 5), (3, 2, 1, 0)],
                mats["roof"],
            ))
            _signature_relief_box(
                parts, "Mansard_CopperRidgeCap",
                (cap_ridge_half * 2 + 0.24, 0.15, 0.13),
                (0.0, 0.0, cap_ridge_z + 0.025),
                mats["roof_lead"], bevel_m=0.025,
            )
        else:
            parts.append(add_box("Mansard_LeadTop", (top_w, top_d, 0.16),
                                 (0, 0, skirt_h + 0.08), mats["roof_lead"]))
        # Flashing bands are intentionally modeled: they catch highlights in
        # aerial views where a normal map alone would disappear.
        parts.append(add_box("Mansard_FrontFlashing", (w + 0.28, 0.16, 0.16),
                             (0, -d / 2 - 0.18, slab_h + 0.08), mats["roof_lead"]))
        parts.append(add_box("Mansard_RearFlashing", (w + 0.28, 0.16, 0.16),
                             (0, d / 2 + 0.18, slab_h + 0.08), mats["roof_lead"]))

        dormer_count = (
            max(5, min(10, round(w / 3.0)))
            if haussmann_roof else
            max(8, min(14, round(w / 6.2)))
            if heritage_roof else
            max(4, min(6, round(w / 4.8)))
        )
        dormer_w = min(1.26 if haussmann_roof else 1.48, w / dormer_count * 0.48)
        dormer_h = min(1.58 if haussmann_roof else 1.75, skirt_h * 0.46)
        dormer_z = slab_h + skirt_h * 0.51
        heritage_dormer = heritage_roof
        for index in range(dormer_count):
            if heritage_roof and "centre_pavilion" in kits:
                # Reserve a true fixed centre bay instead of allowing a
                # repeatable dormer to collide with the landmark pavilion.
                centre_gap = min(18.0, max(12.0, w * 0.19))
                left_count = dormer_count // 2
                if index < left_count:
                    x = -w / 2 + (w / 2 - centre_gap / 2) * (index + 0.5) / left_count
                else:
                    right_count = dormer_count - left_count
                    right_index = index - left_count
                    x = centre_gap / 2 + (w / 2 - centre_gap / 2) * (right_index + 0.5) / right_count
            else:
                x = -w / 2 + w * (index + 0.5) / dormer_count
            body_d = 0.78
            body_y = -d / 2 + 0.30
            parts.append(add_beveled_box(
                f"DormerFront_{index:02d}_ZincBody",
                (dormer_w + 0.28, body_d, dormer_h + 0.30),
                (x, body_y, dormer_z),
                mats["roof"] if heritage_dormer else mats["roof_lead"],
                0.11 if heritage_dormer else 0.085,
            ))
            add_heritage_sash_front(
                parts, f"DormerFront_{index:02d}", x, body_y - body_d / 2 - 0.02, dormer_z,
                dormer_w, dormer_h, mats,
                pediment=(
                    "segmental" if haussmann_roof else
                    "triangle" if index in (0, dormer_count // 2, dormer_count - 1) else "segmental"
                ),
                interior_seed=index + 3,
                overlay=True,
                surround_material=mats["signature_stone"] if heritage_dormer else mats["roof_lead"],
                frame_material=mats["accent"],
                glass_material=(
                    mats["interior_cells"][(index + 3) % len(mats["interior_cells"])]
                    if heritage_dormer or FACADE_SHEET_DETAIL == "city" else mats["glass"]
                ),
                trim_scale=0.70 if heritage_dormer else (0.58 if haussmann_roof else 0.78),
                sash_mullions="single",
                fine_glazing_rails=False,
            )
            if heritage_dormer:
                # Stone sill/hood and a real metal apron tie the dormer to the
                # sandstone elevation while keeping rain-shedding pieces in
                # the same patinated metal family as the roof flashings.
                _signature_relief_box(
                    parts, f"DormerFront_{index:02d}_StoneSill",
                    (dormer_w + 0.42, 0.24, 0.16),
                    (x, body_y - body_d / 2 - 0.09, dormer_z - dormer_h / 2 - 0.07),
                    mats["signature_stone"], bevel_m=0.035,
                )
                _signature_relief_box(
                    parts, f"DormerFront_{index:02d}_LeadApron",
                    (dormer_w + 0.58, 0.42, 0.09),
                    (x, body_y - body_d / 2 + 0.06, dormer_z - dormer_h / 2 - 0.17),
                    mats["roof_lead"], bevel_m=0.022,
                )
            # Rear dormers keep the asset credible in orbit views without
            # duplicating the full carved front surround.
            rear_y = d / 2 - 0.30
            parts.append(add_beveled_box(
                f"DormerRear_{index:02d}_ZincBody",
                (dormer_w + 0.24, body_d, dormer_h + 0.25),
                (x, rear_y, dormer_z),
                mats["roof"] if heritage_dormer else mats["roof_lead"],
                0.075,
            ))
            rear_room_mat = mats["interior_cells"][(index + 1) % len(mats["interior_cells"])]
            rear_glass_mat = rear_room_mat if heritage_dormer or FACADE_SHEET_DETAIL == "city" else mats["glass"]
            parts.append(add_box(f"DormerRear_{index:02d}_Glass", (dormer_w, 0.05, dormer_h),
                                 (x, rear_y + body_d / 2 + 0.03, dormer_z), rear_glass_mat))
            parts.append(add_box(f"DormerRear_{index:02d}_Room", (dormer_w * 0.90, 0.045, dormer_h * 0.88),
                                 (x, rear_y + body_d / 2 - 0.08, dormer_z), rear_room_mat))
            add_frame_bars(parts, f"DormerRear_{index:02d}_Frame", "rear",
                           (x, rear_y + body_d / 2 + 0.06, dormer_z), dormer_w, dormer_h,
                           0.09, mats["accent"], profile=0.046, mullions="single")
            if heritage_dormer:
                for side, sx in (("L", -1), ("R", 1)):
                    _signature_relief_box(
                        parts, f"DormerRear_{index:02d}_StoneReturn{side}",
                        (0.13, 0.22, dormer_h + 0.20),
                        (x + sx * (dormer_w / 2 + 0.07), rear_y + body_d / 2 + 0.04, dormer_z),
                        mats["signature_stone"], bevel_m=0.024,
                    )

        side_dormer_count = max(2, min(4, round(d / 5)))
        for side_name, sign in (("Left", -1), ("Right", 1)):
            for index in range(side_dormer_count):
                y = -d / 2 + d * (index + 0.5) / side_dormer_count
                body_x = sign * (w / 2 - 0.30)
                parts.append(add_beveled_box(
                    f"Dormer{side_name}_{index:02d}_ZincBody",
                    (0.78, dormer_w + 0.18, dormer_h + 0.24),
                    (body_x, y, dormer_z),
                    mats["roof"] if heritage_dormer else mats["roof_lead"],
                    0.075,
                ))
                side_room_mat = mats["interior_cells"][(index + (0 if sign < 0 else 2)) % len(mats["interior_cells"])]
                side_glass_mat = side_room_mat if heritage_dormer or FACADE_SHEET_DETAIL == "city" else mats["glass"]
                parts.append(add_box(f"Dormer{side_name}_{index:02d}_Glass", (0.05, dormer_w, dormer_h),
                                     (sign * (w / 2 + 0.15), y, dormer_z), side_glass_mat))
                parts.append(add_box(f"Dormer{side_name}_{index:02d}_Room", (0.045, dormer_w * 0.90, dormer_h * 0.88),
                                     (sign * (w / 2 + 0.04), y, dormer_z), side_room_mat))
                add_frame_bars(parts, f"Dormer{side_name}_{index:02d}_Frame", "left" if sign < 0 else "right",
                               (sign * (w / 2 + 0.19), y, dormer_z), dormer_w, dormer_h,
                               0.09, mats["accent"], profile=0.046, mullions="single")
                if heritage_dormer:
                    for sy in (-1, 1):
                        _signature_relief_box(
                            parts, f"Dormer{side_name}_{index:02d}_StoneReturn{sy}",
                            (0.22, 0.13, dormer_h + 0.20),
                            (sign * (w / 2 + 0.17), y + sy * (dormer_w / 2 + 0.07), dormer_z),
                            mats["signature_stone"], bevel_m=0.024,
                        )

        if heritage_roof and "centre_pavilion" in kits:
            # The wide LEGO tier must keep the fixed landmark centre rather
            # than stretching a six-dormer roof over 90 metres. A stone-fronted
            # roof pavilion and hipped cap terminate the centre axis while only
            # the subordinate dormer field redistributes with frontage width.
            centre_w = min(16.0, max(12.0, w * 0.18))
            centre_d = min(4.6, max(3.4, d * 0.11))
            centre_y = -d / 2 + centre_d * 0.42
            centre_base_z = 0.34
            centre_drum_h = max(2.6, min(3.72, h - centre_base_z - 1.88))
            # Roof landmarks are authored geometry, not another repeatable
            # facade strip. Mapping the crown photograph over these drums
            # printed several miniature storeys behind the modeled sashes and
            # made the skyline look pasted together at close range.
            centre_field_mat = mats["signature_stone"]
            _signature_relief_box(
                parts, "RoofCentrePavilion_Drum",
                (centre_w, centre_d, centre_drum_h),
                (0.0, centre_y, centre_base_z + centre_drum_h / 2),
                centre_field_mat, bevel_m=0.10,
            )
            _signature_relief_box(
                parts, "RoofCentrePavilion_BaseCourse",
                (centre_w + 0.42, centre_d + 0.28, 0.18),
                (0.0, centre_y, centre_base_z + 0.09),
                mats["signature_stone"], bevel_m=0.045,
            )
            _signature_relief_box(
                parts, "RoofCentrePavilion_Cornice",
                (centre_w + 0.55, centre_d + 0.36, 0.22),
                (0.0, centre_y, centre_base_z + centre_drum_h - 0.11),
                mats["signature_stone"], bevel_m=0.055,
            )
            for pier_index, pier_x in enumerate((-centre_w * 0.43, centre_w * 0.43)):
                _signature_relief_box(
                    parts, f"RoofCentrePavilion_CornerPier{pier_index:02d}",
                    (0.34, 0.28, centre_drum_h - 0.18),
                    (pier_x, centre_y - centre_d / 2 - 0.10,
                     centre_base_z + centre_drum_h / 2),
                    mats["signature_stone"], bevel_m=0.045,
                )
            for sash_index, sash_x in enumerate((-centre_w * 0.27, 0.0, centre_w * 0.27)):
                add_heritage_sash_front(
                    parts, f"RoofCentrePavilion_Sash{sash_index:02d}",
                    sash_x, centre_y - centre_d / 2 - 0.03,
                    centre_base_z + centre_drum_h * 0.54,
                    min(1.22, centre_w * 0.17), min(1.18, centre_drum_h * 0.68), mats,
                    pediment="segmental" if sash_index == 1 else None,
                    interior_seed=sash_index + 5, overlay=True,
                    surround_material=mats["signature_stone"],
                    frame_material=mats["accent"],
                    glass_material=mats["interior_cells"][(sash_index + 1) % len(mats["interior_cells"])],
                    trim_scale=0.64, sash_mullions="single", fine_glazing_rails=False,
                )
            cap_eave_z = centre_base_z + centre_drum_h - 0.02
            cap_rise = max(1.45, min(2.10, h - cap_eave_z - 0.08))
            cap_ridge_z = cap_eave_z + cap_rise
            parts.append(add_gable_roof(
                "RoofCentrePavilion_GabledCap",
                (centre_w + 0.78, centre_d + 0.72, cap_rise),
                (0.0, centre_y, cap_eave_z),
                mats["roof"], bevel_m=0.075, ridge_axis="y",
            ))
            # Paired copper tourelles are fixed to the central landmark, not
            # distributed as repeatable dormers.  They echo the hero's vertical
            # silhouette and visually lock the stone pavilion into the roof.
            tourelle_radius = min(1.28, centre_w * 0.085)
            tourelle_drum_h = min(2.32, centre_drum_h * 0.72)
            tourelle_cap_h = max(1.45, cap_ridge_z - tourelle_drum_h - 0.10)
            tourelle_y = -d / 2 + tourelle_radius * 0.30
            for tourelle_index, sign in enumerate((-1, 1)):
                tourelle_x = sign * (centre_w / 2 - tourelle_radius * 0.28)
                parts.append(add_cylinder(
                    f"RoofCentrePavilion_Tourelle{tourelle_index}_Drum",
                    tourelle_radius, tourelle_drum_h,
                    (tourelle_x, tourelle_y, tourelle_drum_h / 2),
                    mats["signature_stone"], 28,
                ))
                parts.append(add_cylinder(
                    f"RoofCentrePavilion_Tourelle{tourelle_index}_Cornice",
                    tourelle_radius + 0.11, 0.16,
                    (tourelle_x, tourelle_y, tourelle_drum_h - 0.08),
                    mats["signature_stone"], 28,
                ))
                parts.append(add_cone(
                    f"RoofCentrePavilion_Tourelle{tourelle_index}_CopperCone",
                    tourelle_radius + 0.07, tourelle_cap_h,
                    (tourelle_x, tourelle_y,
                     tourelle_drum_h + tourelle_cap_h / 2 - 0.02),
                    mats["roof"], 32,
                ))
                parts.append(add_cylinder(
                    f"RoofCentrePavilion_Tourelle{tourelle_index}_Finial",
                    0.045, 0.28,
                    (tourelle_x, tourelle_y,
                     tourelle_drum_h + tourelle_cap_h + 0.12),
                    mats["accent"], 10,
                ))

            # Two lower gabled pavilions carry the quarter-point projections
            # from every stackable floor into the skyline.  Their authored
            # width is bounded while their positions follow the overall LEGO
            # frontage, so a resized hotel gains or loses repeat bays between
            # landmarks without stretching the landmarks themselves.
            secondary_w = min(8.4, max(5.8, w * 0.09))
            secondary_d = min(4.2, max(3.4, d * 0.105))
            secondary_y = -d / 2 + secondary_d * 0.42
            secondary_base_z = 0.30
            secondary_drum_h = min(3.25, h - secondary_base_z - 2.15)
            secondary_field_mat = mats["signature_stone"]
            for pavilion_index, sign in enumerate((-1, 1)):
                pavilion_x = sign * w * 0.27
                _signature_relief_box(
                    parts, f"RoofSecondaryPavilion{pavilion_index}_Drum",
                    (secondary_w, secondary_d, secondary_drum_h),
                    (pavilion_x, secondary_y,
                     secondary_base_z + secondary_drum_h / 2),
                    secondary_field_mat, bevel_m=0.085,
                )
                _signature_relief_box(
                    parts, f"RoofSecondaryPavilion{pavilion_index}_Cornice",
                    (secondary_w + 0.38, secondary_d + 0.26, 0.20),
                    (pavilion_x, secondary_y,
                     secondary_base_z + secondary_drum_h - 0.10),
                    mats["signature_stone"], bevel_m=0.045,
                )
                for pier_index, pier_sign in enumerate((-1, 1)):
                    _signature_relief_box(
                        parts, f"RoofSecondaryPavilion{pavilion_index}_Pier{pier_index}",
                        (0.30, 0.26, secondary_drum_h - 0.18),
                        (pavilion_x + pier_sign * secondary_w * 0.43,
                         secondary_y - secondary_d / 2 - 0.09,
                         secondary_base_z + secondary_drum_h / 2),
                        mats["signature_stone"], bevel_m=0.04,
                    )
                add_heritage_sash_front(
                    parts, f"RoofSecondaryPavilion{pavilion_index}_Sash",
                    pavilion_x, secondary_y - secondary_d / 2 - 0.03,
                    secondary_base_z + secondary_drum_h * 0.54,
                    min(1.32, secondary_w * 0.24),
                    min(1.30, secondary_drum_h * 0.62), mats,
                    pediment="triangle", interior_seed=pavilion_index + 8,
                    overlay=True, surround_material=mats["signature_stone"],
                    frame_material=mats["accent"],
                    glass_material=mats["interior_cells"][(pavilion_index + 2) % len(mats["interior_cells"])],
                    trim_scale=0.66, sash_mullions="single", fine_glazing_rails=False,
                )
                secondary_eave_z = secondary_base_z + secondary_drum_h - 0.02
                secondary_rise = max(1.35, min(2.05, h - secondary_eave_z - 0.10))
                parts.append(add_gable_roof(
                    f"RoofSecondaryPavilion{pavilion_index}_Gable",
                    (secondary_w + 0.50, secondary_d + 0.54, secondary_rise),
                    (pavilion_x, secondary_y, secondary_eave_z),
                    mats["roof"], bevel_m=0.065, ridge_axis="y",
                ))
                parts.append(add_cylinder(
                    f"RoofSecondaryPavilion{pavilion_index}_Finial",
                    0.05, 0.30,
                    (pavilion_x, secondary_y - secondary_d / 2 - 0.12,
                     secondary_eave_z + secondary_rise + 0.12),
                    mats["accent"], 10,
                ))

        # Four inhabited corner pavilions turn the roof into a composed skyline
        # rather than rooftop equipment. They are deliberately taller than the
        # dormer field and carry their own window and string-course hierarchy.
        pavilion_w = min(4.1, w * 0.18)
        pavilion_d = min(3.8, d * 0.24)
        pavilion_base_z = skirt_h - 1.02
        drum_h = 1.48
        landmark_roof = bool(kits & {"centre_pavilion", "corner_turret"})
        square_corner_pavilions = "centre_pavilion" in kits and "corner_turret" not in kits
        pavilion_positions = [
            (sx * (w / 2 - pavilion_w * 0.62), sy * (d / 2 - pavilion_d * 0.62), sx, sy)
            for sy in (-1, 1) for sx in (-1, 1)
        ] if square_corner_pavilions else []
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

        if landmark_roof and "corner_turret" not in kits:
            # The cupola belongs to monumental mansion/chateau profiles. A
            # regular Haussmann block keeps the quieter continuous mansard
            # silhouette shown by its own archetype references.
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
    elif roof["type"] == "flat" and _has_rooftop_pavilion(grammar) and "roof_monitor" in kits:
        # A mill monitor is a slim folded-metal cap over the inset glass
        # addition, not the pale full-depth roof deck used by residential
        # rooftop pavilions.  Keeping the cap tight removes the suspended
        # cartoon overhang visible at grazing angles.
        massing = grammar.get("massing") or {}
        inset_front = max(float(massing.get("setback_front_m", 0.0)), 1.6)
        inset_side = max(float(massing.get("setback_side_m", 0.0)), 0.9)
        monitor_w = max(4.0, w - inset_side * 2)
        monitor_d = max(4.0, d - inset_front)
        monitor_y = inset_front / 2
        cap_h = 0.18
        parts.append(add_beveled_box(
            "MonitorRoof_Cap", (monitor_w + 0.16, monitor_d + 0.16, cap_h),
            (0, monitor_y, cap_h / 2), mats["accent"], 0.028,
        ))
        parts.append(add_beveled_box(
            "MonitorRoof_FrontDrip", (monitor_w + 0.24, 0.10, 0.12),
            (0, monitor_y - monitor_d / 2 - 0.05, 0.10), mats["roof"], 0.018,
        ))
    elif roof["type"] == "flat" and _has_rooftop_pavilion(grammar):
        # A contemporary rooftop pavilion needs its own smaller pale roof;
        # covering the complete heritage footprint in bright green made the
        # previous City Prompt model look like a game asset. The planted area
        # now lives on the crown's occupiable terrace below.
        massing = grammar.get("massing") or {}
        inset_front = max(float(massing.get("setback_front_m", 0.0)), 1.6)
        inset_side = max(float(massing.get("setback_side_m", 0.0)), 0.9)
        pavilion_w = max(4.0, w - inset_side * 2)
        pavilion_d = max(4.0, d - inset_front)
        pavilion_y = inset_front / 2
        slab_h = 0.25
        parts.append(add_beveled_box(
            "PavilionRoof_Slab", (pavilion_w, pavilion_d, slab_h),
            (0, pavilion_y, slab_h / 2), mats["concrete"], 0.045,
        ))
        parapet_h, parapet_t = 0.52, 0.18
        parts.extend([
            add_beveled_box(
                "PavilionRoof_ParapetFront", (pavilion_w, parapet_t, parapet_h),
                (0, pavilion_y - pavilion_d / 2 + parapet_t / 2, parapet_h / 2),
                mats["secondary"], 0.035,
            ),
            add_beveled_box(
                "PavilionRoof_ParapetRear", (pavilion_w, parapet_t, parapet_h),
                (0, pavilion_y + pavilion_d / 2 - parapet_t / 2, parapet_h / 2),
                mats["secondary"], 0.035,
            ),
            add_beveled_box(
                "PavilionRoof_ParapetLeft", (parapet_t, pavilion_d - parapet_t * 2, parapet_h),
                (-pavilion_w / 2 + parapet_t / 2, pavilion_y, parapet_h / 2),
                mats["secondary"], 0.035,
            ),
            add_beveled_box(
                "PavilionRoof_ParapetRight", (parapet_t, pavilion_d - parapet_t * 2, parapet_h),
                (pavilion_w / 2 - parapet_t / 2, pavilion_y, parapet_h / 2),
                mats["secondary"], 0.035,
            ),
        ])
        # One screened service penthouse plus restrained mechanical units,
        # matching the target render's uncluttered roof silhouette.
        service_h = max(0.58, min(h - 0.08, 1.05))
        parts.append(add_beveled_box(
            "PavilionRoof_ServicePenthouse", (pavilion_w * 0.22, pavilion_d * 0.22, service_h),
            (-pavilion_w * 0.16, pavilion_y + pavilion_d * 0.18, slab_h + service_h / 2),
            mats["secondary"], 0.055,
        ))
        for unit_index, x in enumerate((pavilion_w * 0.08, pavilion_w * 0.24)):
            unit_w = pavilion_w * 0.105
            unit_d = pavilion_d * 0.105
            unit_h = max(0.34, service_h * 0.48)
            unit_y = pavilion_y - pavilion_d * 0.08
            parts.append(add_beveled_box(
                f"PavilionRoof_AHU{unit_index}", (unit_w, unit_d, unit_h),
                (x, unit_y, slab_h + unit_h / 2), mats["accent"], 0.035,
            ))
            parts.append(add_cylinder(
                f"PavilionRoof_AHUFan{unit_index}", min(unit_w, unit_d) * 0.22, 0.055,
                (x, unit_y, slab_h + unit_h + 0.028), mats["roof"], 18,
            ))
        for vent_index, x in enumerate((-pavilion_w * 0.34, pavilion_w * 0.36)):
            parts.append(add_cylinder(
                f"PavilionRoof_Vent{vent_index}", 0.10, 0.44,
                (x, pavilion_y + pavilion_d * 0.32, slab_h + 0.22), mats["accent"], 14,
            ))
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
        if roof.get("mechanical_screen") and not signature_roof_hero:
            mw, md, mh = w * 0.24, d * 0.28, max(0.8, h * 0.75)
            parts.append(add_box("Roof_MechScreen", (mw, md, mh), (w * 0.18, d * 0.12, slab_h + mh / 2), mats["accent"]))

        if h >= 0.75 and not signature_roof_hero:
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
# Landmark massing graph
# ---------------------------------------------------------------------------

def _graph_material(mats: dict, key: str | None):
    if key and key in mats:
        return mats[key]
    return mats["primary"]


def _mark_facade_uv_bounds(material, spec: dict, *, suffix: str = ""):
    """Clone a facade material and attach post-join UV reconstruction bounds."""
    clone = material.copy()
    clone.name = f"{material.name}_{spec.get('id', 'Facade')}{suffix}"
    axis = str(spec.get("axis", "front"))
    cx, cy, cz = (float(value) for value in spec["centre"])
    span = float(spec["span_m"])
    height = float(spec["height_m"])
    if axis in ("front", "rear"):
        u_min, u_max = cx - span / 2, cx + span / 2
    elif axis in ("left", "right"):
        u_min, u_max = cy - span / 2, cy + span / 2
    else:
        raise ValueError(f"facade UV axis {axis!r} is unsupported")
    clone["massing_skin"] = True
    clone["massing_skin_canonical"] = material.name
    clone["massing_skin_axis"] = axis
    clone["massing_skin_flip_u"] = bool(spec.get("flip_u", False))
    clone["massing_skin_u_min"] = u_min
    clone["massing_skin_u_max"] = u_max
    clone["massing_skin_z_min"] = cz - height / 2
    clone["massing_skin_z_max"] = cz + height / 2
    clone["massing_skin_tex_u_min"] = float(spec.get("uv_u_min", 0.0))
    clone["massing_skin_tex_u_max"] = float(spec.get("uv_u_max", 1.0))
    clone["massing_skin_v_min"] = float(spec.get("uv_v_min", 0.0))
    clone["massing_skin_v_max"] = float(spec.get("uv_v_max", 1.0))
    return clone


def _glazing_axis_vectors(axis: str) -> tuple[Vector, Vector]:
    """Return facade outward normal and horizontal along-facade direction."""
    return {
        "front": (Vector((0.0, -1.0, 0.0)), Vector((1.0, 0.0, 0.0))),
        "rear": (Vector((0.0, 1.0, 0.0)), Vector((-1.0, 0.0, 0.0))),
        "left": (Vector((-1.0, 0.0, 0.0)), Vector((0.0, 1.0, 0.0))),
        "right": (Vector((1.0, 0.0, 0.0)), Vector((0.0, -1.0, 0.0))),
    }[axis]


def _glazing_overlay_segment(
    parts: list,
    spec: dict,
    mats: dict,
    *,
    suffix: str = "",
) -> None:
    """Reusable near-LOD assembly: cut-out facade, recessed glass and rooms."""
    role = str(spec.get("band", "elevation"))
    near_base = mats.get(f"sheet_near_{role}")
    glass_base = mats.get(f"glass_overlay_{role}")
    if near_base is None or glass_base is None:
        return
    axis = str(spec.get("axis", "front"))
    if axis not in {"front", "rear", "left", "right"}:
        raise ValueError(f"glazing overlay axis {axis!r} is unsupported")
    centre = Vector(tuple(float(value) for value in spec["centre"]))
    span = float(spec["span_m"])
    height = float(spec["height_m"])
    columns = max(1, int(spec.get("columns", 4)))
    rows = max(1, int(spec.get("rows", 1)))
    profile_name = str(spec.get("glass_profile") or mats["glass_profile_name"])
    profile = glass_profile(profile_name)
    outward, along = _glazing_axis_vectors(axis)
    prefix = f"{spec.get('id', 'GlazingOverlay')}{suffix}"
    pane_recess = float(spec.get("pane_recess_m", profile["pane_recess_m"]))
    frame_depth = float(spec.get("frame_depth_m", profile["frame_depth_m"]))
    requested_interior_depth = float(spec.get("interior_depth_m", profile["interior_depth_m"]))
    frame_width = float(spec.get("profile_m", min(0.11, span / max(columns, 1) * 0.055)))

    geometry_only = bool(spec.get("geometry_only", False))
    near_material = (
        None if geometry_only
        else _mark_facade_uv_bounds(near_base, spec, suffix=f"{suffix}_Near")
    )
    glass_material = (
        None if geometry_only
        else _mark_facade_uv_bounds(glass_base, spec, suffix=f"{suffix}_Glass")
    )
    surface_offset = float(spec.get("surface_offset_m", 0.035))
    near_centre = centre + outward * surface_offset
    # The old section put the glazing in front of the wall and buried the room
    # card inside the solid shadow core. Keep the complete assembly within a
    # shallow ventilated facade cavity: cap at the face, glass behind it, warm
    # occupied room behind the glass but still in front of the structural core.
    cavity_depth = float(spec.get("cavity_depth_m", 0.34))
    pane_recess = min(pane_recess, cavity_depth * 0.42)
    interior_depth = min(
        requested_interior_depth,
        max(0.08, cavity_depth - pane_recess - 0.035),
    )
    glass_centre = near_centre - outward * pane_recess
    # The sash belongs at the recessed glazing plane. Keeping it behind the
    # stone face creates a visible reveal instead of another applied facade
    # decal, especially in oblique street and Google Tiles views.
    frame_centre = (
        centre + outward * max(0.025, frame_depth * 0.42)
        if geometry_only
        else glass_centre + outward * 0.018
    )
    # Keep the occupied room card inside the authored facade cavity, not inside
    # the solid massing core.  Landmark massing graphs often use a full-depth
    # structural box behind the skin; placing the card at the nominal room
    # depth let that pale box occlude it in City Prompt, so close-range window
    # cut-outs became white holes.  The shallow card still sits behind the
    # physical pane and retains the stone-return parallax that establishes
    # convincing window depth.
    room_card_recess = min(
        interior_depth,
        max(0.055, float(spec.get("room_card_recess_m", 0.10))),
    )
    backplate_plane = glass_centre - outward * room_card_recess

    if axis in ("front", "rear"):
        near_size = (span, 0.018, height)
        glass_size = (span, 0.014, height)
    else:
        near_size = (0.018, span, height)
        glass_size = (0.014, span, height)
    if not geometry_only:
        if not bool(spec.get("skip_near_facade", False)):
            parts.append(add_box(f"{prefix}_NearFacade", near_size, tuple(near_centre), near_material))
        parts.append(add_box(f"{prefix}_PhysicalGlass", glass_size, tuple(glass_centre), glass_material))
    if bool(spec.get("surface_only", False)):
        return

    # Real caps project in front of each Gemini-derived opening. The previous
    # coarse full-facade grid crossed brick/timber wall fields and made every
    # archetype read as a cage-like box; semantic regions keep construction
    # depth aligned to actual windows.
    frame_mat = mats.get(str(spec.get("cap_material_key", "glazing_frame")), mats["glazing_frame"])
    frame_mode = str(spec.get("frame_mode", "region_caps"))
    stone_returns = bool(spec.get("stone_returns", False))
    opening_returns = bool(spec.get("opening_returns", stone_returns))
    return_mat = mats.get(
        str(spec.get("return_material_key", "signature_stone" if stone_returns else "primary")),
        mats["secondary"],
    )
    interiors = mats["glazing_interior_cells"]
    source_regions = facade_glass_regions(role)
    tex_u_min = float(spec.get("uv_u_min", 0.0))
    tex_u_max = float(spec.get("uv_u_max", 1.0))
    tex_u_span = max(1e-6, tex_u_max - tex_u_min)
    if tex_u_min > 0.0 or tex_u_max < 1.0:
        cropped_regions: list[list[float]] = []
        for rx0, ry0, rx1, ry1 in source_regions:
            clipped_x0, clipped_x1 = max(rx0, tex_u_min), min(rx1, tex_u_max)
            if clipped_x1 <= clipped_x0:
                continue
            cropped_regions.append([
                (clipped_x0 - tex_u_min) / tex_u_span,
                ry0,
                (clipped_x1 - tex_u_min) / tex_u_span,
                ry1,
            ])
        source_regions = cropped_regions
    # Source-region Y is image-space (zero at the top), while the Blender UV
    # crop is bottom-up. Clip to the authored vertical crop before converting
    # regions into facade-local geometry. Without this guard, tower windows
    # outside a wing crop could create floating panes above the wall surface.
    uv_v_min = float(spec.get("uv_v_min", 0.0))
    uv_v_max = float(spec.get("uv_v_max", 1.0))
    source_y_min = 1.0 - uv_v_max
    source_y_max = 1.0 - uv_v_min
    if uv_v_min > 0.0 or uv_v_max < 1.0:
        cropped_regions = []
        for rx0, ry0, rx1, ry1 in source_regions:
            clipped_y0, clipped_y1 = max(ry0, source_y_min), min(ry1, source_y_max)
            if clipped_y1 <= clipped_y0:
                continue
            cropped_regions.append([rx0, clipped_y0, rx1, clipped_y1])
        source_regions = cropped_regions
    if bool(spec.get("window_region_filter", False)):
        # Generated masks occasionally include roof bands or image-edge fields
        # as "glass". Those broad regions produced giant U-shaped stone cages.
        # Retain only plausible punched-window proportions before repetition.
        source_regions = [
            region for region in source_regions
            if 0.035 <= region[2] - region[0] <= 0.24
            and 0.12 <= region[3] - region[1] <= 0.56
            and region[1] > 0.018 and region[3] < 0.982
        ]
    # UV reconstruction uses raw X/Y coordinates while facade-local `along`
    # reverses on rear/right faces. Account for both so frames stay registered.
    flip_u = bool(spec.get("flip_u", False)) ^ (axis in {"rear", "right"})
    repeat_span = max(0.25, float(spec.get("repeat_span_m", span)))
    regions: list[list[float]] = []
    if source_regions and repeat_span < span * 0.985:
        # ``apply_facade_sheet_uv`` repeats the authored four-bay strip in real
        # metres. Expand the semantic opening boxes with the identical phase;
        # otherwise four oversized physical windows would sit over ten baked
        # bays on a widened user footprint.
        lower = -span / 2
        upper = span / 2
        first_tile = math.floor(lower / repeat_span - 0.5) - 1
        last_tile = math.ceil(upper / repeat_span + 0.5) + 1
        for source_region in source_regions:
            rx0, ry0, rx1, ry1 = source_region
            if flip_u:
                rx0, rx1 = 1.0 - rx1, 1.0 - rx0
            authored_width = max(1e-6, (rx1 - rx0) * repeat_span)
            for tile in range(first_tile, last_tile + 1):
                x0_m = (tile + rx0 - 0.5) * repeat_span
                x1_m = (tile + rx1 - 0.5) * repeat_span
                clipped_x0, clipped_x1 = max(lower, x0_m), min(upper, x1_m)
                if clipped_x1 - clipped_x0 < authored_width * 0.72:
                    continue
                regions.append([
                    (clipped_x0 - lower) / span, ry0,
                    (clipped_x1 - lower) / span, ry1,
                ])
    else:
        for source_region in source_regions:
            x0, y0, x1, y1 = source_region
            if flip_u:
                x0, x1 = 1.0 - x1, 1.0 - x0
            regions.append([x0, y0, x1, y1])
    max_regions = max(0, int(spec.get("max_regions", 0)))
    if max_regions and len(regions) > max_regions:
        # Preserve first/last bays and sample the middle evenly. This bounds
        # runtime geometry while avoiding an obvious dense cluster at one end.
        selected = {
            round(index * (len(regions) - 1) / max(1, max_regions - 1))
            for index in range(max_regions)
        }
        regions = [region for index, region in enumerate(regions) if index in selected]
    if regions:
        for index, source_region in enumerate(regions):
            x0, y0, x1, y1 = source_region
            opening_span = max(frame_width * 2.2, (x1 - x0) * span)
            uv_v_range = max(1e-6, uv_v_max - uv_v_min)
            opening_height = max(frame_width * 2.2, (y1 - y0) / uv_v_range * height)
            along_position = ((x0 + x1) / 2.0 - 0.5) * span
            source_mid_v = 1.0 - (y0 + y1) / 2.0
            cropped_mid_v = (source_mid_v - uv_v_min) / uv_v_range
            z = centre.z + (cropped_mid_v - 0.5) * height
            cap_width = min(frame_width, opening_span * 0.055, opening_height * 0.055)
            cap_width = max(0.035, cap_width)
            cap_bevel = min(0.022, cap_width * 0.20)

            if opening_returns:
                return_width = max(0.07, min(0.16, opening_span * 0.075, opening_height * 0.065))
                return_depth = pane_recess + 0.055
                return_centre = near_centre - outward * (pane_recess * 0.50)
                # A reveal lines the cut opening; it is not an applied
                # architrave. Non-heritage jambs therefore sit wholly inside
                # the opening bounds. The previous centreline placement left
                # half of every box on the wall face, producing pale picture-
                # frame outlines in head-on City Prompt views.
                return_inset = 0.0 if stone_returns else return_width * 0.50
                for side, offset in (
                    ("L", -opening_span / 2 + return_inset),
                    ("R", opening_span / 2 - return_inset),
                ):
                    location = return_centre + along * (along_position + offset)
                    location.z = z
                    size = (
                        (
                            return_width, return_depth,
                            opening_height + return_width * 1.6 if stone_returns else opening_height,
                        )
                        if axis in ("front", "rear")
                        else (
                            return_depth, return_width,
                            opening_height + return_width * 1.6 if stone_returns else opening_height,
                        )
                    )
                    # Return pieces are recessed behind already-bevelled outer
                    # architraves. Keep them as simple solids: applying a
                    # separate Blender bevel modifier to hundreds of mask-
                    # derived jambs makes resizable family export needlessly
                    # expensive without a visible street-scale benefit.
                    parts.append(add_box(
                        f"{prefix}_StoneReturn{index:02d}_{side}", size, tuple(location), return_mat,
                    ))
                return_edges = () if bool(spec.get("vertical_returns_only", False)) else (
                    ("Head", z + opening_height / 2),
                    ("Sill", z - opening_height / 2),
                )
                for edge, edge_z in return_edges:
                    location = return_centre + along * along_position
                    if not stone_returns:
                        edge_z += -return_width * 0.50 if edge == "Head" else return_width * 0.50
                    location.z = min(
                        centre.z + height / 2 - return_width / 2,
                        max(centre.z - height / 2 + return_width / 2, edge_z),
                    )
                    size = (
                        (
                            opening_span + return_width * 1.5 if stone_returns else opening_span,
                            return_depth, return_width,
                        )
                        if axis in ("front", "rear")
                        else (
                            return_depth,
                            opening_span + return_width * 1.5 if stone_returns else opening_span,
                            return_width,
                        )
                    )
                    parts.append(add_box(
                        f"{prefix}_StoneReturn{index:02d}_{edge}", size, tuple(location), return_mat,
                    ))

            if frame_mode == "region_caps":
                for side, offset in (("L", -opening_span / 2), ("R", opening_span / 2)):
                    location = frame_centre + along * (along_position + offset)
                    location.z = z
                    size = (
                        (cap_width, frame_depth, opening_height + cap_width)
                        if axis in ("front", "rear")
                        else (frame_depth, cap_width, opening_height + cap_width)
                    )
                    parts.append(add_beveled_box(
                        f"{prefix}_Opening{index:02d}_{side}", size, tuple(location), frame_mat, cap_bevel,
                    ))
                for edge, edge_z in (("Head", z + opening_height / 2), ("Sill", z - opening_height / 2)):
                    edge_z = min(centre.z + height / 2 - cap_width / 2, edge_z)
                    edge_z = max(centre.z - height / 2 + cap_width / 2, edge_z)
                    location = frame_centre + along * along_position
                    location.z = edge_z
                    size = (
                        (opening_span + cap_width, frame_depth, cap_width)
                        if axis in ("front", "rear")
                        else (frame_depth, opening_span + cap_width, cap_width)
                    )
                    parts.append(add_beveled_box(
                        f"{prefix}_Opening{index:02d}_{edge}", size, tuple(location), frame_mat, cap_bevel,
                    ))


            # The physical sash sits at the glass plane, behind the masonry
            # return. It is intentionally independent of the outer cap mode:
            # audited atlases use ``sash_relief`` to avoid a duplicate dark
            # perimeter while still gaining real parallax and contact shadow.
            if frame_mode in {"region_caps", "sash_relief"} and bool(spec.get("depth_mullions", False)):
                industrial_sash = profile_name == "industrial_sash"
                if "mullion_count_override" in spec:
                    mullion_count = max(0, int(spec["mullion_count_override"]))
                elif industrial_sash:
                    mullion_count = 3 if opening_span > 2.8 else (2 if opening_span > 1.55 else 1)
                else:
                    mullion_count = 2 if opening_span > 2.8 else (1 if opening_span > 1.15 else 0)
                if "transom_count_override" in spec:
                    transom_count = max(0, int(spec["transom_count_override"]))
                elif industrial_sash:
                    transom_count = max(1, min(4, round(opening_height / 1.25) - 1))
                else:
                    transom_count = 1 if opening_height > 1.55 else 0
                sash_width = max(0.026, min(0.050, cap_width * (0.48 if industrial_sash else 0.56)))
                sash_depth = max(0.065, min(0.13, frame_depth * 0.72))
                sash_centre = glass_centre + outward * 0.028
                mullion_height_ratio = max(0.10, min(1.0, float(spec.get("mullion_height_ratio", 0.96))))
                mullion_vertical_offset = float(spec.get("mullion_vertical_offset_ratio", 0.0)) * opening_height
                transom_span_ratio = max(0.10, min(1.0, float(spec.get("transom_span_ratio", 0.96))))
                transom_vertical_span = max(0.10, min(1.0, float(spec.get("transom_vertical_span_ratio", 1.0))))
                transom_vertical_offset = float(spec.get("transom_vertical_offset_ratio", 0.0)) * opening_height
                for mullion_index in range(mullion_count):
                    fraction = (mullion_index + 1) / (mullion_count + 1) - 0.5
                    location = sash_centre + along * (along_position + opening_span * fraction)
                    location.z = z + mullion_vertical_offset
                    size = (
                        (sash_width, sash_depth, opening_height * mullion_height_ratio)
                        if axis in ("front", "rear")
                        else (sash_depth, sash_width, opening_height * mullion_height_ratio)
                    )
                    parts.append(add_beveled_box(
                        f"{prefix}_Opening{index:02d}_Mullion{mullion_index}",
                        size, tuple(location), frame_mat, min(0.010, sash_width * 0.18),
                    ))
                for transom_index in range(transom_count):
                    fraction = (
                        ((transom_index + 1) / (transom_count + 1) - 0.5)
                        * transom_vertical_span
                    )
                    location = sash_centre + along * along_position
                    location.z = z + opening_height * fraction + transom_vertical_offset
                    size = (
                        (opening_span * transom_span_ratio, sash_depth, sash_width)
                        if axis in ("front", "rear")
                        else (sash_depth, opening_span * transom_span_ratio, sash_width)
                    )
                    parts.append(add_beveled_box(
                        f"{prefix}_Opening{index:02d}_Transom{transom_index}",
                        size, tuple(location), frame_mat, min(0.010, sash_width * 0.18),
                    ))

            if bool(spec.get("projecting_sills", False)):
                sill_depth = min(0.28, max(0.16, pane_recess * 0.80))
                sill_height = max(0.045, min(0.085, cap_width * 0.72))
                location = near_centre + outward * (sill_depth * 0.32) + along * along_position
                location.z = max(
                    centre.z - height / 2 + sill_height / 2,
                    z - opening_height / 2 - sill_height * 0.30,
                )
                size = (
                    (opening_span + cap_width * 1.65, sill_depth, sill_height)
                    if axis in ("front", "rear")
                    else (sill_depth, opening_span + cap_width * 1.65, sill_height)
                )
                parts.append(add_beveled_box(
                    f"{prefix}_Opening{index:02d}_ProjectingSill",
                    size, tuple(location), return_mat, min(0.018, sill_height * 0.22),
                ))

            # One always-lit room card per actual opening gives parallax and
            # inhabited warmth without modelling a full floor plate. Fully
            # glazed office archetypes can disable the cards: large semantic
            # regions otherwise read as pale projecting boxes through a
            # reflective curtain wall rather than as distant interiors.
            if bool(spec.get("interior_cards", True)):
                location = backplate_plane + along * along_position
                location.z = z
                if axis in ("front", "rear"):
                    size = (opening_span * 0.90, 0.035, opening_height * 0.86)
                else:
                    size = (0.035, opening_span * 0.90, opening_height * 0.86)
                material = interiors[index % len(interiors)]
                parts.append(add_box(f"{prefix}_LitRoom_{index:02d}", size, tuple(location), material))
    else:
        # Backwards-compatible fallback for pre-v4 facade manifests.
        cell_span = span / columns
        cell_height = height / rows
        if bool(spec.get("interior_cards", True)):
            for row in range(rows):
                for column in range(columns):
                    location = backplate_plane + along * (-span / 2 + cell_span * (column + 0.5))
                    location.z = centre.z - height / 2 + cell_height * (row + 0.5)
                    if axis in ("front", "rear"):
                        size = (cell_span * 0.88, 0.035, cell_height * 0.78)
                    else:
                        size = (0.035, cell_span * 0.88, cell_height * 0.78)
                    material = interiors[(row * columns + column) % len(interiors)]
                    parts.append(add_box(f"{prefix}_LitRoom_{row:02d}_{column:02d}", size, tuple(location), material))


def _graph_glazing_overlay(parts: list, spec: dict, mats: dict) -> None:
    """Build one overlay or a floor-accurate stack from the same assembly kind."""
    levels = list(spec.get("levels") or [])
    if not levels:
        _glazing_overlay_segment(parts, spec, mats)
        return
    axis = str(spec.get("axis", "front"))
    cx, cy, z0 = (float(value) for value in spec["base_centre"])
    current_z = z0
    for index, level in enumerate(levels):
        height = float(level["height_m"])
        segment = {
            **spec,
            "axis": axis,
            "centre": [cx, cy, current_z + height / 2],
            "height_m": height,
            "band": level.get("band", "floor"),
            "columns": level.get("columns", spec.get("columns", 4)),
            "rows": level.get("rows", spec.get("rows", 1)),
            "repeat_span_m": level.get("repeat_span_m", spec.get("repeat_span_m", spec["span_m"])),
        }
        segment.pop("levels", None)
        segment.pop("base_centre", None)
        _glazing_overlay_segment(parts, segment, mats, suffix=f"_{index:02d}")
        current_z += height


def _graph_curtain_wall(parts: list, spec: dict, mats: dict, *, ribbon: bool = False) -> None:
    """Build a framed glass plane on a named facade axis.

    A ribbon window is deliberately a shadowed construction assembly rather
    than a texture decal: the reveal, glass and mullions each sit at a distinct
    depth and therefore respond to sun and orbiting cameras.
    """
    axis = spec.get("axis", "front")
    cx, cy, cz = (float(value) for value in spec["centre"])
    span = float(spec["span_m"])
    height = float(spec["height_m"])
    columns = max(1, int(spec.get("columns", 1)))
    rows = max(1, int(spec.get("rows", 1)))
    frame = float(spec.get("frame_m", 0.075 if ribbon else 0.105))
    depth = float(spec.get("depth_m", 0.075 if ribbon else 0.10))
    reveal = float(spec.get("reveal_m", 0.0))
    bevel = max(0.0, float(spec.get("bevel_m", min(0.025, frame * 0.22))))
    surround = max(0.0, float(spec.get("surround_m", 0.0)))
    surround_depth = max(depth * 1.45, float(spec.get("surround_depth_m", depth * 1.45)))
    sill_projection = max(0.0, float(spec.get("sill_projection_m", 0.0)))
    prefix = str(spec.get("id", "GraphGlazing"))
    glass_mat = _graph_material(mats, spec.get("glass_material", "glass"))
    frame_mat = _graph_material(mats, spec.get("frame_material", "signature_metal"))
    shadow_mat = _graph_material(mats, "massing_joint")
    interior_key = spec.get("interior_material")
    interior_mat = _graph_material(mats, interior_key) if interior_key else None
    interior_recess = float(spec.get("interior_recess_m", 0.055))

    # Some render-locked curtain walls bake the secondary cap/mullion scale
    # into the PBR atlas and add only the larger external structural grid as
    # geometry.  Keep the assembly declarative while avoiding a duplicated
    # cage of fine members over the authored façade.
    if bool(spec.get("skip_glass", False)) and bool(spec.get("skip_frame", False)):
        return

    if axis in ("front", "rear"):
        if reveal:
            parts.append(add_beveled_box(
                f"{prefix}_Reveal", (span + reveal * 2, depth * 1.8, height + reveal * 2),
                (cx, cy + (depth * 0.45 if axis == "front" else -depth * 0.45), cz),
                shadow_mat, min(0.035, reveal * 0.18),
            ))
        if not bool(spec.get("skip_glass", False)):
            parts.append(add_box(f"{prefix}_Glass", (span, depth, height), (cx, cy, cz), glass_mat))
        if interior_mat is not None:
            behind_y = cy + interior_recess if axis == "front" else cy - interior_recess
            parts.append(add_box(
                f"{prefix}_OccupiedInterior",
                (span * 0.94, 0.022, height * 0.92),
                (cx, behind_y, cz), interior_mat,
            ))
        for index in range(columns + 1):
            x = cx - span / 2 + span * index / columns
            parts.append(add_beveled_box(f"{prefix}_Mullion{index:02d}", (frame, depth * 1.45, height), (x, cy, cz), frame_mat, bevel))
        for index in range(rows + 1):
            z = cz - height / 2 + height * index / rows
            parts.append(add_beveled_box(f"{prefix}_Transom{index:02d}", (span, depth * 1.45, frame), (cx, cy, z), frame_mat, bevel))
        if surround:
            outward = -1.0 if axis == "front" else 1.0
            surround_y = cy + outward * max(0.0, surround_depth - depth) * 0.5
            for label, x in (("LeftReturn", cx - span / 2 - surround / 2), ("RightReturn", cx + span / 2 + surround / 2)):
                parts.append(add_beveled_box(f"{prefix}_{label}", (surround, surround_depth, height + surround * 2), (x, surround_y, cz), frame_mat, bevel))
            for label, z in (("HeadReturn", cz + height / 2 + surround / 2), ("SillReturn", cz - height / 2 - surround / 2)):
                projection = sill_projection if label == "SillReturn" else 0.0
                return_depth = surround_depth + projection
                return_y = surround_y + outward * projection * 0.5
                parts.append(add_beveled_box(f"{prefix}_{label}", (span + surround * 2, return_depth, surround), (cx, return_y, z), frame_mat, bevel))
    elif axis in ("left", "right"):
        if reveal:
            parts.append(add_beveled_box(
                f"{prefix}_Reveal", (depth * 1.8, span + reveal * 2, height + reveal * 2),
                (cx + (depth * 0.45 if axis == "left" else -depth * 0.45), cy, cz),
                shadow_mat, min(0.035, reveal * 0.18),
            ))
        if not bool(spec.get("skip_glass", False)):
            parts.append(add_box(f"{prefix}_Glass", (depth, span, height), (cx, cy, cz), glass_mat))
        if interior_mat is not None:
            behind_x = cx + interior_recess if axis == "left" else cx - interior_recess
            parts.append(add_box(
                f"{prefix}_OccupiedInterior",
                (0.022, span * 0.94, height * 0.92),
                (behind_x, cy, cz), interior_mat,
            ))
        for index in range(columns + 1):
            y = cy - span / 2 + span * index / columns
            parts.append(add_beveled_box(f"{prefix}_Mullion{index:02d}", (depth * 1.45, frame, height), (cx, y, cz), frame_mat, bevel))
        for index in range(rows + 1):
            z = cz - height / 2 + height * index / rows
            parts.append(add_beveled_box(f"{prefix}_Transom{index:02d}", (depth * 1.45, span, frame), (cx, cy, z), frame_mat, bevel))
        if surround:
            outward = -1.0 if axis == "left" else 1.0
            surround_x = cx + outward * max(0.0, surround_depth - depth) * 0.5
            for label, y in (("LeftReturn", cy - span / 2 - surround / 2), ("RightReturn", cy + span / 2 + surround / 2)):
                parts.append(add_beveled_box(f"{prefix}_{label}", (surround_depth, surround, height + surround * 2), (surround_x, y, cz), frame_mat, bevel))
            for label, z in (("HeadReturn", cz + height / 2 + surround / 2), ("SillReturn", cz - height / 2 - surround / 2)):
                projection = sill_projection if label == "SillReturn" else 0.0
                return_depth = surround_depth + projection
                return_x = surround_x + outward * projection * 0.5
                parts.append(add_beveled_box(f"{prefix}_{label}", (return_depth, span + surround * 2, surround), (return_x, cy, z), frame_mat, bevel))
    else:
        raise ValueError(f"massing graph glazing axis {axis!r} is unsupported")


def _graph_column_array(parts: list, spec: dict, mats: dict) -> None:
    start = Vector(tuple(float(value) for value in spec["start"]))
    end = Vector(tuple(float(value) for value in spec["end"]))
    count = max(1, int(spec.get("count", 1)))
    width, depth = (float(value) for value in spec.get("section", (0.8, 0.8)))
    height = float(spec["height_m"])
    bevel_m = float(spec.get("bevel_m", 0.035))
    mat = _graph_material(mats, spec.get("material", "concrete"))
    prefix = str(spec.get("id", "GraphColumns"))
    for index in range(count):
        t = index / max(1, count - 1)
        base = start.lerp(end, t)
        parts.append(add_beveled_box(
            f"{prefix}_{index:02d}", (width, depth, height),
            (base.x, base.y, base.z + height / 2), mat, bevel_m,
        ))


def _graph_classical_portico(parts: list, spec: dict, mats: dict) -> None:
    """Reusable giant-order stone portico with real round columns and pediment.

    The portico remains a fixed semantic assembly when side-wing bays repeat.
    Layered bases, capitals and entablature avoid the temporary-cylinder look
    of the older generic column array while staying inexpensive at city LOD.
    """
    cx, facade_y, base_z = (float(value) for value in spec["base_centre"])
    width = float(spec.get("width_m", 20.0))
    depth = float(spec.get("depth_m", 4.6))
    column_height = float(spec.get("column_height_m", 8.4))
    count = max(4, int(spec.get("count", 6)))
    radius = float(spec.get("column_radius_m", 0.46))
    pediment_rise = float(spec.get("pediment_rise_m", 2.35))
    stone = _graph_material(mats, spec.get("material", "signature_stone"))
    bronze = _graph_material(mats, spec.get("door_material", "signature_warm"))
    shadow = _graph_material(mats, "massing_joint")
    prefix = str(spec.get("id", "GraphClassicalPortico"))
    column_y = facade_y - depth * 0.70
    run = width - radius * 3.0
    shaft_base = base_z + 0.38
    for index in range(count):
        x = cx - run / 2 + run * index / max(1, count - 1)
        # Torus-free concentric cylinders read as a moulded Attic base and
        # restrained Ionic capital without requiring a bespoke sculpt mesh.
        parts.append(add_cylinder(
            f"{prefix}_BasePlinth{index:02d}", radius * 1.34, 0.20,
            (x, column_y, base_z + 0.10), stone, 24,
        ))
        parts.append(add_cylinder(
            f"{prefix}_BaseMoulding{index:02d}", radius * 1.16, 0.18,
            (x, column_y, base_z + 0.29), stone, 24,
        ))
        parts.append(add_cylinder(
            f"{prefix}_Shaft{index:02d}", radius, column_height,
            (x, column_y, shaft_base + column_height / 2), stone, 28,
        ))
        capital_z = shaft_base + column_height
        parts.append(add_cylinder(
            f"{prefix}_CapitalNeck{index:02d}", radius * 1.13, 0.20,
            (x, column_y, capital_z + 0.10), stone, 24,
        ))
        parts.append(add_beveled_box(
            f"{prefix}_CapitalAbacus{index:02d}",
            (radius * 2.75, radius * 2.3, 0.24),
            (x, column_y, capital_z + 0.30), stone, 0.055,
        ))

    entablature_z = shaft_base + column_height + 0.58
    entablature_y = facade_y - depth * 0.48
    for layer, (extra_w, layer_depth, layer_h, z_offset) in enumerate((
        (0.0, depth, 0.38, 0.0),
        (0.45, depth + 0.24, 0.34, 0.36),
        (0.85, depth + 0.42, 0.26, 0.66),
    )):
        parts.append(add_beveled_box(
            f"{prefix}_Entablature{layer}",
            (width + extra_w, layer_depth, layer_h),
            (cx, entablature_y, entablature_z + z_offset), stone, 0.055,
        ))

    # A real dentil course provides the small-scale shadow rhythm that makes
    # a classical portico hold up at pedestrian distance. It also remains a
    # fixed entrance component when the repeatable wing bays resize.
    dentil_count = max(24, int(round(width / 0.5)))
    dentil_cell = (width + 0.48) / dentil_count
    dentil_y = facade_y - depth * 0.92
    dentil_z = entablature_z + 0.79
    for index in range(dentil_count):
        x = cx - (width + 0.48) / 2 + dentil_cell * (index + 0.5)
        parts.append(add_beveled_box(
            f"{prefix}_Dentil{index:02d}",
            (dentil_cell * 0.54, 0.30, 0.22),
            (x, dentil_y, dentil_z), stone, 0.026,
        ))

    # ``add_gable_roof`` interprets Z as the eave datum, not the prism centre.
    # Seat the tympanum directly on the upper entablature moulding.
    pediment_eave_z = entablature_z + 0.84
    parts.append(add_gable_roof(
        f"{prefix}_Pediment",
        (width + 1.35, depth * 0.42, pediment_rise),
        (cx, facade_y - depth * 0.80, pediment_eave_z),
        stone, 0.065, "y",
    ))
    # A dark recessed door and transom keep the centre legible behind the
    # colonnade even when the facade atlas is viewed at a grazing angle.
    door_width = float(spec.get("door_width_m", width * 0.22))
    door_height = float(spec.get("door_height_m", 4.1))
    parts.append(add_beveled_box(
        f"{prefix}_DoorReveal", (door_width + 0.65, 0.16, door_height + 0.55),
        (cx, facade_y - 0.10, base_z + door_height / 2 + 0.12), shadow, 0.055,
    ))
    parts.append(add_box(
        f"{prefix}_BronzeDoor", (door_width, 0.05, door_height),
        (cx, facade_y - 0.20, base_z + door_height / 2 + 0.12), bronze,
    ))


def _graph_shaped_gable_array(parts: list, spec: dict, mats: dict) -> None:
    """Fixed Jacobethan/Dutch gables with a layered stone-scroll silhouette.

    These are deliberately semantic entrance-and-crown pieces rather than a
    repeatable roof-bay decoration.  The outer extruded profile provides the
    pale stone scroll edge and construction depth; the smaller brick profile
    sits forward of it so the two materials meet like a built parapet instead
    of a photograph pasted onto a triangular roof.
    """
    axis = str(spec.get("axis", "front"))
    if axis != "front":
        raise ValueError("shaped gable array currently supports the front facade only")
    cx, facade_y, base_z = (float(value) for value in spec["base_centre"])
    positions = [float(value) for value in (spec.get("positions_m") or [0.0])]
    width = float(spec.get("width_m", 7.6))
    height = float(spec.get("height_m", 6.0))
    depth = float(spec.get("depth_m", 0.46))
    stone = _graph_material(mats, spec.get("material", "signature_stone"))
    brick = _graph_material(mats, spec.get("infill_material", "primary"))
    prefix = str(spec.get("id", "GraphShapedGable"))

    profile_style = str(spec.get("profile_style", "ogee_scroll"))
    if profile_style == "steep_triangle":
        # Ruskinian and ecclesiastical frontispieces need a crisp steep gable,
        # not a Dutch-scroll silhouette.  The small shoulder keeps the base
        # course readable at a grazing angle and gives the stone verge a
        # believable return into the wall.
        outline = [
            (-0.50, 0.00), (-0.50, 0.10), (-0.455, 0.10),
            (-0.075, 0.86), (0.00, 1.00), (0.075, 0.86),
            (0.455, 0.10), (0.50, 0.10), (0.50, 0.00),
        ]
    else:
        # A sampled ogee/scroll outline reads as curved after the construction
        # bevel is applied, while remaining deterministic and inexpensive in GLB.
        outline = [
            (-0.50, 0.00), (-0.50, 0.23), (-0.455, 0.23),
            (-0.435, 0.34), (-0.375, 0.395), (-0.345, 0.51),
            (-0.275, 0.62), (-0.225, 0.75), (-0.115, 0.865),
            (0.00, 1.00),
            (0.115, 0.865), (0.225, 0.75), (0.275, 0.62),
            (0.345, 0.51), (0.375, 0.395), (0.435, 0.34),
            (0.455, 0.23), (0.50, 0.23), (0.50, 0.00),
        ]

    def extruded_profile(name: str, centre_x: float, profile_width: float,
                         profile_height: float, profile_depth: float,
                         profile_base_z: float, profile_y: float, material,
                         bevel_m: float) -> bpy.types.Object:
        profile = [(centre_x + x * profile_width, profile_base_z + z * profile_height) for x, z in outline]
        count = len(profile)
        back_y = profile_y
        front_y = profile_y - profile_depth
        verts = [(x, back_y, z) for x, z in profile] + [(x, front_y, z) for x, z in profile]
        faces: list[tuple[int, ...]] = [
            tuple(reversed(range(count))),
            tuple(range(count, count * 2)),
        ]
        for index in range(count):
            nxt = (index + 1) % count
            faces.append((index, nxt, count + nxt, count + index))
        obj = add_prism(name, verts, faces, material)
        bevel = obj.modifiers.new(name="CarvedScrollEdge", type="BEVEL")
        bevel.width = min(bevel_m, profile_depth * 0.22)
        bevel.segments = 3
        bevel.limit_method = "ANGLE"
        try:
            bevel.harden_normals = True
        except AttributeError:
            pass
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.modifier_apply(modifier=bevel.name)
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
        obj.select_set(False)
        return obj

    for index, offset in enumerate(positions):
        x = cx + offset
        tag = f"{prefix}_{index:02d}"
        parts.append(extruded_profile(
            f"{tag}_StoneScroll", x, width, height, depth,
            base_z, facade_y, stone, float(spec.get("bevel_m", 0.075)),
        ))
        parts.append(extruded_profile(
            f"{tag}_BrickInfill", x, width * 0.82, height * 0.78, depth * 0.16,
            base_z + height * 0.10, facade_y - depth - 0.018, brick, 0.025,
        ))
        finial_radius = float(spec.get("finial_radius_m", 0.19))
        finial_z = base_z + height + finial_radius * 1.15
        parts.append(add_cylinder(
            f"{tag}_FinialStem", finial_radius * 0.34, finial_radius * 1.45,
            (x, facade_y - depth * 0.58, finial_z - finial_radius * 0.58), stone, 12,
        ))
        parts.append(add_ellipsoid(
            f"{tag}_FinialBall", (x, facade_y - depth * 0.58, finial_z),
            (finial_radius, finial_radius, finial_radius), stone,
        ))


def _graph_chimney_cluster_array(parts: list, spec: dict, mats: dict) -> None:
    """Grouped masonry flues with banded caps for heritage roof silhouettes."""
    centres = [tuple(float(value) for value in centre) for centre in spec.get("centres", [])]
    if not centres:
        return
    count = max(2, int(spec.get("count_per_cluster", 3)))
    spacing = float(spec.get("spacing_m", 0.72))
    section = float(spec.get("section_m", 0.52))
    height = float(spec.get("height_m", 4.2))
    brick = _graph_material(mats, spec.get("material", "primary"))
    cap = _graph_material(mats, spec.get("cap_material", "secondary"))
    prefix = str(spec.get("id", "GraphChimneyCluster"))
    for cluster_index, (cx, cy, base_z) in enumerate(centres):
        run = spacing * (count - 1)
        for flue_index in range(count):
            x = cx - run / 2 + flue_index * spacing
            tag = f"{prefix}_{cluster_index:02d}_{flue_index:02d}"
            parts.append(add_beveled_box(
                f"{tag}_Flue", (section, section, height),
                (x, cy, base_z + height / 2), brick, 0.045,
            ))
            parts.append(add_beveled_box(
                f"{tag}_NeckCourse", (section * 1.18, section * 1.18, 0.20),
                (x, cy, base_z + height - 0.30), cap, 0.035,
            ))
            parts.append(add_beveled_box(
                f"{tag}_Cap", (section * 1.34, section * 1.34, 0.22),
                (x, cy, base_z + height + 0.05), cap, 0.035,
            ))


def _graph_striped_turret_array(parts: list, spec: dict, mats: dict) -> None:
    """Build fixed cylindrical polychrome corner turrets and conical roofs.

    Ruskinian banding is construction geometry at close range: the pale and
    blue-black courses project slightly from the brick drum, while carved belt
    courses cast broader shadows.  Keeping the complete corner and roof fixed
    prevents LEGO resizing from stretching a turret into an ordinary bay.
    """
    centres = [tuple(float(value) for value in centre) for centre in spec.get("centres", [])]
    if not centres:
        return
    prefix = str(spec.get("id", "GraphStripedTurret"))
    base_z = float(spec.get("base_z", 0.0))
    body_height = float(spec.get("body_height_m", 18.0))
    radius = float(spec.get("radius_m", 2.35))
    vertices = max(24, int(spec.get("vertices", 40)))
    body_mat = _graph_material(mats, spec.get("body_material", "primary"))
    stripe_mat = _graph_material(mats, spec.get("stripe_material", "secondary"))
    dark_mat = _graph_material(mats, spec.get("dark_material", "accent"))
    belt_mat = _graph_material(mats, spec.get("belt_material", "signature_stone"))
    roof_mat = _graph_material(mats, spec.get("roof_material", "roof"))
    stripe_height = float(spec.get("stripe_height_m", 0.48))
    dark_height = float(spec.get("dark_height_m", 0.32))
    belt_height = float(spec.get("belt_height_m", 0.28))
    roof_height = float(spec.get("roof_height_m", 6.4))
    roof_radius = float(spec.get("roof_radius_m", radius * 1.16))
    window_levels = [float(level) for level in spec.get("window_levels_m", [])]
    window_span = float(spec.get("window_span_m", 1.0))
    window_height = float(spec.get("window_height_m", 2.2))
    window_frame = float(spec.get("window_frame_m", 0.07))
    window_depth = float(spec.get("window_depth_m", 0.06))
    window_recess = float(spec.get("window_recess_m", 0.22))
    window_reveal = float(spec.get("window_reveal_m", 0.07))
    window_surround = float(spec.get("window_surround_m", 0.10))
    window_surround_depth = float(spec.get("window_surround_depth_m", 0.20))
    window_sill_projection = float(spec.get("window_sill_projection_m", 0.06))
    window_style = str(spec.get("window_style", "rectangular"))
    window_spring_ratio = float(spec.get("window_spring_ratio", 0.72))
    window_mullions = max(0, int(spec.get("window_mullions", 0)))
    window_transoms = max(0, int(spec.get("window_transoms", 1)))
    # Keep both the occupied card and pane just outside the opaque turret drum.
    # The frame sits farther out and gives the opening a believable stone return.
    window_plane_offset = radius + window_recess + float(spec.get("window_face_clearance_m", 0.035))

    for index, (cx, cy) in enumerate(centres):
        tag = f"{prefix}_{index:02d}"
        parts.append(add_cylinder(
            f"{tag}_BrickDrum", radius, body_height,
            (cx, cy, base_z + body_height / 2), body_mat, vertices,
        ))
        for stripe_index, level in enumerate(spec.get("stripe_levels_m", [])):
            z = base_z + float(level)
            parts.append(add_cylinder(
                f"{tag}_CreamCourse{stripe_index:02d}", radius * 1.012, stripe_height,
                (cx, cy, z), stripe_mat, vertices,
            ))
        for stripe_index, level in enumerate(spec.get("dark_levels_m", [])):
            z = base_z + float(level)
            parts.append(add_cylinder(
                f"{tag}_BlueBlackCourse{stripe_index:02d}", radius * 1.018, dark_height,
                (cx, cy, z), dark_mat, vertices,
            ))
        for belt_index, level in enumerate(spec.get("belt_levels_m", [])):
            z = base_z + float(level)
            parts.append(add_cylinder(
                f"{tag}_CarvedBelt{belt_index:02d}", radius * 1.075, belt_height,
                (cx, cy, z), belt_mat, vertices,
            ))
        roof_z = base_z + body_height + roof_height / 2
        parts.append(add_cone(
            f"{tag}_ConicalRoof", roof_radius, roof_height,
            (cx, cy, roof_z), roof_mat, vertices,
        ))
        finial_radius = float(spec.get("finial_radius_m", 0.15))
        finial_base = base_z + body_height + roof_height
        parts.append(add_cylinder(
            f"{tag}_FinialStem", finial_radius * 0.32, finial_radius * 2.2,
            (cx, cy, finial_base + finial_radius), belt_mat, 12,
        ))
        parts.append(add_ellipsoid(
            f"{tag}_FinialBall", (cx, cy, finial_base + finial_radius * 2.15),
            (finial_radius, finial_radius, finial_radius), belt_mat,
        ))

        if window_levels:
            # Each corner turret owns the two elevations exposed at its corner.
            # This preserves fixed corner identity while the middle wall bays can
            # still repeat or resize independently in the LEGO family.
            facade_axes = (
                "left" if cx < 0.0 else "right",
                "front" if cy < 0.0 else "rear",
            )
            for axis in facade_axes:
                outward, _along = _glazing_axis_vectors(axis)
                plane_x = cx + outward.x * window_plane_offset
                plane_y = cy + outward.y * window_plane_offset
                for level_index, level in enumerate(window_levels):
                    window_spec = {
                        "id": f"{tag}_{axis.title()}InsetWindow{level_index:02d}",
                        "axis": axis,
                        "centre": [plane_x, plane_y, base_z + level],
                        "span_m": window_span,
                        "height_m": window_height,
                        "depth_m": max(window_depth, window_surround_depth),
                        "recess_m": window_recess,
                        "sill_projection_m": window_sill_projection,
                        "material": spec.get("window_material", "signature_stone"),
                        "glass_material": spec.get("window_glass_material", "glass"),
                        "interior_material": spec.get("window_interior_material", "interior_warm"),
                    }
                    if window_style == "pointed":
                        _graph_pointed_window_array(parts, {
                            **window_spec,
                            "count": 1,
                            "gap_m": max(0.08, window_reveal * 2.0),
                            "profile_m": max(0.055, window_surround),
                            "spring_ratio": window_spring_ratio,
                            "mullions": window_mullions,
                            "transoms": window_transoms,
                        }, mats)
                    elif window_style == "rectangular":
                        _graph_curtain_wall(parts, {
                            **window_spec,
                            "columns": 1,
                            "rows": 1,
                            "frame_m": window_frame,
                            "reveal_m": window_reveal,
                            "surround_m": window_surround,
                            "surround_depth_m": window_surround_depth,
                            "bevel_m": min(0.025, window_frame * 0.22),
                            "frame_material": spec.get("window_material", "signature_stone"),
                            "interior_recess_m": window_recess,
                        }, mats)
                    else:
                        raise ValueError(f"striped turret window style {window_style!r} is unsupported")


def _graph_steps(parts: list, spec: dict, mats: dict) -> None:
    cx, cy, cz = (float(value) for value in spec["centre"])
    width = float(spec["width_m"])
    depth = float(spec["depth_m"])
    count = max(1, int(spec.get("count", 3)))
    rise = float(spec.get("rise_m", 0.14))
    mat = _graph_material(mats, spec.get("material", "concrete"))
    prefix = str(spec.get("id", "GraphSteps"))
    for index in range(count):
        step_depth = depth * (count - index) / count
        step_height = rise * (index + 1)
        # Higher treads retreat toward the building (+Y for the front facade).
        y = cy + (depth - step_depth) / 2
        parts.append(add_beveled_box(
            f"{prefix}_{index:02d}", (width, step_depth, step_height),
            (cx, y, cz + step_height / 2), mat, 0.018,
        ))


def _graph_rowhouse_stoop(parts: list, spec: dict, mats: dict) -> None:
    """Build a complete elevated rowhouse entrance as one reusable assembly.

    The ordinary ``steps`` primitive is intentionally austere.  A brownstone
    stoop needs a landing, construction-depth cheek/stringer, sloping iron
    rails, intermediate balusters and substantial newel posts so it reads as
    inhabited architecture from an oblique City Prompt camera rather than as
    a cartoon stair block.  The assembly is front-facing for v1; the axis is
    explicit so unsupported use fails loudly instead of silently rotating the
    entrance away from its facade.
    """
    axis = str(spec.get("axis", "front"))
    if axis != "front":
        raise ValueError(f"rowhouse stoop axis {axis!r} is unsupported")

    cx, facade_y, base_z = (float(value) for value in spec["base_centre"])
    width = float(spec.get("width_m", 2.45))
    run = float(spec.get("run_m", 2.70))
    rise = float(spec.get("rise_m", 1.30))
    landing_depth = float(spec.get("landing_depth_m", 0.95))
    count = max(3, int(spec.get("count", 8)))
    rail_height = float(spec.get("rail_height_m", 0.92))
    rail_profile = float(spec.get("rail_profile_m", 0.055))
    tread_overhang = float(spec.get("tread_overhang_m", 0.055))
    stone = _graph_material(mats, spec.get("stone_material", "signature_stone"))
    iron = _graph_material(mats, spec.get("rail_material", "signature_metal"))
    shadow = _graph_material(mats, spec.get("shadow_material", "massing_joint"))
    prefix = str(spec.get("id", "GraphRowhouseStoop"))
    step_rise = rise / count
    step_run = run / count

    # A thin shadow pad prevents the stair from appearing to float above the
    # prepared parcel surface when viewed against photogrammetry.
    parts.append(add_beveled_box(
        f"{prefix}_GroundShadow",
        (width + 0.34, run + landing_depth + 0.22, 0.045),
        (cx, facade_y - (run + landing_depth) / 2, base_z + 0.0225),
        shadow, 0.012,
    ))

    # Nested tread solids give every riser a real face and a slightly rounded
    # sandstone nosing while keeping the mesh inexpensive and watertight.
    outer_edge = facade_y - landing_depth - run
    for index in range(count):
        step_height = step_rise * (index + 1)
        depth = step_run + tread_overhang
        centre_y = outer_edge + step_run * (index + 0.5)
        parts.append(add_beveled_box(
            f"{prefix}_Tread{index:02d}",
            (width + tread_overhang * 2, depth, step_height),
            (cx, centre_y, base_z + step_height / 2),
            stone, min(0.025, step_rise * 0.16),
        ))

    landing_slab_h = max(0.16, step_rise * 1.15)
    parts.append(add_beveled_box(
        f"{prefix}_Landing",
        (width + tread_overhang * 2, landing_depth, landing_slab_h),
        (cx, facade_y - landing_depth / 2, base_z + rise - landing_slab_h / 2),
        stone, 0.028,
    ))

    # Low stone stringers visually carry the stair and mask the nested tread
    # construction at both exposed edges.
    stringer_width = 0.16
    stringer_length = math.hypot(run, rise)
    stringer_angle = math.atan2(rise, run)
    for side_index, side in enumerate((-1.0, 1.0)):
        x = cx + side * (width / 2 + stringer_width * 0.32)
        stringer = add_beveled_box(
            f"{prefix}_Stringer{side_index}",
            (stringer_width, stringer_length, 0.22),
            (x, outer_edge + run / 2, base_z + rise / 2 - 0.05),
            stone, 0.022,
        )
        stringer.rotation_euler.x = stringer_angle
        parts.append(stringer)

        # The top rail follows the stair pitch; a short horizontal return
        # guards the landing and terminates at the facade.
        rail = add_beveled_box(
            f"{prefix}_SlopedRail{side_index}",
            (rail_profile, stringer_length, rail_profile),
            (x, outer_edge + run / 2, base_z + rise / 2 + rail_height),
            iron, min(0.012, rail_profile * 0.20),
        )
        rail.rotation_euler.x = stringer_angle
        parts.append(rail)
        parts.append(add_beveled_box(
            f"{prefix}_LandingRail{side_index}",
            (rail_profile, landing_depth, rail_profile),
            (x, facade_y - landing_depth / 2, base_z + rise + rail_height),
            iron, min(0.012, rail_profile * 0.20),
        ))

        for post_index in range(count + 1):
            t = post_index / count
            y = outer_edge + run * t
            tread_z = base_z + rise * t
            post_height = rail_height
            parts.append(add_cylinder(
                f"{prefix}_Baluster{side_index}_{post_index:02d}",
                rail_profile * 0.34, post_height,
                (x, y, tread_z + post_height / 2), iron, 10,
            ))

        for post_index, (y, z) in enumerate((
            (outer_edge, base_z),
            (facade_y - landing_depth, base_z + rise),
        )):
            post_radius = rail_profile * 1.65
            post_height = rail_height + 0.16
            parts.append(add_cylinder(
                f"{prefix}_Newel{side_index}_{post_index}",
                post_radius, post_height,
                (x, y, z + post_height / 2), iron, 14,
            ))
            parts.append(add_cone(
                f"{prefix}_NewelCap{side_index}_{post_index}",
                post_radius * 1.22, post_radius * 1.65,
                (x, y, z + post_height + post_radius * 0.82), iron, 14,
            ))


def _graph_tie_grid(parts: list, spec: dict, mats: dict) -> None:
    axis = spec.get("axis", "front")
    cx, cy, cz = (float(value) for value in spec["centre"])
    span = float(spec["span_m"])
    height = float(spec["height_m"])
    columns = max(2, int(spec.get("columns", 6)))
    rows = max(2, int(spec.get("rows", 3)))
    radius = float(spec.get("radius_m", 0.035))
    mat = _graph_material(mats, "massing_joint")
    prefix = str(spec.get("id", "GraphTies"))
    for row in range(rows):
        z = cz - height / 2 + height * (row + 0.5) / rows
        for column in range(columns):
            along = -span / 2 + span * (column + 0.5) / columns
            if axis in ("front", "rear"):
                location = (cx + along, cy, z)
                rotation = (math.pi / 2, 0.0, 0.0)
            else:
                location = (cx, cy + along, z)
                rotation = (0.0, math.pi / 2, 0.0)
            tie = add_cylinder(f"{prefix}_{row:02d}_{column:02d}", radius, 0.028, location, mat, 12)
            tie.rotation_euler = rotation
            parts.append(tie)


def _graph_shadow_line(parts: list, spec: dict, mats: dict) -> None:
    axis = spec.get("axis", "front")
    cx, cy, cz = (float(value) for value in spec["centre"])
    span = float(spec["span_m"])
    height = float(spec.get("height_m", 0.05))
    depth = float(spec.get("depth_m", 0.025))
    if axis in ("front", "rear"):
        size = (span, depth, height)
    else:
        size = (depth, span, height)
    mat = _graph_material(mats, spec.get("material", "massing_joint"))
    parts.append(add_box(str(spec.get("id", "GraphShadowLine")), size, (cx, cy, cz), mat))


def _graph_skin_material(mats: dict, spec: dict, *, suffix: str = ""):
    role = str(spec.get("band", "elevation"))
    base = mats.get(f"sheet_{role}")
    if base is None:
        return None
    material = base.copy()
    material.name = f"{base.name}_{spec.get('id', 'Skin')}{suffix}"
    material["massing_skin"] = True
    material["massing_skin_canonical"] = base.name
    material["massing_skin_axis"] = str(spec.get("axis", "front"))
    material["massing_skin_flip_u"] = bool(spec.get("flip_u", False))
    return material


def _graph_facade_skin(parts: list, spec: dict, mats: dict, *, suffix: str = "") -> None:
    """Apply one rectified Gemini elevation to a thin, shadow-backed surface.

    Bounds live on a unique material clone so UVs can be reconstructed after
    every graph part has been joined into the single runtime mesh.
    """
    material = _graph_skin_material(mats, spec, suffix=suffix)
    if material is None:
        return
    axis = str(spec.get("axis", "front"))
    cx, cy, cz = (float(value) for value in spec["centre"])
    span = float(spec["span_m"])
    height = float(spec["height_m"])
    depth = float(spec.get("depth_m", 0.045))
    if axis in ("front", "rear"):
        size = (span, depth, height)
        u_min, u_max = cx - span / 2, cx + span / 2
    elif axis in ("left", "right"):
        size = (depth, span, height)
        u_min, u_max = cy - span / 2, cy + span / 2
    elif axis == "angle":
        size = (span, depth, height)
        u_min, u_max = -span / 2, span / 2
        angle_deg = float(spec.get("rotation_z_deg", 0.0))
        angle = math.radians(angle_deg)
        material["massing_skin_angle_deg"] = angle_deg
        material["massing_skin_origin_x"] = cx
        material["massing_skin_origin_y"] = cy
        material["massing_skin_along_x"] = math.cos(angle)
        material["massing_skin_along_y"] = math.sin(angle)
    else:
        raise ValueError(f"massing graph facade skin axis {axis!r} is unsupported")
    material["massing_skin_u_min"] = u_min
    material["massing_skin_u_max"] = u_max
    material["massing_skin_z_min"] = cz - height / 2
    material["massing_skin_z_max"] = cz + height / 2
    material["massing_skin_tex_u_min"] = float(spec.get("uv_u_min", 0.0))
    material["massing_skin_tex_u_max"] = float(spec.get("uv_u_max", 1.0))
    material["massing_skin_v_min"] = float(spec.get("uv_v_min", 0.0))
    material["massing_skin_v_max"] = float(spec.get("uv_v_max", 1.0))
    skin = add_box(f"{spec.get('id', 'GraphSkin')}{suffix}", size, (cx, cy, cz), material)
    if axis == "angle":
        skin.rotation_euler.z = math.radians(float(spec.get("rotation_z_deg", 0.0)))
    skin["facade_skin_source"] = str(spec.get("band", "elevation"))
    parts.append(skin)


def _graph_facade_skin_stack(parts: list, spec: dict, mats: dict) -> None:
    """Compose podium, alternating floor, and crown Gemini bands at real scale."""
    axis = str(spec.get("axis", "front"))
    cx, cy, z0 = (float(value) for value in spec["base_centre"])
    span = float(spec["span_m"])
    depth = float(spec.get("depth_m", 0.045))
    levels = list(spec.get("levels") or [])
    if not levels:
        raise ValueError(f"facade skin stack {spec.get('id')!r} has no levels")
    levels = [
        level
        for level in levels
        for _ in range(max(1, int(level.get("repeat", 1))))
    ]
    current_z = z0
    for index, level in enumerate(levels):
        height = float(level["height_m"])
        repeat_count = max(1, int(level.get("repeat_count", spec.get("repeat_count", 1))))
        segment_span = span / repeat_count
        for segment_index in range(repeat_count):
            if axis in ("front", "rear"):
                segment_cx = cx - span / 2 + segment_span * (segment_index + 0.5)
                segment_cy = cy
            elif axis in ("left", "right"):
                segment_cx = cx
                segment_cy = cy - span / 2 + segment_span * (segment_index + 0.5)
            elif axis == "angle":
                angle_deg = float(spec.get("rotation_z_deg", 0.0))
                angle = math.radians(angle_deg)
                offset = -span / 2 + segment_span * (segment_index + 0.5)
                segment_cx = cx + math.cos(angle) * offset
                segment_cy = cy + math.sin(angle) * offset
            else:
                raise ValueError(f"facade skin stack axis {axis!r} is unsupported")
            level_spec = {
                "id": str(spec.get("id", "GraphSkinStack")),
                "axis": axis,
                "centre": [segment_cx, segment_cy, current_z + height / 2],
                "span_m": segment_span,
                "height_m": height,
                "depth_m": depth,
                "band": level.get("band", "floor"),
                "flip_u": spec.get("flip_u", False),
            }
            if axis == "angle":
                level_spec["rotation_z_deg"] = float(spec.get("rotation_z_deg", 0.0))
            _graph_facade_skin(
                parts,
                level_spec,
                mats,
                suffix=f"_{index:02d}_{segment_index:02d}",
            )
        current_z += height


def _graph_frame_grid(parts: list, spec: dict, mats: dict) -> None:
    """Shadow-casting structural grid laid over, but independent from, a skin."""
    axis = str(spec.get("axis", "front"))
    cx, cy, cz = (float(value) for value in spec["centre"])
    span = float(spec["span_m"])
    height = float(spec["height_m"])
    columns = max(1, int(spec.get("columns", 4)))
    rows = max(1, int(spec.get("rows", 4)))
    profile = float(spec.get("profile_m", 0.16))
    vertical_profile = float(spec.get("vertical_profile_m", profile))
    horizontal_profile = float(spec.get("horizontal_profile_m", profile))
    depth = float(spec.get("depth_m", 0.20))
    vertical_depth = float(spec.get("vertical_depth_m", depth))
    horizontal_depth = float(spec.get("horizontal_depth_m", depth))
    edge_multiplier = float(spec.get("edge_profile_multiplier", 1.0))
    vertical_indices = {
        int(value) for value in spec.get("active_vertical_indices", range(columns + 1))
    }
    horizontal_indices = {
        int(value) for value in spec.get("active_horizontal_indices", range(rows + 1))
    }
    mat = _graph_material(mats, spec.get("material", "signature_metal"))
    prefix = str(spec.get("id", "GraphFrame"))
    if axis in ("front", "rear"):
        for index in range(columns + 1):
            if index not in vertical_indices:
                continue
            x = cx - span / 2 + span * index / columns
            member_profile = vertical_profile * (edge_multiplier if index in (0, columns) else 1.0)
            parts.append(add_beveled_box(
                f"{prefix}_V{index:02d}", (member_profile, vertical_depth, height),
                (x, cy - (vertical_depth - depth) * 0.20, cz), mat, member_profile * 0.16,
            ))
        for index in range(rows + 1):
            if index not in horizontal_indices:
                continue
            z = cz - height / 2 + height * index / rows
            parts.append(add_beveled_box(
                f"{prefix}_H{index:02d}", (span, horizontal_depth, horizontal_profile),
                (cx, cy + (depth - horizontal_depth) * 0.20, z), mat, horizontal_profile * 0.16,
            ))
    elif axis in ("left", "right"):
        for index in range(columns + 1):
            if index not in vertical_indices:
                continue
            y = cy - span / 2 + span * index / columns
            member_profile = vertical_profile * (edge_multiplier if index in (0, columns) else 1.0)
            parts.append(add_beveled_box(
                f"{prefix}_V{index:02d}", (vertical_depth, member_profile, height),
                (cx - (vertical_depth - depth) * 0.20, y, cz), mat, member_profile * 0.16,
            ))
        for index in range(rows + 1):
            if index not in horizontal_indices:
                continue
            z = cz - height / 2 + height * index / rows
            parts.append(add_beveled_box(
                f"{prefix}_H{index:02d}", (horizontal_depth, span, horizontal_profile),
                (cx + (depth - horizontal_depth) * 0.20, cy, z), mat, horizontal_profile * 0.16,
            ))
    else:
        raise ValueError(f"massing graph frame grid axis {axis!r} is unsupported")


def _graph_bay_frame_array(parts: list, spec: dict, mats: dict) -> None:
    """Project selected facade bays beyond the primary grid as nested frames."""
    axis = str(spec.get("axis", "front"))
    cx, cy, cz = (float(value) for value in spec["centre"])
    span = float(spec["span_m"])
    height = float(spec["height_m"])
    columns = max(1, int(spec.get("columns", 4)))
    rows = max(1, int(spec.get("rows", 5)))
    active = {int(value) for value in (spec.get("active_columns") or range(columns))}
    row_start = max(0, int(spec.get("row_start", 0)))
    explicit_rows = spec.get("active_rows")
    active_rows = (
        [int(value) for value in explicit_rows]
        if explicit_rows is not None
        else list(range(row_start, rows))
    )
    profile = float(spec.get("profile_m", 0.18))
    depth = float(spec.get("depth_m", 0.52))
    width_ratio = float(spec.get("width_ratio", 0.76))
    height_ratio = float(spec.get("height_ratio", 0.82))
    mat = _graph_material(mats, spec.get("material", "signature_warm"))
    prefix = str(spec.get("id", "GraphBayFrames"))
    bay, floor = span / columns, height / rows
    frame_w, frame_h = bay * width_ratio, floor * height_ratio

    for row in active_rows:
        if not row_start <= row < rows:
            continue
        z = cz - height / 2 + floor * (row + 0.5)
        for column in sorted(active):
            if not 0 <= column < columns:
                continue
            along = -span / 2 + bay * (column + 0.5)
            if axis in ("front", "rear"):
                x, y = cx + along, cy
                for side, offset in (("L", -frame_w / 2), ("R", frame_w / 2)):
                    parts.append(add_beveled_box(
                        f"{prefix}_{row:02d}_{column:02d}_{side}",
                        (profile, depth, frame_h), (x + offset, y, z), mat, profile * 0.18,
                    ))
                for side, offset in (("Sill", -frame_h / 2), ("Head", frame_h / 2)):
                    parts.append(add_beveled_box(
                        f"{prefix}_{row:02d}_{column:02d}_{side}",
                        (frame_w + profile, depth, profile), (x, y, z + offset), mat, profile * 0.18,
                    ))
            elif axis in ("left", "right"):
                x, y = cx, cy + along
                for side, offset in (("L", -frame_w / 2), ("R", frame_w / 2)):
                    parts.append(add_beveled_box(
                        f"{prefix}_{row:02d}_{column:02d}_{side}",
                        (depth, profile, frame_h), (x, y + offset, z), mat, profile * 0.18,
                    ))
                for side, offset in (("Sill", -frame_h / 2), ("Head", frame_h / 2)):
                    parts.append(add_beveled_box(
                        f"{prefix}_{row:02d}_{column:02d}_{side}",
                        (depth, frame_w + profile, profile), (x, y, z + offset), mat, profile * 0.18,
                    ))
            else:
                raise ValueError(f"massing graph bay-frame axis {axis!r} is unsupported")


def _graph_pointed_portal(parts: list, spec: dict, mats: dict) -> None:
    """Deep Gothic gateway with a real lancet opening and inhabited recess."""
    axis = str(spec.get("axis", "front"))
    if axis != "front":
        raise ValueError("pointed portal currently supports the front facade only")
    cx, cy, base_z = (float(value) for value in spec["base_centre"])
    width = float(spec.get("width_m", 4.8))
    spring_z = base_z + float(spec.get("spring_height_m", 5.4))
    apex_z = base_z + float(spec.get("apex_height_m", 8.2))
    depth = float(spec.get("depth_m", 0.72))
    profile = float(spec.get("profile_m", 0.42))
    stone = _graph_material(mats, spec.get("material", "signature_stone"))
    back = _graph_material(mats, spec.get("back_material", "interior_warm"))
    add_pointed_arch_frame(
        parts, str(spec.get("id", "GraphPointedPortal")), cx, cy, base_z,
        spring_z, apex_z, width, depth, profile, stone, back,
    )


def _graph_pointed_window_array(parts: list, spec: dict, mats: dict) -> None:
    """Build repeatable recessed lancets on orthogonal or angled elevations.

    A generated facade sheet still carries the carved Gothic identity, but a
    landmark tower must also retain readable openings when the atlas is
    compressed, viewed at a grazing angle, or temporarily unavailable.  This
    assembly therefore supplies real jambs, converging arch stones, mullions,
    transoms, projecting sills and occupied glass on every exposed facade.
    ``axis=angle`` keeps those parts in the same local construction plane and
    rotates the finished assembly, which lets octagonal lanterns receive the
    same depth and inhabited glazing as their cardinal faces.
    """
    axis = str(spec.get("axis", "front"))
    if axis not in {"front", "rear", "left", "right", "angle"}:
        raise ValueError(f"pointed window array axis {axis!r} is unsupported")
    cx, cy, cz = (float(value) for value in spec["centre"])
    span = float(spec["span_m"])
    height = float(spec["height_m"])
    count = max(1, int(spec.get("count", 3)))
    gap = max(0.08, float(spec.get("gap_m", 0.34)))
    depth = max(0.05, float(spec.get("depth_m", 0.24)))
    profile = max(0.05, float(spec.get("profile_m", 0.15)))
    spring_ratio = min(0.88, max(0.45, float(spec.get("spring_ratio", 0.72))))
    mullions = max(0, int(spec.get("mullions", 1)))
    transoms = max(0, int(spec.get("transoms", 3)))
    recess_m = max(0.02, float(spec.get("recess_m", 0.18)))
    sill_projection = max(0.0, float(spec.get("sill_projection_m", 0.16)))
    stone = _graph_material(mats, spec.get("material", "signature_stone"))
    glass = _graph_material(mats, spec.get("glass_material", "glass"))
    interior = _graph_material(mats, spec.get("interior_material", "interior_warm"))
    prefix = str(spec.get("id", "GraphPointedWindows"))
    angle = math.radians(float(spec.get("rotation_z_deg", 0.0)))
    if axis == "angle":
        along = Vector((math.cos(angle), math.sin(angle), 0.0))
        outward = Vector((-math.sin(angle), math.cos(angle), 0.0))
    else:
        outward, along = _glazing_axis_vectors(axis)
    x_aligned = axis in {"front", "rear", "angle"}
    first_part = len(parts)
    bay = span / count
    inner_width = max(0.28, bay - gap - profile * 2)
    base_z = cz - height / 2
    spring_z = base_z + height * spring_ratio
    apex_z = base_z + height
    jamb_height = spring_z - base_z
    rise = apex_z - spring_z
    half = inner_width / 2
    arch_length = math.sqrt(half * half + rise * rise)
    arch_angle = math.atan2(rise, half)
    bevel = min(0.045, profile * 0.18)

    def location(along_value: float, normal_value: float, z_value: float) -> tuple[float, float, float]:
        return (
            cx + along.x * along_value + outward.x * normal_value,
            cy + along.y * along_value + outward.y * normal_value,
            z_value,
        )

    for index in range(count):
        bay_along = -span / 2 + bay * (index + 0.5)
        item = f"{prefix}_{index:02d}"

        # Recess the glass and warm room card behind the masonry plane so the
        # opening reads as a cavity rather than a dark decal.
        if x_aligned:
            parts.append(add_box(
                f"{item}_Glass", (inner_width, 0.045, height * 0.93),
                location(bay_along, -recess_m, base_z + height * 0.465), glass,
            ))
            parts.append(add_box(
                f"{item}_OccupiedInterior", (inner_width * 0.90, 0.025, height * 0.87),
                location(bay_along, -(recess_m + 0.08), base_z + height * 0.445), interior,
            ))
        else:
            parts.append(add_box(
                f"{item}_Glass", (0.045, inner_width, height * 0.93),
                location(bay_along, -recess_m, base_z + height * 0.465), glass,
            ))
            parts.append(add_box(
                f"{item}_OccupiedInterior", (0.025, inner_width * 0.90, height * 0.87),
                location(bay_along, -(recess_m + 0.08), base_z + height * 0.445), interior,
            ))

        for side, offset in (("L", -half - profile / 2), ("R", half + profile / 2)):
            if x_aligned:
                size = (profile, depth, jamb_height + profile * 0.25)
            else:
                size = (depth, profile, jamb_height + profile * 0.25)
            parts.append(add_beveled_box(
                f"{item}_Jamb{side}", size,
                location(bay_along + offset, 0.0, base_z + jamb_height / 2),
                stone, bevel,
            ))

        for side, offset, sign in (("L", -half / 2, -1.0), ("R", half / 2, 1.0)):
            if x_aligned:
                arch = add_beveled_box(
                    f"{item}_Arch{side}", (arch_length + profile * 0.15, depth, profile),
                    location(bay_along + offset, 0.0, (spring_z + apex_z) / 2),
                    stone, bevel,
                )
                arch.rotation_euler.y = sign * arch_angle
            else:
                arch = add_beveled_box(
                    f"{item}_Arch{side}", (depth, arch_length + profile * 0.15, profile),
                    location(bay_along + offset, 0.0, (spring_z + apex_z) / 2),
                    stone, bevel,
                )
                arch.rotation_euler.x = -sign * arch_angle
            parts.append(arch)

        sill_depth = depth + sill_projection
        if x_aligned:
            sill_size = (inner_width + profile * 1.35, sill_depth, profile * 0.78)
        else:
            sill_size = (sill_depth, inner_width + profile * 1.35, profile * 0.78)
        parts.append(add_beveled_box(
            f"{item}_Sill", sill_size,
            location(bay_along, sill_projection * 0.5, base_z + profile * 0.39),
            stone, bevel,
        ))

        for mullion_index in range(mullions):
            offset = inner_width * ((mullion_index + 1) / (mullions + 1) - 0.5)
            if x_aligned:
                size = (profile * 0.46, depth * 0.72, height * 0.90)
            else:
                size = (depth * 0.72, profile * 0.46, height * 0.90)
            parts.append(add_beveled_box(
                f"{item}_Mullion{mullion_index:02d}", size,
                location(bay_along + offset, -recess_m * 0.42, base_z + height * 0.45),
                stone, bevel * 0.65,
            ))
        for transom_index in range(transoms):
            transom_z = base_z + jamb_height * (transom_index + 1) / (transoms + 1)
            if x_aligned:
                size = (inner_width, depth * 0.72, profile * 0.38)
            else:
                size = (depth * 0.72, inner_width, profile * 0.38)
            parts.append(add_beveled_box(
                f"{item}_Transom{transom_index:02d}", size,
                location(bay_along, -recess_m * 0.42, transom_z),
                stone, bevel * 0.55,
            ))

    if axis == "angle":
        for part in parts[first_part:]:
            part.rotation_euler.z = angle


def _graph_buttress_array(parts: list, spec: dict, mats: dict) -> None:
    """Tapered, stepped buttresses that scale with a facade span."""
    axis = str(spec.get("axis", "front"))
    if axis not in {"front", "rear", "left", "right"}:
        raise ValueError(f"buttress axis {axis!r} is unsupported")
    centre = Vector(tuple(float(value) for value in spec["base_centre"]))
    span = float(spec["span_m"])
    explicit_positions = spec.get("positions_m")
    if explicit_positions is not None:
        offsets = [float(value) for value in explicit_positions]
        if not offsets:
            raise ValueError(f"buttress array {spec.get('id')!r} has no positions")
    else:
        count = max(2, int(spec.get("count", 6)))
        run = max(0.0, span - float(spec.get("edge_inset_m", 0.0)) * 2)
        offsets = [-run / 2 + run * index / max(1, count - 1) for index in range(count)]
    height = float(spec["height_m"])
    base_width = float(spec.get("width_m", 0.72))
    projection = float(spec.get("projection_m", 1.05))
    style = str(spec.get("style", "stepped"))
    mat = _graph_material(mats, spec.get("material", "signature_stone"))
    prefix = str(spec.get("id", "GraphButtress"))
    outward, along = _glazing_axis_vectors(axis)
    if style == "engaged":
        # A shallow continuous pier belongs to the wall plane.  Its collars
        # coincide with the floor courses, avoiding the pasted-on column read
        # of a freestanding, independently stepped buttress.
        floor_courses = [float(value) for value in spec.get("course_levels_m", [])]
        for index, offset in enumerate(offsets):
            datum = centre + along * offset
            shaft_depth = projection * 0.74
            shaft = datum + outward * (shaft_depth / 2)
            shaft.z += height / 2
            shaft_size = (
                (base_width, shaft_depth, height)
                if axis in {"front", "rear"}
                else (shaft_depth, base_width, height)
            )
            parts.append(add_beveled_box(
                f"{prefix}_{index:02d}_Shaft", shaft_size, tuple(shaft), mat,
                min(0.045, base_width * 0.08),
            ))
            foot_h = min(1.05, height * 0.08)
            foot_depth = projection
            foot = datum + outward * (foot_depth / 2)
            foot.z += foot_h / 2
            foot_size = (
                (base_width * 1.18, foot_depth, foot_h)
                if axis in {"front", "rear"}
                else (foot_depth, base_width * 1.18, foot_h)
            )
            parts.append(add_beveled_box(
                f"{prefix}_{index:02d}_Foot", foot_size, tuple(foot), mat, 0.04,
            ))
            for course_index, course_z in enumerate(floor_courses):
                collar = datum + outward * (projection * 0.42)
                collar.z += course_z
                collar_size = (
                    (base_width * 1.14, projection * 0.84, 0.18)
                    if axis in {"front", "rear"}
                    else (projection * 0.84, base_width * 1.14, 0.18)
                )
                parts.append(add_beveled_box(
                    f"{prefix}_{index:02d}_Course{course_index:02d}",
                    collar_size, tuple(collar), mat, 0.025,
                ))
            cap = datum + outward * (projection * 0.34)
            cap.z += height + 0.10
            cap_size = (
                (base_width * 1.12, projection * 0.68, 0.20)
                if axis in {"front", "rear"}
                else (projection * 0.68, base_width * 1.12, 0.20)
            )
            parts.append(add_beveled_box(
                f"{prefix}_{index:02d}_Cap", cap_size, tuple(cap), mat, 0.035,
            ))
        return
    if style != "stepped":
        raise ValueError(f"buttress array {spec.get('id')!r} has unsupported style {style!r}")
    stages = ((0.0, 0.46, 1.0, 1.0), (0.46, 0.34, 0.78, 0.72), (0.80, 0.20, 0.58, 0.48))
    for index, offset in enumerate(offsets):
        datum = centre + along * offset
        for stage_index, (z_frac, h_frac, width_frac, depth_frac) in enumerate(stages):
            stage_h = height * h_frac
            stage_depth = projection * depth_frac
            stage_width = base_width * width_frac
            location = datum + outward * (stage_depth / 2)
            location.z += height * z_frac + stage_h / 2
            size = (
                (stage_width, stage_depth, stage_h)
                if axis in {"front", "rear"}
                else (stage_depth, stage_width, stage_h)
            )
            parts.append(add_beveled_box(
                f"{prefix}_{index:02d}_{stage_index}", size, tuple(location), mat,
                min(0.055, stage_width * 0.10),
            ))
        cap = datum + outward * (projection * 0.25)
        cap.z += height + 0.10
        cap_size = (
            (base_width * 0.70, projection * 0.55, 0.20)
            if axis in {"front", "rear"}
            else (projection * 0.55, base_width * 0.70, 0.20)
        )
        parts.append(add_beveled_box(
            f"{prefix}_{index:02d}_Cap", cap_size, tuple(cap), mat, 0.035,
        ))


def _graph_crenellation_array(parts: list, spec: dict, mats: dict) -> None:
    """Continuous parapet course with independently modeled merlons."""
    axis = str(spec.get("axis", "front"))
    centre = Vector(tuple(float(value) for value in spec["base_centre"]))
    span = float(spec["span_m"])
    count = max(3, int(spec.get("count", round(span / 2.5))))
    depth = float(spec.get("depth_m", 0.72))
    course_h = float(spec.get("course_height_m", 0.42))
    merlon_h = float(spec.get("merlon_height_m", 0.92))
    merlon_ratio = float(spec.get("merlon_width_ratio", 0.54))
    mat = _graph_material(mats, spec.get("material", "signature_stone"))
    prefix = str(spec.get("id", "GraphCrenellation"))
    outward, along = _glazing_axis_vectors(axis)
    plane = centre + outward * (depth / 2)
    course_size = (span, depth, course_h) if axis in {"front", "rear"} else (depth, span, course_h)
    course_location = plane.copy()
    course_location.z += course_h / 2
    parts.append(add_beveled_box(f"{prefix}_Course", course_size, tuple(course_location), mat, 0.045))
    cell = span / count
    for index in range(count):
        location = plane + along * (-span / 2 + cell * (index + 0.5))
        location.z += course_h + merlon_h / 2
        size = (
            (cell * merlon_ratio, depth, merlon_h)
            if axis in {"front", "rear"}
            else (depth, cell * merlon_ratio, merlon_h)
        )
        parts.append(add_beveled_box(
            f"{prefix}_Merlon{index:02d}", size, tuple(location), mat, 0.05,
        ))


def _graph_pinnacle_array(parts: list, spec: dict, mats: dict) -> None:
    """Octagonal shafts and tapered caps for tower and parapet silhouette."""
    axis = str(spec.get("axis", "front"))
    centre = Vector(tuple(float(value) for value in spec["base_centre"]))
    span = float(spec["span_m"])
    count = max(2, int(spec.get("count", 4)))
    shaft_h = float(spec.get("shaft_height_m", 1.25))
    cap_h = float(spec.get("cap_height_m", 0.75))
    radius = float(spec.get("radius_m", 0.22))
    outward_offset = float(spec.get("outward_offset_m", 0.0))
    mat = _graph_material(mats, spec.get("material", "signature_stone"))
    prefix = str(spec.get("id", "GraphPinnacle"))
    outward, along = _glazing_axis_vectors(axis)
    for index in range(count):
        location = centre + along * (-span / 2 + span * index / max(1, count - 1)) + outward * outward_offset
        shaft_location = location.copy()
        shaft_location.z += shaft_h / 2
        parts.append(add_cylinder(
            f"{prefix}_Shaft{index:02d}", radius, shaft_h, tuple(shaft_location), mat, 8,
        ))
        cap_location = location.copy()
        cap_location.z += shaft_h + cap_h / 2
        parts.append(add_cone(
            f"{prefix}_Cap{index:02d}", radius * 1.05, cap_h, tuple(cap_location), mat, 8,
        ))


def _graph_oriel_array(parts: list, spec: dict, mats: dict) -> None:
    """Projecting multi-storey window bays with corbels, glass and tracery bars."""
    axis = str(spec.get("axis", "front"))
    if axis != "front":
        raise ValueError("oriel array currently supports the front facade only")
    cx, facade_y, _ = (float(value) for value in spec["centre"])
    positions = [float(value) for value in (spec.get("positions_x") or [cx])]
    levels = [float(value) for value in (spec.get("levels_z") or [8.0])]
    width = float(spec.get("width_m", 3.2))
    height = float(spec.get("height_m", 4.2))
    projection = float(spec.get("projection_m", 1.05))
    stone = _graph_material(mats, spec.get("material", "signature_stone"))
    glass = _graph_material(mats, spec.get("glass_material", "glass"))
    prefix = str(spec.get("id", "GraphOriel"))
    for position_index, x in enumerate(positions):
        for level_index, z in enumerate(levels):
            tag = f"{prefix}_{position_index:02d}_{level_index:02d}"
            body_y = facade_y - projection / 2
            front_y = facade_y - projection - 0.035
            parts.append(add_beveled_box(
                f"{tag}_Top", (width + 0.38, projection + 0.16, 0.24),
                (x, body_y, z + height / 2), stone, 0.045,
            ))
            parts.append(add_beveled_box(
                f"{tag}_Base", (width + 0.42, projection + 0.20, 0.28),
                (x, body_y, z - height / 2), stone, 0.05,
            ))
            for side in (-1, 1):
                parts.append(add_beveled_box(
                    f"{tag}_Jamb{side}", (0.22, projection, height),
                    (x + side * width / 2, body_y, z), stone, 0.032,
                ))
            parts.append(add_box(
                f"{tag}_Glass", (width - 0.34, 0.055, height - 0.42),
                (x, front_y, z), glass,
            ))
            add_frame_bars(
                parts, f"{tag}_Tracery", "front", (x, front_y - 0.035, z),
                width - 0.48, height - 0.56, 0.12, stone, profile=0.11, mullions="double",
            )
            # Three descending corbel blocks terminate the projection in a
            # tapered stone bracket instead of a floating rectangular bay.
            for corbel_index, scale in enumerate((0.72, 0.48, 0.26)):
                corbel_h = 0.22
                parts.append(add_beveled_box(
                    f"{tag}_Corbel{corbel_index}",
                    (width * scale, projection * scale, corbel_h),
                    (x, facade_y - projection * scale / 2, z - height / 2 - 0.16 - corbel_index * 0.20),
                    stone, 0.035,
                ))


def _graph_balcony_array(parts: list, spec: dict, mats: dict) -> None:
    """Segmented, supported balcony bands for European perimeter blocks.

    A balcony is not a black line floating over a facade: every segment gets a
    stone slab, a shadow return, end rails, regularly spaced pickets and small
    corbels.  ``segments`` keeps individual apartments legible while
    ``levels_z`` lets fixed podium/crown zones remain untouched.
    """
    axis = str(spec.get("axis", "front"))
    centre = Vector(tuple(float(value) for value in spec["centre"]))
    span = float(spec["span_m"])
    levels = [float(value) for value in spec.get("levels_z", [])]
    if not levels:
        raise ValueError(f"balcony array {spec.get('id')!r} has no levels_z")
    segment_count = max(1, int(spec.get("segments", 4)))
    gap = max(0.0, float(spec.get("segment_gap_m", 0.45)))
    depth = float(spec.get("depth_m", 0.92))
    slab_h = float(spec.get("slab_height_m", 0.16))
    rail_h = float(spec.get("rail_height_m", 1.02))
    pickets = max(3, int(spec.get("pickets_per_segment", 7)))
    slab_mat = _graph_material(mats, spec.get("slab_material", "signature_stone"))
    rail_mat = _graph_material(mats, spec.get("rail_material", "signature_metal"))
    shadow_mat = _graph_material(mats, spec.get("shadow_material", "massing_joint"))
    prefix = str(spec.get("id", "GraphBalcony"))
    outward, along = _glazing_axis_vectors(axis)
    cell = span / segment_count
    segment_span = max(0.8, cell - gap)
    rail_profile = min(0.055, segment_span * 0.03)

    def member_size(along_size: float, outward_size: float, z_size: float) -> tuple[float, float, float]:
        return (
            (along_size, outward_size, z_size)
            if axis in {"front", "rear"}
            else (outward_size, along_size, z_size)
        )

    for level_index, z in enumerate(levels):
        for segment_index in range(segment_count):
            offset = -span / 2 + cell * (segment_index + 0.5)
            datum = centre + along * offset
            slab_centre = datum + outward * (depth / 2)
            slab_centre.z = z
            parts.append(add_beveled_box(
                f"{prefix}_{level_index:02d}_{segment_index:02d}_Slab",
                member_size(segment_span, depth, slab_h), tuple(slab_centre), slab_mat, 0.035,
            ))
            shadow = datum + outward * (depth * 0.58)
            shadow.z = z - slab_h * 0.72
            parts.append(add_box(
                f"{prefix}_{level_index:02d}_{segment_index:02d}_Shadow",
                member_size(segment_span * 0.92, depth * 0.36, 0.045), tuple(shadow), shadow_mat,
            ))
            front = datum + outward * depth
            front.z = z + slab_h / 2 + rail_h
            parts.append(add_beveled_box(
                f"{prefix}_{level_index:02d}_{segment_index:02d}_TopRail",
                member_size(segment_span, rail_profile, rail_profile), tuple(front), rail_mat, 0.01,
            ))
            for picket_index in range(pickets + 1):
                picket = datum + along * (-segment_span / 2 + segment_span * picket_index / pickets) + outward * depth
                picket.z = z + slab_h / 2 + rail_h / 2
                parts.append(add_box(
                    f"{prefix}_{level_index:02d}_{segment_index:02d}_Picket{picket_index:02d}",
                    member_size(rail_profile * 0.62, rail_profile, rail_h), tuple(picket), rail_mat,
                ))
            for end_index, end_offset in enumerate((-segment_span / 2, segment_span / 2)):
                end = datum + along * end_offset + outward * (depth / 2)
                end.z = z + slab_h / 2 + rail_h
                parts.append(add_box(
                    f"{prefix}_{level_index:02d}_{segment_index:02d}_EndTop{end_index}",
                    member_size(rail_profile, depth, rail_profile), tuple(end), rail_mat,
                ))
                for post_index, outward_ratio in enumerate((0.08, 0.92)):
                    post = datum + along * end_offset + outward * (depth * outward_ratio)
                    post.z = z + slab_h / 2 + rail_h / 2
                    parts.append(add_box(
                        f"{prefix}_{level_index:02d}_{segment_index:02d}_EndPost{end_index}_{post_index}",
                        member_size(rail_profile, rail_profile, rail_h), tuple(post), rail_mat,
                    ))
            # Paired tapered-looking corbel blocks visually attach the slab to
            # the wall without the cost of a unique sculpted bracket mesh.
            for corbel_index, corbel_offset in enumerate((-segment_span * 0.28, segment_span * 0.28)):
                corbel = datum + along * corbel_offset + outward * (depth * 0.22)
                corbel.z = z - 0.24
                parts.append(add_beveled_box(
                    f"{prefix}_{level_index:02d}_{segment_index:02d}_Corbel{corbel_index}",
                    member_size(0.16, depth * 0.44, 0.34), tuple(corbel), slab_mat, 0.025,
                ))


def _graph_corbel_array(parts: list, spec: dict, mats: dict) -> None:
    """Small masonry blocks repeated along one or more true construction courses."""
    axis = str(spec.get("axis", "front"))
    centre = Vector(tuple(float(value) for value in spec["centre"]))
    span = float(spec["span_m"])
    count = max(3, int(spec.get("count", round(span / 0.8))))
    levels = [float(value) for value in spec.get("levels_z", [])]
    if not levels:
        raise ValueError(f"corbel array {spec.get('id')!r} has no levels_z")
    depth = float(spec.get("depth_m", 0.42))
    height = float(spec.get("height_m", 0.24))
    cell = span / count
    width = min(cell * float(spec.get("width_ratio", 0.46)), float(spec.get("max_width_m", 0.42)))
    mat = _graph_material(mats, spec.get("material", "primary"))
    prefix = str(spec.get("id", "GraphCorbels"))
    outward, along = _glazing_axis_vectors(axis)
    size = (width, depth, height) if axis in {"front", "rear"} else (depth, width, height)
    for level_index, z in enumerate(levels):
        for index in range(count):
            location = centre + along * (-span / 2 + cell * (index + 0.5)) + outward * (depth / 2)
            location.z = z
            parts.append(add_beveled_box(
                f"{prefix}_{level_index:02d}_{index:02d}", size, tuple(location), mat, min(0.025, height * 0.10),
            ))


def _apply_massing_skin_uv(obj: bpy.types.Object) -> None:
    """Restore exact 0..1 rectified-elevation UVs after ``join_as`` box projection."""
    mesh = obj.data
    uv_layer = mesh.uv_layers.get("UVMap") or mesh.uv_layers.new(name="UVMap")
    mesh.uv_layers.active = uv_layer
    for polygon in mesh.polygons:
        if polygon.material_index >= len(mesh.materials):
            continue
        material = mesh.materials[polygon.material_index]
        if not material or not material.get("massing_skin"):
            continue
        axis = str(material.get("massing_skin_axis", "front"))
        u_min = float(material.get("massing_skin_u_min", 0.0))
        u_max = float(material.get("massing_skin_u_max", 1.0))
        z_min = float(material.get("massing_skin_z_min", 0.0))
        z_max = float(material.get("massing_skin_z_max", 1.0))
        v_min = float(material.get("massing_skin_v_min", 0.0))
        v_max = float(material.get("massing_skin_v_max", 1.0))
        tex_u_min = float(material.get("massing_skin_tex_u_min", 0.0))
        tex_u_max = float(material.get("massing_skin_tex_u_max", 1.0))
        span_u, span_v = max(u_max - u_min, 1e-6), max(z_max - z_min, 1e-6)
        flip_u = bool(material.get("massing_skin_flip_u", False))
        for loop_index in polygon.loop_indices:
            coordinate = mesh.vertices[mesh.loops[loop_index].vertex_index].co
            if axis in ("front", "rear"):
                along = coordinate.x
            elif axis in ("left", "right"):
                along = coordinate.y
            elif axis == "angle":
                along = (
                    (coordinate.x - float(material.get("massing_skin_origin_x", 0.0)))
                    * float(material.get("massing_skin_along_x", 1.0))
                    + (coordinate.y - float(material.get("massing_skin_origin_y", 0.0)))
                    * float(material.get("massing_skin_along_y", 0.0))
                )
            else:
                continue
            u = (along - u_min) / span_u
            if flip_u:
                u = 1.0 - u
            u = tex_u_min + u * (tex_u_max - tex_u_min)
            v = v_min + (coordinate.z - z_min) / span_v * (v_max - v_min)
            uv_layer.data[loop_index].uv = (u, v)


def _consolidate_massing_skin_materials(obj: bpy.types.Object) -> None:
    """Collapse UV-bound material clones after their vertex UVs are baked.

    Each elevation needs temporary per-surface bounds while the joined mesh is
    reconstructed. Once UVs live on the vertices, those shader clones are
    identical and only inflate runtime draw-call/material counts.
    """
    mesh = obj.data
    for index, material in enumerate(mesh.materials):
        if material is None or not material.get("massing_skin"):
            continue
        canonical_name = str(material.get("massing_skin_canonical") or "")
        canonical = bpy.data.materials.get(canonical_name)
        if canonical is not None and canonical != material:
            mesh.materials[index] = canonical


def build_massing_graph(grammar: dict, mats: dict) -> bpy.types.Object:
    """Build a single landmark asset from an opt-in ``massing-graph@1`` recipe.

    The ordinary repeatable modules remain available as a fallback. Only the
    assembled hero GLB uses this semantic graph, making the pilot reversible
    and safe for every archetype that does not yet define one.
    """
    graph = grammar.get("massing_graph") or {}
    if graph.get("schema") != "massing-graph@1":
        raise ValueError(f"unsupported massing graph schema {graph.get('schema')!r}")
    parts: list[bpy.types.Object] = []
    for node in graph.get("nodes", []):
        kind = node.get("kind")
        location = tuple(float(value) for value in node["location"])
        if kind == "box":
            size = tuple(float(value) for value in node["size"])
            part = add_beveled_box(
                str(node["id"]), size, location,
                _graph_material(mats, node.get("material")), float(node.get("bevel_m", 0.025)),
            )
            if node.get("rotation_z_deg") is not None:
                part.rotation_euler.z = math.radians(float(node["rotation_z_deg"]))
            parts.append(part)
        elif kind == "chamfered_box":
            size = tuple(float(value) for value in node["size"])
            parts.append(add_chamfered_box(
                str(node["id"]), size, location,
                _graph_material(mats, node.get("material")),
                float(node.get("chamfer_m", min(size[0], size[1]) * 0.12)),
                float(node.get("bevel_m", 0.05)),
            ))
        elif kind == "gable_roof":
            size = tuple(float(value) for value in node["size"])
            parts.append(add_gable_roof(
                str(node["id"]), size, location,
                _graph_material(mats, node.get("material")), float(node.get("bevel_m", 0.05)),
                str(node.get("ridge_axis", "y")),
            ))
        elif kind == "hipped_roof":
            size = tuple(float(value) for value in node["size"])
            parts.append(add_hipped_roof(
                str(node["id"]), size, location,
                _graph_material(mats, node.get("material")), float(node.get("bevel_m", 0.05)),
                str(node.get("ridge_axis", "x")),
                float(node["ridge_inset_m"]) if node.get("ridge_inset_m") is not None else None,
            ))
        elif kind == "cylinder":
            part = add_cylinder(
                str(node["id"]), float(node["radius_m"]), float(node["height_m"]), location,
                _graph_material(mats, node.get("material")), int(node.get("vertices", 24)),
            )
            if node.get("rotation_z_deg") is not None:
                part.rotation_euler.z = math.radians(float(node["rotation_z_deg"]))
            parts.append(part)
        elif kind == "cone":
            part = add_cone(
                str(node["id"]), float(node["radius_m"]), float(node["height_m"]), location,
                _graph_material(mats, node.get("material")), int(node.get("vertices", 24)),
            )
            if node.get("rotation_z_deg") is not None:
                part.rotation_euler.z = math.radians(float(node["rotation_z_deg"]))
            parts.append(part)
        else:
            raise ValueError(f"massing graph node {node.get('id')!r} has unsupported kind {kind!r}")

    for assembly in graph.get("assemblies", []):
        kind = assembly.get("kind")
        if kind == "column_array":
            _graph_column_array(parts, assembly, mats)
        elif kind == "classical_portico":
            _graph_classical_portico(parts, assembly, mats)
        elif kind == "shaped_gable_array":
            _graph_shaped_gable_array(parts, assembly, mats)
        elif kind == "chimney_cluster_array":
            _graph_chimney_cluster_array(parts, assembly, mats)
        elif kind == "striped_turret_array":
            _graph_striped_turret_array(parts, assembly, mats)
        elif kind == "curtain_wall":
            _graph_curtain_wall(parts, assembly, mats)
        elif kind == "ribbon_window":
            _graph_curtain_wall(parts, assembly, mats, ribbon=True)
        elif kind == "steps":
            _graph_steps(parts, assembly, mats)
        elif kind == "rowhouse_stoop":
            _graph_rowhouse_stoop(parts, assembly, mats)
        elif kind == "tie_grid":
            _graph_tie_grid(parts, assembly, mats)
        elif kind == "shadow_line":
            _graph_shadow_line(parts, assembly, mats)
        elif kind == "facade_skin":
            _graph_facade_skin(parts, assembly, mats)
        elif kind == "facade_skin_stack":
            _graph_facade_skin_stack(parts, assembly, mats)
        elif kind == "frame_grid":
            _graph_frame_grid(parts, assembly, mats)
        elif kind == "bay_frame_array":
            _graph_bay_frame_array(parts, assembly, mats)
        elif kind == "pointed_portal":
            _graph_pointed_portal(parts, assembly, mats)
        elif kind == "pointed_window_array":
            _graph_pointed_window_array(parts, assembly, mats)
        elif kind == "buttress_array":
            _graph_buttress_array(parts, assembly, mats)
        elif kind == "crenellation_array":
            _graph_crenellation_array(parts, assembly, mats)
        elif kind == "pinnacle_array":
            _graph_pinnacle_array(parts, assembly, mats)
        elif kind == "oriel_array":
            _graph_oriel_array(parts, assembly, mats)
        elif kind == "glazing_overlay":
            _graph_glazing_overlay(parts, assembly, mats)
        elif kind == "balcony_array":
            _graph_balcony_array(parts, assembly, mats)
        elif kind == "corbel_array":
            _graph_corbel_array(parts, assembly, mats)
        else:
            raise ValueError(f"massing graph assembly {assembly.get('id')!r} has unsupported kind {kind!r}")

    if not parts:
        raise ValueError("massing graph contains no renderable nodes or assemblies")
    model = join_as("ASM_MassingGraph", parts)
    _apply_massing_skin_uv(model)
    _consolidate_massing_skin_materials(model)
    # Bevelled plinths and stair nosings can produce a tiny negative export
    # bound even when their design datum is exactly zero.  Runtime placement
    # requires a true bottom-centre origin, so normalize the completed graph
    # mesh after UV assignment (UVs remain unchanged).
    bottom_z = min(vertex.co.z for vertex in model.data.vertices)
    if abs(bottom_z) > 1e-6:
        for vertex in model.data.vertices:
            vertex.co.z -= bottom_z
        model["massing_graph_origin_adjustment_m"] = round(-bottom_z, 6)
    model["massing_graph_schema"] = graph["schema"]
    model["massing_graph_profile"] = graph.get("profile", "default")
    model["massing_graph_node_count"] = len(graph.get("nodes", []))
    model["massing_graph_assembly_count"] = len(graph.get("assemblies", []))
    model["massing_graph_void_count"] = len(graph.get("voids", []))
    return model


def normalize_bottom_origin(model: bpy.types.Object) -> float:
    """Enforce the module contract after projected details and bevels join."""
    bottom_z = min(vertex.co.z for vertex in model.data.vertices)
    if abs(bottom_z) > 1e-6:
        for vertex in model.data.vertices:
            vertex.co.z -= bottom_z
        model["bottom_origin_adjustment_m"] = round(-bottom_z, 6)
    return bottom_z


# ---------------------------------------------------------------------------
# Export / render
# ---------------------------------------------------------------------------

def sanitize_glb_texture_references(path: Path) -> int:
    """Remove exporter-created texture slots that have no image source.

    Blender 5.1 can emit an empty glTF texture for a linked optional emissive
    mask while still referencing that slot from ``emissiveTexture``. Khronos'
    validator accepts the optional source, but Three.js' GLTFLoader attempts to
    read ``image.uri`` and rejects the whole model. Strip only those broken
    texture infos and compact the texture table; all sourced PBR maps remain.

    GLB JSON chunks are space padded, so the repaired JSON can be written back
    without relocating the binary chunk or changing the file length.
    """
    payload = bytearray(path.read_bytes())
    if payload[:4] != b"glTF" or len(payload) < 20:
        return 0
    json_length = int.from_bytes(payload[12:16], "little")
    if payload[16:20] != b"JSON":
        return 0
    start, end = 20, 20 + json_length
    document = json.loads(bytes(payload[start:end]).decode("utf-8").rstrip(" \t\r\n\0"))
    textures = document.get("textures") or []

    def has_source(texture: dict) -> bool:
        if isinstance(texture.get("source"), int):
            return True
        extensions = texture.get("extensions") or {}
        return any(
            isinstance(extension, dict) and isinstance(extension.get("source"), int)
            for extension in extensions.values()
        )

    invalid = {index for index, texture in enumerate(textures) if not has_source(texture)}
    if not invalid:
        return 0

    index_map: dict[int, int] = {}
    compacted: list[dict] = []
    for old_index, texture in enumerate(textures):
        if old_index in invalid:
            continue
        index_map[old_index] = len(compacted)
        compacted.append(texture)
    document["textures"] = compacted

    removed_references = 0

    def repair_material(node: object) -> None:
        nonlocal removed_references
        if isinstance(node, list):
            for item in node:
                repair_material(item)
            return
        if not isinstance(node, dict):
            return
        for key, value in list(node.items()):
            if isinstance(value, dict) and isinstance(value.get("index"), int):
                old_index = value["index"]
                if old_index in invalid:
                    del node[key]
                    removed_references += 1
                    continue
                if old_index in index_map:
                    value["index"] = index_map[old_index]
            repair_material(value)

    repair_material(document.get("materials") or [])
    encoded = json.dumps(document, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if len(encoded) > json_length:
        raise RuntimeError(f"sanitized GLB JSON grew beyond its chunk: {path.name}")
    payload[start:end] = encoded + (b" " * (json_length - len(encoded)))
    path.write_bytes(payload)
    print(
        f"[blender_generate] sanitized {path.name}: removed {len(invalid)} sourceless "
        f"textures and {removed_references} material references"
    )
    return removed_references


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
        # Semantic facade masks make glTF pack photographic colour + alpha
        # into RGBA. PNG inflated a single elevation to 8 MB; WebP preserves
        # that alpha at high visual quality and is natively supported by the
        # Three.js GLTFLoader used in City Prompt.
        export_image_format="WEBP",
        export_image_quality=90,
        export_image_webp_fallback=False,
    )
    try:
        bpy.ops.export_scene.gltf(**kwargs)
    except TypeError:  # older exporter without WebP quality/fallback controls
        kwargs.pop("export_image_quality", None)
        kwargs.pop("export_image_webp_fallback", None)
        bpy.ops.export_scene.gltf(**kwargs)
    sanitize_glb_texture_references(path)


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
    landmark: bool = False,
) -> tuple[str, list[str]]:
    """Render consistent studio, street and aerial views of the assembled kit.

    Context is deterministic and exists only for these review images; it never
    leaks into the modular or assembled GLBs.
    """
    scene = bpy.context.scene
    engine = pick_render_engine(preferred_engine, samples)
    footprint = max(width, depth)

    # The exported GLB carries complementary material LODs. Blender otherwise
    # renders both at once, letting the far baked window sit between physical
    # glass and its lit room card. Capture the original shader links and switch
    # the same way City Prompt does: physical near, baked facade in aerials.
    lod_materials: list[tuple[bpy.types.Material, str, object, object, object]] = []
    for material in bpy.data.materials:
        tag = str(material.get("glazing_lod", ""))
        if tag not in {"far", "near", "physical", "interior"}:
            continue
        if not material.use_nodes or not material.node_tree:
            continue
        output_node = next((node for node in material.node_tree.nodes if node.type == "OUTPUT_MATERIAL"), None)
        if not output_node:
            continue
        surface = output_node.inputs.get("Surface")
        if not surface or not surface.links:
            continue
        original_socket = surface.links[0].from_socket
        transparent = material.node_tree.nodes.get("LOD_Transparent") or material.node_tree.nodes.new(
            "ShaderNodeBsdfTransparent"
        )
        transparent.name = "LOD_Transparent"
        lod_materials.append((material, tag, surface, original_socket, transparent.outputs[0]))

    # Facade-sheet@3 libraries predate semantic glass masks. They have a baked
    # far material but no complementary cut-out/physical-glass material. Keep
    # that baked facade visible in near review renders; otherwise the wall core
    # is exposed as a dark empty field behind the modeled surrounds. Newer
    # masked sheets still switch to their near construction normally.
    near_facade_roles = {
        str(material.get("facade_sheet_role", ""))
        for material, tag, _surface, _original, _transparent in lod_materials
        if tag == "near" and material.get("facade_sheet_role")
    }

    def set_review_glazing_lod(mode: str) -> None:
        for material, tag, surface, original_socket, transparent_socket in lod_materials:
            for link in list(surface.links):
                material.node_tree.links.remove(link)
            role = str(material.get("facade_sheet_role", ""))
            if mode == "far":
                enabled = tag == "far"
            elif tag == "far":
                enabled = not role or role not in near_facade_roles
            else:
                enabled = True
            material.node_tree.links.new(original_socket if enabled else transparent_socket, surface)

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
    sun_data.energy = 1.55 if landmark else 1.35
    sun_data.angle = math.radians(2.8 if landmark else 4.0)
    if landmark:
        sun_data.color = (1.0, 0.90, 0.78)
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
    if engine.startswith("BLENDER_EEVEE") and hasattr(scene, "eevee"):
        # Principled transmission needs Eevee's screen-ray path to resolve the
        # occupied room cards behind the pane. Without it, transmissive glass
        # collapses to a pale opaque swatch even though the exported material
        # is physically correct.
        if hasattr(scene.eevee, "use_raytracing"):
            scene.eevee.use_raytracing = True
        if hasattr(scene.eevee, "ray_tracing_method"):
            scene.eevee.ray_tracing_method = "SCREEN"

    dist = max(footprint * 2.15, focus_height * 1.95)
    context_dist = max(footprint * 4.2, focus_height * 3.5)
    views = (
        ("preview", (-dist * 0.72, -dist * 0.92, focus_height * 0.68), (0.0, 0.0, focus_height * 0.43), 43),
        *((
            # Pull back enough to retain the roof silhouette and projecting
            # eaves. Cropping those features made softened/gabled buildings
            # read as boxes even when their authored geometry was present.
            ("archetype_match", (-width * 0.88, -(depth / 2 + max(64.0, focus_height * 2.15)), focus_height * 0.50),
             (-1.0, -1.0, focus_height * 0.42), 50),
        ) if landmark else ()),
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
        set_review_glazing_lod("far" if context_visible else "near")
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

    # Leave the saved .blend with the authored shader graphs rather than the
    # last review camera's temporary LOD state.
    for material, _tag, surface, original_socket, _transparent_socket in lod_materials:
        for link in list(surface.links):
            material.node_tree.links.remove(link)
        material.node_tree.links.new(original_socket, surface)

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


def _resolved_massing_graph(grammar: dict, floors: int) -> dict | None:
    """Use a landmark graph only at its authored reference dimensions.

    The repeatable LEGO modules are the authoritative path for user-drawn
    footprints and floor counts. Falling back to that stack prevents a fixed
    showcase graph from silently ignoring City Prompt dimensions.
    """
    graph = grammar.get("massing_graph")
    if not graph:
        return None
    reference = graph.get("reference_dimensions")
    if not reference:
        return graph
    dims = grammar["dimensions"]
    matches = (
        abs(float(dims["width_m"]) - float(reference["width_m"])) <= 0.01
        and abs(float(dims["depth_m"]) - float(reference["depth_m"])) <= 0.01
        and int(floors) == int(reference["floors"])
    )
    if matches:
        return graph
    print(
        "[blender_generate] landmark graph bypassed for non-reference dimensions; "
        f"assembling parametric LEGO stack {dims['width_m']}x{dims['depth_m']}m / {floors} floors"
    )
    return None


FOOTPRINT_PROFILES = ("rectangle", "l_shape", "u_shape", "courtyard")


def footprint_segments(
    profile: str,
    target_width_m: float,
    target_depth_m: float,
    native_width_m: float,
    native_depth_m: float,
    wing_depth_m: float | None = None,
) -> list[dict]:
    """Return a renderer-neutral set of rectangular streetwall segments.

    The exported LEGO modules remain ordinary rectangular, bottom-centred
    pieces. Non-rectangular buildings are unions of those pieces, which is the
    same position/rotation contract consumed by City Prompt recipes. Keeping
    this layout explicit also makes the assembled preview an honest test of
    the runtime path rather than a one-off bespoke mesh.
    """
    if profile not in FOOTPRINT_PROFILES:
        raise ValueError(f"unsupported footprint profile {profile!r}; choose from {FOOTPRINT_PROFILES}")
    width = float(target_width_m)
    depth = float(target_depth_m)
    native_width = float(native_width_m)
    native_depth = float(native_depth_m)
    if min(width, depth, native_width, native_depth) <= 0:
        raise ValueError("footprint and native module dimensions must be positive")

    if profile == "rectangle":
        return [{
            "id": "main", "centre_x_m": 0.0, "centre_y_m": 0.0,
            "length_m": width, "thickness_m": depth, "rotation_degrees": 0.0,
        }]

    # A real perimeter block needs a credible occupied wing. Prefer the
    # authored segment depth and only clamp it when the drawn parcel is too
    # small to retain a useful court/notch.
    requested_wing = float(wing_depth_m) if wing_depth_m else native_depth
    maximum_wing = max(5.5, min(width, depth) * 0.46)
    wing = min(max(5.5, requested_wing), maximum_wing)
    segments = [{
        "id": "front", "centre_x_m": 0.0, "centre_y_m": -(depth - wing) / 2,
        "length_m": width, "thickness_m": wing, "rotation_degrees": 0.0,
    }]
    if profile == "l_shape":
        segments.append({
            "id": "left_return", "centre_x_m": -(width - wing) / 2, "centre_y_m": 0.0,
            "length_m": depth, "thickness_m": wing, "rotation_degrees": 90.0,
        })
    elif profile == "u_shape":
        segments.extend([
            {
                "id": "left_return", "centre_x_m": -(width - wing) / 2, "centre_y_m": 0.0,
                "length_m": depth, "thickness_m": wing, "rotation_degrees": 90.0,
            },
            {
                "id": "right_return", "centre_x_m": (width - wing) / 2, "centre_y_m": 0.0,
                "length_m": depth, "thickness_m": wing, "rotation_degrees": 90.0,
            },
        ])
    else:  # courtyard
        segments.extend([
            {
                "id": "rear", "centre_x_m": 0.0, "centre_y_m": (depth - wing) / 2,
                "length_m": width, "thickness_m": wing, "rotation_degrees": 0.0,
            },
            {
                "id": "left_return", "centre_x_m": -(width - wing) / 2, "centre_y_m": 0.0,
                "length_m": depth, "thickness_m": wing, "rotation_degrees": 90.0,
            },
            {
                "id": "right_return", "centre_x_m": (width - wing) / 2, "centre_y_m": 0.0,
                "length_m": depth, "thickness_m": wing, "rotation_degrees": 90.0,
            },
        ])
    return segments


def generate(grammar: dict, output: Path, *, floors_override: int | None, keep_blend: bool,
             thumbnail: bool, assembled: bool, modules: bool = True,
             ao: bool = True, ao_resolution: int = 512,
             ao_samples: int = 16, presentation_engine: str = "eevee",
             presentation_samples: int = 48, presentation_view_set: str = "all",
             footprint_profile: str = "rectangle", footprint_width_m: float | None = None,
             footprint_depth_m: float | None = None, wing_depth_m: float | None = None) -> None:
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
    dims.setdefault("crown_height_m", dims["floor_height_m"])

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
        ("floor", "typical_c"),
        ("setback", "upper"),
        ("crown", "crown"),
        ("roof", "default"),
    ]
    if not modules:
        module_specs = []
    height_key = {
        "podium": "podium_height_m", "floor": "floor_height_m",
        "setback": "setback_height_m", "crown": "crown_height_m", "roof": "roof_height_m",
    }

    manifest_modules = []
    if not modules:
        existing_manifest = output / f"{family}_manifest.json"
        if existing_manifest.exists():
            try:
                manifest_modules = list(
                    json.loads(existing_manifest.read_text(encoding="utf-8")).get("modules") or []
                )
            except (OSError, ValueError, TypeError):
                manifest_modules = []
    floor_variants = {
        item["key"]: item for item in grammar.get("facade_graph", {}).get("floor_variants", [])
    }
    for role, variant_key in module_specs:
        reset_scene()
        mats = build_materials(grammar)
        module = build_module(role, grammar, mats, variant_key)
        normalize_bottom_origin(module)
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
            "assembly_class": "repeatable_middle" if role == "floor" else "fixed_semantic",
            "fixed_semantic": role in {"podium", "setback", "crown", "roof"},
            "lod": 0,
            "allowed_levels": variant_spec.get("allowed_levels") or [],
            "filename": glb_path.name,
            "module_family": family,
            "width_m": dims["width_m"],
            "depth_m": dims["depth_m"],
            "height_m": dims[height_key[role]],
            "floor_height_m": dims["floor_height_m"],
            "repeatable_z": role == "floor" and variant_key.startswith("typical_"),
            **({"setback_min_floors": int(grammar["massing"].get("setback_min_floors", 5))}
               if role == "setback" else {}),
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
    setback_min_floors = int(grammar["massing"].get("setback_min_floors", 5))
    use_setback = bool(grammar["massing"].get("has_setback")) and floors >= setback_min_floors
    use_crown = floors >= 3
    standard_floors = max(0, floors - 1 - (1 if use_setback else 0) - (1 if use_crown else 0))

    assembled_meta = None
    engine_used = None
    rendered_views: list[str] = []
    if assembled:
        reset_scene()
        mats = build_materials(grammar)
        stack: list[bpy.types.Object] = []
        target_width = float(footprint_width_m or dims["width_m"])
        target_depth = float(footprint_depth_m or dims["depth_m"])
        segments = footprint_segments(
            footprint_profile, target_width, target_depth,
            float(dims["width_m"]), float(dims["depth_m"]), wing_depth_m,
        )
        z = 0.0
        stack_meta: list[dict] = []

        def level(role: str, level_index: int, variant_key: str = "default") -> None:
            nonlocal z
            module_height = dims[height_key[role]]
            stack_meta.append({
                "role": role, "variant_key": variant_key, "level": level_index,
                "z_m": round(z, 3), "height_m": module_height,
            })
            z += module_height

        massing_graph = (
            _resolved_massing_graph(grammar, floors)
            if footprint_profile == "rectangle"
            and abs(target_width - float(dims["width_m"])) <= 0.01
            and abs(target_depth - float(dims["depth_m"])) <= 0.01
            else None
        )
        if massing_graph:
            landmark = build_massing_graph(grammar, mats)
            stack.append(landmark)
            z = float(massing_graph["height_m"])
            stack_meta.append({
                "role": "massing_graph",
                "variant_key": str(massing_graph.get("profile", "default")),
                "level": 0,
                "z_m": 0.0,
                "height_m": z,
            })
            # A massing graph describes a fixed landmark composition. These
            # flags only describe the legacy stack and must not imply that a
            # graph-based model received another crown or setback module.
            use_setback = False
            use_crown = False
        else:
            level("podium", 0)
            middle_variants = ["typical_a", "typical_b"]
            if "floor_c" in (FACADE_SHEET or {}).get("manifest", {}).get("bands", {}):
                middle_variants.append("typical_c")
            for level_index in range(1, standard_floors + 1):
                level("floor", level_index, middle_variants[(level_index - 1) % len(middle_variants)])
            if use_setback:
                level("setback", floors - (2 if use_crown else 1), "upper")
            if use_crown:
                level("crown", floors - 1, "crown")
            level("roof", floors)

            # Build the same semantic vertical kit on each geographic segment.
            # A single entrance/corner/crown/roof remains fixed within every
            # segment; only the middle floor variants repeat vertically.
            for segment in segments:
                for item in stack_meta:
                    role = str(item["role"])
                    variant_key = str(item["variant_key"])
                    level_index = int(item["level"])
                    module = build_module(role, grammar, mats, variant_key, interior_seed=level_index)
                    normalize_bottom_origin(module)
                    module.name = f"ASM_{segment['id']}_{role}_{variant_key}_{level_index:02d}"
                    module.location = (
                        float(segment["centre_x_m"]),
                        float(segment["centre_y_m"]),
                        float(item["z_m"]),
                    )
                    module.rotation_euler.z = math.radians(float(segment["rotation_degrees"]))
                    module.scale.x = float(segment["length_m"]) / float(dims["width_m"])
                    module.scale.y = float(segment["thickness_m"]) / float(dims["depth_m"])
                    bpy.ops.object.select_all(action="DESELECT")
                    module.select_set(True)
                    bpy.context.view_layer.objects.active = module
                    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                    stack.append(module)

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
            "footprint_profile": footprint_profile,
            "footprint_target": {
                "width_m": round(target_width, 3),
                "depth_m": round(target_depth, 3),
                "wing_depth_m": round(float(segments[0]["thickness_m"]), 3),
                "segments": segments,
            },
            "massing_graph": ({
                "schema": massing_graph.get("schema"),
                "profile": massing_graph.get("profile"),
                "node_count": len(massing_graph.get("nodes", [])),
                "assembly_count": len(massing_graph.get("assemblies", [])),
                "void_count": len(massing_graph.get("voids", [])),
            } if massing_graph else None),
        }
        print(f"[blender_generate] exported {assembled_path.name} (height {z:.2f} m, {floors} floors)")

        if thumbnail:
            try:
                engine_used, rendered_views = render_presentation_views(
                    output, family, z, target_width, target_depth,
                    preferred_engine=presentation_engine, samples=presentation_samples,
                    view_set=presentation_view_set,
                    landmark=bool(grammar.get("massing_graph")),
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
        "footprint_compatibility": grammar.get("footprint_compatibility"),
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
            "runtime_material_profile": (
                "pbr_physical_glazing_v2"
                if FACADE_SHEET["manifest"].get("pbr_lods") else "photo_baked_v1"
            ),
            "geometry_detail_profile": FACADE_SHEET_DETAIL,
            "pbr_channels": ["albedo", "normal", "roughness", "ao", "depth", "emissive"],
            "shadow_neutral": FACADE_SHEET["manifest"].get("shadow_neutral"),
            "bay_strategy": FACADE_SHEET["manifest"].get("bay_strategy"),
            "delivery": FACADE_SHEET["manifest"].get("delivery"),
            "assembly_contract": {
                "fixed": ["podium/entrance", "corner returns", "crown", "roof"],
                "repeatable": ["typical_a", "typical_b", "typical_c"],
                "side_elevations": "wrapped PBR atlas with physical recessed glazing",
                "elevation_coverage": {
                    "front": "near/far PBR facade plus physical glazing",
                    "left": "always-visible wrapped secondary elevation",
                    "right": "always-visible wrapped secondary elevation",
                    "rear": "always-visible wrapped secondary elevation",
                },
                "abutting_policy": (
                    "author all four elevations in the asset; City Prompt may occlude an elevation "
                    "only when site geometry confirms a true party-wall condition"
                ),
            },
        } if FACADE_SHEET else None),
        "massing_graph": ({
            "schema": grammar["massing_graph"].get("schema"),
            "profile": grammar["massing_graph"].get("profile"),
            "description": grammar["massing_graph"].get("description"),
            "target_views": grammar["massing_graph"].get("target_views", []),
        } if grammar.get("massing_graph") else None),
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
    parser.add_argument(
        "--assembled-only", action="store_true",
        help="reuse module metadata/files from the existing manifest and rebuild only the assembled model",
    )
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
    parser.add_argument("--footprint-profile", choices=FOOTPRINT_PROFILES, default="rectangle",
                        help="assembled-preview geographic footprint made from rectangular LEGO segments")
    parser.add_argument("--footprint-width", type=float, default=None,
                        help="overall assembled footprint width; defaults to grammar/module width")
    parser.add_argument("--footprint-depth", type=float, default=None,
                        help="overall assembled footprint depth; defaults to grammar/module depth")
    parser.add_argument("--wing-depth", type=float, default=None,
                        help="occupied streetwall thickness for L/U/courtyard profiles")
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
        modules=not args.assembled_only,
        ao=not args.no_ao,
        ao_resolution=args.ao_resolution,
        ao_samples=args.ao_samples,
        presentation_engine=args.presentation_engine,
        presentation_samples=args.presentation_samples,
        presentation_view_set=args.presentation_view_set,
        footprint_profile=args.footprint_profile,
        footprint_width_m=args.footprint_width,
        footprint_depth_m=args.footprint_depth,
        wing_depth_m=args.wing_depth,
    )


if __name__ == "__main__":
    main()
