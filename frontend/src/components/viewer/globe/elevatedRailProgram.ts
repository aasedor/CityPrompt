import type { SpecialistFixture } from './specialistStreetProgram';

export const ELEVATED_RAIL_VARIANT = 'student_elevated_garden_rail_v1';
export const SKYTRAIN_RAIL_VARIANT = 'skytrain_elevated_corridor_v0';
export const CIVIC_RAIL_VARIANT = 'elevated_rail_transit_corridor_v0';
export const STATION_RAIL_VARIANTS = [SKYTRAIN_RAIL_VARIANT, CIVIC_RAIL_VARIANT] as const;
export const isElevatedRail = (variant: unknown): boolean =>
  variant === ELEVATED_RAIL_VARIANT || STATION_RAIL_VARIANTS.some(id => id === variant);
export const hasElevatedStation = (variant: unknown): boolean => STATION_RAIL_VARIANTS.some(id => id === variant);
export interface RailStation { id: string; stationM: number }
const STRUCTURAL = new Set(['rail_pier', 'rail_train', 'rail_buffer', 'rail_end']);

/** A complete 48 m platform, canopy and stair envelope remains inside the route. */
export function elevatedRailStationProblem(length: number, stops: unknown): string | null {
  if (!Array.isArray(stops) || stops.length > 4) return 'Choose at most four rail stations.';
  const ids = new Set<string>(), positions: number[] = [];
  for (const raw of stops) {
    if (!raw || typeof raw !== 'object' || Object.keys(raw).sort().join(',') !== 'id,stationM') return 'A rail station has invalid saved data.';
    const stop = raw as RailStation;
    if (typeof stop.id !== 'string' || !/^[a-zA-Z0-9_-]{1,80}$/.test(stop.id) || ids.has(stop.id) || !Number.isFinite(stop.stationM))
      return 'A rail station needs a unique identity and valid position.';
    if (stop.stationM < 24 || stop.stationM > length - 24 + .001)
      return 'Leave 24 m at each route end for the full platform and ground access.';
    if (positions.some(position => Math.abs(position - stop.stationM) < 52))
      return 'Place rail stations at least 52 m apart so their entrances remain clear.';
    ids.add(stop.id); positions.push(stop.stationM);
  }
  return null;
}

export function elevatedRailPierStations(length: number): number[] {
  const spans = Math.ceil((length - 4) / 22);
  return Array.from({ length: spans + 1 }, (_, i) => 2 + (length - 4) * i / spans);
}

/** Continuous deck lives in the source program. Complete supports are placed
 * independently, including a pier near each end of a non-module-length route. */
export function elevatedRailFixtures(source: SpecialistFixture[], length: number, stops: RailStation[] = []): SpecialistFixture[] {
  const result: SpecialistFixture[] = [];
  const add = (kind: string, x: number, y: number, yaw = 0) => result.push({ kind, x, y, z: 0, yaw, scale: 1 });
  for (let center = 24; center < length + 24; center += 48) {
    for (const pose of source) if (!STRUCTURAL.has(pose.kind) && pose.kind !== 'rail_station') {
      const y = center + pose.y;
      // The full station ground entrance owns this strip. Keep trees, benches,
      // lights and under-deck planting out of its stairs and circulation.
      if (stops.some(stop => Math.abs(y - stop.stationM) < 24 && Math.abs(pose.x) < 10)) continue;
      result.push({ ...pose, y });
    }
  }
  for (const station of elevatedRailPierStations(length)) add('rail_pier', 0, station);
  add('rail_train', 2.05, stops[0]?.stationM ?? length / 2);
  for (const stop of stops) add('rail_station', 0, stop.stationM);
  for (const [station, yaw] of [[1.4, 0], [length - 1.4, Math.PI]]) {
    for (const x of [-2.05, 2.05]) add('rail_buffer', x, station, yaw);
  }
  add('rail_end', 0, .04);
  add('rail_end', 0, length - .04, Math.PI);
  return result;
}
