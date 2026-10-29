import { afterEach, describe, expect, it, vi } from 'vitest';
import validation from '@/data/validationCatalogue.json';
import expansion from '@/data/classroomExpansion.json';

// Isolate the shared registration contract from whichever local pilots a
// catalogue sync currently generates. Placement and persistence remain real.
vi.mock('./publishedBuildingAssets', () => {
  const building = (id: string, readiness: 'ready' | 'pilot', revision: string) => ({
    id, kind: 'object', definitionVersion: 1, readiness,
    label: id === 'generated_published_fixture' ? 'Published fixture hall' : 'Local fixture hall',
    description: 'An exact authored building.', thumbnail: '/fixture-hall.png',
    zoneType: 'building', reshapeMode: 'fixed_native',
    width: 20, depth: 24, minWidth: 20, minDepth: 24, maxSize: 100,
    nativeDimensions: [16, 20, 9],
    calgaryGuide: { groupId: 'civic', basis: 'form_reference' },
    model: { variantId: `${id}_variant`, revision, method: 'RLASM 6.1' },
    reshapeDescription: 'The authored building keeps its proportions.',
    properties: {
      building_archetype_id: 'generated_fixture_hall',
      development_archetype_id: 'generated_fixture_hall',
      development_selected_variant_id: `${id}_variant`,
      floors: 3, floor_count: 3, native_home_plot: false, native_plot_axes: true,
    },
  });
  const assets = [
    building('generated_published_fixture', 'ready', 'published-fixture-v003'),
    building('generated_local_fixture', 'pilot', 'local-fixture-v002'),
    building('validation_timber_sanctuary_church_glazed_gable', 'ready', 'must-not-replace-validation'),
    building('clay_side_by_side_duplex', 'ready', 'must-not-replace-expansion'),
    building('infill_home', 'ready', 'must-not-replace-legacy-saved-home'),
    building('generated_published_fixture', 'ready', 'must-not-duplicate-new-card'),
    {
      ...building('generated_validation_alias_fixture', 'ready', 'must-not-shadow-curated-design'),
      model: {
        variantId: 'timber_sanctuary_church_glazed_gable',
        revision: 'must-not-shadow-curated-design', method: 'RLASM 6.1',
      },
      properties: {
        building_archetype_id: 'timber_sanctuary_church',
        development_archetype_id: 'timber_sanctuary_church',
        development_selected_variant_id: 'timber_sanctuary_church_glazed_gable',
        floors: 3, floor_count: 3, native_home_plot: false, native_plot_axes: true,
      },
    },
  ];
  return {
    CATALOGUE_BUILDING_ASSETS: assets,
    PUBLISHED_BUILDING_ASSETS: assets.filter(asset => asset.readiness === 'ready'),
  };
});

afterEach(() => {
  vi.unstubAllEnvs();
  vi.resetModules();
});

