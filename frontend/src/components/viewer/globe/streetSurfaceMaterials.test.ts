import { describe, expect, it, vi } from 'vitest';
import * as THREE from 'three';

import {
  STREET_SURFACE_MATERIAL_SPECS,
  createMetricSurfaceGeometry,
  createStreetSurfacePaletteTint,
  createStreetSurfaceAlbedoTexture,
  createStreetSurfaceMaterialResources,
  resolveStreetAppearanceMaterialKind,
  resolveStreetSurfaceMaterialKind,
  type StreetSurfaceMaterialKind,
} from './streetSurfaceMaterials';

const MATERIAL_KINDS = Object.keys(
  STREET_SURFACE_MATERIAL_SPECS,
) as StreetSurfaceMaterialKind[];

function pixels(texture: THREE.DataTexture): Uint8Array {
  return texture.image.data as Uint8Array;
}

function uniqueRgbCount(texture: THREE.DataTexture): number {
  const data = pixels(texture);
  const colors = new Set<string>();
  for (let offset = 0; offset < data.length; offset += 4) {
    colors.add(`${data[offset]}:${data[offset + 1]}:${data[offset + 2]}`);
  }
  return colors.size;
}

describe('metric public-realm base geometry', () => {
  it('maps local ENU metres directly to repeatable UV coordinates', () => {
    const source = new THREE.BufferGeometry();
    source.setAttribute('position', new THREE.Float32BufferAttribute([
      -6, -2, 0,
      9, -2, 0,
      9, 4, 0,
    ], 3));
    const metric = createMetricSurfaceGeometry(source);
    expect(Array.from(metric.getAttribute('uv').array)).toEqual([
      -6, -2,
      9, -2,
      9, 4,
    ]);
    expect(source.getAttribute('uv')).toBeUndefined();
    metric.dispose();
    source.dispose();
  });
});

describe('street surface semantic resolution', () => {
  it('uses stone setts across the European carriageway and pedestrian realm without changing other variants', () => {
    expect(resolveStreetAppearanceMaterialKind(
      'asphalt',
      'european_cobblestone_v1',
      'motor',
    )).toBe('buffer_stone');
    expect(resolveStreetAppearanceMaterialKind(
      'parking_asphalt',
      'european_cobblestone_v1',
      'parking',
    )).toBe('buffer_stone');
    expect(resolveStreetAppearanceMaterialKind(
      'concrete',
      'european_cobblestone_v1',
      'sidewalk',
    )).toBe('buffer_stone');
    expect(resolveStreetAppearanceMaterialKind(
      'asphalt',
      'european_cobblestone_v1',
      'path',
    )).toBe('buffer_stone');
    expect(resolveStreetAppearanceMaterialKind(
      'asphalt',
      'classic_tree_lined_v1',
      'motor',
    )).toBe('asphalt');
  });

  it('preserves palette hue without multiplying procedural albedo to black', () => {
    const tint = createStreetSurfacePaletteTint('#8d6e63');
    expect(Math.max(tint.r, tint.g, tint.b)).toBeCloseTo(1, 8);
    expect(tint.r).toBeGreaterThan(tint.g);
    expect(tint.g).toBeGreaterThan(tint.b);
    expect(Math.min(tint.r, tint.g, tint.b)).toBeGreaterThan(0.55);
  });

  it.each([
    [{ kind: 'motor', surface: 'brick paving' }, 'unit_pavers'],
    [{ kind: 'motor', surface: 'red asphalt' }, 'asphalt'],
    [{ kind: 'parking', surface: 'asphalt' }, 'parking_asphalt'],
    [{ kind: 'sidewalk', surface: 'architectural concrete' }, 'concrete'],
    [{ kind: 'planting', surface: 'permeable paving' }, 'unit_pavers'],
    [{ kind: 'planting', label: 'Tree boulevard' }, 'planting_grass'],
    [{ kind: 'buffer', surface: 'granite separator' }, 'buffer_stone'],
    [{ kind: 'shoulder', surface: 'compacted gravel' }, 'buffer_stone'],
  ] as const)('maps %o to %s without erasing explicit surface words', (semantics, expected) => {
    expect(resolveStreetSurfaceMaterialKind(semantics)).toBe(expected);
  });

  it('lets an explicit unit-paver surface override a broad motor band', () => {
    expect(resolveStreetSurfaceMaterialKind({
      kind: 'motor',
      sourceType: 'shared_lane',
      surface: 'permeable unit paving',
    })).toBe('unit_pavers');
  });
});

