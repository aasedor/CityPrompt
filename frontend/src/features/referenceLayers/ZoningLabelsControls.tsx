import { useMemo } from 'react';
import { ChevronDown, ExternalLink, Map as MapIcon } from 'lucide-react';
import { ZONING_SOURCE } from './zoningLabels';
import type { ZoningLabelsState } from './useZoningLabels';

export function ZoningLabelsControls({ state }: { state: ZoningLabelsState }) {
  const guide = useMemo(() => {
    const entries = new Map<string, { label: string; description: string }>();
    for (const district of state.data?.districts ?? []) {
      const description = district.description || 'Description not supplied by Calgary.';
      entries.set(JSON.stringify([district.label, description]), { label: district.label, description });
    }
    return [...entries.entries()].sort(([, a], [, b]) => a.label.localeCompare(b.label));
  }, [state.data]);
  return <section aria-label="Land use" className="max-w-sm space-y-3 rounded-2xl border border-[#151515]/20 bg-[#fffdf6]/95 p-3 text-[#151515] shadow-lg backdrop-blur-sm">
    <header className="flex items-center gap-2.5">
      <span aria-hidden="true" className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl border border-[#151515]/15 bg-[#c9ff3d]"><MapIcon size={17} strokeWidth={1.8} /></span>
      <div><h3 className="text-sm font-bold">Land use</h3><p className="text-[10px] font-semibold uppercase tracking-widest text-[#5c554d]">Calgary zoning</p></div>
    </header>
    <label className={`flex min-h-11 items-center justify-between gap-3 rounded-xl border border-[#151515]/10 bg-white/80 px-3 py-2 text-xs font-semibold ${state.problem ? 'cursor-not-allowed opacity-60' : 'cursor-pointer hover:bg-[#f5f8ec]'}`}>
      Show zoning codes
      <span className="relative inline-flex shrink-0">
        <input type="checkbox" className="peer absolute inset-0 z-10 h-full w-full cursor-pointer opacity-0 disabled:cursor-not-allowed" checked={state.labels} disabled={Boolean(state.problem)} onChange={state.toggle} />
        <span aria-hidden="true" className="h-6 w-10 rounded-full border border-[#151515]/25 bg-stone-200 transition-colors peer-checked:bg-[#c9ff3d] peer-focus-visible:outline peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-[#151515] motion-reduce:transition-none" />
        <span aria-hidden="true" className="pointer-events-none absolute left-1 top-1 h-4 w-4 rounded-full bg-[#151515] transition-transform peer-checked:translate-x-4 motion-reduce:transition-none" />
      </span>
    </label>
    <p className="text-[11px] leading-relaxed text-[#5c554d]">{state.problem ?? 'Visual reference only. Your site and design stay unchanged.'}</p>
    {state.labels && !state.problem && <>
      {state.loading && <p role="status" className="text-xs">Loading Calgary zoning…</p>}
      {state.error && <div role="alert" className="rounded-xl border border-amber-200 bg-amber-50 p-2 text-xs text-amber-950"><p>{state.error.message}</p><button className="min-h-11 font-semibold underline underline-offset-2" onClick={state.retry}>Retry zoning data</button></div>}
      {state.data && <p role="status" className="text-xs font-semibold">{state.data.districts.length ? `${state.data.districts.length} zoning areas` : 'No published zoning areas intersect this boundary.'}</p>}
      <p className="text-[11px] leading-relaxed text-[#5c554d]">Codes label the land-use areas within your site. Zoom in to read more labels.</p>
      {guide.length > 0 && <details className="group rounded-xl border border-[#151515]/15 bg-white/80">
        <summary className="flex min-h-11 cursor-pointer list-none items-center justify-between gap-2 rounded-xl px-3 py-2 text-xs font-semibold hover:bg-[#f5f8ec] focus-visible:outline focus-visible:outline-2 focus-visible:outline-[#151515] [&::-webkit-details-marker]:hidden"><span>Code guide ({guide.length})</span><ChevronDown aria-hidden="true" size={15} className="shrink-0 group-open:rotate-180" /></summary>
        <dl aria-label="Zoning code guide" tabIndex={0} className="max-h-52 divide-y divide-[#151515]/10 overflow-y-auto overscroll-contain border-t border-[#151515]/10 px-3 text-xs focus-visible:outline focus-visible:outline-2 focus-visible:outline-[#151515]">
          {guide.map(([key, entry]) => <div key={key} className="py-3">
            <dt className="inline-flex max-w-full items-center gap-1.5 rounded-lg bg-[#151918] px-2 py-1.5 text-[11px] font-semibold text-[#fff9ec]"><span aria-hidden="true" className="h-1.5 w-1.5 shrink-0 rounded-full bg-[#c9ff3d]" /><span className="break-all">{entry.label}</span></dt>
            <dd className="mt-1.5 leading-relaxed text-[#5c554d]">{entry.description}</dd>
          </div>)}
        </dl>
      </details>}
      <a className="flex min-h-11 items-center gap-2 border-t border-[#151515]/10 pt-2 text-[10px] leading-relaxed text-[#5c554d] underline decoration-[#151515]/30 underline-offset-2 hover:text-[#151515]" href={ZONING_SOURCE} target="_blank" rel="noreferrer"><span>Calgary land-use districts{state.data ? ` · loaded ${state.data.loadedAt.slice(0, 10)}` : ''}</span><ExternalLink aria-hidden="true" size={12} className="shrink-0" /></a>
    </>}
  </section>;
}
