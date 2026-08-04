import { describe, expect, it } from 'vitest';
import * as THREE from 'three';

import {
  STREET_RENDER_VERTICAL_FOV_DEGREES,
  applyStreetCameraProjection,
  applyStreetRoutePose,
  projectStreetRouteToGround,
  restoreStreetCameraProjection,
  verticalFovForHorizontalSensor,
} from './streetRenderProfile';

describe('streetRenderProfile', () => {
  it('converts a full-frame 35 mm lens to the vertical Three.js field of view', () => {
    expect(verticalFovForHorizontalSensor(35, 16 / 9)).toBeCloseTo(32.27, 1);
    expect(STREET_RENDER_VERTICAL_FOV_DEGREES).toBeCloseTo(32.27, 1);
  });

  it('applies and restores the street camera projection exactly', () => {
    const camera = new THREE.PerspectiveCamera(75, 16 / 9, 1, 1000);
    const previous = applyStreetCameraProjection(camera);
    expect(camera.fov).toBeCloseTo(32.27, 1);
    expect(camera.near).toBe(0.1);
    restoreStreetCameraProjection(camera, previous);
    expect(camera.fov).toBe(75);
    expect(camera.near).toBe(1);
  });

  it('projects the drawn route onto a local ground plane without scene geometry', () => {
    const camera = new THREE.PerspectiveCamera(32.27, 16 / 9, 0.1, 1000);
    camera.position.set(0, 1.7, 0);
    camera.up.set(0, 1, 0);
    camera.lookAt(0, 1.7, -20);
    camera.updateMatrixWorld(true);

    const route = projectStreetRouteToGround(camera, [
      { x: 0.42, y: 0.66 },
      { x: 0.58, y: 0.66 },
    ], 16 / 9, camera.up, { maxDistanceMeters: 100 });

    expect(route).toHaveLength(2);
    expect(route[0].y).toBeCloseTo(0);
    expect(route[1].y).toBeCloseTo(0);
    expect(route[0].x).toBeLessThan(route[1].x);
  });

  it('keeps the route camera at eye height and points along the path', () => {
    const camera = new THREE.PerspectiveCamera();
    const curve = new THREE.CatmullRomCurve3([
      new THREE.Vector3(-2, 0, 0),
      new THREE.Vector3(2, 0, 0),
    ], false, 'centripetal');
    applyStreetRoutePose(camera, curve, 0.5, new THREE.Vector3(0, 1, 0));
    const forward = camera.getWorldDirection(new THREE.Vector3());
    expect(camera.position.y).toBeCloseTo(1.7);
    expect(forward.x).toBeGreaterThan(0.99);
  });

  it('keeps a pedestrian fly-by focused on the authored site', () => {
    const camera = new THREE.PerspectiveCamera();
    const curve = new THREE.CatmullRomCurve3([
      new THREE.Vector3(-2, 0, 0),
      new THREE.Vector3(2, 0, 0),
    ], false, 'centripetal');
    const siteFocus = new THREE.Vector3(0, 6, -12);

    applyStreetRoutePose(
      camera,
      curve,
      0.5,
      new THREE.Vector3(0, 1, 0),
      undefined,
      siteFocus,
    );

    const forward = camera.getWorldDirection(new THREE.Vector3());
    const expected = siteFocus.clone().sub(camera.position).normalize();
    expect(forward.angleTo(expected)).toBeLessThan(1e-6);
    expect(forward.z).toBeLessThan(-0.8);
  });
});
