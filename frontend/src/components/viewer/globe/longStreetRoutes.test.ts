import { describe, expect, it } from 'vitest';
import sourcePilots from '@/data/nativeStreetPilots.json';
import { nativeStreetLocalRouteProblem, nativeStreetPilot, placeNativeStreetModules } from './nativeStreetPilot';
import { buildNativeStreetProgram } from './nativeStreetProgram';
import { PUBLIC_REALM_STREET_SELECTIONS } from './streetFamilyCatalog';

describe('long student street routes', () => {
  const repeatable = sourcePilots.filter(p => p.id !== 'landmark_signature_bridge_v2');
  it.each(repeatable.map(p => [p.id]))('%s accepts long routes without changing its source locks', id => {
    const source = sourcePilots.find(p => p.id === id)!;
    const pilot = nativeStreetPilot(id)!;
    for (const length of [508, 1200, 2000]) {
      expect(nativeStreetLocalRouteProblem(pilot, [{ x: 0, y: 0 }, { x: 0, y: length }])).toBeNull();
    }
    expect(nativeStreetLocalRouteProblem(pilot, [{ x: 0, y: 0 }, { x: 0, y: 2001 }])).not.toBeNull();
    expect(PUBLIC_REALM_STREET_SELECTIONS.find(p => p.variantId === id)!.maxLengthM).toBe(2000);
    expect(pilot.programSha256).toBe(source.programSha256);
    expect(pilot.modules).toEqual(source.modules);
  });
  it('continues residential furniture and paving beyond the old cap at native scale', () => {
    const pilot = nativeStreetPilot('student_quiet_residential_street_v1')!;
    const route = [{ x: 0, y: 0 }, { x: 0, y: 1200 }];
    const poses = placeNativeStreetModules(pilot, route);
    expect(poses.some(p => p.stationM > 1100)).toBe(true);
    const sourceScales = new Set(placeNativeStreetModules(pilot, [{ x: 0, y: 0 }, { x: 0, y: 48 }]).map(p => `${p.kind}:${p.scale}`));
    expect(poses.every(p => sourceScales.has(`${p.kind}:${p.scale}`))).toBe(true);
    const meshes = buildNativeStreetProgram(pilot.program!, pilot.widthM, pilot.fixtureLengthM, route);
    const asphalt = meshes.find(m => m.material === 'asphalt')!.geometry;
    asphalt.computeBoundingBox();
    expect(asphalt.boundingBox!.min.y).toBeCloseTo(0);
    expect(asphalt.boundingBox!.max.y).toBeCloseTo(1200);
    meshes.forEach(m => m.geometry.dispose());
  });
  it('keeps the landmark bridge span bounded', () => {
    const pilot = nativeStreetPilot('landmark_signature_bridge_v2')!;
    expect(nativeStreetLocalRouteProblem(pilot, [{ x: 0, y: 0 }, { x: 0, y: 480 }])).toBeNull();
    expect(nativeStreetLocalRouteProblem(pilot, [{ x: 0, y: 0 }, { x: 0, y: 508 }])).toContain('480');
  });
});
