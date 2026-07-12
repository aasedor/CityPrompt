const OBJECT_HEIGHT_FILTER_THRESHOLD_METERS = 2;

/**
 * Raycast terrain anchors sampled during the first frames often hit the
 * planet's UNREFINED root tiles, which sit tens of kilometres off the true
 * surface (measured ≈ -28km at Calgary). Freezing such a sample as a zone's
 * anchor bakes a ±29km offset into everything seated relative to it — the
 * per-instance offsets cancel it visually, but the numbers are fragile
 * (float precision, and any code change on one side of the cancellation
 * strands content in the sky). Anchors are only trusted within this band of
 * a reference height (stored zone terrain or the elevation-API fallback).
 */
export const MAX_ANCHOR_DEVIATION_METERS = 500;

export function isPlausibleTerrainAnchor(
  sampled: number | null | undefined,
  reference: number | null | undefined,
): boolean {
  if (!Number.isFinite(sampled)) return false;
  if (!Number.isFinite(reference)) return true;
  return Math.abs((sampled as number) - (reference as number)) <= MAX_ANCHOR_DEVIATION_METERS;
}

export function shouldFilterObjectTerrainHeight(zoneType: string | null | undefined): boolean {
  return zoneType === 'green_space';
}

export function getObjectFilteredTerrainHeight(
  samples: Array<number | null | undefined>,
  fallback: number | null | undefined,
): number | null {
  const finiteSamples = samples
    .filter((sample): sample is number => Number.isFinite(sample))
    .sort((a, b) => a - b);

  if (finiteSamples.length === 0) {
    return Number.isFinite(fallback) ? fallback as number : null;
  }

  const lowerQuartileIndex = Math.floor((finiteSamples.length - 1) * 0.25);
  const groundCandidate = finiteSamples[lowerQuartileIndex];

  if (
    Number.isFinite(fallback)
    && (fallback as number) - groundCandidate <= OBJECT_HEIGHT_FILTER_THRESHOLD_METERS
  ) {
    return fallback as number;
  }

  return groundCandidate;
}

export function getRepresentativeTerrainHeight(
  samples: Array<number | null | undefined>,
  fallback: number,
): number {
  const finiteSamples = samples
    .filter((sample): sample is number => Number.isFinite(sample))
    .sort((a, b) => a - b);

  if (finiteSamples.length === 0) {
    return fallback;
  }

  const middleIndex = Math.floor(finiteSamples.length / 2);
  if (finiteSamples.length % 2 === 1) {
    return finiteSamples[middleIndex];
  }

  return (finiteSamples[middleIndex - 1] + finiteSamples[middleIndex]) / 2;
}

export function resolveZoneTerrainHeight(
  sampledTerrainHeight: number | null | undefined,
  storedTerrainHeight: number | null | undefined,
  fallbackTerrainHeight: number,
): number {
  if (Number.isFinite(sampledTerrainHeight)) {
    return sampledTerrainHeight as number;
  }

  if (Number.isFinite(storedTerrainHeight)) {
    return storedTerrainHeight as number;
  }

  return fallbackTerrainHeight;
}
