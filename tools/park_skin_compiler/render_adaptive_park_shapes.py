"""Render the same procedural park kit on three generated parcel shapes."""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    return parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])


def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for blocks in (bpy.data.materials, bpy.data.images, bpy.data.meshes, bpy.data.cameras, bpy.data.lights):
        for block in list(blocks):
            blocks.remove(block)


def load_image(path: Path, non_color: bool = False):
    loaded = bpy.data.images.load(str(path), check_existing=True)
    loaded.colorspace_settings.name = "Non-Color" if non_color else "sRGB"
    return loaded


def pbr_material(name: str, directory: Path, metres_per_tile: float):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes, links = material.node_tree.nodes, material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Metallic"].default_value = 0.0
    shader.inputs["Specular IOR Level"].default_value = 0.26
    links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    coords = nodes.new("ShaderNodeTexCoord")
    scale = nodes.new("ShaderNodeVectorMath")
    scale.operation = "MULTIPLY"
    scale.inputs[1].default_value = (1 / metres_per_tile, 1 / metres_per_tile, 1.0)
    links.new(coords.outputs["Object"], scale.inputs[0])

    albedo = nodes.new("ShaderNodeTexImage")
    albedo.image = load_image(directory / "albedo.jpg")
    albedo.extension = "REPEAT"
    links.new(scale.outputs["Vector"], albedo.inputs["Vector"])
    ao = nodes.new("ShaderNodeTexImage")
    ao.image = load_image(directory / "ao.jpg", True)
    ao.extension = "REPEAT"
    links.new(scale.outputs["Vector"], ao.inputs["Vector"])
    multiply = nodes.new("ShaderNodeMixRGB")
    multiply.blend_type = "MULTIPLY"
    multiply.inputs[0].default_value = 0.42
    links.new(albedo.outputs["Color"], multiply.inputs[1])
    links.new(ao.outputs["Color"], multiply.inputs[2])
    links.new(multiply.outputs["Color"], shader.inputs["Base Color"])

    roughness = nodes.new("ShaderNodeTexImage")
    roughness.image = load_image(directory / "roughness.jpg", True)
    roughness.extension = "REPEAT"
    links.new(scale.outputs["Vector"], roughness.inputs["Vector"])
    links.new(roughness.outputs["Color"], shader.inputs["Roughness"])
    normal_tex = nodes.new("ShaderNodeTexImage")
    normal_tex.image = load_image(directory / "normal.png", True)
    normal_tex.extension = "REPEAT"
    links.new(scale.outputs["Vector"], normal_tex.inputs["Vector"])
    normal = nodes.new("ShaderNodeNormalMap")
    normal.inputs["Strength"].default_value = 0.32
    links.new(normal_tex.outputs["Color"], normal.inputs["Color"])
    links.new(normal.outputs["Normal"], shader.inputs["Normal"])
    return material


def solid_material(name: str, colour, roughness: float = 0.85, metallic: float = 0.0):
    material = bpy.data.materials.new(name)
    material.diffuse_color = colour
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = colour
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    return material


def triangle_mesh(name: str, triangles, z: float, material, thickness: float = 0.16):
    vertex_index: dict[tuple[float, float], int] = {}
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int]] = []
    for triangle in triangles:
        face = []
        for x, y in triangle:
            key = (round(x, 4), round(y, 4))
            if key not in vertex_index:
                vertex_index[key] = len(vertices)
                vertices.append((x, y, z))
            face.append(vertex_index[key])
        faces.append(tuple(face))
    mesh = bpy.data.meshes.new(f"{name} mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    object_ = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(object_)
    object_.data.materials.append(material)
    solidify = object_.modifiers.new("Plate thickness", "SOLIDIFY")
    solidify.thickness = thickness
    solidify.offset = -1.0
    bevel = object_.modifiers.new("Soft plate edge", "BEVEL")
    bevel.limit_method = "ANGLE"
    bevel.angle_limit = math.radians(20)
    bevel.width = min(0.11, thickness * 0.45)
    bevel.segments = 3
    return object_


def cube(name: str, location, dimensions, material, bevel_width: float = 0.1):
    bpy.ops.mesh.primitive_cube_add(location=location)
    object_ = bpy.context.object
    object_.name = name
    object_.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bevel = object_.modifiers.new("Soft edge", "BEVEL")
    bevel.width = bevel_width
    bevel.segments = 3
    object_.data.materials.append(material)
    return object_


def add_tree(index: int, point, trunk, foliage) -> None:
    x, y = point
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.16, depth=1.45, location=(x, y, 1.25))
    bpy.context.object.name = f"Tree trunk {index}"
    bpy.context.object.data.materials.append(trunk)
    for offset, radius in (((0, 0, 2.25), 0.83), ((0.35, 0.1, 2.25), 0.62), ((-0.3, -0.08, 2.18), 0.6)):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=radius, location=(x + offset[0], y + offset[1], offset[2]))
        bpy.context.object.data.materials.append(foliage)


