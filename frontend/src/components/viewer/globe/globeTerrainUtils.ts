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

/** Reconcile a current tile probe with a stored placement height. The
 * disagreement rule is DIRECTIONAL (sunk-building fix, 2026-07-25):
 * - stored far ABOVE the sample: the stored height was likely a legacy roof
 *   click — seat on the sampled ground.
 * - sample far BELOW stored: the ray fell into an excavation, ditch, or
 *   unrefined-tile pit — keep the stored site grade so buildings seat level
 *   with the drapes and lawns that share it. */
/** Real sites vary a few metres below a coarse stored/project reference;
 *  drops inside this window are treated as excavation/ditch artifacts and
 *  keep the stored grade, while deeper drops indicate a roof-click store or
 *  a genuinely descending site and trust the sample. */
const EXCAVATION_REJECT_METERS = 6;

export function preferLowerGroundAnchor(
  sampled: number | null | undefined,
  stored: number | null | undefined,
  thresholdMeters = OBJECT_HEIGHT_FILTER_THRESHOLD_METERS,
): number | null {
  const hasSampled = Number.isFinite(sampled);
  const hasStored = Number.isFinite(stored);
  if (!hasSampled) return hasStored ? stored as number : null;
  if (!hasStored) return sampled as number;
  const sampledValue = sampled as number;
  const storedValue = stored as number;
  const drop = storedValue - sampledValue;
  // Three-band rule:
  // - deep drop (> EXCAVATION_REJECT): the stored value was a roof click or
  //   the site genuinely descends a storey — seat on the sampled ground.
  // - shallow drop (threshold..EXCAVATION_REJECT]: the ray likely fell into
  //   an excavation, ditch, or curb cut beside the footprint — keep the
  //   stored site grade so buildings seat level with drapes and lawns
  //   (sunk-building fix, 2026-07-25).
  // - otherwise (agreement, or sample above stored): the stored grade is the
  //   stable reference.
  if (drop > EXCAVATION_REJECT_METERS) return sampledValue;
  if (drop > thresholdMeters) return storedValue;
  return storedValue;
}

/** The regional elevation/geoid estimate is a loading fallback, not a ceiling
 * on measured local grade. Roof rejection requires independent nearby mesh
 * evidence; a height difference from the coarse API cannot establish a roof. */
export function resolveReplacementGroundAnchor(
  sampled: number | null | undefined,
  stored: number | null | undefined,
  projectTerrain: number | null | undefined,
  thresholdMeters = OBJECT_HEIGHT_FILTER_THRESHOLD_METERS,
  surroundingGround?: number | null,
): number | null {
  if (Number.isFinite(surroundingGround)) {
    const nearby = surroundingGround as number;
    if (Number.isFinite(sampled) && Math.abs((sampled as number) - nearby) <= thresholdMeters) {
      // Live local and surrounding ground agree. An old stored API height
      // must not drag both measurements back below the actual mesh.
      return Number.isFinite(stored) && Math.abs((stored as number) - (sampled as number)) <= thresholdMeters
        ? stored as number : sampled as number;
    }
    const local = preferLowerGroundAnchor(sampled, stored, thresholdMeters);
    return local !== null && Math.abs(local - nearby) <= thresholdMeters ? local : nearby;
  }
  const local = preferLowerGroundAnchor(sampled, stored, thresholdMeters);
  if (local === null) return Number.isFinite(projectTerrain) ? projectTerrain as number : null;
  return local;
}

/** Require several nearby hits in the same lower height band, so one ditch
 * or unrefined tile cannot become the persisted building anchor. This is
 * mesh-surface corroboration, not semantic proof that all roofs were excluded. */
export function corroboratedTerrainHeight(
  samples: Array<number | null | undefined>, reference: number | null | undefined,
): number | null {
  const finite = samples.filter((height): height is number => isPlausibleTerrainAnchor(height, reference)).sort((a, b) => a - b);
  for (let start = 0; start < finite.length - 2; start += 1) {
    const cluster = finite.slice(start).filter((height) => height - finite[start] <= 1.5);
    if (cluster.length >= 3) return getRepresentativeTerrainHeight(cluster, cluster[0]);
  }
  return null;
}

/** Only actual surrounding mesh samples can complete/cache a building anchor.
 * Missing tiles keep the fallback temporary so later refinement can recover. */
export function resolveMeasuredReplacementGround(
  localSamples: Array<number | null | undefined>, surroundingSamples: Array<number | null | undefined>,
  stored: number | null | undefined, projectTerrain: number,
): number | null {
  const reference = Number.isFinite(stored) ? stored : projectTerrain;
  const nearby = corroboratedTerrainHeight(surroundingSamples, reference);
  if (nearby === null) return null;
  const local = corroboratedTerrainHeight(localSamples, reference);
  return resolveReplacementGroundAnchor(local, stored, projectTerrain, OBJECT_HEIGHT_FILTER_THRESHOLD_METERS, nearby);
}

export function terrainAnchorRevisionKey(
  buildingId: string, longitude: number, latitude: number,
  sourceRevision: string | undefined, stored: number | null, fallback: number,
): string {
  return JSON.stringify([buildingId, longitude.toFixed(6), latitude.toFixed(6), sourceRevision, stored, fallback]);
}

/** Public realm follows the current streamed tile surface when it agrees with
 * persisted/project terrain. A replacement building benefits from a stable
 * stored base, but a park or street pinned even one metre below current terrain
 * disappears once normal depth testing is enabled. Material disagreement
 * still resolves downward to reject roofs and canopies. */
export function preferCurrentGroundAnchor(
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
    : sampled as number;
}

export function resolvePublicRealmGroundAnchor(
  sampled: number | null | undefined,
  stored: number | null | undefined,
  projectTerrain: number | null | undefined,
  thresholdMeters = OBJECT_HEIGHT_FILTER_THRESHOLD_METERS,
): number | null {
  const local = preferCurrentGroundAnchor(sampled, stored, thresholdMeters);
  return local ?? (Number.isFinite(projectTerrain) ? projectTerrain as number : null);
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
