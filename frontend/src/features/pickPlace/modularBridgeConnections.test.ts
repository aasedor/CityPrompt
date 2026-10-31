import { afterAll, expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
vi.stubEnv('DEV',true);vi.stubEnv('MODE','development');
const { specialistConnectionProblem } = await import('./specialistConnections');
const { PATHWAY_ASSETS } = await import('./assetRegistry');
afterAll(()=>vi.unstubAllEnvs());
function street(id: string, line: number[][], width: number, properties = {}) {
  const ll=line.map(([x,y])=>[x/111320,y/111320]);
  return {id,project_id:'trial',color:'#aaa',sort_order:0,created_at:'',updated_at:'',zone_type:'road',coordinates:bufferLineToPolygon(ll,width),properties:{width,lane_count:2,
    road_archetype_id:'calgary_local',road_selected_variant_id:'calgary_local_v0',plan_centerline:ll,...properties}} as SiteZone;
}
const bridge=street('bridge',[[0,0],[0,80]],6,{lane_count:0,road_archetype_id:'urban_pedestrian_footbridge',
  road_selected_variant_id:'timber_covered_bridge_route_v1'});
const pathAsset=PATHWAY_ASSETS.find(a=>a.id==='concrete_neighbourhood_walk_v1')!;
const path=(station:number)=>street('path',[[-20,station],[20,station]],pathAsset.sectionWidth,pathAsset.properties);

it('rejects intersecting bridge structures in either placement/edit direction',()=>{
  const crossing=street('other',[[-40,40],[40,40]],6,{...bridge.properties,plan_centerline:[[-40/111320,40/111320],[40/111320,40/111320]]});
  expect(specialistConnectionProblem(crossing,[bridge])).toBeTruthy();
  expect(specialistConnectionProblem(bridge,[crossing])).toBeTruthy();
});
it.each([3,40])('protects the bridge from a vehicle street at station%s',station=>{
  const road=street('road',[[-20,station],[20,station]],16);
  expect(specialistConnectionProblem(road,[bridge])).toBeTruthy();
  expect(specialistConnectionProblem(bridge,[road])).toBeTruthy();
});
it('admits a real surface path under the middle but protects the complete stairs and end supports',()=>{
  expect(specialistConnectionProblem(path(40),[bridge])).toBeNull();
  expect(specialistConnectionProblem(bridge,[path(40)])).toBeNull();
  expect(specialistConnectionProblem(path(3),[bridge])).toBeTruthy();
  expect(specialistConnectionProblem(path(15),[bridge])).toBeTruthy();
  expect(specialistConnectionProblem(path(16),[bridge])).toBeNull();
});
it('allows exact endpoint touch and rejects an unknown street merely relabelled as zero lanes',()=>{
  expect(specialistConnectionProblem(street('touch',[[0,-20],[0,0]],16),[bridge])).toBeNull();
  expect(specialistConnectionProblem(street('fake',[[-20,40],[20,40]],4,{lane_count:0}),[bridge])).toBeTruthy();
});
