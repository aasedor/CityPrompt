import { describe, expect, it } from 'vitest';

import { BUILDING_AESTHETIC_OPTIONS_V2 } from './aestheticCatalog';

describe('building aesthetic reference assets', () => {
  it('uses authored catalogue folders and the authored hero before generated visual-system paths', () => {
    const option = BUILDING_AESTHETIC_OPTIONS_V2.find(
      (candidate) => candidate.id === 'contemporary_midrise_residential',
    );

    expect(option).toBeDefined();
    expect(option?.photoUrl).toBe(
      '/archetypes/buildings/contemporary_mid_rise_residential/hero.png',
    );
    expect(option?.archetypeImages?.[0]?.imageUrl).toBe(
      '/archetypes/buildings/contemporary_mid_rise_residential/variant_0.png',
    );
  });

  it('gives every building archetype four distinct authored variant cards', () => {
    for (const option of BUILDING_AESTHETIC_OPTIONS_V2) {
      expect(option.variants, option.id).toHaveLength(4);

      const thumbnailUrls = option.variants?.map((variant) => variant.thumbnailUrl) ?? [];
      expect(thumbnailUrls.every(Boolean), option.id).toBe(true);
      expect(new Set(thumbnailUrls).size, option.id).toBe(4);
    }
  });
});
