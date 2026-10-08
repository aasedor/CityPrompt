import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import type { SiteAssessment } from './SiteAssessmentPanel';
import { assessmentMapOverlay } from './assessmentMapLabel';

const boundary = { id: 'site', coordinates: [[-114.12, 51.01], [-114.119, 51.01], [-114.119, 51.011], [-114.12, 51.011]] } as SiteZone;
const result = { boundary_id: 'site', roll_year: 2026, property_count: 2, partial_property_count: 0,
  missing_value_count: 0, complete: true, full_property_assessed_total: 500000, area_weighted_estimate: 350000,
  fetched_at: '2026-10-08' } as SiteAssessment;
describe('assessment value on the property', () => {
  it('puts the assessed dollar total inside the boundary with its assessment year', () => {
    const overlay = assessmentMapOverlay(boundary, result)!;
    expect(overlay.districts[0].label).toBe('$500,000 / Assessed site value · 2026');
    expect(overlay.districts[0].anchor[0]).toBeGreaterThan(-114.12);
    expect(overlay.districts[0].anchor[0]).toBeLessThan(-114.119);
  });
  it('uses the within-boundary estimate for partial parcels, and flags incomplete values', () => {
    expect(assessmentMapOverlay(boundary, { ...result, partial_property_count: 1 })!.districts[0].label)
      .toBe('$350,000 / Prorated site estimate · 2026');
    expect(assessmentMapOverlay(boundary, { ...result, complete: false })!.districts[0].label).toContain('Incomplete subtotal');
  });
  it('never displays an unrelated, empty or entirely missing assessment as a site value', () => {
    expect(assessmentMapOverlay(undefined, result)).toBeUndefined();
    expect(assessmentMapOverlay({ ...boundary, id: 'other' }, result)).toBeUndefined();
    expect(assessmentMapOverlay(boundary, { ...result, property_count: 0 })).toBeUndefined();
    expect(assessmentMapOverlay(boundary, { ...result, missing_value_count: 2 })).toBeUndefined();
  });
});
