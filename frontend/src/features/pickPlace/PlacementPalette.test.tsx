import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { PlacementPalette } from './PlacementPalette';
import { LOCAL_STREET_ASSET } from './assetRegistry';

describe('student asset browsing', () => {
  it('filters without placing, clears empty results and dispatches street selection separately', () => {
    const onPick = vi.fn(), onPickStreet = vi.fn();
    render(<PlacementPalette selected={null} onPick={onPick} onPickStreet={onPickStreet} onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()} />);
    fireEvent.change(screen.getByLabelText('Search objects or district code'), { target: { value: 'R-C1' } });
    expect(screen.getByRole('button', { name: /Infill homes/ })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Neighbourhood park/ })).not.toBeInTheDocument();
    expect(onPick).not.toHaveBeenCalled();
    fireEvent.change(screen.getByLabelText('Search objects or district code'), { target: { value: 'unavailable' } });
    fireEvent.click(screen.getByRole('button', { name: 'Clear filters' }));
    fireEvent.change(screen.getByLabelText('Object category'), { target: { value: 'local' } });
    fireEvent.click(screen.getByRole('button', { name: /Calgary local street/ }));
    expect(onPickStreet).toHaveBeenCalledWith(LOCAL_STREET_ASSET);
    expect(onPick).not.toHaveBeenCalled();
  });
  it('preserves object selection and cancellation after filtering', () => {
    const onPick = vi.fn(), onCancel = vi.fn();
    render(<PlacementPalette selected="craftsman_bungalow" onPick={onPick} onCancel={onCancel} status="ready" message="" onRetry={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: /Craftsman bungalows/ }));
    expect(onPick).toHaveBeenCalledWith('craftsman_bungalow');
    fireEvent.change(screen.getByLabelText('Object category'), { target: { value: 'neighbourhood' } });
    fireEvent.click(screen.getByRole('button', { name: /Cancel placement/ }));
    expect(onCancel).toHaveBeenCalledOnce();
  });
});
