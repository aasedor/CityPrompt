import { ExternalLink, Map as MapIcon } from 'lucide-react';
import { RILEY_SOURCE } from './rileyPolicy';
import type { RileyPolicyState } from './useRileyPolicy';

export function RileyPolicyPanel({ state }: { state: RileyPolicyState }) {
  return <section aria-label="Local area plan" className="max-w-sm space-y-3 rounded-2xl border border-[#151515]/20 bg-[#fffdf6]/95 p-3 text-[#151515] shadow-lg backdrop-blur-sm">
    <header className="flex items-center gap-2.5">
      <span aria-hidden className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl border border-[#151515]/15 bg-[#fff4b2]"><MapIcon size={17} /></span>
      <div><h3 className="text-sm font-bold">Local area plan</h3><p className="text-[10px] font-semibold uppercase tracking-widest text-[#5c554d]">Riley · Urban Form pilot</p></div>
    </header>
    <label className="flex min-h-11 cursor-pointer items-center justify-between gap-3 rounded-xl border border-[#151515]/15 bg-white/80 px-3 py-2 text-xs font-semibold">
      Show Riley policy map
      <span className="relative inline-flex shrink-0">
        <input type="checkbox" role="switch" className="peer absolute inset-0 z-10 h-full w-full cursor-pointer opacity-0 disabled:cursor-not-allowed" checked={state.enabled} disabled={Boolean(state.problem) && !state.enabled} onChange={event => state.setEnabled(event.target.checked)} />
        <span aria-hidden className="h-6 w-10 rounded-full border border-[#151515]/25 bg-stone-200 peer-checked:bg-[#37594b] peer-focus-visible:outline peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-[#151515]" />
        <span aria-hidden className="pointer-events-none absolute left-1 top-1 h-4 w-4 rounded-full bg-white shadow-sm peer-checked:translate-x-4" />
      </span>
    </label>
    {state.problem && <p role="status" className="text-xs leading-relaxed text-[#5c554d]">{state.problem}</p>}
    {state.enabled && !state.problem && <>
      <p className="text-xs leading-relaxed">Explore the area’s future urban form. These are planning policies, separate from today’s zoning districts.</p>
      <label className="block text-xs"><span className="flex justify-between"><span>Policy map opacity</span><span className="tabular-nums">{Math.round(state.opacity * 100)}%</span></span>
        <input aria-label="Policy map opacity" type="range" min="0" max="100" step="1" value={Math.round(state.opacity * 100)} onChange={event => state.setOpacity(Number(event.target.value) / 100)} className="h-9 w-full cursor-pointer accent-[#37594b]" />
        <span className="flex justify-between text-[10px] text-[#5c554d]"><span>Transparent</span><span>Solid</span></span>
      </label>
      <label className="flex min-h-11 cursor-pointer items-center gap-2 text-xs"><input type="checkbox" className="h-4 w-4 accent-[#37594b]" checked={state.clipToSite} onChange={event => state.setClipToSite(event.target.checked)} />Only show inside my site</label>
      {state.loading && <p role="status" className="text-xs">Loading Riley policy map…</p>}
      {state.error && <div role="alert" className="rounded-xl bg-amber-50 p-2 text-xs"><p>The Riley map could not load.</p><button className="min-h-11 font-semibold underline" onClick={state.retry}>Retry policy map</button></div>}
      {state.partial && <p role="status" className="text-xs text-amber-900">Part of your site is outside Riley. Policy coverage stops at the plan boundary.</p>}
      {state.data && <>
        <details open className="rounded-xl border border-[#151515]/15 bg-white/80">
          <summary className="min-h-11 cursor-pointer px-3 py-3 text-xs font-semibold">Urban form legend</summary>
          <ul aria-label="Riley urban form categories" className="max-h-56 space-y-2 overflow-y-auto border-t border-[#151515]/10 px-3 py-3 text-xs">
            {state.legend.map(entry => <li key={entry.category} className="flex items-start gap-2"><span aria-hidden className="mt-0.5 h-3 w-3 shrink-0 rounded-sm border border-black/20" style={{ backgroundColor: entry.color }} /><span>{entry.category}{entry.withinSite && <span className="ml-1 text-[10px] font-semibold text-[#37594b]">· in your site</span>}</span></li>)}
          </ul>
        </details>
        <p className="text-[10px] leading-relaxed text-[#5c554d]">City map colours · aligned PDF polygons. Five checked street junctions differ by 0.1–4 m. Use Top View to compare boundaries; the 3D overlay follows the site’s reference elevation.</p>
        <p className="text-[10px] leading-relaxed text-[#5c554d]">Urban Form only. Read Building Scale, active frontage, comprehensive planning sites and written policies in the full plan before proposing rezoning.</p>
      </>}
    </>}
    <a className="flex min-h-11 items-center gap-2 border-t border-[#151515]/10 pt-2 text-[10px] leading-relaxed text-[#5c554d] underline underline-offset-2" href={RILEY_SOURCE} target="_blank" rel="noreferrer"><span>Approved Riley plan · Map 3<br />25P2025 · amended 38P2025 (April 2025)</span><ExternalLink size={12} aria-hidden className="shrink-0" /></a>
  </section>;
}
