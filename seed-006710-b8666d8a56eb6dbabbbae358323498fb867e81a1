#!/usr/bin/env node
/**
 * Applies validated dimension data to archetype JSON files.
 * Uses TEXT-LEVEL insertion to avoid json.dump corruption of thumbnailUrl paths.
 *
 * Usage: node scripts/applyDimensions.mjs
 */

import { readFileSync, writeFileSync } from 'fs';

// ── BUILDING DIMENSIONS (168 archetypes, validated + corrected) ─────────────
const BUILDING_DIMS = [
  // Batch 1 (0-55)
  {"id": "collegiate_gothic_education", "suggestedWidth_m": 60, "suggestedDepth_m": 25, "minWidth_m": 40, "maxWidth_m": 100, "minDepth_m": 18, "maxDepth_m": 35, "aspectRatio": "2.5:1"},
  {"id": "brownstone_rowhouse_frontage", "suggestedWidth_m": 6, "suggestedDepth_m": 15, "minWidth_m": 5, "maxWidth_m": 8, "minDepth_m": 12, "maxDepth_m": 18, "aspectRatio": "1:2.5"},
  {"id": "classic_brownstone_streetwall", "suggestedWidth_m": 18, "suggestedDepth_m": 18, "minWidth_m": 12, "maxWidth_m": 30, "minDepth_m": 14, "maxDepth_m": 22, "aspectRatio": "1:1"},
  {"id": "historical_brick_main_street", "suggestedWidth_m": 10, "suggestedDepth_m": 18, "minWidth_m": 6, "maxWidth_m": 15, "minDepth_m": 14, "maxDepth_m": 25, "aspectRatio": "1:1.8"},
  {"id": "victorian_heritage_avenue", "suggestedWidth_m": 8, "suggestedDepth_m": 15, "minWidth_m": 6, "maxWidth_m": 12, "minDepth_m": 12, "maxDepth_m": 20, "aspectRatio": "1:2"},
  {"id": "contemporary_midrise_residential", "suggestedWidth_m": 25, "suggestedDepth_m": 18, "minWidth_m": 18, "maxWidth_m": 40, "minDepth_m": 14, "maxDepth_m": 25, "aspectRatio": "1.4:1"},
  {"id": "contemporary_townhouse_courtyard", "suggestedWidth_m": 8, "suggestedDepth_m": 12, "minWidth_m": 6, "maxWidth_m": 10, "minDepth_m": 10, "maxDepth_m": 16, "aspectRatio": "1:1.5"},
  {"id": "detached_contemporary_infill", "suggestedWidth_m": 10, "suggestedDepth_m": 12, "minWidth_m": 7, "maxWidth_m": 14, "minDepth_m": 9, "maxDepth_m": 16, "aspectRatio": "1:1.2"},
  {"id": "courtyard_family_housing", "suggestedWidth_m": 14, "suggestedDepth_m": 14, "minWidth_m": 10, "maxWidth_m": 20, "minDepth_m": 10, "maxDepth_m": 20, "aspectRatio": "1:1"},
  {"id": "modern_glass_office_institutional", "suggestedWidth_m": 30, "suggestedDepth_m": 20, "minWidth_m": 20, "maxWidth_m": 50, "minDepth_m": 15, "maxDepth_m": 30, "aspectRatio": "1.5:1"},
  {"id": "modernist_civic_block", "suggestedWidth_m": 50, "suggestedDepth_m": 30, "minWidth_m": 30, "maxWidth_m": 80, "minDepth_m": 20, "maxDepth_m": 45, "aspectRatio": "1.7:1"},
  {"id": "mid_century_modern_pavilion_block", "suggestedWidth_m": 50, "suggestedDepth_m": 25, "minWidth_m": 30, "maxWidth_m": 70, "minDepth_m": 18, "maxDepth_m": 35, "aspectRatio": "2:1"},
  {"id": "civic_classical_building", "suggestedWidth_m": 40, "suggestedDepth_m": 25, "minWidth_m": 25, "maxWidth_m": 60, "minDepth_m": 18, "maxDepth_m": 35, "aspectRatio": "1.6:1"},
  {"id": "monumental_courthouse_axis", "suggestedWidth_m": 60, "suggestedDepth_m": 35, "minWidth_m": 40, "maxWidth_m": 80, "minDepth_m": 25, "maxDepth_m": 50, "aspectRatio": "1.7:1"},
  {"id": "industrial_brick_mixed_use", "suggestedWidth_m": 30, "suggestedDepth_m": 20, "minWidth_m": 20, "maxWidth_m": 50, "minDepth_m": 15, "maxDepth_m": 30, "aspectRatio": "1.5:1"},
  {"id": "adaptive_reuse_warehouse_lofts", "suggestedWidth_m": 40, "suggestedDepth_m": 20, "minWidth_m": 25, "maxWidth_m": 60, "minDepth_m": 15, "maxDepth_m": 30, "aspectRatio": "2:1"},
  {"id": "scandinavian_urban_residential", "suggestedWidth_m": 20, "suggestedDepth_m": 16, "minWidth_m": 14, "maxWidth_m": 30, "minDepth_m": 12, "maxDepth_m": 22, "aspectRatio": "1.3:1"},
  {"id": "nordic_timber_midrise", "suggestedWidth_m": 20, "suggestedDepth_m": 16, "minWidth_m": 14, "maxWidth_m": 28, "minDepth_m": 12, "maxDepth_m": 22, "aspectRatio": "1.3:1"},
  {"id": "mediterranean_villa_estate", "suggestedWidth_m": 18, "suggestedDepth_m": 14, "minWidth_m": 12, "maxWidth_m": 25, "minDepth_m": 10, "maxDepth_m": 20, "aspectRatio": "1.3:1"},
  {"id": "mediterranean_arcade_mixed_use", "suggestedWidth_m": 20, "suggestedDepth_m": 16, "minWidth_m": 14, "maxWidth_m": 30, "minDepth_m": 12, "maxDepth_m": 22, "aspectRatio": "1.3:1"},
  {"id": "parametric_future_hub", "suggestedWidth_m": 30, "suggestedDepth_m": 25, "minWidth_m": 20, "maxWidth_m": 50, "minDepth_m": 18, "maxDepth_m": 35, "aspectRatio": "1.2:1"},
  {"id": "autonomous_tech_campus", "suggestedWidth_m": 60, "suggestedDepth_m": 40, "minWidth_m": 35, "maxWidth_m": 100, "minDepth_m": 25, "maxDepth_m": 60, "aspectRatio": "1.5:1"},
  {"id": "art_deco_setback_tower", "suggestedWidth_m": 25, "suggestedDepth_m": 20, "minWidth_m": 18, "maxWidth_m": 35, "minDepth_m": 15, "maxDepth_m": 28, "aspectRatio": "1.25:1"},
  {"id": "deco_theater_mainstreet", "suggestedWidth_m": 20, "suggestedDepth_m": 30, "minWidth_m": 14, "maxWidth_m": 25, "minDepth_m": 22, "maxDepth_m": 40, "aspectRatio": "1:1.5"},
  {"id": "traditional_vernacular_market_street", "suggestedWidth_m": 8, "suggestedDepth_m": 16, "minWidth_m": 5, "maxWidth_m": 12, "minDepth_m": 12, "maxDepth_m": 22, "aspectRatio": "1:2"},
  {"id": "vernacular_courtyard_housing", "suggestedWidth_m": 12, "suggestedDepth_m": 12, "minWidth_m": 8, "maxWidth_m": 16, "minDepth_m": 8, "maxDepth_m": 16, "aspectRatio": "1:1"},
  {"id": "minimalist_courtyard_block", "suggestedWidth_m": 25, "suggestedDepth_m": 25, "minWidth_m": 18, "maxWidth_m": 35, "minDepth_m": 18, "maxDepth_m": 35, "aspectRatio": "1:1"},
  {"id": "minimalist_infill_townhouse", "suggestedWidth_m": 5, "suggestedDepth_m": 14, "minWidth_m": 4, "maxWidth_m": 7, "minDepth_m": 10, "maxDepth_m": 18, "aspectRatio": "1:2.8"},
  {"id": "parisian_midrise_block", "suggestedWidth_m": 30, "suggestedDepth_m": 20, "minWidth_m": 20, "maxWidth_m": 50, "minDepth_m": 15, "maxDepth_m": 28, "aspectRatio": "1.5:1"},
  {"id": "parisian_boulevard_corner", "suggestedWidth_m": 18, "suggestedDepth_m": 18, "minWidth_m": 12, "maxWidth_m": 25, "minDepth_m": 12, "maxDepth_m": 25, "aspectRatio": "1:1"},
  {"id": "mountain_alpine_chalet", "suggestedWidth_m": 14, "suggestedDepth_m": 12, "minWidth_m": 10, "maxWidth_m": 18, "minDepth_m": 9, "maxDepth_m": 16, "aspectRatio": "1.2:1"},
  {"id": "alpine_mixed_use_lodge", "suggestedWidth_m": 25, "suggestedDepth_m": 18, "minWidth_m": 16, "maxWidth_m": 35, "minDepth_m": 14, "maxDepth_m": 25, "aspectRatio": "1.4:1"},
  {"id": "transit_oriented_station_block", "suggestedWidth_m": 35, "suggestedDepth_m": 25, "minWidth_m": 25, "maxWidth_m": 50, "minDepth_m": 18, "maxDepth_m": 35, "aspectRatio": "1.4:1"},
  {"id": "transit_podium_residential", "suggestedWidth_m": 35, "suggestedDepth_m": 25, "minWidth_m": 22, "maxWidth_m": 50, "minDepth_m": 18, "maxDepth_m": 35, "aspectRatio": "1.4:1"},
  {"id": "glass_tower_podium_modern", "suggestedWidth_m": 35, "suggestedDepth_m": 35, "minWidth_m": 25, "maxWidth_m": 50, "minDepth_m": 25, "maxDepth_m": 50, "aspectRatio": "1:1"},
  {"id": "skyline_glass_office_cluster", "suggestedWidth_m": 40, "suggestedDepth_m": 40, "minWidth_m": 28, "maxWidth_m": 55, "minDepth_m": 28, "maxDepth_m": 55, "aspectRatio": "1:1"},
  {"id": "civic_monumental_institution", "suggestedWidth_m": 70, "suggestedDepth_m": 40, "minWidth_m": 45, "maxWidth_m": 100, "minDepth_m": 28, "maxDepth_m": 55, "aspectRatio": "1.75:1"},
  {"id": "monumental_museum_axis", "suggestedWidth_m": 70, "suggestedDepth_m": 35, "minWidth_m": 45, "maxWidth_m": 100, "minDepth_m": 25, "maxDepth_m": 50, "aspectRatio": "2:1"},
  {"id": "japanese_contemporary_lanehouse", "suggestedWidth_m": 5, "suggestedDepth_m": 12, "minWidth_m": 3, "maxWidth_m": 7, "minDepth_m": 8, "maxDepth_m": 16, "aspectRatio": "1:2.4"},
  {"id": "japanese_machiya_mixed_use", "suggestedWidth_m": 5, "suggestedDepth_m": 20, "minWidth_m": 3.5, "maxWidth_m": 7, "minDepth_m": 15, "maxDepth_m": 30, "aspectRatio": "1:4"},
  {"id": "eco_urban_bioclimatic_block", "suggestedWidth_m": 30, "suggestedDepth_m": 22, "minWidth_m": 20, "maxWidth_m": 45, "minDepth_m": 16, "maxDepth_m": 30, "aspectRatio": "1.4:1"},
  {"id": "vertical_forest_residential", "suggestedWidth_m": 28, "suggestedDepth_m": 28, "minWidth_m": 20, "maxWidth_m": 38, "minDepth_m": 20, "maxDepth_m": 38, "aspectRatio": "1:1"},
  {"id": "coastal_resort_terrace_block", "suggestedWidth_m": 45, "suggestedDepth_m": 20, "minWidth_m": 30, "maxWidth_m": 60, "minDepth_m": 15, "maxDepth_m": 28, "aspectRatio": "2.25:1"},
  {"id": "coastal_breezeway_mixed_use", "suggestedWidth_m": 25, "suggestedDepth_m": 16, "minWidth_m": 16, "maxWidth_m": 35, "minDepth_m": 12, "maxDepth_m": 22, "aspectRatio": "1.6:1"},
  {"id": "custom_prompt_ready_archetype", "suggestedWidth_m": 20, "suggestedDepth_m": 20, "minWidth_m": 5, "maxWidth_m": 80, "minDepth_m": 5, "maxDepth_m": 80, "aspectRatio": "1:1"},
  {"id": "custom_contextual_experiment", "suggestedWidth_m": 20, "suggestedDepth_m": 20, "minWidth_m": 5, "maxWidth_m": 80, "minDepth_m": 5, "maxDepth_m": 80, "aspectRatio": "1:1"},
  {"id": "community_recreation_centre", "suggestedWidth_m": 60, "suggestedDepth_m": 40, "minWidth_m": 40, "maxWidth_m": 80, "minDepth_m": 30, "maxDepth_m": 55, "aspectRatio": "1.5:1"},
  // CORRECTED: modern_sports_arena was 100x80, validated to 150x120
  {"id": "modern_sports_arena", "suggestedWidth_m": 150, "suggestedDepth_m": 120, "minWidth_m": 100, "maxWidth_m": 200, "minDepth_m": 80, "maxDepth_m": 160, "aspectRatio": "1.25:1"},
  {"id": "boutique_hotel_tower", "suggestedWidth_m": 25, "suggestedDepth_m": 20, "minWidth_m": 18, "maxWidth_m": 35, "minDepth_m": 15, "maxDepth_m": 28, "aspectRatio": "1.25:1"},
  {"id": "neoclassical_institutional", "suggestedWidth_m": 80, "suggestedDepth_m": 40, "minWidth_m": 50, "maxWidth_m": 120, "minDepth_m": 28, "maxDepth_m": 55, "aspectRatio": "2:1"},
  {"id": "brutalist_institutional", "suggestedWidth_m": 70, "suggestedDepth_m": 50, "minWidth_m": 45, "maxWidth_m": 100, "minDepth_m": 35, "maxDepth_m": 70, "aspectRatio": "1.4:1"},
  {"id": "contemporary_civic", "suggestedWidth_m": 60, "suggestedDepth_m": 40, "minWidth_m": 35, "maxWidth_m": 85, "minDepth_m": 25, "maxDepth_m": 55, "aspectRatio": "1.5:1"},
  {"id": "art_deco_healthcare", "suggestedWidth_m": 60, "suggestedDepth_m": 40, "minWidth_m": 40, "maxWidth_m": 85, "minDepth_m": 28, "maxDepth_m": 55, "aspectRatio": "1.5:1"},
  {"id": "functionalist_healthcare", "suggestedWidth_m": 80, "suggestedDepth_m": 50, "minWidth_m": 55, "maxWidth_m": 110, "minDepth_m": 35, "maxDepth_m": 65, "aspectRatio": "1.6:1"},
  {"id": "biophilic_healthcare", "suggestedWidth_m": 70, "suggestedDepth_m": 50, "minWidth_m": 45, "maxWidth_m": 100, "minDepth_m": 35, "maxDepth_m": 65, "aspectRatio": "1.4:1"},
  {"id": "daylight_factory", "suggestedWidth_m": 60, "suggestedDepth_m": 40, "minWidth_m": 40, "maxWidth_m": 90, "minDepth_m": 28, "maxDepth_m": 55, "aspectRatio": "1.5:1"},
  // Batch 2 (56-111)
  {"id": "industrial_park_modernism", "suggestedWidth_m": 60, "suggestedDepth_m": 35, "minWidth_m": 45, "maxWidth_m": 80, "minDepth_m": 25, "maxDepth_m": 50, "aspectRatio": "5:3"},
  {"id": "art_deco_industrial", "suggestedWidth_m": 50, "suggestedDepth_m": 40, "minWidth_m": 35, "maxWidth_m": 65, "minDepth_m": 30, "maxDepth_m": 55, "aspectRatio": "5:4"},
  {"id": "functionalist_brick_industrial", "suggestedWidth_m": 50, "suggestedDepth_m": 40, "minWidth_m": 35, "maxWidth_m": 70, "minDepth_m": 30, "maxDepth_m": 55, "aspectRatio": "5:4"},
  {"id": "structural_expressionism_industrial", "suggestedWidth_m": 80, "suggestedDepth_m": 50, "minWidth_m": 60, "maxWidth_m": 100, "minDepth_m": 35, "maxDepth_m": 65, "aspectRatio": "8:5"},
  {"id": "corrugated_vernacular_industrial", "suggestedWidth_m": 60, "suggestedDepth_m": 35, "minWidth_m": 40, "maxWidth_m": 80, "minDepth_m": 25, "maxDepth_m": 50, "aspectRatio": "12:7"},
  {"id": "machine_aesthetic_heavy_industrial", "suggestedWidth_m": 80, "suggestedDepth_m": 50, "minWidth_m": 55, "maxWidth_m": 120, "minDepth_m": 35, "maxDepth_m": 70, "aspectRatio": "8:5"},
  {"id": "brutalist_utility_heavy_industrial", "suggestedWidth_m": 70, "suggestedDepth_m": 55, "minWidth_m": 50, "maxWidth_m": 100, "minDepth_m": 40, "maxDepth_m": 75, "aspectRatio": "14:11"},
  {"id": "early_20c_megastructure_industrial", "suggestedWidth_m": 150, "suggestedDepth_m": 80, "minWidth_m": 100, "maxWidth_m": 200, "minDepth_m": 60, "maxDepth_m": 110, "aspectRatio": "15:8"},
  {"id": "romanesque_revival_warehouse", "suggestedWidth_m": 40, "suggestedDepth_m": 40, "minWidth_m": 30, "maxWidth_m": 55, "minDepth_m": 30, "maxDepth_m": 55, "aspectRatio": "1:1"},
  {"id": "midcentury_distribution_warehouse", "suggestedWidth_m": 80, "suggestedDepth_m": 50, "minWidth_m": 55, "maxWidth_m": 110, "minDepth_m": 35, "maxDepth_m": 70, "aspectRatio": "8:5"},
  {"id": "modern_bigbox_warehouse", "suggestedWidth_m": 180, "suggestedDepth_m": 90, "minWidth_m": 120, "maxWidth_m": 250, "minDepth_m": 60, "maxDepth_m": 130, "aspectRatio": "2:1"},
  {"id": "parkitecture_recreational", "suggestedWidth_m": 40, "suggestedDepth_m": 30, "minWidth_m": 25, "maxWidth_m": 55, "minDepth_m": 20, "maxDepth_m": 40, "aspectRatio": "4:3"},
  {"id": "civic_modernism_rec_centre", "suggestedWidth_m": 55, "suggestedDepth_m": 35, "minWidth_m": 40, "maxWidth_m": 70, "minDepth_m": 25, "maxDepth_m": 50, "aspectRatio": "11:7"},
  {"id": "postmodern_rec_centre", "suggestedWidth_m": 50, "suggestedDepth_m": 35, "minWidth_m": 35, "maxWidth_m": 65, "minDepth_m": 25, "maxDepth_m": 50, "aspectRatio": "10:7"},
  {"id": "contemporary_sustainable_rec_centre", "suggestedWidth_m": 55, "suggestedDepth_m": 40, "minWidth_m": 40, "maxWidth_m": 75, "minDepth_m": 30, "maxDepth_m": 55, "aspectRatio": "11:8"},
  {"id": "monumental_antiquity_arena", "suggestedWidth_m": 150, "suggestedDepth_m": 120, "minWidth_m": 100, "maxWidth_m": 190, "minDepth_m": 80, "maxDepth_m": 160, "aspectRatio": "5:4"},
  {"id": "high_tech_arena", "suggestedWidth_m": 180, "suggestedDepth_m": 150, "minWidth_m": 130, "maxWidth_m": 230, "minDepth_m": 110, "maxDepth_m": 190, "aspectRatio": "6:5"},
  {"id": "concrete_megastructure_arena", "suggestedWidth_m": 200, "suggestedDepth_m": 160, "minWidth_m": 150, "maxWidth_m": 260, "minDepth_m": 120, "maxDepth_m": 210, "aspectRatio": "5:4"},
  // CORRECTED: chateauesque_hotel was 80x30, validated to 100x40
  {"id": "chateauesque_hotel", "suggestedWidth_m": 100, "suggestedDepth_m": 40, "minWidth_m": 70, "maxWidth_m": 140, "minDepth_m": 28, "maxDepth_m": 55, "aspectRatio": "2.5:1"},
  {"id": "resort_modernism_hotel", "suggestedWidth_m": 60, "suggestedDepth_m": 35, "minWidth_m": 40, "maxWidth_m": 90, "minDepth_m": 25, "maxDepth_m": 50, "aspectRatio": "12:7"},
  {"id": "corporate_tower_hotel", "suggestedWidth_m": 40, "suggestedDepth_m": 40, "minWidth_m": 25, "maxWidth_m": 55, "minDepth_m": 25, "maxDepth_m": 55, "aspectRatio": "1:1"},
  // CORRECTED: historic_grand_station was 100x50, validated to 200x80
  {"id": "historic_grand_station", "suggestedWidth_m": 200, "suggestedDepth_m": 80, "minWidth_m": 120, "maxWidth_m": 300, "minDepth_m": 50, "maxDepth_m": 120, "aspectRatio": "2.5:1"},
  {"id": "contemporary_transit_hub", "suggestedWidth_m": 80, "suggestedDepth_m": 45, "minWidth_m": 55, "maxWidth_m": 120, "minDepth_m": 30, "maxDepth_m": 65, "aspectRatio": "16:9"},
  {"id": "urban_light_rail_stop", "suggestedWidth_m": 30, "suggestedDepth_m": 7, "minWidth_m": 20, "maxWidth_m": 50, "minDepth_m": 4, "maxDepth_m": 10, "aspectRatio": "4:1"},
  {"id": "climbing_wall_building", "suggestedWidth_m": 35, "suggestedDepth_m": 45, "minWidth_m": 25, "maxWidth_m": 50, "minDepth_m": 30, "maxDepth_m": 60, "aspectRatio": "7:9"},
  // CORRECTED: waste_to_energy_plant was 120x80, validated to 160x70
  {"id": "waste_to_energy_plant", "suggestedWidth_m": 160, "suggestedDepth_m": 70, "minWidth_m": 100, "maxWidth_m": 220, "minDepth_m": 50, "maxDepth_m": 100, "aspectRatio": "2.3:1"},
  {"id": "senior_living_complex", "suggestedWidth_m": 60, "suggestedDepth_m": 25, "minWidth_m": 40, "maxWidth_m": 90, "minDepth_m": 18, "maxDepth_m": 35, "aspectRatio": "12:5"},
  {"id": "brewery_distillery", "suggestedWidth_m": 50, "suggestedDepth_m": 40, "minWidth_m": 35, "maxWidth_m": 70, "minDepth_m": 28, "maxDepth_m": 55, "aspectRatio": "5:4"},
  {"id": "solar_farm_agrivoltaics", "suggestedWidth_m": 350, "suggestedDepth_m": 285, "minWidth_m": 200, "maxWidth_m": 500, "minDepth_m": 200, "maxDepth_m": 500, "aspectRatio": "5:4"},
  {"id": "immersive_experience_venue", "suggestedWidth_m": 55, "suggestedDepth_m": 50, "minWidth_m": 35, "maxWidth_m": 75, "minDepth_m": 35, "maxDepth_m": 70, "aspectRatio": "11:10"},
  {"id": "modern_fire_station", "suggestedWidth_m": 40, "suggestedDepth_m": 35, "minWidth_m": 28, "maxWidth_m": 55, "minDepth_m": 25, "maxDepth_m": 50, "aspectRatio": "8:7"},
  // CORRECTED: concert_hall_modern was 70x55, validated to 90x65
  {"id": "concert_hall_modern", "suggestedWidth_m": 90, "suggestedDepth_m": 65, "minWidth_m": 60, "maxWidth_m": 130, "minDepth_m": 45, "maxDepth_m": 90, "aspectRatio": "1.4:1"},
  {"id": "vertiport_evtol", "suggestedWidth_m": 60, "suggestedDepth_m": 60, "minWidth_m": 40, "maxWidth_m": 80, "minDepth_m": 40, "maxDepth_m": 80, "aspectRatio": "1:1"},
  {"id": "shophouse_southeast_asian", "suggestedWidth_m": 5, "suggestedDepth_m": 28, "minWidth_m": 4, "maxWidth_m": 7, "minDepth_m": 20, "maxDepth_m": 40, "aspectRatio": "1:5"},
  {"id": "food_hall_market_hall", "suggestedWidth_m": 60, "suggestedDepth_m": 45, "minWidth_m": 40, "maxWidth_m": 80, "minDepth_m": 30, "maxDepth_m": 65, "aspectRatio": "4:3"},
  {"id": "ev_charging_hub", "suggestedWidth_m": 60, "suggestedDepth_m": 35, "minWidth_m": 40, "maxWidth_m": 85, "minDepth_m": 25, "maxDepth_m": 50, "aspectRatio": "12:7"},
  {"id": "hyperscale_data_center", "suggestedWidth_m": 180, "suggestedDepth_m": 100, "minWidth_m": 120, "maxWidth_m": 250, "minDepth_m": 70, "maxDepth_m": 150, "aspectRatio": "9:5"},
  {"id": "vertical_farm", "suggestedWidth_m": 25, "suggestedDepth_m": 25, "minWidth_m": 18, "maxWidth_m": 40, "minDepth_m": 18, "maxDepth_m": 40, "aspectRatio": "1:1"},
  {"id": "mall_redevelopment", "suggestedWidth_m": 150, "suggestedDepth_m": 100, "minWidth_m": 80, "maxWidth_m": 250, "minDepth_m": 60, "maxDepth_m": 180, "aspectRatio": "3:2"},
  {"id": "terraced_stepped_building", "suggestedWidth_m": 40, "suggestedDepth_m": 30, "minWidth_m": 25, "maxWidth_m": 60, "minDepth_m": 20, "maxDepth_m": 50, "aspectRatio": "4:3"},
  {"id": "calgary_cbe_brutalist_hq", "suggestedWidth_m": 30, "suggestedDepth_m": 17, "minWidth_m": 22, "maxWidth_m": 38, "minDepth_m": 13, "maxDepth_m": 22, "aspectRatio": "16:9"},
  {"id": "farnsworth_house_glass_pavilion", "suggestedWidth_m": 23, "suggestedDepth_m": 9, "minWidth_m": 18, "maxWidth_m": 28, "minDepth_m": 7, "maxDepth_m": 12, "aspectRatio": "5:2"},
  {"id": "amsterdam_bell_gable_house", "suggestedWidth_m": 6, "suggestedDepth_m": 12, "minWidth_m": 5, "maxWidth_m": 8, "minDepth_m": 9, "maxDepth_m": 15, "aspectRatio": "1:2"},
  {"id": "amsterdam_brown_cafe", "suggestedWidth_m": 6, "suggestedDepth_m": 10, "minWidth_m": 4, "maxWidth_m": 8, "minDepth_m": 7, "maxDepth_m": 14, "aspectRatio": "3:5"},
  {"id": "amsterdam_canal_warehouse", "suggestedWidth_m": 10, "suggestedDepth_m": 20, "minWidth_m": 7, "maxWidth_m": 14, "minDepth_m": 15, "maxDepth_m": 28, "aspectRatio": "1:2"},
  {"id": "amsterdam_cornice_house", "suggestedWidth_m": 7, "suggestedDepth_m": 14, "minWidth_m": 5, "maxWidth_m": 9, "minDepth_m": 10, "maxDepth_m": 18, "aspectRatio": "1:2"},
  {"id": "amsterdam_hofje", "suggestedWidth_m": 25, "suggestedDepth_m": 30, "minWidth_m": 18, "maxWidth_m": 35, "minDepth_m": 22, "maxDepth_m": 40, "aspectRatio": "5:6"},
  {"id": "amsterdam_jordaan_house", "suggestedWidth_m": 5, "suggestedDepth_m": 10, "minWidth_m": 4, "maxWidth_m": 7, "minDepth_m": 7, "maxDepth_m": 14, "aspectRatio": "1:2"},
  {"id": "amsterdam_neck_gable_house", "suggestedWidth_m": 6, "suggestedDepth_m": 13, "minWidth_m": 5, "maxWidth_m": 8, "minDepth_m": 9, "maxDepth_m": 16, "aspectRatio": "1:2"},
  {"id": "amsterdam_school_housing", "suggestedWidth_m": 40, "suggestedDepth_m": 12, "minWidth_m": 25, "maxWidth_m": 60, "minDepth_m": 10, "maxDepth_m": 16, "aspectRatio": "10:3"},
  {"id": "amsterdam_spout_gable_house", "suggestedWidth_m": 6, "suggestedDepth_m": 11, "minWidth_m": 4, "maxWidth_m": 8, "minDepth_m": 8, "maxDepth_m": 14, "aspectRatio": "6:11"},
  {"id": "amsterdam_step_gable_house", "suggestedWidth_m": 6, "suggestedDepth_m": 12, "minWidth_m": 5, "maxWidth_m": 8, "minDepth_m": 9, "maxDepth_m": 15, "aspectRatio": "1:2"},
  {"id": "barcelona_corner_chamfer", "suggestedWidth_m": 18, "suggestedDepth_m": 18, "minWidth_m": 14, "maxWidth_m": 22, "minDepth_m": 14, "maxDepth_m": 22, "aspectRatio": "1:1"},
  {"id": "barcelona_mercat", "suggestedWidth_m": 65, "suggestedDepth_m": 45, "minWidth_m": 45, "maxWidth_m": 90, "minDepth_m": 30, "maxDepth_m": 60, "aspectRatio": "13:9"},
  {"id": "barcelona_modernist_workshop", "suggestedWidth_m": 15, "suggestedDepth_m": 18, "minWidth_m": 10, "maxWidth_m": 22, "minDepth_m": 12, "maxDepth_m": 25, "aspectRatio": "5:6"},
  {"id": "barcelona_townhouse", "suggestedWidth_m": 8, "suggestedDepth_m": 14, "minWidth_m": 6, "maxWidth_m": 12, "minDepth_m": 10, "maxDepth_m": 20, "aspectRatio": "4:7"},
  // Batch 3 (112-167)
  {"id": "ecole_republicaine", "suggestedWidth_m": 40, "suggestedDepth_m": 15, "minWidth_m": 30, "maxWidth_m": 60, "minDepth_m": 12, "maxDepth_m": 20, "aspectRatio": "2.67:1"},
  {"id": "eixample_apartment_block", "suggestedWidth_m": 18, "suggestedDepth_m": 18, "minWidth_m": 15, "maxWidth_m": 22, "minDepth_m": 15, "maxDepth_m": 22, "aspectRatio": "1:1"},
  {"id": "grand_magasin", "suggestedWidth_m": 50, "suggestedDepth_m": 35, "minWidth_m": 35, "maxWidth_m": 70, "minDepth_m": 25, "maxDepth_m": 50, "aspectRatio": "1.43:1"},
  {"id": "hotel_particulier", "suggestedWidth_m": 18, "suggestedDepth_m": 22, "minWidth_m": 14, "maxWidth_m": 25, "minDepth_m": 16, "maxDepth_m": 28, "aspectRatio": "1:1.2"},
  {"id": "marche_couvert", "suggestedWidth_m": 40, "suggestedDepth_m": 25, "minWidth_m": 30, "maxWidth_m": 60, "minDepth_m": 18, "maxDepth_m": 35, "aspectRatio": "1.6:1"},
  {"id": "parisian_cafe_brasserie", "suggestedWidth_m": 10, "suggestedDepth_m": 12, "minWidth_m": 6, "maxWidth_m": 15, "minDepth_m": 8, "maxDepth_m": 18, "aspectRatio": "1:1.2"},
  {"id": "parisian_corner_with_dome", "suggestedWidth_m": 20, "suggestedDepth_m": 20, "minWidth_m": 15, "maxWidth_m": 25, "minDepth_m": 15, "maxDepth_m": 25, "aspectRatio": "1:1"},
  {"id": "passage_couvert", "suggestedWidth_m": 8, "suggestedDepth_m": 30, "minWidth_m": 6, "maxWidth_m": 12, "minDepth_m": 20, "maxDepth_m": 50, "aspectRatio": "1:3.75"},
  {"id": "pre_haussmann_marais_building", "suggestedWidth_m": 8, "suggestedDepth_m": 12, "minWidth_m": 6, "maxWidth_m": 12, "minDepth_m": 8, "maxDepth_m": 16, "aspectRatio": "1:1.5"},
  {"id": "georgian_terrace_house", "suggestedWidth_m": 6, "suggestedDepth_m": 12, "minWidth_m": 5, "maxWidth_m": 8, "minDepth_m": 9, "maxDepth_m": 15, "aspectRatio": "1:2"},
  {"id": "london_crescent_terrace", "suggestedWidth_m": 6, "suggestedDepth_m": 12, "minWidth_m": 5, "maxWidth_m": 8, "minDepth_m": 10, "maxDepth_m": 16, "aspectRatio": "1:2"},
  {"id": "london_mews_house", "suggestedWidth_m": 5, "suggestedDepth_m": 8, "minWidth_m": 4, "maxWidth_m": 7, "minDepth_m": 6, "maxDepth_m": 10, "aspectRatio": "1:1.6"},
  {"id": "london_townhouse", "suggestedWidth_m": 6, "suggestedDepth_m": 12, "minWidth_m": 5, "maxWidth_m": 8, "minDepth_m": 9, "maxDepth_m": 15, "aspectRatio": "1:2"},
  {"id": "regency_stucco_terrace", "suggestedWidth_m": 6, "suggestedDepth_m": 12, "minWidth_m": 5, "maxWidth_m": 8, "minDepth_m": 9, "maxDepth_m": 15, "aspectRatio": "1:2"},
  {"id": "victorian_bay_window_terrace", "suggestedWidth_m": 5, "suggestedDepth_m": 10, "minWidth_m": 4, "maxWidth_m": 7, "minDepth_m": 8, "maxDepth_m": 14, "aspectRatio": "1:2"},
  {"id": "new_york_art_deco_tower", "suggestedWidth_m": 30, "suggestedDepth_m": 30, "minWidth_m": 20, "maxWidth_m": 45, "minDepth_m": 20, "maxDepth_m": 45, "aspectRatio": "1:1"},
  {"id": "new_york_corner_bodega", "suggestedWidth_m": 8, "suggestedDepth_m": 8, "minWidth_m": 5, "maxWidth_m": 12, "minDepth_m": 5, "maxDepth_m": 12, "aspectRatio": "1:1"},
  {"id": "new_york_pre_war_apartment", "suggestedWidth_m": 25, "suggestedDepth_m": 25, "minWidth_m": 18, "maxWidth_m": 35, "minDepth_m": 18, "maxDepth_m": 35, "aspectRatio": "1:1"},
  // CORRECTED: new_york_walk_up_tenement was 8x20, validated to 7.6x27
  {"id": "new_york_walk_up_tenement", "suggestedWidth_m": 7.6, "suggestedDepth_m": 27, "minWidth_m": 6, "maxWidth_m": 10, "minDepth_m": 22, "maxDepth_m": 30, "aspectRatio": "1:3.6"},
  {"id": "soho_cast_iron_loft_building", "suggestedWidth_m": 15, "suggestedDepth_m": 25, "minWidth_m": 10, "maxWidth_m": 20, "minDepth_m": 18, "maxDepth_m": 30, "aspectRatio": "1:1.67"},
  {"id": "halifax_ferry_terminal", "suggestedWidth_m": 30, "suggestedDepth_m": 15, "minWidth_m": 20, "maxWidth_m": 45, "minDepth_m": 10, "maxDepth_m": 20, "aspectRatio": "2:1"},
  {"id": "halifax_georgian_colonial", "suggestedWidth_m": 10, "suggestedDepth_m": 10, "minWidth_m": 8, "maxWidth_m": 14, "minDepth_m": 8, "maxDepth_m": 14, "aspectRatio": "1:1"},
  {"id": "halifax_maritime_commercial", "suggestedWidth_m": 10, "suggestedDepth_m": 15, "minWidth_m": 7, "maxWidth_m": 15, "minDepth_m": 10, "maxDepth_m": 20, "aspectRatio": "1:1.5"},
  {"id": "halifax_painted_clapboard_row", "suggestedWidth_m": 6, "suggestedDepth_m": 10, "minWidth_m": 5, "maxWidth_m": 8, "minDepth_m": 8, "maxDepth_m": 14, "aspectRatio": "1:1.67"},
  {"id": "halifax_waterfront_warehouse", "suggestedWidth_m": 20, "suggestedDepth_m": 15, "minWidth_m": 15, "maxWidth_m": 30, "minDepth_m": 10, "maxDepth_m": 20, "aspectRatio": "1.33:1"},
  {"id": "hydrostone_neighbourhood_house", "suggestedWidth_m": 8, "suggestedDepth_m": 9, "minWidth_m": 6, "maxWidth_m": 10, "minDepth_m": 7, "maxDepth_m": 12, "aspectRatio": "1:1.1"},
  {"id": "inglewood_heritage_brick_commercial", "suggestedWidth_m": 10, "suggestedDepth_m": 15, "minWidth_m": 7, "maxWidth_m": 15, "minDepth_m": 10, "maxDepth_m": 22, "aspectRatio": "1:1.5"},
  {"id": "modernisme_casa", "suggestedWidth_m": 12, "suggestedDepth_m": 18, "minWidth_m": 8, "maxWidth_m": 16, "minDepth_m": 12, "maxDepth_m": 22, "aspectRatio": "1:1.5"},
  {"id": "calgary_beltline_mid_rise", "suggestedWidth_m": 30, "suggestedDepth_m": 25, "minWidth_m": 20, "maxWidth_m": 45, "minDepth_m": 18, "maxDepth_m": 35, "aspectRatio": "1.2:1"},
  {"id": "calgary_ctrain_station", "suggestedWidth_m": 60, "suggestedDepth_m": 6, "minWidth_m": 40, "maxWidth_m": 80, "minDepth_m": 4, "maxDepth_m": 10, "aspectRatio": "10:1"},
  {"id": "calgary_inner_city_bungalow", "suggestedWidth_m": 10, "suggestedDepth_m": 12, "minWidth_m": 8, "maxWidth_m": 13, "minDepth_m": 9, "maxDepth_m": 15, "aspectRatio": "1:1.2"},
  {"id": "calgary_modern_infill_house", "suggestedWidth_m": 7, "suggestedDepth_m": 13, "minWidth_m": 5, "maxWidth_m": 10, "minDepth_m": 10, "maxDepth_m": 16, "aspectRatio": "1:1.85"},
  // CORRECTED: calgary_new_central_library was 80x70, validated to 75x60
  {"id": "calgary_new_central_library", "suggestedWidth_m": 75, "suggestedDepth_m": 60, "minWidth_m": 65, "maxWidth_m": 85, "minDepth_m": 50, "maxDepth_m": 70, "aspectRatio": "1.25:1"},
  {"id": "calgary_plus_15_connected_tower", "suggestedWidth_m": 35, "suggestedDepth_m": 35, "minWidth_m": 25, "maxWidth_m": 50, "minDepth_m": 25, "maxDepth_m": 50, "aspectRatio": "1:1"},
  {"id": "calgary_sandstone_heritage", "suggestedWidth_m": 15, "suggestedDepth_m": 18, "minWidth_m": 10, "maxWidth_m": 22, "minDepth_m": 12, "maxDepth_m": 25, "aspectRatio": "1:1.2"},
  {"id": "gastown_heritage_commercial", "suggestedWidth_m": 10, "suggestedDepth_m": 18, "minWidth_m": 7, "maxWidth_m": 15, "minDepth_m": 12, "maxDepth_m": 25, "aspectRatio": "1:1.8"},
  {"id": "vancouver_craftsman_bungalow", "suggestedWidth_m": 10, "suggestedDepth_m": 12, "minWidth_m": 8, "maxWidth_m": 13, "minDepth_m": 9, "maxDepth_m": 15, "aspectRatio": "1:1.2"},
  {"id": "vancouver_laneway_house", "suggestedWidth_m": 8, "suggestedDepth_m": 9, "minWidth_m": 6, "maxWidth_m": 10, "minDepth_m": 7, "maxDepth_m": 12, "aspectRatio": "1:1.1"},
  {"id": "vancouver_special", "suggestedWidth_m": 10, "suggestedDepth_m": 12, "minWidth_m": 8, "maxWidth_m": 13, "minDepth_m": 9, "maxDepth_m": 15, "aspectRatio": "1:1.2"},
  {"id": "vancouverism_tower_podium", "suggestedWidth_m": 25, "suggestedDepth_m": 25, "minWidth_m": 18, "maxWidth_m": 40, "minDepth_m": 18, "maxDepth_m": 40, "aspectRatio": "1:1"},
  {"id": "skytrain_elevated_station", "suggestedWidth_m": 70, "suggestedDepth_m": 6, "minWidth_m": 50, "maxWidth_m": 90, "minDepth_m": 4, "maxDepth_m": 8, "aspectRatio": "11.67:1"},
  {"id": "west_end_mid_century_tower", "suggestedWidth_m": 20, "suggestedDepth_m": 20, "minWidth_m": 15, "maxWidth_m": 28, "minDepth_m": 15, "maxDepth_m": 28, "aspectRatio": "1:1"},
  {"id": "toronto_annex_mansion", "suggestedWidth_m": 14, "suggestedDepth_m": 16, "minWidth_m": 10, "maxWidth_m": 18, "minDepth_m": 12, "maxDepth_m": 20, "aspectRatio": "1:1.14"},
  {"id": "toronto_bay_and_gable_house", "suggestedWidth_m": 6, "suggestedDepth_m": 12, "minWidth_m": 5, "maxWidth_m": 8, "minDepth_m": 9, "maxDepth_m": 16, "aspectRatio": "1:2"},
  {"id": "toronto_brick_rowhouse", "suggestedWidth_m": 5, "suggestedDepth_m": 12, "minWidth_m": 4, "maxWidth_m": 7, "minDepth_m": 9, "maxDepth_m": 15, "aspectRatio": "1:2.4"},
  {"id": "toronto_condo_podium_tower", "suggestedWidth_m": 30, "suggestedDepth_m": 30, "minWidth_m": 20, "maxWidth_m": 45, "minDepth_m": 20, "maxDepth_m": 45, "aspectRatio": "1:1"},
  {"id": "toronto_edwardian_foursquare", "suggestedWidth_m": 8, "suggestedDepth_m": 10, "minWidth_m": 7, "maxWidth_m": 11, "minDepth_m": 8, "maxDepth_m": 13, "aspectRatio": "1:1.25"},
  {"id": "toronto_junction_converted_industrial", "suggestedWidth_m": 25, "suggestedDepth_m": 20, "minWidth_m": 15, "maxWidth_m": 40, "minDepth_m": 15, "maxDepth_m": 30, "aspectRatio": "1.25:1"},
  {"id": "toronto_streetcar_platform_stop", "suggestedWidth_m": 40, "suggestedDepth_m": 4, "minWidth_m": 25, "maxWidth_m": 60, "minDepth_m": 3, "maxDepth_m": 6, "aspectRatio": "10:1"},
  {"id": "mile_end_cultural_triplex", "suggestedWidth_m": 8, "suggestedDepth_m": 12, "minWidth_m": 6, "maxWidth_m": 10, "minDepth_m": 9, "maxDepth_m": 15, "aspectRatio": "1:1.5"},
  {"id": "montreal_depanneur", "suggestedWidth_m": 8, "suggestedDepth_m": 8, "minWidth_m": 5, "maxWidth_m": 10, "minDepth_m": 6, "maxDepth_m": 12, "aspectRatio": "1:1"},
  {"id": "montreal_duplex", "suggestedWidth_m": 9, "suggestedDepth_m": 12, "minWidth_m": 7, "maxWidth_m": 12, "minDepth_m": 9, "maxDepth_m": 15, "aspectRatio": "1:1.33"},
  // CORRECTED: montreal_plateau_triplex was 9x13, validated to 7.5x16
  {"id": "montreal_plateau_triplex", "suggestedWidth_m": 7.5, "suggestedDepth_m": 16, "minWidth_m": 6, "maxWidth_m": 10, "minDepth_m": 13, "maxDepth_m": 19, "aspectRatio": "1:2.1"},
  {"id": "montreal_second_empire_civic", "suggestedWidth_m": 30, "suggestedDepth_m": 20, "minWidth_m": 20, "maxWidth_m": 45, "minDepth_m": 15, "maxDepth_m": 30, "aspectRatio": "1.5:1"},
  {"id": "old_montreal_limestone_commercial", "suggestedWidth_m": 12, "suggestedDepth_m": 20, "minWidth_m": 8, "maxWidth_m": 18, "minDepth_m": 15, "maxDepth_m": 28, "aspectRatio": "1:1.67"},
  {"id": "old_montreal_warehouse_loft", "suggestedWidth_m": 20, "suggestedDepth_m": 25, "minWidth_m": 15, "maxWidth_m": 30, "minDepth_m": 18, "maxDepth_m": 35, "aspectRatio": "1:1.25"},
];

