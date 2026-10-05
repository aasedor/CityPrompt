import { installPolicyMapFetch } from './policyMapFetch.test-support';
import { describe, expect, it } from 'vitest';
import booleanPointInPolygon from '@turf/boolean-point-in-polygon';
import { loadRileyPolicy, policyCoverageProblem, policyOverlay, readPolicyPreferences, selectPolicySite, type PolicySnapshot } from './rileyPolicy';

installPolicyMapFetch();

const site = [[-114.09789,51.05755],[-114.09489,51.05756],[-114.09488,51.05943],[-114.08762,51.05944],[-114.08766,51.05455],[-114.09791,51.05454]];

describe('Riley policy geography', () => {
  it('preserves the nine official urban form colours and closed finite rings', async () => {
    const data = await loadRileyPolicy();
    expect(data.features).toHaveLength(362);
    expect(new Set(data.features.map(feature => feature.properties.color))).toEqual(new Set(['#e4002b','#ed9d4d','#fedb00','#fff4b2','#a5192e','#a9c23f','#70a355','#4db69f','#b2e0d5']));
    expect(new Set(data.features.map(feature => feature.id)).size).toBe(data.features.length);
    for (const feature of data.features) for (const ring of feature.geometry.coordinates) {
      expect(ring.length).toBeGreaterThanOrEqual(4);
      expect(ring[0]).toEqual(ring[ring.length-1]);
      expect(ring.every(([x,y]) => Number.isFinite(x) && Number.isFinite(y) && x > -114.14 && x < -114.06 && y > 51.04 && y < 51.07)).toBe(true);
    }
  });
  it('retains street openings at independent City centreline check points', async () => {
    const data = await loadRileyPolicy();
    for (const point of [[-114.1105075,51.0572362],[-114.1253902,51.0569095],[-114.0947104,51.0525233]]) {
      expect(data.features.some(feature => booleanPointInPolygon(point, feature.geometry))).toBe(false);
    }
  });
  it('clips real Riley polygons to a concave site without changing the snapshot', async () => {
    const data = await loadRileyPolicy(); const before = JSON.stringify(data);
    const selected = selectPolicySite(data, site);
    expect(selected.hasCoverage).toBe(true); expect(selected.partial).toBe(false);
    expect(selected.features.length).toBeGreaterThan(5);
    const categories = new Set(selected.features.map(feature => feature.properties.category));
    expect(categories.has('Parks and Open Space')).toBe(true);
    expect(categories.has('Neighbourhood Connector')).toBe(true);
    const overlay = policyOverlay(data, selected.features);
    for (const district of overlay.districts) {
      expect(booleanPointInPolygon(district.anchor, { type: 'Polygon', coordinates: [site.concat([site[0]])] })).toBe(true);
      expect(booleanPointInPolygon(district.anchor, { type: 'Polygon', coordinates: district.polygon })).toBe(true);
    }
    expect(JSON.stringify(data)).toBe(before);
  });
  it('rejects sites inside the bounding rectangle but outside the actual plan', async () => {
    const outside = [[-114.070,51.065],[-114.069,51.065],[-114.069,51.066],[-114.070,51.066]];
    expect(policyCoverageProblem(outside)).toBeNull();
    expect(selectPolicySite(await loadRileyPolicy(), outside).hasCoverage).toBe(false);
  });
  it('detects partial coverage and preserves polygon holes', () => {
    const data: PolicySnapshot = { snapshot: 'test', bounds: [0,0,10,10], boundary: { type: 'Polygon', coordinates: [[[0,0],[10,0],[10,10],[0,10],[0,0]]] }, features: [{
      type: 'Feature', id: 'park', properties: { category: 'Park', color: '#70a355' }, geometry: { type: 'Polygon', coordinates: [
        [[1,1],[9,1],[9,9],[1,9],[1,1]], [[3,3],[3,7],[7,7],[7,3],[3,3]],
      ] },
    }] };
    const selected = selectPolicySite(data, [[-1,-1],[11,-1],[11,11],[-1,11]]);
    expect(selected.partial).toBe(true);
    expect(selected.features).toHaveLength(1);
    expect(selected.features[0].geometry.coordinates).toHaveLength(2);
    expect(booleanPointInPolygon([5,5], selected.features[0].geometry)).toBe(false);
  });
  it('requires a valid site and safely reads per-project choices', () => {
    expect(policyCoverageProblem([])).toContain('Draw a site');
    expect(policyCoverageProblem([[0,0],[1,0],[1,1]])).toContain('covers Riley');
    expect(readPolicyPreferences('null')).toEqual({ enabled: false, opacity: .7, clipToSite: false });
    expect(readPolicyPreferences('{broken')).toEqual(readPolicyPreferences(null));
    expect(readPolicyPreferences('{"enabled":"true","opacity":2}')).toEqual({ enabled: false, opacity: 1, clipToSite: false });
  });
});
