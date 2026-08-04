/**
 * Per-zone AI park ground textures (productionized from the 2026-07-11 pilot).
 *
 * Flow: zone polygon -> to-scale letterboxed diagram (canvas) -> Gemini via
 * the existing /render/generate proxy -> uploaded as a reference document ->
 * meta persisted on zone.properties.park_ground_texture -> GlobeZoneLayer
 * drapes it on the green_space fill mesh (UVs from vertex lng/lat).
 *
 * Gemini is the default model: the A/B pilot showed its muted palette blends
 * better with Google photorealistic tiles than GPT Image 2's saturated look.
 */
import { useEffect, useMemo, useState } from 'react';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import { api, documentsApi, rendersApi, siteZonesApi } from '@/services/api';
import { isCommunity3DCompiled } from '@/features/community3d/community3d';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import {
  computeParkPlacements,
  resolveParkRecipeForZone,
  type PropPlacement,
} from './parkScatter';
import {
  describeParkGroundGuideFit,
  fitParkGroundGuides,
  parkGroundSourceSignature,
  resolveParkGuideDimensionsM,
  resolveParkGroundProfile,
  resolveParkPlantingStructure,
  type ParkGroundGuide,
} from './parkGroundProfiles';
import {
  resolveParkLegoAppearance,
  resolveParkLegoContract,
  resolveParkProgramAnchorLayout,
  type ParkLegoAppearance,
} from './parkLegoFamilies';
import {
  buildPublicRealmContextPrompt,
  buildPublicRealmGenerationContext,
} from './publicRealmGenerationContext';

const CANVAS = 1024;
const PROCEDURAL_CANVAS = 512;
/** Park occupies this fraction of the canvas' limiting dimension. */
const FIT = 0.86;
const PARK_GROUND_MODEL = 'gemini-3.1-flash-image';
const PARK_TEXTURE_TIMEOUT_MS = 60_000;
const PARK_TEXTURE_FETCH_ATTEMPTS = 2;

/** Paid park-ground work is deliberately chunked so a large master plan
 * cannot fan out dozens of image calls from one click. */
export const MAX_PARK_GROUND_BATCH_CALLS = 6;

export function takeParkGroundBatch<T>(zones: T[]): T[] {
  return zones.slice(0, MAX_PARK_GROUND_BATCH_CALLS);
}

export interface ParkGroundBBox {
  west: number;
  south: number;
  east: number;
  north: number;
}

export interface ParkGroundUVRect {
  u0: number;
  v0: number;
  u1: number;
  v1: number;
}

export interface ParkGroundTextureMeta {
  url: string;
  document_id: string;
  bbox: ParkGroundBBox;
  /** UV sub-rect of the zone bbox inside the letterboxed texture (v=0 at
   * image bottom, matching three.js flipY convention). */
  uv_rect: ParkGroundUVRect;
  size_m: { width: number; height: number };
  model: string;
  generated_at: string;
  source_signature: string;
  profile_id: string;
  profile_version: number;
  archetype_id: string;
  variant_id?: string;
  /** Saved photoreal render used as the appearance target for this drape. */
  appearance_reference_render_id?: string;
  /** Persisted image-model output or the zero-call live fallback. Older
   * persisted metadata omits this field and is therefore treated as AI. */
  source?: 'ai' | 'procedural';
  /** Context contract used for the paid material pass. Optional for older
   * textures created before surrounding-site conditioning was introduced. */
  context_version?: 1;
  context_neighbor_ids?: string[];
  google_tile_context_attached?: boolean;
}

export interface ParkGroundGenerationOptions {
  /** Current project-visible proposal zones used to measure edge adjacency. */
  siteZones?: SiteZone[];
  /** Compressed current globe frame containing Google tiles and mounted 3D. */
  sceneContextImageBase64?: string | null;
}

/** Public-realm polygons that can own an authored park/plaza ground drape.
 * Planner courtyards often retain a development-like zone_type, while the
 * legacy toolbar stores plazas as `parking`, so zone_type alone is not enough. */
export function isParkGroundZone(
  zone: Pick<SiteZone, 'zone_type' | 'properties'>,
): boolean {
  const props = (zone.properties ?? {}) as Record<string, unknown>;
  const role = props._plan_role;
  return ['green_space', 'park', 'plaza', 'parking'].includes(zone.zone_type)
    || role === 'open_space'
    || role === 'courtyard'
    || typeof props.green_space_archetype_id === 'string'
    || typeof props.plaza_archetype_id === 'string';
}

/** Final mixed-scene renders need the exact internal geometry of only the
 * most design-critical visible parks. Sending every park diagram from a large
 * master plan would crowd out building/style references and weaken all of
 * them, so this selection is deliberately small and deterministic. */
export const MAX_PARK_RENDER_GEOMETRY_REFERENCES = 4;

function parkRenderGeometryPriority(zone: SiteZone): number {
  const archetypeId = resolveParkGroundProfile(zone).archetypeId;
  if (archetypeId.startsWith('reservoir_watershed_park')) return 100;
  if (archetypeId.startsWith('stormwater_retention_pond')) return 98;
  if (archetypeId.startsWith('japanese_garden')) return 95;
  if (archetypeId.startsWith('sports_field_complex')) return 94;
  if (archetypeId.startsWith('botanical_garden')) return 93;
  if (archetypeId.startsWith('urban_forest')) return 92;
  if (archetypeId.startsWith('nature_play_area')) return 91;
  if (archetypeId.startsWith('formal_civic_plaza')) return 90;
  if (archetypeId.startsWith('fountain_water_feature')) return 88;
  if (archetypeId.startsWith('linear_park_greenway')) return 84;
  if (archetypeId.startsWith('urban_pocket_park')) return 72;
  if (archetypeId.startsWith('neighborhood_park')) return 70;
  return 50;
}

function parkRenderAreaM2(zone: SiteZone): number {
  const ring = zone.coordinates ?? [];
  if (ring.length < 3) return 0;
  const meanLat = ring.reduce((sum, coordinate) => sum + coordinate[1], 0) / ring.length;
  const metresPerLng = metersPerDegLon(meanLat);
  let doubledArea = 0;
  for (let index = 0; index < ring.length; index += 1) {
    const [lngA, latA] = ring[index];
    const [lngB, latB] = ring[(index + 1) % ring.length];
    doubledArea += (lngA * metresPerLng) * (latB * METERS_PER_DEG_LAT)
      - (lngB * metresPerLng) * (latA * METERS_PER_DEG_LAT);
  }
  return Math.abs(doubledArea) / 2;
}

export function selectParkRenderGeometryZones(
  zones: SiteZone[],
  maxReferences = MAX_PARK_RENDER_GEOMETRY_REFERENCES,
): SiteZone[] {
  if (maxReferences <= 0) return [];
  return zones
    .filter((zone) => (
      isParkGroundZone(zone)
      && (zone.coordinates?.length ?? 0) >= 3
      && resolveParkGroundProfile(zone).guides.length > 0
    ))
    .sort((a, b) => (
      parkRenderGeometryPriority(b) - parkRenderGeometryPriority(a)
      || parkRenderAreaM2(b) - parkRenderAreaM2(a)
      || a.id.localeCompare(b.id)
    ))
    .slice(0, maxReferences);
}

/** Read persisted texture meta off a zone; null unless complete. */
export function getParkGroundMeta(zone: SiteZone): ParkGroundTextureMeta | null {
  if (!isParkGroundZone(zone)) return null;
  const meta = (zone.properties as Record<string, unknown> | undefined)
    ?.park_ground_texture as ParkGroundTextureMeta | undefined;
  if (!meta || typeof meta.url !== 'string' || !meta.bbox || !meta.uv_rect) return null;
  if (meta.source_signature !== parkGroundSourceSignature(zone)) return null;
  return meta;
}

export type ParkGroundSurfaceSource = 'ai' | 'procedural' | 'none';

/** Choose the best current live surface without spending credits. A valid AI
 * orthophoto always wins; compiled parks otherwise receive the deterministic
 * archetype surface produced locally in the browser. */
export function resolveParkGroundSurfaceSource(zone: SiteZone): ParkGroundSurfaceSource {
  if (getParkGroundMeta(zone)) return 'ai';
  if (isParkGroundZone(zone) && isCommunity3DCompiled(zone)) return 'procedural';
  return 'none';
}

export function hasCurrentParkGroundSurface(zone: SiteZone): boolean {
  return resolveParkGroundSurfaceSource(zone) !== 'none';
}

/** Uncompiled park candidates defer finishing props. Once a park is compiled,
 * both procedural and AI-upgraded grounds retain the same locked topology and
 * may show their deterministic 3D canopy and seating in Google Tiles. */
export function shouldDeferParkFinishingProp(
  zone: SiteZone,
  propId: PropPlacement['propId'],
): boolean {
  return isParkGroundZone(zone)
    && !isCommunity3DCompiled(zone)
    && (propId === 'tree' || propId === 'bench');
}

/** Manifest gate for catalog props. Executable Public Realm LEGO program
 * modules are resolved procedurally by GlobeParkKitLayer before this check;
 * other catalog props render only when their reviewed asset exists. */
export function shouldRenderLiveParkProp(
  zone: SiteZone,
  propId: PropPlacement['propId'],
  hasRealAsset: boolean,
): boolean {
  return hasRealAsset && !shouldDeferParkFinishingProp(zone, propId);
}

interface ParkDiagram {
  canvas: HTMLCanvasElement;
  dataUrl: string;
  bbox: ParkGroundBBox;
  uvRect: ParkGroundUVRect;
  sizeM: { width: number; height: number };
  /** Which fixed program markers were drawn (drives the prompt text).
   * `bench` remains for caller compatibility but is always zero: benches are
   * designed only after paths and water are fixed. */
  markers: { playground: number; pavilion: number; bench: number; plaza: number; access?: number };
  /** Effective fixed program after whole-element parcel fit preflight. */
  guides: ParkGroundGuide[];
  fitInstruction: string;
}

export type ParkDiagramMode = 'conditioning' | 'procedural';

/** Marker palette — must stay in sync with buildParkGroundPrompt's wording. */
const MARKER_COLORS = {
  playground: '#e0c88f', // sand-tan pad
  pavilion: '#8a6b4a',   // brown pad
  plaza: '#cfcfc8',      // light-grey disc
  access: '#f4ead2',     // pale-cream required path gateway
} as const;

function parkAccessPoints(zone: SiteZone): Array<[number, number]> {
  const raw = (zone.properties as Record<string, unknown> | undefined)?.park_access_points;
  if (!Array.isArray(raw)) return [];
  return raw.flatMap((candidate) => {
    if (!Array.isArray(candidate) || candidate.length < 2) return [];
    const lng = Number(candidate[0]);
    const lat = Number(candidate[1]);
    return Number.isFinite(lng) && Number.isFinite(lat) ? [[lng, lat] as [number, number]] : [];
  });
}

