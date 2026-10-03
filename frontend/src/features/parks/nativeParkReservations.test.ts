import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { nativeParkApproaches, clearsNativeParkApproaches, type NativeParkApproach } from './nativeParkReservations';
import { nativeParkLayouts, nativeParkProperties } from './nativeParkRegistry';
import { rectangleAt } from '@/features/pickPlace/geometry';
import { snapPlacement } from '@/features/pickPlace/snapPlacement';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';

const ll = (x:number, y:number):[number,number] => [-114+x/metersPerDegLon(51),51+y/METERS_PER_DEG_LAT];
const metadata = {project_id:'test', color:'#fff', sort_order:0, created_at:'2026-09-26', updated_at:'2026-09-26'};
describe('native park approach reservations',()=>{
  it('keeps a full tree envelope clear and restores it when the approach disappears',()=>{
    const path:NativeParkApproach={owner:{} as SiteZone,points:[ll(0,-10),ll(0,10)],widthM:2};
    expect(clearsNativeParkApproaches(...ll(5,0),5.8,[path])).toBe(false);
    expect(clearsNativeParkApproaches(...ll(8,0),5.8,[path])).toBe(true);
    expect(clearsNativeParkApproaches(...ll(0,0),5.8,[])).toBe(true);
  });
  it('derives the existing native approach without reserving a deleted park',()=>{
    const layout=nativeParkLayouts.find(p=>p.id==='basketball_court_v1--native-v1')!;
    const coordinates=rectangleAt(ll(0,19.5),52,39);
    const park:SiteZone={...metadata,id:'park',zone_type:'green_space',coordinates,properties:nativeParkProperties({},layout,coordinates)};
    const line=[ll(-40,-6),ll(40,-6)];
    const street:SiteZone={...metadata,id:'street',zone_type:'road',coordinates:bufferLineToPolygon(line,10),properties:{road_archetype_id:'narrow_residential_street',width:10,plan_centerline:line}};
    const boundary:SiteZone={...metadata,id:'site',zone_type:'site_boundary',is_active_boundary:true,coordinates:rectangleAt(ll(0,20),160,140),properties:{terrain_elevation_m:1000}};
    const paths=nativeParkApproaches([park,street,boundary],true);
    expect(paths).toHaveLength(1);
    expect(clearsNativeParkApproaches(...ll(0,0),.5,paths)).toBe(false);
    expect(nativeParkApproaches([street,boundary],true)).toEqual([]);
    const fartherLine=[ll(-40,-10),ll(40,-10)];
    const fartherStreet={...street,coordinates:bufferLineToPolygon(fartherLine,10),properties:{...street.properties,plan_centerline:fartherLine}};
    const next=snapPlacement(rectangleAt(ll(0,-1),1,1),[park,fartherStreet,boundary],boundary);
    expect(next.snapped).toBe(true);
    expect(next.problem).toBeNull();
    const center=next.coordinates.reduce((sum,p)=>[sum[0]+p[0]/4,sum[1]+p[1]/4],[0,0]);
    expect(clearsNativeParkApproaches(center[0],center[1],.5,nativeParkApproaches([park,fartherStreet,boundary],true))).toBe(true);
  });
});
