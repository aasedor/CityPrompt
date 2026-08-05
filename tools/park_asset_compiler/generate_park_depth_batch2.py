"""Generate the second bounded catalogue-referenced park depth-kit batch.

The runtime GLBs contain only raised program elements. Ground color, paving,
planting texture, court-like markings, and wet-surface graphics remain the AI
drape's responsibility. QA renders add clearly separated preview surfaces only
after each GLB has been exported.

Run from the repository root:

    blender --background --factory-startup --python \
      tools/park_asset_compiler/generate_park_depth_batch2.py -- \
      --asset-dir assets/park-depth-kits/staging-batch2 \
      --preview-dir docs/park-depth-kit-batch2
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

from generate_park_depth_batch1 import bench, mesh_object, wedge
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


DEFAULT_REFERENCE_SPEC = Path(__file__).with_name("park_depth_batch2_reference_spec.json")
KIT_ORDER = ("inclusive_playground", "community_garden", "splash_pad_area")


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
    if spec.get("batch_id") != "park_depth_kits_batch2":
        raise RuntimeError(f"Unexpected park depth batch spec: {path}")
    kits = spec.get("kits", [])
    if [kit.get("archetype_id") for kit in kits] != list(KIT_ORDER):
        raise RuntimeError("Reference spec must contain the exact bounded three-kit batch")
    contract = spec.get("modeling_contract", {})
    if contract.get("runtime_glb_includes_draped_ground_surface") is not False:
        raise RuntimeError("Runtime GLBs must not duplicate the AI-draped ground surface")
    repository_root = Path(__file__).resolve().parents[2]
    missing: list[Path] = []
    for kit in kits:
        if len(kit.get("views", [])) != 3:
            raise RuntimeError(f"{kit['archetype_id']} needs base, 60-degree and 90-degree references")
        root = repository_root / kit["catalogue_root"]
        missing.extend(root / view for view in kit["views"] if not (root / view).is_file())
        if kit.get("runtime_surface") != "ai_drape":
            raise RuntimeError(f"{kit['archetype_id']} must retain the AI drape as its ground surface")
    if missing:
        raise RuntimeError("Missing catalogue references:\n" + "\n".join(f"  - {item}" for item in missing))
    print(f"[park-depth-batch2] references: 3 kits, 9 catalogue images")
    return spec


def cone(
    name: str,
    radius1: float,
    radius2: float,
    depth: float,
    location: tuple[float, float, float],
    mat,
    *,
    vertices: int = 16,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
):
    bpy.ops.mesh.primitive_cone_add(
        vertices=vertices,
        radius1=radius1,
        radius2=radius2,
        depth=depth,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    assign(obj, mat)
    return obj


def low_sphere(
    name: str,
    radius: float,
    location: tuple[float, float, float],
    mat,
    *,
    scale: tuple[float, float, float] = (1.0, 1.0, 1.0),
):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=radius, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(obj, mat)
    return obj


def arc_tube(
    name: str,
    center: tuple[float, float, float],
    radius: float,
    start_angle: float,
    end_angle: float,
    tube_radius: float,
    mat,
    *,
    segments: int = 24,
) -> list:
    objects = []
    for index in range(segments):
        a = start_angle + (end_angle - start_angle) * index / segments
        b = start_angle + (end_angle - start_angle) * (index + 1) / segments
        p0 = (center[0] + math.cos(a) * radius, center[1], center[2] + math.sin(a) * radius)
        p1 = (center[0] + math.cos(b) * radius, center[1], center[2] + math.sin(b) * radius)
        objects.append(tube_between(f"{name}{index:02d}", p0, p1, tube_radius, mat, vertices=10))
    return objects


def local_to_world(
    location: tuple[float, float, float],
    yaw: float,
    local: tuple[float, float, float],
) -> tuple[float, float, float]:
    return (
        location[0] + local[0] * math.cos(yaw) - local[1] * math.sin(yaw),
        location[1] + local[0] * math.sin(yaw) + local[1] * math.cos(yaw),
        location[2] + local[2],
    )


def accessible_ramp(
    name: str,
    width: float,
    length: float,
    rise: float,
    location: tuple[float, float, float],
    yaw: float,
    mats: dict,
) -> list:
    objects = [wedge(f"{name}Deck", width, length, rise, location, mats["deck"], yaw=yaw)]
    for side in (-width / 2 + 0.15, width / 2 - 0.15):
        rail_start = local_to_world(location, yaw, (side, -length / 2, 0.75))
        rail_end = local_to_world(location, yaw, (side, length / 2, rise + 0.75))
        objects.append(tube_between(f"{name}Rail{side}", rail_start, rail_end, 0.04, mats["steel"], vertices=10))
        for step in range(5):
            t = step / 4
            local_y = -length / 2 + length * t
            z = rise * t
            base = local_to_world(location, yaw, (side, local_y, z))
            top = local_to_world(location, yaw, (side, local_y, z + 0.75))
            objects.append(tube_between(f"{name}Post{side}_{step}", base, top, 0.035, mats["steel"], vertices=8))
    return objects


def gable_roof(name: str, location: tuple[float, float, float], mats: dict) -> list:
    x, y, z = location
    angle = math.radians(24)
    return [
        box(f"{name}West", (2.2, 4.2, 0.14), (x - 0.82, y, z), mats["roof"], rotation=(0.0, -angle, 0.0)),
        box(f"{name}East", (2.2, 4.2, 0.14), (x + 0.82, y, z), mats["roof"], rotation=(0.0, angle, 0.0)),
    ]


def play_tower(name: str, location: tuple[float, float, float], mats: dict) -> list:
    x, y, _ = location
    objects = []
    for dx in (-1.45, 1.45):
        for dy in (-1.45, 1.45):
            objects.append(cylinder(f"{name}Post{dx}_{dy}", 0.12, 4.0, (x + dx, y + dy, 2.0), mats["timber"], vertices=12))
    objects.append(box(f"{name}Platform", (3.2, 3.2, 0.18), (x, y, 1.35), mats["deck"]))
    objects.append(box(f"{name}BackPanel", (3.0, 0.12, 1.4), (x, y + 1.42, 2.05), mats["green"]))
    objects.append(box(f"{name}SidePanel", (0.12, 3.0, 1.4), (x - 1.42, y, 2.05), mats["blue"]))
    objects.extend(gable_roof(f"{name}Roof", (x, y, 4.15), mats))
    return objects


def slide(name: str, start: tuple[float, float, float], end: tuple[float, float, float], mats: dict) -> list:
    a = Vector(start)
    b = Vector(end)
    direction = b - a
    midpoint = (a + b) * 0.5
    yaw = math.atan2(direction.y, direction.x)
    pitch = -math.atan2(direction.z, math.hypot(direction.x, direction.y))
    length = direction.length
    objects = [box(f"{name}Bed", (length, 1.15, 0.18), tuple(midpoint), mats["slide"], rotation=(0.0, pitch, yaw))]
    normal = Vector((-math.sin(yaw), math.cos(yaw), 0.0))
    for side in (-0.52, 0.52):
        offset = normal * side
        objects.append(tube_between(f"{name}Rail{side}", tuple(a + offset + Vector((0, 0, 0.22))), tuple(b + offset + Vector((0, 0, 0.22))), 0.035, mats["steel"], vertices=8))
    return objects


def adaptive_swings(mats: dict) -> list:
    objects = []
    for x in (-20.0, -12.0):
        objects.append(tube_between(f"SwingLeg{x}A", (x, -12.8, 0.0), (x, -10.0, 4.0), 0.10, mats["timber"], vertices=12))
        objects.append(tube_between(f"SwingLeg{x}B", (x, -7.2, 0.0), (x, -10.0, 4.0), 0.10, mats["timber"], vertices=12))
    objects.append(tube_between("SwingTop", (-20.0, -10.0, 4.0), (-12.0, -10.0, 4.0), 0.11, mats["steel"], vertices=12))
    for index, x in enumerate((-18.5, -16.0, -13.5)):
        for chain_x in (x - 0.28, x + 0.28):
            objects.append(tube_between(f"SwingChain{index}_{chain_x}", (chain_x, -10.0, 3.92), (chain_x, -10.0, 1.35), 0.018, mats["steel"], vertices=6))
        objects.append(box(f"SwingSeat{index}", (0.78, 0.55, 0.12), (x, -10.0, 1.28), mats["green"]))
        if index < 2:
            objects.append(box(f"SwingBack{index}", (0.78, 0.12, 0.75), (x, -10.23, 1.62), mats["green"]))
    return objects


def spinner(location: tuple[float, float, float], mats: dict) -> list:
    x, y, _ = location
    objects = [cylinder("SpinnerDeck", 3.0, 0.18, (x, y, 0.12), mats["spinner"], vertices=32)]
    objects.append(cylinder("SpinnerHub", 0.18, 1.25, (x, y, 0.72), mats["steel"], vertices=12))
    objects.append(torus("SpinnerOuterRail", 2.65, 0.045, (x, y, 0.95), mats["steel"]))
    for index in range(6):
        angle = math.tau * index / 6
        outer = (x + math.cos(angle) * 2.65, y + math.sin(angle) * 2.65, 0.95)
        objects.append(tube_between(f"SpinnerSpoke{index}", (x, y, 0.95), outer, 0.035, mats["steel"], vertices=8))
    return objects


def sensory_panel(name: str, location: tuple[float, float, float], yaw: float, mats: dict) -> list:
    x, y, _ = location
    objects = []
    for offset in (-1.25, 1.25):
        dx = math.cos(yaw) * offset
        dy = math.sin(yaw) * offset
        objects.append(cylinder(f"{name}Post{offset}", 0.09, 1.8, (x + dx, y + dy, 0.9), mats["timber"], vertices=10))
    objects.append(box(f"{name}Panel", (2.3, 0.12, 1.15), (x, y, 1.15), mats["blue"], rotation=(0, 0, yaw)))
    for index in range(5):
        dx = math.cos(yaw) * (-0.8 + index * 0.4)
        dy = math.sin(yaw) * (-0.8 + index * 0.4)
        objects.append(cylinder(f"{name}Dial{index}", 0.13, 0.08, (x + dx, y + dy, 1.2), mats["yellow"], vertices=12, rotation=(math.pi / 2, 0, yaw)))
    return objects


def shade_canopy(name: str, location: tuple[float, float, float], mats: dict) -> list:
    x, y, _ = location
    objects = []
    for dx in (-2.4, 2.4):
        objects.append(cylinder(f"{name}Post{dx}", 0.10, 3.0, (x + dx, y, 1.5), mats["steel"], vertices=12))
    objects.append(box(f"{name}Roof", (5.4, 3.4, 0.13), (x, y, 3.1), mats["canopy"], rotation=(0.0, 0.10, 0.0)))
    return objects


def build_playground(mats: dict) -> tuple[list, tuple[float, float], tuple[float, float, float]]:
    objects = []
    objects.extend(accessible_ramp("MainRamp", 3.2, 13.0, 1.35, (0.0, -7.0, 0.02), 0.0, mats))
    objects.append(box("CentralDeck", (8.0, 4.0, 0.20), (0.0, 1.5, 1.35), mats["deck"]))
    for x in (-3.7, 3.7):
        objects.append(tube_between(f"CentralDeckRail{x}", (x, -0.4, 2.1), (x, 3.4, 2.1), 0.04, mats["steel"], vertices=10))
    objects.extend(play_tower("TowerWest", (-5.0, 5.5, 0.0), mats))
    objects.extend(play_tower("TowerEast", (3.5, 5.5, 0.0), mats))
    objects.append(box("TowerBridge", (5.5, 2.0, 0.20), (-0.75, 5.5, 1.35), mats["deck"]))
    objects.extend(slide("WestSlide", (-7.0, 5.5, 1.38), (-11.5, 5.5, 0.15), mats))
    objects.extend(slide("EastSlide", (5.2, 5.5, 1.38), (10.0, 6.5, 0.15), mats))
    objects.extend(adaptive_swings(mats))
    objects.extend(spinner((16.0, -9.0, 0.0), mats))
    objects.extend(sensory_panel("SensoryWest", (-12.0, 11.0, 0.0), 0.0, mats))
    objects.extend(sensory_panel("SensoryEast", (14.0, 8.5, 0.0), math.pi / 2, mats))
    objects.extend(shade_canopy("CanopyNorthWest", (-15.0, 15.0, 0.0), mats))
    objects.extend(shade_canopy("CanopyNorthEast", (14.5, 15.0, 0.0), mats))
    for index, location in enumerate(((-16.0, 16.2, 0.0), (15.0, 16.2, 0.0), (20.0, 4.0, 0.0))):
        objects.extend(bench(f"PlayBench{index}", location, 0.0, mats))
    return objects, (50.0, 40.0), (0.0, 3.0, 1.2)


def timber_fence_run(name: str, start: tuple[float, float], end: tuple[float, float], mats: dict) -> list:
    objects = []
    a = Vector((start[0], start[1], 0.0))
    b = Vector((end[0], end[1], 0.0))
    direction = b - a
    length = direction.length
    count = max(1, math.ceil(length / 4.0))
    for index in range(count + 1):
        point = a.lerp(b, index / count)
        objects.append(cylinder(f"{name}Post{index}", 0.10, 1.45, (point.x, point.y, 0.725), mats["garden_timber"], vertices=10))
    for z in (0.55, 1.2):
        objects.append(tube_between(f"{name}Rail{z}", (a.x, a.y, z), (b.x, b.y, z), 0.075, mats["garden_timber"], vertices=8))
    return objects


def raised_bed(name: str, location: tuple[float, float, float], crop_index: int, mats: dict) -> list:
    x, y, _ = location
    width, length, wall = 3.8, 4.5, 0.22
    objects = [
        box(f"{name}West", (wall, length, 0.65), (x - width / 2, y, 0.325), mats["garden_timber"]),
        box(f"{name}East", (wall, length, 0.65), (x + width / 2, y, 0.325), mats["garden_timber"]),
        box(f"{name}South", (width - wall * 2, wall, 0.65), (x, y - length / 2, 0.325), mats["garden_timber"]),
        box(f"{name}North", (width - wall * 2, wall, 0.65), (x, y + length / 2, 0.325), mats["garden_timber"]),
        box(f"{name}Soil", (width - wall * 2, length - wall * 2, 0.18), (x, y, 0.48), mats["soil"]),
    ]
    crop_mat = mats[("crop_green", "crop_light", "crop_red")[crop_index % 3]]
    for row in range(2):
        for col in range(3):
            px = x - 1.05 + col * 1.05
            py = y - 1.25 + row * 2.5
            objects.append(low_sphere(f"{name}Crop{row}_{col}", 0.34, (px, py, 0.78), crop_mat, scale=(1.0, 1.0, 0.75)))
    return objects


def trellis(name: str, location: tuple[float, float, float], mats: dict) -> list:
    x, y, _ = location
    objects = []
    for dx in (-1.3, 1.3):
        objects.append(cylinder(f"{name}Post{dx}", 0.055, 2.1, (x + dx, y, 1.05), mats["garden_timber"], vertices=8))
    objects.append(tube_between(f"{name}Top", (x - 1.3, y, 2.0), (x + 1.3, y, 2.0), 0.05, mats["garden_timber"], vertices=8))
    for index in range(5):
        px = x - 1.0 + index * 0.5
        objects.append(tube_between(f"{name}String{index}", (px, y, 0.55), (px, y, 1.95), 0.012, mats["steel"], vertices=5))
    return objects


def greenhouse(location: tuple[float, float, float], mats: dict) -> list:
    x, y, _ = location
    width, length, wall_height, ridge_height = 8.0, 6.0, 3.0, 4.5
    objects = []
    for dx in (-width / 2, width / 2):
        for dy in (-length / 2, length / 2):
            objects.append(box(f"GreenhousePost{dx}_{dy}", (0.14, 0.14, wall_height), (x + dx, y + dy, wall_height / 2), mats["garden_timber"]))
    for dy in (-length / 2, length / 2):
        objects.append(tube_between(f"GreenhouseEave{dy}W", (x - width / 2, y + dy, wall_height), (x + width / 2, y + dy, wall_height), 0.07, mats["garden_timber"], vertices=8))
        objects.append(tube_between(f"GreenhouseRoof{dy}W", (x - width / 2, y + dy, wall_height), (x, y + dy, ridge_height), 0.07, mats["garden_timber"], vertices=8))
        objects.append(tube_between(f"GreenhouseRoof{dy}E", (x, y + dy, ridge_height), (x + width / 2, y + dy, wall_height), 0.07, mats["garden_timber"], vertices=8))
    objects.append(tube_between("GreenhouseRidge", (x, y - length / 2, ridge_height), (x, y + length / 2, ridge_height), 0.08, mats["garden_timber"], vertices=8))
    objects.append(box("GreenhouseGlassWest", (0.06, length - 0.2, wall_height - 0.2), (x - width / 2, y, wall_height / 2), mats["glass"]))
    objects.append(box("GreenhouseGlassEast", (0.06, length - 0.2, wall_height - 0.2), (x + width / 2, y, wall_height / 2), mats["glass"]))
    objects.append(box("GreenhouseGlassNorth", (width - 0.2, 0.06, wall_height - 0.2), (x, y + length / 2, wall_height / 2), mats["glass"]))
    roof_angle = math.atan2(ridge_height - wall_height, width / 2)
    roof_span = math.hypot(width / 2, ridge_height - wall_height)
    objects.append(box("GreenhouseGlassRoofWest", (roof_span, length - 0.2, 0.06), (x - width / 4, y, (wall_height + ridge_height) / 2), mats["glass"], rotation=(0.0, -roof_angle, 0.0)))
    objects.append(box("GreenhouseGlassRoofEast", (roof_span, length - 0.2, 0.06), (x + width / 4, y, (wall_height + ridge_height) / 2), mats["glass"], rotation=(0.0, roof_angle, 0.0)))
    return objects


def build_garden(mats: dict) -> tuple[list, tuple[float, float], tuple[float, float, float]]:
    objects = []
    for row, y in enumerate((-12.0, -4.0, 4.0, 12.0)):
        for column, x in enumerate((-16.0, -8.0, 0.0, 8.0, 16.0)):
            objects.extend(raised_bed(f"GardenBed{row}_{column}", (x, y, 0.0), row * 5 + column, mats))
    for index, location in enumerate(((-16.0, -12.0, 0.0), (0.0, 4.0, 0.0), (8.0, 12.0, 0.0))):
        objects.extend(trellis(f"GardenTrellis{index}", location, mats))
    objects.extend(greenhouse((17.0, 19.0, 0.0), mats))
    half = 24.0
    objects.extend(timber_fence_run("GardenWest", (-half, -half), (-half, half), mats))
    objects.extend(timber_fence_run("GardenEast", (half, -half), (half, half), mats))
    objects.extend(timber_fence_run("GardenSouth", (-half, -half), (half, -half), mats))
    objects.extend(timber_fence_run("GardenNorth", (-half, half), (half, half), mats))
    for index, location in enumerate(((-18.5, 18.5, 0.0), (-18.5, -18.5, 0.0))):
        objects.extend(bench(f"GardenBench{index}", location, math.pi / 2, mats))
        objects.append(low_sphere(f"GardenBoulder{index}A", 0.9, (location[0] + 2.0, location[1], 0.55), mats["stone"], scale=(1.4, 1.0, 0.75)))
    for index, x in enumerate((13.0, 16.0, 19.0)):
        objects.append(box(f"CompostBin{index}", (2.2, 2.2, 1.2), (x, -20.5, 0.6), mats["compost"]))
    objects.append(cylinder("RainBarrel", 0.65, 1.5, (11.5, 19.0, 0.75), mats["barrel"], vertices=16))
    return objects, (50.0, 50.0), (17.0, 19.0, 1.8)


def tipping_bucket(location: tuple[float, float, float], mats: dict) -> list:
    x, y, _ = location
    objects = []
    for dx in (-2.1, 2.1):
        objects.append(cylinder(f"BucketTowerPost{dx}", 0.10, 5.7, (x + dx, y, 2.85), mats["copper"], vertices=14))
    objects.append(tube_between("BucketTowerTop", (x - 2.1, y, 5.65), (x + 2.1, y, 5.65), 0.10, mats["copper"], vertices=12))
    objects.append(box("BucketSplashTray", (4.7, 2.7, 0.18), (x, y, 3.25), mats["green"], rotation=(0.08, 0.0, 0.0)))
    objects.append(cone("TippingBucket", 1.15, 0.82, 1.8, (x, y, 5.0), mats["bucket"], vertices=24, rotation=(0.18, 0.0, -0.12)))
    objects.append(tube_between("BucketPivot", (x - 1.35, y, 5.0), (x + 1.35, y, 5.0), 0.07, mats["steel"], vertices=10))
    return objects


def shower_arm(location: tuple[float, float, float], mats: dict) -> list:
    x, y, _ = location
    objects = [tube_between("ShowerStem", (x, y, 0.0), (x, y, 3.7), 0.11, mats["copper"], vertices=14)]
    objects.append(tube_between("ShowerBendA", (x, y, 3.7), (x + 0.8, y, 4.25), 0.11, mats["copper"], vertices=14))
    objects.append(tube_between("ShowerBendB", (x + 0.8, y, 4.25), (x + 1.7, y, 4.25), 0.11, mats["copper"], vertices=14))
    objects.append(cone("ShowerBowl", 0.55, 0.18, 0.45, (x + 1.7, y, 4.0), mats["green"], vertices=18, rotation=(math.pi, 0, 0)))
    return objects


def mushroom_sprayer(name: str, location: tuple[float, float, float], mats: dict) -> list:
    x, y, _ = location
    return [
        cylinder(f"{name}Stem", 0.09, 1.25, (x, y, 0.625), mats["steel"], vertices=12),
        cone(f"{name}Cap", 0.72, 0.18, 0.32, (x, y, 1.35), mats["green"], vertices=20),
    ]


def build_splash(mats: dict) -> tuple[list, tuple[float, float], tuple[float, float, float]]:
    objects = []
    objects.extend(tipping_bucket((-7.0, 6.5, 0.0), mats))
    objects.extend(arc_tube("SprayArch", (2.0, 0.0, 0.0), 4.5, 0.0, math.pi, 0.14, mats["copper"], segments=28))
    objects.extend(shower_arm((-10.5, -4.5, 0.0), mats))
    objects.extend(mushroom_sprayer("MushroomEast", (8.5, 5.5, 0.0), mats))
    objects.extend(mushroom_sprayer("MushroomSouth", (8.0, -6.5, 0.0), mats))
    for index, (x, y) in enumerate(((-7.0, -7.5), (-3.0, -5.0), (3.0, -7.0), (6.0, 1.0), (-1.0, 6.0), (10.0, 1.0))):
        objects.append(cylinder(f"GroundJet{index}", 0.12, 0.16, (x, y, 0.08), mats["steel"], vertices=16))
        objects.append(torus(f"GroundJetRing{index}", 0.22, 0.025, (x, y, 0.16), mats["green"]))
    for index, location in enumerate(((-13.0, 8.5, 0.0), (12.0, 8.5, 0.0), (12.0, -9.0, 0.0))):
        objects.extend(bench(f"SplashBench{index}", location, math.pi / 2, mats))
    return objects, (30.0, 25.0), (-7.0, 6.5, 2.8)


def create_materials() -> dict:
    mats = {
        "steel": material("Brushed Stainless Steel", (0.46, 0.50, 0.51, 1), metallic=0.78, roughness=0.28),
        "timber": material("Play Timber", (0.38, 0.21, 0.09, 1), roughness=0.78),
        "deck": material("Accessible Timber Deck", (0.48, 0.31, 0.14, 1), roughness=0.76),
        "roof": material("Pale Canopy Roof", (0.72, 0.67, 0.57, 1), roughness=0.58),
        "green": material("Play Green", (0.24, 0.58, 0.12, 1), roughness=0.58),
        "blue": material("Play Blue", (0.08, 0.28, 0.58, 1), roughness=0.58),
        "yellow": material("Play Yellow", (0.95, 0.60, 0.05, 1), roughness=0.54),
        "slide": material("Slide Stainless Steel", (0.56, 0.60, 0.61, 1), metallic=0.82, roughness=0.24),
        "spinner": material("Spinner Green", (0.44, 0.72, 0.10, 1), roughness=0.48),
        "canopy": material("Shade Fabric", (0.37, 0.35, 0.29, 1), roughness=0.82),
        "aluminum": material("Bench Aluminum", (0.62, 0.67, 0.68, 1), metallic=0.80, roughness=0.28),
        "garden_timber": material("Garden Rough Timber", (0.39, 0.22, 0.10, 1), roughness=0.88),
        "soil": material("Raised Bed Soil", (0.16, 0.075, 0.025, 1), roughness=0.97),
        "crop_green": material("Leaf Crop Green", (0.07, 0.28, 0.055, 1), roughness=0.93),
        "crop_light": material("Leaf Crop Light", (0.28, 0.48, 0.08, 1), roughness=0.93),
        "crop_red": material("Leaf Crop Red", (0.32, 0.08, 0.055, 1), roughness=0.93),
        "glass": material("Greenhouse Glass", (0.52, 0.68, 0.63, 0.55), metallic=0.05, roughness=0.18),
        "stone": material("Garden Boulder", (0.43, 0.39, 0.31, 1), roughness=0.96),
        "compost": material("Compost Bin", (0.12, 0.07, 0.025, 1), roughness=0.92),
        "barrel": material("Rain Barrel", (0.16, 0.29, 0.32, 1), roughness=0.72),
        "copper": material("Splash Copper", (0.34, 0.13, 0.06, 1), metallic=0.68, roughness=0.32),
        "bucket": material("Rainbow Tipping Bucket", (0.84, 0.18, 0.08, 1), metallic=0.18, roughness=0.45),
        "preview_rubber": material("Preview Rubber Blue", (0.08, 0.30, 0.48, 1), roughness=0.92),
        "preview_rubber_green": material("Preview Rubber Green", (0.35, 0.55, 0.20, 1), roughness=0.92),
        "preview_rubber_orange": material("Preview Rubber Orange", (0.76, 0.31, 0.08, 1), roughness=0.92),
        "preview_gravel": material("Preview Garden Gravel", (0.51, 0.39, 0.24, 1), roughness=0.96),
        "preview_meadow": material("Preview Meadow", (0.25, 0.42, 0.12, 1), roughness=0.96),
        "preview_splash_tan": material("Preview Splash Tan", (0.65, 0.50, 0.32, 1), roughness=0.88),
        "preview_water": material("Preview Water", (0.12, 0.62, 0.88, 1), roughness=0.18, emission=(0.08, 0.45, 0.75, 1)),
    }
    return mats


def add_preview_surface(archetype_id: str, mats: dict) -> None:
    if archetype_id == "inclusive_playground":
        box("PreviewPlaygroundMask", (50.0, 40.0, 0.06), (0, 0, -0.04), mats["preview_rubber"])
        for index, (x, y, radius, mat) in enumerate(((-15, -10, 6, mats["preview_rubber_orange"]), (16, -9, 5, mats["preview_rubber_green"]), (0, 5, 8, mats["preview_rubber_green"]), (14, 9, 5, mats["preview_rubber_orange"]))):
            cylinder(f"PreviewPlayZone{index}", radius, 0.025, (x, y, 0.01), mat, vertices=40)
        box("PreviewAccessiblePath", (4.6, 30.0, 0.025), (0, -4.0, 0.02), mats["preview_gravel"])
    elif archetype_id == "community_garden":
        box("PreviewGardenMask", (50.0, 50.0, 0.06), (0, 0, -0.04), mats["preview_meadow"])
        box("PreviewGardenPaths", (44.0, 38.0, 0.025), (0, -1.0, 0.01), mats["preview_gravel"])
    else:
        box("PreviewSplashMask", (30.0, 25.0, 0.06), (0, 0, -0.04), mats["preview_splash_tan"])
        cylinder("PreviewSplashBlueCenter", 8.5, 0.025, (1.5, 0.0, 0.01), mats["preview_rubber"], vertices=48)
        cylinder("PreviewSplashTanInset", 4.8, 0.028, (7.0, -5.5, 0.025), mats["preview_splash_tan"], vertices=40)


def add_splash_water_preview(mats: dict) -> None:
    for index, (x, y, height) in enumerate(((-7.0, -7.5, 1.4), (-3.0, -5.0, 1.8), (3.0, -7.0, 1.2), (6.0, 1.0, 1.6), (-1.0, 6.0, 1.4))):
        tube_between(f"PreviewJet{index}", (x, y, 0.18), (x, y, height), 0.035, mats["preview_water"], vertices=6)
    for index in range(11):
        angle = math.pi * index / 10
        source = (2.0 + math.cos(angle) * 4.25, 0.0, math.sin(angle) * 4.25)
        target = (2.0, 0.0, 1.8)
        tube_between(f"PreviewArchSpray{index}", source, target, 0.025, mats["preview_water"], vertices=5)


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
    background.inputs["Strength"].default_value = 0.34
    bpy.ops.object.light_add(type="AREA", location=(-18, -24, 36))
    key = bpy.context.object
    key.data.energy = 1900
    key.data.shape = "DISK"
    key.data.size = 18
    look_at(key)
    bpy.ops.object.light_add(type="AREA", location=(24, 16, 22))
    fill = bpy.context.object
    fill.data.energy = 1000
    fill.data.size = 14
    look_at(fill)
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 30))
    sun = bpy.context.object
    sun.rotation_euler = (math.radians(28), math.radians(-18), math.radians(34))
    sun.data.energy = 1.8


def render_qa(
    archetype_id: str,
    preview_dir: Path,
    footprint: tuple[float, float],
    detail_target: tuple[float, float, float],
    mats: dict,
) -> None:
    output = preview_dir
    output.mkdir(parents=True, exist_ok=True)
    if archetype_id == "splash_pad_area":
        add_splash_water_preview(mats)
    configure_scene()
    scene = bpy.context.scene
    maximum = max(footprint)
    bpy.ops.object.camera_add(location=(maximum * 0.72, -maximum * 0.80, maximum * 0.60))
    camera = bpy.context.object
    camera.data.lens = 54
    look_at(camera, (0, 0, 1.2))
    scene.camera = camera
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 900
    scene.render.filepath = str(output / f"{archetype_id}_overview.png")
    bpy.ops.render.render(write_still=True)

    camera.location = (0, 0, maximum * 1.18)
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = maximum * 1.08
    look_at(camera, (0, 0, 0))
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 1000
    scene.render.filepath = str(output / f"{archetype_id}_top.png")
    bpy.ops.render.render(write_still=True)

    camera.data.type = "PERSP"
    camera.data.lens = 62
    target = Vector(detail_target)
    detail_offset = Vector((14, -17, 10)) if archetype_id != "community_garden" else Vector((13, -15, 9))
    camera.location = target + detail_offset
    look_at(camera, target)
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 900
    scene.render.filepath = str(output / f"{archetype_id}_detail.png")
    bpy.ops.render.render(write_still=True)


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
        "inclusive_playground": build_playground,
        "community_garden": build_garden,
        "splash_pad_area": build_splash,
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
        render_qa(archetype_id, args.preview_dir, footprint, detail_target, mats)
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
            "runtime_glb_includes_draped_ground_surface": False,
            "reference_views": kit_spec["views"],
        }
        records.append(record)
        print(f"[park-depth-batch2] {archetype_id}: {path} ({triangles} triangles, {path.stat().st_size} bytes)")
    args.asset_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": 1,
        "batch_id": spec["batch_id"],
        "status": "staging_not_integrated",
        "assets": records,
    }
    (args.asset_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"[park-depth-batch2] manifest: {args.asset_dir / 'manifest.json'}")


if __name__ == "__main__":
    main()
