/**
 * useGlobeAIRender.ts — AI render pipeline for the 3D globe.
 *
 * Captures the R3F canvas screenshot (with photorealistic 3D tiles context),
 * generates a binary mask from zone polygons using Three.js camera projection,
 * builds the prompt from zone archetypes, and sends to the Gemini API.
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

export interface GlobeRenderResult {
  imageUrl: string;  // data:image/png;base64,...
  prompt: string;
  seed?: number;
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

// ─── OCCLUSION CULLING ─────────────────────────────────────────────────

/**
 * Check which zones are significantly occluded by other (taller) zones
 * in screen space. Returns a Set of zone IDs that should be culled.
 *
 * Algorithm: For each zone, render all OTHER building zones (that are taller
 * or in front) as filled polygons onto a test canvas, then check how many
 * pixels of the target zone's footprint are covered.
 * If >60% covered, the zone is occluded and should be removed from the prompt.
 */
function findOccludedZones(
  zones: SiteZone[],
  camera: THREE.Camera,
  width: number,
  height: number,
  terrainHeight: number,
  threshold = 0.6,
): Set<string> {
  const occluded = new Set<string>();
  const renderZones = zones.filter(z => z.zone_type !== 'site_boundary' && z.coordinates?.length >= 3);

  // Project all zones to screen pixels and calculate their properties
  const projected = renderZones.map(zone => {
    const pixels = zone.coordinates
      .map(c => projectToPixels(c[0], c[1], terrainHeight, camera, width, height))
      .filter(Boolean) as { x: number; y: number }[];

    const buildingHeight = (zone.properties?.height_m as number)
      || (zone.properties?.height as number)
      || ((zone.properties?.floors as number) || 0) * 3.2 || 0;

    // Project roof height too for buildings
    const roofPixels = buildingHeight > 0
      ? zone.coordinates
          .map(c => projectToPixels(c[0], c[1], terrainHeight + buildingHeight, camera, width, height))
          .filter(Boolean) as { x: number; y: number }[]
      : [];

    // Average Y position (lower Y = higher on screen = closer to camera in oblique view)
    const avgY = pixels.length > 0 ? pixels.reduce((s, p) => s + p.y, 0) / pixels.length : 0;

    return { zone, pixels, roofPixels, buildingHeight, avgY };
  });

  // Use a small canvas for fast pixel testing (1/4 resolution)
  const scale = 0.25;
  const sw = Math.round(width * scale);
  const sh = Math.round(height * scale);

  for (const target of projected) {
    if (target.pixels.length < 3) continue;

    // Find zones that could occlude this one:
    // - taller buildings whose screen footprint overlaps
    // - zones that are closer to camera (lower avgY in oblique view)
    const occluders = projected.filter(other =>
      other.zone.id !== target.zone.id &&
      other.pixels.length >= 3 &&
      (other.buildingHeight > target.buildingHeight || other.avgY > target.avgY) &&
      ['building', 'residential', 'commercial', 'industrial', 'mixed_use'].includes(other.zone.zone_type),
    );

    if (occluders.length === 0) continue;

    // Draw target zone footprint
    const targetCanvas = document.createElement('canvas');
    targetCanvas.width = sw;
    targetCanvas.height = sh;
    const targetCtx = targetCanvas.getContext('2d')!;
    targetCtx.fillStyle = '#ffffff';
    targetCtx.beginPath();
    targetCtx.moveTo(target.pixels[0].x * scale, target.pixels[0].y * scale);
    for (let i = 1; i < target.pixels.length; i++) {
      targetCtx.lineTo(target.pixels[i].x * scale, target.pixels[i].y * scale);
    }
    targetCtx.closePath();
    targetCtx.fill();

    // Count target pixels
    const targetData = targetCtx.getImageData(0, 0, sw, sh).data;
    let targetPixelCount = 0;
    for (let i = 0; i < targetData.length; i += 4) {
      if (targetData[i] > 128) targetPixelCount++;
    }
    if (targetPixelCount === 0) continue;

    // Draw occluder buildings (footprint + height extent) on top
    const occluderCanvas = document.createElement('canvas');
    occluderCanvas.width = sw;
    occluderCanvas.height = sh;
    const occCtx = occluderCanvas.getContext('2d')!;

    for (const occ of occluders) {
      occCtx.fillStyle = '#ffffff';
      // Draw footprint
      occCtx.beginPath();
      occCtx.moveTo(occ.pixels[0].x * scale, occ.pixels[0].y * scale);
      for (let i = 1; i < occ.pixels.length; i++) {
        occCtx.lineTo(occ.pixels[i].x * scale, occ.pixels[i].y * scale);
      }
      // Extend upward with roof pixels for 3D height
      if (occ.roofPixels.length >= 3) {
        for (const p of occ.roofPixels) {
          occCtx.lineTo(p.x * scale, p.y * scale);
        }
      }
      occCtx.closePath();
      occCtx.fill();
    }

    // Check overlap: how many target pixels are covered by occluders
    const occData = occCtx.getImageData(0, 0, sw, sh).data;
    let coveredCount = 0;
    for (let i = 0; i < targetData.length; i += 4) {
      if (targetData[i] > 128 && occData[i] > 128) coveredCount++;
    }

    const coverageRatio = coveredCount / targetPixelCount;
    if (coverageRatio >= threshold) {
      occluded.add(target.zone.id || '');
      console.log(`[GlobeAIRender] Occlusion: "${target.zone.name || target.zone.zone_type}" is ${(coverageRatio * 100).toFixed(0)}% occluded — CULLED from prompt`);
    }
  }

  if (occluded.size > 0) {
    console.log(`[GlobeAIRender] Occlusion culling: ${occluded.size} zone(s) removed from render`);
  }

  return occluded;
}

