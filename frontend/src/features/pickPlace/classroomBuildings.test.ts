import { describe, expect, it } from 'vitest';
import expansion from '@/data/classroomExpansion.json';
import { CATALOGUE_ASSETS, type PlaceAsset } from './assetRegistry';
import { CANONICAL_CHOICES, filterCanonicalChoices } from './canonicalCatalogue';

describe('classroom building additions', () => {
  it('preserves classroom additions within the growing exact-model catalogue', () => {
    const buildings = CATALOGUE_ASSETS.filter((a): a is PlaceAsset => a.kind === 'object' && a.zoneType === 'building');
    expect(buildings.length).toBeGreaterThanOrEqual(26);
    expect(new Set(buildings.map(a => a.model.variantId)).size).toBe(buildings.length);
    const additions = expansion.entries.filter(e => e.domain === 'building' && e.runtime_status === 'NOT TESTED');
    expect(additions).toHaveLength(14);
    for (const entry of additions) {
      const asset = buildings.find(a => a.id === entry.placement_id)!;
      expect(asset.model.variantId).toBe(entry.variant_id);
      expect(asset.model.revision).toBe(entry.version);
      expect(asset.reshapeMode).toBe('fixed_native');
      expect(asset.properties.native_home_plot).toBe(false);
      expect(asset.readiness).toBe('pilot');
      expect(entry.completed).toBe(false);
      expect(entry.runtime_status).toBe('NOT TESTED');
      expect(filterCanonicalChoices('building', entry.title).some(c => c.placements.includes(asset))).toBe(true);
    }
  });

  it('keeps sibling designs independently discoverable with stable unique card keys', () => {
    const siblings = CANONICAL_CHOICES.filter(c => c.option.id === 'calgary_modern_infill_house');
    expect(siblings).toHaveLength(2);
    expect(new Set(siblings.map(c => c.id)).size).toBe(2);
    expect(siblings.map(c => c.placements[0].model.variantId).sort()).toEqual(['infill_duplex', 'infill_flat_roof_minimal']);
  });

  it('publishes an explicit storey capability for every building', () => {
    const buildings = CATALOGUE_ASSETS.filter((a): a is PlaceAsset => a.kind === 'object' && a.zoneType === 'building');
    for (const asset of buildings) {
      expect(asset.storeyProgram).toBeDefined();
      expect(asset.storeyProgram!.minStoreys).toBeLessThanOrEqual(asset.storeyProgram!.nativeStoreys);
      expect(asset.storeyProgram!.maxStoreys).toBeGreaterThanOrEqual(asset.storeyProgram!.nativeStoreys);
      if (!['trial_postwar_bungalow', 'trial_edwardian_foursquare',
        'validation_clapboard_north_end', 'clay_vancouver_balcony_podium_tower'].includes(asset.id)) {
        expect(asset.storeyProgram!.mode).toBe('fixed_authored_assembly');
        expect(asset.storeyProgram!.minStoreys).toBe(asset.storeyProgram!.maxStoreys);
      }
    }
  });
});
