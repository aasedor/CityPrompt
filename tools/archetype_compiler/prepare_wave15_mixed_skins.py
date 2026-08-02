"""Prepare render-locked PBR source packs for Wave 15.

The two source boards for each family are generated with the built-in image
workflow and reviewed before this deterministic pass crops them, derives the
near/far PBR channels, writes the elevation sheet, and records immutable
generation provenance.
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from prepare_wave8_reference_skins import FAMILY_ROOT, prepare_family
from prepare_wave14_variant_skins import bind_atlas, crop_cells, skin_config as _skin_config
import prepare_wave14_variant_skins as wave14_skin
from wave15_mixed_specs import (
    FAMILIES,
    GOALPOST_CELLS,
    MATERIAL_CELLS,
    goalpost_prompt,
    material_prompt,
)


SOURCE_IDS: dict[str, dict[str, str]] = {
    "copenhill-ski-slope-energy-plant": {
        "goalpost": "exec-4b899008-fc8f-4ed5-9b66-4974f08dfbc5",
        "material": "exec-d24b335c-1b45-48a8-bbe3-14a3fcd3a00c",
    },
    "parametric-wave-natatorium": {
        "goalpost": "exec-16e9bc69-a60e-46ae-aa8e-7c600969fdb4",
        "material": "exec-f6ff42f8-0a98-473f-b13d-930d07df1c8a",
    },
    "second-empire-clocktower-city-hall": {
        "goalpost": "exec-0ec332b6-ab78-49e2-bf24-fe334d3d1cab",
        "material": "exec-ca70fae3-ee76-408e-af90-fd70c161f6ef",
    },
    "glass-greenhouse-vertical-farm": {
        "goalpost": "exec-23374c1c-4839-4973-b3df-19258a2171fe",
        "material": "exec-8f8908cd-62a9-417a-9b5a-91b436b69b17",
    },
    "steel-rib-intermodal-hub": {
        "goalpost": "exec-2f42e799-214c-4c63-9a74-8fafe1460585",
        "material": "exec-9b14bfc2-d936-4e63-b672-4ff89a901a88",
    },
    "monumental-silo-cluster": {
        "goalpost": "exec-229e7e69-0f47-43dd-ab0d-0e2639207a1e",
        "material": "exec-9a2a524b-f19a-41f4-9170-3a223eb86efd",
    },
    "titanium-fold-art-museum": {
        "goalpost": "exec-c5b46865-5a0a-45ae-9025-f3c01990c64d",
        "material": "exec-7d7830ca-1ef6-4713-a3b9-479cc3d22e30",
    },
    "historic-iron-glass-market": {
        "goalpost": "exec-d921390f-aed4-4420-854c-c691f715d44a",
        "material": "exec-3ce0a9e9-f190-4bde-a23a-be5d7d9cf3c1",
    },
    "bronze-curve-concert-hall": {
        "goalpost": "exec-a3d5f104-6996-467a-aff9-7b2744b1e454",
        "material": "exec-40a4a378-c7ba-4745-900e-aad844c02231",
    },
    "deconstructivist-concrete-fire-station": {
        "goalpost": "exec-22cf7123-ae54-4efe-8151-972bcdf0c083",
        "material": "exec-10daa4fb-9205-4352-a914-ede8ee1b52ab",
    },
}


PILOT_GOALPOST_PROMPT = """Use case: photorealistic-natural
Asset type: render-locked four-view architectural construction board for a CityPrompt LEGO building variant
Primary request: Design one coherent, physically buildable Waste-to-Energy Plant - Inhabited Ski Slope from the catalogue contract below and show that exact same building in four equal panels in a precise 2 by 2 grid.
Panel 1: dead-front orthographic elevation, complete building visible. Panel 2: pedestrian-height front-right architectural survey oblique. Panel 3: rear-left oblique proving every material and structural system wraps the secondary elevations. Panel 4: high aerial roof-plan oblique proving roof topology, three slope gradients, public paths, process volumes, and equipment.
Catalogue contract: A monumental silver waste-to-energy plant rises beneath one continuous inhabited green ski slope, climbing from a low public forecourt to a tall industrial summit beside a faceted white emissions stack; a multicolour climbing wall and diagonal aluminum cassette field make the long elevation civic rather than utilitarian.
Building lock: 160 m by 70 m industrial envelope; one uninterrupted skiable roof rises diagonally from the public front edge to the high rear process block; a meandering planted public route and three ski gradients occupy the roof; the long side uses overlapping 1.2 m by 3.3 m aluminum box cassettes and carries an 85 m climbing wall; a glass elevator and separate faceted white emissions stack reach the summit. The slope, building shell, summit, and stack must be integrated construction—not an attached ramp or fantasy mountain.
Scene/backdrop: clean warm-light-grey architectural studio ground and backdrop, no neighbors, trees, cars or people.
Style/medium: premium photoreal architectural survey photography and physically plausible construction reference, not concept art.
Lighting/mood: neutral bright overcast survey illumination with soft contact shadows and controlled glass reflections, consistent in every panel.
Materials/textures: checkerboard brushed and perforated aluminum cassettes; planted and synthetic-turf ski slope with real edge rails; pale exposed concrete process base; graphite industrial steel; neutral high-transmission visitor glazing; warm occupied control-room depth; white ceramic-coated emissions stack and dark service roof.
Constraints: exact same coherent building topology, facade pattern, slope path, stack position, structural bays, openings, entrance, material zones and roof in all four panels; credible load paths; thin neutral gutters; whole building in every frame; no labels, text, signs, logos or watermark.
Avoid: generic factory box, flat green roof, detached ramp, grass pasted on a vertical wall, tiny chimney, blue mirror curtain wall, smoke plume, fantasy mountain, perspective distortion, blank sides, changed geometry between panels, entourage, dramatic sunset."""


PILOT_MATERIAL_PROMPT = """Use case: photorealistic-natural
Asset type: shadow-neutral 3 by 2 construction and occupied-depth material board for the exact Waste-to-Energy Plant - Inhabited Ski Slope shown in Image 1
Input images: Image 1 is the approved four-view geometry, palette, construction-scale and optical authority.
Primary request: Create six equal square straight-on orthographic samples in a precise 3-column by 2-row grid separated only by thin neutral-grey gutters, with no labels.
Top-left: brushed and perforated silver aluminum cassette field using overlapping 1.2 m by 3.3 m box modules, authentic construction scale and fine micro-detail, no facade or opening.
Top-center: green planted ski slope plus pale aggregate public path and synthetic ski surface, authentic construction scale and fine micro-detail, no complete landscape scene.
Top-right: colour-coded climbing holds on dark perforated backing, authentic construction scale and fine micro-detail, no complete climbing-wall elevation.
Bottom-left: graphite industrial structural steel, authentic construction scale and fine micro-detail, no complete frame, door or screen.
Bottom-center: neutral high-transmission visitor and control-room glass plus clean occupied control-room depth seen dead-on, with clear floor, ceiling, sparse warm occupation and process silhouettes, no exterior frame, mullion, screen, facade or skewed perspective.
Bottom-right: white ceramic-coated faceted stack cladding plus charcoal service membrane, authentic construction scale and evenly lit, no complete roof scene.
Scene/backdrop: flat evenly lit material-capture setup. Style/medium: premium physically based photoreal architectural construction texture reference.
Lighting: diffuse neutral overcast capture; no directional sunlight, baked shadow, vignette or perspective.
Constraints: exact 3 by 2 grid; every sample fills its cell edge-to-edge; no labels, text, logos or watermark; no complete facade or repeated window grid; match Image 1 exactly.
Avoid: cartoon materials, generic substitutions, oversized motifs, blue mirror glass, dramatic lighting, building perspective, decorative border."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", choices=sorted(FAMILIES), action="append")
    return parser.parse_args()


