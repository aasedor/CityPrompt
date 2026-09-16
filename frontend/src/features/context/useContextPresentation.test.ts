import { act, renderHook, waitFor } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';
import { useContextPresentation } from './useContextPresentation';

const boundary = (projectId: string, prepared = true): SiteZone => ({ id: 'site', project_id: projectId,
  zone_type: 'site_boundary', is_active_boundary: true, coordinates: [[-114, 51], [-114.001, 51], [-114, 51.001]],
  color: '#fff', sort_order: 0, created_at: 'before', updated_at: 'before',
  properties: { terrain_elevation_m: 1102, community_3d_mask_existing_tiles: prepared } });
const manifest = { id: 'drone-building-scans-flat-roof', kind: '3d-tiles', projectId: 'pilot',
  tilesetPath: '/context-pilot/tileset.json', registration: 'local-engineering-test', groundAuthority: 'saved-project',
  attribution: 'Matthew Guertin, 2026', licenseUrl: 'https://creativecommons.org/licenses/by/4.0/' };
afterEach(() => { vi.unstubAllEnvs(); vi.unstubAllGlobals(); });

it('does not load test data in normal use or replace live measured ground', () => {
  const fetcher = vi.fn(); vi.stubGlobal('fetch', fetcher); vi.stubEnv('VITE_CONTEXT_PILOT', 'false');
  const first = renderHook(() => useContextPresentation([boundary('pilot')]));
  expect(first.result.current.provider).toBeNull(); expect(fetcher).not.toHaveBeenCalled(); first.unmount();
  vi.stubEnv('VITE_CONTEXT_PILOT', 'true');
  const second = renderHook(() => useContextPresentation([boundary('pilot', false)]));
  expect(second.result.current.provider).toBeNull(); expect(fetcher).not.toHaveBeenCalled();
});

it('falls back after a failed capture and requires an explicit selection to retry', async () => {
  vi.stubEnv('VITE_CONTEXT_PILOT', 'true');
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify(manifest))));
  const { result } = renderHook(() => useContextPresentation([boundary('pilot')]));
  await waitFor(() => expect(result.current.provider).toBeTruthy());
  act(() => result.current.select('capture'));
  expect(result.current.visible).toBe('google'); expect(result.current.loading).toBe(true);
  act(() => result.current.onReady()); expect(result.current.visible).toBe('capture');
  act(() => result.current.onFailure()); expect(result.current.visible).toBe('google'); expect(result.current.loadCapture).toBe(false);
  act(() => result.current.select('capture')); expect(result.current.failed).toBe(false); expect(result.current.loadCapture).toBe(true);
});

it('ignores an old project response after navigation', async () => {
  vi.stubEnv('VITE_CONTEXT_PILOT', 'true');
  let finish!: (response: Response) => void;
  const fetcher = vi.fn().mockImplementation(() => Promise.resolve(new Response('null')))
    .mockImplementationOnce(() => new Promise<Response>(resolve => { finish = resolve; }));
  vi.stubGlobal('fetch', fetcher);
  const { result, rerender } = renderHook(({ id }) => useContextPresentation([boundary(id)]), { initialProps: { id: 'pilot' } });
  rerender({ id: 'another-project' });
  await act(async () => { finish(new Response(JSON.stringify(manifest))); });
  expect(fetcher).toHaveBeenCalledTimes(4);
  expect(fetcher.mock.calls[0][1].signal.aborted).toBe(true);
  expect(fetcher.mock.calls[1][1].signal.aborted).toBe(true);
  expect(result.current.provider).toBeNull(); expect(result.current.visible).toBe('google');
});
