import booleanPointInPolygon from '@turf/boolean-point-in-polygon';
import type { MultiPolygon } from 'polygon-clipping';

export const ZONING_SOURCE = 'https://data.calgary.ca/Base-Maps/Land-Use-Districts/qe6k-p9nh';
export const ZONING_LIMIT = 1500;
export type Position = [number, number];
export type ZoningLabel = { id: string; label: string; description?: string; anchor: Position; polygon: Position[][] };
export type ZoningOverlay = { districts: ZoningLabel[]; bounds: [number, number, number, number]; loadedAt: string };

export function zoningBounds(coordinates: number[][]): ZoningOverlay['bounds'] | null {
  if (coordinates.length < 3 || coordinates.some(p => p.length < 2 || !p.slice(0, 2).every(Number.isFinite))) return null;
  const bounds: ZoningOverlay['bounds'] = [Infinity, Infinity, -Infinity, -Infinity];
  for (const [x, y] of coordinates) {
    bounds[0] = Math.min(bounds[0], x); bounds[1] = Math.min(bounds[1], y);
    bounds[2] = Math.max(bounds[2], x); bounds[3] = Math.max(bounds[3], y);
  }
  return bounds;
}

export function zoningCoverageProblem(bounds: ZoningOverlay['bounds'] | null): string | null {
  if (!bounds) return 'Draw a site boundary to view zoning.';
  const [w, s, e, n] = bounds;
  if (!bounds.every(Number.isFinite) || e <= w || n <= s) return 'Draw a valid site boundary to view zoning.';
  if (w < -114.35 || e > -113.85 || s < 50.8 || n > 51.22) return 'Zoning data is currently available for Calgary sites.';
  if ((e - w) * (n - s) * 111320 ** 2 * Math.cos((n + s) / 2 * Math.PI / 180) > 25_000_000) return 'Choose a site smaller than 25 km² to view zoning detail.';
  return null;
}

/** Scanline interior point: stays inside concave districts and outside holes. */
export function zoningAnchor(polygon: Position[][]): Position | null {
  const bounds = zoningBounds(polygon[0] ?? []);
  if (!bounds) return null;
  const [, s, , n] = bounds;
  let best: { width: number; point: Position } | null = null;
  for (const fraction of [0.5, 0.25, 0.75, 0.125, 0.875]) {
    const y = s + (n - s) * fraction;
    const cuts: number[] = [];
    for (const ring of polygon) for (let i = 0; i < ring.length - 1; i++) {
      const a = ring[i], b = ring[i + 1];
      if ((a[1] > y) !== (b[1] > y)) cuts.push(a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]));
    }
    cuts.sort((a, b) => a - b);
    for (let i = 0; i + 1 < cuts.length; i += 2) {
      const width = cuts[i + 1] - cuts[i];
      const point: Position = [(cuts[i] + cuts[i + 1]) / 2, y];
      if (width > (best?.width ?? 0) && booleanPointInPolygon(point, { type: 'Polygon', coordinates: polygon })) best = { width, point };
    }
  }
  return best?.point ?? null;
}

/** Validate before clipping so bad remote geometry cannot break the viewer. */
function validDistrict(value: unknown): value is { type: 'MultiPolygon'; coordinates: MultiPolygon } {
  if (!value || typeof value !== 'object') return false;
  const geometry = value as { type?: unknown; coordinates?: unknown };
  return geometry.type === 'MultiPolygon' && Array.isArray(geometry.coordinates) && geometry.coordinates.length > 0
    && geometry.coordinates.every(poly => Array.isArray(poly) && poly.length > 0 && poly.every(ring =>
      Array.isArray(ring) && ring.length >= 4 && ring.every(p => Array.isArray(p) && p.length >= 2
        && Number.isFinite(p[0]) && Number.isFinite(p[1]) && Math.abs(p[0]) <= 180 && Math.abs(p[1]) <= 90)
      && ring[0][0] === ring[ring.length - 1][0] && ring[0][1] === ring[ring.length - 1][1]));
}

/** Label each district piece inside the actual site, including disjoint areas and holes. */
export async function districtLabels(rows: unknown[], coordinates: number[][], signal?: AbortSignal): Promise<ZoningLabel[]> {
  const { default: clipping } = await import('polygon-clipping');
  const site = coordinates.map(p => [p[0], p[1]] as Position);
  if (site.length < 3) return [];
  if (site[0][0] !== site[site.length - 1][0] || site[0][1] !== site[site.length - 1][1]) site.push([...site[0]]);
  const result: ZoningLabel[] = [];
  for (let i = 0; i < rows.length; i++) {
    if (i % 50 === 0) { await new Promise(resolve => setTimeout(resolve, 0)); signal?.throwIfAborted(); }
    const raw = rows[i];
    if (!raw || typeof raw !== 'object') throw new Error('Calgary returned incomplete zoning data. Try again.');
    const row = raw as Record<string, unknown>;
    if (!validDistrict(row.multipolygon)) throw new Error('Calgary returned district geometry that could not be displayed.');
    const label = [row.label, row.lu_code].find(value => typeof value === 'string' && value.trim()) as string | undefined;
    if (!label) throw new Error('Calgary returned a district without a zoning code.');
    const description = typeof row.description === 'string' ? row.description.trim().slice(0, 300) || undefined : undefined;
    const pieces = clipping.intersection(row.multipolygon.coordinates, [site]);
    for (let j = 0; j < pieces.length; j++) {
      const anchor = zoningAnchor(pieces[j]);
      if (anchor) result.push({ id: `district-${i}-${j}`, label: label.trim().slice(0, 120), description, anchor, polygon: pieces[j] });
      if (result.length > ZONING_LIMIT) throw new Error('This site contains too many zoning areas. Use a smaller boundary.');
    }
  }
  return result;
}

export async function fetchZoningLabels(coordinates: number[][], signal: AbortSignal): Promise<ZoningOverlay> {
  const bounds = zoningBounds(coordinates);
  const problem = zoningCoverageProblem(bounds);
  if (problem || !bounds) throw new Error(problem ?? 'Draw a valid site boundary.');
  const [w, s, e, n] = bounds;
  const query = new URLSearchParams({ '$select': 'multipolygon,label,lu_code,description',
    '$where': `intersects(multipolygon, 'POLYGON((${w} ${s},${e} ${s},${e} ${n},${w} ${n},${w} ${s}))')`, '$limit': String(ZONING_LIMIT + 1) });
  const response = await fetch(`https://data.calgary.ca/resource/qe6k-p9nh.json?${query}`, { signal });
  if (!response.ok) throw new Error('Calgary land-use districts could not load. Try again.');
  const rows: unknown = await response.json();
  if (!Array.isArray(rows)) throw new Error('Calgary returned an unexpected land-use response.');
  if (rows.length > ZONING_LIMIT) throw new Error('This site contains too many districts. Use a smaller boundary to see complete detail.');
  if (!rows.length) throw new Error('No Calgary zoning is published for this site. Check whether it is outside Calgary city limits.');
  const districts = await districtLabels(rows, coordinates, signal);
  return { districts, bounds, loadedAt: new Date().toISOString() };
}
