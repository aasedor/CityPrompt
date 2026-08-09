"""Normalize a Meshy GLB to the pilot's fixed dimensions and render QA views."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


TARGET = Vector((40.0, 20.0, 12.5))


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def bounds(meshes):
    pts = [obj.matrix_world @ Vector(corner) for obj in meshes for corner in obj.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def box(name, dims, loc, color):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mat = bpy.data.materials.new(name + " material")
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = 0.95
    obj.data.materials.append(mat)
    return obj


def normalize(imported, meshes):
    roots = [obj for obj in imported if obj.parent is None]
    root = bpy.data.objects.new("Fixed_40x20m_bottom_centre", None)
    bpy.context.collection.objects.link(root)
    for obj in roots:
        world = obj.matrix_world.copy()
        obj.parent = root
        obj.matrix_world = world

    lo, hi = bounds(meshes)
    native = hi - lo
    rotated = False
    if native.y > native.x:
        root.rotation_euler.z = math.radians(90)
        bpy.context.view_layer.update()
        lo, hi = bounds(meshes)
        native = hi - lo
        rotated = True

    scale = Vector((TARGET.x / native.x, TARGET.y / native.y, TARGET.z / native.z))
    root.scale = scale
    bpy.context.view_layer.update()
    lo, hi = bounds(meshes)
    root.location -= Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    bpy.context.view_layer.update()
    final_lo, final_hi = bounds(meshes)
    return root, native, scale, rotated, final_lo, final_hi


def render_views(output: Path, meshes):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.world.color = (0.025, 0.035, 0.055)
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.11, 0.14, 0.18, 1)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.55
    ground = box("review_ground", (90, 75, 0.22), (0, 0, -0.14), (0.095, 0.105, 0.115, 1))

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
    scene.camera = camera

    def point(location, target):
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
        point(location, target)
        scene.render.filepath = str(output / f"meshy_{name}.png")
        bpy.ops.render.render(write_still=True)

    bpy.data.objects.remove(ground, do_unlink=True)
    bpy.data.objects.remove(camera, do_unlink=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    clear_scene()
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(args.input.resolve()), import_pack_images=True)
    imported = [obj for obj in bpy.context.scene.objects if obj not in before]
    meshes = [obj for obj in imported if obj.type == "MESH"]
    if not meshes:
        raise RuntimeError("Imported Meshy GLB contains no mesh objects")
    root, native, scale, rotated, final_lo, final_hi = normalize(imported, meshes)

    bpy.ops.object.select_all(action="DESELECT")
    for obj in [root, *imported]:
        obj.select_set(True)
    normalized = args.output / "adaptive_warehouse_meshy_fixed.glb"
    bpy.ops.export_scene.gltf(
        filepath=str(normalized),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
    )

    triangles = sum(len(obj.data.loop_triangles) for obj in meshes)
    metadata = {
        "pipeline": "meshy_fixed_asset_normalized_in_blender",
        "source_glb": args.input.name,
        "glb": normalized.name,
        "native_bounds_before_normalization": [round(v, 5) for v in native],
        "authoring_scale": [round(v, 6) for v in scale],
        "rotated_long_axis_to_x": rotated,
        "final_bounds_m": [round(v, 4) for v in (final_hi - final_lo)],
        "origin_min_z": round(final_lo.z, 6),
        "triangle_count": triangles,
        "modular": False,
    }
    (args.output / "meshy_fixed_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    render_views(args.output, meshes)
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output / "adaptive_warehouse_meshy_fixed.blend"))


if __name__ == "__main__":
    if "--" in sys.argv:
        sys.argv = [sys.argv[0], *sys.argv[sys.argv.index("--") + 1 :]]
    main()
