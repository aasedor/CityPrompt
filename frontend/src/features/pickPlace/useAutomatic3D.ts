import { runProjectWrite } from '@/utils/projectWriteQueue';
import { useEffect, useRef, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import type { SiteZone } from '@/types';
import { siteZonesApi, getApiErrorMessage } from '@/services/api';
import { isCommunity3DCompiled } from '@/features/community3d/community3d';
import { compileMixedCommunity3D } from '@/features/legoAssembly/communityCompiler';
import { advanceDerivedZoneRevision } from '@/store/undoActions';
import { assetForZone } from './catalogue';

const automaticZone = (zone: SiteZone) => (assetForZone(zone) || zone.properties?.pick_place_automatic_3d === true) && !zone.id.startsWith('temp-');

export function authoredPlacementKey(zones: SiteZone[]): string {
  return JSON.stringify(zones.map(zone => ({ id: zone.id, coordinates: zone.coordinates,
    design: Object.fromEntries(Object.entries(zone.properties ?? {})
      .filter(([name]) => /^(pick_place|native_home|development_|green_space_|road_|width$|floors$|floor_height$|height|custom_style_|generation_style_input$|neighborhood_park_layout$|park_trio_layout$|pedestrian_|park_access_points$)/.test(name))
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
  const candidates = zones.filter(automaticZone);
  const key = authoredPlacementKey(candidates);
  const compiled = candidates.every(isCommunity3DCompiled);

  useEffect(() => {
    if (state.current.projectId !== projectId) {
      state.current = { projectId, busy: false, completed: '', failed: '' };
      setStatus('idle'); setMessage('');
    }
    const run = state.current;
    if (!projectId || saving || run.busy || key === '[]' || run.failed === key) return;
    if (run.completed === key && compiled) return;
    if (!run.completed && compiled) { run.completed = key; setStatus('ready'); return; }
    const timer = window.setTimeout(async () => {
      run.busy = true; setStatus('updating'); setMessage('');
      try {
        const result = await runProjectWrite(client, projectId, async () => {
          const sources = (client.getQueryData<SiteZone[]>(['site-zones', projectId]) ?? latest.current).filter(automaticZone);
          if (!sources.length) return { plannedMasses: 0 };
          const result = await compileMixedCommunity3D(sources, undefined, { includeResidualLandscape: false, recoverSourceChanges: false });
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
  }, [projectId, key, compiled, saving, client, attempt]);

  const visibleStatus = !compiled && candidates.length > 0 && status !== 'error' ? 'updating' : status;
  return { status: visibleStatus, message: visibleStatus === 'updating' ? 'Your placed objects are being updated.' : message, busy: visibleStatus === 'updating',
    retry: () => { state.current.failed = ''; state.current.completed = ''; setAttempt(value => value + 1); } };
}
