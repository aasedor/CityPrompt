import { describe, expect, it } from 'vitest';
import { BATCH14_PARK_SKINS, batch14ParkSkinForSelection } from './parkBatch14Skins';

describe('batch 14 park skins', () => {
  it('registers ten exact catalogue variants without people or large buildings', () => {
    expect(BATCH14_PARK_SKINS).toHaveLength(10);
    expect(new Set(BATCH14_PARK_SKINS.map((skin) => skin.slug)).size).toBe(10);
    expect(BATCH14_PARK_SKINS.every((skin) => !skin.people && !skin.largeBuildings && skin.roles.length === 6)).toBe(true);
  });

  it('resolves only an exact archetype and variant pair', () => {
    expect(batch14ParkSkinForSelection('airport_airfield', 'airport_airfield_variant_2')?.slug).toBe('airport-general-aviation-v2');
    expect(batch14ParkSkinForSelection('airport_airfield', 'airport_airfield_variant_1')).toBeNull();
  });
});
