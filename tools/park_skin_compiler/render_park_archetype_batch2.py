"""Build, export and render five reference-matched LEGO + depth park kits.

The park grammar owns the registered ground surface. Exported GLBs contain the
reusable identity-bearing equipment that sits on that surface. People and large
buildings are intentionally absent from every generated scene.
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
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from render_adaptive_park_shapes import cube, reset_scene  # noqa: E402
from render_archetype_matched_basketball_pilot import (  # noqa: E402
    add_bench,
    add_tree,
    camera,
    configure_render,
    curve_line,
    cylinder_between,
    image_pbr_material,
    material,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--kit-output", type=Path, required=True)
    parser.add_argument("--skin-root", type=Path)
    parser.add_argument("--archetype", default="all")
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(argv)


def tinted_skin(name: str, directory: Path, repeat: float, tint) -> object:
    mat = image_pbr_material(name, directory, repeat)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    shader = next(node for node in nodes if node.bl_idname == "ShaderNodeBsdfPrincipled")
    source_link = shader.inputs["Base Color"].links[0]
    source_socket = source_link.from_socket
    links.remove(source_link)
    mix = nodes.new("ShaderNodeMixRGB")
    mix.blend_type = "COLOR"
    mix.inputs[0].default_value = 0.76
    mix.inputs[2].default_value = (*tint, 1.0)
    links.new(source_socket, mix.inputs[1])
    links.new(mix.outputs[0], shader.inputs["Base Color"])
    return mat


def materials(skin_root: Path, slug: str) -> dict:
    skin = skin_root / slug / "adaptive-v1"
    paver = image_pbr_material(f"{slug} aggregate", skin / "paver", 3.0, roughness=0.90)
    asphalt = image_pbr_material(f"{slug} dark surface", skin / "asphalt", 3.5, roughness=0.91)
    lawn = image_pbr_material(f"{slug} lawn", skin / "lawn", 4.0, roughness=0.95)
    planting = image_pbr_material(f"{slug} planting", skin / "planting", 3.0, roughness=0.97)
    timber = image_pbr_material(f"{slug} timber", skin / "timber", 2.8, roughness=0.84)
    mats = {
        "concrete": paver,
        "dark_concrete": asphalt,
        "gravel": paver,
        "soil": asphalt,
        "grass": lawn,
        "turf": lawn,
        "rubber_blue": tinted_skin(f"{slug} rubber blue", skin / "safety", 3.0, (0.34, 0.70, 0.92)),
        "rubber_green": tinted_skin(f"{slug} rubber green", skin / "safety", 3.0, (0.48, 0.83, 0.48)),
        "rubber_orange": tinted_skin(f"{slug} rubber orange", skin / "safety", 3.0, (0.95, 0.52, 0.26)),
        "rubber_sand": tinted_skin(f"{slug} rubber sand", skin / "safety", 3.0, (0.88, 0.76, 0.50)),
        "timber": timber,
        "timber_light": timber,
        "steel": material("Galvanized steel", (0.34, 0.38, 0.39, 1), 0.32, 0.72),
        "green_steel": material("Play accent green", (0.18, 0.48, 0.10, 1), 0.48, 0.25),
        "blue_steel": material("Play accent blue", (0.035, 0.18, 0.48, 1), 0.48, 0.25),
        "yellow": material("Play accent yellow", (0.78, 0.50, 0.04, 1), 0.54),
        "rope": material("Rope", (0.12, 0.09, 0.055, 1), 0.93),
        "rock": paver,
        "water": material("Water", (0.22, 0.62, 0.80, 1), 0.12, 0.12),
        "glass": material("Greenhouse glass", (0.22, 0.42, 0.37, 1), 0.12, 0.08),
        "foliage": planting,
        "foliage_light": planting,
        "flower": material("Flowers", (0.75, 0.31, 0.08, 1), 0.86),
        "flower_alt": material("Flowers alternate", (0.58, 0.12, 0.42, 1), 0.86),
        "trunk": material("Tree trunk", (0.16, 0.075, 0.025, 1), 0.95),
        "court_blue": tinted_skin(f"{slug} competition blue", skin / "safety", 3.0, (0.11, 0.27, 0.48)),
        "court_green": tinted_skin(f"{slug} court surround", skin / "lawn", 3.0, (0.18, 0.38, 0.20)),
        "white": material("Court marking white", (0.92, 0.92, 0.88, 1), 0.72),
        "black_steel": material("Blackened steel", (0.045, 0.052, 0.050, 1), 0.45, 0.62),
        "hedge": tinted_skin(f"{slug} clipped hedge", skin / "planting", 2.5, (0.12, 0.30, 0.09)),
        "marble": tinted_skin(f"{slug} pale stone", skin / "paver", 2.5, (0.82, 0.79, 0.70)),
        "water_dark": material("Reflecting water", (0.045, 0.105, 0.095, 1), 0.06, 0.18),
        "sand": tinted_skin(f"{slug} play sand", skin / "paver", 2.8, (0.73, 0.59, 0.37)),
        "asphalt_black": tinted_skin(f"{slug} sealed black asphalt", skin / "asphalt", 3.2, (0.08, 0.09, 0.09)),
    }
    return mats


def root(name: str, location=(0, 0, 0), yaw=0.0):
    obj = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler[2] = yaw
    return obj


def attach(parent, objects):
    for obj in objects:
        obj.parent = parent
    return parent


def cylinder(name: str, location, radius: float, depth: float, mat, vertices=20, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    return obj


def sphere(name: str, location, radius: float, mat, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=radius, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(mat)
    return obj


def disc(name: str, location, radius: float, depth: float, mat, scale=(1, 1, 1)):
    obj = cylinder(name, location, radius, depth, mat, vertices=64)
    obj.scale = scale
    return obj


def sloped_box(name: str, start, end, width: float, thickness: float, mat):
    a, b = Vector(start), Vector(end)
    delta = b - a
    horizontal = math.hypot(delta.x, delta.y)
    obj = cube(name, (a + b) * 0.5, (delta.length, width, thickness), mat, min(0.12, thickness * 0.25))
    obj.rotation_euler[2] = math.atan2(delta.y, delta.x)
    obj.rotation_euler[1] = -math.atan2(delta.z, horizontal)
    return obj


def pyramid_roof(name: str, location, radius: float, depth: float, mat):
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=radius, radius2=0.18, depth=depth, location=location, rotation=(0, 0, math.pi / 4))
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    return obj


def descendants(obj):
    found = []
    pending = list(obj.children)
    while pending:
        child = pending.pop()
        found.append(child)
        pending.extend(child.children)
    return found


def export_root(asset_root, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    old_location = asset_root.location.copy()
    old_rotation = asset_root.rotation_euler.copy()
    asset_root.location = (0, 0, 0)
    asset_root.rotation_euler = (0, 0, 0)
    asset_root.select_set(True)
    for obj in descendants(asset_root):
        obj.select_set(True)
    bpy.context.view_layer.objects.active = asset_root
    bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB", use_selection=True)
    asset_root.location = old_location
    asset_root.rotation_euler = old_rotation


def add_boundary_planting(width: float, depth: float, mats: dict, tree_count=8) -> None:
    for index in range(tree_count):
        side = index % 4
        t = ((index // 4) + 1) / ((tree_count + 3) // 4 + 1)
        if side == 0:
            point = (-width / 2 + t * width, depth / 2 + 2.4)
        elif side == 1:
            point = (width / 2 + 2.4, -depth / 2 + t * depth)
        elif side == 2:
            point = (width / 2 - t * width, -depth / 2 - 2.4)
        else:
            point = (-width / 2 - 2.4, depth / 2 - t * depth)
        add_tree(f"Boundary tree {index}", point, 0.72 + (index % 3) * 0.08, mats["trunk"], mats["foliage"], mats["foliage_light"])


def fence_segment(name: str, location, yaw: float, length: float, mats: dict, height=1.25):
    r = root(name, location, yaw)
    parts = []
    for x in (-length / 2, length / 2):
        parts.append(cylinder(f"{name} post {x}", (x, 0, height / 2), 0.11, height, mats["timber"], 12))
    for z in (0.42, 0.92):
        parts.append(cylinder_between(f"{name} rail {z}", (-length / 2, 0, z), (length / 2, 0, z), 0.075, mats["timber"], 10))
    return attach(r, parts)


def fence_rectangle(width: float, depth: float, mats: dict, asset_roots: dict, asset_name="split-rail-fence.glb", segment=5.0):
    first = None
    index = 0
    for y in (-depth / 2, depth / 2):
        count = max(1, round(width / segment))
        actual = width / count
        for i in range(count):
            item = fence_segment(f"Fence {index}", (-width / 2 + actual * (i + 0.5), y, 0), 0, actual, mats)
            first = first or item
            index += 1
    for x in (-width / 2, width / 2):
        count = max(1, round(depth / segment))
        actual = depth / count
        for i in range(count):
            item = fence_segment(f"Fence {index}", (x, -depth / 2 + actual * (i + 0.5), 0), math.pi / 2, actual, mats)
            first = first or item
            index += 1
    asset_roots.setdefault(asset_name, first)


def fence_cell(name: str, center, width: float, depth: float, mats: dict) -> None:
    cx, cy = center
    fence_segment(f"{name} south", (cx, cy - depth / 2, 0.18), 0, width, mats)
    fence_segment(f"{name} north", (cx, cy + depth / 2, 0.18), 0, width, mats)
    fence_segment(f"{name} west", (cx - width / 2, cy, 0.18), math.pi / 2, depth, mats)
    fence_segment(f"{name} east", (cx + width / 2, cy, 0.18), math.pi / 2, depth, mats)


def shade_shelter(name: str, location, mats: dict, asset_roots: dict, asset_name="shade-shelter.glb"):
    r = root(name, location)
    parts = []
    for x in (-2.2, 2.2):
        for y in (-1.7, 1.7):
            parts.append(cylinder(f"{name} post", (x, y, 1.55), 0.13, 3.1, mats["timber"], 12))
    for i in range(10):
        parts.append(cylinder_between(f"{name} roof slat {i}", (-2.8, -2.0 + i * 0.44, 3.2), (2.8, -2.0 + i * 0.44, 3.2), 0.10, mats["timber"], 10))
    attach(r, parts)
    asset_roots.setdefault(asset_name, r)
    return r


def build_playground(mats: dict) -> tuple[tuple[float, float], dict]:
    width, depth = 50.0, 40.0
    assets = {}
    cube("Playground LEGO surface", (0, 0, 0), (width, depth, 0.18), mats["concrete"], 1.5)
    for i, (x, y, radius, mat_key) in enumerate(((-12, 8, 7, "rubber_blue"), (0, 4, 9, "rubber_green"), (12, -7, 7, "rubber_orange"), (-10, -10, 6, "rubber_sand"), (14, 9, 5, "rubber_blue"))):
        disc(f"Rubber colour field {i}", (x, y, 0.115), radius, 0.05, mats[mat_key], scale=(1.35, 0.8, 1))

    play = root("Accessible play structure", (0, 1, 0.16))
    parts = []
    for tx, ty in ((-4, 1), (3.5, 2.5)):
        parts.append(cube("Tower platform", (tx, ty, 1.35), (4.0, 4.0, 0.28), mats["timber_light"], 0.12))
        for px in (-1.65, 1.65):
            for py in (-1.65, 1.65):
                parts.append(cylinder("Tower post", (tx + px, ty + py, 1.8), 0.13, 3.6, mats["timber"], 12))
        parts.append(pyramid_roof("Tower roof", (tx, ty, 4.15), 3.0, 1.2, mats["timber_light"]))
    parts.extend([
        cube("Accessible bridge", (-0.3, 1.8, 1.45), (4.4, 2.1, 0.22), mats["timber_light"], 0.08),
        sloped_box("Accessible ramp", (-13, -6, 0.28), (-4, 0, 1.4), 2.8, 0.22, mats["timber_light"]),
        sloped_box("Wide slide", (4.5, 3.5, 1.4), (10.5, 8.5, 0.26), 1.65, 0.16, mats["blue_steel"]),
    ])
    for offset in (-1.25, 1.25):
        parts.append(cylinder_between("Ramp handrail", (-13, -6 + offset, 1.05), (-4, offset, 2.15), 0.055, mats["steel"], 12))
    attach(play, parts)
    assets["accessible-play-structure.glb"] = play

    swing = root("Accessible swing bay", (-15, 9, 0.15))
    parts = [cylinder_between("Swing beam", (-3.4, 0, 3.4), (3.4, 0, 3.4), 0.13, mats["timber"], 12)]
    for x in (-3.0, 3.0):
        parts.extend([
            cylinder_between("Swing A post", (x - 1.0, -1.5, 0), (x, 0, 3.4), 0.13, mats["timber"], 12),
            cylinder_between("Swing A post", (x + 1.0, 1.5, 0), (x, 0, 3.4), 0.13, mats["timber"], 12),
        ])
    for x in (-1.1, 1.1):
        parts.extend([
            cylinder_between("Swing chain", (x - 0.3, 0, 3.25), (x - 0.3, 0, 1.25), 0.025, mats["steel"], 8),
            cylinder_between("Swing chain", (x + 0.3, 0, 3.25), (x + 0.3, 0, 1.25), 0.025, mats["steel"], 8),
            cube("Inclusive swing seat", (x, 0, 1.15), (0.8, 0.65, 0.16), mats["green_steel"], 0.09),
        ])
    attach(swing, parts)
    assets["accessible-swing-bay.glb"] = swing

    spinner = root("Inclusive spinner", (14, -8, 0.15))
    parts = [disc("Spinner deck", (0, 0, 0.22), 2.6, 0.28, mats["steel"]), cylinder("Spinner mast", (0, 0, 0.95), 0.09, 1.55, mats["steel"], 16)]
    for angle in (0, math.pi / 2, math.pi, math.pi * 1.5):
        x, y = math.cos(angle) * 1.5, math.sin(angle) * 1.5
        parts.append(cube("Spinner seat", (x, y, 0.7), (1.1, 0.7, 0.18), mats["green_steel"], 0.18))
        parts.append(cylinder_between("Spinner rail", (x, y, 0.75), (x * 0.65, y * 0.65, 1.55), 0.055, mats["steel"], 12))
    attach(spinner, parts)
    assets["inclusive-spinner.glb"] = spinner

    panel = root("Sensory panel", (-14, -8, 0.15))
    parts = [cylinder("Panel post", (-1.3, 0, 1.1), 0.10, 2.2, mats["timber"], 12), cylinder("Panel post", (1.3, 0, 1.1), 0.10, 2.2, mats["timber"], 12), cube("Activity panel", (0, 0, 1.25), (2.5, 0.18, 1.5), mats["blue_steel"], 0.12)]
    for x in (-0.75, -0.25, 0.25, 0.75):
        parts.append(cylinder("Panel tactile disc", (x, -0.13, 1.3), 0.16, 0.08, mats["yellow"], 20, (math.pi / 2, 0, 0)))
    attach(panel, parts)
    assets["sensory-panel.glb"] = panel

    canopy = shade_shelter("Playground shade canopy", (14, 9, 0.15), mats, assets, "shade-canopy.glb")
    canopy.scale = (0.95, 0.75, 0.9)
    add_boundary_planting(width, depth, mats, 12)
    add_bench("Playground bench west", (-21, 0, 0.16), math.pi / 2, mats["timber_light"], mats["steel"])
    add_bench("Playground bench east", (21, 0, 0.16), -math.pi / 2, mats["timber_light"], mats["steel"])
    return (width, depth), assets


def make_bowl(name: str, location, mats: dict, assets: dict):
    """Create a real recessed bowl shell rather than a raised torus proxy."""
    r = root(name, location)
    segments = 72
    rings = (
        (7.0, 11.2, 0.16),
        (6.25, 10.35, -0.20),
        (5.15, 8.90, -1.12),
        (4.45, 7.65, -1.42),
    )
    vertices = []
    for rx, ry, z in rings:
        vertices.extend((math.cos(math.tau * i / segments) * rx, math.sin(math.tau * i / segments) * ry, z) for i in range(segments))
    vertices.append((0, 0, -1.42))
    faces = []
    for ring_index in range(len(rings) - 1):
        start = ring_index * segments
        next_start = (ring_index + 1) * segments
        for i in range(segments):
            j = (i + 1) % segments
            faces.append((start + i, start + j, next_start + j, next_start + i))
    centre = len(vertices) - 1
    last_start = (len(rings) - 1) * segments
    for i in range(segments):
        faces.append((last_start + i, last_start + (i + 1) % segments, centre))
    mesh = bpy.data.meshes.new(f"{name} shell mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    shell = bpy.data.objects.new(f"{name} recessed shell", mesh)
    bpy.context.scene.collection.objects.link(shell)
    shell.data.materials.append(mats["dark_concrete"])
    coping_points = [(math.cos(math.tau * i / segments) * 7.0, math.sin(math.tau * i / segments) * 11.2, 0.21) for i in range(segments)]
    coping = curve_line(f"{name} coping", coping_points, 0.075, mats["steel"], cyclic=True)
    attach(r, [shell, coping])
    assets.setdefault("skate-bowl-module.glb", r)
    return r


def ellipse_surround(name: str, location, rx: float, ry: float, half_width: float, half_depth: float, mat) -> None:
    """Fill the registered rectangular deck outside an elliptical bowl opening."""
    segments = 72
    vertices = []
    for i in range(segments):
        angle = math.tau * i / segments
        c, s = math.cos(angle), math.sin(angle)
        vertices.append((c * rx, s * ry, 0.12))
        tx = half_width / max(abs(c), 1e-6)
        ty = half_depth / max(abs(s), 1e-6)
        reach = min(tx, ty)
        vertices.append((c * reach, s * reach, 0.12))
    faces = []
    for i in range(segments):
        j = (i + 1) % segments
        faces.append((i * 2, j * 2, j * 2 + 1, i * 2 + 1))
    mesh = bpy.data.meshes.new(f"{name} mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    obj.data.materials.append(mat)


def build_skate(mats: dict) -> tuple[tuple[float, float], dict]:
    width, depth = 40.0, 30.0
    assets = {}
    # The LEGO slab is assembled around two registered bowl openings. The bowl
    # GLBs replace those openings instead of z-fighting with a duplicate plane.
    for name, location, dimensions in (
        ("North deck", (0, 13.5, 0), (40, 3, 0.22)),
        ("South deck", (0, -13.5, 0), (40, 3, 0.22)),
        ("West deck", (-18.5, 0, 0), (3, 24, 0.22)),
        ("East deck", (18.5, 0, 0), (3, 24, 0.22)),
        ("Central deck", (0, 0, 0), (7, 24, 0.22)),
    ):
        cube(name, location, dimensions, mats["concrete"], 0.35)
    for label, x in (("West", -10.25), ("East", 10.25)):
        ellipse_surround(f"{label} registered bowl deck", (x, 0, 0), 7.0, 11.2, 7.25, 12.0, mats["concrete"])
        make_bowl(f"{label} bowl module", (x, 0, 0.18), mats, assets)
    hubba = root("Stair and hubba", (0, 0, 0.18))
    parts = []
    for i in range(6):
        parts.append(cube("Stair tread", (0, -2.2 + i * 0.62, 0.12 + i * 0.18), (5.0, 0.75, 0.22 + i * 0.02), mats["concrete"], 0.04))
    parts.extend([cube("Hubba ledge", (-3.4, 0, 0.65), (1.0, 5.8, 1.15), mats["concrete"], 0.12), cube("Hubba ledge", (3.4, 0, 0.65), (1.0, 5.8, 1.15), mats["concrete"], 0.12)])
    attach(hubba, parts)
    assets["stair-hubba-module.glb"] = hubba
    rail = root("Skate rail", (0, -8, 0.18))
    attach(rail, [cylinder_between("Rail bar", (-3, 0, 0.75), (3, 0, 0.75), 0.055, mats["steel"], 12), cylinder_between("Rail foot", (-2.5, 0, 0), (-2.5, 0, 0.75), 0.055, mats["steel"], 12), cylinder_between("Rail foot", (2.5, 0, 0), (2.5, 0, 0.75), 0.055, mats["steel"], 12)])
    assets["skate-rail.glb"] = rail
    ledge = root("Skate ledge", (0, 9, 0.18))
    attach(ledge, [cube("Grind ledge", (0, 0, 0.45), (6.0, 1.0, 0.9), mats["concrete"], 0.08), cube("Ledge coping", (0, -0.48, 0.92), (6.0, 0.08, 0.08), mats["steel"], 0.02)])
    assets["skate-ledge.glb"] = ledge
    add_bench("Skate spectator bench", (0, 13.0, 0.18), math.pi, mats["timber_light"], mats["steel"])
    return (width, depth), assets


def build_dog(mats: dict) -> tuple[tuple[float, float], dict]:
    width, depth = 80.0, 50.0
    assets = {}
    cube("Dog park LEGO gravel", (0, 0, 0), (width, depth, 0.18), mats["gravel"], 3.0)
    for x, y, sx, sy in ((-24, 13, 18, 12), (0, 13, 18, 12), (24, 13, 18, 12), (-18, -13, 24, 14), (18, -13, 24, 14)):
        cube("Turf exercise pen", (x, y, 0.12), (sx, sy, 0.08), mats["turf"], 1.4)
        fence_cell(f"Exercise pen {x} {y}", (x, y), sx, sy, mats)
    fence_rectangle(72, 43, mats, assets, "timber-rail-fence.glb", 6)
    gate = root("Dog park double gate", (0, -21.5, 0))
    parts = [cylinder("Gate post", (-2.2, 0, 0.8), 0.12, 1.6, mats["timber"], 12), cylinder("Gate post", (2.2, 0, 0.8), 0.12, 1.6, mats["timber"], 12)]
    for x1, x2 in ((-2.1, -0.1), (0.1, 2.1)):
        for z in (0.38, 0.95, 1.45):
            parts.append(cylinder_between("Gate rail", (x1, 0, z), (x2, 0, z), 0.06, mats["timber"], 10))
    attach(gate, parts)
    assets["dog-park-gate.glb"] = gate
    for i, point in enumerate(((-25, 13, 0.18), (0, 13, 0.18), (25, 13, 0.18))):
        shade_shelter(f"Dog shade {i}", point, mats, assets)
    rocks = root("Boulder cluster", (-2, -2, 0.18))
    attach(rocks, [sphere("Boulder", (-2.4, 0, 0.65), 1.2, mats["rock"], (1.5, 1.0, 0.65)), sphere("Boulder", (0, 1.0, 0.55), 1.0, mats["rock"], (1.25, 0.9, 0.6)), sphere("Boulder", (2.2, -0.4, 0.75), 1.35, mats["rock"], (1.15, 0.85, 0.62))])
    assets["boulder-cluster.glb"] = rocks
    for x in (-33, -22, -11, 0, 11, 22, 33):
        sphere("Meadow shrub", (x, 23, 0.65), 1.0, mats["foliage_light"], (1.0, 1.0, 0.65))
        sphere("Meadow shrub", (x, -23, 0.65), 1.0, mats["foliage"], (1.0, 1.0, 0.65))
    for y in (-18, -9, 0, 9, 18):
        sphere("Wildflower edge", (-38, y, 0.7), 1.2, mats["flower"], (0.9, 1.5, 0.6))
        sphere("Wildflower edge", (38, y, 0.7), 1.2, mats["flower_alt"], (0.9, 1.5, 0.6))
    return (width, depth), assets


def build_splash(mats: dict) -> tuple[tuple[float, float], dict]:
    width, depth = 30.0, 25.0
    assets = {}
    disc("Splash LEGO surface", (0, 0, 0), 14.8, 0.20, mats["gravel"], (1, 0.84, 1))
    disc("Wet play zone", (0, 0, 0.12), 10.6, 0.06, mats["dark_concrete"], (1, 0.78, 1))
    tower = root("Timber water tower", (3, 1, 0.18))
    parts = []
    for x in (-2.0, 2.0):
        for y in (-1.8, 1.8):
            parts.append(cylinder("Tower post", (x, y, 2.2), 0.16, 4.4, mats["timber"], 12))
    parts.extend([cube("Water platform", (0, 0, 2.5), (4.5, 4.0, 0.25), mats["timber_light"], 0.08), sloped_box("Water chute", (0, -1.8, 2.5), (0, -6.8, 0.35), 2.0, 0.18, mats["timber_light"]), cylinder_between("Bucket support", (-2.5, 0, 5.8), (2.5, 0, 5.8), 0.15, mats["timber"], 12)])
    parts.extend([cylinder("Tipping bucket", (0.7, 0, 5.2), 1.0, 1.6, mats["timber_light"], 24, (0, math.radians(23), 0)), curve_line("Bucket water", [(0.8, -0.2, 4.6), (0.6, -0.3, 3.5), (0.1, -0.2, 2.7), (0, 0, 0.4)], 0.20, mats["water"])])
    attach(tower, parts)
    assets["timber-water-tower.glb"] = tower
    arch = root("Spray arch", (-6, -2, 0.18))
    arch_parts = [cylinder("Arch post", (-2, 0, 1.6), 0.12, 3.2, mats["timber"], 12), cylinder("Arch post", (2, 0, 1.6), 0.12, 3.2, mats["timber"], 12), cylinder_between("Arch beam", (-2, 0, 3.2), (2, 0, 3.2), 0.12, mats["timber"], 12), curve_line("Arch spray", [(-1.7, 0, 3.0), (-1, 0, 2.3), (0, 0, 1.9), (1, 0, 2.3), (1.7, 0, 3.0)], 0.08, mats["water"])]
    attach(arch, arch_parts)
    assets["spray-arch.glb"] = arch
    first_jet = None
    for i, (x, y) in enumerate(((-5, 4), (-3, 6), (0, -5), (5, -3), (7, 3))):
        jet = root(f"Ground jet {i}", (x, y, 0.18))
        attach(jet, [disc("Jet collar", (0, 0, 0.06), 0.32, 0.10, mats["steel"]), curve_line("Water jet", [(0, 0, 0.1), (0.1, 0, 1.4), (0, 0, 2.4)], 0.055, mats["water"])])
        first_jet = first_jet or jet
    assets["ground-jet.glb"] = first_jet
    fence_rectangle(27.5, 21.0, mats, assets, "split-rail-fence.glb", 4.5)
    for i, angle in enumerate(range(0, 360, 30)):
        rad = math.radians(angle)
        sphere(f"Splash border shrub {i}", (math.cos(rad) * 16, math.sin(rad) * 13.5, 0.55), 0.9, mats["foliage" if i % 2 else "foliage_light"], (1.1, 1.1, 0.7))
    add_bench("Splash bench", (12, -7, 0.18), math.radians(120), mats["timber_light"], mats["steel"])
    return (width, depth), assets


def raised_bed(name: str, location, mats: dict, assets: dict, yaw=0.0):
    r = root(name, location, yaw)
    parts = [cube("Bed timber box", (0, 0, 0.38), (4.2, 2.5, 0.75), mats["timber_light"], 0.08), cube("Bed soil", (0, 0, 0.78), (3.7, 2.0, 0.12), mats["soil"], 0.06)]
    for row in (-0.65, 0, 0.65):
        for x in (-1.45, -0.72, 0, 0.72, 1.45):
            parts.append(sphere("Crop", (x, row, 1.05), 0.32, mats["foliage" if (round(x * 10) + round(row * 10)) % 2 else "foliage_light"], (1, 1, 0.75)))
    attach(r, parts)
    assets.setdefault("raised-growing-bed.glb", r)
    return r


def greenhouse(name: str, location, mats: dict, assets: dict):
    r = root(name, location)
    parts = [cube("Greenhouse floor", (0, 0, 0.12), (7.0, 5.5, 0.20), mats["timber_light"], 0.05)]
    for x in (-3.4, 3.4):
        for y in (-2.65, 2.65):
            parts.append(cylinder("Greenhouse post", (x, y, 1.6), 0.07, 3.2, mats["steel"], 10))
    for y in (-2.65, 2.65):
        parts.append(cylinder_between("Greenhouse eave", (-3.4, y, 3.2), (3.4, y, 3.2), 0.06, mats["steel"], 10))
        parts.append(cylinder_between("Greenhouse roof", (-3.4, y, 3.2), (0, y, 4.6), 0.06, mats["steel"], 10))
        parts.append(cylinder_between("Greenhouse roof", (0, y, 4.6), (3.4, y, 3.2), 0.06, mats["steel"], 10))
    parts.extend([
        cube("Greenhouse pane front", (0, -2.7, 1.8), (6.6, 0.04, 2.8), mats["glass"], 0.02),
        cube("Greenhouse pane rear", (0, 2.7, 1.8), (6.6, 0.04, 2.8), mats["glass"], 0.02),
        cube("Greenhouse pane left", (-3.45, 0, 1.8), (0.04, 5.1, 2.8), mats["glass"], 0.02),
        cube("Greenhouse pane right", (3.45, 0, 1.8), (0.04, 5.1, 2.8), mats["glass"], 0.02),
        sloped_box("Greenhouse roof left", (-3.4, 0, 3.2), (0, 0, 4.6), 5.2, 0.06, mats["glass"]),
        sloped_box("Greenhouse roof right", (0, 0, 4.6), (3.4, 0, 3.2), 5.2, 0.06, mats["glass"]),
    ])
    attach(r, parts)
    assets["garden-greenhouse.glb"] = r
    return r


def build_garden(mats: dict) -> tuple[tuple[float, float], dict]:
    width, depth = 50.0, 50.0
    assets = {}
    cube("Garden LEGO gravel", (0, 0, 0), (width, depth, 0.18), mats["gravel"], 1.0)
    for row, y in enumerate((-15, -7.5, 0, 7.5, 15)):
        for col, x in enumerate((-15, -7.5, 0, 7.5)):
            if row == 4 and col >= 2:
                continue
            raised_bed(f"Raised bed {row}-{col}", (x, y, 0.18), mats, assets, math.pi / 2 if row == 0 else 0)
    greenhouse("Garden greenhouse", (15.5, 15, 0.18), mats, assets)
    trellis = root("Garden trellis", (15, 0, 0.18))
    trellis_parts = [cylinder("Trellis post", (-2.5, 0, 1.4), 0.09, 2.8, mats["timber"], 10), cylinder("Trellis post", (2.5, 0, 1.4), 0.09, 2.8, mats["timber"], 10), cylinder_between("Trellis top", (-2.5, 0, 2.8), (2.5, 0, 2.8), 0.08, mats["timber"], 10)]
    for x in (-1.7, -0.85, 0, 0.85, 1.7):
        trellis_parts.append(cylinder_between("Trellis string", (x, 0, 0.25), (x, 0, 2.75), 0.025, mats["rope"], 8))
    attach(trellis, trellis_parts)
    assets["garden-trellis.glb"] = trellis
    compost = root("Compost bins", (18, -15, 0.18))
    attach(compost, [cube("Compost bin", (-2.0, 0, 0.65), (3.0, 2.4, 1.3), mats["timber"], 0.06), cube("Compost bin", (1.4, 0, 0.65), (3.0, 2.4, 1.3), mats["timber"], 0.06), cube("Compost fill", (-2.0, 0, 1.32), (2.7, 2.1, 0.12), mats["soil"], 0.04)])
    assets["compost-bins.glb"] = compost
    fence_rectangle(48, 48, mats, assets, "split-rail-fence.glb", 6)
    for i, x in enumerate((-20, -10, 0, 10, 20)):
        sphere(f"Flower border north {i}", (x, 22.5, 0.65), 1.1, mats["flower" if i % 2 else "flower_alt"], (1.5, 0.8, 0.55))
        sphere(f"Flower border south {i}", (x, -22.5, 0.65), 1.1, mats["flower_alt" if i % 2 else "flower"], (1.5, 0.8, 0.55))
    add_bench("Garden bench", (-21, 0, 0.18), math.pi / 2, mats["timber_light"], mats["steel"])
    return (width, depth), assets


def tennis_fence_section(name: str, location, mats: dict, assets: dict):
    r = root(name, location)
    parts = [cylinder("Fence post", (-3, 0, 1.8), 0.055, 3.6, mats["green_steel"], 10),
             cylinder("Fence post", (3, 0, 1.8), 0.055, 3.6, mats["green_steel"], 10)]
    for z in (0.2, 1.1, 2.0, 2.9, 3.55):
        parts.append(cylinder_between("Fence horizontal", (-3, 0, z), (3, 0, z), 0.018, mats["green_steel"], 8))
    for x in [(-2.7 + i * 0.3) for i in range(19)]:
        parts.append(cylinder_between("Fence vertical", (x, 0, 0.2), (x, 0, 3.55), 0.012, mats["green_steel"], 6))
    attach(r, parts); assets.setdefault("tennis-fence-6m.glb", r); return r


def tennis_net(name: str, location, mats: dict, assets: dict):
    r = root(name, location)
    parts = [cylinder("Net post", (-9.15, 0, 0.55), 0.045, 1.1, mats["steel"], 10),
             cylinder("Net post", (9.15, 0, 0.55), 0.045, 1.1, mats["steel"], 10),
             cylinder_between("Net tape", (-9.15, 0, 1.02), (9.15, 0, 1.02), 0.028, mats["white"], 8)]
    for x in range(-9, 10):
        parts.append(cylinder_between("Net mesh", (x, 0, 0.18), (x, 0, 0.98), 0.008, mats["white"], 6))
    for z in (0.30, 0.48, 0.66, 0.84):
        parts.append(cylinder_between("Net mesh", (-9.1, 0, z), (9.1, 0, z), 0.008, mats["white"], 6))
    attach(r, parts); assets.setdefault("tennis-net.glb", r); return r


def tennis_bleacher(name: str, location, mats: dict, assets: dict):
    r = root(name, location); parts = []
    for row in range(3):
        parts.append(cube("Aluminum bench", (0, row * 0.62, 0.45 + row * 0.38), (6.2, 0.34, 0.10), mats["steel"], 0.03))
        parts.append(cube("Bleacher riser", (0, row * 0.62 + 0.18, 0.22 + row * 0.30), (6.2, 0.62, 0.10), mats["steel"], 0.02))
    attach(r, parts); assets.setdefault("spectator-bleacher.glb", r); return r


def tennis_floodlight(name: str, location, mats: dict, assets: dict):
    r = root(name, location); parts = [cylinder("Light pole", (0, 0, 4.5), 0.09, 9.0, mats["steel"], 12)]
    for x in (-0.8, -0.27, 0.27, 0.8):
        parts.append(cube("LED floodlight", (x, 0, 9.0), (0.42, 0.24, 0.26), mats["white"], 0.03))
    attach(r, parts); assets.setdefault("tennis-floodlight.glb", r); return r


def add_tennis_lines(cx: float, cy: float, mats: dict) -> None:
    z = 0.145; line = 0.055; length = 36.58; width = 18.29
    for y in (-width / 2, width / 2): cube("Court baseline", (cx, cy + y, z), (length, line, 0.025), mats["white"], 0)
    for x in (-length / 2, length / 2): cube("Court sideline", (cx + x, cy, z), (line, width, 0.025), mats["white"], 0)
    for y in (-6.4, 6.4): cube("Singles sideline", (cx, cy + y, z), (length, line, 0.025), mats["white"], 0)
    for x in (-6.4, 6.4): cube("Service line", (cx + x, cy, z), (line, 12.8, 0.025), mats["white"], 0)
    cube("Centre service line", (cx, cy, z), (12.8, line, 0.025), mats["white"], 0)


def build_tennis(mats: dict) -> tuple[tuple[float, float], dict]:
    width, depth = 82.0, 46.0; assets = {}
    cube("Professional tennis apron", (0, 0, 0), (width, depth, 0.18), mats["court_green"], 0.8)
    for row, y in enumerate((-10.0, 10.0)):
        for col, x in enumerate((-19.6, 19.6)):
            cube("Competition court", (x, y, 0.105), (36.58, 18.29, 0.055), mats["court_blue"], 0.35)
            add_tennis_lines(x, y, mats)
            net = tennis_net(f"Court net {row}-{col}", (x, y, 0.12), mats, assets)
            net.rotation_euler[2] = math.pi / 2
    for y in (-22.2, 22.2):
        for x in (-36, -30, -24, -18, -12, -6, 0, 6, 12, 18, 24, 30, 36): tennis_fence_section("Perimeter fence", (x, y, 0.1), mats, assets)
    for x in (-40.8, 40.8):
        for y in (-18, -12, -6, 0, 6, 12, 18):
            section = tennis_fence_section("Perimeter fence", (x, y, 0.1), mats, assets); section.rotation_euler[2] = math.pi / 2
    for x in (-20, 20): tennis_bleacher("Court bleacher", (x, 0, 0.18), mats, assets)
    for x, y in ((-39, -21), (0, -21), (39, -21), (-39, 21), (0, 21), (39, 21)): tennis_floodlight("Court floodlight", (x, y, 0.18), mats, assets)
    return (width, depth), assets


def nature_log(name: str, location, length: float, yaw: float, mats: dict, assets: dict):
    r = root(name, location, yaw)
    log = cylinder("Debarked balance log", (0, 0, 0.48), 0.42, length, mats["timber"], 18, (0, math.pi / 2, 0))
    attach(r, [log]); assets.setdefault("balance-log.glb", r); return r


def build_nature_play(mats: dict) -> tuple[tuple[float, float], dict]:
    width, depth = 40.0, 30.0; assets = {}
    cube("Forest woodchip floor", (0, 0, 0), (width, depth, 0.18), mats["soil"], 2.2)
    disc("Sand excavation", (12, -6, 0.12), 6.0, 0.08, mats["sand"], (1.2, 0.8, 1))
    rill_points = [(-15, 7, 0.18), (-8, 5, 0.16), (-1, 2, 0.15), (6, 1, 0.14), (13, 4, 0.16)]
    rill = root("Stone edged water rill", (0, 0, 0)); rill_parts = []
    for index, (start, end) in enumerate(zip(rill_points, rill_points[1:])):
        a, b = Vector(start), Vector(end); direction = b - a; yaw = math.atan2(direction.y, direction.x)
        rill_parts.append(cube(f"Shallow water reach {index}", (a + b) * 0.5, (direction.length + 0.3, 1.05, 0.055), mats["water_dark"], 0.18))
        rill_parts[-1].rotation_euler[2] = yaw
        normal = Vector((-math.sin(yaw), math.cos(yaw), 0)) * 0.72
        for side in (-1, 1):
            for step in range(max(2, round(direction.length / 1.25))):
                point = a + direction * ((step + 0.5) / max(2, round(direction.length / 1.25))) + normal * side
                rill_parts.append(sphere("Rill edge stone", (point.x, point.y, 0.28), 0.34, mats["rock"], (1.25, 0.9, 0.45)))
    attach(rill, rill_parts); assets["water-rill.glb"] = rill
    for i, (x, y, length, yaw) in enumerate(((-12, -6, 6.5, 0.2), (-6, -9, 5.5, -0.35), (-3, 9, 6.0, 0.55))): nature_log(f"Balance log {i}", (x, y, 0.18), length, yaw, mats, assets)
    fort = root("Forest log fort", (9, 7, 0.18)); parts = []
    for x in (-2.3, 2.3):
        for y in (-2.0, 2.0): parts.append(cylinder("Fort post", (x, y, 1.8), 0.18, 3.6, mats["timber"], 14))
    parts += [cube("Fort platform", (0, 0, 1.5), (5.2, 4.6, 0.24), mats["timber_light"], 0.08),
              sloped_box("Fort ramp", (-6, -2, 0.25), (-2.4, -1.4, 1.5), 1.4, 0.18, mats["timber_light"])]
    attach(fort, parts); assets["log-fort.glb"] = fort
    tunnel = root("Willow tunnel", (-10, 7, 0.18)); tunnel_parts = []
    for x in (-3, -1.5, 0, 1.5, 3):
        tunnel_parts.append(curve_line("Woven willow rib", [(x, -2, 0), (x, -1, 1.5), (x, 0, 2.2), (x, 1, 1.5), (x, 2, 0)], 0.055, mats["timber"]))
    attach(tunnel, tunnel_parts); assets["willow-tunnel.glb"] = tunnel
    stump_root = root("Stepping stump", (0, -5, 0.18)); stump = cylinder("Stepping stump", (0, 0, 0.38), 0.55, 0.76, mats["timber"], 18); attach(stump_root, [stump]); assets["stepping-stump.glb"] = stump_root
    for i, (x, y, h) in enumerate(((-2, -4, 0.4), (0, -5, 0.6), (2, -4, 0.85), (4, -2, 0.5), (6, -1, 0.7))):
        cylinder(f"Stump {i}", (x, y, 0.18 + h / 2), 0.5, h, mats["timber"], 18)
    rocks = root("Nature boulder cluster", (12, -6, 0.18)); attach(rocks, [sphere("Play boulder", (-2, 0, 0.8), 1.2, mats["rock"], (1.2, 0.9, 0.7)), sphere("Play boulder", (1, 1, 0.65), 1.0, mats["rock"], (1.0, 0.8, 0.65)), sphere("Play boulder", (2, -1, 0.9), 1.3, mats["rock"], (1.1, 0.9, 0.7))]); assets["play-boulders.glb"] = rocks
    add_boundary_planting(width, depth, mats, 12)
    return (width, depth), assets


def build_pump_track(mats: dict) -> tuple[tuple[float, float], dict]:
    width, depth = 50.0, 30.0; assets = {}
    cube("Pump track receiving lawn", (0, 0, 0), (width, depth, 0.18), mats["grass"], 1.8)
    loop = root("Competition pump track", (0, 0, 0.18)); parts = []
    points = []
    for i in range(64):
        angle = math.tau * i / 64; x = math.cos(angle) * 20.5; y = math.sin(angle) * (10.8 + 2.1 * math.cos(angle * 2)); z = 0.45 + 0.28 * (0.5 + 0.5 * math.sin(angle * 8))
        points.append((x, y, z))
    outer_track = curve_line("Asphalt rhythm loop", points, 1.25, mats["asphalt_black"], cyclic=True)
    outer_track.scale.z = 0.22; parts.append(outer_track)
    inner = []
    for i in range(64):
        angle = math.tau * i / 64
        inner.append((math.sin(angle) * 9.5, math.sin(angle * 2) * 5.2, 0.42 + 0.14 * (0.5 + 0.5 * math.sin(angle * 6))))
    inner_track = curve_line("Inner crossover loop", inner, 1.15, mats["asphalt_black"], cyclic=True)
    inner_track.scale.z = 0.22; parts.append(inner_track)
    attach(loop, parts); assets["pump-track-loop.glb"] = loop
    mound = root("Pump track start mound", (-18, -2, 0.18)); attach(mound, [cube("Start deck", (0, 0, 0.65), (5.0, 3.2, 1.3), mats["asphalt_black"], 0.7), sloped_box("Start roll-in", (2.3, 0, 1.2), (6.5, 0, 0.32), 3.0, 0.32, mats["asphalt_black"])]); assets["start-mound.glb"] = mound
    add_bench("Pump spectator bench", (0, -13, 0.18), 0, mats["timber_light"], mats["steel"])
    return (width, depth), assets


def bar_frame(name: str, location, width: float, depth: float, height: float, mats: dict, assets: dict, filename: str):
    r = root(name, location); parts = []
    for x in (-width / 2, width / 2):
        for y in (-depth / 2, depth / 2): parts.append(cylinder("Rig upright", (x, y, height / 2), 0.075, height, mats["black_steel"], 12))
    parts += [cylinder_between("Rig top bar", (-width / 2, -depth / 2, height), (width / 2, -depth / 2, height), 0.065, mats["black_steel"], 12),
              cylinder_between("Rig top bar", (-width / 2, depth / 2, height), (width / 2, depth / 2, height), 0.065, mats["black_steel"], 12)]
    for i in range(6):
        x = -width / 2 + width * i / 5; parts.append(cylinder_between("Monkey bar", (x, -depth / 2, height), (x, depth / 2, height), 0.045, mats["black_steel"], 10))
    attach(r, parts); assets.setdefault(filename, r); return r


def build_fitness(mats: dict) -> tuple[tuple[float, float], dict]:
    width, depth = 30.0, 25.0; assets = {}
    cube("Fitness paver apron", (0, 0, 0), (width, depth, 0.18), mats["concrete"], 1.0)
    for x, y, rx, ry in ((-7, 4, 6, 4.5), (6, 3, 6, 4.5), (-5, -7, 5, 3.5), (7, -6, 5, 3.5)): disc("Fitness rubber station", (x, y, 0.12), rx, 0.07, mats["dark_concrete"], (1, ry / rx, 1))
    bar_frame("Main calisthenics rig", (-6, 4, 0.18), 6.0, 3.6, 3.2, mats, assets, "calisthenics-rig.glb")
    dips = root("Parallel dip bars", (6, 3, 0.18)); dip_parts = []
    for y in (-0.55, 0.55):
        dip_parts += [cylinder("Dip upright", (-1.6, y, 0.65), 0.06, 1.3, mats["black_steel"], 10), cylinder("Dip upright", (1.6, y, 0.65), 0.06, 1.3, mats["black_steel"], 10), cylinder_between("Dip rail", (-1.6, y, 1.3), (1.6, y, 1.3), 0.055, mats["black_steel"], 10)]
    attach(dips, dip_parts); assets["parallel-bars.glb"] = dips
    bench = root("Inclined situp bench", (-5, -7, 0.18)); attach(bench, [sloped_box("Situp pad", (-2, 0, 0.35), (2, 0, 0.95), 0.75, 0.16, mats["black_steel"]), cylinder_between("Foot bar", (-2.2, -0.75, 0.45), (-2.2, 0.75, 0.45), 0.055, mats["black_steel"], 10)]); assets["situp-bench.glb"] = bench
    rings = bar_frame("Gymnastics rings frame", (7, -6, 0.18), 4.5, 2.0, 3.0, mats, assets, "rings-frame.glb")
    for x in (-0.65, 0.65):
        cylinder_between("Ring strap", (x, 0, 3.0), (x, 0, 1.9), 0.018, mats["rope"], 8)
        bpy.ops.mesh.primitive_torus_add(major_radius=0.24, minor_radius=0.035, major_segments=24, minor_segments=8, location=(x, 0, 2.0), rotation=(math.pi / 2, 0, 0)); bpy.context.object.data.materials.append(mats["timber"]); bpy.context.object.parent = rings
    add_bench("Fitness entry bench", (0, -11, 0.18), 0, mats["timber_light"], mats["steel"])
    return (width, depth), assets


def build_memorial(mats: dict) -> tuple[tuple[float, float], dict]:
    width, depth = 50.0, 40.0; assets = {}
    cube("Formal gravel parterre", (0, 0, 0), (width, depth, 0.18), mats["gravel"], 1.0)
    for x in (-15, 15):
        for y in (-11, 8):
            cube("Clipped parterre", (x, y, 0.32), (13, 7, 0.58), mats["hedge"], 0.7)
            cube("Parterre gravel inset", (x, y, 0.63), (9, 3, 0.04), mats["gravel"], 0.4)
    pool = root("Axial reflecting pool", (0, 4, 0.18)); attach(pool, [cube("Pool stone basin", (0, 0, 0.25), (12, 21, 0.50), mats["marble"], 0.35), cube("Still reflecting water", (0, 0, 0.52), (10.8, 19.8, 0.06), mats["water_dark"], 0.25)]); assets["reflecting-pool.glb"] = pool
    fountain = root("Classical tiered fountain", (0, -10, 0.18)); fparts = [disc("Lower fountain bowl", (0, 0, 0.38), 3.2, 0.32, mats["marble"]), cylinder("Fountain stem", (0, 0, 1.35), 0.42, 1.8, mats["marble"], 24), disc("Upper fountain bowl", (0, 0, 2.1), 1.8, 0.25, mats["marble"]), cylinder("Fountain finial", (0, 0, 2.9), 0.25, 1.5, mats["marble"], 20)]
    attach(fountain, fparts); assets["tiered-fountain.glb"] = fountain
    wall = root("Commemorative marble wall", (0, 18, 0.18)); attach(wall, [cube("Memorial wall", (0, 0, 2.2), (12, 0.8, 4.4), mats["marble"], 0.25), disc("Memorial medallion", (0, -0.45, 2.4), 1.5, 0.12, mats["black_steel"], (1, 1, 0.2))]); assets["memorial-wall.glb"] = wall
    urn = root("Stone topiary urn", (-20, -13, 0.18)); attach(urn, [cylinder("Urn pedestal", (0, 0, 0.55), 0.55, 1.1, mats["marble"], 20), disc("Urn bowl", (0, 0, 1.3), 0.85, 0.45, mats["marble"]), sphere("Clipped topiary", (0, 0, 2.5), 1.15, mats["hedge"], (1, 1, 1.25))]); assets["topiary-urn.glb"] = urn
    for x, y in ((-20, 13), (20, -13), (20, 13)):
        cylinder("Urn pedestal repeat", (x, y, 0.73), 0.55, 1.1, mats["marble"], 20)
        disc("Urn bowl repeat", (x, y, 1.48), 0.85, 0.45, mats["marble"])
        sphere("Clipped topiary repeat", (x, y, 2.68), 1.15, mats["hedge"], (1, 1, 1.25))
    for x in (-22, 22):
        for y in (-15, -5, 5, 15):
            cylinder("Formal evergreen trunk", (x, y, 1.8), 0.16, 3.2, mats["trunk"], 12)
            bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=1.8, radius2=0.12, depth=5.5, location=(x, y, 4.2)); bpy.context.object.data.materials.append(mats["hedge"])
    return (width, depth), assets


BUILDERS = {
    "inclusive_playground": ("inclusive-accessible-playground", build_playground),
    "skate_park": ("skate-park", build_skate),
    "dog_park": ("dog-park", build_dog),
    "splash_pad_area": ("splash-pad-water-play", build_splash),
    "community_garden": ("community-garden-allotments", build_garden),
    "tennis_court_cluster": ("tennis-court-professional", build_tennis),
    "nature_play_area": ("nature-play-forest-adventure", build_nature_play),
    "pump_track": ("pump-track-asphalt-competition", build_pump_track),
    "outdoor_fitness_circuit": ("outdoor-fitness-calisthenics", build_fitness),
    "memorial_garden": ("memorial-garden-classical-formal", build_memorial),
}


def render_archetype(archetype_id: str, slug: str, builder, output_root: Path, kit_root: Path, skin_root: Path) -> None:
    reset_scene()
    mats = materials(skin_root, slug)
    (width, depth), assets = builder(mats)
    # Large buildings are a separate downstream layer, but the park still needs
    # a neutral receiving landscape so standalone QA does not fall into black.
    if archetype_id == "skate_park":
        # Keep the context receiver outside the registered skate envelope so it
        # cannot fill the authored bowl openings.
        outer_w, outer_d, band = width + 400, depth + 400, 200
        cube("Context ground north", (0, depth / 2 + band / 2, -0.20), (outer_w, band, 0.22), mats["grass"], 1.0)
        cube("Context ground south", (0, -depth / 2 - band / 2, -0.20), (outer_w, band, 0.22), mats["grass"], 1.0)
        cube("Context ground west", (-width / 2 - band / 2, 0, -0.20), (band, depth, 0.22), mats["grass"], 1.0)
        cube("Context ground east", (width / 2 + band / 2, 0, -0.20), (band, depth, 0.22), mats["grass"], 1.0)
    else:
        cube("Separate-building-layer receiving ground", (0, 0, -0.20), (width + 400, depth + 400, 0.22), mats["grass"], 1.0)
    out = output_root / slug
    out.mkdir(parents=True, exist_ok=True)
    kit_dir = kit_root / slug
    kit_dir.mkdir(parents=True, exist_ok=True)
    for filename, asset_root in assets.items():
        export_root(asset_root, kit_dir / filename)
    manifest = {
        "schemaVersion": 1,
        "archetypeId": archetype_id,
        "slug": slug,
        "method": "lego_surface_plus_metric_program_assets",
        "envelopeM": [width, depth],
        "metricScale": 1.0,
        "groundContactOriginZM": 0.0,
        "surfaceOwner": "lego_park_grammar",
        "people": False,
        "largeBuildings": False,
        "skin": f"park-skins/{slug}/adaptive-v1",
        "skinMethod": "reference_statistics_plus_procedural_structure",
        "depthAssets": sorted(assets),
    }
    (kit_dir / "kit_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    configure_render()
    scene = bpy.context.scene
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.view_settings.exposure = -0.25
    max_dim = max(width, depth)
    views = (
        ("generated_base.png", (-width * 0.82, -depth * 0.88, max_dim * 0.42), (0, 0, 1.2), 52, None),
        ("generated_angle_60.png", (-width * 0.76, -depth * 0.80, max_dim * 0.88), (0, 0, 0.5), 54, None),
        ("generated_angle_90.png", (0, 0, max_dim * 1.35), (0, 0, 0), 52, max_dim * 1.32),
    )
    for filename, location, target, lens, ortho_scale in views:
        cam = camera(filename, location, target, lens)
        if ortho_scale is not None:
            cam.data.type = "ORTHO"
            cam.data.ortho_scale = ortho_scale
            cam.rotation_euler[2] += math.pi / 2
        scene.render.filepath = str(out / filename)
        bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out / f"{slug}.blend"))
    print(f"rendered {archetype_id} to {out}")


def main() -> None:
    args = parse_args()
    skin_root = (args.skin_root or (args.repo_root / "frontend/public/park-skins")).resolve()
    selected = BUILDERS if args.archetype == "all" else {args.archetype: BUILDERS[args.archetype]}
    for archetype_id, (slug, builder) in selected.items():
        render_archetype(archetype_id, slug, builder, args.output.resolve(), args.kit_output.resolve(), skin_root)


if __name__ == "__main__":
    main()
