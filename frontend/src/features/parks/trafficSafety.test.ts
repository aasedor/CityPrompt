import { describe, expect, it } from 'vitest';
import { Matrix4, Vector3 } from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import { detailPlacementMatrix } from './detailInstances';
import { DETAIL_CATALOGUE } from './detailCatalogue';
import supplied from './trafficSafetyCatalogue.json';

describe('traffic safety metre and datum contract', () => {
  const item = { lng: -114, lat: 51, height: 1040, angle: 0 };
  const inverse = WGS84_ELLIPSOID.getEastNorthUpFrame(51*Math.PI/180, -114*Math.PI/180, 1040, new Matrix4()).invert();
  it('places authored paint 4 mm above the road, without the furniture lift', () => {
    const matrix = detailPlacementMatrix(item, inverse, [0,0,0], 0);
    const paint = new Vector3(0, .004, 0).applyMatrix4(matrix);
    expect(paint.z).toBeCloseTo(.004, 6);
    expect(new Vector3(0,0,0).applyMatrix4(matrix).z).toBeCloseTo(0, 6);
  });
  it('preserves old saved furniture lift and rigid axes', () => {
    const matrix = detailPlacementMatrix(item, inverse);
    expect(new Vector3().applyMatrix4(matrix).z).toBeCloseTo(.084, 6);
    expect(new Vector3(6,0,0).transformDirection(matrix).x).toBeCloseTo(1, 6);
    expect(new Vector3(0,0,1).transformDirection(matrix).y).toBeCloseTo(-1, 6);
  });
  it('resolves all approved variants to fixed-scale, hash-bound assets in five groups', () => {
    const ids = new Set(supplied.map(a=>a.id));
    const rows = DETAIL_CATALOGUE.filter(a => ids.has(a.id));
    expect(rows).toHaveLength(56);
    expect(new Set(rows.map(a=>a.id)).size).toBe(56);
    expect(new Set(rows.map(a=>a.safety!.group)).size).toBe(5);
    for (const row of rows) {
      expect(row.datumLift).toBe(0);
      expect(row.safety!.sha256).toMatch(/^[a-f0-9]{64}$/);
      expect(row.safety!.transforms).toEqual(['translation','yaw']);
    }
    expect(rows.filter(a=>a.safety!.group==='Crosswalks')).toHaveLength(24);
    expect(rows.filter(a=>a.safety!.group==='Curb bulbs')).toHaveLength(12);
  });
});
