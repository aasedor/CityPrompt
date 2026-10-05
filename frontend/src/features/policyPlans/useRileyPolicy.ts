import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import type { SiteZone } from '@/types';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { readBrowserPreference, writeBrowserPreference } from '@/utils/browserPreferences';
import { loadRileyPolicy, policyCoverageProblem, policyOverlay, readPolicyPreferences, selectPolicySite, type PolicyPreferences } from './rileyPolicy';
import { rileyDesignation } from './rileyDesignations';

const EMPTY_COORDINATES: number[][] = [];

export function useRileyPolicy(projectId: string | undefined, zones: SiteZone[]) {
  const key = `cityprompt:policy-map:v1:${projectId}`;
  const saved = useMemo(() => readPolicyPreferences(readBrowserPreference(key)), [key]);
  const [choices, setChoices] = useState<Record<string, PolicyPreferences>>({});
  const [inspection, setInspection] = useState<{ key: string; category: string; featureId?: string } | null>(null);
  const preferences = choices[key] ?? saved;
  const coordinates = getActiveSiteBoundary(zones)?.coordinates ?? EMPTY_COORDINATES;
  const coverageProblem = policyCoverageProblem(coordinates);
  const query = useQuery({ queryKey: ['riley-urban-form-38P2025-v1'], queryFn: loadRileyPolicy,
    enabled: Boolean(projectId && preferences.enabled && !coverageProblem), staleTime: Infinity, gcTime: 30 * 60_000, retry: false });
  const selection = useMemo(() => {
    if (!preferences.enabled || coverageProblem || !query.data) return undefined;
    try { return { value: selectPolicySite(query.data, coordinates), error: null }; }
    catch { return { value: undefined, error: 'The plan could not be matched to this boundary. Check the site outline.' }; }
  }, [preferences.enabled, coverageProblem, query.data, coordinates]);
  const problem = coverageProblem ?? selection?.error ?? (selection?.value && !selection.value.hasCoverage ? 'This site is outside the Riley plan boundary.' : null);
  const data = useMemo(() => {
    if (!preferences.enabled || problem || !query.data || !selection?.value) return undefined;
    return policyOverlay(query.data, preferences.clipToSite ? selection.value.features : query.data.features);
  }, [preferences.enabled, preferences.clipToSite, problem, query.data, selection]);
  const legend = useMemo(() => {
    const withinSite = new Set(selection?.value?.features.map(feature => feature.properties.category));
    const entries = new Map<string, { color: string; withinSite: boolean }>();
    for (const area of data?.districts ?? []) entries.set(area.label, { color: area.color!, withinSite: withinSite.has(area.label) });
    return [...entries].map(([category, value]) => ({ category, ...value }));
  }, [data, selection]);
  const designation = inspection?.key === key ? rileyDesignation(inspection.category) : undefined;
  const selected = useMemo(() => designation && data && legend.some(entry => entry.category === designation.name)
    && (!inspection?.featureId || data.districts.some(area => area.id === inspection.featureId))
    ? { designation, featureId: inspection?.featureId } : null, [designation, data, legend, inspection]);
  const update = (patch: Partial<PolicyPreferences>) => {
    const next = { ...preferences, ...patch };
    writeBrowserPreference(key, JSON.stringify(next));
    setChoices(current => ({ ...current, [key]: next }));
  };
  return { ...preferences, data, legend, selected, problem, loading: query.isFetching, error: query.error,
    selectCategory: (category: string) => {
      if (rileyDesignation(category) && legend.some(entry => entry.category === category)) setInspection({ key, category });
    },
    selectArea: (featureId: string) => {
      const area = data?.districts.find(area => area.id === featureId);
      if (area && rileyDesignation(area.label)) setInspection({ key, category: area.label, featureId });
    },
    clearSelection: () => setInspection(null),
    partial: selection?.value?.partial ?? false,
    setEnabled: (enabled: boolean) => { if (!enabled) setInspection(null); update({ enabled }); },
    setClipToSite: (clipToSite: boolean) => { setInspection(null); update({ clipToSite }); },
    setOpacity: (opacity: number) => { if (Number.isFinite(opacity)) { if (opacity <= 0) setInspection(null); update({ opacity: Math.min(1, Math.max(0, opacity)) }); } },
    retry: () => { void query.refetch(); } };
}
export type RileyPolicyState = ReturnType<typeof useRileyPolicy>;
