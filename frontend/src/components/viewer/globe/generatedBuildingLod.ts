import { partitionLegoStacksByDistance, type LegoStackLodSelection } from './legoStackBudget';

/** Whole-building Meshy GLBs are heavier than modular LEGO stacks. */
export const GENERATED_BUILDING_DETAIL_BUDGET = 20;

export type GeneratedBuildingLodLevel = '0' | '1' | '2' | '3';

const GENERATED_BUILDING_LOD_DISTANCE_METERS: Readonly<Record<GeneratedBuildingLodLevel, number>> = {
  '0': 260,
  '1': 650,
  '2': 1_400,
  '3': Number.POSITIVE_INFINITY,
};

export function desiredGeneratedBuildingLodLevel(distanceMeters: number): GeneratedBuildingLodLevel {
  const distance = Number.isFinite(distanceMeters) ? Math.max(0, distanceMeters) : Number.POSITIVE_INFINITY;
  if (distance <= GENERATED_BUILDING_LOD_DISTANCE_METERS['0']) return '0';
  if (distance <= GENERATED_BUILDING_LOD_DISTANCE_METERS['1']) return '1';
  if (distance <= GENERATED_BUILDING_LOD_DISTANCE_METERS['2']) return '2';
  return '3';
}

/** Resolve the closest available asset without ever lowering a capture-pinned
 * RLASM/source model below LOD0. */
export function resolveGeneratedBuildingLodUrl(
  lodUrls: Readonly<Record<string, string>> | null | undefined,
  modelUrl: string | null | undefined,
  distanceMeters: number,
  capturePinned = false,
): { level: GeneratedBuildingLodLevel; url: string } | null {
  const available: Partial<Record<GeneratedBuildingLodLevel, string>> = {
    ...(modelUrl ? { '0': modelUrl } : {}),
  };
  for (const level of ['0', '1', '2', '3'] as const) {
    const candidate = lodUrls?.[level]?.trim();
    if (candidate) available[level] = candidate;
  }
  const desired = capturePinned ? '0' : desiredGeneratedBuildingLodLevel(distanceMeters);
  const levels = ['0', '1', '2', '3'] as const;
  const desiredIndex = levels.indexOf(desired);
  const order = [
    ...levels.slice(desiredIndex),
    ...levels.slice(0, desiredIndex).reverse(),
  ];
  const level = order.find((candidate) => Boolean(available[candidate]));
  return level ? { level, url: available[level] as string } : null;
}

/** Capture-pinned entries are always detailed, even if they temporarily exceed
 * the ordinary navigation budget. The remaining budget is filled by distance. */
export function partitionGeneratedBuildingLodWithPins<T>(
  entries: readonly T[],
  distanceSquaredFor: (entry: T) => number,
  isCapturePinned: (entry: T) => boolean,
  budget = GENERATED_BUILDING_DETAIL_BUDGET,
): LegoStackLodSelection<T> {
  const pinned = entries.filter(isCapturePinned);
  const pinnedSet = new Set(pinned);
  const remaining = entries.filter((entry) => !pinnedSet.has(entry));
  const selection = partitionLegoStacksByDistance(
    remaining,
    distanceSquaredFor,
    Math.max(0, budget - pinned.length),
  );
  return {
    detailed: [...pinned, ...selection.detailed],
    simplified: selection.simplified,
  };
}

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
