import { describe,expect,it } from 'vitest';
import type { SiteZone } from '@/types';
import { metersPerDegLon,METERS_PER_DEG_LAT } from '@/components/viewer/mapEngine/geoUtils';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
import { placementProblem,rectangleAt } from './geometry';
import { CALGARY_LOCAL_PLACEMENT } from './streetPlacement';
import { snapStreetBoundaryPlacement, streetBoundaryEditCoordinates } from './streetBoundaryPlacement';
import { streetDrawingGeometry } from './streetDrawingGeometry';
import { streetCoordinateUpdate } from './streetPlacement';
const ll=(x:number,y:number)=>[-114+x/metersPerDegLon(51),51+y/METERS_PER_DEG_LAT];
const site={id:'site',zone_type:'site_boundary',coordinates:rectangleAt(ll(0,0),200,200)} as SiteZone;
const asset=CALGARY_LOCAL_PLACEMENT,width=asset.sectionWidth;
const street=(x:number):SiteZone=>{const points=[ll(x,-40),ll(x,40)];return {id:'road',zone_type:'road',project_id:'',color:'',sort_order:0,created_at:'',updated_at:'',coordinates:bufferLineToPolygon(points,width),properties:{...asset.properties,plan_centerline:points,plan_route_controls:points}};};
describe('street full-width boundary placement',()=>{
 it('preserves sparse bend handles through boundary validation and the coordinate-save pipeline',()=>{
  const original=street(0);
  const controls=[ll(0,-40),ll(5,-15),ll(0,10),ll(10,40)];
  const edited=streetCoordinateUpdate(original,bufferLineToPolygon(controls,width));
  const preview=snapStreetBoundaryPlacement({...original,...edited},[original],site);
  const saved=streetCoordinateUpdate(original,streetBoundaryEditCoordinates(original,preview));
  expect(preview.problem).toBeNull();
  expect(saved.properties?.plan_route_controls).toEqual(edited.properties?.plan_route_controls);
  expect(saved.properties?.plan_centerline).toEqual(edited.properties?.plan_centerline);
  expect((saved.properties?.plan_route_controls as number[][]).length).toBe(4);
  expect((saved.properties?.plan_centerline as number[][]).length).toBeGreaterThan(4);
 });
 it.each([2,-1])('snaps a side edge with signed gap %s and carries both route records',gap=>{
  const zone=street(100-width/2-gap),before=JSON.stringify(zone),result=snapStreetBoundaryPlacement(zone,[zone],site);
  expect(result.problem).toBeNull();expect(placementProblem(result.coordinates,[],site)).toBeNull();
  const line=result.properties.plan_centerline as number[][];
  expect((line[0][0]+114)*metersPerDegLon(51)+width/2).toBeCloseTo(99.92,2);
  expect(result.properties.plan_route_controls).toEqual(line);
  expect(result.properties.width).toBe(width);expect(JSON.stringify(zone)).toBe(before);
 });
 it('uses the same snap for a newly drawn parallel street and its preview',()=>{
  const points=[ll(100-width/2-2,-40),ll(100-width/2-2,40)],result=streetDrawingGeometry(points,asset.properties,[site]);
  expect(result).toEqual(streetDrawingGeometry(points,asset.properties,[site]));
  expect(placementProblem(result.coordinates,[],site)).toBeNull();
  expect(((result.properties.plan_centerline as number[][])[0][0]+114)*metersPerDegLon(51)+width/2).toBeCloseTo(99.92,2);
 });
 it('carries a procedural street route through a body move, boundary snap and save',()=>{
  const original=street(100-width/2-5);
  original.properties={width,procedural_road:1,plan_centerline:original.properties?.plan_centerline,plan_route_controls:original.properties?.plan_route_controls};
  const moved=original.coordinates.map(p=>[p[0]+4/metersPerDegLon(51),p[1]]);
  const draft={...original,...streetCoordinateUpdate(original,moved)};
  const preview=snapStreetBoundaryPlacement(draft,[original],site);
  const saved=streetCoordinateUpdate(original,preview.coordinates);
  expect(preview.problem).toBeNull();
  expect(saved.properties?.plan_centerline).toEqual(preview.properties.plan_centerline);
  expect(saved.properties?.plan_route_controls).toEqual(preview.properties.plan_route_controls);
  expect(((saved.properties?.plan_centerline as number[][])[0][0]+114)*metersPerDegLon(51)+width/2).toBeCloseTo(99.92,2);
 });
 it('keeps blocked, remote and deliberately extended routes under their existing rules',()=>{
  const zone=street(100-width/2-2),block={id:'block',zone_type:'green_space',coordinates:rectangleAt(ll(99.5,0),1,100),properties:{}} as SiteZone;
  expect(snapStreetBoundaryPlacement(zone,[block],site).coordinates).toBe(zone.coordinates);
  const far=street(0);expect(snapStreetBoundaryPlacement(far,[],site).coordinates).toBe(far.coordinates);
  const outside=street(100-width/2+5);expect(snapStreetBoundaryPlacement(outside,[],site).problem).toContain('site boundary');
  const extension={...outside,properties:{...outside.properties,connect_to_public_road:true}};
  expect(snapStreetBoundaryPlacement(extension,[],site).coordinates).toBe(extension.coordinates);
 });
});
