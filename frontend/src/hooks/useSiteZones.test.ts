import { describe, it, expect, vi, beforeEach } from 'vitest';
import React from 'react';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useSiteZones } from './useSiteZones';
import { siteZonesApi } from '@/services/api';
import type { SiteZone } from '@/types';

vi.mock('@/services/api', () => ({
  siteZonesApi: {
    list: vi.fn().mockResolvedValue([]),
    create: vi.fn(),
    update: vi.fn().mockResolvedValue({}),
    delete: vi.fn().mockResolvedValue(undefined),
    fetchContext: vi.fn(),
  },
}));

vi.mock('react-hot-toast', () => ({
  default: { success: vi.fn(), error: vi.fn() },
}));

const PROJECT_ID = 'b1bb189e-8bf9-3888-9912-ace4e6543111';
const REAL_ZONE_ID = 'a3bb189e-8bf9-3888-9912-ace4e6543002';
const TEMP_ZONE_ID = 'temp-1751900000000';

function makeZone(id: string): SiteZone {
  return {
    id,
    project_id: PROJECT_ID,
    zone_type: 'site_boundary',
    coordinates: [[0, 0], [0, 1], [1, 1]],
    color: '#ff0000',
    properties: {},
    is_active_boundary: true,
    sort_order: 0,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  } as SiteZone;
}

describe('useSiteZones temp-id guards', () => {
  let queryClient: QueryClient;

  const wrapper = ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);

  beforeEach(() => {
    vi.clearAllMocks();
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
    });
  });

  it('handleZoneUpdated skips the API for temp ids and updates the cache only', () => {
    queryClient.setQueryData(['site-zones', PROJECT_ID], [makeZone(TEMP_ZONE_ID)]);
    const { result } = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });

    const newCoords = [[2, 2], [2, 3], [3, 3]];
    result.current.handleZoneUpdated(TEMP_ZONE_ID, newCoords);

    expect(siteZonesApi.update).not.toHaveBeenCalled();
    const cached = queryClient.getQueryData<SiteZone[]>(['site-zones', PROJECT_ID]);
    expect(cached?.[0].coordinates).toEqual(newCoords);
  });

  it('handleZoneUpdated calls the API for persisted ids', async () => {
    queryClient.setQueryData(['site-zones', PROJECT_ID], [makeZone(REAL_ZONE_ID)]);
    const { result } = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });

    const newCoords = [[2, 2], [2, 3], [3, 3]];
    result.current.handleZoneUpdated(REAL_ZONE_ID, newCoords);

    await waitFor(() => {
      expect(siteZonesApi.update).toHaveBeenCalledWith(REAL_ZONE_ID, { coordinates: newCoords });
    });
  });

  it('deleteZone skips the API for temp ids', async () => {
    queryClient.setQueryData(['site-zones', PROJECT_ID], [makeZone(TEMP_ZONE_ID)]);
    const { result } = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });

    result.current.deleteZone.mutate(TEMP_ZONE_ID);

    await waitFor(() => {
      expect(result.current.deleteZone.isSuccess).toBe(true);
    });
    expect(siteZonesApi.delete).not.toHaveBeenCalled();
  });

  it('deleteZone calls the API for persisted ids', async () => {
    queryClient.setQueryData(['site-zones', PROJECT_ID], [makeZone(REAL_ZONE_ID)]);
    const { result } = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });

    result.current.deleteZone.mutate(REAL_ZONE_ID);

    await waitFor(() => {
      expect(siteZonesApi.delete).toHaveBeenCalledWith(REAL_ZONE_ID);
    });
  });

  it('loads boundary context independently after the boundary is saved', async () => {
    const context = {
      buildings: [],
      roads: [],
      water: [],
      parks: [],
      fetched_at: '2026-08-03T00:00:00Z',
      buffer_m: 50,
    };
    vi.mocked(siteZonesApi.create).mockResolvedValue(makeZone(REAL_ZONE_ID));
    vi.mocked(siteZonesApi.fetchContext).mockResolvedValue(context);
    const { result } = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });

    result.current.createZone.mutate({
      zone_type: 'site_boundary',
      coordinates: [[0, 0], [0, 1], [1, 1]],
    });

    await waitFor(() => expect(result.current.createZone.isSuccess).toBe(true));
    await waitFor(() => expect(siteZonesApi.fetchContext).toHaveBeenCalledWith(REAL_ZONE_ID));
  });

  it('reuses boundary context returned by create instead of fetching it twice', async () => {
    const context = {
      buildings: [],
      roads: [],
      water: [],
      parks: [],
      fetched_at: '2026-08-03T00:00:00Z',
      buffer_m: 50,
    };
    vi.mocked(siteZonesApi.create).mockResolvedValue({
      ...makeZone(REAL_ZONE_ID),
      properties: { _osm_context: context },
    });
    const { result } = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });

    result.current.createZone.mutate({
      zone_type: 'site_boundary',
      coordinates: [[0, 0], [0, 1], [1, 1]],
    });

    await waitFor(() => expect(result.current.createZone.isSuccess).toBe(true));
    expect(siteZonesApi.fetchContext).not.toHaveBeenCalled();
  });
});
