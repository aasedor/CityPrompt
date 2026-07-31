"""Author the Wave 10 Prairie Courtyard Motor Inn LEGO family.

The assembled GLB is a complete two-storey L-shaped motor inn rather than a
generic hospitality box. It has deep-eaved hip roofs, fourteen repeated room
bays per level, physical low-E windows with occupied room depth, a continuous
exterior gallery, two structurally integrated open-tread stairs, a brick-and-
glass inside-corner lobby and porte-cochere, a fenced pool court, and a complete
rear service edge. A semantic LEGO stack remains available for imperfect
rectangle, L- and U-shaped user drawings.

Run with Blender 5.x from the repository root:

    blender --background --factory-startup --python \
      tools/archetype_compiler/generate_wave10_motor_inn_family.py -- \
      --output-root frontend/public/families --view-set pilot
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import bpy
from mathutils import Vector

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from generate_wave3_landmark_families import (
    aim_camera,
    box,
    clear_scene,
    cylinder,
    delete_objects,
    export_glb,
    facade_contract,
    load_skin_manifest,
    material,
    module_contract_markers,
    skin_material,
    texture_inventory,
)


FAMILY = "prairie-courtyard-motor-inn"
ARCHETYPE_ID = "highway_motor_hotel"
VARIANT_ID = "hotel_two_storey_motor_inn"
ALIASES = [
    ARCHETYPE_ID,
    VARIANT_ID,
    "prairie_courtyard_motor_inn",
    "two_storey_exterior_corridor_motel",
]
LABEL = "Highway Motor Hotel - Two-Storey Prairie Motor Inn"
GLASS_PROFILE = "low_iron_neutral"

NATIVE_WIDTH = 64.0
NATIVE_DEPTH = 36.0
NATIVE_HEIGHT = 9.25
NATIVE_FLOORS = 2
MIN_FLOORS = 1
MAX_FLOORS = 3
PODIUM_HEIGHT = 0.30
FLOOR_HEIGHT = 3.20
CROWN_HEIGHT = 0.72
ROOF_HEIGHT = 2.10

MAIN_WIDTH = 56.0
MAIN_FRONT_Y = 7.0
MAIN_REAR_Y = 18.0
RETURN_FACE_X = 17.0
RETURN_OUTER_X = 28.0
RETURN_FRONT_Y = -12.0
RETURN_REAR_Y = 18.0
ROOM_BAY_WIDTH = 4.20
MAIN_ROOM_CENTRES = tuple(-25.4 + index * ROOM_BAY_WIDTH for index in range(10))
RETURN_ROOM_CENTRES = (-9.3, -5.1, -0.9, 3.3)

COORDINATE_CONTRACT = {
    "units": "metres",
    "blender_up": "+Z",
    "gltf_up": "+Y (export_yup)",
    "origin": "bottom centre",
    "front_facade": "-Y in Blender, +Z in glTF",
    "transforms": "applied",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("frontend/public/families"),
    )
    parser.add_argument(
        "--view-set",
        default="all",
        help="preview, pilot, all, or one named render view",
    )
    parser.add_argument("--skip-renders", action="store_true")
    parser.add_argument("--skip-modules", action="store_true")
    parser.add_argument("--skip-assembled-export", action="store_true")
    parser.add_argument("--render-existing", action="store_true")
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(argv)


def bsdf_for(mat: bpy.types.Material) -> bpy.types.Node:
    return next(
        node
        for node in mat.node_tree.nodes
        if node.bl_idname == "ShaderNodeBsdfPrincipled"
    )


def grade_material(
    mat: bpy.types.Material,
    *,
    saturation: float = 1.0,
    value: float = 1.0,
) -> bpy.types.Material:
    socket = bsdf_for(mat).inputs["Base Color"]
    if socket.is_linked:
        source = socket.links[0].from_socket
        mat.node_tree.links.remove(socket.links[0])
        grade = mat.node_tree.nodes.new("ShaderNodeHueSaturation")
        grade.name = grade.label = "REFERENCE_LOCKED_GRADE"
        grade.inputs["Saturation"].default_value = saturation
        grade.inputs["Value"].default_value = value
        mat.node_tree.links.new(source, grade.inputs["Color"])
        mat.node_tree.links.new(grade.outputs["Color"], socket)
    return mat


def set_normal_strength(
    mat: bpy.types.Material,
    strength: float,
) -> bpy.types.Material:
    for node in mat.node_tree.nodes:
        if node.bl_idname == "ShaderNodeNormalMap":
            node.inputs["Strength"].default_value = strength
    return mat


def make_glass_material(
    assets: dict[str, str],
    *,
    lobby: bool = False,
) -> bpy.types.Material:
    name = (
        "MAT_W10_MOTOR_INN_LobbyLowEGlass"
        if lobby
        else "MAT_W10_MOTOR_INN_GuestRoomLowEGlass"
    )
    mat = material(
        name,
        (0.055, 0.095, 0.115, 0.30 if lobby else 0.34),
        0.060,
        metallic=0.015,
    )
    bsdf = bsdf_for(mat)
    if bsdf.inputs.get("Transmission Weight"):
        bsdf.inputs["Transmission Weight"].default_value = 0.91
    if bsdf.inputs.get("Coat Weight"):
        bsdf.inputs["Coat Weight"].default_value = 0.34
    if bsdf.inputs.get("Coat Roughness"):
        bsdf.inputs["Coat Roughness"].default_value = 0.055
    if bsdf.inputs.get("IOR"):
        bsdf.inputs["IOR"].default_value = 1.52
    if bsdf.inputs.get("Alpha"):
        bsdf.inputs["Alpha"].default_value = 0.30 if lobby else 0.34
    try:
        mat.surface_render_method = "BLENDED"
    except Exception:
        pass
    mat.use_transparency_overlap = False
    mat["glazing_profile"] = GLASS_PROFILE
    mat["glazing_lod"] = "physical_separate_pane"
    mat["skin_zone"] = "low_e_glass"
    mat["pbr_channels"] = json.dumps(
        ["albedo", "normal", "roughness", "ao", "depth", "emissive"]
    )
    mat["semantic_glass_mask"] = assets["glass_mask"]
    mat["semantic_opaque_mask"] = assets["opaque_mask"]
    mat["pane_recess_m"] = 0.18
    mat["interior_depth_m"] = 3.2 if not lobby else 8.0
    mat["source_variant_id"] = VARIANT_ID
    mat["generation_archetype_id"] = VARIANT_ID
    mat["reference_locked"] = True
    return mat


def load_palette(folder: Path) -> tuple[dict[str, bpy.types.Material], dict]:
    skin = load_skin_manifest(folder)
    if not skin:
        raise FileNotFoundError(folder / "textures" / "skin_manifest.json")
    near = {zone: values["near"] for zone, values in skin["zones"].items()}
    mats: dict[str, bpy.types.Material] = {}
    mats["stucco"] = set_normal_strength(
        grade_material(
            skin_material(
                "MAT_W10_MOTOR_INN_IvoryStucco",
                folder,
                near["ivory_stucco"],
                "ivory_stucco",
            ),
            saturation=0.72,
            value=0.88,
        ),
        0.30,
    )
    mats["brick"] = set_normal_strength(
        grade_material(
            skin_material(
                "MAT_W10_MOTOR_INN_RussetBrick",
                folder,
                near["russet_brick"],
                "russet_brick",
            ),
            saturation=0.92,
            value=0.78,
        ),
        0.55,
    )
    mats["shingle"] = set_normal_strength(
        grade_material(
            skin_material(
                "MAT_W10_MOTOR_INN_CharcoalShingle",
                folder,
                near["charcoal_shingles"],
                "charcoal_shingles",
            ),
            saturation=0.42,
            value=0.34,
        ),
        0.72,
    )
    mats["cedar"] = set_normal_strength(
        grade_material(
            skin_material(
                "MAT_W10_MOTOR_INN_CedarSoffit",
                folder,
                near["cedar_soffit"],
                "cedar_soffit",
            ),
            saturation=0.93,
            value=0.77,
        ),
        0.38,
    )
    mats["door"] = grade_material(
        skin_material(
            "MAT_W10_MOTOR_INN_KelpDoor",
            folder,
            near["kelp_door"],
            "kelp_door",
            metallic=0.12,
        ),
        saturation=0.72,
        value=0.64,
    )
    mats["steel"] = grade_material(
        skin_material(
            "MAT_W10_MOTOR_INN_BlackSteel",
            folder,
            near["black_steel"],
            "black_steel",
            metallic=0.50,
        ),
        saturation=0.36,
        value=0.43,
    )
    mats["concrete"] = set_normal_strength(
        grade_material(
            skin_material(
                "MAT_W10_MOTOR_INN_PaleConcrete",
                folder,
                near["pale_concrete"],
                "pale_concrete",
            ),
            saturation=0.30,
            value=0.86,
        ),
        0.18,
    )
    mats["pool"] = grade_material(
        skin_material(
            "MAT_W10_MOTOR_INN_PoolWater",
            folder,
            near["pool_water"],
            "pool_water",
            transmission=0.42,
        ),
        saturation=0.78,
        value=0.84,
    )
    pool_bsdf = bsdf_for(mats["pool"])
    if pool_bsdf.inputs.get("Roughness"):
        pool_bsdf.inputs["Roughness"].default_value = 0.08
    mats["asphalt"] = set_normal_strength(
        grade_material(
            skin_material(
                "MAT_W10_MOTOR_INN_Asphalt",
                folder,
                near["asphalt"],
                "asphalt",
            ),
            saturation=0.25,
            value=0.56,
        ),
        0.16,
    )
    mats["curtain"] = grade_material(
        skin_material(
            "MAT_W10_MOTOR_INN_RoomCurtain",
            folder,
            near["room_curtain"],
            "room_curtain",
        ),
        saturation=0.28,
        value=0.90,
    )
    mats["service"] = grade_material(
        skin_material(
            "MAT_W10_MOTOR_INN_ServiceMetal",
            folder,
            near["service_metal"],
            "service_metal",
            metallic=0.46,
        ),
        saturation=0.30,
        value=0.66,
    )
    mats["gravel"] = grade_material(
        skin_material(
            "MAT_W10_MOTOR_INN_LandscapeGravel",
            folder,
            near["landscape_gravel"],
            "landscape_gravel",
        ),
        saturation=0.62,
        value=0.72,
    )
    mats["prairie"] = grade_material(
        skin_material(
            "MAT_W10_MOTOR_INN_PrairiePlanting",
            folder,
            near["prairie_planting"],
            "prairie_planting",
        ),
        saturation=0.58,
        value=0.64,
    )
    mats["wood"] = grade_material(
        skin_material(
            "MAT_W10_MOTOR_INN_InteriorWood",
            folder,
            near["interior_wood"],
            "interior_wood",
        ),
        saturation=0.78,
        value=0.64,
    )
    mats["interior"] = grade_material(
        skin_material(
            "MAT_W10_MOTOR_INN_OccupiedGuestDepth",
            folder,
            near["interior"],
            "occupied_guest_room",
            emission_strength=0.30,
        ),
        saturation=0.62,
        value=0.63,
    )
    mats["light"] = skin_material(
        "MAT_W10_MOTOR_INN_WarmLight",
        folder,
        near["warm_light"],
        "warm_light",
        emission_strength=4.0,
    )
    mats["glass"] = make_glass_material(near["low_e_glass"])
    mats["lobby_glass"] = make_glass_material(near["low_e_glass"], lobby=True)
    mats["galvanized"] = material(
        "MAT_W10_MOTOR_INN_GalvanizedTread",
        (0.33, 0.36, 0.37, 1.0),
        0.34,
        metallic=0.72,
    )
    mats["dark"] = material(
        "MAT_W10_MOTOR_INN_InteriorShadow",
        (0.025, 0.031, 0.034, 1.0),
        0.74,
    )
    mats["bedding"] = material(
        "MAT_W10_MOTOR_INN_WarmBedding",
        (0.62, 0.55, 0.44, 1.0),
        0.86,
    )
    mats["white"] = material(
        "MAT_W10_MOTOR_INN_ParkingMarking",
        (0.80, 0.81, 0.77, 1.0),
        0.76,
    )
    mats["blackout"] = material(
        "MAT_W10_MOTOR_INN_BlackoutCurtain",
        (0.20, 0.22, 0.21, 1.0),
        0.93,
    )
    return mats, skin


def tag_object(
    obj: bpy.types.Object,
    *,
    component: str,
    level: int | None = None,
    variant: str = "reference_locked",
) -> bpy.types.Object:
    obj["family"] = FAMILY
    obj["component"] = component
    obj["source_variant_id"] = VARIANT_ID
    obj["generation_archetype_id"] = VARIANT_ID
    obj["reference_locked"] = True
    obj["reuse_keys"] = json.dumps(ALIASES)
    obj["variant_key"] = variant
    if level is not None:
        obj["level"] = level
    return obj


def b(
    name: str,
    size: tuple[float, float, float],
    location: tuple[float, float, float],
    mat: bpy.types.Material,
    *,
    bevel: float = 0.0,
    component: str,
    level: int | None = None,
    variant: str = "reference_locked",
) -> bpy.types.Object:
    return tag_object(
        box(name, size, location, mat, bevel),
        component=component,
        level=level,
        variant=variant,
    )


def c(
    name: str,
    radius: float,
    depth: float,
    location: tuple[float, float, float],
    mat: bpy.types.Material,
    *,
    vertices: int = 16,
    component: str,
    level: int | None = None,
    variant: str = "reference_locked",
) -> bpy.types.Object:
    return tag_object(
        cylinder(name, radius, depth, location, mat, vertices=vertices),
        component=component,
        level=level,
        variant=variant,
    )


def oriented_box(
    name: str,
    *,
    orientation: str,
    along_size: float,
    depth_size: float,
    height: float,
    along: float,
    wall: float,
    z: float,
    recess: float,
    mat: bpy.types.Material,
    component: str,
    level: int | None = None,
    bevel: float = 0.0,
    variant: str = "reference_locked",
) -> bpy.types.Object:
    """Place facade geometry whose exterior points toward -Y or -X."""
    if orientation == "south":
        size = (along_size, depth_size, height)
        location = (along, wall + recess, z)
    elif orientation == "west":
        size = (depth_size, along_size, height)
        location = (wall + recess, along, z)
    else:
        raise ValueError(orientation)
    return b(
        name,
        size,
        location,
        mat,
        bevel=bevel,
        component=component,
        level=level,
        variant=variant,
    )


def outward_box(
    name: str,
    *,
    orientation: str,
    along_size: float,
    depth_size: float,
    height: float,
    along: float,
    wall: float,
    z: float,
    recess: float,
    mat: bpy.types.Material,
    component: str,
    level: int | None = None,
    bevel: float = 0.0,
) -> bpy.types.Object:
    """Place rear facade geometry whose exterior points toward +Y or +X."""
    if orientation == "north":
        size = (along_size, depth_size, height)
        location = (along, wall - recess, z)
    elif orientation == "east":
        size = (depth_size, along_size, height)
        location = (wall - recess, along, z)
    else:
        raise ValueError(orientation)
    return b(
        name,
        size,
        location,
        mat,
        bevel=bevel,
        component=component,
        level=level,
    )


def rectangular_beam(
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    cross_x: float,
    cross_y: float,
    mat: bpy.types.Material,
    *,
    component: str,
) -> bpy.types.Object:
    a = Vector(start)
    d = Vector(end) - a
    midpoint = a + d * 0.5
    bpy.ops.mesh.primitive_cube_add(size=1, location=midpoint)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = (cross_x, cross_y, d.length)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0.0, 0.0, 1.0)).rotation_difference(
        d.normalized()
    )
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    return tag_object(obj, component=component)


def add_plant_tuft(
    objects: list[bpy.types.Object],
    mat: bpy.types.Material,
    *,
    name: str,
    x: float,
    y: float,
    base_z: float,
    scale: float,
) -> None:
    """Build a small irregular grass tuft instead of a cartoon cylinder."""
    seed_angle = x * 0.17 + y * 0.11
    for blade_index in range(4):
        angle = blade_index * math.tau / 4.0 + seed_angle
        height = scale * (0.40 + blade_index * 0.055)
        radius = scale * (0.050 - blade_index * 0.004)
        offset = scale * 0.07
        bpy.ops.mesh.primitive_cone_add(
            vertices=6,
            radius1=radius,
            radius2=0.006,
            depth=height,
            location=(
                x + math.cos(angle) * offset,
                y + math.sin(angle) * offset,
                base_z + height * 0.5,
            ),
        )
        blade = bpy.context.object
        blade.name = f"{name}_Blade_{blade_index}"
        blade.rotation_euler.x = math.sin(angle) * 0.14
        blade.rotation_euler.y = -math.cos(angle) * 0.14
        blade.data.materials.append(mat)
        objects.append(
            tag_object(
                blade,
                component="drought_tolerant_prairie_planting",
            )
        )


def add_shrub_cluster(
    objects: list[bpy.types.Object],
    mat: bpy.types.Material,
    *,
    name: str,
    x: float,
    y: float,
    base_z: float,
    scale: float,
) -> None:
    """Build a low multi-lobed shrub with intentionally irregular massing."""
    lobes = (
        (-0.22, -0.05, 0.78, 0.62, 0.50),
        (0.20, 0.08, 0.68, 0.74, 0.56),
        (0.02, 0.22, 0.60, 0.54, 0.46),
    )
    for lobe_index, (dx, dy, sx, sy, sz) in enumerate(lobes):
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=2,
            radius=1.0,
            location=(
                x + dx * scale,
                y + dy * scale,
                base_z + sz * scale * 0.55,
            ),
        )
        lobe = bpy.context.object
        lobe.name = f"{name}_Lobe_{lobe_index}"
        lobe.scale = (sx * scale, sy * scale, sz * scale)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        lobe.data.materials.append(mat)
        objects.append(
            tag_object(
                lobe,
                component="drought_tolerant_prairie_shrub",
            )
        )


def hip_roof(
    name: str,
    bounds: tuple[float, float, float, float],
    eave_z: float,
    ridge_z: float,
    mat: bpy.types.Material,
    *,
    component: str,
) -> bpy.types.Object:
    x0, x1, y0, y1 = bounds
    width = x1 - x0
    depth = y1 - y0
    if width >= depth:
        inset = depth * 0.5
        verts = [
            (x0, y0, eave_z),
            (x1, y0, eave_z),
            (x1, y1, eave_z),
            (x0, y1, eave_z),
            (x0 + inset, (y0 + y1) * 0.5, ridge_z),
            (x1 - inset, (y0 + y1) * 0.5, ridge_z),
        ]
        faces = [
            (0, 1, 5, 4),
            (3, 4, 5, 2),
            (0, 4, 3),
            (1, 2, 5),
        ]
    else:
        inset = width * 0.5
        verts = [
            (x0, y0, eave_z),
            (x1, y0, eave_z),
            (x1, y1, eave_z),
            (x0, y1, eave_z),
            ((x0 + x1) * 0.5, y0 + inset, ridge_z),
            ((x0 + x1) * 0.5, y1 - inset, ridge_z),
        ]
        faces = [
            (0, 4, 5, 3),
            (1, 2, 5, 4),
            (0, 1, 4),
            (3, 5, 2),
        ]
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    solidify = obj.modifiers.new("RoofBuildUp", "SOLIDIFY")
    solidify.thickness = 0.14
    solidify.offset = -1.0
    bevel = obj.modifiers.new("RoofEdgeSoftening", "BEVEL")
    bevel.width = 0.035
    bevel.segments = 2
    return tag_object(obj, component=component)


def add_wall_light(
    objects: list[bpy.types.Object],
    mats: dict[str, bpy.types.Material],
    *,
    orientation: str,
    along: float,
    wall: float,
    z: float,
    level: int,
    name: str,
) -> None:
    objects.append(
        oriented_box(
            f"{name}_Housing",
            orientation=orientation,
            along_size=0.18,
            depth_size=0.11,
            height=0.38,
            along=along,
            wall=wall,
            z=z,
            recess=-0.055,
            mat=mats["steel"],
            component="guest_room_wall_light_housing",
            level=level,
            bevel=0.025,
        )
    )
    objects.append(
        oriented_box(
            f"{name}_Glow",
            orientation=orientation,
            along_size=0.10,
            depth_size=0.04,
            height=0.24,
            along=along,
            wall=wall,
            z=z,
            recess=-0.12,
            mat=mats["light"],
            component="guest_room_wall_light",
            level=level,
            bevel=0.02,
        )
    )


def add_guest_room_depth(
    objects: list[bpy.types.Object],
    mats: dict[str, bpy.types.Material],
    *,
    orientation: str,
    window_center: float,
    wall: float,
    base: float,
    level: int,
    bay_index: int,
) -> None:
    # A registered depth card establishes colour/light while real furniture
    # supplies parallax and silhouette behind the separate pane and curtains.
    objects.append(
        oriented_box(
            f"ROOM_{orientation}_{level}_{bay_index:02d}_DepthCard",
            orientation=orientation,
            along_size=1.34,
            depth_size=0.045,
            height=1.42,
            along=window_center,
            wall=wall,
            z=base + 1.51,
            recess=0.92,
            mat=mats["interior"],
            component="registered_occupied_guest_room_depth",
            level=level,
        )
    )
    bed_along = window_center - 0.13
    objects.extend(
        [
            oriented_box(
                f"ROOM_{orientation}_{level}_{bay_index:02d}_Bed",
                orientation=orientation,
                along_size=1.18,
                depth_size=0.82,
                height=0.28,
                along=bed_along,
                wall=wall,
                z=base + 0.61,
                recess=1.18,
                mat=mats["bedding"],
                component="modeled_guest_room_bed",
                level=level,
                bevel=0.06,
            ),
            oriented_box(
                f"ROOM_{orientation}_{level}_{bay_index:02d}_Headboard",
                orientation=orientation,
                along_size=1.22,
                depth_size=0.10,
                height=0.68,
                along=bed_along,
                wall=wall,
                z=base + 1.02,
                recess=1.52,
                mat=mats["wood"],
                component="modeled_guest_room_headboard",
                level=level,
                bevel=0.025,
            ),
            oriented_box(
                f"ROOM_{orientation}_{level}_{bay_index:02d}_Nightstand",
                orientation=orientation,
                along_size=0.32,
                depth_size=0.30,
                height=0.42,
                along=window_center + 0.57,
                wall=wall,
                z=base + 0.50,
                recess=1.16,
                mat=mats["wood"],
                component="modeled_guest_room_nightstand",
                level=level,
                bevel=0.025,
            ),
            oriented_box(
                f"ROOM_{orientation}_{level}_{bay_index:02d}_Lamp",
                orientation=orientation,
                along_size=0.14,
                depth_size=0.12,
                height=0.24,
                along=window_center + 0.57,
                wall=wall,
                z=base + 0.83,
                recess=1.12,
                mat=mats["light"],
                component="modeled_guest_room_lamp",
                level=level,
                bevel=0.035,
            ),
        ]
    )


def add_room_bay(
    objects: list[bpy.types.Object],
    mats: dict[str, bpy.types.Material],
    *,
    orientation: str,
    centre: float,
    wall: float,
    base: float,
    level: int,
    bay_index: int,
    variant: str = "reference_locked",
) -> None:
    half = ROOM_BAY_WIDTH * 0.5
    u0 = centre - half
    u1 = centre + half
    window_center = centre - 0.63
    window_width = 1.48
    window_left = window_center - window_width * 0.5
    window_right = window_center + window_width * 0.5
    door_center = centre + 1.15
    door_width = 0.98
    door_left = door_center - door_width * 0.5
    door_right = door_center + door_width * 0.5
    top = base + 3.08
    window_bottom = base + 0.76
    window_top = base + 2.31
    door_bottom = base + 0.10
    door_top = base + 2.48

    def panel(
        suffix: str,
        left: float,
        right: float,
        bottom: float,
        upper: float,
    ) -> None:
        if right <= left or upper <= bottom:
            return
        objects.append(
            oriented_box(
                f"ROOM_{orientation}_{level}_{bay_index:02d}_{suffix}",
                orientation=orientation,
                along_size=right - left,
                depth_size=0.30,
                height=upper - bottom,
                along=(left + right) * 0.5,
                wall=wall,
                z=(bottom + upper) * 0.5,
                recess=0.15,
                mat=mats["stucco"],
                component="physical_guest_room_wall_panel",
                level=level,
                variant=variant,
            )
        )

    panel("LeftPier", u0, window_left, base, top)
    panel("MiddlePier", window_right, door_left, base, top)
    panel("RightPier", door_right, u1, base, top)
    panel("WindowApron", window_left, window_right, base, window_bottom)
    panel("WindowHead", window_left, window_right, window_top, top)
    panel("DoorHead", door_left, door_right, door_top, top)

    if level == 0:
        brick_ranges = (
            (u0, window_left),
            (window_left, window_right),
            (window_right, door_left),
            (door_right, u1),
        )
        for brick_index, (left, right) in enumerate(brick_ranges):
            if right <= left:
                continue
            objects.append(
                oriented_box(
                    f"ROOM_{orientation}_{bay_index:02d}_Brick_{brick_index}",
                    orientation=orientation,
                    along_size=right - left,
                    depth_size=0.055,
                    height=0.62,
                    along=(left + right) * 0.5,
                    wall=wall,
                    z=base + 0.36,
                    recess=-0.028,
                    mat=mats["brick"],
                    component="russet_brick_guest_room_base",
                    level=level,
                    variant=variant,
                )
            )

    # Recessed door, continuous jamb/head, threshold, closer and lever.
    objects.append(
        oriented_box(
            f"ROOM_{orientation}_{level}_{bay_index:02d}_Door",
            orientation=orientation,
            along_size=door_width - 0.10,
            depth_size=0.075,
            height=door_top - door_bottom - 0.09,
            along=door_center,
            wall=wall,
            z=(door_bottom + door_top) * 0.5,
            recess=0.235,
            mat=mats["door"],
            component="recessed_guest_room_door",
            level=level,
            bevel=0.018,
            variant=variant,
        )
    )
    for jamb_along in (door_left, door_right):
        objects.append(
            oriented_box(
                f"ROOM_{orientation}_{level}_{bay_index:02d}_DoorJamb",
                orientation=orientation,
                along_size=0.075,
                depth_size=0.12,
                height=door_top - door_bottom + 0.10,
                along=jamb_along,
                wall=wall,
                z=(door_bottom + door_top) * 0.5,
                recess=0.115,
                mat=mats["steel"],
                component="guest_room_door_frame",
                level=level,
                variant=variant,
            )
        )
    objects.extend(
        [
            oriented_box(
                f"ROOM_{orientation}_{level}_{bay_index:02d}_DoorHeadFrame",
                orientation=orientation,
                along_size=door_width + 0.08,
                depth_size=0.12,
                height=0.075,
                along=door_center,
                wall=wall,
                z=door_top + 0.03,
                recess=0.115,
                mat=mats["steel"],
                component="guest_room_door_frame",
                level=level,
                variant=variant,
            ),
            oriented_box(
                f"ROOM_{orientation}_{level}_{bay_index:02d}_Threshold",
                orientation=orientation,
                along_size=door_width + 0.12,
                depth_size=0.34,
                height=0.055,
                along=door_center,
                wall=wall,
                z=door_bottom,
                recess=-0.015,
                mat=mats["galvanized"],
                component="guest_room_door_threshold",
                level=level,
                variant=variant,
            ),
            oriented_box(
                f"ROOM_{orientation}_{level}_{bay_index:02d}_DoorCloser",
                orientation=orientation,
                along_size=0.42,
                depth_size=0.07,
                height=0.07,
                along=door_center,
                wall=wall,
                z=door_top - 0.15,
                recess=0.185,
                mat=mats["galvanized"],
                component="guest_room_door_hardware",
                level=level,
                bevel=0.012,
                variant=variant,
            ),
            oriented_box(
                f"ROOM_{orientation}_{level}_{bay_index:02d}_DoorLever",
                orientation=orientation,
                along_size=0.16,
                depth_size=0.10,
                height=0.045,
                along=door_center - 0.27,
                wall=wall,
                z=base + 1.18,
                recess=0.155,
                mat=mats["galvanized"],
                component="guest_room_door_hardware",
                level=level,
                bevel=0.012,
                variant=variant,
            ),
        ]
    )

    # Window: true frame and two separate panes with mullion, sill and flashing.
    frame_z = (window_bottom + window_top) * 0.5
    for frame_along in (window_left, window_right):
        objects.append(
            oriented_box(
                f"ROOM_{orientation}_{level}_{bay_index:02d}_WindowJamb",
                orientation=orientation,
                along_size=0.075,
                depth_size=0.14,
                height=window_top - window_bottom + 0.10,
                along=frame_along,
                wall=wall,
                z=frame_z,
                recess=0.11,
                mat=mats["steel"],
                component="thermally_broken_window_frame",
                level=level,
                variant=variant,
            )
        )
    for frame_height, suffix in (
        (window_bottom, "SillFrame"),
        (window_top, "HeadFrame"),
    ):
        objects.append(
            oriented_box(
                f"ROOM_{orientation}_{level}_{bay_index:02d}_{suffix}",
                orientation=orientation,
                along_size=window_width + 0.12,
                depth_size=0.14,
                height=0.075,
                along=window_center,
                wall=wall,
                z=frame_height,
                recess=0.11,
                mat=mats["steel"],
                component="thermally_broken_window_frame",
                level=level,
                variant=variant,
            )
        )
    objects.append(
        oriented_box(
            f"ROOM_{orientation}_{level}_{bay_index:02d}_Mullion",
            orientation=orientation,
            along_size=0.065,
            depth_size=0.12,
            height=window_top - window_bottom,
            along=window_center,
            wall=wall,
            z=frame_z,
            recess=0.10,
            mat=mats["steel"],
            component="window_operable_sash_mullion",
            level=level,
            variant=variant,
        )
    )
    pane_width = (window_width - 0.12) * 0.5
    for pane_index, offset in enumerate((-pane_width * 0.5, pane_width * 0.5)):
        objects.append(
            oriented_box(
                f"ROOM_{orientation}_{level}_{bay_index:02d}_Pane_{pane_index}",
                orientation=orientation,
                along_size=pane_width - 0.025,
                depth_size=0.032,
                height=window_top - window_bottom - 0.10,
                along=window_center + offset,
                wall=wall,
                z=frame_z,
                recess=0.19,
                mat=mats["glass"],
                component="physical_low_e_guest_room_pane",
                level=level,
                variant=variant,
            )
        )
    objects.extend(
        [
            oriented_box(
                f"ROOM_{orientation}_{level}_{bay_index:02d}_Sill",
                orientation=orientation,
                along_size=window_width + 0.22,
                depth_size=0.26,
                height=0.055,
                along=window_center,
                wall=wall,
                z=window_bottom - 0.055,
                recess=0.01,
                mat=mats["concrete"],
                component="sloped_guest_room_window_sill",
                level=level,
                variant=variant,
            ),
            oriented_box(
                f"ROOM_{orientation}_{level}_{bay_index:02d}_HeadFlashing",
                orientation=orientation,
                along_size=window_width + 0.19,
                depth_size=0.18,
                height=0.035,
                along=window_center,
                wall=wall,
                z=window_top + 0.075,
                recess=0.01,
                mat=mats["galvanized"],
                component="guest_room_window_head_flashing",
                level=level,
                variant=variant,
            ),
        ]
    )
    for curtain_index, offset in enumerate((-0.38, 0.38)):
        width = 0.42 if (bay_index + level + curtain_index) % 3 else 0.29
        objects.append(
            oriented_box(
                f"ROOM_{orientation}_{level}_{bay_index:02d}_Sheer_{curtain_index}",
                orientation=orientation,
                along_size=width,
                depth_size=0.025,
                height=window_top - window_bottom - 0.16,
                along=window_center + offset,
                wall=wall,
                z=frame_z,
                recess=0.35,
                mat=mats["curtain"],
                component="guest_room_sheer_curtain",
                level=level,
                variant=variant,
            )
        )
    blackout_offset = -0.52 if (bay_index + level) % 2 else 0.52
    objects.append(
        oriented_box(
            f"ROOM_{orientation}_{level}_{bay_index:02d}_Blackout",
            orientation=orientation,
            along_size=0.28,
            depth_size=0.030,
            height=window_top - window_bottom - 0.12,
            along=window_center + blackout_offset,
            wall=wall,
            z=frame_z,
            recess=0.42,
            mat=mats["blackout"],
            component="guest_room_blackout_curtain",
            level=level,
            variant=variant,
        )
    )
    add_guest_room_depth(
        objects,
        mats,
        orientation=orientation,
        window_center=window_center,
        wall=wall,
        base=base,
        level=level,
        bay_index=bay_index,
    )
    add_wall_light(
        objects,
        mats,
        orientation=orientation,
        along=door_left - 0.20,
        wall=wall,
        z=base + 2.28,
        level=level,
        name=f"ROOM_{orientation}_{level}_{bay_index:02d}_WallLight",
    )


def add_rear_window_bay(
    objects: list[bpy.types.Object],
    mats: dict[str, bpy.types.Material],
    *,
    orientation: str,
    centre: float,
    wall: float,
    base: float,
    level: int,
    bay_index: int,
) -> None:
    half = ROOM_BAY_WIDTH * 0.5
    left = centre - half
    right = centre + half
    width = 1.52
    window_left = centre - width * 0.5
    window_right = centre + width * 0.5
    bottom = base + 0.78
    top = base + 2.30
    wall_top = base + 3.08

    def panel(
        suffix: str,
        u0: float,
        u1: float,
        z0: float,
        z1: float,
    ) -> None:
        objects.append(
            outward_box(
                f"REAR_{orientation}_{level}_{bay_index:02d}_{suffix}",
                orientation=orientation,
                along_size=u1 - u0,
                depth_size=0.30,
                height=z1 - z0,
                along=(u0 + u1) * 0.5,
                wall=wall,
                z=(z0 + z1) * 0.5,
                recess=0.15,
                mat=mats["stucco"],
                component="rear_guest_room_wall_panel",
                level=level,
            )
        )

    panel("Left", left, window_left, base, wall_top)
    panel("Right", window_right, right, base, wall_top)
    panel("Apron", window_left, window_right, base, bottom)
    panel("Head", window_left, window_right, top, wall_top)
    if level == 0:
        for index, (u0, u1) in enumerate(
            ((left, window_left), (window_left, window_right), (window_right, right))
        ):
            objects.append(
                outward_box(
                    f"REAR_{orientation}_{bay_index:02d}_Brick_{index}",
                    orientation=orientation,
                    along_size=u1 - u0,
                    depth_size=0.055,
                    height=0.62,
                    along=(u0 + u1) * 0.5,
                    wall=wall,
                    z=base + 0.36,
                    recess=-0.028,
                    mat=mats["brick"],
                    component="rear_russet_brick_base",
                    level=level,
                )
            )
    for frame_along in (window_left, centre, window_right):
        objects.append(
            outward_box(
                f"REAR_{orientation}_{level}_{bay_index:02d}_Frame",
                orientation=orientation,
                along_size=0.075,
                depth_size=0.13,
                height=top - bottom + 0.08,
                along=frame_along,
                wall=wall,
                z=(bottom + top) * 0.5,
                recess=0.11,
                mat=mats["steel"],
                component="rear_thermally_broken_window_frame",
                level=level,
            )
        )
    for z, suffix in ((bottom, "SillFrame"), (top, "HeadFrame")):
        objects.append(
            outward_box(
                f"REAR_{orientation}_{level}_{bay_index:02d}_{suffix}",
                orientation=orientation,
                along_size=width + 0.10,
                depth_size=0.13,
                height=0.075,
                along=centre,
                wall=wall,
                z=z,
                recess=0.11,
                mat=mats["steel"],
                component="rear_thermally_broken_window_frame",
                level=level,
            )
        )
    for pane_index, offset in enumerate((-0.37, 0.37)):
        objects.append(
            outward_box(
                f"REAR_{orientation}_{level}_{bay_index:02d}_Pane_{pane_index}",
                orientation=orientation,
                along_size=0.69,
                depth_size=0.03,
                height=top - bottom - 0.10,
                along=centre + offset,
                wall=wall,
                z=(bottom + top) * 0.5,
                recess=0.19,
                mat=mats["glass"],
                component="physical_low_e_rear_guest_room_pane",
                level=level,
            )
        )
    objects.append(
        outward_box(
            f"REAR_{orientation}_{level}_{bay_index:02d}_Curtain",
            orientation=orientation,
            along_size=1.28,
            depth_size=0.025,
            height=top - bottom - 0.13,
            along=centre,
            wall=wall,
            z=(bottom + top) * 0.5,
            recess=0.34,
            mat=mats["curtain"],
            component="rear_guest_room_curtain",
            level=level,
        )
    )
    if level == 0 or bay_index % 2 == 0:
        objects.append(
            outward_box(
                f"REAR_{orientation}_{level}_{bay_index:02d}_Vent",
                orientation=orientation,
                along_size=0.72,
                depth_size=0.095,
                height=0.28,
                along=centre + 0.92,
                wall=wall,
                z=base + 0.52,
                recess=-0.05,
                mat=mats["service"],
                component="aligned_guest_room_ventilation_grille",
                level=level,
                bevel=0.018,
            )
        )


def add_gallery(
    objects: list[bpy.types.Object],
    mats: dict[str, bpy.types.Material],
) -> None:
    # Main and return slabs join the lobby bridge at matching datums.
    objects.extend(
        [
            b(
                "GALLERY_MainWalkwaySlab",
                (43.0, 1.82, 0.22),
                (-6.5, 6.09, 3.49),
                mats["concrete"],
                bevel=0.025,
                component="continuous_upper_gallery_slab",
                level=1,
            ),
            b(
                "GALLERY_ReturnWalkwaySlab",
                (1.82, 18.5, 0.22),
                (16.09, -3.0, 3.49),
                mats["concrete"],
                bevel=0.025,
                component="continuous_upper_gallery_slab",
                level=1,
            ),
            b(
                "GALLERY_MainCedarCeiling",
                (43.0, 1.92, 0.12),
                (-6.5, 6.03, 6.57),
                mats["cedar"],
                component="deep_cedar_gallery_soffit",
                level=1,
            ),
            b(
                "GALLERY_ReturnCedarCeiling",
                (1.92, 18.5, 0.12),
                (16.03, -3.0, 6.57),
                mats["cedar"],
                component="deep_cedar_gallery_soffit",
                level=1,
            ),
        ]
    )
    main_boundaries = tuple(-27.5 + index * ROOM_BAY_WIDTH for index in range(11))
    for index, x in enumerate(main_boundaries):
        objects.append(
            b(
                f"GALLERY_MainColumn_{index:02d}",
                (0.11, 0.11, 6.28),
                (x, 5.20, 3.43),
                mats["steel"],
                bevel=0.018,
                component="gallery_structural_column",
            )
        )
    return_boundaries = (-11.4, -7.2, -3.0, 1.2, 5.4)
    for index, y in enumerate(return_boundaries):
        objects.append(
            b(
                f"GALLERY_ReturnColumn_{index:02d}",
                (0.11, 0.11, 6.28),
                (15.20, y, 3.43),
                mats["steel"],
                bevel=0.018,
                component="gallery_structural_column",
            )
        )
    for index, x in enumerate(
        -27.5 + index * 1.42 for index in range(31)
    ):
        objects.append(
            b(
                f"GALLERY_MainRailPost_{index:02d}",
                (0.055, 0.065, 1.12),
                (x, 5.17, 4.13),
                mats["steel"],
                component="gallery_guardrail_post",
                level=1,
            )
        )
    for rail_index, z in enumerate((3.74, 3.95, 4.16, 4.37, 4.58)):
        objects.append(
            b(
                f"GALLERY_MainHorizontalRail_{rail_index}",
                (43.0, 0.045, 0.045),
                (-6.5, 5.14, z),
                mats["steel"],
                component="gallery_horizontal_guardrail",
                level=1,
            )
        )
    for index, y in enumerate(-11.3 + index * 1.40 for index in range(13)):
        objects.append(
            b(
                f"GALLERY_ReturnRailPost_{index:02d}",
                (0.065, 0.055, 1.12),
                (15.17, y, 4.13),
                mats["steel"],
                component="gallery_guardrail_post",
                level=1,
            )
        )
    for rail_index, z in enumerate((3.74, 3.95, 4.16, 4.37, 4.58)):
        objects.append(
            b(
                f"GALLERY_ReturnHorizontalRail_{rail_index}",
                (0.045, 18.5, 0.045),
                (15.14, -3.0, z),
                mats["steel"],
                component="gallery_horizontal_guardrail",
                level=1,
            )
        )
    for index, x in enumerate(MAIN_ROOM_CENTRES):
        objects.append(
            c(
                f"GALLERY_MainSoffitLight_{index:02d}",
                0.075,
                0.035,
                (x, 6.02, 6.49),
                mats["light"],
                vertices=18,
                component="gallery_recessed_soffit_light",
                level=1,
            )
        )
    for index, y in enumerate(RETURN_ROOM_CENTRES):
        objects.append(
            c(
                f"GALLERY_ReturnSoffitLight_{index:02d}",
                0.075,
                0.035,
                (16.02, y, 6.49),
                mats["light"],
                vertices=18,
                component="gallery_recessed_soffit_light",
                level=1,
            )
        )


def add_stair(
    objects: list[bpy.types.Object],
    mats: dict[str, bpy.types.Material],
    *,
    name: str,
    orientation: str,
    centre: float,
) -> None:
    count = 18
    rise = 3.18 / count
    run = 5.04 / count
    if orientation == "main":
        start = 0.10
        for index in range(count):
            y = start + (index + 0.5) * run
            z = 0.34 + (index + 1) * rise
            objects.append(
                b(
                    f"{name}_Tread_{index:02d}",
                    (1.52, run + 0.025, 0.065),
                    (centre, y, z),
                    mats["galvanized"],
                    bevel=0.018,
                    component="open_galvanized_stair_tread",
                )
            )
        for side in (-0.69, 0.69):
            x = centre + side
            objects.append(
                rectangular_beam(
                    f"{name}_PlateStringer_{side:+.2f}",
                    (x, start, 0.40),
                    (x, start + count * run, 3.60),
                    0.10,
                    0.30,
                    mats["steel"],
                    component="continuous_plate_stair_stringer",
                )
            )
            objects.append(
                rectangular_beam(
                    f"{name}_SlopedHandrail_{side:+.2f}",
                    (x, start, 1.28),
                    (x, start + count * run, 4.48),
                    0.055,
                    0.055,
                    mats["steel"],
                    component="continuous_stair_handrail",
                )
            )
            for post_index in range(7):
                fraction = post_index / 6
                y = start + fraction * count * run
                stair_z = 0.40 + fraction * 3.20
                objects.append(
                    b(
                        f"{name}_RailPost_{side:+.2f}_{post_index}",
                        (0.052, 0.052, 0.88),
                        (x, y, stair_z + 0.44),
                        mats["steel"],
                        component="stair_guardrail_post",
                    )
                )
        objects.extend(
            [
                b(
                    f"{name}_Footing",
                    (2.10, 1.05, 0.20),
                    (centre, start + 0.35, 0.30),
                    mats["concrete"],
                    bevel=0.055,
                    component="stair_concrete_footing",
                ),
                b(
                    f"{name}_UpperLanding",
                    (1.86, 1.18, 0.20),
                    (centre, 5.48, 3.49),
                    mats["concrete"],
                    bevel=0.025,
                    component="gallery_integrated_stair_landing",
                    level=1,
                ),
            ]
        )
        for side in (-0.69, 0.69):
            objects.append(
                b(
                    f"{name}_BasePlate_{side:+.2f}",
                    (0.30, 0.32, 0.035),
                    (centre + side, start + 0.05, 0.42),
                    mats["galvanized"],
                    bevel=0.015,
                    component="stair_stringer_base_plate",
                )
            )
    elif orientation == "return":
        start = 10.05
        for index in range(count):
            x = start + (index + 0.5) * run
            z = 0.34 + (index + 1) * rise
            objects.append(
                b(
                    f"{name}_Tread_{index:02d}",
                    (run + 0.025, 1.52, 0.065),
                    (x, centre, z),
                    mats["galvanized"],
                    bevel=0.018,
                    component="open_galvanized_stair_tread",
                )
            )
        for side in (-0.69, 0.69):
            y = centre + side
            objects.append(
                rectangular_beam(
                    f"{name}_PlateStringer_{side:+.2f}",
                    (start, y, 0.40),
                    (start + count * run, y, 3.60),
                    0.30,
                    0.10,
                    mats["steel"],
                    component="continuous_plate_stair_stringer",
                )
            )
            objects.append(
                rectangular_beam(
                    f"{name}_SlopedHandrail_{side:+.2f}",
                    (start, y, 1.28),
                    (start + count * run, y, 4.48),
                    0.055,
                    0.055,
                    mats["steel"],
                    component="continuous_stair_handrail",
                )
            )
            for post_index in range(7):
                fraction = post_index / 6
                x = start + fraction * count * run
                stair_z = 0.40 + fraction * 3.20
                objects.append(
                    b(
                        f"{name}_RailPost_{side:+.2f}_{post_index}",
                        (0.052, 0.052, 0.88),
                        (x, y, stair_z + 0.44),
                        mats["steel"],
                        component="stair_guardrail_post",
                    )
                )
        objects.extend(
            [
                b(
                    f"{name}_Footing",
                    (1.05, 2.10, 0.20),
                    (start + 0.35, centre, 0.30),
                    mats["concrete"],
                    bevel=0.055,
                    component="stair_concrete_footing",
                ),
                b(
                    f"{name}_UpperLanding",
                    (1.18, 1.86, 0.20),
                    (15.43, centre, 3.49),
                    mats["concrete"],
                    bevel=0.025,
                    component="gallery_integrated_stair_landing",
                    level=1,
                ),
            ]
        )
        for side in (-0.69, 0.69):
            objects.append(
                b(
                    f"{name}_BasePlate_{side:+.2f}",
                    (0.32, 0.30, 0.035),
                    (start + 0.05, centre + side, 0.42),
                    mats["galvanized"],
                    bevel=0.015,
                    component="stair_stringer_base_plate",
                )
            )
    else:
        raise ValueError(orientation)


def add_lobby(
    objects: list[bpy.types.Object],
    mats: dict[str, bpy.types.Material],
) -> None:
    # Inside-corner pavilion physically bridges both wings.
    objects.extend(
        [
            b(
                "LOBBY_GroundFloor",
                (13.0, 11.2, 0.24),
                (21.5, 10.6, 0.33),
                mats["concrete"],
                component="lobby_floor_slab",
            ),
            b(
                "LOBBY_UpperBridgeSlab",
                (8.8, 5.6, 0.22),
                (21.5, 12.4, 3.50),
                mats["concrete"],
                component="lobby_upper_bridge",
                level=1,
            ),
            b(
                "LOBBY_EastWall",
                (0.34, 11.2, 6.82),
                (27.83, 10.6, 3.70),
                mats["stucco"],
                component="lobby_side_wall",
            ),
            b(
                "LOBBY_NorthWall",
                (13.0, 0.34, 6.82),
                (21.5, 16.03, 3.70),
                mats["stucco"],
                component="lobby_rear_wall",
            ),
        ]
    )
    # Project the glazed arrival pavilion into the open court. The original
    # lobby volume remains behind it, but this occupied two-storey bay clears
    # both guest-wing sightlines and becomes the legible entrance goalpost.
    objects.extend(
        [
            b(
                "LOBBY_ProjectingGroundSlab",
                (6.6, 5.3, 0.24),
                (15.1, 5.0, 0.34),
                mats["concrete"],
                bevel=0.05,
                component="projecting_glazed_lobby_floor_slab",
            ),
            b(
                "LOBBY_ProjectingUpperSlab",
                (6.6, 5.3, 0.20),
                (15.1, 5.0, 3.50),
                mats["concrete"],
                bevel=0.035,
                component="projecting_glazed_lobby_upper_slab",
                level=1,
            ),
            b(
                "LOBBY_ProjectingInteriorFeatureWall",
                (4.2, 0.16, 5.65),
                (15.2, 7.35, 3.55),
                mats["interior"],
                bevel=0.035,
                component="modeled_lobby_interior_depth",
            ),
        ]
    )
    for pier_index, (x, y) in enumerate(
        ((11.72, 2.30), (18.48, 2.30), (11.72, 7.62))
    ):
        objects.append(
            b(
                f"LOBBY_ProjectingBrickPier_{pier_index}",
                (0.52, 0.52, 6.92),
                (x, y, 3.72),
                mats["brick"],
                bevel=0.025,
                component="projecting_lobby_structural_brick_pier",
            )
        )
    for level, (z, height) in enumerate(((1.92, 2.72), (5.18, 2.58))):
        for panel_index, x in enumerate((12.75, 14.32, 15.88, 17.45)):
            objects.append(
                b(
                    f"LOBBY_ProjectingSouthGlass_{level}_{panel_index}",
                    (1.38, 0.040, height),
                    (x, 2.36, z),
                    mats["lobby_glass"],
                    component="physical_projecting_lobby_curtain_wall_pane",
                    level=level,
                )
            )
            objects.append(
                b(
                    f"LOBBY_ProjectingSouthMullion_{level}_{panel_index}",
                    (0.075, 0.12, height + 0.10),
                    (x - 0.73, 2.35, z),
                    mats["steel"],
                    component="projecting_lobby_curtain_wall_mullion",
                    level=level,
                )
            )
        for panel_index, y in enumerate((3.25, 4.82, 6.39)):
            objects.append(
                b(
                    f"LOBBY_ProjectingWestGlass_{level}_{panel_index}",
                    (0.040, 1.38, height),
                    (11.78, y, z),
                    mats["lobby_glass"],
                    component="physical_projecting_lobby_curtain_wall_pane",
                    level=level,
                )
            )
            objects.append(
                b(
                    f"LOBBY_ProjectingWestMullion_{level}_{panel_index}",
                    (0.12, 0.075, height + 0.10),
                    (11.77, y - 0.73, z),
                    mats["steel"],
                    component="projecting_lobby_curtain_wall_mullion",
                    level=level,
                )
            )
    for door_index, x in enumerate((14.47, 15.73)):
        objects.extend(
            [
                b(
                    f"LOBBY_ProjectingVestibuleDoor_{door_index}",
                    (1.12, 0.050, 2.52),
                    (x, 2.30, 1.65),
                    mats["lobby_glass"],
                    component="physical_projecting_lobby_vestibule_door",
                ),
                b(
                    f"LOBBY_ProjectingVestibuleHandle_{door_index}",
                    (0.045, 0.12, 0.78),
                    (x + (-0.18 if door_index else 0.18), 2.23, 1.48),
                    mats["galvanized"],
                    bevel=0.015,
                    component="projecting_lobby_vestibule_door_handle",
                ),
            ]
        )
    for light_index, (x, y) in enumerate(
        ((13.1, 4.1), (15.1, 4.1), (17.1, 4.1), (13.1, 6.2), (17.1, 6.2))
    ):
        objects.append(
            c(
                f"LOBBY_ProjectingWarmLight_{light_index}",
                0.11,
                0.08,
                (x, y, 6.82),
                mats["light"],
                vertices=18,
                component="projecting_lobby_recessed_light",
            )
        )
    for x in (24.70, 27.75):
        objects.append(
            b(
                f"LOBBY_SouthBrickPier_{x:.2f}",
                (0.50, 0.55, 6.88),
                (x, 5.22, 3.72),
                mats["brick"],
                bevel=0.025,
                component="inside_corner_lobby_brick_pier",
            )
        )
    for y in (12.20, 15.65):
        objects.append(
            b(
                f"LOBBY_WestBrickPier_{y:.2f}",
                (0.55, 0.50, 6.88),
                (15.22, y, 3.72),
                mats["brick"],
                bevel=0.025,
                component="inside_corner_lobby_brick_pier",
            )
        )
    # South curtain wall, split at slab line and around vestibule doors.
    south_panel_centres = (16.78, 19.78, 23.22, 26.22)
    for level, (z, height) in enumerate(((1.92, 2.76), (5.18, 2.62))):
        for index, x in enumerate(south_panel_centres):
            width = 2.22 if index in (0, 3) else 2.44
            objects.append(
                b(
                    f"LOBBY_SouthGlass_{level}_{index}",
                    (width, 0.035, height),
                    (x, 5.05, z),
                    mats["lobby_glass"],
                    component="physical_lobby_curtain_wall_pane",
                    level=level,
                )
            )
            for edge_index, edge in enumerate((-width * 0.5, width * 0.5)):
                objects.append(
                    b(
                        f"LOBBY_SouthMullion_{level}_{index}_{edge_index}",
                        (0.075, 0.12, height + 0.10),
                        (x + edge, 5.04, z),
                        mats["steel"],
                        component="lobby_curtain_wall_mullion",
                        level=level,
                    )
                )
    for level, (z, height) in enumerate(((1.92, 2.76), (5.18, 2.62))):
        for index, y in enumerate((7.0, 10.0, 13.0, 15.0)):
            objects.append(
                b(
                    f"LOBBY_WestGlass_{level}_{index}",
                    (0.035, 2.15 if index < 3 else 1.25, height),
                    (15.05, y, z),
                    mats["lobby_glass"],
                    component="physical_lobby_curtain_wall_pane",
                    level=level,
                )
            )
            objects.append(
                b(
                    f"LOBBY_WestMullion_{level}_{index}",
                    (0.12, 0.075, height + 0.10),
                    (15.04, y - 1.08, z),
                    mats["steel"],
                    component="lobby_curtain_wall_mullion",
                    level=level,
                )
            )
    for door_index, x in enumerate((20.88, 22.12)):
        objects.extend(
            [
                b(
                    f"LOBBY_VestibuleDoor_{door_index}",
                    (1.08, 0.045, 2.50),
                    (x, 4.97, 1.65),
                    mats["lobby_glass"],
                    component="physical_lobby_vestibule_door",
                ),
                b(
                    f"LOBBY_VestibuleDoorFrame_{door_index}",
                    (0.075, 0.13, 2.60),
                    (x - 0.54, 4.96, 1.65),
                    mats["steel"],
                    component="lobby_vestibule_door_frame",
                ),
                b(
                    f"LOBBY_VestibuleDoorHandle_{door_index}",
                    (0.045, 0.12, 0.78),
                    (x + (-0.18 if door_index else 0.18), 4.91, 1.48),
                    mats["galvanized"],
                    bevel=0.015,
                    component="lobby_vestibule_door_handle",
                ),
            ]
        )
    # Reception, breakfast tables, lounge and upper bridge provide true depth.
    objects.extend(
        [
            b(
                "LOBBY_ReceptionDesk",
                (4.5, 0.75, 1.05),
                (22.0, 8.4, 0.86),
                mats["wood"],
                bevel=0.08,
                component="modeled_lobby_reception_desk",
            ),
            b(
                "LOBBY_ReceptionBackwall",
                (5.2, 0.18, 2.25),
                (22.0, 9.95, 1.50),
                mats["wood"],
                bevel=0.04,
                component="modeled_lobby_reception_backwall",
            ),
        ]
    )
    for table_index, (x, y) in enumerate(
        ((18.0, 12.6), (21.3, 12.8), (24.6, 12.5), (18.5, 15.0), (24.2, 14.9))
    ):
        objects.extend(
            [
                c(
                    f"LOBBY_BreakfastTableTop_{table_index}",
                    0.62,
                    0.08,
                    (x, y, 0.92),
                    mats["wood"],
                    vertices=32,
                    component="modeled_breakfast_table",
                ),
                c(
                    f"LOBBY_BreakfastTablePost_{table_index}",
                    0.055,
                    0.72,
                    (x, y, 0.54),
                    mats["steel"],
                    vertices=12,
                    component="modeled_breakfast_table",
                ),
            ]
        )
        for chair_index, angle in enumerate((0.0, math.pi)):
            objects.append(
                b(
                    f"LOBBY_BreakfastChair_{table_index}_{chair_index}",
                    (0.46, 0.46, 0.46),
                    (
                        x + math.cos(angle) * 0.92,
                        y + math.sin(angle) * 0.92,
                        0.55,
                    ),
                    mats["bedding"],
                    bevel=0.08,
                    component="modeled_breakfast_chair",
                )
            )
    for light_index, (x, y) in enumerate(
        ((18.0, 12.6), (21.3, 12.8), (24.6, 12.5), (21.4, 8.1))
    ):
        objects.extend(
            [
                c(
                    f"LOBBY_PendantCord_{light_index}",
                    0.025,
                    1.1,
                    (x, y, 6.0),
                    mats["steel"],
                    vertices=10,
                    component="lobby_pendant_light",
                ),
                c(
                    f"LOBBY_PendantGlow_{light_index}",
                    0.16,
                    0.24,
                    (x, y, 5.42),
                    mats["light"],
                    vertices=20,
                    component="lobby_pendant_light",
                ),
            ]
        )
    # Thin arrival canopy, cedar underside, drainage and plausible supports.
    objects.extend(
        [
            b(
                "LOBBY_PorteCochereRoof",
                (11.8, 5.6, 0.22),
                (15.1, -0.20, 3.24),
                mats["steel"],
                bevel=0.055,
                component="integrated_lobby_porte_cochere",
            ),
            b(
                "LOBBY_PorteCochereCedarSoffit",
                (11.5, 5.35, 0.10),
                (15.1, -0.20, 3.10),
                mats["cedar"],
                component="porte_cochere_cedar_soffit",
            ),
            b(
                "LOBBY_ArrivalPad",
                (13.5, 8.0, 0.18),
                (15.1, -0.65, 0.31),
                mats["concrete"],
                bevel=0.12,
                component="accessible_lobby_arrival_pad",
            ),
        ]
    )
    for column_index, x in enumerate((9.9, 20.3)):
        objects.append(
            b(
                f"LOBBY_PorteCochereColumn_{column_index}",
                (0.16, 0.16, 2.90),
                (x, -2.73, 1.75),
                mats["steel"],
                bevel=0.025,
                component="porte_cochere_structural_column",
            )
        )
    for light_index, x in enumerate((11.1, 13.8, 16.4, 19.1)):
        objects.append(
            c(
                f"LOBBY_CanopyDownlight_{light_index}",
                0.085,
                0.035,
                (x, -0.20, 3.03),
                mats["light"],
                vertices=18,
                component="porte_cochere_recessed_downlight",
            )
        )
    objects.extend(
        [
            hip_roof(
                "LOBBY_RaisedHipRoof",
                (14.55, 28.45, 4.30, 18.70),
                7.30,
                9.20,
                mats["shingle"],
                component="raised_inside_corner_lobby_hip_roof",
            ),
            b(
                "LOBBY_SouthFascia",
                (13.9, 0.18, 0.28),
                (21.5, 4.30, 7.23),
                mats["steel"],
                component="lobby_roof_fascia",
            ),
            b(
                "LOBBY_WestFascia",
                (0.18, 12.6, 0.28),
                (14.55, 10.60, 7.23),
                mats["steel"],
                component="lobby_roof_fascia",
            ),
            b(
                "LOBBY_EastFascia",
                (0.18, 14.4, 0.28),
                (28.45, 11.50, 7.23),
                mats["steel"],
                component="lobby_roof_fascia",
            ),
            b(
                "LOBBY_NorthFascia",
                (13.9, 0.18, 0.28),
                (21.5, 18.70, 7.23),
                mats["steel"],
                component="lobby_roof_fascia",
            ),
        ]
    )


def add_pool_and_cabana(
    objects: list[bpy.types.Object],
    mats: dict[str, bpy.types.Material],
) -> None:
    pool_x = 4.2
    pool_y = -7.2
    deck_width = 14.6
    deck_depth = 9.4
    water_width = 9.4
    water_depth = 4.8
    objects.extend(
        [
            b(
                "POOL_ConcreteDeck",
                (deck_width, deck_depth, 0.20),
                (pool_x, pool_y, 0.31),
                mats["concrete"],
                bevel=0.10,
                component="pool_court_concrete_deck",
            ),
            b(
                "POOL_BasinShadow",
                (water_width + 0.40, water_depth + 0.40, 0.30),
                (pool_x, pool_y, 0.32),
                mats["dark"],
                bevel=0.18,
                component="physical_pool_basin",
            ),
            b(
                "POOL_Water",
                (water_width, water_depth, 0.055),
                (pool_x, pool_y, 0.51),
                mats["pool"],
                bevel=0.16,
                component="physical_pool_water_surface",
            ),
        ]
    )
    coping_specs = (
        ((water_width + 0.55, 0.28, 0.12), (pool_x, pool_y - water_depth / 2 - 0.12, 0.54)),
        ((water_width + 0.55, 0.28, 0.12), (pool_x, pool_y + water_depth / 2 + 0.12, 0.54)),
        ((0.28, water_depth, 0.12), (pool_x - water_width / 2 - 0.12, pool_y, 0.54)),
        ((0.28, water_depth, 0.12), (pool_x + water_width / 2 + 0.12, pool_y, 0.54)),
    )
    for index, (size, location) in enumerate(coping_specs):
        objects.append(
            b(
                f"POOL_Coping_{index}",
                size,
                location,
                mats["concrete"],
                bevel=0.045,
                component="pool_coping",
            )
        )
    fence_x0 = pool_x - deck_width / 2 + 0.25
    fence_x1 = pool_x + deck_width / 2 - 0.25
    fence_y0 = pool_y - deck_depth / 2 + 0.25
    fence_y1 = pool_y + deck_depth / 2 - 0.25
    for index, x in enumerate(
        fence_x0 + index * 1.35
        for index in range(round((fence_x1 - fence_x0) / 1.35) + 1)
    ):
        for y in (fence_y0, fence_y1):
            objects.append(
                b(
                    f"POOL_FencePost_X_{index}_{y:.1f}",
                    (0.055, 0.055, 1.28),
                    (x, y, 1.05),
                    mats["steel"],
                    component="pool_safety_fence",
                )
            )
    for index, y in enumerate(
        fence_y0 + index * 1.35
        for index in range(round((fence_y1 - fence_y0) / 1.35) + 1)
    ):
        for x in (fence_x0, fence_x1):
            objects.append(
                b(
                    f"POOL_FencePost_Y_{index}_{x:.1f}",
                    (0.055, 0.055, 1.28),
                    (x, y, 1.05),
                    mats["steel"],
                    component="pool_safety_fence",
                )
            )
    for z in (0.52, 1.68):
        objects.extend(
            [
                b(
                    f"POOL_FenceRail_S_{z}",
                    (fence_x1 - fence_x0, 0.042, 0.042),
                    ((fence_x0 + fence_x1) * 0.5, fence_y0, z),
                    mats["steel"],
                    component="pool_safety_fence",
                ),
                b(
                    f"POOL_FenceRail_N_{z}",
                    (fence_x1 - fence_x0, 0.042, 0.042),
                    ((fence_x0 + fence_x1) * 0.5, fence_y1, z),
                    mats["steel"],
                    component="pool_safety_fence",
                ),
                b(
                    f"POOL_FenceRail_W_{z}",
                    (0.042, fence_y1 - fence_y0, 0.042),
                    (fence_x0, (fence_y0 + fence_y1) * 0.5, z),
                    mats["steel"],
                    component="pool_safety_fence",
                ),
                b(
                    f"POOL_FenceRail_E_{z}",
                    (0.042, fence_y1 - fence_y0, 0.042),
                    (fence_x1, (fence_y0 + fence_y1) * 0.5, z),
                    mats["steel"],
                    component="pool_safety_fence",
                ),
            ]
        )
    x_picket_count = max(1, round((fence_x1 - fence_x0) / 0.34))
    for picket_index in range(x_picket_count + 1):
        x = fence_x0 + picket_index * (fence_x1 - fence_x0) / x_picket_count
        for side_index, y in enumerate((fence_y0, fence_y1)):
            objects.append(
                b(
                    f"POOL_FencePicket_X_{picket_index}_{side_index}",
                    (0.028, 0.028, 1.16),
                    (x, y, 1.10),
                    mats["steel"],
                    component="pool_safety_fence_vertical_picket",
                )
            )
    y_picket_count = max(1, round((fence_y1 - fence_y0) / 0.34))
    for picket_index in range(y_picket_count + 1):
        y = fence_y0 + picket_index * (fence_y1 - fence_y0) / y_picket_count
        for side_index, x in enumerate((fence_x0, fence_x1)):
            objects.append(
                b(
                    f"POOL_FencePicket_Y_{picket_index}_{side_index}",
                    (0.028, 0.028, 1.16),
                    (x, y, 1.10),
                    mats["steel"],
                    component="pool_safety_fence_vertical_picket",
                )
            )
    # Small cedar cabana converted from an equipment/garage-like volume.
    cabana_x = 10.1
    cabana_y = -12.5
    objects.extend(
        [
            b(
                "POOL_CabanaBack",
                (5.2, 0.22, 2.55),
                (cabana_x, cabana_y + 1.35, 1.58),
                mats["cedar"],
                component="pool_cedar_cabana",
            ),
            b(
                "POOL_CabanaRoof",
                (5.8, 3.4, 0.22),
                (cabana_x, cabana_y, 2.92),
                mats["steel"],
                bevel=0.05,
                component="pool_cedar_cabana",
            ),
            b(
                "POOL_CabanaSoffit",
                (5.55, 3.15, 0.08),
                (cabana_x, cabana_y, 2.78),
                mats["cedar"],
                component="pool_cedar_cabana",
            ),
        ]
    )
    for x in (cabana_x - 2.4, cabana_x + 2.4):
        for y in (cabana_y - 1.35, cabana_y + 1.35):
            objects.append(
                b(
                    f"POOL_CabanaPost_{x:.1f}_{y:.1f}",
                    (0.14, 0.14, 2.55),
                    (x, y, 1.55),
                    mats["cedar"],
                    bevel=0.025,
                    component="pool_cedar_cabana",
                )
            )
    for chair_index, (x, y) in enumerate(
        ((-0.2, -5.1), (2.2, -5.1), (6.2, -5.1), (8.6, -5.1))
    ):
        objects.extend(
            [
                b(
                    f"POOL_ChairSeat_{chair_index}",
                    (0.62, 0.62, 0.10),
                    (x, y, 0.75),
                    mats["bedding"],
                    bevel=0.08,
                    component="pool_deck_chair",
                ),
                b(
                    f"POOL_ChairBack_{chair_index}",
                    (0.62, 0.10, 0.72),
                    (x, y + 0.28, 1.06),
                    mats["bedding"],
                    bevel=0.06,
                    component="pool_deck_chair",
                ),
            ]
        )


def add_site(
    objects: list[bpy.types.Object],
    mats: dict[str, bpy.types.Material],
) -> None:
    objects.extend(
        [
            b(
                "SITE_AsphaltMotorCourt",
                (NATIVE_WIDTH, NATIVE_DEPTH, 0.22),
                (0.0, 0.0, 0.11),
                mats["asphalt"],
                bevel=0.05,
                component="complete_motor_court_site",
            ),
            b(
                "SITE_MainGalleryWalk",
                (45.0, 3.4, 0.16),
                (-5.5, 5.4, 0.27),
                mats["concrete"],
                bevel=0.08,
                component="continuous_ground_gallery_walk",
            ),
            b(
                "SITE_ReturnGalleryWalk",
                (3.4, 18.5, 0.16),
                (15.4, -3.0, 0.27),
                mats["concrete"],
                bevel=0.08,
                component="continuous_ground_gallery_walk",
            ),
            b(
                "SITE_CourtyardLandscapeIsland",
                (20.0, 4.8, 0.24),
                (-16.0, -6.6, 0.31),
                mats["gravel"],
                bevel=1.2,
                component="prairie_courtyard_landscape_island",
            ),
        ]
    )
    for line_index, x in enumerate((-28.0, -24.1, -20.2, -16.3, -12.4, -8.5)):
        objects.append(
            b(
                f"SITE_ParkingLine_{line_index}",
                (0.075, 5.5, 0.025),
                (x, -11.4, 0.235),
                mats["white"],
                component="parking_stall_marking",
            )
        )
    for drain_index, (x, y) in enumerate(((-7.0, -2.0), (-19.0, -9.0), (14.0, 0.5))):
        objects.append(
            b(
                f"SITE_StormDrain_{drain_index}",
                (0.75, 0.45, 0.035),
                (x, y, 0.24),
                mats["service"],
                bevel=0.04,
                component="motor_court_storm_drain",
            )
        )
    for plant_index in range(38):
        x = -25.0 + (plant_index % 19) * 1.15
        y = -7.4 + (plant_index // 19) * 1.55
        add_plant_tuft(
            objects,
            mats["prairie"],
            name=f"SITE_PrairieGrass_{plant_index:02d}",
            x=x,
            y=y,
            base_z=0.38,
            scale=0.78 + 0.08 * (plant_index % 3),
        )
    for shrub_index in range(11):
        add_shrub_cluster(
            objects,
            mats["prairie"],
            name=f"SITE_PrairieShrub_{shrub_index:02d}",
            x=-24.1 + shrub_index * 1.72,
            y=-6.55 + (0.62 if shrub_index % 2 else -0.28),
            base_z=0.40,
            scale=0.46 + 0.05 * (shrub_index % 3),
        )
    # Abstract roadside sign: no readable text or branded geometry.
    for post_index, x in enumerate((28.4, 30.2)):
        objects.append(
            b(
                f"SITE_RoadsideSignPost_{post_index}",
                (0.22, 0.22, 7.2),
                (x, -14.0, 3.84),
                mats["steel"],
                bevel=0.035,
                component="abstract_roadside_sign_structure",
            )
        )
    objects.extend(
        [
            b(
                "SITE_RoadsideSignPanel",
                (3.15, 0.30, 4.35),
                (29.3, -14.0, 5.40),
                mats["steel"],
                bevel=0.12,
                component="abstract_roadside_sign_panel",
            ),
            b(
                "SITE_RoadsideSignCedarInsert",
                (2.35, 0.08, 3.25),
                (29.3, -13.82, 5.40),
                mats["cedar"],
                bevel=0.06,
                component="abstract_roadside_sign_panel",
            ),
        ]
    )
    add_pool_and_cabana(objects, mats)


def add_shell_and_rooms(
    objects: list[bpy.types.Object],
    mats: dict[str, bpy.types.Material],
) -> None:
    objects.extend(
        [
            b(
                "SHELL_MainGroundSlab",
                (MAIN_WIDTH, MAIN_REAR_Y - MAIN_FRONT_Y, 0.24),
                (0.0, (MAIN_FRONT_Y + MAIN_REAR_Y) * 0.5, 0.32),
                mats["concrete"],
                component="main_guest_wing_floor_slab",
                level=0,
            ),
            b(
                "SHELL_MainUpperSlab",
                (MAIN_WIDTH, MAIN_REAR_Y - MAIN_FRONT_Y, 0.24),
                (0.0, (MAIN_FRONT_Y + MAIN_REAR_Y) * 0.5, 3.49),
                mats["concrete"],
                component="main_guest_wing_floor_slab",
                level=1,
            ),
            b(
                "SHELL_ReturnGroundSlab",
                (RETURN_OUTER_X - RETURN_FACE_X, RETURN_REAR_Y - RETURN_FRONT_Y, 0.24),
                (
                    (RETURN_FACE_X + RETURN_OUTER_X) * 0.5,
                    (RETURN_FRONT_Y + RETURN_REAR_Y) * 0.5,
                    0.32,
                ),
                mats["concrete"],
                component="return_guest_wing_floor_slab",
                level=0,
            ),
            b(
                "SHELL_ReturnUpperSlab",
                (RETURN_OUTER_X - RETURN_FACE_X, RETURN_REAR_Y - RETURN_FRONT_Y, 0.24),
                (
                    (RETURN_FACE_X + RETURN_OUTER_X) * 0.5,
                    (RETURN_FRONT_Y + RETURN_REAR_Y) * 0.5,
                    3.49,
                ),
                mats["concrete"],
                component="return_guest_wing_floor_slab",
                level=1,
            ),
            b(
                "SHELL_MainLeftEnd",
                (0.38, 11.0, 6.48),
                (-27.82, 12.5, 3.54),
                mats["stucco"],
                component="main_guest_wing_end_wall",
            ),
            b(
                "SHELL_MainLeftBrickPylon",
                (0.46, 11.15, 6.72),
                (-28.05, 12.5, 3.62),
                mats["brick"],
                component="russet_brick_end_pylon",
            ),
            b(
                "SHELL_ReturnFrontEnd",
                (11.0, 0.38, 6.48),
                (22.5, -11.82, 3.54),
                mats["stucco"],
                component="return_guest_wing_end_wall",
            ),
            b(
                "SHELL_ReturnFrontBrickPylon",
                (11.15, 0.46, 6.72),
                (22.5, -12.05, 3.62),
                mats["brick"],
                component="russet_brick_end_pylon",
            ),
        ]
    )
    for level in (0, 1):
        base = PODIUM_HEIGHT + level * FLOOR_HEIGHT
        for bay_index, centre in enumerate(MAIN_ROOM_CENTRES):
            add_room_bay(
                objects,
                mats,
                orientation="south",
                centre=centre,
                wall=MAIN_FRONT_Y,
                base=base,
                level=level,
                bay_index=bay_index,
            )
            add_rear_window_bay(
                objects,
                mats,
                orientation="north",
                centre=centre,
                wall=MAIN_REAR_Y,
                base=base,
                level=level,
                bay_index=bay_index,
            )
        for bay_index, centre in enumerate(RETURN_ROOM_CENTRES):
            add_room_bay(
                objects,
                mats,
                orientation="west",
                centre=centre,
                wall=RETURN_FACE_X,
                base=base,
                level=level,
                bay_index=bay_index,
            )
            add_rear_window_bay(
                objects,
                mats,
                orientation="east",
                centre=centre,
                wall=RETURN_OUTER_X,
                base=base,
                level=level,
                bay_index=bay_index,
            )
    for partition_index, x in enumerate(
        -27.5 + index * ROOM_BAY_WIDTH for index in range(11)
    ):
        objects.append(
            b(
                f"SHELL_MainRoomPartition_{partition_index:02d}",
                (0.10, 10.5, 6.25),
                (x, 12.35, 3.51),
                mats["dark"],
                component="guest_room_party_wall",
            )
        )
    for partition_index, y in enumerate((-11.4, -7.2, -3.0, 1.2, 5.4)):
        objects.append(
            b(
                f"SHELL_ReturnRoomPartition_{partition_index:02d}",
                (10.5, 0.10, 6.25),
                (22.65, y, 3.51),
                mats["dark"],
                component="guest_room_party_wall",
            )
        )
    add_gallery(objects, mats)
    add_stair(
        objects,
        mats,
        name="STAIR_MainWing",
        orientation="main",
        centre=-11.8,
    )
    add_stair(
        objects,
        mats,
        name="STAIR_ReturnWing",
        orientation="return",
        centre=-7.0,
    )


def add_roofs_and_service(
    objects: list[bpy.types.Object],
    mats: dict[str, bpy.types.Material],
) -> None:
    objects.extend(
        [
            hip_roof(
                "ROOF_MainGuestWingHip",
                (-28.70, 15.30, 6.25, 18.70),
                6.82,
                8.34,
                mats["shingle"],
                component="deep_eaved_main_guest_wing_hip_roof",
            ),
            hip_roof(
                "ROOF_ReturnGuestWingHip",
                (16.30, 28.70, -12.70, 5.00),
                6.82,
                8.34,
                mats["shingle"],
                component="deep_eaved_return_guest_wing_hip_roof",
            ),
            b(
                "ROOF_MainFrontFascia",
                (44.0, 0.18, 0.28),
                (-6.7, 6.25, 6.75),
                mats["steel"],
                component="charcoal_roof_fascia",
            ),
            b(
                "ROOF_MainRearFascia",
                (44.0, 0.18, 0.28),
                (-6.7, 18.70, 6.75),
                mats["steel"],
                component="charcoal_roof_fascia",
            ),
            b(
                "ROOF_ReturnWestFascia",
                (0.18, 17.7, 0.28),
                (16.30, -3.85, 6.75),
                mats["steel"],
                component="charcoal_roof_fascia",
            ),
            b(
                "ROOF_ReturnEastFascia",
                (0.18, 17.7, 0.28),
                (28.70, -3.85, 6.75),
                mats["steel"],
                component="charcoal_roof_fascia",
            ),
            b(
                "ROOF_MainRearGutter",
                (43.0, 0.16, 0.16),
                (-6.7, 18.66, 6.62),
                mats["steel"],
                bevel=0.035,
                component="continuous_roof_gutter",
            ),
            b(
                "ROOF_ReturnEastGutter",
                (0.16, 16.7, 0.16),
                (28.66, -3.85, 6.62),
                mats["steel"],
                bevel=0.035,
                component="continuous_roof_gutter",
            ),
        ]
    )
    for downspout_index, x in enumerate((-26.5, -15.0, -3.5, 8.0, 13.8)):
        objects.append(
            c(
                f"SERVICE_MainDownspout_{downspout_index}",
                0.055,
                6.25,
                (x, 18.58, 3.47),
                mats["steel"],
                vertices=12,
                component="roof_downspout",
            )
        )
    for downspout_index, y in enumerate((-10.5, -1.5, 6.5)):
        objects.append(
            c(
                f"SERVICE_ReturnDownspout_{downspout_index}",
                0.055,
                6.25,
                (28.58, y, 3.47),
                mats["steel"],
                vertices=12,
                component="roof_downspout",
            )
        )
    # Organized rear equipment at room-bay datums.
    for unit_index, x in enumerate((-22.0, -13.6, -5.2, 3.2, 11.6)):
        objects.extend(
            [
                b(
                    f"SERVICE_CondenserPad_{unit_index}",
                    (1.45, 1.05, 0.12),
                    (x, 18.45, 0.34),
                    mats["concrete"],
                    bevel=0.04,
                    component="rear_heat_pump_pad",
                ),
                b(
                    f"SERVICE_Condenser_{unit_index}",
                    (1.05, 0.78, 0.82),
                    (x, 18.45, 0.80),
                    mats["service"],
                    bevel=0.08,
                    component="rear_heat_pump_condenser",
                ),
            ]
        )
        for grille_index in range(4):
            objects.append(
                b(
                    f"SERVICE_CondenserGrille_{unit_index}_{grille_index}",
                    (0.82, 0.035, 0.055),
                    (
                        x,
                        18.88,
                        0.57 + grille_index * 0.15,
                    ),
                    mats["steel"],
                    component="rear_heat_pump_condenser_grille",
                )
            )
    objects.append(
        b(
            "SERVICE_MeterBackboard",
            (4.6, 0.14, 1.55),
            (19.7, 18.18, 1.28),
            mats["service"],
            bevel=0.025,
            component="organized_rear_meter_bank",
        )
    )
    for meter_index in range(8):
        x = 17.9 + (meter_index % 4) * 1.15
        z = 0.92 + (meter_index // 4) * 0.72
        objects.extend(
            [
                c(
                    f"SERVICE_Meter_{meter_index}",
                    0.18,
                    0.11,
                    (x, 18.10, z),
                    mats["galvanized"],
                    vertices=20,
                    component="organized_rear_meter_bank",
                ),
                b(
                    f"SERVICE_MeterBox_{meter_index}",
                    (0.46, 0.12, 0.50),
                    (x, 18.10, z),
                    mats["service"],
                    bevel=0.025,
                    component="organized_rear_meter_bank",
                ),
            ]
        )
    # Screened two-bin refuse/pool equipment enclosure.
    objects.extend(
        [
            b(
                "SERVICE_RefuseScreenNorth",
                (3.0, 0.18, 2.15),
                (30.0, 15.3, 1.38),
                mats["cedar"],
                component="screened_two_bin_refuse_enclosure",
            ),
            b(
                "SERVICE_RefuseScreenWest",
                (0.18, 4.0, 2.15),
                (28.5, 13.4, 1.38),
                mats["cedar"],
                component="screened_two_bin_refuse_enclosure",
            ),
            b(
                "SERVICE_RefuseScreenEast",
                (0.18, 4.0, 2.15),
                (31.5, 13.4, 1.38),
                mats["cedar"],
                component="screened_two_bin_refuse_enclosure",
            ),
        ]
    )
    for bin_index, x in enumerate((29.25, 30.75)):
        objects.append(
            b(
                f"SERVICE_RefuseBin_{bin_index}",
                (1.10, 1.35, 1.42),
                (x, 14.0, 0.99),
                mats["service"],
                bevel=0.13,
                component="screened_refuse_bin",
            )
        )
    for vent_index, (x, y) in enumerate(
        ((-19.0, 12.7), (-8.0, 12.6), (5.0, 12.6), (22.4, -7.5))
    ):
        objects.append(
            c(
                f"ROOF_RidgeVent_{vent_index}",
                0.13,
                0.72,
                (x, y, 8.12),
                mats["service"],
                vertices=14,
                component="roof_vent",
            )
        )


def build_assembled(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    add_site(objects, mats)
    add_shell_and_rooms(objects, mats)
    add_lobby(objects, mats)
    add_roofs_and_service(objects, mats)
    return objects


def add_module_floor(
    mats: dict[str, bpy.types.Material],
    variant: str,
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = [
        b(
            f"MODULE_{variant}_FloorSlab",
            (52.0, 11.0, 0.20),
            (0.0, 0.0, 0.10),
            mats["concrete"],
            component="repeatable_guest_room_floor_slab",
            variant=variant,
        ),
        b(
            f"MODULE_{variant}_GallerySlab",
            (52.0, 1.82, 0.18),
            (0.0, -6.0, 0.11),
            mats["concrete"],
            component="repeatable_exterior_gallery_slab",
            variant=variant,
        ),
    ]
    centres = tuple(-23.1 + index * ROOM_BAY_WIDTH for index in range(12))
    for bay_index, centre in enumerate(centres):
        add_room_bay(
            objects,
            mats,
            orientation="south",
            centre=centre,
            wall=-5.5,
            base=0.20,
            level=0,
            bay_index=bay_index,
            variant=variant,
        )
        add_rear_window_bay(
            objects,
            mats,
            orientation="north",
            centre=centre,
            wall=5.5,
            base=0.20,
            level=0,
            bay_index=bay_index,
        )
    for post_index, x in enumerate(-25.2 + index * 1.40 for index in range(37)):
        objects.append(
            b(
                f"MODULE_{variant}_GalleryRailPost_{post_index:02d}",
                (0.055, 0.055, 1.05),
                (x, -6.90, 0.72),
                mats["steel"],
                component="repeatable_gallery_guardrail",
                variant=variant,
            )
        )
    for rail_index, z in enumerate((0.42, 0.63, 0.84, 1.05, 1.26)):
        objects.append(
            b(
                f"MODULE_{variant}_GalleryRail_{rail_index}",
                (52.0, 0.045, 0.045),
                (0.0, -6.92, z),
                mats["steel"],
                component="repeatable_gallery_guardrail",
                variant=variant,
            )
        )
    objects.extend(module_contract_markers("floor", variant, FLOOR_HEIGHT))
    return objects


def build_module(
    role: str,
    variant: str,
    mats: dict[str, bpy.types.Material],
) -> tuple[list[bpy.types.Object], float]:
    if role == "podium":
        height = PODIUM_HEIGHT
        objects = [
            b(
                "MODULE_PodiumMotorCourt",
                (NATIVE_WIDTH, NATIVE_DEPTH, PODIUM_HEIGHT),
                (0.0, 0.0, PODIUM_HEIGHT * 0.5),
                mats["asphalt"],
                bevel=0.04,
                component="fixed_motor_court_podium",
            ),
            b(
                "MODULE_PodiumGalleryWalk",
                (54.0, 3.0, 0.15),
                (0.0, -6.3, PODIUM_HEIGHT + 0.075),
                mats["concrete"],
                bevel=0.06,
                component="fixed_accessible_gallery_walk",
            ),
        ]
        objects.extend(module_contract_markers(role, variant, height))
    elif role == "floor":
        height = FLOOR_HEIGHT
        objects = add_module_floor(mats, variant)
    elif role == "crown":
        height = CROWN_HEIGHT
        objects = [
            b(
                "MODULE_CrownCedarSoffit",
                (56.0, 12.4, 0.16),
                (0.0, 0.0, 0.18),
                mats["cedar"],
                component="fixed_deep_cedar_eave",
            ),
            b(
                "MODULE_CrownFrontFascia",
                (57.2, 0.18, 0.30),
                (0.0, -6.25, 0.34),
                mats["steel"],
                component="fixed_charcoal_roof_fascia",
            ),
            b(
                "MODULE_CrownRearFascia",
                (57.2, 0.18, 0.30),
                (0.0, 6.25, 0.34),
                mats["steel"],
                component="fixed_charcoal_roof_fascia",
            ),
        ]
        objects.extend(module_contract_markers(role, variant, height))
    elif role == "roof":
        height = ROOF_HEIGHT
        objects = [
            hip_roof(
                "MODULE_RoofHip",
                (-28.7, 28.7, -6.3, 6.3),
                0.14,
                ROOF_HEIGHT,
                mats["shingle"],
                component="fixed_shallow_hip_roof",
            )
        ]
    else:
        raise ValueError(role)
    return objects, height


def evaluated_triangle_count(objects: list[bpy.types.Object]) -> int:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    count = 0
    for obj in objects:
        if obj.type != "MESH":
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        count += sum(max(1, len(poly.vertices) - 2) for poly in mesh.polygons)
        evaluated.to_mesh_clear()
    return count


def material_count(objects: list[bpy.types.Object]) -> int:
    return len(
        {
            slot.material.name
            for obj in objects
            if obj.type == "MESH"
            for slot in obj.material_slots
            if slot.material
        }
    )


def normalize_bottom_origin(objects: list[bpy.types.Object]) -> None:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    minimum_z = min(
        (evaluated.matrix_world @ Vector(corner)).z
        for obj in objects
        if obj.type == "MESH"
        for evaluated in (obj.evaluated_get(depsgraph),)
        for corner in evaluated.bound_box
    )
    for obj in objects:
        obj.location.z -= minimum_z
    bpy.context.view_layer.update()


def module_payload(
    role: str,
    variant: str,
    filename: str,
    height: float,
    objects: list[bpy.types.Object],
    size_bytes: int,
    skin: dict,
) -> dict:
    repeatable = role == "floor"
    return {
        "role": role,
        "variant_key": variant,
        "assembly_class": "repeatable_middle" if repeatable else "fixed_semantic",
        "fixed_semantic": not repeatable,
        "lod": 0,
        "allowed_levels": [0, 1, 2],
        "filename": filename,
        "module_family": FAMILY,
        "width_m": NATIVE_WIDTH,
        "depth_m": NATIVE_DEPTH,
        "height_m": height,
        "floor_height_m": FLOOR_HEIGHT,
        "repeatable_z": repeatable,
        "allow_inset_footprint": True,
        "triangle_count": evaluated_triangle_count(objects),
        "material_count": material_count(objects),
        "texture_keys": sorted(skin["zones"]),
        "ao_baked": True,
        "size_bytes": size_bytes,
    }


def add_presentation_context(
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    road = material(
        "MAT_W10_MOTOR_INN_PresentationRoad",
        (0.052, 0.055, 0.055, 1.0),
        0.91,
    )
    objects = [
        box(
            "PRESENTATION_PrairieGround",
            (125.0, 105.0, 0.18),
            (0.0, 0.0, -0.18),
            mats["prairie"],
            0.04,
        ),
        box(
            "PRESENTATION_Highway",
            (125.0, 12.0, 0.18),
            (0.0, -29.0, -0.02),
            road,
            0.03,
        ),
    ]
    for line_index, x in enumerate(range(-56, 57, 8)):
        objects.append(
            box(
                f"PRESENTATION_HighwayDash_{line_index}",
                (4.5, 0.12, 0.025),
                (float(x), -29.0, 0.08),
                mats["white"],
            )
        )
    for plant_index in range(58):
        x = -59.0 + plant_index * 2.05
        y = 27.0 + math.sin(plant_index * 1.23) * 2.8
        add_plant_tuft(
            objects,
            mats["prairie"],
            name=f"PRESENTATION_PrairieGrass_{plant_index:02d}",
            x=x,
            y=y,
            base_z=0.0,
            scale=0.86 + 0.12 * ((plant_index * 5) % 4),
        )
    return objects


def configure_render() -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 920
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.view_settings.exposure = 0.26
    scene.eevee.taa_render_samples = 96
    scene.eevee.use_raytracing = True
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass
    for obj in list(bpy.data.objects):
        if obj.type == "LIGHT":
            bpy.data.objects.remove(obj, do_unlink=True)
    world = scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputWorld")
    background = nodes.new("ShaderNodeBackground")
    background.inputs["Strength"].default_value = 0.82
    coordinates = nodes.new("ShaderNodeTexCoord")
    separate = nodes.new("ShaderNodeSeparateXYZ")
    gradient = nodes.new("ShaderNodeValToRGB")
    gradient.color_ramp.elements[0].position = 0.0
    gradient.color_ramp.elements[0].color = (0.42, 0.62, 0.88, 1.0)
    gradient.color_ramp.elements[1].position = 0.70
    gradient.color_ramp.elements[1].color = (0.10, 0.24, 0.52, 1.0)
    links.new(coordinates.outputs["Normal"], separate.inputs["Vector"])
    links.new(separate.outputs["Z"], gradient.inputs["Fac"])
    links.new(gradient.outputs["Color"], background.inputs["Color"])
    links.new(background.outputs["Background"], output.inputs["Surface"])
    bpy.ops.object.light_add(type="SUN", location=(-48.0, -66.0, 82.0))
    sun = bpy.context.object
    sun.name = "PRESENTATION_MotorInnSun"
    sun.data.energy = 2.15
    sun.data.color = (1.0, 0.87, 0.72)
    sun.data.angle = math.radians(5.5)
    sun.rotation_euler = (
        Vector((-2.0, 3.0, 3.5)) - sun.location
    ).to_track_quat("-Z", "Y").to_euler()
    bpy.ops.object.light_add(type="AREA", location=(-8.0, -24.0, 15.0))
    fill = bpy.context.object
    fill.name = "PRESENTATION_CourtyardFill"
    fill.data.energy = 1750.0
    fill.data.shape = "RECTANGLE"
    fill.data.size = 46.0
    fill.data.size_y = 18.0
    fill.rotation_euler = (
        Vector((-4.0, 6.0, 3.7)) - fill.location
    ).to_track_quat("-Z", "Y").to_euler()
    bpy.ops.object.light_add(type="AREA", location=(14.9, 5.2, 4.8))
    interior = bpy.context.object
    interior.name = "PRESENTATION_LobbyWarmFill"
    interior.data.energy = 1450.0
    interior.data.color = (1.0, 0.58, 0.27)
    interior.data.shape = "RECTANGLE"
    interior.data.size = 11.0
    interior.data.size_y = 8.0
    interior.rotation_euler = (
        Vector((15.1, 2.3, 3.0)) - interior.location
    ).to_track_quat("-Z", "Y").to_euler()


def render_views(
    folder: Path,
    mats: dict[str, bpy.types.Material],
    *,
    view_set: str,
) -> list[str]:
    context = add_presentation_context(mats)
    configure_render()
    views = {
        "preview": ((-55.0, -53.0, 13.0), (0.0, 3.0, 3.5), 50),
        "street": ((-18.0, -54.0, 5.8), (1.0, 4.0, 3.45), 53),
        "front_corner_oblique": ((-43.0, -38.0, 14.5), (3.0, 4.0, 3.6), 55),
        "rear_corner_oblique": ((-43.0, 38.0, 13.5), (0.0, 11.0, 3.8), 57),
        "aerial": ((-43.0, -37.0, 48.0), (1.0, 2.0, 3.5), 55),
        "facade_close": ((-19.0, -9.0, 5.5), (-9.0, 7.0, 3.5), 68),
        "stair_close": ((-22.0, -9.0, 5.4), (-11.8, 4.2, 2.8), 72),
        "window_close": ((-5.0, -4.8, 4.8), (-3.5, 7.0, 3.55), 76),
        "lobby_close": ((-3.0, -8.0, 2.65), (15.1, 2.45, 2.55), 56),
        "pool_close": ((-8.0, -18.0, 7.2), (3.5, -7.0, 1.2), 66),
        "service_close": ((42.0, 31.0, 6.8), (8.0, 18.7, 1.65), 54),
        "roof_close": ((-35.0, -10.0, 35.0), (2.0, 5.0, 5.8), 62),
        "context": ((-60.0, -58.0, 25.0), (1.0, 3.0, 3.4), 58),
    }
    pilot = {
        "preview",
        "street",
        "front_corner_oblique",
        "rear_corner_oblique",
        "aerial",
        "facade_close",
        "stair_close",
        "window_close",
        "lobby_close",
        "service_close",
        "context",
    }
    if view_set == "preview":
        selected = {"preview"}
    elif view_set == "pilot":
        selected = pilot
    elif view_set == "all":
        selected = set(views)
    elif view_set in views:
        selected = {view_set}
    else:
        raise ValueError(f"Unknown render view: {view_set}")
    glass_snapshots: list[
        tuple[bpy.types.Material, bpy.types.Node, float, float, str]
    ] = []
    for mat in bpy.data.materials:
        if not mat.get("glazing_profile") or not mat.use_nodes:
            continue
        bsdf = next(
            (
                node
                for node in mat.node_tree.nodes
                if node.bl_idname == "ShaderNodeBsdfPrincipled"
            ),
            None,
        )
        if bsdf is None or not bsdf.inputs.get("Alpha"):
            continue
        transmission = bsdf.inputs.get("Transmission Weight")
        glass_snapshots.append(
            (
                mat,
                bsdf,
                float(bsdf.inputs["Alpha"].default_value),
                float(transmission.default_value) if transmission else 0.0,
                getattr(mat, "surface_render_method", "DITHERED"),
            )
        )
        bsdf.inputs["Alpha"].default_value = 0.09
        mat.diffuse_color = (*tuple(mat.diffuse_color)[:3], 0.09)
        if transmission:
            transmission.default_value = 0.0
        if hasattr(mat, "surface_render_method"):
            mat.surface_render_method = "BLENDED"
    renders: list[str] = []
    try:
        for role, (location, target, lens) in views.items():
            if role not in selected:
                continue
            aim_camera(location, target, lens)
            scene = bpy.context.scene
            scene.render.filepath = str(folder / f"{FAMILY}_{role}.png")
            bpy.ops.render.render(write_still=True)
            renders.append(f"{FAMILY}_{role}.png")
    finally:
        for mat, bsdf, alpha, transmission_value, method in glass_snapshots:
            bsdf.inputs["Alpha"].default_value = alpha
            transmission = bsdf.inputs.get("Transmission Weight")
            if transmission:
                transmission.default_value = transmission_value
            if hasattr(mat, "surface_render_method"):
                mat.surface_render_method = method
            mat.diffuse_color = (*tuple(mat.diffuse_color)[:3], 1.0)
        delete_objects(context)
    return renders


def footprint_contract() -> dict:
    rectangle = {
        "recommendedWidth_m": [32.0, 92.0],
        "recommendedDepth_m": [14.0, 32.0],
        "recommendedFloors": [1, 3],
        "preferredBayMultiple_m": ROOM_BAY_WIDTH,
    }
    l_shape = {
        "recommendedWidth_m": [46.0, 108.0],
        "recommendedDepth_m": [26.0, 60.0],
        "recommendedFloors": [1, 3],
        "wingDepth_m": [10.0, 17.0],
        "preferredBayMultiple_m": ROOM_BAY_WIDTH,
        "minimumCourtyard_m": 14.0,
    }
    u_shape = {
        "recommendedWidth_m": [56.0, 126.0],
        "recommendedDepth_m": [32.0, 74.0],
        "recommendedFloors": [1, 3],
        "wingDepth_m": [10.0, 17.0],
        "preferredBayMultiple_m": ROOM_BAY_WIDTH,
        "minimumCourtyard_m": 16.0,
    }
    return {
        "preferredProfiles": ["rectangle", "l_shape", "u_shape"],
        "minimumPreferredProfiles": 3,
        "profileRationale": (
            "The identity is a sequence of complete 4.2 metre guest-room bays "
            "served by a continuous exterior gallery. Rectangles preserve one "
            "roadside bar; L and U drawings turn whole bars at gallery-connected "
            "corners while keeping room openings, stairs, eaves and service "
            "datums intact."
        ),
        "fixedLandmarkScaleBand": {
            "scaleMin": 0.72,
            "scaleMax": 1.34,
            "maxAxisRatio": 1.30,
        },
        "recommendedWidth_m": [32.0, 108.0],
        "recommendedDepth_m": [14.0, 60.0],
        "recommendedFloors": [1, 3],
        "wingDepth_m": [10.0, 17.0],
        "preferredBayMultiple_m": ROOM_BAY_WIDTH,
        "minimumCourtyard_m": 14.0,
        "profiles": {
            "rectangle": rectangle,
            "l_shape": l_shape,
            "u_shape": u_shape,
        },
    }


def facade_sheet_contract(skin: dict) -> dict:
    contract = facade_contract(
        FAMILY,
        skin,
        f"/families/{FAMILY}/textures/source/archetype-goalpost.png",
    )
    contract["geometry_detail_profile"] = "hero"
    contract["bay_strategy"] = {
        "fixed_end_bays": [
            "russet_brick_end_pylon_and_integrated_stair",
            "inside_corner_glazed_lobby_and_porte_cochere",
        ],
        "repeatable_middle_bays": list(range(1, 11)),
        "middle_variants": ["typical_a", "typical_b", "typical_c"],
        "rule": (
            "Repeat complete 4.2 metre room bays along each guest wing. Keep "
            "door, paired low-E window, occupied depth, gallery column, rail "
            "attachments, rear vent and roof datum registered to the bay; never "
            "stretch one door or pane."
        ),
    }
    contract["assembly_contract"] = {
        "fixed": [
            "podium/entrance",
            "corner returns",
            "crown",
            "roof",
            "inside-corner lobby and porte-cochere",
            "two integrated stairs and upper landings",
            "deep cedar eaves and hip roofs",
            "pool court and rear service edge",
        ],
        "repeatable": ["typical_a", "typical_b", "typical_c"],
        "side_elevations": (
            "The courtyard sides carry doors, occupied paired windows and the "
            "continuous exterior gallery; outside elevations carry only deeply "
            "inset guest windows, vents, gutters, downspouts, organized "
            "condensers, meters, service access and screened refuse."
        ),
        "elevation_coverage": {
            "front": "ten occupied main-wing room bays, gallery and integrated stair",
            "left": "full-depth russet brick end pylon and hip roof return",
            "right": "four occupied return-wing bays, gallery and integrated stair",
            "rear": "quiet paired-window schedule, vents, utilities and screened service",
            "roof": "two coherent shallow hip roofs, lobby hip, gutters and vents",
        },
        "variation_policy": (
            "Scale complete room-bar assemblies only inside 0.72-1.34 with an "
            "independent-axis ratio no greater than 1.30. Larger targets use "
            "long-axis streetwall repeat of whole 4.2 metre room bays, never "
            "family_incompatible."
        ),
    }
    return contract


def build_modules(
    folder: Path,
    mats: dict[str, bpy.types.Material],
    skin: dict,
) -> list[dict]:
    specs = (
        ("podium", "default"),
        ("floor", "typical_a"),
        ("floor", "typical_b"),
        ("floor", "typical_c"),
        ("crown", "crown"),
        ("roof", "default"),
    )
    payloads: list[dict] = []
    for role, variant in specs:
        objects, height = build_module(role, variant, mats)
        normalize_bottom_origin(objects)
        suffix = role if variant == "default" else f"{role}_{variant}"
        filename = f"{FAMILY}_{suffix}.glb"
        destination = folder / filename
        export_glb(destination, objects)
        payloads.append(
            module_payload(
                role,
                variant,
                filename,
                height,
                objects,
                destination.stat().st_size,
                skin,
            )
        )
        delete_objects(objects)
    return payloads


def build_family(
    output_root: Path,
    *,
    view_set: str,
    skip_renders: bool,
    skip_modules: bool,
    skip_assembled_export: bool,
) -> None:
    clear_scene()
    folder = output_root / FAMILY
    folder.mkdir(parents=True, exist_ok=True)
    mats, skin = load_palette(folder)
    objects = build_assembled(mats)
    normalize_bottom_origin(objects)
    assembled_path = folder / f"{FAMILY}_assembled.glb"
    manifest_path = folder / f"{FAMILY}_manifest.json"
    previous = (
        json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest_path.is_file()
        else {}
    )
    if not skip_assembled_export:
        export_glb(assembled_path, objects)
        assembled_triangles = evaluated_triangle_count(objects)
        assembled_materials = material_count(objects)
    else:
        assembled_triangles = int(
            (previous.get("assembled") or {}).get("triangle_count")
            or evaluated_triangle_count(objects)
        )
        assembled_materials = int(
            (previous.get("assembled") or {}).get("material_count")
            or material_count(objects)
        )
    renders = (
        list(previous.get("renders") or [])
        if skip_renders
        else render_views(folder, mats, view_set=view_set)
    )
    delete_objects(objects)
    modules = (
        list(previous.get("modules") or [])
        if skip_modules
        else build_modules(folder, mats, skin)
    )
    footprint = footprint_contract()
    massing_graph = {
        "type": "modular_exterior_corridor_motor_inn",
        "silhouette": "two_storey_L_wings_with_deep_hip_roofs_and_raised_lobby",
        "main_guest_wing_bays": 10,
        "return_guest_wing_bays": 4,
        "guest_room_levels": 2,
        "occupied_guest_room_modules": 28,
        "exterior_gallery_depth_m": 1.8,
        "integrated_stair_assemblies": 2,
        "inside_corner_glazed_lobby": 1,
        "porte_cochere_structural_columns": 2,
        "pool_basins": 1,
        "pool_cabana_modules": 1,
        "rear_condenser_units": 5,
        "screened_refuse_bins": 2,
    }
    assembled = {
        "filename": assembled_path.name,
        "floors": NATIVE_FLOORS,
        "uses_setback": False,
        "uses_crown": True,
        "height_m": NATIVE_HEIGHT,
        "triangle_count": assembled_triangles,
        "material_count": assembled_materials,
        "stack": [
            {
                "role": "assembled",
                "variant_key": "reference_locked",
                "level": 0,
                "z_m": 0.0,
                "height_m": NATIVE_HEIGHT,
            }
        ],
        "footprint_profile": "l_shape",
        "footprint_target": {
            "width_m": NATIVE_WIDTH,
            "depth_m": NATIVE_DEPTH,
            "wing_depth_m": 11.0,
            "segments": [
                {
                    "id": "main_ten_bay_guest_wing",
                    "centre_x_m": 0.0,
                    "centre_y_m": 12.5,
                    "length_m": MAIN_WIDTH,
                    "thickness_m": 11.0,
                    "rotation_degrees": 0.0,
                },
                {
                    "id": "return_four_bay_guest_wing",
                    "centre_x_m": 22.5,
                    "centre_y_m": 3.0,
                    "length_m": 30.0,
                    "thickness_m": 11.0,
                    "rotation_degrees": 90.0,
                },
                {
                    "id": "inside_corner_lobby",
                    "centre_x_m": 21.5,
                    "centre_y_m": 10.6,
                    "length_m": 13.0,
                    "thickness_m": 11.2,
                    "rotation_degrees": 0.0,
                },
            ],
        },
        "massing_graph": massing_graph,
        "texture_keys": sorted(skin["zones"]),
        "ao_baked": True,
    }
    manifest = {
        "manifest_schema": 3,
        "grammar_schema_version": 3,
        "generator": {
            "name": "archetype_compiler/generate_wave10_motor_inn_family.py",
            "version": "1.0.0",
            "blender_version": bpy.app.version_string,
            "render_engine": "BLENDER_EEVEE",
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "family": FAMILY,
        "archetype_id": ARCHETYPE_ID,
        "archetype_label": LABEL,
        "variant_id": VARIANT_ID,
        "generation_archetype_id": VARIANT_ID,
        "archetype_aliases": ALIASES,
        "aesthetic_category_id": "roadside_commercial",
        "development_type": "hospitality",
        "reuse_keys": [
            *ALIASES,
            "Highway Motor Hotel",
            "Two-Storey Motor Inn",
            "Prairie Courtyard Motel",
            "Exterior Corridor Hotel",
        ],
        "generation_tags": [
            "wave10",
            "standard_building",
            "modular_hospitality_bar",
            "custom_pbr_skin",
            "physical_guest_room_glazing",
            "occupied_guest_room_depth",
            "continuous_exterior_gallery",
            "integrated_structural_stairs",
            "deep_eaved_hip_roofs",
            "inside_corner_glazed_lobby",
            "complete_pool_and_rear_service_edge",
        ],
        "footprint_compatibility": footprint,
        "coordinate_contract": COORDINATE_CONTRACT,
        "textures": texture_inventory(skin),
        "facade_sheet": facade_sheet_contract(skin),
        "massing_graph": massing_graph,
        "material_budget": {
            "max_assembled_materials": 30,
            "rationale": (
                "Ivory stucco, russet brick, charcoal shingles, cedar soffit, "
                "kelp doors, black structural steel, galvanized treads, physical "
                "low-E guest/lobby glazing, curtains, occupied room/lobby depth, "
                "concrete, asphalt, pool water, planting, service metal, lighting "
                "and furniture remain optically distinct because those responses "
                "carry the reference identity."
            ),
        },
        "dimensions": {
            "width_m": NATIVE_WIDTH,
            "depth_m": NATIVE_DEPTH,
            "podium_height_m": PODIUM_HEIGHT,
            "floor_height_m": FLOOR_HEIGHT,
            "setback_height_m": FLOOR_HEIGHT,
            "roof_height_m": ROOF_HEIGHT,
            "crown_height_m": CROWN_HEIGHT,
            "default_floors": NATIVE_FLOORS,
            "min_floors": MIN_FLOORS,
            "max_floors": MAX_FLOORS,
        },
        "native_width_m": NATIVE_WIDTH,
        "native_depth_m": NATIVE_DEPTH,
        "native_floors": NATIVE_FLOORS,
        "min_floors": MIN_FLOORS,
        "max_floors": MAX_FLOORS,
        "default_floors": NATIVE_FLOORS,
        "modules": modules,
        "assembled": assembled,
        "thumbnail": f"{FAMILY}_preview.png",
        "renders": renders,
        "architectural_identity": (
            "Two deep-eaved hip-roof guest wings form an L-shaped motor court "
            "around a landscaped pool, with repeated occupied room openings, a "
            "continuous black-steel gallery, two integrated open-tread stairs "
            "and a taller brick-and-glass inside-corner lobby."
        ),
        "material_zones": (
            "warm ivory fine-grain stucco; dark russet running-bond brick base "
            "and pylons; charcoal dimensional asphalt shingles; warm cedar "
            "tongue-and-groove soffits; muted kelp-green metal room doors; "
            "bronze-black gallery steel; galvanized stair treads; physical "
            "neutral low-E guest and lobby glazing; sheer and blackout curtains; "
            "occupied room and lobby depth; pale concrete; asphalt; pool water; "
            "prairie planting; organized rear service metal"
        ),
        "glass_profile": GLASS_PROFILE,
        "source_provenance": {
            "catalogue_archetype_id": ARCHETYPE_ID,
            "catalogue_variant_id": VARIANT_ID,
            "catalogue_alias_ids": ALIASES[2:],
            "elevation_source": f"/families/{FAMILY}/elevation.jpg",
            "goalpost": f"/families/{FAMILY}/textures/source/archetype-goalpost.png",
            "reference_generation": (
                f"/families/{FAMILY}/textures/source/reference-generation.json"
            ),
            "method": (
                "reference-locked eight-view ImageGen source pack, nine-zone "
                "orthographic construction plate, deterministic L-shaped metric "
                "geometry, physical room/lobby openings, modeled occupied depth, "
                "structurally continuous stairs/gallery, coherent hip roofs, "
                "pool court and complete rear service schedule"
            ),
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    grammar = {
        "family_id": FAMILY,
        "source": {
            "archetype_id": ARCHETYPE_ID,
            "variant_id": VARIANT_ID,
            "generation_archetype_id": VARIANT_ID,
            "reuse_keys": manifest["reuse_keys"],
        },
        "dimensions": manifest["dimensions"],
        "architectural_signature": {
            "identity": manifest["architectural_identity"],
            "material_zones": manifest["material_zones"],
            "glass_profile": manifest["glass_profile"],
            "kits": [
                "reference_locked_L_shaped_motor_inn",
                "physical_guest_room_opening_bays",
                "integrated_gallery_and_stair_assemblies",
                "inside_corner_lobby_and_porte_cochere",
                "complete_pool_roof_and_rear_service",
                "flexible_semantic_stack",
            ],
        },
        "archetype_aliases": ALIASES,
        "footprint_compatibility": footprint,
        "massing_graph": massing_graph,
    }
    (folder / "grammar.json").write_text(
        json.dumps(grammar, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (folder / "archetype-source.json").write_text(
        json.dumps(manifest["source_provenance"], indent=2, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    print(
        f"[wave10-motor-inn] {FAMILY}: {assembled_triangles} triangles, "
        f"{assembled_materials} materials, {len(modules)} modules, "
        f"{len(renders)} renders",
        flush=True,
    )


def render_existing(output_root: Path, *, view_set: str) -> None:
    clear_scene()
    folder = output_root / FAMILY
    mats, _skin = load_palette(folder)
    manifest_path = folder / f"{FAMILY}_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    bpy.ops.import_scene.gltf(
        filepath=str(folder / manifest["assembled"]["filename"])
    )
    render_views(folder, mats, view_set=view_set)
    manifest["renders"] = sorted(
        path.name
        for path in folder.glob(f"{FAMILY}_*.png")
        if path.is_file()
    )
    if (folder / "elevation.jpg").is_file():
        manifest["renders"].append("elevation.jpg")
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"[wave10-motor-inn-render] {FAMILY}: {len(manifest['renders'])} renders"
    )


def main() -> int:
    args = parse_args()
    output_root = args.output_root.resolve()
    if args.render_existing:
        render_existing(output_root, view_set=args.view_set)
    else:
        build_family(
            output_root,
            view_set=args.view_set,
            skip_renders=args.skip_renders,
            skip_modules=args.skip_modules,
            skip_assembled_export=args.skip_assembled_export,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
