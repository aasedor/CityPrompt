import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, within } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { PlacementPalette } from './PlacementPalette';
import { CANONICAL_CHOICES } from './canonicalCatalogue';
import { cataloguePresentationFor } from './cataloguePresentation';

describe('local student validation discovery',()=>{
  it('shows the current roster and expandable details across catalogue domains',()=>{
    const onPick=vi.fn(),onPickStreet=vi.fn();
    const onPickCanonical = vi.fn();
    render(<PlacementPalette selected={null} onPick={onPick} onPickStreet={onPickStreet}
      onPickCanonical={onPickCanonical} onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()}/>);
    fireEvent.click(screen.getByRole('button',{name:'Buildings'}));
    fireEvent.click(screen.getByRole('button', { name: /^Browse all / }));
    expect(within(screen.getByLabelText('Catalogue collection')).getAllByRole('option')).toHaveLength(1);
    expect(screen.getAllByRole('article')).toHaveLength(12);
    const count = (domain: string) => CANONICAL_CHOICES.filter(choice => choice.domain === domain).length;
    expect(screen.getByText(new RegExp(`${count('building')} buildings, ${count('park_plaza')} parks, ${count('street_pathway')} streets`))).toBeInTheDocument();
    for(const article of screen.getAllByRole('article')) {
      expect(within(article).queryByRole('combobox')).not.toBeInTheDocument();
      fireEvent.click(within(article).getByRole('button', { name: /^Expand details for / }));
      expect(within(article).getAllByRole('option')).toHaveLength(1);
    }
    fireEvent.click(screen.getAllByRole('button',{name:'Parks'})[1]);
    fireEvent.click(screen.getByRole('button', { name: /^Browse all / }));
    expect(screen.getAllByRole('article')).toHaveLength(12);
    fireEvent.click(screen.getAllByRole('button',{name:'Streets'})[1]);
    fireEvent.click(screen.getByRole('button', { name: /^Browse all / }));
    expect(screen.queryByRole('button', { name: /Place fixed review segment/ })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Show 9 fixed review segments (placement only)' }));
    expect(screen.getAllByRole('article')).toHaveLength(12);
    expect(onPickStreet).not.toHaveBeenCalled();
    expect(onPick).not.toHaveBeenCalled();
    expect(onPickCanonical).not.toHaveBeenCalled();
  });

  // Each choice is independent: a slow aggregate case previously hid the
  // failing street behind a 60-second timeout during concurrent build/QA.
  it.each(CANONICAL_CHOICES.filter(choice => choice.domain === 'street_pathway').map((choice, index) => ({
    index, asset: choice.placements[0], label: choice.placements[0].label,
  })))('selects $label from its catalogue page', ({ index, asset }) => {
    const onPick=vi.fn(), onPickStreet=vi.fn(), onPickCanonical=vi.fn();
    render(<PlacementPalette selected={null} onPick={onPick} onPickStreet={onPickStreet}
      onPickCanonical={onPickCanonical} onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()}/>);
    fireEvent.click(screen.getByRole('button', { name: 'Streets' }));
    fireEvent.click(screen.getByRole('button', { name: /^Browse all / }));
    fireEvent.click(screen.getByRole('button', { name: 'Show 9 fixed review segments (placement only)' }));
    for (let page = 0; page < Math.floor(index / 12); page++) {
      fireEvent.click(screen.getByRole('button', { name: 'Show more choices' }));
    }
    const label = cataloguePresentationFor(asset.id)?.label ?? asset.label;
    fireEvent.click(screen.getByRole('button', { name: `Expand details for ${label}` }));
    const article = screen.getByLabelText(`Variant for ${label}`).closest('article')!;
    if (asset.kind === 'street') {
      fireEvent.click(within(article).getByRole('button', { name: 'Choose & draw route' }));
      expect(onPickStreet).toHaveBeenCalledExactlyOnceWith(asset);
      expect(onPick).not.toHaveBeenCalled();
    } else {
      expect(asset.zoneType).toBe('road');
      expect(asset.reshapeMode).toBe('fixed_native');
      expect(asset.model.method).toBe('fixed_public_realm_v1');
      expect(within(article).queryByRole('button', { name: 'Choose & draw route' })).not.toBeInTheDocument();
      fireEvent.click(within(article).getByRole('button', { name: 'Place fixed review segment' }));
      expect(onPick).toHaveBeenCalledExactlyOnceWith(asset.id);
      expect(onPickStreet).not.toHaveBeenCalled();
    }
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    expect(onPickCanonical).not.toHaveBeenCalled();
  });
  it('leaves street drawing in Streets and reserves the primary action for walking',()=>{
    const onPickStreet=vi.fn();
    render(<PlacementPalette primaryAction={<button>Walk</button>} selected={null} onPick={vi.fn()} onPickStreet={onPickStreet}
      onPickCanonical={vi.fn()} onCancel={vi.fn()} status="idle" message="" onRetry={vi.fn()}/>);
    expect(screen.queryByRole('button',{name:'Draw a road route'})).not.toBeInTheDocument();
    expect(screen.getByRole('button',{name:'Walk'})).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button',{name:'Streets'}));
    fireEvent.click(screen.getByRole('button', { name: /^Browse all / }));
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(onPickStreet).not.toHaveBeenCalled();
  });
});
