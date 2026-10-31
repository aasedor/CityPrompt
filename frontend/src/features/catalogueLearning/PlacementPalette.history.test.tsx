import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, within } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import { PlacementPalette } from '@/features/pickPlace/PlacementPalette';

it('combines era and planning idea, clears an empty intersection and resets across domains', () => {
  const onPick = vi.fn(), onPickCanonical = vi.fn(), onPickStreet = vi.fn();
  render(<PlacementPalette selected={null} onPick={onPick} onPickCanonical={onPickCanonical}
    onPickStreet={onPickStreet} onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()} />);
  fireEvent.click(screen.getByRole('button', { name: 'Buildings' }));
  fireEvent.click(screen.getByRole('button', { name: 'Browse by era' }));
  fireEvent.change(screen.getByLabelText('Design era'), { target: { value: 'contemporary' } });
  fireEvent.change(screen.getByLabelText('Planning idea'), { target: { value: 'missing_middle' } });
  expect(screen.getByRole('region', { name: 'About the selected design era' })).toHaveTextContent(/2000/);
  expect(screen.getByRole('region', { name: 'About the selected planning idea' })).toHaveTextContent(/house-scale/i);
  expect(screen.getAllByRole('article').length).toBeGreaterThan(0);
  fireEvent.change(screen.getByLabelText('Design era'), { target: { value: 'postwar' } });
  expect(screen.queryByRole('article')).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', { name: 'Clear filters' }));
  expect(screen.getByLabelText('Design era')).toHaveValue('');
  expect(screen.getByLabelText('Planning idea')).toHaveValue('');
  expect(screen.getAllByRole('article')).toHaveLength(12);
  fireEvent.change(screen.getByLabelText('Design era'), { target: { value: 'postwar' } });
  fireEvent.click(within(screen.getByRole('navigation', { name: 'Catalogue sections' })).getByRole('button', { name: 'Parks' }));
  fireEvent.click(screen.getByRole('button', { name: 'Browse by era' }));
  expect(screen.getByLabelText('Design era')).toHaveValue('');
  expect(screen.queryByRole('region', { name: 'About the selected design era' })).not.toBeInTheDocument();
  expect(onPick).not.toHaveBeenCalled();
  expect(onPickCanonical).not.toHaveBeenCalled();
  expect(onPickStreet).not.toHaveBeenCalled();
});
