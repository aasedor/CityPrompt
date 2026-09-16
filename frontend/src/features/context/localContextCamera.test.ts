import { expect, it } from 'vitest';
import { Matrix4, PerspectiveCamera, Quaternion, Vector3 } from 'three';
import { copyCameraToLocalFrame } from './localContextCamera';

it('preserves projected points and authored camera at ECEF magnitudes', () => {
  const frame = new Matrix4().compose(new Vector3(-1643557, -3670025, 4935603),
    new Quaternion().setFromAxisAngle(new Vector3(1, 2, 3).normalize(), 1.1), new Vector3(1, 1, 1));
  const camera = new PerspectiveCamera(55, 1.6, 0.1, 10000000);
  camera.position.copy(new Vector3(30, -60, 35).applyMatrix4(frame));
  camera.up.set(0, 0, 1).transformDirection(frame);
  camera.lookAt(new Vector3().applyMatrix4(frame)); camera.updateMatrixWorld(true);
  const before = camera.toJSON();
  const local = new PerspectiveCamera();
  copyCameraToLocalFrame(camera, local, frame.clone().invert());
  expect(local.position.distanceTo(new Vector3(30, -60, 35))).toBeLessThan(1e-8);
  expect(local.projectionMatrix.elements).toEqual(camera.projectionMatrix.elements);
  for (const point of [new Vector3(0, 0, 0), new Vector3(5, 7, 3)]) {
    expect(point.clone().project(local).distanceTo(point.clone().applyMatrix4(frame).project(camera))).toBeLessThan(1e-8);
  }
  expect(camera.toJSON()).toEqual(before);
});
