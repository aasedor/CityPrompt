import { describe, expect, it } from 'vitest';
import { buildNeighborhoodParkLayout, neighborhoodParkLayoutForZone, envelopeFits, envelopesOverlap, type ParkPoint } from './neighborhoodParkLayout';
import {metersPerDegLon,METERS_PER_DEG_LAT} from '../mapEngine/geoUtils';
import type {SiteZone} from '@/types';

const rectangle = (w: number, h: number): ParkPoint[] => [{ x: 0, y: 0 }, { x: w, y: 0 }, { x: w, y: h }, { x: 0, y: h }];
describe('reference-locked neighbourhood park composition', () => {
  it.each([30,40])('uses the same world geometry from a park, building or capture origin (%s m)',width=>{
    const zone={coordinates:rectangle(width,width).map(p=>[-114+p.x/metersPerDegLon(51),51+p.y/METERS_PER_DEG_LAT])} as SiteZone;
    const origins=[{lng:-114,lat:51},{lng:-114.002,lat:51.001},{lng:-113.9998,lat:51.0001}];
    const world=origins.map(origin=>{const layout=neighborhoodParkLayoutForZone(zone,origin);return [...layout.loop,...layout.trees,...layout.modules.flatMap(m=>[m.center,...m.envelope])].map(p=>[origin.lng+p.x/metersPerDegLon(origin.lat),origin.lat+p.y/METERS_PER_DEG_LAT]);});
    for(const points of world.slice(1)){
      expect(points).toHaveLength(world[0].length);
      points.forEach((p,i)=>{expect(p[0]).toBeCloseTo(world[0][i][0],10);expect(p[1]).toBeCloseTo(world[0][i][1],10);});
    }
  });
  it.each([30,31,32])('keeps a contained walking loop at the advertised 30 m minimum (%s m depth)', depth => {
    const boundary=rectangle(40,depth),layout=buildNeighborhoodParkLayout(boundary);
    expect(layout.loop).toHaveLength(64);
    expect(envelopeFits(layout.loop,boundary,layout.pathWidth/2)).toBe(true);
    expect(layout.notes.join(' ')).toContain('Compact arrangement');
  });
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
  it('keeps a narrow plot as landscape without shrinking a playground', () => {
    const layout = buildNeighborhoodParkLayout(rectangle(8, 80));
    expect(layout.status).toBe('constrained');
    expect(layout.modules).toHaveLength(0);
    expect(layout.trees.length+layout.shrubs.length).toBeGreaterThan(0);
    expect(layout.notes.join(' ')).toContain('you can keep this landscape layout');
  });
  it('rejects envelopes crossing a concave boundary even with all corners inside', () => {
    const u = [{ x: 0, y: 0 }, { x: 20, y: 0 }, { x: 20, y: 20 }, { x: 13, y: 20 }, { x: 13, y: 7 }, { x: 7, y: 7 }, { x: 7, y: 20 }, { x: 0, y: 20 }];
    expect(envelopeFits([{ x: 3, y: 10 }, { x: 17, y: 10 }, { x: 17, y: 16 }, { x: 3, y: 16 }], u)).toBe(false);
  });
});
