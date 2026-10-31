import { describe,expect,it } from 'vitest';
import booleanPointInPolygon from '@turf/boolean-point-in-polygon';
import { pathwaySurfacePolygons } from './pathwayFootprint';

const inside=(point:number[],coordinates:ReturnType<typeof pathwaySurfacePolygons>)=>
  booleanPointInPolygon(point,{type:'MultiPolygon',coordinates});

describe('flat pathway footprint',()=>{
  it('keeps the exact straight width and square connection caps',()=>{
    const polygons=pathwaySurfacePolygons([[0,0],[20,0]],2);
    expect(inside([10,.99],polygons)).toBe(true);
    expect(inside([10,1.01],polygons)).toBe(false);
    expect(inside([-.1,0],polygons)).toBe(false);
  });
  it('joins reversals, tight folds and crossings without losing either arm',()=>{
    const polygons=pathwaySurfacePolygons([[0,0],[20,0],[0,0],[0,20],[20,0]],2);
    expect(polygons).toHaveLength(1);
    for(const point of [[10,.4],[20,.4],[.4,10],[10,10]]) expect(inside(point,polygons)).toBe(true);
    expect(polygons.flat(3).every(Number.isFinite)).toBe(true);
  });
  it('preserves the unpaved interior of an enclosed route',()=>{
    const polygons=pathwaySurfacePolygons([[0,0],[20,0],[20,20],[0,20],[0,0]],2);
    expect(polygons[0]).toHaveLength(2);
    expect(inside([10,10],polygons)).toBe(false);
    expect(inside([10,.4],polygons)).toBe(true);
  });
});
