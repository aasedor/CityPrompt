import { describe, expect, it } from 'vitest';

import buildingCatalog from '@/data/buildingArchetypes.json';
import type { SiteZone } from '@/types';

import { withPlanArchetypeDefaults } from './resolvePlanZoneArchetypes';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const BUILDINGS = ((buildingCatalog as any).archetypes ?? buildingCatalog) as any[];

// ~200m x 160m block near the Beltline — big enough to not be a pocket park.
const BLOCK_COORDS = [
  [-114.085, 51.0405],
  [-114.0821, 51.0405],
  [-114.0821, 51.0419],
  [-114.085, 51.0419],
];

// ~30m x 30m — under the pocket-park threshold.
const TINY_COORDS = [
  [-114.085, 51.0405],
  [-114.08457, 51.0405],
  [-114.08457, 51.04077],
  [-114.085, 51.04077],
];

let zoneCounter = 0;
function planZone(
  zoneType: string,
  role: string,
  properties: Record<string, unknown> = {},
  coordinates: number[][] = BLOCK_COORDS,
): SiteZone {
  zoneCounter += 1;
  return {
    id: `zone-${zoneCounter}`,
    project_id: 'p1',
    zone_type: zoneType,
    coordinates,
    color: '#ff0000',
    sort_order: 0,
    created_at: '',
    updated_at: '',
    properties: { _plan_scenario: 'climate_first', _plan_role: role, ...properties },
  } as unknown as SiteZone;
}

describe('withPlanArchetypeDefaults', () => {
  it('is deterministic: same inputs resolve to the same archetype', () => {
    const make = () =>
      planZone('building', 'building', {
        development_type: 'mixed_use',
        development_aesthetic: 'contemporary',
        floors: 6,
      });
    const [a] = withPlanArchetypeDefaults([make()]);
    const [b] = withPlanArchetypeDefaults([make()]);
    expect(a.properties?.development_archetype_id).toBeTruthy();
    expect(a.properties?.development_archetype_id).toBe(b.properties?.development_archetype_id);
    expect(a.properties?.development_selected_variant_id).toBe(
      b.properties?.development_selected_variant_id,
    );
  });

  it('respects the catalog floor range for the drawn storeys', () => {
    const [zone] = withPlanArchetypeDefaults([
      planZone('building', 'building', { development_type: 'mixed_use', floors: 6 }),
    ]);
    const id = zone.properties?.development_archetype_id as string;
    const entry = BUILDINGS.find((e) => e.id === id);
    expect(entry).toBeTruthy();
    expect(entry.minFloors ?? 1).toBeLessThanOrEqual(6);
    expect(entry.maxFloors ?? 999).toBeGreaterThanOrEqual(6);
  });

  it('falls back to a family match for a loose development_type hint', () => {
    const [zone] = withPlanArchetypeDefaults([
      planZone('building', 'building', { development_type: 'residential', floors: 5 }),
    ]);
    const id = zone.properties?.development_archetype_id as string;
    expect(id).toBeTruthy();
    const entry = BUILDINGS.find((e) => e.id === id);
    expect(String(entry.developmentType)).toMatch(/^residential/);
  });

  it('maps parks by size: block park vs pocket park', () => {
    const [big] = withPlanArchetypeDefaults([planZone('green_space', 'open_space')]);
    const [tiny] = withPlanArchetypeDefaults([
      planZone('green_space', 'open_space', {}, TINY_COORDS),
    ]);
    expect(big.properties?.green_space_archetype_id).toBe('neighborhood_park');
    expect(tiny.properties?.green_space_archetype_id).toBe('urban_pocket_park');
  });

  it('maps streets by right-of-way width band', () => {
    const cases: Array<[number, string]> = [
      [8, 'yield_street'],
      [12, 'narrow_residential_street'],
      [16, 'collector_road'],
      [26, 'main_street_complete'],
    ];
    for (const [width, expected] of cases) {
      const [zone] = withPlanArchetypeDefaults([planZone('road', 'street', { width })]);
      expect(zone.properties?.road_archetype_id).toBe(expected);
    }
  });

  it('skips framework-height zones entirely', () => {
    const [zone] = withPlanArchetypeDefaults([
      planZone('development_area', 'framework_height', { max_floors: 6 }),
    ]);
    expect(zone.properties?.development_archetype_id).toBeUndefined();
    expect(zone.properties?._plan_archetype_resolved).toBeUndefined();
  });

  it('never overrides an explicit archetype ID or custom style', () => {
    const [explicit] = withPlanArchetypeDefaults([
      planZone('building', 'building', {
        development_type: 'mixed_use',
        floors: 6,
        development_archetype_id: 'user_choice',
      }),
    ]);
    expect(explicit.properties?.development_archetype_id).toBe('user_choice');
    expect(explicit.properties?._plan_archetype_resolved).toBeUndefined();

    const [custom] = withPlanArchetypeDefaults([
      planZone('building', 'building', {
        development_type: 'mixed_use',
        floors: 6,
        custom_style_enabled: true,
      }),
    ]);
    expect(custom.properties?.development_archetype_id).toBeUndefined();
  });

  it('leaves hand-drawn (non-plan) zones untouched', () => {
    const zone = planZone('building', 'building');
    delete (zone.properties as Record<string, unknown>)._plan_role;
    const [result] = withPlanArchetypeDefaults([zone]);
    expect(result).toBe(zone);
  });
});
