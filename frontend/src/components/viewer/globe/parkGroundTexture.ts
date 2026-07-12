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
import { useEffect, useState } from 'react';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import { api, documentsApi, rendersApi, siteZonesApi } from '@/services/api';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { resolveParkRecipe } from '@/data/parkKitRecipes';
import { computeParkPlacements, type PropPlacement } from './parkScatter';

const CANVAS = 1024;
/** Park occupies this fraction of the canvas' limiting dimension. */
const FIT = 0.86;
const PARK_GROUND_MODEL = 'gemini-3.1-flash-image';

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
}

/** Read persisted texture meta off a zone; null unless complete. */
export function getParkGroundMeta(zone: SiteZone): ParkGroundTextureMeta | null {
  if (zone.zone_type !== 'green_space') return null;
  const meta = (zone.properties as Record<string, unknown> | undefined)
    ?.park_ground_texture as ParkGroundTextureMeta | undefined;
  if (!meta || typeof meta.url !== 'string' || !meta.bbox || !meta.uv_rect) return null;
  return meta;
}

interface ParkDiagram {
  dataUrl: string;
  bbox: ParkGroundBBox;
  uvRect: ParkGroundUVRect;
  sizeM: { width: number; height: number };
  /** Which furniture markers were drawn (drives the prompt text). */
  markers: { playground: number; pavilion: number; bench: number; plaza: number };
}

/** Marker palette — must stay in sync with buildParkGroundPrompt's wording. */
const MARKER_COLORS = {
  playground: '#e0c88f', // sand-tan pad
  pavilion: '#8a6b4a',   // brown pad
  bench: '#3a3a3a',      // dark dash
  plaza: '#cfcfc8',      // light-grey disc
} as const;

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

