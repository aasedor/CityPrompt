import { afterEach, describe, expect, it } from 'vitest';
import { Matrix4, Vector3 } from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import { detailPlacementMatrix, type DetailPlacement } from './detailInstances';
import { registerDetailWalkSurfaces, detailWalkGround, type DetailWalkSurface } from './detailWalking';

const cleanups: (() => void)[] = [];
afterEach(() => { cleanups.splice(0).forEach(cleanup => cleanup()); });
const placement = { id: 'ramp', lng: -114, lat: 51, height: 1000, angle: 0 };
const ramp: DetailWalkSurface = { type: 'profile', width: 1.8, stations: [
  { z: -5.1, height: 0 }, { z: -3.6, height: 0 }, { z: 3.6, height: .6 }, { z: 5.1, height: .6 },
] };
function point(item: DetailPlacement, x: number, z: number, offset?: number[]) {
  const world = new Vector3(x, 0, z).applyMatrix4(detailPlacementMatrix(item, new Matrix4(), offset));
  const geo = WGS84_ELLIPSOID.getPositionToCartographic(world, { lat: 0, lon: 0, height: 0 });
  return { lng: geo.lon * 180 / Math.PI, lat: geo.lat * 180 / Math.PI };
}
function height(p: {lng:number;lat:number}, previous = 1000, base = 1000) {
  return detailWalkGround(p.lng, p.lat, base, previous);
}
describe('placed detail walking', () => {
  it('follows ramp and landings using rendered rotation, offsets and lift', () => {
    const rotated = { ...placement, angle: 67 }, offset = [2, .1, -3];
    cleanups.push(registerDetailWalkSurfaces(ramp, [rotated], offset));
    expect(height(point(rotated, 0, -4, offset))).toBeCloseTo(1000.184, 3);
    expect(height(point(rotated, 0, 0, offset), 1000.4)).toBeCloseTo(1000.484, 3);
    expect(height(point(rotated, 0, 4, offset), 1000.7)).toBeCloseTo(1000.784, 3);
    expect(height(point(rotated, .91, 0, offset), 1000.4)).toBe(1000);
    expect(height(point(rotated, 0, 5.11, offset), 1000.7)).toBe(1000);
  });
  it('climbs treads without interpolating across a vertical riser', () => {
    const stairs: DetailWalkSurface = { type: 'profile', width: 2, stations: [
      {z:-.6,height:.15},{z:-.3,height:.15},{z:-.3,height:.3},{z:0,height:.3},
      {z:0,height:.45},{z:.3,height:.45},{z:.3,height:.6},{z:.6,height:.6},
    ] };
    cleanups.push(registerDetailWalkSurfaces(stairs, [placement]));
    let feet = 1000;
    for (const [z, expected] of [[-.45,1000.234],[-.15,1000.384],[.15,1000.534],[.45,1000.684]]) {
      feet = height(point(placement,0,z), feet);
      expect(feet).toBeCloseTo(expected, 3);
    }
    expect(height(point(placement,0,.61), feet)).toBe(1000);
  });
  it('keeps walking anywhere without teleporting onto raised sides or distant surfaces', () => {
    cleanups.push(registerDetailWalkSurfaces(ramp, [placement]));
    expect(height(point(placement,0,4))).toBe(1000);
    expect(height({lng:0,lat:0})).toBe(1000);
    expect(height(point(placement,0,4),1000.6)).toBeCloseTo(1000.684,3);
    expect(height(point(placement,0,4),1000.6,1010)).toBe(1010);
  });
  it('excludes cursor previews and removes surfaces when deleted or unmounted', () => {
    cleanups.push(registerDetailWalkSurfaces(ramp, [{...placement,id:'detail-preview:cursor'}]));
    expect(height(point(placement,0,0),1000.3)).toBe(1000);
    const remove = registerDetailWalkSurfaces(ramp,[placement]);
    expect(height(point(placement,0,0),1000.3)).toBeCloseTo(1000.384,3);
    remove();
    expect(height(point(placement,0,0),1000.3)).toBe(1000);
  });
  it('descends and steps off without retaining an inherited elevated ground height', () => {
    cleanups.push(registerDetailWalkSurfaces(ramp,[placement]));
    const previous = point(placement,0,4);
    const next = point(placement,0,3);
    expect(detailWalkGround(next.lng,next.lat,1000.684,1000.684,previous)).toBeCloseTo(1000.634,3);
    const outside = point(placement,0,5.2);
    expect(detailWalkGround(outside.lng,outside.lat,1000.684,1000.684,previous)).toBe(1000);
  });
});
