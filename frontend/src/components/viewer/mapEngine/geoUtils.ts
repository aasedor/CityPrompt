import type { SiteZone, SiteZoneType } from '@/types';
import { ZONE_TYPE_CONFIG } from '@/types';
import { getColourForDevelopmentType } from '@/data/landUseColours';
import { getShadeForArchetype } from '@/data/archetypeShadeMap';
import {
  BUILDING_AESTHETIC_OPTIONS_V2,
  ROADWAY_AESTHETIC_OPTIONS_V2,
  GREEN_SPACE_AESTHETIC_OPTIONS_V2,
  PLAZA_AESTHETIC_OPTIONS_V2,
} from '../aestheticCatalog';

const subcategoryLabelMap = new Map<string, string>();
for (const option of [
  ...BUILDING_AESTHETIC_OPTIONS_V2,
  ...ROADWAY_AESTHETIC_OPTIONS_V2,
  ...GREEN_SPACE_AESTHETIC_OPTIONS_V2,
  ...PLAZA_AESTHETIC_OPTIONS_V2,
]) {
  subcategoryLabelMap.set(option.id, option.label);
}

export function resolveZoneLabel(zone: SiteZone): string {
  const props = zone.properties || {};
  for (const prefix of ['development', 'green_space', 'road', 'plaza'] as const) {
    const subcategoryId = props[`${prefix}_subcategory`] as string | undefined;
    const archetypeId = props[`${prefix}_archetype_id`] as string | undefined;
    const aestheticId = props[`${prefix}_aesthetic`] as string | undefined;
    const id = subcategoryId || archetypeId || aestheticId;
    if (id && subcategoryLabelMap.has(id)) {
      return subcategoryLabelMap.get(id)!;
    }
  }
  return zone.name || ZONE_TYPE_CONFIG[zone.zone_type]?.label || zone.zone_type;
}

export function shiftHex(hex: string, hueShift: number, lightnessShift: number): string {
  const r = parseInt(hex.slice(1, 3), 16) / 255;
  const g = parseInt(hex.slice(3, 5), 16) / 255;
  const b = parseInt(hex.slice(5, 7), 16) / 255;
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  let h = 0;
  let s = 0;
  let l = (max + min) / 2;
  if (max !== min) {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    if (max === r) h = ((g - b) / d + (g < b ? 6 : 0)) / 6;
    else if (max === g) h = ((b - r) / d + 2) / 6;
    else h = ((r - g) / d + 4) / 6;
  }
  h = ((h * 360 + hueShift) % 360 + 360) % 360 / 360;
  l = Math.max(0, Math.min(1, l + lightnessShift));
  const hue2rgb = (p: number, q: number, t: number) => {
    if (t < 0) t += 1;
    if (t > 1) t -= 1;
    if (t < 1 / 6) return p + (q - p) * 6 * t;
    if (t < 1 / 2) return q;
    if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
    return p;
  };
  const q2 = l < 0.5 ? l * (1 + s) : l + s - l * s;
  const p2 = 2 * l - q2;
  const toHex = (value: number) => Math.round(value * 255).toString(16).padStart(2, '0');
  return `#${toHex(hue2rgb(p2, q2, h + 1 / 3))}${toHex(hue2rgb(p2, q2, h))}${toHex(hue2rgb(p2, q2, h - 1 / 3))}`;
}

const VARIANT_SHIFTS: [number, number][] = [[0, 0], [8, -0.06], [-8, 0.06], [16, -0.03]];

