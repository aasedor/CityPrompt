"""Build the fixed metric 3D object kit for Neighborhood Park v0 in Blender.

The five exported GLBs are whole, non-scalable identity objects. Their PBR
materials use the exact-reference intrinsic Sticker Method skin prepared by
``prepare_assets.py``; silhouettes, openings, rails, seats and structural
members remain physical geometry.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Callable

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_OUTPUT = REPO_ROOT / "frontend" / "public" / "park-kits" / "neighborhood-park-rustic-v0"
SKIN_ROOT = REPO_ROOT / "frontend" / "public" / "park-skins" / "neighborhood-park-rustic-v0" / "adaptive-v1"
REFERENCE = REPO_ROOT / "frontend" / "public" / "archetypes" / "openspaces" / "neighborhood-park" / "variant_0.png"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--pilot", action="store_true", help="Build pavilion and tower only.")
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(argv)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.images,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for block in list(collection):
            if block.users == 0:
                collection.remove(block)


def intrinsic_material(
    name: str,
    role: str,
    tint: tuple[float, float, float, float],
    *,
    roughness: float,
    metallic: float = 0.0,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = tint
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    links.new(shader.outputs["BSDF"], output.inputs["Surface"])

    role_dir = SKIN_ROOT / role
    albedo_path = role_dir / "albedo.jpg"
    if albedo_path.exists():
        albedo = nodes.new("ShaderNodeTexImage")
        albedo.image = bpy.data.images.load(str(albedo_path), check_existing=True)
        albedo.image.colorspace_settings.name = "sRGB"
        multiply = nodes.new("ShaderNodeMixRGB")
        multiply.blend_type = "MULTIPLY"
        multiply.inputs[0].default_value = 1.0
        multiply.inputs[2].default_value = tint
        links.new(albedo.outputs["Color"], multiply.inputs[1])
        links.new(multiply.outputs["Color"], shader.inputs["Base Color"])

        rough_path = role_dir / "roughness.jpg"
        if rough_path.exists():
            rough = nodes.new("ShaderNodeTexImage")
            rough.image = bpy.data.images.load(str(rough_path), check_existing=True)
            rough.image.colorspace_settings.name = "Non-Color"
            links.new(rough.outputs["Color"], shader.inputs["Roughness"])

        normal_path = role_dir / "normal.png"
        if normal_path.exists():
            normal = nodes.new("ShaderNodeTexImage")
            normal.image = bpy.data.images.load(str(normal_path), check_existing=True)
            normal.image.colorspace_settings.name = "Non-Color"
            normal_map = nodes.new("ShaderNodeNormalMap")
            normal_map.inputs["Strength"].default_value = 0.42
            links.new(normal.outputs["Color"], normal_map.inputs["Color"])
            links.new(normal_map.outputs["Normal"], shader.inputs["Normal"])
    else:
        shader.inputs["Base Color"].default_value = tint
    material["sticker_role"] = role
    material["source_reference"] = "neighborhood-park/variant_0.png"
    material["printed_geometry_forbidden"] = True
    return material


def materials() -> dict[str, bpy.types.Material]:
    return {
        "timber": intrinsic_material("Weathered rough-hewn timber", "timber", (0.83, 0.70, 0.56, 1), roughness=0.9),
        "timber_dark": intrinsic_material("Dark weathered timber", "timber", (0.48, 0.38, 0.29, 1), roughness=0.93),
        "roof": intrinsic_material("Weathered timber roof", "timber", (0.60, 0.52, 0.45, 1), roughness=0.87),
        "stone": intrinsic_material("Natural park stone", "stone", (0.76, 0.77, 0.72, 1), roughness=0.96),
        "metal": intrinsic_material("Dark galvanized fittings", "metal", (0.20, 0.22, 0.21, 1), roughness=0.58, metallic=0.55),
        "rope": intrinsic_material("Natural rope", "rope", (0.48, 0.39, 0.28, 1), roughness=0.98),
    }


def own(obj: bpy.types.Object, semantic: str, material_role: str) -> bpy.types.Object:
    obj["sticker_owner"] = "neighborhood_park_v0"
    obj["semantic_role"] = semantic
    obj["material_role"] = material_role
    obj["fixed_metric_object"] = True
    obj["nonuniform_scaling_allowed"] = False
    return obj


def assign(obj: bpy.types.Object, material: bpy.types.Material) -> bpy.types.Object:
    obj.data.materials.append(material)
    return obj


def metric_uv(obj: bpy.types.Object, metres_per_tile: float = 2.0) -> None:
    if obj.type != "MESH":
        return
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    try:
        bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.015)
    finally:
        bpy.ops.object.mode_set(mode="OBJECT")
    uv = obj.data.uv_layers.active
    if uv:
        for entry in uv.data:
            entry.uv.x /= metres_per_tile
            entry.uv.y /= metres_per_tile


def box(
    name: str,
    size: tuple[float, float, float],
    location: tuple[float, float, float],
    material: bpy.types.Material,
    semantic: str,
    role: str,
    *,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    bevel: float = 0.025,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(own(obj, semantic, role), material)
    if bevel:
        modifier = obj.modifiers.new("Construction edge", "BEVEL")
        modifier.width = bevel
        modifier.segments = 1
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    metric_uv(obj)
    return obj


def cylinder(
    name: str,
    radius: float,
    depth: float,
    location: tuple[float, float, float],
    material: bpy.types.Material,
    semantic: str,
    role: str,
    *,
    vertices: int = 12,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    assign(own(obj, semantic, role), material)
    metric_uv(obj)
    return obj


def tube_between(
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    radius: float,
    material: bpy.types.Material,
    semantic: str,
    role: str,
    *,
    vertices: int = 10,
) -> bpy.types.Object:
    first = Vector(start)
    last = Vector(end)
    direction = last - first
    obj = cylinder(name, radius, direction.length, tuple((first + last) * 0.5), material, semantic, role, vertices=vertices)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = direction.to_track_quat("Z", "Y")
    bpy.context.view_layer.update()
    return obj


def beam_between(
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    width: float,
    depth: float,
    material: bpy.types.Material,
    semantic: str,
    role: str,
) -> bpy.types.Object:
    first = Vector(start)
    last = Vector(end)
    direction = last - first
    obj = box(name, (direction.length, width, depth), tuple((first + last) * 0.5), material, semantic, role, bevel=0.02)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = direction.to_track_quat("X", "Z")
    bpy.context.view_layer.update()
    return obj


def build_pavilion(mats: dict[str, bpy.types.Material]) -> None:
    for x in (-3.35, 0.0, 3.35):
        for y in (-2.20, 2.20):
            cylinder(f"Pavilion post {x} {y}", 0.16, 3.0, (x, y, 1.5), mats["timber_dark"], "timber_pavilion_post", "timber", vertices=12)
    for y in (-2.20, 2.20):
        beam_between(f"Pavilion eave beam {y}", (-3.55, y, 2.9), (3.55, y, 2.9), 0.20, 0.24, mats["timber_dark"], "timber_pavilion_eave", "timber")
        tube_between(f"Pavilion gable left {y}", (-3.55, y, 2.92), (0, y, 4.18), 0.11, mats["timber_dark"], "timber_pavilion_truss", "timber")
        tube_between(f"Pavilion gable right {y}", (0, y, 4.18), (3.55, y, 2.92), 0.11, mats["timber_dark"], "timber_pavilion_truss", "timber")
    tube_between("Pavilion ridge", (0, -2.75, 4.18), (0, 2.75, 4.18), 0.12, mats["timber_dark"], "timber_pavilion_ridge", "timber")
    slope = math.atan2(1.30, 3.85)
    for side in (-1, 1):
        box(
            f"Pavilion roof plane {side}",
            (4.15, 5.80, 0.16),
            (side * 1.92, 0, 3.54),
            mats["roof"],
            "timber_pavilion_roof",
            "roof",
            rotation=(0, -side * slope, 0),
            bevel=0.025,
        )
    # One real picnic table makes the pavilion visibly occupied without people.
    for index, y in enumerate((-0.42, -0.14, 0.14, 0.42)):
        box(f"Picnic tabletop slat {index}", (3.15, 0.20, 0.10), (0, y, 0.78), mats["timber"], "pavilion_picnic_table", "timber", bevel=0.018)
    for side in (-1, 1):
        box(f"Picnic bench {side}", (2.85, 0.34, 0.11), (0, side * 0.86, 0.49), mats["timber"], "pavilion_picnic_bench", "timber", bevel=0.018)
    for x in (-0.95, 0.95):
        for side in (-1, 1):
            tube_between(f"Picnic leg {x} {side}", (x, side * 0.68, 0.05), (x, side * 0.20, 0.73), 0.055, mats["metal"], "pavilion_picnic_frame", "metal")


def build_tower_slide(mats: dict[str, bpy.types.Material]) -> None:
    posts = [(-1.1, -1.0, 4.0), (-1.1, 1.0, 4.15), (1.1, -1.0, 4.35), (1.1, 1.0, 4.2)]
    for index, (x, y, height) in enumerate(posts):
        cylinder(f"Tower log post {index}", 0.15, height, (x, y, height / 2), mats["timber_dark"], "timber_climbing_tower_post", "timber", vertices=11)
    box("Tower lower deck", (2.55, 2.35, 0.18), (0, 0, 1.55), mats["timber"], "timber_climbing_tower_deck", "timber")
    box("Tower upper deck", (1.30, 2.35, 0.18), (0.62, 0, 2.40), mats["timber"], "timber_climbing_tower_deck", "timber")
    for z in (2.05, 2.78):
        for y in (-1.02, 1.02):
            beam_between(f"Tower guard {z} {y}", (-1.0, y, z), (1.0, y, z), 0.09, 0.10, mats["timber_dark"], "timber_climbing_tower_guard", "timber")
    for x in (-1.02, 1.02):
        for y in (-1.02, 1.02):
            tube_between(f"Tower rail post {x} {y}", (x, y, 1.55), (x, y, 2.85), 0.055, mats["timber_dark"], "timber_climbing_tower_guard", "timber")
    # Low climbing ramp and tall slide are distinct whole pieces.
    beam_between("Timber climbing ramp", (-3.4, 0, 0.18), (-1.15, 0, 1.55), 1.05, 0.17, mats["timber"], "timber_climbing_ramp", "timber")
    for step in range(6):
        t = (step + 1) / 7
        x = -3.4 + (-1.15 + 3.4) * t
        z = 0.18 + (1.55 - 0.18) * t + 0.08
        box(f"Ramp cleat {step}", (0.11, 1.08, 0.09), (x, 0, z), mats["timber_dark"], "timber_climbing_ramp_cleat", "timber", rotation=(0, -0.55, 0), bevel=0.01)
    beam_between("Timber slide bed", (1.08, 0, 2.42), (4.25, 0, 0.20), 0.88, 0.14, mats["timber"], "timber_slide", "timber")
    for y in (-0.48, 0.48):
        tube_between(f"Slide side rail {y}", (1.08, y, 2.58), (4.25, y, 0.36), 0.065, mats["timber_dark"], "timber_slide_edge", "timber")


def build_swing(mats: dict[str, bpy.types.Material]) -> None:
    for x in (-2.25, 2.25):
        tube_between(f"Swing leg front {x}", (x - math.copysign(0.55, x), -1.35, 0), (x, 0, 3.15), 0.11, mats["timber_dark"], "timber_swing_frame", "timber")
        tube_between(f"Swing leg rear {x}", (x - math.copysign(0.55, x), 1.35, 0), (x, 0, 3.15), 0.11, mats["timber_dark"], "timber_swing_frame", "timber")
    beam_between("Swing top beam", (-2.55, 0, 3.18), (2.55, 0, 3.18), 0.22, 0.22, mats["timber_dark"], "timber_swing_top_beam", "timber")
    for seat_x in (-0.92, 0.92):
        for chain_y in (-0.29, 0.29):
            tube_between(f"Swing rope {seat_x} {chain_y}", (seat_x, chain_y, 3.08), (seat_x, chain_y, 0.82), 0.018, mats["rope"], "timber_swing_rope", "rope", vertices=8)
        box(f"Swing seat {seat_x}", (0.62, 0.72, 0.09), (seat_x, 0, 0.77), mats["timber"], "timber_swing_seat", "timber", bevel=0.025)


def build_fence(mats: dict[str, bpy.types.Material]) -> None:
    for x, tilt in ((-2.0, -0.08), (2.0, 0.09)):
        cylinder(f"Fence post {x}", 0.10, 1.55, (x, 0, 0.74), mats["timber_dark"], "split_rail_fence_post", "timber", vertices=9, rotation=(0, tilt, 0.04))
    tube_between("Fence lower rail", (-2.12, 0, 0.57), (2.12, 0, 0.75), 0.075, mats["timber"], "split_rail_fence_rail", "timber", vertices=9)
    tube_between("Fence upper rail", (-2.12, 0, 1.02), (2.12, 0, 1.22), 0.078, mats["timber"], "split_rail_fence_rail", "timber", vertices=9)


def build_boulders(mats: dict[str, bpy.types.Material]) -> None:
    boulders = [(-1.15, -0.30, 0.70, (1.35, 0.90, 0.62)), (0.20, 0.20, 0.55, (1.05, 0.82, 0.56)), (1.22, -0.18, 0.42, (0.84, 0.68, 0.44)), (-0.25, 0.95, 0.35, (0.72, 0.60, 0.38))]
    for index, (x, y, z, scale) in enumerate(boulders):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1, location=(x, y, z))
        obj = bpy.context.object
        obj.name = f"Natural boulder {index}"
        obj.scale = scale
        obj.rotation_euler = (index * 0.17, index * 0.11, index * 0.57)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        assign(own(obj, "natural_boulder", "stone"), mats["stone"])
        metric_uv(obj, 2.4)


BUILDERS: tuple[tuple[str, str, str, Callable[[dict[str, bpy.types.Material]], None]], ...] = (
    ("timber_pavilion", "rustic-timber-pavilion.glb", "timber_pavilion", build_pavilion),
    ("timber_climbing_tower_with_slide", "timber-climbing-tower-slide.glb", "timber_climbing_tower_with_slide", build_tower_slide),
    ("timber_swing_frame", "timber-swing-frame.glb", "timber_swing_frame", build_swing),
    ("split_rail_fence", "split-rail-fence-section.glb", "split_rail_fence", build_fence),
    ("natural_boulder_group", "natural-boulder-group.glb", "natural_boulder_group", build_boulders),
)


def export_asset(output: Path, builder: Callable[[dict[str, bpy.types.Material]], None]) -> tuple[int, list[float]]:
    reset_scene()
    builder(materials())
    objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not objects:
        raise RuntimeError(f"builder produced no mesh for {output}")
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.export_scene.gltf(
        filepath=str(output),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_extras=True,
        export_materials="EXPORT",
    )
    minimum = Vector((math.inf, math.inf, math.inf))
    maximum = Vector((-math.inf, -math.inf, -math.inf))
    for obj in objects:
        for corner in obj.bound_box:
            point = obj.matrix_world @ Vector(corner)
            minimum.x = min(minimum.x, point.x)
            minimum.y = min(minimum.y, point.y)
            minimum.z = min(minimum.z, point.z)
            maximum.x = max(maximum.x, point.x)
            maximum.y = max(maximum.y, point.y)
            maximum.z = max(maximum.z, point.z)
    return len(objects), [round(maximum[index] - minimum[index], 4) for index in range(3)]


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    selected = BUILDERS[:2] if args.pilot else BUILDERS
    assets: dict[str, dict[str, object]] = {}
    for asset_id, filename, semantic, builder in selected:
        path = output_dir / filename
        object_count, dimensions = export_asset(path, builder)
        assets[asset_id] = {
            "file": filename,
            "semantic": semantic,
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
            "meshObjectCount": object_count,
            "dimensionsM": dimensions,
            "metricScale": 1.0,
            "nonuniformScalingAllowed": False,
        }
        print(f"wrote {path} ({object_count} mesh objects)")

    manifest = {
        "schemaVersion": 1,
        "archetypeId": "neighborhood_park",
        "variantId": "neighborhood_park_v0",
        "slug": "neighborhood-park-rustic-v0",
        "method": "sticker_method_site_adaptive_whole_program",
        "reference": {
            "path": "frontend/public/archetypes/openspaces/neighborhood-park/variant_0.png",
            "sha256": sha256(REFERENCE),
        },
        "canonicalSiteM": [100.0, 80.0],
        "fixedProgramEnvelopeM": [50.0, 38.0],
        "skin": "park-skins/neighborhood-park-rustic-v0/adaptive-v1",
        "surfaceOwner": "park_ground_profile_plus_fixed_sticker_assembly",
        "assets": assets,
    }
    (output_dir / "kit_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {output_dir / 'kit_manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
