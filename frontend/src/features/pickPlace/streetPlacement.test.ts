import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { bufferLineToPolygon, extractCenterline } from '@/utils/roadGeometry';
import { resolvePilotStreetSectionProfile } from '@/components/viewer/globe/streetSectionProfiles';
import { resolveManualParkAccess } from '@/components/viewer/globe/parkAccessConnections';
import { addStreetBend, CALGARY_LOCAL_PLACEMENT, reshapeStreetPoint, streetCoordinateUpdate, streetRouteProblem } from './streetPlacement';
import { STREET_ASSETS } from './assetRegistry';
import { isFixedSectionStreet, streetAssetForZone } from './streetPlacement';

const mLon = 111320*Math.cos(51*Math.PI/180);
const ll = ([x,y]:number[])=>[-114+x/mLon,51+y/111320];
const xy = ([x,y]:number[])=>[(x+114)*mLon,(y-51)*111320];
const line = [[0,0],[70,0]].map(ll);
const zone:SiteZone = {id:'street',project_id:'pilot',color:'#777777',sort_order:0,created_at:'2026-09-05',updated_at:'2026-09-05',zone_type:'road',coordinates:bufferLineToPolygon(line,16), properties:{...CALGARY_LOCAL_PLACEMENT.properties,plan_centerline:line}};

describe('fixed sections across street types', () => {
  it.each(STREET_ASSETS.map(asset => [asset.label, asset] as const))('%s retains its section through route edits and reopening', (_, asset) => {
    const width = asset.sectionWidth;
    const saved: SiteZone = JSON.parse(JSON.stringify({ ...zone, coordinates: bufferLineToPolygon(line, width), properties: { ...asset.properties, plan_centerline: line } }));
    expect(streetAssetForZone(saved)).toBe(asset);
    const profile = resolvePilotStreetSectionProfile(saved)!;
    expect(profile.rowM).toBe(width);
    expect(profile.bands.reduce((sum, band) => sum + band.widthM, 0)).toBeCloseTo(width, 8);
    const bend = addStreetBend(saved)!;
    const reshaped = reshapeStreetPoint(bend, 1, ll([35, 8]), width);
    const updated = streetCoordinateUpdate(saved, reshaped);
    expect(updated.properties?.width).toBe(width);
    expect(updated.properties?.plan_centerline).toEqual(extractCenterline(reshaped));
    const a = xy(reshaped[0]), b = xy(reshaped[reshaped.length - 1]);
    expect(Math.hypot(a[0]-b[0], a[1]-b[1])).toBeCloseTo(width, 2);
    const moved = streetCoordinateUpdate({ ...saved, ...updated }, reshaped.map(([x,y]) => [x, y + 2/111320]));
    expect(moved.properties?.width).toBe(width);
    expect(streetAssetForZone({ ...saved, ...moved })).toBe(asset);
    expect(streetRouteProblem(bufferLineToPolygon([[0,0],[width-1,0]].map(ll),width),width)).toContain(`${width} m`);
    expect(streetRouteProblem(bufferLineToPolygon([[0,0],[width+1,0]].map(ll),width),width)).toBeNull();
  });
  it('allows a short narrow-lane segment that the old 16 m rule rejected', () => {
    const asset = STREET_ASSETS.find(a=>a.properties.road_archetype_id==='green_alley')!;
    const narrow = { ...zone, coordinates: bufferLineToPolygon([[0,0],[12,0]].map(ll),5), properties: asset.properties };
    expect(addStreetBend(narrow)).not.toBeNull();
    expect(streetRouteProblem(narrow.coordinates,5)).toBeNull();
  });
  it('does not lock an unrelated or changed advanced street to a stale placement marker', () => {
    expect(isFixedSectionStreet({ ...zone, properties: { ...zone.properties, road_archetype_id: 'another_type' } })).toBe(false);
    expect(isFixedSectionStreet({ ...zone, properties: { ...zone.properties, road_selected_variant_id: 'another_variant' } })).toBe(false);
  });
});

describe('Calgary local route placement',()=>{
  it.each([{points:[[0,0],[60,40]]}, {points:[[0,0],[40,0],[40,40]]}])('keeps every segment 16 m wide including diagonal and bent routes',({points})=>{
    const polygon=bufferLineToPolygon(points.map(ll),16).map(xy), n=points.length;
    for(let i=0;i<n-1;i++){
      const a=points[i],b=points[i+1],dx=b[0]-a[0],dy=b[1]-a[1],length=Math.hypot(dx,dy);
      for(const j of [i,i+1]) for(const k of [j,2*n-1-j]){
        expect(Math.abs((polygon[k][0]-a[0])*dy-(polygon[k][1]-a[1])*dx)/length).toBeCloseTo(8,5);
      }
    }
  });
  it('moves the persisted source line with the buffer and retains the exact authored bands',()=>{
    const moved=zone.coordinates.map(([x,y])=>[x,y+20/111320]);
    const patch=streetCoordinateUpdate(zone,moved);
    expect(patch.properties?.plan_centerline).toEqual(extractCenterline(moved));
    expect(zone.properties?.plan_centerline).toEqual(line);
    const profile=resolvePilotStreetSectionProfile({...zone,properties:patch.properties})!;
    expect(profile.rowM).toBe(16);
    expect(profile.bands.map(b=>b.widthM)).toEqual([.3,1.8,2.65,3.25,3.25,2.65,1.8,.3]);
  });
  it('adds and moves a bend without widening the road and rejects too-short/tight segments',()=>{
    const added=addStreetBend(zone)!;
    expect(extractCenterline(added)).toHaveLength(3);
    const reshaped=reshapeStreetPoint(added,1,ll([35,10]));
    expect(xy(extractCenterline(reshaped)[1])[1]).toBeCloseTo(10,5);
    expect(streetRouteProblem(reshaped)).toBeNull();
    expect(streetRouteProblem(bufferLineToPolygon([[0,0],[5,0]].map(ll),16))).toContain('16 m');
    expect(streetRouteProblem(bufferLineToPolygon([[0,0],[40,0],[4,2]].map(ll),16))).toContain('gentler bend');
  });
  it('connects the adaptive park to the near-side sidewalk and invalidates a moved route',()=>{
    const park:SiteZone={...zone,id:'park',zone_type:'green_space',coordinates:[[15,10],[55,10],[55,45],[15,45]].map(ll),properties:{green_space_archetype_id:'neighborhood_park',green_space_selected_variant_id:'neighborhood_park_v0',neighborhood_park_layout:'adaptive_rustic_v1'}};
    const boundary:SiteZone={...zone,id:'site',zone_type:'site_boundary',is_active_boundary:true,coordinates:[[-20,-60],[100,-60],[100,70],[-20,70]].map(ll),properties:{terrain_elevation_m:1000}};
    const plan=resolveManualParkAccess([zone,park,boundary]);
    expect(plan.parks[0].connections).toHaveLength(1);
    const connection=plan.parks[0].connections[0];
    expect(connection.streetBand).toBe('sidewalk');
    expect(xy(connection.streetPoint)[1]).toBeGreaterThan(6);
    expect(connection.path.map(xy).every(p=>p[1]>3.25)).toBe(true);
    const moved=streetCoordinateUpdate(zone,zone.coordinates.map(([x,y])=>[x,y-40/111320]));
    expect(resolveManualParkAccess([{...zone,...moved},park,boundary]).parks[0].connections).toHaveLength(0);
  });
});
