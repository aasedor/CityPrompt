import { act, cleanup, render } from '@testing-library/react';
import { afterEach, beforeEach, describe, it, expect, vi } from 'vitest';
import type { ReactNode } from 'react';
import type { SiteZone } from '@/types';
import type { SharedSiteGroundState } from './SharedSiteGroundProvider';
import { createSharedSiteGroundLayout } from './sharedSiteGround';
import { AutomaticParkGround } from './AutomaticParkGround';
const mock = vi.hoisted(() => ({
  callback: null as null | ((s: SharedSiteGroundState) => void),
  mounts: 0,
}));
vi.mock('./SharedSiteGroundProvider', () => ({
  SharedSiteGroundProvider: ({
    onChange,
    children,
  }: {
    onChange: (s: SharedSiteGroundState) => void;
    children: ReactNode;
  }) => {
    mock.callback = onChange;
    mock.mounts++;
    return children;
  },
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
  properties: {
    green_space_archetype_id: 'neighborhood_park',
    green_space_selected_variant_id: 'neighborhood_park_v0',
    neighborhood_park_layout: 'adaptive_rustic_v1',
    park_terrain: { version: 0 },
  },
  updated_at: 'r1',
} as unknown as SiteZone;
function measured(z: SiteZone): SharedSiteGroundState {
  const layout = createSharedSiteGroundLayout(z)!;
  const heights = Array(layout.grid.rows * layout.grid.columns).fill(1050);
  return {
    status: 'inactive',
    snapshot: null,
    heightAt: () => null,
    contains: () => false,
    revision: 'test',
    inspectionStatus: 'ready',
    review: { layout, heights, previousHeights: [...heights] },
  };
}
beforeEach(() => {
  vi.useFakeTimers();
  mock.callback = null;
  mock.mounts = 0;
});
afterEach(() => {
  cleanup();
  vi.useRealTimers();
});
describe('automatic park measurement queue', () => {
  it('debounces edits, discards late measurements, then saves the latest footprint', async () => {
    const save = vi.fn().mockResolvedValue(true),
      change = vi.fn();
    const view = render(
      <AutomaticParkGround
        zones={[park]}
        paused={false}
        onSave={save}
        onChange={change}
        fallback={1050}
      >
        {null}
      </AutomaticParkGround>,
    );
    act(() => vi.advanceTimersByTime(950));
    const old = mock.callback!;
    const moved = {
      ...park,
      coordinates: park.coordinates.map(([x, y]) => [x + 0.00001, y]),
    };
    view.rerender(
      <AutomaticParkGround
        zones={[moved]}
        paused={false}
        onSave={save}
        onChange={change}
        fallback={1050}
      >
        {null}
      </AutomaticParkGround>,
    );
    await act(async () => old(measured(park)));
    expect(save).not.toHaveBeenCalled();
    act(() => vi.advanceTimersByTime(950));
    await act(async () => mock.callback!(measured(moved)));
    expect(save).toHaveBeenCalledOnce();
    expect(save.mock.calls[0][0].coordinates).toEqual(moved.coordinates);
  });
  it('bounds an attempt even when the tile provider never finishes', async () => {
    const save = vi.fn(),
      change = vi.fn();
    render(
      <AutomaticParkGround
        zones={[park]}
        paused={false}
        onSave={save}
        onChange={change}
        fallback={1050}
      >
        {null}
      </AutomaticParkGround>,
    );
    for (let i = 0; i < 3; i++) {
      act(() => vi.advanceTimersByTime(6000));
      await act(async () => vi.advanceTimersByTime(60000));
    }
    expect(change).toHaveBeenLastCalledWith(
      expect.objectContaining({ pending: true, needsAttention: true }),
    );
    expect(save).not.toHaveBeenCalled();
  });
  it('does not measure during an authored save and bounds repeated failures', async () => {
    const save = vi.fn(),
      change = vi.fn();
    const view = render(
      <AutomaticParkGround
        zones={[park]}
        paused
        onSave={save}
        onChange={change}
        fallback={1050}
      >
        {null}
      </AutomaticParkGround>,
    );
    act(() => vi.advanceTimersByTime(1000));
    expect(mock.callback).toBeNull();
    view.rerender(
      <AutomaticParkGround
        zones={[park]}
        paused={false}
        onSave={save}
        onChange={change}
        fallback={1050}
      >
        {null}
      </AutomaticParkGround>,
    );
    for (let i = 0; i < 3; i++) {
      act(() => vi.advanceTimersByTime(6000));
      await act(async () =>
        mock.callback!({
          ...measured(park),
          review: null,
          inspectionStatus: 'unavailable',
        }),
      );
    }
    expect(change).toHaveBeenLastCalledWith(
      expect.objectContaining({ pending: true, needsAttention: true }),
    );
    expect(save).not.toHaveBeenCalled();
  });
});
