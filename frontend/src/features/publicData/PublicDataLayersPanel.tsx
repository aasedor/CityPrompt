import { useId } from 'react';
import { ReferenceLayersPanel } from '../referenceLayers/ReferenceLayersPanel';
import { PUBLIC_DATASETS, PUBLIC_REFERENCES, PUBLIC_DATA_TERMS } from './publicDatasets';
import { PUBLIC_DATA_LIMITS } from './publicData';
import type { PublicDataLayersState } from './usePublicDataLayers';

const NO_HIDDEN_LAYERS = new Set<string>();
const sourceLinkClass = 'font-medium text-blue-700 underline';

export function PublicDataLayersPanel({ state }: { state: PublicDataLayersState }) {
  const id = useId();
  return <details className="w-80 max-w-full rounded-xl border border-slate-300 bg-white p-3 text-slate-900">
    <summary className="min-h-11 cursor-pointer py-2 font-semibold">Optional public data</summary>
    <p className="mt-1 text-xs text-slate-600">Calgary reference data near your site, including a 250 m buffer. Off by default. Up to {PUBLIC_DATA_LIMITS.layers} map layers at once.</p>
    {state.problem && <p className="mt-2 text-sm text-amber-800">{state.problem} Draw a site boundary to use map overlays.</p>}
    {state.atLimit && <p role="status" className="mt-2 text-sm text-amber-800">Untick a map layer before adding another.</p>}
    <fieldset className="mt-3 space-y-1">
      <legend className="text-sm font-semibold">Map overlays</legend>
      {PUBLIC_DATASETS.map(dataset => {
        const checked = state.selectedIds.has(dataset.id);
        const status = state.states.find(item => item.dataset.id === dataset.id);
        return <div key={dataset.id}>
          <label className="flex min-h-11 items-center gap-2 text-sm" htmlFor={`${id}-${dataset.id}`}>
            <input type="checkbox" id={`${id}-${dataset.id}`} checked={checked} disabled={!checked && (Boolean(state.problem) || state.atLimit)} onChange={event => state.setEnabled(dataset.id, event.target.checked)} className="h-4 w-4 accent-blue-700" />
            <span aria-hidden className="h-2.5 w-2.5 shrink-0 rounded-full" style={{ backgroundColor: dataset.color }} />
            {dataset.name}
          </label>
          {checked && <div className="mb-2 ml-6 space-y-1 text-xs text-slate-600">
            <p>{dataset.vintage}. {dataset.note}</p>
            <a href={`https://data.calgary.ca/d/${dataset.sourceId}`} target="_blank" rel="noreferrer" className={sourceLinkClass}>{dataset.name} source</a>
            {dataset.id === 'community' && <a href="https://www.calgary.ca/communities/profiles.html" target="_blank" rel="noreferrer" className={`block ${sourceLinkClass}`}>Open full community profiles</a>}
            {status?.loading && <p role="status">Loading nearby data…</p>}
            {status?.error && <p role="alert" className="text-red-800">{status.error} <button type="button" onClick={status.retry} className="min-h-11 underline">Retry {dataset.name}</button></p>}
            {status?.layer && <>
              <p>{status.layer.feature_count.toLocaleString()} loaded records · retrieved {new Date(status.layer.created_at).toLocaleDateString()}</p>
              {status.layer.warnings.map(warning => <p key={warning} className="text-amber-800">{warning}</p>)}
            </>}
          </div>}
        </div>;
      })}
    </fieldset>
    <fieldset className="mt-3 space-y-1 border-t border-slate-200 pt-2">
      <legend className="text-sm font-semibold">Source reference cards (no map overlay)</legend>
      {PUBLIC_REFERENCES.map(reference => <div key={reference.id}>
        <label className="flex min-h-11 items-center gap-2 text-sm" htmlFor={`${id}-${reference.id}`}>
          <input type="checkbox" id={`${id}-${reference.id}`} checked={state.selectedIds.has(reference.id)} onChange={event => state.setEnabled(reference.id, event.target.checked)} className="h-4 w-4 accent-blue-700" />{reference.name}
        </label>
        {state.selectedIds.has(reference.id) && <div className="mb-2 ml-6 space-y-1 text-xs text-slate-600">
          <p>{reference.note}</p>
          <a href={reference.url} target="_blank" rel="noreferrer" className={sourceLinkClass}>{reference.id === 'rental-context' ? 'Open CMHC rental tables' : 'Open current levy information'}</a>
        </div>}
      </div>)}
    </fieldset>
    {state.layers.length > 0 && <details className="mt-3">
      <summary className="min-h-11 cursor-pointer py-2 text-sm font-semibold">Inspect selected data</summary>
      <ReferenceLayersPanel layers={state.layers} hiddenIds={NO_HIDDEN_LAYERS} onToggle={layerId => state.setEnabled(layerId.replace('public-data:', ''), false)} />
    </details>}
    <p className="mt-3 text-xs text-slate-500">Nearby extracts may be incomplete. Check source dates and limits before drawing conclusions. Contains information licensed under the <a href={PUBLIC_DATA_TERMS} target="_blank" rel="noreferrer" className="underline">Open Government Licence – City of Calgary</a>.</p>
  </details>;
}
