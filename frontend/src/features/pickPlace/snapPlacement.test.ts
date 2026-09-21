import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';
import { placementProblem, rectangleAt, rectangleDimensions } from './geometry';
import { snapPlacement } from './snapPlacement';

const ll = (x: number, y: number) => [-114 + x/metersPerDegLon(51),51 + y/METERS_PER_DEG_LAT];
const zone = (id: string, coords: number[][], zone_type: SiteZone['zone_type'] = 'building') => ({id, coordinates:coords, zone_type,properties:{}} as SiteZone);
const site = zone('site',rectangleAt(ll(0,0),100,100),'site_boundary');
describe('ideation placement snapping',()=>{
  it('leaves clear placements exactly unchanged',()=>{
    const coords=rectangleAt(ll(20,0),12,16);
    expect(snapPlacement(coords,[],site)).toEqual({coordinates:coords,snapped:false,problem:null});
  });
  it('settles immediately beside a neighbour, preserving size and angle',()=>{
    const other=zone('other',rectangleAt(ll(0,0),12,16));
    const result=snapPlacement(rectangleAt(ll(10,0),12,16),[other],site);
    expect(result.problem).toBeNull();
    expect(result.snapped).toBe(true);
    const d=rectangleDimensions(result.coordinates);
    expect((d.center[0]+114)*metersPerDegLon(51)).toBeCloseTo(12.02,2);
    expect(d.width).toBeCloseTo(12,3);expect(d.depth).toBeCloseTo(16,3);
  });
  it('finds space around rotated neighbours and checks every other plot',()=>{
    const neighbours=[zone('a',rectangleAt(ll(0,0),14,20,35)),zone('b',rectangleAt(ll(17,0),12,16))];
    const result=snapPlacement(rectangleAt(ll(7,2),12,16,-20),neighbours,site);
    expect(result.problem).toBeNull();
    expect(placementProblem(result.coordinates,neighbours,site)).toBeNull();
    expect(rectangleDimensions(result.coordinates).degrees).toBeCloseTo(-20,3);
  });
  it('moves inward at the site edge without overlapping a neighbour',()=>{
    const neighbours=[zone('a',rectangleAt(ll(40,0),12,16))];
    const result=snapPlacement(rectangleAt(ll(48,1),12,16),neighbours,site);
    expect(result.problem).toBeNull();
    expect(placementProblem(result.coordinates,neighbours,site)).toBeNull();
  });
  it('respects a concave site and cannot jump across its missing notch',()=>{
    const concave=zone('site',[ll(-40,-40),ll(40,-40),ll(40,0),ll(0,0),ll(0,40),ll(-40,40)],'site_boundary');
    const result=snapPlacement(rectangleAt(ll(2,2),12,16),[],concave);
    expect(result.problem).toBeNull();
    expect(placementProblem(result.coordinates,[],concave)).toBeNull();
  });
  it('ignores the moving object and refuses impossible spaces',()=>{
    const coords=rectangleAt(ll(0,0),12,16),self=zone('self',coords);
    expect(snapPlacement(coords,[self],site,'self').snapped).toBe(false);
    expect(snapPlacement(coords,[],zone('tiny',rectangleAt(ll(0,0),5,5),'site_boundary')).problem).toBeTruthy();
  });
});
