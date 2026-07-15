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

GENERATOR_VERSION = "0.3.0"
SUPPORTED_SCHEMA_VERSION = 1

# Set from CLI in main(); make_material reads them so build_materials stays a
# pure function of the grammar.
TEXTURES_DIR: Path | None = None
UV_TILE_METRES = 2.0  # one texture tile covers 2 m of facade (matches generate_textures.py prompts)


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
    tex_dir = TEXTURES_DIR / texture_key
    albedo = tex_dir / "albedo.jpg"
    if not albedo.exists():
        return None
    found = {"albedo": albedo}
    for slot, filename in (("normal", "normal.png"), ("roughness", "roughness.jpg")):
        path = tex_dir / filename
        if path.exists():
            found[slot] = path
    return found


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
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = float(spec.get("metallic", 0.0))
    bsdf.inputs["Roughness"].default_value = float(spec.get("roughness", 0.6))
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
        links.new(albedo_node.outputs["Color"], bsdf.inputs["Base Color"])

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
            normal_map.location = (-180, -340)
            links.new(normal_tex.outputs["Color"], normal_map.inputs["Color"])
            links.new(normal_map.outputs["Normal"], bsdf.inputs["Normal"])

        mat["texture_key"] = spec.get("texture_key")
    return mat


def build_materials(grammar: dict) -> dict[str, bpy.types.Material]:
    materials = grammar["materials"]
    return {
        "primary": make_material("MAT_Facade_Primary", materials["primary"]),
        "secondary": make_material("MAT_Facade_Secondary", materials["secondary"]),
        "accent": make_material("MAT_Accent", materials["accent"]),
        "glass": make_material("MAT_Glass", materials["glass"]),
        "concrete": make_material("MAT_Concrete", materials["concrete"]),
        "roof": make_material("MAT_Roof", materials["roof"]),
        "green_roof": make_material("MAT_GreenRoof", materials["green_roof"]),
    }


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


