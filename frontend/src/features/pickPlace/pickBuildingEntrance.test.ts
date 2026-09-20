import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';
import { resolveBuildingGroundContact, type GroundPoint } from '@/components/viewer/globe/buildingGroundContact';
import type { SharedSiteGroundState } from '@/components/viewer/globe/SharedSiteGroundProvider';
import { rectangleAt } from './geometry';
import { entrancePickOccluded, entrancePickZoneKey, pickBuildingEntrance, type NativeEntranceHit } from './pickBuildingEntrance';
import { preparedEntranceGround } from '@/components/viewer/globe/preparedEntranceGround';

const geo = ([x,y]:number[]):GroundPoint => [-114+x/metersPerDegLon(51),51+y/METERS_PER_DEG_LAT];
const zone = (id:string,zone_type:SiteZone['zone_type'],coordinates:number[][],properties:SiteZone['properties']={}):SiteZone =>
  ({id,project_id:'test',zone_type,coordinates,properties,color:'#aaa',sort_order:0,created_at:'test',updated_at:'test'});
function fixture(degrees=0, centerY=-15, groundHeight=(lng:number,lat:number)=>100+0*lng+0*lat) {
  const r=degrees*Math.PI/180, rotate=([x,y]:number[]):GroundPoint=>[x*Math.cos(r)-y*Math.sin(r),x*Math.sin(r)+y*Math.cos(r)];
  const center=geo(rotate([0,centerY]));
  const entrance={version:1,xM:0,yM:8,referenceWidthM:12,referenceDepthM:20,scaleWithPlot:true,streetId:'street',widthM:1.8};
  const house=zone('house','building',rectangleAt(center,12,20,degrees),{pedestrian_building_entrance:entrance});
  const line=[geo(rotate([-40,0])),geo(rotate([40,0]))];
  const street=zone('street','road',bufferLineToPolygon(line,6),{road_archetype_id:'yield_street',width:6,lane_count:1,plan_centerline:line});
  const boundary={...zone('boundary','site_boundary',rectangleAt(geo([0,0]),150,150)),is_active_boundary:true};
  const ground:SharedSiteGroundState={status:'ready',snapshot:null,heightAt:groundHeight,contains:()=>true,revision:'test',isCurrent:()=>true};
  const footprints=[([[-4,-8],[4,-8],[4,8],[-4,8]]).map(rotate)];
  const contact=resolveBuildingGroundContact(footprints,...center,ground);
  const point=rotate([1,7.8]);
  const hit:NativeEntranceHit={point:[...point,.16],footprints,lng:center[0],lat:center[1],contact};
  const zones=[house,street,boundary];
  const pick=(h=hit,g=ground,inventory=zones)=>pickBuildingEntrance(h,house,inventory,house.properties,inventory.map(z=>z.id),g);
  return {house,zones,hit,ground,pick};
}
describe('native entrance step picking',()=>{
  it.each([0,95,-90])('maps a real edge back to plot coordinates at %s degrees and validates its approach',degrees=>{
    const f=fixture(degrees),before=JSON.stringify(f.zones),picked=f.pick();
    expect(picked).toMatchObject({result:{status:'ready',anchor:{xM:1,yM:8,heightAboveBaseM:0,scaleWithPlot:false,streetId:'street'}}});
    expect(JSON.stringify(f.zones)).toBe(before);
  });
  it('rejects roofs and points far from the native step edge',()=>{
    const f=fixture();
    expect(f.pick({...f.hit,point:[1,7.8,3]})).toMatchObject({error:expect.stringContaining('lowest entrance step')});
    expect(f.pick({...f.hit,point:[0,0,0]})).toMatchObject({error:expect.stringContaining('outer edge')});
  });
  it('picks and checks the same authored level used by a prepared-site house',()=>{
    const f=fixture();
    const prepared=preparedEntranceGround(f.zones[2],100)!;
    const hit={...f.hit,contact:resolveBuildingGroundContact(f.hit.footprints,f.hit.lng,f.hit.lat,prepared)};
    expect(f.pick(hit,prepared)).toMatchObject({result:{status:'ready',anchor:{xM:1,yM:8}}});
    expect(f.pick(hit,{...prepared,heightAt:()=>101})).toMatchObject({error:expect.stringContaining('still aligning')});
    expect(prepared.heightAt(...geo([100,100]))).toBeNull();
  });
  it('rejects pending, synchronously stale, draft, and mismatched model ground',()=>{
    const f=fixture();
    for(const ground of [{...f.ground,status:'sampling' as const},{...f.ground,isCurrent:()=>false},{...f.ground,preview:true}])
      expect(f.pick(f.hit,ground)).toMatchObject({error:expect.stringContaining('Ground is still')});
    expect(f.pick(f.hit,{...f.ground,heightAt:()=>101})).toMatchObject({error:expect.stringContaining('still aligning')});
  });
  it('reports a missing street without discarding the picked draft point',()=>{
    const f=fixture();
    expect(f.pick(f.hit,f.ground,f.zones.filter(z=>z.id!=='street'))).toMatchObject({result:{status:'unresolved',anchor:{xM:1,yM:8},message:expect.stringContaining('missing or hidden')}});
  });
  it('gives setback recovery when a raised step has too little run',()=>{
    const f=fixture(0,-12,(_lng,lat)=>(lat-51)*METERS_PER_DEG_LAT < -3.9 ? 101.5:100);
    expect(f.pick()).toMatchObject({result:{status:'unresolved',message:expect.stringContaining('farther from the street')}});
  });
  it('invalidates a picking session on optimistic geometry edits even before updated_at changes',()=>{
    const f=fixture();
    expect(entrancePickZoneKey({...f.house,coordinates:rectangleAt(geo([2,-15]),12,20)})).not.toBe(entrancePickZoneKey(f.house));
  });
  it('blocks a pick through visible foreground geometry, but ignores hidden geometry and editor overlays',()=>{
    const f=fixture(), scene=new THREE.Scene();
    const mesh=new THREE.Mesh(new THREE.BoxGeometry(2,2,2),new THREE.MeshBasicMaterial());
    mesh.position.z=5;scene.add(mesh);scene.updateMatrixWorld(true);
    const hit={...f.hit,ray:{origin:[0,0,10] as [number,number,number],direction:[0,0,-1] as [number,number,number],distance:10}};
    expect(entrancePickOccluded(scene,hit)).toBe(true);
    mesh.visible=false;expect(entrancePickOccluded(scene,hit)).toBe(false);
    mesh.visible=true;mesh.userData.siteforgeExcludeFromDirect3DCapture=true;
    expect(entrancePickOccluded(scene,hit)).toBe(false);
    mesh.geometry.dispose();mesh.material.dispose();
  });
  it('does not treat the transparent margin of a tree billboard as a visible obstruction',()=>{
    const f=fixture(),scene=new THREE.Scene(),data=new Uint8Array([255,255,255,0]);
    const texture=new THREE.DataTexture(data,1,1);texture.needsUpdate=true;
    const material=new THREE.MeshBasicMaterial({map:texture,alphaTest:.18});
    const mesh=new THREE.Mesh(new THREE.PlaneGeometry(2,2),material);mesh.position.z=5;scene.add(mesh);scene.updateMatrixWorld(true);
    const hit={...f.hit,ray:{origin:[0,0,10] as [number,number,number],direction:[0,0,-1] as [number,number,number],distance:10}};
    expect(entrancePickOccluded(scene,hit)).toBe(false);
    data[3]=255;expect(entrancePickOccluded(scene,hit)).toBe(true);
    mesh.geometry.dispose();material.dispose();texture.dispose();
  });
});