/**
 * Generate a COLOR-CODED mask from zone polygons.
 * Each zone drawn in its actual map color so Gemini can match the COLOR-TO-ZONE legend.
 * Black = keep as-is, colored = render this zone.
 */
function generateMask(
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

  // If site boundary exists, clip all zone rendering to within it
  const siteBoundary = zones.find(z => z.zone_type === 'site_boundary' && z.coordinates?.length >= 3);
  if (siteBoundary) {
    const boundaryPixels = siteBoundary.coordinates
      .map(c => projectToPixels(c[0], c[1], terrainHeight, camera, width, height))
      .filter(Boolean) as { x: number; y: number }[];

    if (boundaryPixels.length >= 3) {
      ctx.save();
      ctx.beginPath();
      ctx.moveTo(boundaryPixels[0].x, boundaryPixels[0].y);
      for (let i = 1; i < boundaryPixels.length; i++) ctx.lineTo(boundaryPixels[i].x, boundaryPixels[i].y);
      ctx.closePath();
      ctx.clip(); // All subsequent drawing is clipped to the boundary
      console.log(`[GlobeAIRender] Mask clipped to site boundary (${boundaryPixels.length} vertices)`);
    }
  }

  // Draw each zone as WHITE (binary mask) with ~2m dilation — skip site_boundary
  // Binary mask: white = edit area, black = preserve. No colors in the mask.
  // Zone identification comes from the colored polygons already visible in the
  // screenshot + prompt text + archetype reference images.
  // The dilation gives Gemini "peripheral vision" to see adjacent context.
  const DILATION_PX = 8; // ~2m at typical aerial zoom
  ctx.fillStyle = '#ffffff';
  ctx.strokeStyle = '#ffffff';
  ctx.lineWidth = DILATION_PX * 2;
  ctx.lineJoin = 'round';

  for (const zone of zones) {
    if (!zone.coordinates || zone.coordinates.length < 3) continue;
    if (zone.zone_type === 'site_boundary') continue;

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
    ctx.stroke(); // Dilation: thick white stroke adds ~2m bleed room
  }

  // Restore context (remove clip)
  if (siteBoundary) ctx.restore();

  return canvas.toDataURL('image/png').split(',')[1];
}

/**
 * Compress an image blob to JPEG at a target max width.
 * Returns base64 string without data URI prefix.
 */
function compressImage(blob: Blob, maxWidth = 512, quality = 0.7): Promise<string> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      const scale = Math.min(1, maxWidth / img.naturalWidth);
      const w = Math.round(img.naturalWidth * scale);
      const h = Math.round(img.naturalHeight * scale);

      const canvas = document.createElement('canvas');
      canvas.width = w;
      canvas.height = h;
      const ctx = canvas.getContext('2d')!;
      ctx.drawImage(img, 0, 0, w, h);

      canvas.toBlob((outBlob) => {
        if (!outBlob) return reject(new Error('Compression failed'));
        const reader = new FileReader();
        reader.onloadend = () => resolve((reader.result as string).split(',')[1]);
        reader.readAsDataURL(outBlob);
      }, 'image/jpeg', quality);
    };
    img.onerror = () => reject(new Error('Failed to load image for compression'));
    img.src = URL.createObjectURL(blob);
  });
}

