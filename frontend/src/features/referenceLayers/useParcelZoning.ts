import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import type { SiteZone } from '@/types';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { readBrowserPreference, writeBrowserPreference } from '@/utils/browserPreferences';
import { fetchParcelZoning, parcelBounds, parcelCoverageProblem } from './parcelZoning';

export function useParcelZoning(projectId: string | undefined, zones: SiteZone[]) {
  const key = `cityprompt:parcel-zoning:${projectId}`;
  const [choices, setChoices] = useState<Record<string, { lines: boolean; labels: boolean }>>({});
  const saved = useMemo(() => {
    try { const value = JSON.parse(readBrowserPreference(key) ?? '{}'); return { lines: value?.lines === true, labels: value?.labels === true }; } catch { return { lines: false, labels: false }; }
  }, [key]);
  const visibility = choices[key] ?? saved;
  const boundary = getActiveSiteBoundary(zones);
  const bounds = parcelBounds(boundary?.coordinates ?? []);
  const problem = parcelCoverageProblem(bounds);
  const query = useQuery({
    queryKey: ['parcel-zoning-fabric-v1', projectId, bounds],
    queryFn: ({ signal }) => fetchParcelZoning(bounds!, AbortSignal.any([signal, AbortSignal.timeout(30_000)])),
    enabled: Boolean(projectId && bounds && !problem && (visibility.lines || visibility.labels)),
    staleTime: 15 * 60_000, gcTime: 30 * 60_000, retry: false,
  });
  const toggle = (part: 'lines' | 'labels') => {
    const next = { ...visibility, [part]: !visibility[part] };
    setChoices(current => ({ ...current, [key]: next }));
    writeBrowserPreference(key, JSON.stringify(next));
  };
  return { ...visibility, toggle, problem, data: problem ? undefined : query.data, loading: query.isFetching, error: query.error, retry: () => { void query.refetch(); } };
}
export type ParcelZoningState = ReturnType<typeof useParcelZoning>;