describe('generated building registration', () => {
  it.each([false, true])('exposes generated exact designs through the UI catalogue with DEV=%s', async development => {
    vi.stubEnv('DEV', development);
    const { CANONICAL_CHOICES, CLASSROOM_CHOICES, filterCanonicalChoices } = await import('./canonicalCatalogue');
    const choice = filterCanonicalChoices('building', 'Published fixture hall')
      .find(item => item.placements[0]?.id === 'generated_published_fixture');
    expect(choice).toBeDefined();
    expect(choice?.option).toMatchObject({
      id: 'generated_fixture_hall', photoUrl: '/fixture-hall.png',
      variants: [{ id: 'generated_published_fixture_variant', thumbnailUrl: '/fixture-hall.png' }],
    });
    expect(CLASSROOM_CHOICES).toContain(choice);
    expect(CANONICAL_CHOICES.some(item => item.placements[0]?.id === 'generated_local_fixture')).toBe(development);
    expect(new Set(CANONICAL_CHOICES.map(item => item.id)).size).toBe(CANONICAL_CHOICES.length);
    const curatedSource = validation.assets.find(asset => asset.id === 'validation_timber_sanctuary_church_glazed_gable')!;
    const curatedChoice = CANONICAL_CHOICES.find(item => item.placements[0]?.id === curatedSource.id)!;
    expect(curatedChoice.option.photoUrl).toBe(curatedSource.thumbnail);
    expect(curatedChoice.placements[0].model).toEqual(curatedSource.model);
    expect(CANONICAL_CHOICES.filter(item => item.option.id === 'timber_sanctuary_church'
      && item.placements[0]?.model.variantId === 'timber_sanctuary_church_glazed_gable')).toHaveLength(1);
  });

  it.each([false, true])('browses, places and reopens an exact published model with DEV=%s', async development => {
    vi.stubEnv('DEV', development);
    const { browseAssets, validateRegistry } = await import('./assetRegistry');
    const { assetForZone, placeAsset, placementPlanRequest, placementProperties } = await import('./catalogue');
    const matches = browseAssets('Published fixture hall', 'civic');
    expect(matches.map(asset => asset.id)).toEqual(['generated_published_fixture']);
    const asset = placeAsset('generated_published_fixture');
    expect(asset.model).toEqual({
      variantId: 'generated_published_fixture_variant',
      revision: 'published-fixture-v003', method: 'RLASM 6.1',
    });
    expect(validateRegistry([asset])).toEqual([]);
    expect(placementPlanRequest(asset, 20, 24)).toMatchObject({
      archetype_id: 'generated_published_fixture_variant', target_floors: 3,
      allow_forced_fit: false, native_home_plot: false,
    });
    const saved = JSON.parse(JSON.stringify({ properties: placementProperties(asset) }));
    expect(saved.properties).toMatchObject({
      pick_place_asset: 'generated_published_fixture',
      development_selected_variant_id: 'generated_published_fixture_variant',
      pick_place_model_revision: 'published-fixture-v003',
    });
    expect(assetForZone(saved)).toBe(asset);
  });

  it.each([false, true])('exposes a new local pilot only in development with DEV=%s', async development => {
    vi.stubEnv('DEV', development);
    const { CATALOGUE_ASSETS, browseAssets } = await import('./assetRegistry');
    const { placeAsset } = await import('./catalogue');
    expect(CATALOGUE_ASSETS.some(asset => asset.id === 'generated_local_fixture')).toBe(development);
    expect(browseAssets('Local fixture hall').some(asset => asset.id === 'generated_local_fixture')).toBe(development);
    if (development) {
      expect(placeAsset('generated_local_fixture').model.revision).toBe('local-fixture-v002');
    } else {
      expect(() => placeAsset('generated_local_fixture')).toThrow('Unknown placeable asset');
    }
  });

  it.each([false, true])('preserves curated bindings and unique IDs with DEV=%s', async development => {
    vi.stubEnv('DEV', development);
    const { CATALOGUE_ASSETS, browseAssets, validateRegistry } = await import('./assetRegistry');
    const { placeAsset } = await import('./catalogue');
    for (const source of [...validation.assets, ...expansion.assets].filter(asset =>
      ['validation_timber_sanctuary_church_glazed_gable', 'clay_side_by_side_duplex'].includes(asset.id))) {
      expect(placeAsset(source.id)).toMatchObject({
        model: source.model, readiness: source.readiness, properties: source.properties,
      });
      expect(browseAssets().some(asset => asset.id === source.id)).toBe(true);
    }
    expect(placeAsset('infill_home').model.variantId).toBe('infill_flat_roof_minimal');
    expect(CATALOGUE_ASSETS.some(asset => asset.id === 'infill_home')).toBe(false);
    expect(new Set(CATALOGUE_ASSETS.map(asset => asset.id)).size).toBe(CATALOGUE_ASSETS.length);
    expect(validateRegistry(CATALOGUE_ASSETS)).toEqual([]);
  });
});
