import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import type { SiteZone } from '@/types';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { readBrowserPreference, writeBrowserPreference } from '@/utils/browserPreferences';
import { policyOverlay, selectPolicySite } from './rileyPolicy';
import { loadLocalAreaPlan, localAreaPlan, matchLocalAreaPlans, readLocalPolicyPreferences, type LocalPolicyPreferences } from './localAreaPlans';

const EMPTY_COORDINATES: number[][] = [];

export function useLocalAreaPolicy(projectId: string | undefined, zones: SiteZone[], exploration: number[][] = EMPTY_COORDINATES) {
  // Preserve Riley visibility/opacity/clipping saved by existing projects.
  const key = `cityprompt:policy-map:v1:${projectId}`;
  const saved = useMemo(() => readLocalPolicyPreferences(readBrowserPreference(key)), [key]);
  const [choices, setChoices] = useState<Record<string, LocalPolicyPreferences>>({});
  const [inspection, setInspection] = useState<{ key: string; category: string; featureId?: string } | null>(null);
  const preferences = choices[key] ?? saved;
  const boundary = getActiveSiteBoundary(zones);
  const coordinates = boundary?.coordinates ?? EMPTY_COORDINATES;
  const matchCoordinates = boundary ? coordinates : exploration;
  const coverage = useMemo(() => matchLocalAreaPlans(matchCoordinates), [matchCoordinates]);
  const plan = preferences.planId === 'auto' ? coverage.matches[0] : localAreaPlan(preferences.planId);
  const inspectionKey = `${key}:${plan?.snapshot}`;
  const query = useQuery({ queryKey: ['local-area-urban-form', plan?.snapshot],
    queryFn: () => { if (!plan) throw new Error('Select a plan'); return loadLocalAreaPlan(plan.id); },
    enabled: Boolean(projectId && preferences.enabled && plan), staleTime: Infinity, gcTime: 30 * 60_000, retry: false });
  const selection = useMemo(() => {
    if (!preferences.enabled || !plan || !query.data) return undefined;
    if (coordinates.length < 3) return { value: { features: [], hasCoverage: false, partial: false }, error: null };
    try { return { value: selectPolicySite(query.data, coordinates), error: null }; }
    catch { return { value: undefined, error: 'The plan could not be matched to this boundary. Check the site outline.' }; }
  }, [preferences.enabled, plan, query.data, coordinates]);
  const problem = (!plan ? boundary ? coverage.problem : 'Choose a local area plan below to browse its map, or move to an area with an approved plan.' : null) ?? selection?.error ?? null;
  const data = useMemo(() => {
    if (!preferences.enabled || problem || !query.data || !selection?.value) return undefined;
    return policyOverlay(query.data, preferences.clipToSite && boundary ? selection.value.features : query.data.features);
  }, [preferences.enabled, preferences.clipToSite, boundary, problem, query.data, selection]);
  const legend = useMemo(() => {
    const withinSite = new Set(selection?.value?.features.map(feature => feature.properties.category));
    const available = new Set(data?.districts.map(area => area.label));
    return (plan?.designations ?? []).filter(item => available.has(item.name)).map(item => ({ category: item.name, color: item.color, withinSite: withinSite.has(item.name) }));
  }, [data, plan, selection]);
  const designation = inspection?.key === inspectionKey ? plan?.designations.find(item => item.name === inspection.category) : undefined;
  const selected = useMemo(() => designation && data && preferences.opacity > 0 && legend.some(entry => entry.category === designation.name)
    && (!inspection?.featureId || data.districts.some(area => area.id === inspection.featureId))
    ? { designation, featureId: inspection?.featureId, plan } : null, [designation, data, preferences.opacity, legend, inspection, plan]);
  const update = (patch: Partial<LocalPolicyPreferences>) => {
    const next = { ...preferences, ...patch };
    writeBrowserPreference(key, JSON.stringify(next));
    setChoices(current => ({ ...current, [key]: next }));
  };
  return { ...preferences, hasBoundary: Boolean(boundary), plan, matchingPlans: coverage.matches, data, legend, selected, problem,
    loading: query.isFetching, error: query.error,
    outsideSite: Boolean(boundary && selection?.value && !selection.value.hasCoverage),
    selectCategory: (category: string) => {
      if (legend.some(entry => entry.category === category)) setInspection({ key: inspectionKey, category });
    },
    selectArea: (featureId: string) => {
      const area = data?.districts.find(area => area.id === featureId);
      if (area && plan?.designations.some(item => item.name === area.label)) setInspection({ key: inspectionKey, category: area.label, featureId });
    },
    clearSelection: () => setInspection(null),
    partial: selection?.value?.partial ?? false,
    setPlan: (planId: string) => { if (planId === 'auto' || localAreaPlan(planId)) { setInspection(null); update({ planId }); } },
    setEnabled: (enabled: boolean) => { if (!enabled) setInspection(null); update({ enabled }); },
    setClipToSite: (clipToSite: boolean) => { setInspection(null); update({ clipToSite }); },
    setOpacity: (opacity: number) => { if (Number.isFinite(opacity)) { if (opacity <= 0) setInspection(null); update({ opacity: Math.min(1, Math.max(0, opacity)) }); } },
    retry: () => { void query.refetch(); } };
}
export type LocalAreaPolicyState = ReturnType<typeof useLocalAreaPolicy>;
