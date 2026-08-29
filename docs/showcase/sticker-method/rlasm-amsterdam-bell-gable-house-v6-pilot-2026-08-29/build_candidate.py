from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
MODE = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "full"
W, D = 8.4, 15.2
PLINTH_Z, FLOOR_Z, CORNICE_Z = 0.36, 3.45, 9.55


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def set_input(node, names, value) -> None:
    for name in names:
        if name in node.inputs:
            node.inputs[name].default_value = value
            return


def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        if collection.name != "Collection":
            bpy.data.collections.remove(collection)


def collection(name: str):
    target = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(target)
    return target


def link_only(obj, target) -> None:
    for source in list(obj.users_collection):
        source.objects.unlink(obj)
    target.objects.link(obj)


def mark_building(obj, role: str) -> None:
    obj["rlasm_building_object"] = True
    obj["rlasm_role"] = role


def plain_material(name, color, roughness=0.7, metallic=0.0, *, building=False):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    set_input(bsdf, ("Base Color",), color)
    set_input(bsdf, ("Roughness",), roughness)
    set_input(bsdf, ("Metallic",), metallic)
    material.diffuse_color = color
    material["rlasm_context_only"] = not building
    return material


def world_material(name, relative_path, axes, tile_m, roughness, metallic=0.0, bump=0.12, saturation=1.0, value=1.0):
    path = ROOT / relative_path
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    geometry = nodes.new("ShaderNodeNewGeometry")
    separate = nodes.new("ShaderNodeSeparateXYZ")
    combine = nodes.new("ShaderNodeCombineXYZ")
    image = nodes.new("ShaderNodeTexImage")
    image.image = bpy.data.images.load(str(path), check_existing=True)
    image.extension = "REPEAT"
    scale_nodes = []
    for index, axis in enumerate(axes):
        scale = nodes.new("ShaderNodeMath")
        scale.operation = "MULTIPLY"
        scale.inputs[1].default_value = 1.0 / tile_m
        links.new(separate.outputs[axis], scale.inputs[0])
        links.new(scale.outputs[0], combine.inputs[index])
        scale_nodes.append(scale)
    links.new(geometry.outputs["Position"], separate.inputs["Vector"])
    links.new(combine.outputs["Vector"], image.inputs["Vector"])
    grade = nodes.new("ShaderNodeHueSaturation")
    grade.inputs["Saturation"].default_value = saturation
    grade.inputs["Value"].default_value = value
    links.new(image.outputs["Color"], grade.inputs["Color"])
    links.new(grade.outputs["Color"], bsdf.inputs["Base Color"])
    if bump > 0:
        rgb = nodes.new("ShaderNodeRGBToBW")
        bump_node = nodes.new("ShaderNodeBump")
        bump_node.inputs["Strength"].default_value = bump
        bump_node.inputs["Distance"].default_value = min(0.16, tile_m / 30.0)
        links.new(image.outputs["Color"], rgb.inputs["Color"])
        links.new(rgb.outputs["Val"], bump_node.inputs["Height"])
        links.new(bump_node.outputs["Normal"], bsdf.inputs["Normal"])
    set_input(bsdf, ("Roughness",), roughness)
    set_input(bsdf, ("Metallic",), metallic)
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    material["rlasm_status"] = "reference_specific_finished"
    material["rlasm_source_sha256"] = sha256(path)
    material["rlasm_mapping_axes"] = "-".join(axes)
    material["rlasm_tile_m"] = tile_m
    material["rlasm_generic_fallback"] = False
    return material


def box_world_material(name, relative_path, tile_m, roughness, metallic=0.0, bump=0.12, saturation=1.0, value=1.0):
    """Reference texture with tri-planar world mapping for curves, arches, and returns."""
    path = ROOT / relative_path
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    geometry = nodes.new("ShaderNodeNewGeometry")
    scale = nodes.new("ShaderNodeVectorMath")
    scale.operation = "SCALE"
    scale.inputs[3].default_value = 1.0 / tile_m
    image = nodes.new("ShaderNodeTexImage")
    image.image = bpy.data.images.load(str(path), check_existing=True)
    image.extension = "REPEAT"
    image.projection = "BOX"
    image.projection_blend = 0.22
    grade = nodes.new("ShaderNodeHueSaturation")
    grade.inputs["Saturation"].default_value = saturation
    grade.inputs["Value"].default_value = value
    links.new(geometry.outputs["Position"], scale.inputs[0])
    links.new(scale.outputs[0], image.inputs["Vector"])
    links.new(image.outputs["Color"], grade.inputs["Color"])
    links.new(grade.outputs["Color"], bsdf.inputs["Base Color"])
    if bump > 0:
        rgb = nodes.new("ShaderNodeRGBToBW")
        bump_node = nodes.new("ShaderNodeBump")
        bump_node.inputs["Strength"].default_value = bump
        bump_node.inputs["Distance"].default_value = min(0.14, tile_m / 34.0)
        links.new(image.outputs["Color"], rgb.inputs["Color"])
        links.new(rgb.outputs["Val"], bump_node.inputs["Height"])
        links.new(bump_node.outputs["Normal"], bsdf.inputs["Normal"])
    set_input(bsdf, ("Roughness",), roughness)
    set_input(bsdf, ("Metallic",), metallic)
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    material["rlasm_status"] = "reference_specific_finished"
    material["rlasm_source_sha256"] = sha256(path)
    material["rlasm_mapping_axes"] = "world_box_triplanar"
    material["rlasm_tile_m"] = tile_m
    material["rlasm_generic_fallback"] = False
    return material


