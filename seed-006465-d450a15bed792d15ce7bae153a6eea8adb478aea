import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import {
  convexHull,
  createTileSpatialMaskConfig,
  isPointInsideSpatialMask,
  patchMaterialForSpatialMask,
  shouldUseSpatialTileMask,
  unpatchMaterialSpatialMask,
} from './TileSpatialMaskPlugin';

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

  it('builds a convex demolition envelope and clips only points inside its height band', () => {
    const config = createTileSpatialMaskConfig(boundary(), 1045);
    expect(config).not.toBeNull();
    expect(config?.halfSpaces).toHaveLength(4);
    expect(isPointInsideSpatialMask({ x: 0, y: 0, z: 5 }, config!)).toBe(true);
    expect(isPointInsideSpatialMask({ x: 500, y: 0, z: 5 }, config!)).toBe(false);
    expect(isPointInsideSpatialMask({ x: 0, y: 0, z: 220 }, config!)).toBe(false);
  });

  it('removes interior dents from a concave parcel without changing winding', () => {
    const hull = convexHull([
      { x: 0, y: 0 }, { x: 10, y: 0 }, { x: 10, y: 10 },
      { x: 5, y: 5 }, { x: 0, y: 10 },
    ]);
    expect(hull).toHaveLength(4);
    expect(hull.every((point) => !(point.x === 5 && point.y === 5))).toBe(true);
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

  it('pads the fixed-length shader half-space uniform', () => {
    const material = new THREE.MeshBasicMaterial();
    const config = createTileSpatialMaskConfig(boundary(), 1045)!;
    patchMaterialForSpatialMask(material, config);
    const shader = {
      uniforms: {},
      vertexShader: '#include <common>\n#include <worldpos_vertex>',
      fragmentShader: '#include <common>\n#include <clipping_planes_fragment>',
    };
    material.onBeforeCompile(shader as never, {} as never);
    expect((shader.uniforms as { siteMaskHalfSpaces: { value: THREE.Vector3[] } })
      .siteMaskHalfSpaces.value).toHaveLength(32);
  });
});
