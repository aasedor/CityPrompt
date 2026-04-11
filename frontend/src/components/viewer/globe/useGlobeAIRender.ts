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
import { api } from '@/services/api';

const DEG_TO_RAD = Math.PI / 180;

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
 * Build a simple prompt from zone archetypes.
 */
function buildPrompt(zones: SiteZone[], style: string): string {
  const zoneDescriptions: string[] = [];

  for (const zone of zones) {
    const props = zone.properties || {};
    const archetypeId = (props.development_subcategory as string)
      || (props.green_space_subcategory as string)
      || (props.road_subcategory as string)
      || (props.plaza_subcategory as string)
      || (props.development_archetype_id as string)
      || (props.green_space_archetype_id as string)
      || '';

    const height = (props.height_m as number) || (props.height as number) || ((props.floors as number) || 0) * 3.2 || 0;
    const name = zone.name || archetypeId.replace(/_/g, ' ') || zone.zone_type;

    let desc = `${name}`;
    if (height > 0) desc += ` (${Math.round(height)}m tall)`;
    zoneDescriptions.push(desc);
  }

  const stylePrompts: Record<string, string> = {
    photorealistic: 'Photorealistic architectural visualization, photomontage quality, golden hour afternoon sunlight, sharp detail on materials and facades.',
    winter: 'Photorealistic winter scene with fresh snow on roofs and ground, bare deciduous trees, cool winter afternoon light, frost on surfaces.',
    atmospheric: 'Photorealistic dusk scene, warm orange sunset light from the west, long shadows, building windows glowing warm, twilight sky.',
    spring: 'Photorealistic spring scene, fresh green foliage on trees, cherry blossoms, bright midday sunlight, vivid colors, people enjoying the outdoors.',
    night: 'Photorealistic nighttime scene, city lights illuminating the scene, warm interior glow from windows, moonlit sky, wet reflective streets.',
  };
  const stylePrompt = stylePrompts[style] || stylePrompts.photorealistic;

  return `This is a hybrid spatial blueprint captured from a 3D photorealistic city model. Areas with photographic textures are existing real-world context — strictly preserve their geometry, appearance, and lighting. The white masked areas are new architectural interventions — render these as: ${zoneDescriptions.join('; ')}. ${stylePrompt} Match the lighting, shadows, and perspective of the surrounding 3D photograph exactly. CRITICAL: Only modify pixels within the white masked areas. Do NOT alter, extend, or bleed outside the mask boundary. All existing buildings, roads, trees, and terrain outside the mask must remain pixel-perfect identical to the input image.`;
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
    flyToStreetLevel: (lat: number, lng: number, heading: number, terrainH: number) => void,
    restoreAerialView: (state: any) => void,
    saveCameraState: () => any,
  ): Promise<string | null> => {
    // Save current camera state
    const savedState = saveCameraState();
    if (!savedState) return null;

    try {
      // Move camera to street level
      flyToStreetLevel(lat, lng, headingDeg, terrainHeight);

      // Wait for tiles to load at new LOD (street level needs higher detail)
      // Multiple frames to ensure the renderer processes the new camera position
      for (let i = 0; i < 5; i++) {
        await new Promise(r => requestAnimationFrame(r));
      }
      // Additional wait for tile streaming
      await new Promise(r => setTimeout(r, 3000));
      // A few more frames for the final render
      for (let i = 0; i < 3; i++) {
        await new Promise(r => requestAnimationFrame(r));
      }

      // Capture the street-level view
      console.log('[GlobeAIRender] Capturing street-level view...');
      const imageBase64 = await captureCanvasBase64(canvas);

      return imageBase64 || null;
    } finally {
      // Always restore the camera
      restoreAerialView(savedState);
    }
  }, []);

  return { render, captureStreetView, isRenderingRef };
}
