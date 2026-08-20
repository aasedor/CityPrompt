"""Generate ten commonplace, catalogue-registered Wave 16 LEGO families.

The builders share audited construction systems (sash, storefront, balcony,
stair, parapet, gable and loading bay) while each family keeps an independent
silhouette and identity graph.  Catalogue thumbnails are never promoted by
this script; comparison review remains a human checkpoint.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy


TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

import generate_wave14_variant_families as core  # noqa: E402
from wave16_standard_specs import FAMILIES, with_family  # noqa: E402


_CORE_LOAD_PALETTE = core.load_palette
_CORE_VIEW_MAP = core.view_map


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
            "preview", "pilot", "assessment", "all", "street", "context",
            "front_elevation", "front_corner_oblique", "rear_corner_oblique",
            "aerial", "facade_close",
        ),
        default="all",
    )
    parser.add_argument("--skip-renders", action="store_true")
    parser.add_argument("--skip-modules", action="store_true")
    parser.add_argument("--skip-assembled-export", action="store_true")
    parser.add_argument("--render-existing", action="store_true")
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(argv)


def load_palette(
    folder: Path,
    cfg: dict,
    *,
    texture_lod: str = "near",
) -> tuple[dict[str, bpy.types.Material], dict]:
    mats, skin = _CORE_LOAD_PALETTE(folder, cfg, texture_lod=texture_lod)
    # The shared studio rig is intentionally bright.  Restore the catalogue's
    # practical value hierarchy so roofs, frames and timber do not wash out.
    for key, value in {
        "primary": 0.82,
        "secondary": 0.84,
        "ornament": 0.72,
        "frame": 0.60,
        "roof": 0.42,
    }.items():
        core.grade_material(mats[key], saturation=1.04, value=value)
    for material in mats.values():
        material["wave16_catalogue_registered_material"] = True
        material["coverage_cohort"] = cfg["cohort"]
    mats["dark"] = core.material(
        f"MAT_W16_{cfg['family']}_DeepShadow",
        (0.035, 0.042, 0.041, 1.0),
        0.70,
    )
    mats["white"] = core.material(
        f"MAT_W16_{cfg['family']}_PaintedWhite",
        (0.77, 0.76, 0.70, 1.0),
        0.68,
    )
    mats["plant"] = core.material(
        f"MAT_W16_{cfg['family']}_Planting",
        (0.055, 0.19, 0.045, 1.0),
        0.82,
    )
    for key in ("dark", "white", "plant"):
        mats[key]["wave16_catalogue_registered_material"] = True
        mats[key]["coverage_cohort"] = cfg["cohort"]
    return mats, skin


def view_map(cfg: dict) -> dict:
    views = _CORE_VIEW_MAP(cfg)
    width, depth, height = cfg["native"]
    if height < 11.0:
        distance = max(width * 1.45, depth * 2.4, 24.0)
        views.update(
            {
                "preview": ((distance * 0.58, -distance, height * 0.95), (0.0, 0.0, height * 0.40), 52),
                "street": ((distance * 0.40, -distance * 0.82, height * 0.48), (0.0, -depth * 0.10, height * 0.36), 58),
                "facade_close": ((width * 0.30, -max(depth * 0.92, width * 0.72), height * 0.36), (0.0, -depth * 0.46, height * 0.36), 65),
            }
        )
    return views


def add_mesh(
    objects: list[bpy.types.Object],
    name: str,
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, ...]],
    mat: bpy.types.Material,
    cfg: dict,
    semantic: str,
    *,
    role: str = "assembled",
) -> bpy.types.Object:
    return core.create_mesh_object(
        objects, name, vertices, faces, mat, cfg, semantic, role=role
    )


def add_gable_roof(
    objects: list[bpy.types.Object],
    name: str,
    *,
    centre: tuple[float, float],
    width: float,
    depth: float,
    base_z: float,
    rise: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
) -> None:
    cx, cy = centre
    x0, x1 = cx - width / 2, cx + width / 2
    y0, y1 = cy - depth / 2, cy + depth / 2
    vertices = [
        (x0, y0, base_z), (x1, y0, base_z), (x1, y1, base_z),
        (x0, y1, base_z), (cx, y0, base_z + rise),
        (cx, y1, base_z + rise),
    ]
    faces = [(0, 3, 2, 1), (0, 1, 4), (3, 5, 2), (0, 4, 5, 3), (1, 2, 5, 4)]
    add_mesh(objects, name, vertices, faces, mats["roof"], cfg, "solid_gable_roof", role=role)
    for suffix, y in (("Front", y0 - 0.05), ("Rear", y1 + 0.05)):
        core.add_beam(objects, f"{name}_{suffix}FasciaL", (x0, y, base_z), (cx, y, base_z + rise), 0.10, mats["frame"], cfg, "supported_gable_fascia", role=role)
        core.add_beam(objects, f"{name}_{suffix}FasciaR", (cx, y, base_z + rise), (x1, y, base_z), 0.10, mats["frame"], cfg, "supported_gable_fascia", role=role)


def add_hip_roof(
    objects: list[bpy.types.Object],
    name: str,
    *,
    centre: tuple[float, float],
    width: float,
    depth: float,
    base_z: float,
    rise: float,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
) -> None:
    cx, cy = centre
    x0, x1 = cx - width / 2, cx + width / 2
    y0, y1 = cy - depth / 2, cy + depth / 2
    ridge_half = min(width * 0.16, max(0.25, (depth - width) * 0.20 + 0.35))
    vertices = [
        (x0, y0, base_z), (x1, y0, base_z), (x1, y1, base_z), (x0, y1, base_z),
        (cx, cy - ridge_half, base_z + rise), (cx, cy + ridge_half, base_z + rise),
    ]
    faces = [(0, 1, 4), (1, 2, 5, 4), (2, 3, 5), (3, 0, 4, 5), (0, 3, 2, 1)]
    add_mesh(objects, name, vertices, faces, mats["roof"], cfg, "solid_hip_roof", role=role)
    core.add_box(objects, name + "_EaveFasciaFront", (width + 0.25, 0.14, 0.16), (cx, y0 - 0.04, base_z), mats["frame"], cfg, "continuous_roof_fascia", role=role)


def add_flat_roof(
    objects: list[bpy.types.Object],
    name: str,
    *,
    width: float,
    depth: float,
    z: float,
    mats: dict,
    cfg: dict,
    parapet: float = 0.55,
    centre: tuple[float, float] = (0.0, 0.0),
    role: str = "assembled",
) -> None:
    cx, cy = centre
    core.add_box(objects, name, (width, depth, 0.22), (cx, cy, z + 0.11), mats["roof"], cfg, "complete_flat_roof", role=role)
    for suffix, size, location in (
        ("Front", (width, 0.25, parapet), (cx, cy - depth / 2, z + parapet / 2)),
        ("Rear", (width, 0.25, parapet), (cx, cy + depth / 2, z + parapet / 2)),
        ("Left", (0.25, depth, parapet), (cx - width / 2, cy, z + parapet / 2)),
        ("Right", (0.25, depth, parapet), (cx + width / 2, cy, z + parapet / 2)),
    ):
        core.add_box(objects, f"{name}_Parapet_{suffix}", size, location, mats["secondary"], cfg, "grounded_roof_parapet", role=role)


def add_window_y(
    objects: list[bpy.types.Object],
    prefix: str,
    *,
    x: float,
    y: float,
    centre_z: float,
    width: float,
    height: float,
    outward: int,
    mats: dict,
    cfg: dict,
    divisions: int = 2,
    role: str = "assembled",
) -> None:
    room_y = y - outward * 0.25
    pane_y = y + outward * 0.025
    frame_y = y + outward * 0.09
    core.add_box(objects, prefix + "_OccupiedDepth", (width - 0.16, 0.08, height - 0.16), (x, room_y, centre_z), mats["interior"], cfg, "occupied_room_depth", role=role)
    core.add_box(objects, prefix + "_PhysicalGlass", (width - 0.12, 0.08, height - 0.12), (x, pane_y, centre_z), mats["glass"], cfg, "physical_recessed_glazing", role=role)
    for side in (-1, 1):
        core.add_box(objects, f"{prefix}_Jamb_{side:+d}", (0.10, 0.16, height + 0.18), (x + side * width / 2, frame_y, centre_z), mats["frame"], cfg, "physical_window_jamb", role=role)
    for side in (-1, 1):
        core.add_box(objects, f"{prefix}_Rail_{side:+d}", (width + 0.20, 0.16, 0.10), (x, frame_y, centre_z + side * height / 2), mats["secondary"], cfg, "physical_window_head_or_sill", role=role)
    for index in range(1, divisions):
        mx = x - width / 2 + width * index / divisions
        core.add_box(objects, f"{prefix}_Mullion_{index}", (0.065, 0.18, height - 0.10), (mx, frame_y, centre_z), mats["frame"], cfg, "physical_window_mullion", role=role)
    core.add_box(objects, prefix + "_Transom", (width - 0.10, 0.18, 0.06), (x, frame_y, centre_z), mats["frame"], cfg, "physical_window_transom", role=role)


def add_window_x(
    objects: list[bpy.types.Object],
    prefix: str,
    *,
    x: float,
    y: float,
    centre_z: float,
    width: float,
    height: float,
    outward: int,
    mats: dict,
    cfg: dict,
    role: str = "assembled",
) -> None:
    room_x = x - outward * 0.25
    pane_x = x + outward * 0.025
    frame_x = x + outward * 0.09
    core.add_box(objects, prefix + "_OccupiedDepth", (0.08, width - 0.16, height - 0.16), (room_x, y, centre_z), mats["interior"], cfg, "occupied_room_depth", role=role)
    core.add_box(objects, prefix + "_PhysicalGlass", (0.08, width - 0.12, height - 0.12), (pane_x, y, centre_z), mats["glass"], cfg, "physical_recessed_glazing", role=role)
    for side in (-1, 1):
        core.add_box(objects, f"{prefix}_Jamb_{side:+d}", (0.16, 0.10, height + 0.18), (frame_x, y + side * width / 2, centre_z), mats["frame"], cfg, "physical_window_jamb", role=role)
    for side in (-1, 1):
        core.add_box(objects, f"{prefix}_Rail_{side:+d}", (0.16, width + 0.20, 0.10), (frame_x, y, centre_z + side * height / 2), mats["secondary"], cfg, "physical_window_head_or_sill", role=role)
    core.add_box(objects, prefix + "_Mullion", (0.18, 0.065, height - 0.10), (frame_x, y, centre_z), mats["frame"], cfg, "physical_window_mullion", role=role)


def add_door_y(
    objects: list[bpy.types.Object],
    prefix: str,
    *,
    x: float,
    y: float,
    width: float,
    height: float,
    mats: dict,
    cfg: dict,
    outward: int = -1,
    role: str = "assembled",
) -> None:
    core.add_box(objects, prefix + "_Threshold", (width + 0.55, 0.75, 0.18), (x, y + outward * 0.27, 0.09), mats["secondary"], cfg, "grounded_entrance_threshold", role=role)
    core.add_box(objects, prefix + "_Door", (width, 0.14, height), (x, y + outward * 0.08, height / 2 + 0.18), mats["ornament"], cfg, "physical_entrance_door", role=role)
    core.add_box(objects, prefix + "_Glass", (width * 0.42, 0.06, height * 0.48), (x, y + outward * 0.17, height * 0.58), mats["glass"], cfg, "entrance_door_glazing", role=role)
    for side in (-1, 1):
        core.add_box(objects, f"{prefix}_Jamb_{side:+d}", (0.14, 0.30, height + 0.28), (x + side * (width / 2 + 0.08), y, height / 2 + 0.18), mats["frame"], cfg, "physical_door_jamb", role=role)


def add_storefront_y(
    objects: list[bpy.types.Object],
    prefix: str,
    *,
    centre_x: float,
    width: float,
    y: float,
    height: float,
    mats: dict,
    cfg: dict,
    outward: int = -1,
    role: str = "assembled",
) -> None:
    core.add_box(objects, prefix + "_OccupiedShop", (width - 0.25, 0.10, height - 0.20), (centre_x, y - outward * 0.42, height / 2 + 0.20), mats["interior"], cfg, "deep_occupied_shop_interior", role=role)
    core.add_box(objects, prefix + "_Glass", (width - 0.18, 0.08, height - 0.14), (centre_x, y + outward * 0.03, height / 2 + 0.20), mats["glass"], cfg, "clear_physical_storefront_glass", role=role)
    for index in range(5):
        x = centre_x - width / 2 + width * index / 4
        core.add_box(objects, f"{prefix}_Mullion_{index}", (0.10, 0.18, height), (x, y + outward * 0.10, height / 2 + 0.20), mats["frame"], cfg, "storefront_mullion", role=role)
    core.add_box(objects, prefix + "_Head", (width + 0.15, 0.22, 0.16), (centre_x, y + outward * 0.10, height + 0.22), mats["frame"], cfg, "storefront_head", role=role)


def add_guard_y(objects: list[bpy.types.Object], prefix: str, *, x0: float, x1: float, y: float, z: float, mats: dict, cfg: dict, role: str = "assembled") -> None:
    core.add_box(objects, prefix + "_TopRail", (x1 - x0, 0.09, 0.09), ((x0 + x1) / 2, y, z + 0.95), mats["frame"], cfg, "continuous_guard_top_rail", role=role)
    for index in range(max(2, round((x1 - x0) / 0.55)) + 1):
        x = x0 + (x1 - x0) * index / max(1, round((x1 - x0) / 0.55))
        core.add_box(objects, f"{prefix}_Picket_{index}", (0.045, 0.07, 0.95), (x, y, z + 0.48), mats["frame"], cfg, "grounded_guard_picket", role=role)


def add_stair_x(objects: list[bpy.types.Object], prefix: str, *, x0: float, x1: float, y: float, top_z: float, mats: dict, cfg: dict) -> None:
    steps = 14
    for index in range(steps):
        fraction = (index + 1) / steps
        x = x0 + (x1 - x0) * fraction
        height = top_z * fraction
        core.add_box(objects, f"{prefix}_Step_{index}", (abs(x1 - x0) / steps + 0.10, 1.25, 0.12), (x, y, height), mats["ornament"], cfg, "open_exterior_stair_tread")
        if index in {0, steps - 1}:
            core.add_box(objects, f"{prefix}_Support_{index}", (0.12, 1.0, max(0.12, height)), (x, y, height / 2), mats["frame"], cfg, "grounded_stair_support")
    for side in (-1, 1):
        stringer_y = y + side * 0.54
        core.add_beam(objects, f"{prefix}_Stringer_{side:+d}", (x0, stringer_y, 0.12), (x1, stringer_y, top_z), 0.07, mats["frame"], cfg, "continuous_grounded_stair_stringer")
    for side in (-1, 1):
        rail_y = y + side * 0.70
        core.add_beam(objects, f"{prefix}_Rail_{side:+d}", (x0, rail_y, 0.95), (x1, rail_y, top_z + 0.95), 0.055, mats["frame"], cfg, "continuous_supported_stair_guard")


def add_fire_escape(objects: list[bpy.types.Object], prefix: str, *, x: float, y: float, floors: int, floor_height: float, mats: dict, cfg: dict) -> None:
    for floor in range(1, floors):
        z = floor * floor_height + 0.25
        core.add_box(objects, f"{prefix}_Platform_{floor}", (4.0, 1.15, 0.12), (x, y, z), mats["ornament"], cfg, "supported_fire_escape_platform")
        add_guard_y(objects, f"{prefix}_Guard_{floor}", x0=x - 2.0, x1=x + 2.0, y=y - 0.50, z=z, mats=mats, cfg=cfg)
        if floor < floors - 1:
            core.add_beam(objects, f"{prefix}_FlightA_{floor}", (x - 1.5, y - 0.42, z + 0.10), (x + 1.5, y - 0.42, z + floor_height - 0.12), 0.055, mats["ornament"], cfg, "supported_fire_escape_stringer")
            core.add_beam(objects, f"{prefix}_FlightB_{floor}", (x - 1.5, y + 0.42, z + 0.10), (x + 1.5, y + 0.42, z + floor_height - 0.12), 0.055, mats["ornament"], cfg, "supported_fire_escape_stringer")


def add_window_rows(objects: list[bpy.types.Object], *, prefix: str, xs: list[float], levels: list[float], y: float, width: float, height: float, mats: dict, cfg: dict, divisions: int = 2) -> None:
    for floor, z in enumerate(levels):
        for bay, x in enumerate(xs):
            add_window_y(objects, f"{prefix}_{floor}_{bay}", x=x, y=y, centre_z=z, width=width, height=height, outward=-1, mats=mats, cfg=cfg, divisions=divisions)


def build_craftsman_bungalow(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    core.add_box(objects, "BUNGALOW_MasonryBase", (9.6, 11.4, 0.65), (0.0, 0.0, 0.325), mats["primary"], cfg, "grounded_masonry_base")
    core.add_box(objects, "BUNGALOW_OccupiedBody", (9.3, 11.1, 2.65), (0.0, 0.05, 1.95), mats["secondary"], cfg, "complete_one_storey_house_body")
    core.add_box(objects, "BUNGALOW_BrickFrontField", (9.0, 0.22, 1.55), (0.0, -5.58, 1.25), mats["primary"], cfg, "brick_public_facade")
    add_window_rows(objects, prefix="BUNGALOW_FrontSash", xs=[-3.0, -0.8, 3.0], levels=[1.95], y=-5.72, width=1.45, height=1.55, mats=mats, cfg=cfg, divisions=2)
    add_door_y(objects, "BUNGALOW_FrontDoor", x=1.0, y=-5.70, width=1.0, height=2.15, mats=mats, cfg=cfg)
    for side in (-1, 1):
        for index, y in enumerate((-2.9, 0.0, 2.9)):
            add_window_x(objects, f"BUNGALOW_Side_{side:+d}_{index}", x=side * 4.68, y=y, centre_z=1.95, width=1.35, height=1.40, outward=side, mats=mats, cfg=cfg)
    add_gable_roof(objects, "BUNGALOW_MainGableRoof", centre=(0.0, 0.0), width=10.8, depth=12.6, base_z=3.22, rise=2.85, mats=mats, cfg=cfg)
    core.add_box(objects, "BUNGALOW_FrontPorchDeck", (5.0, 2.2, 0.24), (1.0, -6.25, 0.48), mats["secondary"], cfg, "grounded_front_porch_deck")
    for x in (-1.0, 3.0):
        core.add_box(objects, f"BUNGALOW_PorchPost_{x:+.1f}", (0.34, 0.34, 2.35), (x, -6.80, 1.76), mats["ornament"], cfg, "load_bearing_porch_post")
    add_gable_roof(objects, "BUNGALOW_FrontPorch", centre=(1.0, -6.18), width=5.4, depth=2.8, base_z=2.88, rise=1.55, mats=mats, cfg=cfg)
    for step in range(3):
        core.add_box(objects, f"BUNGALOW_EntryStep_{step}", (1.7 + step * 0.25, 0.36, 0.16 * (step + 1)), (1.0, -7.65 + step * 0.30, 0.08 * (step + 1)), mats["secondary"], cfg, "grounded_entry_step")
    core.add_box(objects, "BUNGALOW_MasonryChimney", (0.75, 0.75, 3.5), (-3.25, 2.0, 4.55), mats["primary"], cfg, "masonry_chimney_with_roof_intersection")
    return objects


def build_edwardian_foursquare(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    core.add_box(objects, "FOURSQUARE_StoneFoundation", (10.5, 12.5, 0.75), (0.0, 0.0, 0.375), mats["secondary"], cfg, "grounded_stone_foundation")
    core.add_box(objects, "FOURSQUARE_RedBrickBody", (10.3, 12.3, 5.7), (0.0, 0.0, 3.55), mats["primary"], cfg, "complete_two_storey_brick_body")
    levels = [2.05, 5.05]
    add_window_rows(objects, prefix="FOURSQUARE_FrontSash", xs=[-3.2, 0.0, 3.2], levels=levels, y=-6.22, width=1.35, height=1.75, mats=mats, cfg=cfg)
    for side in (-1, 1):
        for floor, z in enumerate(levels):
            for index, y in enumerate((-3.5, 0.0, 3.5)):
                add_window_x(objects, f"FOURSQUARE_Side_{side:+d}_{floor}_{index}", x=side * 5.22, y=y, centre_z=z, width=1.25, height=1.65, outward=side, mats=mats, cfg=cfg)
    add_hip_roof(objects, "FOURSQUARE_HippedRoof", centre=(0.0, 0.0), width=11.7, depth=13.7, base_z=6.40, rise=2.85, mats=mats, cfg=cfg)
    core.add_box(objects, "FOURSQUARE_FullWidthPorch_Deck", (10.6, 2.25, 0.25), (0.0, -6.65, 0.52), mats["secondary"], cfg, "grounded_full_width_porch")
    core.add_box(objects, "FOURSQUARE_FullWidthPorch_Roof", (11.0, 2.75, 0.24), (0.0, -6.62, 3.08), mats["roof"], cfg, "supported_full_width_porch_roof")
    for index, x in enumerate((-4.3, -2.15, 0.0, 2.15, 4.3)):
        core.add_box(objects, f"FOURSQUARE_PorchColumn_{index}", (0.34, 0.34, 2.45), (x, -7.25, 1.75), mats["white"], cfg, "load_bearing_porch_column")
    add_guard_y(objects, "FOURSQUARE_PorchGuard", x0=-4.5, x1=4.5, y=-7.34, z=0.60, mats=mats, cfg=cfg)
    add_door_y(objects, "FOURSQUARE_CentralDoor", x=0.0, y=-6.26, width=1.10, height=2.25, mats=mats, cfg=cfg)
    core.add_box(objects, "FOURSQUARE_FrontDormer", (2.4, 1.9, 1.45), (0.0, -3.90, 7.25), mats["primary"], cfg, "occupied_front_roof_dormer")
    add_window_y(objects, "FOURSQUARE_DormerSash", x=0.0, y=-4.89, centre_z=7.35, width=1.25, height=1.15, outward=-1, mats=mats, cfg=cfg)
    core.add_box(objects, "FOURSQUARE_SideChimney", (0.78, 1.05, 3.8), (-4.20, 2.2, 6.95), mats["primary"], cfg, "masonry_chimney_with_roof_intersection")
    return objects


def build_montreal_duplex(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    core.add_box(objects, "DUPLEX_StoneBody", (8.8, 11.8, 6.25), (0.0, 0.0, 3.125), mats["primary"], cfg, "complete_two_storey_stone_duplex")
    for side in (-1, 1):
        core.add_box(objects, f"DUPLEX_CantedBay_{side:+d}", (3.1, 0.72, 5.75), (side * 2.25, -6.10, 3.10), mats["primary"], cfg, "shallow_projecting_stone_bay")
        for floor, z in enumerate((1.85, 4.85)):
            add_window_y(objects, f"DUPLEX_BaySash_{side:+d}_{floor}", x=side * 2.25, y=-6.50, centre_z=z, width=1.75, height=1.70, outward=-1, mats=mats, cfg=cfg)
    add_door_y(objects, "DUPLEX_GroundDoor", x=-0.55, y=-5.98, width=0.90, height=2.18, mats=mats, cfg=cfg)
    add_door_y(objects, "DUPLEX_UpperDoor", x=0.75, y=-5.98, width=0.90, height=2.18, mats=mats, cfg=cfg)
    add_stair_x(objects, "DUPLEX_ExteriorStair", x0=-3.9, x1=0.8, y=-6.95, top_z=3.15, mats=mats, cfg=cfg)
    core.add_box(objects, "DUPLEX_UpperLanding", (2.2, 1.7, 0.18), (0.75, -6.72, 3.15), mats["ornament"], cfg, "supported_upper_dwelling_landing")
    add_guard_y(objects, "DUPLEX_UpperLandingGuard", x0=-0.25, x1=1.75, y=-7.50, z=3.16, mats=mats, cfg=cfg)
    for side in (-1, 1):
        for floor, z in enumerate((1.85, 4.85)):
            for index, y in enumerate((-2.8, 1.2, 4.0)):
                add_window_x(objects, f"DUPLEX_Side_{side:+d}_{floor}_{index}", x=side * 4.48, y=y, centre_z=z, width=1.20, height=1.55, outward=side, mats=mats, cfg=cfg)
    add_flat_roof(objects, "DUPLEX_FlatCornicedRoof", width=9.2, depth=12.2, z=6.25, mats=mats, cfg=cfg, parapet=0.72)
    core.add_box(objects, "DUPLEX_FrontCornice", (9.5, 0.50, 0.36), (0.0, -6.20, 6.35), mats["secondary"], cfg, "deep_stone_front_cornice")
    return objects


def build_victorian_rowhouse(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    unit = 5.5
    for index in range(4):
        x = -8.25 + index * unit
        core.add_box(objects, f"ROWHOUSE_Dwelling_{index}", (5.35, 11.8, 6.45), (x, 0.0, 3.225), mats["primary"], cfg, "complete_repeatable_rowhouse_dwelling")
        core.add_box(objects, f"ROWHOUSE_PartyPier_{index}", (0.32, 12.2, 7.0), (x - unit / 2, 0.0, 3.5), mats["primary"], cfg, "continuous_party_wall_pier")
        for floor, z in enumerate((2.0, 5.0)):
            for bay, offset in enumerate((-1.45, 1.45)):
                add_window_y(objects, f"ROWHOUSE_Sash_{index}_{floor}_{bay}", x=x + offset, y=-5.98, centre_z=z, width=1.15, height=1.65, outward=-1, mats=mats, cfg=cfg)
        add_door_y(objects, f"ROWHOUSE_Door_{index}", x=x, y=-6.0, width=0.95, height=2.2, mats=mats, cfg=cfg)
        for step in range(4):
            core.add_box(objects, f"ROWHOUSE_Stoop_{index}_{step}", (1.55, 0.42, 0.16 * (step + 1)), (x, -7.05 + step * 0.34, 0.08 * (step + 1)), mats["secondary"], cfg, "individual_grounded_rowhouse_stoop")
        if index % 2 == 0:
            add_gable_roof(objects, f"ROWHOUSE_Gable_{index}", centre=(x, 0.0), width=5.5, depth=12.4, base_z=6.50, rise=2.1, mats=mats, cfg=cfg)
        else:
            add_flat_roof(objects, f"ROWHOUSE_ParapetRoof_{index}", width=5.5, depth=12.0, z=6.45, mats=mats, cfg=cfg, parapet=0.72, centre=(x, 0.0))
    core.add_box(objects, "ROWHOUSE_TerraceStreetwall", (22.2, 0.36, 0.42), (0.0, -6.06, 6.38), mats["secondary"], cfg, "continuous_terrace_cornice")
    return objects


def build_new_law_tenement(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    core.add_box(objects, "TENEMENT_BrickCornerBlock", (23.6, 19.6, 17.1), (0.0, 0.0, 8.55), mats["primary"], cfg, "complete_five_storey_corner_block")
    tenant_width = 5.5
    for tenant in range(4):
        x = -8.25 + tenant * tenant_width
        add_storefront_y(objects, f"TENEMENT_GroundStorefront_{tenant}", centre_x=x, width=5.0, y=-9.88, height=2.85, mats=mats, cfg=cfg)
        core.add_box(objects, f"TENEMENT_StorefrontSpandrel_{tenant}", (5.1, 0.32, 0.62), (x, -9.96, 3.36), mats["frame"], cfg, "retail_spandrel_band")
    levels = [5.0, 8.15, 11.30, 14.45]
    add_window_rows(objects, prefix="TENEMENT_FrontSash", xs=[-9.4, -6.2, -3.1, 0.0, 3.1, 6.2, 9.4], levels=levels, y=-9.90, width=1.35, height=1.85, mats=mats, cfg=cfg)
    for floor, z in enumerate(levels):
        for bay, y in enumerate((-7.0, -3.5, 0.0, 3.5, 7.0)):
            add_window_x(objects, f"TENEMENT_SideSash_{floor}_{bay}", x=11.90, y=y, centre_z=z, width=1.35, height=1.85, outward=1, mats=mats, cfg=cfg)
    add_fire_escape(objects, "TENEMENT_CastIronFireEscape", x=4.7, y=-10.55, floors=5, floor_height=3.15, mats=mats, cfg=cfg)
    add_fire_escape(objects, "TENEMENT_SideFireEscape", x=11.95, y=3.0, floors=5, floor_height=3.15, mats=mats, cfg=cfg)
    add_flat_roof(objects, "TENEMENT_BuiltUpRoof", width=24.0, depth=20.0, z=17.1, mats=mats, cfg=cfg, parapet=0.78)
    core.add_box(objects, "TENEMENT_DeepBracketedCornice", (24.4, 0.68, 0.85), (0.0, -10.08, 17.0), mats["secondary"], cfg, "deep_bracketed_street_cornice")
    for index in range(13):
        core.add_box(objects, f"TENEMENT_CorniceBracket_{index}", (0.28, 0.72, 0.52), (-11.0 + index * 1.83, -10.28, 16.55), mats["secondary"], cfg, "individual_masonry_cornice_bracket")
    return objects


def add_storefront_x(
    objects: list[bpy.types.Object],
    prefix: str,
    *,
    centre_y: float,
    width: float,
    x: float,
    height: float,
    mats: dict,
    cfg: dict,
    outward: int = 1,
) -> None:
    core.add_box(objects, prefix + "_OccupiedShop", (0.10, width - 0.25, height - 0.20), (x - outward * 0.42, centre_y, height / 2 + 0.20), mats["interior"], cfg, "deep_occupied_shop_interior")
    core.add_box(objects, prefix + "_Glass", (0.08, width - 0.18, height - 0.14), (x + outward * 0.03, centre_y, height / 2 + 0.20), mats["glass"], cfg, "clear_physical_storefront_glass")
    for index in range(5):
        y = centre_y - width / 2 + width * index / 4
        core.add_box(objects, f"{prefix}_Mullion_{index}", (0.18, 0.10, height), (x + outward * 0.10, y, height / 2 + 0.20), mats["frame"], cfg, "storefront_mullion")
    core.add_box(objects, prefix + "_Head", (0.22, width + 0.15, 0.16), (x + outward * 0.10, centre_y, height + 0.22), mats["frame"], cfg, "storefront_head")


def build_midcentury_balcony_tower(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    core.add_box(objects, "TOWER_RetailPodium", (21.5, 21.5, 3.45), (0.0, 0.0, 1.725), mats["secondary"], cfg, "transparent_neighbourhood_retail_podium")
    add_storefront_y(objects, "TOWER_GroundRetail", centre_x=0.0, width=17.5, y=-10.84, height=2.75, mats=mats, cfg=cfg)
    core.add_box(objects, "TOWER_OccupiedApartmentCore", (16.8, 16.8, 31.5), (0.0, 0.0, 19.20), mats["interior"], cfg, "complete_occupied_apartment_core")
    floor_height = 3.15
    for floor in range(10):
        z = 3.45 + floor * floor_height
        core.add_box(objects, f"TOWER_ContinuousBalconySlab_{floor}", (19.8, 19.8, 0.22), (0.0, 0.0, z), mats["primary"], cfg, "continuous_wraparound_balcony_slab")
        for side, y in (("Front", -9.72), ("Rear", 9.72)):
            core.add_box(objects, f"TOWER_{side}GlassGuard_{floor}", (18.8, 0.07, 0.90), (0.0, y, z + 0.58), mats["glass"], cfg, "physical_balcony_glass_guard")
            core.add_box(objects, f"TOWER_{side}GuardRail_{floor}", (18.8, 0.10, 0.10), (0.0, y, z + 1.05), mats["frame"], cfg, "continuous_balcony_top_rail")
        for side, x in (("Left", -9.72), ("Right", 9.72)):
            core.add_box(objects, f"TOWER_{side}GlassGuard_{floor}", (0.07, 18.8, 0.90), (x, 0.0, z + 0.58), mats["glass"], cfg, "physical_balcony_glass_guard")
        for bay, x in enumerate((-6.2, -2.1, 2.1, 6.2)):
            add_window_y(objects, f"TOWER_FrontApartment_{floor}_{bay}", x=x, y=-8.48, centre_z=z + 1.58, width=3.35, height=2.55, outward=-1, mats=mats, cfg=cfg, divisions=2)
        # Brick planters and live planting make the repeating slab inhabited.
        for planter, x in enumerate((-6.6, 6.6)):
            core.add_box(objects, f"TOWER_Planter_{floor}_{planter}", (3.1, 0.75, 0.52), (x, -9.25, z + 0.37), mats["secondary"], cfg, "integrated_balcony_planter")
            core.add_box(objects, f"TOWER_Planting_{floor}_{planter}", (2.65, 0.52, 0.38), (x, -9.25, z + 0.79), mats["plant"], cfg, "balcony_planting")
        if floor % 2 == 0:
            for row in range(7):
                for column in range(3):
                    core.add_box(objects, f"TOWER_BreezeBlockScreen_{floor}_{row}_{column}", (0.36, 0.24, 0.36), (-8.72 + column * 0.58, -9.05, z + 0.62 + row * 0.40), mats["ornament"], cfg, "real_gap_perforated_breeze_block")
    top_z = 3.45 + 10 * floor_height
    add_flat_roof(objects, "TOWER_RoofCanopy", width=19.2, depth=19.2, z=top_z, mats=mats, cfg=cfg, parapet=0.60)
    for x in (-7.8, -2.6, 2.6, 7.8):
        core.add_box(objects, f"TOWER_RoofPergolaPost_{x:+.1f}", (0.18, 0.18, 2.3), (x, -6.0, top_z + 1.65), mats["frame"], cfg, "grounded_rooftop_pergola_post")
    core.add_box(objects, "TOWER_RoofPergola", (17.0, 5.0, 0.20), (0.0, -6.0, top_z + 2.82), mats["roof"], cfg, "supported_rooftop_pergola")
    return objects


def build_classic_strip_mall(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    core.add_box(objects, "STRIP_OccupiedRetailBar", (59.0, 17.2, 4.8), (0.0, 0.0, 2.4), mats["primary"], cfg, "complete_one_storey_retail_bar")
    tenant_width = 9.1
    for tenant in range(6):
        x = -22.75 + tenant * tenant_width
        core.add_box(objects, f"STRIP_BrickPier_{tenant}", (0.78, 0.65, 4.35), (x - tenant_width / 2, -8.72, 2.18), mats["secondary"], cfg, "grounded_brick_tenant_pier")
        add_storefront_y(objects, f"STRIP_TenantStorefront_{tenant}", centre_x=x, width=8.25, y=-8.66, height=3.2, mats=mats, cfg=cfg)
        core.add_box(objects, f"STRIP_TenantSignPanel_{tenant}", (7.8, 0.28, 0.75), (x, -8.86, 4.18), mats["ornament" if tenant % 2 else "secondary"], cfg, "blank_replaceable_tenant_sign_panel")
    core.add_box(objects, "STRIP_ContinuousTenantCanopy", (58.2, 1.15, 0.24), (0.0, -9.18, 3.42), mats["roof"], cfg, "continuous_supported_retail_canopy")
    for index in range(13):
        core.add_box(objects, f"STRIP_CanopyPost_{index}", (0.16, 0.16, 3.15), (-27.0 + index * 4.5, -9.48, 1.58), mats["frame"], cfg, "grounded_canopy_post")
    core.add_box(objects, "STRIP_AnchorTower", (10.2, 17.6, 6.3), (-24.0, 0.0, 3.15), mats["primary"], cfg, "taller_anchor_store_tower")
    core.add_box(objects, "STRIP_AnchorSignPanel", (8.4, 0.30, 1.0), (-24.0, -8.96, 5.25), mats["secondary"], cfg, "blank_anchor_store_sign_panel")
    add_flat_roof(objects, "STRIP_MembraneRoof", width=59.5, depth=17.6, z=4.8, mats=mats, cfg=cfg, parapet=1.05)
    return objects


def build_corner_bodega(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    core.add_box(objects, "BODEGA_BrickCornerBody", (15.6, 17.6, 13.0), (0.0, 0.0, 6.5), mats["primary"], cfg, "complete_four_storey_corner_mixed_use_block")
    add_storefront_y(objects, "BODEGA_WraparoundStorefront_Front", centre_x=0.0, width=14.5, y=-8.88, height=3.05, mats=mats, cfg=cfg)
    add_storefront_x(objects, "BODEGA_WraparoundStorefront_Side", centre_y=-0.3, width=16.0, x=7.88, height=3.05, mats=mats, cfg=cfg)
    core.add_box(objects, "BODEGA_GreenStorefrontFront", (15.2, 0.40, 3.75), (0.0, -9.00, 1.90), mats["secondary"], cfg, "weathered_green_storefront_surround")
    core.add_box(objects, "BODEGA_GreenStorefrontSide", (0.40, 17.0, 3.75), (8.00, 0.0, 1.90), mats["secondary"], cfg, "weathered_green_storefront_surround")
    # Restore clear glass in front of the continuous green surround.
    add_storefront_y(objects, "BODEGA_FrontGlassLayer", centre_x=0.0, width=14.0, y=-9.24, height=2.70, mats=mats, cfg=cfg)
    add_storefront_x(objects, "BODEGA_SideGlassLayer", centre_y=-0.3, width=15.5, x=8.24, height=2.70, mats=mats, cfg=cfg)
    core.add_box(objects, "BODEGA_CornerAwningFront", (15.2, 1.35, 0.18), (0.0, -9.60, 3.52), mats["secondary"], cfg, "supported_wraparound_bodega_awning")
    core.add_box(objects, "BODEGA_CornerAwningSide", (1.35, 17.0, 0.18), (8.60, 0.0, 3.52), mats["secondary"], cfg, "supported_wraparound_bodega_awning")
    levels = [5.15, 8.30, 11.45]
    add_window_rows(objects, prefix="BODEGA_FrontApartmentSash", xs=[-5.3, -1.8, 1.8, 5.3], levels=levels, y=-8.90, width=1.35, height=1.78, mats=mats, cfg=cfg)
    for floor, z in enumerate(levels):
        for bay, y in enumerate((-6.2, -2.2, 2.2, 6.2)):
            add_window_x(objects, f"BODEGA_SideApartmentSash_{floor}_{bay}", x=7.90, y=y, centre_z=z, width=1.35, height=1.78, outward=1, mats=mats, cfg=cfg)
    add_fire_escape(objects, "BODEGA_FireEscape", x=3.2, y=-9.55, floors=4, floor_height=3.15, mats=mats, cfg=cfg)
    add_flat_roof(objects, "BODEGA_BuiltUpRoof", width=16.0, depth=18.0, z=13.0, mats=mats, cfg=cfg, parapet=0.78)
    core.add_box(objects, "BODEGA_TurningMasonryCornice", (16.4, 0.58, 0.70), (0.0, -9.08, 12.85), mats["ornament"], cfg, "turning_bracketed_masonry_cornice")
    core.add_box(objects, "BODEGA_SideMasonryCornice", (0.58, 18.4, 0.70), (8.08, 0.0, 12.85), mats["ornament"], cfg, "turning_bracketed_masonry_cornice")
    return objects


def build_tilt_up_industrial(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    core.add_box(objects, "INDUSTRIAL_TiltUpPanelField", (59.0, 34.0, 9.2), (0.0, 0.0, 4.6), mats["primary"], cfg, "complete_tilt_up_concrete_envelope")
    core.add_box(objects, "INDUSTRIAL_ExposedAggregateBase", (59.4, 34.4, 1.0), (0.0, 0.0, 0.5), mats["secondary"], cfg, "grounded_exposed_aggregate_base")
    for joint in range(11):
        x = -29.0 + joint * 5.8
        core.add_box(objects, f"INDUSTRIAL_PanelJoint_{joint}", (0.07, 0.08, 8.0), (x, -17.06, 5.0), mats["dark"], cfg, "real_tilt_up_panel_joint")
        for row in range(3):
            core.add_cylinder(objects, f"INDUSTRIAL_TieHole_{joint}_{row}", 0.09, 0.08, (x + 1.7, -17.12, 2.2 + row * 2.2), mats["dark"], cfg, "tilt_up_form_tie_recess", vertices=12)
    core.add_box(objects, "INDUSTRIAL_RecessedOffice", (17.5, 1.4, 7.0), (-18.5, -17.25, 3.75), mats["secondary"], cfg, "recessed_two_level_office_entry")
    add_storefront_y(objects, "INDUSTRIAL_OfficeGroundGlass", centre_x=-18.5, width=14.5, y=-18.02, height=2.75, mats=mats, cfg=cfg)
    add_window_rows(objects, prefix="INDUSTRIAL_OfficeRibbon", xs=[-24.0, -20.3, -16.6, -12.9], levels=[5.5], y=-18.02, width=3.0, height=1.45, mats=mats, cfg=cfg, divisions=3)
    core.add_box(objects, "INDUSTRIAL_OfficeCanopy", (17.0, 2.2, 0.24), (-18.5, -18.4, 3.45), mats["ornament"], cfg, "supported_office_entry_canopy")
    for door in range(4):
        x = 5.5 + door * 6.0
        core.add_box(objects, f"INDUSTRIAL_LoadingDoorVoid_{door}", (4.5, 0.30, 4.8), (x, -17.18, 2.7), mats["dark"], cfg, "deep_loading_door_void")
        for segment in range(6):
            core.add_box(objects, f"INDUSTRIAL_LoadingDoor_{door}_Panel_{segment}", (4.1, 0.15, 0.68), (x, -17.38, 0.72 + segment * 0.72), mats["ornament"], cfg, "sectional_loading_door_panel")
        core.add_box(objects, f"INDUSTRIAL_LoadingCanopy_{door}", (5.0, 1.4, 0.18), (x, -18.0, 5.35), mats["roof"], cfg, "supported_loading_dock_canopy")
        for bollard in (-1, 1):
            core.add_cylinder(objects, f"INDUSTRIAL_Bollard_{door}_{bollard:+d}", 0.12, 1.15, (x + bollard * 2.1, -18.05, 0.575), mats["ornament"], cfg, "grounded_loading_bollard", vertices=12)
    add_flat_roof(objects, "INDUSTRIAL_MembraneRoof", width=59.5, depth=34.5, z=9.2, mats=mats, cfg=cfg, parapet=0.62)
    for unit, x in enumerate((-10.0, 4.0, 18.0)):
        core.add_box(objects, f"INDUSTRIAL_RoofMechanical_{unit}", (5.0, 3.5, 1.5), (x, 4.0, 10.05), mats["ornament"], cfg, "screened_rooftop_mechanical_unit")
    return objects


def build_provincial_brick_school(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    # Two classroom wings and a rear connector create a real open entry court.
    for side in (-1, 1):
        x = side * 13.8
        core.add_box(objects, f"SCHOOL_ClassroomWing_{side:+d}", (11.8, 27.0, 10.8), (x, 0.5, 5.4), mats["primary"], cfg, "complete_three_storey_classroom_wing")
        core.add_box(objects, f"SCHOOL_StoneBase_{side:+d}", (12.1, 27.3, 1.15), (x, 0.5, 0.575), mats["secondary"], cfg, "grounded_school_stone_base")
        for band in (3.55, 7.1, 10.55):
            core.add_box(objects, f"SCHOOL_FloorBand_{side:+d}_{band:.2f}", (12.2, 27.4, 0.22), (x, 0.5, band), mats["secondary"], cfg, "continuous_school_floor_band")
        for floor, z in enumerate((2.1, 5.65, 9.15)):
            for bay, bx in enumerate((x - 3.8, x, x + 3.8)):
                add_window_y(objects, f"SCHOOL_FrontClassroom_{side:+d}_{floor}_{bay}", x=bx, y=-13.10, centre_z=z, width=2.65, height=2.0, outward=-1, mats=mats, cfg=cfg, divisions=3)
        add_hip_roof(objects, f"SCHOOL_WingRoof_{side:+d}", centre=(x, 0.5), width=13.0, depth=28.2, base_z=10.85, rise=2.65, mats=mats, cfg=cfg)
    core.add_box(objects, "SCHOOL_RearConnector", (16.0, 10.0, 10.8), (0.0, 8.8, 5.4), mats["primary"], cfg, "occupied_rear_classroom_connector")
    for floor, z in enumerate((2.1, 5.65, 9.15)):
        for bay, x in enumerate((-5.5, -1.8, 1.8, 5.5)):
            add_window_y(objects, f"SCHOOL_RearConnectorWindow_{floor}_{bay}", x=x, y=3.72, centre_z=z, width=2.45, height=1.95, outward=-1, mats=mats, cfg=cfg, divisions=3)
    core.add_box(objects, "SCHOOL_CourtyardBridge", (15.5, 3.2, 3.55), (0.0, -10.8, 8.9), mats["primary"], cfg, "occupied_bridge_over_open_school_gateway")
    core.add_box(objects, "SCHOOL_OpenGateway", (9.0, 4.0, 5.6), (0.0, -10.9, 2.8), mats["dark"], cfg, "real_open_arched_school_gateway")
    # Physical stone piers and an arch-like head preserve the open threshold.
    for side in (-1, 1):
        core.add_box(objects, f"SCHOOL_GatewayPier_{side:+d}", (1.1, 4.3, 5.8), (side * 4.8, -10.9, 2.9), mats["secondary"], cfg, "load_bearing_gateway_pier")
    core.add_box(objects, "SCHOOL_GatewayHead", (10.6, 4.3, 1.0), (0.0, -10.9, 5.45), mats["secondary"], cfg, "supported_gateway_arch_head")
    core.add_box(objects, "SCHOOL_ClockTower", (5.2, 5.2, 7.0), (0.0, 6.8, 14.3), mats["secondary"], cfg, "modest_grounded_school_clock_tower")
    for side in (-1, 1):
        core.add_box(objects, f"SCHOOL_ClockFace_{side:+d}", (2.2, 0.15, 2.2), (0.0, 4.12 if side < 0 else 9.48, 15.2), mats["ornament"], cfg, "physical_clock_face")
    add_hip_roof(objects, "SCHOOL_ClockTowerRoof", centre=(0.0, 6.8), width=6.4, depth=6.4, base_z=17.8, rise=2.6, mats=mats, cfg=cfg)
    core.add_cylinder(objects, "SCHOOL_BellCupola", 1.05, 2.2, (0.0, 6.8, 21.0), mats["ornament"], cfg, "open_bell_cupola", vertices=20)
    return objects


def build_assembled(mats: dict, cfg: dict) -> list[bpy.types.Object]:
    return {
        "craftsman_bungalow": build_craftsman_bungalow,
        "edwardian_foursquare": build_edwardian_foursquare,
        "montreal_duplex": build_montreal_duplex,
        "victorian_rowhouse": build_victorian_rowhouse,
        "new_law_tenement": build_new_law_tenement,
        "midcentury_balcony_tower": build_midcentury_balcony_tower,
        "classic_strip_mall": build_classic_strip_mall,
        "corner_bodega": build_corner_bodega,
        "tilt_up_industrial": build_tilt_up_industrial,
        "provincial_brick_school": build_provincial_brick_school,
    }[cfg["shape"]](mats, cfg)


def build_module(role: str, variant: str, mats: dict, cfg: dict) -> tuple[list[bpy.types.Object], float]:
    objects: list[bpy.types.Object] = []
    width = min(max(cfg["native"][0] * 0.55, 5.0), 18.0)
    depth = min(max(cfg["native"][1] * 0.68, 6.0), 20.0)
    if role == "podium":
        height = cfg["podium_height"]
        core.add_box(objects, "MODULE_GroundedPlinth", (width, depth, 0.30), (0.0, 0.0, 0.15), mats["secondary"], cfg, "complete_grounded_podium_plinth", role=role)
        core.add_box(objects, "MODULE_OccupiedPodium", (width - 0.35, depth - 0.35, height - 0.30), (0.0, 0.10, 0.30 + (height - 0.30) / 2), mats["primary"], cfg, "complete_occupied_podium_bay", role=role)
        if cfg["development_type"] in {"retail_commercial", "mixed_use_neighbourhood"}:
            add_storefront_y(objects, "MODULE_PublicStorefront", centre_x=0.0, width=width - 0.8, y=-depth / 2 - 0.04, height=max(2.2, height - 0.75), mats=mats, cfg=cfg, role=role)
        else:
            add_door_y(objects, "MODULE_GroundedEntry", x=0.0, y=-depth / 2 - 0.04, width=1.05, height=min(2.35, height - 0.35), mats=mats, cfg=cfg, role=role)
    elif role == "floor":
        height = cfg["floor_height"]
        phase = {"typical_a": 0, "typical_b": 1, "typical_c": 2}[variant]
        core.add_box(objects, f"MODULE_OccupiedBay_{variant}", (width, depth, height), (0.0, 0.0, height / 2), mats["primary"], cfg, "repeatable_complete_occupied_construction_bay", role=role)
        bay_count = 2 + phase
        xs = [(-width * 0.36 + index * width * 0.72 / max(1, bay_count - 1)) for index in range(bay_count)]
        for index, x in enumerate(xs):
            add_window_y(objects, f"MODULE_FrontWindow_{variant}_{index}", x=x, y=-depth / 2 - 0.04, centre_z=height * 0.53, width=min(1.45, width / (bay_count + 1)), height=max(1.1, height - 0.85), outward=-1, mats=mats, cfg=cfg, role=role)
            add_window_y(objects, f"MODULE_RearWindow_{variant}_{index}", x=x, y=depth / 2 + 0.04, centre_z=height * 0.53, width=min(1.45, width / (bay_count + 1)), height=max(1.1, height - 0.85), outward=1, mats=mats, cfg=cfg, role=role)
    elif role == "crown":
        height = max(0.45, cfg["crown_height"])
        core.add_box(objects, "MODULE_CrownTransition", (width, depth, height), (0.0, 0.0, height / 2), mats["secondary"], cfg, "fixed_complete_crown_transition", role=role)
        for index in range(7):
            core.add_box(objects, f"MODULE_CrownBracket_{index}", (0.20, 0.35, height * 0.62), (-width * 0.42 + index * width * 0.14, -depth / 2 - 0.12, height * 0.35), mats["ornament"], cfg, "individual_crown_bracket", role=role)
    else:
        height = max(0.55, cfg["roof_height"])
        if cfg["shape"] in {"craftsman_bungalow", "edwardian_foursquare", "victorian_rowhouse", "provincial_brick_school"}:
            add_gable_roof(objects, "MODULE_FixedPitchedRoof", centre=(0.0, 0.0), width=width, depth=depth, base_z=0.0, rise=height, mats=mats, cfg=cfg, role=role)
        else:
            add_flat_roof(objects, "MODULE_FixedFlatRoof", width=width, depth=depth, z=0.0, mats=mats, cfg=cfg, parapet=min(0.7, height), role=role)
    for marker in core.module_contract_markers(role, variant, height):
        objects.append(core.tag_object(marker, "four_elevation_material_contract", cfg, role=role))
    return objects, height


def footprint_contract(cfg: dict) -> dict:
    width, depth, _height = cfg["native"]
    detached = cfg["development_type"] == "residential_single_family"
    scale_min, scale_max, axis = (0.78, 1.24, 1.18) if detached else (0.62, 1.40, 1.30)
    bay = round(width / (4 if detached else 6), 2)
    rectangle = {
        "recommendedWidth_m": [round(width * scale_min, 1), round(width * scale_max, 1)],
        "recommendedDepth_m": [round(depth * scale_min, 1), round(depth * scale_max, 1)],
        "recommendedFloors": [cfg["min_floors"], cfg["max_floors"]],
        "scaleMin": scale_min,
        "scaleMax": scale_max,
        "maxAxisRatio": axis,
        "preferredBayMultiple_m": bay,
    }
    return {
        "preferredProfiles": ["rectangle"],
        "minimumPreferredProfiles": 1,
        "profileRationale": (
            f"The complete commonplace building remains fixed through the {scale_min:.2f}x-{scale_max:.2f}x band. "
            f"Larger drawings repeat complete {bay:.2f} m rooms, dwellings, storefronts, classrooms or industrial panels; "
            "entrances, stairs, corners, roofs and crowns never stretch independently."
        ),
        "fixedLandmarkScaleBand": {"scaleMin": scale_min, "scaleMax": scale_max, "maxAxisRatio": axis},
        **rectangle,
        "profiles": {"rectangle": rectangle},
    }


def massing_graph(cfg: dict) -> dict:
    features = {
        "craftsman_bungalow": ["broad_front_gable", "cross_gabled_supported_porch", "grounded_masonry_base", "divided_residential_sash", "intersecting_masonry_chimney"],
        "edwardian_foursquare": ["compact_two_storey_brick_cube", "deep_hipped_roof", "occupied_front_dormer", "full_width_supported_porch", "stone_trimmed_sash"],
        "montreal_duplex": ["paired_shallow_stone_bays", "two_independent_thresholds", "complete_exterior_steel_stair", "supported_upper_landing", "deep_flat_roof_cornice"],
        "victorian_rowhouse": ["four_complete_dwellings", "continuous_party_wall_piers", "individual_stoops_and_doors", "tall_stone_trimmed_sash", "alternating_gable_and_parapet_roofs"],
        "new_law_tenement": ["complete_corner_retail_base", "four_residential_window_storeys", "two_supported_fire_escape_stacks", "wrapped_secondary_elevation", "deep_bracketed_cornice"],
        "midcentury_balcony_tower": ["continuous_wraparound_balcony_slabs", "physical_clear_guards", "real_gap_breeze_block_screens", "integrated_planted_upstands", "transparent_retail_lobby"],
        "classic_strip_mall": ["six_complete_tenant_bays", "continuous_supported_canopy", "grounded_brick_pier_rhythm", "individual_clear_storefronts", "taller_anchor_store_tower"],
        "corner_bodega": ["wraparound_green_storefront", "supported_corner_awning", "clear_deep_retail_interior", "aligned_upper_residential_sash", "turning_masonry_cornice"],
        "tilt_up_industrial": ["complete_tilt_up_panel_field", "real_panel_joints_and_tie_holes", "recessed_two_level_office", "four_deep_loading_portals", "grounded_canopies_and_bollards"],
        "provincial_brick_school": ["two_complete_classroom_wings", "real_open_entry_court", "occupied_gateway_bridge", "aligned_classroom_window_bands", "modest_clock_and_bell_tower"],
    }[cfg["shape"]]
    return {
        "type": f"fixed_{cfg['shape']}_with_repeatable_complete_common_bays",
        "variant_id": cfg["variant_id"],
        "occupied_storeys": cfg["native_floors"],
        "features": features,
        "physical_window_layers": ["occupied_depth", "physical_pane", "separate_frame", "head_and_sill", "floor_datum", "material_return"],
        "fallback_policy": "fixed identity ends plus repeatable complete room dwelling storefront classroom or industrial-panel bays",
    }


def install_wave16_hooks() -> None:
    core.FAMILIES = FAMILIES
    core.load_palette = load_palette
    core.build_assembled = build_assembled
    core.build_module = build_module
    core.footprint_contract = footprint_contract
    core.massing_graph = massing_graph
    core.view_map = view_map
    # Human comparison approval is mandatory before any catalogue card changes.
    core.promote_catalogue_variant = lambda _folder, _cfg: None


def postprocess_manifest(output_root: Path, cfg: dict) -> None:
    folder = (output_root / cfg["family"]).resolve()
    manifest_path = folder / f"{cfg['family']}_manifest.json"
    if not manifest_path.is_file():
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["generator"] = {
        **(manifest.get("generator") or {}),
        "name": "archetype_compiler/generate_wave16_standard_families.py",
        "version": "1.0.0",
    }
    graph = massing_graph(cfg)
    manifest["generation_tags"] = [
        "wave16", "catalogue_expansion_wave3", "commonplace_standard",
        "existing_catalogue_reference", "fixed_landmark_and_modular_fallback",
        "physical_separate_glazing", "occupied_interior_depth",
        "complete_semantic_bay_repeat", "grounding_normalized_bottom_zero",
        *graph["features"],
    ]
    provenance = manifest.get("source_provenance") or {}
    provenance["method"] = (
        "immutable shipped catalogue card; deterministic material extraction; "
        "shared true-metric construction kits; physical layered glazing; occupied "
        "depth; complete secondary elevations; normalized bottom-centre origin; "
        "fixed whole-building landmark and complete-semantic-bay LEGO fallback"
    )
    provenance["coverage_cohort"] = cfg["cohort"]
    provenance["catalogue_card_preserved"] = True
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
    install_wave16_hooks()
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
