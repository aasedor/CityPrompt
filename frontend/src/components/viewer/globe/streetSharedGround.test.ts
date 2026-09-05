import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { applySharedStreetGround, createStreetGroundOffset, seatStreetFixture, sharedStreetStationTerrain } from './streetSharedGround';

const longitude = -114.1, latitude = 51;
const east = metersPerDegLon(latitude);
const heightAt = (lng: number, lat: number) => {
  const x = (lng - longitude) * east, y = (lat - latitude) * METERS_PER_DEG_LAT;
  return 1000 + x * 0.07 + y * 0.04 + x * y * 0.001;
};
const mesh = (points: number[]) => new THREE.BufferGeometry().setAttribute('position', new THREE.Float32BufferAttribute(points, 3));

describe('shared street and node terrain field', () => {
  it('splits shifted street surfaces at the shared diagonal so triangle interiors keep their authored lift', () => {
    // All edges are below the old 4 m subdivision threshold, but this face
    // crosses the shared SW–NE break. A roundabout uses the same local shift.
    const source = mesh([-8.5, 6.5, 0.1, -5.5, 6.5, 0.1, -8.5, 8.5, 0.1]);
    const grid = { westX: 0, southY: 0, stepX: 4, stepY: 4, columns: 2, rows: 2 };
    const offsetAt = (x: number, y: number) => Math.min(x, y) / 4;
    expect(applySharedStreetGround(source, offsetAt, 9, -6, grid)).toBe(true);
    const position = source.getAttribute('position');
    const indices = source.index ? Array.from(source.index.array) : Array.from({ length: position.count }, (_, i) => i);
    expect(indices.length).toBeGreaterThan(3);
    for (let i = 0; i < indices.length; i += 3) {
      const triangle = indices.slice(i, i + 3);
      const x = triangle.reduce((sum, index) => sum + position.getX(index), 0) / 3 + 9;
      const y = triangle.reduce((sum, index) => sum + position.getY(index), 0) / 3 - 6;
      const z = triangle.reduce((sum, index) => sum + position.getZ(index), 0) / 3;
      expect(z).toBeCloseTo(offsetAt(x, y) + 0.1, 5);
    }
    expect(grid.westX).toBe(0); expect(grid.southY).toBe(0);
    source.dispose();
  });

  it('gives a street and junction in different frames the same seam height and preserves lane lifts', () => {
    const node = mesh([11, -4, 0.1, 11, 4, 0.1, 10, 0, 0.1]);
    const ribbon = mesh([41, -4, 0.1, 41, 4, 0.1, 42, 0, 0.1]);
    const nodeFrame = heightAt(longitude, latitude);
    const roadLng = longitude - 30 / east;
    const roadFrame = heightAt(roadLng, latitude);
    expect(applySharedStreetGround(node, createStreetGroundOffset(longitude, latitude, nodeFrame, heightAt))).toBe(true);
    expect(applySharedStreetGround(ribbon, createStreetGroundOffset(roadLng, latitude, roadFrame, heightAt))).toBe(true);
    for (const i of [0, 1]) {
      const nodeZ = node.getAttribute('position').getZ(i) + nodeFrame;
      const roadZ = ribbon.getAttribute('position').getZ(i) + roadFrame;
      expect(nodeZ).toBeCloseTo(roadZ, 5);
      expect(nodeZ).toBeCloseTo(heightAt(longitude + 11 / east, latitude + (i ? 4 : -4) / METERS_PER_DEG_LAT) + 0.1, 5);
    }
    node.dispose(); ribbon.dispose();
  });

  it('samples every station side from the shared field and seats rigid fixtures individually', () => {
    const offset = createStreetGroundOffset(longitude, latitude, 1000, heightAt);
    const stations = sharedStreetStationTerrain([{ x: 10, y: 0 }], [{ x: 0, y: 1 }], 8, offset)!;
    expect(stations[0].centerZ).toBeCloseTo(0.7);
    expect(stations[0].leftZ).toBeCloseTo(1.1);
    expect(stations[0].rightZ).toBeCloseTo(0.3);
    const pose = { x: 10, y: 4, z: 0.245, yawRad: 0.3, heightM: 5 };
    expect(seatStreetFixture(pose, offset)).toEqual({ ...pose, z: pose.z + offset(10, 4)! });
    expect(pose.z).toBe(0.245);
  });

  it('does not partially modify or fall back when the shared surface is unavailable', () => {
    const source = mesh([0, 0, 0.1, 2, 0, 0.1, 0, 2, 0.1]);
    const before = Array.from(source.getAttribute('position').array);
    expect(applySharedStreetGround(source, (x) => x > 1 ? null : 4)).toBe(false);
    expect(Array.from(source.getAttribute('position').array)).toEqual(before);
    expect(sharedStreetStationTerrain([{ x: 0, y: 0 }], [{ x: 0, y: 1 }], 8, () => null)).toBeNull();
    expect(seatStreetFixture({ x: 0, y: 0, z: 1 }, () => null)).toBeNull();
    source.dispose();
  });
});
