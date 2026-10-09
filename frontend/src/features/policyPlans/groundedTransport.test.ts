import { describe, expect, it, vi } from 'vitest';
import * as THREE from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import { buildGroundedTransport, sampleGeographicSurface } from './groundedTransport';
import type { TransportSnapshot } from './transportVectors';

const data: TransportSnapshot = { type: 'FeatureCollection', network: '5a', retrieved: 'today', sources: {}, featureCount: 2, features: [
  { type: 'Feature', id: 'route', properties: { category: 'existing-pathway', source: 'test' }, geometry: { type: 'LineString', coordinates: [[-114.07, 51.05], [-114.069, 51.05]] } },
  { type: 'Feature', id: 'stop', properties: { category: 'service-stop', source: 'test' }, geometry: { type: 'Point', coordinates: [-114.07, 51.05] } },
] };
describe('grounded transportation', () => {
  it('rejects transient Calgary tile heights kilometres above or below the city without inventing ground', () => {
    const root = new THREE.Group(), shown = new THREE.Mesh(); root.add(shown);
    const ray = new THREE.Raycaster();
    for (const height of [-27836, 3400]) {
      const point = WGS84_ELLIPSOID.getCartographicToPosition(51.05 * Math.PI / 180, -114.07 * Math.PI / 180, height, new THREE.Vector3());
      vi.spyOn(ray, 'intersectObjects').mockReturnValue([{ object: shown, point, distance: 50000-height }]);
      expect(sampleGeographicSurface(-114.07, 51.05, [root], ray)).toBeNull();
    }
  });
  it('ignores cached tile hits detached from the visible tile root', () => {
    const root = new THREE.Group(), shown = new THREE.Mesh(), detached = new THREE.Mesh();
    root.add(shown);
    const point = (height: number) => WGS84_ELLIPSOID.getCartographicToPosition(51.05 * Math.PI / 180, -114.07 * Math.PI / 180, height, new THREE.Vector3());
    const ray = new THREE.Raycaster();
    vi.spyOn(ray, 'intersectObjects').mockReturnValue([
      { object: detached, point: point(3400), distance: 46600 },
      { object: shown, point: point(1030), distance: 48970 },
    ]);
    expect(sampleGeographicSurface(-114.07, 51.05, [root], ray)).toBeCloseTo(1030, 4);
  });
  it('densifies routes and follows location-specific elevations without a camera or site datum', () => {
    const result = buildGroundedTransport(data, 'test', 970);
    expect(result.nodes.length).toBeGreaterThan(5);
    expect(new Set(result.chunks.flatMap(chunk => chunk.nodes))).toEqual(new Set(result.nodes));
    for (const node of result.nodes) result.setHeight(node, 1000 + (node.lng + 114.07) * 10000);
    for (const node of result.nodes) {
      const world = node.position.clone().add(result.origin);
      expect(WGS84_ELLIPSOID.getPositionElevation(world)).toBeCloseTo(1000 + (node.lng + 114.07) * 10000 + .2, 4);
    }
    // Geographic coordinates remain grounded, but map ink must stay readable
    // when the Google mesh lies above a sampled line or stop triangle.
    expect(result.objects.every(o => !(o.material as THREE.Material).depthTest)).toBe(true);
    expect(result.objects.every(o => !(o.material as THREE.Material).depthWrite)).toBe(true);
    expect(result.objects[0].userData.transportIds.every((id: string) => id === 'route')).toBe(true);
    expect(result.objects[1].userData.transportIds.every((id: string) => id === 'stop')).toBe(true);
    result.dispose();
  });
  it('hides unknown ground, retains measured locations on missing tiles, and drapes stop edges too', () => {
    const result = buildGroundedTransport(data, 'test', 970);
    expect(result.nodes.every(n => n.height === null)).toBe(true);
    expect(result.objects[0].geometry.getAttribute('instanceGrounded').array.every(n => n === 0)).toBe(true);
    const stop = result.objects[1];
    expect(stop.geometry.getAttribute('position').array.every(n => n === 0)).toBe(true);
    result.nodes.forEach(n => result.setHeight(n, 1030));
    expect(result.objects[0].geometry.getAttribute('instanceGrounded').array.every(n => n === 1)).toBe(true);
    const before = result.nodes[0].position.clone();
    result.setHeight(result.nodes[0], null);
    expect(result.nodes[0].position.equals(before)).toBe(true);
    expect(stop.geometry.getAttribute('position').count).toBeGreaterThan(20);
    result.dispose();
  });
  it('does not create zero-length line instances from duplicate source coordinates', () => {
    const source = { ...data, features: [{ ...data.features[0], geometry: { type: 'LineString' as const, coordinates: [[-114.07, 51.05], [-114.07, 51.05]] } }] };
    const result = buildGroundedTransport(source, 'test', 970);
    expect(result.objects).toHaveLength(0);
    result.dispose();
  });
  it('casts along geographic vertical against visible ground, independent of camera direction', () => {
    const world = WGS84_ELLIPSOID.getCartographicToPosition(51.05 * Math.PI / 180, -114.07 * Math.PI / 180, 1100, new THREE.Vector3());
    const normal = WGS84_ELLIPSOID.getCartographicToNormal(51.05 * Math.PI / 180, -114.07 * Math.PI / 180, new THREE.Vector3());
    const plane = new THREE.Mesh(new THREE.PlaneGeometry(100, 100), new THREE.MeshBasicMaterial());
    plane.position.copy(world); plane.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), normal); plane.updateMatrixWorld(true);
    expect(sampleGeographicSurface(-114.07, 51.05, [plane])).toBeCloseTo(1100, 5);
    plane.visible = false;
    expect(sampleGeographicSurface(-114.07, 51.05, [plane])).toBeNull();
  });
});
