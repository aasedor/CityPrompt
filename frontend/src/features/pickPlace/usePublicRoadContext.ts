import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';
import type { SiteZone } from '@/types';
import type { PublicRoadContext } from './publicRoadSuggestions';
import { isPersistedZoneId } from '@/utils/zoneIdentity';

/** Read-only lookup: never edits boundary properties or invalidates the scene. */
export function usePublicRoadContext(boundary: SiteZone | null, enabled: boolean) {
  const query = useQuery({
    queryKey: ['public-road-context', boundary?.id, boundary?.coordinates, boundary?.properties?.community_3d_mask_existing_tiles],
    queryFn: async ({ signal }) => {
      const { data } = await api.get<PublicRoadContext>(`/api/v1/site-zones/${boundary!.id}/public-road-context`, { signal, timeout: 35000 });
      return data;
    },
    enabled: Boolean(boundary && enabled && isPersistedZoneId(boundary.id)), staleTime: 10 * 60 * 1000, retry: false,
    refetchOnWindowFocus: false,
  });
  // A failed refresh must not leave old geometry active as an apparently
  // current snap target while the UI reports that the source is unavailable.
  return {...query,data:query.isError ? undefined : query.data};
}
