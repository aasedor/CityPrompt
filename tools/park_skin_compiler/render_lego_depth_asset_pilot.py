"""Render the LEGO-surface / authored-depth basketball pilot in Blender."""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from .render_adaptive_park_shapes import (
        add_pavilion,
        add_tree,
        aim,
        cube,
        pbr_material,
        reset_scene,
        solid_material,
        triangle_mesh,
    )
except ImportError:  # Blender direct script execution
    from render_adaptive_park_shapes import (
        add_pavilion,
        add_tree,
        aim,
        cube,
        pbr_material,
        reset_scene,
        solid_material,
        triangle_mesh,
    )


COURT_TOP_Z = 0.68


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(argv)


def torus(name: str, major_radius: float, minor_radius: float, location, material):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_radius,
        minor_radius=minor_radius,
        major_segments=64,
        minor_segments=8,
        location=location,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    return obj


def import_asset(path: Path, name: str, location, yaw: float):
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    imported = [obj for obj in bpy.context.scene.objects if obj not in before]
    root = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(root)
    for obj in imported:
        if obj.parent is None:
            obj.parent = root
    root.location = location
    root.rotation_euler[2] = yaw
    if tuple(root.scale) != (1.0, 1.0, 1.0):
        raise RuntimeError(f"{name} was unexpectedly scaled")
    return root


def add_court_markings(center, line_material) -> None:
    cx, cy = center
    line_z = COURT_TOP_Z + 0.016
    for offset_y in (-7.5, 7.5):
        cube(f"Court sideline {offset_y}", (cx, cy + offset_y, line_z), (28.0, 0.07, 0.02), line_material, 0.01)
    for offset_x in (-14.0, 0.0, 14.0):
        cube(f"Court line {offset_x}", (cx + offset_x, cy, line_z), (0.07, 15.0, 0.02), line_material, 0.01)
    torus("Court center circle", 1.8, 0.035, (cx, cy, line_z + 0.006), line_material)
    for direction in (-1, 1):
        key_x = cx + direction * 11.55
        cube(f"Key outer {direction}", (key_x, cy, line_z), (4.9, 4.9, 0.018), line_material, 0.015)
        cube(f"Key fill {direction}", (key_x, cy, line_z + 0.012), (4.72, 4.72, 0.018), bpy.data.materials["Court acrylic"], 0.01)


