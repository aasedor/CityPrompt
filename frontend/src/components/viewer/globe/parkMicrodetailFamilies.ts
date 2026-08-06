/**
 * Pure, deterministic placement for the small elements that make a park read
 * as an authored place rather than a green polygon. Coordinates are local ENU
 * metres; the render layer owns conversion from/to lng/lat and terrain drape.
 *
 * Every returned footprint is fully contained by the supplied park boundary,
 * clears circulation/water/fixed-program guides, and clears both primary park
 * objects and its microdetail peers. The hard budget is deliberately shared by
 * all families so a large district park cannot create an unbounded draw load.
 */

import { seededRandom } from '@/utils/seededRandom';
import type { ParkLegoFamilyId } from './parkLegoFamilies';

export const MAX_PARK_MICRODETAIL_PLACEMENTS = 96 as const;
export const MAX_PARK_MICRODETAIL_STATIONS_PER_SOURCE = 160 as const;
export const MAX_PARK_MICRODETAIL_CANDIDATES_PER_TIER = 384 as const;
export const MAX_PARK_MICRODETAIL_CANDIDATES_PER_KIND = 768 as const;
export const MAX_PARK_MICRODETAIL_ELEMENTS_PER_PLACEMENT = 16 as const;

export type ParkMicrodetailKind =
  | 'shrub'
  | 'perennial'
  | 'ornamental_grass'
  | 'reed'
  | 'boulder'
  | 'riprap'
  | 'light'
  | 'bin'
  | 'bike_rack'
  | 'bollard'
  | 'picnic_table'
  | 'drinking_fountain'
  | 'tree_grate';

export interface ParkMicrodetailPoint {
  x: number;
  y: number;
}

export type ParkMicrodetailGuideKind = 'circulation' | 'water' | 'fixed_program';

/** Interpret fitted 2D program guides before candidate generation. Keeping
 * this policy pure makes infrastructure-clear zones independently testable. */
export function resolveParkMicrodetailGuideKind(
  familyId: ParkLegoFamilyId,
  authoredGuideKind: string,
): ParkMicrodetailGuideKind | null {
  if (familyId === 'park_water_ecology' || familyId === 'park_constructed_wetland_boardwalk_v0') {
    return authoredGuideKind === 'ellipse' ? 'water' : 'fixed_program';
  }
  if (['line', 'axis', 'polyline', 'path_loop'].includes(authoredGuideKind)) {
    return 'circulation';
  }
  if (['soccer_field', 'tennis_court', 'track', 'basketball_court'].includes(authoredGuideKind)) {
    return 'fixed_program';
  }
  if (familyId === 'park_civic_plaza' && authoredGuideKind === 'ellipse') {
    return 'fixed_program';
  }
  return null;
}

export interface ParkMicrodetailGuide {
  kind: ParkMicrodetailGuideKind;
  /** Local-metre polyline or polygon vertices. */
  points: readonly ParkMicrodetailPoint[];
  closed?: boolean;
  /** Closed guides default to area geometry for water/fixed programs. */
  isArea?: boolean;
  /** Physical stroke/corridor width for line geometry. */
  widthM?: number;
  /** Clearance outside the authored geometry, before prop radius is added. */
  bufferM?: number;
}

export type ParkMicrodetailPrimaryKind =
  | 'tree'
  | 'bench'
  | 'playground'
  | 'pavilion'
  | 'fixed_program'
  | 'other';

export interface ParkMicrodetailPrimaryPlacement extends ParkMicrodetailPoint {
  footprintRadiusM: number;
  kind?: ParkMicrodetailPrimaryKind;
}

export interface ParkMicrodetailFamilyInput {
  zoneId: string;
  familyId: ParkLegoFamilyId;
  /** Simple park boundary in local ENU metres; repeated closing point is OK. */
  boundary: readonly ParkMicrodetailPoint[];
  guides?: readonly ParkMicrodetailGuide[];
  primaryPlacements?: readonly ParkMicrodetailPrimaryPlacement[];
  /** Lower values are useful for low-detail devices; values above 96 clamp. */
  maxPlacements?: number;
  /** Extra gap between peer/primary footprints. Defaults to 0.25 m. */
  collisionClearanceM?: number;
}

export interface ParkMicrodetailPlacement extends ParkMicrodetailPoint {
  id: string;
  familyId: ParkLegoFamilyId;
  kind: ParkMicrodetailKind;
  yawRad: number;
  /** Conservative radius of the complete rendered, scaled assembly. */
  footprintRadiusM: number;
  scale: number;
  /** Number of stems/stones represented by a procedural clump. */
  elementCount: number;
  /** Present when a grate intentionally shares the centre of a primary tree. */
  sourcePrimaryIndex?: number;
}

interface Candidate extends ParkMicrodetailPoint {
  yawRad: number;
  sourcePrimaryIndex?: number;
}

interface Target {
  kind: ParkMicrodetailKind;
  count: number;
}

const DEFAULT_GUIDE_BUFFERS: Record<ParkMicrodetailGuideKind, number> = {
  circulation: 0.35,
  water: 0.9,
  fixed_program: 1.1,
};

const FOOTPRINT_RADIUS_M: Record<ParkMicrodetailKind, number> = {
  shrub: 0.9,
  perennial: 0.62,
  ornamental_grass: 0.68,
  reed: 0.52,
  boulder: 0.82,
  riprap: 0.72,
  light: 0.34,
  bin: 0.4,
  bike_rack: 0.78,
  bollard: 0.22,
  picnic_table: 1.42,
  drinking_fountain: 0.56,
  tree_grate: 1.05,
};

const PLANTING_KINDS = new Set<ParkMicrodetailKind>([
  'shrub',
  'perennial',
  'ornamental_grass',
  'reed',
]);

const CLUSTERED_KINDS = new Set<ParkMicrodetailKind>([
  'shrub',
  'perennial',
  'ornamental_grass',
  'reed',
  'riprap',
]);

