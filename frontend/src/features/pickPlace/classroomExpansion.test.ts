import { describe, expect, it } from 'vitest';
import { CANONICAL_CHOICES, filterCanonicalChoices } from './canonicalCatalogue';
import { CATALOGUE_ASSETS, validateRegistry } from './assetRegistry';
import { nativeParkLayouts } from '@/features/parks/nativeParkRegistry';
import expansion from '@/data/classroomExpansion.json';

describe('classroom park additions', () => {
  const parks = expansion.entries.filter(e => e.domain === 'park');
  it('adds twenty-six distinct park types without counting alternate layouts twice', () => {
    expect(parks).toHaveLength(26);
    expect(new Set(parks.map(e => e.archetype_id)).size).toBe(26);
    expect(parks.every(e => e.completed === false && ['NOT TESTED', 'PASS_LOCAL_PREPARED_SITE'].includes(e.runtime_status))).toBe(true);
  });
  it('keeps the five neighbourhood programmes native and uses their original source photographs', () => {
    const variants = [
      ['student_prairie_picnic_grove_v1', 'prairie-picnic-grove', 40, 52],
      ['student_sensory_wellness_garden_v1', 'sensory-wellness-garden', 36, 46],
      ['student_urban_skate_plaza_v1', 'urban-skate-plaza', 42, 54],
      ['student_bicycle_pump_track_park_v1', 'bicycle-pump-track-park', 48, 60],
      ['student_neighbourhood_sports_green_v1', 'neighbourhood-sports-green', 48, 66],
    ] as const;
    for (const [variant, slug, width, depth] of variants) {
      const layout = nativeParkLayouts.find(p => p.variantId === variant)!;
      const asset = expansion.assets.find(p => p.model.variantId === variant)!;
      expect(layout).toBeDefined();
      expect([layout.widthM, layout.depthM]).toEqual([width, depth]);
      expect(layout.mode).toBe('native_assembly');
      expect(layout.groundOwner).toBe('assembly');
      expect(asset.thumbnail).toBe(`/archetypes/openspaces/${slug}/variant_0.png`);
      expect(asset.reshapeMode).toBe('authored_footprint');
    }
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
