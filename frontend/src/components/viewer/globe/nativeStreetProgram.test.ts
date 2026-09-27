import { describe,expect,it } from 'vitest';
import { nativeStreetPilot,nativeStreetRouteProblem,placeNativeStreetModules } from './nativeStreetPilot';
import { buildNativeStreetProgram,nativeStreetGroundCells,nativeStreetHasPreparedGround } from './nativeStreetProgram';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
import { expectsNativeStreet } from './nativeStreetReadiness';
import type { SiteZone } from '@/types';

const residential=nativeStreetPilot('student_quiet_residential_street_v1')!;
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
