"""Prepare reference-locked PBR packages for the Wave 12 diverse families.

Wave 12 uses a coherent four-view goalpost plus a shadow-neutral construction
plate for every family.  This adapter crops those authored sources and delegates
near/far PBR derivation to the shared reference-skin pipeline.

Run from the repository root::

    python tools/archetype_compiler/prepare_wave12_diverse_skins.py \
      --family vertical-forest-residential
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from PIL import Image, ImageOps

from prepare_wave8_reference_skins import FAMILY_ROOT, prepare_family


VERTICAL_FOREST_GOALPOST_PROMPT = """Use case: photorealistic architectural reference board
Asset type: render-locked multi-angle construction goalpost for a metric LEGO 3D building family
Input images: Image 1 is the catalogue identity and material reference for the Bosco-style vertical forest tower.
Primary request: Create one coherent four-view architectural reference board of the exact same single vertical-forest residential tower, suitable for reconstructing as a true-metric 3D model.
Scene/backdrop: quiet neutral architectural studio plaza with pale warm-grey paving and a clean light-grey sky; no neighboring buildings; no cars; no people.
Subject: an 18-storey, approximately 28 m by 28 m rectangular residential tower with the same topology in every panel: a dark glazed residential core, a clearly expressed off-white concrete perimeter frame, very deep cantilevered concrete balcony trays, integral dark soil planters, mature deciduous trees and varied shrubs on every level, a transparent planted lobby at grade, and an intensive rooftop garden. The frame, floor count, bay count, balcony projections, major tree positions, roof edge, and entrance stay identical in all four views. Make the balconies physically thick with visible soffits and slab edges; glass sits recessed behind the frame with believable reflections and warm occupied depth.
Composition/framing: a precise 2x2 board with equal panels showing (1) orthographic-like front elevation, (2) front-right street corner three-quarter view, (3) rear-left three-quarter view proving wrapped secondary elevations, and (4) high aerial oblique proving roof and balcony depth. Entire building visible with generous margin in every panel. Thin neutral gutters only, no labels.
Style/medium: premium photoreal architectural photography / visualization, physically plausible construction and materials, fine facade detail, no illustration or game-art look.
Lighting/mood: consistent bright overcast daylight in all panels, shadow-neutral enough to read material color and construction depth.
Materials/textures: lightly weathered board-formed white concrete; dark bronze thermally broken window frames; low-iron neutral grey vision glass with distinct reflectivity; dark planter soil; seasonally varied real foliage with individual trunks and branches, not green blobs.
Constraints: topology locked across all four views; exactly 18 occupied floors plus rooftop garden; front facade faces the viewer in panel 1; no perspective distortion in the front elevation; no text; no logos; no watermark; no fantasy forms.
Avoid: generic glass box, flat green texture, plants painted onto walls, oversized foliage hiding all construction, inconsistent floor count, changed balconies between views, duplicated buildings, blue opaque windows, cartoonish saturation."""


VERTICAL_FOREST_MATERIAL_PROMPT = """Use case: photorealistic architectural material reference
Asset type: shadow-neutral 3x2 construction and occupied-depth board for the exact vertical-forest tower in Image 1
Input images: Image 1 is the approved topology and palette authority.
Primary request: Create six equal square, straight-on, orthographic material samples separated by thin neutral gutters, with no labels: top-left lightly weathered off-white board-formed architectural concrete with subtle pores and horizontal formwork grain; top-center dark bronze anodized thermally broken aluminium window-frame material; top-right neutral low-iron residential vision glass with subtle grey-green reflection variation but no mullion grid; bottom-left a clean warm occupied-apartment depth plate seen through glass, showing believable curtains, ceiling edge, warm interior darkness and varied room depth but no exterior frame; bottom-center dense temperate deciduous foliage from the approved palette, with individually legible leaves, fine twigs, olive-green and restrained burgundy seasonal variation, no sky; bottom-right dark rich planter soil with a narrow charcoal waterproof planter lining and small groundcover.
Scene/backdrop: flat, evenly lit material-capture setup.
Style/medium: physically based photoreal architectural texture reference, high micro-detail, realistic scale.
Lighting/mood: diffuse neutral overcast capture, no baked directional shadows, no sun hotspots, no perspective.
Constraints: exact 3 columns by 2 rows; each sample fills its cell edge-to-edge; no text; no labels; no logos; no watermark; no photographed complete facade; no repeating window grid.
Avoid: cartoon foliage, plastic concrete, saturated emerald green, blue glass, baked building perspective, decorative borders, heavy vignette."""


VERTICAL_FOREST_FOLIAGE_PROMPT = """Use case: photorealistic architectural vegetation asset
Asset type: isolated temperate deciduous tree-canopy cutout for crossed 3D foliage cards
Input images: Image 1 is the approved vertical-forest palette and botanical density authority.
Primary request: Create one single dense but naturally irregular temperate deciduous tree crown, viewed straight-on, with individually legible olive-green leaves, fine twigs, small branch forks, subtle yellow-green variation, and a few restrained burgundy leaves. The crown must feel like a mature balcony tree in the approved architecture, not a clipped topiary. Include no trunk below the crown; fine internal branches may show through natural gaps.
Scene/backdrop: perfectly flat, uniform solid #ff00ff chroma-key background.
Composition/framing: one crown centered, filling about 82 percent of a square canvas, generous clear padding on every side, no cropped leaves, no floor, no horizon.
Style/medium: premium photoreal botanical asset, natural leaf translucency and fine silhouette, architectural visualization quality.
Lighting/mood: diffuse neutral overcast illumination with no cast shadow and no directional hotspot.
Constraints: background must be exactly one uniform #ff00ff with no gradient, texture, shadow, reflection, floor plane, or lighting variation; crisp detailed foliage boundary; no magenta anywhere in the foliage; no text; no logo; no watermark.
Avoid: spherical topiary, low-poly foliage, cartoon leaves, blurred green blob, entire tree trunk, pot, planter, sky, building, multiple disconnected crowns."""


GOTHIC_GOALPOST_PROMPT = """Use case: photorealistic architectural reference board
Asset type: render-locked multi-angle construction goalpost for a metric LEGO 3D building family
Primary request: Create one coherent four-view architectural reference board of the exact same Tudor Collegiate Gothic gatehouse quadrangle, suitable for true-metric 3D reconstruction.
Scene/backdrop: quiet neutral stone civic plaza and clipped lawn court under a clean pale overcast sky; no neighboring buildings touching the subject; no cars; only a few tiny scale figures far from facade openings.
Subject: a four-storey university college arranged as a complete open rectangular quadrangle, approximately 64 m wide by 44 m deep. Four connected academic wings in warm honey Cotswold limestone surround a clearly open central court. The formal front wing is centered on one projecting square gatehouse tower with a real tall four-centred pointed through-passage, deep carved portal returns, heavy dark oak doors held open inside the passage, a broad integrated stone approach stair, three tall traceried tower windows, crenellated parapet, and four slender pinnacles. Wings have an eleven-bay rhythm of real deep pointed mullioned-and-transomed leaded windows between load-bearing stone piers and buttresses. Steep dark Welsh-slate gable roofs, clustered octagonal chimneys, stone string courses, and restrained heraldic shields complete the silhouette.
Composition/framing: precise 2x2 board with equal panels showing (1) rectified orthographic-like front elevation, (2) front-right street corner view proving gate depth and side wing, (3) rear-left court-side view proving the open quadrangle and all four wings, and (4) high aerial oblique proving the open court, connected slate roof fields, tower, chimneys, and passage. Entire building visible with generous margin in every panel. Thin neutral gutters only, no labels.
Style/medium: premium photoreal architectural photography / visualization, physically plausible historic masonry construction, fine carved detail, no illustration or theme-park look.
Lighting/mood: consistent bright overcast survey daylight, soft contact shadows, neutral white balance.
Materials/textures: lightly weathered honey limestone ashlar with recessed warm mortar; deeper carved limestone tracery; dark blue-grey slate; lead-grey glazing with subtle warm occupied academic room depth; dark oak; black iron.
Constraints: exact same topology, bay count, floor count, tower, passage, quadrangle, roof ridges, chimneys, opening cadence, and material zoning in all four panels; front facade faces viewer in panel 1; the gate and courtyard must be real visible voids, not black painted arches; no text; no logos; no watermark.
Avoid: cathedral nave, church-only massing, fantasy castle, oversized random towers, blocked gate, filled courtyard, flat roof, red brick, modern glass box, cartoon saturation, changed design between panels."""


GOTHIC_MATERIAL_PROMPT = """Use case: photorealistic architectural material reference
Asset type: shadow-neutral 3x2 construction and occupied-depth board for the exact Tudor collegiate quadrangle in Image 1
Input images: Image 1 is the approved topology, age, scale, and palette authority.
Primary request: Create six equal square, straight-on, orthographic material samples separated by thin neutral gutters, with no labels: top-left warm honey Cotswold limestone ashlar in regular collegiate courses with fine pores and recessed warm-grey lime mortar; top-center deeper finely carved honey limestone showing rectilinear Gothic tracery mouldings and subtle tool marks but no complete window; top-right dark blue-grey hand-cut Welsh slate in small regular roof courses with restrained mineral variation; bottom-left neutral lead-grey heritage glazing with a subtle diamond lead-came pattern and realistic low reflectivity but no surrounding stone frame; bottom-center a clean warm occupied academic-room depth plate seen through glazing, with timber shelves, ceiling edge, lamps and room darkness but no exterior mullion; bottom-right aged dark English oak with vertical grain, iron-stud marks, and restrained wear suitable for a heavy gate door.
Scene/backdrop: flat evenly lit material-capture setup.
Style/medium: physically based photoreal historic construction texture reference, fine micro-detail and real-world scale.
Lighting/mood: diffuse neutral overcast capture, no baked directional shadow, no sun hotspot, no perspective.
Constraints: exact 3 columns by 2 rows; each sample fills its cell edge-to-edge; no text; no labels; no logos; no watermark; no complete facade; no objects spanning cells.
Avoid: fantasy runes, cathedral scene, plastic stone, orange sandstone, bright blue glass, cartoon mortar, baked architecture perspective, decorative border, vignette."""


TERMINAL_GOALPOST_PROMPT = """Use case: photorealistic architectural reference board
Asset type: render-locked multi-angle construction goalpost for a metric LEGO 3D building family
Primary request: Create one coherent four-view architectural reference board of the exact same cable-stayed high-tech airport terminal, suitable for true-metric 3D reconstruction.
Scene/backdrop: a clean pale concrete airport apron and landside drop-off plaza under a bright overcast sky; no aircraft blocking the building; no brands, airline logos, text, cars, or crowds.
Subject: a wide low three-level terminal approximately 90 m wide by 68 m deep. A transparent two-level departure hall is enclosed by high-transmission neutral glass and real silver pressure caps. One shallow sweeping translucent space-frame canopy spans the whole building and projects deeply over the landside frontage. Six dark graphite branching steel tree-columns rise inside and in front of the glass to support the roof. A single tapered central mast rises above the canopy near the landside center, with ten clearly visible slender stay cables fanning to the front and rear roof edges. Both side elevations are wrapped by occupied glass behind champagne-silver diamond diagonal bracing. A broad integrated entry canopy and six glazed automatic doors mark the center. The rear airside elevation has exactly three complete glazed gate bridges projecting from the building. Pale concrete floor plates and two warm occupied concourse levels remain visible through the glass.
Composition/framing: precise 2x2 board with equal panels showing (1) rectified orthographic-like landside front elevation, (2) front-right oblique proving canopy depth, branching columns, mast and cable fan, (3) rear-left airside oblique proving all three gate bridges and wrapped side enclosure, and (4) high aerial oblique proving the complete sweeping roof grid, central mast, cable anchor points, service roof and building depth. Entire terminal visible with generous margin in every panel. Thin neutral gutters only, no labels.
Style/medium: premium photoreal architectural photography / visualization, physically plausible long-span engineering, fine curtain-wall detail, no concept-art fantasy.
Lighting/mood: consistent neutral bright overcast survey light, soft contact shadows, restrained reflections.
Materials/textures: graphite and silver structural steel; champagne-silver aluminium panels; neutral low-iron terminal glass; translucent pearl roof infill; pale apron concrete; warm occupied depth.
Constraints: exact same width, depth, floor count, bay rhythm, roof curve, mast location, stay count, tree-column positions, diamond bracing, three rear bridges, entrances, and material zones in every panel; front facade faces viewer in panel 1; cables and branching supports must connect structurally; no text; no logos; no watermark.
Avoid: airport control tower, aircraft-shaped building, multiple random masts, tent roof, opaque shed, blue mirrored glass, missing rear bridges, exposed fantasy cantilevers, changed topology between views, cartoon rendering."""


TERMINAL_MATERIAL_PROMPT = """Use case: photorealistic architectural material reference
Asset type: shadow-neutral 3x2 construction and occupied-depth board for the exact cable-stayed terminal in Image 1
Input images: Image 1 is the approved engineering, scale, and palette authority.
Primary request: Create six equal square, straight-on, orthographic material samples separated by thin neutral gutters, with no labels: top-left satin silver structural steel with fine rolled grain and subtle outdoor oxidation; top-center dark graphite painted structural steel with restrained coating texture; top-right warm champagne-silver anodized aluminium composite panel with fine directional grain; bottom-left neutral high-transmission low-iron terminal glass with subtle grey-green reflection variation but no mullion grid; bottom-center a clean warm occupied airport concourse depth plate seen through glass, showing floor-plate edges, ceiling lights, distant retail-like room depth and people-scale silhouettes but absolutely no signage or text and no exterior frame; bottom-right translucent pearl polycarbonate or fritted-glass roof infill with a fine diffuse dot texture, suitable for a sweeping canopy, with no structural grid baked into it.
Scene/backdrop: flat evenly lit material-capture setup.
Style/medium: physically based photoreal high-tech construction texture reference, fine micro-detail and real-world scale.
Lighting/mood: diffuse neutral overcast capture, no baked directional shadow, no sun hotspot, no perspective.
Constraints: exact 3 columns by 2 rows; each sample fills its cell edge-to-edge; no text; no labels; no logos; no watermark; no complete facade; no truss or mullion pattern spanning a material cell.
Avoid: blue mirrored glass, brushed kitchen steel, rusty ruin, opaque roof, cartoon metal, baked building perspective, decorative border, vignette."""


GOALPOST_CELLS = {
    "front-elevation-source-v1.png": (0.002, 0.002, 0.498, 0.498),
    "street-hero-source-v1.png": (0.502, 0.002, 0.998, 0.498),
    "rear-corner-source-v1.png": (0.002, 0.502, 0.498, 0.998),
    "aerial-roof-source-v1.png": (0.502, 0.502, 0.998, 0.998),
}


FAMILIES: dict[str, dict] = {
    "vertical-forest-residential": {
        "archetype_id": "vertical_forest_residential",
        "variant_id": "vertical_forest_bosco",
        "skin_schema": "vertical-forest-residential-skin@1",
        "goalpost_cells": GOALPOST_CELLS,
        "material_cells": {
            "concrete-material-source-v1.png": (0.002, 0.002, 0.331, 0.498),
            "bronze-frame-material-source-v1.png": (0.335, 0.002, 0.665, 0.498),
            "vision-glass-material-source-v1.png": (0.669, 0.002, 0.998, 0.498),
            "occupied-residential-source-v1.png": (0.002, 0.502, 0.331, 0.998),
            "foliage-material-source-v1.png": (0.335, 0.502, 0.665, 0.998),
            "planter-soil-material-source-v1.png": (0.669, 0.502, 0.998, 0.998),
        },
        "config": {
            "archetype_id": "vertical_forest_residential",
            "variant_id": "vertical_forest_bosco",
            "skin_schema": "vertical-forest-residential-skin@1",
            "elevation_source": "front-elevation-source-v1.png",
            "occupied_depth_source": "occupied-residential-source-v1.png",
            "bands": {
                "facade": (0.105, 0.035, 0.895, 0.975),
                "podium": (0.105, 0.845, 0.895, 0.975),
                "floor_a": (0.105, 0.610, 0.895, 0.825),
                "floor_b": (0.105, 0.390, 0.895, 0.610),
                "crown": (0.105, 0.035, 0.895, 0.165),
                "side": (0.105, 0.180, 0.300, 0.920),
            },
            "prefixes": {
                "facade": "bosco_registered_front",
                "podium": "planted_transparent_lobby",
                "floor_a": "deep_planted_balcony_floor_a",
                "floor_b": "deep_planted_balcony_floor_b",
                "crown": "intensive_rooftop_garden_crown",
                "side": "wrapped_planted_secondary_elevation",
                "interior": "occupied_residential_depth",
                "concrete": "board_formed_off_white_concrete",
                "bronze_frame": "dark_bronze_anodized_frame",
                "vision_glass": "neutral_low_iron_residential_glass",
                "foliage": "temperate_deciduous_foliage",
                "soil": "dark_planter_soil",
                "planter": "charcoal_waterproof_planter",
                "trunk": "natural_tree_bark",
                "roof": "intensive_green_roof_membrane",
                "paving": "warm_grey_studio_paving",
            },
            "support": {
                "concrete": ((218, 214, 204), "stone", 12101),
                "bronze_frame": ((49, 43, 38), "metal", 12111),
                "vision_glass": ((92, 105, 103), "glass", 12121),
                "foliage": ((74, 91, 48), "wood", 12131),
                "soil": ((37, 30, 23), "stone", 12141),
                "planter": ((49, 48, 44), "metal", 12151),
                "trunk": ((79, 59, 40), "wood", 12161),
                "roof": ((80, 87, 70), "stone", 12171),
                "paving": ((185, 181, 173), "stone", 12181),
            },
            "support_sources": {
                "concrete": "concrete-material-source-v1.png",
                "bronze_frame": "bronze-frame-material-source-v1.png",
                "vision_glass": "vision-glass-material-source-v1.png",
                "foliage": "foliage-material-source-v1.png",
                "soil": "planter-soil-material-source-v1.png",
                "planter": "planter-soil-material-source-v1.png",
                "trunk": "foliage-material-source-v1.png",
                "roof": "planter-soil-material-source-v1.png",
                "paving": "concrete-material-source-v1.png",
            },
            "registered_surfaces": [
                "eighteen_storey_dark_glazed_residential_core",
                "continuous_off_white_perimeter_concrete_frame",
                "deep_cantilevered_balcony_trays_with_visible_soffits",
                "integral_soil_planters_and_structurally_supported_trees",
                "physical_recessed_glass_with_occupied_residential_depth",
                "transparent_planted_ground_floor_lobby",
                "complete_wrapped_secondary_elevations",
                "intensive_rooftop_garden_with_service_core",
            ],
            "registration": (
                "The four-view board locks one eighteen-storey Bosco-style tower: "
                "a dark occupied core sits behind a continuous off-white perimeter "
                "frame, deep balcony trays and real planted soil volumes on all sides."
            ),
            "opening_method": (
                "Every residential pane is a separate recessed physical glass layer "
                "with bronze frame, slab edge, reveal and occupied room depth. Plants "
                "and balcony structure remain geometry in front of those openings."
            ),
            "generic_tiling_allowed": False,
        },
        "design_lock": {
            "native_building_dimensions_m": [28.0, 28.0, 65.6],
            "native_envelope_dimensions_m": [31.0, 31.0, 69.0],
            "occupied_storeys": 18,
            "primary_material": "lightly weathered off-white board-formed concrete",
            "window_rule": "recessed neutral glass in dark bronze frames with warm occupied depth",
            "front_identity": "continuous structural grid in front of irregular deep planted balconies",
            "roof_rule": "intensive rooftop garden around a compact screened service core",
        },
        "prompts": {
            "goalpost": VERTICAL_FOREST_GOALPOST_PROMPT,
            "material": VERTICAL_FOREST_MATERIAL_PROMPT,
        },
        "source_ids": {
            "goalpost": "exec-70cd6565-109b-4455-b606-aaad45ae550a",
            "material": "exec-1ceec380-b199-4a4f-b7ff-fd3c596ba8b0",
        },
        "input_paths": [
            "/archetypes/buildings/vertical_forest_residential/variant_0.png",
        ],
        "extra_sources": [
            {
                "file": "foliage-card-source-v1.png",
                "source_id": "exec-1872f1fc-3fd9-4ed8-b165-4bed3ddd8b55",
                "role": "family_specific_chroma_keyed_foliage_source",
                "prompt": VERTICAL_FOREST_FOLIAGE_PROMPT,
            },
            {
                "file": "foliage-card-v1.png",
                "source_id": "exec-1872f1fc-3fd9-4ed8-b165-4bed3ddd8b55:soft-matte-despill",
                "role": "transparent_crossed_foliage_card",
                "postprocess": "remove_chroma_key.py --auto-key border --soft-matte --transparent-threshold 12 --opaque-threshold 220 --despill",
            },
        ],
    },
    "collegiate-gothic-gatehouse": {
        "archetype_id": "collegiate_gothic_education",
        "variant_id": "collegiate_gothic_tudor",
        "skin_schema": "collegiate-gothic-gatehouse-skin@1",
        "goalpost_cells": GOALPOST_CELLS,
        "material_cells": {
            "limestone-material-source-v1.png": (0.002, 0.002, 0.331, 0.498),
            "carved-stone-material-source-v1.png": (0.335, 0.002, 0.665, 0.498),
            "slate-material-source-v1.png": (0.669, 0.002, 0.998, 0.498),
            "leaded-glass-material-source-v1.png": (0.002, 0.502, 0.331, 0.998),
            "occupied-academic-source-v1.png": (0.335, 0.502, 0.665, 0.998),
            "oak-material-source-v1.png": (0.669, 0.502, 0.998, 0.998),
        },
        "config": {
            "archetype_id": "collegiate_gothic_education",
            "variant_id": "collegiate_gothic_tudor",
            "skin_schema": "collegiate-gothic-gatehouse-skin@1",
            "elevation_source": "front-elevation-source-v1.png",
            "occupied_depth_source": "occupied-academic-source-v1.png",
            "bands": {
                "facade": (0.012, 0.035, 0.988, 0.890),
                "podium": (0.012, 0.690, 0.988, 0.890),
                "floor_a": (0.015, 0.430, 0.985, 0.700),
                "floor_b": (0.015, 0.235, 0.985, 0.505),
                "crown": (0.260, 0.025, 0.740, 0.245),
                "side": (0.015, 0.175, 0.265, 0.850),
            },
            "prefixes": {
                "facade": "tudor_college_registered_front",
                "podium": "real_gate_passage_and_stair_podium",
                "floor_a": "pointed_academic_floor_a",
                "floor_b": "pointed_academic_floor_b",
                "crown": "crenellated_gatehouse_crown",
                "side": "wrapped_gothic_academic_wing",
                "interior": "occupied_academic_room_depth",
                "limestone": "honey_cotswold_limestone_ashlar",
                "carved_stone": "carved_honey_limestone_tracery",
                "slate": "dark_welsh_slate",
                "leaded_glass": "neutral_lead_came_heritage_glass",
                "oak": "aged_dark_english_oak",
                "iron": "black_forged_iron",
                "paving": "honey_limestone_college_paving",
            },
            "support": {
                "limestone": ((184, 151, 99), "stone", 12201),
                "carved_stone": ((175, 139, 88), "stone", 12211),
                "slate": ((54, 61, 65), "stone", 12221),
                "leaded_glass": ((91, 99, 98), "glass", 12231),
                "oak": ((60, 39, 24), "wood", 12241),
                "iron": ((36, 36, 34), "metal", 12251),
                "paving": ((169, 151, 119), "stone", 12261),
            },
            "support_sources": {
                "limestone": "limestone-material-source-v1.png",
                "carved_stone": "carved-stone-material-source-v1.png",
                "slate": "slate-material-source-v1.png",
                "leaded_glass": "leaded-glass-material-source-v1.png",
                "oak": "oak-material-source-v1.png",
                "paving": "limestone-material-source-v1.png",
            },
            "registered_surfaces": [
                "complete_four_wing_open_college_quadrangle",
                "projecting_central_gatehouse_tower",
                "real_four_centred_through_passage_with_deep_returns",
                "integrated_ceremonial_stone_gate_stair",
                "deep_pointed_mullioned_and_transomed_leaded_windows",
                "load_bearing_limestone_piers_and_buttresses",
                "four_connected_steep_welsh_slate_gable_fields",
                "crenellations_pinnacles_and_clustered_chimneys",
            ],
            "registration": (
                "The four-view board locks one complete honey-limestone Tudor "
                "college quadrangle: four occupied academic wings surround an "
                "open court and centre on a real gate passage below a traceried, "
                "crenellated gatehouse tower."
            ),
            "opening_method": (
                "Every academic opening is a real gap between limestone piers "
                "with deep jambs, continuous pointed frame, mullion, transom, "
                "lead-grey pane and occupied room depth. The gate is a complete "
                "walk-through volume rather than a dark arch painted on stone."
            ),
            "generic_tiling_allowed": False,
        },
        "design_lock": {
            "native_building_dimensions_m": [64.0, 44.0, 30.0],
            "native_envelope_dimensions_m": [66.0, 49.0, 31.0],
            "occupied_storeys": 4,
            "primary_material": "weathered honey Cotswold limestone ashlar",
            "window_rule": "deep pointed leaded openings with carved tracery and occupied academic depth",
            "front_identity": "real gate passage, integrated stair and traceried crenellated gatehouse tower",
            "roof_rule": "four steep connected Welsh-slate gable fields with chimneys and pinnacles",
        },
        "prompts": {"goalpost": GOTHIC_GOALPOST_PROMPT, "material": GOTHIC_MATERIAL_PROMPT},
        "source_ids": {
            "goalpost": "exec-902efcd2-dc05-441a-9874-cc981cb0d326",
            "material": "exec-01f40bf4-0a18-4bb0-889f-2461c7db68e9",
        },
        "input_paths": [],
    },
    "cable-stayed-airport-terminal": {
        "archetype_id": "airport_terminal_building",
        "variant_id": "cable_stayed_steel_truss_terminal",
        "skin_schema": "cable-stayed-airport-terminal-skin@1",
        "goalpost_cells": GOALPOST_CELLS,
        "material_cells": {
            "silver-steel-material-source-v1.png": (0.002, 0.002, 0.331, 0.498),
            "graphite-steel-material-source-v1.png": (0.335, 0.002, 0.665, 0.498),
            "aluminum-material-source-v1.png": (0.669, 0.002, 0.998, 0.498),
            "terminal-glass-material-source-v1.png": (0.002, 0.502, 0.331, 0.998),
            "occupied-terminal-source-v1.png": (0.335, 0.502, 0.665, 0.998),
            "roof-infill-material-source-v1.png": (0.669, 0.502, 0.998, 0.998),
        },
        "config": {
            "archetype_id": "airport_terminal_building",
            "variant_id": "cable_stayed_steel_truss_terminal",
            "skin_schema": "cable-stayed-airport-terminal-skin@1",
            "elevation_source": "front-elevation-source-v1.png",
            "occupied_depth_source": "occupied-terminal-source-v1.png",
            "bands": {
                "facade": (0.015, 0.085, 0.985, 0.850),
                "podium": (0.015, 0.640, 0.985, 0.850),
                "floor_a": (0.025, 0.420, 0.975, 0.665),
                "floor_b": (0.025, 0.260, 0.975, 0.510),
                "crown": (0.015, 0.080, 0.985, 0.300),
                "side": (0.015, 0.200, 0.245, 0.790),
            },
            "prefixes": {
                "facade": "cable_stayed_terminal_registered_front",
                "podium": "integrated_departure_entry_podium",
                "floor_a": "occupied_terminal_concourse_floor_a",
                "floor_b": "occupied_terminal_concourse_floor_b",
                "crown": "space_frame_cable_crown",
                "side": "diamond_braced_terminal_side",
                "interior": "occupied_terminal_concourse_depth",
                "steel": "satin_silver_structural_steel",
                "graphite": "dark_graphite_structural_steel",
                "aluminum": "champagne_anodized_aluminum",
                "terminal_glass": "neutral_high_transmission_terminal_glass",
                "roof_infill": "translucent_pearl_roof_infill",
                "concrete": "pale_airport_apron_concrete",
                "roof": "dark_terminal_service_roof",
            },
            "support": {
                "steel": ((174, 178, 178), "metal", 12301),
                "graphite": ((52, 56, 58), "metal", 12311),
                "aluminum": ((190, 181, 166), "metal", 12321),
                "terminal_glass": ((126, 143, 145), "glass", 12331),
                "roof_infill": ((198, 204, 202), "glass", 12341),
                "concrete": ((186, 184, 179), "stone", 12351),
                "roof": ((70, 74, 74), "stone", 12361),
            },
            "support_sources": {
                "steel": "silver-steel-material-source-v1.png",
                "graphite": "graphite-steel-material-source-v1.png",
                "aluminum": "aluminum-material-source-v1.png",
                "terminal_glass": "terminal-glass-material-source-v1.png",
                "roof_infill": "roof-infill-material-source-v1.png",
                "concrete": "silver-steel-material-source-v1.png",
                "roof": "graphite-steel-material-source-v1.png",
            },
            "registered_surfaces": [
                "wide_transparent_two_level_departure_hall",
                "complete_shallow_sweeping_space_frame_canopy",
                "six_branching_graphite_tree_columns",
                "single_central_mast_with_ten_radiating_stays",
                "occupied_glass_behind_diamond_braced_side_walls",
                "integrated_dropoff_canopy_and_six_glazed_doors",
                "three_complete_airside_gate_bridges",
                "complete_roof_grid_anchor_points_and_service_roof",
            ],
            "registration": (
                "The four-view board locks one wide cable-stayed terminal: a "
                "transparent occupied hall sits below one shallow space-frame "
                "canopy carried by branching columns and a central ten-stay mast, "
                "with diamond sides and three airside gate bridges."
            ),
            "opening_method": (
                "Every curtain-wall bay uses a separate neutral pane, pressure "
                "caps, floor-plate edge and occupied concourse depth. The side "
                "diamonds, tree columns, mast, stays and gate bridges remain "
                "connected shadow-casting structure outside that enclosure."
            ),
            "generic_tiling_allowed": False,
        },
        "design_lock": {
            "native_building_dimensions_m": [90.0, 68.0, 27.2],
            "native_envelope_dimensions_m": [92.0, 70.0, 28.0],
            "occupied_storeys": 3,
            "primary_material": "neutral high-transmission glass within a silver and graphite long-span structure",
            "window_rule": "physical terminal panes with real caps, slabs and warm occupied concourse depth",
            "front_identity": "six branching columns below one mast and ten connected stay cables",
            "roof_rule": "one shallow translucent space-frame canopy with visible complete grid and anchor points",
        },
        "prompts": {"goalpost": TERMINAL_GOALPOST_PROMPT, "material": TERMINAL_MATERIAL_PROMPT},
        "source_ids": {
            "goalpost": "exec-c5216855-e804-4aac-a172-eef7a3c759d0",
            "material": "exec-123cc800-3fe4-410d-bc88-bf0ed127c537",
        },
        "input_paths": [],
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", choices=sorted(FAMILIES), action="append")
    return parser.parse_args()


def crop_cells(
    source_root: Path,
    source_name: str,
    cells: dict[str, tuple[float, float, float, float]],
) -> None:
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
        "input_paths": spec.get("input_paths", []),
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
            *spec.get("extra_sources", []),
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
        lod: dict(payload["zones"]["facade"][lod]) for lod in ("near", "far")
    }
    manifest_path.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    selected = args.family or sorted(FAMILIES)
    for family in selected:
        spec = FAMILIES[family]
        source_root = FAMILY_ROOT / family / "textures" / "source"
        crop_cells(source_root, "archetype-goalpost.png", spec["goalpost_cells"])
        crop_cells(
            source_root,
            "material-construction-source-v1.png",
            spec["material_cells"],
        )
        write_provenance(family, spec)
        prepare_family(family, spec["config"], batch_label="wave12")
        bind_atlas(family)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
