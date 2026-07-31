"""Prepare the reference-locked PBR package for the Wave 10 fire station.

The source pack fixes the three-bay drive-through plan, integrated training
tower, occupied glazing and planted photovoltaic roof.  This adapter promotes
the material/detail-sheet cells and the two occupied-depth captures into clean
source plates before the shared high-quality PBR builder derives near/far
channel sets.

Run from the repository root:

    python tools/archetype_compiler/prepare_wave10_fire_station_skin.py
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps

from prepare_wave8_reference_skins import FAMILY_ROOT, prepare_family


FAMILY = "modern-fire-station-mass-timber"
SOURCE_ROOT = FAMILY_ROOT / FAMILY / "textures" / "source"

MATERIAL_CELLS = {
    "honey-timber-material-source-v1.png": (0.0, 0.0, 1.0 / 3.0, 0.5),
    # Isolate a continuous column face rather than the full glulam vignette.
    # The broader source cell includes beam junctions which visibly repeat as
    # false blocks when the material is tiled across long structural members.
    "glulam-material-source-v1.png": (0.438, 0.303, 0.523, 0.493),
    "charred-timber-material-source-v1.png": (2.0 / 3.0, 0.0, 1.0, 0.5),
    "board-formed-concrete-source-v1.png": (0.0, 0.5, 1.0 / 3.0, 1.0),
    # Keep these crops within the vegetation and photovoltaic surfaces.  The
    # full source cells also contain section edges, flashings and timber,
    # which should be modeled as geometry rather than baked into the tile.
    "green-roof-material-source-v1.png": (0.36, 0.53, 0.64, 0.67),
    "solar-metal-material-source-v1.png": (0.67, 0.50, 0.995, 0.655),
}

OCCUPIED_CELLS = {
    "apparatus-interior-source-v1.png": (0.0, 0.0, 0.5, 1.0),
    "crew-interior-source-v1.png": (0.5, 0.0, 1.0, 1.0),
}

CONFIG = {
    "archetype_id": "modern_fire_station",
    "variant_id": "fire_mass_timber",
    "skin_schema": "modern-fire-station-mass-timber-skin@1",
    "elevation_source": "front-elevation-source-v1.png",
    "occupied_depth_source": "crew-interior-source-v1.png",
    "bands": {
        "facade": (0.035, 0.115, 0.965, 0.915),
        "podium": (0.035, 0.555, 0.965, 0.915),
        "floor_a": (0.205, 0.330, 0.965, 0.590),
        "floor_b": (0.205, 0.285, 0.965, 0.545),
        "crown": (0.180, 0.165, 0.965, 0.365),
        "side": (0.710, 0.300, 0.965, 0.880),
    },
    "prefixes": {
        "facade": "elevation",
        "podium": "podium",
        "floor_a": "floor",
        "floor_b": "floor_alt",
        "crown": "crown",
        "side": "side",
        "interior": "interior",
        "apparatus": "apparatus",
        "honey_timber": "honey_timber",
        "glulam": "glulam",
        "charred_timber": "charred_timber",
        "concrete": "concrete",
        "green_roof": "green_roof",
        "solar_metal": "solar_metal",
        "paving": "paving",
    },
    "support": {
        "apparatus": ((84, 58, 43), "stone", 13001),
        "honey_timber": ((184, 124, 66), "wood", 13011),
        "glulam": ((190, 132, 74), "wood", 13021),
        "charred_timber": ((31, 31, 29), "wood", 13031),
        "concrete": ((164, 159, 150), "stone", 13041),
        "green_roof": ((78, 91, 48), "stone", 13051),
        "solar_metal": ((42, 49, 59), "metal", 13061),
        "paving": ((145, 143, 136), "stone", 13071),
    },
    "support_sources": {
        "apparatus": "apparatus-interior-source-v1.png",
        "honey_timber": "honey-timber-material-source-v1.png",
        "glulam": "glulam-material-source-v1.png",
        "charred_timber": "charred-timber-material-source-v1.png",
        "concrete": "board-formed-concrete-source-v1.png",
        "green_roof": "green-roof-material-source-v1.png",
        "solar_metal": "solar-metal-material-source-v1.png",
    },
    "registered_surfaces": [
        "forty_by_thirty_five_metre_two_storey_station",
        "exactly_three_drive_through_apparatus_lanes",
        "three_deep_glass_four_fold_front_and_rear_doors",
        "three_physical_red_engines_and_apparatus_hall_depth",
        "integrated_concrete_and_channel_glass_training_tower",
        "real_alternating_stair_flights_and_landings",
        "recessed_honey_glulam_public_entry",
        "occupied_honey_timber_crew_gallery",
        "charred_timber_service_spine",
        "board_formed_concrete_piers_and_apparatus_base",
        "extensive_native_meadow_roof_and_gravel_breaks",
        "two_orderly_photovoltaic_arrays",
        "rear_decontamination_and_service_connections",
    ],
    "registration": (
        "The authored goalpost and rectified elevation lock a forty-metre civic "
        "front with one integrated stair/training tower, one recessed public "
        "entry, exactly three equal transparent apparatus doors and one solid "
        "charred service wing. The aerial and rear sources lock the complete "
        "thirty-five-metre drive-through depth, matching rear doors, planted "
        "roof, photovoltaic arrays, drainage, decontamination and service yard."
    ),
    "opening_method": (
        "Every apparatus door, crew window, public door, service door and "
        "channel-glass tower slot is authored as a wall void with modeled "
        "jambs, heads, sills, thermally broken frames, mullions and separate "
        "physical panes. Apparatus and occupied-dayroom plates sit several "
        "metres or at least half a metre behind the glass; the tower contains "
        "real stair flights and landings behind translucent channel glazing."
    ),
    "generic_tiling_allowed": False,
}


def _split_cells(
    source_name: str,
    destinations: dict[str, tuple[float, float, float, float]],
) -> None:
    source = ImageOps.exif_transpose(
        Image.open(SOURCE_ROOT / source_name)
    ).convert("RGB")
    width, height = source.size
    for filename, (x0, y0, x1, y1) in destinations.items():
        crop = source.crop(
            (
                round(width * x0),
                round(height * y0),
                round(width * x1),
                round(height * y1),
            )
        )
        crop.save(SOURCE_ROOT / filename, optimize=True)


def split_source_sheets() -> None:
    """Promote clean material and occupied-depth cells for PBR derivation."""
    _split_cells("material-construction-source-v1.png", MATERIAL_CELLS)
    _split_cells(
        "glazing-occupied-depth-source-v1.png",
        OCCUPIED_CELLS,
    )


def main() -> int:
    split_source_sheets()
    prepare_family(FAMILY, CONFIG, batch_label="wave10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
