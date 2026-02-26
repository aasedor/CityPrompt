import { useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { siteZonesApi } from '@/services/api';
import type { SiteZoneType, SiteZoneProperties } from '@/types';
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
    mutationFn: (vars: { coordinates: number[][]; zone_type: SiteZoneType }) =>
      siteZonesApi.create(projectId!, {
        zone_type: vars.zone_type,
        coordinates: vars.coordinates,
        color: ZONE_TYPE_CONFIG[vars.zone_type].color,
        properties: ZONE_TYPE_CONFIG[vars.zone_type].defaultProperties,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['site-zones', projectId] });
      toast.success('Zone created');
    },
    onError: (err: Error) => {
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

  const handleZoneCreated = useCallback((coordinates: number[][], zoneType: SiteZoneType) => {
    createZone.mutate({ coordinates, zone_type: zoneType });
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
