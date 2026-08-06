import { describe, expect, it } from 'vitest';
import * as THREE from 'three';

import type { SiteZone } from '@/types';
import {
  applyResidualLandscapeUVs,
  createResidualLandscapeTexture,
  createResidualLandscapeRegionIndex,
  getCurrentResidualLandscapeClaim,
  getResidualLandscapeRecipe,
  hasCurrentResidualLandscapeRecipe,
  pointInPolygonWithHoles,
  pointInResidualGeometry,
  rasterizeResidualLandscapeRegions,
  residualLandscapeTextureSize,
  type ResidualLandscapeRecipe,
} from './residualLandscape';

const boundary: SiteZone = {
  id: 'boundary-1',
  project_id: 'project-1',
  zone_type: 'site_boundary',
  coordinates: [[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]],
  color: '#ffffff',
  properties: {},
  sort_order: 0,
  created_at: '2026-07-20T00:00:00Z',
  updated_at: '2026-07-20T00:00:00Z',
};

const leftWithHole = {
  type: 'Polygon' as const,
  coordinates: [
    [[0, 0], [5, 0], [5, 10], [0, 10], [0, 0]],
    [[1, 3], [3, 3], [3, 7], [1, 7], [1, 3]],
  ] as [number, number][][],
};

const recipe: ResidualLandscapeRecipe = {
  schema_version: 1,
  state: 'compiled',
  generator: 'residual_landscape',
  boundary_id: boundary.id,
  compiled_at: '2026-07-20T01:00:00Z',
  source_hash: '0123456789abcdef'.repeat(4),
  metric_crs: 'EPSG:32612',
  area_sqm: 42,
  occupied_area_sqm: 58,
  geometry: leftWithHole,
  regions: [{
    id: 'lawn-0001',
    kind: 'lawn',
    area_sqm: 42,
    minimum_width_m: 5,
    geometry: leftWithHole,
  }],
  placements: [{
    id: 'tree-0001',
    kind: 'tree',
    lng: 4,
    lat: 8,
    yaw_rad: 1.25,
    scale: 0.95,
  }],
};

const multipartRegionGeometry = {
  type: 'MultiPolygon' as const,
  coordinates: [
    [
      [[0, 0], [4, 0], [4, 10], [0, 10], [0, 0]],
      [[1, 3], [3, 3], [3, 7], [1, 7], [1, 3]],
    ],
    [
      [[6, 6], [9, 6], [9, 9], [6, 9], [6, 6]],
    ],
  ] as [number, number][][][],
};

const multipartRegionRecipe: ResidualLandscapeRecipe = {
  ...recipe,
  regions: [{
    id: 'lawn-multipart',
    kind: 'lawn',
    area_sqm: 35,
    minimum_width_m: 3,
    geometry: multipartRegionGeometry,
  }],
};

function withRecipe(value: unknown): SiteZone {
  return {
    ...boundary,
    properties: { community_3d_landscape: value },
  };
}

function pixel(texture: THREE.DataTexture, x: number, y: number): number[] {
  const width = texture.image.width;
  const data = texture.image.data as Uint8Array;
  const offset = (y * width + x) * 4;
  return Array.from(data.slice(offset, offset + 4));
}

