import { describe, expect, it } from 'vitest';

import type { SiteZone } from '@/types';
import {
  resolveFourWayIntersectionControl,
  resolveStreetControlHierarchy,
} from './streetIntersectionControlPolicy';

function zone(properties: Record<string, unknown>): Pick<SiteZone, 'properties'> {
  return { properties } as Pick<SiteZone, 'properties'>;
}

describe('street intersection control policy', () => {
  it('keeps an all-local residential four-way intersection unsignalized', () => {
    const locals = [
      zone({ street_role: 'local', road_archetype_id: 'calgary_local', width: 22 }),
      zone({ street_role: 'residential', road_archetype_id: 'narrow_residential_street' }),
      zone({
        public_realm_lego: {
          family_id: 'street_local_public_realm',
          archetype_id: 'yield_street',
        },
      }),
    ];
    expect(locals.map(resolveStreetControlHierarchy)).toEqual(['local', 'local', 'local']);
    expect(resolveFourWayIntersectionControl(locals)).toBe('unsignalized');
  });

  it('signals a crossing connected to the executable complete-main family', () => {
    const main = zone({
      street_role: 'local',
      public_realm_lego: {
        family_id: 'street_complete_main_22m',
        archetype_id: 'main_street_complete',
      },
    });
    expect(resolveStreetControlHierarchy(main)).toBe('major');
    expect(resolveFourWayIntersectionControl([zone({ street_role: 'local' }), main]))
      .toBe('traffic_signal');
  });

  it.each([
    [{ street_role: 'collector' }, 'collector role'],
    [{ street_role: 'spine' }, 'planner spine role'],
    [{ road_class: 'Major' }, 'major functional class'],
    [{ functional_class: 'major collector' }, 'compound collector class'],
    [{ road_archetype_id: 'calgary_arterial_4lane_50' }, 'arterial archetype'],
    [{ road_archetype_id: 'collector_road' }, 'collector archetype'],
  ] as const)('treats %s as a signal warrant (%s)', (properties, _label) => {
    expect(resolveStreetControlHierarchy(zone(properties))).toBe('major');
  });

  it('is deterministic regardless of connected-zone order', () => {
    const local = zone({ street_role: 'local' });
    const main = zone({ road_archetype_id: 'main_street_complete' });
    expect(resolveFourWayIntersectionControl([local, main]))
      .toBe(resolveFourWayIntersectionControl([main, local]));
  });
});
