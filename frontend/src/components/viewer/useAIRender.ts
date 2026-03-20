/**
 * useAIRender — React hook for the Vertex AI Imagen 3 render pipeline.
 *
 * Sends a map screenshot (with colored zone polygon overlays) and a structured
 * prompt to the backend, which proxies the request to Google Cloud Vertex AI
 * Imagen 3 for photorealistic architectural rendering.
 *
 * The pipeline relies on Imagen 3's native inpaint-insertion mode: colored
 * polygons in the screenshot serve as spatial guides, and a structured prompt
 * maps each color to its archetype description.
 */
import { useState, useCallback, useRef } from 'react';
import axios from 'axios';
import mapboxgl from 'mapbox-gl';
import type { Map as MapboxMap } from 'mapbox-gl';
import type { SiteZone } from '@/types';
import { ZONE_TYPE_CONFIG } from '@/types';
import archetypeCatalog from '@/data/buildingArchetypes.json';
import { getArchetypeForShade } from '@/data/archetypeShadeMap';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface AIRenderStyle {
  id: string;
  label: string;
  prompt: string;
  /** Optional negative prompt fragments */
  negative?: string;
  /** img2img strength override for this style (0–1). Higher = more transformation. */
  strength?: number;
}

export interface AIRenderOptions {
  /** Style preset id — maps to a prompt template */
  style?: string;
  /** Free-form prompt appended after the style prompt */
  customPrompt?: string;
  /** 0–1 — how closely the AI follows the source image (strength) */
  controlStrength?: number;
  /** Number of denoising steps (20–35 recommended) */
  steps?: number;
  /** Guidance scale */
  guidanceScale?: number;
  /** Optional reference image URL or data-URI for style transfer */
  referenceImageUrl?: string;
  /** Reference strength (0–1) */
  referenceStrength?: number;
  /** Archetype positive prompt — appended to the style prompt */
  archetypePrompt?: string;
  /** Archetype negative prompt — appended to the negative prompt */
  archetypeNegative?: string;
  /** Reference image URLs from archetype selections */
  referenceImageUrls?: string[];
  /** Explicit seed for reproducibility */
  seed?: number;
  /** Override output image dimensions */
  imageSize?: { width: number; height: number } | string;
  /** Render style id — alias for style, used by expanded catalog */
  renderStyleId?: string;
  /**
   * Map-overlay prompt from enriched archetype metadata.
   * When set, this replaces the generic style preset prompt entirely.
   */
  mapOverlayPrompt?: string;
  /** Negative prompt from enriched archetype renderPrompt */
  mapOverlayNegative?: string;
  /**
   * Site boundary polygon in geographic coordinates [[lng, lat], ...].
   * Used for boundary-aware prompt generation.
   */
  siteBoundaryCoords?: number[][];
  /**
   * All site zones — used for structured zone-by-zone prompt generation.
   */
  siteZones?: SiteZone[];
}

export interface AIRenderResult {
  /** URL or data-URI of the generated image */
  imageUrl: string;
  /** Geographic bounds at the time of capture: [[W,N],[E,N],[E,S],[W,S]] */
  bounds: [[number, number], [number, number], [number, number], [number, number]];
  /** Seed used for generation */
  seed?: number;
  /** The prompt that was actually sent */
  prompt: string;
}

/** A single face render with its bearing label */
export interface FaceRender {
  label: 'front' | 'right' | 'rear' | 'left';
  bearing: number;
  result: AIRenderResult;
}

export interface UseAIRenderReturn {
  /** Trigger a single render at the current camera position */
  render: (map: MapboxMap, options?: AIRenderOptions) => Promise<AIRenderResult | null>;
  /**
   * Zone-targeted render: zooms to the building zone, captures, renders,
   * overlays only that area. Pass the zone's polygon coordinates [[lng,lat],...].
   */
  renderZone: (map: MapboxMap, zoneCoords: number[][], options?: AIRenderOptions) => Promise<AIRenderResult | null>;
  /** Generate 3 preview renders in parallel with different seeds */
  renderPreviews: (map: MapboxMap, options?: AIRenderOptions) => Promise<AIRenderResult[]>;
  /** Generate a full-quality render with a locked seed. */
  renderFull: (map: MapboxMap, options: AIRenderOptions, seed: number, singleView?: boolean) => Promise<AIRenderResult | null>;
  /** 4-face render results — one per bearing */
  faceRenders: FaceRender[];
  /** Whether a render is currently in flight */
  isRendering: boolean;
  /** 0–100 progress estimate (indeterminate: stays at -1 while waiting) */
  progress: number;
  /** Status message for the UI */
  statusMessage: string;
  /** Last successful result (single render or selected preview) */
  result: AIRenderResult | null;
  /** Preview results from renderPreviews */
  previews: AIRenderResult[];
  /** Currently selected preview index (null = none selected) */
  selectedPreviewIndex: number | null;
  /** Set the selected preview index */
  setSelectedPreviewIndex: (index: number | null) => void;
  /** Last error message, if any */
  error: string | null;
  /** Clear the current result / error */
  reset: () => void;
  /**
   * Per-zone sequential rendering: zoom into each zone individually,
   * render with zone-specific mask and prompt, composite results.
   * Higher detail per zone (4-16x more pixels) at the cost of speed.
   */
  renderPerZone: (map: MapboxMap, options?: AIRenderOptions) => Promise<AIRenderResult | null>;
  /** Attach bearing-based face swapping to a map */
  attachFaceSwapping: (map: MapboxMap) => () => void;
}

// ---------------------------------------------------------------------------
// Style presets (kept for UI compatibility — the structured prompt overrides)
// ---------------------------------------------------------------------------

