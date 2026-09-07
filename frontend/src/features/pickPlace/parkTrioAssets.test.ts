import {describe,expect,it} from 'vitest';
import {PARK_TRIO_ASSETS} from './parkTrioAssets';
import {CALGARY_GROUPS} from '../calgaryCatalogue/guide';
import {parkTrioKind} from '@/components/viewer/globe/parkTrioLayout';

describe('local park trio catalogue cards',()=>{
  it('places every pilot in a visible park group with a working exact renderer identity',()=>{
    expect(PARK_TRIO_ASSETS).toHaveLength(3);
    for(const asset of PARK_TRIO_ASSETS){
      expect(CALGARY_GROUPS.find(g=>g.id===asset.calgaryGuide?.groupId)?.domain).toBe('park_plaza');
      expect(parkTrioKind({zone_type:asset.zoneType,properties:asset.properties})).not.toBeNull();
      expect(asset.readiness).toBe('pilot');
      expect(asset.width).toBeGreaterThanOrEqual(asset.minWidth!);
      expect(asset.depth).toBeGreaterThanOrEqual(asset.minDepth!);
    }
  });
});