function finitePoint(point: ParkMicrodetailPoint): boolean {
  return Number.isFinite(point.x) && Number.isFinite(point.y);
}

function samePoint(first: ParkMicrodetailPoint, second: ParkMicrodetailPoint): boolean {
  return Math.abs(first.x - second.x) <= 1e-7 && Math.abs(first.y - second.y) <= 1e-7;
}

function cleanRing(points: readonly ParkMicrodetailPoint[]): ParkMicrodetailPoint[] {
  const ring = points.filter(finitePoint).map(({ x, y }) => ({ x, y }));
  if (ring.length > 2 && samePoint(ring[0], ring[ring.length - 1])) ring.pop();
  return ring;
}

function pointOnSegment(
  point: ParkMicrodetailPoint,
  start: ParkMicrodetailPoint,
  end: ParkMicrodetailPoint,
): boolean {
  const cross = (point.y - start.y) * (end.x - start.x)
    - (point.x - start.x) * (end.y - start.y);
  if (Math.abs(cross) > 1e-7) return false;
  const dot = (point.x - start.x) * (end.x - start.x)
    + (point.y - start.y) * (end.y - start.y);
  if (dot < -1e-7) return false;
  const lengthSquared = (end.x - start.x) ** 2 + (end.y - start.y) ** 2;
  return dot <= lengthSquared + 1e-7;
}

function pointInRing(point: ParkMicrodetailPoint, ring: readonly ParkMicrodetailPoint[]): boolean {
  if (ring.length < 3) return false;
  let inside = false;
  for (let index = 0, previous = ring.length - 1; index < ring.length; previous = index++) {
    if (pointOnSegment(point, ring[previous], ring[index])) return true;
    const current = ring[index];
    const prior = ring[previous];
    if ((current.y > point.y) !== (prior.y > point.y)
      && point.x < ((prior.x - current.x) * (point.y - current.y))
        / (prior.y - current.y) + current.x) {
      inside = !inside;
    }
  }
  return inside;
}

function distanceToSegment(
  point: ParkMicrodetailPoint,
  start: ParkMicrodetailPoint,
  end: ParkMicrodetailPoint,
): number {
  const dx = end.x - start.x;
  const dy = end.y - start.y;
  const lengthSquared = dx * dx + dy * dy;
  if (lengthSquared <= 1e-12) return Math.hypot(point.x - start.x, point.y - start.y);
  const ratio = Math.max(0, Math.min(1,
    ((point.x - start.x) * dx + (point.y - start.y) * dy) / lengthSquared));
  return Math.hypot(point.x - (start.x + dx * ratio), point.y - (start.y + dy * ratio));
}

function segmentsFor(
  points: readonly ParkMicrodetailPoint[],
  closed: boolean,
): Array<readonly [ParkMicrodetailPoint, ParkMicrodetailPoint]> {
  const segments: Array<readonly [ParkMicrodetailPoint, ParkMicrodetailPoint]> = [];
  for (let index = 1; index < points.length; index += 1) {
    segments.push([points[index - 1], points[index]]);
  }
  if (closed && points.length > 2) segments.push([points[points.length - 1], points[0]]);
  return segments;
}

function distanceToPolyline(
  point: ParkMicrodetailPoint,
  points: readonly ParkMicrodetailPoint[],
  closed: boolean,
): number {
  let distance = Infinity;
  for (const [start, end] of segmentsFor(points, closed)) {
    distance = Math.min(distance, distanceToSegment(point, start, end));
  }
  if (points.length === 1) return Math.hypot(point.x - points[0].x, point.y - points[0].y);
  return distance;
}

function polygonArea(ring: readonly ParkMicrodetailPoint[]): number {
  let twiceArea = 0;
  for (let index = 0; index < ring.length; index += 1) {
    const next = ring[(index + 1) % ring.length];
    twiceArea += ring[index].x * next.y - next.x * ring[index].y;
  }
  return Math.abs(twiceArea) / 2;
}

function polygonPerimeter(ring: readonly ParkMicrodetailPoint[]): number {
  return segmentsFor(ring, true).reduce(
    (sum, [start, end]) => sum + Math.hypot(end.x - start.x, end.y - start.y),
    0,
  );
}

function guideIsArea(guide: ParkMicrodetailGuide): boolean {
  return guide.isArea ?? (
    guide.closed === true && (guide.kind === 'water' || guide.kind === 'fixed_program')
  );
}

/** Public for focused geometry tests and future authoring previews. */
export function parkMicrodetailFootprintFits(
  point: ParkMicrodetailPoint,
  footprintRadiusM: number,
  boundary: readonly ParkMicrodetailPoint[],
  guides: readonly ParkMicrodetailGuide[] = [],
): boolean {
  const ring = cleanRing(boundary);
  if (ring.length < 3 || !pointInRing(point, ring)) return false;
  if (distanceToPolyline(point, ring, true) + 1e-7 < footprintRadiusM) return false;

  for (const guide of guides) {
    const points = guide.points.filter(finitePoint);
    if (points.length === 0) continue;
    const closed = guide.closed === true;
    const bufferM = Math.max(0, guide.bufferM ?? DEFAULT_GUIDE_BUFFERS[guide.kind]);
    const distance = distanceToPolyline(point, points, closed);
    if (guideIsArea(guide)) {
      if (points.length >= 3 && pointInRing(point, points)) return false;
      if (distance + 1e-7 < bufferM + footprintRadiusM) return false;
    } else {
      const halfWidthM = Math.max(0, guide.widthM ?? 0) / 2;
      if (distance + 1e-7 < halfWidthM + bufferM + footprintRadiusM) return false;
    }
  }
  return true;
}

function cappedCount(value: number, minimum: number, maximum: number): number {
  return Math.max(minimum, Math.min(maximum, Math.round(value)));
}

