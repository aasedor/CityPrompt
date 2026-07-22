/**
 * A terrain probe expressed in a local east/north/up frame, in metres.
 * Keeping the fit local avoids the numerical conditioning problems caused by
 * solving directly in longitude/latitude or Earth-centred coordinates.
 */
export interface TerrainContactSample {
  x: number;
  y: number;
  z: number;
}

export type TerrainContactPlaneKind = 'least_squares' | 'flat_fallback';

/** z = originZ + slopeX * (x - originX) + slopeY * (y - originY). */
export interface TerrainContactPlane {
  originX: number;
  originY: number;
  originZ: number;
  /** Rise in metres for one metre travelled east. */
  slopeX: number;
  /** Rise in metres for one metre travelled north. */
  slopeY: number;
  kind: TerrainContactPlaneKind;
  /** Number of finite input samples before deterministic fit downsampling. */
  sampleCount: number;
  /** Number of bounded samples considered by the robust fit. */
  fitSampleCount: number;
  inlierCount: number;
  rmsResidualMeters: number;
  maxResidualMeters: number;
}

export interface TerrainContactPlaneOptions {
  /** Stable stored/project terrain used when a plane cannot be identified. */
  fallbackElevationMeters?: number | null;
  /** Maximum residual admitted to the initial ground-surface consensus. */
  outlierToleranceMeters?: number;
  /** Robust-scale multiplier used while refining the consensus. */
  madMultiplier?: number;
  /** Small residual floor that prevents millimetre noise rejecting all probes. */
  minimumResidualToleranceMeters?: number;
  /** Minority object-top hits are rejected; at least this ratio must agree. */
  minimumInlierRatio?: number;
  /** Hard runtime bound. Samples are selected evenly and deterministically. */
  maximumFitSamples?: number;
}

export interface FoundationContactProfileOptions {
  /** Visible foundation above the highest perimeter terrain sample. */
  revealMeters?: number;
  /** Maximum total vertical foundation skirt, including the high-side reveal. */
  maxSkirtHeightMeters?: number;
  /** Used only when no finite perimeter elevations are available. */
  fallbackElevationMeters?: number | null;
}

export interface FoundationContactProfile {
  sampleCount: number;
  lowGroundElevationMeters: number;
  highGroundElevationMeters: number;
  terrainReliefMeters: number;
  foundationTopElevationMeters: number;
  skirtBottomElevationMeters: number;
  skirtHeightMeters: number;
  requiredSkirtHeightMeters: number;
  /** Ground relief below a capped skirt that needs grading/retaining treatment. */
  uncoveredReliefMeters: number;
  revealMeters: number;
  isSkirtCapped: boolean;
}

export interface TerrainContactResolveOptions {
  /** Maximum positive residual before a probe is treated as roof/canopy. */
  raisedObjectToleranceMeters?: number;
  /** Maximum negative residual before a coarse/root-tile miss is rejected. */
  loweredSurfaceToleranceMeters?: number;
}

const DEFAULT_OUTLIER_TOLERANCE_METERS = 1.25;
const DEFAULT_MAD_MULTIPLIER = 3.5;
const DEFAULT_MINIMUM_RESIDUAL_TOLERANCE_METERS = 0.08;
const DEFAULT_MINIMUM_INLIER_RATIO = 0.5;
const DEFAULT_MAXIMUM_FIT_SAMPLES = 24;
const DEFAULT_FOUNDATION_REVEAL_METERS = 0.18;
const DEFAULT_MAX_SKIRT_HEIGHT_METERS = 3;
const DEGENERATE_RELATIVE_EPSILON = 1e-10;

interface LeastSquaresPlane {
  originX: number;
  originY: number;
  originZ: number;
  slopeX: number;
  slopeY: number;
}

function clamp(value: number, minimum: number, maximum: number): number {
  return Math.max(minimum, Math.min(maximum, value));
}

function finiteOr(value: number | null | undefined, fallback: number): number {
  return Number.isFinite(value) ? value as number : fallback;
}

function median(values: number[]): number {
  if (values.length === 0) return Number.NaN;
  const sorted = [...values].sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 === 1
    ? sorted[middle]
    : (sorted[middle - 1] + sorted[middle]) / 2;
}

function selectBoundedSamples(
  samples: TerrainContactSample[],
  maximumFitSamples: number,
): TerrainContactSample[] {
  if (samples.length <= maximumFitSamples) return samples;
  if (maximumFitSamples <= 1) return [samples[Math.floor((samples.length - 1) / 2)]];

  const selected: TerrainContactSample[] = [];
  for (let index = 0; index < maximumFitSamples; index += 1) {
    const sourceIndex = Math.round(index * (samples.length - 1) / (maximumFitSamples - 1));
    selected.push(samples[sourceIndex]);
  }
  return selected;
}

