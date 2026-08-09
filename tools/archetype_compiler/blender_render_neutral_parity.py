"""Render a deterministic neutral view from either a source blend or exported GLB.

Run under Blender.  The deliberately plain studio setup makes modelling and
material/export errors visible without atmospheric lighting or colour grade.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def parse_args() -> argparse.Namespace:
    values = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--kind", choices=("blend", "glb"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(values)


def reset_and_load(path: Path, kind: str) -> None:
    if kind == "blend":
        bpy.ops.wm.open_mainfile(filepath=str(path.resolve()))
    else:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(path.resolve()))
    for obj in list(bpy.data.objects):
        if obj.type in {"CAMERA", "LIGHT"}:
            bpy.data.objects.remove(obj, do_unlink=True)


def model_bounds() -> tuple[Vector, Vector]:
    points: list[Vector] = []
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH" or obj.hide_render:
            continue
        points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    if not points:
        raise RuntimeError("neutral renderer found no visible mesh geometry")
    minimum = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    maximum = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return minimum, maximum


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def add_ground(minimum: Vector, maximum: Vector) -> None:
    span = max(maximum.x - minimum.x, maximum.y - minimum.y) * 2.4
    bpy.ops.mesh.primitive_plane_add(
        size=span,
        location=((minimum.x + maximum.x) / 2, (minimum.y + maximum.y) / 2, minimum.z - 0.03),
    )
    ground = bpy.context.object
    ground.name = "QA_NeutralGround"
    material = bpy.data.materials.new("QA_NeutralGround")
    material.diffuse_color = (0.19, 0.20, 0.21, 1.0)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.19, 0.20, 0.21, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.92
    ground.data.materials.append(material)


def add_area(name: str, location: Vector, energy: float, size: float, target: Vector) -> None:
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    look_at(obj, target)


def configure_scene(minimum: Vector, maximum: Vector, output: Path) -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.filepath = str(output.resolve())
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.render.image_settings.color_depth = "8"
    if scene.world is None:
        scene.world = bpy.data.worlds.new("QA_NeutralWorld")
    scene.world.color = (0.055, 0.060, 0.068)
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.055, 0.060, 0.068, 1.0)
    background.inputs["Strength"].default_value = 0.44

    centre = (minimum + maximum) * 0.5
    dimensions = maximum - minimum
    scale = max(dimensions.x, dimensions.y, dimensions.z * 1.75)
    add_ground(minimum, maximum)
    add_area(
        "QA_Key",
        centre + Vector((-0.75, -1.10, 1.65)) * scale,
        1500.0,
        scale * 0.75,
        centre,
    )
    add_area(
        "QA_Fill",
        centre + Vector((1.20, 0.30, 0.75)) * scale,
        650.0,
        scale * 0.90,
        centre,
    )
    sun_data = bpy.data.lights.new("QA_Sun", "SUN")
    sun_data.energy = 1.4
    sun_data.angle = math.radians(18)
    sun = bpy.data.objects.new("QA_Sun", sun_data)
    bpy.context.scene.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(34), math.radians(-18), math.radians(-142))

    camera_data = bpy.data.cameras.new("QA_NeutralCamera")
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = scale * 1.30
    camera = bpy.data.objects.new("QA_NeutralCamera", camera_data)
    bpy.context.scene.collection.objects.link(camera)
    camera.location = centre + Vector((1.28, -1.55, 0.92)) * scale
    look_at(camera, centre + Vector((0.0, 0.0, dimensions.z * 0.04)))
    scene.camera = camera


def main() -> None:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    reset_and_load(args.input, args.kind)
    minimum, maximum = model_bounds()
    configure_scene(minimum, maximum, args.output)
    bpy.ops.render.render(write_still=True)
    print(f"[neutral-parity] wrote {args.output}")


if __name__ == "__main__":
    main()
