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
import type { Map as MapboxMap } from 'mapbox-gl';
import type { SiteZone } from '@/types';
import { ZONE_TYPE_CONFIG } from '@/types';
import archetypeCatalog from '@/data/buildingArchetypes.json';
import openSpaceCatalogData from '@/data/openSpaceArchetypes.json';
import streetPathCatalogData from '@/data/streetPathArchetypes.json';
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
  /** Gemini model ID override (e.g. 'gemini-3-pro-image-preview') */
  model?: string;
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
  {
    id: 'photorealistic',
    label: 'Photo Realistic',
    strength: 0.65,
    prompt:
      'Hyper-realistic exterior architectural rendering with cinematic lighting. Golden hour sunlight casting realistic shadows. Highly detailed materials including reflective glass facades, textured concrete, natural stone, and weathered brick with visible grain. Lush realistic landscaping with mature trees showing individual leaf clusters. Sharp focus, 8k resolution, ray-traced lighting, professional architectural photography, high dynamic range, neutral 5500K white balance.',
    negative: 'cartoon, illustration, sketch, painting, artistic, stylized, watercolor, pencil, monochrome, low quality, blurry, text, watermark, people, pedestrians, human figures',
  },
  {
    id: 'drone-photography',
    label: 'Drone Photo',
    strength: 0.65,
    prompt:
      'Aerial drone photograph shot from 200 feet altitude, angled downward at 45 degrees. Building situated within realistic urban context with surrounding streets, neighboring rooftops, and parked vehicles. Sunny day with clear cast shadows, subtle atmospheric haze on distant objects, deep depth of field with everything sharp. High-resolution aerial photography, construction-complete, 8k.',
    negative: 'cartoon, illustration, sketch, painting, fish-eye, indoor, close-up, low quality, blurry, text, watermark, people, pedestrians',
  },
  {
    id: 'massing-study',
    label: 'Massing Study',
    strength: 0.65,
    prompt:
      'Architectural massing study rendered entirely as plain untextured matte white blocks on a neutral grey background. No windows, no doors, no material details. Focus strictly on volume, form, scale, and spatial relationships. Clean ambient occlusion lighting with sharp directional sunlight showing deep shadows where forms meet. Minimalist architectural diagram, white foam-board scale model style.',
    negative: 'photorealistic, color, materials, brick, glass, wood, vegetation, trees, people, cars, detailed, textured, realistic, windows, doors, low quality, blurry',
  },
  {
    id: 'site-plan',
    label: 'Site Plan',
    strength: 0.65,
    prompt:
      'Top-down 2D architectural site plan in strict orthographic projection looking straight down. Clean architectural linework with soft flat pastel colors. Stylized trees depicted as simple overlapping green circles viewed from above. Paved pathways in light grey, defined property lines, crisp shadows indicating building height. Roads as clean strips, landscaping in matte green, water features in blue. Professional urban planning drawing quality.',
    negative: 'perspective, 3D, oblique angle, horizon visible, photorealistic facades, eye-level, detailed buildings, low quality, blurry, noisy, text, watermark',
  },
  {
    id: 'ink-wash',
    label: 'Ink Wash',
    strength: 0.65,
    prompt:
      'Expressive architectural ink wash painting on heavy textured watercolor paper. Monochromatic black and grey tones with diluted ink gradients creating atmospheric perspective. Loose and fluid brushstrokes with bold confident calligraphic strokes defining edges. Wet ink bleeding softly at boundaries, white paper left untouched for sky and highlights. Ink splatter accents for vegetation, varying line weight from thick structural strokes to delicate details. Moody, artistic, and conceptual architectural illustration.',
    negative: 'photorealistic, photograph, digital, 3D render, perfect lines, computer generated, neon colors, cartoon, color, vibrant, low quality, blurry',
  },
  {
    id: 'charcoal',
    label: 'Charcoal',
    strength: 0.65,
    prompt:
      'Dramatic charcoal sketch on rough textured paper with deep black smudged shadows and expressive gestural line work. High contrast black and white, full tonal range from bright white paper to deep velvety black charcoal. Focus on the interplay of stark light and heavy shadow. Soft blended areas for atmosphere, sharp charcoal edge lines for architectural definition. Visible paper grain and charcoal particle texture throughout. Artistic and raw gallery-quality architectural drawing.',
    negative: 'photorealistic, photograph, color, painting, watercolor, digital, 3D render, cartoon, smooth, clean lines, low quality, blurry',
  },
  {
    id: 'marker-render',
    label: 'Marker Render',
    strength: 0.65,
    prompt:
      'Traditional architectural marker rendering with classic Copic marker style. Crisp fine-liner black ink outlines overlaid with layered transparent color strokes showing visible marker overlap and bleed effects. Bright optimistic lighting, vibrant saturated palette with warm and cool contrasts. Stylized architectural entourage and simplified trees. Selective areas of high detail dissolving into loose suggestive strokes at edges. White gel pen highlights on bare paper. Professional design presentation sketch aesthetic.',
    negative: 'photorealistic, photograph, digital, 3D render, watercolor bleeding, pencil shading, oil paint, dull colors, low quality, blurry',
  },
  {
    id: 'isometric',
    label: 'Isometric',
    strength: 0.65,
    prompt:
      'Isometric 3D architectural diagram with clean parallel projection and zero perspective distortion. Perfect 30-degree axonometric geometry. Rendered in smooth matte pastel colors with crisp hard edges and thin precise black outlines on every surface edge. No gradients, no shading, no cast shadows. Clear spatial layout with simplified geometric building forms. Vector-art aesthetic, highly detailed and precise. Contemporary tech-company infographic style, editorial design quality.',
    negative: 'photorealistic, photograph, perspective, vanishing point, gradients, shading, realistic shadows, texture, painterly, sketch, rough, low quality, blurry',
  },
  {
    id: 'woodblock',
    label: 'Wood Block',
    strength: 0.65,
    prompt:
      'Stylized woodblock print of an urban architectural scene. Bold thick black outlines defining all forms, flat and limited vintage color palette of 4-6 colors with crisp clean separation. Visible wood grain texture heavily integrated into the image. Zero gradation or blending within color areas. Graphic retro and stylized architectural illustration with strong balanced composition. Decorative patterned elements, depth through layered overlapping color planes. Museum-quality fine art print.',
    negative: 'photorealistic, photograph, digital, 3D render, gradients, shading, blending, watercolor bleeding, cartoon, smooth, modern, low quality, blurry',
  },
  {
    id: 'watercolour',
    label: 'Water Colour',
    strength: 0.65,
    prompt:
      'Beautiful watercolor architectural painting on highly textured watercolor paper. Soft bleeding edges where colors mix organically, translucent layered color washes with white paper glowing through as highlights. Bright airy and inviting atmosphere. Loose and artistic representation with pigment granulation and sedimentation in shadow areas. Faint underlying pencil construction lines visible beneath washes. Wet-on-wet bloom effects and cauliflower edges. Muted earth-tone palette with sage green, ochre, and ultramarine accents. Hand-painted competition entry by a master watercolourist.',
    negative: 'photorealistic, photograph, digital, sharp edges, perfect lines, 3D render, high contrast, neon colors, acrylic, oil paint, low quality, blurry',
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
    label: 'Photo Realistic',
    prompt: 'Hyper-realistic exterior architectural rendering with cinematic lighting. Golden hour sunlight casting realistic shadows. Highly detailed materials including reflective glass facades, textured concrete, natural stone, and weathered brick with visible grain. Lush realistic landscaping. Sharp focus, 8k resolution, ray-traced lighting, professional architectural photography.',
  },
  'drone-photography': {
    id: 'drone-photography',
    label: 'Drone Photo',
    prompt: 'Aerial drone photograph shot from 200 feet altitude, angled downward at 45 degrees. Realistic urban context with surrounding streets, neighboring rooftops, and parked vehicles. Sunny day with clear cast shadows, subtle atmospheric haze, deep depth of field. High-resolution aerial photography, construction-complete, 8k.',
  },
  'massing-study': {
    id: 'massing-study',
    label: 'Massing Study',
    prompt: 'Architectural massing study rendered entirely as plain untextured matte white blocks on neutral grey background. No windows, no doors, no material details. Focus on volume, form, scale, and spatial relationships. Clean ambient occlusion lighting, white foam-board scale model style.',
  },
  'site-plan': {
    id: 'site-plan',
    label: 'Site Plan',
    prompt: 'Top-down 2D architectural site plan in strict orthographic projection. Clean architectural linework with soft flat pastel colors. Stylized trees as simple green circles from above. Professional urban planning drawing quality.',
  },
  'ink-wash': {
    id: 'ink-wash',
    label: 'Ink Wash',
    prompt: 'Expressive architectural ink wash painting. Monochromatic black and grey tones with diluted ink gradients. Loose and fluid brushstrokes with bold calligraphic edges. Wet ink bleeding softly at boundaries. Moody, artistic, and conceptual architectural illustration.',
  },
  charcoal: {
    id: 'charcoal',
    label: 'Charcoal',
    prompt: 'Dramatic charcoal sketch on rough textured paper with deep black smudged shadows. High contrast black and white, full tonal range. Soft blended areas for atmosphere, sharp charcoal edge lines for architectural definition. Gallery-quality architectural drawing.',
  },
  'marker-render': {
    id: 'marker-render',
    label: 'Marker Render',
    prompt: 'Traditional architectural marker rendering with Copic marker style. Crisp fine-liner black ink outlines with layered transparent color strokes. Bright optimistic lighting, vibrant saturated palette. White gel pen highlights. Professional design presentation sketch aesthetic.',
  },
  isometric: {
    id: 'isometric',
    label: 'Isometric',
    prompt: 'Isometric 3D architectural diagram with clean parallel projection and zero perspective distortion. Perfect 30-degree axonometric geometry. Smooth matte pastel colors with crisp hard edges and thin black outlines. Vector-art aesthetic, contemporary infographic style.',
  },
  woodblock: {
    id: 'woodblock',
    label: 'Wood Block',
    prompt: 'Stylized woodblock print. Bold thick black outlines, flat limited vintage color palette of 4-6 colors with crisp separation. Visible wood grain texture. Zero gradation or blending. Graphic retro architectural illustration, museum-quality fine art print.',
  },
  watercolour: {
    id: 'watercolour',
    label: 'Water Colour',
    prompt: 'Beautiful watercolor architectural painting on textured paper. Soft bleeding edges where colors mix organically, translucent layered washes with white paper glowing through. Loose and artistic, pigment granulation in shadows. Muted earth-tone palette with sage green, ochre, and ultramarine accents.',
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
  // 3. Building zones get upward headroom expansion for 3D perspective height
  ctx.fillStyle = '#ffffff';
  let drawnCount = 0;

  const BUILDING_TYPES = ['building', 'residential', 'commercial', 'industrial', 'mixed_use'];
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

    // For building zones, expand the mask upward based on the actual building
    // height with a 3x safety margin. This gives the AI enough room to render
    // the full 3D building without giving it unlimited space to over-generate.
    if (BUILDING_TYPES.includes(zone.zone_type)) {
      const buildingHeight = zone.properties?.height_m ? Number(zone.properties.height_m)
        : zone.properties?.height ? Number(zone.properties.height) : 0;
      const headroom = buildingHeight > 0
        ? calculatePerspectiveHeadroom(map, buildingHeight)
        : 80 * dpr; // conservative default if no height specified
      if (headroom > 0) {
        const devicePixels = pixels.map(p => ({ x: p.x * dpr, y: p.y * dpr }));
        const minY = Math.min(...devicePixels.map(p => p.y));
        const minX = Math.min(...devicePixels.map(p => p.x));
        const maxX = Math.max(...devicePixels.map(p => p.x));
        const expandedTop = Math.max(0, minY - headroom);
        ctx.fillRect(minX, expandedTop, maxX - minX, minY - expandedTop);

        // Soft feathered edge at the top to blend with background
        const featherHeight = Math.min(20 * dpr, headroom * 0.25);
        if (featherHeight > 2) {
          const gradient = ctx.createLinearGradient(0, expandedTop, 0, expandedTop + featherHeight);
          gradient.addColorStop(0, 'rgba(0,0,0,1)');
          gradient.addColorStop(1, 'rgba(0,0,0,0)');
          ctx.globalCompositeOperation = 'destination-out';
          ctx.fillStyle = gradient;
          ctx.fillRect(minX, expandedTop, maxX - minX, featherHeight);
          ctx.globalCompositeOperation = 'source-over';
          ctx.fillStyle = '#ffffff'; // restore for next zone
        }
        console.log(`[AIRender] Mask: building headroom ${headroom.toFixed(0)}px (3x margin) for "${zone.name || zone.id}"`);
      }
    }

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
 * Stitch the AI-rendered result back onto the original screenshot using a
 * hybrid approach:
 *  1) Polygon clip to site boundary — controls horizontal extent
 *  2) Pixel-diff ABOVE building zones — captures 3D vertical extent
 *     without bleeding horizontally outside the boundary
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
  const dpr = window.devicePixelRatio || 1;

  // ── Step 1: Mask-based composite of AI result ──
  // Build a mask that includes the site boundary polygon AND extends upward
  // to the top of the canvas above each building zone (the "massive box"
  // approach). This ensures 3D buildings are never clipped at the ground-level
  // boundary, regardless of camera angle.
  const canvas = document.createElement('canvas');
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext('2d')!;

  ctx.drawImage(originalImg, 0, 0, w, h);

  const boundaries = siteZones.filter(z => z.zone_type === 'site_boundary' && z.coordinates && z.coordinates.length >= 3);
  const clipZones = boundaries.length > 0 ? boundaries : siteZones.filter(z => z.coordinates && z.coordinates.length >= 3);

  const BUILDING_TYPES_STITCH = ['building', 'residential', 'commercial', 'industrial', 'mixed_use'];
  const hasBuildingZones = siteZones.some(z =>
    BUILDING_TYPES_STITCH.includes(z.zone_type) && z.coordinates && z.coordinates.length >= 3
  );

  // Build a white-on-black mask: white = show AI render, black = keep original
  const maskCanvas = document.createElement('canvas');
  maskCanvas.width = w;
  maskCanvas.height = h;
  const maskCtx = maskCanvas.getContext('2d')!;
  maskCtx.fillStyle = '#000000';
  maskCtx.fillRect(0, 0, w, h);
  maskCtx.fillStyle = '#ffffff';

  // Draw site boundary polygon(s) into the mask
  for (const zone of clipZones) {
    const pixels = siteBoundaryToPixels(map, zone.coordinates!);
    maskCtx.beginPath();
    maskCtx.moveTo(pixels[0].x * dpr, pixels[0].y * dpr);
    for (let i = 1; i < pixels.length; i++) {
      maskCtx.lineTo(pixels[i].x * dpr, pixels[i].y * dpr);
    }
    maskCtx.closePath();
    maskCtx.fill();
  }

  // For each building zone, extend the mask upward by the building's
  // perspective headroom (bounded, not infinite) so the stitch captures
  // the 3D silhouette without over-compositing
  if (hasBuildingZones) {
    const bldgZones = siteZones.filter(z =>
      BUILDING_TYPES_STITCH.includes(z.zone_type) && z.coordinates && z.coordinates.length >= 3
    );
    for (const zone of bldgZones) {
      const pixels = siteBoundaryToPixels(map, zone.coordinates!);
      const devicePixels = pixels.map(p => ({ x: p.x * dpr, y: p.y * dpr }));

      const bldgHeight = zone.properties?.height_m ? Number(zone.properties.height_m)
        : zone.properties?.height ? Number(zone.properties.height) : 0;
      const headroom = bldgHeight > 0
        ? calculatePerspectiveHeadroom(map, bldgHeight)
        : 100 * dpr;

      const minX = Math.min(...devicePixels.map(p => p.x));
      const maxX = Math.max(...devicePixels.map(p => p.x));
      const minY = Math.min(...devicePixels.map(p => p.y));
      const expandedTop = Math.max(0, Math.floor(minY - headroom));
      maskCtx.fillRect(minX, expandedTop, maxX - minX, minY - expandedTop);
      console.log(`[AIRender] Stitch mask: ${headroom.toFixed(0)}px headroom for "${zone.name || zone.zone_type}"`);
    }
  }

  // Composite: draw AI render masked by the stitch mask
  const aiCanvas = document.createElement('canvas');
  aiCanvas.width = w;
  aiCanvas.height = h;
  const aiCtx = aiCanvas.getContext('2d')!;
  aiCtx.drawImage(renderedImg, 0, 0, w, h);
  // Keep only AI pixels where mask is white
  aiCtx.globalCompositeOperation = 'destination-in';
  aiCtx.drawImage(maskCanvas, 0, 0);
  // Draw the masked AI render on top of the original
  ctx.drawImage(aiCanvas, 0, 0);

  // ── Step 2: Pixel-diff ABOVE each building zone ──
  // For each building, compare original vs AI in the region directly above
  // the building's polygon (between its top edge and the headroom ceiling).
  // This captures the building's 3D silhouette without horizontal bleed.
  const BUILDING_TYPES = ['building', 'residential', 'commercial', 'industrial', 'mixed_use'];
  const buildingZones = siteZones.filter(z =>
    BUILDING_TYPES.includes(z.zone_type) && z.coordinates && z.coordinates.length >= 3
  );

  if (buildingZones.length > 0) {
    // Get pixel data from original and AI render for diff comparison
    const origTmpCanvas = document.createElement('canvas');
    origTmpCanvas.width = w;
    origTmpCanvas.height = h;
    const origTmpCtx = origTmpCanvas.getContext('2d')!;
    origTmpCtx.drawImage(originalImg, 0, 0, w, h);

    const rendTmpCanvas = document.createElement('canvas');
    rendTmpCanvas.width = w;
    rendTmpCanvas.height = h;
    const rendTmpCtx = rendTmpCanvas.getContext('2d')!;
    rendTmpCtx.drawImage(renderedImg, 0, 0, w, h);

    // Get the current composited result (with polygon-clipped ground)
    const currentData = ctx.getImageData(0, 0, w, h);
    const currentPx = currentData.data;

    const DIFF_THRESHOLD = 18;

    for (const zone of buildingZones) {
      const pixels = siteBoundaryToPixels(map, zone.coordinates!);
      const devicePixels = pixels.map(p => ({ x: p.x * dpr, y: p.y * dpr }));

      const bldgHeight = zone.properties?.height_m ? Number(zone.properties.height_m)
        : zone.properties?.height ? Number(zone.properties.height) : 0;
      const headroom = bldgHeight > 0
        ? calculatePerspectiveHeadroom(map, bldgHeight)
        : 100 * dpr;

      const minX = Math.min(...devicePixels.map(p => p.x));
      const maxX = Math.max(...devicePixels.map(p => p.x));
      const minY = Math.min(...devicePixels.map(p => p.y));
      const expandedTop = Math.max(0, Math.floor(minY - headroom));

      // Only process the region ABOVE the polygon (between expandedTop and minY)
      // The polygon interior is already handled by the site boundary clip in Step 1
      const regionX = Math.max(0, Math.floor(minX));
      const regionR = Math.min(w, Math.ceil(maxX));
      const regionY = expandedTop;
      const regionB = Math.floor(minY);
      if (regionB <= regionY || regionR <= regionX) continue;

      const rw = regionR - regionX;
      const rh = regionB - regionY;

      const origRegion = origTmpCtx.getImageData(regionX, regionY, rw, rh);
      const rendRegion = rendTmpCtx.getImageData(regionX, regionY, rw, rh);

      for (let row = 0; row < rh; row++) {
        for (let col = 0; col < rw; col++) {
          const idx = (row * rw + col) * 4;
          const dr = Math.abs(origRegion.data[idx] - rendRegion.data[idx]);
          const dg = Math.abs(origRegion.data[idx + 1] - rendRegion.data[idx + 1]);
          const db = Math.abs(origRegion.data[idx + 2] - rendRegion.data[idx + 2]);

          if (Math.max(dr, dg, db) > DIFF_THRESHOLD) {
            const globalIdx = ((regionY + row) * w + (regionX + col)) * 4;
            currentPx[globalIdx] = rendRegion.data[idx];
            currentPx[globalIdx + 1] = rendRegion.data[idx + 1];
            currentPx[globalIdx + 2] = rendRegion.data[idx + 2];
            currentPx[globalIdx + 3] = rendRegion.data[idx + 3];
          }
        }
      }

      console.log(`[AIRender] Building "${zone.name || zone.zone_type}" pixel-diff: ${rw}x${rh}px above polygon`);
    }

    ctx.putImageData(currentData, 0, 0);
  }

  console.log(`[AIRender] Hybrid stitch: polygon clip + pixel-diff for ${buildingZones.length} building(s)`);
  return canvas.toDataURL('image/png');
}

