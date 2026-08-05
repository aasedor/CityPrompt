import { describe, expect, it } from 'vitest';

import {
  MAX_PARK_SPECIALTY_TERRAIN_ANCHORS,
  buildGreenwayGatewayBollardAnchors,
  buildParkSpecialtyTerrainAnchors,
  resolveStormwaterInfrastructureGuides,
} from './parkSpecialtyGeometry';

const frame = {
  minX: -50,
  maxX: 50,
  minY: -20,
  maxY: 20,
  width: 100,
  height: 40,
};

describe('park specialty geometry', () => {
  it('aligns greenway gateway bollards to the first segment normal outside the clear route', () => {
    const route = [{ x: -10, y: -4 }, { x: 10, y: 6 }];
    const anchors = buildGreenwayGatewayBollardAnchors(route, 3.5, 0.45);
    expect(anchors).toHaveLength(2);
    const dx = route[1].x - route[0].x;
    const dy = route[1].y - route[0].y;
    for (const anchor of anchors) {
      const offsetX = anchor.x - route[0].x;
      const offsetY = anchor.y - route[0].y;
      expect(Math.abs(offsetX * dx + offsetY * dy)).toBeLessThan(1e-7);
      expect(Math.hypot(offsetX, offsetY)).toBeCloseTo(2.2, 7);
    }
  });

  it('uses bounded actual route and fixed-program anchors for terrain contact', () => {
    const greenway = buildParkSpecialtyTerrainAnchors('greenway_edge_assembly', [{
      kind: 'polyline',
      x: 0.5,
      y: 0.5,
      width: 1,
      height: 1,
      points: [[0.05, 0.2], [0.45, 0.7], [0.95, 0.35]],
      strokeWidthM: 3.5,
      color: '#fff',
    }], frame);
    expect(greenway.length).toBeGreaterThanOrEqual(7);
    expect(greenway.some(({ x, y }) => x === -45 && y === 12)).toBe(true);

    const stormwater = buildParkSpecialtyTerrainAnchors('stormwater_control_assembly', [{
      kind: 'ellipse', x: 0.45, y: 0.52, width: 0.58, height: 0.42, color: '#fff',
    }, {
      kind: 'rectangle', x: 0.8, y: 0.5, width: 0.08, height: 0.12, color: '#fff',
    }], frame);
    expect(stormwater.length).toBeGreaterThanOrEqual(10);
    expect(stormwater.length).toBeLessThanOrEqual(MAX_PARK_SPECIALTY_TERRAIN_ANCHORS);

    const skate = buildParkSpecialtyTerrainAnchors('skate_park_v0_assembly', [], {
      minX: -22,
      maxX: 22,
      minY: -18,
      maxY: 18,
      width: 44,
      height: 36,
      points: [
        { x: -22, y: -18 },
        { x: 22, y: -18 },
        { x: 22, y: 18 },
        { x: -22, y: 18 },
      ],
    });
    expect(skate).toHaveLength(5);
    expect(skate).toContainEqual({ x: -20, y: -15 });
    expect(skate).toContainEqual({ x: 20, y: 15 });
  });

  it('keeps fitted stormwater inlet and outlet centers and dimensions authoritative', () => {
    const resolved = resolveStormwaterInfrastructureGuides([{
      kind: 'rectangle', x: 0.16, y: 0.62, width: 0.08, height: 0.15, color: '#fff',
      rotationDeg: 12,
    }, {
      kind: 'rectangle', x: 0.84, y: 0.41, width: 0.05, height: 0.11, color: '#fff',
      widthM: 6.5,
      heightM: 3.25,
    }], frame);

    expect(resolved).not.toBeNull();
    expect(resolved?.inlet.center).toEqual({ x: -34, y: -4.800000000000001 });
    expect(resolved?.inlet.width).toBeCloseTo(8);
    expect(resolved?.inlet.height).toBeCloseTo(6);
    expect(resolved?.inlet.rotationRad).toBeCloseTo(-12 * Math.PI / 180);
    expect(resolved?.outlet.center).toEqual({ x: 34, y: 3.6000000000000014 });
    expect(resolved?.outlet.width).toBe(6.5);
    expect(resolved?.outlet.height).toBe(3.25);
  });
});
