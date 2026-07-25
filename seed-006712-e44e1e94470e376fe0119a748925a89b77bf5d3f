#!/usr/bin/env node
/**
 * Applies validated dimension data to streetPathArchetypes.json.
 * Uses TEXT-LEVEL insertion to avoid json.dump corruption of thumbnailUrl paths.
 *
 * Usage: node scripts/applyStreetDimensions.mjs
 */

import { readFileSync, writeFileSync } from 'fs';

// ── STREET DIMENSIONS (62 archetypes, validated + corrected) ─────────────
const STREET_DIMS = [
  // Generic / North American streets
  { id: "narrow_residential_street", typicalWidth_m: 12, minWidth_m: 9, maxWidth_m: 15, suggestedAreaSqm: 1200, laneCount: 2, hasSidewalk: true, hasMedian: false, hasBikeLane: false, shape: "linear" },
  { id: "suburban_residential_street", typicalWidth_m: 16, minWidth_m: 13, maxWidth_m: 20, suggestedAreaSqm: 1600, laneCount: 2, hasSidewalk: true, hasMedian: false, hasBikeLane: false, shape: "linear" },
  { id: "collector_road", typicalWidth_m: 20, minWidth_m: 16, maxWidth_m: 24, suggestedAreaSqm: 2000, laneCount: 2, hasSidewalk: true, hasMedian: false, hasBikeLane: true, shape: "linear" },
  { id: "arterial_boulevard", typicalWidth_m: 30, minWidth_m: 24, maxWidth_m: 40, suggestedAreaSqm: 3000, laneCount: 4, hasSidewalk: true, hasMedian: true, hasBikeLane: true, shape: "linear" },
  { id: "highway_freeway", typicalWidth_m: 40, minWidth_m: 30, maxWidth_m: 60, suggestedAreaSqm: 4000, laneCount: 6, hasSidewalk: false, hasMedian: true, hasBikeLane: false, shape: "linear" },
  { id: "roundabout", typicalWidth_m: 30, minWidth_m: 20, maxWidth_m: 45, suggestedAreaSqm: 2800, laneCount: 2, hasSidewalk: true, hasMedian: false, hasBikeLane: false, shape: "circle" },
  // CORRECTED: cul_de_sac typicalWidth_m 18 → 24
  { id: "cul_de_sac", typicalWidth_m: 24, minWidth_m: 18, maxWidth_m: 30, suggestedAreaSqm: 2400, laneCount: 2, hasSidewalk: true, hasMedian: false, hasBikeLane: false, shape: "loop" },
  { id: "back_alley_service_lane", typicalWidth_m: 5, minWidth_m: 3.5, maxWidth_m: 7, suggestedAreaSqm: 500, laneCount: 1, hasSidewalk: false, hasMedian: false, hasBikeLane: false, shape: "linear" },
  { id: "separated_bike_lane", typicalWidth_m: 3.5, minWidth_m: 2.5, maxWidth_m: 5, suggestedAreaSqm: 350, laneCount: 2, hasSidewalk: false, hasMedian: false, hasBikeLane: true, shape: "linear" },
  { id: "multi_use_trail", typicalWidth_m: 4, minWidth_m: 3, maxWidth_m: 6, suggestedAreaSqm: 400, laneCount: 0, hasSidewalk: false, hasMedian: false, hasBikeLane: true, shape: "linear" },
  { id: "pedestrian_promenade", typicalWidth_m: 12, minWidth_m: 6, maxWidth_m: 20, suggestedAreaSqm: 1200, laneCount: 0, hasSidewalk: false, hasMedian: false, hasBikeLane: false, shape: "linear" },
  { id: "woonerf_shared_street", typicalWidth_m: 10, minWidth_m: 6, maxWidth_m: 14, suggestedAreaSqm: 1000, laneCount: 1, hasSidewalk: false, hasMedian: false, hasBikeLane: false, shape: "linear" },
  { id: "main_street_complete", typicalWidth_m: 26, minWidth_m: 20, maxWidth_m: 34, suggestedAreaSqm: 2600, laneCount: 4, hasSidewalk: true, hasMedian: true, hasBikeLane: true, shape: "linear" },
  { id: "campus_pedestrian_spine", typicalWidth_m: 8, minWidth_m: 5, maxWidth_m: 12, suggestedAreaSqm: 800, laneCount: 0, hasSidewalk: false, hasMedian: false, hasBikeLane: false, shape: "linear" },
  { id: "scenic_parkway", typicalWidth_m: 22, minWidth_m: 16, maxWidth_m: 30, suggestedAreaSqm: 2200, laneCount: 4, hasSidewalk: false, hasMedian: true, hasBikeLane: false, shape: "linear" },
  { id: "riverfront_promenade", typicalWidth_m: 10, minWidth_m: 6, maxWidth_m: 18, suggestedAreaSqm: 1000, laneCount: 0, hasSidewalk: false, hasMedian: false, hasBikeLane: true, shape: "linear" },
  { id: "custom_streets_pathways", typicalWidth_m: 14, minWidth_m: 4, maxWidth_m: 40, suggestedAreaSqm: 1400, laneCount: 2, hasSidewalk: true, hasMedian: false, hasBikeLane: false, shape: "linear" },
  { id: "downtown_thoroughfare", typicalWidth_m: 24, minWidth_m: 18, maxWidth_m: 32, suggestedAreaSqm: 2400, laneCount: 4, hasSidewalk: true, hasMedian: true, hasBikeLane: true, shape: "linear" },
  { id: "pedestrian_only_street", typicalWidth_m: 10, minWidth_m: 5, maxWidth_m: 18, suggestedAreaSqm: 1000, laneCount: 0, hasSidewalk: false, hasMedian: false, hasBikeLane: false, shape: "linear" },
  { id: "green_alley", typicalWidth_m: 5, minWidth_m: 3.5, maxWidth_m: 7, suggestedAreaSqm: 500, laneCount: 1, hasSidewalk: false, hasMedian: false, hasBikeLane: false, shape: "linear" },
  { id: "commercial_alley_laneway", typicalWidth_m: 6, minWidth_m: 4, maxWidth_m: 8, suggestedAreaSqm: 600, laneCount: 1, hasSidewalk: true, hasMedian: false, hasBikeLane: false, shape: "linear" },
  { id: "yield_street", typicalWidth_m: 8, minWidth_m: 6, maxWidth_m: 10, suggestedAreaSqm: 800, laneCount: 1, hasSidewalk: true, hasMedian: false, hasBikeLane: false, shape: "linear" },
  { id: "neighborhood_main_street", typicalWidth_m: 20, minWidth_m: 16, maxWidth_m: 26, suggestedAreaSqm: 2000, laneCount: 2, hasSidewalk: true, hasMedian: false, hasBikeLane: true, shape: "linear" },
  // European streets
  { id: "amsterdam_gracht", typicalWidth_m: 22, minWidth_m: 16, maxWidth_m: 30, suggestedAreaSqm: 2200, laneCount: 2, hasSidewalk: true, hasMedian: false, hasBikeLane: true, shape: "linear" },
  { id: "amsterdam_steeg", typicalWidth_m: 3, minWidth_m: 1.5, maxWidth_m: 4.5, suggestedAreaSqm: 300, laneCount: 0, hasSidewalk: false, hasMedian: false, hasBikeLane: false, shape: "linear" },
  { id: "amsterdam_straat", typicalWidth_m: 16, minWidth_m: 12, maxWidth_m: 22, suggestedAreaSqm: 1600, laneCount: 2, hasSidewalk: true, hasMedian: false, hasBikeLane: true, shape: "linear" },
  { id: "barcelona_eixample_carrer", typicalWidth_m: 20, minWidth_m: 16, maxWidth_m: 24, suggestedAreaSqm: 2000, laneCount: 2, hasSidewalk: true, hasMedian: false, hasBikeLane: true, shape: "linear" },
  { id: "barcelona_passatge", typicalWidth_m: 5, minWidth_m: 3, maxWidth_m: 8, suggestedAreaSqm: 500, laneCount: 0, hasSidewalk: false, hasMedian: false, hasBikeLane: false, shape: "linear" },
  // CORRECTED: barcelona_passeig typicalWidth_m 30 → 60
  { id: "barcelona_passeig", typicalWidth_m: 60, minWidth_m: 40, maxWidth_m: 70, suggestedAreaSqm: 6000, laneCount: 6, hasSidewalk: true, hasMedian: true, hasBikeLane: true, shape: "linear" },
  { id: "haussmann_boulevard", typicalWidth_m: 35, minWidth_m: 28, maxWidth_m: 45, suggestedAreaSqm: 3500, laneCount: 4, hasSidewalk: true, hasMedian: true, hasBikeLane: true, shape: "linear" },
  { id: "parisian_passage", typicalWidth_m: 4, minWidth_m: 3, maxWidth_m: 6, suggestedAreaSqm: 400, laneCount: 0, hasSidewalk: false, hasMedian: false, hasBikeLane: false, shape: "linear" },
  { id: "parisian_rue", typicalWidth_m: 14, minWidth_m: 10, maxWidth_m: 18, suggestedAreaSqm: 1400, laneCount: 2, hasSidewalk: true, hasMedian: false, hasBikeLane: false, shape: "linear" },
  { id: "london_crescent_road", typicalWidth_m: 16, minWidth_m: 12, maxWidth_m: 20, suggestedAreaSqm: 1600, laneCount: 2, hasSidewalk: true, hasMedian: false, hasBikeLane: false, shape: "linear" },
  { id: "london_mews_lane", typicalWidth_m: 6, minWidth_m: 4, maxWidth_m: 8, suggestedAreaSqm: 600, laneCount: 1, hasSidewalk: false, hasMedian: false, hasBikeLane: false, shape: "linear" },
  { id: "london_terrace_street", typicalWidth_m: 14, minWidth_m: 11, maxWidth_m: 18, suggestedAreaSqm: 1400, laneCount: 2, hasSidewalk: true, hasMedian: false, hasBikeLane: false, shape: "linear" },
  // North American city-specific
  { id: "new_york_brownstone_side_street", typicalWidth_m: 18, minWidth_m: 14, maxWidth_m: 22, suggestedAreaSqm: 1800, laneCount: 2, hasSidewalk: true, hasMedian: false, hasBikeLane: false, shape: "linear" },
  { id: "soho_cobblestone_street", typicalWidth_m: 16, minWidth_m: 12, maxWidth_m: 20, suggestedAreaSqm: 1600, laneCount: 2, hasSidewalk: true, hasMedian: false, hasBikeLane: false, shape: "linear" },
  { id: "montreal_commercial_boulevard", typicalWidth_m: 26, minWidth_m: 20, maxWidth_m: 34, suggestedAreaSqm: 2600, laneCount: 4, hasSidewalk: true, hasMedian: true, hasBikeLane: true, shape: "linear" },
  { id: "montreal_plateau_residential_rue", typicalWidth_m: 14, minWidth_m: 10, maxWidth_m: 18, suggestedAreaSqm: 1400, laneCount: 2, hasSidewalk: true, hasMedian: false, hasBikeLane: false, shape: "linear" },
  { id: "montreal_ruelle_verte", typicalWidth_m: 5, minWidth_m: 3.5, maxWidth_m: 7, suggestedAreaSqm: 500, laneCount: 0, hasSidewalk: false, hasMedian: false, hasBikeLane: false, shape: "linear" },
  { id: "toronto_laneway", typicalWidth_m: 5, minWidth_m: 3.5, maxWidth_m: 6.5, suggestedAreaSqm: 500, laneCount: 1, hasSidewalk: false, hasMedian: false, hasBikeLane: false, shape: "linear" },
  // CORRECTED: toronto_streetcar_street typicalWidth_m 26 → 20
  { id: "toronto_streetcar_street", typicalWidth_m: 20, minWidth_m: 16, maxWidth_m: 24, suggestedAreaSqm: 2000, laneCount: 4, hasSidewalk: true, hasMedian: true, hasBikeLane: false, shape: "linear" },
  { id: "toronto_victorian_residential_street", typicalWidth_m: 16, minWidth_m: 12, maxWidth_m: 20, suggestedAreaSqm: 1600, laneCount: 2, hasSidewalk: true, hasMedian: false, hasBikeLane: false, shape: "linear" },
  { id: "vancouver_back_lane", typicalWidth_m: 6, minWidth_m: 4.5, maxWidth_m: 7, suggestedAreaSqm: 600, laneCount: 1, hasSidewalk: false, hasMedian: false, hasBikeLane: false, shape: "linear" },
  { id: "vancouver_cherry_blossom_street", typicalWidth_m: 16, minWidth_m: 13, maxWidth_m: 20, suggestedAreaSqm: 1600, laneCount: 2, hasSidewalk: true, hasMedian: false, hasBikeLane: true, shape: "linear" },
  // CORRECTED: bow_river_pathway typicalWidth_m 4 → 3
  { id: "bow_river_pathway", typicalWidth_m: 3, minWidth_m: 2.5, maxWidth_m: 4, suggestedAreaSqm: 300, laneCount: 0, hasSidewalk: false, hasMedian: false, hasBikeLane: true, shape: "linear" },
  { id: "inglewood_main_street", typicalWidth_m: 20, minWidth_m: 16, maxWidth_m: 24, suggestedAreaSqm: 2000, laneCount: 2, hasSidewalk: true, hasMedian: false, hasBikeLane: true, shape: "linear" },
  { id: "skytrain_elevated_corridor", typicalWidth_m: 10, minWidth_m: 8, maxWidth_m: 14, suggestedAreaSqm: 1000, laneCount: 2, hasSidewalk: false, hasMedian: false, hasBikeLane: false, shape: "elevated" },
  { id: "stephen_avenue_pedestrian_mall", typicalWidth_m: 18, minWidth_m: 14, maxWidth_m: 24, suggestedAreaSqm: 1800, laneCount: 0, hasSidewalk: false, hasMedian: false, hasBikeLane: false, shape: "linear" },
  { id: "halifax_steep_residential_street", typicalWidth_m: 12, minWidth_m: 9, maxWidth_m: 16, suggestedAreaSqm: 1200, laneCount: 2, hasSidewalk: true, hasMedian: false, hasBikeLane: false, shape: "linear" },
  { id: "halifax_waterfront_boardwalk", typicalWidth_m: 6, minWidth_m: 4, maxWidth_m: 10, suggestedAreaSqm: 600, laneCount: 0, hasSidewalk: false, hasMedian: false, hasBikeLane: false, shape: "linear" },
  // Transit corridors
  { id: "brt_bus_rapid_transit_corridor", typicalWidth_m: 28, minWidth_m: 22, maxWidth_m: 36, suggestedAreaSqm: 2800, laneCount: 4, hasSidewalk: true, hasMedian: true, hasBikeLane: false, shape: "linear" },
  { id: "elevated_rail_transit_corridor", typicalWidth_m: 10, minWidth_m: 8, maxWidth_m: 14, suggestedAreaSqm: 1000, laneCount: 2, hasSidewalk: false, hasMedian: false, hasBikeLane: false, shape: "elevated" },
  { id: "light_rail_tram_avenue", typicalWidth_m: 28, minWidth_m: 22, maxWidth_m: 36, suggestedAreaSqm: 2800, laneCount: 4, hasSidewalk: true, hasMedian: true, hasBikeLane: true, shape: "linear" },
  // Bridges
  { id: "urban_vehicular_bridge", typicalWidth_m: 20, minWidth_m: 14, maxWidth_m: 30, suggestedAreaSqm: 2000, laneCount: 4, hasSidewalk: true, hasMedian: true, hasBikeLane: false, shape: "elevated" },
  { id: "landmark_signature_bridge", typicalWidth_m: 28, minWidth_m: 18, maxWidth_m: 40, suggestedAreaSqm: 2800, laneCount: 4, hasSidewalk: true, hasMedian: true, hasBikeLane: true, shape: "elevated" },
  { id: "rail_transit_viaduct", typicalWidth_m: 12, minWidth_m: 9, maxWidth_m: 16, suggestedAreaSqm: 1200, laneCount: 2, hasSidewalk: false, hasMedian: false, hasBikeLane: false, shape: "elevated" },
  { id: "transit_priority_bridge", typicalWidth_m: 16, minWidth_m: 12, maxWidth_m: 22, suggestedAreaSqm: 1600, laneCount: 2, hasSidewalk: true, hasMedian: false, hasBikeLane: true, shape: "elevated" },
  { id: "urban_pedestrian_footbridge", typicalWidth_m: 4, minWidth_m: 2.5, maxWidth_m: 6, suggestedAreaSqm: 400, laneCount: 0, hasSidewalk: false, hasMedian: false, hasBikeLane: false, shape: "elevated" },
  { id: "landscape_park_pedestrian_bridge", typicalWidth_m: 3.5, minWidth_m: 2, maxWidth_m: 5, suggestedAreaSqm: 350, laneCount: 0, hasSidewalk: false, hasMedian: false, hasBikeLane: false, shape: "elevated" },
  { id: "dedicated_cycle_bridge", typicalWidth_m: 5, minWidth_m: 3, maxWidth_m: 7, suggestedAreaSqm: 500, laneCount: 2, hasSidewalk: false, hasMedian: false, hasBikeLane: true, shape: "elevated" },
  { id: "shared_cycle_pedestrian_bridge", typicalWidth_m: 5, minWidth_m: 3.5, maxWidth_m: 7, suggestedAreaSqm: 500, laneCount: 0, hasSidewalk: false, hasMedian: false, hasBikeLane: true, shape: "elevated" },
];