/**
 * Collect archetype reference card images for multi-image rendering.
 * Returns up to 6 images, compressed to ~30-50KB JPEG each.
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

    if (!archetypeId) {
      console.log(`[GlobeAIRender] Skipping zone "${zone.name || zone.zone_type}" — no archetype ID`);
      continue;
    }

    const entry = catalog.find((a: any) => a.id === archetypeId || archetypeId.startsWith(a.id + '_'));
    if (!entry) {
      console.log(`[GlobeAIRender] Skipping zone "${zone.name || zone.zone_type}" — archetype "${archetypeId}" not found in catalog`);
      continue;
    }
    if (!entry.thumbnailUrl) {
      console.log(`[GlobeAIRender] Skipping zone "${zone.name || zone.zone_type}" — archetype "${archetypeId}" has no thumbnailUrl`);
      continue;
    }

    // Fetch and compress the card image (512px wide JPEG ~30-50KB)
    try {
      const resp = await fetch(entry.thumbnailUrl);
      if (!resp.ok) continue;
      const blob = await resp.blob();
      const base64 = await compressImage(blob, 512, 0.7);

      const sizeKB = Math.round(base64.length * 0.75 / 1024);
      console.log(`[GlobeAIRender] Archetype image: ${entry.title} — ${sizeKB}KB (compressed)`);

      images.push({
        image_base64: base64,
        label: entry.title || archetypeId,
        zone_color: colorName(resolveZoneColor(zone)),
      });
    } catch { /* skip failed fetches */ }
  }

  return images;
}

// ─── COLOR NAMING ──────────────────────────────────────────────────────

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
 * Map hex color to a visually descriptive, unique name for prompts.
 * Uses specific color vocabulary so Gemini can distinguish similar shades.
 * Always includes the hex value for precise matching.
 */
function colorName(hex: string): string {
  const normalized = hex.toLowerCase();
  const knownNames: Record<string, string> = {
    '#e03c31': 'bright vermillion',
    '#ff6b6b': 'light coral pink',
    '#e8927c': 'warm salmon',
    '#f5a623': 'vivid amber',
    '#ffd700': 'bright gold',
    '#ffeb3b': 'lemon yellow',
    '#f0e68c': 'pale khaki',
    '#4caf50': 'medium green',
    '#66bb6a': 'fresh spring green',
    '#2e7d32': 'deep forest green',
    '#009688': 'dark teal',
    '#4169e1': 'royal blue',
    '#3f51b5': 'deep indigo',
    '#2196f3': 'sky blue',
    '#9c27b0': 'rich purple',
    '#795548': 'warm brown',
    '#607d8b': 'cool blue-grey',
    '#bdbdbd': 'light silver',
    '#c62828': 'deep maroon',
    '#d84315': 'burnt sienna',
    '#ad1457': 'dark magenta',
    '#6a1b9a': 'deep violet',
    '#4527a0': 'dark royal purple',
    '#b71c1c': 'dark crimson',
    '#e65100': 'dark burnt orange',
    '#ff5722': 'bright orange-red',
    '#ff9800': 'bright orange',
    '#8bc34a': 'lime green',
    '#00bcd4': 'bright cyan',
    '#e91e63': 'hot pink',
    '#ff7043': 'warm tangerine',
    '#a1887f': 'dusty mauve',
    '#90a4ae': 'steel grey',
  };

  const name = knownNames[normalized];
  if (name) return `${name} ${hex}`;

  try {
    const [h, s, l] = hexToHsl(hex);
    const lightDesc = l < 25 ? 'very dark ' : l < 40 ? 'dark ' : l > 75 ? 'very light ' : l > 60 ? 'light ' : '';
    const satDesc = s < 20 ? 'muted ' : s > 80 ? 'vivid ' : '';
    let hueName = 'brown';
    if (h < 10 || h >= 350) hueName = 'red';
    else if (h < 20) hueName = 'red-orange';
    else if (h < 35) hueName = 'orange';
    else if (h < 50) hueName = 'amber-orange';
    else if (h < 65) hueName = 'golden yellow';
    else if (h < 80) hueName = 'yellow-green';
    else if (h < 140) hueName = 'green';
    else if (h < 170) hueName = 'teal-green';
    else if (h < 200) hueName = 'cyan';
    else if (h < 230) hueName = 'blue';
    else if (h < 260) hueName = 'blue-violet';
    else if (h < 290) hueName = 'purple';
    else if (h < 320) hueName = 'magenta';
    else if (h < 350) hueName = 'rose';
    return `${lightDesc}${satDesc}${hueName} ${hex}`;
  } catch {
    return hex;
  }
}

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
 */
