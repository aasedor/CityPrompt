import type { SiteZone } from '@/types';
import type { SiteAssessment } from './SiteAssessmentPanel';
import { zoningAnchor, zoningBounds, type ZoningOverlay, type Position } from './zoningLabels';

export const assessmentDollars = new Intl.NumberFormat('en-CA', { style: 'currency', currency: 'CAD', maximumFractionDigits: 0 });

export function assessmentMapOverlay(boundary: SiteZone | null | undefined, data: SiteAssessment | undefined): ZoningOverlay | undefined {
  if (!boundary || !data || data.boundary_id !== boundary.id || !data.property_count || data.missing_value_count >= data.property_count) return undefined;
  const ring: Position[] = boundary.coordinates.map(([lng, lat]) => [lng, lat]);
  if (ring.length < 3) return undefined;
  if (ring[0][0] !== ring[ring.length - 1][0] || ring[0][1] !== ring[ring.length - 1][1]) ring.push([...ring[0]]);
  const bounds = zoningBounds(ring), anchor = zoningAnchor([ring]);
  if (!bounds || !anchor) return undefined;
  const partial = data.partial_property_count > 0;
  const value = partial ? data.area_weighted_estimate : data.full_property_assessed_total;
  if (!Number.isFinite(value)) return undefined;
  const description = !data.complete ? (partial ? 'Incomplete prorated estimate' : 'Incomplete subtotal')
    : partial ? 'Prorated site estimate' : 'Assessed site value';
  return { bounds, loadedAt: data.fetched_at, districts: [{ id: `assessment:${boundary.id}`,
    label: `${assessmentDollars.format(value)} / ${description}${data.roll_year ? ` · ${data.roll_year}` : ''}`,
    anchor, polygon: [ring] }] };
}
