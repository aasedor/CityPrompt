/**
 * useAIRender â€” React hook for the Vertex AI Imagen 3 render pipeline.
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
import { resolveApiFileUrl } from '@/services/api';
import { getCustomZoneStyle } from './customZoneStyle';
import { prepareZonesForRender } from './resolvePlanZoneArchetypes';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface AIRenderStyle {
  id: string;
  label: string;
  prompt: string;
  /** Optional negative prompt fragments */
  negative?: string;
  /** img2img strength override for this style (0â€“1). Higher = more transformation. */
  strength?: number;
}

export interface AIRenderOptions {
  /** Style preset id â€” maps to a prompt template */
  style?: string;
  /** Free-form prompt appended after the style prompt */
  customPrompt?: string;
  /** 0â€“1 â€” how closely the AI follows the source image (strength) */
  controlStrength?: number;
  /** Number of denoising steps (20â€“35 recommended) */
  steps?: number;
  /** Guidance scale */
  guidanceScale?: number;
  /** Optional reference image URL or data-URI for style transfer */
  referenceImageUrl?: string;
  /** Reference strength (0â€“1) */
  referenceStrength?: number;
  /** Archetype positive prompt â€” appended to the style prompt */
  archetypePrompt?: string;
  /** Archetype negative prompt â€” appended to the negative prompt */
  archetypeNegative?: string;
  /** Reference image URLs from archetype selections */
  referenceImageUrls?: string[];
  /** Explicit seed for reproducibility */
  seed?: number;
  /** Override output image dimensions */
  imageSize?: { width: number; height: number } | string;
  /** Render style id â€” alias for style, used by expanded catalog */
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
   * All site zones â€” used for structured zone-by-zone prompt generation.
   */
  siteZones?: SiteZone[];
  /** Gemini model ID override (e.g. 'gemini-3-pro-image-preview') */
  model?: string;
  /** Project ID for render audit log linking */
  projectId?: string;
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
  /** 4-face render results â€” one per bearing */
  faceRenders: FaceRender[];
  /** Whether a render is currently in flight */
  isRendering: boolean;
  /** 0â€“100 progress estimate (indeterminate: stays at -1 while waiting) */
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
// Style presets (kept for UI compatibility â€” the structured prompt overrides)
// ---------------------------------------------------------------------------

export const AI_RENDER_STYLES: AIRenderStyle[] = [
  // â”€â”€ Realistic â€” photo-style final-stage visualization â”€â”€
  {
    id: 'photorealistic',
    label: 'Photo Realistic',
    strength: 0.65,
    prompt:
      'Hyper-realistic exterior architectural rendering with cinematic lighting. Golden hour sunlight casting realistic shadows. Highly detailed materials including reflective glass facades, textured concrete, natural stone, and weathered brick with visible grain. Lush realistic landscaping with mature trees showing individual leaf clusters. Sharp focus, 8k resolution, ray-traced lighting, professional architectural photography, high dynamic range, neutral 5500K white balance.',
    negative: 'cartoon, illustration, sketch, painting, artistic, stylized, watercolor, pencil, monochrome, low quality, blurry, text, watermark, people, pedestrians, human figures',
  },
  {
    id: 'photomontage',
    label: 'Photomontage',
    strength: 0.65,
    prompt:
      'Professional architectural photomontage indistinguishable from a real drone photograph. Shot on a DJI Mavic 3 Enterprise at 60 meters altitude, angled downward at approximately 40 degrees, captured with a Hasselblad 4/3 CMOS sensor and 24mm equivalent lens at f/5.6, ISO 100. The proposed development appears as if fully constructed and occupied within the existing site context. Lighting, shadow direction, and color temperature precisely match the surrounding real environment. Subtle atmospheric haze increases with distance from the camera, reducing contrast and shifting distant elements toward blue-grey. Building materials show realistic weathering appropriate to a structure 1-2 years post-completion -- faint water staining below window sills, minor dust accumulation on ledges, natural patina on metal surfaces. Rooftop mechanical equipment, safety railings, and drainage infrastructure visible. Surrounding context includes real parked vehicles, existing tree canopy, neighboring rooftops with typical rooftop clutter. Natural lens vignetting at frame edges, slight chromatic aberration on high-contrast edges. No pristine CG perfection -- this must read as documentary aerial photography of an existing place.',
    negative: 'cartoon, illustration, sketch, painting, artistic, stylized, CGI look, perfect pristine surfaces, floating buildings, perspective distortion, unrealistic shadows, low quality, blurry, text, watermark',
  },
  {
    id: 'atmospheric',
    label: 'Atmospheric',
    strength: 0.65,
    prompt:
      'Cinematic aerial architectural photograph with dramatic atmospheric conditions. Shot from 80 meters altitude at an oblique angle during the final minutes of golden hour. CRITICAL: Every building must have photorealistic architectural materials â€” real brick, stone, concrete, glass, metal cladding, and proper roofing materials. Completely replace ALL colored polygon overlay fills (green, blue, purple, red, orange, yellow) with appropriate real building materials. No building should have a flat colored roof or facade â€” every surface must show realistic architectural textures and materials. Low-angle warm sunlight rakes across rooftops and facade surfaces, casting extremely long shadows. The sky dominates the upper third â€” towering cumulus clouds lit amber and rose, transitioning to deep blue-grey overhead. Subtle ground-level haze creates atmospheric depth layers. Wet surfaces from recent rainfall create mirror-like reflections on rooftops, roads, and plaza surfaces. Interior lights glowing warm amber through windows. Lush vegetation with individual leaf detail. Photographed on medium format digital with exceptional dynamic range.',
    negative: 'flat lighting, generic blue sky, midday sun, sterile, clinical, uniform exposure, low quality, blurry, text, watermark, people, pedestrians, colored polygon fills, flat colored roofs, green roofs on non-eco buildings, blue facades, purple walls, orange surfaces',
  },
  {
    id: 'winter',
    label: 'Winter',
    strength: 0.75,
    prompt:
      'Photorealistic winter scene aerial architectural visualization. Snow-covered roofs with realistic drift patterns and accumulation on all horizontal surfaces â€” ledges, parapets, window sills. Bare deciduous trees with visible branch architecture and no foliage. Evergreen conifers with heavy snow-load clumps on branches. Frosted ground plane showing plowed vs. unplowed contrast â€” plowed paths with salt-grit residue and thin slush, undisturbed areas with soft powder drifts. Soft diffuse winter daylight from a pale blue-grey overcast sky. Low sun angle casting long blue-tinted shadows. Increased specular reflectivity on all horizontal surfaces by 20% to simulate melt and ice sheen. Warm incandescent glow visible through windows. Frost on exposed metal and glass surfaces.',
    negative: 'lush green vegetation, summer foliage, bright green lawns, tropical plants, vibrant green trees, warm golden sunlight, low quality, blurry',
  },
  // â”€â”€ Concept â€” hand-drawn / painterly early-stage exploration â”€â”€
  {
    id: 'watercolour',
    label: 'Water Colour',
    strength: 0.65,
    prompt:
      'Beautiful watercolor architectural painting on highly textured watercolor paper. Soft bleeding edges where colors mix organically, translucent layered color washes with white paper glowing through as highlights. Bright airy and inviting atmosphere. Loose and artistic representation with pigment granulation and sedimentation in shadow areas. Faint underlying pencil construction lines visible beneath washes. Wet-on-wet bloom effects and cauliflower edges. Muted earth-tone palette with sage green, ochre, and ultramarine accents. Hand-painted competition entry by a master watercolourist.',
    negative: 'photorealistic, photograph, digital, sharp edges, perfect lines, 3D render, high contrast, neon colors, acrylic, oil paint, low quality, blurry',
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
    id: 'pen-and-ink',
    label: 'Pen & Ink',
    strength: 0.65,
    prompt:
      'Architectural pen-and-ink line drawing on cream-toned drawing paper. Strict ink-only linework with zero colour and zero tonal smudging â€” every mark is a discrete line drawn by a technical pen. Crisp construction lines defining building footprints, roof planes, openings, and material transitions. Cross-hatching and parallel-line hatching for shadow areas, denser hatching for deeper shadows. Visible line-weight variation from delicate hairlines for distant elements to confident heavier strokes for foreground edges. Stippling for soft transitions like foliage, gravel, or weathered surfaces. Trees as outlined forms with minimal shadow hatching. Background dissolves into lighter, sparser linework. Cream paper showing through as the only highlight. Hand-drafted mid-20th-century architectural illustration / contemporary urban-sketcher tradition.',
    negative: 'photorealistic, photograph, color, paint, watercolor wash, charcoal smudge, tonal blending, gradients, shading without lines, 3D render, perspective distortion, low quality, blurry, text, watermark',
  },
  // â”€â”€ Plan â€” top-down orthographic / drafted planning views â”€â”€
  {
    id: 'site-plan',
    label: 'Site Plan',
    strength: 0.65,
    prompt:
      'Top-down 2D architectural site plan in strict orthographic projection looking straight down. Clean architectural linework with soft flat pastel colors. Stylized trees depicted as simple overlapping green circles viewed from above. Paved pathways in light grey, defined property lines, crisp shadows indicating building height. Roads as clean strips, landscaping in matte green, water features in blue. Professional urban planning drawing quality.',
    negative: 'perspective, 3D, oblique angle, horizon visible, photorealistic facades, eye-level, detailed buildings, low quality, blurry, noisy, text, watermark',
  },
  {
    id: 'site-plan-photo',
    label: 'Site Plan Photo',
    strength: 0.65,
    prompt:
      'Professional near-top-down architectural photomontage shot from a DJI Mavic 3 Enterprise drone at 100 meters altitude, looking almost straight down at approximately 15-20 degrees from nadir. Hasselblad 4/3 CMOS sensor, 24mm equivalent lens at f/5.6, ISO 100. The proposed development appears as if fully constructed and occupied, photographed from directly above in a real drone survey. All buildings, parks, streets, and landscaping are photorealistic with accurate materials, shadows, and proportions as seen from near-overhead. Building rooftops show realistic roofing materials, mechanical equipment, and drainage. Shadows are short and fall consistently in one direction indicating building height. Surrounding context preserves the real satellite imagery seamlessly. Materials show realistic weathering 1-2 years post-completion. Natural lens vignetting at frame edges. This must read as a real drone survey photograph of a completed development, not a diagram or illustration. CRITICAL: The colored polygon overlay zones (green, red, blue, orange, yellow fills) visible in the reference image are ONLY spatial markers showing where each element should be placed. You MUST completely replace every colored fill with photorealistic materials â€” real rooftop surfaces, real grass textures, real pavement, real building materials. No flat colored fills should remain visible in the output.',
    negative: 'cartoon, illustration, sketch, painting, artistic, stylized, CGI look, diagram, linework, pastel colors, perfect pristine surfaces, floating buildings, unrealistic shadows, low quality, blurry, text, watermark, flat colored polygon fills, green overlay, red overlay, blue overlay, colored zone fills',
  },
  {
    id: 'blueprint',
    label: 'Blueprint',
    strength: 0.65,
    prompt:
      'Architectural blueprint cyanotype rendering on aged blueprint paper. Strict orthographic projection looking straight down at the site. Pure white architectural linework on a deep Prussian-blue ground â€” crisp construction lines defining building footprints, roads, property lines, and landscape elements. Hatched line patterns indicate grass, pavement, and parking areas. Trees as small white circular symbols with crosshair centers. Roads as parallel white lines. Building footprints shown with thin white outlines and subtle internal cross-hatching. Faint vintage paper texture with slight mottling and edge fade. No tonal shading, no gradients, no realistic materials â€” pure 2D architectural drawing convention. Drafted-by-hand quality reminiscent of mid-20th-century architectural drawings.',
    negative: 'photorealistic, photograph, color other than blue and white, gradients, shading, 3D, perspective, oblique angle, eye-level, painterly, watercolor, sketch, pencil grey tones, realistic materials, low quality, blurry, text, watermark, people, vehicles',
  },
  {
    id: 'site-plan-watercolor',
    label: 'Site Plan WC',
    strength: 0.65,
    prompt:
      'Near-top-down architectural site plan rendered as a beautiful hand-painted watercolor illustration on heavy textured watercolor paper, viewed from approximately 15-20 degrees above nadir. The layout shows the proposed development from almost directly overhead, maintaining accurate spatial relationships and building footprints. Soft translucent watercolor washes define each zone â€” warm ochre and sienna for buildings, sage green washes for parks and landscaping, soft grey for roads and paving, ultramarine blue for water features. Building rooftops shown as watercolor-washed forms with faint pencil construction lines visible beneath. Trees depicted as loose circular watercolor daubs in varied greens with wet-on-wet bloom effects. Shadows painted as soft blue-grey washes indicating building height. White watercolor paper glowing through as highlights. Pigment granulation and sedimentation in shadow areas. Bleeding edges where colors mix organically at zone boundaries, creating natural soft transitions. Surrounding context rendered in lighter, more transparent washes fading to white at the edges. Hand-painted architectural competition entry quality.',
    negative: 'photorealistic, photograph, digital, 3D render, sharp edges, perfect lines, perspective, eye-level view, neon colors, flat colored polygon fills, green overlay, red overlay, blue overlay, colored zone fills, low quality, blurry',
  },
  // â”€â”€ Stylized â€” bold, graphic, distinctive â”€â”€
  {
    id: 'isometric',
    label: 'Isometric',
    strength: 0.65,
    prompt:
      'Isometric 3D architectural diagram with clean parallel projection and zero perspective distortion. Perfect 30-degree axonometric geometry. Rendered in smooth matte pastel colors with crisp hard edges and thin precise black outlines on every surface edge. No gradients, no shading, no cast shadows. Clear spatial layout with simplified geometric building forms. Vector-art aesthetic, highly detailed and precise. Contemporary tech-company infographic style, editorial design quality.',
    negative: 'photorealistic, photograph, perspective, vanishing point, gradients, shading, realistic shadows, texture, painterly, sketch, rough, low quality, blurry',
  },
  {
    id: 'clay-maquette',
    label: 'Clay Maquette',
    strength: 0.65,
    prompt:
      'Photorealistic macro photography of a physical architectural scale model carved entirely from a single block of pure white matte plaster or foam board. CRITICAL: EVERY element in the entire scene â€” every building, every tree, every road, every park, every fence, every vehicle â€” is made of the SAME pure white matte material with ZERO color variation. No colored surfaces whatsoever. No green for parks, no gray for roads, no brown for brick â€” everything is identical pure white plaster. The ONLY visual differentiation comes from form, shadow, and depth. Studio lighting with a single soft overhead softbox creating deep ambient occlusion shadows in cool gray tones that define every edge, setback, roof pitch, and topographic contour. High-angle isometric aerial view. Shallow depth of field with tilt-shift miniature effect. The model sits on a white base board. This is a monochromatic white architectural maquette â€” a physical object photographed in a studio.',
    negative: 'ANY color whatsoever, green parks, gray roads, brown brick, blue water, red buildings, orange surfaces, purple walls, colored roofs, realistic materials, photorealistic buildings, realistic vegetation, people, cars, outdoor lighting, sky background, clouds, digital rendering',
  },
  {
    id: 'woodblock',
    label: 'Wood Block',
    strength: 0.65,
    prompt:
      'Stylized woodblock print of an urban architectural scene. Bold thick black outlines defining all forms, flat and limited vintage color palette of 4-6 colors with crisp clean separation. Visible wood grain texture heavily integrated into the image. Zero gradation or blending within color areas. Graphic retro and stylized architectural illustration with strong balanced composition. Decorative patterned elements, depth through layered overlapping color planes. Museum-quality fine art print.',
    negative: 'photorealistic, photograph, digital, 3D render, gradients, shading, blending, watercolor bleeding, cartoon, smooth, modern, low quality, blurry',
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
  photomontage: {
    id: 'photomontage',
    label: 'Photomontage',
    prompt: 'Professional architectural photomontage indistinguishable from a real drone photograph. DJI Mavic 3 at 60m altitude, Hasselblad sensor, 24mm lens f/5.6. Proposed development appears fully constructed within existing site context. Lighting and shadows match surroundings. Atmospheric haze increasing with distance. Realistic material weathering 1-2 years post-completion. Natural lens vignetting and chromatic aberration. Documentary aerial photography of an existing place.',
  },
  atmospheric: {
    id: 'atmospheric',
    label: 'Atmospheric',
    prompt: 'Cinematic aerial architectural photograph with dramatic atmospheric conditions. CRITICAL: Replace all colored polygon fills with photorealistic building materials â€” real brick, stone, glass, concrete, metal roofing. No flat colored surfaces. Final minutes of golden hour, low-angle warm sunlight casting extremely long shadows. Towering cumulus clouds lit amber and rose overhead. Ground-level haze creating depth layers. Wet surfaces with mirror-like reflections. Interior lights glowing warm amber through windows. Medium format digital with exceptional dynamic range.',
  },
  'site-plan': {
    id: 'site-plan',
    label: 'Site Plan',
    prompt: 'Top-down 2D architectural site plan in strict orthographic projection. Clean architectural linework with soft flat pastel colors. Stylized trees as simple green circles from above. Professional urban planning drawing quality.',
  },
  'site-plan-photo': {
    id: 'site-plan-photo',
    label: 'Site Plan Photo',
    prompt: 'Professional near-top-down drone photomontage at 100m altitude, 15-20 degrees from nadir. DJI Mavic 3, Hasselblad sensor, 24mm lens f/5.6. Photorealistic materials, accurate short shadows, real rooftop equipment visible. Seamless integration with surrounding satellite context. Documentary drone survey photography of a completed development. CRITICAL: Replace all colored polygon fills completely with photorealistic materials. No flat green, red, blue, or orange overlay colors should remain visible.',
  },
  'site-plan-watercolor': {
    id: 'site-plan-watercolor',
    label: 'Site Plan WC',
    prompt: 'Near-top-down architectural site plan as a hand-painted watercolor on textured paper, 15-20 degrees from nadir. Soft translucent washes â€” warm ochre for buildings, sage green for parks, soft grey for roads, ultramarine for water. Faint pencil construction lines beneath washes. Trees as loose circular watercolor daubs. Shadows as soft blue-grey washes. White paper glowing through as highlights. Pigment granulation, wet-on-wet blooms, bleeding edges at zone boundaries. Architectural competition entry quality.',
  },
  winter: {
    id: 'winter',
    label: 'Winter',
    prompt: 'Photorealistic winter scene. Snow-covered roofs with drift patterns. Bare deciduous trees, snow-laden evergreens. Frosted surfaces, salt-grit on plowed paths. Soft diffuse winter light, pale blue-grey sky, long blue-tinted shadows. Specular melt/ice sheen on horizontal surfaces. Warm window glow.',
  },
  charcoal: {
    id: 'charcoal',
    label: 'Charcoal',
    prompt: 'Dramatic charcoal sketch on rough textured paper with deep black smudged shadows. High contrast black and white, full tonal range. Soft blended areas for atmosphere, sharp charcoal edge lines for architectural definition. Gallery-quality architectural drawing.',
  },
  'pen-and-ink': {
    id: 'pen-and-ink',
    label: 'Pen & Ink',
    prompt: 'Architectural pen-and-ink line drawing on cream paper. Pure ink-only linework with zero colour and zero tonal smudging. Crisp construction lines, cross-hatching for shadow, line-weight variation for depth. Stippling for foliage and weathered surfaces. Hand-drafted urban-sketcher tradition. Cream paper as the only highlight.',
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
  'clay-maquette': {
    id: 'clay-maquette',
    label: 'Clay Maquette',
    prompt: 'Photorealistic macro photography of a physical architectural scale model carved from a single block of PURE WHITE matte plaster. CRITICAL: Every single element â€” buildings, trees, roads, parks, vehicles â€” is the SAME pure white material with ZERO color. No green, no gray, no brown, no color of any kind. Only white plaster with shadows defining form. Studio lighting with soft overhead softbox and deep ambient occlusion shadows. High-angle isometric view with tilt-shift miniature effect. Monochromatic white architectural maquette on white base board.',
  },
  blueprint: {
    id: 'blueprint',
    label: 'Blueprint',
    prompt: 'Architectural blueprint cyanotype on aged blueprint paper. Strict orthographic projection straight down. Pure white linework on deep Prussian-blue ground â€” crisp construction lines, building footprints, property lines, hatched landscape patterns. Trees as small white circular symbols. Faint vintage paper mottling. No tonal shading, no gradients, no realistic materials. Mid-20th-century architectural drafting convention.',
  },
};

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** Backend render endpoint */
const API_BASE = import.meta.env.VITE_API_URL || '';
const RENDER_API_URL = `${API_BASE}/api/v1/render/generate`;

/** Timeout for the backend request (3 minutes â€” Imagen 3 can be slow) */
const RENDER_TIMEOUT = 300_000;

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
        // Strip the "data:image/png;base64," prefix â€” backend wants raw base64
        const base64 = dataUri.split(',')[1];
        resolve(base64);
      };
      reader.onerror = () => reject(new Error('Failed to read canvas blob'));
      reader.readAsDataURL(blob);
    }, 'image/png');
  });
}

