import {describe,expect,it} from 'vitest';
import {PARK_TRIO_ASSETS} from './parkTrioAssets';
import {CALGARY_GROUPS} from '../calgaryCatalogue/guide';
import {parkTrioKind, buildParkTrio, rect} from '@/components/viewer/globe/parkTrioLayout';
import {CATALOGUE_ASSETS, browseAssets} from './assetRegistry';

describe('local park trio catalogue cards',()=>{
  it('includes all three parks in the normal catalogue without a trial flag',()=>{
    for(const asset of PARK_TRIO_ASSETS){
      expect(CATALOGUE_ASSETS).toContain(asset);
      expect(browseAssets(asset.label)).toContain(asset);
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
