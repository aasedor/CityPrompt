/**
 * useStreetViewRender — utilities and React hook for generating street-level
 * architectural renders from a pegman position and viewing angle.
 *
 * Provides view-cone geometry, zone intersection, distance sorting, and
 * structured prompt building for Vertex AI Imagen 3 text-to-image generation.
 */
import { useCallback } from 'react';
import axios from 'axios';
import type { SiteZone } from '@/types';
import buildingCatalog from '@/data/buildingArchetypes.json';
import openSpaceCatalog from '@/data/openSpaceArchetypes.json';
import streetPathCatalog from '@/data/streetPathArchetypes.json';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const RENDER_API_URL = '/api/v1/render/generate';
const DEG_TO_RAD = Math.PI / 180;
const EARTH_RADIUS_M = 6_371_000;

/** Meters per degree of latitude (roughly constant). */
const METERS_PER_DEG_LAT = 110_540;

// Merge all archetype catalogs into a single lookup array
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const catalog: any[] = [
  ...((buildingCatalog as any)?.archetypes || []),
  ...((openSpaceCatalog as any)?.archetypes || []),
  ...((streetPathCatalog as any)?.archetypes || []),
];

// ---------------------------------------------------------------------------
// Compass helpers
// ---------------------------------------------------------------------------

const COMPASS_LABELS: [number, string][] = [
  [0, 'north'],
  [45, 'northeast'],
  [90, 'east'],
  [135, 'southeast'],
  [180, 'south'],
  [225, 'southwest'],
  [270, 'west'],
  [315, 'northwest'],
];

/** Map a heading (0 = N, clockwise) to a compass label. */
function compassDirection(angleDeg: number): string {
  const norm = ((angleDeg % 360) + 360) % 360;
  let best = COMPASS_LABELS[0][1];
  let bestDiff = 360;
  for (const [refAngle, label] of COMPASS_LABELS) {
    let diff = Math.abs(norm - refAngle);
    if (diff > 180) diff = 360 - diff;
    if (diff < bestDiff) {
      bestDiff = diff;
      best = label;
    }
  }
  return best;
}

// ---------------------------------------------------------------------------
// Archetype info extraction (mirrors useAIRender's private helper)
// ---------------------------------------------------------------------------

interface ArchetypeInfo {
  archetypeTitle?: string;
  facadeDescription?: string;
  roofDescription?: string;
  materials?: string;
  massing?: string;
  heightTendency?: string;
  publicRealm?: string;
  mapOverlayPrompt?: string;
  colorScheme?: string;
  aerialAppearance?: string;
  corridorDescription?: string;
  surfaceType?: string;
  plantingCharacter?: string;
  edgeConditions?: string;
  // Park/open space specific
  landscapeCharacter?: string;
  plantingType?: string;
  seatingRealm?: string;
  waterFeatures?: string;
  opennessEnclosure?: string;
  pavingType?: string;
}

/**
 * Extract archetype metadata for a zone by looking up its archetype id
 * properties against the archetype catalog.
 */
export function getZoneArchetypeInfo(zone: SiteZone): ArchetypeInfo {
  if (!zone.properties || !catalog) return {};

  const PREFIXES = ['development', 'road', 'green_space', 'plaza'] as const;

  for (const prefix of PREFIXES) {
    const archetypeId = zone.properties[`${prefix}_archetype_id`] as string | undefined;
    if (!archetypeId) continue;

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const entry = catalog.find((a: any) =>
      a.id === archetypeId || archetypeId.startsWith(a.id + '_'),
    );
    if (!entry) continue;

    const sp = entry.styleProfile || {};
    const fd = entry.facadeDetail || {};
    const rd = entry.roofDetail || {};

    // Build facade description from facadeDetail (buildings)
    const facadeParts: string[] = [];
    if (fd.primaryMaterial) facadeParts.push(fd.primaryMaterial);
    if (fd.groundFloor) facadeParts.push(`Ground floor: ${fd.groundFloor}`);
    if (fd.upperFloors) facadeParts.push(`Upper floors: ${fd.upperFloors}`);
    if (fd.cornice) facadeParts.push(`Cornice: ${fd.cornice}`);
    if (fd.colorScheme) facadeParts.push(`Colors: ${fd.colorScheme}`);

    // Build roof description (buildings)
    const roofParts: string[] = [];
    if (rd.form) roofParts.push(rd.form);
    if (rd.material) roofParts.push(rd.material);
    if (rd.features) roofParts.push(rd.features);
    if (rd.aerialAppearance) roofParts.push(`Aerial: ${rd.aerialAppearance}`);

    const materials = Array.isArray(sp.materials) ? sp.materials.join(', ') : sp.materials;

    // Road/corridor specific fields
    const corridorParts: string[] = [];
    if (sp.corridorCharacter) corridorParts.push(sp.corridorCharacter);
    if (sp.movementHierarchy) corridorParts.push(sp.movementHierarchy);
    if (sp.surfaceType) corridorParts.push(`Surface: ${sp.surfaceType}`);
    if (sp.plantingCharacter) corridorParts.push(sp.plantingCharacter);
    if (sp.edgeConditions) corridorParts.push(`Edges: ${sp.edgeConditions}`);
    if (sp.publicRealm) corridorParts.push(sp.publicRealm);

    return {
      archetypeTitle: entry.title,
      facadeDescription: facadeParts.length > 0 ? facadeParts.join('. ') : undefined,
      roofDescription: roofParts.length > 0 ? roofParts.join('. ') : undefined,
      materials: materials || undefined,
      massing: sp.massing || undefined,
      heightTendency: sp.heightTendency || undefined,
      publicRealm: sp.publicRealm || undefined,
      mapOverlayPrompt: entry.renderPrompt?.mapOverlay || entry.prompt?.subject || undefined,
      colorScheme: fd.colorScheme || undefined,
      aerialAppearance: rd.aerialAppearance || undefined,
      corridorDescription: corridorParts.length > 0 ? corridorParts.join('. ') : undefined,
      surfaceType: sp.surfaceType || sp.pavingType || undefined,
      plantingCharacter: sp.plantingCharacter || sp.plantingType || undefined,
      edgeConditions: sp.edgeConditions || undefined,
      // Park/open space specific
      landscapeCharacter: sp.landscapeCharacter || undefined,
      plantingType: sp.plantingType || undefined,
      seatingRealm: sp.seatingRealm || undefined,
      waterFeatures: sp.waterFeatures || undefined,
      opennessEnclosure: sp.opennessEnclosure || undefined,
      pavingType: sp.pavingType || undefined,
    };
  }

  return {};
}

