import { Suspense, useEffect, useMemo, useState } from 'react';
import { createPortal } from 'react-dom';
import { useQueryClient } from '@tanstack/react-query';
import { Canvas } from '@react-three/fiber';
import { Bounds, Environment, Grid, OrbitControls } from '@react-three/drei';
import { AlertTriangle, Bookmark, Box, Check, Loader2, MapPin, Minus, Plus, RefreshCw, Save, Trash2, X } from 'lucide-react';
import { getApiErrorMessage, siteZonesApi } from '@/services/api';
import type { SiteZone, SiteZoneProperties } from '@/types';
import { assemblyFootprintCoordinates, isDetachedArchetype } from './detachedPlot';
import { isNativeClayPlan } from './nativeClayPlacement';
import { computeFootprintFrame } from '@/components/viewer/globe/buildingPlacement';
import {
  legoArchetypeContextFromZone,
  legoAssemblyApi,
  getLegoPlanningFailure,
  type LegoAssemblyPlan,
  type LegoAssemblyRecipe,
  type LegoPlanningFailure,
  type LegoSupportedFamily,
} from './legoAssemblyApi';
import {
  MAX_DIMENSION_M,
  MAX_FLOORS,
  MIN_DIMENSION_M,
  MIN_FLOORS,
  ModuleInstance,
  PreviewErrorBoundary,
  Progress,
  clamp,
  deriveZoneTargets,
  findZoneCatalogOption,
  fitIsStretched,
  normalizeArchetypeId,
} from './legoShared';

function AssemblyScene({ plan }: { plan: LegoAssemblyPlan }) {
  return (
    <>
      <ambientLight intensity={0.8} />
      <directionalLight castShadow position={[8, 12, 7]} intensity={1.5} />
      <directionalLight position={[-8, 5, -6]} intensity={0.35} />
      <Environment preset="city" background={false} />
      <Grid args={[80, 80]} cellSize={1} sectionSize={5} fadeDistance={70} />
      <Bounds fit clip observe margin={1.25}>
        <group>
          {plan.instances.map((instance, index) => (
            <ModuleInstance key={`${instance.asset_id}-${instance.level}-${index}`} instance={instance} nativeScaleLocked={isNativeClayPlan(plan)} />
          ))}
        </group>
      </Bounds>
      <OrbitControls makeDefault enablePan />
    </>
  );
}

function supportedFamilyLabel(supported: LegoSupportedFamily): string {
  const widths = supported.widths_m.length > 0 ? supported.widths_m.join('/') : '?';
  const depths = supported.depths_m.length > 0 ? supported.depths_m.join('/') : '?';
  const floorRange = supported.min_floors != null && supported.max_floors != null
    ? supported.min_floors === supported.max_floors
      ? `${supported.min_floors} floors`
      : `${supported.min_floors}–${supported.max_floors} floors`
    : supported.min_floors != null
      ? `${supported.min_floors}+ floors`
      : supported.max_floors != null
        ? `up to ${supported.max_floors} floors`
        : 'floor range not specified';
  return `${supported.family}: ${widths} × ${depths} m; ${floorRange}`;
}

/** The place endpoint rejects a recipe prepared against an older zone revision.
 * Only that conflict is safe to recover by reloading the zone and placing again;
 * other 409s (catalogue drift, missing AI revision) stay hard failures. */
function isZoneSourceRevisionConflict(error: unknown): boolean {
  const status = (error as { response?: { status?: number } } | undefined)?.response?.status;
  if (status !== 409) return false;
  return /changed while its LEGO recipe was being prepared/i.test(getApiErrorMessage(error, ''));
}

