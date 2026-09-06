import type { PlaceAsset } from './assetRegistry';

/** Human-activated RLASM 6.1 buildings. Stable IDs preserve existing trial projects. */
export const PUBLISHED_BUILDING_ASSETS: PlaceAsset[] = [
  {
    id: 'trial_postwar_bungalow', kind: 'object', definitionVersion: 1, readiness: 'ready',
    label: 'Post-war bungalow', description: 'One-storey brick home with a sheltered porch.',
    thumbnail: '/archetypes/buildings/calgary-inner-city-bungalow/variant_2.png',
    model: { variantId: 'bungalow_postwar_ranch', revision: 'clay-v005-2026-09-06', method: 'RLASM 6.1' },
    calgaryGuide: { groupId: 'detached', basis: 'form_reference' }, zoneType: 'building',
    reshapeMode: 'repeat_native', width: 15, depth: 20, minWidth: 15, minDepth: 20, maxSize: 100,
    nativeDimensions: [10.899, 16.05, 6.36],
    reshapeDescription: 'Widen the plot to add complete houses. Each house keeps its authored proportions.',
    properties: { building_archetype_id: 'calgary_inner_city_bungalow', development_archetype_id: 'calgary_inner_city_bungalow', development_selected_variant_id: 'bungalow_postwar_ranch', development_archetype_label: 'Post-war bungalow', native_home_plot: true, floors: 1, floor_count: 1 },
  },
  {
    id: 'trial_edwardian_foursquare', kind: 'object', definitionVersion: 1, readiness: 'ready',
    label: 'Edwardian Foursquare', description: 'Two-storey brick home with a porch and dormer.',
    thumbnail: '/archetypes/buildings/toronto-edwardian-foursquare/variant_0.png',
    model: { variantId: 'toronto_foursquare_red_brick', revision: 'clay-v004-2026-09-06', method: 'RLASM 6.1' },
    calgaryGuide: { groupId: 'detached', basis: 'form_reference' }, zoneType: 'building',
    reshapeMode: 'repeat_native', width: 15, depth: 22, minWidth: 15, minDepth: 22, maxSize: 100,
    nativeDimensions: [11.07, 17.93, 10.81],
    reshapeDescription: 'Widen the plot to add complete houses. The porch, dormer and two storeys keep their proportions.',
    properties: { building_archetype_id: 'toronto_edwardian_foursquare', development_archetype_id: 'toronto_edwardian_foursquare', development_selected_variant_id: 'toronto_foursquare_red_brick', development_archetype_label: 'Edwardian Foursquare', native_home_plot: true, floors: 2, floor_count: 2 },
  },
  {
    id: 'trial_sandstone_civic', kind: 'object', definitionVersion: 1, readiness: 'ready',
    label: 'Sandstone civic hall', description: 'Courtyard institution with an arched facade and clock tower.',
    thumbnail: '/archetypes/buildings/calgary-sandstone-heritage/variant_0.png',
    model: { variantId: 'sandstone_romanesque_revival', revision: 'clay-v007-2026-09-06', method: 'RLASM 6.1' },
    calgaryGuide: { groupId: 'civic', basis: 'form_reference' }, zoneType: 'building',
    reshapeMode: 'fixed_native', width: 64, depth: 66, minWidth: 64, minDepth: 66, maxSize: 100,
    nativeDimensions: [59.41, 60.01, 44],
    reshapeDescription: 'A complete landmark at its authored size. Move or rotate it; the courtyard and tower retain their proportions.',
    properties: { building_archetype_id: 'calgary_sandstone_heritage', development_archetype_id: 'calgary_sandstone_heritage', development_selected_variant_id: 'sandstone_romanesque_revival', development_archetype_label: 'Sandstone civic hall', floors: 3, floor_count: 3 },
  },
];