function familyTargets(
  familyId: ParkLegoFamilyId,
  areaM2: number,
  perimeterM: number,
  treeCount: number,
): Target[] {
  const target = (kind: ParkMicrodetailKind, count: number): Target => ({ kind, count });
  switch (familyId) {
    case 'park_basketball_court_v0':
      return [
        target('light', cappedCount(perimeterM / 34, 2, 4)),
        target('bin', cappedCount(areaM2 / 1800, 1, 2)),
        target('bike_rack', 1),
        target('picnic_table', cappedCount(areaM2 / 1400, 1, 3)),
        target('drinking_fountain', 1),
      ];
    case 'park_skate_archetype_v0':
    case 'park_inclusive_playground_v0':
    case 'park_dog_archetype_v0':
    case 'park_splash_pad_v0':
    case 'park_community_garden_v0':
    case 'park_tennis_cluster_v0':
    case 'park_caged_soccer_v0':
    case 'park_athletics_fields_v0':
    case 'park_nature_play_v0':
    case 'park_pump_track_v0':
    case 'park_outdoor_fitness_v0':
    case 'park_memorial_garden_v0':
    case 'park_pickleball_community_v1':
    case 'park_track_oval_school_v2':
    case 'park_baseball_club_hub_v1':
    case 'park_cricket_village_green_v0':
    case 'park_sports_complex_tournament_v0':
    case 'park_playground_adventure_v0':
      // Benches, grass edge and all fixed objects belong to the exact
      // archetype kit. Generic microdetail would corrupt its authored layout.
      return [];
    case 'park_pocket_courtyard':
      return [
        target('shrub', cappedCount(areaM2 / 115, 3, 16)),
        target('perennial', cappedCount(areaM2 / 170, 2, 10)),
        target('light', cappedCount(perimeterM / 26, 2, 8)),
        target('bin', cappedCount(areaM2 / 650, 1, 3)),
        target('bike_rack', areaM2 >= 260 ? cappedCount(areaM2 / 950, 1, 3) : 0),
        target('bollard', cappedCount(perimeterM / 22, 3, 10)),
        target('tree_grate', Math.min(treeCount, 10)),
      ];
    case 'park_neighborhood_community':
      return [
        target('shrub', cappedCount(areaM2 / 175, 4, 20)),
        target('perennial', cappedCount(areaM2 / 420, 2, 8)),
        target('ornamental_grass', cappedCount(areaM2 / 235, 3, 16)),
        target('boulder', cappedCount(areaM2 / 720, 1, 6)),
        target('light', cappedCount(perimeterM / 32, 3, 12)),
        target('bin', cappedCount(areaM2 / 850, 2, 5)),
        target('bike_rack', cappedCount(areaM2 / 1500, 1, 4)),
        target('bollard', cappedCount(perimeterM / 38, 2, 8)),
        target('picnic_table', cappedCount(areaM2 / 720, 2, 8)),
        target('drinking_fountain', areaM2 >= 500 ? cappedCount(areaM2 / 2600, 1, 2) : 0),
      ];
    case 'park_civic_plaza':
      return [
        target('perennial', cappedCount(areaM2 / 260, 2, 12)),
        target('ornamental_grass', cappedCount(areaM2 / 420, 1, 8)),
        target('light', cappedCount(perimeterM / 24, 4, 14)),
        target('bin', cappedCount(areaM2 / 700, 2, 6)),
        target('bike_rack', cappedCount(areaM2 / 950, 2, 6)),
        target('bollard', cappedCount(perimeterM / 16, 6, 18)),
        target('tree_grate', Math.min(treeCount, 16)),
      ];
    case 'park_linear_greenway':
      return [
        target('shrub', cappedCount(areaM2 / 225, 4, 18)),
        target('ornamental_grass', cappedCount(areaM2 / 165, 5, 24)),
        target('boulder', cappedCount(areaM2 / 650, 2, 8)),
        target('light', cappedCount(perimeterM / 34, 3, 14)),
        target('bin', cappedCount(areaM2 / 900, 2, 5)),
        target('bike_rack', cappedCount(areaM2 / 1450, 1, 4)),
        target('bollard', cappedCount(perimeterM / 28, 4, 12)),
        target('picnic_table', cappedCount(areaM2 / 1200, 1, 5)),
        target('drinking_fountain', areaM2 >= 1000 ? cappedCount(areaM2 / 4200, 1, 2) : 0),
      ];
    case 'park_water_ecology':
      return [
        target('reed', cappedCount(areaM2 / 110, 8, 32)),
        target('ornamental_grass', cappedCount(areaM2 / 240, 4, 18)),
        target('shrub', cappedCount(areaM2 / 440, 2, 10)),
        target('riprap', cappedCount(perimeterM / 22, 4, 16)),
        target('boulder', cappedCount(areaM2 / 700, 2, 8)),
        target('bollard', cappedCount(perimeterM / 55, 2, 8)),
      ];
    case 'park_cultural_gardens':
      return [
        target('shrub', cappedCount(areaM2 / 180, 6, 24)),
        target('perennial', cappedCount(areaM2 / 150, 8, 28)),
        target('ornamental_grass', cappedCount(areaM2 / 260, 3, 14)),
        target('boulder', cappedCount(areaM2 / 900, 1, 6)),
        target('bin', cappedCount(areaM2 / 1800, 1, 3)),
      ];
    case 'park_urban_forest':
      return [
        target('shrub', cappedCount(areaM2 / 240, 8, 28)),
        target('ornamental_grass', cappedCount(areaM2 / 360, 4, 18)),
        target('boulder', cappedCount(areaM2 / 1200, 2, 8)),
        target('bin', cappedCount(areaM2 / 4200, 1, 3)),
      ];
    case 'park_amphitheater_lawn_v0':
      return [
        target('light', cappedCount(perimeterM / 34, 3, 10)),
        target('bin', cappedCount(areaM2 / 1600, 1, 4)),
        target('bollard', cappedCount(perimeterM / 42, 2, 8)),
      ];
    case 'park_disc_golf_wooded_v0':
      return [target('shrub', 18), target('ornamental_grass', 10), target('boulder', 8), target('bin', 3), target('drinking_fountain', 1)];
    case 'park_bocce_piazza_v0':
      return [target('perennial', 8), target('light', 4), target('bin', 2), target('bike_rack', 1)];
    case 'park_climbing_competition_v0':
      return [target('light', 5), target('bin', 2), target('bike_rack', 2), target('bollard', 5)];
    case 'park_mini_golf_classic_v0':
      return [target('shrub', 12), target('perennial', 10), target('light', 6), target('bin', 2)];
    case 'park_beach_volleyball_competition_v0':
      return [target('light', 4), target('bin', 2), target('bike_rack', 1), target('drinking_fountain', 1)];
    case 'park_pollinator_prairie_v0':
      return [target('perennial', 28), target('ornamental_grass', 28), target('shrub', 8), target('boulder', 4)];
    case 'park_orchard_heritage_v0':
      return [target('perennial', 16), target('ornamental_grass', 12), target('picnic_table', 4), target('bin', 2), target('drinking_fountain', 1)];
    case 'park_bioswale_streetside_v0':
      return [target('reed', 24), target('ornamental_grass', 22), target('perennial', 14), target('riprap', 10), target('bollard', 6)];
    case 'park_sculpture_museum_court_v0':
      return [target('ornamental_grass', 14), target('perennial', 10), target('light', 7), target('bin', 2)];
    case 'park_labyrinth_classical_v0':
      return [target('shrub', 14), target('perennial', 8), target('light', 4), target('bin', 1)];
    case 'park_ice_rink_multipurpose_v3':
      return [target('light', 4), target('bollard', 6), target('bin', 2), target('bike_rack', 2)];
    case 'park_kayak_river_launch_v0':
      return [target('shrub', 12), target('ornamental_grass', 14), target('riprap', 10), target('picnic_table', 2), target('bollard', 4)];
    case 'park_tidal_marsh_cordgrass_v0':
      return [target('reed', 32), target('ornamental_grass', 24), target('shrub', 5), target('riprap', 6)];
    case 'park_cinema_lawn_projection_v1':
      return [target('light', 4), target('bollard', 6), target('bin', 2), target('bike_rack', 2)];
    case 'park_food_truck_permanent_v1':
      return [target('perennial', 10), target('ornamental_grass', 12), target('light', 8), target('bin', 4), target('bike_rack', 3)];
    case 'park_great_lawn_v2':
      return [target('shrub', 16), target('ornamental_grass', 12), target('picnic_table', 4), target('bin', 4), target('drinking_fountain', 2)];
    case 'park_campus_meadow_quad_v0':
      return [target('perennial', 24), target('ornamental_grass', 24), target('boulder', 12), target('picnic_table', 3), target('bike_rack', 4)];
    case 'park_urban_beach_family_v2':
      return [target('ornamental_grass', 10), target('picnic_table', 5), target('bin', 3), target('bike_rack', 2), target('drinking_fountain', 2)];
    case 'park_velodrome_open_air_v0':
      return [target('light', 8), target('bollard', 6), target('bin', 3), target('bike_rack', 6), target('drinking_fountain', 2)];
    case 'park_mtb_skills_dirt_v2':
      return [target('boulder', 12), target('riprap', 8), target('picnic_table', 3), target('bin', 2), target('bike_rack', 4), target('drinking_fountain', 1)];
    case 'park_regional_english_landscape_v0':
      return [target('shrub', 18), target('perennial', 10), target('boulder', 8), target('picnic_table', 5), target('bin', 4), target('drinking_fountain', 2)];
    case 'park_beer_garden_munich_v0':
      return [target('light', 10), target('bin', 4), target('bike_rack', 4), target('ornamental_grass', 8)];
    case 'park_sunken_courtyard_v0':
      return [target('shrub', 12), target('perennial', 8), target('light', 6), target('bin', 2)];
    case 'park_terraced_cascade_v3':
      return [target('shrub', 16), target('ornamental_grass', 18), target('light', 8), target('bin', 3)];
    case 'park_market_festival_lawn_v1':
      return [target('light', 8), target('bollard', 12), target('bin', 6), target('bike_rack', 5), target('drinking_fountain', 2)];
    case 'park_boardwalk_maritime_v0':
      return [target('ornamental_grass', 18), target('light', 10), target('bollard', 10), target('bin', 4), target('drinking_fountain', 2)];
    case 'park_fountain_formal_pool_v1':
      return [target('shrub', 16), target('perennial', 10), target('light', 8), target('bin', 2)];
    case 'park_natural_swimming_pond_v0':
      return [target('reed', 24), target('ornamental_grass', 16), target('riprap', 12), target('picnic_table', 4), target('bin', 3), target('drinking_fountain', 2)];
    case 'park_nature_preserve_prairie_v1':
      return [target('ornamental_grass', 30), target('perennial', 24), target('shrub', 8), target('boulder', 6)];
    case 'park_riverfront_lake_beach_v1':
      return [target('ornamental_grass', 14), target('picnic_table', 6), target('bike_rack', 4), target('bin', 4), target('drinking_fountain', 2)];
    case 'park_reclaimed_wharf_v0':
      return [target('ornamental_grass', 18), target('light', 8), target('bin', 4), target('bike_rack', 3), target('bollard', 8)];
    case 'park_quarry_tier_cascade_v2':
      return [target('shrub', 18), target('perennial', 18), target('ornamental_grass', 12), target('light', 6), target('bin', 3)];
    case 'park_estate_oak_picnic_v1':
      return [target('ornamental_grass', 8), target('bin', 4), target('drinking_fountain', 2)];
    case 'park_constructed_wetland_boardwalk_v0':
      return [target('reed', 32), target('ornamental_grass', 22), target('riprap', 10), target('bin', 3)];
    case 'park_academic_planted_court_v0':
      return [target('perennial', 14), target('ornamental_grass', 16), target('light', 6), target('bin', 2), target('bike_rack', 2)];
    case 'park_campus_green_spine_v0':
      return [target('perennial', 22), target('ornamental_grass', 24), target('light', 10), target('bin', 4), target('bike_rack', 5)];
    case 'park_botanical_rose_garden_v3':
      return [target('shrub', 18), target('perennial', 28), target('light', 6), target('bin', 3)];
    case 'park_research_arboretum_v0':
      return [target('shrub', 12), target('perennial', 16), target('boulder', 8), target('bin', 4), target('drinking_fountain', 2)];
    case 'park_rewilding_reforestation_v1':
      return [target('shrub', 24), target('perennial', 18), target('ornamental_grass', 20), target('boulder', 8)];
    case 'park_stormwater_arid_channel_v3':
      return [target('ornamental_grass', 24), target('boulder', 18), target('riprap', 16), target('bin', 3), target('drinking_fountain', 2)];
    case 'park_urban_pocket_rustic_v0':
      return [target('perennial', 18), target('ornamental_grass', 12), target('boulder', 6), target('bin', 1)];
    case 'park_neighborhood_contemporary_v3':
      return [target('perennial', 18), target('ornamental_grass', 20), target('light', 6), target('bin', 3), target('bike_rack', 3)];
    case 'park_cemetery_classical_v0':
      return [target('shrub', 18), target('perennial', 10), target('light', 6), target('bin', 2)];
    case 'park_courtyard_linear_water_v1':
      return [target('ornamental_grass', 14), target('perennial', 12), target('light', 5), target('bollard', 6), target('bike_rack', 2)];
    case 'park_parklet_sf_timber_v1':
      return [target('shrub', 6), target('perennial', 8), target('bollard', 2), target('bin', 1)];
    case 'park_french_parterre_axis_v1':
      return [target('shrub', 24), target('perennial', 20), target('light', 8), target('bin', 3)];
    case 'park_london_railed_square_v1':
      return [target('shrub', 18), target('perennial', 14), target('light', 6), target('bin', 3)];
    case 'park_halifax_rose_bandstand_v0':
      return [target('shrub', 20), target('perennial', 28), target('light', 8), target('bin', 3), target('drinking_fountain', 1)];
    case 'park_olmsted_multilandscape_v3':
      return [target('shrub', 26), target('perennial', 18), target('boulder', 10), target('picnic_table', 4), target('bin', 5), target('drinking_fountain', 2)];
    case 'park_hilltop_viewpoint_v3':
      return [target('shrub', 18), target('boulder', 14), target('riprap', 10), target('bin', 3), target('drinking_fountain', 2)];
    case 'park_amsterdam_hofje_garden_v0':
      return [target('shrub', 12), target('perennial', 18), target('light', 2), target('bin', 1)];
    case 'park_amsterdam_plein_v0':
      return [target('light', 8), target('bike_rack', 10), target('bin', 4), target('bollard', 8)];
    case 'park_amsterdam_vondelpark_pavilion_v3':
      return [target('shrub', 22), target('perennial', 16), target('boulder', 6), target('picnic_table', 4), target('bin', 4), target('drinking_fountain', 2)];
    case 'park_barcelona_pati_green_v0':
      return [target('shrub', 14), target('perennial', 20), target('light', 4), target('bin', 2), target('drinking_fountain', 1)];
    case 'park_barcelona_xamfra_corner_v2':
      return [target('light', 5), target('bike_rack', 4), target('bin', 2), target('bollard', 6)];
    case 'park_barcelona_superilla_green_v1':
      return [target('shrub', 16), target('perennial', 18), target('light', 8), target('bike_rack', 8), target('bin', 5), target('bollard', 10)];
    case 'park_calgary_prairie_market_v1':
      return [target('ornamental_grass', 24), target('perennial', 16), target('light', 8), target('bin', 5), target('bike_rack', 4)];
    case 'park_calgary_princes_island_festival_v0':
      return [target('reed', 18), target('ornamental_grass', 20), target('picnic_table', 6), target('bin', 5), target('drinking_fountain', 2)];
    case 'park_montreal_mount_royal_grove_v2':
      return [target('shrub', 24), target('boulder', 16), target('riprap', 12), target('bin', 4), target('drinking_fountain', 2)];
    case 'park_montreal_neighbourhood_square_v3':
      return [target('shrub', 16), target('perennial', 18), target('light', 6), target('bin', 3), target('bike_rack', 3)];
    case 'park_paris_place_royale_v2': return [target('light',8),target('bin',4),target('bollard',8),target('bike_rack',4)];
    case 'park_paris_square_tree_grid_v3': return [target('shrub',12),target('perennial',14),target('light',6),target('bin',3)];
    case 'park_london_circus_planted_v1': return [target('shrub',16),target('perennial',16),target('light',7),target('bike_rack',5),target('bin',3)];
    case 'park_newyork_pocket_water_v0': return [target('shrub',14),target('perennial',18),target('light',4),target('bin',2)];
    case 'park_newyork_community_greenhouse_v3': return [target('shrub',12),target('perennial',20),target('bin',2),target('drinking_fountain',1)];
    case 'park_vancouver_seawall_cycle_v2': return [target('light',10),target('bike_rack',8),target('bin',6),target('drinking_fountain',2),target('bollard',8)];
    case 'park_vancouver_beach_pavilion_v0': return [target('ornamental_grass',20),target('shrub',14),target('bike_rack',6),target('bin',5),target('drinking_fountain',2)];
    case 'park_toronto_ravine_creek_v1': return [target('shrub',24),target('boulder',14),target('riprap',12),target('bin',3)];
    case 'park_toronto_urban_market_v1': return [target('ornamental_grass',16),target('light',8),target('bike_rack',6),target('bin',4),target('bollard',8)];
    case 'park_halifax_coastal_fog_path_v2': return [target('shrub',22),target('boulder',16),target('riprap',12),target('bin',3)];
    case 'park_city_hall_modernist_fountain_v2': return [target('light',10),target('bollard',10),target('bin',4),target('bike_rack',4)];
    case 'park_cathedral_courtyard_fountain_v3': return [target('shrub',12),target('light',8),target('bin',3)];
    case 'park_cultural_museum_terrace_v0': return [target('ornamental_grass',18),target('light',8),target('bollard',8),target('bike_rack',4)];
    case 'park_transit_green_civic_v2': return [target('ornamental_grass',20),target('light',10),target('bollard',12),target('bike_rack',8),target('bin',5)];
    case 'park_amphitheater_terraced_v0': return [target('light',8),target('bin',4),target('drinking_fountain',2)];
    case 'park_concert_timber_lawn_v2': return [target('shrub',16),target('light',8),target('bin',5),target('drinking_fountain',2)];
    case 'park_night_market_hawker_v0': return [target('light',16),target('bin',8),target('bollard',10),target('bike_rack',6)];
    case 'park_parade_national_mall_v3': return [target('light',12),target('bollard',10),target('bin',6)];
    case 'park_canal_ecological_wetland_v3': return [target('reed',28),target('shrub',18),target('boulder',10),target('riprap',14),target('bin',3)];
    case 'park_custom_biophilic_urban_v1': return [target('shrub',22),target('perennial',28),target('ornamental_grass',18),target('light',7),target('bin',4)];
    case 'park_rooftop_intensive_garden_v0': return [target('shrub',18),target('perennial',24),target('ornamental_grass',16),target('light',5),target('bin',2)];
    case 'park_community_healing_garden_v2': return [target('shrub',18),target('perennial',28),target('ornamental_grass',14),target('drinking_fountain',2),target('bin',3)];
    case 'park_greenbelt_rail_trail_v1': return [target('shrub',24),target('boulder',10),target('bike_rack',6),target('bin',5),target('drinking_fountain',2)];
    case 'park_foothill_heathland_trail_v2': return [target('shrub',18),target('boulder',22),target('riprap',12),target('bin',3)];
    case 'park_marina_pacific_dock_v2': return [target('bollard',14),target('light',10),target('bin',6),target('bike_rack',6)];
    case 'park_working_pier_brooklyn_park_v3': return [target('ornamental_grass',18),target('light',10),target('bin',6),target('bike_rack',6),target('bollard',12)];
    case 'park_floating_meadow_loop_v2': return [target('ornamental_grass',26),target('perennial',22),target('light',6),target('bin',4)];
    case 'park_lighthouse_pacific_headland_v2': return [target('shrub',22),target('boulder',20),target('riprap',12),target('bin',3)];
    case 'park_lake_edge_timber_deck_v2': return [target('ornamental_grass',20),target('light',10),target('bin',6),target('bike_rack',5),target('bollard',10)];
    case 'park_stormwater_natural_creek_v0': return [target('reed',28),target('shrub',22),target('boulder',14),target('riprap',16),target('bin',3)];
  }
}

