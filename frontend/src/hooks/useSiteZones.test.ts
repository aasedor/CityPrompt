import { describe, it, expect, vi, beforeEach } from 'vitest';
import React from 'react';
import { act, renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useSiteZones } from './useSiteZones';
import { siteZonesApi } from '@/services/api';
import type { SiteZone } from '@/types';
import { useViewerStore } from '@/store';
import { useUndoRedoStore } from '@/store/undoRedo';
import toast from 'react-hot-toast';

vi.mock('@/services/api', () => ({
  getApiErrorMessage: (error: Error) => error.message,
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
const OUTSIDE_SITE_DETAIL = 'The new zone must stay completely inside the active site boundary.';

function outsideSiteRejection() {
  return Object.assign(new Error(OUTSIDE_SITE_DETAIL), { response: { status: 409, data: { detail: OUTSIDE_SITE_DETAIL } } });
}

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

describe('useSiteZones', () => {
  let queryClient: QueryClient;

  const wrapper = ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    useUndoRedoStore.getState().setProjectScope(null);
    useUndoRedoStore.getState().clearHistory();
    vi.mocked(siteZonesApi.list).mockImplementation(() => new Promise(() => {}));
    vi.mocked(siteZonesApi.update).mockImplementation(async (id) => makeZone(id));
    vi.mocked(siteZonesApi.delete).mockResolvedValue(undefined);
    useViewerStore.setState({
      selectedZoneId: null,
      activeSitePlannerTool: 'site_boundary',
    });
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
    const zone = makeZone(REAL_ZONE_ID);
    queryClient.setQueryData(['site-zones', PROJECT_ID], [zone]);
    const { result } = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });

    const newCoords = [[2, 2], [2, 3], [3, 3]];
    result.current.handleZoneUpdated(REAL_ZONE_ID, newCoords);

    await waitFor(() => {
      expect(siteZonesApi.update).toHaveBeenCalledWith(REAL_ZONE_ID, { coordinates: newCoords, expected_updated_at: zone.updated_at });
    });
  });

  it('explains a boundary rejection without claiming another session changed the drawing', async () => {
    queryClient.setQueryData(['site-zones', PROJECT_ID], [makeZone(REAL_ZONE_ID)]);
    const detail = 'The updated zone must stay completely inside the active site boundary.';
    vi.mocked(siteZonesApi.update).mockRejectedValueOnce(Object.assign(new Error(detail), {
      response: { status: 409, data: { detail } },
    }));
    const { result } = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });
    act(() => result.current.handleZoneUpdated(REAL_ZONE_ID, [[2,2],[2,3],[3,3]]));
    await waitFor(() => expect(toast.error).toHaveBeenCalledWith(detail));
    expect(vi.mocked(toast.error).mock.calls.every(([message]) => !String(message).includes('newer saved version'))).toBe(true);
  });

  it('reconciles a persisted ghost zone after an update returns 404', async () => {
    queryClient.setQueryData(['site-zones', PROJECT_ID], [makeZone(REAL_ZONE_ID)]);
    useViewerStore.setState({ selectedZoneId: REAL_ZONE_ID });
    vi.mocked(siteZonesApi.list)
      .mockImplementationOnce(() => new Promise(() => {}))
      .mockResolvedValueOnce([]);
    vi.mocked(siteZonesApi.update).mockRejectedValueOnce(Object.assign(
      new Error('Request failed with status code 404'),
      { response: { status: 404 } },
    ));
    const { result } = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });

    result.current.updateZone.mutate({
      zoneId: REAL_ZONE_ID,
      data: { name: 'Basketball Court' },
    });

    await waitFor(() => expect(result.current.updateZone.isError).toBe(true));
    await waitFor(() => expect(useViewerStore.getState().selectedZoneId).toBeNull());
    expect(queryClient.getQueryData<SiteZone[]>(['site-zones', PROJECT_ID])).toEqual([]);
    expect(toast.error).toHaveBeenCalledWith(
      'This zone no longer exists on the server. The plan was refreshed; draw it again.',
    );
  });

  it('keeps an unsaved drawing until its save has been reconciled', async () => {
    queryClient.setQueryData(['site-zones', PROJECT_ID], [makeZone(TEMP_ZONE_ID)]);
    const { result } = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });

    result.current.deleteZone.mutate(TEMP_ZONE_ID);

    await waitFor(() => {
      expect(result.current.deleteZone.isError).toBe(true);
    });
    expect(siteZonesApi.delete).not.toHaveBeenCalled();
    expect(queryClient.getQueryData<SiteZone[]>(['site-zones', PROJECT_ID])?.[0].id).toBe(TEMP_ZONE_ID);
  });

  it('deleteZone calls the API for persisted ids', async () => {
    const zone = makeZone(REAL_ZONE_ID);
    queryClient.setQueryData(['site-zones', PROJECT_ID], [zone]);
    const { result } = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });

    result.current.deleteZone.mutate(REAL_ZONE_ID);

    await waitFor(() => {
      expect(siteZonesApi.delete).toHaveBeenCalledWith(REAL_ZONE_ID, zone.updated_at);
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

  it('reconciles the saved boundary and opens its Site DNA panel', async () => {
    const context = {
      buildings: [],
      roads: [],
      water: [],
      parks: [],
      fetched_at: '2026-08-03T00:00:00Z',
      buffer_m: 50,
    };
    vi.mocked(siteZonesApi.list).mockImplementation(() => new Promise(() => {}));
    vi.mocked(siteZonesApi.create).mockResolvedValue(makeZone(REAL_ZONE_ID));
    vi.mocked(siteZonesApi.fetchContext).mockResolvedValue(context);
    const { result } = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });

    result.current.createZone.mutate({
      zone_type: 'site_boundary',
      coordinates: [[0, 0], [0, 1], [1, 1]],
    });

    await waitFor(() => expect(result.current.createZone.isSuccess).toBe(true));
    expect(useViewerStore.getState().activeSitePlannerTool).toBeNull();
    expect(useViewerStore.getState().selectedZoneId).toBe(REAL_ZONE_ID);
    expect(queryClient.getQueryData<SiteZone[]>(['site-zones', PROJECT_ID])).toEqual([
      expect.objectContaining({ id: REAL_ZONE_ID, zone_type: 'site_boundary' }),
    ]);
  });

  it.each([true, false])('advances undo only for our context source revision (matches=%s)', async matches => {
    const created = {...makeZone(REAL_ZONE_ID), updated_at: 'created'};
    const context = {buildings: [], roads: [], water: [], parks: [], fetched_at: '', buffer_m: 50,
      zone_id: REAL_ZONE_ID, source_updated_at: matches ? 'created' : 'teammate', updated_at: 'enriched'};
    vi.mocked(siteZonesApi.create).mockResolvedValue(created);
    vi.mocked(siteZonesApi.fetchContext).mockResolvedValue(context);
    const {result} = renderHook(() => useSiteZones(PROJECT_ID), {wrapper});
    act(() => result.current.createZone.mutate({zone_type:'site_boundary',coordinates:created.coordinates}));
    await waitFor(() => expect(useViewerStore.getState().osmContext).toEqual(context));
    expect(useUndoRedoStore.getState().undoStack).toHaveLength(1);
    vi.spyOn(queryClient, 'invalidateQueries').mockResolvedValue(undefined);
    await act(() => useUndoRedoStore.getState().undo());
    expect(siteZonesApi.delete).toHaveBeenCalledWith(REAL_ZONE_ID, matches ? 'enriched' : 'created', {skipHistory:true});
    if (matches) {
      await act(() => useUndoRedoStore.getState().redo());
      expect(siteZonesApi.create).toHaveBeenLastCalledWith(PROJECT_ID,
        expect.objectContaining({coordinates:created.coordinates,properties:expect.objectContaining({_osm_context:context})}), {skipHistory:true});
    }
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

  it('retains a failed drawing across remount and retries with the same request ID', async () => {
    const coordinates = [[-114.1, 51.0], [-114.1, 51.001], [-114.099, 51.001]];
    vi.mocked(siteZonesApi.create).mockRejectedValueOnce(new Error('Connection lost'));
    const first = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });
    act(() => first.result.current.createZone.mutate({ zone_type: 'green_space', coordinates }));
    await waitFor(() => expect(first.result.current.pendingDrafts[0]?.error).toBe('Connection lost'));
    const requestId = first.result.current.pendingDrafts[0].requestId;
    first.unmount();

    const reopened = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });
    expect(reopened.result.current.siteZones[0].coordinates).toEqual(coordinates);
    expect(reopened.result.current.pendingDrafts[0].requestId).toBe(requestId);
    vi.mocked(siteZonesApi.create).mockResolvedValueOnce({ ...makeZone(REAL_ZONE_ID), zone_type: 'green_space', coordinates });
    act(() => reopened.result.current.retryDraft(reopened.result.current.pendingDrafts[0]));
    await waitFor(() => expect(reopened.result.current.pendingDrafts).toHaveLength(0));
    expect(siteZonesApi.create).toHaveBeenNthCalledWith(2, PROJECT_ID, expect.objectContaining({ client_request_id: requestId, coordinates }));
    expect(reopened.result.current.siteZones.filter((zone) => zone.id === REAL_ZONE_ID)).toHaveLength(1);
  });

  it('does not show drafts from a different project', async () => {
    vi.mocked(siteZonesApi.create).mockRejectedValueOnce(new Error('Offline'));
    const first = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });
    act(() => first.result.current.createZone.mutate({ zone_type: 'green_space', coordinates: [[0, 0], [0, 1], [1, 1]] }));
    await waitFor(() => expect(first.result.current.pendingDrafts).toHaveLength(1));
    first.unmount();
    const other = renderHook(() => useSiteZones('another-project'), { wrapper });
    expect(other.result.current.pendingDrafts).toHaveLength(0);
  });

  it.each([400, 422])('keeps a %s rejection until explicitly discarded, including after remount', async (status) => {
    vi.mocked(siteZonesApi.create).mockRejectedValueOnce(Object.assign(new Error('Invalid drawing'), { response: { status } }));
    const first = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });
    act(() => first.result.current.createZone.mutate({ zone_type: 'green_space', coordinates: [[0, 0], [0, 1], [1, 1]] }));
    await waitFor(() => expect(first.result.current.discardableDrafts).toHaveLength(1));
    expect(first.result.current.pendingDrafts[0].rejectionStatus).toBe(status);
    first.unmount();

    const reopened = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });
    const draft = reopened.result.current.discardableDrafts[0];
    expect(draft.rejectionStatus).toBe(status);
    act(() => { expect(reopened.result.current.discardDraft(draft)).toBe(true); });
    expect(reopened.result.current.pendingDrafts).toHaveLength(0);
    expect(reopened.result.current.siteZones).toHaveLength(0);
    expect(siteZonesApi.delete).not.toHaveBeenCalled();
  });

  it.each([401, 403, 500, undefined])('protects a draft with an uncertain or non-validation failure (%s)', async (status) => {
    vi.mocked(siteZonesApi.create).mockRejectedValueOnce(Object.assign(new Error('Save failed'), { response: status ? { status } : undefined }));
    const { result } = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });
    act(() => result.current.createZone.mutate({ zone_type: 'green_space', coordinates: [[0, 0], [0, 1], [1, 1]] }));
    await waitFor(() => expect(result.current.pendingDrafts[0]?.error).toBe('Save failed'));
    expect(result.current.discardableDrafts).toHaveLength(0);
    // A stale or forged caller snapshot cannot override the stored outcome.
    act(() => { expect(result.current.discardDraft({ ...result.current.pendingDrafts[0], rejectionStatus: 400 })).toBe(false); });
    expect(result.current.pendingDrafts).toHaveLength(1);
  });

  it('lets the explicit delete action discard a definitively rejected temp drawing locally', async () => {
    vi.mocked(siteZonesApi.create).mockRejectedValueOnce(Object.assign(new Error('Invalid drawing'), { response: { status: 422 } }));
    const { result } = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });
    act(() => result.current.createZone.mutate({ zone_type: 'green_space', coordinates: [[0, 0], [0, 1], [1, 1]] }));
    await waitFor(() => expect(result.current.discardableDrafts).toHaveLength(1));
    const tempId = `temp-${result.current.discardableDrafts[0].requestId}`;
    act(() => { useViewerStore.setState({ selectedZoneId: tempId }); result.current.deleteZone.mutate(tempId); });
    await waitFor(() => expect(result.current.deleteZone.isSuccess).toBe(true));
    expect(result.current.pendingDrafts).toHaveLength(0);
    expect(useViewerStore.getState().selectedZoneId).toBeNull();
    expect(siteZonesApi.delete).not.toHaveBeenCalled();
    expect(toast.success).toHaveBeenCalledWith('Rejected drawing discarded');
  });

  it('allows discarding a boundary rejected for excluding an existing building without deleting server work', async () => {
    const detail = 'The site boundary must contain every authored zone. Outside the proposed boundary: Tower.';
    vi.mocked(siteZonesApi.create).mockRejectedValueOnce(Object.assign(new Error(detail), {response:{status:409,data:{detail}}}));
    const {result} = renderHook(() => useSiteZones(PROJECT_ID), {wrapper});
    act(() => result.current.createZone.mutate({zone_type:'site_boundary',coordinates:[[0,0],[0,1],[1,1]]}));
    await waitFor(() => expect(result.current.discardableDrafts).toHaveLength(1));
    const draft = result.current.discardableDrafts[0];
    expect(draft.rejectionReason).toBe('boundary_excludes_zones');
    act(() => { expect(result.current.discardDraft(draft)).toBe(true); });
    expect(result.current.pendingDrafts).toHaveLength(0);
    expect(siteZonesApi.delete).not.toHaveBeenCalled();
  });

  it('discards a confirmed outside-site create locally after remount while preserving saved zones', async () => {
    const savedZone = makeZone(REAL_ZONE_ID);
    queryClient.setQueryData(['site-zones', PROJECT_ID], [savedZone]);
    vi.mocked(siteZonesApi.create).mockRejectedValueOnce(outsideSiteRejection());
    const first = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });
    act(() => first.result.current.createZone.mutate({ zone_type: 'green_space', coordinates: [[2, 2], [2, 3], [3, 3]] }));
    await waitFor(() => expect(first.result.current.discardableDrafts).toHaveLength(1));
    expect(first.result.current.pendingDrafts[0]).toMatchObject({ rejectionStatus: 409, rejectionReason: 'outside_site_boundary' });
    first.unmount();

    const reopened = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });
    const tempId = `temp-${reopened.result.current.discardableDrafts[0].requestId}`;
    act(() => { useViewerStore.setState({ selectedZoneId: tempId }); reopened.result.current.deleteZone.mutate(tempId); });
    await waitFor(() => expect(reopened.result.current.deleteZone.isSuccess).toBe(true));
    expect(reopened.result.current.pendingDrafts).toHaveLength(0);
    expect(reopened.result.current.siteZones).toEqual([savedZone]);
    expect(useViewerStore.getState().selectedZoneId).toBeNull();
    expect(siteZonesApi.delete).not.toHaveBeenCalled();
    expect(toast.success).toHaveBeenCalledWith('Rejected drawing discarded');
  });

  it.each([undefined, 'This zone changed after you loaded it. Refresh before applying your edit.', 'This save request ID was used for a different zone'])(
    'preserves a create draft on an unrecognized or existing-work 409 (%s)', async (detail) => {
      vi.mocked(siteZonesApi.create).mockRejectedValueOnce(Object.assign(new Error('Save conflict'), { response: { status: 409, data: { detail } } }));
      const { result } = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });
      act(() => result.current.createZone.mutate({ zone_type: 'green_space', coordinates: [[0, 0], [0, 1], [1, 1]] }));
      await waitFor(() => expect(result.current.createZone.isError).toBe(true));
      expect(result.current.discardableDrafts).toHaveLength(0);
      const draft = result.current.pendingDrafts[0];
      act(() => { expect(result.current.discardDraft({ ...draft, rejectionStatus: 409, rejectionReason: 'outside_site_boundary' })).toBe(false); });
      act(() => result.current.deleteZone.mutate(`temp-${draft.requestId}`));
      await waitFor(() => expect(result.current.deleteZone.isError).toBe(true));
      expect(result.current.pendingDrafts).toHaveLength(1);
      expect(siteZonesApi.delete).not.toHaveBeenCalled();
    });

  it('requires a verified response before discarding a legacy or network-error draft with outside-site text', async () => {
    vi.mocked(siteZonesApi.create).mockRejectedValueOnce(new Error(OUTSIDE_SITE_DETAIL)).mockRejectedValueOnce(outsideSiteRejection());
    const { result } = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });
    act(() => result.current.createZone.mutate({ zone_type: 'green_space', coordinates: [[2, 2], [2, 3], [3, 3]] }));
    await waitFor(() => expect(result.current.pendingDrafts[0]?.error).toBe(OUTSIDE_SITE_DETAIL));
    expect(result.current.discardableDrafts).toHaveLength(0);
    const draft = result.current.pendingDrafts[0];
    act(() => { expect(result.current.discardDraft(draft)).toBe(false); result.current.retryDraft(draft); });
    await waitFor(() => expect(result.current.discardableDrafts).toHaveLength(1));
    expect(siteZonesApi.create).toHaveBeenNthCalledWith(2, PROJECT_ID, expect.objectContaining({ client_request_id: draft.requestId }));
    act(() => { expect(result.current.discardDraft(result.current.discardableDrafts[0])).toBe(true); });
    expect(result.current.pendingDrafts).toHaveLength(0);
  });

  it('keeps persisted-zone revision conflicts on the server reconciliation path', async () => {
    const zone = makeZone(REAL_ZONE_ID);
    queryClient.setQueryData(['site-zones', PROJECT_ID], [zone]);
    vi.mocked(siteZonesApi.list).mockResolvedValue([zone]);
    const conflict = Object.assign(new Error('Drawing changed'), { response: { status: 409 } });
    vi.mocked(siteZonesApi.update).mockRejectedValueOnce(conflict);
    vi.mocked(siteZonesApi.delete).mockRejectedValueOnce(conflict);
    const { result } = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });
    act(() => result.current.updateZone.mutate({ zoneId: REAL_ZONE_ID, data: { name: 'Rejected edit' } }));
    await waitFor(() => expect(result.current.updateZone.isError).toBe(true));
    expect(result.current.saveError).toContain('Drawing changed');
    act(() => result.current.deleteZone.mutate(REAL_ZONE_ID));
    await waitFor(() => expect(result.current.deleteZone.isError).toBe(true));
    expect(siteZonesApi.delete).toHaveBeenCalledWith(REAL_ZONE_ID, zone.updated_at);
    expect(result.current.siteZones).toEqual([zone]);
    expect(result.current.discardableDrafts).toHaveLength(0);
    expect(toast.error).toHaveBeenCalledWith('This drawing has a newer saved version. Review it before deleting.');
  });

  it.each([400, 409])('revokes discard permission before retrying a %s rejection and preserves a lost-response retry', async (status) => {
    let failRetry!: (error: Error) => void;
    vi.mocked(siteZonesApi.create)
      .mockRejectedValueOnce(status === 409 ? outsideSiteRejection() : Object.assign(new Error('Invalid drawing'), { response: { status: 400 } }))
      .mockImplementationOnce(() => new Promise((_resolve, reject) => { failRetry = reject; }));
    const { result } = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });
    act(() => result.current.createZone.mutate({ zone_type: 'green_space', coordinates: [[0, 0], [0, 1], [1, 1]] }));
    await waitFor(() => expect(result.current.discardableDrafts).toHaveLength(1));
    const staleDraft = result.current.discardableDrafts[0];
    act(() => result.current.retryDraft(staleDraft));
    await waitFor(() => expect(result.current.isSaving).toBe(true));
    expect(result.current.discardableDrafts).toHaveLength(0);
    act(() => { expect(result.current.discardDraft(staleDraft)).toBe(false); });
    await act(async () => failRetry(new Error('Connection lost')));
    await waitFor(() => expect(result.current.pendingDrafts[0]?.error).toBe('Connection lost'));
    expect(result.current.pendingDrafts[0].requestId).toBe(staleDraft.requestId);
    expect(result.current.discardableDrafts).toHaveLength(0);
  });

  it('shows saving while a geometry move is awaiting the server', async () => {
    const zone = makeZone(REAL_ZONE_ID);
    queryClient.setQueryData(['site-zones', PROJECT_ID], [zone]);
    let complete!: (value: SiteZone) => void;
    vi.mocked(siteZonesApi.update).mockImplementationOnce(() => new Promise((resolve) => { complete = resolve; }));
    const { result } = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });
    act(() => result.current.handleZoneUpdated(REAL_ZONE_ID, [[2, 2], [2, 3], [3, 3]]));
    await waitFor(() => expect(result.current.isSaving).toBe(true));
    await act(async () => complete(zone));
    await waitFor(() => expect(result.current.isSaving).toBe(false));
  });

  it('keeps a failed property edit visible until that drawing saves successfully', async () => {
    const zone = makeZone(REAL_ZONE_ID);
    queryClient.setQueryData(['site-zones', PROJECT_ID], [zone]);
    vi.mocked(siteZonesApi.list).mockResolvedValue([zone]);
    vi.mocked(siteZonesApi.update).mockRejectedValueOnce(new Error('Offline'));
    const { result } = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });
    act(() => result.current.updateZone.mutate({ zoneId: REAL_ZONE_ID, data: { name: 'Library' } }));
    await waitFor(() => expect(result.current.saveError).toContain('Offline'));
    expect(result.current.isSaving).toBe(false);
    expect(result.current.pendingDrafts).toHaveLength(0);
    act(() => result.current.updateZone.mutate({ zoneId: REAL_ZONE_ID, data: { name: 'Library' } }));
    await waitFor(() => expect(result.current.updateZone.isSuccess).toBe(true));
    expect(result.current.saveError).toBeNull();
  });

  it('clears failed geometry only after an explicit successful reload, not a failed reload', async () => {
    const zone = makeZone(REAL_ZONE_ID);
    queryClient.setQueryData(['site-zones', PROJECT_ID], [zone]);
    vi.mocked(siteZonesApi.list).mockResolvedValue([zone]);
    vi.mocked(siteZonesApi.update).mockRejectedValueOnce(new Error('Move was not saved'));
    const { result } = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });
    await waitFor(() => expect(queryClient.isFetching()).toBe(0));
    act(() => result.current.handleZoneUpdated(REAL_ZONE_ID, [[2, 2], [2, 3], [3, 3]]));
    await waitFor(() => expect(result.current.saveError).toContain('Move was not saved'));
    vi.mocked(siteZonesApi.list).mockRejectedValueOnce(new Error('Reload failed'));
    await act(async () => { await result.current.reloadZones(); });
    expect(result.current.saveError).toContain('Move was not saved');
    await act(async () => { await result.current.reloadZones(); });
    expect(result.current.saveError).toBeNull();
  });

  it('does not clear another drawing failure when an unrelated drawing saves', async () => {
    const otherId = 'a3bb189e-8bf9-3888-9912-ace4e6543003';
    const zones = [makeZone(REAL_ZONE_ID), makeZone(otherId)];
    queryClient.setQueryData(['site-zones', PROJECT_ID], zones);
    vi.mocked(siteZonesApi.list).mockResolvedValue(zones);
    vi.mocked(siteZonesApi.update).mockRejectedValueOnce(new Error('First drawing failed'));
    const { result } = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });
    act(() => result.current.handleZoneUpdated(REAL_ZONE_ID, [[2, 2], [2, 3], [3, 3]]));
    await waitFor(() => expect(result.current.saveError).toContain('First drawing failed'));
    act(() => result.current.updateZone.mutate({ zoneId: otherId, data: { name: 'Park' } }));
    await waitFor(() => expect(result.current.updateZone.isSuccess).toBe(true));
    expect(result.current.saveError).toContain('First drawing failed');
  });

  it('serializes edits and retains the newest failure after an older success', async () => {
    let completeOld!: (zone: SiteZone) => void;
    const zone = makeZone(REAL_ZONE_ID);
    queryClient.setQueryData(['site-zones', PROJECT_ID], [zone]);
    vi.mocked(siteZonesApi.list).mockResolvedValue([zone]);
    vi.mocked(siteZonesApi.update)
      .mockImplementationOnce(() => new Promise((resolve) => { completeOld = resolve; }))
      .mockRejectedValueOnce(new Error('Latest edit failed'));
    const { result } = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });
    act(() => result.current.updateZone.mutate({ zoneId: REAL_ZONE_ID, data: { name: 'Old name' } }));
    await waitFor(() => expect(siteZonesApi.update).toHaveBeenCalledTimes(1));
    act(() => result.current.updateZone.mutate({ zoneId: REAL_ZONE_ID, data: { name: 'New name' } }));
    expect(siteZonesApi.update).toHaveBeenCalledTimes(1);
    await act(async () => completeOld({ ...zone, name: 'Old name' }));
    await waitFor(() => expect(result.current.saveError).toContain('Latest edit failed'));
    expect(result.current.saveError).toContain('Latest edit failed');
  });

  it('clears displayed errors on project navigation and ignores a late failure from the previous project', async () => {
    let failLate!: (error: Error) => void;
    const zone = makeZone(REAL_ZONE_ID);
    queryClient.setQueryData(['site-zones', PROJECT_ID], [zone]);
    vi.mocked(siteZonesApi.list).mockResolvedValue([zone]);
    vi.mocked(siteZonesApi.update).mockRejectedValueOnce(new Error('First error'))
      .mockImplementationOnce(() => new Promise((_resolve, reject) => { failLate = reject; }));
    const { result, rerender } = renderHook(({ projectId }) => useSiteZones(projectId), { wrapper, initialProps: { projectId: PROJECT_ID } });
    act(() => result.current.handleZoneUpdated(REAL_ZONE_ID, [[2, 2], [2, 3], [3, 3]]));
    await waitFor(() => expect(result.current.saveError).toContain('First error'));
    act(() => result.current.handleZoneUpdated(REAL_ZONE_ID, [[4, 4], [4, 5], [5, 5]]));
    await waitFor(() => expect(result.current.isSaving).toBe(true));
    rerender({ projectId: 'next-project' });
    expect(result.current.saveError).toBeNull();
    await act(async () => failLate(new Error('Late error')));
    expect(result.current.saveError).toBeNull();
  });

  it('records a successful authored drawing even while an independent undo is in progress', async () => {
    vi.mocked(siteZonesApi.create).mockResolvedValueOnce({ ...makeZone(REAL_ZONE_ID), zone_type: 'green_space' });
    const { result } = renderHook(() => useSiteZones(PROJECT_ID), { wrapper });
    useUndoRedoStore.setState({ _isSystemAction: true });
    act(() => result.current.createZone.mutate({ zone_type: 'green_space', coordinates: [[0, 0], [0, 1], [1, 1]] }));
    await waitFor(() => expect(result.current.createZone.isSuccess).toBe(true));
    expect(useUndoRedoStore.getState().undoStack).toHaveLength(1);
    expect(useUndoRedoStore.getState().undoStack[0].projectId).toBe(PROJECT_ID);
  });

  it('does not promise device persistence when browser storage is blocked', async () => {
    const storage = vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => { throw new Error('Quota exceeded'); });
    vi.mocked(siteZonesApi.create).mockRejectedValueOnce(new Error('Offline'));
    try {
      const { result } = renderHook(() => useSiteZones('storage-blocked-project'), { wrapper });
      act(() => result.current.createZone.mutate({ zone_type: 'green_space', coordinates: [[0, 0], [0, 1], [1, 1]] }));
      await waitFor(() => expect(result.current.pendingDrafts[0]?.error).toBe('Offline'));
      expect(result.current.draftsPersistOnDevice).toBe(false);
      expect(toast.error).toHaveBeenCalledWith(expect.stringContaining('kept in this tab'));
    } finally { storage.mockRestore(); }
  });
});


