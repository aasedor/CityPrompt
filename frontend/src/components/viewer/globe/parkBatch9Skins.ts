export interface Batch9ParkSkinDefinition {
  archetypeId: string;
  variantId: string;
  slug: string;
  roles: readonly ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'];
  people: false;
  largeBuildings: false;
}

const ROLES = ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'] as const;
const skin = (archetypeId: string, variantId: string, slug: string): Batch9ParkSkinDefinition => Object.freeze({
  archetypeId, variantId, slug, roles: ROLES, people: false, largeBuildings: false,
});

/** Exact references were selected by comparing all four catalogue variants.
 * They provide spatial and material evidence, never projected source pixels. */
export const BATCH9_PARK_SKINS = Object.freeze([
  skin('urban_pocket_park', 'urban_pocket_park_v0', 'urban-pocket-rustic-v0'),
  skin('neighborhood_park', 'neighborhood_park_v3', 'neighborhood-urban-contemporary-v3'),
  skin('cemetery_memorial_grounds', 'cemetery_memorial_grounds_v0', 'cemetery-classical-formal-v0'),
  skin('courtyard_plaza', 'courtyard_plaza_v1', 'courtyard-contemporary-water-v1'),
  skin('street_plaza_parklet', 'street_plaza_parklet_v1', 'street-parklet-sf-timber-v1'),
  skin('parisian_jardin', 'parisian_jardin_v1', 'jardin-francaise-water-axis-v1'),
  skin('london_garden_square', 'london_garden_square_v1', 'london-garden-square-railed-v1'),
  skin('halifax_public_gardens', 'halifax_public_gardens_v0', 'halifax-public-rose-bandstand-v0'),
  skin('picturesque_olmsted_park', 'picturesque_olmsted_park_v3', 'olmsted-central-park-multilandscape-v3'),
  skin('hilltop_topographic_park', 'hilltop_topographic_park_v3', 'hilltop-pacific-terraced-viewpoint-v3'),
]);

export function batch9ParkSkinForSelection(archetypeId: string, variantId: string): Batch9ParkSkinDefinition | null {
  return BATCH9_PARK_SKINS.find((candidate) => candidate.archetypeId === archetypeId && candidate.variantId === variantId) ?? null;
}

export function batch9ParkSkinRoot(definition: Batch9ParkSkinDefinition): string {
  return `/park-skins/${definition.slug}/adaptive-v1`;
}
