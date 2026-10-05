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
function App({ id = 'one', zones = [boundary] }: { id?: string; zones?: SiteZone[] }) {
  const state = useZoningLabels(id, zones);
  return <><ZoningLabelsControls state={state} /><output data-testid="data">{state.data?.loadedAt ?? 'none'}</output></>;
}
function setup() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return (props: { id?: string; zones?: SiteZone[] } = {}) => <QueryClientProvider client={client}><App {...props} /></QueryClientProvider>;
}
beforeEach(() => { localStorage.clear(); vi.clearAllMocks(); });

describe('zoning label controls', () => {
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
    fireEvent.click(screen.getByLabelText('Show zoning codes'));
    const guide = await screen.findByText('Code guide (4)');
    fireEvent.click(guide);
    expect(screen.getAllByText('Residential - Grade-Oriented Infill')).toHaveLength(1);
    expect(screen.getByText('M-C1 d75')).toBeInTheDocument();
    expect(screen.getByText('M-C1 d100')).toBeInTheDocument();
    expect(screen.getByText('Description not supplied by Calgary.')).toBeInTheDocument();
    fireEvent.click(screen.getByLabelText('Show zoning codes'));
    expect(screen.queryByText('Code guide (4)')).not.toBeInTheDocument();
  });
  it('fetches only when requested and has no lot-line control', async () => {
    vi.mocked(fetchZoningLabels).mockResolvedValue({ districts: [], bounds: [-114.12, 51.01, -114.119, 51.011], loadedAt: 'ready' });
    render(setup()());
    expect(fetchZoningLabels).not.toHaveBeenCalled();
    expect(screen.queryByLabelText('Parcel boundaries')).not.toBeInTheDocument();
    fireEvent.click(screen.getByLabelText('Show zoning codes'));
    await waitFor(() => expect(screen.getByTestId('data')).toHaveTextContent('ready'));
    fireEvent.click(screen.getByLabelText('Show zoning codes'));
    expect(screen.getByLabelText('Show zoning codes')).not.toBeChecked();
    expect(fetchZoningLabels).toHaveBeenCalledOnce();
  });
  it('preserves the previous label preference without enabling old lot lines', () => {
    localStorage.setItem('cityprompt:parcel-zoning:one', JSON.stringify({ labels: true, lines: true }));
    vi.mocked(fetchZoningLabels).mockReturnValue(new Promise(() => {}));
    render(setup()());
    expect(screen.getByLabelText('Show zoning codes')).toBeChecked();
    expect(screen.getAllByRole('checkbox')).toHaveLength(2);
    expect(screen.getByLabelText('Show zoning boundaries')).not.toBeChecked();
  });
  it('loads outlines independently, reuses code data, and retains the district preference', async () => {
    vi.mocked(fetchZoningLabels).mockResolvedValue({ districts: [], bounds: [-114.12, 51.01, -114.119, 51.011], loadedAt: 'ready' });
    const view = setup(); const { unmount } = render(view());
    fireEvent.click(screen.getByLabelText('Show zoning boundaries'));
    await waitFor(() => expect(screen.getByTestId('data')).toHaveTextContent('ready'));
    expect(screen.getByLabelText('Show zoning codes')).not.toBeChecked();
    fireEvent.click(screen.getByLabelText('Show zoning codes'));
    expect(fetchZoningLabels).toHaveBeenCalledOnce();
    expect(JSON.parse(localStorage.getItem('cityprompt:parcel-zoning:one')!)).toEqual({ labels: true, districtLines: true });
    unmount(); render(view());
    expect(screen.getByLabelText('Show zoning boundaries')).toBeChecked();
  });
  it('does not reuse old site geometry after boundary changes or deletion', async () => {
    let resolveSecond: (value: Awaited<ReturnType<typeof fetchZoningLabels>>) => void = () => {};
    vi.mocked(fetchZoningLabels).mockResolvedValueOnce({ districts: [], bounds: [-114.12, 51.01, -114.119, 51.011], loadedAt: 'first' })
      .mockImplementationOnce(() => new Promise(resolve => { resolveSecond = resolve; }));
    const view = setup(); const { rerender } = render(view());
    fireEvent.click(screen.getByLabelText('Show zoning codes'));
    await waitFor(() => expect(screen.getByTestId('data')).toHaveTextContent('first'));
    rerender(view({ zones: [{ ...boundary, coordinates: boundary.coordinates.map(([x, y]) => [x + 0.001, y]) }] }));
    expect(screen.getByTestId('data')).toHaveTextContent('none');
    rerender(view({ zones: [] }));
    await act(async () => resolveSecond({ districts: [], bounds: [-114.12, 51.01, -114.119, 51.011], loadedAt: 'late' }));
    expect(screen.getByTestId('data')).toHaveTextContent('none');
    expect(screen.getByLabelText('Show zoning codes')).toBeDisabled();
  });
  it('recovers from failures and scopes preferences by project', async () => {
    vi.mocked(fetchZoningLabels).mockRejectedValueOnce(new Error('Temporary outage')).mockResolvedValue({ districts: [], bounds: [-114.12, 51.01, -114.119, 51.011], loadedAt: 'ready' });
    const view = setup(); const { rerender } = render(view());
    fireEvent.click(screen.getByLabelText('Show zoning codes'));
    expect(await screen.findByRole('alert')).toHaveTextContent('Temporary outage');
    fireEvent.click(screen.getByRole('button', { name: 'Retry zoning data' }));
    await waitFor(() => expect(screen.getByTestId('data')).toHaveTextContent('ready'));
    rerender(view({ id: 'two' })); expect(screen.getByLabelText('Show zoning codes')).not.toBeChecked();
    rerender(view()); expect(screen.getByLabelText('Show zoning codes')).toBeChecked();
  });
});
