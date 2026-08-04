import { useEffect, useState } from 'react';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import { api, documentsApi, rendersApi, siteZonesApi } from '@/services/api';
import { resolveCommunity3DKind } from '@/features/community3d/community3d';
import { isPersistedZoneId } from '@/utils/zoneIdentity';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';

const STREET_NETWORK_ATLAS_FIT = 0.9;
const STREET_NETWORK_ATLAS_CANVAS_SIZE = 1024;
const STREET_NETWORK_GROUND_MODEL = 'gpt-image-2';
const STREET_TEXTURE_TIMEOUT_MS = 60_000;
const STREET_TEXTURE_FETCH_ATTEMPTS = 2;

export interface StreetNetworkGroundBBox {
  west: number;
  south: number;
  east: number;
  north: number;
}

export interface StreetNetworkGroundUVRect {
  u0: number;
  v0: number;
  u1: number;
  v1: number;
}

export interface StreetNetworkGroundTextureMeta {
  schema_version: 1;
  url: string;
  document_id: string;
  bbox: StreetNetworkGroundBBox;
  uv_rect: StreetNetworkGroundUVRect;
  size_m: { width: number; height: number };
  model: string;
  provider: 'openai' | 'google' | 'imported';
  generated_at: string;
  source_signature: string;
  zone_source_signature: string;
  boundary_zone_id: string;
  road_zone_ids: string[];
  source: 'ai_network_atlas';
}

export interface StreetNetworkPlacement {
  bbox: StreetNetworkGroundBBox;
  uv_rect: StreetNetworkGroundUVRect;
  size_m: { width: number; height: number };
  boundary_zone_id: string;
  road_zone_ids: string[];
  source_signature: string;
}

export interface StreetNetworkGroundGenerationOptions {
  /** Compressed current globe frame containing Google tiles and proposal context. */
  sceneContextImageBase64?: string | null;
}

function finiteCoordinate(value: unknown): number | null {
  const number = Number(value);
  return Number.isFinite(number) ? Math.round(number * 1_000_000_000) / 1_000_000_000 : null;
}

function compactHash(value: string): string {
  let left = 2_166_136_261;
  let right = 2_166_136_261 ^ 0x9e3779b9;
  for (let index = 0; index < value.length; index += 1) {
    const code = value.charCodeAt(index);
    left = Math.imul(left ^ code, 16_777_619);
    right = Math.imul(right ^ code, 2_246_822_519);
  }
  return [left, right]
    .map((hash) => (hash >>> 0).toString(16).padStart(8, '0'))
    .join('');
}

/** Geometry and design inputs that make one road's pixels current. */
export function streetZoneSourceSignature(zone: SiteZone): string {
  const properties = (zone.properties ?? {}) as Record<string, unknown>;
  return compactHash(JSON.stringify({
    id: zone.id,
    coordinates: zone.coordinates.map((coordinate) => [
      finiteCoordinate(coordinate[0]),
      finiteCoordinate(coordinate[1]),
    ]),
    width: properties.width ?? null,
    clear_width_m: properties.clear_width_m ?? null,
    street_role: properties.street_role ?? null,
    plan_centerline: properties.plan_centerline ?? null,
    road_archetype_id: properties.road_archetype_id ?? null,
    road_selected_variant_id: properties.road_selected_variant_id ?? null,
    plan_boundary_zone_id: properties._plan_boundary_zone_id ?? null,
  }));
}

function selectStreetNetworkZones(zones: SiteZone[], boundaryZoneId?: string): SiteZone[] {
  return zones
    .filter((zone) => (
      resolveCommunity3DKind(zone) === 'street'
      && zone.coordinates.length >= 3
      && isPersistedZoneId(zone.id)
      && (!boundaryZoneId || !zone.properties?._plan_boundary_zone_id
        || zone.properties._plan_boundary_zone_id === boundaryZoneId)
    ))
    .sort((left, right) => left.id.localeCompare(right.id));
}

