"""Create a compact, source-conditioned City Prompt GLB from an RLASM keeper.

Run through Blender:

    blender -b --python tools/archetype_compiler/blender_rlasm_delivery.py -- \
      --contract artifacts/.../delivery-contract.json \
      --output artifacts/.../candidate-cityprompt.glb \
      --provenance artifacts/.../delivery-provenance.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy


TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from rlasm_delivery_contract import (  # noqa: E402
    load_delivery_contract,
    validate_delivery_glb,
)


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--provenance", type=Path, required=True)
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(argv)


def _clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        if collection.users == 0:
            bpy.data.collections.remove(collection)


def _remove_evidence_context(prefixes: tuple[str, ...]) -> list[str]:
    removed: list[str] = []
    for obj in list(bpy.data.objects):
        if any(obj.name.startswith(prefix) for prefix in prefixes):
            removed.append(obj.name)
            bpy.data.objects.remove(obj, do_unlink=True)
    return removed


def _set_input(bsdf, name: str, value) -> None:
    socket = bsdf.inputs.get(name)
    if socket is None:
        raise RuntimeError(f"Blender Principled BSDF input is unavailable: {name}")
    socket.default_value = value


def _apply_optical_contract(contract) -> None:
    for optical in contract.optical_materials:
        material = bpy.data.materials.get(optical.name)
        if material is None:
            raise RuntimeError(f"required optical material is missing: {optical.name}")
        material.use_nodes = True
        material.surface_render_method = "BLENDED"
        material.use_transparency_overlap = False
        material.diffuse_color = optical.base_color
        material["rlasm_source_role"] = optical.source_role
        material["rlasm_source_sha256"] = optical.source_sha256
        material["rlasm_delivery_optical"] = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        nodes.clear()
        output = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        _set_input(bsdf, "Base Color", optical.base_color)
        _set_input(bsdf, "Roughness", optical.roughness)
        _set_input(bsdf, "Metallic", optical.metallic)
        _set_input(bsdf, "Transmission Weight", optical.transmission)
        _set_input(bsdf, "IOR", optical.ior)
        _set_input(bsdf, "Alpha", optical.base_color[3])
        links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])


def main() -> int:
    args = _arguments()
    contract = load_delivery_contract(args.contract.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.provenance.parent.mkdir(parents=True, exist_ok=True)

    _clear_scene()
    bpy.ops.import_scene.gltf(filepath=str(contract.source_glb))
    removed = _remove_evidence_context(contract.exclude_object_prefixes)
    _apply_optical_contract(contract)
    bpy.context.scene["rlasm_source_candidate"] = contract.candidate
    bpy.context.scene["rlasm_delivery_version"] = contract.delivery_version
    bpy.context.scene["rlasm_source_sha256"] = contract.source_sha256

    bpy.ops.export_scene.gltf(
        filepath=str(args.output.resolve()),
        export_format="GLB",
        export_yup=True,
        export_materials="EXPORT",
        export_attributes=True,
        export_extras=True,
        export_apply=True,
        export_cameras=False,
        export_lights=False,
    )

    provenance = validate_delivery_glb(args.output.resolve(), contract)
    provenance["removed_objects"] = removed
    provenance["removed_object_count"] = len(removed)
    args.provenance.write_text(
        json.dumps(provenance, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(provenance, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
