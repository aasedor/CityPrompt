import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';
import { placementProblem, rectangleAt, rectangleDimensions } from './geometry';
import { snapBuildingMove, snapPlacement } from './snapPlacement';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
import { CATALOGUE_ASSETS } from './assetRegistry';
import { placeAsset, placementProperties } from './catalogue';
import savedCourtScene from './__fixtures__/courtRotationStreetTower20261029.json';

const ll = (x: number, y: number) => [-114 + x/metersPerDegLon(51),51 + y/METERS_PER_DEG_LAT];
const zone = (id: string, coords: number[][], zone_type: SiteZone['zone_type'] = 'building') => ({id, coordinates:coords, zone_type,properties:{}} as SiteZone);
const site = zone('site',rectangleAt(ll(0,0),100,100),'site_boundary');
const cycleStreet = () => {
  const asset=CATALOGUE_ASSETS.find(a=>a.id==='student_neighbourhood_cycle_street_v1')!;
  const points=[ll(0,-80),ll(0,0),ll(60,0)];
  return {...zone('cycle-street',bufferLineToPolygon(points,13),'road'),
    properties:{...asset.properties,plan_centerline:points,plan_route_controls:points}};
};
const court = (x=20,y=-25) => {
  const asset=placeAsset('native-park:court_only_basketball_v1--native-v1');
  const coordinates=rectangleAt(ll(x,y),21,36);
  return {...zone('court',coordinates,'green_space'),properties:placementProperties(asset,0,coordinates)};
};
const savedCourtZones = () => {
  const [lng,lat]=savedCourtScene.origin;
  const world=(p:number[])=>[lng+p[0]/metersPerDegLon(lat),lat+p[1]/METERS_PER_DEG_LAT];
  return savedCourtScene.zones.map(item=>({...zone(item.id,item.coordinatesM.map(world),item.zone_type as SiteZone['zone_type']),
    properties:{...item.properties,...(item.centerlineM ? {plan_centerline:item.centerlineM.map(world)} : {}),
      ...(item.routeControlsM ? {plan_route_controls:item.routeControlsM.map(world)} : {})}} as SiteZone));
};
describe('ideation placement snapping',()=>{
  it('finds the bounded diagonal fit for the saved court between a tower and cycle street',()=>{
    const zones=savedCourtZones();
    const self=zones.find(item=>item.properties?.court_only_native===true)!;
    const boundary=zones.find(item=>item.zone_type==='site_boundary')!;
    const dimensions=rectangleDimensions(self.coordinates),before=JSON.stringify(zones);
    const proposed=rectangleAt(dimensions.center,dimensions.width,dimensions.depth,15);
    expect(placementProblem(self.coordinates,zones,boundary,self.id)).toBeNull();
    expect(placementProblem(proposed,zones,boundary,self.id)).toContain('street and sidewalks');
    const result=snapPlacement(proposed,zones,boundary,self.id,self.properties,self.zone_type);
    expect(result.problem).toBeNull();
    const d=rectangleDimensions(result.coordinates);
    const dx=(d.center[0]-dimensions.center[0])*metersPerDegLon(dimensions.center[1]);
    const dy=(d.center[1]-dimensions.center[1])*METERS_PER_DEG_LAT;
    expect(dx).toBeLessThan(-4.2);expect(dy).toBeGreaterThan(29.5);
    expect(Math.hypot(dx,dy)).toBeLessThanOrEqual(30);
    expect(d.width).toBeCloseTo(21,3);expect(d.depth).toBeCloseTo(36,3);expect(d.degrees).toBeCloseTo(15,3);
    expect(placementProblem(result.coordinates,zones,boundary,self.id)).toBeNull();
    expect(JSON.stringify(zones)).toBe(before);
  });
  it('settles a rotated fixed court at the nearest clear inside corner of a cycle street',()=>{
    const road=cycleStreet(),self=court(),boundary=zone('site',rectangleAt(ll(0,0),200,200),'site_boundary');
    const before=JSON.stringify(self),context=[self,road,boundary];
    expect(placementProblem(self.coordinates,context,boundary,self.id)).toBeNull();
    const proposed=rectangleAt(ll(20,-25),21,36,15);
    expect(placementProblem(proposed,context,boundary,self.id)).toContain('street and sidewalks');
    const result=snapPlacement(proposed,context,boundary,self.id,self.properties,self.zone_type);
    expect(result.problem).toBeNull();
    expect(result.snapped).toBe(true);
    const d=rectangleDimensions(result.coordinates);
    // 6.5 m half-street + rotated half-court extent + 2 cm contact margin.
    expect((d.center[0]+114)*metersPerDegLon(51)).toBeCloseTo(21.32196,2);
    expect((d.center[1]-51)*METERS_PER_DEG_LAT).toBeCloseTo(-26.62426,2);
    expect(d.width).toBeCloseTo(21,3);expect(d.depth).toBeCloseTo(36,3);expect(d.degrees).toBeCloseTo(15,3);
    expect(placementProblem(result.coordinates,context,boundary,self.id)).toBeNull();
    expect(JSON.stringify(self)).toBe(before);
  });
  it('keeps the requested court and boundary conflict when rotation has no fit',()=>{
    const self=court(),road=cycleStreet(),boundary=zone('site',self.coordinates,'site_boundary');
    const before=JSON.stringify(self),proposed=rectangleAt(ll(20,-25),21,36,15);
    const result=snapPlacement(proposed,[self,road,boundary],boundary,self.id,self.properties,self.zone_type);
    expect(result.problem).toContain('site boundary');
    expect(result.snapped).toBe(false);expect(result.coordinates).toEqual(proposed);
    expect(JSON.stringify(self)).toBe(before);
  });
  it('preserves other plots while settling a rotated court around a concave street',()=>{
    const self=court(),road=cycleStreet(),boundary=zone('site',rectangleAt(ll(0,0),200,200),'site_boundary');
    const neighbour=zone('neighbour',rectangleAt(ll(30,-50),14,10));
    const context=[self,road,neighbour,boundary],before=JSON.stringify(context);
    const result=snapPlacement(rectangleAt(ll(20,-25),21,36,15),context,boundary,self.id,self.properties,self.zone_type);
    expect(result.problem).toBeNull();
    expect(placementProblem(result.coordinates,context,boundary,self.id)).toBeNull();
    expect(rectangleDimensions(result.coordinates).width).toBeCloseTo(21,3);
    expect(rectangleDimensions(result.coordinates).depth).toBeCloseTo(36,3);
    expect(JSON.stringify(context)).toBe(before);
  });
  it('refuses a street correction beyond the bounded nearby search',()=>{
    const self=court(0,0),road={...cycleStreet(),coordinates:rectangleAt(ll(0,0),100,100),properties:{width:100}};
    const boundary=zone('site',rectangleAt(ll(0,0),500,500),'site_boundary'),proposed=rectangleAt(ll(0,0),21,36,15);
    const result=snapPlacement(proposed,[self,road,boundary],boundary,self.id,self.properties,self.zone_type);
    expect(result.problem).toContain('street and sidewalks');
    expect(result.snapped).toBe(false);expect(result.coordinates).toEqual(proposed);
  });
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
  it.each([[48,1,15.7],[44.5,15,1.3]])('chooses the closest fitting corner around a boundary and neighbour at (%s, %s)',(x,y,maxShift)=>{
    const neighbours=[zone('a',rectangleAt(ll(40,0),12,16))];
    const proposed=rectangleAt(ll(x,y),12,16,0);
    const properties={validation_fixed_fixture:true};
    const result=snapPlacement(proposed,neighbours,site,undefined,properties,'building');
    expect(result.problem).toBeNull();
    const d=rectangleDimensions(result.coordinates);
    const dx=(d.center[0]-rectangleDimensions(proposed).center[0])*metersPerDegLon(51);
    const dy=(d.center[1]-rectangleDimensions(proposed).center[1])*METERS_PER_DEG_LAT;
    expect(Math.hypot(dx,dy)).toBeLessThan(maxShift);
    expect(d.width).toBeCloseTo(12,3);expect(d.depth).toBeCloseTo(16,3);expect(d.degrees).toBeCloseTo(0,3);
    expect(placementProblem(result.coordinates,neighbours,site,undefined,{properties})).toBeNull();
  });
  it('settles a fixed model moved slightly over a neighbour without resizing it',()=>{
    const self={...zone('self',rectangleAt(ll(25,0),12,16)),properties:{validation_fixed_fixture:true}};
    const other=zone('other',rectangleAt(ll(0,0),12,16));
    const proposed=rectangleAt(ll(11,0),12,16);
    const result=snapBuildingMove(self,proposed,[self,other],site);
    expect(result.problem).toBeNull();expect(result.snapped).toBe(true);
    const d=rectangleDimensions(result.coordinates);
    expect((d.center[0]+114)*metersPerDegLon(51)).toBeCloseTo(12.02,2);
    expect(d.width).toBeCloseTo(12,3);expect(d.depth).toBeCloseTo(16,3);
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
  it('explains the obstruction when a clear nearby position does not exist',()=>{
    const narrow=zone('site',rectangleAt(ll(0,0),22,24),'site_boundary');
    const footprint=rectangleAt(ll(0,0),12,16);
    const park={...zone('park',footprint,'green_space'),name:'Basketball park'};
    expect(snapPlacement(footprint,[park],narrow).problem).toContain('overlaps Basketball park');
    expect(snapPlacement(rectangleAt(ll(80,0),12,16),[],narrow).problem).toContain('site boundary');
  });
  it('slides a regulation park clear of a street without shrinking or rotating its court', () => {
    const road = {...zone('main',bufferLineToPolygon([ll(0,-80),ll(0,80)],23),'road'), properties:{width:23}};
    const park = rectangleAt(ll(27,0),52,39,90);
    const boundary = zone('site',rectangleAt(ll(0,0),180,180),'site_boundary');
    const result = snapPlacement(park,[road],boundary,undefined,{pick_place_asset:'park_trio_basketball'});
    expect(result.snapped).toBe(true);
    expect(result.problem).toBeNull();
    expect(placementProblem(result.coordinates,[road],boundary)).toBeNull();
    const dimensions=rectangleDimensions(result.coordinates);
    expect(dimensions.width).toBeCloseTo(52,3);
    expect(dimensions.depth).toBeCloseTo(39,3);
    expect(dimensions.degrees).toBeCloseTo(90,3);
  });
  it.each([0,90,180,270])('closes a two-metre park gap to the sidewalk at %s degrees', angle => {
    const road=zone('street',rectangleAt(ll(0,0),80,20,angle),'road');
    const rad=angle*Math.PI/180, distance=10+8+2;
    const coords=rectangleAt(ll(-distance*Math.sin(rad),distance*Math.cos(rad)),12,16,angle);
    const result=snapPlacement(coords,[road],site,undefined,{},'green_space');
    expect(result.problem).toBeNull();expect(result.snapped).toBe(true);
    const d=rectangleDimensions(result.coordinates);
    expect(Math.hypot((d.center[0]+114)*metersPerDegLon(51),(d.center[1]-51)*METERS_PER_DEG_LAT)).toBeCloseTo(18.02,2);
    expect(d.width).toBeCloseTo(12,4);expect(d.depth).toBeCloseTo(16,4);expect(d.degrees).toBeCloseTo(angle>180?angle-360:angle,4);
    expect(snapPlacement(result.coordinates,[road],site,undefined,{},'green_space').snapped).toBe(false);
  });
  it('keeps distant parks and nonparallel edges where the student places them',()=>{
    const road=zone('street',rectangleAt(ll(0,0),80,20),'road');
    for(const coords of [rectangleAt(ll(0,22),12,16),rectangleAt(ll(0,25),12,16,25)])
      expect(snapPlacement(coords,[road],site,undefined,{},'green_space')).toEqual({coordinates:coords,snapped:false,problem:null});
  });
  it.each(['building','residential'] as const)('snaps any clear %s side or rotated corner to a sidewalk',zoneType=>{
    const road=zone('street',rectangleAt(ll(0,0),80,20),'road');
    for(const angle of [0,90,25]) {
      const r=angle*Math.PI/180,halfNorth=6*Math.abs(Math.sin(r))+8*Math.abs(Math.cos(r));
      const coords=rectangleAt(ll(0,10+halfNorth+2),12,16,angle);
      const result=snapPlacement(coords,[road],site,undefined,{},zoneType);
      expect(result.problem).toBeNull();expect(result.snapped).toBe(true);
      const d=rectangleDimensions(result.coordinates);
      expect((d.center[1]-51)*METERS_PER_DEG_LAT-halfNorth).toBeCloseTo(10.02,2);
      expect(d.width).toBeCloseTo(12,4);expect(d.depth).toBeCloseTo(16,4);expect(d.degrees).toBeCloseTo(angle,4);
      expect(placementProblem(result.coordinates,[road],site)).toBeNull();
    }
  });
  it('brings a rotated park corner to the street while keeping its complete outline',()=>{
    const road=zone('street',rectangleAt(ll(0,0),80,20),'road'),angle=25,rad=angle*Math.PI/180;
    const halfNorth=6*Math.sin(rad)+8*Math.cos(rad),coords=rectangleAt(ll(0,10+halfNorth+2),12,16,angle);
    const result=snapPlacement(coords,[road],site,undefined,{},'green_space');
    expect(result.problem).toBeNull();expect(result.snapped).toBe(true);
    const d=rectangleDimensions(result.coordinates);
    expect((d.center[1]-51)*METERS_PER_DEG_LAT-halfNorth).toBeCloseTo(10.02,2);
    expect(d.degrees).toBeCloseTo(angle,4);expect(d.width).toBeCloseTo(12,4);expect(d.depth).toBeCloseTo(16,4);
    expect(placementProblem(result.coordinates,[road],site)).toBeNull();
  });
  it('does not snap a park through a neighbouring plot to reach the street',()=>{
    const road=zone('street',rectangleAt(ll(0,0),80,20),'road');
    const occupied=zone('frontage',rectangleAt(ll(0,11),30,2));
    const coords=rectangleAt(ll(0,21),12,16);
    expect(snapPlacement(coords,[road,occupied],site,undefined,{},'green_space')).toEqual({coordinates:coords,snapped:false,problem:null});
  });
  it('keeps unknown building revisions within their full saved plot',()=>{
    const road=zone('street',rectangleAt(ll(0,0),80,20),'road');
    const coords=rectangleAt(ll(0,20),12,16),properties={native_plot_axes:true,pick_place_asset:'validation_minimalist_infill_brick_monolith',pick_place_model_revision:'unknown'};
    const result=snapPlacement(coords,[road],site,undefined,properties,'building');
    expect(result.problem).toBeNull();expect(result.snapped).toBe(true);
    expect((rectangleDimensions(result.coordinates).center[1]-51)*METERS_PER_DEG_LAT).toBeCloseTo(18.02,2);
    expect(placementProblem(result.coordinates,[road],site,undefined,{properties})).toBeNull();
  });
});