/**
 * Apply a winter color grade to a satellite base64 image.
 * Desaturates greens (vegetation â†’ muted brown/grey), adds cool blue cast,
 * slight brightness boost, and global desaturation for winter atmosphere.
 * This helps Gemini see winter-toned context and blend rendered zones naturally.
 */
async function applyWinterColorGrade(base64: string): Promise<string> {
  const t0 = performance.now();
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      canvas.width = img.width;
      canvas.height = img.height;
      const ctx = canvas.getContext('2d')!;
      ctx.drawImage(img, 0, 0);

      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const px = imageData.data;

      for (let i = 0; i < px.length; i += 4) {
        let r = px[i];
        let g = px[i + 1];
        let b = px[i + 2];

        // 1. Detect vegetation: green-dominant pixels â†’ shift to muted winter brown/grey
        if (g > r + 15 && g > b + 15 && g > 80) {
          r = r * 0.85 + g * 0.15 + 20;
          g = g * 0.55 + r * 0.1;
          b = b * 0.7 + 15;
        }

        // 2. Global desaturation (20% toward luminance) for muted winter palette
        const lum = 0.299 * r + 0.587 * g + 0.114 * b;
        r = r * 0.8 + lum * 0.2;
        g = g * 0.8 + lum * 0.2;
        b = b * 0.8 + lum * 0.2;

        // 3. Cool blue shift
        r = r - 3;
        b = b + 8;

        // 4. Slight brightness boost for snow/frost reflectance
        px[i] = Math.min(255, Math.max(0, r + 10));
        px[i + 1] = Math.min(255, Math.max(0, g + 10));
        px[i + 2] = Math.min(255, Math.max(0, b + 12));
      }

      ctx.putImageData(imageData, 0, 0);
      const dataUri = canvas.toDataURL('image/png');
      const result = dataUri.split(',')[1];
      console.log(`[AIRender] Winter color grade applied in ${(performance.now() - t0).toFixed(0)}ms (${canvas.width}x${canvas.height})`);
      resolve(result);
    };
    img.onerror = () => reject(new Error('Failed to load image for winter color grade'));
    img.src = `data:image/png;base64,${base64}`;
  });
}

