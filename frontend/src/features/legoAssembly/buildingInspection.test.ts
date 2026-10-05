import { afterEach, describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import type { SiteZone } from '@/types';
import { beginBuildingInspection, buildingInspectionStart, constrainBuildingInspection, endBuildingInspection, mountBuildingInspection } from './buildingInspection';

const zone = { id: 'shell', coordinates: [[0,0],[1,0],[1,1]], properties: {}, updated_at: 'first' } as unknown as SiteZone;
afterEach(endBuildingInspection);
function placed(up: 'y' | 'z', yaw: number) {
  const frame = new THREE.Group(), source = new THREE.Group();
  const pos = new THREE.Vector3(), east = new THREE.Vector3(), north = new THREE.Vector3(), vertical = new THREE.Vector3();
  const lat = 51 * Math.PI / 180, lon = -114 * Math.PI / 180;
  WGS84_ELLIPSOID.getCartographicToPosition(lat, lon, 1100, pos);
  WGS84_ELLIPSOID.getEastNorthUpAxes(lat, lon, east, north, vertical);
  frame.matrixAutoUpdate = false; frame.matrix.makeBasis(east,north,vertical); frame.matrix.setPosition(pos);
  const rotation = new THREE.Group(); rotation.rotation.z = yaw; frame.add(rotation);
  if (up === 'y') source.rotation.x = Math.PI / 2;
  rotation.add(source);
  const material = new THREE.MeshStandardMaterial(), geometry = new THREE.BoxGeometry(10, up === 'y' ? 8 : 12, up === 'y' ? 12 : 8);
  const mesh = new THREE.Mesh(geometry, material); mesh.position[up] = 4; source.add(mesh); frame.updateMatrixWorld(true);
  const cleanup = mountBuildingInspection('fixture', zone, source, up);
  const local = (pose: ReturnType<typeof beginBuildingInspection>) => {
    const p = new THREE.Vector3();
    WGS84_ELLIPSOID.getCartographicToPosition(pose!.lat*Math.PI/180,pose!.lng*Math.PI/180,pose!.groundHeight,p);
    return source.worldToLocal(p);
  };
  return { source, material, mesh, geometry, cleanup, local };
}
describe('explicit exterior-shell inspection', () => {
  it.each(['y','z'] as const)('uses the actual %s-up model transform, bounds and base', up => {
    for (const yaw of [0,Math.PI/2,Math.PI,Math.PI*1.5]) {
      const f = placed(up,yaw);
      try {
        const start = beginBuildingInspection([zone],zone.id)!;
        expect(f.local(start)[up]).toBeCloseTo(.05,5);
        expect(start.heading).toBeGreaterThanOrEqual(0); expect(start.heading).toBeLessThan(360);
        const moved = constrainBuildingInspection([zone],zone.id,{...start,lng:start.lng+.01,lat:start.lat+.01,groundHeight:1300,heading:77})!;
        const point = f.local(moved);
        expect(Math.abs(point.x)).toBeLessThanOrEqual(4.801);
        expect(Math.abs(point[up === 'y' ? 'z' : 'y'])).toBeLessThanOrEqual(5.801);
        expect(point[up]).toBeCloseTo(.05,5); expect(moved.heading).toBe(77);
        expect(buildingInspectionStart([zone],zone.id)).toEqual(start);
      } finally { f.cleanup(); f.geometry.dispose(); f.material.dispose(); }
    }
  });
  it('temporarily shows interior faces using owned copies and restores shared materials and geometry', () => {
    const f = placed('y',0), original = f.geometry.getAttribute('position').array.slice();
    try {
      beginBuildingInspection([zone],zone.id);
      expect(f.mesh.material).not.toBe(f.material);
      expect((f.mesh.material as THREE.Material).side).toBe(THREE.DoubleSide);
      expect(f.material.side).toBe(THREE.FrontSide);
      expect(f.material.polygonOffset).toBe(false);
      expect(f.mesh.geometry).toBe(f.geometry);
      expect(f.geometry.getAttribute('position').array).toEqual(original);
      endBuildingInspection(); expect(f.mesh.material).toBe(f.material);
      expect(constrainBuildingInspection([zone],zone.id,{lng:-114,lat:51,groundHeight:1100,heading:0})).toBeNull();
    } finally { f.cleanup(); f.geometry.dispose(); f.material.dispose(); }
  });
  it('rejects moved/deleted/unmounted models and retires active material changes on unmount', () => {
    const f = placed('y',0);
    try {
      expect(beginBuildingInspection([{...zone,updated_at:'moved'}],zone.id)).toBeNull();
      const start = beginBuildingInspection([zone],zone.id)!;
      expect(constrainBuildingInspection([],zone.id,start)).toBeNull();
      expect(constrainBuildingInspection([{...zone,coordinates:[[2,2],[3,2],[3,3]]}],zone.id,start)).toBeNull();
      f.cleanup(); expect(f.mesh.material).toBe(f.material);
      expect(beginBuildingInspection([zone],zone.id)).toBeNull();
    } finally { f.cleanup(); f.geometry.dispose(); f.material.dispose(); }
  });
  it('does not treat an empty or invalid model as an available interior', () => {
    mountBuildingInspection('empty',zone,new THREE.Group());
    expect(beginBuildingInspection([zone],zone.id)).toBeNull();
  });
  it('temporarily hides only a mass cap’s sibling foundation and restores its prior visibility', () => {
    const frame = new THREE.Group(), mesh = new THREE.Mesh(new THREE.BoxGeometry(10,12,8));
    mesh.position.z = 4; frame.add(mesh);
    const foundation = new THREE.Group(); foundation.name = 'landscaped-building-foundation'; frame.add(foundation);
    const context = new THREE.Group(); frame.add(context);
    const cleanup = mountBuildingInspection('mass',zone,mesh,'z');
    try {
      beginBuildingInspection([zone],zone.id);
      expect(foundation.visible).toBe(false); expect(context.visible).toBe(true);
      endBuildingInspection(); expect(foundation.visible).toBe(true);
      foundation.visible=false; beginBuildingInspection([zone],zone.id); cleanup(); expect(foundation.visible).toBe(false);
    } finally { cleanup(); mesh.geometry.dispose(); (mesh.material as THREE.Material).dispose(); }
  });
});
