import { describe, expect, it } from 'vitest';
import { modularBridgePoses, modularBridgeRouteProblem, modularBridgeWalkingHeight } from './modularBridgeProgram';

const bridge = { approachM: 6.3, endM: 41 / 6, bayM: 13 / 3, deckHeightM: 3.45, clearWidthM: 4 };
const program = { adapter: 'modular-bridge-v1', bridge, minLengthM: 32, maxLengthM: 240 };
const kinds = ['bridge_left_stair', 'bridge_left_end', 'bridge_bay', 'bridge_right_end', 'bridge_right_stair'];
const pilot = { widthM: 6, program, modules: Object.fromEntries(kinds.map((kind, i) => [kind,
  { url: `/street-kits/pilots/timber_covered_bridge_route_v1/${kind}.glb`, sha256: String(i).repeat(64) }])) };

describe('drawn native modular bridge', () => {
  it.each([32, 45, 80, 150, 240])('fills a %sm bridge with fixed ends and a continuous repeated centre', length => {
    const route = [{ x: 0, y: 0 }, { x: 0, y: length }];
    expect(modularBridgeRouteProblem(program, route)).toBeNull();
    const poses = modularBridgePoses(pilot, route);
    expect(poses.map(p => p.kind).filter(k => k !== 'bridge_bay')).toEqual(kinds.filter(k => k !== 'bridge_bay'));
    const bounds = (p: typeof poses[number]) => {
      const nativeLength = p.kind.endsWith('stair') ? bridge.approachM : p.kind === 'bridge_bay' ? bridge.bayM : bridge.endM;
      return [p.stationM - nativeLength * (p.longitudinalScale ?? 1) / 2,
        p.stationM + nativeLength * (p.longitudinalScale ?? 1) / 2];
    };
    expect(bounds(poses[0])[0]).toBeCloseTo(0, 6);
    expect(bounds(poses[poses.length - 1])[1]).toBeCloseTo(length, 6);
    for (let i = 1; i < poses.length; i++) expect(bounds(poses[i])[0]).toBeCloseTo(bounds(poses[i - 1])[1], 6);
    for (const p of poses) {
      expect(p.x).toBeCloseTo(0); expect(p.y).toBeCloseTo(p.stationM);
      expect(p.z).toBe(0); expect(p.scale).toBe(1);
      if (p.kind !== 'bridge_bay') expect(p.longitudinalScale ?? 1).toBe(1);
      else expect(p.longitudinalScale).toBeGreaterThan(.7);
    }
    if (length === 150) expect(poses.filter(p => p.kind === 'bridge_bay').length).toBeGreaterThan(25);
  });

  it('orients the same modules between oblique or reversed endpoints without changing width or height', () => {
    for (const [a, b] of [[{ x: 10, y: 20 }, { x: 58, y: 84 }], [{ x: 58, y: 84 }, { x: 10, y: 20 }]]) {
      const poses = modularBridgePoses(pilot, [a, b]);
      for (const p of poses) {
        expect(p.x).toBeCloseTo(a.x + (b.x - a.x) * p.stationM / 80);
        expect(p.y).toBeCloseTo(a.y + (b.y - a.y) * p.stationM / 80);
        expect(p.yaw).toBeCloseTo(Math.atan2(b.y - a.y, b.x - a.x) - Math.PI / 2);
        expect(p.scale).toBe(1);
      }
    }
  });

  it('accepts renderer densification of a straight two-point route, without turning it into multiple bridges', () => {
    const samples = Array.from({ length: 41 }, (_, i) => ({ x: 0, y: i * 2 }));
    const dense = modularBridgePoses(pilot, samples);
    expect(dense).toEqual(modularBridgePoses(pilot, [samples[0], samples[samples.length - 1]]));
  });

  it.each([
    [{ x: 0, y: 0 }],
    [{ x: 0, y: 0 }, { x: 0, y: 31 }],
    [{ x: 0, y: 0 }, { x: 0, y: 241 }],
    [{ x: 0, y: 0 }, { x: 2, y: 40 }, { x: 0, y: 80 }],
    [{ x: 0, y: 0 }, { x: 0, y: 90 }, { x: 0, y: 80 }],
    [{ x: 0, y: 0 }, { x: NaN, y: 80 }],
  ])('keeps unsupported drafts out of geometry and capture', (...route) => {
    expect(modularBridgeRouteProblem(program, route)).toBeTruthy();
    expect(() => modularBridgePoses(pilot, route)).toThrow();
  });

  it('follows the narrow stair and deck surface, without inventing walkable banks', () => {
    expect(modularBridgeWalkingHeight(program, 0, 0, 80)).toBe(0);
    expect(modularBridgeWalkingHeight(program, 0, bridge.approachM, 80)).toBe(bridge.deckHeightM);
    expect(modularBridgeWalkingHeight(program, 0, 40, 80)).toBe(bridge.deckHeightM);
    expect(modularBridgeWalkingHeight(program, 0, 80, 80)).toBe(0);
    expect(modularBridgeWalkingHeight(program, 0, bridge.approachM / 2, 80)).toBeGreaterThan(1.5);
    expect(modularBridgeWalkingHeight(program, 0, .01, 80)).toBeCloseTo(bridge.deckHeightM / 18);
    expect(modularBridgeWalkingHeight(program, 0, .36, 80)).toBeCloseTo(bridge.deckHeightM * 2 / 18);
    expect(modularBridgeWalkingHeight(program, 2.1, 40, 80)).toBeNull();
    expect(modularBridgeWalkingHeight(program, 0, -1, 80)).toBeNull();
    expect(modularBridgeWalkingHeight(program, 0, 81, 80)).toBeNull();
  });
});