/**
 * Calculate the upward pixel expansion needed for a building mask
 * to accommodate 3D perspective height. In an oblique aerial view,
 * a tall building's roof shifts "up-screen" relative to its footprint.
 */
function calculatePerspectiveHeadroom(
  map: MapboxMap,
  buildingHeightM: number,
): number {
  const pitch = map.getPitch(); // camera pitch in degrees (0=top-down, 60=oblique)
  if (pitch < 5 || buildingHeightM <= 0) return 0;

  // Estimate pixels-per-meter at current zoom level using map projection
  // Project two points 100m apart vertically to get screen-space scale
  const center = map.getCenter();
  const p1 = map.project(center);
  const latOffset = 0.0009; // ~100m in latitude
  const p2 = map.project({ lng: center.lng, lat: center.lat + latOffset });
  const pixelsPer100m = Math.abs(p2.y - p1.y);
  const pixelsPerMeter = pixelsPer100m / 100;

  // Vertical shift: building height projected onto screen Y-axis.
  // At higher pitch angles, buildings appear to lean more "up-screen".
  // sin(pitch) is correct: at pitch=0 (top-down) shift is 0,
  // at pitch=60° (oblique) shift is large.
  const pitchRad = pitch * Math.PI / 180;
  const verticalShift = buildingHeightM * pixelsPerMeter * Math.sin(pitchRad);

  const dpr = window.devicePixelRatio || 1;
  // Apply 2.0x safety margin to handle perspective distortion at edges
  // and ensure buildings are fully captured at steep oblique angles
  return verticalShift * dpr * 2.0;
}

