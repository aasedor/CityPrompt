import { StrictMode, type ReactNode } from 'react';
import { act, renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { afterEach, describe, expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';
import { usePublicDataLayers } from './usePublicDataLayers';

const zones = [{ id: 'boundary', zone_type: 'site_boundary', coordinates: [[-114.08, 51.04], [-114.079, 51.04], [-114.079, 51.041]] }] as SiteZone[];
function setup() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return { client, wrapper: ({ children }: { children: ReactNode }) => <StrictMode><QueryClientProvider client={client}>{children}</QueryClientProvider></StrictMode> };
}
afterEach(() => vi.unstubAllGlobals());

describe('public data lazy selection', () => {
  it('makes no requests by default or for source-reference cards', async () => {
    vi.stubGlobal('fetch', vi.fn());
    const { result } = renderHook(() => usePublicDataLayers('project', zones), setup());
    expect(result.current.layers).toEqual([]);
    act(() => result.current.setEnabled('rental-context', true));
    expect(result.current.selectedIds.has('rental-context')).toBe(true);
    expect(fetch).not.toHaveBeenCalled();
  });

  it('loads on demand, reuses cached data and removes geometry immediately when unticked', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => new Response(JSON.stringify([{ point: { type: 'Point', coordinates: [-114.0795, 51.0405] }, name: 'School' }]))));
    const { result } = renderHook(() => usePublicDataLayers('project', zones), setup());
    act(() => result.current.setEnabled('schools', true));
    await waitFor(() => expect(result.current.layers).toHaveLength(1));
    expect(fetch).toHaveBeenCalledTimes(1);
    act(() => result.current.setEnabled('schools', false));
    expect(result.current.layers).toEqual([]);
    act(() => result.current.setEnabled('schools', true));
    await waitFor(() => expect(result.current.layers).toHaveLength(1));
    expect(fetch).toHaveBeenCalledTimes(1);
  });

  it('aborts an unticked request and hides stale geometry on site or project changes', async () => {
    const signals: AbortSignal[] = [];
    vi.stubGlobal('fetch', vi.fn((_url, options: RequestInit) => new Promise<Response>((_resolve, reject) => {
      const signal = options.signal!; signals.push(signal);
      signal.addEventListener('abort', () => reject(signal.reason), { once: true });
    })));
    const { result, rerender, unmount } = renderHook(({ project, site }) => usePublicDataLayers(project, site), { ...setup(), initialProps: { project: 'first', site: zones } });
    act(() => result.current.setEnabled('schools', true));
    await waitFor(() => expect(signals).toHaveLength(1));
    act(() => result.current.setEnabled('schools', false));
    await waitFor(() => expect(signals[0].aborted).toBe(true));
    act(() => result.current.setEnabled('schools', true));
    await waitFor(() => expect(signals).toHaveLength(2));
    const secondSite = [{ ...zones[0], coordinates: zones[0].coordinates.map(([x, y]) => [x + .01, y]) }];
    rerender({ project: 'first', site: secondSite });
    await waitFor(() => expect(signals).toHaveLength(3));
    expect(signals[1].aborted).toBe(true);
    expect(result.current.layers).toEqual([]);
    rerender({ project: 'second', site: zones });
    await waitFor(() => expect(signals[2].aborted).toBe(true));
    expect(result.current.selectedIds.size).toBe(0);
    unmount();
  });

  it('refreshes a cached layer when it is selected again after ten minutes', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => new Response('[]')));
    const context = setup();
    const { result } = renderHook(() => usePublicDataLayers('project', zones), context);
    act(() => result.current.setEnabled('schools', true));
    await waitFor(() => expect(result.current.states[0].layer).toBeDefined());
    act(() => result.current.setEnabled('schools', false));
    const cached = context.client.getQueryCache().findAll({ queryKey: ['optional-public-data-v1'] })[0];
    act(() => context.client.setQueryData(cached.queryKey, cached.state.data, { updatedAt: Date.now() - 11 * 60_000 }));
    act(() => result.current.setEnabled('schools', true));
    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(2));
  });

  it('limits map layers, allows reference cards, and will not query without a valid site', async () => {
    vi.stubGlobal('fetch', vi.fn());
    const { result } = renderHook(() => usePublicDataLayers('project', []), setup());
    act(() => ['schools', 'trees', 'water-mains', 'community', 'canopy', 'levies'].forEach(id => result.current.setEnabled(id, true)));
    expect(result.current.selectedIds.has('canopy')).toBe(false);
    expect(result.current.selectedIds.has('levies')).toBe(true);
    expect(result.current.atLimit).toBe(true);
    expect(result.current.problem).toMatch(/site/i);
    expect(fetch).not.toHaveBeenCalled();
  });

  it('shows an error without automatic retries and supports an explicit retry', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(new Response('Unavailable', { status: 503 })).mockResolvedValue(new Response('[]')));
    const { result } = renderHook(() => usePublicDataLayers('project', zones), setup());
    act(() => result.current.setEnabled('schools', true));
    await waitFor(() => expect(result.current.states[0].error).toMatch(/503/));
    expect(fetch).toHaveBeenCalledTimes(1);
    act(() => result.current.states[0].retry());
    await waitFor(() => expect(result.current.states[0].layer?.feature_count).toBe(0));
    expect(fetch).toHaveBeenCalledTimes(2);
  });
});
