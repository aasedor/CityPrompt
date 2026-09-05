import { describe, expect, it } from 'vitest';
import { createMeadowPatch } from './parkPlantingGeometry';
import { buildNeighborhoodParkLayout, envelopeFits } from './neighborhoodParkLayout';

describe('metric planting envelopes', () => {
  it('keeps the actual shared plant mesh inside every reserved planting footprint', () => {
    const mesh = createMeadowPatch();
    const p = mesh.getAttribute('position');
    let radius = 0;
    for (let i = 0; i < p.count; i++) {
      radius = Math.max(radius, Math.hypot(p.getX(i), p.getY(i)) * 1.08);
      expect(p.getZ(i)).toBeGreaterThanOrEqual(0);
      expect(p.getZ(i)).toBeLessThan(.7);
    }
    expect(radius).toBeLessThan(1.1);
    for (const [width, depth] of [[40, 35], [70, 55], [105, 75]]) {
      const boundary = [{x:0,y:0},{x:width,y:0},{x:width,y:depth},{x:0,y:depth}];
      const layout = buildNeighborhoodParkLayout(boundary);
      for (const point of layout.shrubs) {
        const edge = Array.from({length:24}, (_,i) => ({x:point.x+Math.cos(i*Math.PI/12)*radius,y:point.y+Math.sin(i*Math.PI/12)*radius}));
        expect(envelopeFits(edge,boundary,0)).toBe(true);
      }
      for (const point of layout.trees) {
        const edge = Array.from({length:24}, (_,i) => ({x:point.x+Math.cos(i*Math.PI/12)*3.24,y:point.y+Math.sin(i*Math.PI/12)*3.24}));
        expect(envelopeFits(edge,boundary,0)).toBe(true);
      }
    }
    mesh.dispose();
  });
});
