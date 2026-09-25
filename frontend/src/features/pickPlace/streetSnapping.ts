import type { SiteZone } from '@/types';
import { collapseStraightStreetStations, extractZoneCenterline } from '@/utils/roadGeometry';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';
import { isFixedSectionStreet, streetSectionWidth } from './streetPlacement';

/** Snap an endpoint to a through street at a supported 45–135 degree angle.
 * Keep the adjacent point fixed and reserve enough straight approach for both
 * complete street sections; a near-end connection slides gently inward.
 * Only catalogue streets participate; reference layers never become proposals. */
export function snapStreetEndpoint(line: number[][], index: number, zones: SiteZone[], ownerId?: string, incomingWidth = 16): number[][] {
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
    const target = collapseStraightStreetStations(extractZoneCenterline(street));
    for (let i = 0; i < target.length - 1; i++) {
      const [ax, ay] = local(target[i]), [bx, by] = local(target[i + 1]);
      const dx = bx - ax, dy = by - ay, length = Math.hypot(dx, dy);
      const cosine = Math.abs((px * dx + py * dy) / approachLength / length);
      if (length < 1 || cosine > Math.SQRT1_2) continue;
      const hostWidth = streetSectionWidth(street);
      const rawT = ((px - ax) * dx + (py - ay) * dy) / (length * length);
      if (rawT < 0 || rawT > 1 || Math.hypot(ax + rawT * dx - px, ay + rawT * dy - py) > hostWidth / 2 + 1) continue;
      // Near-square gestures still straighten naturally. Oblique gestures
      // retain their intended bearing instead of inventing a perpendicular arm.
      let station = (cosine <= Math.sin(12 * Math.PI / 180)
        ? -(ax * dx + ay * dy) / (length * length) : rawT) * length;
      let x = 0, y = 0, eligible = true;
      for (let pass = 0; pass < 8; pass++) {
        x = ax + station * dx / length; y = ay + station * dy / length;
        const cos = Math.abs((x * dx + y * dy) / Math.hypot(x, y) / length);
        const sin = Math.sqrt(1 - Math.min(1, cos * cos));
        if (sin < Math.SQRT1_2) { eligible = false; break; }
        const clearance = (incomingWidth / 2 + 4 + hostWidth / 2 * cos) / sin + .1;
        if (length < clearance * 2) { eligible = false; break; }
        const next = Math.max(clearance, Math.min(length - clearance, station));
        if (Math.abs(next - station) < .01) break;
        station = next;
      }
      if (!eligible) continue;
      x = ax + station * dx / length; y = ay + station * dy / length;
      const distance = Math.hypot(x - px, y - py);
      // The end may touch the near kerb, but don't pull a remote route in.
      if (distance > hostWidth / 2 + incomingWidth / 2 || Math.hypot(x, y) < hostWidth / 2 + 4
        || (x * px + y * py) <= 0 || (best && distance >= best.distance)) continue;
      best = { point: [adjacent[0] + x / lonM, adjacent[1] + y / METERS_PER_DEG_LAT], distance };
    }
  }
  return best ? line.map((p, i) => i === index ? best!.point : p) : line;
}

export function snapStreetEnds(line: number[][], zones: SiteZone[], ownerId?: string, incomingWidth = 16): number[][] {
  return snapStreetEndpoint(snapStreetEndpoint(line, 0, zones, ownerId, incomingWidth), line.length - 1, zones, ownerId, incomingWidth);
}
