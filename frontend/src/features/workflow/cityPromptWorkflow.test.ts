import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { deriveCityPromptWorkflow } from './cityPromptWorkflow';

const HASH = 'a'.repeat(64);

function zone(
  id: string,
  zoneType: SiteZone['zone_type'],
  properties: Record<string, unknown> = {},
): SiteZone {
  return {
    id,
    project_id: 'project-1',
    name: id,
    zone_type: zoneType,
    coordinates: [[0, 0], [1, 0], [1, 1]],
    color: '#fff',
    properties,
    sort_order: 0,
    created_at: '2026-08-03T00:00:00Z',
    updated_at: '2026-08-03T00:00:00Z',
  };
}

function activeBoundary(residual = false): SiteZone {
  return {
    ...zone('boundary', 'site_boundary', residual ? {
      community_3d_landscape: {
        schema_version: 1,
        state: 'compiled',
        boundary_id: 'boundary',
        source_hash: HASH,
      },
    } : {}),
    is_active_boundary: true,
  };
}

function compiledBuilding(): SiteZone {
  return zone('building', 'building', {
    community_3d: {
      schema_version: 1,
      state: 'compiled',
      kind: 'building',
      generator: 'lego_assembly',
      compiled_at: '2026-08-03T01:00:00Z',
      source_hash: HASH,
      representation_hash: 'b'.repeat(64),
    },
  });
}

describe('deriveCityPromptWorkflow', () => {
  it('starts with the site boundary', () => {
    const state = deriveCityPromptWorkflow([]);
    expect(state.currentStep).toBe(1);
    expect(state.canGenerate3D).toBe(false);
  });

  it('moves from planning to 3D generation as authored zones appear', () => {
    expect(deriveCityPromptWorkflow([activeBoundary()]).currentStep).toBe(2);

    const planned = deriveCityPromptWorkflow([
      activeBoundary(),
      zone('building', 'building'),
    ]);
    expect(planned.currentStep).toBe(3);
    expect(planned.canGenerate3D).toBe(true);
    expect(planned.canRender).toBe(false);
  });

  it('requires both current zone compilation and residual landscaping before render', () => {
    const missingLandscape = deriveCityPromptWorkflow([
      activeBoundary(),
      compiledBuilding(),
    ]);
    expect(missingLandscape.currentStep).toBe(3);
    expect(missingLandscape.renderReason).toMatch(/residual landscaping/i);

    const ready = deriveCityPromptWorkflow([
      activeBoundary(true),
      compiledBuilding(),
    ], true);
    expect(ready.currentStep).toBe(4);
    expect(ready.sceneReady).toBe(true);
    expect(ready.canRender).toBe(true);
    expect(ready.hasOutput).toBe(true);
  });

  it('treats stale compiled metadata as needing regeneration', () => {
    const stale = compiledBuilding();
    stale.properties = {
      community_3d: {
        ...(stale.properties?.community_3d as Record<string, unknown>),
        state: 'stale',
      },
    };
    const state = deriveCityPromptWorkflow([activeBoundary(true), stale]);
    expect(state.currentStep).toBe(3);
    expect(state.compiledZoneCount).toBe(0);
  });
});
