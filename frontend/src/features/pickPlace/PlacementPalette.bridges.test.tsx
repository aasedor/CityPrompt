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

const recentBridgeIds = ['stone-arch-road-bridge-compact-r002', 'timber-covered-footbridge',
  'tied-arch-shared-bridge', 'planted-green-bridge'];

it.each(recentBridgeIds)('shows and selects %s through the main Bridges category without a review toggle', id => {
  const choice = CLASSROOM_CHOICES.find(c => c.placements.some(asset => asset.id.startsWith(`claude_public_realm:${id}:`)))!;
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
  expect(within(card).queryByRole('button', { name: 'Choose & draw route' })).not.toBeInTheDocument();
  fireEvent.click(within(card).getByRole('button', { name: 'Place fixed review segment' }));
  expect(pick).toHaveBeenCalledExactlyOnceWith(asset.id);
  expect(draw).not.toHaveBeenCalled();
});

it('finds imported bridges in a normal street search without a review toggle', () => {
  render(<PlacementPalette selected={null} onPick={vi.fn()} onPickStreet={vi.fn()} onPickCanonical={vi.fn()}
    onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()} />);
  fireEvent.click(screen.getByRole('button', { name: 'Streets' }));
  fireEvent.change(screen.getByLabelText('Search objects or district code'), { target: { value: 'bridge' } });
  for (const id of recentBridgeIds) {
    const asset = CLASSROOM_CHOICES.find(c => c.placements.some(a => a.id.startsWith(`claude_public_realm:${id}:`)))!.placements[0];
    const label = cataloguePresentationFor(asset.id)?.label ?? asset.label;
    expect(screen.getByRole('button', { name: `Expand details for ${label}` })).toBeVisible();
  }
});
