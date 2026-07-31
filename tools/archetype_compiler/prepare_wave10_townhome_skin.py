"""Prepare the reference-locked PBR package for Wave 10 townhomes.

The generated survey views lock the four-home cadence and roof/service
topology.  Dedicated cedar and corrugated-metal captures own true-scale
construction material, while the occupied-depth atlas is only used behind
separate physical low-e panes.

Run from the repository root:

    python tools/archetype_compiler/prepare_wave10_townhome_skin.py
"""
from __future__ import annotations

from prepare_wave8_reference_skins import prepare_family


FAMILY = "rndsqr-cedar-black-townhomes"
CONFIG = {
    "archetype_id": "rndsqr_missing_middle_townhomes",
    "variant_id": "rndsqr_townhome_dark_wood_metal",
    "skin_schema": "rndsqr-cedar-black-townhomes-skin@1",
    "elevation_source": "elevation-source-v1.png",
    "occupied_depth_source": "occupied-depth-source-v1.png",
    "bands": {
        "facade": (0.045, 0.095, 0.955, 0.900),
        "podium": (0.045, 0.610, 0.955, 0.900),
        "floor_a": (0.045, 0.405, 0.955, 0.665),
        "floor_b": (0.045, 0.185, 0.955, 0.445),
        "crown": (0.045, 0.095, 0.955, 0.235),
        "side": (0.060, 0.205, 0.940, 0.785),
    },
    "prefixes": {
        "facade": "elevation",
        "podium": "podium",
        "floor_a": "floor",
        "floor_b": "floor_alt",
        "crown": "crown",
        "side": "side",
        "interior": "interior",
        "cedar": "cedar",
        "metal": "metal",
        "concrete": "concrete",
        "roof": "roof",
        "paving": "paving",
    },
    "support": {
        "cedar": ((177, 112, 50), "wood", 11001),
        "metal": ((42, 43, 44), "metal", 11011),
        "concrete": ((158, 154, 145), "stone", 11021),
        "roof": ((47, 49, 50), "stone", 11031),
        "paving": ((132, 131, 126), "stone", 11041),
    },
    "support_sources": {
        "cedar": "cedar-material-source-v1.png",
        "metal": "charcoal-metal-material-source-v1.png",
    },
    "registered_surfaces": [
        "four_distinct_seven_metre_dwelling_bays",
        "alternating_shallow_front_offsets",
        "charcoal_corrugated_and_cedar_identity_fields",
        "four_deep_individual_entry_recesses",
        "large_residential_picture_windows_with_operable_lites",
        "cedar_privacy_fin_accents",
        "four_private_rooftop_terraces",
        "four_compact_stair_bulkheads",
        "four_lane_loaded_rear_garages",
        "complete_side_returns_and_downpipes",
    ],
    "registration": (
        "The authored goalpost and rectified elevation lock exactly four "
        "three-level ground-oriented homes, alternating charcoal and cedar "
        "identity fields, individual recessed entrances, a coherent residential "
        "window cadence, four private roof terraces, and four stair bulkheads. "
        "The aerial and rear elevation lock the complete 28-by-14-metre volume, "
        "party-wall alignment, drainage, and one lane garage per dwelling."
    ),
    "opening_method": (
        "Every public and rear window, entry door, and garage is a physical "
        "recess with modeled jambs, heads, sills, frames, panes, room cards, and "
        "construction-depth shadow. Clean cedar and metal PBR are applied only "
        "to solid wall geometry; occupied depth is clipped behind separate "
        "neutral low-e glazing."
    ),
    "generic_tiling_allowed": False,
}


def main() -> int:
    prepare_family(FAMILY, CONFIG, batch_label="wave10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