/**
 * Centred least-squares solve for z = ax + by + c. The determinant check is
 * relative to the sample spread, so a valid small site is not mistaken for a
 * degenerate one merely because its coordinates are close together.
 */
function fitLeastSquaresPlane(samples: TerrainContactSample[]): LeastSquaresPlane | null {
  if (samples.length < 3) return null;

  const inverseCount = 1 / samples.length;
  const originX = samples.reduce((total, sample) => total + sample.x, 0) * inverseCount;
  const originY = samples.reduce((total, sample) => total + sample.y, 0) * inverseCount;
  const originZ = samples.reduce((total, sample) => total + sample.z, 0) * inverseCount;

  let xx = 0;
  let xy = 0;
  let yy = 0;
  let xz = 0;
  let yz = 0;
  for (const sample of samples) {
    const x = sample.x - originX;
    const y = sample.y - originY;
    const z = sample.z - originZ;
    xx += x * x;
    xy += x * y;
    yy += y * y;
    xz += x * z;
    yz += y * z;
  }

  const determinant = xx * yy - xy * xy;
  const spreadScale = Math.max(1, xx * yy);
  if (!Number.isFinite(determinant) || determinant <= spreadScale * DEGENERATE_RELATIVE_EPSILON) {
    return null;
  }

  const slopeX = (xz * yy - yz * xy) / determinant;
  const slopeY = (yz * xx - xz * xy) / determinant;
  if (![originX, originY, originZ, slopeX, slopeY].every(Number.isFinite)) return null;

  return { originX, originY, originZ, slopeX, slopeY };
}

function signedResidual(plane: LeastSquaresPlane, sample: TerrainContactSample): number {
  return sample.z - (
    plane.originZ
    + plane.slopeX * (sample.x - plane.originX)
    + plane.slopeY * (sample.y - plane.originY)
  );
}

function flatFallbackPlane(
  samples: TerrainContactSample[],
  fallbackElevationMeters: number | null | undefined,
  sampleCount: number,
): TerrainContactPlane | null {
  const fallback = Number.isFinite(fallbackElevationMeters)
    ? fallbackElevationMeters as number
    : median(samples.map((sample) => sample.z));
  if (!Number.isFinite(fallback)) return null;

  return {
    originX: samples.length > 0
      ? samples.reduce((total, sample) => total + sample.x, 0) / samples.length
      : 0,
    originY: samples.length > 0
      ? samples.reduce((total, sample) => total + sample.y, 0) / samples.length
      : 0,
    originZ: fallback,
    slopeX: 0,
    slopeY: 0,
    kind: 'flat_fallback',
    sampleCount,
    fitSampleCount: samples.length,
    inlierCount: samples.length,
    rmsResidualMeters: 0,
    maxResidualMeters: 0,
  };
}

interface ConsensusCandidate {
  plane: LeastSquaresPlane;
  inlierIndices: number[];
  inlierMedianResidual: number;
  allMedianResidual: number;
}

function isBetterConsensus(
  candidate: ConsensusCandidate,
  current: ConsensusCandidate | null,
): boolean {
  if (!current) return true;
  if (candidate.inlierIndices.length !== current.inlierIndices.length) {
    return candidate.inlierIndices.length > current.inlierIndices.length;
  }
  if (candidate.inlierMedianResidual !== current.inlierMedianResidual) {
    return candidate.inlierMedianResidual < current.inlierMedianResidual;
  }
  if (candidate.allMedianResidual !== current.allMedianResidual) {
    return candidate.allMedianResidual < current.allMedianResidual;
  }
  // The loop is lexicographic, so keeping the first exact tie is deterministic.
  return false;
}