export function LegoAssemblyPreview({
  widthM,
  depthM,
  floors,
  properties,
  zone,
  buildingId = null,
  onClose,
}: {
  widthM?: number;
  depthM?: number;
  floors?: number;
  properties?: SiteZoneProperties;
  /** Preferred entry point — properties are derived from zone.properties. */
  zone?: SiteZone;
  /** Generated building linked to the zone; enables saving/restoring recipes. */
  buildingId?: string | null;
  onClose: () => void;
}) {
  const zoneProperties = zone?.properties ?? properties;
  const archetypeContext = useMemo(() => legoArchetypeContextFromZone(zoneProperties), [zoneProperties]);
  const catalogFingerprint = typeof zoneProperties?._lego_catalog_fingerprint === 'string'
    && zoneProperties._lego_catalog_fingerprint
    ? zoneProperties._lego_catalog_fingerprint
    : null;

  const catalogOption = useMemo(
    () => findZoneCatalogOption(archetypeContext.archetype_id, zoneProperties),
    [archetypeContext.archetype_id, zoneProperties],
  );

  const archetypeLabel = catalogOption?.label
    || (zoneProperties?.development_archetype_label as string | undefined)
    || normalizeArchetypeId(archetypeContext.archetype_id)
    || 'No archetype selected';

  // Catalogue-derived defaults, computed once on open; explicit props win.
  const [defaultTargets] = useState(() => {
    const defaults = deriveZoneTargets(catalogOption, zoneProperties);
    const frame = isDetachedArchetype(archetypeContext.archetype_id) && zone?.coordinates
      ? computeFootprintFrame(zone.coordinates) : null;
    return frame ? { ...defaults, width_m: frame.longDim, depth_m: frame.shortDim } : defaults;
  });
  const [targetWidth, setTargetWidth] = useState(() =>
    clamp(widthM ?? defaultTargets.width_m, MIN_DIMENSION_M, MAX_DIMENSION_M));
  const [targetDepth, setTargetDepth] = useState(() =>
    clamp(depthM ?? defaultTargets.depth_m, MIN_DIMENSION_M, MAX_DIMENSION_M));
  const [targetFloors, setTargetFloors] = useState(() =>
    clamp(floors ?? defaultTargets.floors, MIN_FLOORS, MAX_FLOORS));
  const [allowSetback, setAllowSetback] = useState(() => archetypeContext.allow_setback ?? false);

  const [plan, setPlan] = useState<LegoAssemblyPlan | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [planningFailure, setPlanningFailure] = useState<LegoPlanningFailure | null>(null);
  const [savedRecipe, setSavedRecipe] = useState<LegoAssemblyRecipe | null>(null);
  const [saving, setSaving] = useState(false);
  const [placing, setPlacing] = useState(false);
  // Building the recipe landed on via Place — the zone prop is a snapshot, so
  // a building created by Place is only known through the endpoint's response.
  const [placedBuildingId, setPlacedBuildingId] = useState<string | null>(null);
  const [clearing, setClearing] = useState(false);
  const queryClient = useQueryClient();

  // Restore any saved recipe for this building when the composer opens.
  useEffect(() => {
    if (!buildingId) return;
    let cancelled = false;
    legoAssemblyApi
      .getRecipe(buildingId)
      .then((recipe) => {
        if (!cancelled) setSavedRecipe(recipe);
      })
      .catch(() => {
        // No saved recipe (or backend unavailable) — the composer still works.
      });
    return () => {
      cancelled = true;
    };
  }, [buildingId]);

  const assemble = async (targets?: { width_m: number; depth_m: number; floors: number }) => {
    const width = clamp(targets?.width_m ?? targetWidth, MIN_DIMENSION_M, MAX_DIMENSION_M);
    const depth = clamp(targets?.depth_m ?? targetDepth, MIN_DIMENSION_M, MAX_DIMENSION_M);
    const floorCount = clamp(Math.round(targets?.floors ?? targetFloors), MIN_FLOORS, MAX_FLOORS);
    setTargetWidth(width);
    setTargetDepth(depth);
    setTargetFloors(floorCount);
    setLoading(true);
    setError(null);
    setPlanningFailure(null);
    try {
      const result = await legoAssemblyApi.plan({
        target_width_m: width,
        target_depth_m: depth,
        target_floors: floorCount,
        footprint_local_m: assemblyFootprintCoordinates(zone?.coordinates, { width_m: width, depth_m: depth }),
        ...(zone?.project_id ? { project_id: zone.project_id } : {}),
        ...archetypeContext,
        allow_setback: allowSetback,
        // A reviewed family either fits its declared contract or this preview
        // reports the normal correct-size fallback. Do not silently distort a
        // fixed family in the manual authoring path.
        allow_forced_fit: false,
      });
      setPlan(result);
    } catch (cause) {
      const failure = getLegoPlanningFailure(cause);
      setPlanningFailure(failure);
      setError(failure ? null : getApiErrorMessage(cause, 'Could not assemble this building.'));
    } finally {
      setLoading(false);
    }
  };

  const loadSavedRecipe = () => {
    if (!savedRecipe) return;
    void assemble({
      width_m: savedRecipe.target.width_m,
      depth_m: savedRecipe.target.depth_m,
      floors: savedRecipe.target.floors,
    });
  };

  const handleSaveRecipe = async () => {
    if (!plan || !buildingId) return;
    setSaving(true);
    setError(null);
    try {
      const saved = await legoAssemblyApi.saveRecipe(buildingId, {
        schema_version: 1,
        module_family: plan.family,
        ...(plan.catalog_fingerprint ?? catalogFingerprint
          ? { catalog_fingerprint: plan.catalog_fingerprint ?? catalogFingerprint }
          : {}),
        archetype_id: plan.archetype_id ?? archetypeContext.archetype_id ?? null,
        reuse_keys: plan.reuse_keys,
        target: plan.target,
        instances: plan.instances,
        assembled_height_m: plan.assembled_height_m,
        fit: plan.fit,
        assembled_preview_url: null,
      });
      setSavedRecipe(saved);
    } catch (cause) {
      setError(getApiErrorMessage(cause, 'Could not save the assembly recipe.'));
    } finally {
      setSaving(false);
    }
  };

  const recipeFromCurrentPlan = (): LegoAssemblyRecipe | null => {
    if (!plan) return null;
    const currentCatalogFingerprint = plan.catalog_fingerprint ?? catalogFingerprint;
    return {
      schema_version: 1,
      module_family: plan.family,
      ...(currentCatalogFingerprint ? { catalog_fingerprint: currentCatalogFingerprint } : {}),
      archetype_id: plan.archetype_id ?? archetypeContext.archetype_id ?? null,
      reuse_keys: plan.reuse_keys,
      target: plan.target,
      instances: plan.instances,
      assembled_height_m: plan.assembled_height_m,
      fit: plan.fit,
      assembled_preview_url: null,
    };
  };

  // Place = save the recipe zone-addressed; the backend creates/links the
  // building when the zone has none, then the globe swaps polygon -> stack.
  const handlePlace = async () => {
    const recipe = recipeFromCurrentPlan();
    if (!recipe || !zone) return;
    setPlacing(true);
    setError(null);
    try {
      const payload = {
        ...recipe,
        building_name: archetypeLabel,
        source_updated_at: zone.updated_at,
      };
      let result: Awaited<ReturnType<typeof legoAssemblyApi.place>>;
      try {
        result = await legoAssemblyApi.place(zone.id, payload);
      } catch (cause) {
        if (!isZoneSourceRevisionConflict(cause)) throw cause;
        // This panel keeps the zone it was opened with, so editing width, depth
        // or floors leaves `zone.updated_at` behind the server's revision and
        // every later Place would keep failing on the same stale timestamp.
        // Reload the zone once and place against its current revision.
        const refreshed = (await siteZonesApi.list(zone.project_id))
          .find((candidate) => candidate.id === zone.id);
        if (!refreshed) throw cause;
        result = await legoAssemblyApi.place(zone.id, {
          ...payload,
          source_updated_at: refreshed.updated_at,
        });
      }
      setSavedRecipe(recipe);
      setPlacedBuildingId(result.building_id);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['project', zone.project_id] }),
        queryClient.invalidateQueries({ queryKey: ['site-zones', zone.project_id] }),
      ]);
    } catch (cause) {
      setError(getApiErrorMessage(cause, 'Could not place the assembly on the map.'));
    } finally {
      setPlacing(false);
    }
  };

  const handleClearRecipe = async () => {
    const clearTarget = buildingId ?? placedBuildingId;
    if (!clearTarget || !savedRecipe) return;
    setClearing(true);
    setError(null);
    try {
      await legoAssemblyApi.clearRecipe(clearTarget);
      setSavedRecipe(null);
      setPlacedBuildingId(null);
      if (zone) {
        await Promise.all([
          queryClient.invalidateQueries({ queryKey: ['project', zone.project_id] }),
          queryClient.invalidateQueries({ queryKey: ['site-zones', zone.project_id] }),
        ]);
      }
    } catch (cause) {
      setError(getApiErrorMessage(cause, 'Could not clear the saved recipe.'));
    } finally {
      setClearing(false);
    }
  };

  const scaleWarning = fitIsStretched(plan?.fit);

  const stepperButtonClass = 'flex h-7 w-7 items-center justify-center rounded border-2 border-[#151515] bg-white shadow-[2px_2px_0_0_rgba(21,21,21,0.25)] transition hover:bg-[#fff9ec] disabled:opacity-40';
  const numberFieldClass = 'mt-0.5 w-full rounded border-2 border-[#151515] bg-white px-2 py-1 text-xs font-bold text-[#151515] focus:bg-[#fff9ec] focus:outline-none';

  return createPortal(
    <div className="fixed inset-0 z-[110] flex items-center justify-center bg-black/75 p-4" onClick={onClose}>
      <div
        className="relative flex h-[84vh] w-[94vw] max-w-6xl overflow-hidden rounded-xl border-2 border-[#151515] bg-[#f7f7f1] shadow-[8px_8px_0_0_rgba(0,0,0,0.45)]"
        onClick={(event) => event.stopPropagation()}
      >
        <aside className="w-72 shrink-0 overflow-y-auto border-r-2 border-[#151515] bg-white p-4">
          <div className="mb-3 flex items-center gap-2">
            <Box className="h-5 w-5" />
            <h2 className="text-sm font-black uppercase">LEGO Assembly</h2>
          </div>

          {savedRecipe && (
            <div className="mb-3 rounded border-2 border-emerald-600 bg-emerald-50 p-2">
              <div className="flex items-center gap-1.5 text-[11px] font-black uppercase text-emerald-700">
                <Bookmark className="h-3.5 w-3.5" />
                Saved recipe
              </div>
              <p className="mt-1 text-[11px] text-emerald-900">
                {savedRecipe.target.floors} floors · <span className="break-all font-semibold">{savedRecipe.module_family}</span>
              </p>
              <button
                type="button"
                onClick={loadSavedRecipe}
                disabled={loading}
                className="mt-1.5 w-full rounded border-2 border-emerald-700 bg-white px-2 py-1 text-[11px] font-black uppercase text-emerald-700 transition hover:bg-emerald-100 disabled:opacity-50"
              >
                Load
              </button>
            </div>
          )}

          <dl className="space-y-2 text-xs">
            <div className="flex items-baseline justify-between gap-2">
              <dt className="shrink-0">Archetype</dt>
              <dd className="truncate text-right font-bold" title={archetypeLabel}>{archetypeLabel}</dd>
            </div>
          </dl>

          <div className="mt-3 grid grid-cols-2 gap-2">
            <label className="block text-xs">
              Width (m)
              <input
                type="number"
                min={MIN_DIMENSION_M}
                max={MAX_DIMENSION_M}
                step={0.5}
                value={targetWidth}
                onChange={(event) => {
                  const value = event.target.valueAsNumber;
                  if (!Number.isNaN(value)) setTargetWidth(value);
                }}
                onBlur={() => setTargetWidth((value) => clamp(value, MIN_DIMENSION_M, MAX_DIMENSION_M))}
                className={numberFieldClass}
              />
            </label>
            <label className="block text-xs">
              Depth (m)
              <input
                type="number"
                min={MIN_DIMENSION_M}
                max={MAX_DIMENSION_M}
                step={0.5}
                value={targetDepth}
                onChange={(event) => {
                  const value = event.target.valueAsNumber;
                  if (!Number.isNaN(value)) setTargetDepth(value);
                }}
                onBlur={() => setTargetDepth((value) => clamp(value, MIN_DIMENSION_M, MAX_DIMENSION_M))}
                className={numberFieldClass}
              />
            </label>
          </div>

          <div className="mt-2 flex items-center justify-between text-xs">
            <span>Floors</span>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setTargetFloors((value) => clamp(value - 1, MIN_FLOORS, MAX_FLOORS))}
                disabled={targetFloors <= MIN_FLOORS}
                className={stepperButtonClass}
                aria-label="Fewer floors"
              >
                <Minus className="h-3.5 w-3.5" />
              </button>
              <span className="w-8 text-center text-sm font-black">{targetFloors}</span>
              <button
                type="button"
                onClick={() => setTargetFloors((value) => clamp(value + 1, MIN_FLOORS, MAX_FLOORS))}
                disabled={targetFloors >= MAX_FLOORS}
                className={stepperButtonClass}
                aria-label="More floors"
              >
                <Plus className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>

          <label className="mt-2 flex items-center justify-between text-xs">
            <span>Allow setback modules</span>
            <input
              type="checkbox"
              checked={allowSetback}
              onChange={(event) => setAllowSetback(event.target.checked)}
              className="h-4 w-4 accent-[#151515]"
            />
          </label>

          {plan && (
            <dl className="mt-3 space-y-2 border-t-2 border-[#151515]/15 pt-3 text-xs">
              <div className="flex justify-between"><dt>Family</dt><dd className="max-w-32 truncate font-bold" title={plan.family}>{plan.family}</dd></div>
              <div className="flex justify-between"><dt>Fit score</dt><dd className="font-bold">{plan.fit.score.toFixed(2)}</dd></div>
              <div className="flex justify-between"><dt>Height</dt><dd className="font-bold">{plan.assembled_height_m.toFixed(1)} m</dd></div>
              <div className="flex justify-between"><dt>Modules</dt><dd className="font-bold">{plan.instances.length}</dd></div>
              {plan.fit.placement_mode === 'detached_lots' && <div className="flex justify-between"><dt>Separate homes</dt><dd className="font-bold">{plan.fit.dwelling_count}</dd></div>}
            </dl>
          )}

          {scaleWarning && plan && (
            <div className="mt-2 flex items-start gap-1.5 rounded border border-amber-400 bg-amber-50 p-2 text-[11px] text-amber-800">
              <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
              <span>
                Modules are stretched to fit ({(plan.fit.scale_x * 100).toFixed(0)}% × {(plan.fit.scale_y * 100).toFixed(0)}%).
                Adjust width/depth toward the family's native size for cleaner joints.
              </span>
            </div>
          )}

          {plan?.fit.footprint_mode === 'archetype_contain' && (
            <div className="mt-2 rounded border border-emerald-300 bg-emerald-50 p-2 text-[11px] font-semibold text-emerald-800">
              Archetype form preserved: the building is uniformly scaled and contained inside the drawn site envelope.
            </div>
          )}
          {plan?.fit.placement_mode === 'detached_lots' && <p className="mt-2 rounded border border-emerald-300 bg-emerald-50 p-2 text-xs text-emerald-900">
            {plan.fit.dwelling_count} separate homes fit within your drawn plot. Gaps between homes are a starting point for your design; check local requirements in your planning report.
          </p>}

          <button
            type="button"
            onClick={() => assemble()}
            disabled={loading}
            className="mt-4 flex w-full items-center justify-center gap-2 rounded border-2 border-[#151515] bg-[#c9ff3d] px-3 py-2 text-xs font-black uppercase shadow-[3px_3px_0_0_#151515] disabled:opacity-50"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
            {plan ? 'Reassemble' : 'Auto assemble'}
          </button>

          <button
            type="button"
            onClick={handlePlace}
            disabled={!plan || !zone || placing}
            title={!zone
              ? 'Open the composer from a zone to place its assembly on the map.'
              : !plan
                ? 'Assemble the building first.'
                : 'Save the recipe on this zone (a building is created if needed) and show the stack on the globe.'}
            className="mt-2 flex w-full items-center justify-center gap-2 rounded border-2 border-[#151515] bg-[#28c7e8] px-3 py-2 text-xs font-black uppercase shadow-[3px_3px_0_0_#151515] disabled:opacity-50"
          >
            {placing ? <Loader2 className="h-4 w-4 animate-spin" /> : placedBuildingId ? <Check className="h-4 w-4" /> : <MapPin className="h-4 w-4" />}
            {placedBuildingId ? 'Placed — place again' : 'Place on map'}
          </button>

          <button
            type="button"
            onClick={handleSaveRecipe}
            disabled={!plan || !buildingId || saving}
            title={!buildingId
              ? 'This zone has no generated building yet — Place on map creates one, or generate buildings first.'
              : !plan
                ? 'Assemble the building first.'
                : 'Save this assembly so it can be restored later.'}
            className="mt-2 flex w-full items-center justify-center gap-2 rounded border-2 border-[#151515] bg-white px-3 py-2 text-xs font-black uppercase shadow-[3px_3px_0_0_#151515] disabled:opacity-50"
          >
            {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
            Save assembly recipe
          </button>

          {savedRecipe && (buildingId || placedBuildingId) && (
            <button
              type="button"
              onClick={handleClearRecipe}
              disabled={clearing}
              className="mt-2 flex w-full items-center justify-center gap-2 rounded border-2 border-[#151515] bg-white px-3 py-2 text-xs font-black uppercase text-[#d92618] shadow-[3px_3px_0_0_#151515] disabled:opacity-50"
            >
              {clearing ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
              Clear saved recipe
            </button>
          )}

          <button
            type="button"
            onClick={onClose}
            className="mt-2 flex w-full items-center justify-center gap-2 rounded border-2 border-[#151515] bg-white px-3 py-2 text-xs font-black uppercase shadow-[3px_3px_0_0_#151515]"
          >
            <X className="h-4 w-4" />
            Close
          </button>

          {error && <p className="mt-3 rounded border border-red-300 bg-red-50 p-2 text-xs text-red-800">{error}</p>}

          {planningFailure?.code === 'family_not_found' && (
            <div className="mt-2 rounded border border-amber-300 bg-amber-50 p-2 text-[11px] text-amber-950">
              <p className="font-bold">Detailed Sticker/LEGO family to add</p>
              <p className="mt-1">
                This does not block the plan. Generate to 3D uses correctly sized {targetWidth} × {targetDepth} m,
                {` ${targetFloors}-floor`} massing now. After the reviewed family is imported, Rebuild buildings
                upgrades it in place.
              </p>
            </div>
          )}

          {planningFailure?.code === 'family_incompatible' && (
            <div className="mt-2 rounded border border-amber-400 bg-amber-50 p-2 text-[11px] text-amber-900">
              <p className="font-bold">This detailed family is outside its reviewed fit.</p>
              <p className="mt-1">
                This does not block the plan. Generate to 3D uses correctly sized {targetWidth} × {targetDepth} m,
                {` ${targetFloors}-floor`} massing now. Change the dimensions only if you want to use this reviewed
                detailed family.
              </p>
              {planningFailure.supported_families && planningFailure.supported_families.length > 0 && (
                <div className="mt-1.5">
                  <p className="font-bold">Optional detailed-family sizes</p>
                  <ul className="mt-0.5 list-disc space-y-0.5 pl-4">
                    {planningFailure.supported_families.map((supported) => (
                      <li key={supported.family}>{supportedFamilyLabel(supported)}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          <p className="mt-4 text-[11px] leading-relaxed text-black/55">
            Uses the selected Urban Intelligence archetype ID and reuse keys to choose a compatible podium, repeating floor, setback and roof family.
          </p>
        </aside>

        <main className="relative min-w-0 flex-1 bg-[#1b1b1b]">
          <button
            type="button"
            onClick={onClose}
            className="absolute right-3 top-3 z-10 rounded bg-black/60 p-2 text-white hover:bg-black"
            aria-label="Close LEGO assembly preview"
          >
            <X className="h-4 w-4" />
          </button>

          {plan ? (
            <Canvas shadows camera={{ position: [12, 10, 16], fov: 42 }} dpr={[1, 2]}>
              <PreviewErrorBoundary>
                <Suspense fallback={<Progress />}>
                  <AssemblyScene plan={plan} />
                </Suspense>
              </PreviewErrorBoundary>
            </Canvas>
          ) : (
            <div className="flex h-full items-center justify-center text-center text-white/55">
              <div>
                <Box className="mx-auto mb-3 h-10 w-10" />
                <p className="text-sm font-bold">Choose Auto Assemble to preview the archetype as reusable modules.</p>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>,
    document.body,
  );
}
