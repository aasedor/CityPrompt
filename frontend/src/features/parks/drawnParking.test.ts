import { describe, expect, it } from 'vitest';
import clipping from 'polygon-clipping';
import { drawnParkingLayout, drawnParkingProperties, isDrawnParking } from './drawnParking';

const outline = [[0, 0], [18, 0], [18, 40], [0, 40]];
describe('parking drawn like a ground surface', () => {
  it('chooses the direction with more usable stalls automatically', () => {
    const layout = drawnParkingLayout(outline, 'auto');
    expect(layout.spaces).toHaveLength(24);
    expect(layout.aisles.length).toBeGreaterThan(0);
    expect(layout.problem).toBeNull();
  });
  it('keeps fixed dimensions when resized and rotated instead of stretching the paint', () => {
    const rotated = outline.map(([x, y]) => [x * .8 - y * .6, x * .6 + y * .8]);
    const layout = drawnParkingLayout(rotated, 'auto');
    expect(layout.spaces).toHaveLength(24);
    const p = layout.spaces[0].corners;
    expect(Math.hypot(p[1][0] - p[0][0], p[1][1] - p[0][1])).toBeCloseTo(2.7);
    expect(Math.hypot(p[2][0] - p[1][0], p[2][1] - p[1][1])).toBeCloseTo(5.5);
    expect(drawnParkingLayout([[0, 0], [18, 0], [18, 30], [0, 30]], 'auto').spaces).toHaveLength(16);
  });
  it('does not change rows merely because the same ring is closed, reversed or starts at another corner', () => {
    const original = drawnParkingLayout(outline, 'auto');
    const reordered = [...outline.slice(2), ...outline.slice(0, 2)].reverse();
    reordered.push(reordered[0]);
    expect(drawnParkingLayout(reordered, 'auto')).toEqual(original);
  });
  it('keeps every stall and drive aisle inside a concave lot', () => {
    const ring = [[0, 0], [40, 0], [40, 18], [20, 18], [20, 35], [0, 35]];
    const layout = drawnParkingLayout(ring, 'auto');
    expect(layout.spaces.length).toBeGreaterThan(0);
    for (const polygon of [...layout.spaces.map(s => s.corners), ...layout.aisles]) {
      expect(clipping.difference([polygon as [number, number][]], [ring as [number, number][]])).toEqual([]);
    }
  });
  it('reports a narrow lot without inventing undersized stalls and bounds oversized input', () => {
    const narrow = drawnParkingLayout([[0, 0], [8, 0], [8, 8], [0, 8]], 'auto');
    expect(narrow.spaces).toHaveLength(0);
    expect(narrow.problem).toBeTruthy();
    expect(drawnParkingLayout([[0, 0], [500, 0], [500, 500], [0, 500]], 'auto').spaces).toHaveLength(0);
    expect(drawnParkingLayout([], 'auto').spaces).toHaveLength(0);
  });
  it('uses a single row with a real drive lane where a double row cannot fit', () => {
    const lot = drawnParkingLayout([[0, 0], [30, 0], [30, 12.5], [0, 12.5]], 'auto');
    expect(lot.spaces).toHaveLength(8);
    expect(lot.aisles).toHaveLength(2);
    expect(lot.aisles[1][2][1] - lot.aisles[1][1][1]).toBeCloseTo(6);
  });
  it('fits a hand-drawn slightly skewed lot instead of leaving almost all of its asphalt empty', () => {
    const ring = [[0, 0], [83.83237, .87554], [84.49546, -27.19281], [1.67596, -28.39105]];
    expect(drawnParkingLayout(ring, 'auto').spaces.length).toBeGreaterThanOrEqual(40);
  });
  it('identifies only the new asphalt parking recipe and preserves older parking/plaza zones', () => {
    expect(isDrawnParking({ properties: drawnParkingProperties() })).toBe(true);
    expect(isDrawnParking({ properties: {} })).toBe(false);
    expect(isDrawnParking({ properties: { ground_surface_material: 'asphalt' } })).toBe(false);
  });
});
