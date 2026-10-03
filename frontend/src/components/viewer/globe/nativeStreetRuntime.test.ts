import { describe, expect, it, vi } from 'vitest';
import recipes from './__fixtures__/classroomStreetRecipes.json';
import { nativeStreetPilotForZone } from './nativeStreetPilot';
import { validateStreetRecipeProperties } from './streetLegoContract';
import { resolvePilotStreetSectionProfile } from './streetSectionProfiles';
import { CLASSROOM_CHOICES } from '@/features/pickPlace/canonicalCatalogue';
import pilots from '@/data/nativeStreetPilots.json';
import { PUBLIC_REALM_STREET_FAMILIES, PUBLIC_REALM_STREET_SELECTIONS } from './streetFamilyCatalog';

describe('saved classroom native streets in a production build', () => {
  it('registers an executable family and exact selection for every packaged native street', () => {
    expect(pilots).toHaveLength(19);
    for (const pilot of pilots) {
      const familyId = `street_native_${pilot.id}`;
      const family = PUBLIC_REALM_STREET_FAMILIES[familyId as keyof typeof PUBLIC_REALM_STREET_FAMILIES];
      const selection = PUBLIC_REALM_STREET_SELECTIONS.find(candidate => candidate.variantId === pilot.id);
      expect(family?.sourceArchetypeIds).toContain(pilot.sourceArchetypeId);
      expect(family?.nativeRowM).toBe(pilot.widthM);
      expect(selection?.familyId).toBe(familyId);
      expect(selection?.archetypeId).toBe(pilot.sourceArchetypeId);
    }
  });
  it.each(recipes)('loads $variant_id with server-compiled ownership and exact module locks', recipe => {
    vi.stubEnv('DEV', false);
    try {
      const asset = CLASSROOM_CHOICES.flatMap(c => c.placements).find(a => a.model.variantId === recipe.variant_id)!;
      const zone = { zone_type: 'road' as const, properties: { ...asset.properties, public_realm_lego: recipe } };
      const reopened = JSON.parse(JSON.stringify(zone));
      expect(validateStreetRecipeProperties(reopened.properties)).toMatchObject({ valid: true });
      expect(nativeStreetPilotForZone(reopened)?.id).toBe(recipe.variant_id);
      const profile = resolvePilotStreetSectionProfile(reopened);
      expect(profile?.recipeHash).toBe(recipe.recipe_hash);
      expect(profile?.familyId).toBe(recipe.family_id);
      expect(profile?.rowM).toBe(recipe.target.row_width_m);
      expect(profile?.bands.reduce((total, band) => total + band.widthM, 0)).toBe(recipe.target.row_width_m);
      const corrupted = { ...reopened, properties: { ...reopened.properties, public_realm_lego: {
        ...recipe, component_set_ids: recipe.component_set_ids.slice(1),
      } } };
      expect(nativeStreetPilotForZone(corrupted)).toBeUndefined();
      expect(validateStreetRecipeProperties(corrupted.properties)).toMatchObject({ valid: false, code: 'integrity_incompatible' });
      expect(nativeStreetPilotForZone({ ...zone, properties: { ...zone.properties, width: 30 } })).toBeUndefined();
      expect(nativeStreetPilotForZone({ ...zone, properties: { ...asset.properties, native_street_pilot_id: recipe.variant_id } })).toBeUndefined();
    } finally { vi.unstubAllEnvs(); }
  });
});
