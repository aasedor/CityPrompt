import { describe, expect, it } from 'vitest';
import { projectedBoundsIntersectFrame } from './renderZoneVisibility';

describe('render-zone frame visibility', () => {
  it('keeps polygons inside, crossing, or enclosing the frame', () => {
    expect(projectedBoundsIntersectFrame([{ x: 50, y: 50 }], 100, 100)).toBe(true);
    expect(projectedBoundsIntersectFrame([{ x: -20, y: 50 }, { x: 20, y: 50 }], 100, 100, 0)).toBe(true);
    expect(projectedBoundsIntersectFrame([
      { x: -50, y: -50 },
      { x: 150, y: 150 },
    ], 100, 100, 0)).toBe(true);
  });

  it('drops zones wholly outside the captured frame', () => {
    expect(projectedBoundsIntersectFrame([
      { x: 180, y: 20 },
      { x: 240, y: 80 },
    ], 100, 100, 10)).toBe(false);
    expect(projectedBoundsIntersectFrame([
      { x: 20, y: -120 },
      { x: 80, y: -80 },
    ], 100, 100, 10)).toBe(false);
  });

  it('uses a bounded margin and rejects invalid inputs', () => {
    expect(projectedBoundsIntersectFrame([{ x: 110, y: 50 }], 100, 100, 12)).toBe(true);
    expect(projectedBoundsIntersectFrame([{ x: 110, y: 50 }], 100, 100, 0)).toBe(false);
    expect(projectedBoundsIntersectFrame([{ x: Number.NaN, y: 50 }], 100, 100)).toBe(false);
    expect(projectedBoundsIntersectFrame([{ x: 10, y: 10 }], 0, 100)).toBe(false);
  });
});
