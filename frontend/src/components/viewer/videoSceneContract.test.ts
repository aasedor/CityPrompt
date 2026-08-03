import { describe, expect, it } from 'vitest';

import type { SiteZone } from '@/types';
import { buildVideoSceneContract } from './videoSceneContract';

function zone(id: string, zone_type: SiteZone['zone_type'], properties: Record<string, unknown>): SiteZone {
  return {
    id,
    project_id: 'project',
    zone_type,
    coordinates: [],
    color: '#fff',
    properties,
    sort_order: 0,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  };
}

describe('buildVideoSceneContract', () => {
  it('binds each authored archetype to its exact massing and reference', () => {
    const contract = buildVideoSceneContract([
      zone('b1', 'building', {
        floors: 6,
        height: 18,
        development_archetype_id: 'custom_midrise_variant_0',
        development_archetype_image: '/building.png',
        development_style_profile: {
          massing: 'Boulevard mid-rise',
          roofForm: 'zinc mansard',
          materials: ['cream limestone', 'wrought iron'],
        },
      }),
      zone('p1', 'green_space', {
        plaza_archetype_id: 'custom_garden_variant_0',
        plaza_archetype_image: '/park.png',
        plaza_style_profile: { waterFeatures: 'None — no fountains' },
      }),
    ]);

    expect(contract.summary).toBe('1 building archetype · 1 open-space archetype · geometry-first video');
    expect(contract.referenceImageUrls).toEqual(['/building.png', '/park.png']);
    expect(contract.text).not.toContain('custom_midrise_variant_0');
    expect(contract.text).toContain('6 storeys');
    expect(contract.text).not.toContain('custom_garden_variant_0');
    expect(contract.text).not.toContain('Boulevard mid-rise');
    expect(contract.text).not.toContain('zinc mansard');
    expect(contract.text).not.toContain('cream limestone');
    expect(contract.text).not.toContain('None — no fountains');
    expect(contract.text).toContain('no place, city, or historical style name is supplied');
    expect(contract.text).toContain('descriptive style words are intentionally withheld');
    expect(contract.text).toContain('first frame is the geometric source of truth');
    expect(contract.text).toContain('visible courtyards, lightwells, roof voids, and wings');
    expect(contract.text).toContain('Never lengthen, widen, shrink, merge, split, fill, or invent');
    expect(contract.referenceRoleLabels).toEqual(['B1', 'P1']);
    expect(contract.text).not.toContain('<IMAGE_REF_0>');
  });

  it('falls back safely when zones have no archetype data', () => {
    const contract = buildVideoSceneContract([]);
    expect(contract.referenceImageUrls).toEqual([]);
    expect(contract.referenceRoleLabels).toEqual([]);
    expect(contract.text).toContain('Preserve every authored zone exactly');
  });

  it('repairs stale stored image paths from the current archetype catalogs', () => {
    const contract = buildVideoSceneContract([
      zone('b1', 'building', {
        development_archetype_id: 'parisian_midrise_block_variant_0',
        development_archetype_image: '/archetypes/buildings/parisian_mid_rise/variant_0.png',
      }),
      zone('p1', 'green_space', {
        plaza_archetype_id: 'beer_garden_variant_0',
      }),
    ]);

    expect(contract.referenceImageUrls).toContain('/archetypes/buildings/parisian_midrise_block/variant_0.png');
    expect(contract.referenceImageUrls).toContain('/archetypes/openspaces/beer-garden/variant_0_video.png');
  });

  it('locks multiple building zones as disconnected solids', () => {
    const contract = buildVideoSceneContract([
      zone('b1', 'building', { development_archetype_id: 'first_building' }),
      zone('b2', 'building', { development_archetype_id: 'second_building' }),
    ]);

    expect(contract.text).toContain('exactly 2 mutually disconnected solids');
    expect(contract.text).toContain('Never bridge, join, fuse, wrap, or extend one building toward another');
    expect(contract.text).toContain('never consolidate them into a perimeter block');
    expect(contract.text).toContain('ARCHETYPE SCOPE LOCK');
    expect(contract.text).toContain('All non-authored background buildings are immutable captured context');
    expect(contract.text).toContain('never copy, repeat, or propagate an authored facade');
  });
});
