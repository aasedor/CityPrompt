import { describe, expect, it } from 'vitest';
import { STREET_ASSETS } from './assetRegistry';
import { streetDrawingGeometry, streetPreviewPoints } from './streetDrawingGeometry';
import { nativeStreetPilotForZone } from '@/components/viewer/globe/nativeStreetPilot';
import { resolvePilotStreetSectionProfile } from '@/components/viewer/globe/streetSectionProfiles';
const lonM = 111320 * Math.cos(51 * Math.PI / 180);
const ll = (x: number, y: number) => [-114 + x / lonM, 51 + y / 111320];

describe('live street route geometry', () => {
  it('waits for the first waypoint, rejects duplicate cursor positions and clears the draft', () => {
    expect(streetPreviewPoints([], ll(20, 0))).toEqual([]);
    expect(streetPreviewPoints([ll(0, 0)], ll(.1, 0))).toEqual([ll(0, 0)]);
    expect(streetPreviewPoints([ll(0, 0)], ll(20, 0))).toEqual([ll(0, 0), ll(20, 0)]);
    expect(streetPreviewPoints([ll(0, 0), ll(20, 0)], null)).toHaveLength(2);
    expect(streetPreviewPoints([], null)).toEqual([]);
  });
  it.each(STREET_ASSETS)('$label previews the same metric route that is saved', asset => {
    const points = [ll(0, 0), ll(120, 0)];
    const preview = streetDrawingGeometry(streetPreviewPoints([points[0]], points[1]), asset.properties, []);
    const saved = streetDrawingGeometry(points, asset.properties, []);
    expect(preview).toEqual(saved);
    expect(preview.coordinates.flat().every(Number.isFinite)).toBe(true);
    expect(preview.properties.road_selected_variant_id).toBe(asset.model.variantId);
    expect(resolvePilotStreetSectionProfile(preview)?.rowM).toBe(asset.sectionWidth);
    const zone = { zone_type: 'road' as const, properties: preview.properties };
    // A draft never forges a trusted persisted recipe to unlock its native model.
    expect(preview.properties.public_realm_lego).toBeUndefined();
    expect(nativeStreetPilotForZone(zone)).toBeUndefined();
  });
  it('rounds bends without mutating the clicked points or selected properties', () => {
    const points = [ll(0, 0), ll(60, 0), ll(110, 40)];
    const properties = { ...STREET_ASSETS[0].properties };
    const before = JSON.stringify({ points, properties });
    const result = streetDrawingGeometry(points, properties, []);
    expect(result.properties.plan_route_controls).toEqual(points);
    expect(JSON.stringify({ points, properties })).toBe(before);
  });
});
