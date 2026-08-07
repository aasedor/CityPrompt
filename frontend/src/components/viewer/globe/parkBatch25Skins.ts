export interface Batch25ParkSkinDefinition {
  archetypeId: string;
  variantId: string;
  slug: string;
  roles: readonly ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'];
  people: false;
  largeBuildings: false;
}

const ROLES = ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'] as const;
const skin = (archetypeId: string, variantId: string, slug: string): Batch25ParkSkinDefinition => Object.freeze({
  archetypeId, variantId, slug, roles: ROLES, people: false as const, largeBuildings: false as const,
});

/** Reference-derived packs for the waterfront, ravine, civic-square,
 * topographic, post-industrial, picnic and reservoir closure families. */
export const BATCH25_PARK_SKINS = Object.freeze([
  skin('vancouver_seawall', 'vancouver_seawall_v0', 'vancouver-seawall-promenade-v0'),
  skin('vancouver_seawall', 'vancouver_seawall_v1', 'vancouver-seawall-bench-v1'),
  skin('vancouver_seawall', 'vancouver_seawall_v3', 'vancouver-seawall-esplanade-v3'),
  skin('vancouver_beach_park', 'vancouver_beach_park_v1', 'vancouver-beach-brick-pavilion-v1'),
  skin('vancouver_beach_park', 'vancouver_beach_park_v2', 'vancouver-beach-glazed-pavilion-v2'),
  skin('vancouver_beach_park', 'vancouver_beach_park_v3', 'vancouver-beach-waterfront-garden-v3'),
  skin('toronto_ravine', 'toronto_ravine_v0', 'toronto-ravine-spring-trillium-v0'),
  skin('toronto_ravine', 'toronto_ravine_v2', 'toronto-ravine-autumn-maple-v2'),
  skin('toronto_ravine', 'toronto_ravine_v3', 'toronto-ravine-winter-creek-v3'),
  skin('toronto_urban_square', 'toronto_urban_square_v0', 'toronto-square-winter-rink-v0'),
  skin('toronto_urban_square', 'toronto_urban_square_v2', 'toronto-square-modernist-pool-v2'),
  skin('toronto_urban_square', 'toronto_urban_square_v3', 'toronto-square-rain-garden-v3'),
  skin('picturesque_olmsted_park', 'picturesque_olmsted_park_v0', 'olmsted-wild-heath-v0'),
  skin('picturesque_olmsted_park', 'picturesque_olmsted_park_v1', 'olmsted-hillside-lookout-v1'),
  skin('picturesque_olmsted_park', 'picturesque_olmsted_park_v2', 'olmsted-meadow-ravine-lake-v2'),
  skin('reclaimed_industrial_park', 'reclaimed_industrial_park_v1', 'reclaimed-gasworks-mound-v1'),
  skin('reclaimed_industrial_park', 'reclaimed_industrial_park_v2', 'reclaimed-colliery-headframe-v2'),
  skin('reclaimed_industrial_park', 'reclaimed_industrial_park_v3', 'reclaimed-steelworks-basin-v3'),
  skin('quarry_sunken_garden_park', 'quarry_sunken_garden_park_v0', 'quarry-sculpture-bowl-v0'),
  skin('quarry_sunken_garden_park', 'quarry_sunken_garden_park_v1', 'quarry-lake-beach-v1'),
  skin('quarry_sunken_garden_park', 'quarry_sunken_garden_park_v3', 'quarry-show-garden-v3'),
  skin('hilltop_topographic_park', 'hilltop_topographic_park_v0', 'hilltop-cypress-terraces-v0'),
  skin('hilltop_topographic_park', 'hilltop_topographic_park_v1', 'hilltop-urban-switchback-v1'),
  skin('hilltop_topographic_park', 'hilltop_topographic_park_v2', 'hilltop-rocky-folly-v2'),
  skin('estate_picnic_grove', 'estate_picnic_grove_v0', 'estate-pine-creek-v0'),
  skin('estate_picnic_grove', 'estate_picnic_grove_v2', 'estate-meadow-pavilion-v2'),
  skin('estate_picnic_grove', 'estate_picnic_grove_v3', 'estate-regional-picnic-v3'),
  skin('reservoir_watershed_park', 'reservoir_watershed_park_v1', 'reservoir-stone-bank-v1'),
  skin('reservoir_watershed_park', 'reservoir_watershed_park_v2', 'reservoir-forested-upland-v2'),
  skin('reservoir_watershed_park', 'reservoir_watershed_park_v3', 'reservoir-earthen-dam-v3'),
]);

export const batch25ParkSkinForSelection = (archetypeId: string, variantId: string): Batch25ParkSkinDefinition | null => (
  BATCH25_PARK_SKINS.find((candidate) => candidate.archetypeId === archetypeId && candidate.variantId === variantId) ?? null
);
