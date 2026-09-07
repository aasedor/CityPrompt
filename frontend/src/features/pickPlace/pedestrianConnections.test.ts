import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';
import { rectangleAt } from './geometry';
import { entranceWorldPoint, readCrossings, resolvePedestrianConnections, type BuildingEntrance } from './pedestrianConnections';

const ll=([x,y]:number[])=>[-114+x/metersPerDegLon(51),51+y/METERS_PER_DEG_LAT];
const xy=([x,y]:number[])=>[(x+114)*metersPerDegLon(51),(y-51)*METERS_PER_DEG_LAT];
const zone=(id:string,zone_type:SiteZone['zone_type'],coordinates:number[][],properties:SiteZone['properties']={}):SiteZone=>
  ({id,project_id:'test',zone_type,coordinates,properties,color:'#aaa',sort_order:0,created_at:'2026-09-06',updated_at:'2026-09-06'});
function fixture(){
  const entrance:BuildingEntrance={version:1,xM:0,yM:8,referenceWidthM:12,referenceDepthM:20,scaleWithPlot:true,streetId:'street',widthM:1.8};
  const house=zone('house','building',rectangleAt(ll([0,-25]),12,20),{pedestrian_building_entrance:entrance});
  const line=[ll([-40,0]),ll([40,0])];
  const street=zone('street','road',bufferLineToPolygon(line,16),{road_archetype_id:'calgary_local',road_selected_variant_id:'calgary_local_v0',width:16,plan_centerline:line});
  const boundary={...zone('site','site_boundary',rectangleAt(ll([0,0]),120,100)),is_active_boundary:true};
  return {house,street,boundary,entrance,zones:[house,street,boundary]};
}
describe('saved pedestrian relationships',()=>{
  it('joins the near sidewalk, follows translation, and leaves the source data unchanged',()=>{
    const f=fixture(),before=JSON.stringify(f.zones),first=resolvePedestrianConnections(f.zones)[0];
    expect(first.status).toBe('connected');expect(first.strips).toHaveLength(1);
    expect(xy(first.strips[0].start)[1]).toBeLessThan(0);
    const moved={...f.house,coordinates:rectangleAt(ll([5,-25]),12,20)};
    const next=resolvePedestrianConnections([moved,f.street,f.boundary])[0];
    expect(next.status).toBe('connected');expect(xy(next.strips[0].end)[0]).toBeCloseTo(5,3);
    expect(JSON.stringify(f.zones)).toBe(before);
  });
  it('rotates anchors and supports scaled offsets or fixed-size native homes',()=>{
    const {house,entrance}=fixture();
    const rotated={...house,coordinates:rectangleAt(ll([0,-25]),12,20,90)};
    expect(xy(entranceWorldPoint(rotated,entrance)!)[0]).toBeCloseTo(-8,3);
    const resized={...house,coordinates:rectangleAt(ll([0,-25]),24,40)};
    expect(xy(entranceWorldPoint(resized,entrance)!)[1]).toBeCloseTo(-9,3);
    expect(xy(entranceWorldPoint(resized,{...entrance,scaleWithPlot:false})!)[1]).toBeCloseTo(-17,3);
  });
  it('regenerates from serialized sources and follows a moved sidewalk',()=>{
    const f=fixture(),line=[ll([-40,3]),ll([40,3])];
    const street={...f.street,coordinates:bufferLineToPolygon(line,16),properties:{...f.street.properties,plan_centerline:line}};
    const result=resolvePedestrianConnections(JSON.parse(JSON.stringify([f.house,street,f.boundary])))[0];
    expect(result.status).toBe('connected');
    expect(xy(result.strips[0].start)[1]).toBeCloseTo(-3.8,2);
  });
  it('reports deleted/hidden targets and never switches to another street',()=>{
    const f=fixture();
    expect(resolvePedestrianConnections([f.house,f.boundary])[0].status).toBe('unresolved');
    expect(resolvePedestrianConnections(f.zones,['house','site'])[0].reason).toMatch(/missing or hidden/);
  });
  it('does not route through another building or across the road',()=>{
    const f=fixture(),barrier=zone('barrier','building',rectangleAt(ll([0,-12]),8,3));
    expect(resolvePedestrianConnections([...f.zones,barrier])[0].status).toBe('unresolved');
    const motorOnly={...f.street,properties:{...f.street.properties,road_archetype_id:'highway',road_selected_variant_id:undefined}};
    expect(resolvePedestrianConnections([f.house,motorOnly,f.boundary])[0].status).toBe('unresolved');
  });
  it('only creates deliberately saved crossings, including raised surfaces and vehicle ramps',()=>{
    const f=fixture();expect(resolvePedestrianConnections(f.zones).filter(r=>r.kind==='crossing')).toHaveLength(0);
    const street={...f.street,properties:{...f.street.properties,pedestrian_crossings:[{id:'cross',position:0.5,widthM:3}]}};
    const result=resolvePedestrianConnections([f.house,street,f.boundary]).find(r=>r.kind==='crossing')!;
    expect(result.status).toBe('connected');expect(result.strips.some(s=>s.id.includes('ramp'))).toBe(true);
    const surface=result.strips[0];expect(xy(surface.start)[1]).toBeLessThan(-6);expect(xy(surface.end)[1]).toBeGreaterThan(6);
  });
  it('rejects crossing near an end and one through an intersecting street',()=>{
    const f=fixture();
    const crossing=(position:number)=>({...f.street,properties:{...f.street.properties,pedestrian_crossings:[{id:'cross',position,widthM:3}]}});
    expect(resolvePedestrianConnections([crossing(0.01),f.boundary])[0].status).toBe('unresolved');
    const line=[ll([0,-40]),ll([0,40])];
    const other=zone('other','road',bufferLineToPolygon(line,16),{...f.street.properties,plan_centerline:line});
    expect(resolvePedestrianConnections([crossing(0.5),other,f.boundary])[0].status).toBe('unresolved');
  });
  it('allows a park beyond the sidewalk but rejects overlapping crossing footprints',()=>{
    const f=fixture(),park=zone('park','green_space',rectangleAt(ll([0,25]),40,30));
    const crossings=[{id:'one',position:0.5,widthM:3}];
    const street={...f.street,properties:{...f.street.properties,pedestrian_crossings:crossings}};
    expect(resolvePedestrianConnections([street,park,f.boundary])[0].status).toBe('connected');
    crossings.push({id:'two',position:0.51,widthM:3});
    expect(resolvePedestrianConnections([street,park,f.boundary]).every(r=>r.status==='unresolved')).toBe(true);
  });
  it('does not draw an approach back through its own building',()=>{
    const f=fixture(),back={...f.house,properties:{...f.house.properties,pedestrian_building_entrance:{...f.entrance,yM:-8}}};
    expect(resolvePedestrianConnections([back,f.street,f.boundary])[0].status).toBe('unresolved');
  });
  it('ignores malformed, duplicated or oversized crossing lists',()=>{
    const {street}=fixture();
    expect(readCrossings({...street,properties:{pedestrian_crossings:[{id:'bad',position:NaN,widthM:3}]}})).toEqual([]);
    expect(readCrossings({...street,properties:{pedestrian_crossings:Array.from({length:9},(_,i)=>({id:String(i),position:0.5,widthM:3}))}})).toEqual([]);
  });
});
