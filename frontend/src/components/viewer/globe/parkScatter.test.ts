import { describe, expect, it } from 'vitest';

import {
  computeParkPlacements,
  resolveContainedParkProgramAnchor,
  resolveParkRecipeForZone,
  PLANTING_STRUCTURES,
  type PropPlacement,
  type ParkPlacementExclusion,
} from './parkScatter';
import {
  BOTANICAL_GARDEN,
  JAPANESE_GARDEN,
  LINEAR_GREENWAY,
  NATURE_PLAY_AREA,
  NEIGHBORHOOD_PARK,
  PAVED_PLAZA,
  RESERVOIR_WATERSHED_PARK,
  SPORTS_FIELD_COMPLEX,
  STORMWATER_POND,
  URBAN_FOREST,
  URBAN_POCKET_PARK,
  resolveParkRecipe,
} from '@/data/parkKitRecipes';
import { pointInPolygon } from '@/utils/coordTransform';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import {
  CIVIC_FOUNTAIN_ASSEMBLY_SPEC,
  NEIGHBORHOOD_COMMUNITY_PROGRAM_ANCHORS,
} from './parkLegoFamilies';

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

function rectangleRing(widthM: number, depthM: number): number[][] {
  const dLng = widthM / M_PER_LON;
  const dLat = depthM / METERS_PER_DEG_LAT;
  return [
    [LNG, LAT],
    [LNG + dLng, LAT],
    [LNG + dLng, LAT + dLat],
    [LNG, LAT + dLat],
  ];
}

function rotatedRectangleLocal(widthM: number, depthM: number, angleDeg: number): number[][] {
  const angle = (angleDeg * Math.PI) / 180;
  const cos = Math.cos(angle);
  const sin = Math.sin(angle);
  return [
    [-widthM / 2, -depthM / 2],
    [widthM / 2, -depthM / 2],
    [widthM / 2, depthM / 2],
    [-widthM / 2, depthM / 2],
  ].map(([x, y]) => [x * cos - y * sin, x * sin + y * cos]);
}

function localRingToLngLat(local: number[][]): number[][] {
  return local.map(([x, y]) => [LNG + x / M_PER_LON, LAT + y / METERS_PER_DEG_LAT]);
}

