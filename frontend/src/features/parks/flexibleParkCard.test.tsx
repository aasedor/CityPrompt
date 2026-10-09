import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, within } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import { PlacementPalette } from '@/features/pickPlace/PlacementPalette';

it('keeps reviewed parks and makes all four flexible parks searchable and drawable', () => {
  const onPick = vi.fn();
  render(<PlacementPalette selected={null} onPick={onPick} onPickStreet={vi.fn()}
    onPickCanonical={vi.fn()} onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()}/>);
  fireEvent.click(screen.getByRole('button', { name: 'Parks' }));
  fireEvent.click(screen.getByRole('button', { name: /^Browse all / }));
  expect(screen.getByRole('button', { name: /Conservatory botanical garden.*Choose & place/ })).toBeInTheDocument();
  fireEvent.change(screen.getByRole('searchbox', { name: 'Search objects or district code' }), { target: { value: 'Flexible' } });
  expect(screen.getAllByRole('article')).toHaveLength(4);
  const pocket = screen.getByRole('button', { name: /Flexible pocket park.*Choose & draw park/ });
  const greenway = screen.getByRole('button', { name: /Flexible linear greenway.*Choose & draw park/ });
  expect(within(pocket).getByText('Flexible 3D · draw your outline')).toBeInTheDocument();
  expect(within(greenway).getByText('Flexible 3D · draw your outline')).toBeInTheDocument();
  fireEvent.click(greenway);
  expect(onPick).toHaveBeenCalledWith('flexible_linear_greenway_v1');
});

it.each([
  ['shade courtyard', 'flexible_shade_courtyard_v1'],
  ['meadow grove', 'flexible_meadow_grove_v1'],
])('draws the exact %s design selected from search', (query, id) => {
  const onPick = vi.fn();
  render(<PlacementPalette selected={null} onPick={onPick} onPickStreet={vi.fn()}
    onPickCanonical={vi.fn()} onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()}/>);
  fireEvent.click(screen.getByRole('button', { name: 'Parks' }));
  fireEvent.click(screen.getByRole('button', { name: /^Browse all / }));
  fireEvent.change(screen.getByRole('searchbox', { name: 'Search objects or district code' }), { target: { value: query } });
  fireEvent.click(screen.getByRole('button', {name: /Choose & draw park/}));
  expect(onPick).toHaveBeenCalledWith(id);
});