def identity_material():
    path = ROOT / "references/registered/printing-rosette-iron-only-v3.png"
    material = bpy.data.materials.new("Barcelona_Registered_Iron_Printing_Rosette")
    material.use_nodes = True
    nodes, links = material.node_tree.nodes, material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    image = nodes.new("ShaderNodeTexImage")
    image.image = bpy.data.images.load(str(path), check_existing=True)
    image.interpolation = "Linear"
    links.new(image.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(image.outputs["Alpha"], bsdf.inputs["Alpha"])
    set_input(bsdf, ("Roughness",), 0.72)
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    if hasattr(material, "surface_render_method"):
        material.surface_render_method = "BLENDED"
    material["rlasm_status"] = "registered_identity"
    material["rlasm_source_sha256"] = sha256(path)
    material["rlasm_generic_fallback"] = False
    return material


def glass_material():
    source = ROOT / "references/catalogue/variant_0.png"
    material = bpy.data.materials.new("Amsterdam_Neutral_Occupied_Sash_Glass")
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    set_input(bsdf, ("Base Color",), (0.56, 0.62, 0.60, 1.0))
    set_input(bsdf, ("Roughness",), 0.075)
    set_input(bsdf, ("Metallic",), 0.0)
    set_input(bsdf, ("IOR",), 1.46)
    set_input(bsdf, ("Transmission Weight", "Transmission"), 0.82)
    set_input(bsdf, ("Alpha",), 0.18)
    material.diffuse_color = (0.56, 0.62, 0.60, 0.18)
    if hasattr(material, "surface_render_method"):
        material.surface_render_method = "BLENDED"
    material["rlasm_status"] = "source_specific_optical"
    material["rlasm_source_sha256"] = sha256(source)
    material["rlasm_optical_authority"] = "exact Amsterdam bell-gable variant-0 sash glazing"
    material["rlasm_generic_fallback"] = False
    return material


def lantern_glass_material():
    """Uniform aged monitor glass calibrated from the exact 60-degree source."""
    source = ROOT / "references/catalogue/variant_2_angle_60.jpg"
    material = bpy.data.materials.new("Barcelona_Aged_Continuous_Monitor_Glass")
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    set_input(bsdf, ("Base Color",), (0.46, 0.50, 0.45, 1.0))
    set_input(bsdf, ("Roughness",), 0.30)
    set_input(bsdf, ("Metallic",), 0.0)
    set_input(bsdf, ("IOR",), 1.47)
    set_input(bsdf, ("Transmission Weight", "Transmission"), 0.30)
    set_input(bsdf, ("Alpha",), 0.74)
    set_input(bsdf, ("Emission Color", "Emission"), (0.035, 0.040, 0.035, 1.0))
    set_input(bsdf, ("Emission Strength",), 0.035)
    material.diffuse_color = (0.46, 0.50, 0.45, 0.74)
    if hasattr(material, "surface_render_method"):
        material.surface_render_method = "BLENDED"
    material.use_backface_culling = False
    material["rlasm_status"] = "exact_source_conditioned_translucent_monitor"
    material["rlasm_source_sha256"] = sha256(source)
    material["rlasm_optical_authority"] = "exact variant-2 60-degree roof-monitor panes"
    material["rlasm_generic_fallback"] = False
    return material


def warm_room_material(timber):
    material = timber.copy()
    material.name = "Amsterdam_Occupied_Residential_Depth"
    nodes = material.node_tree.nodes
    bsdf = next(node for node in nodes if node.bl_idname == "ShaderNodeBsdfPrincipled")
    set_input(bsdf, ("Emission Color", "Emission"), (0.24, 0.095, 0.030, 1.0))
    set_input(bsdf, ("Emission Strength",), 0.16)
    set_input(bsdf, ("Alpha",), 0.18)
    set_input(bsdf, ("Transmission Weight", "Transmission"), 0.22)
    if hasattr(material, "surface_render_method"):
        material.surface_render_method = "BLENDED"
    material["rlasm_status"] = "source_specific_occupied_depth"
    return material


def box(name, location, scale, material, target, *, bevel=0.0, role="construction"):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = (scale[0] / 2.0, scale[1] / 2.0, scale[2] / 2.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        obj.data.materials.append(material)
    if bevel:
        modifier = obj.modifiers.new("PhysicalEdge", "BEVEL")
        modifier.width = bevel
        modifier.segments = 2
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    link_only(obj, target)
    if role != "context":
        mark_building(obj, role)
    else:
        obj["rlasm_context_object"] = True
    return obj


def curve_tube(name, points, radius, material, target, role="ornament"):
    curve = bpy.data.curves.new(name + "_Curve", "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 2
    curve.bevel_depth = radius
    curve.bevel_resolution = 3
    curve.use_fill_caps = True
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for item, point in zip(spline.points, points):
        item.co = (*point, 1.0)
    obj = bpy.data.objects.new(name, curve)
    curve.materials.append(material)
    target.objects.link(obj)
    mark_building(obj, role)
    return obj


def prism_y(name, profile, depth, material, target, y=0.0, role="construction"):
    vertices = [(x, y - depth / 2, z) for x, z in profile] + [(x, y + depth / 2, z) for x, z in profile]
    count = len(profile)
    faces = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    for index in range(count):
        nxt = (index + 1) % count
        faces.append((index, nxt, count + nxt, count + index))
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    mesh.materials.append(material)
    target.objects.link(obj)
    mark_building(obj, role)
    return obj


def profile_strip_y(name, centerline, width, depth, material, target, y=0.0, role="construction"):
    """One continuous mitered strip around a 2D x/z centerline."""
    points = [Vector((float(x), float(z))) for x, z in centerline]
    normals = []
    for index, point in enumerate(points):
        if index == 0:
            tangent = (points[1] - point).normalized()
        elif index == len(points) - 1:
            tangent = (point - points[index - 1]).normalized()
        else:
            tangent = (points[index + 1] - points[index - 1]).normalized()
        normals.append(Vector((-tangent.y, tangent.x)).normalized())
    half = width / 2.0
    outer = [(point.x + normal.x * half, point.y + normal.y * half) for point, normal in zip(points, normals)]
    inner = [(point.x - normal.x * half, point.y - normal.y * half) for point, normal in zip(reversed(points), reversed(normals))]
    return prism_y(name, outer + inner, depth, material, target, y=y, role=role)


def catmull_rom_open_2d(points, samples_per_segment=4):
    """Interpolate an open x/z profile with tangent-continuous Catmull-Rom spans."""
    values = [Vector((float(x), float(z))) for x, z in points]
    if len(values) < 3:
        return [(point.x, point.y) for point in values]
    extended = [values[0]] + values + [values[-1]]
    result = []
    for index in range(1, len(extended) - 2):
        p0, p1, p2, p3 = extended[index - 1:index + 3]
        for sample in range(samples_per_segment):
            t = sample / samples_per_segment
            t2, t3 = t * t, t * t * t
            point = 0.5 * ((2.0 * p1) + (-p0 + p2) * t + (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * t2 + (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * t3)
            result.append((point.x, point.y))
    result.append((values[-1].x, values[-1].y))
    return result


def prism_x(name, profile, depth, material, target, x=0.0, role="construction"):
    # Profile coordinates are (y, z).
    vertices = [(x - depth / 2, y, z) for y, z in profile] + [(x + depth / 2, y, z) for y, z in profile]
    count = len(profile)
    faces = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    for index in range(count):
        nxt = (index + 1) % count
        faces.append((index, nxt, count + nxt, count + index))
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    mesh.materials.append(material)
    target.objects.link(obj)
    mark_building(obj, role)
    return obj


def arch_profile(center, bottom, width, spring, segments=24):
    radius = width / 2.0
    points = [(center - radius, bottom), (center - radius, spring)]
    for index in range(segments + 1):
        angle = math.pi - math.pi * index / segments
        points.append((center + math.cos(angle) * radius, spring + math.sin(angle) * radius))
    points.append((center + radius, bottom))
    return points


def cut_with(panel, cutter) -> None:
    modifier = panel.modifiers.new("TrueOpening", "BOOLEAN")
    modifier.operation = "DIFFERENCE"
    modifier.solver = "EXACT"
    modifier.object = cutter
    bpy.context.view_layer.objects.active = panel
    panel.select_set(True)
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def cut_arch_x(panel, surface_x, center_y, width, bottom, spring, target, cutter_material):
    """Cut a robust rectilinear-plus-round arched opening through an X-facing wall."""
    rectangle = box(
        panel.name + "_RectCutter",
        (surface_x, center_y, (bottom + spring) / 2),
        (1.2, width, spring - bottom),
        cutter_material,
        target,
        role="temporary",
    )
    cut_with(panel, rectangle)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=48,
        radius=width / 2,
        depth=1.2,
        location=(surface_x, center_y, spring),
        rotation=(0, math.pi / 2, 0),
    )
    crown = bpy.context.object
    crown.name = panel.name + "_CrownCutter"
    link_only(crown, target)
    cut_with(panel, crown)


def arch_window_y(prefix, x, surface_y, outward, width, bottom, spring, brick, iron, glass, occupied, target):
    inner_width = width - 0.34
    plane_y = surface_y - outward * 0.22
    room_y = surface_y - outward * 0.92
    profile = arch_profile(x, bottom + 0.08, inner_width, spring)
    prism_y(prefix + "_Glass", profile, 0.035, glass, target, y=plane_y, role="optical_glass")
    prism_y(prefix + "_OccupiedDepth", arch_profile(x, bottom + 0.16, inner_width - 0.22, spring - 0.05), 0.06, occupied, target, y=room_y, role="occupied_depth")
    arch_points = [(px, surface_y + outward * 0.07, pz) for px, pz in arch_profile(x, bottom, width, spring)]
    curve_tube(prefix + "_BrickReveal", arch_points, 0.12, brick, target, role="opening_return")
    sash_points = [(px, plane_y + outward * 0.03, pz) for px, pz in arch_profile(x, bottom + 0.08, inner_width, spring)]
    curve_tube(prefix + "_SashPerimeter", sash_points, 0.07, iron, target, role="window_frame")
    crown = spring + inner_width / 2
    for offset in (-inner_width / 4, 0, inner_width / 4):
        box(prefix + f"_Mullion_{offset:.2f}", (x + offset, plane_y + outward * 0.03, (bottom + crown) / 2), (0.08, 0.07, crown - bottom - 0.12), iron, target, bevel=0.012, role="window_frame")
    for z in (bottom + 1.08, spring):
        box(prefix + f"_Transom_{z:.2f}", (x, plane_y + outward * 0.03, z), (inner_width, 0.07, 0.08), iron, target, bevel=0.012, role="window_frame")
    # Short room sidewalls prove that the warm layer is not coplanar with glass.
    for xx in (x - inner_width / 2 - 0.08, x + inner_width / 2 + 0.08):
        box(prefix + f"_RoomSide_{xx:.2f}", (xx, (plane_y + room_y) / 2, (bottom + spring) / 2), (0.12, abs(room_y - plane_y), spring - bottom + 0.5), brick, target, role="room_enclosure")


def arch_window_x(prefix, y, surface_x, outward, width, bottom, spring, brick, iron, glass, occupied, target):
    inner_width = width - 0.34
    plane_x = surface_x - outward * 0.22
    room_x = surface_x - outward * 0.92
    profile = arch_profile(y, bottom + 0.08, inner_width, spring)
    prism_x(prefix + "_Glass", profile, 0.035, glass, target, x=plane_x, role="optical_glass")
    prism_x(prefix + "_OccupiedDepth", arch_profile(y, bottom + 0.16, inner_width - 0.22, spring - 0.05), 0.06, occupied, target, x=room_x, role="occupied_depth")
    arch_points = [(surface_x + outward * 0.07, py, pz) for py, pz in arch_profile(y, bottom, width, spring)]
    curve_tube(prefix + "_BrickReveal", arch_points, 0.12, brick, target, role="opening_return")
    sash_points = [(plane_x + outward * 0.03, py, pz) for py, pz in arch_profile(y, bottom + 0.08, inner_width, spring)]
    curve_tube(prefix + "_SashPerimeter", sash_points, 0.07, iron, target, role="window_frame")
    crown = spring + inner_width / 2
    for offset in (-inner_width / 4, 0, inner_width / 4):
        box(prefix + f"_Mullion_{offset:.2f}", (plane_x + outward * 0.03, y + offset, (bottom + crown) / 2), (0.07, 0.08, crown - bottom - 0.12), iron, target, bevel=0.012, role="window_frame")
    for z in (bottom + 1.08, spring):
        box(prefix + f"_Transom_{z:.2f}", (plane_x + outward * 0.03, y, z), (0.07, inner_width, 0.08), iron, target, bevel=0.012, role="window_frame")
    for yy in (y - inner_width / 2 - 0.08, y + inner_width / 2 + 0.08):
        box(prefix + f"_RoomSide_{yy:.2f}", ((plane_x + room_x) / 2, yy, (bottom + spring) / 2), (abs(room_x - plane_x), 0.12, spring - bottom + 0.5), brick, target, role="room_enclosure")


def ground_glazing_y(prefix, x, surface_y, outward, width, iron, glass, timber, target, *, entrance=False):
    bottom, height = 0.62, 3.72
    center_z = bottom + height / 2
    pane_y = surface_y - outward * 0.20
    box(prefix + "_Pane", (x, pane_y, center_z), (width - 0.22, 0.035, height), glass, target, role="optical_glass")
    for xx in (x - width / 2, x + width / 2):
        box(prefix + f"_Jamb_{xx:.2f}", (xx, surface_y + outward * 0.03, center_z), (0.12, 0.16, height + 0.22), iron, target, bevel=0.015, role="window_frame")
    for z in (bottom, bottom + height, bottom + 2.55):
        box(prefix + f"_Rail_{z:.2f}", (x, surface_y + outward * 0.03, z), (width, 0.16, 0.10), iron, target, bevel=0.012, role="window_frame")
    for index in range(1, 4):
        xx = x - width / 2 + width * index / 4
        box(prefix + f"_Mullion_{index}", (xx, surface_y + outward * 0.03, center_z), (0.08, 0.14, height), iron, target, bevel=0.012, role="window_frame")
    if entrance:
        for xx in (x - 0.72, x + 0.72):
            box(prefix + f"_DoorStile_{xx:.2f}", (xx, surface_y + outward * 0.08, 1.75), (0.10, 0.18, 2.35), timber, target, bevel=0.02, role="door_frame")
        box(prefix + "_DoorRail", (x, surface_y + outward * 0.08, 0.88), (1.55, 0.18, 0.42), timber, target, bevel=0.025, role="door_leaf")
        box(prefix + "_Threshold", (x, surface_y + outward * 0.30, 0.18), (2.1, 0.65, 0.18), timber, target, bevel=0.025, role="grade_contact")


def ground_glazing_x(prefix, y, surface_x, outward, width, iron, glass, target):
    bottom, height = 0.62, 3.72
    center_z = bottom + height / 2
    pane_x = surface_x - outward * 0.20
    box(prefix + "_Pane", (pane_x, y, center_z), (0.035, width - 0.22, height), glass, target, role="optical_glass")
    for yy in (y - width / 2, y + width / 2):
        box(prefix + f"_Jamb_{yy:.2f}", (surface_x + outward * 0.03, yy, center_z), (0.16, 0.12, height + 0.22), iron, target, bevel=0.015, role="window_frame")
    for z in (bottom, bottom + height, bottom + 2.55):
        box(prefix + f"_Rail_{z:.2f}", (surface_x + outward * 0.03, y, z), (0.16, width, 0.10), iron, target, bevel=0.012, role="window_frame")
    for index in range(1, 4):
        yy = y - width / 2 + width * index / 4
        box(prefix + f"_Mullion_{index}", (surface_x + outward * 0.03, yy, center_z), (0.14, 0.08, height), iron, target, bevel=0.012, role="window_frame")


def railing_segment_y(prefix, x0, x1, y, iron, target):
    z0, zm, z1 = 9.30, 9.61, 9.92
    for suffix, z in (("Bottom", z0), ("Middle", zm), ("Top", z1)):
        box(prefix + "_" + suffix, ((x0 + x1) / 2, y, z), (x1 - x0, 0.038, 0.038), iron, target, role="parapet_railing")
    count = max(4, int((x1 - x0) / 0.34))
    for index in range(count + 1):
        x = x0 + (x1 - x0) * index / count
        box(prefix + f"_Post_{index}", (x, y, (z0 + z1) / 2), (0.026, 0.036, z1 - z0), iron, target, role="parapet_railing")
    for index in range(count):
        xa = x0 + (x1 - x0) * index / count
        xb = x0 + (x1 - x0) * (index + 1) / count
        for half, low, high in (("Lower", z0, zm), ("Upper", zm, z1)):
            curve_tube(prefix + f"_{half}X1_{index}", [(xa, y, low), (xb, y, high)], 0.012, iron, target, role="parapet_railing")
            curve_tube(prefix + f"_{half}X2_{index}", [(xa, y, high), (xb, y, low)], 0.012, iron, target, role="parapet_railing")


def railing_segment_x(prefix, y0, y1, x, iron, target):
    z0, zm, z1 = 9.30, 9.61, 9.92
    for suffix, z in (("Bottom", z0), ("Middle", zm), ("Top", z1)):
        box(prefix + "_" + suffix, (x, (y0 + y1) / 2, z), (0.038, y1 - y0, 0.038), iron, target, role="parapet_railing")
    count = max(4, int((y1 - y0) / 0.34))
    for index in range(count + 1):
        y = y0 + (y1 - y0) * index / count
        box(prefix + f"_Post_{index}", (x, y, (z0 + z1) / 2), (0.036, 0.026, z1 - z0), iron, target, role="parapet_railing")
    for index in range(count):
        ya = y0 + (y1 - y0) * index / count
        yb = y0 + (y1 - y0) * (index + 1) / count
        for half, low, high in (("Lower", z0, zm), ("Upper", zm, z1)):
            curve_tube(prefix + f"_{half}X1_{index}", [(x, ya, low), (x, yb, high)], 0.012, iron, target, role="parapet_railing")
            curve_tube(prefix + f"_{half}X2_{index}", [(x, ya, high), (x, yb, low)], 0.012, iron, target, role="parapet_railing")


def gable_top_profile(center=0.0, wide=5.2, main_radius=1.08, shoulder_offset=1.85, shoulder_radius=0.42, base_z=9.58):
    left = center - wide / 2
    right = center + wide / 2
    top = [(left, 9.22), (left, 9.48)]
    # Small side lobe, shallow shoulder, source-defining central semicircle.
    for index in range(7):
        angle = math.pi - math.pi * index / 6
        top.append((center - shoulder_offset + math.cos(angle) * shoulder_radius, 9.56 + math.sin(angle) * shoulder_radius))
    top.extend([(center - 1.38, 9.44), (center - main_radius, base_z)])
    for index in range(13):
        angle = math.pi - math.pi * index / 12
        top.append((center + math.cos(angle) * main_radius, base_z + math.sin(angle) * main_radius))
    top.extend([(center + 1.38, 9.44)])
    for index in range(7):
        angle = math.pi - math.pi * index / 6
        top.append((center + shoulder_offset + math.cos(angle) * shoulder_radius, 9.56 + math.sin(angle) * shoulder_radius))
    top.extend([(right, 9.48), (right, 9.22)])
    return top


def corner_finial_profile(center):
    """Tall faceted corner pinnacle measured from the locked 60-degree view."""
    return [
        (center - 0.42, 9.24), (center - 0.42, 10.10),
        (center - 0.30, 10.10), (center, 10.48),
        (center + 0.30, 10.10), (center + 0.42, 10.10),
        (center + 0.42, 9.24),
    ]


def identity_plane_y(name, center_x, y, z, size, material, target):
    vertices = [
        (center_x - size / 2, y, z - size / 2),
        (center_x + size / 2, y, z - size / 2),
        (center_x + size / 2, y, z + size / 2),
        (center_x - size / 2, y, z + size / 2),
    ]
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], [(0, 1, 2, 3)])
    mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
    target.objects.link(obj)
    mark_building(obj, "registered_identity")
    uv = obj.data.uv_layers.new(name="UVMap")
    for loop, value in zip(uv.data, ((0, 0), (1, 0), (1, 1), (0, 1))):
        loop.uv = value
    return obj


def identity_plane_x(name, center_y, x, z, size, material, target):
    vertices = [
        (x, center_y - size / 2, z - size / 2),
        (x, center_y - size / 2, z + size / 2),
        (x, center_y + size / 2, z + size / 2),
        (x, center_y + size / 2, z - size / 2),
    ]
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], [(0, 1, 2, 3)])
    mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
    target.objects.link(obj)
    mark_building(obj, "registered_identity")
    uv = obj.data.uv_layers.new(name="UVMap")
    for loop, value in zip(uv.data, ((0, 0), (1, 0), (1, 1), (0, 1))):
        loop.uv = value
    return obj


