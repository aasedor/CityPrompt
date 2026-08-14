import { describe, expect, it } from 'vitest';

import manifest from './neighborhoodParkV0StickerKit.json';

describe('neighborhood park v0 Sticker Method kit', () => {
  it('locks the exact reference and whole-object adaptation contract', () => {
    expect(manifest.reference.sha256)
      .toBe('38c1079127126017edb7945f77f47d73c4d0dde1fe5a566ac5dc0e791473d5c3');
    expect(manifest.method).toBe('sticker_method_site_adaptive_whole_program');
    expect(manifest.fixedProgramEnvelopeM).toEqual([50, 38]);
    expect(manifest.adaptation).toEqual({
      cropFixedObjectsAllowed: false,
      nonuniformObjectScalingAllowed: false,
      siteAdaptiveGround: true,
      wholeFixedKit: true,
    });
    expect(manifest.skin.roles).toEqual([
      'asphalt', 'lawn', 'metal', 'paver', 'planting', 'rope', 'safety', 'stone', 'timber',
    ]);
  });

  it('ships the five exact metric object families with complete ownership', () => {
    expect(Object.keys(manifest.assets).sort()).toEqual([
      'natural_boulder_group',
      'split_rail_fence',
      'timber_climbing_tower_with_slide',
      'timber_pavilion',
      'timber_swing_frame',
    ]);
    expect(manifest.surfaceOwnership.exactOne).toBe(true);
    expect(manifest.surfaceOwnership.fallbackAllowed).toBe(false);
    for (const asset of Object.values(manifest.assets)) {
      expect(asset.metricScale).toBe(1);
      expect(asset.nonuniformScalingAllowed).toBe(false);
      expect(asset.url).toMatch(/^\/park-kits\/neighborhood-park-rustic-v0\/.+\.glb$/);
      expect(asset.sha256).toMatch(/^[a-f0-9]{64}$/);
    }
  });

  it('places one pavilion, tower and swing plus a bounded fence and boulders', () => {
    const ids = manifest.placements.map(({ assetId }) => assetId);
    expect(ids.filter((id) => id === 'timber_pavilion')).toHaveLength(1);
    expect(ids.filter((id) => id === 'timber_climbing_tower_with_slide')).toHaveLength(1);
    expect(ids.filter((id) => id === 'timber_swing_frame')).toHaveLength(1);
    expect(ids.filter((id) => id === 'split_rail_fence')).toHaveLength(17);
    expect(ids.filter((id) => id === 'natural_boulder_group')).toHaveLength(3);
    expect(manifest.groundPatches.map(({ role }) => role).sort())
      .toEqual(['asphalt', 'paver', 'safety']);
  });
});
