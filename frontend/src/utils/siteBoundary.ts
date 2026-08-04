import type { SiteZone } from '@/types';

/** Resolve the project's one authoritative, drawable site boundary.
 *
 * New API responses carry an explicit active flag. Legacy fixtures and saved
 * browser state may not, so the first valid boundary remains a safe fallback
 * only when no boundary has an explicit state at all.
 */
export function getActiveSiteBoundary(zones: SiteZone[]): SiteZone | null {
  const boundaries = zones.filter((zone) => (
    zone.zone_type === 'site_boundary' && zone.coordinates.length >= 3
  ));
  const explicit = boundaries.find((zone) => zone.is_active_boundary === true);
  if (explicit) return explicit;
  if (boundaries.some((zone) => zone.is_active_boundary !== undefined)) return null;
  return boundaries[0] ?? null;
}
