import { describe, expect, it } from 'vitest';
import { CANONICAL_CHOICES, filterCanonicalChoices } from './canonicalCatalogue';
import { CATALOGUE_ASSETS, validateRegistry } from './assetRegistry';
import { nativeParkLayouts } from '@/features/parks/nativeParkRegistry';
import expansion from '@/data/classroomExpansion.json';

describe('classroom park additions', () => {
  const parks = expansion.entries.filter(e => e.domain === 'park');
  it('adds thirteen distinct park types without counting alternate layouts twice', () => {
    expect(parks).toHaveLength(13);
    expect(new Set(parks.map(e => e.archetype_id)).size).toBe(13);
    expect(parks.every(e => e.completed === false && e.runtime_status === 'NOT TESTED')).toBe(true);
  });
  it('offers each added park through ordinary search with its exact native layout', () => {
    for (const entry of parks) {
      const choice = filterCanonicalChoices('park_plaza', entry.title).find(c => c.option.id === entry.archetype_id);
      expect(choice).toBeDefined();
      expect(choice!.placements).toHaveLength(1);
      const asset = choice!.placements[0];
      const layout = nativeParkLayouts.find(p => p.variantId === entry.variant_id)!;
      expect(asset.model.variantId).toBe(entry.variant_id);
      expect(asset.model.revision).toBe(layout.contentRevision);
      expect(asset.properties.green_space_native_layout_id).toBe(layout.id);
      expect(asset.kind).toBe('object');
      if (asset.kind === 'object') {
        expect(asset.width).toBeGreaterThanOrEqual(layout.occupiedWidthM);
        expect(asset.depth).toBeGreaterThanOrEqual(layout.occupiedDepthM);
      }
    }
  });

  it('retains valid unique placement and discovery identities', () => {
    expect(validateRegistry(CATALOGUE_ASSETS)).toEqual([]);
    expect(new Set(CANONICAL_CHOICES.map(c => c.id)).size).toBe(CANONICAL_CHOICES.length);
    expect(CANONICAL_CHOICES.every(c => c.placements.every(Boolean))).toBe(true);
  });
});