function fitTargetsToBudget(targets: readonly Target[], budget: number): Target[] {
  const active = targets.filter(({ count }) => count > 0);
  if (active.length === 0 || budget <= 0) return [];
  if (active.length > budget) return active.slice(0, budget).map(({ kind }) => ({ kind, count: 1 }));
  const total = active.reduce((sum, { count }) => sum + count, 0);
  if (total <= budget) return active.map((entry) => ({ ...entry }));

  const remaining = budget - active.length;
  const extraTotal = active.reduce((sum, { count }) => sum + count - 1, 0);
  const scaled = active.map((entry, index) => {
    const exact = extraTotal > 0 ? ((entry.count - 1) * remaining) / extraTotal : 0;
    return {
      kind: entry.kind,
      count: 1 + Math.floor(exact),
      fraction: exact - Math.floor(exact),
      index,
    };
  });
  let left = budget - scaled.reduce((sum, { count }) => sum + count, 0);
  for (const entry of [...scaled].sort((a, b) => b.fraction - a.fraction || a.index - b.index)) {
    if (left <= 0) break;
    entry.count += 1;
    left -= 1;
  }
  return scaled.sort((a, b) => a.index - b.index).map(({ kind, count }) => ({ kind, count }));
}

function shuffle<T>(values: T[], random: () => number): T[] {
  for (let index = values.length - 1; index > 0; index -= 1) {
    const swapIndex = Math.floor(random() * (index + 1));
    [values[index], values[swapIndex]] = [values[swapIndex], values[index]];
  }
  return values;
}

