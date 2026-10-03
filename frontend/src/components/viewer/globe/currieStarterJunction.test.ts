import { it, expect } from 'vitest';
import type { SiteZone } from '@/types';
import saved from './__fixtures__/currieStarterJunction.json';
import { detectConnectedStreetIntersections } from './streetGraphIntersections';
import { resolveStreetJunctionLayout } from './streetJunctionGeometry';
import { snapStreetEnds } from '@/features/pickPlace/streetSnapping';

it('resolves the saved Currie angled T with a sub-metre endpoint gap', () => {
  const zones = saved as unknown as SiteZone[];
  const nodes = detectConnectedStreetIntersections(zones);
  const tee = nodes.find(node => node.zoneIds.includes('currie-street-0'))!;
  expect(tee.armCount).toBe(3);
  expect(resolveStreetJunctionLayout(tee, zones)?.sections).toHaveLength(2);
  expect(tee.longitude).toBeCloseTo(-114.1258624244, 8);
});

it('does not distort a near-end gesture when a full-width junction cannot fit', () => {
  const zones = saved as unknown as SiteZone[];
  const main = zones[1];
  const controls = main.properties!.plan_route_controls as number[][];
  const snapped = snapStreetEnds(controls, zones, main.id, 23);
  expect(snapped).toBe(controls);
  const node = detectConnectedStreetIntersections(zones).find(node => node.zoneIds.includes(main.id))!;
  expect(resolveStreetJunctionLayout(node, zones)).toBeNull();
});
