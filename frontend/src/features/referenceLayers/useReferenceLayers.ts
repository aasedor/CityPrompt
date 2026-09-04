import { useCallback, useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { getApiErrorMessage } from '@/services/api';
import { referenceLayerQueryKey, referenceLayersApi } from './api';

const keyFor = (projectId: string) => `cityprompt:reference-visibility:${projectId}`;

function readHidden(projectId: string): Set<string> {
  try {
    const stored: unknown = JSON.parse(localStorage.getItem(keyFor(projectId)) ?? '[]');
    return new Set(Array.isArray(stored) ? stored.filter((id): id is string => typeof id === 'string') : []);
  } catch { return new Set(); }
}

/** Visibility is personal display state; it never alters the authored proposal. */
export function useReferenceLayers(projectId: string | undefined) {
  const queryClient = useQueryClient();
  const [hiddenByProject, setHiddenByProject] = useState<Record<string, Set<string>>>({});
  const hiddenIds = useMemo(() => projectId ? hiddenByProject[projectId] ?? readHidden(projectId) : new Set<string>(), [hiddenByProject, projectId]);
  const query = useQuery({
    queryKey: referenceLayerQueryKey(projectId),
    queryFn: () => referenceLayersApi.list(projectId!),
    enabled: Boolean(projectId),
    staleTime: 30_000,
  });
  const layers = query.data?.layers ?? [];
  const toggleLayer = useCallback((layerId: string) => {
    if (!projectId) return;
    setHiddenByProject((previous) => {
      const next = new Set(previous[projectId] ?? readHidden(projectId));
      if (next.has(layerId)) next.delete(layerId);
      else next.add(layerId);
      try { localStorage.setItem(keyFor(projectId), JSON.stringify([...next])); } catch { /* private browsing can disable storage */ }
      return { ...previous, [projectId]: next };
    });
  }, [projectId]);
  const deletion = useMutation({
    mutationFn: referenceLayersApi.remove,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: referenceLayerQueryKey(projectId) }),
    onError: (error) => toast.error(getApiErrorMessage(error, 'Reference layer could not be removed.')),
  });
  return {
    layers,
    visibleLayers: layers.filter((layer) => !hiddenIds.has(layer.id)),
    hiddenIds,
    toggleLayer,
    canEdit: Boolean(query.data?.can_edit),
    removeLayer: deletion.mutate,
    deletingId: deletion.isPending ? deletion.variables : null,
    isLoading: query.isLoading,
    error: query.error ? getApiErrorMessage(query.error, 'Reference layers could not load.') : null,
    refetch: query.refetch,
  };
}
