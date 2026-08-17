import { describe, expect, it } from 'vitest';
import { MODEL_BENCHMARK_ASSETS } from './modelBenchmarkAssets';


describe('MODEL_BENCHMARK_ASSETS', () => {
  it('keeps benchmark ids and source paths unique', () => {
    expect(new Set(MODEL_BENCHMARK_ASSETS.map((asset) => asset.id)).size)
      .toBe(MODEL_BENCHMARK_ASSETS.length);
    expect(new Set(MODEL_BENCHMARK_ASSETS.map((asset) => asset.relativePath)).size)
      .toBe(MODEL_BENCHMARK_ASSETS.length);
  });

  it('uses the same immutable delivery object for the Machiya A/A control', () => {
    const control = MODEL_BENCHMARK_ASSETS.find(
      (asset) => asset.id === 'restored-kyoto-machiya-control',
    );

    expect(control?.comparisonKind).toBe('delivery-control');
    expect(control?.relativePath).toContain(
      'restored-kyoto-machiya/assembled--default--lod0.glb',
    );
    expect(control?.original).toEqual(control?.optimized);
    expect(control?.original.sha256).toBe(
      '5a785be0b30a37be50c1228cf0e5d00636b13f745bad753a103dcfc77a68bb9c',
    );
  });
});