def add_prism(name: str, verts: list[tuple[float, float, float]], faces: list[tuple[int, ...]], mat) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


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
        for loop_index in poly.loop_indices:
            co = mesh.vertices[mesh.loops[loop_index].vertex_index].co
            if az >= ax and az >= ay:
                u, v = co.x, co.y
            elif ax >= ay:
                u, v = co.y, co.z
            else:
                u, v = co.x, co.z
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

    for mat in mesh.materials:
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
        # bake writes into each material's ACTIVE image texture node
        for node in nodes:
            node.select = node is tex_node
        nodes.active = tex_node

    scene = bpy.context.scene
    previous_engine = scene.render.engine
    try:
        scene.render.engine = "CYCLES"
        scene.cycles.samples = samples
        scene.cycles.device = "CPU"
        try:  # AO ray distance: architectural scale, not world-sized
            scene.world.light_settings.distance = 10.0
        except AttributeError:
            pass
        bpy.ops.object.bake(type="AO", margin=8, use_clear=True)
        image.pack()
        return True
    except Exception as exc:  # pragma: no cover - depends on Cycles availability
        print(f"[blender_generate] WARNING: AO bake failed for {obj.name}: {exc}")
        for mat in mesh.materials:
            nodes = mat.node_tree.nodes
            for stale in [n for n in nodes if n.name.startswith("AO_BAKE")]:
                nodes.remove(stale)
        return False
    finally:
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
) -> None:
    """A row of glazing+frame pairs flush on one wall. Windows sit slightly proud
    of the wall plane so they read at a distance without boolean cuts."""
    bay = wall_length / bay_count
    window_w = min(window_w, bay * 0.78)
    for i in range(bay_count):
        along = -wall_length / 2 + bay * (i + 0.5)
        z_center = z0 + sill + window_h / 2
        if axis in ("front", "rear"):
            sign = -1.0 if axis == "front" else 1.0
            glass_loc = (along, sign * (wall_offset + 0.03), z_center)
            frame_loc = (along, sign * (wall_offset + 0.015), z_center)
            glass_size = (window_w, 0.06, window_h)
            frame_size = (window_w + frame_depth * 2, 0.05, window_h + frame_depth * 2)
        else:
            sign = -1.0 if axis == "left" else 1.0
            glass_loc = (sign * (wall_offset + 0.03), along, z_center)
            frame_loc = (sign * (wall_offset + 0.015), along, z_center)
            glass_size = (0.06, window_w, window_h)
            frame_size = (0.05, window_w + frame_depth * 2, window_h + frame_depth * 2)
        parts.append(add_box(f"{prefix}_Frame_{axis}_{i:02d}", frame_size, frame_loc, mats["accent"]))
        parts.append(add_box(f"{prefix}_Glass_{axis}_{i:02d}", glass_size, glass_loc, mats["glass"]))


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

    for i in range(bay_count):
        x = -w / 2 + bay * (i + 0.5)
        has_balcony = (not setback) and balcony_mode == "projecting" and (i % balcony_every == 0)
        z_center = sill + window_h / 2
        # Window (door-height glazing behind balconies)
        glass_h = h * 0.72 if has_balcony else window_h
        glass_z = 0.25 + glass_h / 2 if has_balcony else z_center
        parts.append(add_box(f"Floor_Frame_{i:02d}", (window_w + 0.14, 0.05, glass_h + 0.14),
                             (x, -(front_wall_y + 0.015), glass_z), mats["accent"]))
        parts.append(add_box(f"Floor_Glass_{i:02d}", (window_w, 0.06, glass_h),
                             (x, -(front_wall_y + 0.03), glass_z), mats["glass"]))
        if has_balcony:
            bw = bay * 0.85
            by = -(front_wall_y + balcony_depth / 2)
            parts.append(add_box(f"Floor_BalconySlab_{i:02d}", (bw, balcony_depth, 0.14), (x, by, 0.2), mats["concrete"]))
            # Solid balustrade (reads as timber/wood panel via secondary material)
            parts.append(add_box(f"Floor_Balustrade_{i:02d}", (bw, 0.06, 1.02),
                                 (x, -(front_wall_y + balcony_depth - 0.03), 0.27 + 0.51), mats["secondary"]))
            parts.append(add_box(f"Floor_BalustradeL_{i:02d}", (0.06, balcony_depth - 0.06, 1.02),
                                 (x - bw / 2 + 0.03, by, 0.27 + 0.51), mats["secondary"]))
            parts.append(add_box(f"Floor_BalustradeR_{i:02d}", (0.06, balcony_depth - 0.06, 1.02),
                                 (x + bw / 2 - 0.03, by, 0.27 + 0.51), mats["secondary"]))

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
        if roof.get("green_roof"):
            parts.append(add_box("Roof_GreenSurface", (w - 0.8, d - 0.8, 0.09), (0, 0, slab_h + 0.045), mats["green_roof"]))
        if roof.get("mechanical_screen"):
            mw, md, mh = w * 0.24, d * 0.28, max(0.8, h * 0.75)
            parts.append(add_box("Roof_MechScreen", (mw, md, mh), (w * 0.18, d * 0.12, slab_h + mh / 2), mats["accent"]))

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
        # JPEG keeps textured module GLBs well under the 8 MB budget; PNG
        # albedo sets would triple it. AO/normal accept the mild loss.
        export_image_format="JPEG",
        export_jpeg_quality=85,
    )
    try:
        bpy.ops.export_scene.gltf(**kwargs)
    except TypeError:  # older exporter without export_jpeg_quality
        kwargs.pop("export_jpeg_quality", None)
        bpy.ops.export_scene.gltf(**kwargs)


def triangle_count(obj: bpy.types.Object) -> int:
    obj.data.calc_loop_triangles()
    return len(obj.data.loop_triangles)


def pick_render_engine() -> str:
    scene = bpy.context.scene
    for engine in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "BLENDER_WORKBENCH"):
        try:
            scene.render.engine = engine
            return engine
        except TypeError:
            continue
    return scene.render.engine


