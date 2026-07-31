"""Prepare the reference-locked PBR package for the prairie motor inn.

The source pack fixes one two-storey L-shaped guest-room court, a continuous
exterior gallery, two structurally integrated stairs, a glazed inside-corner
lobby, a shallow hip-roof silhouette, a pool court, and a complete rear service
edge. Projection-clean material samples are extracted from a dedicated 3 x 3
construction plate before the shared reference-skin pipeline derives near/far
PBR channels.

Run from the repository root:

    python tools/archetype_compiler/prepare_wave10_motor_inn_skin.py
"""
from __future__ import annotations

from PIL import Image, ImageOps

from prepare_wave8_reference_skins import FAMILY_ROOT, prepare_family


FAMILY = "prairie-courtyard-motor-inn"
SOURCE_ROOT = FAMILY_ROOT / FAMILY / "textures" / "source"

# The construction source is a clean 3 x 3 plate with narrow gray gutters.
MATERIAL_CELLS = {
    "ivory-stucco-material-source-v1.png": (0.002, 0.002, 0.330, 0.330),
    "russet-brick-material-source-v1.png": (0.337, 0.002, 0.664, 0.330),
    "charcoal-shingle-material-source-v1.png": (0.671, 0.002, 0.998, 0.330),
    "cedar-soffit-material-source-v1.png": (0.002, 0.337, 0.330, 0.664),
    "kelp-door-material-source-v1.png": (0.337, 0.337, 0.664, 0.664),
    "black-steel-material-source-v1.png": (0.671, 0.337, 0.998, 0.664),
    "low-e-glass-material-source-v1.png": (0.002, 0.671, 0.330, 0.998),
    "pale-concrete-material-source-v1.png": (0.337, 0.671, 0.664, 0.998),
    "pool-water-material-source-v1.png": (0.671, 0.671, 0.998, 0.998),
}

