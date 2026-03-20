/**
 * Archetype Shade Map
 *
 * Maps every archetype ID to a unique hex "shadeId" colour, grouped by hue family:
 *   - Red   (h 5-15, s 55-90%, l 35-55%)  : commercial / mixed-use / institutional / industrial
 *   - Yellow (h 45-55, s 60-90%, l 40-55%) : purely residential
 *   - Gray  (h 0, s 0-8%, l 30-60%)        : streets & pathways
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
  kyoto_philosophers_walk:            '#4d4d4d',
  parisian_boulevard:                 '#595959',
  barcelona_rambla:                   '#666666',
  amsterdam_canal_street:             '#737373',
  copenhagen_cycle_street:            '#808080',
  brownstone_residential_street:      '#8c8c8c',
  whistler_village_lane:              '#999999',
  english_garden_path:                '#4f4a4a',
  central_park_drive:                 '#5c5757',
  tokyo_shared_street:                '#696363',
  scandinavian_green_street:          '#767070',
  mediterranean_promenade:            '#837c7c',
  modern_transit_boulevard:           '#8f8989',
  brt_corridor:                       '#9c9696',
  mountain_scenic_parkway:            '#514848',
  dutch_woonerf:                      '#5e5454',
  campus_pedestrian_spine:            '#6b6161',
  riverfront_promenade:               '#796d6d',
  industrial_greenway:                '#867979',
  main_street_complete_street:        '#928686',
  tram_priority_avenue:               '#9e9494',
  festival_pedestrian_street:         '#534646',
  neighborhood_school_street:         '#605252',
  civic_esplanade:                    '#6e5e5e',
  eco_mobility_greenway:              '#7c6a6a',
  airport_connector_boulevard:        '#8a7575',
  hillside_switchback_road:           '#958383',
  custom_streets_pathways:            '#a19191',
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
  return SHADE_MAP[archetypeId] ?? '#888888';
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
