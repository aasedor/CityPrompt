import type { SiteZone } from '@/types';
import { extractZoneCenterline } from '@/utils/roadGeometry';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';
import { isFixedSectionStreet, streetSectionWidth } from './streetPlacement';

/** Snap a near-perpendicular endpoint to a through street. Keep the adjacent
 * point fixed so the preview and saved route share one exact square junction.
 * Only catalogue streets participate; reference layers never become proposals. */
export function snapStreetEndpoint(line: number[][], index: number, zones: SiteZone[], ownerId?: string): number[][] {
  if (line.length < 2 || (index !== 0 && index !== line.length - 1)
    || line.some(p => p.length < 2 || !p.slice(0, 2).every(Number.isFinite))) return line;
  const point = line[index], adjacent = line[index === 0 ? 1 : index - 1];
  const lonM = metersPerDegLon(adjacent[1]);
  const local = (p: number[]) => [(p[0] - adjacent[0]) * lonM, (p[1] - adjacent[1]) * METERS_PER_DEG_LAT];
  const [px, py] = local(point), approachLength = Math.hypot(px, py);
  if (approachLength < 1) return line;
  let best: { point: number[]; distance: number } | undefined;
  for (const street of [...zones].sort((a, b) => a.id.localeCompare(b.id))) {
    if (street.id === ownerId || !isFixedSectionStreet(street) || street.properties?._imported_from) continue;
    const target = extractZoneCenterline(street);
    for (let i = 0; i < target.length - 1; i++) {
      const [ax, ay] = local(target[i]), [bx, by] = local(target[i + 1]);
      const dx = bx - ax, dy = by - ay, length = Math.hypot(dx, dy);
      if (length < 1 || Math.abs((px * dx + py * dy) / approachLength / length) > Math.sin(12 * Math.PI / 180)) continue;
      const t = -(ax * dx + ay * dy) / (length * length);
      // A through street needs space on both sides of the new junction.
      if (t * length < 12 || (1 - t) * length < 12) continue;
      const x = ax + t * dx, y = ay + t * dy;
      const distance = Math.hypot(x - px, y - py);
      // The end may touch the near kerb, but don't pull a remote route in.
      if (distance > streetSectionWidth(street) / 2 + 1 || Math.hypot(x, y) < 4
        || (x * px + y * py) <= 0 || (best && distance >= best.distance)) continue;
      best = { point: [adjacent[0] + x / lonM, adjacent[1] + y / METERS_PER_DEG_LAT], distance };
    }
  }
  return best ? line.map((p, i) => i === index ? best!.point : p) : line;
}

export function snapStreetEnds(line: number[][], zones: SiteZone[], ownerId?: string): number[][] {
  return snapStreetEndpoint(snapStreetEndpoint(line, 0, zones, ownerId), line.length - 1, zones, ownerId);
}
