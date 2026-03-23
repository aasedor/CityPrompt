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
import archetypeCatalog from '@/data/buildingArchetypes.json';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const RENDER_API_URL = '/api/v1/render/generate';
const DEG_TO_RAD = Math.PI / 180;
const EARTH_RADIUS_M = 6_371_000;

/** Meters per degree of latitude (roughly constant). */
const METERS_PER_DEG_LAT = 110_540;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const catalog = (archetypeCatalog as any)?.archetypes as any[] | undefined;

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
      surfaceType: sp.surfaceType || undefined,
      plantingCharacter: sp.plantingCharacter || undefined,
      edgeConditions: sp.edgeConditions || undefined,
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
  fovDeg: number = 60,
  distanceMeters: number = 150,
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

    // Need at least 3 coords to form a polygon
    if (!zone.coordinates || zone.coordinates.length < 3) continue;

    const zoneCoords = zone.coordinates as [number, number][];

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
}

/**
 * Sort zones by distance from the pegman position (nearest first) and
 * annotate each with distance and relative bearing.
 */
export function sortZonesByDistance(
  zones: SiteZone[],
  pegmanPos: [number, number],
  pegmanAngle: number,
): ZoneWithDistance[] {
  const annotated: ZoneWithDistance[] = zones.map((zone) => {
    const centroid = polygonCentroid(zone.coordinates) as [number, number];
    const dist = haversineDistance(pegmanPos, centroid);
    const brng = bearing(pegmanPos, centroid);

    // Relative angle: positive = right of center, negative = left
    let relAngle = brng - pegmanAngle;
    if (relAngle > 180) relAngle -= 360;
    if (relAngle < -180) relAngle += 360;

    let relativePosition: 'left' | 'center' | 'right';
    if (relAngle < -15) {
      relativePosition = 'left';
    } else if (relAngle > 15) {
      relativePosition = 'right';
    } else {
      relativePosition = 'center';
    }

    return { zone, distance: dist, relativePosition };
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

/** Classify distance into foreground / midground / background. */
function depthBand(distanceM: number): 'FOREGROUND' | 'MIDGROUND' | 'BACKGROUND' {
  if (distanceM < 30) return 'FOREGROUND';
  if (distanceM < 80) return 'MIDGROUND';
  return 'BACKGROUND';
}

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
    // Parks, plazas, green spaces
    if (info.mapOverlayPrompt) {
      parts.push(info.mapOverlayPrompt);
    } else {
      if (info.plantingCharacter) parts.push(info.plantingCharacter);
      if (info.surfaceType) parts.push(`Surface: ${info.surfaceType}`);
      if (info.materials) parts.push(`Materials: ${info.materials}`);
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
    `Generate a wide-angle 16:9 street-level photograph of an urban development, ` +
    `as seen from eye level (1.7m height) looking ${direction}. ` +
    `The image MUST show ALL of the following elements composed together in a single coherent scene. ` +
    `This is a wide establishing shot showing multiple buildings, landscape areas, and infrastructure ` +
    `receding into the distance. Do NOT focus on just one element — show the full streetscape panorama.`,
  );

  // Separate zones into left / center / right groups
  const leftZones = visibleZones.filter(z => z.relativePosition === 'left');
  const centerZones = visibleZones.filter(z => z.relativePosition === 'center');
  const rightZones = visibleZones.filter(z => z.relativePosition === 'right');

  // Build spatial composition description
  lines.push('SPATIAL COMPOSITION OF THE SCENE:');

  if (leftZones.length > 0) {
    const descs = leftZones.map(entry => {
      const info = getZoneArchetypeInfo(entry.zone);
      const desc = describeZoneForStreetView(entry.zone, info);
      const dist = depthBand(entry.distance).toLowerCase();
      return `[${dist}, ~${Math.round(entry.distance)}m away] ${desc}`;
    });
    lines.push(`LEFT SIDE OF FRAME: ${descs.join('. ')}.`);
  }

  if (centerZones.length > 0) {
    const descs = centerZones.map(entry => {
      const info = getZoneArchetypeInfo(entry.zone);
      const desc = describeZoneForStreetView(entry.zone, info);
      const dist = depthBand(entry.distance).toLowerCase();
      return `[${dist}, ~${Math.round(entry.distance)}m away] ${desc}`;
    });
    lines.push(`CENTER OF FRAME: ${descs.join('. ')}.`);
  }

  if (rightZones.length > 0) {
    const descs = rightZones.map(entry => {
      const info = getZoneArchetypeInfo(entry.zone);
      const desc = describeZoneForStreetView(entry.zone, info);
      const dist = depthBand(entry.distance).toLowerCase();
      return `[${dist}, ~${Math.round(entry.distance)}m away] ${desc}`;
    });
    lines.push(`RIGHT SIDE OF FRAME: ${descs.join('. ')}.`);
  }

  // If no zones were categorized, describe as empty site
  if (visibleZones.length === 0) {
    lines.push('The view shows an empty development site with cleared ground, construction fencing, and surrounding neighborhood context.');
  }

  // Ground plane and context
  lines.push(
    'GROUND PLANE: The immediate foreground shows a paved sidewalk or street surface. ' +
    'Include realistic urban context: curbs, street trees, lamp posts, crosswalks where appropriate. ' +
    'The scene transitions naturally between the different zones described above.',
  );

  // Style modifier
  if (styleModifier) {
    lines.push(styleModifier);
  }

  // Closing quality directives
  lines.push(
    'STYLE: Photorealistic architectural visualization photograph. Sunny day, warm golden hour lighting ' +
    'from the side casting long soft shadows. Sharp detail on building materials and textures. ' +
    'Wide-angle lens (24mm equivalent). Depth of field with sharp foreground and slightly softer background. ' +
    '8K resolution, no people, no text overlays, no watermarks.',
  );

  return lines.join('\n\n');
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
  const fov = options?.fovDeg ?? 60;
  const distance = options?.distanceMeters ?? 150;

  // 1. View cone
  const cone = getViewConePolygon(pegmanPos, angleDeg, fov, distance);

  // 2. Zone intersection
  const intersecting = getZonesInViewCone(siteZones, cone);

  // 3. Sort by distance
  const sorted = sortZonesByDistance(intersecting, pegmanPos, angleDeg);

  // 4. Build prompt
  const prompt = buildStreetViewPrompt(pegmanPos, angleDeg, sorted, options?.styleModifier);

  // 5. Call render API
  try {
    const response = await axios.post(RENDER_API_URL, {
      prompt,
      aspect_ratio: '16:9',
      // Text-only generation — no image_base64
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
