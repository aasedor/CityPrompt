"""Derive a texture-free semantic architectural-clay GLB from an RLASM source.

Run with Blender 5.2 in background mode.  Geometry, object transforms, and the
bottom-centre coordinate contract are inherited unchanged from a source GLB or
Blend file.  When RLASM object markers are available in a Blend file, review
context is removed automatically and only the authored building plus occupied
depth is exported.  Only material ownership changes: source-specific PBR
materials are collapsed to a small flat-role palette that tells the image
model which construction systems are roof, wall, trim, glass, timber, masonry,
interior, or hardware.
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


SEMANTIC_PALETTE: dict[str, tuple[tuple[float, float, float, float], float]] = {
    "masonry": ((0.55, 0.28, 0.20, 1.0), 0.86),
    "wall": ((0.72, 0.69, 0.62, 1.0), 0.88),
    "trim": ((0.88, 0.84, 0.74, 1.0), 0.82),
    "roof": ((0.30, 0.31, 0.31, 1.0), 0.92),
    "glass": ((0.18, 0.29, 0.33, 1.0), 0.36),
    "timber": ((0.43, 0.27, 0.14, 1.0), 0.79),
    "interior": ((0.66, 0.47, 0.27, 1.0), 0.84),
    "hardware": ((0.10, 0.11, 0.12, 1.0), 0.58),
}

RENDERABLE_TYPES = {"MESH", "CURVE", "SURFACE", "FONT", "META"}
QA_VIEWS = ("front", "front_corner", "aerial", "rear_corner", "true_top")


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument(
        "--comparison-source",
        type=Path,
        help="Optional full RLASM GLB used as the byte-reduction comparison basis.",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--preview", type=Path, required=True)
    parser.add_argument("--preview-dir", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument(
        "--scope",
        choices=("auto", "building", "all"),
        default="auto",
        help="Auto keeps marked RLASM building objects when markers exist.",
    )
    return parser.parse_args(argv)


def semantic_role(source_name: str) -> str:
    name = source_name.upper()
    if any(token in name for token in ("GLASS", "CURTAIN", "PANE")):
        return "glass"
    if any(token in name for token in ("SHINGLE", "ROOF", "PANTILE", "SLATE")):
        return "roof"
    if any(token in name for token in ("TERRACOTTA", "DRESSING", "COPING")):
        return "trim"
    if any(token in name for token in ("BRICK", "MASONRY")):
        return "masonry"
    if any(token in name for token in ("TRIM", "FLASHING", "SANDSTONE", "STONE")):
        return "trim"
    if any(token in name for token in ("TIMBER", "FIR", "WOOD", "OAK", "SASH", "DOOR")):
        return "timber"
    if any(token in name for token in ("HARDWARE", "APPLIANCE", "METAL", "ZINC")):
        return "hardware"
    if any(
        token in name
        for token in (
            "INTERIOR",
            "LIGHT",
            "CUSHION",
            "RUG",
            "SOFA",
            "CABINET",
            "COUNTER",
            "PLASTER",
            "TEXTILE",
            "DOMESTIC",
            "OCCUPIED",
            "ROOM",
        )
    ):
        return "interior"
    return "wall"


def make_flat_material(role: str) -> bpy.types.Material:
    color, roughness = SEMANTIC_PALETTE[role]
    material = bpy.data.materials.new(f"CP_SEMANTIC_CLAY_{role.upper()}")
    material.use_nodes = True
    material.diffuse_color = color
    nodes = material.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = 0.0
    material.node_tree.links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    return material


def remap_materials() -> dict[str, int]:
    semantic_materials = {role: make_flat_material(role) for role in SEMANTIC_PALETTE}
    role_slots = {role: 0 for role in SEMANTIC_PALETTE}
    for obj in bpy.context.scene.objects:
        if obj.type not in RENDERABLE_TYPES:
            continue
        object_roles: set[str] = set()
        for slot in obj.material_slots:
            source_name = slot.material.name if slot.material else ""
            role = semantic_role(source_name)
            slot.material = semantic_materials[role]
            role_slots[role] += 1
            object_roles.add(role)
        obj["cityprompt_material_mode"] = "semantic_architectural_clay"
        obj["cityprompt_semantic_roles"] = ",".join(sorted(object_roles))
    return {role: count for role, count in role_slots.items() if count}


def load_source(source: Path) -> str:
    if source.suffix.lower() == ".blend":
        bpy.ops.wm.open_mainfile(filepath=str(source))
        return "blend"
    if source.suffix.lower() in {".glb", ".gltf"}:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(source))
        return "gltf"
    raise ValueError(f"Unsupported semantic-clay source: {source.suffix}")


def filter_source_scope(scope: str) -> dict[str, int | str]:
    renderables = [obj for obj in bpy.context.scene.objects if obj.type in RENDERABLE_TYPES]
    marked = [obj for obj in renderables if bool(obj.get("rlasm_building_object"))]
    resolved_scope = "building" if scope == "building" or (scope == "auto" and marked) else "all"

    if resolved_scope == "building" and not marked:
        raise RuntimeError("Building-only scope requested, but the source has no RLASM building markers")

    removed = 0
    if resolved_scope == "building":
        for obj in renderables:
            if obj not in marked:
                bpy.data.objects.remove(obj, do_unlink=True)
                removed += 1

    # Source review cameras and lights are never part of a runtime clay asset.
    for obj in list(bpy.context.scene.objects):
        if obj.type in {"CAMERA", "LIGHT"}:
            bpy.data.objects.remove(obj, do_unlink=True)

    retained = sum(1 for obj in bpy.context.scene.objects if obj.type in RENDERABLE_TYPES)
    return {
        "requested": scope,
        "resolved": resolved_scope,
        "source_renderable_objects": len(renderables),
        "marked_building_objects": len(marked),
        "removed_renderable_objects": removed,
        "retained_renderable_objects": retained,
    }


def mesh_bounds() -> tuple[Vector, Vector]:
    points: list[Vector] = []
    for obj in bpy.context.scene.objects:
        if obj.type not in RENDERABLE_TYPES or obj.hide_render:
            continue
        points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    if not points:
        raise RuntimeError("Imported GLB contains no renderable mesh bounds")
    return (
        Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points))),
        Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points))),
    )


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def preview_camera(view: str, bounds_min: Vector, bounds_max: Vector) -> bpy.types.Object:
    centre = (bounds_min + bounds_max) * 0.5
    width = bounds_max.x - bounds_min.x
    depth = bounds_max.y - bounds_min.y
    height = bounds_max.z - bounds_min.z
    target = Vector((centre.x, centre.y, bounds_min.z + height * 0.46))

    if view == "front":
        location = (centre.x, bounds_min.y - depth * 1.82, bounds_min.z + height * 0.54)
        lens = 58
    elif view == "front_corner":
        location = (centre.x + width * 1.42, bounds_min.y - depth * 1.58, bounds_min.z + height * 0.82)
        lens = 54
    elif view == "aerial":
        location = (centre.x + width * 1.90, bounds_min.y - depth * 1.62, bounds_max.z + height * 1.32)
        lens = 56
    elif view == "rear_corner":
        location = (centre.x + width * 1.45, bounds_max.y + depth * 1.56, bounds_min.z + height * 0.80)
        lens = 54
    elif view == "true_top":
        location = (centre.x, centre.y, bounds_max.z + max(width, depth, height) * 4.0)
        lens = 58
    else:
        raise ValueError(f"Unknown semantic-clay preview view: {view}")

    bpy.ops.object.camera_add(location=location)
    camera = bpy.context.object
    camera.name = f"SemanticClayCamera_{view}"
    camera.data.lens = lens
    look_at(camera, target)
    if view == "true_top":
        camera.data.type = "ORTHO"
        camera.data.ortho_scale = max(width, depth) * 1.22
        look_at(camera, Vector((centre.x, centre.y, bounds_min.z)))
    return camera


def setup_preview_lighting(bounds_min: Vector, bounds_max: Vector) -> None:
    bounds_min, bounds_max = mesh_bounds()
    centre = (bounds_min + bounds_max) * 0.5
    width = bounds_max.x - bounds_min.x
    depth = bounds_max.y - bounds_min.y
    height = bounds_max.z - bounds_min.z

    bpy.ops.object.light_add(type="AREA", location=(centre.x - width * 0.25, centre.y - depth, bounds_max.z + height))
    key = bpy.context.object
    key.data.energy = 1450
    key.data.shape = "DISK"
    key.data.size = max(width, depth) * 1.25
    look_at(key, centre)

    bpy.ops.object.light_add(type="AREA", location=(centre.x + width, centre.y + depth * 0.25, bounds_max.z + height * 0.35))
    fill = bpy.context.object
    fill.data.energy = 700
    fill.data.size = max(width, depth)
    look_at(fill, centre)

    bpy.ops.object.light_add(type="SUN", location=(0.0, 0.0, bounds_max.z + 10.0))
    sun = bpy.context.object
    sun.rotation_euler = (math.radians(28.0), math.radians(-18.0), math.radians(132.0))
    sun.data.energy = 1.25
    sun.data.angle = math.radians(10.0)

    world = bpy.context.scene.world or bpy.data.worlds.new("Semantic Clay World")
    bpy.context.scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.085, 0.105, 0.12, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.48

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.look = "AgX - Medium High Contrast"


def render_preview(path: Path, view: str = "front_corner") -> None:
    bounds_min, bounds_max = mesh_bounds()
    if not any(obj.name.startswith("SemanticClayKey") for obj in bpy.context.scene.objects):
        setup_preview_lighting(bounds_min, bounds_max)
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        # Name the first area light so repeated preview renders reuse the rig.
        area_lights = [obj for obj in bpy.context.scene.objects if obj.type == "LIGHT" and obj.data.type == "AREA"]
        if area_lights:
            area_lights[0].name = "SemanticClayKey"

    for obj in list(bpy.context.scene.objects):
        if obj.type == "CAMERA":
            bpy.data.objects.remove(obj, do_unlink=True)
    camera = preview_camera(view, bounds_min, bounds_max)
    scene = bpy.context.scene
    scene.camera = camera
    scene.render.filepath = str(path.resolve())
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.render.render(write_still=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    args = parse_args()
    source = args.source.resolve()
    comparison_source = args.comparison_source.resolve() if args.comparison_source else source
    output = args.output.resolve()
    preview = args.preview.resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if not comparison_source.is_file():
        raise FileNotFoundError(comparison_source)

    source_kind = load_source(source)
    scope_report = filter_source_scope(args.scope)
    role_slots = remap_materials()
    bounds_min, bounds_max = mesh_bounds()

    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(output),
        export_format="GLB",
        export_yup=True,
        export_materials="EXPORT",
        export_extras=True,
        export_cameras=False,
        export_lights=False,
    )
    render_preview(preview, "front_corner")
    preview_paths = {"front_corner": str(preview)}
    if args.preview_dir:
        preview_dir = args.preview_dir.resolve()
        for view in QA_VIEWS:
            path = preview_dir / f"{view}.png"
            render_preview(path, view)
            preview_paths[view] = str(path)

    report = {
        "schema": "cityprompt.rlasm.semantic-clay-export@1",
        "source": str(source),
        "source_kind": source_kind,
        "source_sha256": sha256(source),
        "source_bytes": source.stat().st_size,
        "comparison_source": str(comparison_source),
        "comparison_source_sha256": sha256(comparison_source),
        "comparison_source_bytes": comparison_source.stat().st_size,
        "output": str(output),
        "output_sha256": sha256(output),
        "output_bytes": output.stat().st_size,
        "byte_reduction_percent": round(
            (1.0 - output.stat().st_size / comparison_source.stat().st_size) * 100.0,
            1,
        ),
        "previews": preview_paths,
        "scope": scope_report,
        "semantic_roles": role_slots,
        "blender_bounds": {
            "min": [round(value, 6) for value in bounds_min],
            "max": [round(value, 6) for value in bounds_max],
        },
    }
    if args.report:
        report_path = args.report.resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("SEMANTIC_CLAY_EXPORT " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
