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
import { isCatalogueOnlyScene } from './catalogue';
import { representationNotice } from './representationNotice';

const physicalZone = (zone: SiteZone) => resolveCommunity3DKind(zone) !== null && !zone.id.startsWith('temp-');
const physicalScopeZone = (zone: SiteZone) => zone.zone_type !== 'site_boundary'
  && zone.properties?._plan_role !== 'framework_height'
  && !zone.id.startsWith('temp-');

export function authoredPlacementKey(zones: SiteZone[], includeRuntimeEntrance = true): string {
  return JSON.stringify(zones.map(zone => ({ id: zone.id, coordinates: zone.coordinates,
    design: Object.fromEntries(Object.entries(zone.properties ?? {})
      .filter(([name]) => (includeRuntimeEntrance || name !== 'pedestrian_building_entrance')
        && /^(pick_place|native_home|building_footprint_|development_|green_space_|road_|width$|floors$|floor_height$|height|custom_style_|generation_style_input$|neighborhood_park_layout$|park_trio_layout$|pedestrian_|park_access_points$|community_3d_landscape_mode$)/.test(name))
      .sort(([a],[b]) => a.localeCompare(b))) })).sort((a,b) => a.id.localeCompare(b.id)));
}

/** One queued rebuild per authored change. Compilation metadata never schedules itself. */
export function useAutomatic3D(projectId: string | undefined, zones: SiteZone[], saving: boolean) {
  const client = useQueryClient();
  const [status, setStatus] = useState<'idle'|'updating'|'ready'|'error'>('idle');
  const [message, setMessage] = useState('');
  const [attempt, setAttempt] = useState(0);
  const [assetError, setAssetError] = useState<{projectId:string|undefined;zoneId:string;revision:string;message:string;kind:'park'|'street'}|null>(null);
  const state = useRef({ projectId, busy: false, completed: '', failed: '' });
  const latest = useRef(zones);
  latest.current = zones;
  useEffect(()=>{
    const onAssetError=(event:Event)=>{
      const detail=(event as CustomEvent<{zoneId:string;revision:string;message:string}>).detail;
      const kind=event.type==='cityprompt:native-street-error'?'street':'park';
      if(!detail || !latest.current.some(zone=>zone.id===detail.zoneId && (kind==='street'?nativeStreetRevision(zone):JSON.stringify(zone.properties?.green_space_native_layout ?? null))===detail.revision))return;
      setAssetError({projectId,...detail,kind});
    };
    window.addEventListener('cityprompt:native-park-error',onAssetError);
    window.addEventListener('cityprompt:native-street-error',onAssetError);
    return()=>{window.removeEventListener('cityprompt:native-park-error',onAssetError);window.removeEventListener('cityprompt:native-street-error',onAssetError);};
  },[projectId]);
  const candidates = zones.filter(physicalZone);
  const scopeZones = zones.filter(physicalScopeZone);
  const boundary = deriveCityPromptWorkflow(zones).activeBoundary;
  // Catalogue placements build immediately. Other designs enter this path after
  // their first explicit 3D build, so subsequent moves keep renders current.
  const eligible = isCatalogueOnlyScene(zones)
    || candidates.some(zone => getCommunity3DMeta(zone) || zone.properties?.community_3d);
  // The building entrance is derived beside the native model, and is not an
  // input to the backend building source hash. Recompiling on a width/anchor
  // edit changes the model's compiled_at while Undo can restore older zone
  // metadata, stranding an otherwise identical model. Keep the full authored
  // key below for revision comparisons; only the rebuild trigger excludes it.
  const key = authoredPlacementKey([...scopeZones, ...(boundary ? [boundary] : [])], false);
  const compiled = deriveCityPromptWorkflow(zones).sceneReady;

  useEffect(() => {
    if (state.current.projectId !== projectId) {
      state.current = { projectId, busy: false, completed: '', failed: '' };
      setStatus('idle'); setMessage('');
    }
    const run = state.current;
    if (!projectId || !eligible || saving || run.busy || candidates.length === 0 || run.failed === key) return;
    if (run.completed === key && compiled) return;
    if (!run.completed && compiled) { run.completed = key; setStatus('ready'); return; }
    const timer = window.setTimeout(async () => {
      run.busy = true; setStatus('updating'); setMessage('');
      try {
        const result = await runProjectWrite(client, projectId, async () => {
          const currentZones = client.getQueryData<SiteZone[]>(['site-zones', projectId]) ?? latest.current;
          const sources = currentZones.filter(physicalZone);
          const scope = currentZones.filter(physicalScopeZone);
          if (!sources.length) return { plannedMasses: 0 };
          const result = await compileMixedCommunity3D(sources, undefined, {
            includeResidualLandscape: true,
            scopeZoneIds: scope.map(zone => zone.id),
          });
          const saved = await siteZonesApi.list(projectId);
          // Derived writes may advance undo's revision only over our own exact source.
          for (const source of sources) {
            const after = saved.find(zone => zone.id === source.id);
            if (after && authoredPlacementKey([source]) === authoredPlacementKey([after])) {
              advanceDerivedZoneRevision(client, projectId, source.id, source.updated_at, after.updated_at);
            }
          }
          client.setQueryData(['site-zones', projectId], saved);
          return result;
        });
        await Promise.all([
          client.invalidateQueries({ queryKey: ['site-zones', projectId] }),
          client.invalidateQueries({ queryKey: ['project', projectId] }),
        ]);
        run.completed = key;
        if (state.current === run) {
          setStatus('ready');
          setMessage(result.plannedMasses ? 'Some detailed models are unavailable. Simple building volumes are shown.' : 'Your 3D scene updates automatically.');
        }
      } catch (error) {
        const newestZones = latest.current;
        const newestBoundary = deriveCityPromptWorkflow(newestZones).activeBoundary;
        const newestKey = authoredPlacementKey([
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
  }, [projectId, key, compiled, eligible, saving, client, attempt]);

  const currentAssetError = assetError?.projectId === projectId && zones.some(zone=>zone.id===assetError?.zoneId && (assetError.kind==='street'?nativeStreetRevision(zone):JSON.stringify(zone.properties?.green_space_native_layout ?? null))===assetError.revision) ? assetError : null;
  const visibleStatus = currentAssetError ? 'error' : eligible && !compiled && candidates.length > 0 && status !== 'error' ? 'updating' : status;
  return { status: visibleStatus, message: currentAssetError?.message ?? (visibleStatus === 'updating' ? 'Your placed objects are being updated.' : visibleStatus === 'ready' ? representationNotice(candidates) : message), busy: visibleStatus === 'updating',
    retry: () => { setAssetError(null); clearFailedNativeParkLoads(); clearFailedNativeStreetLoads(); state.current.failed = ''; state.current.completed = ''; setAttempt(value => value + 1); } };
}
