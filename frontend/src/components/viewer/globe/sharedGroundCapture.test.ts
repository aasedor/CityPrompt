import { describe, expect, it } from 'vitest';
import type { SharedSiteGroundState } from './SharedSiteGroundProvider';
import { captureSharedGround, assertSharedGroundUnchanged } from './sharedGroundCapture';
import { createSharedSiteGroundLayout, createSharedSiteGroundSnapshot } from './sharedSiteGround';
import type { SiteZone } from '@/types';

function readyState(): SharedSiteGroundState {
  const boundary: SiteZone = { id: 'boundary', project_id: 'project', zone_type: 'site_boundary', color: '#ffffff', sort_order: 0,
    created_at: '2026-09-04T12:00:00Z', updated_at: '2026-09-04T12:00:00Z', is_active_boundary: true,
    coordinates: [[0, 0], [0.0001, 0], [0.0001, 0.0001], [0, 0.0001]],
    properties: { community_3d_mask_existing_tiles: false } };
  const layout = createSharedSiteGroundLayout(boundary)!;
  const heights = Array.from({ length: layout.grid.columns * layout.grid.rows }, (_, i) => 100 + i * 0.01);
  const snapshot = createSharedSiteGroundSnapshot(layout, heights, heights)!;
  return { status: 'ready', snapshot, revision: snapshot.signature, heightAt: () => 100, contains: () => true };
}

describe('measured ground capture guard', () => {
  it('freezes all measured samples instead of sharing mutable runtime arrays', () => {
    const state = readyState();
    const capture = captureSharedGround(state)!;
    expect(capture).toEqual(state.snapshot);
    state.snapshot!.heights[0] = 500;
    expect(capture.heights[0]).toBe(100);
  });
  it.each(['sampling', 'unavailable'] as const)('rejects %s even if an old snapshot is present', (status) => {
    expect(() => captureSharedGround({ ...readyState(), status })).toThrow('Ground alignment is not ready');
  });
  it('rejects terrain refinement, source changes and activation during capture', () => {
    const state = readyState(), snapshot = captureSharedGround(state);
    expect(() => assertSharedGroundUnchanged(snapshot, state)).not.toThrow();
    expect(() => assertSharedGroundUnchanged(snapshot, { ...state, status: 'sampling' })).toThrow('terrain changed');
    expect(() => assertSharedGroundUnchanged(snapshot, { ...state, snapshot: { ...state.snapshot!, signature: 'changed' } })).toThrow('terrain changed');
    expect(() => assertSharedGroundUnchanged(undefined, state)).toThrow('terrain changed');
  });
  it('preserves the inactive legacy path without claiming measurements', () => {
    const state = { ...readyState(), status: 'inactive' as const, snapshot: null };
    expect(captureSharedGround(state)).toBeUndefined();
    expect(() => assertSharedGroundUnchanged(undefined, state)).not.toThrow();
  });
});
