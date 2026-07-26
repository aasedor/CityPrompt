"""Convert a fused Meshy concert-hall GLB into a bounded fixed LEGO assembly.

The image-to-3D source is useful for its crown, apertures and roof, but its
warehouse base must remain a repeatable City Prompt kit. This Blender script
normalizes the source to the authored 90 x 65 x 57.2 m envelope, removes
geometry below the crown interface, decimates the retained surface and
downsamples embedded textures for a practical runtime reference module.

Run with Blender:

  blender --background --factory-startup --python convert_meshy_concert_reference.py -- \
      --source source.glb --output concert-hall-modern-v1-meshy-crown.glb
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector


TARGET_SIZE = (90.0, 65.0, 57.2)
CROWN_INTERFACE_Z_M = 17.4
TARGET_TRIANGLES = 120_000
MAX_TEXTURE_PX = 1024


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--interface-z", type=float, default=CROWN_INTERFACE_Z_M)
    parser.add_argument("--target-triangles", type=int, default=TARGET_TRIANGLES)
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(args)


def world_bounds(obj: bpy.types.Object) -> tuple[Vector, Vector]:
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return (
        Vector((min(v.x for v in corners), min(v.y for v in corners), min(v.z for v in corners))),
        Vector((max(v.x for v in corners), max(v.y for v in corners), max(v.z for v in corners))),
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> int:
    args = parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    manifest = (args.manifest or output.with_suffix(".manifest.json")).resolve()
    if not source.exists():
        raise FileNotFoundError(source)

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(source))
    imported = [
        obj for obj in bpy.data.objects
        if obj not in before and obj.type == "MESH"
    ]
    if not imported:
        raise RuntimeError(f"no mesh objects imported from {source}")
    crown = max(imported, key=lambda obj: len(obj.data.polygons))
    source_triangles = len(crown.data.polygons)

    minimum, maximum = world_bounds(crown)
    source_size = maximum - minimum
    crown.scale = (
        TARGET_SIZE[0] / source_size.x,
        TARGET_SIZE[1] / source_size.y,
        TARGET_SIZE[2] / source_size.z,
    )
    bpy.context.view_layer.objects.active = crown
    crown.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    minimum, maximum = world_bounds(crown)
    crown.location += Vector((
        -(minimum.x + maximum.x) / 2,
        -(minimum.y + maximum.y) / 2,
        -minimum.z,
    ))
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

    mesh = crown.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    below = [vertex for vertex in bm.verts if vertex.co.z < float(args.interface_z)]
    bmesh.ops.delete(bm, geom=below, context="VERTS")
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    if not mesh.polygons:
        raise RuntimeError("crown cut removed every source polygon")

    pre_decimate_triangles = len(mesh.polygons)
    if pre_decimate_triangles > args.target_triangles:
        modifier = crown.modifiers.new(name="RuntimeTriangleBudget", type="DECIMATE")
        modifier.decimate_type = "COLLAPSE"
        modifier.ratio = max(0.01, args.target_triangles / pre_decimate_triangles)
        modifier.use_collapse_triangulate = True
        bpy.context.view_layer.objects.active = crown
        bpy.ops.object.modifier_apply(modifier=modifier.name)

    for image in bpy.data.images:
        if image.source == "GENERATED":
            continue
        width, height = image.size
        maximum_dimension = max(width, height)
        if maximum_dimension > MAX_TEXTURE_PX:
            ratio = MAX_TEXTURE_PX / maximum_dimension
            image.scale(max(1, round(width * ratio)), max(1, round(height * ratio)))

    crown.name = "FIXED_ConcertHall_MeshyCrown"
    crown.data.name = crown.name
    crown["lego_role"] = "fixed_crown_roof"
    crown["source_kind"] = "meshy_image_to_3d"
    crown["interface_z_m"] = float(args.interface_z)
    crown["target_dimensions_m"] = list(TARGET_SIZE)

    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    crown.select_set(True)
    bpy.context.view_layer.objects.active = crown
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(output),
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=True,
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_draco_position_quantization=14,
        export_draco_normal_quantization=10,
        export_draco_texcoord_quantization=12,
    )

    payload = {
        "schema": "external-fixed-assembly@1",
        "source_file": source.name,
        "source_sha256": sha256(source),
        "output_file": output.name,
        "output_sha256": sha256(output),
        "source_triangles": source_triangles,
        "pre_decimate_triangles": pre_decimate_triangles,
        "output_triangles": len(crown.data.polygons),
        "target_dimensions_m": list(TARGET_SIZE),
        "interface_z_m": float(args.interface_z),
        "max_texture_px": MAX_TEXTURE_PX,
        "lego_contract": {
            "role": "fixed_crown_roof",
            "repeatable": False,
            "paired_repeatable_kit": "concert_warehouse_brick",
        },
    }
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
