import { useQuery, useQueryClient } from '@tanstack/react-query';
import { zoneHistoryApi } from '@/services/api';
import type { ZoneHistoryEntry } from '@/types';

export function useZoneHistory(projectId: string | undefined) {
  const queryClient = useQueryClient();
  const queryKey = ['zone-history', projectId, 'all'];

  const result = useQuery({
    queryKey,
    queryFn: () => zoneHistoryApi.list(projectId!, { limit: 50 }),
    enabled: !!projectId,
    refetchInterval: 15000,
  });

  const history: ZoneHistoryEntry[] = result.data?.items ?? [];
  const total = result.data?.total ?? 0;
  const hasMore = result.data?.has_more ?? false;

  const loadMore = async () => {
    if (!result.data || !hasMore) return;
    const moreData = await zoneHistoryApi.list(projectId!, {
      limit: 50,
      offset: result.data.items.length,
    });
    queryClient.setQueryData(queryKey, {
      items: [...result.data.items, ...moreData.items],
      total: moreData.total,
      has_more: moreData.has_more,
    });
  };

  return { history, total, isLoading: result.isLoading, hasMore, loadMore };
}