function findInitialConsensus(
  samples: TerrainContactSample[],
  outlierToleranceMeters: number,
  minimumInliers: number,
): number[] | null {
  let best: ConsensusCandidate | null = null;

  // At most 24 bounded samples reach this loop (2,024 triples / ~49k probes).
  for (let a = 0; a < samples.length - 2; a += 1) {
    for (let b = a + 1; b < samples.length - 1; b += 1) {
      for (let c = b + 1; c < samples.length; c += 1) {
        const plane = fitLeastSquaresPlane([samples[a], samples[b], samples[c]]);
        if (!plane) continue;
        const residuals = samples.map((sample) => Math.abs(signedResidual(plane, sample)));
        const inlierIndices = residuals
          .map((residual, index) => ({ residual, index }))
          .filter(({ residual }) => residual <= outlierToleranceMeters)
          .map(({ index }) => index);
        if (inlierIndices.length < minimumInliers) continue;

        const candidate: ConsensusCandidate = {
          plane,
          inlierIndices,
          inlierMedianResidual: median(inlierIndices.map((index) => residuals[index])),
          allMedianResidual: median(residuals),
        };
        if (isBetterConsensus(candidate, best)) best = candidate;
      }
    }
  }

  return best?.inlierIndices ?? null;
}

/**
 * Fit a presentation-safe terrain plane while rejecting minority roof/canopy
 * hits. A deterministic exhaustive consensus seed is followed by a centred
 * least-squares refinement, so legitimate cross-slope is preserved rather
 * than being confused with an absolute elevation change.
 */
export function fitTerrainContactPlane(
  inputSamples: Array<TerrainContactSample | null | undefined>,
  options: TerrainContactPlaneOptions = {},
): TerrainContactPlane | null {
  const finiteSamples = inputSamples.filter(
    (sample): sample is TerrainContactSample => Boolean(sample)
      && Number.isFinite(sample?.x)
      && Number.isFinite(sample?.y)
      && Number.isFinite(sample?.z),
  );
  const maximumFitSamples = Math.max(
    3,
    Math.floor(finiteOr(options.maximumFitSamples, DEFAULT_MAXIMUM_FIT_SAMPLES)),
  );
  const samples = selectBoundedSamples(finiteSamples, maximumFitSamples);
  if (samples.length < 3) {
    return flatFallbackPlane(
      samples,
      options.fallbackElevationMeters,
      finiteSamples.length,
    );
  }

  const outlierToleranceMeters = Math.max(
    0.01,
    finiteOr(options.outlierToleranceMeters, DEFAULT_OUTLIER_TOLERANCE_METERS),
  );
  const minimumResidualToleranceMeters = clamp(
    finiteOr(
      options.minimumResidualToleranceMeters,
      DEFAULT_MINIMUM_RESIDUAL_TOLERANCE_METERS,
    ),
    0.001,
    outlierToleranceMeters,
  );
  const madMultiplier = Math.max(1, finiteOr(options.madMultiplier, DEFAULT_MAD_MULTIPLIER));
  const minimumInlierRatio = clamp(
    finiteOr(options.minimumInlierRatio, DEFAULT_MINIMUM_INLIER_RATIO),
    0.34,
    1,
  );
  const minimumInliers = Math.max(3, Math.ceil(samples.length * minimumInlierRatio));
  let inlierIndices = findInitialConsensus(samples, outlierToleranceMeters, minimumInliers);
  if (!inlierIndices) {
    return flatFallbackPlane(
      samples,
      options.fallbackElevationMeters,
      finiteSamples.length,
    );
  }

  let plane: LeastSquaresPlane | null = null;
  // Two refinement passes are sufficient after the exact consensus seed and
  // keep this helper predictably bounded when many public-realm zones mount.
  for (let iteration = 0; iteration < 2; iteration += 1) {
    plane = fitLeastSquaresPlane(inlierIndices.map((index) => samples[index]));
    if (!plane) break;

    const residuals = samples.map((sample) => signedResidual(plane as LeastSquaresPlane, sample));
    const residualMedian = median(residuals);
    const medianAbsoluteDeviation = median(
      residuals.map((residual) => Math.abs(residual - residualMedian)),
    );
    const robustSigma = 1.4826 * medianAbsoluteDeviation;
    const refinementTolerance = Math.min(
      outlierToleranceMeters,
      Math.max(minimumResidualToleranceMeters, robustSigma * madMultiplier),
    );
    const refined = residuals
      .map((residual, index) => ({ residual, index }))
      .filter(({ residual }) => Math.abs(residual - residualMedian) <= refinementTolerance)
      .map(({ index }) => index);
    if (refined.length < minimumInliers || !fitLeastSquaresPlane(refined.map((index) => samples[index]))) {
      break;
    }
    inlierIndices = refined;
  }

  plane = fitLeastSquaresPlane(inlierIndices.map((index) => samples[index]));
  if (!plane) {
    return flatFallbackPlane(
      samples,
      options.fallbackElevationMeters,
      finiteSamples.length,
    );
  }

  const absoluteResiduals = inlierIndices.map(
    (index) => Math.abs(signedResidual(plane as LeastSquaresPlane, samples[index])),
  );
  const squaredResidualTotal = absoluteResiduals.reduce(
    (total, residual) => total + residual * residual,
    0,
  );

  return {
    ...plane,
    kind: 'least_squares',
    sampleCount: finiteSamples.length,
    fitSampleCount: samples.length,
    inlierCount: inlierIndices.length,
    rmsResidualMeters: Math.sqrt(squaredResidualTotal / inlierIndices.length),
    maxResidualMeters: Math.max(...absoluteResiduals),
  };
}

