import { Suspense, useCallback, useEffect, useMemo, useRef, useState, type ChangeEvent } from 'react';
import { createPortal } from 'react-dom';
import { useQueryClient } from '@tanstack/react-query';
import { Canvas } from '@react-three/fiber';
import { Bounds, Environment, Grid, OrbitControls } from '@react-three/drei';
import { AlertTriangle, Blocks, Check, Copy, Loader2, MapPin, RefreshCw, Route, Save, Trees, Upload, X } from 'lucide-react';
import { getApiErrorMessage } from '@/services/api';
import type { SiteZone } from '@/types';
import { resolveCommunity3DKind } from '@/features/community3d/community3d';
import { allSettledWithConcurrency } from './allSettledWithConcurrency';
import {
  legoArchetypeContextFromZone,
  legoAssemblyApi,
  getLegoPlanningFailure,
  type LegoAssemblyPlan,
} from './legoAssemblyApi';
import {
  ModuleInstance,
  PreviewErrorBoundary,
  Progress,
  familyGenerationCommands,
  fitIsStretched,
  fitPreservesArchetypeForm,
} from './legoShared';
import {
  deriveGroundItems,
  deriveItems,
  recipeFromPlan,
  type GroundBuildItem,
  type ZoneBuildItem,
} from './communityCompiler';
import {
  getStreetNetworkGroundMeta,
  importStreetNetworkGroundTexture,
} from '@/components/viewer/globe/streetNetworkGroundTexture';
import {
  generatePublicRealmDrapes,
  planPublicRealmDrapes,
} from '@/components/viewer/globe/publicRealmDrapeGenerator';

function BuilderScene({ items }: { items: ZoneBuildItem[] }) {
  const placed = items.filter(
    (item): item is ZoneBuildItem & { plan: LegoAssemblyPlan; offset: [number, number] } =>
      Boolean(item.plan && item.offset),
  );
  return (
    <>
      <ambientLight intensity={0.8} />
      <directionalLight castShadow position={[8, 12, 7]} intensity={1.5} />
      <directionalLight position={[-8, 5, -6]} intensity={0.35} />
      <Environment preset="city" background={false} />
      {/* Neutral ground plane under the whole plan. */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.05, 0]}>
        <planeGeometry args={[4000, 4000]} />
        <meshStandardMaterial color="#262626" />
      </mesh>
      <Grid args={[600, 600]} cellSize={5} sectionSize={25} fadeDistance={500} />
      <Bounds fit clip observe margin={1.2}>
        <group>
          {placed.map((item) => (
            // Each assembly is stacked at the zone centroid without per-building
            // rotation — orienting modules to the parcel is a known v1 limitation.
            <group key={item.zone.id} position={[item.offset[0], 0, item.offset[1]]}>
              {item.plan.instances.map((instance, index) => (
                <ModuleInstance
                  key={`${item.zone.id}-${instance.asset_id}-${instance.level}-${index}`}
                  instance={instance}
                />
              ))}
            </group>
          ))}
        </group>
      </Bounds>
      <OrbitControls makeDefault enablePan />
    </>
  );
}

