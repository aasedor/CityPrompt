import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, within } from '@testing-library/react';
import { afterAll, expect, it, vi } from 'vitest';

// Exercise the actual local catalogue without changing production pilot gates.
vi.stubEnv('DEV', true);
vi.stubEnv('MODE', 'development');
const { PlacementPalette } = await import('./PlacementPalette');
const { CLASSROOM_CHOICES } = await import('./canonicalCatalogue');
const { cataloguePresentationFor } = await import('./cataloguePresentation');
afterAll(() => vi.unstubAllEnvs());

const recentBridgeIds = ['stone_arch_road_bridge_route_v1','timber_covered_bridge_route_v1',
  'tied_arch_shared_bridge_route_v1','planted_green_bridge_route_v1','brick_arch_viaduct_route_v1',
  'rail_through_truss_route_v1','steel_truss_road_bridge_route_v1','cable_stayed_cycle_ring_route_v1',
  'swooping_cycle_flyover_route_v1','weathering_steel_v_footbridge_route_v1'];
const bridgeChoice = (id: string) => CLASSROOM_CHOICES.find(c => c.placements.some(asset => asset.id===id))!;

it.each(recentBridgeIds)('shows and selects %s through the main Bridges category without a review toggle', id => {
  const choice = bridgeChoice(id);
  expect(choice).toBeDefined();
  const asset = choice.placements[0], pick = vi.fn(), draw = vi.fn();
  render(<PlacementPalette selected={null} onPick={pick} onPickStreet={draw} onPickCanonical={draw}
    onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()} />);
  fireEvent.click(screen.getByRole('button', { name: 'Streets' }));
  fireEvent.click(screen.getByRole('button', { name: 'Browse Bridges & viaducts' }));
  expect(screen.getByRole('heading', { name: 'Bridges & viaducts' })).toBeVisible();
  const label = cataloguePresentationFor(asset.id)?.label ?? asset.label;
  fireEvent.click(screen.getByRole('button', { name: `Expand details for ${label}` }));
  const card = screen.getByLabelText(`Variant for ${label}`).closest('article')!;
  expect(asset.kind).toBe('street');
  expect(asset.properties.lane_count).toBe(id==='stone_arch_road_bridge_route_v1'?4:id==='steel_truss_road_bridge_route_v1'?2:0);
  expect(within(card).queryByRole('button', {name:'Place fixed review segment'})).not.toBeInTheDocument();
  fireEvent.click(within(card).getByRole('button', { name: 'Choose & draw route' }));
  expect(draw).toHaveBeenCalledExactlyOnceWith(asset); expect(pick).not.toHaveBeenCalled();
});

it('finds imported bridges in a normal street search without a review toggle', () => {
  render(<PlacementPalette selected={null} onPick={vi.fn()} onPickStreet={vi.fn()} onPickCanonical={vi.fn()}
    onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()} />);
  fireEvent.click(screen.getByRole('button', { name: 'Streets' }));
  fireEvent.change(screen.getByLabelText('Search objects or district code'), { target: { value: 'bridge' } });
  for (const id of recentBridgeIds) {
    const asset = bridgeChoice(id).placements[0];
    const label = cataloguePresentationFor(asset.id)?.label ?? asset.label;
    expect(screen.getByRole('button', { name: `Expand details for ${label}` })).toBeVisible();
  }
});

it('explains the two-endpoint bridge preview without promising site-edge road snapping', () => {
  render(<PlacementPalette selected={null} onPick={vi.fn()} onPickStreet={vi.fn()} onPickCanonical={vi.fn()}
    onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()}
    activeStreetVariant="timber_covered_bridge_route_v1" />);
  expect(screen.getByText(/Draw two endpoints.*32.*240 m/)).toBeVisible();
  expect(screen.queryByText(/Start near a site edge to snap/)).toBeNull();
});
