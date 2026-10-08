import '@testing-library/jest-dom/vitest';
import { act, render, renderHook, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState, type ReactNode } from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useCityPolicyMaps } from './useCityPolicyMaps';
import { CityPolicyDetailsCard } from './CityPolicyDetailsCard';
import { CityPolicyMapsPanel } from './CityPolicyMapsPanel';
import { CITY_MAP_LAYERS } from './citywidePlans';
import type { TransportSnapshot } from './transportVectors';
import { parseTransportSnapshot } from './transportVectors';
import routeJson from '../../../public/policy-maps/transport-vectors-v1/service-routes.geojson?raw';
import stopJson from '../../../public/policy-maps/transport-vectors-v1/service-stops.geojson?raw';

const routes: TransportSnapshot = { type: 'FeatureCollection', network: 'service-routes', retrieved: '2026-10-08',
  sources: { routes: { url: 'https://data.calgary.ca/d/hpnd-riq4', featureCount: 2, updated: '2026-09-29' } }, featureCount: 2,
  features: ['7', '9'].map(number => ({ type: 'Feature', id: number, properties: { category: 'service-regular', source: 'routes', name: 'Route ' + number, routeNumber: number },
    geometry: { type: 'MultiLineString', coordinates: [[[-114.1, 51.05], [-114.11, 51.06]]] } })) };
const stops: TransportSnapshot = { ...routes, network: 'service-stops', featureCount: 1,
  sources: { stops: { url: 'https://data.calgary.ca/d/muzh-c9qc', featureCount: 1 } },
  features: [{ type: 'Feature', id: 'stop', properties: { category: 'service-stop', source: 'stops', name: 'WB Example', stopNumber: '1234',
    routes: [{ number: '7', name: 'Marda Loop' }, { number: '9', name: 'Dalhousie' }] }, geometry: { type: 'Point', coordinates: [-114.1, 51.05] } }] };
const fetchMap = vi.fn(async (url: string) => ({ ok: true, json: async () => url.endsWith('service-stops.geojson') ? stops : routes }));
function wrapper({ children }: { children: ReactNode }) {
  const [client] = useState(() => new QueryClient({ defaultOptions: { queries: { retry: false } } }));
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}
beforeEach(() => { localStorage.clear(); vi.clearAllMocks(); vi.stubGlobal('fetch', fetchMap); });

describe('Calgary Transit service layers', () => {
  it('ships complete route and active-stop snapshots with valid geographic geometry and provenance', () => {
    const routeData = parseTransportSnapshot(JSON.parse(routeJson), 'service-routes');
    const stopData = parseTransportSnapshot(JSON.parse(stopJson), 'service-stops');
    expect(routeData.features).toHaveLength(261);
    expect(stopData.features).toHaveLength(6213);
    expect(routeData.features.every(f => f.properties.routeNumber && f.properties.name && f.geometry.type === 'MultiLineString')).toBe(true);
    expect(stopData.features.every(f => f.properties.stopNumber && f.properties.designation === 'ACTIVE' && f.geometry.type === 'Point')).toBe(true);
    expect(stopData.sources['stop-routes'].updated).toBeTruthy();
  });
  it('loads routes and stops independently, keeps them vector-only and persists route selection', async () => {
    const { result, rerender } = renderHook(({ project }) => useCityPolicyMaps(project), { wrapper, initialProps: { project: 'service' } });
    const layer = (id: string) => result.current.layers.find(l => l.map.id === id)!;
    expect(fetchMap).not.toHaveBeenCalled();
    act(() => result.current.setEnabled('service-routes', true));
    await waitFor(() => expect(layer('service-routes').vectorData?.features).toHaveLength(2));
    expect(layer('service-stops').enabled).toBe(false);
    act(() => result.current.setFormat('service-routes', 'pdf'));
    expect(layer('service-routes').format).toBe('vector');
    act(() => result.current.setRouteId('7'));
    expect(layer('service-routes').vectorData?.features.map(f => f.id)).toEqual(['7']);
    act(() => result.current.setEnabled('service-stops', true));
    await waitFor(() => expect(layer('service-stops').vectorData?.features).toHaveLength(1));
    act(() => result.current.inspect('service-stops::stop'));
    expect(result.current.selectedFeature?.properties.stopNumber).toBe('1234');
    rerender({ project: 'another' });
    expect(result.current.selected).toBeNull();
    rerender({ project: 'service' });
    expect(layer('service-routes').vectorData?.features.map(f => f.id)).toEqual(['7']);
    act(() => result.current.hideAll());
    expect(result.current.layers.some(l => l.enabled)).toBe(false);
    expect(fetchMap.mock.calls.every(([url]) => !url.includes('map.json'))).toBe(true);
  });

  it('shows stop identity and serving routes without a fabricated PDF legend', () => {
    render(<CityPolicyDetailsCard map={CITY_MAP_LAYERS.find(m => m.id === 'service-stops')!}
      feature={stops.features[0]} snapshot={stops} onClose={() => {}} />);
    expect(screen.getByText('WB Example')).toBeInTheDocument();
    expect(screen.getByText(/1234/)).toBeInTheDocument();
    expect(screen.getByText(/7.*Marda Loop/)).toBeInTheDocument();
    expect(screen.getByText(/9.*Dalhousie/)).toBeInTheDocument();
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
    expect(screen.queryByText(/Read the plan/)).not.toBeInTheDocument();
  });

  it('offers separate existing-service controls without a PDF source selector', async () => {
    const { result } = renderHook(() => useCityPolicyMaps('ui'), { wrapper });
    act(() => result.current.setEnabled('service-routes', true));
    await waitFor(() => expect(result.current.layers.find(l => l.map.id === 'service-routes')?.vectorData).toBeDefined());
    render(<CityPolicyMapsPanel state={result.current} />);
    expect(screen.getByLabelText('Show Calgary Transit routes')).toBeInTheDocument();
    expect(screen.getByLabelText('Show Calgary Transit stops')).toBeInTheDocument();
    expect(screen.getByLabelText('Choose transit route')).toBeInTheDocument();
    expect(screen.queryByText('Published PDF · compare')).not.toBeInTheDocument();
  });
});
