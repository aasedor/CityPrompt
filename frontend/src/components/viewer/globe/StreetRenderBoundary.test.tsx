import { act, cleanup, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';
import { nativeStreetRevision } from './nativeStreetReadiness';
import { StreetRenderBoundary, StreetRenderProblem } from './StreetRenderBoundary';

const zone: SiteZone = { id: 'brt', name: 'BRT corridor', project_id: 'test', zone_type: 'road',
  color: '#aaa', sort_order: 0, created_at: '1', updated_at: '1', coordinates: [[0, 0], [0, 1]],
  properties: { road_selected_variant_id: 'brt_bus_rapid_transit_corridor_v0' } };
function Geometry({ fails }: { fails: boolean }) {
  if (fails) throw new Error('BRT needs a straight route 100–480 m long.');
  return <span>Detailed street</span>;
}
const expectedError = (event: ErrorEvent) => { if (event.message.includes('BRT needs a straight route')) event.preventDefault(); };
beforeEach(() => window.addEventListener('error', expectedError));
afterEach(() => { cleanup(); vi.restoreAllMocks(); window.removeEventListener('error', expectedError); });

it('contains geometry failures, keeps editing controls mounted, and recovers after a route edit', async () => {
  vi.spyOn(console, 'error').mockImplementation(() => {});
  const listener = vi.fn();
  window.addEventListener('cityprompt:native-street-error', listener);
  try {
    const view = (route: SiteZone, fails: boolean) => <>
      <button>Adjust route</button><StreetRenderBoundary zone={route}><Geometry fails={fails} /></StreetRenderBoundary>
    </>;
    const { rerender } = render(view(zone, true));
    expect(screen.getByText('Adjust route')).toBeTruthy();
    expect(screen.queryByText('Detailed street')).toBeNull();
    await waitFor(() => expect(listener).toHaveBeenCalledOnce());
    expect(listener.mock.calls[0][0].detail).toMatchObject({ zoneId: 'brt', revision: nativeStreetRevision(zone) });
    expect(listener.mock.calls[0][0].detail.message).toContain('100–480');
    rerender(view({ ...zone, coordinates: [[0, 0], [0, 2]] }, false));
    expect(screen.getByText('Detailed street')).toBeTruthy();
  } finally { window.removeEventListener('cityprompt:native-street-error', listener); }
});

it('supports retry without a route edit and does not publish draft failures as saved errors', async () => {
  vi.spyOn(console, 'error').mockImplementation(() => {});
  const listener = vi.fn();
  window.addEventListener('cityprompt:native-street-error', listener);
  try {
    let fails = true;
    const TransientGeometry = () => <Geometry fails={fails} />;
    render(<StreetRenderBoundary zone={zone} preview><TransientGeometry /></StreetRenderBoundary>);
    await act(async () => { await new Promise(resolve => setTimeout(resolve, 10)); });
    expect(listener).not.toHaveBeenCalled();
    fails = false;
    act(() => { window.dispatchEvent(new Event('cityprompt:retry-native-streets')); });
    expect(screen.getByText('Detailed street')).toBeTruthy();
  } finally { window.removeEventListener('cityprompt:native-street-error', listener); }
});

it('reports a rejected saved route even when there is no builder exception', async () => {
  vi.spyOn(console, 'error').mockImplementation(() => {});
  const listener = vi.fn();
  window.addEventListener('cityprompt:native-street-error', listener);
  try {
    render(<StreetRenderProblem zone={zone} message="Keep this route straight." />);
    await waitFor(() => expect(listener).toHaveBeenCalledOnce());
    expect(listener.mock.calls[0][0].detail.message).toContain('Select the street');
  } finally { window.removeEventListener('cityprompt:native-street-error', listener); }
});
