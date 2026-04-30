/**
 * useStreetViewRender — utilities and React hook for generating street-level
 * architectural renders from a pegman position and viewing angle.
 *
 * Provides view-cone geometry, zone intersection, distance sorting, and
 * structured prompt building for Vertex AI Imagen 3 text-to-image generation.
 */
import { useCallback } from 'react';
import axios from 'axios';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import buildingCatalog from '@/data/buildingArchetypes.json';
import openSpaceCatalog from '@/data/openSpaceArchetypes.json';
import streetPathCatalog from '@/data/streetPathArchetypes.json';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const API_BASE = import.meta.env.VITE_API_URL || '';
const RENDER_API_URL = `${API_BASE}/api/v1/render/generate`;
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
  fovDeg: number = 70,
  distanceMeters: number = 200,
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
 * Buffer a polyline into a polygon by offsetting perpendicular to each segment.
 * Takes a line [[lng,lat], ...] and a width in meters, returns a polygon [[lng,lat], ...].
 * Uses a simple perpendicular offset approach — good enough for street widths.
 */
export function bufferLineToPolygon(
  lineCoords: number[][],
  widthMeters: number,
): number[][] {
  if (lineCoords.length < 2) return lineCoords;

  const halfWidth = widthMeters / 2;
  const leftSide: number[][] = [];
  const rightSide: number[][] = [];

  for (let i = 0; i < lineCoords.length; i++) {
    const [lng, lat] = lineCoords[i];

    // Calculate the direction vector at this point
    let dx = 0, dy = 0;
    if (i < lineCoords.length - 1) {
      dx += lineCoords[i + 1][0] - lng;
      dy += lineCoords[i + 1][1] - lat;
    }
    if (i > 0) {
      dx += lng - lineCoords[i - 1][0];
      dy += lat - lineCoords[i - 1][1];
    }

    // Normalize
    const len = Math.sqrt(dx * dx + dy * dy);
    if (len < 1e-12) continue;
    dx /= len;
    dy /= len;

    // Perpendicular vector (rotated 90°)
    const px = -dy;
    const py = dx;

    // Convert meters to degrees (approximate)
    const metersPerDegLat = 110540;
    const metersPerDegLng = metersPerDegLat * Math.cos(lat * DEG_TO_RAD);
    const offsetLng = (halfWidth / metersPerDegLng) * px;
    const offsetLat = (halfWidth / metersPerDegLat) * py;

    leftSide.push([lng + offsetLng, lat + offsetLat]);
    rightSide.push([lng - offsetLng, lat - offsetLat]);
  }

  // Combine left side forward + right side reversed to form a closed polygon
  return [...leftSide, ...rightSide.reverse()];
}

/**
 * Pre-process site zones: convert street/path polylines into buffered polygons
 * so they can be detected by the view cone and rendered in the clay model.
 * Returns a new array with lines converted to polygons.
 */
