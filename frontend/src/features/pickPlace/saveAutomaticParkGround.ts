import { runProjectWrite } from '@/utils/projectWriteQueue';
import type { QueryClient } from '@tanstack/react-query';
import type { SiteZone } from '@/types';
import { siteZonesApi } from '@/services/api';
import { advanceDerivedZoneRevision } from '@/store/undoActions';
import { parkFootprintKey } from '@/components/viewer/globe/parkTerrain';
import type { ParkTerrainProfile } from '@/components/viewer/globe/parkTerrain';

/** Derived data: no toast or undo step. Bind the write to the sampled revision,
 * including time spent waiting behind an authored write in the project queue. */
export async function saveAutomaticParkGround(
  client: QueryClient,
  projectId: string,
  source: SiteZone,
  profile: ParkTerrainProfile,
): Promise<boolean> {
  return runProjectWrite(client, projectId, async () => {
    const key = ['site-zones', projectId],
      current = client
        .getQueryData<SiteZone[]>(key)
        ?.find((z) => z.id === source.id);
    if (
      !current ||
      current.updated_at !== source.updated_at ||
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
            // Replace Google vegetation inside the measured park outline.
            // The park's saved terrain mesh retains the hillside itself.
            community_3d_mask_existing_tiles: true,
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
  });
}
