import { useState } from 'react';
import type { SiteZone, SiteZoneProperties } from '@/types';
import { CANONICAL_CHOICES } from './canonicalCatalogue';
import { canonicalStreetAsset, streetDesignUpdate } from './canonicalStreetPlacement';

const choices = CANONICAL_CHOICES.filter(c => c.domain === 'street_pathway');
const defaults = choices.map(choice => canonicalStreetAsset({ choice, variant: choice.option.variants?.[0] }));
const widths = [...new Set(defaults.map(a => a.sectionWidth))].sort((a, b) => a - b);
const field = 'mt-1 min-h-11 w-full rounded border border-slate-400 bg-white px-2 text-sm';

export function StreetDesignControls({ zone, disabled, onSave }: {
  zone: SiteZone; disabled: boolean;
  onSave: (data: { coordinates: number[][]; properties: SiteZoneProperties }) => void;
}) {
  const [parent, setParent] = useState(String(zone.properties?.road_archetype_id ?? ''));
  const [variantId, setVariantId] = useState(String(zone.properties?.road_selected_variant_id ?? ''));
  const [query, setQuery] = useState('');
  const choice = choices.find(c => c.option.id === parent);
  const variant = choice?.option.variants?.find(v => v.id === variantId);
  const asset = choice ? canonicalStreetAsset({ choice, variant }) : undefined;
  const choose = (id: string) => { const next = choices.find(c => c.option.id === id)!; setParent(id); setVariantId(next.option.variants?.[0]?.id ?? ''); };
  return <form className="my-3 space-y-2" onSubmit={event => { event.preventDefault(); if (asset) onSave(streetDesignUpdate(zone, asset)); }}>
    <label className="block text-xs font-semibold">Find street type<input type="search" className={field} value={query} onChange={e => setQuery(e.target.value)} /></label>
    <label className="block text-xs font-semibold">Street type<select className={field} value={parent} onChange={e => choose(e.target.value)}>
      {choices.filter(c => c.option.id === parent || `${c.option.label} ${c.option.description}`.toLowerCase().includes(query.toLowerCase())).map(c => <option key={c.id} value={c.option.id}>{c.option.label}</option>)}
    </select></label>
    <label className="block text-xs font-semibold">Street variant<select className={field} value={variantId} onChange={e => setVariantId(e.target.value)}>
      {choice?.option.variants?.map(v => <option key={v.id} value={v.id}>{v.label}</option>)}
    </select></label>
    <label className="block text-xs font-semibold">Street width<select className={field} value={asset?.sectionWidth} onChange={e => {
      const next = defaults.find(a => a.sectionWidth === Number(e.target.value)); if (next) choose(String(next.properties.road_archetype_id));
    }}>
      {widths.map(width => <option key={width} value={width}>{width} m · {defaults.filter(a => a.sectionWidth === width).length} street types</option>)}
    </select></label>
    <p className="text-xs text-slate-600">Choosing a width selects a compatible street type. Your route stays in place; sidewalks and lanes keep their defined sizes.</p>
    <button disabled={disabled || !asset} className="min-h-11 w-full rounded-lg border border-slate-700 bg-lime-200 text-sm font-semibold disabled:opacity-40">Apply street</button>
  </form>;
}
