import '@testing-library/jest-dom/vitest';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';
import { api } from '@/services/api';
import { SiteAssessmentPanel, useSiteAssessment, type SiteAssessment } from './SiteAssessmentPanel';
import { useState } from 'react';

vi.mock('@/services/api', () => ({ api: { post: vi.fn() }, getApiErrorMessage: (error: Error) => error.message }));
const boundary = { id: 'site', zone_type: 'site_boundary', is_active_boundary: true,
  coordinates: [[-114.12, 51.01], [-114.119, 51.01], [-114.119, 51.011], [-114.12, 51.011]], properties: {} } as SiteZone;
const result: SiteAssessment = {
  boundary_id: 'site', roll_year: 2026, property_count: 2, partial_property_count: 1,
  missing_value_count: 0, complete: true, full_property_assessed_total: 500000,
  area_weighted_estimate: 350000, assessed_coverage_pct: 90, details_omitted: 0,
  warnings: ['Some properties extend beyond the site.'], source_url: 'https://data.calgary.ca/4bsw-nn7w',
  fetched_at: '2026-10-05T12:00:00Z', records: [{ roll_number: '1', address: 'Test property', property_type: 'LI',
    assessed_value: 500000, overlap_pct: 70, partial: true }],
};
function setup() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return (zones = [boundary], projectId = 'one') => <QueryClientProvider client={client}><SiteAssessmentPanel zones={zones} projectId={projectId} /></QueryClientProvider>;
}
beforeEach(() => vi.clearAllMocks());

describe('site assessments', () => {
  it('keeps the map value when the panel closes, supports hiding it, and clears it on a boundary edit', async () => {
    vi.mocked(api.post).mockResolvedValue({ data: result });
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    function Trial({ zones }: { zones: SiteZone[] }) {
      const state = useSiteAssessment(zones, 'one');
      const [open, setOpen] = useState(true);
      return <><button onClick={() => setOpen(value => !value)}>Toggle panel</button>
        {open && <SiteAssessmentPanel zones={zones} projectId="one" state={state} />}
        <output aria-label="Map value">{state.mapData?.districts[0].label}</output></>;
    }
    const view = (zones = [boundary]) => <QueryClientProvider client={client}><Trial zones={zones} /></QueryClientProvider>;
    const { rerender } = render(view());
    fireEvent.click(screen.getByRole('button', { name: 'Calculate assessed value' }));
    await waitFor(() => expect(screen.getByLabelText('Map value')).toHaveTextContent('$350,000 / Prorated site estimate · 2026'));
    fireEvent.click(screen.getByRole('switch', { name: 'Show assessed value on map' }));
    expect(screen.getByLabelText('Map value')).toBeEmptyDOMElement();
    fireEvent.click(screen.getByRole('switch', { name: 'Show assessed value on map' }));
    fireEvent.click(screen.getByRole('button', { name: 'Toggle panel' }));
    expect(screen.getByLabelText('Map value')).toHaveTextContent('$350,000');
    rerender(view([{ ...boundary, coordinates: boundary.coordinates.map(([x, y]) => [x + .001, y]) }]));
    expect(screen.getByLabelText('Map value')).toBeEmptyDOMElement();
    expect(api.post).toHaveBeenCalledOnce();
  });
  it('looks up on request and distinguishes official property totals from partial-site estimates', async () => {
    vi.mocked(api.post).mockResolvedValue({ data: result });
    render(setup()());
    expect(api.post).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'Calculate assessed value' }));
    expect(await screen.findByText('$500,000')).toBeInTheDocument();
    expect(screen.getByText('Within-boundary area estimate: $350,000')).toBeInTheDocument();
    expect(screen.getByText(/concept estimate/)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Calgary assessment data/ })).toHaveAttribute('href', result.source_url);
    expect(vi.mocked(api.post).mock.calls[0][1]).toEqual({ coordinates: boundary.coordinates });
  });
  it('hides a previous total immediately after edits, switches or deletion and ignores late responses', async () => {
    let finish: (response: { data: SiteAssessment }) => void = () => {};
    vi.mocked(api.post).mockImplementationOnce(() => new Promise(resolve => { finish = resolve; }));
    const view = setup(); const { rerender } = render(view());
    fireEvent.click(screen.getByRole('button', { name: 'Calculate assessed value' }));
    await waitFor(() => expect(api.post).toHaveBeenCalledOnce());
    rerender(view([{ ...boundary, coordinates: boundary.coordinates.map(([x, y]) => [x + .001, y]) }]));
    await act(async () => finish({ data: result }));
    expect(screen.queryByText('$500,000')).not.toBeInTheDocument();
    rerender(view([boundary], 'two'));
    expect(screen.queryByText('$500,000')).not.toBeInTheDocument();
    rerender(view([]));
    expect(screen.getByRole('button', { name: 'Calculate assessed value' })).toBeDisabled();
  });
  it('recovers from an outage without automatic repeated requests', async () => {
    vi.mocked(api.post).mockRejectedValueOnce(new Error('Temporary outage')).mockResolvedValue({ data: result });
    render(setup()());
    fireEvent.click(screen.getByRole('button', { name: 'Calculate assessed value' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Temporary outage');
    expect(api.post).toHaveBeenCalledOnce();
    fireEvent.click(screen.getByRole('button', { name: 'Calculate assessed value' }));
    expect(await screen.findByText('$500,000')).toBeInTheDocument();
  });
  it('keeps missing-value subtotals visible and restores a cached result when the panel reopens', async () => {
    vi.mocked(api.post).mockResolvedValue({ data: { ...result, complete: false, missing_value_count: 1 } });
    const view = setup(); const first = render(view());
    fireEvent.click(screen.getByRole('button', { name: 'Calculate assessed value' }));
    expect(await screen.findByText('Known property assessments · incomplete subtotal')).toBeInTheDocument();
    first.unmount(); render(view());
    expect(screen.getByText('$500,000')).toBeInTheDocument();
    expect(api.post).toHaveBeenCalledOnce();
  });
});
