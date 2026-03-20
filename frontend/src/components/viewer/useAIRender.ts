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
    if (zone.zone_type === 'site_boundary') continue;
    if (!zone.coordinates?.length) continue;

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

  // Deduplicate by color (multiple zones of same type/color get merged description)
  const colorMap = new Map<string, ZonePromptEntry>();
  for (const entry of entries) {
    if (!colorMap.has(entry.color)) {
      colorMap.set(entry.color, entry);
    }
    // If a later entry has better metadata, prefer it
    else if (entry.archetypeTitle && !colorMap.get(entry.color)!.archetypeTitle) {
      colorMap.set(entry.color, entry);
    }
  }

  return Array.from(colorMap.values());
}

/**
 * Human-readable color name for common hex colors used by zone types.
 */
function colorName(hex: string): string {
  const map: Record<string, string> = {
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
  return map[hex] || hex;
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
 * Build the complete structured prompt following the 3-block Orchestration Spec:
 *
 * Block 1: Anchor Command — strict geometry/footprint adherence
 * Block 2: Zone Mapping — iterate zones: color → archetype → render details
 * Block 3: Environmental Context & Style Application
 */
function buildStructuredPrompt(options: AIRenderOptions): string {
  const zones = options.siteZones || [];
  const zoneEntries = collectZonePromptEntries(zones);
  const styleId = options.renderStyleId || options.style || 'photorealistic';
  const styleModifier = GEMINI_STYLE_MODIFIERS[styleId] || GEMINI_STYLE_MODIFIERS['photorealistic'];

  // ── Block 1: Anchor Command ──
  const block1 = [
    'You are looking at an aerial/satellite photograph with colored polygon overlays representing a proposed urban development.',
    'Each colored polygon marks the EXACT footprint of a building, road, park, or other zone.',
    'CRITICAL RULES:',
    '- Replace ONLY the colored polygon areas with photorealistic content as described below.',
    '- Preserve the EXACT footprint, shape, and position of each colored polygon — do not move, resize, or reshape any zone.',
    '- Keep ALL surrounding satellite imagery, roads, existing buildings, and context EXACTLY as they appear — change NOTHING outside the colored areas.',
    '- Match the lighting direction, color temperature, and perspective of the surrounding satellite context.',
    '- The result must look like a seamless photomontage where new development is composited into the real satellite photograph.',
  ].join('\n');

  // ── Block 2: Zone Mapping ──
  let block2: string;
  if (zoneEntries.length > 0) {
    const zoneLines = zoneEntries.map((entry) => {
      const color = colorName(entry.color);
      let desc: string;

      if (entry.mapOverlayPrompt) {
        // Use the archetype's specific render prompt (best quality)
        desc = entry.mapOverlayPrompt;
      } else if (entry.archetypeTitle) {
        // Build from archetype metadata
        const parts = [`${entry.archetypeTitle}`];
        if (entry.facadeDescription) parts.push(`Facade: ${entry.facadeDescription}`);
        if (entry.roofDescription) parts.push(`Roof: ${entry.roofDescription}`);
        if (entry.materials) parts.push(`Materials: ${entry.materials}`);
        if (entry.massing) parts.push(`Massing: ${entry.massing}`);
        if (entry.heightTendency) parts.push(`Height: ${entry.heightTendency}`);
        if (entry.publicRealm) parts.push(`Street edge: ${entry.publicRealm}`);
        desc = parts.join('. ');
      } else {
        // Fallback to zone-type default
        desc = defaultZoneDescription(entry.zoneType);
      }

      return `• ${color.toUpperCase()} zones (${entry.color}, ${entry.zoneName}): ${desc}`;
    });

    block2 = [
      '',
      'ZONE-BY-ZONE INSTRUCTIONS:',
      ...zoneLines,
    ].join('\n');
  } else {
    // No specific zones — provide generic color mapping
    block2 = [
      '',
      'ZONE-BY-ZONE INSTRUCTIONS:',
      '• RED zones (#E03C31): Replace with photorealistic commercial or mixed-use buildings with detailed facades, glass and brick materials',
      '• YELLOW zones (#F5D63D): Replace with residential buildings — townhouses or apartments with warm materials and balconies',
      '• GREEN zones (#4CAF50): Replace with landscaped parks with mature trees, grass lawns, walking paths, and benches',
      '• DARK GRAY zones (#616161): Replace with paved roads with lane markings, sidewalks, street trees, and parked cars',
      '• LIGHT GRAY zones (#9E9E9E): Replace with paved plazas or surface parking with pedestrian paving and street furniture',
      '• BLUE zones (#4A90D9): Replace with water features — ponds, fountains, or reflecting pools',
      '• GOLD/AMBER zones (#C8A02A): Replace with mixed-use urban development with varied heights and active ground floors',
    ].join('\n');
  }

  // ── Block 3: Environmental Context & Style ──
  const block3Parts = [
    '',
    'STYLE & ENVIRONMENT:',
    styleModifier.prompt,
  ];

  // Add custom prompt if provided
  if (options.customPrompt?.trim()) {
    block3Parts.push(`Additional direction: ${options.customPrompt.trim()}`);
  }

  // Add archetype positive prompts if available
  if (options.archetypePrompt?.trim()) {
    block3Parts.push(`Archetype style: ${options.archetypePrompt.trim()}`);
  }

  block3Parts.push(
    '',
    'QUALITY: Ultra-high resolution, sharp focus, photorealistic materials with visible texture and grain, realistic shadows consistent with sun position, 8k quality.',
  );

  const block3 = block3Parts.join('\n');

  return [block1, block2, block3].join('\n');
}

/**
 * Build a simpler prompt for when we have a specific mapOverlayPrompt
 * (single-archetype scenario — the archetype already has a complete prompt).
 */
function buildSingleArchetypePrompt(options: AIRenderOptions): string {
  if (!options.mapOverlayPrompt?.trim()) return buildStructuredPrompt(options);

  const parts = [
    'You are looking at an aerial/satellite photograph with colored polygon overlays.',
    'Replace ONLY the colored polygon areas with the following:',
    '',
    options.mapOverlayPrompt.trim(),
    '',
    'CRITICAL: Keep ALL surrounding satellite imagery exactly as-is. Change NOTHING outside the colored areas.',
    'Match the lighting, color temperature, and perspective of the surrounding context.',
  ];

  if (options.customPrompt?.trim()) {
    parts.push(`Additional: ${options.customPrompt.trim()}`);
  }

  return parts.join('\n');
}

/**
 * Master prompt builder — decides between structured multi-zone prompt
 * and single-archetype prompt based on available data.
 */
function buildPrompt(options: AIRenderOptions): string {
  // If we have multiple zones with data, use the structured prompt
  const zones = options.siteZones?.filter(z => z.zone_type !== 'site_boundary') || [];
  if (zones.length > 0) {
    return buildStructuredPrompt(options);
  }

  // If we have a single archetype overlay prompt, use that
  if (options.mapOverlayPrompt?.trim()) {
    return buildSingleArchetypePrompt(options);
  }

  // Final fallback: use generic style preset
  const styleId = options.renderStyleId || options.style || 'photorealistic';
  const preset = AI_RENDER_STYLES.find((s) => s.id === styleId) || AI_RENDER_STYLES[0];
  let prompt = `Transform the colored overlay zones in this aerial photograph into photorealistic development. ${preset.prompt}`;
  if (options.archetypePrompt?.trim()) {
    prompt += ', ' + options.archetypePrompt.trim();
  }
  if (options.customPrompt?.trim()) {
    prompt += ', ' + options.customPrompt.trim();
  }
  return prompt;
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
): Promise<{ imageDataUri: string; seed: number }> {
  console.log('[AIRender] Calling Vertex AI via backend — prompt length:', prompt.length);

  const resp = await axios.post(
    RENDER_API_URL,
    {
      image_base64: imageBase64,
      prompt,
      aspect_ratio: aspectRatio,
      seed,
    },
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
    ): Promise<AIRenderResult | null> => {
      const prompt = buildPrompt(options);

      try {
        const { imageDataUri, seed: resultSeed } = await callVertexAI(
          imageBase64,
          prompt,
          seed,
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
        const imageBase64 = await captureMapCanvasBase64(map);
        const bounds = getMapBounds(map);

        setStatusMessage('Generating render... Please wait');

        const seed = options.seed ?? Math.floor(Math.random() * 2147483647);
        const renderResult = await renderSingle(imageBase64, bounds, options, seed);

        if (!renderResult) throw new Error('Vertex AI returned no image');

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
        const renderResult = await renderSingle(imageBase64, bounds, options, seed);

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
        const imageBase64 = await captureMapCanvasBase64(map);
        const bounds = getMapBounds(map);

        setStatusMessage('Generating 3 previews... Please wait');

        // Generate 3 renders with different seeds
        const seeds = Array.from({ length: 3 }, () => Math.floor(Math.random() * 2147483647));

        const promises = seeds.map((seed) =>
          renderSingle(imageBase64, bounds, options, seed).catch(() => null),
        );

        const rawResults = await Promise.all(promises);
        const successful = rawResults.filter((r): r is AIRenderResult => r !== null);

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
          const imageBase64 = await captureMapCanvasBase64(map);
          const bounds = getMapBounds(map);

          setStatusMessage('Rendering full quality... Please wait');

          const fullResult = await renderSingle(imageBase64, bounds, options, seed);
          if (!fullResult) throw new Error('Vertex AI returned no image');

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

        const renderPromises = captures.map((cap) =>
          renderSingle(cap.base64, cap.bounds, options, seed)
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
