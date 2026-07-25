import { describe, expect, it } from 'vitest';

import {
  isWithinPolygonCloseRadius,
  normalizePolygonDrawing,
  POLYGON_CLOSE_RADIUS_METERS,
} from './drawingGeometry';

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