def skin_config(family: str) -> dict:
    # Reuse the proven deterministic derivation contract with the Wave 15 data.
    wave14_skin.FAMILIES = FAMILIES
    wave14_skin.GOALPOST_CELLS = GOALPOST_CELLS
    wave14_skin.MATERIAL_CELLS = MATERIAL_CELLS
    return _skin_config(family)


def recorded_goalpost_prompt(family: str) -> str:
    if family == "copenhill-ski-slope-energy-plant":
        return PILOT_GOALPOST_PROMPT
    return goalpost_prompt(family)


def recorded_material_prompt(family: str) -> str:
    if family == "copenhill-ski-slope-energy-plant":
        return PILOT_MATERIAL_PROMPT
    return material_prompt(family)


def write_provenance(family: str) -> None:
    spec = FAMILIES[family]
    source_ids = SOURCE_IDS.get(family)
    if not source_ids or not all(source_ids.get(key) for key in ("goalpost", "material")):
        raise RuntimeError(f"{family}: reviewed source ids have not been recorded")
    source_root = FAMILY_ROOT / family / "textures" / "source"
    config = skin_config(family)
    goal_id = source_ids["goalpost"]
    material_id = source_ids["material"]
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
        "source_mode": "catalogue_contract_to_render_locked_board",
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
                "role": "canonical_four_view_variant_reference_board",
                "prompt": recorded_goalpost_prompt(family),
                "registered_surfaces": config["registered_surfaces"],
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
                "prompt": recorded_material_prompt(family),
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
    crop_cells(source_root, "material-construction-source-v1.png", MATERIAL_CELLS)
    write_provenance(family)
    prepare_family(family, skin_config(family), batch_label="wave15")
    bind_atlas(family)


def main() -> int:
    args = parse_args()
    for family in args.family or sorted(FAMILIES):
        prepare_one(family)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