/**
 * Generate a binary mask for a SINGLE zone polygon.
 * White (255) = the zone's footprint, Black (0) = everything else.
 * For building zones, the mask is expanded upward to accommodate
 * the 3D perspective height of the building.
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
    const isBuilding = ['building', 'residential', 'commercial', 'industrial', 'mixed_use'].includes(zone.zone_type);
    const buildingHeight = zone.properties?.height_m ? Number(zone.properties.height_m)
      : zone.properties?.height ? Number(zone.properties.height) : 0;

    ctx.fillStyle = '#ffffff';
    ctx.beginPath();

    if (isBuilding && buildingHeight > 0) {
      // PERSPECTIVE-EXPANDED MASK: expand the top edge upward to give
      // Gemini room to render the building's full 3D height.
      // Bottom and sides stay locked to the polygon; top extends upward.
      const headroom = calculatePerspectiveHeadroom(map, buildingHeight);
      console.log(`[AIRender] Building mask headroom: ${headroom.toFixed(0)}px for ${buildingHeight}m height, pitch=${map.getPitch().toFixed(1)}°`);

      // Find the top-most Y coordinate of the polygon
      const devicePixels = pixels.map(p => ({ x: p.x * dpr, y: p.y * dpr }));
      const minY = Math.min(...devicePixels.map(p => p.y));

      // Draw the original polygon
      ctx.moveTo(devicePixels[0].x, devicePixels[0].y);
      for (let i = 1; i < devicePixels.length; i++) {
        ctx.lineTo(devicePixels[i].x, devicePixels[i].y);
      }
      ctx.closePath();
      ctx.fill();

      // Draw an expanded rectangle above the polygon for headroom
      // This covers from the polygon's top edge up by the headroom amount
      const minX = Math.min(...devicePixels.map(p => p.x));
      const maxX = Math.max(...devicePixels.map(p => p.x));
      const expandedTop = Math.max(0, minY - headroom);
      ctx.fillRect(minX, expandedTop, maxX - minX, minY - expandedTop);

      // Apply soft feathered edge at the very top (gradient from white to black)
      // This prevents a hard seam between building roof and background
      const featherHeight = Math.min(20 * dpr, headroom * 0.3);
      if (featherHeight > 2) {
        const gradient = ctx.createLinearGradient(0, expandedTop, 0, expandedTop + featherHeight);
        gradient.addColorStop(0, 'rgba(0,0,0,1)');   // black (transparent/keep)
        gradient.addColorStop(1, 'rgba(0,0,0,0)');    // transparent (white shows through)
        ctx.globalCompositeOperation = 'destination-out';
        ctx.fillStyle = gradient;
        ctx.fillRect(minX, expandedTop, maxX - minX, featherHeight);
        ctx.globalCompositeOperation = 'source-over';
      }
    } else {
      // Standard mask: just the polygon footprint
      ctx.moveTo(pixels[0].x * dpr, pixels[0].y * dpr);
      for (let i = 1; i < pixels.length; i++) {
        ctx.lineTo(pixels[i].x * dpr, pixels[i].y * dpr);
      }
      ctx.closePath();
      ctx.fill();
    }
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
 * Generate a combined binary mask for MULTIPLE zones.
 * White (255) = union of all provided zone polygons, Black (0) = keep.
 * Used in Pass 1 to mask all ground-level zones at once.
 */
function generateCombinedMask(
  map: MapboxMap,
  zones: SiteZone[],
): string {
  const mapCanvas = map.getCanvas();
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

  // Draw each zone polygon as white (area to edit)
  ctx.fillStyle = '#ffffff';
  let drawnCount = 0;

  for (const zone of zones) {
    if (!zone.coordinates || zone.coordinates.length < 3) continue;
    const pixels = siteBoundaryToPixels(map, zone.coordinates);

    ctx.beginPath();
    ctx.moveTo(pixels[0].x * dpr, pixels[0].y * dpr);
    for (let i = 1; i < pixels.length; i++) {
      ctx.lineTo(pixels[i].x * dpr, pixels[i].y * dpr);
    }
    ctx.closePath();
    ctx.fill();
    drawnCount++;
  }

  // Debug: count white pixels
  const imgData = ctx.getImageData(0, 0, w, h).data;
  let whiteCount = 0;
  for (let i = 0; i < imgData.length; i += 4) {
    if (imgData[i] > 128) whiteCount++;
  }
  const totalPx = w * h;
  console.log(`[AIRender] Combined mask: ${w}x${h}, ${drawnCount} zones drawn, white=${whiteCount}/${totalPx} (${((whiteCount / totalPx) * 100).toFixed(1)}%)`);

  return maskCanvas.toDataURL('image/png').split(',')[1];
}

/**
 * Build a zone-specific prompt for per-zone rendering.
 * Simple, natural language — Gemini handles spatial reasoning natively.
 */

// ── Color utilities for variant-specific polygon colors ──────────────
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

function hslToHex(h: number, s: number, l: number): string {
  h = ((h % 360) + 360) % 360;
  s = Math.max(0, Math.min(100, s)) / 100;
  l = Math.max(0, Math.min(100, l)) / 100;
  const a = s * Math.min(l, 1 - l);
  const f = (n: number) => {
    const k = (n + h / 30) % 12;
    const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
    return Math.round(255 * color).toString(16).padStart(2, '0');
  };
  return `#${f(0)}${f(8)}${f(4)}`;
}

function shiftColorForVariant(baseHex: string, variantIndex: number): string {
  const lightnessShifts = [-8, -3, 3, 8];
  const hueShifts = [-5, 5, -10, 10];
  const idx = Math.max(0, Math.min(3, variantIndex));
  const [h, s, l] = hexToHsl(baseHex);
  return hslToHex(h + hueShifts[idx], s, l + lightnessShifts[idx]);
}

function colorName(hex: string): string {
  const genericMap: Record<string, string> = {
    '#E03C31': 'red', '#e03c31': 'red',
    '#FF6B6B': 'coral', '#ff6b6b': 'coral',
    '#E8927C': 'salmon', '#e8927c': 'salmon',
    '#F5A623': 'amber', '#f5a623': 'amber',
    '#FFD700': 'gold', '#ffd700': 'gold',
    '#FFEB3B': 'yellow', '#ffeb3b': 'yellow',
    '#F0E68C': 'khaki', '#f0e68c': 'khaki',
    '#4CAF50': 'green', '#4caf50': 'green',
    '#66BB6A': 'spring green', '#66bb6a': 'spring green',
    '#2E7D32': 'forest green', '#2e7d32': 'forest green',
    '#009688': 'teal',
    '#4169E1': 'royal blue', '#4169e1': 'royal blue',
    '#3F51B5': 'indigo', '#3f51b5': 'indigo',
    '#2196F3': 'blue', '#2196f3': 'blue',
    '#9C27B0': 'purple', '#9c27b0': 'purple',
    '#795548': 'brown',
    '#607D8B': 'blue grey', '#607d8b': 'blue grey',
    '#BDBDBD': 'silver', '#bdbdbd': 'silver',
    '#ffffff': 'white', '#FFFFFF': 'white',
  };
  if (genericMap[hex]) return genericMap[hex];
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
    return `${lightness}${hueName} (${hex})`;
  } catch {
    return hex;
  }
}

