/**
 * useGlobeAIRender.ts — AI render pipeline for the 3D globe.
 *
 * Captures the R3F canvas screenshot (with photorealistic 3D tiles context),
 * generates masks from zone polygons using Three.js camera projection,
 * builds structured prompts from zone archetypes, and sends to the Gemini API.
 *
 * Supports two render modes:
 * - Single-shot: all zones in one API call (fast, good for <10 zones)
 * - Per-zone sequential: 2-pass rendering (ground first, then each building)
 *   for complex multi-zone sites with higher accuracy
 *
 * Key advantage over Mapbox version: the screenshot includes real 3D buildings
 * from Google Photorealistic Tiles, giving Gemini much better spatial context.
 */

import { useCallback, useRef } from 'react';
import * as THREE from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import type { SiteZone } from '@/types';
import { ZONE_TYPE_CONFIG } from '@/types';
import { api } from '@/services/api';
import { resolveZoneColor } from '../mapEngine/geoUtils';
import archetypeCatalog from '@/data/buildingArchetypes.json';
import openSpaceCatalog from '@/data/openSpaceArchetypes.json';
import streetPathCatalog from '@/data/streetPathArchetypes.json';

const DEG_TO_RAD = Math.PI / 180;
const catalog = [
  ...((archetypeCatalog as any)?.archetypes || []),
  ...((openSpaceCatalog as any)?.archetypes || (openSpaceCatalog as any) || []),
  ...((streetPathCatalog as any)?.archetypes || (streetPathCatalog as any) || []),
] as any[];

const BUILDING_TYPES = ['building', 'residential', 'commercial', 'industrial', 'mixed_use'];
const GROUND_TYPES = ['green_space', 'park', 'road', 'street', 'path', 'plaza', 'parking', 'water', 'development_area'];

export interface GlobeRenderResult {
  imageUrl: string;  // data:image/png;base64,...
  prompt: string;
  seed?: number;
}

/** Prompt entry for structured per-zone prompt generation */
interface ZonePromptEntry {
  color: string;
  zoneType: string;
  zoneName: string;
  descriptionText?: string;
  floors?: number;
  heightM?: number;
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
}

/**
 * Capture the R3F canvas as a base64 PNG string.
 * Requires Canvas gl={{ preserveDrawingBuffer: true }}
 */
function captureCanvasBase64(canvas: HTMLCanvasElement): Promise<string> {
  return new Promise((resolve) => {
    canvas.toBlob((blob) => {
      if (!blob) { resolve(''); return; }
      const reader = new FileReader();
      reader.onloadend = () => {
        const dataUrl = reader.result as string;
        resolve(dataUrl.split(',')[1]); // Raw base64 without prefix
      };
      reader.readAsDataURL(blob);
    }, 'image/png');
  });
}

/**
 * Project a [lng, lat] coordinate to screen pixels using Three.js camera.
 */
function projectToPixels(
  lng: number, lat: number, height: number,
  camera: THREE.Camera, width: number, height_px: number,
): { x: number; y: number } | null {
  const pos = new THREE.Vector3();
  WGS84_ELLIPSOID.getCartographicToPosition(lat * DEG_TO_RAD, lng * DEG_TO_RAD, height, pos);
  pos.project(camera);

  // Behind camera check
  if (pos.z > 1) return null;

  return {
    x: (pos.x + 1) / 2 * width,
    y: (1 - pos.y) / 2 * height_px,
  };
}

// ─── COLOR UTILITIES ───────────────────────────────────────────────────

function hexToHsl(hex: string): [number, number, number] {
  const r = parseInt(hex.slice(1, 3), 16) / 255;
  const g = parseInt(hex.slice(3, 5), 16) / 255;
  const b = parseInt(hex.slice(5, 7), 16) / 255;
  const max = Math.max(r, g, b), min = Math.min(r, g, b);
  const l = (max + min) / 2;
  if (max === min) return [0, 0, l * 100];
  const d = max - min;
  const s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
  let h = 0;
  if (max === r) h = ((g - b) / d + (g < b ? 6 : 0)) / 6;
  else if (max === g) h = ((b - r) / d + 2) / 6;
  else h = ((r - g) / d + 4) / 6;
  return [h * 360, s * 100, l * 100];
}

/**
 * Map hex color to a UNIQUE human-readable name for prompts.
 * Always includes the hex value so Gemini can match the exact shade,
 * even when multiple zones share similar hue names like "red".
 */
function colorName(hex: string): string {
  const normalized = hex.toLowerCase();
  const knownNames: Record<string, string> = {
    '#e03c31': 'red',
    '#ff6b6b': 'coral',
    '#e8927c': 'salmon',
    '#f5a623': 'amber',
    '#ffd700': 'gold',
    '#ffeb3b': 'yellow',
    '#f0e68c': 'khaki',
    '#4caf50': 'green',
    '#66bb6a': 'spring green',
    '#2e7d32': 'forest green',
    '#009688': 'teal',
    '#4169e1': 'royal blue',
    '#3f51b5': 'indigo',
    '#2196f3': 'blue',
    '#9c27b0': 'purple',
    '#795548': 'brown',
    '#607d8b': 'blue grey',
    '#bdbdbd': 'silver',
    '#c62828': 'dark red',
    '#d84315': 'deep orange',
    '#ad1457': 'dark pink',
    '#6a1b9a': 'deep purple',
    '#4527a0': 'deep indigo',
    '#b71c1c': 'crimson',
    '#e65100': 'burnt orange',
  };

  const name = knownNames[normalized];
  if (name) return `${name} ${hex}`;

  try {
    const [h, , l] = hexToHsl(hex);
    const lightness = l < 35 ? 'dark ' : l > 65 ? 'light ' : '';
    let hueName = 'brown';
    if (h < 15 || h >= 345) hueName = 'red';
    else if (h < 45) hueName = 'orange';
    else if (h < 65) hueName = 'amber';
    else if (h < 80) hueName = 'gold';
    else if (h < 150) hueName = 'green';
    else if (h < 210) hueName = 'blue';
    else if (h < 270) hueName = 'indigo';
    else if (h < 330) hueName = 'purple';
    return `${lightness}${hueName} ${hex}`;
  } catch {
    return hex;
  }
}

// ─── PERSPECTIVE HEADROOM ──────────────────────────────────────────────

/**
 * Calculate the upward pixel expansion needed for a building mask
 * to accommodate 3D perspective height. In an oblique aerial view,
 * a tall building's roof shifts "up-screen" relative to its footprint.
 *
 * Globe-specific: derives pitch from the camera and uses projectToPixels()
 * for the pixels-per-meter calculation instead of Mapbox's map.project().
 */
function calculateGlobeHeadroom(
  camera: THREE.Camera,
  lat: number,
  lng: number,
  buildingHeightM: number,
  canvasWidth: number,
  canvasHeight: number,
  terrainHeight: number,
): number {
  if (buildingHeightM <= 0) return 0;

  // Estimate camera pitch from the camera's forward vector vs surface normal
  // (the angle between camera-look-direction and the surface tangent plane)
  const camDir = new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion).normalize();
  const surfacePos = new THREE.Vector3();
  WGS84_ELLIPSOID.getCartographicToPosition(lat * DEG_TO_RAD, lng * DEG_TO_RAD, terrainHeight, surfacePos);
  const surfaceNormal = surfacePos.clone().normalize();
  // Pitch = angle between camera forward and surface tangent plane
  // dot(camDir, -surfaceNormal) gives cos(angle from nadir)
  const cosAngle = Math.abs(camDir.dot(surfaceNormal.clone().negate()));
  const pitchFromNadir = Math.acos(Math.min(1, cosAngle)); // 0 = looking straight down
  const pitchDeg = pitchFromNadir * 180 / Math.PI;

  if (pitchDeg < 5) return 0; // Near top-down, no headroom needed

  // Project two points at ground and at building height to get pixel shift
  const groundPx = projectToPixels(lng, lat, terrainHeight, camera, canvasWidth, canvasHeight);
  const roofPx = projectToPixels(lng, lat, terrainHeight + buildingHeightM, camera, canvasWidth, canvasHeight);

  if (!groundPx || !roofPx) {
    // Fallback: estimate from pitch
    return 80;
  }

  // The vertical pixel distance between ground and roof
  const verticalShift = Math.abs(groundPx.y - roofPx.y);

  // Apply 2.0x safety margin for perspective distortion at edges
  return verticalShift * 2.0;
}

