import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import streetPathCatalog from '@/data/streetPathArchetypes.json';
import {
  CATALOG_STREET_ARCHETYPE_IDS,
  buildStreetRenderGroundTruthInstruction,
  resolvePilotStreetSectionProfile,
} from './streetSectionProfiles';

function compiledStreetRecipe({
  familyId,
  archetypeId,
  variantId,
  appearanceKitId,
  rowM,
  node = false,
}: {
  familyId: string;
  archetypeId: string;
  variantId: string;
  appearanceKitId: string;
  rowM: number;
  node?: boolean;
}) {
  return {
    schema_version: 1,
    family_id: familyId,
    family_version: 1,
    kind: 'street',
    generator: 'street_section',
    archetype_id: archetypeId,
    variant_id: variantId,
    profile_id: `${archetypeId.replace(/_/g, '-')}-v1`,
    profile_version: 1,
    appearance_kit_id: appearanceKitId,
    target: node
      ? { target_type: 'street_node', approach_row_width_m: rowM, arm_count: 4 }
      : { target_type: 'street_segment', row_width_m: rowM, length_m: 80 },
    catalog_fingerprint: 'a'.repeat(64),
    capability_fingerprint: 'b'.repeat(64),
    recipe_hash: 'c'.repeat(64),
  };
}

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
    expect(profile?.bands.map((band) => band.kind)).toEqual([
      'shoulder', 'planting', 'motor', 'planting', 'shoulder',
    ]);
    expect(profile?.bands.find((band) => band.kind === 'motor')?.color).toBe('#a76547');
    expect(profile?.treeOffsetsM).toHaveLength(2);
    expect(profile?.markings).toHaveLength(0);
  });

  it('compiles green alleys as a permeable shared lane between two bioswales', () => {
    const profile = resolvePilotStreetSectionProfile('green_alley');
    expect(profile).not.toBeNull();
    expect(profile?.rowM).toBe(5);
    expect(profile?.renderCurbs).toBe(false);
    expect(profile?.bands.map((band) => band.kind)).toEqual([
      'planting', 'motor', 'planting',
    ]);
    expect(profile?.bands.filter((band) => band.kind === 'planting').map((band) => band.widthM))
      .toEqual([0.75, 0.75]);
    expect(profile?.bands.find((band) => band.kind === 'motor')?.widthM).toBe(3.5);
  });

  it('preserves the reviewed Calgary v0 local section and records the recipe target width', () => {
    const profile = resolvePilotStreetSectionProfile({
      properties: {
        public_realm_lego: {
          ...compiledStreetRecipe({
            familyId: 'street_local_public_realm',
            archetypeId: 'calgary_local',
            variantId: 'calgary_local_v0',
            appearanceKitId: 'calgary_contemporary_native',
            rowM: 14,
          }),
          recipe_hash: 'd'.repeat(64),
          capability_fingerprint: 'e'.repeat(64),
        },
      },
    } as Pick<SiteZone, 'properties'>);
    expect(profile).toMatchObject({
      familyId: 'street_local_public_realm',
      familyVersion: 1,
      appearanceKitId: 'calgary_contemporary_native',
      archetypeId: 'calgary_local',
      rowM: 16,
      targetRowM: 14,
      metricWidthLocked: true,
      recipeHash: 'd'.repeat(64),
      sourceCapabilityFingerprint: 'e'.repeat(64),
    });
    expect(profile?.bands.reduce((sum, band) => sum + band.widthM, 0)).toBe(16);
    expect(profile?.treeOffsetsM).toHaveLength(2);
    expect(profile?.bands.find((band) => band.kind === 'sidewalk')?.color).toBe('#c5c1b7');
    expect(profile?.rendererFingerprint).toMatch(/^street-v1-[0-9a-f]{16}$/);
  });

  it('fits the approved 18 m complete-main program to a saved 22 m envelope', () => {
    const profile = resolvePilotStreetSectionProfile({
      properties: {
        public_realm_lego: {
          ...compiledStreetRecipe({
            familyId: 'street_complete_main_22m',
            archetypeId: 'main_street_complete',
            variantId: 'main_street_complete_v2',
            appearanceKitId: 'timber_biophilic',
            rowM: 22,
          }),
        },
      },
    } as Pick<SiteZone, 'properties'>);
    expect(profile?.rowM).toBe(18);
    expect(profile?.targetRowM).toBe(22);
    expect(profile?.bands.reduce((sum, band) => sum + band.widthM, 0)).toBeCloseTo(18, 6);
    expect(profile?.bands.filter((band) => band.kind === 'cycle')).toHaveLength(0);
    expect(profile?.bands.filter((band) => band.kind === 'parking')).toHaveLength(2);
    expect(profile?.appearanceKitId).toBe('european_cobblestone_v1');
    expect(profile?.markings).toHaveLength(0);
  });

  it.each([
    ['street_local_public_realm', 'narrow_residential_street', 10, 1.5, 3],
    ['street_complete_main_18m', 'main_street_complete', 18, 3.2, 3.4],
  ] as const)(
    'fits the tropical %s/%s median program to the exact %sm right-of-way',
    (familyId, archetypeId, rowM, medianWidthM, laneWidthM) => {
      const profile = resolvePilotStreetSectionProfile({
        properties: {
          public_realm_lego: compiledStreetRecipe({
            familyId,
            archetypeId,
            variantId: `${archetypeId}_v3`,
            appearanceKitId: 'tropical_boulevard_v1',
            rowM,
          }),
        },
      } as Pick<SiteZone, 'properties'>);
      const median = profile?.bands.find((band) => band.sourceType === 'planted_median');
      const lanes = profile?.bands.filter((band) => band.kind === 'motor') ?? [];
      expect(profile?.appearanceKitId).toBe('tropical_boulevard_v1');
      expect(profile?.rowM).toBe(rowM);
      expect(profile?.bands.reduce((sum, band) => sum + band.widthM, 0))
        .toBeCloseTo(rowM, 8);
      expect(median).toMatchObject({
        kind: 'planting',
        centerM: 0,
        widthM: medianWidthM,
        surface: 'lush tropical planting',
      });
      expect(lanes).toHaveLength(2);
      expect(lanes.every((lane) => lane.widthM >= 3 && lane.widthM === laneWidthM))
        .toBe(true);
      expect(profile?.treeOffsetsM).toEqual([0]);
    },
  );

  it('makes the modern-minimalist section fully flush and curb-free', () => {
    const profile = resolvePilotStreetSectionProfile({
      properties: {
        public_realm_lego: compiledStreetRecipe({
          familyId: 'street_local_public_realm',
          archetypeId: 'narrow_residential_street',
          variantId: 'narrow_residential_street_v1',
          appearanceKitId: 'modern_minimalist_v1',
          rowM: 10,
        }),
      },
    } as Pick<SiteZone, 'properties'>);
    expect(profile?.renderCurbs).toBe(false);
    expect(profile?.curbOffsetsM).toEqual([]);
    expect(new Set(profile?.bands.map((band) => band.liftM.toFixed(6))).size).toBe(1);
  });

  it('keeps local-family trails and laneways at their source-program metric widths', () => {
    const profile = (archetypeId: string, appearanceKitId = 'calgary_contemporary_native') => resolvePilotStreetSectionProfile({
      properties: {
        width: archetypeId === 'multi_use_trail' ? 4 : 5,
        public_realm_lego: {
          ...compiledStreetRecipe({
            familyId: 'street_local_public_realm',
            archetypeId,
            variantId: archetypeId === 'multi_use_trail'
              ? 'multi_use_trail_v1'
              : `${archetypeId}_v0`,
            appearanceKitId,
            rowM: archetypeId === 'multi_use_trail' ? 4 : 5,
          }),
        },
      },
    } as Pick<SiteZone, 'properties'>);
    expect(profile('multi_use_trail', 'green_corridor_v1')).toMatchObject({
      rowM: 4,
      renderCurbs: false,
      appearanceKitId: 'green_corridor_v1',
    });
    expect(profile('toronto_laneway')?.rowM).toBe(5);
    expect(profile('toronto_laneway')?.renderCurbs).toBe(false);
  });

  it.each([
    ['yield_street', 6, 'dutch_woonerf_v1'],
    ['narrow_residential_street', 10, 'classic_tree_lined_v1'],
    ['woonerf_shared_street', 10, 'dutch_woonerf_v1'],
    ['green_alley', 5, 'green_corridor_v1'],
    ['toronto_laneway', 5, 'calgary_contemporary_native'],
    ['calgary_local', 16, 'calgary_contemporary_native'],
    ['multi_use_trail', 4, 'green_corridor_v1'],
  ])('executes strict-AI local source alias %s at %sm', (archetypeId, rowM, appearanceKitId) => {
    const isTrail = archetypeId === 'multi_use_trail';
    const profile = resolvePilotStreetSectionProfile({
      properties: {
        public_realm_lego: {
          ...compiledStreetRecipe({
            familyId: 'street_local_public_realm',
            archetypeId,
            variantId: isTrail ? 'multi_use_trail_v1' : `${archetypeId}_v0`,
            appearanceKitId,
            rowM,
          }),
        },
      },
    } as Pick<SiteZone, 'properties'>);
    expect(profile, archetypeId).not.toBeNull();
    expect(profile?.familyId).toBe('street_local_public_realm');
    expect(profile?.rowM).toBeCloseTo(rowM, 6);
  });

  it('exposes the existing parametric roundabout through the versioned family contract', () => {
    const profile = resolvePilotStreetSectionProfile({
      properties: {
        public_realm_lego: {
          ...compiledStreetRecipe({
            familyId: 'street_compact_roundabout',
            archetypeId: 'roundabout',
            variantId: 'roundabout_v0',
            appearanceKitId: 'classic_tree_lined_v1',
            rowM: 12,
            node: true,
          }),
        },
      },
    } as Pick<SiteZone, 'properties'>);
    expect(profile?.familyId).toBe('street_compact_roundabout');
    expect(profile?.appearanceKitId).toBe('classic_tree_lined_v1');
  });

  it('keeps malformed V1 metadata on the Classic profile path', () => {
    const profile = resolvePilotStreetSectionProfile({
      properties: {
        road_archetype_id: 'calgary_local',
        public_realm_lego: {
          family_id: 'street_local_public_realm',
          family_version: 1,
          archetype_id: 'calgary_local',
          variant_id: 'calgary_local_v0',
          appearance_kit_id: 'calgary_contemporary_native',
        },
      },
    } as Pick<SiteZone, 'properties'>);
    expect(profile?.archetypeId).toBe('calgary_local');
    expect(profile?.familyId).toBeUndefined();
    expect(profile?.appearanceKitId).toBeUndefined();
    expect(profile?.metricWidthLocked).toBeUndefined();
  });

  it('keeps an explicit family-pending fallback on procedural street geometry', () => {
    const profile = resolvePilotStreetSectionProfile({
      properties: {
        road_archetype_id: 'calgary_local',
        road_selected_variant_id: 'calgary_local_v0',
        public_realm_fallback: {
          schema_version: 1,
          state: 'family_pending',
          kind: 'street',
          generator: 'street_section',
          archetype_id: 'calgary_local',
          variant_id: 'calgary_local_v0',
          target_source: 'zone_geometry',
        },
      },
    } as Pick<SiteZone, 'properties'>);

    expect(profile?.archetypeId).toBe('calgary_local');
    expect(profile?.familyId).toBeUndefined();
    expect(profile?.metricWidthLocked).toBeUndefined();
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
