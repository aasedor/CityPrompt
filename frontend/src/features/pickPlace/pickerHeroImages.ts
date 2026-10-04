/** Curated picker views for exact choices whose runtime thumbnails are
 * technical model previews. Placement and capture continue to use the locked
 * asset thumbnail and revision from the catalogue registry. */
export const PICKER_HERO_IMAGES: Record<string, string> = {
  validation_machiya_cafe_gallery: '/archetypes/buildings/classroom-heroes/machiya-cafe-gallery-v005.webp',
  'native-park:student_neighbourhood_orchard_v1--native-v1': '/archetypes/openspaces/classroom-heroes/orchard-v002.webp',
  'native-park:student_garden_square_v1--native-v1': '/archetypes/openspaces/classroom-heroes/square-v003.webp',
  'native-park:student_reading_garden_v2--native-v1': '/archetypes/openspaces/classroom-heroes/reading-v002.webp',
  'native-park:student_pickleball_garden_v1--native-v1': '/archetypes/openspaces/classroom-heroes/pickleball-v001.webp',
  'native-park:student_tennis_garden_v2--native-v1': '/archetypes/openspaces/classroom-heroes/tennis-v002.webp',
  'native-park:student_bocce_garden_v2--native-v1': '/archetypes/openspaces/classroom-heroes/bocce-v002.webp',
  'native-park:urban_pocket_park_v0--native-v1': '/archetypes/openspaces/classroom-heroes/pocket-v003.webp',
  'native-park:linear_park_greenway_v0--native-v1': '/archetypes/openspaces/classroom-heroes/greenway-v002.webp',
  'native-park:inclusive_accessible_playground_v0--native-v1': '/archetypes/openspaces/classroom-heroes/inclusive-v002.webp',
  student_planted_shared_lane_v1: '/archetypes/streets/classroom-heroes/shared-v001.webp',
  student_quiet_residential_street_v1: '/archetypes/streets/classroom-heroes/residential-v002.webp',
  trial_neighborhood20_childcare_garden_pavilion: '/validation-assets/neighborhood20/childcare-garden-v004/hero.png',
  trial_neighborhood20_fourplex_corner_entries: '/validation-assets/neighborhood20/fourplex-corner-v004/hero.png',
  trial_neighborhood20_sixplex_brick_walk_up: '/validation-assets/neighborhood20/sixplex-brick-v003/hero.png',
  trial_neighborhood20_library_neighborhood_pavilion: '/validation-assets/neighborhood20/library-pavilion-v004/hero.png',
  trial_neighborhood20_hall_prairie_community_league: '/validation-assets/neighborhood20/hall-prairie-v003/hero.png',
  trial_neighborhood20_school_shared_community_campus: '/validation-assets/neighborhood20/school-campus-v005/hero.png',
  trial_neighborhood20_childcare_sheltered_courtyard: '/validation-assets/neighborhood20/childcare-courtyard-v003/hero.png',
  trial_neighborhood20_sixplex_two_storey_garden: '/validation-assets/neighborhood20/sixplex-garden-v002/hero.png',
  trial_neighborhood20_hall_timber_park_edge: '/validation-assets/neighborhood20/hall-park-v002/hero.png',
  trial_neighborhood20_school_timber_learning_courtyard: '/validation-assets/neighborhood20/school-timber-v001/hero.png',
};

export function pickerHeroImage(placementId: string | undefined, fallback: string): string {
  return (placementId && PICKER_HERO_IMAGES[placementId]) || fallback;
}
