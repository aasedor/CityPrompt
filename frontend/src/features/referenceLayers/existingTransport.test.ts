import { afterEach, describe, expect, it, vi } from 'vitest';
import type { ReferenceLayer } from './api';
import { CALGARY_TRANSPORT_ROOT, existingTransport, fetchCalgaryTransport } from './existingTransport';

function layer(properties:Record<string,unknown>={}):ReferenceLayer {
  return {id:'layer',project_id:'pilot',name:'Context',source_filename:'context.geojson',source_crs:'EPSG:4326',description:null,kind:'reference',feature_count:1,bounds:[-114.001,51,-114,51],warnings:[],color:'#0088aa',opacity:0.7,created_at:'2026-09-06',source_url:CALGARY_TRANSPORT_ROOT,feature_collection:{type:'FeatureCollection',features:[{
    type:'Feature',geometry:{type:'LineString',coordinates:[[-114,51,0],[-114.001,51,0]]},
    properties:{cp_transport_source:'Pathways_close_view',GLOBALID:'path',LIFE_CYCLE_STATUS:'ACTIVE',OPERATIONAL:'OPEN',ASSET_TYPE:'PATHWAY',...properties},
  }]}};
}
afterEach(()=>vi.unstubAllGlobals());
describe('Calgary existing transport snapshot',()=>{
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
  it('fetches bounded WGS84 snapshots and retains provenance',async()=>{
    const fetcher=vi.fn().mockResolvedValue({ok:true,json:async()=>({type:'FeatureCollection',features:layer().feature_collection.features})});
    vi.stubGlobal('fetch',fetcher);
    const features=await fetchCalgaryTransport([-114.01,51,-114,51.005]);
    expect(features).toHaveLength(3);expect(features[0].properties.cp_transport_source).toBe('Street_Centreline');
    expect(fetcher.mock.calls[0][0]).toContain('outSR=4326');
  });
  it('rejects oversized areas and truncated datasets rather than silently losing context',async()=>{
    await expect(fetchCalgaryTransport([-115,50,-113,52])).rejects.toThrow('smaller');
    vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:true,json:async()=>({type:'FeatureCollection',features:[],exceededTransferLimit:true})}));
    await expect(fetchCalgaryTransport([-114.01,51,-114,51.005])).rejects.toThrow('smaller site');
  });
});
