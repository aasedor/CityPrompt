/** Educational browsing metadata, never a parcel permission or geometry preset.
 * Reviewed against City sources on 2026-09-05. See docs/CALGARY_CATALOGUE_GUIDE.md.
 */
export type CatalogueDomain = 'building' | 'park_plaza' | 'street_pathway';
export const CALGARY_GUIDE_REVIEWED = '2026-09-05';
export const CALGARY_SOURCES = {
  lowDensity: { label: 'Land Use Bylaw · low density housing', url: 'https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html?part=5', status: 'Bylaw · includes August 2026 amendments' },
  apartments: { label: 'Land Use Bylaw · multi-residential', url: 'https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html?part=6', status: 'Bylaw' },
  districts: { label: 'Calgary land use districts', url: 'https://www.calgary.ca/planning/land-use/districts.html', status: 'City district summaries' },
  useGroups: { label: 'Land Use Bylaw · groups of uses', url: 'https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html?div=A&part=S', status: 'Schedule A · activities, separate from districts' },
  hotelUse: { label: 'Hotel · defined use', url: 'https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html?alphaSearch=209&div=2&part=4', status: 'Part 4 · section 209' },
  foodProduction: { label: 'Food Production · defined use', url: 'https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html?alphaSearch=198.1&div=2&part=4', status: 'Part 4 · section 198.1' },
  streets: { label: 'Complete Streets Policy & Guide', url: 'https://www.calgary.ca/planning/transportation/complete-streets.html', status: 'Council approved · 2014' },
  streetManual: { label: 'Street Manual', url: 'https://www.calgary.ca/planning/city-building-program/city-building-program/the-street-manual.html', status: 'Draft · final approval anticipated Q2 2027' },
  parks: { label: 'Connect: Calgary’s Parks Plan', url: 'https://www.calgary.ca/planning/parks-rec/parks-plan.html', status: 'Council approved · May 2025' },
  parkTypes: { label: 'Parks Plan · park types and connections', url: 'https://www.calgary.ca/content/dam/www/programs-services/city-planning/parks-projects-and-developments/parks-plan.pdf', status: 'Connect · sections 4.4–4.5' },
  localPlans: { label: 'Local area plans', url: 'https://www.calgary.ca/planning/local-area/resources.html', status: 'Check the plan that covers your site' },
  specifications: { label: 'City design guides and specifications', url: 'https://www.calgary.ca/planning/publications.html', status: 'Includes landscape construction 2026 and subdivision servicing 2020' },
} as const;
type SourceId = keyof typeof CALGARY_SOURCES;
export interface CalgaryGroup {
  id: string;
  domain: CatalogueDomain;
  label: string;
  /** District examples to investigate, not an exhaustive compatibility matrix. */
  districts: string[];
  note: string;
  sources: SourceId[];
}
function group(id: string, domain: CatalogueDomain, label: string, districts: string[], note: string, sources: SourceId[]): CalgaryGroup {
  return { id, domain, label, districts, note, sources };
}
export const CALGARY_GROUPS: CalgaryGroup[] = [
  group('detached', 'building', 'Detached homes', ['R-C1', 'R-C1N', 'R-1', 'R-CG'], 'Single detached house forms. R-C1 is one district to investigate; a collection of houses also needs a parcel and access strategy.', ['lowDensity']),
  group('two_home', 'building', 'Duplexes & semi-detached homes', ['R-C2', 'R-2', 'R-CG'], 'Check how the bylaw defines your chosen dwelling arrangement.', ['lowDensity']),
  group('ground_housing', 'building', 'Rowhouses & townhomes', ['R-CG', 'H-GO', 'M-CG', 'M-G'], 'Homes with access from ground level. The district and site rules depend on the arrangement and context.', ['lowDensity', 'apartments', 'districts']),
  group('apartments', 'building', 'Apartments', ['M-C1', 'M-C2', 'M-1', 'M-2', 'M-H1', 'M-H2'], 'Explore multi-residential districts according to height, density and location.', ['apartments']),
  group('towers', 'building', 'Residential towers', ['M-H2', 'M-H3'], 'A tower form needs a district and site-specific scale review.', ['apartments']),
  group('mixed', 'building', 'Homes over shops & mixed use', ['MU-1', 'MU-2', 'C-COR1'], 'Consider the ground-floor uses and how entrances meet the street. MU-2 has active commercial frontage requirements.', ['districts']),
  group('shops', 'building', 'Shops & services', ['C-N1', 'C-N2', 'C-C1', 'C-C2', 'C-COR2'], 'These are commercial district starting points. The individual use, size and location need review.', ['districts']),
  group('hotels', 'building', 'Hotels & visitor accommodation', ['C-C2', 'C-COR1', 'C-COR2', 'MU-1', 'MU-2'], 'Hotel belongs to the bylaw’s Residential Group. That use group is separate from a parcel’s district. Check room count, neighbouring uses and any restaurant component.', ['hotelUse', 'useGroups', 'districts']),
  group('offices', 'building', 'Offices', ['C-O', 'C-COR2'], 'Explore office and corridor districts, including their site-specific limits.', ['districts']),
  group('civic', 'building', 'Schools, civic & recreation', ['S-CI', 'S-CS', 'S-SPR', 'S-R'], 'Public, private and reserve-land facilities have different district requirements. A civic appearance does not decide the designation.', ['districts']),
  group('industry', 'building', 'Industry & warehouses', ['I-G', 'I-B', 'I-H'], 'Match the actual industrial activity and its impacts to a district.', ['districts']),
  group('indoor_food', 'building', 'Indoor farms & food production', [], 'Food Production covers growing food inside a building, including vertical growing and hydroponics, within the General Industrial Group. Confirm the operation and parcel district; outdoor growing needs its own use review.', ['foodProduction', 'useGroups', 'districts']),
  group('infrastructure', 'building', 'Transit & utilities', ['S-CRI', 'S-TUC'], 'Infrastructure has its own ownership, servicing and approval context.', ['districts']),
  group('building_other', 'building', 'Other building ideas', [], 'Custom and unusual concepts remain available. Start with the intended use and relevant local plan.', ['districts', 'localPlans']),
  group('small_park', 'park_plaza', 'Pocket & sub-neighbourhood parks', [], 'Small local spaces complement the wider park network. This is a design grouping, not an automatic official park designation.', ['parks', 'parkTypes']),
  group('neighbourhood', 'park_plaza', 'Neighbourhood & community parks', [], 'A local destination for everyday play, gathering and green space. Legacy community-park assets are included here for browsing.', ['parks', 'parkTypes']),
  group('regional', 'park_plaza', 'Regional & destination parks', [], 'Larger park concepts with a wider catchment. Size alone does not establish an official park classification.', ['parks', 'parkTypes']),
  group('linear', 'park_plaza', 'Linear parks & green connections', [], 'Connect green spaces and nearby destinations with useful walking and wheeling routes.', ['parkTypes', 'streets']),
  group('nature', 'park_plaza', 'Natural areas & restoration', ['S-UN'], 'Protect or restore ecological systems. S-UN is a district to investigate for land kept in a natural state.', ['parks', 'districts']),
  group('plazas', 'park_plaza', 'Plazas & gathering places', [], 'Connect the gathering space to surrounding uses and pedestrian routes. Public access and land ownership need separate consideration.', ['parkTypes']),
  group('play_sport', 'park_plaza', 'Play & sport amenities', [], 'Courts, play areas and sports facilities are park amenities; their presence does not define the park’s service area.', ['parks', 'specifications']),
  group('gardens', 'park_plaza', 'Gardens & quiet spaces', [], 'Planting, food growing and quiet recreation can support several park types.', ['parks', 'specifications']),
  group('water', 'park_plaza', 'Waterfront & stormwater spaces', [], 'Water, drainage and recreation need coordinated design. A drawn pond is not a validated drainage system.', ['parks', 'specifications']),
  group('space_other', 'park_plaza', 'Parking, special sites & custom spaces', [], 'Parking and transport sites remain separate from park types, even where the legacy catalogue stored them with plazas.', ['districts', 'specifications']),
  group('local', 'street_pathway', 'Local & residential streets', [], 'Choose a street role, then consider access, sidewalks, trees and its relationship to the buildings.', ['streets', 'streetManual']),
  group('collector', 'street_pathway', 'Collector streets', [], 'Connect local streets to the wider network while considering people walking, wheeling and taking transit.', ['streets', 'streetManual']),
  group('arterial', 'street_pathway', 'Arterial & major streets', [], 'Larger movement corridors need context-specific crossing and frontage design.', ['streets', 'streetManual']),
  group('alley', 'street_pathway', 'Alleys & service lanes', [], 'Consider rear access, servicing and pedestrian connections.', ['streets', 'streetManual']),
  group('active', 'street_pathway', 'Walking, wheeling & shared streets', [], 'Choose connected routes for walking and wheeling. International and Alberta references remain design inspiration.', ['streets']),
  group('transit', 'street_pathway', 'Transit corridors', [], 'Coordinate transit stops, access and nearby development.', ['streets']),
  group('intersection', 'street_pathway', 'Intersections & crossings', [], 'Check how each movement crosses or joins the street.', ['streets', 'streetManual']),
  group('calming', 'street_pathway', 'Traffic calming & safer streets', [], 'Explore measures that fit the street role and nearby activity.', ['streets', 'streetManual']),
  group('street_other', 'street_pathway', 'Other streets & global inspiration', [], 'These designs are references to adapt, not certified Calgary street sections.', ['streets']),
];
const GROUP_BY_ID = new Map(CALGARY_GROUPS.map(item => [item.id, item]));
export interface CalgaryClassification { groupId: string; basis: 'form_reference' | 'park_function' | 'draft_manual' | 'design_reference' }
export interface CatalogueSeed {
  id: string; developmentType?: string; developmentTypes?: string[]; aestheticCategory?: string; spaceType?: string;
}
// Reviewed parent-program/form corrections from the September 2 study.
// See docs/CALGARY_RESEARCH_RECONCILIATION_2026_09_05.md. These are browsing
// defaults, not legal use assignments; variants can change the actual program.
const BUILDING_OVERRIDES: Record<string, string> = {
  transit_oriented_station_block: 'mixed', transit_podium_residential: 'mixed',
  old_montreal_warehouse_loft: 'apartments', junction_converted_industrial_loft: 'mixed',
  vertical_farm: 'indoor_food', vertical_farm_indoor_agriculture: 'indoor_food',
  brownstone_rowhouse_frontage: 'ground_housing', classic_brownstone_streetwall: 'ground_housing',
  victorian_heritage_avenue: 'ground_housing', contemporary_townhouse_courtyard: 'ground_housing',
  vernacular_courtyard_housing: 'ground_housing', minimalist_infill_townhouse: 'ground_housing',
  victorian_bay_window_terrace: 'ground_housing', halifax_painted_clapboard_row: 'ground_housing',
  toronto_brick_rowhouse: 'ground_housing', brick_rowhouse_terrace: 'ground_housing',
  london_townhouse: 'ground_housing', london_crescent_terrace: 'ground_housing', regency_stucco_terrace: 'ground_housing',
  rndsqr_missing_middle_townhomes: 'ground_housing',
};
const BUILDING_TYPES: Record<string, string> = {
  residential_single_family: 'detached', residential_duplex: 'two_home', residential_multifamily: 'apartments',
  residential_highrise: 'towers', mixed_use: 'mixed', 'mixed-use': 'mixed', commercial_office: 'offices',
  commercial: 'shops', commercial_light: 'shops', commercial_retail: 'shops', hotel: 'hotels',
  institutional: 'civic', institutional_education: 'civic', institutional_health: 'civic',
  recreational: 'civic', recreational_centre: 'civic', sports_arena: 'civic',
  industrial: 'industry', industrial_light: 'industry', industrial_heavy: 'industry', industrial_warehouse: 'industry',
  transit_station: 'infrastructure', transit_hub: 'infrastructure', energy_infrastructure: 'infrastructure',
  energy_renewable: 'infrastructure', mobility_infrastructure: 'infrastructure',
};
const PARK_OVERRIDES: Record<string, string> = {
  neighborhood_park: 'neighbourhood', community_park: 'neighbourhood',
  urban_pocket_park: 'small_park', newyork_pocket_park: 'small_park', dog_park: 'play_sport',
  regional_park: 'regional', linear_park_greenway: 'linear', street_plaza_parklet: 'plazas',
  community_garden: 'gardens', community_garden_enhanced: 'gardens', newyork_community_garden: 'gardens',
  rooftop_garden: 'gardens', urban_orchard_food_forest: 'gardens',
  wetland_rain_garden: 'water', bioswale_rain_garden: 'water', stormwater_retention_pond: 'water',
  stormwater_naturalized_drainage_corridor: 'water', stormwater_resilience_park: 'water',
  swimming_pool_complex: 'play_sport', fountain_water_feature: 'water',
};
const STREET_OVERRIDES: Record<string, string> = {
  narrow_residential_street: 'local', suburban_residential_street: 'local', cul_de_sac: 'local', yield_street: 'local',
  calgary_local: 'local', calgary_local_industrial: 'local', collector_road: 'collector', calgary_collector: 'collector',
  calgary_local_high_activity: 'local', calgary_local_rural: 'local',
  calgary_collector_industrial: 'collector', calgary_collector_high_activity: 'collector',
  calgary_alley: 'alley', back_alley_service_lane: 'alley', green_alley: 'alley', commercial_alley_laneway: 'alley',
  arterial_boulevard: 'arterial', downtown_thoroughfare: 'arterial', highway_freeway: 'arterial', calgary_skeletal: 'arterial',
};
export function classifyCalgaryAsset(domain: CatalogueDomain, seed: CatalogueSeed): CalgaryClassification {
  if (domain === 'building') return {
    groupId: BUILDING_OVERRIDES[seed.id] ?? BUILDING_TYPES[seed.developmentType ?? seed.developmentTypes?.[0] ?? ''] ?? 'building_other',
    basis: 'form_reference',
  };
  const category = seed.aestheticCategory ?? '';
  if (domain === 'park_plaza') {
    const groupId = PARK_OVERRIDES[seed.id] ?? (
      ['parking_areas', 'transport_infrastructure', 'custom'].includes(category) ? 'space_other'
      : category === 'sports_recreation' ? 'play_sport'
      : category === 'water_features' || category === 'waterfront_spaces' ? 'water'
      : seed.spaceType === 'plaza' || category === 'social_event_spaces' ? 'plazas'
      : category === 'ecological_resilience' ? 'nature'
      : category === 'neighborhood_public_realm' ? 'play_sport'
      : category === 'landscape_parks' ? 'regional' : category ? 'gardens' : 'space_other');
    return { groupId, basis: 'park_function' };
  }
  const groupId = STREET_OVERRIDES[seed.id] ?? (
    seed.id.startsWith('calgary_arterial') || seed.id === 'calgary_urban_boulevard' ? 'arterial'
    : category === 'intersections' ? 'intersection'
    : category === 'traffic_safety_vision_zero' ? 'calming'
    : category === 'transit_oriented' ? 'transit'
    : ['cycling_oriented', 'pedestrian_oriented', 'alberta_bike_design_guide'].includes(category) ? 'active' : 'street_other');
  return { groupId, basis: category === 'calgary_street_manual' ? 'draft_manual' : 'design_reference' };
}
export function calgaryGroup(classification?: CalgaryClassification) {
  return classification ? GROUP_BY_ID.get(classification.groupId) : undefined;
}
export interface CalgaryBrowsable { label: string; calgaryGuide?: CalgaryClassification }
const SEARCH_ALIASES: Record<string, string[]> = {
  detached: ['single family', 'single detached', 'houses'],
  ground_housing: ['townhouses', 'row homes'],
  apartments: ['multi family', 'multifamily'],
  small_park: ['pocket park', 'subneighbourhood', 'subneighborhood'],
};
export const normalizeCatalogueSearch = (value: string) => value.toLocaleLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]/g, '');
export function filterCalgaryCatalogue<T extends CalgaryBrowsable>(options: T[], groupId: string, query: string): T[] {
  const needle = normalizeCatalogueSearch(query);
  return options.filter(option => {
    const definition = calgaryGroup(option.calgaryGuide);
    if (groupId && definition?.id !== groupId) return false;
    return !needle || [option.label, definition?.label ?? '', ...(definition?.districts ?? []), ...(SEARCH_ALIASES[definition?.id ?? ''] ?? [])]
      .some(value => normalizeCatalogueSearch(value).includes(needle));
  });
}
