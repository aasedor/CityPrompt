import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { BICYCLE_CAMERA_HEIGHT_METERS } from '../videoRouteControls';

import {
  STREET_RENDER_VERTICAL_FOV_DEGREES,
  applyStreetCameraProjection,
  applyStreetRoutePose,
  geographicStreetUp,
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

  it('keeps cycling eye height and a forward, level heading through a bend', () => {
    const camera = new THREE.PerspectiveCamera();
    const curve = new THREE.CatmullRomCurve3([
      new THREE.Vector3(0, 100, 0), new THREE.Vector3(10, 100, 0), new THREE.Vector3(20, 100, 10),
    ], false, 'centripetal');
    for (const progress of [0, .25, .5, .75, 1]) {
      applyStreetRoutePose(camera, curve, progress, new THREE.Vector3(0, 1, 0), BICYCLE_CAMERA_HEIGHT_METERS);
      const forward = camera.getWorldDirection(new THREE.Vector3());
      expect(camera.position.y).toBeCloseTo(101.6);
      expect(forward.y).toBeCloseTo(0);
      expect(forward.dot(curve.getTangentAt(progress))).toBeGreaterThan(.98);
    }
  });
});

// Overhead map cameras use north as camera.up; near-ground routes must use
// the Earth's surface normal instead, regardless of the starting orbit.
describe('geographic street route orientation', () => {
  it('raises a Calgary route six metres vertically with a level north-facing horizon', () => {
    const lat = 51.05 * Math.PI / 180, lng = -114.08 * Math.PI / 180;
    const normal = new THREE.Vector3(Math.cos(lat)*Math.cos(lng), Math.cos(lat)*Math.sin(lng), Math.sin(lat));
    const north = new THREE.Vector3(-Math.sin(lat)*Math.cos(lng), -Math.sin(lat)*Math.sin(lng), Math.cos(lat));
    const origin = normal.clone().multiplyScalar(6370000);
    const path = new THREE.CatmullRomCurve3([origin, origin.clone().addScaledVector(north, 36)]);
    const camera = new THREE.PerspectiveCamera();
    camera.up.copy(north);
    const up = geographicStreetUp(51.05, -114.08);
    applyStreetRoutePose(camera, path, .5, up, 6);
    const rise = camera.position.clone().sub(path.getPointAt(.5));
    expect(rise.dot(normal)).toBeCloseTo(6, 6);
    expect(rise.dot(north)).toBeCloseTo(0, 6);
    expect(camera.up.dot(normal)).toBeCloseTo(1, 8);
    expect(camera.getWorldDirection(new THREE.Vector3()).dot(north)).toBeCloseTo(1, 6);
  });
});
