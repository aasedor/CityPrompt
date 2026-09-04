import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import {
  createTileSpatialMaskConfig,
  createTileSpatialMaskSetConfig,
  isPointInsideSpatialMask,
  patchMaterialForSpatialMask,
  shouldUseSpatialTileMask,
  unpatchMaterialSpatialMask,
} from './TileSpatialMaskPlugin';
import { computeCentroid, METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { normalizeTileMaskRing, pointInTileMaskRing } from './tileMaskGeometry';
import { GlobeTileMaskLayer } from './GlobeTileMaskLayer';

function boundary(): SiteZone {
  return {
    id: 'site-1',
    project_id: 'project-1',
    zone_type: 'site_boundary',
    coordinates: [
      [-114.001, 50.999],
      [-113.999, 50.999],
      [-113.999, 51.001],
      [-114.001, 51.001],
    ],
    color: '#ffffff',
    properties: {},
    sort_order: 0,
    created_at: '2026-07-17T00:00:00Z',
    updated_at: '2026-07-17T00:00:00Z',
  };
}

describe('world-coordinate tile masking', () => {
  it('uses spatial clipping for a single placed building footprint', () => {
    const building = { ...boundary(), zone_type: 'building' as const };
    expect(shouldUseSpatialTileMask(building)).toBe(true);
    expect(createTileSpatialMaskConfig(building, 1045)).not.toBeNull();
  });

  it('uses the camera-independent mask for authored parks and legacy plazas', () => {
    const park = { ...boundary(), zone_type: 'green_space' as const };
    const plaza = { ...boundary(), id: 'plaza-1', zone_type: 'parking' as const };
    expect(shouldUseSpatialTileMask(park)).toBe(true);
    expect(shouldUseSpatialTileMask(plaza)).toBe(true);
    expect(createTileSpatialMaskSetConfig([park, plaza], 1045)?.maskCount).toBe(2);
  });

  it('clips a rectangular footprint only inside its height band', () => {
    const config = createTileSpatialMaskConfig(boundary(), 1045);
    expect(config).not.toBeNull();
    expect(config?.edges).toHaveLength(4);
    expect(isPointInsideSpatialMask({ x: 0, y: 0, z: 5 }, config!)).toBe(true);
    expect(isPointInsideSpatialMask({ x: 500, y: 0, z: 5 }, config!)).toBe(false);
    expect(isPointInsideSpatialMask({ x: 0, y: 0, z: 220 }, config!)).toBe(false);
  });

  it('combines disjoint replacement footprints without clipping the space between them', () => {
    const second = {
      ...boundary(),
      id: 'site-2',
      coordinates: boundary().coordinates.map(([lng, lat]) => [lng + 0.01, lat] as [number, number]),
    };
    const config = createTileSpatialMaskSetConfig([boundary(), second], 1045);
    expect(config).not.toBeNull();
    expect(config?.maskCount).toBe(2);
    expect(config?.edges).toHaveLength(8);
    expect(config?.maskRanges.map((range) => [range.x, range.y])).toEqual([
      [0, 4],
      [4, 4],
    ]);

    const firstCenterX = -0.005 * 69_700;
    const secondCenterX = 0.005 * 69_700;
    expect(isPointInsideSpatialMask({ x: firstCenterX, y: 0, z: 5 }, config!)).toBe(true);
    expect(isPointInsideSpatialMask({ x: secondCenterX, y: 0, z: 5 }, config!)).toBe(true);
    expect(isPointInsideSpatialMask({ x: 0, y: 0, z: 5 }, config!)).toBe(false);
  });

  it('retains context instead of falling back to projected prisms when capacity is exceeded', () => {
    const masks = Array.from({ length: 9 }, (_, index) => ({
      ...boundary(),
      id: `site-${index}`,
    }));
    expect(createTileSpatialMaskSetConfig(masks, 1045)).toBeNull();
    expect(GlobeTileMaskLayer({ zones: masks, terrainHeight: 1045 })).toBeNull();
  });

  it('preserves a concave notch rather than clearing its convex envelope', () => {
    const ring = normalizeTileMaskRing([
      { x: 0, y: 0 }, { x: 30, y: 0 }, { x: 30, y: 10 },
      { x: 10, y: 10 }, { x: 10, y: 30 }, { x: 0, y: 30 },
    ])!;
    for (const points of [ring, [...ring].reverse()]) {
      expect(pointInTileMaskRing({ x: 5, y: 25 }, points)).toBe(true);
      expect(pointInTileMaskRing({ x: 25, y: 5 }, points)).toBe(true);
      expect(pointInTileMaskRing({ x: 20, y: 20 }, points)).toBe(false);
      expect(pointInTileMaskRing({ x: 10, y: 10 }, points)).toBe(true);
      expect(pointInTileMaskRing({ x: 30.001, y: 5 }, points)).toBe(false);
    }
  });

  it('restores material shader hooks after spatial clipping is removed', () => {
    const material = new THREE.MeshBasicMaterial();
    const originalCompile = material.onBeforeCompile;
    const originalCacheKey = material.customProgramCacheKey;
    const config = createTileSpatialMaskConfig(boundary(), 1045)!;
    patchMaterialForSpatialMask(material, config);
    expect(material.onBeforeCompile).not.toBe(originalCompile);
    expect(material.customProgramCacheKey()).toContain('site-mask:');
    unpatchMaterialSpatialMask(material);
    expect(material.onBeforeCompile).toBe(originalCompile);
    expect(material.customProgramCacheKey).toBe(originalCacheKey);
  });

  it('pads fixed-length shader arrays and exposes the active mask count', () => {
    const material = new THREE.MeshBasicMaterial();
    const config = createTileSpatialMaskConfig(boundary(), 1045)!;
    patchMaterialForSpatialMask(material, config);
    const shader = {
      uniforms: {},
      vertexShader: '#include <common>\n#include <project_vertex>',
      fragmentShader: '#include <common>\n#include <clipping_planes_fragment>',
    };
    material.onBeforeCompile(shader as never, {} as never);
    expect((shader.uniforms as { siteMaskEdges: { value: THREE.Vector4[] } })
      .siteMaskEdges.value).toHaveLength(32);
    expect((shader.uniforms as { siteMaskRanges: { value: THREE.Vector2[] } })
      .siteMaskRanges.value).toHaveLength(8);
    expect((shader.uniforms as { siteMaskCount: { value: number } })
      .siteMaskCount.value).toBe(1);
    expect(shader.fragmentShader).toContain('insideAnySiteMask');
    expect(shader.fragmentShader).toContain('insideCurrentSiteMask = !insideCurrentSiteMask');
    expect(shader.vertexShader).toContain('instanceMatrix * siteMaskPosition');
  });

  it('matches an independently triangulated L-shaped site over a dense coverage grid', () => {
    const ring = [
      new THREE.Vector2(0, 0), new THREE.Vector2(30, 0), new THREE.Vector2(30, 10),
      new THREE.Vector2(10, 10), new THREE.Vector2(10, 30), new THREE.Vector2(0, 30),
    ];
    const triangles = THREE.ShapeUtils.triangulateShape(ring, []).map((indices) => new THREE.Triangle(
      ...indices.map((index) => new THREE.Vector3(ring[index].x, ring[index].y, 0)) as [THREE.Vector3, THREE.Vector3, THREE.Vector3],
    ));
    for (let x = -2.5; x < 33; x += 1) {
      for (let y = -2.5; y < 33; y += 1) {
        const expected = triangles.some((triangle) => triangle.containsPoint(new THREE.Vector3(x, y, 0)));
        expect(pointInTileMaskRing({ x, y }, ring), `coverage at ${x},${y}`).toBe(expected);
      }
    }
  });

  it('normalizes only redundant vertices and refuses crossings and invalid input', () => {
    const rectangle = [{ x: 0, y: 0 }, { x: 5, y: 0 }, { x: 10, y: 0 }, { x: 10, y: 0 }, { x: 10, y: 10 }, { x: 0, y: 10 }, { x: 0, y: 0 }];
    expect(normalizeTileMaskRing(rectangle)).toHaveLength(4);
    expect(normalizeTileMaskRing([{ x: 0, y: 0 }, { x: 10, y: 10 }, { x: 0, y: 10 }, { x: 10, y: 0 }])).toBeNull();
    expect(normalizeTileMaskRing([{ x: 0, y: 0 }, { x: NaN, y: 10 }, { x: 10, y: 0 }])).toBeNull();
    expect(normalizeTileMaskRing([{ x: 0, y: 0 }, { x: 5, y: 0 }, { x: 10, y: 0 }])).toBeNull();
  });

  it('changes the cache identity when an unchanged footprint moves to another location', () => {
    const first = boundary();
    const second = { ...first, coordinates: first.coordinates.map(([lng, lat]) => [lng + .02, lat] as [number, number]) };
    expect(createTileSpatialMaskConfig(first, 1045)!.cacheKey).not.toBe(createTileSpatialMaskConfig(second, 1045)!.cacheKey);
  });

  it('keeps context in a concave notch even when it is behind a masked point in the camera view', () => {
    const zone = boundary();
    const mPerLon = metersPerDegLon(51);
    zone.coordinates = [[0, 0], [30, 0], [30, 10], [10, 10], [10, 30], [0, 30]].map(([x, y]) => [
      -114 + x / mPerLon, 51 + y / METERS_PER_DEG_LAT,
    ]);
    const centroid = computeCentroid(zone.coordinates);
    const offset = new THREE.Vector3((-114 - centroid[0]) * metersPerDegLon(centroid[1]), (51 - centroid[1]) * METERS_PER_DEG_LAT, 0);
    const config = createTileSpatialMaskConfig(zone, 1045)!;
    const context = new THREE.Vector3(20, 20, 0).add(offset);
    const foreground = new THREE.Vector3(5, 5, 15).add(offset);
    const camera = new THREE.PerspectiveCamera(50, 1, .1, 1000);
    camera.position.copy(new THREE.Vector3(-40, -40, 60).add(offset));
    camera.lookAt(context);
    camera.updateMatrixWorld(true);
    const projectedContext = context.clone().project(camera);
    const projectedForeground = foreground.clone().project(camera);
    expect(projectedContext.x).toBeCloseTo(projectedForeground.x, 8);
    expect(projectedContext.y).toBeCloseTo(projectedForeground.y, 8);
    expect(isPointInsideSpatialMask(foreground, config)).toBe(true);
    expect(isPointInsideSpatialMask(context, config)).toBe(false);
  });
});
