import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { QueryClient } from '@tanstack/react-query';
import { siteZonesApi } from '@/services/api';
import { createZoneUpdateAction } from '@/store/undoActions';
import type { SiteZone, SiteZoneProperties } from '@/types';
import { assetForZone, placeAsset, placementProperties } from './catalogue';
import { rectangleAt } from './geometry';
import {
  exactModelProperties, readResizeTrialState, resizeTrialFamilyForAsset, resizeTrialPlotReshape,
  resizeTrialRectangle, shapeFreelyProperties,
} from './buildingResizeTrial';

vi.mock('@/services/api', () => ({ siteZonesApi: { create: vi.fn(), update: vi.fn(), delete: vi.fn() },
  zoneHistoryApi: { restoreSnapshot: vi.fn() }, buildingsApi: {} }));

/** What the server stores and returns: JSON, so cleared keys are simply absent. */
const reload = <T,>(value: T): T => JSON.parse(JSON.stringify(value));
const asset = () => placeAsset('final_seniors_apartments');
const centre = [-114, 51];

describe('building resize pilot: undo, redo and reload', () => {
  beforeEach(() => {
    vi.stubEnv('VITE_ENABLE_BUILDING_RESIZE_TRIAL', 'true');
    vi.mocked(siteZonesApi.update).mockReset();
  });
  afterEach(() => vi.unstubAllEnvs());

  const steps = () => {
    const family = resizeTrialFamilyForAsset(asset())!;
    const placed = { coordinates: rectangleAt(centre, 36.4, 22, 15), properties: placementProperties(asset()) };
    const stretched = { coordinates: rectangleAt(centre, 44, 22, 15),
      properties: exactModelProperties(placed.properties, family, 1.2, 0.9, asset()) };
    const squeezedCoordinates = rectangleAt(centre, 34, 22, 15);
    const squeezed = { coordinates: squeezedCoordinates,
      properties: resizeTrialPlotReshape(stretched, squeezedCoordinates, asset())! };
    const freely = { coordinates: resizeTrialRectangle(centre, 55, 17.98, 15),
      properties: shapeFreelyProperties(squeezed.properties, 'stretch_out_of_band') };
    return { placed, stretched, squeezed, freely };
  };

  it('saves every pilot edit as one step that undo and redo restore whole', async () => {
    const { placed, stretched, squeezed, freely } = steps();
    const client = new QueryClient();
    const pairs: [typeof placed, typeof placed][] = [[placed, stretched], [stretched, squeezed], [squeezed, freely]];
    for (const [before, after] of pairs) {
      vi.mocked(siteZonesApi.update).mockReset()
        .mockResolvedValueOnce({ updated_at: 'r2' } as SiteZone).mockResolvedValueOnce({ updated_at: 'r3' } as SiteZone);
      const action = createZoneUpdateAction('project', 'midrise', before, after, client, 'r1');
      await action.undo();
      await action.redo();
      // Outline and properties travel together, so a plot never outlives its building's stretch.
      expect(siteZonesApi.update).toHaveBeenNthCalledWith(1, 'midrise', { ...before, expected_updated_at: 'r1' }, { skipHistory: true });
      expect(siteZonesApi.update).toHaveBeenNthCalledWith(2, 'midrise', { ...after, expected_updated_at: 'r2' }, { skipHistory: true });
    }
  });

  it('reads back the same state after a reload at every step', () => {
    const { placed, stretched, squeezed, freely } = steps();
    const state = (properties: SiteZoneProperties) => {
      const { family: _family, ...rest } = readResizeTrialState(properties)!;
      return rest;
    };
    expect(state(reload(placed.properties))).toEqual({ mode: 'exact_model', widthScale: 1, depthScale: 1, declared: false });
    expect(state(reload(stretched.properties))).toEqual({ mode: 'exact_model', widthScale: 1.2, depthScale: 0.9, declared: true });
    expect(state(reload(squeezed.properties))).toMatchObject({ mode: 'exact_model', depthScale: 0.9, declared: true });
    expect(state(reload(squeezed.properties)).widthScale).toBeLessThan(1);
    expect(state(reload(freely.properties))).toEqual({ mode: 'shape_freely', widthScale: 1, depthScale: 1, declared: true, reason: 'stretch_out_of_band' });
    for (const step of [placed, stretched, squeezed, freely]) {
      expect(reload(step.properties)).toEqual(reload(reload(step.properties)));
      expect(state(reload(step.properties))).toEqual(state(step.properties));
    }
    // The editing tools resolve the same asset shape before and after a reload.
    const tools = (step: typeof placed) => {
      const resolved = assetForZone({ properties: reload(step.properties) })!;
      return [resolved.reshapeMode, resolved.footprintProgram?.mode];
    };
    expect(tools(stretched)).toEqual(['fixed_native', 'independent_horizontal_scale']);
    expect(tools(freely)).toEqual(['authored_footprint', undefined]);
  });

  it('undoing back to the placed building leaves no pilot state behind', () => {
    const { placed, freely } = steps();
    const stored = reload(freely.properties);
    expect(stored).not.toHaveProperty('building_footprint_width_scale');
    expect(stored).not.toHaveProperty('pedestrian_building_entrance');
    const restored = reload(placed.properties);
    for (const key of Object.keys(restored)) expect(key.startsWith('building_footprint_')).toBe(false);
    expect(restored.pedestrian_building_entrance).toMatchObject({ xM: -4, fixedNative: true });
    expect(restored.building_geometry_basis).toBe('placement_plot');
  });
});
