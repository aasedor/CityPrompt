"""Render locked-camera QA evidence from an exported delivery GLB.

Run inside Blender 4.2+ / 5.x::

    blender --background --factory-startup --python render_delivery_glb.py -- \
      --input path/to/family_assembled.glb --output-dir artifacts/family-review

Unlike the compiler's presentation renders, this imports the final on-disk GLB.
The evidence therefore catches export transforms, missing embedded materials,
bad pivots, and bounds that differ from the pre-export Blender scene.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--family", default=None)
    parser.add_argument("--resolution-x", type=int, default=960)
    parser.add_argument("--resolution-y", type=int, default=720)
    parser.add_argument("--samples", type=int, default=32)
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(argv)


def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for item in list(collection):
            if item.users == 0:
                collection.remove(item)


def imported_mesh_bounds() -> tuple[Vector, Vector, list[bpy.types.Object]]:
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not meshes:
        raise RuntimeError("delivery GLB imported no mesh objects")
    corners = [obj.matrix_world @ Vector(corner) for obj in meshes for corner in obj.bound_box]
    minimum = Vector(tuple(min(point[axis] for point in corners) for axis in range(3)))
    maximum = Vector(tuple(max(point[axis] for point in corners) for axis in range(3)))
    return minimum, maximum, meshes


def make_material(name: str, color: tuple[float, float, float, float], roughness: float) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = roughness
    return material


def add_review_ground(minimum: Vector, maximum: Vector) -> None:
    width = maximum.x - minimum.x
    depth = maximum.y - minimum.y
    centre_x = (minimum.x + maximum.x) / 2
    centre_y = (minimum.y + maximum.y) / 2
    size = max(width, depth, 1.0) * 4.0
    bpy.ops.mesh.primitive_plane_add(
        size=size,
        location=(centre_x, centre_y, minimum.z - 0.012),
    )
    ground = bpy.context.object
    ground.name = "QA_GroundDatum"
    ground.data.materials.append(make_material("QA_Ground", (0.19, 0.21, 0.18, 1.0), 0.96))


def look_at(camera: bpy.types.Object, target: Vector) -> None:
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()


def configure_scene(options: argparse.Namespace) -> tuple[bpy.types.Scene, bpy.types.Object, str]:
    scene = bpy.context.scene
    engine = ""
    for candidate in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "BLENDER_WORKBENCH"):
        try:
            scene.render.engine = candidate
            engine = candidate
            break
        except TypeError:
            continue
    if not engine:
        raise RuntimeError("no supported Blender render engine is available")

    scene.render.resolution_x = options.resolution_x
    scene.render.resolution_y = options.resolution_y
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.use_file_extension = True
    if hasattr(scene, "eevee") and hasattr(scene.eevee, "taa_render_samples"):
        scene.eevee.taa_render_samples = options.samples
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.5

    world = scene.world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.055, 0.075, 0.11, 1.0)
    background.inputs["Strength"].default_value = 0.45

    bpy.ops.object.light_add(
        type="SUN",
        rotation=(math.radians(28), math.radians(-22), math.radians(-32)),
    )
    sun = bpy.context.object
    sun.name = "QA_Sun"
    sun.data.energy = 2.6
    sun.data.angle = math.radians(8)

    bpy.ops.object.light_add(type="AREA", location=(-18, -22, 28))
    key = bpy.context.object
    key.name = "QA_Key"
    key.data.energy = 1200
    key.data.shape = "DISK"
    key.data.size = 16

    bpy.ops.object.light_add(type="AREA", location=(18, 12, 16))
    fill = bpy.context.object
    fill.name = "QA_Fill"
    fill.data.energy = 600
    fill.data.size = 12

    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.name = "QA_Camera"
    camera.data.lens = 52
    camera.data.clip_start = 0.05
    camera.data.clip_end = 5000
    scene.camera = camera
    return scene, camera, engine


def render_views(
    scene: bpy.types.Scene,
    camera: bpy.types.Object,
    output_dir: Path,
    minimum: Vector,
    maximum: Vector,
) -> list[dict[str, object]]:
    centre = (minimum + maximum) / 2
    width = max(maximum.x - minimum.x, 1.0)
    depth = max(maximum.y - minimum.y, 1.0)
    height = max(maximum.z - minimum.z, 1.0)
    radius = max(width, depth, height)
    target = Vector((centre.x, centre.y, minimum.z + height * 0.46))
    views = (
        ("front", Vector((centre.x, minimum.y - radius * 1.85, minimum.z + height * 0.55)), 58),
        ("front_corner", Vector((maximum.x + radius * 1.05, minimum.y - radius * 1.35, minimum.z + height * 0.72)), 52),
        ("rear_corner", Vector((minimum.x - radius * 1.0, maximum.y + radius * 1.30, minimum.z + height * 0.78)), 52),
        ("aerial", Vector((maximum.x + radius * 0.80, minimum.y - radius * 1.05, maximum.z + radius * 1.45)), 55),
    )
    evidence: list[dict[str, object]] = []
    for role, location, lens in views:
        camera.location = location
        camera.data.lens = lens
        look_at(camera, target)
        path = output_dir / f"delivery-{role}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        evidence.append(
            {
                "role": role,
                "path": path.name,
                "camera_location": [round(value, 6) for value in location],
                "target": [round(value, 6) for value in target],
                "lens_mm": lens,
            }
        )
        print(f"[delivery-review] wrote {path}", flush=True)
    return evidence


def main() -> int:
    options = parse_args()
    source = options.input.resolve()
    output_dir = options.output_dir.resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if source.stat().st_size < 200:
        raise RuntimeError(f"{source} is a Git LFS pointer, not a hydrated GLB")
    output_dir.mkdir(parents=True, exist_ok=True)

    reset_scene()
    bpy.ops.import_scene.gltf(filepath=str(source))
    minimum, maximum, meshes = imported_mesh_bounds()
    add_review_ground(minimum, maximum)
    scene, camera, engine = configure_scene(options)
    views = render_views(scene, camera, output_dir, minimum, maximum)

    dimensions = maximum - minimum
    report = {
        "schema": "cityprompt-delivery-glb-review@1",
        "family": options.family or source.stem,
        "source": str(source),
        "blender_version": bpy.app.version_string,
        "render_engine": engine,
        "mesh_objects": len(meshes),
        "bounds": {
            "minimum": [round(value, 6) for value in minimum],
            "maximum": [round(value, 6) for value in maximum],
            "dimensions": [round(value, 6) for value in dimensions],
        },
        "ground_delta_m": round(minimum.z, 6),
        "views": views,
    }
    report_path = output_dir / "delivery-review.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"[delivery-review] wrote {report_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
