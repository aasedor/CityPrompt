import { useEffect, useRef, useState } from 'react';
import { legoAssemblyApi } from '@/features/legoAssembly/legoAssemblyApi';
import { buildPlanRequestForItem, deriveItems } from '@/features/legoAssembly/communityCompiler';
import { getApiErrorMessage } from '@/services/api';
import type { SiteZone, SiteZoneProperties } from '@/types';
import { CANONICAL_CHOICES, canonicalDrawing } from './canonicalCatalogue';
import { canonicalBuildingAsset } from './canonicalBuildingPlacement';
import { assetForZone, placementProperties } from './catalogue';
import { savedModelRevision } from './savedModelRevision';
import { withStoreyMetadata, type PlaceAsset } from './assetRegistry';
import { storeyProgramHeight, storeyProgramSupports } from './buildingStoreyProgram';
import { footprintProgramSupports } from './buildingFootprintProgram';
import {
  RESIZE_TRIAL_SETTINGS, decideResizeTrialStretch, exactModelProperties, fitResizeTrialScalesToPlot,
  readResizeTrialState, resizeTrialBuildingSize, resizeTrialOutlineFrame, resizeTrialOutlineProblem,
  resizeTrialPlotFor, resizeTrialRectangle, shapeFreelyProperties, type ResizeTrialMode,
} from './buildingResizeTrial';

const choices = CANONICAL_CHOICES.filter(choice => choice.domain === 'building');
const field = 'mt-1 min-h-11 w-full rounded border border-slate-400 bg-white px-2 text-sm text-slate-900';
const heightText = (value: unknown) => String(Math.round(Number(value) * 100) / 100);
const metres = (value: number) => String(Math.round(value * 100) / 100);
const percent = (value: number) => `${Math.round(value * 100)}%`;