def lantern_axis_y(prefix, center_y, length, width, base_z, ridge_z, iron, glass, stone, target):
    x0, x1 = -width / 2, width / 2
    y0, y1 = center_y - length / 2, center_y + length / 2
    wall_top = base_z + 0.55
    for x in (x0, x1):
        box(prefix + f"_CurbSide_{x}", (x, center_y, base_z), (0.22, length, 0.34), stone, target, bevel=0.025, role="roof_contact")
        box(prefix + f"_GlassWall_{x}", (x, center_y, base_z + 0.35), (0.035, length - 0.2, 0.55), glass, target, role="roof_lantern_glass")
    for y in (y0, y1):
        box(prefix + f"_CurbEnd_{y}", (0, y, base_z), (width, 0.22, 0.34), stone, target, bevel=0.025, role="roof_contact")
        end_profile = [(x0, base_z + 0.08), (x1, base_z + 0.08), (x1, wall_top), (0, ridge_z), (x0, wall_top)]
        prism_y(prefix + f"_GlazedEnd_{y}", end_profile, 0.035, glass, target, y=y, role="roof_lantern_glass")
        curve_tube(prefix + f"_EndFrame_{y}", [(x0, y, wall_top), (0, y, ridge_z), (x1, y, wall_top)], 0.045, iron, target, role="roof_lantern_frame")
    left = [(x0, y0, wall_top), (0, y0, ridge_z), (0, y1, ridge_z), (x0, y1, wall_top)]
    right = [(0, y0, ridge_z), (x1, y0, wall_top), (x1, y1, wall_top), (0, y1, ridge_z)]
    for name, verts in (("LeftSlope", left), ("RightSlope", right)):
        mesh = bpy.data.meshes.new(prefix + name + "_Mesh")
        mesh.from_pydata(verts, [], [(0, 1, 2, 3)])
        mesh.materials.append(glass)
        obj = bpy.data.objects.new(prefix + name, mesh)
        target.objects.link(obj)
        mark_building(obj, "roof_lantern_glass")
    curve_tube(prefix + "_Ridge", [(0, y0, ridge_z), (0, y1, ridge_z)], 0.055, iron, target, role="roof_lantern_frame")
    for index in range(7):
        y = y0 + length * index / 6
        curve_tube(prefix + f"_Rib_{index}", [(x0, y, wall_top), (0, y, ridge_z), (x1, y, wall_top)], 0.045, iron, target, role="roof_lantern_frame")


def lantern_axis_x(prefix, center_x, center_y, length, width, base_z, ridge_z, iron, glass, stone, target):
    x0, x1 = center_x - length / 2, center_x + length / 2
    y0, y1 = center_y - width / 2, center_y + width / 2
    wall_top = base_z + 0.55
    for y in (y0, y1):
        box(prefix + f"_CurbSide_{y}", (center_x, y, base_z), (length, 0.22, 0.34), stone, target, bevel=0.025, role="roof_contact")
        box(prefix + f"_GlassWall_{y}", (center_x, y, base_z + 0.35), (length - 0.2, 0.035, 0.55), glass, target, role="roof_lantern_glass")
    for x in (x0, x1):
        box(prefix + f"_CurbEnd_{x}", (x, center_y, base_z), (0.22, width, 0.34), stone, target, bevel=0.025, role="roof_contact")
        end_profile = [(y0, base_z + 0.08), (y1, base_z + 0.08), (y1, wall_top), (center_y, ridge_z), (y0, wall_top)]
        prism_x(prefix + f"_GlazedEnd_{x}", end_profile, 0.035, glass, target, x=x, role="roof_lantern_glass")
        curve_tube(prefix + f"_EndFrame_{x}", [(x, y0, wall_top), (x, center_y, ridge_z), (x, y1, wall_top)], 0.045, iron, target, role="roof_lantern_frame")
    front = [(x0, y0, wall_top), (x0, center_y, ridge_z), (x1, center_y, ridge_z), (x1, y0, wall_top)]
    back = [(x0, center_y, ridge_z), (x0, y1, wall_top), (x1, y1, wall_top), (x1, center_y, ridge_z)]
    for name, verts in (("FrontSlope", front), ("BackSlope", back)):
        mesh = bpy.data.meshes.new(prefix + name + "_Mesh")
        mesh.from_pydata(verts, [], [(0, 1, 2, 3)])
        mesh.materials.append(glass)
        obj = bpy.data.objects.new(prefix + name, mesh)
        target.objects.link(obj)
        mark_building(obj, "roof_lantern_glass")
    curve_tube(prefix + "_Ridge", [(x0, center_y, ridge_z), (x1, center_y, ridge_z)], 0.055, iron, target, role="roof_lantern_frame")
    for index in range(7):
        x = x0 + length * index / 6
        curve_tube(prefix + f"_Rib_{index}", [(x, y0, wall_top), (x, center_y, ridge_z), (x, y1, wall_top)], 0.045, iron, target, role="roof_lantern_frame")


def face_object(name, vertices, material, target, role):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], [tuple(range(len(vertices)))])
    mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
    target.objects.link(obj)
    mark_building(obj, role)
    return obj


def wall_between(name, start, end, z_center, height, thickness, material, target, role):
    x0, y0 = start
    x1, y1 = end
    length = math.hypot(x1 - x0, y1 - y0)
    obj = box(name, ((x0 + x1) / 2, (y0 + y1) / 2, z_center), (length, thickness, height), material, target, role=role)
    obj.rotation_euler[2] = math.atan2(y1 - y0, x1 - x0)
    return obj


def bar_between_3d(name, start, end, thickness, material, target, role):
    """Capped square frame member whose ends terminate at the supplied nodes."""
    start_v, end_v = Vector(start), Vector(end)
    delta = end_v - start_v
    obj = box(name, (start_v + end_v) / 2, (thickness, thickness, delta.length), material, target, role=role)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = delta.to_track_quat("Z", "Y")
    return obj


def joined_mesh_from_faces(name, face_coordinates, material, target, role):
    """Create one shared-vertex surface from a sequence of coordinate faces."""
    vertices = []
    indices = {}
    faces = []
    for coordinates in face_coordinates:
        face = []
        for coordinate in coordinates:
            key = tuple(round(float(value), 6) for value in coordinate)
            if key not in indices:
                indices[key] = len(vertices)
                vertices.append(tuple(coordinate))
            face.append(indices[key])
        faces.append(tuple(face))
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
    target.objects.link(obj)
    mark_building(obj, role)
    return obj


def joined_t_lantern(prefix, iron, glass, flashing, target):
    """One joined T monitor with a shared skin, continuous curb, and bounded nodes."""
    x_outer, x_stem = 4.10, 1.55
    y_back, y_cross, y_front = 1.55, -1.55, -4.70
    base_z, eave_z, ridge_z = 9.12, 10.02, 11.18
    outline = [
        (-x_outer, y_cross), (-x_stem, y_cross), (-x_stem, y_front),
        (x_stem, y_front), (x_stem, y_cross), (x_outer, y_cross),
        (x_outer, y_back), (-x_outer, y_back),
    ]
    outer = [
        (-4.42, -1.87), (-1.87, -1.87), (-1.87, -5.02), (1.87, -5.02),
        (1.87, -1.87), (4.42, -1.87), (4.42, 1.87), (-4.42, 1.87),
    ]
    inner = [
        (-3.96, -1.40), (-1.40, -1.40), (-1.40, -4.55), (1.40, -4.55),
        (1.40, -1.40), (3.96, -1.40), (3.96, 1.40), (-3.96, 1.40),
    ]

    flashing_faces = []
    for index in range(len(outline)):
        nxt = (index + 1) % len(outline)
        flashing_faces.extend([
            [(outer[index][0], outer[index][1], base_z - 0.10), (outer[nxt][0], outer[nxt][1], base_z - 0.10),
             (outline[nxt][0], outline[nxt][1], base_z + 0.02), (outline[index][0], outline[index][1], base_z + 0.02)],
            [(outer[index][0], outer[index][1], base_z - 0.20), (outer[nxt][0], outer[nxt][1], base_z - 0.20),
             (outer[nxt][0], outer[nxt][1], base_z - 0.10), (outer[index][0], outer[index][1], base_z - 0.10)],
        ])
    joined_mesh_from_faces(prefix + "_ContinuousFlashingSkirt", flashing_faces, flashing, target, "roof_contact")

    curb_faces = []
    for index in range(len(outline)):
        nxt = (index + 1) % len(outline)
        curb_faces.extend([
            [(outline[index][0], outline[index][1], base_z), (outline[nxt][0], outline[nxt][1], base_z),
             (outline[nxt][0], outline[nxt][1], base_z + 0.32), (outline[index][0], outline[index][1], base_z + 0.32)],
            [(inner[index][0], inner[index][1], 8.50), (inner[nxt][0], inner[nxt][1], 8.50),
             (inner[nxt][0], inner[nxt][1], base_z + 0.32), (inner[index][0], inner[index][1], base_z + 0.32)],
            [(inner[index][0], inner[index][1], base_z + 0.32), (inner[nxt][0], inner[nxt][1], base_z + 0.32),
             (outline[nxt][0], outline[nxt][1], base_z + 0.32), (outline[index][0], outline[index][1], base_z + 0.32)],
        ])
    joined_mesh_from_faces(prefix + "_ContinuousCurbAndRoofReturn", curb_faces, iron, target, "roof_contact")

    glass_faces = []
    for index in range(len(outline)):
        nxt = (index + 1) % len(outline)
        glass_faces.append([
            (outline[index][0], outline[index][1], base_z + 0.32),
            (outline[nxt][0], outline[nxt][1], base_z + 0.32),
            (outline[nxt][0], outline[nxt][1], eave_z),
            (outline[index][0], outline[index][1], eave_z),
        ])
    glass_faces.extend([
        [(-x_outer, 0, ridge_z), (x_outer, 0, ridge_z), (x_outer, y_back, eave_z), (-x_outer, y_back, eave_z)],
        [(-x_outer, y_cross, eave_z), (-x_outer, 0, ridge_z), (-x_stem, 0, ridge_z), (-x_stem, y_cross, eave_z)],
        [(x_stem, y_cross, eave_z), (x_stem, 0, ridge_z), (x_outer, 0, ridge_z), (x_outer, y_cross, eave_z)],
        [(-x_stem, y_front, eave_z), (0, y_front, ridge_z), (0, y_cross, ridge_z), (-x_stem, y_cross, eave_z)],
        [(0, y_front, ridge_z), (x_stem, y_front, eave_z), (x_stem, y_cross, eave_z), (0, y_cross, ridge_z)],
        [(-x_stem, y_cross, eave_z), (-x_stem, 0, ridge_z), (0, 0, ridge_z), (0, y_cross, ridge_z)],
        [(0, y_cross, ridge_z), (0, 0, ridge_z), (x_stem, 0, ridge_z), (x_stem, y_cross, eave_z)],
        [(-x_outer, y_cross, eave_z), (-x_outer, y_back, eave_z), (-x_outer, 0, ridge_z)],
        [(x_outer, y_back, eave_z), (x_outer, y_cross, eave_z), (x_outer, 0, ridge_z)],
        [(-x_stem, y_front, eave_z), (x_stem, y_front, eave_z), (0, y_front, ridge_z)],
    ])
    joined_mesh_from_faces(prefix + "_JoinedGlazedEnvelope", glass_faces, glass, target, "roof_lantern_glass")

    for index in range(len(outline)):
        nxt = (index + 1) % len(outline)
        bar_between_3d(prefix + f"_EaveFrame_{index}", (*outline[index], eave_z), (*outline[nxt], eave_z), 0.085, iron, target, "roof_lantern_frame")
    bar_between_3d(prefix + "_CrossRidge", (-x_outer, 0, ridge_z), (x_outer, 0, ridge_z), 0.11, iron, target, "roof_lantern_frame")
    bar_between_3d(prefix + "_StemRidge", (0, y_front, ridge_z), (0, 0, ridge_z), 0.11, iron, target, "roof_lantern_frame")
    bar_between_3d(prefix + "_LeftValley", (-x_stem, y_cross, eave_z), (0, 0, ridge_z), 0.09, iron, target, "roof_lantern_frame")
    bar_between_3d(prefix + "_RightValley", (x_stem, y_cross, eave_z), (0, 0, ridge_z), 0.09, iron, target, "roof_lantern_frame")
    box(prefix + "_ResolvedTNode", (0, 0, ridge_z), (0.22, 0.22, 0.22), iron, target, bevel=0.025, role="roof_lantern_frame")

    def framed_slope(label, start, ridge, end):
        bar_between_3d(prefix + label + "A", start, ridge, 0.078, iron, target, "roof_lantern_frame")
        bar_between_3d(prefix + label + "B", ridge, end, 0.078, iron, target, "roof_lantern_frame")

    for index, x in enumerate((-3.15, -2.30, 2.30, 3.15)):
        framed_slope(f"_CrossRib_{index}_", (x, y_cross, eave_z), (x, 0, ridge_z), (x, y_back, eave_z))
    for index, y in enumerate((-3.95, -3.15, -2.35)):
        framed_slope(f"_StemRib_{index}_", (-x_stem, y, eave_z), (0, y, ridge_z), (x_stem, y, eave_z))
    framed_slope("_CrossEndLeft_", (-x_outer, y_cross, eave_z), (-x_outer, 0, ridge_z), (-x_outer, y_back, eave_z))
    framed_slope("_CrossEndRight_", (x_outer, y_cross, eave_z), (x_outer, 0, ridge_z), (x_outer, y_back, eave_z))
    framed_slope("_StemEnd_", (-x_stem, y_front, eave_z), (0, y_front, ridge_z), (x_stem, y_front, eave_z))
    for index, (x, y) in enumerate(((-x_outer, -0.72), (-x_outer, 0.72), (x_outer, -0.72), (x_outer, 0.72), (-x_stem, -3.45), (-x_stem, -2.35), (x_stem, -3.45), (x_stem, -2.35))):
        bar_between_3d(prefix + f"_VerticalMullion_{index}", (x, y, base_z + 0.32), (x, y, eave_z), 0.074, iron, target, "roof_lantern_frame")