/** Reproduce the pilot atlas' north-up 90%-fit placement from live geometry. */
export function buildStreetNetworkPlacement(zones: SiteZone[]): StreetNetworkPlacement | null {
  const boundary = getActiveSiteBoundary(zones);
  if (!boundary) return null;
  const roads = selectStreetNetworkZones(zones, boundary.id);
  if (roads.length === 0) return null;

  const points = boundary.coordinates.filter((coordinate) => (
    Number.isFinite(coordinate[0]) && Number.isFinite(coordinate[1])
  ));
  if (points.length < 3) return null;
  const west = Math.min(...points.map((coordinate) => coordinate[0]));
  const east = Math.max(...points.map((coordinate) => coordinate[0]));
  const south = Math.min(...points.map((coordinate) => coordinate[1]));
  const north = Math.max(...points.map((coordinate) => coordinate[1]));
  const latitude = (south + north) / 2;
  const widthM = (east - west) * metersPerDegLon(latitude);
  const heightM = (north - south) * METERS_PER_DEG_LAT;
  const longest = Math.max(widthM, heightM);
  if (!(longest > 0)) return null;

  const fittedWidth = STREET_NETWORK_ATLAS_FIT * widthM / longest;
  const fittedHeight = STREET_NETWORK_ATLAS_FIT * heightM / longest;
  const roadZoneIds = roads.map((zone) => zone.id);
  const sourceSignature = compactHash(JSON.stringify(
    roads.map((zone) => [zone.id, streetZoneSourceSignature(zone)]),
  ));
  return {
    bbox: { west, south, east, north },
    uv_rect: {
      u0: (1 - fittedWidth) / 2,
      v0: (1 - fittedHeight) / 2,
      u1: (1 + fittedWidth) / 2,
      v1: (1 + fittedHeight) / 2,
    },
    size_m: {
      width: Math.round(widthM * 100) / 100,
      height: Math.round(heightM * 100) / 100,
    },
    boundary_zone_id: boundary.id,
    road_zone_ids: roadZoneIds,
    source_signature: sourceSignature,
  };
}

export function getStreetNetworkGroundMeta(zone: SiteZone): StreetNetworkGroundTextureMeta | null {
  if (resolveCommunity3DKind(zone) !== 'street') return null;
  const meta = (zone.properties as Record<string, unknown> | undefined)
    ?.street_network_ground_texture as StreetNetworkGroundTextureMeta | undefined;
  if (
    !meta
    || meta.schema_version !== 1
    || typeof meta.url !== 'string'
    || !meta.bbox
    || !meta.uv_rect
    || !Array.isArray(meta.road_zone_ids)
    || !meta.road_zone_ids.includes(zone.id)
    || meta.zone_source_signature !== streetZoneSourceSignature(zone)
  ) return null;
  return meta;
}

/** Return the one current shared atlas only when every road in the active
 * network points at the same complete, geometry-current document. */
export function getCurrentStreetNetworkGroundMeta(
  zones: SiteZone[],
): StreetNetworkGroundTextureMeta | null {
  const placement = buildStreetNetworkPlacement(zones);
  if (!placement) return null;
  const roads = selectStreetNetworkZones(zones, placement.boundary_zone_id)
    .filter((zone) => placement.road_zone_ids.includes(zone.id));
  if (roads.length !== placement.road_zone_ids.length) return null;
  const metas = roads.map(getStreetNetworkGroundMeta);
  const first = metas[0];
  if (!first || first.source_signature !== placement.source_signature) return null;
  const expectedIds = [...placement.road_zone_ids].sort().join('|');
  return metas.every((meta) => (
    meta
    && meta.document_id === first.document_id
    && meta.source_signature === placement.source_signature
    && [...meta.road_zone_ids].sort().join('|') === expectedIds
  )) ? first : null;
}

interface StreetNetworkDiagram {
  dataUrl: string;
  placement: StreetNetworkPlacement;
  archetypeIds: string[];
}

function polygonPoints(
  zone: SiteZone,
  toPixel: (coordinate: number[]) => [number, number],
): Array<[number, number]> {
  return zone.coordinates
    .filter((coordinate) => Number.isFinite(coordinate[0]) && Number.isFinite(coordinate[1]))
    .map(toPixel);
}

function fillPolygon(
  context: CanvasRenderingContext2D,
  points: Array<[number, number]>,
  fill: string,
  stroke: string,
  lineWidth = 1,
): void {
  if (points.length < 3) return;
  context.beginPath();
  context.moveTo(points[0][0], points[0][1]);
  points.slice(1).forEach(([x, y]) => context.lineTo(x, y));
  context.closePath();
  context.fillStyle = fill;
  context.fill();
  context.strokeStyle = stroke;
  context.lineWidth = lineWidth;
  context.stroke();
}

