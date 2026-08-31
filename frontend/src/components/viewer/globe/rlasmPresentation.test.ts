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

  it('preserves the existing globe profile for other generation engines', () => {
    const buildings = [{
      generation_engine: 'meshy',
      lod_urls: { '0': '/files/example.glb' },
    }];

    expect(hasPlacedRlasmModel(buildings)).toBe(false);
    expect(getArchitecturalLightingProfile(buildings)).toEqual(DEFAULT_GLOBE_LIGHTING);
  });
});