/**
 * Invert a binary mask (whiteâ†”black). Used to create a mask that targets
 * the context area (outside zones) for the winter second-pass enhancement.
 */
async function invertMask(maskBase64: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      const ctx = canvas.getContext('2d')!;
      ctx.drawImage(img, 0, 0);
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const px = imageData.data;
      for (let i = 0; i < px.length; i += 4) {
        px[i] = 255 - px[i];
        px[i + 1] = 255 - px[i + 1];
        px[i + 2] = 255 - px[i + 2];
      }
      ctx.putImageData(imageData, 0, 0);
      resolve(canvas.toDataURL('image/png').split(',')[1]);
    };
    img.onerror = () => reject(new Error('Failed to load mask for inversion'));
    img.src = `data:image/png;base64,${maskBase64}`;
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

  console.log(`[AIRender] Canvas ${w}x${h} (ratio ${ratio.toFixed(3)}) â†’ aspect ratio: ${best.label}`);
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
  const activeBoundary = getActiveSiteBoundary(siteZones);
  const boundaries = activeBoundary ? [activeBoundary] : [];
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
    console.log(`[AIRender] Mask: drew zone "${zone.name || zone.id}" (${zone.zone_type}) â€” ${pixels.length} vertices`);
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
 *  1) Polygon clip to site boundary â€” controls horizontal extent
 *  2) Pixel-diff ABOVE building zones â€” captures 3D vertical extent
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

  // â”€â”€ Step 1: Mask-based composite of AI result â”€â”€
  // Build a mask that includes the site boundary polygon AND extends upward
  // to the top of the canvas above each building zone (the "massive box"
  // approach). This ensures 3D buildings are never clipped at the ground-level
  // boundary, regardless of camera angle.
  const canvas = document.createElement('canvas');
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext('2d')!;

  ctx.drawImage(originalImg, 0, 0, w, h);

  const activeBoundary = getActiveSiteBoundary(siteZones);
  const boundaries = activeBoundary ? [activeBoundary] : [];
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

  // â”€â”€ Step 2: Pixel-diff ABOVE each building zone â”€â”€
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
  // at pitch=60Â° (oblique) shift is large.
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
      console.log(`[AIRender] Building mask headroom: ${headroom.toFixed(0)}px for ${buildingHeight}m height, pitch=${map.getPitch().toFixed(1)}Â°`);

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
 * Simple, natural language â€” Gemini handles spatial reasoning natively.
 */

