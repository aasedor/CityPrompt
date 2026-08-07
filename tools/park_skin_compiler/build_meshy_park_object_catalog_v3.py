"""Build four reviewed, finite Meshy park-object batch declarations.

The source plan deliberately assigns one detail-rich object to each selected
archetype variant. Geometry that needs regulation dimensions or is better made
procedurally is excluded. This script writes declarations only and performs no
paid API calls.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "frontend/public/data/openSpaceArchetypes.json"
if not CATALOG.is_file():
    CATALOG = ROOT / "frontend/src/data/openSpaceArchetypes.json"

MATERIALS = {
    "iron": "layered charcoal wrought iron, subtle edge wear, restrained brown oxidation, realistic outdoor matte PBR",
    "timber": "weathered exterior hardwood with varied warm-gray grain, darker joints, end-grain detail, subtle checking and matte PBR",
    "cedar": "silvered cedar with warm exposed grain, darkened fasteners and joints, mild damp staining and matte outdoor PBR",
    "corten": "layered orange, russet and dark-brown Corten patina with rain streaks, darker folds and satin-matte PBR",
    "stone": "weathered pale limestone with warm buff variation, chipped edges, darker pores, restrained lichen and rough matte PBR",
    "granite": "coarse mottled gray granite with charcoal mineral flecks, tan weathering, dark creases and rough matte PBR",
    "concrete": "board-formed light-gray concrete with pores, fine aggregate, formwork lines, edge wear and matte PBR",
    "bronze": "aged cast bronze with green-blue verdigris, warm brown polished high points, dark oxidation and satin-matte PBR",
    "galvanized": "weathered galvanized steel with zinc mottling, dark hardware, mild water streaks and realistic non-glossy PBR",
    "terracotta": "hand-fired terracotta with layered ochre, warm red and pale mineral bloom, chipped edges and porous matte PBR",
    "driftwood": "salt-bleached driftwood with silver-gray grain, pale fibers, charcoal checks, rounded worn edges and rough matte PBR",
    "basalt": "dark volcanic basalt with charcoal and brown mineral variation, vesicular pores, wet-dark creases and rough matte PBR",
    "mosaic": "hand-set ceramic mosaic with varied colored tesserae, pale grout, weathered edges and realistic ceramic roughness",
    "rope": "marine-grade tan rope with twisted fibers, salt weathering, dark lashings and non-glossy PBR",
    "painted_steel": "powder-coated exterior steel with restrained chips, dark exposed edges, galvanized hardware and satin PBR",
    "shell": "irregular pale oyster shell and mineral-cement surfaces with layered gray, cream and green staining, rough porous PBR",
}


def o(
    slug: str,
    role: str,
    dimensions: list[float],
    geometry: str,
    material: str,
    orientation: str = "preserve-upright",
    repeat: bool = False,
) -> dict[str, Any]:
    return {
        "slug": slug,
        "role": role,
        "dimensions": dimensions,
        "geometry": geometry,
        "material": material,
        "orientation": orientation,
        "repeat": repeat,
    }


WAVES: dict[str, dict[str, list[dict[str, Any]]]] = {
    "v3a": {
        "urban_pocket_park": [
            o("ornamental-iron-loveseat", "pocket_park_ornamental_loveseat", [1.7, .72, .95], "ornamental two-person cast-iron garden bench with a fine botanical back pattern, timber seat slats, curved arms and stable feet", "iron"),
            o("concrete-timber-seat", "pocket_park_sculptural_seat", [2.4, .9, .75], "single contemporary seat combining one folded board-formed concrete shell with a warm timber sitting surface and concealed stable base", "concrete"),
            o("terracotta-planter-ensemble", "pocket_park_mediterranean_planter", [2.2, 1.4, 1.25], "one coherent ensemble of three interlocking oversized terracotta vessels at varied heights, empty and stable for procedural planting", "terracotta", repeat=True),
            o("basalt-water-bowl", "pocket_park_tropical_water_bowl", [1.7, 1.7, .72], "low hand-hewn volcanic-basalt water bowl with an irregular circular rim, shallow empty basin and discreet stable foot", "basalt"),
        ],
        "neighborhood_park": [
            o("romantic-stone-footbridge", "neighborhood_romantic_footbridge", [4.4, 1.6, 1.15], "small gently arched limestone footbridge with a shallow voussoir arch, simple parapets and worn pedestrian deck", "stone", "long-axis-x"),
            o("corten-planter-bench", "neighborhood_modern_planter_bench", [3.2, 1.1, .85], "integrated Corten planter and timber bench: one long rusted-steel planting trough with a cantilevered slatted seat and clean drainage feet", "corten", "long-axis-x", True),
            o("limestone-seat-wall", "neighborhood_mediterranean_seat_wall", [3.6, .75, .62], "single dry-stacked limestone seat-wall module with irregular coursing, a broad smooth cap and stable flat back", "stone", "long-axis-x", True),
            o("woven-palm-shade", "neighborhood_tropical_shade", [3.6, 3.2, 2.9], "small open-sided shade canopy on four timber posts with a gently pitched woven-palm roof and simple lashings; no walls or furniture", "cedar"),
        ],
        "community_park": [
            o("carved-stone-urn", "community_park_formal_urn", [1.1, 1.1, 1.65], "large classical carved-stone garden urn with restrained acanthus relief, thick rim, empty bowl and square pedestal foot", "stone", repeat=True),
            o("corten-path-light-cluster", "community_park_modern_path_lights", [2.4, .7, 1.05], "single coordinated cluster of three slim folded Corten path lights at staggered heights with concealed downward apertures and shared base", "corten", "long-axis-x", True),
            o("olive-oil-amphora", "community_park_mediterranean_amphora", [1.0, 1.0, 1.65], "oversized weathered Mediterranean amphora with two strong handles, rounded body, narrow neck and stable discreet base", "terracotta", repeat=True),
            o("thatched-shade-umbrella", "community_park_tropical_parasol", [3.4, 3.4, 3.0], "single robust public-park shade umbrella with a thick timber mast and layered natural thatch roof, no furniture or ground attached", "cedar", repeat=True),
        ],
        "regional_park": [
            o("carved-stone-drinking-fountain", "regional_park_stone_drinking_fountain", [1.1, .85, 1.25], "freestanding heritage stone drinking fountain with a shallow metal basin, restrained carved panel and sturdy pedestal, no readable text", "stone"),
            o("sculptural-concrete-lounger", "regional_park_modern_lounger", [2.25, .75, .78], "single flowing S-profile board-formed concrete park lounger with integrated seat and back, softened edges and stable ground contact", "concrete", "long-axis-x", True),
            o("limestone-picnic-hearth", "regional_park_mediterranean_hearth", [1.6, 1.2, 1.15], "permanent public picnic hearth built from irregular limestone with a recessed blackened firebox and simple steel grill plate", "stone", repeat=True),
            o("volcanic-rock-seat-cluster", "regional_park_tropical_rock_seating", [3.0, 2.0, 1.05], "one coherent cluster of four low naturally interlocked volcanic boulders with two subtly flattened sitting surfaces", "basalt", "long-axis-x", True),
        ],
        "botanical_garden": [
            o("formal-fluted-urn", "botanical_formal_urn", [1.2, 1.2, 1.75], "classical fluted stone urn with rolled handles, deep empty planting bowl, carved foot and square plinth", "stone", repeat=True),
            o("fern-grotto-rock-arch", "botanical_woodland_grotto", [3.5, 2.0, 2.3], "natural mossy stone grotto arch formed by irregular weathered boulders with one clear walk-through opening and stable footprint", "granite", "long-axis-x"),
            o("concrete-corten-art-plinth", "botanical_sculptural_plinth", [2.2, 1.2, 2.6], "one abstract botanical display plinth combining an offset polished-concrete slab, narrow Corten frame and recessed specimen niche; empty", "corten"),
            o("weathered-cottage-gate", "botanical_cottage_gate", [2.6, .65, 2.25], "freestanding weathered timber garden gate with two posts, curved top rail, fine diagonal lattice and believable iron latch, without fence runs", "timber", "long-axis-x"),
        ],
        "memorial_garden": [
            o("stone-sundial", "memorial_formal_sundial", [1.1, 1.1, 1.45], "restrained carved-stone memorial sundial with circular bronze dial plate on a tapered pedestal and broad stable base, no inscriptions", "stone"),
            o("woodland-remembrance-marker", "memorial_woodland_marker", [1.2, .55, 1.75], "single hand-carved woodland remembrance marker made from a weathered split oak slab held by two discreet dark steel feet, no readable text", "timber"),
            o("stainless-mourning-sculpture", "memorial_contemporary_sculpture", [2.1, 1.2, 3.0], "single abstract brushed-stainless memorial sculpture of two gently leaning folded planes forming a quiet central void and stable concealed base", "galvanized"),
            o("antique-remembrance-bench", "memorial_romantic_bench", [2.0, .8, 1.05], "ornate but restrained Victorian memorial bench with cast-iron botanical side frames, curved timber slats and a blank central medallion", "iron"),
        ],
        "community_garden": [
            o("timber-compost-bay", "community_garden_compost_bay", [3.0, 1.2, 1.25], "one three-bay outdoor compost station built from robust slatted timber, removable front boards and open empty compartments", "timber", "long-axis-x"),
            o("rain-barrel-rack", "community_garden_rain_barrel_rack", [2.5, .9, 1.7], "single galvanized frame holding two closed rain barrels with downpipe manifold, taps and stable feet; no building wall", "galvanized", "long-axis-x"),
            o("seed-library-cabinet", "community_garden_seed_library", [1.1, .55, 1.8], "freestanding weathered timber seed-library cabinet on two posts with many small blank drawers, a shallow cap and no readable labels", "cedar"),
            o("garden-wash-station", "community_garden_wash_station", [2.2, .8, 1.25], "robust outdoor produce-wash station with timber frame, galvanized double basin, drainboard, lower slatted shelf and integrated hose hook", "timber", "long-axis-x"),
        ],
        "community_garden_enhanced": [
            o("accessible-raised-planter", "enhanced_garden_accessible_planter", [3.0, 1.3, .9], "single wheelchair-accessible raised planter with weathered timber sides, recessed knee space, rounded cap and empty dark soil surface", "cedar", "long-axis-x", True),
            o("glazed-cold-frame", "enhanced_garden_cold_frame", [2.2, 1.2, 1.05], "low freestanding timber cold frame with two sloped glazed lids, visible hinge hardware and empty interior growing bed", "cedar", "long-axis-x", True),
            o("communal-harvest-table", "enhanced_garden_harvest_table", [2.8, 1.0, .9], "single heavy communal harvest worktable with thick weathered top, trestle frame, lower slatted shelf and integrated galvanized weighing tray", "timber", "long-axis-x"),
            o("woven-harvest-basket-rack", "enhanced_garden_basket_rack", [2.0, .65, 1.55], "one timber storage rack holding four empty woven harvest baskets in organized cubbies, all components joined as one stable object", "cedar", "long-axis-x"),
        ],
    },
    "v3b": {
        "urban_forest": [
            o("interpretive-trail-marker", "urban_forest_interpretive_marker", [1.2, .45, 1.55], "single low-impact timber trail marker with angled blank interpretive panel, split-log post and discreet metal foot", "cedar", repeat=True),
            o("rain-cistern-pipework", "urban_forest_rain_cistern", [2.0, 1.4, 2.2], "compact galvanized rain-harvesting cistern with ribbed cylindrical tank, inlet basket, overflow pipe, tap and stable plinth", "galvanized"),
            o("reclaimed-habitat-tower", "urban_forest_reclaimed_habitat_tower", [1.4, .8, 2.6], "tall habitat tower assembled from reclaimed brick, drilled hardwood, bark and hollow reeds inside a weathered steel frame", "timber"),
            o("oyster-reef-module", "urban_forest_coastal_oyster_reef", [2.8, 1.8, .9], "one irregular low living-shoreline reef module made from clustered oyster shells bound into porous ridges with many cavities", "shell", "long-axis-x", True),
        ],
        "riparian_buffer": [
            o("timber-overlook-rail", "riparian_overlook_rail_module", [3.5, .6, 1.2], "single rustic timber overlook railing module with three posts, two horizontal rails and a small integrated leaning shelf", "cedar", "long-axis-x", True),
            o("gabion-seat-module", "riparian_gabion_seat", [2.5, .8, .65], "single rectangular galvanized gabion basket filled with varied river stone and topped by a thick weathered timber seat", "galvanized", "long-axis-x", True),
            o("reclaimed-trail-bench", "riparian_reclaimed_bench", [2.2, .75, .9], "single trail bench built from one reclaimed heavy timber beam on two mismatched corten-steel supports, with naturally worn edges", "timber", "long-axis-x", True),
            o("coir-bank-fascine", "riparian_coir_bank_fascine", [4.0, 1.1, .65], "one coherent bank-stabilization fascine bundle of tightly bound natural coir rolls, willow stakes and short branch weave", "rope", "long-axis-x", True),
        ],
        "wetland_rain_garden": [
            o("wildlife-interpretive-sign", "wetland_interpretive_sign", [1.5, .5, 1.45], "angled wetland interpretive panel on two weathered timber posts with a blank illustrated face and robust outdoor frame", "cedar", repeat=True),
            o("stone-steel-check-weir", "wetland_check_weir", [3.6, 1.0, .8], "single low stream check-weir combining irregular stone abutments and one dark galvanized notch plate with believable water passage", "stone", "long-axis-x", True),
            o("pallet-insect-habitat", "wetland_reclaimed_insect_habitat", [2.1, 1.1, 1.7], "compact porous habitat pile assembled from reclaimed timber frames, bark slabs, drilled branches and clay tubes as one stable unit", "timber", "long-axis-x", True),
            o("oyster-shell-bag-cluster", "wetland_coastal_reef_bags", [3.0, 1.8, .7], "one low cluster of four interlocked biodegradable mesh bags densely filled with irregular oyster shells for living shoreline restoration", "shell", "long-axis-x", True),
        ],
        "pond_lake": [
            o("carved-lakeside-bench", "pond_lake_stone_bench", [2.3, .75, .9], "single carved limestone lakeside bench with a slightly curved seat, solid sculpted supports and weather-softened edges", "stone", "long-axis-x", True),
            o("timber-nesting-island", "pond_lake_nesting_island", [2.7, 2.0, .75], "one floating wildlife nesting island with a low timber perimeter, porous brush center, two sheltered cavities and concealed buoyancy", "cedar", repeat=True),
            o("fishing-rod-rest", "pond_lake_fishing_rod_rest", [2.2, .6, 1.15], "freestanding weathered timber fishing rod rest with notched upper rail, small tackle shelf and stable feet; no rods or people", "cedar", "long-axis-x", True),
            o("reed-habitat-bundle", "pond_lake_reed_habitat_bundle", [2.4, 1.4, 1.2], "one arranged aquatic habitat bundle of upright hollow reed tubes, short timber stakes and woven willow surround with no live plants", "timber", "long-axis-x", True),
        ],
        "stormwater_retention_pond": [
            o("stormwater-trash-rack", "retention_pond_trash_rack", [2.8, 1.0, 1.4], "single angled galvanized stormwater trash rack with closely spaced bars, side braces, base frame and realistic service access handle", "galvanized", "long-axis-x"),
            o("pond-overlook-screen", "retention_pond_overlook_screen", [3.5, .8, 1.8], "low open-air timber pond-observation screen with two viewing slots, leaning rail and short side wings, no roof or deck", "cedar", "long-axis-x"),
            o("gabion-overflow-weir", "retention_pond_gabion_weir", [4.0, 1.4, 1.0], "single broad gabion overflow weir filled with angular stone, central lowered spill notch and reinforced galvanized edges", "galvanized", "long-axis-x"),
            o("rock-armored-spillway", "retention_pond_rock_spillway", [4.2, 2.2, 1.2], "one coherent dry spillway cluster of interlocked angular boulders forming a shallow central chute and stable stepped edges", "granite", "long-axis-x"),
        ],
        "linear_park_greenway": [
            o("railroad-tie-bench", "linear_park_rail_tie_bench", [2.6, .75, .8], "single bench built from two deeply weathered reclaimed railway ties on dark steel sled supports, preserving bolt holes and end grain", "timber", "long-axis-x", True),
            o("kayak-storage-rack", "linear_park_kayak_rack", [3.0, 1.2, 1.8], "freestanding timber-and-galvanized rack with three empty curved kayak cradles, tie-down loops and stable feet", "cedar", "long-axis-x"),
            o("natural-riffle-weir", "linear_park_riffle_weir", [4.0, 1.8, .8], "one low natural stone riffle-weir cluster with irregular river boulders forming a shallow V-shaped central flow notch", "granite", "long-axis-x", True),
            o("railway-switch-sculpture", "linear_park_rail_switch_sculpture", [3.4, 1.5, 1.0], "single preserved heritage railway switch assembly with short rail fragments, switch stand and rusted mechanical linkage on discrete sleepers", "corten", "long-axis-x"),
        ],
        "nature_preserve": [
            o("observation-scope-pedestal", "nature_preserve_observation_scope", [1.0, .75, 1.55], "single weatherproof wildlife observation scope on a sturdy adjustable pedestal with angled binocular housing and stable base", "painted_steel", repeat=True),
            o("prairie-nesting-tower", "nature_preserve_nesting_tower", [1.3, 1.3, 3.8], "freestanding prairie wildlife nesting tower with weathered timber mast, stacked sheltered nesting boxes and simple predator guard", "cedar"),
            o("dune-sand-fence", "nature_preserve_dune_fence", [4.0, .45, 1.2], "single flexible dune sand-fence module of irregular vertical timber slats joined by two dark wire strands and braced end stakes", "driftwood", "long-axis-x", True),
            o("mossy-nurse-log", "nature_preserve_nurse_log", [4.5, 1.2, 1.05], "single horizontal old-growth nurse log with deeply cracked bark, broken hollow end, stable underside and restrained moss mats", "driftwood", "long-axis-x", True),
        ],
        "constructed_wetland_eco_park": [
            o("pond-dipping-platform", "constructed_wetland_dipping_platform", [3.2, 2.4, 1.15], "compact freestanding timber pond-dipping deck with low edge rail, one open access side and visible subframe; no boardwalk attached", "cedar"),
            o("sluice-control-gate", "constructed_wetland_sluice_gate", [3.2, 1.1, 2.0], "single small water-control sluice with galvanized frame, central adjustable gate plate, hand wheel, braces and short concrete sill", "galvanized", "long-axis-x"),
            o("wildlife-nesting-raft", "constructed_wetland_nesting_raft", [3.0, 2.2, .7], "one floating wildlife nesting raft with low timber frame, brush-and-gravel center, two sheltered nesting cavities and concealed floats", "cedar", repeat=True),
            o("tactile-interpretive-table", "constructed_wetland_tactile_table", [1.8, 1.0, 1.05], "accessible outdoor tactile interpretation table with angled bronze relief surface, two robust stone supports and no readable text", "bronze"),
        ],
    },
    "v3c": {
        "promenade_boardwalk": [
            o("maritime-bollard-rope", "promenade_maritime_bollard_rope", [2.8, .7, 1.05], "single coordinated module of two weathered timber mooring bollards joined by a relaxed heavy nautical rope, with stable feet", "rope", "long-axis-x", True),
            o("cantilevered-steel-lounger", "promenade_modern_lounger", [2.2, .75, .85], "single contemporary cantilevered waterfront lounger made from a folded powder-coated steel ribbon with perforated sitting surface", "painted_steel", "long-axis-x", True),
            o("thatched-cabana-daybed", "promenade_tropical_cabana", [3.2, 2.4, 2.7], "one compact open-sided timber cabana with layered thatch roof, raised slatted daybed platform and four sturdy posts; no loose cushions", "cedar"),
            o("timber-fishing-rod-rack", "promenade_riparian_rod_rack", [2.6, .7, 1.2], "single boardwalk fishing rack with weathered timber frame, six rounded rod notches, small bait shelf and stable feet; no rods", "cedar", "long-axis-x", True),
        ],
        "riverfront_park_beach": [
            o("parasol-deckchair-ensemble", "riverfront_urban_beach_ensemble", [2.8, 2.6, 2.5], "one coordinated beach ensemble containing a folded-fabric striped parasol and one empty timber sling chair on a shared discreet base", "timber"),
            o("cedar-kayak-rack", "riverfront_swimming_beach_kayak_rack", [3.4, 1.4, 1.8], "freestanding cedar rack with four empty curved kayak cradles, galvanized straps and a stable weatherproof frame", "cedar", "long-axis-x"),
            o("cargo-net-climbing-frame", "riverfront_adventure_pier_climber", [3.6, 3.0, 3.0], "single compact adventure-pier climbing frame with four heavy timber posts and a taut pyramidal marine-rope cargo net, no slide or platform", "rope"),
            o("willow-fascine-revetment", "riverfront_naturalized_fascine", [4.2, 1.4, .85], "one coherent bioengineered bank-revetment bundle of woven willow branches, coir rolls, timber stakes and visible porous gaps", "rope", "long-axis-x", True),
        ],
        "urban_beach": [
            o("sculptural-sun-lounger", "urban_beach_sun_lounger", [2.1, .8, .72], "single flowing public beach lounger with perforated powder-coated steel shell, raised head curve and broad stable sled base", "painted_steel", "long-axis-x", True),
            o("shade-sail-canopy", "urban_beach_shade_sail", [4.2, 3.4, 3.1], "one compact three-mast tensile shade canopy with taut triangular fabric, dark steel masts and realistic cable connections; no furniture", "painted_steel"),
            o("beach-shower-column", "urban_beach_shower", [1.0, .8, 2.4], "single robust public beach shower column with two stainless shower heads, push controls, foot rinse and discreet grated base", "galvanized"),
            o("driftwood-windbreak", "urban_beach_driftwood_windbreak", [3.5, .7, 1.6], "one low sculptural windbreak screen assembled from varied vertical salt-bleached driftwood pieces in a stable concealed frame", "driftwood", "long-axis-x", True),
        ],
        "tidal_marsh_boardwalk": [
            o("hexagonal-overlook-rail", "tidal_marsh_overlook_rail", [3.2, 1.2, 1.15], "single three-sided segment of a hexagonal timber overlook rail with sturdy posts, top leaning shelf and open back", "cedar", "long-axis-x"),
            o("mangrove-bird-hide", "tidal_marsh_mangrove_hide", [3.6, 1.3, 2.2], "compact open-air mangrove bird hide with woven timber screen, three viewing slots, short side returns and raised post feet; no roof", "cedar", "long-axis-x"),
            o("timber-birdwatch-tower", "tidal_marsh_birdwatch_tower", [2.8, 2.8, 5.2], "small open timber observation tower with cross-braced legs, upper viewing deck, slatted guardrail and integrated straight stair", "cedar"),
            o("low-wetland-viewing-hide", "tidal_marsh_viewing_hide", [3.8, 1.5, 1.7], "single low faceted timber viewing hide with four narrow slots at varied heights, leaning rail and stable wetland feet", "cedar", "long-axis-x", True),
        ],
        "rooftop_garden": [
            o("corten-planter-bench", "rooftop_corten_planter_bench", [3.2, 1.1, .85], "integrated rooftop Corten planter with a cantilevered timber bench, concealed drainage tray and broad wind-stable base", "corten", "long-axis-x", True),
            o("sculptural-shade-pergola", "rooftop_sculptural_pergola", [3.8, 3.0, 2.8], "single compact rooftop pergola with four dark steel posts and a folded perforated-metal shade canopy shaped as two overlapping planes", "painted_steel"),
            o("rainwater-tank", "rooftop_rainwater_tank", [1.8, 1.3, 2.0], "compact rooftop rainwater harvesting tank with ribbed galvanized body, inlet basket, overflow, gauge, tap and stable wind frame", "galvanized"),
            o("beehive-stand", "rooftop_beehive_stand", [2.2, .9, 1.55], "one secure rooftop apiary stand holding three closed timber beehive boxes under a shallow weather cap, with all pieces joined", "cedar", "long-axis-x"),
        ],
        "street_plaza_parklet": [
            o("bench-planter-module", "parklet_bench_planter", [3.4, 1.2, .9], "single curbside parklet module combining a long timber bench, raised steel planter and protective end panel on one stable platform", "timber", "long-axis-x", True),
            o("bike-corral-planter", "parklet_bike_corral_planter", [3.2, 1.0, .9], "one coordinated steel bicycle-corral module with three sculptural inverted-U racks integrated into a long planted end trough; empty", "painted_steel", "long-axis-x", True),
            o("compact-cafe-counter", "parklet_cafe_counter", [2.4, .8, 1.15], "single weatherproof parklet café counter with timber serving top, folded-steel body, two integrated standing ledges and no loose stools", "painted_steel", "long-axis-x"),
            o("curbside-stage-platform", "parklet_stage_platform", [3.6, 2.2, .65], "single low modular curbside performance platform with timber deck, faceted dark-steel skirt, one integrated step and rounded street-safe corners", "timber", "long-axis-x"),
        ],
        "beer_garden": [
            o("communal-trestle-set", "beer_garden_communal_table", [2.8, 1.8, .85], "one joined beer-garden furniture set with a heavy timber trestle table and two matching integrated benches, structurally straight and empty", "timber", "long-axis-x", True),
            o("string-light-mast", "beer_garden_light_mast", [1.3, 1.3, 3.8], "single freestanding timber string-light mast with four radial dark cables, small warm bulb housings and weighted steel foot; no surrounding lights", "cedar", repeat=True),
            o("barrel-standing-table", "beer_garden_barrel_table", [1.0, 1.0, 1.15], "single repurposed oak beer barrel standing table with circular timber top, dark iron hoops and stable concealed feet", "timber", repeat=True),
            o("sculptural-fire-bowl", "beer_garden_fire_bowl", [1.6, 1.6, .72], "large low Corten fire bowl with hand-formed irregular rim, dark interior, three discreet feet and no flames or fuel", "corten"),
        ],
        "amphitheater_lawn": [
            o("portable-acoustic-shell", "amphitheater_portable_shell", [4.2, 2.4, 3.2], "single compact open-front timber acoustic shell with layered curved ribs, faceted back panels and stable weighted base; no stage deck", "cedar"),
            o("carved-stone-seat-block", "amphitheater_stone_seat", [2.6, .85, .7], "single long carved-granite amphitheater seat block with gently concave top, chiseled sides and broad stable underside", "granite", "long-axis-x", True),
            o("timber-sound-reflector", "amphitheater_sound_reflector", [3.0, 1.2, 2.7], "freestanding timber acoustic reflector panel with shallow concave face, visible laminated ribs, dark steel feet and no signage", "cedar", "long-axis-x", True),
            o("stage-lantern-tower", "amphitheater_lantern_tower", [1.2, 1.2, 3.5], "single sculptural outdoor lantern tower with weathered steel lattice, protected warm light chambers and stable square base", "corten", repeat=True),
        ],
    },
    "v3d": {
        "dog_park": [
            o("rustic-agility-ramp", "dog_park_rustic_agility_ramp", [3.4, 1.0, 1.45], "single A-frame dog agility ramp built from weathered timber planks with anti-slip cleats, sturdy braces and safe rounded edges", "cedar", "long-axis-x"),
            o("curved-concrete-tunnel", "dog_park_concrete_tunnel", [2.8, 1.5, 1.4], "single low curved board-formed concrete dog tunnel with clear walk-through opening, softened rim and broad stable ground contact", "concrete", "long-axis-x"),
            o("dog-drinking-fountain", "dog_park_drinking_fountain", [1.0, .8, 1.15], "freestanding dual-height dog drinking fountain with stainless upper bowl, low pet basin, push controls and dark steel pedestal", "galvanized"),
            o("urban-dog-wash", "dog_park_wash_station", [1.8, 1.0, 1.55], "compact outdoor dog-wash station with galvanized splash panel, low basin, flexible hose hook, leash ring and grated stable base", "galvanized"),
        ],
        "playground_adventure": [
            o("rope-climbing-pyramid", "adventure_play_rope_pyramid", [4.0, 4.0, 3.8], "single compact rope-climbing pyramid with central timber mast, taut radial rope web, dark connectors and stable perimeter anchors", "rope"),
            o("timber-adventure-tower", "adventure_play_timber_tower", [3.2, 2.8, 4.0], "single open timber adventure tower with cross-braced posts, small roofless platform, rope ladder and climbing net; no slide", "cedar"),
            o("concrete-play-tunnel-mound", "adventure_play_concrete_mound", [4.0, 2.6, 1.8], "single sculptural low concrete play mound with one broad crawl-through tunnel, two climbable ridges and child-safe rounded edges", "concrete", "long-axis-x"),
            o("carved-timber-play-animal", "adventure_play_carved_animal", [2.8, 1.2, 1.45], "single abstract child-safe carved hardwood woodland animal play sculpture with broad climbable back, integrated handholds and stable base", "timber", "long-axis-x"),
        ],
        "splash_pad_area": [
            o("stainless-water-arch", "splash_pad_water_arch", [2.8, .8, 2.6], "single stainless splash-pad arch with thick curved tube, six small downward nozzles, two reinforced feet and no running water", "galvanized", "long-axis-x"),
            o("stone-splash-bowl", "splash_pad_stone_bowl", [1.8, 1.8, .8], "low hand-carved stone splash bowl with irregular circular rim, shallow empty basin and broad non-slip pedestal", "granite"),
            o("bronze-animal-sprayer", "splash_pad_animal_sprayer", [1.5, .8, 1.2], "single stylized bronze river-fish water sprayer sculpture with simple child-safe form, open mouth nozzle and stable plinth", "bronze", "long-axis-x"),
            o("water-curtain-frame", "splash_pad_water_curtain", [3.2, .8, 2.7], "single sculptural Corten water-curtain frame with two folded uprights, curved top manifold and a row of fine downward nozzles; dry", "corten", "long-axis-x"),
        ],
        "fountain_water_feature": [
            o("bronze-lotus-bowl", "fountain_bronze_lotus_bowl", [2.0, 2.0, 1.0], "single cast-bronze fountain bowl shaped as restrained overlapping lotus petals with empty basin and stable circular foot", "bronze"),
            o("carved-wall-spout", "fountain_carved_wall_spout", [1.4, .8, 1.8], "freestanding carved-stone fountain wall panel with one bronze spout, shallow catch basin and stable concealed back support; dry", "stone"),
            o("stainless-water-hoop", "fountain_stainless_water_hoop", [2.6, .7, 2.6], "single thick stainless-steel circular water hoop with fine inward nozzles and two discreet base plates; no running water", "galvanized"),
            o("corten-cascade-vessels", "fountain_corten_cascade", [2.2, 1.5, 2.0], "one coherent stack of three offset folded-Corten cascade vessels at descending heights with empty basins and stable shared base", "corten"),
        ],
        "parisian_jardin": [
            o("versailles-stone-urn", "parisian_jardin_stone_urn", [1.25, 1.25, 1.8], "grand French formal garden urn with restrained garland relief, deep empty bowl, carved foot and square limestone pedestal", "stone", repeat=True),
            o("wrought-iron-chair-pair", "parisian_jardin_chair_pair", [1.8, .8, .95], "one coordinated pair of empty classic Parisian wrought-iron garden chairs joined by a discreet small circular side table", "iron", "long-axis-x", True),
            o("classical-stone-sundial", "parisian_jardin_sundial", [1.2, 1.2, 1.55], "classical French limestone sundial with bronze dial plate, fluted tapered pedestal and broad square plinth", "stone"),
            o("ornate-iron-fountain", "parisian_jardin_iron_fountain", [1.8, 1.8, 2.2], "ornate but compact cast-iron garden fountain with circular basin, central fluted column and two tiered bowls; dry", "iron"),
        ],
        "amsterdam_hofje_garden": [
            o("sandstone-water-pump", "hofje_sandstone_water_pump", [1.1, .85, 1.55], "traditional Dutch courtyard water pump with carved sandstone pedestal, dark iron hand pump and shallow catch basin", "stone"),
            o("timber-storage-bench", "hofje_storage_bench", [2.0, .75, 1.0], "single traditional oak courtyard bench with hinged storage-box seat, paneled back and simple dark iron strap hinges", "timber", "long-axis-x", True),
            o("communal-well-cover", "hofje_communal_well_cover", [1.8, 1.8, 1.5], "single octagonal communal well cover with low brick-and-stone curb, oak roof frame, small pulley wheel and no bucket", "timber"),
            o("wrought-iron-courtyard-gate", "hofje_courtyard_gate", [2.6, .5, 2.4], "freestanding traditional Dutch wrought-iron courtyard gate with simple arched top, fine vertical bars, scroll details and two masonry-free posts", "iron", "long-axis-x"),
        ],
        "newyork_community_garden": [
            o("compost-sifter-station", "nyc_garden_compost_sifter", [2.2, 1.0, 1.5], "single reclaimed-timber compost sifter station with angled galvanized mesh screen, collection tray and sturdy open frame", "timber", "long-axis-x"),
            o("mosaic-garden-bench", "nyc_garden_mosaic_bench", [2.2, .8, 1.0], "single community-made curved garden bench with concrete body and richly varied ceramic mosaic seat and back", "mosaic", "long-axis-x", True),
            o("painted-rain-barrel", "nyc_garden_rain_barrel", [1.0, 1.0, 1.35], "single cylindrical steel rain barrel with hand-painted botanical mural, fitted lid, brass tap and stable low stand; no readable text", "painted_steel", repeat=True),
            o("salvaged-steel-garden-arch", "nyc_garden_salvaged_arch", [2.8, .8, 2.6], "single walk-through garden arch assembled from bent salvaged steel strips and small welded leaf motifs, with stable feet and no plants", "painted_steel", "long-axis-x"),
        ],
        "halifax_public_gardens": [
            o("victorian-cast-iron-urn", "halifax_gardens_victorian_urn", [1.2, 1.2, 1.7], "ornate Victorian cast-iron garden urn with fluted bowl, restrained floral relief, curled handles and stable pedestal", "iron", repeat=True),
            o("victorian-park-bench", "halifax_gardens_victorian_bench", [2.0, .8, 1.05], "single ornate Victorian public-garden bench with cast-iron scroll side frames and warm weathered timber slats", "iron", "long-axis-x", True),
            o("sandstone-drinking-fountain", "halifax_gardens_drinking_fountain", [1.0, .8, 1.35], "heritage sandstone drinking fountain with carved Gothic panel, shallow bronze basin, simple tap and broad pedestal", "stone"),
            o("timber-duck-house", "halifax_gardens_duck_house", [1.5, 1.2, 1.55], "small freestanding decorative timber duck house with pitched cedar-shingle roof, arched opening, raised legs and no birds", "cedar", repeat=True),
        ],
    },
}


POSITIONS = [(.24, .28, 18), (.72, .28, -12), (.28, .72, 28), (.72, .72, -24)]


def main() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    archetypes = {item["id"]: item for item in catalog["archetypes"]}
    all_ids: set[str] = set()
    for wave, families in WAVES.items():
        objects: list[dict[str, Any]] = []
        for archetype_id, plans in families.items():
            archetype = archetypes[archetype_id]
            variants = archetype["variants"]
            if len(plans) != 4 or len(variants) < 4:
                raise ValueError(f"{archetype_id}: expected four plans and variants")
            family_slug = Path(archetype["thumbnailUrl"]).parent.name
            for index, plan in enumerate(plans):
                variant = variants[index]
                asset_id = f"{archetype_id.replace('_', '-')}-{plan['slug']}-v1"
                if asset_id in all_ids:
                    raise ValueError(f"duplicate asset id: {asset_id}")
                all_ids.add(asset_id)
                reference = ROOT / "frontend/public" / variant["thumbnailUrl"].lstrip("/")
                if not reference.is_file():
                    raise FileNotFoundError(reference)
                u, v, yaw = POSITIONS[index]
                objects.append({
                    "assetId": asset_id,
                    "family": family_slug,
                    "archetypeId": archetype_id,
                    "variantIds": [variant["id"]],
                    "references": [str(reference.relative_to(ROOT)).replace("\\", "/")],
                    "dimensionsM": plan["dimensions"],
                    "orientation": plan["orientation"],
                    "placementRole": plan["role"],
                    "placement": {
                        "u": u,
                        "v": v,
                        "yawDeg": yaw,
                        "repeatOnOversize": plan["repeat"],
                    },
                    "multiviewPrompt": (
                        f"Create three mutually consistent orthographic product views of exactly one {plan['geometry']}. "
                        f"Derive its design language, proportions and visible construction from the {archetype['title']} — "
                        f"{variant['label']} reference image. It must be one coherent freestanding, game-ready park object with "
                        "believable construction and a stable ground-contact side. Isolate the same exact object on a neutral "
                        "light-gray studio background in front three-quarter, rear three-quarter and side views, fully visible "
                        "and not cropped. No people, human figures, buildings, terrain, landscape, ground plane, live planting, "
                        "vehicles, text, signs, loose tools, surrounding furniture, water effects or extra objects."
                    ),
                    "texturePrompt": (
                        f"Photoreal archetype-derived material finish: {MATERIALS[plan['material']]}. Preserve construction joints, "
                        "contact wear and material variation. No people, ground, live plants, scenery, text, labels or extra props."
                    ),
                })
        batch = {
            "batchId": f"meshy-park-object-catalog-{wave}",
            "version": "2026-08-07",
            "creditCeiling": 1248,
            "estimatedCreditsPerAsset": 39,
            "objects": objects,
        }
        output = Path(__file__).with_name(f"meshy_park_object_batch_{wave}.json")
        output.write_text(json.dumps(batch, indent=2) + "\n", encoding="utf-8")
        print(f"{output}: {len(objects)} objects, {len(objects) * 39} estimated credits")
    print(f"total: {len(all_ids)} objects, {len(all_ids) * 39} estimated credits")


if __name__ == "__main__":
    main()