// ─── MASK GENERATION (Phase 1) ─────────────────────────────────────────

/**
 * Generate a COLOR-CODED mask from zone polygons.
 * Each zone drawn in its actual map color so Gemini can match the COLOR-TO-ZONE legend.
 * Black = keep as-is, colored = render this zone.
 */
function generateColorCodedMask(
  zones: SiteZone[],
  camera: THREE.Camera,
  width: number,
  height: number,
  terrainHeight: number,
): string {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d')!;

  // Start with black (preserve everything)
  ctx.fillStyle = '#000000';
  ctx.fillRect(0, 0, width, height);

  // Draw each zone in its ACTUAL color — skip site_boundary
  for (const zone of zones) {
    if (!zone.coordinates || zone.coordinates.length < 3) continue;
    if (zone.zone_type === 'site_boundary') continue;

    const zoneColor = resolveZoneColor(zone);
    ctx.fillStyle = zoneColor;

    const pixels = zone.coordinates
      .map(c => projectToPixels(c[0], c[1], terrainHeight, camera, width, height))
      .filter(Boolean) as { x: number; y: number }[];

    if (pixels.length < 3) continue;

    ctx.beginPath();
    ctx.moveTo(pixels[0].x, pixels[0].y);
    for (let i = 1; i < pixels.length; i++) {
      ctx.lineTo(pixels[i].x, pixels[i].y);
    }
    ctx.closePath();

    // For buildings, expand upward to include building height
    const buildingHeight = (zone.properties?.height_m as number)
      || (zone.properties?.height as number)
      || ((zone.properties?.floors as number) || 0) * 3.2
      || 0;

    if (buildingHeight > 0 && (zone.zone_type === 'building' || zone.zone_type === 'residential')) {
      const topPixels = zone.coordinates
        .map(c => projectToPixels(c[0], c[1], terrainHeight + buildingHeight, camera, width, height))
        .filter(Boolean) as { x: number; y: number }[];

      if (topPixels.length >= 3) {
        for (const p of topPixels) ctx.lineTo(p.x, p.y);
      }
    }

    ctx.fill();
  }

  return canvas.toDataURL('image/png').split(',')[1];
}

/**
 * Collect archetype reference card images for multi-image rendering.
 * Returns up to 6 images with their zone labels.
 */
async function collectArchetypeImages(
  zones: SiteZone[],
): Promise<Array<{ image_base64: string; label: string; zone_color: string }>> {
  const images: Array<{ image_base64: string; label: string; zone_color: string }> = [];

  for (const zone of zones) {
    if (images.length >= 6) break;
    if (zone.zone_type === 'site_boundary') continue;

    const props = zone.properties || {};
    const archetypeId = (props.development_archetype_id as string)
      || (props.green_space_archetype_id as string)
      || (props.road_archetype_id as string)
      || (props.plaza_archetype_id as string)
      || (props.development_subcategory as string)
      || (props.green_space_subcategory as string)
      || '';

    if (!archetypeId) continue;

    const entry = catalog.find((a: any) => a.id === archetypeId || archetypeId.startsWith(a.id + '_'));
    if (!entry?.thumbnailUrl) continue;

    // Fetch the card image
    try {
      const resp = await fetch(entry.thumbnailUrl);
      if (!resp.ok) continue;
      const blob = await resp.blob();
      const base64 = await new Promise<string>((resolve) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve((reader.result as string).split(',')[1]);
        reader.readAsDataURL(blob);
      });

      images.push({
        image_base64: base64,
        label: entry.title || archetypeId,
        zone_color: resolveZoneColor(zone),
      });
    } catch { /* skip failed fetches */ }
  }

  return images;
}

/**
 * Generate a BINARY mask from zone polygons.
 * White (255) = area to edit (inside zone polygons), Black (0) = keep untouched.
 * For building zones, expands upward with feathered edges to accommodate 3D height.
 */
function generateBinaryMask(
  zones: SiteZone[],
  camera: THREE.Camera,
  width: number,
  height: number,
  terrainHeight: number,
): string {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d')!;

  ctx.fillStyle = '#000000';
  ctx.fillRect(0, 0, width, height);
  ctx.fillStyle = '#ffffff';

  const boundaries = zones.filter(z => z.zone_type === 'site_boundary');
  const others = zones.filter(z => z.zone_type !== 'site_boundary');
  let drawnCount = 0;

  for (const zone of [...boundaries, ...others]) {
    if (!zone.coordinates || zone.coordinates.length < 3) continue;

    const pixels = zone.coordinates
      .map(c => projectToPixels(c[0], c[1], terrainHeight, camera, width, height))
      .filter(Boolean) as { x: number; y: number }[];
    if (pixels.length < 3) continue;

    ctx.beginPath();
    ctx.moveTo(pixels[0].x, pixels[0].y);
    for (let i = 1; i < pixels.length; i++) ctx.lineTo(pixels[i].x, pixels[i].y);
    ctx.closePath();
    ctx.fill();

    // For buildings, expand mask upward for 3D height
    if (BUILDING_TYPES.includes(zone.zone_type)) {
      const buildingHeight = (zone.properties?.height_m as number)
        || (zone.properties?.height as number)
        || ((zone.properties?.floors as number) || 0) * 3.2 || 0;
      const centroid = zone.coordinates.reduce(
        (acc, c) => [acc[0] + c[0] / zone.coordinates!.length, acc[1] + c[1] / zone.coordinates!.length],
        [0, 0],
      );
      const headroom = buildingHeight > 0
        ? calculateGlobeHeadroom(camera, centroid[1], centroid[0], buildingHeight, width, height, terrainHeight)
        : 80;

      if (headroom > 0) {
        const minY = Math.min(...pixels.map(p => p.y));
        const minX = Math.min(...pixels.map(p => p.x));
        const maxX = Math.max(...pixels.map(p => p.x));
        const expandedTop = Math.max(0, minY - headroom);
        ctx.fillRect(minX, expandedTop, maxX - minX, minY - expandedTop);

        // Soft feathered edge at the top
        const featherHeight = Math.min(20, headroom * 0.25);
        if (featherHeight > 2) {
          const gradient = ctx.createLinearGradient(0, expandedTop, 0, expandedTop + featherHeight);
          gradient.addColorStop(0, 'rgba(0,0,0,1)');
          gradient.addColorStop(1, 'rgba(0,0,0,0)');
          ctx.globalCompositeOperation = 'destination-out';
          ctx.fillStyle = gradient;
          ctx.fillRect(minX, expandedTop, maxX - minX, featherHeight);
          ctx.globalCompositeOperation = 'source-over';
          ctx.fillStyle = '#ffffff';
        }
      }
    }

    drawnCount++;
  }
  console.log(`[GlobeAIRender] Binary mask: ${drawnCount}/${zones.length} zones on ${width}x${height}`);
  return canvas.toDataURL('image/png').split(',')[1];
}

