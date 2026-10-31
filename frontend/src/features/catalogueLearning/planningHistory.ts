import data from '@/data/cataloguePlanningHistory.json';
import type { CanonicalChoice } from '@/features/pickPlace/canonicalCatalogue';
import type { CatalogueDomain } from '@/features/calgaryCatalogue/guide';
import { LOCAL_TEACHING_HISTORY } from '@/features/pickPlace/localTeachingBuildings';

export interface EraDefinition {
  label: string; dates: string; description: string; designIdea: string;
  canadianContext: string; internationalContext: string; sourceIds: string[]; searchTerms: string[];
}
export interface PlanningHistoryLesson {
  domain: string; archetypeId: string; variantId: string; modelMethod: string; modelRevision: string | null;
  status: string; formId: string; eraIds: string[]; designPeriod: string; eraRationale: string;
  canadianContext: string; internationalContext: string; sourceIds: string[];
  styleIds: string[]; planningIds: string[]; constructionYear: null;
}

const lessons: Readonly<Record<string, PlanningHistoryLesson>> = { ...data.lessons, ...LOCAL_TEACHING_HISTORY };
const eras: Readonly<Record<string, EraDefinition>> = data.eras;
// Plain labels for the authored use/form tags. These describe the component,
// never its ownership, occupancy agreement, provider or affordability.
const FORM_LABELS: Readonly<Record<string, string>> = {
  civic: 'Civic / community building',
  fourplex: 'Fourplex',
  single_family: 'Detached home',
  detached: 'Detached home',
  shops: 'Shop / commercial building',
  apartments: 'Apartment building',
  townhouse: 'Townhouse / rowhouse',
  gardens: 'Garden',
  neighbourhood: 'Neighbourhood park',
  plazas: 'Plaza / public square',
  linear: 'Linear park',
  local: 'Local street',
  transit: 'Transit corridor / facility',
  active: 'Walking / cycling route',
  street_other: 'Street / pathway component',
  mixed: 'Mixed-use building',
  play_sport: 'Play / sports space',
  duplex: 'Duplex',
  courtyard_frontage_component: 'Courtyard frontage component',
  office_tower: 'Office tower',
  residential_tower_podium: 'Residential tower and podium',
  alley: 'Lane / alley',
  arterial: 'Arterial street',
  offices: 'Office building',
  railway_station: 'Railway station',
  hotels: 'Hotel',
  water: 'Water / stormwater space',
  industry: 'Industrial building',
  courtyard_cluster: 'Courtyard housing cluster',
  cottage_court: 'Cottage court',
  stacked_townhouse: 'Stacked townhouses',
  lowrise_apartments: 'Low-rise apartment building',
  shop_and_home: 'Shop with housing above',
  midrise_apartments: 'Mid-rise apartment building',
  infrastructure: 'Infrastructure building',
  mixed_use_courtyard_block: 'Mixed-use courtyard block',
  parking_structure: 'Parking structure',
  parkades: 'Parking structure',
  adapted_mill: 'Adapted mill / mixed-use building',
  indoor_food: 'Indoor food-production building',
  towers: 'Residential tower',
  small_park: 'Small park',
  collector: 'Collector street',
};
export const formLabel = (id: string): string | undefined => FORM_LABELS[id];
export const HISTORY_STYLE_DEFINITIONS = data.styles;
export const HISTORY_PLANNING_DEFINITIONS = data.planning;
export const HISTORY_PLANNING_ORDER: readonly string[] = data.planningOrder;
export const HISTORY_SOURCES = data.sources;
export const eraDefinition = (id: string): EraDefinition | undefined => eras[id];

/** Dates describe reviewed design associations, never an inferred construction year. */
export function historyForChoice(choice: CanonicalChoice, variantId?: string): {
  status: 'classified' | 'review' | 'stale'; lesson: PlanningHistoryLesson;
} | undefined {
  const asset = variantId ? choice.placements.find(item => item.model.variantId === variantId) : choice.placements[0];
  if (!asset) return undefined;
  const lesson = lessons[asset.id];
  if (!lesson) return undefined;
  if (lesson.domain !== choice.domain || lesson.archetypeId !== choice.option.id
      || lesson.variantId !== asset.model.variantId || lesson.modelMethod !== asset.model.method
      || lesson.modelRevision !== (asset.model.revision ?? null)) return { status: 'stale', lesson };
  return { status: lesson.status === 'classified' ? 'classified' : 'review', lesson };
}

export function eraIds(choice: CanonicalChoice, variantId?: string): string[] {
  const match = historyForChoice(choice, variantId);
  return match?.status === 'classified' ? [...match.lesson.eraIds] : [];
}

export function availableEras(choices: CanonicalChoice[], domain: CatalogueDomain) {
  const ids = new Set(choices.filter(choice => choice.domain === domain).flatMap(choice => eraIds(choice)));
  return data.eraOrder.filter(id => ids.has(id)).map(id => ({ id, label: `${eras[id].label} · ${eras[id].dates}` }));
}

export function historySearchTerms(choice: CanonicalChoice): string[] {
  const match = historyForChoice(choice);
  if (match?.status !== 'classified') return [];
  return [formLabel(match.lesson.formId) ?? '', match.lesson.designPeriod, ...match.lesson.eraIds.flatMap(id => {
    const era = eras[id];
    return era ? [era.label, era.dates, ...era.searchTerms] : [];
  })];
}
