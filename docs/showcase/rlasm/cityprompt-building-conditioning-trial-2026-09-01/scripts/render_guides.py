"""Render the three deterministic conditioning guides for the CityPrompt trial.

Run this script from Blender with the approved Calgary bungalow v020 .blend
already loaded.  The only variable is ``--mode``: polygon, clay, or full.
All three lanes use the exact same camera, lighting, resolution, and site.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import bpy


CAMERA_NAME = "camera_front_corner_60"
CONTEXT_OBJECTS = {"source_site_lawn", "public_sidewalk"}
LANDSCAPE_PREFIXES = ("hydrangea", "shrub")


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=("polygon", "clay", "full"))
    parser.add_argument("--output", required=True)
    return parser.parse_args(argv)


def principled_material(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float,
    metallic: float = 0.0,
) -> bpy.types.Material:
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    material.node_tree.links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    return material


def assign_material(obj: bpy.types.Object, material: bpy.types.Material) -> None:
    obj.data.materials.clear()
    obj.data.materials.append(material)


def configure_common(output: Path) -> None:
    scene = bpy.context.scene
    camera = bpy.data.objects.get(CAMERA_NAME)
    if camera is None:
        raise RuntimeError(f"Missing locked camera: {CAMERA_NAME}")

    scene.camera = camera
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.film_transparent = False
    scene.render.filepath = str(output.resolve())
    output.parent.mkdir(parents=True, exist_ok=True)


def make_clay() -> None:
    clay = principled_material(
        "TRIAL_ARCHITECTURAL_CLAY",
        (0.73, 0.66, 0.54, 1.0),
        roughness=0.78,
    )

    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        if obj.name in CONTEXT_OBJECTS:
            continue
        if obj.name.startswith(LANDSCAPE_PREFIXES) or obj.name == "front_walk":
            obj.hide_render = True
            continue
        assign_material(obj, clay)


def add_edge_box(
    a: tuple[float, float],
    b: tuple[float, float],
    material: bpy.types.Material,
) -> None:
    ax, ay = a
    bx, by = b
    dx = bx - ax
    dy = by - ay
    length = math.hypot(dx, dy)
    bpy.ops.mesh.primitive_cube_add(
        location=((ax + bx) * 0.5, (ay + by) * 0.5, 0.095),
        scale=(length * 0.5, 0.075, 0.055),
    )
    edge = bpy.context.object
    edge.name = "trial_polygon_boundary"
    edge.rotation_euler[2] = math.atan2(dy, dx)
    assign_material(edge, material)


def make_polygon() -> None:
    for obj in bpy.data.objects:
        if obj.type == "MESH" and obj.name not in CONTEXT_OBJECTS:
            obj.hide_render = True

    # The polygon follows the approved measured footprint: 11.8 x 13.6 m main
    # body plus the clipped-gable projection and deep right-hand porch.  Steps
    # are excluded, matching CityPrompt's building-zone convention.
    points_2d = [
        (-5.90, -6.80),
        (-2.20, -6.80),
        (-2.20, -8.20),
        (0.75, -8.20),
        (0.75, -9.10),
        (6.35, -9.10),
        (6.35, -6.80),
        (5.90, -6.80),
        (5.90, 6.80),
        (-5.90, 6.80),
    ]
    vertices = [(x, y, 0.045) for x, y in points_2d]
    mesh = bpy.data.meshes.new("trial_colored_polygon_mesh")
    mesh.from_pydata(vertices, [], [list(range(len(vertices)))])
    mesh.update()
    polygon = bpy.data.objects.new("trial_colored_polygon", mesh)
    bpy.context.collection.objects.link(polygon)

    fill = principled_material(
        "TRIAL_CITYPROMPT_BUILDING_RED",
        (0.745, 0.045, 0.030, 1.0),
        roughness=0.66,
    )
    boundary = principled_material(
        "TRIAL_CITYPROMPT_BOUNDARY",
        (1.0, 0.78, 0.18, 1.0),
        roughness=0.54,
    )
    assign_material(polygon, fill)

    for index, start in enumerate(points_2d):
        add_edge_box(start, points_2d[(index + 1) % len(points_2d)], boundary)


def main() -> None:
    args = parse_args()
    output = Path(args.output)
    configure_common(output)

    if args.mode == "clay":
        make_clay()
    elif args.mode == "polygon":
        make_polygon()

    bpy.ops.render.render(write_still=True)
    print(
        "TRIAL_RENDER",
        {
            "mode": args.mode,
            "camera": CAMERA_NAME,
            "resolution": [1280, 960],
            "output": str(output.resolve()),
        },
    )


if __name__ == "__main__":
    main()