// â”€â”€ Color utilities for variant-specific polygon colors â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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
 * Renders parks, roads, plazas â€” no vertical structures.
 */
function buildGroundPlanePrompt(groundZones: SiteZone[], options: AIRenderOptions): string {
  const entries: ZonePromptEntry[] = groundZones.map(z => {
    const info = getZoneArchetypeInfo(z);
    const color = colorName(z.color || '#4CAF50');
    return {
      color,
      zoneType: z.zone_type,
      zoneName: z.name || z.zone_type,
      descriptionText: (z.properties?.description_text as string) || undefined,
      customPromptText: getCustomZoneStyle(z)?.promptText,
      floors: undefined,
      heightM: undefined,
      archetypeTitle: info.archetypeTitle,
      facadeDescription: info.facadeDescription,
      roofDescription: info.roofDescription,
      materials: info.materials,
      massing: info.massing,
      heightTendency: info.heightTendency,
      publicRealm: info.publicRealm,
      colorScheme: info.colorScheme,
      aerialAppearance: info.aerialAppearance,
    };
  });
  return buildSCHEMAPrompt(entries, options, 'ground');
}

/**
 * Build a BUILDING prompt for Pass 2 of the two-pass pipeline.
 * Renders a single building onto the already-rendered ground plane.
 * Uses narrative prose following the formula: Subject + Environment + Materials + Lighting + Camera.
 */
