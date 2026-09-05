import { useDeferredValue, useMemo, useState } from 'react';
import { ChevronDown, ChevronRight, Eye, EyeOff, Trash2 } from 'lucide-react';
import type { ReferenceLayer } from './api';
import { referenceFeatureLabel } from './referenceGeometry';

interface ReferenceLayersPanelProps {
  layers: ReferenceLayer[];
  hiddenIds: Set<string>;
  onToggle: (id: string) => void;
  onDelete?: (id: string) => void;
  deletingId?: string | null;
  isLoading?: boolean;
  error?: string | null;
  onRetry?: () => void;
  onFocus?: (center: [number, number]) => void;
}

export function ReferenceLayersPanel({ layers, hiddenIds, onToggle, onDelete, deletingId,
  isLoading, error, onRetry, onFocus }: ReferenceLayersPanelProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [confirmId, setConfirmId] = useState<string | null>(null);
  if (!isLoading && !error && layers.length === 0) return null;
  return <section aria-label="Reference layers" className="w-80 max-w-full rounded-xl border-2 border-[#151515] bg-white p-3 text-[#151515] shadow-lg">
    <h2 className="font-bold">Reference layers</h2>
    <p className="mt-1 text-xs text-slate-600">Optional context. These layers never become buildings or limit your design.</p>
    {isLoading && <p role="status" className="mt-2 text-sm">Loading reference layers…</p>}
    {error && <div role="alert" className="mt-2 text-sm text-red-800">{error} <button type="button" onClick={onRetry} className="underline">Retry</button></div>}
    <ul className="mt-2 space-y-2">
      {layers.map((layer) => <li key={layer.id} className="rounded-lg border border-slate-200 p-2">
        <div className="flex items-center gap-2">
          <button type="button" aria-label={`${hiddenIds.has(layer.id) ? 'Show' : 'Hide'} ${layer.name}`} aria-pressed={!hiddenIds.has(layer.id)} onClick={() => onToggle(layer.id)} className="flex min-h-11 min-w-11 items-center justify-center rounded hover:bg-slate-100 focus-visible:outline focus-visible:outline-2">
            {hiddenIds.has(layer.id) ? <EyeOff size={18} /> : <Eye size={18} />}
          </button>
          <span aria-hidden className="h-3 w-3 shrink-0 rounded-full" style={{ backgroundColor: layer.color }} />
          <button type="button" title={layer.name} aria-expanded={expandedId === layer.id} onClick={() => setExpandedId((current) => current === layer.id ? null : layer.id)} className="flex min-h-11 min-w-0 flex-1 items-center gap-1 rounded text-left text-sm font-semibold focus-visible:outline focus-visible:outline-2">
            <span className="truncate">{layer.name}</span>{expandedId === layer.id ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
          </button>
          {onDelete && <button type="button" aria-label={`Remove ${layer.name}`} disabled={deletingId === layer.id} onClick={() => setConfirmId(layer.id)} className="flex min-h-11 min-w-11 items-center justify-center rounded hover:bg-red-50 focus-visible:outline focus-visible:outline-2"><Trash2 size={16} /></button>}
        </div>
        {confirmId === layer.id && <div className="mt-2 text-sm">
          <p>Remove this reference layer for everyone in the project?</p>
          <button type="button" disabled={deletingId === layer.id} className="mr-3 mt-1 min-h-11 font-semibold text-red-700" onClick={() => { onDelete?.(layer.id); setConfirmId(null); }}>Remove layer</button>
          <button type="button" className="min-h-11 underline" onClick={() => setConfirmId(null)}>Cancel</button>
        </div>}
        {expandedId === layer.id && <div className="mt-2 space-y-2 text-sm">
          <p>{layer.feature_count.toLocaleString()} {layer.feature_count === 1 ? 'feature' : 'features'} · {layer.kind === 'zoning' ? 'Zoning reference' : 'Reference data'}</p>
          <p className="break-words text-slate-600">Source file: {layer.source_filename}<br />Source CRS: {layer.source_crs}</p>
          {layer.description && <p>{layer.description}</p>}
          {layer.source_url && /^https?:\/\//i.test(layer.source_url) && <a href={layer.source_url} target="_blank" rel="noreferrer" className="block text-blue-700 underline">Open source</a>}
          {layer.warnings.map((warning) => <p key={warning} className="text-amber-800">{warning}</p>)}
          {onFocus && <button type="button" className="font-semibold underline" onClick={() => onFocus([(layer.bounds[0] + layer.bounds[2]) / 2, (layer.bounds[1] + layer.bounds[3]) / 2])}>Go to layer</button>}
          <FeatureAttributes layer={layer} />
        </div>}
      </li>)}
    </ul>
  </section>;
}

function FeatureAttributes({ layer }: { layer: ReferenceLayer }) {
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const features = layer.feature_collection.features;
  const search = useDeferredValue(query.toLowerCase());
  const searchable = useMemo(() => features.map((feature, index) => ({ feature, index,
    text: `${referenceFeatureLabel(feature.properties, index)} ${JSON.stringify(feature.properties)}`.toLowerCase(),
  })), [features]);
  const matches = searchable.filter(({ text }) => text.includes(search));
  const shownMatches = matches.slice(0, 200);
  const selectionOutsidePage = matches.find(({ index }) => index === selectedIndex && !shownMatches.some((item) => item.index === index));
  if (selectionOutsidePage) shownMatches.push(selectionOutsidePage);
  const selected = features[selectedIndex];
  return <div className="border-t border-slate-200 pt-2">
    <label className="block font-semibold">Find a feature<input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="District, address or attribute" className="mt-1 w-full rounded border border-slate-300 p-2 font-normal" /></label>
    <label className="mt-2 block">Feature
      <select className="mt-1 w-full rounded border border-slate-300 p-1.5" value={matches.some(({ index }) => index === selectedIndex) ? selectedIndex : ''} onChange={(event) => setSelectedIndex(Number(event.target.value))}>
        <option value="" disabled>{matches.length ? 'Choose a feature' : 'No matching features'}</option>
        {shownMatches.map(({ feature, index }) => <option key={index} value={index}>{referenceFeatureLabel(feature.properties, index)}</option>)}
      </select>
    </label>
    {matches.length > 200 && <p className="mt-1 text-slate-500">Showing the first 200 matches. Search to narrow the list.</p>}
    {selected && matches.some(({ index }) => index === selectedIndex) && <dl className="mt-2 max-h-48 space-y-1 overflow-y-auto break-words">
      {Object.entries(selected.properties).map(([name, value]) => <div key={name}><dt className="font-semibold">{name}</dt><dd className="text-slate-600">{typeof value === 'object' ? JSON.stringify(value) : String(value ?? '—')}</dd></div>)}
      {Object.keys(selected.properties).length === 0 && <p>No attributes provided.</p>}
    </dl>}
  </div>;
}
