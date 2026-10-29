import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import saved from '@/components/viewer/globe/__fixtures__/currieRehearsalStreetEdit.json';
import currentRecipes from '@/components/viewer/globe/__fixtures__/classroomStreetRecipes.json';
import longCrossing from '@/components/viewer/globe/__fixtures__/longStreetCrossing.json';
import { detectConnectedStreetIntersections } from '@/components/viewer/globe/streetGraphIntersections';
import { resolveStreetJunctionLayout } from '@/components/viewer/globe/streetJunctionGeometry';
import { bufferLineToPolygon, extractZoneCenterline } from '@/utils/roadGeometry';
import { streetCoordinateUpdate } from './streetPlacement';
import { snapConnectedStreetEdit, streetEditConnectionCheck } from './streetEditConnections';
import { snapStreetBoundaryPlacement } from './streetBoundaryPlacement';

// Replay the recorded gesture against current module bindings. The historical
// fixture stays unchanged; its pre-upgrade locks cannot approve today's models.
const zones = (saved.zones as unknown as SiteZone[]).map(zone => {
  const recipe=currentRecipes.find(r=>r.variant_id===zone.properties?.road_selected_variant_id);
  return recipe ? {...zone,properties:{...zone.properties,public_realm_lego:recipe}} : zone;
});
const main = zones.find(zone => zone.id === 'main')!;
const patches = (items: SiteZone[]) => detectConnectedStreetIntersections(items)
  .filter(node => resolveStreetJunctionLayout(node, items));

describe('connected street editing', () => {
  it('allows a long X crossing to become a complete T without retaining a spur', () => {
    const network=longCrossing as unknown as SiteZone[];
    const branch=network[0], host=network[1];
    const hostLine=extractZoneCenterline(host);
    const centre=hostLine[0].map((value,axis)=>(value+hostLine[1][axis])/2);
    const shortened=bufferLineToPolygon([extractZoneCenterline(branch)[0],centre],18);
    const proposed={...branch,...streetCoordinateUpdate(branch,shortened)};
    expect(patches(network)[0].armCount).toBe(4);
    const next=network.map(zone=>zone.id===branch.id?proposed:zone);
    expect(patches(next)).toHaveLength(1);
    expect(patches(next)[0].armCount).toBe(3);
    expect(streetEditConnectionCheck(branch,network)(proposed)).toBe(true);
    expect(snapConnectedStreetEdit(branch,shortened,network)).toBe(shortened);
    // Extending the same branch back through the street remains connected.
    expect(streetEditConnectionCheck(proposed,next)(branch)).toBe(true);
  });

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

  it('does not let boundary snapping approve a disconnected street edit', () => {
    const boundary = saved.nonRoadZones.find(zone => zone.zone_type === 'site_boundary') as unknown as SiteZone;
    const gesture = bufferLineToPolygon(saved.brokenControls, 23);
    const broken = { ...main, ...streetCoordinateUpdate(main, gesture) };
    const result = snapStreetBoundaryPlacement(broken, zones, boundary);
    expect(result.problem).not.toBeNull();
    expect(streetEditConnectionCheck(main, zones)({ ...broken, ...result })).toBe(false);
  });
});
