import booleanPointInPolygon from '@turf/boolean-point-in-polygon';
import { fetchParcelFabric, PARCEL_FABRIC_SOURCE, polygonArea } from './calgaryParcelFabric';
import type { ReferenceFeature, ReferenceLayer } from './api';

export const PARCEL_SOURCE = PARCEL_FABRIC_SOURCE;
export const ZONING_SOURCE = 'https://data.calgary.ca/Base-Maps/Land-Use-Districts/qe6k-p9nh';
export const PARCEL_LIMIT = 1500;
type Position = [number, number];
export type Parcel = { id: string; geometry: { type: 'MultiPolygon'; coordinates: Position[][][] }; label: string; anchor: Position; year: string };
export type ParcelOverlay = { parcels: Parcel[]; bounds: [number, number, number, number]; loadedAt: string };

export function parcelBounds(coordinates: number[][]): ParcelOverlay['bounds'] | null {
  if (coordinates.length < 3 || coordinates.some(p => p.length < 2 || !p.slice(0, 2).every(Number.isFinite))) return null;
  const bounds: ParcelOverlay['bounds'] = [Infinity, Infinity, -Infinity, -Infinity];
  for (const [x, y] of coordinates) {
    bounds[0] = Math.min(bounds[0], x); bounds[1] = Math.min(bounds[1], y);
    bounds[2] = Math.max(bounds[2], x); bounds[3] = Math.max(bounds[3], y);
  }
  return bounds;
}

export function parcelCoverageProblem(bounds: ParcelOverlay['bounds'] | null): string | null {
  if (!bounds) return 'Draw a site boundary to view parcels.';
  const [w, s, e, n] = bounds;
  if (!bounds.every(Number.isFinite) || e <= w || n <= s) return 'Draw a valid site boundary to view parcels.';
  if (w < -114.35 || e > -113.85 || s < 50.8 || n > 51.22) return 'Parcel data is currently available for Calgary sites.';
  if ((e - w) * (n - s) * 111320 ** 2 * Math.cos((n + s) / 2 * Math.PI / 180) > 25_000_000) return 'Choose a site smaller than 25 km² to view parcel detail.';
  return null;
}

