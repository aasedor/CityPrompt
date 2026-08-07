export interface Batch22ParkSkinDefinition {
  archetypeId: string;
  variantId: string;
  slug: string;
  roles: readonly ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'];
  people: false;
  largeBuildings: false;
}

const ROLES = ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'] as const;
const skin = (archetypeId: string, variantId: string, slug: string): Batch22ParkSkinDefinition => Object.freeze({
  archetypeId, variantId, slug, roles: ROLES, people: false as const, largeBuildings: false as const,
});

/** Exact reference-derived packs for memorial, civic, performance, water,
 * preserve, riverfront and curbside public-realm families. */
export const BATCH22_PARK_SKINS = Object.freeze([
  skin('cemetery_memorial_grounds', 'cemetery_memorial_grounds_v1', 'cemetery-woodland-naturalistic-v1'),
  skin('cemetery_memorial_grounds', 'cemetery_memorial_grounds_v2', 'cemetery-contemporary-sculptural-v2'),
  skin('cemetery_memorial_grounds', 'cemetery_memorial_grounds_v3', 'cemetery-cottage-romantic-v3'),
  skin('courtyard_plaza', 'courtyard_plaza_v0', 'courtyard-neoclassical-stone-v0'),
  skin('courtyard_plaza', 'courtyard_plaza_v2', 'courtyard-green-civic-v2'),
  skin('courtyard_plaza', 'courtyard_plaza_v3', 'courtyard-festival-market-v3'),
  skin('transit_plaza', 'transit_plaza_v0', 'transit-neoclassical-stone-v0'),
  skin('transit_plaza', 'transit_plaza_v1', 'transit-contemporary-urban-v1'),
  skin('transit_plaza', 'transit_plaza_v3', 'transit-festival-market-v3'),
  skin('amphitheater_performance_space', 'amphitheater_performance_space_v1', 'amphitheater-open-festival-v1'),
  skin('amphitheater_performance_space', 'amphitheater_performance_space_v2', 'amphitheater-intimate-garden-v2'),
  skin('amphitheater_performance_space', 'amphitheater_performance_space_v3', 'performance-amphitheater-industrial-adaptive-v3'),
  skin('stormwater_retention_pond', 'stormwater_retention_pond_v1', 'stormwater-formal-reflecting-v1'),
  skin('stormwater_retention_pond', 'stormwater_retention_pond_v2', 'stormwater-contemporary-interactive-v2'),
  skin('stormwater_retention_pond', 'stormwater_retention_pond_v3', 'stormwater-ecological-wetland-v3'),
  skin('canal_waterway', 'canal_waterway_v0', 'canal-naturalistic-v0'),
  skin('canal_waterway', 'canal_waterway_v1', 'canal-formal-reflecting-v1'),
  skin('canal_waterway', 'canal_waterway_v2', 'canal-contemporary-interactive-v2'),
  skin('custom_parks_plazas', 'custom_parks_plazas_v0', 'custom-eclectic-mixed-use-v0'),
  skin('custom_parks_plazas', 'custom_parks_plazas_v2', 'custom-tech-smart-v2'),
  skin('custom_parks_plazas', 'custom_parks_plazas_v3', 'custom-heritage-adaptive-v3'),
  skin('nature_preserve', 'nature_preserve_v0', 'nature-preserve-wetland-boardwalk-v0'),
  skin('nature_preserve', 'nature_preserve_v2', 'nature-preserve-coastal-dune-v2'),
  skin('nature_preserve', 'nature_preserve_v3', 'nature-preserve-old-growth-v3'),
  skin('riverfront_park_beach', 'riverfront_park_beach_v0', 'riverfront-urban-river-beach-v0'),
  skin('riverfront_park_beach', 'riverfront_park_beach_v2', 'riverfront-adventure-pier-v2'),
  skin('riverfront_park_beach', 'riverfront_park_beach_v3', 'riverfront-naturalized-v3'),
  skin('street_plaza_parklet', 'street_plaza_parklet_v0', 'parklet-nyc-street-plaza-v0'),
  skin('street_plaza_parklet', 'street_plaza_parklet_v2', 'parklet-tactical-urbanism-v2'),
  skin('street_plaza_parklet', 'street_plaza_parklet_v3', 'parklet-european-pocket-v3'),
]);

export const batch22ParkSkinForSelection = (archetypeId: string, variantId: string): Batch22ParkSkinDefinition | null => (
  BATCH22_PARK_SKINS.find((candidate) => candidate.archetypeId === archetypeId && candidate.variantId === variantId) ?? null
);
