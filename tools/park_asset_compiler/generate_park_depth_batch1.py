"""Generate three catalogue-referenced park depth kits for later pilots.

This is a bounded staging batch. It exports metric GLBs and multi-angle QA
renders, but deliberately does not register the assets in the live viewer.

Run from the repository root:

    blender --background --factory-startup --python \
      tools/park_asset_compiler/generate_park_depth_batch1.py -- \
      --asset-dir assets/park-depth-kits/staging \
      --preview-dir artifacts/park-depth-kit-batch1
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from park_mesh_utils import (
    asset_metrics,
    assign,
    box,
    cylinder,
    export_glb,
    join_by_material,
    look_at,
    material,
    reset_scene,
    torus,
    tube_between,
)


DEFAULT_REFERENCE_SPEC = Path(__file__).with_name("park_depth_batch1_reference_spec.json")
KIT_ORDER = ("tennis_court_cluster", "skate_park", "dog_park")


def args_after_double_dash() -> list[str]:
    return sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--asset-dir", type=Path, required=True)
    parser.add_argument("--preview-dir", type=Path, required=True)
    parser.add_argument("--reference-spec", type=Path, default=DEFAULT_REFERENCE_SPEC)
    parser.add_argument("--only", choices=KIT_ORDER, action="append")
    parser.add_argument("--validate-references-only", action="store_true")
    return parser.parse_args(args_after_double_dash())


def load_reference_spec(path: Path) -> dict:
    spec = json.loads(path.read_text(encoding="utf-8"))
    if spec.get("batch_id") != "park_depth_kits_batch1":
        raise RuntimeError(f"Unexpected park depth batch spec: {path}")
    repository_root = Path(__file__).resolve().parents[2]
    kits = spec.get("kits", [])
    if [kit.get("archetype_id") for kit in kits] != list(KIT_ORDER):
        raise RuntimeError("Reference spec must contain the exact bounded three-kit batch")
    missing: list[Path] = []
    for kit in kits:
        views = kit.get("views", [])
        if len(views) < 3:
            raise RuntimeError(f"{kit['archetype_id']} needs at least three reference angles")
        root = repository_root / kit["catalogue_root"]
        missing.extend(candidate for candidate in (root / view for view in views) if not candidate.is_file())
        if kit.get("surface_mode") not in {"depth_only", "sculptural_overlay"}:
            raise RuntimeError(f"Unknown surface mode for {kit['archetype_id']}")
    if missing:
        raise RuntimeError("Missing catalogue references:\n" + "\n".join(f"  - {path}" for path in missing))
    print(f"[park-depth-batch1] references: {len(kits)} kits, {sum(len(k['views']) for k in kits)} images")
    return spec


def mesh_object(name: str, vertices: list[tuple[float, float, float]], faces: list[tuple[int, ...]], mat):
    mesh = bpy.data.meshes.new(f"{name}Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    assign(obj, mat)
    return obj


def wedge(name: str, width: float, length: float, height: float,
          location: tuple[float, float, float], mat, *, yaw: float = 0.0):
    x = width / 2
    y = length / 2
    vertices = [
        (-x, -y, 0), (x, -y, 0), (x, y, 0), (-x, y, 0),
        (-x, y, height), (x, y, height),
    ]
    faces = [(0, 1, 2, 3), (3, 2, 5, 4), (0, 4, 5, 1), (0, 3, 4), (1, 5, 2)]
    obj = mesh_object(name, vertices, faces, mat)
    obj.location = location
    obj.rotation_euler[2] = yaw
    return obj


def quarter_pipe(name: str, width: float, run: float, height: float,
                 location: tuple[float, float, float], mat, *, yaw: float = 0.0):
    segments = 14
    vertices: list[tuple[float, float, float]] = []
    for side in (-width / 2, width / 2):
        for index in range(segments + 1):
            t = index / segments
            vertices.append((side, -run / 2 + run * t, height * t * t))
    faces = []
    stride = segments + 1
    for index in range(segments):
        faces.append((index, index + 1, stride + index + 1, stride + index))
    obj = mesh_object(name, vertices, faces, mat)
    obj.location = location
    obj.rotation_euler[2] = yaw
    return obj


def elliptical_bowl(name: str, radius_x: float, radius_y: float, rim_height: float,
                    location: tuple[float, float, float], concrete, corten, floor_mat, coping_mat):
    radial_segments = 12
    angular_segments = 64
    vertices = [(0.0, 0.0, 0.05)]
    for ring in range(1, radial_segments + 1):
        t = ring / radial_segments
        wall_t = max(0.0, (t - 0.30) / 0.70)
        z = 0.05 + rim_height * (wall_t ** 1.35)
        for index in range(angular_segments):
            angle = math.tau * index / angular_segments
            vertices.append((math.cos(angle) * radius_x * t, math.sin(angle) * radius_y * t, z))
    faces: list[tuple[int, ...]] = []
    for index in range(angular_segments):
        faces.append((0, 1 + index, 1 + (index + 1) % angular_segments))
    for ring in range(1, radial_segments):
        inner = 1 + (ring - 1) * angular_segments
        outer = 1 + ring * angular_segments
        for index in range(angular_segments):
            nxt = (index + 1) % angular_segments
            faces.append((inner + index, outer + index, outer + nxt, inner + nxt))
    bowl = mesh_object(name, vertices, faces, concrete)
    bowl.location = location
    for polygon in bowl.data.polygons:
        polygon.use_smooth = True

    floor_vertices = [(0.0, 0.0, 0.065)]
    for index in range(angular_segments):
        angle = math.tau * index / angular_segments
        floor_vertices.append((math.cos(angle) * radius_x * 0.30, math.sin(angle) * radius_y * 0.30, 0.065))
    floor_faces = [
        (0, 1 + index, 1 + (index + 1) % angular_segments)
        for index in range(angular_segments)
    ]
    floor = mesh_object(f"{name}GraphicFloor", floor_vertices, floor_faces, floor_mat)
    floor.location = location
    rim_vertices = []
    rim_faces = []
    for z in (0.0, rim_height + 0.12):
        for index in range(angular_segments):
            angle = math.tau * index / angular_segments
            rim_vertices.append((math.cos(angle) * (radius_x + 0.16), math.sin(angle) * (radius_y + 0.16), z))
    for index in range(angular_segments):
        nxt = (index + 1) % angular_segments
        rim_faces.append((index, nxt, angular_segments + nxt, angular_segments + index))
    skirt = mesh_object(f"{name}CortenSkirt", rim_vertices, rim_faces, corten)
    skirt.location = location
    coping = []
    for index in range(angular_segments):
        angle_a = math.tau * index / angular_segments
        angle_b = math.tau * (index + 1) / angular_segments
        start = (
            location[0] + math.cos(angle_a) * radius_x,
            location[1] + math.sin(angle_a) * radius_y,
            location[2] + rim_height + 0.08,
        )
        end = (
            location[0] + math.cos(angle_b) * radius_x,
            location[1] + math.sin(angle_b) * radius_y,
            location[2] + rim_height + 0.08,
        )
        coping.append(tube_between(f"{name}Coping{index}", start, end, 0.045, coping_mat, vertices=6))
    return [bowl, skirt, floor, *coping]


def fence_run(name: str, start: tuple[float, float], end: tuple[float, float], height: float,
              mat, wire_mat, *, post_spacing: float = 4.0, windscreen=None) -> list:
    objects = []
    a = Vector((start[0], start[1], 0.0))
    b = Vector((end[0], end[1], 0.0))
    direction = b - a
    length = direction.length
    count = max(1, math.ceil(length / post_spacing))
    unit = direction.normalized()
    for index in range(count + 1):
        point = a + direction * (index / count)
        objects.append(cylinder(f"{name}Post{index}", 0.045, height, (point.x, point.y, height / 2), mat, vertices=10))
    for z in (0.12, height - 0.1):
        objects.append(tube_between(f"{name}Rail{z}", (a.x, a.y, z), (b.x, b.y, z), 0.032, mat, vertices=8))
    normal = Vector((-unit.y, unit.x, 0.0))
    for index in range(count):
        p0 = a + direction * (index / count)
        p1 = a + direction * ((index + 1) / count)
        for step in range(1, 6):
            t = step / 6
            base = p0.lerp(p1, t)
            objects.append(tube_between(
                f"{name}Wire{index}_{step}",
                (base.x, base.y, 0.12),
                (base.x, base.y, height - 0.1),
                0.009,
                wire_mat,
                vertices=5,
            ))
        if windscreen is not None:
            midpoint = (p0 + p1) * 0.5 + normal * 0.018
            panel = box(
                f"{name}Windscreen{index}",
                ((p1 - p0).length - 0.08, 0.025, min(1.35, height - 0.3)),
                (midpoint.x, midpoint.y, min(1.35, height - 0.3) / 2 + 0.25),
                windscreen,
                rotation=(0.0, 0.0, math.atan2(unit.y, unit.x)),
            )
            objects.append(panel)
    return objects


def tennis_net(name: str, center: tuple[float, float], yaw: float, mats: dict) -> list:
    objects = []
    half_width = 6.4
    cos = math.cos(yaw)
    sin = math.sin(yaw)
    def place(local_x: float, local_y: float, z: float) -> tuple[float, float, float]:
        return (center[0] + local_x * cos - local_y * sin, center[1] + local_x * sin + local_y * cos, z)
    for side in (-half_width, half_width):
        objects.append(cylinder(f"{name}Post{side}", 0.045, 1.12, place(side, 0, 0.56), mats["steel"], vertices=10))
    objects.append(tube_between(f"{name}Top", place(-half_width, 0, 1.06), place(half_width, 0, 1.06), 0.018, mats["net"], vertices=6))
    for index in range(17):
        x = -half_width + index * (half_width * 2 / 16)
        objects.append(tube_between(f"{name}Drop{index}", place(x, 0, 0.08), place(x, 0, 1.04), 0.006, mats["net"], vertices=5))
    return objects


def bench(name: str, location: tuple[float, float, float], yaw: float, mats: dict) -> list:
    objects = [box(f"{name}Seat", (2.8, 0.42, 0.10), (location[0], location[1], location[2] + 0.52), mats["aluminum"], rotation=(0, 0, yaw))]
    for offset in (-1.05, 1.05):
        dx = math.cos(yaw) * offset
        dy = math.sin(yaw) * offset
        objects.append(cylinder(f"{name}Leg{offset}", 0.045, 0.52, (location[0] + dx, location[1] + dy, location[2] + 0.26), mats["steel"], vertices=8))
    return objects


def floodlight(name: str, location: tuple[float, float, float], yaw: float, mats: dict) -> list:
    objects = []
    objects.append(cylinder(f"{name}Pole", 0.09, 10.0, (location[0], location[1], 5.0), mats["steel"], vertices=12))
    cross_dir = Vector((math.cos(yaw), math.sin(yaw), 0.0))
    a = Vector(location) + cross_dir * -1.15 + Vector((0, 0, 9.85))
    b = Vector(location) + cross_dir * 1.15 + Vector((0, 0, 9.85))
    objects.append(tube_between(f"{name}Bar", tuple(a), tuple(b), 0.055, mats["steel"], vertices=8))
    for index, offset in enumerate((-0.75, 0.0, 0.75)):
        point = Vector(location) + cross_dir * offset + Vector((0, 0, 10.0))
        objects.append(box(f"{name}Lamp{index}", (0.34, 0.22, 0.18), tuple(point), mats["light"], rotation=(0.1, 0, yaw)))
    return objects


def build_tennis(mats: dict) -> tuple[list, tuple[float, float], tuple[float, float, float]]:
    objects = []
    court_x = (-10.145, 10.145)
    court_y = (-19.79, 19.79)
    for ix, x in enumerate(court_x):
        for iy, y in enumerate(court_y):
            objects.extend(tennis_net(f"TennisNet{ix}_{iy}", (x, y), 0.0, mats))
            objects.extend(bench(f"TennisBench{ix}_{iy}", (x + (-8.2 if ix == 0 else 8.2), y, 0), math.pi / 2, mats))
    half_x = 20.5
    half_y = 38.5
    objects.extend(fence_run("TennisWest", (-half_x, -half_y), (-half_x, half_y), 3.05, mats["green_steel"], mats["wire"], windscreen=mats["windscreen"]))
    objects.extend(fence_run("TennisEast", (half_x, -half_y), (half_x, half_y), 3.05, mats["green_steel"], mats["wire"], windscreen=mats["windscreen"]))
    objects.extend(fence_run("TennisSouth", (-half_x, -half_y), (half_x, -half_y), 3.05, mats["green_steel"], mats["wire"]))
    objects.extend(fence_run("TennisNorth", (-half_x, half_y), (half_x, half_y), 3.05, mats["green_steel"], mats["wire"]))
    objects.extend(fence_run("TennisDivider", (0, -half_y), (0, half_y), 1.25, mats["green_steel"], mats["wire"]))
    for index, (x, y) in enumerate(((-19, -25), (-19, 0), (-19, 25), (19, -25), (19, 0), (19, 25))):
        objects.extend(floodlight(f"TennisLight{index}", (x, y, 0), math.pi / 2, mats))
    return objects, (42.0, 78.0), (10.0, -19.8, 0.8)


def rail(name: str, start: tuple[float, float, float], end: tuple[float, float, float], mats: dict) -> list:
    objects = [tube_between(f"{name}Top", start, end, 0.055, mats["steel"], vertices=10)]
    for index, point in enumerate((start, end)):
        objects.append(tube_between(f"{name}Leg{index}", (point[0], point[1], 0.0), point, 0.045, mats["steel"], vertices=8))
    return objects


def build_skate(mats: dict) -> tuple[list, tuple[float, float], tuple[float, float, float]]:
    objects = []
    objects.extend(elliptical_bowl("SkateBowlWest", 8.5, 6.5, 2.2, (-13.0, 8.0, 0.0), mats["concrete"], mats["corten"], mats["skate_graphic"], mats["steel"]))
    objects.extend(elliptical_bowl("SkateBowlEast", 7.0, 5.5, 1.9, (12.5, 8.5, 0.0), mats["concrete"], mats["corten"], mats["skate_graphic"], mats["steel"]))
    objects.append(quarter_pipe("SkateQuarterWest", 8.0, 7.0, 2.5, (-16.0, -9.0, 0.02), mats["concrete"], yaw=math.pi / 2))
    objects.append(quarter_pipe("SkateQuarterEast", 7.0, 6.0, 2.1, (16.0, -8.0, 0.02), mats["concrete"], yaw=-math.pi / 2))
    objects.append(wedge("SkateBankCenter", 9.0, 7.0, 1.5, (0.0, -8.0, 0.02), mats["concrete"], yaw=math.pi))
    objects.append(box("SkateLedgeWest", (7.0, 1.0, 0.55), (-8.0, -1.0, 0.275), mats["concrete"]))
    objects.append(box("SkateLedgeEast", (6.0, 0.8, 0.45), (9.0, -2.0, 0.225), mats["concrete"]))
    for index, (y, width) in enumerate(((-4.5, 8.0), (-5.8, 6.5), (-7.0, 5.0))):
        objects.append(box(f"SkateStep{index}", (width, 1.1, 0.22 + index * 0.22), (0.0, y, (0.22 + index * 0.22) / 2), mats["concrete"]))
    objects.extend(rail("SkateRailCenter", (-5.0, -3.2, 0.62), (5.0, -3.2, 0.62), mats))
    objects.extend(rail("SkateRailSouth", (-13.0, -14.0, 0.48), (-3.0, -14.0, 0.48), mats))
    objects.extend(rail("SkateRailEast", (8.0, -12.0, 0.52), (17.0, -12.0, 0.52), mats))
    for index, (size, location) in enumerate((((52, 0.25, 1.2), (0, -20.0, 0.6)), ((52, 0.25, 1.2), (0, 20.0, 0.6)), ((0.25, 40, 1.2), (-25.0, 0, 0.6)), ((0.25, 40, 1.2), (25.0, 0, 0.6)))):
        objects.append(box(f"SkateCortenEdge{index}", size, location, mats["corten"]))
    return objects, (52.0, 42.0), (-13.0, 8.0, 0.8)


def welded_fence_run(name: str, start: tuple[float, float], end: tuple[float, float], mats: dict, *, height=1.8) -> list:
    return fence_run(name, start, end, height, mats["black_steel"], mats["black_wire"], post_spacing=2.5)


def shade_canopy(name: str, location: tuple[float, float, float], mats: dict) -> list:
    x, y, _ = location
    objects = [cylinder(f"{name}Post", 0.11, 3.1, (x, y, 1.55), mats["black_steel"], vertices=12)]
    objects.append(box(f"{name}Roof", (4.2, 4.2, 0.12), (x, y, 3.15), mats["canopy"], rotation=(0.0, 0.12, 0.12)))
    for offset in (-1.5, -0.5, 0.5, 1.5):
        objects.append(box(f"{name}Slat{offset}", (0.18, 4.0, 0.05), (x + offset, y, 3.24), mats["black_steel"], rotation=(0.0, 0.12, 0.12)))
    return objects


def agility_tunnel(name: str, location: tuple[float, float, float], mats: dict) -> list:
    objects = []
    x, y, z = location
    for index in range(8):
        objects.append(torus(f"{name}Rib{index}", 0.8, 0.07, (x - 2.1 + index * 0.6, y, z + 0.82), mats["steel"], rotation=(0, math.pi / 2, 0)))
    return objects


def build_dog(mats: dict) -> tuple[list, tuple[float, float], tuple[float, float, float]]:
    objects = []
    half_x, half_y = 20.5, 14.5
    objects.extend(welded_fence_run("DogWest", (-half_x, -half_y), (-half_x, half_y), mats))
    objects.extend(welded_fence_run("DogEast", (half_x, -half_y), (half_x, half_y), mats))
    objects.extend(welded_fence_run("DogSouth", (-half_x, -half_y), (half_x, -half_y), mats))
    objects.extend(welded_fence_run("DogNorth", (-half_x, half_y), (half_x, half_y), mats))
    objects.extend(welded_fence_run("DogDivider", (2.5, -half_y), (2.5, half_y), mats))
    for name, x in (("Large", -10.0), ("Small", 10.0)):
        objects.extend(welded_fence_run(f"Dog{name}VestibuleWest", (x - 2, -half_y), (x - 2, -11.5), mats))
        objects.extend(welded_fence_run(f"Dog{name}VestibuleEast", (x + 2, -half_y), (x + 2, -11.5), mats))
        objects.extend(welded_fence_run(f"Dog{name}VestibuleNorth", (x - 2, -11.5), (x + 2, -11.5), mats))
    for index, location in enumerate(((-12.0, 7.5, 0), (8.5, 7.0, 0), (15.0, -5.0, 0))):
        objects.extend(shade_canopy(f"DogCanopy{index}", location, mats))
    objects.append(wedge("DogAgilityRampSouth", 2.8, 5.0, 1.4, (-9.0, -2.5, 0.02), mats["turf"]))
    objects.append(wedge("DogAgilityRampNorth", 2.8, 5.0, 1.4, (-9.0, 2.5, 0.02), mats["turf"], yaw=math.pi))
    objects.extend(agility_tunnel("DogTunnel", (9.0, 0.0, 0), mats))
    for index, location in enumerate(((-15.5, 10.5, 0), (14.0, 10.5, 0), (-15.0, -9.0, 0), (15.0, -9.0, 0))):
        objects.extend(bench(f"DogBench{index}", location, 0.0, mats))
    for index, (x, y) in enumerate(((-18, -12), (-5, -12), (5, -12), (18, -12), (-1, 2), (14, 3))):
        objects.append(cylinder(f"DogBollard{index}", 0.09, 0.85, (x, y, 0.425), mats["bollard"], vertices=12))
        objects.append(box(f"DogBollardLight{index}", (0.15, 0.15, 0.10), (x, y, 0.78), mats["light"]))
    return objects, (42.0, 30.0), (-9.0, 2.5, 0.8)


def create_materials() -> dict:
    return {
        "steel": material("Galvanized Steel", (0.22, 0.26, 0.27, 1), metallic=0.72, roughness=0.35),
        "green_steel": material("Tennis Green Steel", (0.035, 0.18, 0.10, 1), metallic=0.58, roughness=0.42),
        "wire": material("Tennis Wire", (0.10, 0.24, 0.15, 1), metallic=0.52, roughness=0.48),
        "windscreen": material("Navy Windscreen", (0.025, 0.08, 0.16, 1), roughness=0.8),
        "net": material("Sports Net", (0.86, 0.88, 0.84, 1), roughness=0.92),
        "aluminum": material("Bleacher Aluminum", (0.62, 0.67, 0.68, 1), metallic=0.8, roughness=0.28),
        "light": material("LED Lens", (0.78, 0.88, 0.84, 1), roughness=0.2, emission=(0.72, 0.84, 0.78, 1)),
        "concrete": material("Skate Concrete", (0.48, 0.49, 0.47, 1), roughness=0.82),
        "corten": material("Corten Steel", (0.34, 0.11, 0.045, 1), metallic=0.45, roughness=0.64),
        "skate_graphic": material("Skate Bowl Graphic", (0.055, 0.06, 0.065, 1), roughness=0.94),
        "black_steel": material("Dog Park Black Steel", (0.035, 0.045, 0.05, 1), metallic=0.7, roughness=0.34),
        "black_wire": material("Dog Park Welded Wire", (0.08, 0.09, 0.09, 1), metallic=0.6, roughness=0.42),
        "canopy": material("Perforated Canopy", (0.13, 0.14, 0.13, 1), metallic=0.55, roughness=0.45),
        "turf": material("Agility Turf", (0.16, 0.35, 0.11, 1), roughness=0.9),
        "bollard": material("Lit Bollard", (0.11, 0.10, 0.09, 1), metallic=0.55, roughness=0.42),
        "preview_blue": material("Preview Court Blue", (0.08, 0.28, 0.48, 1), roughness=0.84),
        "preview_green": material("Preview Court Green", (0.12, 0.32, 0.16, 1), roughness=0.9),
        "preview_dark": material("Preview Skate Asphalt", (0.055, 0.06, 0.065, 1), roughness=0.94),
        "preview_path": material("Preview Dog Path", (0.48, 0.34, 0.22, 1), roughness=0.92),
        "preview_grass": material("Preview Dog Turf", (0.12, 0.29, 0.09, 1), roughness=0.95),
        "preview_line": material("Preview Line", (0.92, 0.93, 0.88, 1), roughness=0.7),
    }


def add_preview_surface(archetype_id: str, mats: dict) -> None:
    if archetype_id == "tennis_court_cluster":
        box("PreviewTennisApron", (42.0, 78.0, 0.06), (0, 0, -0.04), mats["preview_green"])
        for x in (-10.145, 10.145):
            for y in (-19.79, 19.79):
                box(f"PreviewCourt{x}_{y}", (18.29, 36.58, 0.035), (x, y, 0.0), mats["preview_blue"])
                for dx in (-5.485, 5.485):
                    box(f"PreviewSide{dx}_{x}_{y}", (0.055, 23.77, 0.012), (x + dx, y, 0.035), mats["preview_line"])
                for dy in (-11.885, 0, 11.885):
                    box(f"PreviewBase{dy}_{x}_{y}", (10.97, 0.055, 0.012), (x, y + dy, 0.035), mats["preview_line"])
    elif archetype_id == "skate_park":
        box("PreviewSkateMask", (52.0, 42.0, 0.06), (0, 0, -0.04), mats["preview_dark"])
    else:
        box("PreviewDogMask", (42.0, 30.0, 0.06), (0, 0, -0.04), mats["preview_grass"])
        box("PreviewDogPath", (39.0, 3.0, 0.025), (0, -10.5, 0.005), mats["preview_path"])


def configure_scene() -> None:
    scene = bpy.context.scene
    for engine in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "BLENDER_WORKBENCH"):
        try:
            scene.render.engine = engine
            break
        except TypeError:
            continue
    scene.render.image_settings.file_format = "PNG"
    scene.render.resolution_percentage = 100
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.075, 0.09, 0.105, 1)
    background.inputs["Strength"].default_value = 0.32
    bpy.ops.object.light_add(type="AREA", location=(-18, -24, 36))
    key = bpy.context.object
    key.data.energy = 1900
    key.data.shape = "DISK"
    key.data.size = 18
    look_at(key)
    bpy.ops.object.light_add(type="AREA", location=(24, 16, 22))
    fill = bpy.context.object
    fill.data.energy = 1100
    fill.data.size = 14
    look_at(fill)
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 30))
    sun = bpy.context.object
    sun.rotation_euler = (math.radians(28), math.radians(-18), math.radians(34))
    sun.data.energy = 1.8


def render_qa(archetype_id: str, preview_dir: Path, footprint: tuple[float, float], detail_target: tuple[float, float, float]) -> None:
    output = preview_dir / archetype_id
    output.mkdir(parents=True, exist_ok=True)
    configure_scene()
    scene = bpy.context.scene
    maximum = max(footprint)
    bpy.ops.object.camera_add(location=(maximum * 0.70, -maximum * 0.78, maximum * 0.58))
    camera = bpy.context.object
    camera.data.lens = 54
    look_at(camera, (0, 0, 1.2))
    scene.camera = camera
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 900
    scene.render.filepath = str(output / "overview.png")
    bpy.ops.render.render(write_still=True)

    camera.location = (0, 0, maximum * 1.15)
    camera.rotation_euler = (0, 0, 0)
    look_at(camera, (0, 0, 0))
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = maximum * 1.08
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 1000
    scene.render.filepath = str(output / "top.png")
    bpy.ops.render.render(write_still=True)

    camera.data.type = "PERSP"
    camera.data.lens = 60
    target = Vector(detail_target)
    detail_offset = Vector((24, -27, 16)) if archetype_id == "skate_park" else Vector((15, -18, 11))
    camera.location = target + detail_offset
    look_at(camera, target)
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 900
    scene.render.filepath = str(output / "detail.png")
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output / f"{archetype_id}_qa.blend"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    args = parse_args()
    args.asset_dir = args.asset_dir.resolve()
    args.preview_dir = args.preview_dir.resolve()
    args.reference_spec = args.reference_spec.resolve()
    spec = load_reference_spec(args.reference_spec)
    if args.validate_references_only:
        return
    selected = set(args.only or KIT_ORDER)
    builders = {
        "tennis_court_cluster": build_tennis,
        "skate_park": build_skate,
        "dog_park": build_dog,
    }
    records = []
    for kit_spec in spec["kits"]:
        archetype_id = kit_spec["archetype_id"]
        if archetype_id not in selected:
            continue
        reset_scene()
        mats = create_materials()
        objects, footprint, detail_target = builders[archetype_id](mats)
        joined = join_by_material(objects, archetype_id)
        height, triangles = asset_metrics(joined)
        filename = f"{kit_spec['variant_id'].replace('_', '-')}-depth-kit.glb"
        path = args.asset_dir / filename
        export_glb(path, joined)
        add_preview_surface(archetype_id, mats)
        render_qa(archetype_id, args.preview_dir, footprint, detail_target)
        record = {
            "archetype_id": archetype_id,
            "variant_id": kit_spec["variant_id"],
            "status": "staging_not_integrated",
            "file": filename,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "triangles": triangles,
            "mesh_parts": len(joined),
            "height_m": round(height, 3),
            "footprint_m": list(footprint),
            "surface_mode": kit_spec["surface_mode"],
            "metric_scale": 1.0,
            "ground_contact_origin_z_m": 0.0,
            "reference_views": kit_spec["views"],
        }
        records.append(record)
        print(f"[park-depth-batch1] {archetype_id}: {path} ({triangles} triangles, {path.stat().st_size} bytes)")
    args.asset_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": 1,
        "batch_id": spec["batch_id"],
        "status": "staging_not_integrated",
        "assets": records,
    }
    (args.asset_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"[park-depth-batch1] manifest: {args.asset_dir / 'manifest.json'}")


if __name__ == "__main__":
    main()
