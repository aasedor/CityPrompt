import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import {
  buildPrompt,
  MAX_DETAILED_RENDER_PROMPT_ZONES,
  MAX_DISTRICT_RENDER_GROUP_LINES,
} from './useGlobeAIRender';

function square(index: number): number[][] {
  const lng = -114 + (index % 20) * 0.0002;
  const lat = 51 + Math.floor(index / 20) * 0.0002;
  return [
    [lng, lat],
    [lng + 0.0001, lat],
    [lng + 0.0001, lat + 0.0001],
    [lng, lat + 0.0001],
  ];
}

function building(index: number): SiteZone {
  return {
    id: `building-${index}`,
    project_id: 'project-1',
    zone_type: 'building',
    coordinates: square(index),
    color: '#aa6633',
    properties: {
      _plan_role: 'building',
      development_archetype_id: 'contemporary_midrise_residential',
      floors: 6,
      height_m: 21,
    },
    sort_order: index,
    created_at: '2026-07-18T00:00:00Z',
    updated_at: '2026-07-18T00:00:00Z',
  };
}

function park(index: number): SiteZone {
  return {
    id: `park-${index}`,
    project_id: 'project-1',
    zone_type: 'green_space',
    coordinates: square(1000 + index),
    color: '#4caf50',
    properties: {
      _plan_role: 'open_space',
      green_space_archetype_id: 'neighborhood_park',
    },
    sort_order: index,
    created_at: '2026-07-18T00:00:00Z',
    updated_at: '2026-07-18T00:00:00Z',
  };
}

function uniquelyNamedGround(index: number): SiteZone {
  return {
    id: `unique-ground-${index}`,
    project_id: 'project-1',
    name: `Unique program ${index}`,
    zone_type: 'water',
    coordinates: square(2000 + index),
    color: '#3f7ca8',
    properties: {},
    sort_order: index,
    created_at: '2026-07-18T00:00:00Z',
    updated_at: '2026-07-18T00:00:00Z',
  };
}

function exactFamilyBuilding(index: number, archetypeId: string): SiteZone {
  const candidate = building(index);
  return {
    ...candidate,
    id: `exact-${archetypeId}`,
    name: archetypeId,
    properties: {
      ...candidate.properties,
      development_archetype_id: archetypeId,
    },
  };
}

function compiledReservoirPark(index: number): SiteZone {
  const candidate = park(index);
  return {
    ...candidate,
    name: 'Reservoir / Watershed Park',
    properties: {
      ...candidate.properties,
      green_space_archetype_id: 'reservoir_watershed_park',
      park_design_structure: 'reservoir_perimeter',
      community_3d: {
        schema_version: 1,
        state: 'compiled',
        kind: 'park',
        generator: 'park_kit',
        compiled_at: '2026-07-18T01:00:00Z',
      },
    },
  };
}

function compiledBotanicalPark(index: number): SiteZone {
  const candidate = park(index);
  return {
    ...candidate,
    name: 'Botanical Garden',
    properties: {
      ...candidate.properties,
      green_space_archetype_id: 'botanical_garden',
      community_3d: {
        schema_version: 1,
        state: 'compiled',
        kind: 'park',
        generator: 'park_kit',
        compiled_at: '2026-07-18T01:00:00Z',
      },
    },
  };
}

