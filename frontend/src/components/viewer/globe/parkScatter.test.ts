import { describe, expect, it } from 'vitest';

import { computeParkPlacements, PLANTING_STRUCTURES, type PropPlacement } from './parkScatter';
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

/** Placement position back to metres from the ring origin (LNG/LAT corner). */
function toMeters(p: { lng: number; lat: number }): [number, number] {
  return [(p.lng - LNG) * M_PER_LON, (p.lat - LAT) * METERS_PER_DEG_LAT];
}

function treesOf(placements: PropPlacement[]): PropPlacement[] {
  return placements.filter((p) => p.propId === 'tree');
}

function meanNearestNeighborM(trees: PropPlacement[]): number {
  const pts = trees.map(toMeters);
  let sum = 0;
  for (let i = 0; i < pts.length; i++) {
    let best = Infinity;
    for (let j = 0; j < pts.length; j++) {
      if (i === j) continue;
      best = Math.min(best, Math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1]));
    }
    sum += best;
  }
  return sum / pts.length;
}

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

describe('planting structures', () => {
  it('is deterministic for every planting structure', () => {
    const zone = { id: 'z-det', coordinates: squareRing(90) };
    for (const s of PLANTING_STRUCTURES) {
      const a = computeParkPlacements(zone, NEIGHBORHOOD, s);
      const b = computeParkPlacements(zone, NEIGHBORHOOD, s);
      expect(a).toEqual(b);
      expect(a.length).toBeGreaterThan(0);
    }
  });

  it('falls back to legacy scatter for absent or unknown structures', () => {
    const zone = { id: 'z-fallback', coordinates: squareRing(90) };
    const legacy = computeParkPlacements(zone, NEIGHBORHOOD);
    expect(computeParkPlacements(zone, NEIGHBORHOOD, 'martian_bog')).toEqual(legacy);
    expect(computeParkPlacements(zone, NEIGHBORHOOD, undefined)).toEqual(legacy);
  });

  it('keeps every structure inside a concave (L-shaped) polygon', () => {
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
    for (const s of PLANTING_STRUCTURES) {
      const placements = computeParkPlacements({ id: 'z-l', coordinates: lShape }, NEIGHBORHOOD, s);
      for (const p of placements) {
        expect(pointInPolygon(p.lng, p.lat, lShape)).toBe(true);
      }
    }
  });

  it('respects min tree spacing in the densest structures', () => {
    for (const s of ['naturalistic_grove', 'buffer_edge', 'formal_allee'] as const) {
      const trees = treesOf(
        computeParkPlacements({ id: `z-space-${s}`, coordinates: squareRing(100) }, NEIGHBORHOOD, s),
      );
      for (let i = 0; i < trees.length; i++) {
        for (let j = i + 1; j < trees.length; j++) {
          const dx = (trees[i].lng - trees[j].lng) * M_PER_LON;
          const dy = (trees[i].lat - trees[j].lat) * METERS_PER_DEG_LAT;
          expect(Math.hypot(dx, dy)).toBeGreaterThanOrEqual(NEIGHBORHOOD.trees.minSpacing_m - 1e-6);
        }
      }
    }
  });

  it('formal_allee: rows are collinear, evenly spaced, uniform, and hug the edges', () => {
    const zone = { id: 'z-allee', coordinates: squareRing(100) };
    const trees = treesOf(computeParkPlacements(zone, NEIGHBORHOOD, 'formal_allee'));
    expect(trees.length).toBeGreaterThan(20);
    for (const t of trees) {
      expect(t.scale).toBe(1); // uniform scale
      const [x, y] = toMeters(t);
      // open centre: allee planting stays in the perimeter rows
      expect(Math.min(x, y, 100 - x, 100 - y)).toBeLessThanOrEqual(10);
    }
    // mid-span of the bottom-edge row (clear of the perpendicular rows'
    // corner trees): collinear + regular interval
    const row = trees
      .map(toMeters)
      .filter(([x, y]) => y < 4 && x > 10 && x < 90)
      .sort((a, b) => a[0] - b[0]);
    expect(row.length).toBeGreaterThanOrEqual(6);
    for (const [, y] of row) expect(y).toBeCloseTo(row[0][1], 5);
    const gaps = row.slice(1).map((p, i) => p[0] - row[i][0]);
    for (const g of gaps) {
      expect(g).toBeGreaterThanOrEqual(7 - 1e-6); // uniform 7-9m interval
      expect(g).toBeLessThanOrEqual(9 + 1e-6);
      expect(g).toBeCloseTo(gaps[0], 5);
    }
  });

  it('formal_allee keeps benches but drops the playground', () => {
    const placements = computeParkPlacements(
      { id: 'z-allee-b', coordinates: squareRing(80) },
      NEIGHBORHOOD,
      'formal_allee',
    );
    expect(placements.filter((p) => p.propId === 'bench').length).toBeGreaterThan(0);
    expect(placements.filter((p) => p.propId === 'playground')).toHaveLength(0);
  });

  it('naturalistic_grove clusters trees far more tightly than open_meadow', () => {
    const ring = squareRing(140); // ~2 ha — room for distinct groves
    const grove = treesOf(
      computeParkPlacements({ id: 'z-structure', coordinates: ring }, NEIGHBORHOOD, 'naturalistic_grove'),
    );
    const meadow = treesOf(
      computeParkPlacements({ id: 'z-structure', coordinates: ring }, NEIGHBORHOOD, 'open_meadow'),
    );
    expect(grove.length).toBeGreaterThan(meadow.length);
    // grove trees pack near min spacing (the few meadow singles lift the mean)
    expect(meanNearestNeighborM(grove)).toBeLessThan(10);
    expect(meanNearestNeighborM(grove)).toBeLessThan(meanNearestNeighborM(meadow) * 0.75);
  });

  it('open_meadow is sparse with 1-3 specimen trees near (not on) the centroid', () => {
    const zone = { id: 'z-meadow', coordinates: squareRing(100) };
    const legacyTrees = treesOf(computeParkPlacements(zone, NEIGHBORHOOD));
    const trees = treesOf(computeParkPlacements(zone, NEIGHBORHOOD, 'open_meadow'));
    expect(trees.length).toBeGreaterThan(0);
    expect(trees.length).toBeLessThan(legacyTrees.length * 0.5);
    const specimens = trees.filter((t) => t.scale >= 1.3);
    expect(specimens.length).toBeGreaterThanOrEqual(1);
    expect(specimens.length).toBeLessThanOrEqual(3);
    for (const s of specimens) {
      const [x, y] = toMeters(s);
      const d = Math.hypot(x - 50, y - 50);
      expect(d).toBeGreaterThan(2); // never ON the centroid
      expect(d).toBeLessThan(30); // but near it
    }
  });

  it('active_recreation pulls trees toward benches and the playground clearance ring', () => {
    const zone = { id: 'z-rec', coordinates: squareRing(80) }; // playground gates on
    const active = computeParkPlacements(zone, NEIGHBORHOOD, 'active_recreation');
    const legacy = computeParkPlacements(zone, NEIGHBORHOOD);
    const meanAnchorDist = (list: PropPlacement[]) => {
      const anchors = list.filter((p) => p.propId !== 'tree').map(toMeters);
      const trees = treesOf(list).map(toMeters);
      let sum = 0;
      for (const [x, y] of trees) {
        sum += Math.min(...anchors.map(([ax, ay]) => Math.hypot(x - ax, y - ay)));
      }
      return sum / trees.length;
    };
    // same seed + furniture path -> identical anchors; only trees differ
    expect(meanAnchorDist(active)).toBeLessThan(meanAnchorDist(legacy) * 0.8);
    // shade trees ring the playground clearance, never enter it
    for (const t of treesOf(active)) {
      const [x, y] = toMeters(t);
      expect(Math.hypot(x - 40, y - 40)).toBeGreaterThanOrEqual(
        NEIGHBORHOOD.playground!.clearance_m - 1e-6,
      );
    }
  });

  it('formal_quad lays a uniform grid aligned to the long axis', () => {
    const zone = { id: 'z-quad', coordinates: squareRing(40) };
    const trees = treesOf(computeParkPlacements(zone, NEIGHBORHOOD, 'formal_quad'));
    expect(trees.length).toBeGreaterThanOrEqual(9);
    for (const t of trees) {
      expect(t.scale).toBe(1);
      expect(t.yawRad).toBe(trees[0].yawRad); // aligned, single species read
    }
    // full grid: every (row, column) combination is occupied
    const xs = new Set(trees.map((t) => Math.round(toMeters(t)[0] * 10)));
    const ys = new Set(trees.map((t) => Math.round(toMeters(t)[1] * 10)));
    expect(xs.size).toBeGreaterThanOrEqual(2);
    expect(ys.size).toBeGreaterThanOrEqual(2);
    expect(xs.size * ys.size).toBe(trees.length);
  });

  it('garden_courtyard tucks small clusters into corners plus one specimen', () => {
    const zone = { id: 'z-court', coordinates: squareRing(40) };
    const trees = treesOf(computeParkPlacements(zone, NEIGHBORHOOD, 'garden_courtyard'));
    expect(trees.length).toBeGreaterThan(3);
    expect(trees.length).toBeLessThanOrEqual(13); // 4 corners x 3 + specimen
    const specimens = trees.filter((t) => t.scale >= 1.3);
    expect(specimens).toHaveLength(1);
    const corners = [
      [3, 3],
      [37, 3],
      [37, 37],
      [3, 37],
    ];
    for (const t of trees) {
      if (t.scale >= 1.3) continue; // the off-centre specimen
      const [x, y] = toMeters(t);
      const dMin = Math.min(...corners.map(([cx, cy]) => Math.hypot(x - cx, y - cy)));
      expect(dMin).toBeLessThanOrEqual(10);
    }
  });

  it('paved_plaza places at most six trees along a single edge and keeps benches', () => {
    const placements = computeParkPlacements(
      { id: 'z-plaza', coordinates: squareRing(100) },
      NEIGHBORHOOD,
      'paved_plaza',
    );
    const trees = treesOf(placements);
    expect(trees.length).toBeGreaterThan(0);
    expect(trees.length).toBeLessThanOrEqual(6);
    // single row just inside ONE edge: the cross-edge coordinate is constant
    // (in the local metric frame the N-S edges of this square measure a hair
    // longer than the E-W ones, so the row may run along either axis)
    const pts = trees.map(toMeters);
    const spread = (vals: number[]) => Math.max(...vals) - Math.min(...vals);
    const xSpread = spread(pts.map(([x]) => x));
    const ySpread = spread(pts.map(([, y]) => y));
    expect(Math.min(xSpread, ySpread)).toBeLessThan(1e-4); // collinear
    for (const [x, y] of pts) {
      expect(Math.min(x, y, 100 - x, 100 - y)).toBeLessThanOrEqual(3); // hugging one edge
    }
    expect(placements.filter((p) => p.propId === 'bench').length).toBeGreaterThan(0);
  });

  it('buffer_edge builds a dense perimeter belt with a sparse interior', () => {
    const zone = { id: 'z-buffer', coordinates: squareRing(100) };
    const trees = treesOf(computeParkPlacements(zone, NEIGHBORHOOD, 'buffer_edge'));
    const edgeDist = (t: PropPlacement) => {
      const [x, y] = toMeters(t);
      return Math.min(x, y, 100 - x, 100 - y);
    };
    const belt = trees.filter((t) => edgeDist(t) <= 9); // double row at 2m + ~8m
    const interior = trees.filter((t) => edgeDist(t) > 9);
    expect(belt.length).toBeGreaterThanOrEqual(50);
    expect(interior.length).toBeLessThanOrEqual(6);
    expect(belt.length).toBeGreaterThan(interior.length * 5);
  });
});