/**
 * Generate a binary mask for a SINGLE zone polygon.
 * White = the zone's footprint (+ headroom for buildings), Black = everything else.
 */
function generateSingleZoneMask(
  zone: SiteZone,
  camera: THREE.Camera,
  width: number,
  height: number,
  terrainHeight: number,
): string {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d')!;

  ctx.fillStyle = '#000000';
  ctx.fillRect(0, 0, width, height);

  if (!zone.coordinates || zone.coordinates.length < 3) {
    return canvas.toDataURL('image/png').split(',')[1];
  }

  const pixels = zone.coordinates
    .map(c => projectToPixels(c[0], c[1], terrainHeight, camera, width, height))
    .filter(Boolean) as { x: number; y: number }[];
  if (pixels.length < 3) return canvas.toDataURL('image/png').split(',')[1];

  const isBuilding = BUILDING_TYPES.includes(zone.zone_type);
  const buildingHeight = (zone.properties?.height_m as number)
    || (zone.properties?.height as number)
    || ((zone.properties?.floors as number) || 0) * 3.2 || 0;

  ctx.fillStyle = '#ffffff';
  ctx.beginPath();
  ctx.moveTo(pixels[0].x, pixels[0].y);
  for (let i = 1; i < pixels.length; i++) ctx.lineTo(pixels[i].x, pixels[i].y);
  ctx.closePath();
  ctx.fill();

  if (isBuilding && buildingHeight > 0) {
    const centroid = zone.coordinates.reduce(
      (acc, c) => [acc[0] + c[0] / zone.coordinates!.length, acc[1] + c[1] / zone.coordinates!.length],
      [0, 0],
    );
    const headroom = calculateGlobeHeadroom(camera, centroid[1], centroid[0], buildingHeight, width, height, terrainHeight);

    if (headroom > 0) {
      const minY = Math.min(...pixels.map(p => p.y));
      const minX = Math.min(...pixels.map(p => p.x));
      const maxX = Math.max(...pixels.map(p => p.x));
      const expandedTop = Math.max(0, minY - headroom);
      ctx.fillRect(minX, expandedTop, maxX - minX, minY - expandedTop);

      const featherHeight = Math.min(20, headroom * 0.3);
      if (featherHeight > 2) {
        const gradient = ctx.createLinearGradient(0, expandedTop, 0, expandedTop + featherHeight);
        gradient.addColorStop(0, 'rgba(0,0,0,1)');
        gradient.addColorStop(1, 'rgba(0,0,0,0)');
        ctx.globalCompositeOperation = 'destination-out';
        ctx.fillStyle = gradient;
        ctx.fillRect(minX, expandedTop, maxX - minX, featherHeight);
        ctx.globalCompositeOperation = 'source-over';
      }
    }
    console.log(`[GlobeAIRender] Single-zone mask: building headroom ${headroom.toFixed(0)}px for ${buildingHeight}m, zone="${zone.name || zone.zone_type}"`);
  }

  // Debug coverage
  const imgData = ctx.getImageData(0, 0, width, height).data;
  let whiteCount = 0;
  for (let i = 0; i < imgData.length; i += 4) if (imgData[i] > 128) whiteCount++;
  console.log(`[GlobeAIRender] Single-zone mask: white=${whiteCount}/${width * height} (${((whiteCount / (width * height)) * 100).toFixed(1)}%), zone="${zone.name || zone.zone_type}"`);

  return canvas.toDataURL('image/png').split(',')[1];
}

/**
 * Generate a combined binary mask for MULTIPLE zones.
 * White = union of all provided zone polygons, Black = keep.
 * Used in Pass 1 to mask all ground-level zones at once.
 */
function generateCombinedMask(
  zones: SiteZone[],
  camera: THREE.Camera,
  width: number,
  height: number,
  terrainHeight: number,
): string {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d')!;

  ctx.fillStyle = '#000000';
  ctx.fillRect(0, 0, width, height);
  ctx.fillStyle = '#ffffff';

  let drawnCount = 0;
  for (const zone of zones) {
    if (!zone.coordinates || zone.coordinates.length < 3) continue;
    const pixels = zone.coordinates
      .map(c => projectToPixels(c[0], c[1], terrainHeight, camera, width, height))
      .filter(Boolean) as { x: number; y: number }[];
    if (pixels.length < 3) continue;

    ctx.beginPath();
    ctx.moveTo(pixels[0].x, pixels[0].y);
    for (let i = 1; i < pixels.length; i++) ctx.lineTo(pixels[i].x, pixels[i].y);
    ctx.closePath();
    ctx.fill();
    drawnCount++;
  }

  const imgData = ctx.getImageData(0, 0, width, height).data;
  let whiteCount = 0;
  for (let i = 0; i < imgData.length; i += 4) if (imgData[i] > 128) whiteCount++;
  console.log(`[GlobeAIRender] Combined mask: ${drawnCount} zones, white=${whiteCount}/${width * height} (${((whiteCount / (width * height)) * 100).toFixed(1)}%)`);

  return canvas.toDataURL('image/png').split(',')[1];
}

// ─── COMPOSITING ENGINE (Phase 2) ─────────────────────────────────────

/** Load an image from a data URI and return an HTMLImageElement */
function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = (e) => reject(new Error(`Failed to load image: ${e}`));
    img.src = src;
  });
}

/**
 * Composite a single zone's AI render onto a cumulative canvas.
 * Ground zones: strict polygon clip with feathered edges.
 * Buildings: polygon clip for footprint + pixel-diff above for 3D silhouette.
 */
