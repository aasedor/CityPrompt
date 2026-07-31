"""Prepare the reference-locked PBR package for the Wave 10 courtyard pilot.

The elevation sheet fixes the facade rhythm.  The dedicated buff-brick capture
owns the true-scale construction material so photographed windows are never
painted onto physical walls; occupied depth appears only behind real glazing.

Run from the repository root:

    python tools/archetype_compiler/prepare_wave10_courtyard_skin.py
"""
from __future__ import annotations

from prepare_wave8_reference_skins import prepare_family


FAMILY = "courtyard-family-brick-mews"
CONFIG = {
    "archetype_id": "courtyard_family_housing",
    "variant_id": "courtyard_family_brick_modern",
    "skin_schema": "courtyard-family-brick-mews-skin@1",
    "elevation_source": "elevation-source-v1.png",
    "occupied_depth_source": "occupied-depth-source-v1.png",
    "bands": {
        "facade": (0.045, 0.145, 0.955, 0.895),
        "podium": (0.045, 0.665, 0.955, 0.895),
        "floor_a": (0.045, 0.465, 0.955, 0.685),
        "floor_b": (0.045, 0.275, 0.955, 0.495),
        "crown": (0.045, 0.190, 0.955, 0.325),
        "side": (0.075, 0.285, 0.925, 0.720),
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
        "metal": "metal",
        "roof": "roof",
        "paving": "paving",
        "soffit": "soffit",
    },
    "support": {
        "brick": ((191, 154, 88), "stone", 10001),
        "metal": ((42, 43, 42), "metal", 10011),
        "roof": ((73, 76, 78), "stone", 10021),
        "paving": ((137, 136, 130), "stone", 10031),
        "soffit": ((93, 75, 51), "stone", 10041),
    },
    "support_sources": {
        "brick": "buff-brick-material-source-v1.png",
    },
    "registered_surfaces": [
        "three_occupied_buff_brick_levels",
        "four_wing_open_to_sky_courtyard",
        "deep_through_carriage_passage",
        "grouped_ground_floor_brick_arches",
        "recessed_room_scale_black_windows",
        "black_steel_juliet_balconies",
        "continuous_soldier_course_datums",
        "integrated_bicycle_storage_recesses",
        "connected_dark_pitched_roof_ring",
        "courtyard_elevations_and_hidden_gutters",
    ],
    "registration": (
        "The selected catalogue card and the authored elevation lock three "
        "occupied buff-brick levels, a calm domestic bay rhythm, black Juliet "
        "guards, four grouped ground arches, one deep through-passage and a "
        "dark pitched roof. The aerial and courtyard references lock a complete "
        "four-wing ring around one uninterrupted open-to-sky paved court."
    ),
    "opening_method": (
        "Every window, door, storage arch and carriage passage is a physical "
        "cavity with modeled brick reveals. The clean buff-brick PBR is applied "
        "to construction geometry; registered occupied depth is clipped behind "
        "separate low-e panes only."
    ),
    "generic_tiling_allowed": False,
}


def main() -> int:
    prepare_family(FAMILY, CONFIG, batch_label="wave10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