function ringContains(x: number, y: number, ring: Array<[number, number]>): boolean {
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [xi, yi] = ring[i];
    const [xj, yj] = ring[j];
    if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) {
      inside = !inside;
    }
  }
  return inside;
}

export function resolveParkGroundGuideFit(
  zone: SiteZone,
  sizeM: { width: number; height: number },
) {
  const ring = zone.coordinates ?? [];
  if (ring.length < 3) {
    return fitParkGroundGuides(resolveParkGroundProfile(zone).guides, sizeM, []);
  }
  const lngs = ring.map(([lng]) => lng);
  const lats = ring.map(([, lat]) => lat);
  const west = Math.min(...lngs);
  const east = Math.max(...lngs);
  const south = Math.min(...lats);
  const north = Math.max(...lats);
  const lngSpan = Math.max(east - west, Number.EPSILON);
  const latSpan = Math.max(north - south, Number.EPSILON);
  const normalizedRing = ring.map(([lng, lat]) => ([
    (lng - west) / lngSpan,
    (north - lat) / latSpan,
  ] as [number, number]));
  return fitParkGroundGuides(
    resolveParkGroundProfile(zone).guides,
    sizeM,
    normalizedRing,
  );
}

export function resolveParkGroundFitInstruction(zone: SiteZone): string {
  const ring = zone.coordinates ?? [];
  if (ring.length < 3) return '';
  const lngs = ring.map(([lng]) => lng);
  const lats = ring.map(([, lat]) => lat);
  const west = Math.min(...lngs);
  const east = Math.max(...lngs);
  const south = Math.min(...lats);
  const north = Math.max(...lats);
  const width = (east - west) * metersPerDegLon((south + north) / 2);
  const height = (north - south) * METERS_PER_DEG_LAT;
  if (width <= 0 || height <= 0) return '';
  return describeParkGroundGuideFit(resolveParkGroundGuideFit(zone, { width, height }));
}