def render_thumbnail(path: Path, focus_height: float, footprint: float) -> str:
    """Neutral three-quarter presentation: daylight sun, ground plane, soft sky."""
    scene = bpy.context.scene
    engine = pick_render_engine()

    ground_mat = make_material("MAT_PreviewGround", {"base_color": "#c9c7c2", "roughness": 0.95, "metallic": 0.0})
    ground = add_box("PreviewGround", (footprint * 14, footprint * 14, 0.05), (0, 0, -0.05), ground_mat)

    sun_data = bpy.data.lights.new("PreviewSun", type="SUN")
    sun_data.energy = 3.5
    sun_data.angle = math.radians(3)
    sun = bpy.data.objects.new("PreviewSun", sun_data)
    sun.rotation_euler = (math.radians(50), math.radians(-12), math.radians(-35))
    scene.collection.objects.link(sun)

    cam_data = bpy.data.cameras.new("PreviewCamera")
    cam_data.lens = 42
    cam = bpy.data.objects.new("PreviewCamera", cam_data)
    scene.collection.objects.link(cam)
    dist = max(footprint * 1.9, focus_height * 1.7)
    cam.location = (-dist * 0.78, -dist * 0.95, focus_height * 0.66 + dist * 0.22)
    target = Vector((0.0, 0.0, focus_height * 0.45))
    # Blender cameras look down local -Z with +Y up; track-quat aims it at the building
    direction = target - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam

    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.88, 0.9, 0.93, 1.0)
        bg.inputs[1].default_value = 1.0

    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.filepath = str(path)
    scene.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)

    # Clean up presentation rig so it never leaks into GLB exports
    for obj in (ground, sun, cam):
        bpy.data.objects.remove(obj, do_unlink=True)
    return engine


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def build_module(role: str, grammar: dict, mats: dict) -> bpy.types.Object:
    if role == "podium":
        return build_podium(grammar, mats)
    if role == "floor":
        return build_floor(grammar, mats, setback=False)
    if role == "setback":
        return build_floor(grammar, mats, setback=True)
    if role == "roof":
        return build_roof(grammar, mats)
    raise ValueError(f"unknown module role {role}")


def generate(grammar: dict, output: Path, *, floors_override: int | None, keep_blend: bool,
             thumbnail: bool, assembled: bool, ao: bool = True, ao_resolution: int = 512,
             ao_samples: int = 16) -> None:
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

    roles = ["podium", "floor", "setback", "roof"]
    height_key = {
        "podium": "podium_height_m", "floor": "floor_height_m",
        "setback": "setback_height_m", "roof": "roof_height_m",
    }

    manifest_modules = []
    for role in roles:
        reset_scene()
        mats = build_materials(grammar)
        module = build_module(role, grammar, mats)
        ao_baked = bake_ao(module, ao_resolution, ao_samples) if ao else False
        glb_path = output / f"{family}_{role}.glb"
        export_objects(glb_path, [module])
        manifest_modules.append({
            "role": role,
            "filename": glb_path.name,
            "module_family": family,
            "width_m": dims["width_m"],
            "depth_m": dims["depth_m"],
            "height_m": dims[height_key[role]],
            "floor_height_m": dims["floor_height_m"],
            "repeatable_z": role == "floor",
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
    use_setback = bool(grammar["massing"].get("has_setback")) and floors >= 3
    standard_floors = max(0, floors - 1 - (1 if use_setback else 0))

    assembled_meta = None
    engine_used = None
    if assembled:
        reset_scene()
        mats = build_materials(grammar)
        stack: list[bpy.types.Object] = []
        z = 0.0

        def place(role: str, level: int) -> None:
            nonlocal z
            module = build_module(role, grammar, mats)
            module.name = f"ASM_{role}_{level:02d}"
            module.location.z = z
            bpy.ops.object.select_all(action="DESELECT")
            module.select_set(True)
            bpy.context.view_layer.objects.active = module
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            stack.append(module)
            z += dims[height_key[role]]

        place("podium", 0)
        for level in range(1, standard_floors + 1):
            place("floor", level)
        if use_setback:
            place("setback", floors - 1)
        place("roof", floors)

        assembled_path = output / f"{family}_assembled.glb"
        export_objects(assembled_path, stack)
        assembled_meta = {
            "filename": assembled_path.name,
            "floors": floors,
            "uses_setback": use_setback,
            "height_m": round(z, 3),
            "triangle_count": sum(triangle_count(obj) for obj in stack),
        }
        print(f"[blender_generate] exported {assembled_path.name} (height {z:.2f} m, {floors} floors)")

        if thumbnail:
            try:
                engine_used = render_thumbnail(output / f"{family}_preview.png", z, max(dims["width_m"], dims["depth_m"]))
                print(f"[blender_generate] rendered {family}_preview.png via {engine_used}")
            except Exception as exc:  # pragma: no cover - render backends vary by machine
                print(f"[blender_generate] WARNING: thumbnail render failed: {exc}")

        if keep_blend:
            blend_path = output / f"{family}.blend"
            bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
            print(f"[blender_generate] saved {blend_path.name}")

    manifest = {
        "manifest_schema": 2,
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
    )


if __name__ == "__main__":
    main()
