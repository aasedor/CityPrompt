import { describe, expect, it } from 'vitest';
import { placeAsset, placementPlanRequest, placementProperties } from './catalogue';
import { footprintProgramSupports, footprintProgramTarget } from './buildingFootprintProgram';

const pilotIds = [
  'trial_postwar_bungalow',
  'trial_edwardian_foursquare',
  'validation_clapboard_north_end',
] as const;

describe('authored low-rise footprint programs', () => {
  it.each(pilotIds)('uses a uniform 85–115 percent scale band for %s', assetId => {
    const asset = placeAsset(assetId);
    const program = asset.footprintProgram!;
    expect(program.mode).toBe('uniform_horizontal_scale');
    expect(footprintProgramSupports(program, 0.85)).toBe(true);
    expect(footprintProgramSupports(program, 1.15)).toBe(true);
    expect(footprintProgramSupports(program, 0.84)).toBe(false);
    expect(footprintProgramSupports(program, 1.16)).toBe(false);
    expect(footprintProgramTarget(program, 1.15)).toEqual({
      widthM: Math.round(program.nativeWidthM * 1.15 * 10000) / 10000,
      depthM: Math.round(program.nativeDepthM * 1.15 * 10000) / 10000,
      scale: 1.15,
    });
    expect(placementProperties(asset)).toMatchObject({
      building_footprint_scale: 1,
      building_footprint_program_id: 'house-flex-pilot-v001',
      building_footprint_native_width_m: program.nativeWidthM,
      building_footprint_native_depth_m: program.nativeDepthM,
    });
    const request = placementPlanRequest(asset, asset.width, asset.depth)!;
    expect(request.target_width_m).toBeCloseTo(program.nativeWidthM, 4);
    expect(request.target_depth_m).toBeCloseTo(program.nativeDepthM, 4);
  });
});
