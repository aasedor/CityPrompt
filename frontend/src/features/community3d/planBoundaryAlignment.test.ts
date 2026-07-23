import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { analyzePlanBoundaryAlignment, planZoneFitsBoundary } from './planBoundaryAlignment';

function zone(
  id: string,
  zoneType: string,
  coordinates: number[][],
  properties: Record<string, unknown> = {},
): SiteZone {
  return {
    id,
    project_id: 'project',
    name: id,
    zone_type: zoneType,
    coordinates,
    color: '#000000',
    properties,
    sort_order: 0,
    created_at: '',
    updated_at: '',
  } as SiteZone;
}

const boundary = zone('boundary', 'site_boundary', [[0, 0], [10, 0], [10, 10], [0, 10]]);
const planProps = { _plan_scenario: 'economic', _plan_role: 'open_space' };

describe('plan boundary alignment', () => {
  it('accepts proposal geometry inside or exactly touching the boundary', () => {
    const inside = zone('inside', 'green_space', [[1, 1], [9, 1], [9, 9], [1, 9]], planProps);
    const touching = zone('touching', 'road', [[0, 4], [5, 4], [5, 5], [0, 5]], planProps);
    const result = analyzePlanBoundaryAlignment([boundary, inside, touching]);
    expect(result.isAligned).toBe(true);
    expect(result.misalignedZones).toEqual([]);
  });

  it('ignores a legacy near-duplicate closing click on the site boundary', () => {
    const legacyBoundary = zone(
      'legacy-boundary',
      'site_boundary',
      [[0, 0], [10, 0], [10, 10], [0, 10], [0.000000001, 0.000000001]],
    );
    const inside = zone('inside', 'green_space', [[1, 1], [9, 1], [9, 9], [1, 9]], planProps);

    expect(analyzePlanBoundaryAlignment([legacyBoundary, inside]).isAligned).toBe(true);
  });

  it('detects plan zones generated for a shifted older boundary', () => {
    const stalePark = zone('stale', 'green_space', [[2, 8], [8, 8], [8, 13], [2, 13]], planProps);
    const result = analyzePlanBoundaryAlignment([boundary, stalePark]);
    expect(result.isAligned).toBe(false);
    expect(result.misalignedZones.map((item) => item.id)).toEqual(['stale']);
  });

  it('rejects an edge that cuts across a concave boundary notch', () => {
    const concave = zone(
      'concave',
      'site_boundary',
      [[0, 0], [10, 0], [10, 4], [4, 4], [4, 10], [0, 10]],
    );
    const chord = zone('chord', 'road', [[2, 8], [8, 2], [7, 1], [1, 7]], planProps);
    expect(chord.coordinates.every(([x, y]) => x <= 4 || y <= 4)).toBe(true);
    expect(planZoneFitsBoundary(chord, concave)).toBe(false);
  });

  it('ignores hand-drawn and framework-only overlays', () => {
    const handDrawn = zone('manual', 'green_space', [[20, 20], [21, 20], [21, 21]], {});
    const framework = zone(
      'framework',
      'development_area',
      [[20, 20], [21, 20], [21, 21]],
      { _plan_scenario: 'economic', _plan_role: 'framework_height' },
    );
    const withBoundary = analyzePlanBoundaryAlignment([boundary, handDrawn, framework]);
    expect(withBoundary.isAligned).toBe(true);
    expect(withBoundary.requiresBoundary).toBe(false);
    const manualOnly = analyzePlanBoundaryAlignment([handDrawn]);
    expect(manualOnly.isAligned).toBe(true);
    expect(manualOnly.requiresBoundary).toBe(false);
  });

  it('requires a boundary for generated plans but not for persisted manual public realm', () => {
    const generated = zone(
      'generated-park',
      'green_space',
      [[1, 1], [9, 1], [9, 9], [1, 9]],
      planProps,
    );
    const missingBoundary = analyzePlanBoundaryAlignment([generated]);
    expect(missingBoundary.requiresBoundary).toBe(true);
    expect(missingBoundary.boundary).toBeNull();
    expect(missingBoundary.isAligned).toBe(false);

    const restoredBoundary = analyzePlanBoundaryAlignment([boundary, generated]);
    expect(restoredBoundary.requiresBoundary).toBe(true);
    expect(restoredBoundary.isAligned).toBe(true);
  });

  it('honors an explicit stale flag from future boundary edits', () => {
    const flagged = zone(
      'flagged',
      'building',
      [[1, 1], [2, 1], [2, 2], [1, 2]],
      { ...planProps, _plan_boundary_stale: true },
    );
    expect(analyzePlanBoundaryAlignment([boundary, flagged]).misalignedZones).toHaveLength(1);
  });
});
