import { partitionLegoStacksByDistance, type LegoStackLodSelection } from './legoStackBudget';

/** Whole-building Meshy GLBs are heavier than modular LEGO stacks. */
export const GENERATED_BUILDING_DETAIL_BUDGET = 20;

/**
 * Keep the nearest generated GLBs detailed and retain every other building as
 * exact-footprint 3D massing. The generic partitioner is deterministic and
 * preserves source order inside each tier.
 */
export function partitionGeneratedBuildingLod<T>(
  entries: readonly T[],
  distanceSquaredFor: (entry: T) => number,
  budget = GENERATED_BUILDING_DETAIL_BUDGET,
): LegoStackLodSelection<T> {
  return partitionLegoStacksByDistance(entries, distanceSquaredFor, budget);
}