export function preprocessZonesForStreetView(siteZones: SiteZone[]): SiteZone[] {
  return siteZones.map(zone => {
    const zt = zone.zone_type as string;
    const isLine = zt === 'road' || zt === 'street' || zt === 'path' || zt === 'pedestrian';

    // If it looks like a polyline (few points, or explicitly a line type)
    if (isLine && zone.coordinates && zone.coordinates.length >= 2) {
      const width = Number(zone.properties?.width) || 10; // default 10m
      const buffered = bufferLineToPolygon(zone.coordinates, width);
      if (buffered.length >= 3) {
        return {
          ...zone,
          coordinates: buffered,
          // Preserve original for reference
          properties: {
            ...zone.properties,
            _original_line_coords: zone.coordinates,
            _is_buffered_line: true,
          },
        };
      }
    }
    return zone;
  });
}

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
  fovDeg: number = 70,
): ZoneWithDistance[] {
  const halfFov = fovDeg / 2;

  const annotated: ZoneWithDistance[] = zones.filter(z => z.coordinates && z.coordinates.length >= 2).map((zone) => {
    const centroid = polygonCentroid(zone.coordinates!) as [number, number];
    const dist = haversineDistance(pegmanPos, centroid);

    // Angular extent of this zone from the camera
    const angular = calcZoneAngularExtent(zone.coordinates!, pegmanPos, pegmanAngle);

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
// Occlusion culling — remove zones hidden behind closer buildings
// ---------------------------------------------------------------------------

/** Normalize a bearing difference to [-180, 180] range. */
function angleDiff(a: number, b: number): number {
  let d = b - a;
  while (d > 180) d -= 360;
  while (d < -180) d += 360;
  return d;
}

/**
 * Cull zones that are fully occluded by closer building zones.
 *
 * Algorithm: process building zones from nearest to farthest, accumulating
 * the angular ranges (relative to pegman) that each building blocks. Any
 * non-building zone (park, street, plaza) whose angular extent is fully
 * contained within the blocked angles is removed from the visible list.
 * Building zones themselves are never culled (they're always visible as facades).
 */
export function cullOccludedZones(
  pegmanPos: [number, number],
  sortedZones: ZoneWithDistance[],
): ZoneWithDistance[] {
  const BUILDING_TYPES = new Set(['building', 'residential', 'commercial', 'industrial', 'mixed_use', 'development_area']);

  // Compute the angular extent [minBearing, maxBearing] of each zone from the pegman
  type ZoneAngles = { zone: ZoneWithDistance; minBearing: number; maxBearing: number; isBuilding: boolean };
  const zoneAngles: ZoneAngles[] = [];

  for (const z of sortedZones) {
    const coords = z.zone.coordinates as [number, number][] | undefined;
    if (!coords || coords.length < 2) {
      zoneAngles.push({ zone: z, minBearing: 0, maxBearing: 0, isBuilding: false });
      continue;
    }

    const bearings = coords.map(c => bearing(pegmanPos, c));
    // Handle wrap-around at 0/360 by checking if the spread crosses north
    const sorted = [...bearings].sort((a, b) => a - b);
    let minB = sorted[0];
    let maxB = sorted[sorted.length - 1];

    // If the angular span is > 180, the zone wraps around north (0/360)
    // In that case, shift bearings to avoid the discontinuity
    if (maxB - minB > 180) {
      const shifted = bearings.map(b => b < 180 ? b + 360 : b);
      const sortedShifted = [...shifted].sort((a, b) => a - b);
      minB = sortedShifted[0];
      maxB = sortedShifted[sortedShifted.length - 1];
    }

    const isBuilding = BUILDING_TYPES.has(z.zone.zone_type as string);
    zoneAngles.push({ zone: z, minBearing: minB, maxBearing: maxB, isBuilding });
  }

  // Sort by distance (closest first) — buildings cast shadows on things behind them
  const byDistance = [...zoneAngles].sort((a, b) => a.zone.distance - b.zone.distance);

  // Accumulate blocked angular ranges from buildings
  const blockedRanges: Array<{ min: number; max: number }> = [];

  const result: ZoneWithDistance[] = [];

  for (const za of byDistance) {
    if (za.isBuilding) {
      // Buildings are always visible (you see their facade) and they block things behind them
      result.push(za.zone);
      // Add this building's angular range to the blocked set
      blockedRanges.push({ min: za.minBearing, max: za.maxBearing });
    } else {
      // Non-building zone: check if it's fully occluded by accumulated blocked ranges
      const zoneMin = za.minBearing;
      const zoneMax = za.maxBearing;
      const zoneSpan = zoneMax - zoneMin;

      if (zoneSpan <= 0) {
        // Degenerate zone, keep it
        result.push(za.zone);
        continue;
      }

      // Check what fraction of this zone's angular extent is blocked
      let blockedDegrees = 0;
      for (const br of blockedRanges) {
        // Calculate overlap between [zoneMin, zoneMax] and [br.min, br.max]
        const overlapMin = Math.max(zoneMin, br.min);
        const overlapMax = Math.min(zoneMax, br.max);
        if (overlapMax > overlapMin) {
          blockedDegrees += overlapMax - overlapMin;
        }
      }

      const blockedFraction = blockedDegrees / zoneSpan;

      if (blockedFraction >= 0.8) {
        // Zone is 80%+ occluded — cull it
        console.log(`[StreetView] Occlusion: culled "${za.zone.zone.name || za.zone.zone.zone_type}" (${Math.round(blockedFraction * 100)}% blocked by buildings)`);
      } else {
        result.push(za.zone);
      }
    }
  }

  // Re-sort by distance (the original sort order)
  result.sort((a, b) => a.distance - b.distance);
  return result;
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
  } else if (['road', 'street', 'path', 'pedestrian'].includes(zone.zone_type as string)) {
    // Road/path corridor — rich street-level description
    const streetWidth = Number(zone.properties?.width) || 10;
    parts.push(`${streetWidth}m wide corridor`);
    if (info.corridorDescription) {
      parts.push(info.corridorDescription);
    } else {
      if (info.surfaceType) parts.push(`Surface: ${info.surfaceType}`);
      if (info.plantingCharacter) parts.push(info.plantingCharacter);
      if (info.edgeConditions) parts.push(`Edges: ${info.edgeConditions}`);
      if (info.publicRealm) parts.push(info.publicRealm);
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
/**
 * Determine what type of zone the pegman is standing inside.
 * Returns the context type AND the actual zone (for archetype lookup).
 * Searches all site zones (not just visible ones) since the standing zone
 * may be behind the camera / outside the view cone.
 */
export function detectPegmanContext(
  pegmanPos: [number, number],
  zones: ZoneWithDistance[],
  allZones?: SiteZone[],
): { context: 'park' | 'water' | 'street' | 'default'; zone?: SiteZone } {
  // First try the visible/processed zones (these have buffered street polygons)
  for (const z of zones) {
    const coords = z.zone.coordinates as [number, number][] | undefined;
    if (!coords || coords.length < 3) continue;
    if (pointInPolygon(pegmanPos, coords)) {
      const zt = z.zone.zone_type;
      if (zt === 'green_space' || zt === 'park') return { context: 'park', zone: z.zone };
      if (zt === 'water') return { context: 'water', zone: z.zone };
      if (zt === 'road' || zt === 'street' || zt === 'path' || zt === 'pedestrian') return { context: 'street', zone: z.zone };
    }
  }
  // Fallback: search all site zones (catches zones behind the camera)
  if (allZones) {
    for (const zone of allZones) {
      const coords = zone.coordinates as [number, number][] | undefined;
      if (!coords || coords.length < 3) continue;
      if (pointInPolygon(pegmanPos, coords)) {
        const zt = zone.zone_type;
        if (zt === 'green_space' || zt === 'park') return { context: 'park', zone };
        if (zt === 'water') return { context: 'water', zone };
        if (zt === 'road' || zt === 'street' || zt === 'path' || zt === 'pedestrian') return { context: 'street', zone };
      }
    }
  }

  // Nearest-zone fallback: pegman is between zones, find the closest one within 50m
  const MAX_SNAP_DISTANCE = 50; // meters
  let nearestZone: SiteZone | undefined;
  let nearestDist = Infinity;
  const searchZones = allZones || zones.map(z => z.zone);
  for (const zone of searchZones) {
    if (zone.zone_type === 'site_boundary') continue;
    const coords = zone.coordinates as [number, number][] | undefined;
    if (!coords || coords.length < 2) continue;
    // Find distance to nearest vertex of this zone
    for (const coord of coords) {
      const d = haversineDistance(pegmanPos, coord);
      if (d < nearestDist) {
        nearestDist = d;
        nearestZone = zone;
      }
    }
  }
  if (nearestZone && nearestDist <= MAX_SNAP_DISTANCE) {
    const zt = nearestZone.zone_type;
    if (zt === 'green_space' || (zt as string) === 'park') return { context: 'park', zone: nearestZone };
    if (zt === 'water') return { context: 'water', zone: nearestZone };
    if (zt === 'road' || (zt as string) === 'street' || (zt as string) === 'path' || (zt as string) === 'pedestrian')
      return { context: 'street', zone: nearestZone };
    // Default to street context if nearest zone is any other type
    return { context: 'default', zone: nearestZone };
  }

  return { context: 'default' };
}

export function buildStreetViewPrompt(
  _pegmanPos: [number, number],
  angleDeg: number,
  visibleZones: ZoneWithDistance[],
  styleModifier?: string,
  standingZoneInfo?: ArchetypeInfo,
): string {
  const direction = compassDirection(angleDeg);
  const lines: string[] = [];
  const { context: pegmanContext } = detectPegmanContext(_pegmanPos, visibleZones);

  // ─── Style instruction FIRST — Gemini weights earlier instructions more heavily ───
  if (styleModifier) {
    if (styleModifier.startsWith('PHOTO STYLE:')) {
      // Photorealistic variants (photomontage, atmospheric) — keep photographic, no "not a photograph"
      lines.push(
        `MANDATORY PHOTOGRAPHIC STYLE: ${styleModifier.replace('PHOTO STYLE: ', '')}\n` +
        `This IS a photograph. Apply the photographic style described above to every element. ` +
        `Maintain full photorealistic quality with the specific camera, lighting, and atmospheric conditions specified.`,
      );
    } else {
      // Artistic styles — override to non-photorealistic
      lines.push(
        `MANDATORY OUTPUT STYLE: ${styleModifier}\n` +
        `This is NOT a photograph. The entire output image MUST be rendered in the artistic style described above. ` +
        `Every element — buildings, landscape, sky, ground — must be rendered in this style with zero photorealistic elements.`,
      );
    }
  }

  // ─── SCHEMA-style perspective grid prompt ───
  // Uses foreground/midground/background depth planes with optical constraints

  // ─── CLAUSE 1: GEOMETRIC LOCKDOWN ───
  lines.push(
    `GEOMETRIC LOCKDOWN: Analyze the provided reference image (Image 1). It is a color-coded ` +
    `3D massing model. Strictly adhere to the perspective, building geometry, volumetric proportions, ` +
    `and structural massing shown in the reference. Do not alter the silhouette, scale, or footprint ` +
    `of any provided volume. Each colored volume maps to a specific architectural zone described below.`,
  );

  // ─── CLAUSE 2: NUMERICAL INVENTORY ───
  const buildingCount = visibleZones.filter(z =>
    z.zone.zone_type === 'building' || z.zone.zone_type === 'residential' || z.zone.zone_type === 'development_area'
  ).length;
  const parkCount = visibleZones.filter(z => z.zone.zone_type === 'green_space').length;
  const waterCount = visibleZones.filter(z => z.zone.zone_type === 'water').length;
  const streetCount = visibleZones.filter(z => {
    const zt = z.zone.zone_type as string;
    return zt === 'road' || zt === 'street' || zt === 'path' || zt === 'pedestrian';
  }).length;
  lines.push(
    `NUMERICAL INVENTORY: This scene contains exactly ${visibleZones.length} zones: ` +
    `${buildingCount} building(s), ${parkCount} park(s), ${waterCount} water feature(s), ` +
    `${streetCount} street/path(s). Render ONLY these elements. Do not add any additional structures.`,
  );

  // ─── CLAUSE 3: VOID DEFINITION (context-aware, archetype-enriched) ───
  const isWinter = styleModifier?.toLowerCase().includes('winter') ?? false;
  let voidSurface: string;
  if (isWinter) {
    // Winter-specific void surfaces
    if (pegmanContext === 'park') {
      voidSurface = 'snow-covered ground with soft undulating drifts over lawn areas, bare deciduous canopies with visible branch architecture, snow-laden evergreens with heavy clumps on branches, undisturbed powder with small-animal tracks';
    } else if (pegmanContext === 'water') {
      voidSurface = 'a milky translucent frozen surface with frost patterns, visible texture cracks, and thin snow dusting along the shoreline';
    } else if (pegmanContext === 'street' && standingZoneInfo?.surfaceType) {
      voidSurface = `a plowed surface of ${standingZoneInfo.surfaceType} with salt-grit residue, thin slush patches, tire tracks in compacted snow, and sculptural snow windrows at curb edges`;
    } else {
      voidSurface = 'concrete pavement with mottled salt residue, thin black-ice patches reflecting surrounding architecture, and compacted snow at edges';
    }
  } else if (pegmanContext === 'park') {
    voidSurface = standingZoneInfo?.landscapeCharacter
      || 'a continuous, manicured grass lawn with scattered mature trees and natural ground cover';
  } else if (pegmanContext === 'water') {
    voidSurface = 'a calm, reflective water surface with natural shoreline vegetation';
  } else if (pegmanContext === 'street' && standingZoneInfo?.surfaceType) {
    const parts = [`a continuous surface of ${standingZoneInfo.surfaceType}`];
    if (standingZoneInfo.plantingCharacter) parts.push(`with ${standingZoneInfo.plantingCharacter}`);
    voidSurface = parts.join(' ');
  } else {
    voidSurface = 'a flat, unbroken, deserted concrete pavement surface';
  }
  const skyDesc = isWinter
    ? 'a pale blue-grey winter overcast gradient'
    : 'a continuous atmospheric gradient';
  lines.push(
    `VOID DEFINITION: All space between the defined zones consists of ${voidSurface}. ` +
    `The background behind all structures consists solely ` +
    `of a clear, unobstructed skyline meeting a flat, empty horizon. The sky is ${skyDesc} ` +
    `with no additional towers, buildings, or structures on the horizon.`,
  );

  // ─── COLOR-TO-ZONE MAPPING LEGEND ───
  const DEFAULT_ZONE_COLORS: Record<string, string> = {
    building: '#E03C31', residential: '#E03C31', development_area: '#E03C31',
    green_space: '#4CAF50', water: '#2196F3',
    road: '#757575', street: '#757575', path: '#9E9E9E', pedestrian: '#8D6E63',
  };
  const colorLegend = visibleZones.map(entry => {
    const info = getZoneArchetypeInfo(entry.zone);
    const name = info.archetypeTitle || entry.zone.name || zoneTypeLabel(entry.zone.zone_type);
    const color = entry.zone.color || DEFAULT_ZONE_COLORS[entry.zone.zone_type] || '#888888';
    return `  • The ${color} colored volume = "${name}"`;
  });
  lines.push(
    `COLOR-TO-ZONE MAPPING (match the colored volumes in Image 1):\n${colorLegend.join('\n')}\n` +
    `Apply photorealistic materials and textures ONLY within each color zone's boundary. ` +
    `Do not allow materials from one zone to bleed into adjacent zones.`,
  );

  lines.push(
    `PERSPECTIVE GRID LAYOUT: 3-Tier Depth Frustum (Foreground, Midground, Background).`,
  );
  lines.push(
    `CAMERA PARAMETERS: ${pegmanContext === 'park' ? 'Park pathway' : pegmanContext === 'water' ? 'Waterfront promenade' : 'Street-level'} perspective, ` +
    `camera height fixed at exactly 1.7 meters, ` +
    `looking ${direction}. 50mm lens, f/8 aperture, deep focus. 16:9 wide panoramic frame.`,
  );

  // Categorize zones into depth planes
  const foreground: ZoneWithDistance[] = []; // < 30m
  const midground: ZoneWithDistance[] = [];  // 30-80m
  const background: ZoneWithDistance[] = []; // > 80m

  for (const z of visibleZones) {
    if (z.distance < 30) foreground.push(z);
    else if (z.distance < 80) midground.push(z);
    else background.push(z);
  }

  // ─── FOREGROUND PLANE ───
  lines.push(`═══ FOREGROUND PLANE (bottom 25% of frame, closest to camera) ═══`);
  lines.push(
    `Spatial Position: Immediate proximity to the camera lens, dominating the lower quarter of the frame.`,
  );
  if (foreground.length > 0) {
    const fgDescriptions = foreground.map(entry => {
      const info = getZoneArchetypeInfo(entry.zone);
      const desc = describeZoneForStreetView(entry.zone, info);
      const name = info.archetypeTitle || entry.zone.name || zoneTypeLabel(entry.zone.zone_type);
      const pos = entry.relativePosition === 'left' ? 'LEFT' :
                  entry.relativePosition === 'right' ? 'RIGHT' : 'CENTER';
      const floors = Number(entry.zone.properties?.floors) || Number(entry.zone.properties?.max_floors) || 0;
      const heightNote = floors > 0 ? ` (${floors} stories tall)` : '';
      return `  ${pos} (frame ${entry.frameLeftPct}%-${entry.frameRightPct}%, ~${Math.round(entry.distance)}m): ` +
             `"${name}"${heightNote} — ${desc}`;
    });
    lines.push(`Content Assignment:\n${fgDescriptions.join('\n')}`);
  } else {
    let fgFallback: string;
    if (pegmanContext === 'park') {
      fgFallback = standingZoneInfo?.landscapeCharacter
        || 'Lush grass lawn with a winding stone pathway, mature trees, and planted garden beds extending into the scene.';
    } else if (pegmanContext === 'water') {
      fgFallback = 'Natural shoreline with reeds, smooth stones, and a wooden boardwalk extending into the scene.';
    } else if (pegmanContext === 'street' && standingZoneInfo?.corridorDescription) {
      fgFallback = `${standingZoneInfo.corridorDescription} extending into the scene.`;
    } else {
      fgFallback = 'Paved sidewalk and street extending into the scene with curbs and street trees.';
    }
    lines.push(`Content Assignment: ${fgFallback}`);
  }
  lines.push(
    `Optical Effect: Sharp, high-contrast resolution. Every material texture (brick joints, glass reflections, ` +
    `leaf veins, stone grain) must be rendered with maximum detail. Close structures cast crisp shadows ` +
    `onto the foreground pavement.`,
  );

  // ─── MIDGROUND PLANE ───
  lines.push(`═══ MIDGROUND PLANE (center 45% of frame, primary focal area) ═══`);
  lines.push(
    `Spatial Position: The primary focal zone, intersecting the center horizontal axis of the frame.`,
  );
  if (midground.length > 0) {
    const mgDescriptions = midground.map(entry => {
      const info = getZoneArchetypeInfo(entry.zone);
      const desc = describeZoneForStreetView(entry.zone, info);
      const name = info.archetypeTitle || entry.zone.name || zoneTypeLabel(entry.zone.zone_type);
      const pos = entry.relativePosition === 'left' ? 'LEFT' :
                  entry.relativePosition === 'right' ? 'RIGHT' : 'CENTER';
      const floors = Number(entry.zone.properties?.floors) || Number(entry.zone.properties?.max_floors) || 0;
      const heightNote = floors > 0 ? ` (${floors} stories tall)` : '';
      return `  ${pos} (frame ${entry.frameLeftPct}%-${entry.frameRightPct}%, ~${Math.round(entry.distance)}m): ` +
             `"${name}"${heightNote} — ${desc}`;
    });
    lines.push(`Content Assignment:\n${mgDescriptions.join('\n')}`);
  } else {
    lines.push(`Content Assignment: Open development ground transitioning to the background.`);
  }
  lines.push(
    `Optical Effect: Render with sharp resolution but slightly softer than the foreground. ` +
    `Structural shadows from buildings must connect with the foreground ground plane.`,
  );

  // ─── BACKGROUND PLANE ───
  lines.push(`═══ BACKGROUND PLANE (top 30% of frame, deep distance) ═══`);
  lines.push(
    `Spatial Position: Deep distance, occupying the top portion of the frame behind the midground structures.`,
  );
  if (background.length > 0) {
    const bgDescriptions = background.map(entry => {
      const info = getZoneArchetypeInfo(entry.zone);
      const desc = describeZoneForStreetView(entry.zone, info);
      const name = info.archetypeTitle || entry.zone.name || zoneTypeLabel(entry.zone.zone_type);
      const pos = entry.relativePosition === 'left' ? 'LEFT' :
                  entry.relativePosition === 'right' ? 'RIGHT' : 'CENTER';
      return `  ${pos} (~${Math.round(entry.distance)}m): "${name}" — ${desc}`;
    });
    lines.push(`Content Assignment:\n${bgDescriptions.join('\n')}`);
  }
  lines.push(
    `Content Assignment (sky): Clear sky fading from warm golden tones at the horizon to ` +
    `deeper blue overhead.`,
  );
  lines.push(
    `Optical Effect: Enforce atmospheric perspective. Background structures must appear ` +
    `desaturated, hazy, and blue-tinted compared to the crisp foreground and midground. ` +
    `Distant buildings are visibly smaller due to perspective foreshortening.`,
  );

  // ─── GROUND PLANE (archetype-enriched) ───
  let groundPlaneDesc: string;
  if (pegmanContext === 'park') {
    groundPlaneDesc = standingZoneInfo?.landscapeCharacter
      || 'Manicured grass lawn and winding gravel or stone pathways in the immediate foreground, with mature trees, flower beds, and park benches.';
  } else if (pegmanContext === 'water') {
    groundPlaneDesc = 'Wooden boardwalk or natural stone shoreline in the immediate foreground, with reeds, smooth rocks, and water lapping at the edges.';
  } else if (pegmanContext === 'street' && standingZoneInfo?.corridorDescription) {
    groundPlaneDesc = `${standingZoneInfo.corridorDescription} extending into the scene in the immediate foreground.`;
  } else {
    groundPlaneDesc = 'Paved sidewalk and street in the immediate foreground with realistic curbs, utility poles, and street trees.';
  }
  lines.push(
    `═══ GROUND PLANE ═══\n` +
    `${groundPlaneDesc} ` +
    `The ground plane recedes naturally toward the horizon using one-point ` +
    `perspective, visually connecting all depth planes.`,
  );

  // ─── WATER/PARK SPECIFIC INSTRUCTIONS ───
  const hasWater = visibleZones.some(z => z.zone.zone_type === 'water');
  const hasParks = visibleZones.some(z => z.zone.zone_type === 'green_space');

  if (hasWater) {
    lines.push(
      `═══ WATER RENDERING (MANDATORY) ═══\n` +
      `Any blue surface in the clay model MUST be rendered as a body of water. ` +
      `Show realistic water with: mirror-like reflections of adjacent buildings and sky, ` +
      `subtle ripples on the surface, natural shoreline with reeds/rocks/vegetation at edges, ` +
      `color gradient from deep blue in the center to lighter blue-green at shallow edges. ` +
      `Water must NOT be rendered as a blue floor, pavement, or solid surface.`,
    );
  }

  if (hasParks) {
    lines.push(
      `═══ PARK/GREEN SPACE RENDERING (MANDATORY) ═══\n` +
      `Green volumes in the clay model represent parks and green spaces. These MUST be rendered as ` +
      `lush, detailed landscape with: mature trees with visible trunks and leafy canopies, ` +
      `manicured lawns, walking paths (gravel or stone), park benches, planted beds, ` +
      `and natural ground cover. Parks should feel alive and inviting — NOT empty grass fields. ` +
      `Tree canopies should break the skyline, creating organic silhouettes against the sky.`,
    );
  }

  // ─── MANDATORY CHECKLIST ───
  const zoneNames = visibleZones.map(z => {
    const info = getZoneArchetypeInfo(z.zone);
    return info.archetypeTitle || z.zone.name || zoneTypeLabel(z.zone.zone_type);
  });
  if (zoneNames.length > 0) {
    lines.push(
      `MANDATORY ELEMENTS (all ${zoneNames.length} must be visible):\n` +
      zoneNames.map((n, i) => `  ${i + 1}. ${n}`).join('\n'),
    );
  }

  // Closing style + prohibitions
  if (styleModifier && styleModifier.startsWith('PHOTO STYLE:')) {
    // Photorealistic variants — keep photographic language
    lines.push(
      `FINAL REMINDER: Maintain the specific photographic style, camera parameters, and atmospheric conditions ` +
      `specified at the top of this prompt. This must look like a real photograph, not a CG render.`,
    );
    lines.push(
      `SCENE CONDITIONS: The fictional human figures described in ENTOURAGE must be present. ` +
      `The scene feels lived-in and welcoming — a real place with real activity. ${
        pegmanContext === 'park' ? 'Pathways wind naturally through lush green landscape with people enjoying the space.'
        : pegmanContext === 'water' ? 'The waterfront is active with people strolling and enjoying views.'
        : 'Streets and sidewalks have natural pedestrian activity with people going about their day.'
      }`,
    );
  } else if (styleModifier) {
    lines.push(
      `FINAL REMINDER: The entire image MUST be in the artistic style specified at the top of this prompt. ` +
      `Apply the artistic medium consistently to every element including buildings, landscape, sky, AND human figures.`,
    );
    lines.push(
      `SCENE CONDITIONS: Include the fictional human figures described in ENTOURAGE, rendered in the same ` +
      `artistic style as the architecture. ${
        pegmanContext === 'park' ? 'Pathways wind naturally through lush green landscape with figures enjoying the space.'
        : pegmanContext === 'water' ? 'The waterfront has figures strolling along the boardwalk.'
        : 'Streets have figures walking and sitting at cafes, all in the specified artistic style.'
      }`,
    );
  } else {
    lines.push(
      `STYLE: Photorealistic architectural visualization photograph. Sunny day, warm golden hour lighting. ` +
      `Sharp material detail on close elements, atmospheric haze on distant ones. 50mm lens, f/8 aperture, ` +
      `deep focus. 8K resolution.`,
    );
    lines.push(
      `SCENE CONDITIONS: Include the fictional human figures described in ENTOURAGE. ` +
      `The scene feels alive and inhabited. ${
        pegmanContext === 'park' ? 'People enjoy the green space on paths and benches.'
        : pegmanContext === 'water' ? 'People stroll along the waterfront promenade.'
        : 'Pedestrians walk the sidewalks and sit at outdoor cafes.'
      }`,
    );
  }

  // ─── ENTOURAGE — Style 6 photorealistic fictional people ───
  let entourageDesc: string;
  if (pegmanContext === 'park') {
    entourageDesc = (
      'Include 5-8 diverse human figures naturally enjoying the park — ' +
      'on pathways, sitting on benches, a parent with a child, someone walking a dog. '
    );
  } else if (pegmanContext === 'water') {
    entourageDesc = (
      'Include 4-6 diverse human figures along the waterfront — ' +
      'on the boardwalk, sitting on rocks, a couple looking at the water. '
    );
  } else {
    entourageDesc = (
      'Include 6-10 diverse human figures naturally inhabiting the street — ' +
      'walking on sidewalks, sitting at outdoor cafe tables, a cyclist, someone walking a dog. '
    );
  }
  lines.push(
    `═══ ENTOURAGE ═══\n` +
    entourageDesc +
    `The ARCHITECTURE AND SPACE are the primary subject — people are secondary, providing ` +
    `scale and life. Place most figures in the mid-ground and background (15-40m from camera). ` +
    `Each figure must have anatomically correct proportions, natural posture, realistic clothing ` +
    `appropriate for the setting, and visible hair and skin textures with natural subsurface scattering. ` +
    `Diverse ages, ethnicities, and body types reflecting a contemporary urban community. ` +
    `NO figures blocking the central architectural view. NO wall of people across the frame. ` +
    `These are fictional characters — not real individuals. ` +
    `Shot on 35mm SLR, Kodak Portra 400 film stock color science.`,
  );

  return lines.join('\n\n');
}

// ---------------------------------------------------------------------------
// Perspective depth map — color-coded guide image for spatial accuracy
// ---------------------------------------------------------------------------

const DEPTH_MAP_WIDTH = 1024;
const DEPTH_MAP_HEIGHT = 576; // 16:9
const EYE_HEIGHT_M = 1.7;
const FALLBACK_FLOOR_HEIGHT_M = 3.2; // used only when a zone has no floor_height property
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
    const floorH = Number(zone.properties?.floor_height) || FALLBACK_FLOOR_HEIGHT_M;
    const heightM = floors * floorH;

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

      // Draw a tall green block above ground to represent park's vertical presence
      // (trees, vegetation) — simpler than individual circles to avoid literal interpretation
      const vegHeight = Math.min(horizonY * 0.5, 40 * perspScale);
      ctx.fillStyle = color;
      ctx.globalAlpha = 0.5;
      ctx.fillRect(leftX + 4, groundTop - vegHeight, width - 8, vegHeight);
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
// Three.js Clay Render — solid gray 3D massing model from street level
// ---------------------------------------------------------------------------

const CLAY_WIDTH = 1024;
const CLAY_HEIGHT = 576;

/**
 * Generate a "clay render" — a gray-shaded 3D massing model from street level.
 * Uses Three.js offscreen renderer to produce solid gray volumes with proper
 * perspective, occlusion, and lighting. This gives Gemini unambiguous spatial
 * data about building heights, positions, and depth ordering.
 *
 * Buildings → extruded gray boxes
 * Parks → flat green-tinted ground planes with low hedge volumes
 * Water → flat blue-tinted ground planes
 * Roads → flat gray ground strips
 */
export function generateClayRender(
  pegmanPos: [number, number],
  angleDeg: number,
  visibleZones: ZoneWithDistance[],
): string {
  // --- Set up offscreen Three.js scene ---
  const renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: false,
    preserveDrawingBuffer: true,
  });
  renderer.setSize(CLAY_WIDTH, CLAY_HEIGHT);
  renderer.setClearColor(0xd4e6f1, 1); // light sky blue background
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  const scene = new THREE.Scene();
  // Sky-like fog for atmospheric perspective (distant objects fade)
  scene.fog = new THREE.Fog(0xc8dce8, 80, 350);

  // --- Camera at eye level, facing the heading direction ---
  const camera = new THREE.PerspectiveCamera(60, CLAY_WIDTH / CLAY_HEIGHT, 0.5, 500);
  camera.position.set(0, EYE_HEIGHT_M, 0);

  // Convert compass heading to Three.js look direction
  // Compass: 0=North(+Y), 90=East(+X). Three.js: -Z is forward by default.
  const headingRad = angleDeg * DEG_TO_RAD;
  const lookX = Math.sin(headingRad) * 100;
  const lookZ = -Math.cos(headingRad) * 100;
  camera.lookAt(new THREE.Vector3(lookX, EYE_HEIGHT_M * 0.8, lookZ));

  // --- Lighting ---
  // Ambient for base illumination
  const ambient = new THREE.AmbientLight(0xffffff, 0.5);
  scene.add(ambient);

  // Directional sun light (slightly from front-left for shading definition)
  const sunLight = new THREE.DirectionalLight(0xfff4e0, 1.2);
  sunLight.position.set(-30, 60, -20);
  sunLight.castShadow = true;
  sunLight.shadow.mapSize.width = 1024;
  sunLight.shadow.mapSize.height = 1024;
  sunLight.shadow.camera.near = 0.5;
  sunLight.shadow.camera.far = 300;
  sunLight.shadow.camera.left = -150;
  sunLight.shadow.camera.right = 150;
  sunLight.shadow.camera.top = 150;
  sunLight.shadow.camera.bottom = -150;
  scene.add(sunLight);

  // Hemisphere light for natural sky/ground color variation
  const hemiLight = new THREE.HemisphereLight(0x87ceeb, 0x8b7355, 0.3);
  scene.add(hemiLight);

  // --- Ground plane ---
  const groundGeo = new THREE.PlaneGeometry(600, 600);
  const groundMat = new THREE.MeshStandardMaterial({
    color: 0x9e9e9e,
    roughness: 0.9,
    metalness: 0,
  });
  const ground = new THREE.Mesh(groundGeo, groundMat);
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = 0;
  ground.receiveShadow = true;
  scene.add(ground);

  // --- Helper: convert zone's lat/lng polygon centroid to local meters ---
  const [pegLng, pegLat] = pegmanPos;
  const metersPerDegLng = METERS_PER_DEG_LAT * Math.cos(pegLat * DEG_TO_RAD);

  function toLocal(lng: number, lat: number): [number, number] {
    const x = (lng - pegLng) * metersPerDegLng;
    const z = -(lat - pegLat) * METERS_PER_DEG_LAT; // negative because Three.js -Z is north
    return [x, z];
  }

  function getPolygonCentroid(coords: number[][]): [number, number] {
    let sumX = 0, sumY = 0;
    for (const c of coords) {
      sumX += c[0];
      sumY += c[1];
    }
    return [sumX / coords.length, sumY / coords.length];
  }

  function getPolygonExtent(coords: number[][]): { minX: number; maxX: number; minY: number; maxY: number } {
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    for (const c of coords) {
      if (c[0] < minX) minX = c[0];
      if (c[0] > maxX) maxX = c[0];
      if (c[1] < minY) minY = c[1];
      if (c[1] > maxY) maxY = c[1];
    }
    return { minX, maxX, minY, maxY };
  }

  // --- Ground plane grid for perspective anchoring ---
  // Research shows a visible grid prevents tilt-shift and locks vanishing points
  const gridHelper = new THREE.GridHelper(600, 60, 0x666666, 0x888888);
  gridHelper.position.y = 0.02;
  (gridHelper.material as THREE.Material).opacity = 0.25;
  (gridHelper.material as THREE.Material).transparent = true;
  scene.add(gridHelper);

  // --- Helper: parse hex color to Three.js color number ---
  function hexToThreeColor(hex: string): number {
    const clean = hex.replace('#', '');
    return parseInt(clean, 16);
  }

  // --- Zone-specific color materials (full opacity, unique per zone) ---
  // Each zone gets its own material based on its actual map color
  const zoneMaterials = new Map<string, THREE.MeshStandardMaterial>();
  function getZoneMaterial(zone: SiteZone, fallbackColor: number, roughness = 0.7, metalness = 0.1): THREE.MeshStandardMaterial {
    const zoneColor = zone.color;
    const key = zone.id || `${zoneColor}_${fallbackColor}`;
    if (zoneMaterials.has(key)) return zoneMaterials.get(key)!;
    const color = zoneColor ? hexToThreeColor(zoneColor) : fallbackColor;
    const mat = new THREE.MeshStandardMaterial({ color, roughness, metalness });
    zoneMaterials.set(key, mat);
    return mat;
  }

  // Fallback materials for roads (keep neutral)
  const roadMat = new THREE.MeshStandardMaterial({
    color: 0x757575,
    roughness: 0.95,
    metalness: 0,
  });

  // --- Build 3D volumes for each zone ---
  for (const entry of visibleZones) {
    const zone = entry.zone;
    const coords = zone.coordinates;
    if (!coords || coords.length < 3) continue;

    const centroid = getPolygonCentroid(coords);
    const [cx, cz] = toLocal(centroid[0], centroid[1]);
    const extent = getPolygonExtent(coords);

    // Convert extent to local meters for sizing
    const [minLocalX, minLocalZ] = toLocal(extent.minX, extent.maxY);
    const [maxLocalX, maxLocalZ] = toLocal(extent.maxX, extent.minY);
    const widthM = Math.abs(maxLocalX - minLocalX);
    const depthM = Math.abs(maxLocalZ - minLocalZ);

    // Skip extremely small or distant zones
    if (widthM < 1 && depthM < 1) continue;
    if (entry.distance > 300) continue;

    const isBuilding = zone.zone_type === 'building' || zone.zone_type === 'residential' || zone.zone_type === 'development_area';

    if (isBuilding) {
      // Extruded box for buildings
      const floors = Number(zone.properties?.floors) || Number(zone.properties?.max_floors) || 4;
      const floorH = Number(zone.properties?.floor_height) || FALLBACK_FLOOR_HEIGHT_M;
      const heightM = floors * floorH;

      const geo = new THREE.BoxGeometry(
        Math.max(widthM, 5),
        heightM,
        Math.max(depthM, 5),
      );
      // Use each zone's unique color at full opacity for color-coded semantic mapping
      const mat = getZoneMaterial(zone, 0xb0b0b0);
      const mesh = new THREE.Mesh(geo, mat);
      mesh.position.set(cx, heightM / 2, cz);
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      scene.add(mesh);

      // Add subtle edge lines for definition
      const edges = new THREE.EdgesGeometry(geo);
      const lineMat = new THREE.LineBasicMaterial({ color: 0x666666, opacity: 0.4, transparent: true });
      const lineSegments = new THREE.LineSegments(edges, lineMat);
      lineSegments.position.copy(mesh.position);
      scene.add(lineSegments);

    } else if (zone.zone_type === 'green_space') {
      // Parks: organic green ground with scattered tree canopy spheres
      const pw = Math.max(widthM, 5);
      const pd = Math.max(depthM, 5);

      // Grass ground plane — use zone's actual color at full opacity
      const planeGeo = new THREE.PlaneGeometry(pw, pd);
      const parkMat = getZoneMaterial(zone, 0x7cb342, 0.9, 0);
      const plane = new THREE.Mesh(planeGeo, parkMat);
      plane.rotation.x = -Math.PI / 2;
      plane.position.set(cx, 0.08, cz);
      plane.receiveShadow = true;
      scene.add(plane);

      // Scatter tree canopy spheres (organic shapes, not boxes)
      const treeCount = Math.max(3, Math.floor((pw * pd) / 80));
      const canopyMat = new THREE.MeshStandardMaterial({
        color: 0x4a7c2a,
        roughness: 0.85,
        metalness: 0,
      });
      const darkCanopyMat = new THREE.MeshStandardMaterial({
        color: 0x2e5a1a,
        roughness: 0.85,
        metalness: 0,
      });
      // Use a seeded random based on zone position for consistency
      let seed = Math.abs(cx * 17 + cz * 31) % 1000;
      const seededRandom = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };

      for (let t = 0; t < treeCount; t++) {
        const tx = cx + (seededRandom() - 0.5) * pw * 0.85;
        const tz = cz + (seededRandom() - 0.5) * pd * 0.85;

        // Tree trunk (thin cylinder)
        const trunkH = 2 + seededRandom() * 2;
        const trunkGeo = new THREE.CylinderGeometry(0.15, 0.2, trunkH, 6);
        const trunkMat = new THREE.MeshStandardMaterial({ color: 0x5d4037, roughness: 0.9 });
        const trunk = new THREE.Mesh(trunkGeo, trunkMat);
        trunk.position.set(tx, trunkH / 2, tz);
        trunk.castShadow = true;
        scene.add(trunk);

        // Tree canopy (sphere or icosahedron for organic look)
        const canopyR = 2 + seededRandom() * 3;
        const canopyGeo = new THREE.IcosahedronGeometry(canopyR, 1);
        const canopy = new THREE.Mesh(canopyGeo, t % 2 === 0 ? canopyMat : darkCanopyMat);
        canopy.position.set(tx, trunkH + canopyR * 0.6, tz);
        // Slightly squash vertically for realistic canopy shape
        canopy.scale.set(1, 0.7, 1);
        canopy.castShadow = true;
        scene.add(canopy);
      }

      // Add a path/walkway through the park (thin light strip)
      const pathGeo = new THREE.PlaneGeometry(pw * 0.15, pd * 0.8);
      const pathMat = new THREE.MeshStandardMaterial({ color: 0xbcaaa4, roughness: 0.95 });
      const path = new THREE.Mesh(pathGeo, pathMat);
      path.rotation.x = -Math.PI / 2;
      path.position.set(cx, 0.1, cz);
      scene.add(path);

    } else if (zone.zone_type === 'water') {
      // Water: reflective blue plane with darker shoreline border
      const ww = Math.max(widthM, 5);
      const wd = Math.max(depthM, 5);

      // Shoreline border (darker ground ring around water)
      const shoreGeo = new THREE.PlaneGeometry(ww + 3, wd + 3);
      const shoreMat = new THREE.MeshStandardMaterial({
        color: 0x6d4c41,
        roughness: 0.9,
        metalness: 0,
      });
      const shore = new THREE.Mesh(shoreGeo, shoreMat);
      shore.rotation.x = -Math.PI / 2;
      shore.position.set(cx, 0.01, cz);
      scene.add(shore);

      // Vegetation around shoreline (small green spheres at edges)
      const vegMat = new THREE.MeshStandardMaterial({ color: 0x558b2f, roughness: 0.9 });
      const vegCount = Math.floor((ww + wd) / 4);
      for (let v = 0; v < vegCount; v++) {
        const angle = (v / vegCount) * Math.PI * 2;
        const rx = cx + Math.cos(angle) * (ww / 2 + 0.5);
        const rz = cz + Math.sin(angle) * (wd / 2 + 0.5);
        const vegGeo = new THREE.SphereGeometry(0.6 + Math.random() * 0.5, 6, 4);
        const veg = new THREE.Mesh(vegGeo, vegMat);
        veg.position.set(rx, 0.5, rz);
        scene.add(veg);
      }

      // Water surface — use zone's actual color at full opacity, with reflective properties
      const waterGeo = new THREE.PlaneGeometry(ww, wd);
      const waterColor = zone.color ? hexToThreeColor(zone.color) : 0x1976d2;
      const waterSurfaceMat = new THREE.MeshStandardMaterial({
        color: waterColor,
        roughness: 0.1,
        metalness: 0.6,
      });
      const water = new THREE.Mesh(waterGeo, waterSurfaceMat);
      water.rotation.x = -Math.PI / 2;
      water.position.set(cx, -0.1, cz); // slightly below ground for "recessed" look
      water.receiveShadow = true;
      scene.add(water);

    } else {
      // Roads, streets, paths, and other ground zones
      const zt2 = zone.zone_type as string;
      const isStreet = zt2 === 'road' || zt2 === 'street' || zt2 === 'path' || zt2 === 'pedestrian';

      if (isStreet && zone.properties?._original_line_coords) {
        // Buffered street — draw as a raised dark strip following the original line
        const lineCoords = zone.properties._original_line_coords as number[][];
        const streetWidth = Number(zone.properties?.width) || 10;

        // Draw street segments as elongated boxes
        for (let seg = 0; seg < lineCoords.length - 1; seg++) {
          const [lng1, lat1] = lineCoords[seg];
          const [lng2, lat2] = lineCoords[seg + 1];
          const [lx1, lz1] = toLocal(lng1, lat1);
          const [lx2, lz2] = toLocal(lng2, lat2);

          const segLength = Math.sqrt((lx2 - lx1) ** 2 + (lz2 - lz1) ** 2);
          if (segLength < 0.5) continue;

          const midX = (lx1 + lx2) / 2;
          const midZ = (lz1 + lz2) / 2;
          const angle = Math.atan2(lx2 - lx1, lz2 - lz1);

          // Street surface as a flat dark box
          const streetGeo = new THREE.BoxGeometry(streetWidth, 0.15, segLength);
          const streetMesh = new THREE.Mesh(streetGeo, roadMat);
          streetMesh.position.set(midX, 0.08, midZ);
          streetMesh.rotation.y = angle;
          streetMesh.receiveShadow = true;
          scene.add(streetMesh);

          // Sidewalk curbs (slightly raised edges)
          const curbMat = new THREE.MeshStandardMaterial({ color: 0xa0a0a0, roughness: 0.85 });
          const curbWidth = 1.5;
          for (const side of [-1, 1]) {
            const curbGeo = new THREE.BoxGeometry(curbWidth, 0.25, segLength);
            const curb = new THREE.Mesh(curbGeo, curbMat);
            const offset = (streetWidth / 2 + curbWidth / 2);
            curb.position.set(
              midX + Math.cos(angle) * offset * side,
              0.12,
              midZ - Math.sin(angle) * offset * side,
            );
            curb.rotation.y = angle;
            scene.add(curb);
          }
        }
      } else {
        // Generic ground zone — flat gray strip
        const planeGeo = new THREE.PlaneGeometry(
          Math.max(widthM, 3),
          Math.max(depthM, 3),
        );
        const plane = new THREE.Mesh(planeGeo, roadMat);
        plane.rotation.x = -Math.PI / 2;
        plane.position.set(cx, 0.03, cz);
        plane.receiveShadow = true;
        scene.add(plane);
      }
    }
  }

  // --- Render the 3D scene (no text labels — user can add those after) ---
  renderer.render(scene, camera);
  const dataUrl = renderer.domElement.toDataURL('image/png');

  // Clean up Three.js resources
  renderer.dispose();
  scene.traverse((obj) => {
    if (obj instanceof THREE.Mesh) {
      obj.geometry.dispose();
      if (Array.isArray(obj.material)) {
        obj.material.forEach((m) => m.dispose());
      } else {
        obj.material.dispose();
      }
    }
  });

  return dataUrl.split(',')[1];
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
/**
 * Fetch an image from a URL and return its base64 data (without prefix).
 * Used to collect archetype card images for multi-image routing.
 */
async function fetchImageAsBase64(url: string): Promise<string | null> {
  try {
    // For relative URLs (archetype cards served from public/)
    const fullUrl = url.startsWith('http') ? url : window.location.origin + url;
    const resp = await fetch(fullUrl);
    if (!resp.ok) return null;
    const blob = await resp.blob();
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const dataUrl = reader.result as string;
        resolve(dataUrl.split(',')[1] || null);
      };
      reader.readAsDataURL(blob);
    });
  } catch {
    return null;
  }
}

