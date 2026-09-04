import { useCallback, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { useQuery, useMutation, useQueryClient, useIsMutating } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { getApiErrorMessage, siteZonesApi } from '@/services/api';
import { isPersistedZoneId } from '@/utils/zoneIdentity';
import type { SiteZone, SiteZoneType, SiteZoneProperties } from '@/types';
import { ZONE_TYPE_CONFIG } from '@/types';
import { useViewerStore, useAuthStore } from '@/store';
import { draftToZone, isDiscardableDraft, useZoneDrafts, type ZoneDraft } from './zoneDrafts';
import { useUndoRedoStore } from '@/store/undoRedo';
import {
  createZoneCreateAction,
  createZoneDeleteAction,
  createZoneUpdateAction,
  createZoneCoordinatesAction,
} from '@/store/undoActions';

function apiStatus(error: unknown): number | undefined {
  return (error as { response?: { status?: number } } | undefined)?.response?.status;
}

function createRejection(error: unknown): Pick<ZoneDraft, 'rejectionStatus' | 'rejectionReason'> {
  const status = apiStatus(error);
  if (status === 400 || status === 422) return { rejectionStatus: status };
  const detail = (error as { response?: { data?: { detail?: unknown } } } | undefined)?.response?.data?.detail;
  // This exact create guard runs before insertion and after request-ID lookup.
  // Other 409s can refer to already-saved work and must remain protected.
  if (status === 409 && detail === 'The new zone must stay completely inside the active site boundary.') {
    return { rejectionStatus: 409, rejectionReason: 'outside_site_boundary' };
  }
  return {};
}

export function useSiteZones(projectId: string | undefined) {
  const queryClient = useQueryClient();
  const { selectZone } = useViewerStore();
  const userId = useAuthStore((state) => state.user?.id);
  const currentProject = useRef(projectId);
  const editOrder = useRef(0);
  const latestEdits = useRef(new Map<string, number>());
  const [failedEdits, setFailedEdits] = useState<Record<string, string>>({});
  const beginEdit = useCallback((zoneId: string) => {
    const attempt = ++editOrder.current;
    latestEdits.current.set(zoneId, attempt);
    return attempt;
  }, []);
  const recordFailedEdit = useCallback((zoneId: string, error: unknown, attempt?: number) => {
    if (currentProject.current !== projectId
        || (attempt !== undefined && latestEdits.current.get(zoneId) !== attempt)) return;
    setFailedEdits((previous) => ({ ...previous, [zoneId]: getApiErrorMessage(error) }));
  }, [projectId]);
  const clearFailedEdit = useCallback((zoneId?: string, attempt?: number) => {
    if (currentProject.current !== projectId
        || (zoneId && attempt !== undefined && latestEdits.current.get(zoneId) !== attempt)) return;
    setFailedEdits((previous) => zoneId
      ? Object.fromEntries(Object.entries(previous).filter(([id]) => id !== zoneId)) : {});
  }, [projectId]);
  const failedMessages = Object.values(failedEdits);
  const saveError = failedMessages.length
    ? `${failedMessages.length === 1 ? 'A drawing change was' : `${failedMessages.length} drawing changes were`} not saved. ${failedMessages[0]}`
    : null;
  const { drafts, upsertDraft, removeDraft, discardRejectedDraft, draftsPersistOnDevice } = useZoneDrafts(projectId, userId);
  const discardableDrafts = useMemo(() => drafts.filter(isDiscardableDraft), [drafts]);
  const discardDraft = useCallback((draft: ZoneDraft): boolean => {
    const discarded = discardRejectedDraft(draft.requestId);
    if (discarded && useViewerStore.getState().selectedZoneId === `temp-${draft.requestId}`
        && useUndoRedoStore.getState().projectId === projectId) selectZone(null);
    return discarded;
  }, [discardRejectedDraft, projectId, selectZone]);
  useLayoutEffect(() => {
    currentProject.current = projectId;
    latestEdits.current.clear();
    setFailedEdits({});
    useUndoRedoStore.getState().setProjectScope(projectId ?? null);
    selectZone(null);
  }, [projectId, selectZone]);
  const isSaving = useIsMutating({ mutationKey: ['save-zone', projectId] }) > 0;

  const { data: savedZones = [], isLoading: siteZonesLoading, error: siteZonesError, refetch: refetchZones } = useQuery({
    queryKey: ['site-zones', projectId],
    queryFn: () => siteZonesApi.list(projectId!),
    enabled: !!projectId,
  });
  const reloadZones = useCallback(async () => {
    const result = await refetchZones();
    if (!result.error && result.status === 'success') clearFailedEdit();
    return result;
  }, [refetchZones, clearFailedEdit]);

  const siteZones = useMemo(() => {
    const savedRequests = new Set(savedZones.map((zone) => zone.properties?._client_request_id));
    return [...savedZones, ...drafts.filter((draft) => !savedRequests.has(draft.requestId))
      .map((draft) => draftToZone(draft, projectId ?? ''))];
  }, [savedZones, drafts, projectId]);

  const createZone = useMutation({
    mutationKey: ['save-zone', projectId],
    mutationFn: (vars: { coordinates: number[][]; zone_type: SiteZoneType; properties?: SiteZoneProperties; requestId?: string; createdAt?: string }) =>
      siteZonesApi.create(projectId!, {
        client_request_id: vars.requestId,
        zone_type: vars.zone_type,
        coordinates: vars.coordinates,
        color: ZONE_TYPE_CONFIG[vars.zone_type].color,
        properties: vars.properties ?? ZONE_TYPE_CONFIG[vars.zone_type].defaultProperties,
        is_active_boundary: vars.zone_type === 'site_boundary',
      }),
    onMutate: (vars) => {
      // Assign once before the first network request. A lost response and its
      // retry carry the same ID, so the server cannot create two drawings.
      vars.requestId ??= crypto.randomUUID();
      vars.createdAt ??= new Date().toISOString();
      const draft: ZoneDraft = {
        requestId: vars.requestId, createdAt: vars.createdAt,
        coordinates: vars.coordinates, zoneType: vars.zone_type,
        properties: vars.properties,
      };
      upsertDraft(draft);
      return { draft, optimisticId: `temp-${vars.requestId}` };
    },
    onSuccess: (createdZone, _vars, context) => {
      if (context?.draft) removeDraft(context.draft.requestId);
      // Replace the exact optimistic polygon with the authoritative response
      // before refetching. This removes the temp-id gap so selection-dependent
      // panels can open as soon as the create request succeeds.
      queryClient.setQueryData<SiteZone[]>(['site-zones', projectId], (old) => {
        const withoutOptimistic = (old ?? []).filter((zone) => zone.id !== context?.optimisticId);
        return [...withoutOptimistic.filter((zone) => zone.id !== createdZone.id), createdZone];
      });
      void queryClient.invalidateQueries({ queryKey: ['site-zones', projectId] });
      if (useUndoRedoStore.getState().projectId !== projectId) return;
      toast.success('Drawing saved');
      // Undo/redo calls the API directly. Every successful authored mutation
      // in this hook retains its own undo action, even during another undo.
      if (projectId) {
        useUndoRedoStore.getState().pushAction(
          createZoneCreateAction(projectId, createdZone, queryClient),
        );
      }
      if (createdZone.zone_type === 'site_boundary') {
        // A project can have only one active boundary. Leave drawing mode and
        // hand the user directly into the boundary-owned Site DNA panel.
        const viewer = useViewerStore.getState();
        viewer.setActiveSitePlannerTool(null);
        viewer.selectZone(createdZone.id);
        const ctx = createdZone.properties?._osm_context;
        if (ctx) {
          viewer.setOSMContext(ctx);
          const total = ctx.buildings.length + ctx.roads.length + ctx.water.length + ctx.parks.length;
          toast.success(`Site ready with ${total} nearby context features`);
          return;
        }

        // The boundary is authoritative as soon as create returns. Enrich it
        // independently so a slow or unavailable Overpass service cannot leave
        // the user waiting or tempt them to submit a duplicate boundary.
        toast.success('Site boundary saved. Loading surrounding context…');
        void siteZonesApi.fetchContext(createdZone.id).then((context) => {
          if (useUndoRedoStore.getState().projectId !== projectId) return;
          const { setOSMContext } = useViewerStore.getState();
          setOSMContext(context);
          void queryClient.invalidateQueries({ queryKey: ['site-zones', projectId] });
          const total = context.buildings.length + context.roads.length + context.water.length + context.parks.length;
          toast.success(`Site ready with ${total} nearby context features`);
        }).catch((error: unknown) => {
          const message = getApiErrorMessage(error, 'context service unavailable');
          toast.error(`Site boundary saved, but surrounding context could not load: ${message}`);
        });
      }
    },
    onError: (error: unknown, _vars, context) => {
      const message = getApiErrorMessage(error);
      const persisted = context?.draft && upsertDraft({ ...context.draft, error: message,
        ...createRejection(error),
      });
      toast.error(persisted ? `Drawing kept on this device. Save again when ready: ${message}`
        : `Drawing kept in this tab. Keep it open and save again: ${message}`);
    },
  });

  const updateZone = useMutation({
    mutationKey: ['save-zone', projectId],
    onMutate: (vars) => beginEdit(vars.zoneId),
    mutationFn: (vars: { zoneId: string; data: { name?: string; color?: string; properties?: SiteZoneProperties }; previousData?: { name?: string; color?: string; properties?: SiteZoneProperties } }) =>
      siteZonesApi.update(vars.zoneId, {
        ...vars.data,
        expected_updated_at: queryClient.getQueryData<SiteZone[]>(['site-zones', projectId])
          ?.find((zone) => zone.id === vars.zoneId)?.updated_at,
      }),
    onSuccess: async (result, vars, attempt) => {
      clearFailedEdit(vars.zoneId, attempt);
      // Await refetch so the cache is fresh before the user can click away
      await queryClient.refetchQueries({ queryKey: ['site-zones', projectId] });
      toast.success('Zone updated');
      // Push undo action
      if (projectId && currentProject.current === projectId && vars.previousData) {
        useUndoRedoStore.getState().pushAction(
          createZoneUpdateAction(projectId, vars.zoneId, vars.previousData, vars.data, queryClient, result.updated_at),
        );
      }
    },
    onError: async (err: unknown, vars, attempt) => {
      recordFailedEdit(vars.zoneId, err, attempt);
      if (apiStatus(err) === 409) {
        await queryClient.refetchQueries({ queryKey: ['site-zones', projectId] });
        toast.error('This drawing changed in another session. Review the latest version before applying your change again.');
        return;
      }
      if (apiStatus(err) === 404) {
        // A backend restart or another tab can invalidate a cached polygon.
        // Reconcile immediately instead of leaving a selectable ghost zone
        // that will block Generate to 3D forever.
        await queryClient.refetchQueries({ queryKey: ['site-zones', projectId] });
        selectZone(null);
        toast.error('This zone no longer exists on the server. The plan was refreshed; draw it again.');
        return;
      }
      toast.error(`Failed to update zone: ${getApiErrorMessage(err)}`);
    },
  });

  const deleteZone = useMutation({
    mutationKey: ['save-zone', projectId],
    // Keep an unsaved drawing until its in-flight request has been reconciled.
    // Silently removing it could make a successful delayed save reappear.
    mutationFn: async (zoneId: string) => {
      if (isPersistedZoneId(zoneId)) {
        await siteZonesApi.delete(zoneId, savedZones.find((zone) => zone.id === zoneId)?.updated_at);
        return 'deleted';
      }
      const draft = drafts.find((item) => `temp-${item.requestId}` === zoneId);
      if (draft && discardDraft(draft)) return 'discarded';
      throw new Error('Save this drawing before deleting it. Your draft is kept on this device.');
    },
    onMutate: (zoneId) => {
      // Capture zone snapshot before deletion for undo
      const zones = queryClient.getQueryData<SiteZone[]>(['site-zones', projectId]);
      const deletedZone = zones?.find((z) => z.id === zoneId);
      return { deletedZone };
    },
    onSuccess: (outcome, zoneId, context) => {
      clearFailedEdit(zoneId);
      queryClient.invalidateQueries({ queryKey: ['site-zones', projectId] });
      if (useUndoRedoStore.getState().projectId === projectId) selectZone(null);
      toast.success(outcome === 'discarded' ? 'Rejected drawing discarded' : 'Zone deleted');
      // Push undo action
      if (outcome === 'deleted' && projectId && currentProject.current === projectId && context?.deletedZone) {
        useUndoRedoStore.getState().pushAction(
          createZoneDeleteAction(projectId, context.deletedZone, queryClient),
        );
      }
    },
    onError: async (err: Error) => {
      if (apiStatus(err) === 409) {
        await queryClient.refetchQueries({ queryKey: ['site-zones', projectId] });
        toast.error('This drawing changed in another session. Review it before deleting.');
        return;
      }
      toast.error(`Failed to delete zone: ${getApiErrorMessage(err)}`);
    },
  });

  const handleZoneCreated = useCallback((coordinates: number[][], zoneType: SiteZoneType, properties?: SiteZoneProperties) => {
    const toolProps = properties ?? useViewerStore.getState().activeToolProperties;
    createZone.mutate({ coordinates, zone_type: zoneType, properties: toolProps ?? undefined });
  }, [createZone]);

  const coordinateUpdate = useMutation({
    mutationKey: ['save-zone', projectId],
    onMutate: (vars) => beginEdit(vars.zoneId),
    mutationFn: (vars: { zoneId: string; coordinates: number[][]; revision?: string }) =>
      siteZonesApi.update(vars.zoneId, { coordinates: vars.coordinates,
        ...(vars.revision ? { expected_updated_at: vars.revision } : {}) }),
    onSuccess: (_result, vars, attempt) => clearFailedEdit(vars.zoneId, attempt),
    onError: (error, vars, attempt) => recordFailedEdit(vars.zoneId, error, attempt),
  });
  const updateCoordinates = coordinateUpdate.mutateAsync;
  const handleZoneUpdated = useCallback((zoneId: string, coordinates: number[][]) => {
    // Unsaved optimistic zones (temp- id, create still in flight) can't be
    // updated server-side — the endpoint 422s on non-UUID ids, and this used
    // to surface as an uncaught promise rejection. Update the cache only so
    // the drag doesn't visually snap back; the next refetch reconciles.
    if (!isPersistedZoneId(zoneId)) {
      if (drafts.some((draft) => `temp-${draft.requestId}` === zoneId)) {
        toast.error('Save this drawing before moving it. Your draft is kept on this device.');
        return;
      }
      queryClient.setQueryData<SiteZone[]>(['site-zones', projectId], (old) =>
        (old ?? []).map((z) => (z.id === zoneId ? { ...z, coordinates } : z)));
      return;
    }

    // Capture previous coordinates from cache before updating
    const zones = queryClient.getQueryData<SiteZone[]>(['site-zones', projectId]);
    const prevZone = zones?.find((z) => z.id === zoneId);
    const prevCoords = prevZone?.coordinates;

    updateCoordinates({ zoneId, coordinates, revision: prevZone?.updated_at }).then((result) => {
      queryClient.invalidateQueries({ queryKey: ['site-zones', projectId] });
      // Push undo action for coordinate change
      if (projectId && currentProject.current === projectId && prevCoords) {
        useUndoRedoStore.getState().pushAction(
          createZoneCoordinatesAction(projectId, zoneId, prevCoords, coordinates, queryClient, result.updated_at),
        );
      }
    }).catch(async (err: unknown) => {
      if (apiStatus(err) === 409) {
        await queryClient.refetchQueries({ queryKey: ['site-zones', projectId] });
        toast.error('This drawing changed in another session. Review the latest shape before moving it again.');
        return;
      }
      if (apiStatus(err) === 404) {
        await queryClient.refetchQueries({ queryKey: ['site-zones', projectId] });
        selectZone(null);
        toast.error('This zone no longer exists on the server. The plan was refreshed; draw it again.');
        return;
      }
      toast.error(`Failed to update zone geometry: ${getApiErrorMessage(err)}`);
    });
  }, [queryClient, projectId, selectZone, drafts, updateCoordinates]);

  const retryDraft = (draft: ZoneDraft) => createZone.mutate({
    requestId: draft.requestId, createdAt: draft.createdAt, coordinates: draft.coordinates,
    zone_type: draft.zoneType, properties: draft.properties,
  });

  return {
    siteZones,
    siteZonesError,
    reloadZones,
    pendingDrafts: drafts,
    discardableDrafts,
    discardDraft,
    draftsPersistOnDevice,
    retryDraft,
    isSaving,
    saveError,
    siteZonesLoading,
    createZone,
    updateZone,
    deleteZone,
    handleZoneCreated,
    handleZoneUpdated,
  };
}
