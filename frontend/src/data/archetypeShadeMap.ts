/**
 * Archetype Shade Map
 *
 * Maps every archetype ID to a unique hex "shadeId" colour, grouped by hue family:
 *   - Red   (h 5-15, s 55-90%, l 35-55%)  : commercial / mixed-use / institutional / industrial
 *   - Yellow (h 45-55, s 60-90%, l 40-55%) : purely residential
 *   - Gray  (h 0, s 0-8%, l 30-60%)        : streets & pathways
 *   - Green (h 90-160, s 30-70%, l 25-50%) : parks & green space
 *   - Teal  (h 170-200, s 30-60%, l 30-50%): plazas & hardscape
 *   - Blue  (h 200-230, s 40-70%, l 30-50%): water features & parking
 *
 * Every shade within a family is guaranteed >= 2 % HSL lightness or saturation
 * apart from its neighbours.
 */

// ---------------------------------------------------------------------------
// Shade map  (archetypeId -> hex)
// ---------------------------------------------------------------------------

export const SHADE_MAP: Record<string, string> = {
  // ── Red family: Commercial / Mixed-use / Institutional ──────────────
  brownstone_rowhouse_frontage:       '#8a3028',
  historical_brick_main_street:       '#9e382e',
  victorian_heritage_avenue:          '#b23f34',
  contemporary_midrise_residential:   '#c64739',
  modern_glass_office_institutional:  '#cb5a4d',
  modernist_civic_block:              '#8f2f24',
  mid_century_modern_pavilion_block:  '#a33729',
  civic_classical_building:           '#b83e2e',
  monumental_courthouse_axis:         '#cc4633',
  industrial_brick_mixed_use:         '#d15947',
  adaptive_reuse_warehouse_lofts:     '#932f1f',
  nordic_timber_midrise:              '#a83624',
  mediterranean_arcade_mixed_use:     '#bd3e28',
  parametric_future_hub:              '#d2462d',
  autonomous_tech_campus:             '#d75942',
  art_deco_setback_tower:             '#982f1b',
  deco_theater_mainstreet:            '#ad361f',
  traditional_vernacular_market_street: '#c33e22',
  parisian_midrise_block:             '#d94626',
  parisian_boulevard_corner:          '#dd593c',
  alpine_mixed_use_lodge:             '#9c2f16',
  transit_oriented_station_block:     '#b33719',
  transit_podium_residential:         '#c93f1d',
  glass_tower_podium_modern:          '#df4720',
  skyline_glass_office_cluster:       '#e25a36',
  civic_monumental_institution:       '#a13012',
  monumental_museum_axis:             '#b83814',
  japanese_machiya_mixed_use:         '#cf4017',
  eco_urban_bioclimatic_block:        '#e64819',
  coastal_resort_terrace_block:       '#e85b30',
  coastal_breezeway_mixed_use:        '#a5320d',
  custom_prompt_ready_archetype:      '#bd3a0f',
  custom_contextual_experiment:       '#d44211',

  // ── Yellow family: Residential ──────────────────────────────────────
  classic_brownstone_streetwall:      '#a38529',
  contemporary_townhouse_courtyard:   '#c2a030',
  detached_contemporary_infill:       '#d1b347',
  courtyard_family_housing:           '#ab8f21',
  scandinavian_urban_residential:     '#cbac27',
  mediterranean_villa_estate:         '#dabf3f',
  vernacular_courtyard_housing:       '#b39a19',
  minimalist_courtyard_block:         '#d4ba1e',
  minimalist_infill_townhouse:        '#e2cc36',
  mountain_alpine_chalet:             '#baa712',
  japanese_contemporary_lanehouse:    '#ddc915',
  vertical_forest_residential:        '#ebdb2e',

  // ── Gray family: Streets & Pathways ─────────────────────────────────
  narrow_residential_street:          '#4d4d4d',
  suburban_residential_street:        '#565656',
  collector_road:                     '#5f5f5f',
  arterial_boulevard:                 '#686868',
  highway_freeway:                    '#717171',
  roundabout:                         '#7a7a7a',
  cul_de_sac:                         '#838383',
  back_alley_service_lane:            '#8c8c8c',
  separated_bike_lane:                '#959595',
  multi_use_trail:                    '#4f4a4a',
  pedestrian_promenade:               '#585353',
  woonerf_shared_street:              '#615c5c',
  brt_corridor:                       '#6a6565',
  light_rail_avenue:                  '#736e6e',
  main_street_complete:               '#7c7777',
  campus_pedestrian_spine:            '#858080',
  scenic_parkway:                     '#8e8989',
  riverfront_promenade:               '#979292',
  custom_streets_pathways:            '#a09b9b',

  // ── Green family: Parks & Green Space ───────────────────────────────
  urban_pocket_park:                  '#2d6b30',
  neighborhood_park:                  '#357a38',
  community_park:                     '#3d8940',
  regional_park:                      '#2a5e2d',
  dog_park:                           '#4b8f4e',
  skate_park:                         '#539756',
  sports_field_complex:               '#3a7f3d',
  tennis_court_cluster:               '#5ba05e',
  botanical_garden:                   '#326e35',
  japanese_garden:                    '#427442',
  memorial_garden:                    '#4a7d4d',
  urban_forest:                       '#255725',
  riparian_buffer:                    '#2f632f',
  wetland_rain_garden:                '#376b3a',
  playground_adventure:               '#63a866',
  splash_pad_area:                    '#6bb06e',
  amphitheater_lawn:                  '#527f55',
  community_garden:                   '#5a8a5d',
  cemetery_memorial_grounds:          '#488048',

  // ── Teal family: Plazas & Hardscape ─────────────────────────────────
  formal_civic_plaza:                 '#2d6b6b',
  market_square:                      '#357a7a',
  courtyard_plaza:                    '#3d7878',
  promenade_boardwalk:                '#2a6060',
  transit_plaza:                      '#458585',
  amphitheater_performance_space:     '#4d8d8d',

  // ── Blue family: Water Features & Parking ───────────────────────────
  surface_parking_lot:                '#4a6a8a',
  structured_parking_garage:          '#527292',
  underground_parking_entry:          '#3f5f7f',
  green_parking_lot:                  '#5a7a9a',
  pond_lake:                          '#2d5b8a',
  fountain_water_feature:             '#356392',
  stormwater_retention_pond:          '#3d6b9a',
  swimming_pool_complex:              '#4573a2',
  canal_waterway:                     '#2a5580',

  // ── Custom ──────────────────────────────────────────────────────────
  custom_parks_plazas:                '#629062',
};