export function boundedParkMicrodetailStationCount(totalLengthM: number, spacingM: number): number {
  if (!Number.isFinite(totalLengthM) || totalLengthM <= 0) return 0;
  return Math.min(
    MAX_PARK_MICRODETAIL_STATIONS_PER_SOURCE,
    Math.max(1, Math.floor(totalLengthM / Math.max(0.5, spacingM))),
  );
}

function boundedTier<T>(values: T[], maximum: number): T[] {
  if (values.length <= maximum) return values;
  if (maximum <= 1) return [values[Math.floor((values.length - 1) / 2)]];
  return Array.from({ length: maximum }, (_, index) => (
    values[Math.round(index * (values.length - 1) / (maximum - 1))]
  ));
}

/** Shuffle inside preference tiers without allowing a global shuffle to erase
 * water/path affinity. The combined list is also hard-bounded. */
export function mergeParkMicrodetailCandidateTiers<T>(
  tiers: readonly (readonly T[])[],
  random: () => number,
): T[] {
  const result: T[] = [];
  for (const tier of tiers) {
    const remaining = MAX_PARK_MICRODETAIL_CANDIDATES_PER_KIND - result.length;
    if (remaining <= 0) break;
    const bounded = boundedTier(
      [...tier],
      Math.min(MAX_PARK_MICRODETAIL_CANDIDATES_PER_TIER, remaining),
    );
    result.push(...shuffle(bounded, random));
  }
  return result;
}