export const AI_RENDER_STYLES: AIRenderStyle[] = [
  // ── Photorealistic Renders ──────────────────────────────────────────────
  {
    id: 'photorealistic',
    label: 'Photorealistic',
    strength: 0.55,
    prompt:
      'ultra-photorealistic DSLR aerial photograph of a completed urban development, sharp focus, accurate brick stone glass and concrete materials with visible grain and texture, precise cast shadows from midday sun at 60 degrees, mature trees with individual leaf clusters, parked cars and street furniture, clear blue sky with small cumulus clouds, neutral 5500K white balance, high dynamic range, architectural photography, 8k',
    negative: 'cartoon, illustration, sketch, painting, artistic, stylized, watercolor, pencil, monochrome, low quality, blurry, text, watermark',
  },
  {
    id: 'drone-photography',
    label: 'Drone Photo',
    strength: 0.58,
    prompt:
      'professional DJI Mavic 3 drone photograph of completed urban development from 80 meters altitude, slight wide-angle barrel distortion at edges, deep depth of field with everything sharp, subtle atmospheric haze on distant objects, desaturated color from atmospheric scattering, comprehensive site context showing neighboring streets and buildings, real-estate aerial survey documentation style, construction-complete, 8k',
    negative: 'cartoon, illustration, sketch, painting, fish-eye, indoor, close-up, low quality, blurry, text, watermark',
  },
  {
    id: 'photomontage',
    label: 'Photomontage',
    strength: 0.52,
    prompt:
      'professional architectural photomontage, proposed buildings seamlessly composited into real satellite photograph, matched sun direction and color temperature with surrounding context, building slightly sharper and cleaner than photographic surroundings, realistic ground plane contact with existing pavement, planning application submission quality, photorealistic, 8k',
    negative: 'cartoon, illustration, sketch, painting, floating buildings, mismatched shadows, low quality, blurry, text, watermark',
  },

  // ── Lighting & Atmosphere ──────────────────────────────────────────────
  {
    id: 'golden-hour',
    label: 'Golden Hour',
    strength: 0.62,
    prompt:
      'cinematic golden hour aerial photograph, warm 3000K amber-orange sunlight from extremely low angle 10 degrees above horizon, very long dramatic shadows stretching across entire ground plane, building facades glowing warm orange, windows reflecting sunset colors, interior warm yellow lights visible through glass, sky gradient from deep orange at horizon through pink to dark blue at zenith, rim lighting on tree edges, wet-look reflective pavement, 8k',
    negative: 'cartoon, illustration, sketch, midday sun, overhead lighting, flat lighting, overcast, cool blue tones, low quality, blurry, text, watermark',
  },
  {
    id: 'night-scene',
    label: 'Night Scene',
    strength: 0.68,
    prompt:
      'aerial night photograph with dark navy-black sky, buildings defined entirely by warm interior lighting glowing through window rectangles, exterior uplighting on key facades, street lamps casting isolated pools of warm light on pavement, dramatic high-contrast between bright windows and dark silhouetted walls, wet reflective pavement with light reflections, subtle blue-hour ambient fill, cool moonlight rim on rooftops, architectural night photography, 8k',
    negative: 'cartoon, illustration, sketch, daytime, bright sunlight, blue sky, green vegetation, flat lighting, low quality, blurry, text, watermark',
  },
  {
    id: 'overcast-soft',
    label: 'Overcast',
    strength: 0.52,
    prompt:
      'aerial photograph under uniform white-grey overcast sky, completely diffused flat lighting with zero harsh shadows, all surfaces evenly illuminated, cool 6500K color temperature with subtle blue-grey cast, saturation reduced 25 percent, accurate material colors without glare or specular highlights, calm muted atmosphere, clean professional survey documentation quality, 8k',
    negative: 'cartoon, illustration, sketch, dramatic lighting, lens flare, golden hour, warm tones, strong shadows, colorful sky, low quality, blurry, text, watermark',
  },

  // ── Seasonal ──────────────────────────────────────────────────────────
  {
    id: 'summer',
    label: 'Summer',
    strength: 0.58,
    prompt:
      'aerial photograph of completed development in peak midsummer, dense fully-leafed deciduous tree canopy in deep saturated greens, lush maintained lawns, vivid blue sky with white cumulus clouds, strong high-angle sun with short crisp shadows, vibrant flower beds, people in summer clothing using outdoor terraces and plazas, active occupied neighbourhood full of life, photorealistic, 8k',
    negative: 'cartoon, illustration, sketch, winter, snow, bare trees, autumn colors, orange leaves, dead grass, low quality, blurry, text, watermark',
  },
  {
    id: 'autumn',
    label: 'Autumn',
    strength: 0.65,
    prompt:
      'aerial photograph of completed development in peak autumn, deciduous trees in rich mix of burnt orange deep red gold amber and russet foliage, scattered fallen leaves covering pathways and lawns, warm low-angle golden sunlight with long afternoon shadows, slight atmospheric haze, warm earth-tone color palette dominating, some trees partially bare showing branch structure, cozy inviting atmosphere, photorealistic, 8k',
    negative: 'cartoon, illustration, sketch, summer green, snow, bare trees only, spring blossoms, low quality, blurry, text, watermark',
  },

  // ── Technical / Planning ──────────────────────────────────────────────
  {
    id: 'massing-study',
    label: 'Massing Study',
    strength: 0.48,
    prompt:
      'architectural white massing model, every surface is uniform matte white plaster with zero material texture, no windows no doors no detail, pure clean geometric volumes showing only mass and proportion, soft studio lighting from upper left, gentle ambient occlusion shadows where forms meet, flat light grey ground plane, no trees no cars no people no color, white foam-board scale model under diffused light, design review presentation',
    negative: 'photorealistic, color, materials, brick, glass, wood, vegetation, trees, people, cars, detailed, textured, realistic, low quality, blurry',
  },
  {
    id: 'site-plan',
    label: 'Site Plan',
    strength: 0.62,
    prompt:
      'professional architectural site plan rendered from directly above in perfect nadir top-down orthographic projection, buildings shown as flat roof footprints with subtle shadow indicating height, trees as circular dark-green canopy blobs viewed from above, roads as clean grey strips, landscaping areas in matte green, water features in blue, paving patterns visible, clear figure-ground contrast, planning document quality',
    negative: 'perspective, 3D, oblique angle, horizon visible, photorealistic facades, eye-level, low quality, blurry, noisy, text, watermark',
  },

  // ── Artistic / Competition ────────────────────────────────────────────
  {
    id: 'watercolour',
    label: 'Watercolour',
    strength: 0.85,
    prompt:
      'watercolour painting on cold-pressed textured paper, transparent pigment washes with white paper showing through as highlights, soft bleeding edges where wet paint meets wet paint, visible paper grain texture under all paint, pigment granulation and sedimentation, selective detail at building focal point dissolving into loose washes at periphery, muted earth tones with sage green and ochre, underlying pencil guidelines visible, wet-on-wet bloom effects, hand-painted architectural competition entry style',
    negative: 'photorealistic, photograph, digital, sharp edges, perfect lines, 3D render, high contrast, neon colors, low quality, blurry',
  },
  {
    id: 'pencil-sketch',
    label: 'Pencil Sketch',
    strength: 0.88,
    prompt:
      'monochrome graphite pencil architectural sketch on white paper, zero color purely grey tones, confident hand-drawn lines with varying pressure and weight, heavy bold lines for building profile and ground plane, lighter lines for detail, parallel hatching and cross-hatching for shadow areas, white paper left blank for sky and highlights, slightly uneven hand-drawn imperfection, corners slightly overshooting, vegetation suggested as loose scribbled clusters, freehand architectural concept drawing quality',
    negative: 'photorealistic, photograph, color, painting, watercolor, digital, 3D render, perfect lines, computer generated, low quality, blurry',
  },
  {
    id: 'collage',
    label: 'Collage',
    strength: 0.80,
    prompt:
      'architectural digital collage visualization, visibly assembled from disparate photographic fragments with different image qualities and white balances, flat photographic textures applied to building surfaces without perspectival correction, cut-out people figures at slightly wrong scales, intentional visible seams between image sources, mix of hand-drawn linework and photographic elements, eclectic layered composition, contemporary architecture school post-digital aesthetic',
    negative: 'photorealistic, seamless, clean render, 3D software, smooth uniform, consistent lighting, low quality, blurry',
  },
];

// ---------------------------------------------------------------------------
// Gemini render style modifiers (from the Orchestration Spec)
// ---------------------------------------------------------------------------

interface GeminiStyleModifier {
  id: string;
  label: string;
  prompt: string;
}

const GEMINI_STYLE_MODIFIERS: Record<string, GeminiStyleModifier> = {
  photorealistic: {
    id: 'photorealistic',
    label: 'Photorealistic',
    prompt: 'Photorealistic aerial rendering. Accurate material textures, precise cast shadows, realistic vegetation, parked cars and street furniture. DSLR-quality, sharp focus, neutral white balance, high dynamic range. 8k architectural photography.',
  },
  'drone-photography': {
    id: 'drone-photography',
    label: 'Drone Photo',
    prompt: 'Professional DJI drone photograph style. Deep depth of field, subtle atmospheric haze on distant objects, real-estate aerial survey documentation quality. Construction-complete, 8k.',
  },
  'photomontage': {
    id: 'photomontage',
    label: 'Photomontage',
    prompt: 'Professional architectural photomontage. Buildings seamlessly composited into real satellite photograph, matched sun direction and color temperature. Planning application submission quality.',
  },
  'golden-hour': {
    id: 'golden-hour',
    label: 'Golden Hour',
    prompt: 'Cinematic golden hour. Warm 3000K amber-orange sunlight, long dramatic shadows, building facades glowing warm orange, windows reflecting sunset colors, sky gradient from deep orange through pink to dark blue. Rim lighting on tree edges.',
  },
  'night-scene': {
    id: 'night-scene',
    label: 'Night Scene',
    prompt: 'Night photograph. Dark navy sky, buildings defined by warm interior lighting through windows, street lamps casting pools of warm light, wet reflective pavement with light reflections, cool moonlight rim on rooftops.',
  },
  'overcast-soft': {
    id: 'overcast-soft',
    label: 'Overcast',
    prompt: 'Overcast conditions. Uniform diffused lighting with zero harsh shadows, cool 6500K color temperature, accurate material colors without glare, calm muted atmosphere.',
  },
  'summer': {
    id: 'summer',
    label: 'Summer',
    prompt: 'Peak midsummer. Dense fully-leafed tree canopy in deep saturated greens, lush lawns, vivid blue sky, strong high-angle sun, vibrant flower beds, people using outdoor terraces.',
  },
  'autumn': {
    id: 'autumn',
    label: 'Autumn',
    prompt: 'Peak autumn. Trees in rich burnt orange, deep red, gold and amber foliage, scattered fallen leaves, warm low-angle golden sunlight with long shadows, slight atmospheric haze.',
  },
  watercolour: {
    id: 'watercolour',
    label: 'Watercolour',
    prompt: 'Watercolour painting style. Transparent pigment washes on textured paper, soft bleeding edges, visible paper grain, selective detail dissolving into loose washes at periphery, muted earth tones.',
  },
  'pencil-sketch': {
    id: 'pencil-sketch',
    label: 'Pencil Sketch',
    prompt: 'Monochrome graphite pencil sketch. Confident hand-drawn lines with varying pressure, parallel hatching for shadows, white paper for sky and highlights, freehand architectural concept quality.',
  },
  collage: {
    id: 'collage',
    label: 'Collage',
    prompt: 'Architectural digital collage. Photographic fragments with different qualities, flat textures on building surfaces, cut-out people, intentional seams, eclectic layered composition.',
  },
  'massing-study': {
    id: 'massing-study',
    label: 'Massing Study',
    prompt: 'White massing model. All surfaces uniform matte white plaster, no texture detail, pure geometric volumes showing mass and proportion, soft studio lighting, ambient occlusion shadows.',
  },
  'site-plan': {
    id: 'site-plan',
    label: 'Site Plan',
    prompt: 'Top-down site plan. Buildings as flat roof footprints with subtle shadow, trees as circular green canopy blobs, roads as clean grey strips, planning document quality.',
  },
};

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** Backend render endpoint */
const RENDER_API_URL = '/api/v1/render/generate';

