import type { SpecialistFixture } from './specialistStreetProgram';

export const ELEVATED_RAIL_VARIANT = 'student_elevated_garden_rail_v1';
const STRUCTURAL = new Set(['rail_pier', 'rail_train', 'rail_buffer', 'rail_end']);

export function elevatedRailPierStations(length: number): number[] {
  const spans = Math.ceil((length - 4) / 22);
  return Array.from({ length: spans + 1 }, (_, i) => 2 + (length - 4) * i / spans);
}

/** Continuous deck lives in the source program. Complete supports are placed
 * independently, including a pier near each end of a non-module-length route. */
export function elevatedRailFixtures(source: SpecialistFixture[], length: number): SpecialistFixture[] {
  const result: SpecialistFixture[] = [];
  const add = (kind: string, x: number, y: number, yaw = 0) => result.push({ kind, x, y, z: 0, yaw, scale: 1 });
  for (let center = 24; center < length + 24; center += 48) {
    for (const pose of source) if (!STRUCTURAL.has(pose.kind)) result.push({ ...pose, y: center + pose.y });
  }
  for (const station of elevatedRailPierStations(length)) add('rail_pier', 0, station);
  add('rail_train', 2.05, length / 2);
  for (const [station, yaw] of [[1.4, 0], [length - 1.4, Math.PI]]) {
    for (const x of [-2.05, 2.05]) add('rail_buffer', x, station, yaw);
  }
  add('rail_end', 0, .04);
  add('rail_end', 0, length - .04, Math.PI);
  return result;
}
