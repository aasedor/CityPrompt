export interface Batch18ParkSkinDefinition {
  archetypeId: string;
  variantId: string;
  slug: string;
  roles: readonly ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'];
  people: false;
  largeBuildings: false;
}

const ROLES = ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'] as const;
const skin = (archetypeId: string, variantId: string, slug: string): Batch18ParkSkinDefinition => Object.freeze({
  archetypeId, variantId, slug, roles: ROLES, people: false as const, largeBuildings: false as const,
});

export const BATCH18_PARK_SKINS = Object.freeze([
  skin('disc_golf_course', 'disc_golf_course_v1', 'disc-golf-open-park-v1'),
  skin('disc_golf_course', 'disc_golf_course_v2', 'disc-golf-hillside-terrain-v2'),
  skin('disc_golf_course', 'disc_golf_course_v3', 'disc-golf-urban-short-v3'),
  skin('bocce_petanque_court', 'bocce_petanque_court_v1', 'bocce-french-petanque-v1'),
  skin('bocce_petanque_court', 'bocce_petanque_court_v2', 'bocce-modern-park-v2'),
  skin('bocce_petanque_court', 'bocce_petanque_court_v3', 'bocce-community-senior-v3'),
  skin('climbing_bouldering_wall', 'climbing_bouldering_wall_v1', 'climbing-natural-rock-v1'),
  skin('climbing_bouldering_wall', 'climbing_bouldering_wall_v2', 'climbing-kids-adventure-v2'),
  skin('climbing_bouldering_wall', 'climbing_bouldering_wall_v3', 'climbing-urban-art-v3'),
  skin('mini_golf_course', 'mini_golf_course_v1', 'mini-golf-garden-putting-v1'),
  skin('mini_golf_course', 'mini_golf_course_v2', 'mini-golf-urban-art-v2'),
  skin('mini_golf_course', 'mini_golf_course_v3', 'mini-golf-nature-adventure-v3'),
  skin('beach_volleyball_courts', 'beach_volleyball_courts_v1', 'beach-volleyball-beachside-v1'),
  skin('beach_volleyball_courts', 'beach_volleyball_courts_v2', 'beach-volleyball-park-sand-v2'),
  skin('beach_volleyball_courts', 'beach_volleyball_courts_v3', 'beach-volleyball-indoor-outdoor-v3'),
  skin('pollinator_meadow', 'pollinator_meadow_v1', 'pollinator-butterfly-garden-v1'),
  skin('pollinator_meadow', 'pollinator_meadow_v2', 'pollinator-urban-strip-v2'),
  skin('pollinator_meadow', 'pollinator_meadow_v3', 'pollinator-formal-border-v3'),
  skin('urban_orchard_food_forest', 'urban_orchard_food_forest_v1', 'urban-orchard-permaculture-v1'),
  skin('urban_orchard_food_forest', 'urban_orchard_food_forest_v2', 'urban-orchard-pick-your-own-v2'),
  skin('urban_orchard_food_forest', 'urban_orchard_food_forest_v3', 'urban-orchard-citrus-grove-v3'),
  skin('bioswale_rain_garden', 'bioswale_rain_garden_v1', 'bioswale-park-rain-garden-v1'),
  skin('bioswale_rain_garden', 'bioswale_rain_garden_v2', 'bioswale-terraced-rain-steps-v2'),
  skin('bioswale_rain_garden', 'bioswale_rain_garden_v3', 'bioswale-parking-lot-v3'),
  skin('sculpture_garden', 'sculpture_garden_v1', 'sculpture-landscape-art-v1'),
  skin('sculpture_garden', 'sculpture_garden_v2', 'sculpture-interactive-kinetic-v2'),
  skin('sculpture_garden', 'sculpture_garden_v3', 'sculpture-rotating-exhibition-v3'),
  skin('labyrinth_meditation', 'labyrinth_meditation_v1', 'labyrinth-zen-rock-v1'),
  skin('labyrinth_meditation', 'labyrinth_meditation_v2', 'labyrinth-healing-garden-v2'),
  skin('labyrinth_meditation', 'labyrinth_meditation_v3', 'labyrinth-modern-mindfulness-v3'),
]);

export const batch18ParkSkinForSelection = (archetypeId: string, variantId: string): Batch18ParkSkinDefinition | null => (
  BATCH18_PARK_SKINS.find((candidate) => candidate.archetypeId === archetypeId && candidate.variantId === variantId) ?? null
);
