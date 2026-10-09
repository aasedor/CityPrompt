import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';

vi.mock('./assetRegistry', async importOriginal => {
  const actual = await importOriginal<typeof import('./assetRegistry')>();
  return { ...actual, CATALOGUE_ASSETS: actual.CATALOGUE_ASSETS.filter(
    asset => asset.model.variantId !== 'student_main_street_v1',
  ) };
});

it('opens the catalogue when a listed road has no registered placement asset', async () => {
  const { PlacementPalette } = await import('./PlacementPalette');
  render(<PlacementPalette selected={null} onPick={vi.fn()} onPickStreet={vi.fn()}
    onPickCanonical={vi.fn()} onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()} />);
  fireEvent.click(screen.getByRole('button', { name: 'Streets' }));
  fireEvent.click(screen.getByRole('button', { name: /^Browse all / }));
  expect(screen.getByRole('dialog')).toBeInTheDocument();
  expect(screen.queryByRole('button', { name: /Neighbourhood Main Street.*Choose/ })).not.toBeInTheDocument();
  expect(screen.getByText(/1 design is temporarily unavailable/)).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /Pedestrian Market Street.*Choose & draw route/ })).toBeEnabled();
  fireEvent.click(screen.getAllByRole('button', { name: 'Buildings' })[1]);
  fireEvent.click(screen.getByRole('button', { name: /^Browse all / }));
  expect(screen.getAllByRole('article')).toHaveLength(12);
  fireEvent.click(screen.getAllByRole('button', { name: 'Parks' })[1]);
  fireEvent.click(screen.getByRole('button', { name: /^Browse all / }));
  expect(screen.getAllByRole('article')).toHaveLength(12);
});