function stationsAlong(
  points: readonly ParkMicrodetailPoint[],
  closed: boolean,
  spacingM: number,
): Array<Candidate & { nx: number; ny: number }> {
  const segments = segmentsFor(points, closed).map(([start, end]) => ({
    start,
    end,
    length: Math.hypot(end.x - start.x, end.y - start.y),
  })).filter(({ length }) => length > 1e-6);
  const total = segments.reduce((sum, { length }) => sum + length, 0);
  if (total <= 0) return [];
  const count = boundedParkMicrodetailStationCount(total, spacingM);
  const result: Array<Candidate & { nx: number; ny: number }> = [];
  for (let station = 0; station < count; station += 1) {
    let distance = ((station + 0.5) / count) * total;
    for (const segment of segments) {
      if (distance > segment.length) {
        distance -= segment.length;
        continue;
      }
      const ratio = distance / segment.length;
      const ux = (segment.end.x - segment.start.x) / segment.length;
      const uy = (segment.end.y - segment.start.y) / segment.length;
      result.push({
        x: segment.start.x + (segment.end.x - segment.start.x) * ratio,
        y: segment.start.y + (segment.end.y - segment.start.y) * ratio,
        yawRad: Math.atan2(uy, ux),
        nx: -uy,
        ny: ux,
      });
      break;
    }
  }
  return result;
}

