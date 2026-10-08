import { describe, expect, it } from 'vitest';
import fiveAJson from '../../../public/policy-maps/transport-vectors-v1/5a.geojson?raw';
import transitJson from '../../../public/policy-maps/transport-vectors-v1/transit.geojson?raw';
import { parseTransportSnapshot, transportNetworkForMap, transportStyle } from './transportVectors';

describe('transportation vector snapshots', () => {
  it('ships complete validated snapshots with resolvable official source attribution', () => {
    for (const network of ['transit', '5a'] as const) {
      const value = JSON.parse(network === 'transit' ? transitJson : fiveAJson);
      const snapshot = parseTransportSnapshot(value, network);
      expect(value.sourceFeatureCount).toBe(network === 'transit' ? 189 : 34779);
      for (const feature of snapshot.features) {
        expect(snapshot.sources[feature.properties.source]?.url).toMatch(/^https:\/\/services1.arcgis.com\/AVP60cs0Q9PEA8rH\//);
      }
    }
  });
  it('shares the transit source across MDP and CTP and leaves other maps unchanged', () => {
    expect(transportNetworkForMap('mdp-2')).toBe('transit');
    expect(transportNetworkForMap('ctp-2')).toBe('transit');
    expect(transportNetworkForMap('ctp-1')).toBe('5a');
    expect(transportNetworkForMap('ctp-3')).toBeUndefined();
  });
  it('keeps existing and proposed routes visually distinct', () => {
    expect(transportStyle('existing-pathway').dashed).toBe(false);
    expect(transportStyle('proposed-pathway').dashed).toBe(true);
    expect(transportStyle('proposed-bikeway').color).not.toBe(transportStyle('proposed-pathway').color);
  });
  it('rejects truncated or malformed data instead of silently drawing a partial network', () => {
    const snapshot = { type: 'FeatureCollection', network: 'transit', retrieved: '2026-10-07', sources: {}, featureCount: 1,
      features: [{ type: 'Feature', id: 'hub', properties: { category: 'hub', source: 'city' }, geometry: { type: 'Point', coordinates: [-114.1, 51.05] } }] };
    expect(parseTransportSnapshot(snapshot, 'transit').features).toHaveLength(1);
    expect(() => parseTransportSnapshot({ ...snapshot, features: [] }, 'transit')).toThrow();
    expect(() => parseTransportSnapshot(snapshot, '5a')).toThrow();
    expect(() => parseTransportSnapshot({ ...snapshot, features: [{ ...snapshot.features[0], geometry: null }] }, 'transit')).toThrow();
  });
});
