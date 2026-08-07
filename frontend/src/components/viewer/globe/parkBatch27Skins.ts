export interface Batch27ParkSkinDefinition {
  archetypeId: string;
  variantId: string;
  slug: string;
  roles: readonly ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'];
  people: false;
  largeBuildings: false;
}

const ROLES = ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'] as const;
const skin = (archetypeId: string, variantId: string, slug: string): Batch27ParkSkinDefinition => Object.freeze({
  archetypeId, variantId, slug, roles: ROLES, people: false as const, largeBuildings: false as const,
});

/** Final catalogue closure: twenty-one exact-reference material packs across
 * the seven remaining partial civic, teaching and resilience families. */
export const BATCH27_PARK_SKINS = Object.freeze([
  skin('academic_courtyard', 'academic_courtyard_variant_1', 'academic-corten-hardscape-v1'),
  skin('academic_courtyard', 'academic_courtyard_variant_2', 'academic-glass-canopy-v2'),
  skin('academic_courtyard', 'academic_courtyard_variant_3', 'academic-timber-screen-v3'),
  skin('campus_pedestrian_spine', 'campus_pedestrian_spine_variant_1', 'campus-urban-paved-spine-v1'),
  skin('campus_pedestrian_spine', 'campus_pedestrian_spine_variant_2', 'campus-pavilion-spine-v2'),
  skin('campus_pedestrian_spine', 'campus_pedestrian_spine_variant_3', 'campus-pergola-spine-v3'),
  skin('constructed_wetland_eco_park', 'constructed_wetland_eco_park_variant_1', 'wetland-tidal-treatment-v1'),
  skin('constructed_wetland_eco_park', 'constructed_wetland_eco_park_variant_2', 'wetland-wildlife-v2'),
  skin('constructed_wetland_eco_park', 'constructed_wetland_eco_park_variant_3', 'wetland-nature-center-v3'),
  skin('research_garden_teaching_arboretum', 'research_garden_teaching_arboretum_variant_1', 'research-greenhouse-garden-v1'),
  skin('research_garden_teaching_arboretum', 'research_garden_teaching_arboretum_variant_2', 'research-teaching-pavilion-v2'),
  skin('research_garden_teaching_arboretum', 'research_garden_teaching_arboretum_variant_3', 'research-demonstration-plots-v3'),
  skin('rewilding_ecological_restoration_zone', 'rewilding_ecological_restoration_zone_variant_0', 'rewilding-urban-prairie-v0'),
  skin('rewilding_ecological_restoration_zone', 'rewilding_ecological_restoration_zone_variant_2', 'rewilding-interpretive-v2'),
  skin('rewilding_ecological_restoration_zone', 'rewilding_ecological_restoration_zone_variant_3', 'rewilding-riparian-v3'),
  skin('stormwater_naturalized_drainage_corridor', 'stormwater_naturalized_drainage_corridor_variant_1', 'drainage-urban-daylit-v1'),
  skin('stormwater_naturalized_drainage_corridor', 'stormwater_naturalized_drainage_corridor_variant_2', 'drainage-seasonal-planted-v2'),
  skin('stormwater_naturalized_drainage_corridor', 'stormwater_naturalized_drainage_corridor_variant_3', 'drainage-stream-shelter-v3'),
  skin('stormwater_resilience_park', 'stormwater_resilience_park_variant_0', 'stormwater-urban-bioswale-v0'),
  skin('stormwater_resilience_park', 'stormwater_resilience_park_variant_1', 'stormwater-naturalistic-detention-v1'),
  skin('stormwater_resilience_park', 'stormwater_resilience_park_variant_2', 'stormwater-engineered-plaza-v2'),
]);

export const batch27ParkSkinForSelection = (archetypeId: string, variantId: string): Batch27ParkSkinDefinition | null => (
  BATCH27_PARK_SKINS.find((candidate) => candidate.archetypeId === archetypeId && candidate.variantId === variantId) ?? null
);
