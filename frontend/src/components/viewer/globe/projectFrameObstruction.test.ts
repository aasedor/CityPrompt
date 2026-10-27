import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import { findUnobstructedProjectFrame } from './projectFrameObstruction';
import { patchMaterialForSpatialMask } from './TileSpatialMaskPlugin';
import { DIRECT_3D_PROPOSAL_ROLE_KEY } from './direct3dCapture';

const up = new THREE.Vector3(0, 0, 1);
function cameraAt(position = new THREE.Vector3(30, -120, 80), target = new THREE.Vector3(0, 0, 10)) {
  const camera = new THREE.PerspectiveCamera(75, 2048 / 710, 1, 100000);
  camera.up.copy(up); camera.position.copy(position); camera.lookAt(target); camera.updateMatrixWorld(true);
  return camera;
}
function contextBox(scene: THREE.Scene, min: number[], max: number[]) {
  const bounds = new THREE.Box3(new THREE.Vector3(...min), new THREE.Vector3(...max));
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(...bounds.getSize(new THREE.Vector3()).toArray()),
    new THREE.MeshBasicMaterial({ side: THREE.DoubleSide }));
  mesh.position.copy(bounds.getCenter(new THREE.Vector3()));
  const context = new THREE.Group(); context.userData = { sceneRole: 'existing', contextProvider: 'google' };
  context.add(mesh); scene.add(context); scene.updateMatrixWorld(true);
  return mesh;
}
describe('project framing around existing context', () => {
  it('clears the measured QA foreground context volume without changing target range or scene geometry', () => {
    const scene = new THREE.Scene();
    const mesh = contextBox(scene, [-1639164.656,-3668803.747,4937964.726], [-1639122.772,-3668748.129,4938013.468]);
    const normal = new THREE.Vector3(), target = new THREE.Vector3();
    WGS84_ELLIPSOID.getCartographicToNormal(51.052131808 * Math.PI / 180, -114.07463463 * Math.PI / 180, normal);
    WGS84_ELLIPSOID.getCartographicToPosition(51.052131808 * Math.PI / 180, -114.07463463 * Math.PI / 180, 1043.4869, target);
    const camera = cameraAt(new THREE.Vector3(-1639148.829,-3668791.746,4937984.415), target);
    camera.up.copy(normal); camera.lookAt(target); camera.updateMatrixWorld(true);
    const ray = new THREE.Raycaster(camera.position.clone(), target.clone().sub(camera.position).normalize());
    // The recorded world bounds enclose the camera; the box exit is foreground.
    expect(ray.intersectObject(mesh)[0].distance).toBeLessThan(60);
    const before = mesh.matrixWorld.clone(), position = camera.position.clone();
    const next = findUnobstructedProjectFrame(camera, scene, target, normal);
    expect(next).not.toBeNull();
    expect(next!.clone().sub(position).dot(normal)).toBeGreaterThan(0);
    expect(next!.distanceTo(target)).toBeCloseTo(position.distanceTo(target), 6);
    ray.set(next!, target.clone().sub(next!).normalize()); ray.far = next!.distanceTo(target) * .75;
    expect(ray.intersectObject(mesh)).toHaveLength(0);
    expect(camera.position).toEqual(position);
    expect(mesh.matrixWorld).toEqual(before); expect(mesh.visible).toBe(true);
  });
  it('keeps a clear view unchanged, including proposal geometry and hidden context', () => {
    const scene = new THREE.Scene(), camera = cameraAt(), target = new THREE.Vector3(0, 0, 10);
    expect(findUnobstructedProjectFrame(camera, scene, target, up)).toBeNull();
    const mesh = contextBox(scene, [10,-130,60], [50,-100,100]);
    mesh.parent!.userData.sceneRole = 'proposal';
    expect(findUnobstructedProjectFrame(camera, scene, target, up)).toBeNull();
    mesh.parent!.userData.sceneRole = 'existing'; mesh.visible = false;
    expect(findUnobstructedProjectFrame(camera, scene, target, up)).toBeNull();
    mesh.visible = true; mesh.userData[DIRECT_3D_PROPOSAL_ROLE_KEY] = 'building';
    expect(findUnobstructedProjectFrame(camera, scene, target, up)).toBeNull();
  });
  it('ignores existing geometry discarded by the prepared-site spatial shader', () => {
    const scene = new THREE.Scene(), camera = cameraAt(), target = new THREE.Vector3(0, 0, 10);
    const mesh = contextBox(scene, [10,-130,60], [50,-100,100]);
    patchMaterialForSpatialMask(mesh.material as THREE.Material, { worldToLocal: new THREE.Matrix4(),
      edges: [new THREE.Vector4(-200,-200,200,-200), new THREE.Vector4(200,-200,200,200),
        new THREE.Vector4(200,200,-200,200), new THREE.Vector4(-200,200,-200,-200)],
      maskRanges: [new THREE.Vector2(0,4)], maskCount: 1, minHeight: -100, maxHeight: 200, cacheKey: 'prepared' });
    expect(findUnobstructedProjectFrame(camera, scene, target, up)).toBeNull();
  });
  it('leaves the camera unchanged when all bounded pitches are obstructed', () => {
    const scene = new THREE.Scene(), camera = cameraAt(), target = new THREE.Vector3(0, 0, 10);
    const shell = new THREE.Mesh(new THREE.SphereGeometry(100, 48, 24), new THREE.MeshBasicMaterial({ side: THREE.DoubleSide }));
    shell.position.copy(target); shell.userData = { sceneRole: 'existing' }; scene.add(shell); scene.updateMatrixWorld(true);
    const before = camera.position.clone();
    expect(findUnobstructedProjectFrame(camera, scene, target, up)).toBeNull();
    expect(camera.position).toEqual(before);
  });
  it('clears a foreground roof covering a site-ground sample below an unobstructed optical centre', () => {
    const scene = new THREE.Scene(), camera = cameraAt(), target = new THREE.Vector3(0, 0, 10);
    const roof = contextBox(scene, [0,-110,0], [40,-80,40]);
    expect(findUnobstructedProjectFrame(camera, scene, target, up)).toBeNull();
    const groundSample = new THREE.Vector3(0,-65,0);
    const next = findUnobstructedProjectFrame(camera, scene, target, up, [groundSample]);
    expect(next).not.toBeNull();
    const ray = new THREE.Raycaster(next!.clone(), groundSample.clone().sub(next!).normalize(), 0, next!.distanceTo(groundSample)-1);
    expect(ray.intersectObject(roof)).toHaveLength(0);
    expect(next!.distanceTo(target)).toBeCloseTo(camera.position.distanceTo(target), 6);
  });
  it('does not triangle-raycast the 1309 distant context meshes outside the project frame', () => {
    const scene = new THREE.Scene(), camera = cameraAt(), target = new THREE.Vector3(0, 0, 10);
    const context = new THREE.Group(); context.userData.sceneRole = 'existing'; scene.add(context);
    const geometry = new THREE.BoxGeometry(20,20,20), material = new THREE.MeshBasicMaterial();
    let triangleChecks = 0;
    for (let index = 0; index < 1309; index++) {
      const mesh = new THREE.Mesh(geometry, material); mesh.position.set(10000 + index * 20, 10000, 0);
      mesh.raycast = function (ray, hits) { triangleChecks++; THREE.Mesh.prototype.raycast.call(this,ray,hits); };
      context.add(mesh);
    }
    scene.updateMatrixWorld(true);
    expect(findUnobstructedProjectFrame(camera, scene, target, up, [target])).toBeNull();
    expect(triangleChecks).toBe(0);
    geometry.dispose(); material.dispose();
  });
});