def add_depth_kit(repo_root: Path, center) -> None:
    asset_root = repo_root / "frontend/public/park-kits"
    paths = {
        "hoop": asset_root / "basketball-hoop.glb",
        "fence": asset_root / "chainlink-fence-4m.glb",
        "gate": asset_root / "chainlink-gate-3m.glb",
        "floodlight": asset_root / "basketball-floodlight.glb",
    }
    missing = [str(path) for path in paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing pilot depth assets:\n" + "\n".join(missing))
    cx, cy = center
    z = COURT_TOP_Z + 0.025
    import_asset(paths["hoop"], "Hoop west", (cx - 15.2, cy, z), 0.0)
    import_asset(paths["hoop"], "Hoop east", (cx + 15.2, cy, z), math.pi)
    for side_y in (-9.5, 9.5):
        for x in (-14, -10, -6, -2, 2, 6, 10, 14):
            import_asset(paths["fence"], f"Fence Y{side_y} X{x}", (cx + x, cy + side_y, z), 0.0)
    end_pattern = [(-7.5, "fence"), (-3.5, "fence"), (0.0, "gate"), (3.5, "fence"), (7.5, "fence")]
    for side_x in (-16.0, 16.0):
        for y, kind in end_pattern:
            import_asset(paths[kind], f"Fence X{side_x} Y{y}", (cx + side_x, cy + y, z), math.pi / 2)
    for x, y in ((-15.5, -9.0), (-15.5, 9.0), (15.5, -9.0), (15.5, 9.0)):
        import_asset(
            paths["floodlight"],
            f"Floodlight {x} {y}",
            (cx + x, cy + y, z),
            math.atan2(-y, -x),
        )


def build_scene(repo_root: Path, layout: dict, with_depth: bool) -> None:
    reset_scene()
    material_root = repo_root / "artifacts/neighborhood-park-adaptive-urban-v1/materials"
    manifest = json.loads((material_root / "manifest.json").read_text(encoding="utf-8"))
    materials = {
        role: pbr_material(role, material_root / role, manifest["materials"][role]["metresPerTile"])
        for role in manifest["materials"]
    }
    edge = solid_material("Graphite plate edge", (0.045, 0.06, 0.055, 1.0), 0.88)
    dark_ground = solid_material("Presentation ground material", (0.055, 0.07, 0.065, 1.0), 0.94)
    trunk = solid_material("Tree trunk", (0.22, 0.12, 0.06, 1.0), 0.92)
    foliage = solid_material("Tree foliage", (0.20, 0.38, 0.16, 1.0), 0.98)
    metal = solid_material("Dark metal", (0.065, 0.085, 0.09, 1.0), 0.48, 0.7)
    court = solid_material("Court acrylic", (0.055, 0.285, 0.41, 1.0), 0.82)
    line = solid_material("Court marking", (0.9, 0.91, 0.84, 1.0), 0.7)

    triangle_mesh("Parcel edge", layout["surfaces"]["paver"], 0.08, edge, 0.38)
    heights = {"paver": 0.30, "lawn": 0.43, "planting": 0.48, "asphalt": 0.52, "timber": 0.57}
    for role in ("paver", "lawn", "planting", "asphalt", "timber"):
        triangle_mesh(role.title(), layout["surfaces"][role], heights[role], materials[role], 0.14)
    triangle_mesh("Exact 32 x 19 m court envelope", layout["surfaces"]["court"], COURT_TOP_Z, court, 0.16)
    add_court_markings(layout["court"]["center"], line)
    for index, point in enumerate(layout["trees"]):
        add_tree(index, point, trunk, foliage)
    add_pavilion(layout["pavilionCenter"], metal, materials["timber"])
    if with_depth:
        add_depth_kit(repo_root, layout["court"]["center"])
    cube("Presentation ground", (0, 0, -0.42), (92, 74, 0.4), dark_ground, 0.5)


def setup_lighting() -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.world.color = (0.035, 0.045, 0.042)
    bpy.ops.object.light_add(type="AREA", location=(-18, -22, 34))
    key = bpy.context.object
    key.data.energy = 2100
    key.data.size = 15
    aim(key, (2, 0, 1))
    bpy.ops.object.light_add(type="AREA", location=(28, 12, 22))
    fill = bpy.context.object
    fill.data.energy = 1250
    fill.data.size = 12
    aim(fill, (8, 0, 2))
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 28))
    bpy.context.object.data.energy = 1.3
    bpy.context.object.rotation_euler = (math.radians(25), math.radians(-20), math.radians(32))


def add_camera(location, target, ortho_scale: float):
    bpy.ops.object.camera_add(location=location)
    camera = bpy.context.object
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = ortho_scale
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = camera
    return camera


def render(repo_root: Path, layout: dict, output: Path, with_depth: bool, view: str) -> None:
    build_scene(repo_root, layout, with_depth)
    setup_lighting()
    scene = bpy.context.scene
    if view == "top":
        add_camera((0, 0, 90), (0, 0, 0), 82)
        scene.render.resolution_x = 1280
        scene.render.resolution_y = 980
    else:
        add_camera((54, -66, 54), (1, 0, 2), 83)
        scene.render.resolution_x = 1440
        scene.render.resolution_y = 980
    scene.render.filepath = str(output)
    bpy.ops.render.render(write_still=True)


def main() -> None:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    layout = json.loads(
        (repo_root / "artifacts/neighborhood-park-lego-depth-pilot/layout/layout.json").read_text(encoding="utf-8")
    )
    render(repo_root, layout, output / "surface_only_overview.png", False, "overview")
    render(repo_root, layout, output / "combined_overview.png", True, "overview")
    render(repo_root, layout, output / "combined_top.png", True, "top")
    print(f"rendered LEGO depth pilot to {output}")


if __name__ == "__main__":
    main()