def add_play_equipment(center, metal, accent) -> None:
    x, y = center
    cube("Play deck", (x, y, 1.0), (2.1, 1.1, 0.18), accent, 0.08)
    for dx in (-0.82, 0.82):
        for dy in (-0.38, 0.38):
            cube("Play post", (x + dx, y + dy, 1.65), (0.11, 0.11, 1.45), metal, 0.025)
    cube("Play canopy", (x, y, 2.35), (2.4, 1.35, 0.12), accent, 0.09)
    slide = cube("Slide", (x + 1.55, y, 0.78), (1.5, 0.65, 0.12), metal, 0.06)
    slide.rotation_euler[1] = math.radians(-24)


def add_pavilion(center, metal, timber) -> None:
    x, y = center
    for dx in (-1.65, 1.65):
        for dy in (-1.05, 1.05):
            cube("Pavilion column", (x + dx, y + dy, 1.55), (0.14, 0.14, 2.2), metal, 0.025)
    roof = cube("Pavilion roof", (x, y, 2.7), (4.2, 3.0, 0.18), timber, 0.13)
    roof.rotation_euler[2] = math.radians(2)


def aim(object_, target=(0, 0, 0)) -> None:
    object_.rotation_euler = (Vector(target) - object_.location).to_track_quat("-Z", "Y").to_euler()


def setup_scene(layout, dark_ground) -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 840
    scene.render.resolution_y = 600
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.world.color = (0.035, 0.045, 0.042)
    cube("Presentation ground", (0, 0, -0.42), (70, 52, 0.4), dark_ground, 0.5)

    bpy.ops.object.light_add(type="AREA", location=(-12, -14, 24))
    key = bpy.context.object
    key.data.energy = 1650
    key.data.size = 12
    aim(key)
    bpy.ops.object.light_add(type="AREA", location=(15, 5, 14))
    fill = bpy.context.object
    fill.data.energy = 1000
    fill.data.size = 10
    aim(fill)
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 20))
    bpy.context.object.data.energy = 1.1
    bpy.context.object.rotation_euler = (math.radians(25), math.radians(-20), math.radians(32))

    span = max(layout["widthM"], layout["heightM"])
    bpy.ops.object.camera_add(location=(span * 0.64, -span * 0.76, span * 0.68))
    camera = bpy.context.object
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = max(layout["widthM"] * 1.08, layout["heightM"] * 1.46)
    aim(camera, (0, 0, 0.35))
    scene.camera = camera


def render_layout(repo_root: Path, layout: dict, output: Path, manifest: dict) -> None:
    reset_scene()
    material_root = repo_root / "artifacts/neighborhood-park-adaptive-urban-v1/materials"
    materials = {
        role: pbr_material(role, material_root / role, manifest["materials"][role]["metresPerTile"])
        for role in manifest["materials"]
    }
    edge = solid_material("Graphite plate edge", (0.045, 0.06, 0.055, 1.0), 0.88)
    dark_ground = solid_material("Presentation ground material", (0.055, 0.07, 0.065, 1.0), 0.94)
    trunk = solid_material("Tree trunk", (0.22, 0.12, 0.06, 1.0), 0.92)
    foliage = solid_material("Tree foliage", (0.20, 0.38, 0.16, 1.0), 0.98)
    metal = solid_material("Dark metal", (0.065, 0.085, 0.09, 1.0), 0.48, 0.7)
    accent = solid_material("Play accent", (0.78, 0.52, 0.20, 1.0), 0.72)

    triangle_mesh("Parcel edge", layout["surfaces"]["paver"], 0.08, edge, 0.38)
    heights = {"paver": 0.30, "lawn": 0.43, "planting": 0.48, "safety": 0.47, "asphalt": 0.52, "timber": 0.57}
    for role in ("paver", "lawn", "planting", "safety", "asphalt", "timber"):
        triangle_mesh(role.title(), layout["surfaces"][role], heights[role], materials[role], 0.14)
    for index, point in enumerate(layout["trees"]):
        add_tree(index, point, trunk, foliage)
    add_play_equipment(layout["playCenter"], metal, accent)
    add_pavilion(layout["pavilionCenter"], metal, materials["timber"])
    setup_scene(layout, dark_ground)
    bpy.context.scene.render.filepath = str(output / f"{layout['id']}.png")
    bpy.ops.render.render(write_still=True)


def main() -> None:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    root = repo_root / "artifacts/neighborhood-park-adaptive-urban-v1"
    layouts = json.loads((root / "layouts/adaptive_layouts.json").read_text(encoding="utf-8"))["layouts"]
    materials = json.loads((root / "materials/manifest.json").read_text(encoding="utf-8"))
    output = root / "renders"
    output.mkdir(parents=True, exist_ok=True)
    for layout in layouts.values():
        render_layout(repo_root, layout, output, materials)
        print(f"rendered {output / (layout['id'] + '.png')}")


if __name__ == "__main__":
    main()
