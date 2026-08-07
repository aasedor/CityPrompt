export interface Batch19ParkSkinDefinition {
  archetypeId: string;
  variantId: string;
  slug: string;
  roles: readonly ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'];
  people: false;
  largeBuildings: false;
}

const ROLES = ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'] as const;
const skin = (archetypeId: string, variantId: string, slug: string): Batch19ParkSkinDefinition => Object.freeze({
  archetypeId, variantId, slug, roles: ROLES, people: false as const, largeBuildings: false as const,
});

export const BATCH19_PARK_SKINS = Object.freeze([
  skin('outdoor_ice_rink', 'outdoor_ice_rink_v0', 'ice-rink-holiday-market-v0'),
  skin('outdoor_ice_rink', 'outdoor_ice_rink_v1', 'ice-rink-urban-plaza-v1'),
  skin('outdoor_ice_rink', 'outdoor_ice_rink_v2', 'ice-rink-nature-trail-v2'),
  skin('kayak_launch_dock', 'kayak_launch_dock_v1', 'kayak-urban-harbour-v1'),
  skin('kayak_launch_dock', 'kayak_launch_dock_v2', 'kayak-lake-beach-v2'),
  skin('kayak_launch_dock', 'kayak_launch_dock_v3', 'kayak-community-boathouse-v3'),
  skin('tidal_marsh_boardwalk', 'tidal_marsh_boardwalk_v1', 'tidal-marsh-mangrove-v1'),
  skin('tidal_marsh_boardwalk', 'tidal_marsh_boardwalk_v2', 'tidal-marsh-reedbed-v2'),
  skin('tidal_marsh_boardwalk', 'tidal_marsh_boardwalk_v3', 'tidal-marsh-bird-blind-v3'),
  skin('outdoor_cinema_lawn', 'outdoor_cinema_lawn_v0', 'cinema-pop-up-festival-v0'),
  skin('outdoor_cinema_lawn', 'outdoor_cinema_lawn_v2', 'cinema-drive-in-heritage-v2'),
  skin('outdoor_cinema_lawn', 'outdoor_cinema_lawn_v3', 'cinema-rooftop-terrace-v3'),
  skin('food_truck_plaza', 'food_truck_plaza_v0', 'food-truck-industrial-pop-up-v0'),
  skin('food_truck_plaza', 'food_truck_plaza_v2', 'food-truck-adaptive-lot-v2'),
  skin('food_truck_plaza', 'food_truck_plaza_v3', 'food-truck-night-market-v3'),
  skin('festival_event_lawn', 'festival_event_lawn_v0', 'festival-concert-lawn-v0'),
  skin('festival_event_lawn', 'festival_event_lawn_v1', 'festival-farmers-market-v1'),
  skin('festival_event_lawn', 'festival_event_lawn_v3', 'festival-winter-market-v3'),
  skin('campus_central_quad', 'campus_central_quad_variant_1', 'campus-modern-plaza-v1'),
  skin('campus_central_quad', 'campus_central_quad_variant_2', 'campus-garden-pavilion-v2'),
  skin('campus_central_quad', 'campus_central_quad_variant_3', 'campus-formal-collegiate-v3'),
  skin('urban_beach', 'urban_beach_v0', 'urban-beach-paris-plages-v0'),
  skin('urban_beach', 'urban_beach_v1', 'urban-beach-riverfront-bar-v1'),
  skin('urban_beach', 'urban_beach_v3', 'urban-beach-sand-garden-v3'),
  skin('velodrome_cycling_track', 'velodrome_cycling_track_variant_1', 'velodrome-indoor-arena-v1'),
  skin('velodrome_cycling_track', 'velodrome_cycling_track_variant_2', 'velodrome-parkland-v2'),
  skin('velodrome_cycling_track', 'velodrome_cycling_track_variant_3', 'velodrome-community-training-v3'),
  skin('mountain_bike_park', 'mountain_bike_park_variant_0', 'mountain-bike-paved-pump-v0'),
  skin('mountain_bike_park', 'mountain_bike_park_variant_1', 'mountain-bike-hillside-v1'),
  skin('mountain_bike_park', 'mountain_bike_park_variant_3', 'mountain-bike-urban-dirt-v3'),
]);

export const batch19ParkSkinForSelection = (archetypeId: string, variantId: string): Batch19ParkSkinDefinition | null => (
  BATCH19_PARK_SKINS.find((candidate) => candidate.archetypeId === archetypeId && candidate.variantId === variantId) ?? null
);