CONFIG = {
    "archetype_id": "highway_motor_hotel",
    "variant_id": "hotel_two_storey_motor_inn",
    "skin_schema": "prairie-courtyard-motor-inn-skin@1",
    "elevation_source": "courtyard-elevation-source-v1.png",
    "occupied_depth_source": "guest-window-source-v1.png",
    "bands": {
        "facade": (0.028, 0.260, 0.985, 0.765),
        "podium": (0.028, 0.485, 0.985, 0.765),
        "floor_a": (0.028, 0.395, 0.850, 0.720),
        "floor_b": (0.028, 0.285, 0.850, 0.540),
        "crown": (0.028, 0.235, 0.985, 0.405),
        "side": (0.835, 0.235, 0.985, 0.765),
    },
    "prefixes": {
        "facade": "elevation",
        "podium": "ground_room_band",
        "floor_a": "gallery_room_band_a",
        "floor_b": "gallery_room_band_b",
        "crown": "hip_roof_eave_band",
        "side": "lobby_return",
        "interior": "occupied_guest_room",
        "ivory_stucco": "ivory_stucco",
        "russet_brick": "russet_brick",
        "charcoal_shingles": "charcoal_shingles",
        "cedar_soffit": "cedar_soffit",
        "kelp_door": "kelp_door",
        "black_steel": "black_steel",
        "low_e_glass": "low_e_glass",
        "pale_concrete": "pale_concrete",
        "pool_water": "pool_water",
        "asphalt": "asphalt",
        "room_curtain": "room_curtain",
        "service_metal": "service_metal",
        "landscape_gravel": "landscape_gravel",
        "prairie_planting": "prairie_planting",
        "interior_wood": "interior_wood",
        "warm_light": "warm_light",
    },
    "support": {
        "ivory_stucco": ((211, 202, 187), "stone", 18101),
        "russet_brick": ((127, 62, 42), "brick", 18111),
        "charcoal_shingles": ((47, 49, 50), "stone", 18121),
        "cedar_soffit": ((137, 74, 37), "wood", 18131),
        "kelp_door": ((60, 72, 63), "metal", 18141),
        "black_steel": ((27, 30, 31), "metal", 18151),
        "low_e_glass": ((92, 117, 132), "glass", 18161),
        "pale_concrete": ((188, 184, 176), "stone", 18171),
        "pool_water": ((32, 151, 177), "glass", 18181),
        "asphalt": ((56, 57, 56), "stone", 18191),
        "room_curtain": ((196, 190, 180), "fabric", 18201),
        "service_metal": ((87, 91, 89), "metal", 18211),
        "landscape_gravel": ((122, 109, 88), "stone", 18221),
        "prairie_planting": ((100, 105, 64), "stone", 18231),
        "interior_wood": ((104, 58, 33), "wood", 18241),
        "warm_light": ((246, 174, 92), "metal", 18251),
    },
    "support_sources": {
        "ivory_stucco": "ivory-stucco-material-source-v1.png",
        "russet_brick": "russet-brick-material-source-v1.png",
        "charcoal_shingles": "charcoal-shingle-material-source-v1.png",
        "cedar_soffit": "cedar-soffit-material-source-v1.png",
        "kelp_door": "kelp-door-material-source-v1.png",
        "black_steel": "black-steel-material-source-v1.png",
        "low_e_glass": "low-e-glass-material-source-v1.png",
        "pale_concrete": "pale-concrete-material-source-v1.png",
        "pool_water": "pool-water-material-source-v1.png",
        # Perspective close-ups remain design goalposts, never tiled albedo.
        # Closely related orthographic construction samples supply these zones.
        "service_metal": "black-steel-material-source-v1.png",
        "interior_wood": "cedar-soffit-material-source-v1.png",
    },
    "registered_surfaces": [
        "fifty_six_metre_two_storey_main_guest_wing",
        "thirty_metre_perpendicular_return_guest_wing",
        "shallow_charcoal_hip_roofs_with_deep_cedar_eaves",
        "continuous_one_point_eight_metre_upper_gallery",
        "aligned_black_steel_gallery_columns_and_guardrails",
        "two_structurally_integrated_open_tread_stairs",
        "real_stringers_base_plates_landings_and_handrails",
        "recessed_kelp_green_guest_room_doors",
        "paired_low_e_windows_with_deep_returns",
        "sheer_and_blackout_curtains_behind_separate_panes",
        "modeled_guest_room_beds_headboards_lamps_and_casework",
        "inside_corner_brick_and_glass_lobby",
        "cedar_lined_cantilevered_porte_cochere",
        "modeled_reception_breakfast_room_and_upper_bridge",
        "fenced_rectangular_pool_and_cedar_cabana",
        "quiet_rear_guest_window_schedule",
        "rear_condensers_meter_bank_vents_and_downspouts",
        "screened_two_bin_refuse_and_pool_equipment",
        "parking_court_curb_ramps_drains_and_prairie_planting",
    ],
    "registration": (
        "The canonical, courtyard elevation, aerial, stair, lobby, guest-window "
        "and rear-service sources lock one two-storey L-shaped prairie motor "
        "inn: deep hip roofs, an occupied exterior gallery, two integrated "
        "stairs, a transparent inside-corner lobby and a complete pool/service "
        "court."
    ),
    "opening_method": (
        "Each room bay receives a physical recessed door and a separate paired "
        "low-E glazing assembly with modeled frame, deep stucco return, head "
        "flashing, sill, pane, screen, sheer, blackout curtain and occupied "
        "room depth. Lobby panes use full-depth mullions, vestibule thresholds "
        "and modeled reception/breakfast space."
    ),
    "generic_tiling_allowed": False,
}


def _split_plate(
    source_name: str,
    cells: dict[str, tuple[float, float, float, float]],
) -> None:
    source = ImageOps.exif_transpose(
        Image.open(SOURCE_ROOT / source_name)
    ).convert("RGB")
    width, height = source.size
    for filename, (x0, y0, x1, y1) in cells.items():
        source.crop(
            (
                round(width * x0),
                round(height * y0),
                round(width * x1),
                round(height * y1),
            )
        ).save(SOURCE_ROOT / filename, optimize=True)


def main() -> int:
    _split_plate("material-construction-source-v1.png", MATERIAL_CELLS)
    prepare_family(FAMILY, CONFIG, batch_label="wave10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
