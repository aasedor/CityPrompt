export interface Batch14ParkSkinDefinition {
  archetypeId: string;
  variantId: string;
  slug: string;
  roles: readonly ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'];
  people: false;
  largeBuildings: false;
}

const ROLES = ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'] as const;
const skin = (archetypeId: string, variantId: string, slug: string): Batch14ParkSkinDefinition => Object.freeze({
  archetypeId,
  variantId,
  slug,
  roles: ROLES,
  people: false as const,
  largeBuildings: false as const,
});

export const BATCH14_PARK_SKINS = Object.freeze([
  skin('surface_parking_lot', 'surface_parking_lot_v0', 'surface-parking-standard-v0'),
  skin('structured_parking_garage', 'structured_parking_garage_v2', 'structured-parking-urban-v2'),
  skin('underground_parking_entry', 'underground_parking_entry_v1', 'underground-parking-green-v1'),
  skin('green_parking_lot', 'green_parking_lot_v1', 'green-parking-infrastructure-v1'),
  skin('airport_airfield', 'airport_airfield_variant_2', 'airport-general-aviation-v2'),
  skin('equestrian_center', 'equestrian_center_variant_1', 'equestrian-working-stable-v1'),
  skin('golf_course_18_hole', 'golf_course_18_hole_variant_0', 'golf-seaside-links-v0'),
  skin('golf_driving_range', 'golf_driving_range_variant_0', 'driving-range-single-tier-v0'),
  skin('multi_sport_complex', 'multi_sport_complex_variant_3', 'multi-sport-track-field-v3'),
  skin('suburban_retail_parking_lot', 'suburban_retail_parking_lot_v1', 'retail-parking-landscaped-v1'),
]);

export const batch14ParkSkinForSelection = (archetypeId: string, variantId: string): Batch14ParkSkinDefinition | null => (
  BATCH14_PARK_SKINS.find((candidate) => candidate.archetypeId === archetypeId && candidate.variantId === variantId) ?? null
);
