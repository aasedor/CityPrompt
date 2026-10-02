import { PARCEL_SOURCE, ZONING_SOURCE } from './parcelZoning';
import type { ParcelZoningState } from './useParcelZoning';

export function ParcelZoningControls({ state }: { state: ParcelZoningState }) {
  const enabled = state.lines || state.labels;
  return <section aria-label="Parcel zoning" className="max-w-sm space-y-2 rounded-xl border border-slate-300 bg-white/95 p-3 text-slate-900">
    <h3 className="text-sm font-bold">Parcels & land use</h3>
    <label className="flex min-h-11 items-center gap-2 text-sm"><input type="checkbox" checked={state.lines} disabled={Boolean(state.problem)} onChange={() => state.toggle('lines')} />Parcel boundaries</label>
    <label className="flex min-h-11 items-center gap-2 text-sm"><input type="checkbox" checked={state.labels} disabled={Boolean(state.problem)} onChange={() => state.toggle('labels')} />Land-use labels</label>
    <p className="text-xs text-slate-600">{state.problem ?? 'Visual reference only. Your site and design stay unchanged.'}</p>
    {enabled && !state.problem && <>
      {state.loading && <p role="status" className="text-xs">Loading Calgary parcels…</p>}
      {state.error && <div role="alert" className="text-xs"><p>{state.error.message}</p><button className="min-h-11 underline" onClick={state.retry}>Retry parcel data</button></div>}
      {state.data && <p role="status" className="text-xs">{state.data.parcels.length ? `${state.data.parcels.length} non-road parcels` : 'No non-road parcels found in the published parcel map.'}</p>}
      <p className="text-xs text-slate-600">Published land-use districts matched to the city parcel map. Split zoning shows all intersecting codes; Unknown means no match. Zoom in to read more labels.</p>
      <a className="text-xs underline" href={PARCEL_SOURCE} target="_blank" rel="noreferrer">City of Calgary · parcel map</a>
      <a className="block text-xs underline" href={ZONING_SOURCE} target="_blank" rel="noreferrer">Land-use districts · {state.data ? `loaded ${state.data.loadedAt.slice(0, 10)}` : 'source'}</a>
    </>}
  </section>;
}
