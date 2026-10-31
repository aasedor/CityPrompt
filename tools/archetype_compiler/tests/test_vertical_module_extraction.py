"""Exact source cuts use world floor datums, including translated source nodes."""
import subprocess
from pathlib import Path

from tools.archetype_compiler.blender_locator import find_blender


def test_translated_mesh_is_clipped_at_world_floor_planes():
    extractor = Path(__file__).resolve().parents[1] / 'blender_extract_vertical_module.py'
    expression = f"""
import bpy, runpy
from mathutils import Vector
clip = runpy.run_path({str(extractor)!r})['_clip_mesh']
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_cube_add(size=2, location=(2, 3, 10))
obj = bpy.context.object
assert clip(obj, 9.5, 10.5), 'Translated source mesh disappeared during world-plane clipping'
points = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
assert abs(min(p.z for p in points)) < 1e-5, 'Clipped base is not zero'
assert abs(max(p.z for p in points)-1) < 1e-5, 'Clipped height changed'
assert abs(min(p.x for p in points)-1) < 1e-5, 'Authored horizontal offset changed'
assert abs(min(p.y for p in points)-2) < 1e-5, 'Authored horizontal offset changed'
"""
    result = subprocess.run([find_blender(), '-b', '--python-exit-code', '1', '--python-expr', expression],
                            capture_output=True, text=True, timeout=90)
    assert result.returncode == 0, result.stdout + result.stderr
