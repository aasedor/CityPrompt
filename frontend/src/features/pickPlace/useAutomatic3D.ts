import { clearFailedNativeParkLoads } from '@/features/parks/nativeParkAssets';
import { clearFailedNativeStreetLoads } from '@/components/viewer/globe/nativeStreetAssets';
import { nativeStreetRevision } from '@/components/viewer/globe/nativeStreetReadiness';
import { runProjectWrite } from '@/utils/projectWriteQueue';
import { useEffect, useRef, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import type { SiteZone } from '@/types';
import { siteZonesApi, getApiErrorMessage } from '@/services/api';
import { getCommunity3DMeta, resolveCommunity3DKind } from '@/features/community3d/community3d';
import { compileMixedCommunity3D } from '@/features/legoAssembly/communityCompiler';
import { deriveCityPromptWorkflow } from '@/features/workflow/cityPromptWorkflow';
import { advanceDerivedZoneRevision } from '@/store/undoActions';
import { representationNotice } from './representationNotice';
import { nativeBuildingContract, nativeBuildingUrl } from './nativeBuildingContract';
import { buildingAssetRevision, retryBuildingAssets } from './buildingAssetRecovery';
import { automaticSiteTreesEnabled } from '@/features/siteLandscape/automaticSiteTrees';

const physicalZone = (zone: SiteZone) => resolveCommunity3DKind(zone) !== null && !zone.id.startsWith('temp-');
const physicalScopeZone = (zone: SiteZone) => zone.zone_type !== 'site_boundary'
  && zone.properties?._plan_role !== 'framework_height'
  && !zone.id.startsWith('temp-');

// Additional authored inputs from residual_landscape.community_3d_source_properties.
// Compilation metadata, asset URLs, timestamps and Building linkage stay excluded.
const customSourceFields = new Set([
  '_plan_role', '_saved_layout', 'native_plot_axes', 'unit_count', 'facade_material',
  'secondary_material', 'roof_style', 'roof_material', 'description_text',
  'planting_structure', 'tree_density', 'skate_spectator_edge', 'paving_type',
  'planting_type', 'water_features', 'street_role', 'lane_count', 'surface_type',
  'material', 'plan_centerline', 'generation_style_inputs',
]);

export function authoredPlacementKey(zones: SiteZone[], includeRuntimeEntrance = true): string {
  return JSON.stringify(zones.map(zone => ({ id: zone.id, zoneType: zone.zone_type, coordinates: zone.coordinates,
    automaticSiteTrees: zone.zone_type === 'site_boundary' ? automaticSiteTreesEnabled(zone) : undefined,
    design: Object.fromEntries(Object.entries(zone.properties ?? {})
      .filter(([name]) => name !== 'community_3d_landscape_mode' && (includeRuntimeEntrance || name !== 'pedestrian_building_entrance')
        && (customSourceFields.has(name) || /^(pick_place|user_generated_|native_home|building_footprint_|development_|green_space_|plaza_|road_|width$|floors$|floor_height$|height|custom_style_|generation_style_input$|neighborhood_park_layout$|park_trio_layout$|pedestrian_|park_access_points$|community_3d_landscape_mode$)/.test(name)))
      .sort(([a],[b]) => a.localeCompare(b))) })).sort((a,b) => a.id.localeCompare(b.id)));
}

/** One queued rebuild per authored change. Compilation metadata never schedules itself. */
export function useAutomatic3D(projectId: string | undefined, zones: SiteZone[], saving: boolean,
  visibility?: { hiddenLayers: ReadonlySet<string>; comparingPlans: boolean }) {
  const client = useQueryClient();
  const [status, setStatus] = useState<'idle'|'updating'|'ready'|'error'>('idle');
  const [message, setMessage] = useState('');
  const [attempt, setAttempt] = useState(0);
  const [assetError, setAssetError] = useState<{projectId:string|undefined;zoneId:string;revision:string;message:string;kind:'park'|'street'|'building'}|null>(null);
  const state = useRef({ projectId, busy: false, completed: '', failed: '', force: false });
  const latest = useRef(zones);
  // Local drafts may be invalid or rejected. They remain in the editor, but
  // must not change the persisted scene's compilation key or readiness.
  const persistedZones = zones.filter(zone => !zone.id.startsWith('temp-'));
  latest.current = persistedZones;
  useEffect(()=>{
    const onAssetError=(event:Event)=>{
      const detail=(event as CustomEvent<{zoneId:string;revision:string;message:string}>).detail;
      const kind=event.type==='cityprompt:native-street-error'?'street':event.type==='cityprompt:native-building-error'?'building':'park';
      if(!detail || !latest.current.some(zone=>zone.id===detail.zoneId && (kind==='street'?nativeStreetRevision(zone):kind==='building'?buildingAssetRevision(zone):JSON.stringify(zone.properties?.green_space_native_layout ?? null))===detail.revision))return;
      setAssetError({projectId,...detail,kind});
    };
    window.addEventListener('cityprompt:native-park-error',onAssetError);
    window.addEventListener('cityprompt:native-street-error',onAssetError);
    window.addEventListener('cityprompt:native-building-error',onAssetError);
    return()=>{window.removeEventListener('cityprompt:native-park-error',onAssetError);window.removeEventListener('cityprompt:native-street-error',onAssetError);window.removeEventListener('cityprompt:native-building-error',onAssetError);};
  },[projectId]);
  const candidates = persistedZones.filter(physicalZone);
  const scopeZones = persistedZones.filter(physicalScopeZone);
  const boundary = deriveCityPromptWorkflow(persistedZones).activeBoundary;
  // Every retained authored scene prepares automatically, including old/custom
  // scenes without initial compilation metadata. Permission is gated by projectId.
  const eligible = candidates.length > 0 && !visibility?.comparingPlans;
  const visibilityKey = JSON.stringify([...(visibility?.hiddenLayers ?? [])].sort());
  // The building entrance is derived beside the native model, and is not an
  // input to the backend building source hash. Recompiling on a width/anchor
  // edit changes the model's compiled_at while Undo can restore older zone
  // metadata, stranding an otherwise identical model. Keep the full authored
  // key below for revision comparisons; only the rebuild trigger excludes it.
  const key = visibilityKey + authoredPlacementKey([...scopeZones, ...(boundary ? [boundary] : [])], false);
  const compiled = deriveCityPromptWorkflow(persistedZones).sceneReady;
  const canRefreshDetail = candidates.some(zone => getCommunity3DMeta(zone)?.generator === 'planned_massing'
    && !(zone.zone_type === 'building' && nativeBuildingUrl(zone)));
  const hasInstalledMassingUpgrade = candidates.some(zone => zone.zone_type === 'building'
    && getCommunity3DMeta(zone)?.generator === 'planned_massing' && nativeBuildingContract(zone)
    && !nativeBuildingUrl(zone));

  useEffect(() => {
    const hiddenLayers = new Set<string>(JSON.parse(visibilityKey));
    if (state.current.projectId !== projectId) {
      state.current = { projectId, busy: false, completed: '', failed: '', force: false };
      setStatus('idle'); setMessage('');
    }
    const run = state.current;
    if (!candidates.length) {
      // Deleting the failed object (or the last object during a request) is
      // recovery. An obsolete request must not leave this scene in error/busy.
      run.failed = ''; run.completed = ''; run.force = false;
      setStatus('idle'); setMessage('');
      return;
    }
    if (!projectId || !eligible || saving || run.busy) return;
    if (!run.force && compiled && (run.completed === key || (!run.completed && !hasInstalledMassingUpgrade))) {
      run.completed = key; run.failed = ''; setStatus('ready'); setMessage(''); return;
    }
    if (run.failed === key) return;
    const timer = window.setTimeout(async () => {
      run.busy = true; run.force = false; setStatus('updating'); setMessage('');
      try {
        const { result, readiness } = await runProjectWrite(client, projectId, async () => {
          // Refresh objects from the full cache, but keep the selected scenario.
          // Hidden alternatives must never occupy or invalidate its landscape.
          const currentZones = (client.getQueryData<SiteZone[]>(['site-zones', projectId]) ?? latest.current)
            .filter(zone => !zone.id.startsWith('temp-'))
            .filter(zone => !hiddenLayers.has(String(zone.properties?._imported_from ?? '')));
          const sources = currentZones.filter(physicalZone);
          const scope = currentZones.filter(physicalScopeZone);
          const currentBoundary = deriveCityPromptWorkflow(currentZones).activeBoundary;
          if (!sources.length) return { result: { plannedMasses: 0 }, readiness: null };
          const result = await compileMixedCommunity3D(sources, undefined, {
            includeResidualLandscape: automaticSiteTreesEnabled(currentBoundary),
            scopeMode: hiddenLayers.size ? 'selection' : 'project',
            scopeZoneIds: scope.map(zone => zone.id),
          });
          const saved = await siteZonesApi.list(projectId);
          // Derived writes may advance undo's revision only over our own exact source.
          for (const source of [...sources, ...(currentBoundary ? [currentBoundary] : [])]) {
            const after = saved.find(zone => zone.id === source.id);
            if (after && authoredPlacementKey([source]) === authoredPlacementKey([after])) {
              advanceDerivedZoneRevision(client, projectId, source.id, source.updated_at, after.updated_at);
            }
          }
          client.setQueryData(['site-zones', projectId], saved);
          const savedVisible = saved.filter(zone => !zone.id.startsWith('temp-')
            && !hiddenLayers.has(String(zone.properties?._imported_from ?? '')));
          return { result, readiness: deriveCityPromptWorkflow(savedVisible) };
        });
        // Object compilation can commit new Building representations while an
        // applied landscape still needs manual regeneration. Refresh both caches
        // before reporting that remaining issue so capture sees matching records.
        await Promise.all([
          client.invalidateQueries({ queryKey: ['site-zones', projectId] }),
          client.invalidateQueries({ queryKey: ['project', projectId] }),
        ]);
        // Applying the landscape later can finish this same authored revision.
        run.completed = key;
        if (readiness && !readiness.sceneReady) {
          throw new Error(readiness.renderReason);
        }
        if (state.current === run) {
          setStatus('ready');
          setMessage(result.plannedMasses ? 'Some detailed models are unavailable. Simple building volumes are shown.' : 'Your 3D scene updates automatically.');
        }
      } catch (error) {
        const newestZones = latest.current;
        const newestBoundary = deriveCityPromptWorkflow(newestZones).activeBoundary;
        const newestKey = visibilityKey + authoredPlacementKey([
          ...newestZones.filter(physicalScopeZone),
          ...(newestBoundary ? [newestBoundary] : []),
        ], false);
        // An obsolete request may correctly fail the backend's source-revision
        // guard after a student makes another edit. Keep the newer edit queued;
        // only surface an error when the failed request still represents the
        // current authored scene.
        if (newestKey !== key) {
          if (state.current === run) { setStatus('updating'); setMessage(''); }
        } else {
          run.failed = key;
          if (state.current === run) { setStatus('error'); setMessage(getApiErrorMessage(error)); }
        }
      } finally {
        run.busy = false;
        if (state.current === run) setAttempt(value => value + 1);
      }
    }, 700);
    return () => window.clearTimeout(timer);
  }, [projectId, key, visibilityKey, compiled, eligible, saving, client, attempt, candidates.length, hasInstalledMassingUpgrade]);

  const currentAssetError = assetError?.projectId === projectId && zones.some(zone=>zone.id===assetError?.zoneId && (assetError.kind==='street'?nativeStreetRevision(zone):assetError.kind==='building'?buildingAssetRevision(zone):JSON.stringify(zone.properties?.green_space_native_layout ?? null))===assetError.revision) ? assetError : null;
  const visibleStatus = currentAssetError ? 'error' : eligible && !compiled && candidates.length > 0 && status !== 'error' ? 'updating' : status;
  return { status: visibility?.comparingPlans ? 'error' : visibleStatus, message: visibility?.comparingPlans ? 'Choose one scenario in Layers to update its 3D scene.' : currentAssetError?.message ?? (visibleStatus === 'updating' ? 'Your placed objects are being updated.' : visibleStatus === 'ready' ? representationNotice(candidates) : message), busy: !visibility?.comparingPlans && visibleStatus === 'updating', canRefreshDetail,
    retry: () => { setAssetError(null); clearFailedNativeParkLoads(); clearFailedNativeStreetLoads(); retryBuildingAssets(); state.current.failed = ''; state.current.completed = ''; state.current.force = true; setAttempt(value => value + 1); } };
}
