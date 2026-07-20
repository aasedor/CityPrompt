/**
 * Bound the number of fully detailed LEGO stacks mounted at once.
 *
 * The original pilot limit of 20 hid valid compiled buildings in ordinary
 * community plans. Ninety-six covers every currently supported building in
 * the mixed-plan QA scene while retaining a guard until district-scale
 * instancing is introduced.
 */
export const LEGO_STACK_RENDER_BUDGET = 96;

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

/** Initial deterministic tier before the first camera-distance sample. */
export function selectDetailedLegoStacks<T>(
  entries: readonly T[],
  budget = LEGO_STACK_RENDER_BUDGET,
): T[] {
  return partitionLegoStacksByDistance(entries, () => 0, budget).detailed;
}
