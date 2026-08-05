"""Blender QA render for the fixed neighborhood-park LEGO geometry.

Run with Blender, after compile_neighborhood_park_skins.py:
  blender --background --python render_neighborhood_park_skins.py -- --repo-root <path>
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

SITE_WIDTH = 25.0
SITE_HEIGHT = 18.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])


def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.materials, bpy.data.images, bpy.data.curves, bpy.data.meshes, bpy.data.cameras, bpy.data.lights):
        for block in list(datablocks):
            datablocks.remove(block)


def image(path: Path, non_color: bool = False):
    loaded = bpy.data.images.load(str(path), check_existing=True)
    loaded.colorspace_settings.name = "Non-Color" if non_color else "sRGB"
    return loaded


def projected_atlas_material(name: str, texture_dir: Path):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Metallic"].default_value = 0.0
    shader.inputs["Specular IOR Level"].default_value = 0.28
    links.new(shader.outputs["BSDF"], output.inputs["Surface"])

    texcoord = nodes.new("ShaderNodeTexCoord")
    multiply = nodes.new("ShaderNodeVectorMath")
    multiply.operation = "MULTIPLY"
    multiply.inputs[1].default_value = (1.0 / SITE_WIDTH, -1.0 / SITE_HEIGHT, 0.0)
    add = nodes.new("ShaderNodeVectorMath")
    add.operation = "ADD"
    add.inputs[1].default_value = (0.5, 0.5, 0.0)
    links.new(texcoord.outputs["Object"], multiply.inputs[0])
    links.new(multiply.outputs["Vector"], add.inputs[0])

    albedo = nodes.new("ShaderNodeTexImage")
    albedo.image = image(texture_dir / "albedo.jpg")
    albedo.extension = "CLIP"
    ao = nodes.new("ShaderNodeTexImage")
    ao.image = image(texture_dir / "ao.jpg", non_color=True)
    ao.extension = "CLIP"
    mix = nodes.new("ShaderNodeMixRGB")
    mix.blend_type = "MULTIPLY"
    mix.inputs[0].default_value = 0.58
    links.new(add.outputs["Vector"], albedo.inputs["Vector"])
    links.new(add.outputs["Vector"], ao.inputs["Vector"])
    links.new(albedo.outputs["Color"], mix.inputs[1])
    links.new(ao.outputs["Color"], mix.inputs[2])
    links.new(mix.outputs["Color"], shader.inputs["Base Color"])

    roughness = nodes.new("ShaderNodeTexImage")
    roughness.image = image(texture_dir / "roughness.jpg", non_color=True)
    roughness.extension = "CLIP"
    links.new(add.outputs["Vector"], roughness.inputs["Vector"])
    links.new(roughness.outputs["Color"], shader.inputs["Roughness"])

    normal_tex = nodes.new("ShaderNodeTexImage")
    normal_tex.image = image(texture_dir / "normal.png", non_color=True)
    normal_tex.extension = "CLIP"
    normal = nodes.new("ShaderNodeNormalMap")
    normal.inputs["Strength"].default_value = 0.34
    links.new(add.outputs["Vector"], normal_tex.inputs["Vector"])
    links.new(normal_tex.outputs["Color"], normal.inputs["Color"])
    links.new(normal.outputs["Normal"], shader.inputs["Normal"])
    return material


def solid_material(name: str, color: tuple[float, float, float, float], roughness: float = 0.8):
    material = bpy.data.materials.new(name)
    material.diffuse_color = color
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = roughness
    return material


def bevel(object_, amount: float = 0.22, segments: int = 3) -> None:
    modifier = object_.modifiers.new("Soft LEGO edge", "BEVEL")
    modifier.width = amount
    modifier.segments = segments


def cube(name: str, location, dimensions, material, bevel_width: float = 0.18):
    bpy.ops.mesh.primitive_cube_add(location=location)
    object_ = bpy.context.object
    object_.name = name
    object_.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bevel(object_, bevel_width)
    object_.data.materials.append(material)
    return object_


def ellipse(name: str, location, dimensions, depth: float, material):
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.5, depth=depth, location=location)
    object_ = bpy.context.object
    object_.name = name
    object_.scale = (dimensions[0], dimensions[1], 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bevel(object_, 0.14)
    object_.data.materials.append(material)
    return object_


def path_segment(name: str, start: tuple[float, float], end: tuple[float, float], width: float, material):
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = math.hypot(dx, dy)
    object_ = cube(name, ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2, 0.52), (length + width * 0.5, width, 0.22), material, 0.28)
    object_.rotation_euler[2] = math.atan2(dy, dx)
    return object_


def build_fixed_park(atlas, edge, trunk, foliage) -> None:
    cube("Park base", (0, 0, 0.18), (SITE_WIDTH, SITE_HEIGHT, 0.55), edge, 0.42)
    cube("Atlas surface", (0, 0, 0.49), (SITE_WIDTH - 0.35, SITE_HEIGHT - 0.35, 0.16), atlas, 0.34)

    ellipse("Central lawn plate", (0.0, 0.2, 0.70), (10.8, 7.8), 0.28, atlas)
    ellipse("Meadow plate", (-7.2, 4.5, 0.72), (4.4, 3.0), 0.32, atlas)
    ellipse("Rain garden plate", (7.4, -4.1, 0.72), (4.5, 3.2), 0.32, atlas)
    ellipse("Play plate", (7.5, 4.6, 0.75), (4.2, 3.0), 0.38, atlas)
    cube("Pavilion plate", (6.0, -2.0, 0.75), (3.0, 2.2, 0.38), atlas, 0.32)

    path_points = [(-12.0, 0.0), (-6.0, -0.6), (0.0, 0.2), (6.0, 1.3), (12.0, 1.0)]
    for index, (start, end) in enumerate(zip(path_points, path_points[1:])):
        path_segment(f"Main path {index}", start, end, 1.35, atlas)
    for index, (start, end) in enumerate((((0, 8.4), (-0.4, 4.0)), ((0, -8.4), (0.0, -4.0)), ((6.0, 1.3), (7.5, 4.6)))):
        path_segment(f"Branch path {index}", start, end, 1.15, atlas)

    tree_positions = [(-10.6, 6.7), (-7.6, 7.4), (-3.8, 7.3), (3.6, 7.5), (8.0, 7.0), (10.8, 5.8),
                      (-10.8, -6.2), (-7.8, -7.3), (-3.6, -7.4), (3.7, -7.5), (8.0, -7.1), (10.8, -5.7)]
    for index, (x, y) in enumerate(tree_positions):
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.18, depth=1.65, location=(x, y, 1.45))
        tree_trunk = bpy.context.object
        tree_trunk.name = f"Tree trunk {index}"
        tree_trunk.data.materials.append(trunk)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.95, location=(x, y, 2.55))
        crown = bpy.context.object
        crown.name = f"Tree crown {index}"
        crown.scale = (1.0, 1.0, 0.82)
        crown.data.materials.append(foliage)


def aim(object_, target=(0, 0, 0)) -> None:
    object_.rotation_euler = (Vector(target) - object_.location).to_track_quat("-Z", "Y").to_euler()


def setup_scene() -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 760
    scene.render.resolution_y = 560
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.render.resolution_percentage = 100
    scene.world.color = (0.035, 0.045, 0.042)

    ground = solid_material("Ground", (0.055, 0.07, 0.065, 1.0), 0.92)
    cube("Presentation ground", (0, 0, -0.26), (36, 30, 0.3), ground, 0.4)

    bpy.ops.object.light_add(type="AREA", location=(-8, -10, 18))
    key = bpy.context.object
    key.data.energy = 1500
    key.data.shape = "DISK"
    key.data.size = 10
    aim(key)
    bpy.ops.object.light_add(type="AREA", location=(12, 4, 10))
    fill = bpy.context.object
    fill.data.energy = 900
    fill.data.size = 8
    aim(fill)
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 12))
    sun = bpy.context.object
    sun.rotation_euler = (math.radians(24), math.radians(-18), math.radians(28))
    sun.data.energy = 1.25
    sun.data.angle = math.radians(18)

    bpy.ops.object.camera_add(location=(21, -24, 23))
    camera = bpy.context.object
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 31.5
    aim(camera, (0, 0, 0.4))
    scene.camera = camera


def render_variant(repo_root: Path, output: Path, variant_id: str) -> None:
    reset_scene()
    texture_dir = repo_root / "frontend/public/park-skins/neighborhood-park" / variant_id
    atlas = projected_atlas_material(f"{variant_id} projected atlas", texture_dir)
    edge = solid_material("Charcoal plate edge", (0.055, 0.075, 0.068, 1.0), 0.84)
    trunk = solid_material("Timber trunks", (0.21, 0.12, 0.065, 1.0), 0.9)
    foliage_colors = {
        "variant_0": (0.17, 0.31, 0.13, 1.0),
        "variant_1": (0.22, 0.39, 0.18, 1.0),
        "variant_2": (0.31, 0.42, 0.12, 1.0),
        "variant_3": (0.20, 0.36, 0.16, 1.0),
    }
    foliage = solid_material("Tree crowns", foliage_colors[variant_id], 0.96)
    build_fixed_park(atlas, edge, trunk, foliage)
    setup_scene()
    bpy.context.scene.render.filepath = str(output / f"{variant_id}.png")
    bpy.ops.render.render(write_still=True)


def main() -> None:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    output = (args.output or repo_root / "artifacts/neighborhood-park-reference-skins-v2/renders").resolve()
    output.mkdir(parents=True, exist_ok=True)
    for variant_id in ("variant_0", "variant_1", "variant_2", "variant_3"):
        render_variant(repo_root, output, variant_id)
        print(f"rendered {output / (variant_id + '.png')}")


if __name__ == "__main__":
    main()
