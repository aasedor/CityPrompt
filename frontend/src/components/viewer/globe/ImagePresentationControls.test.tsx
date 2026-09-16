import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import { ImagePresentationControls } from './ImagePresentationControls';
import { STYLES, STYLE_GROUPS } from './imageStyles';

const props = {style: 'photorealistic', onStyle: vi.fn(), addPeople: false, addVehicles: false, onPeople: vi.fn(), onVehicles: vi.fn()};
afterEach(() => { cleanup(); vi.clearAllMocks(); });
it('keeps every established style directly discoverable with its original name and independent entourage', () => {
  render(<ImagePresentationControls {...props} />);
  expect(screen.getByRole('button', { name: 'Photo Realistic' }).getAttribute('aria-pressed')).toBe('true');
  expect(screen.getAllByRole('button')).toHaveLength(STYLES.length);
  for (const group of STYLE_GROUPS) expect(screen.getByRole('group', {name: group.label})).toBeTruthy();
  for (const option of STYLES) {
    const button = screen.getByRole('button', {name: option.label});
    expect(button.closest('details')).toBeNull();
    fireEvent.click(button); expect(props.onStyle).toHaveBeenLastCalledWith(option.id);
  }
  expect((screen.getByRole('checkbox', {name: 'Add People'}) as HTMLInputElement).checked).toBe(false);
  expect((screen.getByRole('checkbox', {name: 'Add Vehicles'}) as HTMLInputElement).checked).toBe(false);
  fireEvent.click(screen.getByRole('checkbox', {name: 'Add People'}));
  expect(props.onPeople).toHaveBeenCalledWith(true); expect(props.onVehicles).not.toHaveBeenCalled();
});
it('retains availability gates without hiding styles', () => {
  render(<ImagePresentationControls {...props} isStyleDisabled={id => id === 'development'} />);
  const button = screen.getByRole('button', {name: 'Development'}) as HTMLButtonElement;
  expect(button.disabled).toBe(true); fireEvent.click(button); expect(props.onStyle).not.toHaveBeenCalled();
});
it('explains projection changes only for the selected plan or axonometric style', () => {
  const {rerender} = render(<ImagePresentationControls {...props} style="isometric" />);
  expect(screen.getByText(/creates a different projection/)).toBeTruthy();
  rerender(<ImagePresentationControls {...props} style="watercolour" />);
  expect(screen.queryByText(/creates a different projection/)).toBeNull();
});
