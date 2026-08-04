import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import openSpaceCatalog from '@/data/openSpaceArchetypes.json';
import {
  JAPANESE_GARDEN_BRIDGE_DIMENSIONS_M,
  PILOT_PARK_ARCHETYPE_IDS,
  buildParkRenderQualityInstruction,
  describeParkGroundGuideFit,
  fitParkGroundGuides,
  parkGroundSourceSignature,
  resolveParkGuideDimensionsM,
  resolveParkGroundProfile,
  resolveParkPlantingStructure,
  resolveParkSpecialtyStructureKind,
  shouldMountParkProgramFrame,
} from './parkGroundProfiles';
import {
  buildParkGroundPrompt,
  hasCurrentParkGroundSurface,
  isParkGroundZone,
  MAX_PARK_RENDER_GEOMETRY_REFERENCES,
  MAX_PARK_GROUND_BATCH_CALLS,
  replaceEdgeConnectedPaperWithTurf,
  resolveParkGroundSurfaceSource,
  selectLatestParkRenderReference,
  selectParkRenderGeometryZones,
  shouldDeferParkFinishingProp,
  shouldRenderLiveParkProp,
  takeParkGroundBatch,
} from './parkGroundTexture';

function zone(archetypeId: string): SiteZone {
  return {
    id: `zone-${archetypeId}`,
    project_id: 'project-1',
    zone_type: 'green_space',
    name: archetypeId,
    coordinates: [
      [-114.071, 51.041],
      [-114.069, 51.041],
      [-114.069, 51.042],
      [-114.071, 51.042],
    ],
    color: '#65a30d',
    properties: { green_space_archetype_id: archetypeId },
    sort_order: 0,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  };
}

function trustedParkRecipe(selection: Record<string, unknown>): Record<string, unknown> {
  return {
    schema_version: 1,
    kind: 'park',
    generator: 'park_kit',
    catalog_fingerprint: 'a'.repeat(64),
    capability_fingerprint: 'b'.repeat(64),
    recipe_hash: 'c'.repeat(64),
    ...selection,
  };
}

