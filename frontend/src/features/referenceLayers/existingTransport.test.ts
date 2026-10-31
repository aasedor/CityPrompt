import { describe, expect, it } from 'vitest';
import type { ReferenceLayer } from './api';
import { CALGARY_TRANSPORT_ROOT, existingTransport, isLegacyCalgaryTransportLayer } from './existingTransport';

function layer(properties:Record<string,unknown>={}):ReferenceLayer {
  return {id:'layer',project_id:'pilot',name:'Context',source_filename:'context.geojson',source_crs:'EPSG:4326',description:null,kind:'reference',feature_count:1,bounds:[-114.001,51,-114,51],warnings:[],color:'#0088aa',opacity:0.7,created_at:'2026-09-06',source_url:CALGARY_TRANSPORT_ROOT,feature_collection:{type:'FeatureCollection',features:[{
    type:'Feature',geometry:{type:'LineString',coordinates:[[-114,51,0],[-114.001,51,0]]},
    properties:{cp_transport_source:'Pathways_close_view',GLOBALID:'path',LIFE_CYCLE_STATUS:'ACTIVE',OPERATIONAL:'OPEN',ASSET_TYPE:'PATHWAY',...properties},
  }]}};
}
describe('Calgary existing transport snapshot',()=>{
  it('recognizes old route snapshots while preserving unrelated imports and zoning',()=>{
    expect(isLegacyCalgaryTransportLayer(layer())).toBe(true);
    expect(isLegacyCalgaryTransportLayer({...layer(), source_url:'https://example.com'})).toBe(false);
    expect(isLegacyCalgaryTransportLayer({...layer(), kind:'zoning'})).toBe(false);
    expect(isLegacyCalgaryTransportLayer({...layer(),feature_collection:{type:'FeatureCollection',features:[]}})).toBe(false);
  });
  it('retains mapped paths separately, deduplicates overlapping services, and does not assert height or unknown width',()=>{
    const first=layer(),second=layer({cp_transport_source:'Walkway_Sidewalk_Connections_view'});
    second.id='second';
    const result=existingTransport([second,first]);
    expect(result.lines).toHaveLength(1);
    expect(result.lines[0].points[0]).toEqual([-114,51]);
    expect(result.lines[0].widthM).toBeNull();
    expect(result.lines[0].id).toBe('existing:layer:path:path:0');
  });
  it.each([{LIFE_CYCLE_STATUS:'PLANNED'},{OPERATIONAL:'CLOSED'},{ASSET_TYPE:'BRIDGE'},{OWNERSHIP:'PRIVATE'},{cp_transport_source:'unknown'}])('omits ineligible pedestrian targets %j',props=>{
    expect(existingTransport([layer(props)]).lines).toHaveLength(0);
  });
  it('does not interpret generic GIS or zoning as transport',()=>{
    expect(existingTransport([{...layer(),source_url:'https://example.com'}]).lines).toHaveLength(0);
  });
  it('keeps built road centrelines as barriers, never pedestrian targets',()=>{
    expect(existingTransport([layer({cp_transport_source:'Street_Centreline',BUILT_STATUS:'Built'})]).lines[0].kind).toBe('road');
  });
  it('offers access roads only when explicitly recorded for pedestrian or multiuse travel',()=>{
    expect(existingTransport([layer({ASSET_TYPE:'CONX-ACCESS ROAD',USAGE_TYPE:'UNKNOWN'})]).lines).toHaveLength(0);
    expect(existingTransport([layer({ASSET_TYPE:'CONX-ACCESS ROAD',USAGE_TYPE:'MULTIUSE',WIDTH:3})]).lines[0]).toMatchObject({label:'Shared access route',widthM:3});
  });
});
