import data from '@/data/cataloguePlanningHistory.json';
import type { CanonicalChoice } from '@/features/pickPlace/canonicalCatalogue';
import type { CatalogueDomain } from '@/features/calgaryCatalogue/guide';

export interface EraDefinition {
  label: string; dates: string; description: string; designIdea: string;
  canadianContext: string; internationalContext: string; sourceIds: string[]; searchTerms: string[];
}
export interface PlanningHistoryLesson {
  domain: string; archetypeId: string; variantId: string; modelMethod: string; modelRevision: string | null;
  status: string; eraIds: string[]; designPeriod: string; eraRationale: string;
  canadianContext: string; internationalContext: string; sourceIds: string[];
  styleIds: string[]; planningIds: string[]; constructionYear: null;
}

const lessons: Readonly<Record<string, PlanningHistoryLesson>> = data.lessons;
const eras: Readonly<Record<string, EraDefinition>> = data.eras;
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
  return [match.lesson.designPeriod, ...match.lesson.eraIds.flatMap(id => {
    const era = eras[id];
    return era ? [era.label, era.dates, ...era.searchTerms] : [];
  })];
}