function buildBuildingPrompt(zone: SiteZone, options: AIRenderOptions): string {
  const archetypeInfo = getZoneArchetypeInfo(zone);
  const zoneColor = colorName(getZoneRenderColor(zone.id, zone.color || '#E03C31'));
  const floors = zone.properties?.floors ?? zone.properties?.num_floors;
  const heightM = zone.properties?.height_m ?? zone.properties?.height;

  const entry: ZonePromptEntry = {
    color: zoneColor,
    zoneType: zone.zone_type,
    zoneName: zone.name || zone.zone_type,
    descriptionText: (zone.properties?.description_text as string) || undefined,
    customPromptText: getCustomZoneStyle(zone)?.promptText,
    floors: typeof floors === 'number' ? floors : undefined,
    heightM: typeof heightM === 'number' ? heightM : undefined,
    archetypeTitle: archetypeInfo.archetypeTitle,
    facadeDescription: archetypeInfo.facadeDescription,
    roofDescription: archetypeInfo.roofDescription,
    materials: archetypeInfo.materials,
    massing: archetypeInfo.massing,
    heightTendency: archetypeInfo.heightTendency,
    publicRealm: archetypeInfo.publicRealm,
    colorScheme: archetypeInfo.colorScheme,
    aerialAppearance: archetypeInfo.aerialAppearance,
  };
  return buildSCHEMAPrompt([entry], options, 'building');
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
void _buildSingleZonePrompt; // suppress unused warning â€” kept for fallback use

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
void buildArchetypeDescription; // suppress unused warning â€” kept for fallback use

/** Extract N keywords from verbose description text, joining with '+' */
function condenseToKeywords(text: string | undefined, maxTokens = 4): string {
  if (!text) return '';
  // Split on sentence/clause boundaries
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

/**
 * Check if a zone is a "priority" type that needs a richer description (~150 chars)
 * to prevent hallucination. Large/unique building types get more detail.
 */
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
 *  Standard zones: ~80 chars. Priority zones: ~150 chars for richer detail.
 *  Custom-style zones: the user's prompt passes through intact (never condensed),
 *  truncated to customCharBudget. */
function buildCompressedZoneLabel(entry: ZonePromptEntry, imageIndex?: number, customCharBudget = 250): string {
  const BUILDING_TYPES = ['building', 'residential', 'commercial', 'industrial', 'mixed_use'];
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

  // Custom-style zone: the user's own description IS the spec â€” keep it intact.
  // Prefer the zone's own name; a retained (but overridden) archetype title
  // would contradict the custom description.
  if (entry.customPromptText) {
    const customName = entry.zoneName || name;
    let text = entry.customPromptText.replace(/\s+/g, ' ').trim();
    if (text.length > customCharBudget) text = text.slice(0, customCharBudget - 3) + '...';
    const imgRef = imageIndex != null ? ` | match style of Image ${imageIndex}` : '';
    return `[${entry.color}] ${customName} | ${scale} | CUSTOM: ${text}${imgRef}`;
  }

  // If we have an archetype image reference, use that instead of materials
  if (imageIndex != null) {
    return `[${entry.color}] ${name} | ${scale} | match style of Image ${imageIndex}`;
  }

  // Materials/features â€” priority zones get more keywords for richer detail
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
    // Streets: use corridor description or public realm
    const roadDesc = entry.publicRealm || entry.materials || entry.descriptionText;
    features = condenseToKeywords(roadDesc, maxKeywords);
    // Add surface type if available
    if (entry.materials && !features.includes(condenseToKeywords(entry.materials, 1))) {
      features += '+' + condenseToKeywords(entry.materials, 1);
    }
  } else if (isPark) {
    // Parks/plazas: use public realm, landscape features
    const parkDesc = entry.publicRealm || entry.materials || entry.descriptionText;
    features = condenseToKeywords(parkDesc, maxKeywords);
  } else {
    features = condenseToKeywords(entry.descriptionText || entry.materials || entry.publicRealm, maxKeywords);
  }

  // User description override takes priority if present and non-empty
  if (entry.descriptionText?.trim() && entry.descriptionText.trim().length > 10) {
    // Append user description to features rather than replacing
    const userKeywords = condenseToKeywords(entry.descriptionText, 3);
    if (userKeywords && !features.includes(userKeywords)) {
      features = features ? `${features}, ${userKeywords}` : userKeywords;
    }
  }

  if (!features) features = entry.zoneType.replace(/_/g, ' ');

  // Priority zones: allow up to 160 chars. Standard: 100 chars.
  const maxLen = priority ? 160 : 100;
  const label = `[${entry.color}] ${name} | ${scale} | ${features}`;
  return label.length > maxLen ? label.slice(0, maxLen - 3) + '...' : label;
}

/**
 * Build a SCHEMA AVANZATO format prompt â€” structured labels instead of paragraphs.
 * Targets 2,200-2,500 chars for optimal Gemini 3 Pro attention.
 */
function buildSCHEMAPrompt(
  zoneEntries: ZonePromptEntry[],
  options: AIRenderOptions,
  mode: 'structured' | 'ground' | 'building',
  imageIndices?: Map<string, number>,
): string {
  const styleId = options.renderStyleId || options.style || 'photorealistic';
  const style = GEMINI_STYLE_MODIFIERS[styleId];
  const isArtistic = ['watercolour', 'charcoal', 'isometric', 'woodblock', 'site-plan', 'site-plan-watercolor', 'clay-maquette', 'blueprint', 'pen-and-ink'].includes(styleId);
  const isSitePlan = styleId === 'site-plan' || styleId === 'site-plan-watercolor' || styleId === 'site-plan-photo';
  const isClay = styleId === 'clay-maquette';

  const lines: string[] = [];

  // â”€â”€ STYLE â”€â”€
  // Truncate style prompt to first sentence or 200 chars
  if (style) {
    let styleText = style.prompt;
    const firstSentence = styleText.indexOf('. ');
    if (firstSentence > 0 && firstSentence < 200) {
      styleText = styleText.slice(0, firstSentence + 1);
    } else if (styleText.length > 200) {
      styleText = styleText.slice(0, 197) + '...';
    }
    lines.push(`STYLE: ${styleText}`);
  }

  // â”€â”€ COMPOSITION â”€â”€
  if (isSitePlan) {
    lines.push('COMPOSITION: Near-top-down aerial, 15-20 degrees from nadir, colored polygons mark proposed zones on satellite photo');
  } else if (mode === 'ground') {
    lines.push('COMPOSITION: Oblique aerial, drone 60m altitude, ground-level zones only, no vertical structures');
  } else if (mode === 'building') {
    const entry = zoneEntries[0];
    lines.push(`COMPOSITION: Oblique aerial, drone 60m, single building on ${entry?.color || 'colored'} footprint, full 3D mass extending into sky`);
  } else {
    lines.push('COMPOSITION: Oblique aerial, DJI drone 60m altitude, colored polygons mark proposed zones on satellite photo');
  }

  // â”€â”€ LIGHTING â”€â”€
  if (isClay) {
    lines.push('LIGHTING: Soft diffused studio light, gentle shadows defining form only');
  } else if (isArtistic) {
    lines.push(`LIGHTING: Match ${style?.label || styleId} artistic conventions`);
  } else if (styleId === 'atmospheric') {
    lines.push('LIGHTING: Dramatic golden hour, low-angle warm sun, long architectural shadows, volumetric haze');
  } else if (styleId === 'winter') {
    lines.push('LIGHTING: Soft diffuse winter daylight, low sun angle, long blue-tinted shadows, pale blue-grey overcast sky. Snow-covered roofs, frosted ground plane, bare deciduous trees with visible branch structure, evergreens with heavy snow-load clumps. Increase specular reflectivity of all horizontal surfaces by 20% to simulate melt and ice sheen.');
  } else {
    lines.push('LIGHTING: Golden hour, warm southwest sun, crisp architectural shadows');
  }

  // â”€â”€ CONTEXT â”€â”€
  lines.push('CONTEXT: Preserve all unmasked satellite imagery exactly as-is. Rendered zones must blend naturally at edges â€” match tones, lighting, and scale of adjacent satellite context.');

  // â”€â”€ ZONES â”€â”€
  if (zoneEntries.length > 0) {
    // Custom-style prompts get more room when the prompt covers a single zone
    // (Pass 2 per-building) than in a crowded multi-zone prompt. LLM-expanded
    // descriptions run 80-140 words (~600-900 chars) â€” budgets sized to carry
    // most of that through rather than truncating what the user paid to generate.
    const customCharBudget = mode === 'building' || zoneEntries.length === 1 ? 900 : 600;
    lines.push('ZONES:');
    zoneEntries.forEach((entry, i) => {
      const imgIdx = imageIndices?.get(entry.color);
      lines.push(`${i + 1}. ${buildCompressedZoneLabel(entry, imgIdx, customCharBudget)}`);
    });
  }

  // â”€â”€ MANDATORY â”€â”€
  if (isClay) {
    lines.push('MANDATORY: ALL elements rendered as pure white matte plaster/clay. Every building, street, park, tree â€” everything is the same white material. Only shadows and form define shapes. Zero color, zero texture, zero real materials.');
  } else {
    lines.push('MANDATORY: Each zone renders ONLY within its colored polygon boundary. Realistic rooftop materials â€” no colored polygon fill visible on any surface. Replace ALL colored overlays with appropriate materials.');
  }

  // â”€â”€ PROHIBITIONS â”€â”€
  const prohibitions = [
    'buildings extending beyond polygon boundaries',
    'colored polygon fills visible on rooftops or facades',
    'boundary lines or outlines visible in final image',
    'people or pedestrians',
    'text overlays or watermarks',
  ];
  if (isClay) {
    prohibitions.push('any color other than white/off-white', 'any real building materials or textures', 'any colored surfaces');
  }
  if (isArtistic && !isClay) {
    prohibitions.push('photorealistic rendering');
  }
  if (styleId === 'winter') {
    prohibitions.push('lush green vegetation on deciduous trees', 'summer foliage', 'bright green lawns');
  }
  lines.push(`PROHIBITIONS: ${prohibitions.join(', ')}`);

  // â”€â”€ User custom prompt â”€â”€
  if (options.customPrompt?.trim()) {
    lines.push(`ADDITIONAL: ${options.customPrompt.trim()}`);
  }

  const result = lines.join('\n');
  console.log(`[AIRender] SCHEMA prompt (${result.length} chars, ${zoneEntries.length} zones):\n${result}`);
  return result;
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

  // Apply soft feather to mask edges so zones blend into satellite
  const featherPx = 4 * dpr;
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
      console.log(`[AIRender] compositeZoneRender: BUILDING "${zone.name || zone.zone_type}" â€” polygon clip + pixel-diff ${rw}x${rh}px above`);
    } else {
      console.log(`[AIRender] compositeZoneRender: BUILDING "${zone.name || zone.zone_type}" â€” polygon clip only (no headroom region)`);
    }
  } else {
    console.log(`[AIRender] compositeZoneRender: ${zone.zone_type} â€” strict polygon clip`);
  }

  return canvas.toDataURL('image/png');
}