describe('procedural street surface albedo', () => {
  it.each(MATERIAL_KINDS)('creates deterministic non-flat %s texture resources', (kind) => {
    const first = createStreetSurfaceAlbedoTexture(kind, {
      seed: 'street-a', size: 32, anisotropy: 2,
    });
    const second = createStreetSurfaceAlbedoTexture(kind, {
      seed: 'street-a', size: 32, anisotropy: 8,
    });

    expect(Array.from(pixels(second))).toEqual(Array.from(pixels(first)));
    expect(uniqueRgbCount(first)).toBeGreaterThan(8);
    expect(first.wrapS).toBe(THREE.RepeatWrapping);
    expect(first.wrapT).toBe(THREE.RepeatWrapping);
    expect(first.colorSpace).toBe(THREE.SRGBColorSpace);
    expect(first.anisotropy).toBeGreaterThanOrEqual(4);
    expect(second.anisotropy).toBe(8);
    expect(first.generateMipmaps).toBe(true);
    expect(first.repeat.x).toBeCloseTo(
      1 / STREET_SURFACE_MATERIAL_SPECS[kind].metersPerTile,
      8,
    );
    expect(first.repeat.y).toBeCloseTo(first.repeat.x, 8);
    expect(first.userData).toMatchObject({
      streetSurfaceKind: kind,
      metersPerTile: STREET_SURFACE_MATERIAL_SPECS[kind].metersPerTile,
    });

    first.dispose();
    second.dispose();
  });

  it('changes its deterministic grain when the seed changes', () => {
    const first = createStreetSurfaceAlbedoTexture('asphalt', { seed: 'one', size: 32 });
    const second = createStreetSurfaceAlbedoTexture('asphalt', { seed: 'two', size: 32 });
    expect(Array.from(pixels(second))).not.toEqual(Array.from(pixels(first)));
    first.dispose();
    second.dispose();
  });

  it('requires power-of-two dimensions suitable for generated mipmaps', () => {
    expect(() => createStreetSurfaceAlbedoTexture('concrete', { size: 30 }))
      .toThrow(/power of two/i);
  });
});

describe('street surface material ownership', () => {
  it('resolves semantics, applies physical defaults and disposes owned resources once', () => {
    const resources = createStreetSurfaceMaterialResources({
      kind: 'motor',
      surface: 'brick herringbone pavers',
    }, {
      seed: 'shared-street',
      size: 32,
      tint: '#f2e5d4',
    });
    const materialDispose = vi.spyOn(resources.material, 'dispose');
    const textureDispose = vi.spyOn(resources.albedo, 'dispose');

    expect(resources.kind).toBe('unit_pavers');
    expect(resources.material.map).toBe(resources.albedo);
    expect(resources.material.roughness).toBe(
      STREET_SURFACE_MATERIAL_SPECS.unit_pavers.roughness,
    );
    expect(resources.material.metalness).toBe(0);
    expect(resources.material.color.getHexString()).toBe('f2e5d4');

    resources.dispose();
    resources.dispose();
    expect(materialDispose).toHaveBeenCalledTimes(1);
    expect(textureDispose).toHaveBeenCalledTimes(1);
  });

  it('returns independent owned resources rather than retaining a hidden cache', () => {
    const first = createStreetSurfaceMaterialResources('asphalt', { size: 16 });
    const second = createStreetSurfaceMaterialResources('asphalt', { size: 16 });
    expect(first.material).not.toBe(second.material);
    expect(first.albedo).not.toBe(second.albedo);
    expect(Array.from(pixels(first.albedo))).toEqual(Array.from(pixels(second.albedo)));
    first.dispose();
    second.dispose();
  });
});
