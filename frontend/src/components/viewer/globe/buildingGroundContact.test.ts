import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { currentBuildingGroundingIssues, geographicFootprint, placedNativeFootprints, resolveBuildingGroundContact, updateBuildingGroundingIssues, type GroundPoint, type PlacedModuleBounds } from './buildingGroundContact';
import { createSharedSiteGroundSnapshot, sampleSharedSiteGround, sharedSiteGroundContains, type SharedSiteGroundLayout } from './sharedSiteGround';

const lng = -114, lat = 51;
const footprint: GroundPoint[][] = [[[-5, -6], [5, -6], [5, 6], [-5, 6]]];
const module = (rotationYRad = 0): PlacedModuleBounds => ({ bounds: new THREE.Box3(new THREE.Vector3(-5, 0, -6), new THREE.Vector3(5, 8, 6)),
  transform: { position: [0, 0, 0], scale: [1, 1, 1], rotationYRad } });
const ground = (heightAt = (_lng: number, _lat: number) => 1031.3) => ({ status: 'ready', contains: () => true, heightAt });

function peakedGround(peakX: number, peakY: number) {
  const ll = (x: number, y: number): GroundPoint => [lng + x / metersPerDegLon(lat), lat + y / METERS_PER_DEG_LAT];
  const layout: SharedSiteGroundLayout = { boundaryId: 'site', boundaryUpdatedAt: 'now', sourceSignature: 'source',
    boundaryCoordinates: [[-12, -12], [12, -12], [12, 12], [-12, 12]].map(([x, y]) => ll(x, y)),
    grid: { west: ll(-12, -12)[0], south: ll(-12, -12)[1], columns: 7, rows: 7,
      stepLng: 4 / metersPerDegLon(lat), stepLat: 4 / METERS_PER_DEG_LAT } };
  const heights = Array<number>(49).fill(1000);
  heights[(peakY + 12) / 4 * 7 + (peakX + 12) / 4] = 1000.5;
  const snapshot = createSharedSiteGroundSnapshot(layout, heights, heights);
  if (!snapshot) throw new Error('Peak fixture must pass real shared-surface quality checks');
  return { status: 'ready', snapshot, contains: (x: number, y: number) => sharedSiteGroundContains(snapshot.boundaryCoordinates, x, y),
    heightAt: (x: number, y: number) => sampleSharedSiteGround(snapshot, x, y) };
}