function boundaryCandidates(
  ring: readonly ParkMicrodetailPoint[],
  footprintRadiusM: number,
): Candidate[] {
  const candidates: Candidate[] = [];
  const insetM = footprintRadiusM + 1.25;
  for (const station of stationsAlong(ring, true, Math.max(3.4, footprintRadiusM * 3.2))) {
    const first = { x: station.x + station.nx * 0.15, y: station.y + station.ny * 0.15 };
    const sign = pointInRing(first, ring) ? 1 : -1;
    candidates.push({
      x: station.x + station.nx * insetM * sign,
      y: station.y + station.ny * insetM * sign,
      yawRad: station.yawRad,
    });
  }
  return candidates;
}

function adjacentGuideCandidates(
  guides: readonly ParkMicrodetailGuide[],
  guideKind: 'circulation' | 'water',
  footprintRadiusM: number,
): Candidate[] {
  const candidates: Candidate[] = [];
  for (const guide of guides) {
    if (guide.kind !== guideKind) continue;
    if (candidates.length >= MAX_PARK_MICRODETAIL_CANDIDATES_PER_TIER) break;
    const points = guide.points.filter(finitePoint);
    if (points.length < 2) continue;
    const isArea = guideIsArea(guide);
    const buffer = Math.max(0, guide.bufferM ?? DEFAULT_GUIDE_BUFFERS[guide.kind]);
    const halfWidth = isArea ? 0 : Math.max(0, guide.widthM ?? 0) / 2;
    const offset = halfWidth + buffer + footprintRadiusM + 0.55;
    for (const station of stationsAlong(points, guide.closed === true, 5.5)) {
      const sides = [1, -1];
      if (isArea && points.length >= 3) {
        const positive = {
          x: station.x + station.nx * 0.15,
          y: station.y + station.ny * 0.15,
        };
        // Area-edge details belong outside the water/program polygon.
        sides.splice(0, sides.length, pointInRing(positive, points) ? -1 : 1);
      }
      for (const side of sides) {
        if (candidates.length >= MAX_PARK_MICRODETAIL_CANDIDATES_PER_TIER) break;
        candidates.push({
          x: station.x + station.nx * offset * side,
          y: station.y + station.ny * offset * side,
          yawRad: station.yawRad,
        });
      }
    }
  }
  return candidates;
}

function gridCandidates(
  ring: readonly ParkMicrodetailPoint[],
  areaM2: number,
  random: () => number,
): Candidate[] {
  const xs = ring.map(({ x }) => x);
  const ys = ring.map(({ y }) => y);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const step = Math.max(2.6, Math.sqrt(Math.max(areaM2, 1) / 420));
  const candidates: Candidate[] = [];
  for (let y = minY + step / 2;
    y < maxY && candidates.length < MAX_PARK_MICRODETAIL_CANDIDATES_PER_TIER;
    y += step) {
    for (let x = minX + step / 2;
      x < maxX && candidates.length < MAX_PARK_MICRODETAIL_CANDIDATES_PER_TIER;
      x += step) {
      candidates.push({
        x: x + (random() - 0.5) * step * 0.52,
        y: y + (random() - 0.5) * step * 0.52,
        yawRad: random() * Math.PI * 2,
      });
    }
  }
  return candidates;
}

function candidatesForKind(
  kind: ParkMicrodetailKind,
  footprintRadiusM: number,
  ring: readonly ParkMicrodetailPoint[],
  areaM2: number,
  guides: readonly ParkMicrodetailGuide[],
  primaries: readonly ParkMicrodetailPrimaryPlacement[],
  random: () => number,
): Candidate[] {
  const radius = footprintRadiusM;
  if (kind === 'tree_grate') {
    return primaries.flatMap((primary, sourcePrimaryIndex) => primary.kind === 'tree'
      ? [{ x: primary.x, y: primary.y, yawRad: 0, sourcePrimaryIndex }]
      : []);
  }
  const grid = gridCandidates(ring, areaM2, random);
  const boundary = boundaryCandidates(ring, radius);
  const circulation = adjacentGuideCandidates(guides, 'circulation', radius);
  const water = adjacentGuideCandidates(guides, 'water', radius);

  if (kind === 'reed' || kind === 'riprap') {
    return mergeParkMicrodetailCandidateTiers([water, boundary, grid], random);
  }
  if (PLANTING_KINDS.has(kind) || kind === 'boulder') {
    return mergeParkMicrodetailCandidateTiers([boundary, water, grid], random);
  }
  if (kind === 'picnic_table') {
    return mergeParkMicrodetailCandidateTiers([circulation, grid, boundary], random);
  }
  return mergeParkMicrodetailCandidateTiers([circulation, boundary, grid], random);
}

