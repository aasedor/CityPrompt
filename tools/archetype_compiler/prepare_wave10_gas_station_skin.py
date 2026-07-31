"""Prepare the reference-locked PBR package for the prairie fuel-bar pilot.

The source pack fixes a six-column canopy, exactly three pump islands, one
occupied convenience-store frontage and a complete service/roof plan.  This
adapter splits the clean ImageGen plates into material and occupied-depth
sources, then delegates deterministic near/far PBR derivation to the shared
Wave 8 pipeline.

Run from the repository root:

    python tools/archetype_compiler/prepare_wave10_gas_station_skin.py
"""
from __future__ import annotations

from PIL import Image, ImageOps

from prepare_wave8_reference_skins import FAMILY_ROOT, prepare_family


FAMILY = "prairie-modern-fuel-bar"
SOURCE_ROOT = FAMILY_ROOT / FAMILY / "textures" / "source"

# The material source is a clean 3 x 2 plate with narrow neutral gutters.
MATERIAL_CELLS = {
    "buff-brick-material-source-v1.png": (0.002, 0.003, 0.315, 0.305),
    "charcoal-metal-material-source-v1.png": (0.525, 0.030, 0.645, 0.455),
    "canopy-aluminum-material-source-v1.png": (0.735, 0.050, 0.985, 0.180),
    "timber-soffit-material-source-v1.png": (0.012, 0.690, 0.245, 0.982),
    "storefront-glass-material-source-v1.png": (0.337, 0.506, 0.663, 0.997),
    "forecourt-concrete-material-source-v1.png": (0.675, 0.735, 0.835, 0.985),
}

DETAIL_CELLS = {
    "store-occupied-depth-source-v1.png": (0.105, 0.235, 0.455, 0.805),
    "pump-equipment-source-v1.png": (0.555, 0.175, 0.925, 0.875),
}

CONFIG = {
    "archetype_id": "rural_gas_station",
    "variant_id": "gas_modern_fuel_bar",
    "skin_schema": "prairie-modern-fuel-bar-skin@1",
    "elevation_source": "front-elevation-source-v1.png",
    "occupied_depth_source": "store-occupied-depth-source-v1.png",
    "bands": {
        "facade": (0.205, 0.310, 0.970, 0.790),
        "podium": (0.205, 0.610, 0.970, 0.790),
        "floor_a": (0.205, 0.500, 0.970, 0.735),
        "floor_b": (0.205, 0.405, 0.970, 0.575),
        "crown": (0.110, 0.315, 0.970, 0.440),
        "side": (0.790, 0.390, 0.995, 0.780),
    },
    "prefixes": {
        "facade": "elevation",
        "podium": "store_plinth",
        "floor_a": "storefront_band",
        "floor_b": "store_parapet",
        "crown": "canopy_fascia",
        "side": "service_side",
        "interior": "store_interior",
        "buff_brick": "buff_brick",
        "charcoal_metal": "charcoal_metal",
        "canopy_aluminum": "canopy_aluminum",
        "timber_soffit": "timber_soffit",
        "storefront_glass": "storefront_glass",
        "forecourt_concrete": "forecourt_concrete",
        "burnt_orange": "burnt_orange",
        "pump_equipment": "pump_equipment",
        "stainless": "stainless",
        "black_trim": "black_trim",
        "roof_membrane": "roof_membrane",
        "prairie_planting": "prairie_planting",
    },
    "support": {
        "buff_brick": ((188, 166, 128), "brick", 16101),
        "charcoal_metal": ((37, 42, 46), "metal", 16111),
        "canopy_aluminum": ((224, 226, 225), "metal", 16121),
        "timber_soffit": ((154, 99, 53), "wood", 16131),
        "storefront_glass": ((74, 103, 116), "glass", 16141),
        "forecourt_concrete": ((177, 174, 166), "stone", 16151),
        "burnt_orange": ((182, 62, 31), "metal", 16161),
        "pump_equipment": ((64, 66, 65), "metal", 16171),
        "stainless": ((151, 156, 156), "metal", 16181),
        "black_trim": ((18, 21, 23), "metal", 16191),
        "roof_membrane": ((64, 67, 66), "stone", 16201),
        "prairie_planting": ((111, 102, 64), "stone", 16211),
    },
    "support_sources": {
        "buff_brick": "buff-brick-material-source-v1.png",
        "charcoal_metal": "charcoal-metal-material-source-v1.png",
        "canopy_aluminum": "canopy-aluminum-material-source-v1.png",
        "timber_soffit": "timber-soffit-material-source-v1.png",
        "storefront_glass": "storefront-glass-material-source-v1.png",
        "forecourt_concrete": "forecourt-concrete-material-source-v1.png",
        "pump_equipment": "pump-equipment-source-v1.png",
    },
    "registered_surfaces": [
        "thirty_five_by_thirty_metre_complete_fuel_bar_site",
        "twenty_eight_by_fourteen_metre_thin_flat_canopy",
        "exactly_six_structurally_aligned_charcoal_columns",
        "exactly_three_separate_double_sided_pump_islands",
        "white_aluminium_fascia_with_one_burnt_orange_band",
        "honey_linear_soffit_with_recessed_lighting",
        "twenty_four_metre_buff_brick_and_charcoal_store",
        "deeply_recessed_physical_low_e_storefront",
        "central_automatic_double_door_public_entry",
        "occupied_convenience_store_depth_and_cooler_wall",
        "integrated_blank_sign_blade_and_roadside_pylon",
        "propane_cage_and_rear_service_yard",
        "screened_roof_with_exactly_two_hvac_units",
        "parking_bays_bollards_drains_and_forecourt_joints",
        "native_prairie_bioswale_edge",
    ],
    "registration": (
        "The canonical, front, aerial and rear sources lock one complete rural "
        "fuel-bar site. The broad canopy always has six aligned charcoal "
        "columns and exactly three separate pump islands; the store remains a "
        "24 metre occupied glazed volume with buff-brick end piers, charcoal "
        "parapet, honey soffit and restrained burnt-orange identity band."
    ),
    "opening_method": (
        "The convenience-store facade is a physical recessed curtain wall "
        "with modeled jambs, sill, head, thermally broken frames, separate "
        "low-E panes and automatic entrance doors. The rectified occupied "
        "store source is placed behind those panes; shelves, coolers, ceiling "
        "lights and counter depth are also reinforced with physical geometry."
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
    _split_plate("storefront-pump-detail-source-v1.png", DETAIL_CELLS)
    prepare_family(FAMILY, CONFIG, batch_label="wave10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
