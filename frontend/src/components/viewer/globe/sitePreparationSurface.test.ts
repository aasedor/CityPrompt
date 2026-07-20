import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import {
  createSitePreparationGeometry,
  createSitePreparationTexture,
  getPreparedSiteBoundaryIds,
  hasCompiledCommunity,
  overlapPreparedGroundEdges,
  shouldRenderReplacementFootprintGround,
} from './sitePreparationSurface';

function zone(id: string, zoneType: SiteZone['zone_type'], properties: Record<string, unknown> = {}): SiteZone {
  return {
    id,
    project_id: 'project-1',
    zone_type: zoneType,
    coordinates: [[-114, 51], [-113.99, 51], [-113.99, 51.01]],
    color: '#ffffff',
    properties,
    sort_order: 0,
    created_at: '2026-07-17T00:00:00Z',
    updated_at: '2026-07-17T00:00:00Z',
  };
}

const compiledPark = {
  community_3d: {
    schema_version: 1,
    state: 'compiled',
    kind: 'park',
    generator: 'park_kit',
    compiled_at: '2026-07-17T01:00:00Z',
  },
};

describe('compiled site preparation', () => {
  it('covers a clipped standalone building only without a prepared site boundary', () => {
    const building = zone('building', 'building');
    expect(shouldRenderReplacementFootprintGround(building, true, false)).toBe(true);
    expect(shouldRenderReplacementFootprintGround(building, false, false)).toBe(false);
    expect(shouldRenderReplacementFootprintGround(building, true, true)).toBe(false);
    expect(
      shouldRenderReplacementFootprintGround(zone('park', 'green_space'), true, false),
    ).toBe(false);
  });

  it('activates only when a compilable community zone has been built', () => {
    const boundary = zone('boundary', 'site_boundary');
    const planningPark = zone('park', 'green_space', { _plan_role: 'open_space' });
    expect(hasCompiledCommunity([boundary, planningPark])).toBe(false);
    expect(getPreparedSiteBoundaryIds([boundary, planningPark]).size).toBe(0);

    const prepared = getPreparedSiteBoundaryIds([
      boundary,
      zone('park', 'green_space', { _plan_role: 'open_space', ...compiledPark }),
    ]);
    expect(prepared).toEqual(new Set(['boundary']));
  });

  it('adds deterministic natural variation without mutating source geometry', () => {
    const source = new THREE.PlaneGeometry(20, 20, 2, 2);
    const preparedA = createSitePreparationGeometry(source, 'boundary-1');
    const preparedB = createSitePreparationGeometry(source, 'boundary-1');
    expect(source.getAttribute('color')).toBeUndefined();
    expect(Array.from(preparedA.getAttribute('color').array)).toEqual(
      Array.from(preparedB.getAttribute('color').array),
    );
    expect(new Set(Array.from(preparedA.getAttribute('color').array)).size).toBeGreaterThan(1);
    expect(preparedA.getAttribute('uv').count).toBe(
      preparedA.getAttribute('position').count,
    );
    source.dispose();
    preparedA.dispose();
    preparedB.dispose();
  });

  it('creates a deterministic textured aerial surface instead of a flat site wash', () => {
    const textureA = createSitePreparationTexture('boundary-1', 32);
    const textureB = createSitePreparationTexture('boundary-1', 32);
    const dataA = textureA.image.data as Uint8Array;
    const dataB = textureB.image.data as Uint8Array;
    expect(Array.from(dataA)).toEqual(Array.from(dataB));
    expect(new Set(Array.from(dataA.filter((_, index) => index % 4 !== 3))).size).toBeGreaterThan(16);
    expect(textureA.wrapS).toBe(THREE.RepeatWrapping);
    expect(textureA.wrapT).toBe(THREE.RepeatWrapping);
    expect(textureA.generateMipmaps).toBe(true);
    expect(textureA.minFilter).toBe(THREE.LinearMipmapLinearFilter);
    const channelMeans = [0, 1, 2].map((channel) => {
      let total = 0;
      for (let index = channel; index < dataA.length; index += 4) total += dataA[index];
      return total / (dataA.length / 4);
    });
    expect(Math.max(...channelMeans) - Math.min(...channelMeans)).toBeLessThan(32);
    expect(channelMeans.every((mean) => mean > 100 && mean < 165)).toBe(true);
    expect(channelMeans[0]).toBeGreaterThanOrEqual(channelMeans[1]);
    expect(channelMeans[1] - channelMeans[2]).toBeLessThan(24);
    textureA.dispose();
    textureB.dispose();
  });

  it('adds a hidden edge overlap to cover spatial-mask raster seams', () => {
    const source = new THREE.PlaneGeometry(20, 10, 1, 1);
    source.computeBoundingBox();
    const before = source.boundingBox!.clone();
    overlapPreparedGroundEdges(source, 0.6);
    expect(source.boundingBox!.min.x).toBeCloseTo(before.min.x - 0.6, 5);
    expect(source.boundingBox!.max.x).toBeCloseTo(before.max.x + 0.6, 5);
    expect(source.boundingBox!.min.y).toBeCloseTo(before.min.y - 0.6, 5);
    expect(source.boundingBox!.max.y).toBeCloseTo(before.max.y + 0.6, 5);
    source.dispose();
  });
});