function clearsCollisions(
  candidate: Candidate,
  radiusM: number,
  placements: readonly ParkMicrodetailPlacement[],
  primaries: readonly ParkMicrodetailPrimaryPlacement[],
  clearanceM: number,
): boolean {
  for (let index = 0; index < primaries.length; index += 1) {
    if (candidate.sourcePrimaryIndex === index) continue;
    const primary = primaries[index];
    if (Math.hypot(candidate.x - primary.x, candidate.y - primary.y)
      + 1e-7 < radiusM + Math.max(0, primary.footprintRadiusM) + clearanceM) return false;
  }
  return placements.every((placement) => (
    Math.hypot(candidate.x - placement.x, candidate.y - placement.y) + 1e-7
      >= radiusM + placement.footprintRadiusM + clearanceM
  ));
}

function elementCount(kind: ParkMicrodetailKind, random: () => number): number {
  switch (kind) {
    case 'shrub': return 5 + Math.floor(random() * 5);
    case 'perennial': return 7 + Math.floor(random() * 7);
    case 'ornamental_grass': return 5 + Math.floor(random() * 7);
    case 'reed': return 8 + Math.floor(random() * 8);
    case 'riprap': return 5 + Math.floor(random() * 5);
    default: return 1;
  }
}

function renderedFootprintRadiusM(kind: ParkMicrodetailKind, scale: number): number {
  if (kind === 'tree_grate') return FOOTPRINT_RADIUS_M[kind];
  if (kind === 'bike_rack') {
    // Three rendered hoops span +/-0.62 m; include each scaled 0.4 m hoop.
    return 0.62 + 0.4 * scale;
  }
  return FOOTPRINT_RADIUS_M[kind] * scale;
}

export interface ParkMicrodetailElementOffset {
  x: number;
  y: number;
  yawRad: number;
  sizeFactor: number;
}

/** Expand one authored clump into a bounded deterministic element layout.
 * Renderers can instance every returned element in the same per-kind draw call. */
export function buildParkMicrodetailElementOffsets(
  placement: Pick<ParkMicrodetailPlacement, 'kind' | 'elementCount' | 'yawRad' | 'footprintRadiusM'>,
): ParkMicrodetailElementOffset[] {
  const requested = CLUSTERED_KINDS.has(placement.kind) ? placement.elementCount : 1;
  const count = Math.max(1, Math.min(
    MAX_PARK_MICRODETAIL_ELEMENTS_PER_PLACEMENT,
    Math.floor(requested),
  ));
  if (count === 1) return [{ x: 0, y: 0, yawRad: placement.yawRad, sizeFactor: 0.82 }];
  const goldenAngle = Math.PI * (3 - Math.sqrt(5));
  return Array.from({ length: count }, (_, index) => {
    const radial = Math.sqrt((index + 0.5) / count) * placement.footprintRadiusM * 0.54;
    const angle = placement.yawRad + index * goldenAngle;
    return {
      x: Math.cos(angle) * radial,
      y: Math.sin(angle) * radial,
      yawRad: angle + index * 0.17,
      sizeFactor: 0.34 + (index % 4) * 0.035,
    };
  });
}

export function buildParkMicrodetailFamily(
  input: ParkMicrodetailFamilyInput,
): ParkMicrodetailPlacement[] {
  const ring = cleanRing(input.boundary);
  if (ring.length < 3) return [];
  const areaM2 = polygonArea(ring);
  if (!Number.isFinite(areaM2) || areaM2 < 16) return [];

  const guides = input.guides ?? [];
  const primaries = (input.primaryPlacements ?? []).filter((placement) => (
    finitePoint(placement) && Number.isFinite(placement.footprintRadiusM)
  ));
  const maxPlacements = Math.max(0, Math.min(
    MAX_PARK_MICRODETAIL_PLACEMENTS,
    Math.floor(input.maxPlacements ?? MAX_PARK_MICRODETAIL_PLACEMENTS),
  ));
  if (maxPlacements === 0) return [];

  const random = seededRandom(`${input.zoneId}|${input.familyId}|park-microdetail-v1`);
  const targets = fitTargetsToBudget(familyTargets(
    input.familyId,
    areaM2,
    polygonPerimeter(ring),
    primaries.filter(({ kind }) => kind === 'tree').length,
  ), maxPlacements);
  const placements: ParkMicrodetailPlacement[] = [];
  const clearanceM = Math.max(0, input.collisionClearanceM ?? 0.25);

  for (const target of targets) {
    // Candidate offsets reserve the largest possible scaled assembly. Exact
    // collision/containment checks below use each accepted assembly's scale.
    const candidateRadiusM = renderedFootprintRadiusM(target.kind, 1.12);
    const candidates = candidatesForKind(
      target.kind,
      candidateRadiusM,
      ring,
      areaM2,
      guides,
      primaries,
      random,
    );
    let placedForKind = 0;
    for (const candidate of candidates) {
      if (placedForKind >= target.count || placements.length >= maxPlacements) break;
      const scale = 0.88 + random() * 0.24;
      const radiusM = renderedFootprintRadiusM(target.kind, scale);
      // `candidateRadiusM` is intentionally evaluated to document and retain
      // the maximum-radius candidate tier spacing contract.
      if (radiusM > candidateRadiusM + 1e-7) continue;
      if (!parkMicrodetailFootprintFits(candidate, radiusM, ring, guides)) continue;
      if (!clearsCollisions(candidate, radiusM, placements, primaries, clearanceM)) continue;
      const placementIndex = placements.length;
      placements.push({
        id: `${input.zoneId}:micro:${target.kind}:${placementIndex}`,
        familyId: input.familyId,
        kind: target.kind,
        x: candidate.x,
        y: candidate.y,
        yawRad: candidate.yawRad,
        footprintRadiusM: radiusM,
        scale,
        elementCount: elementCount(target.kind, random),
        ...(candidate.sourcePrimaryIndex === undefined
          ? {}
          : { sourcePrimaryIndex: candidate.sourcePrimaryIndex }),
      });
      placedForKind += 1;
    }
  }
  return placements;
}