function fallbackCenterline(points: Array<[number, number]>): Array<[number, number]> {
  if (points.length < 3) return [];
  const center = points.reduce(
    (sum, point) => [sum[0] + point[0] / points.length, sum[1] + point[1] / points.length],
    [0, 0],
  );
  let xx = 0;
  let xy = 0;
  let yy = 0;
  points.forEach(([x, y]) => {
    const dx = x - center[0];
    const dy = y - center[1];
    xx += dx * dx;
    xy += dx * dy;
    yy += dy * dy;
  });
  const angle = 0.5 * Math.atan2(2 * xy, xx - yy);
  const axis: [number, number] = [Math.cos(angle), Math.sin(angle)];
  const projections = points.map(([x, y]) => (
    (x - center[0]) * axis[0] + (y - center[1]) * axis[1]
  ));
  const min = Math.min(...projections) * 0.92;
  const max = Math.max(...projections) * 0.92;
  return [
    [center[0] + axis[0] * min, center[1] + axis[1] * min],
    [center[0] + axis[0] * max, center[1] + axis[1] * max],
  ];
}

/** Build the immutable north-up whole-site geometry contract sent to the image
 * model. The generated pixels are later sampled only inside exact road meshes. */
export function buildStreetNetworkDiagram(zones: SiteZone[]): StreetNetworkDiagram | null {
  if (typeof document === 'undefined') return null;
  const placement = buildStreetNetworkPlacement(zones);
  if (!placement) return null;
  const boundary = zones.find((zone) => zone.id === placement.boundary_zone_id);
  if (!boundary) return null;
  const roads = selectStreetNetworkZones(zones, placement.boundary_zone_id)
    .filter((zone) => placement.road_zone_ids.includes(zone.id));
  const canvas = document.createElement('canvas');
  canvas.width = STREET_NETWORK_ATLAS_CANVAS_SIZE;
  canvas.height = STREET_NETWORK_ATLAS_CANVAS_SIZE;
  const context = canvas.getContext('2d');
  if (!context) return null;
  context.fillStyle = '#e6e1d6';
  context.fillRect(0, 0, canvas.width, canvas.height);

  const { bbox, uv_rect: uv } = placement;
  const x0 = uv.u0 * canvas.width;
  const y0 = (1 - uv.v1) * canvas.height;
  const fittedWidth = (uv.u1 - uv.u0) * canvas.width;
  const fittedHeight = (uv.v1 - uv.v0) * canvas.height;
  const toPixel = (coordinate: number[]): [number, number] => [
    x0 + ((coordinate[0] - bbox.west) / Math.max(1e-12, bbox.east - bbox.west)) * fittedWidth,
    y0 + ((bbox.north - coordinate[1]) / Math.max(1e-12, bbox.north - bbox.south)) * fittedHeight,
  ];

  fillPolygon(context, polygonPoints(boundary, toPixel), '#b8cba5', '#625f58', 3);
  zones.forEach((zone) => {
    const kind = resolveCommunity3DKind(zone);
    if (kind === 'park') {
      fillPolygon(context, polygonPoints(zone, toPixel), '#8fae78', '#5f7252', 1.5);
    } else if (kind === 'building') {
      fillPolygon(context, polygonPoints(zone, toPixel), '#d8c9b4', '#775f4d', 1.5);
    }
  });

  roads.forEach((road) => {
    fillPolygon(context, polygonPoints(road, toPixel), '#c8c3b8', '#36393a', 2);
  });
  roads.forEach((road) => {
    const props = (road.properties ?? {}) as Record<string, unknown>;
    const role = String(props.street_role ?? '').toLowerCase();
    const row = polygonPoints(road, toPixel);
    const authored = Array.isArray(props.plan_centerline)
      ? (props.plan_centerline as unknown[])
          .filter((point): point is number[] => (
            Array.isArray(point) && Number.isFinite(point[0]) && Number.isFinite(point[1])
          ))
          .map(toPixel)
      : [];
    const line = authored.length >= 2 ? authored : fallbackCenterline(row);
    if (line.length < 2) return;
    const metresPerPixel = Math.max(placement.size_m.width, placement.size_m.height)
      / (STREET_NETWORK_ATLAS_CANVAS_SIZE * STREET_NETWORK_ATLAS_FIT);
    const clearWidth = Number(props.clear_width_m ?? props.width ?? (role === 'path' ? 3.5 : 6));
    context.beginPath();
    context.moveTo(line[0][0], line[0][1]);
    line.slice(1).forEach(([x, y]) => context.lineTo(x, y));
    context.lineCap = 'butt';
    context.lineJoin = 'miter';
    context.strokeStyle = role === 'path' ? '#9b8668' : '#5c6061';
    context.lineWidth = Math.max(3, clearWidth / Math.max(0.01, metresPerPixel));
    context.stroke();
    if (role !== 'path' && role !== 'roundabout') {
      context.setLineDash(role === 'spine' ? [14, 9] : [9, 12]);
      context.strokeStyle = role === 'spine' ? '#d6b854' : '#e8e7e1';
      context.lineWidth = Math.max(1.5, 0.18 / Math.max(0.01, metresPerPixel));
      context.stroke();
      context.setLineDash([]);
    }
  });

  const archetypeIds = [...new Set(roads.map((road) => (
    String((road.properties as Record<string, unknown> | undefined)?.road_archetype_id ?? 'urban-local-street')
  )))];
  return { dataUrl: canvas.toDataURL('image/png'), placement, archetypeIds };
}

