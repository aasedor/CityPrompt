import {describe,expect,it} from 'vitest';
import {PARK_TRIO_ASSETS} from './parkTrioAssets';
import {CALGARY_GROUPS} from '../calgaryCatalogue/guide';
import {parkTrioKind, buildParkTrio, rect} from '@/components/viewer/globe/parkTrioLayout';
import {CATALOGUE_ASSETS, browseAssets} from './assetRegistry';

describe('local park trio catalogue cards',()=>{
  it('keeps historical trio renderers out of discovery while offering the reviewed native replacements',()=>{
    for(const asset of PARK_TRIO_ASSETS){
      expect(CATALOGUE_ASSETS.some(candidate => candidate.id === asset.id)).toBe(false);
      expect(browseAssets(asset.label).some(candidate => candidate.id === asset.id)).toBe(false);

    }
    for (const variant of ['basketball_court_v1', 'research_garden_teaching_arboretum_variant_3']) {
      const current = CATALOGUE_ASSETS.find(candidate => candidate.model.variantId === variant);
      expect(current?.model.method).toBe('native_park_v2');
      expect(current?.properties.green_space_native_layout_id).toBeTruthy();
    }
  });
  it('places every pilot in a visible park group with a working exact renderer identity',()=>{
    expect(PARK_TRIO_ASSETS).toHaveLength(6);
    for(const asset of PARK_TRIO_ASSETS){
      expect(CALGARY_GROUPS.find(g=>g.id===asset.calgaryGuide?.groupId)?.domain).toBe('park_plaza');
      expect(parkTrioKind({zone_type:asset.zoneType,properties:asset.properties})).not.toBeNull();
      expect(asset.readiness).toBe('pilot');
      expect(asset.width).toBeGreaterThanOrEqual(asset.minWidth!);
      expect(asset.depth).toBeGreaterThanOrEqual(asset.minDepth!);
    }
  });
  it('starts every park with a full programme and preserves compact resizing',()=>{
    for(const asset of PARK_TRIO_ASSETS){
      const kind=parkTrioKind({zone_type:asset.zoneType,properties:asset.properties})!;
      expect(buildParkTrio(kind,rect(0,0,asset.width,asset.depth)).status).toBe('full');
      expect(buildParkTrio(kind,rect(0,0,asset.minWidth,asset.minDepth)).status).not.toBe('constrained');
    }
    const garden=PARK_TRIO_ASSETS.find(asset=>asset.id==='park_trio_garden')!;
    const layout=buildParkTrio('garden',rect(0,0,garden.width,garden.depth));
    expect(layout.modules.filter(m=>m.asset==='garden/bed')).toHaveLength(12);
    expect(layout.modules.filter(m=>m.asset==='garden/shelter')).toHaveLength(1);
  });
});