/**
 * Build a GROUND PLANE prompt for Pass 1 of the two-pass pipeline.
 * Renders parks, roads, plazas — no vertical structures.
 */
function buildGroundPlanePrompt(groundZones: SiteZone[], options: AIRenderOptions): string {
  const styleId = options.renderStyleId || options.style || 'photorealistic';
  const styleMod = GEMINI_STYLE_MODIFIERS[styleId];
  const isArtistic = ['watercolour', 'ink-wash', 'charcoal', 'marker-render', 'isometric', 'woodblock', 'massing-study', 'site-plan'].includes(styleId);

  const zoneDescriptions = groundZones.map(z => {
    const info = getZoneArchetypeInfo(z);
    const desc = buildArchetypeDescription(info, z.zone_type);
    const color = colorName(z.color || '#4CAF50');
    return `The ${color} polygon is a ${desc}`;
  });

  const parts: string[] = [];

  parts.push(
    'Aerial photograph captured by a DJI drone at approximately 60 meters altitude, looking down at an oblique angle.',
    `In this image, colored polygon overlays mark proposed landscape zones on an empty site (the white area).`,
  );

  // Zone descriptions as narrative
  parts.push(zoneDescriptions.join('. ') + '.');

  parts.push(
    'Transform each colored zone into its described landscape, perfectly filling the colored area.',
  );

  // CRITICAL RULES for zone containment
  parts.push(
    'CRITICAL RULES:',
    '1. Each zone\'s landscape must stay strictly inside its colored polygon boundary — zero bleed into any neighboring zone.',
    '2. Treat every polygon edge as a hard physical curb or wall that no element may cross.',
    '3. Match each polygon by its specific color and fill only that polygon with the described content.',
    '4. The landscape must be entirely ground-level: an empty site with only grass, trees, paths, and paving.',
    '5. Do not generate any people, pedestrians, or human figures.',
    '6. Do not generate any buildings, walls, vertical structures, or rooftops.',
  );

  if (isArtistic && styleMod) {
    parts.push(`Render in ${styleMod.label} style: ${styleMod.prompt}`);
  } else if (styleMod && styleId !== 'photorealistic') {
    parts.push(`Render style: ${styleMod.prompt}`);
  }

  parts.push('Keep all satellite imagery outside the white site boundary exactly as it is.');

  if (options.customPrompt?.trim()) {
    parts.push(options.customPrompt.trim());
  }

  return parts.join(' ');
}

/**
 * Build a BUILDING prompt for Pass 2 of the two-pass pipeline.
 * Renders a single building onto the already-rendered ground plane.
 * Uses narrative prose following the formula: Subject + Environment + Materials + Lighting + Camera.
 */
function buildBuildingPrompt(zone: SiteZone, options: AIRenderOptions): string {
  const archetypeInfo = getZoneArchetypeInfo(zone);
  const zoneColor = colorName(getZoneRenderColor(zone.id, zone.color || '#E03C31'));

  // Build narrative description from archetype metadata
  const floors = zone.properties?.floors ?? zone.properties?.num_floors;
  const heightM = zone.properties?.height_m ?? zone.properties?.height;
  const floorText = floors ? `${floors}-story` : heightM ? `${heightM}m tall` : 'multi-story';

  // Descriptive text from the zone properties (auto-populated from archetype card)
  const userDesc = (zone.properties?.description_text as string) || '';

  // Archetype-derived narrative
  const narrativeParts: string[] = [];
  if (archetypeInfo.archetypeTitle) {
    narrativeParts.push(`A completed ${floorText} ${archetypeInfo.archetypeTitle} building`);
  } else {
    narrativeParts.push(`A completed ${floorText} commercial building`);
  }
  if (archetypeInfo.facadeDescription) narrativeParts.push(`with ${archetypeInfo.facadeDescription.toLowerCase()}`);
  if (archetypeInfo.roofDescription) narrativeParts.push(`topped by ${archetypeInfo.roofDescription.toLowerCase()}`);
  if (archetypeInfo.materials) narrativeParts.push(`Materials: ${archetypeInfo.materials}`);
  if (archetypeInfo.colorScheme) narrativeParts.push(`Color palette: ${archetypeInfo.colorScheme}`);

  const buildingNarrative = narrativeParts.join('. ') + '.';

  // Style
  const styleId = options.renderStyleId || options.style || 'photorealistic';
  const styleMod = GEMINI_STYLE_MODIFIERS[styleId];
  const isArtistic = ['watercolour', 'ink-wash', 'charcoal', 'marker-render', 'isometric', 'woodblock', 'massing-study', 'site-plan'].includes(styleId);

  const parts: string[] = [];

  // Narrative prose prompt — Subject + Environment + Materials + Lighting + Camera
  parts.push(
    `Using the provided landscape image, render a building on the ${zoneColor} colored footprint.`,
    buildingNarrative,
  );

  if (userDesc) {
    parts.push(userDesc);
  }

  parts.push(
    `The ${zoneColor} polygon is the building's absolute ground foundation. The building sits on the already-rendered park and streetscape — its base shadows should blend naturally onto the surrounding grass and pathways.`,
    `Treat the ${zoneColor} footprint as the ground-level base only. Render the full vertical 3D mass and roofline extending naturally into the sky above, respecting aerial perspective. Do not clip the architecture at any boundary line.`,
    `Replace every ${zoneColor} pixel with building facade, structure, or ground-plane landscaping. No colored overlay should remain visible.`,
    `Do not let building materials bleed into the surrounding grass, pathways, or other zones. Keep strict horizontal containment at the foundation level.`,
    `CRITICAL: The building's walls, shadows, and all architectural elements must stay strictly within the horizontal boundaries of the colored polygon footprint. No part of the building may extend sideways beyond the polygon perimeter.`,
  );

  if (isArtistic && styleMod) {
    parts.push(`Render in ${styleMod.label} style: ${styleMod.prompt}`);
  } else if (styleMod && styleId !== 'photorealistic') {
    parts.push(`Render style: ${styleMod.prompt}`);
  } else {
    parts.push('Warm afternoon sunlight from the southwest casts crisp architectural shadows. Captured with a DJI drone at 60m altitude, matching the existing satellite imagery perspective and lighting.');
  }

  parts.push(
    'If an archetype reference image is provided, apply its exact architectural style, facade materials, ' +
    'window patterns, and material textures to the building. The reference image shows what the finished ' +
    'building should look like — match it as closely as possible while respecting the aerial perspective.',
  );

  parts.push('Keep everything else in the image exactly the same, preserving the original style, lighting, and composition.');

  if (options.customPrompt?.trim()) {
    parts.push(options.customPrompt.trim());
  }

  return parts.join(' ');
}

/**
 * Legacy single-zone prompt builder (used when two-pass is not applicable).
 */
function _buildSingleZonePrompt(zone: SiteZone, options: AIRenderOptions, _allZones?: SiteZone[]): string {
  const isBuilding = ['building', 'residential', 'commercial', 'industrial', 'mixed_use'].includes(zone.zone_type);
  if (isBuilding) {
    return buildBuildingPrompt(zone, options);
  }
  return buildGroundPlanePrompt([zone], options);
}
void _buildSingleZonePrompt; // suppress unused warning — kept for fallback use

/**
 * Build a natural-language description from archetype metadata.
 * Used by both single-zone and multi-zone prompt builders.
 */
function buildArchetypeDescription(
  info: ReturnType<typeof getZoneArchetypeInfo>,
  zoneType: string,
): string {
  if (info.mapOverlayPrompt) return info.mapOverlayPrompt;

  const isRoad = zoneType === 'road' || zoneType === 'street' || zoneType === 'path';
  const isPark = zoneType === 'green_space' || zoneType === 'park' || zoneType === 'plaza';

  if (info.archetypeTitle) {
    if (isRoad && info.corridorDescription) {
      // Road/pathway: use corridor-specific metadata
      const parts = [info.archetypeTitle.toLowerCase() + ' streetscape'];
      parts.push(info.corridorDescription);
      if (info.materials) parts.push(`Materials: ${info.materials}`);
      return parts.join('. ');
    }

    if (isPark) {
      // Park/green space: use landscape-oriented description
      const parts = [info.archetypeTitle.toLowerCase() + ' landscape'];
      if (info.corridorDescription) parts.push(info.corridorDescription);
      if (info.publicRealm) parts.push(info.publicRealm);
      if (info.materials) parts.push(info.materials);
      return parts.join('. ');
    }

    // Building: use facade/roof metadata
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
 * For ground-level zones: strict polygon clip.
 * For buildings: polygon clip for footprint + pixel-diff above for 3D height.
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
  ctx.drawImage(baseImg, 0, 0, w, h);

  if (!zone.coordinates || zone.coordinates.length < 3) {
    return canvas.toDataURL('image/png');
  }

  const dpr = window.devicePixelRatio || 1;
  const pixels = siteBoundaryToPixels(map, zone.coordinates);
  const devicePixels = pixels.map(p => ({ x: p.x * dpr, y: p.y * dpr }));
  const isBuilding = ['building', 'residential', 'commercial', 'industrial', 'mixed_use'].includes(zone.zone_type);

  // Step 1: Mask-based composite for the footprint + building height
  // For buildings, the mask extends to the top of the canvas so the full
  // 3D silhouette is captured regardless of camera angle.
  const maskCanvas = document.createElement('canvas');
  maskCanvas.width = w;
  maskCanvas.height = h;
  const maskCtx = maskCanvas.getContext('2d')!;
  maskCtx.fillStyle = '#000000';
  maskCtx.fillRect(0, 0, w, h);
  maskCtx.fillStyle = '#ffffff';

  // Draw zone footprint polygon
  maskCtx.beginPath();
  maskCtx.moveTo(devicePixels[0].x, devicePixels[0].y);
  for (let i = 1; i < devicePixels.length; i++) {
    maskCtx.lineTo(devicePixels[i].x, devicePixels[i].y);
  }
  maskCtx.closePath();
  maskCtx.fill();

  // For buildings, extend mask upward by perspective headroom (bounded)
  if (isBuilding) {
    const bldgH = zone.properties?.height_m ? Number(zone.properties.height_m)
      : zone.properties?.height ? Number(zone.properties.height) : 0;
    const hr = bldgH > 0
      ? calculatePerspectiveHeadroom(map, bldgH)
      : 100 * dpr;
    if (hr > 0) {
      const mnX = Math.min(...devicePixels.map(p => p.x));
      const mxX = Math.max(...devicePixels.map(p => p.x));
      const mnY = Math.min(...devicePixels.map(p => p.y));
      const expTop = Math.max(0, Math.floor(mnY - hr));
      maskCtx.fillRect(mnX, expTop, mxX - mnX, mnY - expTop);
    }
  }

  // Composite: AI render masked, then drawn onto base
  const aiCanvas = document.createElement('canvas');
  aiCanvas.width = w;
  aiCanvas.height = h;
  const aiCtx = aiCanvas.getContext('2d')!;
  aiCtx.drawImage(renderedImg, 0, 0, w, h);
  aiCtx.globalCompositeOperation = 'destination-in';
  aiCtx.drawImage(maskCanvas, 0, 0);
  ctx.drawImage(aiCanvas, 0, 0);

  // Step 2: For buildings, pixel-diff above the polygon for 3D height
  if (isBuilding) {
    const bldgHeight = zone.properties?.height_m ? Number(zone.properties.height_m)
      : zone.properties?.height ? Number(zone.properties.height) : 0;
    const headroom = bldgHeight > 0
      ? calculatePerspectiveHeadroom(map, bldgHeight)
      : 100 * dpr;

    const minX = Math.min(...devicePixels.map(p => p.x));
    const maxX = Math.max(...devicePixels.map(p => p.x));
    const minY = Math.min(...devicePixels.map(p => p.y));
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
      console.log(`[AIRender] compositeZoneRender: BUILDING "${zone.name || zone.zone_type}" — polygon clip + pixel-diff ${rw}x${rh}px above`);
    } else {
      console.log(`[AIRender] compositeZoneRender: BUILDING "${zone.name || zone.zone_type}" — polygon clip only (no headroom region)`);
    }
  } else {
    console.log(`[AIRender] compositeZoneRender: ${zone.zone_type} — strict polygon clip`);
  }

  return canvas.toDataURL('image/png');
}

