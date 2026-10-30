import type { SiteZone } from '@/types';
import { groundSurfaceFor } from './groundSurfaces';
import { isDrawnParking, parkingRowDirection } from '@/features/parks/drawnParking';

export interface AuthoredSurfaceClaim { zone_id: string; source_hash: string }

/** Canonical source at the same 1e-7 degree precision as compiled polygons. */
function canonicalRing(coordinates: number[][]): string {
  const points = coordinates.map(point => {
    if (!Number.isFinite(point[0]) || !Number.isFinite(point[1])) throw new Error('Invalid ground surface outline.');
    return `${Math.round(point[0] * 1e7)},${Math.round(point[1] * 1e7)}`;
  });
  if (points[0] === points[points.length - 1]) points.pop();
  if (points.length < 3) throw new Error('Invalid ground surface outline.');
  const candidates: string[] = [];
  for (const ring of [points, [...points].reverse()]) {
    const first = [...ring].sort()[0];
    ring.forEach((point, index) => {
      if (point === first) candidates.push([...ring.slice(index), ...ring.slice(0, index)].join(';'));
    });
  }
  return candidates.sort()[0];
}

export function authoredSurfaceSourceIdentity(zone: SiteZone): string | null {
  const finish = groundSurfaceFor(zone);
  if (zone.zone_type === 'site_boundary' || zone.properties?._plan_role === 'framework_height' || !finish) return null;
  const payload: unknown[] = ['cityprompt.authored-surface@1', finish.id, [canonicalRing(zone.coordinates)]];
  if (isDrawnParking(zone)) payload.push(['parking@1', parkingRowDirection(zone)]);
  return JSON.stringify(payload);
}

export function authoredSurfaceRevision(zones: SiteZone[]): string {
  return JSON.stringify(zones.flatMap(zone => {
    const identity = authoredSurfaceSourceIdentity(zone);
    return identity ? [[zone.id, identity]] : [];
  }).sort((left, right) => left[0].localeCompare(right[0])));
}

/** Snapshot every payload synchronously before WebCrypto yields to UI edits. */
export async function getAuthoredSurfaceCaptureClaims(zones: SiteZone[]): Promise<AuthoredSurfaceClaim[]> {
  const sources = zones.flatMap(zone => {
    const identity = authoredSurfaceSourceIdentity(zone);
    return identity ? [{ zone_id: zone.id, identity }] : [];
  });
  return Promise.all(sources.map(async source => ({ zone_id: source.zone_id,
    source_hash: Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(source.identity))),
      byte => byte.toString(16).padStart(2, '0')).join(''),
  })));
}