/** Draw the zone polygon to scale, letterboxed in a square canvas. */
export function buildParkDiagram(zone: SiteZone): ParkDiagram | null {
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

  const pxPerM = (CANVAS * FIT) / Math.max(widthM, heightM);
  const parkW = widthM * pxPerM;
  const parkH = heightM * pxPerM;
  const x0 = (CANVAS - parkW) / 2;
  const y0 = (CANVAS - parkH) / 2;

  const canvas = document.createElement('canvas');
  canvas.width = CANVAS;
  canvas.height = CANVAS;
  const ctx = canvas.getContext('2d');
  if (!ctx) return null;
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, CANVAS, CANVAS);
  ctx.beginPath();
  ring.forEach(([lng, lat], i) => {
    const x = x0 + (lng - bbox.west) * mPerDegLon * pxPerM;
    const y = y0 + (bbox.north - lat) * METERS_PER_DEG_LAT * pxPerM; // north up
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.closePath();
  ctx.fillStyle = '#a5c88a';
  ctx.fill();
  ctx.strokeStyle = '#333333';
  ctx.lineWidth = 4;
  ctx.stroke();

  // ── Furniture markers ──────────────────────────────────────────────────
  // Draw the SAME deterministic placements the 3D layer stands its props on
  // (identical computeParkPlacements call — seeded by zone.id), so the AI
  // texture and the scattered GLBs agree. Trees are deliberately NOT drawn:
  // the texture is painted treeless and 3D canopies land on lawn.
  // Markers are PADS/anchors (sand pad, concrete pads, plaza disc) — the 3D
  // furniture stands ON them, so the texture must not paint the furniture
  // itself.
  const props = zone.properties as Record<string, unknown> | undefined;
  const recipe = resolveParkRecipe(String(props?.green_space_archetype_id ?? ''));
  const plantingStructure =
    typeof props?.planting_structure === 'string' ? props.planting_structure : undefined;
  const placements = computeParkPlacements(
    { id: zone.id, coordinates: ring },
    recipe,
    plantingStructure,
  );

  const toPx = (lng: number, lat: number): [number, number] => [
    x0 + (lng - bbox.west) * mPerDegLon * pxPerM,
    y0 + (bbox.north - lat) * METERS_PER_DEG_LAT * pxPerM,
  ];
  const ringPx = ring.map(([lng, lat]) => toPx(lng, lat)) as Array<[number, number]>;

  const playgrounds = placements.filter((p) => p.propId === 'playground');
  const pavilions = placements.filter((p) => p.propId === 'pavilion');
  const benches = placements.filter((p) => p.propId === 'bench');
  const markers = { playground: 0, pavilion: 0, bench: 0, plaza: 0 };

  // Plaza disc at the polygon centroid — the paved anchor the paths converge
  // on. Skipped when a playground cluster sits there (the cluster centers on
  // the same centroid) or the centroid falls outside a concave parcel.
  const centroidPx = ringPx
    .reduce(([ax, ay], [x, y]) => [ax + x, ay + y], [0, 0])
    .map((v) => v / ringPx.length) as [number, number];
  if (playgrounds.length === 0 && ringContains(centroidPx[0], centroidPx[1], ringPx)) {
    ctx.beginPath();
    ctx.arc(centroidPx[0], centroidPx[1], 7 * pxPerM, 0, Math.PI * 2);
    ctx.fillStyle = MARKER_COLORS.plaza;
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
    ctx.fillStyle = MARKER_COLORS.playground;
    ctx.fill();
    markers.playground = playgrounds.length;
  }

  // Pavilion: brown pad square, ~5 m.
  for (const p of pavilions) {
    const [x, y] = toPx(p.lng, p.lat);
    const half = 2.5 * pxPerM;
    ctx.fillStyle = MARKER_COLORS.pavilion;
    ctx.fillRect(x - half, y - half, half * 2, half * 2);
    markers.pavilion += 1;
  }

  // Benches: short dark dashes, long axis along the bench (ENU yaw is CCW
  // from east; canvas y points south, so the canvas rotation is -yaw).
  const drawDash = (p: PropPlacement) => {
    const [x, y] = toPx(p.lng, p.lat);
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(-p.yawRad);
    const halfL = 1.2 * pxPerM;
    const halfW = 0.4 * pxPerM;
    ctx.fillStyle = MARKER_COLORS.bench;
    ctx.fillRect(-halfL, -halfW, halfL * 2, halfW * 2);
    ctx.restore();
  };
  for (const b of benches) {
    drawDash(b);
    markers.bench += 1;
  }

  return {
    dataUrl: canvas.toDataURL('image/png'),
    bbox,
    uvRect: {
      u0: x0 / CANVAS,
      v0: (CANVAS - (y0 + parkH)) / CANVAS,
      u1: (x0 + parkW) / CANVAS,
      v1: (CANVAS - y0) / CANVAS,
    },
    sizeM: { width: widthM, height: heightM },
    markers,
  };
}

/** Prompt evolved from the validated A/B pilot (scripts/_pilot_park_ortho_ab.py):
 * the diagram now carries FURNITURE MARKERS at the exact spots the 3D prop
 * scatter will stand its GLBs, and the prompt anchors the design to them.
 * Critical constraints stay at the END (Gemini weights later instructions). */
function buildParkGroundPrompt(
  sizeM: { width: number; height: number },
  markers: ParkDiagram['markers'],
): string {
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
  if (markers.bench > 0) {
    markerLines.push(
      'each small DARK dash is a park bench spot - render a small rectangular concrete pad there, '
      + 'oriented like the dash (the bench itself is added later in 3D)',
    );
  }
  if (markers.plaza > 0) {
    markerLines.push('the LIGHT-GREY disc is a small circular paved plaza with decorative paving');
  }
  const markerBlock = markerLines.length
    ? 'The diagram also marks the park\'s FIXED FURNITURE locations: '
      + `${markerLines.join('; ')}. Route the walking paths so they connect these marked features. `
    : 'Include a small circular paved plaza where the paths meet. ';

  return (
    'The attached image is a to-scale site-plan DIAGRAM of a neighborhood park. '
    + `The green polygon is the park parcel, about ${Math.round(sizeM.width)} m wide (east-west) by `
    + `${Math.round(sizeM.height)} m tall (north-south); north is up. `
    + markerBlock
    + "Render this as a photorealistic straight-down TOP-DOWN AERIAL (nadir) orthophoto of the park's "
    + 'GROUND PLANE in summer, in the style of high-resolution Google Earth imagery: mowed lawn with '
    + 'natural tone variation and mowing stripes, smooth curving concrete walking paths, low planting '
    + 'beds with shrubs and perennials, and a gravel fitness loop. This is an OPEN TREELESS lawn park '
    + '- all planting is low groundcover and shrubs seen from directly above; tree canopies are added '
    + 'later in 3D. Fill the parcel polygon with the park design and continue plain mowed grass beyond '
    + 'the outline to the image edges. CRITICAL: keep every marked furniture feature EXACTLY at its '
    + 'marked position and size - do not move, resize, add or remove any of them; camera pointing '
    + 'exactly straight down with zero perspective, flat even midday light with no long shadows, no '
    + 'tree canopies, no buildings, no vehicles, no people, no text, labels or watermarks.'
  );
}

function base64ToFile(b64: string, filename: string): File {
  const bytes = atob(b64);
  const buf = new Uint8Array(bytes.length);
  for (let i = 0; i < bytes.length; i += 1) buf[i] = bytes.charCodeAt(i);
  return new File([buf], filename, { type: 'image/png' });
}

/**
 * Generate, upload, and persist a ground texture for one green_space zone.
 * Returns the stored meta. Costs one Gemini render call.
 */
export async function generateParkGroundTexture(zone: SiteZone): Promise<ParkGroundTextureMeta> {
  const diagram = buildParkDiagram(zone);
  if (!diagram) throw new Error('Zone has no usable polygon');

  const { image_base64 } = await rendersApi.generateEdit({
    image_base64: diagram.dataUrl.split(',')[1],
    // No mask: the proxy only forwards a mask when non-empty; the diagram is
    // the sole conditioning image.
    mask_base64: '',
    prompt: buildParkGroundPrompt(diagram.sizeM, diagram.markers),
    model: PARK_GROUND_MODEL,
    project_id: zone.project_id,
  });
  if (!image_base64) throw new Error('Render returned no image');

  const doc = await documentsApi.upload(
    zone.project_id,
    base64ToFile(image_base64, `park-ground-${zone.id.slice(0, 8)}.png`),
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
  };
  await siteZonesApi.update(zone.id, {
    properties: {
      ...((zone.properties as Record<string, unknown> | undefined) ?? {}),
      park_ground_texture: meta,
    },
  });
  return meta;
}

// ── Texture loading (authenticated) ─────────────────────────────────────────
// /api/v1/documents/{id}/file requires the Authorization header, so
// THREE.TextureLoader can't fetch it directly; go through the axios instance
// as a blob and load from an object URL. Cache per document URL.
const textureCache = new Map<string, THREE.Texture>();

export function useParkGroundTexture(zone: SiteZone): {
  meta: ParkGroundTextureMeta | null;
  texture: THREE.Texture | null;
} {
  const meta = getParkGroundMeta(zone);
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
    api
      .get(url, { responseType: 'blob' })
      .then(({ data }) => {
        if (cancelled) return;
        const objectUrl = URL.createObjectURL(data as Blob);
        new THREE.TextureLoader().load(objectUrl, (tex) => {
          URL.revokeObjectURL(objectUrl);
          tex.colorSpace = THREE.SRGBColorSpace;
          tex.anisotropy = 8;
          textureCache.set(url, tex);
          if (!cancelled) setTexture(tex);
        });
      })
      .catch((err) => {
        console.warn('[parkGroundTexture] texture fetch failed', err);
      });
    return () => {
      cancelled = true;
    };
  }, [url]);

  return { meta, texture };
}

/**
 * Write a `uv` attribute mapping each vertex's lng/lat into the texture's UV
 * sub-rect. `fillCoords` is the per-vertex [lng, lat] list emitted by
 * createLocalGeometry in the same order as the position attribute.
 */
export function applyParkGroundUVs(
  geometry: THREE.BufferGeometry,
  fillCoords: number[][],
  meta: ParkGroundTextureMeta,
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
