"""Prepare reference-locked PBR packages for the Wave 11 diverse families.

Each family starts from one selected catalogue variant, one coherent four-view
goalpost board, and one shadow-neutral material plate.  This adapter extracts
the registered source views and delegates deterministic near/far PBR creation
to the shared reference-skin pipeline.

Run from the repository root:

    python tools/archetype_compiler/prepare_wave11_diverse_skins.py \
      --family coastal-mediterranean-resort
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from PIL import Image, ImageOps

from prepare_wave8_reference_skins import FAMILY_ROOT, prepare_family


GOALPOST_PROMPT = """Use case: photorealistic-natural
Asset type: render-locked architectural construction goalpost for a metric LEGO 3D family
Input images: Image 1 is the sole hard design reference for Coastal / Resort Terrace Block variant coastal_resort_white_mediterranean. Preserve this exact building identity; do not borrow any sibling variant.
Primary request: create one clean 2x2 architectural reference board showing the SAME coherent white Mediterranean coastal resort block in four views: front street oblique, straight-on orthographic front elevation, rear corner oblique, and high aerial roof view.
Subject: exactly three occupied levels arranged as cascading stepped terraces; irregular hand-trowelled white lime-stucco masses; pale local rubble-stone retaining walls and right-hand service wing; blue timber shutters; tall recessed French doors; thin black wrought-iron balcony rails; blue-grey open timber pergolas; restrained bougainvillea; a long rectangular infinity pool on the front terrace; flat parapeted roofs with planted roof terraces and one small white chimney.
Composition/framing: 2x2 equal panels with generous separation and the complete building visible in every panel. No labels or text.
Lighting/mood: neutral bright overcast architectural survey light, soft contact shadows only, consistent white balance in all panels.
Materials/textures: tactile imperfect lime stucco, pale rough-cut stone, painted blue timber, physically transparent neutral glass with visible warm interior depth, slender ironwork, water with subtle reflection.
Constraints: preserve the same footprint, floor count, terrace steps, opening cadence, pool location, stair location, shutters, pergolas, rooflines and material zoning across all four panels. The front elevation must be rectified and shadow-neutral. The aerial must clearly prove the setbacks and roof terraces. No redesign, no extra floors, no tower, no pitched or thatched roof, no contemporary all-glass replacement, no cliff cave, no neighboring buildings touching the subject, no people blocking facade geometry, no vehicles, no signage, no logos, no watermark."""


MATERIAL_PROMPT = """Use case: stylized-concept
Asset type: shadow-neutral construction material source plate for a physically based architectural model
Input images: Image 1 is the approved render-locked four-view goalpost for coastal_resort_white_mediterranean and is the sole palette/material authority.
Primary request: create a clean 3-column by 2-row orthographic material reference plate containing exactly six large seamless-looking square swatches, with no labels and narrow neutral gutters.
Swatches, left-to-right top row then bottom row: (1) imperfect warm-white hand-trowelled lime stucco with subtle aggregate and hairline variation; (2) pale cream local rubble limestone with small irregular blocks and recessed warm-grey mortar; (3) weathered muted Aegean blue painted timber with fine grain; (4) nearly black slender wrought iron with softly worn painted finish; (5) pale limestone pool coping and honed exterior paving; (6) neutral low-iron residential glass plus a shallow warm occupied interior study, shown frontally without perspective.
Composition/framing: each swatch fills its cell edge-to-edge; orthographic and rectified; consistent real-world material scale; no objects, doors, windows, railings, plants, furniture, sky, floor horizon, text, symbols, or labels.
Lighting/mood: perfectly even diffuse studio illumination, no cast shadows, no highlights indicating a light direction, neutral white balance.
Constraints: derive all hues and weathering from Image 1; construction-source realism, not a beauty render; no baked sun, no perspective distortion, no vignette, no borders other than narrow neutral gutters, no logos, no watermark."""


SKYLINE_GOALPOST_PROMPT = """Create one render-locked 2x2 survey board of the same skyline glass office complex: exactly three staggered curtain-wall towers on one transparent podium, tallest in the centre, two enclosed skybridges at different heights, stepped glazed roof lanterns, an occupied lobby and a paved civic plaza. Show front oblique, rectified front, rear oblique and aerial. Preserve tower count, bay cadence, bridge positions and crown geometry in every view; neutral overcast realism, no text or redesign."""

SKYLINE_MATERIAL_PROMPT = """Create one rectified 3x2 construction plate with six separate shadow-neutral sources: low-e vision glass, silver anodized aluminum, charcoal glass spandrel, pale podium stone, warm occupied office depth and graphite structural steel. Keep cells orthographic, facade-ready and physically plausible; no labels, objects spanning cells or baked sunlight."""

CAMPUS_GOALPOST_PROMPT = """Create one render-locked 2x2 survey board of the same low-rise Silicon Valley research campus: three connected two- to three-storey glass-and-white-steel pavilion wings around one landscaped courtyard, expressed external frame, broad cantilevered roof plates, glazed connectors, warm laboratories, photovoltaic arrays and a screened penthouse. Show arrival oblique, rectified front, courtyard rear and aerial. Preserve wing layout, floor counts, frame cadence and roof equipment in every view; no text or redesign."""

CAMPUS_MATERIAL_PROMPT = """Create one rectified 3x2 construction plate with six separate shadow-neutral sources: low-iron occupied glass, warm-white powder-coated steel, pale precast concrete, warm occupied laboratory depth, blue-black photovoltaic panels and pale concrete pavers. Keep cells orthographic, facade-ready and physically plausible; no labels, objects spanning cells or baked sunlight."""


FAMILIES: dict[str, dict] = {
    "coastal-mediterranean-resort": {
        "archetype_id": "coastal_resort_terrace_block",
        "variant_id": "coastal_resort_white_mediterranean",
        "skin_schema": "coastal-mediterranean-resort-skin@1",
        "goalpost_cells": {
            "street-hero-source-v1.png": (0.002, 0.002, 0.496, 0.496),
            "front-elevation-source-v1.png": (0.504, 0.002, 0.998, 0.496),
            "rear-corner-source-v1.png": (0.002, 0.504, 0.496, 0.998),
            "aerial-roof-source-v1.png": (0.504, 0.504, 0.998, 0.998),
        },
        "material_cells": {
            "lime-stucco-material-source-v1.png": (0.002, 0.002, 0.331, 0.493),
            "rubble-stone-material-source-v1.png": (0.337, 0.002, 0.665, 0.493),
            "blue-timber-material-source-v1.png": (0.670, 0.002, 0.998, 0.493),
            "wrought-iron-material-source-v1.png": (0.002, 0.507, 0.331, 0.998),
            "pool-coping-material-source-v1.png": (0.337, 0.507, 0.665, 0.998),
            "occupied-residential-source-v1.png": (0.670, 0.507, 0.998, 0.998),
        },
        "config": {
            "archetype_id": "coastal_resort_terrace_block",
            "variant_id": "coastal_resort_white_mediterranean",
            "skin_schema": "coastal-mediterranean-resort-skin@1",
            "elevation_source": "front-elevation-source-v1.png",
            "occupied_depth_source": "occupied-residential-source-v1.png",
            "bands": {
                "facade": (0.035, 0.045, 0.965, 0.935),
                "podium": (0.030, 0.650, 0.970, 0.935),
                "floor_a": (0.060, 0.335, 0.940, 0.690),
                "floor_b": (0.175, 0.105, 0.885, 0.450),
                "crown": (0.100, 0.035, 0.930, 0.260),
                "side": (0.015, 0.070, 0.285, 0.920),
            },
            "prefixes": {
                "facade": "white_mediterranean_front",
                "podium": "pool_terrace_podium",
                "floor_a": "arched_balcony_storey",
                "floor_b": "setback_roof_storey",
                "crown": "parapet_pergola_crown",
                "side": "quiet_stucco_return",
                "interior": "occupied_resort_room",
                "stucco": "hand_trowelled_lime_stucco",
                "stone": "pale_local_rubble_limestone",
                "blue_timber": "aegean_blue_painted_timber",
                "wrought_iron": "black_wrought_iron",
                "paving": "honed_pool_limestone",
                "glass": "neutral_low_iron_residential_glass",
                "water": "infinity_pool_water",
                "roof": "pale_flat_roof_membrane",
                "vegetation": "mediterranean_olive_foliage",
                "bougainvillea": "magenta_bougainvillea",
            },
            "support": {
                "stucco": ((225, 220, 208), "stone", 21101),
                "stone": ((188, 176, 151), "stone", 21111),
                "blue_timber": ((65, 107, 133), "wood", 21121),
                "wrought_iron": ((34, 34, 32), "metal", 21131),
                "paving": ((205, 199, 184), "stone", 21141),
                "glass": ((102, 127, 139), "glass", 21151),
                "water": ((53, 130, 151), "glass", 21161),
                "roof": ((205, 201, 190), "stone", 21171),
                "vegetation": ((72, 91, 51), "wood", 21181),
                "bougainvillea": ((151, 43, 93), "wood", 21191),
            },
            "support_sources": {
                "stucco": "lime-stucco-material-source-v1.png",
                "stone": "rubble-stone-material-source-v1.png",
                "blue_timber": "blue-timber-material-source-v1.png",
                "wrought_iron": "wrought-iron-material-source-v1.png",
                "paving": "pool-coping-material-source-v1.png",
                "glass": "occupied-residential-source-v1.png",
                "water": "occupied-residential-source-v1.png",
                "roof": "pool-coping-material-source-v1.png",
                "vegetation": "blue-timber-material-source-v1.png",
                "bougainvillea": "blue-timber-material-source-v1.png",
            },
            "registered_surfaces": [
                "three_level_cascading_white_stucco_resort_mass",
                "real_front_infinity_pool_basin_coping_and_stair",
                "arched_french_door_balcony_openings_with_deep_returns",
                "weathered_aegean_blue_operable_timber_shutters",
                "slender_open_wrought_iron_balcony_guards",
                "three_open_blue_timber_pergola_assemblies",
                "pale_rubble_stone_rear_service_and_retaining_walls",
                "occupied_neutral_low_iron_residential_glazing",
                "flat_parapeted_roof_terraces_with_one_chimney",
                "integrated_olive_and_bougainvillea_planting",
            ],
            "registration": (
                "The canonical board locks one three-level white Mediterranean "
                "resort: stepped lime-stucco rooms rise behind a long front "
                "infinity pool, with blue shutters, arched balcony doors, open "
                "pergolas, roof terraces and a quieter rubble-stone rear service "
                "elevation."
            ),
            "opening_method": (
                "Principal French doors occupy real gaps between stucco piers. "
                "Every opening has recessed low-iron panes, painted timber "
                "frames, occupied room depth, sill or threshold, shutters and "
                "open iron balcony guards where the reference requires them."
            ),
            "generic_tiling_allowed": False,
        },
        "design_lock": {
            "native_building_dimensions_m": [34.0, 19.0, 12.6],
            "native_envelope_dimensions_m": [40.0, 28.0, 13.4],
            "occupied_storeys": 3,
            "primary_material": "imperfect warm-white hand-trowelled lime stucco",
            "window_rule": "deep recessed French doors with blue shutters and occupied neutral glazing",
            "front_identity": "long infinity pool, side stair and layered open pergolas",
            "roof_rule": "cascading flat roof terraces with open iron guards and one white chimney",
        },
        "prompts": {
            "goalpost": GOALPOST_PROMPT,
            "material": MATERIAL_PROMPT,
        },
        "source_ids": {
            "goalpost": "exec-b69b625a-3937-4123-a533-2c95f464d16f",
            "material": "exec-66f79ae5-02d9-410b-8f85-4bfebc3adce1",
        },
    },
    "skyline-glass-office-cluster": {
        "archetype_id": "skyline_glass_office_cluster",
        "variant_id": "skyline_cluster_staggered",
        "skin_schema": "skyline-glass-office-cluster-skin@1",
        "goalpost_cells": {
            "street-hero-source-v1.png": (0.002, 0.002, 0.496, 0.496),
            "front-elevation-source-v1.png": (0.504, 0.002, 0.998, 0.496),
            "rear-corner-source-v1.png": (0.002, 0.504, 0.496, 0.998),
            "aerial-roof-source-v1.png": (0.504, 0.504, 0.998, 0.998),
        },
        "material_cells": {
            "vision-glass-material-source-v1.png": (0.002, 0.002, 0.331, 0.493),
            "aluminum-material-source-v1.png": (0.337, 0.002, 0.665, 0.493),
            "spandrel-material-source-v1.png": (0.670, 0.002, 0.998, 0.493),
            "podium-stone-material-source-v1.png": (0.002, 0.507, 0.331, 0.998),
            "occupied-office-source-v1.png": (0.337, 0.507, 0.665, 0.998),
            "structural-steel-material-source-v1.png": (0.670, 0.507, 0.998, 0.998),
        },
        "config": {
            "archetype_id": "skyline_glass_office_cluster",
            "variant_id": "skyline_cluster_staggered",
            "skin_schema": "skyline-glass-office-cluster-skin@1",
            "elevation_source": "front-elevation-source-v1.png",
            "occupied_depth_source": "occupied-office-source-v1.png",
            "bands": {
                "facade": (0.035, 0.045, 0.965, 0.950),
                "podium": (0.025, 0.720, 0.975, 0.950),
                "floor_a": (0.050, 0.405, 0.950, 0.760),
                "floor_b": (0.070, 0.215, 0.930, 0.565),
                "crown": (0.090, 0.035, 0.910, 0.245),
                "side": (0.015, 0.105, 0.315, 0.930),
            },
            "prefixes": {
                "facade": "three_tower_registered_front",
                "podium": "transparent_civic_podium",
                "floor_a": "occupied_curtain_wall_floor_a",
                "floor_b": "occupied_curtain_wall_floor_b",
                "crown": "stepped_glazed_roof_lantern",
                "side": "wrapped_curtain_wall_return",
                "interior": "warm_occupied_office_depth",
                "vision_glass": "neutral_blue_grey_low_e_vision_glass",
                "aluminum": "silver_anodized_aluminum_caps",
                "spandrel": "charcoal_glass_spandrel",
                "stone": "pale_honed_podium_stone",
                "steel": "graphite_structural_steel",
                "plaza": "pale_civic_plaza_paving",
                "roof": "dark_low_slope_roof_membrane",
            },
            "support": {
                "vision_glass": ((112, 139, 157), "glass", 21201),
                "aluminum": ((184, 190, 192), "metal", 21211),
                "spandrel": ((46, 53, 58), "glass", 21221),
                "stone": ((196, 193, 185), "stone", 21231),
                "steel": ((48, 52, 54), "metal", 21241),
                "plaza": ((188, 187, 181), "stone", 21251),
                "roof": ((65, 69, 71), "stone", 21261),
            },
            "support_sources": {
                "vision_glass": "vision-glass-material-source-v1.png",
                "aluminum": "aluminum-material-source-v1.png",
                "spandrel": "spandrel-material-source-v1.png",
                "stone": "podium-stone-material-source-v1.png",
                "steel": "structural-steel-material-source-v1.png",
                "plaza": "podium-stone-material-source-v1.png",
                "roof": "structural-steel-material-source-v1.png",
            },
            "registered_surfaces": [
                "exact_three_tower_staggered_silhouette",
                "two_enclosed_glazed_skybridges",
                "shared_transparent_civic_podium",
                "physical_vision_spandrel_and_aluminum_curtain_wall",
                "stepped_glazed_roof_lanterns",
                "warm_occupied_office_depth",
            ],
            "registration": "One exact three-tower office complex with a tallest centre tower, lower flanking towers, two enclosed bridges, one transparent podium and three stepped glazed crowns.",
            "opening_method": "Vision panes and spandrels are separate recessed surfaces behind physical aluminum pressure caps; warm occupied room cards sit behind vision zones only.",
            "generic_tiling_allowed": False,
        },
        "design_lock": {
            "native_building_dimensions_m": [64.0, 30.0, 70.0],
            "native_envelope_dimensions_m": [70.0, 40.0, 76.1],
            "occupied_storeys": 17,
            "primary_material": "neutral blue-grey low-e glass in a silver aluminum curtain wall",
            "window_rule": "separate vision panes, charcoal spandrels and physical aluminum caps with occupied depth",
            "front_identity": "exactly three staggered towers joined by two enclosed bridges over one transparent podium",
            "roof_rule": "three stepped glazed lantern crowns, with the tallest mast on the centre tower",
        },
        "prompts": {"goalpost": SKYLINE_GOALPOST_PROMPT, "material": SKYLINE_MATERIAL_PROMPT},
        "source_ids": {
            "goalpost": "exec-9a882913-bb61-4b3a-9e08-ad2c0a8c50db",
            "material": "exec-f5355841-d9fc-464c-9e4c-79b8a2f9b2dc",
        },
    },
    "autonomous-tech-campus-silicon-valley": {
        "archetype_id": "autonomous_tech_campus",
        "variant_id": "tech_campus_silicon_valley",
        "skin_schema": "autonomous-tech-campus-skin@1",
        "goalpost_cells": {
            "street-hero-source-v1.png": (0.002, 0.002, 0.496, 0.496),
            "front-elevation-source-v1.png": (0.504, 0.002, 0.998, 0.496),
            "courtyard-source-v1.png": (0.002, 0.504, 0.496, 0.998),
            "aerial-roof-source-v1.png": (0.504, 0.504, 0.998, 0.998),
        },
        "material_cells": {
            "low-iron-glass-material-source-v1.png": (0.002, 0.002, 0.331, 0.493),
            "white-steel-material-source-v1.png": (0.337, 0.002, 0.665, 0.493),
            "precast-material-source-v1.png": (0.670, 0.002, 0.998, 0.493),
            "occupied-lab-source-v1.png": (0.002, 0.507, 0.331, 0.998),
            "photovoltaic-material-source-v1.png": (0.337, 0.507, 0.665, 0.998),
            "paver-material-source-v1.png": (0.670, 0.507, 0.998, 0.998),
        },
        "config": {
            "archetype_id": "autonomous_tech_campus",
            "variant_id": "tech_campus_silicon_valley",
            "skin_schema": "autonomous-tech-campus-skin@1",
            "elevation_source": "front-elevation-source-v1.png",
            "occupied_depth_source": "occupied-lab-source-v1.png",
            "bands": {
                "facade": (0.040, 0.100, 0.960, 0.930),
                "podium": (0.030, 0.685, 0.970, 0.930),
                "floor_a": (0.050, 0.400, 0.950, 0.700),
                "floor_b": (0.080, 0.215, 0.920, 0.520),
                "crown": (0.070, 0.055, 0.930, 0.255),
                "side": (0.015, 0.160, 0.310, 0.900),
            },
            "prefixes": {
                "facade": "three_pavilion_registered_front",
                "podium": "landscaped_courtyard_podium",
                "floor_a": "occupied_research_floor_a",
                "floor_b": "occupied_research_floor_b",
                "crown": "cantilevered_canopy_and_pv_crown",
                "side": "wrapped_glass_pavilion_return",
                "interior": "warm_occupied_laboratory_depth",
                "glass": "neutral_low_iron_research_glass",
                "white_steel": "warm_white_powder_coated_steel",
                "precast": "pale_architectural_precast",
                "photovoltaic": "blue_black_photovoltaic_cells",
                "paving": "pale_concrete_campus_pavers",
                "roof": "light_grey_cool_roof_membrane",
                "landscape": "bioswale_grass_and_shrub_foliage",
            },
            "support": {
                "glass": ((116, 145, 156), "glass", 21301),
                "white_steel": ((220, 218, 208), "metal", 21311),
                "precast": ((194, 190, 180), "stone", 21321),
                "photovoltaic": ((30, 50, 75), "metal", 21331),
                "paving": ((190, 188, 181), "stone", 21341),
                "roof": ((186, 188, 185), "stone", 21351),
                "landscape": ((73, 93, 55), "wood", 21361),
            },
            "support_sources": {
                "glass": "low-iron-glass-material-source-v1.png",
                "white_steel": "white-steel-material-source-v1.png",
                "precast": "precast-material-source-v1.png",
                "photovoltaic": "photovoltaic-material-source-v1.png",
                "paving": "paver-material-source-v1.png",
                "roof": "white-steel-material-source-v1.png",
                "landscape": "paver-material-source-v1.png",
            },
            "registered_surfaces": [
                "three_connected_low_rise_pavilions",
                "landscaped_central_research_courtyard",
                "expressed_external_white_steel_frame",
                "separate_low_iron_glass_and_occupied_lab_depth",
                "broad_cantilevered_roof_canopies",
                "roof_photovoltaic_arrays_and_screened_penthouse",
            ],
            "registration": "One exact U-shaped low-rise research campus with three connected pavilion wings, an expressed white frame, a planted courtyard, broad canopy roofs and visible photovoltaic arrays.",
            "opening_method": "Full-height low-iron panes are recessed behind a physical white steel post-and-beam grid; occupied lab cards and slabs establish real depth behind the glazing.",
            "generic_tiling_allowed": False,
        },
        "design_lock": {
            "native_building_dimensions_m": [68.0, 48.0, 15.0],
            "native_envelope_dimensions_m": [74.0, 54.0, 13.4],
            "occupied_storeys": 3,
            "primary_material": "neutral low-iron glass behind a warm-white expressed steel frame",
            "window_rule": "full-height separate panes with occupied laboratory depth and external white posts/beams",
            "front_identity": "three low-rise pavilion wings frame one landscaped research courtyard",
            "roof_rule": "broad cantilevered canopy plates, photovoltaic arrays and one screened mechanical penthouse",
        },
        "prompts": {"goalpost": CAMPUS_GOALPOST_PROMPT, "material": CAMPUS_MATERIAL_PROMPT},
        "source_ids": {
            "goalpost": "exec-cb1dd5a6-f86c-4414-a77d-5042e4a56ba1",
            "material": "exec-46ef1cc8-8a03-400f-826a-46a777757873",
        },
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", choices=sorted(FAMILIES), required=True)
    return parser.parse_args()


def crop_cells(source_root, source_name: str, cells: dict[str, tuple[float, float, float, float]]) -> None:
    source = ImageOps.exif_transpose(Image.open(source_root / source_name)).convert("RGB")
    width, height = source.size
    for filename, (x0, y0, x1, y1) in cells.items():
        source.crop(
            (
                round(width * x0),
                round(height * y0),
                round(width * x1),
                round(height * y1),
            )
        ).save(source_root / filename, optimize=True)


def write_provenance(family: str, spec: dict) -> None:
    source_root = FAMILY_ROOT / family / "textures" / "source"
    goalpost_id = spec["source_ids"]["goalpost"]
    material_id = spec["source_ids"]["material"]
    payload = {
        "schema": "reference-generation@1",
        "family": family,
        "archetype_id": spec["archetype_id"],
        "variant_id": spec["variant_id"],
        "provider": "OpenAI built-in image generation",
        "model": "gpt-image-2",
        "generated_at": date.today().isoformat(),
        "status": "source-pack-complete",
        "input_paths": [
            f"/archetypes/buildings/{spec['archetype_id']}/variant_0.png",
        ],
        "design_lock": spec["design_lock"],
        "sources": [
            {
                "file": "archetype-goalpost.png",
                "source_id": goalpost_id,
                "role": "canonical_four_view_reference_board",
                "prompt": spec["prompts"]["goalpost"],
                "registered_surfaces": spec["config"]["registered_surfaces"],
            },
            *(
                {
                    "file": filename,
                    "source_id": f"{goalpost_id}:{Path(filename).stem}",
                    "role": f"registered_goalpost_crop:{Path(filename).stem}",
                }
                for filename in spec["goalpost_cells"]
            ),
            {
                "file": "material-construction-source-v1.png",
                "source_id": material_id,
                "role": "six_zone_shadow_neutral_material_plate",
                "prompt": spec["prompts"]["material"],
            },
            *(
                {
                    "file": filename,
                    "source_id": f"{material_id}:{Path(filename).stem}",
                    "role": f"registered_material_crop:{Path(filename).stem}",
                }
                for filename in spec["material_cells"]
            ),
        ],
    }
    (source_root / "reference-generation.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )


def bind_atlas(family: str) -> None:
    manifest_path = FAMILY_ROOT / family / "textures" / "skin_manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["atlases"] = {
        lod: dict(payload["zones"]["facade"][lod])
        for lod in ("near", "far")
    }
    manifest_path.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    family = args.family
    spec = FAMILIES[family]
    source_root = FAMILY_ROOT / family / "textures" / "source"
    crop_cells(source_root, "archetype-goalpost.png", spec["goalpost_cells"])
    crop_cells(
        source_root,
        "material-construction-source-v1.png",
        spec["material_cells"],
    )
    write_provenance(family, spec)
    prepare_family(family, spec["config"], batch_label="wave11")
    bind_atlas(family)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
