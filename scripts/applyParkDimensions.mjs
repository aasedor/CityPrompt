#!/usr/bin/env node
/**
 * Applies validated dimension data to openSpaceArchetypes.json.
 * Uses TEXT-LEVEL insertion to avoid json.dump corruption of thumbnailUrl paths.
 *
 * Usage: node scripts/applyParkDimensions.mjs
 */

import { readFileSync, writeFileSync } from 'fs';

// ── PARK DIMENSIONS (88 archetypes, validated + corrected) ─────────────────
const PARK_DIMS = [
  // Landscape Parks
  {"id": "urban_pocket_park", "suggestedWidth_m": 20, "suggestedDepth_m": 20, "minWidth_m": 10, "maxWidth_m": 30, "minDepth_m": 10, "maxDepth_m": 30, "minAreaSqm": 200, "maxAreaSqm": 900, "aspectRatio": "1:1", "shape": "rectangular", "suggestedAreaSqm": 400},
  {"id": "neighborhood_park", "suggestedWidth_m": 100, "suggestedDepth_m": 80, "minWidth_m": 50, "maxWidth_m": 200, "minDepth_m": 40, "maxDepth_m": 160, "minAreaSqm": 2000, "maxAreaSqm": 32000, "aspectRatio": "1.25:1", "shape": "rectangular", "suggestedAreaSqm": 8000},
  {"id": "community_park", "suggestedWidth_m": 250, "suggestedDepth_m": 160, "minWidth_m": 100, "maxWidth_m": 400, "minDepth_m": 80, "maxDepth_m": 250, "minAreaSqm": 8000, "maxAreaSqm": 100000, "aspectRatio": "1.6:1", "shape": "irregular", "suggestedAreaSqm": 40000},
  {"id": "regional_park", "suggestedWidth_m": 500, "suggestedDepth_m": 400, "minWidth_m": 200, "maxWidth_m": 1000, "minDepth_m": 150, "maxDepth_m": 800, "minAreaSqm": 30000, "maxAreaSqm": 800000, "aspectRatio": "1.25:1", "shape": "irregular", "suggestedAreaSqm": 200000},
  {"id": "dog_park", "suggestedWidth_m": 80, "suggestedDepth_m": 50, "minWidth_m": 30, "maxWidth_m": 150, "minDepth_m": 20, "maxDepth_m": 100, "minAreaSqm": 600, "maxAreaSqm": 15000, "aspectRatio": "1.6:1", "shape": "irregular", "suggestedAreaSqm": 4000},

  // Sports & Recreation
  {"id": "skate_park", "suggestedWidth_m": 40, "suggestedDepth_m": 30, "minWidth_m": 20, "maxWidth_m": 80, "minDepth_m": 15, "maxDepth_m": 60, "minAreaSqm": 300, "maxAreaSqm": 4800, "aspectRatio": "1.3:1", "shape": "irregular"},
  {"id": "sports_field_complex", "suggestedWidth_m": 120, "suggestedDepth_m": 90, "minWidth_m": 70, "maxWidth_m": 250, "minDepth_m": 50, "maxDepth_m": 180, "minAreaSqm": 3500, "maxAreaSqm": 45000, "aspectRatio": "1.3:1", "shape": "rectangular"},
  {"id": "tennis_court_cluster", "suggestedWidth_m": 40, "suggestedDepth_m": 36, "minWidth_m": 20, "maxWidth_m": 80, "minDepth_m": 18, "maxDepth_m": 72, "minAreaSqm": 360, "maxAreaSqm": 5760, "aspectRatio": "1.1:1", "shape": "rectangular"},

  // Specialty Gardens
  {"id": "botanical_garden", "suggestedWidth_m": 200, "suggestedDepth_m": 150, "minWidth_m": 80, "maxWidth_m": 400, "minDepth_m": 60, "maxDepth_m": 300, "minAreaSqm": 4800, "maxAreaSqm": 120000, "aspectRatio": "1.3:1", "shape": "irregular", "suggestedAreaSqm": 30000},
  {"id": "japanese_garden", "suggestedWidth_m": 70, "suggestedDepth_m": 70, "minWidth_m": 30, "maxWidth_m": 150, "minDepth_m": 30, "maxDepth_m": 150, "minAreaSqm": 900, "maxAreaSqm": 22500, "aspectRatio": "1:1", "shape": "irregular", "suggestedAreaSqm": 5000},
  {"id": "memorial_garden", "suggestedWidth_m": 50, "suggestedDepth_m": 40, "minWidth_m": 20, "maxWidth_m": 100, "minDepth_m": 15, "maxDepth_m": 80, "minAreaSqm": 300, "maxAreaSqm": 8000, "aspectRatio": "1.25:1", "shape": "rectangular", "suggestedAreaSqm": 2000},

  // Ecological Resilience
  {"id": "urban_forest", "suggestedWidth_m": 250, "suggestedDepth_m": 200, "minWidth_m": 100, "maxWidth_m": 500, "minDepth_m": 80, "maxDepth_m": 400, "minAreaSqm": 8000, "maxAreaSqm": 200000, "aspectRatio": "1.25:1", "shape": "irregular", "suggestedAreaSqm": 50000},
  {"id": "riparian_buffer", "suggestedWidth_m": 200, "suggestedDepth_m": 50, "minWidth_m": 50, "maxWidth_m": 500, "minDepth_m": 15, "maxDepth_m": 100, "minAreaSqm": 750, "maxAreaSqm": 50000, "aspectRatio": "4:1", "shape": "linear", "suggestedAreaSqm": 10000},
  {"id": "wetland_rain_garden", "suggestedWidth_m": 80, "suggestedDepth_m": 60, "minWidth_m": 30, "maxWidth_m": 150, "minDepth_m": 20, "maxDepth_m": 120, "minAreaSqm": 600, "maxAreaSqm": 18000, "aspectRatio": "1.3:1", "shape": "organic", "suggestedAreaSqm": 5000},

  // Neighborhood Public Realm
  {"id": "playground_adventure", "suggestedWidth_m": 40, "suggestedDepth_m": 35, "minWidth_m": 20, "maxWidth_m": 80, "minDepth_m": 15, "maxDepth_m": 60, "minAreaSqm": 300, "maxAreaSqm": 4800, "aspectRatio": "1.15:1", "shape": "irregular", "suggestedAreaSqm": 1500},
  {"id": "splash_pad_area", "suggestedWidth_m": 30, "suggestedDepth_m": 25, "minWidth_m": 15, "maxWidth_m": 50, "minDepth_m": 12, "maxDepth_m": 40, "minAreaSqm": 180, "maxAreaSqm": 2000, "aspectRatio": "1.2:1", "shape": "circular", "suggestedAreaSqm": 800},

  // Social / Event Spaces
  {"id": "amphitheater_lawn", "suggestedWidth_m": 80, "suggestedDepth_m": 60, "minWidth_m": 40, "maxWidth_m": 150, "minDepth_m": 30, "maxDepth_m": 120, "minAreaSqm": 1200, "maxAreaSqm": 18000, "aspectRatio": "1.3:1", "shape": "semi-circular", "suggestedAreaSqm": 5000},
  {"id": "community_garden", "suggestedWidth_m": 50, "suggestedDepth_m": 50, "minWidth_m": 20, "maxWidth_m": 100, "minDepth_m": 20, "maxDepth_m": 100, "minAreaSqm": 400, "maxAreaSqm": 10000, "aspectRatio": "1:1", "shape": "rectangular", "suggestedAreaSqm": 2500},
  {"id": "cemetery_memorial_grounds", "suggestedWidth_m": 250, "suggestedDepth_m": 200, "minWidth_m": 100, "maxWidth_m": 500, "minDepth_m": 80, "maxDepth_m": 400, "minAreaSqm": 8000, "maxAreaSqm": 200000, "aspectRatio": "1.25:1", "shape": "rectangular", "suggestedAreaSqm": 50000},

  // Civic Plazas
  {"id": "formal_civic_plaza", "suggestedWidth_m": 80, "suggestedDepth_m": 75, "minWidth_m": 40, "maxWidth_m": 150, "minDepth_m": 35, "maxDepth_m": 140, "minAreaSqm": 1400, "maxAreaSqm": 21000, "aspectRatio": "1.07:1", "shape": "rectangular", "suggestedAreaSqm": 6000},
  {"id": "market_square", "suggestedWidth_m": 65, "suggestedDepth_m": 60, "minWidth_m": 30, "maxWidth_m": 120, "minDepth_m": 28, "maxDepth_m": 110, "minAreaSqm": 840, "maxAreaSqm": 13200, "aspectRatio": "1.08:1", "shape": "rectangular", "suggestedAreaSqm": 4000},
  {"id": "courtyard_plaza", "suggestedWidth_m": 35, "suggestedDepth_m": 35, "minWidth_m": 15, "maxWidth_m": 60, "minDepth_m": 15, "maxDepth_m": 60, "minAreaSqm": 225, "maxAreaSqm": 3600, "aspectRatio": "1:1", "shape": "rectangular", "suggestedAreaSqm": 1200},

  // Waterfront Spaces
  {"id": "promenade_boardwalk", "suggestedWidth_m": 300, "suggestedDepth_m": 20, "minWidth_m": 100, "maxWidth_m": 600, "minDepth_m": 8, "maxDepth_m": 40, "minAreaSqm": 800, "maxAreaSqm": 24000, "aspectRatio": "15:1", "shape": "linear", "suggestedAreaSqm": 6000},

  // Transit
  {"id": "transit_plaza", "suggestedWidth_m": 60, "suggestedDepth_m": 50, "minWidth_m": 25, "maxWidth_m": 100, "minDepth_m": 20, "maxDepth_m": 80, "minAreaSqm": 500, "maxAreaSqm": 8000, "aspectRatio": "1.2:1", "shape": "rectangular", "suggestedAreaSqm": 3000},
  {"id": "amphitheater_performance_space", "suggestedWidth_m": 50, "suggestedDepth_m": 40, "minWidth_m": 25, "maxWidth_m": 80, "minDepth_m": 20, "maxDepth_m": 65, "minAreaSqm": 500, "maxAreaSqm": 5200, "aspectRatio": "1.25:1", "shape": "semi-circular"},

  // Parking Areas
  {"id": "surface_parking_lot", "suggestedWidth_m": 50, "suggestedDepth_m": 40, "minWidth_m": 25, "maxWidth_m": 100, "minDepth_m": 20, "maxDepth_m": 80, "minAreaSqm": 500, "maxAreaSqm": 8000, "aspectRatio": "1.25:1", "shape": "rectangular"},
  {"id": "structured_parking_garage", "suggestedWidth_m": 50, "suggestedDepth_m": 20, "minWidth_m": 30, "maxWidth_m": 80, "minDepth_m": 15, "maxDepth_m": 30, "minAreaSqm": 450, "maxAreaSqm": 2400, "aspectRatio": "2.5:1", "shape": "rectangular"},
  {"id": "underground_parking_entry", "suggestedWidth_m": 20, "suggestedDepth_m": 20, "minWidth_m": 10, "maxWidth_m": 35, "minDepth_m": 10, "maxDepth_m": 35, "minAreaSqm": 100, "maxAreaSqm": 1225, "aspectRatio": "1:1", "shape": "rectangular", "suggestedAreaSqm": 400},
  {"id": "green_parking_lot", "suggestedWidth_m": 40, "suggestedDepth_m": 30, "minWidth_m": 20, "maxWidth_m": 70, "minDepth_m": 15, "maxDepth_m": 50, "minAreaSqm": 300, "maxAreaSqm": 3500, "aspectRatio": "1.3:1", "shape": "rectangular", "suggestedAreaSqm": 1200},

  // Water Features
  {"id": "pond_lake", "suggestedWidth_m": 80, "suggestedDepth_m": 60, "minWidth_m": 20, "maxWidth_m": 200, "minDepth_m": 15, "maxDepth_m": 150, "minAreaSqm": 300, "maxAreaSqm": 30000, "aspectRatio": "1.3:1", "shape": "organic"},
  {"id": "fountain_water_feature", "suggestedWidth_m": 20, "suggestedDepth_m": 20, "minWidth_m": 5, "maxWidth_m": 50, "minDepth_m": 5, "maxDepth_m": 50, "minAreaSqm": 25, "maxAreaSqm": 2500, "aspectRatio": "1:1", "shape": "circular", "suggestedAreaSqm": 400},
  {"id": "stormwater_retention_pond", "suggestedWidth_m": 60, "suggestedDepth_m": 40, "minWidth_m": 20, "maxWidth_m": 120, "minDepth_m": 15, "maxDepth_m": 80, "minAreaSqm": 300, "maxAreaSqm": 9600, "aspectRatio": "1.5:1", "shape": "organic"},
  {"id": "swimming_pool_complex", "suggestedWidth_m": 60, "suggestedDepth_m": 40, "minWidth_m": 25, "maxWidth_m": 100, "minDepth_m": 20, "maxDepth_m": 70, "minAreaSqm": 500, "maxAreaSqm": 7000, "aspectRatio": "1.5:1", "shape": "rectangular"},
  {"id": "canal_waterway", "suggestedWidth_m": 200, "suggestedDepth_m": 25, "minWidth_m": 50, "maxWidth_m": 500, "minDepth_m": 10, "maxDepth_m": 50, "minAreaSqm": 500, "maxAreaSqm": 25000, "aspectRatio": "8:1", "shape": "linear", "suggestedAreaSqm": 5000},

  // Custom
  {"id": "custom_parks_plazas", "suggestedWidth_m": 50, "suggestedDepth_m": 50, "minWidth_m": 10, "maxWidth_m": 200, "minDepth_m": 10, "maxDepth_m": 200, "minAreaSqm": 100, "maxAreaSqm": 40000, "aspectRatio": "1:1", "shape": "rectangular", "suggestedAreaSqm": 5000},

  // Extended Parks
  {"id": "linear_park_greenway", "suggestedWidth_m": 400, "suggestedDepth_m": 30, "minWidth_m": 100, "maxWidth_m": 1000, "minDepth_m": 15, "maxDepth_m": 60, "minAreaSqm": 1500, "maxAreaSqm": 60000, "aspectRatio": "13:1", "shape": "linear", "suggestedAreaSqm": 12000},
  {"id": "nature_preserve", "suggestedWidth_m": 400, "suggestedDepth_m": 250, "minWidth_m": 150, "maxWidth_m": 800, "minDepth_m": 100, "maxDepth_m": 500, "minAreaSqm": 15000, "maxAreaSqm": 400000, "aspectRatio": "1.6:1", "shape": "irregular", "suggestedAreaSqm": 100000},
  {"id": "rooftop_garden", "suggestedWidth_m": 25, "suggestedDepth_m": 20, "minWidth_m": 10, "maxWidth_m": 50, "minDepth_m": 8, "maxDepth_m": 40, "minAreaSqm": 80, "maxAreaSqm": 2000, "aspectRatio": "1.25:1", "shape": "rectangular", "suggestedAreaSqm": 500},
  {"id": "riverfront_park_beach", "suggestedWidth_m": 200, "suggestedDepth_m": 75, "minWidth_m": 80, "maxWidth_m": 400, "minDepth_m": 30, "maxDepth_m": 150, "minAreaSqm": 2400, "maxAreaSqm": 60000, "aspectRatio": "2.7:1", "shape": "linear", "suggestedAreaSqm": 15000},
  {"id": "street_plaza_parklet", "suggestedWidth_m": 10, "suggestedDepth_m": 6, "minWidth_m": 5, "maxWidth_m": 20, "minDepth_m": 3, "maxDepth_m": 12, "minAreaSqm": 15, "maxAreaSqm": 240, "aspectRatio": "1.7:1", "shape": "rectangular", "suggestedAreaSqm": 60},
  {"id": "community_garden_enhanced", "suggestedWidth_m": 60, "suggestedDepth_m": 50, "minWidth_m": 25, "maxWidth_m": 120, "minDepth_m": 20, "maxDepth_m": 100, "minAreaSqm": 500, "maxAreaSqm": 12000, "aspectRatio": "1.2:1", "shape": "rectangular", "suggestedAreaSqm": 3000},

  // City-specific parks — Paris
  {"id": "parisian_place", "suggestedWidth_m": 120, "suggestedDepth_m": 80, "minWidth_m": 50, "maxWidth_m": 250, "minDepth_m": 35, "maxDepth_m": 170, "minAreaSqm": 1750, "maxAreaSqm": 42500, "aspectRatio": "1.5:1", "shape": "rectangular", "suggestedAreaSqm": 10000},
  {"id": "parisian_square", "suggestedWidth_m": 80, "suggestedDepth_m": 60, "minWidth_m": 30, "maxWidth_m": 150, "minDepth_m": 25, "maxDepth_m": 110, "minAreaSqm": 750, "maxAreaSqm": 16500, "aspectRatio": "1.3:1", "shape": "rectangular", "suggestedAreaSqm": 5000},
  {"id": "parisian_jardin", "suggestedWidth_m": 180, "suggestedDepth_m": 140, "minWidth_m": 80, "maxWidth_m": 350, "minDepth_m": 60, "maxDepth_m": 270, "minAreaSqm": 4800, "maxAreaSqm": 94500, "aspectRatio": "1.3:1", "shape": "irregular", "suggestedAreaSqm": 25000},

  // City-specific parks — Amsterdam
  {"id": "amsterdam_vondelpark", "suggestedWidth_m": 250, "suggestedDepth_m": 160, "minWidth_m": 100, "maxWidth_m": 500, "minDepth_m": 70, "maxDepth_m": 300, "minAreaSqm": 7000, "maxAreaSqm": 150000, "aspectRatio": "1.6:1", "shape": "irregular", "suggestedAreaSqm": 40000},
  {"id": "amsterdam_hofje_garden", "suggestedWidth_m": 25, "suggestedDepth_m": 25, "minWidth_m": 10, "maxWidth_m": 50, "minDepth_m": 10, "maxDepth_m": 50, "minAreaSqm": 100, "maxAreaSqm": 2500, "aspectRatio": "1:1", "shape": "rectangular", "suggestedAreaSqm": 600},
  {"id": "amsterdam_plein", "suggestedWidth_m": 70, "suggestedDepth_m": 55, "minWidth_m": 30, "maxWidth_m": 120, "minDepth_m": 25, "maxDepth_m": 100, "minAreaSqm": 750, "maxAreaSqm": 12000, "aspectRatio": "1.3:1", "shape": "rectangular", "suggestedAreaSqm": 4000},

  // City-specific parks — Barcelona
  {"id": "barcelona_pati_interior", "suggestedWidth_m": 50, "suggestedDepth_m": 40, "minWidth_m": 20, "maxWidth_m": 80, "minDepth_m": 15, "maxDepth_m": 65, "minAreaSqm": 300, "maxAreaSqm": 5200, "aspectRatio": "1.25:1", "shape": "rectangular", "suggestedAreaSqm": 2000},
  {"id": "barcelona_placa_xamfra", "suggestedWidth_m": 30, "suggestedDepth_m": 28, "minWidth_m": 15, "maxWidth_m": 50, "minDepth_m": 14, "maxDepth_m": 45, "minAreaSqm": 210, "maxAreaSqm": 2250, "aspectRatio": "1.07:1", "shape": "octagonal", "suggestedAreaSqm": 800},
  {"id": "barcelona_superilla", "suggestedWidth_m": 130, "suggestedDepth_m": 130, "minWidth_m": 80, "maxWidth_m": 200, "minDepth_m": 80, "maxDepth_m": 200, "minAreaSqm": 6400, "maxAreaSqm": 40000, "aspectRatio": "1:1", "shape": "square", "suggestedAreaSqm": 16000},

  // City-specific parks — London
  {"id": "london_garden_square", "suggestedWidth_m": 100, "suggestedDepth_m": 80, "minWidth_m": 40, "maxWidth_m": 200, "minDepth_m": 30, "maxDepth_m": 160, "minAreaSqm": 1200, "maxAreaSqm": 32000, "aspectRatio": "1.25:1", "shape": "rectangular", "suggestedAreaSqm": 8000},
  {"id": "london_circus", "suggestedWidth_m": 80, "suggestedDepth_m": 80, "minWidth_m": 30, "maxWidth_m": 150, "minDepth_m": 30, "maxDepth_m": 150, "minAreaSqm": 900, "maxAreaSqm": 22500, "aspectRatio": "1:1", "shape": "circular", "suggestedAreaSqm": 5000},

  // City-specific parks — New York
  {"id": "newyork_pocket_park", "suggestedWidth_m": 18, "suggestedDepth_m": 18, "minWidth_m": 8, "maxWidth_m": 30, "minDepth_m": 8, "maxDepth_m": 30, "minAreaSqm": 64, "maxAreaSqm": 900, "aspectRatio": "1:1", "shape": "rectangular", "suggestedAreaSqm": 350},
  {"id": "newyork_community_garden", "suggestedWidth_m": 30, "suggestedDepth_m": 25, "minWidth_m": 12, "maxWidth_m": 50, "minDepth_m": 10, "maxDepth_m": 45, "minAreaSqm": 120, "maxAreaSqm": 2250, "aspectRatio": "1.2:1", "shape": "rectangular", "suggestedAreaSqm": 800},

  // City-specific parks — Montreal
  {"id": "montreal_mount_royal", "suggestedWidth_m": 500, "suggestedDepth_m": 400, "minWidth_m": 200, "maxWidth_m": 800, "minDepth_m": 150, "maxDepth_m": 650, "minAreaSqm": 30000, "maxAreaSqm": 520000, "aspectRatio": "1.25:1", "shape": "irregular"},
  {"id": "montreal_square", "suggestedWidth_m": 70, "suggestedDepth_m": 55, "minWidth_m": 30, "maxWidth_m": 120, "minDepth_m": 25, "maxDepth_m": 100, "minAreaSqm": 750, "maxAreaSqm": 12000, "aspectRatio": "1.27:1", "shape": "rectangular", "suggestedAreaSqm": 4000},

  // City-specific parks — Vancouver
  {"id": "vancouver_seawall", "suggestedWidth_m": 300, "suggestedDepth_m": 25, "minWidth_m": 100, "maxWidth_m": 600, "minDepth_m": 10, "maxDepth_m": 50, "minAreaSqm": 1000, "maxAreaSqm": 30000, "aspectRatio": "12:1", "shape": "linear", "suggestedAreaSqm": 8000},
  {"id": "vancouver_beach_park", "suggestedWidth_m": 150, "suggestedDepth_m": 80, "minWidth_m": 60, "maxWidth_m": 300, "minDepth_m": 30, "maxDepth_m": 150, "minAreaSqm": 1800, "maxAreaSqm": 45000, "aspectRatio": "1.9:1", "shape": "irregular"},

  // City-specific parks — Toronto
  {"id": "toronto_ravine", "suggestedWidth_m": 300, "suggestedDepth_m": 100, "minWidth_m": 100, "maxWidth_m": 600, "minDepth_m": 40, "maxDepth_m": 200, "minAreaSqm": 4000, "maxAreaSqm": 120000, "aspectRatio": "3:1", "shape": "linear"},
  {"id": "toronto_urban_square", "suggestedWidth_m": 80, "suggestedDepth_m": 60, "minWidth_m": 30, "maxWidth_m": 150, "minDepth_m": 25, "maxDepth_m": 110, "minAreaSqm": 750, "maxAreaSqm": 16500, "aspectRatio": "1.3:1", "shape": "rectangular", "suggestedAreaSqm": 5000},

  // City-specific parks — Calgary
  {"id": "calgary_princes_island", "suggestedWidth_m": 400, "suggestedDepth_m": 200, "minWidth_m": 150, "maxWidth_m": 700, "minDepth_m": 80, "maxDepth_m": 350, "minAreaSqm": 12000, "maxAreaSqm": 245000, "aspectRatio": "2:1", "shape": "irregular"},
  {"id": "calgary_prairie_plaza", "suggestedWidth_m": 70, "suggestedDepth_m": 55, "minWidth_m": 30, "maxWidth_m": 120, "minDepth_m": 25, "maxDepth_m": 100, "minAreaSqm": 750, "maxAreaSqm": 12000, "aspectRatio": "1.27:1", "shape": "rectangular", "suggestedAreaSqm": 4000},

  // City-specific parks — Halifax
  {"id": "halifax_public_gardens", "suggestedWidth_m": 200, "suggestedDepth_m": 150, "minWidth_m": 80, "maxWidth_m": 350, "minDepth_m": 60, "maxDepth_m": 260, "minAreaSqm": 4800, "maxAreaSqm": 91000, "aspectRatio": "1.3:1", "shape": "rectangular"},
  {"id": "halifax_coastal_park", "suggestedWidth_m": 250, "suggestedDepth_m": 100, "minWidth_m": 80, "maxWidth_m": 500, "minDepth_m": 40, "maxDepth_m": 200, "minAreaSqm": 3200, "maxAreaSqm": 100000, "aspectRatio": "2.5:1", "shape": "irregular"},

  // Sports courts (CORRECTED entries marked)
  // CORRECTED: basketball_court was 20x35, validated to 32x19
  {"id": "basketball_court", "suggestedWidth_m": 32, "suggestedDepth_m": 19, "minWidth_m": 26, "maxWidth_m": 40, "minDepth_m": 15, "maxDepth_m": 24, "minAreaSqm": 390, "maxAreaSqm": 960, "aspectRatio": "1.7:1", "shape": "rectangular"},
  {"id": "pickleball_courts", "suggestedWidth_m": 20, "suggestedDepth_m": 14, "minWidth_m": 10, "maxWidth_m": 40, "minDepth_m": 7, "maxDepth_m": 28, "minAreaSqm": 70, "maxAreaSqm": 1120, "aspectRatio": "1.4:1", "shape": "rectangular"},
  {"id": "soccer_pitch_caged", "suggestedWidth_m": 105, "suggestedDepth_m": 68, "minWidth_m": 45, "maxWidth_m": 120, "minDepth_m": 30, "maxDepth_m": 90, "minAreaSqm": 1350, "maxAreaSqm": 10800, "aspectRatio": "1.5:1", "shape": "rectangular"},
  // CORRECTED: running_track_oval was 120x150, validated to 177x93
  {"id": "running_track_oval", "suggestedWidth_m": 177, "suggestedDepth_m": 93, "minWidth_m": 140, "maxWidth_m": 200, "minDepth_m": 75, "maxDepth_m": 110, "minAreaSqm": 10500, "maxAreaSqm": 22000, "aspectRatio": "1.9:1", "shape": "oval"},
  {"id": "outdoor_fitness_circuit", "suggestedWidth_m": 30, "suggestedDepth_m": 25, "minWidth_m": 15, "maxWidth_m": 60, "minDepth_m": 12, "maxDepth_m": 50, "minAreaSqm": 180, "maxAreaSqm": 3000, "aspectRatio": "1.2:1", "shape": "irregular"},
  {"id": "baseball_softball_diamond", "suggestedWidth_m": 120, "suggestedDepth_m": 120, "minWidth_m": 60, "maxWidth_m": 150, "minDepth_m": 60, "maxDepth_m": 150, "minAreaSqm": 3600, "maxAreaSqm": 22500, "aspectRatio": "1:1", "shape": "diamond"},
  {"id": "cricket_pitch_oval", "suggestedWidth_m": 150, "suggestedDepth_m": 140, "minWidth_m": 100, "maxWidth_m": 180, "minDepth_m": 90, "maxDepth_m": 170, "minAreaSqm": 9000, "maxAreaSqm": 30600, "aspectRatio": "1.07:1", "shape": "oval"},
  {"id": "disc_golf_course", "suggestedWidth_m": 300, "suggestedDepth_m": 200, "minWidth_m": 150, "maxWidth_m": 500, "minDepth_m": 100, "maxDepth_m": 350, "minAreaSqm": 15000, "maxAreaSqm": 175000, "aspectRatio": "1.5:1", "shape": "irregular"},
  // CORRECTED: bocce_petanque_court was 15x40, validated to 28x16
  {"id": "bocce_petanque_court", "suggestedWidth_m": 28, "suggestedDepth_m": 16, "minWidth_m": 20, "maxWidth_m": 35, "minDepth_m": 12, "maxDepth_m": 20, "minAreaSqm": 240, "maxAreaSqm": 700, "aspectRatio": "1.75:1", "shape": "rectangular"},
  {"id": "climbing_bouldering_wall", "suggestedWidth_m": 25, "suggestedDepth_m": 20, "minWidth_m": 12, "maxWidth_m": 40, "minDepth_m": 10, "maxDepth_m": 35, "minAreaSqm": 120, "maxAreaSqm": 1400, "aspectRatio": "1.25:1", "shape": "rectangular"},
  {"id": "nature_play_area", "suggestedWidth_m": 40, "suggestedDepth_m": 30, "minWidth_m": 20, "maxWidth_m": 80, "minDepth_m": 15, "maxDepth_m": 60, "minAreaSqm": 300, "maxAreaSqm": 4800, "aspectRatio": "1.3:1", "shape": "organic"},
  {"id": "inclusive_playground", "suggestedWidth_m": 50, "suggestedDepth_m": 40, "minWidth_m": 25, "maxWidth_m": 80, "minDepth_m": 20, "maxDepth_m": 65, "minAreaSqm": 500, "maxAreaSqm": 5200, "aspectRatio": "1.25:1", "shape": "irregular"},
  {"id": "mini_golf_course", "suggestedWidth_m": 50, "suggestedDepth_m": 30, "minWidth_m": 25, "maxWidth_m": 80, "minDepth_m": 15, "maxDepth_m": 50, "minAreaSqm": 375, "maxAreaSqm": 4000, "aspectRatio": "1.7:1", "shape": "irregular"},
  {"id": "pollinator_meadow", "suggestedWidth_m": 80, "suggestedDepth_m": 60, "minWidth_m": 30, "maxWidth_m": 200, "minDepth_m": 20, "maxDepth_m": 150, "minAreaSqm": 600, "maxAreaSqm": 30000, "aspectRatio": "1.3:1", "shape": "organic"},
  {"id": "urban_orchard_food_forest", "suggestedWidth_m": 60, "suggestedDepth_m": 50, "minWidth_m": 25, "maxWidth_m": 120, "minDepth_m": 20, "maxDepth_m": 100, "minAreaSqm": 500, "maxAreaSqm": 12000, "aspectRatio": "1.2:1", "shape": "irregular"},
  {"id": "bioswale_rain_garden", "suggestedWidth_m": 60, "suggestedDepth_m": 15, "minWidth_m": 20, "maxWidth_m": 150, "minDepth_m": 5, "maxDepth_m": 30, "minAreaSqm": 100, "maxAreaSqm": 4500, "aspectRatio": "4:1", "shape": "linear"},
  {"id": "urban_beach", "suggestedWidth_m": 80, "suggestedDepth_m": 40, "minWidth_m": 30, "maxWidth_m": 150, "minDepth_m": 15, "maxDepth_m": 80, "minAreaSqm": 450, "maxAreaSqm": 12000, "aspectRatio": "2:1", "shape": "irregular"},
  {"id": "sculpture_garden", "suggestedWidth_m": 60, "suggestedDepth_m": 50, "minWidth_m": 25, "maxWidth_m": 120, "minDepth_m": 20, "maxDepth_m": 100, "minAreaSqm": 500, "maxAreaSqm": 12000, "aspectRatio": "1.2:1", "shape": "irregular"},
  {"id": "labyrinth_meditation", "suggestedWidth_m": 20, "suggestedDepth_m": 20, "minWidth_m": 10, "maxWidth_m": 35, "minDepth_m": 10, "maxDepth_m": 35, "minAreaSqm": 100, "maxAreaSqm": 1225, "aspectRatio": "1:1", "shape": "circular"},
  {"id": "festival_event_lawn", "suggestedWidth_m": 120, "suggestedDepth_m": 80, "minWidth_m": 50, "maxWidth_m": 250, "minDepth_m": 35, "maxDepth_m": 170, "minAreaSqm": 1750, "maxAreaSqm": 42500, "aspectRatio": "1.5:1", "shape": "rectangular"},
  {"id": "pump_track", "suggestedWidth_m": 50, "suggestedDepth_m": 30, "minWidth_m": 25, "maxWidth_m": 80, "minDepth_m": 15, "maxDepth_m": 50, "minAreaSqm": 375, "maxAreaSqm": 4000, "aspectRatio": "1.7:1", "shape": "loop"},
  {"id": "outdoor_ice_rink", "suggestedWidth_m": 60, "suggestedDepth_m": 30, "minWidth_m": 25, "maxWidth_m": 80, "minDepth_m": 15, "maxDepth_m": 50, "minAreaSqm": 375, "maxAreaSqm": 4000, "aspectRatio": "2:1", "shape": "rectangular"},
  {"id": "beach_volleyball_courts", "suggestedWidth_m": 24, "suggestedDepth_m": 16, "minWidth_m": 16, "maxWidth_m": 50, "minDepth_m": 10, "maxDepth_m": 32, "minAreaSqm": 160, "maxAreaSqm": 1600, "aspectRatio": "1.5:1", "shape": "rectangular"},
  {"id": "kayak_launch_dock", "suggestedWidth_m": 40, "suggestedDepth_m": 15, "minWidth_m": 15, "maxWidth_m": 80, "minDepth_m": 8, "maxDepth_m": 30, "minAreaSqm": 120, "maxAreaSqm": 2400, "aspectRatio": "2.7:1", "shape": "linear"},
];

