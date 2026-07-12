import { describe, expect, it } from 'vitest';

import { computeParkPlacements } from './parkScatter';
import { resolveParkRecipe } from '@/data/parkKitRecipes';
import { pointInPolygon } from '@/utils/coordTransform';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';

// ~1 hectare square (100m x 100m) near Calgary
const LAT = 51.05;
const LNG = -114.07;
const M_PER_LON = metersPerDegLon(LAT);
function squareRing(sizeM: number): number[][] {
  const dLng = sizeM / M_PER_LON;
  const dLat = sizeM / METERS_PER_DEG_LAT;
  return [
    [LNG, LAT],
    [LNG + dLng, LAT],
    [LNG + dLng, LAT + dLat],
    [LNG, LAT + dLat],
  ];
}

const NEIGHBORHOOD = resolveParkRecipe('neighborhood_park');

describe('computeParkPlacements', () => {
  it('is deterministic for the same zone id', () => {
    const zone = { id: 'zone-abc', coordinates: squareRing(100) };
    const a = computeParkPlacements(zone, NEIGHBORHOOD);
    const b = computeParkPlacements(zone, NEIGHBORHOOD);
    expect(a).toEqual(b);
    expect(a.length).toBeGreaterThan(0);
  });

  it('differs between zones but stays stable per zone', () => {
    const ring = squareRing(100);
    const a = computeParkPlacements({ id: 'zone-1', coordinates: ring }, NEIGHBORHOOD);
    const b = computeParkPlacements({ id: 'zone-2', coordinates: ring }, NEIGHBORHOOD);
    expect(a).not.toEqual(b);
  });

  it('places roughly the recipe tree density inside the polygon', () => {
    const zone = { id: 'zone-density', coordinates: squareRing(100) };
    const placements = computeParkPlacements(zone, NEIGHBORHOOD);
    const trees = placements.filter((p) => p.propId === 'tree');
    // 40/ha target; spacing rejection may drop a few
    expect(trees.length).toBeGreaterThanOrEqual(30);
    expect(trees.length).toBeLessThanOrEqual(40);
    for (const t of placements) {
      expect(pointInPolygon(t.lng, t.lat, zone.coordinates)).toBe(true);
    }
  });

  it('respects minimum tree spacing', () => {
    const zone = { id: 'zone-spacing', coordinates: squareRing(100) };
    const trees = computeParkPlacements(zone, NEIGHBORHOOD).filter((p) => p.propId === 'tree');
    for (let i = 0; i < trees.length; i++) {
      for (let j = i + 1; j < trees.length; j++) {
        const dx = (trees[i].lng - trees[j].lng) * M_PER_LON;
        const dy = (trees[i].lat - trees[j].lat) * METERS_PER_DEG_LAT;
        expect(Math.hypot(dx, dy)).toBeGreaterThanOrEqual(NEIGHBORHOOD.trees.minSpacing_m - 1e-6);
      }
    }
  });

  it('gates the playground on area', () => {
    const small = computeParkPlacements({ id: 'z-small', coordinates: squareRing(45) }, NEIGHBORHOOD); // ~2000 m²
    const big = computeParkPlacements({ id: 'z-big', coordinates: squareRing(70) }, NEIGHBORHOOD); // ~4900 m²
    expect(small.filter((p) => p.propId === 'playground')).toHaveLength(0);
    expect(big.filter((p) => p.propId === 'playground').length).toBeGreaterThan(0);
  });

  it('keeps trees out of the playground clearance', () => {
    const zone = { id: 'z-clear', coordinates: squareRing(80) };
    const placements = computeParkPlacements(zone, NEIGHBORHOOD);
    const trees = placements.filter((p) => p.propId === 'tree');
    // playground cluster is centered at the polygon centroid
    const cLng = LNG + 40 / M_PER_LON;
    const cLat = LAT + 40 / METERS_PER_DEG_LAT;
    for (const t of trees) {
      const d = Math.hypot((t.lng - cLng) * M_PER_LON, (t.lat - cLat) * METERS_PER_DEG_LAT);
      expect(d).toBeGreaterThanOrEqual(NEIGHBORHOOD.playground!.clearance_m - 1e-6);
    }
  });

  it('puts benches near the boundary facing inward', () => {
    const zone = { id: 'z-bench', coordinates: squareRing(100) };
    const benches = computeParkPlacements(zone, NEIGHBORHOOD).filter((p) => p.propId === 'bench');
    expect(benches.length).toBeGreaterThanOrEqual(NEIGHBORHOOD.benches!.min);
    for (const b of benches) {
      const x = (b.lng - LNG) * M_PER_LON;
      const y = (b.lat - LAT) * METERS_PER_DEG_LAT;
      const edgeDist = Math.min(x, y, 100 - x, 100 - y);
      expect(edgeDist).toBeLessThanOrEqual(NEIGHBORHOOD.benches!.edgeInset_m + 0.6);
    }
  });

  it('never places props outside a concave (L-shaped) polygon', () => {
    // L-shape whose vertex-mean centroid falls in the notch (outside).
    const d = (m: number) => m / M_PER_LON;
    const dl = (m: number) => m / METERS_PER_DEG_LAT;
    const lShape = [
      [LNG, LAT],
      [LNG + d(120), LAT],
      [LNG + d(120), LAT + dl(40)],
      [LNG + d(40), LAT + dl(40)],
      [LNG + d(40), LAT + dl(120)],
      [LNG, LAT + dl(120)],
    ];
    const placements = computeParkPlacements({ id: 'z-lshape', coordinates: lShape }, NEIGHBORHOOD);
    for (const p of placements) {
      expect(pointInPolygon(p.lng, p.lat, lShape)).toBe(true);
    }
  });

  it('returns nothing for degenerate zones', () => {
    expect(computeParkPlacements({ id: 'z', coordinates: [] }, NEIGHBORHOOD)).toEqual([]);
    expect(
      computeParkPlacements({ id: 'z', coordinates: squareRing(5) }, NEIGHBORHOOD),
    ).toEqual([]);
  });
});
