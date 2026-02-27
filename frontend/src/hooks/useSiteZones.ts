import { useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { siteZonesApi } from '@/services/api';
import type { SiteZone, SiteZoneType, SiteZoneProperties } from '@/types';
import { ZONE_TYPE_CONFIG } from '@/types';
import { useViewerStore } from '@/store';

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
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['site-zones', projectId] });
      toast.success('Zone created');
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
    mutationFn: (vars: { zoneId: string; data: { name?: string; properties?: SiteZoneProperties } }) =>
      siteZonesApi.update(vars.zoneId, vars.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['site-zones', projectId] });
      toast.success('Zone updated');
    },
    onError: (err: Error) => {
      toast.error(`Failed to update zone: ${err.message}`);
    },
  });

  const deleteZone = useMutation({
    mutationFn: (zoneId: string) => siteZonesApi.delete(zoneId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['site-zones', projectId] });
      selectZone(null);
      toast.success('Zone deleted');
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
    siteZonesApi.update(zoneId, { coordinates }).then(() => {
      queryClient.invalidateQueries({ queryKey: ['site-zones', projectId] });
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
