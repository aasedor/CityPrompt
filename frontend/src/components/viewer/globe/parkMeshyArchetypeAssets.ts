export interface ParkMeshyArchetypeAsset {
  id: string;
  url: string;
  archetypeId: string;
  variantIds: readonly string[];
  dimensionsM: readonly [number, number, number];
  placementRole: string;
  sourceKind: 'meshy_multiview_archetype_reference';
  people: false;
  largeBuildings: false;
}

const asset = (
  definition: Omit<ParkMeshyArchetypeAsset, 'sourceKind' | 'people' | 'largeBuildings'>,
): ParkMeshyArchetypeAsset => Object.freeze({
  ...definition,
  variantIds: Object.freeze(definition.variantIds),
  dimensionsM: Object.freeze(definition.dimensionsM),
  sourceKind: 'meshy_multiview_archetype_reference',
  people: false,
  largeBuildings: false,
});

/** Runtime-approved Meshy props. Regulation dimensions, clearances, paths and
 * surfaces remain procedural LEGO geometry; only detail-rich props live here. */
export const PARK_MESHY_ARCHETYPE_ASSETS = Object.freeze({
  naturePlayGraniteBoulder: asset({
    id: 'nature-play-climbing-boulder-granite-v1',
    url: '/park-kits/nature-play-forest-adventure/nature-play-climbing-boulder-granite-v1.glb',
    archetypeId: 'nature_play_area', variantIds: ['nature_play_area_v0'],
    dimensionsM: [2.8, 2.2, 1.8], placementRole: 'natural_climbing_boulder',
  }),
  naturePlaySandstoneBoulder: asset({
    id: 'nature-play-climbing-boulder-sandstone-v1',
    url: '/park-kits/nature-play-forest-adventure/nature-play-climbing-boulder-sandstone-v1.glb',
    archetypeId: 'nature_play_area', variantIds: ['nature_play_area_v1', 'nature_play_area_v3'],
    dimensionsM: [2.6, 2.0, 1.6], placementRole: 'natural_climbing_boulder_warm',
  }),
  rewildingRootWad: asset({
    id: 'rewilding-root-wad-large-v1',
    url: '/park-kits/rewilding-ecological-restoration/rewilding-root-wad-large-v1.glb',
    archetypeId: 'rewilding_ecological_restoration_zone', variantIds: ['rewilding_ecological_restoration_zone_variant_3'],
    dimensionsM: [3.2, 2.8, 2.2], placementRole: 'riparian_root_wad',
  }),
  rewildingStandingSnag: asset({
    id: 'rewilding-standing-snag-v1',
    url: '/park-kits/rewilding-ecological-restoration/rewilding-standing-snag-v1.glb',
    archetypeId: 'rewilding_ecological_restoration_zone', variantIds: ['rewilding_ecological_restoration_zone_variant_0', 'rewilding_ecological_restoration_zone_variant_1'],
    dimensionsM: [1.2, 1.2, 5.5], placementRole: 'standing_habitat_snag',
  }),
  rewildingHollowSnag: asset({
    id: 'rewilding-standing-snag-hollow-v1',
    url: '/park-kits/rewilding-ecological-restoration/rewilding-standing-snag-hollow-v1.glb',
    archetypeId: 'rewilding_ecological_restoration_zone', variantIds: ['rewilding_ecological_restoration_zone_variant_2', 'rewilding_ecological_restoration_zone_variant_3'],
    dimensionsM: [1.4, 1.4, 6.0], placementRole: 'hollow_habitat_snag',
  }),
  rewildingBrushPile: asset({
    id: 'rewilding-brush-habitat-pile-v1',
    url: '/park-kits/rewilding-ecological-restoration/rewilding-brush-habitat-pile-v1.glb',
    archetypeId: 'rewilding_ecological_restoration_zone', variantIds: ['rewilding_ecological_restoration_zone_variant_0', 'rewilding_ecological_restoration_zone_variant_3'],
    dimensionsM: [4.0, 2.6, 1.6], placementRole: 'brush_habitat_pile',
  }),
  pollinatorInsectHotel: asset({
    id: 'pollinator-insect-hotel-timber-v1',
    url: '/park-kits/pollinator-meadow/pollinator-insect-hotel-timber-v1.glb',
    archetypeId: 'pollinator_meadow', variantIds: ['pollinator_meadow_v0', 'pollinator_meadow_v1', 'pollinator_meadow_v2', 'pollinator_meadow_v3'],
    dimensionsM: [1.4, 0.5, 2.0], placementRole: 'pollinator_insect_hotel',
  }),
  productiveGardenPottingBench: asset({
    id: 'productive-garden-rustic-potting-bench-v1',
    url: '/park-kits/urban-orchard-food-forest/productive-garden-rustic-potting-bench-v1.glb',
    archetypeId: 'urban_orchard_food_forest', variantIds: ['urban_orchard_food_forest_v0', 'urban_orchard_food_forest_v1', 'urban_orchard_food_forest_v2', 'urban_orchard_food_forest_v3'],
    dimensionsM: [2.2, 0.8, 1.3], placementRole: 'community_garden_potting_bench',
  }),
  memorialWoodlandBench: asset({
    id: 'memorial-woodland-bench-v1',
    url: '/park-kits/memorial-garden-woodland-naturalistic/memorial-woodland-bench-v1.glb',
    archetypeId: 'memorial_garden', variantIds: ['memorial_garden_v1'],
    dimensionsM: [2.4, 0.8, 1.0], placementRole: 'memorial_woodland_bench',
  }),
  miniGolfRockObstacle: asset({
    id: 'mini-golf-sculptural-rock-obstacle-v1',
    url: '/park-kits/mini-golf/mini-golf-sculptural-rock-obstacle-v1.glb',
    archetypeId: 'mini_golf_course', variantIds: ['mini_golf_course_v3'],
    dimensionsM: [3.0, 2.2, 2.0], placementRole: 'mini_golf_sculptural_rock_obstacle',
  }),
  sculptureCortenLoop: asset({
    id: 'sculpture-garden-corten-loop-v1',
    url: '/park-kits/sculpture-garden/sculpture-garden-corten-loop-v1.glb',
    archetypeId: 'sculpture_garden', variantIds: ['sculpture_garden_v0', 'sculpture_garden_v1', 'sculpture_garden_v2'],
    dimensionsM: [2.2, 1.6, 3.0], placementRole: 'sculpture_garden_corten_loop',
  }),
  sculptureStonePortal: asset({
    id: 'sculpture-garden-stone-portal-v1',
    url: '/park-kits/sculpture-garden/sculpture-garden-stone-portal-v1.glb',
    archetypeId: 'sculpture_garden', variantIds: ['sculpture_garden_v0', 'sculpture_garden_v1', 'sculpture_garden_v3'],
    dimensionsM: [2.6, 1.5, 3.2], placementRole: 'sculpture_garden_stone_portal',
  }),
});

export function parkMeshyAssetsForSelection(archetypeId: string, variantId: string) {
  return Object.values(PARK_MESHY_ARCHETYPE_ASSETS).filter((candidate) => (
    candidate.archetypeId === archetypeId && candidate.variantIds.includes(variantId)
  ));
}