/** Clip the composite to the site boundary polygon so nothing renders outside it.
 *  Uses a feathered mask so the boundary edge blends rather than hard-cuts. */
async function clipToSiteBoundary(
  dataUri: string,
  map: MapboxMap,
  boundaryZone: SiteZone,
): Promise<string> {
  const img = await loadImage(dataUri);
  const w = img.naturalWidth;
  const h = img.naturalHeight;
  const dpr = window.devicePixelRatio || 1;

  const pixels = siteBoundaryToPixels(map, boundaryZone.coordinates!);
  const devicePixels = pixels.map(p => ({ x: p.x * dpr, y: p.y * dpr }));

  // Draw site boundary polygon as white on black mask
  const maskCanvas = document.createElement('canvas');
  maskCanvas.width = w;
  maskCanvas.height = h;
  const maskCtx = maskCanvas.getContext('2d')!;
  maskCtx.fillStyle = '#000000';
  maskCtx.fillRect(0, 0, w, h);
  maskCtx.fillStyle = '#ffffff';
  maskCtx.beginPath();
  maskCtx.moveTo(devicePixels[0].x, devicePixels[0].y);
  for (let i = 1; i < devicePixels.length; i++) {
    maskCtx.lineTo(devicePixels[i].x, devicePixels[i].y);
  }
  maskCtx.closePath();
  maskCtx.fill();

  // Slight feather so the boundary edge blends
  const featherCanvas = document.createElement('canvas');
  featherCanvas.width = w;
  featherCanvas.height = h;
  const featherCtx = featherCanvas.getContext('2d')!;
  featherCtx.filter = `blur(${6 * dpr}px)`;
  featherCtx.drawImage(maskCanvas, 0, 0);

  // Apply mask to composite
  const canvas = document.createElement('canvas');
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext('2d')!;
  ctx.drawImage(img, 0, 0, w, h);
  ctx.globalCompositeOperation = 'destination-in';
  ctx.drawImage(featherCanvas, 0, 0);

  return canvas.toDataURL('image/png');
}

/** Apply an alpha feather at the edges of an image so the overlay fades into the map. */
async function applyEdgeFeather(dataUri: string, featherPx: number): Promise<string> {
  const img = await loadImage(dataUri);
  const w = img.naturalWidth;
  const h = img.naturalHeight;
  const dpr = window.devicePixelRatio || 1;
  const f = featherPx * dpr;

  // Create an inset rectangle mask and blur it for soft edges
  const maskCanvas = document.createElement('canvas');
  maskCanvas.width = w;
  maskCanvas.height = h;
  const maskCtx = maskCanvas.getContext('2d')!;
  maskCtx.filter = `blur(${f}px)`;
  maskCtx.fillStyle = '#ffffff';
  maskCtx.fillRect(f, f, w - f * 2, h - f * 2);

  // Apply the mask to the image
  const canvas = document.createElement('canvas');
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext('2d')!;
  ctx.drawImage(img, 0, 0, w, h);
  ctx.globalCompositeOperation = 'destination-in';
  ctx.drawImage(maskCanvas, 0, 0);

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
// Structured prompt builder â€” Spatial-to-Render Orchestration
// ---------------------------------------------------------------------------

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const catalog = (archetypeCatalog as any)?.archetypes as any[] | undefined;

interface ZonePromptEntry {
  color: string;
  zoneType: string;
  zoneName: string;
  descriptionText?: string; // User-editable description from the text box
  customPromptText?: string; // Custom-style zone: expanded (or raw) user prompt â€” passed intact, never condensed
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

    // Skip site_boundary â€” it's never composited and including it in the
    // prompt risks the AI drawing visible boundary lines/edges
    if (zone.zone_type === 'site_boundary') continue;

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
        customPromptText: getCustomZoneStyle(zone)?.promptText,
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
      return 'photorealistic residential buildings â€” townhouses or apartment blocks with warm materials, balconies, and landscaped entries';
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
      return 'water feature â€” pond, fountain, or reflecting pool with clean blue water and stone edges';
    case 'development_area':
      return 'mixed-use urban development with varied building heights, active ground floors, and public realm';
    default:
      return 'photorealistic urban development appropriate to the zone type';
  }
}

/**
 * Build the multi-zone prompt â€” narrative prose for Gemini.
 * Uses the same Subject + Environment + Materials + Lighting + Camera formula
 * as the two-pass pipeline, but describes all zones in a single prompt.
 */
function buildStructuredPrompt(options: AIRenderOptions): string {
  const zones = options.siteZones || [];
  const zoneEntries = collectZonePromptEntries(zones);
  return buildSCHEMAPrompt(zoneEntries, options, 'structured');
}

/**
 * Master prompt builder â€” generates a simple, natural-language prompt
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
    // Canonical variant resolution (ported from useGlobeAIRender
    // collectArchetypeImages): the selection lives in *_selected_variant_id
    // (a variant id string), NOT the legacy selected_variant integer — reading
    // only the integer silently falls back to variant 0 / hero for every zone.
    const props: any = zone.properties || {};
    const selectedVariantId = props.development_selected_variant_id
      || props.green_space_selected_variant_id
      || props.road_selected_variant_id
      || props.plaza_selected_variant_id
      || props.selected_variant_id;
    let variant = selectedVariantId
      ? catalogEntry.variants.find((v: any) => v.id === selectedVariantId)
      : undefined;
    if (!variant) {
      const selectedIdx = Number(props.selected_variant) || 0;
      variant = catalogEntry.variants[selectedIdx] || catalogEntry.variants[0];
    }
    thumbnailUrl = variant?.thumbnailUrl || null;
  }
  if (!thumbnailUrl) thumbnailUrl = catalogEntry.thumbnailUrl || null;
  if (!thumbnailUrl) return null;

  const b64 = await fetchArchetypeImageBase64(thumbnailUrl);
  if (!b64) return null;

  const label = info.archetypeTitle || zone.name || zone.zone_type;
  return { image_base64: b64, label };
}

/**
 * Fetch user-uploaded reference photos for a custom-style zone as multi-image
 * routing cards. Returns [] when the zone isn't custom or has no photos.
 * Fetch failures (e.g. deleted documents) are skipped silently.
 */
