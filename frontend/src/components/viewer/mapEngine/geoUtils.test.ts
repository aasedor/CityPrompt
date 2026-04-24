import { describe, expect, it } from 'vitest';
import {
  METERS_PER_DEG_LAT,
  metersPerDegLon,
  polygonAreaM2,
  polygonDimensionsMeters,
} from './geoUtils';

const CENTER_LNG = -114.0719;
const CENTER_LAT = 51.0447;

function localMeterPolygon(points: Array<[number, number]>): number[][] {
  const mPerDegLon = metersPerDegLon(CENTER_LAT);
  return points.map(([x, y]) => [
    CENTER_LNG + x / mPerDegLon,
    CENTER_LAT + y / METERS_PER_DEG_LAT,
  ]);
}

function rectangle(width: number, depth: number, angleDeg = 0): number[][] {
  const halfW = width / 2;
  const halfD = depth / 2;
  const angle = angleDeg * Math.PI / 180;
  const cos = Math.cos(angle);
  const sin = Math.sin(angle);

  return localMeterPolygon([
    [-halfW, -halfD],
    [halfW, -halfD],
    [halfW, halfD],
    [-halfW, halfD],
  ].map(([x, y]) => [
    x * cos - y * sin,
    x * sin + y * cos,
  ]));
}

describe('geoUtils map-meter footprint helpers', () => {
  it('computes area for a 10m by 10m drawn footprint', () => {
    const square = rectangle(10, 10);
    const dimensions = polygonDimensionsMeters(square);

    expect(polygonAreaM2(square)).toBeCloseTo(100, 0);
    expect(dimensions.area).toBeCloseTo(100, 0);
    expect(dimensions.width).toBeCloseTo(10, 0);
    expect(dimensions.depth).toBeCloseTo(10, 0);
  });

  it('reports oriented dimensions for a rotated footprint', () => {
    const footprint = rectangle(40, 20, 31);
    const dimensions = polygonDimensionsMeters(footprint);

    expect(dimensions.area).toBeCloseTo(800, 0);
    expect(dimensions.width).toBeCloseTo(40, 0);
    expect(dimensions.depth).toBeCloseTo(20, 0);
  });
});
