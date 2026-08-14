import { describe, expect, it } from 'vitest';

import {
  BUILDING_AESTHETIC_OPTIONS_V2,
  OPENSPACE_AESTHETIC_OPTIONS_V2,
  ROADWAY_AESTHETIC_OPTIONS_V2,
} from './aestheticCatalog';
import { TRANSPORT_STANDARDS } from '@/data/transportStandards';
import stickerMethodPilots from '@/data/stickerMethodPilots.json';

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

  it('gives traditional Machiya an explicit photoreal card render without changing its variant metadata', () => {
    const option = BUILDING_AESTHETIC_OPTIONS_V2.find(
      (candidate) => candidate.id === 'japanese_machiya_mixed_use',
    );
    const traditional = option?.variants?.find((variant) => (
      variant.id === 'machiya_traditional_restored'
    ));

    expect(option?.catalogCardImageUrl).toBe(
      '/archetypes/buildings/japanese_machiya_mixed_use/variant_3.png',
    );
    expect(traditional?.thumbnailUrl).toBe(
      '/archetypes/buildings/japanese_machiya_mixed_use/variant_0.png',
    );
  });

  it('keeps every approved Sticker Method pilot on its catalogue-domain variant image', () => {
    for (const pilot of stickerMethodPilots.buildings) {
      const option = BUILDING_AESTHETIC_OPTIONS_V2.find(
        (candidate) => candidate.id === pilot.archetypeId,
      );
      const variant = option?.variants?.find((candidate) => candidate.id === pilot.variantId);
      expect(variant?.thumbnailUrl, `${pilot.archetypeId}/${pilot.variantId}`)
        .toMatch(/^\/archetypes\/buildings\//);
    }

    for (const pilot of stickerMethodPilots.parks) {
      const option = OPENSPACE_AESTHETIC_OPTIONS_V2.find(
        (candidate) => candidate.id === pilot.archetypeId,
      );
      const variant = option?.variants?.find((candidate) => candidate.id === pilot.variantId);
      expect(variant?.thumbnailUrl, `${pilot.archetypeId}/${pilot.variantId}`)
        .toMatch(/^\/archetypes\/openspaces\//);
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

describe('current street catalogue reference assets', () => {
  it('uses the current CityPrompt variants instead of legacy hero images', () => {
    const option = ROADWAY_AESTHETIC_OPTIONS_V2.find(
      (candidate) => candidate.id === 'narrow_residential_street',
    );

    expect(option).toBeDefined();
    expect(option?.photoUrl).toBe(
      '/archetypes/streets/narrow-residential-street/variant_0.webp',
    );
    expect(option?.variants?.map((variant) => variant.thumbnailUrl)).toEqual([
      '/archetypes/streets/narrow-residential-street/variant_0.webp',
      '/archetypes/streets/narrow-residential-street/variant_1.webp',
      '/archetypes/streets/narrow-residential-street/variant_2.webp',
      '/archetypes/streets/narrow-residential-street/variant_3.webp',
    ]);
  });

  it('exposes only the variants authored for each street archetype', () => {
    const diagram = ROADWAY_AESTHETIC_OPTIONS_V2.find(
      (candidate) => candidate.id === 'speed_hump_diagram',
    );

    expect(diagram?.variants).toHaveLength(1);
    expect(diagram?.archetypeImages).toHaveLength(1);
    expect(diagram?.archetypeImages?.[0]?.imageUrl).toBe(
      '/archetypes/streets/speed-hump-diagram/variant_0.webp',
    );
  });
});
