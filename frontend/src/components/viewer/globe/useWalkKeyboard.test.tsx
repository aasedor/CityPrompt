import { afterEach, describe, expect, it, vi } from 'vitest';
import { act, fireEvent, render, renderHook } from '@testing-library/react';
import { useWalkKeyboard } from './useWalkKeyboard';
import { StudioDialog } from '@/features/projects/StudioControls';
const pose = () => ({ current: { lng: -114, lat: 51, groundHeight: 1000, heading: 0 } });
afterEach(() => { vi.useRealTimers(); vi.restoreAllMocks(); });
describe('walk modal ownership', () => {
  it('lets Escape close a dialog without cancelling the underlying walk picker', () => {
    const cancel = vi.fn(), close = vi.fn();
    const ref = pose();
    function View({ paused }: { paused: boolean }) {
      useWalkKeyboard('pick', paused, ref, vi.fn(), vi.fn(), cancel);
      return paused ? <StudioDialog title="Planning report" onClose={close}>Report</StudioDialog> : null;
    }
    const view = render(<View paused={false} />);
    view.rerender(<View paused />);
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(close).toHaveBeenCalledOnce();
    expect(cancel).not.toHaveBeenCalled();
    view.rerender(<View paused={false} />);
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(cancel).toHaveBeenCalledOnce();
  });
  it('stops movement and clears held keys while paused, then resumes on a new keypress', () => {
    vi.useFakeTimers();
    const apply = vi.fn(), ref = pose(), exit = vi.fn(), cancel = vi.fn();
    const view = renderHook(({ paused }) => useWalkKeyboard('active', paused, ref, apply, exit, cancel), { initialProps: { paused: false } });
    fireEvent.keyDown(document, { key: 'w' });
    act(() => vi.advanceTimersByTime(40));
    expect(apply).toHaveBeenCalled();
    view.rerender({ paused: true });
    apply.mockClear();
    fireEvent.keyDown(document, { key: 'w' });
    fireEvent.keyDown(document, { key: 'Escape' });
    act(() => vi.advanceTimersByTime(40));
    expect(apply).not.toHaveBeenCalled();
    expect(exit).not.toHaveBeenCalled();
    view.rerender({ paused: false });
    act(() => vi.advanceTimersByTime(40));
    expect(apply).not.toHaveBeenCalled();
    fireEvent.keyDown(document, { key: 'w' });
    act(() => vi.advanceTimersByTime(40));
    expect(apply).toHaveBeenCalled();
  });
});
