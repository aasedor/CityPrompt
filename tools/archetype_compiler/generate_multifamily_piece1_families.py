"""Generate the reference-locked multifamily Piece 1 pilot.

The pilot is a true-metric fixed landmark plus six semantic LEGO fallback
modules.  Its public identity comes from physical construction: exposed glulam
load paths, recessed occupied glazing, a carved double-height lobby, supported
balconies, a setback top floor, and independently modelled roof systems.

Run from the repository root with Blender 5.x::

    blender --background --factory-startup --python \
      tools/archetype_compiler/generate_multifamily_piece1_families.py -- \
      --family contemporary-timber-glass-midrise --view-set pilot
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

import generate_wave14_variant_families as core  # noqa: E402
from multifamily_piece1_specs import FAMILIES, with_family  # noqa: E402


_CORE_LOAD_PALETTE = core.load_palette


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", choices=sorted(FAMILIES), required=True)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("frontend/public/families"),
    )
    parser.add_argument(
        "--view-set",
        choices=(
            "preview",
            "pilot",
            "assessment",
            "all",
            "street",
            "context",
            "front_elevation",
            "front_corner_oblique",
            "rear_corner_oblique",
            "aerial",
            "facade_close",
        ),
        default="all",
    )
    parser.add_argument("--skip-renders", action="store_true")
    parser.add_argument("--skip-modules", action="store_true")
    parser.add_argument("--skip-assembled-export", action="store_true")
    parser.add_argument("--render-existing", action="store_true")
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(argv)


def _mark_materials(mats: dict[str, bpy.types.Material], cfg: dict) -> None:
    for material in mats.values():
        material["multifamily_piece1_reference_locked_material"] = True
        material["source_variant_id"] = cfg["variant_id"]
        material["generation_archetype_id"] = cfg["variant_id"]


def load_palette(folder: Path, cfg: dict) -> tuple[dict[str, bpy.types.Material], dict]:
    mats, skin = _CORE_LOAD_PALETTE(folder, cfg)
    mats["timber_dark"] = core.grade_material(
        mats["primary"].copy(), saturation=0.88, value=0.67
    )
    mats["timber_dark"].name = f"MAT_MF1_{cfg['family']}_GlulamEndGrain"
    mats["timber_light"] = core.grade_material(
        mats["primary"].copy(), saturation=0.92, value=1.08
    )
    mats["timber_light"].name = f"MAT_MF1_{cfg['family']}_LarchSoffit"
    mats["concrete_dark"] = core.grade_material(
        mats["secondary"].copy(), saturation=0.58, value=0.70
    )
    mats["concrete_dark"].name = f"MAT_MF1_{cfg['family']}_ConcreteReveal"
    mats["sedum"] = core.material(
        f"MAT_MF1_{cfg['family']}_ProceduralMixedSedumRoof",
        (0.18, 0.29, 0.085, 1.0),
        0.91,
    )
    # Fine-scale procedural variation keeps the extensive roof visibly alive
    # without stretching a complete photographed roof-detail panel across it.
    sedum_nodes = mats["sedum"].node_tree.nodes
    sedum_links = mats["sedum"].node_tree.links
    sedum_bsdf = next(
        node for node in sedum_nodes
        if node.bl_idname == "ShaderNodeBsdfPrincipled"
    )
    coordinates = sedum_nodes.new("ShaderNodeTexCoord")
    noise = sedum_nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 9.0
    noise.inputs["Detail"].default_value = 5.0
    noise.inputs["Roughness"].default_value = 0.72
    ramp = sedum_nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.24
    ramp.color_ramp.elements[0].color = (0.018, 0.055, 0.012, 1.0)
    ramp.color_ramp.elements[1].position = 0.78
    ramp.color_ramp.elements[1].color = (0.16, 0.105, 0.025, 1.0)
    middle = ramp.color_ramp.elements.new(0.52)
    middle.color = (0.055, 0.135, 0.018, 1.0)
    bump = sedum_nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.30
    bump.inputs["Distance"].default_value = 0.06
    sedum_links.new(coordinates.outputs["Generated"], noise.inputs["Vector"])
    sedum_links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    sedum_links.new(ramp.outputs["Color"], sedum_bsdf.inputs["Base Color"])
    sedum_links.new(noise.outputs["Fac"], bump.inputs["Height"])
    sedum_links.new(bump.outputs["Normal"], sedum_bsdf.inputs["Normal"])
    mats["soil"] = core.material(
        f"MAT_MF1_{cfg['family']}_DarkPlanterSoil",
        (0.105, 0.072, 0.043, 1.0),
        0.94,
    )
    mats["plant_dark"] = core.material(
        f"MAT_MF1_{cfg['family']}_PlanterEvergreen",
        (0.048, 0.145, 0.055, 1.0),
        0.83,
    )
    mats["plant_light"] = core.material(
        f"MAT_MF1_{cfg['family']}_PlanterGrass",
        (0.20, 0.34, 0.095, 1.0),
        0.88,
    )
    mats["gravel"] = core.material(
        f"MAT_MF1_{cfg['family']}_RoofGravel",
        (0.48, 0.47, 0.43, 1.0),
        0.95,
    )
    mats["membrane"] = core.material(
        f"MAT_MF1_{cfg['family']}_CharcoalRoofMembrane",
        (0.075, 0.085, 0.083, 1.0),
        0.88,
    )
    # Cell and edge-frame optics are deliberately authored as dedicated
    # materials.  Reusing the sedum/roof capture here washed the panels pale in
    # the first visual checkpoint and made them read as roof tiles.
    mats["pv_cell"] = core.material(
        f"MAT_MF1_{cfg['family']}_PhotovoltaicCell",
        (0.006, 0.018, 0.032, 1.0),
        0.48,
        metallic=0.08,
    )
    mats["pv_frame"] = core.material(
        f"MAT_MF1_{cfg['family']}_PhotovoltaicSilverFrame",
        (0.42, 0.47, 0.49, 1.0),
        0.26,
        metallic=0.82,
    )
    mats["curtain"] = core.material(
        f"MAT_MF1_{cfg['family']}_InteriorCurtain",
        (0.58, 0.49, 0.38, 1.0),
        0.86,
    )
    # Preserve neutral, high-transmission residential optics.  The pane remains
    # physically separate from both the room-depth and graphite frame layers.
    core.configure_glass(
        mats["glass"],
        cfg,
        tint=(0.44, 0.57, 0.55),
        transmission=0.78,
        alpha=0.32,
    )
    _mark_materials(mats, cfg)
    return mats, skin


def add_window_y(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    centre_x: float,
    facade_y: float,
    base_z: float,
    width: float,
    height: float,
    outward_sign: float,
    mats: dict,
    cfg: dict,
    mullions: int = 1,
    role: str = "assembled",
) -> None:
    inside_y = facade_y - outward_sign * 0.38
    pane_y = facade_y
    frame_y = facade_y + outward_sign * 0.075
    centre_z = base_z + height / 2
    core.add_box(
        objects,
        prefix + "_OccupiedDepth",
        (width - 0.22, 0.08, height - 0.22),
        (centre_x, inside_y, centre_z),
        mats["interior"],
        cfg,
        "warm_occupied_room_depth",
        role=role,
    )
    core.add_box(
        objects,
        prefix + "_LowIronPane",
        (width - 0.16, 0.10, height - 0.15),
        (centre_x, pane_y, centre_z),
        mats["glass"],
        cfg,
        "physical_neutral_low_iron_pane",
        role=role,
    )
    # A partial curtain and a floor datum make the occupied depth legible
    # without turning the glass into an emissive flat card.
    curtain_width = max(0.35, width * 0.22)
    core.add_box(
        objects,
        prefix + "_Curtain",
        (curtain_width, 0.035, height * 0.73),
        (centre_x - width * 0.31, inside_y - outward_sign * 0.035, centre_z + 0.05),
        mats["curtain"],
        cfg,
        "restrained_occupied_room_curtain",
        role=role,
    )
    for x in (centre_x - width / 2, centre_x + width / 2):
        core.add_box(
            objects,
            f"{prefix}_Jamb_{x:.2f}",
            (0.13, 0.19, height),
            (x, frame_y, centre_z),
            mats["frame"],
            cfg,
            "slim_graphite_window_frame",
            role=role,
        )
    for index in range(1, mullions + 1):
        x = centre_x - width / 2 + width * index / (mullions + 1)
        core.add_box(
            objects,
            f"{prefix}_Mullion_{index}",
            (0.10, 0.18, height - 0.08),
            (x, frame_y, centre_z),
            mats["frame"],
            cfg,
            "slim_graphite_operable_mullion",
            role=role,
        )
    for z in (base_z, base_z + height):
        core.add_box(
            objects,
            f"{prefix}_Rail_{z:.2f}",
            (width, 0.19, 0.13),
            (centre_x, frame_y, z),
            mats["frame"],
            cfg,
            "slim_graphite_window_frame",
            role=role,
        )
    core.add_box(
        objects,
        prefix + "_FloorDatum",
        (width - 0.22, 0.19, 0.11),
        (centre_x, inside_y, base_z + 0.12),
        mats["timber_dark"],
        cfg,
        "visible_cross_laminated_timber_floor_edge",
        role=role,
    )


def add_rectangular_beam(
    objects: list[bpy.types.Object],
    *,
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    thickness: float,
    mat: bpy.types.Material,
    cfg: dict,
    semantic: str,
    role: str = "assembled",
) -> bpy.types.Object:
    a, b = Vector(start), Vector(end)
    delta = b - a
    obj = core.add_box(
        objects,
        name,
        (thickness, thickness, delta.length),
        tuple((a + b) * 0.5),
        mat,
        cfg,
        semantic,
        role=role,
    )
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0.0, 0.0, 1.0)).rotation_difference(
        delta.normalized()
    )
    return obj


def add_window_x(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    centre_y: float,
    facade_x: float,
    base_z: float,
    width: float,
    height: float,
    outward_sign: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
) -> None:
    inside_x = facade_x - outward_sign * 0.38
    frame_x = facade_x + outward_sign * 0.075
    centre_z = base_z + height / 2
    core.add_box(
        objects,
        prefix + "_OccupiedDepth",
        (0.08, width - 0.22, height - 0.22),
        (inside_x, centre_y, centre_z),
        mats["interior"],
        cfg,
        "warm_occupied_secondary_room_depth",
        role=role,
    )
    core.add_box(
        objects,
        prefix + "_LowIronPane",
        (0.10, width - 0.16, height - 0.15),
        (facade_x, centre_y, centre_z),
        mats["glass"],
        cfg,
        "physical_neutral_low_iron_secondary_pane",
        role=role,
    )
    for y in (centre_y - width / 2, centre_y + width / 2, centre_y):
        core.add_box(
            objects,
            f"{prefix}_Mullion_{y:.2f}",
            (0.19, 0.11, height),
            (frame_x, y, centre_z),
            mats["frame"],
            cfg,
            "slim_graphite_secondary_frame",
            role=role,
        )
    for z in (base_z, base_z + height):
        core.add_box(
            objects,
            f"{prefix}_Rail_{z:.2f}",
            (0.19, width, 0.13),
            (frame_x, centre_y, z),
            mats["frame"],
            cfg,
            "slim_graphite_secondary_frame",
            role=role,
        )


def add_planter(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    centre: tuple[float, float, float],
    size: tuple[float, float, float],
    mats: dict,
    cfg: dict,
    role: str = "assembled",
    plants: int = 4,
) -> None:
    x, y, z = centre
    width, depth, height = size
    wall = 0.10
    core.add_box(objects, prefix + "_Front", (width, wall, height), (x, y - depth / 2, z), mats["timber_dark"], cfg, "integral_timber_planter_box", role=role)
    core.add_box(objects, prefix + "_Back", (width, wall, height), (x, y + depth / 2, z), mats["timber_dark"], cfg, "integral_timber_planter_box", role=role)
    for sign in (-1.0, 1.0):
        core.add_box(objects, f"{prefix}_End_{sign}", (wall, depth, height), (x + sign * width / 2, y, z), mats["timber_dark"], cfg, "integral_timber_planter_return", role=role)
    soil_z = z + height / 2 - 0.06
    core.add_box(objects, prefix + "_Soil", (width - 0.15, depth - 0.15, 0.11), (x, y, soil_z), mats["soil"], cfg, "visible_dark_planter_soil", role=role)
    for index in range(plants):
        px = x - width * 0.36 + width * 0.72 * index / max(1, plants - 1)
        stem_height = 0.38 + 0.10 * ((index + len(prefix)) % 3)
        core.add_cylinder(objects, f"{prefix}_Stem_{index}", 0.035, stem_height, (px, y, soil_z + stem_height / 2), mats["plant_dark"], cfg, "individual_planter_stem", vertices=8, role=role)
        core.add_sphere(objects, f"{prefix}_Foliage_{index}", 0.25, (px, y, soil_z + stem_height), mats["plant_light"] if index % 2 else mats["plant_dark"], cfg, "individual_mixed_balcony_plant", scale=(0.30 + 0.05 * (index % 2), 0.24, 1.55 + 0.18 * (index % 3)), role=role)


def add_balcony_y(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    centre_x: float,
    facade_y: float,
    base_z: float,
    width: float,
    outward_sign: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
    planted: bool = True,
) -> None:
    projection = 1.72
    centre_y = facade_y + outward_sign * projection * 0.50
    edge_y = facade_y + outward_sign * projection
    core.add_box(objects, prefix + "_CLTSlab", (width - 0.18, projection, 0.20), (centre_x, centre_y, base_z + 0.06), mats["timber_light"], cfg, "supported_projecting_clt_balcony_slab", role=role)
    for side in (-1.0, 1.0):
        add_rectangular_beam(
            objects,
            name=f"{prefix}_Bracket_{side}",
            start=(centre_x + side * width * 0.34, facade_y, base_z - 0.04),
            end=(centre_x + side * width * 0.34, edge_y, base_z - 0.70),
            thickness=0.13,
            mat=mats["timber_dark"],
            cfg=cfg,
            semantic="integral_rectangular_glulam_balcony_knee_brace",
            role=role,
        )
    guard_z = base_z + 0.56
    core.add_box(objects, prefix + "_GlassGuard", (width - 0.34, 0.055, 0.92), (centre_x, edge_y, guard_z), mats["glass"], cfg, "open_low_iron_balcony_guard", role=role)
    for side in (-1.0, 1.0):
        x = centre_x + side * (width / 2 - 0.09)
        core.add_box(objects, f"{prefix}_GuardPost_{side}", (0.075, 0.095, 1.05), (x, edge_y, base_z + 0.56), mats["frame"], cfg, "slim_graphite_balcony_guard_post", role=role)
    core.add_box(objects, prefix + "_TopRail", (width, 0.105, 0.075), (centre_x, edge_y, base_z + 1.08), mats["frame"], cfg, "slim_graphite_balcony_top_rail", role=role)
    # A real timber outer frame ties the projecting slab back into the facade
    # grid, so the balcony reads as a complete structural bay rather than a
    # railing box fastened onto a finished elevation.
    for side in (-1.0, 1.0):
        x = centre_x + side * (width / 2 - 0.10)
        core.add_box(objects, f"{prefix}_OuterTimberPost_{side}", (0.16, 0.18, 1.16), (x, edge_y, base_z + 0.58), mats["primary"], cfg, "balcony_outer_post_continuous_with_timber_bay", role=role)
    core.add_box(objects, prefix + "_OuterTimberHeader", (width, 0.18, 0.16), (centre_x, edge_y, base_z + 1.14), mats["primary"], cfg, "balcony_outer_header_continuous_with_timber_bay", role=role)
    if planted:
        planter_y = edge_y - outward_sign * 0.23
        add_planter(
            objects,
            prefix=prefix + "_Planter",
            centre=(centre_x, planter_y, base_z + 0.40),
            size=(width * 0.62, 0.38, 0.46),
            mats=mats,
            cfg=cfg,
            role=role,
            plants=4,
        )


def add_glulam_grid_y(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    facade_y: float,
    width: float,
    base_z: float,
    top_z: float,
    bays: int,
    datums: list[float],
    mats: dict,
    cfg: dict,
    role: str = "assembled",
    clear_central_datum: float | None = None,
) -> None:
    bay = width / bays
    for index in range(bays + 1):
        x = -width / 2 + index * bay
        core.add_box(objects, f"{prefix}_Column_{index}", (0.32, 0.46, top_z - base_z), (x, facade_y, (base_z + top_z) / 2), mats["primary"], cfg, "continuous_exposed_glulam_column", role=role)
        core.add_box(objects, f"{prefix}_KnifePlate_{index}", (0.20, 0.50, 0.26), (x, facade_y, base_z + 0.18), mats["frame"], cfg, "recessed_steel_glulam_knife_plate", role=role)
    for datum in datums:
        if clear_central_datum is not None and abs(datum - clear_central_datum) < 0.01:
            wing_width = (width - bay * 2) / 2
            for side in (-1.0, 1.0):
                core.add_box(objects, f"{prefix}_SplitBeam_{datum:.2f}_{side}", (wing_width, 0.50, 0.34), (side * (bay + wing_width / 2), facade_y, datum), mats["primary"], cfg, "glulam_beam_terminating_at_double_height_lobby", role=role)
        else:
            core.add_box(objects, f"{prefix}_Beam_{datum:.2f}", (width, 0.50, 0.34), (0.0, facade_y, datum), mats["primary"], cfg, "continuous_exposed_glulam_floor_beam", role=role)


def add_lobby(
    objects: list[bpy.types.Object],
    *,
    facade_y: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
    double_height: bool = True,
) -> None:
    width = 7.10
    base_z = 0.48
    height = 6.35 if double_height else 3.0
    centre_z = base_z + height / 2
    inside_y = facade_y + 0.55
    core.add_box(objects, "LOBBY_DeepOccupiedVoid", (width - 0.35, 0.10, height - 0.26), (0.0, inside_y, centre_z), mats["interior"], cfg, "carved_deep_occupied_lobby_void", role=role)
    core.add_box(objects, "LOBBY_LowIronWall", (width - 0.20, 0.11, height - 0.18), (0.0, facade_y - 0.04, centre_z), mats["glass"], cfg, "double_height_low_iron_lobby_wall", role=role)
    for x in (-width / 2, -width / 4, 0.0, width / 4, width / 2):
        core.add_box(objects, f"LOBBY_Mullion_{x:.2f}", (0.11, 0.21, height), (x, facade_y - 0.11, centre_z), mats["frame"], cfg, "physical_double_height_lobby_mullion", role=role)
    for z in (base_z, base_z + height * 0.43, base_z + height):
        core.add_box(objects, f"LOBBY_Rail_{z:.2f}", (width, 0.21, 0.12), (0.0, facade_y - 0.11, z), mats["frame"], cfg, "physical_double_height_lobby_rail", role=role)
    # The entrance is recessed behind the curtain wall and reads as a real door
    # set in the carved lobby, not another window panel.
    door_y = facade_y - 0.18
    for x in (-0.92, 0.0, 0.92):
        core.add_box(objects, f"LOBBY_DoorStile_{x}", (0.095, 0.22, 2.55), (x, door_y, 1.75), mats["frame"], cfg, "operable_lobby_door_stile", role=role)
    core.add_box(objects, "LOBBY_DoorHead", (2.0, 0.22, 0.10), (0.0, door_y, 3.02), mats["frame"], cfg, "operable_lobby_door_head", role=role)
    # Deep glulam canopy, supported from the same front structural grid.
    canopy_outer_y = facade_y - 2.50
    core.add_box(objects, "LOBBY_IntegratedCanopySoffit", (8.25, 2.75, 0.22), (0.0, (facade_y + canopy_outer_y) / 2, 3.60), mats["timber_light"], cfg, "deep_integral_glulam_entrance_canopy", role=role)
    for x in (-3.72, 3.72):
        core.add_box(objects, f"LOBBY_CanopyBeam_{x}", (0.32, 2.90, 0.48), (x, (facade_y + canopy_outer_y) / 2, 3.78), mats["primary"], cfg, "canopy_beam_continuous_with_glulam_grid", role=role)
        core.add_box(objects, f"LOBBY_CanopyColumn_{x}", (0.34, 0.42, 3.45), (x, canopy_outer_y + 0.15, 1.73), mats["primary"], cfg, "canopy_column_continuous_to_ground", role=role)
    core.add_box(objects, "LOBBY_CanopyFrontBeam", (8.25, 0.42, 0.48), (0.0, canopy_outer_y, 3.78), mats["primary"], cfg, "integrated_canopy_front_beam", role=role)
    for index, x in enumerate((-3.0, -1.5, 0.0, 1.5, 3.0)):
        core.add_box(objects, f"LOBBY_CanopyRafter_{index}", (0.14, 2.72, 0.24), (x, (facade_y + canopy_outer_y) / 2, 3.47), mats["timber_dark"], cfg, "visible_glulam_entrance_canopy_rafter", role=role)
    for step in range(3):
        core.add_box(objects, f"LOBBY_ThresholdStep_{step}", (7.0 - step * 0.30, 0.48, 0.12), (0.0, canopy_outer_y - 0.30 - step * 0.27, 0.12 + step * 0.12), mats["secondary"], cfg, "integral_pale_concrete_lobby_threshold", role=role)


def add_pv_module(
    objects: list[bpy.types.Object],
    *,
    prefix: str,
    centre_x: float,
    centre_y: float,
    base_z: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
) -> None:
    width, depth = 1.90, 1.05
    core.add_box(objects, prefix + "_RailA", (width, 0.065, 0.10), (centre_x, centre_y - depth * 0.30, base_z + 0.05), mats["pv_frame"], cfg, "raised_photovoltaic_racking_rail", role=role)
    core.add_box(objects, prefix + "_RailB", (width, 0.065, 0.10), (centre_x, centre_y + depth * 0.30, base_z + 0.05), mats["pv_frame"], cfg, "raised_photovoltaic_racking_rail", role=role)
    panel_z = base_z + 0.16
    core.add_box(objects, prefix + "_CellField", (width - 0.10, depth - 0.10, 0.07), (centre_x, centre_y, panel_z), mats["pv_cell"], cfg, "physical_blue_black_photovoltaic_cell_field", role=role)
    for x in (centre_x - width / 2, centre_x + width / 2):
        core.add_box(objects, f"{prefix}_FrameX_{x:.2f}", (0.055, depth, 0.11), (x, centre_y, panel_z + 0.01), mats["pv_frame"], cfg, "silver_photovoltaic_edge_frame", role=role)
    for y in (centre_y - depth / 2, centre_y + depth / 2):
        core.add_box(objects, f"{prefix}_FrameY_{y:.2f}", (width, 0.055, 0.11), (centre_x, y, panel_z + 0.01), mats["pv_frame"], cfg, "silver_photovoltaic_edge_frame", role=role)
    # Fine real cell separators stop the panels reading as oversized black roof tiles.
    for column in range(1, 6):
        x = centre_x - width / 2 + width * column / 6
        core.add_box(objects, f"{prefix}_CellLineX_{column}", (0.010, depth - 0.12, 0.010), (x, centre_y, panel_z + 0.045), mats["frame"], cfg, "fine_dark_photovoltaic_cell_separator", role=role)
    for row in range(1, 4):
        y = centre_y - depth / 2 + depth * row / 4
        core.add_box(objects, f"{prefix}_CellLineY_{row}", (width - 0.12, 0.010, 0.010), (centre_x, y, panel_z + 0.045), mats["frame"], cfg, "fine_dark_photovoltaic_cell_separator", role=role)


def add_roof_landscape(
    objects: list[bpy.types.Object],
    *,
    base_z: float,
    width: float,
    depth: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
) -> None:
    core.add_box(objects, "ROOF_DarkMembrane", (width, depth, 0.16), (0.0, 0.0, base_z + 0.08), mats["membrane"], cfg, "continuous_weatherproof_roof_membrane", role=role)
    # Gravel fire-breaks and drainage edges are continuous and visibly separate.
    for x in (-width / 2 + 0.42, width / 2 - 0.42):
        core.add_box(objects, f"ROOF_GravelEdgeX_{x:.2f}", (0.68, depth - 0.30, 0.12), (x, 0.0, base_z + 0.18), mats["gravel"], cfg, "continuous_roof_gravel_fire_break", role=role)
    for y in (-depth / 2 + 0.42, depth / 2 - 0.42):
        core.add_box(objects, f"ROOF_GravelEdgeY_{y:.2f}", (width - 0.30, 0.68, 0.12), (0.0, y, base_z + 0.18), mats["gravel"], cfg, "continuous_roof_gravel_fire_break", role=role)
        core.add_box(objects, f"ROOF_DrainageEdge_{y:.2f}", (width, 0.11, 0.23), (0.0, y + (0.30 if y > 0 else -0.30), base_z + 0.19), mats["frame"], cfg, "physical_metal_roof_drainage_edge", role=role)
    # One continuous extensive field wraps the service circulation and array,
    # matching the aerial goalpost instead of reading as decorative green pads.
    core.add_box(objects, "ROOF_ContinuousSedumCarrier", (width - 1.48, depth - 1.48, 0.12), (0.0, 0.0, base_z + 0.22), mats["soil"], cfg, "continuous_physical_sedum_soil_build_up", role=role)
    core.add_box(objects, "ROOF_ContinuousSedumField", (width - 1.62, depth - 1.62, 0.07), (0.0, 0.0, base_z + 0.315), mats["sedum"], cfg, "continuous_mixed_extensive_sedum_field", role=role)
    core.add_box(objects, "ROOF_PVServicePad", (11.55, 6.15, 0.075), (3.72, 1.80, base_z + 0.39), mats["membrane"], cfg, "separate_dark_photovoltaic_service_pad", role=role)
    core.add_box(objects, "ROOF_AccessGravelWalk", (1.05, depth - 2.0, 0.09), (-4.85, 0.0, base_z + 0.40), mats["gravel"], cfg, "continuous_roof_access_gravel_walk", role=role)
    core.add_box(objects, "ROOF_AccessCrossWalk", (6.15, 1.05, 0.09), (-7.15, 3.55, base_z + 0.40), mats["gravel"], cfg, "roof_access_cross_walk_to_penthouse", role=role)
    pv_start_x = -0.45
    pv_start_y = -0.10
    for row in range(4):
        for column in range(5):
            add_pv_module(
                objects,
                prefix=f"ROOF_PV_{row}_{column}",
                centre_x=pv_start_x + column * 2.10,
                centre_y=pv_start_y + row * 1.26,
                base_z=base_z + 0.28,
                mats=mats,
                cfg=cfg,
                role=role,
            )


def build_assembled(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    width, depth = 32.0, 22.0
    front_y, rear_y = -10.55, 10.55
    main_width = 28.80
    bay = main_width / 6
    bay_centres = [-main_width / 2 + bay * (index + 0.5) for index in range(6)]
    level_bases = [0.48, 3.85, 7.00, 10.15, 13.30]
    full_top = 16.45

    core.add_box(objects, "MF1_PaleConcreteFoundation", (width, depth, 0.46), (0.0, 0.0, 0.23), mats["secondary"], cfg, "pale_concrete_foundation_plinth")
    # Two real side wings leave the central lobby volume carved out through two levels.
    for side in (-1.0, 1.0):
        core.add_box(objects, f"MF1_GroundWing_{side}", (10.65, 19.25, 3.15), (side * 9.20, 0.15, 2.02), mats["concrete_dark"], cfg, "solid_ground_floor_wing_around_carved_lobby")
    core.add_box(objects, "MF1_LobbyRearCore", (7.15, 10.4, 6.38), (0.0, 5.05, 3.66), mats["interior"], cfg, "occupied_rear_lobby_and_circulation_core_closing_front_void")
    # Physical floor plates; the first upper datum is split around the double-height void.
    for side in (-1.0, 1.0):
        core.add_box(objects, f"MF1_SplitCLTDatum_{side}", (10.8, 20.0, 0.24), (side * 9.0, 0.0, 3.85), mats["timber_light"], cfg, "clt_floor_plate_terminating_at_lobby_void")
    for z in (7.00, 10.15, 13.30, 16.45):
        core.add_box(objects, f"MF1_ContinuousCLTDatum_{z:.2f}", (30.0, 20.0, 0.24), (0.0, 0.0, z), mats["timber_light"], cfg, "continuous_cross_laminated_timber_floor_plate")

    # Public front and secondary rear carry the same structural load path.
    add_glulam_grid_y(objects, prefix="MF1_FrontGlulam", facade_y=front_y - 0.12, width=main_width, base_z=0.46, top_z=full_top, bays=6, datums=[3.85, 7.00, 10.15, 13.30, 16.45], mats=mats, cfg=cfg, clear_central_datum=3.85)
    add_glulam_grid_y(objects, prefix="MF1_RearGlulam", facade_y=rear_y + 0.12, width=main_width, base_z=0.46, top_z=full_top, bays=6, datums=[3.85, 7.00, 10.15, 13.30, 16.45], mats=mats, cfg=cfg)

    # Pale ground-floor side bays and the carved central lobby.
    for index, x in enumerate(bay_centres):
        if index not in (2, 3):
            add_window_y(objects, prefix=f"MF1_GroundFront_{index}", centre_x=x, facade_y=front_y, base_z=0.68, width=bay - 0.38, height=2.72, outward_sign=-1.0, mats=mats, cfg=cfg, mullions=1)
        add_window_y(objects, prefix=f"MF1_GroundRear_{index}", centre_x=x, facade_y=rear_y, base_z=0.68, width=bay - 0.42, height=2.66, outward_sign=1.0, mats=mats, cfg=cfg, mullions=1)
    add_lobby(objects, facade_y=front_y, mats=mats, cfg=cfg, double_height=True)

    # Four full upper residential floors.  Level two remains open at the centre
    # for the double-height lobby; upper levels close it with occupied glazing.
    for level, base_z in enumerate(level_bases[1:], start=1):
        opening_height = 2.66
        for index, x in enumerate(bay_centres):
            front_lobby_void = level == 1 and index in (2, 3)
            if not front_lobby_void:
                add_window_y(objects, prefix=f"MF1_FrontL{level + 1}B{index}", centre_x=x, facade_y=front_y, base_z=base_z + 0.24, width=bay - 0.36, height=opening_height, outward_sign=-1.0, mats=mats, cfg=cfg, mullions=1)
            add_window_y(objects, prefix=f"MF1_RearL{level + 1}B{index}", centre_x=x, facade_y=rear_y, base_z=base_z + 0.24, width=bay - 0.42, height=opening_height, outward_sign=1.0, mats=mats, cfg=cfg, mullions=1)
            # Alternating outer planted balconies form a deliberate cadence,
            # while the lobby and central circulation remain visually clear.
            front_balcony = index in (0, 5)
            rear_balcony = index in (1, 4)
            if front_balcony and not front_lobby_void:
                add_balcony_y(objects, prefix=f"MF1_FrontBalconyL{level + 1}B{index}", centre_x=x, facade_y=front_y - 0.14, base_z=base_z + 0.18, width=bay - 0.22, outward_sign=-1.0, mats=mats, cfg=cfg, planted=True)
            if rear_balcony:
                add_balcony_y(objects, prefix=f"MF1_RearBalconyL{level + 1}B{index}", centre_x=x, facade_y=rear_y + 0.14, base_z=base_z + 0.18, width=bay - 0.22, outward_sign=1.0, mats=mats, cfg=cfg, planted=level in (2, 4))
        # Timber spandrels remain behind the expressed frame, tying windows to
        # the CLT datum instead of reading as one continuous curtain wall.
        core.add_box(objects, f"MF1_FrontLarchSpandrel_{level}", (main_width - 0.40, 0.28, 0.40), (0.0, front_y + 0.18, base_z + 0.12), mats["primary"], cfg, "continuous_larch_floor_spandrel")
        core.add_box(objects, f"MF1_RearLarchSpandrel_{level}", (main_width - 0.40, 0.28, 0.40), (0.0, rear_y - 0.18, base_z + 0.12), mats["primary"], cfg, "wrapped_larch_floor_spandrel")

    # Four-bay side elevations wrap every datum and carry their own occupied
    # punched windows rather than a copied public-front texture.  Cladding is
    # split around each opening so no broad opaque card can mask the pane.
    side_y = (-6.9, -2.3, 2.3, 6.9)
    for side in (-1.0, 1.0):
        side_x = side * 15.10
        cladding_x = side_x - side * 0.16
        for boundary, y in enumerate((-9.2, -4.6, 0.0, 4.6, 9.2)):
            core.add_box(objects, f"MF1_SideColumn_{side}_{boundary}", (0.42, 0.42, full_top - 0.46), (side_x, y, (full_top + 0.46) / 2), mats["primary"], cfg, "continuous_wrapped_side_glulam_column")
        for datum in (3.85, 7.00, 10.15, 13.30, 16.45):
            core.add_box(objects, f"MF1_SideBeam_{side}_{datum:.2f}", (0.48, 18.4, 0.34), (side_x, 0.0, datum), mats["primary"], cfg, "continuous_wrapped_side_glulam_beam")
        for level, base_z in enumerate(level_bases):
            for bay_index, y in enumerate(side_y):
                opening_width = 1.48
                opening_height = 2.34 if level else 2.28
                opening_base = base_z + 0.43
                cladding = mats["primary"] if level else mats["secondary"]
                filler_width = (4.60 - opening_width) / 2
                for direction in (-1.0, 1.0):
                    filler_y = y + direction * (opening_width / 2 + filler_width / 2)
                    core.add_box(objects, f"MF1_SideCladdingReturn_{side}_{level}_{bay_index}_{direction}", (0.28, filler_width, 2.86), (cladding_x, filler_y, base_z + 1.62), cladding, cfg, "individual_side_cladding_return_around_punched_window")
                bottom_height = opening_base - base_z
                top_height = 3.15 - bottom_height - opening_height
                core.add_box(objects, f"MF1_SideCladdingSill_{side}_{level}_{bay_index}", (0.28, opening_width, bottom_height), (cladding_x, y, base_z + bottom_height / 2), cladding, cfg, "physical_side_cladding_sill_return")
                core.add_box(objects, f"MF1_SideCladdingHead_{side}_{level}_{bay_index}", (0.28, opening_width, top_height), (cladding_x, y, opening_base + opening_height + top_height / 2), cladding, cfg, "physical_side_cladding_head_return")
                add_window_x(objects, prefix=f"MF1_Side{side}L{level + 1}B{bay_index}", centre_y=y, facade_x=side_x, base_z=opening_base, width=opening_width, height=opening_height, outward_sign=side, mats=mats, cfg=cfg)

    # Set-back sixth floor and a communal fifth-floor terrace.
    setback_base = 16.45
    setback_width, setback_depth = 25.60, 16.60
    setback_front, setback_rear = -8.15, 8.45
    core.add_box(objects, "MF1_SetbackOccupiedVolume", (setback_width - 0.80, setback_depth - 0.80, 2.86), (0.0, 0.15, setback_base + 1.60), mats["interior"], cfg, "occupied_setback_sixth_floor_depth")
    top_bays = 5
    top_bay = setback_width / top_bays
    for index in range(top_bays):
        x = -setback_width / 2 + top_bay * (index + 0.5)
        add_window_y(objects, prefix=f"MF1_SetbackFront_{index}", centre_x=x, facade_y=setback_front, base_z=setback_base + 0.26, width=top_bay - 0.38, height=2.64, outward_sign=-1.0, mats=mats, cfg=cfg, mullions=1)
        add_window_y(objects, prefix=f"MF1_SetbackRear_{index}", centre_x=x, facade_y=setback_rear, base_z=setback_base + 0.26, width=top_bay - 0.42, height=2.64, outward_sign=1.0, mats=mats, cfg=cfg, mullions=1)
    add_glulam_grid_y(objects, prefix="MF1_SetbackFrontGlulam", facade_y=setback_front - 0.10, width=setback_width, base_z=setback_base, top_z=19.66, bays=top_bays, datums=[19.66], mats=mats, cfg=cfg)
    add_glulam_grid_y(objects, prefix="MF1_SetbackRearGlulam", facade_y=setback_rear + 0.10, width=setback_width, base_z=setback_base, top_z=19.66, bays=top_bays, datums=[19.66], mats=mats, cfg=cfg)
    for side in (-1.0, 1.0):
        side_x = side * setback_width / 2
        cladding_x = side_x - side * 0.15
        for index, y in enumerate((-5.8, -1.9, 2.0, 5.9)):
            opening_width = 1.55
            filler_width = (3.90 - opening_width) / 2
            for direction in (-1.0, 1.0):
                filler_y = y + direction * (opening_width / 2 + filler_width / 2)
                core.add_box(objects, f"MF1_SetbackSideReturn_{side}_{index}_{direction}", (0.27, filler_width, 2.92), (cladding_x, filler_y, setback_base + 1.60), mats["primary"], cfg, "setback_larch_cladding_return")
            core.add_box(objects, f"MF1_SetbackSideSill_{side}_{index}", (0.27, opening_width, 0.35), (cladding_x, y, setback_base + 0.18), mats["primary"], cfg, "setback_larch_window_sill")
            core.add_box(objects, f"MF1_SetbackSideHead_{side}_{index}", (0.27, opening_width, 0.30), (cladding_x, y, setback_base + 3.05), mats["primary"], cfg, "setback_larch_window_head")
            add_window_x(objects, prefix=f"MF1_SetbackSide{side}_{index}", centre_y=y, facade_x=side_x, base_z=setback_base + 0.38, width=opening_width, height=2.52, outward_sign=side, mats=mats, cfg=cfg)

    # Communal timber deck occupies the front terrace; side sedum and planted
    # guards turn the setback into a real accessible roof landscape.
    for board in range(26):
        x = -12.3 + board * 0.98
        core.add_box(objects, f"MF1_TerraceDeckBoard_{board}", (0.88, 2.05, 0.10), (x, -9.30, setback_base + 0.13), mats["timber_light"], cfg, "individual_communal_terrace_deck_board")
    for side in (-1.0, 1.0):
        add_planter(objects, prefix=f"MF1_TerracePlanter_{side}", centre=(side * 10.4, -9.72, setback_base + 0.37), size=(3.4, 0.65, 0.48), mats=mats, cfg=cfg, plants=6)
    core.add_box(objects, "MF1_TerraceOpenGuard", (23.8, 0.07, 0.98), (0.0, -10.38, setback_base + 0.64), mats["glass"], cfg, "continuous_low_iron_communal_terrace_guard")
    for x in (-11.9, -8.0, -4.0, 0.0, 4.0, 8.0, 11.9):
        core.add_box(objects, f"MF1_TerraceGuardPost_{x}", (0.075, 0.11, 1.05), (x, -10.40, setback_base + 0.65), mats["frame"], cfg, "slim_terrace_guard_post")

    # Seventh datum is roof only, not an occupied storey.
    roof_base = 19.70
    add_roof_landscape(objects, base_z=roof_base, width=25.8, depth=16.8, mats=mats, cfg=cfg)
    core.add_box(objects, "MF1_RoofAccessPenthouse", (4.0, 3.1, 1.05), (-7.7, 4.8, roof_base + 0.61), mats["timber_dark"], cfg, "compact_timber_roof_access_penthouse")
    core.add_box(objects, "MF1_RoofAccessDoor", (1.05, 0.10, 0.88), (-7.7, 3.22, roof_base + 0.55), mats["glass"], cfg, "physical_glazed_roof_access_door")
    return objects


def _module_window_row(
    objects: list[bpy.types.Object],
    *,
    width: float,
    depth: float,
    height: float,
    phase: int,
    mats: dict,
    cfg: dict,
    role: str,
) -> None:
    bays = 6
    bay = width / bays
    centres = [-width / 2 + bay * (index + 0.5) for index in range(bays)]
    for facade_y, outward, label in ((-depth / 2, -1.0, "Front"), (depth / 2, 1.0, "Rear")):
        for index, x in enumerate(centres):
            add_window_y(objects, prefix=f"MODULE_{label}_{phase}_{index}", centre_x=x, facade_y=facade_y, base_z=0.22, width=bay - 0.34, height=height - 0.48, outward_sign=outward, mats=mats, cfg=cfg, role=role)
            balcony_indices = {0, 5}
            if index in balcony_indices and label == "Front":
                add_balcony_y(objects, prefix=f"MODULE_Balcony_{phase}_{index}", centre_x=x, facade_y=facade_y - 0.10, base_z=0.18, width=bay - 0.20, outward_sign=-1.0, mats=mats, cfg=cfg, role=role, planted=True)
        add_glulam_grid_y(objects, prefix=f"MODULE_{label}Grid_{phase}", facade_y=facade_y + outward * 0.10, width=width, base_z=0.0, top_z=height, bays=bays, datums=[height], mats=mats, cfg=cfg, role=role)
    core.add_box(objects, f"MODULE_CLTPlate_{phase}", (width, depth - 0.45, 0.20), (0.0, 0.0, 0.10), mats["timber_light"], cfg, "repeatable_complete_clt_apartment_floor_datum", role=role)


def build_module(
    role: str,
    variant: str,
    mats: dict,
    cfg: dict,
) -> tuple[list[bpy.types.Object], float]:
    objects: list[bpy.types.Object] = []
    width, depth = 28.8, 20.0
    if role == "podium":
        height = cfg["podium_height"]
        core.add_box(objects, "MODULE_PaleConcretePlinth", (30.0, 20.8, 0.44), (0.0, 0.0, 0.22), mats["secondary"], cfg, "fixed_pale_concrete_podium_plinth", role=role)
        add_lobby(objects, facade_y=-depth / 2, mats=mats, cfg=cfg, role=role, double_height=False)
        bay = width / 8
        for index in (0, 1, 4, 5):
            x = -width / 2 + bay * (index + 0.5)
            add_window_y(objects, prefix=f"MODULE_PodiumFront_{index}", centre_x=x, facade_y=-depth / 2, base_z=0.62, width=bay - 0.38, height=2.75, outward_sign=-1.0, mats=mats, cfg=cfg, role=role)
            add_window_y(objects, prefix=f"MODULE_PodiumRear_{index}", centre_x=x, facade_y=depth / 2, base_z=0.62, width=bay - 0.38, height=2.75, outward_sign=1.0, mats=mats, cfg=cfg, role=role)
        add_glulam_grid_y(objects, prefix="MODULE_PodiumFrontGrid", facade_y=-depth / 2 - 0.10, width=width, base_z=0.44, top_z=height, bays=6, datums=[height], mats=mats, cfg=cfg, role=role)
        add_glulam_grid_y(objects, prefix="MODULE_PodiumRearGrid", facade_y=depth / 2 + 0.10, width=width, base_z=0.44, top_z=height, bays=6, datums=[height], mats=mats, cfg=cfg, role=role)
    elif role == "floor":
        height = cfg["floor_height"]
        phase = {"typical_a": 0, "typical_b": 1, "typical_c": 2}[variant]
        _module_window_row(objects, width=width, depth=depth, height=height, phase=phase, mats=mats, cfg=cfg, role=role)
    elif role == "crown":
        height = cfg["crown_height"]
        crown_width, crown_depth = 25.6, 16.6
        _module_window_row(objects, width=crown_width, depth=crown_depth, height=height, phase=1, mats=mats, cfg=cfg, role=role)
        core.add_box(objects, "MODULE_SetbackTerraceDeck", (29.5, 2.0, 0.10), (0.0, -9.25, 0.12), mats["timber_light"], cfg, "fixed_communal_setback_terrace", role=role)
    else:
        height = cfg["roof_height"]
        add_roof_landscape(objects, base_z=0.0, width=25.8, depth=16.8, mats=mats, cfg=cfg, role=role)
    for marker in core.module_contract_markers(role, variant, height):
        objects.append(core.tag_object(marker, "four_elevation_material_contract", cfg, role=role))
    return objects, height


def footprint_contract(cfg: dict) -> dict:
    floors = [cfg["min_floors"], cfg["max_floors"]]
    common = {
        "recommendedFloors": floors,
        "scaleMin": 0.62,
        "scaleMax": 1.40,
        "maxAxisRatio": 1.30,
        "preferredBayMultiple_m": 4.80,
    }
    profiles = {
        "rectangle": {
            **common,
            "recommendedWidth_m": [19.8, 57.6],
            "recommendedDepth_m": [13.6, 34.8],
        },
        "l_shape": {
            **common,
            "recommendedWidth_m": [23.0, 65.0],
            "recommendedDepth_m": [15.4, 39.0],
            "wingDepth_m": [7.2, 14.4],
        },
        "u_shape": {
            **common,
            "recommendedWidth_m": [26.0, 70.0],
            "recommendedDepth_m": [17.0, 42.0],
            "wingDepth_m": [7.2, 14.4],
            "minimumCourtyard_m": 10.8,
        },
    }
    return {
        "preferredProfiles": ["rectangle", "l_shape", "u_shape"],
        "minimumPreferredProfiles": 3,
        "profileRationale": (
            "Rectangle, L and U drawings repeat complete 4.80 m glulam apartment bays "
            "around authored secondary elevations. Each repeated bay preserves its CLT "
            "datum, physical pane, occupied depth, frame, timber load path and optional "
            "supported balcony; the carved lobby, corners, setback and roof systems remain fixed."
        ),
        "fixedLandmarkScaleBand": {
            "scaleMin": 0.62,
            "scaleMax": 1.40,
            "maxAxisRatio": 1.30,
        },
        **profiles["rectangle"],
        "wingDepth_m": [7.2, 14.4],
        "minimumCourtyard_m": 10.8,
        "profiles": profiles,
        "notes": [
            "Vary width only in whole 4.80 m structural apartment bays.",
            "Vary height only with complete floor modules between four and eight occupied levels.",
            "Preserve the central lobby, corner returns, setback terrace and roof systems as fixed semantic pieces.",
        ],
    }


def massing_graph(cfg: dict) -> dict:
    features = [
        "exactly_six_occupied_levels",
        "carved_double_height_central_lobby",
        "continuous_exposed_glulam_load_path",
        "alternating_supported_planted_balconies",
        "setback_sixth_floor_and_communal_terrace",
        "physical_low_iron_glazing_with_occupied_depth",
        "wrapped_secondary_elevations",
        "separate_sedum_pv_deck_gravel_and_drainage_roof_zones",
    ]
    return {
        "type": "fixed_six_storey_mass_timber_midrise_with_repeatable_complete_apartment_bays",
        "variant_id": cfg["variant_id"],
        "occupied_storeys": cfg["native_floors"],
        "features": features,
        "physical_window_layers": [
            "occupied_depth",
            "physical_low_iron_pane",
            "separate_graphite_frame",
            "glulam_structural_surround",
            "clt_floor_datum",
            "timber_wall_return",
        ],
        "fallback_policy": (
            "fixed lobby, ends, setback and roof plus repeatable complete 4.80 m "
            "glulam apartment construction bays"
        ),
    }


def view_map(cfg: dict) -> dict[str, tuple[tuple[float, float, float], tuple[float, float, float], float]]:
    target = (0.0, 0.0, 9.2)
    return {
        "preview": ((42.0, -58.0, 30.0), target, 54),
        "street": ((26.0, -48.0, 11.5), (0.0, -2.0, 8.2), 57),
        "context": ((55.0, -70.0, 34.0), target, 52),
        "front_corner_oblique": ((39.0, -56.0, 24.0), target, 56),
        "front_elevation": ((0.0, -67.0, 10.8), (0.0, -0.5, 10.2), 61),
        "rear_corner_oblique": ((-40.0, 56.0, 26.0), target, 55),
        "aerial": ((38.0, -42.0, 51.0), (0.0, 0.0, 8.0), 53),
        "facade_close": ((20.0, -39.0, 10.0), (0.0, -8.0, 8.4), 67),
    }


def install_hooks() -> None:
    core.FAMILIES = FAMILIES
    core.load_palette = load_palette
    core.build_assembled = build_assembled
    core.build_module = build_module
    core.footprint_contract = footprint_contract
    core.massing_graph = massing_graph
    core.view_map = view_map


def postprocess_manifest(output_root: Path, cfg: dict) -> None:
    folder = (output_root / cfg["family"]).resolve()
    manifest_path = folder / f"{cfg['family']}_manifest.json"
    if not manifest_path.is_file():
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["generator"] = {
        **(manifest.get("generator") or {}),
        "name": "archetype_compiler/generate_multifamily_piece1_families.py",
        "version": "1.0.0",
    }
    graph = massing_graph(cfg)
    manifest["generation_tags"] = [
        "multifamily_completion_piece1",
        "timber_glass_pilot",
        "reference_locked_goalpost",
        "six_zone_custom_pbr_skin",
        "fixed_landmark_and_modular_fallback",
        "complete_semantic_apartment_bay_repeat",
        "physical_separate_low_iron_glazing",
        "occupied_residential_depth",
        "credible_timber_load_paths",
        "integrated_supported_balconies",
        "roof_systems_not_texture",
        *graph["features"],
    ]
    provenance = manifest.get("source_provenance") or {}
    provenance["method"] = (
        "corrected six-storey four-view goalpost, separate construction-material board, "
        "deterministic true-metric physical geometry, exposed glulam load paths, carved "
        "double-height lobby, supported planted balconies, physical low-iron panes with "
        "occupied room depth, independently modelled roof systems, and complete semantic "
        "LEGO apartment-bay fallback modules"
    )
    provenance["coverage_cohort"] = cfg["cohort"]
    manifest["source_provenance"] = provenance
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (folder / "archetype-source.json").write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    cfg = with_family(args.family)
    install_hooks()
    if args.render_existing:
        core.render_existing(args.output_root, cfg, view_set=args.view_set)
    else:
        core.build_family(
            args.output_root,
            cfg,
            view_set=args.view_set,
            skip_renders=args.skip_renders,
            skip_modules=args.skip_modules,
            skip_assembled_export=args.skip_assembled_export,
        )
    postprocess_manifest(args.output_root, cfg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