// ── Apply dimensions to a JSON file ─────────────────────────────────────────
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

    // Check if dimensions already exist
    const afterId = content.substring(match.index);
    const nextBrace = afterId.indexOf('}');
    const entrySlice = afterId.substring(0, nextBrace);

    // Build the dimension fields to add
    const dimFields = [];
    if (dim.suggestedWidth_m !== undefined) dimFields.push(`"suggestedWidth_m": ${dim.suggestedWidth_m}`);
    if (dim.suggestedDepth_m !== undefined) dimFields.push(`"suggestedDepth_m": ${dim.suggestedDepth_m}`);
    if (dim.minWidth_m !== undefined) dimFields.push(`"minWidth_m": ${dim.minWidth_m}`);
    if (dim.maxWidth_m !== undefined) dimFields.push(`"maxWidth_m": ${dim.maxWidth_m}`);
    if (dim.minDepth_m !== undefined) dimFields.push(`"minDepth_m": ${dim.minDepth_m}`);
    if (dim.maxDepth_m !== undefined) dimFields.push(`"maxDepth_m": ${dim.maxDepth_m}`);
    if (dim.aspectRatio !== undefined) dimFields.push(`"aspectRatio": "${dim.aspectRatio}"`);
    // Street-specific fields
    if (dim.typicalWidth_m !== undefined) dimFields.push(`"typicalWidth_m": ${dim.typicalWidth_m}`);
    if (dim.laneCount !== undefined) dimFields.push(`"laneCount": ${dim.laneCount}`);
    if (dim.hasSidewalk !== undefined) dimFields.push(`"hasSidewalk": ${dim.hasSidewalk}`);
    if (dim.hasMedian !== undefined) dimFields.push(`"hasMedian": ${dim.hasMedian}`);
    if (dim.hasBikeLane !== undefined) dimFields.push(`"hasBikeLane": ${dim.hasBikeLane}`);
    if (dim.shape !== undefined) dimFields.push(`"shape": "${dim.shape}"`);
    // Park-specific fields
    if (dim.minAreaSqm !== undefined) dimFields.push(`"minAreaSqm": ${dim.minAreaSqm}`);
    if (dim.maxAreaSqm !== undefined) dimFields.push(`"maxAreaSqm": ${dim.maxAreaSqm}`);

    // Check if suggestedWidth_m already exists for this entry
    if (entrySlice.includes('"suggestedWidth_m"') || entrySlice.includes('"typicalWidth_m"')) {
      console.log(`  SKIP (already has dims): ${dim.id}`);
      continue;
    }

    // Find the right insertion point — after "id": "..." line
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
    const dimStr = '\n    ' + dimFields.join(',\n    ') + ',';
    content = content.substring(0, insertPoint) + dimStr + content.substring(insertPoint);

    applied++;
  }

  writeFileSync(filePath, content);
  console.log(`Applied ${applied} dimension sets, ${notFound} not found`);
}

// ── MAIN ────────────────────────────────────────────────────────────────────
const BASE = 'C:/Users/andre/OneDrive/Documents/Playground/frontend/src/data';

console.log('=== Applying BUILDING dimensions ===');
applyDimensionsToFile(`${BASE}/buildingArchetypes.json`, BUILDING_DIMS);

console.log('\nDone! Dimensions applied to archetype JSON files.');
console.log('Parks and streets will be applied in a follow-up pass.');
