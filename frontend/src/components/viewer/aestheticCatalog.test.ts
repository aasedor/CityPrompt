import { describe, expect, it } from 'vitest';

import {
  BUILDING_AESTHETIC_OPTIONS_V2,
  ROADWAY_AESTHETIC_OPTIONS_V2,
} from './aestheticCatalog';
import { TRANSPORT_STANDARDS } from '@/data/transportStandards';

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

describe('Calgary Street Manual reference assets', () => {
  it('uses every authored cross-section as the primary, traceable roadway reference', () => {
    const standards = TRANSPORT_STANDARDS.filter((entry) => entry.category === 'calgary_street_manual');
    expect(standards).toHaveLength(13);

    for (const standard of standards) {
      const option = ROADWAY_AESTHETIC_OPTIONS_V2.find(
        (candidate) => candidate.id === standard.archetypeId,
      );
      expect(option, standard.archetypeId).toBeDefined();
      expect(option?.photoUrl, standard.archetypeId).toBe(standard.sectionSvgUrl);
      expect(option?.archetypeImages?.[0]?.imageUrl, standard.archetypeId)
        .toBe(standard.sectionSvgUrl);
      expect(option?.standardSection, standard.archetypeId).toMatchObject({
        sectionSvgUrl: standard.sectionSvgUrl,
        rowM: standard.rowM,
        targetSpeedKmh: standard.targetSpeedKmh,
        citation: standard.citation,
      });
    }
  });
});
