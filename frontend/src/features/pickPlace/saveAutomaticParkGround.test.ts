import { beforeEach, describe, it, expect, vi } from 'vitest';
import { QueryClient } from '@tanstack/react-query';
import type { SiteZone } from '@/types';
import { siteZonesApi } from '@/services/api';
import { createZoneCoordinatesAction } from '@/store/undoActions';
import { saveAutomaticParkGround } from './saveAutomaticParkGround';
import type { ParkTerrainProfile } from '@/components/viewer/globe/parkTerrain';
vi.mock('@/services/api', () => ({
  siteZonesApi: { update: vi.fn() },
  buildingsApi: {},
}));
const zone = {
  id: 'park',
  project_id: 'p',
  coordinates: [
    [1, 2],
    [2, 2],
    [2, 3],
  ],
  properties: { name: 'keep' },
  updated_at: 'r1',
} as unknown as SiteZone;
const profile = { version: 1 } as ParkTerrainProfile;
beforeEach(() => vi.clearAllMocks());
describe('quiet automatic ground persistence', () => {
  it('does not save a late result after movement or deletion', async () => {
    const client = new QueryClient();
    client.setQueryData(
      ['site-zones', 'p'],
      [{ ...zone, coordinates: [[9, 9]] }],
    );
    expect(await saveAutomaticParkGround(client, 'p', zone, profile)).toBe(
      false,
    );
    client.setQueryData(['site-zones', 'p'], []);
    expect(await saveAutomaticParkGround(client, 'p', zone, profile)).toBe(
      false,
    );
    expect(siteZonesApi.update).not.toHaveBeenCalled();
  });
  it('merges current properties and advances our undo revision without another undo step', async () => {
    const client = new QueryClient();
    client.setQueryData(
      ['site-zones', 'p'],
      [{ ...zone, properties: { ...zone.properties, color: 'new' } }],
    );
    const action = createZoneCoordinatesAction(
      'p',
      'park',
      [[0, 0]],
      zone.coordinates,
      client,
      'r1',
    );
    vi.mocked(siteZonesApi.update)
      .mockResolvedValueOnce({ ...zone, updated_at: 'r2' })
      .mockResolvedValueOnce({ ...zone, updated_at: 'r3' });
    expect(await saveAutomaticParkGround(client, 'p', zone, profile)).toBe(
      true,
    );
    expect(siteZonesApi.update).toHaveBeenNthCalledWith(
      1,
      'park',
      {
        expected_updated_at: 'r1',
        properties: {
          name: 'keep',
          color: 'new',
          park_terrain: profile,
          proposed_terrace: null,
          community_3d_mask_existing_tiles: true,
        },
      },
      { skipHistory: true },
    );
    await action.undo();
    expect(siteZonesApi.update).toHaveBeenLastCalledWith(
      'park',
      expect.objectContaining({ expected_updated_at: 'r2' }),
      { skipHistory: true },
    );
  });
  it('refreshes conflicts without overwriting the newer row', async () => {
    const client = new QueryClient();
    client.setQueryData(['site-zones', 'p'], [zone]);
    vi.mocked(siteZonesApi.update).mockRejectedValue({
      response: { status: 409 },
    });
    expect(await saveAutomaticParkGround(client, 'p', zone, profile)).toBe(
      false,
    );
    expect(client.getQueryData(['site-zones', 'p'])).toEqual([zone]);
  });
});
