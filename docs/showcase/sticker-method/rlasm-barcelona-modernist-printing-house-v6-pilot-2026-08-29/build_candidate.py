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
W, D = 15.0, 18.0
PLINTH_Z, FLOOR_Z, CORNICE_Z = 0.45, 4.55, 8.65


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
    material = bpy.data.materials.new("Barcelona_Neutral_Workshop_Glass")
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    set_input(bsdf, ("Base Color",), (0.68, 0.74, 0.72, 1.0))
    set_input(bsdf, ("Roughness",), 0.055)
    set_input(bsdf, ("Metallic",), 0.0)
    set_input(bsdf, ("IOR",), 1.46)
    set_input(bsdf, ("Transmission Weight", "Transmission"), 0.86)
    set_input(bsdf, ("Alpha",), 0.14)
    material.diffuse_color = (0.68, 0.74, 0.72, 0.14)
    if hasattr(material, "surface_render_method"):
        material.surface_render_method = "BLENDED"
    material["rlasm_status"] = "source_specific_optical"
    material["rlasm_optical_authority"] = "exact variant-2 front and oblique glazing"
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
    material.name = "Barcelona_Occupied_Workshop_Depth"
    nodes = material.node_tree.nodes
    bsdf = next(node for node in nodes if node.bl_idname == "ShaderNodeBsdfPrincipled")
    set_input(bsdf, ("Emission Color", "Emission"), (0.28, 0.11, 0.035, 1.0))
    set_input(bsdf, ("Emission Strength",), 0.20)
    set_input(bsdf, ("Alpha",), 0.13)
    set_input(bsdf, ("Transmission Weight", "Transmission"), 0.28)
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
        "status": "builder_pass_only_pending_independent_review",
        "object_count": len(building_objects),
        "role_counts": {},
        "materials": materials,
        "generic_fallback_count": sum(1 for item in materials if item["generic_fallback"]),
        "registered_identity_count": sum(1 for obj in building_objects if obj.get("rlasm_role") == "registered_identity"),
        "renders": renders,
        "keeper_status": "NOT_A_KEEPER_AWAITING_INDEPENDENT_REVIEW"
    }
    for obj in building_objects:
        role = obj.get("rlasm_role", "unknown")
        payload["role_counts"][role] = payload["role_counts"].get(role, 0) + 1
    (ROOT / "evidence/builder-evidence.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


build_scene()
render_views()
if MODE == "full":
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "barcelona-modernist-printing-house-v7.blend"))
    bpy.ops.export_scene.gltf(filepath=str(ROOT / "barcelona-modernist-printing-house-v7.glb"), export_format="GLB", export_yup=True)
    write_evidence()
elif MODE == "proof":
    write_evidence()
