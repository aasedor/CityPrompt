import { describe, expect, it } from 'vitest';
import { SHARED_PARK_EQUIPMENT } from './sharedParkEquipment';

describe('shared park equipment catalog', () => {
  it('keeps every reviewed asset metric, bounded, and directly servable', () => {
    const assets = Object.values(SHARED_PARK_EQUIPMENT);
    expect(assets).toHaveLength(5);
    expect(assets.every((asset) => asset.url.startsWith('/park-kits/shared-park-equipment-v1/')))
      .toBe(true);
    expect(assets.every((asset) => asset.targetHeightM > 0 && asset.maxTriangles <= 3500))
      .toBe(true);
    expect(assets.every((asset) => asset.footprintM.width > 0 && asset.footprintM.depth > 0))
      .toBe(true);
  });

  it('retains the regulation basketball datum and post-base anchor', () => {
    const hoop = SHARED_PARK_EQUIPMENT.basketball_hoop_regulation;
    expect(hoop.targetHeightM).toBe(3.95);
    expect(hoop.placementAnchor).toBe('post_base');
    expect(hoop.clearanceM).toBe(2);
  });
});
