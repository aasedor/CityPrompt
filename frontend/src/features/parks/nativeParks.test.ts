import { describe,it,expect } from 'vitest';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import { rectangleAt } from '@/features/pickPlace/geometry';
import { nativeParkLayouts,nativeParkProperties,nativeParkFitProblem,nativeParkEditProperties,readNativePark } from './nativeParkRegistry';
import { parkLayoutProposal } from './ParkLayoutControls';
import { assertNativeParksReady, waitForNativeParksReady } from './NativeParkLayer';
import { hasExecutablePublicRealmRecipe } from '@/features/community3d/community3d';

const native=nativeParkLayouts.find(p=>p.id==='basketball_court_v1--native-v1')!;
const long=nativeParkLayouts.find(p=>p.id==='basketball_court_v1--long-v1')!;
const coords=rectangleAt([-114.05,51.04],52,39);
const zone=()=>({id:'park',updated_at:'one',zone_type:'green_space',coordinates:coords,properties:nativeParkProperties({},native,coords)} as SiteZone);
describe('native parks',()=>{
  it.each(['student_woodland_stream_garden_v1','student_reflecting_fountain_garden_v1','student_terraced_cafe_court_v1'])('%s preserves the exact native assembly through movement and reload',variant=>{
    const layout=nativeParkLayouts.find(p=>p.variantId===variant)!;
    expect(layout).toBeDefined();
    const coordinates=rectangleAt([-114.05,51.04],layout.occupiedWidthM!,layout.occupiedDepthM!);
    const p={...zone(),coordinates,properties:nativeParkProperties({},layout,coordinates)};
    expect(nativeParkFitProblem(p)).toBeNull();
    const moved=rectangleAt([-114.049,51.04],layout.occupiedWidthM!,layout.occupiedDepthM!,35);
    const saved=JSON.parse(JSON.stringify({...p,coordinates:moved,properties:nativeParkEditProperties(p,moved)}));
    expect(nativeParkFitProblem(saved)).toBeNull();
    expect(readNativePark(saved)?.layout.contentRevision).toBe(layout.contentRevision);
    expect(readNativePark(saved)?.layout.assets.assembly?.sha256).toBe(layout.assets.assembly?.sha256);
  });
  it('accepts the server v2 recipe and rejects stale or mixed capture contracts',()=>{
    const p=zone(),selection=readNativePark(p)!.selection;
    const recipe={schema_version:2,kind:'park',generator:'park_kit',family_id:'native_park',family_version:1,
      terrain_policy:'prepared_level',archetype_id:native.archetypeId,variant_id:native.variantId,
      ...selection,mode:native.mode,recipe_hash:'a'.repeat(64),asset_hashes:Object.fromEntries(Object.entries(native.assets).map(([key,asset])=>[key,asset!.sha256]))};
    expect(hasExecutablePublicRealmRecipe(p)).toBe(false);
    expect(hasExecutablePublicRealmRecipe({...p,properties:{...p.properties,public_realm_lego:recipe}})).toBe(true);
    expect(hasExecutablePublicRealmRecipe({...p,properties:{...p.properties,public_realm_lego:{...recipe,content_revision:'0'.repeat(64)}}})).toBe(false);
    expect(hasExecutablePublicRealmRecipe({...p,properties:{...p.properties,public_realm_lego:recipe,public_realm_fallback:{}}})).toBe(false);
  });
  it('retains the selected layout when its parcel grows',()=>{
    const p=zone(),larger=rectangleAt([-114.05,51.04],100,60);
    const properties=nativeParkEditProperties(p,larger);
    expect(readNativePark({properties})?.layout.id).toBe(native.id);
    expect(nativeParkFitProblem({...p,coordinates:larger,properties})).toBeNull();
  });
  it('moves and rotates the complete frame without changing model dimensions',()=>{
    const p=zone(),coordinates=rectangleAt([-114.049,51.04],52,39,35);
    const properties=nativeParkEditProperties(p,coordinates);
    expect(nativeParkFitProblem({...p,coordinates,properties})).toBeNull();
    expect(readNativePark({properties})?.layout.widthM).toBe(52);
  });
  it('previews enlargement atomically without mutating the old park',()=>{
    const p=zone(),before=JSON.stringify(p),proposal=parkLayoutProposal(p,long,[p]);
    expect(proposal.problem).toBeNull();
    expect(readNativePark({properties:proposal.properties})?.layout.id).toBe(long.id);
    expect(nativeParkFitProblem({...p,...proposal})).toBeNull();
    expect(JSON.stringify(p)).toBe(before);
  });
  it('rejects another plot in the proposed enlargement',()=>{
    const p=zone(),other={...p,id:'other',coordinates:rectangleAt([-114.0494,51.04],10,30)};
    expect(parkLayoutProposal(p,long,[p,other]).problem).toBeTruthy();
  });
  it('preserves an offset placement frame on layout change in a larger parcel',()=>{
    const p=zone();
    p.coordinates=rectangleAt([-114.0499,51.04],150,80);
    const before=readNativePark(p)!.selection.frame;
    const proposal=parkLayoutProposal(p,long,[p]);
    expect(proposal.problem).toBeNull();
    expect(readNativePark({properties:proposal.properties})!.selection.frame).toEqual(before);
  });
  it('never replaces a four-corner freeform parcel with a rectangle',()=>{
    const p=zone();
    p.coordinates=p.coordinates.map((point,i)=>i===2?[point[0]-.0001,point[1]]:point);
    const proposal=parkLayoutProposal(p,long,[p]);
    expect(proposal.coordinates).toEqual(p.coordinates);
    expect(proposal.problem).toBeTruthy();
  });
  it('rejects undersized and excluded areas without simplifying the model',()=>{
    const p=zone();
    expect(nativeParkFitProblem({...p,coordinates:rectangleAt([-114.05,51.04],30,30)})).toContain('complete');
    expect(nativeParkFitProblem({...p,properties:{...p.properties,park_exclusion_rings:[rectangleAt([-114.05,51.04],2,2)]}})).toContain('complete');
  });
  it('withholds native upgrades on custom terrain without changing the original park',()=>{
    const p=zone();p.properties={...p.properties,park_terrain:{version:1,mode:'terraced'}};
    const before=JSON.stringify(p);
    expect(parkLayoutProposal(p,long,[p]).problem).toContain('prepared level ground');
    expect(JSON.stringify(p)).toBe(before);
    expect(nativeParkFitProblem({...p,properties:{...zone().properties,park_exclusion_rings:[null]}})).toContain('exclusion areas are invalid');
    expect(nativeParkFitProblem({...p,properties:{...zone().properties,park_exclusion_rings:null}})).toContain('exclusion areas are invalid');
  });
  it('accepts an irregular parcel only while its actual notch clears the intact park',()=>{
    const p=zone(),east=111320*Math.cos(51.04*Math.PI/180);
    const outline=(inset:number)=>[[-60,-40],[60,-40],[60,40],[inset,40],[inset,10],[-60,10],[-60,-40]]
      .map(([x,y])=>[-114.05+x/east,51.04+y/111320]);
    // Use an L whose upper-left removal is beyond the complete native footprint.
    const good=outline(-30),bad=outline(0);
    expect(nativeParkFitProblem({...p,coordinates:good})).toBeNull();
    expect(nativeParkFitProblem({...p,coordinates:bad})).toContain('complete');
  });
  it('requires expected instances and the current saved revision for capture',()=>{
    const p=zone(),scene=new THREE.Scene();
    expect(()=>assertNativeParksReady(scene,[p])).toThrow('updating');
    const instance=new THREE.Group(),loaded=new THREE.Group();
    instance.userData={nativeParkZone:p.id,nativeParkRevision:JSON.stringify(p.properties?.green_space_native_layout)};
    loaded.userData.nativeParkStatus='ready';instance.add(loaded);scene.add(instance);
    expect(()=>assertNativeParksReady(scene,[p])).not.toThrow();
    const edited={...p,properties:nativeParkProperties(p.properties!,long,rectangleAt([-114.05,51.04],92,39))};
    expect(()=>assertNativeParksReady(scene,[edited])).toThrow('updating');
  });
  it('rejects an unavailable expected model without a successful partial capture',async()=>{
    const p=zone(),scene=new THREE.Scene(),instance=new THREE.Group(),failed=new THREE.Group();
    instance.userData={nativeParkZone:p.id,nativeParkRevision:JSON.stringify(p.properties?.green_space_native_layout)};
    failed.userData={nativeParkStatus:'error',nativeParkError:'Model verification failed. Retry 3D update.'};
    instance.add(failed);scene.add(instance);
    await expect(waitForNativeParksReady(scene,[p])).rejects.toThrow('verification failed');
    expect(()=>assertNativeParksReady(scene,[])).not.toThrow();
    await expect(waitForNativeParksReady(new THREE.Scene(),[p],0)).rejects.toThrow('updating');
  });
});
