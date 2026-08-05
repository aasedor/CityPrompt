"""Generate the metric, reusable City Prompt park-equipment kit in Blender.

The kit deliberately keeps the ground/surface in the LEGO park grammar. These
GLBs contain only depth-bearing equipment. Run a two-object pilot first:

    blender --background --factory-startup --python \
      tools/park_skin_compiler/generate_shared_park_equipment.py -- \
      --output-dir artifacts/shared-park-equipment/pilot/glb \
      --preview-dir artifacts/shared-park-equipment/pilot --pilot

Omit ``--pilot`` for the bounded five-asset batch.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_SPEC = SCRIPT_DIR / "shared_park_equipment_spec.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--preview-dir", type=Path, required=True)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--pilot", action="store_true")
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(argv)


def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def material(name, color, *, metallic=0.0, roughness=0.55, emission=None):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    if emission is not None:
        shader.inputs["Emission Color"].default_value = emission
        shader.inputs["Emission Strength"].default_value = 1.25
    return mat


def assign(obj, mat):
    obj.data.materials.append(mat)
    return obj


def box(name, size, location, mat, *, rotation=(0.0, 0.0, 0.0), bevel=0.02):
    bpy.ops.mesh.primitive_cube_add(location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(obj, mat)
    if bevel > 0:
        modifier = obj.modifiers.new("Edge softness", "BEVEL")
        modifier.width = bevel
        modifier.segments = 2
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    return obj


def cylinder(name, radius, depth, location, mat, *, vertices=18, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    assign(obj, mat)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def tube_between(name, start, end, radius, mat, *, vertices=12):
    a = Vector(start)
    b = Vector(end)
    direction = b - a
    obj = cylinder(name, radius, direction.length, tuple((a + b) * 0.5), mat, vertices=vertices)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = direction.to_track_quat("Z", "Y")
    return obj


def torus(name, major_radius, minor_radius, location, mat, *, rotation=(0.0, 0.0, 0.0), arc=math.tau):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_radius,
        minor_radius=minor_radius,
        major_segments=32,
        minor_segments=8,
        abso_major_rad=major_radius + minor_radius,
        abso_minor_rad=minor_radius,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    assign(obj, mat)
    if arc < math.tau - 0.001:
        # Blender's torus operator has no stable partial-arc API across 4.x/5.x;
        # callers use tube segments for open shapes instead.
        raise ValueError("Use tube segments for partial arcs")
    return obj


def materials() -> dict:
    return {
        "steel": material("Powder-coated charcoal steel", (0.075, 0.095, 0.105, 1), metallic=0.63, roughness=0.34),
        "galvanized": material("Galvanized steel", (0.42, 0.47, 0.47, 1), metallic=0.72, roughness=0.34),
        "orange": material("Safety orange", (0.94, 0.20, 0.028, 1), metallic=0.2, roughness=0.42),
        "board": material("Translucent pale backboard", (0.78, 0.86, 0.85, 0.92), roughness=0.24),
        "white": material("Court white", (0.95, 0.95, 0.91, 1), roughness=0.5),
        "net": material("Braided white net", (0.90, 0.91, 0.86, 1), roughness=0.92),
        "pad": material("Navy post padding", (0.026, 0.065, 0.12, 1), roughness=0.76),
        "timber": material("Oiled cedar slats", (0.43, 0.20, 0.075, 1), roughness=0.7),
        "timber_edge": material("Cedar end grain", (0.28, 0.105, 0.035, 1), roughness=0.82),
        "blue": material("Recycling blue", (0.025, 0.30, 0.54, 1), metallic=0.18, roughness=0.5),
        "green": material("Waste green", (0.08, 0.31, 0.20, 1), metallic=0.18, roughness=0.52),
        "black": material("Dark aperture", (0.01, 0.012, 0.013, 1), roughness=0.62),
        "water": material("Water fitting", (0.63, 0.78, 0.78, 1), metallic=0.74, roughness=0.2),
        "label": material("Equipment label", (0.88, 0.88, 0.82, 1), roughness=0.55),
    }


def build_basketball_hoop(mats: dict) -> list:
    objects = [
        cylinder("Post", 0.095, 3.30, (0, 0, 1.65), mats["steel"], vertices=20),
        cylinder("Post pad", 0.18, 1.55, (0, 0, 0.775), mats["pad"], vertices=20),
        tube_between("Gooseneck support", (0, 0, 3.22), (1.22, 0, 3.45), 0.075, mats["steel"], vertices=16),
        box("Backboard", (0.055, 1.80, 1.05), (1.245, 0, 3.425), mats["board"], bevel=0.025),
        torus("Rim", 0.225, 0.012, (1.62, 0, 3.05), mats["orange"]),
        box("Rim bracket", (0.38, 0.08, 0.08), (1.43, 0, 3.05), mats["orange"], bevel=0.01),
        box("Height datum", (0.06, 1.82, 0.01), (1.245, 0, 3.945), mats["steel"], bevel=0),
    ]
    for y in (-0.2825, 0.2825):
        objects.append(box(f"Target side {y}", (0.012, 0.025, 0.305), (1.279, y, 3.39), mats["white"], bevel=0))
    objects.extend([
        box("Target top", (0.012, 0.59, 0.025), (1.279, 0, 3.53), mats["white"], bevel=0),
        box("Target bottom", (0.012, 0.59, 0.025), (1.279, 0, 3.25), mats["white"], bevel=0),
    ])
    rim_center = Vector((1.62, 0, 3.05))
    for index in range(12):
        angle = math.tau * index / 12
        lower = angle + 0.22
        objects.append(tube_between(
            f"Net strand {index:02d}",
            rim_center + Vector((math.cos(angle) * 0.215, math.sin(angle) * 0.215, -0.025)),
            (rim_center.x + math.cos(lower) * 0.115, rim_center.y + math.sin(lower) * 0.115, 2.66),
            0.0065,
            mats["net"],
            vertices=6,
        ))
    objects.append(torus("Net lower ring", 0.115, 0.006, (1.62, 0, 2.66), mats["net"]))
    return objects


def add_slat(objects, name, center, size, mats):
    objects.append(box(name, size, center, mats["timber"], bevel=0.028))
    for x in (-size[0] / 2 + 0.04, size[0] / 2 - 0.04):
        objects.append(box(f"{name} end {x}", (0.025, size[1] * 0.94, size[2] * 0.94), (center[0] + x, center[1], center[2]), mats["timber_edge"], bevel=0.006))


def build_picnic_table(mats: dict) -> list:
    objects = []
    # Five narrow slats give aerial renders readable timber rhythm. The top
    # extends beyond one frame to create an accessible 0.76 m end position.
    for index in range(5):
        add_slat(objects, f"Top slat {index}", (0.18, -0.38 + index * 0.19, 0.735), (2.76, 0.15, 0.09), mats)
    for side in (-1, 1):
        y = side * 0.72
        for index in range(2):
            add_slat(objects, f"Bench {side} slat {index}", (-0.16, y + (index - 0.5) * 0.16, 0.46), (2.08, 0.13, 0.085), mats)
    # Two steel A-frames stop 0.78 m short of the accessible east end.
    for x in (-0.72, 0.48):
        for side in (-1, 1):
            objects.append(tube_between(f"A-frame {x} {side}", (x, side * 0.62, 0.03), (x, side * 0.28, 0.695), 0.038, mats["steel"], vertices=10))
        objects.append(tube_between(f"Crossbar {x}", (x, -0.77, 0.44), (x, 0.77, 0.44), 0.035, mats["steel"], vertices=10))
    objects.append(tube_between("Long brace", (-0.78, 0, 0.34), (0.55, 0, 0.34), 0.038, mats["steel"], vertices=10))
    for x in (-0.72, 0.48):
        for y in (-0.72, 0.72):
            objects.append(cylinder(f"Foot {x} {y}", 0.075, 0.018, (x, y, 0.009), mats["galvanized"], vertices=14))
    return objects


def build_dual_stream_bin(mats: dict) -> list:
    objects = [
        box("Bin cabinet", (0.84, 0.50, 0.90), (0, 0, 0.45), mats["steel"], bevel=0.055),
        box("Blue lid", (0.42, 0.52, 0.12), (-0.21, 0, 0.96), mats["blue"], bevel=0.045),
        box("Green lid", (0.42, 0.52, 0.12), (0.21, 0, 0.96), mats["green"], bevel=0.045),
        cylinder("Recycling aperture", 0.105, 0.025, (-0.21, -0.263, 0.94), mats["black"], vertices=24, rotation=(math.pi / 2, 0, 0)),
        box("Waste aperture", (0.22, 0.025, 0.10), (0.21, -0.263, 0.94), mats["black"], bevel=0.025),
        box("Recycling label", (0.19, 0.018, 0.13), (-0.21, -0.268, 0.68), mats["blue"], bevel=0.012),
        box("Waste label", (0.19, 0.018, 0.13), (0.21, -0.268, 0.68), mats["green"], bevel=0.012),
        box("Height datum", (0.02, 0.02, 0.01), (0, 0, 1.075), mats["steel"], bevel=0),
    ]
    return objects


def build_bike_rack(mats: dict) -> list:
    objects = []
    for index, x in enumerate((-0.62, 0.0, 0.62)):
        points = [
            (x - 0.28, 0, 0), (x - 0.28, 0, 0.55), (x - 0.17, 0, 0.76),
            (x, 0, 0.831), (x + 0.17, 0, 0.76), (x + 0.28, 0, 0.55), (x + 0.28, 0, 0),
        ]
        for segment, (start, end) in enumerate(zip(points, points[1:])):
            objects.append(tube_between(f"Rack {index} segment {segment}", start, end, 0.032, mats["galvanized"], vertices=12))
        for foot_x in (x - 0.28, x + 0.28):
            objects.append(cylinder(f"Rack foot {index} {foot_x}", 0.075, 0.018, (foot_x, 0, 0.009), mats["steel"], vertices=14))
    return objects


def build_drinking_fountain(mats: dict) -> list:
    objects = [
        cylinder("Pedestal", 0.23, 0.78, (0, 0, 0.39), mats["steel"], vertices=24),
        cylinder("Basin", 0.34, 0.11, (0, 0, 0.83), mats["galvanized"], vertices=32),
        cylinder("Basin inset", 0.27, 0.025, (0, 0, 0.89), mats["water"], vertices=32),
        cylinder("Drain", 0.035, 0.012, (0, 0, 0.906), mats["black"], vertices=18),
        tube_between("Bubbler neck", (0.17, 0, 0.90), (0.17, 0, 0.995), 0.025, mats["water"], vertices=14),
        cylinder("Bubbler head", 0.045, 0.08, (0.17, 0, 0.995), mats["water"], vertices=14, rotation=(math.pi / 2, 0, 0)),
        cylinder("Push button", 0.035, 0.04, (-0.235, 0, 0.75), mats["blue"], vertices=16, rotation=(0, math.pi / 2, 0)),
        # Lower side bowl makes the station usable from a seated position.
        cylinder("Accessible side bowl", 0.245, 0.10, (-0.34, 0, 0.69), mats["galvanized"], vertices=28),
        cylinder("Accessible basin inset", 0.18, 0.018, (-0.34, 0, 0.746), mats["water"], vertices=28),
        box("Height datum", (0.02, 0.02, 0.01), (0, 0, 1.035), mats["steel"], bevel=0),
    ]
    return objects


def join_by_material(objects: list, asset_name: str) -> list:
    groups: dict[str, list] = {}
    for obj in objects:
        material_name = obj.data.materials[0].name if obj.data.materials else "Unassigned"
        groups.setdefault(material_name, []).append(obj)
    joined = []
    for material_name, group in groups.items():
        bpy.ops.object.select_all(action="DESELECT")
        for obj in group:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = group[0]
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        bpy.ops.object.join()
        merged = bpy.context.object
        merged.name = f"{asset_name}_{material_name.replace(' ', '_')}"
        joined.append(merged)
    return joined


def asset_metrics(objects: list) -> tuple[Vector, int]:
    minimum = Vector((math.inf, math.inf, math.inf))
    maximum = Vector((-math.inf, -math.inf, -math.inf))
    triangles = 0
    for obj in objects:
        for corner in obj.bound_box:
            world = obj.matrix_world @ Vector(corner)
            minimum.x = min(minimum.x, world.x)
            minimum.y = min(minimum.y, world.y)
            minimum.z = min(minimum.z, world.z)
            maximum.x = max(maximum.x, world.x)
            maximum.y = max(maximum.y, world.y)
            maximum.z = max(maximum.z, world.z)
        obj.data.calc_loop_triangles()
        triangles += len(obj.data.loop_triangles)
    return maximum - minimum, triangles


def export_glb(path: Path, objects: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
        export_cameras=False,
        export_lights=False,
        export_extras=True,
    )


def import_asset(path: Path, name: str, location, yaw=0.0):
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
    return root


def look_at(obj, target=(0, 0, 0)):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def render_preview(preview_dir: Path, paths: dict[str, Path], *, pilot: bool) -> None:
    reset_scene()
    mats = materials()
    box("Catalogue floor", (18, 11, 0.08), (0, 0, -0.05), material("Warm concrete", (0.34, 0.33, 0.30, 1), roughness=0.88), bevel=0)
    layout = [
        ("basketball_hoop_regulation", (-4.5, 1.6, 0), math.radians(-25)),
        ("picnic_table_accessible", (1.0, 2.0, 0), math.radians(18)),
    ]
    if not pilot:
        layout.extend([
            ("dual_stream_bin", (5.0, 1.8, 0), math.radians(-18)),
            ("bike_rack_three_stall", (-1.6, -2.1, 0), math.radians(12)),
            ("drinking_fountain_accessible", (3.2, -2.2, 0), math.radians(-25)),
        ])
    for key, location, yaw in layout:
        import_asset(paths[key], key, location, yaw)
    for location, energy, size in [((-7, -8, 13), 1250, 7), ((8, 5, 10), 850, 6)]:
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.data.energy = energy
        light.data.shape = "DISK"
        light.data.size = size
        look_at(light, (0, 0, 1.5))
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 10))
    bpy.context.object.rotation_euler = (math.radians(25), math.radians(-22), math.radians(32))
    bpy.context.object.data.energy = 2.0
    bpy.ops.object.camera_add(location=(14, -16, 11))
    camera = bpy.context.object
    camera.data.lens = 58
    look_at(camera, (0, 0, 1.2))
    scene = bpy.context.scene
    scene.camera = camera
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.055, 0.072, 0.085, 1)
    background.inputs["Strength"].default_value = 0.42
    preview_dir.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(preview_dir / ("pilot-hoop-table.png" if pilot else "shared-park-equipment-catalogue.png"))
    bpy.ops.render.render(write_still=True)
    camera.location = (-14, -15, 8)
    look_at(camera, (0, 0, 1.15))
    scene.render.filepath = str(preview_dir / ("pilot-hoop-table-reverse.png" if pilot else "shared-park-equipment-reverse.png"))
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(preview_dir / ("pilot.blend" if pilot else "catalogue.blend")))


def main() -> None:
    args = parse_args()
    spec = json.loads(args.spec.resolve().read_text(encoding="utf-8"))
    definitions = {asset["id"]: asset for asset in spec["assets"]}
    builders = {
        "basketball_hoop_regulation": build_basketball_hoop,
        "picnic_table_accessible": build_picnic_table,
        "dual_stream_bin": build_dual_stream_bin,
        "bike_rack_three_stall": build_bike_rack,
        "drinking_fountain_accessible": build_drinking_fountain,
    }
    selected = list(builders)[:2] if args.pilot else list(builders)
    reset_scene()
    mats = materials()
    paths: dict[str, Path] = {}
    report = {"schemaVersion": 1, "kitId": spec["kitId"], "assets": []}
    for key in selected:
        authored = builders[key](mats)
        objects = join_by_material(authored, key)
        dimensions, triangles = asset_metrics(objects)
        expected_height = definitions[key]["heightM"]
        if not math.isclose(dimensions.z, expected_height, abs_tol=0.012):
            raise RuntimeError(f"{key} height {dimensions.z:.4f} m != {expected_height:.4f} m")
        path = args.output_dir.resolve() / definitions[key]["filename"]
        export_glb(path, objects)
        paths[key] = path
        report["assets"].append({
            "id": key,
            "filename": path.name,
            "dimensionsM": [round(dimensions.x, 3), round(dimensions.y, 3), round(dimensions.z, 3)],
            "triangles": triangles,
            "bytes": path.stat().st_size,
        })
        for obj in objects:
            bpy.data.objects.remove(obj, do_unlink=True)
    args.preview_dir.resolve().mkdir(parents=True, exist_ok=True)
    report_path = args.preview_dir.resolve() / ("pilot-report.json" if args.pilot else "kit-report.json")
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    render_preview(args.preview_dir.resolve(), paths, pilot=args.pilot)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
