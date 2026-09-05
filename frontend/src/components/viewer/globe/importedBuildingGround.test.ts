import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { importedModelGroundFootprints } from './importedBuildingGround';
import { resolveBuildingGroundContact } from './buildingGroundContact';
import type { FootprintFrame } from './buildingPlacement';
import { metersPerDegLon } from '../mapEngine/geoUtils';

const frame: FootprintFrame = { centroidLng: -114, centroidLat: 51, bearingRad: 0.2,
  longDim: 50, shortDim: 30, rectCenterLocal: [3, -7] };
const bounds = new THREE.Box3(new THREE.Vector3(8, -5, -20), new THREE.Vector3(12, 3, -14));

describe('imported model shared-ground footprint', () => {
  it('matches actual nested render transforms with asymmetric origin, scale and yaw', () => {
    const placement = { scale: 1.7, yawRad: 0.63, heightWarning: false };
    const outer = new THREE.Group(); outer.position.set(...frame.rectCenterLocal, 0); outer.rotation.z = placement.yawRad;
    const swizzle = new THREE.Group(); swizzle.rotation.x = Math.PI / 2; swizzle.scale.setScalar(placement.scale); outer.add(swizzle);
    const recenter = new THREE.Group(); recenter.position.set(-10, 5, 17); swizzle.add(recenter); outer.updateMatrixWorld(true);
    const actual = importedModelGroundFootprints(bounds, placement, frame)[0];
    [[8, -20], [12, -20], [12, -14], [8, -14]].forEach(([x, z], i) => {
      const expected = new THREE.Vector3(x, -5, z).applyMatrix4(recenter.matrixWorld);
      expect(actual[i][0]).toBeCloseTo(expected.x, 10); expect(actual[i][1]).toBeCloseTo(expected.y, 10);
    });
    expect(bounds.min.toArray()).toEqual([8, -5, -20]);
    expect(bounds.max.toArray()).toEqual([12, 3, -14]);
  });
  it('supports only the fitted model envelope and leaves the larger plot uncovered', () => {
    const footprints = importedModelGroundFootprints(bounds, { scale: 2, yawRad: 0, heightWarning: false }, frame);
    expect(footprints).toEqual([[[-1, -1], [7, -1], [7, -13], [-1, -13]]]);
    const ground = { status: 'ready', contains: () => true,
      heightAt: (lng: number) => 100 + (lng - frame.centroidLng) * metersPerDegLon(frame.centroidLat) * 0.05 };
    const contact = resolveBuildingGroundContact(footprints, frame.centroidLng, frame.centroidLat, ground);
    if (contact.status !== 'ready') throw new Error('Expected a measured foundation');
    expect(contact.anchorHeight).toBeCloseTo(100.39, 6);
    expect(contact.reliefM).toBeCloseTo(0.4, 6);
    for (let i = 0; i < contact.positions.length; i += 3) {
      expect(contact.positions[i]).toBeGreaterThanOrEqual(-1); expect(contact.positions[i]).toBeLessThanOrEqual(7);
      expect(contact.positions[i + 1]).toBeGreaterThanOrEqual(-13); expect(contact.positions[i + 1]).toBeLessThanOrEqual(-1);
    }
  });
  it('cannot invent support for a missing model placement or partially measured footprint', () => {
    expect(importedModelGroundFootprints(bounds, null, frame)).toEqual([]);
    const footprints = importedModelGroundFootprints(bounds, { scale: 2, yawRad: 0, heightWarning: false }, frame);
    expect(resolveBuildingGroundContact(footprints, frame.centroidLng, frame.centroidLat,
      { status: 'sampling', contains: () => true, heightAt: () => null })).toEqual({ status: 'unresolved', reason: 'ground_not_ready' });
    expect(resolveBuildingGroundContact(footprints, frame.centroidLng, frame.centroidLat,
      { status: 'ready', contains: (lng) => lng <= frame.centroidLng, heightAt: () => 100 })).toEqual({ status: 'unresolved', reason: 'incomplete_footprint_ground' });
  });
});
