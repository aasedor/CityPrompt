import { describe, expect, it } from 'vitest';
import { CATALOGUE_ASSETS, validateRegistry } from './assetRegistry';
import { CANONICAL_CHOICES, CLASSROOM_CHOICES } from './canonicalCatalogue';
import roster from '@/data/validationCatalogue.json';
import { rectangleAt, resizeRectangleCorner } from './geometry';
import { publicRealmTrialAsset, publicRealmTrialGroundCells } from '@/components/viewer/globe/publicRealmTrial';
import { trimNativeStreetModel } from '@/components/viewer/globe/nativeStreetModelTrim';
import type { SiteZone } from '@/types';
import * as THREE from 'three';

describe('exact local validation catalogue', () => {
  it('offers exactly 27 locked variants in both discovery collections', () => {
    expect(CATALOGUE_ASSETS).toHaveLength(27);
    expect(validateRegistry(CATALOGUE_ASSETS)).toEqual([]);
    expect(CANONICAL_CHOICES).toHaveLength(27);
    expect(CLASSROOM_CHOICES).toEqual(CANONICAL_CHOICES);
    for (const [domain, count] of [['building',12],['park_plaza',8],['street_pathway',7]] as const) {
      expect(CANONICAL_CHOICES.filter(c=>c.domain===domain)).toHaveLength(count);
    }
    for (const c of CANONICAL_CHOICES) {
      expect(c.placements).toHaveLength(1);
      expect(c.option.variants?.map(v=>v.id)).toEqual([c.placements[0].model.variantId]);
    }
    expect(new Set(roster.entries.map(e=>e.sha256)).size).toBe(27);
    expect(roster.entries.every(e=>e.runtime_status==='NOT TESTED')).toBe(true);
  });
  it('never stretches or substitutes a fixed review fixture', () => {
    const fixed=CATALOGUE_ASSETS.filter(a=>a.kind==='object' && a.properties.validation_fixed_fixture);
    expect(fixed).toHaveLength(11);
    for(const a of fixed) {
      if(a.kind!=='object')continue;
      const coords=rectangleAt([-114.1,51.0],a.width,a.depth);
      expect(resizeRectangleCorner(coords,0,[-114.2,51.2],a)).toEqual(coords);
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
  it('binds the four adaptive public-realm candidates to their native runtimes',()=>{
    expect(CATALOGUE_ASSETS.filter(a=>a.kind==='street').map(a=>a.model.variantId).sort()).toEqual(['student_main_street_v1','student_market_street_v1']);
    expect(CATALOGUE_ASSETS.filter(a=>a.reshapeMode==='adaptive_layout').map(a=>a.model.variantId).sort()).toEqual(['basketball_court_v1','research_garden_teaching_arboretum_variant_3']);
  });
});
