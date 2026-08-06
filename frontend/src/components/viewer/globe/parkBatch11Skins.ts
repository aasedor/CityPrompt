export interface Batch11ParkSkinDefinition {
  archetypeId: string; variantId: string; slug: string;
  roles: readonly ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'];
  people: false; largeBuildings: false;
}
const ROLES = ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'] as const;
const skin = (archetypeId: string, variantId: string, slug: string): Batch11ParkSkinDefinition => Object.freeze({ archetypeId, variantId, slug, roles: ROLES, people: false, largeBuildings: false });
export const BATCH11_PARK_SKINS = Object.freeze([
  skin('parisian_place', 'parisian_place_v2', 'paris-place-royale-cobbles-v2'),
  skin('parisian_square', 'parisian_square_v3', 'paris-square-tree-grid-v3'),
  skin('london_circus', 'london_circus_v1', 'london-circus-planted-v1'),
  skin('newyork_pocket_park', 'newyork_pocket_park_v0', 'new-york-pocket-water-v0'),
  skin('newyork_community_garden', 'newyork_community_garden_v3', 'new-york-community-greenhouse-v3'),
  skin('vancouver_seawall', 'vancouver_seawall_v2', 'vancouver-seawall-cycle-v2'),
  skin('vancouver_beach_park', 'vancouver_beach_park_v0', 'vancouver-beach-pavilion-v0'),
  skin('toronto_ravine', 'toronto_ravine_v1', 'toronto-ravine-creek-v1'),
  skin('toronto_urban_square', 'toronto_urban_square_v1', 'toronto-urban-market-v1'),
  skin('halifax_coastal_park', 'halifax_coastal_park_v2', 'halifax-coastal-fog-path-v2'),
]);
export function batch11ParkSkinForSelection(archetypeId: string, variantId: string): Batch11ParkSkinDefinition | null {
  return BATCH11_PARK_SKINS.find((candidate) => candidate.archetypeId === archetypeId && candidate.variantId === variantId) ?? null;
}
