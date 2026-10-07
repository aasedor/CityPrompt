import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { centreNativeClayClone } from '@/features/legoAssembly/nativeClayPlacement';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { sharedSiteGroundContains } from './sharedSiteGround';
import type { SharedSiteGroundState } from './SharedSiteGroundProvider';
import { reviewBuildingFootprints, reviewBuildingGroundContact } from './reviewBuildingGround';

const lng = -114, lat = 51;
function source() {
  const scene = new THREE.Group();
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(38, 7.27, 30));
  mesh.position.set(2, 5.635, 3);
  scene.add(mesh);
  return scene;
}
function ground(halfWidth = 25): SharedSiteGroundState {
  const boundaryCoordinates: [number, number][] = [[-halfWidth,-20],[halfWidth,-20],[halfWidth,20],[-halfWidth,20]]
    .map(([x,y]) => [lng + x / metersPerDegLon(lat), lat + y / METERS_PER_DEG_LAT]);
  const contains = (x: number, y: number) => sharedSiteGroundContains(boundaryCoordinates, x, y);
  return { status: 'ready', snapshot: null, revision: 'measured:1', boundaryCoordinates, contains,
    heightAt: (x,y) => contains(x,y) ? 1102.662 : null, isCurrent: () => true };
}

describe('fixed review GLB ground contact', () => {
  it.each([0, Math.PI / 6, Math.PI / 2, Math.PI])('matches the actual bottom-centred Three instance at yaw %s', yaw => {
    const original = source();
    const before = new THREE.Box3().setFromObject(original, true);
    const model = centreNativeClayClone(original.clone(true));
    const root = new THREE.Group(); root.rotation.z = yaw;
    const axes = new THREE.Group(); axes.rotation.x = Math.PI / 2; axes.add(model); root.add(axes);
    root.updateMatrixWorld(true);
    const actual = reviewBuildingFootprints(original, yaw)[0];
    const originalCorners = [[before.min.x,before.min.z],[before.max.x,before.min.z],
      [before.max.x,before.max.z],[before.min.x,before.max.z]];
    originalCorners.forEach(([x,z], i) => {
      const expected = new THREE.Vector3(x, before.min.y, z).applyMatrix4(model.children[0].matrixWorld);
      expect(actual[i][0]).toBeCloseTo(expected.x, 6); expect(actual[i][1]).toBeCloseTo(expected.y, 6);
      expect(expected.z).toBeCloseTo(0, 6);
    });
    expect(new THREE.Box3().setFromObject(original, true).equals(before)).toBe(true);
    expect(original.children[0].scale.toArray()).toEqual([1,1,1]);
  });
  it('seats the entire native plot on shared measured ground and creates a bounded foundation', () => {
    const result = reviewBuildingGroundContact(reviewBuildingFootprints(source(),0),lng,lat,ground());
    expect(result.status).toBe('ready');
    if (result.status !== 'ready') throw new Error('Expected measured contact');
    expect(result.anchorHeight).toBeCloseTo(1102.702, 8);
    expect(result.reliefM).toBe(0); expect(result.indices.length).toBeGreaterThan(0);
  });
  it('rejects missing support at the full plot edge, even if the central building fits', () => {
    const result = reviewBuildingGroundContact(reviewBuildingFootprints(source(),0),lng,lat,ground(18.9));
    expect(result).toEqual({status:'unresolved',reason:'incomplete_footprint_ground'});
  });
  it.each(['stale','preview','sampling','missing'] as const)('does not authorize contact from %s ground', mode => {
    const g = ground();
    if (mode === 'stale') g.isCurrent = () => false;
    if (mode === 'preview') g.preview = true;
    if (mode === 'sampling') g.status = 'sampling';
    if (mode === 'missing') g.heightAt = () => null;
    expect(reviewBuildingGroundContact(reviewBuildingFootprints(source(),0),lng,lat,g).status).toBe('unresolved');
  });
  it('keeps empty or nonfinite sources unresolved', () => {
    expect(reviewBuildingFootprints(new THREE.Group(),0)).toEqual([]);
    expect(reviewBuildingFootprints(source(),NaN)).toEqual([]);
    expect(reviewBuildingGroundContact([],lng,lat,ground())).toEqual({status:'unresolved',reason:'missing_footprint'});
  });
});