function getZoneArchetypeInfo(zone: SiteZone): {
  archetypeTitle?: string;
  facadeDescription?: string;
  roofDescription?: string;
  materials?: string;
  aerialAppearance?: string;
  publicRealm?: string;
  colorScheme?: string;
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
    if (fd.groundFloor) facadeParts.push(fd.groundFloor);
    if (fd.upperFloors) facadeParts.push(fd.upperFloors);
    if (fd.colorScheme) facadeParts.push(fd.colorScheme);

    const roofParts: string[] = [];
    if (rd.form) roofParts.push(rd.form);
    if (rd.material) roofParts.push(rd.material);
    if (rd.aerialAppearance) roofParts.push(rd.aerialAppearance);

    return {
      archetypeTitle: entry.title,
      facadeDescription: facadeParts.join(', ') || undefined,
      roofDescription: roofParts.join(', ') || undefined,
      materials: Array.isArray(sp.materials) ? sp.materials.join(', ') : sp.materials,
      aerialAppearance: rd.aerialAppearance || undefined,
      publicRealm: sp.publicRealm || undefined,
      colorScheme: fd.colorScheme || undefined,
    };
  }
  return {};
}

/**
 * Build SCHEMA-style structured prompt for aerial renders.
 * Based on the proven Mapbox aerial prompt structure.
 */