/** Scanline interior point: stays inside concave parcels and outside holes. */
export function parcelAnchor(polygon: Position[][]): Position | null {
  const bounds = parcelBounds(polygon[0] ?? []);
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

export function normalizeParcels(rows: unknown[]): Parcel[] {
  const parcels = new Map<string, Parcel>();
  for (const raw of rows) {
    if (!raw || typeof raw !== 'object') continue;
    const row = raw as Record<string, unknown>;
    const geometry = row.multipolygon as Parcel['geometry'] | undefined;
    if (!geometry || geometry.type !== 'MultiPolygon' || !Array.isArray(geometry.coordinates) || !geometry.coordinates.length) continue;
    const valid = geometry.coordinates.every(poly => Array.isArray(poly) && poly.length && poly.every(ring => Array.isArray(ring) && ring.length >= 4 && ring.every(p => Array.isArray(p) && p.length >= 2 && Number.isFinite(p[0]) && Number.isFinite(p[1]) && Math.abs(p[0]) <= 180 && Math.abs(p[1]) <= 90) && ring[0][0] === ring[ring.length - 1][0] && ring[0][1] === ring[ring.length - 1][1]));
    if (!valid) continue;
    const anchor = geometry.coordinates.map(parcelAnchor).find(p => p !== null);
    if (!anchor) continue;
    const id = String(row.cpid ?? JSON.stringify(geometry.coordinates));
    const label = typeof row.land_use_designation === 'string' && row.land_use_designation.trim() ? row.land_use_designation.trim().slice(0, 120) : 'Unknown';
    const existing = parcels.get(id);
    if (existing) {
      existing.label = [...new Set([...existing.label.split(','), ...label.split(',')])].join(',');
    } else parcels.set(id, { id, geometry, label, anchor, year: String(row.roll_year ?? '') });
  }
  return [...parcels.values()];
}

export async function fetchParcelZoning(bounds: ParcelOverlay['bounds'], signal: AbortSignal): Promise<ParcelOverlay> {
  const problem = parcelCoverageProblem(bounds);
  if (problem) throw new Error(problem);
  const [w, s, e, n] = bounds;
  const query = new URLSearchParams({ '$select': 'multipolygon,label,lu_code',
    '$where': `intersects(multipolygon, 'POLYGON((${w} ${s},${e} ${s},${e} ${n},${w} ${n},${w} ${s}))')`, '$limit': String(PARCEL_LIMIT + 1) });
  const [fabric, response] = await Promise.all([
    fetchParcelFabric(bounds, signal),
    fetch(`https://data.calgary.ca/resource/qe6k-p9nh.json?${query}`, { signal }),
  ]);
  if (!response.ok) throw new Error('Calgary land-use districts could not load. Try again.');
  const districts: unknown = await response.json();
  if (!Array.isArray(districts)) throw new Error('Calgary returned an unexpected land-use response.');
  if (districts.length > PARCEL_LIMIT) throw new Error('This site contains too many districts. Use a smaller boundary to see complete detail.');
  if (!districts.length) throw new Error('No Calgary zoning is published for this site. Check whether it is outside Calgary city limits.');
  let parcels = normalizeParcels(fabric.map((coordinates, i) => ({ cpid: `fabric-${i}`, multipolygon: { type: 'MultiPolygon', coordinates } })));
  parcels = await labelParcels(parcels, districts, signal);

  return { parcels, bounds, loadedAt: new Date().toISOString() };
}

export function parcelReferenceLayer(data: ParcelOverlay): ReferenceLayer {
  const features: ReferenceFeature[] = data.parcels.map(p => ({ type: 'Feature', id: p.id, geometry: p.geometry, properties: { label: p.label } }));
  return { id: 'parcel-zoning-overlay', project_id: '', name: 'Calgary parcels', kind: 'zoning', source_filename: '', source_crs: 'WGS84', source_url: PARCEL_SOURCE, description: null, feature_collection: { type: 'FeatureCollection', features }, feature_count: features.length, bounds: data.bounds, warnings: [], color: '#fef08a', opacity: 0.95, created_at: data.loadedAt };
}

/** Join by actual polygon area, preserving split zoning and ignoring boundary-only contact. */
export async function labelParcels(parcels: Parcel[], rows: unknown[], signal?: AbortSignal): Promise<Parcel[]> {
  const { default: clipping } = await import('polygon-clipping');
  const districts = normalizeParcels(rows.map((raw, i) => {
    const row = (raw && typeof raw === 'object' ? raw : {}) as Record<string, unknown>;
    return { ...row, cpid: String(i), land_use_designation: row.label || row.lu_code };
  })).map(d => ({ ...d, bounds: parcelBounds(d.geometry.coordinates.flatMap(poly => poly[0]))! }));
  if (rows.length && !districts.length) throw new Error('Calgary returned land-use geometry that could not be displayed.');
  const result: Parcel[] = [];
  for (let i = 0; i < parcels.length; i++) {
    if (i % 50 === 0) { await new Promise(resolve => setTimeout(resolve, 0)); signal?.throwIfAborted(); }
    const parcel = parcels[i];
    const bounds = parcelBounds(parcel.geometry.coordinates.flatMap(poly => poly[0]))!;
    const labels = new Set<string>();
    for (const district of districts) {
      const b = district.bounds;
      if (b[2] <= bounds[0] || b[0] >= bounds[2] || b[3] <= bounds[1] || b[1] >= bounds[3]) continue;
      const overlap = clipping.intersection(parcel.geometry.coordinates, district.geometry.coordinates);
      // Quarter-square-metre tolerance suppresses survey digitization slivers.
      const area = polygonArea(overlap) * 111320 ** 2 * Math.cos(parcel.anchor[1] * Math.PI / 180);
      if (area > 0.25) labels.add(district.label);
    }
    result.push({ ...parcel, label: labels.size ? [...labels].sort().join(' / ') : 'Unknown' });
  }
  return result;
}
