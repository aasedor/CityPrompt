export interface Batch15ParkSkinDefinition {
  archetypeId: string;
  variantId: string;
  slug: string;
  roles: readonly ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'];
  people: false;
  largeBuildings: false;
}

const ROLES = ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'] as const;
const skin = (archetypeId: string, variantId: string, slug: string): Batch15ParkSkinDefinition => Object.freeze({
  archetypeId, variantId, slug, roles: ROLES, people: false as const, largeBuildings: false as const,
});

export const BATCH15_PARK_SKINS = Object.freeze([
  skin('surface_parking_lot', 'surface_parking_lot_v1', 'surface-parking-green-v1'),
  skin('surface_parking_lot', 'surface_parking_lot_v2', 'surface-parking-urban-v2'),
  skin('surface_parking_lot', 'surface_parking_lot_v3', 'surface-parking-screened-v3'),
  skin('structured_parking_garage', 'structured_parking_garage_v0', 'structured-parking-standard-v0'),
  skin('structured_parking_garage', 'structured_parking_garage_v1', 'structured-parking-green-v1'),
  skin('structured_parking_garage', 'structured_parking_garage_v3', 'structured-parking-screened-v3'),
  skin('underground_parking_entry', 'underground_parking_entry_v0', 'underground-parking-standard-v0'),
  skin('underground_parking_entry', 'underground_parking_entry_v2', 'underground-parking-urban-v2'),
  skin('underground_parking_entry', 'underground_parking_entry_v3', 'underground-parking-screened-v3'),
  skin('green_parking_lot', 'green_parking_lot_v0', 'green-parking-standard-v0'),
  skin('green_parking_lot', 'green_parking_lot_v2', 'green-parking-urban-v2'),
  skin('green_parking_lot', 'green_parking_lot_v3', 'green-parking-screened-v3'),
  skin('airport_airfield', 'airport_airfield_variant_0', 'airport-major-hub-v0'),
  skin('airport_airfield', 'airport_airfield_variant_1', 'airport-regional-v1'),
  skin('airport_airfield', 'airport_airfield_variant_3', 'airport-mid-size-v3'),
  skin('equestrian_center', 'equestrian_center_variant_0', 'equestrian-boarding-v0'),
  skin('equestrian_center', 'equestrian_center_variant_2', 'equestrian-competition-v2'),
  skin('equestrian_center', 'equestrian_center_variant_3', 'equestrian-academy-v3'),
  skin('golf_course_18_hole', 'golf_course_18_hole_variant_1', 'golf-parkland-v1'),
  skin('golf_course_18_hole', 'golf_course_18_hole_variant_2', 'golf-desert-v2'),
  skin('golf_course_18_hole', 'golf_course_18_hole_variant_3', 'golf-modern-club-v3'),
  skin('golf_driving_range', 'golf_driving_range_variant_1', 'driving-range-entertainment-v1'),
  skin('golf_driving_range', 'golf_driving_range_variant_2', 'driving-range-parkland-v2'),
  skin('golf_driving_range', 'golf_driving_range_variant_3', 'driving-range-modern-v3'),
  skin('multi_sport_complex', 'multi_sport_complex_variant_0', 'multi-sport-community-v0'),
  skin('multi_sport_complex', 'multi_sport_complex_variant_1', 'multi-sport-stadium-v1'),
  skin('multi_sport_complex', 'multi_sport_complex_variant_2', 'multi-sport-dome-v2'),
  skin('suburban_retail_parking_lot', 'suburban_retail_parking_lot_v0', 'retail-parking-big-box-v0'),
  skin('suburban_retail_parking_lot', 'suburban_retail_parking_lot_v2', 'retail-parking-gravel-v2'),
  skin('suburban_retail_parking_lot', 'suburban_retail_parking_lot_v3', 'retail-parking-plaza-v3'),
]);

export const batch15ParkSkinForSelection = (archetypeId: string, variantId: string): Batch15ParkSkinDefinition | null => (
  BATCH15_PARK_SKINS.find((candidate) => candidate.archetypeId === archetypeId && candidate.variantId === variantId) ?? null
);
