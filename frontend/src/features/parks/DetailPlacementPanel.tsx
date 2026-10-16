import { useEffect, useRef, useState } from 'react';
import { ArrowLeft, X } from 'lucide-react';
import { DETAIL_CATEGORIES, searchDetails, detailAsset, type DetailAsset } from './detailCatalogue';
import { detailThumbnail } from './detailThumbnail';
import type { useDetailPlacement } from './useDetailPlacement';
import { DetailEditControls } from './DetailEditControls';
import { DetailCategoryTiles } from './DetailCategoryTiles';
import { SafetyVariantCards } from './SafetyVariantCards';

function Thumbnail({ asset }: { asset: DetailAsset }) {
  const root = useRef<HTMLDivElement>(null);
  const [image, setImage] = useState(''), [failed, setFailed] = useState(false);
  useEffect(() => {
    setImage(''); setFailed(false);
    let active = true;
    const observer = new IntersectionObserver(entries => {
      if (!entries.some(e => e.isIntersecting)) return;
      observer.disconnect();
      detailThumbnail(asset.id).then(url => { if (active) setImage(url); }).catch(() => { if (active) setFailed(true); });
    }, { rootMargin: '80px' });
    if (root.current) observer.observe(root.current);
    return () => { active = false; observer.disconnect(); };
  }, [asset.id]);
  return <div ref={root} className="flex h-28 items-center justify-center bg-slate-100 text-xs text-slate-500">
    {image ? <img src={image} alt={asset.label} className="h-full w-full object-contain" /> : failed ? 'Preview unavailable' : 'Loading preview…'}
  </div>;
}