describe('residual landscape recipe', () => {
  it('accepts only a current compiled recipe owned by the boundary', () => {
    expect(getResidualLandscapeRecipe(withRecipe(recipe))).toEqual(recipe);
    expect(getCurrentResidualLandscapeClaim([withRecipe(recipe)])).toEqual({
      boundary_id: boundary.id,
      source_hash: recipe.source_hash,
    });
    expect(getResidualLandscapeRecipe(withRecipe({ ...recipe, state: 'stale' }))).toBeNull();
    expect(getResidualLandscapeRecipe(withRecipe({ ...recipe, boundary_id: 'other' }))).toBeNull();
    expect(getResidualLandscapeRecipe({ ...withRecipe(recipe), zone_type: 'building' })).toBeNull();
  });

  it('accepts a current compiled recipe with multipart classified regions', () => {
    expect(getResidualLandscapeRecipe(withRecipe(multipartRegionRecipe)))
      .toEqual(multipartRegionRecipe);
    expect(hasCurrentResidualLandscapeRecipe([withRecipe(multipartRegionRecipe)])).toBe(true);
    expect(getCurrentResidualLandscapeClaim([withRecipe(multipartRegionRecipe)])).toEqual({
      boundary_id: boundary.id,
      source_hash: multipartRegionRecipe.source_hash,
    });
  });

  it('accepts a current zero-area residual when authored zones occupy the parcel', () => {
    const fullyOccupiedRecipe: ResidualLandscapeRecipe = {
      ...recipe,
      area_sqm: 0,
      occupied_area_sqm: 100,
      geometry: { type: 'Polygon', coordinates: [] },
      regions: [],
      placements: [],
    };

    expect(getResidualLandscapeRecipe(withRecipe(fullyOccupiedRecipe))).toEqual(fullyOccupiedRecipe);
    expect(hasCurrentResidualLandscapeRecipe([withRecipe(fullyOccupiedRecipe)])).toBe(true);
    expect(pointInResidualGeometry([5, 5], fullyOccupiedRecipe.geometry)).toBe(false);
  });

  it('blocks Direct 3D when an existing boundary recipe is stale or ambiguous', () => {
    const ordinaryZone = { ...boundary, id: 'building-1', zone_type: 'building' as const };
    expect(hasCurrentResidualLandscapeRecipe([withRecipe(recipe), ordinaryZone])).toBe(true);
    expect(hasCurrentResidualLandscapeRecipe([
      withRecipe({ ...recipe, state: 'stale' }), ordinaryZone,
    ])).toBe(false);
    expect(hasCurrentResidualLandscapeRecipe([
      withRecipe(recipe),
      { ...withRecipe(recipe), id: 'boundary-2' },
    ])).toBe(false);
    expect(hasCurrentResidualLandscapeRecipe([ordinaryZone])).toBe(true);
    expect(hasCurrentResidualLandscapeRecipe([
      ordinaryZone,
      { ...ordinaryZone, id: 'building-2' },
    ])).toBe(true);
  });

  it('respects polygon holes and multipolygon islands', () => {
    expect(pointInPolygonWithHoles([4, 5], leftWithHole.coordinates)).toBe(true);
    expect(pointInPolygonWithHoles([2, 5], leftWithHole.coordinates)).toBe(false);
    expect(pointInPolygonWithHoles([8, 5], leftWithHole.coordinates)).toBe(false);
    expect(pointInResidualGeometry([8, 8], {
      type: 'MultiPolygon',
      coordinates: [
        leftWithHole.coordinates,
        [[[7, 7], [9, 7], [9, 9], [7, 9], [7, 7]]],
      ],
    })).toBe(true);
  });

  it('paints only classified residual pixels and leaves holes neutral', () => {
    const texture = createResidualLandscapeTexture(boundary, recipe, 32);
    const lawn = pixel(texture, 13, 26); // lng~4.2, lat~8.3
    const occupied = pixel(texture, 26, 16); // right half
    const hole = pixel(texture, 6, 16); // lng~2, lat~5

    expect(lawn[0]).toBeLessThan(125);
    expect(occupied[0]).toBeGreaterThan(135);
    expect(hole[0]).toBeGreaterThan(135);
    expect(texture.wrapS).toBe(THREE.ClampToEdgeWrapping);
    expect(texture.wrapT).toBe(THREE.ClampToEdgeWrapping);
    texture.dispose();
  });

  it('rasterizes every multipart island, preserves holes, and keeps first-region wins', () => {
    const overlappingGroundcover = {
      id: 'groundcover-overlap',
      kind: 'low_groundcover' as const,
      area_sqm: 9,
      minimum_width_m: 3,
      geometry: {
        type: 'Polygon' as const,
        coordinates: [[[6, 6], [9, 6], [9, 9], [6, 9], [6, 6]]] as [number, number][][],
      },
    };
    const regions = [...multipartRegionRecipe.regions, overlappingGroundcover];
    const labels = rasterizeResidualLandscapeRegions(
      regions,
      { west: 0, east: 10, south: 0, north: 10 },
      32,
    );
    const labelAt = (x: number, y: number) => labels[y * 32 + x];

    expect(labelAt(11, 16)).toBe(0); // first polygon exterior
    expect(labelAt(24, 24)).toBe(0); // second polygon wins over later overlap
    expect(labelAt(6, 16)).toBe(-1); // first polygon hole
    expect(labelAt(16, 16)).toBe(-1); // gap between polygon parts

    const texture = createResidualLandscapeTexture(
      boundary,
      { ...multipartRegionRecipe, regions },
      32,
    );
    expect(pixel(texture, 11, 16)[0]).toBeLessThan(125);
    expect(pixel(texture, 24, 24)[0]).toBeLessThan(125);
    expect(pixel(texture, 6, 16)[0]).toBeGreaterThan(135);
    expect(pixel(texture, 16, 16)[0]).toBeGreaterThan(135);
    texture.dispose();
  });

  it('maps terrain vertices to a north-up geographic UV frame', () => {
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute([
      0, 0, 0,
      1, 0, 0,
      1, 1, 0,
      0, 1, 0,
    ], 3));
    applyResidualLandscapeUVs(
      geometry,
      [[0, 0], [10, 0], [10, 10], [0, 10]],
      boundary.coordinates,
    );
    expect(Array.from(geometry.getAttribute('uv').array)).toEqual([
      0, 0,
      1, 0,
      1, 1,
      0, 1,
    ]);
    geometry.dispose();
  });

  it('bounds candidate scans for hundreds of district-scale regions', () => {
    const regions = Array.from({ length: 900 }, (_, index) => {
      const x = index % 30;
      const y = Math.floor(index / 30);
      return {
        id: `lawn-${index}`,
        kind: 'lawn' as const,
        area_sqm: 1,
        minimum_width_m: 1,
        geometry: {
          type: 'Polygon' as const,
          coordinates: [[
            [x, y], [x + 1, y], [x + 1, y + 1], [x, y + 1], [x, y],
          ]] as [number, number][][],
        },
      };
    });
    const index = createResidualLandscapeRegionIndex(regions, {
      west: 0, east: 30, south: 0, north: 30,
    });
    const candidateCounts = regions.map((_, regionIndex) => (
      index.candidatesAt([
        (regionIndex % 30) + 0.5,
        Math.floor(regionIndex / 30) + 0.5,
      ]).length
    ));

    expect(index.gridSize).toBe(30);
    expect(Math.max(...candidateCounts)).toBeLessThanOrEqual(4);
  });

  it('indexes multipart islands without treating their holes or gaps as region content', () => {
    const region = multipartRegionRecipe.regions[0];
    const index = createResidualLandscapeRegionIndex(
      multipartRegionRecipe.regions,
      { west: 0, east: 10, south: 0, north: 10 },
    );

    expect(index.regionAt(3.5, 5)).toBe(region);
    expect(index.regionAt(7.5, 7.5)).toBe(region);
    expect(index.regionAt(2, 5)).toBeUndefined();
    expect(index.regionAt(5, 5)).toBeUndefined();
  });

  it('increases texture resolution by physical extent within a fixed GPU cap', () => {
    const smallParcel = {
      ...boundary,
      coordinates: [
        [-114.08, 51.04], [-114.079, 51.04],
        [-114.079, 51.041], [-114.08, 51.041], [-114.08, 51.04],
      ],
    };
    const kilometreDistrict = {
      ...boundary,
      coordinates: [
        [-114.08, 51.04], [-114.066, 51.04],
        [-114.066, 51.049], [-114.08, 51.049], [-114.08, 51.04],
      ],
    };
    const oversizedDistrict = {
      ...boundary,
      coordinates: [
        [-114.10, 51.02], [-113.90, 51.02],
        [-113.90, 51.20], [-114.10, 51.20], [-114.10, 51.02],
      ],
    };

    expect(residualLandscapeTextureSize(smallParcel)).toBe(256);
    expect(residualLandscapeTextureSize(kilometreDistrict)).toBe(1024);
    expect(residualLandscapeTextureSize(oversizedDistrict)).toBe(1024);
  });

  it('rasterizes a 1024px residual with many authored holes within a bounded time', () => {
    const holes = Array.from({ length: 40 }, (_, index) => {
      const column = index % 8;
      const row = Math.floor(index / 8);
      const west = 0.45 + column * 1.15;
      const south = 0.55 + row * 1.65;
      return [
        [west, south], [west + 0.55, south],
        [west + 0.55, south + 0.7], [west, south + 0.7], [west, south],
      ] as [number, number][];
    });
    const exterior = boundary.coordinates.map(
      ([lng, lat]) => [lng, lat] as [number, number],
    );
    const manyHoleGeometry = {
      type: 'Polygon' as const,
      coordinates: [exterior, ...holes],
    };
    const manyHoleRecipe: ResidualLandscapeRecipe = {
      ...recipe,
      geometry: manyHoleGeometry,
      regions: [{
        id: 'lawn-many-holes',
        kind: 'lawn',
        area_sqm: 80,
        minimum_width_m: 10,
        geometry: manyHoleGeometry,
      }],
      placements: [],
    };

    const startedAt = performance.now();
    const texture = createResidualLandscapeTexture(boundary, manyHoleRecipe, 1024);
    const elapsedMs = performance.now() - startedAt;

    expect(elapsedMs).toBeLessThan(3000);
    texture.dispose();
  }, 10_000);

  it('scanline-rasterizes a high-vertex imported boundary without a main-thread stall', () => {
    const exterior = Array.from({ length: 1001 }, (_, index) => {
      const angle = (index / 1000) * Math.PI * 2;
      return [
        5 + Math.cos(angle) * 4.5,
        5 + Math.sin(angle) * 4.5,
      ] as [number, number];
    });
    const highVertexGeometry = {
      type: 'Polygon' as const,
      coordinates: [exterior],
    };
    const highVertexRecipe: ResidualLandscapeRecipe = {
      ...recipe,
      geometry: highVertexGeometry,
      regions: [{
        id: 'lawn-high-vertex',
        kind: 'lawn',
        area_sqm: 64,
        minimum_width_m: 9,
        geometry: highVertexGeometry,
      }],
      placements: [],
    };

    const startedAt = performance.now();
    const texture = createResidualLandscapeTexture(boundary, highVertexRecipe, 1024);
    const elapsedMs = performance.now() - startedAt;

    expect(pixel(texture, 512, 512)[0]).toBeLessThan(125);
    expect(pixel(texture, 8, 8)[0]).toBeGreaterThan(135);
    expect(elapsedMs).toBeLessThan(2000);
    texture.dispose();
  }, 10_000);
});
