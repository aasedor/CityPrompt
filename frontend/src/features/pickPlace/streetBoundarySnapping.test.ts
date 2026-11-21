import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { STREET_ASSETS } from './assetRegistry';
import { streetDrawingGeometry } from './streetDrawingGeometry';
import { placementProblem } from './geometry';
import { streetRouteProblem } from './streetPlacement';
import { snapStreetToBoundary } from './streetBoundarySnapping';
import { BRT_VARIANT } from '@/components/viewer/globe/brtStreetProgram';
import { streetConnectionProblem } from './streetConnectionProblem';
import { modularBridgeProgramFor } from '@/components/viewer/globe/modularBridgeProgram';

const sx = 111320 * Math.cos(51 * Math.PI / 180);
const ll = (x: number, y: number) => [-114 + x / sx, 51 + y / 111320];
const xy = (p: number[]) => [(p[0] + 114) * sx, (p[1] - 51) * 111320];
const boundary = { id: 'site', zone_type: 'site_boundary', coordinates: [ll(0, 0), ll(300, 0), ll(300, 300), ll(0, 300)] } as SiteZone;
const props = { width: 20, pick_place_street_section: 'test' };

describe('street boundary entrances', () => {
  // Bridge drawings fit their structural span first. A 150 m gesture cannot
  // promise a contained flyover whose minimum supported span exceeds this site.
  // Their supported fit and unfit-parcel rejection are covered in the bridge suite.
  it.each(STREET_ASSETS.filter(a=>!modularBridgeProgramFor(a.model.variantId)))('$label fits flush at each edge with its full native width', asset => {
    for (const start of [ll(0, 150), ll(300, 150), ll(150, 0), ll(150, 300)]) {
      const result = streetDrawingGeometry([start, ll(150, 150)], asset.properties, [boundary]);
      expect(placementProblem(result.coordinates, [], boundary)).toBeNull();
      expect(streetRouteProblem(result.coordinates, asset.sectionWidth, result.properties.plan_route_controls as number[][])).toBeNull();
      expect(Math.hypot(...xy(start).map((n, i) => n - xy((result.properties.plan_centerline as number[][])[0])[i]))).toBeLessThan(.1);
    }
  });
  it('snaps a slightly outside click and adds a full-width normal approach for an oblique route', () => {
    const points = [ll(-2, 100), ll(160, 170)];
    const result = streetDrawingGeometry(points, props, [boundary]);
    const controls = result.properties.plan_route_controls as number[][];
    expect(controls).toHaveLength(3);
    expect(xy(controls[0])[0]).toBeCloseTo(.08);
    expect(xy(controls[0])[1]).toBeCloseTo(100);
    expect(xy(controls[1])[1]).toBeCloseTo(100);
    expect(controls[controls.length - 1]).toEqual(points[1]);
    expect(placementProblem(result.coordinates, [], boundary)).toBeNull();
    expect(streetRouteProblem(result.coordinates, 20, controls)).toBeNull();
    expect(points[0]).toEqual(ll(-2, 100));
  });
  it('handles reversed ring order, rotated boundaries, both ends, and preview/save parity', () => {
    const rotate = (p: number[]) => { const [x, y] = xy(p); return ll(x * .8 - y * .6, x * .6 + y * .8); };
    const site = { ...boundary, coordinates: boundary.coordinates.map(rotate).reverse() };
    const points = [ll(0, 100), ll(300, 170)].map(rotate);
    const draft = streetDrawingGeometry(points, props, [site]);
    expect(draft).toEqual(streetDrawingGeometry(points, props, [site]));
    expect(placementProblem(draft.coordinates, [], site)).toBeNull();
    expect(streetRouteProblem(draft.coordinates, 20, draft.properties.plan_route_controls as number[][])).toBeNull();
  });
  it('keeps an almost-normal road straight across slightly skewed site edges so its middle can host junctions', () => {
    const site = { ...boundary, coordinates: [[0, 0], [150, 2], [150, 77], [0, 75]].map(([x,y]) => ll(x,y)) };
    const asset = STREET_ASSETS.find(row => row.model.variantId === 'student_quiet_residential_street_v1')!;
    const points = [ll(85, 6), ll(85, 71)];
    const result = streetDrawingGeometry(points, asset.properties, [site]);
    const controls = result.properties.plan_route_controls as number[][];
    expect(controls).toHaveLength(2);
    expect(xy(controls[0])[0]).toBeCloseTo(85, 5);
    expect(xy(controls[1])[0]).toBeCloseTo(85, 5);
    expect(placementProblem(result.coordinates, [], site)).toBeNull();
    expect(streetRouteProblem(result.coordinates, 18, controls)).toBeNull();
    const host = { id:'host', zone_type:'road', ...result } as SiteZone;
    for (const far of [ll(128, 63), ll(128, 13)]) {
      const branch = streetDrawingGeometry([ll(85, 38), far], asset.properties, [site,host]);
      expect(streetConnectionProblem({id:'branch',zone_type:'road',...branch} as SiteZone,[host])).toBeNull();
    }
  });
  it('retains strict containment for remote clicks, narrow corners, parallel routes and short approaches', () => {
    for (const points of [[ll(-10, 100), ll(150, 100)], [ll(0, 0), ll(150, 150)],
      [ll(0, 100), ll(0, 200)], [ll(0, 100), ll(10, 130)]]) {
      expect(snapStreetToBoundary(points, 20, boundary, props)).toEqual(points);
      expect(placementProblem(streetDrawingGeometry(points, props, [boundary]).coordinates, [], boundary)).not.toBeNull();
    }
  });
  it('does not allow a street to cut across a concave recess', () => {
    const site = { ...boundary, coordinates: [[0, 0], [300, 0], [300, 300], [180, 300], [180, 60], [120, 60], [120, 300], [0, 300]].map(([x, y]) => ll(x, y)) };
    const points = [ll(0, 150), ll(300, 150)];
    expect(snapStreetToBoundary(points, 20, site, props)).toEqual(points);
    expect(placementProblem(streetDrawingGeometry(points, props, [site]).coordinates, [], site)).not.toBeNull();
  });
  it('keeps rigid transit corridors straight, never inserting a curved approach', () => {
    const properties = { ...props, road_selected_variant_id: BRT_VARIANT };
    const result = streetDrawingGeometry([ll(-1, 100), ll(180, 102)], properties, [boundary]);
    const controls = result.properties.plan_route_controls as number[][];
    expect(controls).toHaveLength(2);
    expect(xy(controls[0])[1]).toBeCloseTo(102);
    expect(placementProblem(result.coordinates, [], boundary)).toBeNull();
    const oblique = [ll(0, 100), ll(180, 150)];
    expect(snapStreetToBoundary(oblique, 20, boundary, properties)).toEqual(oblique);
  });
  it('preserves interior routes, explicitly authored public-road extensions, and inactive boundaries', () => {
    const points = [ll(50, 100), ll(200, 100)];
    expect(snapStreetToBoundary(points, 20, boundary, props)).toEqual(points);
    const outside = [ll(-2, 100), ll(150, 100)];
    expect(snapStreetToBoundary(outside, 20, boundary, { ...props, connect_to_public_road: true })).toEqual(outside);
    expect(streetDrawingGeometry(outside, props, [{ ...boundary, is_active_boundary: false }]).properties.plan_route_controls).toEqual(outside);
  });
});
