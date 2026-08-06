export interface Batch6ParkSkinDefinition {
  archetypeId: string;
  variantId: string;
  slug: string;
  roles: readonly ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'];
  people: false;
  largeBuildings: false;
}

const ROLES = ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'] as const;

const skin = (
  archetypeId: string,
  variantId: string,
  slug: string,
): Batch6ParkSkinDefinition => Object.freeze({
  archetypeId,
  variantId,
  slug,
  roles: ROLES,
  people: false,
  largeBuildings: false,
});

/** Batch 6 remains exact-selection only. Material statistics come from the
 * selected catalogue image, while procedural structure makes each map
 * stationary and tileable. Source pixels are never projected onto geometry. */
export const BATCH6_PARK_SKINS = Object.freeze([
  skin('outdoor_ice_rink', 'outdoor_ice_rink_v3', 'outdoor-ice-rink-multipurpose'),
  skin('kayak_launch_dock', 'kayak_launch_dock_v0', 'kayak-river-launch'),
  skin('tidal_marsh_boardwalk', 'tidal_marsh_boardwalk_v0', 'tidal-marsh-cordgrass'),
  skin('outdoor_cinema_lawn', 'outdoor_cinema_lawn_v1', 'outdoor-cinema-park-lawn'),
  skin('food_truck_plaza', 'food_truck_plaza_v1', 'food-truck-permanent-park'),
  skin('festival_event_lawn', 'festival_event_lawn_v2', 'festival-great-lawn'),
  skin('campus_central_quad', 'campus_central_quad_variant_0', 'campus-naturalized-meadow-quad'),
  skin('urban_beach', 'urban_beach_v2', 'urban-beach-family-splash'),
  skin('velodrome_cycling_track', 'velodrome_cycling_track_variant_0', 'velodrome-open-air'),
  skin('mountain_bike_park', 'mountain_bike_park_variant_2', 'mountain-bike-skills-dirt'),
]);

export function batch6ParkSkinForSelection(
  archetypeId: string,
  variantId: string,
): Batch6ParkSkinDefinition | null {
  return BATCH6_PARK_SKINS.find((candidate) => (
    candidate.archetypeId === archetypeId && candidate.variantId === variantId
  )) ?? null;
}

export function batch6ParkSkinRoot(definition: Batch6ParkSkinDefinition): string {
  return `/park-skins/${definition.slug}/adaptive-v1`;
}
