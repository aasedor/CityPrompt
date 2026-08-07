export interface Batch10ParkSkinDefinition {
  archetypeId: string;
  variantId: string;
  slug: string;
  roles: readonly ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'];
  people: false;
  largeBuildings: false;
}

const ROLES = ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'] as const;
const skin = (archetypeId: string, variantId: string, slug: string): Batch10ParkSkinDefinition => Object.freeze({
  archetypeId, variantId, slug, roles: ROLES, people: false, largeBuildings: false,
});

/** Exact ground and park-kit evidence selected after reviewing all four references.
 * Building-dominated pixels are never emitted as park geometry. */
export const BATCH10_PARK_SKINS = Object.freeze([
  skin('amsterdam_hofje_garden', 'amsterdam_hofje_garden_v0', 'amsterdam-hofje-garden-v0'),
  skin('amsterdam_plein', 'amsterdam_plein_v0', 'amsterdam-brick-plein-v0'),
  skin('amsterdam_vondelpark', 'amsterdam_vondelpark_v3', 'amsterdam-vondelpark-pavilion-v3'),
  skin('barcelona_pati_interior', 'barcelona_pati_interior_v0', 'barcelona-pati-green-v0'),
  skin('barcelona_placa_xamfra', 'barcelona_placa_xamfra_v2', 'barcelona-xamfra-corner-v2'),
  skin('barcelona_superilla', 'barcelona_superilla_v1', 'barcelona-superilla-green-v1'),
  skin('calgary_prairie_plaza', 'calgary_prairie_plaza_v1', 'calgary-prairie-market-v1'),
  skin('calgary_princes_island', 'calgary_princes_island_v0', 'calgary-princes-island-festival-v0'),
  skin('montreal_mount_royal', 'montreal_mount_royal_v2', 'montreal-mount-royal-grove-v2'),
  skin('montreal_square', 'montreal_square_v3', 'montreal-neighbourhood-square-v3'),
]);

export function batch10ParkSkinForSelection(archetypeId: string, variantId: string): Batch10ParkSkinDefinition | null {
  return BATCH10_PARK_SKINS.find((candidate) => candidate.archetypeId === archetypeId && candidate.variantId === variantId) ?? null;
}
