import { Suspense, useCallback, useEffect, useRef, useState, type ChangeEvent } from 'react';
import { createPortal } from 'react-dom';
import { useQueryClient } from '@tanstack/react-query';
import { Canvas } from '@react-three/fiber';
import { Bounds, Environment, Grid, OrbitControls } from '@react-three/drei';
import { AlertTriangle, Blocks, Check, Loader2, MapPin, RefreshCw, Route, Save, Trees, Upload, X } from 'lucide-react';
import { getApiErrorMessage, siteZonesApi } from '@/services/api';
import type { SiteZone } from '@/types';
import { resolveCommunity3DKind } from '@/features/community3d/community3d';
import { allSettledWithConcurrency } from './allSettledWithConcurrency';
import {
  legoArchetypeContextFromZone,
  legoAssemblyApi,
  getLegoPlanningFailure,
  type Community3DCompileResponse,
  type LegoAssemblyPlan,
} from './legoAssemblyApi';
import {
  ModuleInstance,
  PreviewErrorBoundary,
  Progress,
  fitIsStretched,
  fitPreservesArchetypeForm,
} from './legoShared';
import {
  assertCommunityCompileResponse,
  deriveGroundItems,
  deriveItems,
  compileMixedCommunity3D,
  isCommunity3DSourceRevisionConflict,
  isSourceLockedRlasmZone,
  recipeFromPlan,
  type CommunityCompileExpectation,
  type GroundBuildItem,
  type ZoneBuildItem,
} from './communityCompiler';
import {
  getStreetNetworkGroundMeta,
  importStreetNetworkGroundTexture,
} from '@/components/viewer/globe/streetNetworkGroundTexture';
import { usesArchetypeOwnedParkSurface } from '@/components/viewer/globe/parkLegoFamilies';
import { compileProjectCommunity3D } from './projectCommunityCompile';
import { detachedPlotCoordinates } from './detachedPlot';

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
}: {
  zones: SiteZone[];
  onClose: () => void;
  /** Top-level workflow entry: plan, then compile the complete scene once. */
  autoGenerate?: boolean;
}) {
  const [items, setItems] = useState<ZoneBuildItem[]>(() => deriveItems(zones));
  const [groundItems, setGroundItems] = useState<GroundBuildItem[]>(() => deriveGroundItems(zones));
  const [planning, setPlanning] = useState(false);
  const [saving, setSaving] = useState(false);
  const [placingAll, setPlacingAll] = useState(false);
  const [generationStage, setGenerationStage] = useState<string | null>(null);
  const [initialPlanningComplete, setInitialPlanningComplete] = useState(false);
  const [saveResult, setSaveResult] = useState<string | null>(null);
  const queryClient = useQueryClient();
  const autoGenerateStartedRef = useRef(false);
  const initialPlanStartedRef = useRef(false);
  const batchInFlightRef = useRef(false);
  const batchEpochRef = useRef(0);
  const placingAllRef = useRef(false);
  const streetAtlasInputRef = useRef<HTMLInputElement | null>(null);
  const [streetAtlasStatus, setStreetAtlasStatus] = useState<{
    kind: 'success' | 'error';
    message: string;
  } | null>(null);
  const [importingStreetAtlas, setImportingStreetAtlas] = useState(false);
  const projectId = zones[0]?.project_id;
  const streetZones = zones.filter((zone) => resolveCommunity3DKind(zone) === 'street');
  const streetsWithAtlas = streetZones.filter((zone) => getStreetNetworkGroundMeta(zone)).length;

  // The globe reads buildings from the project query and links from the zone
  // query — both must refetch for the placed stack to appear.
  const refetchPlacedData = useCallback(async () => {
    if (!projectId) return [];
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['project', projectId] }),
      queryClient.invalidateQueries({ queryKey: ['site-zones', projectId] }),
    ]);
    return queryClient.getQueryData<SiteZone[]>(['site-zones', projectId]) ?? [];
  }, [queryClient, projectId]);

  const setPlaceState = useCallback((zoneId: string, placeState: ZoneBuildItem['placeState']) => {
    setItems((prev) => prev.map((item) => (item.zone.id === zoneId ? { ...item, placeState } : item)));
  }, []);

  const handlePlaceOne = useCallback(async (target: ZoneBuildItem) => {
    if (!target.plan || !target.offset || target.placeState === 'placing') return;
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
    const blockingPlanningFailures = items.filter((item) => (
      !item.plan && Boolean(item.error) && !item.familyMissing && !item.familyIncompatible
    ));
    if (blockingPlanningFailures.length > 0) {
      setSaveResult(
        `${blockingPlanningFailures.length} building plan${blockingPlanningFailures.length === 1 ? '' : 's'} `
        + 'need review. Nothing was compiled; retry planning before Generate to 3D.',
      );
      return;
    }
    const invalidFootprints = items.filter((item) => item.offset === null);
    if (invalidFootprints.length > 0) {
      setSaveResult(
        `${invalidFootprints.length} building zone${invalidFootprints.length === 1 ? '' : 's'} `
        + 'need a usable footprint. Nothing was compiled; repair the plan before Generate to 3D.',
      );
      return;
    }
    const placeable = items.filter(
      (item): item is ZoneBuildItem & { plan: LegoAssemblyPlan; offset: [number, number] } => (
        Boolean(item.plan && item.offset) && (forceRebuild || item.placeState !== 'placed')
      ),
    );
    const massingOnly = items.filter((item) => (
      !item.plan
      && (item.familyMissing || item.familyIncompatible)
      && Boolean(item.offset)
      && (forceRebuild || item.massingState !== 'compiled')
    ));
    const groundToCompile = groundItems.filter((item) => (
      forceRebuild || item.state !== 'compiled'
    ));
    if (
      (placeable.length === 0 && massingOnly.length === 0 && groundToCompile.length === 0)
      || placingAllRef.current
      || importingStreetAtlas
    ) return;
    const placeableIds = new Set(placeable.map((item) => item.zone.id));
    const massingOnlyIds = new Set(massingOnly.map((item) => item.zone.id));
    const groundToCompileIds = new Set(groundToCompile.map((item) => item.zone.id));
    const requestedZoneIds = new Set([
      ...placeableIds,
      ...massingOnlyIds,
      ...groundToCompileIds,
    ]);
    const expectedItems: CommunityCompileExpectation[] = [
      ...placeable.map((item) => ({
        zoneId: item.zone.id,
        label: item.label,
        kind: 'building' as const,
        generators: new Set(['lego_assembly'] as const),
      })),
      ...massingOnly.map((item) => ({
        zoneId: item.zone.id,
        label: item.label,
        kind: 'building' as const,
        generators: new Set(
          isSourceLockedRlasmZone(item.zone)
            ? ['meshy'] as const
            : ['planned_massing'] as const,
        ),
      })),
      ...groundToCompile.map((item) => ({
        zoneId: item.zone.id,
        label: item.zone.name || item.kind,
        kind: item.kind,
        generators: new Set([item.kind === 'park' ? 'park_kit' : 'street_section'] as const),
      })),
    ];
    placingAllRef.current = true;
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
      setGenerationStage('Placing 3D buildings and public-realm objects');
      let authoritativeById = new Map(sourceZones.map((zone) => [zone.id, zone]));
      const authoritativeZone = (zoneId: string): SiteZone => {
        const zone = authoritativeById.get(zoneId);
        if (!zone) throw new Error('A plan zone changed while Generate to 3D was preparing. Refresh and retry.');
        return zone;
      };
      if (!projectId) throw new Error('The project could not be identified for Community 3D generation.');
      let result: Community3DCompileResponse;
      let responseAlreadyValidated = false;
      let recoveredBuildings: ZoneBuildItem[] | undefined;
      try {
        result = await compileProjectCommunity3D(projectId, [
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
      } catch (error) {
        if (!isCommunity3DSourceRevisionConflict(error)) throw error;
        setGenerationStage('Refreshing changed zones and rebuilding their 3D plans');
        const panelZoneIds = new Set(sourceZones.map((zone) => zone.id));
        const refreshedZones = (await siteZonesApi.list(projectId)).filter((zone) => (
          panelZoneIds.has(zone.id)
        ));
        if (refreshedZones.length !== panelZoneIds.size) {
          throw new Error(
            'A Community 3D source zone was removed while the scene was being prepared. '
            + 'The plan was refreshed; review it before rebuilding.',
          );
        }
        queryClient.setQueryData(['site-zones', projectId], refreshedZones);
        authoritativeById = new Map(refreshedZones.map((zone) => [zone.id, zone]));
        const refreshedRequestedZones = refreshedZones.filter((zone) => requestedZoneIds.has(zone.id));
        if (refreshedRequestedZones.length !== requestedZoneIds.size) {
          throw new Error(
            'A requested Community 3D source zone was removed while the scene was being prepared. '
            + 'The plan was refreshed; review it before rebuilding.',
          );
        }
        const recovered = await compileMixedCommunity3D(
          refreshedRequestedZones,
          undefined,
          {
            scopeZoneIds: refreshedZones
              .filter((zone) => resolveCommunity3DKind(zone) !== null)
              .map((zone) => zone.id),
          },
        );
        result = recovered.response;
        recoveredBuildings = recovered.resolvedBuildings;
        // The shared compiler replans the refreshed subset and validates its
        // potentially changed detailed-vs-massing capability classification.
        responseAlreadyValidated = true;
      }
      if (!responseAlreadyValidated) assertCommunityCompileResponse(expectedItems, result);
      const refreshedAfterCompile = await refetchPlacedData();
      if (refreshedAfterCompile.length > 0) {
        authoritativeById = new Map(refreshedAfterCompile.map((zone) => [zone.id, zone]));
      }
      const recoveredById = new Map(
        (recoveredBuildings ?? []).map((item) => [item.zone.id, item]),
      );
      const representationById = new Map(result.items.map((item) => [item.zone_id, item]));
      setItems((prev) => prev.map((item) => {
        if (!requestedZoneIds.has(item.zone.id)) return item;
        const base = recoveredById.get(item.zone.id) ?? item;
        const zone = authoritativeZone(item.zone.id);
        const representation = representationById.get(item.zone.id);
        if (
          representation?.generator === 'lego_assembly'
          || representation?.generator === 'meshy'
        ) {
          return { ...base, zone, placeState: 'placed', massingState: undefined };
        }
        if (representation?.generator === 'planned_massing') {
          return {
            ...base,
            zone,
            plan: undefined,
            placeState: undefined,
            massingState: 'compiled',
          };
        }
        return { ...base, zone };
      }));
      setGroundItems((prev) => prev.map((item) => (
        groundToCompileIds.has(item.zone.id)
          ? { ...item, zone: authoritativeZone(item.zone.id), state: 'compiled' }
          : item
      )));
      const groundCount = result.counts.park + result.counts.street;
      const detailedCount = result.items.filter((item) => (
        item.generator === 'lego_assembly' || item.generator === 'meshy'
      )).length;
      const massingCount = result.items.filter((item) => item.generator === 'planned_massing').length;
      const residual = result.residual_landscape;
      const residualSummary = residual && residual.boundary_count > 0
        ? `; landscaped ${Math.round(residual.area_sqm).toLocaleString()} m² of residual site`
          + ` with ${residual.placement_count} tree${residual.placement_count === 1 ? '' : 's'}`
        : '';
      setSaveResult(
        `Built ${detailedCount} detailed building${detailedCount === 1 ? '' : 's'}, `
        + `${massingCount} correct-size massing fallback${massingCount === 1 ? '' : 's'}, and `
        + `${groundCount} park/street layer${groundCount === 1 ? '' : 's'}`
        + residualSummary,
      );
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
      placingAllRef.current = false;
      setPlacingAll(false);
    }
  }, [groundItems, importingStreetAtlas, items, projectId, queryClient, refetchPlacedData, zones]);

  const runBatch = useCallback(async (replacePlaced = false) => {
    // StrictMode replays mount effects and fast double-clicks can land before
    // React paints the disabled state. Only one planning epoch may own panel
    // state at a time, so a late result can never overwrite a compiled row.
    if (batchInFlightRef.current || placingAllRef.current || importingStreetAtlas) return;
    batchInFlightRef.current = true;
    const batchEpoch = ++batchEpochRef.current;
    const isCurrentBatch = () => batchEpochRef.current === batchEpoch;
    const latestPanelZoneById = new Map([
      ...items.map((item) => [item.zone.id, item.zone] as const),
      ...groundItems.map((item) => [item.zone.id, item.zone] as const),
    ]);
    const cachedZoneById = new Map(
      (projectId
        ? queryClient.getQueryData<SiteZone[]>(['site-zones', projectId]) ?? []
        : []).map((zone) => [zone.id, zone]),
    );
    const latestZones = zones.map((zone) => (
      cachedZoneById.get(zone.id) ?? latestPanelZoneById.get(zone.id) ?? zone
    ));
    const base = deriveItems(latestZones);
    setItems(base);
    setGroundItems(deriveGroundItems(latestZones));
    setSaveResult(null);
    setInitialPlanningComplete(false);
    if (base.length === 0) {
      setInitialPlanningComplete(true);
      batchInFlightRef.current = false;
      return;
    }
    setPlanning(true);
    try {
      const results = await allSettledWithConcurrency(
      base,
      (item) => legoAssemblyApi.plan({
          target_width_m: item.targets.width_m,
          target_depth_m: item.targets.depth_m,
          target_floors: item.targets.floors,
          footprint_profile: item.targets.footprint_profile,
          footprint_local_m: detachedPlotCoordinates(item.archetypeId, item.zone.coordinates, item.targets),
          wing_depth_m: item.targets.wing_depth_m,
          project_id: item.zone.project_id,
          // A manually drawn parcel is an intentional design target. Match the
          // single-building LEGO composer by allowing modular families to
          // repeat or uniformly contain-scale into that footprint. AI master
          // plans stay strict because their recipes are catalog-locked and
          // certified again by the atomic community compiler.
          allow_forced_fit: !String(item.zone.properties?._plan_scenario ?? '').trim(),
          ...legoArchetypeContextFromZone(item.zone.properties),
        }),
      8,
    );
      if (!isCurrentBatch()) return;
      const plannedItems = base.map((item, index) => {
      const result = results[index];
      if (result.status === 'fulfilled') return { ...item, plan: result.value };
      const planningFailure = getLegoPlanningFailure(result.reason);
      return {
        ...item,
        error: planningFailure?.message || getApiErrorMessage(result.reason, 'Could not assemble this zone.'),
        familyMissing: planningFailure?.code === 'family_not_found',
        familyIncompatible: planningFailure?.code === 'family_incompatible',
      };
    });
      setItems(plannedItems);

    // "Rebuild" must update recipes already on the globe and upgrade a prior
    // exact-massing fallback as soon as its reviewed family is imported.
    // Merely recalculating the preview would leave either the old content hash
    // or neutral massing live. The initial panel load still plans read-only.
      if (replacePlaced) {
      const replaceable = plannedItems.filter(
        (item): item is ZoneBuildItem & { plan: LegoAssemblyPlan } => (
          Boolean(item.plan)
          && (item.placeState === 'placed' || item.massingState === 'compiled')
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
        const replacedIds = new Set(
          replaceable
            .filter((_item, index) => replaced[index].status === 'fulfilled')
            .map((item) => item.zone.id),
        );
        const replacedCount = replaced.filter((result) => result.status === 'fulfilled').length;
        setSaveResult(
          failedIds.size > 0
            ? `Rebuilt ${replacedCount} of ${replaceable.length} placed building${replaceable.length === 1 ? '' : 's'}`
            : `Rebuilt ${replacedCount} placed building${replacedCount === 1 ? '' : 's'} with the latest family assets`,
        );
        const refreshedZones = await refetchPlacedData();
        if (!isCurrentBatch()) return;
        // Placing the refreshed recipe intentionally marks its owning source
        // zone stale, which advances zone.updated_at. Carry that authoritative
        // revision into the next atomic Community 3D request; otherwise the
        // immediately-following "Rebuild current 3D scene" deterministically
        // fails optimistic concurrency with the pre-place timestamp.
        const refreshedById = new Map(refreshedZones.map((zone) => [zone.id, zone]));
        setItems(plannedItems.map((item) => ({
          ...item,
          zone: refreshedById.get(item.zone.id) ?? item.zone,
          ...(failedIds.has(item.zone.id)
            ? { placeState: 'failed' as const }
            : replacedIds.has(item.zone.id)
              ? { placeState: 'placed' as const, massingState: undefined }
              : {}),
        })));
      }
      }
      setInitialPlanningComplete(true);
    } catch (error) {
      setSaveResult(getApiErrorMessage(
        error,
        'Could not finish rebuilding the building plans. Refresh the project and retry.',
      ));
      setInitialPlanningComplete(false);
    } finally {
      if (isCurrentBatch()) {
        batchInFlightRef.current = false;
        setPlanning(false);
      }
    }
  }, [groundItems, importingStreetAtlas, items, projectId, queryClient, refetchPlacedData, zones]);

  // Plan every buildable zone once when the panel opens; "Rebuild all" re-runs it.
  useEffect(() => {
    if (initialPlanStartedRef.current) return;
    initialPlanStartedRef.current = true;
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
  const missingFamilyCount = items.filter((item) => item.familyMissing).length;
  const incompatibleFamilyCount = items.filter((item) => item.familyIncompatible).length;
  const massingFallbackCount = missingFamilyCount + incompatibleFamilyCount;
  const issueCount = items.filter((item) => (
    item.error && !item.familyMissing && !item.familyIncompatible
  )).length;
  const skippedCount = items.filter((item) => !item.offset).length;
  const placedCount = items.filter((item) => item.plan && item.offset).length;
  const compiledMassingCount = items.filter((item) => item.massingState === 'compiled').length;
  const parkCount = groundItems.filter((item) => item.kind === 'park').length;
  const streetCount = groundItems.filter((item) => item.kind === 'street').length;
  const compiledGroundCount = groundItems.filter((item) => item.state === 'compiled').length;
  const unplacedDetailedCount = items.filter(
    (item) => item.plan && item.offset && item.placeState !== 'placed',
  ).length;
  const uncompiledMassingCount = items.filter((item) => (
    !item.plan
    && (item.familyMissing || item.familyIncompatible)
    && item.offset
    && item.massingState !== 'compiled'
  )).length;
  const canBuildCommunity = (
    unplacedDetailedCount > 0
    || uncompiledMassingCount > 0
    || compiledGroundCount < groundItems.length
  );
  const hasPlaceableSceneContent = items.some((item) => Boolean(item.offset))
    || groundItems.length > 0;
  const saveResultIsError = Boolean(
    items.some((item) => item.placeState === 'failed' || item.massingState === 'failed')
    || groundItems.some((item) => item.state === 'failed'),
  );

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

  const handleStreetAtlasImport = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.currentTarget.files?.[0];
    event.currentTarget.value = '';
    if (!file || !projectId || importingStreetAtlas || planning || placingAll || saving) return;
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
              {`Detailed ${assembledCount} · Massing ready ${massingFallbackCount} · Needs footprint ${skippedCount}`}
              {issueCount > 0 ? ` · Needs review ${issueCount}` : ''}
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
                  item.error && !item.familyMissing && !item.familyIncompatible
                    ? 'border-red-300 bg-red-50'
                    : item.familyMissing || item.familyIncompatible
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
                  {!item.plan && !item.massingState && (item.familyMissing || item.familyIncompatible) && (
                    <span className="shrink-0 rounded bg-sky-100 px-1.5 py-0.5 text-[10px] font-bold text-sky-800">
                      massing ready
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
                      {item.plan.fit.placement_mode === 'detached_lots'
                        ? `${item.plan.fit.dwelling_count} separate homes within your plot`
                        : `${item.plan.family} · fit ${item.plan.fit.score.toFixed(2)}`}
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
                        disabled={!item.offset || item.placeState === 'placing' || placingAll}
                        title={item.offset
                          ? "Save this recipe on the zone's building (created if needed) and show the stack on the globe."
                          : 'Restore polygon coordinates before placing this building.'}
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
                {item.familyMissing && (
                  <p className="mt-0.5 text-amber-950">
                    <span className="font-black">Detailed family to add. </span>
                    Generate to 3D uses this exact footprint and {item.targets.floors}-floor height now;
                    importing its reviewed Sticker/LEGO family later upgrades it in place.
                  </p>
                )}
                {item.familyIncompatible && (
                  <p className="mt-0.5 text-amber-950">
                    <span className="font-black">Detailed family outside its reviewed fit. </span>
                    {item.error} Correctly sized {item.targets.floors}-floor massing remains ready for this parcel.
                  </p>
                )}
                {item.error && !item.familyMissing && !item.familyIncompatible && (
                  <p className="mt-0.5 text-red-800">{item.error}</p>
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
                          {item.state === 'compiling'
                            ? 'building…'
                            : item.state === 'compiled'
                              ? '3D ready'
                              : item.state === 'ready'
                                ? item.kind === 'park' && usesArchetypeOwnedParkSurface(item.zone)
                                  ? 'Sticker kit ready'
                                  : 'procedural ready'
                                : 'retry build'}
                        </span>
                      </div>
                      <p className="mt-0.5 text-black/55">
                        {item.kind === 'park'
                          ? usesArchetypeOwnedParkSurface(item.zone)
                            ? 'Archetype-owned skin and metric 3D depth kit; no AI drape or generic park dressing'
                            : 'Archetype-driven procedural skin with programmed 3D trees, structures, planting and seating; no image API call'
                          : getStreetNetworkGroundMeta(item.zone)
                            ? 'Imported connected road atlas with 3D curbs, markings, trees, lights, furniture and vehicles'
                            : 'Engineered procedural street surface with 3D curbs, markings, trees, lights, furniture and vehicles; no image API call'}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {massingFallbackCount > 0 && (
              <div className="rounded border border-amber-300 bg-amber-50 p-2 text-[11px] text-amber-950">
                <p className="font-bold">
                  {massingFallbackCount === 1
                    ? 'One building uses upgrade-ready massing.'
                    : `${massingFallbackCount} buildings use upgrade-ready massing.`}
                </p>
                <p className="mt-1">
                  Nothing is blocked: their drawn footprint and floor height build now. Add the reviewed
                  Sticker/LEGO families when ready, then choose Rebuild buildings to upgrade them in place.
                </p>
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
                  disabled={importingStreetAtlas || planning || placingAll || saving}
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
              disabled={planning || saving || placingAll || importingStreetAtlas}
              className="flex w-full items-center justify-center gap-2 rounded border-2 border-[#151515] bg-[#c9ff3d] px-3 py-2 text-xs font-black uppercase shadow-[3px_3px_0_0_#151515] disabled:opacity-50"
            >
              {planning ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
              Rebuild buildings
            </button>

            <button
              type="button"
              onClick={() => void handlePlaceAll(!canBuildCommunity)}
              disabled={!hasPlaceableSceneContent || placingAll || planning || saving || importingStreetAtlas || issueCount > 0 || skippedCount > 0}
              title={skippedCount > 0
                ? 'One or more buildings need a usable footprint. Repair the plan before compiling any 3D changes.'
                : issueCount > 0
                ? 'One or more building plans need review. Retry planning before compiling any 3D changes.'
                : canBuildCommunity
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
                    : compiledMassingCount > 0 || compiledGroundCount > 0
                      ? `Built ${compiledMassingCount} massing building${compiledMassingCount === 1 ? '' : 's'} and ${compiledGroundCount} park/street layer${compiledGroundCount === 1 ? '' : 's'} on the globe. Close this dialog to review the 3D scene.`
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
