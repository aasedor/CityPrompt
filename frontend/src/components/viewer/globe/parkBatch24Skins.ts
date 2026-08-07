export interface Batch24ParkSkinDefinition {
  archetypeId: string;
  variantId: string;
  slug: string;
  roles: readonly ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'];
  people: false;
  largeBuildings: false;
}

const ROLES = ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'] as const;
const skin = (archetypeId: string, variantId: string, slug: string): Batch24ParkSkinDefinition => Object.freeze({
  archetypeId, variantId, slug, roles: ROLES, people: false as const, largeBuildings: false as const,
});

/** Exact reference-derived packs for Calgary, Halifax, London, Montreal and
 * New York park families. People establish scale in the references but are
 * not generated; enclosing buildings remain separate LEGO families. */
export const BATCH24_PARK_SKINS = Object.freeze([
  skin('calgary_prairie_plaza', 'calgary_prairie_plaza_v0', 'calgary-prairie-winter-v0'),
  skin('calgary_prairie_plaza', 'calgary_prairie_plaza_v2', 'calgary-prairie-indigenous-art-v2'),
  skin('calgary_prairie_plaza', 'calgary_prairie_plaza_v3', 'calgary-prairie-corporate-green-v3'),
  skin('calgary_princes_island', 'calgary_princes_island_v1', 'calgary-princes-autumn-v1'),
  skin('calgary_princes_island', 'calgary_princes_island_v2', 'calgary-princes-winter-v2'),
  skin('calgary_princes_island', 'calgary_princes_island_v3', 'calgary-princes-spring-flood-v3'),
  skin('halifax_coastal_park', 'halifax_coastal_park_v0', 'halifax-coastal-storm-watch-v0'),
  skin('halifax_coastal_park', 'halifax_coastal_park_v1', 'halifax-coastal-summer-trail-v1'),
  skin('halifax_coastal_park', 'halifax_coastal_park_v3', 'halifax-coastal-sunset-boardwalk-v3'),
  skin('halifax_public_gardens', 'halifax_public_gardens_v1', 'halifax-public-bandstand-concert-v1'),
  skin('halifax_public_gardens', 'halifax_public_gardens_v2', 'halifax-public-autumn-stroll-v2'),
  skin('halifax_public_gardens', 'halifax_public_gardens_v3', 'halifax-public-spring-tulip-v3'),
  skin('london_circus', 'london_circus_v0', 'london-circus-round-island-v0'),
  skin('london_circus', 'london_circus_v2', 'london-circus-side-court-v2'),
  skin('london_circus', 'london_circus_v3', 'london-circus-narrow-passage-v3'),
  skin('london_garden_square', 'london_garden_square_v0', 'london-garden-open-garden-v0'),
  skin('london_garden_square', 'london_garden_square_v2', 'london-garden-lush-brick-v2'),
  skin('london_garden_square', 'london_garden_square_v3', 'london-garden-cafe-forecourt-v3'),
  skin('montreal_mount_royal', 'montreal_mount_royal_v0', 'montreal-mount-royal-overlook-v0'),
  skin('montreal_mount_royal', 'montreal_mount_royal_v1', 'montreal-mount-royal-lawn-grove-v1'),
  skin('montreal_mount_royal', 'montreal_mount_royal_v3', 'montreal-mount-royal-hillside-v3'),
  skin('montreal_square', 'montreal_square_v0', 'montreal-square-hard-plaza-v0'),
  skin('montreal_square', 'montreal_square_v1', 'montreal-square-linear-bench-v1'),
  skin('montreal_square', 'montreal_square_v2', 'montreal-square-pocket-court-v2'),
  skin('newyork_community_garden', 'newyork_community_garden_v0', 'new-york-community-allotment-v0'),
  skin('newyork_community_garden', 'newyork_community_garden_v1', 'new-york-community-raised-grid-v1'),
  skin('newyork_community_garden', 'newyork_community_garden_v2', 'new-york-community-garden-shed-v2'),
  skin('newyork_pocket_park', 'newyork_pocket_park_v1', 'new-york-pocket-linear-planters-v1'),
  skin('newyork_pocket_park', 'newyork_pocket_park_v2', 'new-york-pocket-brick-seat-v2'),
  skin('newyork_pocket_park', 'newyork_pocket_park_v3', 'new-york-pocket-promenade-v3'),
]);

export const batch24ParkSkinForSelection = (archetypeId: string, variantId: string): Batch24ParkSkinDefinition | null => (
  BATCH24_PARK_SKINS.find((candidate) => candidate.archetypeId === archetypeId && candidate.variantId === variantId) ?? null
);