async function compositeZoneRender(
  baseDataUri: string,
  renderedDataUri: string,
  zone: SiteZone,
  camera: THREE.Camera,
  canvasWidth: number,
  canvasHeight: number,
  terrainHeight: number,
): Promise<string> {
  const [baseImg, renderedImg] = await Promise.all([
    loadImage(baseDataUri),
    loadImage(renderedDataUri),
  ]);

  const w = baseImg.naturalWidth;
  const h = baseImg.naturalHeight;

  const canvas = document.createElement('canvas');
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext('2d')!;
  ctx.drawImage(baseImg, 0, 0, w, h);

  if (!zone.coordinates || zone.coordinates.length < 3) {
    return canvas.toDataURL('image/png');
  }

  const pixels = zone.coordinates
    .map(c => projectToPixels(c[0], c[1], terrainHeight, camera, canvasWidth, canvasHeight))
    .filter(Boolean) as { x: number; y: number }[];
  if (pixels.length < 3) return canvas.toDataURL('image/png');

  const isBuilding = BUILDING_TYPES.includes(zone.zone_type);

  // Step 1: Mask-based composite with feathered edges
  const maskCanvas = document.createElement('canvas');
  maskCanvas.width = w;
  maskCanvas.height = h;
  const maskCtx = maskCanvas.getContext('2d')!;
  maskCtx.fillStyle = '#000000';
  maskCtx.fillRect(0, 0, w, h);
  maskCtx.fillStyle = '#ffffff';

  // Draw zone footprint polygon
  maskCtx.beginPath();
  maskCtx.moveTo(pixels[0].x, pixels[0].y);
  for (let i = 1; i < pixels.length; i++) maskCtx.lineTo(pixels[i].x, pixels[i].y);
  maskCtx.closePath();
  maskCtx.fill();

  // For buildings, extend mask upward by perspective headroom
  if (isBuilding) {
    const bldgH = (zone.properties?.height_m as number)
      || (zone.properties?.height as number)
      || ((zone.properties?.floors as number) || 0) * 3.2 || 0;
    const centroid = zone.coordinates.reduce(
      (acc, c) => [acc[0] + c[0] / zone.coordinates!.length, acc[1] + c[1] / zone.coordinates!.length],
      [0, 0],
    );
    const hr = bldgH > 0
      ? calculateGlobeHeadroom(camera, centroid[1], centroid[0], bldgH, canvasWidth, canvasHeight, terrainHeight)
      : 100;
    if (hr > 0) {
      const mnX = Math.min(...pixels.map(p => p.x));
      const mxX = Math.max(...pixels.map(p => p.x));
      const mnY = Math.min(...pixels.map(p => p.y));
      const expTop = Math.max(0, Math.floor(mnY - hr));
      maskCtx.fillRect(mnX, expTop, mxX - mnX, mnY - expTop);
    }
  }

  // Apply soft feather to mask edges (4px blur)
  const featherPx = 4;
  const featherCanvas = document.createElement('canvas');
  featherCanvas.width = w;
  featherCanvas.height = h;
  const featherCtx = featherCanvas.getContext('2d')!;
  featherCtx.filter = `blur(${featherPx}px)`;
  featherCtx.drawImage(maskCanvas, 0, 0);

  // Composite: AI render masked with feathered edges, then drawn onto base
  const aiCanvas = document.createElement('canvas');
  aiCanvas.width = w;
  aiCanvas.height = h;
  const aiCtx = aiCanvas.getContext('2d')!;
  aiCtx.drawImage(renderedImg, 0, 0, w, h);
  aiCtx.globalCompositeOperation = 'destination-in';
  aiCtx.drawImage(featherCanvas, 0, 0);
  ctx.drawImage(aiCanvas, 0, 0);

  // Step 2: For buildings, pixel-diff above the polygon for 3D silhouette
  if (isBuilding) {
    const bldgHeight = (zone.properties?.height_m as number)
      || (zone.properties?.height as number)
      || ((zone.properties?.floors as number) || 0) * 3.2 || 0;
    const centroid = zone.coordinates.reduce(
      (acc, c) => [acc[0] + c[0] / zone.coordinates!.length, acc[1] + c[1] / zone.coordinates!.length],
      [0, 0],
    );
    const headroom = bldgHeight > 0
      ? calculateGlobeHeadroom(camera, centroid[1], centroid[0], bldgHeight, canvasWidth, canvasHeight, terrainHeight)
      : 100;

    const minX = Math.min(...pixels.map(p => p.x));
    const maxX = Math.max(...pixels.map(p => p.x));
    const minY = Math.min(...pixels.map(p => p.y));
    const expandedTop = Math.max(0, Math.floor(minY - headroom));

    const regionX = Math.max(0, Math.floor(minX));
    const regionR = Math.min(w, Math.ceil(maxX));
    const regionY = expandedTop;
    const regionB = Math.floor(minY);

    if (regionB > regionY && regionR > regionX) {
      const rw = regionR - regionX;
      const rh = regionB - regionY;

      const baseTmpCanvas = document.createElement('canvas');
      baseTmpCanvas.width = w;
      baseTmpCanvas.height = h;
      const baseTmpCtx = baseTmpCanvas.getContext('2d')!;
      baseTmpCtx.drawImage(baseImg, 0, 0, w, h);

      const rendTmpCanvas = document.createElement('canvas');
      rendTmpCanvas.width = w;
      rendTmpCanvas.height = h;
      const rendTmpCtx = rendTmpCanvas.getContext('2d')!;
      rendTmpCtx.drawImage(renderedImg, 0, 0, w, h);

      const baseRegion = baseTmpCtx.getImageData(regionX, regionY, rw, rh);
      const rendRegion = rendTmpCtx.getImageData(regionX, regionY, rw, rh);
      const currentData = ctx.getImageData(0, 0, w, h);
      const currentPx = currentData.data;

      const DIFF_THRESHOLD = 18;
      for (let row = 0; row < rh; row++) {
        for (let col = 0; col < rw; col++) {
          const idx = (row * rw + col) * 4;
          const dr = Math.abs(baseRegion.data[idx] - rendRegion.data[idx]);
          const dg = Math.abs(baseRegion.data[idx + 1] - rendRegion.data[idx + 1]);
          const db = Math.abs(baseRegion.data[idx + 2] - rendRegion.data[idx + 2]);

          if (Math.max(dr, dg, db) > DIFF_THRESHOLD) {
            const globalIdx = ((regionY + row) * w + (regionX + col)) * 4;
            currentPx[globalIdx] = rendRegion.data[idx];
            currentPx[globalIdx + 1] = rendRegion.data[idx + 1];
            currentPx[globalIdx + 2] = rendRegion.data[idx + 2];
            currentPx[globalIdx + 3] = rendRegion.data[idx + 3];
          }
        }
      }

      ctx.putImageData(currentData, 0, 0);
      console.log(`[GlobeAIRender] compositeZoneRender: BUILDING "${zone.name || zone.zone_type}" — polygon clip + pixel-diff ${rw}x${rh}px above`);
    } else {
      console.log(`[GlobeAIRender] compositeZoneRender: BUILDING "${zone.name || zone.zone_type}" — polygon clip only`);
    }
  } else {
    console.log(`[GlobeAIRender] compositeZoneRender: ${zone.zone_type} — strict polygon clip`);
  }

  return canvas.toDataURL('image/png');
}

/**
 * Paint ALL zone polygons with numbered labels onto a screenshot.
 * Each zone gets its colored polygon fill + a bold number label at its centroid.
 * The number matches the ZONES list in the prompt so Gemini can identify each zone.
 */
