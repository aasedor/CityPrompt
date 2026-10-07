import { nativePavingProbe } from '@/features/parks/nativeParkAccess';
import { nativeParkLayouts, nativeParkProperties } from '@/features/parks/nativeParkRegistry';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
vi.mock('@/features/parks/nativeParkAccess',()=>({nativePavingProbe:vi.fn()}));
import { describe, expect, it, vi, beforeEach } from 'vitest';
import type { SiteZone } from '@/types';
import { rectangleAt } from '@/features/pickPlace/geometry';
import { authoredCameraGround } from './authoredCameraGround';
import {bufferLineToPolygon} from '@/utils/roadGeometry';
import { canalRoute } from './canalRoute';
import { roundMetricStreetCenterline } from '@/utils/streetRouteCurves';

const boundary: SiteZone = { id:'site', project_id:'test', zone_type:'site_boundary',
  coordinates:rectangleAt([-114,51],100,100), is_active_boundary:true,
  properties:{terrain_elevation_m:1103,community_3d_mask_existing_tiles:true},
  color:'#aaa',sort_order:0,created_at:'now',updated_at:'now' };
describe('camera ground for authored communities',()=>{
  it('walks the relocated canal arch and bent banks without creating a floor over water', () => {
    const points = roundMetricStreetCenterline([[0,0],[0,120],[140,220]],54).map(([x,y])=>({x,y}));
    const layout = canalRoute(points), sx = metersPerDegLon(51);
    const ll = ([x,y]: number[]) => [-114+x/sx,51+y/111320];
    const line = points.map(p=>ll([p.x,p.y]));
    const canal = {...boundary,id:'canal',zone_type:'road' as const,is_active_boundary:false,
      coordinates:bufferLineToPolygon(line,36),properties:{width:36,
        road_selected_variant_id:'amsterdam_gracht_v1',plan_centerline:line}};
    const large = {...boundary,coordinates:rectangleAt([-114,51],1000,1000)};
    for (const [offset,station,height] of [[0,layout.crossing!,1.72],[0,30,-2.05],[13.5,180,.12]]) {
      const [lng,lat] = ll(layout.point(offset,station,0));
      expect(authoredCameraGround([large,canal],lng,lat,1103)).toBeCloseTo(1103+height,2);
    }
  });
  it('keeps the elevated railway paths at ground level even when the picked deck is above them',()=>{
    const line=[[-114,51-40/111320],[-114,51+40/111320]];
    const rail={...boundary,id:'rail',zone_type:'road' as const,is_active_boundary:false,coordinates:bufferLineToPolygon(line,26),
      properties:{width:26,road_selected_variant_id:'student_elevated_garden_rail_v1',plan_centerline:line}};
    for(const measured of [1103,1111,1115])expect(authoredCameraGround([boundary,rail],-114,51,measured,1111)).toBeCloseTo(1103.025);
  });
  beforeEach(()=>vi.resetAllMocks());
  it('keeps a pedestrian below the bridge while deck and ramp users follow their upper surface',()=>{
    const line=[[-114,51-130/111320],[-114,51+130/111320]];
    const bridge={...boundary,id:'bridge',zone_type:'road' as const,is_active_boundary:false,coordinates:bufferLineToPolygon(line,36),
      properties:{width:36,road_selected_variant_id:'landmark_signature_bridge_v2',plan_centerline:line}};
    const large={...boundary,coordinates:rectangleAt([-114,51],100,300)};
    expect(authoredCameraGround([large,bridge],-114,51,1103)).toBe(1103);
    expect(authoredCameraGround([large,bridge],-114,51,1107.3)).toBeCloseTo(1107.3);
    expect(authoredCameraGround([large,bridge],-114,51,1103,1107.3)).toBeCloseTo(1107.3);
    expect(authoredCameraGround([large,bridge],-114,51,1103,1103)).toBeCloseTo(1107.3);
    // The caller still rejects an actual arch hit over three metres above this plane.
    expect(authoredCameraGround([large,bridge],-114,51,1103,1126)).toBeCloseTo(1107.3);
    expect(authoredCameraGround([large,bridge],-114,51-90/111320,1105)).toBeCloseTo(1105.15,2);
  });
  it('uses verified native steps and lawn heights in the saved placement frame',()=>{
    const layout=nativeParkLayouts.find(p=>p.id==='amphitheater_lawn_v0--native-v1')!;
    const coordinates=rectangleAt([-114,51],70,70,90);
    const park={...boundary,id:'performance',zone_type:'green_space' as const,is_active_boundary:false,coordinates,properties:nativeParkProperties({},layout,coordinates)};
    const probe=vi.fn(([x,y]:[number,number])=>Math.abs(x+30)<.1 && Math.abs(y)<.1 ? .6667 : null);
    vi.mocked(nativePavingProbe).mockReturnValue(probe);
    const f=park.properties.green_space_native_layout as {frame:{longitude:number;latitude:number;yaw:number}};
    const lng=f.frame.longitude-30*Math.cos(f.frame.yaw)/metersPerDegLon(f.frame.latitude);
    const lat=f.frame.latitude-30*Math.sin(f.frame.yaw)/METERS_PER_DEG_LAT;
    expect(authoredCameraGround([boundary,park],lng,lat,1099)).toBeCloseTo(1103.6667,3);
    expect(nativePavingProbe).toHaveBeenCalledWith(layout,true);
    expect(authoredCameraGround([boundary,park],-114,51,1099)).toBe(1103);
    vi.mocked(nativePavingProbe).mockImplementation(()=>{throw Promise.resolve()});
    expect(authoredCameraGround([boundary,park],lng,lat,1099)).toBe(1103);
    const retained={...boundary,properties:{...boundary.properties,community_3d_mask_existing_tiles:false}};
    expect(authoredCameraGround([retained,park],lng,lat,1099)).toBe(1099);
  });
  it('uses the redevelopment level even when Google terrain is below or above it',()=>{
    expect(authoredCameraGround([boundary],-114,51,1099)).toBe(1103);
    expect(authoredCameraGround([boundary],-114,51,1110)).toBe(1103);
    expect(authoredCameraGround([boundary],-113,51,1099)).toBe(1099);
  });
  it('does not flatten landscape or retained sites',()=>{
    expect(authoredCameraGround([{...boundary,properties:{...boundary.properties,terrain_strategy:'landscape'}}],-114,51,1099)).toBe(1099);
    expect(authoredCameraGround([{...boundary,properties:{...boundary.properties,community_3d_mask_existing_tiles:false}}],-114,51,1099)).toBe(1099);
  });
  it('respects an explicit terrace inside the prepared site',()=>{
    const plot={...boundary,id:'house',zone_type:'building' as const,is_active_boundary:false,coordinates:rectangleAt([-114,51],15,20),properties:{proposed_terrace:{version:1,offsetM:1}}};
    expect(authoredCameraGround([boundary,plot],-114,51,1099)).toBe(1104);
  });
});
