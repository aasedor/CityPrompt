import { StrictMode, type ReactNode } from 'react';
import { act, renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useReferenceLayers } from './useReferenceLayers';

vi.mock('./api', () => ({
  referenceLayerQueryKey: (id: string) => ['reference-layers', id],
  referenceLayersApi: {
    list: vi.fn(async () => ({ layers: [{ id: 'zoning' }], can_edit: true })),
    remove: vi.fn(),
  },
}));

function wrapper({ children }: { children: ReactNode }) {
  return <StrictMode><QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
    {children}
  </QueryClientProvider></StrictMode>;
}

beforeEach(() => localStorage.clear());

describe('reference layer visibility in StrictMode', () => {
  it('hides on the first click, persists across remount, and can be shown again', async () => {
    const first = renderHook(() => useReferenceLayers('pilot'), { wrapper });
    await waitFor(() => expect(first.result.current.visibleLayers).toHaveLength(1));
    act(() => first.result.current.toggleLayer('zoning'));
    expect(first.result.current.hiddenIds.has('zoning')).toBe(true);
    expect(first.result.current.visibleLayers).toEqual([]);
    expect(JSON.parse(localStorage.getItem('cityprompt:reference-visibility:pilot')!)).toEqual(['zoning']);
    first.unmount();

    const second = renderHook(() => useReferenceLayers('pilot'), { wrapper });
    await waitFor(() => expect(second.result.current.layers).toHaveLength(1));
    expect(second.result.current.visibleLayers).toEqual([]);
    act(() => second.result.current.toggleLayer('zoning'));
    expect(second.result.current.visibleLayers).toHaveLength(1);
    expect(JSON.parse(localStorage.getItem('cityprompt:reference-visibility:pilot')!)).toEqual([]);
  });

  it('keeps each project’s visibility separate when switching projects', () => {
    localStorage.setItem('cityprompt:reference-visibility:second', JSON.stringify(['other']));
    const { result, rerender } = renderHook(({ project }) => useReferenceLayers(project), {
      initialProps: { project: 'first' }, wrapper,
    });
    act(() => result.current.toggleLayer('zoning'));
    rerender({ project: 'second' });
    expect([...result.current.hiddenIds]).toEqual(['other']);
    act(() => result.current.toggleLayer('other'));
    rerender({ project: 'first' });
    expect([...result.current.hiddenIds]).toEqual(['zoning']);
    expect(JSON.parse(localStorage.getItem('cityprompt:reference-visibility:second')!)).toEqual([]);
  });
});
