// The browser production tsconfig intentionally omits Node globals, while
// Vitest executes this asset-integrity check in Node.
// @ts-expect-error -- available in the Vitest runtime without @types/node.
import { existsSync } from 'node:fs';
// @ts-expect-error -- available in the Vitest runtime without @types/node.
import { resolve } from 'node:path';

import { describe, expect, it } from 'vitest';

import {
  STREET_VISUAL_CONTRACTS,
  resolveStreetVisualContract,
  streetVisualContractKey,
} from './streetVisualContracts';

declare const process: { cwd: () => string; env: Record<string, string | undefined> };

function frontendRoot(): string {
  return existsSync(resolve(process.cwd(), 'src/main.tsx'))
    ? process.cwd()
    : resolve(process.cwd(), 'frontend');
}

// Match Vite's explicit asset root for isolated source worktrees. The same
// reference files are still checked; no missing assets are silently skipped.
function publicRoot(): string {
  return process.env.CITYPROMPT_PUBLIC_DIR || resolve(frontendRoot(), 'public');
}

describe('street visual QA contracts', () => {
  it('defines one uniquely addressable v0 keeper for each current-project archetype', () => {
    expect(STREET_VISUAL_CONTRACTS).toHaveLength(5);
    expect(new Set(STREET_VISUAL_CONTRACTS.map((contract) => contract.contractId)).size).toBe(5);
    expect(new Set(STREET_VISUAL_CONTRACTS.map((contract) => contract.archetypeId)).size).toBe(5);
    expect(STREET_VISUAL_CONTRACTS.map((contract) => contract.variantId).sort()).toEqual([
      'main_street_complete_v0',
      'narrow_residential_street_v0',
      'roundabout_v0',
      'woonerf_shared_street_v0',
      'yield_street_v0',
    ]);
    for (const contract of STREET_VISUAL_CONTRACTS) {
      expect(contract.contractId).toBe(`${contract.archetypeId}/${contract.variantId}`);
      expect(contract.scope).toBe('within_right_of_way');
      expect(contract.withinRow.required.length).toBeGreaterThan(5);
      expect(contract.withinRow.forbidden.length).toBeGreaterThan(4);
      expect(contract.surfaces.length).toBeGreaterThan(2);
    }
  });

  it('binds each keeper to real 30, 60 and 90 degree catalog references', () => {
    for (const contract of STREET_VISUAL_CONTRACTS) {
      expect(contract.referenceViews.map((view) => view.angleDeg)).toEqual([30, 60, 90]);
      for (const view of contract.referenceViews) {
        const localPath = resolve(publicRoot(), view.path.replace(/^\/+/, ''));
        expect(existsSync(localPath), `${contract.contractId}: ${localPath}`).toBe(true);
      }
    }
  });

  it('locks the residential street to an unmarked shaded parking street', () => {
    const contract = resolveStreetVisualContract(
      'narrow_residential_street',
      'narrow_residential_street_v0',
    );
    expect(contract?.target).toMatchObject({ type: 'segment', rowWidthM: 10 });
    expect(contract?.withinRow.required).toEqual(expect.arrayContaining([
      'unmarked_yield_carriageway',
      'bilateral_parallel_parking',
      'mature_deciduous_canopy',
    ]));
    expect(contract?.withinRow.forbidden).toEqual(expect.arrayContaining([
      'painted_centerline',
      'raised_median',
      'separated_cycle_track',
    ]));
    expect(contract?.rhythm.trees[0].spacingM).toEqual([9, 11]);
  });

  it('distinguishes the complete main street from a generic multi-lane road', () => {
    const contract = resolveStreetVisualContract(
      'main_street_complete',
      'main_street_complete_v0',
    );
    expect(contract?.target).toMatchObject({ type: 'segment', rowWidthM: 18 });
    expect(contract?.withinRow.required).toEqual(expect.arrayContaining([
      'two_way_travel_lanes',
      'parking_stall_markings',
      'sharrow_markings',
      'transit_shelter',
    ]));
    expect(contract?.withinRow.forbidden).toEqual(expect.arrayContaining([
      'painted_centerline',
      'raised_median',
      'separated_cycle_track',
    ]));
    expect(contract?.surfaces.find((surface) => surface.role === 'motor')).toMatchObject({
      material: 'asphalt',
      widthM: 3.65,
      markings: 'sharrows',
    });
  });

  it('keeps both Dutch shared streets curb-free while preserving their different scale', () => {
    const woonerf = resolveStreetVisualContract('woonerf_shared_street', 'woonerf_shared_street_v0');
    const yieldStreet = resolveStreetVisualContract('yield_street', 'yield_street_v0');

    expect(woonerf?.target).toMatchObject({ type: 'segment', rowWidthM: 10 });
    expect(yieldStreet?.target).toMatchObject({ type: 'segment', rowWidthM: 6 });
    for (const contract of [woonerf, yieldStreet]) {
      expect(contract?.withinRow.required).toEqual(expect.arrayContaining([
        'continuous_flush_surface',
        'herringbone_brick_paving',
        'chicane_delineation',
        'bollards',
      ]));
      expect(contract?.withinRow.forbidden).toEqual(expect.arrayContaining([
        'raised_curbs',
        'standard_lane_markings',
        'separated_sidewalks',
        'traffic_signals',
      ]));
      expect(contract?.surfaces.find((surface) => surface.role === 'shared')?.material)
        .toBe('unit_pavers');
    }
    expect(woonerf?.withinRow.required).toEqual(expect.arrayContaining([
      'raised_tables',
      'play_elements',
    ]));
    expect(yieldStreet?.withinRow.required).toContain('hydrangea_planters');
  });

  it('locks the roundabout to the reviewed compact single-lane node', () => {
    const contract = resolveStreetVisualContract('roundabout', 'roundabout_v0');
    expect(contract?.target).toMatchObject({
      type: 'node',
      armCount: 4,
      inscribedCircleDiameterM: 28,
    });
    expect(contract?.withinRow.required).toEqual(expect.arrayContaining([
      'single_lane_circulatory_ring',
      'truck_apron',
      'landscaped_central_island',
      'splitter_islands',
      'zebra_crosswalks',
      'yield_markings',
    ]));
    expect(contract?.withinRow.forbidden).toEqual(expect.arrayContaining([
      'multi_lane_circulatory_ring',
      'traffic_signals',
      'building_in_central_island',
    ]));
  });

  it('resolves canonical aliases exactly and fails closed for unsupported variants', () => {
    expect(streetVisualContractKey(' Main-Street-Complete ', 'MAIN-STREET-COMPLETE-V0'))
      .toBe('main_street_complete/main_street_complete_v0');
    expect(resolveStreetVisualContract(' Main-Street-Complete ', 'MAIN-STREET-COMPLETE-V0'))
      .toMatchObject({ contractId: 'main_street_complete/main_street_complete_v0' });
    expect(resolveStreetVisualContract('main_street_complete', 'main_street_complete_v3')).toBeNull();
    expect(resolveStreetVisualContract('main_street_complete', undefined)).toBeNull();
    expect(resolveStreetVisualContract('unknown', 'unknown_v0')).toBeNull();
  });
});