describe('project write coordination', () => {
  it('waits for a derived revision before moving, then deletes with the move revision', async () => {
    const { runProjectWrite } = await import('@/utils/projectWriteQueue');
    const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
    const zone = { ...makeZone(REAL_ZONE_ID), updated_at: 'r1' };
    client.setQueryData(['site-zones', PROJECT_ID], [zone]);
    vi.mocked(siteZonesApi.list).mockImplementation(() => new Promise(() => {}));
    vi.mocked(siteZonesApi.update).mockReset().mockResolvedValue({ ...zone, updated_at: 'r3' });
    vi.mocked(siteZonesApi.delete).mockReset().mockResolvedValue(undefined);
    let release!: () => void;
    const compiling = runProjectWrite(client, PROJECT_ID, async () => {
      await new Promise<void>(resolve => { release = resolve; });
      client.setQueryData(['site-zones', PROJECT_ID], [{ ...zone, updated_at: 'r2' }]);
    });
    const wrapper = ({children}: {children:React.ReactNode}) => React.createElement(QueryClientProvider, {client}, children);
    const {result} = renderHook(() => useSiteZones(PROJECT_ID), {wrapper});
    await act(async () => { await Promise.resolve(); });
    act(() => result.current.handleZoneUpdated(REAL_ZONE_ID, [[2,2],[2,3],[3,3]]));
    expect(siteZonesApi.update).not.toHaveBeenCalled();
    await act(async () => { release(); await compiling; });
    await waitFor(() => expect(siteZonesApi.update).toHaveBeenCalledWith(REAL_ZONE_ID, expect.objectContaining({expected_updated_at:'r2'})));
    await act(async () => { await result.current.deleteZone.mutateAsync(REAL_ZONE_ID); });
    expect(siteZonesApi.delete).toHaveBeenCalledWith(REAL_ZONE_ID, 'r3');
    expect(client.getQueryData(['site-zones', PROJECT_ID])).toEqual([]);
  });

  it('reconciles a delete 404 only after the project confirms the drawing is absent', async () => {
    const client = new QueryClient({defaultOptions:{queries:{retry:false},mutations:{retry:false}}});
    client.setQueryData(['site-zones', PROJECT_ID], [makeZone(REAL_ZONE_ID)]);
    vi.mocked(siteZonesApi.list).mockReset().mockImplementationOnce(() => new Promise(() => {})).mockResolvedValue([]);
    vi.mocked(siteZonesApi.delete).mockReset().mockRejectedValue({response:{status:404}});
    const wrapper = ({children}: {children:React.ReactNode}) => React.createElement(QueryClientProvider, {client}, children);
    const {result} = renderHook(() => useSiteZones(PROJECT_ID), {wrapper});
    await act(async () => { await result.current.deleteZone.mutateAsync(REAL_ZONE_ID); });
    expect(client.getQueryData(['site-zones', PROJECT_ID])).toEqual([]);
    expect(result.current.deleteZone.isSuccess).toBe(true);
  });
});
