import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import { MapCleanupControls } from './MapCleanupControls';
import type { MapCleanupBox } from './mapCleanup';

it('keeps picked edits local until applied and can restore the original map fragment', async () => {
  const box: MapCleanupBox = { id: 'one', lng: -114, lat: 51, altitude: 1051,
    width: 4, depth: 4, height: 3, yaw: 0, enabled: true };
  const save = vi.fn().mockResolvedValue(undefined), draft = vi.fn(), pick = vi.fn();
  const props = { boxes: [], draft: box, picking: false, onDraft: draft, onPick: pick,
    onSave: save, onClose: vi.fn() };
  const { rerender } = render(<MapCleanupControls {...props} />);
  expect(save).not.toHaveBeenCalled();
  fireEvent.change(screen.getByLabelText('Box width (m)'), { target: { value: '5' } });
  expect(draft).toHaveBeenLastCalledWith({ ...box, width: 5 });
  fireEvent.click(screen.getByRole('button', { name: 'Apply cleanup' }));
  await waitFor(() => expect(save).toHaveBeenCalledWith([box]));
  rerender(<MapCleanupControls {...props} boxes={[box]} />);
  fireEvent.click(screen.getByRole('button', { name: 'Restore fragment 1' }));
  await waitFor(() => expect(save).toHaveBeenLastCalledWith([{ ...box, enabled: false }]));
});

it('lets the operator cancel a pending pick', () => {
  const pick = vi.fn();
  render(<MapCleanupControls boxes={[]} draft={null} picking onDraft={vi.fn()} onPick={pick} onSave={vi.fn()} onClose={vi.fn()} />);
  fireEvent.click(screen.getByRole('button', { name: 'Cancel pick' }));
  expect(pick).toHaveBeenCalledWith(false);
  expect(screen.queryByRole('button', { name: 'Apply cleanup' })).toBeNull();
});

it('refuses an oversized box instead of cutting a large part of the city', () => {
  render(<MapCleanupControls boxes={[]} draft={{ id: 'one', lng: -114, lat: 51,
    altitude: 1051, width: 200, depth: 4, height: 3, yaw: 0, enabled: true }}
    picking={false} onDraft={vi.fn()} onPick={vi.fn()} onSave={vi.fn()} onClose={vi.fn()} />);
  expect((screen.getByRole('button', { name: 'Apply cleanup' }) as HTMLButtonElement).disabled).toBe(true);
});