export function resolveZoneColor(zone: SiteZone): string {
  const props = zone.properties;
  if (props) {
    const archetypeId =
      (props.development_subcategory as string) ||
      (props.road_subcategory as string) ||
      (props.green_space_subcategory as string) ||
      (props.plaza_subcategory as string) ||
      (props.development_archetype_id as string) ||
      (props.road_archetype_id as string) ||
      (props.green_space_archetype_id as string) ||
      (props.plaza_archetype_id as string);

    if (archetypeId) {
      const baseColor = getShadeForArchetype(archetypeId);
      if (baseColor !== '#888888') {
        const variantId =
          (props.development_selected_variant_id as string) ||
          (props.road_selected_variant_id as string) ||
          (props.green_space_selected_variant_id as string) ||
          (props.plaza_selected_variant_id as string) ||
          '';
        const variantMatch = variantId.match(/_v(\d+)$/);
        const variantIndex = variantMatch ? Math.max(0, parseInt(variantMatch[1], 10) - 1) : 0;
        const [hShift, lShift] = VARIANT_SHIFTS[variantIndex % VARIANT_SHIFTS.length];
        return hShift === 0 && lShift === 0 ? baseColor : shiftHex(baseColor, hShift, lShift);
      }
    }

    const developmentType = props.development_type as string | undefined;
    if (developmentType) {
      const apaColor = getColourForDevelopmentType(developmentType);
      if (apaColor.label !== 'Unclassified') return apaColor.fill;
    }
  }

  return ZONE_TYPE_CONFIG[zone.zone_type]?.color || zone.color;
}

export const LINEAR_ZONE_TYPES: SiteZoneType[] = ['road'];

export function isLinearTool(tool: SiteZoneType | null): boolean {
  return tool != null && LINEAR_ZONE_TYPES.includes(tool);
}

export function minPointsForTool(tool: SiteZoneType | null): number {
  return isLinearTool(tool) ? 2 : 3;
}

export function getToolDisplayLabel(tool: SiteZoneType): string {
  if (tool === 'site_boundary') return 'Site Boundary';
  if (tool === 'building' || tool === 'residential') return 'Buildings';
  if (tool === 'road') return 'Streets and Paths';
  if (tool === 'green_space' || tool === 'parking') return 'Parks / Plazas';
  return ZONE_TYPE_CONFIG[tool]?.label || tool;
}

export function haversineDistance(a: number[], b: number[]): number {
  const toRad = (degrees: number) => (degrees * Math.PI) / 180;
  const radius = 6371000;
  const dLat = toRad(b[1] - a[1]);
  const dLon = toRad(b[0] - a[0]);
  const sinLat = Math.sin(dLat / 2);
  const sinLon = Math.sin(dLon / 2);
  const h = sinLat * sinLat + Math.cos(toRad(a[1])) * Math.cos(toRad(b[1])) * sinLon * sinLon;
  return 2 * radius * Math.asin(Math.sqrt(h));
}

export function polylineLength(points: number[][]): number {
  let total = 0;
  for (let i = 1; i < points.length; i += 1) {
    total += haversineDistance(points[i - 1], points[i]);
  }
  return total;
}

export function formatDistance(meters: number): string {
  if (meters < 1000) return `${Math.round(meters)} m`;
  return `${(meters / 1000).toFixed(2)} km`;
}

export function geodesicArea(coords: number[][]): number {
  if (coords.length < 3) return 0;
  const toRad = (degrees: number) => (degrees * Math.PI) / 180;
  const radius = 6371000;
  let total = 0;
  for (let i = 0; i < coords.length; i += 1) {
    const j = (i + 1) % coords.length;
    total += toRad(coords[j][0] - coords[i][0]) * (
      2 + Math.sin(toRad(coords[i][1])) + Math.sin(toRad(coords[j][1]))
    );
  }
  return Math.abs(total * radius * radius / 2);
}

export function formatArea(squareMeters: number): string {
  if (squareMeters < 10000) return `${Math.round(squareMeters).toLocaleString()} m2`;
  return `${(squareMeters / 10000).toFixed(1)} ha`;
}

