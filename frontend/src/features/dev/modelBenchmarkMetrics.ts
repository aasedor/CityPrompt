export interface FrameTimingSummary {
  averageMs: number;
  medianMs: number;
  p95Ms: number;
  fpsFromMedian: number;
}

export interface BenchmarkGridPosition {
  x: number;
  z: number;
}

export interface ComparableBenchmarkRun {
  modelDrawCalls: number;
  timing: FrameTimingSummary;
  triangles: number;
  minY: number;
  extents: [number, number, number];
}

export interface BenchmarkComparison {
  drawCallReductionPercent: number;
  medianSpeedup: number;
  p95Speedup: number;
  geometryMatches: boolean;
  groundDatumMatches: boolean;
}

function rounded(value: number, digits = 2): number {
  return Number(value.toFixed(digits));
}

export function percentile(values: readonly number[], quantile: number): number {
  if (values.length === 0) return 0;
  const sorted = [...values].sort((left, right) => left - right);
  const index = Math.min(
    sorted.length - 1,
    Math.max(0, Math.ceil(quantile * sorted.length) - 1),
  );
  return sorted[index];
}

export function summarizeFrameTimings(values: readonly number[]): FrameTimingSummary {
  if (values.length === 0) {
    return { averageMs: 0, medianMs: 0, p95Ms: 0, fpsFromMedian: 0 };
  }
  const averageMs = values.reduce((total, value) => total + value, 0) / values.length;
  const medianMs = percentile(values, 0.5);
  return {
    averageMs: rounded(averageMs),
    medianMs: rounded(medianMs),
    p95Ms: rounded(percentile(values, 0.95)),
    fpsFromMedian: medianMs > 0 ? rounded(1_000 / medianMs, 1) : 0,
  };
}

export function buildInstanceGrid(
  count: number,
  spacingX: number,
  spacingZ: number,
): BenchmarkGridPosition[] {
  const safeCount = Math.max(1, Math.floor(count));
  const columns = Math.ceil(Math.sqrt(safeCount));
  const rows = Math.ceil(safeCount / columns);
  return Array.from({ length: safeCount }, (_, index) => {
    const column = index % columns;
    const row = Math.floor(index / columns);
    return {
      x: (column - (columns - 1) / 2) * spacingX,
      z: (row - (rows - 1) / 2) * spacingZ,
    };
  });
}

export function compareBenchmarkRuns(
  original: ComparableBenchmarkRun,
  optimized: ComparableBenchmarkRun,
  tolerance = 1e-4,
): BenchmarkComparison {
  const geometryMatches = original.triangles === optimized.triangles
    && original.extents.every(
      (value, index) => Math.abs(value - optimized.extents[index]) <= tolerance,
    );
  return {
    drawCallReductionPercent: original.modelDrawCalls > 0
      ? rounded((1 - optimized.modelDrawCalls / original.modelDrawCalls) * 100)
      : 0,
    medianSpeedup: optimized.timing.medianMs > 0
      ? rounded(original.timing.medianMs / optimized.timing.medianMs)
      : 0,
    p95Speedup: optimized.timing.p95Ms > 0
      ? rounded(original.timing.p95Ms / optimized.timing.p95Ms)
      : 0,
    geometryMatches,
    groundDatumMatches: Math.abs(original.minY - optimized.minY) <= tolerance
      && Math.abs(optimized.minY) <= 0.02,
  };
}

export function formatBytes(bytes: number): string {
  return `${(bytes / 1_048_576).toFixed(2)} MiB`;
}
