export interface Batch26ParkSkinDefinition {
  archetypeId: string;
  variantId: string;
  slug: string;
  roles: readonly ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'];
  people: false;
  largeBuildings: false;
}

const ROLES = ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'] as const;
const skin = (archetypeId: string, variantId: string, slug: string): Batch26ParkSkinDefinition => Object.freeze({
  archetypeId, variantId, slug, roles: ROLES, people: false as const, largeBuildings: false as const,
});

/** Exact-reference material packs for the Batch 26 landscape and waterfront
 * closure families. Geometry remains parcel-adaptive and contains no people
 * or separately rendered large buildings. */
export const BATCH26_PARK_SKINS = Object.freeze([
  skin('greenbelt_buffer_park', 'greenbelt_buffer_park_v0', 'greenbelt-suburban-lawn-v0'),
  skin('greenbelt_buffer_park', 'greenbelt_buffer_park_v2', 'greenbelt-hedgerow-buffer-v2'),
  skin('greenbelt_buffer_park', 'greenbelt_buffer_park_v3', 'greenbelt-active-spine-v3'),
  skin('foothill_trail_park', 'foothill_trail_park_v0', 'foothill-sage-ridge-v0'),
  skin('foothill_trail_park', 'foothill_trail_park_v1', 'foothill-eucalyptus-ridge-v1'),
  skin('foothill_trail_park', 'foothill_trail_park_v3', 'foothill-alpine-larch-v3'),
  skin('concert_pavilion_lawn', 'concert_pavilion_lawn_v0', 'concert-forest-hills-v0'),
  skin('concert_pavilion_lawn', 'concert_pavilion_lawn_v1', 'concert-wave-canopy-v1'),
  skin('concert_pavilion_lawn', 'concert_pavilion_lawn_v3', 'concert-bowl-shell-v3'),
  skin('night_market', 'night_market_v1', 'night-market-christmas-v1'),
  skin('night_market', 'night_market_v2', 'night-market-latin-canopy-v2'),
  skin('night_market', 'night_market_v3', 'night-market-food-hall-v3'),
  skin('parade_ground', 'parade_ground_v0', 'parade-stadium-forecourt-v0'),
  skin('parade_ground', 'parade_ground_v1', 'parade-mall-allee-v1'),
  skin('parade_ground', 'parade_ground_v2', 'parade-champ-de-mars-v2'),
  skin('marina_yacht_harbor', 'marina_yacht_harbor_v0', 'marina-inland-lake-v0'),
  skin('marina_yacht_harbor', 'marina_yacht_harbor_v1', 'marina-fishing-harbour-v1'),
  skin('marina_yacht_harbor', 'marina_yacht_harbor_v3', 'marina-superyacht-v3'),
  skin('working_pier_wharf_conversion', 'working_pier_wharf_conversion_v0', 'working-pier-public-market-v0'),
  skin('working_pier_wharf_conversion', 'working_pier_wharf_conversion_v1', 'working-pier-retail-boardwalk-v1'),
  skin('working_pier_wharf_conversion', 'working_pier_wharf_conversion_v2', 'working-pier-industrial-overlay-v2'),
  skin('floating_park_pool', 'floating_park_pool_v0', 'floating-plus-pool-v0'),
  skin('floating_park_pool', 'floating_park_pool_v1', 'floating-harbour-bath-v1'),
  skin('floating_park_pool', 'floating_park_pool_v3', 'floating-little-island-v3'),
  skin('lighthouse_point_park', 'lighthouse_point_park_v0', 'lighthouse-cape-headland-v0'),
  skin('lighthouse_point_park', 'lighthouse_point_park_v1', 'lighthouse-atlantic-dune-v1'),
  skin('lighthouse_point_park', 'lighthouse_point_park_v3', 'lighthouse-fortress-v3'),
  skin('lake_edge_plaza', 'lake_edge_plaza_v0', 'lake-edge-como-terrace-v0'),
  skin('lake_edge_plaza', 'lake_edge_plaza_v1', 'lake-edge-geneva-esplanade-v1'),
  skin('lake_edge_plaza', 'lake_edge_plaza_v3', 'lake-edge-chicago-plaza-v3'),
]);

export const batch26ParkSkinForSelection = (archetypeId: string, variantId: string): Batch26ParkSkinDefinition | null => (
  BATCH26_PARK_SKINS.find((candidate) => candidate.archetypeId === archetypeId && candidate.variantId === variantId) ?? null
);
