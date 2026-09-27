import {describe,it,expect} from 'vitest';
import type {SiteZone} from '@/types';
import {bufferLineToPolygon} from '@/utils/roadGeometry';
import {brtConnectionProblem} from './brtConnections';
import {BRT_VARIANT} from '@/components/viewer/globe/brtStreetProgram';

function street(id:string,line:number[][],width:number,brt=false):SiteZone {
  const coords=line.map(([x,y])=>[x/111320,y/111320]);
  return {id,project_id:'test',color:'#aaa',sort_order:0,created_at:'1',updated_at:'1',zone_type:'road',coordinates:bufferLineToPolygon(coords,width),properties:{width,plan_centerline:coords,
    road_archetype_id:brt?'brt_bus_rapid_transit_corridor':'neighborhood_main_street',
    road_selected_variant_id:brt?BRT_VARIANT:'student_main_street_v1',
    ...(brt?{road_native_stops:[{id:'chosen',stationM:80}]}:{})}} as SiteZone;
}
describe('BRT full stop reservations',()=>{
  const brt=street('brt',[[0,0],[0,200]],40,true);
  it('rejects another road crossing a station, preserving the original objects',()=>{
    const other=street('other',[[-80,80],[80,80]],18),before=JSON.stringify(brt);
    expect(brtConnectionProblem(other,[brt])).toMatch(/platform/);
    expect(JSON.stringify(brt)).toBe(before);
  });
  it('allows an endpoint connection away from station access',()=>{
    expect(brtConnectionProblem(street('end',[[-80,0],[0,0]],18),[brt])).toBeNull();
  });
  it('also catches moving the BRT station into an existing crossing',()=>{
    const other=street('other',[[-80,110],[80,110]],18);
    expect(brtConnectionProblem(brt,[other])).toMatch(/platform/);
  });
});
