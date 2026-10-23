import { useEffect, useRef, useState } from 'react';
import { ArrowLeft, X } from 'lucide-react';
import { DETAIL_CATEGORIES, searchDetails, detailAsset, type DetailAsset } from './detailCatalogue';
import { detailThumbnail } from './detailThumbnail';
import type { useDetailPlacement } from './useDetailPlacement';
import { DetailEditControls } from './DetailEditControls';
import { DetailCategoryTiles } from './DetailCategoryTiles';
import { SafetyVariantCards } from './SafetyVariantCards';
import { useNarrowViewport } from '@/hooks/useNarrowViewport';

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
  return <div ref={root} className={`flex ${asset.appearancePreview ? 'h-52' : 'h-28'} items-center justify-center bg-slate-100 text-xs text-slate-500`}>
    {image ? <img src={image} alt={asset.appearancePreview ? `${asset.appearancePreview.name} · ${asset.appearancePreview.style} · AI appearance preview` : asset.label} className="h-full w-full object-contain" /> : failed ? 'Preview unavailable' : 'Loading preview…'}
  </div>;
}

export function DetailPlacementPanel({ placement, canEdit, onClose, onArrange }: {
  placement: ReturnType<typeof useDetailPlacement>; canEdit: boolean; onClose: () => void; onArrange: () => void;
}) {
  const [query, setQuery] = useState(''), [category, setCategory] = useState('All');
  const narrow = useNarrowViewport();
  const editingId = placement.editing?.id;
  const context = placement.selected ? `place:${placement.selected}` : editingId ? `edit:${editingId}` : 'browse';
  const [expandedFor, setExpandedFor] = useState<string | null>('browse');
  const expanded = expandedFor === context;
  const compact = narrow && !expanded;
  const [categoryView, setCategoryView] = useState(true);
  const scrollArea = useRef<HTMLDivElement>(null);
  useEffect(() => { if (scrollArea.current) scrollArea.current.scrollTop = 0; }, [placement.editing?.id]);
  const [view, setView] = useState<'browse' | 'placed'>('browse');
  const showCategories = () => { setCategory('All'); setQuery(''); setCategoryView(true); };
  const options = searchDetails(query, category);
  const appearanceCount = options.filter(asset => asset.appearancePreview).length;
  const selected = placement.selected ? detailAsset(placement.selected) : null;
  const choose = (id: string | null) => { placement.choose(id); if (narrow && id) setExpandedFor(null); };
  return <aside aria-label="Detail catalogue" className={`fixed bottom-0 inset-x-0 z-[80] flex max-h-[65dvh] flex-col rounded-t-2xl border border-slate-300 bg-[#fff9ec] text-slate-950 shadow-2xl lg:left-auto lg:top-16 lg:w-[420px] lg:max-w-[calc(100vw-3rem)] lg:max-h-none lg:rounded-none ${compact ? '!max-h-[42dvh]' : ''}`}
    onPointerDown={e => e.stopPropagation()} onWheel={e => e.stopPropagation()}>
    <header className="flex shrink-0 items-center justify-between border-b border-slate-200 p-4">
      <h2 className="text-lg font-bold">Add details</h2>
      {narrow && <button type="button" aria-expanded={expanded} aria-label={expanded ? 'Collapse detail catalogue' : 'Expand detail catalogue'} onClick={() => setExpandedFor(expanded ? null : context)} className="ml-auto min-h-11 rounded-lg px-3 text-sm font-semibold hover:bg-lime-100">{expanded ? 'Show map' : 'Browse / more'}</button>}
      <button type="button" aria-label="Close detail catalogue" onClick={onClose} className="flex h-11 w-11 items-center justify-center rounded-lg hover:bg-slate-200"><X size={22} /></button>
    </header>
    {!compact && <>
    <div className="flex shrink-0 gap-2 border-b border-slate-200 p-3" aria-label="Detail views">
      <button type="button" aria-pressed={view === 'browse'} onClick={() => setView('browse')} className={`min-h-11 flex-1 rounded-full border-2 border-slate-900 text-sm font-bold ${view === 'browse' ? 'bg-[#c9ff3d]' : 'bg-white'}`}>Browse catalogue</button>
      <button type="button" aria-pressed={view === 'placed'} onClick={() => { setView('placed'); placement.choose(null); }} className={`min-h-11 flex-1 rounded-full border-2 border-slate-900 text-sm font-bold ${view === 'placed' ? 'bg-[#c9ff3d]' : 'bg-white'}`}>Placed items ({placement.items.length})</button>
    </div>
    {!categoryView && <button type="button" onClick={() => {setView('browse');setCategory('People');setQuery('');setCategoryView(false);}}
      className="mx-3 mt-3 min-h-11 shrink-0 rounded-xl border-2 border-slate-900 bg-lime-100 px-3 text-left text-sm font-extrabold">People · choose a person & action</button>}
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
      <p className="text-xs text-slate-600">{options.length} items · {appearanceCount > 0 ? appearanceCount === options.length ? 'AI appearance previews' : 'model and AI appearance previews' : 'actual 3D model previews'}</p>
      {appearanceCount > 0 && <p className="rounded-lg border border-lime-200 bg-lime-50 p-2 text-xs text-slate-700">Realistic style previews. Placed people use simplified 3D models; AI results may vary.</p>}
      {options.some(a=>a.safety) && <p className="rounded border border-amber-300 bg-amber-50 p-2 text-xs">Traffic-safety kits are visualization assets, not approved construction or operational traffic-control designs. Amber is static.</p>}
      </>}
    </div>
    <div key={categoryView ? 'categories' : category} className="min-h-0 flex-1 overflow-y-auto p-3">
      {categoryView ? <DetailCategoryTiles onChoose={value => { setCategory(value); setQuery(''); setCategoryView(false); }} onBrowseAll={() => { setCategory('All'); setQuery(''); setCategoryView(false); }}/> : <>
      <div className="grid grid-cols-2 gap-3">
        <SafetyVariantCards assets={options.filter(a=>a.safety)} selected={placement.selected} disabled={!canEdit || placement.saving} onChoose={choose} thumbnail={Thumbnail}/>
        {options.filter(asset=>!asset.safety).map(asset => <article key={asset.id} className="overflow-hidden rounded-xl border border-slate-300 bg-white">
          <button type="button" aria-label={`Choose ${asset.appearancePreview ? `${asset.appearancePreview.name} · ${asset.appearancePreview.style}` : asset.label}`} aria-pressed={placement.selected === asset.id} disabled={!canEdit || placement.saving}
            onClick={() => choose(asset.id)} className={`w-full text-left hover:bg-lime-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-[-3px] disabled:opacity-50 ${placement.selected === asset.id ? 'bg-lime-100 ring-2 ring-inset ring-lime-600' : ''}`}>
            <Thumbnail asset={asset} />
            <span className="block space-y-1 p-3"><span className="block text-sm font-bold">{asset.appearancePreview?.name ?? asset.label}</span>
              <span className="block line-clamp-2 text-xs text-slate-600">{asset.appearancePreview?.style ?? asset.description}</span>
              {asset.appearancePreview && <span className="block text-[10px] font-semibold uppercase tracking-wide text-slate-500">AI appearance preview</span>}
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
    </>}
    <footer className="min-h-0 shrink-0 space-y-2 overflow-y-auto border-t border-slate-300 bg-white p-3">
      {(!placement.editing || compact) && <DetailEditControls placement={placement} compact={compact} />}
      {selected && <><p className="text-sm font-semibold">Placing: {selected.label}</p>
        <div className="flex items-center gap-2"><label className="text-xs">Rotation <input aria-label="Detail rotation" type="number" step="15" value={placement.angle} disabled={placement.saving} onChange={e => placement.setAngle(Number(e.target.value) || 0)} className="w-20 rounded border border-slate-400 p-2" /></label>
          <button type="button" className="ml-2 min-h-11 rounded-lg border border-slate-400 px-3 text-xs sm:ml-auto" onClick={() => placement.choose(null)}>Stop placing</button></div></>}
      <p role="status" className={`text-xs ${placement.error ? 'text-amber-900' : 'text-slate-600'}`}>{placement.saving ? 'Saving item…' : placement.error || placement.status || (canEdit ? 'Each placement saves automatically.' : 'View only. Editing access is required to place items.')}</p>
      {!compact && <button type="button" disabled={placement.saving} onClick={onArrange} className="min-h-11 w-full rounded-lg border border-slate-400 bg-white px-3 text-sm">Arrange details & custom paving</button>}
    </footer>
  </aside>;
}
