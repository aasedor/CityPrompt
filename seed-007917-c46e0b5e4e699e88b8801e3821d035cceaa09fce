/**
 * Placement recipes for park kits — the "expand/contract with geography"
 * rules. A bigger park gets MORE trees/benches, never bigger ones; features
 * gate on real area thresholds. Metric prop dimensions live in
 * archetypeMetadataSchema (PARK_FURNITURE / PLAYGROUND_EQUIPMENT).
 *
 * Kept as a TS module (not openSpaceArchetypes.json): these are runtime
 * geometry config with types and area functions, not AI prompt text.
 */

export interface TreeRule {
  perHectare: number;
  /** share of trees placed in the perimeter band (0..1) */
  edgeBias: number;
  /** perimeter band depth: trees sit inset 2..bandDepth_m from the edge */
  bandDepth_m: number;
  minSpacing_m: number;
  scaleJitter: [number, number];
}

export interface BenchRule {
  areaPerBench_m2: number;
  min: number;
  max: number;
  edgeInset_m: number;
}

export interface ClusterRule {
  minArea_m2: number;
  clusterRadius_m: number;
  instances: number;
  /** trees are rejected within this radius of the cluster center */
  clearance_m: number;
}

export interface ParkKitRecipe {
  trees: TreeRule;
  benches?: BenchRule;
  playground?: ClusterRule;
  pavilion?: ClusterRule;
}

export const NEIGHBORHOOD_PARK: ParkKitRecipe = {
  trees: { perHectare: 40, edgeBias: 0.7, bandDepth_m: 10, minSpacing_m: 6, scaleJitter: [0.8, 1.2] },
  benches: { areaPerBench_m2: 2000, min: 2, max: 8, edgeInset_m: 2 },
  playground: { minArea_m2: 3000, clusterRadius_m: 6, instances: 3, clearance_m: 10 },
  pavilion: { minArea_m2: 8000, clusterRadius_m: 0, instances: 1, clearance_m: 8 },
};

export const URBAN_POCKET_PARK: ParkKitRecipe = {
  // A compact downtown park needs a continuous mature canopy frame to read
  // against surrounding mid-rise massing. 125/ha yields roughly 16 trees on
  // a 0.13 ha court and 25-30 on a larger 0.2-0.25 ha pocket park, while the
  // edge bias and spacing keep the central lawn usable and visible.
  trees: { perHectare: 125, edgeBias: 0.88, bandDepth_m: 7, minSpacing_m: 4.2, scaleJitter: [0.95, 1.35] },
  benches: { areaPerBench_m2: 800, min: 2, max: 4, edgeInset_m: 1.5 },
};

/** Planner greenways are circulation-first. Their path is authored in the
 * ground drape; only restrained edge planting and occasional seating anchors
 * are eligible for the later finishing pass. */
export const LINEAR_GREENWAY: ParkKitRecipe = {
  trees: { perHectare: 24, edgeBias: 1, bandDepth_m: 7, minSpacing_m: 8, scaleJitter: [0.78, 1.08] },
  benches: { areaPerBench_m2: 2800, min: 1, max: 8, edgeInset_m: 2.5 },
};

/** Engineered stormwater landscapes must remain operationally clear. */
export const STORMWATER_POND: ParkKitRecipe = {
  trees: { perHectare: 8, edgeBias: 1, bandDepth_m: 6, minSpacing_m: 10, scaleJitter: [0.72, 1] },
};

/** Playground-titled archetypes are equipment-first: low area gate, bigger
 *  cluster, generous clearance, light tree cover for shade only. */
export const PLAYGROUND_PARK: ParkKitRecipe = {
  trees: { perHectare: 20, edgeBias: 0.8, bandDepth_m: 8, minSpacing_m: 6, scaleJitter: [0.8, 1.2] },
  benches: { areaPerBench_m2: 600, min: 2, max: 6, edgeInset_m: 1.5 },
  playground: { minArea_m2: 800, clusterRadius_m: 8, instances: 4, clearance_m: 12 },
};

/** Civic plazas stay predominantly paved and open: one restrained tree row
 * and frequent seating provide scale without turning hardscape into a park. */
export const PAVED_PLAZA: ParkKitRecipe = {
  trees: { perHectare: 14, edgeBias: 1, bandDepth_m: 5, minSpacing_m: 9, scaleJitter: [0.85, 1.05] },
  benches: { areaPerBench_m2: 1000, min: 2, max: 10, edgeInset_m: 2 },
};

/** Pilot: specimen-scale trees and restrained seating around a garden whose
 * pond / gravel / bridge program is carried by the shared ground diagram. */
export const JAPANESE_GARDEN: ParkKitRecipe = {
  trees: { perHectare: 34, edgeBias: 0.45, bandDepth_m: 9, minSpacing_m: 7, scaleJitter: [0.72, 1.08] },
  benches: { areaPerBench_m2: 1800, min: 2, max: 6, edgeInset_m: 2.2 },
};

/** Pilot: playing surfaces remain clear; a light perimeter tree/bench frame
 * gives the complex scale without contaminating field safety areas. */
