import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import streetPathCatalog from './streetPathArchetypes.json';
import { RENDERLOCK_V1_STREETS } from './renderlockV1Streets';
import { resolvePilotStreetSectionProfile } from '../components/viewer/globe/streetSectionProfiles';

function zone(archetypeId: string, variantId: string, width: number): SiteZone {
  return {
    id: `zone-${archetypeId}`,
    project_id: 'renderlock-streets-v1',
    zone_type: 'road',
    name: archetypeId,
    coordinates: [[-113.58, 53.37], [-113.57, 53.37], [-113.57, 53.3699], [-113.58, 53.3699]],
    color: '#64748b',
    properties: {
      _plan_role: 'street',
      road_archetype_id: archetypeId,
      road_selected_variant_id: variantId,
      width,
    },
    sort_order: 0,
    created_at: '2026-07-20T00:00:00Z',
    updated_at: '2026-07-20T00:00:00Z',
  };
}

describe('render-lock v1 street cohort', () => {
  it('is finite, ordered and unique', () => {
    expect(RENDERLOCK_V1_STREETS).toHaveLength(10);
    expect(RENDERLOCK_V1_STREETS.map((entry) => entry.sequence)).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
    expect(new Set(RENDERLOCK_V1_STREETS.map((entry) => entry.archetypeId)).size).toBe(10);
    expect(new Set(RENDERLOCK_V1_STREETS.map((entry) => entry.variantId)).size).toBe(10);
    expect(RENDERLOCK_V1_STREETS.every((entry) => entry.reviewState === 'keeper')).toBe(true);
  });

  it('references real selected catalog variants', () => {
    const catalog = (streetPathCatalog as { archetypes: Array<{ id: string; variants: Array<{ id: string }> }> }).archetypes;
    for (const entry of RENDERLOCK_V1_STREETS) {
      const archetype = catalog.find((candidate) => candidate.id === entry.archetypeId);
      expect(archetype, entry.archetypeId).toBeDefined();
      expect(archetype?.variants.some((variant) => variant.id === entry.variantId), entry.variantId).toBe(true);
      expect(entry.referenceViews.length).toBeGreaterThan(0);
      expect(entry.referenceViews.every((path) => path.startsWith('/archetypes/streets/'))).toBe(true);
    }
  });

  it('locks an exact complete cross-section for every keeper', () => {
    for (const entry of RENDERLOCK_V1_STREETS) {
      const profile = resolvePilotStreetSectionProfile(zone(entry.archetypeId, entry.variantId, entry.rowM));
      expect(profile, entry.archetypeId).not.toBeNull();
      expect(profile?.isPilot).toBe(true);
      expect(profile?.variantId).toBe(entry.variantId);
      expect(profile?.rowM).toBeCloseTo(entry.rowM, 5);
      expect(profile?.bands.reduce((sum, band) => sum + band.widthM, 0)).toBeCloseTo(entry.rowM, 5);
      expect(profile?.bands.every((band) => band.widthM > 0)).toBe(true);
      expect(entry.crossSectionTruth.length).toBeGreaterThan(40);
    }
  });

  it('keeps soft/shared facilities curb-free and engineered roads curbed', () => {
    for (const id of ['yield_street', 'multi_use_trail', 'toronto_laneway']) {
      const entry = RENDERLOCK_V1_STREETS.find((candidate) => candidate.archetypeId === id)!;
      const profile = resolvePilotStreetSectionProfile(zone(id, entry.variantId, entry.rowM));
      expect(profile?.renderCurbs, id).toBe(false);
      expect(profile?.curbOffsetsM, id).toEqual([]);
    }
    for (const id of ['collector_road', 'main_street_complete', 'protected_bike_lane_bidirectional', 'calgary_arterial_4lane_50']) {
      const entry = RENDERLOCK_V1_STREETS.find((candidate) => candidate.archetypeId === id)!;
      const profile = resolvePilotStreetSectionProfile(zone(id, entry.variantId, entry.rowM));
      expect(profile?.renderCurbs, id).toBe(true);
      expect(profile?.curbOffsetsM.length, id).toBeGreaterThan(0);
    }
  });
});
