import { describe, expect, it } from 'vitest';
import {
  buildInstanceGrid,
  compareBenchmarkRuns,
  formatBytes,
  percentile,
  summarizeFrameTimings,
} from './modelBenchmarkMetrics';

describe('model benchmark metrics', () => {
  it('summarizes deterministic frame timings without averaging the percentile', () => {
    expect(percentile([8, 2, 4, 6], 0.5)).toBe(4);
    expect(summarizeFrameTimings([2, 4, 6, 8])).toEqual({
      averageMs: 5,
      medianMs: 4,
      p95Ms: 8,
      fpsFromMedian: 250,
    });
  });

  it('centres 1, 10, and 25 instance grids around the same origin', () => {
    for (const count of [1, 10, 25]) {
      const positions = buildInstanceGrid(count, 20, 10);
      expect(positions).toHaveLength(count);
      const xValues = positions.map(({ x }) => x);
      expect(Math.min(...xValues) + Math.max(...xValues)).toBeCloseTo(0);
    }
  });

  it('reports draw-call speedup and rejects geometry or ground drift', () => {
    const original = {
      modelDrawCalls: 2_011,
      timing: summarizeFrameTimings([20, 22, 24]),
      triangles: 41_656,
      minY: 0,
      extents: [91.45, 22.1, 43.34] as [number, number, number],
    };
    const optimized = {
      modelDrawCalls: 15,
      timing: summarizeFrameTimings([3, 4, 5]),
      triangles: 41_656,
      minY: 0,
      extents: [91.45, 22.1, 43.34] as [number, number, number],
    };

    expect(compareBenchmarkRuns(original, optimized)).toMatchObject({
      drawCallReductionPercent: 99.25,
      medianSpeedup: 5.5,
      geometryMatches: true,
      groundDatumMatches: true,
    });
    expect(compareBenchmarkRuns(original, { ...optimized, minY: -0.2 }).groundDatumMatches).toBe(false);
    expect(formatBytes(3_922_560)).toBe('3.74 MiB');
  });
});
