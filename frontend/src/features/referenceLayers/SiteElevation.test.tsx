import '@testing-library/jest-dom/vitest';
import { useState } from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { api } from '@/services/api';
import { SiteElevation } from './SiteElevation';

vi.mock('@/services/api', () => ({ api: { get: vi.fn() } }));
function setup(child = <SiteElevation lat={51} lon={-114} />) {
  return render(<QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>{child}</QueryClientProvider>);
}
const available = { elevation: 1048.6, ellipsoidal_height: 1023.6, resolution: 19.1, status: 'available', source: 'google_elevation', vertical_reference: 'mean_sea_level', approximate: true };
describe('Optional site elevation', () => {
  beforeEach(() => vi.clearAllMocks());
  it('shows approximate provider MSL height, with resolution and source in optional details', async () => {
    vi.mocked(api.get).mockResolvedValue({ data: available });
    setup();
    await screen.findByText('Approx. 1,049 m above sea level');
    fireEvent.click(screen.getByText('About this estimate'));
    expect(screen.getByText(/Source: Google Elevation/)).toBeVisible();
    expect(screen.getByText(/Data resolution: about 19 m/)).toBeVisible();
    expect(screen.queryByText(/1,024 m/)).not.toBeInTheDocument();
    expect(api.get).toHaveBeenCalledWith('/api/v1/elevation', expect.objectContaining({ params: { lat: 51, lng: -114 } }));
  });
  it.each([
    { elevation: 0, ellipsoidal_height: -25, resolution: 1000, status: 'unavailable', source: 'renderer_fallback' },
    { elevation: 0, ellipsoidal_height: -25, resolution: 1000 },
  ])('never presents a renderer fallback or old API response as actual elevation', async (data) => {
    vi.mocked(api.get).mockResolvedValue({ data });
    setup();
    await screen.findByText('Elevation unavailable');
    expect(screen.queryByText(/m above sea level/)).not.toBeInTheDocument();
    expect(screen.getByText('Try again')).toBeEnabled();
  });
  it('allows a network-error retry and recognizes genuine sea level', async () => {
    vi.mocked(api.get).mockRejectedValueOnce(new Error('offline')).mockResolvedValueOnce({ data: { ...available, elevation: 0 } });
    setup();
    await screen.findByText('Elevation unavailable');
    fireEvent.click(screen.getByRole('button', { name: 'Try again' }));
    await screen.findByText('Approx. 0 m above sea level');
    expect(api.get).toHaveBeenCalledTimes(2);
  });
  it('waits until the Layers content mounts, reuses cached data and does not request invalid locations', async () => {
    vi.mocked(api.get).mockResolvedValue({ data: available });
    function Layers() {
      const [open, setOpen] = useState(false);
      return <><button onClick={() => setOpen(!open)}>Layers</button>{open && <SiteElevation lat={51} lon={-114} />}</>;
    }
    const view = setup(<Layers />);
    expect(api.get).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'Layers' }));
    await screen.findByText('Approx. 1,049 m above sea level');
    fireEvent.click(screen.getByRole('button', { name: 'Layers' }));
    fireEvent.click(screen.getByRole('button', { name: 'Layers' }));
    await waitFor(() => expect(api.get).toHaveBeenCalledTimes(1));
    view.unmount();
    setup(<SiteElevation lat={null} lon={null} />);
    expect(screen.getByText(/Add a project location/)).toBeInTheDocument();
    expect(api.get).toHaveBeenCalledTimes(1);
  });
});
