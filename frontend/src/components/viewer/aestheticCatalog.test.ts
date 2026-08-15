import { describe, expect, it } from 'vitest';

import {
  BUILDING_AESTHETIC_OPTIONS_V2,
  OPENSPACE_AESTHETIC_OPTIONS_V2,
  ROADWAY_AESTHETIC_OPTIONS_V2,
} from './aestheticCatalog';
import { TRANSPORT_STANDARDS } from '@/data/transportStandards';
import archetypeReferenceAvailability from '@/data/archetypeReferenceAvailability.json';
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

  it('exposes only building references that the generated runtime manifest marks available', () => {
    const availability = archetypeReferenceAvailability.domains.building.entries as Record<
      string,
      { availableUrls: string[] }
    >;
    for (const option of BUILDING_AESTHETIC_OPTIONS_V2) {
      const availableUrls = new Set(availability[option.id]?.availableUrls ?? []);
      expect(availableUrls.has(option.photoUrl), option.id).toBe(true);
      const thumbnailUrls = option.variants?.map((variant) => variant.thumbnailUrl) ?? [];
      expect(thumbnailUrls.every(Boolean), option.id).toBe(true);
      expect(thumbnailUrls.every((url) => availableUrls.has(url ?? '')), option.id).toBe(true);
      expect(new Set(thumbnailUrls).size, option.id).toBe(thumbnailUrls.length);
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
    expect(traditional).toMatchObject({
      minFloors: 3,
      maxFloors: 3,
      suggestedWidth_m: 20,
      suggestedDepth_m: 14,
      suggestedAreaSqm: 280,
    });
    expect(option).toMatchObject({
      suggestedWidth_m: 20,
      suggestedDepth_m: 14,
    });
  });

  it('advertises the reviewed historic market landmark as exactly two floors', () => {
    const option = BUILDING_AESTHETIC_OPTIONS_V2.find(
      (candidate) => candidate.id === 'food_hall_market_hall',
    );
    const historic = option?.variants?.find((variant) => (
      variant.id === 'market_historic_iron_glass'
    ));

    expect(historic).toMatchObject({
      minFloors: 2,
      maxFloors: 2,
      suggestedWidth_m: 45,
      suggestedDepth_m: 60,
      suggestedAreaSqm: 2700,
    });
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
