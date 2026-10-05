import { useState } from 'react';
import type { SiteZone, SiteZoneProperties } from '@/types';
import { CANONICAL_CHOICES, canonicalDrawing } from './canonicalCatalogue';
import { canonicalBuildingAsset } from './canonicalBuildingPlacement';
import { assetForZone, placementProperties } from './catalogue';
import { savedModelRevision } from './savedModelRevision';
import { withStoreyMetadata } from './assetRegistry';
import { storeyProgramHeight, storeyProgramSupports } from './buildingStoreyProgram';
import { footprintProgramSupports } from './buildingFootprintProgram';

const choices = CANONICAL_CHOICES.filter(choice => choice.domain === 'building');
const field = 'mt-1 min-h-11 w-full rounded border border-slate-400 bg-white px-2 text-sm text-slate-900';
const heightText = (value: unknown) => String(Math.round(Number(value) * 100) / 100);

/** Essential design properties share the existing save/undo/compiler path. */
export function BuildingDesignControls({ zone, disabled, onSave }: {
  zone: SiteZone; disabled: boolean; onSave: (properties: SiteZoneProperties) => void;
}) {
  const savedProperties = zone.properties ?? {};
  const initialParent = String(savedProperties.development_subcategory ?? savedProperties.development_archetype_id ?? '');
  const initialVariant = String(savedProperties.development_selected_variant_id ?? '');
  const initialChoice = choices.find(c => c.option.id === initialParent && c.option.variants?.some(v => v.id === initialVariant))
    ?? choices.find(c => c.option.id === initialParent);
  const initialCandidate = initialChoice?.placements.find(asset => asset.kind === 'object' && asset.model.variantId === initialVariant);
  const resolvedSaved = initialCandidate?.kind === 'object' ? savedModelRevision(initialCandidate, savedProperties) : initialCandidate;
  const legacySaved = assetForZone(zone);
  const initialAsset = resolvedSaved ?? (legacySaved && legacySaved.model.revision === savedProperties.pick_place_model_revision
    ? withStoreyMetadata(legacySaved) : undefined);
  const initialStoreyProgram = initialAsset?.kind === 'object' ? initialAsset.storeyProgram : undefined;
  const savedFloors = savedProperties.floor_count ?? savedProperties.floors ?? 2;
  const initialFloors = initialStoreyProgram?.mode === 'fixed_authored_assembly'
    ? initialStoreyProgram.nativeStoreys
    : savedFloors;
  const savedHeight = savedProperties.height_m ?? savedProperties.height
    ?? (initialAsset?.kind === 'object' ? initialAsset.nativeDimensions?.[2] : undefined)
    ?? Number(initialFloors) * 3.2;
  const initialHeight = initialStoreyProgram?.mode === 'fixed_authored_assembly'
    ? storeyProgramHeight(initialStoreyProgram, initialStoreyProgram.nativeStoreys)
    : savedHeight;
  const [choiceId, setChoiceId] = useState(initialChoice?.id ?? '');
  const [variantId, setVariantId] = useState(String(savedProperties.development_selected_variant_id ?? ''));
  const [query, setQuery] = useState('');
  const [floors, setFloors] = useState(String(initialFloors));
  const [height, setHeight] = useState(heightText(initialHeight ?? assetForZone(zone)?.nativeDimensions?.[2]));
  const [footprintScale, setFootprintScale] = useState(String(savedProperties.building_footprint_scale ?? 1));
  const [heightEdited, setHeightEdited] = useState(false);
  const choice = choices.find(c => c.id === choiceId);
  const variant = choice?.option.variants?.find(v => v.id === variantId);
  const selectedAsset = choiceId === initialChoice?.id && variantId === initialVariant ? initialAsset
    : choice?.placements.find(asset => asset.kind === 'object' && asset.model.variantId === variantId);
  const storeyProgram = selectedAsset?.kind === 'object' ? selectedAsset.storeyProgram : undefined;
  const footprintProgram = selectedAsset?.kind === 'object' ? selectedAsset.footprintProgram : undefined;
  const filtered = choices.filter(c => c.id === choiceId || `${c.option.label} ${c.option.description}`.toLowerCase().includes(query.toLowerCase()));
  const floorCountValid = Number.isInteger(Number(floors))
    && Number(floors) >= (storeyProgram?.minStoreys ?? 1)
    && Number(floors) <= (storeyProgram?.maxStoreys ?? 100);
  const valid = choice && floorCountValid
    && !(choiceId === initialChoice?.id && variantId === initialVariant && savedProperties.pick_place_model_revision && !initialAsset)
    && height.trim() !== '' && Number.isFinite(Number(height)) && Number(height) > 0 && Number(height) <= 1000
    && (!storeyProgram || storeyProgramSupports(storeyProgram, floors, height))
    && (!footprintProgram || footprintProgram.editable === false || footprintProgramSupports(footprintProgram, footprintScale));
  const choose = (nextChoiceId: string, nextVariantId?: string) => {
    const next = choices.find(c => c.id === nextChoiceId)!;
    const selectedVariant = next.option.variants?.find(v => v.id === nextVariantId)
      ?? next.option.variants?.find(v => v.id === next.placements[0]?.model.variantId) ?? next.option.variants?.[0];
    const native = next.placements.find(a => a.model.variantId === selectedVariant?.id && a.kind === 'object');
    const props = native?.properties ?? canonicalDrawing({ choice: next, variant: selectedVariant }).properties;
    setChoiceId(nextChoiceId); setVariantId(selectedVariant?.id ?? '');
    setFloors(String(props.floor_count ?? props.floors ?? 2));
    setHeight(heightText(native?.kind === 'object' && native.nativeDimensions ? native.nativeDimensions[2] : props.height ?? Number(props.floors) * 3.2));
    setFootprintScale(String(native?.kind === 'object' && native.footprintProgram ? native.footprintProgram.defaultScale : 1));
    setHeightEdited(false);
  };
  return <form className="mb-3 space-y-2 border-b border-slate-300 pb-3" onSubmit={event => {
    event.preventDefault(); if (!valid || !choice) return;
    const changedType = choiceId !== initialChoice?.id || variantId !== savedProperties.development_selected_variant_id;
    const selection = { choice, variant };
    const native = choice.placements.find(a => a.kind === 'object' && a.model.variantId === variantId);
    const properties = changedType ? { ...savedProperties, native_home_plot: undefined,
      building_footprint_scale: undefined, building_footprint_program_id: undefined,
      building_footprint_native_width_m: undefined, building_footprint_native_depth_m: undefined,
      model_native_dimensions_m: undefined, model_dimensions_revision: undefined, pick_place_model_revision: undefined,
      ...canonicalDrawing(selection).properties, ...(native?.kind === 'object' ? placementProperties(native) : {}),
      pick_place_asset: native?.id ?? canonicalBuildingAsset(selection).id,
      building_archetype_id: choice.option.id, development_height_override_m: undefined,
    } : { ...savedProperties };
    const savedScale = Number(savedProperties.building_footprint_scale);
    const selectedFootprintScale = footprintProgram?.editable !== false
      ? Number(footprintScale)
      : !changedType && footprintProgram && footprintProgramSupports(footprintProgram, savedScale)
        ? savedScale
        : footprintProgram?.defaultScale;
    onSave({ ...properties, pick_place_automatic_3d: true, native_plot_axes: true,
      floors: Number(floors), floor_count: Number(floors), height: Number(height), height_m: Number(height),
      floor_height: storeyProgram?.mode === 'fixed_authored_assembly' ? properties.floor_height : Number(height) / Number(floors),
      ...(footprintProgram && selectedFootprintScale != null ? {
        building_footprint_scale: selectedFootprintScale,
        building_footprint_program_id: footprintProgram.id,
        building_footprint_native_width_m: footprintProgram.nativeWidthM,
        building_footprint_native_depth_m: footprintProgram.nativeDepthM,
      } : {}),
      ...(storeyProgram
        ? { development_height_override_m: storeyProgram.mode === 'fixed_authored_assembly' ? undefined : Number(height) }
        : heightEdited ? { development_height_override_m: Number(height) } : {}),
    });
  }}>
    {Boolean(savedProperties.pick_place_model_revision) && !initialAsset && choiceId === initialChoice?.id && variantId === initialVariant
      && <p role="alert" className="text-xs text-amber-800">This saved model revision is unavailable. Your design is preserved. Select another building explicitly to replace it.</p>}
    <label className="block text-xs font-semibold">Find building type<input type="search" value={query} onChange={e => setQuery(e.target.value)} className={field} /></label>
    <label className="block text-xs font-semibold">Building type<select value={choiceId} onChange={e => choose(e.target.value)} className={field}>
      {!choice && <option value="">Current building</option>}
      {filtered.map(c => <option value={c.id} key={c.id}>{c.option.label}</option>)}
    </select></label>
    {Boolean(choice?.option.variants?.length) && <label className="block text-xs font-semibold">Building variant<select value={variantId} onChange={e => choose(choiceId, e.target.value)} className={field}>
      {choice?.option.variants?.map(v => <option value={v.id} key={v.id}>{v.label}</option>)}
    </select></label>}
    <div className="grid grid-cols-2 gap-2">
      <label className="text-xs font-semibold">Storeys<input type="number" min={storeyProgram?.minStoreys ?? 1} max={storeyProgram?.maxStoreys ?? 100} value={floors}
        readOnly={storeyProgram?.mode === 'fixed_authored_assembly'} aria-readonly={storeyProgram?.mode === 'fixed_authored_assembly'} onChange={e => {
        const nextStoreys = Number(e.target.value);
        setFloors(e.target.value);
        setHeight(String(storeyProgram
          ? storeyProgramHeight(storeyProgram, nextStoreys)
          : nextStoreys * (variant?.suggestedFloorHeight ?? choice?.option.suggestedFloorHeight ?? 3.2)));
        setHeightEdited(true);
      }} className={`${field} ${storeyProgram?.mode === 'fixed_authored_assembly' ? 'bg-slate-100' : ''}`} /></label>
      <label className="text-xs font-semibold">Height (m)<input type="number" min="0.1" max="1000" step="any" value={height}
        readOnly={Boolean(storeyProgram)} aria-readonly={Boolean(storeyProgram)}
        onChange={e => { setHeight(e.target.value); setHeightEdited(true); }} className={`${field} ${storeyProgram ? 'bg-slate-100' : ''}`} /></label>
    </div>
    {footprintProgram && footprintProgram.editable !== false && <label className="block text-xs font-semibold">Building footprint ({Math.round(Number(footprintScale) * 100)}%)
      <input aria-label="Building footprint (%)" type="range"
        min={Math.round(footprintProgram.minScale * 100)} max={Math.round(footprintProgram.maxScale * 100)}
        step={Math.round(footprintProgram.step * 100)} value={Math.round(Number(footprintScale) * 100)}
        onChange={e => setFootprintScale(String(Number(e.target.value) / 100))}
        className="mt-1 min-h-11 w-full accent-lime-500" />
      <span className="block font-normal text-slate-600">Changes width and depth together. Storeys and height stay unchanged.</span>
    </label>}
    <p className="text-xs text-slate-600">{storeyProgram
      ? storeyProgram.mode === 'fixed_authored_assembly'
        ? `This exact model is currently available at ${storeyProgram.nativeStoreys} ${storeyProgram.nativeStoreys === 1 ? 'storey' : 'storeys'}.`
        : storeyProgram.mode === 'select_authored_assembly'
        ? `Choose ${storeyProgram.minStoreys}–${storeyProgram.maxStoreys} storeys. Each choice uses a complete authored house with its walls, openings and roof intact.`
        : `Choose ${storeyProgram.minStoreys}–${storeyProgram.maxStoreys} storeys. The podium and roof stay complete while authored floors repeat at full proportions.`
      : 'Your footprint stays in place. Unsupported sizes use design massing.'}</p>
    <button disabled={disabled || !valid} className="min-h-11 w-full rounded-lg border border-slate-700 bg-lime-200 text-sm font-semibold disabled:opacity-40">Apply building</button>
  </form>;
}
