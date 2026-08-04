import { useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { siteZonesApi } from '@/services/api';
import { isPersistedZoneId } from '@/utils/zoneIdentity';
import type { SiteZone, SiteZoneType, SiteZoneProperties } from '@/types';
import { ZONE_TYPE_CONFIG } from '@/types';
import { useViewerStore } from '@/store';
import { useUndoRedoStore } from '@/store/undoRedo';
import {
  createZoneCreateAction,
  createZoneDeleteAction,
  createZoneUpdateAction,
  createZoneCoordinatesAction,
} from '@/store/undoActions';

export function useSiteZones(projectId: string | undefined) {
  const queryClient = useQueryClient();
  const { selectZone } = useViewerStore();

  const { data: siteZones = [], isLoading: siteZonesLoading } = useQuery({
    queryKey: ['site-zones', projectId],
    queryFn: () => siteZonesApi.list(projectId!),
    enabled: !!projectId,
  });

  const createZone = useMutation({
    mutationFn: (vars: { coordinates: number[][]; zone_type: SiteZoneType; properties?: SiteZoneProperties }) =>
      siteZonesApi.create(projectId!, {
        zone_type: vars.zone_type,
        coordinates: vars.coordinates,
        color: ZONE_TYPE_CONFIG[vars.zone_type].color,
        properties: vars.properties ?? ZONE_TYPE_CONFIG[vars.zone_type].defaultProperties,
        is_active_boundary: vars.zone_type === 'site_boundary',
      }),
    onMutate: async (vars) => {
      // Cancel outgoing refetches so they don't overwrite optimistic update
      await queryClient.cancelQueries({ queryKey: ['site-zones', projectId] });
      const previous = queryClient.getQueryData<SiteZone[]>(['site-zones', projectId]);
      // Optimistic zone so the map renders it immediately
      const optimistic: SiteZone = {
        id: `temp-${Date.now()}`,
        project_id: projectId!,
        zone_type: vars.zone_type,
        coordinates: vars.coordinates,
        color: ZONE_TYPE_CONFIG[vars.zone_type].color,
        properties: vars.properties ?? ZONE_TYPE_CONFIG[vars.zone_type].defaultProperties,
        sort_order: (previous?.length ?? 0),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      queryClient.setQueryData<SiteZone[]>(['site-zones', projectId], (old) => [...(old ?? []), optimistic]);
      return { previous };
    },
    onSuccess: async (createdZone) => {
      queryClient.invalidateQueries({ queryKey: ['site-zones', projectId] });
      toast.success('Zone created');
      // Push undo action (skip if this was triggered by undo/redo system)
      if (!useUndoRedoStore.getState()._isSystemAction && projectId) {
        useUndoRedoStore.getState().pushAction(
          createZoneCreateAction(projectId, createdZone, queryClient),
        );
      }
      // Boundary creation already fetches context atomically on the backend.
      // Reuse that response instead of issuing a duplicate Overpass request.
      if (createdZone.zone_type === 'site_boundary') {
        const ctx = createdZone.properties?._osm_context;
        if (ctx) {
          const { setOSMContext } = useViewerStore.getState();
          setOSMContext(ctx);
          const total = ctx.buildings.length + ctx.roads.length + ctx.water.length + ctx.parks.length;
          toast.success(`Site ready with ${total} nearby context features`);
        }
      }
    },
    onError: (err: Error, _vars, context) => {
      // Roll back to previous state on failure
      if (context?.previous) {
        queryClient.setQueryData(['site-zones', projectId], context.previous);
      }
      toast.error(`Failed to create zone: ${err.message}`);
    },
  });

  const updateZone = useMutation({
    mutationFn: (vars: { zoneId: string; data: { name?: string; color?: string; properties?: SiteZoneProperties }; previousData?: { name?: string; color?: string; properties?: SiteZoneProperties } }) =>
      siteZonesApi.update(vars.zoneId, vars.data),
    onSuccess: async (_result, vars) => {
      // Await refetch so the cache is fresh before the user can click away
      await queryClient.refetchQueries({ queryKey: ['site-zones', projectId] });
      toast.success('Zone updated');
      // Push undo action
      if (!useUndoRedoStore.getState()._isSystemAction && projectId && vars.previousData) {
        useUndoRedoStore.getState().pushAction(
          createZoneUpdateAction(projectId, vars.zoneId, vars.previousData, vars.data, queryClient),
        );
      }
    },
    onError: (err: Error) => {
      toast.error(`Failed to update zone: ${err.message}`);
    },
  });

  const deleteZone = useMutation({
    // Unsaved optimistic zones (temp- id, create still in flight) don't exist
    // server-side — the endpoint 422s on non-UUID ids. Resolve locally; the
    // onSuccess invalidate drops the optimistic entry from the cache. (If the
    // in-flight create lands afterwards the zone reappears persisted — rare
    // sub-second race, and it can then be deleted normally.)
    mutationFn: (zoneId: string) =>
      isPersistedZoneId(zoneId) ? siteZonesApi.delete(zoneId) : Promise.resolve(),
    onMutate: (zoneId) => {
      // Capture zone snapshot before deletion for undo
      const zones = queryClient.getQueryData<SiteZone[]>(['site-zones', projectId]);
      const deletedZone = zones?.find((z) => z.id === zoneId);
      return { deletedZone };
    },
    onSuccess: (_data, _zoneId, context) => {
      queryClient.invalidateQueries({ queryKey: ['site-zones', projectId] });
      selectZone(null);
      toast.success('Zone deleted');
      // Push undo action
      if (!useUndoRedoStore.getState()._isSystemAction && projectId && context?.deletedZone) {
        useUndoRedoStore.getState().pushAction(
          createZoneDeleteAction(projectId, context.deletedZone, queryClient),
        );
      }
    },
    onError: (err: Error) => {
      toast.error(`Failed to delete zone: ${err.message}`);
    },
  });

  const handleZoneCreated = useCallback((coordinates: number[][], zoneType: SiteZoneType, properties?: SiteZoneProperties) => {
    const toolProps = properties ?? useViewerStore.getState().activeToolProperties;
    createZone.mutate({ coordinates, zone_type: zoneType, properties: toolProps ?? undefined });
  }, [createZone]);

  const handleZoneUpdated = useCallback((zoneId: string, coordinates: number[][]) => {
    // Unsaved optimistic zones (temp- id, create still in flight) can't be
    // updated server-side — the endpoint 422s on non-UUID ids, and this used
    // to surface as an uncaught promise rejection. Update the cache only so
    // the drag doesn't visually snap back; the next refetch reconciles.
    if (!isPersistedZoneId(zoneId)) {
      queryClient.setQueryData<SiteZone[]>(['site-zones', projectId], (old) =>
        (old ?? []).map((z) => (z.id === zoneId ? { ...z, coordinates } : z)));
      return;
    }

    // Capture previous coordinates from cache before updating
    const zones = queryClient.getQueryData<SiteZone[]>(['site-zones', projectId]);
    const prevZone = zones?.find((z) => z.id === zoneId);
    const prevCoords = prevZone?.coordinates;

    siteZonesApi.update(zoneId, { coordinates }).then(() => {
      queryClient.invalidateQueries({ queryKey: ['site-zones', projectId] });
      // Push undo action for coordinate change
      if (!useUndoRedoStore.getState()._isSystemAction && projectId && prevCoords) {
        useUndoRedoStore.getState().pushAction(
          createZoneCoordinatesAction(projectId, zoneId, prevCoords, coordinates, queryClient),
        );
      }
    }).catch((err: Error) => {
      toast.error(`Failed to update zone geometry: ${err.message}`);
    });
  }, [queryClient, projectId]);

  return {
    siteZones,
    siteZonesLoading,
    createZone,
    updateZone,
    deleteZone,
    handleZoneCreated,
    handleZoneUpdated,
  };
}
