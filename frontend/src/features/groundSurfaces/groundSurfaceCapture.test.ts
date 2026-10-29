import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';
import { authoredSurfaceRevision, getAuthoredSurfaceCaptureClaims } from './groundSurfaceCapture';

const finish = (): SiteZone => ({ id: 'surface', zone_type: 'development_area',
  coordinates: [[-114.08, 51.04], [-114.079, 51.04], [-114.079, 51.041], [-114.08, 51.041]],
  project_id: 'surface-test', color: '#303336', sort_order: 0, created_at: '2026-10-29', updated_at: '2026-10-29',
  properties: { ground_surface_material: 'black_pavers' } });
const GOLDEN = 'd0b0d2c05786a8fe8d4284b35862a1c888dec5fd144d8254cbaf003d66869cff';
beforeEach(async () => {
  const cryptoModule = 'node:crypto';
  const { webcrypto } = await import(cryptoModule);
  vi.stubGlobal('crypto', webcrypto);
});
afterEach(() => vi.unstubAllGlobals());

it('matches the backend geometry/material hash without an archetype compilation', async () => {
  expect(await getAuthoredSurfaceCaptureClaims([finish()])).toEqual([{ zone_id: 'surface', source_hash: GOLDEN }]);
});

it('hashes the same polygon consistently across closure, winding and first vertex', async () => {
  const zone = finish();
  zone.coordinates = [...zone.coordinates.slice(2), ...zone.coordinates.slice(0, 2)].reverse();
  zone.coordinates.push(zone.coordinates[0]);
  expect((await getAuthoredSurfaceCaptureClaims([zone]))[0].source_hash).toBe(GOLDEN);
});

it('snapshots claims before yielding and invalidates geometry and material revisions', async () => {
  const zone = finish(), before = authoredSurfaceRevision([zone]);
  const pending = getAuthoredSurfaceCaptureClaims([zone]);
  zone.coordinates[1][0] += .0001;
  expect((await pending)[0].source_hash).toBe(GOLDEN);
  expect((await getAuthoredSurfaceCaptureClaims([zone]))[0].source_hash).not.toBe(GOLDEN);
  expect(authoredSurfaceRevision([zone])).not.toBe(before);
  const material = finish(); material.properties!.ground_surface_material = 'red_brick';
  expect((await getAuthoredSurfaceCaptureClaims([material]))[0].source_hash).not.toBe(GOLDEN);
  expect(authoredSurfaceRevision([material])).not.toBe(before);
});

it('excludes unknown finishes and framework/boundary overlays', async () => {
  const unknown = finish(); unknown.properties!.ground_surface_material = 'not-supported';
  const framework = finish(); framework.properties!._plan_role = 'framework_height';
  const boundary = finish(); boundary.zone_type = 'site_boundary';
  expect(await getAuthoredSurfaceCaptureClaims([unknown, framework, boundary])).toEqual([]);
});
