import { expect, it } from 'vitest';
import { Group } from 'three';
import { assertStreetGroundReady, streetGroundCaptureStatus } from './streetGroundCapture';

it('does not capture a missing road while its independent ground is sampling', () => {
  const scene = new Group(), road = new Group(); scene.add(road);
  road.userData.streetGroundStatus = 'sampling';
  expect(streetGroundCaptureStatus(scene)).toBe('sampling');
  road.userData.streetGroundStatus = 'unavailable';
  expect(streetGroundCaptureStatus(scene)).toBe('unavailable');
  road.userData.streetGroundStatus = 'ready';
  expect(streetGroundCaptureStatus(scene)).toBe('ready');
  scene.remove(road);
  expect(streetGroundCaptureStatus(scene)).toBe('ready');
});

it('blocks an early prepared-road export and rejects a new pending alignment during capture', () => {
  const scene = new Group(), road = new Group(); scene.add(road);
  road.userData.streetGroundStatus = 'sampling';
  expect(() => assertStreetGroundReady(scene)).toThrow(/still aligning/);
  road.userData.streetGroundStatus = 'ready';
  expect(() => assertStreetGroundReady(scene)).not.toThrow();
  road.userData.streetGroundStatus = 'sampling';
  expect(() => assertStreetGroundReady(scene)).toThrow(/still aligning/);
  road.userData.streetGroundStatus = 'unavailable';
  expect(() => assertStreetGroundReady(scene)).toThrow(/could not be measured completely/);
});
