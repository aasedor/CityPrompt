import type { QueryClient } from '@tanstack/react-query';
import { siteZonesApi, buildingsApi } from '@/services/api';
import type { SiteZone, SiteZoneProperties } from '@/types';
import { ZONE_TYPE_CONFIG } from '@/types';
import type { UndoableAction } from './undoRedo';

// =============================================================================
// Helpers
// =============================================================================

/** Mutable ID reference — handles server reassigning IDs after delete+recreate */
interface IdRef {
  current: string;
}

function invalidateZones(queryClient: QueryClient, projectId: string) {
  queryClient.invalidateQueries({ queryKey: ['site-zones', projectId] });
}

function invalidateProject(queryClient: QueryClient, projectId: string) {
  queryClient.invalidateQueries({ queryKey: ['project', projectId] });
}

// =============================================================================
// Zone Actions
// =============================================================================

export function createZoneCreateAction(
  projectId: string,
  createdZone: SiteZone,
  queryClient: QueryClient,
): UndoableAction {
  const idRef: IdRef = { current: createdZone.id };

  return {
    label: 'Create zone',
    undo: async () => {
      await siteZonesApi.delete(idRef.current);
      invalidateZones(queryClient, projectId);
    },
    redo: async () => {
      const zone = await siteZonesApi.create(projectId, {
        name: createdZone.name,
        zone_type: createdZone.zone_type,
        coordinates: createdZone.coordinates,
        color: createdZone.color,
        properties: createdZone.properties,
        sort_order: createdZone.sort_order,
      });
      idRef.current = zone.id;
      invalidateZones(queryClient, projectId);
    },
  };
}

export function createZoneDeleteAction(
  projectId: string,
  deletedZone: SiteZone,
  queryClient: QueryClient,
): UndoableAction {
  const idRef: IdRef = { current: deletedZone.id };

  return {
    label: 'Delete zone',
    undo: async () => {
      const zone = await siteZonesApi.create(projectId, {
        name: deletedZone.name,
        zone_type: deletedZone.zone_type,
        coordinates: deletedZone.coordinates,
        color: deletedZone.color,
        properties: deletedZone.properties,
        sort_order: deletedZone.sort_order,
      });
      idRef.current = zone.id;
      invalidateZones(queryClient, projectId);
    },
    redo: async () => {
      await siteZonesApi.delete(idRef.current);
      invalidateZones(queryClient, projectId);
    },
  };
}

export function createZoneUpdateAction(
  projectId: string,
  zoneId: string,
  prevData: { name?: string; properties?: SiteZoneProperties },
  newData: { name?: string; properties?: SiteZoneProperties },
  queryClient: QueryClient,
): UndoableAction {
  return {
    label: 'Update zone',
    undo: async () => {
      await siteZonesApi.update(zoneId, prevData);
      invalidateZones(queryClient, projectId);
    },
    redo: async () => {
      await siteZonesApi.update(zoneId, newData);
      invalidateZones(queryClient, projectId);
    },
  };
}

export function createZoneCoordinatesAction(
  projectId: string,
  zoneId: string,
  prevCoords: number[][],
  newCoords: number[][],
  queryClient: QueryClient,
): UndoableAction {
  return {
    label: 'Move zone',
    undo: async () => {
      await siteZonesApi.update(zoneId, { coordinates: prevCoords });
      invalidateZones(queryClient, projectId);
    },
    redo: async () => {
      await siteZonesApi.update(zoneId, { coordinates: newCoords });
      invalidateZones(queryClient, projectId);
    },
  };
}

// =============================================================================
// Building Actions
// =============================================================================

export interface BuildingSnapshot {
  id: string;
  name?: string;
  height_meters?: number;
  floor_count?: number;
  floor_height_meters?: number;
  roof_type?: string;
  construction_phase?: number;
  footprint_coordinates?: number[][];
  rotation_degrees?: number;
  specifications?: Record<string, unknown>;
  architectural_style?: string;
}

export function createBuildingDeleteAction(
  projectId: string,
  building: BuildingSnapshot,
  queryClient: QueryClient,
): UndoableAction {
  const idRef: IdRef = { current: building.id };

  return {
    label: 'Delete building',
    undo: async () => {
      const created = await buildingsApi.create(projectId, {
        name: building.name,
        height_meters: building.height_meters,
        floor_count: building.floor_count,
        floor_height_meters: building.floor_height_meters,
        roof_type: building.roof_type,
        construction_phase: building.construction_phase,
        footprint_coordinates: building.footprint_coordinates,
        specifications: building.specifications,
      });
      idRef.current = created.id;
      invalidateProject(queryClient, projectId);
    },
    redo: async () => {
      await buildingsApi.delete(idRef.current);
      invalidateProject(queryClient, projectId);
    },
  };
}

export function createBuildingUpdateAction(
  projectId: string,
  buildingId: string,
  prevData: Record<string, unknown>,
  newData: Record<string, unknown>,
  label: string,
  queryClient: QueryClient,
): UndoableAction {
  return {
    label,
    undo: async () => {
      await buildingsApi.update(buildingId, prevData);
      invalidateProject(queryClient, projectId);
    },
    redo: async () => {
      await buildingsApi.update(buildingId, newData);
      invalidateProject(queryClient, projectId);
    },
  };
}

// Convenience wrappers

export function createBuildingMoveAction(
  projectId: string,
  buildingId: string,
  prevCoords: number[][],
  newCoords: number[][],
  queryClient: QueryClient,
): UndoableAction {
  return createBuildingUpdateAction(
    projectId,
    buildingId,
    { footprint_coordinates: prevCoords },
    { footprint_coordinates: newCoords },
    'Move building',
    queryClient,
  );
}

export function createBuildingRotationAction(
  projectId: string,
  buildingId: string,
  prevDeg: number,
  newDeg: number,
  queryClient: QueryClient,
): UndoableAction {
  return createBuildingUpdateAction(
    projectId,
    buildingId,
    { rotation_degrees: prevDeg },
    { rotation_degrees: newDeg },
    'Rotate building',
    queryClient,
  );
}

export function createBuildingMaterialAction(
  projectId: string,
  buildingId: string,
  prevSpecs: Record<string, unknown> | undefined,
  newSpecs: Record<string, unknown>,
  queryClient: QueryClient,
): UndoableAction {
  return createBuildingUpdateAction(
    projectId,
    buildingId,
    { specifications: prevSpecs ?? {} },
    { specifications: newSpecs },
    'Change material',
    queryClient,
  );
}
