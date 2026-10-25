import data from '@/data/catalogueTeaching.json';
import type { CanonicalChoice } from '@/features/pickPlace/canonicalCatalogue';
import type { CatalogueDomain } from '@/features/calgaryCatalogue/guide';

export interface TeachingDefinition {
  label: string; description: string; designIdea: string; sourceIds: string[];
}
export interface PlanningDefinition extends TeachingDefinition { componentLimit: string }
export interface CatalogueLesson {
  domain: string; archetypeId: string; variantId: string; modelRevision: string | null;
  modelMethod: string; typeLabel: string; styleIds: string[]; planningIds: string[];
  confidence: string; referenceReviewed: boolean; rationale: string;
}
export interface LessonMatch { status: 'classified' | 'review' | 'stale'; lesson: CatalogueLesson }

const lessons: Readonly<Record<string, CatalogueLesson>> = data.lessons;
const styles: Readonly<Record<string, TeachingDefinition>> = data.styles;
const planning: Readonly<Record<string, PlanningDefinition>> = data.planning;
export const TEACHING_SOURCES: Readonly<Record<string, {label:string;url:string}>> = data.sources;
export const INTRODUCTORY_PLANNING_IDS: readonly string[] = data.introductoryPlanningIds;

const styleAlias = (id: string) => id === 'nordic' ? 'scandinavian_nordic' : id;
export const styleDefinition = (id: string): TeachingDefinition | undefined =>
  styles[id === 'scandinavian_nordic' ? 'nordic' : id];
export const planningDefinition = (id: string): PlanningDefinition | undefined => planning[id];

/** Teaching attaches to an exact asset contract, never to a parent or name. */
export function lessonForChoice(choice: CanonicalChoice, variantId?: string): LessonMatch | undefined {
  const asset = variantId ? choice.placements.find(item => item.model.variantId === variantId) : choice.placements[0];
  if (!asset) return undefined;
  const lesson = lessons[asset.id];
  if (!lesson) return undefined;
  if (lesson.domain !== choice.domain || lesson.archetypeId !== choice.option.id
      || lesson.variantId !== asset.model.variantId || lesson.modelMethod !== asset.model.method
      || lesson.modelRevision !== (asset.model.revision ?? null)) return {status:'stale', lesson};
  return {status:lesson.confidence === 'Review' ? 'review' : 'classified',lesson};
}

/** Undefined preserves authored fallback for a genuinely unclassified future asset.
 * An empty array deliberately withholds a held/stale record's old style. */
export function teachingStyleIds(choice: CanonicalChoice, variantId?: string): string[] | undefined {
  const match = lessonForChoice(choice, variantId);
  if (!match) return undefined;
  return match.status === 'classified' ? [...new Set(match.lesson.styleIds.map(styleAlias))] : [];
}

export function planningIds(choice: CanonicalChoice, variantId?: string): string[] {
  const match = lessonForChoice(choice, variantId);
  return match?.status === 'classified' ? [...match.lesson.planningIds] : [];
}

export function availablePlanningIdeas(choices: CanonicalChoice[], domain: CatalogueDomain) {
  const ids = new Set(choices.filter(choice => choice.domain === domain).flatMap(choice => planningIds(choice)));
  return INTRODUCTORY_PLANNING_IDS.filter(id => ids.has(id)).map(id => ({id,label:planning[id].label}));
}

export function teachingSearchTerms(choice: CanonicalChoice): string[] {
  const match = lessonForChoice(choice);
  if (match?.status !== 'classified') return [];
  return [...match.lesson.styleIds.map(id => styleDefinition(id)?.label ?? ''),
    ...planningIds(choice).map(id => planningDefinition(id)?.label ?? '')];
}
