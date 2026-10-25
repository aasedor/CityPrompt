import type { ReferenceFeature, ReferenceGeometry, ReferenceLayer } from '../referenceLayers/api';
import { zoningBounds } from '../referenceLayers/zoningLabels';
import { referenceGeometryPaths } from '../referenceLayers/referenceGeometry';
import { PUBLIC_DATASETS, type PublicDataset } from './publicDatasets';

export type PublicBounds = [number, number, number, number];
export const PUBLIC_DATA_LIMITS = { rows: 300, bytes: 2 * 1024 * 1024, vertices: 4000, layers: 4, requests: 2 } as const;
const MAX_RAW_VERTICES = 20_000;

function boundsProblem(bounds: PublicBounds | null): string | null {
  if (!bounds || !bounds.every(Number.isFinite) || bounds[0] >= bounds[2] || bounds[1] >= bounds[3]) return 'Choose a valid site or nearby map area.';
  const [w, s, e, n] = bounds;
  if (w < -114.4 || e > -113.8 || s < 50.8 || n > 51.25) return 'These public map datasets are available for the Calgary area.';
  const width = (e - w) * 111_320 * Math.cos((n + s) * Math.PI / 360), height = (n - s) * 111_320;
  return width * height > 4_000_000 || width > 4000 || height > 4000 ? 'Draw a smaller site boundary: public data is limited to a nearby area under 4 km².' : null;
}

export function publicDataBounds(coordinates: number[][]): { bounds: PublicBounds | null; problem: string | null } {
  const site = zoningBounds(coordinates);
  const problem = boundsProblem(site);
  if (problem || !site) return { bounds: null, problem };
  const latBuffer = 250 / 111_320, lonBuffer = latBuffer / Math.cos((site[1] + site[3]) * Math.PI / 360);
  const bounds = [site[0] - lonBuffer, site[1] - latBuffer, site[2] + lonBuffer, site[3] + latBuffer].map(n => Number(n.toFixed(6))) as PublicBounds;
  return { bounds, problem: boundsProblem(bounds) };
}

let active = 0;
const queue: (() => void)[] = [];
function requestSlot(signal: AbortSignal): Promise<() => void> {
  return new Promise((resolve, reject) => {
    const start = () => {
      signal.removeEventListener('abort', cancel);
      active++;
      resolve(() => { active--; queue.shift()?.(); });
    };
    const cancel = () => { const index = queue.indexOf(start); if (index >= 0) queue.splice(index, 1); reject(signal.reason); };
    if (signal.aborted) { reject(signal.reason); return; }
    if (active < PUBLIC_DATA_LIMITS.requests) start();
    else { queue.push(start); signal.addEventListener('abort', cancel, { once: true }); }
  });
}

async function readRows(response: Response, signal: AbortSignal): Promise<unknown[]> {
  const tooLarge = () => new Error('This public dataset is too large. Draw a smaller site boundary.');
  if (Number(response.headers.get('content-length')) > PUBLIC_DATA_LIMITS.bytes) { await response.body?.cancel(); throw tooLarge(); }
  const reader = response.body?.getReader();
  if (!reader) throw new Error('The public data response could not be read. Try again.');
  const decoder = new TextDecoder();
  let text = '', bytes = 0;
  try {
    while (true) {
      signal.throwIfAborted();
      const chunk = await reader.read();
      if (chunk.done) break;
      bytes += chunk.value.byteLength;
      if (bytes > PUBLIC_DATA_LIMITS.bytes) { await reader.cancel(); throw tooLarge(); }
      text += decoder.decode(chunk.value, { stream: true });
    }
    text += decoder.decode();
  } finally { reader.releaseLock(); }
  let rows: unknown;
  try { rows = JSON.parse(text); } catch { throw new Error('The public data service returned an unexpected response. Try again.'); }
  if (!Array.isArray(rows)) throw new Error('The public data service returned an unexpected response. Try again.');
  return rows;
}

