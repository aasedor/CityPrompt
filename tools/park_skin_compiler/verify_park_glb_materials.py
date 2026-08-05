"""Verify that textured park GLB surfaces retain portable UV0 coordinates.

Run inside Blender:
  blender --background --python verify_park_glb_materials.py -- \
    --glb path/to/full-park-assembly.glb --report path/to/report.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--glb", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(argv)


def material_uses_images(material) -> bool:
    return bool(
        material
        and material.use_nodes
        and any(
            node.bl_idname == "ShaderNodeTexImage" and node.image
            for node in material.node_tree.nodes
        )
    )


def main() -> None:
    args = parse_args()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(args.glb.resolve()))
    textured_meshes = []
    missing_uv0 = []
    for object_ in bpy.context.scene.objects:
        if object_.type != "MESH":
            continue
        textured = any(material_uses_images(material) for material in object_.data.materials)
        if not textured:
            continue
        textured_meshes.append(object_.name)
        if len(object_.data.uv_layers) == 0:
            missing_uv0.append(object_.name)
    report = {
        "schemaVersion": 1,
        "glb": str(args.glb),
        "texturedMeshCount": len(textured_meshes),
        "missingUv0": missing_uv0,
        "passed": len(textured_meshes) > 0 and not missing_uv0,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
