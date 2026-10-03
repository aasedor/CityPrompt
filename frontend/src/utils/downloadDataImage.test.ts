import { afterEach, describe, expect, it, vi } from 'vitest';
import { downloadDataImage } from './downloadDataImage';

describe('downloadDataImage', () => {
  const originalCreate = URL.createObjectURL;
  const originalRevoke = URL.revokeObjectURL;

  afterEach(() => {
    Object.defineProperty(URL, 'createObjectURL', { configurable: true, value: originalCreate });
    Object.defineProperty(URL, 'revokeObjectURL', { configurable: true, value: originalRevoke });
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  it('downloads the exact PNG bytes through a temporary Blob URL', () => {
    vi.useFakeTimers();
    const create = vi.fn((_blob: Blob) => 'blob:cityprompt-test');
    const revoke = vi.fn();
    Object.defineProperty(URL, 'createObjectURL', { configurable: true, value: create });
    Object.defineProperty(URL, 'revokeObjectURL', { configurable: true, value: revoke });
    const click = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(function (this: HTMLAnchorElement) {
      expect(this.href).toBe('blob:cityprompt-test');
      expect(this.download).toBe('currie-view.png');
      expect(this.isConnected).toBe(true);
    });

    downloadDataImage('data:image/png;base64,iVBORw0KGgo=', 'currie-view.png');

    expect(create).toHaveBeenCalledOnce();
    expect(create.mock.calls[0][0]).toMatchObject({ type: 'image/png', size: 8 });
    expect(click).toHaveBeenCalledOnce();
    expect(document.querySelector('a[href="blob:cityprompt-test"]')).toBeNull();
    vi.advanceTimersByTime(60_000);
    expect(revoke).toHaveBeenCalledWith('blob:cityprompt-test');
  });
});
