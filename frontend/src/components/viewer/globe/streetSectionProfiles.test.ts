import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import streetPathCatalog from '@/data/streetPathArchetypes.json';
import {
  CATALOG_STREET_ARCHETYPE_IDS,
  buildStreetRenderGroundTruthInstruction,
  resolvePilotStreetSectionProfile,
} from './streetSectionProfiles';

describe('street section pilot profiles', () => {
  it.each([
    ['yield_street', 6],
    ['narrow_residential_street', 10],
    ['collector_road', 16],
    ['main_street_complete', 18],
    ['calgary_local', 16],
    ['protected_bike_lane_bidirectional', 20],
    ['calgary_arterial_4lane_50', 33],
    ['multi_use_trail', 4],
    ['toronto_victorian_residential_street', 16],
    ['toronto_laneway', 5],
  ])('compiles %s to its measured right-of-way', (id, rowM) => {
    const profile = resolvePilotStreetSectionProfile(id);
    expect(profile).not.toBeNull();
    expect(profile?.rowM).toBeCloseTo(rowM, 4);
    expect(profile?.bands.reduce((sum, band) => sum + band.widthM, 0)).toBeCloseTo(rowM, 4);
  });

  it('keeps the protected two-way cycle track and its center marking', () => {
    const profile = resolvePilotStreetSectionProfile('protected_bike_lane_bidirectional');
    expect(profile?.bands.some((band) => band.kind === 'cycle' && band.widthM === 3.6)).toBe(true);
    expect(profile?.markings.some((marking) => marking.color === '#d6b34a')).toBe(true);
  });

  it('uses realistic centerline conventions for the two undivided streets', () => {
    expect(resolvePilotStreetSectionProfile('calgary_local')?.markings).toHaveLength(0);
    const protectedStreet = resolvePilotStreetSectionProfile('protected_bike_lane_bidirectional');
    expect(protectedStreet?.markings.filter((marking) => marking.color === '#d6b34a')).toHaveLength(2);
  });

  it('renders Toronto residential streets and laneways as distinct sections', () => {
    const residential = resolvePilotStreetSectionProfile('toronto_victorian_residential_street');
    expect(residential?.markings).toHaveLength(0);
    expect(residential?.bands.filter((band) => band.kind === 'parking')).toHaveLength(2);
    expect(residential?.treeOffsetsM).toHaveLength(2);

    const laneway = resolvePilotStreetSectionProfile('toronto_laneway');
    expect(laneway?.renderCurbs).toBe(false);
    expect(laneway?.markings).toHaveLength(0);
    expect(laneway?.bands.map((band) => band.kind)).toEqual(['shoulder', 'motor', 'shoulder']);
  });

  it('uses street hierarchy when an imported planner road has no archetype id', () => {
    const profile = resolvePilotStreetSectionProfile({
      properties: { street_role: 'spine' },
    } as Pick<SiteZone, 'properties'>);
    expect(profile?.archetypeId).toBe('main_street_complete');
    expect(profile?.rowM).toBe(18);
  });

  it('records the boulevard bands available for render-stage trees', () => {
    expect(resolvePilotStreetSectionProfile('calgary_local')?.treeOffsetsM).toHaveLength(2);
    expect(resolvePilotStreetSectionProfile('calgary_arterial_4lane_50')?.treeOffsetsM).toHaveLength(2);
  });

  it('adds realistic street trees only during render and only inside planting bands', () => {
    const planted = resolvePilotStreetSectionProfile('calgary_local');
    const trail = resolvePilotStreetSectionProfile('multi_use_trail');
    expect(planted).not.toBeNull();
    expect(trail).not.toBeNull();
    const plantedInstruction = buildStreetRenderGroundTruthInstruction(planted!);
    expect(plantedInstruction).toContain('Street trees are render-stage elements');
    expect(plantedInstruction).toContain('only inside the designated planting bands');
    expect(plantedInstruction).not.toContain('PRESERVE every street-tree row');
    expect(buildStreetRenderGroundTruthInstruction(trail!))
      .toContain('no designated street-tree band');
  });

  it('puts curbs at carriageway edges rather than the outer right-of-way', () => {
    const mainStreet = resolvePilotStreetSectionProfile('main_street_complete');
    expect(mainStreet?.curbOffsetsM).toHaveLength(2);
    expect(Math.max(...(mainStreet?.curbOffsetsM.map((offset) => Math.abs(offset)) ?? []))).toBeLessThan(
      (mainStreet?.rowM ?? 0) / 2,
    );
    expect(resolvePilotStreetSectionProfile('yield_street')?.renderCurbs).toBe(false);
  });

  it('gives planner-selected streets their stated movement hierarchy', () => {
    const residential = resolvePilotStreetSectionProfile('narrow_residential_street');
    expect(residential?.markings).toHaveLength(0);
    expect(residential?.bands.some((band) => band.kind === 'parking')).toBe(true);
    expect(residential?.treeOffsetsM).toHaveLength(2);

    const collector = resolvePilotStreetSectionProfile('collector_road');
    expect(collector?.markings.filter((marking) => marking.color === '#d6b34a')).toHaveLength(2);

    const mainStreet = resolvePilotStreetSectionProfile('main_street_complete');
    expect(mainStreet?.bands.filter((band) => band.kind === 'parking')).toHaveLength(2);
    expect(mainStreet?.treeOffsetsM).toHaveLength(2);
  });

  it('compiles contextual trails as soft-edged paths rather than motor roads', () => {
    const profile = resolvePilotStreetSectionProfile('multi_use_trail');
    expect(profile?.renderCurbs).toBe(false);
    expect(profile?.bands.map((band) => band.kind)).toEqual(['shoulder', 'path', 'shoulder']);
    expect(profile?.bands.reduce((sum, band) => sum + band.widthM, 0)).toBeCloseTo(4, 4);
    expect(profile?.markings).toEqual([
      expect.objectContaining({ color: '#d6b34a', dashed: true }),
    ]);
  });

  it('compiles a flush, curb-free section for a woonerf instead of a generic road', () => {
    const profile = resolvePilotStreetSectionProfile('woonerf_shared_street');
    expect(profile).not.toBeNull();
    expect(profile?.renderCurbs).toBe(false);
    expect(profile?.bands.map((band) => band.kind)).toEqual(['shoulder', 'motor', 'shoulder']);
    expect(profile?.markings).toHaveLength(0);
  });

  it('compiles every street/path catalog entry to a measured non-empty section', () => {
    expect(streetPathCatalog.archetypes).toHaveLength(115);
    expect(CATALOG_STREET_ARCHETYPE_IDS).toHaveLength(115);
    for (const entry of streetPathCatalog.archetypes) {
      const profile = resolvePilotStreetSectionProfile(entry.id);
      expect(profile, entry.id).not.toBeNull();
      expect(profile?.archetypeId, entry.id).toBe(entry.id);
      expect(profile?.rowM, entry.id).toBeGreaterThanOrEqual(3);
      expect(profile?.bands.length, entry.id).toBeGreaterThan(0);
      expect(profile?.bands.every((band) => band.widthM > 0), entry.id).toBe(true);
      expect(profile?.bands.reduce((sum, band) => sum + band.widthM, 0), entry.id)
        .toBeCloseTo(profile?.rowM ?? 0, 4);
      expect(profile?.renderSummary.length, entry.id).toBeGreaterThan(35);
    }
  });

  it('resolves every selected street variant into the section and render contract', () => {
    expect(streetPathCatalog.archetypes.reduce((sum, entry) => sum + entry.variants.length, 0))
      .toBe(355);
    for (const entry of streetPathCatalog.archetypes) {
      for (const variant of entry.variants) {
        const profile = resolvePilotStreetSectionProfile({
          properties: {
            road_archetype_id: entry.id,
            road_selected_variant_id: variant.id,
          },
        } as Pick<SiteZone, 'properties'>);
        expect(profile, `${entry.id}/${variant.id}`).not.toBeNull();
        expect(profile?.variantId, `${entry.id}/${variant.id}`).toBe(variant.id);
        expect(profile?.title, `${entry.id}/${variant.id}`).toContain(variant.label);
        expect(profile?.renderSummary, `${entry.id}/${variant.id}`).toContain(variant.description);
      }
    }
  });
});
