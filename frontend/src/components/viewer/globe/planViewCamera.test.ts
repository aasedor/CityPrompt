import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { PLAN_VIEW_FOV_DEGREES, WORKING_VIEW_FOV_DEGREES, distanceForFieldOfView, setWorkingCameraProjection, syncPlanCameraClipping, syncPlanCameraFog } from './planViewCamera';
import { applyStreetCameraProjection, restoreStreetCameraProjection } from './streetRenderProfile';

describe('plan view camera', () => {
  it('keeps the ground framing while reducing the roof displacement of a 100 m tower to less than 2 pixels', () => {
    const camera = new THREE.PerspectiveCamera(75, 1681 / 1160, 1, 1e11);
    const ground = new THREE.Vector3(80, 0, 0);
    const roof = new THREE.Vector3(80, 0, 100);
    camera.position.set(0, 0, 200); camera.lookAt(0, 0, 0); camera.updateMatrixWorld();
    const originalGround = ground.clone().project(camera);
    const originalShift = Math.abs(roof.clone().project(camera).x - originalGround.x) * 1681 / 2;
    const distance = distanceForFieldOfView(200, camera.fov, PLAN_VIEW_FOV_DEGREES);
    camera.position.z = distance;
    setWorkingCameraProjection(camera, true, distance); camera.updateMatrixWorld();
    const planGround = ground.clone().project(camera);
    const planShift = Math.abs(roof.clone().project(camera).x - planGround.x) * 1681 / 2;
    expect(planGround.x).toBeCloseTo(originalGround.x, 8);
    expect(originalShift).toBeGreaterThan(250);
    expect(planShift).toBeLessThan(2);
    expect(distanceForFieldOfView(distance, camera.fov, WORKING_VIEW_FOV_DEGREES)).toBeCloseTo(200, 8);
  });

  it('keeps millimetre ground layers distinguishable and updates clipping after zooming', () => {
    const camera = new THREE.PerspectiveCamera(75, 1, 1, 1e11);
    setWorkingCameraProjection(camera, true, 8000);
    camera.position.set(0, 0, 8000); camera.lookAt(0, 0, 0); camera.updateMatrixWorld();
    const groundDepth = new THREE.Vector3(0, 0, 0).project(camera).z;
    const pavingDepth = new THREE.Vector3(0, 0, .025).project(camera).z;
    expect(Math.abs(groundDepth - pavingDepth)).toBeGreaterThan(2 / 2 ** 24);
    syncPlanCameraClipping(camera, 4000);
    expect(camera.near).toBe(1000);
    setWorkingCameraProjection(camera, false);
    expect(camera.fov).toBe(75); expect(camera.near).toBe(1);
  });

  it('restores the plan lens and clipping after a street capture', () => {
    const camera = new THREE.PerspectiveCamera(75, 1, 1, 1e11);
    setWorkingCameraProjection(camera, true, 8000);
    const previous = applyStreetCameraProjection(camera);
    expect(camera.fov).toBeGreaterThan(20); expect(camera.near).toBe(.1);
    syncPlanCameraClipping(camera, 8000);
    expect(camera.near).toBe(.1);
    restoreStreetCameraProjection(camera, previous);
    expect(camera.fov).toBe(PLAN_VIEW_FOV_DEGREES); expect(camera.near).toBe(2000);
  });

  it('keeps the same atmosphere at the distant plan lens, then restores working and street fog', () => {
    const camera = new THREE.PerspectiveCamera(75, 1, 1, 1e11);
    const fog = new THREE.Fog('#b8c8d8', 8000, 80000);
    setWorkingCameraProjection(camera, true, 80000);
    syncPlanCameraFog(camera, fog);
    expect(fog.near).toBeGreaterThan(700000);
    const once = fog.near;
    syncPlanCameraFog(camera, fog); expect(fog.near).toBe(once);
    setWorkingCameraProjection(camera, false);
    syncPlanCameraFog(camera, fog);
    expect(fog.near).toBe(8000); expect(fog.far).toBe(80000);
    const streetFog = new THREE.Fog('#cfdae4', 180, 900);
    syncPlanCameraFog(camera, streetFog);
    expect(streetFog.near).toBe(180); expect(streetFog.far).toBe(900);
  });
});
