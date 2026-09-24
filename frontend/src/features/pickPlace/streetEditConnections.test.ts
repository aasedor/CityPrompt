import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import saved from '@/components/viewer/globe/__fixtures__/currieRehearsalStreetEdit.json';
import { detectConnectedStreetIntersections } from '@/components/viewer/globe/streetGraphIntersections';
import { resolveStreetJunctionLayout } from '@/components/viewer/globe/streetJunctionGeometry';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
import { streetCoordinateUpdate } from './streetPlacement';
import { snapConnectedStreetEdit, streetEditConnectionCheck } from './streetEditConnections';

const zones = saved.zones as unknown as SiteZone[];
const main = zones.find(zone => zone.id === 'main')!;
const patches = (items: SiteZone[]) => detectConnectedStreetIntersections(items)
  .filter(node => resolveStreetJunctionLayout(node, items));

describe('connected street editing', () => {
  it('checks the same junctions with buildings, parks and a site boundary present', () => {
    const wholeSite = [...zones, ...saved.nonRoadZones] as unknown as SiteZone[];
    expect(patches(wholeSite)).toEqual(patches(zones));
    const gesture = bufferLineToPolygon(saved.brokenControls, 23);
    expect(streetEditConnectionCheck(main, wholeSite)({ ...main, ...streetCoordinateUpdate(main, gesture) })).toBe(false);
    const snapped = snapConnectedStreetEdit(main, gesture, wholeSite);
    expect(snapped).not.toEqual(gesture);
    expect(patches(wholeSite.map(zone => zone.id === main.id
      ? { ...main, ...streetCoordinateUpdate(main, snapped) } : zone))).toHaveLength(2);
  });

  it('clamps the observed Currie bend gesture before its local-street T disappears', () => {
    const gesture = bufferLineToPolygon(saved.brokenControls, 23);
    const before = JSON.stringify(zones);
    const broken = { ...main, ...streetCoordinateUpdate(main, gesture) };
    expect(patches(zones)).toHaveLength(2);
    expect(patches(zones.map(zone => zone.id === main.id ? broken : zone))).toHaveLength(1);
    const snapped = snapConnectedStreetEdit(main, gesture, zones);
    const updated = { ...main, ...streetCoordinateUpdate(main, snapped) };
    expect(snapped).not.toEqual(gesture);
    expect(updated.coordinates).not.toEqual(main.coordinates);
    expect(patches(zones.map(zone => zone.id === main.id ? updated : zone))).toHaveLength(2);
    expect(streetEditConnectionCheck(main, zones)(updated)).toBe(true);
    expect(JSON.stringify(zones)).toBe(before);
    // Rechecking at commit is idempotent after the live preview has snapped.
    expect(snapConnectedStreetEdit(main, snapped, zones)).toBe(snapped);
  });

  it('leaves a valid gesture alone and does not lock an unconnected street', () => {
    expect(snapConnectedStreetEdit(main, main.coordinates, zones)).toBe(main.coordinates);
    const gesture = bufferLineToPolygon(saved.brokenControls, 23);
    expect(snapConnectedStreetEdit(main, gesture, [main])).toBe(gesture);
  });

  it('detects a lost junction for section replacement without mutating neighbours', () => {
    const gesture = bufferLineToPolygon(saved.brokenControls, 23);
    expect(streetEditConnectionCheck(main, zones)({ ...main, ...streetCoordinateUpdate(main, gesture) })).toBe(false);
  });
});
