import { describe, expect, it } from 'vitest';

import { PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS } from './publicRealmDepthPolicy';
import {
  PLANNING_BUILDING_SURFACE_LIFT_METERS,
  resolveZoneSurfaceMode,
} from './zoneSurfaceMode';

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
      flatSurfaceLiftMeters: PLANNING_BUILDING_SURFACE_LIFT_METERS,
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
      flatSurfaceLiftMeters: PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS,
    });
  });

  it('continues terrain-draping park and prepared ground', () => {
    expect(resolveZoneSurfaceMode({
      isBuilding: false,
      isCompiledCommunity: true,
      isCompiledGround: true,
      isPark: true,
      isPreparedBoundary: true,
    })).toMatchObject({
      useTerrainGridFlat: true,
      flatSurfaceLiftMeters: PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS,
    });
  });
});
