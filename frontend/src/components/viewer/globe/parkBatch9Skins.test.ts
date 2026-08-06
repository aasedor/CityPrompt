import { describe, expect, it } from 'vitest';
import openSpaceCatalog from '@/data/openSpaceArchetypes.json';
import { BATCH9_PARK_SKINS, batch9ParkSkinForSelection } from './parkBatch9Skins';

describe('Batch 9 park skins', () => {
  it('locks ten exact reviewed selections without people or large buildings', () => {
    expect(BATCH9_PARK_SKINS).toHaveLength(10);
    expect(new Set(BATCH9_PARK_SKINS.map(({ archetypeId }) => archetypeId)).size).toBe(10);
    expect(new Set(BATCH9_PARK_SKINS.map(({ slug }) => slug)).size).toBe(10);
    for (const skin of BATCH9_PARK_SKINS) {
      expect(skin.roles).toEqual(['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber']);
      expect(skin.people).toBe(false);
      expect(skin.largeBuildings).toBe(false);
      expect(batch9ParkSkinForSelection(skin.archetypeId, skin.variantId)).toBe(skin);
    }
  });

  it('fails closed for adjacent unreviewed variants', () => {
    expect(batch9ParkSkinForSelection('urban_pocket_park', 'urban_pocket_park_v1')).toBeNull();
    expect(batch9ParkSkinForSelection('parisian_jardin', 'parisian_jardin_v0')).toBeNull();
    expect(batch9ParkSkinForSelection('hilltop_topographic_park', 'hilltop_topographic_park_v2')).toBeNull();
  });

  it('keeps the three heritage-garden targets visible in the Specialty Gardens picker', () => {
    const targetIds = ['parisian_jardin', 'london_garden_square', 'halifax_public_gardens'];
    const targets = openSpaceCatalog.archetypes.filter(({ id }) => targetIds.includes(id));

    expect(targets).toHaveLength(3);
    expect(targets.map(({ aestheticCategory }) => aestheticCategory)).toEqual([
      'specialty_gardens',
      'specialty_gardens',
      'specialty_gardens',
    ]);
  });
});
