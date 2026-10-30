import type { NativeStreetPose, StreetRouteStation } from './nativeStreetPilot';
import bridges from '@/data/nativeBridgePilots.json';

export function modularBridgeProgramFor(variant: unknown): ModularBridgeProgram | undefined {
  return import.meta.env.DEV && import.meta.env.MODE === 'development'
    ? bridges.find(row => row.id === variant)?.program : undefined;
}

export interface ModularBridgeProgram {
  adapter: string; minLengthM: number; maxLengthM: number;
  bridge: { approachM: number; endM: number; bayM: number; deckHeightM: number; clearWidthM: number };
}
interface BridgePilot {
  widthM: number; program: ModularBridgeProgram;
  modules: Record<string, { url: string; sha256: string }>;
}

export function modularBridgeRouteProblem(program: ModularBridgeProgram, route: StreetRouteStation[], sampled = false): string | null {
  if (sampled ? route.length < 2 : route.length !== 2) return 'Draw a start and end point for this straight bridge.';
  if (route.some(p => !Number.isFinite(p.x) || !Number.isFinite(p.y))) return 'Choose two valid bridge endpoints.';
  const a = route[0], b = route[route.length - 1], dx = b.x - a.x, dy = b.y - a.y, length = Math.hypot(dx, dy);
  if (length < program.minLengthM - .01 || length > program.maxLengthM + .01)
    return `Draw a bridge ${program.minLengthM}–${program.maxLengthM} m long, including its compact approaches.`;
  let previous = -1;
  for (const p of route) {
    const x = p.x - a.x, y = p.y - a.y, station = (x * dx + y * dy) / length;
    if (Math.abs(x * dy - y * dx) / length > .05 || station < previous - .01)
      return 'Keep the bridge straight between its two endpoints.';
    previous = station;
  }
  return null;
}

/** End structures and stair geometry stay rigid. Only the repeated middle bay
 * adjusts along the route, sharing the small remainder across all its bays. */
export function modularBridgePoses(pilot: BridgePilot, route: StreetRouteStation[]): NativeStreetPose[] {
  const problem = modularBridgeRouteProblem(pilot.program, route, true);
  if (problem) throw new Error(problem);
  const a = route[0], b = route[route.length - 1], dx = b.x - a.x, dy = b.y - a.y, length = Math.hypot(dx, dy);
  const { approachM, endM, bayM } = pilot.program.bridge;
  const middle = length - 2 * (approachM + endM), count = Math.max(1, Math.round(middle / bayM));
  const bayLength = middle / count;
  const parts = [
    { kind: 'bridge_left_stair', length: approachM }, { kind: 'bridge_left_end', length: endM },
    ...Array.from({ length: count }, () => ({ kind: 'bridge_bay', length: bayLength })),
    { kind: 'bridge_right_end', length: endM }, { kind: 'bridge_right_stair', length: approachM },
  ];
  let start = 0;
  return parts.map(part => {
    const asset = pilot.modules[part.kind];
    if (!asset) throw new Error('A bridge component has no verified module binding.');
    const stationM = start + part.length / 2; start += part.length;
    return { kind: part.kind, ...asset, x: a.x + dx * stationM / length, y: a.y + dy * stationM / length,
      z: (a.z ?? 0) + ((b.z ?? 0) - (a.z ?? 0)) * stationM / length,
      yaw: Math.atan2(dy, dx) - Math.PI / 2, scale: 1, stationM, surfaceLiftM: 0,
      ...(part.kind === 'bridge_bay' ? { longitudinalScale: bayLength / bayM } : {}),
    };
  });
}

/** The source uses risers <= 0.2 m at each end and a 4 m clear deck.
 * Return null outside that real walking surface, including the empty banks. */
export function modularBridgeWalkingHeight(program: ModularBridgeProgram, lateral: number, station: number, length: number): number | null {
  const { approachM, deckHeightM, clearWidthM } = program.bridge;
  if (![lateral, station, length].every(Number.isFinite) || Math.abs(lateral) > clearWidthM / 2
    || station < 0 || station > length) return null;
  const distance = Math.min(station, length - station);
  if (distance >= approachM) return deckHeightM;
  const count = Math.ceil(deckHeightM / .2);
  return distance <= 0 ? 0 : Math.min(deckHeightM,
    (Math.floor(distance / (approachM / count) + 1e-7) + 1) * deckHeightM / count);
}
