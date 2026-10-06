import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { PlacementPalette } from './PlacementPalette';
import * as catalogue from './canonicalCatalogue';

describe('student asset browsing', () => {
  it('offers an explicit refresh when saved detailed models were unavailable', () => {
    const onRetry=vi.fn();
    render(<PlacementPalette onPickCanonical={vi.fn()} selected={null} onPick={vi.fn()} onCancel={vi.fn()}
      status="ready" message="1 building is shown as design massing" canRefreshDetail onRetry={onRetry} />);
    fireEvent.click(screen.getByRole('button',{name:'Refresh detailed models'}));
    expect(onRetry).toHaveBeenCalledOnce();
  });
  it('filters towers and transit independently, and resets categories on a section change', () => {
    const onPick=vi.fn();
    render(<PlacementPalette onPickCanonical={vi.fn()} selected={null} onPick={onPick} onPickStreet={vi.fn()} onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', {name:'Buildings'}));
    expect(screen.getByRole('option',{name:'Low density'})).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText('Object category'),{target:{value:'towers'}});
    expect(screen.getByRole('button',{name:/Blue glass office tower.*Choose & place/})).toBeInTheDocument();
    expect(screen.queryByRole('button',{name:/Side-by-side duplex.*Choose & place/})).not.toBeInTheDocument();
    expect(onPick).not.toHaveBeenCalled();
    fireEvent.click(screen.getAllByRole('button',{name:'Streets'})[1]);
    expect(screen.getByLabelText('Object category')).toHaveValue('');
    fireEvent.change(screen.getByLabelText('Object category'),{target:{value:'transit'}});
    expect(screen.getByRole('button',{name:/Garden Tram Avenue.*Choose & draw route/})).toBeInTheDocument();
    expect(screen.queryByRole('button',{name:/London Cobbled Mews.*Choose & draw route/})).not.toBeInTheDocument();
  });
  it('shows the current exact catalogue counts and pages the building and park choices', () => {
    render(<PlacementPalette onPickCanonical={vi.fn()} selected={null} onPick={vi.fn()} onPickStreet={vi.fn()} onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()} />);
    const count = (domain: string) => catalogue.CLASSROOM_CHOICES.filter(choice => choice.domain === domain).length;
    fireEvent.click(screen.getByRole('button', { name: 'Buildings' }));
    expect(screen.getByLabelText('Catalogue collection')).toHaveValue('starter');
    expect(screen.getByText(new RegExp(`${catalogue.CLASSROOM_CHOICES.length} exact choices: ${count('building')} buildings, ${count('park_plaza')} parks, ${count('street_pathway')} streets`))).toBeInTheDocument();
    expect(screen.getAllByRole('article')).toHaveLength(12);
    fireEvent.click(screen.getByRole('button', { name: 'Show more choices' }));
    expect(screen.getAllByRole('article')).toHaveLength(24);
    fireEvent.click(screen.getByRole('button', { name: 'Show more choices' }));
    while (screen.queryByRole('button', { name: 'Show more choices' })) {
      fireEvent.click(screen.getByRole('button', { name: 'Show more choices' }));
    }
    expect(screen.getAllByRole('article')).toHaveLength(count('building'));
    fireEvent.click(screen.getAllByRole('button', { name: 'Parks' })[1]);
    expect(screen.getAllByRole('article')).toHaveLength(12);
    fireEvent.click(screen.getByRole('button', { name: 'Show more choices' }));
    fireEvent.click(screen.getByRole('button', { name: 'Show more choices' }));
    expect(screen.getAllByRole('article')).toHaveLength(count('park_plaza'));
    expect(catalogue.CLASSROOM_CHOICES.every(choice => choice.placements.length === 1 && choice.option.variants?.length === 1)).toBe(true);
  });
  it('shows the active native street width and marks only the selected street card', () => {
    const onPickStreet = vi.fn();
    render(<PlacementPalette onPickCanonical={vi.fn()} selected={null} onPick={vi.fn()} onPickStreet={onPickStreet}
      activeStreetVariant="student_green_alley_v1" onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()} />);
    expect(screen.getByText('Ruelle Verte Community Alley · 11 m wide')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Streets' }));
    expect(screen.getAllByRole('article')).toHaveLength(12);
    fireEvent.click(screen.getByRole('button', { name: 'Show more choices' }));
    expect(screen.getByRole('button', { name: /Ruelle Verte Community Alley.*Choose & draw route/ })).toHaveAttribute('aria-pressed','true');
    expect(screen.getByRole('button', { name: /Playful School Street.*Choose & draw route/ })).toHaveAttribute('aria-pressed','false');
    fireEvent.click(screen.getByRole('button', { name: /Playful School Street.*Choose & draw route/ }));
    expect(onPickStreet).toHaveBeenCalledWith(expect.objectContaining({sectionWidth:18}));
  });
  it('filters without placing, clears empty results and dispatches street selection separately', () => {
    const onPick = vi.fn(), onPickStreet = vi.fn();
    render(<PlacementPalette onPickCanonical={vi.fn()} selected={null} onPick={onPick} onPickStreet={onPickStreet} onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()} />);
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Buildings' }));
    fireEvent.change(screen.getByLabelText('Search objects or district code'), { target: { value: 'Side-by-side duplex' } });
    expect(screen.getByRole('button', { name: /Side-by-side duplex.*Choose & place/ })).toBeInTheDocument();
    expect(onPick).not.toHaveBeenCalled();
    fireEvent.change(screen.getByLabelText('Search objects or district code'), { target: { value: 'unavailable' } });
    fireEvent.click(screen.getByRole('button', { name: 'Clear filters' }));
    fireEvent.click(screen.getAllByRole('button', { name: 'Streets' })[1]);
    fireEvent.change(screen.getByLabelText('Search objects or district code'), { target: { value: 'Ruelle Verte' } });
    fireEvent.click(screen.getByRole('button', { name: /Ruelle Verte Community Alley.*Choose & draw route/ }));
    expect(onPickStreet).toHaveBeenCalledWith(expect.objectContaining({id:'student_green_alley_v1'}));
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    expect(onPick).not.toHaveBeenCalled();
  });
  it('bounds a growing catalogue and resets the page when filtering', () => {
    const home = catalogue.CANONICAL_CHOICES.find(choice => choice.option.id === 'calgary_modern_infill_house')!;
    const spy = vi.spyOn(catalogue, 'filterCanonicalChoices').mockReturnValue(Array.from({ length: 30 }, (_, i) => ({ ...home, id: `home-${i}`, option: {...home.option, label: `House ${i}`} })));
    try {
      render(<PlacementPalette onPickCanonical={vi.fn()} selected={null} onPick={vi.fn()} onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()} />);
      fireEvent.click(screen.getByRole('button', { name: 'Buildings' }));
      expect(screen.getAllByRole('article')).toHaveLength(12);
      fireEvent.click(screen.getByRole('button', { name: 'Show more choices' }));
      expect(screen.getAllByRole('article')).toHaveLength(24);
      fireEvent.change(screen.getByLabelText('Search objects or district code'), { target: { value: 'home' } });
      expect(screen.getAllByRole('article')).toHaveLength(12);
    } finally { spy.mockRestore(); }
  });
  it('closes with Escape and restores launcher focus without placing', () => {
    const onPick = vi.fn(), onBrowseChange = vi.fn();
    render(<PlacementPalette onPickCanonical={vi.fn()} selected={null} onPick={onPick} onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()} onBrowseChange={onBrowseChange} />);
    const launcher = screen.getByRole('button', { name: 'Parks' });
    launcher.focus(); fireEvent.click(launcher);
    expect(onBrowseChange).toHaveBeenLastCalledWith(true);
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    expect(launcher).toHaveFocus();
    expect(onBrowseChange).toHaveBeenLastCalledWith(false);
    expect(onPick).not.toHaveBeenCalled();
  });
  it('preserves object selection and cancellation after filtering', () => {
    const onPick = vi.fn(), onCancel = vi.fn();
    render(<PlacementPalette onPickCanonical={vi.fn()} selected="clay_side_by_side_duplex" onPick={onPick} onCancel={onCancel} status="ready" message="" onRetry={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: 'Buildings' }));
    fireEvent.change(screen.getByLabelText('Search objects or district code'), { target: { value: 'Side-by-side duplex' } });
    fireEvent.click(screen.getByRole('button', { name: /Side-by-side duplex.*Choose & place/ }));
    expect(onPick).toHaveBeenCalledWith('clay_side_by_side_duplex');
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /Cancel placement/ }));
    expect(onCancel).toHaveBeenCalledOnce();
  });
});
