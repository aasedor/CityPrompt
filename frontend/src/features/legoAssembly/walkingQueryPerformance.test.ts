import { afterEach, describe, expect, it, vi } from 'vitest';
import * as THREE from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import type { SiteZone } from '@/types';
import { mountBuildingInspection, updateWalkBuildingInspection, endBuildingInspection } from './buildingInspection';
import { buildingWalkEntrance, mountBuildingWalking, type BuildingWalkNetwork } from './buildingWalking';

const cleanup: Array<() => void> = [];
afterEach(() => { cleanup.splice(0).reverse().forEach(fn => fn()); endBuildingInspection(); vi.restoreAllMocks(); });
const radians = Math.PI / 180;
const pose = { lng: -114, lat: 51, groundHeight: 1100, heading: 25 };
function fixture(index: number, distance: number, kind: 'shell' | 'network') {
  const object = new THREE.Group(), frame = new THREE.Group();
  const east = new THREE.Vector3(), north = new THREE.Vector3(), up = new THREE.Vector3();
  WGS84_ELLIPSOID.getEastNorthUpAxes(pose.lat*radians, pose.lng*radians, east, north, up);
  frame.matrixAutoUpdate = false;
  frame.matrix.makeBasis(east, north, up);
  frame.matrix.setPosition(WGS84_ELLIPSOID.getCartographicToPosition(pose.lat*radians, pose.lng*radians, pose.groundHeight, new THREE.Vector3()));
  object.rotation.x = Math.PI/2; object.position.x = distance; frame.add(object);
  const geometry = new THREE.BoxGeometry(10, 8, 12), material = new THREE.MeshStandardMaterial();
  const mesh = new THREE.Mesh(geometry, material); mesh.position.y = 4; object.add(mesh);
  const serialize = vi.fn(() => ({ description: 'architectural metadata '.repeat(500) }));
  const zone = { id: `perf-${index}`, coordinates: [[0,0],[1,0],[1,1]], properties: { toJSON: serialize }, updated_at: 'first' } as unknown as SiteZone;
  const network: BuildingWalkNetwork = { version: 2, footprint: [10,12], entrance: [0,0,0], portals: [[-1,1,-6,0]],
    maxStepM: .2, routes: [], obstacles: [], triangles: [[[-5,-6,0],[5,-6,0],[5,6,0]],[[-5,-6,0],[5,6,0],[-5,6,0]]] };
  const unmount = kind === 'shell' ? mountBuildingInspection(zone.id, zone, object)
    : mountBuildingWalking(zone.id, zone, object, network);
  cleanup.push(() => { unmount(); geometry.dispose(); material.dispose(); });
  serialize.mockClear();
  return { zone, serialize, frame, object, mesh };
}

describe('walking queries in a larger community', () => {
  it.each(['shell', 'network'] as const)('skips expensive revision checks for distant %s models and converts the camera once', kind => {
    const fixtures = Array.from({ length: 40 }, (_, i) => fixture(i, 100 + i*20, kind));
    const zones = fixtures.map(f => f.zone);
    const convert = vi.spyOn(WGS84_ELLIPSOID, 'getCartographicToPosition');
    const query = kind === 'shell' ? updateWalkBuildingInspection : buildingWalkEntrance;
    for (let i = 0; i < 200; i++) expect(query(zones, pose)).toBeNull();
    expect(fixtures.reduce((sum, f) => sum + f.serialize.mock.calls.length, 0)).toBe(0);
    expect(convert).toHaveBeenCalledTimes(200);
  });

  it.each(['shell', 'network'] as const)('refreshes moved parent transforms and rejects edited, deleted and unmounted %s models', kind => {
    const f = fixture(0, 100, kind), zones = [f.zone];
    const query = kind === 'shell' ? updateWalkBuildingInspection : buildingWalkEntrance;
    expect(query(zones, pose)).toBeNull();
    // Move the parent without calling updateMatrixWorld: queries must see it.
    f.frame.matrix.multiply(new THREE.Matrix4().makeTranslation(-100, 0, 0));
    expect(query(zones, pose)).not.toBeNull();
    // Even same-reference metadata changes must invalidate the registration.
    f.serialize.mockImplementation(() => ({ description: 'changed metadata' }));
    expect(query(zones, pose)).toBeNull();
    f.zone.properties = { changed: true } as SiteZone['properties'];
    expect(query(zones, pose)).toBeNull();
    expect(query([], pose)).toBeNull();
    cleanup.splice(0).reverse().forEach(fn => fn());
    expect(query(zones, pose)).toBeNull();
  });
});
