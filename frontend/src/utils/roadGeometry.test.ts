import { describe, expect, it } from 'vitest';
import { bufferLineToPolygon, extractCenterline } from './roadGeometry';

describe('road centerline extraction', () => {
  it('recovers a centerline from the open polygon emitted by the buffer helper', () => {
    const source = [[-114.15, 51.04], [-114.14, 51.045], [-114.13, 51.047]];
    const centerline = extractCenterline(bufferLineToPolygon(source, 14));
    expect(centerline).toHaveLength(source.length);
    centerline.forEach((point, index) => {
      expect(point[0]).toBeCloseTo(source[index][0], 8);
      expect(point[1]).toBeCloseTo(source[index][1], 8);
    });
  });

  it('ignores the repeated GeoJSON closing vertex returned by PostGIS', () => {
    const open = [
      [-114.151225029, 51.046883822],
      [-114.151267442, 51.046940775],
      [-114.150087295, 51.047289978],
      [-114.150044884, 51.047233025],
    ];
    const closed = [...open, open[0]];
    const centerline = extractCenterline(closed);
    expect(centerline).toHaveLength(2);
    expect(centerline[0]).toEqual([
      (open[0][0] + open[3][0]) / 2,
      (open[0][1] + open[3][1]) / 2,
    ]);
    expect(centerline[1]).toEqual([
      (open[1][0] + open[2][0]) / 2,
      (open[1][1] + open[2][1]) / 2,
    ]);
  });
});
