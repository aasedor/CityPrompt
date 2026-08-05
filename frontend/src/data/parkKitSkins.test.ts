import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import {
  NEIGHBORHOOD_PARK_SKIN_VARIANTS,
  isNeighborhoodParkLegoPilot,
  resolveParkKitSkin,
} from './parkKitSkins';

function zone(archetypeId: string, variantId?: string): Pick<SiteZone, 'properties'> {
  return {
    properties: {
      green_space_archetype_id: archetypeId,
      ...(variantId ? { green_space_selected_variant_id: variantId } : {}),
    },
  };
}

describe('neighborhood park LEGO skin pilot', () => {
  it('maps the four existing catalog variants to distinct local skins', () => {
    expect(NEIGHBORHOOD_PARK_SKIN_VARIANTS).toHaveLength(4);
    const skins = NEIGHBORHOOD_PARK_SKIN_VARIANTS.map((variantId) => (
      resolveParkKitSkin(zone('neighborhood_park', variantId))
    ));
    expect(skins.every(Boolean)).toBe(true);
    expect(new Set(skins.map((skin) => skin?.id)).size).toBe(4);
    expect(new Set(skins.map((skin) => skin?.baseGround)).size).toBe(4);
    expect(new Set(skins.map((skin) => skin?.materials.path.fill)).size).toBe(4);
    expect(new Set(skins.map((skin) => skin?.atlas.albedo)).size).toBe(4);
    expect(skins.every((skin) => skin?.atlas.sourceReference.endsWith('_angle_90.jpg'))).toBe(true);
  });

  it('keeps the pilot bounded to the neighborhood-park family', () => {
    expect(resolveParkKitSkin(zone('botanical_garden', 'botanical_garden_v0'))).toBeNull();
    expect(resolveParkKitSkin(zone('neighborhood_park'))).toBeNull();
    expect(isNeighborhoodParkLegoPilot(zone('neighborhood_park', 'neighborhood_park_v3'))).toBe(true);
    expect(isNeighborhoodParkLegoPilot(zone('urban_pocket_park', 'urban_pocket_park_v3'))).toBe(false);
  });

  it('tolerates a variant id stored as the archetype id', () => {
    expect(resolveParkKitSkin(zone('neighborhood_park_v2'))?.label).toBe('Natural Meadow');
  });
});
