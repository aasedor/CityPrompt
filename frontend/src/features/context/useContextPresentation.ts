import { useCallback, useEffect, useState } from 'react';
import type { SiteZone } from '@/types';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { readContextPilot, visibleContext, type ContextProviderDefinition, type ContextView } from './contextProvider';
import { readSurveyGround } from './surveyGround';

/** Opt-in developer pilot. No network request or extra control in normal use. */
export function useContextPresentation(zones: SiteZone[]) {
  const projectId = zones[0]?.project_id;
  const boundary = getActiveSiteBoundary(zones);
  const prepared = Boolean(boundary && boundary.properties?.community_3d_mask_existing_tiles !== false
    && boundary.properties?.terrain_strategy !== 'landscape' && Number.isFinite(boundary.properties?.terrain_elevation_m));
  const survey = Boolean(boundary && readSurveyGround(boundary.properties?.survey_ground));
  const [provider, setProvider] = useState<ContextProviderDefinition | null>(null);
  const [requested, setRequested] = useState<ContextView>('google');
  const [ready, setReady] = useState(false);
  const [failed, setFailed] = useState(false);
  useEffect(() => {
    setProvider(null); setRequested('google'); setReady(false); setFailed(false);
    if (!import.meta.env.DEV || import.meta.env.VITE_CONTEXT_PILOT !== 'true' || !projectId || (!prepared && !survey)) return;
    const controller = new AbortController();
    void fetch(survey ? '/sf-lidar/manifest.json' : '/context-pilot/manifest.json', { signal: controller.signal }).then(r => r.ok ? r.json() : null)
      .then(value => { if (!controller.signal.aborted) setProvider(readContextPilot(value, projectId)); })
      .catch(() => { /* Missing optional capture leaves Google available. */ });
    return () => controller.abort();
  }, [projectId, prepared, survey]);
  const available = provider?.projectId === projectId && (prepared || survey) ? provider : null;
  const select = useCallback((view: ContextView) => { setRequested(view); setReady(false); setFailed(false); }, []);
  const onReady = useCallback(() => setReady(true), []);
  const onFailure = useCallback(() => { setFailed(true); setReady(false); }, []);
  return { provider: available, requested, visible: available ? visibleContext(requested, ready, failed) : 'google' as ContextView,
    loading: Boolean(available && requested === 'capture' && !ready && !failed), failed,
    loadCapture: Boolean(available && requested === 'capture' && !failed), select, onReady, onFailure };
}
