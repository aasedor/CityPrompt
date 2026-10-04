import { describe, expect, it } from 'vitest';
import { canalRoute, canalRouteProblem, canalWalkingHeight } from './canalRoute';
import { buildSpecialistStreetProgram, CANAL_VARIANT } from './specialistStreetProgram';
import { nativeStreetPilot, placeNativeStreetModules } from './nativeStreetPilot';
import { roundMetricStreetCenterline } from '@/utils/streetRouteCurves';

const pilot = nativeStreetPilot(CANAL_VARIANT)!;
const straight = (length: number) => [{ x: 0, y: 0 }, { x: 0, y: length }];
const curve = roundMetricStreetCenterline([[0, 0], [0, 120], [140, 220]], 54).map(([x, y]) => ({ x, y }));

describe('student-drawn canals', () => {
  it.each([36, 47.3, 79, 80, 334, 712.5, 2000])('accepts a freely drawn %s metre canal', length => {
    expect(canalRouteProblem(straight(length))).toBeNull();
  });
  it('keeps the original assembly on saved straight canals', () => {
    expect(canalRoute(straight(120)).original).toBe(true);
    const poses = placeNativeStreetModules(pilot, straight(120));
    for (const kind of ['canal_ground', 'canal_crossing', 'canal_furnishings']) {
      expect(poses.find(p => p.kind === kind)).toMatchObject({ x: 0, y: 40, yaw: 0, scale: 1 });
    }
  });
  it.each([straight(36), straight(53.7), curve].map(route => ({route})))('fits an unscaled crossing and complete banks to the route', ({route}) => {
    const layout = canalRoute(route);
    expect(canalRouteProblem(route)).toBeNull();
    expect(layout.original).toBe(false);
    expect(layout.crossing).not.toBeNull();
    const poses = placeNativeStreetModules(pilot, route);
    expect(poses.filter(p => p.kind === 'canal_crossing')).toHaveLength(1);
    expect(poses.every(p => p.scale === 1)).toBe(true);
    const bridge = poses.find(p => p.kind === 'canal_crossing')!;
    // Source bridge centre is local Y=20; its transformed centre must land
    // on the selected straight stretch even when its origin precedes a bend.
    const centre = layout.point(0, layout.crossing!, 0);
    expect(bridge.x - Math.sin(bridge.yaw) * 20).toBeCloseTo(centre[0], 4);
    expect(bridge.y + Math.cos(bridge.yaw) * 20).toBeCloseTo(centre[1], 4);
    expect(canalWalkingHeight(0, layout.crossing!, layout.length, layout.crossing, false)).toBeCloseTo(1.72);
    expect(canalWalkingHeight(0, 3, layout.length, layout.crossing, false)).toBe(-2.05);
    const meshes = buildSpecialistStreetProgram(CANAL_VARIANT, route);
    const water = meshes.find(m => m.material === 'water')!.geometry.getAttribute('position');
    expect(water.count).toBeGreaterThan(0);
    for (let i = 0; i < water.count; i++) expect(water.getZ(i)).toBeCloseTo(-2.05, 5);
    for (const mesh of meshes) {
      expect(Array.from(mesh.geometry.getAttribute('position').array).every(Number.isFinite)).toBe(true);
      mesh.geometry.dispose();
    }
  });
  it('does not place a rigid crossing across a continuously bending route', () => {
    const route = Array.from({ length: 31 }, (_, i) => ({ x: 70 * Math.cos(i / 30), y: 70 * Math.sin(i / 30) }));
    expect(canalRouteProblem(route)).toBeNull();
    expect(canalRoute(route).crossing).toBeNull();
    expect(placeNativeStreetModules(pilot, route).some(p => p.kind === 'canal_crossing')).toBe(false);
  });
});
