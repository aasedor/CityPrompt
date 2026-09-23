import { describe, expect, it } from 'vitest';
import { PLACE_ASSETS, placeAsset, placementPlanRequest } from './catalogue';
import { rectangleAt, rectangleDimensions, resizeRectangleCorner } from './geometry';

describe('native catalogue placement contracts', () => {
  it('cannot share a preview plan between two homes on identically sized plots', () => {
    const infill = placementPlanRequest(placeAsset('infill_home'), 30, 30, 'project');
    const bungalow = placementPlanRequest(placeAsset('craftsman_bungalow'), 30, 30, 'project');
    expect(infill?.archetype_id).toBe('infill_flat_roof_minimal');
    expect(bungalow?.archetype_id).toBe('craftsman_classic');
    expect(bungalow?.target_floors).toBe(1);
    expect(JSON.stringify(infill)).not.toBe(JSON.stringify(bungalow));
    expect(placementPlanRequest(placeAsset('neighbourhood_park'), 40, 35)).toBeNull();
  });
  it.each(PLACE_ASSETS.filter(asset => asset.zoneType === 'building'))('keeps $id whole when a corner is dragged too close', asset => {
    const coordinates = rectangleAt([-114.04677, 51.04542], asset.width * 2, asset.depth * 2, 37);
    const fixed = coordinates[2];
    const resized = resizeRectangleCorner(coordinates, 0, fixed, asset);
    const dimensions = rectangleDimensions(resized);
    expect(dimensions.width).toBeCloseTo(asset.minWidth, 3);
    expect(dimensions.depth).toBeCloseTo(asset.minDepth, 3);
    expect(dimensions.width - asset.nativeDimensions![0]).toBeGreaterThanOrEqual(3 - 1e-6);
    expect(dimensions.depth - asset.nativeDimensions![1]).toBeGreaterThanOrEqual(3 - 1e-6);
    expect(resized[2][0]).toBeCloseTo(fixed[0], 7);
    expect(resized[2][1]).toBeCloseTo(fixed[1], 7);
  });
});