export function smoothPolyline(points: number[][], segmentsPerSpan = 8): number[][] {
  if (points.length < 3) return points;

  const result: number[][] = [points[0]];
  for (let i = 0; i < points.length - 1; i += 1) {
    const p0 = points[Math.max(0, i - 1)];
    const p1 = points[i];
    const p2 = points[Math.min(points.length - 1, i + 1)];
    const p3 = points[Math.min(points.length - 1, i + 2)];

    for (let step = 1; step <= segmentsPerSpan; step += 1) {
      const t = step / segmentsPerSpan;
      const t2 = t * t;
      const t3 = t2 * t;

      const lng = 0.5 * (
        (2 * p1[0]) +
        (-p0[0] + p2[0]) * t +
        (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
        (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3
      );
      const lat = 0.5 * (
        (2 * p1[1]) +
        (-p0[1] + p2[1]) * t +
        (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
        (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3
      );

      result.push([lng, lat]);
    }
  }

  return result;
}

export function bufferLineToPolygon(points: number[][], widthMeters: number): number[][] {
  if (points.length < 2) return points;

  const halfWidth = widthMeters / 2;
  const lat = points[0][1];
  const metersPerDegLat = 111320;
  const localMetersPerDegLon = metersPerDegLat * Math.cos((lat * Math.PI) / 180);
  const left: number[][] = [];
  const right: number[][] = [];

  for (let i = 0; i < points.length; i += 1) {
    let dx: number;
    let dy: number;
    if (i === 0) {
      dx = points[1][0] - points[0][0];
      dy = points[1][1] - points[0][1];
    } else if (i === points.length - 1) {
      dx = points[i][0] - points[i - 1][0];
      dy = points[i][1] - points[i - 1][1];
    } else {
      dx = points[i + 1][0] - points[i - 1][0];
      dy = points[i + 1][1] - points[i - 1][1];
    }

    const len = Math.sqrt(dx * dx + dy * dy);
    if (len === 0) continue;

    const perpLng = (-dy / len) * (halfWidth / localMetersPerDegLon);
    const perpLat = (dx / len) * (halfWidth / metersPerDegLat);
    left.push([points[i][0] + perpLng, points[i][1] + perpLat]);
    right.push([points[i][0] - perpLng, points[i][1] - perpLat]);
  }

  return [...left, ...right.reverse()];
}

export function computeCentroid(coords: number[][]): [number, number] {
  let lng = 0;
  let lat = 0;
  for (const coord of coords) {
    lng += coord[0];
    lat += coord[1];
  }
  return [lng / coords.length, lat / coords.length];
}

export function computeRotationHandlePos(coords: number[][]): [number, number] {
  const [cx, cy] = computeCentroid(coords);
  const a = coords[0];
  const b = coords[1 % coords.length];
  const midX = (a[0] + b[0]) / 2;
  const midY = (a[1] + b[1]) / 2;
  let dx = midX - cx;
  let dy = midY - cy;
  const len = Math.sqrt(dx * dx + dy * dy);
  if (len < 1e-12) return [cx, cy + 0.00015];

  dx /= len;
  dy /= len;

  let maxDist = 0;
  for (const coord of coords) {
    const dist = Math.sqrt((coord[0] - cx) ** 2 + (coord[1] - cy) ** 2);
    if (dist > maxDist) maxDist = dist;
  }

  const offset = Math.max(maxDist * 1.5, 0.00015);
  return [cx + dx * offset, cy + dy * offset];
}

export function pickSmallestByArea(zones: SiteZone[], candidateIds: string[]): string | null {
  let bestId: string | null = null;
  let bestArea = Infinity;
  for (const candidateId of candidateIds) {
    const zone = zones.find((item) => item.id === candidateId);
    if (zone && zone.coordinates.length >= 3) {
      const area = geodesicArea(zone.coordinates);
      if (area < bestArea) {
        bestArea = area;
        bestId = candidateId;
      }
    }
  }
  return bestId;
}

export function shoelaceArea(coords: number[][]): number {
  let area = 0;
  for (let i = 0; i < coords.length; i += 1) {
    const j = (i + 1) % coords.length;
    area += coords[i][0] * coords[j][1];
    area -= coords[j][0] * coords[i][1];
  }
  return Math.abs(area / 2);
}

export const METERS_PER_DEG_LAT = 111320;

export function metersPerDegLon(lat: number): number {
  return METERS_PER_DEG_LAT * Math.cos((lat * Math.PI) / 180);
}
