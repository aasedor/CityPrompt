import { describe, expect, it } from 'vitest';

import { fitSkateParkV0Program, SKATE_PARK_V0_PROGRAM } from './skateParkFit';

function rotate(points: Array<{ x: number; y: number }>, angle: number) {
  const cos = Math.cos(angle);
  const sin = Math.sin(angle);
  return points.map(({ x, y }) => ({ x: x * cos - y * sin, y: x * sin + y * cos }));
}

describe('Skate Park v0 site fit', () => {
  it('centres the exact 40 x 30 m kit in the current 44 x 36 m pilot zone', () => {
    const fit = fitSkateParkV0Program([
      { x: -22, y: -18 },
      { x: 22, y: -18 },
      { x: 22, y: 18 },
      { x: -22, y: 18 },
    ]);

    expect(fit).toMatchObject({
      center: { x: 0, y: 0 },
      widthM: 40,
      depthM: 30,
      clearanceM: 0.5,
      scale: 1,
    });
    expect(fit?.rotationRad).toBeCloseTo(0, 7);
  });

  it('follows a rotated parcel without scaling the archetype', () => {
    const angle = Math.PI / 6;
    const fit = fitSkateParkV0Program(rotate([
      { x: -22, y: -18 },
      { x: 22, y: -18 },
      { x: 22, y: 18 },
      { x: -22, y: 18 },
    ], angle));

    expect(fit).not.toBeNull();
    expect(fit?.scale).toBe(1);
    expect(fit?.widthM).toBe(SKATE_PARK_V0_PROGRAM.widthM);
    expect(Math.abs((fit?.rotationRad ?? 0) - angle)).toBeLessThan(1e-6);
  });

  it('rejects a concave parcel whose bounds cannot contain the whole kit', () => {
    const fit = fitSkateParkV0Program([
      { x: -22, y: -18 },
      { x: -6, y: -18 },
      { x: -6, y: 8 },
      { x: 6, y: 8 },
      { x: 6, y: -18 },
      { x: 22, y: -18 },
      { x: 22, y: 18 },
      { x: -22, y: 18 },
    ]);

    expect(fit).toBeNull();
  });
});