// ---------------------------------------------------------------------------
// Spatial math utilities
// ---------------------------------------------------------------------------

/** Convert meters to approximate degrees of longitude at a given latitude. */
function metersToDegreesLng(meters: number, latDeg: number): number {
  return meters / (111_320 * Math.cos(latDeg * DEG_TO_RAD));
}

/** Convert meters to approximate degrees of latitude. */
function metersToDegreesLat(meters: number): number {
  return meters / METERS_PER_DEG_LAT;
}

/**
 * Compute the centroid of a polygon defined by [[lng, lat], ...].
 */
function polygonCentroid(coords: number[][]): [number, number] {
  let sumLng = 0;
  let sumLat = 0;
  const n = coords.length;
  for (const [lng, lat] of coords) {
    sumLng += lng;
    sumLat += lat;
  }
  return [sumLng / n, sumLat / n];
}

/**
 * Haversine distance in meters between two [lng, lat] points.
 */
function haversineDistance(a: [number, number], b: [number, number]): number {
  const [lng1, lat1] = a;
  const [lng2, lat2] = b;
  const dLat = (lat2 - lat1) * DEG_TO_RAD;
  const dLng = (lng2 - lng1) * DEG_TO_RAD;
  const sinLat = Math.sin(dLat / 2);
  const sinLng = Math.sin(dLng / 2);
  const h =
    sinLat * sinLat +
    Math.cos(lat1 * DEG_TO_RAD) * Math.cos(lat2 * DEG_TO_RAD) * sinLng * sinLng;
  return 2 * EARTH_RADIUS_M * Math.asin(Math.sqrt(h));
}

/**
 * Bearing from point A to point B in degrees (0 = North, clockwise).
 * Both points are [lng, lat].
 */
function bearing(a: [number, number], b: [number, number]): number {
  const [lng1, lat1] = a;
  const [lng2, lat2] = b;
  const dLng = (lng2 - lng1) * DEG_TO_RAD;
  const lat1R = lat1 * DEG_TO_RAD;
  const lat2R = lat2 * DEG_TO_RAD;
  const y = Math.sin(dLng) * Math.cos(lat2R);
  const x =
    Math.cos(lat1R) * Math.sin(lat2R) -
    Math.sin(lat1R) * Math.cos(lat2R) * Math.cos(dLng);
  const brng = Math.atan2(y, x) / DEG_TO_RAD;
  return ((brng % 360) + 360) % 360;
}

/**
 * Ray-casting point-in-polygon test.
 * polygon is [[lng, lat], ...], point is [lng, lat].
 */
function pointInPolygon(point: [number, number], polygon: [number, number][]): boolean {
  const [px, py] = point;
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const [xi, yi] = polygon[i];
    const [xj, yj] = polygon[j];
    const intersects =
      yi > py !== yj > py &&
      px < ((xj - xi) * (py - yi)) / (yj - yi) + xi;
    if (intersects) inside = !inside;
  }
  return inside;
}

/**
 * Check if two line segments (a1-a2) and (b1-b2) intersect.
 */
function segmentsIntersect(
  a1: [number, number],
  a2: [number, number],
  b1: [number, number],
  b2: [number, number],
): boolean {
  const cross = (o: [number, number], a: [number, number], b: [number, number]) =>
    (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);

  const d1 = cross(b1, b2, a1);
  const d2 = cross(b1, b2, a2);
  const d3 = cross(a1, a2, b1);
  const d4 = cross(a1, a2, b2);

  if (((d1 > 0 && d2 < 0) || (d1 < 0 && d2 > 0)) &&
      ((d3 > 0 && d4 < 0) || (d3 < 0 && d4 > 0))) {
    return true;
  }

  // Collinear / on-segment checks omitted for performance — the
  // point-in-polygon tests already cover degenerate overlaps.
  return false;
}

