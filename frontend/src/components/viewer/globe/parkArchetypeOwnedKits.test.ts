import { describe, expect, it } from 'vitest';

import {
  ARCHETYPE_OWNED_PARK_KITS,
  archetypeOwnedParkKitForSelection,
} from './parkArchetypeOwnedKits';

describe('archetype-owned park kit registry', () => {
  it('contains fifteen exact, non-generic pilot identities across three batches', () => {
    const kits = Object.values(ARCHETYPE_OWNED_PARK_KITS);
    expect(kits).toHaveLength(15);
    expect(new Set(kits.map(({ familyId }) => familyId)).size).toBe(15);
    expect(new Set(kits.map(({ appearanceKitId }) => appearanceKitId)).size).toBe(15);
    expect(kits.every(({ people, largeBuildings }) => !people && !largeBuildings)).toBe(true);
  });

  it.each([
    ['skate_park', 'skate_park_v0', 40, 30],
    ['inclusive_playground', 'inclusive_playground_v0', 50, 40],
    ['dog_park', 'dog_park_v0', 80, 50],
    ['splash_pad_area', 'splash_pad_area_v0', 30, 25],
    ['community_garden', 'community_garden_v0', 50, 50],
    ['tennis_court_cluster', 'tennis_court_cluster_v0', 82, 46],
    ['nature_play_area', 'nature_play_area_v0', 40, 30],
    ['pump_track', 'pump_track_v0', 50, 30],
    ['outdoor_fitness_circuit', 'outdoor_fitness_circuit_v0', 30, 25],
    ['memorial_garden', 'memorial_garden_v0', 50, 40],
    ['pickleball_courts', 'pickleball_courts_v1', 78, 66],
    ['running_track_oval', 'running_track_oval_v2', 220, 135],
    ['baseball_softball_diamond', 'baseball_softball_diamond_v1', 230, 210],
    ['cricket_pitch_oval', 'cricket_pitch_oval_v0', 190, 170],
    ['sports_field_complex', 'sports_field_complex_v0', 330, 245],
  ])('locks %s/%s to its authored metric envelope', (archetypeId, variantId, widthM, depthM) => {
    expect(archetypeOwnedParkKitForSelection(archetypeId, variantId)).toMatchObject({
      archetypeId,
      variantId,
      widthM,
      depthM,
      clearanceM: 0.5,
    });
  });
});
