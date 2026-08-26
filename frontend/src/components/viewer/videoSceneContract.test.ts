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
  it('uses zone metadata only to lock the captured scene', () => {
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

    expect(contract.summary).toBe('1 building archetype · 1 open-space archetype · source-fidelity animation');
    expect(contract.text).not.toContain('custom_midrise_variant_0');
    expect(contract.text).toContain('6 storeys');
    expect(contract.text).not.toContain('custom_garden_variant_0');
    expect(contract.text).not.toContain('Boulevard mid-rise');
    expect(contract.text).not.toContain('zinc mansard');
    expect(contract.text).not.toContain('cream limestone');
    expect(contract.text).not.toContain('None — no fountains');
    expect(contract.text).toContain('no place, city, historical style name, material prompt, or catalog image is supplied');
    expect(contract.text).toContain('descriptive style words, and catalog images are intentionally withheld');
    expect(contract.text).toContain('Image1 is the sole geometric and visual source of truth');
    expect(contract.text).toContain('without enhancement');
    expect(contract.text).toContain('visible courtyards, lightwells, roof voids, and wings');
    expect(contract.text).toContain('Never lengthen, widen, shrink, merge, split, fill, or invent');
    expect(contract.text).not.toContain('<IMAGE_REF_0>');
  });

  it('falls back safely when zones have no archetype data', () => {
    const contract = buildVideoSceneContract([]);
    expect(contract.text).toContain('Preserve every authored zone exactly');
    expect(contract.text).toContain('without adding materials, lighting, detail, or design interpretation');
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

  it('keeps every geometry lock but unlocks appearance in photoreal finish', () => {
    const zones = [
      zone('b1', 'building', { floors: 6, height: 18, development_archetype_id: 'custom_midrise_variant_0' }),
      zone('p1', 'green_space', { plaza_archetype_id: 'custom_garden_variant_0' }),
    ];
    const contract = buildVideoSceneContract(zones, 'photoreal');

    expect(contract.finishMode).toBe('photoreal');
    expect(contract.summary).toBe('1 building archetype · 1 open-space archetype · photoreal finish');

    // Appearance is deliberately unlocked.
    expect(contract.text).toContain('untextured study massing');
    expect(contract.text).toContain('materialize its surfaces into photoreal');
    expect(contract.text).not.toContain('without enhancement');

    // Geometry, topology and count locks survive unchanged.
    expect(contract.text).toContain('Preserve its exact on-screen footprint');
    expect(contract.text).toContain('visible courtyards, lightwells, roof voids, and wings');
    expect(contract.text).toContain('Never lengthen, widen, shrink, merge, split, fill, or invent');
    expect(contract.text).toContain('ARCHETYPE SCOPE LOCK');
    expect(contract.text).toContain('GLOBAL FORBIDDEN CHANGES');

    // Archetype identity still never reaches the model.
    expect(contract.text).not.toContain('custom_midrise_variant_0');
    expect(contract.text).not.toContain('custom_garden_variant_0');
    expect(contract.text).toContain('do not invent a named architectural style');
  });

  it('defaults to massing fidelity and separates the two modes by signature', () => {
    const zones = [zone('b1', 'building', { floors: 4 })];
    const locked = buildVideoSceneContract(zones);
    const photoreal = buildVideoSceneContract(zones, 'photoreal');

    expect(locked.finishMode).toBe('massing_fidelity');
    expect(locked.text).toBe(buildVideoSceneContract(zones, 'massing_fidelity').text);
    // A request prepared under one mode must not satisfy the other.
    expect(locked.signature).not.toBe(photoreal.signature);
  });

  it('materializes the fallback contract when no zone carries archetype data', () => {
    const contract = buildVideoSceneContract([], 'photoreal');
    expect(contract.text).toContain('materialize its untextured study surfaces');
    expect(contract.text).not.toContain('without adding materials, lighting, detail');
  });
});
