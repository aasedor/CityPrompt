import { fireEvent, render, screen, cleanup } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { PlacementControls } from './PlacementControls';
import { PLACE_ASSETS } from './catalogue';
afterEach(cleanup);
describe('pre-placement reshaping', () => {
  it('lets a student edit a draft, rejects undersized plots, and normalizes rotation before updating', () => {
    const asset = PLACE_ASSETS[0], onChange = vi.fn();
    render(<PlacementControls draft={{ assetId: asset.id, width: asset.width, depth: asset.depth, degrees: 0 }} onChange={onChange} />);
    fireEvent.change(screen.getByLabelText('Placement width'), { target: { value: '0' } });
    fireEvent.click(screen.getByText('Update placement preview')); expect(onChange).not.toHaveBeenCalled();
    fireEvent.change(screen.getByLabelText('Placement width'), { target: { value: String(asset.minWidth) } });
    fireEvent.change(screen.getByLabelText('Placement degrees'), { target: { value: '-90' } });
    fireEvent.click(screen.getByText('Update placement preview'));
    expect(onChange).toHaveBeenCalledWith({ assetId: asset.id, width: asset.minWidth, depth: asset.depth, degrees: 270 });
  });
});