/** Timeout for the backend request (3 minutes — Imagen 3 can be slow) */
const RENDER_TIMEOUT = 180_000;

/** The 4 face bearings */
const FACE_BEARINGS: { label: 'front' | 'right' | 'rear' | 'left'; bearing: number }[] = [
  { label: 'front', bearing: 0 },
  { label: 'right', bearing: 90 },
  { label: 'rear', bearing: 180 },
  { label: 'left', bearing: 270 },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Compute the geographic bounding box of a polygon [[lng,lat],...] with padding factor */
function zoneBounds(coords: number[][], padding = 0.3): { west: number; south: number; east: number; north: number } {
  let west = Infinity, south = Infinity, east = -Infinity, north = -Infinity;
  for (const [lng, lat] of coords) {
    if (lng < west) west = lng;
    if (lng > east) east = lng;
    if (lat < south) south = lat;
    if (lat > north) north = lat;
  }
  const lngPad = (east - west) * padding;
  const latPad = (north - south) * padding;
  return {
    west: west - lngPad,
    south: south - latPad,
    east: east + lngPad,
    north: north + latPad,
  };
}

/** Capture the Mapbox canvas as a base64-encoded PNG string (no data-URI prefix) */
async function captureMapCanvasBase64(map: MapboxMap): Promise<string> {
  const canvas = map.getCanvas();
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (!blob) return reject(new Error('Failed to capture map canvas'));
      const reader = new FileReader();
      reader.onloadend = () => {
        const dataUri = reader.result as string;
        // Strip the "data:image/png;base64," prefix — backend wants raw base64
        const base64 = dataUri.split(',')[1];
        resolve(base64);
      };
      reader.onerror = () => reject(new Error('Failed to read canvas blob'));
      reader.readAsDataURL(blob);
    }, 'image/png');
  });
}

/**
 * Compute the nearest standard aspect ratio string from the map canvas dimensions.
 * Vertex AI Imagen 3 accepts: "1:1", "3:4", "4:3", "9:16", "16:9".
 */
function computeAspectRatio(map: MapboxMap): string {
  const canvas = map.getCanvas();
  const w = canvas.width;
  const h = canvas.height;
  const ratio = w / h;

  const ratios: { label: string; value: number }[] = [
    { label: '1:1', value: 1 },
    { label: '3:4', value: 3 / 4 },
    { label: '4:3', value: 4 / 3 },
    { label: '9:16', value: 9 / 16 },
    { label: '16:9', value: 16 / 9 },
  ];

  let best = ratios[0];
  let bestDiff = Math.abs(ratio - best.value);
  for (const r of ratios) {
    const diff = Math.abs(ratio - r.value);
    if (diff < bestDiff) {
      best = r;
      bestDiff = diff;
    }
  }

  console.log(`[AIRender] Canvas ${w}x${h} (ratio ${ratio.toFixed(3)}) → aspect ratio: ${best.label}`);
  return best.label;
}


/**
 * Convert site boundary geographic coordinates to pixel coordinates on the Mapbox canvas.
 */
function siteBoundaryToPixels(
  map: MapboxMap,
  coords: number[][],
): { x: number; y: number }[] {
  return coords.map(([lng, lat]) => {
    const point = map.project([lng, lat]);
    return { x: point.x, y: point.y };
  });
}

/**
 * Generate a binary mask from site zone polygons.
 * White (255) = area to edit (inside zone polygons), Black (0) = keep untouched.
 * The mask matches the canvas dimensions exactly.
 */
function generateBinaryMask(
  map: MapboxMap,
  siteZones: SiteZone[],
): string {
  const mapCanvas = map.getCanvas();
  // Use the actual pixel dimensions (accounts for device pixel ratio)
  const w = mapCanvas.width;
  const h = mapCanvas.height;
  const dpr = window.devicePixelRatio || 1;

  const maskCanvas = document.createElement('canvas');
  maskCanvas.width = w;
  maskCanvas.height = h;
  const ctx = maskCanvas.getContext('2d')!;

  // Fill entirely black (keep everything by default)
  ctx.fillStyle = '#000000';
  ctx.fillRect(0, 0, w, h);

  // Draw zone polygons as white (area to edit) in hierarchical order:
  // 1. site_boundary FIRST (master clipping area)
  // 2. All other zones on top (redundant but explicit)
  ctx.fillStyle = '#ffffff';
  let drawnCount = 0;

  const boundaries = siteZones.filter(z => z.zone_type === 'site_boundary');
  const others = siteZones.filter(z => z.zone_type !== 'site_boundary');

  for (const zone of [...boundaries, ...others]) {
    if (!zone.coordinates || zone.coordinates.length < 3) continue;
    const pixels = siteBoundaryToPixels(map, zone.coordinates);

    // Scale pixel coords by DPR to match the actual canvas pixel dimensions
    ctx.beginPath();
    ctx.moveTo(pixels[0].x * dpr, pixels[0].y * dpr);
    for (let i = 1; i < pixels.length; i++) {
      ctx.lineTo(pixels[i].x * dpr, pixels[i].y * dpr);
    }
    ctx.closePath();
    ctx.fill();
    drawnCount++;
    console.log(`[AIRender] Mask: drew zone "${zone.name || zone.id}" (${zone.zone_type}) — ${pixels.length} vertices`);
  }
  console.log(`[AIRender] Mask complete: ${drawnCount}/${siteZones.length} zones drawn on ${w}x${h} canvas (DPR=${dpr})`);

  // Return raw base64 (no data-URI prefix)
  return maskCanvas.toDataURL('image/png').split(',')[1];
}

/** Load an image from a URL or Blob and return an HTMLImageElement */
function loadImage(src: string | Blob): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => resolve(img);
    img.onerror = (e) => reject(new Error(`Failed to load image: ${e}`));
    if (src instanceof Blob) {
      const url = URL.createObjectURL(src);
      img.onload = () => { URL.revokeObjectURL(url); resolve(img); };
      img.src = url;
    } else {
      img.src = src;
    }
  });
}

/**
 * Stitch the AI-rendered result back onto the original screenshot,
 * using site zone polygons as a clip mask so only the zone areas change.
 * Returns a data-URI for the composited image.
 */
async function stitchWithBoundaryMask(
  originalBase64: string,
  renderedDataUri: string,
  map: MapboxMap,
  siteZones: SiteZone[],
): Promise<string> {
  const [originalImg, renderedImg] = await Promise.all([
    loadImage(`data:image/png;base64,${originalBase64}`),
    loadImage(renderedDataUri),
  ]);

  const w = originalImg.naturalWidth;
  const h = originalImg.naturalHeight;

  const canvas = document.createElement('canvas');
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext('2d')!;

  // Step 1: Draw the original screenshot (untouched background)
  ctx.drawImage(originalImg, 0, 0, w, h);

  // Step 2: Clip to the site boundary (master container) so the AI result
  // replaces everything inside. Using only site_boundary avoids winding-rule
  // conflicts where inner zone sub-paths with opposite winding create holes.
  const dpr = window.devicePixelRatio || 1;
  const boundaries = siteZones.filter(z => z.zone_type === 'site_boundary' && z.coordinates && z.coordinates.length >= 3);
  // Fall back to all zones if no site_boundary exists
  const clipZones = boundaries.length > 0 ? boundaries : siteZones.filter(z => z.coordinates && z.coordinates.length >= 3);

  ctx.save();
  ctx.beginPath();
  for (const zone of clipZones) {
    const pixels = siteBoundaryToPixels(map, zone.coordinates!);
    ctx.moveTo(pixels[0].x * dpr, pixels[0].y * dpr);
    for (let i = 1; i < pixels.length; i++) {
      ctx.lineTo(pixels[i].x * dpr, pixels[i].y * dpr);
    }
    ctx.closePath();
  }
  ctx.clip();

  // Step 3: Draw the rendered image within the clipped region
  ctx.drawImage(renderedImg, 0, 0, w, h);
  ctx.restore();

  return canvas.toDataURL('image/png');
}

