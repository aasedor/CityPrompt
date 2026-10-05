import { ExternalLink, Map as MapIcon } from 'lucide-react';
import { LOCAL_AREA_PLANS } from './localAreaPlans';
import type { LocalAreaPolicyState } from './useLocalAreaPolicy';

export function LocalAreaPlanPanel({ state }: { state: LocalAreaPolicyState }) {
  const { plan } = state;
  return <section aria-label="Local area plan" className="max-w-sm space-y-3 rounded-2xl border border-[#151515]/20 bg-[#fffdf6]/95 p-3 text-[#151515] shadow-lg backdrop-blur-sm">
    <header className="flex items-center gap-2.5">
      <span aria-hidden className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl border border-[#151515]/15 bg-[#fff4b2]"><MapIcon size={17} /></span>
      <div><h3 className="text-sm font-bold">Local area plan</h3><p className="text-[10px] font-semibold uppercase tracking-widest text-[#5c554d]">{plan ? `${plan.name} · Urban Form` : 'Approved Calgary plans'}</p></div>
    </header>
    <label className="block text-xs font-semibold">Plan to explore
      <select aria-label="Local area plan" value={state.planId} onChange={event => state.setPlan(event.target.value)} className="mt-1 min-h-11 w-full rounded-xl border border-[#151515]/20 bg-white px-2 text-xs">
        <option value="auto">Automatically match my site</option>
        {LOCAL_AREA_PLANS.map(item => <option key={item.id} value={item.id}>{item.name}{state.matchingPlans.some(match => match.id === item.id) ? ' · covers your site' : ''}</option>)}
      </select>
    </label>
    {state.matchingPlans.length > 1 && <p role="status" className="text-xs leading-relaxed text-[#5c554d]">Your site crosses {state.matchingPlans.map(item => item.name).join(' and ')}. Explore each plan with the selector; automatic selection shows the largest overlap.</p>}
    <label className="flex min-h-11 cursor-pointer items-center justify-between gap-3 rounded-xl border border-[#151515]/15 bg-white/80 px-3 py-2 text-xs font-semibold">
      {plan ? `Show ${plan.name} policy map` : 'Show local policy map'}
      <span className="relative inline-flex shrink-0">
        <input type="checkbox" role="switch" className="peer absolute inset-0 z-10 h-full w-full cursor-pointer opacity-0 disabled:cursor-not-allowed" checked={state.enabled} disabled={!plan && !state.enabled} onChange={event => state.setEnabled(event.target.checked)} />
        <span aria-hidden className="h-6 w-10 rounded-full border border-[#151515]/25 bg-stone-200 peer-checked:bg-[#37594b] peer-focus-visible:outline peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-[#151515]" />
        <span aria-hidden className="pointer-events-none absolute left-1 top-1 h-4 w-4 rounded-full bg-white shadow-sm peer-checked:translate-x-4" />
      </span>
    </label>
    {state.problem && <p role="status" className="text-xs leading-relaxed text-[#5c554d]">{state.problem}</p>}
    {state.enabled && !state.problem && plan && <>
      <p className="text-xs leading-relaxed">Click a coloured area on the map or a designation in the legend to learn what it means. These are planning policies, separate from today’s zoning districts.</p>
      <label className="block text-xs"><span className="flex justify-between"><span>Policy map opacity</span><span className="tabular-nums">{Math.round(state.opacity * 100)}%</span></span>
        <input aria-label="Policy map opacity" type="range" min="0" max="100" step="1" value={Math.round(state.opacity * 100)} onChange={event => state.setOpacity(Number(event.target.value) / 100)} className="h-9 w-full cursor-pointer accent-[#37594b]" />
        <span className="flex justify-between text-[10px] text-[#5c554d]"><span>Transparent</span><span>Solid</span></span>
      </label>
      <label className="flex min-h-11 cursor-pointer items-center gap-2 text-xs"><input type="checkbox" className="h-4 w-4 accent-[#37594b]" checked={state.clipToSite} onChange={event => state.setClipToSite(event.target.checked)} />Only show inside my site</label>
      {state.loading && <p role="status" className="text-xs">Loading {plan.name} policy map…</p>}
      {state.error && <div role="alert" className="rounded-xl bg-amber-50 p-2 text-xs"><p>The {plan.name} map could not load.</p><button className="min-h-11 font-semibold underline" onClick={state.retry}>Retry policy map</button></div>}
      {state.partial && <p role="status" className="text-xs text-amber-900">Part of your site is outside {plan.name}. Policy coverage stops at the plan boundary.</p>}
      {state.outsideSite && <p role="status" className="text-xs text-amber-900">{state.clipToSite ? 'This plan has no coverage inside your site. Turn off site clipping to explore the full map.' : `Browsing ${plan.name}; this plan does not overlap your current site.`}</p>}
      {state.data && state.legend.length > 0 && <>
        <details open className="rounded-xl border border-[#151515]/15 bg-white/80">
          <summary className="min-h-11 cursor-pointer px-3 py-3 text-xs font-semibold">Urban form legend</summary>
          <ul aria-label={`${plan.name} urban form categories`} className="max-h-56 overflow-y-auto border-t border-[#151515]/10 p-1 text-xs">
            {state.legend.map(entry => <li key={entry.category}><button type="button" aria-label={`About ${entry.category}`} aria-pressed={state.selected?.designation.name === entry.category}
              onClick={() => state.selectCategory(entry.category)} className="flex min-h-11 w-full items-start gap-2 rounded-lg px-2 py-3 text-left hover:bg-[#edf2ec] aria-pressed:bg-[#e7eee8] focus-visible:outline focus-visible:outline-2 focus-visible:outline-[#37594b]">
              <span aria-hidden className="mt-0.5 h-3 w-3 shrink-0 rounded-sm border border-black/20" style={{ backgroundColor: entry.color }} /><span>{entry.category}{entry.withinSite && <span className="ml-1 text-[10px] font-semibold text-[#37594b]">· in your site</span>}</span>
            </button></li>)}
          </ul>
        </details>
        <p className="text-[10px] leading-relaxed text-[#5c554d]">Published City colours · generalized planning boundaries. {plan.alignmentChecks} checked street junctions differ by up to {plan.alignmentMaxMetres} m. Use Top View to compare; the overlay follows the site’s reference elevation.</p>
      </>}
      <p className="text-[10px] leading-relaxed text-[#5c554d]">Urban Form only. Building Scale, hatching, Active Frontage and other additional policy symbols are not shown here. Read those maps and written policies in the full plan before proposing rezoning.</p>
    </>}
    {plan && <a className="flex min-h-11 items-center gap-2 border-t border-[#151515]/10 pt-2 text-[10px] leading-relaxed text-[#5c554d] underline underline-offset-2" href={`${plan.source}#page=${plan.mapPage}`} target="_blank" rel="noreferrer"><span>Approved {plan.name} plan · Map 3<br />{plan.edition}</span><ExternalLink size={12} aria-hidden className="shrink-0" /></a>}
    <details className="border-t border-[#151515]/10 pt-1 text-[10px] text-[#5c554d]"><summary className="min-h-11 cursor-pointer py-3">Plans still in progress</summary><p>South Bow, Carburn and South McKnight do not yet have approved maps in this collection.</p><a className="flex min-h-11 items-center gap-1 underline" href="https://www.calgary.ca/planning/local-area/in-progress.html" target="_blank" rel="noreferrer">View the City’s current plan status<ExternalLink size={11} aria-hidden /></a></details>
  </section>;
}
