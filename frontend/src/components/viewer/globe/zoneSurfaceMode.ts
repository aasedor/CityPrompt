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
 * Keep pre-generation buildings flat without treating them like extruded
 * buildings. Their planning footprint must use the terrain-conforming surface
 * path or it disappears into sloped photogrammetry.
 */
export function resolveZoneSurfaceMode({
  isBuilding,
  isCompiledCommunity,
  isCompiledGround,
  isPark,
  isPreparedBoundary,
}: ZoneSurfaceModeInput): ZoneSurfaceMode {
  const isPlanningBuilding = isBuilding && !isCompiledCommunity;
  const isExtrudedBuilding = isBuilding && isCompiledCommunity;
  return {
    isPlanningBuilding,
    isExtrudedBuilding,
    useTerrainGridFlat: (
      isCompiledGround
      || isPark
      || isPreparedBoundary
      || isPlanningBuilding
    ),
  };
}