/** Get the current visible bounds as image-source coordinates: [[W,N],[E,N],[E,S],[W,S]]
 *  When headroomPixels is provided, the NORTH edge is expanded upward to accommodate
 *  3D building height in oblique/pitched views, preventing tall buildings from being clipped.
 */
function getMapBounds(
  map: MapboxMap,
  headroomPixels = 0,
): [[number, number], [number, number], [number, number], [number, number]] {
  const bounds = map.getBounds()!;
  let north = bounds.getNorth();

  if (headroomPixels > 0) {
    // Convert pixel headroom to a latitude offset:
    // Take the top-center pixel of the viewport, subtract headroomPixels from Y,
    // then unproject back to lat/lng to get the expanded north latitude.
    const canvas = map.getCanvas();
    const topCenterX = canvas.clientWidth / 2;
    const topCenterY = 0;
    const expandedPoint = map.unproject([topCenterX, topCenterY - headroomPixels]);
    north = expandedPoint.lat;
  }

  const nw: [number, number] = [bounds.getWest(), north];
  const ne: [number, number] = [bounds.getEast(), north];
  const se: [number, number] = [bounds.getEast(), bounds.getSouth()];
  const sw: [number, number] = [bounds.getWest(), bounds.getSouth()];
  return [nw, ne, se, sw];
}

/** Calculate the maximum building height from a set of zones, returning pixel headroom needed */
function getMaxBuildingHeadroom(map: MapboxMap, zones?: SiteZone[]): number {
  if (!zones || zones.length === 0) return 0;

  const BUILDING_TYPES = ['building', 'residential', 'commercial', 'industrial', 'mixed_use'];
  let maxHeight = 0;

  for (const z of zones) {
    if (!BUILDING_TYPES.includes(z.zone_type)) continue;
    const h = z.properties?.height_m ? Number(z.properties.height_m)
      : z.properties?.height ? Number(z.properties.height) : 0;
    if (h > maxHeight) maxHeight = h;
  }

  if (maxHeight <= 0) return 0;
  return calculatePerspectiveHeadroom(map, maxHeight);
}

/**
 * Post-composite cleanup: restore original pixels inside OTHER zones' polygons.
 * Prevents Zone A's render from visually intruding into Zone B.
 * @param renderedDataUri  The cumulative render after compositing the current zone
 * @param preRenderDataUri The cumulative render BEFORE compositing (original pixels)
 * @param map              Mapbox map for coordinate projection
 * @param currentZone      The zone that was just rendered
 * @param allZones         All site zones
 */
async function cleanupZoneBleed(
  renderedDataUri: string,
  preRenderDataUri: string,
  map: MapboxMap,
  currentZone: SiteZone,
  allZones: SiteZone[],
): Promise<string> {
  // Collect other zones (not the current one, not site_boundary)
  const otherZones = allZones.filter(
    z => z.id !== currentZone.id
      && z.zone_type !== 'site_boundary'
      && z.coordinates && z.coordinates.length >= 3
  );
  if (otherZones.length === 0) return renderedDataUri;

  const [renderedImg, preRenderImg] = await Promise.all([
    loadImage(renderedDataUri),
    loadImage(preRenderDataUri),
  ]);

  const w = renderedImg.naturalWidth;
  const h = renderedImg.naturalHeight;
  const dpr = window.devicePixelRatio || 1;

  const canvas = document.createElement('canvas');
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext('2d')!;

  // Start with the rendered result
  ctx.drawImage(renderedImg, 0, 0, w, h);

  // For each other zone, clip to its polygon and draw the pre-render pixels
  // This restores original content inside neighboring zones
  for (const otherZone of otherZones) {
    const pixels = siteBoundaryToPixels(map, otherZone.coordinates!);
    const devicePixels = pixels.map(p => ({ x: p.x * dpr, y: p.y * dpr }));
    if (devicePixels.length < 3) continue;

    ctx.save();
    ctx.beginPath();
    ctx.moveTo(devicePixels[0].x, devicePixels[0].y);
    for (let i = 1; i < devicePixels.length; i++) {
      ctx.lineTo(devicePixels[i].x, devicePixels[i].y);
    }
    ctx.closePath();
    ctx.clip();
    ctx.drawImage(preRenderImg, 0, 0, w, h);
    ctx.restore();
  }

  console.log(`[AIRender] cleanupZoneBleed: restored ${otherZones.length} neighboring zone(s)`);
  return canvas.toDataURL('image/png');
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
  descriptionText?: string; // User-editable description from the text box
  floors?: number;          // Number of stories
  heightM?: number;         // Building height in meters
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
  // Road/path specific
  corridorDescription?: string;
  surfaceType?: string;
  plantingCharacter?: string;
  edgeConditions?: string;
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

    // Build a rich facade description from facadeDetail (buildings)
    const facadeParts: string[] = [];
    if (fd.primaryMaterial) facadeParts.push(fd.primaryMaterial);
    if (fd.groundFloor) facadeParts.push(`Ground floor: ${fd.groundFloor}`);
    if (fd.upperFloors) facadeParts.push(`Upper floors: ${fd.upperFloors}`);
    if (fd.cornice) facadeParts.push(`Cornice: ${fd.cornice}`);
    if (fd.colorScheme) facadeParts.push(`Colors: ${fd.colorScheme}`);

    // Build roof description (buildings)
    const roofParts: string[] = [];
    if (rd.form) roofParts.push(rd.form);
    if (rd.material) roofParts.push(rd.material);
    if (rd.features) roofParts.push(rd.features);
    if (rd.aerialAppearance) roofParts.push(`Aerial: ${rd.aerialAppearance}`);

    // Materials list
    const materials = Array.isArray(sp.materials) ? sp.materials.join(', ') : sp.materials;

    // Road/corridor specific fields from styleProfile
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
      materials: materials || undefined,
      massing: sp.massing || undefined,
      heightTendency: sp.heightTendency || undefined,
      publicRealm: sp.publicRealm || undefined,
      mapOverlayPrompt: entry.renderPrompt?.mapOverlay || entry.prompt?.subject || undefined,
      colorScheme: fd.colorScheme || undefined,
      aerialAppearance: rd.aerialAppearance || undefined,
      corridorDescription: corridorParts.length > 0 ? corridorParts.join('. ') : undefined,
      surfaceType: sp.surfaceType || undefined,
      plantingCharacter: sp.plantingCharacter || undefined,
      edgeConditions: sp.edgeConditions || undefined,
    };
  }

  return {};
}

/**
 * Palette of visually distinct variant colors for disambiguating multiple
 * unassigned building zones that would otherwise share the same default red
 * (#E03C31). Only used temporarily during AI rendering -- the zone's persisted
 * color in the database is never modified.
 */
const BUILDING_VARIANT_PALETTE = [
  '#E03C31', // red (original default -- first building keeps this)
  '#C62828', // dark red
  '#D84315', // deep orange
  '#AD1457', // dark pink
  '#6A1B9A', // deep purple
  '#4527A0', // indigo
  '#B71C1C', // crimson
  '#E65100', // burnt orange
];

/**
 * Maps zone IDs to reassigned variant colors for the current render session.
 * Populated by collectZonePromptEntries and consumed by the screenshot
 * capture code to ensure the map overlay color matches the prompt text.
 */
let _zoneColorOverrides: Map<string, string> = new Map();

/**
 * Get the render-time color override for a zone, if any.
 * Returns the variant color assigned during prompt collection, or the
 * provided fallback if no override was needed.
 */
function getZoneRenderColor(zoneId: string, fallback: string): string {
  return _zoneColorOverrides.get(zoneId) ?? fallback;
}

