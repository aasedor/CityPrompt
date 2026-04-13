#!/usr/bin/env node
/**
 * Regenerates SHADE_MAP colors with enforced minimum RGB Euclidean distance.
 *
 * Usage: node scripts/regenerateShadeMap.mjs
 *
 * Outputs the new SHADE_MAP entries to stdout. Pipe to a file or copy-paste.
 */

// ── Config ──────────────────────────────────────────────────────────────────
const MIN_RGB_DISTANCE = 15; // Minimum Euclidean RGB distance — muted tones + per-zone rendering

// ── HSL-to-RGB ──────────────────────────────────────────────────────────────
function hslToRgb(h, s, l) {
  // h in [0,360], s in [0,1], l in [0,1]
  const c = (1 - Math.abs(2 * l - 1)) * s;
  const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
  const m = l - c / 2;
  let r, g, b;
  if (h < 60) { r = c; g = x; b = 0; }
  else if (h < 120) { r = x; g = c; b = 0; }
  else if (h < 180) { r = 0; g = c; b = x; }
  else if (h < 240) { r = 0; g = x; b = c; }
  else if (h < 300) { r = x; g = 0; b = c; }
  else { r = c; g = 0; b = x; }
  return [
    Math.round((r + m) * 255),
    Math.round((g + m) * 255),
    Math.round((b + m) * 255),
  ];
}

function rgbToHex(r, g, b) {
  return '#' + [r, g, b].map(v => v.toString(16).padStart(2, '0')).join('');
}

function rgbDist(a, b) {
  return Math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2);
}

// ── Family definitions ──────────────────────────────────────────────────────
// Expanded ranges to fit more colors with spacing
const FAMILIES = {
  red: {
    // Muted warm tones: reds, oranges, browns, dusty pinks — NOT neon/vivid
    // Wide hue range but capped saturation to avoid color bleed in renders
    hRanges: [[0, 60], [300, 360]],
    sRange: [0.25, 0.65],
    lRange: [0.15, 0.55],
  },
  yellow: {
    hRanges: [[42, 70]],
    sRange: [0.30, 0.65],
    lRange: [0.25, 0.55],
  },
  gray: {
    // Tinted neutrals — warm grays, cool grays
    hRanges: [[0, 360]],
    sRange: [0.0, 0.15],
    lRange: [0.20, 0.78],
  },
  green: {
    hRanges: [[68, 178]],
    sRange: [0.20, 0.65],
    lRange: [0.15, 0.50],
  },
  teal: {
    hRanges: [[170, 210]],
    sRange: [0.20, 0.60],
    lRange: [0.25, 0.50],
  },
  blue: {
    hRanges: [[200, 255]],
    sRange: [0.25, 0.65],
    lRange: [0.20, 0.50],
  },
};

