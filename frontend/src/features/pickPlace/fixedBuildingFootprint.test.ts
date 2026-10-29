import { expect, it } from 'vitest';
import { hasFixedBuildingFootprint } from './fixedBuildingFootprint';
import { CATALOGUE_BUILDING_ASSETS } from './publishedBuildingAssets';
import { placeAsset } from './catalogue';
import { rectangleAt, resizeRectangleCorner } from './geometry';

it('removes horizontal reshape affordances from the three exact practical assemblies', () => {
  for (const id of ['claude_hospital_v006', 'claude_fire_station_v010', 'claude_student_residence_v004']) {
    expect(hasFixedBuildingFootprint(CATALOGUE_BUILDING_ASSETS.find(asset => asset.id === id)), id).toBe(true);
  }
});

it('preserves the reviewed Vancouver footprint programme and repeat-home plot tools', () => {
  expect(hasFixedBuildingFootprint(placeAsset('clay_vancouver_balcony_podium_tower'))).toBe(false);
  expect(hasFixedBuildingFootprint(placeAsset('trial_postwar_bungalow'))).toBe(false);
  expect(hasFixedBuildingFootprint(undefined)).toBe(false);
});

it('refuses a corner edit for an exact fixed warehouse', () => {
  const asset = placeAsset('claude_trial_cmu_dock_warehouse');
  const ring = rectangleAt([-114, 51], asset.width, asset.depth, 20);
  expect(resizeRectangleCorner(ring, 0, [-114.002, 50.998], asset)).toBe(ring);
});
