import { describe, expect, it } from 'vitest';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { resolveBuildingGroundContact, type GroundPoint } from './buildingGroundContact';
import { buildBuildingEntranceApproach } from './buildingEntranceApproach';

const lng = -114, lat = 51;
const geo = ([x, y]: number[]): GroundPoint => [lng + x / metersPerDegLon(lat), lat + y / METERS_PER_DEG_LAT];
const footprints: GroundPoint[][] = [[[-5, -4], [5, -4], [5, 4], [-5, 4]]];
const ground = {
  status: 'ready', contains: () => true,
  heightAt: (x: number) => 100 + Math.max(0, 5 - (x - lng) * metersPerDegLon(lat)) * .2,
};
const contact = resolveBuildingGroundContact(footprints, lng, lat, ground);
const strip = { id: 'entrance:house', ownerId: 'house', start: geo([11, 0]), end: geo([5, 0]),
  widthM: 1.8, startLiftM: .025, endLiftM: .025, color: '#aaa' };
const input = { contact, footprints, lng, lat, ground, strip, heightAboveBaseM: 0 };

describe('entrances on generated foundations', () => {
  it('meets the actual elevated building base instead of draping the entrance onto the terrain below it', () => {
    const result = buildBuildingEntranceApproach(input);
    expect(result.status).toBe('ready');
    if (result.status !== 'ready') return;
    expect(result.steps).toBeGreaterThan(1);
    expect(result.endHeightM).toBeCloseTo(102.04);
    expect(result.startHeightM).toBeCloseTo(100.025);
    expect(result.positions.filter((_, i) => i % 3 === 2)).toContain(0);
    expect(result.positions.every(Number.isFinite)).toBe(true);
    for (let vertex=0;vertex<result.positions.length;vertex+=6) {
      const underside=result.positions[vertex+2],top=result.positions[vertex+5];
      expect(top-underside).toBeGreaterThanOrEqual(0);
      expect(top-underside).toBeLessThanOrEqual(.24+1e-6);
    }
    // Two continuous stringers reach both ends of the run while the earlier
    // full-polygon checks still gate the terrain below every tread.
    const beams=result.positions.slice(-16*3);
    expect(Math.min(...beams.filter((_,i)=>i%3===0))).toBeCloseTo(5,3);
    expect(Math.max(...beams.filter((_,i)=>i%3===0))).toBeCloseTo(11,3);
  });
  it('keeps the native model and authored route immutable', () => {
    const before = JSON.stringify(input);
    buildBuildingEntranceApproach(input);
    expect(JSON.stringify(input)).toBe(before);
  });
  it('rejects an anchor inside the foundation instead of drawing stairs through its cap', () => {
    expect(buildBuildingEntranceApproach({ ...input, strip: { ...strip, end: geo([3, 0]) } }))
      .toMatchObject({ status: 'unresolved', reason: 'entrance_anchor_not_at_edge' });
  });
  it('rejects a route through another detached foundation', () => {
    expect(buildBuildingEntranceApproach({ ...input, footprints: [...footprints, [[7,-2],[9,-2],[9,2],[7,2]]] }))
      .toMatchObject({ status: 'unresolved', reason: 'entrance_approach_obstructed' });
  });
  it('rejects inadequate stair run rather than inventing steep or overlapping treads', () => {
    expect(buildBuildingEntranceApproach({ ...input, strip: { ...strip, start: geo([6, 0]) } }))
      .toMatchObject({ status: 'unresolved', reason: 'entrance_approach_too_short' });
  });
  it('requires support across the entire approach, including narrow site notches', () => {
    const boundary = [[-20,-20],[20,-20],[20,-.05],[8,-.05],[8,.05],[20,.05],[20,20],[-20,20]];
    const bounded = { ...ground, boundaryCoordinates: boundary.map(geo), contains: (x: number, y: number) => {
      const localX = (x-lng)*metersPerDegLon(lat), localY=(y-lat)*METERS_PER_DEG_LAT;
      return localX < 8 || Math.abs(localY) > .05;
    } };
    expect(buildBuildingEntranceApproach({ ...input, ground: bounded })).toMatchObject({ status: 'unresolved' });
  });
  it('does not guess an elevation while ground or the building is unresolved', () => {
    expect(buildBuildingEntranceApproach({ ...input, contact: { status: 'unresolved' } })).toMatchObject({ status: 'unresolved' });
    expect(buildBuildingEntranceApproach({ ...input, ground: { ...ground, status: 'sampling' } })).toMatchObject({ status: 'unresolved' });
    expect(buildBuildingEntranceApproach({ ...input, ground: { ...ground, heightAt: () => null } })).toMatchObject({ status: 'unresolved' });
  });
  it('rejects terrain protruding through a tread rather than hiding a ridge', () => {
    expect(buildBuildingEntranceApproach({ ...input, ground: { ...ground, heightAt: () => 104 } }))
      .toMatchObject({ status: 'unresolved' });
  });
  it('keeps a measured entrance offset above the native base', () => {
    const result = buildBuildingEntranceApproach({ ...input, heightAboveBaseM: .18 });
    expect(result.status).toBe('ready');
    if (result.status !== 'ready') return;
    expect(result.endHeightM).toBeCloseTo(102.22);
    expect(Math.max(...result.positions.filter((_, i) => i % 3 === 2))).toBeCloseTo(.18);
  });
  it('supports a descending approach from an uphill street', () => {
    const uphill = { ...ground, heightAt: (x: number) => 100 + Math.max(0, (x-lng)*metersPerDegLon(lat)-5)*.2 };
    const result = buildBuildingEntranceApproach({ ...input, ground: uphill,
      contact: resolveBuildingGroundContact(footprints,lng,lat,uphill) });
    expect(result.status).toBe('ready');
    if (result.status !== 'ready') return;
    expect(result.startHeightM).toBeCloseTo(101.225);
    expect(result.endHeightM).toBeCloseTo(100.04);
    expect(result.steps).toBe(7);
  });
  it('preserves approach elevation and run after rotating the house and route together', () => {
    const angle = 95*Math.PI/180;
    const rotate = ([x,y]: GroundPoint): GroundPoint => [x*Math.cos(angle)-y*Math.sin(angle),x*Math.sin(angle)+y*Math.cos(angle)];
    const rotatedGround = { ...ground, heightAt: (x: number,y: number) => {
      const east=(x-lng)*metersPerDegLon(lat),north=(y-lat)*METERS_PER_DEG_LAT;
      return 100+Math.max(0,5-east*Math.cos(angle)-north*Math.sin(angle))*.2;
    } };
    const rotatedPads=footprints.map(ring=>ring.map(rotate));
    const result=buildBuildingEntranceApproach({ ...input, footprints:rotatedPads,ground:rotatedGround,
      contact:resolveBuildingGroundContact(rotatedPads,lng,lat,rotatedGround),
      strip:{...strip,start:geo(rotate([11,0])),end:geo(rotate([5,0]))} });
    expect(result.status).toBe('ready');
    if (result.status !== 'ready') return;
    expect(result.startHeightM).toBeCloseTo(100.025);
    expect(result.endHeightM).toBeCloseTo(102.04);
    expect(result.steps).toBe(12);
  });
  it('rejects a non-finite street elevation instead of certifying empty geometry', () => {
    expect(buildBuildingEntranceApproach({ ...input, strip: { ...strip, startLiftM: NaN } }))
      .toMatchObject({ status: 'unresolved', reason: 'entrance_height_invalid' });
  });
});
