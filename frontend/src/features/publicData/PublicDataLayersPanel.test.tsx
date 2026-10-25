import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { afterEach, describe, expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';
import { usePublicDataLayers } from './usePublicDataLayers';
import { PublicDataLayersPanel } from './PublicDataLayersPanel';

afterEach(() => vi.unstubAllGlobals());
const zones = [{ id: 'boundary', zone_type: 'site_boundary', coordinates: [[-114.08, 51.04], [-114.079, 51.04], [-114.079, 51.041]] }] as SiteZone[];
function renderPanel(site = zones) {
  function Subject() { return <PublicDataLayersPanel state={usePublicDataLayers('project', site)} />; }
  render(<QueryClientProvider client={new QueryClient()}><Subject /></QueryClientProvider>);
  fireEvent.click(screen.getByText('Optional public data'));
}

describe('public data tick boxes', () => {
  it('uses accessible checkboxes and shows status, limitations, empty results and removal', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => new Response('[]')));
    renderPanel();
    const schools = screen.getByRole('checkbox', { name: 'Schools' });
    expect(schools).not.toBeChecked();
    expect(fetch).not.toHaveBeenCalled();
    fireEvent.click(schools);
    expect(schools).toBeChecked();
    await waitFor(() => expect(screen.getByText(/No displayable records/)).toBeInTheDocument());
    expect(screen.getByText(/enrolment capacity/)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Schools source' })).toHaveAttribute('href', 'https://data.calgary.ca/d/fd9t-tdn2');
    fireEvent.click(schools);
    expect(screen.queryByText(/No displayable records/)).not.toBeInTheDocument();
  });

  it('offers source cards independently of map coverage and makes no external request', () => {
    vi.stubGlobal('fetch', vi.fn());
    renderPanel([]);
    expect(screen.getByRole('checkbox', { name: 'Schools' })).toBeDisabled();
    fireEvent.click(screen.getByRole('checkbox', { name: 'Rental market context (CMHC)' }));
    expect(screen.getByRole('link', { name: 'Open CMHC rental tables' })).toHaveAttribute('href', expect.stringContaining('cmhc-schl.gc.ca'));
    expect(screen.getByText(/area-level statistics/)).toBeInTheDocument();
    expect(fetch).not.toHaveBeenCalled();
  });
});