def add_press(prefix, location, timber, iron, target):
    x, y, z = location
    box(prefix + "_Base", (x, y, z + 0.22), (1.25, 1.0, 0.44), iron, target, bevel=0.06, role="printing_press")
    box(prefix + "_Bed", (x, y, z + 0.72), (1.4, 1.1, 0.16), timber, target, bevel=0.035, role="printing_press")
    for xx in (x - 0.48, x + 0.48):
        box(prefix + f"_Post_{xx}", (xx, y, z + 1.42), (0.12, 0.15, 1.45), iron, target, bevel=0.025, role="printing_press")
    box(prefix + "_Head", (x, y, z + 1.95), (1.1, 0.35, 0.28), iron, target, bevel=0.05, role="printing_press")
    bpy.ops.mesh.primitive_torus_add(major_radius=0.48, minor_radius=0.06, location=(x + 0.72, y, z + 1.45), rotation=(math.pi / 2, 0, 0))
    wheel = bpy.context.object
    wheel.name = prefix + "_Flywheel"
    wheel.data.materials.append(iron)
    link_only(wheel, target)
    mark_building(wheel, "printing_press")


def add_detailed_press(prefix, location, timber, iron, paper, target):
    """Source-legible platen press: bed, platen, rollers, feed, flywheel, and frame."""
    x, y, z = location
    box(prefix + "_ContinuousBase", (x, y, z + 0.18), (1.85, 1.25, 0.36), iron, target, bevel=0.06, role="printing_press")
    for dx in (-0.68, 0.68):
        box(prefix + f"_CastSide_{dx}", (x + dx, y, z + 1.35), (0.20, 0.62, 2.25), iron, target, bevel=0.045, role="printing_press")
    box(prefix + "_Crown", (x, y, z + 2.45), (1.65, 0.70, 0.32), iron, target, bevel=0.06, role="printing_press")
    box(prefix + "_PressBed", (x, y - 0.18, z + 0.76), (1.60, 1.48, 0.16), timber, target, bevel=0.035, role="printing_press")
    platen = box(prefix + "_Platen", (x, y + 0.16, z + 1.45), (1.42, 0.16, 1.05), iron, target, bevel=0.045, role="printing_press")
    platen.rotation_euler[0] = math.radians(-11)
    box(prefix + "_PaperFeed", (x, y - 0.92, z + 1.05), (1.72, 0.72, 0.055), paper, target, bevel=0.018, role="printing_program")
    for dz in (1.92, 2.17):
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.12, depth=1.48, location=(x, y - 0.26, z + dz), rotation=(0, math.pi / 2, 0))
        roller = bpy.context.object
        roller.name = prefix + f"_InkRoller_{dz}"
        roller.data.materials.append(iron)
        link_only(roller, target)
        mark_building(roller, "printing_press")
    wheel_center = (x + 1.04, y, z + 1.52)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.62, minor_radius=0.065, location=wheel_center, rotation=(math.pi / 2, 0, 0))
    wheel = bpy.context.object
    wheel.name = prefix + "_Flywheel"
    wheel.data.materials.append(iron)
    link_only(wheel, target)
    mark_building(wheel, "printing_press")
    for angle in (0, math.pi / 2, math.pi, math.pi * 1.5):
        end = (wheel_center[0] + math.cos(angle) * 0.58, wheel_center[1], wheel_center[2] + math.sin(angle) * 0.58)
        curve_tube(prefix + f"_FlywheelSpoke_{angle:.2f}", [wheel_center, end], 0.035, iron, target, role="printing_press")
    box(prefix + "_TypeTray", (x - 1.25, y - 0.10, z + 1.04), (0.72, 1.15, 0.14), timber, target, bevel=0.025, role="printing_program")


def add_table(prefix, location, timber, iron, target):
    x, y, z = location
    box(prefix + "_Top", (x, y, z + 0.85), (2.0, 0.9, 0.12), timber, target, bevel=0.035, role="workshop_furniture")
    for dx in (-0.82, 0.82):
        for dy in (-0.32, 0.32):
            box(prefix + f"_Leg_{dx}_{dy}", (x + dx, y + dy, z + 0.42), (0.09, 0.09, 0.84), iron, target, bevel=0.015, role="workshop_furniture")


