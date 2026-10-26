import { describe,expect,it } from 'vitest';
import type { SiteZone } from '@/types';
import { metersPerDegLon,METERS_PER_DEG_LAT } from '@/components/viewer/mapEngine/geoUtils';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
import { placementProblem,rectangleAt } from './geometry';
import { CALGARY_LOCAL_PLACEMENT } from './streetPlacement';
import { snapStreetBoundaryPlacement, streetBoundaryEditCoordinates } from './streetBoundaryPlacement';
import { streetDrawingGeometry } from './streetDrawingGeometry';
import { streetCoordinateUpdate } from './streetPlacement';
import { streetConnectionProblem } from './streetConnectionProblem';
import { detectConnectedStreetIntersections } from '@/components/viewer/globe/streetGraphIntersections';
import { resolveStreetJunctionLayout } from '@/components/viewer/globe/streetJunctionGeometry';
import { CLASSROOM_CHOICES } from './canonicalCatalogue';
const ll=(x:number,y:number)=>[-114+x/metersPerDegLon(51),51+y/METERS_PER_DEG_LAT];
const site={id:'site',zone_type:'site_boundary',coordinates:rectangleAt(ll(0,0),200,200)} as SiteZone;
const asset=CALGARY_LOCAL_PLACEMENT,width=asset.sectionWidth;
const street=(x:number):SiteZone=>{const points=[ll(x,-40),ll(x,40)];return {id:'road',zone_type:'road',project_id:'',color:'',sort_order:0,created_at:'',updated_at:'',coordinates:bufferLineToPolygon(points,width),properties:{...asset.properties,plan_centerline:points,plan_route_controls:points,public_realm_lego:{schema_version:1,family_id:'street_local_public_realm',family_version:1,kind:'street',generator:'street_section',archetype_id:'calgary_local',variant_id:'calgary_local_v0',profile_id:'calgary-local-v1',profile_version:1,appearance_kit_id:'calgary_contemporary_native',target:{target_type:'street_segment',row_width_m:16},catalog_fingerprint:'a'.repeat(64),capability_fingerprint:'b'.repeat(64),recipe_hash:'c'.repeat(64)}}};};
describe('street full-width boundary placement',()=>{
 it('aligns a nearly collinear end connection without moving the saved host street',()=>{
  const host=street(0),points=[ll(.8,39.2),ll(.8,80)];
  const candidate={...street(0),id:'draft-street',coordinates:bufferLineToPolygon(points,width),properties:{...host.properties,plan_centerline:points,plan_route_controls:points}};
  const before=JSON.stringify(host);
  expect(streetConnectionProblem(candidate,[host])).toBeTruthy();
  const result=snapStreetBoundaryPlacement(candidate,[host],site);
  expect(result.problem).toBeNull();
  const line=result.properties.plan_centerline as number[][];
  expect((line[0][0]+114)*metersPerDegLon(51)).toBeCloseTo(0,3);
  expect((line[0][1]-51)*METERS_PER_DEG_LAT).toBeCloseTo(40,3);
  expect(result.properties.plan_route_controls).toEqual(line);
  expect(JSON.stringify(host)).toBe(before);
 });
 it('recovers a crossing just below the supported angle only after complete geometry validation',()=>{
  const host=street(0),angle=46*Math.PI/180;
  const points=[ll(-45*Math.cos(angle),-45*Math.sin(angle)),ll(45*Math.cos(angle),45*Math.sin(angle))];
  const candidate={...street(0),id:'draft-street',coordinates:bufferLineToPolygon(points,width),properties:{...host.properties,plan_centerline:points,plan_route_controls:points}};
  expect(streetConnectionProblem(candidate,[host])).toBeTruthy();
  const result=snapStreetBoundaryPlacement(candidate,[host],site);
  expect(result.problem).toBeNull();
  const saved={...candidate,...result},network=[host,saved];
  const nodes=detectConnectedStreetIntersections(network,true);
  expect(nodes).toHaveLength(1);
  expect(resolveStreetJunctionLayout(nodes[0],network)).not.toBeNull();
  expect(result.properties.plan_route_controls).toEqual(result.properties.plan_centerline);
  const line=result.properties.plan_centerline as number[][];
  for(const [index,point] of line.entries())expect(Math.hypot((point[0]-points[index][0])*metersPerDegLon(51),(point[1]-points[index][1])*METERS_PER_DEG_LAT)).toBeLessThanOrEqual(3);
 });
 it('keeps unsupported duplicates and large-angle corrections rejected',()=>{
  const host=street(0);
  for(const points of [[ll(1,-40),ll(1,40)],[ll(-10,-45),ll(10,45)]]) {
   const candidate={...street(0),id:'draft-street',coordinates:bufferLineToPolygon(points,width),properties:{...asset.properties,plan_centerline:points}};
   const result=snapStreetBoundaryPlacement(candidate,[host],site);
   expect(result.problem).toMatch(/junction/);
   expect(result.coordinates).toBe(candidate.coordinates);
  }
 });
 it('uses the same bounded recovery for a fresh picker route and its save without a forged recipe',()=>{
  const host=street(0),asset=CLASSROOM_CHOICES.flatMap(choice=>choice.placements).find(row=>row.model.variantId==='student_quiet_residential_street_v1')!;
  const angle=46*Math.PI/180,points=[ll(-45*Math.cos(angle),-45*Math.sin(angle)),ll(45*Math.cos(angle),45*Math.sin(angle))];
  const result=streetDrawingGeometry(points,asset.properties,[site,host]);
  const candidate={...host,...result,id:'draft-street'};
  expect(streetConnectionProblem(candidate,[host])).toBeNull();
  expect(result.properties.public_realm_lego).toBeUndefined();
  expect(result.properties.plan_route_controls).toEqual(result.properties.plan_centerline);
  expect(result).toEqual(streetDrawingGeometry(points,asset.properties,[site,host]));
 });
 it('rejects a nearby junction correction that would overlap occupied land',()=>{
  const host=street(0),points=[ll(.8,39.2),ll(.8,80)];
  const candidate={...host,id:'draft-street',coordinates:bufferLineToPolygon(points,width),properties:{...host.properties,plan_centerline:points,plan_route_controls:points}};
  const blocker={...site,id:'occupied',zone_type:'building' as const,coordinates:rectangleAt(ll(-7.9,60),.2,20),properties:{}};
  const before=JSON.stringify(candidate),result=snapStreetBoundaryPlacement(candidate,[host,blocker],site);
  expect(result.problem).toBeTruthy();
  expect(result.coordinates).toBe(candidate.coordinates);
  expect(JSON.stringify(candidate)).toBe(before);
 });
 it('rejects junction snapping that would push the full street outside the site',()=>{
  const host=street(0),points=[ll(.8,39.2),ll(.8,99.8)];
  const candidate={...host,id:'draft-street',coordinates:bufferLineToPolygon(points,width),properties:{...host.properties,plan_centerline:points,plan_route_controls:points}};
  expect(placementProblem(candidate.coordinates,[host],site,undefined,{allowStreetIntersections:true})).toBeNull();
  const result=snapStreetBoundaryPlacement(candidate,[host],site);
  expect(result.problem).toMatch(/junction/);
  expect(result.coordinates).toBe(candidate.coordinates);
 });
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
