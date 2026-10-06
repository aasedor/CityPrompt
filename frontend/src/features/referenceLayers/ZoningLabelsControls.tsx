import { useMemo } from 'react';
import { ChevronDown, ExternalLink, Map as MapIcon } from 'lucide-react';
import { ZONING_SOURCE } from './zoningLabels';
import { zoningColor } from './zoningAppearance';
import type { ZoningLabelsState } from './useZoningLabels';

export function ZoningLabelsControls({ state, onInspect }: { state: ZoningLabelsState; onInspect?: (id: string) => void }) {
  const guide = useMemo(() => {
    const entries = new Map<string, { id: string; label: string; description: string; color: string }>();
    for (const district of state.data?.districts ?? []) {
      const description = district.description || 'Description not supplied by Calgary.';
      entries.set(JSON.stringify([district.label, description]), { id: district.id, label: district.label, description, color: zoningColor(district) });
    }
    return [...entries.entries()].sort(([, a], [, b]) => a.label.localeCompare(b.label));
  }, [state.data]);
  const available = !state.problem;
  return <section aria-label="Land use" className="max-w-sm space-y-3 rounded-2xl border border-[#151515]/20 bg-[#fffdf6]/95 p-3 text-[#151515] shadow-lg backdrop-blur-sm">
    <header className="flex items-center gap-2.5">
      <span aria-hidden="true" className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl border border-[#151515]/15 bg-[#e7eee8]"><MapIcon size={17} strokeWidth={1.8} /></span>
      <div><h3 className="text-sm font-bold">Land-use map</h3><p className="text-[10px] font-semibold uppercase tracking-widest text-[#5c554d]">Existing · City of Calgary</p></div>
    </header>
    <label className={`flex min-h-11 items-center justify-between gap-3 rounded-xl border border-[#151515]/15 px-3 py-2 text-xs font-semibold ${!available ? 'cursor-not-allowed opacity-60' : 'cursor-pointer hover:bg-[#edf2ec]'} ${state.enabled ? 'bg-[#e7eee8]' : 'bg-white/80'}`}>
      Show land-use map
      <span className="relative inline-flex shrink-0">
        <input type="checkbox" role="switch" className="peer absolute inset-0 z-10 h-full w-full cursor-pointer opacity-0 disabled:cursor-not-allowed" checked={state.enabled} disabled={!available} onChange={event => state.setEnabled(event.target.checked)} />
        <span aria-hidden="true" className="h-6 w-10 rounded-full border border-[#151515]/25 bg-stone-200 transition-colors peer-checked:bg-[#37594b] peer-focus-visible:outline peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-[#151515] motion-reduce:transition-none" />
        <span aria-hidden="true" className="pointer-events-none absolute left-1 top-1 h-4 w-4 rounded-full bg-white shadow-sm transition-transform peer-checked:translate-x-4 motion-reduce:transition-none" />
      </span>
    </label>
    {state.problem && <p className="text-[11px] leading-relaxed text-[#5c554d]">{state.problem}</p>}
    {state.enabled && available && <>
      <div className="grid grid-cols-2 gap-x-3 gap-y-1">
        <label className="flex min-h-11 cursor-pointer items-center gap-2 text-xs"><input type="checkbox" className="h-4 w-4 accent-[#37594b]" checked={state.lines} onChange={state.toggleLines} />Boundaries</label>
        <label className="flex min-h-11 cursor-pointer items-center gap-2 text-xs"><input type="checkbox" className="h-4 w-4 accent-[#37594b]" checked={state.labels} onChange={state.toggle} />District labels</label>
        <label className="col-span-2 flex min-h-11 cursor-pointer items-center gap-2 text-xs"><input type="checkbox" className="h-4 w-4 accent-[#37594b]" checked={state.fill} onChange={state.toggleFill} />Colour fills</label>
      </div>
      {state.fill && <label className="block text-xs">
        <span className="flex justify-between gap-2"><span>Fill opacity</span><span className="tabular-nums text-[#5c554d]">{Math.round(state.fillOpacity * 100)}%</span></span>
        <input aria-label="Fill opacity" type="range" min="0" max="100" step="1" value={Math.round(state.fillOpacity * 100)} onChange={event => state.setFillOpacity(Number(event.target.value) / 100)} className="h-8 w-full cursor-pointer accent-[#37594b]" />
        <span className="flex justify-between text-[10px] text-[#5c554d]"><span>Transparent</span><span>Solid</span></span>
      </label>}
      {state.loading && <p role="status" className="text-xs">Loading Calgary zoning…</p>}
      {state.error && <div role="alert" className="rounded-xl border border-amber-200 bg-amber-50 p-2 text-xs text-amber-950"><p>{state.error.message}</p><button className="min-h-11 font-semibold underline underline-offset-2" onClick={state.retry}>Retry zoning data</button></div>}
      {state.data && <p role="status" className="text-xs font-semibold">{state.data.districts.length ? `${state.data.districts.length} zoning areas within your site` : 'No published zoning areas intersect this boundary.'}</p>}
      {state.data?.districts.length ? <p className="text-xs text-[#37594b]">Click a coloured zoning area to explore permitted and discretionary catalogue buildings. Hide policy maps to inspect zoning beneath them.</p> : null}
      {guide.length > 0 && <details open className="group rounded-xl border border-[#151515]/15 bg-white/80">
        <summary className="flex min-h-11 cursor-pointer list-none items-center justify-between gap-2 rounded-xl px-3 py-2 text-xs font-semibold hover:bg-[#edf2ec] focus-visible:outline focus-visible:outline-2 focus-visible:outline-[#151515] [&::-webkit-details-marker]:hidden"><span>District legend ({guide.length})</span><ChevronDown aria-hidden="true" size={15} className="shrink-0 group-open:rotate-180" /></summary>
        <dl aria-label="Zoning code guide" tabIndex={0} className="max-h-48 divide-y divide-[#151515]/10 overflow-y-auto overscroll-contain border-t border-[#151515]/10 px-3 text-xs focus-visible:outline focus-visible:outline-2 focus-visible:outline-[#151515]">
          {guide.map(([key, entry]) => <div key={key} className="py-2.5">
            <dt className="flex items-center gap-2 font-semibold"><span aria-hidden="true" className="h-3 w-3 shrink-0 rounded-sm border border-black/20" style={{ backgroundColor: entry.color }} /><span className="break-words">{entry.label}</span></dt>
            <dd className="mt-1 pl-5 text-[11px] leading-relaxed text-[#5c554d]">{entry.description}</dd>
            {onInspect && <dd className="pl-5"><button type="button" disabled={!state.fill || state.fillOpacity <= 0} onClick={() => onInspect(entry.id)} className="min-h-11 text-left text-[11px] font-semibold text-[#37594b] underline disabled:opacity-40">Explore buildings for {entry.label}</button></dd>}
          </div>)}
        </dl>
      </details>}
      <p className="text-[10px] leading-relaxed text-[#5c554d]">City district codes · CityPrompt presentation colours. Proposed studies have separate layer controls.</p>
      <a className="flex min-h-11 items-center gap-2 border-t border-[#151515]/10 pt-2 text-[10px] leading-relaxed text-[#5c554d] underline decoration-[#151515]/30 underline-offset-2 hover:text-[#151515]" href={ZONING_SOURCE} target="_blank" rel="noreferrer"><span>Calgary land-use districts{state.data ? ` · loaded ${state.data.loadedAt.slice(0, 10)}` : ''}</span><ExternalLink aria-hidden="true" size={12} className="shrink-0" /></a>
    </>}
  </section>;
}
