"""Generate reference-locked Wave 4 standard LEGO building families.

Wave 4 applies the same construction effort used for the sculptural civic
landmarks to ordinary urban buildings.  The pilot is Historical Brick Main
Street: a genuinely modular two-storey Victorian shop block whose fixed
storefront and crown surround repeatable upper-floor bands.

Run with Blender 5.x:

    blender --background --factory-startup --python \
      tools/archetype_compiler/generate_wave4_standard_families.py -- \
      --output-root frontend/public/families \
      --family historical-brick-main-street --view-set all
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

from generate_wave3_landmark_families import (  # noqa: E402
    COORDINATE_CONTRACT,
    aim_camera,
    arch_frame,
    arched_panel,
    beam,
    box,
    cylinder,
    delete_objects,
    export_glb,
    material,
    module_contract_markers,
    setup_render,
    triangle_count,
)


FAMILY = "historical-brick-main-street"
CONFIG = {
    "archetype_id": "historical_brick_main_street",
    "variant_id": "historical_brick_victorian",
    "generation_archetype_id": "historical_brick_victorian",
    "label": "Historical Brick Main Street — Victorian Polychrome",
    "dimensions": (15.0, 22.0, 11.25),
    "floors": (2, 4, 2),
    "podium_height_m": 3.80,
    "floor_height_m": 3.60,
    "crown_height_m": 1.45,
    "roof_height_m": 2.40,
    "development_type": "commercial_light",
    "aesthetic_category_id": "historical",
    "aliases": ["historical_brick_main_street", "historical_brick_victorian"],
    "reuse_keys": [
        "historical_brick_main_street",
        "historical_brick_victorian",
        "Commercial — Main Street / Heritage Retail",
    ],
    "identity": (
        "A two-storey Victorian polychrome main-street shop with six fixed "
        "round-arched upper sashes, red-and-cream brick banding, a deep "
        "forest-green cast-iron double storefront, carved frieze and panelled "
        "parapet around a concealed corrugated service roof."
    ),
    "materials": (
        "rich red pressed brick; cream brick and carved limestone; forest-green "
        "painted cast iron and timber; weathered corrugated metal; clear occupied "
        "heritage glazing"
    ),
    "glass_profile": "heritage_leaded_occupied",
    "kits": [
        "cast_iron_double_storefront",
        "round_arch_sashes",
        "polychrome_brick_bands",
        "carved_floral_frieze",
        "panelled_parapet",
        "concealed_service_roof",
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("frontend/public/families"),
    )
    parser.add_argument("--family", choices=[FAMILY], default=FAMILY)
    parser.add_argument("--view-set", choices=("pilot", "all"), default="all")
    parser.add_argument("--skip-renders", action="store_true")
    parser.add_argument(
        "--skip-modules",
        action="store_true",
        help="Bounded visual pilot: export/render only the canonical assembled model.",
    )
    parser.add_argument("--render-existing", action="store_true")
    return parser.parse_args(sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else [])


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for item in list(block):
            if item.users == 0:
                block.remove(item)


def _principled(mat: bpy.types.Material) -> bpy.types.Node:
    return next(
        node
        for node in mat.node_tree.nodes
        if node.bl_idname == "ShaderNodeBsdfPrincipled"
    )


def pbr_material(
    name: str,
    family_dir: Path,
    assets: dict[str, str],
    zone: str,
    *,
    alpha_mask: bool = False,
    metallic: float = 0.0,
    transmission: float = 0.0,
    emission_strength: float = 0.0,
    saturation: float = 1.0,
    value: float = 1.0,
) -> bpy.types.Material:
    """Load one registered PBR zone with optional semantic opening alpha."""
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Metallic"].default_value = metallic
    if bsdf.inputs.get("Transmission Weight"):
        bsdf.inputs["Transmission Weight"].default_value = transmission
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    def image_node(channel: str, *, non_color: bool = False) -> bpy.types.Node:
        node = nodes.new("ShaderNodeTexImage")
        node.name = node.label = f"SKIN_{channel.upper()}"
        node.image = bpy.data.images.load(
            str(family_dir / assets[channel]),
            check_existing=True,
        )
        node.extension = "REPEAT"
        if non_color:
            node.image.colorspace_settings.name = "Non-Color"
        return node

    albedo = image_node("albedo")
    grade = nodes.new("ShaderNodeHueSaturation")
    grade.name = grade.label = "REFERENCE_GRADE"
    grade.inputs["Saturation"].default_value = saturation
    grade.inputs["Value"].default_value = value
    links.new(albedo.outputs["Color"], grade.inputs["Color"])
    ao = image_node("ao", non_color=True)
    multiply = nodes.new("ShaderNodeMixRGB")
    multiply.blend_type = "MULTIPLY"
    multiply.inputs[0].default_value = 0.70
    links.new(grade.outputs["Color"], multiply.inputs[1])
    links.new(ao.outputs["Color"], multiply.inputs[2])
    links.new(multiply.outputs["Color"], bsdf.inputs["Base Color"])

    roughness = image_node("roughness", non_color=True)
    links.new(roughness.outputs["Color"], bsdf.inputs["Roughness"])
    normal = image_node("normal", non_color=True)
    normal_map = nodes.new("ShaderNodeNormalMap")
    normal_map.inputs["Strength"].default_value = 0.68
    links.new(normal.outputs["Color"], normal_map.inputs["Color"])
    depth = image_node("depth", non_color=True)
    bump = nodes.new("ShaderNodeBump")
    bump.name = bump.label = "REGISTERED_DEPTH"
    bump.inputs["Strength"].default_value = 0.26
    bump.inputs["Distance"].default_value = 0.065
    links.new(depth.outputs["Color"], bump.inputs["Height"])
    links.new(normal_map.outputs["Normal"], bump.inputs["Normal"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    emissive = image_node("emissive")
    if bsdf.inputs.get("Emission Color"):
        links.new(emissive.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = emission_strength

    if alpha_mask:
        opaque = image_node("opaque_mask", non_color=True)
        if bsdf.inputs.get("Alpha"):
            links.new(opaque.outputs["Color"], bsdf.inputs["Alpha"])
        try:
            mat.surface_render_method = "DITHERED"
        except Exception:
            pass

    mat["skin_zone"] = zone
    mat["pbr_channels"] = json.dumps(
        ["albedo", "normal", "roughness", "ao", "depth", "emissive"]
    )
    mat["semantic_glass_mask"] = assets["glass_mask"]
    mat["semantic_opaque_mask"] = assets["opaque_mask"]
    return mat


def palette(family_dir: Path) -> tuple[dict[str, bpy.types.Material], dict]:
    skin_path = family_dir / "textures" / "skin_manifest.json"
    skin = json.loads(skin_path.read_text(encoding="utf-8"))
    near = {zone: values["near"] for zone, values in skin["zones"].items()}
    mats = {
        "facade": pbr_material(
            "MAT_W4_VictorianFacade",
            family_dir,
            near["facade"],
            "facade",
            alpha_mask=True,
            emission_strength=0.18,
            value=0.94,
        ),
        "podium_skin": pbr_material(
            "MAT_W4_VictorianPodiumSkin",
            family_dir,
            near["podium"],
            "podium",
            alpha_mask=True,
            emission_strength=0.14,
            value=0.93,
        ),
        "floor_a": pbr_material(
            "MAT_W4_VictorianFloorA",
            family_dir,
            near["floor_a"],
            "floor_a",
            alpha_mask=True,
            emission_strength=0.12,
            value=0.94,
        ),
        "floor_b": pbr_material(
            "MAT_W4_VictorianFloorB",
            family_dir,
            near["floor_b"],
            "floor_b",
            alpha_mask=True,
            emission_strength=0.15,
            value=0.95,
        ),
        "floor_c": pbr_material(
            "MAT_W4_VictorianFloorC",
            family_dir,
            near["floor_c"],
            "floor_c",
            alpha_mask=True,
            emission_strength=0.10,
            value=0.93,
        ),
        "crown_skin": pbr_material(
            "MAT_W4_VictorianCrownSkin",
            family_dir,
            near["crown"],
            "crown",
            value=0.95,
        ),
        "side_skin": pbr_material(
            "MAT_W4_VictorianSideSkin",
            family_dir,
            near["side"],
            "side",
            alpha_mask=True,
            emission_strength=0.08,
            saturation=1.08,
            value=0.96,
        ),
        "side_crown_skin": pbr_material(
            "MAT_W4_VictorianSideCrownSkin",
            family_dir,
            near["side_crown"],
            "side_crown",
            saturation=1.05,
            value=0.94,
        ),
        "deck_skin": pbr_material(
            "MAT_W4_VictorianServiceDeckSkin",
            family_dir,
            near["deck"],
            "deck",
            value=0.78,
        ),
        "roof_skin": pbr_material(
            "MAT_W4_VictorianRoofSkin",
            family_dir,
            near["roof"],
            "roof",
            metallic=0.34,
            value=0.88,
        ),
        "brick": material("MAT_W4_RedPressedBrick", (0.39, 0.105, 0.055, 1), 0.88),
        "stone": material("MAT_W4_CreamStone", (0.73, 0.64, 0.47, 1), 0.74),
        "stone_light": material(
            "MAT_W4_CarvedLimestone",
            (0.82, 0.75, 0.60, 1),
            0.68,
        ),
        "green": material(
            "MAT_W4_ForestGreenCastIron",
            (0.035, 0.16, 0.075, 1),
            0.42,
            metallic=0.18,
        ),
        "green_dark": material(
            "MAT_W4_ForestGreenShadow",
            (0.012, 0.055, 0.028, 1),
            0.54,
            metallic=0.10,
        ),
        "roof": material(
            "MAT_W4_RoofEdge",
            (0.33, 0.34, 0.33, 1),
            0.60,
            metallic=0.34,
        ),
        "gravel": material("MAT_W4_ServiceRoofGravel", (0.075, 0.075, 0.070, 1), 0.97),
        "glass": material(
            "MAT_W4_HeritageGlass",
            (0.055, 0.095, 0.085, 0.38),
            0.15,
            metallic=0.02,
        ),
        "glass_alt": material(
            "MAT_W4_HeritageGlassAlt",
            (0.075, 0.10, 0.09, 0.42),
            0.19,
            metallic=0.02,
        ),
        "warm": material(
            "MAT_W4_OccupiedInterior",
            (0.065, 0.026, 0.012, 1),
            0.74,
            emission=(0.80, 0.18, 0.035, 1),
            emission_strength=0.32,
        ),
        "warm_alt": material(
            "MAT_W4_OccupiedInteriorAlt",
            (0.040, 0.018, 0.010, 1),
            0.78,
            emission=(0.62, 0.10, 0.018, 1),
            emission_strength=0.18,
        ),
        "dark": material("MAT_W4_InteriorCavity", (0.018, 0.015, 0.012, 1), 0.88),
        "timber": material("MAT_W4_DarkOakDoor", (0.12, 0.045, 0.022, 1), 0.66),
        "brass": material(
            "MAT_W4_AgedBrass",
            (0.38, 0.22, 0.065, 1),
            0.33,
            metallic=0.68,
        ),
    }
    glass_bsdf = _principled(mats["glass"])
    if glass_bsdf.inputs.get("Transmission Weight"):
        glass_bsdf.inputs["Transmission Weight"].default_value = 0.24
    if glass_bsdf.inputs.get("Coat Weight"):
        glass_bsdf.inputs["Coat Weight"].default_value = 0.22
    alt_bsdf = _principled(mats["glass_alt"])
    if alt_bsdf.inputs.get("Transmission Weight"):
        alt_bsdf.inputs["Transmission Weight"].default_value = 0.18
    return mats, skin


def facade_panel(
    name: str,
    *,
    axis: str,
    centre: tuple[float, float, float],
    span: float,
    height: float,
    mat: bpy.types.Material,
    flip_u: bool = False,
) -> bpy.types.Object:
    """Create one rectified facade plane with deterministic 0..1 UVs."""
    cx, cy, cz = centre
    z0 = cz - height / 2
    z1 = cz + height / 2
    half = span / 2
    if axis == "front":
        vertices = [
            (cx - half, cy, z0),
            (cx + half, cy, z0),
            (cx + half, cy, z1),
            (cx - half, cy, z1),
        ]
    elif axis == "rear":
        vertices = [
            (cx + half, cy, z0),
            (cx - half, cy, z0),
            (cx - half, cy, z1),
            (cx + half, cy, z1),
        ]
    elif axis == "left":
        vertices = [
            (cx, cy + half, z0),
            (cx, cy - half, z0),
            (cx, cy - half, z1),
            (cx, cy + half, z1),
        ]
    elif axis == "right":
        vertices = [
            (cx, cy - half, z0),
            (cx, cy + half, z0),
            (cx, cy + half, z1),
            (cx, cy - half, z1),
        ]
    else:
        raise ValueError(axis)
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(vertices, [], [(0, 1, 2, 3)])
    mesh.materials.append(mat)
    uv = mesh.uv_layers.new(name="UVMap")
    values = ((0, 0), (1, 0), (1, 1), (0, 1))
    if flip_u:
        values = tuple((1 - u, v) for u, v in values)
    for loop_index, value in enumerate(values):
        uv.data[loop_index].uv = value
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def _oriented_box(
    name: str,
    axis: str,
    lateral: float,
    plane: float,
    z: float,
    lateral_size: float,
    depth: float,
    height: float,
    mat: bpy.types.Material,
    bevel: float = 0.0,
) -> bpy.types.Object:
    if axis in {"front", "rear"}:
        return box(
            name,
            (lateral_size, depth, height),
            (lateral, plane, z),
            mat,
            bevel=bevel,
        )
    return box(
        name,
        (depth, lateral_size, height),
        (plane, lateral, z),
        mat,
        bevel=bevel,
    )


def slim_arch_frame(
    name: str,
    *,
    axis: str,
    lateral: float,
    plane: float,
    sill_z: float,
    width: float,
    height: float,
    depth: float,
    rail_radius: float,
    mat: bpy.types.Material,
    include_jambs: bool = True,
) -> list[bpy.types.Object]:
    """Construction-scale arched cap; unlike the legacy helper it is not a cage."""
    objs: list[bpy.types.Object] = []
    radius = width / 2
    spring_z = sill_z + height - radius
    if include_jambs:
        for side in (-1.0, 1.0):
            objs.append(
                _oriented_box(
                    f"{name}_Jamb_{side:+.0f}",
                    axis,
                    lateral + side * radius,
                    plane,
                    sill_z + (height - radius) / 2,
                    rail_radius * 1.75,
                    depth,
                    height - radius,
                    mat,
                    bevel=rail_radius * 0.35,
                )
            )
    if axis in {"front", "rear"}:
        points = [
            (
                lateral + radius * math.cos(math.pi * index / 24),
                plane,
                spring_z + radius * math.sin(math.pi * index / 24),
            )
            for index in range(25)
        ]
    else:
        points = [
            (
                plane,
                lateral + radius * math.cos(math.pi * index / 24),
                spring_z + radius * math.sin(math.pi * index / 24),
            )
            for index in range(25)
        ]
    for index in range(24):
        objs.append(
            beam(
                f"{name}_Arc_{index:02d}",
                points[index],
                points[index + 1],
                rail_radius,
                mat,
            )
        )
    return objs


def heritage_arch_window(
    name: str,
    *,
    axis: str,
    lateral: float,
    plane: float,
    sill_z: float,
    width: float,
    height: float,
    mats: dict[str, bpy.types.Material],
    interior_key: str = "warm",
) -> list[bpy.types.Object]:
    """Layer a recessed occupied pane, sash, return and carved arch surround."""
    objs: list[bpy.types.Object] = []
    outward_sign = -1.0 if axis in {"front", "left"} else 1.0
    if axis == "front":
        pane_plane = plane - outward_sign * 0.08
        room_plane = plane - outward_sign * 0.34
    else:
        # Secondary-elevation skins carry alpha-registered openings over a
        # structural wall.  Keep the cavity and glass between that skin and the
        # projecting sash so the opening reads as carved, never pasted on.
        pane_plane = plane + outward_sign * 0.024
        room_plane = plane + outward_sign * 0.010
    frame_plane = plane + outward_sign * 0.035
    front_axis = "y" if axis in {"front", "rear"} else "x"

    if front_axis == "y":
        pane = arched_panel(
            name + "_Pane",
            lateral,
            pane_plane,
            sill_z,
            width,
            height,
            mats["glass"],
            segments=28,
        )
        room = arched_panel(
            name + "_Room",
            lateral,
            room_plane,
            sill_z + 0.06,
            width * 0.94,
            height * 0.94,
            mats["dark"],
            segments=24,
        )
    else:
        pane = arched_panel(
            name + "_Pane",
            plane,
            lateral,
            sill_z,
            width,
            height,
            mats["glass"],
            segments=28,
            front_axis="x",
        )
        room = arched_panel(
            name + "_Room",
            room_plane,
            lateral,
            sill_z + 0.06,
            width * 0.94,
            height * 0.94,
            mats["dark"],
            segments=24,
            front_axis="x",
        )
    objs.extend([room, pane])
    # The archetype has uniformly dark daytime heritage glazing.  Occupancy is
    # expressed through reflection and transmission rather than orange cards.
    # The atlas owns the carved surround. These narrow caps supply only the
    # grazing-angle return and sash depth, avoiding a second picture frame.
    if axis != "front":
        objs.extend(
            slim_arch_frame(
                name + "_StoneReturn",
                axis=axis,
                lateral=lateral,
                plane=frame_plane,
                sill_z=sill_z,
                width=width + 0.08,
                height=height + 0.06,
                depth=0.09,
                rail_radius=0.035,
                mat=mats["stone"],
            )
        )
    objs.extend(
        slim_arch_frame(
            name + "_GreenSash",
            axis=axis,
            lateral=lateral,
            plane=frame_plane + outward_sign * 0.025,
            sill_z=sill_z + 0.055,
            width=width * 0.92,
            height=height * 0.93,
            depth=0.065,
            rail_radius=0.028,
            mat=mats["green"],
        )
    )
    spring_z = sill_z + height - width / 2
    if front_axis == "y":
        objs.append(
            box(
                name + "_Mullion",
                (0.038, 0.065, height - 0.22),
                (lateral, frame_plane + outward_sign * 0.04, sill_z + height / 2),
                mats["green"],
                bevel=0.018,
            )
        )
        objs.append(
            box(
                name + "_Transom",
                (width * 0.84, 0.065, 0.042),
                (lateral, frame_plane + outward_sign * 0.04, spring_z - 0.35),
                mats["green"],
                bevel=0.015,
            )
        )
        objs.append(
            box(
                name + "_Sill",
                (width + 0.18, 0.17, 0.085),
                (lateral, frame_plane + outward_sign * 0.08, sill_z - 0.06),
                mats["stone_light"],
                bevel=0.035,
            )
        )
    else:
        objs.append(
            box(
                name + "_Mullion",
                (0.065, 0.038, height - 0.22),
                (frame_plane + outward_sign * 0.04, lateral, sill_z + height / 2),
                mats["green"],
                bevel=0.018,
            )
        )
        objs.append(
            box(
                name + "_Transom",
                (0.065, width * 0.84, 0.042),
                (frame_plane + outward_sign * 0.04, lateral, spring_z - 0.35),
                mats["green"],
                bevel=0.015,
            )
        )
        objs.append(
            box(
                name + "_Sill",
                (0.17, width + 0.18, 0.085),
                (frame_plane + outward_sign * 0.08, lateral, sill_z - 0.06),
                mats["stone_light"],
                bevel=0.035,
            )
        )
    return objs


def storefront_door(
    name: str,
    x: float,
    base_z: float,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objs: list[bpy.types.Object] = []
    y = -10.72
    objs.append(
        box(name + "_Cavity", (1.38, 0.10, 3.02), (x, y + 0.14, base_z + 1.62), mats["dark"])
    )
    objs.append(
        box(
            name + "_Leaf",
            (1.12, 0.105, 2.78),
            (x, y - 0.02, base_z + 1.52),
            mats["green_dark"],
            bevel=0.035,
        )
    )
    objs.append(
        box(
            name + "_UpperGlass",
            (0.76, 0.055, 1.10),
            (x, y - 0.09, base_z + 2.05),
            mats["glass_alt"],
            bevel=0.02,
        )
    )
    for z in (base_z + 0.47, base_z + 0.93):
        objs.append(
            box(
                f"{name}_Panel_{z:.2f}",
                (0.78, 0.07, 0.30),
                (x, y - 0.10, z),
                mats["green"],
                bevel=0.025,
            )
        )
    for side in (-0.48, 0.48):
        objs.append(
            box(
                f"{name}_Jamb_{side:+.2f}",
                (0.10, 0.16, 2.88),
                (x + side, y - 0.10, base_z + 1.55),
                mats["green"],
                bevel=0.025,
            )
        )
    objs.append(
        cylinder(
            name + "_Handle",
            0.035,
            0.18,
            (x + 0.30, y - 0.18, base_z + 1.43),
            mats["brass"],
            vertices=16,
        )
    )
    objs[-1].rotation_euler.x = math.radians(90)
    objs.append(
        box(
            name + "_Threshold",
            (1.45, 0.74, 0.10),
            (x, -11.02, base_z + 0.05),
            mats["stone_light"],
            bevel=0.025,
        )
    )
    return objs


def build_storefront(
    mats: dict[str, bpy.types.Material],
    *,
    base_z: float = 0.0,
    band_skin: bool = False,
) -> list[bpy.types.Object]:
    objs: list[bpy.types.Object] = []
    if band_skin:
        objs.append(
            facade_panel(
                "VictorianPodiumRegisteredSkin",
                axis="front",
                centre=(0, -10.83, base_z + CONFIG["podium_height_m"] / 2),
                span=15.0,
                height=CONFIG["podium_height_m"],
                mat=mats["podium_skin"],
            )
        )
    objs.append(
        box(
            "VictorianStorefrontShadowBack",
            (14.35, 0.12, 3.48),
            (0, -10.54, base_z + 1.84),
            mats["dark"],
        )
    )
    display_centres = (-6.05, -4.72, -1.94, -0.68, 0.68, 1.94, 4.72, 6.05)
    for index, x in enumerate(display_centres):
        room = mats["warm"] if index % 3 else mats["warm_alt"]
        objs.append(
            box(
                f"VictorianDisplayRoom_{index:02d}",
                (1.03, 0.06, 2.62),
                (x, -10.47, base_z + 1.70),
                room,
            )
        )
        objs.append(
            box(
                f"VictorianDisplayGlass_{index:02d}",
                (1.08, 0.055, 2.68),
                (x, -10.74, base_z + 1.72),
                mats["glass"] if index % 2 else mats["glass_alt"],
                bevel=0.018,
            )
        )
        objs.append(
            box(
                f"VictorianDisplayTransom_{index:02d}",
                (1.08, 0.10, 0.065),
                (x, -10.91, base_z + 2.82),
                mats["green"],
                bevel=0.015,
            )
        )
    for x in (-7.13, 0.0, 7.13):
        objs.append(
            box(
                f"VictorianStorefrontMainPilaster_{x:+.2f}",
                (0.40, 0.38, 3.72),
                (x, -10.94, base_z + 1.92),
                mats["green"],
                bevel=0.045,
            )
        )
        objs.append(
            box(
                f"VictorianStorefrontPilasterPanel_{x:+.2f}",
                (0.23, 0.06, 1.35),
                (x, -11.16, base_z + 1.48),
                mats["green_dark"],
                bevel=0.025,
            )
        )
        objs.append(
            box(
                f"VictorianStorefrontCapital_{x:+.2f}",
                (0.62, 0.48, 0.22),
                (x, -10.98, base_z + 3.66),
                mats["green"],
                bevel=0.035,
            )
        )
    for x in (-4.10, -1.90, 1.90, 4.10):
        objs.append(
            box(
                f"VictorianStorefrontColonnette_{x:+.2f}",
                (0.115, 0.20, 2.74),
                (x, -10.96, base_z + 1.70),
                mats["green"],
                bevel=0.025,
            )
        )
        objs.append(
            cylinder(
                f"VictorianStorefrontColumnCapital_{x:+.2f}",
                0.12,
                0.16,
                (x, -11.00, base_z + 3.03),
                mats["green"],
                vertices=20,
            )
        )
    objs.extend(storefront_door("VictorianDoorLeft", -3.15, base_z, mats))
    objs.extend(storefront_door("VictorianDoorRight", 3.00, base_z, mats))

    # The registered podium skin owns the fine pressed-metal lace.  Physical
    # duplication here reads as a fan-shaped prop at oblique angles.
    objs.append(
        box(
            "VictorianStorefrontFrieze",
            (14.90, 0.46, 0.58),
            (0, -10.95, base_z + 3.70),
            mats["green"],
            bevel=0.045,
        )
    )
    objs.append(
        box(
            "VictorianStorefrontFriezeInset",
            (13.85, 0.08, 0.27),
            (0, -11.20, base_z + 3.72),
            mats["green_dark"],
            bevel=0.025,
        )
    )
    for index, x in enumerate(
        -7.0 + index * (14.0 / 15.0) for index in range(16)
    ):
        objs.append(
            box(
                f"VictorianStorefrontBracket_{index:02d}",
                (0.22, 0.34, 0.24),
                (x, -11.03, base_z + 3.98),
                mats["green"],
                bevel=0.03,
            )
        )
    objs.append(
        box(
            "VictorianStorefrontPlinth",
            (14.85, 0.42, 0.24),
            (0, -10.95, base_z + 0.12),
            mats["green"],
            bevel=0.035,
        )
    )
    return objs


UPPER_WINDOWS = (
    (-5.53, 1.29),
    (-3.81, 1.21),
    (-1.92, 1.17),
    (1.56, 1.17),
    (3.67, 1.17),
    (5.31, 1.17),
)


def build_upper_front(
    mats: dict[str, bpy.types.Material],
    *,
    base_z: float,
    skin_key: str | None,
    interior_pattern: tuple[str, ...] = ("warm", "warm_alt"),
) -> list[bpy.types.Object]:
    objs: list[bpy.types.Object] = []
    if skin_key:
        objs.append(
            facade_panel(
                "VictorianUpperRegisteredSkin_" + skin_key,
                axis="front",
                centre=(0, -10.83, base_z + CONFIG["floor_height_m"] / 2),
                span=15.0,
                height=CONFIG["floor_height_m"],
                mat=mats[skin_key],
            )
        )
    canonical_registration = skin_key is None
    sill = base_z + (1.20 if canonical_registration else 0.50)
    opening_height = 2.28 if canonical_registration else 2.42
    for index, (x, opening_width) in enumerate(UPPER_WINDOWS):
        objs.extend(
            heritage_arch_window(
                f"VictorianUpperWindow_{base_z:.2f}_{index}",
                axis="front",
                lateral=x,
                plane=-10.84,
                sill_z=sill,
                width=opening_width,
                height=opening_height,
                mats=mats,
                interior_key=interior_pattern[index % len(interior_pattern)],
            )
        )

    # The registered skin already owns the polychrome courses. Do not draw a
    # second ladder of pale bands over those pixels.
    return objs


def build_crown_front(
    mats: dict[str, bpy.types.Material],
    *,
    base_z: float,
    band_skin: bool,
) -> list[bpy.types.Object]:
    objs: list[bpy.types.Object] = []
    height = CONFIG["crown_height_m"]
    if band_skin:
        objs.append(
            facade_panel(
                "VictorianCrownRegisteredSkin",
                axis="front",
                centre=(0, -10.84, base_z + height / 2),
                span=15.0,
                height=height,
                mat=mats["crown_skin"],
            )
        )
    # The registered crown crop carries the floral frieze, dentils and recessed
    # parapet panels. Only the silhouette-bearing cornice/cap projects here.
    objs.extend(
        [
            box(
                "VictorianCorniceUpper",
                (14.98, 0.24, 0.09),
                (0, -10.96, base_z + 0.81),
                mats["stone_light"],
                bevel=0.035,
            ),
        ]
    )
    objs.append(
        box(
            "VictorianParapetCap",
            (14.98, 0.38, 0.16),
            (0, -10.98, base_z + 1.38),
            mats["stone_light"],
            bevel=0.03,
        )
    )
    return objs


def build_side_and_rear(
    mats: dict[str, bpy.types.Material],
    *,
    base_z: float,
    height: float,
    upper: bool,
    variant_index: int = 0,
) -> list[bpy.types.Object]:
    objs: list[bpy.types.Object] = []
    centre_z = base_z + height / 2
    objs.extend(
        [
            box(
                f"VictorianLeftWall_{base_z:.2f}",
                (0.30, 21.40, height),
                (-7.15, 0, centre_z),
                mats["brick"],
                bevel=0.035,
            ),
            box(
                f"VictorianRightWall_{base_z:.2f}",
                (0.30, 21.40, height),
                (7.15, 0, centre_z),
                mats["brick"],
                bevel=0.035,
            ),
            box(
                f"VictorianRearWall_{base_z:.2f}",
                (14.30, 0.30, height),
                (0, 10.70, centre_z),
                mats["brick"],
                bevel=0.035,
            ),
        ]
    )
    # Wrap a purpose-authored long side elevation around each LEGO storey.  Its
    # brick scale, cream datums and alpha openings come from the selected
    # angled reference rather than a stretched crop of the ceremonial front.
    for side, x, flip in (("left", -7.31, True), ("right", 7.31, False)):
        objs.append(
            facade_panel(
                f"Victorian{side.title()}PolychromeSkin_{base_z:.2f}",
                axis=side,
                centre=(x, 0.0, centre_z),
                span=21.40,
                height=height,
                mat=mats["side_skin"],
                flip_u=flip,
            )
        )

    if upper:
        side_centres = (-6.20, -0.50, 5.20)
        for side, x in (("left", -7.31), ("right", 7.31)):
            for bay_index, y in enumerate(side_centres):
                objs.extend(
                    heritage_arch_window(
                        f"Victorian{side.title()}Window_{base_z:.2f}_{bay_index}",
                        axis=side,
                        lateral=y,
                        plane=x,
                        sill_z=base_z + 0.50,
                        width=1.20,
                        height=min(2.24, height - 0.75),
                        mats=mats,
                        interior_key="warm" if (bay_index + variant_index) % 2 else "warm_alt",
                    )
                )
        rear_positions = (-5.20, -1.75, 1.75, 5.20)
        for index, x in enumerate(rear_positions):
            objs.extend(
                heritage_arch_window(
                    f"VictorianRearWindow_{base_z:.2f}_{index}",
                    axis="rear",
                    lateral=x,
                    plane=10.87,
                    sill_z=base_z + 0.50,
                    width=1.18,
                    height=min(2.22, height - 0.75),
                    mats=mats,
                    interior_key="warm_alt" if (index + variant_index) % 3 == 0 else "warm",
                )
            )
        rear_solid_intervals = (
            (-7.05, -5.95),
            (-4.45, -2.50),
            (-1.00, 1.00),
            (2.50, 4.45),
            (5.95, 7.05),
        )
        for level_index, z in enumerate(
            (base_z + 0.80, base_z + 1.48, base_z + 2.16, base_z + 2.84)
        ):
            for span_index, (start, end) in enumerate(rear_solid_intervals):
                objs.append(
                    box(
                        f"VictorianRearCourse_{level_index}_{span_index}",
                        (end - start, 0.08, 0.10),
                        ((start + end) / 2, 10.88, z),
                        mats["stone"],
                        bevel=0.012,
                    )
                )
    else:
        # The side skin has the same three registered openings at ground level;
        # physical sash depth keeps the repeatable module convincing in orbit.
        for side, x in (("left", -7.31), ("right", 7.31)):
            for index, y in enumerate((-6.20, -0.50, 5.20)):
                objs.extend(
                    heritage_arch_window(
                        f"Victorian{side.title()}GroundWindow_{index}",
                        axis=side,
                        lateral=y,
                        plane=x,
                        sill_z=base_z + 0.48,
                        width=1.20,
                        height=2.48,
                        mats=mats,
                        interior_key="warm_alt",
                    )
                )
        objs.append(
            box(
                "VictorianRearServiceDoor",
                (1.55, 0.12, 2.55),
                (-3.8, 10.90, base_z + 1.42),
                mats["green_dark"],
                bevel=0.035,
            )
        )
        for index, x in enumerate((0.0, 3.9)):
            objs.append(
                box(
                    f"VictorianRearGroundWindow_{index}",
                    (1.45, 0.10, 1.65),
                    (x, 10.90, base_z + 1.68),
                    mats["glass_alt"],
                    bevel=0.025,
                )
            )
    return objs


def build_crown_envelope(
    mats: dict[str, bpy.types.Material],
    *,
    base_z: float,
) -> list[bpy.types.Object]:
    height = CONFIG["crown_height_m"]
    objs = [
        box(
            "VictorianLeftParapet",
            (0.38, 21.45, height),
            (-7.18, 0, base_z + height / 2),
            mats["brick"],
            bevel=0.035,
        ),
        box(
            "VictorianRightParapet",
            (0.38, 21.45, height),
            (7.18, 0, base_z + height / 2),
            mats["brick"],
            bevel=0.035,
        ),
        box(
            "VictorianRearParapet",
            (14.35, 0.38, height),
            (0, 10.72, base_z + height / 2),
            mats["brick"],
            bevel=0.035,
        ),
    ]
    for side, x, flip in (("left", -7.385, True), ("right", 7.385, False)):
        objs.append(
            facade_panel(
                f"Victorian{side.title()}PressedBrickParapet",
                axis=side,
                centre=(x, 0.0, base_z + height / 2),
                span=21.45,
                height=height,
                mat=mats["side_crown_skin"],
                flip_u=flip,
            )
        )
    return objs


def perimeter_hip_roof(
    name: str,
    width: float,
    depth: float,
    eave_z: float,
    plateau_z: float,
    inner_centre: tuple[float, float],
    inner_size: tuple[float, float],
    mat: bpy.types.Material,
) -> bpy.types.Object:
    half_w = width / 2
    half_d = depth / 2
    inner_x, inner_y = inner_centre
    inner_half_w = inner_size[0] / 2
    inner_half_d = inner_size[1] / 2
    vertices = [
        (-half_w, -half_d, eave_z),
        (half_w, -half_d, eave_z),
        (half_w, half_d, eave_z),
        (-half_w, half_d, eave_z),
        (inner_x - inner_half_w, inner_y - inner_half_d, plateau_z),
        (inner_x + inner_half_w, inner_y - inner_half_d, plateau_z),
        (inner_x + inner_half_w, inner_y + inner_half_d, plateau_z),
        (inner_x - inner_half_w, inner_y + inner_half_d, plateau_z),
    ]
    faces = [
        (0, 1, 5, 4),
        (1, 2, 6, 5),
        (2, 3, 7, 6),
        (3, 0, 4, 7),
    ]
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(mat)
    uv = mesh.uv_layers.new(name="UVMap")
    for polygon in mesh.polygons:
        for loop_index in polygon.loop_indices:
            co = mesh.vertices[mesh.loops[loop_index].vertex_index].co
            uv.data[loop_index].uv = (
                (co.x + half_w) / width,
                (co.y + half_d) / depth,
            )
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def build_roof(
    mats: dict[str, bpy.types.Material],
    *,
    base_z: float,
) -> list[bpy.types.Object]:
    objs: list[bpy.types.Object] = []
    width = 14.15
    depth = 20.55
    eave_z = base_z + 0.08
    plateau_z = base_z + 1.04
    # The 90-degree goalpost shows a large, rear-biased plant deck rather than
    # a token central square.  Its offset also creates the unequal hip widths
    # visible on the two long sides.
    inner_centre = (1.25, 2.25)
    inner_size = (8.00, 8.50)
    inner_left = inner_centre[0] - inner_size[0] / 2
    inner_right = inner_centre[0] + inner_size[0] / 2
    inner_front = inner_centre[1] - inner_size[1] / 2
    inner_rear = inner_centre[1] + inner_size[1] / 2
    objs.append(
        perimeter_hip_roof(
            "VictorianCorrugatedPerimeterHipRoof",
            width,
            depth,
            eave_z,
            plateau_z,
            inner_centre,
            inner_size,
            mats["roof_skin"],
        )
    )
    # Register corrugation as construction-scale ribs terminating at the flat
    # service roof, rather than crossing through a slab laid on top of a hip.
    for index, x in enumerate(-6.35 + i * 0.96 for i in range(14)):
        # Distribute outer seams continuously along the inner edge. Clamping
        # several ribs to one corner creates a false sunburst.
        plateau_x = inner_left + ((x + width / 2) / width) * inner_size[0]
        if abs(x + 2.30) >= 0.90:
            objs.append(
                beam(
                    f"VictorianFrontRoofSeam_{index:02d}",
                    (x, -depth / 2 + 0.06, eave_z + 0.025),
                    (plateau_x, inner_front, plateau_z + 0.025),
                    0.012,
                    mats["roof"],
                )
            )
        objs.append(
            beam(
                f"VictorianRearRoofSeam_{index:02d}",
                (x, depth / 2 - 0.06, eave_z + 0.025),
                (plateau_x, inner_rear, plateau_z + 0.025),
                0.012,
                mats["roof"],
            )
        )
    # Side-slope corrugation stays in the registered normal/depth skin. A
    # second set of crossing physical ribs would form a false roof lattice and
    # cut through the front skylight.
    objs.append(
        box(
            "VictorianServiceRoofDeck",
            (inner_size[0], inner_size[1], 0.16),
            (inner_centre[0], inner_centre[1], plateau_z - 0.08),
            mats["deck_skin"],
            bevel=0.025,
        )
    )
    for index, (x, y, sx, sy, curb_z, glass_z) in enumerate(
        (
            (-2.3, -3.55, 1.45, 2.05, 0.82, 0.95),
            (2.55, 3.15, 1.15, 1.65, 1.18, 1.31),
        )
    ):
        objs.append(
            box(
                f"VictorianSkylightCurb_{index}",
                (sx + 0.18, sy + 0.18, 0.20),
                (x, y, base_z + curb_z),
                mats["roof"],
                bevel=0.035,
            )
        )
        objs.append(
            box(
                f"VictorianSkylightGlass_{index}",
                (sx, sy, 0.10),
                (x, y, base_z + glass_z),
                mats["glass"],
                bevel=0.035,
            )
        )
    objs.append(
        box(
            "VictorianBrickChimney",
            (0.95, 0.95, 1.72),
            (-5.30, 4.65, base_z + 1.45),
            mats["brick"],
            bevel=0.035,
        )
    )
    objs.extend(
        [
            box(
                "VictorianChimneyStoneBand",
                (1.04, 1.04, 0.16),
                (-5.30, 4.65, base_z + 2.08),
                mats["stone"],
                bevel=0.025,
            ),
            box(
                "VictorianChimneyCap",
                (1.18, 1.18, 0.18),
                (-5.30, 4.65, base_z + 2.31),
                mats["stone_light"],
                bevel=0.025,
            ),
        ]
    )
    for index, (x, y) in enumerate(((3.55, 4.3), (1.05, 1.4))):
        objs.append(
            cylinder(
                f"VictorianRoofVent_{index}",
                0.20 if index else 0.28,
                0.62 if index else 0.78,
                (x, y, base_z + 1.50),
                mats["roof"],
                vertices=24,
            )
        )
        objs.append(
            cylinder(
                f"VictorianRoofVentCap_{index}",
                0.30 if index else 0.38,
                0.10,
                (x, y, base_z + 1.93),
                mats["roof"],
                vertices=24,
            )
        )
    return objs


def build_podium_module(
    mats: dict[str, bpy.types.Material],
    *,
    base_z: float = 0.0,
) -> list[bpy.types.Object]:
    height = CONFIG["podium_height_m"]
    objs = build_storefront(mats, base_z=base_z, band_skin=True)
    objs.extend(build_side_and_rear(mats, base_z=base_z, height=height, upper=False))
    objs.append(
        box(
            "VictorianPodiumFloorSlab",
            (14.35, 21.35, 0.18),
            (0, 0, base_z + 0.09),
            mats["brick"],
        )
    )
    objs.append(
        box(
            "VictorianPodiumCeilingSlab",
            (14.35, 21.35, 0.16),
            (0, 0, base_z + height - 0.08),
            mats["brick"],
        )
    )
    return objs


def build_floor_module(
    mats: dict[str, bpy.types.Material],
    variant: str,
    *,
    base_z: float = 0.0,
    setback: bool = False,
) -> list[bpy.types.Object]:
    height = CONFIG["floor_height_m"]
    skin_key = {
        "typical_a": "floor_a",
        "typical_b": "floor_b",
        "typical_c": "floor_c",
        "setback_upper": "floor_c",
    }[variant]
    pattern = {
        "typical_a": ("warm", "warm_alt", "warm"),
        "typical_b": ("warm_alt", "warm", "warm"),
        "typical_c": ("warm", "warm", "warm_alt"),
        "setback_upper": ("warm_alt", "warm", "warm_alt"),
    }[variant]
    objs = build_upper_front(
        mats,
        base_z=base_z,
        skin_key=skin_key,
        interior_pattern=pattern,
    )
    objs.extend(
        build_side_and_rear(
            mats,
            base_z=base_z,
            height=height,
            upper=True,
            variant_index=("typical_a", "typical_b", "typical_c", "setback_upper").index(
                variant
            ),
        )
    )
    objs.append(
        box(
            f"VictorianFloorSlab_{variant}",
            ((13.7 if setback else 14.35), (20.5 if setback else 21.35), 0.16),
            (0, 0.35 if setback else 0, base_z + 0.08),
            mats["brick"],
        )
    )
    return objs


def build_crown_module(
    mats: dict[str, bpy.types.Material],
    *,
    base_z: float = 0.0,
) -> list[bpy.types.Object]:
    objs = build_crown_front(mats, base_z=base_z, band_skin=True)
    objs.extend(build_crown_envelope(mats, base_z=base_z))
    return objs


def build_canonical(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    """Build the exact two-storey selected variant from all reference views."""
    podium_h = CONFIG["podium_height_m"]
    floor_h = CONFIG["floor_height_m"]
    crown_base = podium_h + floor_h
    roof_base = crown_base + CONFIG["crown_height_m"]
    objs: list[bpy.types.Object] = [
        facade_panel(
            "VictorianFullRenderLockedFacade",
            axis="front",
            centre=(0, -10.83, 4.94),
            span=15.0,
            height=9.88,
            mat=mats["facade"],
        )
    ]
    objs.extend(build_storefront(mats, base_z=0.0, band_skin=False))
    objs.extend(
        build_upper_front(
            mats,
            base_z=podium_h,
            skin_key=None,
            interior_pattern=("warm", "warm_alt", "warm"),
        )
    )
    objs.extend(build_crown_front(mats, base_z=crown_base, band_skin=False))
    objs.extend(build_side_and_rear(mats, base_z=0.0, height=podium_h, upper=False))
    objs.extend(
        build_side_and_rear(
            mats,
            base_z=podium_h,
            height=floor_h,
            upper=True,
        )
    )
    objs.extend(build_crown_envelope(mats, base_z=crown_base))
    objs.extend(build_roof(mats, base_z=roof_base))
    return objs


def material_count(objects: list[bpy.types.Object]) -> int:
    return len(
        {
            material_slot.material.name
            for obj in objects
            if obj.type == "MESH"
            for material_slot in obj.material_slots
            if material_slot.material is not None
        }
    )


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
        "allowed_levels": [],
        "filename": filename,
        "module_family": FAMILY,
        "width_m": CONFIG["dimensions"][0],
        "depth_m": CONFIG["dimensions"][1],
        "height_m": height,
        "floor_height_m": CONFIG["floor_height_m"],
        "repeatable_z": repeatable,
        "allow_inset_footprint": True,
        "triangle_count": triangle_count(objects),
        "material_count": material_count(objects),
        "texture_keys": sorted(skin["zones"]),
        "ao_baked": True,
        "size_bytes": size_bytes,
    }


def texture_inventory(skin: dict) -> list[dict]:
    inventory: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    for zone, lods in skin["zones"].items():
        for lod, channels in lods.items():
            for channel, path in channels.items():
                key = (lod, channel, path)
                if key in seen:
                    continue
                seen.add(key)
                inventory.append(
                    {
                        "key": f"{zone}_{lod}_{channel}",
                        "path": path,
                        "lod": lod,
                        "channel": channel,
                        "zone": zone,
                    }
                )
    return inventory


def footprint_contract() -> dict:
    return {
        "preferredProfiles": ["rectangle", "l_shape", "u_shape"],
        "minimumPreferredProfiles": 3,
        "profileRationale": (
            "The fixed public storefront occupies the first streetwall segment; "
            "ordinary upper sash/display bays and quiet secondary elevations may "
            "continue around an L or U without changing floor or cornice datums."
        ),
        "recommendedWidth_m": [8, 30],
        "recommendedDepth_m": [14, 30],
        "recommendedFloors": [2, 4],
        "wingDepth_m": [7, 11],
        "preferredBayMultiple_m": 2.10,
        "minimumCourtyard_m": 8,
        "profiles": {
            "rectangle": {
                "recommendedWidth_m": [8, 30],
                "recommendedDepth_m": [14, 27],
                "recommendedFloors": [2, 4],
            },
            "l_shape": {
                "recommendedWidth_m": [16, 36],
                "recommendedDepth_m": [16, 34],
                "recommendedFloors": [2, 4],
                "wingDepth_m": [7, 11],
            },
            "u_shape": {
                "recommendedWidth_m": [24, 44],
                "recommendedDepth_m": [18, 36],
                "recommendedFloors": [2, 4],
                "wingDepth_m": [7, 11],
                "minimumCourtyard_m": 8,
            },
        },
        "notes": [
            "Keep the two recessed storefront entries, end piers and panelled parapet fixed.",
            "Vary width in whole 2.10 metre bays and height in whole 3.60 metre upper floors.",
            "Use authored secondary-elevation bands on returns; never wrap the public entrance atlas.",
        ],
    }


def facade_contract(skin: dict) -> dict:
    return {
        "schema": "facade-sheet@5",
        "source_directory": f"/families/{FAMILY}",
        "model": "gpt-image-2",
        "style_reference": "elevation.jpg",
        "goalpost_reference": (
            "/archetypes/buildings/historical_brick_main_street/variant_0.png"
        ),
        "goalpost_policy": (
            "The selected Victorian Polychrome images control the exact two-storey "
            "height, six upper arches, two storefront entries, roof orientation and "
            "red/cream/forest-green material hierarchy."
        ),
        "runtime_material_profile": "pbr_physical_glazing_v2",
        "geometry_detail_profile": "hero",
        "pbr_channels": ["albedo", "normal", "roughness", "ao", "depth", "emissive"],
        "shadow_neutral": {
            "enabled": True,
            "method": "render-locked orthographic source and deterministic PBR derivation",
            "lighting_authority": "City Prompt environment and sun",
        },
        "bay_strategy": {
            "fixed_end_bays": [0, 6],
            "repeatable_middle_bays": [1, 2, 3, 4, 5],
            "middle_variants": ["typical_a", "typical_b", "typical_c"],
            "preferred_bay_multiple_m": 2.10,
            "rule": (
                "the double storefront, end piers and parapet terminals stay fixed; "
                "only ordinary upper sash and display bays repeat"
            ),
        },
        "delivery": {
            "near_atlas_width_px": 2048,
            "far_atlas_width_px": 1024,
            "near_usage": "close-range registered skin and physical glazing",
            "far_usage": "city-scale baked facade bands",
            "container": "PNG sources embedded into delivery GLBs; KTX2/UASTC at runtime packaging",
        },
        "assembly_contract": {
            "fixed": [
                "podium/entrance",
                "corner returns",
                "crown",
                "roof",
            ],
            "repeatable": ["typical_a", "typical_b", "typical_c"],
            "side_elevations": (
                "front, left, right, rear and roof are authored as related but "
                "different elevations; the ceremonial storefront never wraps"
            ),
            "elevation_coverage": {
                "front": "registered full elevation with physical storefront and six sashes",
                "left": "three occupied secondary bays over a quiet service base",
                "right": "three occupied secondary bays over a quiet service base",
                "rear": "four upper sashes, service door and restrained ground windows",
                "roof": "corrugated hip, service deck, skylights, chimney and vents",
            },
            "abutting_policy": "author every elevation; site geometry alone controls occlusion",
        },
        "assets": {
            "skin_manifest": "textures/skin_manifest.json",
            "source": skin["source"],
            "near": skin["atlases"]["near"],
            "far": skin["atlases"]["far"],
            "semantic_masks": {
                "glass_mask": skin["atlases"]["near"]["glass_mask"],
                "opaque_mask": skin["atlases"]["near"]["opaque_mask"],
            },
        },
        "reference_registration": skin["reference_registration"],
    }


def source_provenance() -> dict:
    return {
        "kind": "reviewed_render_locked_elevation_plus_authored_modular_geometry",
        "catalogue_archetype_id": CONFIG["archetype_id"],
        "catalogue_variant_id": CONFIG["variant_id"],
        "goalpost": "/archetypes/buildings/historical_brick_main_street/variant_0.png",
        "goalpost_local_source": "textures/source/archetype-goalpost.png",
        "angle_reference": "textures/source/angle-reference-60.jpg",
        "roof_reference": "textures/source/angle-reference-90.jpg",
        "orthographic_elevation": "textures/source/elevation-source.jpg",
        "registered_openings": "textures/source/registered-openings.json",
        "registered_bands": "textures/source/registered-bands.json",
        "skin_manifest": "textures/skin_manifest.json",
        "generator": "tools/archetype_compiler/generate_wave4_standard_families.py",
    }


def setup_standard_render() -> None:
    setup_render()
    scene = bpy.context.scene
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.view_settings.exposure = 0.72
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.23, 0.34, 0.46, 1)
    background.inputs["Strength"].default_value = 0.56
    ground = bpy.data.materials.get("MAT_W3_Ground")
    if ground:
        _principled(ground).inputs["Base Color"].default_value = (0.42, 0.39, 0.34, 1)
    bpy.ops.object.light_add(
        type="SUN",
        location=(-30, -40, 55),
        rotation=(math.radians(28), math.radians(-18), math.radians(-38)),
    )
    sun = bpy.context.object
    sun.name = "PRESENTATION_Wave4Sun"
    sun.data.color = (1.0, 0.78, 0.58)
    sun.data.energy = 2.15
    sun.data.angle = math.radians(8)
    key = bpy.data.objects.get("PRESENTATION_Key")
    if key:
        key.data.color = (1.0, 0.80, 0.63)
        key.data.energy = 6200
    fill = bpy.data.objects.get("PRESENTATION_Fill")
    if fill:
        fill.data.color = (0.70, 0.82, 1.0)
        fill.data.energy = 2100


def render_views(
    family_dir: Path,
    *,
    selected_roles: set[str] | None = None,
) -> list[str]:
    setup_standard_render()
    height = CONFIG["dimensions"][2]
    views = {
        "preview": ((10.0, -34.0, 8.0), (0, -0.8, 4.55), 54),
        "front_corner_oblique": ((14.5, -31.0, 9.7), (0, -0.5, 4.50), 54),
        "rear_corner_oblique": ((-15.0, 30.5, 11.5), (0, 0.5, 4.65), 54),
        "facade_close": ((0, -28.5, 5.1), (0, -1.2, 4.85), 62),
        "street": ((-7.0, -27.0, 2.15), (0, -1.5, 3.55), 50),
        "aerial": ((15.5, -23.5, 28.0), (0, 0.5, 3.20), 52),
        "context": ((18.0, -37.0, 13.0), (0, 0.0, 4.25), 58),
    }
    outputs: list[str] = []
    for role, (location, target, lens) in views.items():
        if selected_roles is not None and role not in selected_roles:
            continue
        aim_camera(location, target, lens)
        filename = f"{FAMILY}_{role}.png"
        bpy.context.scene.render.filepath = str(family_dir / filename)
        bpy.ops.render.render(write_still=True)
        outputs.append(filename)
    return outputs


def build_family(
    output_root: Path,
    view_set: str,
    skip_renders: bool,
    skip_modules: bool = False,
) -> None:
    clear_scene()
    family_dir = output_root / FAMILY
    family_dir.mkdir(parents=True, exist_ok=True)
    mats, skin = palette(family_dir)
    canonical = build_canonical(mats)
    assembled_path = family_dir / f"{FAMILY}_assembled.glb"
    export_glb(assembled_path, canonical)
    assembled_tris = triangle_count(canonical)
    assembled_materials = material_count(canonical)

    if skip_renders:
        renders = sorted(path.name for path in family_dir.glob(f"{FAMILY}_*.png"))
    else:
        selected = None
        if view_set == "pilot":
            selected = {"preview", "front_corner_oblique", "facade_close", "aerial"}
        renders = render_views(family_dir, selected_roles=selected)
        delete_objects(
            [
                obj
                for obj in list(bpy.data.objects)
                if obj.name.startswith("PRESENTATION_")
            ]
        )
    if "elevation.jpg" not in renders:
        renders.append("elevation.jpg")
    if skip_modules:
        print(
            f"[wave4-standard-pilot] {FAMILY}: {assembled_tris:,} tris, "
            f"{len(renders)} renders",
            flush=True,
        )
        return
    delete_objects(canonical)

    role_specs = (
        ("podium", "default", CONFIG["podium_height_m"]),
        ("floor", "typical_a", CONFIG["floor_height_m"]),
        ("floor", "typical_b", CONFIG["floor_height_m"]),
        ("floor", "typical_c", CONFIG["floor_height_m"]),
        ("setback", "setback_upper", CONFIG["floor_height_m"]),
        ("crown", "crown", CONFIG["crown_height_m"]),
        ("roof", "default", CONFIG["roof_height_m"]),
    )
    modules: list[dict] = []
    for role, variant, module_height in role_specs:
        if role == "podium":
            objects = build_podium_module(mats)
        elif role == "floor":
            objects = build_floor_module(mats, variant)
        elif role == "setback":
            objects = build_floor_module(mats, variant, setback=True)
        elif role == "crown":
            objects = build_crown_module(mats)
        else:
            objects = build_roof(mats, base_z=0.0)
        objects.extend(module_contract_markers(role, variant, module_height))
        filename = (
            f"{FAMILY}_{role}.glb"
            if variant == "default"
            else f"{FAMILY}_{role}_{variant}.glb"
        )
        destination = family_dir / filename
        export_glb(destination, objects)
        modules.append(
            module_payload(
                role,
                variant,
                filename,
                module_height,
                objects,
                destination.stat().st_size,
                skin,
            )
        )
        delete_objects(objects)

    podium_h = CONFIG["podium_height_m"]
    floor_h = CONFIG["floor_height_m"]
    crown_h = CONFIG["crown_height_m"]
    roof_h = CONFIG["roof_height_m"]
    width, depth, height = CONFIG["dimensions"]
    footprint = footprint_contract()
    provenance = source_provenance()
    assembled = {
        "filename": assembled_path.name,
        "floors": 2,
        "uses_setback": False,
        "uses_crown": True,
        "height_m": height,
        "triangle_count": assembled_tris,
        "material_count": assembled_materials,
        "stack": [
            {
                "role": "podium",
                "variant_key": "default",
                "level": 0,
                "z_m": 0.0,
                "height_m": podium_h,
            },
            {
                "role": "floor",
                "variant_key": "typical_a",
                "level": 1,
                "z_m": podium_h,
                "height_m": floor_h,
            },
            {
                "role": "crown",
                "variant_key": "crown",
                "level": 2,
                "z_m": podium_h + floor_h,
                "height_m": crown_h,
            },
            {
                "role": "roof",
                "variant_key": "default",
                "level": 3,
                "z_m": podium_h + floor_h + crown_h,
                "height_m": roof_h,
            },
        ],
        "footprint_profile": "rectangle",
        "footprint_target": {
            "width_m": width,
            "depth_m": depth,
            "wing_depth_m": depth,
            "segments": [
                {
                    "id": "main",
                    "centre_x_m": 0.0,
                    "centre_y_m": 0.0,
                    "length_m": width,
                    "thickness_m": depth,
                    "rotation_degrees": 0.0,
                }
            ],
        },
        "massing_graph": {
            "type": "modular_streetwall",
            "profile": "victorian_polychrome_main_street_v2",
        },
        "texture_keys": sorted(skin["zones"]),
        "ao_baked": True,
    }
    manifest = {
        "manifest_schema": 3,
        "grammar_schema_version": 3,
        "generator": {
            "name": "archetype_compiler/generate_wave4_standard_families.py",
            "version": "1.0.0",
            "blender_version": bpy.app.version_string,
            "render_engine": "BLENDER_EEVEE",
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "family": FAMILY,
        "archetype_id": CONFIG["archetype_id"],
        "archetype_label": CONFIG["label"],
        "variant_id": CONFIG["variant_id"],
        "generation_archetype_id": CONFIG["generation_archetype_id"],
        "archetype_aliases": CONFIG["aliases"],
        "aesthetic_category_id": CONFIG["aesthetic_category_id"],
        "development_type": CONFIG["development_type"],
        "reuse_keys": CONFIG["reuse_keys"],
        "generation_tags": [
            "wave4",
            "standard_building",
            "modular_streetwall",
            "custom_pbr_skin",
            *CONFIG["kits"],
        ],
        "footprint_compatibility": footprint,
        "coordinate_contract": COORDINATE_CONTRACT,
        "textures": texture_inventory(skin),
        "facade_sheet": facade_contract(skin),
        "massing_graph": {
            "type": "modular_streetwall",
            "profile": "victorian_polychrome_main_street_v2",
            "render_locked": True,
            "goalpost": (
                "/archetypes/buildings/historical_brick_main_street/variant_0.png"
            ),
            "fixed": ["podium/entrance", "corner returns", "crown", "roof"],
            "repeatable": ["typical_a", "typical_b", "typical_c"],
        },
        "material_budget": {
            "max_assembled_materials": 24,
            "rationale": (
                "The registered facade bands, physical heritage glazing, cast-iron "
                "storefront, occupied rooms, secondary elevations and roof remain "
                "separate so close-range construction depth is preserved."
            ),
        },
        "dimensions": {
            "width_m": width,
            "depth_m": depth,
            "podium_height_m": podium_h,
            "floor_height_m": floor_h,
            "setback_height_m": floor_h,
            "roof_height_m": roof_h,
            "crown_height_m": crown_h,
            "default_floors": 2,
            "min_floors": 2,
            "max_floors": 4,
        },
        "native_width_m": width,
        "native_depth_m": depth,
        "native_floors": 2,
        "min_floors": 2,
        "max_floors": 4,
        "default_floors": 2,
        "modules": modules,
        "assembled": assembled,
        "thumbnail": f"{FAMILY}_preview.png",
        "renders": renders,
        "architectural_identity": CONFIG["identity"],
        "material_zones": CONFIG["materials"],
        "glass_profile": CONFIG["glass_profile"],
        "source_provenance": provenance,
    }
    (family_dir / f"{FAMILY}_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    grammar = {
        "family_id": FAMILY,
        "source": {
            "archetype_id": CONFIG["archetype_id"],
            "variant_id": CONFIG["variant_id"],
            "generation_archetype_id": CONFIG["generation_archetype_id"],
            "reuse_keys": CONFIG["reuse_keys"],
        },
        "dimensions": manifest["dimensions"],
        "architectural_signature": {
            "identity": CONFIG["identity"],
            "material_zones": CONFIG["materials"],
            "glass_profile": CONFIG["glass_profile"],
            "kits": CONFIG["kits"],
        },
        "archetype_aliases": CONFIG["aliases"],
        "footprint_compatibility": footprint,
        "massing_graph": manifest["massing_graph"],
    }
    (family_dir / "grammar.json").write_text(
        json.dumps(grammar, indent=2) + "\n",
        encoding="utf-8",
    )
    (family_dir / "archetype-source.json").write_text(
        json.dumps(provenance, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"[wave4-standard] {FAMILY}: {assembled_tris:,} tris, "
        f"{len(modules)} modules, {len(renders)} renders",
        flush=True,
    )


def render_existing(output_root: Path, view_set: str) -> None:
    clear_scene()
    family_dir = output_root / FAMILY
    manifest_path = family_dir / f"{FAMILY}_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    bpy.ops.import_scene.gltf(
        filepath=str(family_dir / manifest["assembled"]["filename"])
    )
    selected = None
    if view_set == "pilot":
        selected = {"preview", "front_corner_oblique", "facade_close", "aerial"}
    renders = render_views(family_dir, selected_roles=selected)
    if "elevation.jpg" not in renders:
        renders.append("elevation.jpg")
    if view_set == "all":
        manifest["renders"] = renders
        manifest_path.write_text(
            json.dumps(manifest, indent=2) + "\n",
            encoding="utf-8",
        )
    print(f"[wave4-standard-render] {FAMILY}: {len(renders)} renders", flush=True)


def main() -> int:
    args = parse_args()
    output_root = args.output_root.resolve()
    if args.render_existing:
        render_existing(output_root, args.view_set)
    else:
        build_family(
            output_root,
            args.view_set,
            args.skip_renders,
            args.skip_modules,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
