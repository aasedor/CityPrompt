import { describe, expect, it } from 'vitest';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { computeParkProgramAssetPlacements } from './parkProgramAssets';
import { PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS } from './publicRealmDepthPolicy';

function rectangularZone(
  widthM: number,
  heightM: number,
  archetypeId = 'basketball_court',
  variantId = 'basketball_court_v0',
) {
  const center = { lng: -114.0719, lat: 51.0447 };
  const halfLng = widthM / 2 / metersPerDegLon(center.lat);
  const halfLat = heightM / 2 / METERS_PER_DEG_LAT;
  return {
    coordinates: [
      [center.lng - halfLng, center.lat - halfLat],
      [center.lng + halfLng, center.lat - halfLat],
      [center.lng + halfLng, center.lat + halfLat],
      [center.lng - halfLng, center.lat + halfLat],
    ],
    properties: {
      green_space_archetype_id: archetypeId,
      green_space_selected_variant_id: variantId,
    },
    zone_type: 'green_space' as const,
  };
}

describe('computeParkProgramAssetPlacements', () => {
  it('anchors two regulation hoops to a complete fitted basketball court', () => {
    const placements = computeParkProgramAssetPlacements(rectangularZone(40, 30));
    expect(placements).toHaveLength(2);
    expect(placements.every(({ propId }) => propId === 'basketball_hoop_regulation')).toBe(true);
    expect(placements.every(({ surfaceOffsetM }) => (
      surfaceOffsetM === PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS
    ))).toBe(true);
    const separationM = Math.abs(placements[1].lng - placements[0].lng)
      * metersPerDegLon(51.0447);
    expect(separationM).toBeCloseTo(30.4, 1);
  });

  it('builds two complete courts and four hoops on an oversized parcel', () => {
    const placements = computeParkProgramAssetPlacements(rectangularZone(72, 30));
    expect(placements).toHaveLength(4);
  });

  it('builds the community mural variant as one half-court with one hoop', () => {
    const placements = computeParkProgramAssetPlacements(rectangularZone(
      25,
      20,
      'basketball_court',
      'basketball_court_v2',
    ));
    expect(placements).toHaveLength(1);
  });

  it('rotates the complete pair when only the orthogonal court fits', () => {
    const placements = computeParkProgramAssetPlacements(rectangularZone(25, 38));
    expect(placements).toHaveLength(2);
    const eastWestM = Math.abs(placements[1].lng - placements[0].lng)
      * metersPerDegLon(51.0447);
    const northSouthM = Math.abs(placements[1].lat - placements[0].lat)
      * METERS_PER_DEG_LAT;
    expect(eastWestM).toBeLessThan(0.05);
    expect(northSouthM).toBeCloseTo(30.4, 1);
  });

  it('omits equipment when the regulation envelope cannot fit', () => {
    expect(computeParkProgramAssetPlacements(rectangularZone(25, 18))).toEqual([]);
  });

  it('does not leak basketball equipment into another archetype', () => {
    expect(computeParkProgramAssetPlacements(rectangularZone(40, 30, 'urban_pocket_park')))
      .toEqual([]);
  });
});
