export interface Batch23ParkSkinDefinition {
  archetypeId: string;
  variantId: string;
  slug: string;
  roles: readonly ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'];
  people: false;
  largeBuildings: false;
}

const ROLES = ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'] as const;
const skin = (archetypeId: string, variantId: string, slug: string): Batch23ParkSkinDefinition => Object.freeze({
  archetypeId, variantId, slug, roles: ROLES, people: false as const, largeBuildings: false as const,
});

/** Exact reference-derived packs for community gardens and the Paris,
 * Amsterdam and Barcelona public-realm families. Large enclosing buildings
 * and reference-image people are deliberately excluded from every pack. */
export const BATCH23_PARK_SKINS = Object.freeze([
  skin('community_garden_enhanced', 'garden_classic_allotment', 'community-garden-classic-allotment-v0'),
  skin('community_garden_enhanced', 'garden_permaculture_farm', 'community-garden-permaculture-farm-v1'),
  skin('community_garden_enhanced', 'garden_intercultural', 'community-garden-intercultural-social-v3'),
  skin('parisian_place', 'parisian_place_v0', 'paris-place-quiet-cobble-v0'),
  skin('parisian_place', 'parisian_place_v1', 'paris-place-statue-axis-v1'),
  skin('parisian_place', 'parisian_place_v3', 'paris-place-cafe-paved-v3'),
  skin('parisian_square', 'parisian_square_v0', 'paris-square-linear-edge-v0'),
  skin('parisian_square', 'parisian_square_v1', 'paris-square-corner-cafe-v1'),
  skin('parisian_square', 'parisian_square_v2', 'paris-square-compact-cobble-v2'),
  skin('parisian_jardin', 'parisian_jardin_v0', 'paris-jardin-clipped-parterre-v0'),
  skin('parisian_jardin', 'parisian_jardin_v2', 'paris-jardin-rill-garden-v2'),
  skin('parisian_jardin', 'parisian_jardin_v3', 'paris-jardin-paved-forecourt-v3'),
  skin('amsterdam_vondelpark', 'amsterdam_vondelpark_v0', 'amsterdam-vondelpark-neighbourhood-edge-v0'),
  skin('amsterdam_vondelpark', 'amsterdam_vondelpark_v1', 'amsterdam-vondelpark-cafe-edge-v1'),
  skin('amsterdam_vondelpark', 'amsterdam_vondelpark_v2', 'amsterdam-vondelpark-planted-corner-v2'),
  skin('amsterdam_hofje_garden', 'amsterdam_hofje_garden_v1', 'amsterdam-hofje-lush-communal-v1'),
  skin('amsterdam_hofje_garden', 'amsterdam_hofje_garden_v2', 'amsterdam-hofje-pocket-garden-v2'),
  skin('amsterdam_hofje_garden', 'amsterdam_hofje_garden_v3', 'amsterdam-hofje-historic-lawn-v3'),
  skin('amsterdam_plein', 'amsterdam_plein_v1', 'amsterdam-plein-glass-canopy-v1'),
  skin('amsterdam_plein', 'amsterdam_plein_v2', 'amsterdam-plein-cafe-threshold-v2'),
  skin('amsterdam_plein', 'amsterdam_plein_v3', 'amsterdam-plein-open-brick-v3'),
  skin('barcelona_pati_interior', 'barcelona_pati_interior_v1', 'barcelona-pati-lawn-court-v1'),
  skin('barcelona_pati_interior', 'barcelona_pati_interior_v2', 'barcelona-pati-social-paved-v2'),
  skin('barcelona_pati_interior', 'barcelona_pati_interior_v3', 'barcelona-pati-shade-paved-v3'),
  skin('barcelona_placa_xamfra', 'barcelona_placa_xamfra_v0', 'barcelona-xamfra-cafe-corner-v0'),
  skin('barcelona_placa_xamfra', 'barcelona_placa_xamfra_v1', 'barcelona-xamfra-clear-corner-v1'),
  skin('barcelona_placa_xamfra', 'barcelona_placa_xamfra_v3', 'barcelona-xamfra-active-corner-v3'),
  skin('barcelona_superilla', 'barcelona_superilla_v0', 'barcelona-superilla-plaza-planters-v0'),
  skin('barcelona_superilla', 'barcelona_superilla_v2', 'barcelona-superilla-green-corridor-v2'),
  skin('barcelona_superilla', 'barcelona_superilla_v3', 'barcelona-superilla-social-garden-v3'),
]);

export const batch23ParkSkinForSelection = (archetypeId: string, variantId: string): Batch23ParkSkinDefinition | null => (
  BATCH23_PARK_SKINS.find((candidate) => candidate.archetypeId === archetypeId && candidate.variantId === variantId) ?? null
);
