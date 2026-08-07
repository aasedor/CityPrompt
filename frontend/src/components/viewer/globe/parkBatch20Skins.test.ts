import { describe, expect, it } from 'vitest';
import { BATCH20_PARK_SKINS, batch20ParkSkinForSelection } from './parkBatch20Skins';

describe('Batch 20 reference-derived park skins', () => {
  it('registers thirty exact variants with no people or embedded large buildings', () => {
    expect(BATCH20_PARK_SKINS).toHaveLength(30);
    expect(new Set(BATCH20_PARK_SKINS.map(({ slug }) => slug)).size).toBe(30);
    expect(BATCH20_PARK_SKINS.every(({ roles, people, largeBuildings }) => (
      roles.length === 6 && people === false && largeBuildings === false
    ))).toBe(true);
  });

  it('resolves exact selections without claiming the retained anchor', () => {
    expect(batch20ParkSkinForSelection('stepped_terraced_plaza', 'stepped_terraced_plaza_v1')?.slug)
      .toBe('stepped-spanish-travertine-v1');
    expect(batch20ParkSkinForSelection('stepped_terraced_plaza', 'stepped_terraced_plaza_v3')).toBeNull();
  });
});
