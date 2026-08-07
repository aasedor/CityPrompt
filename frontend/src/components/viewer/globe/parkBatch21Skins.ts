export interface Batch21ParkSkinDefinition {
  archetypeId: string;
  variantId: string;
  slug: string;
  roles: readonly ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'];
  people: false;
  largeBuildings: false;
}

const ROLES = ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'] as const;
const skin = (archetypeId: string, variantId: string, slug: string): Batch21ParkSkinDefinition => Object.freeze({
  archetypeId, variantId, slug, roles: ROLES, people: false as const, largeBuildings: false as const,
});

/** Exact reference-derived packs for regulation athletics, productive gardens,
 * water rooms, event/civic spaces, greenways, boardwalks and roof landscapes. */
export const BATCH21_PARK_SKINS = Object.freeze([
  skin('athletics_precinct_sports_fields', 'athletics_precinct_sports_fields_variant_1', 'athletics-university-grandstand-v1'),
  skin('athletics_precinct_sports_fields', 'athletics_precinct_sports_fields_variant_2', 'athletics-campus-precinct-v2'),
  skin('athletics_precinct_sports_fields', 'athletics_precinct_sports_fields_variant_3', 'athletics-open-oval-pavilion-v3'),
  skin('community_garden', 'community_garden_v1', 'community-garden-modern-steel-turf-v1'),
  skin('community_garden', 'community_garden_v2', 'community-garden-natural-meadow-v2'),
  skin('community_garden', 'community_garden_v3', 'community-garden-urban-contemporary-v3'),
  skin('fountain_water_feature', 'fountain_water_feature_v0', 'fountain-naturalistic-pond-v0'),
  skin('fountain_water_feature', 'fountain_water_feature_v2', 'fountain-contemporary-interactive-v2'),
  skin('fountain_water_feature', 'fountain_water_feature_v3', 'fountain-ecological-wetland-v3'),
  skin('pond_lake', 'pond_lake_v1', 'pond-formal-reflecting-v1'),
  skin('pond_lake', 'pond_lake_v2', 'pond-contemporary-interactive-v2'),
  skin('pond_lake', 'pond_lake_v3', 'pond-ecological-wetland-v3'),
  skin('market_square', 'market_square_v0', 'market-terraced-performance-v0'),
  skin('market_square', 'market_square_v2', 'market-intimate-garden-venue-v2'),
  skin('market_square', 'market_square_v3', 'market-industrial-adaptive-v3'),
  skin('formal_civic_plaza', 'formal_civic_plaza_v1', 'formal-civic-contemporary-urban-v1'),
  skin('formal_civic_plaza', 'formal_civic_plaza_v2', 'formal-civic-green-v2'),
  skin('formal_civic_plaza', 'formal_civic_plaza_v3', 'formal-civic-festival-market-v3'),
  skin('linear_park_greenway', 'linear_park_greenway_v1', 'linear-greenway-riverfront-v1'),
  skin('linear_park_greenway', 'linear_park_greenway_v2', 'linear-greenway-daylighted-creek-v2'),
  skin('linear_park_greenway', 'linear_park_greenway_v3', 'linear-greenway-elevated-viaduct-v3'),
  skin('promenade_boardwalk', 'promenade_boardwalk_v1', 'promenade-modern-esplanade-v1'),
  skin('promenade_boardwalk', 'promenade_boardwalk_v2', 'promenade-tropical-resort-v2'),
  skin('promenade_boardwalk', 'promenade_boardwalk_v3', 'promenade-naturalized-riparian-v3'),
  skin('swimming_pool_complex', 'swimming_pool_complex_v1', 'swimming-formal-reflecting-v1'),
  skin('swimming_pool_complex', 'swimming_pool_complex_v2', 'swimming-contemporary-interactive-v2'),
  skin('swimming_pool_complex', 'swimming_pool_complex_v3', 'swimming-ecological-wetland-v3'),
  skin('rooftop_garden', 'rooftop_garden_v1', 'rooftop-sedum-green-roof-v1'),
  skin('rooftop_garden', 'rooftop_garden_v2', 'rooftop-urban-farm-v2'),
  skin('rooftop_garden', 'rooftop_garden_v3', 'rooftop-social-terrace-v3'),
]);

export const batch21ParkSkinForSelection = (archetypeId: string, variantId: string): Batch21ParkSkinDefinition | null => (
  BATCH21_PARK_SKINS.find((candidate) => candidate.archetypeId === archetypeId && candidate.variantId === variantId) ?? null
);