function streetNetworkPrompt(diagram: StreetNetworkDiagram): string {
  return [
    'Create one photorealistic north-up orthographic ground-material atlas for the connected street and pathway network in Image 1.',
    `The immutable site is approximately ${Math.round(diagram.placement.size_m.width)} by ${Math.round(diagram.placement.size_m.height)} metres.`,
    `Respect these selected street families: ${diagram.archetypeIds.join(', ')}.`,
    'Image 1 is the exact, to-scale geometry contract. Preserve every footprint, width, right angle, connection, junction, curb edge, pathway and roundabout pixel-for-pixel.',
    'Make all streets work with the adjacent building pads and green park polygons as one coordinated development.',
    'Replace semantic colours with realistic restrained urban materials: locally plausible medium-grey asphalt with fine aggregate and subtle wear, pale cast-in-place concrete sidewalks with correctly scaled joints, curb-and-gutter bands, planted boulevards, and crisp slightly weathered markings.',
    'No invented ramps, highway channelization, disconnected lanes, moved roads, added roads, removed roads, perspective, labels or watermark.',
    'GROUND MATERIALS ONLY. Do not add buildings, roofs, tree canopies, vehicles, people, benches, lights, signs, equipment or shadows from vertical objects; City Prompt places those as separate 3D models afterward.',
    'Camera exactly 90-degree nadir, zero perspective, even overcast midday lighting. Output must register pixel-for-pixel to Image 1.',
  ].join(' ');
}

function base64ImageFile(value: string, name: string): File {
  const encoded = value.includes(',') ? value.split(',').pop() ?? '' : value;
  const bytes = Uint8Array.from(atob(encoded), (character) => character.charCodeAt(0));
  return new File([bytes], name, { type: 'image/png' });
}

/** Generate and persist one geometry-locked AI atlas for the complete active
 * street network. Costs one image call regardless of road polygon count. */
export async function generateStreetNetworkGroundTexture(
  projectId: string,
  zones: SiteZone[],
  options: StreetNetworkGroundGenerationOptions = {},
): Promise<StreetNetworkGroundTextureMeta> {
  const diagram = buildStreetNetworkDiagram(zones);
  if (!diagram) throw new Error('A saved site boundary and street network are required.');
  const { image_base64: imageBase64 } = await rendersApi.generateEdit({
    image_base64: diagram.dataUrl.split(',')[1] ?? '',
    mask_base64: '',
    prompt: streetNetworkPrompt(diagram),
    archetype_images: options.sceneContextImageBase64
      ? [{
          image_base64: options.sceneContextImageBase64,
          label: 'LIVE GOOGLE-TILE SITE CONTEXT: use only for local material character, grade and edge relationships; Image 1 remains the immutable geometry contract',
        }]
      : undefined,
    model: STREET_NETWORK_GROUND_MODEL,
    image_quality: 'high',
    project_id: projectId,
  });
  if (!imageBase64) throw new Error('Street drape generation returned no image.');
  return importStreetNetworkGroundTexture(
    projectId,
    zones,
    base64ImageFile(imageBase64, `street-network-${diagram.placement.source_signature}.png`),
    { model: STREET_NETWORK_GROUND_MODEL, provider: 'openai' },
  );
}