// ── Archetype assignments by family ─────────────────────────────────────────
const ARCHETYPES = {
  red: [
    'brownstone_rowhouse_frontage', 'historical_brick_main_street', 'victorian_heritage_avenue',
    'contemporary_midrise_residential', 'modern_glass_office_institutional', 'modernist_civic_block',
    'mid_century_modern_pavilion_block', 'civic_classical_building', 'monumental_courthouse_axis',
    'industrial_brick_mixed_use', 'adaptive_reuse_warehouse_lofts', 'nordic_timber_midrise',
    'mediterranean_arcade_mixed_use', 'parametric_future_hub', 'autonomous_tech_campus',
    'art_deco_setback_tower', 'deco_theater_mainstreet', 'traditional_vernacular_market_street',
    'parisian_midrise_block', 'parisian_boulevard_corner', 'alpine_mixed_use_lodge',
    'transit_oriented_station_block', 'transit_podium_residential', 'glass_tower_podium_modern',
    'skyline_glass_office_cluster', 'civic_monumental_institution', 'monumental_museum_axis',
    'japanese_machiya_mixed_use', 'eco_urban_bioclimatic_block', 'coastal_resort_terrace_block',
    'coastal_breezeway_mixed_use', 'custom_prompt_ready_archetype', 'custom_contextual_experiment',
    // Institutional
    'collegiate_gothic_education', 'neoclassical_institutional', 'brutalist_institutional', 'contemporary_civic',
    // Healthcare
    'art_deco_healthcare', 'functionalist_healthcare', 'biophilic_healthcare',
    // Industrial
    'daylight_factory', 'industrial_park_modernism', 'art_deco_industrial',
    'functionalist_brick_industrial', 'structural_expressionism_industrial', 'corrugated_vernacular_industrial',
    'machine_aesthetic_heavy_industrial', 'brutalist_utility_heavy_industrial', 'early_20c_megastructure_industrial',
    'romanesque_revival_warehouse', 'midcentury_distribution_warehouse', 'modern_bigbox_warehouse',
    // Hospitality
    'boutique_hotel_tower', 'chateauesque_hotel', 'resort_modernism_hotel', 'corporate_tower_hotel',
    // Transit
    'historic_grand_station', 'contemporary_transit_hub', 'urban_light_rail_stop',
    // Recreation
    'community_recreation_centre', 'modern_sports_arena', 'parkitecture_recreational',
    'civic_modernism_rec_centre', 'postmodern_rec_centre', 'contemporary_sustainable_rec_centre',
    'monumental_antiquity_arena', 'high_tech_arena', 'concrete_megastructure_arena',
    // Specialty
    'climbing_wall_building', 'waste_to_energy_plant', 'brewery_distillery',
    'solar_farm_agrivoltaics', 'immersive_experience_venue', 'modern_fire_station',
    // City-Specific Buildings
    'amsterdam_bell_gable_house', 'amsterdam_brown_cafe', 'amsterdam_canal_warehouse',
    'amsterdam_cornice_house', 'amsterdam_hofje', 'amsterdam_jordaan_house',
    'amsterdam_neck_gable_house', 'amsterdam_school_housing', 'amsterdam_spout_gable_house',
    'amsterdam_step_gable_house', 'barcelona_corner_chamfer', 'barcelona_mercat',
    'barcelona_modernist_workshop', 'barcelona_townhouse', 'calgary_cbe_brutalist_hq',
    'concert_hall_modern', 'ev_charging_hub', 'farnsworth_house_glass_pavilion',
    'food_hall_market_hall', 'hyperscale_data_center', 'mall_redevelopment',
    'shophouse_southeast_asian', 'terraced_stepped_building', 'vertical_farm', 'vertiport_evtol',
    // City-Specific batch 2
    'calgary_beltline_mid_rise', 'calgary_ctrain_station', 'calgary_inner_city_bungalow',
    'calgary_modern_infill_house', 'calgary_new_central_library', 'calgary_plus_15_connected_tower',
    'calgary_sandstone_heritage', 'ecole_republicaine', 'eixample_apartment_block',
    'gastown_heritage_commercial', 'georgian_terrace_house', 'grand_magasin',
    'halifax_ferry_terminal', 'halifax_georgian_colonial', 'halifax_maritime_commercial',
    'halifax_painted_clapboard_row', 'halifax_waterfront_warehouse', 'hotel_particulier',
    'hydrostone_neighbourhood_house', 'inglewood_heritage_brick_commercial', 'london_crescent_terrace',
    'london_mews_house', 'london_townhouse', 'marche_couvert', 'mile_end_cultural_triplex',
    'modernisme_casa', 'montreal_depanneur', 'montreal_duplex', 'montreal_plateau_triplex',
    'montreal_second_empire_civic', 'new_york_art_deco_tower', 'new_york_corner_bodega',
    'new_york_pre_war_apartment', 'new_york_walk_up_tenement', 'old_montreal_limestone_commercial',
    'old_montreal_warehouse_loft', 'parisian_cafe_brasserie', 'parisian_corner_with_dome',
    'passage_couvert', 'pre_haussmann_marais_building', 'regency_stucco_terrace',
    'skytrain_elevated_station', 'soho_cast_iron_loft_building', 'toronto_annex_mansion',
    'toronto_bay_and_gable_house', 'toronto_brick_rowhouse', 'toronto_condo_podium_tower',
    'toronto_edwardian_foursquare', 'toronto_junction_converted_industrial',
    'toronto_streetcar_platform_stop', 'vancouver_craftsman_bungalow', 'vancouver_laneway_house',
    'vancouver_special', 'vancouverism_tower_podium', 'victorian_bay_window_terrace',
    'west_end_mid_century_tower',
  ],
  yellow: [
    'classic_brownstone_streetwall', 'contemporary_townhouse_courtyard', 'detached_contemporary_infill',
    'courtyard_family_housing', 'scandinavian_urban_residential', 'mediterranean_villa_estate',
    'vernacular_courtyard_housing', 'minimalist_courtyard_block', 'minimalist_infill_townhouse',
    'mountain_alpine_chalet', 'japanese_contemporary_lanehouse', 'vertical_forest_residential',
    'senior_living_complex',
  ],
  gray: [
    'narrow_residential_street', 'suburban_residential_street', 'collector_road',
    'arterial_boulevard', 'highway_freeway', 'roundabout', 'cul_de_sac',
    'back_alley_service_lane', 'separated_bike_lane', 'multi_use_trail',
    'pedestrian_promenade', 'woonerf_shared_street', 'brt_corridor',
    'light_rail_avenue', 'main_street_complete', 'campus_pedestrian_spine',
    'scenic_parkway', 'riverfront_promenade', 'custom_streets_pathways',
    'downtown_thoroughfare', 'pedestrian_only_street', 'green_alley',
    'commercial_alley_laneway', 'yield_street', 'neighborhood_main_street',
    'elevated_rail_transit',
    // City-specific streets
    'amsterdam_gracht', 'amsterdam_steeg', 'amsterdam_straat',
    'barcelona_eixample_carrer', 'barcelona_passatge', 'barcelona_passeig',
    'haussmann_boulevard', 'parisian_passage', 'parisian_rue',
    'london_crescent_road', 'london_mews_lane', 'london_terrace_street',
    'new_york_brownstone_side_street', 'soho_cobblestone_street',
    'montreal_commercial_boulevard', 'montreal_plateau_residential_rue',
    'montreal_ruelle_verte', 'toronto_laneway', 'toronto_streetcar_street',
    'toronto_victorian_residential_street', 'vancouver_back_lane',
    'vancouver_cherry_blossom_street', 'bow_river_pathway', 'inglewood_main_street',
    'skytrain_elevated_corridor', 'stephen_avenue_pedestrian_mall',
    'halifax_steep_residential_street', 'halifax_waterfront_boardwalk',
    'brt_bus_rapid_transit_corridor', 'elevated_rail_transit_corridor',
    'light_rail_tram_avenue',
    // Bridges
    'urban_vehicular_bridge', 'landmark_signature_bridge', 'rail_transit_viaduct',
    'transit_priority_bridge', 'urban_pedestrian_footbridge',
    'landscape_park_pedestrian_bridge', 'dedicated_cycle_bridge',
    'shared_cycle_pedestrian_bridge',
  ],
  green: [
    'urban_pocket_park', 'neighborhood_park', 'community_park', 'regional_park',
    'dog_park', 'skate_park', 'sports_field_complex', 'tennis_court_cluster',
    'botanical_garden', 'japanese_garden', 'memorial_garden', 'urban_forest',
    'riparian_buffer', 'wetland_rain_garden', 'playground_adventure', 'splash_pad_area',
    'amphitheater_lawn', 'community_garden', 'cemetery_memorial_grounds',
    'linear_park_greenway', 'nature_preserve', 'rooftop_garden',
    'riverfront_park_beach', 'street_plaza_parklet',
    // Sports
    'basketball_court', 'pickleball_courts', 'soccer_pitch_caged', 'running_track_oval',
    'outdoor_fitness_circuit', 'baseball_softball_diamond', 'cricket_pitch_oval',
    'disc_golf_course', 'bocce_petanque_court', 'climbing_bouldering_wall',
    'pump_track', 'outdoor_ice_rink', 'beach_volleyball_courts', 'mini_golf_course',
    // Children & Nature
    'nature_play_area', 'inclusive_playground',
    // Ecological
    'pollinator_meadow', 'urban_orchard_food_forest', 'bioswale_rain_garden',
    // Cultural & Waterfront
    'urban_beach', 'sculpture_garden', 'labyrinth_meditation',
    'festival_event_lawn', 'kayak_launch_dock',
    // City-Specific Parks
    'amsterdam_hofje_garden', 'amsterdam_plein', 'amsterdam_vondelpark',
    'barcelona_pati_interior', 'barcelona_placa_xamfra', 'barcelona_superilla',
    'calgary_prairie_plaza', 'calgary_princes_island', 'community_garden_enhanced',
    'halifax_coastal_park', 'halifax_public_gardens', 'london_circus',
    'london_garden_square', 'montreal_mount_royal', 'montreal_square',
    'newyork_community_garden', 'newyork_pocket_park', 'parisian_jardin',
    'parisian_place', 'parisian_square', 'toronto_ravine', 'toronto_urban_square',
    'vancouver_beach_park', 'vancouver_seawall',
    // Custom
    'custom_parks_plazas',
  ],
  teal: [
    'formal_civic_plaza', 'market_square', 'courtyard_plaza',
    'promenade_boardwalk', 'transit_plaza', 'amphitheater_performance_space',
  ],
  blue: [
    'surface_parking_lot', 'structured_parking_garage', 'underground_parking_entry',
    'green_parking_lot', 'pond_lake', 'fountain_water_feature',
    'stormwater_retention_pond', 'swimming_pool_complex', 'canal_waterway',
  ],
};

