import { beforeEach, describe, it, expect, vi } from 'vitest';
import { QueryClient } from '@tanstack/react-query';
import type { SiteZone } from '@/types';
import { siteZonesApi } from '@/services/api';
import { createZoneCoordinatesAction } from '@/store/undoActions';
import { saveAutomaticParkGround } from './saveAutomaticParkGround';
import type { ParkTerrainProfile } from '@/components/viewer/globe/parkTerrain';
import { runProjectWrite } from '@/utils/projectWriteQueue';
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
  it('discards a measurement queued before a newer grade edit finishes saving', async () => {
    const client = new QueryClient();
    client.setQueryData(['site-zones', 'p'], [zone]);
    let release!: () => void;
    const gate = new Promise<void>((resolve) => { release = resolve; });
    const edited = { ...zone, updated_at: 'r2', properties: {
      ...zone.properties, proposed_terrace: { version: 1, offsetM: 2 },
    } };
    vi.mocked(siteZonesApi.update).mockResolvedValue({ ...edited, updated_at: 'r3' });
    const edit = runProjectWrite(client, 'p', async () => {
      await gate;
      client.setQueryData(['site-zones', 'p'], [edited]);
    });
    const save = saveAutomaticParkGround(client, 'p', zone, profile);
    release();
    await edit;
    expect(await save).toBe(false);
    expect(siteZonesApi.update).not.toHaveBeenCalled();
    expect(client.getQueryData(['site-zones', 'p'])).toEqual([edited]);
  });
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
  it('retains a newer cache revision when an already submitted ground write returns', async () => {
    const client = new QueryClient();
    client.setQueryData(['site-zones', 'p'], [zone]);
    const newer = { ...zone, updated_at: 'r3', properties: { name: 'newer edit' } };
    vi.mocked(siteZonesApi.update).mockImplementationOnce(async () => {
      client.setQueryData(['site-zones', 'p'], [newer]);
      return { ...zone, updated_at: 'r2' };
    });
    expect(await saveAutomaticParkGround(client, 'p', zone, profile)).toBe(true);
    expect(client.getQueryData(['site-zones', 'p'])).toEqual([newer]);
  });
});
