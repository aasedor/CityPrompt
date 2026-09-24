import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { PlacementPalette } from './PlacementPalette';
import { LOCAL_STREET_ASSET } from './assetRegistry';
import * as catalogue from './canonicalCatalogue';

describe('student asset browsing', () => {
  it('starts with three exact variants per domain and preserves exploratory discovery', () => {
    render(<PlacementPalette onPickCanonical={vi.fn()} selected={null} onPick={vi.fn()} onPickStreet={vi.fn()} onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()} />);
    expect(catalogue.CLASSROOM_CHOICES).toHaveLength(9);
    fireEvent.click(screen.getByRole('button', { name: 'Buildings' }));
    expect(screen.getByLabelText('Catalogue collection')).toHaveValue('starter');
    for (const section of ['Buildings', 'Parks', 'Streets']) {
      fireEvent.click(screen.getAllByRole('button', { name: section })[1]);
      expect(screen.getAllByRole('article')).toHaveLength(3);
      expect(catalogue.CLASSROOM_CHOICES.every(choice => choice.placements.length === 1 && choice.option.variants?.length === 1)).toBe(true);
    }
    fireEvent.change(screen.getByLabelText('Catalogue collection'), { target: { value: 'explore' } });
    expect(screen.getAllByRole('article')).toHaveLength(12);
    expect(screen.getByText(/Exploratory catalogue/)).toBeInTheDocument();
  });
  it('shows the active fixed width and marks only the selected street card', () => {
    const onPickStreet = vi.fn();
    render(<PlacementPalette onPickCanonical={vi.fn()} selected={null} onPick={vi.fn()} onPickStreet={onPickStreet}
      activeStreetVariant="yield_street_v0" onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()} />);
    expect(screen.getByText('Shared street · 6 m wide')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Streets' }));
    fireEvent.change(screen.getByLabelText('Catalogue collection'), { target: { value: 'explore' } });
    expect(screen.getByRole('button', { name: /Shared street/ })).toHaveAttribute('aria-pressed','true');
    expect(screen.getByRole('button', { name: /Planted laneway/ })).toHaveAttribute('aria-pressed','false');
    fireEvent.click(screen.getByRole('button', { name: /Planted laneway/ }));
    expect(onPickStreet).toHaveBeenCalledWith(expect.objectContaining({sectionWidth:5}));
  });
  it('filters without placing, clears empty results and dispatches street selection separately', () => {
    const onPick = vi.fn(), onPickStreet = vi.fn();
    render(<PlacementPalette onPickCanonical={vi.fn()} selected={null} onPick={onPick} onPickStreet={onPickStreet} onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()} />);
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Buildings' }));
    fireEvent.change(screen.getByLabelText('Search objects or district code'), { target: { value: 'R-C1' } });
    expect(screen.getByRole('button', { name: /Infill home/ })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Neighbourhood park/ })).not.toBeInTheDocument();
    expect(onPick).not.toHaveBeenCalled();
    fireEvent.change(screen.getByLabelText('Search objects or district code'), { target: { value: 'unavailable' } });
    fireEvent.click(screen.getByRole('button', { name: 'Clear filters' }));
    fireEvent.click(screen.getAllByRole('button', { name: 'Streets' })[1]);
    fireEvent.change(screen.getByLabelText('Object category'), { target: { value: 'local' } });
    fireEvent.click(screen.getByRole('button', { name: /Calgary local street/ }));
    expect(onPickStreet).toHaveBeenCalledWith(LOCAL_STREET_ASSET);
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
    render(<PlacementPalette onPickCanonical={vi.fn()} selected="craftsman_bungalow" onPick={onPick} onCancel={onCancel} status="ready" message="" onRetry={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: 'Buildings' }));
    fireEvent.change(screen.getByLabelText('Catalogue collection'), { target: { value: 'explore' } });
    fireEvent.click(screen.getByRole('button', { name: /Craftsman bungalows/ }));
    expect(onPick).toHaveBeenCalledWith('craftsman_bungalow');
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /Cancel placement/ }));
    expect(onCancel).toHaveBeenCalledOnce();
  });
});
