"""Extract one exact vertical band from a reviewed GLB.

Run with Blender, not CPython::

    blender -b --python blender_extract_vertical_module.py -- \
      source.glb output.glb 19.4 22.6

The operation clips every mesh at the two authored floor planes, translates the
band to ground level, and preserves its materials.  It is intended for a finite,
reviewed modularization task; the caller owns the source lock and must record
the source/output hashes and the architectural meaning of the cut planes.
"""

from __future__ import annotations

import sys
from pathlib import Path

import bmesh
import bpy


def _arguments() -> tuple[Path, Path, float, float]:
    try:
        separator = sys.argv.index("--")
        source, output, lower, upper = sys.argv[separator + 1 : separator + 5]
    except (ValueError, IndexError) as exc:
        raise SystemExit("Expected: source.glb output.glb lower_m upper_m") from exc
    lower_m, upper_m = float(lower), float(upper)
    if lower_m < 0 or upper_m <= lower_m:
        raise SystemExit("Vertical module planes must satisfy 0 <= lower < upper")
    return Path(source).resolve(), Path(output).resolve(), lower_m, upper_m


def _clip_mesh(obj: bpy.types.Object, lower_m: float, upper_m: float) -> bool:
    """Clip one imported mesh in Blender Z-up coordinates."""
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.select_set(False)

    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    geometry = list(mesh.verts) + list(mesh.edges) + list(mesh.faces)
    bmesh.ops.bisect_plane(
        mesh,
        geom=geometry,
        plane_co=(0.0, 0.0, lower_m),
        plane_no=(0.0, 0.0, 1.0),
        clear_inner=True,
        clear_outer=False,
    )
    geometry = list(mesh.verts) + list(mesh.edges) + list(mesh.faces)
    bmesh.ops.bisect_plane(
        mesh,
        geom=geometry,
        plane_co=(0.0, 0.0, upper_m),
        plane_no=(0.0, 0.0, 1.0),
        clear_inner=False,
        clear_outer=True,
    )
    if not mesh.faces:
        mesh.free()
        return False
    bmesh.ops.translate(mesh, verts=list(mesh.verts), vec=(0.0, 0.0, -lower_m))
    mesh.to_mesh(obj.data)
    mesh.free()
    obj.data.update()
    return True


def main() -> None:
    source, output, lower_m, upper_m = _arguments()
    if not source.is_file():
        raise SystemExit(f"Source GLB is missing: {source}")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source))
    for obj in list(bpy.context.scene.objects):
        if obj.type == "MESH" and not _clip_mesh(obj, lower_m, upper_m):
            bpy.data.objects.remove(obj, do_unlink=True)
    if not any(obj.type == "MESH" for obj in bpy.context.scene.objects):
        raise SystemExit("The selected vertical band contains no mesh geometry")
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(output),
        export_format="GLB",
        export_yup=True,
        export_apply=True,
    )
    print(f"Extracted {lower_m:.3f}-{upper_m:.3f} m to {output}")


if __name__ == "__main__":
    main()
