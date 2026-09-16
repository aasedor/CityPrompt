import type { QueryClient } from '@tanstack/react-query';
import { siteZonesApi, buildingsApi } from '@/services/api';
import type { SiteZone, SiteZoneProperties } from '@/types';
import type { UndoableAction } from './undoRedo';
import { streetCoordinateUpdate } from '@/features/pickPlace/streetPlacement';
import { readParkTerrain, type ParkTerrainProfile } from '@/components/viewer/globe/parkTerrain';

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

/** A locally compiled representation is not an intervening authored edit. */
export function advanceDerivedZoneRevision(client: QueryClient, projectId: string, zoneId: string, before: string, after: string) {
  const revisions = localRevisions.get(client);
  const key = `${projectId}:${zoneId}`;
  if (revisions?.get(key) === before) revisions.set(key, after);
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
  let restoreZone = createdZone;
  const idRef: IdRef = { current: createdZone.id, revision: createdZone.updated_at };
  rememberRevision(queryClient, projectId, createdZone.id, createdZone.updated_at);

  return {
    projectId,
    label: 'Create zone',
    getZoneId: () => idRef.current,
    matchesZoneId: (zoneId) => zoneId === originalZoneId || zoneId === idRef.current,
    undo: async () => {
      const expected = currentRevision(queryClient, projectId, idRef.current, idRef.revision);
      const current = queryClient.getQueryData<SiteZone[]>(['site-zones', projectId])?.find(zone => zone.id === idRef.current);
      await siteZonesApi.delete(idRef.current, expected, { skipHistory: true });
      if (current && current.updated_at === expected) restoreZone = current;
      await invalidateZones(queryClient, projectId);
    },
    redo: async () => {
      const zone = await siteZonesApi.create(projectId, {
        name: restoreZone.name,
        zone_type: restoreZone.zone_type,
        coordinates: restoreZone.coordinates,
        color: restoreZone.color,
        properties: restoreZone.properties,
        sort_order: restoreZone.sort_order,
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
  prevData: { name?: string; color?: string; coordinates?: number[][]; properties?: SiteZoneProperties },
  newData: { name?: string; color?: string; coordinates?: number[][]; properties?: SiteZoneProperties },
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
  previousZone?: SiteZone,
): UndoableAction {
  let revision = savedRevision;
  rememberRevision(queryClient, projectId, zoneId, revision);
  // Ground measurements belong to the outline they measured. A smaller park's
  // derived grid cannot replace the larger outline's support when undoing.
  const terrain = (zone?: SiteZone): ParkTerrainProfile | undefined =>
    zone && readParkTerrain(zone) ? zone.properties?.park_terrain as ParkTerrainProfile : undefined;
  let beforeTerrain = terrain(previousZone), afterTerrain: ParkTerrainProfile | undefined;
  const coordinateData = (current: SiteZone | undefined, coordinates: number[][], profile?: ParkTerrainProfile) => {
    const data = streetCoordinateUpdate(current, coordinates);
    if (!current || !profile) return data;
    const properties = { ...current.properties, park_terrain: profile };
    return readParkTerrain({ ...current, coordinates, properties }) ? { ...data, properties } : data;
  };
  return {
    projectId,
    label: 'Move zone',
    zoneId,
    undo: async () => {
      const current = queryClient.getQueryData<SiteZone[]>(['site-zones', projectId])?.find(zone => zone.id === zoneId);
      const measured = terrain(current);
      const zone = await siteZonesApi.update(zoneId, { ...coordinateData(current, prevCoords, beforeTerrain), expected_updated_at: currentRevision(queryClient, projectId, zoneId, revision) }, { skipHistory: true });
      afterTerrain = measured ?? afterTerrain;
      revision = zone.updated_at;
      rememberRevision(queryClient, projectId, zoneId, revision);
      await invalidateZones(queryClient, projectId);
    },
    redo: async () => {
      const current = queryClient.getQueryData<SiteZone[]>(['site-zones', projectId])?.find(zone => zone.id === zoneId);
      const measured = terrain(current);
      const zone = await siteZonesApi.update(zoneId, { ...coordinateData(current, newCoords, afterTerrain), expected_updated_at: currentRevision(queryClient, projectId, zoneId, revision) }, { skipHistory: true });
      beforeTerrain = measured ?? beforeTerrain;
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
