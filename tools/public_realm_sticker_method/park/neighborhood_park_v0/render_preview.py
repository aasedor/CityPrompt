"""Render bounded visual-QA views of the compiled Neighborhood Park v0 kit."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[4]
MANIFEST = HERE / "compiled-kit.json"


def args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(argv)


def reset() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def material(name: str, role: str, roughness: float = 0.9) -> bpy.types.Material:
    skin = REPO_ROOT / "frontend/public/park-skins/neighborhood-park-rustic-v0/adaptive-v1"
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    shader = result.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Roughness"].default_value = roughness
    image = bpy.data.images.load(str(skin / role / "albedo.jpg"), check_existing=True)
    texture = result.node_tree.nodes.new("ShaderNodeTexImage")
    texture.image = image
    texture.interpolation = "Linear"
    result.node_tree.links.new(texture.outputs["Color"], shader.inputs["Base Color"])
    return result


def plane(
    name: str,
    size: tuple[float, float],
    center: tuple[float, float],
    z: float,
    mat: bpy.types.Material,
    yaw_deg: float = 0,
) -> None:
    bpy.ops.mesh.primitive_plane_add(size=2, location=(center[0], center[1], z))
    obj = bpy.context.object
    obj.name = name
    obj.scale = (size[0] / 2, size[1] / 2, 1)
    obj.rotation_euler[2] = math.radians(yaw_deg)
    obj.data.materials.append(mat)


def ellipse(name: str, size: tuple[float, float], center: tuple[float, float], z: float, mat: bpy.types.Material) -> None:
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=1, depth=0.035, location=(center[0], center[1], z))
    obj = bpy.context.object
    obj.name = name
    obj.scale = (size[0] / 2, size[1] / 2, 1)
    obj.data.materials.append(mat)


def import_asset(url: str, location: list[float], yaw_deg: float) -> None:
    path = REPO_ROOT / "frontend/public" / url.removeprefix("/")
    existing = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    imported = [obj for obj in bpy.context.scene.objects if obj not in existing]
    root = bpy.data.objects.new(f"placement_{path.stem}", None)
    bpy.context.collection.objects.link(root)
    root.location = location
    root.rotation_euler[2] = math.radians(yaw_deg)
    for obj in imported:
        if obj.parent is None:
            obj.parent = root


def tree(x: float, y: float, scale: float) -> None:
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.25 * scale, depth=3.2 * scale, location=(x, y, 1.6 * scale))
    trunk = bpy.context.object
    trunk.data.materials.append(bpy.data.materials["preview_timber"])
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=2.2 * scale, location=(x, y, 4.0 * scale))
    crown = bpy.context.object
    crown.data.materials.append(bpy.data.materials["preview_lawn"])


def look_at(camera: bpy.types.Object, target: tuple[float, float, float]) -> None:
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()


def main() -> int:
    options = args()
    options.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    reset()

    lawn = material("preview_lawn", "lawn")
    timber = material("preview_timber", "timber", 0.82)
    paver = material("preview_paver", "paver")
    safety = material("preview_safety", "safety")
    asphalt = material("preview_asphalt", "asphalt")
    plane("site_adaptive_lawn", (58, 46), (0, 0), 0, lawn)
    for patch in manifest["groundPatches"]:
        mat = {"paver": paver, "safety": safety, "asphalt": asphalt}[patch["role"]]
        if patch["kind"] == "ellipse":
            ellipse(patch["id"], tuple(patch["sizeM"]), tuple(patch["centerM"]), patch["zM"], mat)
        else:
            plane(
                patch["id"], tuple(patch["sizeM"]), tuple(patch["centerM"]), patch["zM"], mat,
                patch.get("yawDeg", 0),
            )

    for placement in manifest["placements"]:
        import_asset(
            manifest["assets"][placement["assetId"]]["url"],
            placement["positionM"],
            placement["yawDeg"],
        )

    for x, y, scale in [(-25, -14, 1.1), (-23, 15, 0.9), (23, -14, 1.0), (25, 13, 1.15), (-20, -5, 0.8), (21, 3, 0.85)]:
        tree(x, y, scale)

    world = bpy.context.scene.world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.18, 0.23, 0.30, 1)
    background.inputs["Strength"].default_value = 0.65
    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(28), math.radians(-18), math.radians(-35)))
    bpy.context.object.data.energy = 3.0
    bpy.context.object.data.angle = math.radians(12)
    bpy.ops.object.light_add(type="AREA", location=(-16, -20, 28))
    bpy.context.object.data.energy = 1700
    bpy.context.object.data.shape = "DISK"
    bpy.context.object.data.size = 18
    bpy.ops.object.light_add(type="AREA", location=(20, 12, 14))
    bpy.context.object.data.energy = 650
    bpy.context.object.data.size = 12

    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.data.lens = 48
    bpy.context.scene.camera = camera
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1100
    scene.render.resolution_y = 760
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 1.0

    for filename, location, target in (
        ("neighborhood-park-v0-hero.png", (34, -42, 27), (0, 0, 1.2)),
        ("neighborhood-park-v0-aerial.png", (0, -12, 58), (0, 0, 0)),
    ):
        camera.location = location
        look_at(camera, target)
        scene.render.filepath = str(options.output_dir / filename)
        bpy.ops.render.render(write_still=True)
        print(f"wrote {scene.render.filepath}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
