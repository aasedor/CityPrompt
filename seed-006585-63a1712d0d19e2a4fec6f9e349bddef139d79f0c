import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import openSpaceCatalog from './openSpaceArchetypes.json';
import { isDefaultParkRecipe, resolveParkRecipe } from './parkKitRecipes';
import { RENDERLOCK_V1_PARKS } from './renderlockV1Parks';
import {
  resolveParkGroundProfile,
  resolveParkSpecialtyStructureKind,
  shouldMountParkProgramFrame,
} from '../components/viewer/globe/parkGroundProfiles';

function zone(archetypeId: string, variantId: string): SiteZone {
  return {
    id: `zone-${archetypeId}`,
    project_id: 'renderlock-parks-v1',
    zone_type: 'green_space',
    name: archetypeId,
    coordinates: [[-113.58, 53.37], [-113.57, 53.37], [-113.57, 53.38], [-113.58, 53.38]],
    color: '#65a30d',
    properties: {
      green_space_archetype_id: archetypeId,
      green_space_selected_variant_id: variantId,
    },
    sort_order: 0,
    created_at: '2026-07-20T00:00:00Z',
    updated_at: '2026-07-20T00:00:00Z',
  };
}

describe('render-lock v1 park cohort', () => {
  it('is finite, ordered and unique', () => {
    expect(RENDERLOCK_V1_PARKS).toHaveLength(10);
    expect(RENDERLOCK_V1_PARKS.map((entry) => entry.sequence)).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
    expect(new Set(RENDERLOCK_V1_PARKS.map((entry) => entry.archetypeId)).size).toBe(10);
    expect(new Set(RENDERLOCK_V1_PARKS.map((entry) => entry.variantId)).size).toBe(10);
    expect(RENDERLOCK_V1_PARKS.every((entry) => entry.reviewState === 'keeper')).toBe(true);
  });

  it('locks three catalog camera references for each selected variant', () => {
    for (const entry of RENDERLOCK_V1_PARKS) {
      expect(entry.referenceViews.street).toMatch(/\/variant_\d\.png$/);
      expect(entry.referenceViews.angle_60).toMatch(/\/variant_\d_angle_60\.jpg$/);
      expect(entry.referenceViews.angle_90).toMatch(/\/variant_\d_angle_90\.jpg$/);
      const roots = Object.values(entry.referenceViews).map((path) => path.replace(/(?:_angle_(?:60|90))?\.(?:png|jpg)$/, ''));
      expect(new Set(roots).size).toBe(1);
    }
  });

  it('references real variants and exact non-default LEGO recipes', () => {
    const catalog = (openSpaceCatalog as { archetypes: Array<{ id: string; variants: Array<{ id: string }> }> }).archetypes;
    for (const entry of RENDERLOCK_V1_PARKS) {
      const archetype = catalog.find((candidate) => candidate.id === entry.archetypeId);
      expect(archetype, entry.archetypeId).toBeDefined();
      expect(archetype?.variants.some((variant) => variant.id === entry.variantId), entry.variantId).toBe(true);

      const candidate = zone(entry.archetypeId, entry.variantId);
      const profile = resolveParkGroundProfile(candidate);
      expect(profile.id).toBe(entry.profileId);
      expect(profile.version).toBe(entry.profileVersion);
      expect(profile.isPilot).toBe(true);
      expect(profile.guides.length).toBeGreaterThan(0);
      expect(isDefaultParkRecipe(resolveParkRecipe(entry.archetypeId))).toBe(false);
    }
  });

  it('retains the required fixed-program 3D hosts', () => {
    const required = new Map([
      ['japanese_garden', 'japanese_garden_bridge'],
      ['sports_field_complex', 'sports_field_furniture'],
      ['botanical_garden', 'botanical_conservatory'],
    ]);
    for (const entry of RENDERLOCK_V1_PARKS.filter((candidate) => required.has(candidate.archetypeId))) {
      const candidate = zone(entry.archetypeId, entry.variantId);
      expect(resolveParkSpecialtyStructureKind(candidate)).toBe(required.get(entry.archetypeId));
      expect(shouldMountParkProgramFrame(candidate, 0)).toBe(true);
    }
  });
});