/** Upload one reviewed atlas and attach the shared placement contract to every road. */
export async function importStreetNetworkGroundTexture(
  projectId: string,
  zones: SiteZone[],
  textureFile: File,
  options: {
    model?: string;
    provider?: StreetNetworkGroundTextureMeta['provider'];
  } = {},
): Promise<StreetNetworkGroundTextureMeta> {
  if (!textureFile.type.startsWith('image/')) {
    throw new Error('Choose a PNG or JPEG street-network atlas.');
  }
  const placement = buildStreetNetworkPlacement(zones);
  if (!placement) throw new Error('A saved site boundary and road network are required.');
  const roads = selectStreetNetworkZones(zones)
    .filter((zone) => placement.road_zone_ids.includes(zone.id));
  const document = await documentsApi.upload(projectId, textureFile, 'reference');
  const sharedMeta = {
    schema_version: 1 as const,
    url: `/api/v1/documents/${document.id}/file`,
    document_id: document.id,
    bbox: placement.bbox,
    uv_rect: placement.uv_rect,
    size_m: placement.size_m,
    model: options.model ?? 'reviewed-network-atlas',
    provider: options.provider ?? 'imported',
    generated_at: new Date().toISOString(),
    source_signature: placement.source_signature,
    boundary_zone_id: placement.boundary_zone_id,
    road_zone_ids: placement.road_zone_ids,
    source: 'ai_network_atlas' as const,
  };

  let applied = 0;
  try {
    for (const road of roads) {
      const meta: StreetNetworkGroundTextureMeta = {
        ...sharedMeta,
        zone_source_signature: streetZoneSourceSignature(road),
      };
      await siteZonesApi.update(road.id, {
        properties: {
          ...((road.properties as Record<string, unknown> | undefined) ?? {}),
          street_network_ground_texture: meta,
        },
      });
      applied += 1;
    }
  } catch (error) {
    const detail = error instanceof Error && error.message ? ` ${error.message}` : '';
    throw new Error(
      `The atlas uploaded, but was attached to only ${applied}/${roads.length} roads. Retry the import to finish the network.${detail}`,
    );
  }
  return {
    ...sharedMeta,
    zone_source_signature: streetZoneSourceSignature(roads[0]),
  };
}

const textureCache = new Map<string, THREE.Texture>();
const texturePromiseCache = new Map<string, Promise<THREE.Texture>>();

async function loadStreetNetworkTexture(url: string): Promise<THREE.Texture> {
  const cached = textureCache.get(url);
  if (cached) return cached;
  const pending = texturePromiseCache.get(url);
  if (pending) return pending;
  const promise = (async () => {
    let lastError: unknown;
    for (let attempt = 0; attempt < STREET_TEXTURE_FETCH_ATTEMPTS; attempt += 1) {
      try {
        const { data } = await api.get<Blob>(url, {
          responseType: 'blob',
          timeout: STREET_TEXTURE_TIMEOUT_MS,
        });
        const objectUrl = URL.createObjectURL(data);
        try {
          const texture = await new THREE.TextureLoader().loadAsync(objectUrl);
          texture.colorSpace = THREE.SRGBColorSpace;
          texture.anisotropy = 8;
          textureCache.set(url, texture);
          return texture;
        } finally {
          URL.revokeObjectURL(objectUrl);
        }
      } catch (error) {
        lastError = error;
      }
    }
    throw lastError;
  })();
  texturePromiseCache.set(url, promise);
  void promise.then(
    () => texturePromiseCache.delete(url),
    () => texturePromiseCache.delete(url),
  );
  return promise;
}

export function useStreetNetworkGroundTexture(zone: SiteZone): {
  meta: StreetNetworkGroundTextureMeta | null;
  texture: THREE.Texture | null;
} {
  const meta = getStreetNetworkGroundMeta(zone);
  const url = meta?.url ?? null;
  const [texture, setTexture] = useState<THREE.Texture | null>(
    url ? textureCache.get(url) ?? null : null,
  );
  useEffect(() => {
    if (!url) {
      setTexture(null);
      return undefined;
    }
    const cached = textureCache.get(url);
    if (cached) {
      setTexture(cached);
      return undefined;
    }
    let cancelled = false;
    loadStreetNetworkTexture(url)
      .then((loaded) => {
        if (!cancelled) setTexture(loaded);
      })
      .catch((error) => console.warn('[streetNetworkGroundTexture] texture fetch failed', error));
    return () => {
      cancelled = true;
    };
  }, [url]);
  return { meta, texture };
}