function buildPrompt(zones: SiteZone[], style: string, camera?: THREE.Camera, terrainHeight?: number): string {
  // --- STYLE ---
  const stylePrompts: Record<string, string> = {
    photorealistic: 'Photorealistic architectural visualization, photomontage quality, golden hour afternoon sunlight, sharp detail on materials and facades.',
    winter: 'Photorealistic winter scene with fresh snow on roofs and ground, bare deciduous trees, cool winter afternoon light, frost on surfaces. Snow-covered roofs, frosted ground plane, bare deciduous trees, evergreens with heavy snow-load.',
    atmospheric: 'Dramatic golden hour, low-angle warm sun, long architectural shadows, volumetric haze, warm orange light from the west.',
    spring: 'Photorealistic spring scene, fresh green foliage on trees, cherry blossoms, bright midday sunlight, vivid colors.',
    night: 'Nighttime scene, city lights, warm interior glow from windows, moonlit sky, wet reflective streets.',
  };

  // --- CAMERA ANGLE ---
  let pitchDesc = 'oblique aerial (~50°)';
  if (camera && terrainHeight != null) {
    // Estimate pitch from camera direction vs surface normal
    const camDir = new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion).normalize();
    const camPos = camera.position.clone().normalize(); // surface normal at camera position
    const cosAngle = Math.abs(camDir.dot(camPos.clone().negate()));
    const pitchDeg = Math.round(Math.acos(Math.min(1, cosAngle)) * 180 / Math.PI);
    if (pitchDeg < 20) pitchDesc = `near top-down (~${pitchDeg}°)`;
    else if (pitchDeg < 40) pitchDesc = `steep aerial (~${pitchDeg}°)`;
    else if (pitchDeg < 60) pitchDesc = `oblique aerial (~${pitchDeg}°)`;
    else pitchDesc = `low-angle oblique (~${pitchDeg}°)`;
    console.log(`[GlobeAIRender] Camera pitch: ${pitchDeg}° → "${pitchDesc}"`);
  }

  // --- COMPOSITION ---
  const hasBuildings = zones.some(z => z.zone_type === 'building' || z.zone_type === 'residential');
  const composition = hasBuildings
    ? `${pitchDesc} view from 3D photorealistic city model, colored polygons mark proposed zones on the existing photographic context. Render buildings with correct 3D perspective for this viewing angle.`
    : `${pitchDesc} view, ground-level zones only on photorealistic 3D terrain.`;

  // --- LIGHTING ---
  const lightingMap: Record<string, string> = {
    photorealistic: 'Golden hour, warm southwest sun, crisp architectural shadows.',
    winter: 'Soft diffuse winter daylight, low sun angle, long blue-tinted shadows, pale blue-grey overcast sky.',
    atmospheric: 'Dramatic golden hour, low-angle warm sun, long architectural shadows, volumetric haze.',
    spring: 'Bright spring midday sun, vivid colors, fresh green light.',
    night: 'Moonlight and city glow, artificial lighting, warm window light.',
  };

  // --- ZONES (SCHEMA format) — skip site_boundary ---
  const renderZones = zones.filter(z => z.zone_type !== 'site_boundary');
  const zoneLines: string[] = [];
  for (let i = 0; i < renderZones.length; i++) {
    const zone = renderZones[i];
    const color = colorName(resolveZoneColor(zone));
    const props = zone.properties || {};
    const info = getZoneArchetypeInfo(zone);

    const floors = (props.floors as number) || 0;
    const heightM = (props.height_m as number) || (props.height as number) || floors * 3.2 || 0;
    const name = info.archetypeTitle || zone.name || ZONE_TYPE_CONFIG[zone.zone_type]?.label || zone.zone_type;

    // Scale descriptor
    let scale = '';
    if (zone.zone_type === 'building' || zone.zone_type === 'residential') {
      if (floors > 0 && heightM > 0) scale = `${floors}F ${Math.round(heightM)}m`;
      else if (floors > 0) scale = `${floors}F`;
      else if (heightM > 0) scale = `${Math.round(heightM)}m`;
      else scale = 'multi-story';
    } else {
      scale = 'gnd';
    }

    // Map overlay prompt (archetype-specific aerial rendering instruction)
    const overlayPrompt = getMapOverlayPrompt(zone);

    // Feature keywords from archetype metadata
    const features: string[] = [];
    if (overlayPrompt) {
      // Use the archetype's own rendering instruction if available
      features.push(overlayPrompt);
    } else {
      if (info.facadeDescription) features.push(info.facadeDescription);
      if (info.roofDescription) features.push(info.roofDescription);
      if (info.materials) features.push(info.materials);
      if (info.aerialAppearance) features.push(`Aerial: ${info.aerialAppearance}`);
      if (info.publicRealm) features.push(info.publicRealm);
    }

    // User description override
    const userDesc = (props.description as string) || (props.descriptive_text as string) || '';
    if (userDesc.length > 10) features.push(userDesc);

    const featureStr = features.join(', ').substring(0, 200);
    zoneLines.push(`${i + 1}. [${color}] ${name} | ${scale} | ${featureStr || 'render as described'}`);
  }

  // --- ASSEMBLE SCHEMA PROMPT ---
  const sections = [
    `STYLE: ${stylePrompts[style] || stylePrompts.photorealistic}`,
    `COMPOSITION: ${composition}`,
    `LIGHTING: ${lightingMap[style] || lightingMap.photorealistic}`,
    `CONTEXT: This image is captured from a 3D photorealistic city model with real Google Earth buildings. Preserve ALL unmasked photographic context exactly as-is. Rendered zones must blend naturally at edges — match tones, lighting, and scale of adjacent real buildings.`,
    `COLOR TEMPERATURE MATCHING: Analyze the color temperature and atmospheric conditions of the EXISTING buildings and terrain in the photograph. Match the EXACT same warm/cool tone, haze level, and ambient light color on all rendered zones. If the scene has golden-hour warmth, render buildings with the same warm amber tones — NOT neutral daylight grey. Rendered materials must look like they exist in the same atmosphere and light as the surrounding real buildings.`,
    `ATMOSPHERIC PERSPECTIVE: Apply the same atmospheric haze and aerial perspective visible on surrounding buildings at similar distances. Distant rendered zones should have reduced contrast and shifted color matching the existing depth cues in the photograph.`,
    `NUMERICAL INVENTORY: This scene contains exactly ${renderZones.length} zone${renderZones.length > 1 ? 's' : ''}: ${renderZones.filter(z => z.zone_type === 'building' || z.zone_type === 'residential').length} building${renderZones.filter(z => z.zone_type === 'building' || z.zone_type === 'residential').length !== 1 ? 's' : ''}, ${renderZones.filter(z => z.zone_type === 'green_space').length} park${renderZones.filter(z => z.zone_type === 'green_space').length !== 1 ? 's' : ''}, ${renderZones.filter(z => z.zone_type === 'road').length} road${renderZones.filter(z => z.zone_type === 'road').length !== 1 ? 's' : ''}.`,
    `ZONES:\n${zoneLines.join('\n')}`,
    `MANDATORY: The white mask shows the EXACT area to edit. Replace the colored polygon overlays visible in the screenshot with photorealistic architectural materials. Each colored polygon in the screenshot corresponds to a zone in the ZONES list above — match by color. Realistic rooftop materials, facades, and landscaping. Match scale and density of surrounding real 3D buildings. Rendered building facades and roofs MUST have the same color cast, warmth, and atmospheric tint as adjacent real buildings.`,
    `PROHIBITIONS: colored polygon fills visible on ANY rendered surface (rooftops, facades, ground), boundary lines or outlines visible, text overlays, watermarks, color temperature mismatch between rendered and existing buildings, rendered buildings appearing unnaturally crisp or clean compared to surroundings${style === 'winter' ? ', lush green vegetation, summer foliage, bright green lawns' : ''}`,
    `SITE BOUNDARY: Do NOT add any NEW buildings, structures, roads, people, vehicles, or landscaping outside the colored zone polygons. However, rendered zones MUST blend seamlessly into the surrounding landscape at their edges — match lighting, ground plane, and context so there is no visible seam between rendered and existing areas.`,
    `OCCLUSION: Some zones may be partially or fully hidden behind taller buildings from this camera angle. This is CORRECT — do NOT distort the perspective to make hidden zones visible. If a zone is occluded by a building in front of it, leave it hidden. Render only what would naturally be visible from this specific camera position and angle.`,
    `FINAL CONSTRAINT: Stay strictly within each colored zone polygon. Do not alter pixels outside the mask. Accuracy to the polygon boundary is more important than architectural flair. Each zone renders ONLY within its own colored boundary — never overlapping into adjacent zones.`,
  ];

  return sections.join('\n');
}