/**
 * Collect archetype card images for all visible zones (up to 6).
 * Returns array of { image_base64, label, zone_color } for multi-image routing.
 */
async function collectArchetypeImages(
  visibleZones: ZoneWithDistance[],
): Promise<Array<{ image_base64: string; label: string; zone_color: string }>> {
  const results: Array<{ image_base64: string; label: string; zone_color: string }> = [];

  // Take up to 6 closest/most important zones
  const candidates = visibleZones.slice(0, 6);

  const promises = candidates.map(async (entry) => {
    const info = getZoneArchetypeInfo(entry.zone);
    const title = info.archetypeTitle || entry.zone.name || zoneTypeLabel(entry.zone.zone_type);

    // Try to find the archetype's thumbnail image
    let thumbnailUrl: string | null = null;

    const archetypeId = entry.zone.properties?.development_archetype_id
      || entry.zone.properties?.road_archetype_id
      || entry.zone.properties?.green_space_archetype_id
      || entry.zone.properties?.plaza_archetype_id
      || entry.zone.properties?.archetype_id
      || entry.zone.properties?.subcategory;
    if (archetypeId) {
      // Look up the catalog entry for its thumbnail
      const catalogEntry = catalog.find(
        (c: any) => c.id === archetypeId,
      );
      if (catalogEntry?.variants) {
        // Use the SELECTED variant if available, otherwise variant 0
        const selectedVariantIdx = Number(entry.zone.properties?.selected_variant) || 0;
        const variant = catalogEntry.variants[selectedVariantIdx] || catalogEntry.variants[0];
        if (variant?.thumbnailUrl) {
          thumbnailUrl = variant.thumbnailUrl;
        }
      } else if (catalogEntry?.thumbnailUrl) {
        thumbnailUrl = catalogEntry.thumbnailUrl;
      }
    }

    if (!thumbnailUrl) return null;

    const b64 = await fetchImageAsBase64(thumbnailUrl);
    if (!b64) return null;

    // Use relative position as zone identifier for routing
    const positionLabel = entry.relativePosition; // left/center/right

    return { image_base64: b64, label: title, zone_color: positionLabel };
  });

  const settled = await Promise.all(promises);
  for (const item of settled) {
    if (item) results.push(item);
  }

  console.log(`[StreetView] Collected ${results.length} archetype card images for multi-image routing`);
  return results;
}