type Point = [number, number];
function geometry(value: unknown): { shape: ReferenceGeometry; count: number } | null {
  if (!value || typeof value !== 'object') return null;
  const { type, coordinates } = value as { type?: string; coordinates?: unknown };
  const depth = ({ Point: 0, MultiPoint: 1, LineString: 1, MultiLineString: 2, Polygon: 2, MultiPolygon: 3 } as Record<string, number>)[type ?? ''];
  if (depth === undefined) return null;
  let count = 0;
  const valid = (node: unknown, level: number): boolean => {
    if (!Array.isArray(node) || count > MAX_RAW_VERTICES) return false;
    if (level === 0) { count++; return node.length >= 2 && node.slice(0, 2).every(Number.isFinite) && Math.abs(node[0]) <= 180 && Math.abs(node[1]) <= 90; }
    return node.length > 0 && node.every(part => valid(part, level - 1));
  };
  if (!valid(coordinates, depth) || count > MAX_RAW_VERTICES) return null;
  const shape = { type, coordinates } as ReferenceGeometry;
  // The clipping library requires closed rings of at least four positions.
  const polygons = shape.type === 'MultiPolygon' ? shape.coordinates : shape.type === 'Polygon' ? [shape.coordinates] : [];
  if (polygons.some(poly => poly.some(ring => ring.length < 4 || ring[0][0] !== ring[ring.length - 1][0] || ring[0][1] !== ring[ring.length - 1][1]))) return null;
  return { shape, count };
}

/** Liang–Barsky segment clipping keeps long utility lines inside the local window. */
function clipLine(points: number[][], [w, s, e, n]: PublicBounds): Point[][] {
  const lines: Point[][] = [];
  for (let i = 1; i < points.length; i++) {
    const [x, y] = points[i - 1], dx = points[i][0] - x, dy = points[i][1] - y;
    let lo = 0, hi = 1, valid = true;
    const ps = [-dx, dx, -dy, dy], qs = [x - w, e - x, y - s, n - y];
    for (let j = 0; j < 4; j++) {
      if (ps[j] === 0) { if (qs[j] < 0) valid = false; }
      else { const ratio = qs[j] / ps[j]; if (ps[j] < 0) lo = Math.max(lo, ratio); else hi = Math.min(hi, ratio); }
    }
    if (!valid || lo > hi) continue;
    const a: Point = [x + lo * dx, y + lo * dy], b: Point = [x + hi * dx, y + hi * dy];
    const last = lines[lines.length - 1], end = last?.[last.length - 1];
    if (last && end[0] === a[0] && end[1] === a[1]) last.push(b);
    else lines.push([a, b]);
  }
  return lines;
}

async function clip(shape: ReferenceGeometry, bounds: PublicBounds): Promise<ReferenceGeometry | null> {
  const [w, s, e, n] = bounds;
  const inside = (p: number[]) => p[0] >= w && p[0] <= e && p[1] >= s && p[1] <= n;
  if (shape.type === 'Point') return inside(shape.coordinates) ? shape : null;
  if (shape.type === 'MultiPoint') { const coordinates = shape.coordinates.filter(inside); return coordinates.length ? { type: 'MultiPoint', coordinates } : null; }
  if (shape.type === 'LineString' || shape.type === 'MultiLineString') {
    const lines = (shape.type === 'LineString' ? [shape.coordinates] : shape.coordinates) as number[][][];
    const coordinates = lines.flatMap(line => clipLine(line, bounds));
    return coordinates.length ? { type: 'MultiLineString', coordinates } : null;
  }
  if (shape.type === 'Polygon' || shape.type === 'MultiPolygon') {
    const { default: clipping } = await import('polygon-clipping');
    const polygons = shape.type === 'Polygon' ? [shape.coordinates] : shape.coordinates;
    const coordinates = clipping.intersection(polygons as Point[][][], [[[[w, s], [e, s], [e, n], [w, n], [w, s]]]]);
    return coordinates.length ? { type: 'MultiPolygon', coordinates } : null;
  }
  return null;
}

/** The shared renderer samples line segments every ten metres. Bound that
 * expanded work as well as the source vertices before mounting an overlay. */
function groundSampleCost(shape: ReferenceGeometry): number {
  const paths = referenceGeometryPaths(shape);
  let count = paths.points.length;
  for (const line of paths.lines) {
    count++;
    for (let i = 1; i < line.length; i++) {
      const a = line[i - 1], b = line[i];
      const distance = Math.hypot((b[0] - a[0]) * 111_320 * Math.cos(a[1] * Math.PI / 180), (b[1] - a[1]) * 111_320);
      count += Math.ceil(distance / 10);
      if (count > PUBLIC_DATA_LIMITS.vertices) return count;
    }
  }
  return count;
}

function properties(row: Record<string, unknown>, source: PublicDataset): Record<string, string | number | boolean> {
  const result: Record<string, string | number | boolean> = {};
  for (const [field, title] of Object.entries(source.fields)) {
    const value = row[field];
    if (typeof value === 'string') result[title] = value.slice(0, 600);
    else if (typeof value === 'number' && Number.isFinite(value) || typeof value === 'boolean') result[title] = value as number | boolean;
  }
  result.name = String(row[source.label] ?? source.name).slice(0, 160);
  return result;
}