export function DetailPlacementPanel({ placement, canEdit, onClose, onArrange }: {
  placement: ReturnType<typeof useDetailPlacement>; canEdit: boolean; onClose: () => void; onArrange: () => void;
}) {
  const [query, setQuery] = useState(''), [category, setCategory] = useState('All');
  const [categoryView, setCategoryView] = useState(true);
  const scrollArea = useRef<HTMLDivElement>(null);
  useEffect(() => { if (scrollArea.current) scrollArea.current.scrollTop = 0; }, [placement.editing?.id]);
  const [view, setView] = useState<'browse' | 'placed'>('browse');
  const showCategories = () => { setCategory('All'); setQuery(''); setCategoryView(true); };
  const options = searchDetails(query, category);
  const selected = placement.selected ? detailAsset(placement.selected) : null;
  return <aside aria-label="Detail catalogue" className="fixed bottom-0 right-0 top-16 z-[80] flex w-[420px] max-w-[calc(100vw-3rem)] flex-col border-l border-slate-300 bg-[#fff9ec] text-slate-950 shadow-2xl"
    onPointerDown={e => e.stopPropagation()} onWheel={e => e.stopPropagation()}>
    <header className="flex shrink-0 items-center justify-between border-b border-slate-200 p-4">
      <h2 className="text-lg font-bold">Add details</h2>
      <button type="button" aria-label="Close detail catalogue" onClick={onClose} className="rounded-lg p-2 hover:bg-slate-200"><X size={22} /></button>
    </header>
    <div className="flex shrink-0 gap-2 border-b border-slate-200 p-3" aria-label="Detail views">
      <button type="button" aria-pressed={view === 'browse'} onClick={() => setView('browse')} className={`min-h-11 flex-1 rounded-full border-2 border-slate-900 text-sm font-bold ${view === 'browse' ? 'bg-[#c9ff3d]' : 'bg-white'}`}>Browse catalogue</button>
      <button type="button" aria-pressed={view === 'placed'} onClick={() => { setView('placed'); placement.choose(null); }} className={`min-h-11 flex-1 rounded-full border-2 border-slate-900 text-sm font-bold ${view === 'placed' ? 'bg-[#c9ff3d]' : 'bg-white'}`}>Placed items ({placement.items.length})</button>
    </div>
    <div ref={scrollArea} className="min-h-0 flex-1 overflow-y-auto">
    {placement.editing && <div className="p-3"><DetailEditControls placement={placement} /></div>}
    {view === 'placed' ? <div className="space-y-2 p-3">
      <p className="text-sm text-slate-600">Select any item to move, rotate or delete it, even when it is hidden behind something.</p>
      {placement.items.map((item, index) => <button type="button" key={item.id} disabled={!canEdit || placement.saving} aria-pressed={placement.editing?.id === item.id}
        onClick={() => placement.selectItem(item.id)} className={`min-h-14 w-full rounded-xl border p-3 text-left disabled:opacity-50 ${placement.editing?.id === item.id ? 'border-slate-900 bg-lime-100 ring-1 ring-slate-900' : 'border-slate-300 bg-white hover:bg-lime-50'}`}>
        <span className="block text-sm font-bold">{detailAsset(item.variant).label} · {index + 1}</span>
        <span className="text-xs text-slate-600">Rotation {Math.round(item.angle)}° · Select to edit</span>
      </button>)}
      {!placement.items.length && <p className="py-4 text-sm">No details placed yet. Choose an item from the catalogue to get started.</p>}
    </div> : <>
    <div className="space-y-2 border-b border-slate-200 p-3">
      <p className="text-sm">Choose an item, then click the map to place it. Keep browsing to add more.</p>
      <input aria-label="Search individual items" placeholder="Search benches, trees, lights…" value={query} onChange={e => { setQuery(e.target.value); setCategoryView(false); }} className="min-h-11 w-full rounded-lg border border-slate-400 bg-white px-3 text-sm" />
      {!categoryView && <>
      <button type="button" onClick={showCategories} className="flex min-h-11 items-center gap-2 rounded-full border-2 border-[#232323] px-3 text-xs font-bold hover:bg-[#c9ff3d]"><ArrowLeft size={16} aria-hidden="true"/>All categories</button>
      <select aria-label="Item category" value={category} onChange={e => setCategory(e.target.value)} className="min-h-11 w-full rounded-lg border border-slate-400 bg-white px-3 text-sm">
        {['All', ...DETAIL_CATEGORIES].map(c => <option key={c} value={c}>{c === 'All' ? 'All individual items' : c}</option>)}
      </select>
      <p className="text-xs text-slate-600">{options.length} items · actual 3D model previews</p>
      {options.some(a=>a.safety) && <p className="rounded border border-amber-300 bg-amber-50 p-2 text-xs">Traffic-safety kits are visualization assets, not approved construction or operational traffic-control designs. Amber is static.</p>}
      </>}
    </div>
    <div key={categoryView ? 'categories' : category} className="min-h-0 flex-1 overflow-y-auto p-3">
      {categoryView ? <DetailCategoryTiles onChoose={value => { setCategory(value); setQuery(''); setCategoryView(false); }} onBrowseAll={() => { setCategory('All'); setQuery(''); setCategoryView(false); }}/> : <>
      <div className="grid grid-cols-2 gap-3">
        <SafetyVariantCards assets={options.filter(a=>a.safety)} selected={placement.selected} disabled={!canEdit || placement.saving} onChoose={placement.choose} thumbnail={Thumbnail}/>
        {options.filter(asset=>!asset.safety).map(asset => <article key={asset.id} className="overflow-hidden rounded-xl border border-slate-300 bg-white">
          <button type="button" aria-label={`Choose ${asset.label}`} aria-pressed={placement.selected === asset.id} disabled={!canEdit || placement.saving}
            onClick={() => placement.choose(asset.id)} className={`w-full text-left hover:bg-lime-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-[-3px] disabled:opacity-50 ${placement.selected === asset.id ? 'bg-lime-100 ring-2 ring-inset ring-lime-600' : ''}`}>
            <Thumbnail asset={asset} />
            <span className="block space-y-1 p-3"><span className="block text-sm font-bold">{asset.label}</span>
              <span className="block line-clamp-2 text-xs text-slate-600">{asset.description}</span>
              <span className="block text-[11px] text-slate-600">{asset.dimensions.map(n => n.toFixed(1)).join(' × ')} m</span>
              <span className="block pt-1 text-xs font-semibold underline">Choose & place</span></span>
          </button>
        </article>)}
      </div>
      {!options.length && <p className="py-4 text-sm">No matching items. Try another search or category.</p>}
      </>}
    </div>
    </>}
    </div>
    <footer className="shrink-0 space-y-2 border-t border-slate-300 bg-white p-3">
      {!placement.editing && <DetailEditControls placement={placement} />}
      {selected && <><p className="text-sm font-semibold">Placing: {selected.label}</p>
        <div className="flex items-center gap-2"><label className="text-xs">Rotation <input aria-label="Detail rotation" type="number" step="15" value={placement.angle} disabled={placement.saving} onChange={e => placement.setAngle(Number(e.target.value) || 0)} className="w-20 rounded border border-slate-400 p-2" /></label>
          <button type="button" className="ml-auto min-h-11 rounded-lg border border-slate-400 px-3 text-xs" onClick={() => placement.choose(null)}>Stop placing</button></div></>}
      <p role="status" className={`text-xs ${placement.error ? 'text-amber-900' : 'text-slate-600'}`}>{placement.saving ? 'Saving item…' : placement.error || placement.status || (canEdit ? 'Each placement saves automatically.' : 'View only. Editing access is required to place items.')}</p>
      <button type="button" disabled={placement.saving} onClick={onArrange} className="min-h-10 w-full rounded-lg border border-slate-400 bg-white px-3 text-sm">Arrange details & custom paving</button>
    </footer>
  </aside>;
}
