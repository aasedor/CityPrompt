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
  { id: 'street-manual', domain: 'street_pathway', label: 'Street Manual', groups: [] },
  { id: 'neighbourhood-streets', domain: 'street_pathway', label: 'Neighbourhood streets', groups: ['local', 'calming'] },
  { id: 'boulevards', domain: 'street_pathway', label: 'Boulevards & bridges', groups: ['collector', 'arterial', 'intersection', 'street_other'] },
  { id: 'walking-cycling', domain: 'street_pathway', label: 'Walking & cycling', groups: ['active'] },
  { id: 'transit', domain: 'street_pathway', label: 'Transit', groups: ['transit'] },
  { id: 'alleys', domain: 'street_pathway', label: 'Alleys & mews', groups: ['alley'] },
] satisfies { id: string; domain: CatalogueDomain; label: string; groups: string[] }[];

export function pickerCategory(choice: CanonicalChoice): string {
  const asset = choice.placements[0];
  if (asset?.model.method === 'manual_metric_section_v1') return 'street-manual';
  const guideGroup = asset?.calgaryGuide.groupId ?? choice.option.calgaryGuide?.groupId ?? '';
  return PICKER_CATEGORIES.find(category => category.domain === choice.domain && category.groups.includes(guideGroup))?.id
    ?? ({ building: 'industry', park_plaza: 'community-parks', street_pathway: 'boulevards' }[choice.domain]);
}

export function availablePickerCategories(domain: CatalogueDomain, choices: CanonicalChoice[]) {
  const available = new Set(choices.filter(choice => choice.domain === domain).map(pickerCategory));
  return PICKER_CATEGORIES.filter(category => category.domain === domain && available.has(category.id));
}
