import type { PlaceAsset } from './assetRegistry';

export type BuildingFootprintProgram = NonNullable<PlaceAsset['footprintProgram']>;

/** Storey editing can be supported while the authored plan stays locked. */
export function hasFixedBuildingFootprint(asset: PlaceAsset | undefined): boolean {
  const program = asset?.footprintProgram;
  return Boolean(program && (program.editable === false || program.minScale === program.maxScale));
}

export function footprintProgramSupports(program: BuildingFootprintProgram, scale: unknown): boolean {
  const parsed = Number(scale);
  return Number.isFinite(parsed) && parsed >= program.minScale && parsed <= program.maxScale;
}

export function footprintProgramTarget(
  program: BuildingFootprintProgram,
  scale: unknown = program.defaultScale,
): { widthM: number; depthM: number; scale: number } {
  const parsed = Number(scale);
  const safeScale = footprintProgramSupports(program, parsed) ? parsed : program.defaultScale;
  const fixed = program.minScale === program.maxScale;
  return {
    widthM: fixed ? program.nativeWidthM * safeScale : Math.round(program.nativeWidthM * safeScale * 10000) / 10000,
    depthM: fixed ? program.nativeDepthM * safeScale : Math.round(program.nativeDepthM * safeScale * 10000) / 10000,
    scale: safeScale,
  };
}
