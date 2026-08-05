"""Generate the metric SiteForge basketball-court pilot kit with Blender.

Run from the repository root:

    blender --background --factory-startup --python \
      tools/park_asset_compiler/generate_basketball_kit.py -- \
      --output-dir frontend/public/park-kits \
      --preview-dir artifacts/park-kit-pilot/basketball

The GLBs are intentionally small, texture-free PBR assets. Court surfacing and
linework belong to the AI drape; these models provide only fixed vertical
program elements.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


HOOP_TOP_M = 3.95
FENCE_HEIGHT_M = 3.05
FLOODLIGHT_HEIGHT_M = 12.35
DEFAULT_REFERENCE_SPEC = Path(__file__).with_name("basketball_court_reference_spec.json")


def args_after_double_dash() -> list[str]:
    return sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--preview-dir", type=Path, required=True)
    parser.add_argument("--reference-spec", type=Path, default=DEFAULT_REFERENCE_SPEC)
    parser.add_argument("--validate-references-only", action="store_true")
    return parser.parse_args(args_after_double_dash())


def validate_reference_spec(path: Path) -> dict:
    """Fail generation when the catalogue views or drape contract are missing."""
    spec = json.loads(path.read_text(encoding="utf-8"))
    if spec.get("archetype_id") != "basketball_court":
        raise RuntimeError(f"Unexpected archetype reference spec: {path}")
    contract = spec.get("modeling_contract", {})
    if contract.get("runtime_surface") != "ai_drape":
        raise RuntimeError("Basketball runtime surface must come from the AI drape")
    if contract.get("runtime_glb_includes_court_surface") is not False:
        raise RuntimeError("Runtime basketball GLBs must not duplicate the draped court surface")

    repository_root = Path(__file__).resolve().parents[2]
    catalogue_root = repository_root / spec["catalogue_root"]
    required_paths = [catalogue_root / spec["hero"]]
    reference_sets = spec.get("reference_sets", [])
    if not reference_sets:
        raise RuntimeError("Basketball reference spec has no catalogue variants")
    for reference_set in reference_sets:
        views = reference_set.get("views", {})
        for view_name in ("base", "angle_60", "angle_90"):
            filename = views.get(view_name)
            if not filename:
                raise RuntimeError(
                    f"{reference_set.get('variant_id', 'unknown')} is missing {view_name}"
                )
            required_paths.append(catalogue_root / filename)
    missing = [candidate for candidate in required_paths if not candidate.is_file()]
    if missing:
        raise RuntimeError(
            "Missing basketball catalogue reference images:\n"
            + "\n".join(f"  - {candidate}" for candidate in missing)
        )
    print(
        f"[basketball-kit] references: {len(reference_sets)} variants, "
        f"{len(required_paths)} catalogue images ({path})"
    )
    return spec


def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def material(name: str, color: tuple[float, float, float, float], *, metallic: float = 0.0,
             roughness: float = 0.55, emission: tuple[float, float, float, float] | None = None):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = emission
        bsdf.inputs["Emission Strength"].default_value = 1.8
    return mat


def assign(obj, mat) -> None:
    obj.data.materials.append(mat)


def box(name: str, size: tuple[float, float, float], location: tuple[float, float, float], mat,
        *, rotation: tuple[float, float, float] = (0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(obj, mat)
    return obj


def cylinder(name: str, radius: float, depth: float, location: tuple[float, float, float], mat,
             *, vertices: int = 16, rotation: tuple[float, float, float] = (0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth,
                                       location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    assign(obj, mat)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def tube_between(name: str, start: tuple[float, float, float], end: tuple[float, float, float],
                 radius: float, mat, *, vertices: int = 12):
    a = Vector(start)
    b = Vector(end)
    direction = b - a
    obj = cylinder(name, radius, direction.length, tuple((a + b) * 0.5), mat, vertices=vertices)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = direction.to_track_quat("Z", "Y")
    return obj


def torus(name: str, major_radius: float, minor_radius: float,
          location: tuple[float, float, float], mat, *, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major_radius, minor_radius=minor_radius,
                                    major_segments=32, minor_segments=8,
                                    location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    assign(obj, mat)
    return obj


def move_to_collection(objects: list, name: str):
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    for obj in objects:
        for source in list(obj.users_collection):
            source.objects.unlink(obj)
        collection.objects.link(obj)
    return collection


def join_by_material(objects: list, asset_name: str) -> list:
    """Collapse authored pieces to one mesh per material before instancing."""
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    # Joining against a rotated active object can otherwise retain a rotated
    # object frame and inflate the exported bounds. Bake authored transforms
    # while preserving each piece's world-space location.
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
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
        bpy.ops.object.join()
        merged = bpy.context.object
        merged.name = f"{asset_name}_{material_name.replace(' ', '_')}"
        joined.append(merged)
    return joined


def asset_metrics(objects: list) -> tuple[float, int]:
    min_z = math.inf
    max_z = -math.inf
    triangles = 0
    for obj in objects:
        for corner in obj.bound_box:
            world = obj.matrix_world @ Vector(corner)
            min_z = min(min_z, world.z)
            max_z = max(max_z, world.z)
        obj.data.calc_loop_triangles()
        triangles += len(obj.data.loop_triangles)
    return max_z - min_z, triangles


def build_hoop(mats: dict) -> list:
    objects = []
    objects.append(cylinder("HoopPost", 0.095, 3.30, (0.0, 0.0, 1.65), mats["steel"], vertices=20))
    objects.append(cylinder("HoopPostPad", 0.18, 1.55, (0.0, 0.0, 0.775), mats["pad"], vertices=20))
    objects.append(tube_between("HoopSupport", (0.0, 0.0, 3.22), (1.22, 0.0, 3.45),
                                0.075, mats["steel"], vertices=16))
    objects.append(box("Backboard", (0.055, 1.80, 1.05), (1.245, 0.0, 3.425), mats["board"]))
    # Backboard target rectangle on the court-facing (+X) surface.
    objects.append(box("BackboardTargetTop", (0.012, 0.59, 0.025), (1.279, 0.0, 3.53), mats["line"]))
    objects.append(box("BackboardTargetBottom", (0.012, 0.59, 0.025), (1.279, 0.0, 3.25), mats["line"]))
    for y in (-0.2825, 0.2825):
        objects.append(box(f"BackboardTargetSide{y}", (0.012, 0.025, 0.305),
                           (1.279, y, 3.39), mats["line"]))
    rim_center = (1.62, 0.0, 3.05)
    objects.append(torus("Rim", 0.225, 0.012, rim_center, mats["orange"]))
    objects.append(box("RimBracket", (0.38, 0.08, 0.08), (1.43, 0.0, 3.05), mats["orange"]))
    strand_count = 12
    for index in range(strand_count):
        angle = math.tau * index / strand_count
        top = (rim_center[0] + math.cos(angle) * 0.215,
               rim_center[1] + math.sin(angle) * 0.215, 3.025)
        bottom_angle = angle + 0.22
        bottom = (rim_center[0] + math.cos(bottom_angle) * 0.115,
                  rim_center[1] + math.sin(bottom_angle) * 0.115, 2.66)
        objects.append(tube_between(f"NetStrand{index:02d}", top, bottom, 0.007,
                                    mats["net"], vertices=6))
    objects.append(torus("NetLowerRing", 0.115, 0.006, (rim_center[0], rim_center[1], 2.66), mats["net"]))
    # A tiny cap establishes the authoritative 3.95 m model height.
    objects.append(box("BackboardTopCap", (0.06, 1.82, 0.01), (1.245, 0.0, HOOP_TOP_M - 0.005), mats["steel"]))
    return objects


def diagonal_strip(name: str, x1: float, z1: float, x2: float, z2: float, y: float, mat):
    dx = x2 - x1
    dz = z2 - z1
    length = math.hypot(dx, dz)
    return box(name, (length, 0.012, 0.018), ((x1 + x2) / 2, y, (z1 + z2) / 2), mat,
               rotation=(0.0, -math.atan2(dz, dx), 0.0))


def build_fence(length: float, mats: dict, *, gate: bool) -> list:
    objects = []
    post_xs = (-length / 2, 0.0, length / 2) if gate else (-length / 2, length / 2)
    for index, x in enumerate(post_xs):
        objects.append(cylinder(f"FencePost{index}", 0.045, FENCE_HEIGHT_M,
                                (x, 0.0, FENCE_HEIGHT_M / 2), mats["steel"], vertices=12))
    for z in (0.12, FENCE_HEIGHT_M - 0.10):
        objects.append(box(f"FenceRail{z}", (length, 0.05, 0.05), (0.0, 0.0, z), mats["steel"]))
    spacing = 0.34
    diagonal = math.hypot(length, FENCE_HEIGHT_M)
    count = math.ceil(diagonal / spacing)
    slope = FENCE_HEIGHT_M / length
    # Clip two diagonal strip families against the rectangular panel.
    for family in (-1, 1):
        for index in range(-count, count + 1):
            intercept = index * spacing
            candidates = []
            for x in (-length / 2, length / 2):
                z = family * slope * x + FENCE_HEIGHT_M / 2 + intercept
                if 0.08 <= z <= FENCE_HEIGHT_M - 0.08:
                    candidates.append((x, z))
            for z in (0.08, FENCE_HEIGHT_M - 0.08):
                x = (z - FENCE_HEIGHT_M / 2 - intercept) / (family * slope)
                if -length / 2 <= x <= length / 2:
                    candidates.append((x, z))
            if len(candidates) >= 2:
                a, b = candidates[0], candidates[1]
                objects.append(diagonal_strip(f"FenceMesh{family}_{index}", a[0], a[1], b[0], b[1],
                                              0.012, mats["mesh"]))
    if gate:
        objects.append(box("GateLatch", (0.14, 0.10, 0.18), (0.0, -0.06, 1.10), mats["orange"]))
        objects.append(box("GateKickPlate", (length - 0.12, 0.025, 0.16),
                           (0.0, -0.025, 0.16), mats["steel"]))
    return objects


def build_floodlight(mats: dict) -> list:
    objects = []
    bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=0.14, radius2=0.075, depth=12.0,
                                    location=(0.0, 0.0, 6.0))
    pole = bpy.context.object
    pole.name = "FloodlightPole"
    assign(pole, mats["steel"])
    objects.append(pole)
    objects.append(box("FloodlightCrossbar", (0.18, 2.65, 0.16), (0.0, 0.0, 12.05), mats["steel"]))
    for index, y in enumerate((-0.9, 0.0, 0.9)):
        objects.append(box(f"FloodlightHousing{index}", (0.36, 0.48, 0.30),
                           (0.16, y, 12.15), mats["housing"], rotation=(0.0, -0.20, 0.0)))
        objects.append(box(f"FloodlightLens{index}", (0.015, 0.40, 0.22),
                           (0.348, y, 12.11), mats["lens"], rotation=(0.0, -0.20, 0.0)))
    objects.append(box("FloodlightTopCap", (0.02, 0.02, 0.01),
                       (0.0, 0.0, FLOODLIGHT_HEIGHT_M - 0.005), mats["steel"]))
    return objects


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


def look_at(obj, target=(0.0, 0.0, 0.0)) -> None:
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def import_asset(path: Path, name: str, location: tuple[float, float, float], yaw: float = 0.0):
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


def add_court_preview(mats: dict) -> None:
    box("PreviewApron", (32.0, 19.0, 0.06), (0.0, 0.0, -0.04), mats["apron"])
    box("PreviewCourt", (28.0, 15.0, 0.05), (0.0, 0.0, 0.0), mats["court"])
    line_z = 0.032
    for y in (-7.5, 7.5):
        box(f"CourtSideline{y}", (28.0, 0.055, 0.012), (0.0, y, line_z), mats["line"])
    for x in (-14.0, 14.0, 0.0):
        box(f"CourtLine{x}", (0.055, 15.0, 0.012), (x, 0.0, line_z), mats["line"])
    torus("CourtCenterCircle", 1.80, 0.025, (0.0, 0.0, line_z + 0.01), mats["line"])


def render_preview(output_dir: Path, asset_paths: dict[str, Path], mats: dict) -> None:
    reset_scene()
    # Recreate preview-only materials after reset removed unused datablocks.
    mats = create_materials()
    add_court_preview(mats)
    import_asset(asset_paths["hoop"], "HoopWest", (-15.2, 0.0, 0.0), 0.0)
    import_asset(asset_paths["hoop"], "HoopEast", (15.2, 0.0, 0.0), math.pi)
    for side_y in (-9.5, 9.5):
        for x in (-14, -10, -6, -2, 2, 6, 10, 14):
            import_asset(asset_paths["fence"], f"FenceY{side_y}_{x}", (x, side_y, 0.0), 0.0)
    pattern = [(-7.5, "fence"), (-3.5, "fence"), (0.0, "gate"), (3.5, "fence"), (7.5, "fence")]
    for side_x in (-16.0, 16.0):
        for y, kind in pattern:
            import_asset(asset_paths[kind], f"FenceX{side_x}_{y}", (side_x, y, 0.0), math.pi / 2)
    for x, y in ((-15.5, -9.0), (-15.5, 9.0), (15.5, -9.0), (15.5, 9.0)):
        yaw = math.atan2(-y, -x)
        import_asset(asset_paths["floodlight"], f"Floodlight{x}_{y}", (x, y, 0.0), yaw)

    bpy.ops.object.light_add(type="AREA", location=(-8.0, -10.0, 24.0))
    key = bpy.context.object
    key.data.energy = 1700
    key.data.shape = "DISK"
    key.data.size = 12.0
    look_at(key)
    bpy.ops.object.light_add(type="AREA", location=(18.0, 8.0, 14.0))
    fill = bpy.context.object
    fill.data.energy = 900
    fill.data.size = 10.0
    look_at(fill)
    bpy.ops.object.light_add(type="SUN", location=(0.0, 0.0, 20.0))
    sun = bpy.context.object
    sun.rotation_euler = (math.radians(28), math.radians(-22), math.radians(28))
    sun.data.energy = 2.1
    bpy.ops.object.camera_add(location=(46.0, -50.0, 36.0))
    camera = bpy.context.object
    camera.data.lens = 52
    look_at(camera, (0.0, 0.0, 2.4))
    scene = bpy.context.scene
    scene.camera = camera
    for engine in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT", "BLENDER_WORKBENCH"):
        try:
            scene.render.engine = engine
            break
        except TypeError:
            continue
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.16, 0.19, 0.22, 1.0)
    background.inputs["Strength"].default_value = 0.35
    output_dir.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(output_dir / "basketball_kit_court_preview.png")
    bpy.ops.render.render(write_still=True)
    camera.location = (9.0, -8.5, 6.4)
    camera.data.lens = 62
    look_at(camera, (15.2, 0.0, 2.65))
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 1000
    scene.render.filepath = str(output_dir / "basketball_hoop_closeup.png")
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output_dir / "basketball_kit_preview.blend"))


def create_materials() -> dict:
    return {
        "steel": material("Galvanized Steel", (0.19, 0.23, 0.24, 1.0), metallic=0.72, roughness=0.34),
        "mesh": material("Chainlink Mesh", (0.27, 0.31, 0.31, 1.0), metallic=0.62, roughness=0.42),
        "pad": material("Post Padding", (0.045, 0.08, 0.12, 1.0), roughness=0.75),
        "board": material("Backboard", (0.84, 0.88, 0.86, 1.0), roughness=0.26),
        "line": material("Court White", (0.94, 0.95, 0.91, 1.0), roughness=0.48),
        "orange": material("Safety Orange", (0.92, 0.22, 0.035, 1.0), metallic=0.28, roughness=0.4),
        "net": material("Net Cord", (0.94, 0.94, 0.89, 1.0), roughness=0.92),
        "housing": material("Light Housing", (0.12, 0.15, 0.16, 1.0), metallic=0.5, roughness=0.42),
        "lens": material("Light Lens", (0.78, 0.88, 0.84, 1.0), roughness=0.2,
                         emission=(0.72, 0.84, 0.78, 1.0)),
        "court": material("Court Acrylic", (0.08, 0.32, 0.47, 1.0), roughness=0.83),
        "apron": material("Court Apron", (0.13, 0.17, 0.18, 1.0), roughness=0.9),
    }


def main() -> None:
    args = parse_args()
    args.output_dir = args.output_dir.resolve()
    args.preview_dir = args.preview_dir.resolve()
    args.reference_spec = args.reference_spec.resolve()
    validate_reference_spec(args.reference_spec)
    if args.validate_references_only:
        return
    reset_scene()
    mats = create_materials()
    assets = {
        "hoop": ("basketball-hoop.glb", build_hoop(mats)),
        "fence": ("chainlink-fence-4m.glb", build_fence(4.0, mats, gate=False)),
        "gate": ("chainlink-gate-3m.glb", build_fence(3.0, mats, gate=True)),
        "floodlight": ("basketball-floodlight.glb", build_floodlight(mats)),
    }
    paths: dict[str, Path] = {}
    expected_heights = {
        "hoop": HOOP_TOP_M,
        "fence": FENCE_HEIGHT_M,
        "gate": FENCE_HEIGHT_M,
        "floodlight": FLOODLIGHT_HEIGHT_M,
    }
    for key, (filename, authored_objects) in assets.items():
        objects = join_by_material(authored_objects, key)
        height, triangles = asset_metrics(objects)
        if not math.isclose(height, expected_heights[key], abs_tol=0.002):
            raise RuntimeError(
                f"{key} height {height:.4f} m does not match {expected_heights[key]:.4f} m"
            )
        move_to_collection(objects, f"BasketballKit_{key}")
        path = args.output_dir / filename
        export_glb(path, objects)
        paths[key] = path
        print(
            f"[basketball-kit] {key}: {path} ({path.stat().st_size} bytes, "
            f"{triangles} triangles, {len(objects)} material meshes)"
        )
    render_preview(args.preview_dir, paths, mats)
    print(f"[basketball-kit] preview: {args.preview_dir / 'basketball_kit_court_preview.png'}")


if __name__ == "__main__":
    main()
