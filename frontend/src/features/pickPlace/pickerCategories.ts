import type { CatalogueDomain } from '@/features/calgaryCatalogue/guide';
import type { CanonicalChoice } from './canonicalCatalogue';

/** Student browsing groups only: these never change geometry or district metadata. */
export const PICKER_CATEGORIES = [
  { id: 'low-density', domain: 'building', label: 'Low density', groups: ['detached', 'two_home'] },
  { id: 'townhomes', domain: 'building', label: 'Townhomes & rowhouses', groups: ['ground_housing'] },
  { id: 'apartments', domain: 'building', label: 'Apartments & mixed use', groups: ['apartments', 'mixed'] },
  { id: 'towers', domain: 'building', label: 'Towers', groups: ['towers'] },
  { id: 'workplaces', domain: 'building', label: 'Shops & workplaces', groups: ['shops', 'offices', 'hotels'] },
  { id: 'civic', domain: 'building', label: 'Civic & culture', groups: ['civic'] },
  { id: 'industry', domain: 'building', label: 'Industry & infrastructure', groups: ['industry', 'indoor_food', 'infrastructure', 'building_other'] },
  { id: 'gardens', domain: 'park_plaza', label: 'Gardens', groups: ['gardens'] },
  { id: 'play-sport', domain: 'park_plaza', label: 'Play & sport', groups: ['play_sport'] },
  { id: 'community-parks', domain: 'park_plaza', label: 'Community parks', groups: ['small_park', 'neighbourhood', 'regional', 'space_other'] },
  { id: 'nature-trails', domain: 'park_plaza', label: 'Nature & trails', groups: ['nature', 'linear'] },
  { id: 'plazas-water', domain: 'park_plaza', label: 'Plazas & water', groups: ['plazas', 'water'] },
  { id: 'neighbourhood-streets', domain: 'street_pathway', label: 'Neighbourhood streets', groups: ['local', 'calming'] },
  { id: 'boulevards', domain: 'street_pathway', label: 'Boulevards & bridges', groups: ['collector', 'arterial', 'intersection', 'street_other'] },
  { id: 'walking-cycling', domain: 'street_pathway', label: 'Walking & cycling', groups: ['active'] },
  { id: 'transit', domain: 'street_pathway', label: 'Transit', groups: ['transit'] },
  { id: 'alleys', domain: 'street_pathway', label: 'Alleys & mews', groups: ['alley'] },
] satisfies { id: string; domain: CatalogueDomain; label: string; groups: string[] }[];

// Exact forms whose authored program is more specific than the inherited guide.
const VARIANT_CATEGORY: Record<string, string> = {
  clapboard_north_end: 'low-density',
  glass_tower_blue_reflective: 'towers',
  art_deco_cream_terracotta: 'towers',
  art_deco_streamline_moderne: 'apartments',
  market_historic_iron_glass: 'workplaces',
  brewery_crystal_brewhouse: 'workplaces',
  deco_theater_movie_palace: 'civic',
  student_pickleball_garden_v1: 'play-sport',
  student_tennis_garden_v2: 'play-sport',
  student_bocce_garden_v2: 'play-sport',
  student_urban_splash_plaza_v1: 'play-sport',
  student_sheltered_dog_park_v1: 'play-sport',
  inclusive_accessible_playground_v0: 'play-sport',
  student_neighbourhood_orchard_v1: 'community-parks',
  amphitheater_lawn_v0: 'community-parks',
  wetland_rain_garden_v0: 'nature-trails',
  student_woodland_stream_garden_v1: 'nature-trails',
  linear_park_greenway_v0: 'nature-trails',
  student_reflecting_fountain_garden_v1: 'plazas-water',
  student_terraced_cafe_court_v1: 'plazas-water',
  student_garden_square_v1: 'plazas-water',
  student_quiet_residential_street_v1: 'neighbourhood-streets',
  student_school_street_v1: 'neighbourhood-streets',
  student_green_alley_v1: 'alleys',
  student_london_cobbled_mews_v1: 'alleys',
  student_cherry_blossom_street_v1: 'neighbourhood-streets',
  student_market_street_v1: 'walking-cycling',
  student_planted_shared_lane_v1: 'walking-cycling',
};

export function pickerCategory(choice: CanonicalChoice): string {
  const asset = choice.placements[0];
  const override = VARIANT_CATEGORY[asset?.model.variantId ?? ''];
  if (override) return override;
  const guideGroup = asset?.calgaryGuide.groupId ?? choice.option.calgaryGuide?.groupId ?? '';
  const nativeStoreys = asset?.kind === 'object' ? asset.storeyProgram?.nativeStoreys ?? Number(asset.properties.floors ?? 0) : 0;
  if (choice.domain === 'building' && nativeStoreys >= 12) return 'towers';
  return PICKER_CATEGORIES.find(category => category.domain === choice.domain && category.groups.includes(guideGroup))?.id
    ?? ({ building: 'industry', park_plaza: 'community-parks', street_pathway: 'boulevards' }[choice.domain]);
}

export function availablePickerCategories(domain: CatalogueDomain, choices: CanonicalChoice[]) {
  const available = new Set(choices.filter(choice => choice.domain === domain).map(pickerCategory));
  return PICKER_CATEGORIES.filter(category => category.domain === domain && available.has(category.id));
}
