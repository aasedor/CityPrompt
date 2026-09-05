import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { createSharedSiteGroundLayout, createSharedSiteGroundSnapshot, sampleSharedSiteGround,
  sharedSiteGroundContains, sharedSiteGroundGridPoint, sharedSiteGroundSourceSignature,
  validateSharedSiteGroundPass } from './sharedSiteGround';

const ll = (x: number, y: number): [number, number] => [-114 + x / metersPerDegLon(51), 51 + y / METERS_PER_DEG_LAT];
const boundary = (ring = [[0, 0], [24, 0], [24, 20], [0, 20]]): SiteZone => ({
  id: 'site', project_id: 'project', zone_type: 'site_boundary', coordinates: ring.map(([x, y]) => ll(x, y)),
  properties: { community_3d_mask_existing_tiles: false, terrain_elevation_m: 900 }, is_active_boundary: true,
  color: '#888888', sort_order: 0, created_at: '2026-09-04', updated_at: '2026-09-04',
});
function sloped() {
  const layout = createSharedSiteGroundLayout(boundary())!;
  const heights = Array.from({ length: layout.grid.columns * layout.grid.rows }, (_, i) => {
    const [lng, lat] = sharedSiteGroundGridPoint(layout, i);
    return 1030 + (lng + 114) * metersPerDegLon(51) * 0.07 + (lat - 51) * METERS_PER_DEG_LAT * 0.02;
  });
  return { layout, heights };
}

describe('shared retained-site terrain', () => {
  it('retains actual sloped tile heights across both triangles and boundary edges', () => {
    const { layout, heights } = sloped();
    const snapshot = createSharedSiteGroundSnapshot(layout, heights, heights)!;
    expect(snapshot.verticalReference).toBe('WGS84_ellipsoid');
    expect(snapshot.quality.stablePasses).toBe(2);
    for (const [x, y] of [[0, 0], [24, 20], [3, 1], [1, 3], [8.25, 12.4]]) {
      expect(sampleSharedSiteGround(snapshot, ...ll(x, y))).toBeCloseTo(1030 + x * 0.07 + y * 0.02, 5);
    }
    expect(snapshot.heights).toEqual(heights);
    expect(sampleSharedSiteGround(snapshot, ...ll(-1, 2))).toBeNull();
  });
  it('keeps a concave notch outside its domain and requires its support cells to be measured', () => {
    const site = boundary([[0, 0], [24, 0], [24, 20], [16, 20], [16, 8], [8, 8], [8, 20], [0, 20]]);
    const layout = createSharedSiteGroundLayout(site)!;
    const heights = Array<number>(layout.grid.columns * layout.grid.rows).fill(1030);
    const snapshot = createSharedSiteGroundSnapshot(layout, heights, heights)!;
    expect(sharedSiteGroundContains(layout.boundaryCoordinates, ...ll(12, 14))).toBe(false);
    expect(sampleSharedSiteGround(snapshot, ...ll(12, 14))).toBeNull();
    expect(sampleSharedSiteGround(snapshot, ...ll(4, 14))).toBe(1030);
    expect(sampleSharedSiteGround(snapshot, ...ll(12, 4))).toBe(1030);
    const missing: Array<number | null> = [...heights]; missing[0] = null;
    expect(createSharedSiteGroundSnapshot(layout, heights, missing)).toBeNull();
  });
  it('rejects missing, nonfinite, root-tile and isolated object hits without inventing ground', () => {
    const { layout, heights } = sloped();
    for (const value of [null, NaN, Infinity, -28000, 1050]) {
      const bad: Array<number | null> = [...heights]; bad[layout.grid.columns + 1] = value;
      expect(validateSharedSiteGroundPass(layout, bad).valid).toBe(false);
      expect(createSharedSiteGroundSnapshot(layout, heights, bad)).toBeNull();
    }
    expect(validateSharedSiteGroundPass(layout, heights.slice(1)).reason).toBe('missing_samples');
  });
  it('requires stable complete passes and produces a new signature when the surface changes', () => {
    const { layout, heights } = sloped();
    expect(createSharedSiteGroundSnapshot(layout, heights, heights.map((z) => z + 0.09))).toBeNull();
    const first = createSharedSiteGroundSnapshot(layout, heights, heights)!;
    const second = createSharedSiteGroundSnapshot(layout, heights, heights.map((z) => z + 0.04))!;
    expect(second.signature).not.toBe(first.signature);
    expect(second.quality.maxPassDeltaM).toBeCloseTo(0.04);
    const changed = boundary(); changed.is_active_boundary = false;
    expect(sharedSiteGroundSourceSignature(changed)).not.toBe(layout.sourceSignature);
    changed.is_active_boundary = true; changed.updated_at = '2026-09-05';
    expect(sharedSiteGroundSourceSignature(changed)).not.toBe(layout.sourceSignature);
  });
  it('bounds the grid while retaining declared metric spacing, and refuses excessively large or invalid sites', () => {
    const pilot = createSharedSiteGroundLayout(boundary([[0, 0], [62, 0], [62, 84], [0, 84]]))!;
    expect(pilot.grid.columns * pilot.grid.rows).toBe(910);
    expect(pilot.grid.stepLat * METERS_PER_DEG_LAT).toBeLessThanOrEqual(2.5);
    const layout = createSharedSiteGroundLayout(boundary([[0, 0], [180, 0], [180, 130], [0, 130]]))!;
    expect(layout.grid.columns * layout.grid.rows).toBeLessThanOrEqual(1200);
    expect(layout.grid.stepLat * METERS_PER_DEG_LAT).toBeGreaterThan(4);
    expect(createSharedSiteGroundLayout(boundary([[0, 0], [10000, 0], [10000, 10000], [0, 10000]]))).toBeNull();
    expect(createSharedSiteGroundLayout(boundary([[0, 0], [NaN, 0], [0, 20]]))).toBeNull();
  });
  it('uses triangle interpolation consistently rather than a bilinear saddle', () => {
    const layout = createSharedSiteGroundLayout(boundary([[0, 0], [2, 0], [2, 2], [0, 2]]))!;
    const heights = [1000, 1000.3, 1000.3, 1000];
    const snapshot = createSharedSiteGroundSnapshot(layout, heights, heights)!;
    expect(sampleSharedSiteGround(snapshot, ...ll(1, 1))).toBeCloseTo(1000, 6);
  });
});
