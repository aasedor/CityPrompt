import { cleanup, renderHook } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import {
  createSharedSiteGroundLayout,
  sharedSiteGroundGridPoint,
} from './sharedSiteGround';
import { measureParkTerrain } from './parkTerrain';
import { useParkGround } from './useParkGround';
import {
  createSharedGroundTriangulation,
  drapeSharedGroundGeometry,
} from './sharedGroundGeometry';
vi.mock('./AutomaticParkGround', () => ({
  useAutomaticParkContext: () => ({ ids: new Set(['park']), fallback: 1000 }),
}));
const park = {
  id: 'park',
  zone_type: 'green_space',
  coordinates: [
    [-114, 51],
    [-113.9998, 51],
    [-113.9998, 51.0002],
    [-114, 51.0002],
  ],
  properties: {},
  updated_at: 'r1',
} as SiteZone;
const layout = createSharedSiteGroundLayout(park)!;
const heights = Array.from(
  { length: layout.grid.columns * layout.grid.rows },
  (_, i) => 1000 + (i % layout.grid.columns) * 0.1,
);
const profile = measureParkTerrain(park, {
  layout,
  heights,
  previousHeights: [...heights],
})!;
afterEach(cleanup);
describe('park ground during automatic alignment', () => {
  it('keeps the moved draft visible on shared triangles without exposing a capture snapshot', () => {
    const moved = {
      ...park,
      coordinates: park.coordinates.map(([x, y]) => [x + 0.00001, y]),
      properties: { park_terrain: profile },
    };
    const { result } = renderHook(() => useParkGround(moved));
    const state = result.current;
    expect(state.status).toBe('sampling');
    expect(state.preview).toBe(true);
    expect(state.snapshot).toBeNull();
    expect(state.draftLayout).toBeDefined();
    for (
      let i = 0;
      i < state.draftLayout!.grid.columns * state.draftLayout!.grid.rows;
      i++
    )
      expect(
        Number.isFinite(
          state.heightAt(...sharedSiteGroundGridPoint(state.draftLayout!, i)),
        ),
      ).toBe(true);
    const frame = [-113.99989, 51.0001],
      source = new THREE.PlaneGeometry(4, 4);
    const ground = drapeSharedGroundGeometry(
      source,
      (x, y) =>
        state.heightAt(frame[0] + x / 70000, frame[1] + y / 111320)! - 1000,
      4,
      60000,
      createSharedGroundTriangulation(state.draftLayout!, frame[0], frame[1]),
    );
    expect(ground).not.toBeNull();
    source.dispose();
    ground?.dispose();
  });
  it('retains a flat visible draft for a new park, then uses its persisted measurement on reopen', () => {
    const { result, rerender } = renderHook(({ zone }) => useParkGround(zone), {
      initialProps: { zone: park },
    });
    expect(result.current.preview).toBe(true);
    expect(result.current.heightAt(-113.9999, 51.0001)).toBe(1000);
    rerender({ zone: { ...park, properties: { park_terrain: profile } } });
    expect(result.current.status).toBe('ready');
    expect(result.current.snapshot?.signature).toBe(profile.snapshot.signature);
  });
});
