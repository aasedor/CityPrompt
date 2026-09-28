import { describe, expect, it } from 'vitest';
import expansion from '@/data/classroomExpansion.json';
import { CATALOGUE_ASSETS } from './assetRegistry';
import { CANONICAL_CHOICES, filterCanonicalChoices } from './canonicalCatalogue';

describe('classroom building additions', () => {
  it('offers twenty-three distinct exact models with eleven additional native placements', () => {
    const buildings = CATALOGUE_ASSETS.filter(a => a.kind === 'object' && a.zoneType === 'building');
    expect(buildings).toHaveLength(23);
    expect(new Set(buildings.map(a => a.model.variantId)).size).toBe(23);
    const additions = expansion.entries.filter(e => e.domain === 'building');
    expect(additions).toHaveLength(11);
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
});