export async function generateStreetView(
  pegmanPos: [number, number],
  angleDeg: number,
  siteZones: SiteZone[],
  options?: {
    fovDeg?: number;
    distanceMeters?: number;
    styleModifier?: string;
    model?: string;
    projectId?: string;
    previousRenderBase64?: string; // For dual anchoring on re-render
    overrideGuideImage?: string; // Base64 image to use instead of clay render (e.g. 3D tiles capture)
  },
): Promise<StreetViewResult | null> {
  const fov = options?.fovDeg ?? 70;
  const distance = options?.distanceMeters ?? 200;

  // 0. Pre-process: buffer street/path polylines into polygons
  const processedZones = preprocessZonesForStreetView(siteZones);

  // 1. View cone
  const cone = getViewConePolygon(pegmanPos, angleDeg, fov, distance);

  // 2. Zone intersection
  const intersecting = getZonesInViewCone(processedZones, cone);

  // 3. Sort by distance with angular analysis
  const sorted = sortZonesByDistance(intersecting, pegmanPos, angleDeg, fov);

  // 3b. Occlusion culling — remove zones hidden behind closer buildings
  const visible = cullOccludedZones(pegmanPos, sorted);

  // Debug: log what was found
  console.log('[StreetView] Pegman at', pegmanPos, 'facing', angleDeg, '°');
  console.log('[StreetView] FOV:', fov, '° Distance:', distance, 'm');
  console.log('[StreetView] Total site zones:', siteZones.length, '| In view cone:', intersecting.length, '| After occlusion:', visible.length);
  for (const z of visible) {
    const info = getZoneArchetypeInfo(z.zone);
    console.log(
      `  [${z.relativePosition.toUpperCase()}] ${info.archetypeTitle || z.zone.name || z.zone.zone_type}` +
      ` — ${Math.round(z.distance)}m — frame ${z.frameLeftPct}%-${z.frameRightPct}% (${z.framePercent}% wide)` +
      ` — has metadata: ${!!info.archetypeTitle}`,
    );
  }

  // 4. Build SCHEMA-style prompt (context-aware: park/water/street)
  // Pass processedZones as fallback so we find the standing zone even if behind camera
  const { context: pegmanCtx, zone: standingZone } = detectPegmanContext(pegmanPos, visible, processedZones);
  const standingZoneInfo = standingZone ? getZoneArchetypeInfo(standingZone) : undefined;
  console.log(`[StreetView] Pegman context: ${pegmanCtx} — standing on: ${standingZoneInfo?.archetypeTitle || standingZone?.name || 'unknown'}`);
  const prompt = buildStreetViewPrompt(pegmanPos, angleDeg, visible, options?.styleModifier, standingZoneInfo);
  console.log('[StreetView] Prompt length:', prompt.length, 'chars');

  // 5. Generate guide image — use override (e.g. 3D tiles capture) or clay render
  let guideImageBase64: string;
  if (options?.overrideGuideImage) {
    guideImageBase64 = options.overrideGuideImage;
    console.log('[StreetView] Using override guide image (3D tiles capture)');
  } else {
    try {
      guideImageBase64 = generateClayRender(pegmanPos, angleDeg, visible);
      console.log('[StreetView] Clay render generated successfully');
    } catch (clayErr) {
      console.warn('[StreetView] Clay render failed, falling back to flat depth map:', clayErr);
      guideImageBase64 = generateDepthMap(pegmanPos, angleDeg, visible);
    }
  }

  // 6. Collect archetype card images for multi-image routing (up to 6)
  let archetypeImages: Array<{ image_base64: string; label: string; zone_color: string }> = [];
  try {
    archetypeImages = await collectArchetypeImages(sorted);
  } catch (archErr) {
    console.warn('[StreetView] Failed to collect archetype images:', archErr);
  }

  // 7. Call render API with guide image + archetype images + optional dual anchor
  const isRealContext = !!options?.overrideGuideImage;
  try {
    const spatialRef = isRealContext
      ? '\n\nSPATIAL REFERENCE (Image 1): This is a real 3D photorealistic capture of the existing site from street level. ' +
        'You can see the actual existing buildings, trees, roads, and terrain of this real-world location. ' +
        'The colored semi-transparent polygon overlays visible in the image mark where NEW architectural interventions should be placed. ' +
        'CRITICAL INSTRUCTIONS: ' +
        '1. The existing real buildings, streets, trees, and terrain visible in the photograph are GROUND TRUTH — preserve them EXACTLY. Do NOT alter, remove, or reimagine any existing structures. ' +
        '2. The colored overlay areas indicate where NEW architecture should be rendered, as described in the zone descriptions above. ' +
        '3. Render the new architecture so it seamlessly integrates with the REAL surrounding buildings — match the exact lighting direction, shadow angles, atmospheric haze, and color temperature visible in the photograph. ' +
        '4. The result must be indistinguishable from a real photograph — a photomontage where new buildings appear to genuinely exist alongside the real ones. ' +
        '5. Camera is at human eye level (1.7m), maintain exact perspective and focal length. ' +
        '6. Add realistic street-level details: people walking, parked cars, street furniture, trees with accurate shadow casting.'
      : '\n\nSPATIAL REFERENCE (Image 1): The attached color-coded 3D massing model is the STRUCTURAL ANCHOR. ' +
        'Each colored volume maps to a specific architectural zone described in the COLOR-TO-ZONE MAPPING above. ' +
        'The ground plane grid provides perspective and scale calibration. ' +
        'STRICT RULES: ' +
        '1. Preserve the EXACT spatial layout, proportions, and occlusion shown in the massing model. ' +
        '2. Replace each colored volume with photorealistic materials matching its zone description. ' +
        '3. Render ONLY the structures shown in the massing model as listed in the NUMERICAL INVENTORY. ' +
        '4. Apply atmospheric perspective: distant objects appear hazier and more desaturated. ' +
        '5. Maintain camera height (1.7m) and viewing angle exactly.';
    const enhancedPrompt =
      prompt + spatialRef +
      (archetypeImages.length > 0
        ? '\n\nARCHETYPE STYLE REFERENCES (Images 2+): Additional images show the exact architectural ' +
          'style and materials for specific zones. Use Image 1 strictly as the structural foundation. ' +
          'Extract material textures and architectural aesthetic from the style reference images. ' +
          'Apply each reference image\'s style to the corresponding colored volume in Image 1.'
        : '');

    const body: Record<string, unknown> = {
      prompt: enhancedPrompt,
      image_base64: guideImageBase64,
      aspect_ratio: '16:9',
      // Optimal API config from research: temp=0.35 prevents hallucinations while
      // preserving photorealistic material variance; topP=0.85 trims long-tail
      // improbable elements; topK=32 restricts to probable geometric interpretations
      temperature: 0.35,
      top_p: 0.85,
      top_k: 32,
    };

    if (options?.model) {
      body.model = options.model;
    }
    if (options?.projectId) {
      body.project_id = options.projectId;
    }

    // Multi-image archetype routing
    if (archetypeImages.length > 0) {
      body.archetype_images = archetypeImages;
    }

    // Dual anchoring: feed previous render back for iterative refinement
    if (options?.previousRenderBase64) {
      body.previous_render_base64 = options.previousRenderBase64;
      console.log('[StreetView] Dual anchoring: including previous render as structural anchor');
    }

    const svToken = localStorage.getItem('access_token');
    const response = await axios.post(RENDER_API_URL, body, {
      timeout: 300_000,
      headers: svToken ? { Authorization: `Bearer ${svToken}` } : {},
    });

    let resultBase64: string | undefined = response.data?.image_base64;

    if (!resultBase64) {
      console.error('[useStreetViewRender] No image data in API response', response.data);
      return null;
    }

    // --- TWO-PASS GENERATION ---
    // When using Pro model, do a refinement pass for better spatial accuracy.
    // Pass 1 establishes the spatial layout, Pass 2 refines materials and details.
    const isProModel = options?.model === 'gemini-3-pro-image-preview';
    if (isProModel && !options?.previousRenderBase64) {
      console.log('[StreetView] Pass 2: Refining spatial layout with dual anchoring...');
      try {
        const refinementPrompt =
          'REFINEMENT PASS: Use Image 1 (the previous render) as the absolute structural anchor. ' +
          'Preserve the EXACT spatial layout, building positions, heights, camera angle, and proportions. ' +
          'Improve ONLY: material detail and realism, lighting quality, atmospheric effects, ' +
          'texture sharpness on close elements, and natural landscape detail. ' +
          'Do NOT move, resize, add, or remove any structures. ' +
          'The clay model (Image 2) confirms the correct spatial arrangement.\n\n' +
          prompt;

        const pass2Body: Record<string, unknown> = {
          prompt: refinementPrompt,
          image_base64: guideImageBase64,
          previous_render_base64: resultBase64,
          aspect_ratio: '16:9',
          model: options?.model,
          project_id: options?.projectId,
        };

        if (archetypeImages.length > 0) {
          pass2Body.archetype_images = archetypeImages;
        }

        const pass2Response = await axios.post(RENDER_API_URL, pass2Body, {
          timeout: 300_000,
          headers: svToken ? { Authorization: `Bearer ${svToken}` } : {},
        });
        const pass2Base64: string | undefined = pass2Response.data?.image_base64;

        if (pass2Base64) {
          console.log('[StreetView] Pass 2 refinement successful');
          resultBase64 = pass2Base64;
        } else {
          console.warn('[StreetView] Pass 2 returned no image, using Pass 1 result');
        }
      } catch (pass2Err) {
        console.warn('[StreetView] Pass 2 refinement failed, using Pass 1 result:', pass2Err);
      }
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
        model?: string;
        projectId?: string;
        previousRenderBase64?: string;
        overrideGuideImage?: string;
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
