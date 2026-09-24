import { describe, expect, it, vi } from 'vitest';
import recipes from './__fixtures__/classroomStreetRecipes.json';
import { nativeStreetPilotForZone } from './nativeStreetPilot';
import { validateStreetRecipeProperties } from './streetLegoContract';
import { resolvePilotStreetSectionProfile } from './streetSectionProfiles';
import { CLASSROOM_CHOICES } from '@/features/pickPlace/canonicalCatalogue';

describe('saved classroom native streets in a production build', () => {
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
