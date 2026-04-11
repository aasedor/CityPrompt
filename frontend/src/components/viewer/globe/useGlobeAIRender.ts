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

const DEG_TO_RAD = Math.PI / 180;
const catalog = (archetypeCatalog as any)?.archetypes as any[] | undefined;

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
 * Generate a binary mask from zone polygons.
 * White = zone area (to be replaced by AI), Black = keep as-is.
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

  // Draw each zone as white
  ctx.fillStyle = '#ffffff';
  for (const zone of zones) {
    if (!zone.coordinates || zone.coordinates.length < 3) continue;

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

  // --- ZONES (SCHEMA format) ---
  const zoneLines: string[] = [];
  for (let i = 0; i < zones.length; i++) {
    const zone = zones[i];
    const color = resolveZoneColor(zone);
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

    // Feature keywords from archetype metadata
    const features: string[] = [];
    if (info.facadeDescription) features.push(info.facadeDescription);
    if (info.roofDescription) features.push(info.roofDescription);
    if (info.materials) features.push(info.materials);
    if (info.aerialAppearance) features.push(`Aerial: ${info.aerialAppearance}`);
    if (info.publicRealm) features.push(info.publicRealm);

    // User description override
    const userDesc = (props.description as string) || (props.descriptive_text as string) || '';
    if (userDesc.length > 10) features.push(userDesc);

    const featureStr = features.join(', ').substring(0, 160);
    zoneLines.push(`${i + 1}. [${color}] ${name} | ${scale} | ${featureStr || 'render as described'}`);
  }

  // --- ASSEMBLE SCHEMA PROMPT ---
  const sections = [
    `STYLE: ${stylePrompts[style] || stylePrompts.photorealistic}`,
    `COMPOSITION: ${composition}`,
    `LIGHTING: ${lightingMap[style] || lightingMap.photorealistic}`,
    `CONTEXT: This image is captured from a 3D photorealistic city model with real Google Earth buildings. Preserve ALL unmasked photographic context exactly as-is. Rendered zones must blend naturally at edges — match tones, lighting, and scale of adjacent real buildings.`,
    `NUMERICAL INVENTORY: This scene contains exactly ${zones.length} zone${zones.length > 1 ? 's' : ''}: ${zones.filter(z => z.zone_type === 'building' || z.zone_type === 'residential').length} building${zones.filter(z => z.zone_type === 'building' || z.zone_type === 'residential').length !== 1 ? 's' : ''}, ${zones.filter(z => z.zone_type === 'green_space').length} park${zones.filter(z => z.zone_type === 'green_space').length !== 1 ? 's' : ''}, ${zones.filter(z => z.zone_type === 'road').length} road${zones.filter(z => z.zone_type === 'road').length !== 1 ? 's' : ''}.`,
    `ZONES:\n${zoneLines.join('\n')}`,
    `MANDATORY: Each zone renders ONLY within its colored polygon boundary on the white mask. Realistic rooftop materials — no colored polygon fill visible on any surface. Replace ALL colored overlays with appropriate architectural materials. New buildings must match the scale and density of surrounding real 3D buildings.`,
    `PROHIBITIONS: buildings extending beyond polygon boundaries, colored polygon fills visible on rooftops or facades, boundary lines or outlines visible in final image, text overlays or watermarks${style === 'winter' ? ', lush green vegetation on deciduous trees, summer foliage, bright green lawns' : ''}`,
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

      // 3. Build prompt from zone archetypes
      let prompt = buildPrompt(zones, style);
      if (customPrompt) prompt += ` Additional instructions: ${customPrompt}`;
      console.log('[GlobeAIRender] Prompt:', prompt.substring(0, 200) + '...');

      // 4. Send to backend render API
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
