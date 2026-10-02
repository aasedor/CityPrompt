import { describe, expect, it } from 'vitest';
import { nativeStreetPilot, nativeStreetRouteProblem, placeNativeStreetModules } from './nativeStreetPilot';
import { buildNativeStreetProgram } from './nativeStreetProgram';
import { CIVIC_RAIL_VARIANT, SKYTRAIN_RAIL_VARIANT, elevatedRailStationProblem } from './elevatedRailProgram';
import { specialistWalkingHeight } from './specialistStreetProgram';
import { authoredCameraGround } from './authoredCameraGround';
import { elevatedRailLiftDestination } from './elevatedRailWalking';
import { RAIL_LIFT_X_M, RAIL_LIFT_Y_M, RAIL_PLATFORM_HEIGHT_M } from './elevatedRailProgram';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
import type { SiteZone } from '@/types';

const variants=[SKYTRAIN_RAIL_VARIANT,CIVIC_RAIL_VARIANT];
const stop=(stationM:number,id='a')=>({id,stationM});
const route=(length:number)=>[{x:0,y:0},{x:0,y:length}];
const zone=(variant:string,length:number,stops:Array<{id:string;stationM:number}>=[])=>{
  const line=[[0,0],[0,length/111320]];
  return {id:'rail',project_id:'test',zone_type:'road',coordinates:bufferLineToPolygon(line,26),
    color:'#aaa',sort_order:0,created_at:'now',updated_at:'now',
    properties:{road_archetype_id:variant.replace(/_v0$/,''),road_selected_variant_id:variant,
      width:26,plan_centerline:line,road_native_stops:stops}} as SiteZone;
};
const boundary={...zone(variants[0],120),id:'site',zone_type:'site_boundary' as const,
  is_active_boundary:true,properties:{terrain_elevation_m:1103,community_3d_mask_existing_tiles:true}};

describe('elevated stations',()=>{
  it.each(variants)('places and edits only selected full stations for %s',variant=>{
    const pilot=nativeStreetPilot(variant)!;
    expect(pilot.sourceArchetypeId).toBe(variant.replace(/_v0$/,''));
    expect(pilot.modules.rail_station).toBeTruthy();
    const first=placeNativeStreetModules(pilot,route(160),[],[stop(40)]);
    const moved=placeNativeStreetModules(pilot,route(160),[],[stop(100)]);
    const removed=placeNativeStreetModules(pilot,route(160),[],[]);
    expect(first.filter(p=>p.kind==='rail_station').map(p=>p.stationM)).toEqual([40]);
    expect(moved.filter(p=>p.kind==='rail_station').map(p=>p.stationM)).toEqual([100]);
    expect(removed.filter(p=>p.kind==='rail_station')).toHaveLength(0);
    expect(first.filter(p=>p.kind==='rail_train')).toHaveLength(1);
    expect(first.filter(p=>p.kind==='rail_pier').length).toBeGreaterThan(5);
    expect(first.filter(p=>p.kind.startsWith('rail_')).every(p=>p.scale===1)).toBe(true);
    expect(nativeStreetRouteProblem(zone(variant,160,[stop(40)]),boundary)).toBeNull();
  });
  it('requires complete station envelopes, unique IDs and clear spacing',()=>{
    for(const stops of [[stop(23)],[stop(137)],[stop(40),stop(89,'b')],
      [stop(40),stop(100)],[stop(40),stop(100,'b'),stop(150,'c')]]){
      const problem=elevatedRailStationProblem(160,stops);
      if(stops.length===2 && stops[1].id==='b' && stops[1].stationM===100)expect(problem).toBeNull();
      else expect(problem).not.toBeNull();
    }
    expect(elevatedRailStationProblem(160,[stop(40),stop(100,'b')])).toBeNull();
    expect(elevatedRailStationProblem(160,[stop(40),stop(100)])).toMatch(/identity/);
    expect(elevatedRailStationProblem(160,[{id:'x',stationM:NaN}])).toMatch(/valid/);
  });
  it.each(variants)('keeps the track continuous while opening only selected platform edges for %s',variant=>{
    const pilot=nativeStreetPilot(variant)!;
    const noStation=buildNativeStreetProgram(pilot.program!,26,48,route(120));
    const withStation=buildNativeStreetProgram(pilot.program!,26,48,route(120),[stop(60)]);
    const count=(meshes:typeof noStation,material:string)=>meshes.find(m=>m.material===material)!.geometry.index!.count;
    const spansStation=(meshes:typeof noStation)=>{
      const g=meshes.find(m=>m.material==='silver')!.geometry,pos=g.getAttribute('position');
      for(let i=0;i<g.index!.count;i+=3){
        const ys=[0,1,2].map(j=>pos.getY(g.index!.getX(i+j)));
        if(Math.min(...ys)<60&&Math.max(...ys)>60)return true;
      }
      return false;
    };
    expect(count(withStation,'steel')).toBe(count(noStation,'steel'));
    expect(spansStation(noStation)).toBe(true);
    expect(spansStation(withStation)).toBe(false);
    expect(withStation.every(m=>Array.from(m.geometry.getAttribute('position').array).every(Number.isFinite))).toBe(true);
    [...noStation,...withStation].forEach(m=>m.geometry.dispose());
  });
  it.each(variants)('walks from ground up both stair routes to the platform for %s',variant=>{
    const stops=[stop(60)];
    for(const x of [-8.7,8.7]){
      let previous=-1;
      for(let y=46;y<=74;y+=.25){
        const height=specialistWalkingHeight(variant,x,y,120,stops);
        expect(height).not.toBeNull();
        expect(height!).toBeGreaterThanOrEqual(previous);
        previous=height!;
      }
      expect(previous).toBeCloseTo(7.745);
      expect(specialistWalkingHeight(variant,x>0?7:-7,72,120,stops,true)).toBeCloseTo(7.998);
    }
    for(const x of [-3.25,3.25,11])expect(specialistWalkingHeight(variant,x,60,120,stops)).toBe(.025);
    const rail=zone(variant,120,stops),site={...boundary,coordinates:bufferLineToPolygon([[0,0],[0,120/111320]],120)};
    const lng=8.7/(111320*Math.cos(0));
    expect(authoredCameraGround([site,rail],lng,60/111320,1103)).toBeCloseTo(1106.885);
  });
  it.each(variants)('serves both platform sides with a step-free lift for %s',variant=>{
    const rail=zone(variant,120,[stop(60)]),site={...boundary,coordinates:bufferLineToPolygon([[0,0],[0,120/111320]],120)};
    for(const side of [-1,1]){
      const pose={lng:side*RAIL_LIFT_X_M/111320,lat:(60+RAIL_LIFT_Y_M)/111320,groundHeight:1103.025,heading:0};
      const upper=elevatedRailLiftDestination([site,rail],pose);
      expect(upper?.groundHeight).toBeCloseTo(1103+RAIL_PLATFORM_HEIGHT_M);
      expect(authoredCameraGround([site,rail],pose.lng,pose.lat,upper!.groundHeight)).toBeCloseTo(upper!.groundHeight);
      expect(elevatedRailLiftDestination([site,rail],upper!)?.groundHeight).toBeCloseTo(pose.groundHeight);
      expect(elevatedRailLiftDestination([site,rail],{...pose,lat:pose.lat+5/111320})).toBeNull();
      const invalid={...rail,properties:{...rail.properties,road_native_stops:[null]}} as unknown as SiteZone;
      expect(elevatedRailLiftDestination([site,invalid],pose)).toBeNull();
    }
  });
});
