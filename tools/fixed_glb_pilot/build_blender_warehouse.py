"""Build one fixed-size warehouse GLB directly in Blender.

This intentionally avoids the archetype compiler and all modular/LEGO assembly.
The exported asset is a single authored 40 x 20 m building with a bottom-centre
origin, fixed storey count, fixed roof, and fixed facade composition.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


WIDTH = 40.0
DEPTH = 20.0
EAVE_Z = 9.2
RIDGE_Z = 12.5


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.materials, bpy.data.images, bpy.data.cameras, bpy.data.lights):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def solid_material(name: str, color: tuple[float, float, float, float], *, metallic=0.0, roughness=0.6):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def image_material(name: str, root: Path, key: str, *, metallic=0.0, roughness=0.7):
    folder = root / key
    albedo = folder / "albedo.jpg"
    normal = folder / "normal.png"
    rough = folder / "roughness.jpg"
    if not albedo.exists():
        fallback = {
            "red_brick": (0.34, 0.095, 0.045, 1),
            "standing_seam": (0.035, 0.045, 0.055, 1),
            "oak_wood": (0.28, 0.12, 0.045, 1),
        }.get(key, (0.3, 0.3, 0.3, 1))
        return solid_material(name, fallback, metallic=metallic, roughness=roughness)

    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness

    texcoord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (4.0, 4.0, 4.0)
    links.new(texcoord.outputs["UV"], mapping.inputs["Vector"])

    color_tex = nodes.new("ShaderNodeTexImage")
    color_tex.image = bpy.data.images.load(str(albedo), check_existing=True)
    color_tex.extension = "REPEAT"
    links.new(mapping.outputs["Vector"], color_tex.inputs["Vector"])
    links.new(color_tex.outputs["Color"], bsdf.inputs["Base Color"])

    if rough.exists():
        rough_tex = nodes.new("ShaderNodeTexImage")
        rough_tex.image = bpy.data.images.load(str(rough), check_existing=True)
        rough_tex.image.colorspace_settings.name = "Non-Color"
        rough_tex.extension = "REPEAT"
        links.new(mapping.outputs["Vector"], rough_tex.inputs["Vector"])
        links.new(rough_tex.outputs["Color"], bsdf.inputs["Roughness"])
    if normal.exists():
        normal_tex = nodes.new("ShaderNodeTexImage")
        normal_tex.image = bpy.data.images.load(str(normal), check_existing=True)
        normal_tex.image.colorspace_settings.name = "Non-Color"
        normal_tex.extension = "REPEAT"
        normal_map = nodes.new("ShaderNodeNormalMap")
        normal_map.inputs["Strength"].default_value = 0.35
        links.new(mapping.outputs["Vector"], normal_tex.inputs["Vector"])
        links.new(normal_tex.outputs["Color"], normal_map.inputs["Color"])
        links.new(normal_map.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def add_box(name: str, dims, loc, mat, *, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        obj.data.materials.append(mat)
    if bevel > 0:
        mod = obj.modifiers.new("Construction edge", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    return obj


def add_front_window(name, x, z, width, height, mats, y=-10.34):
    glass, metal, interior = mats
    add_box(f"{name}_warm_interior", (width - 0.18, 0.08, height - 0.18), (x, y + 0.13, z), interior)
    add_box(f"{name}_glass", (width - 0.12, 0.055, height - 0.12), (x, y, z), glass)
    frame = 0.085
    for sx in (-width / 2, width / 2):
        add_box(f"{name}_jamb", (frame, 0.12, height), (x + sx, y - 0.035, z), metal, bevel=0.018)
    for sz in (-height / 2, height / 2):
        add_box(f"{name}_rail", (width, 0.12, frame), (x, y - 0.035, z + sz), metal, bevel=0.018)
    for frac in (-0.25, 0.0, 0.25):
        add_box(f"{name}_mullion", (0.065, 0.13, height), (x + width * frac, y - 0.04, z), metal)
    add_box(f"{name}_transom", (width, 0.13, 0.065), (x, y - 0.04, z), metal)


def add_side_window(name, y, z, width, height, mats, x):
    glass, metal, interior = mats
    sign = 1 if x > 0 else -1
    face_x = x + sign * 0.34
    add_box(f"{name}_warm_interior", (0.08, width - 0.18, height - 0.18), (face_x - sign * 0.13, y, z), interior)
    add_box(f"{name}_glass", (0.055, width - 0.12, height - 0.12), (face_x, y, z), glass)
    for sy in (-width / 2, width / 2):
        add_box(f"{name}_jamb", (0.12, 0.085, height), (face_x + sign * 0.035, y + sy, z), metal)
    for sz in (-height / 2, height / 2):
        add_box(f"{name}_rail", (0.12, width, 0.085), (face_x + sign * 0.035, y, z + sz), metal)
    add_box(f"{name}_mullion", (0.13, 0.065, height), (face_x + sign * 0.04, y, z), metal)
    add_box(f"{name}_transom", (0.13, width, 0.065), (face_x + sign * 0.04, y, z), metal)


def add_roof(name, verts, mat):
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    mesh.from_pydata(verts, [], [(0, 1, 2, 3)])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    solidify = obj.modifiers.new("Standing seam roof thickness", "SOLIDIFY")
    solidify.thickness = 0.18
    bevel = obj.modifiers.new("Roof edge", "BEVEL")
    bevel.width = 0.035
    bevel.segments = 2
    return obj


def build(root: Path):
    textures = root / "tools" / "archetype_compiler" / "textures"
    brick = image_material("Aged red brick PBR", textures, "red_brick")
    roof = image_material("Dark standing seam", textures, "standing_seam", metallic=0.55, roughness=0.32)
    timber = image_material("Reclaimed oak", textures, "oak_wood", roughness=0.48)
    metal = solid_material("Bronzed steel frames", (0.035, 0.026, 0.018, 1), metallic=0.72, roughness=0.26)
    glass = solid_material("Warm architectural glazing", (0.18, 0.23, 0.24, 1), metallic=0.05, roughness=0.12)
    interior = solid_material("Occupied warm interior", (0.72, 0.29, 0.075, 1), roughness=0.9)
    concrete = solid_material("Weathered concrete", (0.38, 0.35, 0.31, 1), roughness=0.82)

    # Structure and secondary elevations.
    add_box("foundation", (40.4, 20.4, 0.45), (0, 0, 0.225), concrete, bevel=0.08)
    add_box("rear_wall", (40.0, 0.6, 8.8), (0, 9.7, 4.8), brick, bevel=0.055)
    add_box("left_wall", (0.6, 19.4, 8.8), (-19.7, 0, 4.8), brick, bevel=0.055)
    add_box("right_wall", (0.6, 19.4, 8.8), (19.7, 0, 4.8), brick, bevel=0.055)

    # Front facade is built around real openings, not a window texture on a box.
    add_box("front_sill", (40.0, 0.6, 0.72), (0, -9.7, 0.72), brick, bevel=0.045)
    add_box("front_mid_band", (40.0, 0.72, 0.55), (0, -9.7, 4.48), brick, bevel=0.05)
    add_box("front_head_band", (40.0, 0.72, 0.65), (0, -9.7, 8.86), brick, bevel=0.05)
    bay_pitch = 5.0
    for i in range(9):
        x = -20.0 + i * bay_pitch
        add_box(f"brick_pier_{i:02d}", (0.72, 0.72, 8.4), (x, -9.7, 4.7), brick, bevel=0.045)
    for i in range(8):
        x = -17.5 + i * bay_pitch
        add_front_window(f"ground_bay_{i:02d}", x, 2.43, 4.22, 3.25, (glass, metal, interior))
        add_front_window(f"upper_bay_{i:02d}", x, 6.65, 4.22, 3.55, (glass, metal, interior))

    # Recessed double entrance in the central bay.
    add_box("entrance_recess", (4.0, 0.5, 3.45), (2.5, -9.87, 2.30), metal)
    add_box("entrance_glass_left", (1.72, 0.08, 3.08), (1.57, -10.16, 2.30), glass)
    add_box("entrance_glass_right", (1.72, 0.08, 3.08), (3.43, -10.16, 2.30), glass)
    add_box("entrance_center_mullion", (0.085, 0.14, 3.2), (2.5, -10.22, 2.30), metal)
    add_box("entrance_canopy", (5.2, 1.55, 0.18), (2.5, -10.55, 4.1), metal, bevel=0.045)
    add_box("entrance_step", (5.0, 1.2, 0.18), (2.5, -10.42, 0.56), concrete, bevel=0.04)

    # Preserved loading platform and timber canopy at the left frontage.
    add_box("loading_dock", (9.2, 1.85, 0.55), (-12.0, -10.55, 0.78), timber, bevel=0.06)
    add_box("loading_canopy", (9.4, 1.75, 0.22), (-12.0, -10.48, 4.22), timber, bevel=0.04)
    for x in (-15.8, -12.0, -8.2):
        add_box("loading_post", (0.22, 0.22, 3.4), (x, -11.1, 2.42), timber, bevel=0.025)

    # Side-window arrays make the asset credible in orbit views.
    for side_x in (-19.7, 19.7):
        for row, z in enumerate((2.45, 6.55)):
            for col, y in enumerate((-6.6, -2.2, 2.2, 6.6)):
                add_side_window(f"side_{'r' if side_x > 0 else 'l'}_{row}_{col}", y, z, 3.1, 2.9, (glass, metal, interior), side_x)

    # Authored pitched roof with central glazed monitor.
    add_roof("front_roof", [(-20.35, -10.35, EAVE_Z), (20.35, -10.35, EAVE_Z), (20.35, 0, RIDGE_Z), (-20.35, 0, RIDGE_Z)], roof)
    add_roof("rear_roof", [(-20.35, 0, RIDGE_Z), (20.35, 0, RIDGE_Z), (20.35, 10.35, EAVE_Z), (-20.35, 10.35, EAVE_Z)], roof)
    add_box("ridge_cap", (40.65, 0.28, 0.28), (0, 0, RIDGE_Z + 0.08), metal, bevel=0.08)

    for x in (-12.5, -7.5, -2.5, 2.5, 7.5, 12.5):
        # Low-profile roof lights sit just above the front slope.
        y = -4.7
        z = EAVE_Z + (y + 10.35) / 10.35 * (RIDGE_Z - EAVE_Z) + 0.12
        light = add_box(f"rooflight_{x:+.1f}", (2.7, 1.8, 0.14), (x, y, z), glass, bevel=0.05)
        light.rotation_euler.x = math.radians(17.7)


def world_bounds(objects):
    points = []
    for obj in objects:
        if obj.type != "MESH":
            continue
        points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    lo = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    hi = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return lo, hi


def normalize_to_fixed_bounds(objects):
    root = bpy.data.objects.new("Fixed_40x20m_bottom_centre", None)
    bpy.context.collection.objects.link(root)
    for obj in objects:
        world = obj.matrix_world.copy()
        obj.parent = root
        obj.matrix_world = world
    raw_lo, raw_hi = world_bounds(objects)
    raw_size = raw_hi - raw_lo
    root.scale = (WIDTH / raw_size.x, DEPTH / raw_size.y, RIDGE_Z / raw_size.z)
    bpy.context.view_layer.update()
    lo, hi = world_bounds(objects)
    root.location -= Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    bpy.context.view_layer.update()
    final_lo, final_hi = world_bounds(objects)
    return root, raw_size, final_lo, final_hi


def consolidate_by_material(objects):
    """Apply construction modifiers and join objects into one mesh per material."""
    for obj in list(objects):
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.convert(target="MESH")

    groups = {}
    for obj in objects:
        material = obj.data.materials[0] if obj.data.materials else None
        groups.setdefault(material.name if material else "Unmaterialed", []).append(obj)

    consolidated = []
    for material_name, group in groups.items():
        bpy.ops.object.select_all(action="DESELECT")
        for obj in group:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = group[0]
        bpy.ops.object.join()
        joined = bpy.context.object
        joined.name = f"FIXED_{material_name.replace(' ', '_')}"
        consolidated.append(joined)
    return consolidated


def setup_render(output: Path, objects):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.color = (0.025, 0.035, 0.055)
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.11, 0.14, 0.18, 1)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.55

    ground = add_box("review_ground", (90, 75, 0.22), (0, 0, -0.14), solid_material("Review ground", (0.095, 0.105, 0.115, 1), roughness=0.95))
    bpy.ops.object.light_add(type="SUN", location=(20, -30, 45))
    sun = bpy.context.object
    sun.rotation_euler = (math.radians(28), math.radians(-18), math.radians(-28))
    sun.data.energy = 3.0
    sun.data.angle = math.radians(18)
    bpy.ops.object.light_add(type="AREA", location=(-18, -28, 24))
    key = bpy.context.object
    key.data.energy = 3200
    key.data.shape = "DISK"
    key.data.size = 16

    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.data.lens = 50
    scene.camera = camera

    def point_camera(location, target):
        camera.location = location
        direction = Vector(target) - camera.location
        camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

    views = {
        "street": ((34, -48, 11), (0, 0, 4.5), 54),
        "oblique": ((42, -48, 32), (0, 0, 5.2), 53),
        "aerial": ((44, -54, 60), (0, 0, 3.5), 55),
    }
    for name, (location, target, lens) in views.items():
        camera.data.lens = lens
        point_camera(location, target)
        scene.render.filepath = str(output / f"blender_{name}.png")
        bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(ground, do_unlink=True)
    bpy.data.objects.remove(camera, do_unlink=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    clear_scene()
    build(args.repo_root.resolve())
    building_objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    building_objects = consolidate_by_material(building_objects)
    root, raw_size, lo, hi = normalize_to_fixed_bounds(building_objects)

    bpy.ops.object.select_all(action="DESELECT")
    for obj in building_objects:
        obj.select_set(True)
    root.select_set(True)
    glb_path = output / "adaptive_warehouse_blender_fixed.glb"
    bpy.ops.export_scene.gltf(
        filepath=str(glb_path),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
    )

    metadata = {
        "pipeline": "blender_direct_fixed_asset",
        "archetype": "adaptive_reuse_warehouse_lofts",
        "variant": "warehouse_loft_timber_brick",
        "declared_dimensions_m": [WIDTH, DEPTH, RIDGE_Z],
        "raw_authored_bounds_m": [round(v, 4) for v in raw_size],
        "measured_blender_bounds_m": [round(hi.x - lo.x, 4), round(hi.y - lo.y, 4), round(hi.z - lo.z, 4)],
        "origin_contract": "bottom-centre",
        "modular": False,
        "glb": glb_path.name,
    }
    (output / "blender_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    setup_render(output, building_objects)
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "adaptive_warehouse_blender_fixed.blend"))


if __name__ == "__main__":
    # Blender keeps its own args before `--`.
    import sys
    if "--" in sys.argv:
        sys.argv = [sys.argv[0], *sys.argv[sys.argv.index("--") + 1 :]]
    main()
