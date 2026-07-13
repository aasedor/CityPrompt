"""Blender headless generator for archetype-compiled modular GLBs.

Run:
  blender --background --python blender_generate.py -- grammar.json output_dir
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import bpy


def hex_rgba(value: str, alpha: float = 1.0):
    value = value.lstrip("#")
    if len(value) != 6:
        value = "808080"
    return tuple(int(value[i:i+2], 16) / 255 for i in (0, 2, 4)) + (alpha,)


def material(name: str, color: str, metallic=0.0, roughness=0.55):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = hex_rgba(color)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = hex_rgba(color)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def cube(name, size, location, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new("EdgeSoftening", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    obj.data.materials.append(mat)
    return obj


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def add_front_windows(width, depth, height, z0, grammar, mats, storefront=False):
    facade = grammar["facade"]
    bay = max(1.8, float(facade["bay_width_m"]))
    count = max(1, int(width // bay))
    actual_bay = width / count
    window_w = min(float(facade["window_width_m"]), actual_bay * 0.72)
    window_h = height * (0.62 if storefront else 0.5)
    sill = 0.35 if storefront else float(facade.get("sill_height_m", 0.9))
    y = -depth / 2 - 0.035
    for i in range(count):
        x = -width / 2 + actual_bay * (i + 0.5)
        cube(
            f"Window_{i:02d}",
            (window_w, 0.08, window_h),
            (x, y, z0 + sill + window_h / 2),
            mats["glass"],
            0.025,
        )
        cube(
            f"Frame_{i:02d}",
            (window_w + 0.14, 0.07, window_h + 0.14),
            (x, y + 0.045, z0 + sill + window_h / 2),
            mats["accent"],
            0.02,
        )


def create_podium(grammar, mats):
    w, d, h = grammar["width_m"], grammar["depth_m"], grammar["podium_height_m"]
    cube("PodiumMass", (w, d, h), (0, 0, h / 2), mats["primary"], 0.08)
    add_front_windows(w, d, h, 0, grammar, mats, storefront=True)
    cube("Canopy", (w * 0.72, 1.25, 0.18), (0, -d / 2 - 0.58, h * 0.72), mats["accent"], 0.04)


def create_floor(grammar, mats, setback=False):
    h = grammar["setback_height_m"] if setback else grammar["floor_height_m"]
    inset = 1.4 if setback else 0.0
    w, d = grammar["width_m"] - inset * 2, grammar["depth_m"] - inset * 2
    cube("FloorMass", (w, d, h), (0, 0, h / 2), mats["secondary" if setback else "primary"], 0.06)
    add_front_windows(w, d, h, 0, grammar, mats)
    if grammar["facade"].get("balcony_probability", 0) > 0:
        cube("BalconyBand", (w * 0.72, 1.25, 0.16), (0, -d / 2 - 0.58, h * 0.42), mats["accent"], 0.03)


def create_roof(grammar, mats):
    w, d, h = grammar["width_m"], grammar["depth_m"], grammar["roof_height_m"]
    if grammar.get("roof_type") == "gabled":
        cube("RoofBase", (w, d, 0.25), (0, 0, 0.125), mats["roof"])
        bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=max(w, d) * 0.7, radius2=0, depth=h, location=(0, 0, h / 2))
        roof = bpy.context.object
        roof.name = "GabledRoof"
        roof.scale.y = d / w
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        roof.data.materials.append(mats["roof"])
    else:
        cube("RoofSlab", (w, d, 0.3), (0, 0, 0.15), mats["roof"])
        parapet = 0.65
        t = 0.22
        cube("ParapetFront", (w, t, parapet), (0, -d / 2 + t / 2, parapet / 2), mats["roof"])
        cube("ParapetBack", (w, t, parapet), (0, d / 2 - t / 2, parapet / 2), mats["roof"])
        cube("ParapetLeft", (t, d, parapet), (-w / 2 + t / 2, 0, parapet / 2), mats["roof"])
        cube("ParapetRight", (t, d, parapet), (w / 2 - t / 2, 0, parapet / 2), mats["roof"])
        cube("MechanicalScreen", (w * 0.22, d * 0.25, h), (0, d * 0.1, h / 2), mats["accent"], 0.04)


def export_selected(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
        export_extras=True,
    )


def generate(grammar, output: Path):
    palette = grammar["palette"]
    mats = {
        "primary": material("MAT_Facade_Primary", palette["primary"]),
        "secondary": material("MAT_Facade_Secondary", palette["secondary"]),
        "accent": material("MAT_Accent", palette["accent"], metallic=0.25),
        "glass": material("MAT_Glass", palette["glazing"], roughness=0.18),
        "roof": material("MAT_Roof", palette["roof"]),
    }
    family = grammar["family"]
    jobs = [
        ("podium", create_podium),
        ("floor", lambda g, m: create_floor(g, m, False)),
        ("roof", create_roof),
    ]
    if grammar.get("has_setback"):
        jobs.insert(2, ("setback", lambda g, m: create_floor(g, m, True)))

    manifest = {"family": family, "archetype_id": grammar["archetype_id"], "modules": []}
    for role, builder in jobs:
        clear_scene()
        builder(grammar, mats)
        glb = output / f"{family}_{role}.glb"
        export_selected(glb)
        height_key = {"podium": "podium_height_m", "floor": "floor_height_m", "setback": "setback_height_m", "roof": "roof_height_m"}[role]
        manifest["modules"].append({
            "role": role,
            "path": glb.name,
            "module_family": family,
            "archetype_ids": [grammar["archetype_id"]],
            "reuse_keys": grammar["reuse_keys"],
            "width_m": grammar["width_m"],
            "depth_m": grammar["depth_m"],
            "height_m": grammar[height_key],
            "repeatable_z": role == "floor",
        })
    (output / f"{family}_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(argv) != 2:
        raise SystemExit("Usage: blender --background --python blender_generate.py -- grammar.json output_dir")
    grammar = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    generate(grammar, Path(argv[1]))


if __name__ == "__main__":
    main()
