"""Derive a texture-free semantic architectural-clay GLB from an RLASM GLB.

Run with Blender 5.2 in background mode.  Geometry, object transforms, and the
bottom-centre coordinate contract are inherited unchanged from the source GLB.
Only material ownership changes: source-specific PBR materials are collapsed
to a small flat-role palette that tells the image model which construction
systems are roof, wall, trim, glass, timber, masonry, interior, or hardware.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


SEMANTIC_PALETTE: dict[str, tuple[tuple[float, float, float, float], float]] = {
    "masonry": ((0.55, 0.28, 0.20, 1.0), 0.86),
    "wall": ((0.72, 0.69, 0.62, 1.0), 0.88),
    "trim": ((0.88, 0.84, 0.74, 1.0), 0.82),
    "roof": ((0.30, 0.31, 0.31, 1.0), 0.92),
    "glass": ((0.18, 0.29, 0.33, 1.0), 0.36),
    "timber": ((0.43, 0.27, 0.14, 1.0), 0.79),
    "interior": ((0.66, 0.47, 0.27, 1.0), 0.84),
    "hardware": ((0.10, 0.11, 0.12, 1.0), 0.58),
}


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--preview", type=Path, required=True)
    return parser.parse_args(argv)


def semantic_role(source_name: str) -> str:
    name = source_name.upper()
    if any(token in name for token in ("GLASS", "CURTAIN")):
        return "glass"
    if any(token in name for token in ("SHINGLE", "ROOF")):
        return "roof"
    if any(token in name for token in ("BRICK", "MASONRY")):
        return "masonry"
    if any(token in name for token in ("TRIM", "FLASHING")):
        return "trim"
    if any(token in name for token in ("TIMBER", "FIR", "WOOD")):
        return "timber"
    if any(token in name for token in ("HARDWARE", "APPLIANCE", "METAL")):
        return "hardware"
    if any(
        token in name
        for token in ("INTERIOR", "LIGHT", "CUSHION", "RUG", "SOFA", "CABINET", "COUNTER")
    ):
        return "interior"
    return "wall"


def make_flat_material(role: str) -> bpy.types.Material:
    color, roughness = SEMANTIC_PALETTE[role]
    material = bpy.data.materials.new(f"CP_SEMANTIC_CLAY_{role.upper()}")
    material.use_nodes = True
    material.diffuse_color = color
    nodes = material.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = 0.0
    material.node_tree.links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    return material


def remap_materials() -> dict[str, int]:
    semantic_materials = {role: make_flat_material(role) for role in SEMANTIC_PALETTE}
    role_slots = {role: 0 for role in SEMANTIC_PALETTE}
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH":
            continue
        for slot in obj.material_slots:
            source_name = slot.material.name if slot.material else ""
            role = semantic_role(source_name)
            slot.material = semantic_materials[role]
            role_slots[role] += 1
        obj["cityprompt_material_mode"] = "semantic_architectural_clay"
    return {role: count for role, count in role_slots.items() if count}


def mesh_bounds() -> tuple[Vector, Vector]:
    points: list[Vector] = []
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH" or obj.hide_render:
            continue
        points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    if not points:
        raise RuntimeError("Imported GLB contains no renderable mesh bounds")
    return (
        Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points))),
        Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points))),
    )


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def render_preview(path: Path) -> None:
    bounds_min, bounds_max = mesh_bounds()
    centre = (bounds_min + bounds_max) * 0.5
    width = bounds_max.x - bounds_min.x
    depth = bounds_max.y - bounds_min.y
    height = bounds_max.z - bounds_min.z

    bpy.ops.object.camera_add(
        location=(centre.x + width * 0.92, bounds_min.y - depth * 1.38, bounds_min.z + height * 0.92)
    )
    camera = bpy.context.object
    camera.data.lens = 54
    look_at(camera, Vector((centre.x, centre.y, bounds_min.z + height * 0.43)))
    bpy.context.scene.camera = camera

    bpy.ops.object.light_add(type="AREA", location=(centre.x - width * 0.25, centre.y - depth, bounds_max.z + height))
    key = bpy.context.object
    key.data.energy = 1450
    key.data.shape = "DISK"
    key.data.size = max(width, depth) * 1.25
    look_at(key, centre)

    bpy.ops.object.light_add(type="AREA", location=(centre.x + width, centre.y + depth * 0.25, bounds_max.z + height * 0.35))
    fill = bpy.context.object
    fill.data.energy = 700
    fill.data.size = max(width, depth)
    look_at(fill, centre)

    bpy.ops.object.light_add(type="SUN", location=(0.0, 0.0, bounds_max.z + 10.0))
    sun = bpy.context.object
    sun.rotation_euler = (math.radians(28.0), math.radians(-18.0), math.radians(132.0))
    sun.data.energy = 1.25
    sun.data.angle = math.radians(10.0)

    world = bpy.context.scene.world or bpy.data.worlds.new("Semantic Clay World")
    bpy.context.scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.085, 0.105, 0.12, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.48

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.filepath = str(path.resolve())
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.look = "AgX - Medium High Contrast"
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.render.render(write_still=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    args = parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    preview = args.preview.resolve()
    if not source.is_file():
        raise FileNotFoundError(source)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source))
    role_slots = remap_materials()
    bounds_min, bounds_max = mesh_bounds()

    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(output),
        export_format="GLB",
        export_yup=True,
        export_materials="EXPORT",
        export_extras=True,
        export_cameras=False,
        export_lights=False,
    )
    render_preview(preview)

    print(
        "SEMANTIC_CLAY_EXPORT "
        + json.dumps(
            {
                "source": str(source),
                "source_sha256": sha256(source),
                "output": str(output),
                "output_sha256": sha256(output),
                "output_bytes": output.stat().st_size,
                "preview": str(preview),
                "semantic_roles": role_slots,
                "blender_bounds": {
                    "min": [round(value, 6) for value in bounds_min],
                    "max": [round(value, 6) for value in bounds_max],
                },
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
