import type { SiteZone } from '@/types';
import { getDerivedParkAccess, resolveManualParkAccess, type ParkAccessPath } from '@/components/viewer/globe/parkAccessConnections';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';
import { hasNativePark } from './nativeParkRegistry';

export interface NativeParkApproach extends ParkAccessPath { owner: SiteZone }

/** Reuse the shared access solution for placement and landscape clearance. */
export function nativeParkApproaches(zones: SiteZone[], derive = false): NativeParkApproach[] {
  if (!zones.some(hasNativePark)) return [];
  const plans = derive ? resolveManualParkAccess(zones).parks : null;
  return zones.filter(hasNativePark).flatMap(owner => {
    const plan = plans?.find(p => p.parkZoneId === owner.id) ?? getDerivedParkAccess(owner);
    return (plan?.connections ?? []).map(connection => ({owner, points: connection.path, widthM: connection.widthM}));
  });
}

export function clearsNativeParkApproaches(lng: number, lat: number, radiusM: number, paths: NativeParkApproach[]): boolean {
  const east = metersPerDegLon(lat);
  return paths.every(path => path.points.slice(1).every((end, i) => {
    const start = path.points[i];
    const ax = (start[0] - lng) * east, ay = (start[1] - lat) * METERS_PER_DEG_LAT;
    const dx = (end[0] - start[0]) * east, dy = (end[1] - start[1]) * METERS_PER_DEG_LAT;
    const t = Math.max(0, Math.min(1, -(ax * dx + ay * dy) / Math.max(.000001, dx * dx + dy * dy)));
    return Math.hypot(ax + dx * t, ay + dy * t) >= radiusM + path.widthM / 2;
  }));
}