function drawParkGuides(
  ctx: CanvasRenderingContext2D,
  guides: ParkGroundGuide[],
  ringPx: Array<[number, number]>,
  x0: number,
  y0: number,
  parkW: number,
  parkH: number,
  pxPerM: number,
  mode: ParkDiagramMode,
  archetypeId: string,
): void {
  if (guides.length === 0) return;
  const [centroidX, centroidY] = ringPx.reduce(
    ([sumX, sumY], [x, y]) => [sumX + x, sumY + y],
    [0, 0],
  ).map((value) => value / ringPx.length) as [number, number];
  let covarianceXX = 0;
  let covarianceXY = 0;
  let covarianceYY = 0;
  for (const [x, y] of ringPx) {
    const dx = x - centroidX;
    const dy = y - centroidY;
    covarianceXX += dx * dx;
    covarianceXY += dx * dy;
    covarianceYY += dy * dy;
  }
  const principalAngle = 0.5 * Math.atan2(
    2 * covarianceXY,
    covarianceXX - covarianceYY,
  );
  const principalX = Math.cos(principalAngle);
  const principalY = Math.sin(principalAngle);
  const axisProjections = ringPx.map(([x, y]) => (
    (x - centroidX) * principalX + (y - centroidY) * principalY
  ));
  const axisMin = Math.min(...axisProjections);
  const axisMax = Math.max(...axisProjections);
  const parkSizeM = { width: parkW / pxPerM, height: parkH / pxPerM };
  const isJapaneseGarden = archetypeId.startsWith('japanese_garden');
  const isBotanicalGarden = archetypeId.startsWith('botanical_garden');
  const isNaturePlay = archetypeId.startsWith('nature_play_area');
  ctx.save();
  ctx.beginPath();
  ringPx.forEach(([x, y], index) => {
    if (index === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.closePath();
  ctx.clip();

  for (const guide of guides) {
    const x = x0 + guide.x * parkW;
    const y = y0 + guide.y * parkH;
    ctx.save();
    try {
      if (guide.rotationDeg) {
        ctx.translate(x, y);
        ctx.rotate((guide.rotationDeg * Math.PI) / 180);
        ctx.translate(-x, -y);
      }
    const sizeM = resolveParkGuideDimensionsM(guide, parkSizeM);
    const width = sizeM.width * pxPerM;
    const height = sizeM.height * pxPerM;
    const isMarkedSportsSurface = guide.kind === 'soccer_field' || guide.kind === 'tennis_court';
    if (mode === 'procedural' && !isMarkedSportsSurface) {
      const material = ctx.createLinearGradient(
        x - width / 2,
        y - height / 2,
        x + width / 2,
        y + height / 2,
      );
      material.addColorStop(0, guide.color);
      material.addColorStop(0.55, guide.color);
      material.addColorStop(1, guide.strokeColor ?? guide.color);
      ctx.fillStyle = material;
    } else {
      ctx.fillStyle = guide.color;
    }
    ctx.strokeStyle = guide.strokeColor ?? guide.color;
    ctx.lineWidth = Math.max(1, (guide.strokeWidthM ?? 0.4) * pxPerM);

    if (guide.kind === 'line') {
      if (isJapaneseGarden && mode === 'procedural') {
        const landingDepth = 1.8 * pxPerM;
        const landingWidth = 2.7 * pxPerM;
        ctx.fillStyle = '#7d776b';
        ctx.strokeStyle = '#5e5b53';
        ctx.lineWidth = Math.max(1, 0.18 * pxPerM);
        for (const direction of [-1, 1]) {
          const landingX = x + direction * (width / 2 + landingDepth / 2);
          ctx.fillRect(
            landingX - landingDepth / 2,
            y - landingWidth / 2,
            landingDepth,
            landingWidth,
          );
          ctx.strokeRect(
            landingX - landingDepth / 2,
            y - landingWidth / 2,
            landingDepth,
            landingWidth,
          );
        }
        continue;
      }
      ctx.beginPath();
      ctx.moveTo(x - width / 2, y - height / 2);
      ctx.lineTo(x + width / 2, y + height / 2);
      ctx.strokeStyle = guide.color;
      ctx.lineWidth = Math.max(2, (guide.strokeWidthM ?? 1.5) * pxPerM);
      ctx.stroke();
      continue;
    }

    if (guide.kind === 'polyline' && (guide.points?.length ?? 0) >= 2) {
      const points = guide.points!.map(([normalizedX, normalizedY]) => ([
        x0 + normalizedX * parkW,
        y0 + normalizedY * parkH,
      ] as [number, number]));
      const trace = () => {
        ctx.beginPath();
        ctx.moveTo(points[0][0], points[0][1]);
        for (let index = 1; index < points.length; index += 1) {
          ctx.lineTo(points[index][0], points[index][1]);
        }
        if (guide.closed) ctx.closePath();
      };
      if (mode === 'procedural') {
        trace();
        ctx.strokeStyle = guide.strokeColor ?? '#6e5435';
        ctx.lineWidth = Math.max(3, ((guide.strokeWidthM ?? 2.4) + 0.7) * pxPerM);
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.stroke();
      }
      trace();
      ctx.strokeStyle = guide.color;
      ctx.lineWidth = Math.max(2, (guide.strokeWidthM ?? 2.4) * pxPerM);
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      ctx.stroke();
      continue;
    }

    if (guide.kind === 'axis') {
      const midpoint = (axisMin + axisMax) / 2;
      const halfLength = ((axisMax - axisMin) * guide.width) / 2;
      ctx.beginPath();
      ctx.moveTo(
        centroidX + principalX * (midpoint - halfLength),
        centroidY + principalY * (midpoint - halfLength),
      );
      ctx.lineTo(
        centroidX + principalX * (midpoint + halfLength),
        centroidY + principalY * (midpoint + halfLength),
      );
      ctx.strokeStyle = guide.color;
      ctx.lineWidth = Math.max(2, (guide.strokeWidthM ?? 1.5) * pxPerM);
      ctx.stroke();
      continue;
    }

    if (guide.kind === 'path_loop') {
      if (isBotanicalGarden && mode === 'procedural') {
        const pathWidth = Math.max(2, (guide.strokeWidthM ?? 2.8) * pxPerM);
        ctx.beginPath();
        ctx.ellipse(x, y, width / 2, height / 2, 0, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(91, 76, 55, 0.52)';
        ctx.lineWidth = pathWidth + 0.8 * pxPerM;
        ctx.stroke();
        ctx.beginPath();
        ctx.ellipse(x, y, width / 2, height / 2, 0, 0, Math.PI * 2);
        ctx.strokeStyle = '#d6c7a8';
        ctx.lineWidth = pathWidth;
        ctx.stroke();
        ctx.save();
        ctx.setLineDash([0.34 * pxPerM, 0.52 * pxPerM]);
        ctx.lineDashOffset = 0.17 * pxPerM;
        ctx.beginPath();
        ctx.ellipse(x, y, width / 2, height / 2, 0, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(113, 93, 64, 0.34)';
        ctx.lineWidth = Math.max(0.7, 0.16 * pxPerM);
        ctx.stroke();
        ctx.restore();
        continue;
      }
      ctx.beginPath();
      ctx.ellipse(x, y, width / 2, height / 2, 0, 0, Math.PI * 2);
      ctx.strokeStyle = guide.color;
      ctx.lineWidth = Math.max(2, (guide.strokeWidthM ?? 2) * pxPerM);
      ctx.stroke();
      continue;
    }

    if (guide.kind === 'rectangle') {
      if (isJapaneseGarden) {
        ctx.fillStyle = '#d8cfb5';
        ctx.fillRect(x - width / 2, y - height / 2, width, height);
        ctx.save();
        ctx.beginPath();
        ctx.rect(x - width / 2, y - height / 2, width, height);
        ctx.clip();
        ctx.strokeStyle = 'rgba(116, 105, 80, 0.48)';
        ctx.lineWidth = Math.max(0.65, 0.09 * pxPerM);
        const rakeSpacing = Math.max(2.5, 0.7 * pxPerM);
        for (let rakeY = y - height / 2; rakeY <= y + height / 2; rakeY += rakeSpacing) {
          ctx.beginPath();
          ctx.moveTo(x - width / 2, rakeY);
          ctx.bezierCurveTo(
            x - width / 6,
            rakeY - 0.25 * pxPerM,
            x + width / 6,
            rakeY + 0.25 * pxPerM,
            x + width / 2,
            rakeY,
          );
          ctx.stroke();
        }
        ctx.restore();
        ctx.strokeStyle = guide.strokeColor ?? '#92866a';
        ctx.lineWidth = Math.max(1, (guide.strokeWidthM ?? 0.5) * pxPerM);
        ctx.strokeRect(x - width / 2, y - height / 2, width, height);
        continue;
      }
      if (isBotanicalGarden) {
        const roof = ctx.createLinearGradient(x - width / 2, y, x + width / 2, y);
        roof.addColorStop(0, '#91a39b');
        roof.addColorStop(0.46, '#d7dfd9');
        roof.addColorStop(0.54, '#eef1ec');
        roof.addColorStop(1, '#9aaba4');
        ctx.fillStyle = roof;
        ctx.fillRect(x - width / 2, y - height / 2, width, height);
        ctx.save();
        ctx.beginPath();
        ctx.rect(x - width / 2, y - height / 2, width, height);
        ctx.clip();
        ctx.strokeStyle = 'rgba(77, 93, 87, 0.42)';
        ctx.lineWidth = Math.max(0.7, 0.12 * pxPerM);
        const bay = Math.max(4, 2.4 * pxPerM);
        for (let ribX = x - width / 2; ribX <= x + width / 2; ribX += bay) {
          ctx.beginPath();
          ctx.moveTo(ribX, y - height / 2);
          ctx.lineTo(ribX, y + height / 2);
          ctx.stroke();
        }
        ctx.beginPath();
        ctx.moveTo(x - width / 2, y);
        ctx.lineTo(x + width / 2, y);
        ctx.stroke();
        ctx.restore();
        ctx.strokeStyle = guide.strokeColor ?? '#747f78';
        ctx.lineWidth = Math.max(1, (guide.strokeWidthM ?? 0.7) * pxPerM);
        ctx.strokeRect(x - width / 2, y - height / 2, width, height);
        continue;
      }
      if (isNaturePlay) {
        const rill = ctx.createLinearGradient(x, y - height / 2, x, y + height / 2);
        rill.addColorStop(0, '#466f7c');
        rill.addColorStop(0.5, '#82a9b2');
        rill.addColorStop(1, '#527985');
        ctx.fillStyle = rill;
        ctx.fillRect(x - width / 2, y - height / 2, width, height);
        ctx.strokeStyle = guide.strokeColor ?? '#496b74';
        ctx.strokeRect(x - width / 2, y - height / 2, width, height);
        ctx.beginPath();
        ctx.moveTo(x - width / 2, y);
        ctx.bezierCurveTo(x - width / 5, y - height / 3, x + width / 5, y + height / 3, x + width / 2, y);
        ctx.strokeStyle = 'rgba(226, 240, 236, 0.72)';
        ctx.lineWidth = Math.max(1, 0.18 * pxPerM);
        ctx.stroke();
        continue;
      }
      ctx.fillRect(x - width / 2, y - height / 2, width, height);
      ctx.strokeRect(x - width / 2, y - height / 2, width, height);
      continue;
    }

    if (guide.kind === 'rounded_rectangle') {
      const left = x - width / 2;
      const top = y - height / 2;
      const radius = Math.max(2, Math.min(width, height) * 0.16);
      ctx.beginPath();
      ctx.roundRect(left, top, width, height, radius);
      ctx.fill();
      ctx.stroke();
      continue;
    }

    if (guide.kind === 'soccer_field') {
      const metres = pxPerM;
      const halfW = width / 2;
      const halfH = height / 2;
      const stripeWidth = 8 * metres;
      ctx.save();
      ctx.beginPath();
      ctx.rect(x - halfW, y - halfH, width, height);
      ctx.clip();
      for (let stripeX = x - halfW, stripe = 0; stripeX < x + halfW; stripeX += stripeWidth, stripe += 1) {
        ctx.fillStyle = stripe % 2 === 0 ? '#638f57' : '#59834f';
        ctx.fillRect(stripeX, y - halfH, stripeWidth, height);
      }
      ctx.restore();
      ctx.strokeStyle = guide.strokeColor ?? '#f4f2df';
      ctx.lineWidth = Math.max(1, (guide.strokeWidthM ?? 0.12) * pxPerM);
      ctx.strokeRect(x - halfW, y - halfH, width, height);
      ctx.beginPath();
      ctx.moveTo(x, y - halfH);
      ctx.lineTo(x, y + halfH);
      ctx.moveTo(x + 9.15 * metres, y);
      ctx.arc(x, y, 9.15 * metres, 0, Math.PI * 2);
      ctx.stroke();
      for (const direction of [-1, 1]) {
        const goalX = x + direction * halfW;
        const penaltyX = goalX - direction * 16.5 * metres;
        const goalAreaX = goalX - direction * 5.5 * metres;
        ctx.strokeRect(
          Math.min(goalX, penaltyX),
          y - 20.16 * metres,
          16.5 * metres,
          40.32 * metres,
        );
        ctx.strokeRect(
          Math.min(goalX, goalAreaX),
          y - 9.16 * metres,
          5.5 * metres,
          18.32 * metres,
        );
      }
      continue;
    }

    if (guide.kind === 'tennis_court') {
      const playingW = 23.77 * pxPerM;
      const doublesH = 10.97 * pxPerM;
      const singlesH = 8.23 * pxPerM;
      const serviceOffset = 6.40 * pxPerM;
      ctx.fillStyle = '#416a58';
      ctx.fillRect(x - width / 2, y - height / 2, width, height);
      ctx.fillStyle = guide.color;
      ctx.fillRect(x - playingW / 2, y - doublesH / 2, playingW, doublesH);
      ctx.strokeStyle = guide.strokeColor ?? '#f4f2df';
      ctx.lineWidth = Math.max(1, (guide.strokeWidthM ?? 0.08) * pxPerM);
      ctx.strokeRect(x - playingW / 2, y - doublesH / 2, playingW, doublesH);
      ctx.beginPath();
      ctx.moveTo(x, y - doublesH / 2);
      ctx.lineTo(x, y + doublesH / 2);
      for (const offset of [-serviceOffset, serviceOffset]) {
        ctx.moveTo(x + offset, y - singlesH / 2);
        ctx.lineTo(x + offset, y + singlesH / 2);
      }
      ctx.moveTo(x - playingW / 2, y - singlesH / 2);
      ctx.lineTo(x + playingW / 2, y - singlesH / 2);
      ctx.moveTo(x - playingW / 2, y + singlesH / 2);
      ctx.lineTo(x + playingW / 2, y + singlesH / 2);
      ctx.moveTo(x - serviceOffset, y);
      ctx.lineTo(x + serviceOffset, y);
      ctx.stroke();
      continue;
    }

    if (isJapaneseGarden && guide.kind === 'ellipse') {
      ctx.save();
      ctx.beginPath();
      ctx.ellipse(x, y, width / 2, height / 2, 0, 0, Math.PI * 2);
      ctx.clip();
      const water = ctx.createRadialGradient(
        x - width * 0.12,
        y - height * 0.16,
        width * 0.04,
        x,
        y,
        width * 0.55,
      );
      water.addColorStop(0, '#527f83');
      water.addColorStop(0.48, '#315f69');
      water.addColorStop(1, '#173e49');
      ctx.fillStyle = water;
      ctx.fillRect(x - width / 2, y - height / 2, width, height);
      ctx.strokeStyle = 'rgba(180, 204, 197, 0.34)';
      ctx.lineWidth = Math.max(0.7, 0.08 * pxPerM);
      for (const offset of [-0.23, -0.06, 0.14, 0.31]) {
        ctx.beginPath();
        ctx.ellipse(
          x + width * offset * 0.25,
          y + height * offset,
          width * (0.12 + Math.abs(offset) * 0.16),
          height * 0.045,
          0,
          0,
          Math.PI * 2,
        );
        ctx.stroke();
      }
      ctx.restore();
      ctx.beginPath();
      ctx.ellipse(x, y, width / 2, height / 2, 0, 0, Math.PI * 2);
      ctx.strokeStyle = guide.strokeColor ?? '#263f45';
      ctx.lineWidth = Math.max(1, (guide.strokeWidthM ?? 0.7) * pxPerM);
      ctx.stroke();
      continue;
    }

    if (isBotanicalGarden && guide.kind === 'ellipse' && mode === 'procedural') {
      const bedSeed = `${archetypeId}:${Math.round(x)}:${Math.round(y)}`;
      const palettes = guide.color === '#a66d83'
        ? ['#5e2f48', '#874962', '#c17491', '#df9bb0', '#ece0b1', '#355a38']
        : guide.color === '#a89857'
          ? ['#6d5b24', '#a98b2e', '#d0ad3c', '#e2ca69', '#5f7733', '#8c6930']
          : ['#294d34', '#486b42', '#6d8c58', '#93a879', '#c5c9a0', '#6b5776'];
      ctx.save();
      ctx.beginPath();
      ctx.ellipse(x, y, width / 2, height / 2, 0, 0, Math.PI * 2);
      ctx.clip();
      ctx.fillStyle = '#332b22';
      ctx.fillRect(x - width / 2, y - height / 2, width, height);
      const clusterCount = Math.max(54, Math.round((width * height) / Math.max(1, pxPerM * pxPerM) * 0.34));
      for (let index = 0; index < clusterCount; index += 1) {
        const angle = index * 2.399963 + seededUnit(bedSeed, index * 5) * 0.34;
        const radius = Math.sqrt((index + 0.5) / clusterCount) * 0.86;
        const clusterX = x + Math.cos(angle) * width * 0.48 * radius;
        const clusterY = y + Math.sin(angle) * height * 0.48 * radius;
        const clusterRadius = (0.28 + seededUnit(bedSeed, index * 5 + 1) * 0.78) * pxPerM;
        ctx.beginPath();
        ctx.ellipse(
          clusterX,
          clusterY,
          clusterRadius,
          clusterRadius * (0.62 + seededUnit(bedSeed, index * 5 + 2) * 0.58),
          seededUnit(bedSeed, index * 5 + 3) * Math.PI,
          0,
          Math.PI * 2,
        );
        ctx.fillStyle = palettes[index % palettes.length];
        ctx.fill();
        if (index % 3 === 0) {
          ctx.beginPath();
          ctx.arc(clusterX, clusterY, Math.max(0.55, clusterRadius * 0.22), 0, Math.PI * 2);
          ctx.fillStyle = 'rgba(239, 230, 193, 0.64)';
          ctx.fill();
        }
      }
      ctx.restore();
      ctx.beginPath();
      ctx.ellipse(x, y, width / 2, height / 2, 0, 0, Math.PI * 2);
      ctx.strokeStyle = guide.strokeColor ?? '#536c4c';
      ctx.lineWidth = Math.max(1, (guide.strokeWidthM ?? 0.5) * pxPerM);
      ctx.stroke();
      continue;
    }

    ctx.beginPath();
    ctx.ellipse(x, y, width / 2, height / 2, 0, 0, Math.PI * 2);
    ctx.fill();
    if (mode === 'procedural' && guide.kind === 'ellipse') {
      // Give generic landscape rooms fine-grained planting/turf variation.
      // Solid coloured discs and fully opaque outlines read as a diagram from
      // the Omni camera even when their geometry is correct.
      const guideSeed = `${archetypeId}:${Math.round(x)}:${Math.round(y)}:${Math.round(width)}:${Math.round(height)}`;
      ctx.save();
      ctx.beginPath();
      ctx.ellipse(x, y, width / 2, height / 2, 0, 0, Math.PI * 2);
      ctx.clip();
      const patchCount = Math.max(18, Math.round((width * height) / Math.max(1, pxPerM * pxPerM) * 0.035));
      for (let index = 0; index < patchCount; index += 1) {
        const angle = seededUnit(guideSeed, index * 5) * Math.PI * 2;
        const radius = Math.sqrt(seededUnit(guideSeed, index * 5 + 1));
        const patchX = x + Math.cos(angle) * width * 0.44 * radius;
        const patchY = y + Math.sin(angle) * height * 0.44 * radius;
        const patchRadius = (0.3 + seededUnit(guideSeed, index * 5 + 2) * 1.35) * pxPerM;
        ctx.beginPath();
        ctx.ellipse(
          patchX,
          patchY,
          patchRadius,
          patchRadius * (0.55 + seededUnit(guideSeed, index * 5 + 3) * 0.75),
          seededUnit(guideSeed, index * 5 + 4) * Math.PI,
          0,
          Math.PI * 2,
        );
        ctx.fillStyle = index % 4 === 0
          ? 'rgba(226, 220, 174, 0.10)'
          : index % 3 === 0
            ? 'rgba(38, 65, 35, 0.13)'
            : 'rgba(105, 123, 73, 0.09)';
        ctx.fill();
      }
      ctx.restore();
    }
    if (isBotanicalGarden && guide.kind === 'ellipse') {
      ctx.save();
      ctx.clip();
      const rowSpacing = Math.max(3, 1.8 * pxPerM);
      for (let rowY = y - height / 2; rowY <= y + height / 2; rowY += rowSpacing) {
        const rowIndex = Math.round((rowY - (y - height / 2)) / rowSpacing);
        ctx.beginPath();
        ctx.moveTo(x - width / 2, rowY);
        ctx.bezierCurveTo(
          x - width / 5,
          rowY + (rowIndex % 2 === 0 ? 0.8 : -0.8) * pxPerM,
          x + width / 5,
          rowY + (rowIndex % 2 === 0 ? -0.8 : 0.8) * pxPerM,
          x + width / 2,
          rowY,
        );
        ctx.strokeStyle = rowIndex % 3 === 0
          ? 'rgba(238, 218, 166, 0.72)'
          : rowIndex % 3 === 1
            ? 'rgba(87, 114, 61, 0.74)'
            : 'rgba(238, 187, 201, 0.58)';
        ctx.lineWidth = Math.max(1, 0.7 * pxPerM);
        ctx.stroke();
      }
      ctx.restore();
    }
    if (isNaturePlay && guide.kind === 'ellipse') {
      ctx.save();
      ctx.clip();
      const safetyPalette = ['rgba(101, 78, 50, 0.38)', 'rgba(236, 211, 157, 0.40)', 'rgba(126, 98, 60, 0.28)'];
      for (let index = 0; index < 28; index += 1) {
        const angle = index * 2.399963;
        const radius = Math.sqrt((index + 0.5) / 28);
        const px = x + Math.cos(angle) * width * 0.43 * radius;
        const py = y + Math.sin(angle) * height * 0.43 * radius;
        ctx.beginPath();
        ctx.arc(px, py, (0.25 + (index % 4) * 0.09) * pxPerM, 0, Math.PI * 2);
        ctx.fillStyle = safetyPalette[index % safetyPalette.length];
        ctx.fill();
      }
      ctx.restore();
    }
    ctx.strokeStyle = guide.strokeColor ?? guide.color;
    ctx.lineWidth = Math.max(1, (guide.strokeWidthM ?? 0.4) * pxPerM);
    ctx.globalAlpha = mode === 'procedural' ? 0.58 : 1;
    ctx.stroke();
    ctx.globalAlpha = 1;
    if (guide.kind === 'track') {
      ctx.beginPath();
      ctx.ellipse(x, y, width * 0.37, height * 0.31, 0, 0, Math.PI * 2);
      ctx.fillStyle = '#5f8c54';
      ctx.fill();
      ctx.strokeStyle = '#f4f2df';
      ctx.stroke();
    }
    } finally {
      ctx.restore();
    }
  }
  ctx.restore();
}

function traceRing(
  ctx: CanvasRenderingContext2D,
  ring: Array<[number, number]>,
): void {
  ctx.beginPath();
  ring.forEach(([x, y], index) => {
    if (index === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.closePath();
}

function seededUnit(seed: string, index: number): number {
  let hash = 2_166_136_261;
  const value = `${seed}:${index}`;
  for (let i = 0; i < value.length; i += 1) {
    hash ^= value.charCodeAt(i);
    hash = Math.imul(hash, 16_777_619);
  }
  return (hash >>> 0) / 4_294_967_295;
}

/** Add restrained aerial-material variation so the zero-call live fallback
 * reads as terrain, not a planning fill. The variation is deterministic for a
 * zone and contains no standing objects. */
function paintProceduralGroundMaterial(
  ctx: CanvasRenderingContext2D,
  ringPx: Array<[number, number]>,
  canvasSize: number,
  pxPerM: number,
  isPavedPlaza: boolean,
  seed: string,
  archetypeId: string,
  legoAppearance: ParkLegoAppearance | null,
): void {
  ctx.save();
  traceRing(ctx, ringPx);
  ctx.clip();

  if (legoAppearance) {
    const { materialPattern, palette } = legoAppearance;
    ctx.fillStyle = palette.ground;
    ctx.fillRect(0, 0, canvasSize, canvasSize);

    if (materialPattern === 'modern_turf' || materialPattern === 'modern_minimal') {
      const bandPx = Math.max(12, Math.min(32, 4.8 * pxPerM));
      for (let x = 0, band = 0; x < canvasSize; x += bandPx, band += 1) {
        ctx.globalAlpha = band % 2 === 0 ? 0.16 : 0.07;
        ctx.fillStyle = band % 2 === 0 ? palette.lawn : palette.meadow;
        ctx.fillRect(x, 0, bandPx, canvasSize);
      }
    } else if (materialPattern === 'urban_pavers') {
      ctx.globalAlpha = 0.12;
      ctx.strokeStyle = palette.pathEdge;
      ctx.lineWidth = Math.max(0.6, 0.15 * pxPerM);
      const modulePx = Math.max(7, Math.min(20, 2.4 * pxPerM));
      for (let x = -canvasSize; x < canvasSize * 2; x += modulePx) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x + canvasSize * 0.12, canvasSize);
        ctx.stroke();
      }
    } else {
      const patchCount = Math.round(canvasSize * (
        materialPattern === 'tropical_lush' ? 1.05 : 0.68
      ));
      for (let index = 0; index < patchCount; index += 1) {
        const x = seededUnit(seed, 130_000 + index * 4) * canvasSize;
        const y = seededUnit(seed, 130_001 + index * 4) * canvasSize;
        const rx = (0.65 + seededUnit(seed, 130_002 + index * 4) * 3.5) * pxPerM;
        const ry = rx * (0.45 + seededUnit(seed, 130_003 + index * 4) * 0.8);
        ctx.beginPath();
        ctx.ellipse(x, y, rx, ry, seededUnit(seed, 140_000 + index) * Math.PI, 0, Math.PI * 2);
        ctx.globalAlpha = materialPattern === 'mediterranean_xeriscape' ? 0.24 : 0.18;
        ctx.fillStyle = index % 4 === 0 ? palette.accentSecondary : palette.meadow;
        ctx.fill();
      }
    }
    ctx.globalAlpha = 1;
    ctx.restore();
    return;
  }

  if (archetypeId.startsWith('urban_forest')) {
    ctx.fillStyle = '#43513a';
    ctx.fillRect(0, 0, canvasSize, canvasSize);
    const patches = Math.round(canvasSize * 0.9);
    const palette = [
      'rgba(41, 55, 35, 0.34)',
      'rgba(74, 79, 50, 0.28)',
      'rgba(94, 78, 48, 0.22)',
      'rgba(52, 73, 46, 0.30)',
    ];
    for (let i = 0; i < patches; i += 1) {
      const x = seededUnit(seed, i * 4) * canvasSize;
      const y = seededUnit(seed, i * 4 + 1) * canvasSize;
      const rx = (1.2 + seededUnit(seed, i * 4 + 2) * 5.5) * pxPerM;
      const ry = rx * (0.55 + seededUnit(seed, i * 4 + 3) * 0.9);
      ctx.beginPath();
      ctx.ellipse(x, y, rx, ry, seededUnit(seed, i + 70_000) * Math.PI, 0, Math.PI * 2);
      ctx.fillStyle = palette[i % palette.length];
      ctx.fill();
    }
    ctx.restore();
    return;
  }

  if (archetypeId.startsWith('japanese_garden')) {
    ctx.fillStyle = '#566c4a';
    ctx.fillRect(0, 0, canvasSize, canvasSize);
    const mossPatches = Math.round(canvasSize * 0.45);
    for (let i = 0; i < mossPatches; i += 1) {
      const x = seededUnit(seed, i * 4) * canvasSize;
      const y = seededUnit(seed, i * 4 + 1) * canvasSize;
      const radius = (0.7 + seededUnit(seed, i * 4 + 2) * 3.2) * pxPerM;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fillStyle = i % 3 === 0 ? 'rgba(35, 64, 39, 0.24)' : 'rgba(113, 127, 74, 0.18)';
      ctx.fill();
    }
    ctx.restore();
    return;
  }

  if (archetypeId.startsWith('botanical_garden')) {
    ctx.fillStyle = '#5d7252';
    ctx.fillRect(0, 0, canvasSize, canvasSize);
    const groundPatches = Math.round(canvasSize * 0.58);
    const palette = [
      'rgba(41, 60, 37, 0.22)',
      'rgba(102, 119, 76, 0.24)',
      'rgba(95, 78, 48, 0.17)',
      'rgba(126, 137, 83, 0.18)',
    ];
    for (let i = 0; i < groundPatches; i += 1) {
      const x = seededUnit(seed, i * 4) * canvasSize;
      const y = seededUnit(seed, i * 4 + 1) * canvasSize;
      const rx = (0.8 + seededUnit(seed, i * 4 + 2) * 3.8) * pxPerM;
      const ry = rx * (0.55 + seededUnit(seed, i * 4 + 3) * 0.7);
      ctx.beginPath();
      ctx.ellipse(x, y, rx, ry, seededUnit(seed, i + 80_000) * Math.PI, 0, Math.PI * 2);
      ctx.fillStyle = palette[i % palette.length];
      ctx.fill();
    }
    const lawnBand = Math.max(12, 4.2 * pxPerM);
    for (let x = 0, band = 0; x < canvasSize; x += lawnBand, band += 1) {
      ctx.fillStyle = band % 2 === 0
        ? 'rgba(211, 225, 174, 0.045)'
        : 'rgba(37, 65, 35, 0.035)';
      ctx.fillRect(x, 0, lawnBand, canvasSize);
    }
    const turfFlecks = Math.round(canvasSize * 1.8);
    for (let index = 0; index < turfFlecks; index += 1) {
      const x = seededUnit(seed, 100_000 + index * 3) * canvasSize;
      const y = seededUnit(seed, 100_001 + index * 3) * canvasSize;
      const radius = 0.35 + seededUnit(seed, 100_002 + index * 3) * 1.2;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fillStyle = index % 2 === 0 ? 'rgba(223, 232, 191, 0.15)' : 'rgba(27, 54, 29, 0.13)';
      ctx.fill();
    }
    ctx.restore();
    return;
  }

  if (archetypeId.startsWith('nature_play_area')) {
    ctx.fillStyle = '#687b56';
    ctx.fillRect(0, 0, canvasSize, canvasSize);
    const meadowPatches = Math.round(canvasSize * 0.62);
    for (let i = 0; i < meadowPatches; i += 1) {
      const x = seededUnit(seed, i * 4) * canvasSize;
      const y = seededUnit(seed, i * 4 + 1) * canvasSize;
      const rx = (0.6 + seededUnit(seed, i * 4 + 2) * 3.1) * pxPerM;
      const ry = rx * (0.55 + seededUnit(seed, i * 4 + 3) * 0.8);
      ctx.beginPath();
      ctx.ellipse(x, y, rx, ry, seededUnit(seed, i + 90_000) * Math.PI, 0, Math.PI * 2);
      ctx.fillStyle = i % 3 === 0
        ? 'rgba(177, 158, 94, 0.18)'
        : i % 3 === 1
          ? 'rgba(51, 80, 43, 0.22)'
          : 'rgba(111, 129, 76, 0.20)';
      ctx.fill();
    }
    ctx.restore();
    return;
  }

  if (isPavedPlaza) {
    const modulePx = Math.max(5, Math.min(18, 2.2 * pxPerM));
    ctx.strokeStyle = 'rgba(91, 87, 79, 0.18)';
    ctx.lineWidth = 0.7;
    for (let x = -canvasSize; x < canvasSize * 2; x += modulePx) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x + canvasSize * 0.16, canvasSize);
      ctx.stroke();
    }
    for (let y = 0; y < canvasSize; y += modulePx) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(canvasSize, y);
      ctx.stroke();
    }
  } else {
    const bandPx = Math.max(10, Math.min(30, 4.5 * pxPerM));
    for (let x = 0; x < canvasSize; x += bandPx) {
      ctx.fillStyle = Math.floor(x / bandPx) % 2 === 0
        ? 'rgba(232, 242, 207, 0.055)'
        : 'rgba(45, 74, 38, 0.04)';
      ctx.fillRect(x, 0, bandPx, canvasSize);
    }
    const flecks = Math.round(canvasSize * 1.15);
    for (let i = 0; i < flecks; i += 1) {
      const x = seededUnit(seed, i * 3) * canvasSize;
      const y = seededUnit(seed, i * 3 + 1) * canvasSize;
      const radius = 0.5 + seededUnit(seed, i * 3 + 2) * 2.1;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fillStyle = i % 3 === 0
        ? 'rgba(222, 232, 190, 0.12)'
        : 'rgba(37, 68, 35, 0.08)';
      ctx.fill();
    }
  }
  ctx.restore();
}

function drawProceduralPathNetwork(
  ctx: CanvasRenderingContext2D,
  accessPointsPx: Array<[number, number]>,
  hub: [number, number],
  ringPx: Array<[number, number]>,
  pxPerM: number,
  seed: string,
  isPavedPlaza: boolean,
  plantingStructure: string | undefined,
  legoAppearance: ParkLegoAppearance | null,
): void {
  if (isPavedPlaza || accessPointsPx.length === 0) return;
  ctx.save();
  traceRing(ctx, ringPx);
  ctx.clip();
  // Muted compacted aggregate reads as a real path against Google imagery;
  // near-white diagram lines dominate small parks and look like star symbols
  // at district scale.
  ctx.strokeStyle = legoAppearance?.palette.path ?? '#a99f86';
  ctx.lineWidth = Math.max(1.5, 2.15 * pxPerM);
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';

  const drawBranch = (
    start: [number, number],
    target: [number, number],
    index: number,
  ): void => {
    const [x, y] = start;
    const [targetX, targetY] = target;
    const mx = (x + targetX) / 2;
    const my = (y + targetY) / 2;
    const dx = targetX - x;
    const dy = targetY - y;
    const length = Math.max(1, Math.hypot(dx, dy));
    const bend = (seededUnit(seed, index) - 0.5) * Math.min(8 * pxPerM, length * 0.14);
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.quadraticCurveTo(
      mx + (-dy / length) * bend,
      my + (dx / length) * bend,
      targetX,
      targetY,
    );
    ctx.stroke();
  };

  // Reservoir and stormwater profiles already draw an authoritative shoreline
  // loop. Short gateway spurs terminate beneath that later-painted loop/water
  // guide, avoiding any path across operational water.
  if (plantingStructure === 'reservoir_perimeter' || plantingStructure === 'water_ecology') {
    accessPointsPx.forEach((point, index) => {
      const inward = 0.32 + seededUnit(seed, index + 10_000) * 0.06;
      drawBranch(point, [
        point[0] + (hub[0] - point[0]) * inward,
        point[1] + (hub[1] - point[1]) * inward,
      ], index);
    });
    ctx.restore();
    return;
  }

  if (accessPointsPx.length === 1) {
    drawBranch(accessPointsPx[0], hub, 0);
    ctx.restore();
    return;
  }
  if (accessPointsPx.length === 2) {
    const [a, b] = accessPointsPx;
    const lateral = (seededUnit(seed, 20_000) - 0.5) * 8 * pxPerM;
    ctx.beginPath();
    ctx.moveTo(a[0], a[1]);
    ctx.quadraticCurveTo(hub[0] + lateral, hub[1] - lateral * 0.55, b[0], b[1]);
    ctx.stroke();
    ctx.restore();
    return;
  }

  // Three or more street contacts form one smooth, gateway-derived perimeter
  // walk. Its nodes sit close to the real parcel edge, so four-edge parks read
  // as a rounded irregular loop rather than a radial star or crosshair.
  const innerNodes = accessPointsPx.map((point, index): [number, number] => {
    const inward = 0.10 + seededUnit(seed, index + 30_000) * 0.045;
    const target: [number, number] = [
      point[0] + (hub[0] - point[0]) * inward,
      point[1] + (hub[1] - point[1]) * inward,
    ];
    drawBranch(point, target, index);
    return target;
  }).sort((a, b) => (
    Math.atan2(a[1] - hub[1], a[0] - hub[0])
    - Math.atan2(b[1] - hub[1], b[0] - hub[0])
  ));

  ctx.beginPath();
  const last = innerNodes[innerNodes.length - 1];
  const first = innerNodes[0];
  ctx.moveTo((last[0] + first[0]) / 2, (last[1] + first[1]) / 2);
  for (let i = 0; i < innerNodes.length; i += 1) {
    const node = innerNodes[i];
    const next = innerNodes[(i + 1) % innerNodes.length];
    ctx.quadraticCurveTo(
      node[0],
      node[1],
      (node[0] + next[0]) / 2,
      (node[1] + next[1]) / 2,
    );
  }
  ctx.closePath();
  ctx.stroke();
  ctx.restore();
}

function styleExecutableParkGuides(
  guides: ParkGroundGuide[],
  appearance: ParkLegoAppearance | null,
): ParkGroundGuide[] {
  if (!appearance) return guides;
  const palette = appearance.palette;
  if (appearance.familyId === 'park_pocket_courtyard') {
    return guides.map((guide, index) => index === 0
      ? { ...guide, color: palette.lawn, strokeColor: palette.pathEdge }
      : guide);
  }
  return guides.map((guide, index) => {
    if (index === 0) return { ...guide, color: palette.lawn, strokeColor: palette.pathEdge };
    if (index >= 1 && index <= 4) {
      return { ...guide, color: palette.path, strokeColor: palette.pathEdge };
    }
    if (index === 5) return { ...guide, color: palette.meadow, strokeColor: palette.pathEdge };
    if (index === 6) return { ...guide, color: palette.ground, strokeColor: palette.pathEdge };
    if (index === 7) return { ...guide, color: palette.playSurface, strokeColor: palette.pathEdge };
    if (index === 8) return { ...guide, color: palette.pavilionPad, strokeColor: palette.pathEdge };
    return guide;
  });
}

/** Draw the zone polygon to scale, letterboxed in a square canvas. */
export function buildParkDiagram(
  zone: SiteZone,
  mode: ParkDiagramMode = 'conditioning',
): ParkDiagram | null {
  const ring = zone.coordinates;
  if (!Array.isArray(ring) || ring.length < 3) return null;
  const lngs = ring.map((c) => c[0]);
  const lats = ring.map((c) => c[1]);
  const bbox: ParkGroundBBox = {
    west: Math.min(...lngs),
    south: Math.min(...lats),
    east: Math.max(...lngs),
    north: Math.max(...lats),
  };
  const mPerDegLon = metersPerDegLon((bbox.south + bbox.north) / 2);
  const widthM = (bbox.east - bbox.west) * mPerDegLon;
  const heightM = (bbox.north - bbox.south) * METERS_PER_DEG_LAT;
  if (widthM <= 0 || heightM <= 0) return null;

  const canvasSize = mode === 'procedural' ? PROCEDURAL_CANVAS : CANVAS;
  const pxPerM = (canvasSize * FIT) / Math.max(widthM, heightM);
  const parkW = widthM * pxPerM;
  const parkH = heightM * pxPerM;
  const x0 = (canvasSize - parkW) / 2;
  const y0 = (canvasSize - parkH) / 2;

  const canvas = document.createElement('canvas');
  canvas.width = canvasSize;
  canvas.height = canvasSize;
  const ctx = canvas.getContext('2d');
  if (!ctx) return null;
  const profile = resolveParkGroundProfile(zone);
  const legoAppearance = resolveParkLegoAppearance(zone);
  const guideFit = resolveParkGroundGuideFit(zone, { width: widthM, height: heightM });
  const fitInstruction = describeParkGroundGuideFit(guideFit);
  const plantingStructure = resolveParkPlantingStructure(zone);
  const isPavedPlaza = plantingStructure === 'paved_plaza';
  const parcelBaseColor = legoAppearance?.palette.ground ?? (isPavedPlaza
    ? '#aaa69d'
    : plantingStructure === 'reservoir_perimeter'
      ? '#66775b'
      : plantingStructure === 'water_ecology'
        ? '#6f7857'
      : '#71865f');
  // The source diagram is also an image-generation conditioning input. A
  // white letterbox taught Gemini to preserve blank illustration paper, which
  // then appeared as bright seams in the live terrain drape. Continue the
  // parcel's base ground colour to every image edge instead.
  ctx.fillStyle = parcelBaseColor;
  ctx.fillRect(0, 0, canvasSize, canvasSize);
  ctx.beginPath();
  ring.forEach(([lng, lat], i) => {
    const x = x0 + (lng - bbox.west) * mPerDegLon * pxPerM;
    const y = y0 + (bbox.north - lat) * METERS_PER_DEG_LAT * pxPerM; // north up
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.closePath();
  ctx.fillStyle = parcelBaseColor;
  ctx.fill();
  ctx.strokeStyle = mode === 'procedural' ? parcelBaseColor : '#333333';
  ctx.lineWidth = mode === 'procedural' ? 1 : 4;
  ctx.stroke();

  // ── Furniture markers ──────────────────────────────────────────────────
  // Draw the same deterministic program anchors used by the park kit.
  // (identical computeParkPlacements call — seeded by zone.id), so the AI
  // ground program and later render agree. Trees and benches are deliberately
  // NOT drawn: their locations are designed only after the exact path, water
  // and fixed-program layout is complete. Markers are fixed PADS/anchors
  // (playground surface, pavilion pad, plaza disc) on which real programmed
  // structures may stand; the texture never paints standing objects itself.
  // Shared zone-level resolution — same call as GlobeParkKitLayer.
  const recipe = resolveParkRecipeForZone({
    properties: zone.properties,
    coordinates: ring,
    zone_type: zone.zone_type,
  });
  const placements = computeParkPlacements(
    { id: zone.id, coordinates: ring },
    recipe,
    plantingStructure,
    resolveParkProgramAnchorLayout(zone),
  );
  const fixedProgramPlacements = placements.filter(
    placement => !shouldDeferParkFinishingProp(zone, placement.propId),
  );

  const toPx = (lng: number, lat: number): [number, number] => [
    x0 + (lng - bbox.west) * mPerDegLon * pxPerM,
    y0 + (bbox.north - lat) * METERS_PER_DEG_LAT * pxPerM,
  ];
  const ringPx = ring.map(([lng, lat]) => toPx(lng, lat)) as Array<[number, number]>;
  const centroidPx = ringPx
    .reduce(([ax, ay], [x, y]) => [ax + x, ay + y], [0, 0])
    .map((v) => v / ringPx.length) as [number, number];
  const accessPointsPx = parkAccessPoints(zone).map(([lng, lat]) => toPx(lng, lat));

  if (mode === 'procedural') {
    paintProceduralGroundMaterial(
      ctx,
      ringPx,
      canvasSize,
      pxPerM,
      isPavedPlaza,
      parkGroundSourceSignature(zone),
      profile.archetypeId,
      legoAppearance,
    );
    drawProceduralPathNetwork(
      ctx,
      accessPointsPx,
      centroidPx,
      ringPx,
      pxPerM,
      parkGroundSourceSignature(zone),
      isPavedPlaza,
      plantingStructure,
      legoAppearance,
    );
  }
  drawParkGuides(
    ctx,
    mode === 'procedural'
      ? styleExecutableParkGuides(guideFit.guides, legoAppearance)
      : guideFit.guides,
    ringPx,
    x0,
    y0,
    parkW,
    parkH,
    pxPerM,
    mode,
    profile.archetypeId,
  );

  const playgrounds = fixedProgramPlacements.filter((p) => p.propId === 'playground');
  const pavilions = fixedProgramPlacements.filter((p) => p.propId === 'pavilion');
  const markers = { playground: 0, pavilion: 0, bench: 0, plaza: 0, access: 0 };

  // Exact pedestrian gateways computed from the master planner's street/path
  // graph. The AI must route its internal circulation to these coordinates so
  // the park does not become an attractive but disconnected island.
  for (const [x, y] of accessPointsPx) {
    if (mode === 'conditioning') {
      ctx.beginPath();
      ctx.arc(x, y, Math.max(4, 2.4 * pxPerM), 0, Math.PI * 2);
      ctx.fillStyle = MARKER_COLORS.access;
      ctx.fill();
      ctx.strokeStyle = '#625b4f';
      ctx.lineWidth = Math.max(1, 0.35 * pxPerM);
      ctx.stroke();
    }
    markers.access += 1;
  }

  // Plaza disc at the polygon centroid — the paved anchor the paths converge
  // on. Skipped when a playground cluster sits there (the cluster centers on
  // the same centroid) or the centroid falls outside a concave parcel.
  if (
    profile.includeCentralPlaza
    && playgrounds.length === 0
    && ringContains(centroidPx[0], centroidPx[1], ringPx)
  ) {
    ctx.beginPath();
    ctx.arc(
      centroidPx[0],
      centroidPx[1],
      (mode === 'procedural' ? 5 : 7) * pxPerM,
      0,
      Math.PI * 2,
    );
    ctx.fillStyle = mode === 'procedural' ? '#918b7d' : MARKER_COLORS.plaza;
    ctx.fill();
    markers.plaza = 1;
  }

  // Playground: one sand pad covering the equipment cluster.
  if (playgrounds.length > 0) {
    const pts = playgrounds.map((p) => toPx(p.lng, p.lat));
    const cx = pts.reduce((s, [x]) => s + x, 0) / pts.length;
    const cy = pts.reduce((s, [, y]) => s + y, 0) / pts.length;
    const spreadPx = Math.max(...pts.map(([x, y]) => Math.hypot(x - cx, y - cy)), 0);
    const padR = Math.max(6 * pxPerM, spreadPx + 4 * pxPerM);
    ctx.beginPath();
    ctx.arc(cx, cy, padR, 0, Math.PI * 2);
    ctx.fillStyle = mode === 'procedural'
      ? legoAppearance?.palette.playSurface ?? MARKER_COLORS.playground
      : MARKER_COLORS.playground;
    ctx.fill();
    markers.playground = playgrounds.length;
  }

  // Pavilion: brown pad square, ~5 m.
  for (const p of pavilions) {
    const [x, y] = toPx(p.lng, p.lat);
    const half = 2.5 * pxPerM;
    ctx.fillStyle = mode === 'procedural'
      ? legoAppearance?.palette.pavilionPad ?? MARKER_COLORS.pavilion
      : MARKER_COLORS.pavilion;
    ctx.fillRect(x - half, y - half, half * 2, half * 2);
    markers.pavilion += 1;
  }

  if (mode === 'procedural') {
    // Context grade the deterministic surface toward the warm, moderately
    // desaturated aerial palette of the surrounding Google Tiles. Archetype
    // geometry and material hierarchy remain intact; only the board-like
    // saturation is restrained for the shared 3D/Omni source scene.
    ctx.save();
    traceRing(ctx, ringPx);
    ctx.clip();
    ctx.globalCompositeOperation = 'saturation';
    ctx.globalAlpha = 0.12;
    ctx.fillStyle = '#7e7e7e';
    ctx.fillRect(0, 0, canvasSize, canvasSize);
    ctx.globalCompositeOperation = 'soft-light';
    ctx.globalAlpha = 0.06;
    ctx.fillStyle = '#a28f70';
    ctx.fillRect(0, 0, canvasSize, canvasSize);
    ctx.restore();
  }

  return {
    canvas,
    dataUrl: canvas.toDataURL('image/png'),
    bbox,
    uvRect: {
      u0: x0 / canvasSize,
      v0: (canvasSize - (y0 + parkH)) / canvasSize,
      u1: (x0 + parkW) / canvasSize,
      v1: (canvasSize - y0) / canvasSize,
    },
    sizeM: { width: widthM, height: heightM },
    markers,
    guides: guideFit.guides,
    fitInstruction,
  };
}

/** Prompt evolved from the validated A/B pilot (scripts/_pilot_park_ortho_ab.py):
 * the diagram carries PROGRAM MARKERS at stable dry-land anchors, and the
 * ground and final render prompts both preserve that spatial intent.
 * Critical constraints stay at the END (Gemini weights later instructions). */
export function buildParkGroundPrompt(
  zone: SiteZone,
  sizeM: { width: number; height: number },
  markers: ParkDiagram['markers'],
  hasAppearanceReference = false,
  surroundingContextPrompt = '',
): string {
  const profile = resolveParkGroundProfile(zone);
  const guideFit = resolveParkGroundGuideFit(zone, sizeM);
  const fitInstruction = describeParkGroundGuideFit(guideFit);
  const isPavedPlaza = resolveParkPlantingStructure(zone) === 'paved_plaza';
  const markerLines: string[] = [];
  if (markers.playground > 0) {
    markerLines.push(
      'the SAND-TAN disc is the playground surface - render it as a sand / engineered-wood-fiber '
      + 'safety pad with a thin concrete edge (the play equipment itself is added later in 3D)',
    );
  }
  if (markers.pavilion > 0) {
    markerLines.push(
      'the BROWN square is a picnic pavilion pad - render it as a plain concrete pad '
      + '(the roof structure is added later in 3D)',
    );
  }
  if (markers.plaza > 0) {
    markerLines.push('the LIGHT-GREY disc is a small circular paved plaza with decorative paving');
  }
  const markerBlock = markerLines.length
    ? 'The diagram also marks the park\'s FIXED PROGRAM ANCHORS: '
      + `${markerLines.join('; ')}. Route the walking paths so they connect these marked features. `
    : profile.includeCentralPlaza
      ? 'Include a small circular paved plaza where the paths meet. '
      : '';
  const accessCount = markers.access ?? 0;
  const accessBlock = accessCount > 0
    ? `The ${accessCount} PALE-CREAM circle${accessCount === 1 ? '' : 's'} on the parcel edge mark exact pedestrian gateways into the surrounding street/path network. Extend a continuous path centerline to every gateway, absorb each circle into the path material, and do not leave isolated circular pads. `
    : profile.guideLegend.length > 0
      ? 'The diagram already contains the complete path topology. Do not add any new path, spur, axis, ring, radial connection, plaza or entrance beyond the colored path guides. '
      : 'Provide a connected internal path network with legible entrances at the parcel edge. ';
  const guideBlock = profile.guideLegend.length > 0
    ? `The colored program guides are authoritative: ${profile.guideLegend.join('; ')}. `
    : '';
  const appearanceBlock = hasAppearanceReference
    ? 'A saved photoreal current-view render is attached as the APPEARANCE TARGET. Match its water colour and reflectivity, planting density and palette, paving or timber character, edge transitions and overall landscape maturity. Transpose those appearance qualities into this exact north-up orthophoto; do not copy the render camera, perspective, shadows, surrounding buildings, vehicles or objects. If the appearance target conflicts with the tracing diagram, the diagram always wins for boundary, scale, count and topology. '
    : '';

  return (
    `The attached image is a to-scale site-plan DIAGRAM of ${profile.title}. `
    + `The ${isPavedPlaza ? 'warm-grey polygon is the plaza parcel' : 'green polygon is the park parcel'}, about ${Math.round(sizeM.width)} m wide (east-west) by `
    + `${Math.round(sizeM.height)} m tall (north-south); north is up. `
    + guideBlock
    + accessBlock
    + markerBlock
    + appearanceBlock
    + (surroundingContextPrompt ? `${surroundingContextPrompt}\n` : '')
    + "Render this as a photorealistic straight-down TOP-DOWN AERIAL (nadir) orthophoto of the park's "
    + `GROUND PLANE in summer, in the style of high-resolution aerial imagery. PROGRAM: ${profile.programDescription} `
    + `GROUND MATERIALS: ${profile.groundDescription} `
    + 'GROUND-PLANE QUALITY: make the circulation topology and programmed landscape rooms immediately legible from above. Use nuanced, regionally believable variation within lawns, meadow, low planting and paving; keep edges crisp enough to read at district scale without looking diagrammatic. Never return one uniform green carpet or disconnected ornamental paths. '
    + 'Standing objects are added after this ground pass: playground, pavilion and bridge structures may use live 3D, while mature trees and benches are completed by the final architectural render. '
    + 'Do not paint those objects into the ground texture. Low planting, field markings, water, paving and '
    + 'groundcover must remain visible from directly above. Fill the parcel polygon with the design and '
    + 'continue a neutral version of the dominant ground material beyond '
    + 'the outline to the image edges. The final orthophoto must be fully rendered edge-to-edge: '
    + 'do not preserve the diagram background or return any pure-white, blank, transparent, unpainted '
    + 'or paper-like pixels. Every dry-land pixel must read as a real specified ground material. '
    + 'CRITICAL: keep every marked fixed program anchor EXACTLY at its '
    + 'marked position and size - do not move, resize, add or remove any of them; camera pointing '
    + 'exactly straight down with zero perspective, flat even midday light with no long shadows, no '
    + `tree canopies, no buildings, no vehicles, no people, no text, labels or watermarks. ${profile.criticalConstraints} `
    + (profile.guideLegend.length > 0
      ? `FINAL PIXEL-TO-PIXEL TOPOLOGY LOCK: the input diagram is a tracing template, not design inspiration. Keep the exact silhouettes, centers, dimensions and count of every colored guide: ${profile.guideLegend.join('; ')}. Change only each region's surface appearance. Do not create any additional hardscape, path branch, radial axis, circle, plaza, bed, water feature or structure.`
      : '')
    + (fitInstruction ? ` ${fitInstruction}` : '')
  );
}

/** Create a bounded current-view reference for a park material call. The
 * exact north-up diagram remains Image 1 and controls topology; this frame is
 * attached only so the model can see Google grade, adjacent streets and the
 * proposal buildings that meet the park edge. */
export function capturePublicRealmSceneReference(
  source: HTMLCanvasElement | null,
  maxWidth = 1280,
  quality = 0.82,
): string | null {
  if (!source || source.width <= 0 || source.height <= 0 || typeof document === 'undefined') {
    return null;
  }
  try {
    const scale = Math.min(1, maxWidth / source.width);
    const canvas = document.createElement('canvas');
    canvas.width = Math.max(1, Math.round(source.width * scale));
    canvas.height = Math.max(1, Math.round(source.height * scale));
    const context = canvas.getContext('2d');
    if (!context) return null;
    context.drawImage(source, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg', quality).split(',')[1] || null;
  } catch (error) {
    console.warn('[parkGroundTexture] live globe context capture unavailable', error);
    return null;
  }
}

export function selectLatestParkRenderReference<T extends { id: string; created_at: string }>(
  renders: T[],
): T | null {
  return renders.reduce<T | null>((latest, candidate) => {
    if (!latest) return candidate;
    return Date.parse(candidate.created_at) > Date.parse(latest.created_at) ? candidate : latest;
  }, null);
}

/** Compress the saved photoreal render before using it as a material target.
 * The topology diagram remains the authoritative geometry reference. */
function compressParkAppearanceReference(
  blob: Blob,
  maxWidth = 768,
  quality = 0.82,
): Promise<string> {
  return new Promise((resolve, reject) => {
    const image = new Image();
    const sourceUrl = URL.createObjectURL(blob);
    image.onload = () => {
      const scale = Math.min(1, maxWidth / image.naturalWidth);
      const canvas = document.createElement('canvas');
      canvas.width = Math.round(image.naturalWidth * scale);
      canvas.height = Math.round(image.naturalHeight * scale);
      const context = canvas.getContext('2d');
      if (!context) {
        URL.revokeObjectURL(sourceUrl);
        reject(new Error('Unable to create park appearance canvas'));
        return;
      }
      context.drawImage(image, 0, 0, canvas.width, canvas.height);
      URL.revokeObjectURL(sourceUrl);
      canvas.toBlob((compressed) => {
        if (!compressed) {
          reject(new Error('Park appearance compression failed'));
          return;
        }
        const reader = new FileReader();
        reader.onloadend = () => resolve((reader.result as string).split(',')[1]);
        reader.onerror = () => reject(new Error('Unable to read compressed park appearance'));
        reader.readAsDataURL(compressed);
      }, 'image/jpeg', quality);
    };
    image.onerror = () => {
      URL.revokeObjectURL(sourceUrl);
      reject(new Error('Unable to load park appearance image'));
    };
    image.src = sourceUrl;
  });
}

async function latestParkRenderAppearanceReference(zone: SiteZone): Promise<{
  id: string;
  imageBase64: string;
} | null> {
  if (!zone.project_id) return null;
  try {
    const latest = selectLatestParkRenderReference(await rendersApi.list(zone.project_id));
    if (!latest) return null;
    const { data } = await api.get<Blob>(latest.image_url, {
      responseType: 'blob',
      timeout: PARK_TEXTURE_TIMEOUT_MS,
    });
    return {
      id: latest.id,
      imageBase64: await compressParkAppearanceReference(data),
    };
  } catch (error) {
    console.warn('[parkGroundTexture] saved render appearance reference unavailable', error);
    return null;
  }
}

function base64ToFile(b64: string, filename: string): File {
  const bytes = atob(b64);
  const buf = new Uint8Array(bytes.length);
  for (let i = 0; i < bytes.length; i += 1) buf[i] = bytes.charCodeAt(i);
  return new File([buf], filename, { type: 'image/png' });
}

/**
 * Replace only near-white pixels connected to the image boundary. Image
 * models occasionally retain their input's illustration-paper background
 * despite explicit prompt constraints. Restricting cleanup to an
 * edge-connected component protects pale concrete paths and dam surfaces
 * enclosed by the park design.
 */
export function replaceEdgeConnectedPaperWithTurf(
  data: Uint8ClampedArray,
  width: number,
  height: number,
): number {
  const pixelCount = width * height;
  if (width <= 0 || height <= 0 || data.length < pixelCount * 4) return 0;

  const isPaper = (pixel: number): boolean => {
    const offset = pixel * 4;
    const r = data[offset];
    const g = data[offset + 1];
    const b = data[offset + 2];
    const min = Math.min(r, g, b);
    const max = Math.max(r, g, b);
    return data[offset + 3] > 220 && min >= 225 && max - min <= 28;
  };

  // Derive the replacement palette from existing grass in the generated
  // image, falling back to subdued prairie turf when the image has none.
  const grassR: number[] = [];
  const grassG: number[] = [];
  const grassB: number[] = [];
  const sampleStep = Math.max(1, Math.floor(pixelCount / 8_000));
  for (let pixel = 0; pixel < pixelCount; pixel += sampleStep) {
    const offset = pixel * 4;
    const r = data[offset];
    const g = data[offset + 1];
    const b = data[offset + 2];
    if (r >= 48 && g > r * 1.03 && r > b * 1.12 && g > b * 1.22 && g < 210) {
      grassR.push(r);
      grassG.push(g);
      grassB.push(b);
    }
  }
  const median = (values: number[], fallback: number): number => {
    if (values.length === 0) return fallback;
    values.sort((a, b) => a - b);
    return values[Math.floor(values.length / 2)];
  };
  const baseR = median(grassR, 112);
  const baseG = median(grassG, 132);
  const baseB = median(grassB, 76);

  const marked = new Uint8Array(pixelCount);
  const queue = new Uint32Array(pixelCount);
  let head = 0;
  let tail = 0;
  const enqueue = (pixel: number): void => {
    if (marked[pixel] || !isPaper(pixel)) return;
    marked[pixel] = 1;
    queue[tail] = pixel;
    tail += 1;
  };
  for (let x = 0; x < width; x += 1) {
    enqueue(x);
    enqueue((height - 1) * width + x);
  }
  for (let y = 1; y < height - 1; y += 1) {
    enqueue(y * width);
    enqueue(y * width + width - 1);
  }

  while (head < tail) {
    const pixel = queue[head];
    head += 1;
    const x = pixel % width;
    const y = Math.floor(pixel / width);
    if (x > 0) enqueue(pixel - 1);
    if (x + 1 < width) enqueue(pixel + 1);
    if (y > 0) enqueue(pixel - width);
    if (y + 1 < height) enqueue(pixel + width);
  }

  const clampByte = (value: number): number => Math.max(0, Math.min(255, Math.round(value)));
  for (let pixel = 0; pixel < pixelCount; pixel += 1) {
    if (!marked[pixel]) continue;
    const x = pixel % width;
    const y = Math.floor(pixel / width);
    const hash = (Math.imul(x + 1, 374_761_393) ^ Math.imul(y + 1, 668_265_263)) >>> 0;
    const fine = ((hash & 255) / 255 - 0.5) * 9;
    const broad = 2.6 * Math.sin(x * 0.031) + 1.8 * Math.sin(y * 0.047);
    const mowingBand = Math.floor(x / Math.max(18, Math.round(width / 28))) % 2 === 0 ? -2 : 2;
    const offset = pixel * 4;
    data[offset] = clampByte(baseR + fine * 0.55 + broad + mowingBand);
    data[offset + 1] = clampByte(baseG + fine * 0.7 + broad + mowingBand);
    data[offset + 2] = clampByte(baseB + fine * 0.35 + broad * 0.6);
    data[offset + 3] = 255;
  }
  return tail;
}

/**
 * Generated nadir grounds contain no transparency, so a high-quality JPEG is
 * visually equivalent on the terrain while being far smaller than Gemini's
 * raw PNG (the live QA texture was about 10 MB). Fall back to the source PNG
 * when browser image decoding is unavailable.
 */
async function optimizedParkGroundFile(
  b64: string,
  stem: string,
  removePaperMargins = false,
): Promise<File> {
  const source = base64ToFile(b64, `${stem}.png`);
  if (typeof document === 'undefined' || typeof createImageBitmap !== 'function') return source;
  try {
    const bitmap = await createImageBitmap(source);
    try {
      const canvas = document.createElement('canvas');
      canvas.width = bitmap.width;
      canvas.height = bitmap.height;
      const context = canvas.getContext('2d');
      if (!context) return source;
      context.drawImage(bitmap, 0, 0);
      let cleanedPixels = 0;
      if (removePaperMargins) {
        const pixels = context.getImageData(0, 0, bitmap.width, bitmap.height);
        cleanedPixels = replaceEdgeConnectedPaperWithTurf(
          pixels.data,
          bitmap.width,
          bitmap.height,
        );
        if (cleanedPixels > 0) context.putImageData(pixels, 0, 0);
      }
      const jpeg = await new Promise<Blob | null>((resolve) => (
        canvas.toBlob(resolve, 'image/jpeg', 0.92)
      ));
      if (!jpeg || (cleanedPixels === 0 && jpeg.size >= source.size)) return source;
      return new File([jpeg], `${stem}.jpg`, { type: 'image/jpeg' });
    } finally {
      bitmap.close();
    }
  } catch {
    return source;
  }
}

/**
 * Generate, upload, and persist a ground texture for one green_space zone.
 * Returns the stored meta. Costs one Gemini render call.
 */
export async function generateParkGroundTexture(
  zone: SiteZone,
  options: ParkGroundGenerationOptions = {},
): Promise<ParkGroundTextureMeta> {
  const diagram = buildParkDiagram(zone);
  if (!diagram) throw new Error('Zone has no usable polygon');
  const profile = resolveParkGroundProfile(zone);
  const props = (zone.properties ?? {}) as Record<string, unknown>;
  const legoContract = resolveParkLegoContract(zone);
  const appearanceReference = await latestParkRenderAppearanceReference(zone);
  const siteZones = options.siteZones?.length ? options.siteZones : [zone];
  const surroundingContext = buildPublicRealmGenerationContext(zone, siteZones);
  const surroundingContextPrompt = buildPublicRealmContextPrompt(zone, siteZones, {
    sceneReferenceAttached: Boolean(options.sceneContextImageBase64),
  });
  const archetypeImages = [
    ...(appearanceReference
      ? [{
        image_base64: appearanceReference.imageBase64,
        label: `PHOTOREAL PARK APPEARANCE TARGET for ${profile.title}; transpose materials and landscape maturity into the exact top-down tracing diagram`,
      }]
      : []),
    ...(options.sceneContextImageBase64
      ? [{
        image_base64: options.sceneContextImageBase64,
        label: `LIVE GOOGLE-TILE AND PROPOSAL CONTEXT for ${profile.title}; use only for terrain grade, adjacent road/building relationships, scale, light and edge materials; never copy its camera or override the diagram topology`,
      }]
      : []),
  ];

  const { image_base64 } = await rendersApi.generateEdit({
    image_base64: diagram.dataUrl.split(',')[1],
    // No mask: the proxy only forwards a mask when non-empty; the diagram is
    // the sole conditioning image.
    mask_base64: '',
    prompt: buildParkGroundPrompt(
      zone,
      diagram.sizeM,
      diagram.markers,
      Boolean(appearanceReference),
      surroundingContextPrompt,
    ),
    archetype_images: archetypeImages.length > 0 ? archetypeImages : undefined,
    model: PARK_GROUND_MODEL,
    project_id: zone.project_id,
  });
  if (!image_base64) throw new Error('Render returned no image');

  const textureFile = await optimizedParkGroundFile(
    image_base64,
    `park-ground-${zone.id.slice(0, 8)}`,
    resolveParkPlantingStructure(zone) === 'reservoir_perimeter',
  );
  const doc = await documentsApi.upload(
    zone.project_id,
    textureFile,
    'reference',
  );

  const meta: ParkGroundTextureMeta = {
    url: `/api/v1/documents/${doc.id}/file`,
    document_id: doc.id,
    bbox: diagram.bbox,
    uv_rect: diagram.uvRect,
    size_m: {
      width: Math.round(diagram.sizeM.width * 10) / 10,
      height: Math.round(diagram.sizeM.height * 10) / 10,
    },
    model: PARK_GROUND_MODEL,
    generated_at: new Date().toISOString(),
    source_signature: parkGroundSourceSignature(zone),
    profile_id: profile.id,
    profile_version: profile.version,
    archetype_id: legoContract?.supported
      ? legoContract.archetypeId
      : String(props.green_space_archetype_id ?? profile.archetypeId),
    ...(legoContract?.supported
      ? { variant_id: legoContract.variantId }
      : typeof props.green_space_selected_variant_id === 'string'
        ? { variant_id: props.green_space_selected_variant_id }
      : {}),
    ...(appearanceReference
      ? { appearance_reference_render_id: appearanceReference.id }
      : {}),
    context_version: 1,
    context_neighbor_ids: surroundingContext?.neighbors.map((neighbor) => neighbor.id) ?? [],
    google_tile_context_attached: Boolean(options.sceneContextImageBase64),
  };
  await siteZonesApi.update(zone.id, {
    properties: {
      ...((zone.properties as Record<string, unknown> | undefined) ?? {}),
      park_ground_texture: meta,
    },
  });
  return meta;
}

interface ProceduralParkGroundSurface {
  meta: ParkGroundTextureMeta;
  texture: THREE.Texture;
}

/** Build the immediate, zero-credit surface used by Generate 3D. It shares
 * the same profile, access gateways, pads and UV mapping as the AI drape, so a
 * later Gemini upgrade swaps material fidelity without redesigning geometry. */
function createProceduralParkGroundSurface(zone: SiteZone): ProceduralParkGroundSurface | null {
  const diagram = buildParkDiagram(zone, 'procedural');
  if (!diagram) return null;
  const profile = resolveParkGroundProfile(zone);
  const props = (zone.properties ?? {}) as Record<string, unknown>;
  const legoContract = resolveParkLegoContract(zone);
  const sourceSignature = parkGroundSourceSignature(zone);
  const key = `procedural-park:${sourceSignature}`;
  const texture = new THREE.CanvasTexture(diagram.canvas);
  texture.name = key;
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = 4;
  texture.minFilter = THREE.LinearMipmapLinearFilter;
  texture.magFilter = THREE.LinearFilter;
  texture.needsUpdate = true;

  const selectedVariant = legoContract?.supported
    ? legoContract.variantId
    : props.green_space_selected_variant_id ?? props.plaza_selected_variant_id;
  const selectedArchetype = legoContract?.supported
    ? legoContract.archetypeId
    : props.green_space_archetype_id ?? props.plaza_archetype_id ?? profile.archetypeId;
  return {
    texture,
    meta: {
      url: key,
      document_id: key,
      bbox: diagram.bbox,
      uv_rect: diagram.uvRect,
      size_m: {
        width: Math.round(diagram.sizeM.width * 10) / 10,
        height: Math.round(diagram.sizeM.height * 10) / 10,
      },
      model: 'city-prompt-procedural-ground-v1',
      generated_at: zone.updated_at || zone.created_at || 'deterministic',
      source_signature: sourceSignature,
      profile_id: profile.id,
      profile_version: profile.version,
      archetype_id: String(selectedArchetype),
      ...(typeof selectedVariant === 'string' ? { variant_id: selectedVariant } : {}),
      source: 'procedural',
    },
  };
}

// ── Texture loading (authenticated) ─────────────────────────────────────────
// /api/v1/documents/{id}/file requires the Authorization header, so
// THREE.TextureLoader can't fetch it directly; go through the axios instance
// as a blob and load from an object URL. Cache per document URL.
const textureCache = new Map<string, THREE.Texture>();
const texturePromiseCache = new Map<string, Promise<THREE.Texture>>();

async function fetchParkTextureBlob(url: string): Promise<Blob> {
  let lastError: unknown;
  for (let attempt = 0; attempt < PARK_TEXTURE_FETCH_ATTEMPTS; attempt += 1) {
    try {
      const { data } = await api.get<Blob>(url, {
        responseType: 'blob',
        timeout: PARK_TEXTURE_TIMEOUT_MS,
      });
      return data;
    } catch (error) {
      lastError = error;
    }
  }
  throw lastError;
}

function loadParkGroundTexture(url: string): Promise<THREE.Texture> {
  const cached = textureCache.get(url);
  if (cached) return Promise.resolve(cached);
  const pending = texturePromiseCache.get(url);
  if (pending) return pending;

  const load = (async () => {
    const blob = await fetchParkTextureBlob(url);
    const objectUrl = URL.createObjectURL(blob);
    try {
      const texture = await new THREE.TextureLoader().loadAsync(objectUrl);
      texture.colorSpace = THREE.SRGBColorSpace;
      texture.anisotropy = 8;
      textureCache.set(url, texture);
      return texture;
    } finally {
      URL.revokeObjectURL(objectUrl);
    }
  })();
  texturePromiseCache.set(url, load);
  void load.then(
    () => texturePromiseCache.delete(url),
    () => texturePromiseCache.delete(url),
  );
  return load;
}

export function useParkGroundTexture(zone: SiteZone): {
  meta: ParkGroundTextureMeta | null;
  texture: THREE.Texture | null;
} {
  const persistedMeta = getParkGroundMeta(zone);
  const surfaceSource = resolveParkGroundSurfaceSource(zone);
  const proceduralSignature = surfaceSource === 'procedural'
    ? parkGroundSourceSignature(zone)
    : null;
  const proceduralSurface = useMemo(
    () => (proceduralSignature ? createProceduralParkGroundSurface(zone) : null),
    // The signature covers geometry, archetype, variant and access changes.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [proceduralSignature],
  );
  useEffect(
    () => () => proceduralSurface?.texture.dispose(),
    [proceduralSurface],
  );

  const url = persistedMeta?.url ?? null;
  const [remoteTexture, setRemoteTexture] = useState<THREE.Texture | null>(
    url ? textureCache.get(url) ?? null : null,
  );

  useEffect(() => {
    if (!url) {
      setRemoteTexture(null);
      return undefined;
    }
    const cached = textureCache.get(url);
    if (cached) {
      setRemoteTexture(cached);
      return undefined;
    }
    let cancelled = false;
    loadParkGroundTexture(url)
      .then((loadedTexture) => {
        if (!cancelled) setRemoteTexture(loadedTexture);
      })
      .catch((err) => {
        console.warn('[parkGroundTexture] texture fetch failed', err);
      });
    return () => {
      cancelled = true;
    };
  }, [url]);

  return {
    meta: persistedMeta ?? proceduralSurface?.meta ?? null,
    texture: persistedMeta ? remoteTexture : proceduralSurface?.texture ?? null,
  };
}

/**
 * Write a `uv` attribute mapping each vertex's lng/lat into the texture's UV
 * sub-rect. `fillCoords` is the per-vertex [lng, lat] list emitted by
 * createLocalGeometry in the same order as the position attribute.
 */
export function applyParkGroundUVs(
  geometry: THREE.BufferGeometry,
  fillCoords: number[][],
  meta: Pick<ParkGroundTextureMeta, 'bbox' | 'uv_rect'>,
): void {
  const { bbox, uv_rect: uv } = meta;
  const du = (uv.u1 - uv.u0) / (bbox.east - bbox.west || 1);
  const dv = (uv.v1 - uv.v0) / (bbox.north - bbox.south || 1);
  const uvs = new Float32Array(fillCoords.length * 2);
  fillCoords.forEach(([lng, lat], i) => {
    uvs[i * 2] = uv.u0 + (lng - bbox.west) * du;
    uvs[i * 2 + 1] = uv.v0 + (lat - bbox.south) * dv;
  });
  geometry.setAttribute('uv', new THREE.BufferAttribute(uvs, 2));
}
