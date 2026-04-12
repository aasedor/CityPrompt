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
function buildPrompt(zones: SiteZone[], style: string): string {
  // --- STYLE ---
  const stylePrompts: Record<string, string> = {
    photorealistic: 'Photorealistic architectural visualization, photomontage quality, golden hour afternoon sunlight, sharp detail on materials and facades.',
    winter: 'Photorealistic winter scene with fresh snow on roofs and ground, bare deciduous trees, cool winter afternoon light, frost on surfaces. Snow-covered roofs, frosted ground plane, bare deciduous trees, evergreens with heavy snow-load.',
    atmospheric: 'Dramatic golden hour, low-angle warm sun, long architectural shadows, volumetric haze, warm orange light from the west.',
    spring: 'Photorealistic spring scene, fresh green foliage on trees, cherry blossoms, bright midday sunlight, vivid colors.',
    night: 'Nighttime scene, city lights, warm interior glow from windows, moonlit sky, wet reflective streets.',
  };

  // --- COMPOSITION ---
  const hasBuildings = zones.some(z => z.zone_type === 'building' || z.zone_type === 'residential');
  const composition = hasBuildings
    ? 'Oblique aerial view from 3D photorealistic city model, colored polygons mark proposed zones on the existing photographic context.'
    : 'Oblique aerial view, ground-level zones only on photorealistic 3D terrain.';

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
    `MANDATORY: Each zone renders ONLY within its colored polygon boundary. Realistic rooftop materials — no colored polygon fill visible. Replace ALL colored overlays with appropriate architectural materials. Match scale and density of surrounding real 3D buildings. Rendered building facades and roofs MUST have the same color cast, warmth, and atmospheric tint as adjacent real buildings.`,
    `PROHIBITIONS: buildings extending beyond polygon boundaries, colored polygon fills visible on rooftops or facades, boundary lines visible, text overlays, watermarks, color temperature mismatch between rendered and existing buildings, rendered buildings appearing unnaturally crisp or clean compared to surroundings${style === 'winter' ? ', lush green vegetation, summer foliage, bright green lawns' : ''}`,
    `CRITICAL FINAL INSTRUCTION: Do NOT modify ANY pixels outside the colored polygon zones. Every existing building, house, tree, road, car, and terrain feature outside the zones MUST remain pixel-perfect identical to the input photograph. The white mask defines the EXACT boundary — nothing renders outside it.`,
  ];

  return sections.join('\n');
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
      const maskBase64 = generateMask(zones, camera, canvas.width, canvas.height, terrainHeight);

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
