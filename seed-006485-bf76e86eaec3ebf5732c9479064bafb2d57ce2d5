import { describe, expect, it } from 'vitest';
import { buildLegoMassingMeshData, legoMassingColor } from './legoMassingGeometry';

describe('buildLegoMassingMeshData', () => {
  it('extrudes every vertex of a concave footprint without bounding-box overhang', () => {
    const longitude = -114.15;
    const latitude = 51.04;
    const ring = [
      [longitude, latitude],
      [longitude + 0.0002, latitude],
      [longitude + 0.0002, latitude + 0.0001],
      [longitude + 0.0001, latitude + 0.0001],
      [longitude + 0.0001, latitude + 0.0002],
      [longitude, latitude + 0.0002],
      [longitude, latitude],
    ];

    const mesh = buildLegoMassingMeshData(ring, longitude + 0.0001, latitude + 0.0001, 18);

    expect(mesh).not.toBeNull();
    expect(mesh?.vertexCount).toBe(12);
    expect(mesh?.positions.filter((_value, index) => index % 3 === 2)).toEqual([
      0, 0, 0, 0, 0, 0,
      18, 18, 18, 18, 18, 18,
    ]);
    expect(mesh?.indices.length).toBeGreaterThan(0);
  });

  it('rejects degenerate rings and non-positive heights', () => {
    expect(buildLegoMassingMeshData([[0, 0], [1, 1]], 0, 0, 10)).toBeNull();
    expect(buildLegoMassingMeshData([[0, 0], [1, 0], [0, 1]], 0, 0, 0)).toBeNull();
  });

  it('uses stable muted massing colours instead of plan-zone colors', () => {
    expect(legoMassingColor('family-a:building-1')).toBe(legoMassingColor('family-a:building-1'));
    expect(legoMassingColor('family-a:building-1')).toMatch(/^#[0-9a-f]{6}$/i);
  });
});
