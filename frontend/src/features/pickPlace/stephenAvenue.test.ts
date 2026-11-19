import { describe, expect, it } from 'vitest';
import { CATALOGUE_ASSETS, validateRegistry, type StreetAsset } from './assetRegistry';
import { CANONICAL_CHOICES } from './canonicalCatalogue';
import { nativeStreetPilot, nativeStreetLocalRouteProblem, placeNativeStreetModules } from '@/components/viewer/globe/nativeStreetPilot';
import { resolvePilotStreetSectionProfile } from '@/components/viewer/globe/streetSectionProfiles';
import { buildNativeStreetProgram } from '@/components/viewer/globe/nativeStreetProgram';
import { effectiveRoadWidth } from '@/utils/roadGeometry';
import { roundMetricStreetCenterline } from '@/utils/streetRouteCurves';
import bounds from '@/data/nativeStreetModuleBounds.json';

const id = 'student_stephen_avenue_mall_v1';
type Plan = { plan: number[][]; height: number[] };
const planOf = (sha: string) => (bounds as Record<string, Plan>)[sha];

/** A placement's occupied rectangle in the street frame (x across, y along). */
function footprint(item: { x: number; y: number; yaw: number; scale: number }, plan: Plan) {
  const c = Math.cos(item.yaw), s = Math.sin(item.yaw);
  const corners = [plan.plan[0][0], plan.plan[1][0]].flatMap(x => [plan.plan[0][1], plan.plan[1][1]].map(y =>
    [item.x + (x * c - y * s) * item.scale, item.y + (x * s + y * c) * item.scale]));
  const xs = corners.map(p => p[0]), ys = corners.map(p => p[1]);
  return { x0: Math.min(...xs), x1: Math.max(...xs), y0: Math.min(...ys), y1: Math.max(...ys) };
}

describe('Stephen Avenue pedestrian mall', () => {
  const pilot = nativeStreetPilot(id)!;

  it('is an ordinary drawable street card with its catalogue photograph', () => {
    const asset = CATALOGUE_ASSETS.find(a => a.id === id) as StreetAsset;
    expect(asset).toBeDefined();
    expect(validateRegistry([asset])).toEqual([]);
    expect(asset.kind).toBe('street');
    expect(asset.reshapeMode).toBe('fixed_section_route');
    expect(asset.properties.lane_count).toBe(0);
    expect(asset.sectionWidth).toBe(20);
    expect(effectiveRoadWidth(asset.properties)).toBe(20);
    expect(resolvePilotStreetSectionProfile({ properties: asset.properties })!.rowM).toBe(20);
    expect(asset.properties.road_archetype_id).toBe('stephen_avenue_pedestrian_mall');
    const choice = CANONICAL_CHOICES.find(c => c.placements.some(a => a.id === id));
    expect(choice?.domain).toBe('street_pathway');
    expect(choice!.option.photoUrl).toBe(asset.thumbnail);
  });

  it('accepts straight, bent and curved routes from 30 to 300 m, and nothing outside that', () => {
    const curved = roundMetricStreetCenterline([[0, 0], [0, 50], [40, 90], [40, 150]], 20).map(([x, y]) => ({ x, y }));
    for (const route of [[{ x: 0, y: 0 }, { x: 0, y: 30 }], [{ x: 0, y: 0 }, { x: 0, y: 120 }], [{ x: 0, y: 0 }, { x: 0, y: 60 }, { x: 50, y: 110 }],
      curved, [{ x: 0, y: 0 }, { x: 300, y: 0 }]]) {
      expect(nativeStreetLocalRouteProblem(pilot, route)).toBeNull();
    }
    expect(nativeStreetLocalRouteProblem(pilot, [{ x: 0, y: 0 }, { x: 0, y: 29 }])).not.toBeNull();
    expect(nativeStreetLocalRouteProblem(pilot, [{ x: 0, y: 0 }, { x: 0, y: 2001 }])).not.toBeNull();
  });

  it('repeats every authored item along a long route and keeps the promenade clear', () => {
    const route = [{ x: 0, y: 0 }, { x: 0, y: 160 }];
    const poses = placeNativeStreetModules(pilot, route);
    expect(poses).toHaveLength(pilot.placements.length * 4);
    for (const pose of poses) {
      expect(pose.url).toBe(`/street-kits/pilots/${id}/${pose.kind}.glb`);
      // A linden's crown overhangs the promenade above 2.7 m; on the ground it is its 1.5 m grate.
      const plan = pose.kind === 'linden_grate' ? { plan: [[-.75, -.75], [.75, .75]], height: [0, 0] } : planOf(pose.sha256);
      const box = footprint({ x: pose.x, y: 0, yaw: pose.yaw, scale: pose.scale }, plan);
      expect(box.x0).toBeGreaterThanOrEqual(-10.05);
      expect(box.x1).toBeLessThanOrEqual(10.05);
      // the 8 m granite promenade and its dark borders carry nothing
      expect(box.x1 <= -4.4 + 1e-6 || box.x0 >= 4.4 - 1e-6).toBe(true);
    }
    const kinds = new Set(poses.map(p => p.kind));
    expect([...kinds].sort()).toEqual(['bench', 'cafe_patio', 'heritage_lamp', 'linden_grate', 'litter_bin']);
  });

  it('never stands one piece of furniture inside another, within a cycle or across its ends', () => {
    const items = pilot.placements.flatMap(p => [p, { ...p, y: p.y + pilot.fixtureLengthM }]);
    const boxes = items.map(p => footprint(p, planOf(pilot.modules[p.kind as keyof typeof pilot.modules]!.sha256)));
    for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
      const a = boxes[i], b = boxes[j];
      const overlap = Math.min(a.x1, b.x1) - Math.max(a.x0, b.x0) > .01 && Math.min(a.y1, b.y1) - Math.max(a.y0, b.y0) > .01;
      // A tree's crown may spread over a bench or bin; only ground footprints below 2.5 m must not meet.
      const tree = items[i].kind === 'linden_grate' || items[j].kind === 'linden_grate';
      if (!tree) expect(overlap, `${items[i].kind} ${items[i].y} / ${items[j].kind} ${items[j].y}`).toBe(false);
    }
  });

  it('draws its surfaces from its own palette on a bent route, at the shared base lift', () => {
    const route = [{ x: 0, y: 0 }, { x: 0, y: 70 }, { x: 45, y: 120 }];
    const meshes = buildNativeStreetProgram(pilot.program!, pilot.widthM, pilot.fixtureLengthM, route);
    const materials = meshes.map(m => m.material).sort();
    expect(materials).toEqual(['brick', 'brick_joint', 'brick_soldier', 'edge', 'granite_border', 'paving']);
    for (const { geometry, material } of meshes) {
      expect(pilot.program!.palette[material]).toHaveLength(3);
      expect([...geometry.attributes.position.array].every(Number.isFinite)).toBe(true);
      geometry.computeBoundingBox();
      expect(geometry.boundingBox!.min.z).toBeGreaterThanOrEqual(pilot.program!.baseLiftM - 1e-6);
      expect(geometry.boundingBox!.max.z).toBeLessThan(pilot.program!.baseLiftM + .01);
      geometry.dispose();
    }
  });
});