describe('park ground pilot profiles', () => {
  it.each([
    ['neighborhood_park', 'active_recreation'],
    ['urban_pocket_park', 'garden_courtyard'],
    ['linear_park_greenway', 'naturalistic_grove'],
    ['formal_civic_plaza', 'paved_plaza'],
    ['fountain_water_feature', 'paved_plaza'],
    ['stormwater_retention_pond', 'reservoir_perimeter'],
    ['pond_lake', 'formal_water_edge'],
    ['tennis_court_cluster', 'sports_perimeter'],
    ['wetland_rain_garden', 'water_ecology'],
    ['japanese_garden', 'japanese_stroll_garden'],
    ['sports_field_complex', 'sports_perimeter'],
    ['urban_forest', 'naturalistic_grove'],
    ['botanical_garden', 'botanical_collection'],
    ['nature_play_area', 'nature_play_grove'],
    ['reservoir_watershed_park', 'reservoir_perimeter'],
  ])('resolves %s with its coordinated planting structure', (id, planting) => {
    const candidate = zone(id);
    expect(resolveParkGroundProfile(candidate).isPilot).toBe(true);
    expect(resolveParkPlantingStructure(candidate)).toBe(planting);
  });

  it('gives specialty pilots authoritative program guides', () => {
    expect(resolveParkGroundProfile(zone('neighborhood_park')).guides).toHaveLength(9);
    expect(resolveParkGroundProfile(zone('japanese_garden')).guides).toHaveLength(4);
    expect(resolveParkGroundProfile(zone('sports_field_complex')).guides).toHaveLength(4);
    expect(resolveParkGroundProfile(zone('urban_forest')).guides).toHaveLength(3);
    expect(resolveParkGroundProfile(zone('botanical_garden')).guides).toHaveLength(5);
    expect(resolveParkGroundProfile(zone('nature_play_area')).guides).toHaveLength(5);
    expect(resolveParkGroundProfile(zone('tennis_court_cluster')).guides).toHaveLength(5);
    expect(resolveParkGroundProfile(zone('wetland_rain_garden')).guides).toHaveLength(6);
    expect(resolveParkGroundProfile(zone('pond_lake_variant_0')).guides[0].kind)
      .toBe('rounded_rectangle');
    expect(resolveParkGroundProfile(zone('japanese_garden')).includeCentralPlaza).toBe(false);
    expect(resolveParkGroundProfile(zone('sports_field_complex')).includeCentralPlaza).toBe(false);
    expect(resolveParkGroundProfile(zone('neighborhood_park')).includeCentralPlaza).toBe(false);
  });

  it('keeps fixed specialty structures independent from render-only planting', () => {
    expect(resolveParkSpecialtyStructureKind(zone('japanese_garden')))
      .toBe('japanese_garden_bridge');
    expect(resolveParkSpecialtyStructureKind(zone('japanese_garden_variant_2')))
      .toBe('japanese_garden_bridge');
    expect(resolveParkSpecialtyStructureKind(zone('sports_field_complex')))
      .toBe('sports_field_furniture');
    expect(resolveParkSpecialtyStructureKind(zone('tennis_court_cluster')))
      .toBe('tennis_court_furniture');
    expect(resolveParkSpecialtyStructureKind(zone('wetland_rain_garden')))
      .toBe('wetland_boardwalk');
    expect(resolveParkSpecialtyStructureKind(zone('botanical_garden')))
      .toBe('botanical_conservatory');
    expect(resolveParkSpecialtyStructureKind(zone('neighborhood_park'))).toBeNull();
    expect(shouldMountParkProgramFrame(zone('japanese_garden'), 0)).toBe(true);
    expect(shouldMountParkProgramFrame(zone('sports_field_complex'), 0)).toBe(true);
    expect(shouldMountParkProgramFrame(zone('wetland_rain_garden'), 0)).toBe(true);
    expect(shouldMountParkProgramFrame(zone('botanical_garden'), 0)).toBe(true);
    expect(shouldMountParkProgramFrame(zone('neighborhood_park'), 0)).toBe(false);
    expect(shouldMountParkProgramFrame(zone('neighborhood_park'), 1)).toBe(true);
  });

  it('gives every recurring master-planner public realm an authoritative layout guide', () => {
    const plannerArchetypes = [
      'neighborhood_park',
      'urban_pocket_park',
      'linear_park_greenway',
      'formal_civic_plaza',
      'fountain_water_feature',
      'stormwater_retention_pond',
    ];
    for (const id of plannerArchetypes) {
      const profile = resolveParkGroundProfile(zone(id));
      expect(profile.isPilot, id).toBe(true);
      expect(profile.guides.length, id).toBeGreaterThan(0);
      expect(profile.criticalConstraints.length, id).toBeGreaterThan(120);
    }
    expect(resolveParkGroundProfile(zone('linear_park_greenway')).guides[0].kind).toBe('axis');
  });

  it('invalidates the source signature after geometry, variant, or archetype changes', () => {
    const base = zone('neighborhood_park');
    const signature = parkGroundSourceSignature(base);
    const moved = { ...base, coordinates: base.coordinates.map(([x, y], i) => [x + (i === 0 ? 0.0001 : 0), y]) };
    const variant = { ...base, properties: { ...base.properties, green_space_selected_variant_id: 'neighborhood_park_v2' } };
    const access = { ...base, properties: { ...base.properties, park_access_points: [[-114.07, 51.041]] } };
    // Compatibility lock for existing paid orthophotos: the legacy V6 object
    // shape, property order and FNV-1a hash may not drift during LEGO rollout.
    expect(signature).toBe('pg6-ae6dfa95');
    expect(parkGroundSourceSignature(moved)).not.toBe(signature);
    expect(parkGroundSourceSignature(variant)).not.toBe(signature);
    expect(parkGroundSourceSignature(access)).not.toBe(signature);
    expect(parkGroundSourceSignature(zone('japanese_garden'))).not.toBe(signature);
  });

  it('keeps an untrusted nested recipe on the exact legacy V6 cache identity', () => {
    const legacy = zone('neighborhood_park');
    const untrusted = {
      ...legacy,
      properties: {
        ...legacy.properties,
        public_realm_lego: {
          family_id: 'park_neighborhood_community',
          family_version: 1,
          archetype_id: 'neighborhood_park',
          variant_id: 'neighborhood_park_v0',
          appearance_kit_id: 'rustic_timber_gravel_v1',
          planting_structure: 'active_recreation',
        },
      },
    } satisfies SiteZone;
    expect(parkGroundSourceSignature(untrusted)).toBe(parkGroundSourceSignature(legacy));
    expect(parkGroundSourceSignature(untrusted)).toMatch(/^pg6-/);
  });

  it('treats open and explicitly closed polygon rings as the same ground source', () => {
    const open = zone('reservoir_watershed_park_variant_0');
    const closed = {
      ...open,
      coordinates: [...open.coordinates, [...open.coordinates[0]]],
    } satisfies SiteZone;
    expect(parkGroundSourceSignature(closed)).toBe(parkGroundSourceSignature(open));
  });

  it('compiles catalog semantics for non-hand-authored parks instead of a neighborhood fallback', () => {
    const profile = resolveParkGroundProfile(zone('wetland_rain_garden'));
    expect(profile.isPilot).toBe(true);
    expect(profile.guides.length).toBeGreaterThan(0);
    expect(profile.plantingStructure).toBe('water_ecology');
    expect(profile.programDescription.toLowerCase()).toContain('wetland');
  });

  it('never mistakes courtyards or forecourts for sports courts', () => {
    for (const id of [
      'courtyard_plaza',
      'academic_courtyard',
      'cathedral_religious_forecourt',
      'cultural_institution_forecourt',
    ]) {
      const profile = resolveParkGroundProfile(zone(id));
      expect(profile.plantingStructure, id).not.toBe('sports_recreation');
      expect(profile.guides.some((guide) => guide.kind === 'tennis_court'), id).toBe(false);
      expect(profile.guides.some((guide) => guide.kind === 'soccer_field'), id).toBe(false);
    }
    expect(resolveParkGroundProfile(zone('pickleball_courts')).plantingStructure)
      .toBe('sports_recreation');
  });

  it('prefers the nested Public Realm LEGO selection and records its family contract', () => {
    const candidate = zone('neighborhood_park');
    candidate.properties = {
      ...candidate.properties,
      public_realm_lego: trustedParkRecipe({
        family_id: 'park_neighborhood_community',
        family_version: 1,
        archetype_id: 'community_park',
        variant_id: 'community_park_v2',
        planting_structure: 'naturalistic_grove',
        appearance_kit_id: 'mediterranean_xeriscape_v1',
      }),
    };
    const profile = resolveParkGroundProfile(candidate);
    expect(profile.archetypeId).toBe('community_park');
    expect(profile.title).toContain('Mediterranean Xeriscape');
    expect(profile.legoFamilyId).toBe('park_neighborhood_community');
    expect(profile.legoFamilyVersion).toBe(1);
    expect(profile.variantId).toBe('community_park_v2');
    expect(resolveParkPlantingStructure(candidate)).toBe('naturalistic_grove');
    expect(profile.guides).toHaveLength(9);
    const changedRecipe = {
      ...candidate,
      properties: {
        ...candidate.properties,
        public_realm_lego: {
          ...(candidate.properties?.public_realm_lego as Record<string, unknown>),
          recipe_hash: 'd'.repeat(64),
        },
      },
    } satisfies SiteZone;
    expect(parkGroundSourceSignature(changedRecipe))
      .not.toBe(parkGroundSourceSignature(candidate));
    expect(parkGroundSourceSignature(candidate)).toMatch(/^pg7-/);
  });

  it('binds civic, greenway, and water families to their executable signature assemblies', () => {
    const civic = zone('formal_civic_plaza');
    civic.properties = {
      ...civic.properties,
      planting_structure: 'active_recreation',
      public_realm_lego: trustedParkRecipe({
        family_id: 'park_civic_plaza',
        family_version: 1,
        archetype_id: 'formal_civic_plaza',
        variant_id: 'formal_civic_plaza_v0',
        appearance_kit_id: 'neoclassical_stone_v1',
        planting_structure: 'paved_plaza',
      }),
    };
    expect(resolveParkSpecialtyStructureKind(civic)).toBe('civic_fountain_assembly');
    expect(resolveParkPlantingStructure(civic)).toBe('paved_plaza');

    const water = zone('stormwater_retention_pond');
    water.properties = {
      ...water.properties,
      public_realm_lego: trustedParkRecipe({
        family_id: 'park_water_ecology',
        family_version: 1,
        archetype_id: 'stormwater_retention_pond',
        variant_id: 'stormwater_retention_pond_v0',
        appearance_kit_id: 'naturalistic_pond_v1',
        planting_structure: 'reservoir_perimeter',
      }),
    };
    expect(resolveParkSpecialtyStructureKind(water)).toBe('stormwater_control_assembly');
    const waterProfile = resolveParkGroundProfile(water);
    expect(waterProfile.archetypeId).toBe('stormwater_retention_pond');
    expect(waterProfile.guides.map(({ kind }) => kind))
      .toEqual(['ellipse', 'rectangle', 'rectangle', 'polyline']);
    expect(waterProfile.guideLegend.join(' ')).toContain('maintenance route');

    const greenway = zone('linear_park_greenway');
    greenway.properties = {
      ...greenway.properties,
      public_realm_lego: trustedParkRecipe({
        family_id: 'park_linear_greenway',
        family_version: 1,
        archetype_id: 'linear_park_greenway',
        variant_id: 'linear_park_greenway_v0',
        appearance_kit_id: 'rail_trail_v1',
        planting_structure: 'naturalistic_grove',
      }),
    };
    expect(resolveParkSpecialtyStructureKind(greenway)).toBe('greenway_edge_assembly');
  });

  it('compiles every open-space catalog entry and variant to an explicit 3D ground contract', () => {
    const entries = openSpaceCatalog.archetypes;
    expect(entries).toHaveLength(130);
    expect(entries.reduce((sum, entry) => sum + entry.variants.length, 0)).toBe(520);
    for (const entry of entries) {
      const base = zone(entry.id);
      const profile = resolveParkGroundProfile(base);
      expect(profile.isPilot, entry.id).toBe(true);
      expect(profile.archetypeId, entry.id).toBe(entry.id);
      expect(profile.guides.length, entry.id).toBeGreaterThan(0);
      expect(profile.guideLegend.length, entry.id).toBeGreaterThan(0);
      expect(profile.criticalConstraints.length, entry.id).toBeGreaterThan(180);
      expect(profile.plantingStructure, entry.id).toBeTruthy();
      for (const variant of entry.variants) {
        const variantZone = {
          ...base,
          properties: {
            ...base.properties,
            green_space_selected_variant_id: variant.id,
          },
        } satisfies SiteZone;
        const variantProfile = resolveParkGroundProfile(variantZone);
        expect(variantProfile.title, `${entry.id}/${variant.id}`).toContain(variant.label);
        if (PILOT_PARK_ARCHETYPE_IDS.includes(entry.id)) {
          expect(variantProfile.programDescription, `${entry.id}/${variant.id}`)
            .toContain(`Selected variant style: ${variant.label}`);
          expect(variantProfile.renderSummary, `${entry.id}/${variant.id}`)
            .toContain('without changing the locked program');
        } else {
          expect(variantProfile.programDescription, `${entry.id}/${variant.id}`)
            .toContain(variant.description);
        }
        expect(parkGroundSourceSignature(variantZone), `${entry.id}/${variant.id}`)
          .not.toBe(parkGroundSourceSignature(base));
      }
    }
  });

  it('keeps common court and field archetypes at regulation metric scale', () => {
    const tennis = resolveParkGroundProfile(zone('tennis_court_cluster')).guides
      .filter((guide) => guide.kind === 'tennis_court');
    expect(tennis).toHaveLength(4);
    for (const court of tennis) {
      expect(resolveParkGuideDimensionsM(court, { width: 82, height: 46 }))
        .toEqual({ width: 36.58, height: 18.29 });
    }
    const pickleball = resolveParkGroundProfile(zone('pickleball_courts')).guides;
    expect(pickleball).toHaveLength(2);
    for (const court of pickleball) {
      expect(resolveParkGuideDimensionsM(court, { width: 45, height: 30 }))
        .toEqual({ width: 18.29, height: 9.14 });
    }
    const basketball = resolveParkGroundProfile(zone('basketball_court')).guides[0];
    expect(resolveParkGuideDimensionsM(basketball, { width: 40, height: 30 }))
      .toEqual({ width: 32, height: 19 });
    const track = resolveParkGroundProfile(zone('running_track_oval')).guides[0];
    expect(resolveParkGuideDimensionsM(track, { width: 220, height: 130 }))
      .toEqual({ width: 176.91, height: 92.52 });
  });

  it('keeps toolbar plazas hardscaped instead of falling back to a lawn park', () => {
    const plaza = {
      ...zone('formal_civic_plaza'),
      zone_type: 'parking' as const,
      properties: { plaza_archetype_id: 'formal_civic_plaza' },
    };
    const profile = resolveParkGroundProfile(plaza);
    expect(profile.title.toLowerCase()).toContain('plaza');
    expect(profile.archetypeId).toBe('formal_civic_plaza');
    expect(resolveParkPlantingStructure(plaza)).toBe('paved_plaza');
    expect(profile.groundDescription.toLowerCase()).not.toContain('mowed lawn');
    expect(buildParkGroundPrompt(
      plaza,
      { width: 50, height: 35 },
      { playground: 0, pavilion: 0, bench: 2, plaza: 0 },
    )).toContain('warm-grey polygon is the plaza parcel');
    expect(isParkGroundZone(plaza)).toBe(true);
  });

  it('accepts planner courtyards even when their legacy zone type is development-like', () => {
    const courtyard = {
      ...zone('urban_pocket_park'),
      zone_type: 'development_area' as const,
      properties: { _plan_role: 'courtyard', green_space_archetype_id: 'urban_pocket_park' },
    };
    expect(isParkGroundZone(courtyard)).toBe(true);
  });

  it('does not inject the neighborhood plaza into specialty park prompts', () => {
    const emptyMarkers = { playground: 0, pavilion: 0, bench: 0, plaza: 0 };
    const japanese = buildParkGroundPrompt(zone('japanese_garden'), { width: 60, height: 50 }, emptyMarkers);
    const sports = buildParkGroundPrompt(zone('sports_field_complex'), { width: 140, height: 90 }, emptyMarkers);
    const neighborhood = buildParkGroundPrompt(zone('neighborhood_park'), { width: 80, height: 60 }, emptyMarkers);
    expect(japanese).not.toContain('small circular paved plaza');
    expect(sports).not.toContain('small circular paved plaza');
    expect(neighborhood).not.toContain('small circular paved plaza');
  });

  it('treats an authored specialty diagram as a tracing template instead of inventing circulation', () => {
    const prompt = buildParkGroundPrompt(
      zone('botanical_garden'),
      { width: 146, height: 80 },
      { playground: 0, pavilion: 0, bench: 0, plaza: 0, access: 0 },
    );
    expect(prompt).toContain('Do not add any new path, spur, axis, ring, radial connection, plaza or entrance');
    expect(prompt).not.toContain('Provide a connected internal path network');
    expect(prompt).toContain('FINAL PIXEL-TO-PIXEL TOPOLOGY LOCK');
    expect(prompt).toContain('Do not create any additional hardscape, path branch, radial axis, circle, plaza, bed, water feature or structure.');
  });

  it('uses a saved render as appearance only while preserving diagram topology', () => {
    const prompt = buildParkGroundPrompt(
      zone('wetland_rain_garden'),
      { width: 80, height: 60 },
      { playground: 0, pavilion: 0, bench: 0, plaza: 0, access: 0 },
      true,
    );
    expect(prompt).toContain('APPEARANCE TARGET');
    expect(prompt).toContain('do not copy the render camera');
    expect(prompt).toContain('the diagram always wins for boundary, scale, count and topology');
    expect(prompt).toContain('looping boardwalk network');
    expect(prompt).toContain('FINAL PIXEL-TO-PIXEL TOPOLOGY LOCK');
  });

  it('includes measured surroundings without weakening the diagram topology lock', () => {
    const prompt = buildParkGroundPrompt(
      zone('neighborhood_park'),
      { width: 80, height: 60 },
      { playground: 0, pavilion: 0, bench: 0, plaza: 0, access: 2 },
      false,
      'SURROUNDING-SITE CONTEXT:\n- proposed street "Main Street" touches on the east edge\nEDGE RESPONSE: align park gateways with the street.',
    );

    expect(prompt).toContain('proposed street "Main Street"');
    expect(prompt).toContain('align park gateways with the street');
    expect(prompt).toContain('FINAL PIXEL-TO-PIXEL TOPOLOGY LOCK');
    expect(prompt.indexOf('SURROUNDING-SITE CONTEXT'))
      .toBeLessThan(prompt.indexOf('FINAL PIXEL-TO-PIXEL TOPOLOGY LOCK'));
  });

  it('selects the newest saved render as the drape appearance target', () => {
    expect(selectLatestParkRenderReference([
      { id: 'older', created_at: '2026-07-17T12:00:00Z' },
      { id: 'newest', created_at: '2026-07-18T12:00:00Z' },
      { id: 'middle', created_at: '2026-07-18T06:00:00Z' },
    ])?.id).toBe('newest');
    expect(selectLatestParkRenderReference([])).toBeNull();
  });

  it('locks the five same-geography alternatives to distinct programs', () => {
    const emptyMarkers = { playground: 0, pavilion: 0, bench: 0, plaza: 0, access: 2 };
    const prompts = Object.fromEntries([
      'sports_field_complex',
      'urban_forest',
      'botanical_garden',
      'japanese_garden',
      'nature_play_area',
    ].map((id) => [id, buildParkGroundPrompt(zone(id), { width: 146, height: 80 }, emptyMarkers)]));

    expect(prompts.sports_field_complex).toContain('100 by 64 metre football/soccer pitch');
    expect(prompts.sports_field_complex).toContain('36.58 by 18.29 metres');
    expect(prompts.urban_forest).toContain('three quarters of the parcel must read as woodland habitat');
    expect(prompts.botanical_garden).toContain('conservatory pad');
    expect(prompts.japanese_garden).toContain('exact red lacquer bridge-deck footprint');
    expect(prompts.nature_play_area).toContain('two linked activity clearings');
  });

  it('keeps fixed park programs at real-world metre dimensions on the trial parcel', () => {
    const trialSize = { width: 146, height: 80 };
    const sports = resolveParkGroundProfile(zone('sports_field_complex')).guides;
    const football = sports.find((guide) => guide.kind === 'soccer_field');
    const tennis = sports.filter((guide) => guide.kind === 'tennis_court');
    expect(football && resolveParkGuideDimensionsM(football, trialSize)).toEqual({
      width: 100,
      height: 64,
    });
    expect(tennis).toHaveLength(3);
    for (const court of tennis) {
      expect(resolveParkGuideDimensionsM(court, trialSize)).toEqual({
        width: 36.58,
        height: 18.29,
      });
    }

    const japanese = resolveParkGroundProfile(zone('japanese_garden')).guides;
    expect(resolveParkGuideDimensionsM(japanese[1], trialSize)).toEqual({ width: 34, height: 20 });
    expect(resolveParkGuideDimensionsM(japanese[2], trialSize)).toEqual({ width: 22, height: 14 });
    expect(resolveParkGuideDimensionsM(japanese[3], trialSize)).toEqual({
      width: JAPANESE_GARDEN_BRIDGE_DIMENSIONS_M.length,
      height: 0,
    });

    const botanical = resolveParkGroundProfile(zone('botanical_garden')).guides;
    expect(resolveParkGuideDimensionsM(botanical[1], trialSize)).toEqual({ width: 24, height: 14 });
    const naturePlay = resolveParkGroundProfile(zone('nature_play_area')).guides;
    expect(resolveParkGuideDimensionsM(naturePlay[2], trialSize)).toEqual({ width: 28, height: 22 });
    expect(resolveParkGuideDimensionsM(naturePlay[3], trialSize)).toEqual({ width: 30, height: 22 });
    expect(resolveParkGuideDimensionsM(naturePlay[4], trialSize)).toEqual({ width: 14, height: 5 });
  });

  it('omits a complete tennis court when a concave parcel would clip it', () => {
    const sports = resolveParkGroundProfile(zone('sports_field_complex')).guides;
    const fit = fitParkGroundGuides(
      sports,
      { width: 144, height: 76.8 },
      [[0, 0], [0.82, 0], [0.82, 0.34], [1, 0.34], [1, 1], [0, 1]],
    );

    expect(fit.guides.filter((guide) => guide.kind === 'soccer_field')).toHaveLength(1);
    expect(fit.guides.filter((guide) => guide.kind === 'tennis_court')).toHaveLength(2);
    expect(fit.omittedGuides.filter((guide) => guide.kind === 'tennis_court')).toHaveLength(1);
    expect(describeParkGroundGuideFit(fit)).toContain('2 complete tennis courts fit out of 3');
  });

  it('reduces a four-court archetype to one complete court on a small parcel', () => {
    const tennis = resolveParkGroundProfile(zone('tennis_court_cluster')).guides;
    const fit = fitParkGroundGuides(tennis, { width: 46, height: 26 });

    expect(fit.guides.filter((guide) => guide.kind === 'tennis_court')).toHaveLength(1);
    expect(fit.omittedGuides.filter((guide) => guide.kind === 'tennis_court')).toHaveLength(3);
    expect(describeParkGroundGuideFit(fit)).toContain('1 complete tennis court fits out of 4');
  });

  it('finds orientations for the field and all three whole courts in the current sloped trial parcel', () => {
    const sports = resolveParkGroundProfile(zone('sports_field_complex')).guides;
    const fit = fitParkGroundGuides(
      sports,
      { width: 144, height: 76.8 },
      [
        [0, 0.9172],
        [0.0316, 0],
        [1, 0.1288],
        [0.983, 1],
      ],
    );

    const fittedField = fit.guides.find((guide) => guide.kind === 'soccer_field');
    expect(fittedField).toBeDefined();
    expect(fit.guides.filter((guide) => guide.kind === 'tennis_court')).toHaveLength(3);
    expect(fit.omittedGuides.filter((guide) => guide.kind === 'tennis_court')).toHaveLength(0);
    expect(fittedField?.rotationDeg).not.toBe(0);
    expect(describeParkGroundGuideFit(fit)).toBe('');
  });

  it('turns a regulation court to an alternate orientation when that is the only whole fit', () => {
    const fit = fitParkGroundGuides([{
      kind: 'tennis_court',
      x: 0.5,
      y: 0.5,
      width: 0.9,
      height: 0.9,
      widthM: 36.58,
      heightM: 18.29,
      color: '#3f6f82',
      strokeColor: '#f4f2df',
      strokeWidthM: 0.08,
    }], { width: 20, height: 40 });

    expect(fit.guides).toHaveLength(1);
    expect(Math.abs(fit.guides[0].rotationDeg ?? 0)).toBe(90);
    expect(resolveParkGuideDimensionsM(fit.guides[0], { width: 20, height: 40 }))
      .toEqual({ width: 36.58, height: 18.29 });
  });

  it('removes every part of a grouped object when its outer envelope does not fit', () => {
    const fit = fitParkGroundGuides([
      {
        kind: 'ellipse', x: 0.5, y: 0.5, width: 1, height: 1,
        widthM: 120, heightM: 120, color: '#668855', atomicGroup: 'cricket-field',
      },
      {
        kind: 'rectangle', x: 0.5, y: 0.5, width: 0.1, height: 0.1,
        widthM: 22.56, heightM: 3.05, color: '#aa9966', atomicGroup: 'cricket-field',
      },
    ], { width: 100, height: 100 });

    expect(fit.guides).toHaveLength(0);
    expect(fit.omittedGuides).toHaveLength(2);
  });

  it('tells the image model to keep only complete parcel-compatible elements', () => {
    const sportsZone = zone('sports_field_complex');
    sportsZone.coordinates = [
      [0, 1], [0.82, 1], [0.82, 0.66], [1, 0.66], [1, 0], [0, 0],
    ];
    const prompt = buildParkGroundPrompt(
      sportsZone,
      { width: 144, height: 76.8 },
      { playground: 0, pavilion: 0, bench: 0, plaza: 0 },
    );

    expect(prompt).toContain('2 complete tennis courts fit out of 3');
    expect(prompt).toContain('Do not draw, reconstruct, crop, truncate, squeeze or scale');
  });

  it('forces the reservoir drape to cover all dry land without diagram-paper margins', () => {
    const prompt = buildParkGroundPrompt(
      zone('reservoir_watershed_park'),
      { width: 148, height: 84 },
      { playground: 0, pavilion: 0, bench: 6, plaza: 0 },
    );
    expect(prompt).toContain('covering about 42 percent of the parcel');
    expect(prompt).toContain('fully rendered edge-to-edge');
    expect(prompt).toContain('zero white, blank, unpainted or paper-like ground');
    expect(prompt).toContain('Every dry-land pixel');
  });

  it('locks the five added planner grounds to their actual programs', () => {
    const emptyMarkers = { playground: 0, pavilion: 0, bench: 0, plaza: 0, access: 2 };
    const prompts = Object.fromEntries([
      'urban_pocket_park',
      'linear_park_greenway',
      'formal_civic_plaza',
      'fountain_water_feature',
      'stormwater_retention_pond',
    ].map((id) => [id, buildParkGroundPrompt(zone(id), { width: 90, height: 50 }, emptyMarkers)]));

    expect(prompts.urban_pocket_park).toContain('one usable clear room');
    expect(prompts.urban_pocket_park).toContain('no playground');
    expect(prompts.linear_park_greenway).toContain('exact continuous 3.5-metre multi-use trail');
    expect(prompts.linear_park_greenway).toContain('one continuous, obstruction-free route');
    expect(prompts.formal_civic_plaza).toContain('generous contiguous hardscape event area');
    expect(prompts.fountain_water_feature).toContain('one clear circular water basin');
    expect(prompts.stormwater_retention_pond).toContain('functioning stormwater infrastructure');
    expect(prompts.stormwater_retention_pond).toContain('No trees, benches, paths, buildings or decorative features may enter the water');
  });

  it('cleans only edge-connected paper while preserving enclosed pale hardscape', () => {
    const width = 5;
    const height = 5;
    const pixels = new Uint8ClampedArray(width * height * 4);
    for (let pixel = 0; pixel < width * height; pixel += 1) {
      pixels.set([248, 248, 246, 255], pixel * 4);
    }
    // A green ring disconnects the pale centre hardscape from the white edge.
    for (const pixel of [6, 7, 8, 11, 13, 16, 17, 18]) {
      pixels.set([82, 118, 58, 255], pixel * 4);
    }
    pixels.set([245, 245, 242, 255], 12 * 4);

    expect(replaceEdgeConnectedPaperWithTurf(pixels, width, height)).toBe(16);
    expect(Array.from(pixels.slice(12 * 4, 12 * 4 + 3))).toEqual([245, 245, 242]);
    expect(pixels[1]).toBeLessThan(200);
  });

  it('shows finishing props only after a park surface is compiled', () => {
    const candidate = zone('urban_pocket_park');
    const profile = resolveParkGroundProfile(candidate);
    const generated = {
      ...candidate,
      properties: {
        ...candidate.properties,
        community_3d: {
          schema_version: 1,
          state: 'compiled',
          kind: 'park',
          generator: 'park_kit',
          compiled_at: '2026-07-17T00:00:00Z',
        },
        park_ground_texture: {
          url: '/park.png',
          document_id: 'doc-1',
          bbox: { west: -114.071, south: 51.041, east: -114.069, north: 51.042 },
          uv_rect: { u0: 0.1, v0: 0.1, u1: 0.9, v1: 0.9 },
          size_m: { width: 140, height: 110 },
          model: 'gemini-3.1-flash-image',
          generated_at: '2026-07-17T00:00:00Z',
          source_signature: parkGroundSourceSignature(candidate),
          profile_id: profile.id,
          profile_version: profile.version,
          archetype_id: profile.archetypeId,
        },
      },
    } satisfies SiteZone;
    expect(shouldDeferParkFinishingProp(generated, 'tree')).toBe(false);
    expect(shouldDeferParkFinishingProp(generated, 'bench')).toBe(false);
    expect(shouldDeferParkFinishingProp(generated, 'playground')).toBe(false);
    expect(shouldDeferParkFinishingProp(candidate, 'tree')).toBe(true);
    expect(shouldRenderLiveParkProp(candidate, 'tree', true)).toBe(false);
    expect(shouldRenderLiveParkProp(generated, 'tree', true)).toBe(true);
    expect(shouldRenderLiveParkProp(candidate, 'bench', true)).toBe(false);
    expect(shouldRenderLiveParkProp(candidate, 'playground', false)).toBe(false);
    expect(shouldRenderLiveParkProp(candidate, 'playground', true)).toBe(true);
    expect(shouldRenderLiveParkProp(candidate, 'pavilion', false)).toBe(false);
  });

  it('does not pre-author bench locations before paths and water are finalized', () => {
    const prompt = buildParkGroundPrompt(
      zone('reservoir_watershed_park'),
      { width: 148, height: 84 },
      { playground: 0, pavilion: 0, bench: 6, plaza: 0 },
    );
    expect(prompt).not.toContain('DARK dash');
    expect(prompt).not.toContain('bench spot');
    expect(prompt).not.toContain('bench pad');
    expect(prompt).toContain('mature trees and benches are completed by the final architectural render');
  });

  it('uses a zero-call procedural surface after Generate 3D and lets AI ground win', () => {
    const candidate = zone('linear_park_greenway');
    expect(resolveParkGroundSurfaceSource(candidate)).toBe('none');
    expect(hasCurrentParkGroundSurface(candidate)).toBe(false);

    const compiled = {
      ...candidate,
      properties: {
        ...candidate.properties,
        community_3d: {
          schema_version: 1,
          state: 'compiled',
          kind: 'park',
          generator: 'park_kit',
          compiled_at: '2026-07-17T01:00:00Z',
        },
      },
    } satisfies SiteZone;
    expect(resolveParkGroundSurfaceSource(compiled)).toBe('procedural');
    expect(hasCurrentParkGroundSurface(compiled)).toBe(true);

    const profile = resolveParkGroundProfile(compiled);
    const upgraded = {
      ...compiled,
      properties: {
        ...compiled.properties,
        park_ground_texture: {
          url: '/park.png',
          document_id: 'doc-1',
          bbox: { west: -114.071, south: 51.041, east: -114.069, north: 51.042 },
          uv_rect: { u0: 0.1, v0: 0.1, u1: 0.9, v1: 0.9 },
          size_m: { width: 140, height: 110 },
          model: 'gemini-3.1-flash-image',
          generated_at: '2026-07-17T00:00:00Z',
          source_signature: parkGroundSourceSignature(compiled),
          profile_id: profile.id,
          profile_version: profile.version,
          archetype_id: profile.archetypeId,
        },
      },
    } satisfies SiteZone;
    expect(resolveParkGroundSurfaceSource(upgraded)).toBe('ai');
  });

  it('gives all six recurring public-realm archetypes a zero-call compiled ground contract', () => {
    const recurring = [
      'neighborhood_park',
      'urban_pocket_park',
      'linear_park_greenway',
      'formal_civic_plaza',
      'fountain_water_feature',
      'stormwater_retention_pond',
    ];
    for (const archetypeId of recurring) {
      const candidate = zone(archetypeId);
      const compiled = {
        ...candidate,
        properties: {
          ...candidate.properties,
          community_3d: {
            schema_version: 1,
            state: 'compiled',
            kind: 'park',
            generator: 'park_kit',
            compiled_at: '2026-07-18T00:00:00Z',
          },
        },
      } satisfies SiteZone;
      expect(resolveParkGroundProfile(compiled).isPilot, archetypeId).toBe(true);
      expect(resolveParkGroundSurfaceSource(compiled), archetypeId).toBe('procedural');
      expect(hasCurrentParkGroundSurface(compiled), archetypeId).toBe(true);
      expect(shouldDeferParkFinishingProp(compiled, 'tree'), archetypeId).toBe(false);
      expect(shouldDeferParkFinishingProp(compiled, 'bench'), archetypeId).toBe(false);
    }
  });

  it('caps a paid multi-park action to a deliberate six-call batch', () => {
    const pending = Array.from({ length: 83 }, (_, index) => `park-${index}`);
    expect(MAX_PARK_GROUND_BATCH_CALLS).toBe(6);
    expect(takeParkGroundBatch(pending)).toEqual(pending.slice(0, 6));
    expect(takeParkGroundBatch(pending.slice(0, 3))).toEqual(pending.slice(0, 3));
  });

  it('bounds final-render park geometry references and prioritizes critical water/program layouts', () => {
    const candidates = [
      zone('neighborhood_park'),
      zone('formal_civic_plaza'),
      zone('sports_field_complex'),
      zone('japanese_garden'),
      zone('stormwater_retention_pond'),
      zone('reservoir_watershed_park'),
      zone('botanical_garden'),
    ];
    expect(MAX_PARK_RENDER_GEOMETRY_REFERENCES).toBe(4);
    expect(selectParkRenderGeometryZones(candidates).map((candidate) => candidate.name)).toEqual([
      'reservoir_watershed_park',
      'stormwater_retention_pond',
      'japanese_garden',
      'sports_field_complex',
    ]);
    expect(selectParkRenderGeometryZones(candidates, 1)[0].name)
      .toBe('reservoir_watershed_park');
    expect(selectParkRenderGeometryZones(candidates, 0)).toEqual([]);
  });

  it('routes park paths through exact master-plan gateways', () => {
    const prompt = buildParkGroundPrompt(
      zone('neighborhood_park'),
      { width: 80, height: 60 },
      { playground: 0, pavilion: 0, bench: 0, plaza: 0, access: 3 },
    );
    expect(prompt).toContain('3 PALE-CREAM circles');
    expect(prompt).toContain('continuous path centerline to every gateway');
    expect(prompt).toContain('surrounding street/path network');
    expect(prompt).toContain('Never use one perfect circular track');
    expect(prompt).toContain('native meadow and rain-garden');
  });

  it('sets a mature park quality bar appropriate to nadir and oblique views', () => {
    const profile = resolveParkGroundProfile(zone('botanical_garden'));
    const nadir = buildParkRenderQualityInstruction(profile, 18);
    const oblique = buildParkRenderQualityInstruction(profile, 52);
    expect(nadir).toContain('NEAR-NADIR QUALITY');
    expect(nadir).toContain('aerial mosaic');
    expect(oblique).toContain('OBLIQUE QUALITY');
    expect(oblique).toContain('canopy depth');
    expect(oblique).toContain('No cloned evenly spaced trees');
    expect(oblique).toContain('Trees and benches are render-finishing elements');
    expect(oblique).toContain('chosen only after the exact path, water and fixed-program layout is understood');
    expect(oblique).toContain('paved furnishing shoulders directly beside paths');
    expect(oblique).toContain('never put a bench or tree on a path centerline');
  });
});
