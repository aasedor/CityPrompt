import '@testing-library/jest-dom/vitest';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';
import { ParcelZoningControls } from './ParcelZoningControls';
import { useParcelZoning } from './useParcelZoning';
import { fetchParcelZoning } from './parcelZoning';

vi.mock('./parcelZoning', async original => ({ ...await original<object>(), fetchParcelZoning: vi.fn() }));
const boundary = { id: 'site', zone_type: 'site_boundary', is_active_boundary: true, coordinates: [[-114.12, 51.01], [-114.119, 51.01], [-114.119, 51.011], [-114.12, 51.011]], properties: {} } as SiteZone;
function App({ id = 'one', zones = [boundary] }: { id?: string; zones?: SiteZone[] }) {
  const state = useParcelZoning(id, zones);
  return <><ParcelZoningControls state={state} /><output data-testid="data">{state.data?.loadedAt ?? 'none'}</output></>;
}
function setup() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return (props: { id?: string; zones?: SiteZone[] } = {}) => <QueryClientProvider client={client}><App {...props} /></QueryClientProvider>;
}
beforeEach(() => { localStorage.clear(); vi.clearAllMocks(); });

describe('parcel overlay controls', () => {
  it('does no fetch until requested and keeps boundaries and labels independent', async () => {
    vi.mocked(fetchParcelZoning).mockResolvedValue({ parcels: [], bounds: [-114.12, 51.01, -114.119, 51.011], loadedAt: '2026-10-02' });
    render(setup()());
    expect(fetchParcelZoning).not.toHaveBeenCalled();
    fireEvent.click(screen.getByLabelText('Land-use labels'));
    await waitFor(() => expect(fetchParcelZoning).toHaveBeenCalledOnce());
    expect(screen.getByLabelText('Parcel boundaries')).not.toBeChecked();
    fireEvent.click(screen.getByLabelText('Parcel boundaries'));
    fireEvent.click(screen.getByLabelText('Land-use labels'));
    expect(screen.getByLabelText('Parcel boundaries')).toBeChecked();
    expect(screen.getByLabelText('Land-use labels')).not.toBeChecked();
    expect(fetchParcelZoning).toHaveBeenCalledOnce();
  });
  it('does not reuse old site geometry after boundary changes or deletion', async () => {
    let resolveSecond: (value: Awaited<ReturnType<typeof fetchParcelZoning>>) => void = () => {};
    vi.mocked(fetchParcelZoning).mockResolvedValueOnce({ parcels: [], bounds: [-114.12, 51.01, -114.119, 51.011], loadedAt: 'first' })
      .mockImplementationOnce(() => new Promise(resolve => { resolveSecond = resolve; }));
    const view = setup(); const { rerender } = render(view());
    fireEvent.click(screen.getByLabelText('Parcel boundaries'));
    await waitFor(() => expect(screen.getByTestId('data')).toHaveTextContent('first'));
    rerender(view({ zones: [{ ...boundary, coordinates: boundary.coordinates.map(([x, y]) => [x + 0.001, y]) }] }));
    expect(screen.getByTestId('data')).toHaveTextContent('none');
    rerender(view({ zones: [] }));
    await act(async () => resolveSecond({ parcels: [], bounds: [-114.12, 51.01, -114.119, 51.011], loadedAt: 'late' }));
    expect(screen.getByTestId('data')).toHaveTextContent('none');
    expect(screen.getByLabelText('Parcel boundaries')).toBeDisabled();
  });
  it('recovers from failures and scopes preferences by project', async () => {
    vi.mocked(fetchParcelZoning).mockRejectedValueOnce(new Error('Temporary outage')).mockResolvedValue({ parcels: [], bounds: [-114.12, 51.01, -114.119, 51.011], loadedAt: 'ready' });
    const view = setup(); const { rerender } = render(view());
    fireEvent.click(screen.getByLabelText('Land-use labels'));
    expect(await screen.findByRole('alert')).toHaveTextContent('Temporary outage');
    fireEvent.click(screen.getByRole('button', { name: 'Retry parcel data' }));
    await waitFor(() => expect(screen.getByTestId('data')).toHaveTextContent('ready'));
    rerender(view({ id: 'two' })); expect(screen.getByLabelText('Land-use labels')).not.toBeChecked();
    rerender(view()); expect(screen.getByLabelText('Land-use labels')).toBeChecked();
  });
});
