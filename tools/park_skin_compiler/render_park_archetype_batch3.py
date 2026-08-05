"""Build and render five composition-trained park LEGO pilots.

The scenes translate archetype-photo evidence and paired API composition studies
into deterministic metric geometry. People remain analysis-only scale and use
references; no people or large buildings are generated.
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

from render_adaptive_park_shapes import apply_planar_metric_uv, cube, reset_scene  # noqa: E402
from render_archetype_matched_basketball_pilot import (  # noqa: E402
    add_bench,
    add_tree,
    curve_line,
    cylinder_between,
)
from render_park_archetype_batch2 import (  # noqa: E402
    add_boundary_planting,
    attach,
    cylinder,
    disc,
    export_root,
    materials,
    render_archetype,
    root,
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


def polygon_surface(name: str, vertices, z: float, mat):
    mesh = bpy.data.meshes.new(f"{name} mesh")
    mesh.from_pydata([(x, y, z) for x, y in vertices], [], [list(range(len(vertices)))])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    apply_planar_metric_uv(obj, mat)
    return obj


def line(name: str, start, end, width: float, z: float, mat):
    a, b = Vector((*start, z)), Vector((*end, z))
    delta = b - a
    obj = cube(name, (a + b) * 0.5, (delta.length, width, 0.025), mat, 0)
    obj.rotation_euler[2] = math.atan2(delta.y, delta.x)
    return obj


def ellipse_line(name: str, rx: float, ry: float, z: float, width: float, mat, center=(0, 0)):
    cx, cy = center
    points = [
        (cx + math.cos(math.tau * index / 128) * rx, cy + math.sin(math.tau * index / 128) * ry, z)
        for index in range(128)
    ]
    return curve_line(name, points, width / 2, mat, cyclic=True)


def fence_section(name: str, location, yaw: float, mats: dict, assets: dict, *, filename: str, height=3.0, length=6.0):
    r = root(name, location, yaw)
    parts = [
        cylinder("Fence post west", (-length / 2, 0, height / 2), 0.07, height, mats["black_steel"], 10),
        cylinder("Fence post east", (length / 2, 0, height / 2), 0.07, height, mats["black_steel"], 10),
    ]
    for z in (0.15, height / 2, height - 0.15):
        parts.append(cylinder_between("Fence horizontal wire", (-length / 2, 0, z), (length / 2, 0, z), 0.018, mats["black_steel"], 6))
    wire_count = max(3, round(length / 0.75))
    for index in range(1, wire_count):
        x = -length / 2 + length * index / wire_count
        parts.append(cylinder("Fence vertical wire", (x, 0, height / 2), 0.012, height, mats["black_steel"], 6))
    attach(r, parts)
    assets.setdefault(filename, r)
    return r


def fence_rectangle(width: float, depth: float, mats: dict, assets: dict, filename: str, height=3.0, center=(0.0, 0.0)):
    cx, cy = center
    for y in (-depth / 2, depth / 2):
        count = max(1, math.ceil(width / 6))
        section = width / count
        for index in range(count):
            x = -width / 2 + section * (index + 0.5)
            fence_section("Shared perimeter fence", (cx + x, cy + y, 0.14), 0, mats, assets, filename=filename, height=height, length=section)
    for x in (-width / 2, width / 2):
        count = max(1, math.ceil(depth / 6))
        section = depth / count
        for index in range(count):
            y = -depth / 2 + section * (index + 0.5)
            fence_section("Shared perimeter fence", (cx + x, cy + y, 0.14), math.pi / 2, mats, assets, filename=filename, height=height, length=section)


def low_perimeter_fence(width: float, depth: float, mats: dict, *, center=(0.0, 0.0), height=1.1):
    cx, cy = center
    for y in (-depth / 2, depth / 2):
        cylinder_between("Low fence rail", (cx - width / 2, cy + y, height), (cx + width / 2, cy + y, height), 0.035, mats["white"], 8)
        for x in range(-round(width / 2), round(width / 2) + 1, 4):
            cylinder("Low fence picket", (cx + x, cy + y, height / 2), 0.028, height, mats["white"], 8)
    for x in (-width / 2, width / 2):
        cylinder_between("Low fence rail", (cx + x, cy - depth / 2, height), (cx + x, cy + depth / 2, height), 0.035, mats["white"], 8)
        for y in range(-round(depth / 2), round(depth / 2) + 1, 4):
            cylinder("Low fence picket", (cx + x, cy + y, height / 2), 0.028, height, mats["white"], 8)


def shade_sail(name: str, location, mats: dict, assets: dict):
    r = root(name, location)
    parts = []
    points = [(-3.2, -2.2, 3.2), (3.2, -2.2, 3.8), (3.2, 2.2, 3.2), (-3.2, 2.2, 3.8)]
    for index, (x, y, z) in enumerate(points):
        parts.append(cylinder(f"Shade pole {index}", (x, y, z / 2), 0.07, z, mats["steel"], 12))
    sail = polygon_surface("Tensioned shade fabric", [(-3.0, -2.0), (3.0, -2.0), (3.0, 2.0), (-3.0, 2.0)], 3.42, mats["rubber_sand"])
    parts.append(sail)
    attach(r, parts)
    assets.setdefault("shade-sail.glb", r)
    return r


def pickleball_net(name: str, location, mats: dict, assets: dict):
    r = root(name, location)
    parts = [
        cylinder("Net post south", (0, -3.35, 0.47), 0.045, 0.94, mats["black_steel"], 10),
        cylinder("Net post north", (0, 3.35, 0.47), 0.045, 0.94, mats["black_steel"], 10),
    ]
    for z in (0.10, 0.30, 0.50, 0.70, 0.86):
        parts.append(cylinder_between("Net horizontal cord", (0, -3.35, z), (0, 3.35, z), 0.012, mats["black_steel"], 6))
    for index in range(13):
        y = -3.35 + 6.7 * index / 12
        parts.append(cylinder("Net vertical cord", (0, y, 0.46), 0.009, 0.72, mats["black_steel"], 6))
    attach(r, parts)
    assets.setdefault("pickleball-net.glb", r)
    return r


def add_pickleball_lines(cx: float, cy: float, mats: dict) -> None:
    white = mats["white"]
    z = 0.205
    half_w, half_l = 3.05, 6.705
    for x in (-half_w, half_w): line("Pickleball sideline", (cx + x, cy - half_l), (cx + x, cy + half_l), 0.055, z, white)
    for y in (-half_l, half_l): line("Pickleball baseline", (cx - half_w, cy + y), (cx + half_w, cy + y), 0.055, z, white)
    for y in (-2.13, 2.13): line("Non-volley line", (cx - half_w, cy + y), (cx + half_w, cy + y), 0.055, z, white)
    line("Service centre line north", (cx, cy + 2.13), (cx, cy + half_l), 0.055, z, white)
    line("Service centre line south", (cx, cy - 2.13), (cx, cy - half_l), 0.055, z, white)


def build_pickleball(mats: dict):
    width, depth = 78.0, 66.0
    assets = {}
    cube("Community recreation lawn", (0, 0, 0), (width, depth, 0.18), mats["grass"], 1.2)
    cube("Public arrival walk", (0, -28, 0.13), (70, 5.5, 0.08), mats["concrete"], 0.35)
    cube("Court and play connector", (-2, 3, 0.13), (5.5, 56, 0.08), mats["concrete"], 0.35)
    cube("Four-court compound", (16.5, 7.5, 0.11), (23.0, 40.0, 0.10), mats["court_green"], 0.4)
    cube("Single-court compound", (-24, 17, 0.11), (11.5, 20.5, 0.10), mats["court_green"], 0.4)
    court_centres = ((11, -2), (22, -2), (11, 17), (22, 17), (-24, 17))
    for index, (cx, cy) in enumerate(court_centres):
        cube("Pickleball safety envelope", (cx, cy, 0.16), (9.14, 18.29, 0.06), mats["court_blue"], 0.18)
        add_pickleball_lines(cx, cy, mats)
        net = pickleball_net(f"Pickleball net {index}", (cx, cy, 0.2), mats, assets)
        net.rotation_euler[2] = math.pi / 2
    fence_rectangle(23.0, 40.0, mats, assets, "pickleball-fence-6m.glb", height=3.0, center=(16.5, 7.5))
    fence_rectangle(11.5, 20.5, mats, assets, "pickleball-fence-6m.glb", height=3.0, center=(-24, 17))

    cube("Playground safety surface", (-22, -8, 0.16), (27, 26, 0.06), mats["rubber_sand"], 2.2)
    play = root("Neighbourhood play structure", (-22, -8, 0.2))
    play_parts = [
        cube("Play tower deck", (0, 0, 1.45), (4.6, 4.6, 0.32), mats["timber"], 0.25),
        cube("Play tower roof", (0, 0, 4.0), (5.4, 5.4, 0.30), mats["rubber_orange"], 0.35),
        cube("Wide slide", (4.4, 0, 1.1), (5.5, 2.0, 0.26), mats["green_steel"], 0.55),
    ]
    for x in (-1.8, 1.8):
        for y in (-1.8, 1.8):
            play_parts.append(cylinder("Play tower post", (x, y, 1.9), 0.11, 3.8, mats["blue_steel"], 12))
    attach(play, play_parts)
    assets["play-structure.glb"] = play
    swings = root("Four-seat swing bay", (-22, 2, 0.2))
    swing_parts = [
        cylinder_between("Swing top rail", (-5, 0, 3.3), (5, 0, 3.3), 0.10, mats["blue_steel"], 12),
        cylinder_between("Swing leg", (-5, 0, 3.3), (-4, -1.4, 0), 0.09, mats["blue_steel"], 12),
        cylinder_between("Swing leg", (5, 0, 3.3), (4, -1.4, 0), 0.09, mats["blue_steel"], 12),
    ]
    for x in (-3.5, -1.2, 1.2, 3.5):
        swing_parts.extend([
            cylinder_between("Swing chain", (x - 0.24, 0, 3.25), (x - 0.24, 0, 1.0), 0.018, mats["steel"], 8),
            cylinder_between("Swing chain", (x + 0.24, 0, 3.25), (x + 0.24, 0, 1.0), 0.018, mats["steel"], 8),
            cube("Swing seat", (x, 0, 0.94), (0.65, 0.40, 0.10), mats["rubber_blue"], 0.06),
        ])
    attach(swings, swing_parts)
    assets["swing-bay.glb"] = swings

    for x in (8, 22):
        shade_sail("Social edge shade sail", (x, -25, 0.22), mats, assets)
        add_bench("Social edge bench", (x, -22.3, 0.2), 0, mats["timber_light"], mats["steel"])
    for x, y in ((5, -15), (28, -15), (5, 27), (28, 27), (-30, 27), (-18, 27)):
        pole = root("Shared court floodlight", (x, y, 0.2))
        attach(pole, [cylinder("Light mast", (0, 0, 4.5), 0.08, 9.0, mats["steel"], 12), cube("LED head", (0, 0, 9.0), (1.6, 0.3, 0.3), mats["white"], 0.03)])
        assets.setdefault("pickleball-floodlight.glb", pole)
    for x, y, scale in ((-35, -26, 0.9), (-35, 5, 1.0), (-35, 28, 0.9), (35, -25, 0.95), (35, 28, 1.0)):
        add_tree("Community park edge tree", (x, y), scale, mats["trunk"], mats["foliage"], mats["foliage_light"])
    return (width, depth), assets


def soccer_goal(name: str, location, yaw: float, mats: dict, assets: dict, filename="soccer-goal.glb"):
    r = root(name, location, yaw)
    parts = [
        cylinder("Goal post left", (0, -3.66, 1.22), 0.055, 2.44, mats["white"], 12),
        cylinder("Goal post right", (0, 3.66, 1.22), 0.055, 2.44, mats["white"], 12),
        cylinder_between("Goal crossbar", (0, -3.66, 2.44), (0, 3.66, 2.44), 0.055, mats["white"], 12),
    ]
    attach(r, parts)
    assets.setdefault(filename, r)
    return r


def add_soccer_field(
    cx: float,
    cy: float,
    width: float,
    depth: float,
    mats: dict,
    assets: dict,
    *,
    base_z: float = 0.12,
    line_z: float = 0.19,
):
    cube("Striped soccer field", (cx, cy, base_z), (width, depth, 0.10), mats["turf"], 0.4)
    z, white = line_z, mats["white"]
    stripe_width = width / 10
    for index in range(10):
        if index % 2:
            x = cx - width / 2 + stripe_width * (index + 0.5)
            cube("Mown soccer stripe", (x, cy, base_z + 0.056), (stripe_width, depth, 0.018), mats["court_green"], 0.12)
    for x in (-width / 2, width / 2): line("Touchline", (cx + x, cy - depth / 2), (cx + x, cy + depth / 2), 0.1, z, white)
    for y in (-depth / 2, depth / 2): line("Goal line", (cx - width / 2, cy + y), (cx + width / 2, cy + y), 0.1, z, white)
    line("Halfway line", (cx, cy - depth / 2), (cx, cy + depth / 2), 0.1, z, white)
    points = [(cx + math.cos(math.tau * i / 64) * 9.15, cy + math.sin(math.tau * i / 64) * 9.15, z) for i in range(64)]
    curve_line("Centre circle", points, 0.05, white, cyclic=True)
    penalty_width = min(40.32, depth - 4)
    goal_area_width = min(18.32, depth - 8)
    for direction in (-1, 1):
        goal_x = cx + direction * width / 2
        penalty_x = goal_x - direction * 16.5
        goal_area_x = goal_x - direction * 5.5
        line("Penalty area end", (penalty_x, cy - penalty_width / 2), (penalty_x, cy + penalty_width / 2), 0.1, z, white)
        for y in (-penalty_width / 2, penalty_width / 2):
            line("Penalty area side", (goal_x, cy + y), (penalty_x, cy + y), 0.1, z, white)
        line("Goal area end", (goal_area_x, cy - goal_area_width / 2), (goal_area_x, cy + goal_area_width / 2), 0.1, z, white)
        for y in (-goal_area_width / 2, goal_area_width / 2):
            line("Goal area side", (goal_x, cy + y), (goal_area_x, cy + y), 0.1, z, white)
        disc("Penalty spot", (goal_x - direction * 11.0, cy, z), 0.18, 0.025, white)
    goal_ground_z = base_z + 0.10
    soccer_goal("Soccer goal west", (cx - width / 2, cy, goal_ground_z), 0, mats, assets)
    soccer_goal("Soccer goal east", (cx + width / 2, cy, goal_ground_z), math.pi, mats, assets)


def track_bleacher(name: str, location, mats: dict, assets: dict, filename="track-bleacher.glb"):
    r = root(name, location)
    parts = []
    for row in range(5):
        parts.append(cube("Bleacher seat", (0, row * 0.72, 0.48 + row * 0.34), (28, 0.34, 0.11), mats["steel"], 0.03))
        parts.append(cube("Bleacher tread", (0, row * 0.72 + 0.2, 0.22 + row * 0.28), (28, 0.72, 0.10), mats["steel"], 0.02))
    attach(r, parts)
    assets.setdefault(filename, r)
    return r


def build_track_oval(mats: dict):
    width, depth = 220.0, 135.0
    assets = {}
    cube("Athletics precinct lawn", (0, 0, 0), (width, depth, 0.18), mats["grass"], 2.0)
    disc("Eight lane red track", (0, 0, 0.13), 90, 0.09, mats["rubber_orange"], (1, 50 / 90, 1))
    disc("Track infield", (0, 0, 0.19), 80, 0.08, mats["turf"], (1, 40 / 80, 1))
    for lane_index in range(9):
        ellipse_line("Track lane line", 80 + lane_index * 1.22, 40 + lane_index * 1.22, 0.245, 0.08, mats["white"])
    add_soccer_field(0, 0, 100, 64, mats, assets, base_z=0.25, line_z=0.315)
    cube("Long jump runway", (-28, -58, 0.14), (42, 1.25, 0.08), mats["rubber_orange"], 0.16)
    cube("Long jump sand pit", (-2, -58, 0.15), (9, 3.2, 0.08), mats["sand"], 0.22)
    disc("Shot put circle", (40, -58, 0.16), 1.25, 0.08, mats["concrete"])
    track_bleacher("Track spectator bleacher", (0, 54, 0.18), mats, assets)
    cube("Reserved fieldhouse pad", (-55, 59, 0.13), (32, 11, 0.08), mats["concrete"], 0.35)
    for x, y in ((-101, -60), (101, -60), (-101, 60), (101, 60)):
        add_tree("Athletics corner tree", (x, y), 0.92, mats["trunk"], mats["foliage"], mats["foliage_light"])
    return (width, depth), assets


def baseball_backstop(name: str, location, yaw: float, mats: dict, assets: dict, filename="baseball-backstop.glb"):
    r = root(name, location, yaw)
    parts = []
    for angle in (-0.60, -0.30, 0, 0.30, 0.60):
        x, y = -6.2 * math.cos(angle), 6.2 * math.sin(angle)
        parts.append(cylinder("Backstop post", (x, y, 2.8), 0.075, 5.6, mats["black_steel"], 12))
    for z in (1.0, 2.2, 3.4, 4.6, 5.6):
        parts.append(curve_line("Backstop mesh horizontal", [
            (-5.1, -3.5, z), (-5.9, -1.9, z), (-6.2, 0, z), (-5.9, 1.9, z), (-5.1, 3.5, z),
        ], 0.018, mats["black_steel"]))
    attach(r, parts)
    assets.setdefault(filename, r)
    return r


def add_diamond(home, yaw: float, mats: dict, assets: dict, *, radius=72.0, base=18.29, filename="baseball-backstop.glb"):
    hx, hy = home
    r = root("Youth baseball diamond", (hx, hy, 0), yaw)
    outer_fan = [(0, 0)] + [(math.cos(-math.pi / 4 + math.pi / 2 * i / 64) * radius, math.sin(-math.pi / 4 + math.pi / 2 * i / 64) * radius) for i in range(65)]
    inner_radius = radius - 4.0
    inner_fan = [(0, 0)] + [(math.cos(-math.pi / 4 + math.pi / 2 * i / 64) * inner_radius, math.sin(-math.pi / 4 + math.pi / 2 * i / 64) * inner_radius) for i in range(65)]
    warning = polygon_surface("Textured red-clay warning track sector", outer_fan, 0.12, mats["warning_track"])
    outfield = polygon_surface("Striped mown outfield sector", inner_fan, 0.15, mats["turf"])
    b = base / math.sqrt(2)
    parts = [warning, outfield]
    # Parallel mowing passes are clipped to the 90-degree outfield sector.
    # Their subtle alternate tint preserves the archetype's striped turf
    # character without projecting any source photograph onto the geometry.
    stripe_width = 9.0
    for stripe_index, x0 in enumerate(range(0, math.ceil(inner_radius), round(stripe_width))):
        if stripe_index % 2 == 0:
            continue
        x1 = min(inner_radius, x0 + stripe_width)
        samples = [x0 + (x1 - x0) * index / 12 for index in range(13)]
        upper = [
            (x, min(x, math.sqrt(max(0.0, inner_radius * inner_radius - x * x))))
            for x in samples
        ]
        lower = [(x, -y) for x, y in reversed(upper)]
        parts.append(polygon_surface("Alternating outfield mowing pass", upper + lower, 0.17, mats["turf_alt"]))
    dirt = polygon_surface(
        "Textured red-clay infield",
        [(0, 0), (b, -b), (2 * b, 0), (b, b)],
        0.19,
        mats["infield_clay"],
    )
    inner_grass = polygon_surface(
        "Grass infield centre",
        [(4.2, 0), (b, -b + 3.2), (2 * b - 4.2, 0), (b, b - 3.2)],
        0.215,
        mats["turf_alt"],
    )
    parts.extend([dirt, inner_grass])
    white = mats["white"]
    parts.append(line("First-base foul line", (0, 0), (radius / math.sqrt(2), -radius / math.sqrt(2)), 0.08, 0.24, white))
    parts.append(line("Third-base foul line", (0, 0), (radius / math.sqrt(2), radius / math.sqrt(2)), 0.08, 0.24, white))
    for z in (0.55, 1.25, 2.0):
        arc = [(math.cos(-math.pi / 4 + math.pi / 2 * i / 64) * radius, math.sin(-math.pi / 4 + math.pi / 2 * i / 64) * radius, z) for i in range(65)]
        parts.append(curve_line("Outfield fence rail", arc, 0.028, mats["black_steel"]))
    for i in range(0, 65, 4):
        angle = -math.pi / 4 + math.pi / 2 * i / 64
        parts.append(cylinder("Outfield fence post", (math.cos(angle) * radius, math.sin(angle) * radius, 1.0), 0.045, 2.0, mats["black_steel"], 8))
    for index, (x, y) in enumerate(((0, 0), (b, -b), (2 * b, 0), (b, b))):
        parts.append(cube(f"Base {index}", (x, y, 0.27), (0.38, 0.38, 0.08), white, 0.04))
    parts.append(disc("Pitching mound", (2 * b * 0.52, 0, 0.23), 1.6, 0.08, mats["infield_clay"]))
    for side in (-1, 1):
        dugout_y = side * 14.5
        parts.extend([
            cube("Covered dugout slab", (10.5, dugout_y, 0.18), (10, 3.2, 0.10), mats["concrete"], 0.25),
            cube("Covered dugout roof", (10.5, dugout_y, 2.65), (10.5, 3.5, 0.22), mats["steel"], 0.18),
            cube("Dugout bench", (10.5, dugout_y, 0.60), (8.0, 0.55, 0.18), mats["timber_light"], 0.08),
        ])
    for lx, ly in ((8, -25), (8, 25), (46, -42), (46, 42)):
        parts.extend([
            cylinder("Field light mast", (lx, ly, 6.0), 0.11, 12.0, mats["steel"], 12),
            cube("Field light bank", (lx, ly, 12.0), (2.8, 0.35, 0.32), mats["white"], 0.04),
        ])
    attach(r, parts)
    backstop = baseball_backstop("Diamond backstop", (hx, hy, 0.2), yaw, mats, assets, filename)
    return r, backstop


def shared_bleacher(name: str, location, yaw: float, mats: dict, assets: dict, filename="shared-bleacher.glb"):
    r = root(name, location, yaw)
    parts = []
    for row in range(3):
        parts.append(cube("Shared bleacher seat", (0, row * 0.62, 0.42 + row * 0.32), (8, 0.32, 0.10), mats["steel"], 0.03))
    attach(r, parts)
    assets.setdefault(filename, r)
    return r


def build_baseball_hub(mats: dict):
    width, depth = 230.0, 210.0
    assets = {}
    cube("Three-field baseball complex lawn", (0, 0, 0), (width, depth, 0.18), mats["grass"], 2.0)
    disc("Shared club forecourt", (0, 0, 0.14), 20, 0.08, mats["concrete"])
    cube("Reserved separate clubhouse pad", (0, 0, 0.19), (22, 15, 0.10), mats["dark_concrete"], 0.45)
    cube("South arrival promenade", (0, -64, 0.14), (8, 82, 0.08), mats["concrete"], 0.25)
    diamonds = (
        ((27, 0), 0.0, 72.0),
        ((-13, 24), math.radians(120), 66.0),
        ((-13, -24), math.radians(240), 72.0),
    )
    for index, (home, yaw, radius) in enumerate(diamonds):
        add_diamond(home, yaw, mats, assets, radius=radius)
        for side in (-1, 1):
            lx, ly = 8.0, side * 20.0
            cos, sin = math.cos(yaw), math.sin(yaw)
            bx = home[0] + lx * cos - ly * sin
            by = home[1] + lx * sin + ly * cos
            shared_bleacher(f"Diamond {index} spectator bleacher", (bx, by, 0.2), yaw, mats, assets)
    for index, y in enumerate((40, 47)):
        cage = root("Shared batting cage", (2, y, 0.18), 0)
        cage_parts = [cube("Batting cage lane", (0, 0, 0.05), (22, 4.5, 0.08), mats["dark_concrete"], 0.2)]
        for x in (-11, 11):
            for side in (-2.25, 2.25):
                cage_parts.append(cylinder("Batting cage post", (x, side, 2.2), 0.045, 4.4, mats["black_steel"], 8))
        cage_parts.extend([
            cylinder_between("Batting cage roof rail", (-11, -2.25, 4.4), (11, -2.25, 4.4), 0.035, mats["black_steel"], 8),
            cylinder_between("Batting cage roof rail", (-11, 2.25, 4.4), (11, 2.25, 4.4), 0.035, mats["black_steel"], 8),
        ])
        attach(cage, cage_parts)
        assets.setdefault("batting-cage.glb", cage)
    add_boundary_planting(width - 12, depth - 12, mats, 18)
    return (width, depth), assets


def sight_screen(name: str, location, mats: dict, assets: dict):
    r = root(name, location)
    parts = [cube("White sight screen", (0, 0, 2.1), (8, 0.28, 4.2), mats["white"], 0.08)]
    attach(r, parts)
    assets.setdefault("cricket-sight-screen.glb", r)
    return r


def build_cricket_green(mats: dict):
    width, depth = 190.0, 170.0
    assets = {}
    cube("Village green landscape", (0, 0, 0), (width, depth, 0.18), mats["grass"], 1.6)
    disc("Pastoral perimeter walk", (0, 0, 0.12), 79, 0.08, mats["concrete"], (1, 72 / 79, 1))
    disc("Cricket outfield", (0, 0, 0.18), 75, 0.08, mats["turf"], (1, 68.5 / 75, 1))
    stripe_width = 10.0
    for index, x in enumerate(range(-65, 66, 10)):
        if index % 2:
            half_depth = 68.5 * math.sqrt(max(0.0, 1 - (x / 75.0) ** 2))
            cube("Cricket mowing stripe", (x, 0, 0.225), (stripe_width, half_depth * 2, 0.018), mats["court_green"], 0.15)
    ellipse_line("Boundary rope", 72.5, 66.0, 0.26, 0.10, mats["white"])
    cube("Central wicket strip", (0, 0, 0.24), (22.56, 3.05, 0.08), mats["rubber_sand"], 0.12)
    for x in (-10.06, 10.06):
        for y in (-0.56, 0, 0.56): cylinder("Cricket stump", (x, y, 0.60), 0.025, 0.72, mats["timber_light"], 8)
    sight_screen("West sight screen", (-67, 0, 0.22), mats, assets)
    sight_screen("East sight screen", (67, 0, 0.22), mats, assets)
    cube("Reserved pavilion pad", (84, 0, 0.15), (15, 10, 0.08), mats["concrete"], 0.35)
    cube("Pavilion forecourt", (77, 0, 0.15), (8, 18, 0.08), mats["concrete"], 0.25)
    low_perimeter_fence(182, 158, mats, height=1.05)
    practice = root("Cricket practice nets", (58, 63, 0.2))
    practice_parts = [cube("Practice strip", (0, 0, 0.04), (22, 7, 0.08), mats["rubber_sand"], 0.2)]
    for x in (-11, 11):
        for y in (-3.5, 0, 3.5):
            practice_parts.append(cylinder("Practice net post", (x, y, 2.0), 0.045, 4.0, mats["black_steel"], 8))
    for y in (-3.5, 0, 3.5):
        practice_parts.append(cylinder_between("Practice net top rail", (-11, y, 4.0), (11, y, 4.0), 0.03, mats["black_steel"], 8))
    attach(practice, practice_parts)
    assets["cricket-practice-nets.glb"] = practice
    for x, y, scale in ((-85, -68, 1.2), (-83, 64, 1.1), (79, -66, 1.15), (-50, 75, 1.0), (45, -76, 1.1)):
        add_tree("Village green specimen tree", (x, y), scale, mats["trunk"], mats["foliage"], mats["foliage_light"])
    return (width, depth), assets


def build_mixed_complex(mats: dict):
    width, depth = 330.0, 245.0
    assets = {}
    cube("Regional sports complex lawn", (0, 0, 0), (width, depth, 0.18), mats["grass"], 2.0)
    cube("North south public promenade", (0, 0, 0.14), (9, depth - 16, 0.08), mats["concrete"], 0.25)
    cube("Cross-site service spine", (0, 0, 0.14), (width - 18, 7, 0.08), mats["dark_concrete"], 0.25)
    cube("Reserved operations pad", (0, 0, 0.18), (22, 17, 0.10), mats["concrete"], 0.35)
    for cy in (-47, 47):
        cube("Soccer warning apron", (-82, cy, 0.11), (108, 72, 0.10), mats["rubber_orange"], 0.32)
        add_soccer_field(-82, cy, 100, 64, mats, assets)
        shared_bleacher("Soccer shared bleacher", (-25, cy, 0.2), math.pi / 2, mats, assets, "sports-bleacher.glb")
        fence_rectangle(108, 72, mats, assets, "sports-field-fence.glb", height=2.4, center=(-82, cy))
        for x in (-132, -32):
            for y in (cy - 34, cy + 34):
                light = root("Tournament floodlight", (x, y, 0.2))
                attach(light, [
                    cylinder("Floodlight mast", (0, 0, 7.0), 0.12, 14.0, mats["steel"], 12),
                    cube("Floodlight bank", (0, 0, 14.0), (3.0, 0.4, 0.35), mats["white"], 0.05),
                ])
                assets.setdefault("sports-floodlight.glb", light)
    for home, yaw in (((45, 24), math.pi / 4), ((45, -24), -math.pi / 4)):
        add_diamond(home, yaw, mats, assets, radius=62, base=18.29, filename="softball-backstop.glb")
    cube("Tournament spectator walk", (-82, 0, 0.18), (116, 7, 0.08), mats["concrete"], 0.25)
    add_boundary_planting(width - 16, depth - 16, mats, 20)
    return (width, depth), assets


BUILDERS = {
    "pickleball_courts": ("pickleball-community-bank", build_pickleball),
    "running_track_oval": ("track-oval-school-athletic", build_track_oval),
    "baseball_softball_diamond": ("baseball-youth-pinwheel", build_baseball_hub),
    "cricket_pitch_oval": ("cricket-village-green", build_cricket_green),
    "sports_field_complex": ("sports-complex-tournament", build_mixed_complex),
}

GRAMMAR = {
    "pickleball_courts": {"variantId": "pickleball_courts_v1", "topology": "five_courts_plus_play_social_edge", "moduleCount": 6},
    "running_track_oval": {"variantId": "running_track_oval_v2", "topology": "oval_anchor", "moduleCount": 1},
    "baseball_softball_diamond": {"variantId": "baseball_softball_diamond_v1", "topology": "triangular_three_field_club_hub", "moduleCount": 3},
    "cricket_pitch_oval": {"variantId": "cricket_pitch_oval_v0", "topology": "oval_anchor", "moduleCount": 1},
    "sports_field_complex": {"variantId": "sports_field_complex_v0", "topology": "mixed_blocks_cross_spines", "moduleCount": 4},
}


def enrich_manifest(kit_root: Path, archetype_id: str, slug: str) -> None:
    path = kit_root / slug / "kit_manifest.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["compositionGrammar"] = GRAMMAR[archetype_id]
    payload["humanReferencePolicy"] = {
        "sourcePeopleUsedFor": [
            "approximate feature scale",
            "occupancy and use patterns",
            "circulation and desire lines",
            "spectator and social edge placement",
            "clearance, shade, visibility, and supervision cues",
        ],
        "peopleGenerated": False,
        "authorityLimit": "observational only; regulation and accessibility dimensions remain deterministic",
    }
    payload["largeBuildingInterface"] = "reserved pad and forecourt only"
    payload["fullAssembly"] = "full-park-assembly.glb"
    if archetype_id == "baseball_softball_diamond":
        payload["skinMethod"] = "multi_angle_reference_pbr_plus_metric_uv_v2"
        payload["surfaceRoles"] = [
            "mown_outfield_turf",
            "alternate_mowing_pass",
            "red_infield_clay",
            "red_warning_track",
            "concrete_forecourt",
            "planted_site_edge",
        ]
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def export_full_assembly(slug: str, builder, kit_root: Path, skin_root: Path) -> None:
    """Export the complete reviewed LEGO scene without render-only context."""
    reset_scene()
    mats = materials(skin_root, slug)
    builder(mats)
    assembly = root(f"{slug} complete park assembly")
    top_level = [obj for obj in list(bpy.context.scene.objects) if obj is not assembly and obj.parent is None]
    attach(assembly, top_level)
    export_root(assembly, kit_root / slug / "full-park-assembly.glb")


def main() -> None:
    args = parse_args()
    skin_root = (args.skin_root or (args.repo_root / "frontend/public/park-skins")).resolve()
    selected = BUILDERS if args.archetype == "all" else {args.archetype: BUILDERS[args.archetype]}
    for archetype_id, (slug, builder) in selected.items():
        render_archetype(
            archetype_id,
            slug,
            builder,
            args.output.resolve(),
            args.kit_output.resolve(),
            skin_root,
        )
        export_full_assembly(slug, builder, args.kit_output.resolve(), skin_root)
        enrich_manifest(args.kit_output.resolve(), archetype_id, slug)


if __name__ == "__main__":
    main()
