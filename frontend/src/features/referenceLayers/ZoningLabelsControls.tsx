import { ZONING_SOURCE } from './zoningLabels';
import type { ZoningLabelsState } from './useZoningLabels';

export function ZoningLabelsControls({ state }: { state: ZoningLabelsState }) {
  return <section aria-label="Land use" className="max-w-sm space-y-2 rounded-xl border border-slate-300 bg-white/95 p-3 text-slate-900">
    <h3 className="text-sm font-bold">Land use</h3>
    <label className="flex min-h-11 items-center gap-2 text-sm"><input type="checkbox" checked={state.labels} disabled={Boolean(state.problem)} onChange={state.toggle} />Show zoning codes</label>
    <p className="text-xs text-slate-600">{state.problem ?? 'Visual reference only. Your site and design stay unchanged.'}</p>
    {state.labels && !state.problem && <>
      {state.loading && <p role="status" className="text-xs">Loading Calgary zoning…</p>}
      {state.error && <div role="alert" className="text-xs"><p>{state.error.message}</p><button className="min-h-11 underline" onClick={state.retry}>Retry zoning data</button></div>}
      {state.data && <p role="status" className="text-xs">{state.data.districts.length ? `${state.data.districts.length} zoning areas` : 'No published zoning areas intersect this boundary.'}</p>}
      <p className="text-xs text-slate-600">Codes label the land-use areas within your site. Zoom in to read more labels.</p>
      <a className="block text-xs underline" href={ZONING_SOURCE} target="_blank" rel="noreferrer">Calgary land-use districts{state.data ? ` · loaded ${state.data.loadedAt.slice(0, 10)}` : ''}</a>
    </>}
  </section>;
}
