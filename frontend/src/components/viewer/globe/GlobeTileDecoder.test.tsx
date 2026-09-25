import { StrictMode } from 'react';
import { render } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

const state = vi.hoisted(() => ({ loaders: [] as Array<{ dispose: ReturnType<typeof vi.fn> }>, active: null as unknown }));
vi.mock('three/examples/jsm/loaders/DRACOLoader.js', () => ({
  DRACOLoader: class {
    dispose = vi.fn();
    constructor() { state.loaders.push(this); }
    setDecoderPath() { return this; }
  },
}));
vi.mock('3d-tiles-renderer/r3f', () => ({
  TilesPlugin: ({ args }: { args: Array<{ dracoLoader: unknown; autoDispose: boolean }> }) => {
    state.active = args[0].dracoLoader;
    expect(args[0].autoDispose).toBe(false);
    return null;
  },
}));
vi.mock('3d-tiles-renderer/plugins', () => ({ GLTFExtensionsPlugin: class {} }));
import { GlobeTileDecoder } from './GlobeTileDecoder';

describe('globe tile decoder lifetime', () => {
  it('preserves pending decoder work across parent renders and disposes on unmount', () => {
    state.loaders = [];
    const view = render(<GlobeTileDecoder />);
    const active = state.active;
    view.rerender(<GlobeTileDecoder />);
    view.rerender(<GlobeTileDecoder />);
    expect(state.active).toBe(active);
    expect(state.loaders).toHaveLength(1);
    expect(state.loaders[0].dispose).not.toHaveBeenCalled();
    view.unmount();
    expect(state.loaders[0].dispose).toHaveBeenCalledOnce();
  });

  it('replaces the disposed StrictMode probe with a fresh live decoder', () => {
    state.loaders = [];
    const view = render(<StrictMode><GlobeTileDecoder /></StrictMode>);
    expect(state.loaders).toHaveLength(2);
    expect(state.loaders[0].dispose).toHaveBeenCalledOnce();
    expect(state.active).toBe(state.loaders[1]);
    expect(state.loaders[1].dispose).not.toHaveBeenCalled();
    view.unmount();
    expect(state.loaders[1].dispose).toHaveBeenCalledOnce();
  });
});
