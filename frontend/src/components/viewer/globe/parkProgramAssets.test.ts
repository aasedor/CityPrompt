import { describe, expect, it } from 'vitest';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { computeParkProgramAssetPlacements } from './parkProgramAssets';

function rectangularZone(widthM: number, heightM: number, archetypeId = 'basketball_court') {
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
    properties: { green_space_archetype_id: archetypeId },
    zone_type: 'green_space' as const,
  };
}

describe('computeParkProgramAssetPlacements', () => {
  it('derives a complete basketball equipment kit from the fitted court guide', () => {
    const placements = computeParkProgramAssetPlacements(rectangularZone(40, 30));
    expect(placements.filter((placement) => placement.propId === 'basketball_hoop')).toHaveLength(2);
    expect(placements.filter((placement) => placement.propId === 'chainlink_fence_4m')).toHaveLength(24);
    expect(placements.filter((placement) => placement.propId === 'chainlink_gate_3m')).toHaveLength(2);
    expect(placements.filter((placement) => placement.propId === 'basketball_floodlight')).toHaveLength(4);
    expect(placements).toHaveLength(32);
    expect(placements.every((placement) => placement.surfaceOffsetM === 0.32)).toBe(true);
  });

  it('rotates the complete court kit when that is the only fitting orientation', () => {
    const placements = computeParkProgramAssetPlacements(rectangularZone(25, 38));
    const hoops = placements.filter((placement) => placement.propId === 'basketball_hoop');
    expect(hoops).toHaveLength(2);
    const dLngM = (hoops[1].lng - hoops[0].lng) * metersPerDegLon(51.0447);
    const dLatM = (hoops[1].lat - hoops[0].lat) * METERS_PER_DEG_LAT;
    expect(Math.abs(dLngM)).toBeLessThan(0.05);
    expect(Math.abs(dLatM)).toBeCloseTo(30.4, 1);
  });

  it('omits the kit when the complete metric court cannot fit', () => {
    expect(computeParkProgramAssetPlacements(rectangularZone(25, 18))).toEqual([]);
  });

  it('does not add basketball equipment to another open-space archetype', () => {
    expect(computeParkProgramAssetPlacements(rectangularZone(40, 30, 'urban_pocket_park')))
      .toEqual([]);
  });
});