function paintAllZonesOnScreenshot(
  screenshotBase64: string,
  zones: SiteZone[],
  camera: THREE.Camera,
  canvasWidth: number,
  canvasHeight: number,
  terrainHeight: number,
): Promise<string> {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      const ctx = canvas.getContext('2d')!;
      ctx.drawImage(img, 0, 0);

      // Pass 1: Draw all colored polygon fills
      for (const zone of zones) {
        if (!zone.coordinates || zone.coordinates.length < 3) continue;
        const pixels = zone.coordinates
          .map(c => projectToPixels(c[0], c[1], terrainHeight, camera, canvasWidth, canvasHeight))
          .filter(Boolean) as { x: number; y: number }[];
        if (pixels.length < 3) continue;

        ctx.fillStyle = resolveZoneColor(zone);
        ctx.globalAlpha = 0.7;
        ctx.beginPath();
        ctx.moveTo(pixels[0].x, pixels[0].y);
        for (let i = 1; i < pixels.length; i++) ctx.lineTo(pixels[i].x, pixels[i].y);
        ctx.closePath();
        ctx.fill();
      }

      // Pass 2: Draw numbered labels on top
      ctx.globalAlpha = 1.0;
      for (let zi = 0; zi < zones.length; zi++) {
        const zone = zones[zi];
        if (!zone.coordinates || zone.coordinates.length < 3) continue;
        const pixels = zone.coordinates
          .map(c => projectToPixels(c[0], c[1], terrainHeight, camera, canvasWidth, canvasHeight))
          .filter(Boolean) as { x: number; y: number }[];
        if (pixels.length < 3) continue;

        // Calculate centroid
        const cx = pixels.reduce((s, p) => s + p.x, 0) / pixels.length;
        const cy = pixels.reduce((s, p) => s + p.y, 0) / pixels.length;

        // Calculate polygon size to scale font
        const minX = Math.min(...pixels.map(p => p.x));
        const maxX = Math.max(...pixels.map(p => p.x));
        const polyWidth = maxX - minX;
        const fontSize = Math.max(12, Math.min(32, polyWidth * 0.3));

        const label = String(zi + 1);

        // Draw white circle background
        ctx.fillStyle = 'white';
        ctx.beginPath();
        ctx.arc(cx, cy, fontSize * 0.7, 0, Math.PI * 2);
        ctx.fill();

        // Draw black border
        ctx.strokeStyle = 'black';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Draw number
        ctx.fillStyle = 'black';
        ctx.font = `bold ${fontSize}px Arial, sans-serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(label, cx, cy);
      }

      resolve(canvas.toDataURL('image/png'));
    };
    img.src = `data:image/png;base64,${screenshotBase64}`;
  });
}

// Suppress unused warnings — available for future per-building mode
void generateSingleZoneMask;

// ─── ARCHETYPE & PROMPT HELPERS ────────────────────────────────────────

/**
 * Get the map overlay render prompt for a zone's archetype.
 */
function getMapOverlayPrompt(zone: SiteZone): string | undefined {
  const props = zone.properties || {};
  const archetypeId = (props.development_archetype_id as string)
    || (props.green_space_archetype_id as string)
    || (props.road_archetype_id as string)
    || (props.plaza_archetype_id as string)
    || '';

  if (!archetypeId) return undefined;

  const entry = catalog.find((a: any) => a.id === archetypeId || archetypeId.startsWith(a.id + '_'));
  return entry?.renderPrompt?.mapOverlay || entry?.prompt?.subject || undefined;
}

/**
 * Extract archetype metadata from zone properties.
 * Enriched version with corridor, massing, and height tendency data.
 */
function getZoneArchetypeInfo(zone: SiteZone): {
  archetypeTitle?: string;
  facadeDescription?: string;
  roofDescription?: string;
  materials?: string;
  massing?: string;
  heightTendency?: string;
  aerialAppearance?: string;
  publicRealm?: string;
  mapOverlayPrompt?: string;
  colorScheme?: string;
  corridorDescription?: string;
} {
  if (!zone.properties || !catalog) return {};

  for (const prefix of ['development', 'road', 'green_space', 'plaza'] as const) {
    const archetypeId = zone.properties[`${prefix}_archetype_id`] as string | undefined;
    if (!archetypeId) continue;

    const entry = catalog.find((a: any) => a.id === archetypeId || archetypeId.startsWith(a.id + '_'));
    if (!entry) continue;

    const sp = entry.styleProfile || {};
    const fd = entry.facadeDetail || {};
    const rd = entry.roofDetail || {};

    const facadeParts: string[] = [];
    if (fd.primaryMaterial) facadeParts.push(fd.primaryMaterial);
    if (fd.groundFloor) facadeParts.push(`Ground floor: ${fd.groundFloor}`);
    if (fd.upperFloors) facadeParts.push(`Upper floors: ${fd.upperFloors}`);
    if (fd.cornice) facadeParts.push(`Cornice: ${fd.cornice}`);
    if (fd.colorScheme) facadeParts.push(`Colors: ${fd.colorScheme}`);

    const roofParts: string[] = [];
    if (rd.form) roofParts.push(rd.form);
    if (rd.material) roofParts.push(rd.material);
    if (rd.features) roofParts.push(rd.features);
    if (rd.aerialAppearance) roofParts.push(`Aerial: ${rd.aerialAppearance}`);

    // Road/corridor specific
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
      materials: Array.isArray(sp.materials) ? sp.materials.join(', ') : sp.materials,
      massing: sp.massing || undefined,
      heightTendency: sp.heightTendency || undefined,
      aerialAppearance: rd.aerialAppearance || undefined,
      publicRealm: sp.publicRealm || undefined,
      mapOverlayPrompt: entry.renderPrompt?.mapOverlay || entry.prompt?.subject || undefined,
      colorScheme: fd.colorScheme || undefined,
      corridorDescription: corridorParts.length > 0 ? corridorParts.join('. ') : undefined,
    };
  }
  return {};
}

// ─── STRUCTURED PROMPT SYSTEM (Phase 4) ────────────────────────────────

const STYLE_PROMPTS: Record<string, string> = {
  photorealistic: 'Photorealistic architectural visualization, photomontage quality, golden hour afternoon sunlight, sharp detail on materials and facades.',
  winter: 'Photorealistic winter scene with fresh snow on roofs and ground, bare deciduous trees, cool winter afternoon light, frost on surfaces. Snow-covered roofs, frosted ground plane, bare deciduous trees, evergreens with heavy snow-load.',
  atmospheric: 'Dramatic golden hour, low-angle warm sun, long architectural shadows, volumetric haze, warm orange light from the west.',
  spring: 'Photorealistic spring scene, fresh green foliage on trees, cherry blossoms, bright midday sunlight, vivid colors.',
  night: 'Nighttime scene, city lights, warm interior glow from windows, moonlit sky, wet reflective streets.',
};

const LIGHTING_MAP: Record<string, string> = {
  photorealistic: 'Golden hour, warm southwest sun, crisp architectural shadows.',
  winter: 'Soft diffuse winter daylight, low sun angle, long blue-tinted shadows, pale blue-grey overcast sky. Snow-covered roofs, frosted ground plane, bare deciduous trees with visible branch structure, evergreens with heavy snow-load.',
  atmospheric: 'Dramatic golden hour, low-angle warm sun, long architectural shadows, volumetric haze.',
  spring: 'Bright spring midday sun, vivid colors, fresh green light.',
  night: 'Moonlight and city glow, artificial lighting, warm window light.',
};

/** Extract N keywords from verbose description text, joining with '+' */
function condenseToKeywords(text: string | undefined, maxTokens = 4): string {
  if (!text) return '';
  const tokens = text
    .replace(/\.\s+/g, ', ')
    .split(/[,;:]+/)
    .map(t => t.trim())
    .filter(t => t.length > 2)
    .map(t => t.replace(/^(a |an |the |with |and |or |in |on |at |of |for |is |are |has |have |its |this )/gi, '').trim())
    .filter(t => t.length > 2)
    .slice(0, maxTokens);
  return tokens.join('+');
}

/** Check if a zone is a "priority" type that needs richer description */
function isPriorityZone(entry: ZonePromptEntry): boolean {
  const name = (entry.archetypeTitle || entry.zoneName || '').toLowerCase();
  const PRIORITY_KEYWORDS = [
    'arena', 'stadium', 'colosseum', 'amphitheater',
    'hotel', 'resort', 'chateauesque',
    'transit', 'station', 'vertiport', 'terminal',
    'church', 'mosque', 'temple', 'cathedral',
    'museum', 'courthouse', 'monument',
    'climbing', 'data center', 'vertical farm',
    'fire station', 'brewery', 'distillery',
    'waste-to-energy', 'solar farm',
    'immersive', 'concert hall', 'opera',
    'mall redevelopment', 'terraced',
  ];
  return PRIORITY_KEYWORDS.some(kw => name.includes(kw));
}

/** Build a compressed SCHEMA zone label from a ZonePromptEntry.
 *  Standard zones: ~100 chars. Priority zones: ~160 chars for richer detail. */
function buildCompressedZoneLabel(entry: ZonePromptEntry): string {
  const isBuilding = BUILDING_TYPES.includes(entry.zoneType);
  const isRoad = ['road', 'street', 'path'].includes(entry.zoneType);
  const isPark = ['green_space', 'park', 'plaza', 'water'].includes(entry.zoneType);
  const priority = isPriorityZone(entry);

  const name = entry.archetypeTitle || entry.zoneName || entry.zoneType;

  // Scale
  let scale = 'gnd';
  if (isBuilding) {
    if (entry.floors && entry.heightM) scale = `${entry.floors}F ${entry.heightM}m`;
    else if (entry.floors) scale = `${entry.floors}F`;
    else if (entry.heightM) scale = `${entry.heightM}m`;
    else scale = 'multi-story';
  }

  // Materials/features — priority zones get more keywords
  const maxKeywords = priority ? 6 : 3;
  let features = '';

  if (isBuilding) {
    const parts: string[] = [];
    if (entry.materials) parts.push(condenseToKeywords(entry.materials, priority ? 3 : 2));
    if (entry.facadeDescription) parts.push(condenseToKeywords(entry.facadeDescription, priority ? 3 : 2));
    if (entry.roofDescription) parts.push(condenseToKeywords(entry.roofDescription, priority ? 2 : 1));
    if (priority && entry.aerialAppearance) parts.push(condenseToKeywords(entry.aerialAppearance, 2));
    if (priority && entry.massing) parts.push(condenseToKeywords(entry.massing, 2));
    features = parts.filter(Boolean).join(', ');
  } else if (isRoad) {
    const roadDesc = entry.corridorDescription || entry.publicRealm || entry.materials || entry.descriptionText;
    features = condenseToKeywords(roadDesc, maxKeywords);
  } else if (isPark) {
    const parkDesc = entry.publicRealm || entry.materials || entry.descriptionText;
    features = condenseToKeywords(parkDesc, maxKeywords);
  } else {
    features = condenseToKeywords(entry.descriptionText || entry.materials || entry.publicRealm, maxKeywords);
  }

  // User description appended if present
  if (entry.descriptionText?.trim() && entry.descriptionText.trim().length > 10) {
    const userKeywords = condenseToKeywords(entry.descriptionText, 3);
    if (userKeywords && !features.includes(userKeywords)) {
      features = features ? `${features}, ${userKeywords}` : userKeywords;
    }
  }

  if (!features) features = entry.zoneType.replace(/_/g, ' ');

  const maxLen = priority ? 160 : 100;
  const label = `[${entry.color}] ${name} | ${scale} | ${features}`;
  return label.length > maxLen ? label.slice(0, maxLen - 3) + '...' : label;
}

/** Default zone description for zones with no archetype */
function defaultZoneDescription(zoneType: string): string {
  switch (zoneType) {
    case 'building': return 'photorealistic commercial/mixed-use buildings with glass and concrete facades, multiple stories';
    case 'residential': return 'photorealistic residential buildings — townhouses or apartment blocks with warm materials, balconies';
    case 'road': case 'street': case 'path':
      return 'urban streetscape with asphalt, lane markings, sidewalks, street trees, pedestrian lighting';
    case 'green_space': case 'park':
      return 'landscaped urban park with mature trees, lawns, walking paths, benches, flower beds';
    case 'plaza':
      return 'public plaza with premium paving, cafe seating, water feature, accent planting';
    case 'parking':
      return 'surface parking lot with painted stalls, directional arrows, perimeter landscaping';
    case 'water':
      return 'water feature — pond, fountain, or reflecting pool';
    default: return 'photorealistic urban development appropriate to the zone type';
  }
}
void defaultZoneDescription; // used in fallback prompts
void getMapOverlayPrompt; // used via getZoneArchetypeInfo.mapOverlayPrompt
void buildGroundPlanePrompt; // available for future fine-grained mode
void buildBuildingPrompt; // available for future fine-grained mode
void GROUND_TYPES; // used in zone categorization logic

/** Build a zone prompt entry from a SiteZone */
function zoneToPromptEntry(zone: SiteZone): ZonePromptEntry {
  const info = getZoneArchetypeInfo(zone);
  const color = colorName(resolveZoneColor(zone));
  const props = zone.properties || {};
  const floors = (props.floors as number) || (props.num_floors as number) || undefined;
  const heightM = (props.height_m as number) || (props.height as number) || undefined;

  return {
    color,
    zoneType: zone.zone_type,
    zoneName: zone.name || ZONE_TYPE_CONFIG[zone.zone_type]?.label || zone.zone_type,
    descriptionText: (props.description as string) || (props.descriptive_text as string) || (props.description_text as string) || undefined,
    floors: typeof floors === 'number' ? floors : undefined,
    heightM: typeof heightM === 'number' ? heightM : undefined,
    archetypeTitle: info.archetypeTitle,
    facadeDescription: info.facadeDescription,
    roofDescription: info.roofDescription,
    materials: info.materials,
    massing: info.massing,
    heightTendency: info.heightTendency,
    publicRealm: info.publicRealm,
    mapOverlayPrompt: info.mapOverlayPrompt,
    colorScheme: info.colorScheme,
    aerialAppearance: info.aerialAppearance,
    corridorDescription: info.corridorDescription,
  };
}

/**
 * Build SCHEMA-style structured prompt for aerial renders.
 * Supports three modes:
 * - 'full': all zones in one prompt (single-shot render)
 * - 'ground': ground-level zones only (Pass 1 of per-zone)
 * - 'building': single building zone (Pass 2 of per-zone)
 */
function buildSCHEMAPrompt(
  entries: ZonePromptEntry[],
  style: string,
  mode: 'full' | 'ground' | 'building' = 'full',
): string {
  const lines: string[] = [];

  // ── STYLE ──
  lines.push(`STYLE: ${STYLE_PROMPTS[style] || STYLE_PROMPTS.photorealistic}`);

  // ── COMPOSITION (mode-specific) ──
  if (mode === 'ground') {
    lines.push('COMPOSITION: Oblique aerial view from 3D photorealistic city model, ground-level zones only, no vertical structures.');
  } else if (mode === 'building') {
    const entry = entries[0];
    lines.push(`COMPOSITION: Oblique aerial view from 3D photorealistic city model, single building on ${entry?.color || 'colored'} footprint, full 3D mass extending into sky.`);
  } else {
    const hasBuildings = entries.some(e => BUILDING_TYPES.includes(e.zoneType));
    lines.push(hasBuildings
      ? 'COMPOSITION: Oblique aerial view from 3D photorealistic city model, colored polygons mark proposed zones on the existing photographic context.'
      : 'COMPOSITION: Oblique aerial view, ground-level zones only on photorealistic 3D terrain.');
  }

  // ── LIGHTING ──
  lines.push(`LIGHTING: ${LIGHTING_MAP[style] || LIGHTING_MAP.photorealistic}`);

  // ── CONTEXT (globe-specific) ──
  lines.push('CONTEXT: This image is captured from a 3D photorealistic city model with real Google Earth buildings. Preserve ALL unmasked photographic context exactly as-is. Rendered zones must blend naturally at edges — match tones, lighting, and scale of adjacent real buildings.');
  lines.push('COLOR TEMPERATURE MATCHING: Analyze the color temperature and atmospheric conditions of the EXISTING buildings and terrain in the photograph. Match the EXACT same warm/cool tone, haze level, and ambient light color on all rendered zones. If the scene has golden-hour warmth, render buildings with the same warm amber tones — NOT neutral daylight grey. Rendered materials must look like they exist in the same atmosphere and light as the surrounding real buildings.');
  lines.push('ATMOSPHERIC PERSPECTIVE: Apply the same atmospheric haze and aerial perspective visible on surrounding buildings at similar distances. Distant rendered zones should have reduced contrast and shifted color matching the existing depth cues in the photograph.');

  // ── NUMERICAL INVENTORY (full mode only) ──
  if (mode === 'full' && entries.length > 1) {
    const bldgCount = entries.filter(e => BUILDING_TYPES.includes(e.zoneType)).length;
    const parkCount = entries.filter(e => e.zoneType === 'green_space' || e.zoneType === 'park').length;
    const roadCount = entries.filter(e => e.zoneType === 'road' || e.zoneType === 'street' || e.zoneType === 'path').length;
    lines.push(`NUMERICAL INVENTORY: ${entries.length} zones: ${bldgCount} building${bldgCount !== 1 ? 's' : ''}, ${parkCount} park${parkCount !== 1 ? 's' : ''}, ${roadCount} road${roadCount !== 1 ? 's' : ''}.`);
  }

  // ── ZONES ──
  if (entries.length > 0) {
    lines.push('ZONES (each zone is marked with a numbered circle label on the image AND a colored polygon — use BOTH the number and the color to identify each zone):');
    entries.forEach((entry, i) => {
      lines.push(`${i + 1}. ${buildCompressedZoneLabel(entry)}`);
    });
  }

  // ── MANDATORY ──
  lines.push('MANDATORY: Each zone renders ONLY within its colored polygon boundary. Realistic rooftop materials — no colored polygon fill visible. Replace ALL colored overlays with appropriate architectural materials. Match scale and density of surrounding real 3D buildings. Rendered building facades and roofs MUST have the same color cast, warmth, and atmospheric tint as adjacent real buildings.');

  // ── PROHIBITIONS ──
  const prohibitions = [
    'buildings extending beyond polygon boundaries',
    'colored polygon fills visible on rooftops or facades',
    'boundary lines visible',
    'text overlays',
    'watermarks',
    'color temperature mismatch between rendered and existing buildings',
    'rendered buildings appearing unnaturally crisp or clean compared to surroundings',
  ];
  if (style === 'winter') {
    prohibitions.push('lush green vegetation', 'summer foliage', 'bright green lawns');
  }
  lines.push(`PROHIBITIONS: ${prohibitions.join(', ')}`);

  // ── CRITICAL FINAL ──
  lines.push('CRITICAL FINAL INSTRUCTION: Do NOT modify ANY pixels outside the colored polygon zones. Every existing building, house, tree, road, car, and terrain feature outside the zones MUST remain pixel-perfect identical to the input photograph. The white mask defines the EXACT boundary — nothing renders outside it.');

  const result = lines.join('\n');
  console.log(`[GlobeAIRender] SCHEMA prompt (${result.length} chars, ${entries.length} zones, mode=${mode}):\n${result.substring(0, 300)}...`);
  return result;
}

/** Build prompt for all zones (single-shot) */
function buildPrompt(zones: SiteZone[], style: string): string {
  const renderZones = zones.filter(z => z.zone_type !== 'site_boundary');
  const entries = renderZones.map(z => zoneToPromptEntry(z));
  return buildSCHEMAPrompt(entries, style, 'full');
}

/** Build prompt for ground-level zones only (Pass 1 of per-zone) */
function buildGroundPlanePrompt(groundZones: SiteZone[], style: string): string {
  const entries = groundZones.map(z => zoneToPromptEntry(z));
  return buildSCHEMAPrompt(entries, style, 'ground');
}

/** Build prompt for a single building zone (Pass 2 of per-zone) */
function buildBuildingPrompt(zone: SiteZone, style: string): string {
  const entry = zoneToPromptEntry(zone);
  return buildSCHEMAPrompt([entry], style, 'building');
}

export function useGlobeAIRender() {
  const isRenderingRef = useRef(false);

  const render = useCallback(async (
    canvas: HTMLCanvasElement,
    camera: THREE.Camera,
    zones: SiteZone[],
    terrainHeight: number,
    options: {
      style?: string;
      model?: string;
      projectId?: string;
      customPrompt?: string;
    } = {},
  ): Promise<GlobeRenderResult | null> => {
    if (isRenderingRef.current) return null;
    isRenderingRef.current = true;

    try {
      const { style = 'photorealistic', model = 'gemini-3.1-flash-image-preview', customPrompt } = options;

      // 1. Capture the globe canvas
      console.log('[GlobeAIRender] Capturing canvas...');
      const imageBase64 = await captureCanvasBase64(canvas);
      if (!imageBase64) throw new Error('Failed to capture canvas');

      // 2. Generate binary mask from zone polygons
      console.log('[GlobeAIRender] Generating mask...');
      const maskBase64 = generateColorCodedMask(zones, camera, canvas.width, canvas.height, terrainHeight);

      // 3. Build SCHEMA prompt from zone archetypes
      let prompt = buildPrompt(zones, style);
      if (customPrompt) prompt += `\nADDITIONAL: ${customPrompt}`;

      // 4. Collect archetype reference card images (up to 6)
      console.log('[GlobeAIRender] Collecting archetype reference images...');
      // Archetype images disabled — full-size PNGs cause 502 payload errors
      const archetypeImages: Awaited<ReturnType<typeof collectArchetypeImages>> = [];
      if (archetypeImages.length > 0) {
        prompt += `\n\nARCHETYPE STYLE REFERENCES (Images 2+): ${archetypeImages.length} reference images show the exact architectural style for specific zones. Use Image 1 as the spatial context. Apply each reference style to the matching colored zone.`;
        for (let i = 0; i < archetypeImages.length; i++) {
          prompt += `\nImage ${i + 2}: Style reference for [${archetypeImages[i].zone_color}] ${archetypeImages[i].label}`;
        }
      }

      console.log(`[GlobeAIRender] Prompt (${prompt.length} chars, ${zones.filter(z => z.zone_type !== 'site_boundary').length} zones, ${archetypeImages.length} ref images):`, prompt.substring(0, 200) + '...');

      // 5. Send to backend render API with archetype images
      console.log('[GlobeAIRender] Sending to Gemini via backend...');
      const resp = await api.post(
        '/api/v1/render/generate',
        {
          image_base64: imageBase64,
          mask_base64: maskBase64,
          prompt,
          negative_prompt: 'cartoon, illustration, sketch, low quality, blurry, text, watermark, unrealistic colors',
          model,
          temperature: 0.0,
          guidance_scale: 15,
          archetype_images: archetypeImages.length > 0 ? archetypeImages : undefined,
        },
        { timeout: 120000 },
      );

      if (resp.data?.image_base64) {
        console.log('[GlobeAIRender] Render complete!');
        return {
          imageUrl: `data:image/png;base64,${resp.data.image_base64}`,
          prompt,
          seed: resp.data.seed,
        };
      }

      console.warn('[GlobeAIRender] No image in response');
      return null;

    } catch (err) {
      console.error('[GlobeAIRender] Error:', err);
      return null;
    } finally {
      isRenderingRef.current = false;
    }
  }, []);

  /**
   * Per-zone sequential render — 3-pass system by zone category.
   * Pass 1: All parks/plazas in one call
   * Pass 2: All streets/roads in one call
   * Pass 3: All buildings in one call
   * Each pass gets a focused prompt and combined mask for its category.
   * Total: 3 API calls instead of 20+ — fast AND accurate.
   */
  const renderPerZone = useCallback(async (
    canvas: HTMLCanvasElement,
    camera: THREE.Camera,
    zones: SiteZone[],
    terrainHeight: number,
    options: {
      style?: string;
      model?: string;
      projectId?: string;
      customPrompt?: string;
      onProgress?: (status: string, current: number, total: number) => void;
    } = {},
  ): Promise<GlobeRenderResult | null> => {
    if (isRenderingRef.current) return null;
    isRenderingRef.current = true;

    try {
      const { style = 'photorealistic', model = 'gemini-3.1-flash-image-preview', customPrompt, onProgress } = options;
      const renderZones = zones.filter(z => z.zone_type !== 'site_boundary');

      // Categorize zones into 3 groups
      const parkZones = renderZones.filter(z =>
        ['green_space', 'park', 'plaza', 'water', 'parking'].includes(z.zone_type));
      const streetZones = renderZones.filter(z =>
        ['road', 'street', 'path'].includes(z.zone_type));
      const buildingZones = renderZones.filter(z =>
        BUILDING_TYPES.includes(z.zone_type));
      // Catch-all for zone types that don't fit neatly
      const otherGroundZones = renderZones.filter(z =>
        ['development_area'].includes(z.zone_type));

      // Merge small categories: other ground zones go with parks
      const effectiveParkZones = [...parkZones, ...otherGroundZones];

      // Build pass list (skip empty categories)
      const passes: Array<{ label: string; zones: SiteZone[]; mode: 'ground' | 'building' }> = [];
      if (effectiveParkZones.length > 0) passes.push({ label: 'Parks & Plazas', zones: effectiveParkZones, mode: 'ground' });
      if (streetZones.length > 0) passes.push({ label: 'Streets & Roads', zones: streetZones, mode: 'ground' });
      if (buildingZones.length > 0) passes.push({ label: 'Buildings', zones: buildingZones, mode: 'building' });

      const totalSteps = passes.length;

      // Thinking budget based on total zone count
      let thinkingBudget: number | undefined;
      if (renderZones.length >= 30) thinkingBudget = 24576;
      else if (renderZones.length >= 16) thinkingBudget = 16384;
      else if (renderZones.length >= 6) thinkingBudget = 8192;

      // Capture base screenshot (Google 3D Tiles context)
      console.log('[GlobeAIRender] Per-zone: capturing base screenshot...');
      const baseScreenshot = await captureCanvasBase64(canvas);
      if (!baseScreenshot) throw new Error('Failed to capture canvas');

      // Initialize cumulative result with the base screenshot
      let cumulativeDataUri = `data:image/png;base64,${baseScreenshot}`;

      // Build ONE full prompt with all zones — reused for every pass
      // Each pass gets the full urban context but only edits within its mask
      const allEntries = renderZones.map(z => zoneToPromptEntry(z));
      let fullPrompt = buildSCHEMAPrompt(allEntries, style, 'full');
      fullPrompt += '\nMASK SCOPE: This render uses a multi-pass approach. The white mask defines which zones to render in THIS pass. Zones outside the mask are listed for adjacency context only — do NOT modify them. Render only the masked zones, matching their style to the surrounding urban fabric.';
      if (customPrompt) fullPrompt += `\nADDITIONAL: ${customPrompt}`;

      console.log(`[GlobeAIRender] Full prompt for all passes (${fullPrompt.length} chars, ${allEntries.length} zones)`);

      // ── Execute each pass ──
      for (let pi = 0; pi < passes.length; pi++) {
        const pass = passes[pi];
        onProgress?.(`Pass ${pi + 1}/${totalSteps}: ${pass.label} (${pass.zones.length} zones)...`, pi + 1, totalSteps);
        console.log(`[GlobeAIRender] Pass ${pi + 1}/${totalSteps}: ${pass.label} — ${pass.zones.length} zones`);

        // Generate mask for THIS pass's zones only
        // For buildings, use binary mask with headroom; for ground, combined mask
        const passMask = pass.mode === 'building'
          ? generateBinaryMask(pass.zones, camera, canvas.width, canvas.height, terrainHeight)
          : generateCombinedMask(pass.zones, camera, canvas.width, canvas.height, terrainHeight);

        // Paint ALL zone polygons with numbered labels onto the cumulative result
        // so Gemini sees the full colored + numbered site plan
        const paintedUri = await paintAllZonesOnScreenshot(
          cumulativeDataUri.split(',')[1], renderZones,
          camera, canvas.width, canvas.height, terrainHeight,
        );
        const paintedScreenshot = paintedUri.split(',')[1];

        // API call — same full prompt every pass, different mask
        const resp = await api.post(
          '/api/v1/render/generate',
          {
            image_base64: paintedScreenshot,
            mask_base64: passMask,
            prompt: fullPrompt,
            negative_prompt: 'cartoon, illustration, sketch, low quality, blurry, text, watermark, unrealistic colors',
            model,
            temperature: 0.0,
            guidance_scale: 15,
            thinking_budget: thinkingBudget,
          },
          { timeout: 180000 },
        );

        if (resp.data?.image_base64) {
          const renderedDataUri = `data:image/png;base64,${resp.data.image_base64}`;
          // Composite each zone in this pass onto cumulative
          for (const zone of pass.zones) {
            cumulativeDataUri = await compositeZoneRender(
              cumulativeDataUri, renderedDataUri, zone,
              camera, canvas.width, canvas.height, terrainHeight,
            );
          }
          console.log(`[GlobeAIRender] Pass ${pi + 1} complete — ${pass.label} composited`);
        } else {
          console.warn(`[GlobeAIRender] No image for pass ${pi + 1}: ${pass.label}`);
        }
      }

      onProgress?.('Render complete!', totalSteps, totalSteps);
      console.log(`[GlobeAIRender] Per-zone render complete! ${totalSteps} API calls`);

      return {
        imageUrl: cumulativeDataUri,
        prompt: fullPrompt,
      };

    } catch (err) {
      console.error('[GlobeAIRender] Per-zone error:', err);
      return null;
    } finally {
      isRenderingRef.current = false;
    }
  }, []);

  /**
   * Capture the Google 3D Tiles from street level.
   * Moves camera to street height, waits for tiles, captures, then restores camera.
   */
  const captureStreetView = useCallback(async (
    canvas: HTMLCanvasElement,
    camera: THREE.Camera,
    lat: number,
    lng: number,
    headingDeg: number,
    terrainHeight: number,
    flyToStreetLevel: (lat: number, lng: number, heading: number, terrainH: number, cam?: THREE.Camera) => void,
    restoreAerialView: (state: any, cam?: THREE.Camera) => void,
    saveCameraState: (cam?: THREE.Camera) => any,
  ): Promise<string | null> => {
    // Save current camera state
    const savedState = saveCameraState(camera);
    if (!savedState) return null;

    try {
      // Move camera to street level
      flyToStreetLevel(lat, lng, headingDeg, terrainHeight, camera);

      // Wait for tiles to load at street-level LOD
      // Phase 1: Let renderer process new camera position
      for (let i = 0; i < 10; i++) {
        await new Promise(r => requestAnimationFrame(r));
      }

      // Phase 2: Wait for tile streaming with timeout
      // Poll every 500ms for up to 8 seconds
      console.log('[GlobeAIRender] Waiting for street-level tiles to load...');
      for (let attempt = 0; attempt < 16; attempt++) {
        await new Promise(r => setTimeout(r, 500));
        // Render a frame to trigger tile updates
        await new Promise(r => requestAnimationFrame(r));
      }

      // Phase 3: Final frames for render completion
      for (let i = 0; i < 5; i++) {
        await new Promise(r => requestAnimationFrame(r));
      }

      // Capture the street-level view
      console.log('[GlobeAIRender] Capturing street-level view...');
      const imageBase64 = await captureCanvasBase64(canvas);

      return imageBase64 || null;
    } finally {
      // Always restore the camera
      restoreAerialView(savedState, camera);
    }
  }, []);

  return { render, renderPerZone, captureStreetView, isRenderingRef };
}
