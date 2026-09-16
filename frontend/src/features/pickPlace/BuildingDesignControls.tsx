import { useState } from 'react';
import type { SiteZone, SiteZoneProperties } from '@/types';
import { CANONICAL_CHOICES, canonicalDrawing } from './canonicalCatalogue';
import { canonicalBuildingAsset } from './canonicalBuildingPlacement';
import { assetForZone } from './catalogue';

const choices = CANONICAL_CHOICES.filter(choice => choice.domain === 'building');
const field = 'mt-1 min-h-11 w-full rounded border border-slate-400 bg-white px-2 text-sm text-slate-900';
const heightText = (value: unknown) => String(Math.round(Number(value) * 100) / 100);

/** Essential design properties share the existing save/undo/compiler path. */
export function BuildingDesignControls({ zone, disabled, onSave }: {
  zone: SiteZone; disabled: boolean; onSave: (properties: SiteZoneProperties) => void;
}) {
  const savedProperties = zone.properties ?? {};
  const initialParent = String(savedProperties.development_subcategory ?? savedProperties.development_archetype_id ?? '');
  const [parent, setParent] = useState(initialParent);
  const [variantId, setVariantId] = useState(String(savedProperties.development_selected_variant_id ?? ''));
  const [query, setQuery] = useState('');
  const [floors, setFloors] = useState(String(savedProperties.floor_count ?? savedProperties.floors ?? 2));
  const [height, setHeight] = useState(heightText(savedProperties.height_m ?? savedProperties.height ?? assetForZone(zone)?.nativeDimensions?.[2] ?? Number(floors) * 3.2));
  const [heightEdited, setHeightEdited] = useState(false);
  const choice = choices.find(c => c.option.id === parent);
  const variant = choice?.option.variants?.find(v => v.id === variantId);
  const filtered = choices.filter(c => c.option.id === parent || `${c.option.label} ${c.option.description}`.toLowerCase().includes(query.toLowerCase()));
  const valid = choice && Number.isInteger(Number(floors)) && Number(floors) >= 1 && Number(floors) <= 100
    && height.trim() !== '' && Number.isFinite(Number(height)) && Number(height) > 0 && Number(height) <= 1000;
  const choose = (nextParent: string, nextVariantId?: string) => {
    const next = choices.find(c => c.option.id === nextParent)!;
    const selectedVariant = next.option.variants?.find(v => v.id === nextVariantId)
      ?? next.option.variants?.find(v => v.id === next.placements[0]?.model.variantId) ?? next.option.variants?.[0];
    const native = next.placements.find(a => a.model.variantId === selectedVariant?.id && a.kind === 'object');
    const props = native?.properties ?? canonicalDrawing({ choice: next, variant: selectedVariant }).properties;
    setParent(nextParent); setVariantId(selectedVariant?.id ?? '');
    setFloors(String(props.floor_count ?? props.floors ?? 2));
    setHeight(heightText(native?.kind === 'object' && native.nativeDimensions ? native.nativeDimensions[2] : props.height ?? Number(props.floors) * 3.2));
    setHeightEdited(false);
  };
  return <form className="mb-3 space-y-2 border-b border-slate-300 pb-3" onSubmit={event => {
    event.preventDefault(); if (!valid || !choice) return;
    const changedType = parent !== initialParent || variantId !== savedProperties.development_selected_variant_id;
    const selection = { choice, variant };
    const native = choice.placements.find(a => a.kind === 'object' && a.model.variantId === variantId);
    const properties = changedType ? { ...savedProperties, native_home_plot: undefined,
      ...canonicalDrawing(selection).properties, ...(native?.properties ?? {}),
      pick_place_asset: native?.id ?? canonicalBuildingAsset(selection).id,
      building_archetype_id: parent, development_height_override_m: undefined,
    } : { ...savedProperties };
    onSave({ ...properties, pick_place_automatic_3d: true, native_plot_axes: true,
      floors: Number(floors), floor_count: Number(floors), height: Number(height), height_m: Number(height),
      floor_height: Number(height) / Number(floors),
      ...(heightEdited ? { development_height_override_m: Number(height) } : {}),
    });
  }}>
    <label className="block text-xs font-semibold">Find building type<input type="search" value={query} onChange={e => setQuery(e.target.value)} className={field} /></label>
    <label className="block text-xs font-semibold">Building type<select value={parent} onChange={e => choose(e.target.value)} className={field}>
      {!choice && <option value={parent}>Current building</option>}
      {filtered.map(c => <option value={c.option.id} key={c.id}>{c.option.label}</option>)}
    </select></label>
    {Boolean(choice?.option.variants?.length) && <label className="block text-xs font-semibold">Building variant<select value={variantId} onChange={e => choose(parent, e.target.value)} className={field}>
      {choice?.option.variants?.map(v => <option value={v.id} key={v.id}>{v.label}</option>)}
    </select></label>}
    <div className="grid grid-cols-2 gap-2">
      <label className="text-xs font-semibold">Storeys<input type="number" min="1" max="100" value={floors} onChange={e => {
        setFloors(e.target.value); setHeight(String(Number(e.target.value) * (variant?.suggestedFloorHeight ?? choice?.option.suggestedFloorHeight ?? 3.2))); setHeightEdited(true);
      }} className={field} /></label>
      <label className="text-xs font-semibold">Height (m)<input type="number" min="0.1" max="1000" step="any" value={height} onChange={e => { setHeight(e.target.value); setHeightEdited(true); }} className={field} /></label>
    </div>
    <p className="text-xs text-slate-600">Your footprint stays in place. Unsupported sizes use design massing.</p>
    <button disabled={disabled || !valid} className="min-h-11 w-full rounded-lg border border-slate-700 bg-lime-200 text-sm font-semibold disabled:opacity-40">Apply building</button>
  </form>;
}
