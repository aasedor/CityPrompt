"""Prepare reference-locked PBR packages for the Wave 13 diverse families.

Each family owns a coherent four-view goalpost board and a shadow-neutral
construction plate generated from its selected catalogue variant.  This file
keeps the exact prompts, crops, registration contracts, and source ids so the
approved visual design can be reproduced without conversation history.
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from PIL import Image, ImageOps

from prepare_wave8_reference_skins import FAMILY_ROOT, prepare_family


ART_DECO_GOALPOST_PROMPT = """Use case: photorealistic-natural
Asset type: render-locked four-view architectural reconstruction board for a CityPrompt LEGO building family
Input images: Image 1 is the sole archetype, massing, proportion, ornament, and palette authority.
Primary request: Reconstruct the exact same cream terra-cotta and gold Art Deco setback tower from Image 1 as one coherent true-metric building shown in four equal panels arranged in a precise 2 by 2 grid.
Panel 1: dead-front orthographic elevation, front facade parallel to camera, complete building and crown visible.
Panel 2: pedestrian-height front-right three-quarter architectural survey view.
Panel 3: rear-left three-quarter view proving that terra-cotta piers, punched windows, setbacks, and service elevation wrap the entire tower.
Panel 4: high aerial roof-plan oblique proving every setback terrace, roof deck, octagonal lantern, gilded posts, and finial.
Building lock: approximately 30 m wide by 28 m deep; exactly 15 occupied levels above a dark polished-granite and bronze double-height public podium; a tall seven-bay lower shaft; progressively narrower five-bay and three-bay setback stages; strong continuous vertical cream glazed-terra-cotta piers; dark recessed bronze residential/office windows with real occupied depth; shallow geometric spandrel relief; sunburst ornament at the first major setback; a compact octagonal dark-glass lantern framed by eight separate gilded posts and a faceted gilded cap and finial. Preserve the same setback heights and footprint relationships in all four panels.
Scene/backdrop: clean warm-light-grey architectural studio ground and backdrop, no neighboring buildings, no trees, no cars, no people.
Style/medium: premium photoreal architectural photography and physically plausible construction reference, not concept art.
Lighting/mood: neutral bright overcast survey illumination with soft contact shadows and controlled glazing reflections; consistent lighting in all panels.
Materials/textures: cream glazed architectural terra cotta with fine joints and restrained age variation; charcoal-black polished granite podium; dark bronze doors, frames, and grilles; neutral smoky low-e windows with sparse warm occupied rooms; restrained gold-leaf ornament and lantern metalwork.
Constraints: exact same building topology, 15 occupied levels, floor datums, bay cadence, setback count, crown, entrance position, material zones, and proportions in every panel; panels separated only by thin neutral gutters; complete tower inside every frame; no labels; no text; no signs; no logos; no watermark.
Avoid: generic rectangular skyscraper, extra floors, missing setbacks, pyramidal wedding-cake fantasy, oversized gold ornament, blue mirrored glass, blank sides, flat pasted windows, changed crown between views, perspective-distorted front elevation, entourage, dramatic sunset."""


ART_DECO_MATERIAL_PROMPT = """Use case: photorealistic-natural
Asset type: shadow-neutral 3 by 2 construction and occupied-depth material board for the exact cream terra-cotta Art Deco tower in Image 1
Input images: Image 1 is the approved palette, finish, and architectural-scale authority.
Primary request: Create six equal square straight-on orthographic material samples in a precise 3-column by 2-row grid separated only by thin neutral-grey gutters, with no labels.
Top-left: cream glazed architectural terra-cotta ashlar and narrow geometric relief joints, real 300 to 600 mm unit scale, subtle warm ivory variation, no windows or building perspective.
Top-center: charcoal-black polished granite podium panels with restrained pale mineral veining and fine construction joints, no reflections of a scene.
Top-right: aged dark bronze architectural frames and entrance grille metal with fine brushed grain and slight patina, no door or grille pattern baked across the sample.
Bottom-left: neutral smoky low-e vision glass with restrained grey-green reflection variation, no mullion grid, no complete facade, suitable for physical panes.
Bottom-center: a clean warm occupied Art Deco tower room-depth plate seen straight through glass, with dark room volume, subtle curtains, ceiling edge, one warm lamp zone, and human scale but absolutely no exterior frame, text, furniture focal point, or building perspective.
Bottom-right: restrained gold-leaf and gilded architectural metal with fine hand-laid texture and slight age variation, not mirror chrome and not glitter.
Scene/backdrop: flat evenly lit material-capture setup.
Style/medium: physically based photoreal architectural construction texture reference with fine real-world micro-detail.
Lighting/mood: diffuse neutral overcast capture; no directional sunlight; no baked cast shadow; no vignette; no perspective.
Constraints: exact 3 by 2 grid; each material fills its cell edge-to-edge; straight-on orthographic samples; no labels; no text; no logos; no watermark; no complete facade; no repeated windows; no ornamental motif larger than real construction scale.
Avoid: beige stucco, cartoon gold, blue mirror glass, oversized veining, dramatic lighting, perspective scene, decorative border."""


MACHIYA_GOALPOST_PROMPT = """Use case: photorealistic-natural
Asset type: render-locked four-view architectural reconstruction board for a CityPrompt LEGO building family
Input images: Image 1 is the sole archetype, massing, construction, proportion, and palette authority.
Primary request: Reconstruct the exact same restored Kyoto machiya from Image 1 as one coherent true-metric two-storey building shown in four equal panels arranged in a precise 2 by 2 grid.
Panel 1: dead-front orthographic elevation, facade parallel to camera, complete roof and ground sill visible.
Panel 2: pedestrian-height front-right three-quarter architectural survey view.
Panel 3: rear-left three-quarter view proving timber frame, white clay infill, garden-side openings, gutters, and roof construction wrap the whole building.
Panel 4: high aerial roof-plan oblique proving the deep tiled gable roof, lower street eave, ridge caps, gutters, and small side passage.
Building lock: approximately 18 m wide by 14 m deep by 10.8 m high; exactly two occupied storeys; dark stained Japanese timber post-and-beam frame; white lime-clay infill at the gable and selected wall panels; a continuous upper-storey deep koshi timber lattice screen with narrow real gaps in front of warm recessed glazing; ground floor shopfront lattice and one deeply recessed entrance; three separate indigo noren fabric panels below the lower tiled eave; a planted side passage; one large steep ceramic kawara-tile gable roof with deep eaves and exposed rafters plus a lower street canopy roof; authentic ridge-end and eave tile rhythm. Preserve identical bay positions and roof geometry in every view.
Scene/backdrop: clean warm-light-grey architectural studio ground and backdrop, no neighboring buildings, no trees except the tiny integral side garden, no cars, no people.
Style/medium: premium photoreal architectural photography and physically plausible construction reference, not concept art.
Lighting/mood: neutral bright overcast survey illumination with soft contact shadows and controlled glazing reflections; consistent lighting in all panels.
Materials/textures: dark weathered cedar and cypress; warm brown koshi lattice; matte white clay plaster; charcoal-grey kawara ceramic tiles with distinct individual rows; neutral slightly smoky glass with sparse warm occupied depth; woven indigo noren; blackened copper gutters and downpipes; pebble garden and bamboo.
Constraints: exact same building topology, two storeys, floor datums, post-and-beam bays, lattice spacing, entrance, eave heights, roof pitch, material zones and proportions in every panel; panels separated only by thin neutral gutters; complete building inside every frame; no labels; no text or calligraphy on the noren; no signs; no logos; no watermark.
Avoid: generic Asian house, temple, pagoda, extra floors, cartoon roof, thatch, oversized lattice, solid lattice with no gaps, flat roof, baked-on windows, blue mirror glass, blank sides, changed roof between views, entourage, dramatic sunset."""


MACHIYA_MATERIAL_PROMPT = """Use case: photorealistic-natural
Asset type: shadow-neutral 3 by 2 construction and occupied-depth material board for the exact restored Kyoto machiya in Image 1
Input images: Image 1 is the approved palette, finish, and construction-scale authority.
Primary request: Create six equal square straight-on orthographic material samples in a precise 3-column by 2-row grid separated only by thin neutral-grey gutters, with no labels.
Top-left: dark weathered Japanese cedar and cypress post-and-beam timber, authentic fine vertical grain and restrained age variation, no facade or complete framing pattern.
Top-center: warm brown fine koshi lattice timber with several narrow real slats and actual dark gaps at architectural scale, straight-on and tileable, not a whole window.
Top-right: charcoal-grey glazed kawara ceramic roof tiles in authentic overlapping rows with restrained highlights, correct small building scale and no roof perspective.
Bottom-left: matte warm-white lime-clay plaster with subtle hand-troweled mineral texture, no cracks or ornaments.
Bottom-center: neutral slightly smoky physical glazing plus a clean warm occupied machiya room-depth plate seen straight through it, with dark recessed room, shoji glow and one restrained warm lamp zone, absolutely no exterior lattice or frame.
Bottom-right: woven deep-indigo noren fabric with visible textile weave, subtle folds and plain unprinted field, no lettering or symbols.
Scene/backdrop: flat evenly lit material-capture setup.
Style/medium: physically based photoreal architectural construction texture reference with fine real-world micro-detail.
Lighting/mood: diffuse neutral overcast capture; no directional sunlight; no baked cast shadow; no vignette; no perspective.
Constraints: exact 3 by 2 grid; each material fills its cell edge-to-edge; straight-on orthographic samples; no labels; no text; no calligraphy; no logos; no watermark; no complete facade; no oversized motif.
Avoid: cartoon wood, orange varnish, temple ornament, blue glass, generic shingles, cloth signage, dramatic lighting, perspective scene, decorative border."""


PAVILION_GOALPOST_PROMPT = """Use case: photorealistic-natural
Asset type: render-locked four-view architectural reconstruction board for a CityPrompt LEGO building family
Input images: Image 1 is the sole archetype, massing, structural rhythm, proportion, and palette authority.
Primary request: Reconstruct the exact same mid-century modern glass-and-steel pavilion from Image 1 as one coherent true-metric three-level building shown in four equal panels arranged in a precise 2 by 2 grid.
Panel 1: dead-front orthographic elevation, facade parallel to camera, full floating roof and travertine plinth visible.
Panel 2: pedestrian-height front-right three-quarter architectural survey view.
Panel 3: rear-left three-quarter view proving black steel frame, clear curtain wall, floor plates, service core, and secondary entrances wrap the whole building.
Panel 4: high aerial roof-plan oblique proving the very thin flat roof plane, deep asymmetric cantilevered eaves, recessed curtain-wall box and solid travertine service volume.
Building lock: approximately 25 m wide by 18 m deep by 12.2 m high; exactly three transparent occupied levels; a slender matte-black steel post-and-beam frame at roughly 3.6 m bays; neutral low-iron curtain wall physically recessed behind the frame; visible concrete floor plates and warm occupied interior depth; a pale honed travertine plinth and one solid side service core; one exceptionally thin pale roof plane floating above the glass with a deep front and side cantilever, crisp knife edge, and no parapet. Preserve identical column, mullion, slab and core positions in every view.
Scene/backdrop: clean warm-light-grey architectural studio ground and backdrop, no neighboring buildings, no trees, no cars, no people.
Style/medium: premium photoreal architectural photography and physically plausible construction reference, not concept art.
Lighting/mood: neutral bright overcast survey illumination with soft contact shadows and controlled glazing reflections; consistent lighting in all panels.
Materials/textures: fine matte-black painted structural steel; neutral clear low-iron glazing with subtle grey reflection; warm occupied offices/gallery depth; pale honed travertine with fine horizontal joints; light-grey concrete slab edges; warm-white aluminum roof soffit and knife-edge fascia.
Constraints: exact same topology, three levels, bay cadence, floor datums, column positions, service core, cantilever depths, entrance location and proportions in every panel; panels separated only by thin neutral gutters; complete pavilion inside every frame; no labels; no text; no signs; no logos; no watermark.
Avoid: generic glass cube, office tower, extra floors, thick roof, blue mirrored glass, solid opaque walls replacing glazing, painted-on mullions, blank rear, changed column grid, Mies copy label, entourage, dramatic sunset."""


PAVILION_MATERIAL_PROMPT = """Use case: photorealistic-natural
Asset type: shadow-neutral 3 by 2 construction and occupied-depth material board for the exact mid-century glass-and-steel pavilion in Image 1
Input images: Image 1 is the approved palette, finish, and architectural-scale authority.
Primary request: Create six equal square straight-on orthographic material samples in a precise 3-column by 2-row grid separated only by thin neutral-grey gutters, with no labels.
Top-left: matte-black painted structural steel with fine rolled-metal grain and restrained edge wear, no beam or frame shape.
Top-center: neutral low-iron architectural vision glass with subtle grey sky reflection variation, no blue tint, no mullion grid, suitable for separate physical panes.
Top-right: pale honed travertine panels with fine horizontal bedding, restrained pores and subtle warm variation at 600 to 1200 mm construction scale.
Bottom-left: light-grey smooth concrete floor slab edge and plinth material with fine mineral aggregate and no wall pattern.
Bottom-center: clean warm occupied gallery and office depth viewed straight through clear glass, dark room volume, ceiling plane and restrained warm lights, no exterior frame, no perspective facade, no focal furniture.
Bottom-right: warm-white finely ribbed aluminum roof soffit and smooth knife-edge fascia finish, fine linear scale, no complete roof.
Scene/backdrop: flat evenly lit material-capture setup.
Style/medium: physically based photoreal architectural construction texture reference with fine real-world micro-detail.
Lighting/mood: diffuse neutral overcast capture; no directional sunlight; no baked cast shadow; no vignette; no perspective.
Constraints: exact 3 by 2 grid; each material fills its cell edge-to-edge; straight-on orthographic samples; no labels; no text; no logos; no watermark; no complete facade; no repeated windows.
Avoid: chrome, blue mirrored glass, beige marble, coarse concrete, cartoon materials, dramatic lighting, perspective scene, decorative border."""


PAVILION_OPTICAL_REFINEMENT_PROMPT = """Use case: photorealistic-natural
Asset type: shadow-neutral optical construction source board for the exact mid-century glass-and-steel pavilion
Input images: Image 1 is the approved pavilion glazing, structure, palette, transparency, and occupation authority. Image 2 is the prior construction plate; retain its realistic material scale but improve the optical separation.
Primary request: Create six equal square, straight-on orthographic samples in a precise 3-column by 2-row grid, separated only by thin neutral-grey gutters and with no labels.
Top-left: crystal-clear neutral low-iron architectural glass, faint soft grey exterior-sky reflection variation and an extremely subtle green edge cast, no blue mirror tint, no room, no mullions, no frame, no facade.
Top-center: bright daytime occupied gallery depth seen dead-on from outside, pale ceiling and floor receding at least three metres, one quiet partition and restrained furniture silhouettes, neutral daylight, no exterior glass, frame, mullion, facade, or directional perspective skew.
Top-right: softly occupied evening gallery depth seen dead-on from outside, the same pale ceiling and floor, sparse warm downlights and dark recesses, warm but not brown or orange, no exterior glass, frame, mullion, facade, or directional perspective skew.
Bottom-left: pale acoustic ceiling material with small recessed downlight apertures at real architectural scale, evenly lit, no room perspective.
Bottom-center: pale honed gallery floor with fine construction joints at real scale, evenly lit, no room perspective.
Bottom-right: fine matte-black powder-coated steel pressure-cap finish with restrained rolled-metal grain, no beam, frame, grid, or silhouette.
Scene/backdrop: flat evenly lit material-capture setup.
Style/medium: premium physically based photoreal architectural construction texture reference.
Lighting/mood: diffuse neutral overcast capture; no baked sunlight, cast shadow, vignette, or dramatic contrast.
Constraints: exact 3 by 2 grid; each sample fills its cell edge-to-edge; clean orthographic registration; no labels; no text; no logos; no watermark; no whole windows or facades. Preserve the low-iron, highly transparent optical character and pale occupied interiors of Image 1.
Avoid: smoked brown glass, blue mirror glass, repeated bottle-like lights, opaque room cards, complete window grids, cartoon materials, decorative borders."""


TRANSIT_GOALPOST_PROMPT = """Use case: photorealistic-natural
Asset type: render-locked four-view architectural reconstruction board for a CityPrompt LEGO building family
Input images: Image 1 is the sole archetype, massing, programme, structural rhythm, proportion, and palette authority.
Primary request: Reconstruct the exact same timber-and-glass transit station block from Image 1 as one coherent true-metric six-level building shown in four equal panels arranged in a precise 2 by 2 grid.
Panel 1: dead-front orthographic elevation, facade parallel to camera, full entrance canopy, glass concourse, timber upper block, green roof and PV visible.
Panel 2: pedestrian-height front-right three-quarter architectural survey view.
Panel 3: rear-left three-quarter view proving the glass concourse, platform-side elevation, timber rainscreen, louver bays, cores, and roof construction wrap the whole building.
Panel 4: high aerial roof-plan oblique proving the broad flat green roof, two photovoltaic canopy strips, service zone, entrance canopy and simple rectangular footprint.
Building lock: approximately 58 m wide by 34 m deep by 27 m high; exactly six occupied levels; a double-height transparent public transit concourse plus one glazed mezzanine level forming the lower three-level base; real low-iron curtain wall with slim dark mullions, visible floor plates, escalator/wayfinding depth and multiple recessed entrance doors; three upper levels in warm reddish-brown timber rainscreen organized as long horizontal bands, with regularly alternating full-height windows and dense external timber louver screens; thin projecting timber belt courses between upper floors; one broad steel-and-glass entrance canopy integrated across the street facade; rooftop planting, restrained trees, and two slender photovoltaic canopy rows. Preserve identical bay positions, level heights, glass-to-timber break, entrance and roof layout in every view.
Scene/backdrop: clean warm-light-grey architectural studio ground and backdrop, no neighboring buildings, no street trees, no cars, no people.
Style/medium: premium photoreal architectural photography and physically plausible construction reference, not concept art.
Lighting/mood: neutral bright overcast survey illumination with soft contact shadows and controlled glazing reflections; consistent lighting in all panels.
Materials/textures: neutral high-transmission curtain wall; graphite aluminum pressure caps and steel canopy; warm occupied transit-hall depth; reddish-brown durable timber rainscreen and matching narrow louver blades; pale concrete floor slabs; planted green roof; dark-blue photovoltaic glass.
Constraints: exact same topology, six levels, floor datums, structural and mullion cadence, upper louver rhythm, entrance canopy and roof features in every panel; panels separated only by thin neutral gutters; complete station inside every frame; no labels; no text; no transit logos; no signs; no watermark.
Avoid: generic office tower, extra floors, timber lower concourse, blue mirrored box, opaque transit base, pasted louver texture, blank rear, giant rooftop trees, changed bay grid, railway tracks dominating image, entourage, dramatic sunset."""


TRANSIT_MATERIAL_PROMPT = """Use case: photorealistic-natural
Asset type: shadow-neutral 3 by 2 construction and occupied-depth material board for the exact timber-and-glass transit station in Image 1
Input images: Image 1 is the approved palette, finish, and architectural-scale authority.
Primary request: Create six equal square straight-on orthographic material samples in a precise 3-column by 2-row grid separated only by thin neutral-grey gutters, with no labels.
Top-left: warm reddish-brown durable exterior timber rainscreen boards with fine vertical grain and restrained natural variation, no facade pattern.
Top-center: matching dark timber external louver blades shown as several narrow real slats with genuine dark gaps, straight-on architectural scale, not a whole window.
Top-right: neutral high-transmission low-iron curtain-wall glass with subtle grey reflection, no blue mirror tint and no mullion grid, suitable for physical panes.
Bottom-left: graphite powder-coated aluminum pressure caps and structural steel with fine matte grain, no complete beam shape.
Bottom-center: clean warm occupied transit-concourse depth viewed straight through glass, with a large dark room volume, pale ceiling, escalator hint and restrained warm lights, no exterior frame, no signage, no text, no facade perspective.
Bottom-right: planted extensive green-roof sedum and dark-blue photovoltaic glass as two construction-scale adjacent material fields, evenly lit and without a complete roof scene.
Scene/backdrop: flat evenly lit material-capture setup.
Style/medium: physically based photoreal architectural construction texture reference with fine real-world micro-detail.
Lighting/mood: diffuse neutral overcast capture; no directional sunlight; no baked cast shadow; no vignette; no perspective.
Constraints: exact 3 by 2 grid; each material fills its cell edge-to-edge; straight-on orthographic samples; no labels; no text; no transit logos; no watermark; no complete facade; no repeated windows.
Avoid: orange plastic wood, blue mirror glass, painted-on louvers, cartoon vegetation, dramatic lighting, perspective scene, decorative border."""


PASSIVE_GOALPOST_PROMPT = """Use case: photorealistic-natural
Asset type: render-locked four-view architectural reconstruction board for a CityPrompt LEGO building family
Input images: Image 1 is the sole archetype, massing, passive-building construction, proportion, and palette authority.
Primary request: Reconstruct the exact same passive-house timber urban block from Image 1 as one coherent true-metric four-storey building shown in four equal panels arranged in a precise 2 by 2 grid.
Panel 1: dead-front orthographic elevation, facade parallel to camera, complete dual-pitch roof and ground entrances visible.
Panel 2: pedestrian-height front-right three-quarter architectural survey view.
Panel 3: rear-left three-quarter view proving larch rainscreen, deep window reveals, ventilation louvers, service doors, downpipes and garden-side facade wrap the whole building.
Panel 4: high aerial roof-plan oblique proving the asymmetrical dual mono-pitch/gable roof, south photovoltaic field, north sedum strip, roof windows, gutters and end-wall PV panels.
Building lock: approximately 36 m wide by 20 m deep by 17 m high; exactly four occupied levels; a simple long rectangular urban block in natural vertical larch rainscreen; six strong front bays of deeply recessed triple-glazed openings; real timber-aluminum frames, dark insulated reveals, mixed clear panes and pale balcony/vent panels, and external horizontal sun blinds on selected middle windows; a deeply recessed central timber entrance and secondary ground openings; a steep asymmetrical roof whose sun-facing plane carries one continuous dark photovoltaic field while the other plane carries an extensive green-roof strip and several rooflights; crisp timber-clad gable ends with smaller punched windows and a vertical bank of facade PV panels. Preserve identical bay positions, roof pitches and environmental features in every view.
Scene/backdrop: clean warm-light-grey architectural studio ground and backdrop, no neighboring buildings, no street trees, no cars, no people.
Style/medium: premium photoreal architectural photography and physically plausible passive-house construction reference, not concept art.
Lighting/mood: neutral bright overcast survey illumination with soft contact shadows and controlled glazing reflections; consistent lighting in all panels.
Materials/textures: naturally weathering honey-brown vertical larch; dark bronze/charcoal timber-aluminum frames; neutral high-performance triple glazing with sparse warm occupied depth; pale translucent insulated balcony panels; black external blinds; dark-blue photovoltaic glass; dense green sedum; zinc gutters and flashings.
Constraints: exact same topology, four levels, six-bay cadence, floor datums, deep reveals, entrance, roof geometry, PV and green-roof fields in every panel; panels separated only by thin neutral gutters; complete building inside every frame; no labels; no text; no signs; no logos; no watermark.
Avoid: generic timber box, chalet, extra floors, shallow painted windows, orange plastic siding, blue mirrored glazing, arbitrary balconies, flat roof, missing photovoltaics, blank rear, changed bay grid, entourage, dramatic sunset."""


PASSIVE_MATERIAL_PROMPT = """Use case: photorealistic-natural
Asset type: shadow-neutral 3 by 2 construction and occupied-depth material board for the exact passive-house timber block in Image 1
Input images: Image 1 is the approved palette, finish, and construction-scale authority.
Primary request: Create six equal square straight-on orthographic material samples in a precise 3-column by 2-row grid separated only by thin neutral-grey gutters, with no labels.
Top-left: naturally weathering honey-brown vertical larch rainscreen boards with fine grain, narrow open joints and restrained color variation, no whole facade.
Top-center: dark bronze-charcoal timber-aluminum window frame and insulated reveal material with fine matte grain, no complete window.
Top-right: neutral high-performance triple glazing with restrained grey reflection variation, no blue mirror tint, no mullion grid, suitable for separate physical panes.
Bottom-left: black exterior venetian sun-blind blades shown as fine real horizontal slats with actual dark gaps, straight-on architectural scale, not a whole window.
Bottom-center: clean warm occupied passive-house room depth viewed straight through glass, with dark recessed volume, pale ceiling edge, subtle curtain and one restrained warm light zone, absolutely no exterior frame or facade perspective.
Bottom-right: dark-blue photovoltaic glass and dense extensive green-roof sedum as two adjacent construction-scale material fields, evenly lit, no complete roof scene.
Scene/backdrop: flat evenly lit material-capture setup.
Style/medium: physically based photoreal architectural construction texture reference with fine real-world micro-detail.
Lighting/mood: diffuse neutral overcast capture; no directional sunlight; no baked cast shadow; no vignette; no perspective.
Constraints: exact 3 by 2 grid; each material fills its cell edge-to-edge; straight-on orthographic samples; no labels; no text; no logos; no watermark; no complete facade; no repeated window grid.
Avoid: orange plastic siding, chrome frames, blue mirrored glass, painted blind texture, cartoon sedum, dramatic lighting, perspective scene, decorative border."""


PASSIVE_OPTICAL_PV_REFINEMENT_PROMPT = """Use case: photorealistic-natural
Asset type: shadow-neutral photovoltaic and window construction source board for the exact passive-house timber block
Input images: Image 1 is the approved passive-house roof, photovoltaic module, glazing, blind, and occupation authority. Image 2 is the prior construction plate and exact larch/frame palette authority.
Primary request: Create six equal square, straight-on orthographic samples in a precise 3-column by 2-row grid, separated only by thin neutral-grey gutters and with no labels.
Top-left: one complete contemporary dark-blue monocrystalline photovoltaic module viewed perfectly straight-on, realistic silver-black perimeter frame, visible dark inter-cell gaps, fine white busbars, six columns by ten rows of individual cells, uniform overcast reflection, generous narrow margin around the module, no roof or surrounding scene.
Top-center: neutral high-performance triple glazing viewed straight-on, restrained grey daylight reflection, a faint green edge cast and subtle optical depth, no blue mirror tint, no frame, mullions, room, or facade.
Top-right: dark bronze-charcoal timber-aluminum passive-house frame and deep insulated reveal finish with fine matte grain, shown as material strips only, no whole window.
Bottom-left: bright daytime occupied passive-house room depth viewed dead-on from outside, pale timber floor and ceiling, sheer linen curtain partly drawn, quiet furniture silhouettes and garden-toned daylight beyond, at least three metres of visual depth, no exterior glass, frame, mullion, facade, or skewed perspective.
Bottom-center: softly occupied evening passive-house room depth viewed dead-on from outside, same pale timber interior with one restrained warm lamp and darker recesses, warm but not orange, no exterior glass, frame, mullion, facade, or skewed perspective.
Bottom-right: black exterior venetian blind construction at real scale, separate fine horizontal metal blades with genuine dark gaps, two slim guide cables and a compact headbox, straight-on, no complete window or wall.
Scene/backdrop: flat evenly lit material-capture setup.
Style/medium: premium physically based photoreal architectural construction texture reference.
Lighting/mood: diffuse neutral overcast capture; no baked sunlight, cast shadows, vignette, or dramatic contrast.
Constraints: exact 3 by 2 grid; each cell cleanly registered; no labels; no text; no logos; no watermark; no full facade. Photovoltaic cells must be countable and module-scale. Glass and occupied room depth must remain separate optical layers.
Avoid: one giant solar roof texture, diagonal PV perspective, amorphous blue sheet, blue mirrored windows, opaque window pictures, flat black blind texture, cartoon materials, decorative borders."""


GOALPOST_CELLS = {
    "front-elevation-source-v1.png": (0.002, 0.002, 0.498, 0.498),
    "street-hero-source-v1.png": (0.502, 0.002, 0.998, 0.498),
    "rear-corner-source-v1.png": (0.002, 0.502, 0.498, 0.998),
    "aerial-roof-source-v1.png": (0.502, 0.502, 0.998, 0.998),
}


FAMILIES: dict[str, dict] = {
    "art-deco-cream-terracotta-tower": {
        "archetype_id": "art_deco_setback_tower",
        "variant_id": "art_deco_cream_terracotta",
        "skin_schema": "art-deco-cream-terracotta-tower-skin@1",
        "goalpost_cells": GOALPOST_CELLS,
        "material_cells": {
            "terracotta-material-source-v1.png": (0.002, 0.002, 0.331, 0.498),
            "granite-material-source-v1.png": (0.335, 0.002, 0.665, 0.498),
            "bronze-material-source-v1.png": (0.669, 0.002, 0.998, 0.498),
            "vision-glass-material-source-v1.png": (0.002, 0.502, 0.331, 0.998),
            "occupied-depth-source-v1.png": (0.335, 0.502, 0.665, 0.998),
            "gold-material-source-v1.png": (0.669, 0.502, 0.998, 0.998),
        },
        "config": {
            "archetype_id": "art_deco_setback_tower",
            "variant_id": "art_deco_cream_terracotta",
            "skin_schema": "art-deco-cream-terracotta-tower-skin@1",
            "elevation_source": "front-elevation-source-v1.png",
            "occupied_depth_source": "occupied-depth-source-v1.png",
            "bands": {
                "facade": (0.205, 0.020, 0.795, 0.970),
                "podium": (0.205, 0.830, 0.795, 0.970),
                "floor_a": (0.245, 0.620, 0.755, 0.825),
                "floor_b": (0.300, 0.400, 0.700, 0.610),
                "crown": (0.340, 0.015, 0.660, 0.385),
                "side": (0.205, 0.250, 0.390, 0.900),
            },
            "prefixes": {
                "facade": "art_deco_registered_front",
                "podium": "black_granite_bronze_podium",
                "floor_a": "seven_bay_terracotta_shaft_floor_a",
                "floor_b": "five_bay_setback_floor_b",
                "crown": "octagonal_gilded_lantern_crown",
                "side": "wrapped_terracotta_secondary_elevation",
                "interior": "occupied_art_deco_room_depth",
                "terracotta": "cream_glazed_architectural_terracotta",
                "granite": "charcoal_polished_granite",
                "bronze": "aged_dark_architectural_bronze",
                "vision_glass": "neutral_smoky_low_e_glass",
                "gold": "restrained_architectural_gold_leaf",
                "roof": "dark_setback_terrace_membrane",
            },
            "support": {
                "terracotta": ((221, 207, 177), "stone", 13101),
                "granite": ((30, 31, 30), "stone", 13111),
                "bronze": ((84, 58, 35), "metal", 13121),
                "vision_glass": ((91, 100, 96), "glass", 13131),
                "gold": ((183, 143, 65), "metal", 13141),
                "roof": ((65, 67, 64), "stone", 13151),
            },
            "support_sources": {
                "terracotta": "terracotta-material-source-v1.png",
                "granite": "granite-material-source-v1.png",
                "bronze": "bronze-material-source-v1.png",
                "vision_glass": "vision-glass-material-source-v1.png",
                "gold": "gold-material-source-v1.png",
                "roof": "granite-material-source-v1.png",
            },
            "registered_surfaces": [
                "double_height_black_granite_and_bronze_public_podium",
                "seven_bay_cream_terracotta_lower_shaft",
                "progressive_five_and_three_bay_setback_stages",
                "physical_recessed_bronze_windows_with_occupied_depth",
                "continuous_vertical_piers_and_geometric_spandrel_relief",
                "sunburst_ornament_at_first_major_setback",
                "octagonal_dark_glass_lantern_with_eight_gilded_posts",
                "complete_setback_terraces_and_wrapped_secondary_elevations",
            ],
            "registration": (
                "The four-view board locks one fifteen-level cream glazed terra-"
                "cotta tower with one black granite podium, a seven-bay shaft, "
                "progressive setback tiers and one compact gilded octagonal lantern."
            ),
            "opening_method": (
                "Every punched opening is a real recessed cavity with terra-cotta "
                "returns, bronze frame, neutral physical pane and a separately "
                "registered warm occupied-depth plate."
            ),
            "generic_tiling_allowed": False,
        },
        "design_lock": {
            "native_building_dimensions_m": [30.0, 28.0, 74.5],
            "native_envelope_dimensions_m": [31.0, 29.0, 77.0],
            "occupied_storeys": 15,
            "primary_material": "cream glazed architectural terra cotta",
            "window_rule": "dark bronze recessed frames, neutral smoky physical glass, sparse warm occupied depth",
            "front_identity": "seven-bay vertical shaft stepping to five and three bay stages above a black granite podium",
            "roof_rule": "complete setback terraces terminating in one octagonal dark-glass lantern with eight gilded posts and finial",
        },
        "prompts": {
            "goalpost": ART_DECO_GOALPOST_PROMPT,
            "material": ART_DECO_MATERIAL_PROMPT,
        },
        "source_ids": {
            "goalpost": "exec-4614de9d-2065-43a1-a3d9-0a48f0470072",
            "material": "exec-148ad30f-7fbd-44a3-b871-e539c87b007a",
        },
        "input_paths": [
            "/archetypes/buildings/art_deco_setback_tower/variant_0.png",
        ],
    },
    "restored-kyoto-machiya": {
        "archetype_id": "japanese_machiya_mixed_use",
        "variant_id": "machiya_traditional_restored",
        "skin_schema": "restored-kyoto-machiya-skin@1",
        "goalpost_cells": GOALPOST_CELLS,
        "material_cells": {
            "timber-material-source-v1.png": (0.002, 0.002, 0.331, 0.498),
            "lattice-material-source-v1.png": (0.335, 0.002, 0.665, 0.498),
            "tile-material-source-v1.png": (0.669, 0.002, 0.998, 0.498),
            "plaster-material-source-v1.png": (0.002, 0.502, 0.331, 0.998),
            "occupied-depth-source-v1.png": (0.335, 0.502, 0.665, 0.998),
            "indigo-material-source-v1.png": (0.669, 0.502, 0.998, 0.998),
        },
        "config": {
            "archetype_id": "japanese_machiya_mixed_use",
            "variant_id": "machiya_traditional_restored",
            "skin_schema": "restored-kyoto-machiya-skin@1",
            "elevation_source": "front-elevation-source-v1.png",
            "occupied_depth_source": "occupied-depth-source-v1.png",
            "bands": {
                "facade": (0.045, 0.09, 0.955, 0.94),
                "podium": (0.055, 0.58, 0.945, 0.94),
                "floor_a": (0.08, 0.50, 0.92, 0.76),
                "floor_b": (0.08, 0.26, 0.92, 0.53),
                "crown": (0.04, 0.06, 0.96, 0.35),
                "side": (0.04, 0.22, 0.28, 0.90),
            },
            "prefixes": {
                "facade": "machiya_registered_front",
                "podium": "machiya_shopfront_and_entry",
                "floor_a": "machiya_ground_lattice_bay",
                "floor_b": "machiya_upper_koshi_bay",
                "crown": "machiya_kawara_gable_and_eaves",
                "side": "machiya_wrapped_secondary_elevation",
                "interior": "occupied_machiya_room_depth",
                "timber": "dark_weathered_japanese_cedar",
                "lattice": "warm_brown_koshi_lattice",
                "tile": "charcoal_glazed_kawara_tile",
                "plaster": "matte_white_lime_clay_plaster",
                "vision_glass": "neutral_smoky_machiya_glass",
                "indigo": "plain_woven_indigo_noren",
                "stone": "grey_machiya_sill_and_pebble",
            },
            "support": {
                "timber": ((65, 45, 31), "wood", 13201),
                "lattice": ((83, 54, 34), "wood", 13211),
                "tile": ((54, 55, 54), "stone", 13221),
                "plaster": ((223, 218, 205), "stone", 13231),
                "vision_glass": ((71, 77, 73), "glass", 13241),
                "indigo": ((28, 43, 67), "fabric", 13251),
                "stone": ((91, 91, 84), "stone", 13261),
            },
            "support_sources": {
                "timber": "timber-material-source-v1.png",
                "lattice": "lattice-material-source-v1.png",
                "tile": "tile-material-source-v1.png",
                "plaster": "plaster-material-source-v1.png",
                "vision_glass": "occupied-depth-source-v1.png",
                "indigo": "indigo-material-source-v1.png",
            },
            "registered_surfaces": [
                "dark_post_and_beam_frame_with_white_clay_infill",
                "continuous_upper_koshi_screen_with_real_gaps",
                "ground_shop_lattice_and_deep_recessed_entry",
                "three_plain_indigo_noren_panels",
                "large_kawara_gable_and_lower_street_eave",
                "exposed_rafters_ridge_caps_gutters_and_downpipes",
                "complete_rear_service_and_integral_side_garden",
            ],
            "registration": "The four-view board locks one two-storey restored Kyoto machiya with one deep tiled gable, one lower street eave, continuous upper koshi lattice and one recessed noren entrance.",
            "opening_method": "All public openings sit behind separate fine timber lattice with real gaps, then physical smoky glazing and warm occupied room depth; the entrance is a true recess below the lower eave.",
            "generic_tiling_allowed": False,
        },
        "design_lock": {
            "native_building_dimensions_m": [18.0, 14.0, 10.8],
            "native_envelope_dimensions_m": [19.4, 15.4, 11.4],
            "occupied_storeys": 2,
            "primary_material": "dark weathered Japanese cedar post-and-beam frame",
            "window_rule": "fine koshi lattice with real gaps ahead of smoky panes and warm occupied depth",
            "front_identity": "continuous upper lattice above a lower tiled eave, ground shop lattice, three plain indigo noren and recessed entry",
            "roof_rule": "one deep kawara-tile gable with exposed rafters plus one lower street canopy roof",
        },
        "prompts": {"goalpost": MACHIYA_GOALPOST_PROMPT, "material": MACHIYA_MATERIAL_PROMPT},
        "source_ids": {"goalpost": "exec-bba3be99-49a5-497b-888f-4251f1a3dead", "material": "exec-45eef64c-966b-4560-8326-e06061383375"},
        "input_paths": ["/archetypes/buildings/japanese_machiya_mixed_use/variant_0.png"],
    },
    "mid-century-glass-steel-pavilion": {
        "archetype_id": "mid_century_modern_pavilion_block",
        "variant_id": "mid_century_pavilion_glass_steel",
        "skin_schema": "mid-century-glass-steel-pavilion-skin@2",
        "goalpost_cells": GOALPOST_CELLS,
        "material_cells": {
            "steel-material-source-v1.png": (0.002, 0.002, 0.331, 0.498),
            "vision-glass-material-source-v1.png": (0.335, 0.002, 0.665, 0.498),
            "travertine-material-source-v1.png": (0.669, 0.002, 0.998, 0.498),
            "concrete-material-source-v1.png": (0.002, 0.502, 0.331, 0.998),
            "occupied-depth-source-v1.png": (0.335, 0.502, 0.665, 0.998),
            "soffit-material-source-v1.png": (0.669, 0.502, 0.998, 0.998),
        },
        "refinement_source": "optical-construction-source-v2.png",
        "refinement_cells": {
            "vision-glass-material-source-v2.png": (0.002, 0.002, 0.331, 0.498),
            "occupied-day-depth-source-v2.png": (0.335, 0.002, 0.665, 0.498),
            "occupied-evening-depth-source-v2.png": (0.669, 0.002, 0.998, 0.498),
            "ceiling-material-source-v2.png": (0.002, 0.502, 0.331, 0.998),
            "gallery-floor-material-source-v2.png": (0.335, 0.502, 0.665, 0.998),
            "steel-material-source-v2.png": (0.669, 0.502, 0.998, 0.998),
        },
        "config": {
            "archetype_id": "mid_century_modern_pavilion_block",
            "variant_id": "mid_century_pavilion_glass_steel",
            "skin_schema": "mid-century-glass-steel-pavilion-skin@2",
            "elevation_source": "front-elevation-source-v1.png",
            "occupied_depth_source": "occupied-day-depth-source-v2.png",
            "bands": {
                "facade": (0.06, 0.18, 0.94, 0.87),
                "podium": (0.06, 0.70, 0.94, 0.88),
                "floor_a": (0.14, 0.55, 0.88, 0.74),
                "floor_b": (0.14, 0.36, 0.88, 0.55),
                "crown": (0.015, 0.14, 0.985, 0.30),
                "side": (0.05, 0.24, 0.30, 0.82),
            },
            "prefixes": {
                "facade": "pavilion_registered_front",
                "podium": "travertine_plinth_and_entry",
                "floor_a": "pavilion_complete_glazed_bay_a",
                "floor_b": "pavilion_complete_glazed_bay_b",
                "crown": "floating_knife_edge_roof",
                "side": "wrapped_glass_and_service_core",
                "interior": "occupied_pavilion_gallery_depth_day",
                "interior_evening": "occupied_pavilion_gallery_depth_evening",
                "steel": "matte_black_structural_steel",
                "vision_glass": "neutral_low_iron_pavilion_glass",
                "travertine": "pale_honed_travertine",
                "concrete": "light_grey_smooth_concrete",
                "ceiling": "pale_acoustic_gallery_ceiling",
                "gallery_floor": "pale_honed_gallery_floor",
                "soffit": "warm_white_ribbed_aluminum_soffit",
                "roof": "pale_knife_edge_roof_membrane",
            },
            "support": {
                "interior_evening": ((169, 145, 114), "interior", 13291),
                "steel": ((42, 43, 42), "metal", 13301),
                "vision_glass": ((126, 136, 136), "glass", 13311),
                "travertine": ((207, 197, 180), "stone", 13321),
                "concrete": ((184, 184, 178), "stone", 13331),
                "ceiling": ((224, 218, 205), "stone", 13336),
                "gallery_floor": ((208, 202, 190), "stone", 13338),
                "soffit": ((226, 221, 209), "metal", 13341),
                "roof": ((216, 214, 207), "metal", 13351),
            },
            "support_sources": {
                "interior_evening": "occupied-evening-depth-source-v2.png",
                "steel": "steel-material-source-v2.png",
                "vision_glass": "vision-glass-material-source-v2.png",
                "travertine": "travertine-material-source-v1.png",
                "concrete": "concrete-material-source-v1.png",
                "ceiling": "ceiling-material-source-v2.png",
                "gallery_floor": "gallery-floor-material-source-v2.png",
                "soffit": "soffit-material-source-v1.png",
                "roof": "soffit-material-source-v1.png",
            },
            "registered_surfaces": [
                "three_transparent_occupied_levels",
                "slender_black_steel_post_and_beam_frame",
                "physical_low_iron_curtain_wall_with_separate_day_and_evening_depth",
                "deep_gallery_floor_ceiling_and_partition_returns",
                "visible_concrete_floor_plates",
                "pale_travertine_plinth_and_solid_service_core",
                "exceptionally_thin_floating_roof_with_deep_asymmetric_cantilever",
                "complete_wrapped_secondary_elevations_and_rear_entry",
            ],
            "registration": "The four-view board locks one three-level transparent pavilion with a 3.6 metre black steel grid, one pale travertine core and one exceptionally thin cantilevered roof plane.",
            "opening_method": "Every curtain-wall bay is a separate high-transmission low-iron pane with fine pressure caps, a deep physical floor/ceiling cavity and alternating daylight or evening occupied depth at least 1.4 metres behind the weather plane.",
            "generic_tiling_allowed": False,
        },
        "design_lock": {
            "native_building_dimensions_m": [25.0, 18.0, 12.2],
            "native_envelope_dimensions_m": [29.0, 22.0, 12.6],
            "occupied_storeys": 3,
            "primary_material": "matte-black steel structure and neutral low-iron curtain wall",
            "window_rule": "individual clear panes behind a complete 3.6 metre structural grid with warm gallery depth",
            "front_identity": "three transparent levels, offset pale travertine service core and one floating knife-edge roof",
            "roof_rule": "single exceptionally thin pale plane with deep front and side cantilever and no parapet",
        },
        "prompts": {"goalpost": PAVILION_GOALPOST_PROMPT, "material": PAVILION_MATERIAL_PROMPT, "refinement": PAVILION_OPTICAL_REFINEMENT_PROMPT},
        "source_ids": {"goalpost": "exec-36d999e0-c95b-4844-b065-7c1e3b07350f", "material": "exec-3b03db1b-0130-4ee9-a96c-ccbf8be87b31", "refinement": "exec-df4a2711-d534-4b91-b2b9-3d9f70f9f6ee"},
        "input_paths": ["/archetypes/buildings/mid_century_modern_pavilion_block/variant_0.png"],
    },
    "timber-glass-transit-station-block": {
        "archetype_id": "transit_oriented_station_block",
        "variant_id": "transit_station_modern_glass",
        "skin_schema": "timber-glass-transit-station-block-skin@1",
        "goalpost_cells": GOALPOST_CELLS,
        "material_cells": {
            "timber-material-source-v1.png": (0.002, 0.002, 0.331, 0.498),
            "louver-material-source-v1.png": (0.335, 0.002, 0.665, 0.498),
            "vision-glass-material-source-v1.png": (0.669, 0.002, 0.998, 0.498),
            "steel-material-source-v1.png": (0.002, 0.502, 0.331, 0.998),
            "occupied-depth-source-v1.png": (0.335, 0.502, 0.665, 0.998),
            "green-roof-material-source-v1.png": (0.669, 0.502, 0.833, 0.998),
            "pv-material-source-v1.png": (0.833, 0.502, 0.998, 0.998),
        },
        "config": {
            "archetype_id": "transit_oriented_station_block",
            "variant_id": "transit_station_modern_glass",
            "skin_schema": "timber-glass-transit-station-block-skin@1",
            "elevation_source": "front-elevation-source-v1.png",
            "occupied_depth_source": "occupied-depth-source-v1.png",
            "bands": {
                "facade": (0.04, 0.10, 0.96, 0.90),
                "podium": (0.04, 0.56, 0.96, 0.91),
                "floor_a": (0.07, 0.42, 0.93, 0.65),
                "floor_b": (0.07, 0.18, 0.93, 0.42),
                "crown": (0.05, 0.06, 0.95, 0.22),
                "side": (0.04, 0.20, 0.26, 0.86),
            },
            "prefixes": {
                "facade": "transit_registered_front",
                "podium": "transparent_transit_concourse_and_canopy",
                "floor_a": "complete_glazed_concourse_bay",
                "floor_b": "complete_timber_louver_upper_bay",
                "crown": "green_roof_and_pv_canopies",
                "side": "wrapped_platform_and_timber_elevation",
                "interior": "occupied_transit_concourse_depth",
                "timber": "reddish_brown_transit_timber_rainscreen",
                "louver": "dark_timber_external_louver",
                "vision_glass": "neutral_high_transmission_transit_glass",
                "steel": "graphite_transit_steel_and_pressure_cap",
                "green_roof": "extensive_transit_green_roof",
                "pv": "dark_blue_photovoltaic_glass",
                "concrete": "pale_transit_floor_slab",
            },
            "support": {
                "timber": ((145, 86, 53), "wood", 13401),
                "louver": ((73, 54, 47), "wood", 13411),
                "vision_glass": ((137, 149, 148), "glass", 13421),
                "steel": ((47, 50, 51), "metal", 13431),
                "green_roof": ((86, 100, 53), "foliage", 13441),
                "pv": ((38, 51, 72), "glass", 13451),
                "concrete": ((180, 181, 177), "stone", 13461),
            },
            "support_sources": {
                "timber": "timber-material-source-v1.png",
                "louver": "louver-material-source-v1.png",
                "vision_glass": "vision-glass-material-source-v1.png",
                "steel": "steel-material-source-v1.png",
                "green_roof": "green-roof-material-source-v1.png",
                "pv": "pv-material-source-v1.png",
            },
            "registered_surfaces": [
                "double_height_transparent_public_concourse_and_mezzanine",
                "physical_curtain_wall_with_visible_floor_plates_and_depth",
                "integral_broad_steel_and_glass_entrance_canopy",
                "three_upper_timber_rainscreen_levels",
                "alternating_real_windows_and_external_louver_screens",
                "continuous_projecting_timber_belt_courses",
                "green_roof_two_pv_canopy_rows_and_screened_service_zone",
            ],
            "registration": "The four-view board locks one six-level station block with a transparent three-level concourse, three timber-and-louver upper levels, one integral street canopy and two PV rows on a green roof.",
            "opening_method": "The public base uses independent high-transmission panes, pressure caps, slabs and concourse depth; upper openings use separate panes and real external louver blades within complete timber bays.",
            "generic_tiling_allowed": False,
        },
        "design_lock": {
            "native_building_dimensions_m": [58.0, 34.0, 27.0],
            "native_envelope_dimensions_m": [62.0, 38.0, 29.5],
            "occupied_storeys": 6,
            "primary_material": "neutral glass public concourse beneath reddish-brown timber rainscreen",
            "window_rule": "real lower curtain-wall panes and alternating upper clear windows and external timber louver screens",
            "front_identity": "three transparent transit levels and three horizontally banded timber levels beneath green roof and twin PV canopies",
            "roof_rule": "broad extensive green roof with two long elevated photovoltaic canopy rows and screened service core",
        },
        "prompts": {"goalpost": TRANSIT_GOALPOST_PROMPT, "material": TRANSIT_MATERIAL_PROMPT},
        "source_ids": {"goalpost": "exec-908ce2e1-d897-4146-8481-a5885f4da534", "material": "exec-eb38b48f-1f66-4f16-ab5b-e0eda67fa115"},
        "input_paths": ["/archetypes/buildings/transit_oriented_station_block/variant_0.png"],
    },
    "passive-house-timber-block": {
        "archetype_id": "eco_urban_bioclimatic_block",
        "variant_id": "eco_bioclimatic_passive",
        "skin_schema": "passive-house-timber-block-skin@2",
        "goalpost_cells": GOALPOST_CELLS,
        "material_cells": {
            "larch-material-source-v1.png": (0.002, 0.002, 0.331, 0.498),
            "frame-material-source-v1.png": (0.335, 0.002, 0.665, 0.498),
            "vision-glass-material-source-v1.png": (0.669, 0.002, 0.998, 0.498),
            "blind-material-source-v1.png": (0.002, 0.502, 0.331, 0.998),
            "occupied-depth-source-v1.png": (0.335, 0.502, 0.665, 0.998),
            "pv-material-source-v1.png": (0.669, 0.502, 0.833, 0.998),
            "green-roof-material-source-v1.png": (0.833, 0.502, 0.998, 0.998),
        },
        "refinement_source": "optical-pv-construction-source-v2.png",
        "refinement_cells": {
            "pv-module-material-source-v2.png": (0.018, 0.018, 0.314, 0.482),
            "vision-glass-material-source-v2.png": (0.335, 0.002, 0.665, 0.498),
            "frame-material-source-v2.png": (0.669, 0.002, 0.998, 0.498),
            "occupied-day-depth-source-v2.png": (0.002, 0.502, 0.331, 0.998),
            "occupied-evening-depth-source-v2.png": (0.335, 0.502, 0.665, 0.998),
            "blind-material-source-v2.png": (0.669, 0.502, 0.998, 0.998),
        },
        "config": {
            "archetype_id": "eco_urban_bioclimatic_block",
            "variant_id": "eco_bioclimatic_passive",
            "skin_schema": "passive-house-timber-block-skin@2",
            "elevation_source": "front-elevation-source-v1.png",
            "occupied_depth_source": "occupied-day-depth-source-v2.png",
            "bands": {
                "facade": (0.04, 0.12, 0.96, 0.91),
                "podium": (0.04, 0.67, 0.96, 0.91),
                "floor_a": (0.07, 0.48, 0.93, 0.70),
                "floor_b": (0.07, 0.27, 0.93, 0.49),
                "crown": (0.03, 0.06, 0.97, 0.30),
                "side": (0.04, 0.22, 0.28, 0.88),
            },
            "prefixes": {
                "facade": "passive_registered_front",
                "podium": "passive_recessed_entry_and_ground_bays",
                "floor_a": "passive_complete_window_bay_a",
                "floor_b": "passive_complete_window_bay_b",
                "crown": "passive_dual_roof_pv_and_sedum",
                "side": "wrapped_larch_gable_and_rear_elevation",
                "interior": "occupied_passive_house_room_depth_day",
                "interior_evening": "occupied_passive_house_room_depth_evening",
                "larch": "naturally_weathering_vertical_larch",
                "frame": "dark_timber_aluminum_frame_and_reveal",
                "vision_glass": "neutral_passive_triple_glazing",
                "blind": "black_external_venetian_blind",
                "pv": "dark_blue_passive_photovoltaic_glass",
                "green_roof": "dense_passive_sedum_roof",
                "zinc": "zinc_gutter_and_roof_edge",
            },
            "support": {
                "interior_evening": ((151, 118, 82), "interior", 13491),
                "larch": ((183, 132, 79), "wood", 13501),
                "frame": ((46, 43, 38), "wood", 13511),
                "vision_glass": ((124, 134, 132), "glass", 13521),
                "blind": ((31, 32, 32), "metal", 13531),
                "pv": ((39, 52, 75), "glass", 13541),
                "green_roof": ((87, 91, 52), "foliage", 13551),
                "zinc": ((105, 109, 107), "metal", 13561),
            },
            "support_sources": {
                "larch": "larch-material-source-v1.png",
                "interior_evening": "occupied-evening-depth-source-v2.png",
                "frame": "frame-material-source-v2.png",
                "vision_glass": "vision-glass-material-source-v2.png",
                "blind": "blind-material-source-v2.png",
                "pv": "pv-module-material-source-v2.png",
                "green_roof": "green-roof-material-source-v1.png",
            },
            "registered_surfaces": [
                "four_level_six_bay_vertical_larch_envelope",
                "deep_real_triple_glazed_window_reveals_with_separate_room_depth",
                "mixed_clear_panes_insulated_panels_and_external_blinds",
                "deeply_recessed_central_timber_entrance",
                "asymmetric_dual_pitch_roof_with_individually_framed_pv_modules_and_sedum_fields",
                "rooflights_zinc_gutters_and_downpipes",
                "gable_end_punched_windows_and_vertical_facade_pv_bank",
            ],
            "registration": "The four-view board locks one four-level six-bay passive timber block with deep triple glazing, a recessed central entry, external blinds and one asymmetric PV-and-sedum roof.",
            "opening_method": "Every opening recesses its independent timber-aluminum frame and split triple panes behind physical larch jamb, head and sill returns; alternating daylight/evening room depth sits farther inside and optional real blind blades remain within the reveal cavity.",
            "generic_tiling_allowed": False,
        },
        "design_lock": {
            "native_building_dimensions_m": [36.0, 20.0, 17.0],
            "native_envelope_dimensions_m": [37.2, 21.0, 18.2],
            "occupied_storeys": 4,
            "primary_material": "naturally weathering vertical larch rainscreen",
            "window_rule": "six bays of deep triple glazing with dark insulated reveals, mixed panels and selected real external blinds",
            "front_identity": "six tall larch bays, deeply recessed central entry and environmental roof visible from the street",
            "roof_rule": "asymmetric pitched roof with continuous south PV field, north sedum strip, three rooflights, zinc gutters and facade PV bank",
        },
        "prompts": {"goalpost": PASSIVE_GOALPOST_PROMPT, "material": PASSIVE_MATERIAL_PROMPT, "refinement": PASSIVE_OPTICAL_PV_REFINEMENT_PROMPT},
        "source_ids": {"goalpost": "exec-e8bc5a22-fc2b-4100-b35c-cdf135d0c9db", "material": "exec-94feb115-c27e-41f8-b093-54d931a82ef3", "refinement": "exec-82c8e43d-5ede-41a4-b31c-7209b81e60b7"},
        "input_paths": ["/archetypes/buildings/eco_urban_bioclimatic_block/variant_0.png"],
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
    refinement_id = spec["source_ids"].get("refinement")
    refinement_source = spec.get("refinement_source")
    refinement_cells = spec.get("refinement_cells", {})
    refinement_sources = []
    if refinement_id and refinement_source:
        refinement_sources = [
            {
                "file": refinement_source,
                "source_id": refinement_id,
                "role": "reviewed_optical_and_construction_refinement_plate",
                "prompt": spec["prompts"]["refinement"],
            },
            *(
                {
                    "file": filename,
                    "source_id": f"{refinement_id}:{Path(filename).stem}",
                    "role": f"registered_refinement_crop:{Path(filename).stem}",
                }
                for filename in refinement_cells
            ),
        ]
    payload = {
        "schema": "reference-generation@1",
        "family": family,
        "archetype_id": spec["archetype_id"],
        "variant_id": spec["variant_id"],
        "provider": "OpenAI built-in image generation",
        "model": "gpt-image-2",
        "generated_at": date.today().isoformat(),
        "status": "source-pack-refined" if refinement_sources else "source-pack-complete",
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
            *refinement_sources,
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
        if spec.get("refinement_source"):
            crop_cells(
                source_root,
                spec["refinement_source"],
                spec["refinement_cells"],
            )
        write_provenance(family, spec)
        prepare_family(family, spec["config"], batch_label="wave13")
        bind_atlas(family)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