/** Return the plane's vertical offset from its centred origin at local x/y. */
export function samplePlaneOffset(
  plane: TerrainContactPlane | null | undefined,
  x: number,
  y: number,
): number {
  if (!plane || !Number.isFinite(x) || !Number.isFinite(y)) return 0;
  const offset = plane.slopeX * (x - plane.originX) + plane.slopeY * (y - plane.originY);
  return Number.isFinite(offset) ? offset : 0;
}

/** Reconcile one streamed-tile probe with a robust local terrain plane. Small
 * deviations retain real micro-topography; isolated high object tops and
 * implausible low coarse-tile hits fall back to the fitted contact surface. */
export function resolveTerrainContactElevation(
  plane: TerrainContactPlane | null | undefined,
  sampledElevationMeters: number | null | undefined,
  x: number,
  y: number,
  options: TerrainContactResolveOptions = {},
): number | null {
  if (!plane) return Number.isFinite(sampledElevationMeters)
    ? sampledElevationMeters as number
    : null;
  const expected = plane.originZ + samplePlaneOffset(plane, x, y);
  if (!Number.isFinite(sampledElevationMeters)) return expected;
  const sampled = sampledElevationMeters as number;
  const raisedTolerance = Math.max(0.1, options.raisedObjectToleranceMeters ?? 1.75);
  const loweredTolerance = Math.max(0.1, options.loweredSurfaceToleranceMeters ?? 4);
  return sampled > expected + raisedTolerance || sampled < expected - loweredTolerance
    ? expected
    : sampled;
}

/**
 * Resolve a level foundation top from terrain elevations around its perimeter.
 * The high side keeps a small reveal; the vertical skirt reaches toward the
 * low side but is capped so a bad/very steep contact does not create a tower.
 */
export function resolveFoundationContactProfile(
  perimeterElevations: Array<number | null | undefined>,
  options: FoundationContactProfileOptions = {},
): FoundationContactProfile | null {
  const finiteElevations = perimeterElevations
    .filter((elevation): elevation is number => Number.isFinite(elevation))
    .sort((a, b) => a - b);
  const fallbackElevation = Number.isFinite(options.fallbackElevationMeters)
    ? options.fallbackElevationMeters as number
    : null;
  if (finiteElevations.length === 0 && fallbackElevation === null) return null;

  const elevations = finiteElevations.length > 0 ? finiteElevations : [fallbackElevation as number];
  const revealMeters = Math.max(
    0,
    finiteOr(options.revealMeters, DEFAULT_FOUNDATION_REVEAL_METERS),
  );
  // Never allow the cap to be shallower than the requested high-side reveal.
  const maxSkirtHeightMeters = Math.max(
    revealMeters,
    finiteOr(options.maxSkirtHeightMeters, DEFAULT_MAX_SKIRT_HEIGHT_METERS),
  );
  const lowGroundElevationMeters = elevations[0];
  const highGroundElevationMeters = elevations[elevations.length - 1];
  const terrainReliefMeters = highGroundElevationMeters - lowGroundElevationMeters;
  const foundationTopElevationMeters = highGroundElevationMeters + revealMeters;
  const requiredSkirtHeightMeters = terrainReliefMeters + revealMeters;
  const skirtHeightMeters = Math.min(requiredSkirtHeightMeters, maxSkirtHeightMeters);
  const skirtBottomElevationMeters = foundationTopElevationMeters - skirtHeightMeters;
  const uncoveredReliefMeters = Math.max(
    0,
    skirtBottomElevationMeters - lowGroundElevationMeters,
  );

  return {
    sampleCount: finiteElevations.length,
    lowGroundElevationMeters,
    highGroundElevationMeters,
    terrainReliefMeters,
    foundationTopElevationMeters,
    skirtBottomElevationMeters,
    skirtHeightMeters,
    requiredSkirtHeightMeters,
    uncoveredReliefMeters,
    revealMeters,
    isSkirtCapped: requiredSkirtHeightMeters > maxSkirtHeightMeters,
  };
}
