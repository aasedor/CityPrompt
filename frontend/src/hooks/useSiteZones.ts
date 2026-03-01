import { useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { siteZonesApi } from '@/services/api';
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

  const { data: siteZones = [] } = useQuery({
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
      // Auto-fetch OSM context when a site_boundary is created
      if (createdZone.zone_type === 'site_boundary') {
        try {
          const ctx = await siteZonesApi.fetchContext(createdZone.id);
          const { setOSMContext } = useViewerStore.getState();
          setOSMContext(ctx);
          const total = ctx.buildings.length + ctx.roads.length + ctx.water.length + ctx.parks.length;
          toast.success(`Fetched ${total} OSM features (${ctx.buildings.length} buildings, ${ctx.roads.length} roads)`);
          queryClient.invalidateQueries({ queryKey: ['site-zones', projectId] });
        } catch (e) {
          console.warn('Failed to auto-fetch OSM context:', e);
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
    mutationFn: (vars: { zoneId: string; data: { name?: string; properties?: SiteZoneProperties }; previousData?: { name?: string; properties?: SiteZoneProperties } }) =>
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
    mutationFn: (zoneId: string) => siteZonesApi.delete(zoneId),
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
    });
  }, [queryClient, projectId]);

  return {
    siteZones,
    createZone,
    updateZone,
    deleteZone,
    handleZoneCreated,
    handleZoneUpdated,
  };
}