/**
 * Check if two polygons intersect (any vertex inside the other OR any edges cross).
 */
function polygonsIntersect(
  polyA: [number, number][],
  polyB: [number, number][],
): boolean {
  // Vertex-in-polygon checks
  for (const pt of polyA) {
    if (pointInPolygon(pt, polyB)) return true;
  }
  for (const pt of polyB) {
    if (pointInPolygon(pt, polyA)) return true;
  }

  // Edge-edge intersection checks
  for (let i = 0; i < polyA.length; i++) {
    const a1 = polyA[i];
    const a2 = polyA[(i + 1) % polyA.length];
    for (let j = 0; j < polyB.length; j++) {
      const b1 = polyB[j];
      const b2 = polyB[(j + 1) % polyB.length];
      if (segmentsIntersect(a1, a2, b1, b2)) return true;
    }
  }

  return false;
}

// ---------------------------------------------------------------------------
// Public API — view cone
// ---------------------------------------------------------------------------

/**
 * Calculate a triangular view-cone polygon from a position, viewing angle,
 * and field of view. Returns [[lng, lat], ...] forming a closed triangle
 * (center + two far-edge points + center again to close).
 *
 * @param center   Pegman position as [lng, lat]
 * @param angleDeg Heading in degrees (0 = North, 90 = East, clockwise)
 * @param fovDeg   Field of view in degrees (default 60)
 * @param distanceMeters  View distance in meters (default 150)
 */
export function getViewConePolygon(
  center: [number, number],
  angleDeg: number,
  fovDeg: number = 45,
  distanceMeters: number = 120,
): [number, number][] {
  const [cLng, cLat] = center;
  const halfFov = fovDeg / 2;

  // Two rays at angleDeg ± halfFov
  const leftAngle = ((angleDeg - halfFov) % 360 + 360) % 360;
  const rightAngle = ((angleDeg + halfFov) % 360 + 360) % 360;

  const dLat = metersToDegreesLat(distanceMeters);
  const dLng = metersToDegreesLng(distanceMeters, cLat);

  // Convert compass heading to math angle:
  // compass 0=N → math angle π/2, compass 90=E → math angle 0
  const toXY = (compassDeg: number): [number, number] => {
    const rad = (90 - compassDeg) * DEG_TO_RAD;
    const lng = cLng + dLng * Math.cos(rad);
    const lat = cLat + dLat * Math.sin(rad);
    return [lng, lat];
  };

  const leftPt = toXY(leftAngle);
  const rightPt = toXY(rightAngle);

  // Return closed polygon: center → left far edge → right far edge → center
  return [center, leftPt, rightPt, center];
}

// ---------------------------------------------------------------------------
// Public API — zone intersection
// ---------------------------------------------------------------------------

/**
 * Find which site zones intersect with a view cone polygon.
 * Excludes `site_boundary` zones since they encompass the entire site.
 *
 * Uses point-in-polygon checks (any zone vertex inside cone, any cone vertex
 * inside zone) plus edge-crossing tests for robust detection.
 */
export function getZonesInViewCone(
  siteZones: SiteZone[],
  conePolygon: [number, number][],
): SiteZone[] {
  const result: SiteZone[] = [];

  for (const zone of siteZones) {
    // Skip site boundaries — they wrap everything
    if (zone.zone_type === 'site_boundary') continue;

    if (!zone.coordinates || zone.coordinates.length < 2) continue;

    const zoneCoords = zone.coordinates as [number, number][];

    // For lines (roads/paths with only 2 points), check if either endpoint
    // is inside the cone or if the line segment crosses the cone
    if (zoneCoords.length === 2) {
      const inCone = pointInPolygon(zoneCoords[0], conePolygon) ||
                     pointInPolygon(zoneCoords[1], conePolygon);
      if (inCone) {
        result.push(zone);
      }
      continue;
    }

    if (polygonsIntersect(conePolygon, zoneCoords)) {
      result.push(zone);
    }
  }

  return result;
}

// ---------------------------------------------------------------------------
// Public API — distance sorting
// ---------------------------------------------------------------------------

export interface ZoneWithDistance {
  zone: SiteZone;
  /** Distance from pegman to zone centroid in meters. */
  distance: number;
  /** Position of the zone relative to the pegman's viewing direction. */
  relativePosition: 'left' | 'center' | 'right';
  /** Degrees from center of view (negative = left, positive = right). */
  angularOffset: number;
  /** Angular width of the zone from the camera in degrees. */
  angularWidth: number;
  /** Estimated percentage of the frame width this zone occupies (0-100). */
  framePercent: number;
  /** Left edge position as percentage of frame (0=left edge, 100=right edge). */
  frameLeftPct: number;
  /** Right edge position as percentage of frame. */
  frameRightPct: number;
}

