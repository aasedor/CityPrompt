import { describe, expect, it } from 'vitest';

import { normalizePolygonDrawing } from './drawingGeometry';

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
