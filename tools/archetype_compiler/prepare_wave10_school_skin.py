"""Prepare the reference-locked PBR package for the Wave 10 school.

The ImageGen design-source package fixes the civic composition, masonry
palette, opening depth and roof topology.  This adapter promotes clean
material quadrants into their own source plates before the shared high-quality
PBR builder derives near/far channel sets.

Run from the repository root:

    python tools/archetype_compiler/prepare_wave10_school_skin.py
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps

from prepare_wave8_reference_skins import FAMILY_ROOT, prepare_family


FAMILY = "ecole-republicaine-third-republic"
SOURCE_ROOT = FAMILY_ROOT / FAMILY / "textures" / "source"

MATERIAL_QUADRANTS = {
    "brick-material-source-v1.png": (0.0, 0.0, 0.5, 0.5),
    "limestone-material-source-v1.png": (0.5, 0.0, 1.0, 0.5),
    "meuliere-material-source-v1.png": (0.0, 0.5, 0.5, 1.0),
    "slate-material-source-v1.png": (0.5, 0.5, 1.0, 1.0),
}

CONFIG = {
    "archetype_id": "ecole_republicaine",
    "variant_id": "ecole-republicaine-third-republic-original",
    "skin_schema": "ecole-republicaine-third-republic-skin@1",
    "elevation_source": "elevation-source-v1.png",
    "occupied_depth_source": "classroom-interior-depth-source-v1.png",
    "bands": {
        "facade": (0.045, 0.175, 0.955, 0.895),
        "podium": (0.045, 0.545, 0.955, 0.895),
        "floor_a": (0.045, 0.520, 0.955, 0.875),
        "floor_b": (0.045, 0.315, 0.955, 0.585),
        "crown": (0.045, 0.175, 0.955, 0.365),
        "side": (0.045, 0.215, 0.955, 0.875),
    },
    "prefixes": {
        "facade": "elevation",
        "podium": "podium",
        "floor_a": "floor",
        "floor_b": "floor_alt",
        "crown": "crown",
        "side": "side",
        "interior": "interior",
        "brick": "brick",
        "limestone": "limestone",
        "meuliere": "meuliere",
        "slate": "slate",
        "zinc": "zinc",
        "green_wood": "green_wood",
        "paving": "paving",
    },
    "support": {
        "brick": ((142, 71, 48), "stone", 12001),
        "limestone": ((210, 196, 170), "stone", 12011),
        "meuliere": ((128, 111, 88), "stone", 12021),
        "slate": ((67, 74, 80), "stone", 12031),
        "zinc": ((98, 108, 111), "metal", 12041),
        "green_wood": ((28, 55, 51), "wood", 12051),
        "paving": ((132, 126, 116), "stone", 12061),
    },
    "support_sources": {
        "brick": "brick-material-source-v1.png",
        "limestone": "limestone-material-source-v1.png",
        "meuliere": "meuliere-material-source-v1.png",
        "slate": "slate-material-source-v1.png",
    },
    "registered_surfaces": [
        "forty_metre_symmetrical_two_storey_school_block",
        "projecting_three_bay_central_civic_pavilion",
        "three_deep_arch_entry_portals",
        "tall_segmental_arch_classroom_window_cadence",
        "red_brown_flemish_bond_brick_fields",
        "cream_limestone_quoins_strings_arches_and_dentils",
        "rough_meuliere_base_wrapped_to_all_elevations",
        "paired_slate_hip_roofs_with_zinc_drainage",
        "central_clock_pavilion_and_pyramidal_cap",
        "four_chimney_stacks_and_four_zinc_dormers",
        "rear_stair_pavilion_and_two_service_canopies",
        "dark_green_divided_timber_windows_with_occupied_depth",
    ],
    "registration": (
        "The authored street goalpost and rectified front elevation lock a "
        "forty-metre, two-storey Jules Ferry-era school: symmetrical classroom "
        "wings, a shallow three-bay civic centre, three separate arched "
        "entrances, tall divided classroom windows, red brick and cream stone "
        "polychromy, and a clock pavilion. The aerial and rear elevation lock "
        "the complete fifteen-metre depth, paired slate hips, chimneys, "
        "dormers, drainage, rear stair bay and schoolyard service doors."
    ),
    "opening_method": (
        "Every classroom window, stair window and entrance is cut into authored "
        "wall strips. Modeled jambs, curved heads, sills, timber frames, "
        "mullions, transoms and separate low-e panes establish real depth; the "
        "occupied source appears only on cards behind that physical glazing."
    ),
    "generic_tiling_allowed": False,
}


def split_material_sources() -> None:
    """Promote the four shadow-neutral material quadrants for PBR derivation."""
    source = ImageOps.exif_transpose(
        Image.open(SOURCE_ROOT / "masonry-material-source-v1.png")
    ).convert("RGB")
    width, height = source.size
    for filename, (x0, y0, x1, y1) in MATERIAL_QUADRANTS.items():
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
    split_material_sources()
    prepare_family(FAMILY, CONFIG, batch_label="wave10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
