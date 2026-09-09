import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { bufferLineToPolygon, extractCenterline } from '@/utils/roadGeometry';
import { detectConnectedStreetIntersections } from '@/components/viewer/globe/streetGraphIntersections';
import { resolveStreetJunctionLayout } from '@/components/viewer/globe/streetJunctionGeometry';
import { CALGARY_LOCAL_PLACEMENT, streetCoordinateUpdate } from './streetPlacement';
import { snapStreetEndpoint, snapStreetEnds } from './streetSnapping';

const lonM = 111320 * Math.cos(51 * Math.PI / 180);
const ll = ([x, y]: number[]) => [-114 + x / lonM, 51 + y / 111320];
const xy = ([lng, lat]: number[]) => [(lng + 114) * lonM, (lat - 51) * 111320];
const street = (id: string, points: number[][]): SiteZone => ({ id, project_id: 'pilot', zone_type: 'road',
  coordinates: bufferLineToPolygon(points.map(ll), 16), properties: { ...CALGARY_LOCAL_PLACEMENT.properties, plan_centerline: points.map(ll),
    public_realm_lego: { schema_version: 1, family_id: 'street_local_public_realm', family_version: 1, kind: 'street', generator: 'street_section',
      archetype_id: 'calgary_local', variant_id: 'calgary_local_v0', profile_id: 'calgary-local-v1', profile_version: 1,
      appearance_kit_id: 'calgary_contemporary_native', target: { target_type: 'street_segment', row_width_m: 16 },
      catalog_fingerprint: 'a'.repeat(64), capability_fingerprint: 'b'.repeat(64), recipe_hash: 'c'.repeat(64) } },
  created_at: 'today', updated_at: 'today', sort_order: 0, color: '#777' });
const main = street('main', [[-50, 0], [50, 0]]);

describe('student street endpoint snapping', () => {
  it('turns an imprecise near-kerb endpoint into a renderable T and persists the same line', () => {
    const raw = [[0, -45], [2, -6]].map(ll);
    expect(detectConnectedStreetIntersections([main, street('arm', [[0, -45], [2, -6]])])).toHaveLength(0);
    const line = snapStreetEnds(raw, [main]);
    expect(xy(line[1])[0]).toBeCloseTo(0, 4);
    expect(xy(line[1])[1]).toBeCloseTo(0, 4);
    expect(line[0]).toEqual(raw[0]);
    const arm = street('arm', [[0, -45], [2, -6]]);
    const saved = JSON.parse(JSON.stringify({ ...arm, ...streetCoordinateUpdate(arm, bufferLineToPolygon(line, 16)) }));
    const nodes = detectConnectedStreetIntersections([main, saved]);
    expect(nodes).toHaveLength(1);
    expect(nodes[0].armCount).toBe(3);
    expect(resolveStreetJunctionLayout(nodes[0], [main, saved])).not.toBeNull();
    expect(extractCenterline(saved.coordinates)[1][0]).toBeCloseTo(line[1][0], 9);
    expect(raw[1]).toEqual(ll([2, -6]));
  });
  it('snaps either endpoint and handles rotated/reversed streets', () => {
    const rotate = ([x, y]: number[]) => [(x - y) / Math.sqrt(2), (x + y) / Math.sqrt(2)];
    const rotated = street('main', [[50, 0], [-50, 0]].map(rotate));
    const raw = [[2, -6], [0, -45]].map(rotate).map(ll);
    const snapped = snapStreetEndpoint(raw, 0, [rotated]);
    expect(Math.hypot(...xy(snapped[0]))).toBeLessThan(.01);
    expect(snapped[1]).toEqual(raw[1]);
  });
  it.each([{points:[[0,-45],[2,-18]]}, {points:[[0,-45],[25,-6]]}, {points:[[40,-45],[41,-6]]}])('keeps remote, oblique and near-corner endpoints untouched', ({points}) => {
    const line = points.map(ll);
    expect(snapStreetEnds(line, [main])).toBe(line);
  });
  it('does not snap bends, reference layers, buildings, or itself', () => {
    const line = [[0,-40],[1,-2],[40,-40]].map(ll);
    expect(snapStreetEndpoint(line, 1, [main])).toBe(line);
    const end = [[0,-45],[2,-6]].map(ll);
    expect(snapStreetEnds(end, [main], main.id)).toBe(end);
    expect(snapStreetEnds(end, [{ ...main, zone_type: 'building' }])).toBe(end);
    expect(snapStreetEnds(end, [{ ...main, properties: { ...main.properties, _imported_from: 'city roads' } }])).toBe(end);
  });
});
