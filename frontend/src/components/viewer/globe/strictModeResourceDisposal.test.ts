import { describe, expect, it, vi } from 'vitest';

import { retainResourceForDeferredDisposal } from './strictModeResourceDisposal';


describe('retainResourceForDeferredDisposal', () => {
  it('does not dispose a resource retained again during the StrictMode effect cycle', async () => {
    const resource = {};
    const dispose = vi.fn();

    const firstCleanup = retainResourceForDeferredDisposal(resource, dispose);
    firstCleanup();
    const liveCleanup = retainResourceForDeferredDisposal(resource, dispose);
    await Promise.resolve();

    expect(dispose).not.toHaveBeenCalled();

    liveCleanup();
    await Promise.resolve();
    expect(dispose).toHaveBeenCalledOnce();
  });

  it('disposes a released resource after the microtask boundary', async () => {
    const resource = {};
    const dispose = vi.fn();

    retainResourceForDeferredDisposal(resource, dispose)();
    expect(dispose).not.toHaveBeenCalled();

    await Promise.resolve();
    expect(dispose).toHaveBeenCalledWith(resource);
  });
});
