import '@testing-library/jest-dom/vitest';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';
import { ZoningLabelsControls } from './ZoningLabelsControls';
import { useZoningLabels } from './useZoningLabels';
import { fetchZoningLabels } from './zoningLabels';

vi.mock('./zoningLabels', async original => ({ ...await original<object>(), fetchZoningLabels: vi.fn() }));
const boundary = { id: 'site', zone_type: 'site_boundary', is_active_boundary: true, coordinates: [[-114.12, 51.01], [-114.119, 51.01], [-114.119, 51.011], [-114.12, 51.011]], properties: {} } as SiteZone;
function App({ id = 'one', zones = [boundary], area }: { id?: string; zones?: SiteZone[]; area?: number[][] }) {
  const state = useZoningLabels(id, zones, area);
  return <><ZoningLabelsControls state={state} /><output data-testid="data">{state.data?.loadedAt ?? 'none'}</output></>;
}
function setup() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return (props: Parameters<typeof App>[0] = {}) => <QueryClientProvider client={client}><App {...props} /></QueryClientProvider>;
}
beforeEach(() => { localStorage.clear(); vi.clearAllMocks(); });

describe('zoning label controls', () => {
  it('loads zoning around the map without an authored boundary', async () => {
    vi.mocked(fetchZoningLabels).mockResolvedValue({ districts: [], bounds: [-114.12,51.01,-114.119,51.011], loadedAt: 'exploring' });
    render(setup()({ zones: [], area: boundary.coordinates }));
    expect(screen.getByRole('switch')).toBeEnabled();
    fireEvent.click(screen.getByRole('switch'));
    await waitFor(() => expect(screen.getByTestId('data')).toHaveTextContent('exploring'));
    expect(fetchZoningLabels).toHaveBeenCalledWith(boundary.coordinates, expect.any(AbortSignal));
    expect(screen.getByText(/around the map centre/)).toBeInTheDocument();
  });
  it('supports transparent and solid endpoints without hiding boundaries or labels', async () => {
    vi.mocked(fetchZoningLabels).mockResolvedValue({ districts: [], bounds: [-114.12, 51.01, -114.119, 51.011], loadedAt: 'ready' });
    render(setup()());
    fireEvent.click(screen.getByRole('switch'));
    const slider = screen.getByRole('slider', { name: 'Fill opacity' });
    expect(slider).toHaveAttribute('min', '0');
    expect(slider).toHaveAttribute('max', '100');
    for (const percent of [0, 100, 40]) {
      fireEvent.change(slider, { target: { value: String(percent) } });
      expect(slider).toHaveValue(String(percent));
      expect(screen.getByLabelText('Boundaries')).toBeChecked();
      expect(screen.getByLabelText('District labels')).toBeChecked();
      expect(JSON.parse(localStorage.getItem('cityprompt:parcel-zoning:one')!).fillOpacity).toBe(percent / 100);
    }
    await waitFor(() => expect(fetchZoningLabels).toHaveBeenCalledOnce());
  });
  it('switches the whole map off and on without losing appearance or refetching', async () => {
    vi.mocked(fetchZoningLabels).mockResolvedValue({ districts: [], bounds: [-114.12, 51.01, -114.119, 51.011], loadedAt: 'ready' });
    const view = setup(); const { unmount } = render(view());
    const toggle = screen.getByRole('switch', { name: 'Show land-use map' });
    expect(toggle).not.toBeChecked();
    expect(screen.queryByLabelText('Colour fills')).not.toBeInTheDocument();
    fireEvent.click(toggle);
    await screen.findByText('No published zoning areas intersect this boundary.');
    expect(screen.getByLabelText('District labels')).toBeChecked();
    expect(screen.getByLabelText('Boundaries')).toBeChecked();
    expect(screen.getByLabelText('Colour fills')).toBeChecked();
    fireEvent.change(screen.getByRole('slider', { name: 'Fill opacity' }), { target: { value: '37' } });
    fireEvent.click(screen.getByLabelText('District labels'));
    fireEvent.click(toggle);
    expect(screen.queryByLabelText('Boundaries')).not.toBeInTheDocument();
    unmount(); render(view());
    expect(screen.getByRole('switch')).not.toBeChecked();
    fireEvent.click(screen.getByRole('switch'));
    expect(screen.getByRole('slider')).toHaveValue('37');
    expect(screen.getByLabelText('District labels')).not.toBeChecked();
    expect(screen.getByLabelText('Boundaries')).toBeChecked();
    expect(fetchZoningLabels).toHaveBeenCalledOnce();
  });
  it('explains codes once per designation and keeps different modifiers distinct', async () => {
    vi.mocked(fetchZoningLabels).mockResolvedValue({
      districts: [
        { id: 'a', label: 'R-CG', description: 'Residential - Grade-Oriented Infill', anchor: [-114.12, 51.01], polygon: [boundary.coordinates as [number, number][]] },
        { id: 'b', label: 'R-CG', description: 'Residential - Grade-Oriented Infill', anchor: [-114.12, 51.01], polygon: [boundary.coordinates as [number, number][]] },
        { id: 'c', label: 'M-C1 d75', description: 'Multi-Residential - Contextual Low Profile', anchor: [-114.12, 51.01], polygon: [boundary.coordinates as [number, number][]] },
        { id: 'd', label: 'M-C1 d100', description: 'Multi-Residential - Contextual Low Profile', anchor: [-114.12, 51.01], polygon: [boundary.coordinates as [number, number][]] },
        { id: 'e', label: 'DC48Z84', anchor: [-114.12, 51.01], polygon: [boundary.coordinates as [number, number][]] },
      ], bounds: [-114.12, 51.01, -114.119, 51.011], loadedAt: 'ready',
    });
    render(setup()());
    fireEvent.click(screen.getByLabelText('Show land-use map'));
    const guide = await screen.findByText('District legend (4)');
    expect(guide).toBeInTheDocument();
    expect(screen.getAllByText('Residential - Grade-Oriented Infill')).toHaveLength(1);
    expect(screen.getByText('M-C1 d75')).toBeInTheDocument();
    expect(screen.getByText('M-C1 d100')).toBeInTheDocument();
    expect(screen.getByText('Description not supplied by Calgary.')).toBeInTheDocument();
    fireEvent.click(screen.getByLabelText('Show land-use map'));
    expect(screen.queryByText('District legend (4)')).not.toBeInTheDocument();
  });
  it('fetches only when requested and has no lot-line control', async () => {
    vi.mocked(fetchZoningLabels).mockResolvedValue({ districts: [], bounds: [-114.12, 51.01, -114.119, 51.011], loadedAt: 'ready' });
    render(setup()());
    expect(fetchZoningLabels).not.toHaveBeenCalled();
    expect(screen.queryByLabelText('Parcel boundaries')).not.toBeInTheDocument();
    fireEvent.click(screen.getByLabelText('Show land-use map'));
    await waitFor(() => expect(screen.getByTestId('data')).toHaveTextContent('ready'));
    fireEvent.click(screen.getByLabelText('Show land-use map'));
    expect(screen.getByLabelText('Show land-use map')).not.toBeChecked();
    expect(fetchZoningLabels).toHaveBeenCalledOnce();
  });
  it('preserves the previous label preference without enabling old lot lines', () => {
    localStorage.setItem('cityprompt:parcel-zoning:one', JSON.stringify({ labels: true, lines: true }));
    vi.mocked(fetchZoningLabels).mockReturnValue(new Promise(() => {}));
    render(setup()());
    expect(screen.getByLabelText('Show land-use map')).toBeChecked();
    expect(screen.getAllByRole('checkbox')).toHaveLength(3);
    expect(screen.getByLabelText('Boundaries')).not.toBeChecked();
  });
  it('loads outlines independently, reuses code data, and retains the district preference', async () => {
    vi.mocked(fetchZoningLabels).mockResolvedValue({ districts: [], bounds: [-114.12, 51.01, -114.119, 51.011], loadedAt: 'ready' });
    localStorage.setItem('cityprompt:parcel-zoning:one', JSON.stringify({ enabled: true, labels: false, districtLines: true, fill: false }));
    const view = setup(); const { unmount } = render(view());
    await waitFor(() => expect(screen.getByTestId('data')).toHaveTextContent('ready'));
    expect(screen.getByLabelText('District labels')).not.toBeChecked();
    fireEvent.click(screen.getByLabelText('District labels'));
    expect(fetchZoningLabels).toHaveBeenCalledOnce();
    expect(JSON.parse(localStorage.getItem('cityprompt:parcel-zoning:one')!)).toEqual({ enabled: true, labels: true, districtLines: true, fill: false, fillOpacity: 0.4 });
    unmount(); render(view());
    expect(screen.getByLabelText('Boundaries')).toBeChecked();
  });
  it('does not reuse old site geometry after boundary changes or deletion', async () => {
    let resolveSecond: (value: Awaited<ReturnType<typeof fetchZoningLabels>>) => void = () => {};
    vi.mocked(fetchZoningLabels).mockResolvedValueOnce({ districts: [], bounds: [-114.12, 51.01, -114.119, 51.011], loadedAt: 'first' })
      .mockImplementationOnce(() => new Promise(resolve => { resolveSecond = resolve; }));
    const view = setup(); const { rerender } = render(view());
    fireEvent.click(screen.getByLabelText('Show land-use map'));
    await waitFor(() => expect(screen.getByTestId('data')).toHaveTextContent('first'));
    rerender(view({ zones: [{ ...boundary, coordinates: boundary.coordinates.map(([x, y]) => [x + 0.001, y]) }] }));
    expect(screen.getByTestId('data')).toHaveTextContent('none');
    rerender(view({ zones: [] }));
    await act(async () => resolveSecond({ districts: [], bounds: [-114.12, 51.01, -114.119, 51.011], loadedAt: 'late' }));
    expect(screen.getByTestId('data')).toHaveTextContent('none');
    expect(screen.getByLabelText('Show land-use map')).toBeDisabled();
  });
  it('recovers from failures and scopes preferences by project', async () => {
    vi.mocked(fetchZoningLabels).mockRejectedValueOnce(new Error('Temporary outage')).mockResolvedValue({ districts: [], bounds: [-114.12, 51.01, -114.119, 51.011], loadedAt: 'ready' });
    const view = setup(); const { rerender } = render(view());
    fireEvent.click(screen.getByLabelText('Show land-use map'));
    expect(await screen.findByRole('alert')).toHaveTextContent('Temporary outage');
    fireEvent.click(screen.getByRole('button', { name: 'Retry zoning data' }));
    await waitFor(() => expect(screen.getByTestId('data')).toHaveTextContent('ready'));
    rerender(view({ id: 'two' })); expect(screen.getByLabelText('Show land-use map')).not.toBeChecked();
    rerender(view()); expect(screen.getByLabelText('Show land-use map')).toBeChecked();
  });
});