/**
 * Generate a binary mask for a SINGLE zone polygon.
 * White (255) = the zone's footprint, Black (0) = everything else.
 */
function generateSingleZoneMask(
  map: MapboxMap,
  zone: SiteZone,
): string {
  const mapCanvas = map.getCanvas();
  const w = mapCanvas.width;
  const h = mapCanvas.height;
  const dpr = window.devicePixelRatio || 1;

  const maskCanvas = document.createElement('canvas');
  maskCanvas.width = w;
  maskCanvas.height = h;
  const ctx = maskCanvas.getContext('2d')!;

  // Fill entirely black (keep everything)
  ctx.fillStyle = '#000000';
  ctx.fillRect(0, 0, w, h);

  // Draw only this zone's polygon as white
  if (zone.coordinates && zone.coordinates.length >= 3) {
    const pixels = siteBoundaryToPixels(map, zone.coordinates);
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.moveTo(pixels[0].x * dpr, pixels[0].y * dpr);
    for (let i = 1; i < pixels.length; i++) {
      ctx.lineTo(pixels[i].x * dpr, pixels[i].y * dpr);
    }
    ctx.closePath();
    ctx.fill();
  }

  // Debug: count white pixels to verify mask has actual coverage
  const imgData = ctx.getImageData(0, 0, w, h).data;
  let whiteCount = 0;
  for (let i = 0; i < imgData.length; i += 4) {
    if (imgData[i] > 128) whiteCount++;
  }
  const totalPx = w * h;
  console.log(`[AIRender] Single-zone mask: ${w}x${h}, white=${whiteCount}/${totalPx} (${((whiteCount / totalPx) * 100).toFixed(1)}%), zone="${zone.name || zone.zone_type}"`);

  return maskCanvas.toDataURL('image/png').split(',')[1];
}

/**
 * Build a zone-specific prompt for per-zone rendering.
 * Simple, natural language — Gemini handles spatial reasoning natively.
 */
function buildSingleZonePrompt(zone: SiteZone, options: AIRenderOptions): string {
  const archetypeInfo = getZoneArchetypeInfo(zone);
  const desc = buildArchetypeDescription(archetypeInfo, zone.zone_type);

  // Resolve the selected render style
  const styleId = options.renderStyleId || options.style || 'photorealistic';
  const styleMod = GEMINI_STYLE_MODIFIERS[styleId];
  const styleLabel = styleMod?.label || 'Photorealistic';
  const stylePrompt = styleMod?.prompt || '';

  // For non-photorealistic styles, omit "photorealistic" from the base instruction
  const isPhotoStyle = ['photorealistic', 'drone-photography', 'photomontage', 'golden-hour',
    'night-scene', 'overcast-soft', 'summer', 'autumn'].includes(styleId);
  const isSitePlan = styleId === 'site-plan';
  const isArtistic = ['watercolour', 'pencil-sketch', 'collage', 'massing-study', 'site-plan'].includes(styleId);

  const parts: string[] = [];

  if (isArtistic) {
    parts.push(`Replace the colored overlay area with a ${desc}, rendered in ${styleLabel} style.`);
    parts.push(`RENDER STYLE: ${stylePrompt}`);
  } else {
    parts.push(`Replace the colored overlay area with a photorealistic ${desc}.`);
    if (styleId !== 'photorealistic') {
      parts.push(`RENDER STYLE: ${stylePrompt}`);
    }
  }

  if (isSitePlan) {
    parts.push('Disable 3D perspective and shadows. Render as a flat 2D orthographic view looking straight down.');
  }

  parts.push(
    'The building or content may extend into the surrounding WHITE area (which is the site boundary) — blend naturally with sidewalks, landscaping, or ground-plane there.',
    'However, do NOT extend into or overlap any OTHER colored zones. Each colored area is a separate zone with its own purpose.',
    'Keep all satellite imagery outside the white site boundary EXACTLY as it is.',
  );

  if (isPhotoStyle) {
    parts.push('Match the lighting, shadows, and perspective of the surrounding context so it looks like a seamless aerial photomontage.');
  }

  if (options.customPrompt?.trim()) {
    parts.push(options.customPrompt.trim());
  }

  return parts.join(' ');
}

/**
 * Build a natural-language description from archetype metadata.
 * Used by both single-zone and multi-zone prompt builders.
 */
function buildArchetypeDescription(
  info: ReturnType<typeof getZoneArchetypeInfo>,
  zoneType: string,
): string {
  if (info.mapOverlayPrompt) return info.mapOverlayPrompt;

  if (info.archetypeTitle) {
    const parts = [info.archetypeTitle.toLowerCase() + ' building'];
    if (info.aerialAppearance) parts.push(info.aerialAppearance);
    if (info.facadeDescription) parts.push(info.facadeDescription);
    if (info.roofDescription) parts.push(info.roofDescription);
    if (info.materials) parts.push(info.materials);
    if (info.colorScheme) parts.push(info.colorScheme);
    if (info.heightTendency) parts.push(info.heightTendency);
    return parts.join('. ');
  }

  return defaultZoneDescription(zoneType);
}

/**
 * Composite a single zone render onto a cumulative canvas.
 * Uses the zone polygon as a clip mask — only pixels inside the zone change.
 */
async function compositeZoneRender(
  baseDataUri: string,
  renderedDataUri: string,
  map: MapboxMap,
  zone: SiteZone,
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

  // Draw the base (cumulative result so far)
  ctx.drawImage(baseImg, 0, 0, w, h);

  // Clip to this zone's polygon and draw the rendered image
  if (zone.coordinates && zone.coordinates.length >= 3) {
    const dpr = window.devicePixelRatio || 1;
    const pixels = siteBoundaryToPixels(map, zone.coordinates);
    console.log(`[AIRender] compositeZoneRender: base=${w}x${h}, rendered=${renderedImg.naturalWidth}x${renderedImg.naturalHeight}, dpr=${dpr}, clip pts=${pixels.length}`);
    console.log(`[AIRender]   Clip polygon (device px):`, pixels.slice(0, 4).map(p => `(${(p.x * dpr).toFixed(0)},${(p.y * dpr).toFixed(0)})`).join(' '));
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(pixels[0].x * dpr, pixels[0].y * dpr);
    for (let i = 1; i < pixels.length; i++) {
      ctx.lineTo(pixels[i].x * dpr, pixels[i].y * dpr);
    }
    ctx.closePath();
    ctx.clip();
    ctx.drawImage(renderedImg, 0, 0, w, h);
    ctx.restore();
  }

  return canvas.toDataURL('image/png');
}

/** Get the current visible bounds as image-source coordinates: [[W,N],[E,N],[E,S],[W,S]] */
function getMapBounds(
  map: MapboxMap,
): [[number, number], [number, number], [number, number], [number, number]] {
  const bounds = map.getBounds()!;
  const nw: [number, number] = [bounds.getWest(), bounds.getNorth()];
  const ne: [number, number] = [bounds.getEast(), bounds.getNorth()];
  const se: [number, number] = [bounds.getEast(), bounds.getSouth()];
  const sw: [number, number] = [bounds.getWest(), bounds.getSouth()];
  return [nw, ne, se, sw];
}

/** Ease the map to a specific bearing/pitch and wait for it to finish */
function easeMapTo(map: MapboxMap, bearing: number, pitch: number): Promise<void> {
  return new Promise((resolve) => {
    map.easeTo({ bearing, pitch, duration: 800 });
    const onIdle = () => {
      map.off('idle', onIdle);
      setTimeout(resolve, 300);
    };
    map.on('idle', onIdle);
  });
}

/** Determine which face should be visible based on current map bearing */
function getActiveFaceLabel(bearing: number): 'front' | 'right' | 'rear' | 'left' {
  const b = ((bearing % 360) + 360) % 360;
  if (b >= 315 || b < 45) return 'front';
  if (b >= 45 && b < 135) return 'right';
  if (b >= 135 && b < 225) return 'rear';
  return 'left';
}


// ---------------------------------------------------------------------------
// Structured prompt builder — Spatial-to-Render Orchestration
// ---------------------------------------------------------------------------

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const catalog = (archetypeCatalog as any)?.archetypes as any[] | undefined;

interface ZonePromptEntry {
  color: string;
  zoneType: string;
  zoneName: string;
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
}

/**
 * Extract archetype metadata for a single zone by looking up its
 * `development_archetype_id`, `road_archetype_id`, etc. properties.
 */