/** Essential design properties share the existing save/undo/compiler path. */
export function BuildingDesignControls({ zone, disabled, onSave, requireExplicitSelection = false }: {
  zone: SiteZone; disabled: boolean;
  /** `coordinates` is set only by the building resize pilot, when a stretch or
   * a mode change must move the saved outline together with its properties. */
  onSave: (properties: SiteZoneProperties, coordinates?: number[][]) => void;
  requireExplicitSelection?: boolean;
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
  const [choiceId, setChoiceId] = useState(requireExplicitSelection ? '' : initialChoice?.id ?? '');
  const [variantId, setVariantId] = useState(requireExplicitSelection ? '' : initialVariant);
  const [query, setQuery] = useState('');
  const [floors, setFloors] = useState(String(initialFloors));
  const [height, setHeight] = useState(heightText(initialHeight ?? assetForZone(zone)?.nativeDimensions?.[2]));
  const [footprintScale, setFootprintScale] = useState(String(savedProperties.building_footprint_scale ?? 1));
  const [heightEdited, setHeightEdited] = useState(false);
  const [checking,setChecking] = useState(false);
  const [runtimeError,setRuntimeError] = useState('');
  const active = useRef(true);
  const pending = useRef(false);
  // Connections and other editors can save while the model check is pending.
  // A refetch with identical content is safe; a newer authored zone is not.
  const zoneSnapshot = JSON.stringify([zone.id, zone.project_id, zone.updated_at, zone.zone_type, zone.coordinates, savedProperties]);
  const latestZoneSnapshot = useRef(zoneSnapshot);
  latestZoneSnapshot.current = zoneSnapshot;
  useEffect(()=>{active.current=true;return()=>{active.current=false;};},[]);
  const choice = choices.find(c => c.id === choiceId);
  const variant = choice?.option.variants?.find(v => v.id === variantId);
  const selectedAsset = choiceId === initialChoice?.id && variantId === initialVariant ? initialAsset
    : choice?.placements.find(asset => asset.kind === 'object' && asset.model.variantId === variantId);
  const storeyProgram = selectedAsset?.kind === 'object' ? selectedAsset.storeyProgram : undefined;
  const selectedFootprintProgram = selectedAsset?.kind === 'object' ? selectedAsset.footprintProgram : undefined;
  // Building resize pilot. `trial` is null unless its flag is on AND the saved
  // building is the one pinned model, still selected in this form. Its
  // independent-axis programme has its own controls below, so the uniform
  // house-pilot slider and its saved fields stay out of the way.
  const trial = !requireExplicitSelection && choiceId === initialChoice?.id && variantId === initialVariant
    ? readResizeTrialState(savedProperties) : null;
  const footprintProgram = selectedFootprintProgram?.mode === 'independent_horizontal_scale' ? undefined : selectedFootprintProgram;
  const outline = trial && zone.coordinates.length >= 3 ? resizeTrialOutlineFrame(zone.coordinates) : null;
  const clampScale = (value: number) => Math.max(RESIZE_TRIAL_SETTINGS.scaleMin, Math.min(RESIZE_TRIAL_SETTINGS.scaleMax, value));
  // Returning from Shape freely starts from the nearest size the exact model can take.
  const trialStart = !trial || !outline ? null : trial.mode === 'exact_model'
    ? resizeTrialBuildingSize(trial.family, trial.widthScale, trial.depthScale)
    : resizeTrialBuildingSize(trial.family, clampScale(outline.widthM / trial.family.nativeWidthM), clampScale(outline.depthM / trial.family.nativeDepthM));
  const [trialMode, setTrialMode] = useState<ResizeTrialMode>(trial?.mode ?? 'exact_model');
  const [trialWidth, setTrialWidth] = useState(trialStart ? metres(trialStart.widthM) : '');
  const [trialDepth, setTrialDepth] = useState(trialStart ? metres(trialStart.depthM) : '');
  // The inputs show centimetres; the saved stretch is finer. Until a size is
  // actually typed, Apply must not round the building to what is displayed.
  const [trialSizeEdited, setTrialSizeEdited] = useState(false);
  const trialDecision = trial && trialMode === 'exact_model' && Number(trialWidth) > 0 && Number(trialDepth) > 0
    ? decideResizeTrialStretch(trial.family, Number(trialWidth), Number(trialDepth)) : null;
  // A size beyond the band becomes a freely shaped rectangle, which has limits of its own.
  const trialHandoverProblem = trial && outline && trialDecision?.kind === 'shape_freely'
    ? resizeTrialOutlineProblem(resizeTrialRectangle(outline.center, trialDecision.widthM, trialDecision.depthM, outline.degrees)) : null;
  const trialValid = !trial || trialMode === 'shape_freely' || Boolean(outline && trialDecision && !trialHandoverProblem);
  const filtered = choices.filter(c => c.id === choiceId || `${c.option.label} ${c.option.description}`.toLowerCase().includes(query.toLowerCase()));
  const floorCountValid = Number.isInteger(Number(floors))
    && Number(floors) >= (storeyProgram?.minStoreys ?? 1)
    && Number(floors) <= (storeyProgram?.maxStoreys ?? 100);
  const baseValid = choice && (!choice.option.variants?.length || Boolean(variant)) && floorCountValid
    && !(choiceId === initialChoice?.id && variantId === initialVariant && savedProperties.pick_place_model_revision && !initialAsset)
    && height.trim() !== '' && Number.isFinite(Number(height)) && Number(height) > 0 && Number(height) <= 1000
    && (!storeyProgram || storeyProgramSupports(storeyProgram, floors, height))
    && (!footprintProgram || footprintProgram.editable === false || footprintProgramSupports(footprintProgram, footprintScale));
  const valid = baseValid && trialValid;
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
  const changeStoreys = (value: string) => {
    setFloors(value);
    setHeight(String(storeyProgram ? storeyProgramHeight(storeyProgram, Number(value))
      : Number(value) * (variant?.suggestedFloorHeight ?? choice?.option.suggestedFloorHeight ?? 3.2)));
    setHeightEdited(true);
  };
  /** Building resize pilot: what one Apply (or Fit building to plot) saves.
   * null means the pilot has nothing to change and the ordinary save runs. */
  const resolveTrialSave = (base: SiteZoneProperties, fitToPlot: boolean):
    { properties: SiteZoneProperties; coordinates?: number[][]; checkStretch?: boolean; problem?: string } | null => {
    if (!trial || !outline) return null;
    const { family } = trial;
    const rectangle = (widthM: number, depthM: number) => resizeTrialRectangle(outline.center, widthM, depthM, outline.degrees);
    if (trialMode === 'shape_freely' && !fitToPlot) {
      if (trial.mode === 'shape_freely') return null;
      // The outline starts as the building the student was just looking at.
      const size = resizeTrialBuildingSize(family, trial.widthScale, trial.depthScale);
      return { properties: shapeFreelyProperties(base), coordinates: rectangle(size.widthM, size.depthM) };
    }
    if (!fitToPlot && !trialSizeEdited && trial.mode === 'exact_model') return null;
    const fit = fitToPlot ? fitResizeTrialScalesToPlot(family, outline.widthM, outline.depthM) : null;
    const requested = fit ? resizeTrialBuildingSize(family, fit.widthScale, fit.depthScale)
      : { widthM: Number(trialWidth), depthM: Number(trialDepth) };
    const decision = decideResizeTrialStretch(family, requested.widthM, requested.depthM);
    if (decision.kind === 'shape_freely') {
      // Outside the band: hand over to Shape freely at the size asked for.
      const coordinates = rectangle(decision.widthM, decision.depthM);
      const problem = resizeTrialOutlineProblem(coordinates);
      return problem ? { properties: base, problem }
        : { properties: shapeFreelyProperties(base, decision.reason), coordinates };
    }
    if (trial.mode === 'exact_model' && decision.widthScale === trial.widthScale && decision.depthScale === trial.depthScale) return null;
    const needed = resizeTrialPlotFor(family, decision.widthScale, decision.depthScale);
    // A larger building takes the room it needs; a plot is never shrunk here.
    const keepPlot = trial.mode === 'exact_model';
    const widthM = keepPlot ? Math.max(outline.widthM, needed.widthM) : needed.widthM;
    const depthM = keepPlot ? Math.max(outline.depthM, needed.depthM) : needed.depthM;
    const moved = !keepPlot || widthM > outline.widthM + 0.05 || depthM > outline.depthM + 0.05;
    return { properties: exactModelProperties(base, family, decision.widthScale, decision.depthScale,
      selectedAsset?.kind === 'object' ? selectedAsset as PlaceAsset : undefined), checkStretch: true,
      ...(moved ? { coordinates: rectangle(widthM, depthM) } : {}) };
  };
  const apply = async (fitToPlot = false) => {
    if (!(fitToPlot ? baseValid : valid) || !choice || disabled || pending.current) return;
    const changedType = choiceId !== initialChoice?.id || variantId !== savedProperties.development_selected_variant_id;
    const selection = { choice, variant };
    const native = choice.placements.find(a => a.kind === 'object' && a.model.variantId === variantId);
    const properties = changedType ? { ...savedProperties, native_home_plot: undefined,
      building_footprint_scale: undefined, building_footprint_program_id: undefined,
      building_footprint_native_width_m: undefined, building_footprint_native_depth_m: undefined,
      model_native_dimensions_m: undefined, model_dimensions_revision: undefined, pick_place_model_revision: undefined,
      // A different building leaves the resize pilot's state behind.
      building_footprint_mode: undefined, building_footprint_width_scale: undefined,
      building_footprint_depth_scale: undefined, building_footprint_mode_reason: undefined,
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
    const nextProperties:SiteZoneProperties = { ...properties, pick_place_automatic_3d: true, native_plot_axes: true,
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
    };
    setRuntimeError('');
    const trialSave = changedType ? null : resolveTrialSave(nextProperties, fitToPlot);
    if (trialSave?.problem) { setRuntimeError(trialSave.problem); return; }
    const savedNext = trialSave?.properties ?? nextProperties;
    const needsAuthoredAssembly = storeyProgram && storeyProgram.mode !== 'fixed_authored_assembly'
      && (Number(floors) !== storeyProgram.nativeStoreys || Number(floors) !== Number(savedFloors));
    const needsScaledAssembly = footprintProgram && (selectedFootprintScale !== footprintProgram.defaultScale
      || selectedFootprintScale !== Number(savedProperties.building_footprint_scale ?? footprintProgram.defaultScale));
    if (needsAuthoredAssembly || needsScaledAssembly || trialSave?.checkStretch) {
      pending.current=true;setChecking(true);
      try {
        const item=deriveItems([{...zone,coordinates:trialSave?.coordinates ?? zone.coordinates,properties:savedNext}])[0];
        if (!item) throw new Error('This building cannot be checked against the current model library.');
        const plan=await legoAssemblyApi.plan(buildPlanRequestForItem(item));
        if (!active.current) return;
        // Only the server can stretch the exact model. Anything else is not a stretch.
        if (trialSave?.checkStretch && !plan?.fit?.resize_trial) {
          throw new Error('The server did not stretch this model. Check that the building resize pilot is switched on for the server as well.');
        }
      } catch(error) {
        if(active.current)setRuntimeError(`The building was not changed. ${getApiErrorMessage(error)}`);
        return;
      } finally {
        pending.current=false;if(active.current)setChecking(false);
      }
    }
    if (latestZoneSnapshot.current !== zoneSnapshot) {
      setRuntimeError('The building changed while its model was being checked. Review it and apply again.');
      return;
    }
    if (trialSave?.coordinates) onSave(savedNext, trialSave.coordinates);
    else onSave(savedNext);
  };
  return <form className="mb-3 space-y-2 border-b border-slate-300 pb-3" onSubmit={event => { event.preventDefault(); void apply(); }}>
    <fieldset disabled={checking} className="min-w-0 space-y-2">
    {Boolean(savedProperties.pick_place_model_revision) && !initialAsset && choiceId === initialChoice?.id && variantId === initialVariant
      && <p role="alert" className="text-xs text-amber-800">This saved model revision is unavailable. Your design is preserved. Select another building explicitly to replace it.</p>}
    <label className="block text-xs font-semibold">Find building type<input type="search" value={query} onChange={e => setQuery(e.target.value)} className={field} /></label>
    <label className="block text-xs font-semibold">Building type<select value={choiceId} onChange={e => choose(e.target.value)} className={field}>
      {!choice && <option value="">{requireExplicitSelection ? 'Choose a detailed building' : 'Current building'}</option>}
      {filtered.map(c => <option value={c.id} key={c.id}>{c.option.label}</option>)}
    </select></label>
    {Boolean(choice?.option.variants?.length) && <label className="block text-xs font-semibold">Building variant<select value={variantId} onChange={e => choose(choiceId, e.target.value)} className={field}>
      {choice?.option.variants?.map(v => <option value={v.id} key={v.id}>{v.label}</option>)}
    </select></label>}
    {storeyProgram?.mode==='fixed_authored_assembly' ? <p className="text-sm text-slate-700">{floors} {Number(floors)===1?'storey':'storeys'} · {height} m high</p> : <div className="grid grid-cols-2 gap-2">
      <label className="text-xs font-semibold">Storeys{storeyProgram?.supportedStoreys
        ? <select value={floors} onChange={e=>changeStoreys(e.target.value)} className={field}>
          {!storeyProgram.supportedStoreys.includes(Number(floors)) && <option value={floors} disabled>Saved: {floors}</option>}
          {storeyProgram.supportedStoreys.map(count=><option key={count} value={count}>{count}</option>)}
        </select>
        : <input type="number" min={storeyProgram?.minStoreys ?? 1} max={storeyProgram?.maxStoreys ?? 100} value={floors}
          onChange={e=>changeStoreys(e.target.value)} className={field} />}</label>
      <label className="text-xs font-semibold">Height (m)<input type="number" min="0.1" max="1000" step="any" value={height}
        readOnly={Boolean(storeyProgram)} aria-readonly={Boolean(storeyProgram)}
        onChange={e => { setHeight(e.target.value); setHeightEdited(true); }} className={`${field} ${storeyProgram ? 'bg-slate-100' : ''}`} /></label>
    </div>}
    {footprintProgram && footprintProgram.editable !== false && <label className="block text-xs font-semibold">Building footprint ({Math.round(Number(footprintScale) * 100)}%)
      <input aria-label="Building footprint (%)" type="range"
        min={Math.round(footprintProgram.minScale * 100)} max={Math.round(footprintProgram.maxScale * 100)}
        step={Math.round(footprintProgram.step * 100)} value={Math.round(Number(footprintScale) * 100)}
        onChange={e => setFootprintScale(String(Number(e.target.value) / 100))}
        className="mt-1 min-h-11 w-full accent-lime-500" />
      <span className="block font-normal text-slate-600">Changes width and depth together. Storeys and height stay unchanged.</span>
    </label>}
    {trial && outline && <fieldset className="min-w-0 rounded-lg border border-slate-400 bg-white p-2">
      <legend className="px-1 text-xs font-semibold">Fit this building to your space</legend>
      <div role="radiogroup" aria-label="Building shape" className="grid grid-cols-2 gap-2">
        {(['exact_model', 'shape_freely'] as const).map(mode => <label key={mode}
          className={`flex min-h-11 cursor-pointer items-center justify-center rounded-lg border px-2 text-sm font-semibold ${trialMode === mode ? 'border-slate-900 bg-lime-200' : 'border-slate-400 bg-white'}`}>
          <input type="radio" name={`building-shape-${zone.id}`} className="sr-only" checked={trialMode === mode}
            onChange={() => setTrialMode(mode)} />
          {mode === 'exact_model' ? 'Exact model' : 'Shape freely'}</label>)}
      </div>
      {trial.mode === 'shape_freely' && <p role="status" className="mt-2 rounded bg-amber-50 p-2 text-xs text-slate-900">
        <span className="font-semibold">{trial.reason === 'stretch_out_of_band'
          ? `Switched to Shape freely automatically. The size you asked for is outside the exact model’s ${percent(RESIZE_TRIAL_SETTINGS.scaleMin)}–${percent(RESIZE_TRIAL_SETTINGS.scaleMax)} range.`
          : 'This building is shaped freely.'}</span>{' '}
        It is shown as shaped massing with floor lines and repeating window bays, not the detailed model. Choose Exact model to return to the detailed building.</p>}
      {trialMode === 'exact_model' ? <>
        <div className="mt-2 grid grid-cols-2 gap-2">
          <label className="text-xs font-semibold">Building width (m)<input aria-label="Building width (m)" type="number" step="any"
            min={RESIZE_TRIAL_SETTINGS.minWidthM} max={RESIZE_TRIAL_SETTINGS.maxSizeM} value={trialWidth}
            onChange={e => { setTrialWidth(e.target.value); setTrialSizeEdited(true); }} className={field} />
            <span className="block font-normal text-slate-600">{Number(trialWidth) > 0 ? percent(Number(trialWidth) / trial.family.nativeWidthM) : '—'} of the model</span></label>
          <label className="text-xs font-semibold">Building depth (m)<input aria-label="Building depth (m)" type="number" step="any"
            min={RESIZE_TRIAL_SETTINGS.minDepthM} max={RESIZE_TRIAL_SETTINGS.maxSizeM} value={trialDepth}
            onChange={e => { setTrialDepth(e.target.value); setTrialSizeEdited(true); }} className={field} />
            <span className="block font-normal text-slate-600">{Number(trialDepth) > 0 ? percent(Number(trialDepth) / trial.family.nativeDepthM) : '—'} of the model</span></label>
        </div>
        {trial.mode === 'exact_model' && <button type="button" disabled={disabled || checking || !baseValid} onClick={() => { void apply(true); }}
          className="mt-2 min-h-11 w-full rounded-lg border border-slate-700 bg-white text-sm font-semibold disabled:opacity-40">Fit building to plot</button>}
        <p className="mt-2 text-xs text-slate-600">The exact model stretches {metres(trial.family.nativeWidthM * RESIZE_TRIAL_SETTINGS.scaleMin)}–{metres(trial.family.nativeWidthM * RESIZE_TRIAL_SETTINGS.scaleMax)} m wide and {metres(trial.family.nativeDepthM * RESIZE_TRIAL_SETTINGS.scaleMin)}–{metres(trial.family.nativeDepthM * RESIZE_TRIAL_SETTINGS.scaleMax)} m deep ({percent(RESIZE_TRIAL_SETTINGS.scaleMin)}–{percent(RESIZE_TRIAL_SETTINGS.scaleMax)}). Height and storeys never change.</p>
        {trialDecision?.kind === 'shape_freely' && !trialHandoverProblem && <p role="status" className="mt-1 text-xs font-semibold text-amber-900">This size is outside the exact model’s range. Applying switches this building to Shape freely.</p>}
        {trialHandoverProblem && <p role="alert" className="mt-1 text-xs text-red-700">{trialHandoverProblem}</p>}
      </> : trial.mode === 'exact_model' && <p className="mt-2 text-xs text-slate-600">Applying replaces the detailed model with an outline you can reshape: drag its corners or add points. Storeys and floor height stay the same. Window bays repeat at a fixed width; they never stretch.</p>}
    </fieldset>}
    <p className="text-xs text-slate-600">{storeyProgram
      ? storeyProgram.mode === 'fixed_authored_assembly'
        ? `This exact model is currently available at ${storeyProgram.nativeStoreys} ${storeyProgram.nativeStoreys === 1 ? 'storey' : 'storeys'}.`
        : storeyProgram.mode === 'select_authored_assembly'
        ? `Choose ${storeyProgram.supportedStoreys?.join(', ') ?? `${storeyProgram.minStoreys}–${storeyProgram.maxStoreys}`} storeys. Each choice uses a complete authored building with its walls, openings and roof intact.`
        : `Choose ${storeyProgram.minStoreys}–${storeyProgram.maxStoreys} storeys.${storeyProgram.recommendedMinStoreys && storeyProgram.recommendedMinStoreys !== storeyProgram.minStoreys ? ` Recommended: ${storeyProgram.recommendedMinStoreys}–${storeyProgram.recommendedMaxStoreys ?? storeyProgram.maxStoreys}.` : ''} The podium and roof stay complete while authored floors repeat at full proportions.`
      : 'Your footprint stays in place. Unsupported sizes use design massing.'}</p>
    {runtimeError && <p role="alert" className="text-xs text-amber-900">{runtimeError}</p>}
    <button disabled={disabled || !valid || checking} className="min-h-11 w-full rounded-lg border border-slate-700 bg-lime-200 text-sm font-semibold disabled:opacity-40">{checking?'Checking detailed model…':'Apply building'}</button>
    </fieldset>
  </form>;
}
