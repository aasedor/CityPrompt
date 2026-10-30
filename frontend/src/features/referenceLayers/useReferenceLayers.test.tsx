import { StrictMode, type ReactNode } from 'react';
import { act, renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useReferenceLayers } from './useReferenceLayers';
import { referenceLayersApi, type ReferenceLayer } from './api';

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
  it('retires Calgary route snapshots from display without deleting saved connection data or other imports', async () => {
    const route: ReferenceLayer = {
      id: 'retired-route', project_id: 'pilot', name: 'Calgary existing streets & paths',
      source_filename: 'calgary-existing-transport.geojson', source_crs: 'EPSG:4326',
      source_url: 'https://services1.arcgis.com/AVP60cs0Q9PEA8rH/ArcGIS/rest/services',
      description: null, kind: 'reference', feature_count: 0, bounds: [-114, 51, -113.999, 51.001],
      warnings: [], color: '#0088aa', opacity: 0.7, created_at: '2026-10-01',
      feature_collection: { type: 'FeatureCollection', features: [] },
    };
    const imported = { ...route, id: 'my-import', source_url: 'https://example.com/roads' };
    const cityReference = { ...route, id: 'city-reference', source_filename: 'other-city-data.geojson' };
    vi.mocked(referenceLayersApi.list).mockResolvedValueOnce({ layers: [route, imported, cityReference], can_edit: true });
    localStorage.setItem('cityprompt:reference-visibility:pilot', '[]');
    const hook = renderHook(() => useReferenceLayers('pilot'), { wrapper });
    await waitFor(() => expect(hook.result.current.layers.map(layer => layer.id)).toEqual(['my-import', 'city-reference']));
    expect(hook.result.current.visibleLayers.map(layer => layer.id)).toEqual(['my-import', 'city-reference']);
    expect(hook.result.current.legacyTransportLayers).toEqual([route]);
    act(() => hook.result.current.toggleLayer(route.id));
    act(() => hook.result.current.toggleLayer(route.id));
    expect(hook.result.current.visibleLayers.map(layer => layer.id)).toEqual(['my-import', 'city-reference']);
    expect(referenceLayersApi.remove).not.toHaveBeenCalled();
  });
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