// ── Generate candidate colors for a family ──────────────────────────────────
function generateCandidates(family, step = 2) {
  const { hRanges, sRange, lRange } = family;
  const candidates = [];
  const hStep = Math.max(1, step);
  const sStep = 0.02 * step;
  const lStep = 0.02 * step;

  for (const [hMin, hMax] of hRanges) {
    for (let h = hMin; h <= hMax; h += hStep) {
      for (let s = sRange[0]; s <= sRange[1]; s += sStep) {
        for (let l = lRange[0]; l <= lRange[1]; l += lStep) {
          const rgb = hslToRgb(h, s, l);
          candidates.push({ rgb, hex: rgbToHex(...rgb) });
        }
      }
    }
  }
  return candidates;
}

// ── Greedy max-min-distance assignment ───────────────────────────────────────
function assignColors(archetypeIds, familyDef, allAssigned) {
  // Generate dense candidate grid
  const candidates = generateCandidates(familyDef, 1);
  console.error(`  Candidates: ${candidates.length} for ${archetypeIds.length} archetypes`);

  const assigned = [];

  for (const id of archetypeIds) {
    let bestCandidate = null;
    let bestMinDist = -1;

    for (const cand of candidates) {
      // Check distance to ALL previously assigned colors (global)
      let minDist = Infinity;

      for (const prev of allAssigned) {
        const d = rgbDist(cand.rgb, prev);
        if (d < MIN_RGB_DISTANCE) { minDist = -1; break; }
        if (d < minDist) minDist = d;
      }
      for (const prev of assigned) {
        if (minDist < 0) break;
        const d = rgbDist(cand.rgb, prev.rgb);
        if (d < MIN_RGB_DISTANCE) { minDist = -1; break; }
        if (d < minDist) minDist = d;
      }

      if (minDist > bestMinDist) {
        bestMinDist = minDist;
        bestCandidate = cand;
      }
    }

    if (!bestCandidate || bestMinDist < MIN_RGB_DISTANCE) {
      console.error(`  WARNING: ${id} — best distance ${bestMinDist.toFixed(1)} < ${MIN_RGB_DISTANCE}`);
      // Still assign the best we found
      if (bestCandidate) {
        assigned.push({ id, ...bestCandidate });
        allAssigned.push(bestCandidate.rgb);
      }
    } else {
      assigned.push({ id, ...bestCandidate });
      allAssigned.push(bestCandidate.rgb);
    }
  }

  return assigned;
}