/**
 * Build zone-by-zone entries for the structured prompt.
 * Maps each non-boundary zone to its color, type, and archetype metadata.
 *
 * When multiple building zones share the same default color, each is assigned
 * a distinct variant color so Gemini can distinguish them in the prompt.
 */
function collectZonePromptEntries(zones: SiteZone[]): ZonePromptEntry[] {
  const rawEntries: { entry: ZonePromptEntry; zoneId: string }[] = [];
  _zoneColorOverrides = new Map();

  const BUILDING_TYPES = ['building', 'residential', 'commercial', 'industrial', 'mixed_use'];

  for (const zone of zones) {
    if (!zone.coordinates?.length) continue;

    // Include site_boundary with a special contextual infill entry
    if (zone.zone_type === 'site_boundary') {
      rawEntries.push({
        zoneId: zone.id,
        entry: {
          color: zone.color || '#F5D63D',
          zoneType: 'site_boundary',
          zoneName: 'Site Boundary / Contextual Infill',
        },
      });
      continue;
    }

    const config = ZONE_TYPE_CONFIG[zone.zone_type];
    const color = zone.color || config?.color || '#888888';
    const archetypeInfo = getZoneArchetypeInfo(zone);

    // Extract scale info for buildings
    const floors = zone.properties?.floors ?? zone.properties?.num_floors;
    const heightM = zone.properties?.height_m ?? zone.properties?.height;

    rawEntries.push({
      zoneId: zone.id,
      entry: {
        color,
        zoneType: zone.zone_type,
        zoneName: zone.name || config?.label || zone.zone_type,
        descriptionText: (zone.properties?.description_text as string) || undefined,
        floors: floors != null ? Number(floors) : undefined,
        heightM: heightM != null ? Number(heightM) : undefined,
        ...archetypeInfo,
      },
    });
  }

  // -- Reassign colors for duplicate-colored building zones --
  // Group building entries by color to find duplicates that need distinct colors
  const buildingsByColor = new Map<string, { entry: ZonePromptEntry; zoneId: string }[]>();
  for (const item of rawEntries) {
    if (!BUILDING_TYPES.includes(item.entry.zoneType)) continue;
    const c = item.entry.color.toLowerCase();
    if (!buildingsByColor.has(c)) buildingsByColor.set(c, []);
    buildingsByColor.get(c)!.push(item);
  }

  // Track all colors currently in use to avoid collisions
  const usedColors = new Set(rawEntries.map(e => e.entry.color.toLowerCase()));

  for (const [, group] of buildingsByColor) {
    if (group.length <= 1) continue; // No conflict -- skip

    // First building keeps its original color; reassign the rest
    let variantIdx = 0;
    for (let gi = 1; gi < group.length; gi++) {
      const item = group[gi];
      // Find the next unused variant color
      while (variantIdx < BUILDING_VARIANT_PALETTE.length &&
             usedColors.has(BUILDING_VARIANT_PALETTE[variantIdx].toLowerCase())) {
        variantIdx++;
      }
      if (variantIdx < BUILDING_VARIANT_PALETTE.length) {
        const variantColor = BUILDING_VARIANT_PALETTE[variantIdx];
        item.entry.color = variantColor;
        _zoneColorOverrides.set(item.zoneId, variantColor);
        usedColors.add(variantColor.toLowerCase());
        variantIdx++;
        console.log(`[AIRender] Zone "${item.entry.zoneName}" (${item.zoneId}) color reassigned to ${variantColor} to avoid duplicate`);
      }
    }
  }

  // With unique shade IDs, each archetype-assigned zone has its own color,
  // so deduplication only applies to unassigned zones sharing a default color.
  // After variant reassignment, duplicates should be rare, but keep the guard.
  const seen = new Map<string, ZonePromptEntry>();
  for (const item of rawEntries) {
    const key = `${item.entry.color}_${item.entry.zoneType}`;
    if (!seen.has(key)) {
      seen.set(key, item.entry);
    } else if (item.entry.archetypeTitle && !seen.get(key)!.archetypeTitle) {
      seen.set(key, item.entry);
    }
  }

  // Sort: buildings/parks first, site_boundary LAST -- so the AI prioritizes
  // specific zone instructions over the generic infill instruction.
  const result = Array.from(seen.values());
  result.sort((a, b) => {
    if (a.zoneType === 'site_boundary') return 1;
    if (b.zoneType === 'site_boundary') return -1;
    return 0;
  });
  return result;
}

// colorName() is defined earlier in this file (see "Color utilities for variant-specific polygon colors")

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
    case 'street':
    case 'path':
      return 'complete urban streetscape with smooth asphalt road surface, crisp white lane markings, concrete curbs, wide sidewalks with tactile paving, regularly spaced street trees in tree grates, pedestrian-scale lighting, parked cars along the curb, and accessible crosswalks with painted markings';
    case 'green_space':
    case 'park':
      return 'landscaped urban park with mature canopy trees, manicured grass lawns, meandering walking paths with fine gravel or paved surface, wooden benches, ornamental flower beds, and subtle landscape lighting';
    case 'plaza':
      return 'public urban plaza with premium stone or brick paving in a geometric pattern, cafe seating areas with umbrellas, a central water feature or sculpture, accent planting in raised beds, and pedestrian-scale bollard lighting';
    case 'parking':
      return 'paved surface parking lot with painted parking stalls, directional arrows, concrete wheel stops, LED pole lighting, and perimeter landscaping with low hedges';
    case 'water':
      return 'water feature — pond, fountain, or reflecting pool with clean blue water and stone edges';
    case 'development_area':
      return 'mixed-use urban development with varied building heights, active ground floors, and public realm';
    default:
      return 'photorealistic urban development appropriate to the zone type';
  }
}

/**
 * Build the multi-zone prompt — narrative prose for Gemini.
 * Uses the same Subject + Environment + Materials + Lighting + Camera formula
 * as the two-pass pipeline, but describes all zones in a single prompt.
 */
function buildStructuredPrompt(options: AIRenderOptions): string {
  const zones = options.siteZones || [];
  const zoneEntries = collectZonePromptEntries(zones);
  const styleId = options.renderStyleId || options.style || 'photorealistic';
  const style = GEMINI_STYLE_MODIFIERS[styleId];

  const isArtistic = ['watercolour', 'ink-wash', 'charcoal', 'marker-render', 'isometric', 'woodblock', 'massing-study', 'site-plan'].includes(styleId);
  const isSitePlan = styleId === 'site-plan';

  const parts: string[] = [];

  // ── Opening narrative — Camera + Environment ──
  if (isSitePlan) {
    parts.push(
      'Orthographic top-down site plan of an urban development. Colored polygon overlays on this aerial image mark proposed zones.',
      'Render as a flat 2D view looking straight down — no 3D perspective, no cast shadows.',
    );
  } else if (isArtistic) {
    parts.push(
      `Aerial view of an urban development site. Colored polygon overlays mark proposed zones on this satellite photograph.`,
      `Transform each colored zone into its described content, rendered in ${style?.label || styleId} style.`,
    );
  } else {
    parts.push(
      'Aerial photograph captured by a DJI drone at approximately 60 meters altitude, looking down at an oblique angle over an urban development site.',
      'Colored polygon overlays mark proposed zones. Transform each colored area into photorealistic architecture and landscape that seamlessly replaces the overlay.',
    );
  }

  // ── Style ──
  if (style) {
    parts.push(style.prompt);
  }

  // ── Zone-by-zone narrative descriptions ──
  if (zoneEntries.length > 0) {
    const zoneNarratives: string[] = [];

    for (const entry of zoneEntries) {
      const color = colorName(entry.color);

      if (entry.zoneType === 'site_boundary') {
        zoneNarratives.push(
          `The ${color} background area is the site boundary. Fill it with realistic urban ground-plane context: ` +
          `public sidewalks matching surrounding pavement, manicured grass, small street trees, and pedestrian paths ` +
          `that seamlessly blend the new development with the surrounding satellite imagery.`
        );
        continue;
      }

      const desc = buildArchetypeDescription(entry, entry.zoneType);
      const userDesc = entry.descriptionText?.trim();
      const isBuilding = ['building', 'residential', 'commercial', 'industrial', 'mixed_use'].includes(entry.zoneType);

      if (isBuilding) {
        // Scale text from floors/height
        const scaleText = entry.floors ? `${entry.floors}-story`
          : entry.heightM ? `${entry.heightM}m tall`
          : 'multi-story';

        // Building narrative — emphasize 3D volume, SCALE, and foundation containment
        zoneNarratives.push(
          `The ${color} polygon is a building footprint. Render a ${scaleText} ${desc}.` +
          (userDesc ? ` ${userDesc}.` : '') +
          ` This is a large ${scaleText} structure that fills the entire ${color} footprint — not a small house or cabin.` +
          ` The ${color} area is the building's ground-level foundation only — render the full vertical 3D mass ` +
          `and roofline extending naturally into the sky above, respecting aerial perspective. ` +
          `Replace every ${color} pixel with building facade, structure, or ground-plane landscaping. ` +
          `Do not let building materials bleed horizontally into neighboring zones. ` +
          `CRITICAL: The building's walls, shadows, and all architectural elements must stay strictly within the horizontal boundaries of the ${color} polygon footprint. No part of the building may extend sideways beyond the polygon perimeter.`
        );
      } else {
        // Ground-level zone narrative — emphasize strict horizontal containment
        zoneNarratives.push(
          `The ${color} area is a ${desc}.` +
          (userDesc ? ` ${userDesc}.` : '') +
          ` Fill it precisely within its boundaries, treating edges as hard physical curbs. ` +
          `Replace every ${color} pixel completely — no colored overlay should remain visible.`
        );
      }
    }

    parts.push(zoneNarratives.join(' '));
  }

  // ── Containment + preservation instructions ──
  parts.push(
    'Maintain strict containment — each zone stays within its colored boundary. ' +
    'Do not include any people, pedestrians, human figures, or crowds anywhere in the scene. ' +
    'Keep all satellite imagery outside the site boundary exactly as it is, preserving the original style, lighting, and composition.'
  );

  // ── Lighting (photorealistic only) ──
  if (!isArtistic && !isSitePlan) {
    parts.push(
      'Warm afternoon sunlight from the southwest casts crisp architectural shadows. ' +
      'Match the existing satellite imagery perspective, color temperature, and lighting for a seamless photomontage.'
    );
  }

  // ── User custom prompt ──
  if (options.customPrompt?.trim()) {
    parts.push(options.customPrompt.trim());
  }

  return parts.join(' ');
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

  // 2. Building containment negatives + universal exclusions
  parts.push('building extending beyond footprint, architecture outside polygon, walls outside boundary, building bleed into neighboring zone, people, pedestrians, human figures, faces, crowds, cyclists, joggers');

  // 3. Zone bleeding negatives
  parts.push('zone bleeding into neighboring zone, landscape extending beyond polygon boundary, elements crossing polygon edges, mismatched zone content');

  // 4. Archetype-level negatives passed from the panel
  if (options.mapOverlayNegative?.trim()) {
    parts.push(options.mapOverlayNegative.trim());
  }
  if (options.archetypeNegative?.trim()) {
    parts.push(options.archetypeNegative.trim());
  }

  // 5. Zone-level archetype negatives from catalog
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
/**
 * Fetch an image URL and return base64 data (without data URI prefix).
 */
async function fetchArchetypeImageBase64(url: string): Promise<string | null> {
  try {
    const fullUrl = url.startsWith('http') ? url : window.location.origin + url;
    const resp = await fetch(fullUrl);
    if (!resp.ok) return null;
    const blob = await resp.blob();
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const dataUrl = reader.result as string;
        resolve(dataUrl.split(',')[1] || null);
      };
      reader.readAsDataURL(blob);
    });
  } catch {
    return null;
  }
}