export function LegoBuilderPanel({
  zones,
  onClose,
  autoGenerate = false,
  sceneContextImageBase64 = null,
  onZonesRefreshed,
}: {
  zones: SiteZone[];
  onClose: () => void;
  /** Top-level workflow entry: plan, then compile the complete scene once. */
  autoGenerate?: boolean;
  /** Frozen Google Tiles frame used only as local material/edge context. */
  sceneContextImageBase64?: string | null;
  /** Keep the owning workflow snapshot current after drape metadata writes. */
  onZonesRefreshed?: (zones: SiteZone[]) => void;
}) {
  const [items, setItems] = useState<ZoneBuildItem[]>(() => deriveItems(zones));
  const [groundItems, setGroundItems] = useState<GroundBuildItem[]>(() => deriveGroundItems(zones));
  const [planning, setPlanning] = useState(false);
  const [saving, setSaving] = useState(false);
  const [placingAll, setPlacingAll] = useState(false);
  const [generationStage, setGenerationStage] = useState<string | null>(null);
  const [initialPlanningComplete, setInitialPlanningComplete] = useState(false);
  const [saveResult, setSaveResult] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const queryClient = useQueryClient();
  const autoGenerateStartedRef = useRef(false);
  const streetAtlasInputRef = useRef<HTMLInputElement | null>(null);
  const [streetAtlasStatus, setStreetAtlasStatus] = useState<{
    kind: 'success' | 'error';
    message: string;
  } | null>(null);
  const [importingStreetAtlas, setImportingStreetAtlas] = useState(false);
  const projectId = zones[0]?.project_id;
  const currentDrapeZones = useMemo(() => {
    const currentById = new Map([
      ...items.map((item) => [item.zone.id, item.zone] as const),
      ...groundItems.map((item) => [item.zone.id, item.zone] as const),
    ]);
    return zones.map((zone) => currentById.get(zone.id) ?? zone);
  }, [groundItems, items, zones]);
  const streetZones = currentDrapeZones.filter((zone) => resolveCommunity3DKind(zone) === 'street');
  const streetsWithAtlas = streetZones.filter((zone) => getStreetNetworkGroundMeta(zone)).length;
  const publicRealmDrapePlan = useMemo(
    () => planPublicRealmDrapes(currentDrapeZones),
    [currentDrapeZones],
  );

  // The globe reads buildings from the project query and links from the zone
  // query — both must refetch for the placed stack to appear.
  const refetchPlacedData = useCallback(async () => {
    if (!projectId) return;
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['project', projectId] }),
      queryClient.invalidateQueries({ queryKey: ['site-zones', projectId] }),
    ]);
  }, [queryClient, projectId]);

  const setPlaceState = useCallback((zoneId: string, placeState: ZoneBuildItem['placeState']) => {
    setItems((prev) => prev.map((item) => (item.zone.id === zoneId ? { ...item, placeState } : item)));
  }, []);

  const handlePlaceOne = useCallback(async (target: ZoneBuildItem) => {
    if (!target.plan || target.placeState === 'placing') return;
    setPlaceState(target.zone.id, 'placing');
    try {
      await legoAssemblyApi.place(target.zone.id, recipeFromPlan(target as ZoneBuildItem & { plan: LegoAssemblyPlan }));
      setPlaceState(target.zone.id, 'placed');
      await refetchPlacedData();
    } catch (error) {
      setPlaceState(target.zone.id, 'failed');
      setSaveResult(getApiErrorMessage(error, 'Could not place this zone.'));
    }
  }, [refetchPlacedData, setPlaceState]);

  const handlePlaceAll = useCallback(async (forceRebuild = false) => {
    const placeable = items.filter(
      (item): item is ZoneBuildItem & { plan: LegoAssemblyPlan } => (
        Boolean(item.plan) && (forceRebuild || item.placeState !== 'placed')
      ),
    );
    const massingOnly = items.filter((item) => (
      !item.plan && Boolean(item.offset) && (forceRebuild || item.massingState !== 'compiled')
    ));
    const groundNeedingDrapeIds = new Set([
      ...publicRealmDrapePlan.parksNeedingDrape.map((zone) => zone.id),
      ...(publicRealmDrapePlan.streetNetworkNeedsDrape
        ? publicRealmDrapePlan.streetZones.map((zone) => zone.id)
        : []),
    ]);
    const groundToCompile = groundItems.filter((item) => (
      forceRebuild || item.state !== 'compiled' || groundNeedingDrapeIds.has(item.zone.id)
    ));
    if (
      (placeable.length === 0 && massingOnly.length === 0 && groundToCompile.length === 0)
      || placingAll
    ) return;
    const placeableIds = new Set(placeable.map((item) => item.zone.id));
    const massingOnlyIds = new Set(massingOnly.map((item) => item.zone.id));
    const groundToCompileIds = new Set(groundToCompile.map((item) => item.zone.id));
    setPlacingAll(true);
    setSaveResult(null);
    setItems((prev) => prev.map((item) => {
      if (placeableIds.has(item.zone.id)) {
        return { ...item, placeState: 'placing' };
      }
      if (massingOnlyIds.has(item.zone.id)) {
        return { ...item, massingState: 'compiling' };
      }
      return item;
    }));
    setGroundItems((prev) => prev.map((item) => (
      item.state === 'compiled' ? item : { ...item, state: 'compiling' }
    )));
    try {
      const latestPanelZoneById = new Map([
        ...items.map((item) => [item.zone.id, item.zone] as const),
        ...groundItems.map((item) => [item.zone.id, item.zone] as const),
      ]);
      const sourceZones = zones.map((zone) => latestPanelZoneById.get(zone.id) ?? zone);
      let compileZones = sourceZones;
      if (groundToCompile.length > 0) {
        const drapeResult = await generatePublicRealmDrapes(projectId!, sourceZones, {
          sceneContextImageBase64,
          onProgress: ({ completed, total, label }) => {
            setGenerationStage(
              total > 0 ? `${label} · ${completed}/${total} image calls` : label,
            );
          },
        });
        compileZones = drapeResult.zones;
        onZonesRefreshed?.(compileZones);
        if (drapeResult.remainingParks > 0) {
          throw new Error(
            `Generated ${drapeResult.generatedParks} park drapes in this protected batch. `
            + `${drapeResult.remainingParks} parks remain; run Generate to 3D again to finish them without regenerating completed drapes.`,
          );
        }
      }
      setGenerationStage('Placing 3D buildings and public-realm objects');
      const authoritativeById = new Map(compileZones.map((zone) => [zone.id, zone]));
      const authoritativeZone = (zoneId: string): SiteZone => {
        const zone = authoritativeById.get(zoneId);
        if (!zone) throw new Error('A plan zone changed while Generate to 3D was preparing. Refresh and retry.');
        return zone;
      };
      const result = await legoAssemblyApi.compileCommunity([
        ...placeable.map((item) => ({
          zone_id: item.zone.id,
          source_updated_at: authoritativeZone(item.zone.id).updated_at,
          recipe: recipeFromPlan(item),
        })),
        ...massingOnly.map((item) => ({
          zone_id: item.zone.id,
          source_updated_at: authoritativeZone(item.zone.id).updated_at,
        })),
        ...groundToCompile.map((item) => ({
          zone_id: item.zone.id,
          source_updated_at: authoritativeZone(item.zone.id).updated_at,
        })),
      ]);
      setItems((prev) => prev.map((item) => {
        if (placeableIds.has(item.zone.id)) {
          return { ...item, zone: authoritativeZone(item.zone.id), placeState: 'placed' };
        }
        if (massingOnlyIds.has(item.zone.id)) {
          return { ...item, zone: authoritativeZone(item.zone.id), massingState: 'compiled' };
        }
        return item;
      }));
      setGroundItems((prev) => prev.map((item) => (
        groundToCompileIds.has(item.zone.id)
          ? { ...item, zone: authoritativeZone(item.zone.id), state: 'compiled' }
          : item
      )));
      const groundCount = result.counts.park + result.counts.street;
      const residual = result.residual_landscape;
      const residualSummary = residual && residual.boundary_count > 0
        ? `; landscaped ${Math.round(residual.area_sqm).toLocaleString()} m² of residual site`
          + ` with ${residual.placement_count} tree${residual.placement_count === 1 ? '' : 's'}`
        : '';
      setSaveResult(
        `Built ${placeable.length} detailed building${placeable.length === 1 ? '' : 's'}, `
        + `${massingOnly.length} family-pending mass${massingOnly.length === 1 ? '' : 'es'}, and `
        + `${groundCount} park/street layer${groundCount === 1 ? '' : 's'}`
        + residualSummary,
      );
      await refetchPlacedData();
    } catch (error) {
      setItems((prev) => prev.map((item) => {
        if (placeableIds.has(item.zone.id)) {
          return { ...item, placeState: 'failed' };
        }
        if (massingOnlyIds.has(item.zone.id)) {
          return { ...item, massingState: 'failed' };
        }
        return item;
      }));
      setGroundItems((prev) => prev.map((item) => (
        groundToCompileIds.has(item.zone.id)
          ? { ...item, state: 'failed' }
          : item
      )));
      setSaveResult(getApiErrorMessage(error, 'Could not build this community. No changes were saved.'));
      await refetchPlacedData();
    } finally {
      setGenerationStage(null);
      setPlacingAll(false);
    }
  }, [groundItems, items, onZonesRefreshed, placingAll, projectId, publicRealmDrapePlan, refetchPlacedData, sceneContextImageBase64, zones]);

  const runBatch = useCallback(async (replacePlaced = false) => {
    const base = deriveItems(zones);
    setItems(base);
    setGroundItems(deriveGroundItems(zones));
    setSaveResult(null);
    setInitialPlanningComplete(false);
    if (base.length === 0) {
      setInitialPlanningComplete(true);
      return;
    }
    setPlanning(true);
    const results = await allSettledWithConcurrency(
      base,
      (item) => legoAssemblyApi.plan({
          target_width_m: item.targets.width_m,
          target_depth_m: item.targets.depth_m,
          target_floors: item.targets.floors,
          footprint_profile: item.targets.footprint_profile,
          wing_depth_m: item.targets.wing_depth_m,
          project_id: item.zone.project_id,
          ...legoArchetypeContextFromZone(item.zone.properties),
        }),
      8,
    );
    const plannedItems = base.map((item, index) => {
      const result = results[index];
      if (result.status === 'fulfilled') return { ...item, plan: result.value };
      const planningFailure = getLegoPlanningFailure(result.reason);
      return {
        ...item,
        error: planningFailure?.message || getApiErrorMessage(result.reason, 'Could not assemble this zone.'),
        familyMissing: planningFailure?.code === 'family_not_found',
      };
    });
    setItems(plannedItems);

    // "Rebuild" must update recipes that are already on the globe. Merely
    // recalculating the preview leaves their old content-hashed module URLs in
    // Building.specifications, so a freshly imported family can never replace
    // the cached live asset. The initial panel load still plans read-only.
    if (replacePlaced) {
      const replaceable = plannedItems.filter(
        (item): item is ZoneBuildItem & { plan: LegoAssemblyPlan } => (
          Boolean(item.plan) && item.placeState === 'placed'
        ),
      );
      if (replaceable.length > 0) {
        const replaced = await allSettledWithConcurrency(
          replaceable,
          (item) => legoAssemblyApi.place(item.zone.id, recipeFromPlan(item)),
          8,
        );
        const failedIds = new Set(
          replaceable
            .filter((_item, index) => replaced[index].status === 'rejected')
            .map((item) => item.zone.id),
        );
        const replacedCount = replaced.filter((result) => result.status === 'fulfilled').length;
        setSaveResult(
          failedIds.size > 0
            ? `Rebuilt ${replacedCount} of ${replaceable.length} placed building${replaceable.length === 1 ? '' : 's'}`
            : `Rebuilt ${replacedCount} placed building${replacedCount === 1 ? '' : 's'} with the latest family assets`,
        );
        await refetchPlacedData();
        // Placing the refreshed recipe intentionally marks its owning source
        // zone stale, which advances zone.updated_at. Carry that authoritative
        // revision into the next atomic Community 3D request; otherwise the
        // immediately-following "Rebuild current 3D scene" deterministically
        // fails optimistic concurrency with the pre-place timestamp.
        const refreshedZones = queryClient.getQueryData<SiteZone[]>(['site-zones', projectId]);
        const refreshedById = new Map((refreshedZones ?? []).map((zone) => [zone.id, zone]));
        setItems(plannedItems.map((item) => ({
          ...item,
          zone: refreshedById.get(item.zone.id) ?? item.zone,
          ...(failedIds.has(item.zone.id) ? { placeState: 'failed' as const } : {}),
        })));
      }
    }
    setPlanning(false);
    setInitialPlanningComplete(true);
  }, [projectId, queryClient, refetchPlacedData, zones]);

  // Plan every buildable zone once when the panel opens; "Rebuild all" re-runs it.
  useEffect(() => {
    void runBatch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // The main City Prompt button is intentionally a single action. The panel
  // remains visible as progress/reporting UI while planning completes, then
  // atomically rebuilds buildings, public realm, and residual landscaping.
  useEffect(() => {
    if (!autoGenerate || !initialPlanningComplete || autoGenerateStartedRef.current) return;
    autoGenerateStartedRef.current = true;
    void handlePlaceAll(true);
  }, [autoGenerate, handlePlaceAll, initialPlanningComplete]);

  const assembledCount = items.filter((item) => item.plan).length;
  const noFamilyCount = items.filter((item) => item.familyMissing).length;
  const otherFailedCount = items.filter((item) => item.error && !item.familyMissing).length;
  const skippedCount = items.filter((item) => !item.offset).length;
  const placedCount = items.filter((item) => item.plan && item.offset).length;
  const parkCount = groundItems.filter((item) => item.kind === 'park').length;
  const streetCount = groundItems.filter((item) => item.kind === 'street').length;
  const compiledGroundCount = groundItems.filter((item) => item.state === 'compiled').length;
  const unplacedDetailedCount = items.filter((item) => item.plan && item.placeState !== 'placed').length;
  const uncompiledMassingCount = items.filter((item) => (
    !item.plan && item.offset && item.massingState !== 'compiled'
  )).length;
  const canBuildCommunity = (
    unplacedDetailedCount > 0
    || uncompiledMassingCount > 0
    || compiledGroundCount < groundItems.length
    || publicRealmDrapePlan.totalImageCalls > 0
  );
  const saveResultIsError = Boolean(
    items.some((item) => item.placeState === 'failed' || item.massingState === 'failed')
    || groundItems.some((item) => item.state === 'failed'),
  );

  const missingArchetypeIds = useMemo(
    () => [...new Set(items.filter((item) => item.familyMissing).map((item) => item.archetypeId ?? '<archetype-id>'))],
    [items],
  );
  const hintCommands = missingArchetypeIds.map((id) => familyGenerationCommands(id)).join('\n');

  const savable = items.filter(
    (item): item is ZoneBuildItem & { plan: LegoAssemblyPlan } =>
      Boolean(item.plan && item.zone.building_id),
  );

  const handleSaveAll = async () => {
    if (savable.length === 0 || saving) return;
    setSaving(true);
    setSaveResult(null);
    const results = await allSettledWithConcurrency(
      savable,
      (item) => {
        const buildingId = item.zone.building_id as string;
        const context = legoArchetypeContextFromZone(item.zone.properties);
        return legoAssemblyApi.saveRecipe(buildingId, {
          schema_version: 1,
          module_family: item.plan.family,
          archetype_id: item.plan.archetype_id ?? context.archetype_id ?? null,
          reuse_keys: item.plan.reuse_keys,
          target: item.plan.target,
          instances: item.plan.instances,
          assembled_height_m: item.plan.assembled_height_m,
          fit: item.plan.fit,
          assembled_preview_url: null,
        });
      },
      8,
    );
    const savedCount = results.filter((result) => result.status === 'fulfilled').length;
    setSaveResult(`Saved ${savedCount} of ${savable.length} recipe${savable.length === 1 ? '' : 's'}`);
    setSaving(false);
  };

  const copyHintCommands = async () => {
    try {
      await navigator.clipboard.writeText(hintCommands);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard unavailable (e.g. insecure context) — the commands stay selectable.
    }
  };

  const handleStreetAtlasImport = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.currentTarget.files?.[0];
    event.currentTarget.value = '';
    if (!file || !projectId || importingStreetAtlas) return;
    setImportingStreetAtlas(true);
    setStreetAtlasStatus(null);
    try {
      const meta = await importStreetNetworkGroundTexture(projectId, zones, file, {
        model: 'gpt-image-2',
        provider: 'openai',
      });
      await refetchPlacedData();
      setStreetAtlasStatus({
        kind: 'success',
        message: `Applied one connected atlas to ${meta.road_zone_ids.length} streets. No image call was made during import.`,
      });
    } catch (error) {
      setStreetAtlasStatus({
        kind: 'error',
        message: getApiErrorMessage(error, 'Could not import the connected street atlas.'),
      });
    } finally {
      setImportingStreetAtlas(false);
    }
  };

  return createPortal(
    <div className="fixed inset-0 z-[110] flex items-center justify-center bg-black/75 p-4" onClick={onClose}>
      <div
        className="relative flex h-[88vh] w-[96vw] max-w-7xl overflow-hidden rounded-xl border-2 border-[#151515] bg-[#f7f7f1] shadow-[8px_8px_0_0_rgba(0,0,0,0.45)]"
        onClick={(event) => event.stopPropagation()}
      >
        <aside className="flex w-80 shrink-0 flex-col border-r-2 border-[#151515] bg-white">
          <div className="border-b-2 border-[#151515]/15 p-4 pb-3">
            <div className="mb-2 flex items-center gap-2">
              <Blocks className="h-5 w-5" />
              <h2 className="text-sm font-black uppercase">Generate to 3D</h2>
            </div>
            <p className="text-xs font-bold">
              {`${items.length} buildings · ${parkCount} parks · ${streetCount} streets`}
            </p>
            <p className="mt-1 text-[11px] font-bold text-black/55">
              {`Assembled ${assembledCount} · No family ${noFamilyCount} · Skipped ${skippedCount}`}
              {otherFailedCount > 0 ? ` · Failed ${otherFailedCount}` : ''}
            </p>
            {planning && (
              <p className="mt-1 flex items-center gap-1.5 text-[11px] text-black/55">
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                Assembling {items.length} zone{items.length === 1 ? '' : 's'}…
              </p>
            )}
            {generationStage && (
              <p className="mt-1 flex items-center gap-1.5 text-[11px] font-bold text-sky-800">
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                {generationStage}
              </p>
            )}
            {!placingAll && publicRealmDrapePlan.totalImageCalls > 0 && (
              <p className="mt-1 text-[10px] font-bold text-black/55">
                {`${publicRealmDrapePlan.totalImageCalls} AI ground-drape image call${publicRealmDrapePlan.totalImageCalls === 1 ? '' : 's'} will run during Generate to 3D.`}
              </p>
            )}
          </div>

          <div className="min-h-0 flex-1 space-y-2 overflow-y-auto p-4 pt-3">
            {items.length === 0 && groundItems.length === 0 && (
              <p className="text-xs text-black/55">
                No buildings, parks, or streets in this plan yet.
              </p>
            )}

            {items.map((item) => (
              <div
                key={item.zone.id}
                className={`rounded border-2 p-2 text-[11px] ${
                  item.error && !item.familyMissing
                    ? 'border-red-300 bg-red-50'
                    : item.familyMissing
                      ? 'border-amber-300 bg-amber-50'
                      : 'border-[#151515]/15 bg-white'
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="truncate font-bold" title={item.label}>{item.label}</span>
                  {item.plan && fitIsStretched(item.plan.fit) && (
                    <span className="flex shrink-0 items-center gap-1 rounded bg-amber-100 px-1.5 py-0.5 text-[10px] font-bold text-amber-800">
                      <AlertTriangle className="h-3 w-3" />
                      stretched
                    </span>
                  )}
                  {item.plan && fitPreservesArchetypeForm(item.plan.fit) && (
                    <span className="shrink-0 rounded bg-emerald-100 px-1.5 py-0.5 text-[10px] font-bold text-emerald-800">
                      form preserved
                    </span>
                  )}
                  {!item.plan && item.massingState && (
                    <span className={`shrink-0 rounded px-1.5 py-0.5 text-[10px] font-bold ${
                      item.massingState === 'compiled'
                        ? 'bg-emerald-100 text-emerald-800'
                        : item.massingState === 'failed'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-sky-100 text-sky-800'
                    }`}>
                      {item.massingState === 'compiling'
                        ? 'massing...'
                        : item.massingState === 'compiled' ? '3D massing' : 'retry massing'}
                    </span>
                  )}
                </div>
                <p className="mt-0.5 text-black/55">
                  {`${item.targets.footprint_profile.replace('_', ' ')} · ${item.targets.width_m.toFixed(1)} × ${item.targets.depth_m.toFixed(1)} m · ${item.targets.floors} floors`}
                  {!item.targets.within_recommended_size ? ' · outside preferred range' : ''}
                </p>
                {item.plan && (
                  <div className="mt-0.5 flex items-center justify-between gap-2">
                    <p className="min-w-0 truncate text-black/60" title={item.plan.family}>
                      {item.plan.family} · fit {item.plan.fit.score.toFixed(2)}
                    </p>
                    {item.placeState === 'placed' ? (
                      <span className="flex shrink-0 items-center gap-1 rounded bg-emerald-100 px-1.5 py-0.5 text-[10px] font-bold text-emerald-800">
                        <Check className="h-3 w-3" />
                        placed
                      </span>
                    ) : (
                      <button
                        type="button"
                        onClick={() => void handlePlaceOne(item)}
                        disabled={item.placeState === 'placing' || placingAll}
                        title="Save this recipe on the zone's building (created if needed) and show the stack on the globe."
                        className="flex shrink-0 items-center gap-1 rounded border border-[#151515] bg-white px-1.5 py-0.5 text-[10px] font-black uppercase hover:bg-[#c9ff3d] disabled:opacity-50"
                      >
                        {item.placeState === 'placing'
                          ? <Loader2 className="h-3 w-3 animate-spin" />
                          : <MapPin className="h-3 w-3" />}
                        {item.placeState === 'failed' ? 'Retry place' : 'Place'}
                      </button>
                    )}
                  </div>
                )}
                {item.error && (
                  <p className={`mt-0.5 ${item.familyMissing ? 'text-amber-900' : 'text-red-800'}`}>
                    {item.familyMissing && <span className="font-black uppercase">No family · </span>}
                    {item.error}
                    {item.familyMissing && item.offset && (
                      <span className="font-bold"> Exact-footprint 3D massing will stand in until this family is imported.</span>
                    )}
                  </p>
                )}
                {!item.plan && !item.error && planning && (
                  <p className="mt-0.5 text-black/50">Assembling…</p>
                )}
                {!item.offset && (
                  <p className="mt-0.5 text-black/50">No polygon coordinates — listed only, not placed in the scene.</p>
                )}
              </div>
            ))}

            {groundItems.length > 0 && (
              <div className="pt-1">
                <p className="mb-2 text-[10px] font-black uppercase tracking-wide text-black/45">
                  Ground systems
                </p>
                <div className="space-y-2">
                  {groundItems.map((item) => (
                    <div
                      key={item.zone.id}
                      className={`rounded border-2 p-2 text-[11px] ${
                        item.state === 'failed' ? 'border-red-300 bg-red-50' : 'border-[#151515]/15 bg-white'
                      }`}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="flex min-w-0 items-center gap-1.5 font-bold">
                          {item.kind === 'park'
                            ? <Trees className="h-3.5 w-3.5 shrink-0 text-emerald-700" />
                            : <Route className="h-3.5 w-3.5 shrink-0 text-slate-700" />}
                          <span className="truncate" title={item.zone.name ?? item.kind}>
                            {item.zone.name ?? (item.kind === 'park' ? 'Park / plaza' : 'Street')}
                          </span>
                        </span>
                        <span className={`shrink-0 rounded px-1.5 py-0.5 text-[10px] font-bold ${
                          item.state === 'compiled'
                            ? 'bg-emerald-100 text-emerald-800'
                            : item.state === 'failed'
                              ? 'bg-red-100 text-red-800'
                              : 'bg-sky-100 text-sky-800'
                        }`}>
                          {item.state === 'compiling' ? 'building…' : item.state}
                        </span>
                      </div>
                      <p className="mt-0.5 text-black/55">
                        {item.kind === 'park'
                          ? 'AI-draped archetype ground, then programmed 3D trees, structures, planting and seating'
                          : 'One connected AI road atlas, then 3D curbs, markings, trees, lights, furniture and vehicles'}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {missingArchetypeIds.length > 0 && (
              <div className="rounded border border-amber-300 bg-amber-50 p-2 text-[11px] text-amber-950">
                <p className="font-bold">
                  {missingArchetypeIds.length === 1
                    ? 'One archetype has no module family yet.'
                    : `${missingArchetypeIds.length} archetypes have no module family yet.`}
                </p>
                <p className="mt-1">These zones build as neutral, authoritative-height massing now. Generate and import the families to upgrade them in place:</p>
                <pre className="mt-1.5 select-all overflow-x-auto whitespace-pre-wrap break-all rounded bg-amber-100 p-1.5 font-mono text-[10px] leading-relaxed">{hintCommands}</pre>
                <button
                  type="button"
                  onClick={copyHintCommands}
                  className="mt-1.5 flex items-center gap-1 rounded border border-amber-500 bg-white px-2 py-0.5 text-[10px] font-bold text-amber-900 hover:bg-amber-100"
                >
                  {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                  {copied ? 'Copied' : 'Copy commands'}
                </button>
              </div>
            )}
          </div>

          <div className="border-t-2 border-[#151515]/15 p-4 pt-3">
            {saveResult && (
              <p className={`mb-2 rounded border-2 p-2 text-[11px] font-bold ${
                saveResultIsError
                  ? 'border-red-500 bg-red-50 text-red-800'
                  : 'border-emerald-600 bg-emerald-50 text-emerald-800'
              }`}>
                {saveResult}
              </p>
            )}

            {import.meta.env.DEV && streetZones.length > 0 && (
              <div className="mb-2 rounded border-2 border-sky-300 bg-sky-50 p-2 text-[10px] text-sky-950">
                <p className="font-black uppercase">Connected street drape pilot</p>
                <p className="mt-0.5">
                  {streetsWithAtlas > 0
                    ? `${streetsWithAtlas}/${streetZones.length} streets use the reviewed shared atlas.`
                    : 'Import one reviewed north-up atlas for the complete street network.'}
                </p>
                <input
                  ref={streetAtlasInputRef}
                  type="file"
                  accept="image/png,image/jpeg"
                  className="hidden"
                  onChange={(event) => void handleStreetAtlasImport(event)}
                />
                <button
                  type="button"
                  onClick={() => streetAtlasInputRef.current?.click()}
                  disabled={importingStreetAtlas}
                  className="mt-1.5 flex w-full items-center justify-center gap-1.5 rounded border border-sky-800 bg-white px-2 py-1 font-black uppercase hover:bg-sky-100 disabled:opacity-50"
                >
                  {importingStreetAtlas
                    ? <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    : <Upload className="h-3.5 w-3.5" />}
                  {importingStreetAtlas ? 'Applying atlas…' : 'Import reviewed street atlas'}
                </button>
                {streetAtlasStatus && (
                  <p className={`mt-1 font-bold ${streetAtlasStatus.kind === 'error' ? 'text-red-700' : 'text-emerald-700'}`}>
                    {streetAtlasStatus.message}
                  </p>
                )}
              </div>
            )}

            <button
              type="button"
              onClick={() => void runBatch(true)}
              disabled={planning || saving}
              className="flex w-full items-center justify-center gap-2 rounded border-2 border-[#151515] bg-[#c9ff3d] px-3 py-2 text-xs font-black uppercase shadow-[3px_3px_0_0_#151515] disabled:opacity-50"
            >
              {planning ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
              Rebuild buildings
            </button>

            <button
              type="button"
              onClick={() => void handlePlaceAll(!canBuildCommunity)}
              disabled={(items.length === 0 && groundItems.length === 0) || placingAll || planning || saving}
              title={canBuildCommunity
                ? 'Compile every plan zone: supported buildings use real LEGO families, unsupported families use exact-footprint neutral massing, and parks/streets become generated ground systems.'
                : 'Rebuild every current building, public-realm system, and residual landscape in one atomic scene revision.'}
              className="mt-2 flex w-full items-center justify-center gap-2 rounded border-2 border-[#151515] bg-[#28c7e8] px-3 py-2 text-xs font-black uppercase shadow-[3px_3px_0_0_#151515] disabled:opacity-50"
            >
              {placingAll ? <Loader2 className="h-4 w-4 animate-spin" /> : <MapPin className="h-4 w-4" />}
              {canBuildCommunity ? 'Generate to 3D' : 'Rebuild current 3D scene'}
            </button>

            <button
              type="button"
              onClick={() => void handleSaveAll()}
              disabled={savable.length === 0 || saving || planning || placingAll}
              title={savable.length === 0
                ? 'No assembled zone has a generated building yet — generate buildings first, then save their recipes.'
                : 'Save every assembled zone as its building’s recipe (without creating buildings).'}
              className="mt-2 flex w-full items-center justify-center gap-2 rounded border-2 border-[#151515] bg-white px-3 py-2 text-xs font-black uppercase shadow-[3px_3px_0_0_#151515] disabled:opacity-50"
            >
              {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
              Save all recipes
            </button>

            <button
              type="button"
              onClick={onClose}
              className="mt-2 flex w-full items-center justify-center gap-2 rounded border-2 border-[#151515] bg-white px-3 py-2 text-xs font-black uppercase shadow-[3px_3px_0_0_#151515]"
            >
              <X className="h-4 w-4" />
              Close
            </button>
          </div>
        </aside>

        <main className="relative min-w-0 flex-1 bg-[#1b1b1b]">
          <button
            type="button"
            onClick={onClose}
            className="absolute right-3 top-3 z-10 rounded bg-black/60 p-2 text-white hover:bg-black"
            aria-label="Close Generate to 3D"
          >
            <X className="h-4 w-4" />
          </button>

          {placedCount > 0 ? (
            <Canvas shadows camera={{ position: [110, 90, 150], fov: 42 }} dpr={[1, 2]}>
              <PreviewErrorBoundary>
                <Suspense fallback={<Progress />}>
                  <BuilderScene items={items} />
                </Suspense>
              </PreviewErrorBoundary>
            </Canvas>
          ) : (
            <div className="flex h-full items-center justify-center text-center text-white/55">
              <div>
                <Blocks className="mx-auto mb-3 h-10 w-10" />
                <p className="max-w-md text-sm font-bold">
                  {planning
                    ? 'Assembling the plan from LEGO modules…'
                    : items.length === 0 && groundItems.length === 0
                      ? 'No community zones in this plan yet.'
                      : items.length === 0
                        ? 'Parks and streets are ready to build on the Google-tile globe.'
                      : 'Nothing could be placed — see the zone list for details.'}
                </p>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>,
    document.body,
  );
}
