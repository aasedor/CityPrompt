import type { SiteZone } from '@/types';
import type { SharedSiteGroundState } from './SharedSiteGroundProvider';
import { sharedSiteGroundContains } from './sharedSiteGround';

/** The same authored, level surface used by the prepared-site renderer. The
 * caller must first verify that the whole zone belongs to this boundary. */
export function preparedEntranceGround(boundary: SiteZone | null | undefined,
  level: number | null | undefined): SharedSiteGroundState | null {
  if (!boundary || level == null || !Number.isFinite(level)) return null;
  const ring = boundary.coordinates.map(([lng, lat]): [number, number] => [lng, lat]);
  const contains = (lng: number, lat: number) => sharedSiteGroundContains(ring, lng, lat);
  return { status: 'ready', prepared: true, snapshot: null, boundaryCoordinates: ring, contains,
    heightAt: (lng, lat) => contains(lng, lat) ? level : null,
    revision: `prepared:${boundary.id}:${boundary.updated_at}:${level}`,
    isCurrent: () => true };
}
