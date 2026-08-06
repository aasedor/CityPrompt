export interface Batch16ParkSkinDefinition {
  archetypeId: string;
  variantId: string;
  slug: string;
  roles: readonly ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'];
  people: false;
  largeBuildings: false;
}

const ROLES = ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'] as const;
const skin = (archetypeId: string, variantId: string, slug: string): Batch16ParkSkinDefinition => Object.freeze({
  archetypeId, variantId, slug, roles: ROLES, people: false as const, largeBuildings: false as const,
});

export const BATCH16_PARK_SKINS = Object.freeze([
  skin('community_park', 'community_park_v1', 'community-park-modern-minimalist-v1'),
  skin('community_park', 'community_park_v2', 'community-park-mediterranean-xeriscape-v2'),
  skin('community_park', 'community_park_v3', 'community-park-tropical-lush-v3'),
  skin('regional_park', 'regional_park_v1', 'regional-park-modern-minimalist-v1'),
  skin('regional_park', 'regional_park_v2', 'regional-park-mediterranean-xeriscape-v2'),
  skin('regional_park', 'regional_park_v3', 'regional-park-tropical-lush-v3'),
  skin('dog_park', 'dog_park_v1', 'dog-park-modern-steel-turf-v1'),
  skin('dog_park', 'dog_park_v2', 'dog-park-natural-meadow-v2'),
  skin('dog_park', 'dog_park_v3', 'dog-park-urban-contemporary-v3'),
  skin('skate_park', 'skate_park_v1', 'skate-park-community-recreation-v1'),
  skin('skate_park', 'skate_park_v2', 'skate-park-naturalized-active-v2'),
  skin('skate_park', 'skate_park_v3', 'skate-park-urban-athletic-v3'),
  skin('sports_field_complex', 'sports_field_complex_v1', 'sports-field-complex-community-recreation-v1'),
  skin('sports_field_complex', 'sports_field_complex_v2', 'sports-field-complex-naturalized-active-v2'),
  skin('sports_field_complex', 'sports_field_complex_v3', 'sports-field-complex-urban-athletic-v3'),
  skin('tennis_court_cluster', 'tennis_court_cluster_v1', 'tennis-court-cluster-community-recreation-v1'),
  skin('tennis_court_cluster', 'tennis_court_cluster_v2', 'tennis-court-cluster-naturalized-active-v2'),
  skin('tennis_court_cluster', 'tennis_court_cluster_v3', 'tennis-court-cluster-urban-athletic-v3'),
  skin('botanical_garden', 'botanical_garden_v1', 'botanical-garden-woodland-naturalistic-v1'),
  skin('botanical_garden', 'botanical_garden_v2', 'botanical-garden-contemporary-sculptural-v2'),
  skin('japanese_garden', 'japanese_garden_v1', 'japanese-garden-woodland-naturalistic-v1'),
  skin('japanese_garden', 'japanese_garden_v2', 'japanese-garden-contemporary-sculptural-v2'),
  skin('japanese_garden', 'japanese_garden_v3', 'japanese-garden-cottage-romantic-v3'),
  skin('memorial_garden', 'memorial_garden_v1', 'memorial-garden-woodland-naturalistic-v1'),
  skin('memorial_garden', 'memorial_garden_v2', 'memorial-garden-contemporary-sculptural-v2'),
  skin('memorial_garden', 'memorial_garden_v3', 'memorial-garden-cottage-romantic-v3'),
  skin('urban_forest', 'urban_forest_v1', 'urban-forest-bioengineered-infrastructure-v1'),
  skin('urban_forest', 'urban_forest_v2', 'urban-forest-rewilded-urban-v2'),
  skin('urban_forest', 'urban_forest_v3', 'urban-forest-resilient-coastal-v3'),
]);

export const batch16ParkSkinForSelection = (archetypeId: string, variantId: string): Batch16ParkSkinDefinition | null => (
  BATCH16_PARK_SKINS.find((candidate) => candidate.archetypeId === archetypeId && candidate.variantId === variantId) ?? null
);
