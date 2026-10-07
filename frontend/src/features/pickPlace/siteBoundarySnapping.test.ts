import { describe,expect,it } from 'vitest';
import type { SiteZone } from '@/types';
import { METERS_PER_DEG_LAT,metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';
import { placementProblem,rectangleAt,rectangleDimensions } from './geometry';
import { snapFootprintToSiteBoundary } from './siteBoundarySnapping';
import { snapPlacement } from './snapPlacement';

const ll=(x:number,y:number)=>[-114+x/metersPerDegLon(51),51+y/METERS_PER_DEG_LAT];
const site={id:'site',zone_type:'site_boundary',coordinates:rectangleAt(ll(0,0),100,100)} as SiteZone;
const snap=(coords:number[][],boundary=site,others:SiteZone[]=[])=>snapFootprintToSiteBoundary(coords,boundary,next=>!placementProblem(next,others,boundary));
const xy=(point:number[])=>[(point[0]+114)*metersPerDegLon(51),(point[1]-51)*METERS_PER_DEG_LAT];

describe('complete footprint boundary snapping',()=>{
 it.each([0,90,180,270])('closes a nearby inside gap at %s degrees',angle=>{
  const radians=angle*Math.PI/180,coords=rectangleAt(ll(42*Math.cos(radians),42*Math.sin(radians)),12,12,angle);
  const result=snap(coords),d=rectangleDimensions(result);
  expect(result).not.toEqual(coords);expect(placementProblem(result,[],site)).toBeNull();
  expect(Math.hypot(...xy(d.center))).toBeCloseTo(43.92,2);
  expect(d.width).toBeCloseTo(12,4);expect(d.depth).toBeCloseTo(12,4);
  expect(snap(result)).toBe(result);
 });
 it('repairs a small edge and corner overhang without changing size or angle',()=>{
  for(const center of [ll(46,0),ll(46,46)]) {
   const coords=rectangleAt(center,12,12),result=snap(coords),d=rectangleDimensions(result);
   expect(placementProblem(result,[],site)).toBeNull();
   expect(xy(d.center)[0]).toBeCloseTo(43.92,2);
   if(center[1]!==51)expect(xy(d.center)[1]).toBeCloseTo(43.92,2);
   expect(d.width).toBeCloseTo(12,4);expect(d.depth).toBeCloseTo(12,4);expect(d.degrees).toBeCloseTo(0,4);
  }
 });
 it('handles reversed, rotated boundaries and rotated objects',()=>{
  const angle=28,rad=angle*Math.PI/180,turn=(point:number[])=>{const [x,y]=xy(point);return ll(x*Math.cos(rad)-y*Math.sin(rad),x*Math.sin(rad)+y*Math.cos(rad));};
  const boundary={...site,coordinates:site.coordinates.map(turn).reverse()},coords=rectangleAt(turn(ll(46,0)),12,12,angle),result=snap(coords,boundary);
  expect(placementProblem(result,[],boundary)).toBeNull();
  expect(rectangleDimensions(result).degrees).toBeCloseTo(angle,4);
  expect(snap(result,boundary)).toBe(result);
 });
 it('does not oscillate between opposite edges of a narrow parcel',()=>{
  const boundary={...site,coordinates:rectangleAt(ll(0,0),9,100)},result=snap(rectangleAt(ll(0,0),6,12),boundary);
  expect(snap(result,boundary)).toBe(result);
 });
 it('solves an oblique corner while retaining the first edge contact',()=>{
  const boundary={...site,coordinates:[ll(-50,-50),ll(50,-50),ll(35,50),ll(-50,50)]};
  const coords=rectangleAt(ll(29,46),12,12),result=snap(coords,boundary);
  expect(placementProblem(result,[],boundary)).toBeNull();
  expect(snap(result,boundary)).toBe(result);
  const d=rectangleDimensions(result);
  expect(d.width).toBeCloseTo(12,4);expect(d.depth).toBeCloseTo(12,4);
  expect(xy(d.center)[1]+6).toBeCloseTo(49.92,2);
 });
 it('retains clear remote placements, invalid coordinates and impossible footprints',()=>{
  for(const coords of [rectangleAt(ll(0,0),12,12),rectangleAt(ll(50,0),12,12),rectangleAt(ll(0,0),110,12),[[NaN,51],ll(0,1),ll(1,0)]])
   expect(snap(coords)).toBe(coords);
  const coords=rectangleAt(ll(42,0),12,12);expect(snapFootprintToSiteBoundary(coords,null,()=>true)).toBe(coords);
 });
 it('preserves concave containment and refuses to snap across an occupied boundary edge',()=>{
  const boundary={...site,coordinates:[ll(-50,-50),ll(50,-50),ll(50,0),ll(0,0),ll(0,50),ll(-50,50)]};
  const coords=rectangleAt(ll(2,30),12,12);expect(snap(coords,boundary)).toBe(coords);
  const blocked={id:'block',zone_type:'building',coordinates:rectangleAt(ll(49,0),2,20),properties:{}} as SiteZone;
  const clear=rectangleAt(ll(42,0),12,12);expect(snap(clear,site,[blocked])).toBe(clear);
 });
 it.each(['building','green_space'] as const)('uses the full %s plot with shared collision checks',zoneType=>{
  const result=snapPlacement(rectangleAt(ll(42,0),12,12),[],site,undefined,{},zoneType);
  expect(result.problem).toBeNull();expect(result.snapped).toBe(true);
  expect(xy(rectangleDimensions(result.coordinates).center)[0]).toBeCloseTo(43.92,2);
 });
});
