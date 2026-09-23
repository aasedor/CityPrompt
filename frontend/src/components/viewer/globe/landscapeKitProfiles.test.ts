import { describe, expect, it } from 'vitest';

import {
  LANDSCAPE_TREE_PROFILES,
  LANDSCAPE_TREE_VARIANTS,
  resolveLandscapeTreeHeightM,
  selectLandscapeTreeVariant,
} from './landscapeKitProfiles';

describe('landscape tree kit profiles', () => {
  it('provides core species plus archetype-owned crown silhouettes', () => {
    expect(LANDSCAPE_TREE_VARIANTS).toHaveLength(7);
    expect(new Set(LANDSCAPE_TREE_VARIANTS.map((id) => LANDSCAPE_TREE_PROFILES[id].textureUrl)).size).toBe(3);
    expect(LANDSCAPE_TREE_PROFILES.maple.crownWidthM).toBeGreaterThan(
      LANDSCAPE_TREE_PROFILES.ornamental_pear.crownWidthM,
    );
    expect(LANDSCAPE_TREE_PROFILES.ornamental_pear.crownHeightM).toBeGreaterThan(
      LANDSCAPE_TREE_PROFILES.maple.crownHeightM,
    );
    expect(LANDSCAPE_TREE_PROFILES.mature_oak.crownWidthM).toBeGreaterThan(
      LANDSCAPE_TREE_PROFILES.maple.crownWidthM,
    );
  });

  it('selects a stable species from placement geometry', () => {
    const tree = { x: 12.34, y: -4.56, yawRad: 1.2 };
    expect(selectLandscapeTreeVariant(tree, 2)).toBe(selectLandscapeTreeVariant(tree, 2));
  });

  it.each([
    ['columnar_deciduous', 'columnar_hornbeam'],
    ['pollarded_deciduous', 'pollarded_plane'],
    ['tropical_palm', 'tropical_palm'],
  ] as const)('locks %s silhouettes to the intended family', (canopyClass, expected) => {
    expect(selectLandscapeTreeVariant({ x: 0, y: 0, yawRad: 0, canopyClass }, 0)).toBe(expected);
  });

  it('keeps mature street-tree rows in broad-canopy deciduous families', () => {
    for (let index = 0; index < 24; index += 1) {
      expect(selectLandscapeTreeVariant({
        x: index * 3.7,
        y: -index * 1.9,
        yawRad: index * 0.21,
        canopyClass: 'mature_deciduous',
      }, index)).not.toBe('ornamental_pear');
    }
  });

  it('gives palms a tall slender trunk and a dedicated radial-frond crown', () => {
    const palm = LANDSCAPE_TREE_PROFILES.tropical_palm;
    const deciduous = LANDSCAPE_TREE_PROFILES.honey_locust;
    expect(palm.crownGeometry).toBe('radial_palm_fronds');
    expect(deciduous.crownGeometry).toBe('branching_leaf_cluster');
    expect(palm.trunkHeightM).toBeGreaterThan(deciduous.trunkHeightM * 1.7);
    expect(palm.trunkRadiusM / palm.trunkHeightM)
      .toBeLessThan(deciduous.trunkRadiusM / deciduous.trunkHeightM);
    expect(palm.crownHeightM / palm.crownWidthM).toBeLessThan(0.35);
  });

  it('produces realistic mature urban-tree heights across the approved scale range', () => {
    for (const variant of LANDSCAPE_TREE_VARIANTS) {
      expect(resolveLandscapeTreeHeightM(variant, 0.8)).toBeGreaterThan(6.8);
      expect(resolveLandscapeTreeHeightM(variant, 1.2)).toBeLessThan(11.5);
    }
  });
});