// ── Main ────────────────────────────────────────────────────────────────────
console.error('Regenerating SHADE_MAP with min RGB distance:', MIN_RGB_DISTANCE);
console.error('');

const allAssignedRgb = []; // Global tracking
const results = {};

for (const [familyName, archetypeIds] of Object.entries(ARCHETYPES)) {
  console.error(`Family: ${familyName} (${archetypeIds.length} archetypes)`);
  const familyDef = FAMILIES[familyName];
  const assigned = assignColors(archetypeIds, familyDef, allAssignedRgb);

  for (const { id, hex } of assigned) {
    results[id] = hex;
  }
  console.error(`  Assigned: ${assigned.length}`);
  console.error('');
}

// ── Validate ────────────────────────────────────────────────────────────────
console.error('Validating pairwise distances...');
const allHexes = Object.values(results);
const allRgbs = allHexes.map(hex => {
  const m = hex.match(/^#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i);
  return [parseInt(m[1], 16), parseInt(m[2], 16), parseInt(m[3], 16)];
});

let violations = 0;
let minFound = Infinity;
let minPair = [];
for (let i = 0; i < allRgbs.length; i++) {
  for (let j = i + 1; j < allRgbs.length; j++) {
    const d = rgbDist(allRgbs[i], allRgbs[j]);
    if (d < minFound) {
      minFound = d;
      minPair = [Object.keys(results)[i], Object.keys(results)[j]];
    }
    if (d < MIN_RGB_DISTANCE) {
      violations++;
      if (violations <= 10) {
        console.error(`  VIOLATION: ${Object.keys(results)[i]} <-> ${Object.keys(results)[j]} = ${d.toFixed(1)}`);
      }
    }
  }
}

console.error(`Total colors: ${allHexes.length}`);
console.error(`Min pairwise distance: ${minFound.toFixed(1)} (${minPair[0]} <-> ${minPair[1]})`);
console.error(`Violations (< ${MIN_RGB_DISTANCE}): ${violations}`);
console.error('');

// ── Output ──────────────────────────────────────────────────────────────────
// Output as TypeScript-ready format
let output = '';
let currentFamily = '';

for (const [familyName, archetypeIds] of Object.entries(ARCHETYPES)) {
  const familyLabels = {
    red: 'Red family: Buildings / Commercial / Institutional',
    yellow: 'Yellow family: Residential',
    gray: 'Gray family: Streets & Pathways',
    green: 'Green family: Parks & Green Space',
    teal: 'Teal family: Plazas & Hardscape',
    blue: 'Blue family: Water Features & Parking',
  };
  output += `  // ── ${familyLabels[familyName]} ──\n`;
  for (const id of archetypeIds) {
    const pad = Math.max(0, 45 - id.length);
    output += `  ${id}:${' '.repeat(pad)}'${results[id]}',\n`;
  }
  output += '\n';
}

console.log(output);