// ─── POST-PROCESSING: POLYGON CLIP ─────────────────────────────────────

/**
 * Load an image from a data URI and return an HTMLImageElement.
 */
function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = (e) => reject(new Error(`Failed to load image: ${e}`));
    img.src = src;
  });
}

/**
 * Post-process: clip the AI render to zone polygons with feathered edges.
 * For each zone, only keep the AI render within that zone's polygon
 * (with a soft 6px blur feather). Everything outside zone polygons
 * reverts to the original screenshot.
 *
 * This is the "fail-safe" — no matter what Gemini produces, each zone
 * only shows within its polygon boundary.
 */
async function clipRenderToZones(
  originalBase64: string,
  renderedBase64: string,
  zones: SiteZone[],
  camera: THREE.Camera,
  canvasWidth: number,
  canvasHeight: number,
  terrainHeight: number,
): Promise<string> {
  const [origImg, rendImg] = await Promise.all([
    loadImage(`data:image/png;base64,${originalBase64}`),
    loadImage(`data:image/png;base64,${renderedBase64}`),
  ]);

  const w = origImg.naturalWidth;
  const h = origImg.naturalHeight;

  // Start with the original screenshot as the base
  const resultCanvas = document.createElement('canvas');
  resultCanvas.width = w;
  resultCanvas.height = h;
  const resultCtx = resultCanvas.getContext('2d')!;
  resultCtx.drawImage(origImg, 0, 0, w, h);

  // Build a combined feathered mask for ALL non-boundary zones
  const maskCanvas = document.createElement('canvas');
  maskCanvas.width = w;
  maskCanvas.height = h;
  const maskCtx = maskCanvas.getContext('2d')!;
  maskCtx.fillStyle = '#000000';
  maskCtx.fillRect(0, 0, w, h);
  maskCtx.fillStyle = '#ffffff';

  for (const zone of zones) {
    if (!zone.coordinates || zone.coordinates.length < 3) continue;
    if (zone.zone_type === 'site_boundary') continue;

    const pixels = zone.coordinates
      .map(c => projectToPixels(c[0], c[1], terrainHeight, camera, canvasWidth, canvasHeight))
      .filter(Boolean) as { x: number; y: number }[];
    if (pixels.length < 3) continue;

    // Draw zone polygon
    maskCtx.beginPath();
    maskCtx.moveTo(pixels[0].x, pixels[0].y);
    for (let i = 1; i < pixels.length; i++) maskCtx.lineTo(pixels[i].x, pixels[i].y);
    maskCtx.closePath();
    maskCtx.fill();

    // For buildings, extend upward for 3D height
    const buildingHeight = (zone.properties?.height_m as number)
      || (zone.properties?.height as number)
      || ((zone.properties?.floors as number) || 0) * 3.2 || 0;

    if (buildingHeight > 0 && (zone.zone_type === 'building' || zone.zone_type === 'residential')) {
      const topPixels = zone.coordinates
        .map(c => projectToPixels(c[0], c[1], terrainHeight + buildingHeight, camera, canvasWidth, canvasHeight))
        .filter(Boolean) as { x: number; y: number }[];

      if (topPixels.length >= 3) {
        // Draw expanded rectangle from footprint top to roof top
        const minY = Math.min(...pixels.map(p => p.y));
        const minX = Math.min(...pixels.map(p => p.x));
        const maxX = Math.max(...pixels.map(p => p.x));
        const roofMinY = Math.min(...topPixels.map(p => p.y));
        maskCtx.fillRect(minX, roofMinY, maxX - minX, minY - roofMinY);
      }
    }
  }

  // Apply feathered blur to mask edges (6px)
  const featherCanvas = document.createElement('canvas');
  featherCanvas.width = w;
  featherCanvas.height = h;
  const featherCtx = featherCanvas.getContext('2d')!;
  featherCtx.filter = 'blur(6px)';
  featherCtx.drawImage(maskCanvas, 0, 0);

  // Composite: AI render masked with feathered zones, drawn onto original
  const aiCanvas = document.createElement('canvas');
  aiCanvas.width = w;
  aiCanvas.height = h;
  const aiCtx = aiCanvas.getContext('2d')!;
  aiCtx.drawImage(rendImg, 0, 0, w, h);
  aiCtx.globalCompositeOperation = 'destination-in';
  aiCtx.drawImage(featherCanvas, 0, 0);

  // Draw the masked AI render on top of the original
  resultCtx.drawImage(aiCanvas, 0, 0);

  console.log('[GlobeAIRender] Post-process: clipped render to zone polygons with 6px feathered edges');
  return resultCanvas.toDataURL('image/png').split(',')[1];
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

      // 1b. Occlusion culling — remove zones hidden behind taller buildings
      const occludedIds = findOccludedZones(zones, camera, canvas.width, canvas.height, terrainHeight);
      const visibleZones = occludedIds.size > 0
        ? zones.filter(z => !occludedIds.has(z.id || ''))
        : zones;

      // 2. Generate binary mask from VISIBLE zone polygons only
      console.log('[GlobeAIRender] Generating mask...');
      const maskBase64 = generateMask(visibleZones, camera, canvas.width, canvas.height, terrainHeight);

      // 3. Build SCHEMA prompt from VISIBLE zone archetypes only
      let prompt = buildPrompt(visibleZones, style, camera, terrainHeight);
      if (customPrompt) prompt += `\nADDITIONAL: ${customPrompt}`;

      // 4. Collect archetype reference card images (up to 6, compressed to ~30-50KB JPEG each)
      console.log('[GlobeAIRender] Collecting archetype reference images...');
      const archetypeImages = await collectArchetypeImages(visibleZones);
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
        console.log('[GlobeAIRender] Render complete! Applying polygon clip...');

        // Post-process: clip the AI render to zone polygons with feathered edges
        // This ensures no zone bleeds into adjacent zones or outside boundaries
        const clippedBase64 = await clipRenderToZones(
          imageBase64, resp.data.image_base64,
          visibleZones, camera, canvas.width, canvas.height, terrainHeight,
        );

        return {
          imageUrl: `data:image/png;base64,${clippedBase64}`,
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

  return { render, captureStreetView, isRenderingRef };
}