def build_scene():
    reset_scene()
    building = collection("RLASM_Building")
    interior = collection("RLASM_Occupied_Workshop")
    context = collection("Review_Context")

    clay = plain_material("Clay_Review", (0.58, 0.61, 0.62, 1), 0.78, building=True)
    brick_front = box_world_material("Barcelona_Tawny_Aged_Brick_AllFaces", "references/materials/barcelona-warm-brick-albedo-v1.png", 3.45, 0.80, bump=0.14, saturation=0.84, value=0.91)
    brick_side = brick_front
    iron = world_material("Barcelona_Blackened_Iron", "references/materials/barcelona-blackened-iron-albedo-v1.png", ("X", "Z"), 2.6, 0.42, metallic=0.58, bump=0.05, saturation=0.72, value=1.45)
    press_iron = world_material("Barcelona_Aged_Printing_Press_Iron", "references/materials/barcelona-blackened-iron-albedo-v1.png", ("X", "Z"), 2.2, 0.46, metallic=0.42, bump=0.035, saturation=0.48, value=2.85)
    press_bsdf = next(node for node in press_iron.node_tree.nodes if node.bl_idname == "ShaderNodeBsdfPrincipled")
    set_input(press_bsdf, ("Emission Color", "Emission"), (0.10, 0.075, 0.055, 1.0))
    set_input(press_bsdf, ("Emission Strength",), 0.08)
    roof = world_material("Barcelona_Aged_Patched_Roof_Membrane", "references/materials/barcelona-aged-roof-membrane-albedo-v2.png", ("X", "Y"), 17.0, 0.91, bump=0.07, saturation=0.72, value=0.82)
    stone = world_material("Barcelona_Limited_Warm_Gray_Stone", "references/materials/barcelona-warm-stone-albedo-v1.png", ("X", "Z"), 3.2, 0.78, bump=0.08, saturation=0.42, value=0.56)
    timber = world_material("Barcelona_Workshop_Timber", "references/materials/barcelona-workshop-timber-albedo-v1.png", ("X", "Z"), 2.4, 0.52, bump=0.08)
    glass = glass_material()
    lantern_glass = lantern_glass_material()
    occupied = warm_room_material(timber)
    identity = identity_material()
    if MODE == "clay":
        brick_front = brick_side = iron = press_iron = roof = stone = timber = occupied = identity = clay
        glass = plain_material("Clay_Glass", (0.38, 0.45, 0.46, 1), 0.45, building=True)
        lantern_glass = glass

    pavement = plain_material("Context_Pavement", (0.20, 0.22, 0.23, 1), 0.88)
    road = plain_material("Context_Road", (0.055, 0.065, 0.07, 1), 0.94)
    box("ReviewGround", (0, 0, -0.20), (38, 42, 0.30), pavement, context, bevel=0.04, role="context")
    box("ReviewStreet", (0, -14.2, -0.02), (34, 8.0, 0.14), road, context, bevel=0.02, role="context")

    # Closed grade-bearing foundation, floor plates and roof weathering plane.
    box("ContinuousDarkBaseBeam", (0, 0, 0.20), (W + 0.34, D + 0.34, 0.30), iron, building, bevel=0.035, role="foundation")
    box("GroundFloorSlab", (0, 0, 0.43), (W - 0.7, D - 0.7, 0.26), stone, interior, role="floor")
    box("UpperFloorSlab", (0, 0, FLOOR_Z), (W - 0.75, D - 0.75, 0.24), iron, interior, role="floor")
    roof_plane = box("FlatRoofWeatheringPlane", (0, 0, 8.82), (W - 0.55, D - 0.55, 0.28), roof, building, bevel=0.025, role="roof")
    # Two intersecting full-depth cutters form one continuous T aperture. The
    # overlap is inside the removed volume, so no opaque owner survives below
    # the joined monitor.
    roof_cross_cut = box("RoofCrossApertureCutter", (0, 0, 8.82), (8.05, 3.00, 1.10), clay, building, role="temporary")
    roof_stem_cut = box("RoofStemApertureCutter", (0, -3.06, 8.82), (3.00, 3.25, 1.10), clay, building, role="temporary")
    cut_with(roof_plane, roof_cross_cut)
    cut_with(roof_plane, roof_stem_cut)

    front_centers = (-4.7, 0.0, 4.7)
    side_centers = (-6.45, -2.15, 2.15, 6.45)

    # Front and rear structural grids, glazing and true arched upper openings.
    for label, surface_y, outward in (("Front", -D / 2, -1), ("Rear", D / 2, 1)):
        for x in (-7.28, -2.35, 2.35, 7.28):
            box(f"{label}_IronColumn_{x}", (x, surface_y + outward * 0.04, 4.55), (0.36, 0.48, 8.2), iron, building, bevel=0.035, role="structural_column")
            box(f"{label}_StoneFoot_{x}", (x, surface_y + outward * 0.02, 0.48), (0.62, 0.60, 0.82), stone, building, bevel=0.045, role="load_path")
        box(f"{label}_FloorBeam", (0, surface_y + outward * 0.04, FLOOR_Z), (W, 0.42, 0.38), iron, building, bevel=0.035, role="structural_beam")
        box(f"{label}_CorniceBeam", (0, surface_y + outward * 0.04, CORNICE_Z), (W + 0.12, 0.38, 0.28), iron, building, bevel=0.03, role="structural_beam")
        box(f"{label}_BaseSpandrel", (0, surface_y, 0.43), (W, 0.35, 0.52), iron, building, bevel=0.018, role="foundation")
        for index, x in enumerate(front_centers):
            ground_glazing_y(f"{label}_GroundBay_{index}", x, surface_y, outward, 4.28, iron, glass, timber, building, entrance=(index == 1))
            panel = box(f"{label}_UpperBrickBay_{index}", (x, surface_y, 6.62), (4.28, 0.46, 4.02), brick_front, building, role="brick_infill")
            cutter = prism_y(f"{label}_UpperCutter_{index}", arch_profile(x, 4.96, 3.18, 7.02), 1.2, clay, building, y=surface_y, role="temporary")
            cut_with(panel, cutter)
            arch_window_y(f"{label}_UpperWindow_{index}", x, surface_y, outward, 3.18, 4.96, 7.02, brick_front, iron, glass, occupied, building)
            box(f"{label}_SteelSill_{index}", (x, surface_y + outward * 0.11, 4.90), (3.34, 0.40, 0.11), iron, building, bevel=0.018, role="opening_return")
        for index, x in enumerate((-6.60 + 0.55 * item for item in range(25))):
            wall_y = surface_y + outward * 0.05
            neck_y = surface_y + outward * 0.25
            head_y = surface_y + outward * 0.47
            profile = [(wall_y, 8.27), (wall_y, 8.60), (head_y, 8.60), (head_y, 8.51), (neck_y, 8.47), (neck_y, 8.38), (wall_y, 8.34)]
            prism_x(f"{label}_ProjectingScrollConsole_{index}", profile, 0.12, brick_front, building, x=x, role="cornice_support")

    # Side grids continue the exact construction language rather than boxes.
    for label, surface_x, outward in (("Left", -W / 2, -1), ("Right", W / 2, 1)):
        for y in (-8.72, -4.30, 0.0, 4.30, 8.72):
            box(f"{label}_IronColumn_{y}", (surface_x + outward * 0.04, y, 4.55), (0.48, 0.36, 8.2), iron, building, bevel=0.035, role="structural_column")
            box(f"{label}_StoneFoot_{y}", (surface_x + outward * 0.02, y, 0.48), (0.60, 0.62, 0.82), stone, building, bevel=0.045, role="load_path")
        box(f"{label}_FloorBeam", (surface_x + outward * 0.04, 0, FLOOR_Z), (0.42, D, 0.38), iron, building, bevel=0.035, role="structural_beam")
        box(f"{label}_CorniceBeam", (surface_x + outward * 0.04, 0, CORNICE_Z), (0.38, D + 0.12, 0.28), iron, building, bevel=0.03, role="structural_beam")
        box(f"{label}_BaseSpandrel", (surface_x, 0, 0.43), (0.35, D, 0.52), iron, building, bevel=0.018, role="foundation")
        for index, y in enumerate(side_centers):
            ground_glazing_x(f"{label}_GroundBay_{index}", y, surface_x, outward, 3.90, iron, glass, building)
            panel = box(f"{label}_UpperBrickBay_{index}", (surface_x, y, 6.62), (0.46, 3.90, 4.02), brick_side, building, role="brick_infill")
            cut_arch_x(panel, surface_x, y, 2.86, 4.96, 7.12, building, clay)
            arch_window_x(f"{label}_UpperWindow_{index}", y, surface_x, outward, 2.86, 4.96, 7.12, brick_side, iron, glass, occupied, building)
            box(f"{label}_SteelSill_{index}", (surface_x + outward * 0.11, y, 4.90), (0.40, 3.00, 0.11), iron, building, bevel=0.018, role="opening_return")
        for index, y in enumerate((-8.45 + 0.65 * item for item in range(27))):
            wall_x = surface_x + outward * 0.05
            neck_x = surface_x + outward * 0.25
            head_x = surface_x + outward * 0.47
            profile = [(wall_x, 8.27), (wall_x, 8.60), (head_x, 8.60), (head_x, 8.51), (neck_x, 8.47), (neck_x, 8.38), (wall_x, 8.34)]
            prism_y(f"{label}_ProjectingScrollConsole_{index}", profile, 0.12, brick_side, building, y=y, role="cornice_support")

    # Four physical parapet centers, corner pylons, and bounded iron lattice.
    front_rear_profiles = (
        ("Front", -9.06, -9.31, brick_front, dict(wide=5.2, main_radius=1.08, shoulder_offset=1.85, shoulder_radius=0.42, base_z=9.58)),
        ("Rear", 9.06, 9.31, brick_front, dict(wide=4.8, main_radius=0.94, shoulder_offset=1.68, shoulder_radius=0.34, base_z=9.60)),
    )
    for label, y, outside, mat, parameters in front_rear_profiles:
        top_profile = gable_top_profile(**parameters)
        bound = parameters["wide"] / 2
        gable_profile = [(-bound, 9.18)] + top_profile + [(bound, 9.18)]
        prism_y(label + "_CentralParapet", gable_profile, 0.48, mat, building, y=y, role="identity_geometry")
        coping = [(x, outside, z + 0.03) for x, z in top_profile]
        curve_tube(label + "_ParapetCoping", coping, 0.085, brick_front, building, role="weathering_contact")
        box(label + "_RosetteCarrier", (0, outside, 10.18), (1.04, 0.08, 1.04), brick_front, building, bevel=0.06, role="identity_carrier")
        if MODE != "clay":
            identity_plane_y(label + "_RegisteredRosette", 0, outside + math.copysign(0.055, outside), 10.18, 0.94, identity, building)
        relief_y = outside + math.copysign(0.08, outside)
        for side in (-1, 1):
            points = [(side * 2.16, relief_y, 9.57), (side * 1.78, relief_y, 10.02), (side * 1.38, relief_y, 9.66), (side * 1.62, relief_y, 9.56), (side * 2.16, relief_y, 9.57)]
            curve_tube(label + f"_BoundedShoulderRelief_{side}", points, 0.026, iron, building, role="registered_relief_geometry")
        railing_segment_y(label + "_RailLeft", -7.15, -2.75, outside, iron, building)
        railing_segment_y(label + "_RailRight", 2.75, 7.15, outside, iron, building)
    side_profiles = (
        ("Left", -7.56, -7.81, brick_side, dict(wide=5.0, main_radius=1.00, shoulder_offset=1.72, shoulder_radius=0.36, base_z=9.60)),
        ("Right", 7.56, 7.81, brick_side, dict(wide=5.1, main_radius=1.02, shoulder_offset=1.78, shoulder_radius=0.38, base_z=9.59)),
    )
    for label, x, outside, mat, parameters in side_profiles:
        side_top_profile = gable_top_profile(**parameters)
        bound = parameters["wide"] / 2
        side_gable_profile = [(-bound, 9.18)] + side_top_profile + [(bound, 9.18)]
        prism_x(label + "_CentralParapet", side_gable_profile, 0.48, mat, building, x=x, role="identity_geometry")
        coping = [(outside, y, z + 0.03) for y, z in side_top_profile]
        curve_tube(label + "_ParapetCoping", coping, 0.085, brick_side, building, role="weathering_contact")
        box(label + "_RosetteCarrier", (outside, 0, 10.18), (0.08, 1.04, 1.04), brick_side, building, bevel=0.06, role="identity_carrier")
        if MODE != "clay":
            identity_plane_x(label + "_RegisteredRosette", 0, outside + math.copysign(0.055, outside), 10.18, 0.94, identity, building)
        relief_x = outside + math.copysign(0.08, outside)
        for side in (-1, 1):
            points = [(relief_x, side * 2.10, 9.57), (relief_x, side * 1.74, 10.00), (relief_x, side * 1.36, 9.66), (relief_x, side * 1.59, 9.56), (relief_x, side * 2.10, 9.57)]
            curve_tube(label + f"_BoundedShoulderRelief_{side}", points, 0.026, iron, building, role="registered_relief_geometry")
        railing_segment_x(label + "_RailFront", -8.65, -2.75, outside, iron, building)
        railing_segment_x(label + "_RailRear", 2.75, 8.65, outside, iron, building)

    for x in (-7.25, 7.25):
        for y in (-8.75, 8.75):
            prism_y(f"CornerBrickFinialY_{x}_{y}", corner_finial_profile(x), 0.50, brick_front, building, y=y, role="parapet_support")
            prism_x(f"CornerBrickFinialX_{x}_{y}", corner_finial_profile(y), 0.50, brick_front, building, x=x, role="parapet_support")

    # One joined, source-locked T monitor; no overlapping shed primitives.
    joined_t_lantern("JoinedTLantern", iron, lantern_glass, roof, building)

    # Occupied printing program on both levels, plus a connected stair.
    for index, position in enumerate(((3.3, -1.0, 0.55), (-2.0, 3.3, 0.55), (3.8, 3.8, 0.55))):
        add_press(f"GroundPress_{index}", position, timber, press_iron, interior)
    add_detailed_press("PrimaryGroundPlatenPress", (-4.00, -5.85, 0.55), timber, press_iron, stone, interior)
    add_detailed_press("PrimaryUpperPlatenPress", (-3.90, -7.15, 4.72), timber, press_iron, stone, interior)
    for index, position in enumerate(((0, -4.2, 0.55), (3.6, 3.4, 0.55), (-3.7, 0.8, 0.55), (0.2, 3.2, 0.55))):
        add_table(f"GroundTable_{index}", position, timber, iron, interior)
    for index, position in enumerate(((-3.1, -2.4, 4.75), (2.7, 2.2, 4.75))):
        add_table(f"UpperTable_{index}", position, timber, iron, interior)
    # Type cabinets and paper shelves.
    for index, y in enumerate((-4.8, -2.8, -0.8, 1.2, 3.2, 5.2)):
        box(f"TypeCabinet_{index}", (6.15, y, 1.65), (0.75, 1.35, 2.2), timber, interior, bevel=0.04, role="workshop_furniture")
        for drawer in range(5):
            box(f"TypeCabinet_{index}_Drawer_{drawer}", (5.75, y, 0.82 + drawer * 0.36), (0.06, 1.08, 0.24), iron, interior, bevel=0.012, role="workshop_furniture")
    for step in range(11):
        box(f"StairTread_{step}", (-5.5, 5.8 - step * 0.32, 0.65 + step * 0.35), (1.35, 0.42, 0.14), timber, interior, bevel=0.02, role="circulation")
    curve_tube("StairHandrail", [(-6.15, 5.95, 1.25), (-6.15, 2.55, 5.10)], 0.055, iron, interior, role="circulation")

    # Restrained warm luminaires belong to rooms, not glass.
    if MODE != "clay":
        for index, (x, y, z) in enumerate(((-3.5, -3.0, 3.2), (3.2, -1.0, 3.2), (-1.5, 3.0, 3.2), (-2.8, -2.0, 7.0), (2.5, 2.4, 7.0))):
            data = bpy.data.lights.new(f"WorkshopLamp_{index}", "AREA")
            data.energy = 230
            data.shape = "DISK"
            data.size = 1.3
            data.color = (1.0, 0.55, 0.26)
            lamp = bpy.data.objects.new(f"WorkshopLamp_{index}", data)
            lamp.location = (x, y, z)
            interior.objects.link(lamp)
            lamp.rotation_euler = (0, 0, 0)
        proof_data = bpy.data.lights.new("PrimaryPressProofLight", "AREA")
        proof_data.energy = 105
        proof_data.shape = "DISK"
        proof_data.size = 3.0
        proof_data.color = (1.0, 0.76, 0.54)
        proof_light = bpy.data.objects.new("PrimaryPressProofLight", proof_data)
        proof_light.location = (-3.1, -8.2, 3.7)
        proof_light.rotation_euler = (Vector((-4.0, -5.8, 1.4)) - proof_light.location).to_track_quat("-Z", "Y").to_euler()
        interior.objects.link(proof_light)

    return building, interior, context


def point_camera(name, location, target, lens=48):
    data = bpy.data.cameras.new(name + "_Data")
    data.lens = lens
    data.sensor_width = 36
    camera = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(camera)
    camera.location = location
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    return camera


def setup_render():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 1050
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    scene.world.color = (0.035, 0.045, 0.052)
    try:
        scene.view_settings.look = "AgX - Medium Low Contrast"
    except TypeError:
        pass
    scene.view_settings.exposure = 0.65
    sun_data = bpy.data.lights.new("NeutralSun", "SUN")
    sun_data.energy = 2.0
    sun_data.angle = math.radians(18)
    sun_data.color = (1.0, 0.94, 0.86)
    sun = bpy.data.objects.new("NeutralSun", sun_data)
    scene.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(30), math.radians(-24), math.radians(-32))
    for name, location, energy, size in (
        ("KeyFill", (-12, -16, 21), 1250, 9.0),
        ("RearFill", (13, 12, 17), 950, 8.0),
        ("TopFill", (0, 0, 25), 850, 10.0),
    ):
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        obj = bpy.data.objects.new(name, data)
        obj.location = location
        scene.collection.objects.link(obj)
        obj.rotation_euler = (Vector((0, 0, 5)) - obj.location).to_track_quat("-Z", "Y").to_euler()


def render_views():
    setup_render()
    scene = bpy.context.scene
    if MODE == "clay":
        output_dir = ROOT / "clay"
        views = {
            "front": ((0, -33, 6.4), (0, 0, 5.3), 52),
            "front_corner": ((-31, -36, 21), (0, 0, 5.2), 54),
            "aerial": ((34, -41, 39), (0, 0, 5.4), 55),
            "left_side": ((-38, 0, 7.0), (0, 0, 5.2), 55),
            "rear_side": ((29, 35, 22), (0, 0, 5.2), 54),
        }
    elif MODE == "press":
        output_dir = ROOT / "renders"
        views = {
            "workshop_interior": ((4.80, -7.50, 2.90), (-1.50, -1.00, 1.20), 32),
            "printing_press_close": ((-0.20, -8.80, 4.00), (-4.05, -5.78, 1.42), 32),
        }
    elif MODE == "proof":
        output_dir = ROOT / "renders"
        views = {
            "front": ((0, -33, 6.4), (0, 0, 5.3), 52),
            "front_corner": ((-31, -36, 21), (0, 0, 5.2), 54),
            "glass_close": ((-4.10, -15.0, 6.7), (-4.10, -7.2, 6.05), 55),
            "lantern_below_oblique": ((0.30, -6.75, 5.35), (0, -0.85, 10.10), 27),
            "workshop_interior": ((4.80, -7.50, 2.90), (-1.50, -1.00, 1.20), 32),
            "printing_press_close": ((-0.20, -8.80, 4.00), (-4.05, -5.78, 1.42), 32),
            "roof_lantern_close": ((12.0, -11.5, 16.5), (0, 0, 9.7), 62),
            "aerial": ((34, -41, 39), (0, 0, 5.4), 55),
            "rear_side": ((29, 35, 22), (0, 0, 5.2), 54),
        }
    else:
        output_dir = ROOT / "renders"
        views = {
            "front": ((0, -33, 6.4), (0, 0, 5.3), 52),
            "front_corner": ((-31, -36, 21), (0, 0, 5.2), 54),
            "aerial": ((34, -41, 39), (0, 0, 5.4), 55),
            "left_side": ((-38, 0, 7.0), (0, 0, 5.2), 55),
            "right_side": ((38, 0, 7.0), (0, 0, 5.2), 55),
            "rear": ((0, 34, 6.8), (0, 0, 5.2), 52),
            "rear_side": ((29, 35, 22), (0, 0, 5.2), 54),
            "facade_close": ((-3.0, -18.5, 6.5), (-1.0, -8.7, 6.3), 58),
            "architecture_close": ((-8.5, -17.0, 12.5), (0, -8.7, 9.7), 62),
            "glass_close": ((-4.10, -15.0, 6.7), (-4.10, -7.2, 6.05), 55),
            "roof_lantern_close": ((12.0, -11.5, 16.5), (0, 0, 9.7), 62),
            "lantern_below_oblique": ((0.30, -6.75, 5.35), (0, -0.85, 10.10), 27),
            "workshop_interior": ((4.80, -7.50, 2.90), (-1.50, -1.00, 1.20), 32),
            "printing_press_close": ((-0.20, -8.80, 4.00), (-4.05, -5.78, 1.42), 32),
        }
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, (location, target, lens) in views.items():
        camera = point_camera("Camera_" + name, location, target, lens)
        scene.camera = camera
        scene.render.filepath = str(output_dir / f"{name}.png")
        bpy.ops.render.render(write_still=True)


