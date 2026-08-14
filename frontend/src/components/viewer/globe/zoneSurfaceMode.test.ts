import { describe, expect, it } from 'vitest';

import { resolveZoneSurfaceMode } from './zoneSurfaceMode';

describe('zone surface mode', () => {
  it('terrain-drapes an ungenerated building planning footprint', () => {
    expect(resolveZoneSurfaceMode({
      isBuilding: true,
      isCompiledCommunity: false,
      isCompiledGround: false,
      isPark: false,
      isPreparedBoundary: false,
    })).toEqual({
      isPlanningBuilding: true,
      isExtrudedBuilding: false,
      useTerrainGridFlat: true,
    });
  });

  it('keeps a generated building on the extruded geometry path', () => {
    expect(resolveZoneSurfaceMode({
      isBuilding: true,
      isCompiledCommunity: true,
      isCompiledGround: false,
      isPark: false,
      isPreparedBoundary: false,
    })).toEqual({
      isPlanningBuilding: false,
      isExtrudedBuilding: true,
      useTerrainGridFlat: false,
    });
  });

  it('continues terrain-draping park and prepared ground', () => {
    expect(resolveZoneSurfaceMode({
      isBuilding: false,
      isCompiledCommunity: true,
      isCompiledGround: true,
      isPark: true,
      isPreparedBoundary: true,
    }).useTerrainGridFlat).toBe(true);
  });
});
