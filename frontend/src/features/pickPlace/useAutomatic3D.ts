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

export function authoredPlacementKey(zones: SiteZone[], includeRuntimeEntrance = true): string {
  return JSON.stringify(zones.map(zone => ({ id: zone.id, coordinates: zone.coordinates,
    design: Object.fromEntries(Object.entries(zone.properties ?? {})
      .filter(([name]) => (includeRuntimeEntrance || name !== 'pedestrian_building_entrance')
        && /^(pick_place|native_home|development_|green_space_|road_|width$|floors$|floor_height$|height|custom_style_|generation_style_input$|neighborhood_park_layout$|park_trio_layout$|pedestrian_|park_access_points$|community_3d_landscape_mode$)/.test(name))
      .sort(([a],[b]) => a.localeCompare(b))) })).sort((a,b) => a.id.localeCompare(b.id)));
}

/** One queued rebuild per authored change. Compilation metadata never schedules itself. */
export function useAutomatic3D(projectId: string | undefined, zones: SiteZone[], saving: boolean) {
  const client = useQueryClient();
  const [status, setStatus] = useState<'idle'|'updating'|'ready'|'error'>('idle');
  const [message, setMessage] = useState('');
  const [attempt, setAttempt] = useState(0);
  const state = useRef({ projectId, busy: false, completed: '', failed: '' });
  const latest = useRef(zones);
  latest.current = zones;
  const candidates = zones.filter(physicalZone);
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
  const key = authoredPlacementKey([...candidates, ...(boundary ? [boundary] : [])], false);
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
          if (!sources.length) return { plannedMasses: 0 };
          const result = await compileMixedCommunity3D(sources, undefined, {
            includeResidualLandscape: true,
            scopeZoneIds: sources.map(zone => zone.id),
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
        run.failed = key;
        if (state.current === run) { setStatus('error'); setMessage(getApiErrorMessage(error)); }
      } finally {
        run.busy = false;
        if (state.current === run) setAttempt(value => value + 1);
      }
    }, 700);
    return () => window.clearTimeout(timer);
  }, [projectId, key, compiled, eligible, saving, client, attempt]);

  const visibleStatus = eligible && !compiled && candidates.length > 0 && status !== 'error' ? 'updating' : status;
  return { status: visibleStatus, message: visibleStatus === 'updating' ? 'Your placed objects are being updated.' : visibleStatus === 'ready' ? representationNotice(candidates) : message, busy: visibleStatus === 'updating',
    retry: () => { state.current.failed = ''; state.current.completed = ''; setAttempt(value => value + 1); } };
}
