import { describe, expect, it } from 'vitest';
import { BATCH15_PARK_SKINS, batch15ParkSkinForSelection } from './parkBatch15Skins';

describe('batch 15 park variant skins', () => {
  it('registers thirty exact catalogue variants without people or large buildings', () => {
    expect(BATCH15_PARK_SKINS).toHaveLength(30);
    expect(new Set(BATCH15_PARK_SKINS.map((skin) => `${skin.archetypeId}:${skin.variantId}`)).size).toBe(30);
    expect(new Set(BATCH15_PARK_SKINS.map((skin) => skin.slug)).size).toBe(30);
    expect(BATCH15_PARK_SKINS.every((skin) => !skin.people && !skin.largeBuildings && skin.roles.length === 6)).toBe(true);
  });

  it('resolves only exact archetype and variant pairs', () => {
    expect(batch15ParkSkinForSelection('airport_airfield', 'airport_airfield_variant_0')?.slug).toBe('airport-major-hub-v0');
    expect(batch15ParkSkinForSelection('airport_airfield', 'airport_airfield_variant_2')).toBeNull();
  });
});
