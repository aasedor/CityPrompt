#!/usr/bin/env node
/**
 * Script to add minFloors/maxFloors to each building archetype
 * based on archetype id, title, heightTendency, and developmentTypes.
 */
import { readFileSync, writeFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const filePath = resolve(__dirname, '../src/data/buildingArchetypes.json');

const data = JSON.parse(readFileSync(filePath, 'utf8'));

// Classification rules by archetype id patterns
const FLOOR_RANGES = {
  // Single-family homes: 1-3
  singleFamily: {
    patterns: [
      'detached_contemporary_infill',
      'mediterranean_villa_estate',
      'mountain_alpine_chalet',
      'japanese_contemporary_lanehouse',
    ],
    min: 1,
    max: 3,
  },
  // Duplexes/townhouses: 2-4
  townhouse: {
    patterns: [
      'brownstone_rowhouse_frontage',
      'contemporary_townhouse_courtyard',
      'courtyard_family_housing',
      'minimalist_infill_townhouse',
      'vernacular_courtyard_housing',
    ],
    min: 2,
    max: 4,
  },
  // Low-mid rise: 2-5
  lowMidRise: {
    patterns: [
      'classic_brownstone_streetwall',
      'victorian_heritage_avenue',
      'scandinavian_urban_residential',
      'japanese_machiya_mixed_use',
    ],
    min: 2,
    max: 5,
  },
  // Mid-rise: 4-8
  midRise: {
    patterns: [
      'contemporary_midrise_residential',
      'nordic_timber_midrise',
      'parisian_midrise_block',
      'parisian_boulevard_corner',
      'eco_urban_bioclimatic_block',
      'minimalist_courtyard_block',
      'mediterranean_arcade_mixed_use',
    ],
    min: 4,
    max: 8,
  },
  // Mid-high rise: 3-12
  midHighRise: {
    patterns: [
      'historical_brick_main_street',
      'traditional_vernacular_market_street',
      'transit_oriented_station_block',
      'transit_podium_residential',
      'art_deco_setback_tower',
      'coastal_breezeway_mixed_use',
      'coastal_resort_terrace_block',
      'alpine_mixed_use_lodge',
      'vertical_forest_residential',
    ],
    min: 3,
    max: 12,
  },
  // High-rise: 15-50
  highRise: {
    patterns: [
      'glass_tower_podium_modern',
      'skyline_glass_office_cluster',
    ],
    min: 15,
    max: 50,
  },
  // Institutional/civic: 2-6
  civic: {
    patterns: [
      'civic_classical_building',
      'civic_monumental_institution',
      'monumental_courthouse_axis',
      'monumental_museum_axis',
      'modernist_civic_block',
      'mid_century_modern_pavilion_block',
    ],
    min: 2,
    max: 6,
  },
  // Office: 5-40
  office: {
    patterns: [
      'parametric_future_hub',
      'autonomous_tech_campus',
      'modern_glass_office_institutional',
    ],
    min: 5,
    max: 40,
  },
  // Light commercial/retail: 1-4
  lightCommercial: {
    patterns: [
      'deco_theater_mainstreet',
    ],
    min: 1,
    max: 4,
  },
  // Industrial/warehouse: 1-6
  industrial: {
    patterns: [
      'industrial_brick_mixed_use',
      'adaptive_reuse_warehouse_lofts',
    ],
    min: 1,
    max: 6,
  },
  // Hospitality: 2-8
  hospitality: {
    patterns: [],
    min: 2,
    max: 8,
  },
  // Custom: 1-50
  custom: {
    patterns: [
      'custom_prompt_ready_archetype',
      'custom_contextual_experiment',
    ],
    min: 1,
    max: 50,
  },
};

function getFloorRange(archetype) {
  const id = archetype.id;

  for (const [, group] of Object.entries(FLOOR_RANGES)) {
    if (group.patterns.includes(id)) {
      return { minFloors: group.min, maxFloors: group.max };
    }
  }

  // Fallback based on heightTendency if not explicitly matched
  const ht = archetype.styleProfile?.heightTendency || '';
  if (ht.toLowerCase().includes('high rise') || ht.toLowerCase().includes('high-rise')) {
    return { minFloors: 15, maxFloors: 50 };
  }
  if (ht.toLowerCase().includes('mid to high')) {
    return { minFloors: 4, maxFloors: 12 };
  }
  if (ht.toLowerCase().includes('low-mid') || ht.toLowerCase().includes('low to mid')) {
    return { minFloors: 2, maxFloors: 5 };
  }

  // Default mid-range
  return { minFloors: 2, maxFloors: 8 };
}

let updated = 0;
for (const archetype of data.archetypes) {
  const range = getFloorRange(archetype);
  archetype.minFloors = range.minFloors;
  archetype.maxFloors = range.maxFloors;
  updated++;
  console.log(`  ${archetype.id}: ${range.minFloors}-${range.maxFloors}`);
}

writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf8');
console.log(`\nUpdated ${updated} archetypes with floor ranges.`);
