import type { QueryClient } from '@tanstack/react-query';
import type { SiteZone } from '@/types';
import { siteZonesApi } from '@/services/api';
import { advanceDerivedZoneRevision } from '@/store/undoActions';
import { parkFootprintKey } from '@/components/viewer/globe/parkTerrain';
import type { ParkTerrainProfile } from '@/components/viewer/globe/parkTerrain';

/** Derived data: no toast or undo step; optimistic version check protects edits. */
export async function saveAutomaticParkGround(
  client: QueryClient,
  projectId: string,
  source: SiteZone,
  profile: ParkTerrainProfile,
): Promise<boolean> {
  const key = ['site-zones', projectId],
    current = client
      .getQueryData<SiteZone[]>(key)
      ?.find((z) => z.id === source.id);
  if (
    !current ||
    parkFootprintKey(current) !== parkFootprintKey(source) ||
    client.isMutating({ mutationKey: ['save-zone', projectId] })
  )
    return false;
  try {
    const saved = await siteZonesApi.update(
      source.id,
      {
        expected_updated_at: current.updated_at,
        properties: {
          ...current.properties,
          park_terrain: profile,
          proposed_terrace: null,
        },
      },
      { skipHistory: true },
    );
    advanceDerivedZoneRevision(
      client,
      projectId,
      source.id,
      current.updated_at,
      saved.updated_at,
    );
    client.setQueryData<SiteZone[]>(key, (zones) =>
      zones?.map((z) =>
        z.id === source.id && z.updated_at === current.updated_at ? saved : z,
      ),
    );
    await client.invalidateQueries({ queryKey: key });
    return true;
  } catch (error) {
    const status = (error as { response?: { status?: number } })?.response
      ?.status;
    if (status === 409 || status === 404) {
      await client.invalidateQueries({ queryKey: key });
      return false;
    }
    throw error;
  }
}
