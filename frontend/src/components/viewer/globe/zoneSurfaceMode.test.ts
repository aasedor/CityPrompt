import { describe, expect, it } from 'vitest';

import {
  resolveBuildingExtrudeHeight,
  resolveZoneSurfaceMode,
} from './zoneSurfaceMode';

describe('zone surface mode', () => {
  it('renders an ungenerated building as an editable extruded mass', () => {
    expect(resolveZoneSurfaceMode({
      isBuilding: true,
      isCompiledCommunity: false,
      isCompiledGround: false,
      isPark: false,
      isPreparedBoundary: false,
    })).toEqual({
      isPlanningBuilding: true,
      isExtrudedBuilding: true,
      useTerrainGridFlat: false,
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

  it('uses the configured building height with a visible default mass', () => {
    expect(resolveBuildingExtrudeHeight(true, 21)).toBe(21);
    expect(resolveBuildingExtrudeHeight(true, 0)).toBe(10);
    expect(resolveBuildingExtrudeHeight(true, Number.NaN)).toBe(10);
    expect(resolveBuildingExtrudeHeight(false, 21)).toBe(0);
  });
});
