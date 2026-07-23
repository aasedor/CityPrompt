import { describe, expect, it } from 'vitest';
import { buildContainedTerrainGroundMesh } from './terrainGroundMesh';

function pointInsideOrOnPolygon(point: { x: number; y: number }, polygon: Array<{ x: number; y: number }>): boolean {
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const a = polygon[j];
    const b = polygon[i];
    const cross = (point.x - a.x) * (b.y - a.y) - (point.y - a.y) * (b.x - a.x);
    const onSegment = Math.abs(cross) < 1e-9
      && point.x >= Math.min(a.x, b.x) - 1e-9
      && point.x <= Math.max(a.x, b.x) + 1e-9
      && point.y >= Math.min(a.y, b.y) - 1e-9
      && point.y <= Math.max(a.y, b.y) + 1e-9;
    if (onSegment) return true;
    const intersects = ((a.y > point.y) !== (b.y > point.y))
      && point.x < ((b.x - a.x) * (point.y - a.y)) / (b.y - a.y) + a.x;
    if (intersects) inside = !inside;
  }
  return inside;
}

describe('buildContainedTerrainGroundMesh', () => {
  it('keeps every added terrain vertex inside a concave parcel', () => {
    // L-shaped parcel: its arithmetic vertex centroid (1.67, 1.67) is outside.
    const boundary = [
      { x: 0, y: 0 },
      { x: 4, y: 0 },
      { x: 4, y: 1 },
      { x: 1, y: 1 },
      { x: 1, y: 4 },
      { x: 0, y: 4 },
    ];
    const triangles = [
      [0, 1, 3],
      [1, 2, 3],
      [0, 3, 5],
      [3, 4, 5],
    ];

    const mesh = buildContainedTerrainGroundMesh(boundary, triangles);

    expect(mesh.boundaryVertexCount).toBe(boundary.length);
    expect(mesh.indices).toHaveLength(triangles.length * 9);
    expect(mesh.vertices.every((point) => pointInsideOrOnPolygon(point, boundary))).toBe(true);
  });

  it('splits each source face into three faces with valid indices', () => {
    const mesh = buildContainedTerrainGroundMesh(
      [{ x: 0, y: 0 }, { x: 3, y: 0 }, { x: 0, y: 3 }],
      [[0, 1, 2]],
    );

    expect(mesh.vertices).toEqual([
      { x: 0, y: 0 },
      { x: 3, y: 0 },
      { x: 0, y: 3 },
      { x: 1, y: 1 },
    ]);
    expect(mesh.indices).toEqual([0, 1, 3, 1, 2, 3, 2, 0, 3]);
  });
});
