import * as THREE from 'three';
import type { LegoMassingBay, LegoMassingKitData } from './legoMassingGeometry';
import { createKitMeshes, kitWall } from './legoMassingKitPainter';
import { cleanRing, insetKitRing, insideKitRing, kitCourtyardRing, kitRingArea, localKitRing } from './legoMassingRing';

type Tone = 'wall' | 'stone' | 'trim' | 'glass' | 'shopfront' | 'curtain' | 'railing' | 'roof' | 'plinth' | 'paving' | 'planting' | 'units';

/**
 * A facade kit for a perimeter block over shops: wings of one fixed depth
 * around a courtyard, shopfronts with awnings on the street fronts, a gateway
 * on the front, and balcony and window bays that alternate above. Every
 * length is in metres and comes from the caller; this module tunes nothing.
 */
export interface LegoMassingCourtyardStyle {
  storeys: number;
  plinthHeightM: number;
  groundFloorHeightM: number;
  upperFloorHeightM: number;
  parapetHeightM: number;
  /** Depth of every wing. The courtyard is whatever the wings leave open. */
  wingDepthM: number;
  /** Smallest clear courtyard. An outline too small for it is built solid. */
  courtyardMinClearM: number;
  /** Street fronts: one shopfront below, one balcony or window bay above. */
  bayModuleM: number;
  loggiaWidthM: number;
  loggiaHeightM: number;
  loggiaDepthM: number;
  loggiaDoorWidthM: number;
  loggiaDoorHeightM: number;
  railingHeightM: number;
  windowWidthM: number;
  windowHeightM: number;
  windowSillM: number;
  /** Side and courtyard walls: paired windows on every floor. */
  sideBayModuleM: number;
  sideWindowWidthM: number;
  sideWindowHeightM: number;
  sideWindowSillM: number;
  shopWindowWidthM: number;
  shopDoorWidthM: number;
  shopFrontHeightM: number;
  shopWindowSillM: number;
  awningWidthM: number;
  awningProjectionM: number;
  awningTopM: number;
  awningDropM: number;
  shopBandHeightM: number;
  shopBandProjectionM: number;
  passageWidthM: number;
  passageHeightM: number;
  stringCourseHeightM: number;
  stringCourseProjectionM: number;
  lintelHeightM: number;
  copingHeightM: number;
  copingWidthM: number;
  gardenInsetM: number;
  gardenHeightM: number;
  surfaceOffsetM: number;
  colors: Record<Tone, string>;
}

export interface LegoMassingCourtyardKitData extends LegoMassingKitData {
  /** Open courtyard inside the wings, in m². 0 when the block is built solid. */
  courtyardAreaM2: number;
  /** The front's gateway: through to the courtyard, a recessed door, or none. */
  gateway: 'passage' | 'door' | 'none';
}

/**
 * Upper-floor bays of a street front. Balconies take both ends and alternate
 * with windows towards the middle, so the front is always symmetrical. Bays
 * keep their module: a longer front gains whole bays, never wider ones.
 * `odd` leaves a middle bay for the gateway.
 */
export function legoMassingCourtyardBays(lengthM: number, moduleM: number, odd = false): LegoMassingBay[] {
  let count = moduleM > 0 ? Math.max(0, Math.floor(lengthM / moduleM + 1e-6)) : 0;
  if (odd && count % 2 === 0) count = Math.max(0, count - 1);
  return Array.from({ length: count }, (_, index) => Math.min(index, count - 1 - index) % 2 === 0 ? 'loggia' : 'window');
}

/** Wall thickness shown at the parapet, and the clear door recess of a solid block. */
const PARAPET_THICKNESS_M = 0.3, DOOR_RECESS_M = 1.5;
/** Frame and mullion widths of every window and door. */
const FRAME_M = 0.07, MULLION_M = 0.05;

/**
 * Build a complete perimeter-block shell for an outline. It replaces the
 * plain prism visually. Coordinates share the prism's local ENU frame
 * (X=east, Y=north, Z=up). The first drawn edge is the front and carries the
 * gateway; walls roughly parallel to it are street fronts, the rest are sides.
 */
