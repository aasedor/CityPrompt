import { describe,expect,it } from 'vitest';
import { nativeStreetPilot,nativeStreetRouteProblem,placeNativeStreetModules } from './nativeStreetPilot';
import { buildNativeStreetProgram,nativeStreetGroundCells,nativeStreetHasPreparedGround } from './nativeStreetProgram';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
import { expectsNativeStreet } from './nativeStreetReadiness';
import type { SiteZone } from '@/types';

const residential=nativeStreetPilot('student_quiet_residential_street_v1')!;
const shared=nativeStreetPilot('student_planted_shared_lane_v1')!;

describe('finite native street placement limits',()=>{
  it.each([
    ['student_quiet_residential_street_v1',48,480],
    ['student_planted_shared_lane_v1',40,480],
    ['brt_bus_rapid_transit_corridor_v0',100,480],
    ['amsterdam_gracht_v1',80,320],
    ['landmark_signature_bridge_v2',260,480],
  ] as const)('%s accepts both limits and rejects undersize, oversize or missing prepared ground',(variant,min,max)=>{
    const pilot=nativeStreetPilot(variant)!;
    const boundary:SiteZone={id:'site',project_id:'test',zone_type:'site_boundary',coordinates:[],color:'#aaa',sort_order:0,created_at:'1',updated_at:'1',properties:{terrain_strategy:'level',community_3d_mask_existing_tiles:true}};
    const zone=(length:number)=>{
      const line=[[0,0],[0,length/111320]];
      return {coordinates:bufferLineToPolygon(line,pilot.widthM),properties:{plan_centerline:line,road_selected_variant_id:variant}};
    };
    expect(nativeStreetRouteProblem(zone(min),boundary)).toBeNull();
    expect(nativeStreetRouteProblem(zone(max),boundary)).toBeNull();
    expect(nativeStreetRouteProblem(zone(min-.1),boundary)).not.toBeNull();
    expect(nativeStreetRouteProblem(zone(max+.1),boundary)).not.toBeNull();
    expect(nativeStreetRouteProblem(zone(min),null)).toMatch(/level/);
    expect(nativeStreetRouteProblem(zone(min),{...boundary,properties:{terrain_strategy:'landscape'}})).toMatch(/level/);
  });
});

