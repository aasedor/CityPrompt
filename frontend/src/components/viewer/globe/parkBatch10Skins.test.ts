import { describe, expect, it } from 'vitest';
import openSpaceCatalog from '@/data/openSpaceArchetypes.json';
import { BATCH10_PARK_SKINS, batch10ParkSkinForSelection } from './parkBatch10Skins';

describe('Batch 10 park skins', () => {
  it('locks ten exact city-specific selections without people or large buildings', () => {
    expect(BATCH10_PARK_SKINS).toHaveLength(10);
    expect(new Set(BATCH10_PARK_SKINS.map(({ archetypeId }) => archetypeId)).size).toBe(10);
    for (const skin of BATCH10_PARK_SKINS) {
      expect(skin.roles).toEqual(['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber']);
      expect(skin.people).toBe(false);
      expect(skin.largeBuildings).toBe(false);
      expect(batch10ParkSkinForSelection(skin.archetypeId, skin.variantId)).toBe(skin);
    }
  });

  it('does not claim adjacent variants that have not been reviewed as exact families', () => {
    expect(batch10ParkSkinForSelection('amsterdam_hofje_garden', 'amsterdam_hofje_garden_v1')).toBeNull();
    expect(batch10ParkSkinForSelection('barcelona_superilla', 'barcelona_superilla_v0')).toBeNull();
    expect(batch10ParkSkinForSelection('montreal_square', 'montreal_square_v2')).toBeNull();
  });

  it('keeps every selected parent reachable through a canonical Park picker category', () => {
    const expected = new Map([
      ['amsterdam_hofje_garden', 'specialty_gardens'],
      ['amsterdam_plein', 'civic_plazas'],
      ['amsterdam_vondelpark', 'landscape_parks'],
      ['barcelona_pati_interior', 'specialty_gardens'],
      ['barcelona_placa_xamfra', 'civic_plazas'],
      ['barcelona_superilla', 'neighborhood_public_realm'],
      ['calgary_prairie_plaza', 'civic_plazas'],
      ['calgary_princes_island', 'waterfront_spaces'],
      ['montreal_mount_royal', 'landscape_parks'],
      ['montreal_square', 'civic_plazas'],
    ]);
    const actual = new Map(openSpaceCatalog.archetypes
      .filter(({ id }) => expected.has(id))
      .map(({ id, aestheticCategory }) => [id, aestheticCategory]));
    expect(actual).toEqual(expected);
  });
});
