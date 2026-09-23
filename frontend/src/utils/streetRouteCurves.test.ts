import { describe, expect, it } from 'vitest';
import { bufferLineToPolygon, extractCenterline } from './roadGeometry';
import { roundAuthoredStreetRoute, roundMetricStreetCenterline, roundStreetCenterline } from './streetRouteCurves';

const mLon = 111320 * Math.cos(51 * Math.PI / 180);
const ll = ([x, y]: number[]) => [-114 + x / mLon, 51 + y / 111320];
const xy = ([lng, lat]: number[]) => [(lng + 114) * mLon, (lat - 51) * 111320];

describe('concept street curves', () => {
  it('rounds a square bend with a tangent circular arc and fixed connection ends', () => {
    const controls = [[0, 0], [60, 0], [60, 60]];
    const line = roundMetricStreetCenterline(controls, 24);
    expect(line.length).toBeGreaterThan(15);
    expect(line[0]).toEqual(controls[0]);
    expect(line[line.length - 1]).toEqual(controls[controls.length - 1]);
    expect(line.some(([x, y]) => Math.abs(x - 36) < .01 && Math.abs(y) < .01)).toBe(true);
    expect(line.some(([x, y]) => Math.abs(x - 60) < .01 && Math.abs(y - 24) < .01)).toBe(true);
    expect(line.every(([x, y]) => x >= -1e-8 && x <= 60 + 1e-8 && y >= -1e-8 && y <= 60 + 1e-8)).toBe(true);
    const bearings = line.slice(1).map(([x, y], i) => Math.atan2(y - line[i][1], x - line[i][0]));
    expect(Math.max(...bearings.slice(1).map((angle, i) => Math.abs(angle - bearings[i])))).toBeLessThan(.11);
  });

  it('keeps an S route smooth and a saved ROW paired around the same centreline', () => {
    const controls = [[0, 0], [45, 0], [80, 35], [125, 35]];
    const curved = roundStreetCenterline(controls.map(ll), 30);
    const polygon = bufferLineToPolygon(curved, 20);
    const recovered = extractCenterline(polygon).map(xy);
    expect(curved[0]).toEqual(controls.map(ll)[0]);
    expect(curved[curved.length - 1]).toEqual(ll(controls[controls.length - 1]));
    expect(polygon).toHaveLength(curved.length * 2);
    recovered.forEach(([x, y], index) => {
      const [cx, cy] = xy(curved[index]);
      expect(Math.hypot(x - cx, y - cy)).toBeLessThan(.001);
    });
    expect(roundAuthoredStreetRoute(controls.map(ll), 20)).toHaveLength(curved.length);
  });

  it('bounds tight transitions by their available arms and leaves straight routes untouched', () => {
    const short = roundMetricStreetCenterline([[0, 0], [20, 0], [20, 20]], 100);
    expect(short.every(([x, y]) => x >= -1e-8 && x <= 20 + 1e-8 && y >= -1e-8 && y <= 20 + 1e-8)).toBe(true);
    expect(roundMetricStreetCenterline([[0, 0], [60, 0]], 30)).toEqual([[0, 0], [60, 0]]);
    expect(roundMetricStreetCenterline([[0, 0], [30, 0], [60, 0]], 30)).toEqual([[0, 0], [30, 0], [60, 0]]);
  });
});
