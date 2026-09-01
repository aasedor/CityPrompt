import { describe, expect, it } from 'vitest';
import type { Building } from '@/types';
import type { LegoAssemblyRecipe } from './legoAssemblyApi';
import {
  extractLegoAssemblyRecipe,
  isArchitecturalClayRecipe,
  resolveBuildingModelSource,
} from './buildingModelSource';

const CLAY_FAMILY = 'calgary-inner-city-bungalow-semantic-clay-v022';

function recipe(
  variantKey: 'native' | 'wide_2' | 'wide_4',
  widthM: number,
): LegoAssemblyRecipe {
  return {
    schema_version: 1,
    module_family: CLAY_FAMILY,
    archetype_id: 'calgary_inner_city_bungalow',
    reuse_keys: ['rlasm', 'semantic-clay'],
    target: { width_m: widthM, depth_m: 13.6, floors: 2 },
    instances: [{
      asset_id: `clay-${variantKey}`,
      asset_name: `Architectural Clay ${variantKey}`,
      model_url: `/files/bungalow-${variantKey}-clay.glb`,
      family: CLAY_FAMILY,
      role: 'assembled',
      variant_key: variantKey,
      level: 0,
      position: [0, 0, 0],
      rotation_degrees: 0,
      scale: [1, 1, 1],
      native_dimensions_m: [widthM, 13.6, 7.41],
    }],
    assembled_height_m: 7.41,
    fit: {
      scale_x: 1,
      scale_y: 1,
      score: 1,
      assembly_mode: 'semantic_horizontal_bays',
      selected_variant_key: variantKey,
    },
  };
}

function building(
  legoAssembly: unknown,
  overrides: Partial<Building> = {},
): Building {
  return {
    id: 'building-1',
    project_id: 'project-1',
    created_at: '2026-09-01T00:00:00Z',
    model_url: '/files/historical-full-rlasm.glb',
    specifications: { legoAssembly },
    ...overrides,
  };
}

describe('architectural-clay building model source', () => {
  it.each([
    ['native', 11.8],
    ['wide_2', 16.6],
    ['wide_4', 21.4],
  ] as const)(
    'selects the %s clay assembly at native scale before the historical full model',
    (variantKey, widthM) => {
      const clayRecipe = recipe(variantKey, widthM);
      const source = resolveBuildingModelSource(building(clayRecipe));

      expect(source).toMatchObject({
        kind: 'lego_assembly',
        presentation: 'architectural_clay',
        variantKey,
        downloadUrl: `/files/bungalow-${variantKey}-clay.glb`,
      });
      expect(source?.kind === 'lego_assembly' && source.recipe).toEqual(clayRecipe);
      expect(source?.kind === 'lego_assembly' && source.recipe.instances[0]?.scale)
        .toEqual([1, 1, 1]);
    },
  );

  it('can preview a valid saved assembly without a geospatial footprint', () => {
    const clayRecipe = recipe('native', 11.8);
    const record = building(clayRecipe, { footprint_coordinates: undefined });

    expect(extractLegoAssemblyRecipe(record)).toEqual(clayRecipe);
    expect(isArchitecturalClayRecipe(clayRecipe)).toBe(true);
    expect(resolveBuildingModelSource(record)?.kind).toBe('lego_assembly');
  });

  it('falls back to the monolithic model when the saved assembly is malformed', () => {
    const malformed = {
      ...recipe('native', 11.8),
      instances: [],
    };

    expect(resolveBuildingModelSource(building(malformed))).toEqual({
      kind: 'legacy_model',
      modelUrl: '/files/historical-full-rlasm.glb',
      presentation: 'model',
      variantKey: null,
      downloadUrl: '/files/historical-full-rlasm.glb',
    });
  });

  it('omits a misleading single-file download for a multi-GLB assembly', () => {
    const multi = recipe('native', 11.8);
    multi.instances.push({
      ...multi.instances[0],
      asset_id: 'clay-roof',
      model_url: '/files/bungalow-roof-clay.glb',
      role: 'roof',
    });

    expect(resolveBuildingModelSource(building(multi))).toMatchObject({
      kind: 'lego_assembly',
      downloadUrl: null,
    });
  });
});