/**
 * Look up the archetype card thumbnail for a zone.
 * Returns { image_base64, label } or null if not found.
 */
async function getZoneArchetypeCard(zone: SiteZone): Promise<{ image_base64: string; label: string } | null> {
  const info = getZoneArchetypeInfo(zone);
  const archetypeId = zone.properties?.archetype_id || zone.properties?.subcategory;
  if (!archetypeId) return null;

  // Look through all catalogs
  const allCatalogs: any[] = [
    ...((archetypeCatalog as any)?.archetypes || []),
    ...((openSpaceCatalogData as any)?.archetypes || []),
    ...((streetPathCatalogData as any)?.archetypes || []),
  ];

  const catalogEntry = allCatalogs.find((c: any) => c.id === archetypeId);
  if (!catalogEntry) return null;

  let thumbnailUrl: string | null = null;
  if (catalogEntry.variants) {
    const selectedIdx = Number(zone.properties?.selected_variant) || 0;
    const variant = catalogEntry.variants[selectedIdx] || catalogEntry.variants[0];
    thumbnailUrl = variant?.thumbnailUrl || null;
  }
  if (!thumbnailUrl) thumbnailUrl = catalogEntry.thumbnailUrl || null;
  if (!thumbnailUrl) return null;

  const b64 = await fetchArchetypeImageBase64(thumbnailUrl);
  if (!b64) return null;

  const label = info.archetypeTitle || zone.name || zone.zone_type;
  return { image_base64: b64, label };
}