export const SPORTS_FIELD_COMPLEX: ParkKitRecipe = {
  trees: { perHectare: 8, edgeBias: 1, bandDepth_m: 7, minSpacing_m: 12, scaleJitter: [0.7, 0.95] },
  benches: { areaPerBench_m2: 3500, min: 2, max: 8, edgeInset_m: 2.5 },
};

/** Dense native woodland: trees are the dominant spatial structure, with
 * only a narrow trail and a couple of small daylight clearings. */
export const URBAN_FOREST: ParkKitRecipe = {
  trees: { perHectare: 150, edgeBias: 0.35, bandDepth_m: 14, minSpacing_m: 4.5, scaleJitter: [0.75, 1.35] },
  benches: { areaPerBench_m2: 4500, min: 1, max: 4, edgeInset_m: 3 },
};

/** Curated specimen collection: high species variety and distributed canopy,
 * while formal beds, conservatory pad and interpretive paths remain clear. */
export const BOTANICAL_GARDEN: ParkKitRecipe = {
  trees: { perHectare: 72, edgeBias: 0.42, bandDepth_m: 12, minSpacing_m: 5.5, scaleJitter: [0.65, 1.3] },
  benches: { areaPerBench_m2: 1400, min: 3, max: 10, edgeInset_m: 2 },
  pavilion: { minArea_m2: 6000, clusterRadius_m: 0, instances: 1, clearance_m: 10 },
};

/** Nature play relies on landform, logs, stone and planting rather than a
 * generic plastic equipment scatter. The authored ground keeps two safe play
 * rooms and their connecting loop clear for the final render. */
export const NATURE_PLAY_AREA: ParkKitRecipe = {
  trees: { perHectare: 48, edgeBias: 0.68, bandDepth_m: 10, minSpacing_m: 6, scaleJitter: [0.75, 1.2] },
  benches: { areaPerBench_m2: 1200, min: 3, max: 8, edgeInset_m: 2 },
  playground: { minArea_m2: 1200, clusterRadius_m: 9, instances: 4, clearance_m: 13 },
};

/** Small urban reservoir variant: the water, perimeter loop and dam are
 * carried by the authored ground plane. Standing props stay sparse and hug
 * the outer upland/trail edge so no generic tree scatter lands in the lake. */
export const RESERVOIR_WATERSHED_PARK: ParkKitRecipe = {
  trees: { perHectare: 18, edgeBias: 1, bandDepth_m: 6, minSpacing_m: 8, scaleJitter: [0.75, 1.05] },
  benches: { areaPerBench_m2: 2200, min: 3, max: 8, edgeInset_m: 4 },
};

const DEFAULT_RECIPE: ParkKitRecipe = {
  trees: { perHectare: 30, edgeBias: 0.6, bandDepth_m: 10, minSpacing_m: 6, scaleJitter: [0.8, 1.2] },
};

/** Substring-matched in insertion order — keep more-specific keys first
 *  (`playground` must beat any park-generic key; `urban_pocket_park` and
 *  `pocket_park` land on the same recipe so their order is immaterial). */
const RECIPES: Record<string, ParkKitRecipe> = {
  playground: PLAYGROUND_PARK,
  reservoir_watershed_park: RESERVOIR_WATERSHED_PARK,
  stormwater_retention_pond: STORMWATER_POND,
  linear_park_greenway: LINEAR_GREENWAY,
  fountain_water_feature: PAVED_PLAZA,
  formal_civic_plaza: PAVED_PLAZA,
  japanese_garden: JAPANESE_GARDEN,
  sports_field_complex: SPORTS_FIELD_COMPLEX,
  urban_forest: URBAN_FOREST,
  botanical_garden: BOTANICAL_GARDEN,
  nature_play_area: NATURE_PLAY_AREA,
  neighborhood_park: NEIGHBORHOOD_PARK,
  urban_pocket_park: URBAN_POCKET_PARK,
  pocket_park: URBAN_POCKET_PARK,
  community_park: NEIGHBORHOOD_PARK,
  regional_park: NEIGHBORHOOD_PARK,
  olmsted: NEIGHBORHOOD_PARK,
  default: DEFAULT_RECIPE,
};

/** True when the id resolved to a real recipe (not the trees-only default) —
 *  lets zone-level fallbacks distinguish "matched" from "fell through". */
export function isDefaultParkRecipe(recipe: ParkKitRecipe): boolean {
  return recipe === DEFAULT_RECIPE;
}

/** Resolve a recipe from a green-space archetype id (tolerant of prefixes,
 *  hyphens, and legacy suffixes). */
export function resolveParkRecipe(archetypeId: string | undefined | null): ParkKitRecipe {
  if (!archetypeId) return RECIPES.default;
  const normalized = String(archetypeId).toLowerCase().replace(/-/g, '_');
  for (const key of Object.keys(RECIPES)) {
    if (key !== 'default' && normalized.includes(key)) return RECIPES[key];
  }
  return RECIPES.default;
}
