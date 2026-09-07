import {describe,it,expect} from 'vitest';
import * as THREE from 'three';
import type {SiteZone} from '@/types';
import {buildTerraceScene,suggestTerracePath} from './terraceScene';
import {cutGeometry} from './terraceGeometry';
import {resolvePreparedSiteTerrainForZone} from './sitePreparationSurface';
import {METERS_PER_DEG_LAT,metersPerDegLon} from '../mapEngine/geoUtils';
import {resolveParkSpecialtyStructureKind} from './parkGroundProfiles';

const world=(x:number,y:number)=>[-114+x/metersPerDegLon(51),51+y/METERS_PER_DEG_LAT];
function zone(id:string,type:SiteZone['zone_type'],x:number,y:number,w:number,h:number,properties:Record<string,unknown>={}):SiteZone {
 return {id,project_id:'test',zone_type:type,coordinates:[world(x,y),world(x+w,y),world(x+w,y+h),world(x,y+h)],properties,color:'#ffffff',sort_order:0,created_at:'',updated_at:'',is_active_boundary:type==='site_boundary'};
}
const site=()=>zone('site','site_boundary',0,0,100,100,{terrain_elevation_m:1000});
const path={version:1,targetId:'b',sourceEdge:1,targetEdge:3,sourcePosition:.5,targetPosition:.5,widthM:2,approachM:2};
const pair=()=>[site(),zone('a','building',10,30,20,20,{proposed_terrace:{version:1,offsetM:2},terrace_connection:path}),zone('b','building',50,30,20,20,{proposed_terrace:{version:1,offsetM:-1}})];
describe('object terraces and explicit graded paths',()=>{
 it('finds an unobstructed inward park approach and keeps it after serialization',()=>{
  const park=zone('b','green_space',10,10,30,30,{proposed_terrace:{version:1,offsetM:-1},green_space_archetype_id:'neighborhood_park',green_space_selected_variant_id:'neighborhood_park_v0',neighborhood_park_layout:'adaptive_rustic_v1'});
  park.properties={...park.properties,public_realm_fallback:{state:'family_pending'}};
  expect(resolveParkSpecialtyStructureKind(park)).toBe('neighborhood_park_v0_sticker_assembly');
  expect(resolveParkSpecialtyStructureKind({...park,properties:{...park.properties,neighborhood_park_layout:undefined}})).toBeNull();
  const house=zone('a','building',25,54,15,20,{proposed_terrace:{version:1,offsetM:1}});
  const zones=[site(),house,park],suggestion=suggestTerracePath(zones,'a','b',{...path,version:1});
  expect(suggestion).not.toBeNull();
  house.properties={...house.properties,terrace_connection:suggestion};
  const result=buildTerraceScene(zones,1000).paths[0];
  expect(result.status).toBe('connected');expect(result.gradePercent).toBeGreaterThan(5);
  expect(result.points).toHaveLength(4);
 });
 it('shares offset levels, reports grade and preserves a steep connection',()=>{
  const zones=pair(),scene=buildTerraceScene(zones,999);
  expect(scene.terraces).toHaveLength(2);
  expect(scene.paths[0].status).toBe('connected');
  expect(scene.paths[0].points.map(p=>p[2])).toEqual([1002,1002,999,999]);
  expect(scene.paths[0].gradePercent).toBeCloseTo(15,2);
  expect(scene.paths[0].lengthM).toBeCloseTo(24,2);
  expect(scene.paths[0].reason).toContain('Steep');
 });
 it('recomputes anchors on movement, resize, and site level changes',()=>{
  const zones=pair(); zones[2]={...zone('b','building',60,30,25,20),properties:zones[2].properties};
  zones[0].properties!.terrain_elevation_m=1010;
  const p=buildTerraceScene(zones,999).paths[0];
  expect(p.status).toBe('connected');expect(p.gradePercent).toBeCloseTo(10,2);
  expect(p.points.map(v=>v[2])).toEqual([1012,1012,1009,1009]);
  expect(buildTerraceScene(JSON.parse(JSON.stringify(zones)),999).paths).toEqual([p]);
 });
 it('leaves a blocked or deleted destination unresolved',()=>{
  const zones=pair();zones.push(zone('obstacle','building',35,35,10,10));
  expect(buildTerraceScene(zones,999).paths[0].status).toBe('unresolved');
  expect(buildTerraceScene(pair().filter(z=>z.id!=='b'),999).paths[0].status).toBe('unresolved');
 });
 it('does not change retained terrain or accept invalid offsets',()=>{
  const zones=pair();zones[1].properties!.proposed_terrace={version:1,offsetM:Infinity};
  expect(resolvePreparedSiteTerrainForZone(zones[1],zones,999)).toBe(1000);
  zones[0].properties!.community_3d_mask_existing_tiles=false;
  expect(buildTerraceScene(zones,999).terraces).toHaveLength(0);
 });
});
function area(g:THREE.BufferGeometry){const p=g.getAttribute('position');let sum=0;for(let i=0;i<p.count;i+=3){const a=new THREE.Vector3().fromBufferAttribute(p,i),b=new THREE.Vector3().fromBufferAttribute(p,i+1),c=new THREE.Vector3().fromBufferAttribute(p,i+2);sum+=b.sub(a).cross(c.sub(a)).length()/2;}return sum;}
describe('terrace openings',()=>{
 it('subtracts adjacent and overlapping openings once without changing the source',()=>{
  const source=new THREE.PlaneGeometry(10,10); const cut=cutGeometry(source,[[[-3,-3],[1,-3],[1,3],[-3,3]],[[0,-3],[3,-3],[3,3],[0,3]]]);
  expect(area(cut)).toBeCloseTo(64,4);expect(source.getAttribute('position').count).toBe(4);source.dispose();cut.dispose();
 });
 it('cuts an entrance out of a vertical retaining face',()=>{
  const source=new THREE.PlaneGeometry(10,2).rotateX(Math.PI/2).translate(0,0,1);
  const cut=cutGeometry(source,[[[-1,-1],[1,-1],[1,1],[-1,1]]]);
  expect(area(cut)).toBeCloseTo(16,4);source.dispose();cut.dispose();
 });
});
