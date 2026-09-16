import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import { ImagePresentationControls, IMAGE_PRESENTATION_PRESETS } from './ImagePresentationControls';
import { resolveDirect3DPresentationMode } from './useDirect3DRender';

afterEach(cleanup);
it('offers current-camera presets and separate explicit entourage selections', () => {
  const onStyle = vi.fn(), onPeople = vi.fn(), onVehicles = vi.fn();
  render(<ImagePresentationControls style="photorealistic" onStyle={onStyle} addPeople={false} addVehicles={false} onPeople={onPeople} onVehicles={onVehicles} />);
  expect(screen.getByRole('button', { name: 'Realistic' }).getAttribute('aria-pressed')).toBe('true');
  expect((screen.getByRole('checkbox', { name: 'Add People' }) as HTMLInputElement).checked).toBe(false);
  expect((screen.getByRole('checkbox', { name: 'Add Vehicles' }) as HTMLInputElement).checked).toBe(false);
  fireEvent.click(screen.getByRole('checkbox', { name: 'Add People' }));
  expect(onPeople).toHaveBeenCalledWith(true); expect(onVehicles).not.toHaveBeenCalled();
  for (const preset of IMAGE_PRESENTATION_PRESETS) {
    expect(resolveDirect3DPresentationMode(preset.id)).toBe('scene');
    fireEvent.click(screen.getByRole('button', { name: preset.label }));
    expect(onStyle).toHaveBeenLastCalledWith(preset.id);
  }
});