/**
 * Calculate the angular extent (min/max bearing) of a zone's polygon
 * as seen from the pegman position, relative to the view direction.
 */
function calcZoneAngularExtent(
  zoneCoords: number[][],
  pegmanPos: [number, number],
  pegmanAngle: number,
): { minAngle: number; maxAngle: number; angularWidth: number; centerAngle: number } {
  let minRel = Infinity;
  let maxRel = -Infinity;

  for (const coord of zoneCoords) {
    const brng = bearing(pegmanPos, [coord[0], coord[1]] as [number, number]);
    let rel = brng - pegmanAngle;
    if (rel > 180) rel -= 360;
    if (rel < -180) rel += 360;
    if (rel < minRel) minRel = rel;
    if (rel > maxRel) maxRel = rel;
  }

  return {
    minAngle: minRel,
    maxAngle: maxRel,
    angularWidth: maxRel - minRel,
    centerAngle: (minRel + maxRel) / 2,
  };
}

/**
 * Sort zones by distance from the pegman position (nearest first) and
 * annotate each with distance, relative bearing, angular width, and
 * frame percentage based on the view cone geometry.
 */
export function sortZonesByDistance(
  zones: SiteZone[],
  pegmanPos: [number, number],
  pegmanAngle: number,
  fovDeg: number = 45,
): ZoneWithDistance[] {
  const halfFov = fovDeg / 2;

  const annotated: ZoneWithDistance[] = zones.map((zone) => {
    const centroid = polygonCentroid(zone.coordinates) as [number, number];
    const dist = haversineDistance(pegmanPos, centroid);

    // Angular extent of this zone from the camera
    const angular = calcZoneAngularExtent(zone.coordinates, pegmanPos, pegmanAngle);

    // Clamp to FOV bounds
    const clampedMin = Math.max(angular.minAngle, -halfFov);
    const clampedMax = Math.min(angular.maxAngle, halfFov);
    const clampedWidth = Math.max(0, clampedMax - clampedMin);

    // Frame percentage: what fraction of the FOV this zone occupies
    const framePercent = Math.round((clampedWidth / fovDeg) * 100);

    // Frame position: left/right edges as percentage (0% = left, 100% = right)
    const frameLeftPct = Math.round(((clampedMin + halfFov) / fovDeg) * 100);
    const frameRightPct = Math.round(((clampedMax + halfFov) / fovDeg) * 100);

    let relativePosition: 'left' | 'center' | 'right';
    if (angular.centerAngle < -8) {
      relativePosition = 'left';
    } else if (angular.centerAngle > 8) {
      relativePosition = 'right';
    } else {
      relativePosition = 'center';
    }

    return {
      zone,
      distance: dist,
      relativePosition,
      angularOffset: angular.centerAngle,
      angularWidth: clampedWidth,
      framePercent,
      frameLeftPct,
      frameRightPct,
    };
  });

  annotated.sort((a, b) => a.distance - b.distance);
  return annotated;
}

// ---------------------------------------------------------------------------
// Public API — prompt building
// ---------------------------------------------------------------------------

/** Human-readable label for a zone type. */
function zoneTypeLabel(zoneType: string): string {
  const labels: Record<string, string> = {
    building: 'Building',
    green_space: 'Green Space / Park',
    road: 'Road / Path',
    parking: 'Parking Area',
    water: 'Water Feature',
    plaza: 'Plaza / Public Space',
  };
  return labels[zoneType] || zoneType.replace(/_/g, ' ');
}

// Depth classification is now done inline in buildStreetViewPrompt

/**
 * Build a detailed description for a single zone based on its type and
 * archetype metadata, suitable for street-level rendering.
 */
