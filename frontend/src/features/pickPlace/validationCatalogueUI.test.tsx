import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, within } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { PlacementPalette } from './PlacementPalette';
import { CANONICAL_CHOICES } from './canonicalCatalogue';

describe('local student validation discovery',()=>{
  it('shows the current roster and selects every road across all catalogue pages',()=>{
    const onPick=vi.fn(),onPickStreet=vi.fn();
    const onPickCanonical = vi.fn();
    render(<PlacementPalette selected={null} onPick={onPick} onPickStreet={onPickStreet}
      onPickCanonical={onPickCanonical} onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()}/>);
    fireEvent.click(screen.getByRole('button',{name:'Buildings'}));
    expect(within(screen.getByLabelText('Catalogue collection')).getAllByRole('option')).toHaveLength(1);
    expect(screen.getAllByRole('article')).toHaveLength(12);
    const count = (domain: string) => CANONICAL_CHOICES.filter(choice => choice.domain === domain).length;
    expect(screen.getByText(new RegExp(`${count('building')} buildings, ${count('park_plaza')} parks, ${count('street_pathway')} streets`))).toBeInTheDocument();
    for(const article of screen.getAllByRole('article'))expect(within(article).getAllByRole('option')).toHaveLength(1);
    fireEvent.click(screen.getAllByRole('button',{name:'Parks'})[1]);
    expect(screen.getAllByRole('article')).toHaveLength(12);
    fireEvent.click(screen.getAllByRole('button',{name:'Streets'})[1]);
    const streets = CANONICAL_CHOICES.filter(choice => choice.domain === 'street_pathway');
    for (const [index, choice] of streets.entries()) {
      if (index > 0) fireEvent.click(screen.getByRole('button', { name: 'Streets' }));
      for (let page = 0; page < Math.floor(index / 12); page++) {
        fireEvent.click(screen.getByRole('button', { name: 'Show more choices' }));
      }
      const asset = choice.placements[0];
      expect(asset.kind).toBe('street');
      const article = screen.getByLabelText(`Variant for ${asset.label}`).closest('article')!;
      fireEvent.click(within(article).getByRole('button', { name: /Choose & draw route/ }));
      expect(onPickStreet).toHaveBeenLastCalledWith(asset);
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    }
    expect(onPickStreet).toHaveBeenCalledTimes(streets.length);
    expect(onPick).not.toHaveBeenCalled();
    expect(onPickCanonical).not.toHaveBeenCalled();
  }, 60000);
  it('leaves street drawing in Streets and reserves the primary action for walking',()=>{
    const onPickStreet=vi.fn();
    render(<PlacementPalette primaryAction={<button>Walk</button>} selected={null} onPick={vi.fn()} onPickStreet={onPickStreet}
      onPickCanonical={vi.fn()} onCancel={vi.fn()} status="idle" message="" onRetry={vi.fn()}/>);
    expect(screen.queryByRole('button',{name:'Draw a road route'})).not.toBeInTheDocument();
    expect(screen.getByRole('button',{name:'Walk'})).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button',{name:'Streets'}));
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(onPickStreet).not.toHaveBeenCalled();
  });
});
