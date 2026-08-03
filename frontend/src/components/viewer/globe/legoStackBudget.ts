/**
 * Bound the number of fully detailed LEGO stacks mounted at once.
 *
 * The original pilot limit of 20 hid valid compiled buildings in ordinary
 * community plans. Ninety-six covers every currently supported building in
 * the mixed-plan QA scene while retaining a guard until district-scale
 * instancing is introduced.
 */
export const LEGO_STACK_RENDER_BUDGET = 96;

/**
 * Admit every distinct family that fits within the ordinary stack budget.
 * A lower family-only cap made otherwise valid buildings persist as grey
 * massing proxies whenever a plan used more than two archetypes. The global
 * stack guard and WebGL context recovery remain the safety boundaries.
 */
export const LEGO_DISTINCT_FAMILY_RENDER_BUDGET = LEGO_STACK_RENDER_BUDGET;

export interface LegoStackLodSelection<T> {
  detailed: T[];
  simplified: T[];
}

/**
 * Keep the nearest stacks fully detailed and retain every other stack as a
 * lightweight massing proxy. Source order is the stable tie-breaker and is
 * also preserved within each returned tier.
 */
export function partitionLegoStacksByDistance<T>(
  entries: readonly T[],
  distanceSquaredFor: (entry: T) => number,
  budget = LEGO_STACK_RENDER_BUDGET,
): LegoStackLodSelection<T> {
  const safeBudget = Math.min(entries.length, Math.max(0, Math.floor(budget)));
  const ranked = entries
    .map((entry, index) => ({
      entry,
      index,
      distanceSquared: distanceSquaredFor(entry),
    }))
    .sort((a, b) => (
      a.distanceSquared - b.distanceSquared
      || a.index - b.index
    ));
  const detailedIndexes = new Set(
    ranked.slice(0, safeBudget).map(({ index }) => index),
  );

  return {
    detailed: entries.filter((_entry, index) => detailedIndexes.has(index)),
    simplified: entries.filter((_entry, index) => !detailedIndexes.has(index)),
  };
}

/**
 * Keep the nearest stacks detailed while also limiting distinct heavy family
 * asset sets. Once a family is admitted, later stacks from that same family
 * may continue to use shared detailed resources up to the ordinary stack
 * budget. Source order remains the stable tie-breaker and output order.
 */
export function partitionLegoStacksByDistanceAndFamily<T>(
  entries: readonly T[],
  familyKeyFor: (entry: T) => string,
  distanceSquaredFor: (entry: T) => number,
  stackBudget = LEGO_STACK_RENDER_BUDGET,
  familyBudget = LEGO_DISTINCT_FAMILY_RENDER_BUDGET,
): LegoStackLodSelection<T> {
  const safeStackBudget = Math.min(entries.length, Math.max(0, Math.floor(stackBudget)));
  const safeFamilyBudget = Math.max(0, Math.floor(familyBudget));
  const ranked = entries
    .map((entry, index) => ({
      entry,
      index,
      familyKey: familyKeyFor(entry),
      distanceSquared: distanceSquaredFor(entry),
    }))
    .sort((a, b) => (
      a.distanceSquared - b.distanceSquared
      || a.index - b.index
    ));
  const detailedIndexes = new Set<number>();
  const admittedFamilies = new Set<string>();

  for (const candidate of ranked) {
    if (detailedIndexes.size >= safeStackBudget) break;
    if (!admittedFamilies.has(candidate.familyKey)) {
      if (admittedFamilies.size >= safeFamilyBudget) continue;
      admittedFamilies.add(candidate.familyKey);
    }
    detailedIndexes.add(candidate.index);
  }

  return {
    detailed: entries.filter((_entry, index) => detailedIndexes.has(index)),
    simplified: entries.filter((_entry, index) => !detailedIndexes.has(index)),
  };
}

/** Initial deterministic tier before the first camera-distance sample. */
export function selectDetailedLegoStacks<T>(
  entries: readonly T[],
  budget = LEGO_STACK_RENDER_BUDGET,
): T[] {
  return partitionLegoStacksByDistance(entries, () => 0, budget).detailed;
}
