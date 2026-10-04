import { expect, it } from 'vitest';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';
import { FLEXIBLE_PARK_ASSETS } from '@/features/pickPlace/assetRegistry';
import { CANONICAL_CHOICES } from '@/features/pickPlace/canonicalCatalogue';
import { assetForZone, placementProperties, placeAsset } from '@/features/pickPlace/catalogue';
import { flexibleParkFitProblem } from './flexibleParkFit';

const latitude = 51.12, longitude = -114;
const coordinates = (points: number[][]) => points.map(([x, y]) => [longitude + x / metersPerDegLon(latitude), latitude + y / METERS_PER_DEG_LAT]);

it('offers two distinct draw-first park programmes with stable saved identities', () => {
  expect(FLEXIBLE_PARK_ASSETS.map(asset => asset.model.variantId)).toEqual(['urban_pocket_park_v0', 'linear_park_greenway_v0']);
  for (const asset of FLEXIBLE_PARK_ASSETS) {
    expect(CANONICAL_CHOICES.some(choice => choice.placements.some(candidate => candidate.id === asset.id))).toBe(true);
    expect(assetForZone({ properties: placementProperties(placeAsset(asset.id)) })?.id).toBe(asset.id);
    expect(asset.properties.pick_place_automatic_3d).toBe(true);
  }
});

it('accepts varied complete pocket outlines and a tapered greenway, rejecting unsupported scale', () => {
  const pocket = FLEXIBLE_PARK_ASSETS[0].properties, greenway = FLEXIBLE_PARK_ASSETS[1].properties;
  expect(flexibleParkFitProblem(coordinates([[0, 0], [35, 0], [35, 12], [20, 12], [20, 32], [0, 32]]), pocket)).toBeNull();
  expect(flexibleParkFitProblem(coordinates([[0, 0], [35, 0], [5, 35]]), pocket)).toBeNull();
  expect(flexibleParkFitProblem(coordinates([[0, 0], [90, 0], [90, 15], [50, 18], [50, 24], [0, 20]]), greenway)).toBeNull();
  expect(flexibleParkFitProblem(coordinates([[0, 0], [5, 0], [5, 5], [0, 5]]), pocket)).toContain('64–3,600');
  expect(flexibleParkFitProblem(coordinates([[0, 0], [35, 0], [35, 30], [0, 30]]), greenway)).toContain('60 m long');
});