export async function fetchPublicLayer(datasetId: string, bounds: PublicBounds, signal: AbortSignal): Promise<ReferenceLayer> {
  const source = PUBLIC_DATASETS.find(item => item.id === datasetId);
  if (!source) throw new Error('Unknown public dataset.');
  const problem = boundsProblem(bounds);
  if (problem) throw new Error(problem);
  const release = await requestSlot(signal);
  try {
    const [w, s, e, n] = bounds, year = new Date().getFullYear() - 4;
    const recent = source.recent ? ` AND ${source.recent} >= '${year}${source.recent === 'applieddate' ? '-01-01T00:00:00' : ''}'` : '';
    const query = new URLSearchParams({ '$select': [source.geometry, ...Object.keys(source.fields)].join(','),
      '$where': `intersects(${source.geometry}, 'POLYGON((${w} ${s},${e} ${s},${e} ${n},${w} ${n},${w} ${s}))')${recent}`,
      '$limit': String(PUBLIC_DATA_LIMITS.rows + 1),
      ...(source.recent ? { '$order': `${source.recent} DESC` } : {}),
    });
    const response = await fetch(`https://data.calgary.ca/resource/${source.sourceId}.json?${query}`, { signal, credentials: 'omit' });
    if (!response.ok) throw new Error(`The public data service could not load this layer (${response.status}). Try again.`);
    const rows = await readRows(response, signal), warnings: string[] = [];
    if (rows.length > PUBLIC_DATA_LIMITS.rows) warnings.push('Partial results: the nearby area exceeds the 300-row limit. Draw a smaller site boundary for more detail.');
    const features: ReferenceFeature[] = [], rolls = new Map<string, ReferenceFeature>();
    let vertices = 0, skipped = 0;
    for (const [index, raw] of rows.slice(0, PUBLIC_DATA_LIMITS.rows).entries()) {
      if (index % 20 === 0) { await new Promise(resolve => setTimeout(resolve, 0)); signal.throwIfAborted(); }
      if (!raw || typeof raw !== 'object') { skipped++; continue; }
      const row = raw as Record<string, unknown>;
      const parsed = geometry(row[source.geometry]);
      if (!parsed) { skipped++; continue; }
      if (source.id === 'assessments' && typeof row.roll_number === 'string' && rolls.has(row.roll_number)) {
        const existing = rolls.get(row.roll_number)!;
        existing.properties['Assessment history (CAD)'] += `; ${row.roll_year ?? '?'}: ${row.assessed_value ?? 'unavailable'}`;
        continue;
      }
      let clipped: ReferenceGeometry | null;
      try { clipped = await clip(parsed.shape, bounds); } catch { skipped++; continue; }
      if (!clipped) continue;
      const count = Math.max(geometry(clipped)?.count ?? Infinity, groundSampleCost(clipped));
      if (vertices + count > PUBLIC_DATA_LIMITS.vertices) { skipped++; continue; }
      vertices += count;
      const feature: ReferenceFeature = { type: 'Feature', id: `${source.id}:${index}`, geometry: clipped, properties: properties(row, source) };
      if (source.id === 'assessments') {
        feature.properties['Assessment history (CAD)'] = `${row.roll_year ?? '?'}: ${row.assessed_value ?? 'unavailable'}`;
        if (typeof row.roll_number === 'string') rolls.set(row.roll_number, feature);
      }
      features.push(feature);
    }
    signal.throwIfAborted();
    if (skipped) warnings.push(`Partial results: ${skipped} source rows were skipped because their geometry was invalid or exceeded the display budget. Choose a smaller area.`);
    if (!features.length) warnings.push('No displayable records were found in this nearby area. This does not establish that the site has no relevant features.');
    return { id: `public-data:${source.id}`, project_id: '', name: source.name, source_filename: `Calgary Open Data · ${source.sourceId}`, source_crs: 'EPSG:4326',
      source_url: `https://data.calgary.ca/d/${source.sourceId}`, description: `${source.vintage}. ${source.note}`, kind: 'reference',
      feature_collection: { type: 'FeatureCollection', features }, feature_count: features.length, bounds, warnings, color: source.color, opacity: 0.85, created_at: new Date().toISOString() };
  } finally { release(); }
}
