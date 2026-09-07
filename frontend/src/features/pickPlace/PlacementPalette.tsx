import { useCallback, useState } from 'react';
import { Building2, Trees, Route } from 'lucide-react';
import type { PlaceAssetId } from './catalogue';
import { browseAssets, availableGroups, STREET_ASSETS, type StreetAsset } from './assetRegistry';
import { CalgaryGuideDetails } from '@/features/calgaryCatalogue/CatalogueBrowser';
import { StreetCrossSection } from './StreetCrossSection';
import { StudioDialog } from '@/features/projects/StudioControls';

const sections = [
  { id: 'building', label: 'Buildings', icon: Building2 },
  { id: 'park_plaza', label: 'Parks', icon: Trees },
  { id: 'street_pathway', label: 'Streets', icon: Route },
] as const;
type Section = typeof sections[number]['id'];
const filterStyle = 'min-h-11 min-w-0 rounded-lg border border-slate-400 bg-white px-3 text-sm text-slate-900';

export function PlacementPalette({ selected, onPick, onCancel, status, message, onRetry, onPickStreet, activeStreetVariant, onBrowseChange }: {
  selected: PlaceAssetId | null; onPick: (id: PlaceAssetId) => void; onCancel: () => void;
  status: string; message: string; onRetry: () => void;
  onPickStreet?: (asset: StreetAsset) => void; activeStreetVariant?: string;
  onBrowseChange?: (open: boolean) => void;
}) {
  const [open, setOpen] = useState(false);
  const [section, setSection] = useState<Section>('building');
  const [query, setQuery] = useState('');
  const [groupId, setGroupId] = useState('');
  const [limit, setLimit] = useState(12);
  const close = useCallback(() => { setOpen(false); onBrowseChange?.(false); }, [onBrowseChange]);
  const chooseSection = (id: Section) => { setSection(id); setGroupId(''); setQuery(''); setLimit(12); };
  const groups = availableGroups().filter(group => group.domain === section);
  const assets = browseAssets(query, groupId).filter(asset => groups.some(group => group.id === asset.calgaryGuide.groupId));
  const visibleSections = sections.filter(item => onPickStreet || item.id !== 'street_pathway');
  const activeStreet = STREET_ASSETS.find(asset => asset.model.variantId === activeStreetVariant);
  return <section aria-label="Place 3D objects" className="space-y-2">
    <p className="text-sm font-bold text-slate-900">Add to your community</p>
    <div className="grid grid-cols-3 gap-1">
      {visibleSections.map(({ id, label, icon: Icon }) => <button key={id} aria-haspopup="dialog"
        data-tour={id === 'street_pathway' ? 'tool-streetsPaths' : id === 'building' ? 'place-infill_home' : 'place-neighbourhood_park'}
        onClick={() => { chooseSection(id); setOpen(true); onBrowseChange?.(true); }}
        className="flex min-h-16 flex-col items-center justify-center gap-1 rounded-lg border-2 border-slate-900 bg-white text-xs font-bold text-slate-900 hover:bg-lime-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2">
        <Icon size={22} />{label}
      </button>)}
    </div>
    {activeStreet && <p className="rounded-lg border border-lime-400 bg-lime-50 px-2 py-2 text-xs text-slate-900">
      <strong>{activeStreet.label} · {activeStreet.sectionWidth} m wide</strong><br />Draw its route; the width stays fixed.
    </p>}
    {selected && <button onClick={onCancel} className="min-h-11 w-full rounded-lg border border-slate-500 bg-white text-sm text-slate-900">Cancel placement · Esc</button>}
    <div role="status" aria-live="polite" className={`rounded-lg px-2 py-1 text-xs ${status === 'error' ? 'bg-amber-50 text-amber-950' : 'bg-emerald-50 text-emerald-950'}`}>
      <p className="font-semibold">{status === 'updating' ? 'Updating 3D…' : status === 'error' ? '3D update needs attention' : status === 'ready' ? '3D saved' : '3D appears automatically'}</p>
      {message && <p className="mt-1">{message}</p>}
      {status === 'error' && <button onClick={onRetry} className="mt-1 min-h-11 underline">Retry 3D update</button>}
    </div>
    {open && <StudioDialog title="Community catalogue" onClose={close}>
      <div className="flex h-[min(70dvh,640px)] min-h-0 flex-col gap-3 text-slate-900">
        <div className="shrink-0 space-y-3">
          <nav aria-label="Catalogue sections" className="flex gap-2">
            {visibleSections.map(({ id, label, icon: Icon }) => <button key={id} aria-pressed={section === id} onClick={() => chooseSection(id)}
              className={`flex min-h-11 flex-1 items-center justify-center gap-2 rounded-lg border px-2 text-sm font-semibold ${section === id ? 'border-slate-900 bg-[#c9ff3d]' : 'border-slate-300 bg-white hover:bg-lime-50'}`}><Icon size={18} />{label}</button>)}
          </nav>
          <div className="grid gap-2 sm:grid-cols-2">
            <label className="sr-only" htmlFor="placement-search">Search objects or district code</label>
            <input id="placement-search" type="search" placeholder="Search names or district codes…" value={query} onChange={event => { setQuery(event.target.value); setLimit(12); }} className={filterStyle} />
            <label className="sr-only" htmlFor="placement-group">Object category</label>
            <select id="placement-group" value={groupId} onChange={event => { setGroupId(event.target.value); setLimit(12); }} className={filterStyle}>
              <option value="">All {sections.find(item => item.id === section)?.label.toLowerCase()}</option>
              {groups.map(group => <option key={group.id} value={group.id}>{group.label}</option>)}
            </select>
          </div>
          <p className="text-xs text-slate-600" role="status">{assets.length} {assets.length === 1 ? 'choice' : 'choices'} · Pick an asset, then place it on your site.</p>
        </div>
        <div aria-label="Available objects" className="min-h-0 flex-1 overflow-y-auto overscroll-contain p-1">
          <div className="grid items-start gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {assets.slice(0, limit).map(asset => <article key={asset.id} className="overflow-hidden rounded-xl border border-slate-300 bg-white">
              <button aria-pressed={asset.kind === 'street' ? activeStreetVariant === asset.model.variantId : selected === asset.id}
                onClick={() => { close(); if (asset.kind === 'street') onPickStreet?.(asset); else onPick(asset.id); }}
                className="group w-full text-left hover:bg-lime-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-[-3px]">
                <img loading="lazy" src={asset.thumbnail} alt="" className="h-36 w-full bg-slate-100 object-contain" />
                <span className="block space-y-1 p-3"><span className="block text-sm font-bold">{asset.label}</span><span className="block text-xs text-slate-600">{asset.description}</span><span className="block pt-1 text-sm font-semibold underline">Choose & place</span></span>
              </button>
              <div className="px-3 pb-2">{asset.kind === 'street' && <StreetCrossSection asset={asset} />}<CalgaryGuideDetails classification={asset.calgaryGuide} /></div>
            </article>)}
          </div>
          {!assets.length && <div className="p-4 text-sm">No available objects match.<button onClick={() => { setQuery(''); setGroupId(''); setLimit(12); }} className="block min-h-11 underline">Clear filters</button></div>}
          {assets.length > limit && <button onClick={() => setLimit(value => value + 12)} className="mt-3 min-h-11 w-full rounded-lg border border-slate-400 font-semibold">Show more choices</button>}
        </div>
      </div>
    </StudioDialog>}
  </section>;
}
