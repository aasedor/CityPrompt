import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';
import { RileyPolicyPanel } from './RileyPolicyPanel';
import { useRileyPolicy } from './useRileyPolicy';
import { loadRileyPolicy } from './rileyPolicy';

vi.mock('./rileyPolicy', async original => ({ ...await original<object>(), loadRileyPolicy: vi.fn() }));
const site = { id: 'site', zone_type: 'site_boundary', is_active_boundary: true, coordinates: [[-114.10,51.055],[-114.09,51.055],[-114.09,51.06],[-114.10,51.06]], properties: {} } as SiteZone;
function App({ projectId = 'one', zones = [site] }: { projectId?: string; zones?: SiteZone[] }) {
  const state = useRileyPolicy(projectId, zones);
  return <><RileyPolicyPanel state={state} /><output data-testid="map">{state.data ? 'visible' : 'absent'}</output></>;
}
function setup() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return (props: Parameters<typeof App>[0] = {}) => <QueryClientProvider client={client}><App {...props} /></QueryClientProvider>;
}
beforeEach(async () => {
  localStorage.clear(); vi.clearAllMocks();
  const actual = await vi.importActual<typeof import('./rileyPolicy')>('./rileyPolicy');
  vi.mocked(loadRileyPolicy).mockResolvedValue(await actual.loadRileyPolicy());
});

describe('Riley policy controls', () => {
  it('loads on demand, toggles the entire map, and persists opacity endpoints and site clipping', async () => {
    const view = setup(); const { unmount } = render(view());
    expect(loadRileyPolicy).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('switch', { name: 'Show Riley policy map' }));
    await screen.findByText('Urban form legend');
    expect(screen.getByTestId('map')).toHaveTextContent('visible');
    for (const value of [0, 100, 45]) {
      fireEvent.change(screen.getByRole('slider'), { target: { value: String(value) } });
      expect(screen.getByRole('slider')).toHaveValue(String(value));
    }
    fireEvent.click(screen.getByLabelText('Only show inside my site'));
    fireEvent.click(screen.getByRole('switch'));
    expect(screen.getByTestId('map')).toHaveTextContent('absent');
    unmount(); render(view());
    expect(screen.getByRole('switch')).not.toBeChecked();
    fireEvent.click(screen.getByRole('switch'));
    expect(screen.getByRole('slider')).toHaveValue('45');
    expect(screen.getByLabelText('Only show inside my site')).toBeChecked();
    expect(loadRileyPolicy).toHaveBeenCalledOnce();
  });
  it('does not carry visibility across projects or display stale geometry after site deletion', async () => {
    const view = setup(); const { rerender } = render(view());
    fireEvent.click(screen.getByRole('switch')); await screen.findByText('Urban form legend');
    rerender(view({ projectId: 'two' }));
    expect(screen.getByRole('switch')).not.toBeChecked();
    expect(screen.getByTestId('map')).toHaveTextContent('absent');
    rerender(view({ zones: [] }));
    expect(screen.getByTestId('map')).toHaveTextContent('absent');
    expect(screen.getByText(/Draw a site boundary/)).toBeInTheDocument();
  });
  it('reports unavailable areas and can recover from a load error', async () => {
    vi.mocked(loadRileyPolicy).mockRejectedValueOnce(new Error('Chunk unavailable'));
    render(setup()()); fireEvent.click(screen.getByRole('switch'));
    await screen.findByRole('alert');
    expect(screen.getByTestId('map')).toHaveTextContent('absent');
    fireEvent.click(screen.getByRole('button', { name: 'Retry policy map' }));
    await waitFor(() => expect(screen.getByTestId('map')).toHaveTextContent('visible'));
  });
});