describe('globe render prompt scale', () => {
  it('keeps the detailed per-zone schema for small scenes', () => {
    const prompt = buildPrompt([building(1), park(1)], 'photorealistic');
    expect(prompt).toContain('NUMERICAL INVENTORY: This scene contains exactly 2 zones');
    expect(prompt).toContain('ZONES:\n');
    expect(prompt).not.toContain('DISTRICT ZONE GROUPS');
  });

  it('groups repeated programs for district scenes without losing exact inventory', () => {
    const buildings = Array.from({ length: 90 }, (_, index) => building(index));
    const parks = Array.from({ length: 20 }, (_, index) => park(index));
    const prompt = buildPrompt([...buildings, ...parks], 'photorealistic');

    expect(110).toBeGreaterThan(MAX_DETAILED_RENDER_PROMPT_ZONES);
    expect(prompt).toContain('NUMERICAL INVENTORY: This scene contains exactly 110 zones: 90 buildings, 20 park/plazas, 0 street/paths.');
    expect(prompt).toContain('DISTRICT ZONE GROUPS (2 archetype/program groups summarized in 2 bounded lines; all 110 individual polygons remain authoritative');
    expect(prompt).toContain('90 building zones');
    expect(prompt).toContain('20 park zones');
    expect(prompt).toContain('does not merge, relocate, omit or enlarge polygons');
    expect(prompt.length).toBeLessThan(20_000);
  });

  it('hard-caps uniquely named district groups and preserves an overflow inventory', () => {
    const uniqueZones = Array.from({ length: 100 }, (_, index) => uniquelyNamedGround(index));
    const prompt = buildPrompt(uniqueZones, 'photorealistic');

    expect(MAX_DISTRICT_RENDER_GROUP_LINES).toBe(32);
    expect(prompt).toContain('100 archetype/program groups summarized in 32 bounded lines');
    expect(prompt).toContain('additional program groups covering');
    expect(prompt).toContain('Follow the representative on-image labels, group-consistent fills and exact mask/3D geometry');
    expect(prompt).toContain('Representative text labels identify each program group');
    expect(prompt.length).toBeLessThan(50_000);
  });

  it('keeps the four required mixed-district building identities distinct in the render handoff', () => {
    const prompt = buildPrompt([
      exactFamilyBuilding(1, 'vernacular_courtyard_housing'),
      exactFamilyBuilding(2, 'new_york_walk_up_tenement'),
      exactFamilyBuilding(3, 'new_york_corner_bodega'),
      exactFamilyBuilding(4, 'contemporary_civic'),
    ], 'photorealistic');

    expect(prompt).toContain('Vernacular Courtyard Housing');
    expect(prompt).toContain('New York Walk-Up Tenement');
    expect(prompt).toContain('New York Corner Bodega');
    expect(prompt).toContain('Contemporary Civic');
    expect(prompt).toContain('internal gardens');
    expect(prompt).toContain('cast-iron fire escapes');
    expect(prompt).toContain('corrugated metal awning');
    expect(prompt).toContain('glass curtain wall');
  });

  it('preserves fixed park geometry while leaving planting and furniture to Render', () => {
    const prompt = buildPrompt([compiledReservoirPark(1)], 'photorealistic');

    expect(prompt).toContain('PARK TOPOLOGY LOCK');
    expect(prompt).toContain('Park and street trees, benches and other furniture may be intentionally absent');
    expect(prompt).toContain('eligible dry planting/furnishing areas');
    expect(prompt).toContain('circulation, crossing, sightline and water setbacks');
    expect(prompt).not.toContain('preserve its exact tree positions');
    expect(prompt).not.toContain('vegetation already visible in the screenshot is authoritative');
  });

  it('puts botanical topology ahead of mature-planting prose and forbids invented water', () => {
    const prompt = buildPrompt([compiledBotanicalPark(2)], 'photorealistic');
    const topologyIndex = prompt.indexOf('PARK TOPOLOGY LOCK');
    const realismIndex = prompt.indexOf('MATURE PARK REALISM');

    expect(topologyIndex).toBeGreaterThan(-1);
    expect(realismIndex).toBeGreaterThan(topologyIndex);
    expect(prompt).toContain('continuous 2.8-metre interpretive path');
    expect(prompt).toContain('three distinct collection-bed rooms');
    expect(prompt).toContain('Do not enlarge or relocate the conservatory pad');
    expect(prompt).toContain('invent a fountain, pond, central axis, parterre');
  });
});
