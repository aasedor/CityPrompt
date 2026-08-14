export interface ZoneSurfaceModeInput {
  isBuilding: boolean;
  isCompiledCommunity: boolean;
  isCompiledGround: boolean;
  isPark: boolean;
  isPreparedBoundary: boolean;
}

export interface ZoneSurfaceMode {
  isPlanningBuilding: boolean;
  isExtrudedBuilding: boolean;
  useTerrainGridFlat: boolean;
}

/**
 * A drawn building is an editable mass from the moment its polygon exists.
 * Compilation replaces that mass with detailed geometry; it does not decide
 * whether the building has height. Parks and prepared ground stay on the
 * terrain-conforming flat-surface path.
 */
export function resolveZoneSurfaceMode({
  isBuilding,
  isCompiledCommunity,
  isCompiledGround,
  isPark,
  isPreparedBoundary,
}: ZoneSurfaceModeInput): ZoneSurfaceMode {
  const isPlanningBuilding = isBuilding && !isCompiledCommunity;
  const isExtrudedBuilding = isBuilding;
  return {
    isPlanningBuilding,
    isExtrudedBuilding,
    useTerrainGridFlat: (
      isCompiledGround
      || isPark
      || isPreparedBoundary
    ),
  };
}

export function resolveBuildingExtrudeHeight(
  isBuilding: boolean,
  configuredHeightMeters: number,
): number {
  if (!isBuilding) return 0;
  const finiteHeight = Number.isFinite(configuredHeightMeters) ? configuredHeightMeters : 0;
  return Math.max(finiteHeight, 10);
}
