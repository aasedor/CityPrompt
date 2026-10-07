import type { CatalogueAsset } from './assetRegistry';

/** Reviewed exact-model browsing groups. Never a parcel permission or geometry preset. */
const REVIEWED_VARIANT_GROUPS: Record<string, string> = {
  clapboard_north_end: 'detached',
  glass_tower_blue_reflective: 'towers',
  art_deco_cream_terracotta: 'towers',
  art_deco_streamline_moderne: 'apartments',
  market_historic_iron_glass: 'shops',
  brewery_crystal_brewhouse: 'shops',
  deco_theater_movie_palace: 'civic',
  student_pickleball_garden_v1: 'play_sport',
  student_tennis_garden_v2: 'play_sport',
  student_bocce_garden_v2: 'play_sport',
  student_urban_splash_plaza_v1: 'play_sport',
  student_sheltered_dog_park_v1: 'play_sport',
  inclusive_accessible_playground_v0: 'play_sport',
  student_neighbourhood_orchard_v1: 'neighbourhood',
  amphitheater_lawn_v0: 'neighbourhood',
  wetland_rain_garden_v0: 'linear',
  student_woodland_stream_garden_v1: 'linear',
  linear_park_greenway_v0: 'linear',
  student_reflecting_fountain_garden_v1: 'plazas',
  student_terraced_cafe_court_v1: 'plazas',
  student_garden_square_v1: 'plazas',
  student_quiet_residential_street_v1: 'local',
  student_school_street_v1: 'local',
  student_green_alley_v1: 'alley',
  student_london_cobbled_mews_v1: 'alley',
  student_cherry_blossom_street_v1: 'local',
  student_market_street_v1: 'active',
  student_planted_shared_lane_v1: 'active',
  museum_earth_sheltered: 'civic',
  machiya_cafe_gallery: 'shops',
  cast_iron_italianate: 'apartments',
  rndsqr_midrise_terraced_garden: 'apartments',
  rec_centre_timber_hall: 'civic',
  beltline_brick_modern: 'mixed',
  basketball_court_v1: 'play_sport',
  brt_bus_rapid_transit_corridor_v0: 'transit',
  landmark_signature_bridge_v2: 'street_other',
};

export function reviewedAssetClassification(asset: CatalogueAsset): CatalogueAsset {
  const storeys = asset.kind === 'object' ? asset.storeyProgram?.nativeStoreys ?? Number(asset.properties.floors ?? 0) : 0;
  const groupId = REVIEWED_VARIANT_GROUPS[asset.model.variantId]
    ?? (asset.kind === 'object' && asset.zoneType === 'building' && storeys >= 12 ? 'towers' : undefined);
  return groupId ? { ...asset, calgaryGuide: { ...asset.calgaryGuide, groupId } } : asset;
}