function getZoneArchetypeInfo(zone: SiteZone): {
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
} {
  if (!zone.properties || !catalog) return {};

  const PREFIXES = ['development', 'road', 'green_space', 'plaza'] as const;

  for (const prefix of PREFIXES) {
    const archetypeId = zone.properties[`${prefix}_archetype_id`] as string | undefined;
    if (!archetypeId) continue;

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const entry = catalog.find((a: any) =>
      a.id === archetypeId || archetypeId.startsWith(a.id + '_'),
    );
    if (!entry) continue;

    const sp = entry.styleProfile || {};
    const fd = entry.facadeDetail || {};
    const rd = entry.roofDetail || {};

    // Build a rich facade description from facadeDetail
    const facadeParts: string[] = [];
    if (fd.primaryMaterial) facadeParts.push(fd.primaryMaterial);
    if (fd.groundFloor) facadeParts.push(`Ground floor: ${fd.groundFloor}`);
    if (fd.upperFloors) facadeParts.push(`Upper floors: ${fd.upperFloors}`);
    if (fd.cornice) facadeParts.push(`Cornice: ${fd.cornice}`);
    if (fd.colorScheme) facadeParts.push(`Colors: ${fd.colorScheme}`);

    // Build roof description
    const roofParts: string[] = [];
    if (rd.form) roofParts.push(rd.form);
    if (rd.material) roofParts.push(rd.material);
    if (rd.features) roofParts.push(rd.features);
    if (rd.aerialAppearance) roofParts.push(`Aerial: ${rd.aerialAppearance}`);

    // Materials list
    const materials = Array.isArray(sp.materials) ? sp.materials.join(', ') : sp.materials;

    return {
      archetypeTitle: entry.title,
      facadeDescription: facadeParts.length > 0 ? facadeParts.join('. ') : undefined,
      roofDescription: roofParts.length > 0 ? roofParts.join('. ') : undefined,
      materials: materials || undefined,
      massing: sp.massing || undefined,
      heightTendency: sp.heightTendency || undefined,
      publicRealm: sp.publicRealm || undefined,
      mapOverlayPrompt: entry.renderPrompt?.mapOverlay || undefined,
      colorScheme: fd.colorScheme || undefined,
      aerialAppearance: rd.aerialAppearance || undefined,
    };
  }

  return {};
}

/**
 * Build zone-by-zone entries for the structured prompt.
 * Maps each non-boundary zone to its color, type, and archetype metadata.
 */
function collectZonePromptEntries(zones: SiteZone[]): ZonePromptEntry[] {
  const entries: ZonePromptEntry[] = [];

  for (const zone of zones) {
    if (!zone.coordinates?.length) continue;

    // Include site_boundary with a special contextual infill entry
    if (zone.zone_type === 'site_boundary') {
      entries.push({
        color: zone.color || '#F5D63D',
        zoneType: 'site_boundary',
        zoneName: 'Site Boundary / Contextual Infill',
      });
      continue;
    }

    const config = ZONE_TYPE_CONFIG[zone.zone_type];
    const color = zone.color || config?.color || '#888888';
    const archetypeInfo = getZoneArchetypeInfo(zone);

    entries.push({
      color,
      zoneType: zone.zone_type,
      zoneName: zone.name || config?.label || zone.zone_type,
      ...archetypeInfo,
    });
  }

  // With unique shade IDs, each archetype-assigned zone has its own color,
  // so deduplication only applies to unassigned zones sharing a default color.
  // Deduplicate by color+zoneType to keep distinct zone types separate.
  const seen = new Map<string, ZonePromptEntry>();
  for (const entry of entries) {
    const key = `${entry.color}_${entry.zoneType}`;
    if (!seen.has(key)) {
      seen.set(key, entry);
    } else if (entry.archetypeTitle && !seen.get(key)!.archetypeTitle) {
      seen.set(key, entry);
    }
  }

  // Sort: buildings/parks first, site_boundary LAST — so the AI prioritizes
  // specific zone instructions over the generic infill instruction.
  const result = Array.from(seen.values());
  result.sort((a, b) => {
    if (a.zoneType === 'site_boundary') return 1;
    if (b.zoneType === 'site_boundary') return -1;
    return 0;
  });
  return result;
}

/**
 * Human-readable color name for hex colors — archetype-aware.
 *
 * First tries to match the hex to a known archetype shade (unique per archetype).
 * Falls back to generic zone-type color names for unassigned zones.
 */
function colorName(hex: string): string {
  // Try archetype shade match first (unique per archetype)
  const archetypeId = getArchetypeForShade(hex);
  if (archetypeId) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const entry = catalog?.find((a: any) => a.id === archetypeId || archetypeId.startsWith(a.id + '_'));
    if (entry?.title) return `${entry.title} shade (${hex})`;
  }

  // Fall back to generic zone-type names
  const genericMap: Record<string, string> = {
    '#E03C31': 'red',
    '#e03c31': 'red',
    '#F5D63D': 'yellow',
    '#f5d63d': 'yellow',
    '#616161': 'dark gray',
    '#4CAF50': 'green',
    '#4caf50': 'green',
    '#9E9E9E': 'light gray',
    '#9e9e9e': 'light gray',
    '#4A90D9': 'blue',
    '#4a90d9': 'blue',
    '#C8A02A': 'gold/amber',
    '#c8a02a': 'gold/amber',
    '#F59E0B': 'orange/amber',
    '#f59e0b': 'orange/amber',
  };
  return genericMap[hex] || hex;
}

/**
 * Build the default description for a zone type when no archetype is assigned.
 */
function defaultZoneDescription(zoneType: string): string {
  switch (zoneType) {
    case 'building':
      return 'photorealistic commercial/mixed-use buildings with glass and concrete facades, ground-floor retail, multiple stories';
    case 'residential':
      return 'photorealistic residential buildings — townhouses or apartment blocks with warm materials, balconies, and landscaped entries';
    case 'road':
      return 'paved road with lane markings, sidewalks, street trees, and parked cars';
    case 'green_space':
      return 'landscaped park with mature trees, grass lawns, walking paths, benches, and ornamental planting';
    case 'parking':
      return 'paved surface parking or public plaza with pedestrian paving, bollards, and street furniture';
    case 'water':
      return 'water feature — pond, fountain, or reflecting pool with clean blue water and stone edges';
    case 'development_area':
      return 'mixed-use urban development with varied building heights, active ground floors, and public realm';
    default:
      return 'photorealistic urban development appropriate to the zone type';
  }
}

/**
 * Build the multi-zone prompt — simple, natural language for Gemini.
 * Each zone gets a one-line description built from archetype card metadata.
 */
function buildStructuredPrompt(options: AIRenderOptions): string {
  const zones = options.siteZones || [];
  const zoneEntries = collectZonePromptEntries(zones);
  const styleId = options.renderStyleId || options.style || 'photorealistic';
  const style = GEMINI_STYLE_MODIFIERS[styleId];

  const isArtistic = ['watercolour', 'pencil-sketch', 'collage', 'massing-study', 'site-plan'].includes(styleId);
  const isSitePlan = styleId === 'site-plan';

  const parts: string[] = [
    'This is an aerial/satellite photograph with colored polygon overlays marking proposed development zones.',
  ];

  if (isArtistic) {
    parts.push(`Replace each colored area with the described content, rendered in ${style?.label || styleId} style. Keep all surrounding imagery exactly as it is.`);
  } else {
    parts.push('Replace each colored area with the following photorealistic content. Keep all surrounding imagery exactly as it is.');
  }

  // Inject render style
  if (style) {
    parts.push(`RENDER STYLE: ${style.prompt}`);
  }

  if (isSitePlan) {
    parts.push('Disable 3D perspective and shadows. Render as a flat 2D orthographic view looking straight down.');
  }

  if (zoneEntries.length > 0) {
    for (const entry of zoneEntries) {
      const color = colorName(entry.color);
      let desc: string;

      if (entry.zoneType === 'site_boundary') {
        desc = 'realistic urban ground-plane — sidewalks, grass, small street trees, pedestrian paths blending with surroundings';
      } else {
        desc = buildArchetypeDescription(entry, entry.zoneType);
      }

      parts.push(`- ${color.toUpperCase()} area: ${desc}`);
    }
  }

  if (options.customPrompt?.trim()) {
    parts.push(options.customPrompt.trim());
  }

  if (!isArtistic) {
    parts.push('Make it look like a seamless photomontage — match lighting, shadows, and perspective of the satellite imagery.');
  } else {
    parts.push(`Render the entire scene consistently in ${style?.label || styleId} style.`);
  }

  return parts.join('\n');
}

/**
 * Master prompt builder — generates a simple, natural-language prompt
 * from zone data and archetype card metadata for Gemini.
 */