function describeZoneForStreetView(
  zone: SiteZone,
  info: ArchetypeInfo,
): string {
  const parts: string[] = [];

  // Title / name
  const title = info.archetypeTitle || zone.name || zoneTypeLabel(zone.zone_type);
  parts.push(title);

  // Height info for buildings
  if (zone.zone_type === 'building') {
    const floors = zone.properties?.floors as number | undefined;
    if (floors) {
      parts[0] = `${title} (${floors}-story)`;
    } else if (info.heightTendency) {
      parts[0] = `${title} (${info.heightTendency})`;
    }

    // Facade
    if (info.facadeDescription) {
      parts.push(info.facadeDescription);
    }
    // Roof visible at distance
    if (info.roofDescription) {
      parts.push(`Roof: ${info.roofDescription}`);
    }
    // Massing
    if (info.massing) {
      parts.push(`Massing: ${info.massing}`);
    }
    // Ground-level public realm
    if (info.publicRealm) {
      parts.push(info.publicRealm);
    }
  } else if (zone.zone_type === 'road') {
    // Road/path corridor
    if (info.corridorDescription) {
      parts.push(info.corridorDescription);
    } else {
      if (info.surfaceType) parts.push(`Surface: ${info.surfaceType}`);
      if (info.plantingCharacter) parts.push(info.plantingCharacter);
      if (info.edgeConditions) parts.push(`Edges: ${info.edgeConditions}`);
    }
  } else if (zone.zone_type === 'green_space' || zone.zone_type === 'parking') {
    // Parks, plazas, green spaces — use rich landscape metadata
    if (info.landscapeCharacter) {
      // Best source: the full landscape character description from openSpaceArchetypes
      parts.push(info.landscapeCharacter);
    } else if (info.mapOverlayPrompt) {
      parts.push(info.mapOverlayPrompt);
    }
    // Layer additional details
    if (info.plantingType) parts.push(`Planting: ${info.plantingType}`);
    if (info.pavingType) parts.push(`Paths: ${info.pavingType}`);
    if (info.seatingRealm) parts.push(`Seating: ${info.seatingRealm}`);
    if (info.waterFeatures && info.waterFeatures !== 'None') parts.push(`Water: ${info.waterFeatures}`);
    if (info.opennessEnclosure) parts.push(`Character: ${info.opennessEnclosure}`);
    // Fallbacks if no rich data
    if (parts.length <= 1) {
      if (info.plantingCharacter) parts.push(info.plantingCharacter);
      if (info.surfaceType) parts.push(`Surface: ${info.surfaceType}`);
      if (info.publicRealm) parts.push(info.publicRealm);
    }
  } else if (zone.zone_type === 'water') {
    if (info.mapOverlayPrompt) {
      parts.push(info.mapOverlayPrompt);
    } else {
      parts.push('calm water surface with natural edges and sky reflections');
    }
  }

  return parts.join(' — ');
}

/**
 * Build a rich street-level prompt from the pegman position, heading,
 * and visible zones sorted by distance.
 *
 * The prompt follows a structured spatial layout (foreground / midground /
 * background, left / center / right) so the generative model can compose
 * the scene accurately.
 */
export function buildStreetViewPrompt(
  _pegmanPos: [number, number],
  angleDeg: number,
  visibleZones: ZoneWithDistance[],
  styleModifier?: string,
): string {
  const direction = compassDirection(angleDeg);

  const lines: string[] = [];

  // Strong framing instruction
  lines.push(
    `Generate a wide 16:9 street-level photograph of an urban development, ` +
    `as seen from eye level (1.7m height) looking ${direction}. ` +
    `The image MUST show ALL of the following elements composed together in a single coherent scene. ` +
    `CRITICAL DEPTH RULE: Elements that are CLOSE (under 30m) must appear LARGE and fill much of the frame. ` +
    `Elements that are FAR (over 80m) must appear SMALL, near the horizon line. ` +
    `A zone 20m away should appear roughly 4x larger than a zone 80m away.`,
  );

  if (visibleZones.length === 0) {
    lines.push('The view shows an empty development site with cleared ground and surrounding neighborhood.');
  } else {
    // Separate by depth for structured description
    const foreground = visibleZones.filter(z => z.distance < 30);
    const midground = visibleZones.filter(z => z.distance >= 30 && z.distance < 80);
    const background = visibleZones.filter(z => z.distance >= 80);

    if (foreground.length > 0) {
      lines.push('=== FOREGROUND (CLOSEST, LARGEST IN FRAME — these dominate the view) ===');
      for (const entry of foreground) {
        const info = getZoneArchetypeInfo(entry.zone);
        const desc = describeZoneForStreetView(entry.zone, info);
        const floors = Number(entry.zone.properties?.floors) || Number(entry.zone.properties?.max_floors) || 0;
        const heightDesc = floors > 0 ? `${floors}-story building, ` : '';
        const posDesc = entry.relativePosition === 'left' ? 'on the LEFT side' :
                        entry.relativePosition === 'right' ? 'on the RIGHT side' : 'in the CENTER';

        lines.push(
          `LARGE, ${posDesc} (frame ${entry.frameLeftPct}%-${entry.frameRightPct}%), ` +
          `only ~${Math.round(entry.distance)}m away, ${heightDesc}` +
          `filling ${entry.framePercent}% of frame width: ${desc}`,
        );
      }
    }

    if (midground.length > 0) {
      lines.push('=== MIDGROUND (MEDIUM SIZE — visible but not dominant) ===');
      for (const entry of midground) {
        const info = getZoneArchetypeInfo(entry.zone);
        const desc = describeZoneForStreetView(entry.zone, info);
        const floors = Number(entry.zone.properties?.floors) || Number(entry.zone.properties?.max_floors) || 0;
        const heightDesc = floors > 0 ? `${floors}-story, ` : '';
        const posDesc = entry.relativePosition === 'left' ? 'LEFT' :
                        entry.relativePosition === 'right' ? 'RIGHT' : 'CENTER';

        lines.push(
          `Medium-sized, ${posDesc} (frame ${entry.frameLeftPct}%-${entry.frameRightPct}%), ` +
          `~${Math.round(entry.distance)}m away, ${heightDesc}${desc}`,
        );
      }
    }

    if (background.length > 0) {
      lines.push('=== BACKGROUND (SMALL, near horizon — these should look distant) ===');
      for (const entry of background) {
        const info = getZoneArchetypeInfo(entry.zone);
        const desc = describeZoneForStreetView(entry.zone, info);
        const floors = Number(entry.zone.properties?.floors) || Number(entry.zone.properties?.max_floors) || 0;
        const heightDesc = floors > 0 ? `${floors}-story, ` : '';
        const posDesc = entry.relativePosition === 'left' ? 'LEFT' :
                        entry.relativePosition === 'right' ? 'RIGHT' : 'CENTER';

        lines.push(
          `Small and distant, ${posDesc} (frame ${entry.frameLeftPct}%-${entry.frameRightPct}%), ` +
          `~${Math.round(entry.distance)}m away, ${heightDesc}${desc}`,
        );
      }
    }
  }

  // Ground plane
  lines.push(
    'GROUND: Paved sidewalk and street in the immediate foreground with curbs and street trees. ' +
    'The ground plane recedes naturally toward the horizon, connecting all described elements.',
  );

  // Style modifier
  if (styleModifier) {
    lines.push(styleModifier);
  }

  // Closing quality directives
  lines.push(
    'STYLE: Photorealistic architectural visualization photograph. Sunny day, warm golden hour lighting. ' +
    'Sharp material detail on close elements, atmospheric haze on distant ones. 35mm lens. ' +
    '8K resolution, no people, no text overlays, no watermarks.',
  );

  return lines.join('\n\n');
}

