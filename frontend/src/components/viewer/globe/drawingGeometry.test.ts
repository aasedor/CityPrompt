import { describe, expect, it } from 'vitest';

import {
  buildTerrainRelativeDrawingVertices,
  isWithinPolygonCloseRadius,
  normalizePolygonDrawing,
  POLYGON_CLOSE_RADIUS_METERS,
} from './drawingGeometry';

describe('terrain-relative drawing preview', () => {
  it('keeps every clicked point at its sampled terrain height in one ENU frame', () => {
    const vertices = buildTerrainRelativeDrawingVertices(
      [
        [-114.16, 51.04],
        [-114.159, 51.04],
        [-114.159, 51.041],
      ],
      [1024, 1027, 1025],
      1025,
      0.3,
      true,
    );

    expect(vertices.filter((_, index) => index % 3 === 2)).toEqual([
      -0.7,
      2.3,
      0.3,
      -0.7,
    ]);
  });

  it('falls back to the frame height for a missing point sample', () => {
    const vertices = buildTerrainRelativeDrawingVertices(
      [[-114.16, 51.04], [-114.159, 51.04]],
      [Number.NaN],
      1025,
      0.6,
    );

    expect(vertices[2]).toBeCloseTo(0.6);
    expect(vertices[5]).toBeCloseTo(0.6);
  });
});

describe('polygon close gesture', () => {
  it('only closes within the visible start-marker radius', () => {
    expect(isWithinPolygonCloseRadius(POLYGON_CLOSE_RADIUS_METERS)).toBe(true);
    expect(isWithinPolygonCloseRadius(POLYGON_CLOSE_RADIUS_METERS + 0.01)).toBe(false);
    expect(isWithinPolygonCloseRadius(18)).toBe(false);
  });
});

describe('normalizePolygonDrawing', () => {
  it('drops a final click that is effectively the first polygon vertex', () => {
    const coordinates = [
      [-114.16, 51.04],
      [-114.15, 51.04],
      [-114.15, 51.05],
      [-114.16000001, 51.04000001],
    ];

    expect(normalizePolygonDrawing(coordinates)).toEqual(coordinates.slice(0, -1));
  });

  it('preserves a real final vertex and does not mutate the input', () => {
    const coordinates = [
      [-114.16, 51.04],
      [-114.15, 51.04],
      [-114.15, 51.05],
      [-114.1599, 51.0401],
    ];
    const before = structuredClone(coordinates);

    expect(normalizePolygonDrawing(coordinates)).toEqual(coordinates);
    expect(coordinates).toEqual(before);
  });
});
