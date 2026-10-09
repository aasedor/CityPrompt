import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, within } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import { PlacementPalette } from './PlacementPalette';
import { CLASSROOM_CHOICES, choiceMatchesGroup } from './canonicalCatalogue';
import { CALGARY_GROUPS } from '@/features/calgaryCatalogue/guide';

it('starts with category tiles, drills into existing groups and returns without placing', () => {
  const pick = vi.fn();
  render(<PlacementPalette selected={null} onPick={pick} onPickStreet={pick} onPickCanonical={pick}
    onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()} />);
  fireEvent.click(screen.getByRole('button', { name: 'Buildings' }));
  for (const [domain, label] of [['building', 'Buildings'], ['park_plaza', 'Parks'], ['street_pathway', 'Streets']] as const) {
    fireEvent.click(within(screen.getByRole('navigation', { name: 'Catalogue sections' })).getByRole('button', { name: label }));
    expect(screen.queryByRole('article')).not.toBeInTheDocument();
    const choices = CLASSROOM_CHOICES.filter(c => c.domain === domain && (domain !== 'street_pathway' || c.placements[0]?.kind === 'street'));
    for (const group of CALGARY_GROUPS.filter(g => g.domain === domain && choices.some(c => choiceMatchesGroup(c, g.id)))) {
      const tile = screen.getByRole('button', { name: `Browse ${group.label}` });
      fireEvent.click(tile);
      const matching = choices.filter(c => choiceMatchesGroup(c, group.id));
      expect(screen.getAllByRole('article')).toHaveLength(Math.min(matching.length, 12));
      expect(screen.getByRole('heading', { name: group.label })).toBeInTheDocument();
      fireEvent.click(screen.getByRole('button', { name: 'All categories' }));
      expect(screen.queryByRole('article')).not.toBeInTheDocument();
    }
  }
  expect(pick).not.toHaveBeenCalled();
}, 30000);

it('can search directly from the category view and reopen at categories', () => {
  render(<PlacementPalette selected={null} onPick={vi.fn()} onPickCanonical={vi.fn()}
    onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()} />);
  fireEvent.click(screen.getByRole('button', { name: 'Buildings' }));
  fireEvent.change(screen.getByLabelText('Search objects or district code'), { target: { value: 'Side-by-side duplex' } });
  expect(screen.getByRole('button', { name: /Side-by-side duplex.*Choose & place/ })).toBeVisible();
  fireEvent.keyDown(document, { key: 'Escape' });
  fireEvent.click(screen.getByRole('button', { name: 'Buildings' }));
  expect(screen.queryByRole('article')).not.toBeInTheDocument();
  expect(screen.getByRole('button', { name: 'Browse all buildings' })).toBeVisible();
});