export function buildLegoMassingCourtyardKitData(
  ring: readonly number[][],
  centroidLng: number,
  centroidLat: number,
  style: LegoMassingCourtyardStyle,
): LegoMassingCourtyardKitData | null {
  const cleaned = cleanRing(ring);
  const storeys = Math.floor(style.storeys);
  if (cleaned.length < 3 || !(storeys >= 1) || !(style.groundFloorHeightM > 0) || !(style.upperFloorHeightM > 0)
    || !(style.bayModuleM > style.loggiaWidthM) || !(style.bayModuleM > style.windowWidthM)
    || !(style.sideBayModuleM > style.sideWindowWidthM) || !(style.wingDepthM > 0)) return null;
  const local = localKitRing(cleaned, centroidLng, centroidLat);
  if (!local) return null;

  const meshes = createKitMeshes<Tone>(style.colors);
  const { solid, glass, linear, push } = meshes;
  const off = style.surfaceOffsetM, plinth = style.plinthHeightM;
  const floorLevelsM = Array.from({ length: storeys }, (_, level) =>
    plinth + (level === 0 ? 0 : style.groundFloorHeightM + (level - 1) * style.upperFloorHeightM));
  const roofLevel = plinth + style.groundFloorHeightM + (storeys - 1) * style.upperFloorHeightM;
  const groundTop = floorLevelsM[1] ?? roofLevel;
  const wallHeightM = roofLevel + style.parapetHeightM;
  const courtyard = kitCourtyardRing(local, style.wingDepthM, style.courtyardMinClearM);

  // --- The front and its gateway ------------------------------------------
  const frontLength = Math.hypot(local[1][0] - local[0][0], local[1][1] - local[0][1]);
  const front = [(local[1][0] - local[0][0]) / frontLength, (local[1][1] - local[0][1]) / frontLength];
  const half = style.passageWidthM / 2, gatewayCentre = frontLength / 2;
  const alongFront = (point: readonly number[]) => (point[0] - local[0][0]) * front[0] + (point[1] - local[0][1]) * front[1];
  let gateway: LegoMassingCourtyardKitData['gateway'] = frontLength >= style.passageWidthM + 1.2 ? 'door' : 'none';
  // A passage needs the courtyard wall behind the front to span it.
  if (gateway === 'door' && courtyard
    && alongFront(courtyard[0]) + 0.3 <= gatewayCentre - half && gatewayCentre + half <= alongFront(courtyard[1]) - 0.3) gateway = 'passage';
  const gatewayTop = plinth + Math.min(style.passageHeightM, style.groundFloorHeightM - style.shopBandHeightM - 0.1);

  type Role = 'frontage' | 'side' | 'court';
  const paint = (start: readonly number[], end: readonly number[], role: Role, gateCentre: number | null,
    bays: LegoMassingBay[]): LegoMassingKitData['walls'][number] => {
    const length = Math.hypot(end[0] - start[0], end[1] - start[1]);
    if (length < 1e-6) return { lengthM: 0, bays: [], groundWindows: 0, entrance: false };
    const along = [(end[0] - start[0]) / length, (end[1] - start[1]) / length];
    const { at, face, flat, cheek, box } = kitWall(meshes, start, along);
    const gate = gateCentre === null ? null : { from: gateCentre - half, to: gateCentre + half };
    /** A wall face with the gateway cut out of it. */
    const walled = (tone: Tone, u0: number, u1: number, z0: number, z1: number) => {
      if (!gate || u1 <= gate.from || u0 >= gate.to || z0 >= gatewayTop) { face(solid, tone, u0, u1, z0, z1); return; }
      face(solid, tone, u0, Math.min(u1, gate.from), z0, z1);
      face(solid, tone, Math.max(u0, gate.to), u1, z0, z1);
      face(solid, tone, Math.max(u0, gate.from), Math.min(u1, gate.to), Math.max(z0, gatewayTop), z1);
    };
    /** A framed window of equal lights with a projecting sill. */
    const windowAt = (centre: number, sill: number, width: number, height: number, lights: number, curtains: boolean) => {
      const left = centre - width / 2, light = (width - 2 * FRAME_M - (lights - 1) * MULLION_M) / lights;
      face(solid, 'trim', left, left + width, sill, sill + height, off);
      for (let index = 0; index < lights; index += 1) {
        const u0 = left + FRAME_M + index * (light + MULLION_M);
        face(glass, 'glass', u0, u0 + light, sill + FRAME_M, sill + height - FRAME_M, off * 1.5);
      }
      if (curtains) {
        const curtain = Math.min(0.28, light * 0.4);
        face(solid, 'curtain', left + FRAME_M, left + FRAME_M + curtain, sill + FRAME_M, sill + height - FRAME_M, off * 2);
        face(solid, 'curtain', left + width - FRAME_M - curtain, left + width - FRAME_M, sill + FRAME_M, sill + height - FRAME_M, off * 2);
      }
      box('trim', left - FRAME_M, left + width + FRAME_M, 0, 0.18, sill - FRAME_M, sill);
    };
    const sideBays = Math.max(0, Math.floor(length / style.sideBayModuleM + 1e-6));
    const sideFirst = (length - sideBays * style.sideBayModuleM) / 2;
    /** Paired windows on the side module, leaving the gateway clear. */
    const sideWindows = (floor: number, ceiling: number) => {
      const height = Math.min(style.sideWindowHeightM, ceiling - floor - style.sideWindowSillM - 0.1);
      let drawn = 0;
      for (let bay = 0; bay < sideBays && height > 0.4; bay += 1) {
        const centre = sideFirst + (bay + 0.5) * style.sideBayModuleM, reach = style.sideWindowWidthM / 2 + 0.3;
        if (gate && floor < gatewayTop && centre + reach > gate.from && centre - reach < gate.to) continue;
        windowAt(centre, floor + style.sideWindowSillM, style.sideWindowWidthM, height, 2, false);
        drawn += 1;
      }
      return drawn;
    };
    const module = style.bayModuleM, first = (length - bays.length * module) / 2;
    let groundWindows = 0;

    // --- Ground floor ------------------------------------------------------
    walled('plinth', 0, length, 0, plinth);
    walled(role === 'frontage' ? 'stone' : 'wall', 0, length, plinth, groundTop);
    if (role === 'frontage') {
      const sill = plinth + style.shopWindowSillM, head = plinth + Math.min(style.shopFrontHeightM, style.groundFloorHeightM - 0.6);
      const shop = style.shopWindowWidthM + 0.06 + style.shopDoorWidthM;
      bays.forEach((_, bay) => {
        const centre = first + (bay + 0.5) * module;
        if (gate && Math.abs(centre - gateCentre!) < module / 2) return;
        // The shop door sits on the side nearer the middle of the front.
        const left = centre - shop / 2, mirrored = centre > length / 2 + 1e-6;
        const window0 = mirrored ? left + style.shopDoorWidthM + 0.06 : left, window1 = window0 + style.shopWindowWidthM;
        const door0 = mirrored ? left : left + style.shopWindowWidthM + 0.06, door1 = door0 + style.shopDoorWidthM;
        face(solid, 'trim', window0, window1, sill, head, off);
        const mid = (window0 + window1) / 2;
        face(glass, 'shopfront', window0 + FRAME_M, mid - MULLION_M / 2, sill + FRAME_M, head - FRAME_M, off * 1.5);
        face(glass, 'shopfront', mid + MULLION_M / 2, window1 - FRAME_M, sill + FRAME_M, head - FRAME_M, off * 1.5);
        box('trim', window0 - FRAME_M, window1 + FRAME_M, 0, 0.18, sill - FRAME_M, sill);
        face(solid, 'trim', door0, door1, plinth, head, off);
        face(glass, 'shopfront', door0 + 0.09, door1 - 0.09, plinth + 0.3, head - 0.09, off * 1.5);
        // Awning: a sloped top, a front valance, the underside and both ends.
        const a0 = centre - style.awningWidthM / 2, a1 = centre + style.awningWidthM / 2, reach = style.awningProjectionM;
        const top = plinth + style.awningTopM, edge = top - 0.12, drop = top - style.awningDropM;
        push(solid, 'trim', [at(a0, 0, top), at(a1, 0, top), at(a1, reach, edge), at(a0, reach, edge)]);
        face(solid, 'trim', a0, a1, drop, edge, reach);
        push(solid, 'trim', [at(a0, 0, top), at(a0, reach, drop), at(a1, reach, drop), at(a1, 0, top)]);
        for (const u of [a0, a1]) push(solid, 'trim', [at(u, 0, top), at(u, reach, edge), at(u, reach, drop), at(u, 0, top)]);
        groundWindows += 1;
      });
      // Stone band over the shops, returned round both corners.
      const reach = style.shopBandProjectionM;
      box('stone', -reach, length + reach, 0, reach, groundTop - style.shopBandHeightM, groundTop);
    } else {
      groundWindows = sideWindows(plinth, groundTop);
    }
    if (gate && role !== 'court') {
      // Reveals, soffit and paving of the gateway. A passage runs through the
      // wing; a solid block has a recessed front door instead.
      const depth = gateway === 'passage' ? style.wingDepthM : DOOR_RECESS_M;
      cheek('stone', gate.from, -depth, 0, 0, gatewayTop, true);
      cheek('stone', gate.to, -depth, 0, 0, gatewayTop, false);
      flat('stone', gate.from, gate.to, -depth, 0, gatewayTop, false);
      flat('paving', gate.from, gate.to, -depth, 0.9, 0.04, true);
      if (gateway === 'door') {
        const door = Math.min(2, style.passageWidthM - 0.6), door0 = gateCentre! - door / 2, top = Math.min(2.7, gatewayTop - 0.2);
        face(solid, 'stone', gate.from, gate.to, 0, gatewayTop, -depth);
        face(solid, 'trim', door0, door0 + door, 0.04, top, -depth + off);
        face(glass, 'glass', door0 + FRAME_M, gateCentre! - MULLION_M / 2, 0.12, top - FRAME_M, -depth + off * 1.5);
        face(glass, 'glass', gateCentre! + MULLION_M / 2, door0 + door - FRAME_M, 0.12, top - FRAME_M, -depth + off * 1.5);
      }
    }

    // --- Upper floors ------------------------------------------------------
    for (let level = 1; level < storeys; level += 1) {
      const floor = floorLevelsM[level], ceiling = level + 1 < storeys ? floorLevelsM[level + 1] : roofLevel;
      if (role !== 'frontage') {
        face(solid, 'wall', 0, length, floor, ceiling);
        sideWindows(floor, ceiling);
        if (role === 'side') {
          const reach = style.stringCourseProjectionM;
          box('stone', -reach, length + reach, 0, reach, floor + 0.01 - style.stringCourseHeightM, floor + 0.01);
        }
        continue;
      }
      face(solid, 'wall', 0, first, floor, ceiling);
      face(solid, 'wall', first + bays.length * module, length, floor, ceiling);
      bays.forEach((bay, index) => {
        const cursor = first + index * module, centre = cursor + module / 2;
        if (bay === 'window') {
          const height = Math.min(style.windowHeightM, ceiling - floor - style.windowSillM - style.lintelHeightM - 0.05);
          const sill = floor + style.windowSillM, reach = style.windowWidthM / 2 + 0.1;
          face(solid, 'wall', cursor, cursor + module, floor, ceiling);
          windowAt(centre, sill, style.windowWidthM, height, 3, true);
          box('stone', centre - reach, centre + reach, 0, 0.2, sill + height, sill + height + style.lintelHeightM);
          return;
        }
        const left = centre - style.loggiaWidthM / 2, right = centre + style.loggiaWidthM / 2, depth = style.loggiaDepthM;
        const head = Math.min(floor + style.loggiaHeightM, ceiling - 0.12);
        // Brick around the opening, then the recess: floor, soffit, cheeks, back wall.
        face(solid, 'wall', cursor, left, floor, ceiling);
        face(solid, 'wall', right, cursor + module, floor, ceiling);
        face(solid, 'wall', left, right, head, ceiling);
        flat('stone', left, right, -depth, 0, floor + 0.01, true);
        flat('stone', left, right, -depth, 0, head, false);
        cheek('wall', left, -depth, 0, floor, head, true);
        cheek('wall', right, -depth, 0, floor, head, false);
        face(solid, 'wall', left, right, floor, head, -depth);
        // Glazed doors on the back wall.
        const doors = Math.min(style.loggiaDoorWidthM, style.loggiaWidthM - 0.2), doors0 = centre - doors / 2;
        const doorsTop = Math.min(floor + style.loggiaDoorHeightM, head - 0.05);
        face(solid, 'trim', doors0, doors0 + doors, floor + 0.03, doorsTop, -depth + off);
        face(glass, 'glass', doors0 + FRAME_M, centre - MULLION_M / 2, floor + 0.1, doorsTop - FRAME_M, -depth + off * 1.5);
        face(glass, 'glass', centre + MULLION_M / 2, doors0 + doors - FRAME_M, floor + 0.1, doorsTop - FRAME_M, -depth + off * 1.5);
        // Stone lintel and slab edge, and an open metal railing on the facade line.
        box('stone', left - 0.1, right + 0.1, 0, 0.2, head - 0.05, head - 0.05 + style.lintelHeightM);
        box('stone', left - 0.06, right + 0.06, 0, 0.11, floor - 0.17, floor);
        const rail = floor + style.railingHeightM;
        face(solid, 'railing', left, right, rail - 0.05, rail, off);
        face(solid, 'railing', left, right, floor + 0.08, floor + 0.12, off);
        const balusters = Math.max(2, Math.round((right - left) / 0.15));
        for (let baluster = 0; baluster <= balusters; baluster += 1) {
          const u = left + (right - left - 0.025) * baluster / balusters;
          face(solid, 'railing', u, u + 0.025, floor + 0.12, rail - 0.05, off);
        }
        // A planter at one side of the balcony, as on the archetype.
        box('trim', left + 0.15, left + 0.59, -0.75, -0.31, floor, floor + 0.44);
        box('planting', left + 0.19, left + 0.55, -0.71, -0.35, floor + 0.44, floor + 0.86);
      });
    }

    // --- Parapet and coping ------------------------------------------------
    face(solid, 'wall', 0, length, roofLevel, wallHeightM);
    face(solid, 'wall', 0, length, roofLevel, wallHeightM, -PARAPET_THICKNESS_M);
    const lip = 0.05, back = lip - style.copingWidthM;
    box('stone', -lip, length + lip, back, lip, wallHeightM, wallHeightM + style.copingHeightM);
    face(solid, 'stone', 0, length, wallHeightM, wallHeightM + style.copingHeightM, back);
    return { lengthM: length, bays, groundWindows, entrance: gate !== null && role !== 'court' };
  };

  // --- Street and side walls ------------------------------------------------
  const walls = local.map((start, index) => {
    const end = local[(index + 1) % local.length];
    const length = Math.hypot(end[0] - start[0], end[1] - start[1]);
    const parallel = length < 1e-6 ? 0 : Math.abs(((end[0] - start[0]) * front[0] + (end[1] - start[1]) * front[1]) / length);
    const frontage = index === 0 || parallel >= Math.SQRT1_2 - 1e-9;
    const gate = index === 0 && gateway !== 'none' ? gatewayCentre : null;
    return paint(start, end, frontage ? 'frontage' : 'side', gate,
      frontage ? legoMassingCourtyardBays(length, style.bayModuleM, index === 0)
        : Array<LegoMassingBay>(Math.max(0, Math.floor(length / style.sideBayModuleM + 1e-6))).fill('window'));
  });

  const flatPolygon = (tone: Tone, outline: readonly number[][], z: number, hole?: readonly number[][]) => {
    const base = solid.vertexCount, points = hole ? [...outline, ...hole] : outline;
    for (const point of points) { solid.positions.push(point[0], point[1], z); solid.colors.push(...linear[tone]); }
    const vectors = (source: readonly number[][]) => source.map(point => new THREE.Vector2(point[0], point[1]));
    for (const triangle of THREE.ShapeUtils.triangulateShape(vectors(outline), hole ? [vectors(hole)] : [])) {
      solid.indices.push(base + triangle[0], base + triangle[1], base + triangle[2]);
    }
    solid.vertexCount += points.length;
  };

  // --- Courtyard: its walls, paving and a planted bed ------------------------
  if (courtyard) {
    courtyard.forEach((corner, index) => {
      // Walked the other way round, so open air is again on the right.
      const start = courtyard[(index + 1) % courtyard.length];
      const gate = index === 0 && gateway === 'passage'
        ? (local[0][0] + front[0] * gatewayCentre - start[0]) * -front[0] + (local[0][1] + front[1] * gatewayCentre - start[1]) * -front[1]
        : null;
      paint(start, corner, 'court', gate, []);
    });
    flatPolygon('paving', courtyard, 0.04);
    const garden = insetKitRing(courtyard, style.gardenInsetM);
    if (garden) {
      garden.forEach((corner, index) => {
        const next = garden[(index + 1) % garden.length];
        push(solid, 'stone', [[next[0], next[1], 0.04], [corner[0], corner[1], 0.04],
          [corner[0], corner[1], style.gardenHeightM], [next[0], next[1], style.gardenHeightM]]);
      });
      flatPolygon('planting', garden, style.gardenHeightM);
    }
  }

  // --- Roof deck and roof plant ---------------------------------------------
  flatPolygon('roof', local, roofLevel, courtyard ?? undefined);
  const unit = (centre: readonly number[], axis: readonly number[]) => {
    const across = [-axis[1], axis[0]];
    const corners = [[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([sx, sy]) => [
      centre[0] + axis[0] * sx * 0.85 + across[0] * sy * 0.65, centre[1] + axis[1] * sx * 0.85 + across[1] * sy * 0.65]);
    if (!corners.every(corner => insideKitRing(local, corner[0], corner[1], 0.8)
      && !(courtyard && insideKitRing(courtyard, corner[0], corner[1], 0)))) return;
    // Each unit stands clear of the roof on a low frame, as on the archetype.
    const base = roofLevel + 0.25, top = base + 0.8;
    for (let side = 0; side < 4; side += 1) {
      const a = corners[side], b = corners[(side + 1) % 4];
      push(solid, 'units', [[a[0], a[1], base], [b[0], b[1], base], [b[0], b[1], top], [a[0], a[1], top]]);
      push(solid, 'railing', [[a[0], a[1], roofLevel], [b[0], b[1], roofLevel], [b[0], b[1], base], [a[0], a[1], base]]);
    }
    push(solid, 'units', corners.map(corner => [corner[0], corner[1], top]));
  };
  if (courtyard) {
    // One unit over each of up to four corners of the block, in the middle of the wing.
    const picks = new Set(Array.from({ length: Math.min(4, local.length) }, (_, pick) => Math.round(pick * local.length / 4) % local.length));
    for (const index of picks) {
      const next = local[(index + 1) % local.length], corner = local[index];
      const length = Math.hypot(next[0] - corner[0], next[1] - corner[1]) || 1;
      unit([(corner[0] + courtyard[index][0]) / 2, (corner[1] + courtyard[index][1]) / 2],
        [(next[0] - corner[0]) / length, (next[1] - corner[1]) / length]);
    }
  } else {
    const centre = local.reduce((sum, point) => [sum[0] + point[0] / local.length, sum[1] + point[1] / local.length], [0, 0]);
    for (const shift of [-3, 3]) unit([centre[0] + front[0] * shift, centre[1] + front[1] * shift], front);
  }
  return { solid, glass, wallHeightM, floorLevelsM, walls, gateway,
    courtyardAreaM2: courtyard ? kitRingArea(courtyard) : 0 };
}
