import { beforeEach, describe, expect, it, vi } from 'vitest';
import { QueryClient } from '@tanstack/react-query';
import { siteZonesApi } from '@/services/api';
import { createZoneUpdateAction, createZoneCreateAction, createZoneDeleteAction, createZoneCoordinatesAction } from './undoActions';
import type { SiteZone } from '@/types';

vi.mock('@/services/api', () => ({ siteZonesApi: { create: vi.fn(), update: vi.fn(), delete: vi.fn() }, buildingsApi: {} }));
describe('zone undo revision checks', () => {
  beforeEach(() => vi.clearAllMocks());
  it('follows revisions produced by successive local undos', async () => {
    const client = new QueryClient();
    const first = createZoneUpdateAction('project', 'zone', { name: 'A' }, { name: 'B' }, client, 'r2');
    const second = createZoneUpdateAction('project', 'zone', { name: 'B' }, { name: 'C' }, client, 'r3');
    vi.mocked(siteZonesApi.update).mockResolvedValueOnce({ updated_at: 'r4' } as SiteZone).mockResolvedValueOnce({ updated_at: 'r5' } as SiteZone);
    await second.undo();
    await first.undo();
    expect(siteZonesApi.update).toHaveBeenNthCalledWith(1, 'zone', { name: 'B', expected_updated_at: 'r3' }, { skipHistory: true });
    expect(siteZonesApi.update).toHaveBeenNthCalledWith(2, 'zone', { name: 'A', expected_updated_at: 'r4' }, { skipHistory: true });
  });
  it('does not adopt a teammate revision from a background refetch', async () => {
    const client = new QueryClient();
    const action = createZoneUpdateAction('project', 'zone', { name: 'A' }, { name: 'B' }, client, 'ours');
    client.setQueryData(['site-zones', 'project'], [{ id: 'zone', updated_at: 'teammate' }]);
    vi.mocked(siteZonesApi.update).mockRejectedValueOnce(new Error('Conflict'));
    await expect(action.undo()).rejects.toThrow('Conflict');
    expect(siteZonesApi.update).toHaveBeenCalledWith('zone', { name: 'A', expected_updated_at: 'ours' }, { skipHistory: true });
  });
  it('checks the saved revision before undoing a creation by deletion', async () => {
    const action = createZoneCreateAction('project', { id: 'zone', updated_at: 'created' } as SiteZone, new QueryClient());
    await action.undo();
    expect(siteZonesApi.delete).toHaveBeenCalledWith('zone', 'created', { skipHistory: true });
  });

  it.each(['create', 'delete'] as const)('keeps %s undo and redo history suppression on each request', async (kind) => {
    const original = { id: 'zone', updated_at: 'r1' } as SiteZone;
    const client = new QueryClient();
    const action = kind === 'create'
      ? createZoneCreateAction('project', original, client)
      : createZoneDeleteAction('project', original, client);
    vi.mocked(siteZonesApi.create).mockResolvedValue({ id: 'recreated', updated_at: 'r2' } as SiteZone);
    await action.undo();
    await action.redo();
    expect(siteZonesApi.create).toHaveBeenCalledWith('project', expect.any(Object), { skipHistory: true });
    expect(siteZonesApi.delete).toHaveBeenCalledWith(expect.any(String), expect.any(String), { skipHistory: true });
  });

  it('keeps coordinate undo/redo revisions and request history options together', async () => {
    const action = createZoneCoordinatesAction('project', 'zone', [[1, 2]], [[3, 4]], new QueryClient(), 'r1');
    vi.mocked(siteZonesApi.update).mockResolvedValueOnce({ updated_at: 'r2' } as SiteZone).mockResolvedValueOnce({ updated_at: 'r3' } as SiteZone);
    await action.undo();
    await action.redo();
    expect(siteZonesApi.update).toHaveBeenNthCalledWith(1, 'zone', { coordinates: [[1, 2]], expected_updated_at: 'r1' }, { skipHistory: true });
    expect(siteZonesApi.update).toHaveBeenNthCalledWith(2, 'zone', { coordinates: [[3, 4]], expected_updated_at: 'r2' }, { skipHistory: true });
  });
});