// ── suggestedAreaSqm updates for parks that had undefined ──────────────────
const AREA_UPDATES = {
  "urban_pocket_park": 400,
  "neighborhood_park": 8000,
  "community_park": 40000,
  "regional_park": 200000,
  "dog_park": 4000,
  "botanical_garden": 30000,
  "japanese_garden": 5000,
  "memorial_garden": 2000,
  "urban_forest": 50000,
  "riparian_buffer": 10000,
  "wetland_rain_garden": 5000,
  "playground_adventure": 1500,
  "splash_pad_area": 800,
  "amphitheater_lawn": 5000,
  "community_garden": 2500,
  "cemetery_memorial_grounds": 50000,
  "formal_civic_plaza": 6000,
  "market_square": 4000,
  "courtyard_plaza": 1200,
  "promenade_boardwalk": 6000,
  "transit_plaza": 3000,
  "underground_parking_entry": 400,
  "green_parking_lot": 1200,
  "fountain_water_feature": 400,
  "canal_waterway": 5000,
  "custom_parks_plazas": 5000,
  "linear_park_greenway": 12000,
  "nature_preserve": 100000,
  "rooftop_garden": 500,
  "riverfront_park_beach": 15000,
  "street_plaza_parklet": 60,
  "community_garden_enhanced": 3000,
  "parisian_place": 10000,
  "parisian_square": 5000,
  "parisian_jardin": 25000,
  "amsterdam_vondelpark": 40000,
  "amsterdam_hofje_garden": 600,
  "amsterdam_plein": 4000,
  "barcelona_pati_interior": 2000,
  "barcelona_placa_xamfra": 800,
  "barcelona_superilla": 16000,
  "london_garden_square": 8000,
  "london_circus": 5000,
  "newyork_pocket_park": 350,
  "newyork_community_garden": 800,
  "montreal_square": 4000,
  "vancouver_seawall": 8000,
  "toronto_urban_square": 5000,
  "calgary_prairie_plaza": 4000,
};

