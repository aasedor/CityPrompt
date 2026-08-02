"""Prepare the reference-locked PBR pack for the multifamily Piece 1 pilot."""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from prepare_wave8_reference_skins import FAMILY_ROOT, prepare_family
from prepare_wave14_variant_skins import bind_atlas, crop_cells
from multifamily_piece1_specs import (
    FAMILIES,
    GOALPOST_CELLS,
    MATERIAL_CELLS,
    goalpost_prompt,
    material_prompt,
)


SOURCE_IDS = {
    "contemporary-timber-glass-midrise": {
        "goalpost": "exec-05034d56-f5fe-4829-a16a-b142eb63ca6a",
        "material": "exec-230a3f5f-19fe-4281-9f21-894f272704a2",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", choices=sorted(FAMILIES), action="append")
    return parser.parse_args()


def skin_config(family: str) -> dict:
    spec = FAMILIES[family]
    prefixes = {
        "facade": f"{family}_registered_front",
        "podium": f"{family}_registered_podium",
        "floor_a": f"{family}_registered_floor_a",
        "floor_b": f"{family}_registered_floor_b",
        "crown": f"{family}_registered_setback_crown",
        "side": f"{family}_registered_wrapped_side",
        "interior": f"{family}_occupied_residential_depth",
    }
    support_sources = {
        "primary": "material-a-source-v1.png",
        "secondary": "material-d-source-v1.png",
        "ornament": "material-c-source-v1.png",
        "frame": "material-f-source-v1.png",
        "glass": "occupied-depth-source-v1.png",
        "roof": "material-b-source-v1.png",
    }
    support = {}
    for index, (key, (description, rgb, kind)) in enumerate(spec["palette"].items()):
        prefixes[key] = f"{family}_{key}_{description.replace(' ', '_')}"
        support[key] = (rgb, kind, 17011 + index * 29)
    return {
        "archetype_id": spec["archetype_id"],
        "variant_id": spec["variant_id"],
        "skin_schema": f"{family}-skin@1",
        "elevation_source": "front-elevation-source-v1.png",
        "occupied_depth_source": "occupied-depth-source-v1.png",
        "bands": {
            "facade": (0.075, 0.035, 0.925, 0.965),
            "podium": (0.085, 0.735, 0.915, 0.965),
            "floor_a": (0.095, 0.485, 0.905, 0.755),
            "floor_b": (0.120, 0.245, 0.880, 0.525),
            "crown": (0.175, 0.040, 0.825, 0.300),
            "side": (0.075, 0.245, 0.290, 0.930),
        },
        "prefixes": prefixes,
        "support": support,
        "support_sources": support_sources,
        "registered_surfaces": [
            "complete_six_storey_dead_front_elevation",
            "carved_double_height_central_lobby",
            "continuous_exposed_glulam_load_path",
            "alternating_supported_planted_balconies",
            "setback_sixth_floor_and_communal_terrace",
            "physical_recessed_low_iron_glazing_with_occupied_depth",
            "wrapped_left_right_and_rear_elevations",
            "sedum_pv_deck_gravel_and_drainage_roof_zones",
            "semantic_repeatable_complete_apartment_bays",
        ],
        "registration": (
            "The corrected four-view board locks one exactly six-storey timber-and-glass "
            "mid-rise. The fixed landmark consumes the complete topology; fallback modules "
            "repeat complete glulam apartment bays and never stretch individual panes, "
            "balconies, entrance geometry or roof equipment."
        ),
        "opening_method": (
            "Every residential and lobby opening uses separate occupied depth, physical "
            "low-iron pane, slim graphite frame, timber structural surround, wall return "
            "and floor datum. Balcony slabs, supports, open guards and planters are true "
            "geometry rather than a facade image."
        ),
        "generic_tiling_allowed": False,
    }


def write_provenance(family: str) -> None:
    spec = FAMILIES[family]
    ids = SOURCE_IDS[family]
    config = skin_config(family)
    source_root = FAMILY_ROOT / family / "textures" / "source"
    goal_id = ids["goalpost"]
    material_id = ids["material"]
    payload = {
        "schema": "reference-generation@1",
        "family": family,
        "archetype_id": spec["archetype_id"],
        "variant_id": spec["variant_id"],
        "provider": "OpenAI built-in image generation",
        "model": "gpt-image-2",
        "generated_at": date.today().isoformat(),
        "status": "source-pack-complete",
        "input_paths": [],
        "catalogue_card_path": (
            f"/archetypes/buildings/{spec['catalogue_slug']}/"
            f"variant_{spec['catalogue_variant_index']}.png"
        ),
        "source_mode": "catalogue_contract_to_corrected_render_locked_board",
        "design_lock": {
            "native_envelope_dimensions_m": list(spec["native"]),
            "occupied_storeys": spec["native_floors"],
            "variant_specific_contract": spec["design_lock"],
            "material_zones": spec["material_zones"],
            "glass_profile": spec["glass_profile"],
            "coverage_cohort": spec["cohort"],
        },
        "sources": [
            {
                "file": "archetype-goalpost.png",
                "source_id": goal_id,
                "role": "canonical_corrected_four_view_variant_reference_board",
                "prompt": goalpost_prompt(family),
                "registered_surfaces": config["registered_surfaces"],
                "review_note": "Second-pass correction fixed the board to exactly six occupied levels.",
            },
            *(
                {
                    "file": filename,
                    "source_id": f"{goal_id}:{Path(filename).stem}",
                    "role": f"registered_goalpost_crop:{Path(filename).stem}",
                }
                for filename in GOALPOST_CELLS
            ),
            {
                "file": "material-construction-source-v1.png",
                "source_id": material_id,
                "role": "six_zone_shadow_neutral_variant_material_plate",
                "prompt": material_prompt(family),
            },
            *(
                {
                    "file": filename,
                    "source_id": f"{material_id}:{Path(filename).stem}",
                    "role": f"registered_material_crop:{Path(filename).stem}",
                }
                for filename in MATERIAL_CELLS
            ),
        ],
    }
    (source_root / "reference-generation.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )


def prepare_one(family: str) -> None:
    source_root = FAMILY_ROOT / family / "textures" / "source"
    crop_cells(source_root, "archetype-goalpost.png", GOALPOST_CELLS)
    crop_cells(
        source_root,
        "material-construction-source-v1.png",
        MATERIAL_CELLS,
    )
    write_provenance(family)
    prepare_family(family, skin_config(family), batch_label="multifamily-piece1")
    bind_atlas(family)


def main() -> int:
    args = parse_args()
    for family in args.family or sorted(FAMILIES):
        prepare_one(family)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
