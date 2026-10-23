import { describe, expect, it, vi } from 'vitest';
import manifest from '@/data/publicRealmRelease20261023.json';
import type { PlaceAsset } from './assetRegistry';
import { nativePlacementPreviewUrl } from './nativePlacementPreview';
const gate=vi.hoisted(()=>({allowed:true}));
vi.mock('./publicRealmRelease', async () => {
 const actual=await vi.importActual<typeof import('./publicRealmRelease')>('./publicRealmRelease');
 return {...actual,publicRealmReleaseAllowed:()=>gate.allowed};
});
describe('exact fixed native placement preview',()=>{
 it('previews every park and street release with its exact fixture, retaining legacy fixtures',()=>{
  gate.allowed=true;
  for(const row of manifest.models) expect(nativePlacementPreviewUrl(row.asset as unknown as PlaceAsset)).toBe(row.fixture.url);
  expect(nativePlacementPreviewUrl({id:'legacy',properties:{validation_native_url:'/old.glb'},model:{method:'legacy'}} as unknown as PlaceAsset)).toBe('/old.glb');
 });
 it('rejects stale or redirected release identity and unapproved production rows',()=>{
  for(const mutate of [(a:PlaceAsset)=>{a.model.revision='0'.repeat(64);},(a:PlaceAsset)=>{a.properties.native_public_realm_url='/other.glb';},(a:PlaceAsset)=>{a.width+=1;}]) {
   const asset=structuredClone(manifest.models[0].asset) as unknown as PlaceAsset;mutate(asset);
   expect(nativePlacementPreviewUrl(asset)).toBeNull();
  }
  gate.allowed=false;
  expect(nativePlacementPreviewUrl(manifest.models[0].asset as unknown as PlaceAsset)).toBeNull();
 });
});
