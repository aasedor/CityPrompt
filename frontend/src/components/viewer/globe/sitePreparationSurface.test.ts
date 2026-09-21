import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import {
  createSitePreparationGeometry,
  createPreparedSiteBackingGeometry,
  createSitePreparationTexture,
  createWoonerfPaverTexture,
  getPreparedSiteBoundaryIds,
  getActiveBoundaryTileMaskPreference,
  hasCompiledCommunity,
  overlapPreparedGroundEdges,
  resolvePreparedSiteTerrainHeight,
  resolvePreparedSiteTerrainForZone,
  preparedSiteContainsZone,
  PREPARED_SITE_BACKING_SEPARATION_METERS,
  shouldMaskReplacementBuildingTiles,
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
  it('inherits retained ground inside the boundary, permits an explicit override, and leaves outside objects independent', () => {
    const boundary = { ...zone('site', 'site_boundary', { community_3d_mask_existing_tiles: false }), is_active_boundary: true,
      coordinates: [[0, 0], [10, 0], [10, 10], [0, 10]] as [number, number][] };
    const building = { ...zone('inside', 'building'), coordinates: [[1, 1], [3, 1], [3, 3], [1, 3]] as [number, number][] };
    const inherited = getActiveBoundaryTileMaskPreference([boundary, building], building);
    expect(inherited).toBe(false);
    expect(shouldMaskReplacementBuildingTiles(building, true, inherited)).toBe(false);
    expect(shouldRenderReplacementFootprintGround(building, true, false, inherited)).toBe(false);
    expect(shouldMaskReplacementBuildingTiles({ ...building, properties: { community_3d_mask_existing_tiles: true } }, true, inherited)).toBe(true);
    expect(getActiveBoundaryTileMaskPreference([boundary], { ...building, coordinates: [[11, 1], [13, 1], [13, 3], [11, 3]] })).toBeNull();
    expect(getActiveBoundaryTileMaskPreference([{ ...boundary, is_active_boundary: false }], building)).toBeNull();
    expect(getActiveBoundaryTileMaskPreference([{ ...boundary, properties: {} }], building)).toBeNull();
  });
  it('places prepared backing physically below authored fill without changing its footprint or source', () => {
    const source = new THREE.BufferGeometry();
    source.setAttribute('position', new THREE.Float32BufferAttribute([0, 0, 0.08, 10, 0, 0.08, 0, 10, 0.08], 3));
    const backing = createPreparedSiteBackingGeometry(source, 'site');
    const input = source.getAttribute('position'), output = backing.getAttribute('position');
    for (let index = 0; index < input.count; index += 1) {
      expect(output.getX(index)).toBe(input.getX(index));
      expect(output.getY(index)).toBe(input.getY(index));
      expect(input.getZ(index)).toBeCloseTo(0.08);
      expect(output.getZ(index)).toBeCloseTo(0.08 - PREPARED_SITE_BACKING_SEPARATION_METERS);
      expect(output.getZ(index)).toBeGreaterThan(0);
    }
    source.dispose(); backing.dispose();
  });

  it('shares the active prepared datum only with contained authored zones', () => {
    const boundary = { ...zone('site', 'site_boundary', { terrain_elevation_m: 1031.25 }), is_active_boundary: true,
      coordinates: [[0, 0], [10, 0], [10, 4], [4, 4], [4, 10], [0, 10]] as [number, number][] };
    for (const type of ['building', 'road', 'green_space'] as const) {
      const contained = { ...zone(type, type, { terrain_elevation_m: 1090 }), coordinates: [[1, 1], [3, 1], [3, 3], [1, 3]] as [number, number][] };
      expect(resolvePreparedSiteTerrainForZone(contained, [boundary, contained], 999)).toBe(1031.25);
    }
    const notch = { ...zone('notch', 'building'), coordinates: [[6, 6], [8, 6], [8, 8], [6, 8]] as [number, number][] };
    expect(resolvePreparedSiteTerrainForZone(notch, [boundary, notch], 999)).toBeNull();
    expect(resolvePreparedSiteTerrainForZone(undefined, [boundary], 999)).toBeNull();
    expect(resolvePreparedSiteTerrainForZone(boundary, [{ ...boundary, is_active_boundary: false }], 999)).toBeNull();
    expect(resolvePreparedSiteTerrainForZone(boundary, [{ ...boundary, properties: { community_3d_mask_existing_tiles: false } }], 999)).toBeNull();
  });

  it('rejects an edge crossing a narrow concave notch even when all vertices and quartiles are inside', () => {
    const boundary = { ...zone('site', 'site_boundary'), coordinates: [[0, 0], [10, 0], [10, 10], [2.2, 10], [2.2, 1], [2.1, 1], [2.1, 10], [0, 10]] as [number, number][] };
    const bridge = { ...zone('bridge', 'road'), coordinates: [[1, 4], [9, 4], [9, 5], [1, 5]] as [number, number][] };
    expect(preparedSiteContainsZone(boundary, bridge)).toBe(false);
    expect(preparedSiteContainsZone(boundary, { ...bridge, coordinates: [[3, 4], [9, 4], [9, 5], [3, 5]] })).toBe(true);
    expect(preparedSiteContainsZone(boundary, { ...bridge, coordinates: [[0, 0], [10, 0], [10, 1], [0, 1]] })).toBe(true);
  });

  it('shares one stored terrain datum between the site mask and replacement surface', () => {
    expect(resolvePreparedSiteTerrainHeight(
      zone('boundary', 'site_boundary', { terrain_elevation_m: 1044.75 }),
      1000,
    )).toBe(1044.75);
    expect(resolvePreparedSiteTerrainHeight(zone('boundary', 'site_boundary'), 1000)).toBe(1000);
  });

  it('covers a clipped standalone building only without a prepared site boundary', () => {
    const building = zone('building', 'building');
    expect(shouldRenderReplacementFootprintGround(building, true, false)).toBe(true);
    expect(shouldRenderReplacementFootprintGround(building, false, false)).toBe(false);
    expect(shouldRenderReplacementFootprintGround(building, true, true)).toBe(false);
    expect(
      shouldRenderReplacementFootprintGround(zone('park', 'green_space'), true, false),
    ).toBe(false);
    const clearedLotBuilding = zone('cleared', 'building', {
      community_3d_mask_existing_tiles: false,
    });
    expect(shouldMaskReplacementBuildingTiles(clearedLotBuilding, true)).toBe(false);
    expect(shouldRenderReplacementFootprintGround(clearedLotBuilding, true, false)).toBe(false);
  });

  it('prepares the active boundary immediately, before community compilation', () => {
    const boundary = {
      ...zone('boundary', 'site_boundary'),
      is_active_boundary: true,
    };
    const planningPark = zone('park', 'green_space', { _plan_role: 'open_space' });
    expect(hasCompiledCommunity([boundary, planningPark])).toBe(false);
    expect(getPreparedSiteBoundaryIds([boundary, planningPark])).toEqual(new Set(['boundary']));

    const prepared = getPreparedSiteBoundaryIds([
      boundary,
      zone('park', 'green_space', { _plan_role: 'open_space', ...compiledPark }),
    ]);
    expect(prepared).toEqual(new Set(['boundary']));

    const inactive = {
      ...zone('old-boundary', 'site_boundary'),
      is_active_boundary: false,
    };
    expect(getPreparedSiteBoundaryIds([inactive, boundary])).toEqual(new Set(['boundary']));
  });

  it('does not create a synthetic prepared surface for an explicitly retained empty parcel', () => {
    const retainedGroundBoundary = {
      ...zone('boundary', 'site_boundary', {
        community_3d_mask_existing_tiles: false,
      }),
      is_active_boundary: true,
    };

    expect(getPreparedSiteBoundaryIds([retainedGroundBoundary])).toEqual(new Set());
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

  it.each(['earth', 'grass'] as const)('creates a deterministic %s surface without changing its opacity', (appearance) => {
    const textureA = createSitePreparationTexture('boundary-1', 32, appearance);
    const textureB = createSitePreparationTexture('boundary-1', 32, appearance);
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
    expect(Array.from(dataA.filter((_, index) => index % 4 === 3)).every(alpha => alpha === 255)).toBe(true);
    if (appearance === 'grass') {
      expect(channelMeans[1]).toBeGreaterThan(channelMeans[0] + 20);
      expect(channelMeans[1]).toBeGreaterThan(channelMeans[2] + 40);
    } else {
      expect(Math.max(...channelMeans) - Math.min(...channelMeans)).toBeLessThan(32);
      expect(channelMeans.every((mean) => mean > 100 && mean < 165)).toBe(true);
      expect(channelMeans[0]).toBeGreaterThanOrEqual(channelMeans[1]);
      expect(channelMeans[1] - channelMeans[2]).toBeLessThan(24);
    }
    textureA.dispose();
    textureB.dispose();
  });

  it('creates a deterministic warm unit-paver texture for woonerfs', () => {
    const textureA = createWoonerfPaverTexture('street-1', 64);
    const textureB = createWoonerfPaverTexture('street-1', 64);
    const dataA = textureA.image.data as Uint8Array;
    const dataB = textureB.image.data as Uint8Array;
    expect(Array.from(dataA)).toEqual(Array.from(dataB));
    expect(textureA.wrapS).toBe(THREE.RepeatWrapping);
    expect(textureA.wrapT).toBe(THREE.RepeatWrapping);
    const channelMeans = [0, 1, 2].map((channel) => {
      let total = 0;
      for (let index = channel; index < dataA.length; index += 4) total += dataA[index];
      return total / (dataA.length / 4);
    });
    expect(channelMeans[0]).toBeGreaterThan(channelMeans[1] + 35);
    expect(channelMeans[1]).toBeGreaterThan(channelMeans[2] + 15);
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