function buildPrompt(options: AIRenderOptions): string {
  const zones = options.siteZones?.filter(z => z.zone_type !== 'site_boundary') || [];

  if (zones.length > 0) {
    return buildStructuredPrompt(options);
  }

  if (options.mapOverlayPrompt?.trim()) {
    const parts = [
      `Replace the colored overlay areas with: ${options.mapOverlayPrompt.trim()}.`,
      'Keep all surrounding satellite imagery exactly as it is.',
      'Match lighting, shadows, and perspective for a seamless photomontage.',
    ];
    if (options.customPrompt?.trim()) parts.push(options.customPrompt.trim());
    return parts.join(' ');
  }

  // Fallback: generic
  const parts = [
    'Replace the colored overlay areas in this aerial photograph with photorealistic urban development.',
    'Keep all surrounding imagery exactly as it is.',
  ];
  if (options.archetypePrompt?.trim()) parts.push(options.archetypePrompt.trim());
  if (options.customPrompt?.trim()) parts.push(options.customPrompt.trim());
  return parts.join(' ');
}

// ---------------------------------------------------------------------------
// Negative prompt builder
// ---------------------------------------------------------------------------

/**
 * Aggregate negative prompts from:
 * 1. The selected style preset's negative prompt
 * 2. Archetype-level negative prompts (from mapOverlayNegative or archetypeNegative)
 * 3. Zone-level archetype negatives (extracted from catalog metadata)
 *
 * Returns a single de-duplicated negative prompt string, or empty string if none.
 */
function buildNegativePrompt(options: AIRenderOptions): string {
  const parts: string[] = [];

  // 1. Style preset negative
  const styleId = options.renderStyleId || options.style || 'photorealistic';
  const stylePreset = AI_RENDER_STYLES.find((s) => s.id === styleId);
  if (stylePreset?.negative) {
    parts.push(stylePreset.negative);
  }

  // 2. Archetype-level negatives passed from the panel
  if (options.mapOverlayNegative?.trim()) {
    parts.push(options.mapOverlayNegative.trim());
  }
  if (options.archetypeNegative?.trim()) {
    parts.push(options.archetypeNegative.trim());
  }

  // 3. Zone-level archetype negatives from catalog
  const zones = options.siteZones || [];
  for (const zone of zones) {
    if (zone.zone_type === 'site_boundary') continue;
    if (!zone.properties || !catalog) continue;

    const PREFIXES = ['development', 'road', 'green_space', 'plaza'] as const;
    for (const prefix of PREFIXES) {
      const archetypeId = zone.properties[`${prefix}_archetype_id`] as string | undefined;
      if (!archetypeId) continue;
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const entry = catalog.find((a: any) => a.id === archetypeId || archetypeId.startsWith(a.id + '_'));
      if (entry?.renderPrompt?.negative) {
        parts.push(entry.renderPrompt.negative);
      }
      break;
    }
  }

  if (parts.length === 0) return '';

  // De-duplicate fragments (split by comma, trim, unique, rejoin)
  const allFragments = parts.join(', ').split(',').map(s => s.trim()).filter(Boolean);
  const unique = [...new Set(allFragments.map(s => s.toLowerCase()))];
  // Map back to original casing from first occurrence
  const seen = new Map<string, string>();
  for (const frag of allFragments) {
    const key = frag.toLowerCase();
    if (!seen.has(key)) seen.set(key, frag);
  }
  return unique.map(k => seen.get(k)!).join(', ');
}

// ---------------------------------------------------------------------------
// Vertex AI backend call
// ---------------------------------------------------------------------------

/**
 * Call our backend endpoint which proxies to Vertex AI Imagen 3.
 * Returns a data-URI for the rendered image.
 */
