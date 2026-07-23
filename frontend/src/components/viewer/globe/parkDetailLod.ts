import type { SiteZone } from '@/types';

/** Core authored structures remain available across ordinary compact and
 * stress pilots. Decorative-only parks use a smaller budget because their
 * deterministic ground remains visible even when live furniture is omitted. */
export const MAX_LIVE_FIXED_PROGRAM_PARK_ZONES = 24;
export const MAX_LIVE_DECORATIVE_PARK_ZONES = 16;

export function stableParkDetailHash(value: string): number {
  let hash = 2166136261;
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

export function parkTerrainSampleOffset(zoneId: string, interval: number): number {
  return interval > 0 ? stableParkDetailHash(zoneId) % interval : 0;
}

/** Deterministic, input-order-preserving budget selection. Core fixed program
 * is always ranked ahead of decorative canopy/seating and receives its own
 * independent allowance. */
export function selectBudgetedLiveParkZones(
  zones: SiteZone[],
  hasCoreFixedProgram: (zone: SiteZone) => boolean,
  fixedProgramLimit = MAX_LIVE_FIXED_PROGRAM_PARK_ZONES,
  decorativeLimit = MAX_LIVE_DECORATIVE_PARK_ZONES,
): SiteZone[] {
  const rank = (candidates: SiteZone[], limit: number) => new Set(
    [...candidates]
      .sort((left, right) => (
        stableParkDetailHash(left.id) - stableParkDetailHash(right.id)
        || left.id.localeCompare(right.id)
      ))
      .slice(0, Math.max(0, limit))
      .map((zone) => zone.id),
  );
  const fixedIds = rank(zones.filter(hasCoreFixedProgram), fixedProgramLimit);
  const decorativeIds = rank(zones.filter((zone) => !hasCoreFixedProgram(zone)), decorativeLimit);
  return zones.filter((zone) => fixedIds.has(zone.id) || decorativeIds.has(zone.id));
}