async function callVertexAI(
  imageBase64: string,
  prompt: string,
  seed: number,
  aspectRatio = '4:3',
  maskBase64?: string,
  negativePrompt?: string,
  guidanceScale?: number,
  model?: string,
  archetypeImages?: Array<{ image_base64: string; label: string; zone_color?: string }>,
): Promise<{ imageDataUri: string; seed: number }> {
  console.log('[AIRender] Calling Vertex AI via backend — prompt length:', prompt.length, 'mask:', !!maskBase64, 'negative:', !!negativePrompt, 'guidance:', guidanceScale, 'model:', model || 'default', 'archetypeImages:', archetypeImages?.length || 0);

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
  if (model) {
    body.model = model;
  }
  if (archetypeImages && archetypeImages.length > 0) {
    body.archetype_images = archetypeImages;
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
  const mapRef = useRef<mapboxgl.Map | null>(null);

  const reset = useCallback(() => {
    // Restore zone layers that were hidden during render
    const map = mapRef.current;
    if (map) {
      const RESTORE_LAYERS = ['site-zones-fill', 'site-zones-boundary-fill', 'site-zones-extrusion', 'site-zones-outline', 'site-zones-selected'];
      for (const layerId of RESTORE_LAYERS) {
        if (map.getLayer(layerId)) {
          map.setLayoutProperty(layerId, 'visibility', 'visible');
        }
      }
    }
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
          options.model,
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
      mapRef.current = map;

      try {
        // Generate mask FIRST (synchronous) before the async screenshot capture,
        // so both read canvas dimensions at the same instant. A layout reflow
        // between calls can shift dimensions by ±1px, which Vertex AI rejects.
        const zones = options.siteZones;
        const maskBase64 = zones && zones.length > 0
          ? generateBinaryMask(map, zones)
          : undefined;

        const imageBase64 = await captureMapCanvasBase64(map);
        const headroomPx = getMaxBuildingHeadroom(map, zones);
        const bounds = getMapBounds(map, headroomPx);

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
        const headroomPx = getMaxBuildingHeadroom(map, options.siteZones);
        const bounds = getMapBounds(map, headroomPx);

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
        const headroomPx = getMaxBuildingHeadroom(map, zones);
        const bounds = getMapBounds(map, headroomPx);

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
          const headroomPx = getMaxBuildingHeadroom(map, zones);
          const bounds = getMapBounds(map, headroomPx);

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
          const faceHeadroomPx = getMaxBuildingHeadroom(map, options.siteZones);
          const bounds = getMapBounds(map, faceHeadroomPx);

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
      mapRef.current = map;

      try {
        const zones = options.siteZones || [];
        if (zones.length === 0) {
          return await render(map, options);
        }

        // Save original camera state
        const origCenter = map.getCenter();
        const origZoom = map.getZoom();
        const origBearing = map.getBearing();
        const origPitch = map.getPitch();

        // Hide ONLY the outline/stroke layers before capturing the base screenshot
        // so colored fills remain visible (Gemini uses them as spatial anchors)
        // but polygon borders don't bake into the composite base.
        const OUTLINE_LAYERS = ['site-zones-outline', 'site-zones-selected', 'site-zones-labels', 'massing-preview-extrusion'];
        for (const layerId of OUTLINE_LAYERS) {
          if (map.getLayer(layerId)) map.setLayoutProperty(layerId, 'visibility', 'none');
        }
        await new Promise<void>(resolve => {
          const t = setTimeout(resolve, 500);
          map.once('idle', () => { clearTimeout(t); resolve(); });
        });

        // Capture with fills visible but outlines hidden
        const originalBase64 = await captureMapCanvasBase64(map);

        // Restore outline layers before the full hide pass below
        for (const layerId of OUTLINE_LAYERS) {
          if (map.getLayer(layerId)) map.setLayoutProperty(layerId, 'visibility', 'visible');
        }

        const perZoneHeadroomPx = getMaxBuildingHeadroom(map, zones);
        const originalBounds = getMapBounds(map, perZoneHeadroomPx);
        const aspectRatio = computeAspectRatio(map);
        let cumulativeDataUri = `data:image/png;base64,${originalBase64}`;

        // Separate zones into ground-level (Pass 1) and buildings (Pass 2)
        const GROUND_TYPES = ['water', 'green_space', 'park', 'parking', 'road', 'street', 'path', 'plaza', 'development_area'];
        const BUILDING_TYPES = ['building', 'residential', 'commercial', 'industrial', 'mixed_use'];

        const renderableZones = zones
          .filter(z => z.zone_type !== 'site_boundary' && z.coordinates && z.coordinates.length >= 3);

        const groundZones = renderableZones.filter(z => GROUND_TYPES.includes(z.zone_type));
        const buildingZones = renderableZones.filter(z => BUILDING_TYPES.includes(z.zone_type));

        // Populate _zoneColorOverrides so duplicate-colored buildings get distinct
        // variant colors in both the map overlay and the prompt text.
        collectZonePromptEntries(zones);

        if (renderableZones.length === 0) {
          return await render(map, options);
        }

        const totalSteps = (groundZones.length > 0 ? 1 : 0) + buildingZones.length;
        let currentStep = 0;
        const successfulZones: string[] = [];

        // ── HIDE 3D extrusion layers and labels ──
        const LAYERS_TO_HIDE = [
          'site-zones-extrusion', 'site-zones-outline', 'site-zones-selected',
          'site-zones-labels', 'site-zones-fill', 'site-zones-boundary-fill',
          'massing-preview-extrusion', '3d-buildings',
        ];
        const layerVisibilityBackup: Record<string, string> = {};
        for (const layerId of LAYERS_TO_HIDE) {
          const layer = map.getLayer(layerId);
          if (layer) {
            const vis = map.getLayoutProperty(layerId, 'visibility');
            layerVisibilityBackup[layerId] = typeof vis === 'string' ? vis : 'visible';
            map.setLayoutProperty(layerId, 'visibility', 'none');
          }
        }
        // Wait for repaint
        await new Promise<void>(resolve => {
          const t = setTimeout(resolve, 2000);
          map.once('idle', () => { clearTimeout(t); resolve(); });
        });

        const src = map.getSource('site-zones') as mapboxgl.GeoJSONSource | undefined;
        const guidanceScale = options.guidanceScale ?? 15;
        const negativePrompt = buildNegativePrompt(options);

        // Helper: update map source and wait for idle
        const updateSourceAndWait = async (features: any[]) => {
          if (!src) return;
          src.setData({ type: 'FeatureCollection', features });
          await new Promise<void>(resolve => {
            const t = setTimeout(() => { resolve(); }, 2000);
            map.once('idle', () => { clearTimeout(t); resolve(); });
          });
        };

        // ════════════════════════════════════════════════════════
        // PASS 1: GROUND PLANE (parks, roads, plazas — all at once)
        // ════════════════════════════════════════════════════════
        if (groundZones.length > 0) {
          setStatusMessage(`Pass 1/${totalSteps > 1 ? '2' : '1'}: Rendering ground plane (${groundZones.length} zones)...`);
          setProgress(5);
          console.log(`[AIRender] ═══ PASS 1: GROUND PLANE ═══ (${groundZones.length} zones)`);

          try {
            // Show ALL ground zones colored + site boundary white. No buildings.
            const groundFeatures = zones
              .filter(z => z.coordinates && z.coordinates.length >= 3)
              .filter(z => z.zone_type === 'site_boundary' || GROUND_TYPES.includes(z.zone_type))
              .map(z => ({
                type: 'Feature' as const,
                properties: {
                  id: z.id,
                  color: z.zone_type === 'site_boundary' ? '#ffffff' : (z.color || '#4CAF50'),
                  label: z.name || z.zone_type,
                  zone_type: z.zone_type,
                },
                geometry: {
                  type: 'Polygon' as const,
                  coordinates: [z.coordinates!.map(([lng, lat]) => [lng, lat])],
                },
              }));

            await updateSourceAndWait(groundFeatures);
            const groundScreenshot = await captureMapCanvasBase64(map);

            // Build combined mask for ALL ground zones
            const groundMask = generateCombinedMask(map, groundZones);

            // Build narrative ground plane prompt
            const groundPrompt = buildGroundPlanePrompt(groundZones, options);

            console.log(`[AIRender] Pass 1 prompt (${groundPrompt.length} chars):\n${groundPrompt}`);

            const { imageDataUri: groundResult } = await callVertexAI(
              groundScreenshot,
              groundPrompt,
              options.seed ?? Math.floor(Math.random() * 2147483647),
              aspectRatio,
              groundMask,
              negativePrompt || undefined,
              guidanceScale,
              options.model,
            );

            // Composite ground zones onto the cumulative result with strict polygon clipping
            for (const gz of groundZones) {
              cumulativeDataUri = await compositeZoneRender(cumulativeDataUri, groundResult, map, gz);
              successfulZones.push(gz.name || gz.zone_type);
            }

            currentStep++;
            console.log(`[AIRender] Pass 1 complete — ground plane rendered`);
          } catch (groundErr) {
            console.warn('[AIRender] Pass 1 (ground plane) failed:', groundErr);
          }
        }

        // ════════════════════════════════════════════════════════
        // PASS 2: ARCHITECTURE (buildings, one at a time)
        // Each building renders onto the ground plane from Pass 1.
        // ════════════════════════════════════════════════════════
        for (let i = 0; i < buildingZones.length; i++) {
          const zone = buildingZones[i];
          const zoneName = zone.name || zone.zone_type;
          currentStep++;
          setStatusMessage(`Pass 2: Building ${i + 1}/${buildingZones.length}: ${zoneName}...`);
          setProgress(Math.round((currentStep / totalSteps) * 90) + 5);
          console.log(`[AIRender] ═══ PASS 2: BUILDING ${i + 1}/${buildingZones.length}: "${zoneName}" ═══`);

          try {
            // Show only this building's footprint colored + site boundary white
            // Use the cumulative result as the base (which now has the rendered ground plane)
            const buildingFeatures = zones
              .filter(z => z.coordinates && z.coordinates.length >= 3)
              .filter(z => z.id === zone.id || z.zone_type === 'site_boundary')
              .map(z => ({
                type: 'Feature' as const,
                properties: {
                  id: z.id,
                  color: z.id === zone.id ? getZoneRenderColor(z.id, z.color || '#E03C31') : '#ffffff',
                  label: z.name || z.zone_type,
                  zone_type: z.zone_type,
                  // NO height — flat polygon only
                },
                geometry: {
                  type: 'Polygon' as const,
                  coordinates: [z.coordinates!.map(([lng, lat]) => [lng, lat])],
                },
              }));

            await updateSourceAndWait(buildingFeatures);

            // For Pass 2, use the cumulative result (with rendered ground) as the base image
            // Paint the building footprint colored onto it + add white headroom
            let buildingScreenshot = await captureMapCanvasBase64(map);

            // Add white headroom above building polygon for 3D perspective
            const bldgHeight = zone.properties?.height_m ? Number(zone.properties.height_m)
              : zone.properties?.height ? Number(zone.properties.height) : 0;

            if (bldgHeight > 0) {
              const headroomPx = calculatePerspectiveHeadroom(map, bldgHeight);
              if (headroomPx > 5) {
                const dpr = window.devicePixelRatio || 1;
                const pixels = siteBoundaryToPixels(map, zone.coordinates!);
                const devicePixels = pixels.map(p => ({ x: p.x * dpr, y: p.y * dpr }));
                const minX = Math.min(...devicePixels.map(p => p.x));
                const maxX = Math.max(...devicePixels.map(p => p.x));
                const minY = Math.min(...devicePixels.map(p => p.y));
                const expandedTop = Math.max(0, minY - headroomPx);

                const img = await loadImage(`data:image/png;base64,${buildingScreenshot}`);
                const canvas = document.createElement('canvas');
                canvas.width = img.naturalWidth;
                canvas.height = img.naturalHeight;
                const ctx = canvas.getContext('2d')!;
                ctx.drawImage(img, 0, 0);
                ctx.fillStyle = '#ffffff';
                ctx.fillRect(minX, expandedTop, maxX - minX, minY - expandedTop);

                // Feathered top edge
                const featherH = Math.min(30 * dpr, headroomPx * 0.25);
                if (featherH > 2) {
                  const gradient = ctx.createLinearGradient(0, expandedTop, 0, expandedTop + featherH);
                  gradient.addColorStop(0, 'rgba(255,255,255,0)');
                  gradient.addColorStop(1, 'rgba(255,255,255,1)');
                  ctx.fillStyle = gradient;
                  ctx.fillRect(minX, expandedTop, maxX - minX, featherH);
                }

                buildingScreenshot = canvas.toDataURL('image/png').split(',')[1];
                console.log(`[AIRender] Added ${headroomPx.toFixed(0)}px headroom for ${bldgHeight}m building`);
              }
            }

            // Generate expanded mask for building
            const buildingMask = generateSingleZoneMask(map, zone);

            // Build narrative building prompt
            const buildingPrompt = buildBuildingPrompt(zone, options);

            console.log(`[AIRender] Pass 2 prompt (${buildingPrompt.length} chars):\n${buildingPrompt}`);

            // Fetch archetype card image for multi-image routing
            let buildingArchetypeImages: Array<{ image_base64: string; label: string; zone_color?: string }> | undefined;
            try {
              const card = await getZoneArchetypeCard(zone);
              if (card) {
                const zoneColor = colorName(getZoneRenderColor(zone.id, zone.color || '#E03C31'));
                buildingArchetypeImages = [{ ...card, zone_color: zoneColor }];
                console.log(`[AIRender] Pass 2: Sending archetype card "${card.label}" for multi-image routing`);
              }
            } catch (cardErr) {
              console.warn('[AIRender] Failed to fetch archetype card:', cardErr);
            }

            const { imageDataUri } = await callVertexAI(
              buildingScreenshot,
              buildingPrompt,
              options.seed ?? Math.floor(Math.random() * 2147483647),
              aspectRatio,
              buildingMask,
              negativePrompt || undefined,
              guidanceScale,
              options.model,
              buildingArchetypeImages,
            );

            // Composite with headroom-expanded clip
            const preCompositDataUri = cumulativeDataUri;
            cumulativeDataUri = await compositeZoneRender(cumulativeDataUri, imageDataUri, map, zone);

            // Post-composite cleanup: restore pixels inside other zones' polygons
            cumulativeDataUri = await cleanupZoneBleed(cumulativeDataUri, preCompositDataUri, map, zone, zones);
            successfulZones.push(zoneName);
            console.log(`[AIRender] Building "${zoneName}" rendered successfully`);
          } catch (bldgErr) {
            console.warn(`[AIRender] Building "${zoneName}" failed:`, bldgErr);
          }
        }

        // ── Restore non-visual layers, keep zone fills hidden while render is displayed ──
        const KEEP_HIDDEN_DURING_RENDER = ['site-zones-fill', 'site-zones-boundary-fill', 'site-zones-extrusion', 'site-zones-outline', 'site-zones-selected'];
        for (const [layerId, visibility] of Object.entries(layerVisibilityBackup)) {
          if (map.getLayer(layerId)) {
            if (KEEP_HIDDEN_DURING_RENDER.includes(layerId)) {
              // Keep hidden — the render overlay replaces these visually
              map.setLayoutProperty(layerId, 'visibility', 'none');
            } else {
              map.setLayoutProperty(layerId, 'visibility', visibility as 'none' | 'visible');
            }
          }
        }

        const restoreFeatures = zones.map(z => {
          if (!z.coordinates || z.coordinates.length < 3) return null;
          const zoneHeight = z.properties?.height_m != null
            ? Number(z.properties.height_m)
            : z.properties?.height != null
              ? Number(z.properties.height)
              : undefined;
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
        if (src) {
          src.setData({ type: 'FeatureCollection', features: restoreFeatures as any[] });
        }

        map.jumpTo({
          center: origCenter,
          zoom: origZoom,
          bearing: origBearing,
          pitch: origPitch,
        });

        if (successfulZones.length === 0) {
          throw new Error('All render passes failed');
        }

        const finalResult: AIRenderResult = {
          imageUrl: cumulativeDataUri,
          bounds: originalBounds,
          seed: options.seed,
          prompt: `Two-pass render: ${successfulZones.length} zones (${groundZones.length} ground + ${buildingZones.length} buildings)`,
        };

        setResult(finalResult);
        setProgress(100);
        setStatusMessage(`Complete — ${successfulZones.length} zones rendered (2-pass)`);
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
