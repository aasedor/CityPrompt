import { describe, it, expect } from 'vitest';
import type { SiteZone } from '@/types';
import { duplicateStreet } from './duplicateStreet';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
const line = [[0,0],[0,100/111320]];
const source = { id:'source', zone_type:'road', coordinates:bufferLineToPolygon(line,40), properties:{
  width:40, plan_centerline:line, plan_route_controls:line,
  road_selected_variant_id:'brt_bus_rapid_transit_corridor_v0', road_native_stops:[{id:'stop',stationM:32}],
  community_3d:{state:'compiled'}, _client_request_id:'old', connect_to_public_road:true,
} } as unknown as SiteZone;
describe('street copy',()=>{
  it('moves route, control points and footprint together, preserves stops and cannot mutate the original',()=>{
    const copy=duplicateStreet(source,60,20);
    const movedLine=copy.properties.plan_centerline as number[][];
    expect(movedLine[0][0]*111320).toBeCloseTo(60,0);
    expect(movedLine[0][1]*111320).toBeCloseTo(20);
    expect(copy.properties.plan_route_controls).toEqual(copy.properties.plan_centerline);
    expect(copy.properties.road_native_stops).toEqual(source.properties?.road_native_stops);
    expect(copy.properties.road_selected_variant_id).toBe(source.properties?.road_selected_variant_id);
    expect(copy.properties.community_3d).toBeUndefined();
    expect(copy.properties._client_request_id).toBeUndefined();
    expect(copy.properties.connect_to_public_road).toBeUndefined();
    copy.properties.road_native_stops![0].stationM=45;
    expect(source.properties?.road_native_stops?.[0].stationM).toBe(32);
    expect(source.properties?.plan_centerline).toEqual(line);
  });
  it('rejects invalid offsets and legacy fixed assemblies',()=>{
    for(const offsets of [[0,0],[NaN,20],[1001,0]])expect(()=>duplicateStreet(source,...offsets as [number,number])).toThrow();
    expect(()=>duplicateStreet({...source,properties:{...source.properties,validation_fixed_fixture:true}},50,0)).toThrow(/fixed/);
  });
});
