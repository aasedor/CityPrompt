export interface Batch8ParkSkinDefinition {
  archetypeId: string;
  variantId: string;
  slug: string;
  roles: readonly ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'];
  people: false;
  largeBuildings: false;
}

const ROLES = ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'] as const;

const skin = (archetypeId: string, variantId: string, slug: string): Batch8ParkSkinDefinition => Object.freeze({
  archetypeId, variantId, slug, roles: ROLES, people: false, largeBuildings: false,
});

/** Batch 8 was visually selected from the four catalogue references before
 * authoring. Pixels inform role-specific material statistics only; geometry
 * and repetition remain parcel-aware and no people or large buildings render. */
export const BATCH8_PARK_SKINS = Object.freeze([
  skin('reclaimed_industrial_park', 'reclaimed_industrial_park_v0', 'reclaimed-industrial-wharf-v0'),
  skin('quarry_sunken_garden_park', 'quarry_sunken_garden_park_v2', 'quarry-limestone-tier-cascade-v2'),
  skin('estate_picnic_grove', 'estate_picnic_grove_v1', 'estate-oak-picnic-grove-v1'),
  skin('constructed_wetland_eco_park', 'constructed_wetland_eco_park_variant_0', 'constructed-urban-boardwalk-wetland-v0'),
  skin('academic_courtyard', 'academic_courtyard_variant_0', 'academic-modern-planted-courtyard-v0'),
  skin('campus_pedestrian_spine', 'campus_pedestrian_spine_variant_0', 'campus-green-planted-spine-v0'),
  skin('botanical_garden', 'botanical_garden_v3', 'botanical-romantic-rose-garden-v3'),
  skin('research_garden_teaching_arboretum', 'research_garden_teaching_arboretum_variant_0', 'research-tree-collection-arboretum-v0'),
  skin('rewilding_ecological_restoration_zone', 'rewilding_ecological_restoration_zone_variant_1', 'rewilding-reforestation-zone-v1'),
  skin('stormwater_resilience_park', 'stormwater_resilience_park_variant_3', 'stormwater-arid-rock-channel-v3'),
]);

export function batch8ParkSkinForSelection(archetypeId: string, variantId: string): Batch8ParkSkinDefinition | null {
  return BATCH8_PARK_SKINS.find((candidate) => candidate.archetypeId === archetypeId && candidate.variantId === variantId) ?? null;
}

export function batch8ParkSkinRoot(definition: Batch8ParkSkinDefinition): string {
  return `/park-skins/${definition.slug}/adaptive-v1`;
}
