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
  return [
    'building',
    'residential',
    'road',
    'street',
    'green_space',
    'park',
    'plaza',
    'parking',
  ].includes(zoneType ?? '');
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
    && Math.abs((fallback as number) - groundCandidate) <= OBJECT_HEIGHT_FILTER_THRESHOLD_METERS
  ) {
    return fallback as number;
  }

  return groundCandidate;
}

/** Google Elevation failures historically returned one geoid fallback value
 * for every requested point. Treat a constant response as unavailable so a
 * polygon can fall back to the loaded 3D-tile surface instead of becoming a
 * flat card that bridges across roofs and slopes. */
export function hasUsableElevationRelief(
  elevations: Array<number | null | undefined> | null | undefined,
  minimumRangeMeters = 0.05,
): elevations is number[] {
  const finite = (elevations ?? []).filter(
    (elevation): elevation is number => Number.isFinite(elevation),
  );
  if (finite.length < 2) return false;
  return Math.max(...finite) - Math.min(...finite) >= minimumRangeMeters;
}

/** Reconcile a current tile probe with a stored placement height. A material
 * disagreement is usually "ground versus roof"; the lower plausible surface
 * is the safe seating plane for replacement development. */
export function preferLowerGroundAnchor(
  sampled: number | null | undefined,
  stored: number | null | undefined,
  thresholdMeters = OBJECT_HEIGHT_FILTER_THRESHOLD_METERS,
): number | null {
  const hasSampled = Number.isFinite(sampled);
  const hasStored = Number.isFinite(stored);
  if (!hasSampled) return hasStored ? stored as number : null;
  if (!hasStored) return sampled as number;
  return Math.abs((sampled as number) - (stored as number)) > thresholdMeters
    ? Math.min(sampled as number, stored as number)
    : stored as number;
}

/** Choose the safest bare-ground frame origin for replacement development.
 * A current tile ray, a stored zone height, or the project terrain fallback
 * may each have landed on a roof. Material disagreement therefore resolves to
 * the lower plausible elevation in both comparisons. */
export function resolveReplacementGroundAnchor(
  sampled: number | null | undefined,
  stored: number | null | undefined,
  projectTerrain: number | null | undefined,
  thresholdMeters = OBJECT_HEIGHT_FILTER_THRESHOLD_METERS,
): number | null {
  return preferLowerGroundAnchor(
    preferLowerGroundAnchor(sampled, stored, thresholdMeters),
    projectTerrain,
    thresholdMeters,
  );
}

/**
 * Reject an isolated photogrammetry object-top hit for an interior ground
 * vertex without flattening legitimate terrain below the surrounding ground.
 *
 * Public-realm meshes first obtain expensive, object-filtered samples around
 * their boundary. Interior vertices can then use one cheap raycast each and
 * compare it with the nearest trusted boundary sample. A roof/tree hit rises
 * abruptly above that local reference and is replaced; a swale, reservoir or
 * other lower surface remains valid.
 */
export function rejectRaisedObjectTop(
  sampled: number | null | undefined,
  nearbyGround: number | null | undefined,
  thresholdMeters = OBJECT_HEIGHT_FILTER_THRESHOLD_METERS,
): number | null {
  const hasSampled = Number.isFinite(sampled);
  const hasNearbyGround = Number.isFinite(nearbyGround);
  if (!hasSampled) return hasNearbyGround ? nearbyGround as number : null;
  if (!hasNearbyGround) return sampled as number;
  return (sampled as number) > (nearbyGround as number) + thresholdMeters
    ? nearbyGround as number
    : sampled as number;
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