// ---------------------------------------------------------------------------
// Perspective depth map — color-coded guide image for spatial accuracy
// ---------------------------------------------------------------------------

const DEPTH_MAP_WIDTH = 1024;
const DEPTH_MAP_HEIGHT = 576; // 16:9
const EYE_HEIGHT_M = 1.7;
const FLOOR_HEIGHT_M = 3.2;
// sky color used inline in gradient
const GROUND_COLOR = '#808075';
const DEFAULT_ZONE_COLORS: Record<string, string> = {
  building: '#E03C31',
  green_space: '#4CAF50',
  road: '#808080',
  water: '#2196F3',
  parking: '#9E9E9E',
};

/**
 * Generate a color-coded perspective depth map showing zone positions
 * from the pegman's viewpoint. Uses the pre-computed frame percentages
 * from ZoneWithDistance for accurate horizontal positioning, and
 * distance-based perspective for vertical sizing.
 *
 * Returns base64-encoded PNG (without data URI prefix).
 */
export function generateDepthMap(
  _pegmanPos: [number, number],
  angleDeg: number,
  visibleZones: ZoneWithDistance[],
): string {
  const canvas = document.createElement('canvas');
  canvas.width = DEPTH_MAP_WIDTH;
  canvas.height = DEPTH_MAP_HEIGHT;
  const ctx = canvas.getContext('2d')!;

  const horizonY = DEPTH_MAP_HEIGHT * 0.50;

  // Draw sky gradient
  const skyGrad = ctx.createLinearGradient(0, 0, 0, horizonY);
  skyGrad.addColorStop(0, '#6BA3D6');
  skyGrad.addColorStop(1, '#B8D4E8');
  ctx.fillStyle = skyGrad;
  ctx.fillRect(0, 0, DEPTH_MAP_WIDTH, horizonY);

  // Draw ground plane
  const groundGrad = ctx.createLinearGradient(0, horizonY, 0, DEPTH_MAP_HEIGHT);
  groundGrad.addColorStop(0, '#a0a090');
  groundGrad.addColorStop(1, GROUND_COLOR);
  ctx.fillStyle = groundGrad;
  ctx.fillRect(0, horizonY, DEPTH_MAP_WIDTH, DEPTH_MAP_HEIGHT - horizonY);

  // Sort zones back-to-front (farthest first) so nearer zones overdraw
  const sortedBackToFront = [...visibleZones].sort((a, b) => b.distance - a.distance);

  for (const entry of sortedBackToFront) {
    const zone = entry.zone;
    const color = zone.color || DEFAULT_ZONE_COLORS[zone.zone_type] || '#888888';

    // Use frame percentages for horizontal positioning
    const leftX = (entry.frameLeftPct / 100) * DEPTH_MAP_WIDTH;
    const rightX = (entry.frameRightPct / 100) * DEPTH_MAP_WIDTH;
    const width = rightX - leftX;
    if (width < 2) continue; // too narrow to draw

    // Determine building height and apparent size based on distance
    const isBuilding = zone.zone_type === 'building' || zone.zone_type === 'residential' || zone.zone_type === 'development_area';
    const floors = Number(zone.properties?.floors) || Number(zone.properties?.max_floors) || (isBuilding ? 4 : 0);
    const heightM = floors * FLOOR_HEIGHT_M;

    // Distance-based perspective: closer = taller and lower base
    // Normalize distance: 10m = very close, 150m = far
    const distNorm = Math.max(0.1, Math.min(1, entry.distance / 150));
    const perspScale = 1 / (0.3 + distNorm * 0.7); // closer = larger scale

    if (isBuilding && heightM > 0) {
      // Building: draw as a colored rectangle
      // Base sits on ground, height proportional to floors and distance
      const apparentHeight = Math.min(
        horizonY * 0.9,
        (heightM / EYE_HEIGHT_M) * 30 * perspScale,
      );
      // Base Y: closer buildings have base further below horizon
      const baseY = horizonY + (DEPTH_MAP_HEIGHT - horizonY) * (0.1 + distNorm * 0.3);
      const topY = baseY - apparentHeight;

      ctx.fillStyle = color;
      ctx.globalAlpha = 0.9;
      ctx.fillRect(leftX, Math.max(0, topY), width, baseY - Math.max(0, topY));

      // Outline
      ctx.strokeStyle = '#000000';
      ctx.lineWidth = 2;
      ctx.globalAlpha = 0.6;
      ctx.strokeRect(leftX, Math.max(0, topY), width, baseY - Math.max(0, topY));

      // Label
      ctx.globalAlpha = 1;
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 11px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(
        `${floors}F`,
        leftX + width / 2,
        Math.max(0, topY) + 14,
      );
    } else if (zone.zone_type === 'green_space' || zone.zone_type === 'parking') {
      // Parks and green spaces — draw ground patch PLUS tree canopy above horizon
      // Ground patch (larger for closer parks)
      const groundTop = horizonY + (DEPTH_MAP_HEIGHT - horizonY) * (0.02 + distNorm * 0.25);
      const groundBot = horizonY + (DEPTH_MAP_HEIGHT - horizonY) * (0.25 + distNorm * 0.45);

      ctx.fillStyle = color;
      ctx.globalAlpha = 0.75;

      // Draw ground as trapezoid
      const narrowing = distNorm * 0.1 * width;
      ctx.beginPath();
      ctx.moveTo(leftX + narrowing, groundTop);
      ctx.lineTo(rightX - narrowing, groundTop);
      ctx.lineTo(rightX, groundBot);
      ctx.lineTo(leftX, groundBot);
      ctx.closePath();
      ctx.fill();

      ctx.strokeStyle = '#000000';
      ctx.lineWidth = 1;
      ctx.globalAlpha = 0.3;
      ctx.stroke();

      // Draw tree canopy circles above the ground — parks have vertical presence!
      // Canopy height scales inversely with distance (close = tall trees)
      const treeHeight = Math.min(horizonY * 0.7, 60 * perspScale);
      const numTrees = Math.max(2, Math.min(6, Math.round(width / 40)));
      const treeSpacing = width / (numTrees + 1);

      ctx.globalAlpha = 0.65;
      for (let t = 1; t <= numTrees; t++) {
        const treeX = leftX + t * treeSpacing;
        const treeBaseY = groundTop;
        const treeTopY = treeBaseY - treeHeight;
        const canopyRadius = Math.max(8, 20 * perspScale);

        // Tree trunk
        ctx.fillStyle = '#5D4037';
        ctx.fillRect(treeX - 2, treeTopY + canopyRadius * 0.6, 4, treeHeight - canopyRadius * 0.6);

        // Canopy (green circle)
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(treeX, treeTopY + canopyRadius, canopyRadius, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.globalAlpha = 1;

    } else if (zone.zone_type === 'water') {
      // Water — draw as reflective ground patch with slight blue gradient
      const groundTop = horizonY + (DEPTH_MAP_HEIGHT - horizonY) * (0.03 + distNorm * 0.28);
      const groundBot = horizonY + (DEPTH_MAP_HEIGHT - horizonY) * (0.2 + distNorm * 0.45);

      const waterGrad = ctx.createLinearGradient(0, groundTop, 0, groundBot);
      waterGrad.addColorStop(0, '#64B5F6');
      waterGrad.addColorStop(1, color || '#2196F3');
      ctx.fillStyle = waterGrad;
      ctx.globalAlpha = 0.8;

      const narrowing = distNorm * 0.1 * width;
      ctx.beginPath();
      ctx.moveTo(leftX + narrowing, groundTop);
      ctx.lineTo(rightX - narrowing, groundTop);
      ctx.lineTo(rightX, groundBot);
      ctx.lineTo(leftX, groundBot);
      ctx.closePath();
      ctx.fill();
      ctx.globalAlpha = 1;

    } else {
      // Roads and other ground-level zones
      const groundTop = horizonY + (DEPTH_MAP_HEIGHT - horizonY) * (0.1 + distNorm * 0.3);
      const groundBot = horizonY + (DEPTH_MAP_HEIGHT - horizonY) * (0.2 + distNorm * 0.45);

      ctx.fillStyle = color;
      ctx.globalAlpha = 0.7;

      const narrowing = distNorm * 0.12 * width;
      ctx.beginPath();
      ctx.moveTo(leftX + narrowing, groundTop);
      ctx.lineTo(rightX - narrowing, groundTop);
      ctx.lineTo(rightX, groundBot);
      ctx.lineTo(leftX, groundBot);
      ctx.closePath();
      ctx.fill();
      ctx.globalAlpha = 1;
    }
  }

  // Add zone name labels
  ctx.globalAlpha = 1;
  for (const entry of visibleZones) {
    const info = getZoneArchetypeInfo(entry.zone);
    const title = info.archetypeTitle || entry.zone.name || zoneTypeLabel(entry.zone.zone_type);
    const centerX = ((entry.frameLeftPct + entry.frameRightPct) / 2 / 100) * DEPTH_MAP_WIDTH;

    ctx.fillStyle = 'rgba(0,0,0,0.7)';
    ctx.font = '10px sans-serif';
    ctx.textAlign = 'center';
    const textWidth = ctx.measureText(title).width;
    const labelY = DEPTH_MAP_HEIGHT - 35;
    ctx.fillRect(centerX - textWidth / 2 - 3, labelY - 10, textWidth + 6, 14);
    ctx.fillStyle = '#ffffff';
    ctx.fillText(title, centerX, labelY);
  }

  // Bottom bar label
  ctx.fillStyle = 'rgba(0,0,0,0.6)';
  ctx.fillRect(0, DEPTH_MAP_HEIGHT - 22, DEPTH_MAP_WIDTH, 22);
  ctx.fillStyle = '#ffffff';
  ctx.font = '11px sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText(
    `Street View Guide — Looking ${compassDirection(angleDeg)} — Colored blocks show zone positions`,
    DEPTH_MAP_WIDTH / 2,
    DEPTH_MAP_HEIGHT - 7,
  );

  return canvas.toDataURL('image/png').split(',')[1];
}

// ---------------------------------------------------------------------------
// Public API — async generator
// ---------------------------------------------------------------------------

export interface StreetViewResult {
  /** URL or data-URI of the generated image. */
  imageUrl: string;
  /** The prompt that was sent to the API. */
  prompt: string;
}

/**
 * End-to-end street-view generation pipeline:
 * 1. Compute view cone from position + angle
 * 2. Find intersecting zones
 * 3. Sort by distance and annotate relative positions
 * 4. Build structured prompt
 * 5. POST to the render API (text-only, no source image)
 *
 * Returns the generated image URL and prompt, or null on failure.
 */
export async function generateStreetView(
  pegmanPos: [number, number],
  angleDeg: number,
  siteZones: SiteZone[],
  options?: {
    fovDeg?: number;
    distanceMeters?: number;
    styleModifier?: string;
  },
): Promise<StreetViewResult | null> {
  const fov = options?.fovDeg ?? 45;
  const distance = options?.distanceMeters ?? 120;

  // 1. View cone
  const cone = getViewConePolygon(pegmanPos, angleDeg, fov, distance);

  // 2. Zone intersection
  const intersecting = getZonesInViewCone(siteZones, cone);

  // 3. Sort by distance with angular analysis
  const sorted = sortZonesByDistance(intersecting, pegmanPos, angleDeg, fov);

  // 4. Build prompt
  const prompt = buildStreetViewPrompt(pegmanPos, angleDeg, sorted, options?.styleModifier);

  // 5. Generate color-coded depth map as spatial guide
  const depthMapBase64 = generateDepthMap(pegmanPos, angleDeg, sorted);

  // 6. Call render API with depth map as guide image
  try {
    const enhancedPrompt =
      prompt +
      '\n\nIMPORTANT: The attached image is a color-coded spatial guide showing where each zone ' +
      'should appear in the final render. Each colored block represents a different building or ' +
      'landscape zone. Use the position, size, and color of each block to place the corresponding ' +
      'architectural element in the correct location. Replace each colored block with the photorealistic ' +
      'version described in the prompt above. Maintain the same spatial layout and proportions.';

    const response = await axios.post(RENDER_API_URL, {
      prompt: enhancedPrompt,
      image_base64: depthMapBase64,
      aspect_ratio: '16:9',
    }, { timeout: 180_000 });

    const resultBase64: string | undefined = response.data?.image_base64;

    if (!resultBase64) {
      console.error('[useStreetViewRender] No image data in API response', response.data);
      return null;
    }

    const imageUrl = `data:image/png;base64,${resultBase64}`;
    return { imageUrl, prompt };
  } catch (err) {
    console.error('[useStreetViewRender] Render API call failed:', err);
    return null;
  }
}

// ---------------------------------------------------------------------------
// React Hook
// ---------------------------------------------------------------------------

/**
 * Convenience React hook that exposes all street-view render utilities.
 *
 * Usage:
 * ```ts
 * const { getViewConePolygon, generateStreetView } = useStreetViewRender();
 * const result = await generateStreetView(pegmanPos, angle, zones);
 * ```
 */
export function useStreetViewRender() {
  const generate = useCallback(
    (
      pegmanPos: [number, number],
      angleDeg: number,
      siteZones: SiteZone[],
      options?: {
        fovDeg?: number;
        distanceMeters?: number;
        styleModifier?: string;
      },
    ) => generateStreetView(pegmanPos, angleDeg, siteZones, options),
    [],
  );

  return {
    getViewConePolygon,
    getZonesInViewCone,
    sortZonesByDistance,
    buildStreetViewPrompt,
    generateStreetView: generate,
  } as const;
}
