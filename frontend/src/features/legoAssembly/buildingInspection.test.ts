import { afterEach, describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import type { SiteZone } from '@/types';
import { updateWalkBuildingInspection, beginBuildingInspection, buildingInspectionStart, constrainBuildingInspection, endBuildingInspection, mountBuildingInspection } from './buildingInspection';

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
describe('continuous building exploration', () => {
  it.each(['y','z'] as const)('follows actual steps in a rotated %s-up model without jumping to its roof', up => {
    const f=placed(up,.7);
    const step=new THREE.Mesh(new THREE.BoxGeometry(2,up==='y'?.3:2,up==='y'?2:.3),new THREE.MeshStandardMaterial());
    step.position[up]=.15; f.source.add(step); f.source.updateWorldMatrix(true,true);
    const point=new THREE.Vector3(); point[up]=.05; f.source.localToWorld(point);
    const g=WGS84_ELLIPSOID.getPositionToCartographic(point,{lat:0,lon:0,height:0});
    const pose={lat:g.lat*180/Math.PI,lng:g.lon*180/Math.PI,groundHeight:g.height,heading:0};
    try {
      const entered=updateWalkBuildingInspection([zone],pose)!;
      expect(f.local(entered.pose)[up]).toBeCloseTo(.32,4);
      expect(entered.pose.lng).toBe(pose.lng); expect(entered.pose.lat).toBe(pose.lat);
      step.position[up]=.4; f.source.updateWorldMatrix(true,true);
      const climbed=updateWalkBuildingInspection([zone],entered.pose)!;
      expect(f.local(climbed.pose)[up]).toBeCloseTo(.57,4);
      step.position[up]=.15; f.source.updateWorldMatrix(true,true);
      expect(f.local(updateWalkBuildingInspection([zone],climbed.pose)!.pose)[up]).toBeCloseTo(.32,4);
    } finally { f.cleanup(); f.geometry.dispose(); f.material.dispose(); step.geometry.dispose(); (step.material as THREE.Material).dispose(); }
  });

  it.each(['y','z'] as const)('enters and leaves a rotated %s-up model without teleporting or a separate control', up => {
    const f=placed(up,.7);
    try {
      const inside=beginBuildingInspection([zone],zone.id)!;
      endBuildingInspection();
      const entered=updateWalkBuildingInspection([zone], {...inside,heading:43})!;
      expect(entered.zoneId).toBe(zone.id);
      expect(entered.pose.lng).toBe(inside.lng);
      expect(entered.pose.lat).toBe(inside.lat);
      expect(entered.pose.heading).toBe(43);
      expect(f.local(entered.pose)[up]).toBeCloseTo(.05,4);
      expect(f.mesh.material).not.toBe(f.material);
      expect(updateWalkBuildingInspection([zone],{...inside,lng:inside.lng+.001})).toBeNull();
      expect(f.mesh.material).toBe(f.material);
      expect(updateWalkBuildingInspection([zone],inside)).not.toBeNull();
      expect(updateWalkBuildingInspection([{...zone,updated_at:'changed'}],inside)).toBeNull();
      expect(f.mesh.material).toBe(f.material);
    } finally { f.cleanup(); f.geometry.dispose(); f.material.dispose(); }
  });
});

describe('explicit exterior-shell inspection', () => {
  it('prefers a clear room over open landscape included in model bounds', () => {
    const f = placed('y', .5);
    f.cleanup();
    const landscape = new THREE.Mesh(new THREE.BoxGeometry(28, .05, 32), new THREE.MeshStandardMaterial());
    landscape.position.set(7, .025, 8); f.source.add(landscape);
    const cleanup = mountBuildingInspection('landscape', zone, f.source);
    try {
      const point = f.local(beginBuildingInspection([zone], zone.id));
      expect(Math.abs(point.x)).toBeLessThan(4.5);
      expect(Math.abs(point.z)).toBeLessThan(5.5);
    } finally {
      cleanup(); f.geometry.dispose(); f.material.dispose();
      landscape.geometry.dispose(); (landscape.material as THREE.Material).dispose();
    }
  });
  it.each(['y','z'] as const)('starts away from a central party wall in a rotated %s-up row', up => {
    const f = placed(up, Math.PI / 3);
    const partition = new THREE.Mesh(new THREE.BoxGeometry(.24, up === 'y' ? 8 : 12, up === 'y' ? 12 : 8), new THREE.MeshStandardMaterial());
    partition.position[up] = 4; f.source.add(partition);
    try {
      const pose = beginBuildingInspection([zone], zone.id)!;
      const point = f.local(pose);
      expect(Math.abs(point.x)).toBeGreaterThan(.8);
      expect(point[up]).toBeCloseTo(.05, 5);
      expect(buildingInspectionStart([zone], zone.id)).toEqual(pose);
    } finally {
      f.cleanup(); f.geometry.dispose(); f.material.dispose();
      partition.geometry.dispose(); (partition.material as THREE.Material).dispose();
    }
  });
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