async function callVertexAI(
  imageBase64: string,
  prompt: string,
  seed: number,
  aspectRatio = '4:3',
  maskBase64?: string,
  negativePrompt?: string,
  guidanceScale?: number,
): Promise<{ imageDataUri: string; seed: number }> {
  console.log('[AIRender] Calling Vertex AI via backend — prompt length:', prompt.length, 'mask:', !!maskBase64, 'negative:', !!negativePrompt, 'guidance:', guidanceScale);

  const body: Record<string, unknown> = {
    image_base64: imageBase64,
    prompt,
    aspect_ratio: aspectRatio,
    seed,
  };
  if (maskBase64) {
    body.mask_base64 = maskBase64;
  }
  if (negativePrompt) {
    body.negative_prompt = negativePrompt;
  }
  if (guidanceScale != null) {
    body.guidance_scale = guidanceScale;
  }

  const resp = await axios.post(
    RENDER_API_URL,
    body,
    { timeout: RENDER_TIMEOUT },
  );

  const { image_base64: resultBase64, seed: resultSeed } = resp.data;
  const imageDataUri = `data:image/png;base64,${resultBase64}`;

  console.log('[AIRender] Vertex AI success — image size:', resultBase64.length, 'chars');
  return { imageDataUri, seed: resultSeed ?? seed };
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useAIRender(): UseAIRenderReturn {
  const [isRendering, setIsRendering] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');
  const [result, setResult] = useState<AIRenderResult | null>(null);
  const [previews, setPreviews] = useState<AIRenderResult[]>([]);
  const [faceRenders, setFaceRenders] = useState<FaceRender[]>([]);
  const [selectedPreviewIndex, setSelectedPreviewIndex] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const reset = useCallback(() => {
    setResult(null);
    setPreviews([]);
    setFaceRenders([]);
    setSelectedPreviewIndex(null);
    setError(null);
    setProgress(0);
    setStatusMessage('');
  }, []);

  // ── Core render function: capture → base64 → backend → Vertex AI ──

  const renderSingle = useCallback(
    async (
      imageBase64: string,
      bounds: [[number, number], [number, number], [number, number], [number, number]],
      options: AIRenderOptions,
      seed: number,
      maskBase64?: string,
      aspectRatio = '4:3',
    ): Promise<AIRenderResult | null> => {
      const prompt = buildPrompt(options);
      const negativePrompt = buildNegativePrompt(options);
      const guidanceScale = options.guidanceScale ?? 15;

      try {
        const { imageDataUri, seed: resultSeed } = await callVertexAI(
          imageBase64,
          prompt,
          seed,
          aspectRatio,
          maskBase64,
          negativePrompt || undefined,
          guidanceScale,
        );
        return { imageUrl: imageDataUri, bounds, seed: resultSeed, prompt };
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err);
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const detail = (err as any)?.response?.data?.detail;
        console.error('[AIRender] Vertex AI failed:', detail || msg);
        throw new Error(detail || msg);
      }
    },
    [],
  );

  // ── Single render (current camera position) ────────────────────────

  const render = useCallback(
    async (map: MapboxMap, options: AIRenderOptions = {}): Promise<AIRenderResult | null> => {
      if (abortRef.current) abortRef.current.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      setIsRendering(true);
      setProgress(-1); // indeterminate
      setError(null);
      setStatusMessage('Capturing view...');

      try {
        // Generate mask FIRST (synchronous) before the async screenshot capture,
        // so both read canvas dimensions at the same instant. A layout reflow
        // between calls can shift dimensions by ±1px, which Vertex AI rejects.
        const zones = options.siteZones;
        const maskBase64 = zones && zones.length > 0
          ? generateBinaryMask(map, zones)
          : undefined;

        const imageBase64 = await captureMapCanvasBase64(map);
        const bounds = getMapBounds(map);

        setStatusMessage('Generating render... Please wait');

        const seed = options.seed ?? Math.floor(Math.random() * 2147483647);
        const aspectRatio = computeAspectRatio(map);
        const renderResult = await renderSingle(imageBase64, bounds, options, seed, maskBase64, aspectRatio);

        if (!renderResult) throw new Error('Vertex AI returned no image');

        // Stitch: composite AI render onto original using zone polygons as clip mask
        if (zones && zones.length > 0) {
          const stitched = await stitchWithBoundaryMask(imageBase64, renderResult.imageUrl, map, zones);
          renderResult.imageUrl = stitched;
        }

        setResult(renderResult);
        setProgress(100);
        setStatusMessage('Complete');
        setIsRendering(false);
        return renderResult;
      } catch (err: unknown) {
        if ((err as Error)?.name === 'AbortError') {
          setIsRendering(false);
          setProgress(0);
          setStatusMessage('');
          return null;
        }
        const msg = err instanceof Error ? err.message : String(err);
        setError(msg);
        setIsRendering(false);
        setProgress(0);
        setStatusMessage('');
        return null;
      }
    },
    [renderSingle],
  );

  // ── Zone-targeted render ──────────────────────────────────────────

  const renderZone = useCallback(
    async (
      map: MapboxMap,
      zoneCoords: number[][],
      options: AIRenderOptions = {},
    ): Promise<AIRenderResult | null> => {
      if (abortRef.current) abortRef.current.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      setIsRendering(true);
      setProgress(-1);
      setError(null);
      setStatusMessage('Zooming to building zone...');

      try {
        const originalBearing = map.getBearing();
        const zb = zoneBounds(zoneCoords, 0.5);

        map.fitBounds(
          [[zb.west, zb.south], [zb.east, zb.north]],
          { padding: 60, pitch: 45, bearing: originalBearing, duration: 0 },
        );

        await new Promise<void>((resolve) => {
          const onIdle = () => { map.off('idle', onIdle); setTimeout(resolve, 500); };
          map.on('idle', onIdle);
        });

        setStatusMessage('Capturing zone view...');

        const imageBase64 = await captureMapCanvasBase64(map);
        const bounds = getMapBounds(map);

        setStatusMessage('Generating render... Please wait');

        const seed = options.seed ?? Math.floor(Math.random() * 2147483647);
        const aspectRatio = computeAspectRatio(map);
        const renderResult = await renderSingle(imageBase64, bounds, options, seed, undefined, aspectRatio);

        if (!renderResult) throw new Error('Vertex AI returned no image');

        setResult(renderResult);
        setProgress(100);
        setStatusMessage('Complete — zone rendered');
        setIsRendering(false);
        return renderResult;
      } catch (err: unknown) {
        if ((err as Error)?.name === 'AbortError') {
          setIsRendering(false);
          setProgress(0);
          setStatusMessage('');
          return null;
        }
        const msg = err instanceof Error ? err.message : String(err);
        console.error('[AIRender] Zone render failed:', msg);
        setError(msg);
        setIsRendering(false);
        setProgress(0);
        setStatusMessage('');
        return null;
      }
    },
    [renderSingle],
  );

  // ── Preview renders (3 in parallel) ──────────────────────────────────

  const renderPreviews = useCallback(
    async (map: MapboxMap, options: AIRenderOptions = {}): Promise<AIRenderResult[]> => {
      setIsRendering(true);
      setProgress(-1);
      setError(null);
      setPreviews([]);
      setSelectedPreviewIndex(null);
      setResult(null);
      setStatusMessage('Capturing view...');

      try {
        // Generate mask FIRST (synchronous) to match canvas dimensions exactly
        const zones = options.siteZones;
        const maskBase64 = zones && zones.length > 0
          ? generateBinaryMask(map, zones)
          : undefined;

        const imageBase64 = await captureMapCanvasBase64(map);
        const bounds = getMapBounds(map);

        setStatusMessage('Generating preview... Please wait');

        // Generate 1 preview render
        const seeds = Array.from({ length: 1 }, () => Math.floor(Math.random() * 2147483647));

        const aspectRatio = computeAspectRatio(map);
        const promises = seeds.map((seed) =>
          renderSingle(imageBase64, bounds, options, seed, maskBase64, aspectRatio).catch(() => null),
        );

        const rawResults = await Promise.all(promises);
        let successful = rawResults.filter((r): r is AIRenderResult => r !== null);

        // Stitch each preview onto original using zone polygons as clip mask
        if (zones && zones.length > 0) {
          successful = await Promise.all(
            successful.map(async (r) => {
              const stitched = await stitchWithBoundaryMask(imageBase64, r.imageUrl, map, zones);
              return { ...r, imageUrl: stitched };
            }),
          );
        }

        setPreviews(successful);
        setResult(null);
        setProgress(100);
        setStatusMessage('Select a preview');
        setIsRendering(false);
        return successful;
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err);
        setError(msg);
        setIsRendering(false);
        setProgress(0);
        setStatusMessage('');
        return [];
      }
    },
    [renderSingle],
  );

  // ── Full quality render ─────────────────────────────────────────────

  const renderFull = useCallback(
    async (
      map: MapboxMap,
      options: AIRenderOptions,
      seed: number,
      singleView = true,
    ): Promise<AIRenderResult | null> => {
      setIsRendering(true);
      setProgress(-1);
      setError(null);
      setFaceRenders([]);

      try {
        // ── Single-view mode: render from user's current perspective ──
        if (singleView) {
          setStatusMessage('Capturing current view...');

          // Generate mask FIRST (synchronous) to match canvas dimensions exactly
          const zones = options.siteZones;
          const maskBase64 = zones && zones.length > 0
            ? generateBinaryMask(map, zones)
            : undefined;

          const imageBase64 = await captureMapCanvasBase64(map);
          const bounds = getMapBounds(map);

          setStatusMessage('Rendering full quality... Please wait');

          const aspectRatio = computeAspectRatio(map);
          const fullResult = await renderSingle(imageBase64, bounds, options, seed, maskBase64, aspectRatio);
          if (!fullResult) throw new Error('Vertex AI returned no image');

          // Stitch onto original using zone polygons as clip mask
          if (zones && zones.length > 0) {
            const stitched = await stitchWithBoundaryMask(imageBase64, fullResult.imageUrl, map, zones);
            fullResult.imageUrl = stitched;
          }

          setResult(fullResult);
          setProgress(100);
          setStatusMessage('Complete — full quality render');
          setIsRendering(false);
          return fullResult;
        }

        // ── 4-face mode: rotate camera to 4 bearings ──
        setStatusMessage('Capturing 4 views...');

        const originalBearing = map.getBearing();
        const originalPitch = map.getPitch();
        const originalCenter = map.getCenter();
        const originalZoom = map.getZoom();

        const captures: { label: 'front' | 'right' | 'rear' | 'left'; base64: string; bounds: [[number, number], [number, number], [number, number], [number, number]] }[] = [];

        for (let i = 0; i < FACE_BEARINGS.length; i++) {
          const face = FACE_BEARINGS[i];
          setStatusMessage(`Capturing ${face.label} view (${i + 1}/4)...`);

          await easeMapTo(map, face.bearing, 45);

          const base64 = await captureMapCanvasBase64(map);
          const bounds = getMapBounds(map);

          captures.push({ label: face.label, base64, bounds });
        }

        // Restore original camera
        map.easeTo({
          bearing: originalBearing,
          pitch: originalPitch,
          center: originalCenter,
          zoom: originalZoom,
          duration: 500,
        });

        setStatusMessage('Rendering all 4 faces... Please wait');

        const aspectRatio = computeAspectRatio(map);
        const renderPromises = captures.map((cap) =>
          renderSingle(cap.base64, cap.bounds, options, seed, undefined, aspectRatio)
            .then((result) => result ? { label: cap.label, bearing: FACE_BEARINGS.find(f => f.label === cap.label)!.bearing, result } as FaceRender : null)
            .catch(() => null),
        );

        const faceResults = await Promise.all(renderPromises);
        const successfulFaces = faceResults.filter((f): f is FaceRender => f !== null);

        setStatusMessage('Applying textures...');

        setFaceRenders(successfulFaces);

        const frontFace = successfulFaces.find((f) => f.label === 'front') ?? successfulFaces[0];
        if (frontFace) {
          setResult(frontFace.result);
        }

        setProgress(100);
        setStatusMessage(`Complete — ${successfulFaces.length}/4 faces rendered`);
        setIsRendering(false);
        return frontFace?.result ?? null;
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err);
        setError(msg);
        setIsRendering(false);
        setProgress(0);
        setStatusMessage('');
        return null;
      }
    },
    [renderSingle],
  );

  // ── Per-zone sequential rendering ───────────────────────────────────

  const renderPerZone = useCallback(
    async (map: MapboxMap, options: AIRenderOptions = {}): Promise<AIRenderResult | null> => {
      if (abortRef.current) abortRef.current.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      setIsRendering(true);
      setProgress(0);
      setError(null);
      setStatusMessage('Preparing per-zone render...');

      try {
        const zones = options.siteZones || [];
        if (zones.length === 0) {
          // Fall back to standard render if no zones
          return await render(map, options);
        }

        // Save original camera state
        const origCenter = map.getCenter();
        const origZoom = map.getZoom();
        const origBearing = map.getBearing();
        const origPitch = map.getPitch();

        // Capture the full-view original for compositing
        const originalBase64 = await captureMapCanvasBase64(map);
        const originalBounds = getMapBounds(map);
        const aspectRatio = computeAspectRatio(map);
        let cumulativeDataUri = `data:image/png;base64,${originalBase64}`;

        // Sort zones: ground-level first (parks, roads), then buildings on top.
        // This way buildings composite OVER parks, not under them.
        const ZONE_ORDER: Record<string, number> = {
          water: 0, green_space: 1, parking: 2,
          road: 3, development_area: 4, residential: 5, building: 6,
        };
        const renderableZones = zones
          .filter(z => z.zone_type !== 'site_boundary' && z.coordinates && z.coordinates.length >= 3)
          .sort((a, b) => (ZONE_ORDER[a.zone_type] ?? 99) - (ZONE_ORDER[b.zone_type] ?? 99));

        // Skip site_boundary — it's just the container, not renderable content.
        // Each inner zone already blends into the white site boundary via its prompt.
        const allZonesToRender = renderableZones;

        if (allZonesToRender.length === 0) {
          return await render(map, options);
        }

        const totalZones = allZonesToRender.length;
        const successfulZones: string[] = [];

        // Per-zone rendering: for each zone, hide all OTHER zone layers so Gemini
        // only sees one colored area on the white site boundary. This prevents
        // bleed between zones. Each zone gets its own screenshot, mask, and prompt.
        const ZONE_RENDER_LAYERS = [
          'site-zones-boundary-fill', 'site-zones-fill', 'site-zones-extrusion',
          'site-zones-outline', 'site-zones-selected', 'site-zones-labels',
        ];

        for (let i = 0; i < allZonesToRender.length; i++) {
          const zone = allZonesToRender[i];
          const zoneName = zone.name || zone.zone_type;
          setStatusMessage(`Rendering zone ${i + 1}/${totalZones}: ${zoneName}...`);
          setProgress(Math.round((i / totalZones) * 100));

          try {
            // Temporarily update the zone source to show ONLY this zone + site boundary
            const src = map.getSource('site-zones') as mapboxgl.GeoJSONSource | undefined;
            const allFeatures = zones.map(z => {
              if (!z.coordinates || z.coordinates.length < 3) return null;
              const zoneHeight = z.properties?.height_m != null ? Number(z.properties.height_m) : undefined;
              return {
                type: 'Feature' as const,
                properties: {
                  id: z.id,
                  color: z.id === zone.id ? (z.color || '#E03C31') : '#ffffff',
                  label: z.name || z.zone_type,
                  zone_type: z.zone_type,
                  ...(zoneHeight != null && { height: zoneHeight }),
                },
                geometry: {
                  type: 'Polygon' as const,
                  coordinates: [z.coordinates.map(([lng, lat]) => [lng, lat])],
                },
              };
            }).filter(Boolean);

            // Show only the current zone colored (others white/hidden)
            const soloFeatures = allFeatures.filter(f => {
              if (!f) return false;
              const fId = f.properties.id;
              // Keep site_boundary (white background) and the current zone
              return fId === zone.id || zones.find(z => z.id === fId)?.zone_type === 'site_boundary';
            });

            if (src) {
              src.setData({ type: 'FeatureCollection', features: soloFeatures as any[] });
              // Wait for map to re-render with solo zone
              await new Promise<void>(resolve => {
                map.once('idle', resolve);
                setTimeout(resolve, 500); // fallback
              });
            }

            // Capture screenshot with only this zone visible
            const zoneScreenshot = await captureMapCanvasBase64(map);

            // Generate single-zone mask at the current viewport
            const zoneMask = generateSingleZoneMask(map, zone);

            // Build zone-specific prompt
            const zonePrompt = buildSingleZonePrompt(zone, options);
            const negativePrompt = buildNegativePrompt(options);
            const guidanceScale = options.guidanceScale ?? 15;

            // Debug logging
            console.log(`[AIRender] Per-zone render ${i + 1}/${totalZones}: "${zoneName}" (${zone.zone_type})`);
            console.log(`[AIRender]   Prompt (${zonePrompt.length} chars):\n${zonePrompt}`);
            console.log(`[AIRender]   Aspect ratio: ${aspectRatio}, guidance: ${guidanceScale}`);

            // Call Gemini with screenshot showing ONLY this zone
            const { imageDataUri } = await callVertexAI(
              zoneScreenshot,
              zonePrompt,
              options.seed ?? Math.floor(Math.random() * 2147483647),
              aspectRatio,
              zoneMask,
              negativePrompt || undefined,
              guidanceScale,
            );

            // Composite this zone's render onto the cumulative result
            cumulativeDataUri = await compositeZoneRender(
              cumulativeDataUri,
              imageDataUri,
              map,
              zone,
            );

            successfulZones.push(zoneName);
            console.log(`[AIRender] Zone "${zoneName}" rendered successfully (${i + 1}/${totalZones})`);
          } catch (zoneErr) {
            console.warn(`[AIRender] Zone "${zoneName}" failed, skipping:`, zoneErr);
          }
        }

        // Restore full zone data after per-zone rendering
        const restoreFeatures = zones.map(z => {
          if (!z.coordinates || z.coordinates.length < 3) return null;
          const zoneHeight = z.properties?.height_m != null ? Number(z.properties.height_m) : undefined;
          return {
            type: 'Feature' as const,
            properties: {
              id: z.id,
              color: z.color || '#E03C31',
              label: z.name || z.zone_type,
              zone_type: z.zone_type,
              ...(zoneHeight != null && { height: zoneHeight }),
            },
            geometry: {
              type: 'Polygon' as const,
              coordinates: [z.coordinates.map(([lng, lat]) => [lng, lat])],
            },
          };
        }).filter(Boolean);
        const restoreSrc = map.getSource('site-zones') as mapboxgl.GeoJSONSource | undefined;
        if (restoreSrc) {
          restoreSrc.setData({ type: 'FeatureCollection', features: restoreFeatures as any[] });
        }

        // Restore original camera state
        map.jumpTo({
          center: origCenter,
          zoom: origZoom,
          bearing: origBearing,
          pitch: origPitch,
        });

        if (successfulZones.length === 0) {
          throw new Error('All per-zone renders failed');
        }

        const finalResult: AIRenderResult = {
          imageUrl: cumulativeDataUri,
          bounds: originalBounds,
          seed: options.seed,
          prompt: `Per-zone render: ${successfulZones.length}/${totalZones} zones`,
        };

        setResult(finalResult);
        setProgress(100);
        setStatusMessage(`Complete — ${successfulZones.length}/${totalZones} zones rendered`);
        setIsRendering(false);
        return finalResult;
      } catch (err: unknown) {
        if ((err as Error)?.name === 'AbortError') {
          setIsRendering(false);
          setProgress(0);
          setStatusMessage('');
          return null;
        }
        const msg = err instanceof Error ? err.message : String(err);
        console.error('[AIRender] Per-zone render failed:', msg);
        setError(msg);
        setIsRendering(false);
        setProgress(0);
        setStatusMessage('');
        return null;
      }
    },
    [render, renderSingle],
  );

  // ── Bearing-based face swapping ────────────────────────────────────

  const attachFaceSwapping = useCallback(
    (map: MapboxMap): (() => void) => {
      const SOURCE_PREFIX = 'ai-face-';
      const LAYER_PREFIX = 'ai-face-layer-';

      const updateVisibility = () => {
        if (faceRenders.length === 0) return;
        const activeFace = getActiveFaceLabel(map.getBearing());

        for (const face of faceRenders) {
          const layerId = LAYER_PREFIX + face.label;
          if (map.getLayer(layerId)) {
            map.setLayoutProperty(
              layerId,
              'visibility',
              face.label === activeFace ? 'visible' : 'none',
            );
          }
        }
      };

      for (const face of faceRenders) {
        const sourceId = SOURCE_PREFIX + face.label;
        const layerId = LAYER_PREFIX + face.label;

        if (map.getLayer(layerId)) map.removeLayer(layerId);
        if (map.getSource(sourceId)) map.removeSource(sourceId);

        try {
          map.addSource(sourceId, {
            type: 'image',
            url: face.result.imageUrl,
            coordinates: face.result.bounds,
          });
          map.addLayer({
            id: layerId,
            type: 'raster',
            source: sourceId,
            paint: {
              'raster-opacity': 0.95,
              'raster-fade-duration': 0,
            },
          });
        } catch (err) {
          console.warn(`[AIRender] Failed to add face layer ${face.label}:`, err);
        }
      }

      updateVisibility();
      map.on('rotate', updateVisibility);

      return () => {
        map.off('rotate', updateVisibility);
        for (const face of faceRenders) {
          const sourceId = SOURCE_PREFIX + face.label;
          const layerId = LAYER_PREFIX + face.label;
          try {
            if (map.getLayer(layerId)) map.removeLayer(layerId);
            if (map.getSource(sourceId)) map.removeSource(sourceId);
          } catch { /* map may be destroyed */ }
        }
      };
    },
    [faceRenders],
  );

  return {
    render,
    renderZone,
    renderPerZone,
    renderPreviews,
    renderFull,
    faceRenders,
    isRendering,
    progress,
    statusMessage,
    result,
    previews,
    selectedPreviewIndex,
    setSelectedPreviewIndex,
    error,
    reset,
    attachFaceSwapping,
  };
}