// ── Apply dimensions to a JSON file (TEXT-LEVEL, no JSON.parse) ────────────
function applyDimensionsToFile(filePath, dimensions) {
  let content = readFileSync(filePath, 'utf8');
  let applied = 0;
  let notFound = 0;
  const notFoundIds = [];

  for (const dim of dimensions) {
    // Find the archetype entry by id
    const idPattern = new RegExp(`"id"\\s*:\\s*"${dim.id}"`);
    const match = idPattern.exec(content);
    if (!match) {
      console.error(`  NOT FOUND: ${dim.id}`);
      notFound++;
      notFoundIds.push(dim.id);
      continue;
    }

    // Check if dimensions already exist
    const afterId = content.substring(match.index);
    const nextBrace = afterId.indexOf('}');
    const entrySlice = afterId.substring(0, nextBrace);

    if (entrySlice.includes('"suggestedWidth_m"')) {
      console.log(`  SKIP (already has dims): ${dim.id}`);
      continue;
    }

    // Build the dimension fields to add
    const dimFields = [];
    if (dim.suggestedWidth_m !== undefined) dimFields.push(`"suggestedWidth_m": ${dim.suggestedWidth_m}`);
    if (dim.suggestedDepth_m !== undefined) dimFields.push(`"suggestedDepth_m": ${dim.suggestedDepth_m}`);
    if (dim.minWidth_m !== undefined) dimFields.push(`"minWidth_m": ${dim.minWidth_m}`);
    if (dim.maxWidth_m !== undefined) dimFields.push(`"maxWidth_m": ${dim.maxWidth_m}`);
    if (dim.minDepth_m !== undefined) dimFields.push(`"minDepth_m": ${dim.minDepth_m}`);
    if (dim.maxDepth_m !== undefined) dimFields.push(`"maxDepth_m": ${dim.maxDepth_m}`);
    if (dim.minAreaSqm !== undefined) dimFields.push(`"minAreaSqm": ${dim.minAreaSqm}`);
    if (dim.maxAreaSqm !== undefined) dimFields.push(`"maxAreaSqm": ${dim.maxAreaSqm}`);
    if (dim.aspectRatio !== undefined) dimFields.push(`"aspectRatio": "${dim.aspectRatio}"`);
    if (dim.shape !== undefined) dimFields.push(`"shape": "${dim.shape}"`);

    // Find the right insertion point — after "id": "..." line
    const insertionStr = `"id": "${dim.id}"`;
    const insertIdx = content.indexOf(insertionStr);
    if (insertIdx < 0) {
      console.error(`  INSERT FAILED: ${dim.id}`);
      notFound++;
      notFoundIds.push(dim.id);
      continue;
    }

    // Find the end of the "id" value line (after the closing quote and comma)
    const afterInsert = content.substring(insertIdx + insertionStr.length);
    const commaIdx = afterInsert.indexOf(',');
    if (commaIdx < 0) {
      console.error(`  NO COMMA AFTER ID: ${dim.id}`);
      notFound++;
      notFoundIds.push(dim.id);
      continue;
    }

    const insertPoint = insertIdx + insertionStr.length + commaIdx + 1;

    // Detect indentation — look at the "id" line to determine indent level
    const lineStart = content.lastIndexOf('\n', insertIdx) + 1;
    const lineContent = content.substring(lineStart, insertIdx);
    const indent = lineContent.match(/^(\s*)/)[1];

    const dimStr = '\n' + indent + dimFields.join(',\n' + indent) + ',';
    content = content.substring(0, insertPoint) + dimStr + content.substring(insertPoint);

    applied++;
    console.log(`  APPLIED: ${dim.id}`);
  }

  writeFileSync(filePath, content);
  console.log(`\nApplied ${applied} dimension sets, ${notFound} not found`);
  if (notFoundIds.length > 0) {
    console.log('Not found IDs:', notFoundIds.join(', '));
  }
  return content;
}