function localBoundaryDistance(ring: number[][], point: { x: number; y: number }): number {
  return ring.reduce((best, start, index) => {
    const end = ring[(index + 1) % ring.length];
    const dx = end[0] - start[0];
    const dy = end[1] - start[1];
    const lengthSquared = dx * dx + dy * dy;
    const t = lengthSquared > 0
      ? Math.max(0, Math.min(1, ((point.x - start[0]) * dx + (point.y - start[1]) * dy) / lengthSquared))
      : 0;
    return Math.min(best, Math.hypot(
      point.x - (start[0] + dx * t),
      point.y - (start[1] + dy * t),
    ));
  }, Infinity);
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
  it('keeps complete tree and bench footprints out of completed drape pathways', () => {
    const exclusion: ParkPlacementExclusion = {
      points: [{ x: 0, y: -50 }, { x: 0, y: 50 }],
      widthM: 4,
      bufferM: 0.5,
    };
    const placements = computeParkPlacements(
      { id: 'path-clearance', coordinates: localRingToLngLat(rotatedRectangleLocal(100, 100, 0)) },
      NEIGHBORHOOD,
      'naturalistic_grove',
      undefined,
      [exclusion],
    );
    const local = placements.map((placement) => ({
      ...placement,
      x: (placement.lng - LNG) * M_PER_LON,
      y: (placement.lat - LAT) * METERS_PER_DEG_LAT,
    }));

    expect(local.filter(({ propId }) => propId === 'tree').length).toBeGreaterThan(0);
    expect(local.filter(({ propId }) => propId === 'tree')
      .every(({ x }) => Math.abs(x) >= 4.1)).toBe(true);
    expect(local.filter(({ propId }) => propId === 'bench')
      .every(({ x }) => Math.abs(x) >= 3.4)).toBe(true);
  });

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

  it('frames an urban pocket park with a restrained, distributed specimen canopy', () => {
    const trees = treesOf(computeParkPlacements(
      { id: 'pocket-frame', coordinates: squareRing(36) },
      URBAN_POCKET_PARK,
      'garden_courtyard',
    ));
    const quadrants = new Set(trees.map((tree) => {
      const [x, y] = toMeters(tree);
      return `${x < 18 ? 'west' : 'east'}-${y < 18 ? 'south' : 'north'}`;
    }));
    expect(trees.length).toBeGreaterThanOrEqual(3);
    expect(trees.length).toBeLessThanOrEqual(5);
    expect(quadrants.size).toBeGreaterThanOrEqual(3);
  });

  it('matches the render-scale canopy rhythm on a 60m by 37m pocket park', () => {
    const trees = treesOf(computeParkPlacements(
      { id: 'render-scale-pocket', coordinates: rectangleRing(60, 37) },
      URBAN_POCKET_PARK,
      'garden_courtyard',
    ));
    expect(trees.length).toBeGreaterThanOrEqual(6);
    expect(trees.length).toBeLessThanOrEqual(8);
  });

  it('makes the modern pocket variant a formal but still perimeter-only tree frame', () => {
    const zone = { id: 'pocket-variant-frame', coordinates: squareRing(40) };
    const rustic = treesOf(computeParkPlacements(zone, URBAN_POCKET_PARK, 'garden_courtyard'));
    const modern = treesOf(computeParkPlacements(zone, URBAN_POCKET_PARK, 'formal_quad'));
    expect(modern.length).toBeGreaterThanOrEqual(3);
    expect(modern.length).toBeLessThanOrEqual(rustic.length);
    expect(modern).not.toEqual(rustic);
    expect(modern.every((tree) => tree.scale === 1)).toBe(true);
    for (const tree of modern) {
      const [x, y] = toMeters(tree);
      expect(Math.min(x, y, 40 - x, 40 - y)).toBeLessThanOrEqual(4.3);
    }
  });

  it('gates the playground on area', () => {
    const small = computeParkPlacements({ id: 'z-small', coordinates: squareRing(45) }, NEIGHBORHOOD); // ~2000 m²
    const big = computeParkPlacements({ id: 'z-big', coordinates: squareRing(70) }, NEIGHBORHOOD); // ~4900 m²
    expect(small.filter((p) => p.propId === 'playground')).toHaveLength(0);
    expect(big.filter((p) => p.propId === 'playground').length).toBeGreaterThan(0);
  });

  it('places executable neighborhood modules on the exact ground-guide anchors', () => {
    const placements = computeParkPlacements(
      { id: 'lego-program-anchors', coordinates: squareRing(100) },
      NEIGHBORHOOD,
      'active_recreation',
      NEIGHBORHOOD_COMMUNITY_PROGRAM_ANCHORS,
    );
    const playground = placements.filter((placement) => placement.propId === 'playground');
    const pavilion = placements.filter((placement) => placement.propId === 'pavilion');
    expect(playground).toHaveLength(NEIGHBORHOOD.playground!.instances);
    expect(pavilion).toHaveLength(1);
    const playgroundCenter = playground.map(toMeters).reduce(
      ([sumX, sumY], [x, y]) => [sumX + x, sumY + y],
      [0, 0],
    ).map((value) => value / playground.length);
    // Individual equipment pieces are scattered within the cluster radius;
    // their mean remains close to the authored x=.82, north-up y=.22 pad.
    expect(playgroundCenter[0]).toBeCloseTo(82, 4);
    expect(playgroundCenter[1]).toBeCloseTo(78, 4);
    const [pavilionX, pavilionY] = toMeters(pavilion[0]);
    expect(pavilionX).toBeCloseTo(77, 4);
    expect(pavilionY).toBeCloseTo(42, 4);
  });

  it('rotates authored program anchors with a valid oriented parcel', () => {
    const local = rotatedRectangleLocal(100, 80, 45);
    const placements = computeParkPlacements(
      { id: 'rotated-lego-program', coordinates: localRingToLngLat(local) },
      NEIGHBORHOOD,
      'active_recreation',
      NEIGHBORHOOD_COMMUNITY_PROGRAM_ANCHORS,
    );
    expect(placements.filter((placement) => placement.propId === 'playground'))
      .toHaveLength(NEIGHBORHOOD.playground!.instances);
    expect(placements.filter((placement) => placement.propId === 'pavilion')).toHaveLength(1);

    const playgroundAnchor = resolveContainedParkProgramAnchor(
      local,
      NEIGHBORHOOD_COMMUNITY_PROGRAM_ANCHORS.playground!,
      NEIGHBORHOOD.playground!.clearance_m,
    );
    expect(playgroundAnchor).not.toBeNull();
    expect(localBoundaryDistance(local, playgroundAnchor!))
      .toBeGreaterThanOrEqual(NEIGHBORHOOD.playground!.clearance_m - 1e-6);
    expect(playgroundAnchor!.yawRad).toBeCloseTo(Math.PI / 4, 5);
  });

  it('fits the metric civic fountain clearance disc inside its minimum rotated envelope', () => {
    const local = rotatedRectangleLocal(40, 35, 33);
    const anchor = resolveContainedParkProgramAnchor(
      local,
      [0.5, 0.5],
      CIVIC_FOUNTAIN_ASSEMBLY_SPEC.wholeElementClearanceM,
    );
    expect(anchor).not.toBeNull();
    expect(localBoundaryDistance(local, anchor!))
      .toBeGreaterThanOrEqual(CIVIC_FOUNTAIN_ASSEMBLY_SPEC.wholeElementClearanceM - 1e-6);
    expect(CIVIC_FOUNTAIN_ASSEMBLY_SPEC.outerRadiusM)
      .toBeLessThan(CIVIC_FOUNTAIN_ASSEMBLY_SPEC.wholeElementClearanceM);
  });

  it('omits an anchored playground as one whole element when no safety disc can fit', () => {
    const placements = computeParkPlacements(
      { id: 'lego-program-too-narrow', coordinates: rectangleRing(18, 200) },
      NEIGHBORHOOD,
      'active_recreation',
      NEIGHBORHOOD_COMMUNITY_PROGRAM_ANCHORS,
    );
    expect(placements.filter((placement) => placement.propId === 'playground')).toHaveLength(0);
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

  it('japanese_stroll_garden leaves the pond core free of trees', () => {
    const trees = treesOf(computeParkPlacements(
      { id: 'z-japanese', coordinates: squareRing(60) },
      NEIGHBORHOOD,
      'japanese_stroll_garden',
    ));
    expect(trees.length).toBeGreaterThan(3);
    expect(trees.some((tree) => tree.scale >= 1.3)).toBe(false);
    for (const tree of trees) {
      const [x, y] = toMeters(tree);
      expect(Math.hypot(x - 30, y - 30)).toBeGreaterThan(12);
    }
  });

  it('sports_perimeter keeps the programmed field interior clear', () => {
    const trees = treesOf(computeParkPlacements(
      { id: 'z-sports', coordinates: squareRing(100) },
      NEIGHBORHOOD,
      'sports_perimeter',
    ));
    expect(trees.length).toBeGreaterThan(12);
    for (const tree of trees) {
      const [x, y] = toMeters(tree);
      expect(Math.min(x, y, 100 - x, 100 - y)).toBeLessThanOrEqual(3.6);
    }
  });

  it('reservoir_perimeter keeps the programmed lake interior clear', () => {
    const trees = treesOf(computeParkPlacements(
      { id: 'z-reservoir', coordinates: squareRing(100) },
      RESERVOIR_WATERSHED_PARK,
      'reservoir_perimeter',
    ));
    expect(trees.length).toBeGreaterThan(8);
    for (const tree of trees) {
      const [x, y] = toMeters(tree);
      expect(Math.min(x, y, 100 - x, 100 - y)).toBeLessThanOrEqual(4.6);
    }
  });

  it('botanical_collection keeps trees out of the path, conservatory and collection beds', () => {
    const trees = treesOf(computeParkPlacements(
      { id: 'z-botanical', coordinates: squareRing(100) },
      BOTANICAL_GARDEN,
      'botanical_collection',
    ));
    expect(trees.length).toBeGreaterThan(12);
    for (const tree of trees) {
      const [x, y] = toMeters(tree);

      // 24 x 14 m conservatory at normalized (0.22, 0.24 from north),
      // including the live-canopy safety offset.
      expect(Math.abs(x - 22) <= 14.5 && Math.abs(y - 76) <= 9.5).toBe(false);

      const beds = [
        { x: 48, y: 65, rx: 16.5, ry: 10.5 },
        { x: 70, y: 34, rx: 17.5, ry: 11 },
        { x: 35, y: 28, rx: 15.5, ry: 9.5 },
      ];
      for (const bed of beds) {
        expect(((x - bed.x) / bed.rx) ** 2 + ((y - bed.y) / bed.ry) ** 2).toBeGreaterThan(1);
      }

      const loopRadius = Math.hypot((x - 50) / 41, (y - 50) / 33);
      expect(Math.abs(loopRadius - 1) * 33).toBeGreaterThanOrEqual(4 - 1e-6);
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

describe('resolveParkRecipeForZone', () => {
  const bigRing = squareRing(65); // ~4,225 m2 — above playground gate (3,000)
  const smallRing = squareRing(35); // ~1,225 m2 — below pocket band (1,500)

  it('plan open_space park without an id falls back by area to the neighborhood recipe', () => {
    const recipe = resolveParkRecipeForZone({
      properties: { _plan_role: 'open_space' },
      coordinates: bigRing,
    });
    expect(recipe).toBe(NEIGHBORHOOD_PARK);
    // LEGACY furniture (no planting_structure): big park gets a playground
    const placements = computeParkPlacements({ id: 'z-plan-park', coordinates: bigRing }, recipe);
    expect(placements.some((p) => p.propId === 'playground')).toBe(true);
    expect(placements.some((p) => p.propId === 'bench')).toBe(true);
  });

  it('small plan open_space park bands to the pocket recipe (benches only)', () => {
    const recipe = resolveParkRecipeForZone({
      properties: { _plan_role: 'open_space' },
      coordinates: smallRing,
    });
    expect(recipe).toBe(URBAN_POCKET_PARK);
    const placements = computeParkPlacements({ id: 'z-plan-pocket', coordinates: smallRing }, recipe);
    expect(placements.some((p) => p.propId === 'playground')).toBe(false);
    expect(placements.some((p) => p.propId === 'bench')).toBe(true);
  });

  it('formal planting structure still suppresses the playground on a big plan park', () => {
    const recipe = resolveParkRecipeForZone({
      properties: { _plan_role: 'open_space', planting_structure: 'formal_allee' },
      coordinates: bigRing,
    });
    const placements = computeParkPlacements(
      { id: 'z-plan-formal', coordinates: bigRing },
      recipe,
      'formal_allee',
    );
    expect(placements.some((p) => p.propId === 'playground')).toBe(false);
    expect(placements.some((p) => p.propId === 'bench')).toBe(true);
  });

  it('courtyards get the pocket recipe regardless of size', () => {
    const recipe = resolveParkRecipeForZone({
      properties: { _plan_role: 'courtyard' },
      coordinates: bigRing,
    });
    expect(recipe).toBe(URBAN_POCKET_PARK);
  });

  it('an explicit archetype id beats the plan-role fallback', () => {
    const recipe = resolveParkRecipeForZone({
      properties: { _plan_role: 'open_space', green_space_archetype_id: 'urban_pocket_park' },
      coordinates: bigRing,
    });
    expect(recipe).toBe(URBAN_POCKET_PARK);
  });

  it('catalog cricket parks use the sparse sports recipe', () => {
    const recipe = resolveParkRecipeForZone({
      properties: { green_space_archetype_id: 'cricket_pitch_oval' },
      coordinates: bigRing,
    });
    expect(recipe).toBe(SPORTS_FIELD_COMPLEX);
    expect(recipe.trees.perHectare).toBe(8);
    expect(recipe.playground).toBeUndefined();
    expect(recipe.pavilion).toBeUndefined();
  });

  it('uses the canonical nested family selection ahead of stale legacy fields', () => {
    const recipe = resolveParkRecipeForZone({
      properties: {
        green_space_archetype_id: 'urban_pocket_park',
        public_realm_lego: {
          schema_version: 1,
          kind: 'park',
          generator: 'park_kit',
          family_id: 'park_neighborhood_community',
          family_version: 1,
          archetype_id: 'neighborhood_park',
          variant_id: 'neighborhood_park_v0',
          planting_structure: 'active_recreation',
          appearance_kit_id: 'rustic_timber_gravel_v1',
          catalog_fingerprint: 'a'.repeat(64),
          capability_fingerprint: 'b'.repeat(64),
          recipe_hash: 'c'.repeat(64),
        },
      },
      coordinates: bigRing,
    });
    expect(recipe).toBe(NEIGHBORHOOD_PARK);
  });

  it('the Japanese garden pilot resolves to a restrained garden kit', () => {
    const recipe = resolveParkRecipeForZone({
      properties: { green_space_archetype_id: 'japanese_garden' },
      coordinates: bigRing,
    });
    const placements = computeParkPlacements({ id: 'z-hand', coordinates: bigRing }, recipe);
    expect(placements.some((p) => p.propId === 'tree')).toBe(true);
    expect(placements.some((p) => p.propId === 'bench')).toBe(true);
    expect(placements.some((p) => p.propId === 'playground')).toBe(false);
  });

  it('the reservoir pilot resolves to a sparse shoreline kit', () => {
    const recipe = resolveParkRecipeForZone({
      properties: { green_space_archetype_id: 'reservoir_watershed_park' },
      coordinates: bigRing,
    });
    expect(recipe).toBe(RESERVOIR_WATERSHED_PARK);
    expect(recipe.playground).toBeUndefined();
    expect(recipe.pavilion).toBeUndefined();
  });

  it('resolves recurring planner ground archetypes without generic playground fallback', () => {
    expect(resolveParkRecipe('linear_park_greenway')).toBe(LINEAR_GREENWAY);
    expect(resolveParkRecipe('stormwater_retention_pond')).toBe(STORMWATER_POND);
    expect(resolveParkRecipe('formal_civic_plaza')).toBe(PAVED_PLAZA);
    expect(resolveParkRecipe('fountain_water_feature')).toBe(PAVED_PLAZA);
    expect(LINEAR_GREENWAY.playground).toBeUndefined();
    expect(STORMWATER_POND.benches).toBeUndefined();
  });

  it('resolves all five same-geography park alternatives to distinct authored recipes', () => {
    expect(resolveParkRecipe('sports_field_complex')).toBe(SPORTS_FIELD_COMPLEX);
    expect(resolveParkRecipe('urban_forest')).toBe(URBAN_FOREST);
    expect(resolveParkRecipe('botanical_garden')).toBe(BOTANICAL_GARDEN);
    expect(resolveParkRecipe('japanese_garden')).toBe(JAPANESE_GARDEN);
    expect(resolveParkRecipe('nature_play_area')).toBe(NATURE_PLAY_AREA);
    expect(URBAN_FOREST.trees.perHectare).toBeGreaterThan(BOTANICAL_GARDEN.trees.perHectare);
    expect(SPORTS_FIELD_COMPLEX.trees.perHectare).toBeLessThan(NATURE_PLAY_AREA.trees.perHectare);
  });

  it('gives the toolbar plaza type a restrained hardscape recipe', () => {
    const recipe = resolveParkRecipeForZone({
      zone_type: 'parking',
      properties: {},
      coordinates: bigRing,
    });
    expect(recipe).toBe(PAVED_PLAZA);
    const placements = computeParkPlacements(
      { id: 'z-plaza', coordinates: bigRing },
      recipe,
      'paved_plaza',
    );
    expect(placements.some((p) => p.propId === 'bench')).toBe(true);
    expect(placements.some((p) => p.propId === 'playground')).toBe(false);
  });
});

describe('broadened recipe aliases', () => {
  it('playground archetypes resolve to the equipment-first recipe', () => {
    const recipe = resolveParkRecipe('playground_adventure');
    expect(recipe.playground?.minArea_m2).toBe(800);
    // a modest 1,000 m2 playground lot gets equipment
    const ring = squareRing(32);
    const placements = computeParkPlacements({ id: 'z-playground', coordinates: ring }, recipe);
    expect(placements.some((p) => p.propId === 'playground')).toBe(true);
  });

  it('inclusive_playground and regional/olmsted parks stop falling through to trees-only', () => {
    expect(resolveParkRecipe('inclusive_playground').playground).toBeDefined();
    expect(resolveParkRecipe('regional_park').playground).toBeDefined();
    expect(resolveParkRecipe('picturesque_olmsted_park').playground).toBeDefined();
  });

  it('newyork_pocket_park matches the pocket recipe via the pocket_park alias', () => {
    expect(resolveParkRecipe('newyork_pocket_park')).toBe(URBAN_POCKET_PARK);
  });
});
