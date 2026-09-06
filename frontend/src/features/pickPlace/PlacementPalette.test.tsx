import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { PlacementPalette } from './PlacementPalette';
import { LOCAL_STREET_ASSET } from './assetRegistry';
import * as registry from './assetRegistry';

describe('student asset browsing', () => {
  it('filters without placing, clears empty results and dispatches street selection separately', () => {
    const onPick = vi.fn(), onPickStreet = vi.fn();
    render(<PlacementPalette selected={null} onPick={onPick} onPickStreet={onPickStreet} onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()} />);
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Buildings' }));
    fireEvent.change(screen.getByLabelText('Search objects or district code'), { target: { value: 'R-C1' } });
    expect(screen.getByRole('button', { name: /Infill homes/ })).toBeInTheDocument();
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
    const home = registry.CATALOGUE_ASSETS.find(asset => asset.id === 'infill_home')!;
    const spy = vi.spyOn(registry, 'browseAssets').mockReturnValue(Array.from({ length: 30 }, (_, i) => ({ ...home, id: `home-${i}`, label: `House ${i}` })));
    try {
      render(<PlacementPalette selected={null} onPick={vi.fn()} onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()} />);
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
    render(<PlacementPalette selected={null} onPick={onPick} onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()} onBrowseChange={onBrowseChange} />);
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
    render(<PlacementPalette selected="craftsman_bungalow" onPick={onPick} onCancel={onCancel} status="ready" message="" onRetry={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: 'Buildings' }));
    fireEvent.click(screen.getByRole('button', { name: /Craftsman bungalows/ }));
    expect(onPick).toHaveBeenCalledWith('craftsman_bungalow');
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /Cancel placement/ }));
    expect(onCancel).toHaveBeenCalledOnce();
  });
});
