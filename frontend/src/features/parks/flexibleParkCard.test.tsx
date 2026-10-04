import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, within } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import { PlacementPalette } from '@/features/pickPlace/PlacementPalette';

it('keeps reviewed parks and makes both flexible parks searchable and drawable', () => {
  const onPick = vi.fn();
  render(<PlacementPalette selected={null} onPick={onPick} onPickStreet={vi.fn()}
    onPickCanonical={vi.fn()} onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()}/>);
  fireEvent.click(screen.getByRole('button', { name: 'Parks' }));
  expect(screen.getByRole('button', { name: /Conservatory botanical garden.*Choose & place/ })).toBeInTheDocument();
  fireEvent.change(screen.getByRole('searchbox', { name: 'Search objects or district code' }), { target: { value: 'Flexible' } });
  expect(screen.getAllByRole('article')).toHaveLength(2);
  const pocket = screen.getByRole('button', { name: /Flexible pocket park.*Choose & draw park/ });
  const greenway = screen.getByRole('button', { name: /Flexible linear greenway.*Choose & draw park/ });
  expect(within(pocket).getByText('Flexible 3D · draw your outline')).toBeInTheDocument();
  expect(within(greenway).getByText('Flexible 3D · draw your outline')).toBeInTheDocument();
  fireEvent.click(greenway);
  expect(onPick).toHaveBeenCalledWith('flexible_linear_greenway_v1');
});
