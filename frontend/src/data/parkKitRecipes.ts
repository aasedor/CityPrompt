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

const NEIGHBORHOOD_PARK: ParkKitRecipe = {
  trees: { perHectare: 40, edgeBias: 0.7, bandDepth_m: 10, minSpacing_m: 6, scaleJitter: [0.8, 1.2] },
  benches: { areaPerBench_m2: 2000, min: 2, max: 8, edgeInset_m: 2 },
  playground: { minArea_m2: 3000, clusterRadius_m: 6, instances: 3, clearance_m: 10 },
  pavilion: { minArea_m2: 8000, clusterRadius_m: 0, instances: 1, clearance_m: 8 },
};

const URBAN_POCKET_PARK: ParkKitRecipe = {
  trees: { perHectare: 60, edgeBias: 0.8, bandDepth_m: 6, minSpacing_m: 5, scaleJitter: [0.8, 1.15] },
  benches: { areaPerBench_m2: 800, min: 2, max: 4, edgeInset_m: 1.5 },
};

const DEFAULT_RECIPE: ParkKitRecipe = {
  trees: { perHectare: 30, edgeBias: 0.6, bandDepth_m: 10, minSpacing_m: 6, scaleJitter: [0.8, 1.2] },
};

const RECIPES: Record<string, ParkKitRecipe> = {
  neighborhood_park: NEIGHBORHOOD_PARK,
  urban_pocket_park: URBAN_POCKET_PARK,
  community_park: NEIGHBORHOOD_PARK,
  default: DEFAULT_RECIPE,
};

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
