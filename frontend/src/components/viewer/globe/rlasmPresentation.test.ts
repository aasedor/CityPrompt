import { describe, expect, it } from 'vitest';

import {
  DEFAULT_GLOBE_LIGHTING,
  RLASM_ARCHITECTURAL_LIGHTING,
  getArchitecturalLightingProfile,
  hasPlacedRlasmModel,
} from './rlasmPresentation';

describe('RLASM architectural presentation', () => {
  it('uses the calibrated profile only for a placed RLASM model', () => {
    const buildings = [{
      generation_engine: 'RLASM',
      model_url: '/files/farnsworth-v004-cityprompt-v002.glb',
    }];

    expect(hasPlacedRlasmModel(buildings)).toBe(true);
    expect(getArchitecturalLightingProfile(buildings)).toEqual(RLASM_ARCHITECTURAL_LIGHTING);
  });

  it('does not switch profiles for an RLASM catalogue record without a model', () => {
    expect(hasPlacedRlasmModel([{ generation_engine: 'rlasm' }])).toBe(false);
    expect(getArchitecturalLightingProfile([{ generation_engine: 'rlasm' }]))
      .toEqual(DEFAULT_GLOBE_LIGHTING);
  });

  it('treats a valid architectural-clay assembly as the placed RLASM representation', () => {
    const buildings = [{
      generation_engine: 'rlasm',
      specifications: {
        legoAssembly: {
          schema_version: 1,
          module_family: 'calgary-inner-city-bungalow-semantic-clay-v022',
          archetype_id: 'calgary_inner_city_bungalow',
          reuse_keys: ['semantic-clay'],
          target: { width_m: 11.8, depth_m: 13.6, floors: 2 },
          instances: [{
            asset_id: 'clay-native',
            asset_name: 'Architectural Clay Native',
            model_url: '/files/bungalow-native-clay.glb',
            family: 'calgary-inner-city-bungalow-semantic-clay-v022',
            role: 'assembled',
            level: 0,
            position: [0, 0, 0],
            rotation_degrees: 0,
            scale: [1, 1, 1],
            native_dimensions_m: [11.8, 13.6, 7.41],
          }],
        },
      },
    }];

    expect(hasPlacedRlasmModel(buildings)).toBe(true);
    expect(getArchitecturalLightingProfile(buildings)).toEqual(RLASM_ARCHITECTURAL_LIGHTING);
  });

  it('preserves the existing globe profile for other generation engines', () => {
    const buildings = [{
      generation_engine: 'meshy',
      lod_urls: { '0': '/files/example.glb' },
    }];

    expect(hasPlacedRlasmModel(buildings)).toBe(false);
    expect(getArchitecturalLightingProfile(buildings)).toEqual(DEFAULT_GLOBE_LIGHTING);
  });
});
