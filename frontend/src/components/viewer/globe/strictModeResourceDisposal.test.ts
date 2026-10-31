import { describe, expect, it, vi } from 'vitest';

import * as resources from './strictModeResourceDisposal';
const { retainResourceForDeferredDisposal } = resources;


describe('retainResourceForDeferredDisposal', () => {
  it('releases both prepared module resource groups under one StrictMode-safe lease', async () => {
    const retain = resources.retainPreparedModuleResources;
    expect(retain).toBeTypeOf('function');
    const cutGeometry = {dispose: vi.fn()}, groundGeometry = {dispose: vi.fn()}, groundMaterial = {dispose: vi.fn()};
    const modules = [{buildingOnly: {ownedGeometries: [cutGeometry]},
      landscape: {ownedGeometries: [groundGeometry], ownedMaterials: [groundMaterial]}}];
    const firstCleanup = retain(modules);
    firstCleanup();
    const liveCleanup = retain(modules);
    await Promise.resolve();
    for (const owned of [cutGeometry, groundGeometry, groundMaterial]) expect(owned.dispose).not.toHaveBeenCalled();
    liveCleanup();
    await Promise.resolve();
    for (const owned of [cutGeometry, groundGeometry, groundMaterial]) expect(owned.dispose).toHaveBeenCalledOnce();
  });
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
