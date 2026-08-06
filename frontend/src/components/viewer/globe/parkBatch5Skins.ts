export interface Batch5ParkSkinDefinition {
  archetypeId: string;
  variantId: string;
  slug: string;
  roles: readonly ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'];
  people: false;
  largeBuildings: false;
}

const ROLES = ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'] as const;

const skin = (archetypeId: string, slug: string): Batch5ParkSkinDefinition => Object.freeze({
  archetypeId,
  variantId: `${archetypeId}_v0`,
  slug,
  roles: ROLES,
  people: false,
  largeBuildings: false,
});

/** Batch 5 is deliberately exact-selection only. Each program owns a stationary
 * PBR library derived from its v0 catalogue render; no generic surface family
 * or projected photograph is permitted. */
export const BATCH5_PARK_SKINS = Object.freeze([
  skin('disc_golf_course', 'disc-golf-wooded-championship'),
  skin('bocce_petanque_court', 'bocce-italian-piazza'),
  skin('climbing_bouldering_wall', 'climbing-competition-boulder'),
  skin('mini_golf_course', 'mini-golf-classic-themed'),
  skin('beach_volleyball_courts', 'beach-volleyball-competition'),
  skin('pollinator_meadow', 'pollinator-prairie-restoration'),
  skin('urban_orchard_food_forest', 'urban-orchard-heritage-apple'),
  skin('bioswale_rain_garden', 'bioswale-streetside'),
  skin('sculpture_garden', 'sculpture-museum-court'),
  skin('labyrinth_meditation', 'labyrinth-classical-stone'),
]);

export function batch5ParkSkinForSelection(
  archetypeId: string,
  variantId: string,
): Batch5ParkSkinDefinition | null {
  return BATCH5_PARK_SKINS.find((candidate) => (
    candidate.archetypeId === archetypeId && candidate.variantId === variantId
  )) ?? null;
}

export function batch5ParkSkinRoot(definition: Batch5ParkSkinDefinition): string {
  return `/park-skins/${definition.slug}/adaptive-v1`;
}
