import { describe, expect, it } from 'vitest';
import { CATALOGUE_ASSETS, validateRegistry } from './assetRegistry';
import { CANONICAL_CHOICES, CLASSROOM_CHOICES } from './canonicalCatalogue';
import roster from '@/data/validationCatalogue.json';
import expansion from '@/data/classroomExpansion.json';
import { rectangleAt, resizeRectangleCorner } from './geometry';
import { publicRealmTrialAsset, publicRealmTrialGroundCells } from '@/components/viewer/globe/publicRealmTrial';
import { trimNativeStreetModel } from '@/components/viewer/globe/nativeStreetModelTrim';
import type { SiteZone } from '@/types';
import * as THREE from 'three';
import { LOCAL_CLAUDE_SAVED_ASSETS } from './claudeAssetLocalTrial';
import { PUBLIC_REALM_RELEASE_ASSETS, publicRealmReleaseRow, releaseGateErrors } from './publicRealmRelease';

describe('exact local validation catalogue', () => {
  it('resolves every locked validation variant to one placeable catalogue choice', () => {
    expect(validateRegistry(CATALOGUE_ASSETS)).toEqual([]);
    expect(CLASSROOM_CHOICES).toEqual(CANONICAL_CHOICES);
    for (const c of CANONICAL_CHOICES) {
      expect(c.placements.length).toBeGreaterThan(0);
      expect(c.option.variants?.map(v=>v.id).sort()).toEqual(c.placements.map(a=>a.model.variantId).sort());
      if (!c.groupedVariants) expect(c.placements).toHaveLength(1);
    }
    const entries = [...roster.entries, ...expansion.entries];
    for (const entry of entries) {
      expect(CANONICAL_CHOICES.filter(c => c.placements.some(a => (c.option.id === entry.archetype_id
        || a.properties.green_space_archetype_id === entry.archetype_id)
        && a.model.variantId === entry.variant_id && a.model.method !== 'public_realm_park_kit')), entry.placement_id).toHaveLength(1);
    }
    const fourplex = CATALOGUE_ASSETS.find(a => a.id === 'validation_reference_charcoal_gable_fourplex_v1');
    expect(fourplex?.model.revision).toBe(roster.entries.find(e => e.placement_id === fourplex?.id)?.sha256);
  });
  it('never stretches or substitutes a fixed review fixture', () => {
    const fixed=CATALOGUE_ASSETS.filter(a=>a.kind==='object' && a.properties.validation_fixed_fixture);
    expect(fixed.map(a=>a.model.variantId)).toContain('reference_charcoal_gable_fourplex_v1');
    for(const a of fixed) {
      if(a.kind!=='object')continue;
      const coords=rectangleAt([-114.1,51.0],a.width,a.depth);
      expect(resizeRectangleCorner(coords,0,[-114.2,51.2],a)).toEqual(coords);
      if (a.properties.validation_native_url && a.nativeDimensions) {
        expect(a.width).toBeGreaterThan(a.nativeDimensions[0]);
        expect(a.depth).toBeGreaterThan(a.nativeDimensions[1]);
      }
      if (a.zoneType === 'building') continue;
      const fixture=publicRealmTrialAsset({properties:a.properties} as SiteZone)!;
      expect(fixture.sha256).toBe(a.model.revision);
      expect(publicRealmTrialGroundCells(fixture)).toEqual([]);
      const scene=new THREE.Group();
      const mesh=new THREE.Mesh(new THREE.BoxGeometry(1,1,1),new THREE.MeshStandardMaterial({name:'grass'}));
      scene.add(mesh);
      const result=trimNativeStreetModel(scene,{asset:fixture,lng:0,lat:0,yaw:0,height:0},[]);
      expect(result.clone.children).toHaveLength(1);
    }
  });
  it('offers parks through native contracts without legacy fixture flags', () => {
    // Saved local pilots and published fixed scenes retain distinct contracts.
    const localIds = new Set(LOCAL_CLAUDE_SAVED_ASSETS.map(asset => asset.id));
    const parks=CATALOGUE_ASSETS.filter(a=>a.kind==='object' && a.zoneType==='green_space' && !localIds.has(a.id));
    expect(parks.length).toBeGreaterThanOrEqual(15);
    for(const park of parks) {
      expect(['native_park_v2','native_validation_fixture','public_realm_park_kit','fixed_public_realm_v1']).toContain(park.model.method);
      if (park.model.method === 'fixed_public_realm_v1') {
        expect(PUBLIC_REALM_RELEASE_ASSETS.filter(asset => asset.id === park.id)).toHaveLength(1);
        expect(releaseGateErrors(publicRealmReleaseRow(park.id)!)).toEqual([]);
        expect(park.reshapeMode).toBe('fixed_native');
        expect(park.properties.native_public_realm_url).toBe(publicRealmReleaseRow(park.id)!.fixture.url);
        expect(park.properties.pick_place_flexible_park).toBeUndefined();
        expect(park.properties.green_space_native_layout_id).toBeUndefined();
      }
      if (park.model.method === 'native_park_v2') {
        expect(park.reshapeMode).toBe(park.properties.court_only_native ? 'fixed_native' : 'authored_footprint');
        expect(park.properties.green_space_native_layout_id).toBeTruthy();
      }
      if (park.model.method === 'public_realm_park_kit') {
        expect(park.reshapeMode).toBe('authored_footprint');
        expect(park.properties.pick_place_flexible_park).toBeTruthy();
      }
      expect(park.properties.validation_fixed_fixture).toBeUndefined();
      expect(park.properties.public_realm_trial_asset).toBeUndefined();
      expect(park.properties.park_trio_layout).toBeUndefined();
    }
  });
  it('preserves the remaining adaptive public-realm candidates to their native runtimes',()=>{
    const variants = new Set(CATALOGUE_ASSETS.filter(a=>a.kind==='street').map(a=>a.model.variantId));
    for (const variant of ['amsterdam_gracht_v1','brt_bus_rapid_transit_corridor_v0','landmark_signature_bridge_v2',
      'student_main_street_v1','student_market_street_v1','student_planted_shared_lane_v1']) {
      expect(variants.has(variant)).toBe(true);
    }
    expect(CATALOGUE_ASSETS.filter(a=>a.reshapeMode==='adaptive_layout')).toEqual([]);
  });
});