describe('native building footprint contact', () => {
  it('uses native bounds rather than a larger plot and preserves source dimensions', () => {
    const source = module();
    const points = placedNativeFootprints([source], 0, [2, 3])[0];
    expect(points).toEqual([[-3, 9], [7, 9], [7, -3], [-3, -3]]);
    expect(source.bounds.getSize(new THREE.Vector3()).toArray()).toEqual([10, 8, 12]);
    expect(source.transform.scale).toEqual([1, 1, 1]);
  });
  it('matches the real nested Three transform for offset and both rotations', () => {
    const source = module(Math.PI / 5); source.transform.position = [4, 1, -2];
    const outer = new THREE.Group(); outer.position.set(2, -7, 0); outer.rotation.z = Math.PI / 3;
    const wrapper = new THREE.Group(); wrapper.rotation.x = Math.PI / 2; outer.add(wrapper);
    const instance = new THREE.Group(); instance.position.set(...source.transform.position); instance.rotation.y = source.transform.rotationYRad; wrapper.add(instance);
    outer.updateMatrixWorld(true);
    const expected = new THREE.Vector3(-5, 0, -6).applyMatrix4(instance.matrixWorld);
    const result = placedNativeFootprints([source], outer.rotation.z, [2, -7])[0][0];
    expect(result[0]).toBeCloseTo(expected.x, 10); expect(result[1]).toBeCloseTo(expected.y, 10);
  });
  it('keeps repeated ground-level modules separate and excludes upper roof modules', () => {
    const second = module(); second.transform.position[0] = 20;
    const roof = module(); roof.transform.position[1] = 8;
    expect(placedNativeFootprints([module(), second, roof], 0, [0, 0])).toHaveLength(2);
  });
  it('gives repeated legacy detached houses separate pads, with no yard cap', () => {
    const second = module(); second.transform.position[0] = 20;
    const footprints = placedNativeFootprints([module(), second], 0, [0, 0]);
    const result = resolveBuildingGroundContact(footprints, lng, lat, ground());
    if (result.status !== 'ready') throw new Error('Expected separate pads');
    for (let index = 0; index < result.indices.length; index += 3) {
      const xs = result.indices.slice(index, index + 3).map((vertex) => result.positions[vertex * 3]);
      expect(xs.every((x) => x <= 5) || xs.every((x) => x >= 15)).toBe(true);
    }
    expect(resolveBuildingGroundContact(footprints, lng, lat,
      ground((x) => 1031 + (x - lng) * metersPerDegLon(lat) * 0.15))).toEqual({ status: 'unresolved', reason: 'foundation_exceeds_3m' });
  });
  it('seats rigid native geometry on measured 1031.3 m with a 4 cm reveal', () => {
    const result = resolveBuildingGroundContact(footprint, lng, lat, ground());
    expect(result.status).toBe('ready');
    if (result.status !== 'ready') throw new Error('Expected foundation');
    expect(result.anchorHeight).toBeCloseTo(1031.34); expect(result.reliefM).toBe(0);
    for (let index = 0; index < result.positions.length; index += 3) {
      expect(Math.abs(result.positions[index])).toBeLessThanOrEqual(5);
      expect(Math.abs(result.positions[index + 1])).toBeLessThanOrEqual(6);
      expect(result.positions[index + 2]).toBeGreaterThanOrEqual(-0.061);
      expect(result.positions[index + 2]).toBeLessThanOrEqual(0);
    }
  });
  it('closes a 0.3 m sloped gap with separate terrain-following sides, without scaling', () => {
    const result = resolveBuildingGroundContact(footprint, lng, lat, ground((x) => 1031.3 + (x - lng) * metersPerDegLon(lat) * 0.03));
    if (result.status !== 'ready') throw new Error('Expected foundation');
    expect(result.anchorHeight).toBeCloseTo(1031.49, 6); expect(result.reliefM).toBeCloseTo(0.3, 6);
    const bottoms = result.positions.filter((_, index) => index % 6 === 2);
    expect(Math.min(...bottoms)).toBeCloseTo(-0.36, 6); expect(Math.max(...bottoms)).toBeCloseTo(-0.06, 6);
    expect(result.indices.every((index) => index < result.positions.length / 3)).toBe(true);
  });
  it('clears an off-centre interior terrain peak that all perimeter and centroid probes miss', () => {
    const measured = peakedGround(4, 4);
    const result = resolveBuildingGroundContact([[[-10, -10], [10, -10], [10, 10], [-10, 10]]], lng, lat, measured);
    expect(measured.snapshot.quality.maxSlope).toBeLessThan(0.18);
    expect(measured.snapshot.quality.maxLocalResidualM).toBe(0.5);
    if (result.status !== 'ready') throw new Error('Expected foundation');
    expect(result.anchorHeight).toBeCloseTo(1000.54, 6);
    expect(result.reliefM).toBeCloseTo(0.5, 6);
  });
  it('includes triangle-edge extrema on the footprint boundary when no grid vertex lies inside', () => {
    const measured = peakedGround(4, 0);
    const result = resolveBuildingGroundContact([[[4.1, -0.4], [6.1, -0.4], [6.1, 1.3], [4.1, 1.3]]], lng, lat, measured);
    if (result.status !== 'ready') throw new Error('Expected foundation');
    expect(result.anchorHeight).toBeCloseTo(1000.5275, 5);
    const contactPoints = Array.from({ length: result.positions.length / 6 }, (_, index) => result.positions.slice(index * 6, index * 6 + 3));
    expect(contactPoints.some(([x, y]) => Math.abs(x - 4.1) < 1e-6 && Math.abs(y) < 1e-6)).toBe(true);
    contactPoints.forEach((point, index) => {
      const next = contactPoints[(index + 1) % contactPoints.length];
      const x = point[0] + (next[0] - point[0]) * 0.37, y = point[1] + (next[1] - point[1]) * 0.37;
      const skirtHeight = result.anchorHeight + point[2] + (next[2] - point[2]) * 0.37;
      expect(skirtHeight).toBeCloseTo(measured.heightAt(lng + x / metersPerDegLon(lat), lat + y / METERS_PER_DEG_LAT)! - 0.02, 6);
    });
  });
  it('does not raise detached pads for a terrain peak in the yard between them', () => {
    const measured = peakedGround(0, 0);
    const pads: GroundPoint[][] = [[[-10, -2], [-6, -2], [-6, 2], [-10, 2]], [[6, -2], [10, -2], [10, 2], [6, 2]]];
    const result = resolveBuildingGroundContact(pads, lng, lat, measured);
    if (result.status !== 'ready') throw new Error('Expected separate pads');
    expect(result.anchorHeight).toBeCloseTo(1000.04, 6);
    expect(result.reliefM).toBeCloseTo(0, 6);
  });
  it('does not use a fallback while the common surface is pending or unavailable', () => {
    for (const status of ['sampling', 'unavailable']) expect(resolveBuildingGroundContact(footprint, lng, lat, { ...ground(), status })).toEqual({ status: 'unresolved', reason: 'ground_not_ready' });
  });
  it('recalculates from the next ready surface instead of retaining an earlier anchor', () => {
    const previous = resolveBuildingGroundContact(footprint, lng, lat, ground(() => 1022.89));
    const refined = resolveBuildingGroundContact(footprint, lng, lat, ground());
    expect(previous.status === 'ready' && previous.anchorHeight).toBeCloseTo(1022.93);
    expect(refined.status === 'ready' && refined.anchorHeight).toBeCloseTo(1031.34);
  });
  it('leaves outside-site grounding alone and rejects a partly unsupported footprint', () => {
    expect(resolveBuildingGroundContact(footprint, lng, lat, { ...ground(), contains: () => false })).toEqual({ status: 'outside' });
    expect(resolveBuildingGroundContact(footprint, lng, lat, { ...ground(), contains: (x) => x <= lng })).toEqual({ status: 'unresolved', reason: 'incomplete_footprint_ground' });
    expect(resolveBuildingGroundContact(footprint, lng, lat, { ...ground(), heightAt: () => null })).toEqual({ status: 'unresolved', reason: 'incomplete_footprint_ground' });
  });
  it('refuses a foundation over 3 m instead of stretching or inventing terrain', () => {
    expect(resolveBuildingGroundContact(footprint, lng, lat, ground((x) => 1031 + (x - lng) * metersPerDegLon(lat)))).toEqual({ status: 'unresolved', reason: 'foundation_exceeds_3m' });
  });
  it('converts an authored massing footprint to the same ENU frame and removes closure', () => {
    const ring = [[lng, lat], [lng + 10 / metersPerDegLon(lat), lat], [lng, lat + 12 / METERS_PER_DEG_LAT], [lng, lat]];
    const result = geographicFootprint(ring, lng, lat);
    expect(result).toHaveLength(3); expect(result[1][0]).toBeCloseTo(10); expect(result[2][1]).toBeCloseTo(12);
  });
  it('keeps a detailed contact error when its departing loading fallback cleans up', () => {
    let issues = updateBuildingGroundingIssues(new Map(), 'A', 'fallback', 'ground_not_ready');
    issues = updateBuildingGroundingIssues(issues, 'A', 'detail', 'foundation_exceeds_3m');
    issues = updateBuildingGroundingIssues(issues, 'A', 'fallback', null);
    expect(currentBuildingGroundingIssues(issues, new Set(['A']))).toEqual([{ buildingId: 'A', reason: 'foundation_exceeds_3m' }]);
    issues = updateBuildingGroundingIssues(issues, 'A', 'detail', null);
    expect(currentBuildingGroundingIssues(issues, new Set(['A']))).toEqual([]);
  });
  it('does not carry old-project issues into the new project while old cleanup is pending', () => {
    let issues = updateBuildingGroundingIssues(new Map(), 'A', 'old-renderer', 'incomplete_footprint_ground');
    issues = updateBuildingGroundingIssues(issues, 'B', 'new-renderer', 'ground_not_ready');
    expect(currentBuildingGroundingIssues(issues, new Set(['B']))).toEqual([{ buildingId: 'B', reason: 'ground_not_ready' }]);
    issues = updateBuildingGroundingIssues(issues, 'A', 'old-renderer', null);
    expect(currentBuildingGroundingIssues(issues, new Set(['B']))).toEqual([{ buildingId: 'B', reason: 'ground_not_ready' }]);
  });
});
