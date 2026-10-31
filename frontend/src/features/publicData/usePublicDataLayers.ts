import { useMemo, useReducer } from 'react';
import { useQueries } from '@tanstack/react-query';
import type { SiteZone } from '@/types';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { fetchPublicLayer, publicDataBounds, PUBLIC_DATA_LIMITS } from './publicData';
import { PUBLIC_DATASETS, PUBLIC_REFERENCES } from './publicDatasets';

const EMPTY = new Set<string>();
const knownIds = new Set([...PUBLIC_DATASETS, ...PUBLIC_REFERENCES].map(item => item.id));
type Selection = Record<string, Set<string>>;
type Change = { project: string; id: string; enabled: boolean };
function select(state: Selection, { project, id, enabled }: Change): Selection {
  if (!knownIds.has(id)) return state;
  const current = state[project] ?? EMPTY;
  if (current.has(id) === enabled) return state;
  const isMap = PUBLIC_DATASETS.some(item => item.id === id);
  if (enabled && isMap && PUBLIC_DATASETS.filter(item => current.has(item.id)).length >= PUBLIC_DATA_LIMITS.layers) return state;
  const next = new Set(current);
  if (enabled) next.add(id); else next.delete(id);
  return { ...state, [project]: next };
}

/** Session-only reference choices. Never imports into or changes the project. */
export function usePublicDataLayers(projectId: string | undefined, zones: SiteZone[]) {
  const [selection, dispatch] = useReducer(select, {});
  const selectedIds = projectId ? selection[projectId] ?? EMPTY : EMPTY;
  const boundary = getActiveSiteBoundary(zones);
  const area = useMemo(() => publicDataBounds(boundary?.coordinates ?? []), [boundary?.coordinates]);
  const selected = PUBLIC_DATASETS.filter(item => selectedIds.has(item.id));
  // Removing a query observer consumes TanStack's signal and aborts the request,
  // including queued work. No disabled observers or placeholder site data remain.
  const results = useQueries({ queries: selected.map(dataset => ({
    queryKey: ['optional-public-data-v1', projectId, dataset.id, area.bounds],
    queryFn: ({ signal }: { signal: AbortSignal }) => fetchPublicLayer(dataset.id, area.bounds!, AbortSignal.any([signal, AbortSignal.timeout(20_000)])),
    enabled: Boolean(projectId && area.bounds && !area.problem),
    staleTime: 10 * 60_000, gcTime: 30 * 60_000, retry: false,
    refetchOnWindowFocus: false, refetchOnReconnect: false, refetchOnMount: true,
  })) });
  const states = selected.map((dataset, index) => {
    const query = results[index];
    return { dataset, layer: area.problem ? undefined : query.data, loading: query.isFetching,
      error: query.error ? query.error instanceof Error && query.error.name === 'TimeoutError'
        ? 'This public dataset took too long to respond. Try again or choose a smaller site.'
        : query.error instanceof Error ? query.error.message : 'This public dataset could not load. Try again.' : null,
      retry: () => { if (!area.problem) void query.refetch(); },
    };
  });
  return { selectedIds, states, problem: area.problem,
    atLimit: selected.length >= PUBLIC_DATA_LIMITS.layers,
    layers: states.flatMap(state => state.layer?.feature_count ? [state.layer] : []),
    setEnabled: (id: string, enabled: boolean) => { if (projectId) dispatch({ project: projectId, id, enabled }); },
  };
}

export type PublicDataLayersState = ReturnType<typeof usePublicDataLayers>;