describe('original Shared Lane executable program',()=>{
  it('retains the 14 m shared brick section, four walking arbors and 118 rigid source placements',()=>{
    expect(shared.widthM).toBe(14);
    expect(shared.fixtureLengthM).toBe(40);
    const poses=placeNativeStreetModules(shared,[{x:0,y:0},{x:0,y:40}]);
    expect(poses).toHaveLength(118);
    expect(poses.filter(p=>p.kind==='walkway_arbor')).toHaveLength(4);
    expect(poses.filter(p=>p.kind==='walkway_arbor').every(p=>Math.abs(p.x)>4.5)).toBe(true);
    const cells=nativeStreetGroundCells(14,40,shared.program!.surfaceRegions);
    expect(cells.reduce((sum,c)=>sum+c.width*c.depth,0)).toBeCloseTo(560);
    expect(cells.some(c=>c.material==='asphalt')).toBe(false);
    expect(shared.program!.pavingModuleM).toEqual([.48,.24]);
  });
  it('repeats complete source programs and keeps brick dimensions in a longer, reversed route',()=>{
    for(const route of [[{x:0,y:0},{x:0,y:80}],[{x:0,y:80},{x:0,y:0}]]){
      expect(placeNativeStreetModules(shared,route)).toHaveLength(236);
      const meshes=buildNativeStreetProgram(shared.program!,14,40,route);
      expect(meshes.filter(m=>m.material.startsWith('paving.tile'))).toHaveLength(4);
      expect(meshes.some(m=>m.material==='asphalt')).toBe(false);
      for(const {geometry} of meshes){
        geometry.computeBoundingBox();
        expect(geometry.boundingBox!.min.y).toBeGreaterThanOrEqual(-.0001);
        expect(geometry.boundingBox!.max.y).toBeLessThanOrEqual(80.0001);
        expect(geometry.boundingBox!.min.x).toBeGreaterThanOrEqual(-7.0001);
        expect(geometry.boundingBox!.max.x).toBeLessThanOrEqual(7.0001);
        geometry.dispose();
      }
    }
  });
});
describe('original Residential executable program',()=>{
  it('accepts interior prepared ground without requiring an external-road approach',()=>{
    expect(nativeStreetHasPreparedGround(1200,false,false)).toBe(true);
    expect(nativeStreetHasPreparedGround(0,false,false)).toBe(true);
    expect(nativeStreetHasPreparedGround(null,true,false)).toBe(true);
    expect(nativeStreetHasPreparedGround(null,false,true)).toBe(true);
    expect(nativeStreetHasPreparedGround(null,false,false)).toBe(false);
  });
  it('retains all 138 source placements and the original paving/soil ownership',()=>{
    const poses=placeNativeStreetModules(residential,[{x:0,y:0},{x:0,y:48}]);
    expect(poses).toHaveLength(138);
    const cells=nativeStreetGroundCells(18,48,residential.program!.surfaceRegions);
    expect(cells.reduce((sum,c)=>sum+c.width*c.depth,0)).toBeCloseTo(18*48,6);
    const owners=(x:number,y:number)=>cells.filter(c=>Math.abs(x-c.x)<c.width/2 && Math.abs(y-c.y)<c.depth/2);
    expect(owners(0.1,0.1)[0].material).toBe('paving');
    expect(owners(0.1,4.1)[0].material).toBe('asphalt');
    expect(owners(4.51,17.01)[0].material).toBe('soil');
    expect(owners(4.51,11.41)[0].material).toBe('paving');
    expect(residential.program!.details.filter(d=>d.height===.05)).toHaveLength(32);
  });
  it('preserves native dimensions and complete repeated surfaces through reversal',()=>{
    for(const route of [[{x:0,y:0},{x:0,y:96}],[{x:0,y:96},{x:0,y:0}]]){
      const meshes=buildNativeStreetProgram(residential.program!,18,48,route);
      const ground=meshes.find(m=>m.material==='asphalt')!.geometry;
      ground.computeBoundingBox();
      expect(ground.boundingBox!.min.x).toBeCloseTo(-3);expect(ground.boundingBox!.max.x).toBeCloseTo(3);
      expect(ground.boundingBox!.min.y).toBeCloseTo(0);expect(ground.boundingBox!.max.y).toBeCloseTo(96);
      expect(placeNativeStreetModules(residential,route)).toHaveLength(276);
      meshes.forEach(m=>m.geometry.dispose());
    }
  });
  it('rejects too-short and unsupported terrain before saving but leaves legacy fixtures alone',()=>{
    const boundary:SiteZone={id:'boundary',project_id:'test',zone_type:'site_boundary',coordinates:[],color:'#aaa',sort_order:0,created_at:'1',updated_at:'1',properties:{terrain_strategy:'level',community_3d_mask_existing_tiles:true}};
    const create=(length:number)=>{const line=[[-114,51],[-114,51+length/111320]];return {coordinates:bufferLineToPolygon(line,18),properties:{plan_centerline:line,road_selected_variant_id:residential.id}};};
    expect(nativeStreetRouteProblem(create(48),boundary)).toBeNull();
    expect(nativeStreetRouteProblem(create(47),boundary)).toContain('48–480');
    expect(nativeStreetRouteProblem(create(481),boundary)).toContain('48–480');
    expect(nativeStreetRouteProblem(create(60),{...boundary,properties:{terrain_strategy:'landscape'}})).toContain('level');
    const legacy:SiteZone={...boundary,...create(10),zone_type:'road',properties:{road_selected_variant_id:residential.id,validation_fixed_fixture:true}};
    expect(nativeStreetRouteProblem(legacy)).toBeNull();expect(expectsNativeStreet(legacy)).toBe(false);
  });
});
