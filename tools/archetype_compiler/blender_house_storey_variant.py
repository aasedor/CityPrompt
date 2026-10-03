from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector


ROOT = Path("C:/dev-artifacts/CityPrompt/house-flex-pilot-2026-09-28")


def args():
    marker = sys.argv.index("--")
    family, source, output = sys.argv[marker + 1 : marker + 4]
    return family, Path(source), Path(output)


def bounds(obj):
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return (
        [min(point[i] for point in points) for i in range(3)],
        [max(point[i] for point in points) for i in range(3)],
    )


def clip_above(obj, top):
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.select_set(False)
    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    geometry = list(mesh.verts) + list(mesh.edges) + list(mesh.faces)
    bmesh.ops.bisect_plane(
        mesh,
        geom=geometry,
        plane_co=(0, 0, top),
        plane_no=(0, 0, 1),
        clear_inner=False,
        clear_outer=True,
    )
    if not mesh.faces:
        mesh.free()
        bpy.data.objects.remove(obj, do_unlink=True)
        return
    mesh.to_mesh(obj.data)
    mesh.free()
    obj.data.update()


def shift(obj, dz):
    obj.location.z += dz


def duplicate(obj, dz):
    copy = obj.copy()
    copy.data = obj.data.copy()
    bpy.context.collection.objects.link(copy)
    copy.location.z += dz
    copy.name = obj.name + " upper-storey"
    copy["house_flex_authored_copy"] = True
    return copy


def material(name):
    exact = bpy.data.materials.get(name)
    if exact:
        return exact
    for candidate in bpy.data.materials:
        if candidate.name.startswith(name):
            return candidate
    raise RuntimeError(f"Missing material {name}")


def box(name, location, size, mat, role, module):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = tuple(value / 2 for value in size)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material(mat))
    obj["rlasm_building_object"] = True
    obj["rlasm_method"] = "RLASM v6.1"
    obj["cityprompt_semantic_role"] = role
    obj["cityprompt_lego_module"] = module
    obj["representation_kind"] = "architectural_clay"
    obj["native_geometry_only"] = True
    return obj


def shrink_house(family):
    if family == "foursquare":
        target_eave = 3.98
        delta = target_eave - 7.13
        shifted_modules = {
            "hip roof", "roof edges", "chimney", "attic room", "dormer",
            "dormer cheeks", "dormer front.attic double window",
            "dormer hip eave", "dormer shingles",
        }
        deleted_prefixes = (
            "front.upper", "left.left 1", "right.right 1", "rear.rear 1",
            "paired upper sash",
        )
        upper_start = 7.0
    else:
        target_eave = 3.92
        delta = target_eave - 7.06
        shifted_modules = {
            "roof", "roof shingles", "roof trim", "ridge", "chimney",
            "flashing", "bay roof", "gable -1.attic sash", "gable 1.attic sash",
        }
        deleted_prefixes = (
            "front.front sash 2", "front.front sash 3", "front.front sash 4",
            "left.left rear sash 1", "right.right sash 1",
            "rear.rear sash 2", "rear.rear sash 3", "rear.rear sash 4",
        )
        upper_start = 7.0

    for obj in list(bpy.context.scene.objects):
        if obj.type != "MESH" or not obj.get("rlasm_building_object"):
            continue
        module = str(obj.get("cityprompt_lego_module") or "")
        low, high = bounds(obj)
        if any(module.startswith(prefix) for prefix in deleted_prefixes):
            bpy.data.objects.remove(obj, do_unlink=True)
        elif module in shifted_modules:
            shift(obj, delta)
        elif low[2] >= upper_start:
            # Gable carriers and their source-authored lap/casing pieces live
            # in shared envelope/siding modules, so preserve and lower them.
            shift(obj, delta)
        elif high[2] > target_eave:
            clip_above(obj, target_eave)


def grow_bungalow():
    delta = 2.93
    duplicate_modules = {
        "envelope", "brick bonding", "masonry courses", "occupied room",
        "brick front.living room", "living room sash",
        "projecting bedroom.right room", "rear.rear room",
        "left.left0", "left.left1", "left.left2",
        "right.right0", "right.right1", "right.right2",
    }
    roof_modules = {"hip roof", "gable", "gable boarding", "roof edge", "roof fittings"}
    for obj in list(bpy.context.scene.objects):
        if obj.type != "MESH" or not obj.get("rlasm_building_object"):
            continue
        module = str(obj.get("cityprompt_lego_module") or "")
        if module in duplicate_modules:
            duplicate(obj, delta)
        if module in roof_modules:
            shift(obj, delta)
        if module == "chimney":
            name = obj.name.lower()
            if "cap" in name or "pot" in name:
                shift(obj, delta)
            elif "brick chimney" in name:
                low, high = bounds(obj)
                bpy.ops.object.select_all(action="DESELECT")
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                obj.select_set(False)
                for vertex in obj.data.vertices:
                    world_z = (obj.matrix_world @ vertex.co).z
                    if world_z > low[2] + 1e-6:
                        vertex.co.z += delta * (world_z - low[2]) / (high[2] - low[2])
                obj.data.update()

    # Close the two ground-floor door cuts in the copied upper wall band. The
    # original entrances, stairs and porch remain only at grade.
    box("Authored upper front brick infill", (-0.15, -6.065, 4.64), (0.94, 0.27, 2.18), "CLAY_WALL", "wall", "upper entrance infill")
    box("Authored upper rear siding infill", (2.0, 6.065, 4.625), (0.94, 0.27, 2.15), "CLAY_SIDING", "siding", "upper entrance infill")
    # Continue the source's tight brick course rhythm over the former front
    # entrance, avoiding a conspicuous unjointed patch.
    z0 = 3.55
    for row in range(34):
        z = z0 + (row + 0.5) * 0.085
        if z >= 6.47:
            break
        box(f"Upper entrance bed joint {row}", (-0.15, -6.205, z), (0.94, 0.008, 0.006), "CLAY_MORTAR", "mortar", "upper entrance infill")
        offset = 0.1225 if row % 2 else 0.0
        for x in (-0.15 - 0.245 + offset, -0.15 + offset, -0.15 + 0.245 + offset):
            if -0.60 < x < 0.30:
                box(f"Upper entrance perp joint {row}-{x:.3f}", (x, -6.208, z), (0.006, 0.008, 0.077), "CLAY_MORTAR", "mortar", "upper entrance infill")


