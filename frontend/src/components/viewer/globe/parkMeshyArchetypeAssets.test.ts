import { describe, expect, it } from 'vitest';

import { PARK_MESHY_ARCHETYPE_ASSETS, parkMeshyAssetsForSelection } from './parkMeshyArchetypeAssets';

describe('PARK_MESHY_ARCHETYPE_ASSETS', () => {
  it('contains only reviewed metric park props without people or buildings', () => {
    const assets = Object.values(PARK_MESHY_ARCHETYPE_ASSETS);
    expect(assets).toHaveLength(12);
    expect(new Set(assets.map(({ id }) => id)).size).toBe(12);
    expect(assets.every(({ url }) => url.startsWith('/park-kits/') && url.endsWith('.glb'))).toBe(true);
    expect(assets.every(({ people, largeBuildings }) => !people && !largeBuildings)).toBe(true);
    expect(assets.every(({ dimensionsM }) => dimensionsM.every((value) => value > 0))).toBe(true);
  });

  it('routes variant-specific Meshy detail without treating it as generic kit furniture', () => {
    expect(parkMeshyAssetsForSelection('mini_golf_course', 'mini_golf_course_v3')
      .map(({ id }) => id)).toContain('mini-golf-sculptural-rock-obstacle-v1');
    expect(parkMeshyAssetsForSelection('memorial_garden', 'memorial_garden_v0')).toHaveLength(0);
    expect(parkMeshyAssetsForSelection('memorial_garden', 'memorial_garden_v1')
      .map(({ id }) => id)).toEqual(['memorial-woodland-bench-v1']);
  });
});
