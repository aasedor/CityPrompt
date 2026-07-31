"""Prepare the reference-locked PBR package for the wave-shell aquatic centre.

The source pack locks the unequal double-wave roof, cable masts, concrete
branch supports, transparent pool hall, recessed public entry and disciplined
polycarbonate service elevation.  Geometry carries all seams, ribs, mullions,
supports and openings; this adapter deliberately derives only clean material
zones and occupied interior depth.

Run from the repository root:

    python tools/archetype_compiler/prepare_wave10_aquatic_skin.py
"""
from __future__ import annotations

from PIL import Image, ImageOps

from prepare_wave8_reference_skins import FAMILY_ROOT, prepare_family


FAMILY = "parametric-wave-shell-aquatic-centre"
SOURCE_ROOT = FAMILY_ROOT / FAMILY / "textures" / "source"

# The generated plate is an exact 3 x 2 grid with thin neutral gutters.  Trim
# those gutters so they never become repeating light seams in the PBR maps.
MATERIAL_CELLS = {
    "roof-metal-material-source-v1.png": (0.002, 0.003, 0.330, 0.495),
    "timber-material-source-v1.png": (0.336, 0.003, 0.664, 0.495),
    "concrete-material-source-v1.png": (0.670, 0.003, 0.998, 0.495),
    "polycarbonate-material-source-v1.png": (0.002, 0.505, 0.330, 0.997),
    "cobalt-panel-material-source-v1.png": (0.336, 0.505, 0.664, 0.997),
    "plinth-material-source-v1.png": (0.670, 0.505, 0.998, 0.997),
}

CONFIG = {
    "archetype_id": "community_recreation_centre",
    "variant_id": "rec_centre_aquatic",
    "skin_schema": "parametric-wave-shell-aquatic-centre-skin@1",
    "elevation_source": "front-elevation-source-v1.png",
    "occupied_depth_source": "pool-occupied-depth-source-v1.png",
    "bands": {
        "facade": (0.010, 0.255, 0.990, 0.825),
        "podium": (0.010, 0.660, 0.990, 0.825),
        "floor_a": (0.010, 0.395, 0.990, 0.710),
        "floor_b": (0.010, 0.290, 0.990, 0.535),
        "crown": (0.010, 0.255, 0.990, 0.405),
        "side": (0.675, 0.350, 0.990, 0.760),
    },
    "prefixes": {
        "facade": "elevation",
        "podium": "podium",
        "floor_a": "pool_glazing",
        "floor_b": "roof_edge",
        "crown": "wave_crown",
        "side": "service_side",
        "interior": "pool_interior",
        "roof_metal": "roof_metal",
        "timber": "timber",
        "concrete": "concrete",
        "polycarbonate": "polycarbonate",
        "cobalt_panel": "cobalt_panel",
        "plinth": "plinth",
        "pool_water": "pool_water",
        "wet_deck": "wet_deck",
        "white_structure": "white_structure",
        "landscape": "landscape",
    },
    "support": {
        "roof_metal": ((181, 187, 193), "metal", 15101),
        "timber": ((185, 127, 70), "wood", 15111),
        "concrete": ((190, 188, 181), "stone", 15121),
        "polycarbonate": ((205, 210, 210), "glass", 15131),
        "cobalt_panel": ((18, 55, 102), "metal", 15141),
        "plinth": ((54, 57, 58), "stone", 15151),
        "pool_water": ((30, 151, 194), "glass", 15161),
        "wet_deck": ((200, 195, 184), "stone", 15171),
        "white_structure": ((225, 226, 222), "metal", 15181),
        "landscape": ((74, 91, 48), "stone", 15191),
    },
    "support_sources": {
        "roof_metal": "roof-metal-material-source-v1.png",
        "timber": "timber-material-source-v1.png",
        "concrete": "concrete-material-source-v1.png",
        "polycarbonate": "polycarbonate-material-source-v1.png",
        "cobalt_panel": "cobalt-panel-material-source-v1.png",
        "plinth": "plinth-material-source-v1.png",
    },
    "registered_surfaces": [
        "eighty_by_fifty_five_metre_single_volume_natatorium",
        "continuous_asymmetrical_double_wave_shell",
        "larger_competition_crest_and_smaller_leisure_crest",
        "deep_glazed_saddle_valley",
        "exactly_two_cable_stay_masts_and_tension_rods",
        "pale_board_formed_diagonal_concrete_branch_supports",
        "standing_seam_platinum_aluminium_roof_skin",
        "deep_honey_timber_soffit_glulam_ribs_and_acoustic_baffles",
        "full_height_low_iron_pool_curtain_wall",
        "fifty_metre_lap_pool_diving_tower_and_spectator_depth",
        "recessed_double_height_public_entry_at_right_third",
        "translucent_ribbed_polycarbonate_service_bays",
        "charcoal_honed_concrete_plinth",
        "restrained_cobalt_microperforated_wet_service_panels",
        "bioswale_forecourt_and_cycle_arrival",
    ],
    "registration": (
        "The canonical, front, aerial and rear sources lock one transparent "
        "single-volume natatorium beneath a continuous unequal double-wave "
        "shell. The competition crest is larger than the leisure crest; their "
        "glazed saddle valley contains the recessed public entry. Exactly two "
        "cable masts, pale diagonal concrete supports, the roof seams, warm "
        "timber underside and the translucent cobalt service elevation remain "
        "consistent on every view."
    ),
    "opening_method": (
        "The competition hall, leisure hall, entry and observation windows "
        "are physical openings with modeled thermally broken mullions, "
        "transoms, perimeter pressure caps, recessed returns and separate "
        "low-iron panes. The rectified occupied-depth source sits behind the "
        "competition curtain wall; the pools, diving tower, wet deck, timber "
        "ribs, spectator gallery and lighting also exist as physical depth."
    ),
    "generic_tiling_allowed": False,
}


def split_material_plate() -> None:
    """Promote clean cells before the shared PBR derivation step."""
    source = ImageOps.exif_transpose(
        Image.open(SOURCE_ROOT / "pbr-material-source-v1.png")
    ).convert("RGB")
    width, height = source.size
    for filename, (x0, y0, x1, y1) in MATERIAL_CELLS.items():
        crop = source.crop(
            (
                round(width * x0),
                round(height * y0),
                round(width * x1),
                round(height * y1),
            )
        )
        crop.save(SOURCE_ROOT / filename, optimize=True)


def main() -> int:
    split_material_plate()
    prepare_family(FAMILY, CONFIG, batch_label="wave10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