def write_evidence():
    renders = []
    for path in sorted((ROOT / "renders").glob("*.png")):
        renders.append({"path": str(path.relative_to(ROOT)).replace("\\", "/"), "bytes": path.stat().st_size, "sha256": sha256(path)})
    building_objects = [obj for obj in bpy.data.objects if obj.get("rlasm_building_object")]
    materials = []
    for material in bpy.data.materials:
        if material.get("rlasm_status"):
            materials.append({
                "name": material.name,
                "status": material.get("rlasm_status"),
                "source_sha256": material.get("rlasm_source_sha256"),
                "generic_fallback": bool(material.get("rlasm_generic_fallback", False)),
            })
    payload = {
        "schema": "cityprompt.rlasm.v6.builder-evidence@1",
        "candidate": ROOT.name,
        "status": "render_complete_pending_builder_pixel_review",
        "object_count": len(building_objects),
        "role_counts": {},
        "materials": materials,
        "generic_fallback_count": sum(1 for item in materials if item["generic_fallback"]),
        "registered_identity_count": sum(1 for obj in building_objects if obj.get("rlasm_role") == "registered_identity"),
        "renders": renders,
        "keeper_status": "NOT_A_KEEPER"
    }
    for obj in building_objects:
        role = obj.get("rlasm_role", "unknown")
        payload["role_counts"][role] = payload["role_counts"].get(role, 0) + 1
    (ROOT / "evidence/builder-evidence.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def source_plain_material(name, color, source_relative, roughness=0.7, metallic=0.0):
    material = plain_material(name, color, roughness, metallic, building=True)
    source = ROOT / source_relative
    material["rlasm_status"] = "source_specific_finished"
    material["rlasm_source_sha256"] = sha256(source)
    material["rlasm_generic_fallback"] = False
    return material


def rectangular_opening_y(panel, prefix, center_x, center_z, width, height, surface_y, outward, brick, stone, timber, glass, occupied, room_wall, target):
    # The Boolean operand must use the wall authority so Blender assigns the
    # newly cut jamb faces to brick, not to a thin unintended stone seam.
    cutter = box(prefix + "_Cutter", (center_x, surface_y, center_z), (width, 1.35, height), brick, target, role="temporary")
    cut_with(panel, cutter)
    exterior_y = surface_y + outward * 0.26
    reveal_y = surface_y - outward * 0.02
    sash_y = surface_y - outward * 0.23
    pane_y = surface_y - outward * 0.29
    # Place the room-depth owner behind real furniture rather than directly
    # behind the pane. This preserves optical depth without blocking the
    # source-required domestic program.
    room_y = surface_y - outward * (D - 0.65)
    jamb = 0.13
    surround = 0.12
    for side in (-1, 1):
        box(prefix + f"_BrickReveal_{side}", (center_x + side * (width / 2 - 0.050), reveal_y, center_z), (0.14, 0.47, height), brick, target, bevel=0.010, role="opening_return")
    box(prefix + "_StoneLintel", (center_x, exterior_y, center_z + height / 2 + surround / 2), (width + 0.26, 0.16, surround), stone, target, bevel=0.020, role="opening_return")
    box(prefix + "_StoneSill", (center_x, exterior_y + outward * 0.04, center_z - height / 2 - 0.06), (width + 0.30, 0.24, 0.13), stone, target, bevel=0.020, role="opening_return")
    for side in (-1, 1):
        box(prefix + f"_SashJamb_{side}", (center_x + side * (width / 2 - jamb / 2), sash_y, center_z), (jamb, 0.12, height - 0.12), timber, target, bevel=0.018, role="window_frame")
    box(prefix + "_SashHead", (center_x, sash_y, center_z + height / 2 - jamb / 2), (width - 0.12, 0.12, jamb), timber, target, bevel=0.018, role="window_frame")
    box(prefix + "_SashSill", (center_x, sash_y, center_z - height / 2 + jamb / 2), (width - 0.12, 0.12, jamb), timber, target, bevel=0.018, role="window_frame")
    box(prefix + "_MeetingRail", (center_x, sash_y + outward * 0.01, center_z), (width - 0.18, 0.14, 0.10), timber, target, bevel=0.015, role="window_frame")
    box(prefix + "_CenterMullion", (center_x, sash_y + outward * 0.01, center_z), (0.085, 0.14, height - 0.20), timber, target, bevel=0.012, role="window_frame")
    box(prefix + "_OpticalPane", (center_x, pane_y, center_z), (width - 0.24, 0.045, height - 0.24), glass, target, role="optical_glass")
    # A narrow back-wall witness establishes the separately offset occupied
    # layer without becoming an opaque card over the real domestic program.
    box(prefix + "_OccupiedDepth", (center_x - width * 0.29, room_y, center_z), (width * 0.16, 0.05, height * 0.56), occupied, target, role="occupied_depth")


def rectangular_opening_x(panel, prefix, center_y, center_z, width, height, surface_x, outward, brick, stone, timber, glass, occupied, room_wall, target):
    cutter = box(prefix + "_Cutter", (surface_x, center_y, center_z), (1.35, width, height), brick, target, role="temporary")
    cut_with(panel, cutter)
    exterior_x = surface_x + outward * 0.26
    reveal_x = surface_x - outward * 0.02
    sash_x = surface_x - outward * 0.23
    pane_x = surface_x - outward * 0.29
    room_x = surface_x - outward * (W - 0.65)
    jamb = 0.13
    surround = 0.12
    for side in (-1, 1):
        box(prefix + f"_BrickReveal_{side}", (reveal_x, center_y + side * (width / 2 - 0.050), center_z), (0.47, 0.14, height), brick, target, bevel=0.010, role="opening_return")
    box(prefix + "_StoneLintel", (exterior_x, center_y, center_z + height / 2 + surround / 2), (0.16, width + 0.26, surround), stone, target, bevel=0.020, role="opening_return")
    box(prefix + "_StoneSill", (exterior_x + outward * 0.04, center_y, center_z - height / 2 - 0.06), (0.24, width + 0.30, 0.13), stone, target, bevel=0.020, role="opening_return")
    for side in (-1, 1):
        box(prefix + f"_SashJamb_{side}", (sash_x, center_y + side * (width / 2 - jamb / 2), center_z), (0.12, jamb, height - 0.12), timber, target, bevel=0.018, role="window_frame")
    box(prefix + "_SashHead", (sash_x, center_y, center_z + height / 2 - jamb / 2), (0.12, width - 0.12, jamb), timber, target, bevel=0.018, role="window_frame")
    box(prefix + "_SashSill", (sash_x, center_y, center_z - height / 2 + jamb / 2), (0.12, width - 0.12, jamb), timber, target, bevel=0.018, role="window_frame")
    box(prefix + "_MeetingRail", (sash_x + outward * 0.01, center_y, center_z), (0.14, width - 0.18, 0.10), timber, target, bevel=0.015, role="window_frame")
    box(prefix + "_CenterMullion", (sash_x + outward * 0.01, center_y, center_z), (0.14, 0.085, height - 0.20), timber, target, bevel=0.012, role="window_frame")
    box(prefix + "_OpticalPane", (pane_x, center_y, center_z), (0.045, width - 0.24, height - 0.24), glass, target, role="optical_glass")
    box(prefix + "_OccupiedDepth", (room_x, center_y + width * 0.29, center_z), (0.05, width * 0.16, height * 0.56), occupied, target, role="occupied_depth")


def entrance_y(panel, prefix, center_x, surface_y, outward, brick, stone, timber, glass, occupied, room_wall, target):
    width, height, center_z = 1.35, 2.55, 1.64
    cutter = box(prefix + "_Cutter", (center_x, surface_y, center_z), (width, 1.35, height), brick, target, role="temporary")
    cut_with(panel, cutter)
    exterior_y = surface_y + outward * 0.27
    leaf_y = surface_y - outward * 0.22
    for side in (-1, 1):
        box(prefix + f"_BrickReveal_{side}", (center_x + side * 0.63, surface_y - outward * 0.01, center_z), (0.10, 0.46, height), brick, target, bevel=0.018, role="opening_return")
        box(prefix + f"_TimberJamb_{side}", (center_x + side * 0.60, leaf_y, center_z), (0.12, 0.14, height - 0.10), timber, target, bevel=0.018, role="door_frame")
    box(prefix + "_StoneLintel", (center_x, exterior_y, center_z + height / 2 + 0.10), (1.67, 0.24, 0.18), stone, target, bevel=0.025, role="opening_return")
    # Exact variant-0 oak schedule: paneled leaf, narrow centered glazed inset,
    # and a diamond-leaded transom rather than one large clear field.
    # The oak leaf owns the opaque panels but is physically absent behind the
    # narrow upper light.  Splitting the backing prevents the glass from
    # becoming a decorative card pasted over solid timber.
    box(prefix + "_OakLeafLowerBacking", (center_x, leaf_y, 0.92), (1.06, 0.10, 1.12), timber, target, bevel=0.022, role="door_leaf")
    for side in (-1, 1):
        box(prefix + f"_OakLeafUpperBacking_{side}", (center_x + side * 0.34, leaf_y, 1.73), (0.42, 0.10, 0.90), timber, target, bevel=0.018, role="door_leaf")
    for side in (-1, 1):
        box(prefix + f"_DoorStile_{side}", (center_x + side * 0.49, leaf_y, 1.33), (0.14, 0.12, 1.92), timber, target, bevel=0.020, role="door_leaf")
    for name, z, rail_h in (("BottomRail", 0.42, 0.16), ("LowerRail", 0.90, 0.12), ("LockRail", 1.28, 0.14), ("TopRail", 2.24, 0.14)):
        box(prefix + f"_{name}", (center_x, leaf_y, z), (0.90, 0.12, rail_h), timber, target, bevel=0.018, role="door_leaf")
    for side in (-1, 1):
        box(prefix + f"_RaisedLowerPanel_{side}", (center_x + side * 0.23, leaf_y + outward * 0.075, 0.68), (0.36, 0.045, 0.34), timber, target, bevel=0.022, role="door_leaf")
        box(prefix + f"_RaisedMiddlePanel_{side}", (center_x + side * 0.23, leaf_y + outward * 0.075, 1.08), (0.36, 0.045, 0.24), timber, target, bevel=0.020, role="door_leaf")
    box(prefix + "_NarrowUpperDoorGlass", (center_x, leaf_y - outward * 0.065, 1.73), (0.22, 0.035, 0.88), glass, target, role="optical_glass")
    for side in (-1, 1):
        box(prefix + f"_NarrowGlassJamb_{side}", (center_x + side * 0.16, leaf_y + outward * 0.02, 1.73), (0.08, 0.12, 1.00), timber, target, bevel=0.012, role="door_leaf")
    for z in (1.25, 2.21):
        box(prefix + f"_NarrowGlassRail_{z}", (center_x, leaf_y + outward * 0.02, z), (0.40, 0.12, 0.08), timber, target, bevel=0.012, role="door_leaf")
    box(prefix + "_DoorHandle", (center_x + 0.36, leaf_y + outward * 0.09, 1.28), (0.045, 0.055, 0.18), stone, target, bevel=0.012, role="door_hardware")
    transom_y = leaf_y - outward * 0.05
    box(prefix + "_DiamondTransomGlass", (center_x, transom_y, 2.55), (1.02, 0.045, 0.34), glass, target, role="optical_glass")
    diamond = [
        (center_x - 0.31, transom_y + outward * 0.025, 2.55),
        (center_x, transom_y + outward * 0.025, 2.70),
        (center_x + 0.31, transom_y + outward * 0.025, 2.55),
        (center_x, transom_y + outward * 0.025, 2.40),
    ]
    for index in range(4):
        bar_between_3d(prefix + f"_SingleDiamondLead_{index}", diamond[index], diamond[(index + 1) % 4], 0.022, timber, target, role="door_frame")
    box(prefix + "_OccupiedHall", (center_x, surface_y - outward * 0.78, 1.55), (1.0, 0.05, 2.15), occupied, target, role="occupied_depth")
    box(prefix + "_Threshold", (center_x, exterior_y + outward * 0.12, 0.28), (1.70, 0.52, 0.18), stone, target, bevel=0.025, role="grade_contact")


def amsterdam_bell_profile():
    return [
        (-4.20, 6.30), (-4.20, 7.13), (-3.68, 7.16), (-3.43, 7.48),
        (-3.36, 7.92), (-3.18, 8.38), (-2.94, 8.82), (-2.68, 9.18),
        (-2.39, 9.50), (-2.12, 9.86), (-1.90, 10.28), (-1.73, 10.76),
        (-1.62, 11.30), (-1.57, 11.88), (-1.55, 12.43), (-1.40, 12.92),
        (-1.14, 13.28), (-0.79, 13.52), (-0.40, 13.67), (0.0, 13.72),
        (0.40, 13.67), (0.79, 13.52), (1.14, 13.28), (1.40, 12.92),
        (1.55, 12.43), (1.57, 11.88), (1.62, 11.30), (1.73, 10.76),
        (1.90, 10.28), (2.12, 9.86), (2.39, 9.50), (2.68, 9.18),
        (2.94, 8.82), (3.18, 8.38), (3.36, 7.92), (3.43, 7.48),
        (3.68, 7.16), (4.20, 7.13), (4.20, 6.30),
    ]


def build_amsterdam_scene():
    reset_scene()
    building = collection("RLASM_Building")
    interior = collection("RLASM_Occupied_Residence")
    context = collection("Review_Context")

    clay = plain_material("Clay_Review", (0.58, 0.61, 0.62, 1), 0.78, building=True)
    brick = box_world_material("Amsterdam_Variant0_Aged_Red_Brick", "references/materials/amsterdam-aged-red-brick-albedo-v1.png", 2.85, 0.82, bump=0.13, saturation=0.95, value=0.90)
    roof = world_material("Amsterdam_Variant0_Weathered_Dutch_Roof_Tile", "references/materials/amsterdam-weathered-dutch-roof-tile-albedo-v8.png", ("Y", "X"), 2.15, 0.80, bump=0.07, saturation=0.76, value=0.72)
    stone = box_world_material("Amsterdam_Variant0_Warm_Sandstone", "references/materials/amsterdam-warm-sandstone-albedo-v1.png", 2.6, 0.81, bump=0.06, saturation=0.80, value=0.62)
    terracotta = box_world_material("Amsterdam_Variant0_Integrated_Terracotta_Dressing", "references/materials/amsterdam-aged-red-brick-albedo-v1.png", 2.2, 0.76, bump=0.08, saturation=0.98, value=0.96)
    timber = box_world_material("Amsterdam_Variant0_Stained_Timber", "references/materials/amsterdam-stained-timber-albedo-v1.png", 2.2, 0.52, bump=0.07, saturation=0.72, value=0.68)
    door_oak = box_world_material("Amsterdam_Variant0_Warm_Oak_Door", "references/materials/amsterdam-stained-timber-albedo-v1.png", 1.6, 0.50, bump=0.055, saturation=0.78, value=1.08)
    zinc = source_plain_material("Amsterdam_Aged_Zinc", (0.24, 0.27, 0.28, 1), "references/catalogue/variant_0_angle_60.jpg", 0.48, 0.35)
    plaster = source_plain_material("Amsterdam_Warm_Interior_Plaster", (0.20, 0.145, 0.105, 1), "references/catalogue/variant_0.png", 0.84)
    textile = source_plain_material("Amsterdam_Domestic_Textile", (0.34, 0.19, 0.13, 1), "references/catalogue/variant_0.png", 0.88)
    glass = glass_material()
    occupied = warm_room_material(timber)
    if MODE == "clay":
        brick = roof = stone = terracotta = timber = door_oak = zinc = plaster = textile = occupied = clay
        glass = plain_material("Clay_Glass", (0.38, 0.45, 0.46, 1), 0.45, building=True)

    pavement = plain_material("Context_Pavement", (0.24, 0.25, 0.25, 1), 0.88)
    road = plain_material("Context_Road", (0.07, 0.075, 0.078, 1), 0.94)
    box("ReviewGround", (0, 0, -0.18), (30, 34, 0.28), pavement, context, bevel=0.04, role="context")
    box("ReviewStreet", (0, -11.8, -0.02), (28, 7.0, 0.14), road, context, bevel=0.02, role="context")

    box("ContinuousBrickFoundation", (0, 0, 0.18), (W + 0.18, D + 0.18, 0.36), brick, building, bevel=0.035, role="foundation")
    occupied_floors = {}
    for z in (0.36, 3.36, 6.42):
        occupied_floors[z] = box(f"OccupiedFloor_{z}", (0, 0, z), (W - 0.55, D - 0.55, 0.22), timber, interior, role="floor")

    front_y, rear_y = -D / 2, D / 2
    front_panel = box("FrontBrickCarrier", (0, front_y, 3.35), (W, 0.50, 6.30), brick, building, role="brick_infill")
    rear_panel = box("RearBrickCarrier", (0, rear_y, 3.35), (W, 0.50, 6.30), brick, building, role="brick_infill")
    left_panel = box("LeftBrickCarrier", (-W / 2, 0, 3.35), (0.50, D, 6.30), brick, building, role="brick_infill")
    right_panel = box("RightBrickCarrier", (W / 2, 0, 3.35), (0.50, D, 6.30), brick, building, role="brick_infill")

    for index, x in enumerate((-2.55, 2.55)):
        rectangular_opening_y(front_panel, f"FrontGroundWindow_{index}", x, 1.66, 1.42, 2.30, front_y, -1, brick, stone, timber, glass, occupied, plaster, building)
    entrance_y(front_panel, "FrontPublicEntrance", 0.0, front_y, -1, brick, stone, door_oak, glass, occupied, plaster, building)
    for index, x in enumerate((-2.55, 0.0, 2.55)):
        rectangular_opening_y(front_panel, f"FrontUpperWindow_{index}", x, 4.66, 1.38, 2.02, front_y, -1, brick, stone, timber, glass, occupied, plaster, building)

    for floor, z in enumerate((1.66, 4.66)):
        for index, x in enumerate((-2.55, 0.0, 2.55)):
            rectangular_opening_y(rear_panel, f"RearFloor{floor}Window_{index}", x, z, 1.32, 2.02, rear_y, 1, brick, stone, timber, glass, occupied, plaster, building)

    for label, panel, surface_x, outward in (("Left", left_panel, -W / 2, -1), ("Right", right_panel, W / 2, 1)):
        for floor, z in enumerate((1.66, 4.66)):
            for index, y in enumerate((-5.55, -1.85, 1.85, 5.55)):
                rectangular_opening_x(panel, f"{label}Floor{floor}Window_{index}", y, z, 1.26, 2.02, surface_x, outward, brick, stone, timber, glass, occupied, plaster, building)

    # The locked variant has a restrained eave/cornice datum, not generic
    # institutional stone ribbons at every floor.
    for z in (6.30,):
        box(f"FrontStoneCourse_{z}", (0, front_y - 0.28, z), (W + 0.24, 0.28, 0.13), stone, building, bevel=0.018, role="weathering_contact")
        box(f"RearStoneCourse_{z}", (0, rear_y + 0.28, z), (W + 0.24, 0.28, 0.13), stone, building, bevel=0.018, role="weathering_contact")
        box(f"LeftStoneCourse_{z}", (-W / 2 - 0.28, 0, z), (0.28, D + 0.24, 0.13), stone, building, bevel=0.018, role="weathering_contact")
        box(f"RightStoneCourse_{z}", (W / 2 + 0.28, 0, z), (0.28, D + 0.24, 0.13), stone, building, bevel=0.018, role="weathering_contact")

    left_roof_profile = [(-4.46, 6.42), (0.0, 11.55), (0.0, 11.82), (-4.60, 6.63)]
    right_roof_profile = [(0.0, 11.55), (4.46, 6.42), (4.60, 6.63), (0.0, 11.82)]
    left_roof = prism_y("LeftClosedSlateSlope", left_roof_profile, D - 0.38, roof, building, y=0, role="roof")
    right_roof = prism_y("RightClosedSlateSlope", right_roof_profile, D - 0.38, roof, building, y=0, role="roof")
    roof_dormer_cutter = box("RightSlopeDormerFullDepthCutter", (2.84, 0.75, 8.45), (1.18, 1.48, 2.12), brick, building, role="temporary")
    cut_with(right_roof, roof_dormer_cutter)
    for index, y in enumerate([(-7.10 + step * 0.52) for step in range(28)]):
        box(f"BoundedDutchRidgeCap_{index}", (0, y, 11.73), (0.34, 0.50, 0.20), roof, building, bevel=0.075, role="weathering_contact")
    for x in (-4.40, 4.40):
        curve_tube(f"EaveGutter_{x}", [(x, -7.42, 6.55), (x, 7.42, 6.55)], 0.075, zinc, building, role="weathering_contact")

    bell = amsterdam_bell_profile()
    bell_solid = [(-4.20, 6.28)] + bell + [(4.20, 6.28)]
    front_gable = prism_y("PhysicalBellGable", bell_solid, 0.58, brick, building, y=front_y - 0.05, role="identity_geometry")
    rectangular_opening_y(front_gable, "BellGableMainWindow", 0.0, 8.18, 1.42, 2.22, front_y - 0.05, -1, brick, stone, timber, glass, occupied, plaster, building)
    rectangular_opening_y(front_gable, "BellGableHoistWindow", 0.0, 10.82, 0.92, 1.42, front_y - 0.05, -1, brick, stone, timber, glass, occupied, plaster, building)
    smooth_coping = catmull_rom_open_2d(bell[1:-1], 5)
    profile_strip_y("BellGableContinuousTangentTerracottaCoping", smooth_coping, 0.105, 0.22, terracotta, building, y=front_y - 0.40, role="weathering_contact")
    # Compact tangent-smooth shoulder curls measured from the locked street
    # view; these are integrated masonry volutes, not applied gear rosettes.
    right_scroll = [(3.44, 7.40), (3.49, 7.51), (3.58, 7.58), (3.68, 7.59), (3.77, 7.54), (3.82, 7.45), (3.81, 7.36), (3.74, 7.31), (3.67, 7.33), (3.63, 7.39), (3.66, 7.43)]
    left_scroll = [(-x, z) for x, z in right_scroll]
    for side, scroll in ((-1, left_scroll), (1, right_scroll)):
        smooth_scroll = catmull_rom_open_2d(scroll, 5)
        profile_strip_y(f"BellIntegratedBrickScroll_{side}", smooth_scroll, 0.15, 0.34, brick, building, y=front_y - 0.43, role="identity_geometry")
        profile_strip_y(f"BellScrollTerracottaDressing_{side}", catmull_rom_open_2d(scroll[:6], 5), 0.042, 0.40, terracotta, building, y=front_y - 0.48, role="weathering_contact")

    # Fine seven-flute palmette from the locked crest cadence.
    box("BellPalmetteIntegratedTerracottaBase", (0, front_y - 0.43, 13.77), (0.30, 0.20, 0.07), terracotta, building, bevel=0.016, role="identity_geometry")
    crest_y = front_y - 0.43
    crest_tips = [(-0.19, 13.93), (-0.13, 13.99), (-0.07, 14.03), (0.0, 14.05), (0.07, 14.03), (0.13, 13.99), (0.19, 13.93)]
    for index, (tip_x, tip_z) in enumerate(crest_tips):
        base_x = tip_x * 0.30
        half = 0.020
        prism_y(f"BellPalmetteTerracottaFlute_{index}", [(base_x - half, 13.78), (tip_x - 0.010, tip_z - 0.026), (tip_x, tip_z), (tip_x + 0.010, tip_z - 0.026), (base_x + half, 13.78)], 0.17, terracotta, building, y=crest_y, role="identity_geometry")
    box("HoistingBeam", (0, front_y - 0.70, 12.10), (0.22, 1.72, 0.22), timber, building, bevel=0.026, role="load_path")
    box("HoistingBeamBearing", (0, front_y - 0.37, 12.10), (0.42, 0.20, 0.34), brick, building, bevel=0.018, role="load_path")

    rear_gable_profile = [(-4.20, 6.28), (0.0, 11.52), (4.20, 6.28)]
    rear_gable = prism_y("ClosedRearGable", rear_gable_profile, 0.55, brick, building, y=rear_y, role="brick_infill")
    rectangular_opening_y(rear_gable, "RearGableWindow", 0.0, 8.45, 1.22, 1.82, rear_y, 1, brick, stone, timber, glass, occupied, plaster, building)

    dormer_y, dormer_z = 0.75, 8.58
    dormer_carrier = box("ShedDormerPaleFrontCarrier", (3.42, dormer_y, dormer_z - 0.04), (0.48, 1.58, 1.56), stone, building, bevel=0.018, role="roof_contact")
    dormer_cutter = box("ShedDormerOpeningCutter", (3.55, dormer_y, dormer_z - 0.04), (1.10, 1.12, 1.12), stone, building, role="temporary")
    cut_with(dormer_carrier, dormer_cutter)
    for side_y in (-0.70, 0.70):
        box(f"ShedDormerPaleCheek_{side_y}", (2.98, dormer_y + side_y, dormer_z - 0.10), (1.24, 0.20, 1.62), stone, building, bevel=0.016, role="roof_contact")
        box(f"ShedDormerInteriorReturn_{side_y}", (3.18, dormer_y + side_y * 0.76, dormer_z - 0.04), (0.56, 0.07, 1.08), plaster, building, role="room_enclosure")
    box("ShedDormerWarmSill", (3.68, dormer_y, dormer_z - 0.64), (0.18, 1.38, 0.11), stone, building, bevel=0.016, role="opening_return")
    box("ShedDormerWarmHead", (3.66, dormer_y, dormer_z + 0.58), (0.16, 1.36, 0.10), stone, building, bevel=0.016, role="opening_return")
    for side_y in (-0.50, 0.50):
        box(f"ShedDormerSashJamb_{side_y}", (3.70, dormer_y + side_y, dormer_z), (0.10, 0.09, 1.20), timber, building, bevel=0.015, role="window_frame")
    for side_z in (-0.55, 0.55):
        box(f"ShedDormerSashRail_{side_z}", (3.70, dormer_y, dormer_z + side_z), (0.10, 1.18, 0.09), timber, building, bevel=0.015, role="window_frame")
    box("ShedDormerSashMullion", (3.70, dormer_y, dormer_z), (0.10, 0.08, 1.12), timber, building, bevel=0.012, role="window_frame")
    box("ShedDormerSashMeetingRail", (3.70, dormer_y, dormer_z), (0.10, 1.10, 0.08), timber, building, bevel=0.012, role="window_frame")
    box("ShedDormerGlass", (3.58, dormer_y, dormer_z), (0.04, 1.05, 1.04), glass, building, role="optical_glass")
    box("ShedDormerOccupiedAttic", (3.08, dormer_y, dormer_z), (0.05, 0.98, 0.96), occupied, building, role="occupied_depth")
    shed_cap_profile = [(2.30, 9.60), (3.88, 9.32), (3.88, 9.20), (2.30, 9.48)]
    prism_y("ShedDormerSeatedCap", shed_cap_profile, 1.68, roof, building, y=dormer_y, role="weathering_contact")
    slope_angle = math.radians(49.0)
    for side_y in (-0.86, 0.86):
        strip = box(f"ShedDormerContinuousRoofLegFlashing_{side_y}", (2.86, dormer_y + side_y, 8.39), (1.52, 0.24, 0.095), zinc, building, bevel=0.012, role="weathering_contact")
        strip.rotation_euler[1] = slope_angle
        counter_profile = [(2.30, 8.86), (3.58, 7.39), (3.58, 7.66), (2.30, 9.14)]
        prism_y(f"ShedDormerContinuousCounterFlashing_{side_y}", counter_profile, 0.13, zinc, building, y=dormer_y + side_y * 0.94, role="weathering_contact")
    apron_x = 3.62
    apron_z = 11.55 - (11.55 - 6.42) * (apron_x / 4.46) + 0.10
    apron = box("ShedDormerContinuousDownslopeApron", (apron_x, dormer_y, apron_z), (0.92, 1.88, 0.095), zinc, building, bevel=0.012, role="weathering_contact")
    apron.rotation_euler[1] = slope_angle
    box("ShedDormerApronTurnUp", (3.56, dormer_y, 7.62), (0.16, 1.72, 0.42), zinc, building, bevel=0.012, role="weathering_contact")

    # Unambiguous domestic program: living, kitchen/dining, bedroom/storage,
    # and two connected stair flights to the occupied attic floor.
    box("LivingSofaSeat", (-2.45, -5.95, 0.72), (1.85, 0.78, 0.34), textile, interior, bevel=0.10, role="residential_program")
    box("LivingSofaBack", (-2.45, -5.60, 1.12), (1.85, 0.18, 0.86), textile, interior, bevel=0.10, role="residential_program")
    for side in (-1, 1):
        box(f"LivingSofaArm_{side}", (-2.45 + side * 0.83, -5.95, 0.92), (0.18, 0.78, 0.70), textile, interior, bevel=0.09, role="residential_program")
        box(f"LivingSofaCushion_{side}", (-2.45 + side * 0.38, -6.05, 1.05), (0.62, 0.20, 0.48), plaster, interior, bevel=0.10, role="residential_program")
    box("KitchenCabinetRun", (2.40, -6.02, 0.80), (2.10, 0.58, 1.10), timber, interior, bevel=0.035, role="residential_program")
    box("KitchenStoneCounter", (2.40, -6.02, 1.38), (2.18, 0.66, 0.10), stone, interior, bevel=0.025, role="residential_program")
    box("KitchenRange", (2.40, -6.31, 1.08), (0.62, 0.16, 0.56), zinc, interior, bevel=0.025, role="residential_program")
    for index, x in enumerate((1.78, 2.40, 3.02)):
        box(f"KitchenCabinetDoor_{index}", (x, -6.325, 0.82), (0.48, 0.035, 0.72), timber, interior, bevel=0.018, role="residential_program")
        box(f"KitchenCabinetHandle_{index}", (x + 0.15, -6.348, 0.90), (0.025, 0.025, 0.18), zinc, interior, bevel=0.008, role="residential_program")
    box("DiningTable", (0.0, -2.70, 1.08), (1.55, 0.82, 0.12), timber, interior, bevel=0.025, role="residential_program")
    for dx in (-0.62, 0.62):
        box(f"DiningTableLeg_{dx}", (dx, -2.70, 0.64), (0.09, 0.09, 0.82), timber, interior, bevel=0.012, role="residential_program")
    box("UpperBedFrame", (2.45, -1.85, 3.72), (1.65, 2.10, 0.22), timber, interior, bevel=0.04, role="residential_program")
    box("UpperBedMattress", (2.45, -1.85, 3.92), (1.55, 1.98, 0.25), textile, interior, bevel=0.10, role="residential_program")
    box("UpperBedHeadboard", (2.45, -0.92, 4.38), (1.60, 0.16, 1.05), timber, interior, bevel=0.035, role="residential_program")
    box("UpperBedPillowLeft", (2.08, -1.08, 4.13), (0.58, 0.42, 0.18), plaster, interior, bevel=0.09, role="residential_program")
    box("UpperBedPillowRight", (2.82, -1.08, 4.13), (0.58, 0.42, 0.18), plaster, interior, bevel=0.09, role="residential_program")
    box("UpperWardrobe", (2.35, 0.42, 4.54), (0.62, 1.48, 2.20), timber, interior, bevel=0.035, role="residential_program")
    box("UpperBookcase", (-2.90, -1.20, 4.42), (0.48, 1.70, 1.92), timber, interior, bevel=0.025, role="residential_program")
    stair_y = 1.85
    flight_specs = [
        (0, -3.48, 0.30, stair_y - 0.56, 0.56),
        (1, -0.18, -0.30, stair_y + 0.56, 3.56),
    ]
    for flight, start_x, x_step, flight_y, base_z in flight_specs:
        for step in range(12):
            box(f"ConnectedStair_{flight}_{step}", (start_x + step * x_step, flight_y, base_z + step * 0.25), (0.38, 1.05, 0.12), timber, interior, bevel=0.015, role="circulation")
        start = (start_x, flight_y, base_z + 0.02)
        end = (start_x + 11 * x_step, flight_y, base_z + 11 * 0.25 + 0.02)
        for side in (-0.48, 0.48):
            bar_between_3d(f"StairStringer_{flight}_{side}", (start[0], start[1] + side, start[2]), (end[0], end[1] + side, end[2]), 0.09, timber, interior, role="circulation")
            bar_between_3d(f"StairHandrail_{flight}_{side}", (start[0], start[1] + side, start[2] + 0.88), (end[0], end[1] + side, end[2] + 0.88), 0.065, timber, interior, role="circulation")
            for post_index in (0, 4, 8, 11):
                post_x = start_x + post_index * x_step
                post_z = base_z + post_index * 0.25
                bar_between_3d(f"StairGuardPost_{flight}_{side}_{post_index}", (post_x, flight_y + side, post_z), (post_x, flight_y + side, post_z + 0.90), 0.055, timber, interior, role="circulation")
    box("StairMidLanding", (-0.08, stair_y, 3.45), (1.10, 2.30, 0.18), timber, interior, bevel=0.025, role="circulation")
    box("StairAtticLanding", (-3.45, stair_y, 6.45), (1.12, 2.30, 0.18), timber, interior, bevel=0.025, role="circulation")
    for landing_name, landing_x, landing_z in (("Mid", -0.08, 3.45), ("Attic", -3.45, 6.45)):
        for guard_y in (stair_y - 1.05, stair_y + 1.05):
            bar_between_3d(f"Stair{landing_name}LandingGuard_{guard_y}", (landing_x - 0.45, guard_y, landing_z), (landing_x - 0.45, guard_y, landing_z + 0.94), 0.06, timber, interior, role="circulation")
    for floor_z in (3.36, 6.42):
        stairwell_cutter = box(f"StairwellCut_{floor_z}", (-1.80, stair_y, floor_z), (4.25, 2.45, 0.62), timber, interior, role="temporary")
        cut_with(occupied_floors[floor_z], stairwell_cutter)

    if MODE != "clay":
        for index, (x, y, z) in enumerate(((2.5, -4.0, 2.7), (1.2, 0.0, 2.7), (-1.4, 4.0, 2.7), (0, -2.2, 5.8), (1.2, 2.7, 8.8), (-1.65, 1.85, 4.85))):
            data = bpy.data.lights.new(f"ResidenceLamp_{index}", "AREA")
            data.energy = 135
            data.shape = "DISK"
            data.size = 0.8
            data.color = (1.0, 0.58, 0.30)
            lamp = bpy.data.objects.new(f"ResidenceLamp_{index}", data)
            lamp.location = (x, y, z)
            lamp.rotation_euler = (0, 0, 0)
            interior.objects.link(lamp)

    return building, interior, context


def render_amsterdam_views():
    setup_render()
    scene = bpy.context.scene
    output_dir = ROOT / ("clay" if MODE == "clay" else "renders")
    if MODE == "clay":
        views = {
            "front": ((0, -44.0, 8.5), (0, 0, 7.2), 55),
            "front_corner": ((-31.0, -41.0, 22.0), (0, 0, 7.0), 55),
            "aerial": ((36, -45, 39), (0, 0, 7.0), 56),
            "left_side": ((-45, 0, 9.2), (0, 0, 7.0), 57),
            "rear_side": ((34, 41, 24), (0, 0, 7.0), 55),
        }
    else:
        views = {
            "front": ((0, -44.0, 8.5), (0, 0, 7.2), 55),
            "front_corner": ((-31.0, -41.0, 22.0), (0, 0, 7.0), 55),
            "aerial": ((36, -45, 39), (0, 0, 7.0), 56),
            "left_side": ((-45, 0, 9.2), (0, 0, 7.0), 57),
            "right_side": ((45, 0, 9.2), (0, 0, 7.0), 57),
            "rear": ((0, 45.0, 8.7), (0, 0, 7.0), 55),
            "rear_side": ((34, 41, 24), (0, 0, 7.0), 55),
            "facade_close": ((-7.0, -17.5, 7.0), (0, -7.5, 6.4), 58),
            "architecture_close": ((-4.8, -17.0, 13.8), (0, -7.6, 12.4), 62),
            "glass_close": ((-4.1, -12.4, 5.6), (-2.55, -7.25, 4.65), 62),
            "bell_gable_close": ((0, -17.2, 13.1), (0, -7.7, 12.35), 68),
            "dormer_contact_close": ((12.8, -4.5, 12.2), (3.2, 0.7, 8.65), 67),
            "true_top": ((0, 0, 60), (0, 0, 0.0), 58),
            "residential_interior_close": ((3.55, 0.80, 2.35), (-1.20, -4.75, 1.05), 31),
            "kitchen_living_close": ((2.55, -12.8, 1.95), (2.40, -5.95, 1.00), 55),
            "bedroom_close": ((11.8, -3.8, 5.65), (2.65, -1.25, 4.10), 60),
            "stair_circulation_close": ((-9.0, 0.60, 1.92), (-1.50, 1.85, 2.05), 68),
            "stair_upper_glass_close": ((-9.0, 3.10, 4.88), (-1.40, 1.85, 4.82), 68),
            "stair_interior_oblique": ((3.55, -4.40, 5.35), (-1.70, 1.85, 3.62), 42),
            "entrance_close": ((0.0, -13.2, 1.65), (0.0, -7.48, 1.42), 60),
        }
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, (location, target, lens) in views.items():
        camera = point_camera("Camera_" + name, location, target, lens)
        if name == "true_top":
            camera.data.type = "ORTHO"
            camera.data.ortho_scale = 19.5
            camera.rotation_euler = (0.0, 0.0, math.radians(90.0))
        scene.camera = camera
        scene.render.filepath = str(output_dir / f"{name}.png")
        bpy.ops.render.render(write_still=True)


build_amsterdam_scene()
render_amsterdam_views()
if MODE == "full":
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "amsterdam-bell-gable-house-v10.blend"))
    bpy.ops.export_scene.gltf(filepath=str(ROOT / "amsterdam-bell-gable-house-v10.glb"), export_format="GLB", export_yup=True)
    write_evidence()
elif MODE == "proof":
    write_evidence()
