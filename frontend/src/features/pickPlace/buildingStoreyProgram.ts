import type { PlaceAsset } from './assetRegistry';

export type BuildingStoreyProgram = NonNullable<PlaceAsset['storeyProgram']>;

export function storeyProgramHeight(program: BuildingStoreyProgram, storeys: number): number {
  return Math.round((
    program.podiumHeightM
    + (storeys - program.podiumStoreys) * program.repeatedStoreyHeightM
    + program.roofHeightM
  ) * 100) / 100;
}

/** A saved edit keeps the exact asset only when both its discrete storey count
 * and derived height belong to the reviewed programme. */
export function storeyProgramSupports(
  program: BuildingStoreyProgram,
  storeys: unknown,
  heightM: unknown,
): boolean {
  const parsedStoreys = Number(storeys);
  const parsedHeight = Number(heightM);
  return Number.isInteger(parsedStoreys)
    && parsedStoreys >= program.minStoreys
    && parsedStoreys <= program.maxStoreys
    && Number.isFinite(parsedHeight)
    && Math.abs(parsedHeight - storeyProgramHeight(program, parsedStoreys)) <= 0.05;
}
