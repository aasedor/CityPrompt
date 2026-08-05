"""Render an archetype-matched urban basketball scene from LEGO ground + GLBs.

The scene remains procedural and modular. Horizontal surfaces, markings and
context are generated here; the standing basketball equipment is imported from
the same metric GLBs used by the first pilot.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from render_adaptive_park_shapes import cube, reset_scene, solid_material  # noqa: E402


COURT_TOP_Z = 0.14
COURT_CENTER = (0.0, 0.0)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(argv)


def material(name: str, color, roughness=0.75, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    return mat


def noise_material(name: str, dark, light, *, scale: float, roughness: float, bump_strength: float):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Roughness"].default_value = roughness
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = 7.0
    noise.inputs["Roughness"].default_value = 0.72
    coords = nodes.new("ShaderNodeTexCoord")
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = dark
    ramp.color_ramp.elements[1].color = light
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = bump_strength
    bump.inputs["Distance"].default_value = 0.09
    links.new(coords.outputs["Generated"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], shader.inputs["Base Color"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], shader.inputs["Normal"])
    links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    return mat


def brick_material(name: str, primary, secondary):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Roughness"].default_value = 0.78
    brick = nodes.new("ShaderNodeTexBrick")
    brick.inputs["Color1"].default_value = primary
    brick.inputs["Color2"].default_value = secondary
    brick.inputs["Mortar"].default_value = (0.24, 0.22, 0.19, 1.0)
    brick.inputs["Scale"].default_value = 32.0
    brick.inputs["Mortar Size"].default_value = 0.012
    brick.inputs["Mortar Smooth"].default_value = 0.02
    coords = nodes.new("ShaderNodeTexCoord")
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.28
    bump.inputs["Distance"].default_value = 0.06
    links.new(coords.outputs["Generated"], brick.inputs["Vector"])
    links.new(brick.outputs["Color"], shader.inputs["Base Color"])
    links.new(brick.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], shader.inputs["Normal"])
    links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    return mat


def image_pbr_material(name: str, directory: Path, repeat: float, *, roughness=0.82):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Roughness"].default_value = roughness
    coords = nodes.new("ShaderNodeTexCoord")
    scale = nodes.new("ShaderNodeVectorMath")
    scale.operation = "MULTIPLY"
    scale.inputs[1].default_value = (repeat, repeat, repeat)
    albedo = nodes.new("ShaderNodeTexImage")
    albedo.image = bpy.data.images.load(str(directory / "albedo.jpg"), check_existing=True)
    albedo.image.colorspace_settings.name = "sRGB"
    albedo.extension = "REPEAT"
    rough = nodes.new("ShaderNodeTexImage")
    rough.image = bpy.data.images.load(str(directory / "roughness.jpg"), check_existing=True)
    rough.image.colorspace_settings.name = "Non-Color"
    rough.extension = "REPEAT"
    normal_tex = nodes.new("ShaderNodeTexImage")
    normal_tex.image = bpy.data.images.load(str(directory / "normal.png"), check_existing=True)
    normal_tex.image.colorspace_settings.name = "Non-Color"
    normal_tex.extension = "REPEAT"
    normal = nodes.new("ShaderNodeNormalMap")
    normal.inputs["Strength"].default_value = 0.42
    links.new(coords.outputs["UV"], scale.inputs[0])
    for texture in (albedo, rough, normal_tex):
        links.new(scale.outputs["Vector"], texture.inputs["Vector"])
    links.new(albedo.outputs["Color"], shader.inputs["Base Color"])
    links.new(rough.outputs["Color"], shader.inputs["Roughness"])
    links.new(normal_tex.outputs["Color"], normal.inputs["Color"])
    links.new(normal.outputs["Normal"], shader.inputs["Normal"])
    links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    return mat


def curve_line(name: str, points, bevel: float, mat, *, cyclic=False):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = bevel
    curve.bevel_resolution = 2
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, coordinate in zip(spline.points, points):
        point.co = (*coordinate, 1.0)
    spline.use_cyclic_u = cyclic
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def arc_line(name: str, center, radius: float, start: float, end: float, mat, segments=48):
    cx, cy, cz = center
    points = [
        (cx + math.cos(start + (end - start) * i / segments) * radius,
         cy + math.sin(start + (end - start) * i / segments) * radius,
         cz)
        for i in range(segments + 1)
    ]
    return curve_line(name, points, 0.035, mat)


def cylinder_between(name: str, start, end, radius: float, mat, vertices=12):
    a, b = Vector(start), Vector(end)
    direction = b - a
    midpoint = (a + b) * 0.5
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=direction.length, location=midpoint)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    obj.data.materials.append(mat)
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
    root.scale = (1.0, 1.0, 1.0)
    return root


def add_court(marking, asphalt) -> None:
    cube("Concrete court surround", (0, 0, 0.02), (43.0, 30.0, 0.18), bpy.data.materials["Warm concrete"], 0.03)
    cube("Court asphalt envelope", (0, 0, COURT_TOP_Z - 0.045), (32.0, 19.0, 0.11), asphalt, 0.018)
    z = COURT_TOP_Z + 0.025
    # Playing rectangle and centre line.
    curve_line("Playing boundary", [(-14, -7.5, z), (14, -7.5, z), (14, 7.5, z), (-14, 7.5, z)], 0.035, marking, cyclic=True)
    curve_line("Centre line", [(0, -7.5, z), (0, 7.5, z)], 0.035, marking)
    arc_line("Centre circle", (0, 0, z), 1.8, 0, math.tau, marking)
    # Keys, free-throw circles and three-point arcs at both ends.
    for direction in (-1, 1):
        baseline_x = direction * 14.0
        free_x = direction * 9.1
        inside_x = direction * 9.1
        curve_line(
            f"Key {direction}",
            [(baseline_x, -2.45, z), (inside_x, -2.45, z), (inside_x, 2.45, z), (baseline_x, 2.45, z)],
            0.035,
            marking,
        )
        if direction < 0:
            arc_line(f"Free throw {direction}", (free_x, 0, z), 1.8, -math.pi / 2, math.pi / 2, marking)
            arc_line(f"Three point {direction}", (-12.38, 0, z), 6.75, -1.18, 1.18, marking)
        else:
            arc_line(f"Free throw {direction}", (free_x, 0, z), 1.8, math.pi / 2, math.pi * 1.5, marking)
            arc_line(f"Three point {direction}", (12.38, 0, z), 6.75, math.pi - 1.18, math.pi + 1.18, marking)
        curve_line(f"Three straight A {direction}", [(baseline_x, -6.6, z), (direction * 12.7, -6.6, z)], 0.035, marking)
        curve_line(f"Three straight B {direction}", [(baseline_x, 6.6, z), (direction * 12.7, 6.6, z)], 0.035, marking)
    # Restrained dark crack lines—the surface owns these, never the GLBs.
    crack = bpy.data.materials["Asphalt crack"]
    cracks = [
        [(-10.8, -6.2, z + 0.002), (-9.4, -5.3, z + 0.002), (-8.6, -5.7, z + 0.002), (-7.3, -4.8, z + 0.002)],
        [(4.0, 6.2, z + 0.002), (5.1, 5.4, z + 0.002), (6.0, 5.7, z + 0.002), (7.2, 4.7, z + 0.002)],
        [(9.2, -5.8, z + 0.002), (8.5, -4.8, z + 0.002), (9.0, -3.7, z + 0.002)],
    ]
    for index, points in enumerate(cracks):
        curve_line(f"Asphalt crack {index}", points, 0.016, crack)


def add_depth_assets(repo_root: Path) -> None:
    root = repo_root / "frontend/public/park-kits"
    paths = {
        "hoop": root / "basketball-hoop.glb",
        "fence": root / "chainlink-fence-4m.glb",
        "gate": root / "chainlink-gate-3m.glb",
        "floodlight": root / "basketball-floodlight.glb",
    }
    z = COURT_TOP_Z + 0.035
    import_asset(paths["hoop"], "Hoop west", (-15.2, 0, z), 0)
    import_asset(paths["hoop"], "Hoop east", (15.2, 0, z), math.pi)
    for side_y in (-9.5, 9.5):
        for x in (-14, -10, -6, -2, 2, 6, 10, 14):
            import_asset(paths["fence"], f"Fence Y{side_y} X{x}", (x, side_y, z), 0)
    for side_x in (-16, 16):
        for y, kind in [(-7.5, "fence"), (-3.5, "fence"), (0, "gate"), (3.5, "fence"), (7.5, "fence")]:
            import_asset(paths[kind], f"Fence X{side_x} Y{y}", (side_x, y, z), math.pi / 2)
    for x, y in ((-15.5, -9), (-15.5, 9), (15.5, -9), (15.5, 9)):
        import_asset(paths["floodlight"], f"Floodlight {x} {y}", (x, y, z), math.atan2(-y, -x))


def add_bench(name: str, location, yaw: float, timber, steel) -> None:
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    for index in range(5):
        slat = cube(f"{name} seat slat {index}", (0, -0.34 + index * 0.17, 0.56), (2.4, 0.12, 0.09), timber, 0.025)
        slat.parent = root
    for index in range(5):
        slat = cube(f"{name} back slat {index}", (0, 0.38, 0.72 + index * 0.15), (2.4, 0.08, 0.10), timber, 0.02)
        slat.parent = root
    for x in (-0.9, 0.9):
        for y in (-0.24, 0.25):
            leg = cube(f"{name} leg {x} {y}", (x, y, 0.28), (0.09, 0.09, 0.55), steel, 0.015)
            leg.parent = root
    root.location = location
    root.rotation_euler[2] = yaw


def add_tree(name: str, location, scale: float, trunk, foliage_a, foliage_b) -> None:
    x, y = location
    bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.22 * scale, depth=3.2 * scale, location=(x, y, 1.6 * scale))
    bpy.context.object.name = f"{name} trunk"
    bpy.context.object.data.materials.append(trunk)
    clusters = [(-0.7, 0.0, 3.7, 1.25), (0.55, 0.25, 3.9, 1.35), (0, -0.55, 4.2, 1.45), (0.1, 0.55, 4.55, 1.15)]
    for index, (dx, dy, z, radius) in enumerate(clusters):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=radius * scale, location=(x + dx * scale, y + dy * scale, z * scale))
        leaf = bpy.context.object
        leaf.name = f"{name} foliage {index}"
        leaf.scale.z = 0.82
        leaf.data.materials.append(foliage_a if index % 2 == 0 else foliage_b)


def add_person(name: str, location, yaw: float, shirt, shorts, skin, *, pose="stand", scale=1.0) -> None:
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    # Local parts are parented before the root is positioned/rotated.
    def part_cylinder(part_name, a, b, radius, mat):
        obj = cylinder_between(f"{name} {part_name}", a, b, radius, mat, 12)
        obj.parent = root
        return obj
    torso = cube(f"{name} torso", (0, 0, 1.25), (0.42, 0.26, 0.68), shirt, 0.11)
    torso.parent = root
    hips = cube(f"{name} shorts", (0, 0, 0.88), (0.38, 0.28, 0.28), shorts, 0.07)
    hips.parent = root
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=0.15, location=(0, 0, 1.73))
    head = bpy.context.object
    head.name = f"{name} head"
    head.data.materials.append(skin)
    head.parent = root
    if pose == "shoot":
        arms = [((-0.19, 0, 1.48), (-0.08, -0.16, 1.82)), ((0.19, 0, 1.48), (0.08, -0.16, 1.86))]
        legs = [((-0.12, 0, 0.83), (-0.18, 0.02, 0.08)), ((0.12, 0, 0.83), (0.18, -0.02, 0.08))]
    elif pose == "defend":
        arms = [((-0.19, 0, 1.46), (-0.72, -0.05, 1.42)), ((0.19, 0, 1.46), (0.72, -0.05, 1.42))]
        legs = [((-0.12, 0, 0.83), (-0.34, 0.04, 0.08)), ((0.12, 0, 0.83), (0.34, -0.04, 0.08))]
    else:
        arms = [((-0.19, 0, 1.46), (-0.24, 0, 0.98)), ((0.19, 0, 1.46), (0.24, 0, 0.98))]
        legs = [((-0.12, 0, 0.83), (-0.15, 0, 0.08)), ((0.12, 0, 0.83), (0.15, 0, 0.08))]
    for index, (a, b) in enumerate(arms):
        part_cylinder(f"arm {index}", a, b, 0.065, skin)
    for index, (a, b) in enumerate(legs):
        part_cylinder(f"leg {index}", a, b, 0.078, skin)
    root.location = (*location, COURT_TOP_Z + 0.04)
    root.rotation_euler[2] = yaw
    root.scale = (scale, scale, scale)


def add_ball(location, orange, seam) -> None:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=20, radius=0.12, location=location)
    ball = bpy.context.object
    ball.name = "Basketball"
    ball.data.materials.append(orange)
    for rotation in ((0, 0, 0), (math.pi / 2, 0, 0), (0, math.pi / 2, 0)):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.121, minor_radius=0.006, major_segments=32, minor_segments=6, location=location, rotation=rotation)
        bpy.context.object.data.materials.append(seam)


def add_car(name: str, location, yaw: float, body, glass, tire) -> None:
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    for obj in (
        cube(f"{name} body", (0, 0, 0.55), (4.1, 1.8, 0.7), body, 0.24),
        cube(f"{name} cabin", (-0.15, 0, 1.08), (2.25, 1.58, 0.65), glass, 0.18),
    ):
        obj.parent = root
    for x in (-1.35, 1.25):
        for y in (-0.86, 0.86):
            bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.34, depth=0.18, location=(x, y, 0.35), rotation=(math.pi / 2, 0, 0))
            wheel = bpy.context.object
            wheel.data.materials.append(tire)
            wheel.parent = root
    root.location = location
    root.rotation_euler[2] = yaw


def add_building(name: str, location, dimensions, floors: int, facade, glass, trim, *, windows_x=5, windows_y=3) -> None:
    x, y, z = location
    width, depth, height = dimensions
    cube(name, (x, y, z + height / 2), dimensions, facade, 0.08)
    cube(f"{name} parapet", (x, y, z + height + 0.35), (width + 0.15, depth + 0.15, 0.7), trim, 0.04)
    floor_h = height / floors
    # Windows on long north/south faces.
    for floor in range(floors):
        wz = z + floor_h * (floor + 0.57)
        for index in range(windows_x):
            wx = x - width * 0.42 + index * (width * 0.84 / max(1, windows_x - 1))
            for side in (-1, 1):
                cube(f"{name} window NS {floor} {index} {side}", (wx, y + side * (depth / 2 + 0.025), wz), (1.15, 0.05, 1.55), glass, 0.025)
                cube(f"{name} sill NS {floor} {index} {side}", (wx, y + side * (depth / 2 + 0.055), wz - 0.86), (1.35, 0.10, 0.11), trim, 0.015)
    # Windows on end faces.
    for floor in range(floors):
        wz = z + floor_h * (floor + 0.57)
        for index in range(windows_y):
            wy = y - depth * 0.34 + index * (depth * 0.68 / max(1, windows_y - 1))
            for side in (-1, 1):
                cube(f"{name} window EW {floor} {index} {side}", (x + side * (width / 2 + 0.025), wy, wz), (0.05, 1.1, 1.55), glass, 0.025)


def add_context(mats: dict) -> None:
    # Sidewalk and street establish the urban-neighbourhood context seen in all references.
    cube("Street asphalt", (0, -24.5, -0.06), (92, 13.0, 0.12), mats["road"], 0.03)
    cube("Street north sidewalk", (0, -16.7, 0.01), (92, 3.2, 0.16), mats["concrete"], 0.03)
    curve_line("Street centre dash", [(-45, -24.5, 0.02), (45, -24.5, 0.02)], 0.045, mats["street_line"])

    add_building("Court-side brick building", (2, 20.5, 0), (35, 10, 25), 7, mats["brick"], mats["glass"], mats["stone"], windows_x=8, windows_y=3)
    add_building("Far brick school", (30, 4, 0), (11, 22, 17), 5, mats["brick_dark"], mats["glass"], mats["stone"], windows_x=3, windows_y=5)
    add_building("West walkup", (-31, 4, 0), (11, 21, 15), 4, mats["brick_light"], mats["glass"], mats["stone"], windows_x=3, windows_y=4)
    for index, (x, y, width, depth, height, facade) in enumerate((
        (-29, -35, 16, 10, 18, mats["brick_dark"]),
        (-10, -36, 18, 11, 24, mats["brick"]),
        (12, -37, 20, 12, 21, mats["stone"]),
        (34, -35, 15, 10, 27, mats["brick_light"]),
        (45, 18, 13, 18, 31, mats["stone"]),
    )):
        add_building(f"Background building {index}", (x, y, 0), (width, depth, height), max(4, round(height / 3.3)), facade, mats["glass"], mats["stone"], windows_x=4, windows_y=3)

    for index, point in enumerate(((-20, -14.7), (-10, -14.7), (2, -14.7), (16, -14.7), (27, -14.7), (-23, 13), (22, 13))):
        add_tree(f"Street tree {index}", point, 1.0 + (index % 3) * 0.08, mats["trunk"], mats["foliage"], mats["foliage_light"])
    add_bench("Bench south west", (-8, -11.4, COURT_TOP_Z), 0, mats["timber"], mats["steel"])
    add_bench("Bench north west", (-7, 11.4, COURT_TOP_Z), math.pi, mats["timber"], mats["steel"])
    add_car("Parked car one", (-18, -23.2, 0), 0, mats["car_blue"], mats["glass"], mats["tire"])
    add_car("Parked car two", (6, -25.7, 0), math.pi, mats["car_silver"], mats["glass"], mats["tire"])


def add_people(mats: dict) -> None:
    add_person("Shooter", (-3.0, -0.5), 0.1, mats["shirt_blue"], mats["short_blue"], mats["skin_medium"], pose="shoot", scale=1.05)
    add_person("Defender west", (0.2, -1.0), -0.25, mats["shirt_black"], mats["short_grey"], mats["skin_light"], pose="defend")
    add_person("Defender east", (1.5, 1.0), 0.35, mats["shirt_white"], mats["short_black"], mats["skin_dark"], pose="defend", scale=1.03)
    add_person("Waiting player", (-5.0, 3.4), -0.4, mats["shirt_rust"], mats["short_black"], mats["skin_medium"], pose="stand")
    add_ball((-3.05, -0.62, 2.18), mats["ball"], mats["ball_seam"])


def build_materials(repo_root: Path) -> dict:
    texture_root = repo_root / "tools/archetype_compiler/textures"
    mats = {
        "court": noise_material("Court asphalt", (0.025, 0.028, 0.03, 1), (0.085, 0.075, 0.062, 1), scale=1.7, roughness=0.91, bump_strength=0.38),
        "road": noise_material("Road asphalt", (0.018, 0.022, 0.026, 1), (0.055, 0.06, 0.065, 1), scale=1.2, roughness=0.94, bump_strength=0.45),
        "concrete": image_pbr_material("Warm concrete", texture_root / "concrete", 4.0, roughness=0.86),
        "brick": image_pbr_material("Warm red brick", texture_root / "red_brick", 5.0, roughness=0.80),
        "brick_dark": image_pbr_material("Dark red brick", texture_root / "red_brick", 6.0, roughness=0.84),
        "brick_light": image_pbr_material("Buff brick", texture_root / "buff_brick", 5.0, roughness=0.80),
        "glass": material("Window glass", (0.055, 0.075, 0.08, 1), 0.2, 0.15),
        "stone": material("Limestone trim", (0.52, 0.48, 0.40, 1), 0.78),
        "steel": material("Bench steel", (0.10, 0.11, 0.105, 1), 0.36, 0.65),
        "timber": material("Bench timber", (0.34, 0.16, 0.065, 1), 0.68),
        "trunk": material("Tree bark", (0.17, 0.075, 0.03, 1), 0.95),
        "foliage": material("Foliage", (0.10, 0.25, 0.055, 1), 0.92),
        "foliage_light": material("Sunlit foliage", (0.23, 0.39, 0.10, 1), 0.92),
        "street_line": material("Street line", (0.62, 0.59, 0.49, 1), 0.78),
        "car_blue": material("Car blue", (0.035, 0.085, 0.12, 1), 0.28, 0.55),
        "car_silver": material("Car silver", (0.28, 0.30, 0.31, 1), 0.25, 0.72),
        "tire": material("Tire", (0.012, 0.014, 0.015, 1), 0.92),
        "shirt_blue": material("Blue jersey", (0.02, 0.12, 0.52, 1), 0.72),
        "short_blue": material("Blue shorts", (0.02, 0.08, 0.30, 1), 0.76),
        "shirt_black": material("Black shirt", (0.025, 0.027, 0.03, 1), 0.75),
        "short_black": material("Black shorts", (0.018, 0.02, 0.022, 1), 0.75),
        "short_grey": material("Grey shorts", (0.28, 0.29, 0.28, 1), 0.78),
        "shirt_white": material("White shirt", (0.72, 0.70, 0.64, 1), 0.76),
        "shirt_rust": material("Rust shirt", (0.40, 0.08, 0.035, 1), 0.75),
        "skin_light": material("Light skin", (0.58, 0.32, 0.20, 1), 0.72),
        "skin_medium": material("Medium skin", (0.36, 0.16, 0.075, 1), 0.72),
        "skin_dark": material("Dark skin", (0.15, 0.06, 0.025, 1), 0.72),
        "ball": material("Basketball orange", (0.72, 0.16, 0.025, 1), 0.62),
        "ball_seam": material("Basketball seam", (0.025, 0.012, 0.008, 1), 0.82),
    }
    mats["marking"] = material("Court marking", (0.86, 0.84, 0.76, 1), 0.72)
    mats["crack"] = material("Asphalt crack", (0.006, 0.007, 0.008, 1), 0.96)
    # Helpers look these materials up by exact datablock name.
    mats["concrete"].name = "Warm concrete"
    mats["court"].name = "Court asphalt"
    mats["crack"].name = "Asphalt crack"
    return mats


def setup_scene(repo_root: Path) -> None:
    reset_scene()
    mats = build_materials(repo_root)
    add_court(mats["marking"], mats["court"])
    add_depth_assets(repo_root)
    add_context(mats)


def configure_render() -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.45
    scene.world.use_nodes = True
    nodes = scene.world.node_tree.nodes
    links = scene.world.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputWorld")
    background = nodes.new("ShaderNodeBackground")
    background.inputs["Strength"].default_value = 0.18
    sky = nodes.new("ShaderNodeTexSky")
    sky.sky_type = "MULTIPLE_SCATTERING"
    sky.sun_elevation = math.radians(22)
    sky.sun_rotation = math.radians(222)
    sky.altitude = 0.15
    sky.air_density = 1.05
    links.new(sky.outputs["Color"], background.inputs["Color"])
    links.new(background.outputs["Background"], output.inputs["Surface"])
    bpy.ops.object.light_add(type="SUN", location=(-20, -30, 50))
    sun = bpy.context.object
    sun.name = "Warm afternoon sun"
    sun.data.energy = 3.2
    sun.data.angle = math.radians(4.5)
    sun.data.color = (1.0, 0.63, 0.36)
    sun.rotation_euler = (math.radians(36), math.radians(-18), math.radians(-48))
    bpy.ops.object.light_add(type="AREA", location=(-8, -6, 28))
    fill = bpy.context.object
    fill.data.energy = 420
    fill.data.shape = "DISK"
    fill.data.size = 18
    fill.data.color = (0.72, 0.83, 1.0)
    fill.rotation_euler = (Vector((0, 0, 1)) - fill.location).to_track_quat("-Z", "Y").to_euler()


def camera(name: str, location, target, lens: float):
    bpy.ops.object.camera_add(location=location)
    cam = bpy.context.object
    cam.name = name
    cam.data.lens = lens
    cam.data.sensor_width = 36
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam
    return cam


def render_views(repo_root: Path, output: Path) -> None:
    setup_scene(repo_root)
    configure_render()
    output.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    views = (
        ("generated_base.png", (-15.55, -3.0, 1.9), (7.0, 0.1, 1.4), 34),
        ("generated_angle_60.png", (-31.0, -3.0, 29.0), (1.0, 0.0, 1.0), 48),
        ("generated_angle_90.png", (0.0, 0.0, 67.0), (0.0, 0.0, 0.0), 52),
    )
    for filename, location, target, lens in views:
        cam = camera(filename, location, target, lens)
        if filename == "generated_angle_90.png":
            cam.rotation_euler[2] += math.pi / 2
        scene.render.filepath = str(output / filename)
        bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "archetype_matched_pilot_v2.blend"))
    print(f"rendered archetype-matched views to {output}")


def main() -> None:
    args = parse_args()
    render_views(args.repo_root.resolve(), args.output.resolve())


if __name__ == "__main__":
    main()