function applyDimensionsToFile(filePath, dimensions) {
  let content = readFileSync(filePath, 'utf8');
  let applied = 0;
  let notFound = 0;

  for (const dim of dimensions) {
    // Find the archetype entry by id
    const idPattern = new RegExp(`"id"\\s*:\\s*"${dim.id}"`);
    const match = idPattern.exec(content);
    if (!match) {
      console.error(`  NOT FOUND: ${dim.id}`);
      notFound++;
      continue;
    }

    // Check if dimensions already exist for this entry
    const afterId = content.substring(match.index);
    const nextBrace = afterId.indexOf('}');
    const entrySlice = afterId.substring(0, nextBrace);

    if (entrySlice.includes('"typicalWidth_m"')) {
      console.log(`  SKIP (already has dims): ${dim.id}`);
      continue;
    }

    // Build the dimension fields to insert after "id" line
    const dimFields = [];
    dimFields.push(`"typicalWidth_m": ${dim.typicalWidth_m}`);
    dimFields.push(`"minWidth_m": ${dim.minWidth_m}`);
    dimFields.push(`"maxWidth_m": ${dim.maxWidth_m}`);
    dimFields.push(`"suggestedAreaSqm": ${dim.suggestedAreaSqm}`);
    dimFields.push(`"laneCount": ${dim.laneCount}`);
    dimFields.push(`"hasSidewalk": ${dim.hasSidewalk}`);
    dimFields.push(`"hasMedian": ${dim.hasMedian}`);
    dimFields.push(`"hasBikeLane": ${dim.hasBikeLane}`);
    dimFields.push(`"shape": "${dim.shape}"`);

    // Find the insertion point — after "id": "..." line
    const insertionStr = `"id": "${dim.id}"`;
    const insertIdx = content.indexOf(insertionStr);
    if (insertIdx < 0) {
      console.error(`  INSERT FAILED: ${dim.id}`);
      notFound++;
      continue;
    }

    // Find the end of the "id" value line (after the closing quote and comma)
    const afterInsert = content.substring(insertIdx + insertionStr.length);
    const commaIdx = afterInsert.indexOf(',');
    if (commaIdx < 0) {
      console.error(`  NO COMMA AFTER ID: ${dim.id}`);
      notFound++;
      continue;
    }

    const insertPoint = insertIdx + insertionStr.length + commaIdx + 1;
    // Use 6-space indent to match the streetPathArchetypes.json formatting
    const dimStr = '\n      ' + dimFields.join(',\n      ') + ',';
    content = content.substring(0, insertPoint) + dimStr + content.substring(insertPoint);

    applied++;
    console.log(`  APPLIED: ${dim.id}`);
  }

  writeFileSync(filePath, content);
  console.log(`\nApplied ${applied} dimension sets, ${notFound} not found`);
}

// ── MAIN ────────────────────────────────────────────────────────────────────
const FILE = 'C:/Users/andre/OneDrive/Documents/Playground/frontend/src/data/streetPathArchetypes.json';

console.log('=== Applying STREET dimensions ===');
applyDimensionsToFile(FILE, STREET_DIMS);
console.log('\nDone!');
