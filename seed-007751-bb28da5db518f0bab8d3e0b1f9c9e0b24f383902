import { describe, expect, it } from 'vitest';

import {
  LANDSCAPE_TREE_PROFILES,
  LANDSCAPE_TREE_VARIANTS,
  resolveLandscapeTreeHeightM,
  selectLandscapeTreeVariant,
} from './landscapeKitProfiles';

describe('landscape tree kit profiles', () => {
  it('provides three visibly different metric crown families', () => {
    expect(LANDSCAPE_TREE_VARIANTS).toHaveLength(3);
    expect(new Set(LANDSCAPE_TREE_VARIANTS.map((id) => LANDSCAPE_TREE_PROFILES[id].textureUrl)).size).toBe(3);
    expect(LANDSCAPE_TREE_PROFILES.maple.crownWidthM).toBeGreaterThan(
      LANDSCAPE_TREE_PROFILES.ornamental_pear.crownWidthM,
    );
    expect(LANDSCAPE_TREE_PROFILES.ornamental_pear.crownHeightM).toBeGreaterThan(
      LANDSCAPE_TREE_PROFILES.maple.crownHeightM,
    );
  });

  it('selects a stable species from placement geometry', () => {
    const tree = { x: 12.34, y: -4.56, yawRad: 1.2 };
    expect(selectLandscapeTreeVariant(tree, 2)).toBe(selectLandscapeTreeVariant(tree, 2));
  });

  it('produces realistic mature urban-tree heights across the approved scale range', () => {
    for (const variant of LANDSCAPE_TREE_VARIANTS) {
      expect(resolveLandscapeTreeHeightM(variant, 0.8)).toBeGreaterThan(6.8);
      expect(resolveLandscapeTreeHeightM(variant, 1.2)).toBeLessThan(11.5);
    }
  });
});