async function getCustomZonePhotoCards(
  zone: SiteZone,
): Promise<Array<{ image_base64: string; label: string; zone_color: string }>> {
  const custom = getCustomZoneStyle(zone);
  if (!custom || custom.photoUrls.length === 0) return [];

  const zoneName = zone.name || zone.zone_type;
  const zoneColor = colorName(getZoneRenderColor(zone.id, zone.color || '#E03C31'));
  const cards: Array<{ image_base64: string; label: string; zone_color: string }> = [];

  for (const url of custom.photoUrls) {
    const b64 = await fetchArchetypeImageBase64(resolveApiFileUrl(url));
    if (b64) {
      cards.push({
        image_base64: b64,
        label: `User reference photo for ${zoneName} â€” match the architectural style, materials, and colors shown`,
        zone_color: zoneColor,
      });
    }
  }
  return cards;
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
  projectId?: string,
  archetypeImages?: Array<{ image_base64: string; label: string; zone_color?: string }>,
  thinkingBudget?: number,
  imageSize?: string,
): Promise<{ imageDataUri: string; seed: number }> {
  console.log('[AIRender] Calling Vertex AI via backend â€” prompt length:', prompt.length, 'mask:', !!maskBase64, 'negative:', !!negativePrompt, 'guidance:', guidanceScale, 'model:', model || 'default', 'archetypeImages:', archetypeImages?.length || 0);

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
  if (projectId) {
    body.project_id = projectId;
  }
  if (archetypeImages && archetypeImages.length > 0) {
    body.archetype_images = archetypeImages;
  }
  if (thinkingBudget != null) {
    body.thinking_budget = thinkingBudget;
  }
  if (imageSize) {
    body.image_size = imageSize;
  }

  const token = localStorage.getItem('access_token');
  const resp = await axios.post(
    RENDER_API_URL,
    body,
    {
      timeout: RENDER_TIMEOUT,
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    },
  );

  const { image_base64: resultBase64, seed: resultSeed } = resp.data;
  if (!resultBase64) {
    throw new Error('Backend returned no image_base64 â€” check backend logs or VITE_API_URL config');
  }
  const imageDataUri = `data:image/png;base64,${resultBase64}`;

  console.log('[AIRender] Vertex AI success â€” image size:', resultBase64.length, 'chars');
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

  // â”€â”€ Core render function: capture â†’ base64 â†’ backend â†’ Vertex AI â”€â”€

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

      // Compute thinking budget from zone count
      const zoneCount = options.siteZones?.length ?? 0;
      let thinkingBudget: number | undefined;
      if (zoneCount >= 30) thinkingBudget = 24576;
      else if (zoneCount >= 16) thinkingBudget = 16384;
      else if (zoneCount >= 6) thinkingBudget = 8192;

      // Apply winter color grade to satellite context if winter style is selected
      const styleId = options.renderStyleId || options.style || 'photorealistic';
      const gradedImageBase64 = styleId === 'winter'
        ? await applyWinterColorGrade(imageBase64)
        : imageBase64;

      try {
        const { imageDataUri, seed: resultSeed } = await callVertexAI(
          gradedImageBase64,
          prompt,
          seed,
          aspectRatio,
          maskBase64,
          negativePrompt || undefined,
          guidanceScale,
          options.model,
          options.projectId,
          undefined,
          thinkingBudget,
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

  // â”€â”€ Single render (current camera position) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

  const render = useCallback(
    async (map: MapboxMap, options: AIRenderOptions = {}): Promise<AIRenderResult | null> => {
      if (abortRef.current) abortRef.current.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      // Plan zones carry semantic hints, not archetype IDs â€” resolve once here.
      if (options.siteZones?.length) {
        options = { ...options, siteZones: prepareZonesForRender(options.siteZones) };
      }

      setIsRendering(true);
      setProgress(-1); // indeterminate
      setError(null);
      setStatusMessage('Capturing view...');
      mapRef.current = map;

      try {
        // Generate mask FIRST (synchronous) before the async screenshot capture,
        // so both read canvas dimensions at the same instant. A layout reflow
        // between calls can shift dimensions by Â±1px, which Vertex AI rejects.
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

        // Winter Pass 2: Enhance satellite context outside rendered zones
        const winterStyleId = options.renderStyleId || options.style || 'photorealistic';
        if (winterStyleId === 'winter' && maskBase64 && renderResult.imageUrl) {
          setStatusMessage('Pass 2: Enhancing winter context...');
          console.log('[AIRender] â•â•â• WINTER PASS 2: Enhancing satellite context â•â•â•');

          try {
            // Invert mask: white = context area (outside zones), black = rendered zones (protected)
            const invertedMask = await invertMask(maskBase64);

            // Extract base64 from the stitched data URI
            const stitchedBase64 = renderResult.imageUrl.startsWith('data:')
              ? renderResult.imageUrl.split(',')[1]
              : renderResult.imageUrl;

            const contextPrompt =
              'Enhance the satellite imagery context in the white-masked area to show realistic winter conditions. ' +
              'Add snow accumulation on existing rooftops, bare deciduous trees with visible branch structure, ' +
              'frost on surfaces, and muted winter tones. Make existing buildings look like real buildings with ' +
              'visible facades, windows, and architectural detail â€” not grey blocks. ' +
              'Preserve all road markings, parking lots, and infrastructure detail. ' +
              'Do NOT alter the black-masked zones â€” they are already rendered. ' +
              'Match the winter lighting and snow coverage of the adjacent rendered zones for seamless blending.';

            const pass2Seed = seed + 1;
            const { imageDataUri: pass2DataUri } = await callVertexAI(
              stitchedBase64,
              contextPrompt,
              pass2Seed,
              aspectRatio,
              invertedMask,
              'summer vegetation, lush green trees, bright green grass, warm golden sunlight',
              options.guidanceScale ?? 15,
              options.model,
              options.projectId,
            );

            if (pass2DataUri) {
              renderResult.imageUrl = pass2DataUri;
              console.log('[AIRender] Winter Pass 2 complete â€” context enhanced');
            }
          } catch (pass2Err) {
            console.warn('[AIRender] Winter Pass 2 failed, using Pass 1 result:', pass2Err);
            // Non-fatal: keep the Pass 1 result if Pass 2 fails
          }
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

  // â”€â”€ Zone-targeted render â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

  const renderZone = useCallback(
    async (
      map: MapboxMap,
      zoneCoords: number[][],
      options: AIRenderOptions = {},
    ): Promise<AIRenderResult | null> => {
      if (abortRef.current) abortRef.current.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      if (options.siteZones?.length) {
        options = { ...options, siteZones: prepareZonesForRender(options.siteZones) };
      }

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
        setStatusMessage('Complete â€” zone rendered');
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

  // â”€â”€ Preview renders (3 in parallel) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

  const renderPreviews = useCallback(
    async (map: MapboxMap, options: AIRenderOptions = {}): Promise<AIRenderResult[]> => {
      if (options.siteZones?.length) {
        options = { ...options, siteZones: prepareZonesForRender(options.siteZones) };
      }

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

  // â”€â”€ Full quality render â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

  const renderFull = useCallback(
    async (
      map: MapboxMap,
      options: AIRenderOptions,
      seed: number,
      singleView = true,
    ): Promise<AIRenderResult | null> => {
      if (options.siteZones?.length) {
        options = { ...options, siteZones: prepareZonesForRender(options.siteZones) };
      }

      setIsRendering(true);
      setProgress(-1);
      setError(null);
      setFaceRenders([]);

      try {
        // â”€â”€ Single-view mode: render from user's current perspective â”€â”€
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
          setStatusMessage('Complete â€” full quality render');
          setIsRendering(false);
          return fullResult;
        }

        // â”€â”€ 4-face mode: rotate camera to 4 bearings â”€â”€
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
        setStatusMessage(`Complete â€” ${successfulFaces.length}/4 faces rendered`);
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

  // â”€â”€ Per-zone sequential rendering â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

  const renderPerZone = useCallback(
    async (map: MapboxMap, options: AIRenderOptions = {}): Promise<AIRenderResult | null> => {
      if (abortRef.current) abortRef.current.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      if (options.siteZones?.length) {
        options = { ...options, siteZones: prepareZonesForRender(options.siteZones) };
      }

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
        const OUTLINE_LAYERS = ['site-zones-outline', 'site-zones-selected', 'site-zones-labels', 'site-zones-boundary-fill', 'massing-preview-extrusion'];
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

        // For site-plan style: capture an additional top-down (nadir) screenshot
        // to give Gemini a true orthographic reference for spatial layout
        const styleId = options.renderStyleId || options.style || 'photorealistic';
        let topDownBase64: string | null = null;
        if (styleId === 'site-plan' || styleId === 'site-plan-photo' || styleId === 'site-plan-watercolor') {
          try {
            console.log('[AIRender] Site plan: capturing top-down reference...');
            map.jumpTo({ center: origCenter, zoom: origZoom, bearing: origBearing, pitch: 0 });
            await new Promise<void>(resolve => {
              const t = setTimeout(resolve, 1500);
              map.once('idle', () => { clearTimeout(t); resolve(); });
            });
            topDownBase64 = await captureMapCanvasBase64(map);
            // Restore original pitch
            map.jumpTo({ center: origCenter, zoom: origZoom, bearing: origBearing, pitch: origPitch });
            await new Promise<void>(resolve => {
              const t = setTimeout(resolve, 500);
              map.once('idle', () => { clearTimeout(t); resolve(); });
            });
            console.log('[AIRender] Site plan: top-down reference captured');
          } catch (topDownErr) {
            console.warn('[AIRender] Failed to capture top-down reference:', topDownErr);
          }
        }

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

        // â”€â”€ HIDE 3D extrusion layers and labels â”€â”€
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

        // â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
        // PASS 1: GROUND PLANE (parks, roads, plazas â€” all at once)
        // â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
        if (groundZones.length > 0) {
          setStatusMessage(`Pass 1/${totalSteps > 1 ? '2' : '1'}: Rendering ground plane (${groundZones.length} zones)...`);
          setProgress(5);
          console.log(`[AIRender] â•â•â• PASS 1: GROUND PLANE â•â•â• (${groundZones.length} zones)`);

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

            // For site-plan: include top-down reference as additional image
            const groundArchetypeImages: Array<{ image_base64: string; label: string; zone_color?: string }> = topDownBase64
              ? [{ image_base64: topDownBase64, label: 'Top-down orthographic view of the site â€” use this as the spatial layout reference for the site plan. Maintain exact zone positions and proportions as shown in this nadir view.' }]
              : [];

            // Custom-style zones: attach user-uploaded reference photos
            for (const gz of groundZones) {
              try {
                const customCards = await getCustomZonePhotoCards(gz);
                if (customCards.length > 0) {
                  groundArchetypeImages.push(...customCards);
                  console.log(`[AIRender] Pass 1: attached ${customCards.length} user reference photo(s) for custom zone "${gz.name || gz.zone_type}"`);
                }
              } catch (customErr) {
                console.warn('[AIRender] Failed to fetch custom zone photos:', customErr);
              }
            }

            // Compute thinking budget from total zone count
            const totalZones = options.siteZones?.length ?? 0;
            let groundThinkingBudget: number | undefined;
            if (totalZones >= 30) groundThinkingBudget = 24576;
            else if (totalZones >= 16) groundThinkingBudget = 16384;
            else if (totalZones >= 6) groundThinkingBudget = 8192;

            const { imageDataUri: groundResult } = await callVertexAI(
              groundScreenshot,
              groundPrompt,
              options.seed ?? Math.floor(Math.random() * 2147483647),
              aspectRatio,
              groundMask,
              negativePrompt || undefined,
              guidanceScale,
              options.model,
              options.projectId,
              groundArchetypeImages,
              groundThinkingBudget,
            );

            // Composite ground zones onto the cumulative result with strict polygon clipping
            for (const gz of groundZones) {
              cumulativeDataUri = await compositeZoneRender(cumulativeDataUri, groundResult, map, gz);
              successfulZones.push(gz.name || gz.zone_type);
            }

            currentStep++;
            console.log(`[AIRender] Pass 1 complete â€” ground plane rendered`);
          } catch (groundErr) {
            console.warn('[AIRender] Pass 1 (ground plane) failed:', groundErr);
          }
        }

        // â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
        // PASS 2: ARCHITECTURE (buildings, one at a time)
        // Each building renders onto the ground plane from Pass 1.
        // â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
        for (let i = 0; i < buildingZones.length; i++) {
          const zone = buildingZones[i];
          const zoneName = zone.name || zone.zone_type;
          currentStep++;
          setStatusMessage(`Pass 2: Building ${i + 1}/${buildingZones.length}: ${zoneName}...`);
          setProgress(Math.round((currentStep / totalSteps) * 90) + 5);
          console.log(`[AIRender] â•â•â• PASS 2: BUILDING ${i + 1}/${buildingZones.length}: "${zoneName}" â•â•â•`);

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
                  // NO height â€” flat polygon only
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

            // Custom-style zone: attach user-uploaded reference photos
            try {
              const customCards = await getCustomZonePhotoCards(zone);
              if (customCards.length > 0) {
                buildingArchetypeImages = [...(buildingArchetypeImages || []), ...customCards];
                console.log(`[AIRender] Pass 2: attached ${customCards.length} user reference photo(s) for custom zone "${zoneName}"`);
              }
            } catch (customErr) {
              console.warn('[AIRender] Failed to fetch custom zone photos:', customErr);
            }

            // For site-plan: add top-down reference to archetype images
            const allBuildingImages = [
              ...(buildingArchetypeImages || []),
              ...(topDownBase64 ? [{ image_base64: topDownBase64, label: 'Top-down orthographic view â€” use as spatial layout reference. Maintain exact zone positions and proportions.' }] : []),
            ];

            const { imageDataUri } = await callVertexAI(
              buildingScreenshot,
              buildingPrompt,
              options.seed ?? Math.floor(Math.random() * 2147483647),
              aspectRatio,
              buildingMask,
              negativePrompt || undefined,
              guidanceScale,
              options.model,
              options.projectId,
              allBuildingImages.length > 0 ? allBuildingImages : undefined,
              undefined, // thinkingBudget â€” single building, let backend auto-default
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

        // â”€â”€ Restore non-visual layers, keep zone fills hidden while render is displayed â”€â”€
        const KEEP_HIDDEN_DURING_RENDER = ['site-zones-fill', 'site-zones-boundary-fill', 'site-zones-extrusion', 'site-zones-outline', 'site-zones-selected'];
        for (const [layerId, visibility] of Object.entries(layerVisibilityBackup)) {
          if (map.getLayer(layerId)) {
            if (KEEP_HIDDEN_DURING_RENDER.includes(layerId)) {
              // Keep hidden â€” the render overlay replaces these visually
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

        // Clip final composite to site boundary so nothing bleeds outside
        const siteBoundaryZone = getActiveSiteBoundary(zones);
        if (siteBoundaryZone?.coordinates?.length) {
          cumulativeDataUri = await clipToSiteBoundary(cumulativeDataUri, map, siteBoundaryZone);
        }

        // Apply edge feathering so the overlay rectangle blends into satellite
        const featheredUri = await applyEdgeFeather(cumulativeDataUri, 20);

        const finalResult: AIRenderResult = {
          imageUrl: featheredUri,
          bounds: originalBounds,
          seed: options.seed,
          prompt: `Two-pass render: ${successfulZones.length} zones (${groundZones.length} ground + ${buildingZones.length} buildings)`,
        };

        setResult(finalResult);
        setProgress(100);
        setStatusMessage(`Complete â€” ${successfulZones.length} zones rendered (2-pass)`);
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

  // â”€â”€ Bearing-based face swapping â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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
