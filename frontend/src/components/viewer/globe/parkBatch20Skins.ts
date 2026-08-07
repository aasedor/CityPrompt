export interface Batch20ParkSkinDefinition {
  archetypeId: string;
  variantId: string;
  slug: string;
  roles: readonly ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'];
  people: false;
  largeBuildings: false;
}

const ROLES = ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'] as const;
const skin = (archetypeId: string, variantId: string, slug: string): Batch20ParkSkinDefinition => Object.freeze({
  archetypeId, variantId, slug, roles: ROLES, people: false as const, largeBuildings: false as const,
});

/** Exact reference-derived material packs for the Batch 20 ecological,
 * adventure, performance, hospitality, and civic-plaza closure. Geometry is
 * retained from each reviewed anchor grammar; these definitions preserve the
 * catalogue variant's own material and landscape identity. */
export const BATCH20_PARK_SKINS = Object.freeze([
  skin('riparian_buffer', 'riparian_buffer_v1', 'riparian-buffer-bioengineered-v1'),
  skin('riparian_buffer', 'riparian_buffer_v2', 'riparian-buffer-rewilded-urban-v2'),
  skin('riparian_buffer', 'riparian_buffer_v3', 'riparian-buffer-resilient-coastal-v3'),
  skin('wetland_rain_garden', 'wetland_rain_garden_v1', 'wetland-rain-garden-bioengineered-v1'),
  skin('wetland_rain_garden', 'wetland_rain_garden_v2', 'wetland-rain-garden-rewilded-urban-v2'),
  skin('wetland_rain_garden', 'wetland_rain_garden_v3', 'wetland-rain-garden-resilient-coastal-v3'),
  skin('playground_adventure', 'playground_adventure_v1', 'playground-adventure-modern-steel-v1'),
  skin('playground_adventure', 'playground_adventure_v2', 'playground-adventure-natural-meadow-v2'),
  skin('playground_adventure', 'playground_adventure_v3', 'playground-adventure-urban-contemporary-v3'),
  skin('amphitheater_lawn', 'amphitheater_lawn_v1', 'amphitheater-open-festival-ground-v1'),
  skin('amphitheater_lawn', 'amphitheater_lawn_v2', 'amphitheater-intimate-garden-venue-v2'),
  skin('amphitheater_lawn', 'amphitheater_lawn_v3', 'amphitheater-industrial-adaptive-v3'),
  skin('beer_garden', 'beer_garden_v1', 'beer-garden-brewery-tap-yard-v1'),
  skin('beer_garden', 'beer_garden_v2', 'beer-garden-pergola-terrace-v2'),
  skin('beer_garden', 'beer_garden_v3', 'beer-garden-rooftop-v3'),
  skin('city_hall_government_plaza', 'city_hall_government_plaza_v0', 'city-hall-compact-forecourt-v0'),
  skin('city_hall_government_plaza', 'city_hall_government_plaza_v1', 'city-hall-historic-senate-v1'),
  skin('city_hall_government_plaza', 'city_hall_government_plaza_v3', 'city-hall-brutalist-forecourt-v3'),
  skin('sunken_plaza', 'sunken_plaza_v1', 'sunken-plaza-rockefeller-rink-v1'),
  skin('sunken_plaza', 'sunken_plaza_v2', 'sunken-plaza-corporate-atrium-v2'),
  skin('sunken_plaza', 'sunken_plaza_v3', 'sunken-plaza-asian-transit-v3'),
  skin('cathedral_religious_forecourt', 'cathedral_religious_forecourt_v0', 'cathedral-asian-temple-plaza-v0'),
  skin('cathedral_religious_forecourt', 'cathedral_religious_forecourt_v1', 'cathedral-gothic-parvis-v1'),
  skin('cathedral_religious_forecourt', 'cathedral_religious_forecourt_v2', 'cathedral-renaissance-basilica-v2'),
  skin('cultural_institution_forecourt', 'cultural_institution_forecourt_v1', 'cultural-library-steps-v1'),
  skin('cultural_institution_forecourt', 'cultural_institution_forecourt_v2', 'cultural-concert-hall-v2'),
  skin('cultural_institution_forecourt', 'cultural_institution_forecourt_v3', 'cultural-arena-concourse-v3'),
  skin('stepped_terraced_plaza', 'stepped_terraced_plaza_v0', 'stepped-aegean-village-v0'),
  skin('stepped_terraced_plaza', 'stepped_terraced_plaza_v1', 'stepped-spanish-travertine-v1'),
  skin('stepped_terraced_plaza', 'stepped_terraced_plaza_v2', 'stepped-federation-shard-v2'),
]);

export const batch20ParkSkinForSelection = (archetypeId: string, variantId: string): Batch20ParkSkinDefinition | null => (
  BATCH20_PARK_SKINS.find((candidate) => candidate.archetypeId === archetypeId && candidate.variantId === variantId) ?? null
);
