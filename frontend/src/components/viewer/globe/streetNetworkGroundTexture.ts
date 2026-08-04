import { useEffect, useState } from 'react';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import { api, documentsApi, siteZonesApi } from '@/services/api';
import { resolveCommunity3DKind } from '@/features/community3d/community3d';
import { isPersistedZoneId } from '@/utils/zoneIdentity';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';

const STREET_NETWORK_ATLAS_FIT = 0.9;
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
