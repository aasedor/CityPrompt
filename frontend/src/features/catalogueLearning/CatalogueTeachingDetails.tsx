import type { CanonicalChoice } from '@/features/pickPlace/canonicalCatalogue';
import { lessonForChoice, planningDefinition, styleDefinition } from './teaching';
import { TeachingDefinition, TeachingSources } from './TeachingDefinition';

export function CatalogueTeachingDetails({ choice, variantId }: {choice:CanonicalChoice;variantId:string}) {
  const match=lessonForChoice(choice,variantId);
  if (!match) return null;
  const {lesson,status}=match;
  const label=choice.domain==='building' ? 'Architecture and planning' : 'Design and planning';
  if (status!=='classified') return <section aria-label={label} className="rounded-lg border border-slate-300 bg-white p-3 text-xs text-slate-700">
    <p className="font-bold">Style to be confirmed</p>
    <p className="mt-1">{status==='stale' ? 'This version needs a fresh review before its style is taught.'
      : 'The current reference and description need checking before a specific style is taught.'}</p>
  </section>;
  const definitions=lesson.styleIds.map(id=>styleDefinition(id)).filter(definition=>definition!==undefined);
  const planning=lesson.planningIds.map(id=>planningDefinition(id)).filter(definition=>definition!==undefined);
  return <section aria-label={label} className="space-y-2">
    <p className="text-xs text-slate-700"><strong>Use:</strong> {lesson.typeLabel}</p>
    {lesson.styleIds[0] && <TeachingDefinition kind="style" id={lesson.styleIds[0]} showSources={false} />}
    {definitions.length>1 && <p className="text-[11px] text-slate-600">Other influences: {definitions.slice(1).map(definition=>definition.label).join(' · ')}</p>}
    {planning.length>0 && <p className="text-[11px] text-slate-600"><strong>Planning connections:</strong> {planning.map(definition=>definition.label).join(' · ')}. Components only; the neighbourhood layout matters.</p>}
    {!lesson.referenceReviewed && <p className="text-[11px] text-slate-600">Suggested from this design's catalogue description.</p>}
    <TeachingSources sourceIds={[...definitions,...planning].flatMap(definition=>definition.sourceIds)} />
  </section>;
}
