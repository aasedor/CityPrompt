import type { QueryClient } from '@tanstack/react-query';
import { siteZonesApi, buildingsApi } from '@/services/api';
import type { SiteZone, SiteZoneProperties } from '@/types';
import type { UndoableAction } from './undoRedo';

// =============================================================================
// Helpers
// =============================================================================

/** Mutable ID reference — handles server reassigning IDs after delete+recreate */
interface IdRef {
  current: string;
  revision?: string;
}

// Track only revisions produced by this tab's own actions. Reading the newest
// query cache here would silently accept a teammate's intervening edit. Sharing
// this reference also allows several consecutive local edits to be undone.
const localRevisions = new WeakMap<QueryClient, Map<string, string>>();
function rememberRevision(client: QueryClient, projectId: string, zoneId: string, revision?: string) {
  if (!revision) return;
  let revisions = localRevisions.get(client);
  if (!revisions) { revisions = new Map(); localRevisions.set(client, revisions); }
  revisions.set(`${projectId}:${zoneId}`, revision);
}
function currentRevision(client: QueryClient, projectId: string, zoneId: string, fallback?: string) {
  return localRevisions.get(client)?.get(`${projectId}:${zoneId}`) ?? fallback;
}

function invalidateZones(queryClient: QueryClient, projectId: string) {
  return queryClient.invalidateQueries({ queryKey: ['site-zones', projectId] });
}

function invalidateProject(queryClient: QueryClient, projectId: string) {
  return queryClient.invalidateQueries({ queryKey: ['project', projectId] });
}

// =============================================================================
// Zone Actions
// =============================================================================

export function createZoneCreateAction(
  projectId: string,
  createdZone: SiteZone,
  queryClient: QueryClient,
): UndoableAction {
  const originalZoneId = createdZone.id;
  const idRef: IdRef = { current: createdZone.id, revision: createdZone.updated_at };
  rememberRevision(queryClient, projectId, createdZone.id, createdZone.updated_at);

  return {
    projectId,
    label: 'Create zone',
    getZoneId: () => idRef.current,
    matchesZoneId: (zoneId) => zoneId === originalZoneId || zoneId === idRef.current,
    undo: async () => {
      await siteZonesApi.delete(idRef.current, currentRevision(queryClient, projectId, idRef.current, idRef.revision), { skipHistory: true });
      await invalidateZones(queryClient, projectId);
    },
    redo: async () => {
      const zone = await siteZonesApi.create(projectId, {
        name: createdZone.name,
        zone_type: createdZone.zone_type,
        coordinates: createdZone.coordinates,
        color: createdZone.color,
        properties: createdZone.properties,
        sort_order: createdZone.sort_order,
      }, { skipHistory: true });
      idRef.current = zone.id;
      idRef.revision = zone.updated_at;
      rememberRevision(queryClient, projectId, zone.id, zone.updated_at);
      await invalidateZones(queryClient, projectId);
    },
  };
}

export function createZoneDeleteAction(
  projectId: string,
  deletedZone: SiteZone,
  queryClient: QueryClient,
): UndoableAction {
  const originalZoneId = deletedZone.id;
  const idRef: IdRef = { current: deletedZone.id, revision: deletedZone.updated_at };

  return {
    projectId,
    label: 'Delete zone',
    getZoneId: () => idRef.current,
    matchesZoneId: (zoneId) => zoneId === originalZoneId || zoneId === idRef.current,
    undo: async () => {
      const zone = await siteZonesApi.create(projectId, {
        name: deletedZone.name,
        zone_type: deletedZone.zone_type,
        coordinates: deletedZone.coordinates,
        color: deletedZone.color,
        properties: deletedZone.properties,
        sort_order: deletedZone.sort_order,
      }, { skipHistory: true });
      idRef.current = zone.id;
      idRef.revision = zone.updated_at;
      rememberRevision(queryClient, projectId, zone.id, zone.updated_at);
      await invalidateZones(queryClient, projectId);
    },
    redo: async () => {
      await siteZonesApi.delete(idRef.current, currentRevision(queryClient, projectId, idRef.current, idRef.revision), { skipHistory: true });
      await invalidateZones(queryClient, projectId);
    },
  };
}

export function createZoneUpdateAction(
  projectId: string,
  zoneId: string,
  prevData: { name?: string; color?: string; properties?: SiteZoneProperties },
  newData: { name?: string; color?: string; properties?: SiteZoneProperties },
  queryClient: QueryClient,
  savedRevision?: string,
): UndoableAction {
  let revision = savedRevision;
  rememberRevision(queryClient, projectId, zoneId, revision);
  return {
    projectId,
    label: 'Update zone',
    zoneId,
    undo: async () => {
      const zone = await siteZonesApi.update(zoneId, { ...prevData, expected_updated_at: currentRevision(queryClient, projectId, zoneId, revision) }, { skipHistory: true });
      revision = zone.updated_at;
      rememberRevision(queryClient, projectId, zoneId, revision);
      await invalidateZones(queryClient, projectId);
    },
    redo: async () => {
      const zone = await siteZonesApi.update(zoneId, { ...newData, expected_updated_at: currentRevision(queryClient, projectId, zoneId, revision) }, { skipHistory: true });
      revision = zone.updated_at;
      rememberRevision(queryClient, projectId, zoneId, revision);
      await invalidateZones(queryClient, projectId);
    },
  };
}

export function createZoneCoordinatesAction(
  projectId: string,
  zoneId: string,
  prevCoords: number[][],
  newCoords: number[][],
  queryClient: QueryClient,
  savedRevision?: string,
): UndoableAction {
  let revision = savedRevision;
  rememberRevision(queryClient, projectId, zoneId, revision);
  return {
    projectId,
    label: 'Move zone',
    zoneId,
    undo: async () => {
      const zone = await siteZonesApi.update(zoneId, { coordinates: prevCoords, expected_updated_at: currentRevision(queryClient, projectId, zoneId, revision) }, { skipHistory: true });
      revision = zone.updated_at;
      rememberRevision(queryClient, projectId, zoneId, revision);
      await invalidateZones(queryClient, projectId);
    },
    redo: async () => {
      const zone = await siteZonesApi.update(zoneId, { coordinates: newCoords, expected_updated_at: currentRevision(queryClient, projectId, zoneId, revision) }, { skipHistory: true });
      revision = zone.updated_at;
      rememberRevision(queryClient, projectId, zoneId, revision);
      await invalidateZones(queryClient, projectId);
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
    projectId,
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
      await invalidateProject(queryClient, projectId);
    },
    redo: async () => {
      await buildingsApi.delete(idRef.current);
      await invalidateProject(queryClient, projectId);
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
    projectId,
    label,
    undo: async () => {
      await buildingsApi.update(buildingId, prevData);
      await invalidateProject(queryClient, projectId);
    },
    redo: async () => {
      await buildingsApi.update(buildingId, newData);
      await invalidateProject(queryClient, projectId);
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
