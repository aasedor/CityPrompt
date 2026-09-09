import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';
import type { SiteZone } from '@/types';
import type { RoadNetworkSnapshot } from '@/utils/proceduralRoadNetwork';

/** One request per authored road revision, shared between 2D/3D consumers.
 * A failed/pending revision displays source polygons, never stale junctions.
 */
export function useRoadNetwork(zones: SiteZone[]) {
  const roads = zones.filter((zone) => zone.zone_type === 'road' && zone.properties?.procedural_road === 1);
  const projectId = roads[0]?.project_id;
  const signature = JSON.stringify(roads.map((zone) => [zone.id, zone.coordinates, zone.properties]));
  return useQuery({
    queryKey: ['road-network', projectId, signature],
    enabled: !!projectId && roads.every((zone) => !zone.id.startsWith('temp-')),
    queryFn: async ({ signal }) => (await api.get<RoadNetworkSnapshot>(
      `/api/v1/site-zones/projects/${projectId}/road-network`, { signal },
    )).data,
    staleTime: 30_000,
    retry: false,
  });
}
