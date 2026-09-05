import { describe, expect, it } from 'vitest';
import { buildNeighborhoodParkLayout, envelopeFits, envelopesOverlap, type ParkPoint } from './neighborhoodParkLayout';

const rectangle = (w: number, h: number): ParkPoint[] => [{ x: 0, y: 0 }, { x: w, y: 0 }, { x: w, y: h }, { x: 0, y: h }];
describe('reference-locked neighbourhood park composition', () => {
  for (const [w, h] of [[40, 35], [70, 55], [105, 75]]) it(`composes ${w} × ${h} m without stretching or overlapping equipment`, () => {
    const boundary = rectangle(w, h), layout = buildNeighborhoodParkLayout(boundary);
    expect(layout.loop).toHaveLength(64);
    expect(layout.modules.length).toBeGreaterThanOrEqual(w < 70 ? 2 : 3);
    if (w >= 70) expect(layout.status).toBe('full');
    else { expect(layout.status).toBe('compact'); expect(layout.modules.filter(m => m.kind === 'tower')).toHaveLength(1); }
    expect(layout.modules.filter(m => m.kind === 'pavilion')).toHaveLength(1);
    expect(layout.paths).toHaveLength(layout.modules.length);
    for (const module of layout.modules) {
      expect(envelopeFits(module.envelope, boundary, .79)).toBe(true);
      expect(envelopesOverlap(module.envelope, layout.lawn)).toBe(false);
      expect(module.width).toBe(module.kind === 'tower' ? 12 : module.kind === 'swing' ? 8 : 10);
      expect(module.arrival).toBeDefined();
      expect(Math.hypot(module.arrival!.x - module.center.x, module.arrival!.y - module.center.y)).toBeGreaterThanOrEqual(3.7);
      for (const other of layout.modules) if (other !== module) expect(envelopesOverlap(module.envelope, other.envelope)).toBe(false);
    }
  });
  it('fits an L-shaped lot and retains rotation and repeatability', () => {
    const boundary = [{ x: 0, y: 0 }, { x: 80, y: 0 }, { x: 80, y: 30 }, { x: 55, y: 30 }, { x: 55, y: 60 }, { x: 0, y: 60 }];
    const theta = .37, rotated = boundary.map(p => ({ x: p.x * Math.cos(theta) - p.y * Math.sin(theta), y: p.x * Math.sin(theta) + p.y * Math.cos(theta) }));
    const layout = buildNeighborhoodParkLayout(rotated);
    expect(layout.modules.length).toBeGreaterThanOrEqual(3);
    for (const module of layout.modules) expect(envelopeFits(module.envelope, rotated, .79)).toBe(true);
    expect(buildNeighborhoodParkLayout(rotated)).toEqual(layout);
  });
  it('reports an unusable footprint instead of shrinking a playground', () => {
    const layout = buildNeighborhoodParkLayout(rectangle(8, 80));
    expect(layout.status).toBe('constrained');
    expect(layout.modules).toHaveLength(0);
    expect(layout.notes.join(' ')).toContain('too narrow');
  });
  it('rejects envelopes crossing a concave boundary even with all corners inside', () => {
    const u = [{ x: 0, y: 0 }, { x: 20, y: 0 }, { x: 20, y: 20 }, { x: 13, y: 20 }, { x: 13, y: 7 }, { x: 7, y: 7 }, { x: 7, y: 20 }, { x: 0, y: 20 }];
    expect(envelopeFits([{ x: 3, y: 10 }, { x: 17, y: 10 }, { x: 17, y: 16 }, { x: 3, y: 16 }], u)).toBe(false);
  });
});
