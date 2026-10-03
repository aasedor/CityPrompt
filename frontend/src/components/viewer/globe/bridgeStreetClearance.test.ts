import {describe,it,expect} from 'vitest';
import {clearBridgeOverhead,bridgeClearanceKey} from './bridgeStreetClearance';
import {nativeStreetPilot,placeNativeStreetModules} from './nativeStreetPilot';
import {selectDetailedStreetZones} from './streetDetailLod';
import type {SiteZone} from '@/types';
const bridge={id:'bridge',zone_type:'road',coordinates:[],properties:{road_selected_variant_id:'landmark_signature_bridge_v2',plan_centerline:[[0,0],[0,260/111320]]}} as unknown as SiteZone;
describe('rigid bridge overhead reservations',()=>{
  it('keeps low market programs and removes entire conflicting lamps while preserving lamps outside the deck',()=>{
    const source=placeNativeStreetModules(nativeStreetPilot('student_market_street_v1')!,[{x:-60,y:130},{x:60,y:130}]);
    const result=clearBridgeOverhead(source,{lng:0,lat:0},[bridge],'market');
    expect(result.filter(p=>p.kind==='market_stall')).toEqual(source.filter(p=>p.kind==='market_stall'));
    expect(result.filter(p=>p.kind==='heritage_lantern').length).toBeLessThan(source.filter(p=>p.kind==='heritage_lantern').length);
    expect(result.some(p=>p.kind==='heritage_lantern')).toBe(true);
    expect(clearBridgeOverhead(source,{lng:0,lat:0},[],'market')).toBe(source);
    expect(clearBridgeOverhead(source,{lng:0,lat:0},[bridge],'bridge')).toBe(source);
  });
  it('changes capture context on bridge movement or deletion and preserves all native programs beyond the LOD budget',()=>{
    const moved={...bridge,properties:{...bridge.properties,plan_centerline:[[1,0],[1,260/111320]]}};
    expect(bridgeClearanceKey([bridge])).not.toBe(bridgeClearanceKey([moved]));
    expect(bridgeClearanceKey([bridge])).not.toBe(bridgeClearanceKey([]));
    const native=Array.from({length:165},(_,i)=>({...bridge,id:String(i)}));
    expect(selectDetailedStreetZones(native)).toHaveLength(165);
  });
  it('never drops an entire rigid structure as overhead furniture',()=>{
    const source=placeNativeStreetModules(nativeStreetPilot('landmark_signature_bridge_v2')!,[{x:-130,y:130},{x:130,y:130}]);
    expect(source.some(p=>p.kind==='bridge_structure')).toBe(true);
    expect(clearBridgeOverhead(source,{lng:0,lat:0},[bridge],'other')).toEqual(source);
  });
});
