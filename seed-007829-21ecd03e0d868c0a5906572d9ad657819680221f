import type { SiteZone } from '@/types';

export const MAX_DETAILED_STREET_ZONES = 160;
export const MAX_TREE_STREET_ZONES = 24;

/** Google Tiles keeps streets as authoritative engineering geometry. Mature
 * street trees are resolved by the final architectural render, where they can
 * respect crossings, driveways, sight triangles and the rendered planting
 * design instead of appearing as lightweight procedural props. */
export function shouldRenderLiveStreetTrees(): boolean {
  return false;
}

function normalizedProperty(zone: SiteZone, key: string): string {
  const props = zone.properties as Record<string, unknown> | undefined;
  return String(props?.[key] ?? '').toLowerCase().trim().replace(/-/g, '_');
}

/** Small deterministic hash used for stable LOD ranking and frame staggering. */
export function stableStreetHash(value: string): number {
  let hash = 2166136261;
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

export function streetTerrainSampleOffset(zoneId: string, interval: number): number {
  return interval > 0 ? stableStreetHash(zoneId) % interval : 0;
}

function detailPriority(zone: SiteZone): number {
  const archetype = normalizedProperty(zone, 'road_archetype_id');
  const role = normalizedProperty(zone, 'street_role');
  if (archetype.includes('roundabout')) return 1000;
  if (role === 'spine' || role === 'primary' || archetype.includes('main_street')) return 900;
  if (role === 'collector' || archetype.includes('collector') || archetype.includes('arterial')) return 800;
  if (role === 'trail' || role === 'path' || archetype.includes('trail')) return 700;
  if (role === 'local' || role === 'residential' || archetype.includes('residential')) return 600;
  if (role === 'lane' || archetype.includes('laneway') || archetype.includes('alley')) return 300;
  return 500;
}

function ranked(zones: SiteZone[]): SiteZone[] {
  return [...zones].sort((left, right) => (
    detailPriority(right) - detailPriority(left)
    || stableStreetHash(left.id) - stableStreetHash(right.id)
  ));
}

/**
 * Large communities keep a representative, hierarchy-first street layer
 * instead of dropping all public-realm detail at an arbitrary count.
 */
export function selectDetailedStreetZones(
  zones: SiteZone[],
  limit = MAX_DETAILED_STREET_ZONES,
): SiteZone[] {
  if (zones.length <= limit) return zones;
  const selected = new Set(ranked(zones).slice(0, Math.max(0, limit)).map((zone) => zone.id));
  return zones.filter((zone) => selected.has(zone.id));
}

/** Tree rows are a higher-cost district-scale accent; prioritize key streets. */
export function selectTreeStreetIds(
  zones: SiteZone[],
  limit = MAX_TREE_STREET_ZONES,
): Set<string> {
  const candidates = ranked(zones).filter((zone) => (
    !normalizedProperty(zone, 'road_archetype_id').includes('roundabout')
    && !normalizedProperty(zone, 'road_archetype_id').includes('laneway')
    && normalizedProperty(zone, 'street_role') !== 'lane'
  ));
  return new Set(candidates.slice(0, Math.max(0, limit)).map((zone) => zone.id));
}