def consolidate_for_runtime():
    """Join the authored pieces by their exact material assignment.

    The authoring blend intentionally retains thousands of named semantic
    pieces.  Runtime GLBs do not need that authoring granularity, and shipping
    it would add thousands of draw calls.  Grouping only objects with the same
    ordered material slots preserves every material boundary and transform
    while matching the compact delivery shape of the reviewed source GLBs.
    """
    groups = {}
    for obj in list(bpy.context.scene.objects):
        if obj.type != "MESH" or not obj.get("rlasm_building_object"):
            continue
        key = tuple(slot.material.name if slot.material else "" for slot in obj.material_slots)
        groups.setdefault(key, []).append(obj)
    for index, objects in enumerate(groups.values()):
        if len(objects) < 2:
            continue
        bpy.ops.object.select_all(action="DESELECT")
        for obj in objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = objects[0]
        bpy.ops.object.join()
        objects[0].name = f"House runtime material {index:02d}"
        objects[0]["rlasm_building_object"] = True


def clean_and_export(output):
    consolidate_for_runtime()
    for obj in list(bpy.context.scene.objects):
        if obj.type == "MESH" and obj.get("rlasm_building_object"):
            obj.select_set(True)
        else:
            obj.select_set(False)
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(output),
        export_format="GLB",
        export_yup=True,
        export_apply=True,
        use_selection=True,
    )


def render_views(family, output):
    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH" and obj.get("rlasm_building_object")]
    points = [obj.matrix_world @ Vector(corner) for obj in mesh_objects for corner in obj.bound_box]
    low = Vector(tuple(min(point[i] for point in points) for i in range(3)))
    high = Vector(tuple(max(point[i] for point in points) for i in range(3)))
    centre = (low + high) / 2
    extent = max(high.x - low.x, high.y - low.y, high.z - low.z)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 960
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    world = bpy.data.worlds.new("House flex neutral world") if not bpy.data.worlds else bpy.data.worlds[0]
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.55, 0.58, 0.62, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.7
    scene.world = world
    bpy.ops.object.light_add(type="SUN", location=(-10, -10, 18))
    sun = bpy.context.object
    sun.rotation_euler = (math.radians(35), math.radians(-25), math.radians(-35))
    sun.data.energy = 2.2
    bpy.ops.object.light_add(type="AREA", location=(-10, -12, 14))
    area = bpy.context.object
    area.data.energy = 1100
    area.data.shape = "DISK"
    area.data.size = 9
    direction = centre - area.location
    area.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    ground = bpy.data.objects.get("House flex review ground")
    if not ground:
        bpy.ops.mesh.primitive_plane_add(size=100, location=(centre.x, centre.y, low.z - 0.01))
        ground = bpy.context.object
        ground.name = "House flex review ground"
        mat = bpy.data.materials.new("House flex review ground")
        mat.diffuse_color = (0.38, 0.40, 0.38, 1)
        ground.data.materials.append(mat)
    views = {
        "front": (centre.x, low.y - extent * 2.1, centre.z + extent * 0.12),
        "front_corner": (high.x + extent * 1.35, low.y - extent * 1.65, centre.z + extent * 0.35),
        "aerial": (high.x + extent * 1.1, low.y - extent * 1.25, high.z + extent * 1.6),
    }
    for name, location in views.items():
        bpy.ops.object.camera_add(location=location)
        camera = bpy.context.object
        camera.data.lens = 55 if name != "aerial" else 50
        camera.rotation_euler = (centre - camera.location).to_track_quat("-Z", "Y").to_euler()
        scene.camera = camera
        scene.render.filepath = str(ROOT / f"{family}-{name}.png")
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(camera, do_unlink=True)


def main():
    family, source, output = args()
    bpy.ops.wm.open_mainfile(filepath=str(source))
    if family in {"foursquare", "clapboard"}:
        shrink_house(family)
    elif family == "bungalow":
        grow_bungalow()
    else:
        raise RuntimeError(family)
    render_views(family, output)
    clean_and_export(output)
    report = {
        "family": family,
        "source": str(source),
        "output": str(output),
        "mode": "authored one-storey composition" if family != "bungalow" else "authored two-storey composition",
    }
    (ROOT / f"{family}-build.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