// ---------------------------------------------------------------------------
// Reverse lookup  (hex -> archetypeId)
// ---------------------------------------------------------------------------

export const SHADE_TO_ARCHETYPE: Map<string, string> = new Map(
  Object.entries(SHADE_MAP).map(([id, hex]) => [hex.toLowerCase(), id]),
);

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Return the unique shade hex for a given archetype ID.
 * Falls back to a neutral mid-gray (`#888888`) if the ID is unknown.
 */
export function getShadeForArchetype(archetypeId: string): string {
  // Exact match first
  if (SHADE_MAP[archetypeId]) return SHADE_MAP[archetypeId];

  // Prefix match: the stored ID may be an image-level ID like
  // "parisian_midrise_block_front_day" while the shade map key is the
  // option-level "parisian_midrise_block".  Try all shade map keys as prefixes.
  for (const key of Object.keys(SHADE_MAP)) {
    if (archetypeId.startsWith(key + '_') || archetypeId.startsWith(key)) {
      return SHADE_MAP[key];
    }
  }

  return '#888888';
}

/**
 * Given a hex colour, find the archetype whose shade is closest within
 * an optional per-channel RGB tolerance (default +-3).
 *
 * Returns `null` when no archetype falls within the tolerance window.
 */
export function getArchetypeForShade(
  shadeHex: string,
  tolerance = 3,
): string | null {
  const target = hexToRgb(shadeHex);
  if (!target) return null;

  // Fast exact match first
  const exact = SHADE_TO_ARCHETYPE.get(shadeHex.toLowerCase());
  if (exact) return exact;

  // Fuzzy scan
  let bestId: string | null = null;
  let bestDist = Infinity;

  for (const [hex, id] of SHADE_TO_ARCHETYPE) {
    const rgb = hexToRgb(hex)!;
    const dr = Math.abs(rgb.r - target.r);
    const dg = Math.abs(rgb.g - target.g);
    const db = Math.abs(rgb.b - target.b);

    if (dr <= tolerance && dg <= tolerance && db <= tolerance) {
      const dist = dr + dg + db;
      if (dist < bestDist) {
        bestDist = dist;
        bestId = id;
      }
    }
  }

  return bestId;
}

// ---------------------------------------------------------------------------
// Internal
// ---------------------------------------------------------------------------

function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  const m = /^#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i.exec(hex);
  if (!m) return null;
  return { r: parseInt(m[1], 16), g: parseInt(m[2], 16), b: parseInt(m[3], 16) };
}