// ── Apply suggestedAreaSqm updates ─────────────────────────────────────────
function applySuggestedAreaUpdates(filePath, areaUpdates) {
  let content = readFileSync(filePath, 'utf8');
  let updated = 0;
  let alreadyHas = 0;
  let notFound = 0;

  for (const [id, area] of Object.entries(areaUpdates)) {
    // Find the archetype entry by id (only match top-level archetypes, not variants)
    const insertionStr = `"id": "${id}"`;
    const insertIdx = content.indexOf(insertionStr);
    if (insertIdx < 0) {
      console.error(`  AREA NOT FOUND: ${id}`);
      notFound++;
      continue;
    }

    // Check if this archetype already has suggestedAreaSqm within its block
    // Look from the id forward to the next archetype entry (next "id":)
    const afterId = content.substring(insertIdx + insertionStr.length);

    // Find the extent of this archetype object — look for the pattern that starts the next archetype
    // We search for the next top-level "id": that's at the same indentation
    const lineStart = content.lastIndexOf('\n', insertIdx) + 1;
    const lineContent = content.substring(lineStart, insertIdx);
    const indent = lineContent.match(/^(\s*)/)[1];

    // Look for suggestedAreaSqm at the same indent level within a reasonable range
    // Search up to 2000 chars ahead (well within one archetype block)
    const searchWindow = afterId.substring(0, 2000);

    if (searchWindow.includes('"suggestedAreaSqm"')) {
      console.log(`  AREA SKIP (already has): ${id}`);
      alreadyHas++;
      continue;
    }

    // Insert suggestedAreaSqm before the first "variants" or "renderPrompt" key
    // Find a good insertion point — before "thumbnailUrl" or "variants" or "renderPrompt"
    const thumbIdx = afterId.indexOf('"thumbnailUrl"');
    const variantsIdx = afterId.indexOf('"variants"');
    const renderIdx = afterId.indexOf('"renderPrompt"');

    // Pick the earliest one found
    let targetIdx = Infinity;
    if (thumbIdx > 0 && thumbIdx < targetIdx) targetIdx = thumbIdx;
    if (variantsIdx > 0 && variantsIdx < targetIdx) targetIdx = variantsIdx;
    if (renderIdx > 0 && renderIdx < targetIdx) targetIdx = renderIdx;

    if (targetIdx === Infinity) {
      console.error(`  AREA INSERT FAILED (no anchor): ${id}`);
      notFound++;
      continue;
    }

    // Insert before that line — go back to the start of the line
    const beforeTarget = afterId.substring(0, targetIdx);
    const lastNewline = beforeTarget.lastIndexOf('\n');
    const insertAt = insertIdx + insertionStr.length + lastNewline + 1;

    const areaLine = `${indent}"suggestedAreaSqm": ${area},\n`;
    content = content.substring(0, insertAt) + areaLine + content.substring(insertAt);

    updated++;
    console.log(`  AREA APPLIED: ${id} = ${area}`);
  }

  writeFileSync(filePath, content);
  console.log(`\nArea updates: ${updated} applied, ${alreadyHas} already had value, ${notFound} not found`);
}

// ── MAIN ────────────────────────────────────────────────────────────────────
const FILE = 'C:/Users/andre/OneDrive/Documents/Playground/frontend/src/data/openSpaceArchetypes.json';

console.log('=== Applying PARK dimensions ===');
applyDimensionsToFile(FILE, PARK_DIMS);

console.log('\n=== Applying suggestedAreaSqm updates ===');
applySuggestedAreaUpdates(FILE, AREA_UPDATES);

console.log('\nDone! Park dimensions applied to openSpaceArchetypes.json');
