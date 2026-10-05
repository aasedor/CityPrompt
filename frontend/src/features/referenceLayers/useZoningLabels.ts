import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import type { SiteZone } from '@/types';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { readBrowserPreference, writeBrowserPreference } from '@/utils/browserPreferences';
import { fetchZoningLabels, zoningBounds, zoningCoverageProblem } from './zoningLabels';
import { readZoningPreferences, type ZoningPreferences } from './zoningAppearance';

export function useZoningLabels(projectId: string | undefined, zones: SiteZone[]) {
  // District outlines are distinct from the retired cadastral lot-line toggle.
  const key = `cityprompt:parcel-zoning:${projectId}`;
  const [choices, setChoices] = useState<Record<string, ZoningPreferences>>({});
  const saved = useMemo(() => readZoningPreferences(readBrowserPreference(key)), [key]);
  const visibility = choices[key] ?? saved;
  const boundary = getActiveSiteBoundary(zones);
  const bounds = zoningBounds(boundary?.coordinates ?? []);
  const problem = zoningCoverageProblem(bounds);
  const query = useQuery({
    queryKey: ['zoning-district-map-v3', projectId, boundary?.coordinates],
    queryFn: ({ signal }) => fetchZoningLabels(boundary!.coordinates, AbortSignal.any([signal, AbortSignal.timeout(30_000)])),
    enabled: Boolean(projectId && bounds && !problem && visibility.enabled && (visibility.labels || visibility.lines || visibility.fill)),
    staleTime: 15 * 60_000, gcTime: 30 * 60_000, retry: false,
  });
  const update = (patch: Partial<ZoningPreferences>) => {
    const next = { ...visibility, ...patch };
    writeBrowserPreference(key, JSON.stringify({ ...next, districtLines: next.lines, lines: undefined }));
    setChoices(current => ({ ...current, [key]: next }));
  };
  return { ...visibility, setEnabled: (enabled: boolean) => update({ enabled }),
    toggle: () => update({ labels: !visibility.labels }), toggleLines: () => update({ lines: !visibility.lines }),
    toggleFill: () => update({ fill: !visibility.fill }),
    setFillOpacity: (fillOpacity: number) => { if (Number.isFinite(fillOpacity)) update({ fillOpacity: Math.min(1, Math.max(0, fillOpacity)) }); },
    problem, data: problem ? undefined : query.data, loading: query.isFetching, error: query.error, retry: () => { void query.refetch(); } };
}
export type ZoningLabelsState = ReturnType<typeof useZoningLabels>;
