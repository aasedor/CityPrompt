import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import type { SiteZone } from '@/types';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { readBrowserPreference, writeBrowserPreference } from '@/utils/browserPreferences';
import { fetchZoningLabels, zoningBounds, zoningCoverageProblem } from './zoningLabels';

export function useZoningLabels(projectId: string | undefined, zones: SiteZone[]) {
  // District outlines are distinct from the retired cadastral lot-line toggle.
  const key = `cityprompt:parcel-zoning:${projectId}`;
  const [choices, setChoices] = useState<Record<string, { labels: boolean; lines: boolean }>>({});
  const saved = useMemo(() => {
    try { const value = JSON.parse(readBrowserPreference(key) ?? '{}'); return { labels: value?.labels === true, lines: value?.districtLines === true }; } catch { return { labels: false, lines: false }; }
  }, [key]);
  const visibility = choices[key] ?? saved;
  const boundary = getActiveSiteBoundary(zones);
  const bounds = zoningBounds(boundary?.coordinates ?? []);
  const problem = zoningCoverageProblem(bounds);
  const query = useQuery({
    queryKey: ['zoning-district-map-v3', projectId, boundary?.coordinates],
    queryFn: ({ signal }) => fetchZoningLabels(boundary!.coordinates, AbortSignal.any([signal, AbortSignal.timeout(30_000)])),
    enabled: Boolean(projectId && bounds && !problem && (visibility.labels || visibility.lines)),
    staleTime: 15 * 60_000, gcTime: 30 * 60_000, retry: false,
  });
  const toggleChoice = (choice: 'labels' | 'lines') => {
    const next = { ...visibility, [choice]: !visibility[choice] };
    setChoices(current => ({ ...current, [key]: next }));
    writeBrowserPreference(key, JSON.stringify({ labels: next.labels, districtLines: next.lines }));
  };
  return { ...visibility, toggle: () => toggleChoice('labels'), toggleLines: () => toggleChoice('lines'), problem, data: problem ? undefined : query.data, loading: query.isFetching, error: query.error, retry: () => { void query.refetch(); } };
}
export type ZoningLabelsState = ReturnType<typeof useZoningLabels>;
