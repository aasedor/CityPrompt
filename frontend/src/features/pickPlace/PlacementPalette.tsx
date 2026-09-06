import { useState } from 'react';
import type { PlaceAssetId } from './catalogue';
import { browseAssets, availableGroups, type StreetAsset } from './assetRegistry';
import { CalgaryGuideDetails } from '@/features/calgaryCatalogue/CatalogueBrowser';

export function PlacementPalette({ selected, onPick, onCancel, status, message, onRetry, onPickStreet, streetActive = false }: {
  selected: PlaceAssetId | null; onPick: (id: PlaceAssetId) => void; onCancel: () => void;
  status: string; message: string; onRetry: () => void;
  onPickStreet?: (asset: StreetAsset) => void; streetActive?: boolean;
}) {
  const [query, setQuery] = useState('');
  const [groupId, setGroupId] = useState('');
  const assets = browseAssets(query, groupId).filter(asset => asset.kind === 'object' || onPickStreet);
  return <section aria-label="Place 3D objects" className="space-y-2">
    <div><p className="font-bold text-slate-900">Pick, place & reshape</p>
      <p className="text-xs text-slate-600">Choose an object, then click an empty space.</p></div>
    <label className="sr-only" htmlFor="placement-search">Search objects or district code</label>
    <input id="placement-search" type="search" placeholder="Search homes, parks, R-C1…" value={query} onChange={event => setQuery(event.target.value)} className="min-h-11 w-full rounded border border-slate-400 bg-white px-2 text-sm text-slate-900" />
    <label className="sr-only" htmlFor="placement-group">Object category</label>
    <select id="placement-group" value={groupId} onChange={event => setGroupId(event.target.value)} className="min-h-11 w-full rounded border border-slate-400 bg-white px-2 text-sm text-slate-900">
      <option value="">All available types</option>
      {availableGroups().filter(group => onPickStreet || group.domain !== 'street_pathway').map(group => <option key={group.id} value={group.id}>{group.label}</option>)}
    </select>
    <div aria-label="Available objects" className="max-h-[34vh] space-y-2 overflow-y-auto overscroll-contain pr-1">
    {assets.map(asset => <div key={asset.id}><button data-tour={asset.kind === 'street' ? 'tool-streetsPaths' : `place-${asset.id}`} aria-pressed={asset.kind === 'street' ? streetActive : selected===asset.id}
      onClick={() => asset.kind === 'street' ? onPickStreet?.(asset) : onPick(asset.id)} className={`flex w-full items-center gap-2 rounded-lg border-2 border-slate-900 p-2 text-left ${(asset.kind === 'street' ? streetActive : selected===asset.id)?'bg-[#c9ff3d]':'bg-white hover:bg-lime-50'}`}>
      <img loading="lazy" src={asset.thumbnail} alt="" className="h-16 w-16 rounded object-cover" />
      <span><span className="block text-sm font-bold text-slate-900">{asset.label}</span>
        <span className="block text-xs text-slate-600">{asset.description}</span></span>
    </button>
      <CalgaryGuideDetails classification={asset.calgaryGuide} />
    </div>)}
    {!assets.length && <div role="status" className="p-2 text-sm text-slate-700">No available objects match.<button onClick={() => { setQuery(''); setGroupId(''); }} className="block min-h-11 underline">Clear filters</button></div>}
    </div>
    {selected && <button onClick={onCancel} className="min-h-11 w-full rounded-lg border border-slate-500 bg-white text-sm text-slate-900">Cancel placement · Esc</button>}
    <div role="status" aria-live="polite" className={`rounded-lg px-2 py-2 text-xs ${status==='error'?'bg-amber-50 text-amber-950':'bg-emerald-50 text-emerald-950'}`}>
      <p className="font-semibold">{status==='updating'?'Updating 3D…':status==='error'?'3D update needs attention':status==='ready'?'3D saved':'3D appears automatically'}</p>
      {message && <p className="mt-1">{message}</p>}
      {status==='error' && <button onClick={onRetry} className="mt-1 min-h-11 underline">Retry 3D update</button>}
    </div>
  </section>;
}
