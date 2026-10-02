import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import type { SiteZone } from '@/types';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { readBrowserPreference, writeBrowserPreference } from '@/utils/browserPreferences';
import { fetchZoningLabels, zoningBounds, zoningCoverageProblem } from './zoningLabels';

export function useZoningLabels(projectId: string | undefined, zones: SiteZone[]) {
  // Retain the previous label preference while ignoring the retired line toggle.
  const key = `cityprompt:parcel-zoning:${projectId}`;
  const [choices, setChoices] = useState<Record<string, { labels: boolean }>>({});
  const saved = useMemo(() => {
    try { const value = JSON.parse(readBrowserPreference(key) ?? '{}'); return { labels: value?.labels === true }; } catch { return { labels: false }; }
  }, [key]);
  const visibility = choices[key] ?? saved;
  const boundary = getActiveSiteBoundary(zones);
  const bounds = zoningBounds(boundary?.coordinates ?? []);
  const problem = zoningCoverageProblem(bounds);
  const query = useQuery({
    queryKey: ['zoning-district-labels-v2', projectId, boundary?.coordinates],
    queryFn: ({ signal }) => fetchZoningLabels(boundary!.coordinates, AbortSignal.any([signal, AbortSignal.timeout(30_000)])),
    enabled: Boolean(projectId && bounds && !problem && visibility.labels),
    staleTime: 15 * 60_000, gcTime: 30 * 60_000, retry: false,
  });
  const toggle = () => {
    const next = { ...visibility, labels: !visibility.labels };
    setChoices(current => ({ ...current, [key]: next }));
    writeBrowserPreference(key, JSON.stringify(next));
  };
  return { ...visibility, toggle, problem, data: problem ? undefined : query.data, loading: query.isFetching, error: query.error, retry: () => { void query.refetch(); } };
}
export type ZoningLabelsState = ReturnType<typeof useZoningLabels>;
