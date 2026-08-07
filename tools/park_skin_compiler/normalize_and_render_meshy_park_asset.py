"""Normalize one Meshy park prop to City Prompt metric/ground-contact rules.

Run with Blender in background mode::

    blender --background --factory-startup --python normalize_and_render_meshy_park_asset.py -- \
      --input raw.glb --output cleaned.glb --preview-dir previews \
      --asset-id nature-play-climbing-log-v1 --length 4.2 --diameter 0.9
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def args_after_double_dash() -> list[str]:
    return sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--preview-dir", required=True)
    parser.add_argument("--asset-id", required=True)
    parser.add_argument("--length", type=float, default=4.2)
    parser.add_argument("--diameter", type=float, default=0.9)
    parser.add_argument("--target-faces", type=int, default=18_000)
    parser.add_argument("--texture-max", type=int, default=1_024)
    return parser.parse_args(args_after_double_dash())


def world_bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    corners = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    return (
        Vector((min(c.x for c in corners), min(c.y for c in corners), min(c.z for c in corners))),
        Vector((max(c.x for c in corners), max(c.y for c in corners), max(c.z for c in corners))),
    )


def select_only(objects: list[bpy.types.Object]) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.hide_set(False)
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]


def resize_images(max_dimension: int) -> list[dict[str, object]]:
    resized: list[dict[str, object]] = []
    for image in bpy.data.images:
        if image.source != "FILE" or image.size[0] <= 0 or image.size[1] <= 0:
            continue
        before = [int(image.size[0]), int(image.size[1])]
        scale = min(1.0, max_dimension / max(before))
        if scale < 1.0:
            image.scale(max(1, round(before[0] * scale)), max(1, round(before[1] * scale)))
        image.pack()
        resized.append({"name": image.name, "before": before, "after": list(image.size)})
    return resized


def normalize_mesh(args: argparse.Namespace) -> tuple[bpy.types.Object, dict[str, object]]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(Path(args.input).resolve()))
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not meshes:
        raise RuntimeError("Imported GLB has no mesh objects")

    original_min, original_max = world_bounds(meshes)
    original_dimensions = original_max - original_min

    select_only(meshes)
    bpy.ops.object.convert(target="MESH")
    if len(meshes) > 1:
        bpy.ops.object.join()
    asset = bpy.context.object
    asset.name = f"PARK_{args.asset_id}"
    asset.data.name = f"PARK_{args.asset_id}_Mesh"

    # Meshy outputs are usually axis-aligned, but the longitudinal axis is not
    # guaranteed.  Move the longest bounding-box axis onto City Prompt +X.
    dimensions = list(asset.dimensions)
    longest_axis = dimensions.index(max(dimensions))
    if longest_axis == 1:
        asset.rotation_euler.z = -math.pi / 2
    elif longest_axis == 2:
        asset.rotation_euler.y = math.pi / 2
    bpy.context.view_layer.objects.active = asset
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

    dimensions = asset.dimensions
    asset.scale = (
        args.length / max(dimensions.x, 1e-6),
        args.diameter / max(dimensions.y, 1e-6),
        args.diameter / max(dimensions.z, 1e-6),
    )
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    normalized_min, normalized_max = world_bounds([asset])
    center = (normalized_min + normalized_max) / 2
    asset.location += Vector((-center.x, -center.y, -normalized_min.z))
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    bpy.context.scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR", center="MEDIAN")

    faces_before = len(asset.data.polygons)
    if args.target_faces > 0 and faces_before > args.target_faces:
        modifier = asset.modifiers.new("CityPrompt bounded topology", "DECIMATE")
        modifier.ratio = args.target_faces / faces_before
        modifier.use_collapse_triangulate = True
        bpy.context.view_layer.objects.active = asset
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    faces_after = len(asset.data.polygons)

    for material in asset.data.materials:
        material.name = f"meshy_archetype_bark_{material.name[:36]}"
        material.diffuse_color = (1, 1, 1, 1)

    asset["asset_id"] = args.asset_id
    asset["source_kind"] = "meshy_multiview_archetype_reference"
    asset["metric_length_m"] = args.length
    asset["metric_diameter_m"] = args.diameter
    asset["ground_contact_origin_z_m"] = 0.0
    asset["people"] = False
    asset["large_building"] = False
    asset["placement_role"] = "nature_play_climbing_log"
    asset["collision_proxy_m"] = json.dumps([args.length, args.diameter, args.diameter])

    textures = resize_images(args.texture_max)
    final_min, final_max = world_bounds([asset])
    report = {
        "assetId": args.asset_id,
        "sourceKind": "meshy_multiview_archetype_reference",
        "originalBounds": {"min": list(original_min), "max": list(original_max)},
        "originalDimensions": list(original_dimensions),
        "longestAxisIndex": longest_axis,
        "finalBounds": {"min": list(final_min), "max": list(final_max)},
        "finalDimensionsM": list(final_max - final_min),
        "facesBefore": faces_before,
        "facesAfter": faces_after,
        "materials": [material.name for material in asset.data.materials],
        "textures": textures,
        "people": False,
        "largeBuildings": False,
    }
    return asset, report


def add_area_light(name: str, location: tuple[float, float, float], energy: float, size: float) -> None:
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    direction = Vector((0, 0, 0.35)) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def render_previews(asset: bpy.types.Object, preview_dir: Path) -> None:
    preview_dir.mkdir(parents=True, exist_ok=True)
    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.color = (0.035, 0.045, 0.04)

    floor_mat = bpy.data.materials.new("Neutral park floor")
    floor_mat.diffuse_color = (0.16, 0.18, 0.16, 1)
    floor_mat.roughness = 0.96
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, -0.012))
    floor = bpy.context.object
    floor.name = "QA_Floor"
    floor.data.materials.append(floor_mat)

    add_area_light("Key", (5.5, -6.5, 7.5), 1200, 5.0)
    add_area_light("Fill", (-4.5, -2.0, 4.0), 650, 4.0)
    add_area_light("Rim", (1.0, 6.0, 5.0), 900, 3.0)

    camera_data = bpy.data.cameras.new("QA_Camera")
    camera = bpy.data.objects.new("QA_Camera", camera_data)
    bpy.context.collection.objects.link(camera)
    bpy.context.scene.camera = camera
    camera_data.lens = 58

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 900
    scene.render.resolution_y = 600
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"

    views = {
        "front-three-quarter": (6.8, -6.5, 4.2),
        "rear-three-quarter": (-6.8, 6.5, 4.2),
        "side-human-scale": (0.0, -7.6, 2.0),
        "park-oblique": (7.5, -8.5, 7.5),
    }
    target = Vector((0, 0, 0.45))
    for name, position in views.items():
        camera.location = position
        camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str(preview_dir / f"{name}.png")
        bpy.ops.render.render(write_still=True)

    # Do not let the temporary QA scene leak into the runtime GLB.
    for obj in [floor, camera, *[obj for obj in bpy.context.scene.objects if obj.type == "LIGHT"]]:
        bpy.data.objects.remove(obj, do_unlink=True)
    asset.hide_render = False


def main() -> None:
    args = parse_args()
    output = Path(args.output).resolve()
    preview_dir = Path(args.preview_dir).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    asset, report = normalize_mesh(args)
    render_previews(asset, preview_dir)

    select_only([asset])
    bpy.ops.export_scene.gltf(
        filepath=str(output),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
        export_extras=True,
        export_materials="EXPORT",
        export_image_format="AUTO",
    )
    report["output"] = str(output)
    report["outputBytes"] = output.stat().st_size
    (preview_dir / "normalization-report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
