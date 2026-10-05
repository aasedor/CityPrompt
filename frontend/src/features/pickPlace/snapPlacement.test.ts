import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';
import { placementProblem, rectangleAt, rectangleDimensions } from './geometry';
import { snapPlacement } from './snapPlacement';
import { bufferLineToPolygon } from '@/utils/roadGeometry';

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
