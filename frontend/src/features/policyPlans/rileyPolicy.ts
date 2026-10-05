import clipping from 'polygon-clipping';
import { zoningAnchor, zoningBounds, type Position, type ZoningOverlay } from '@/features/referenceLayers/zoningLabels';

export const RILEY_SOURCE = 'https://www.calgary.ca/content/dam/www/pda/pd/publishingimages/riley-communities-local-area-plan/Riley-Communities-Local-Area-Plan.pdf#page=24';
export const RILEY_BOUNDS = [-114.12874, 51.04701, -114.06241, 51.06699] as const;
export type PolicyFeature = { type: 'Feature'; id: string; properties: { category: string; color: string }; geometry: { type: 'Polygon'; coordinates: Position[][] } };
export type PolicySnapshot = { snapshot: string; bounds: ZoningOverlay['bounds']; boundary: PolicyFeature['geometry']; features: PolicyFeature[] };
export type PolicyPreferences = { enabled: boolean; opacity: number; clipToSite: boolean };

export function readPolicyPreferences(raw: string | null): PolicyPreferences {
  const defaults = { enabled: false, opacity: 0.7, clipToSite: false };
  try {
    const value: unknown = JSON.parse(raw ?? 'null');
    if (!value || typeof value !== 'object') return defaults;
    const saved = value as Record<string, unknown>;
    return { enabled: saved.enabled === true, clipToSite: saved.clipToSite === true,
      opacity: typeof saved.opacity === 'number' && Number.isFinite(saved.opacity) ? Math.max(0, Math.min(1, saved.opacity)) : defaults.opacity };
  } catch { return defaults; }
}

export function policyCoverageProblem(coordinates: number[][]): string | null {
  const bounds = zoningBounds(coordinates);
  if (!bounds) return 'Draw a site boundary to explore the local area plan.';
  const [w, s, e, n] = bounds;
  if (w >= e || s >= n) return 'Draw a valid site boundary to explore the local area plan.';
  if (e < RILEY_BOUNDS[0] || w > RILEY_BOUNDS[2] || n < RILEY_BOUNDS[1] || s > RILEY_BOUNDS[3]) {
    return 'This pilot covers Riley: Hillhurst, West Hillhurst, Sunnyside and Hounsfield Heights–Briar Hill.';
  }
  return null;
}

export async function loadRileyPolicy(): Promise<PolicySnapshot> {
  // Separate cached chunk: no PDF processing or City API call on student laptops.
  const { default: snapshot } = await import('./data/rileyUrbanForm.json');
  // JSON imports widen tuple/literal types. Snapshot geometry is checked by the
  // extractor and the committed-data regression tests, not supplied by users.
  return snapshot as unknown as PolicySnapshot;
}

export function selectPolicySite(snapshot: PolicySnapshot, coordinates: number[][]) {
  const ring = coordinates.map(([x, y]) => [x, y] as Position);
  if (ring.length < 3) throw new Error('Draw a site boundary first.');
  if (ring[0][0] !== ring[ring.length - 1][0] || ring[0][1] !== ring[ring.length - 1][1]) ring.push([...ring[0]]);
  const site = [ring];
  const coverage = clipping.intersection(snapshot.boundary.coordinates, site);
  const features = snapshot.features.flatMap(feature => clipping.intersection(feature.geometry.coordinates, site).map((polygon, index) => ({
    ...feature, id: `${feature.id}-site-${index}`, geometry: { type: 'Polygon' as const, coordinates: polygon },
  })));
  return { features, hasCoverage: coverage.length > 0,
    partial: coverage.length > 0 && clipping.difference(site, snapshot.boundary.coordinates).length > 0 };
}

export function policyOverlay(snapshot: PolicySnapshot, features: PolicyFeature[]): ZoningOverlay {
  return { bounds: snapshot.bounds, loadedAt: new Date().toISOString(), districts: features.flatMap(feature => {
    const anchor = zoningAnchor(feature.geometry.coordinates);
    return anchor ? [{ id: feature.id, label: feature.properties.category, color: feature.properties.color,
      anchor, polygon: feature.geometry.coordinates }] : [];
  }) };
}
