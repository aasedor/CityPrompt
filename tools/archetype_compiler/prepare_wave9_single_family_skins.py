"""Prepare registered PBR packages for the Wave 9 detached houses.

The rectified elevations remain the colour and construction authority. Physical
window, door, balcony, screen, eave, roof, and chimney geometry owns silhouette
and depth; the occupied-depth plates sit only behind real openings.

Run from the repository root:

    python tools/archetype_compiler/prepare_wave9_single_family_skins.py
"""
from __future__ import annotations

import argparse

from prepare_wave8_reference_skins import prepare_family


FAMILIES = {
    "swiss-chalet-residence": {
        "archetype_id": "mountain_alpine_chalet",
        "variant_id": "alpine_swiss_traditional",
        "skin_schema": "swiss-chalet-residence-skin@1",
        "bands": {
            "facade": (0.080, 0.105, 0.930, 0.865),
            "podium": (0.080, 0.595, 0.930, 0.865),
            "floor_a": (0.080, 0.400, 0.930, 0.635),
            "floor_b": (0.080, 0.205, 0.930, 0.445),
            "crown": (0.080, 0.105, 0.930, 0.330),
            "side": (0.120, 0.185, 0.880, 0.790),
        },
        "prefixes": {
            "facade": "elevation",
            "podium": "podium",
            "floor_a": "floor",
            "floor_b": "floor_alt",
            "crown": "crown",
            "side": "side",
            "interior": "interior",
            "stone": "stone",
            "timber": "timber",
            "carved": "carved",
            "roof": "roof",
            "metal": "metal",
            "flower": "flower",
        },
        "support": {
            "stone": ((145, 140, 128), "stone", 9101),
            "timber": ((78, 46, 27), "wood", 9111),
            "carved": ((52, 29, 18), "wood", 9121),
            "roof": ((92, 79, 68), "wood", 9131),
            "metal": ((66, 57, 50), "metal", 9141),
            "flower": ((135, 35, 28), "stone", 9151),
        },
        "support_sources": {
            "timber": "timber-material-source.png",
            "stone": "stone-material-source.png",
            "roof": "roof-material-source.png",
        },
        "registered_surfaces": [
            "three_level_stone_and_timber_body",
            "paired_projecting_front_gables",
            "deep_shingled_eaves_and_exposed_rafters",
            "stacked_carved_timber_balconies",
            "recessed_arched_carved_entrance",
            "room_scale_sash_window_assemblies",
            "painted_folk_art_panels_and_flower_boxes",
            "twin_masonry_chimneys",
        ],
        "registration": (
            "The selected catalogue card fixes the heavy fieldstone ground floor, "
            "two aged-timber upper levels, paired projecting gables, deep eaves, "
            "stacked carved balconies, central arched entrance, folk-art panels, "
            "window-box accents and twin masonry chimneys."
        ),
        "opening_method": (
            "The generator's residential-scale sash schedule and carved arched "
            "door are physical openings. The occupied-depth source is registered "
            "behind those cavities only."
        ),
        "generic_tiling_allowed": False,
    },
    "timber-screen-lanehouse": {
        "archetype_id": "japanese_contemporary_lanehouse",
        "variant_id": "japanese_lane_timber_screen",
        "skin_schema": "timber-screen-lanehouse-skin@1",
        "bands": {
            "facade": (0.130, 0.105, 0.865, 0.892),
            "podium": (0.130, 0.655, 0.865, 0.892),
            "floor_a": (0.130, 0.395, 0.865, 0.675),
            "floor_b": (0.130, 0.145, 0.865, 0.440),
            "crown": (0.130, 0.105, 0.865, 0.235),
            "side": (0.130, 0.145, 0.865, 0.892),
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
        },
        "support": {
            "cedar": ((188, 126, 68), "wood", 9201),
            "metal": ((48, 48, 44), "metal", 9211),
            "concrete": ((142, 139, 130), "stone", 9221),
            "roof": ((66, 65, 60), "metal", 9231),
        },
        "support_sources": {
            "cedar": "cedar-material-source.png",
        },
        "registered_surfaces": [
            "three_level_narrow_lanehouse",
            "continuous_vertical_cedar_privacy_screen",
            "screen_support_rail_datums",
            "occupied_glazing_behind_screen",
            "deeply_recessed_entrance_and_bench",
            "wrapped_side_screen",
            "rooftop_clerestory_light_monitor",
        ],
        "registration": (
            "The selected catalogue card fixes the narrow three-level mass, one "
            "continuous vertical cedar screen over both upper levels and side "
            "return, deep ground entrance/bench recess, dark rails and shallow "
            "rooftop clerestory."
        ),
        "opening_method": (
            "The generator's full-height upper glazing and clerestory panes sit "
            "behind individually modeled cedar battens. The registered occupied-"
            "depth source supplies room variation only behind those layers."
        ),
        "generic_tiling_allowed": False,
    },
    "spanish-colonial-villa": {
        "archetype_id": "mediterranean_villa_estate",
        "variant_id": "med_villa_spanish_colonial",
        "skin_schema": "spanish-colonial-villa-skin@1",
        "bands": {
            "facade": (0.045, 0.060, 0.958, 0.918),
            "podium": (0.045, 0.570, 0.958, 0.918),
            "floor_a": (0.120, 0.335, 0.925, 0.640),
            "floor_b": (0.120, 0.180, 0.925, 0.410),
            "crown": (0.045, 0.060, 0.958, 0.255),
            "side": (0.045, 0.250, 0.958, 0.918),
        },
        "prefixes": {
            "facade": "elevation",
            "podium": "podium",
            "floor_a": "floor",
            "floor_b": "floor_alt",
            "crown": "crown",
            "side": "side",
            "interior": "interior",
            "stucco": "stucco",
            "brick": "brick",
            "roof": "roof",
            "stone": "stone",
            "iron": "iron",
            "timber": "timber",
            "bronze": "bronze",
        },
        "support": {
            "stucco": ((190, 151, 101), "stone", 9301),
            "brick": ((150, 74, 44), "stone", 9311),
            "roof": ((156, 72, 40), "stone", 9321),
            "stone": ((177, 151, 111), "stone", 9331),
            "iron": ((38, 35, 31), "metal", 9341),
            "timber": ((68, 42, 27), "wood", 9351),
            "bronze": ((94, 67, 43), "metal", 9361),
        },
        "support_sources": {
            "stucco": "stucco-material-source.png",
            "brick": "brick-material-source.png",
            "roof": "roof-material-source.png",
            "stone": "stone-material-source.png",
        },
        "registered_surfaces": [
            "three_level_aged_stucco_villa",
            "asymmetrical_left_bell_tower",
            "deep_central_stone_arch_portal",
            "recessed_wood_sash_and_iron_grilles",
            "central_balcony_and_juliet_rails",
            "localized_exposed_brick_construction_zones",
            "low_pitch_terracotta_barrel_tile_roof",
            "physical_bell_and_tower_arches",
        ],
        "registration": (
            "The selected catalogue card fixes the three-level warm-stucco villa, "
            "asymmetrical left bell tower, low terracotta roof, deep central "
            "portal, barred opening rhythm, iron balconies, exposed brick patches "
            "and pale limestone side/base zones."
        ),
        "opening_method": (
            "The generator's recessed timber sash, iron-grille cages, central "
            "portal and tower arches are physical openings. Registered occupied "
            "depth sits behind their panes and dark cavities."
        ),
        "generic_tiling_allowed": False,
    },
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", action="append", choices=sorted(FAMILIES))
    args = parser.parse_args()
    selected = args.family or sorted(FAMILIES)
    for family in selected:
        prepare_family(family, FAMILIES[family], batch_label="wave9")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
