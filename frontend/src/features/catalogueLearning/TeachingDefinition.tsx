import { planningDefinition, styleDefinition, TEACHING_SOURCES } from './teaching';
import { eraDefinition } from './planningHistory';

export function TeachingSources({ sourceIds }: {sourceIds:string[]}) {
  const sources=[...new Set(sourceIds)].map(id=>TEACHING_SOURCES[id]).filter(Boolean);
  if (!sources.length) return null;
  return <details className="text-[11px] text-slate-600">
    <summary className="min-h-8 cursor-pointer py-1 font-semibold">Learn more / sources</summary>
    <ul className="space-y-1 pb-1">
      {sources.map(source=><li key={source.url}><a href={source.url} target="_blank" rel="noreferrer"
        className="inline-flex min-h-8 items-center underline">{source.label}</a></li>)}
    </ul>
  </details>;
}

export function TeachingDefinition({ kind, id, regionLabel, showSources=true }: {
  kind:'style'|'planning'|'era'; id:string; regionLabel?:string; showSources?:boolean;
}) {
  const era=kind==='era' ? eraDefinition(id) : undefined;
  const definition=kind==='style' ? styleDefinition(id) : kind==='planning' ? planningDefinition(id) : era;
  if (!definition) return null;
  const planning=kind==='planning' ? planningDefinition(id) : undefined;
  return <section aria-label={regionLabel} className="space-y-1 rounded-lg border border-lime-300 bg-lime-50 p-3 text-xs leading-relaxed text-slate-800">
    <h4 className="font-bold text-slate-950">{definition.label}</h4>
    {era && <p className="font-semibold">{era.dates} · Approximate design association</p>}
    <p>{definition.description}</p>
    <p><strong>Main idea:</strong> {definition.designIdea}</p>
    {planning && <p className="text-[11px] text-slate-600">Components to explore. {planning.componentLimit}</p>}
    {showSources && <TeachingSources sourceIds={definition.sourceIds} />}
  </section>;
}
