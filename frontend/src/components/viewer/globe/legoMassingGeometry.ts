import * as THREE from 'three';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { createKitMeshes, kitWall } from './legoMassingKitPainter';
import { cleanRing, insideKitRing, localKitRing } from './legoMassingRing';

export interface LegoMassingMeshData {
  positions: number[];
  indices: number[];
  vertexCount: number;
}

const MASSING_PALETTE = [
  '#c8c2b8',
  '#bbc5c1',
  '#d0bfac',
  '#bcc0c5',
  '#c9b7a8',
] as const;

/** Stable muted architecture colour; never reuse neon plan-zone fills. */
export function legoMassingColor(seed: string): string {
  let hash = 2166136261;
  for (let index = 0; index < seed.length; index += 1) {
    hash ^= seed.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return MASSING_PALETTE[Math.abs(hash) % MASSING_PALETTE.length];
}

/**
 * Build a low-cost exact-footprint prism for district-scale LEGO LOD.
 * Coordinates stay in the same local ENU convention as GlobeZoneLayer:
 * X=east, Y=north, Z=up.
 */
export function buildLegoMassingMeshData(
  ring: readonly number[][],
  centroidLng: number,
  centroidLat: number,
  heightMeters: number,
): LegoMassingMeshData | null {
  const cleaned = cleanRing(ring);
  if (cleaned.length < 3 || !(heightMeters > 0)) return null;

  const metresPerDegreeLongitude = metersPerDegLon(centroidLat);
  const local = cleaned.map(([longitude, latitude]) => new THREE.Vector2(
    (longitude - centroidLng) * metresPerDegreeLongitude,
    (latitude - centroidLat) * METERS_PER_DEG_LAT,
  ));
  const triangles = THREE.ShapeUtils.triangulateShape(local, []);
  if (triangles.length === 0) return null;

  const positions: number[] = [];
  for (const point of local) positions.push(point.x, point.y, 0);
  for (const point of local) positions.push(point.x, point.y, heightMeters);

  const count = local.length;
  const indices: number[] = [];
  for (const triangle of triangles) {
    // Double-sided material makes winding immaterial visually; opposing base
    // and roof windings still give computeVertexNormals a coherent shell.
    indices.push(triangle[0], triangle[1], triangle[2]);
    indices.push(triangle[0] + count, triangle[2] + count, triangle[1] + count);
  }
  for (let index = 0; index < count; index += 1) {
    const next = (index + 1) % count;
    indices.push(index, next, next + count);
    indices.push(index, next + count, index + count);
  }

  return { positions, indices, vertexCount: count * 2 };
}

/** Dressing for a massing prism: floor lines and window bays. Every length is
 * a real-world metre value supplied by the caller; nothing here is tuned. */
export interface LegoMassingDressingOptions {
  storeys: number;
  /** null draws one line per storey at heightMeters / storeys. */
  floorLineSpacingM: number | null;
  bayModuleM: number;
  windowWidthM: number;
  windowHeightM: number;
  windowSillM: number;
  wallEndMarginM: number;
  floorLineHeightM: number;
  surfaceOffsetM: number;
}

export interface LegoMassingDressingData {
  floorLines: LegoMassingMeshData;
  windows: LegoMassingMeshData;
  /** Whole window bays on each wall, in ring order. */
  baysPerWall: number[];
  /** Heights of the drawn floor lines above the base. */
  floorLevelsM: number[];
}

/**
 * Floor lines and window bays for an exact-footprint massing prism.
 *
 * Window bays sit on a fixed module. A longer wall gains whole bays and a
 * shorter wall loses them; a window is never widened or narrowed to fit, so
 * the facade keeps a believable rhythm at any outline. Coordinates share the
 * prism's local ENU frame (X=east, Y=north, Z=up).
 */
export function buildLegoMassingDressingData(
  ring: readonly number[][],
  centroidLng: number,
  centroidLat: number,
  heightMeters: number,
  options: LegoMassingDressingOptions,
): LegoMassingDressingData | null {
  const cleaned = cleanRing(ring);
  const storeys = Math.floor(options.storeys);
  if (cleaned.length < 3 || !(heightMeters > 0) || !(storeys >= 1)
    || !(options.bayModuleM > 0) || !(options.windowWidthM > 0) || options.windowWidthM >= options.bayModuleM) return null;

  const metresPerDegreeLongitude = metersPerDegLon(centroidLat);
  const local = cleaned.map(([longitude, latitude]) => [
    (longitude - centroidLng) * metresPerDegreeLongitude,
    (latitude - centroidLat) * METERS_PER_DEG_LAT,
  ]);
  const signedArea = local.reduce((sum, point, index) => {
    const next = local[(index + 1) % local.length];
    return sum + point[0] * next[1] - next[0] * point[1];
  }, 0) / 2;
  if (!signedArea) return null;
  // Outward is to the right of travel on a counter-clockwise ring.
  const outward = signedArea > 0 ? 1 : -1;

  const spacing = options.floorLineSpacingM && options.floorLineSpacingM > 0
    ? options.floorLineSpacingM : heightMeters / storeys;
  const rows = Math.max(1, Math.floor(heightMeters / spacing + 1e-6));
  const floorLevelsM = Array.from({ length: rows - 1 }, (_, index) => (index + 1) * spacing);
  // A window stays inside its own storey, below the floor line above it.
  const windowHeight = Math.min(options.windowHeightM,
    spacing - options.windowSillM - options.floorLineHeightM);

  const floorLines: LegoMassingMeshData = { positions: [], indices: [], vertexCount: 0 };
  const windows: LegoMassingMeshData = { positions: [], indices: [], vertexCount: 0 };
  const quad = (target: LegoMassingMeshData, a: number[], b: number[], bottom: number, top: number) => {
    const base = target.vertexCount;
    target.positions.push(a[0], a[1], bottom, b[0], b[1], bottom, b[0], b[1], top, a[0], a[1], top);
    target.indices.push(base, base + 1, base + 2, base, base + 2, base + 3);
    target.vertexCount += 4;
  };

  const baysPerWall: number[] = [];
  for (let index = 0; index < local.length; index += 1) {
    const start = local[index], end = local[(index + 1) % local.length];
    const length = Math.hypot(end[0] - start[0], end[1] - start[1]);
    if (length < 1e-6) { baysPerWall.push(0); continue; }
    const along = [(end[0] - start[0]) / length, (end[1] - start[1]) / length];
    const normal = [outward * along[1], -outward * along[0]];
    const at = (distance: number) => [
      start[0] + along[0] * distance + normal[0] * options.surfaceOffsetM,
      start[1] + along[1] * distance + normal[1] * options.surfaceOffsetM,
    ];
    for (const level of floorLevelsM) {
      quad(floorLines, at(0), at(length), level - options.floorLineHeightM / 2, level + options.floorLineHeightM / 2);
    }
    const bays = Math.max(0, Math.floor((length - 2 * options.wallEndMarginM) / options.bayModuleM + 1e-9));
    baysPerWall.push(bays);
    if (!bays || !(windowHeight > 0)) continue;
    // Centre the whole group; leftover wall is shared between both ends.
    const first = (length - bays * options.bayModuleM) / 2 + (options.bayModuleM - options.windowWidthM) / 2;
    for (let row = 0; row < rows; row += 1) {
      const sill = row * spacing + options.windowSillM;
      for (let bay = 0; bay < bays; bay += 1) {
        const left = first + bay * options.bayModuleM;
        quad(windows, at(left), at(left + options.windowWidthM), sill, sill + windowHeight);
      }
    }
  }
  return { floorLines, windows, baysPerWall, floorLevelsM };
}

/** One mesh whose faces carry their own colour (linear RGB per vertex). */
export interface LegoMassingColoredMesh extends LegoMassingMeshData {
  colors: number[];
}

/**
 * A facade kit for one archetype: real floor levels, fixed-width window and
 * balcony bays, and the archetype's own colours. Every length is in metres and
 * comes from the caller; this module tunes nothing.
 */
export interface LegoMassingKitStyle {
  storeys: number;
  plinthHeightM: number;
  groundFloorHeightM: number;
  upperFloorHeightM: number;
  parapetHeightM: number;
  /** Solid wall kept at each end of every facade. */
  cornerPierM: number;
  windowBayModuleM: number;
  windowWidthM: number;
  windowHeightM: number;
  windowSillM: number;
  groundWindowHeightM: number;
  groundWindowSillM: number;
  loggiaBayModuleM: number;
  loggiaWidthM: number;
  loggiaHeightM: number;
  loggiaDepthM: number;
  /** Only a wall at least this long carries balcony columns. */
  loggiaMinWallM: number;
  railingHeightM: number;
  entranceWidthM: number;
  entranceDepthM: number;
  entranceHeightM: number;
  floorLineHeightM: number;
  surfaceOffsetM: number;
  colors: Record<'wall' | 'timber' | 'frame' | 'glass' | 'curtain' | 'slab' | 'railing' | 'roof' | 'plinth' | 'joint' | 'cap' | 'units', string>;
}

export type LegoMassingBay = 'window' | 'loggia';

export interface LegoMassingKitData {
  solid: LegoMassingColoredMesh;
  glass: LegoMassingColoredMesh;
  /** Top of the parapet above the base. */
  wallHeightM: number;
  /** Floor levels above the base, ground floor first. */
  floorLevelsM: number[];
  /** Upper-floor bay sequence, ground windows and entrance, per wall in ring order. */
  walls: { lengthM: number; bays: LegoMassingBay[]; groundWindows: number; entrance: boolean }[];
}

/** The upper-floor bay sequence for one wall. Bays keep their module width:
 * a longer wall gains whole bays, never wider ones. Balcony columns sit in
 * the middle with a window bay at each end, as on the archetype's front. */
export function legoMassingKitBays(lengthM: number, style: Pick<LegoMassingKitStyle,
  'cornerPierM' | 'windowBayModuleM' | 'loggiaBayModuleM' | 'loggiaMinWallM'>): LegoMassingBay[] {
  const usable = lengthM - 2 * style.cornerPierM;
  const window = style.windowBayModuleM, loggia = style.loggiaBayModuleM;
  const fit = (space: number, module: number) => Math.max(0, Math.floor(space / module + 1e-6));
  if (lengthM + 1e-6 >= style.loggiaMinWallM && usable + 1e-6 >= 2 * window + loggia) {
    // Whatever is left over is less than one bay; it becomes solid wall, shared
    // between both ends, so the facade stays symmetrical.
    return ['window', ...Array<LegoMassingBay>(fit(usable - 2 * window, loggia)).fill('loggia'), 'window'];
  }
  return Array<LegoMassingBay>(fit(usable, window)).fill('window');
}

/**
 * Build a complete archetype-styled shell for an outline: walls with window
 * bays and recessed balconies, entrance, parapet, roof and roof plant.
 * It replaces the plain prism visually, so its walls are closed on their own.
 * Coordinates share the prism's local ENU frame (X=east, Y=north, Z=up); the
 * first drawn edge is the front and carries the entrance.
 */
export function buildLegoMassingKitData(
  ring: readonly number[][],
  centroidLng: number,
  centroidLat: number,
  style: LegoMassingKitStyle,
): LegoMassingKitData | null {
  const cleaned = cleanRing(ring);
  const storeys = Math.floor(style.storeys);
  if (cleaned.length < 3 || !(storeys >= 1) || !(style.groundFloorHeightM > 0) || !(style.upperFloorHeightM > 0)
    || !(style.windowBayModuleM > style.windowWidthM) || !(style.loggiaBayModuleM > style.loggiaWidthM)) return null;
  // Counter-clockwise, keeping the first drawn edge as wall 0 (the front).
  const local = localKitRing(cleaned, centroidLng, centroidLat);
  if (!local) return null;

  type Tone = keyof LegoMassingKitStyle['colors'];
  const meshes = createKitMeshes<Tone>(style.colors);
  const { solid, glass, linear, push } = meshes;

  const plinth = style.plinthHeightM, off = style.surfaceOffsetM;
  const floorLevelsM = Array.from({ length: storeys }, (_, level) =>
    plinth + (level === 0 ? 0 : style.groundFloorHeightM + (level - 1) * style.upperFloorHeightM));
  const roofLevel = plinth + style.groundFloorHeightM + (storeys - 1) * style.upperFloorHeightM;
  const wallHeightM = roofLevel + style.parapetHeightM;
  const walls: LegoMassingKitData['walls'] = [];

  for (let index = 0; index < local.length; index += 1) {
    const start = local[index], end = local[(index + 1) % local.length];
    const length = Math.hypot(end[0] - start[0], end[1] - start[1]);
    if (length < 1e-6) { walls.push({ lengthM: 0, bays: [], groundWindows: 0, entrance: false }); continue; }
    const along = [(end[0] - start[0]) / length, (end[1] - start[1]) / length];
    const { face, flat, cheek, box } = kitWall(meshes, start, along);
    /** A framed window with two lights, a transom and a curtain at each side. */
    const windowAt = (centre: number, sill: number, width: number, height: number) => {
      const left = centre - width / 2, frame = 0.07;
      face(solid, 'frame', left, left + width, sill, sill + height, off);
      const transom = sill + height * 0.62, mid = centre;
      for (const [u0, u1] of [[left + frame, mid - frame / 2], [mid + frame / 2, left + width - frame]]) {
        face(glass, 'glass', u0, u1, sill + frame, transom - frame / 2, off * 1.5);
        face(glass, 'glass', u0, u1, transom + frame / 2, sill + height - frame, off * 1.5);
      }
      const curtain = Math.min(0.3, width * 0.12);
      face(solid, 'curtain', left + frame, left + frame + curtain, sill + frame, sill + height - frame, off * 2);
      face(solid, 'curtain', left + width - frame - curtain, left + width - frame, sill + frame, sill + height - frame, off * 2);
    };

    const bays = legoMassingKitBays(length, style);
    const baysWidth = bays.reduce((sum, bay) => sum + (bay === 'loggia' ? style.loggiaBayModuleM : style.windowBayModuleM), 0);
    // --- Plinth, floor joints, parapet cap --------------------------------
    face(solid, 'plinth', 0, length, 0, plinth, off);
    for (const level of floorLevelsM.slice(1)) face(solid, 'joint', 0, length, level - style.floorLineHeightM, level, off * 0.5);
    face(solid, 'cap', 0, length, wallHeightM - 0.08, wallHeightM, off * 1.5);
    face(solid, 'cap', 0, length, wallHeightM - 0.08, wallHeightM, -0.3);
    flat('cap', 0, length, -0.3, off * 1.5, wallHeightM, true);
    face(solid, 'wall', 0, length, roofLevel, wallHeightM - 0.08, -0.3);

    // --- Ground floor ------------------------------------------------------
    const groundTop = floorLevelsM[1] ?? roofLevel;
    const usable = length - 2 * style.cornerPierM;
    const entranceWidth = Math.min(style.entranceWidthM, usable - 2 * style.windowBayModuleM);
    const entrance = index === 0 && entranceWidth >= 4;
    const entranceLeft = length / 2 - entranceWidth / 2, entranceRight = length / 2 + entranceWidth / 2;
    let groundWindows = 0;
    face(solid, 'wall', 0, length, 0, groundTop);
    // Ground windows fill the wall each side of the entrance on the same module.
    const runs = entrance
      ? [[style.cornerPierM, entranceLeft + 0.4], [entranceRight - 0.4, length - style.cornerPierM]]
      : [[style.cornerPierM, length - style.cornerPierM]];
    for (const [from, to] of runs) {
      const count = Math.max(0, Math.floor((to - from) / style.windowBayModuleM + 1e-6));
      const first = (from + to - count * style.windowBayModuleM) / 2;
      for (let bay = 0; bay < count; bay += 1) {
        windowAt(first + (bay + 0.5) * style.windowBayModuleM, plinth + style.groundWindowSillM, style.windowWidthM,
          Math.min(style.groundWindowHeightM, style.groundFloorHeightM - style.groundWindowSillM - 0.3));
        groundWindows += 1;
      }
    }
    if (index === 0 && !entrance && length >= 2 * style.cornerPierM + 2.4) {
      // Too narrow for the canopy: a plain glazed front door between the windows.
      const door = Math.min(1.8, style.windowBayModuleM - style.windowWidthM - 0.1 > 1.2 ? 1.8 : 1.0);
      const doorLeft = length / 2 - door / 2;
      face(solid, 'frame', doorLeft, doorLeft + door, plinth, plinth + 2.6, off * 2.5);
      face(glass, 'glass', doorLeft + 0.07, doorLeft + door - 0.07, plinth + 0.07, plinth + 2.53, off * 3);
      box('roof', doorLeft - 0.4, doorLeft + door + 0.4, 0, 0.9, plinth + 2.75, plinth + 2.9);
    }
    if (entrance) {
      // Canopy slab with a dark fascia, timber fins each side, glazed doors between.
      const top = plinth + style.entranceHeightM, depth = style.entranceDepthM, door = Math.min(2.6, entranceWidth * 0.3);
      box('roof', entranceLeft, entranceRight, 0, depth, top - 0.22, top);
      face(solid, 'cap', entranceLeft, entranceRight, top - 0.22, top, depth + off);
      const doorLeft = length / 2 - door / 2;
      face(solid, 'frame', doorLeft, doorLeft + door, plinth, plinth + 2.9, off);
      face(glass, 'glass', doorLeft + 0.08, length / 2 - 0.04, plinth + 0.08, plinth + 2.82, off * 1.5);
      face(glass, 'glass', length / 2 + 0.04, doorLeft + door - 0.08, plinth + 0.08, plinth + 2.82, off * 1.5);
      for (const [from, to] of [[entranceLeft + 0.3, doorLeft - 0.9], [doorLeft + door + 0.9, entranceRight - 0.3]]) {
        for (let fin = from; fin + 0.14 <= to + 1e-6; fin += 0.4) box('timber', fin, fin + 0.14, 0, depth - 0.15, plinth, top - 0.22);
      }
    }

    // --- Upper floors ------------------------------------------------------
    for (let level = 1; level < storeys; level += 1) {
      const floor = floorLevelsM[level], ceiling = level + 1 < storeys ? floorLevelsM[level + 1] : roofLevel;
      let cursor = (length - baysWidth) / 2;
      face(solid, 'wall', 0, cursor, floor, ceiling);
      for (const bay of bays) {
        if (bay === 'window') {
          const module = style.windowBayModuleM;
          face(solid, 'wall', cursor, cursor + module, floor, ceiling);
          windowAt(cursor + module / 2, floor + style.windowSillM, style.windowWidthM, Math.min(style.windowHeightM, ceiling - floor - style.windowSillM - 0.2));
          cursor += module;
          continue;
        }
        const module = style.loggiaBayModuleM, pier = (module - style.loggiaWidthM) / 2;
        const left = cursor + pier, right = cursor + module - pier, depth = style.loggiaDepthM;
        const head = Math.min(floor + style.loggiaHeightM, ceiling - 0.25);
        // Brick around the opening.
        face(solid, 'wall', cursor, left, floor, ceiling);
        face(solid, 'wall', right, cursor + module, floor, ceiling);
        face(solid, 'wall', left, right, head, ceiling);
        // Timber-lined recess: floor, soffit, cheeks and back wall.
        flat('slab', left, right, -depth, 0, floor + 0.02, true);
        flat('timber', left, right, -depth, 0, head, false);
        cheek('timber', left, -depth, 0, floor, head, true);
        cheek('timber', right, -depth, 0, floor, head, false);
        face(solid, 'timber', left, right, floor, head, -depth);
        // Glazed doors on the back wall.
        // The doors leave timber showing each side, as on the archetype.
        const doors = style.loggiaWidthM * 0.72, doorsLeft = (left + right) / 2 - doors / 2, doorsTop = head - 0.12;
        face(solid, 'frame', doorsLeft, doorsLeft + doors, floor + 0.02, doorsTop, -depth + off);
        for (let pane = 0; pane < 3; pane += 1) {
          const u0 = doorsLeft + 0.07 + pane * (doors - 0.07) / 3, u1 = doorsLeft + (pane + 1) * (doors - 0.07) / 3;
          face(glass, 'glass', u0, u1, floor + 0.1, doorsTop - 0.07, -depth + off * 1.5);
        }
        // Slab edge and an open metal railing at the facade line.
        face(solid, 'slab', left, right, floor - 0.16, floor + 0.02, off);
        const rail = floor + style.railingHeightM;
        face(solid, 'railing', left, right, rail - 0.05, rail, off);
        face(solid, 'railing', left, right, floor + 0.08, floor + 0.12, off);
        const balusters = Math.max(2, Math.round((right - left) / 0.14));
        for (let baluster = 0; baluster <= balusters; baluster += 1) {
          const u = left + (right - left - 0.025) * baluster / balusters;
          face(solid, 'railing', u, u + 0.025, floor + 0.12, rail - 0.05, off);
        }
        cursor += module;
      }
      face(solid, 'wall', cursor, length, floor, ceiling);
    }
    walls.push({ lengthM: length, bays, groundWindows, entrance });
  }

  // --- Roof deck and roof plant -------------------------------------------
  const outline = local.map(point => new THREE.Vector2(point[0], point[1]));
  const roofBase = solid.vertexCount;
  for (const point of local) { solid.positions.push(point[0], point[1], roofLevel); solid.colors.push(...linear.roof); }
  for (const triangle of THREE.ShapeUtils.triangulateShape(outline, [])) {
    solid.indices.push(roofBase + triangle[0], roofBase + triangle[1], roofBase + triangle[2]);
  }
  solid.vertexCount += local.length;
  const centre = local.reduce((sum, point) => [sum[0] + point[0] / local.length, sum[1] + point[1] / local.length], [0, 0]);
  const front = local[1], origin = local[0], frontLength = Math.hypot(front[0] - origin[0], front[1] - origin[1]) || 1;
  const ax = [(front[0] - origin[0]) / frontLength, (front[1] - origin[1]) / frontLength], ay = [-ax[1], ax[0]];
  // Plant sizes and offsets follow the archetype's roof; a unit is left out
  // where the outline has no clear roof for it.
  for (const [dx, dy, width, depth, height] of [[1, 3, 3, 3, 1.8], [-3, 3, 2.2, 2, 1], [-2, -4, 1.8, 1.4, 0.8], [5, 4, 1.4, 1.5, 1.1]]) {
    const cx = centre[0] + ax[0] * dx + ay[0] * dy, cy = centre[1] + ax[1] * dx + ay[1] * dy;
    const corners = [[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([sx, sy]) => [
      cx + ax[0] * sx * width / 2 + ay[0] * sy * depth / 2, cy + ax[1] * sx * width / 2 + ay[1] * sy * depth / 2]);
    if (!corners.every(corner => insideKitRing(local, corner[0], corner[1], 1.5))) continue;
    // Each unit stands on a 0.24 m plinth, as on the archetype.
    const top = roofLevel + 0.24 + height;
    for (let side = 0; side < 4; side += 1) {
      const a = corners[side], b = corners[(side + 1) % 4];
      push(solid, 'units', [[a[0], a[1], roofLevel], [b[0], b[1], roofLevel], [b[0], b[1], top], [a[0], a[1], top]]);
    }
    push(solid, 'units', corners.map(corner => [corner[0], corner[1], top]));
  }
  return { solid, glass, wallHeightM, floorLevelsM, walls };
}
