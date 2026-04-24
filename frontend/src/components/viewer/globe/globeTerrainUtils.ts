const STABLE_SURFACE_ZONE_TYPES = new Set([
  'building',
  'residential',
  'green_space',
  'site_boundary',
]);

export function shouldUseStableSurfaceHeight(zoneType: string | null | undefined): boolean {
  return !!zoneType && STABLE_SURFACE_ZONE_TYPES.has(zoneType);
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
