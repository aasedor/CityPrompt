import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { resolveCommunity3DKind } from '@/features/community3d/community3d';

import {
  resolveBuildingExtrudeHeight,
  resolveZoneSurfaceMode,
} from './zoneSurfaceMode';

function plannedZone(properties: Record<string, unknown>): SiteZone {
  return {
    id: 'planned-zone',
    project_id: 'project-1',
    zone_type: 'development_area',
    coordinates: [[-114, 51], [-113.99, 51], [-113.99, 51.01]],
    color: '#abcdef',
    properties,
    sort_order: 0,
    created_at: '2026-08-14T00:00:00Z',
    updated_at: '2026-08-14T00:00:00Z',
  };
}

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

  it('extrudes AI Planner development areas but not framework-height overlays', () => {
    const plannedBuildingKind = resolveCommunity3DKind(plannedZone({
      _plan_role: 'building',
      height_m: 24,
    }));
    const frameworkKind = resolveCommunity3DKind(plannedZone({
      _plan_role: 'framework_height',
      height_m: 36,
    }));

    expect(plannedBuildingKind).toBe('building');
    expect(resolveZoneSurfaceMode({
      isBuilding: plannedBuildingKind === 'building',
      isCompiledCommunity: false,
      isCompiledGround: false,
      isPark: false,
      isPreparedBoundary: false,
    }).isExtrudedBuilding).toBe(true);

    expect(frameworkKind).toBeNull();
    expect(resolveZoneSurfaceMode({
      isBuilding: frameworkKind === 'building',
      isCompiledCommunity: false,
      isCompiledGround: false,
      isPark: false,
      isPreparedBoundary: false,
    }).isExtrudedBuilding).toBe(false);
  });
});
