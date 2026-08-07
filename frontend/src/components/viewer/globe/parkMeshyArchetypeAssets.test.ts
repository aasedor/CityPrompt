import { describe, expect, it } from 'vitest';

import { PARK_MESHY_ARCHETYPE_ASSETS, parkMeshyAssetsForSelection } from './parkMeshyArchetypeAssets';
import { PARK_MESHY_ARCHETYPE_ASSETS_V3 } from './parkMeshyArchetypeAssetsV3';

describe('PARK_MESHY_ARCHETYPE_ASSETS', () => {
  it('contains only reviewed metric park props without people or buildings', () => {
    const assets = Object.values(PARK_MESHY_ARCHETYPE_ASSETS);
    expect(assets).toHaveLength(23 + Object.keys(PARK_MESHY_ARCHETYPE_ASSETS_V3).length);
    expect(new Set(assets.map(({ id }) => id)).size).toBe(assets.length);
    expect(assets.every(({ url }) => url.startsWith('/park-kits/') && url.endsWith('.glb'))).toBe(true);
    expect(assets.every(({ people, largeBuildings }) => !people && !largeBuildings)).toBe(true);
    expect(assets.every(({ dimensionsM }) => dimensionsM.every((value) => value > 0))).toBe(true);
  });

  it('routes variant-specific Meshy detail without treating it as generic kit furniture', () => {
    expect(parkMeshyAssetsForSelection('mini_golf_course', 'mini_golf_course_v3')
      .map(({ id }) => id)).toContain('mini-golf-sculptural-rock-obstacle-v1');
    expect(parkMeshyAssetsForSelection('memorial_garden', 'memorial_garden_v0')
      .map(({ id }) => id)).toEqual(['memorial-garden-stone-sundial-v1']);
    expect(parkMeshyAssetsForSelection('memorial_garden', 'memorial_garden_v1')
      .map(({ id }) => id)).toEqual([
        'memorial-woodland-bench-v1',
        'memorial-garden-woodland-remembrance-marker-v1',
      ]);
    expect(parkMeshyAssetsForSelection('japanese_garden', 'japanese_garden_v2')
      .map(({ id }) => id)).toEqual(['japanese-garden-concrete-corten-sculpture-v1']);
    expect(parkMeshyAssetsForSelection('nature_play_area', 'nature_play_area_v2')
      .map(({ id }) => id)).toEqual(['nature-play-timber-water-table-v1']);
    expect(parkMeshyAssetsForSelection('mini_golf_course', 'mini_golf_course_v3')
      .map(({ id }) => id)).toEqual([
        'mini-golf-sculptural-rock-obstacle-v1',
        'mini-golf-hollow-log-tunnel-v1',
        'mini-golf-stump-gate-obstacle-v1',
      ]);
    expect(parkMeshyAssetsForSelection('constructed_wetland_eco_park', 'constructed_wetland_eco_park_variant_2')
      .map(({ id }) => id)).toEqual([
        'wetland-timber-bird-blind-v1',
        'constructed-wetland-eco-park-wildlife-nesting-raft-v1',
      ]);
    expect(parkMeshyAssetsForSelection('urban_pocket_park', 'urban_pocket_park_v2')
      .map(({ id }) => id)).toEqual(['urban-pocket-park-terracotta-planter-ensemble-v1']);
    expect(parkMeshyAssetsForSelection('botanical_garden', 'botanical_garden_v1')).toHaveLength(0);
    expect(parkMeshyAssetsForSelection('community_garden_enhanced', 'garden_healing')
      .map(({ id }) => id)).toEqual(['community-garden-enhanced-communal-harvest-table-v1']);
    expect(parkMeshyAssetsForSelection('halifax_public_gardens', 'halifax_public_gardens_v1')
      .map(({ id }) => id)).toEqual(['halifax-public-gardens-victorian-park-bench-v1']);
  });
});
